import { useCallback, useEffect, useState } from 'react'
import { api, qs } from '../../api'
import { ngay } from '../../format'
import { ChiCho } from './AdminLayout'

function Kho() {
  const [loc, setLoc] = useState('canDate')
  const [lo, setLo] = useState([])
  const [sapHet, setSapHet] = useState([])
  const [sanPham, setSanPham] = useState([])
  const [f, setF] = useState({ maSP: '', soLuong: 50, ngaySanXuat: '', hanSuDung: '' })
  const [loi, setLoi] = useState('')
  const [tb, setTb] = useState('')

  const tai = useCallback(() => {
    api.get('/api/admin/batches' + qs({ canDate: loc === 'canDate' || undefined, hetHan: loc === 'hetHan' || undefined })).then(setLo).catch((e) => setLoi(e.message))
    api.get('/api/admin/batches/low-stock').then(setSapHet).catch(() => {})
  }, [loc])
  useEffect(() => { tai() }, [tai])
  // Danh sách sản phẩm để chọn khi nhập lô (API công khai, không cần quyền Quản lý)
  useEffect(() => { api.get('/api/products?pageSize=48').then((r) => setSanPham(r.items)).catch(() => {}) }, [])

  const nhapLo = async (e) => {
    e.preventDefault(); setLoi(''); setTb('')
    try {
      const r = await api.post('/api/admin/batches', { maSP: Number(f.maSP), soLuong: Number(f.soLuong), ngaySanXuat: f.ngaySanXuat || null, hanSuDung: f.hanSuDung })
      setTb(`Đã nhập lô #${r.maLo}.`); setF({ ...f, soLuong: 50, ngaySanXuat: '', hanSuDung: '' }); tai()
    } catch (err) { setLoi(err.message) }
  }

  return (
    <div>
      <h2>Kho & lô hàng</h2>
      <div className="two-col">
        <div>
          <div className="tabs">
            <button className={loc === 'canDate' ? 'active' : ''} onClick={() => setLoc('canDate')}>Cận date (≤ 30 ngày)</button>
            <button className={loc === 'hetHan' ? 'active' : ''} onClick={() => setLoc('hetHan')}>Đã hết hạn</button>
            <button className={loc === '' ? 'active' : ''} onClick={() => setLoc('')}>Tất cả lô còn hàng</button>
          </div>
          <table className="table">
            <thead><tr><th>Lô</th><th>Sản phẩm</th><th>Tồn / Nhập</th><th>NSX</th><th>HSD</th><th></th></tr></thead>
            <tbody>
              {lo.map((l) => (
                <tr key={l.maLo}>
                  <td>#{l.maLo}</td><td>{l.tenSP}</td><td>{l.soLuongTon} / {l.soLuongNhap}</td>
                  <td>{ngay(l.ngaySanXuat)}</td><td><b>{ngay(l.hanSuDung)}</b></td>
                  <td>{l.hetHan ? <span className="badge do">Hết hạn</span> : l.canDate ? <span className="badge vang">Cận date</span> : null}</td>
                </tr>
              ))}
              {lo.length === 0 && <tr><td colSpan={6} className="muted">Không có lô nào.</td></tr>}
            </tbody>
          </table>
        </div>
        <div>
          <form className="panel form" onSubmit={nhapLo}>
            <h3>Nhập lô mới</h3>
            <label>Sản phẩm<select required value={f.maSP} onChange={(e) => setF({ ...f, maSP: e.target.value })}>
              <option value="">— Chọn —</option>
              {sanPham.map((p) => <option key={p.maSP} value={p.maSP}>{p.tenSP}</option>)}
            </select></label>
            <label>Số lượng<input type="number" min={1} required value={f.soLuong} onChange={(e) => setF({ ...f, soLuong: e.target.value })} /></label>
            <label>Ngày sản xuất<input type="date" value={f.ngaySanXuat} onChange={(e) => setF({ ...f, ngaySanXuat: e.target.value })} /></label>
            <label>Hạn sử dụng<input type="date" required value={f.hanSuDung} onChange={(e) => setF({ ...f, hanSuDung: e.target.value })} /></label>
            {loi && <p className="loi">{loi}</p>}
            {tb && <p className="ok">{tb}</p>}
            <button className="btn full">Nhập kho</button>
          </form>
          <div className="panel">
            <h3>Sắp hết hàng (&lt; 10)</h3>
            {sapHet.length === 0 ? <p className="muted">Không có.</p> : sapHet.map((s) => <div key={s.maSP} className="line small"><span>{s.tenSP}</span><b className={s.ton === 0 ? 'do-text' : ''}>{s.ton}</b></div>)}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function AdminKho() {
  return <ChiCho vaiTro={['NhanVien', 'QuanLy']}><Kho /></ChiCho>
}
