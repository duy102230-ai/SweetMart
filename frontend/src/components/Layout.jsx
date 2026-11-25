import { useState } from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { laNoiBo, useAuth } from '../auth'
import { VAI_TRO } from '../format'

export default function Layout() {
  const { user, dangXuat, soLuongGio } = useAuth()
  const [tuKhoa, setTuKhoa] = useState('')
  const nav = useNavigate()

  const timKiem = (e) => {
    e.preventDefault()
    nav('/?keyword=' + encodeURIComponent(tuKhoa.trim()))
  }

  return (
    <>
      <header className="header">
        <div className="container header-in">
          <Link to="/" className="logo">🍬 SweetMart</Link>
          <form className="search" onSubmit={timKiem}>
            <input value={tuKhoa} onChange={(e) => setTuKhoa(e.target.value)} placeholder="Tìm bánh, kẹo, socola… (gõ không dấu cũng được)" />
            <button>Tìm</button>
          </form>
          <nav className="menu">
            {user?.vaiTro === 'KhachHang' && <>
              <NavLink to="/don-hang">Đơn của tôi</NavLink>
              <NavLink to="/gio-hang" className="cart">Giỏ hàng {soLuongGio > 0 && <span className="cart-n">{soLuongGio}</span>}</NavLink>
            </>}
            {laNoiBo(user) && <NavLink to="/quan-tri">Quản trị</NavLink>}
            {user ? <>
              <span className="hello" title={user.email}>{user.hoTen} <small>({VAI_TRO[user.vaiTro]})</small></span>
              <button className="link" onClick={() => { dangXuat(); nav('/') }}>Đăng xuất</button>
            </> : <>
              <NavLink to="/dang-nhap">Đăng nhập</NavLink>
              <NavLink to="/dang-ky" className="btn-sm">Đăng ký</NavLink>
            </>}
          </nav>
        </div>
      </header>
      <main><Outlet /></main>
      <footer className="footer">
        <div className="container">
          SweetMart – Đồ án Tích hợp hệ thống · Thanh toán VNPay · Giao hàng GHN · Miễn phí ship đơn từ 300.000 ₫
        </div>
      </footer>
    </>
  )
}
