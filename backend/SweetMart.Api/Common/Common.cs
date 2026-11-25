using System.Globalization;
using System.Security.Claims;
using System.Text;
using System.Text.Json;

namespace SweetMart.Api.Common;

/// <summary>Lỗi nghiệp vụ có mã lỗi để Frontend hiển thị (ví dụ OUT_OF_STOCK, COD_LIMIT_EXCEEDED).</summary>
public class BusinessException(string code, string message, int statusCode = 422) : Exception(message)
{
    public string Code { get; } = code;
    public int StatusCode { get; } = statusCode;
}

public class ErrorHandlingMiddleware(RequestDelegate next, ILogger<ErrorHandlingMiddleware> logger)
{
    public async Task Invoke(HttpContext ctx)
    {
        try
        {
            await next(ctx);
        }
        catch (BusinessException ex)
        {
            await Write(ctx, ex.StatusCode, ex.Code, ex.Message);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Lỗi không xác định khi xử lý {Path}", ctx.Request.Path);
            await Write(ctx, 500, "INTERNAL_ERROR", "Hệ thống đang gặp sự cố, vui lòng thử lại sau.");
        }
    }

    private static Task Write(HttpContext ctx, int status, string code, string message)
    {
        ctx.Response.StatusCode = status;
        ctx.Response.ContentType = "application/json; charset=utf-8";
        return ctx.Response.WriteAsync(JsonSerializer.Serialize(new { code, message }));
    }
}

public static class TextUtil
{
    /// <summary>"Bánh quy Bơ" → "banh quy bo" (phục vụ tìm kiếm không dấu).</summary>
    public static string BoDau(string? s)
    {
        if (string.IsNullOrWhiteSpace(s)) return "";
        var normalized = s.Trim().ToLowerInvariant().Replace('đ', 'd').Normalize(NormalizationForm.FormD);
        var sb = new StringBuilder(normalized.Length);
        foreach (var c in normalized)
            if (CharUnicodeInfo.GetUnicodeCategory(c) != UnicodeCategory.NonSpacingMark) sb.Append(c);
        return sb.ToString().Normalize(NormalizationForm.FormC);
    }
}

public static class ClaimsExtensions
{
    public static int MaND(this ClaimsPrincipal user) =>
        int.TryParse(user.FindFirstValue(ClaimTypes.NameIdentifier), out var id)
            ? id
            : throw new BusinessException("UNAUTHORIZED", "Chưa đăng nhập.", 401);
}

public static class Clock
{
    /// <summary>Ngày hiện tại theo giờ Việt Nam (UTC+7) – dùng để so hạn sử dụng.</summary>
    public static DateOnly HomNayVN() => DateOnly.FromDateTime(DateTime.UtcNow.AddHours(7));
}

public record PagedResult<T>(IReadOnlyList<T> Items, int Total, int Page, int PageSize);
