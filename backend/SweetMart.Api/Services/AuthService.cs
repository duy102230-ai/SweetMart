using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using SweetMart.Api.Common;
using SweetMart.Api.Data;
using SweetMart.Api.Domain;
using SweetMart.Api.Dtos;
using SweetMart.Api.Integrations;

namespace SweetMart.Api.Services;

public class JwtOptions
{
    public string Issuer { get; set; } = "SweetMart";
    public string Audience { get; set; } = "SweetMart";
    public string Key { get; set; } = "";
    public int ExpiryMinutes { get; set; } = 60;
}

public class AuthService(AppDbContext db, IOptions<JwtOptions> jwt, EmailQueue email, IConfiguration config)
{
    public async Task<AuthResponse> DangKyAsync(RegisterRequest req, CancellationToken ct = default)
    {
        var mail = req.Email.Trim().ToLowerInvariant();
        if (await db.NguoiDung.AnyAsync(u => u.Email == mail, ct))
            throw new BusinessException("EMAIL_EXISTS", "Email đã được sử dụng.", 409);
        var user = new NguoiDung
        {
            Email = mail,
            HoTen = req.HoTen.Trim(),
            SoDienThoai = req.SoDienThoai,
            MaVaiTro = VaiTros.MaKhachHang,
            MatKhauHash = BCrypt.Net.BCrypt.HashPassword(req.MatKhau)
        };
        db.NguoiDung.Add(user);
        await db.SaveChangesAsync(ct);
        return TaoToken(user, VaiTros.KhachHang);
    }

    /// <summary>Đăng nhập; sai 5 lần liên tiếp thì khóa 15 phút (NFR04).</summary>
    public async Task<AuthResponse> DangNhapAsync(LoginRequest req, DateTime nowUtc, CancellationToken ct = default)
    {
        var mail = req.Email.Trim().ToLowerInvariant();
        var user = await db.NguoiDung.Include(u => u.VaiTro).FirstOrDefaultAsync(u => u.Email == mail, ct);
        var loiChung = new BusinessException("INVALID_CREDENTIALS", "Email hoặc mật khẩu không đúng.", 401);
        if (user is null) throw loiChung;
        if (!user.HoatDong) throw new BusinessException("ACCOUNT_DISABLED", "Tài khoản đã bị khóa, vui lòng liên hệ cửa hàng.", 403);
        if (user.KhoaDen is { } khoa && khoa > nowUtc)
            throw new BusinessException("ACCOUNT_LOCKED", $"Đăng nhập sai quá nhiều lần. Thử lại sau {Math.Ceiling((khoa - nowUtc).TotalMinutes)} phút.", 423);

        if (!BCrypt.Net.BCrypt.Verify(req.MatKhau, user.MatKhauHash))
        {
            user.SoLanDangNhapSai++;
            if (user.SoLanDangNhapSai >= BusinessRules.SoLanSaiToiDa)
            {
                user.KhoaDen = nowUtc.AddMinutes(BusinessRules.PhutKhoaDangNhap);
                user.SoLanDangNhapSai = 0;
            }
            await db.SaveChangesAsync(ct);
            throw loiChung;
        }
        user.SoLanDangNhapSai = 0;
        user.KhoaDen = null;
        await db.SaveChangesAsync(ct);
        return TaoToken(user, user.VaiTro!.TenVaiTro);
    }

    public async Task QuenMatKhauAsync(string emailNhap, CancellationToken ct = default)
    {
        var user = await db.NguoiDung.FirstOrDefaultAsync(u => u.Email == emailNhap.Trim().ToLowerInvariant(), ct);
        if (user is null) return;   // không tiết lộ email có tồn tại hay không
        user.MaDatLaiMatKhau = Convert.ToHexString(RandomNumberGenerator.GetBytes(32));
        user.HanDatLaiMatKhau = DateTime.UtcNow.AddMinutes(30);
        await db.SaveChangesAsync(ct);
        var link = $"{config["App:FrontendUrl"]}/dat-lai-mat-khau?token={user.MaDatLaiMatKhau}";
        email.Enqueue(user.Email, "[SweetMart] Đặt lại mật khẩu", $"<p>Nhấn vào liên kết sau để đặt lại mật khẩu (hiệu lực 30 phút):</p><p><a href=\"{link}\">{link}</a></p>");
    }

    public async Task DatLaiMatKhauAsync(ResetPasswordRequest req, CancellationToken ct = default)
    {
        var user = await db.NguoiDung.FirstOrDefaultAsync(u => u.MaDatLaiMatKhau == req.Token, ct);
        if (user is null || user.HanDatLaiMatKhau < DateTime.UtcNow)
            throw new BusinessException("TOKEN_INVALID", "Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.", 400);
        user.MatKhauHash = BCrypt.Net.BCrypt.HashPassword(req.MatKhauMoi);
        user.MaDatLaiMatKhau = null;
        user.HanDatLaiMatKhau = null;
        await db.SaveChangesAsync(ct);
    }

    public AuthResponse TaoToken(NguoiDung user, string vaiTro)
    {
        var o = jwt.Value;
        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.MaND.ToString()),
            new Claim(ClaimTypes.Name, user.HoTen),
            new Claim(ClaimTypes.Email, user.Email),
            new Claim(ClaimTypes.Role, vaiTro),
        };
        var creds = new SigningCredentials(new SymmetricSecurityKey(Encoding.UTF8.GetBytes(o.Key)), SecurityAlgorithms.HmacSha256);
        var token = new JwtSecurityToken(o.Issuer, o.Audience, claims, expires: DateTime.UtcNow.AddMinutes(o.ExpiryMinutes), signingCredentials: creds);
        return new AuthResponse(new JwtSecurityTokenHandler().WriteToken(token), user.MaND, user.HoTen, user.Email, vaiTro);
    }
}
