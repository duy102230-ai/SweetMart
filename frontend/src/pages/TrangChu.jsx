import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, qs } from '../api'
import { tien } from '../format'

export default function TrangChu() {
  const [params, setParams] = useSearchParams()
  const [danhMuc, setDanhMuc] = useState([])
  const [kq, setKq] = useState(null)
  const [loi, setLoi] = useState('')

  const keyword = params.get('keyword') || ''
  const categoryId = params.get('categoryId') || ''
  const sort = params.get('sort') || ''
  const minPrice = params.get('minPrice') || ''
  const maxPrice = params.get('maxPrice') || ''
  const page = Number(params.get('page') || 1)

  useEffect(() => { api.get('/api/categories').then(setDanhMuc).catch(() => {}) }, [])

  useEffect(() => {
    setLoi('')
    api.get('/api/products' + qs({ keyword, categoryId, sort, minPrice, maxPrice, page, pageSize: 12 }))
      .then(setKq).catch((e) => setLoi(e.message))
  }, [keyword, categoryId, sort, minPrice, maxPrice, page])

  const dat = (k, v) => {
    const p = new URLSearchParams(params)
    if (v) p.set(k, v); else p.delete(k)
    if (k !== 'page') p.delete('page')
    setParams(p)
  }

  const soTrang = kq ? Math.ceil(kq.total / kq.pageSize) : 0

  return (
    <div className="container">
      {!keyword && !categoryId && (
        <section className="hero">
          <div>
            <h1>Bánh kẹo chính hãng, hạn dùng rõ ràng</h1>
            <p>Hiển thị hạn sử dụng từng lô · Thanh toán VNPay hoặc COD · Giao nhanh qua GHN</p>
          </div>
        </section>
      )}
      <div className="shop">
        <aside className="filters">
          <h3>Danh mục</h3>
          <ul className="cat-list">
            <li><button className={!categoryId ? 'active' : ''} onClick={() => dat('categoryId', '')}>Tất cả</button></li>
            {danhMuc.filter((d) => !d.maDMCha).map((d) => (
              <li key={d.maDM}><button className={categoryId === String(d.maDM) ? 'active' : ''} onClick={() => dat('categoryId', d.maDM)}>{d.tenDanhMuc}</button></li>
            ))}
          </ul>
          <h3>Khoảng giá</h3>
          <div className="price-range">
            <input type="number" placeholder="Từ" defaultValue={minPrice} onBlur={(e) => dat('minPrice', e.target.value)} />
            <input type="number" placeholder="Đến" defaultValue={maxPrice} onBlur={(e) => dat('maxPrice', e.target.value)} />
          </div>
        </aside>
        <section className="grow">
          <div className="toolbar">
            <span>{keyword ? <>Kết quả cho “<b>{keyword}</b>”: </> : null}{kq ? `${kq.total} sản phẩm` : 'Đang tải…'}</span>
            <select value={sort} onChange={(e) => dat('sort', e.target.value)}>
              <option value="">Mới nhất</option>
              <option value="bestseller">Bán chạy</option>
              <option value="price_asc">Giá tăng dần</option>
              <option value="price_desc">Giá giảm dần</option>
            </select>
          </div>
          {loi && <p className="loi">{loi}</p>}
          {kq && kq.items.length === 0 && <p className="muted">Không tìm thấy sản phẩm phù hợp.</p>}
          <div className="grid">
            {kq?.items.map((p) => (
              <Link to={'/san-pham/' + p.maSP} key={p.maSP} className="card">
                <img src={p.hinhAnh} alt={p.tenSP} loading="lazy" />
                <div className="card-body">
                  <div className="muted small">{p.thuongHieu} · {p.tenDanhMuc}</div>
                  <div className="card-title">{p.tenSP}</div>
                  <div className="price">{tien(p.giaBan)} <small>/ {p.donViTinh}</small></div>
                  {p.tonKhaDung === 0 ? <span className="badge do">Hết hàng</span>
                    : p.tonKhaDung < 10 ? <span className="badge vang">Còn {p.tonKhaDung}</span> : null}
                </div>
              </Link>
            ))}
          </div>
          {soTrang > 1 && (
            <div className="pager">
              {Array.from({ length: soTrang }, (_, i) => i + 1).map((n) => (
                <button key={n} className={n === page ? 'active' : ''} onClick={() => dat('page', n)}>{n}</button>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
