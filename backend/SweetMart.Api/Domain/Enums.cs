namespace SweetMart.Api.Domain;

public enum LoaiGiam { PhanTram = 1, SoTien = 2 }

public enum PhuongThucThanhToan { COD = 1, VNPAY = 2 }

public enum TrangThaiDon
{
    ChoThanhToan = 1,
    ChoXacNhan = 2,
    DaXacNhan = 3,
    DangDongGoi = 4,
    DangGiao = 5,
    DaGiao = 6,
    GiaoThatBai = 7,
    DaHuy = 8
}

public enum TrangThaiThanhToan
{
    ChuaThu = 1,        // COD, chưa giao
    ChoThanhToan = 2,   // VNPay, chờ IPN
    DaThanhToan = 3,    // VNPay thành công
    ThatBai = 4,        // VNPay lỗi / hết hạn
    ChoHoanTien = 5,    // Đã trả tiền nhưng đơn bị hủy
    DaThuCOD = 6,
    KhongThuDuoc = 7
}

public static class VaiTros
{
    public const int MaKhachHang = 1, MaNhanVien = 2, MaQuanLy = 3, MaQuanTri = 4;
    public const string KhachHang = "KhachHang", NhanVien = "NhanVien", QuanLy = "QuanLy", QuanTri = "QuanTri";
    public const string NoiBo = NhanVien + "," + QuanLy;
}

/// <summary>Các hằng số của quy tắc nghiệp vụ (Bước 2 – mục 1.3).</summary>
public static class BusinessRules
{
    public const int SoNgayCanDate = 30;              // BR03
    public const decimal MienPhiShipTu = 300_000m;    // BR05
    public const decimal PhiShipMacDinh = 30_000m;    // dùng khi GHN lỗi
    public const decimal HanMucCOD = 2_000_000m;      // BR07
    public const int PhutChoThanhToan = 15;           // BR08
    public const int SoLanSaiToiDa = 5;               // NFR04
    public const int PhutKhoaDangNhap = 15;           // NFR04
}
