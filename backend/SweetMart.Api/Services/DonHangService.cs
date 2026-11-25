using Microsoft.EntityFrameworkCore;
using SweetMart.Api.Common;
using SweetMart.Api.Data;
using SweetMart.Api.Domain;
using SweetMart.Api.Dtos;
using SweetMart.Api.Integrations;

namespace SweetMart.Api.Services;

public record TamTinh(decimal TongTienHang, decimal TienGiam, decimal PhiVanChuyen, decimal TongThanhToan, KhuyenMai? KhuyenMai);

/// <summary>Nghiệp vụ đơn hàng: tính tiền, tạo đơn, chuyển trạng thái, hủy, tạo vận đơn.</summary>
public class DonHangService(AppDbContext db, TonKhoService tonKho, KhuyenMaiService khuyenMai, IGhnClient ghn,
    EmailQueue email, ILogger<DonHangService> logger)
{
    /// <summary>Tính tạm tiền hàng, giảm giá, phí ship cho giỏ hàng hiện tại (BR05, BR06).</summary>
    public async Task<TamTinh> TinhTienAsync(int maND, DiaChi diaChi, string? maCode, CancellationToken ct = default)
    {
        var gio = await LayGioHangAsync(maND, ct);
        var tongTienHang = gio.Sum(x => x.SanPham!.GiaBan * x.SoLuong);
        KhuyenMai? km = null;
        decimal tienGiam = 0;
        if (!string.IsNullOrWhiteSpace(maCode))
            (km, tienGiam) = await khuyenMai.KiemTraAsync(maCode, maND, tongTienHang, DateTime.UtcNow, ct);

        var sauGiam = tongTienHang - tienGiam;
        decimal phiShip = 0;
        if (sauGiam < BusinessRules.MienPhiShipTu)
        {
            var khoiLuong = gio.Sum(x => x.SanPham!.KhoiLuongGram * x.SoLuong);
            try
            {
                phiShip = await ghn.TinhPhiAsync(diaChi.MaQuanHuyenGHN, diaChi.MaPhuongXaGHN, khoiLuong, sauGiam, ct);
            }
            catch (Exception ex)
            {
                logger.LogWarning(ex, "GHN không tính được phí, dùng phí mặc định");
                phiShip = BusinessRules.PhiShipMacDinh;
            }
        }
        return new TamTinh(tongTienHang, tienGiam, phiShip, sauGiam + phiShip, km);
    }

    /// <summary>Tạo đơn từ giỏ hàng. Toàn bộ việc giữ tồn kho và ghi đơn nằm trong một transaction.</summary>
    public async Task<DonHang> TaoDonAsync(int maND, TaoDonRequest req, CancellationToken ct = default)
    {
        var diaChi = await db.DiaChi.FirstOrDefaultAsync(d => d.MaDC == req.MaDC && d.MaND == maND, ct)
                     ?? throw new BusinessException("ADDRESS_NOT_FOUND", "Địa chỉ giao hàng không hợp lệ.", 400);

        var tam = await TinhTienAsync(maND, diaChi, req.MaCode, ct);
        if (req.PhuongThucTT == PhuongThucThanhToan.COD && tam.TongThanhToan > BusinessRules.HanMucCOD)
            throw new BusinessException("COD_LIMIT_EXCEEDED",
                $"Đơn trên {BusinessRules.HanMucCOD:N0}đ cần thanh toán online qua VNPay.");

        await using var tx = await db.Database.BeginTransactionAsync(ct);
        var gio = await LayGioHangAsync(maND, ct);
        var online = req.PhuongThucTT == PhuongThucThanhToan.VNPAY;
        var don = new DonHang
        {
            MaND = maND,
            MaKM = tam.KhuyenMai?.MaKM,
            TongTienHang = tam.TongTienHang,
            TienGiam = tam.TienGiam,
            PhiVanChuyen = tam.PhiVanChuyen,
            TongThanhToan = tam.TongThanhToan,
            PhuongThucTT = req.PhuongThucTT,
            NguoiNhan = diaChi.NguoiNhan,
            SoDienThoaiNhan = diaChi.SoDienThoai,
            DiaChiGiao = diaChi.DiaChiChiTiet,
            MaQuanHuyenGHN = diaChi.MaQuanHuyenGHN,
            MaPhuongXaGHN = diaChi.MaPhuongXaGHN,
            GhiChu = req.GhiChu,
            TrangThai = online ? TrangThaiDon.ChoThanhToan : TrangThaiDon.ChoXacNhan,
            TrangThaiThanhToan = online ? TrangThaiThanhToan.ChoThanhToan : TrangThaiThanhToan.ChuaThu,
        };

        foreach (var item in gio)
        {
            var phanBo = await tonKho.GiuHangAsync(item.MaSP, item.SoLuong, ct);   // BR01, BR02, BR04
            don.ChiTiet.Add(new ChiTietDonHang
            {
                MaSP = item.MaSP,
                SoLuong = item.SoLuong,
                DonGia = item.SanPham!.GiaBan,                                      // BR11
                PhanBo = phanBo.Select(p => new PhanBoLo { MaSP = item.MaSP, MaLo = p.MaLo, SoLuong = p.SoLuong }).ToList()
            });
        }
        if (tam.KhuyenMai is { } km) km.SoLuotConLai--;
        don.LichSu.Add(new LichSuDonHang { TrangThaiMoi = don.TrangThai, NguoiThucHien = maND, GhiChu = "Khách đặt hàng" });

        db.DonHang.Add(don);
        db.GioHang.RemoveRange(gio);
        await db.SaveChangesAsync(ct);
        await tx.CommitAsync(ct);

        if (!online) await GuiEmailTrangThaiAsync(don, "Đặt hàng thành công", ct);
        return don;
    }

    public async Task<DonHang> CapNhatTrangThaiAsync(int maDH, TrangThaiDon moi, int? nguoiThucHien, string? ghiChu, CancellationToken ct = default)
    {
        if (moi == TrangThaiDon.DaHuy) return await HuyDonAsync(maDH, nguoiThucHien, false, ghiChu ?? "Nhân viên hủy", ct);
        if (moi == TrangThaiDon.DangGiao)
            throw new BusinessException("USE_SHIPMENT", "Hãy dùng chức năng \"Tạo vận đơn\" để chuyển sang Đang giao.", 400);

        var don = await LayDonAsync(maDH, ct);
        DamBaoChuyenHopLe(don, moi);
        await using var tx = await db.Database.BeginTransactionAsync(ct);
        var cu = don.TrangThai;
        don.TrangThai = moi;
        if (moi == TrangThaiDon.DaGiao && don.PhuongThucTT == PhuongThucThanhToan.COD)
            don.TrangThaiThanhToan = TrangThaiThanhToan.DaThuCOD;
        if (moi == TrangThaiDon.GiaoThatBai)
        {
            await tonKho.HoanKhoAsync(maDH, ct);
            if (don.PhuongThucTT == PhuongThucThanhToan.COD) don.TrangThaiThanhToan = TrangThaiThanhToan.KhongThuDuoc;
        }
        don.LichSu.Add(new LichSuDonHang { TrangThaiCu = cu, TrangThaiMoi = moi, NguoiThucHien = nguoiThucHien, GhiChu = ghiChu });
        await db.SaveChangesAsync(ct);
        await tx.CommitAsync(ct);
        await GuiEmailTrangThaiAsync(don, $"Đơn hàng {don.MaHienThi}: {TenTrangThai(moi)}", ct);
        return don;
    }

    /// <summary>Hủy đơn và hoàn kho (BR09). Khách chỉ hủy được khi đơn chưa được xác nhận.</summary>
    public async Task<DonHang> HuyDonAsync(int maDH, int? nguoiThucHien, bool laKhachHang, string lyDo, CancellationToken ct = default)
    {
        var don = await LayDonAsync(maDH, ct);
        if (laKhachHang)
        {
            if (don.MaND != nguoiThucHien) throw new BusinessException("NOT_FOUND", "Không tìm thấy đơn hàng.", 404);
            if (don.TrangThai is not (TrangThaiDon.ChoXacNhan or TrangThaiDon.ChoThanhToan))
                throw new BusinessException("CANNOT_CANCEL", "Đơn đã được cửa hàng xác nhận, vui lòng liên hệ cửa hàng để hủy.");
        }
        DamBaoChuyenHopLe(don, TrangThaiDon.DaHuy);

        await using var tx = await db.Database.BeginTransactionAsync(ct);
        var cu = don.TrangThai;
        if (cu != TrangThaiDon.GiaoThatBai) await tonKho.HoanKhoAsync(maDH, ct);   // giao thất bại đã hoàn kho trước đó
        if (don.MaKM is { } maKM)
        {
            var km = await db.KhuyenMai.FindAsync([maKM], ct);
            if (km is not null) km.SoLuotConLai++;
        }
        don.TrangThai = TrangThaiDon.DaHuy;
        don.TrangThaiThanhToan = don.TrangThaiThanhToan switch
        {
            TrangThaiThanhToan.DaThanhToan => TrangThaiThanhToan.ChoHoanTien,
            TrangThaiThanhToan.ChoThanhToan => TrangThaiThanhToan.ThatBai,
            var x => x
        };
        don.LichSu.Add(new LichSuDonHang { TrangThaiCu = cu, TrangThaiMoi = TrangThaiDon.DaHuy, NguoiThucHien = nguoiThucHien, GhiChu = lyDo });
        await db.SaveChangesAsync(ct);
        await tx.CommitAsync(ct);
        await GuiEmailTrangThaiAsync(don, $"Đơn hàng {don.MaHienThi} đã bị hủy", ct);
        return don;
    }

    /// <summary>Tạo vận đơn GHN cho đơn đã đóng gói, chuyển sang Đang giao.</summary>
    public async Task<DonHang> TaoVanDonAsync(int maDH, int nguoiThucHien, CancellationToken ct = default)
    {
        var don = await LayDonAsync(maDH, ct);
        if (don.TrangThai != TrangThaiDon.DangDongGoi)
            throw new BusinessException("INVALID_STATE", "Chỉ tạo vận đơn cho đơn đang đóng gói.", 409);

        var khoiLuong = await db.ChiTietDonHang.Where(c => c.MaDH == maDH).SumAsync(c => c.SanPham!.KhoiLuongGram * c.SoLuong, ct);
        string maVanDon;
        try
        {
            maVanDon = await ghn.TaoDonAsync(new GhnKienHang(khoiLuong, don.TongTienHang,
                don.PhuongThucTT == PhuongThucThanhToan.COD ? don.TongThanhToan : 0,
                don.NguoiNhan, don.SoDienThoaiNhan, don.DiaChiGiao, don.MaQuanHuyenGHN, don.MaPhuongXaGHN, don.MaHienThi, don.GhiChu), ct);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Tạo vận đơn GHN thất bại cho {MaDH}", maDH);
            throw new BusinessException("GHN_ERROR", "Không tạo được vận đơn GHN, vui lòng thử lại sau.", 502);
        }
        don.MaVanDonGHN = maVanDon;
        don.LichSu.Add(new LichSuDonHang { TrangThaiCu = don.TrangThai, TrangThaiMoi = TrangThaiDon.DangGiao, NguoiThucHien = nguoiThucHien, GhiChu = $"Mã vận đơn GHN {maVanDon}" });
        don.TrangThai = TrangThaiDon.DangGiao;
        await db.SaveChangesAsync(ct);
        await GuiEmailTrangThaiAsync(don, $"Đơn hàng {don.MaHienThi} đang được giao", ct);
        return don;
    }

    private static void DamBaoChuyenHopLe(DonHang don, TrangThaiDon moi)
    {
        if (!OrderStateMachine.CoTheChuyen(don.TrangThai, moi))
            throw new BusinessException("INVALID_TRANSITION",
                $"Không thể chuyển đơn từ \"{TenTrangThai(don.TrangThai)}\" sang \"{TenTrangThai(moi)}\".", 409);
    }

    private async Task<DonHang> LayDonAsync(int maDH, CancellationToken ct) =>
        await db.DonHang.Include(d => d.LichSu).FirstOrDefaultAsync(d => d.MaDH == maDH, ct)
        ?? throw new BusinessException("NOT_FOUND", "Không tìm thấy đơn hàng.", 404);

    private async Task<List<GioHang>> LayGioHangAsync(int maND, CancellationToken ct)
    {
        var gio = await db.GioHang.Include(g => g.SanPham).Where(g => g.MaND == maND).ToListAsync(ct);
        if (gio.Count == 0) throw new BusinessException("CART_EMPTY", "Giỏ hàng đang trống.", 400);
        var ngungBan = gio.FirstOrDefault(g => !g.SanPham!.DangBan);
        if (ngungBan is not null)
            throw new BusinessException("PRODUCT_UNAVAILABLE", $"Sản phẩm \"{ngungBan.SanPham!.TenSP}\" đã ngừng bán.", 409);
        return gio;
    }

    public async Task GuiEmailTrangThaiAsync(DonHang don, string tieuDe, CancellationToken ct = default)
    {
        var emailKhach = await db.NguoiDung.Where(u => u.MaND == don.MaND).Select(u => u.Email).FirstOrDefaultAsync(ct);
        if (emailKhach is null) return;
        email.Enqueue(emailKhach, $"[SweetMart] {tieuDe}",
            $"<p>Đơn hàng <b>{don.MaHienThi}</b> – trạng thái: <b>{TenTrangThai(don.TrangThai)}</b>.</p>" +
            $"<p>Tổng thanh toán: {don.TongThanhToan:N0}đ.</p><p>Cảm ơn bạn đã mua sắm tại SweetMart!</p>");
    }

    public static string TenTrangThai(TrangThaiDon t) => t switch
    {
        TrangThaiDon.ChoThanhToan => "Chờ thanh toán",
        TrangThaiDon.ChoXacNhan => "Chờ xác nhận",
        TrangThaiDon.DaXacNhan => "Đã xác nhận",
        TrangThaiDon.DangDongGoi => "Đang đóng gói",
        TrangThaiDon.DangGiao => "Đang giao",
        TrangThaiDon.DaGiao => "Đã giao",
        TrangThaiDon.GiaoThatBai => "Giao thất bại",
        TrangThaiDon.DaHuy => "Đã hủy",
        _ => t.ToString()
    };
}
