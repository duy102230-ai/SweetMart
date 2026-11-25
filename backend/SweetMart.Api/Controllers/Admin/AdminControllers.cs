using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SweetMart.Api.Common;
using SweetMart.Api.Data;
using SweetMart.Api.Domain;
using SweetMart.Api.Dtos;
using SweetMart.Api.Services;

namespace SweetMart.Api.Controllers.Admin;

[ApiController, Route("api/admin"), Authorize(Roles = VaiTros.QuanLy)]
public class AdminCatalogController(AppDbContext db) : ControllerBase
{
    [HttpGet("products")]
    public async Task<IActionResult> Products(string? keyword, CancellationToken ct)
    {
        var homNay = Clock.HomNayVN();
        var q = db.SanPham.AsQueryable();
        if (!string.IsNullOrWhiteSpace(keyword)) { var k = TextUtil.BoDau(keyword); q = q.Where(p => p.TenKhongDau.Contains(k)); }
        return Ok(await q.OrderByDescending(p => p.MaSP).Select(p => new
        {
            p.MaSP, p.TenSP, p.ThuongHieu, p.GiaBan, p.DonViTinh, p.KhoiLuongGram, p.MoTa, p.MaDM, p.DanhMuc!.TenDanhMuc, p.DangBan,
            HinhAnh = p.HinhAnh.Select(h => h.DuongDan).ToList(),
            TonKhaDung = p.LoHang.Where(l => l.HanSuDung > homNay).Sum(l => l.SoLuongTon)
        }).ToListAsync(ct));
    }

    [HttpPost("products")]
    public async Task<IActionResult> Create(SanPhamRequest req, CancellationToken ct)
    {
        await DamBaoDanhMuc(req.MaDM, ct);
        var sp = new SanPham();
        Ap(sp, req);
        db.SanPham.Add(sp);
        await db.SaveChangesAsync(ct);
        return StatusCode(201, new { sp.MaSP });
    }

    [HttpPut("products/{id:int}")]
    public async Task<IActionResult> Update(int id, SanPhamRequest req, CancellationToken ct)
    {
        await DamBaoDanhMuc(req.MaDM, ct);
        var sp = await db.SanPham.Include(p => p.HinhAnh).FirstOrDefaultAsync(p => p.MaSP == id, ct);
        if (sp is null) return NotFound();
        db.HinhAnhSP.RemoveRange(sp.HinhAnh);
        sp.HinhAnh.Clear();
        Ap(sp, req);   // đơn giá trong đơn cũ không đổi vì được lưu riêng (BR11)
        await db.SaveChangesAsync(ct);
        return NoContent();
    }

    /// <summary>Sản phẩm không xóa vật lý để giữ lịch sử đơn hàng – chỉ ngừng bán.</summary>
    [HttpDelete("products/{id:int}")]
    public async Task<IActionResult> Hide(int id, CancellationToken ct)
    {
        var n = await db.SanPham.Where(p => p.MaSP == id).ExecuteUpdateAsync(s => s.SetProperty(p => p.DangBan, false), ct);
        return n == 0 ? NotFound() : NoContent();
    }

    [HttpPost("categories")]
    public async Task<IActionResult> CreateCategory(DanhMucRequest req, CancellationToken ct)
    {
        if (req.MaDMCha is { } cha) await DamBaoDanhMuc(cha, ct);
        var dm = new DanhMuc { TenDanhMuc = req.TenDanhMuc.Trim(), MaDMCha = req.MaDMCha };
        db.DanhMuc.Add(dm);
        await db.SaveChangesAsync(ct);
        return StatusCode(201, dm);
    }

    [HttpPut("categories/{id:int}")]
    public async Task<IActionResult> UpdateCategory(int id, DanhMucRequest req, CancellationToken ct)
    {
        if (req.MaDMCha == id) throw new BusinessException("INVALID_PARENT", "Danh mục không thể là cha của chính nó.", 400);
        var n = await db.DanhMuc.Where(d => d.MaDM == id)
            .ExecuteUpdateAsync(s => s.SetProperty(d => d.TenDanhMuc, req.TenDanhMuc.Trim()).SetProperty(d => d.MaDMCha, req.MaDMCha), ct);
        return n == 0 ? NotFound() : NoContent();
    }

    [HttpDelete("categories/{id:int}")]
    public async Task<IActionResult> DeleteCategory(int id, CancellationToken ct)
    {
        if (await db.SanPham.AnyAsync(p => p.MaDM == id, ct) || await db.DanhMuc.AnyAsync(d => d.MaDMCha == id, ct))
            throw new BusinessException("CATEGORY_IN_USE", "Danh mục đang có sản phẩm hoặc danh mục con.", 409);
        var n = await db.DanhMuc.Where(d => d.MaDM == id).ExecuteDeleteAsync(ct);
        return n == 0 ? NotFound() : NoContent();
    }

    private static void Ap(SanPham sp, SanPhamRequest req)
    {
        sp.TenSP = req.TenSP.Trim();
        sp.TenKhongDau = TextUtil.BoDau(req.TenSP + " " + req.ThuongHieu);
        sp.MaDM = req.MaDM;
        sp.ThuongHieu = req.ThuongHieu;
        sp.GiaBan = req.GiaBan;
        sp.DonViTinh = req.DonViTinh;
        sp.KhoiLuongGram = req.KhoiLuongGram;
        sp.MoTa = req.MoTa;
        sp.DangBan = req.DangBan;
        sp.HinhAnh = req.HinhAnh.Select(u => new HinhAnhSP { DuongDan = u }).ToList();
    }

    private async Task DamBaoDanhMuc(int maDM, CancellationToken ct)
    {
        if (!await db.DanhMuc.AnyAsync(d => d.MaDM == maDM, ct))
            throw new BusinessException("CATEGORY_NOT_FOUND", "Danh mục không tồn tại.", 400);
    }
}

[ApiController, Route("api/admin/batches"), Authorize(Roles = VaiTros.NoiBo)]
public class AdminInventoryController(AppDbContext db) : ControllerBase
{
    /// <summary>Danh sách lô; canDate=true chỉ lấy lô còn ≤ 30 ngày hạn (FR08, BR03).</summary>
    [HttpGet]
    public async Task<List<LoHangDto>> List(int? maSP, bool canDate = false, bool hetHan = false, CancellationToken ct = default)
    {
        var homNay = Clock.HomNayVN();
        var moc = homNay.AddDays(BusinessRules.SoNgayCanDate);
        var q = db.LoHang.Where(l => l.SoLuongTon > 0);
        if (maSP is { } sp) q = q.Where(l => l.MaSP == sp);
        if (canDate) q = q.Where(l => l.HanSuDung > homNay && l.HanSuDung <= moc);
        if (hetHan) q = q.Where(l => l.HanSuDung <= homNay);
        return await q.OrderBy(l => l.HanSuDung)
            .Select(l => new LoHangDto(l.MaLo, l.MaSP, l.SanPham!.TenSP, l.SoLuongNhap, l.SoLuongTon, l.NgaySanXuat, l.HanSuDung, l.NgayNhap,
                l.HanSuDung > homNay && l.HanSuDung <= moc, l.HanSuDung <= homNay))
            .ToListAsync(ct);
    }

    [HttpPost]
    public async Task<IActionResult> NhapLo(NhapLoRequest req, CancellationToken ct)
    {
        var homNay = Clock.HomNayVN();
        if (req.HanSuDung <= homNay) throw new BusinessException("INVALID_EXPIRY", "Hạn sử dụng không hợp lệ.", 400);
        if (req.NgaySanXuat is { } nsx && nsx > homNay) throw new BusinessException("INVALID_MFG", "Ngày sản xuất không được sau hôm nay.", 400);
        if (!await db.SanPham.AnyAsync(p => p.MaSP == req.MaSP, ct)) throw new BusinessException("PRODUCT_NOT_FOUND", "Sản phẩm không tồn tại.", 400);
        var lo = new LoHang { MaSP = req.MaSP, SoLuongNhap = req.SoLuong, SoLuongTon = req.SoLuong, NgaySanXuat = req.NgaySanXuat, HanSuDung = req.HanSuDung, NgayNhap = homNay };
        db.LoHang.Add(lo);
        await db.SaveChangesAsync(ct);
        return StatusCode(201, new { lo.MaLo });
    }

    /// <summary>Sản phẩm có tồn khả dụng dưới ngưỡng (mặc định 10).</summary>
    [HttpGet("low-stock")]
    public async Task<IActionResult> LowStock(int nguong = 10, CancellationToken ct = default)
    {
        var homNay = Clock.HomNayVN();
        return Ok(await db.SanPham.Where(p => p.DangBan)
            .Select(p => new { p.MaSP, p.TenSP, Ton = p.LoHang.Where(l => l.HanSuDung > homNay).Sum(l => l.SoLuongTon) })
            .Where(x => x.Ton < nguong).OrderBy(x => x.Ton).ToListAsync(ct));
    }
}

[ApiController, Route("api/admin/orders"), Authorize(Roles = VaiTros.NoiBo)]
public class AdminOrdersController(AppDbContext db, DonHangService donHang) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> List(TrangThaiDon? status, string? keyword, int page = 1, CancellationToken ct = default)
    {
        var q = db.DonHang.AsQueryable();
        if (status is { } s) q = q.Where(d => d.TrangThai == s);
        if (!string.IsNullOrWhiteSpace(keyword))
        {
            var k = keyword.Trim().ToUpperInvariant().Replace("SM", "");
            q = int.TryParse(k, out var ma) ? q.Where(d => d.MaDH == ma) : q.Where(d => d.SoDienThoaiNhan.Contains(keyword) || d.NguoiNhan.Contains(keyword));
        }
        var total = await q.CountAsync(ct);
        var items = await q.OrderByDescending(d => d.NgayDat).Skip((Math.Max(page, 1) - 1) * 20).Take(20)
            .Select(d => new { d.MaDH, d.NgayDat, d.NguoiNhan, d.SoDienThoaiNhan, d.TongThanhToan, PhuongThucTT = d.PhuongThucTT.ToString(),
                TrangThai = d.TrangThai.ToString(), TrangThaiThanhToan = d.TrangThaiThanhToan.ToString(), d.MaVanDonGHN })
            .ToListAsync(ct);
        var demTheoTrangThai = (await db.DonHang.Select(d => d.TrangThai).ToListAsync(ct)).GroupBy(t => t.ToString()).ToDictionary(g => g.Key, g => g.Count());
        return Ok(new { items, total, demTheoTrangThai });
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<DonHangDto>> Detail(int id, CancellationToken ct)
    {
        var r = await OrderQueries.ChiTietAsync(db, id, ct);
        return r is null ? NotFound() : r.Value.dto;
    }

    [HttpPut("{id:int}/status")]
    public async Task<IActionResult> UpdateStatus(int id, CapNhatTrangThaiRequest req, CancellationToken ct)
    {
        var d = await donHang.CapNhatTrangThaiAsync(id, req.TrangThaiMoi, User.MaND(), req.GhiChu, ct);
        return Ok(new { TrangThai = d.TrangThai.ToString() });
    }

    [HttpPut("{id:int}/cancel")]
    public async Task<IActionResult> Cancel(int id, HuyDonRequest req, CancellationToken ct)
    {
        await donHang.HuyDonAsync(id, User.MaND(), false, req.LyDo, ct);
        return NoContent();
    }

    [HttpPost("{id:int}/shipment")]
    public async Task<IActionResult> Shipment(int id, CancellationToken ct)
    {
        var d = await donHang.TaoVanDonAsync(id, User.MaND(), ct);
        return Ok(new { d.MaVanDonGHN, TrangThai = d.TrangThai.ToString() });
    }
}

[ApiController, Route("api/admin/vouchers"), Authorize(Roles = VaiTros.QuanLy)]
public class AdminVouchersController(AppDbContext db) : ControllerBase
{
    [HttpGet] public async Task<IActionResult> List(CancellationToken ct) => Ok(await db.KhuyenMai.OrderByDescending(k => k.NgayBatDau).ToListAsync(ct));

    [HttpPost]
    public async Task<IActionResult> Create(KhuyenMaiRequest req, CancellationToken ct)
    {
        Validate(req);
        var code = req.MaCode.Trim().ToUpperInvariant();
        if (await db.KhuyenMai.AnyAsync(k => k.MaCode == code, ct)) throw new BusinessException("VOUCHER_EXISTS", "Mã đã tồn tại.", 409);
        var km = new KhuyenMai();
        Ap(km, req, code);
        db.KhuyenMai.Add(km);
        await db.SaveChangesAsync(ct);
        return StatusCode(201, km);
    }

    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(int id, KhuyenMaiRequest req, CancellationToken ct)
    {
        Validate(req);
        var km = await db.KhuyenMai.FindAsync([id], ct);
        if (km is null) return NotFound();
        Ap(km, req, req.MaCode.Trim().ToUpperInvariant());
        await db.SaveChangesAsync(ct);
        return NoContent();
    }

    private static void Validate(KhuyenMaiRequest r)
    {
        if (r.NgayKetThuc <= r.NgayBatDau) throw new BusinessException("INVALID_DATE", "Ngày kết thúc phải sau ngày bắt đầu.", 400);
        if (r.LoaiGiam == LoaiGiam.PhanTram && r.GiaTriGiam > 100) throw new BusinessException("INVALID_PERCENT", "Giảm theo phần trăm tối đa 100%.", 400);
    }

    private static void Ap(KhuyenMai km, KhuyenMaiRequest r, string code)
    {
        km.MaCode = code; km.LoaiGiam = r.LoaiGiam; km.GiaTriGiam = r.GiaTriGiam; km.GiamToiDa = r.GiamToiDa;
        km.DonToiThieu = r.DonToiThieu; km.NgayBatDau = r.NgayBatDau; km.NgayKetThuc = r.NgayKetThuc; km.SoLuotConLai = r.SoLuotConLai;
    }
}

[ApiController, Route("api/admin/reports"), Authorize(Roles = VaiTros.QuanLy)]
public class AdminReportsController(BaoCaoService baoCao) : ControllerBase
{
    [HttpGet("revenue")]
    public Task<BaoCaoDoanhThu> Revenue(DateOnly? from, DateOnly? to, CancellationToken ct)
    {
        var den = to ?? Clock.HomNayVN();
        var tu = from ?? den.AddDays(-29);
        if (tu > den) throw new BusinessException("INVALID_RANGE", "Khoảng thời gian không hợp lệ.", 400);
        return baoCao.DoanhThuAsync(tu, den, ct);
    }
}

[ApiController, Route("api/admin/users"), Authorize(Roles = VaiTros.QuanTri)]
public class AdminUsersController(AppDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> List(CancellationToken ct) =>
        Ok(await db.NguoiDung.OrderBy(u => u.MaVaiTro).ThenBy(u => u.HoTen)
            .Select(u => new { u.MaND, u.HoTen, u.Email, VaiTro = u.VaiTro!.TenVaiTro, u.HoatDong, u.NgayTao }).ToListAsync(ct));

    [HttpPost]
    public async Task<IActionResult> CreateStaff(TaoNhanVienRequest req, CancellationToken ct)
    {
        var mail = req.Email.Trim().ToLowerInvariant();
        if (await db.NguoiDung.AnyAsync(u => u.Email == mail, ct)) throw new BusinessException("EMAIL_EXISTS", "Email đã được sử dụng.", 409);
        var u = new NguoiDung { Email = mail, HoTen = req.HoTen, MaVaiTro = req.MaVaiTro, MatKhauHash = BCrypt.Net.BCrypt.HashPassword(req.MatKhau) };
        db.NguoiDung.Add(u);
        await db.SaveChangesAsync(ct);
        return StatusCode(201, new { u.MaND });
    }

    [HttpPut("{id:int}/active")]
    public async Task<IActionResult> SetActive(int id, [FromQuery] bool value, CancellationToken ct)
    {
        if (id == User.MaND()) throw new BusinessException("SELF_LOCK", "Không thể tự khóa tài khoản của mình.", 400);
        var n = await db.NguoiDung.Where(u => u.MaND == id).ExecuteUpdateAsync(s => s.SetProperty(u => u.HoatDong, value), ct);
        return n == 0 ? NotFound() : NoContent();
    }
}
