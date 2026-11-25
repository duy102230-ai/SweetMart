export const tien = (v) => (Number(v) || 0).toLocaleString('vi-VN') + ' ₫'

export const ngay = (s) => (s ? new Date(s).toLocaleDateString('vi-VN') : '')
export const ngayGio = (s) => (s ? new Date(s.endsWith?.('Z') ? s : s + 'Z').toLocaleString('vi-VN') : '')

export const TRANG_THAI_DON = {
  ChoThanhToan: { ten: 'Chờ thanh toán', mau: 'xam' },
  ChoXacNhan: { ten: 'Chờ xác nhận', mau: 'vang' },
  DaXacNhan: { ten: 'Đã xác nhận', mau: 'xanh' },
  DangDongGoi: { ten: 'Đang đóng gói', mau: 'xanh' },
  DangGiao: { ten: 'Đang giao', mau: 'tim' },
  DaGiao: { ten: 'Đã giao', mau: 'luc' },
  GiaoThatBai: { ten: 'Giao thất bại', mau: 'do' },
  DaHuy: { ten: 'Đã hủy', mau: 'do' },
}

export const TRANG_THAI_TT = {
  ChuaThu: 'Chưa thu (COD)', ChoThanhToan: 'Chờ thanh toán', DaThanhToan: 'Đã thanh toán', ThatBai: 'Thất bại',
  ChoHoanTien: 'Chờ hoàn tiền', DaThuCOD: 'Đã thu COD', KhongThuDuoc: 'Không thu được',
}

// Bám theo OrderStateMachine ở Backend (trừ DangGiao do thao tác "Tạo vận đơn GHN" đảm nhận)
export const TIEP_THEO = {
  ChoXacNhan: ['DaXacNhan'],
  DaXacNhan: ['DangDongGoi'],
  DangGiao: ['DaGiao', 'GiaoThatBai'],
}

export const VAI_TRO = { KhachHang: 'Khách hàng', NhanVien: 'Nhân viên', QuanLy: 'Quản lý', QuanTri: 'Quản trị' }

export function Badge({ trangThai }) {
  const t = TRANG_THAI_DON[trangThai] || { ten: trangThai, mau: 'xam' }
  return <span className={'badge ' + t.mau}>{t.ten}</span>
}
