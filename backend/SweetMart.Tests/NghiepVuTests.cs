using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using SweetMart.Api.Common;
using SweetMart.Api.Domain;
using SweetMart.Api.Dtos;
using SweetMart.Api.Integrations;
using SweetMart.Api.Services;

namespace SweetMart.Tests;

/// <summary>US09 – Giữ hàng theo FEFO (BR01, BR02, BR04).</summary>
public class TonKhoServiceTests
{
    [Fact]
    public async Task GiuHang_LayLoGanHetHanTruoc()   // AC1
    {
        using var t = new TestDb();
        var sp = t.ThemSanPham(50_000, (30, 3), (180, 10));
        var loA = sp.LoHang[0]; var loB = sp.LoHang[1];

        var kq = await new TonKhoService(t.Db).GiuHangAsync(sp.MaSP, 5);
        await t.Db.SaveChangesAsync();

        Assert.Equal([new PhanBo(loA.MaLo, 3), new PhanBo(loB.MaLo, 2)], kq);
        Assert.Equal(0, loA.SoLuongTon);
        Assert.Equal(8, loB.SoLuongTon);
    }

    [Fact]
    public async Task GiuHang_BoQuaLoHetHan()   // AC2
    {
        using var t = new TestDb();
        var sp = t.ThemSanPham(50_000, (-1, 4), (90, 1));

        var ex = await Assert.ThrowsAsync<BusinessException>(() => new TonKhoService(t.Db).GiuHangAsync(sp.MaSP, 2));

        Assert.Equal("OUT_OF_STOCK", ex.Code);
        Assert.Equal(1, await new TonKhoService(t.Db).TonKhaDungAsync(sp.MaSP));
    }

    [Fact]
    public async Task HoanKho_CongLaiDungLo()   // AC4
    {
        using var t = new TestDb();
        var kh = t.ThemKhach(); var dc = t.ThemDiaChi(kh.MaND);
        var sp = t.ThemSanPham(50_000, (30, 3), (180, 10));
        t.ThemVaoGio(kh.MaND, sp.MaSP, 5);
        var svc = t.DonHangService();
        var don = await svc.TaoDonAsync(kh.MaND, new TaoDonRequest(dc.MaDC, PhuongThucThanhToan.COD, null, null));

        await svc.HuyDonAsync(don.MaDH, kh.MaND, true, "Đổi ý");

        var lo = await t.Db.LoHang.AsNoTracking().OrderBy(l => l.HanSuDung).ToListAsync();
        Assert.Equal([3, 10], lo.Select(l => l.SoLuongTon));
    }
}

/// <summary>US14 – Mã giảm giá (BR06).</summary>
public class KhuyenMaiServiceTests
{
    private static KhuyenMai Ma(LoaiGiam loai, decimal giaTri, decimal? max = null, decimal min = 0) => new()
    {
        MaCode = "TEST", LoaiGiam = loai, GiaTriGiam = giaTri, GiamToiDa = max, DonToiThieu = min,
        NgayBatDau = DateTime.UtcNow.AddDays(-1), NgayKetThuc = DateTime.UtcNow.AddDays(10), SoLuotConLai = 5
    };

    [Theory]
    [InlineData(LoaiGiam.PhanTram, 10, null, 350_000, 35_000)]
    [InlineData(LoaiGiam.PhanTram, 10, 20_000d, 350_000, 20_000)]   // không vượt mức giảm tối đa
    [InlineData(LoaiGiam.SoTien, 20_000, null, 150_000, 20_000)]
    [InlineData(LoaiGiam.SoTien, 50_000, null, 30_000, 30_000)]     // không giảm quá tiền hàng
    public void TinhTienGiam(LoaiGiam loai, double giaTri, double? max, double tong, double ketQua) =>
        Assert.Equal((decimal)ketQua, KhuyenMaiService.TinhTienGiam(Ma(loai, (decimal)giaTri, (decimal?)max), (decimal)tong));

    [Fact]
    public async Task MaHetHan_BiTuChoi()
    {
        using var t = new TestDb();
        var km = Ma(LoaiGiam.SoTien, 20_000); km.NgayKetThuc = DateTime.UtcNow.AddDays(-1); km.NgayBatDau = DateTime.UtcNow.AddDays(-5);
        t.Db.KhuyenMai.Add(km); await t.Db.SaveChangesAsync();
        var ex = await Assert.ThrowsAsync<BusinessException>(() => new KhuyenMaiService(t.Db).KiemTraAsync("test", 1, 500_000, DateTime.UtcNow));
        Assert.Equal("VOUCHER_INVALID", ex.Code);
    }

    [Fact]
    public async Task ChuaDatGiaTriToiThieu_BiTuChoi()
    {
        using var t = new TestDb();
        t.Db.KhuyenMai.Add(Ma(LoaiGiam.SoTien, 20_000, min: 150_000)); await t.Db.SaveChangesAsync();
        await Assert.ThrowsAsync<BusinessException>(() => new KhuyenMaiService(t.Db).KiemTraAsync("TEST", 1, 100_000, DateTime.UtcNow));
    }

    [Fact]
    public async Task MoiKhachChiDungMotLan()
    {
        using var t = new TestDb();
        var kh = t.ThemKhach(); var dc = t.ThemDiaChi(kh.MaND);
        t.Db.KhuyenMai.Add(Ma(LoaiGiam.SoTien, 20_000)); await t.Db.SaveChangesAsync();
        var sp = t.ThemSanPham(100_000, (100, 20));
        var svc = t.DonHangService();
        t.ThemVaoGio(kh.MaND, sp.MaSP, 1);
        await svc.TaoDonAsync(kh.MaND, new TaoDonRequest(dc.MaDC, PhuongThucThanhToan.COD, "TEST", null));

        var ex = await Assert.ThrowsAsync<BusinessException>(() => new KhuyenMaiService(t.Db).KiemTraAsync("TEST", kh.MaND, 100_000, DateTime.UtcNow));
        Assert.Contains("đã sử dụng", ex.Message);
    }
}

/// <summary>US12, US19 – Đặt hàng, hủy đơn, chuyển trạng thái (BR04, BR05, BR07, BR09, BR10, BR11).</summary>
public class DonHangServiceTests
{
    [Fact]
    public async Task TaoDonCOD_ThanhCong()   // US12 – AC1
    {
        using var t = new TestDb();
        var kh = t.ThemKhach(); var dc = t.ThemDiaChi(kh.MaND);
        var sp = t.ThemSanPham(120_000, (100, 10));
        t.ThemVaoGio(kh.MaND, sp.MaSP, 2);

        var don = await t.DonHangService().TaoDonAsync(kh.MaND, new TaoDonRequest(dc.MaDC, PhuongThucThanhToan.COD, null, "Gói quà"));

        Assert.Equal(TrangThaiDon.ChoXacNhan, don.TrangThai);
        Assert.Equal(240_000, don.TongTienHang);
        Assert.Equal(22_000, don.PhiVanChuyen);       // dưới 300.000đ nên tính phí ship (GHN giả lập)
        Assert.Equal(262_000, don.TongThanhToan);
        Assert.Empty(t.Db.GioHang.Where(g => g.MaND == kh.MaND));
        Assert.Equal(8, await new TonKhoService(t.Db).TonKhaDungAsync(sp.MaSP));
        Assert.Single(don.LichSu);
    }

    [Fact]
    public async Task DuoiNguongMienPhi_TinhPhiShip_TuDuoi300k()   // BR05
    {
        using var t = new TestDb();
        var kh = t.ThemKhach(); var dc = t.ThemDiaChi(kh.MaND);
        var spRe = t.ThemSanPham(100_000, (100, 10));
        t.ThemVaoGio(kh.MaND, spRe.MaSP, 2);
        var svc = t.DonHangService(new FakeGhnClient());

        var tam = await svc.TinhTienAsync(kh.MaND, dc, null);
        Assert.Equal(22_000, tam.PhiVanChuyen);

        t.Db.GioHang.First().SoLuong = 3; await t.Db.SaveChangesAsync();
        var tam2 = await svc.TinhTienAsync(kh.MaND, dc, null);
        Assert.Equal(0, tam2.PhiVanChuyen);
    }

    [Fact]
    public async Task VuotHanMucCOD_BiTuChoi()   // US12 – AC2, BR07
    {
        using var t = new TestDb();
        var kh = t.ThemKhach(); var dc = t.ThemDiaChi(kh.MaND);
        var sp = t.ThemSanPham(529_000, (200, 10));
        t.ThemVaoGio(kh.MaND, sp.MaSP, 4);   // 2.116.000đ

        var ex = await Assert.ThrowsAsync<BusinessException>(() =>
            t.DonHangService().TaoDonAsync(kh.MaND, new TaoDonRequest(dc.MaDC, PhuongThucThanhToan.COD, null, null)));
        Assert.Equal("COD_LIMIT_EXCEEDED", ex.Code);
        Assert.Equal(10, await new TonKhoService(t.Db).TonKhaDungAsync(sp.MaSP));   // không giữ hàng
    }

    [Fact]
    public async Task DoiGiaSanPham_KhongAnhHuongDonCu()   // BR11
    {
        using var t = new TestDb();
        var kh = t.ThemKhach(); var dc = t.ThemDiaChi(kh.MaND);
        var sp = t.ThemSanPham(100_000, (100, 10));
        t.ThemVaoGio(kh.MaND, sp.MaSP, 1);
        var don = await t.DonHangService().TaoDonAsync(kh.MaND, new TaoDonRequest(dc.MaDC, PhuongThucThanhToan.COD, null, null));

        sp.GiaBan = 150_000; await t.Db.SaveChangesAsync();

        var ct = await t.Db.ChiTietDonHang.AsNoTracking().SingleAsync(c => c.MaDH == don.MaDH);
        Assert.Equal(100_000, ct.DonGia);
    }

    [Fact]
    public async Task KhachKhongHuyDuocDonDaXacNhan()   // BR09
    {
        using var t = new TestDb();
        var kh = t.ThemKhach(); var dc = t.ThemDiaChi(kh.MaND);
        var sp = t.ThemSanPham(100_000, (100, 10));
        t.ThemVaoGio(kh.MaND, sp.MaSP, 1);
        var svc = t.DonHangService();
        var don = await svc.TaoDonAsync(kh.MaND, new TaoDonRequest(dc.MaDC, PhuongThucThanhToan.COD, null, null));
        await svc.CapNhatTrangThaiAsync(don.MaDH, TrangThaiDon.DaXacNhan, null, null);

        var ex = await Assert.ThrowsAsync<BusinessException>(() => svc.HuyDonAsync(don.MaDH, kh.MaND, true, "Đổi ý"));
        Assert.Equal("CANNOT_CANCEL", ex.Code);
    }

    [Fact]
    public async Task ChuyenTrangThaiSaiThuTu_BiTuChoi()   // US19 – AC3, BR10
    {
        using var t = new TestDb();
        var kh = t.ThemKhach(); var dc = t.ThemDiaChi(kh.MaND);
        var sp = t.ThemSanPham(100_000, (100, 10));
        t.ThemVaoGio(kh.MaND, sp.MaSP, 1);
        var svc = t.DonHangService();
        var don = await svc.TaoDonAsync(kh.MaND, new TaoDonRequest(dc.MaDC, PhuongThucThanhToan.COD, null, null));

        var ex = await Assert.ThrowsAsync<BusinessException>(() => svc.CapNhatTrangThaiAsync(don.MaDH, TrangThaiDon.DaGiao, null, null));
        Assert.Equal("INVALID_TRANSITION", ex.Code);
    }

    [Fact]
    public async Task GiaoThanhCong_DonCOD_GhiNhanDaThuTien()
    {
        using var t = new TestDb();
        var kh = t.ThemKhach(); var dc = t.ThemDiaChi(kh.MaND);
        var sp = t.ThemSanPham(100_000, (100, 10));
        t.ThemVaoGio(kh.MaND, sp.MaSP, 1);
        var svc = t.DonHangService();
        var don = await svc.TaoDonAsync(kh.MaND, new TaoDonRequest(dc.MaDC, PhuongThucThanhToan.COD, null, null));
        await svc.CapNhatTrangThaiAsync(don.MaDH, TrangThaiDon.DaXacNhan, null, null);
        await svc.CapNhatTrangThaiAsync(don.MaDH, TrangThaiDon.DangDongGoi, null, null);
        await svc.TaoVanDonAsync(don.MaDH, kh.MaND);
        var kq = await svc.CapNhatTrangThaiAsync(don.MaDH, TrangThaiDon.DaGiao, null, "GHN: delivered");

        Assert.Equal(TrangThaiThanhToan.DaThuCOD, kq.TrangThaiThanhToan);
        Assert.StartsWith("FAKE", kq.MaVanDonGHN);
        Assert.Equal(5, kq.LichSu.Count);
    }

    [Theory]
    [InlineData(TrangThaiDon.ChoXacNhan, TrangThaiDon.DaXacNhan, true)]
    [InlineData(TrangThaiDon.DaXacNhan, TrangThaiDon.DangDongGoi, true)]
    [InlineData(TrangThaiDon.DangGiao, TrangThaiDon.GiaoThatBai, true)]
    [InlineData(TrangThaiDon.ChoXacNhan, TrangThaiDon.DangGiao, false)]
    [InlineData(TrangThaiDon.DangGiao, TrangThaiDon.DaHuy, false)]
    [InlineData(TrangThaiDon.DaGiao, TrangThaiDon.DaHuy, false)]
    public void OrderStateMachine_KiemTraChuyenTrangThai(TrangThaiDon tu, TrangThaiDon den, bool hopLe) =>
        Assert.Equal(hopLe, OrderStateMachine.CoTheChuyen(tu, den));
}

/// <summary>US15 – Thanh toán VNPay (BR08, NFR06).</summary>
public class VnPayTests
{
    [Fact]
    public void UrlThanhToan_CoChuKyHopLe_VaPhatHienSuaDoi()
    {
        var vnp = TestDb.VnPay();
        var url = vnp.TaoUrlThanhToan(123, 325_000, "127.0.0.1", new DateTime(2026, 11, 25, 3, 0, 0, DateTimeKind.Utc));
        var q = Microsoft.AspNetCore.WebUtilities.QueryHelpers.ParseQuery(new Uri(url).Query)
                .ToDictionary(x => x.Key, x => x.Value.ToString());

        Assert.Equal("32500000", q["vnp_Amount"]);
        Assert.Equal("20261125100000", q["vnp_CreateDate"]);   // giờ Việt Nam
        Assert.True(vnp.XacThucChuKy(q));

        q["vnp_Amount"] = "100";
        Assert.False(vnp.XacThucChuKy(q));
    }

    private static async Task<(TestDb t, DonHang don, ThanhToanService svc)> TaoDonVnPay()
    {
        var t = new TestDb();
        var kh = t.ThemKhach(); var dc = t.ThemDiaChi(kh.MaND);
        var sp = t.ThemSanPham(150_000, (100, 10));
        t.ThemVaoGio(kh.MaND, sp.MaSP, 2);
        var dh = t.DonHangService();
        var don = await dh.TaoDonAsync(kh.MaND, new TaoDonRequest(dc.MaDC, PhuongThucThanhToan.VNPAY, null, null));
        return (t, don, new ThanhToanService(t.Db, TestDb.VnPay(), dh, NullLogger<ThanhToanService>.Instance));
    }

    [Fact]
    public async Task Ipn_HopLe_CapNhatDonDaThanhToan()   // AC1
    {
        var (t, don, svc) = await TaoDonVnPay();
        using var _ = t;
        var r = await svc.XuLyIpnAsync(TestDb.IpnKyHopLe(don.MaDH, (long)don.TongThanhToan * 100));

        Assert.Equal("00", r.RspCode);
        Assert.Equal(TrangThaiDon.ChoXacNhan, don.TrangThai);
        Assert.Equal(TrangThaiThanhToan.DaThanhToan, don.TrangThaiThanhToan);
        Assert.Single(t.Db.ThanhToan);
    }

    [Fact]
    public async Task Ipn_SaiChuKy_TraVe97()   // AC2
    {
        var (t, don, svc) = await TaoDonVnPay();
        using var _ = t;
        var r = await svc.XuLyIpnAsync(TestDb.IpnKyHopLe(don.MaDH, (long)don.TongThanhToan * 100, hashSecret: "KHOA-GIA-MAO-KHONG-DUNG-1234567890"));
        Assert.Equal("97", r.RspCode);
        Assert.Equal(TrangThaiDon.ChoThanhToan, don.TrangThai);
    }

    [Fact]
    public async Task Ipn_SaiSoTien_TraVe04()   // AC2
    {
        var (t, don, svc) = await TaoDonVnPay();
        using var _ = t;
        var r = await svc.XuLyIpnAsync(TestDb.IpnKyHopLe(don.MaDH, 100));
        Assert.Equal("04", r.RspCode);
    }

    [Fact]
    public async Task Ipn_GuiLai_KhongGhiNhanTrung()   // AC4
    {
        var (t, don, svc) = await TaoDonVnPay();
        using var _ = t;
        var ipn = TestDb.IpnKyHopLe(don.MaDH, (long)don.TongThanhToan * 100);
        await svc.XuLyIpnAsync(ipn);
        var lan2 = await svc.XuLyIpnAsync(ipn);

        Assert.Equal("02", lan2.RspCode);
        Assert.Single(t.Db.ThanhToan);
    }
}

/// <summary>US01 – Đăng nhập, khóa tạm sau 5 lần sai (NFR04).</summary>
public class AuthServiceTests
{
    [Fact]
    public async Task DangNhapSai5Lan_BiKhoa15Phut()
    {
        using var t = new TestDb();
        t.ThemKhach("khoa@test.vn");
        var auth = new AuthService(t.Db, Options.Create(new JwtOptions { Key = new string('k', 40) }), null!, null!);
        var now = DateTime.UtcNow;
        for (var i = 0; i < 5; i++)
            await Assert.ThrowsAsync<BusinessException>(() => auth.DangNhapAsync(new LoginRequest("khoa@test.vn", "SaiMatKhau1"), now));

        var ex = await Assert.ThrowsAsync<BusinessException>(() => auth.DangNhapAsync(new LoginRequest("khoa@test.vn", "Matkhau123"), now.AddMinutes(1)));
        Assert.Equal("ACCOUNT_LOCKED", ex.Code);

        var ok = await auth.DangNhapAsync(new LoginRequest("khoa@test.vn", "Matkhau123"), now.AddMinutes(16));
        Assert.Equal(VaiTros.KhachHang, ok.VaiTro);
    }

    [Fact]
    public async Task DangKy_EmailTrung_BiTuChoi()
    {
        using var t = new TestDb();
        t.ThemKhach("trung@test.vn");
        var auth = new AuthService(t.Db, Options.Create(new JwtOptions { Key = new string('k', 40) }), null!, null!);
        var ex = await Assert.ThrowsAsync<BusinessException>(() => auth.DangKyAsync(new RegisterRequest("Trung@Test.vn", "Matkhau123", "A", null)));
        Assert.Equal("EMAIL_EXISTS", ex.Code);
    }

    [Theory]
    [InlineData("Bánh quy Bơ Đan Mạch", "banh quy bo dan mach")]
    [InlineData("  KẸO dẻo  ", "keo deo")]
    public void BoDau_TimKiemKhongDau(string vao, string ra) => Assert.Equal(ra, TextUtil.BoDau(vao));
}
