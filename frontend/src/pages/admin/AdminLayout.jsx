import { NavLink, Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../auth'

// Menu theo vai trò – khớp với [Authorize(Roles=...)] ở Backend
export const MENU = [
  { to: 'don-hang', ten: 'Đơn hàng', vaiTro: ['NhanVien', 'QuanLy'] },
  { to: 'kho', ten: 'Kho & lô hàng', vaiTro: ['NhanVien', 'QuanLy'] },
  { to: 'san-pham', ten: 'Sản phẩm', vaiTro: ['QuanLy'] },
  { to: 'khuyen-mai', ten: 'Mã giảm giá', vaiTro: ['QuanLy'] },
  { to: 'bao-cao', ten: 'Báo cáo doanh thu', vaiTro: ['QuanLy'] },
  { to: 'nguoi-dung', ten: 'Người dùng', vaiTro: ['QuanTri'] },
]

export default function AdminLayout() {
  const { user } = useAuth()
  const loc = useLocation()
  const menu = MENU.filter((m) => m.vaiTro.includes(user.vaiTro))
  if (loc.pathname.replace(/\/$/, '') === '/quan-tri' && menu[0] && menu[0].to !== 'don-hang')
    return <Navigate to={'/quan-tri/' + menu[0].to} replace />
  return (
    <div className="container admin">
      <aside className="admin-nav">
        <h3>Quản trị</h3>
        {menu.map((m) => <NavLink key={m.to} to={'/quan-tri/' + m.to}>{m.ten}</NavLink>)}
      </aside>
      <section className="grow"><Outlet /></section>
    </div>
  )
}

export function ChiCho({ vaiTro, children }) {
  const { user } = useAuth()
  if (!vaiTro.includes(user?.vaiTro)) return <p className="loi">Vai trò của bạn không được dùng chức năng này.</p>
  return children
}
