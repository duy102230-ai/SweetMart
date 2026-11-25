// Lớp gọi REST API của SweetMart. Token JWT lưu ở localStorage, gửi kèm header Authorization.
const BASE = import.meta.env.VITE_API_URL || ''
const TOKEN_KEY = 'sm_auth'

export function layPhien() {
  try { return JSON.parse(localStorage.getItem(TOKEN_KEY)) } catch { return null }
}
export function luuPhien(p) {
  if (p) localStorage.setItem(TOKEN_KEY, JSON.stringify(p))
  else localStorage.removeItem(TOKEN_KEY)
}

export class ApiError extends Error {
  constructor(status, code, message) { super(message); this.status = status; this.code = code }
}

async function request(method, path, body) {
  const headers = { 'Content-Type': 'application/json' }
  const phien = layPhien()
  if (phien?.token) headers.Authorization = 'Bearer ' + phien.token
  const res = await fetch(BASE + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) })
  const text = await res.text()
  let data = null
  try { data = text ? JSON.parse(text) : null } catch { data = text }
  if (!res.ok) {
    if (res.status === 401 && phien) { luuPhien(null); window.dispatchEvent(new Event('sm-logout')) }
    // Lỗi nghiệp vụ: {code, message}; lỗi validate của ASP.NET: {errors: {...}}
    let msg = data?.message
    if (!msg && data?.errors) msg = Object.values(data.errors).flat().join(' ')
    if (!msg) msg = res.status === 403 ? 'Bạn không có quyền thực hiện thao tác này.'
      : res.status === 401 ? 'Vui lòng đăng nhập.' : `Lỗi ${res.status}`
    throw new ApiError(res.status, data?.code, msg)
  }
  return data
}

export const api = {
  get: (p) => request('GET', p),
  post: (p, b) => request('POST', p, b ?? {}),
  put: (p, b) => request('PUT', p, b ?? {}),
  del: (p) => request('DELETE', p),
}

export const qs = (obj) => {
  const s = new URLSearchParams()
  Object.entries(obj).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') s.set(k, v) })
  const t = s.toString()
  return t ? '?' + t : ''
}
