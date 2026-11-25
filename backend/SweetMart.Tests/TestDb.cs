using System.Net;
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using SweetMart.Api.Common;
using SweetMart.Api.Data;
using SweetMart.Api.Domain;
using SweetMart.Api.Integrations;
using SweetMart.Api.Services;

namespace SweetMart.Tests;

/// <summary>CSDL SQLite trong bộ nhớ – có transaction và ràng buộc thật, mỗi test một CSDL riêng.</summary>
public sealed class TestDb : IDisposable
{
    private readonly SqliteConnection _conn;
    public AppDbContext Db { get; }
    public const string HashSecret = "TESTSECRET0123456789ABCDEFGHIJKL";

    public TestDb()
    {
        _conn = new SqliteConnection("DataSource=:memory:");
        _conn.Open();
        Db = new AppDbContext(new DbContextOptionsBuilder<AppDbContext>().UseSqlite(_conn).Options);
        Db.Database.EnsureCreated();
    }

    public static DateOnly HomNay => Clock.HomNayVN();

    public NguoiDung ThemKhach(string email = "khach@test.vn")
    {
        var u = new NguoiDung { Email = email, HoTen = "Khách Test", MaVaiTro = VaiTros.MaKhachHang, MatKhauHash = BCrypt.Net.BCrypt.HashPassword("Matkhau123") };
        Db.NguoiDung.Add(u);
        Db.SaveChanges();
        return u;
    }

    public DiaChi ThemDiaChi(int maND)
    {
        var dc = new DiaChi { MaND = maND, NguoiNhan = "Khách Test", SoDienThoai = "0900000000", DiaChiChiTiet = "Hải Phòng", MaQuanHuyenGHN = 1588, MaPhuongXaGHN = "30210", MacDinh = true };
        Db.DiaChi.Add(dc);
        Db.SaveChanges();
        return dc;
    }

    /// <summary>Thêm sản phẩm với các lô (số ngày còn hạn so với hôm nay, số lượng).</summary>
    public SanPham ThemSanPham(decimal gia, params (int hanNgay, int soLuong)[] lo)
    {
        if (!Db.DanhMuc.Any()) { Db.DanhMuc.Add(new DanhMuc { TenDanhMuc = "Kẹo" }); Db.SaveChanges(); }
        var sp = new SanPham { TenSP = "SP " + gia, TenKhongDau = "sp", MaDM = Db.DanhMuc.First().MaDM, GiaBan = gia, KhoiLuongGram = 200 };
        foreach (var (han, sl) in lo)
            sp.LoHang.Add(new LoHang { SoLuongNhap = sl, SoLuongTon = sl, NgayNhap = HomNay.AddDays(-400), HanSuDung = HomNay.AddDays(han) });
        Db.SanPham.Add(sp);
        Db.SaveChanges();
        return sp;
    }

    public void ThemVaoGio(int maND, int maSP, int soLuong)
    {
        Db.GioHang.Add(new GioHang { MaND = maND, MaSP = maSP, SoLuong = soLuong });
        Db.SaveChanges();
    }

    public DonHangService DonHangService(IGhnClient? ghn = null)
    {
        var sp = new ServiceCollection().AddLogging().AddScoped<IEmailSender, LogEmailSender>().BuildServiceProvider();
        var email = new EmailQueue(sp.GetRequiredService<IServiceScopeFactory>(), NullLogger<EmailQueue>.Instance);
        return new DonHangService(Db, new TonKhoService(Db), new KhuyenMaiService(Db), ghn ?? new FakeGhnClient(), email, NullLogger<DonHangService>.Instance);
    }

    public static VnPayClient VnPay() => new(Options.Create(new VnPayOptions { TmnCode = "TESTTMN1", HashSecret = HashSecret }));

    /// <summary>Tạo bộ tham số IPN có chữ ký đúng (cài đặt độc lập theo tài liệu VNPay để đối chiếu).</summary>
    public static Dictionary<string, string> IpnKyHopLe(int maDH, long amountX100, string responseCode = "00", string? hashSecret = null)
    {
        var p = new SortedDictionary<string, string>(StringComparer.Ordinal)
        {
            ["vnp_Amount"] = amountX100.ToString(),
            ["vnp_BankCode"] = "NCB",
            ["vnp_OrderInfo"] = $"Thanh toan don hang SM{maDH:D6}",
            ["vnp_ResponseCode"] = responseCode,
            ["vnp_TmnCode"] = "TESTTMN1",
            ["vnp_TransactionNo"] = "1400" + maDH,
            ["vnp_TransactionStatus"] = responseCode,
            ["vnp_TxnRef"] = maDH.ToString(),
        };
        var data = string.Join("&", p.Select(x => $"{WebUtility.UrlEncode(x.Key)}={WebUtility.UrlEncode(x.Value)}"));
        var dict = new Dictionary<string, string>(p) { ["vnp_SecureHash"] = VnPayClient.HmacSha512(hashSecret ?? HashSecret, data) };
        return dict;
    }

    public void Dispose()
    {
        Db.Dispose();
        _conn.Dispose();
    }
}
