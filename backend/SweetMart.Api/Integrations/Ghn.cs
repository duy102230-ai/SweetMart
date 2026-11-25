using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Options;

namespace SweetMart.Api.Integrations;

public class GhnOptions
{
    public string BaseUrl { get; set; } = "https://dev-online-gateway.ghn.vn/shiip/public-api";
    public string Token { get; set; } = "";
    public int ShopId { get; set; }
    /// <summary>Quận/huyện, phường/xã nơi cửa hàng gửi hàng.</summary>
    public int FromDistrictId { get; set; }
    public string FromWardCode { get; set; } = "";
    /// <summary>Chuỗi bí mật đặt trong URL webhook để chỉ GHN gọi được.</summary>
    public string WebhookToken { get; set; } = "";
    public bool Enabled => !string.IsNullOrWhiteSpace(Token) && ShopId > 0;
}

public record GhnKienHang(int KhoiLuongGram, decimal GiaTriHang, decimal TienThuHo, string TenNguoiNhan, string SoDienThoai,
    string DiaChi, int MaQuanHuyen, string MaPhuongXa, string MaDonCuaHang, string? GhiChu);

public interface IGhnClient
{
    Task<decimal> TinhPhiAsync(int maQuanHuyen, string maPhuongXa, int khoiLuongGram, decimal giaTriHang, CancellationToken ct = default);
    Task<string> TaoDonAsync(GhnKienHang kien, CancellationToken ct = default);
}

/// <summary>Gọi API Giao Hàng Nhanh (môi trường dev). Timeout 10 giây, lỗi được ném ra để tầng nghiệp vụ xử lý (NFR06).</summary>
public class GhnClient(HttpClient http, IOptions<GhnOptions> options, ILogger<GhnClient> logger) : IGhnClient
{
    private readonly GhnOptions _opt = options.Value;

    public async Task<decimal> TinhPhiAsync(int maQuanHuyen, string maPhuongXa, int khoiLuongGram, decimal giaTriHang, CancellationToken ct = default)
    {
        var body = new
        {
            service_type_id = 2,
            from_district_id = _opt.FromDistrictId,
            from_ward_code = _opt.FromWardCode,
            to_district_id = maQuanHuyen,
            to_ward_code = maPhuongXa,
            weight = Math.Max(khoiLuongGram, 100),
            insurance_value = (long)giaTriHang
        };
        var res = await Send<GhnFee>("/v2/shipping-order/fee", body, ct);
        return res.Total;
    }

    public async Task<string> TaoDonAsync(GhnKienHang k, CancellationToken ct = default)
    {
        var body = new
        {
            payment_type_id = 1,          // shop trả phí cho GHN (phí ship đã thu của khách trong tổng đơn)
            required_note = "CHOXEMHANGKHONGTHU",
            to_name = k.TenNguoiNhan,
            to_phone = k.SoDienThoai,
            to_address = k.DiaChi,
            to_district_id = k.MaQuanHuyen,
            to_ward_code = k.MaPhuongXa,
            client_order_code = k.MaDonCuaHang,
            cod_amount = (long)k.TienThuHo,
            weight = Math.Max(k.KhoiLuongGram, 100),
            insurance_value = (long)k.GiaTriHang,
            service_type_id = 2,
            note = k.GhiChu,
            items = new[] { new { name = "Banh keo SweetMart", quantity = 1, weight = Math.Max(k.KhoiLuongGram, 100) } }
        };
        var res = await Send<GhnCreate>("/v2/shipping-order/create", body, ct);
        return res.OrderCode;
    }

    private async Task<T> Send<T>(string path, object body, CancellationToken ct)
    {
        using var req = new HttpRequestMessage(HttpMethod.Post, _opt.BaseUrl + path) { Content = JsonContent.Create(body) };
        req.Headers.Add("Token", _opt.Token);
        req.Headers.Add("ShopId", _opt.ShopId.ToString());
        using var resp = await http.SendAsync(req, ct);
        var text = await resp.Content.ReadAsStringAsync(ct);
        logger.LogInformation("GHN {Path} -> {Status}: {Body}", path, (int)resp.StatusCode, text);
        var env = JsonSerializer.Deserialize<GhnEnvelope<T>>(text);
        if (!resp.IsSuccessStatusCode || env?.Code != 200 || env.Data is null)
            throw new HttpRequestException($"GHN lỗi: {env?.Message ?? resp.StatusCode.ToString()}");
        return env.Data;
    }

    private class GhnEnvelope<T>
    {
        [JsonPropertyName("code")] public int Code { get; set; }
        [JsonPropertyName("message")] public string? Message { get; set; }
        [JsonPropertyName("data")] public T? Data { get; set; }
    }
    private class GhnFee { [JsonPropertyName("total")] public decimal Total { get; set; } }
    private class GhnCreate { [JsonPropertyName("order_code")] public string OrderCode { get; set; } = ""; }
}

/// <summary>Bản giả lập dùng khi chưa cấu hình token GHN (chạy demo, kiểm thử).</summary>
public class FakeGhnClient : IGhnClient
{
    public Task<decimal> TinhPhiAsync(int maQuanHuyen, string maPhuongXa, int khoiLuongGram, decimal giaTriHang, CancellationToken ct = default)
        => Task.FromResult(khoiLuongGram <= 1000 ? 22_000m : 22_000m + Math.Ceiling((khoiLuongGram - 1000) / 500m) * 5_000m);

    public Task<string> TaoDonAsync(GhnKienHang kien, CancellationToken ct = default)
        => Task.FromResult("FAKE" + Random.Shared.Next(100000, 999999));
}
