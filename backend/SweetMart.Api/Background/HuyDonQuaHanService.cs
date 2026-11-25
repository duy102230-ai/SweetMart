using Microsoft.EntityFrameworkCore;
using SweetMart.Api.Data;
using SweetMart.Api.Domain;
using SweetMart.Api.Services;

namespace SweetMart.Api.Background;

/// <summary>Mỗi phút hủy các đơn VNPay quá 15 phút chưa thanh toán và hoàn tồn kho (BR08).</summary>
public class HuyDonQuaHanService(IServiceScopeFactory scopes, ILogger<HuyDonQuaHanService> logger) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var timer = new PeriodicTimer(TimeSpan.FromMinutes(1));
        do
        {
            try
            {
                using var scope = scopes.CreateScope();
                var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
                var donHang = scope.ServiceProvider.GetRequiredService<DonHangService>();
                var han = DateTime.UtcNow.AddMinutes(-BusinessRules.PhutChoThanhToan);
                var quaHan = await db.DonHang.Where(d => d.TrangThai == TrangThaiDon.ChoThanhToan && d.NgayDat < han)
                                             .Select(d => d.MaDH).ToListAsync(stoppingToken);
                foreach (var maDH in quaHan)
                {
                    await donHang.HuyDonAsync(maDH, null, false, "Quá hạn thanh toán VNPay", stoppingToken);
                    logger.LogInformation("Đã hủy đơn {MaDH} do quá hạn thanh toán", maDH);
                }
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                logger.LogError(ex, "Lỗi khi hủy đơn quá hạn");
            }
        } while (await timer.WaitForNextTickAsync(stoppingToken));
    }
}
