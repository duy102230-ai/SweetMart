import { Badge, TRANG_THAI_DON, TRANG_THAI_TT, ngayGio, tien } from '../format'

/** Khối hiển thị chi tiết đơn – dùng chung cho trang khách hàng và trang quản trị. */
export default function DonHangChiTiet({ don, cotThem }) {
  return (
    <div className="order">
      <div className="order-head">
        <h2>Đơn {don.maHienThi} <Badge trangThai={don.trangThai} /></h2>
        <span className="muted">Đặt lúc {ngayGio(don.ngayDat)}</span>
      </div>
      <div className="grid3">
        <div className="panel"><h4>Người nhận</h4><b>{don.nguoiNhan}</b><div>{don.soDienThoaiNhan}</div><div className="muted">{don.diaChiGiao}</div></div>
        <div className="panel"><h4>Thanh toán</h4><div>{don.phuongThucTT === 'VNPAY' ? 'VNPay' : 'COD'}</div><div>{TRANG_THAI_TT[don.trangThaiThanhToan] || don.trangThaiThanhToan}</div></div>
        <div className="panel"><h4>Vận chuyển</h4><div>GHN: {don.maVanDonGHN || 'chưa tạo vận đơn'}</div>{don.ghiChu && <div className="muted">Ghi chú: {don.ghiChu}</div>}</div>
      </div>
      <table className="table">
        <thead><tr><th>Sản phẩm</th><th>Đơn giá</th><th>SL</th><th>Thành tiền</th>{cotThem && <th></th>}</tr></thead>
        <tbody>
          {don.chiTiet.map((c) => (
            <tr key={c.maSP}><td>{c.tenSP}</td><td>{tien(c.donGia)}</td><td>{c.soLuong}</td><td>{tien(c.thanhTien)}</td>{cotThem && <td>{cotThem(c)}</td>}</tr>
          ))}
        </tbody>
      </table>
      <div className="totals">
        <div className="line"><span>Tiền hàng</span><span>{tien(don.tongTienHang)}</span></div>
        <div className="line"><span>Giảm giá</span><span>− {tien(don.tienGiam)}</span></div>
        <div className="line"><span>Phí vận chuyển</span><span>{tien(don.phiVanChuyen)}</span></div>
        <div className="line total"><span>Tổng thanh toán</span><b>{tien(don.tongThanhToan)}</b></div>
      </div>
      <h4>Lịch sử trạng thái</h4>
      <ol className="timeline">
        {don.lichSu.map((l, i) => (
          <li key={i}><b>{TRANG_THAI_DON[l.trangThaiMoi]?.ten || l.trangThaiMoi}</b> <span className="muted small">{ngayGio(l.thoiGian)}</span>{l.ghiChu && <div className="small">{l.ghiChu}</div>}</li>
        ))}
      </ol>
    </div>
  )
}
