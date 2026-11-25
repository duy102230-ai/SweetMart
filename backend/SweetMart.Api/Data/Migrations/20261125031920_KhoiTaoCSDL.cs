using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

#pragma warning disable CA1814 // Prefer jagged arrays over multidimensional

namespace SweetMart.Api.Data.Migrations
{
    /// <inheritdoc />
    public partial class KhoiTaoCSDL : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "DanhMuc",
                columns: table => new
                {
                    MaDM = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    TenDanhMuc = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    MaDMCha = table.Column<int>(type: "int", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DanhMuc", x => x.MaDM);
                    table.ForeignKey(
                        name: "FK_DanhMuc_DanhMuc_MaDMCha",
                        column: x => x.MaDMCha,
                        principalTable: "DanhMuc",
                        principalColumn: "MaDM",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "KhuyenMai",
                columns: table => new
                {
                    MaKM = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaCode = table.Column<string>(type: "nvarchar(30)", maxLength: 30, nullable: false),
                    LoaiGiam = table.Column<int>(type: "int", nullable: false),
                    GiaTriGiam = table.Column<decimal>(type: "decimal(12,0)", precision: 12, scale: 0, nullable: false),
                    GiamToiDa = table.Column<decimal>(type: "decimal(12,0)", precision: 12, scale: 0, nullable: true),
                    DonToiThieu = table.Column<decimal>(type: "decimal(12,0)", precision: 12, scale: 0, nullable: false),
                    NgayBatDau = table.Column<DateTime>(type: "datetime2", nullable: false),
                    NgayKetThuc = table.Column<DateTime>(type: "datetime2", nullable: false),
                    SoLuotConLai = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_KhuyenMai", x => x.MaKM);
                    table.CheckConstraint("CK_KhuyenMai_Ngay", "[NgayKetThuc] > [NgayBatDau]");
                });

            migrationBuilder.CreateTable(
                name: "VaiTro",
                columns: table => new
                {
                    MaVaiTro = table.Column<int>(type: "int", nullable: false),
                    TenVaiTro = table.Column<string>(type: "nvarchar(30)", maxLength: 30, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_VaiTro", x => x.MaVaiTro);
                });

            migrationBuilder.CreateTable(
                name: "SanPham",
                columns: table => new
                {
                    MaSP = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaDM = table.Column<int>(type: "int", nullable: false),
                    TenSP = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    TenKhongDau = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    ThuongHieu = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    GiaBan = table.Column<decimal>(type: "decimal(12,0)", precision: 12, scale: 0, nullable: false),
                    DonViTinh = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    KhoiLuongGram = table.Column<int>(type: "int", nullable: false),
                    MoTa = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    DangBan = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_SanPham", x => x.MaSP);
                    table.CheckConstraint("CK_SanPham_GiaBan", "[GiaBan] > 0");
                    table.ForeignKey(
                        name: "FK_SanPham_DanhMuc_MaDM",
                        column: x => x.MaDM,
                        principalTable: "DanhMuc",
                        principalColumn: "MaDM",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "NguoiDung",
                columns: table => new
                {
                    MaND = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaVaiTro = table.Column<int>(type: "int", nullable: false),
                    HoTen = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    Email = table.Column<string>(type: "nvarchar(150)", maxLength: 150, nullable: false),
                    MatKhauHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    SoDienThoai = table.Column<string>(type: "nvarchar(15)", maxLength: 15, nullable: true),
                    HoatDong = table.Column<bool>(type: "bit", nullable: false),
                    SoLanDangNhapSai = table.Column<int>(type: "int", nullable: false),
                    KhoaDen = table.Column<DateTime>(type: "datetime2", nullable: true),
                    NgayTao = table.Column<DateTime>(type: "datetime2", nullable: false),
                    MaDatLaiMatKhau = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    HanDatLaiMatKhau = table.Column<DateTime>(type: "datetime2", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_NguoiDung", x => x.MaND);
                    table.ForeignKey(
                        name: "FK_NguoiDung_VaiTro_MaVaiTro",
                        column: x => x.MaVaiTro,
                        principalTable: "VaiTro",
                        principalColumn: "MaVaiTro",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "HinhAnhSP",
                columns: table => new
                {
                    MaHA = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaSP = table.Column<int>(type: "int", nullable: false),
                    DuongDan = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_HinhAnhSP", x => x.MaHA);
                    table.ForeignKey(
                        name: "FK_HinhAnhSP_SanPham_MaSP",
                        column: x => x.MaSP,
                        principalTable: "SanPham",
                        principalColumn: "MaSP",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "LoHang",
                columns: table => new
                {
                    MaLo = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaSP = table.Column<int>(type: "int", nullable: false),
                    SoLuongNhap = table.Column<int>(type: "int", nullable: false),
                    SoLuongTon = table.Column<int>(type: "int", nullable: false),
                    NgaySanXuat = table.Column<DateOnly>(type: "date", nullable: true),
                    HanSuDung = table.Column<DateOnly>(type: "date", nullable: false),
                    NgayNhap = table.Column<DateOnly>(type: "date", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_LoHang", x => x.MaLo);
                    table.CheckConstraint("CK_LoHang_HanSuDung", "[HanSuDung] > [NgayNhap]");
                    table.CheckConstraint("CK_LoHang_SoLuongTon", "[SoLuongTon] >= 0");
                    table.ForeignKey(
                        name: "FK_LoHang_SanPham_MaSP",
                        column: x => x.MaSP,
                        principalTable: "SanPham",
                        principalColumn: "MaSP",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "DiaChi",
                columns: table => new
                {
                    MaDC = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaND = table.Column<int>(type: "int", nullable: false),
                    NguoiNhan = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    SoDienThoai = table.Column<string>(type: "nvarchar(15)", maxLength: 15, nullable: false),
                    DiaChiChiTiet = table.Column<string>(type: "nvarchar(300)", maxLength: 300, nullable: false),
                    MaQuanHuyenGHN = table.Column<int>(type: "int", nullable: false),
                    MaPhuongXaGHN = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    MacDinh = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DiaChi", x => x.MaDC);
                    table.ForeignKey(
                        name: "FK_DiaChi_NguoiDung_MaND",
                        column: x => x.MaND,
                        principalTable: "NguoiDung",
                        principalColumn: "MaND",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "DonHang",
                columns: table => new
                {
                    MaDH = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaND = table.Column<int>(type: "int", nullable: false),
                    MaKM = table.Column<int>(type: "int", nullable: true),
                    NgayDat = table.Column<DateTime>(type: "datetime2", nullable: false),
                    TongTienHang = table.Column<decimal>(type: "decimal(12,0)", precision: 12, scale: 0, nullable: false),
                    PhiVanChuyen = table.Column<decimal>(type: "decimal(12,0)", precision: 12, scale: 0, nullable: false),
                    TienGiam = table.Column<decimal>(type: "decimal(12,0)", precision: 12, scale: 0, nullable: false),
                    TongThanhToan = table.Column<decimal>(type: "decimal(12,0)", precision: 12, scale: 0, nullable: false),
                    PhuongThucTT = table.Column<string>(type: "nvarchar(10)", maxLength: 10, nullable: false),
                    NguoiNhan = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    SoDienThoaiNhan = table.Column<string>(type: "nvarchar(15)", maxLength: 15, nullable: false),
                    DiaChiGiao = table.Column<string>(type: "nvarchar(300)", maxLength: 300, nullable: false),
                    MaQuanHuyenGHN = table.Column<int>(type: "int", nullable: false),
                    MaPhuongXaGHN = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    GhiChu = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    MaVanDonGHN = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    TrangThai = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    TrangThaiThanhToan = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DonHang", x => x.MaDH);
                    table.ForeignKey(
                        name: "FK_DonHang_KhuyenMai_MaKM",
                        column: x => x.MaKM,
                        principalTable: "KhuyenMai",
                        principalColumn: "MaKM",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_DonHang_NguoiDung_MaND",
                        column: x => x.MaND,
                        principalTable: "NguoiDung",
                        principalColumn: "MaND",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "GioHang",
                columns: table => new
                {
                    MaND = table.Column<int>(type: "int", nullable: false),
                    MaSP = table.Column<int>(type: "int", nullable: false),
                    SoLuong = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_GioHang", x => new { x.MaND, x.MaSP });
                    table.ForeignKey(
                        name: "FK_GioHang_NguoiDung_MaND",
                        column: x => x.MaND,
                        principalTable: "NguoiDung",
                        principalColumn: "MaND",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_GioHang_SanPham_MaSP",
                        column: x => x.MaSP,
                        principalTable: "SanPham",
                        principalColumn: "MaSP",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ChiTietDonHang",
                columns: table => new
                {
                    MaDH = table.Column<int>(type: "int", nullable: false),
                    MaSP = table.Column<int>(type: "int", nullable: false),
                    SoLuong = table.Column<int>(type: "int", nullable: false),
                    DonGia = table.Column<decimal>(type: "decimal(12,0)", precision: 12, scale: 0, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ChiTietDonHang", x => new { x.MaDH, x.MaSP });
                    table.CheckConstraint("CK_ChiTiet_SoLuong", "[SoLuong] > 0");
                    table.ForeignKey(
                        name: "FK_ChiTietDonHang_DonHang_MaDH",
                        column: x => x.MaDH,
                        principalTable: "DonHang",
                        principalColumn: "MaDH",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ChiTietDonHang_SanPham_MaSP",
                        column: x => x.MaSP,
                        principalTable: "SanPham",
                        principalColumn: "MaSP",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "DanhGia",
                columns: table => new
                {
                    MaDG = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaND = table.Column<int>(type: "int", nullable: false),
                    MaSP = table.Column<int>(type: "int", nullable: false),
                    MaDH = table.Column<int>(type: "int", nullable: false),
                    SoSao = table.Column<int>(type: "int", nullable: false),
                    NoiDung = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: true),
                    NgayDanhGia = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DanhGia", x => x.MaDG);
                    table.CheckConstraint("CK_DanhGia_SoSao", "[SoSao] BETWEEN 1 AND 5");
                    table.ForeignKey(
                        name: "FK_DanhGia_DonHang_MaDH",
                        column: x => x.MaDH,
                        principalTable: "DonHang",
                        principalColumn: "MaDH",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_DanhGia_NguoiDung_MaND",
                        column: x => x.MaND,
                        principalTable: "NguoiDung",
                        principalColumn: "MaND",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_DanhGia_SanPham_MaSP",
                        column: x => x.MaSP,
                        principalTable: "SanPham",
                        principalColumn: "MaSP",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "LichSuDonHang",
                columns: table => new
                {
                    MaLS = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaDH = table.Column<int>(type: "int", nullable: false),
                    TrangThaiCu = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: true),
                    TrangThaiMoi = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    NguoiThucHien = table.Column<int>(type: "int", nullable: true),
                    ThoiGian = table.Column<DateTime>(type: "datetime2", nullable: false),
                    GhiChu = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_LichSuDonHang", x => x.MaLS);
                    table.ForeignKey(
                        name: "FK_LichSuDonHang_DonHang_MaDH",
                        column: x => x.MaDH,
                        principalTable: "DonHang",
                        principalColumn: "MaDH",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_LichSuDonHang_NguoiDung_NguoiThucHien",
                        column: x => x.NguoiThucHien,
                        principalTable: "NguoiDung",
                        principalColumn: "MaND",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "ThanhToan",
                columns: table => new
                {
                    MaTT = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaDH = table.Column<int>(type: "int", nullable: false),
                    SoTien = table.Column<decimal>(type: "decimal(12,0)", precision: 12, scale: 0, nullable: false),
                    MaGiaoDichVNPay = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    MaNganHang = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: true),
                    TrangThai = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    ThoiGian = table.Column<DateTime>(type: "datetime2", nullable: false),
                    DuLieuIPN = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ThanhToan", x => x.MaTT);
                    table.ForeignKey(
                        name: "FK_ThanhToan_DonHang_MaDH",
                        column: x => x.MaDH,
                        principalTable: "DonHang",
                        principalColumn: "MaDH",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "PhanBoLo",
                columns: table => new
                {
                    MaDH = table.Column<int>(type: "int", nullable: false),
                    MaSP = table.Column<int>(type: "int", nullable: false),
                    MaLo = table.Column<int>(type: "int", nullable: false),
                    SoLuong = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PhanBoLo", x => new { x.MaDH, x.MaSP, x.MaLo });
                    table.ForeignKey(
                        name: "FK_PhanBoLo_ChiTietDonHang_MaDH_MaSP",
                        columns: x => new { x.MaDH, x.MaSP },
                        principalTable: "ChiTietDonHang",
                        principalColumns: new[] { "MaDH", "MaSP" },
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_PhanBoLo_LoHang_MaLo",
                        column: x => x.MaLo,
                        principalTable: "LoHang",
                        principalColumn: "MaLo",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.InsertData(
                table: "VaiTro",
                columns: new[] { "MaVaiTro", "TenVaiTro" },
                values: new object[,]
                {
                    { 1, "KhachHang" },
                    { 2, "NhanVien" },
                    { 3, "QuanLy" },
                    { 4, "QuanTri" }
                });

            migrationBuilder.CreateIndex(
                name: "IX_ChiTietDonHang_MaSP",
                table: "ChiTietDonHang",
                column: "MaSP");

            migrationBuilder.CreateIndex(
                name: "IX_DanhGia_MaDH_MaSP",
                table: "DanhGia",
                columns: new[] { "MaDH", "MaSP" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_DanhGia_MaND",
                table: "DanhGia",
                column: "MaND");

            migrationBuilder.CreateIndex(
                name: "IX_DanhGia_MaSP",
                table: "DanhGia",
                column: "MaSP");

            migrationBuilder.CreateIndex(
                name: "IX_DanhMuc_MaDMCha",
                table: "DanhMuc",
                column: "MaDMCha");

            migrationBuilder.CreateIndex(
                name: "IX_DiaChi_MaND",
                table: "DiaChi",
                column: "MaND");

            migrationBuilder.CreateIndex(
                name: "IX_DonHang_MaKM",
                table: "DonHang",
                column: "MaKM");

            migrationBuilder.CreateIndex(
                name: "IX_DonHang_MaND",
                table: "DonHang",
                column: "MaND");

            migrationBuilder.CreateIndex(
                name: "IX_DonHang_TrangThai_NgayDat",
                table: "DonHang",
                columns: new[] { "TrangThai", "NgayDat" });

            migrationBuilder.CreateIndex(
                name: "IX_GioHang_MaSP",
                table: "GioHang",
                column: "MaSP");

            migrationBuilder.CreateIndex(
                name: "IX_HinhAnhSP_MaSP",
                table: "HinhAnhSP",
                column: "MaSP");

            migrationBuilder.CreateIndex(
                name: "IX_KhuyenMai_MaCode",
                table: "KhuyenMai",
                column: "MaCode",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_LichSuDonHang_MaDH",
                table: "LichSuDonHang",
                column: "MaDH");

            migrationBuilder.CreateIndex(
                name: "IX_LichSuDonHang_NguoiThucHien",
                table: "LichSuDonHang",
                column: "NguoiThucHien");

            migrationBuilder.CreateIndex(
                name: "IX_LoHang_MaSP_HanSuDung",
                table: "LoHang",
                columns: new[] { "MaSP", "HanSuDung" });

            migrationBuilder.CreateIndex(
                name: "IX_NguoiDung_Email",
                table: "NguoiDung",
                column: "Email",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_NguoiDung_MaVaiTro",
                table: "NguoiDung",
                column: "MaVaiTro");

            migrationBuilder.CreateIndex(
                name: "IX_PhanBoLo_MaLo",
                table: "PhanBoLo",
                column: "MaLo");

            migrationBuilder.CreateIndex(
                name: "IX_SanPham_MaDM",
                table: "SanPham",
                column: "MaDM");

            migrationBuilder.CreateIndex(
                name: "IX_SanPham_TenKhongDau",
                table: "SanPham",
                column: "TenKhongDau");

            migrationBuilder.CreateIndex(
                name: "IX_ThanhToan_MaDH",
                table: "ThanhToan",
                column: "MaDH");

            migrationBuilder.CreateIndex(
                name: "IX_ThanhToan_MaGiaoDichVNPay",
                table: "ThanhToan",
                column: "MaGiaoDichVNPay",
                unique: true,
                filter: "[MaGiaoDichVNPay] IS NOT NULL");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "DanhGia");

            migrationBuilder.DropTable(
                name: "DiaChi");

            migrationBuilder.DropTable(
                name: "GioHang");

            migrationBuilder.DropTable(
                name: "HinhAnhSP");

            migrationBuilder.DropTable(
                name: "LichSuDonHang");

            migrationBuilder.DropTable(
                name: "PhanBoLo");

            migrationBuilder.DropTable(
                name: "ThanhToan");

            migrationBuilder.DropTable(
                name: "ChiTietDonHang");

            migrationBuilder.DropTable(
                name: "LoHang");

            migrationBuilder.DropTable(
                name: "DonHang");

            migrationBuilder.DropTable(
                name: "SanPham");

            migrationBuilder.DropTable(
                name: "KhuyenMai");

            migrationBuilder.DropTable(
                name: "NguoiDung");

            migrationBuilder.DropTable(
                name: "DanhMuc");

            migrationBuilder.DropTable(
                name: "VaiTro");
        }
    }
}
