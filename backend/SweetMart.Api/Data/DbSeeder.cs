using Microsoft.EntityFrameworkCore;
using SweetMart.Api.Common;
using SweetMart.Api.Domain;

namespace SweetMart.Api.Data;

/// <summary>Dữ liệu mẫu cho môi trường Dev/Test: tài khoản theo vai trò, danh mục, sản phẩm, lô hàng, mã giảm giá.</summary>
public static class DbSeeder
{
    public static async Task SeedAsync(AppDbContext db, IConfiguration config)
    {
        if (!await db.NguoiDung.AnyAsync())
        {
            var pass = config["Seed:DefaultPassword"] ?? throw new InvalidOperationException("Thiếu cấu hình Seed:DefaultPassword");
            var hash = BCrypt.Net.BCrypt.HashPassword(pass);
            db.NguoiDung.AddRange(
                new NguoiDung { Email = "quantri@sweetmart.test", HoTen = "Quản trị hệ thống", MaVaiTro = VaiTros.MaQuanTri, MatKhauHash = hash },
                new NguoiDung { Email = "quanly@sweetmart.test", HoTen = "Chủ cửa hàng", MaVaiTro = VaiTros.MaQuanLy, MatKhauHash = hash },
                new NguoiDung { Email = "nhanvien@sweetmart.test", HoTen = "Nhân viên bán hàng", MaVaiTro = VaiTros.MaNhanVien, MatKhauHash = hash },
                new NguoiDung { Email = "khachhang@sweetmart.test", HoTen = "Nguyễn Văn Khách", MaVaiTro = VaiTros.MaKhachHang, MatKhauHash = hash, SoDienThoai = "0900000001" });
            await db.SaveChangesAsync();
            var kh = await db.NguoiDung.FirstAsync(u => u.Email == "khachhang@sweetmart.test");
            db.DiaChi.Add(new DiaChi
            {
                MaND = kh.MaND, NguoiNhan = "Nguyễn Văn Khách", SoDienThoai = "0900000001",
                DiaChiChiTiet = "484 Lạch Tray, Kênh Dương, Lê Chân, Hải Phòng", MaQuanHuyenGHN = 1588, MaPhuongXaGHN = "30210", MacDinh = true
            });
            await db.SaveChangesAsync();
        }

        if (await db.DanhMuc.AnyAsync()) return;

        string[] tenDM = ["Bánh quy", "Kẹo", "Socola", "Bánh ngọt đóng gói", "Hộp quà Tết"];
        var dms = tenDM.Select(t => new DanhMuc { TenDanhMuc = t }).ToList();
        db.DanhMuc.AddRange(dms);
        await db.SaveChangesAsync();

        var hom = Clock.HomNayVN();
        (string ten, int dm, string hieu, decimal gia, string dvt, int gram, int[] hanNgay)[] sp =
        [
            ("Bánh quy bơ hộp thiếc 454g", 0, "Danisa", 165_000, "hộp", 454, [20, 240]),
            ("Bánh quy socola chip 300g", 0, "Cosy", 52_000, "gói", 300, [180]),
            ("Bánh quy yến mạch 400g", 0, "Kinh Đô", 68_000, "gói", 400, [25, 200]),
            ("Bánh quy bơ sữa Butter Cookies 340g", 0, "Kjeldsens", 135_000, "hộp", 340, [300]),
            ("Kẹo dẻo trái cây 200g", 1, "Haribo", 45_000, "gói", 200, [150]),
            ("Kẹo sữa bò 150g", 1, "Alpenliebe", 28_000, "gói", 150, [10, 120]),
            ("Kẹo bạc hà không đường 35g", 1, "Mentos", 18_000, "hộp", 35, [365]),
            ("Kẹo mút hương trái cây (túi 30 cây)", 1, "Chupa Chups", 75_000, "túi", 360, [270]),
            ("Socola sữa thanh 100g", 2, "Kinh Đô", 32_000, "thanh", 100, [60, 200]),
            ("Socola đen 70% cacao 100g", 2, "Marou", 89_000, "thanh", 100, [220]),
            ("Socola viên phủ đậu phộng 180g", 2, "M&M's", 59_000, "gói", 180, [28, 160]),
            ("Bánh bông lan cuộn kem 360g", 3, "Solite", 55_000, "hộp", 360, [45]),
            ("Bánh trứng Custas 282g", 3, "Orion", 62_000, "hộp", 282, [90]),
            ("Bánh Chocopie 12 cái", 3, "Orion", 58_000, "hộp", 396, [15, 110]),
            ("Hộp quà Tết Phú Quý 900g", 4, "SweetMart", 389_000, "hộp", 900, [200]),
            ("Hộp quà Tết An Khang 1,2kg", 4, "SweetMart", 529_000, "hộp", 1200, [210]),
        ];
        foreach (var (ten, dm, hieu, gia, dvt, gram, hanNgay) in sp)
        {
            var p = new SanPham
            {
                TenSP = ten, TenKhongDau = TextUtil.BoDau(ten + " " + hieu), MaDM = dms[dm].MaDM, ThuongHieu = hieu, GiaBan = gia,
                DonViTinh = dvt, KhoiLuongGram = gram, MoTa = $"{ten} – thương hiệu {hieu}. Bảo quản nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp.",
                HinhAnh = [new HinhAnhSP { DuongDan = $"https://placehold.co/600x600/FCE8EF/E85D8A?text={Uri.EscapeDataString(hieu)}" }]
            };
            foreach (var h in hanNgay)
                p.LoHang.Add(new LoHang { SoLuongNhap = 40, SoLuongTon = 40, NgayNhap = hom.AddDays(-10), NgaySanXuat = hom.AddDays(-60), HanSuDung = hom.AddDays(h) });
            db.SanPham.Add(p);
        }
        db.KhuyenMai.AddRange(
            new KhuyenMai { MaCode = "CHAOBAN", LoaiGiam = LoaiGiam.SoTien, GiaTriGiam = 20_000, DonToiThieu = 150_000, NgayBatDau = DateTime.UtcNow.AddDays(-1), NgayKetThuc = DateTime.UtcNow.AddMonths(6), SoLuotConLai = 500 },
            new KhuyenMai { MaCode = "TET2027", LoaiGiam = LoaiGiam.PhanTram, GiaTriGiam = 10, GiamToiDa = 100_000, DonToiThieu = 300_000, NgayBatDau = DateTime.UtcNow.AddDays(-1), NgayKetThuc = DateTime.UtcNow.AddMonths(3), SoLuotConLai = 200 });
        await db.SaveChangesAsync();
    }
}
