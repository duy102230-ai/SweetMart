using System.Net;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Options;

namespace SweetMart.Api.Integrations;

public class VnPayOptions
{
    public string BaseUrl { get; set; } = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html";
    public string TmnCode { get; set; } = "";
    public string HashSecret { get; set; } = "";
    /// <summary>Trang Frontend hiển thị kết quả sau khi VNPay chuyển khách về.</summary>
    public string ReturnUrl { get; set; } = "http://localhost:5173/thanh-toan/ket-qua";
}

/// <summary>
/// Đóng gói giao thức VNPay 2.1.0: tạo URL thanh toán có chữ ký và xác thực chữ ký dữ liệu VNPay gửi về.
/// Chỉ xử lý chữ ký và tham số; việc cập nhật đơn hàng nằm ở ThanhToanService.
/// </summary>
public class VnPayClient(IOptions<VnPayOptions> options)
{
    private readonly VnPayOptions _opt = options.Value;

    public string TaoUrlThanhToan(int maDH, decimal soTien, string ipAddress, DateTime thoiDiemUtc)
    {
        var gioVN = thoiDiemUtc.AddHours(7);
        var p = new SortedDictionary<string, string>(StringComparer.Ordinal)
        {
            ["vnp_Version"] = "2.1.0",
            ["vnp_Command"] = "pay",
            ["vnp_TmnCode"] = _opt.TmnCode,
            ["vnp_Amount"] = ((long)(soTien * 100)).ToString(),   // VNPay yêu cầu nhân 100
            ["vnp_CurrCode"] = "VND",
            ["vnp_TxnRef"] = maDH.ToString(),
            ["vnp_OrderInfo"] = $"Thanh toan don hang SM{maDH:D6}",
            ["vnp_OrderType"] = "other",
            ["vnp_Locale"] = "vn",
            ["vnp_ReturnUrl"] = _opt.ReturnUrl,
            ["vnp_IpAddr"] = ipAddress,
            ["vnp_CreateDate"] = gioVN.ToString("yyyyMMddHHmmss"),
            ["vnp_ExpireDate"] = gioVN.AddMinutes(Domain.BusinessRules.PhutChoThanhToan).ToString("yyyyMMddHHmmss"),
        };
        var query = BuildQuery(p);
        return $"{_opt.BaseUrl}?{query}&vnp_SecureHash={HmacSha512(_opt.HashSecret, query)}";
    }

    /// <summary>Kiểm tra vnp_SecureHash của dữ liệu VNPay gửi về (IPN hoặc ReturnUrl).</summary>
    public bool XacThucChuKy(IEnumerable<KeyValuePair<string, string>> thamSo)
    {
        var dict = thamSo.Where(x => x.Key.StartsWith("vnp_", StringComparison.Ordinal))
                         .ToDictionary(x => x.Key, x => x.Value);
        if (!dict.TryGetValue("vnp_SecureHash", out var hashNhan) || string.IsNullOrEmpty(hashNhan)) return false;
        dict.Remove("vnp_SecureHash");
        dict.Remove("vnp_SecureHashType");
        var query = BuildQuery(new SortedDictionary<string, string>(dict, StringComparer.Ordinal));
        var hashTinh = HmacSha512(_opt.HashSecret, query);
        return CryptographicOperations.FixedTimeEquals(
            Encoding.ASCII.GetBytes(hashTinh.ToLowerInvariant()), Encoding.ASCII.GetBytes(hashNhan.ToLowerInvariant()));
    }

    private static string BuildQuery(IEnumerable<KeyValuePair<string, string>> p) =>
        string.Join("&", p.Where(x => !string.IsNullOrEmpty(x.Value))
                          .Select(x => $"{WebUtility.UrlEncode(x.Key)}={WebUtility.UrlEncode(x.Value)}"));

    public static string HmacSha512(string key, string data)
    {
        using var hmac = new HMACSHA512(Encoding.UTF8.GetBytes(key));
        return Convert.ToHexString(hmac.ComputeHash(Encoding.UTF8.GetBytes(data))).ToLowerInvariant();
    }
}
