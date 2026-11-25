import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import { tien } from '../format'

const DIA_CHI_TRONG = { nguoiNhan: '', soDienThoai: '', diaChiChiTiet: '', maQuanHuyenGHN: 1588, maPhuongXaGHN: '30210', macDinh: false }

export default function ThanhToan() {
  const { taiGio } = useAuth()
  const nav = useNavigate()
  const [gio, setGio] = useState([])
  const [diaChi, setDiaChi] = useState([])
  const [maDC, setMaDC] = useState(null)
  const [form, setForm] = useState(null)
  const [maCode, setMaCode] = useState('')
  const [maDaApDung, setMaDaApDung] = useState('')
  const [phi, setPhi] = useState(null)
  const [pttt, setPttt] = useState('COD')
  const [ghiChu, setGhiChu] = useState('')
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)

  const taiDiaChi = useCallback(async () => {
    const ds = await api.get('/api/addresses')
    setDiaChi(ds)
    setMaDC((cu) => cu ?? ds[0]?.maDC ?? null)
    if (ds.length === 0) setForm({ ...DIA_CHI_TRONG, macDinh: true })
  }, [])

  useEffect(() => {
    api.get('/api/cart').then(setGio).catch((e) => setLoi(e.message))
    taiDiaChi().catch((e) => setLoi(e.message))
  }, [taiDiaChi])

  // Tính tạm tiền hàng, giảm giá, phí ship GHN mỗi khi đổi địa chỉ hoặc mã giảm giá
  useEffect(() => {
    if (!maDC) return
    setLoi('')
    api.post('/api/orders/preview', { maDC, maCode: maDaApDung || null })
      .then((r) => { setPhi(r); if (!r.choPhepCOD) setPttt('VNPAY') })
      .catch((e) => { setLoi(e.message); if (maDaApDung) setMaDaApDung('') })
  }, [maDC, maDaApDung])

  const luuDiaChi = async (e) => {
    e.preventDefault()
    try {
      const dc = await api.post('/api/addresses', { ...form, maQuanHuyenGHN: Number(form.maQuanHuyenGHN) })
      setForm(null); await taiDiaChi(); setMaDC(dc.maDC)
    } catch (err) { setLoi(err.message) }
  }

  const datHang = async () => {
    setDangGui(true); setLoi('')
    try {
      const r = await api.post('/api/orders', { maDC, phuongThucTT: pttt, maCode: maDaApDung || null, ghiChu: ghiChu || null })
      await taiGio()
      if (r.paymentUrl) window.location.href = r.paymentUrl     // chuyển sang cổng VNPay
      else nav('/don-hang/' + r.maDH + '?moi=1')
    } catch (e) { setLoi(e.message); setDangGui(false) }
  }

  const doiForm = (k) => (e) => setForm({ ...form, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value })

  return (
    <div className="container">
      <h2>Đặt hàng</h2>
      <div className="two-col">
        <div>
          <section className="panel">
            <h3>1. Địa chỉ nhận hàng</h3>
            {diaChi.map((d) => (
              <label key={d.maDC} className={'addr' + (maDC === d.maDC ? ' active' : '')}>
                <input type="radio" checked={maDC === d.maDC} onChange={() => setMaDC(d.maDC)} />
                <div><b>{d.nguoiNhan}</b> · {d.soDienThoai} {d.macDinh && <span className="badge xanh">Mặc định</span>}<div className="muted">{d.diaChiChiTiet}</div></div>
              </label>
            ))}
            {form ? (
              <form className="form" onSubmit={luuDiaChi}>
                <div className="row2">
                  <label>Người nhận<input required value={form.nguoiNhan} onChange={doiForm('nguoiNhan')} /></label>
                  <label>Số điện thoại<input required pattern="0\d{9,10}" value={form.soDienThoai} onChange={doiForm('soDienThoai')} /></label>
                </div>
                <label>Địa chỉ chi tiết<input required value={form.diaChiChiTiet} onChange={doiForm('diaChiChiTiet')} placeholder="Số nhà, đường, phường/xã, quận/huyện, tỉnh" /></label>
                <div className="row2">
                  <label>Mã quận/huyện (GHN)<input required type="number" value={form.maQuanHuyenGHN} onChange={doiForm('maQuanHuyenGHN')} /></label>
                  <label>Mã phường/xã (GHN)<input required value={form.maPhuongXaGHN} onChange={doiForm('maPhuongXaGHN')} /></label>
                </div>
                <label className="check"><input type="checkbox" checked={form.macDinh} onChange={doiForm('macDinh')} /> Đặt làm địa chỉ mặc định</label>
                <div className="actions">
                  <button className="btn">Lưu địa chỉ</button>
                  {diaChi.length > 0 && <button type="button" className="btn outline" onClick={() => setForm(null)}>Hủy</button>}
                </div>
              </form>
            ) : <button className="link" onClick={() => setForm(DIA_CHI_TRONG)}>+ Thêm địa chỉ mới</button>}
          </section>

          <section className="panel">
            <h3>2. Phương thức thanh toán</h3>
            <label className="addr">
              <input type="radio" checked={pttt === 'COD'} disabled={phi && !phi.choPhepCOD} onChange={() => setPttt('COD')} />
              <div><b>Thanh toán khi nhận hàng (COD)</b>{phi && !phi.choPhepCOD && <div className="loi small">Đơn trên 2.000.000 ₫ không hỗ trợ COD</div>}</div>
            </label>
            <label className="addr">
              <input type="radio" checked={pttt === 'VNPAY'} onChange={() => setPttt('VNPAY')} />
              <div><b>Thanh toán online qua VNPay</b><div className="muted small">ATM nội địa, thẻ quốc tế, QR. Đơn sẽ tự hủy nếu không thanh toán trong 15 phút.</div></div>
            </label>
            <label>Ghi chú cho cửa hàng<textarea rows={2} maxLength={500} value={ghiChu} onChange={(e) => setGhiChu(e.target.value)} /></label>
          </section>
        </div>

        <aside className="summary">
          <h3>Đơn hàng ({gio.length} sản phẩm)</h3>
          {gio.map((i) => <div className="line small" key={i.maSP}><span>{i.tenSP} × {i.soLuong}</span><span>{tien(i.thanhTien)}</span></div>)}
          <div className="voucher">
            <input value={maCode} onChange={(e) => setMaCode(e.target.value.toUpperCase())} placeholder="Mã giảm giá" />
            <button className="btn outline" onClick={() => setMaDaApDung(maCode.trim())} disabled={!maCode.trim() || !maDC}>Áp dụng</button>
          </div>
          {maDaApDung && phi && <p className="ok small">Đã áp dụng mã {maDaApDung} <button className="link" onClick={() => { setMaDaApDung(''); setMaCode('') }}>Bỏ</button></p>}
          {phi && <>
            <div className="line"><span>Tiền hàng</span><span>{tien(phi.tongTienHang)}</span></div>
            <div className="line"><span>Giảm giá</span><span>− {tien(phi.tienGiam)}</span></div>
            <div className="line"><span>Phí vận chuyển (GHN)</span><span>{phi.phiVanChuyen === 0 ? 'Miễn phí' : tien(phi.phiVanChuyen)}</span></div>
            <div className="line total"><span>Tổng thanh toán</span><b>{tien(phi.tongThanhToan)}</b></div>
          </>}
          {loi && <p className="loi">{loi}</p>}
          <button className="btn full" disabled={!maDC || !phi || gio.length === 0 || dangGui} onClick={datHang}>
            {dangGui ? 'Đang xử lý…' : pttt === 'VNPAY' ? 'Thanh toán qua VNPay' : 'Đặt hàng'}
          </button>
        </aside>
      </div>
    </div>
  )
}
