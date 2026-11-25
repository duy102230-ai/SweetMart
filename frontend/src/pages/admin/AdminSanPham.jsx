import { useCallback, useEffect, useState } from 'react'
import { api, qs } from '../../api'
import { tien } from '../../format'
import { ChiCho } from './AdminLayout'

const TRONG = { tenSP: '', maDM: '', thuongHieu: '', giaBan: '', donViTinh: 'gói', khoiLuongGram: '', moTa: '', hinhAnh: '', dangBan: true }

function SanPham() {
  const [ds, setDs] = useState([])
  const [danhMuc, setDanhMuc] = useState([])
  const [keyword, setKeyword] = useState('')
  const [f, setF] = useState(null)      // form thêm/sửa; f.maSP có giá trị = đang sửa
  const [tenDM, setTenDM] = useState('')
  const [loi, setLoi] = useState('')
  const [tb, setTb] = useState('')

  const tai = useCallback(() => api.get('/api/admin/products' + qs({ keyword })).then(setDs).catch((e) => setLoi(e.message)), [keyword])
  const taiDM = () => api.get('/api/categories').then(setDanhMuc).catch(() => {})
  useEffect(() => { tai() }, [tai])
  useEffect(() => { taiDM() }, [])

  const luu = async (e) => {
    e.preventDefault(); setLoi(''); setTb('')
    const body = {
      tenSP: f.tenSP, maDM: Number(f.maDM), thuongHieu: f.thuongHieu || null, giaBan: Number(f.giaBan), donViTinh: f.donViTinh,
      khoiLuongGram: Number(f.khoiLuongGram), moTa: f.moTa || null, dangBan: f.dangBan,
      hinhAnh: f.hinhAnh.split('\n').map((s) => s.trim()).filter(Boolean),
    }
    try {
      if (f.maSP) await api.put('/api/admin/products/' + f.maSP, body)
      else await api.post('/api/admin/products', body)
      setTb(f.maSP ? 'Đã cập nhật sản phẩm.' : 'Đã thêm sản phẩm. Hãy nhập lô hàng để mở bán.'); setF(null); tai()
    } catch (err) { setLoi(err.message) }
  }

  const ngungBan = async (p) => {
    if (!window.confirm(`Ngừng bán “${p.tenSP}”? Sản phẩm vẫn được giữ trong lịch sử đơn hàng.`)) return
    try { await api.del('/api/admin/products/' + p.maSP); tai() } catch (e) { setLoi(e.message) }
  }

  const themDM = async (e) => {
    e.preventDefault()
    try { await api.post('/api/admin/categories', { tenDanhMuc: tenDM, maDMCha: null }); setTenDM(''); taiDM() } catch (err) { setLoi(err.message) }
  }
  const xoaDM = async (d) => {
    if (!window.confirm(`Xóa danh mục “${d.tenDanhMuc}”?`)) return
    try { await api.del('/api/admin/categories/' + d.maDM); taiDM() } catch (err) { setLoi(err.message) }
  }

  const doi = (k) => (e) => setF({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value })

  return (
    <div>
      <h2>Sản phẩm & danh mục</h2>
      {loi && <p className="loi">{loi}</p>}
      {tb && <p className="ok">{tb}</p>}
      {f ? (
        <form className="panel form" onSubmit={luu}>
          <h3>{f.maSP ? 'Sửa sản phẩm #' + f.maSP : 'Thêm sản phẩm'}</h3>
          <label>Tên sản phẩm<input required maxLength={200} value={f.tenSP} onChange={doi('tenSP')} /></label>
          <div className="row2">
            <label>Danh mục<select required value={f.maDM} onChange={doi('maDM')}><option value="">— Chọn —</option>{danhMuc.map((d) => <option key={d.maDM} value={d.maDM}>{d.tenDanhMuc}</option>)}</select></label>
            <label>Thương hiệu<input value={f.thuongHieu} onChange={doi('thuongHieu')} /></label>
          </div>
          <div className="row3">
            <label>Giá bán (₫)<input type="number" min={1} required value={f.giaBan} onChange={doi('giaBan')} /></label>
            <label>Đơn vị tính<input required value={f.donViTinh} onChange={doi('donViTinh')} /></label>
            <label>Khối lượng (g)<input type="number" min={1} required value={f.khoiLuongGram} onChange={doi('khoiLuongGram')} /></label>
          </div>
          <label>Mô tả<textarea rows={3} value={f.moTa} onChange={doi('moTa')} /></label>
          <label>Đường dẫn ảnh (mỗi dòng một ảnh)<textarea rows={2} required value={f.hinhAnh} onChange={doi('hinhAnh')} /></label>
          <label className="check"><input type="checkbox" checked={f.dangBan} onChange={doi('dangBan')} /> Đang bán</label>
          <div className="actions"><button className="btn">Lưu</button><button type="button" className="btn outline" onClick={() => setF(null)}>Hủy</button></div>
        </form>
      ) : (
        <div className="toolbar">
          <form onSubmit={(e) => { e.preventDefault(); setKeyword(e.target.k.value) }}><input name="k" placeholder="Tìm theo tên" /> <button className="btn outline">Tìm</button></form>
          <button className="btn" onClick={() => setF(TRONG)}>+ Thêm sản phẩm</button>
        </div>
      )}
      <div className="two-col wide-left">
        <table className="table">
          <thead><tr><th></th><th>Sản phẩm</th><th>Giá</th><th>Tồn</th><th>Trạng thái</th><th></th></tr></thead>
          <tbody>
            {ds.map((p) => (
              <tr key={p.maSP}>
                <td><img className="thumb" src={p.hinhAnh[0]} alt="" /></td>
                <td>{p.tenSP}<div className="muted small">{p.thuongHieu} · {p.tenDanhMuc}</div></td>
                <td>{tien(p.giaBan)}</td>
                <td>{p.tonKhaDung}</td>
                <td>{p.dangBan ? <span className="badge luc">Đang bán</span> : <span className="badge xam">Ngừng bán</span>}</td>
                <td className="nowrap">
                  <button className="link" onClick={() => setF({ ...p, thuongHieu: p.thuongHieu || '', moTa: p.moTa || '', hinhAnh: p.hinhAnh.join('\n') })}>Sửa</button>
                  {p.dangBan && <> · <button className="link do-text" onClick={() => ngungBan(p)}>Ngừng bán</button></>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="panel">
          <h3>Danh mục</h3>
          {danhMuc.map((d) => <div key={d.maDM} className="line small"><span>{d.tenDanhMuc}</span><button className="link do-text" onClick={() => xoaDM(d)}>Xóa</button></div>)}
          <form className="voucher" onSubmit={themDM}><input required placeholder="Tên danh mục mới" value={tenDM} onChange={(e) => setTenDM(e.target.value)} /><button className="btn outline">Thêm</button></form>
        </div>
      </div>
    </div>
  )
}

export default function AdminSanPham() {
  return <ChiCho vaiTro={['QuanLy']}><SanPham /></ChiCho>
}
