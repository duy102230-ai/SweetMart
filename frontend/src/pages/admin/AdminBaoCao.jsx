import { useEffect, useState } from 'react'
import { api, qs } from '../../api'
import { TRANG_THAI_DON, tien } from '../../format'
import { ChiCho } from './AdminLayout'

const iso = (d) => d.toISOString().slice(0, 10)

/** Biểu đồ cột doanh thu theo ngày, vẽ bằng SVG (không cần thư viện ngoài). */
function BieuDo({ duLieu }) {
  const W = 720, H = 220, P = 30
  const max = Math.max(1, ...duLieu.map((d) => d.doanhThu))
  const bw = (W - P * 2) / Math.max(1, duLieu.length)
  return (
    <svg viewBox={`0 0 ${W} ${H + 24}`} className="chart" role="img" aria-label="Doanh thu theo ngày">
      <line x1={P} y1={H} x2={W - P} y2={H} stroke="currentColor" opacity=".25" />
      {duLieu.map((d, i) => {
        const h = (d.doanhThu / max) * (H - 20)
        const w = Math.min(bw * 0.7, 36)
        return (
          <g key={d.ngay}>
            <rect x={P + i * bw + (bw - w) / 2} y={H - h} width={w} height={h} rx="2" className="bar"><title>{d.ngay}: {tien(d.doanhThu)} ({d.soDon} đơn)</title></rect>
            {(duLieu.length <= 15 || i % Math.ceil(duLieu.length / 10) === 0) &&
              <text x={P + i * bw + bw / 2} y={H + 16} textAnchor="middle" fontSize="10" fill="currentColor" opacity=".7">{d.ngay.slice(8, 10)}/{d.ngay.slice(5, 7)}</text>}
          </g>
        )
      })}
    </svg>
  )
}

function BaoCao() {
  const den = new Date()
  const [tu, setTu] = useState(iso(new Date(den.getTime() - 29 * 864e5)))
  const [denNgay, setDenNgay] = useState(iso(den))
  const [bc, setBc] = useState(null)
  const [loi, setLoi] = useState('')

  useEffect(() => {
    setLoi('')
    api.get('/api/admin/reports/revenue' + qs({ from: tu, to: denNgay })).then(setBc).catch((e) => setLoi(e.message))
  }, [tu, denNgay])

  return (
    <div>
      <h2>Báo cáo doanh thu</h2>
      <div className="toolbar">
        <span>Từ <input type="date" value={tu} onChange={(e) => setTu(e.target.value)} /> đến <input type="date" value={denNgay} onChange={(e) => setDenNgay(e.target.value)} /></span>
      </div>
      {loi && <p className="loi">{loi}</p>}
      {bc && <>
        <div className="stats">
          <div className="stat"><div className="muted">Doanh thu (đơn đã giao)</div><b>{tien(bc.tongDoanhThu)}</b></div>
          <div className="stat"><div className="muted">Số đơn đã giao</div><b>{bc.tongSoDon}</b></div>
          <div className="stat"><div className="muted">Giá trị TB/đơn</div><b>{tien(bc.tongSoDon ? Math.round(bc.tongDoanhThu / bc.tongSoDon) : 0)}</b></div>
        </div>
        <div className="panel"><h3>Doanh thu theo ngày</h3><BieuDo duLieu={bc.theoNgay} /></div>
        <div className="two-col">
          <div className="panel">
            <h3>Top sản phẩm bán chạy</h3>
            <table className="table"><thead><tr><th>Sản phẩm</th><th>SL bán</th><th>Doanh thu</th></tr></thead>
              <tbody>{bc.topSanPham.map((s) => <tr key={s.maSP}><td>{s.tenSP}</td><td>{s.soLuongBan}</td><td>{tien(s.doanhThu)}</td></tr>)}
                {bc.topSanPham.length === 0 && <tr><td colSpan={3} className="muted">Chưa có dữ liệu.</td></tr>}</tbody></table>
          </div>
          <div className="panel">
            <h3>Đơn theo trạng thái</h3>
            {Object.entries(bc.donTheoTrangThai).map(([k, v]) => <div key={k} className="line small"><span>{TRANG_THAI_DON[k]?.ten || k}</span><b>{v}</b></div>)}
          </div>
        </div>
      </>}
    </div>
  )
}

export default function AdminBaoCao() {
  return <ChiCho vaiTro={['QuanLy']}><BaoCao /></ChiCho>
}
