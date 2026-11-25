using System.ComponentModel.DataAnnotations;
using SweetMart.Api.Domain;

namespace SweetMart.Api.Dtos;

// ---------- Tài khoản ----------
public record RegisterRequest(
    [Required, EmailAddress, MaxLength(150)] string Email,
    [Required, MinLength(8), RegularExpression(@"^(?=.*[A-Za-z])(?=.*\d).+$", ErrorMessage = "Mật khẩu phải có cả chữ và số.")] string MatKhau,
    [Required, MaxLength(100)] string HoTen,
    [MaxLength(15)] string? SoDienThoai);

public record LoginRequest([Required, EmailAddress] string Email, [Required] string MatKhau);
public record ForgotPasswordRequest([Required, EmailAddress] string Email);
public record ResetPasswordRequest([Required] string Token, [Required, MinLength(8)] string MatKhauMoi);
public record AuthResponse(string Token, int MaND, string HoTen, string Email, string VaiTro);

public record DiaChiRequest(
    [Required, MaxLength(100)] string NguoiNhan,
    [Required, MaxLength(15)] string SoDienThoai,
    [Required, MaxLength(300)] string DiaChiChiTiet,
    [Range(1, int.MaxValue)] int MaQuanHuyenGHN,
    [Required] string MaPhuongXaGHN,
    bool MacDinh);

public record TaoNhanVienRequest([Required, EmailAddress] string Email, [Required, MinLength(8)] string MatKhau,
    [Required] string HoTen, [Range(2, 4)] int MaVaiTro);

// ---------- Sản phẩm ----------
public record SanPhamListItem(int MaSP, string TenSP, string? ThuongHieu, decimal GiaBan, string DonViTinh,
    string? HinhAnh, int TonKhaDung, string TenDanhMuc);

public record SanPhamDetail(int MaSP, string TenSP, string? ThuongHieu, decimal GiaBan, string DonViTinh, int KhoiLuongGram,
    string? MoTa, int MaDM, string TenDanhMuc, List<string> HinhAnh, int TonKhaDung, DateOnly? HanSuDungGanNhat,
    double? DiemTrungBinh, int SoDanhGia);

public record SanPhamRequest(
    [Required, MaxLength(200)] string TenSP,
    [Range(1, int.MaxValue)] int MaDM,
    [MaxLength(100)] string? ThuongHieu,
    [Range(1, 1_000_000_000)] decimal GiaBan,
    [Required, MaxLength(20)] string DonViTinh,
    [Range(1, 100_000)] int KhoiLuongGram,
    string? MoTa,
    [MinLength(1)] List<string> HinhAnh,
    bool DangBan = true);

public record DanhMucRequest([Required, MaxLength(100)] string TenDanhMuc, int? MaDMCha);

public record NhapLoRequest([Range(1, int.MaxValue)] int MaSP, [Range(1, 100_000)] int SoLuong, DateOnly? NgaySanXuat, DateOnly HanSuDung);

public record LoHangDto(int MaLo, int MaSP, string TenSP, int SoLuongNhap, int SoLuongTon, DateOnly? NgaySanXuat,
    DateOnly HanSuDung, DateOnly NgayNhap, bool CanDate, bool HetHan);

// ---------- Giỏ hàng, đơn hàng ----------
public record CartItemRequest([Range(1, int.MaxValue)] int MaSP, [Range(1, 999)] int SoLuong);
public record CartItemDto(int MaSP, string TenSP, string? HinhAnh, decimal GiaBan, int SoLuong, int TonKhaDung, decimal ThanhTien);

public record TinhPhiRequest([Range(1, int.MaxValue)] int MaDC, string? MaCode);
public record TinhPhiResponse(decimal TongTienHang, decimal TienGiam, decimal PhiVanChuyen, decimal TongThanhToan, bool ChoPhepCOD);

public record TaoDonRequest([Range(1, int.MaxValue)] int MaDC, PhuongThucThanhToan PhuongThucTT, string? MaCode, [MaxLength(500)] string? GhiChu);
public record TaoDonResponse(int MaDH, string MaHienThi, string TrangThai, decimal TongThanhToan, string? PaymentUrl);

public record ChiTietDto(int MaSP, string TenSP, int SoLuong, decimal DonGia, decimal ThanhTien);
public record LichSuDto(string? TrangThaiCu, string TrangThaiMoi, DateTime ThoiGian, string? GhiChu);

public record DonHangDto(int MaDH, string MaHienThi, DateTime NgayDat, string TrangThai, string TrangThaiThanhToan,
    string PhuongThucTT, decimal TongTienHang, decimal PhiVanChuyen, decimal TienGiam, decimal TongThanhToan,
    string NguoiNhan, string SoDienThoaiNhan, string DiaChiGiao, string? GhiChu, string? MaVanDonGHN,
    List<ChiTietDto> ChiTiet, List<LichSuDto> LichSu);

public record CapNhatTrangThaiRequest(TrangThaiDon TrangThaiMoi, [MaxLength(500)] string? GhiChu);
public record HuyDonRequest([Required, MaxLength(500)] string LyDo);

public record KhuyenMaiRequest([Required, MaxLength(30)] string MaCode, LoaiGiam LoaiGiam, [Range(1, 100_000_000)] decimal GiaTriGiam,
    decimal? GiamToiDa, [Range(0, 100_000_000)] decimal DonToiThieu, DateTime NgayBatDau, DateTime NgayKetThuc, [Range(0, 1_000_000)] int SoLuotConLai);

public record DanhGiaRequest([Range(1, int.MaxValue)] int MaDH, [Range(1, int.MaxValue)] int MaSP, [Range(1, 5)] int SoSao, [MaxLength(1000)] string? NoiDung);
public record DanhGiaDto(string HoTen, int SoSao, string? NoiDung, DateTime NgayDanhGia);

// ---------- Báo cáo ----------
public record DoanhThuNgay(DateOnly Ngay, int SoDon, decimal DoanhThu);
public record TopSanPham(int MaSP, string TenSP, int SoLuongBan, decimal DoanhThu);
public record BaoCaoDoanhThu(DateOnly TuNgay, DateOnly DenNgay, decimal TongDoanhThu, int TongSoDon,
    List<DoanhThuNgay> TheoNgay, List<TopSanPham> TopSanPham, Dictionary<string, int> DonTheoTrangThai);
