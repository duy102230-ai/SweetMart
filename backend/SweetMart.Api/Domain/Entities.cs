namespace SweetMart.Api.Domain;

public class VaiTro
{
    public int MaVaiTro { get; set; }
    public string TenVaiTro { get; set; } = "";
}

public class NguoiDung
{
    public int MaND { get; set; }
    public int MaVaiTro { get; set; }
    public VaiTro? VaiTro { get; set; }
    public string HoTen { get; set; } = "";
    public string Email { get; set; } = "";
    public string MatKhauHash { get; set; } = "";
    public string? SoDienThoai { get; set; }
    public bool HoatDong { get; set; } = true;
    public int SoLanDangNhapSai { get; set; }
    public DateTime? KhoaDen { get; set; }
    public DateTime NgayTao { get; set; } = DateTime.UtcNow;
    public string? MaDatLaiMatKhau { get; set; }
    public DateTime? HanDatLaiMatKhau { get; set; }
}

public class DiaChi
{
    public int MaDC { get; set; }
    public int MaND { get; set; }
    public string NguoiNhan { get; set; } = "";
    public string SoDienThoai { get; set; } = "";
    public string DiaChiChiTiet { get; set; } = "";
    /// <summary>Mã quận/huyện theo danh mục địa chính của GHN (dùng để tính phí, tạo vận đơn).</summary>
    public int MaQuanHuyenGHN { get; set; }
    public string MaPhuongXaGHN { get; set; } = "";
    public bool MacDinh { get; set; }
}

public class DanhMuc
{
    public int MaDM { get; set; }
    public string TenDanhMuc { get; set; } = "";
    public int? MaDMCha { get; set; }
    public DanhMuc? DanhMucCha { get; set; }
}

public class SanPham
{
    public int MaSP { get; set; }
    public int MaDM { get; set; }
    public DanhMuc? DanhMuc { get; set; }
    public string TenSP { get; set; } = "";
    /// <summary>Tên viết thường, bỏ dấu – phục vụ tìm kiếm không dấu.</summary>
    public string TenKhongDau { get; set; } = "";
    public string? ThuongHieu { get; set; }
    public decimal GiaBan { get; set; }
    public string DonViTinh { get; set; } = "gói";
    public int KhoiLuongGram { get; set; }
    public string? MoTa { get; set; }
    public bool DangBan { get; set; } = true;
    public List<HinhAnhSP> HinhAnh { get; set; } = new();
    public List<LoHang> LoHang { get; set; } = new();
}

public class HinhAnhSP
{
    public int MaHA { get; set; }
    public int MaSP { get; set; }
    public string DuongDan { get; set; } = "";
}

public class LoHang
{
    public int MaLo { get; set; }
    public int MaSP { get; set; }
    public SanPham? SanPham { get; set; }
    public int SoLuongNhap { get; set; }
    public int SoLuongTon { get; set; }
    public DateOnly? NgaySanXuat { get; set; }
    public DateOnly HanSuDung { get; set; }
    public DateOnly NgayNhap { get; set; }

    public bool ConHan(DateOnly homNay) => HanSuDung > homNay;
    public bool LaCanDate(DateOnly homNay) => ConHan(homNay) && HanSuDung.DayNumber - homNay.DayNumber <= BusinessRules.SoNgayCanDate;
}

public class GioHang
{
    public int MaND { get; set; }
    public int MaSP { get; set; }
    public SanPham? SanPham { get; set; }
    public int SoLuong { get; set; }
}

public class KhuyenMai
{
    public int MaKM { get; set; }
    public string MaCode { get; set; } = "";
    public LoaiGiam LoaiGiam { get; set; }
    public decimal GiaTriGiam { get; set; }
    /// <summary>Số tiền giảm tối đa khi giảm theo phần trăm (null = không giới hạn).</summary>
    public decimal? GiamToiDa { get; set; }
    public decimal DonToiThieu { get; set; }
    public DateTime NgayBatDau { get; set; }
    public DateTime NgayKetThuc { get; set; }
    public int SoLuotConLai { get; set; }
}

public class DonHang
{
    public int MaDH { get; set; }
    public int MaND { get; set; }
    public NguoiDung? NguoiDung { get; set; }
    public int? MaKM { get; set; }
    public KhuyenMai? KhuyenMai { get; set; }
    public DateTime NgayDat { get; set; } = DateTime.UtcNow;
    public decimal TongTienHang { get; set; }
    public decimal PhiVanChuyen { get; set; }
    public decimal TienGiam { get; set; }
    public decimal TongThanhToan { get; set; }
    public PhuongThucThanhToan PhuongThucTT { get; set; }
    public string NguoiNhan { get; set; } = "";
    public string SoDienThoaiNhan { get; set; } = "";
    public string DiaChiGiao { get; set; } = "";
    public int MaQuanHuyenGHN { get; set; }
    public string MaPhuongXaGHN { get; set; } = "";
    public string? GhiChu { get; set; }
    public string? MaVanDonGHN { get; set; }
    public TrangThaiDon TrangThai { get; set; }
    public TrangThaiThanhToan TrangThaiThanhToan { get; set; }
    public List<ChiTietDonHang> ChiTiet { get; set; } = new();
    public List<ThanhToan> ThanhToan { get; set; } = new();
    public List<LichSuDonHang> LichSu { get; set; } = new();

    public string MaHienThi => $"SM{MaDH:D6}";
}

public class ChiTietDonHang
{
    public int MaDH { get; set; }
    public int MaSP { get; set; }
    public SanPham? SanPham { get; set; }
    public int SoLuong { get; set; }
    /// <summary>Đơn giá tại thời điểm đặt (BR11).</summary>
    public decimal DonGia { get; set; }
    public List<PhanBoLo> PhanBo { get; set; } = new();
}

/// <summary>Số lượng của một dòng hàng được xuất từ lô nào (một dòng có thể lấy từ nhiều lô theo FEFO).</summary>
public class PhanBoLo
{
    public int MaDH { get; set; }
    public int MaSP { get; set; }
    public int MaLo { get; set; }
    public LoHang? LoHang { get; set; }
    public int SoLuong { get; set; }
}

public class ThanhToan
{
    public int MaTT { get; set; }
    public int MaDH { get; set; }
    public decimal SoTien { get; set; }
    public string? MaGiaoDichVNPay { get; set; }
    public string? MaNganHang { get; set; }
    public string TrangThai { get; set; } = "";
    public DateTime ThoiGian { get; set; } = DateTime.UtcNow;
    public string? DuLieuIPN { get; set; }
}

public class LichSuDonHang
{
    public int MaLS { get; set; }
    public int MaDH { get; set; }
    public TrangThaiDon? TrangThaiCu { get; set; }
    public TrangThaiDon TrangThaiMoi { get; set; }
    public int? NguoiThucHien { get; set; }
    public DateTime ThoiGian { get; set; } = DateTime.UtcNow;
    public string? GhiChu { get; set; }
}

public class DanhGia
{
    public int MaDG { get; set; }
    public int MaND { get; set; }
    public NguoiDung? NguoiDung { get; set; }
    public int MaSP { get; set; }
    public int MaDH { get; set; }
    public int SoSao { get; set; }
    public string? NoiDung { get; set; }
    public DateTime NgayDanhGia { get; set; } = DateTime.UtcNow;
}
