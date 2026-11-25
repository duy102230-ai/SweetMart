import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { api } from '../api'

/**
 * VNPay chuyển trình duyệt về đây (ReturnUrl). Trang chỉ HIỂN THỊ kết quả sau khi Backend kiểm tra chữ ký;
 * trạng thái đơn hàng chỉ được cập nhật qua IPN (máy chủ VNPay gọi máy chủ SweetMart).
 */
export default function KetQuaThanhToan() {
  const { search } = useLocation()
  const [kq, setKq] = useState(null)
  const [loi, setLoi] = useState('')

  useEffect(() => {
    api.get('/api/payments/vnpay/return' + search).then(setKq).catch((e) => setLoi(e.message))
  }, [search])

  if (loi) return <div className="container"><p className="loi">{loi}</p></div>
  if (!kq) return <div className="container">Đang kiểm tra kết quả thanh toán…</div>

  return (
    <div className="container center">
      {!kq.hopLe ? (
        <div className="result fail"><h2>⚠️ Dữ liệu trả về không hợp lệ</h2><p>Chữ ký không đúng. Vui lòng kiểm tra lại đơn hàng trong mục “Đơn của tôi”.</p></div>
      ) : kq.thanhCong ? (
        <div className="result ok"><h2>✅ Thanh toán thành công</h2><p>Đơn hàng <b>{kq.maHienThi}</b> đã được ghi nhận và đang chờ cửa hàng xác nhận.</p></div>
      ) : (
        <div className="result fail"><h2>❌ Thanh toán chưa thành công</h2><p>Đơn hàng <b>{kq.maHienThi}</b> chưa được thanh toán. Đơn sẽ tự hủy sau 15 phút nếu không thanh toán.</p></div>
      )}
      <p>{kq.maDH > 0 && <Link className="btn" to={'/don-hang/' + kq.maDH}>Xem đơn hàng</Link>} <Link className="btn outline" to="/">Về trang chủ</Link></p>
    </div>
  )
}
