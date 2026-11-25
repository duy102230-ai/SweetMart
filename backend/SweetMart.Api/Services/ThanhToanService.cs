using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using SweetMart.Api.Data;
using SweetMart.Api.Domain;
using SweetMart.Api.Integrations;

namespace SweetMart.Api.Services;

public record IpnResult(string RspCode, string Message);

/// <summary>Xử lý kết quả thanh toán VNPay gửi về qua IPN (BR08, NFR06).</summary>
public class ThanhToanService(AppDbContext db, VnPayClient vnPay, DonHangService donHang, ILogger<ThanhToanService> logger)
{
    public async Task<IpnResult> XuLyIpnAsync(Dictionary<string, string> q, CancellationToken ct = default)
    {
        logger.LogInformation("VNPay IPN: {Data}", JsonSerializer.Serialize(q));
        if (!vnPay.XacThucChuKy(q)) return new("97", "Invalid signature");

        if (!int.TryParse(q.GetValueOrDefault("vnp_TxnRef"), out var maDH)) return new("01", "Order not found");
        var don = await db.DonHang.Include(d => d.LichSu).FirstOrDefaultAsync(d => d.MaDH == maDH, ct);
        if (don is null) return new("01", "Order not found");

        if (!long.TryParse(q.GetValueOrDefault("vnp_Amount"), out var amount) || amount != (long)(don.TongThanhToan * 100))
            return new("04", "Invalid amount");

        // Đơn đã được xử lý trước đó (IPN gửi lại) → không ghi nhận trùng.
        if (don.TrangThaiThanhToan != TrangThaiThanhToan.ChoThanhToan || don.TrangThai != TrangThaiDon.ChoThanhToan)
            return new("02", "Order already confirmed");

        var thanhCong = q.GetValueOrDefault("vnp_ResponseCode") == "00" && q.GetValueOrDefault("vnp_TransactionStatus") == "00";
        db.ThanhToan.Add(new ThanhToan
        {
            MaDH = maDH,
            SoTien = don.TongThanhToan,
            MaGiaoDichVNPay = q.GetValueOrDefault("vnp_TransactionNo"),
            MaNganHang = q.GetValueOrDefault("vnp_BankCode"),
            TrangThai = thanhCong ? "ThanhCong" : "ThatBai",
            DuLieuIPN = JsonSerializer.Serialize(q)
        });

        if (thanhCong)
        {
            don.LichSu.Add(new LichSuDonHang { TrangThaiCu = don.TrangThai, TrangThaiMoi = TrangThaiDon.ChoXacNhan, GhiChu = "VNPay xác nhận thanh toán" });
            don.TrangThai = TrangThaiDon.ChoXacNhan;
            don.TrangThaiThanhToan = TrangThaiThanhToan.DaThanhToan;
        }
        // Thất bại: giữ "Chờ thanh toán", job HuyDonQuaHan sẽ hủy và hoàn kho sau 15 phút.
        await db.SaveChangesAsync(ct);
        if (thanhCong) await donHang.GuiEmailTrangThaiAsync(don, "Thanh toán thành công", ct);
        return new("00", "Confirm Success");
    }
}
