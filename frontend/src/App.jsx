import { Route, Routes } from 'react-router-dom'
import { YeuCau } from './auth'
import Layout from './components/Layout'
import TrangChu from './pages/TrangChu'
import ChiTietSanPham from './pages/ChiTietSanPham'
import GioHang from './pages/GioHang'
import ThanhToan from './pages/ThanhToan'
import KetQuaThanhToan from './pages/KetQuaThanhToan'
import DonCuaToi from './pages/DonCuaToi'
import ChiTietDon from './pages/ChiTietDon'
import { DangNhap, DangKy, QuenMatKhau, DatLaiMatKhau } from './pages/TaiKhoan'
import AdminLayout from './pages/admin/AdminLayout'
import AdminDonHang from './pages/admin/AdminDonHang'
import AdminKho from './pages/admin/AdminKho'
import AdminSanPham from './pages/admin/AdminSanPham'
import AdminKhuyenMai from './pages/admin/AdminKhuyenMai'
import AdminBaoCao from './pages/admin/AdminBaoCao'
import AdminNguoiDung from './pages/admin/AdminNguoiDung'

const KH = ['KhachHang']

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<TrangChu />} />
        <Route path="san-pham/:id" element={<ChiTietSanPham />} />
        <Route path="dang-nhap" element={<DangNhap />} />
        <Route path="dang-ky" element={<DangKy />} />
        <Route path="quen-mat-khau" element={<QuenMatKhau />} />
        <Route path="dat-lai-mat-khau" element={<DatLaiMatKhau />} />
        <Route path="gio-hang" element={<YeuCau vaiTro={KH}><GioHang /></YeuCau>} />
        <Route path="thanh-toan" element={<YeuCau vaiTro={KH}><ThanhToan /></YeuCau>} />
        <Route path="thanh-toan/ket-qua" element={<KetQuaThanhToan />} />
        <Route path="don-hang" element={<YeuCau vaiTro={KH}><DonCuaToi /></YeuCau>} />
        <Route path="don-hang/:id" element={<YeuCau vaiTro={KH}><ChiTietDon /></YeuCau>} />
        <Route path="quan-tri" element={<YeuCau vaiTro={['NhanVien', 'QuanLy', 'QuanTri']}><AdminLayout /></YeuCau>}>
          <Route index element={<AdminDonHang />} />
          <Route path="don-hang" element={<AdminDonHang />} />
          <Route path="kho" element={<AdminKho />} />
          <Route path="san-pham" element={<AdminSanPham />} />
          <Route path="khuyen-mai" element={<AdminKhuyenMai />} />
          <Route path="bao-cao" element={<AdminBaoCao />} />
          <Route path="nguoi-dung" element={<AdminNguoiDung />} />
        </Route>
        <Route path="*" element={<div className="container"><h2>Không tìm thấy trang</h2></div>} />
      </Route>
    </Routes>
  )
}
