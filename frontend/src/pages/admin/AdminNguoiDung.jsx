import { useCallback, useEffect, useState } from 'react'
import { api } from '../../api'
import { ngay } from '../../format'
import { ChiCho } from './AdminLayout'

const TEN_VT = { KhachHang: 'Khách hàng', NhanVien: 'Nhân viên', QuanLy: 'Quản lý', QuanTri: 'Quản trị' }

function NguoiDung() {
  const [ds, setDs] = useState([])
  const [f, setF] = useState({ hoTen: '', email: '', matKhau: '', maVaiTro: 2 })
  const [loi, setLoi] = useState('')
  const [tb, setTb] = useState('')

  const tai = useCallback(() => api.get('/api/admin/users').then(setDs).catch((e) => setLoi(e.message)), [])
  useEffect(() => { tai() }, [tai])

  const tao = async (e) => {
    e.preventDefault(); setLoi(''); setTb('')
    try { await api.post('/api/admin/users', { ...f, maVaiTro: Number(f.maVaiTro) }); setTb('Đã tạo tài khoản ' + f.email); setF({ hoTen: '', email: '', matKhau: '', maVaiTro: 2 }); tai() }
    catch (err) { setLoi(err.message) }
  }
  const doiKhoa = async (u) => {
    setLoi('')
    try { await api.put(`/api/admin/users/${u.maND}/active?value=${!u.hoatDong}`); tai() } catch (e) { setLoi(e.message) }
  }

  return (
    <div>
      <h2>Người dùng</h2>
      {loi && <p className="loi">{loi}</p>}
      {tb && <p className="ok">{tb}</p>}
      <div className="two-col wide-left">
        <table className="table">
          <thead><tr><th>Họ tên</th><th>Email</th><th>Vai trò</th><th>Ngày tạo</th><th>Trạng thái</th><th></th></tr></thead>
          <tbody>
            {ds.map((u) => (
              <tr key={u.maND}>
                <td>{u.hoTen}</td><td>{u.email}</td><td>{TEN_VT[u.vaiTro] || u.vaiTro}</td><td>{ngay(u.ngayTao)}</td>
                <td>{u.hoatDong ? <span className="badge luc">Hoạt động</span> : <span className="badge do">Đã khóa</span>}</td>
                <td><button className="link" onClick={() => doiKhoa(u)}>{u.hoatDong ? 'Khóa' : 'Mở khóa'}</button></td>
              </tr>
            ))}
          </tbody>
        </table>
        <form className="panel form" onSubmit={tao}>
          <h3>Tạo tài khoản nội bộ</h3>
          <label>Họ tên<input required value={f.hoTen} onChange={(e) => setF({ ...f, hoTen: e.target.value })} /></label>
          <label>Email<input type="email" required value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></label>
          <label>Mật khẩu ban đầu<input type="password" required minLength={8} value={f.matKhau} onChange={(e) => setF({ ...f, matKhau: e.target.value })} autoComplete="new-password" /></label>
          <label>Vai trò<select value={f.maVaiTro} onChange={(e) => setF({ ...f, maVaiTro: e.target.value })}>
            <option value={2}>Nhân viên</option><option value={3}>Quản lý</option><option value={4}>Quản trị</option>
          </select></label>
          <button className="btn full">Tạo tài khoản</button>
        </form>
      </div>
    </div>
  )
}

export default function AdminNguoiDung() {
  return <ChiCho vaiTro={['QuanTri']}><NguoiDung /></ChiCho>
}
