import { useCallback, useEffect, useState } from 'react'
import { api } from '../../api'
import { ngay, tien } from '../../format'
import { ChiCho } from './AdminLayout'

const homNay = () => new Date().toISOString().slice(0, 10)
const TRONG = { maCode: '', loaiGiam: 'SoTien', giaTriGiam: '', giamToiDa: '', donToiThieu: 0, ngayBatDau: homNay(), ngayKetThuc: '', soLuotConLai: 100 }

function KhuyenMai() {
  const [ds, setDs] = useState([])
  const [f, setF] = useState(null)
  const [loi, setLoi] = useState('')

  const tai = useCallback(() => api.get('/api/admin/vouchers').then(setDs).catch((e) => setLoi(e.message)), [])
  useEffect(() => { tai() }, [tai])

  const luu = async (e) => {
    e.preventDefault(); setLoi('')
    const body = {
      maCode: f.maCode, loaiGiam: f.loaiGiam, giaTriGiam: Number(f.giaTriGiam), giamToiDa: f.giamToiDa ? Number(f.giamToiDa) : null,
      donToiThieu: Number(f.donToiThieu), soLuotConLai: Number(f.soLuotConLai),
      ngayBatDau: new Date(f.ngayBatDau).toISOString(), ngayKetThuc: new Date(f.ngayKetThuc + 'T23:59:59').toISOString(),
    }
    try {
      if (f.maKM) await api.put('/api/admin/vouchers/' + f.maKM, body)
      else await api.post('/api/admin/vouchers', body)
      setF(null); tai()
    } catch (err) { setLoi(err.message) }
  }

  const sua = (k) => setF({ ...k, giamToiDa: k.giamToiDa ?? '', ngayBatDau: k.ngayBatDau.slice(0, 10), ngayKetThuc: k.ngayKetThuc.slice(0, 10) })
  const doi = (k) => (e) => setF({ ...f, [k]: e.target.value })
  const conHieuLuc = (k) => new Date(k.ngayKetThuc) > new Date() && new Date(k.ngayBatDau) <= new Date() && k.soLuotConLai > 0

  return (
    <div>
      <h2>Mã giảm giá</h2>
      {loi && <p className="loi">{loi}</p>}
      {f ? (
        <form className="panel form" onSubmit={luu}>
          <h3>{f.maKM ? 'Sửa mã ' + f.maCode : 'Tạo mã mới'}</h3>
          <div className="row3">
            <label>Mã<input required maxLength={30} value={f.maCode} onChange={(e) => setF({ ...f, maCode: e.target.value.toUpperCase() })} /></label>
            <label>Loại giảm<select value={f.loaiGiam} onChange={doi('loaiGiam')}><option value="SoTien">Số tiền</option><option value="PhanTram">Phần trăm</option></select></label>
            <label>Giá trị {f.loaiGiam === 'PhanTram' ? '(%)' : '(₫)'}<input type="number" min={1} required value={f.giaTriGiam} onChange={doi('giaTriGiam')} /></label>
          </div>
          <div className="row3">
            <label>Giảm tối đa (₫)<input type="number" min={0} disabled={f.loaiGiam !== 'PhanTram'} value={f.giamToiDa} onChange={doi('giamToiDa')} /></label>
            <label>Đơn tối thiểu (₫)<input type="number" min={0} required value={f.donToiThieu} onChange={doi('donToiThieu')} /></label>
            <label>Số lượt<input type="number" min={0} required value={f.soLuotConLai} onChange={doi('soLuotConLai')} /></label>
          </div>
          <div className="row2">
            <label>Ngày bắt đầu<input type="date" required value={f.ngayBatDau} onChange={doi('ngayBatDau')} /></label>
            <label>Ngày kết thúc<input type="date" required value={f.ngayKetThuc} onChange={doi('ngayKetThuc')} /></label>
          </div>
          <div className="actions"><button className="btn">Lưu</button><button type="button" className="btn outline" onClick={() => setF(null)}>Hủy</button></div>
        </form>
      ) : <div className="toolbar"><span /><button className="btn" onClick={() => setF(TRONG)}>+ Tạo mã</button></div>}
      <table className="table">
        <thead><tr><th>Mã</th><th>Mức giảm</th><th>Đơn tối thiểu</th><th>Hiệu lực</th><th>Lượt còn</th><th></th><th></th></tr></thead>
        <tbody>
          {ds.map((k) => (
            <tr key={k.maKM}>
              <td><b>{k.maCode}</b></td>
              <td>{k.loaiGiam === 'PhanTram' ? `${k.giaTriGiam}%${k.giamToiDa ? ' (tối đa ' + tien(k.giamToiDa) + ')' : ''}` : tien(k.giaTriGiam)}</td>
              <td>{tien(k.donToiThieu)}</td>
              <td>{ngay(k.ngayBatDau)} – {ngay(k.ngayKetThuc)}</td>
              <td>{k.soLuotConLai}</td>
              <td>{conHieuLuc(k) ? <span className="badge luc">Đang chạy</span> : <span className="badge xam">Không hiệu lực</span>}</td>
              <td><button className="link" onClick={() => sua(k)}>Sửa</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function AdminKhuyenMai() {
  return <ChiCho vaiTro={['QuanLy']}><KhuyenMai /></ChiCho>
}
