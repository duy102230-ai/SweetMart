using Microsoft.EntityFrameworkCore;
using SweetMart.Api.Data;
using SweetMart.Api.Domain;
using SweetMart.Api.Dtos;

namespace SweetMart.Api.Services;

/// <summary>Báo cáo doanh thu (FR20). Doanh thu chỉ tính các đơn "Đã giao".</summary>
public class BaoCaoService(AppDbContext db)
{
    public async Task<BaoCaoDoanhThu> DoanhThuAsync(DateOnly tuNgay, DateOnly denNgay, CancellationToken ct = default)
    {
        // Ngày theo giờ Việt Nam → khoảng thời gian UTC tương ứng
        var tuUtc = tuNgay.ToDateTime(TimeOnly.MinValue).AddHours(-7);
        var denUtc = denNgay.AddDays(1).ToDateTime(TimeOnly.MinValue).AddHours(-7);

        var donTrongKy = db.DonHang.Where(d => d.NgayDat >= tuUtc && d.NgayDat < denUtc);
        var daGiao = await donTrongKy.Where(d => d.TrangThai == TrangThaiDon.DaGiao)
                                     .Select(d => new { d.NgayDat, d.TongThanhToan }).ToListAsync(ct);

        var theoNgay = daGiao.GroupBy(d => DateOnly.FromDateTime(d.NgayDat.AddHours(7)))
                             .OrderBy(g => g.Key)
                             .Select(g => new DoanhThuNgay(g.Key, g.Count(), g.Sum(x => x.TongThanhToan)))
                             .ToList();

        var dong = await db.ChiTietDonHang
            .Where(c => db.DonHang.Any(d => d.MaDH == c.MaDH && d.TrangThai == TrangThaiDon.DaGiao && d.NgayDat >= tuUtc && d.NgayDat < denUtc))
            .Select(c => new { c.MaSP, c.SanPham!.TenSP, c.SoLuong, c.DonGia }).ToListAsync(ct);
        var top = dong.GroupBy(x => new { x.MaSP, x.TenSP })
                      .Select(g => new TopSanPham(g.Key.MaSP, g.Key.TenSP, g.Sum(x => x.SoLuong), g.Sum(x => x.SoLuong * x.DonGia)))
                      .OrderByDescending(x => x.SoLuongBan).Take(10).ToList();

        var theoTrangThai = (await donTrongKy.Select(d => d.TrangThai).ToListAsync(ct))
                            .GroupBy(t => t.ToString()).ToDictionary(g => g.Key, g => g.Count());

        return new BaoCaoDoanhThu(tuNgay, denNgay, daGiao.Sum(x => x.TongThanhToan), daGiao.Count, theoNgay, top, theoTrangThai);
    }
}
