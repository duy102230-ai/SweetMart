using Microsoft.EntityFrameworkCore;
using SweetMart.Api.Common;
using SweetMart.Api.Data;
using SweetMart.Api.Domain;

namespace SweetMart.Api.Services;

public record PhanBo(int MaLo, int SoLuong);

/// <summary>Giữ và hoàn tồn kho theo lô, áp dụng FEFO – lô hết hạn trước xuất trước (BR01, BR02, BR04).</summary>
public class TonKhoService(AppDbContext db)
{
    /// <summary>
    /// Giữ <paramref name="soLuong"/> sản phẩm, lấy từ các lô còn hạn có hạn sử dụng gần nhất trước.
    /// Phải gọi bên trong transaction: với SQL Server, các lô bị khóa UPDLOCK đến khi commit để hai đơn đồng thời không cùng trừ một lô.
    /// </summary>
    public async Task<List<PhanBo>> GiuHangAsync(int maSP, int soLuong, CancellationToken ct = default)
    {
        if (soLuong <= 0) throw new BusinessException("INVALID_QUANTITY", "Số lượng phải lớn hơn 0.");
        var homNay = Clock.HomNayVN();

        IQueryable<LoHang> query = db.Database.IsSqlServer()
            ? db.LoHang.FromSqlInterpolated($"SELECT * FROM LoHang WITH (UPDLOCK, ROWLOCK) WHERE MaSP = {maSP}")
            : db.LoHang.Where(l => l.MaSP == maSP);

        var cacLo = await query.Where(l => l.SoLuongTon > 0 && l.HanSuDung > homNay)
                               .OrderBy(l => l.HanSuDung).ThenBy(l => l.MaLo)
                               .ToListAsync(ct);

        var tongCo = cacLo.Sum(l => l.SoLuongTon);
        if (tongCo < soLuong)
            throw new BusinessException("OUT_OF_STOCK", $"Sản phẩm #{maSP} chỉ còn {tongCo} trong kho.", 409);

        var ketQua = new List<PhanBo>();
        var conLai = soLuong;
        foreach (var lo in cacLo)
        {
            if (conLai == 0) break;
            var lay = Math.Min(conLai, lo.SoLuongTon);
            lo.SoLuongTon -= lay;
            conLai -= lay;
            ketQua.Add(new PhanBo(lo.MaLo, lay));
        }
        return ketQua;
    }

    /// <summary>Cộng lại số lượng đã giữ của đơn vào đúng các lô (khi hủy hoặc giao thất bại).</summary>
    public async Task HoanKhoAsync(int maDH, CancellationToken ct = default)
    {
        var phanBo = await db.PhanBoLo.Where(p => p.MaDH == maDH).ToListAsync(ct);
        var maLos = phanBo.Select(p => p.MaLo).Distinct().ToList();
        var cacLo = await db.LoHang.Where(l => maLos.Contains(l.MaLo)).ToDictionaryAsync(l => l.MaLo, ct);
        foreach (var p in phanBo) cacLo[p.MaLo].SoLuongTon += p.SoLuong;
    }

    public Task<int> TonKhaDungAsync(int maSP, CancellationToken ct = default)
    {
        var homNay = Clock.HomNayVN();
        return db.LoHang.Where(l => l.MaSP == maSP && l.HanSuDung > homNay).SumAsync(l => l.SoLuongTon, ct);
    }
}
