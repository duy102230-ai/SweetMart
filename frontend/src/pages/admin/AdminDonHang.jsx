import { useCallback, useEffect, useState } from 'react'
import { api, qs } from '../../api'
import DonHangChiTiet from '../../components/DonHangChiTiet'
import { Badge, TIEP_THEO, TRANG_THAI_DON, TRANG_THAI_TT, ngayGio, tien } from '../../format'
import { ChiCho } from './AdminLayout'

function DanhSach() {
  const [status, setStatus] = useState('ChoXacNhan')
  const [keyword, setKeyword] = useState('')
  const [page, setPage] = useState(1)
  const [kq, setKq] = useState(null)
  const [chon, setChon] = useState(null)
  const [loi, setLoi] = useState('')
  const [tb, setTb] = useState('')

  const tai = useCallback(() => {
    api.get('/api/admin/orders' + qs({ status, keyword, page })).then(setKq).catch((e) => setLoi(e.message))
  }, [status, keyword, page])
  useEffect(() => { tai() }, [tai])

  const moDon = async (maDH) => {
    setLoi(''); setTb('')
    try { setChon(await api.get('/api/admin/orders/' + maDH)) } catch (e) { setLoi(e.message) }
  }

  const thucHien = async (fn, thongBao) => {
    setLoi(''); setTb('')
    try { await fn(); await moDon(chon.maDH); setTb(thongBao); tai() } catch (e) { setLoi(e.message) }
  }

  const chuyen = (moi) => thucHien(() => api.put(`/api/admin/orders/${chon.maDH}/status`, { trangThaiMoi: moi }), 'Đã chuyển sang “' + TRANG_THAI_DON[moi].ten + '”.')
  const taoVanDon = () => thucHien(() => api.post(`/api/admin/orders/${chon.maDH}/shipment`), 'Đã tạo vận đơn GHN.')
  const huy = () => {
    const lyDo = window.prompt('Lý do hủy đơn?')
    if (lyDo) thucHien(() => api.put(`/api/admin/orders/${chon.maDH}/cancel`, { lyDo }), 'Đã hủy đơn, tồn kho đã được hoàn lại.')
  }

  if (chon) {
    const coTheHuy = ['ChoThanhToan', 'ChoXacNhan', 'DaXacNhan', 'GiaoThatBai'].includes(chon.trangThai)
    return (
      <div>
        <button className="link" onClick={() => { setChon(null); setTb('') }}>← Danh sách đơn</button>
        {tb && <p className="ok">{tb}</p>}
        {loi && <p className="loi">{loi}</p>}
        <div className="actions bar">
          {(TIEP_THEO[chon.trangThai] || []).map((t) => <button key={t} className="btn" onClick={() => chuyen(t)}>→ {TRANG_THAI_DON[t].ten}</button>)}
          {chon.trangThai === 'DangDongGoi' && <button className="btn" onClick={taoVanDon}>Tạo vận đơn GHN</button>}
          {coTheHuy && <button className="btn danger" onClick={huy}>Hủy đơn</button>}
        </div>
        <DonHangChiTiet don={chon} />
      </div>
    )
  }

  const soTrang = kq ? Math.ceil(kq.total / 20) : 0
  return (
    <div>
      <h2>Quản lý đơn hàng</h2>
      <div className="tabs">
        <button className={!status ? 'active' : ''} onClick={() => { setStatus(''); setPage(1) }}>Tất cả</button>
        {Object.entries(TRANG_THAI_DON).map(([k, v]) => (
          <button key={k} className={status === k ? 'active' : ''} onClick={() => { setStatus(k); setPage(1) }}>
            {v.ten} {kq?.demTheoTrangThai?.[k] ? <span className="cnt">{kq.demTheoTrangThai[k]}</span> : null}
          </button>
        ))}
      </div>
      <form className="toolbar" onSubmit={(e) => { e.preventDefault(); setKeyword(e.target.k.value); setPage(1) }}>
        <input name="k" placeholder="Mã đơn (SM000001), SĐT hoặc tên người nhận" defaultValue={keyword} />
        <button className="btn outline">Tìm</button>
      </form>
      {loi && <p className="loi">{loi}</p>}
      <table className="table">
        <thead><tr><th>Mã đơn</th><th>Ngày đặt</th><th>Người nhận</th><th>Tổng tiền</th><th>Thanh toán</th><th>Trạng thái</th></tr></thead>
        <tbody>
          {kq?.items.map((d) => (
            <tr key={d.maDH} className="click" onClick={() => moDon(d.maDH)}>
              <td><b>SM{String(d.maDH).padStart(6, '0')}</b></td>
              <td>{ngayGio(d.ngayDat)}</td>
              <td>{d.nguoiNhan}<div className="muted small">{d.soDienThoaiNhan}</div></td>
              <td>{tien(d.tongThanhToan)}</td>
              <td>{d.phuongThucTT}<div className="muted small">{TRANG_THAI_TT[d.trangThaiThanhToan]}</div></td>
              <td><Badge trangThai={d.trangThai} /></td>
            </tr>
          ))}
          {kq && kq.items.length === 0 && <tr><td colSpan={6} className="muted">Không có đơn hàng.</td></tr>}
        </tbody>
      </table>
      {soTrang > 1 && <div className="pager">{Array.from({ length: soTrang }, (_, i) => i + 1).map((n) => <button key={n} className={n === page ? 'active' : ''} onClick={() => setPage(n)}>{n}</button>)}</div>}
    </div>
  )
}

export default function AdminDonHang() {
  return <ChiCho vaiTro={['NhanVien', 'QuanLy']}><DanhSach /></ChiCho>
}
