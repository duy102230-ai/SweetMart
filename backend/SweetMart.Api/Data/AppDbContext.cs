using Microsoft.EntityFrameworkCore;
using SweetMart.Api.Domain;

namespace SweetMart.Api.Data;

public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<VaiTro> VaiTro => Set<VaiTro>();
    public DbSet<NguoiDung> NguoiDung => Set<NguoiDung>();
    public DbSet<DiaChi> DiaChi => Set<DiaChi>();
    public DbSet<DanhMuc> DanhMuc => Set<DanhMuc>();
    public DbSet<SanPham> SanPham => Set<SanPham>();
    public DbSet<HinhAnhSP> HinhAnhSP => Set<HinhAnhSP>();
    public DbSet<LoHang> LoHang => Set<LoHang>();
    public DbSet<GioHang> GioHang => Set<GioHang>();
    public DbSet<KhuyenMai> KhuyenMai => Set<KhuyenMai>();
    public DbSet<DonHang> DonHang => Set<DonHang>();
    public DbSet<ChiTietDonHang> ChiTietDonHang => Set<ChiTietDonHang>();
    public DbSet<PhanBoLo> PhanBoLo => Set<PhanBoLo>();
    public DbSet<ThanhToan> ThanhToan => Set<ThanhToan>();
    public DbSet<LichSuDonHang> LichSuDonHang => Set<LichSuDonHang>();
    public DbSet<DanhGia> DanhGia => Set<DanhGia>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.Entity<VaiTro>(e =>
        {
            e.HasKey(x => x.MaVaiTro);
            e.Property(x => x.MaVaiTro).ValueGeneratedNever();
            e.Property(x => x.TenVaiTro).HasMaxLength(30);
            e.HasData(new VaiTro { MaVaiTro = VaiTros.MaKhachHang, TenVaiTro = VaiTros.KhachHang },
                      new VaiTro { MaVaiTro = VaiTros.MaNhanVien, TenVaiTro = VaiTros.NhanVien },
                      new VaiTro { MaVaiTro = VaiTros.MaQuanLy, TenVaiTro = VaiTros.QuanLy },
                      new VaiTro { MaVaiTro = VaiTros.MaQuanTri, TenVaiTro = VaiTros.QuanTri });
        });

        b.Entity<NguoiDung>(e =>
        {
            e.HasKey(x => x.MaND);
            e.HasIndex(x => x.Email).IsUnique();
            e.Property(x => x.Email).HasMaxLength(150);
            e.Property(x => x.HoTen).HasMaxLength(100);
            e.Property(x => x.SoDienThoai).HasMaxLength(15);
            e.Property(x => x.MaDatLaiMatKhau).HasMaxLength(100);
            e.HasOne(x => x.VaiTro).WithMany().HasForeignKey(x => x.MaVaiTro).OnDelete(DeleteBehavior.Restrict);
        });

        b.Entity<DiaChi>(e =>
        {
            e.HasKey(x => x.MaDC);
            e.Property(x => x.NguoiNhan).HasMaxLength(100);
            e.Property(x => x.SoDienThoai).HasMaxLength(15);
            e.Property(x => x.DiaChiChiTiet).HasMaxLength(300);
            e.Property(x => x.MaPhuongXaGHN).HasMaxLength(20);
            e.HasOne<NguoiDung>().WithMany().HasForeignKey(x => x.MaND).OnDelete(DeleteBehavior.Cascade);
        });

        b.Entity<DanhMuc>(e =>
        {
            e.HasKey(x => x.MaDM);
            e.Property(x => x.TenDanhMuc).HasMaxLength(100);
            e.HasOne(x => x.DanhMucCha).WithMany().HasForeignKey(x => x.MaDMCha).OnDelete(DeleteBehavior.Restrict);
        });

        b.Entity<SanPham>(e =>
        {
            e.HasKey(x => x.MaSP);
            e.Property(x => x.TenSP).HasMaxLength(200);
            e.Property(x => x.TenKhongDau).HasMaxLength(200);
            e.Property(x => x.ThuongHieu).HasMaxLength(100);
            e.Property(x => x.DonViTinh).HasMaxLength(20);
            e.Property(x => x.GiaBan).HasPrecision(12, 0);
            e.HasIndex(x => x.TenKhongDau);
            e.HasOne(x => x.DanhMuc).WithMany().HasForeignKey(x => x.MaDM).OnDelete(DeleteBehavior.Restrict);
            e.ToTable(t => t.HasCheckConstraint("CK_SanPham_GiaBan", "[GiaBan] > 0"));
        });

        b.Entity<HinhAnhSP>(e =>
        {
            e.HasKey(x => x.MaHA);
            e.Property(x => x.DuongDan).HasMaxLength(500);
            e.HasOne<SanPham>().WithMany(x => x.HinhAnh).HasForeignKey(x => x.MaSP).OnDelete(DeleteBehavior.Cascade);
        });

        b.Entity<LoHang>(e =>
        {
            e.HasKey(x => x.MaLo);
            e.HasOne(x => x.SanPham).WithMany(x => x.LoHang).HasForeignKey(x => x.MaSP).OnDelete(DeleteBehavior.Restrict);
            e.HasIndex(x => new { x.MaSP, x.HanSuDung });
            e.ToTable(t =>
            {
                t.HasCheckConstraint("CK_LoHang_SoLuongTon", "[SoLuongTon] >= 0");
                t.HasCheckConstraint("CK_LoHang_HanSuDung", "[HanSuDung] > [NgayNhap]");
            });
        });

        b.Entity<GioHang>(e =>
        {
            e.HasKey(x => new { x.MaND, x.MaSP });
            e.HasOne<NguoiDung>().WithMany().HasForeignKey(x => x.MaND).OnDelete(DeleteBehavior.Cascade);
            e.HasOne(x => x.SanPham).WithMany().HasForeignKey(x => x.MaSP).OnDelete(DeleteBehavior.Cascade);
        });

        b.Entity<KhuyenMai>(e =>
        {
            e.HasKey(x => x.MaKM);
            e.Property(x => x.MaCode).HasMaxLength(30);
            e.HasIndex(x => x.MaCode).IsUnique();
            e.Property(x => x.GiaTriGiam).HasPrecision(12, 0);
            e.Property(x => x.GiamToiDa).HasPrecision(12, 0);
            e.Property(x => x.DonToiThieu).HasPrecision(12, 0);
            e.ToTable(t => t.HasCheckConstraint("CK_KhuyenMai_Ngay", "[NgayKetThuc] > [NgayBatDau]"));
        });

        b.Entity<DonHang>(e =>
        {
            e.HasKey(x => x.MaDH);
            e.Ignore(x => x.MaHienThi);
            e.Property(x => x.TongTienHang).HasPrecision(12, 0);
            e.Property(x => x.PhiVanChuyen).HasPrecision(12, 0);
            e.Property(x => x.TienGiam).HasPrecision(12, 0);
            e.Property(x => x.TongThanhToan).HasPrecision(12, 0);
            e.Property(x => x.NguoiNhan).HasMaxLength(100);
            e.Property(x => x.SoDienThoaiNhan).HasMaxLength(15);
            e.Property(x => x.DiaChiGiao).HasMaxLength(300);
            e.Property(x => x.MaPhuongXaGHN).HasMaxLength(20);
            e.Property(x => x.GhiChu).HasMaxLength(500);
            e.Property(x => x.MaVanDonGHN).HasMaxLength(50);
            e.Property(x => x.TrangThai).HasConversion<string>().HasMaxLength(20);
            e.Property(x => x.TrangThaiThanhToan).HasConversion<string>().HasMaxLength(20);
            e.Property(x => x.PhuongThucTT).HasConversion<string>().HasMaxLength(10);
            e.HasIndex(x => new { x.TrangThai, x.NgayDat });
            e.HasOne(x => x.NguoiDung).WithMany().HasForeignKey(x => x.MaND).OnDelete(DeleteBehavior.Restrict);
            e.HasOne(x => x.KhuyenMai).WithMany().HasForeignKey(x => x.MaKM).OnDelete(DeleteBehavior.Restrict);
        });

        b.Entity<ChiTietDonHang>(e =>
        {
            e.HasKey(x => new { x.MaDH, x.MaSP });
            e.Property(x => x.DonGia).HasPrecision(12, 0);
            e.HasOne<DonHang>().WithMany(x => x.ChiTiet).HasForeignKey(x => x.MaDH).OnDelete(DeleteBehavior.Cascade);
            e.HasOne(x => x.SanPham).WithMany().HasForeignKey(x => x.MaSP).OnDelete(DeleteBehavior.Restrict);
            e.ToTable(t => t.HasCheckConstraint("CK_ChiTiet_SoLuong", "[SoLuong] > 0"));
        });

        b.Entity<PhanBoLo>(e =>
        {
            e.HasKey(x => new { x.MaDH, x.MaSP, x.MaLo });
            e.HasOne<ChiTietDonHang>().WithMany(x => x.PhanBo).HasForeignKey(x => new { x.MaDH, x.MaSP }).OnDelete(DeleteBehavior.Cascade);
            e.HasOne(x => x.LoHang).WithMany().HasForeignKey(x => x.MaLo).OnDelete(DeleteBehavior.Restrict);
        });

        b.Entity<ThanhToan>(e =>
        {
            e.HasKey(x => x.MaTT);
            e.Property(x => x.SoTien).HasPrecision(12, 0);
            e.Property(x => x.MaGiaoDichVNPay).HasMaxLength(50);
            e.Property(x => x.MaNganHang).HasMaxLength(20);
            e.Property(x => x.TrangThai).HasMaxLength(20);
            e.HasIndex(x => x.MaGiaoDichVNPay).IsUnique().HasFilter("[MaGiaoDichVNPay] IS NOT NULL");
            e.HasOne<DonHang>().WithMany(x => x.ThanhToan).HasForeignKey(x => x.MaDH).OnDelete(DeleteBehavior.Cascade);
        });

        b.Entity<LichSuDonHang>(e =>
        {
            e.HasKey(x => x.MaLS);
            e.Property(x => x.TrangThaiCu).HasConversion<string>().HasMaxLength(20);
            e.Property(x => x.TrangThaiMoi).HasConversion<string>().HasMaxLength(20);
            e.Property(x => x.GhiChu).HasMaxLength(500);
            e.HasOne<DonHang>().WithMany(x => x.LichSu).HasForeignKey(x => x.MaDH).OnDelete(DeleteBehavior.Cascade);
            e.HasOne<NguoiDung>().WithMany().HasForeignKey(x => x.NguoiThucHien).OnDelete(DeleteBehavior.Restrict);
        });

        b.Entity<DanhGia>(e =>
        {
            e.HasKey(x => x.MaDG);
            e.Property(x => x.NoiDung).HasMaxLength(1000);
            e.HasIndex(x => new { x.MaDH, x.MaSP }).IsUnique();
            e.HasOne(x => x.NguoiDung).WithMany().HasForeignKey(x => x.MaND).OnDelete(DeleteBehavior.Restrict);
            e.HasOne<SanPham>().WithMany().HasForeignKey(x => x.MaSP).OnDelete(DeleteBehavior.Restrict);
            e.HasOne<DonHang>().WithMany().HasForeignKey(x => x.MaDH).OnDelete(DeleteBehavior.Restrict);
            e.ToTable(t => t.HasCheckConstraint("CK_DanhGia_SoSao", "[SoSao] BETWEEN 1 AND 5"));
        });
    }
}
