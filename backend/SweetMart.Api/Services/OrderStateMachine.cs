using SweetMart.Api.Domain;

namespace SweetMart.Api.Services;

/// <summary>Các chuyển trạng thái hợp lệ của đơn hàng (sơ đồ trạng thái – Bước 3, BR10).</summary>
public static class OrderStateMachine
{
    private static readonly Dictionary<TrangThaiDon, TrangThaiDon[]> HopLe = new()
    {
        [TrangThaiDon.ChoThanhToan] = [TrangThaiDon.ChoXacNhan, TrangThaiDon.DaHuy],
        [TrangThaiDon.ChoXacNhan] = [TrangThaiDon.DaXacNhan, TrangThaiDon.DaHuy],
        [TrangThaiDon.DaXacNhan] = [TrangThaiDon.DangDongGoi, TrangThaiDon.DaHuy],
        [TrangThaiDon.DangDongGoi] = [TrangThaiDon.DangGiao],
        [TrangThaiDon.DangGiao] = [TrangThaiDon.DaGiao, TrangThaiDon.GiaoThatBai],
        [TrangThaiDon.GiaoThatBai] = [TrangThaiDon.DaHuy],
        [TrangThaiDon.DaGiao] = [],
        [TrangThaiDon.DaHuy] = [],
    };

    public static bool CoTheChuyen(TrangThaiDon tu, TrangThaiDon den) => HopLe[tu].Contains(den);

    public static IReadOnlyList<TrangThaiDon> TiepTheo(TrangThaiDon tu) => HopLe[tu];
}
