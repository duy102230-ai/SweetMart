import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { api, layPhien, luuPhien } from './api'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(layPhien)
  const [soLuongGio, setSoLuongGio] = useState(0)

  const dangXuat = useCallback(() => { luuPhien(null); setUser(null); setSoLuongGio(0) }, [])

  useEffect(() => {
    const h = () => setUser(null)
    window.addEventListener('sm-logout', h)
    return () => window.removeEventListener('sm-logout', h)
  }, [])

  const taiGio = useCallback(async () => {
    if (layPhien()?.vaiTro !== 'KhachHang') { setSoLuongGio(0); return }
    try { const g = await api.get('/api/cart'); setSoLuongGio(g.reduce((s, i) => s + i.soLuong, 0)) } catch { /* bỏ qua */ }
  }, [])

  useEffect(() => { taiGio() }, [user, taiGio])

  const dangNhap = async (email, matKhau) => {
    const r = await api.post('/api/auth/login', { email, matKhau })
    luuPhien(r); setUser(r); return r
  }
  const dangKy = async (body) => {
    const r = await api.post('/api/auth/register', body)
    luuPhien(r); setUser(r); return r
  }

  return <AuthCtx.Provider value={{ user, dangNhap, dangKy, dangXuat, soLuongGio, taiGio }}>{children}</AuthCtx.Provider>
}

export const useAuth = () => useContext(AuthCtx)

export const laNoiBo = (u) => ['NhanVien', 'QuanLy', 'QuanTri'].includes(u?.vaiTro)

/** Chặn trang theo vai trò; chưa đăng nhập thì chuyển về trang đăng nhập. */
export function YeuCau({ vaiTro, children }) {
  const { user } = useAuth()
  const loc = useLocation()
  if (!user) return <Navigate to={'/dang-nhap?next=' + encodeURIComponent(loc.pathname + loc.search)} replace />
  if (vaiTro && !vaiTro.includes(user.vaiTro)) return <div className="container"><p className="loi">Bạn không có quyền truy cập trang này.</p></div>
  return children
}
