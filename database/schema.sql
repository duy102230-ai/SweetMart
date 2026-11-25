IF OBJECT_ID(N'[__EFMigrationsHistory]') IS NULL
BEGIN
    CREATE TABLE [__EFMigrationsHistory] (
        [MigrationId] nvarchar(150) NOT NULL,
        [ProductVersion] nvarchar(32) NOT NULL,
        CONSTRAINT [PK___EFMigrationsHistory] PRIMARY KEY ([MigrationId])
    );
END;
GO

BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [DanhMuc] (
        [MaDM] int NOT NULL IDENTITY,
        [TenDanhMuc] nvarchar(100) NOT NULL,
        [MaDMCha] int NULL,
        CONSTRAINT [PK_DanhMuc] PRIMARY KEY ([MaDM]),
        CONSTRAINT [FK_DanhMuc_DanhMuc_MaDMCha] FOREIGN KEY ([MaDMCha]) REFERENCES [DanhMuc] ([MaDM]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [KhuyenMai] (
        [MaKM] int NOT NULL IDENTITY,
        [MaCode] nvarchar(30) NOT NULL,
        [LoaiGiam] int NOT NULL,
        [GiaTriGiam] decimal(12,0) NOT NULL,
        [GiamToiDa] decimal(12,0) NULL,
        [DonToiThieu] decimal(12,0) NOT NULL,
        [NgayBatDau] datetime2 NOT NULL,
        [NgayKetThuc] datetime2 NOT NULL,
        [SoLuotConLai] int NOT NULL,
        CONSTRAINT [PK_KhuyenMai] PRIMARY KEY ([MaKM]),
        CONSTRAINT [CK_KhuyenMai_Ngay] CHECK ([NgayKetThuc] > [NgayBatDau])
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [VaiTro] (
        [MaVaiTro] int NOT NULL,
        [TenVaiTro] nvarchar(30) NOT NULL,
        CONSTRAINT [PK_VaiTro] PRIMARY KEY ([MaVaiTro])
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [SanPham] (
        [MaSP] int NOT NULL IDENTITY,
        [MaDM] int NOT NULL,
        [TenSP] nvarchar(200) NOT NULL,
        [TenKhongDau] nvarchar(200) NOT NULL,
        [ThuongHieu] nvarchar(100) NULL,
        [GiaBan] decimal(12,0) NOT NULL,
        [DonViTinh] nvarchar(20) NOT NULL,
        [KhoiLuongGram] int NOT NULL,
        [MoTa] nvarchar(max) NULL,
        [DangBan] bit NOT NULL,
        CONSTRAINT [PK_SanPham] PRIMARY KEY ([MaSP]),
        CONSTRAINT [CK_SanPham_GiaBan] CHECK ([GiaBan] > 0),
        CONSTRAINT [FK_SanPham_DanhMuc_MaDM] FOREIGN KEY ([MaDM]) REFERENCES [DanhMuc] ([MaDM]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [NguoiDung] (
        [MaND] int NOT NULL IDENTITY,
        [MaVaiTro] int NOT NULL,
        [HoTen] nvarchar(100) NOT NULL,
        [Email] nvarchar(150) NOT NULL,
        [MatKhauHash] nvarchar(max) NOT NULL,
        [SoDienThoai] nvarchar(15) NULL,
        [HoatDong] bit NOT NULL,
        [SoLanDangNhapSai] int NOT NULL,
        [KhoaDen] datetime2 NULL,
        [NgayTao] datetime2 NOT NULL,
        [MaDatLaiMatKhau] nvarchar(100) NULL,
        [HanDatLaiMatKhau] datetime2 NULL,
        CONSTRAINT [PK_NguoiDung] PRIMARY KEY ([MaND]),
        CONSTRAINT [FK_NguoiDung_VaiTro_MaVaiTro] FOREIGN KEY ([MaVaiTro]) REFERENCES [VaiTro] ([MaVaiTro]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [HinhAnhSP] (
        [MaHA] int NOT NULL IDENTITY,
        [MaSP] int NOT NULL,
        [DuongDan] nvarchar(500) NOT NULL,
        CONSTRAINT [PK_HinhAnhSP] PRIMARY KEY ([MaHA]),
        CONSTRAINT [FK_HinhAnhSP_SanPham_MaSP] FOREIGN KEY ([MaSP]) REFERENCES [SanPham] ([MaSP]) ON DELETE CASCADE
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [LoHang] (
        [MaLo] int NOT NULL IDENTITY,
        [MaSP] int NOT NULL,
        [SoLuongNhap] int NOT NULL,
        [SoLuongTon] int NOT NULL,
        [NgaySanXuat] date NULL,
        [HanSuDung] date NOT NULL,
        [NgayNhap] date NOT NULL,
        CONSTRAINT [PK_LoHang] PRIMARY KEY ([MaLo]),
        CONSTRAINT [CK_LoHang_HanSuDung] CHECK ([HanSuDung] > [NgayNhap]),
        CONSTRAINT [CK_LoHang_SoLuongTon] CHECK ([SoLuongTon] >= 0),
        CONSTRAINT [FK_LoHang_SanPham_MaSP] FOREIGN KEY ([MaSP]) REFERENCES [SanPham] ([MaSP]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [DiaChi] (
        [MaDC] int NOT NULL IDENTITY,
        [MaND] int NOT NULL,
        [NguoiNhan] nvarchar(100) NOT NULL,
        [SoDienThoai] nvarchar(15) NOT NULL,
        [DiaChiChiTiet] nvarchar(300) NOT NULL,
        [MaQuanHuyenGHN] int NOT NULL,
        [MaPhuongXaGHN] nvarchar(20) NOT NULL,
        [MacDinh] bit NOT NULL,
        CONSTRAINT [PK_DiaChi] PRIMARY KEY ([MaDC]),
        CONSTRAINT [FK_DiaChi_NguoiDung_MaND] FOREIGN KEY ([MaND]) REFERENCES [NguoiDung] ([MaND]) ON DELETE CASCADE
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [DonHang] (
        [MaDH] int NOT NULL IDENTITY,
        [MaND] int NOT NULL,
        [MaKM] int NULL,
        [NgayDat] datetime2 NOT NULL,
        [TongTienHang] decimal(12,0) NOT NULL,
        [PhiVanChuyen] decimal(12,0) NOT NULL,
        [TienGiam] decimal(12,0) NOT NULL,
        [TongThanhToan] decimal(12,0) NOT NULL,
        [PhuongThucTT] nvarchar(10) NOT NULL,
        [NguoiNhan] nvarchar(100) NOT NULL,
        [SoDienThoaiNhan] nvarchar(15) NOT NULL,
        [DiaChiGiao] nvarchar(300) NOT NULL,
        [MaQuanHuyenGHN] int NOT NULL,
        [MaPhuongXaGHN] nvarchar(20) NOT NULL,
        [GhiChu] nvarchar(500) NULL,
        [MaVanDonGHN] nvarchar(50) NULL,
        [TrangThai] nvarchar(20) NOT NULL,
        [TrangThaiThanhToan] nvarchar(20) NOT NULL,
        CONSTRAINT [PK_DonHang] PRIMARY KEY ([MaDH]),
        CONSTRAINT [FK_DonHang_KhuyenMai_MaKM] FOREIGN KEY ([MaKM]) REFERENCES [KhuyenMai] ([MaKM]) ON DELETE NO ACTION,
        CONSTRAINT [FK_DonHang_NguoiDung_MaND] FOREIGN KEY ([MaND]) REFERENCES [NguoiDung] ([MaND]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [GioHang] (
        [MaND] int NOT NULL,
        [MaSP] int NOT NULL,
        [SoLuong] int NOT NULL,
        CONSTRAINT [PK_GioHang] PRIMARY KEY ([MaND], [MaSP]),
        CONSTRAINT [FK_GioHang_NguoiDung_MaND] FOREIGN KEY ([MaND]) REFERENCES [NguoiDung] ([MaND]) ON DELETE CASCADE,
        CONSTRAINT [FK_GioHang_SanPham_MaSP] FOREIGN KEY ([MaSP]) REFERENCES [SanPham] ([MaSP]) ON DELETE CASCADE
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [ChiTietDonHang] (
        [MaDH] int NOT NULL,
        [MaSP] int NOT NULL,
        [SoLuong] int NOT NULL,
        [DonGia] decimal(12,0) NOT NULL,
        CONSTRAINT [PK_ChiTietDonHang] PRIMARY KEY ([MaDH], [MaSP]),
        CONSTRAINT [CK_ChiTiet_SoLuong] CHECK ([SoLuong] > 0),
        CONSTRAINT [FK_ChiTietDonHang_DonHang_MaDH] FOREIGN KEY ([MaDH]) REFERENCES [DonHang] ([MaDH]) ON DELETE CASCADE,
        CONSTRAINT [FK_ChiTietDonHang_SanPham_MaSP] FOREIGN KEY ([MaSP]) REFERENCES [SanPham] ([MaSP]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [DanhGia] (
        [MaDG] int NOT NULL IDENTITY,
        [MaND] int NOT NULL,
        [MaSP] int NOT NULL,
        [MaDH] int NOT NULL,
        [SoSao] int NOT NULL,
        [NoiDung] nvarchar(1000) NULL,
        [NgayDanhGia] datetime2 NOT NULL,
        CONSTRAINT [PK_DanhGia] PRIMARY KEY ([MaDG]),
        CONSTRAINT [CK_DanhGia_SoSao] CHECK ([SoSao] BETWEEN 1 AND 5),
        CONSTRAINT [FK_DanhGia_DonHang_MaDH] FOREIGN KEY ([MaDH]) REFERENCES [DonHang] ([MaDH]) ON DELETE NO ACTION,
        CONSTRAINT [FK_DanhGia_NguoiDung_MaND] FOREIGN KEY ([MaND]) REFERENCES [NguoiDung] ([MaND]) ON DELETE NO ACTION,
        CONSTRAINT [FK_DanhGia_SanPham_MaSP] FOREIGN KEY ([MaSP]) REFERENCES [SanPham] ([MaSP]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [LichSuDonHang] (
        [MaLS] int NOT NULL IDENTITY,
        [MaDH] int NOT NULL,
        [TrangThaiCu] nvarchar(20) NULL,
        [TrangThaiMoi] nvarchar(20) NOT NULL,
        [NguoiThucHien] int NULL,
        [ThoiGian] datetime2 NOT NULL,
        [GhiChu] nvarchar(500) NULL,
        CONSTRAINT [PK_LichSuDonHang] PRIMARY KEY ([MaLS]),
        CONSTRAINT [FK_LichSuDonHang_DonHang_MaDH] FOREIGN KEY ([MaDH]) REFERENCES [DonHang] ([MaDH]) ON DELETE CASCADE,
        CONSTRAINT [FK_LichSuDonHang_NguoiDung_NguoiThucHien] FOREIGN KEY ([NguoiThucHien]) REFERENCES [NguoiDung] ([MaND]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [ThanhToan] (
        [MaTT] int NOT NULL IDENTITY,
        [MaDH] int NOT NULL,
        [SoTien] decimal(12,0) NOT NULL,
        [MaGiaoDichVNPay] nvarchar(50) NULL,
        [MaNganHang] nvarchar(20) NULL,
        [TrangThai] nvarchar(20) NOT NULL,
        [ThoiGian] datetime2 NOT NULL,
        [DuLieuIPN] nvarchar(max) NULL,
        CONSTRAINT [PK_ThanhToan] PRIMARY KEY ([MaTT]),
        CONSTRAINT [FK_ThanhToan_DonHang_MaDH] FOREIGN KEY ([MaDH]) REFERENCES [DonHang] ([MaDH]) ON DELETE CASCADE
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE TABLE [PhanBoLo] (
        [MaDH] int NOT NULL,
        [MaSP] int NOT NULL,
        [MaLo] int NOT NULL,
        [SoLuong] int NOT NULL,
        CONSTRAINT [PK_PhanBoLo] PRIMARY KEY ([MaDH], [MaSP], [MaLo]),
        CONSTRAINT [FK_PhanBoLo_ChiTietDonHang_MaDH_MaSP] FOREIGN KEY ([MaDH], [MaSP]) REFERENCES [ChiTietDonHang] ([MaDH], [MaSP]) ON DELETE CASCADE,
        CONSTRAINT [FK_PhanBoLo_LoHang_MaLo] FOREIGN KEY ([MaLo]) REFERENCES [LoHang] ([MaLo]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    IF EXISTS (SELECT * FROM [sys].[identity_columns] WHERE [name] IN (N'MaVaiTro', N'TenVaiTro') AND [object_id] = OBJECT_ID(N'[VaiTro]'))
        SET IDENTITY_INSERT [VaiTro] ON;
    EXEC(N'INSERT INTO [VaiTro] ([MaVaiTro], [TenVaiTro])
    VALUES (1, N''KhachHang''),
    (2, N''NhanVien''),
    (3, N''QuanLy''),
    (4, N''QuanTri'')');
    IF EXISTS (SELECT * FROM [sys].[identity_columns] WHERE [name] IN (N'MaVaiTro', N'TenVaiTro') AND [object_id] = OBJECT_ID(N'[VaiTro]'))
        SET IDENTITY_INSERT [VaiTro] OFF;
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_ChiTietDonHang_MaSP] ON [ChiTietDonHang] ([MaSP]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE UNIQUE INDEX [IX_DanhGia_MaDH_MaSP] ON [DanhGia] ([MaDH], [MaSP]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_DanhGia_MaND] ON [DanhGia] ([MaND]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_DanhGia_MaSP] ON [DanhGia] ([MaSP]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_DanhMuc_MaDMCha] ON [DanhMuc] ([MaDMCha]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_DiaChi_MaND] ON [DiaChi] ([MaND]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_DonHang_MaKM] ON [DonHang] ([MaKM]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_DonHang_MaND] ON [DonHang] ([MaND]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_DonHang_TrangThai_NgayDat] ON [DonHang] ([TrangThai], [NgayDat]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_GioHang_MaSP] ON [GioHang] ([MaSP]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_HinhAnhSP_MaSP] ON [HinhAnhSP] ([MaSP]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE UNIQUE INDEX [IX_KhuyenMai_MaCode] ON [KhuyenMai] ([MaCode]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_LichSuDonHang_MaDH] ON [LichSuDonHang] ([MaDH]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_LichSuDonHang_NguoiThucHien] ON [LichSuDonHang] ([NguoiThucHien]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_LoHang_MaSP_HanSuDung] ON [LoHang] ([MaSP], [HanSuDung]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE UNIQUE INDEX [IX_NguoiDung_Email] ON [NguoiDung] ([Email]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_NguoiDung_MaVaiTro] ON [NguoiDung] ([MaVaiTro]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_PhanBoLo_MaLo] ON [PhanBoLo] ([MaLo]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_SanPham_MaDM] ON [SanPham] ([MaDM]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_SanPham_TenKhongDau] ON [SanPham] ([TenKhongDau]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    CREATE INDEX [IX_ThanhToan_MaDH] ON [ThanhToan] ([MaDH]);
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    EXEC(N'CREATE UNIQUE INDEX [IX_ThanhToan_MaGiaoDichVNPay] ON [ThanhToan] ([MaGiaoDichVNPay]) WHERE [MaGiaoDichVNPay] IS NOT NULL');
END;

IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261125031920_KhoiTaoCSDL'
)
BEGIN
    INSERT INTO [__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20261125031920_KhoiTaoCSDL', N'9.0.10');
END;

COMMIT;
GO

