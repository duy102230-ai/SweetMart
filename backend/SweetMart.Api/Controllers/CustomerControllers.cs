using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SweetMart.Api.Common;
using SweetMart.Api.Data;
using SweetMart.Api.Domain;
using SweetMart.Api.Dtos;
using SweetMart.Api.Integrations;
using SweetMart.Api.Services;

namespace SweetMart.Api.Controllers;

[ApiController, Route("api/auth")]
public class AuthController(AuthService auth) : ControllerBase
{
    [HttpPost("register")]
    public Task<AuthResponse> Register(RegisterRequest req, CancellationToken ct) => auth.DangKyAsync(req, ct);

    [HttpPost("login")]
    public Task<AuthResponse> Login(LoginRequest req, CancellationToken ct) => auth.DangNhapAsync(req, DateTime.UtcNow, ct);

    [HttpPost("forgot-password")]
    public async Task<IActionResult> Forgot(ForgotPasswordRequest req, CancellationToken ct)
    {
        await auth.QuenMatKhauAsync(req.Email, ct);
        return Ok(new { message = "Nếu email tồn tại, liên kết đặt lại mật khẩu đã được gửi." });
    }

    [HttpPost("reset-password")]
    public async Task<IActionResult> Reset(ResetPasswordRequest req, CancellationToken ct)
    {
        await auth.DatLaiMatKhauAsync(req, ct);
        return NoContent();
    }
}

[ApiController, Route("api")]
public class CatalogController(AppDbContext db) : ControllerBase
{
    [HttpGet("categories")]
    public async Task<IActionResult> Categories(CancellationToken ct) =>
        Ok(await db.DanhMuc.OrderBy(d => d.TenDanhMuc).Select(d => new { d.MaDM, d.TenDanhMuc, d.MaDMCha }).ToListAsync(ct));

    /// <summary>Danh sách, tìm kiếm không dấu, lọc, sắp xếp sản phẩm (FR05).</summary>
    [HttpGet("products")]
    public async Task<PagedResult<SanPhamListItem>> Products(string? keyword, int? categoryId, string? brand, decimal? minPrice,
        decimal? maxPrice, string? sort, int page = 1, int pageSize = 12, CancellationToken ct = default)
    {
        pageSize = Math.Clamp(pageSize, 1, 48);
        page = Math.Max(page, 1);
        var homNay = Clock.HomNayVN();
        var q = db.SanPham.Where(p => p.DangBan);
        if (!string.IsNullOrWhiteSpace(keyword))
        {
            var k = TextUtil.BoDau(keyword);
            q = q.Where(p => p.TenKhongDau.Contains(k));
        }
        if (categoryId is { } dm) q = q.Where(p => p.MaDM == dm || p.DanhMuc!.MaDMCha == dm);
        if (!string.IsNullOrWhiteSpace(brand)) q = q.Where(p => p.ThuongHieu == brand);
        if (minPrice is { } min) q = q.Where(p => p.GiaBan >= min);
        if (maxPrice is { } max) q = q.Where(p => p.GiaBan <= max);
        q = sort switch
        {
            "price_asc" => q.OrderBy(p => p.GiaBan),
            "price_desc" => q.OrderByDescending(p => p.GiaBan),
            "bestseller" => q.OrderByDescending(p => db.ChiTietDonHang.Where(c => c.MaSP == p.MaSP).Sum(c => (int?)c.SoLuong) ?? 0),
            _ => q.OrderByDescending(p => p.MaSP)
        };
        var total = await q.CountAsync(ct);
        var items = await q.Skip((page - 1) * pageSize).Take(pageSize)
            .Select(p => new SanPhamListItem(p.MaSP, p.TenSP, p.ThuongHieu, p.GiaBan, p.DonViTinh,
                p.HinhAnh.OrderBy(h => h.MaHA).Select(h => h.DuongDan).FirstOrDefault(),
                p.LoHang.Where(l => l.HanSuDung > homNay).Sum(l => l.SoLuongTon),
                p.DanhMuc!.TenDanhMuc))
            .ToListAsync(ct);
        return new PagedResult<SanPhamListItem>(items, total, page, pageSize);
    }

    [HttpGet("products/{id:int}")]
    public async Task<ActionResult<SanPhamDetail>> Product(int id, CancellationToken ct)
    {
        var homNay = Clock.HomNayVN();
        var p = await db.SanPham.Where(x => x.MaSP == id && x.DangBan)
            .Select(x => new SanPhamDetail(x.MaSP, x.TenSP, x.ThuongHieu, x.GiaBan, x.DonViTinh, x.KhoiLuongGram, x.MoTa,
                x.MaDM, x.DanhMuc!.TenDanhMuc, x.HinhAnh.OrderBy(h => h.MaHA).Select(h => h.DuongDan).ToList(),
                x.LoHang.Where(l => l.HanSuDung > homNay).Sum(l => l.SoLuongTon),
                x.LoHang.Where(l => l.HanSuDung > homNay && l.SoLuongTon > 0).OrderBy(l => l.HanSuDung).Select(l => (DateOnly?)l.HanSuDung).FirstOrDefault(),
                db.DanhGia.Where(d => d.MaSP == x.MaSP).Average(d => (double?)d.SoSao),
                db.DanhGia.Count(d => d.MaSP == x.MaSP)))
            .FirstOrDefaultAsync(ct);
        return p is null ? NotFound() : p;
    }

    [HttpGet("products/{id:int}/reviews")]
    public async Task<IActionResult> Reviews(int id, CancellationToken ct) =>
        Ok(await db.DanhGia.Where(d => d.MaSP == id).OrderByDescending(d => d.NgayDanhGia)
            .Select(d => new DanhGiaDto(d.NguoiDung!.HoTen, d.SoSao, d.NoiDung, d.NgayDanhGia)).Take(50).ToListAsync(ct));
}

[ApiController, Route("api/addresses"), Authorize(Roles = VaiTros.KhachHang)]
public class AddressesController(AppDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> List(CancellationToken ct) =>
        Ok(await db.DiaChi.Where(d => d.MaND == User.MaND()).OrderByDescending(d => d.MacDinh).ToListAsync(ct));

    [HttpPost]
    public async Task<IActionResult> Create(DiaChiRequest req, CancellationToken ct)
    {
        var maND = User.MaND();
        var laDauTien = !await db.DiaChi.AnyAsync(d => d.MaND == maND, ct);
        if (req.MacDinh) await db.DiaChi.Where(d => d.MaND == maND).ExecuteUpdateAsync(s => s.SetProperty(d => d.MacDinh, false), ct);
        var dc = new DiaChi
        {
            MaND = maND, NguoiNhan = req.NguoiNhan, SoDienThoai = req.SoDienThoai, DiaChiChiTiet = req.DiaChiChiTiet,
            MaQuanHuyenGHN = req.MaQuanHuyenGHN, MaPhuongXaGHN = req.MaPhuongXaGHN, MacDinh = req.MacDinh || laDauTien
        };
        db.DiaChi.Add(dc);
        await db.SaveChangesAsync(ct);
        return Ok(dc);
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id, CancellationToken ct)
    {
        var n = await db.DiaChi.Where(d => d.MaDC == id && d.MaND == User.MaND()).ExecuteDeleteAsync(ct);
        return n == 0 ? NotFound() : NoContent();
    }
}

[ApiController, Route("api/cart"), Authorize(Roles = VaiTros.KhachHang)]
public class CartController(AppDbContext db, TonKhoService tonKho) : ControllerBase
{
    [HttpGet]
    public async Task<List<CartItemDto>> Get(CancellationToken ct)
    {
        var homNay = Clock.HomNayVN();
        return await db.GioHang.Where(g => g.MaND == User.MaND())
            .Select(g => new CartItemDto(g.MaSP, g.SanPham!.TenSP, g.SanPham.HinhAnh.Select(h => h.DuongDan).FirstOrDefault(),
                g.SanPham.GiaBan, g.SoLuong, g.SanPham.LoHang.Where(l => l.HanSuDung > homNay).Sum(l => l.SoLuongTon),
                g.SanPham.GiaBan * g.SoLuong))
            .ToListAsync(ct);
    }

    /// <summary>Thêm hoặc cập nhật số lượng; không cho vượt tồn khả dụng (BR04).</summary>
    [HttpPut("items")]
    public async Task<IActionResult> Upsert(CartItemRequest req, CancellationToken ct)
    {
        var maND = User.MaND();
        if (!await db.SanPham.AnyAsync(p => p.MaSP == req.MaSP && p.DangBan, ct)) return NotFound();
        var ton = await tonKho.TonKhaDungAsync(req.MaSP, ct);
        if (req.SoLuong > ton)
            throw new BusinessException("OUT_OF_STOCK", $"Chỉ còn {ton} sản phẩm.", 409);
        var item = await db.GioHang.FindAsync([maND, req.MaSP], ct);
        if (item is null) db.GioHang.Add(new GioHang { MaND = maND, MaSP = req.MaSP, SoLuong = req.SoLuong });
        else item.SoLuong = req.SoLuong;
        await db.SaveChangesAsync(ct);
        return NoContent();
    }

    [HttpDelete("items/{maSP:int}")]
    public async Task<IActionResult> Remove(int maSP, CancellationToken ct)
    {
        await db.GioHang.Where(g => g.MaND == User.MaND() && g.MaSP == maSP).ExecuteDeleteAsync(ct);
        return NoContent();
    }
}

[ApiController, Route("api/orders"), Authorize(Roles = VaiTros.KhachHang)]
public class OrdersController(AppDbContext db, DonHangService donHang, VnPayClient vnPay) : ControllerBase
{
    /// <summary>Tính tạm tiền hàng, giảm giá, phí ship trước khi đặt (dùng ở trang Checkout).</summary>
    [HttpPost("preview")]
    public async Task<TinhPhiResponse> Preview(TinhPhiRequest req, CancellationToken ct)
    {
        var maND = User.MaND();
        var dc = await db.DiaChi.FirstOrDefaultAsync(d => d.MaDC == req.MaDC && d.MaND == maND, ct)
                 ?? throw new BusinessException("ADDRESS_NOT_FOUND", "Địa chỉ không hợp lệ.", 400);
        var t = await donHang.TinhTienAsync(maND, dc, req.MaCode, ct);
        return new TinhPhiResponse(t.TongTienHang, t.TienGiam, t.PhiVanChuyen, t.TongThanhToan, t.TongThanhToan <= BusinessRules.HanMucCOD);
    }

    [HttpPost]
    public async Task<ActionResult<TaoDonResponse>> Create(TaoDonRequest req, CancellationToken ct)
    {
        var don = await donHang.TaoDonAsync(User.MaND(), req, ct);
        string? url = null;
        if (don.PhuongThucTT == PhuongThucThanhToan.VNPAY)
        {
            var ip = HttpContext.Connection.RemoteIpAddress?.MapToIPv4().ToString() ?? "127.0.0.1";
            url = vnPay.TaoUrlThanhToan(don.MaDH, don.TongThanhToan, ip, DateTime.UtcNow);
        }
        return StatusCode(201, new TaoDonResponse(don.MaDH, don.MaHienThi, don.TrangThai.ToString(), don.TongThanhToan, url));
    }

    [HttpGet("my")]
    public async Task<IActionResult> My(CancellationToken ct) =>
        Ok(await db.DonHang.Where(d => d.MaND == User.MaND()).OrderByDescending(d => d.NgayDat)
            .Select(d => new { d.MaDH, d.NgayDat, TrangThai = d.TrangThai.ToString(), d.TongThanhToan, d.MaVanDonGHN, SoSanPham = d.ChiTiet.Count })
            .ToListAsync(ct));

    [HttpGet("{id:int}")]
    public async Task<ActionResult<DonHangDto>> Detail(int id, CancellationToken ct)
    {
        var dto = await OrderQueries.ChiTietAsync(db, id, ct);
        return dto is null || dto.Value.maND != User.MaND() ? NotFound() : dto.Value.dto;
    }

    [HttpPut("{id:int}/cancel")]
    public async Task<IActionResult> Cancel(int id, HuyDonRequest req, CancellationToken ct)
    {
        await donHang.HuyDonAsync(id, User.MaND(), true, "Khách hủy: " + req.LyDo, ct);
        return NoContent();
    }
}

[ApiController, Route("api/reviews"), Authorize(Roles = VaiTros.KhachHang)]
public class ReviewsController(AppDbContext db) : ControllerBase
{
    /// <summary>Chỉ đánh giá sản phẩm trong đơn đã giao của chính mình, mỗi sản phẩm/đơn một lần (BR12).</summary>
    [HttpPost]
    public async Task<IActionResult> Create(DanhGiaRequest req, CancellationToken ct)
    {
        var maND = User.MaND();
        var hopLe = await db.DonHang.AnyAsync(d => d.MaDH == req.MaDH && d.MaND == maND && d.TrangThai == TrangThaiDon.DaGiao
                                                   && d.ChiTiet.Any(c => c.MaSP == req.MaSP), ct);
        if (!hopLe) throw new BusinessException("REVIEW_NOT_ALLOWED", "Bạn chỉ đánh giá được sản phẩm trong đơn đã giao.");
        if (await db.DanhGia.AnyAsync(d => d.MaDH == req.MaDH && d.MaSP == req.MaSP, ct))
            throw new BusinessException("REVIEW_EXISTS", "Bạn đã đánh giá sản phẩm này trong đơn hàng.", 409);
        db.DanhGia.Add(new DanhGia { MaND = maND, MaDH = req.MaDH, MaSP = req.MaSP, SoSao = req.SoSao, NoiDung = req.NoiDung });
        await db.SaveChangesAsync(ct);
        return StatusCode(201);
    }
}

[ApiController, Route("api/payments/vnpay")]
public class PaymentsController(ThanhToanService thanhToan, VnPayClient vnPay) : ControllerBase
{
    /// <summary>VNPay gọi máy chủ – máy chủ. Đây là nơi duy nhất cập nhật trạng thái thanh toán.</summary>
    [HttpGet("ipn")]
    public async Task<IActionResult> Ipn(CancellationToken ct)
    {
        var q = Request.Query.ToDictionary(x => x.Key, x => x.Value.ToString());
        var r = await thanhToan.XuLyIpnAsync(q, ct);
        return Ok(new { RspCode = r.RspCode, Message = r.Message });
    }

    /// <summary>Frontend gửi lại tham số ReturnUrl để kiểm tra chữ ký trước khi hiển thị; không cập nhật dữ liệu.</summary>
    [HttpGet("return")]
    public IActionResult Return()
    {
        var q = Request.Query.ToDictionary(x => x.Key, x => x.Value.ToString());
        var hopLe = vnPay.XacThucChuKy(q);
        var thanhCong = hopLe && q.GetValueOrDefault("vnp_ResponseCode") == "00";
        int.TryParse(q.GetValueOrDefault("vnp_TxnRef"), out var maDH);
        return Ok(new { hopLe, thanhCong, maDH, maHienThi = $"SM{maDH:D6}" });
    }
}

[ApiController, Route("api/shipping")]
public class ShippingController(AppDbContext db, DonHangService donHang, Microsoft.Extensions.Options.IOptions<GhnOptions> ghn) : ControllerBase
{
    public record GhnWebhook(string? OrderCode, string? Status);

    /// <summary>GHN gọi khi trạng thái vận đơn thay đổi. URL chứa token bí mật cấu hình ở Ghn:WebhookToken.</summary>
    [HttpPost("ghn-webhook/{token}")]
    public async Task<IActionResult> Webhook(string token, GhnWebhook body, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(ghn.Value.WebhookToken) || token != ghn.Value.WebhookToken) return Unauthorized();
        var don = await db.DonHang.FirstOrDefaultAsync(d => d.MaVanDonGHN == body.OrderCode, ct);
        if (don is null) return Ok();
        var moi = body.Status switch
        {
            "delivered" => TrangThaiDon.DaGiao,
            "returned" or "return" or "delivery_fail" => TrangThaiDon.GiaoThatBai,
            _ => (TrangThaiDon?)null
        };
        if (moi is { } m && OrderStateMachine.CoTheChuyen(don.TrangThai, m))
            await donHang.CapNhatTrangThaiAsync(don.MaDH, m, nguoiThucHien: null, ghiChu: $"GHN: {body.Status}", ct);
        return Ok();
    }
}

public static class OrderQueries
{
    public static async Task<(DonHangDto dto, int maND)?> ChiTietAsync(AppDbContext db, int maDH, CancellationToken ct)
    {
        var d = await db.DonHang.AsNoTracking()
            .Include(x => x.ChiTiet).ThenInclude(c => c.SanPham)
            .Include(x => x.LichSu)
            .FirstOrDefaultAsync(x => x.MaDH == maDH, ct);
        if (d is null) return null;
        var dto = new DonHangDto(d.MaDH, d.MaHienThi, d.NgayDat, d.TrangThai.ToString(), d.TrangThaiThanhToan.ToString(), d.PhuongThucTT.ToString(),
            d.TongTienHang, d.PhiVanChuyen, d.TienGiam, d.TongThanhToan, d.NguoiNhan, d.SoDienThoaiNhan, d.DiaChiGiao, d.GhiChu, d.MaVanDonGHN,
            d.ChiTiet.Select(c => new ChiTietDto(c.MaSP, c.SanPham!.TenSP, c.SoLuong, c.DonGia, c.DonGia * c.SoLuong)).ToList(),
            d.LichSu.OrderBy(l => l.ThoiGian).Select(l => new LichSuDto(l.TrangThaiCu?.ToString(), l.TrangThaiMoi.ToString(), l.ThoiGian, l.GhiChu)).ToList());
        return (dto, d.MaND);
    }
}
