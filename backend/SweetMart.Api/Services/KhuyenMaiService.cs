using Microsoft.EntityFrameworkCore;
using SweetMart.Api.Common;
using SweetMart.Api.Data;
using SweetMart.Api.Domain;

namespace SweetMart.Api.Services;

/// <summary>Kiểm tra và tính tiền giảm của mã khuyến mãi (BR06).</summary>
public class KhuyenMaiService(AppDbContext db)
{
    public async Task<(KhuyenMai km, decimal tienGiam)> KiemTraAsync(string maCode, int maND, decimal tongTienHang, DateTime nowUtc, CancellationToken ct = default)
    {
        var code = maCode.Trim().ToUpperInvariant();
        var km = await db.KhuyenMai.FirstOrDefaultAsync(x => x.MaCode == code, ct)
                 ?? throw new BusinessException("VOUCHER_INVALID", "Mã giảm giá không tồn tại.");
        if (nowUtc < km.NgayBatDau || nowUtc > km.NgayKetThuc)
            throw new BusinessException("VOUCHER_INVALID", "Mã giảm giá đã hết hạn hoặc chưa đến thời gian áp dụng.");
        if (km.SoLuotConLai <= 0)
            throw new BusinessException("VOUCHER_INVALID", "Mã giảm giá đã hết lượt sử dụng.");
        if (tongTienHang < km.DonToiThieu)
            throw new BusinessException("VOUCHER_INVALID", $"Đơn hàng cần tối thiểu {km.DonToiThieu:N0}đ để dùng mã này.");
        var daDung = await db.DonHang.AnyAsync(d => d.MaND == maND && d.MaKM == km.MaKM && d.TrangThai != TrangThaiDon.DaHuy, ct);
        if (daDung)
            throw new BusinessException("VOUCHER_INVALID", "Bạn đã sử dụng mã giảm giá này.");
        return (km, TinhTienGiam(km, tongTienHang));
    }

    public static decimal TinhTienGiam(KhuyenMai km, decimal tongTienHang)
    {
        var giam = km.LoaiGiam == LoaiGiam.PhanTram
            ? Math.Round(tongTienHang * km.GiaTriGiam / 100m, 0, MidpointRounding.AwayFromZero)
            : km.GiaTriGiam;
        if (km.GiamToiDa is { } max) giam = Math.Min(giam, max);
        return Math.Min(giam, tongTienHang);
    }
}
