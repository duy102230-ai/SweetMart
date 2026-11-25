import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import { tien } from '../format'

export default function GioHang() {
  const { taiGio } = useAuth()
  const nav = useNavigate()
  const [gio, setGio] = useState(null)
  const [loi, setLoi] = useState('')

  const tai = useCallback(() => api.get('/api/cart').then(setGio).catch((e) => setLoi(e.message)), [])
  useEffect(() => { tai() }, [tai])

  const doiSoLuong = async (maSP, soLuong) => {
    setLoi('')
    try {
      if (soLuong <= 0) await api.del('/api/cart/items/' + maSP)
      else await api.put('/api/cart/items', { maSP, soLuong })
      await tai(); taiGio()
    } catch (e) { setLoi(e.message) }
  }

  if (!gio) return <div className="container">{loi || 'Đang tải…'}</div>
  const tong = gio.reduce((s, i) => s + i.thanhTien, 0)
  const vuotTon = gio.some((i) => i.soLuong > i.tonKhaDung)

  return (
    <div className="container">
      <h2>Giỏ hàng</h2>
      {loi && <p className="loi">{loi}</p>}
      {gio.length === 0 ? <p>Giỏ hàng trống. <Link to="/">Tiếp tục mua sắm</Link></p> : (
        <div className="two-col">
          <table className="table">
            <thead><tr><th>Sản phẩm</th><th>Đơn giá</th><th>Số lượng</th><th>Thành tiền</th><th></th></tr></thead>
            <tbody>
              {gio.map((i) => (
                <tr key={i.maSP}>
                  <td><div className="row-sp"><img src={i.hinhAnh} alt="" /><Link to={'/san-pham/' + i.maSP}>{i.tenSP}</Link></div>
                    {i.soLuong > i.tonKhaDung && <div className="loi small">Chỉ còn {i.tonKhaDung} sản phẩm</div>}</td>
                  <td>{tien(i.giaBan)}</td>
                  <td><div className="qty">
                    <button onClick={() => doiSoLuong(i.maSP, i.soLuong - 1)}>−</button>
                    <input value={i.soLuong} readOnly />
                    <button onClick={() => doiSoLuong(i.maSP, i.soLuong + 1)} disabled={i.soLuong >= i.tonKhaDung}>+</button>
                  </div></td>
                  <td><b>{tien(i.thanhTien)}</b></td>
                  <td><button className="link do-text" onClick={() => doiSoLuong(i.maSP, 0)}>Xóa</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="summary">
            <div className="line"><span>Tạm tính</span><b>{tien(tong)}</b></div>
            <p className="muted small">{tong >= 300000 ? 'Đơn hàng được miễn phí vận chuyển.' : `Mua thêm ${tien(300000 - tong)} để được miễn phí vận chuyển.`}</p>
            <button className="btn full" disabled={vuotTon} onClick={() => nav('/thanh-toan')}>Tiến hành đặt hàng</button>
          </div>
        </div>
      )}
    </div>
  )
}
