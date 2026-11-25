import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from './auth'
import App from './App'
import './index.css'

// Ảnh sản phẩm lỗi (mất mạng, link hỏng) → thay bằng ảnh nền hồng có chữ SweetMart
const ANH_DU_PHONG = 'data:image/svg+xml,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600"><rect width="600" height="600" fill="#FCE8EF"/>' +
  '<text x="300" y="320" font-size="56" text-anchor="middle" fill="#E85D8A" font-family="Arial">SweetMart</text></svg>')
document.addEventListener('error', (e) => {
  const el = e.target
  if (el.tagName === 'IMG' && el.src !== ANH_DU_PHONG) el.src = ANH_DU_PHONG
}, true)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
