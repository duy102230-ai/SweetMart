# SweetMart – Tiến độ dự án (cập nhật 25/11/2026)

## Đã xong

### Tài liệu
- `docs/SweetMart - Buoc 1-3 (theo mau).docx`: Bước 1 (Khởi tạo), Bước 2 (Yêu cầu), Bước 3 (Thiết kế), theo khung mẫu, font Times New Roman, 48 trang.
- `docs/so-do/`: toàn bộ sơ đồ dạng PNG (Use Case, Activity, DFD, Sequence, Class, State, ERD, kiến trúc, sitemap, wireframe, roadmap, burndown, Scrum board, Git flow, CI/CD).
- `docs/cong-cu-tai-lieu/`: script Python sinh sơ đồ và file Word (chạy lại khi cần sửa).
  - `python diagrams.py <thư mục ảnh>`, `python diagrams2.py <thư mục ảnh>`, `python diagrams3.py <thư mục ảnh>` → vẽ sơ đồ
  - `python build2.py <thư mục ảnh> <file .docx>` → xuất file Word Bước 1–3

### Thay đổi thiết kế cần cập nhật vào file Word
- **Thêm bảng `PhanBoLo` (MaDH, MaSP, MaLo, SoLuong)** và bỏ `MaLo` khỏi `ChiTietDonHang`.
  Lý do: khóa chính ChiTietDonHang là (MaDH, MaSP); khi một sản phẩm phải lấy từ 2 lô theo FEFO thì sẽ trùng khóa.
  Ảnh ERD và sơ đồ lớp trong `docs/so-do/` đã được sửa; **nội dung chữ trong file Word (Bước 3 – mục 2.1, 2.2) chưa sửa** (bảng thực thể, bảng quan hệ, Data Dictionary, câu "14 thực thể" → 15).
- US15 – AC4 (IPN gửi trùng): mã nguồn trả `RspCode = 02` (đơn đã xác nhận) theo đặc tả VNPay; nên sửa câu chữ AC4 cho khớp.
- Phân bổ Sprint dự kiến mới (dùng cho Bước 4): S1 – thiết lập dự án, US01, US03, US05, US06 · S2 – US07, US08, US09, US11 ·
  S3 – US12, US13, US15, US19 (demo giữa kỳ) · S4 – US10, US14, US16, US17, US18, US20 · S5 – US02, US21, US23, US24 (+US04, US22 nếu còn thời gian).

### Mã nguồn (Bước 5)
- `backend/SweetMart.Api`: ASP.NET Core 9 Web API + EF Core + SQL Server.
  - Nghiệp vụ: đặt hàng (transaction), giữ kho theo FEFO có khóa UPDLOCK, mã giảm giá, máy trạng thái đơn, hủy đơn/hoàn kho, báo cáo.
  - Tích hợp: VNPay (tạo URL ký HMAC-SHA512, xử lý IPN), GHN (tính phí, tạo vận đơn, webhook), Email SMTP.
    Chưa có khóa thật thì tự dùng bản giả lập (FakeGhnClient, LogEmailSender).
  - Job nền tự hủy đơn VNPay quá 15 phút.
  - Swagger tại `/swagger` khi chạy Development.
- `backend/SweetMart.Tests`: 32 unit test xUnit (SQLite in-memory) – **đang đạt 32/32**.
- `backend/SweetMart.Api/Data/Migrations` + `database/schema.sql`: migration và script tạo CSDL.
- Đã chạy thử với SQL Server Express trên máy (CSDL `SweetMartDb` đã được tạo và nạp dữ liệu mẫu).

## Chưa làm
1. Chạy hết script kiểm thử tích hợp `docs/cong-cu-tai-lieu/smoke.py`.
   Lần chạy trước dừng ở bước in tiếng Việt ra console; cần chạy với `PYTHONUTF8=1`, API phải đang chạy ở cổng 5080.
2. Frontend React (Vite): trang chủ, danh sách/chi tiết SP, giỏ hàng, checkout, kết quả VNPay, đơn của tôi, trang quản trị.
3. Docker (`docker-compose.yml`), GitHub Actions CI (`.github/workflows/ci.yml`), `README.md`.
4. Viết Bước 4 (Lập kế hoạch) và Bước 5 (Lập trình) vào file Word.
   Sơ đồ đã có sẵn: `roadmap.png`, `burndown.png` (minh họa), `scrumboard.png`, `gitflow.png`, `cicd.png`.
5. Đăng ký tài khoản sandbox VNPay, GHN và điền khóa (không commit khóa thật – dùng `dotnet user-secrets`).

## Chạy Backend
```
cd backend/SweetMart.Api
dotnet run --urls http://localhost:5080
```
- Tài khoản mẫu (vai trò quản trị, quản lý, nhân viên, khách hàng) được tạo trong `Data/DbSeeder.cs`.
- Mật khẩu mẫu nằm ở `Seed:DefaultPassword` trong `appsettings.Development.json`.
- Chạy test: `dotnet test` (tại thư mục SweetMart).
