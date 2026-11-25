import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { laNoiBo, useAuth } from '../auth'

function Khung({ tieuDe, children }) {
  return <div className="container auth"><div className="panel"><h2>{tieuDe}</h2>{children}</div></div>
}

export function DangNhap() {
  const { dangNhap } = useAuth()
  const nav = useNavigate()
  const [params] = useSearchParams()
  const [email, setEmail] = useState('')
  const [matKhau, setMatKhau] = useState('')
  const [loi, setLoi] = useState('')

  const gui = async (e) => {
    e.preventDefault(); setLoi('')
    try {
      const u = await dangNhap(email, matKhau)
      nav(params.get('next') || (laNoiBo(u) ? (u.vaiTro === 'QuanTri' ? '/quan-tri/nguoi-dung' : '/quan-tri') : '/'), { replace: true })
    } catch (err) { setLoi(err.message) }
  }

  return (
    <Khung tieuDe="Đăng nhập">
      <form className="form" onSubmit={gui}>
        <label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="username" /></label>
        <label>Mật khẩu<input type="password" required value={matKhau} onChange={(e) => setMatKhau(e.target.value)} autoComplete="current-password" /></label>
        {loi && <p className="loi">{loi}</p>}
        <button className="btn full">Đăng nhập</button>
      </form>
      <p className="small"><Link to="/quen-mat-khau">Quên mật khẩu?</Link> · Chưa có tài khoản? <Link to="/dang-ky">Đăng ký</Link></p>
    </Khung>
  )
}

export function DangKy() {
  const { dangKy } = useAuth()
  const nav = useNavigate()
  const [f, setF] = useState({ hoTen: '', email: '', soDienThoai: '', matKhau: '', nhapLai: '' })
  const [loi, setLoi] = useState('')
  const doi = (k) => (e) => setF({ ...f, [k]: e.target.value })

  const gui = async (e) => {
    e.preventDefault(); setLoi('')
    if (f.matKhau !== f.nhapLai) { setLoi('Mật khẩu nhập lại không khớp.'); return }
    try {
      await dangKy({ hoTen: f.hoTen, email: f.email, soDienThoai: f.soDienThoai || null, matKhau: f.matKhau })
      nav('/', { replace: true })
    } catch (err) { setLoi(err.message) }
  }

  return (
    <Khung tieuDe="Tạo tài khoản">
      <form className="form" onSubmit={gui}>
        <label>Họ tên<input required maxLength={100} value={f.hoTen} onChange={doi('hoTen')} /></label>
        <label>Email<input type="email" required value={f.email} onChange={doi('email')} /></label>
        <label>Số điện thoại<input pattern="0\d{9,10}" value={f.soDienThoai} onChange={doi('soDienThoai')} /></label>
        <label>Mật khẩu (tối thiểu 8 ký tự, có chữ và số)<input type="password" required minLength={8} value={f.matKhau} onChange={doi('matKhau')} autoComplete="new-password" /></label>
        <label>Nhập lại mật khẩu<input type="password" required value={f.nhapLai} onChange={doi('nhapLai')} autoComplete="new-password" /></label>
        {loi && <p className="loi">{loi}</p>}
        <button className="btn full">Đăng ký</button>
      </form>
      <p className="small">Đã có tài khoản? <Link to="/dang-nhap">Đăng nhập</Link></p>
    </Khung>
  )
}

export function QuenMatKhau() {
  const [email, setEmail] = useState('')
  const [tb, setTb] = useState('')
  const [loi, setLoi] = useState('')
  const gui = async (e) => {
    e.preventDefault(); setLoi('')
    try { const r = await api.post('/api/auth/forgot-password', { email }); setTb(r.message) } catch (err) { setLoi(err.message) }
  }
  return (
    <Khung tieuDe="Quên mật khẩu">
      {tb ? <p className="ok">{tb}</p> : (
        <form className="form" onSubmit={gui}>
          <label>Email đã đăng ký<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>
          {loi && <p className="loi">{loi}</p>}
          <button className="btn full">Gửi liên kết đặt lại</button>
        </form>
      )}
    </Khung>
  )
}

export function DatLaiMatKhau() {
  const [params] = useSearchParams()
  const [mk, setMk] = useState('')
  const [xong, setXong] = useState(false)
  const [loi, setLoi] = useState('')
  const gui = async (e) => {
    e.preventDefault(); setLoi('')
    try { await api.post('/api/auth/reset-password', { token: params.get('token'), matKhauMoi: mk }); setXong(true) } catch (err) { setLoi(err.message) }
  }
  return (
    <Khung tieuDe="Đặt lại mật khẩu">
      {xong ? <p className="ok">Đã đổi mật khẩu. <Link to="/dang-nhap">Đăng nhập</Link></p> : (
        <form className="form" onSubmit={gui}>
          <label>Mật khẩu mới<input type="password" required minLength={8} value={mk} onChange={(e) => setMk(e.target.value)} autoComplete="new-password" /></label>
          {loi && <p className="loi">{loi}</p>}
          <button className="btn full">Lưu mật khẩu</button>
        </form>
      )}
    </Khung>
  )
}
