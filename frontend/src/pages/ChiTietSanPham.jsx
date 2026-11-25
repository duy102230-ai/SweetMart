import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import { ngay, tien } from '../format'

export default function ChiTietSanPham() {
  const { id } = useParams()
  const { user, taiGio } = useAuth()
  const nav = useNavigate()
  const [sp, setSp] = useState(null)
  const [danhGia, setDanhGia] = useState([])
  const [anh, setAnh] = useState(0)
  const [sl, setSl] = useState(1)
  const [tb, setTb] = useState({ loai: '', text: '' })

  useEffect(() => {
    api.get('/api/products/' + id).then(setSp).catch((e) => setTb({ loai: 'loi', text: e.message }))
    api.get(`/api/products/${id}/reviews`).then(setDanhGia).catch(() => {})
  }, [id])

  const themVaoGio = async (muaNgay) => {
    if (!user) { nav('/dang-nhap?next=/san-pham/' + id); return }
    if (user.vaiTro !== 'KhachHang') { setTb({ loai: 'loi', text: 'Chỉ tài khoản khách hàng mới mua hàng được.' }); return }
    try {
      // API giỏ hàng nhận tổng số lượng → cộng thêm vào số lượng đang có
      const gio = await api.get('/api/cart')
      const dangCo = gio.find((g) => g.maSP === sp.maSP)?.soLuong || 0
      await api.put('/api/cart/items', { maSP: sp.maSP, soLuong: dangCo + sl })
      await taiGio()
      if (muaNgay) nav('/gio-hang')
      else setTb({ loai: 'ok', text: `Đã thêm ${sl} sản phẩm vào giỏ.` })
    } catch (e) { setTb({ loai: 'loi', text: e.message }) }
  }

  if (!sp) return <div className="container">{tb.text ? <p className="loi">{tb.text}</p> : 'Đang tải…'}</div>
  const het = sp.tonKhaDung === 0

  return (
    <div className="container">
      <p className="breadcrumb"><Link to="/">Trang chủ</Link> / <Link to={'/?categoryId=' + sp.maDM}>{sp.tenDanhMuc}</Link> / {sp.tenSP}</p>
      <div className="detail">
        <div className="gallery">
          <img src={sp.hinhAnh[anh]} alt={sp.tenSP} />
          {sp.hinhAnh.length > 1 && <div className="thumbs">{sp.hinhAnh.map((h, i) => <img key={i} src={h} alt="" onClick={() => setAnh(i)} className={i === anh ? 'active' : ''} />)}</div>}
        </div>
        <div className="info">
          <h1>{sp.tenSP}</h1>
          <p className="muted">Thương hiệu: <b>{sp.thuongHieu}</b> · Khối lượng: {sp.khoiLuongGram} g</p>
          {sp.soDanhGia > 0 && <p>⭐ {sp.diemTrungBinh.toFixed(1)} / 5 ({sp.soDanhGia} đánh giá)</p>}
          <p className="price big">{tien(sp.giaBan)} <small>/ {sp.donViTinh}</small></p>
          <div className="box">
            <div>Tình trạng: {het ? <b className="do-text">Hết hàng</b> : <b>Còn {sp.tonKhaDung} {sp.donViTinh}</b>}</div>
            {sp.hanSuDungGanNhat && <div>Hạn sử dụng (lô xuất trước): <b>{ngay(sp.hanSuDungGanNhat)}</b></div>}
          </div>
          {!het && (
            <div className="buy">
              <div className="qty">
                <button onClick={() => setSl(Math.max(1, sl - 1))}>−</button>
                <input type="number" value={sl} min={1} max={sp.tonKhaDung} onChange={(e) => setSl(Math.min(sp.tonKhaDung, Math.max(1, Number(e.target.value) || 1)))} />
                <button onClick={() => setSl(Math.min(sp.tonKhaDung, sl + 1))}>+</button>
              </div>
              <button className="btn outline" onClick={() => themVaoGio(false)}>Thêm vào giỏ</button>
              <button className="btn" onClick={() => themVaoGio(true)}>Mua ngay</button>
            </div>
          )}
          {tb.text && <p className={tb.loai}>{tb.text}</p>}
          <h3>Mô tả</h3>
          <p>{sp.moTa}</p>
        </div>
      </div>
      <section className="reviews">
        <h3>Đánh giá của khách hàng</h3>
        {danhGia.length === 0 && <p className="muted">Chưa có đánh giá.</p>}
        {danhGia.map((d, i) => (
          <div key={i} className="review">
            <b>{d.hoTen}</b> <span className="stars">{'★'.repeat(d.soSao)}{'☆'.repeat(5 - d.soSao)}</span> <span className="muted small">{ngay(d.ngayDanhGia)}</span>
            <div>{d.noiDung}</div>
          </div>
        ))}
      </section>
    </div>
  )
}
