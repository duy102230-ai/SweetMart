# SweetMart – Tiến độ dự án (cập nhật 25/11/2026, lần 2)

## Đã xong

### Tài liệu
- **`docs/SweetMart - Buoc 1-5.docx`** (68 trang, Times New Roman) – bản mới nhất, gồm Bước 1–5:
  - Bước 1–3 theo khung mẫu, **đã sửa**: thêm bảng `PhanBoLo`, bỏ `maLo` khỏi `ChiTietDonHang`, "15 thực thể";
    US15 – AC4 ghi đúng RspCode = 02; phân bổ Sprint mới ở mục Refinement.
  - Bước 4 – Lập kế hoạch: vai trò nhóm, sự kiện Scrum, Release Plan, ước lượng Story Point (101 SP), Sprint Goal từng Sprint,
    Sprint Backlog Sprint 1, DoR/DoD, Scrum board, Burndown, Velocity, ứng phó rủi ro.
  - Bước 5 – Lập trình: công nghệ, Git flow, cấu trúc mã, CSDL, API, FEFO, máy trạng thái, **tích hợp VNPay/GHN/Email** (trọng tâm),
    Frontend + 7 ảnh giao diện thật, unit test, CI, Docker.
  - File cũ `docs/SweetMart - Buoc 1-3 (theo mau).docx` giữ lại để đối chiếu.
- `docs/so-do/`: sơ đồ PNG + ảnh chụp giao diện `ui_*.jpg`.
- `docs/cong-cu-tai-lieu/`: script sinh tài liệu.
  - `python build2.py ../so-do "../SweetMart - Buoc 1-5.docx"` → xuất Word (Bước 4–5 nằm trong `buoc45.py`, được build2.py tự nạp).
  - `diagrams.py`, `diagrams2.py`, `diagrams3.py <thư mục ảnh>` → vẽ lại sơ đồ.

### Mã nguồn
- `backend/SweetMart.Api`: ASP.NET Core 9 + EF Core + SQL Server; VNPay, GHN, Email (có bản giả lập khi chưa có khóa).
  - Sửa 25/11: IPN trả đúng khóa `RspCode`/`Message` (trước đó bị đổi thành `rspCode` → VNPay sẽ không đọc được).
  - Sửa 25/11: DbSeeder từ chối tạo tài khoản mẫu nếu `Seed:DefaultPassword` rỗng.
- `backend/SweetMart.Tests`: 32 unit test – **đạt 32/32**.
- `docs/cong-cu-tai-lieu/smoke.py`: kiểm thử tích hợp đầu – cuối, **đạt 21/21**; mỗi lần chạy tự đăng ký khách mới nên chạy lại được nhiều lần.
- **`frontend/`** (React 19 + Vite): trang chủ (lọc, sắp xếp, tìm không dấu), chi tiết SP, giỏ hàng, đặt hàng (địa chỉ, phí GHN, mã giảm giá, COD/VNPay),
  kết quả VNPay, đơn của tôi (hủy, đánh giá), đăng nhập/đăng ký/quên mật khẩu; trang quản trị theo vai trò: đơn hàng, kho & lô, sản phẩm, mã giảm giá, báo cáo, người dùng.
  Đã chạy thử luồng: đăng nhập → tìm → thêm giỏ → đặt COD → nhân viên xác nhận → đóng gói → tạo vận đơn GHN.
- `docker-compose.yml` (SQL Server + API + Nginx), `.env.example`, Dockerfile cho API và Web, `frontend/nginx.conf`.
- `.github/workflows/ci.yml`: build + test Backend, lint + build Frontend, build Docker image.
- `README.md`: hướng dẫn chạy, test, cấu hình khóa, Docker, tài khoản mẫu.

## Chưa làm / cần anh tự làm
1. **GitHub**: đã đưa lên repo riêng tư https://github.com/iamduydzs1-web/SweetMart (nhánh `main` + `develop`).
   GitHub Actions đang báo "not currently enabled" dù cài đặt repo đã là "Allow all actions" → kiểm tra giới hạn ở cấp tài khoản
   (tài khoản mới / xác minh / billing) để CI chạy được.
2. **Docker chưa chạy thử** vì máy chưa cài Docker Desktop (file compose đã kiểm tra cú pháp YAML).
3. Đăng ký sandbox **VNPay** và **GHN dev**, điền khóa bằng `dotnet user-secrets` (xem README). IPN cần URL công khai (ngrok/cloudflared).
4. Điền tên thật các thành viên thay cho `[Thành viên 1..5]` trong tài liệu (sửa trong build2.py / buoc45.py rồi build lại).
5. Bước 6 (Kiểm thử) trở đi chưa viết.
6. Lưu ý nhỏ Frontend: nút "Đánh giá" trong chi tiết đơn không biết sản phẩm đã được đánh giá từ trước (Backend vẫn chặn trùng và báo lỗi).

## Chạy nhanh
```
cd backend/SweetMart.Api && dotnet run --urls http://localhost:5080     # API + Swagger /swagger
cd frontend && npm install && npm run dev                                # http://localhost:5173
dotnet test                                                              # tại thư mục SweetMart
PYTHONUTF8=1 python docs/cong-cu-tai-lieu/smoke.py backend/SweetMart.Api/appsettings.Development.json
```
Tài khoản mẫu: `quantri@ / quanly@ / nhanvien@ / khachhang@sweetmart.test`, mật khẩu ở `Seed:DefaultPassword` trong `appsettings.Development.json`.
