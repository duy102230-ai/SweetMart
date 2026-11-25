import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { Badge, ngayGio, tien } from '../format'

export default function DonCuaToi() {
  const [ds, setDs] = useState(null)
  const [loi, setLoi] = useState('')
  useEffect(() => { api.get('/api/orders/my').then(setDs).catch((e) => setLoi(e.message)) }, [])

  return (
    <div className="container">
      <h2>Đơn hàng của tôi</h2>
      {loi && <p className="loi">{loi}</p>}
      {ds && ds.length === 0 && <p>Bạn chưa có đơn hàng nào. <Link to="/">Mua sắm ngay</Link></p>}
      {ds && ds.length > 0 && (
        <table className="table">
          <thead><tr><th>Mã đơn</th><th>Ngày đặt</th><th>Số SP</th><th>Tổng tiền</th><th>Trạng thái</th><th>Vận đơn GHN</th></tr></thead>
          <tbody>
            {ds.map((d) => (
              <tr key={d.maDH}>
                <td><Link to={'/don-hang/' + d.maDH}><b>SM{String(d.maDH).padStart(6, '0')}</b></Link></td>
                <td>{ngayGio(d.ngayDat)}</td>
                <td>{d.soSanPham}</td>
                <td>{tien(d.tongThanhToan)}</td>
                <td><Badge trangThai={d.trangThai} /></td>
                <td>{d.maVanDonGHN || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
