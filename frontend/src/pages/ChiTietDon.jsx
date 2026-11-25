import { useCallback, useEffect, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import DonHangChiTiet from '../components/DonHangChiTiet'

export default function ChiTietDon() {
  const { id } = useParams()
  const [params] = useSearchParams()
  const [don, setDon] = useState(null)
  const [loi, setLoi] = useState('')
  const [tb, setTb] = useState('')
  const [danhGia, setDanhGia] = useState(null)   // { maSP, tenSP, soSao, noiDung }
  const [daDanhGia, setDaDanhGia] = useState([])

  const tai = useCallback(() => api.get('/api/orders/' + id).then(setDon).catch((e) => setLoi(e.message)), [id])
  useEffect(() => { tai() }, [tai])

  const huy = async () => {
    const lyDo = window.prompt('Lý do hủy đơn?')
    if (!lyDo) return
    try { await api.put(`/api/orders/${id}/cancel`, { lyDo }); setTb('Đã hủy đơn hàng.'); tai() } catch (e) { setLoi(e.message) }
  }

  const guiDanhGia = async (e) => {
    e.preventDefault()
    try {
      await api.post('/api/reviews', { maDH: Number(id), maSP: danhGia.maSP, soSao: danhGia.soSao, noiDung: danhGia.noiDung })
      setDaDanhGia([...daDanhGia, danhGia.maSP]); setDanhGia(null); setTb('Cảm ơn bạn đã đánh giá!')
    } catch (err) { setLoi(err.message) }
  }

  if (!don) return <div className="container">{loi ? <p className="loi">{loi}</p> : 'Đang tải…'}</div>
  const coTheHuy = ['ChoThanhToan', 'ChoXacNhan'].includes(don.trangThai)

  return (
    <div className="container">
      <p className="breadcrumb"><Link to="/don-hang">← Đơn hàng của tôi</Link></p>
      {params.get('moi') && <p className="ok">🎉 Đặt hàng thành công! Email xác nhận đã được gửi tới bạn.</p>}
      {tb && <p className="ok">{tb}</p>}
      {loi && <p className="loi">{loi}</p>}
      <DonHangChiTiet don={don} cotThem={don.trangThai === 'DaGiao' ? (c) => daDanhGia.includes(c.maSP)
        ? <span className="muted small">Đã đánh giá</span>
        : <button className="link" onClick={() => setDanhGia({ maSP: c.maSP, tenSP: c.tenSP, soSao: 5, noiDung: '' })}>Đánh giá</button> : null} />
      {danhGia && (
        <form className="panel form" onSubmit={guiDanhGia}>
          <h4>Đánh giá “{danhGia.tenSP}”</h4>
          <div className="stars pick">{[1, 2, 3, 4, 5].map((n) => <span key={n} onClick={() => setDanhGia({ ...danhGia, soSao: n })}>{n <= danhGia.soSao ? '★' : '☆'}</span>)}</div>
          <textarea rows={3} maxLength={1000} value={danhGia.noiDung} onChange={(e) => setDanhGia({ ...danhGia, noiDung: e.target.value })} placeholder="Cảm nhận của bạn về sản phẩm" />
          <div className="actions"><button className="btn">Gửi đánh giá</button><button type="button" className="btn outline" onClick={() => setDanhGia(null)}>Hủy</button></div>
        </form>
      )}
      {coTheHuy && <button className="btn danger" onClick={huy}>Hủy đơn hàng</button>}
    </div>
  )
}
