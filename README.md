# SweetMart – Website bán bánh kẹo

Đồ án môn **Tích hợp hệ thống**. Website thương mại điện tử bán bánh kẹo, tích hợp:

| Hệ thống ngoài | Vai trò | Cách tích hợp |
|---|---|---|
| **VNPay** (sandbox) | Thanh toán online | Tạo URL thanh toán ký HMAC‑SHA512, nhận kết quả qua **IPN** (máy chủ ↔ máy chủ), ReturnUrl chỉ để hiển thị |
| **GHN** (môi trường dev) | Tính phí và tạo vận đơn | REST API `fee`, `create`; nhận **webhook** cập nhật trạng thái giao hàng |
| **Email SMTP** (Gmail) | Gửi email xác nhận đơn, đổi trạng thái, quên mật khẩu | Hàng đợi nền, gửi lại khi lỗi |

Khi chưa có khóa thật, hệ thống tự dùng bản giả lập (`FakeGhnClient`, `LogEmailSender`) để vẫn chạy được đầy đủ luồng.

## Công nghệ

- **Backend:** ASP.NET Core 9 Web API, Entity Framework Core 9, SQL Server, JWT, BCrypt, Swagger
- **Frontend:** React 19 + Vite, React Router
- **Kiểm thử:** xUnit (32 unit test, SQLite in‑memory), script kiểm thử tích hợp `docs/cong-cu-tai-lieu/smoke.py`
- **Triển khai:** Docker Compose (SQL Server + API + Nginx), GitLab CI/CD

## Cấu trúc thư mục

```
SweetMart/
├── backend/
│   ├── SweetMart.Api/          # Web API: Controllers, Services, Integrations (VnPay, Ghn, Email), Data (EF Core)
│   └── SweetMart.Tests/        # Unit test nghiệp vụ
├── frontend/                   # React (Vite): trang khách hàng + trang quản trị
├── database/schema.sql         # Script tạo CSDL (sinh từ migration)
├── docs/                       # Tài liệu Word, sơ đồ PNG, script sinh tài liệu và smoke test
├── docker-compose.yml
├── .gitlab-ci.yml              # CI trên GitLab
└── .github/workflows/ci.yml    # CI tương đương trên GitHub
```

## Chạy trên máy (môi trường phát triển)

Yêu cầu: .NET SDK 9, Node.js 20+, SQL Server Express (hoặc LocalDB).

**1. Backend** (cổng 5080)

Lần đầu, đặt khóa JWT dev và mật khẩu tài khoản mẫu bằng user‑secrets (không lưu trong Git):

```bash
cd backend/SweetMart.Api
dotnet user-secrets set "Jwt:Key" "<chuỗi ngẫu nhiên tối thiểu 32 ký tự>"
dotnet user-secrets set "Seed:DefaultPassword" "<mật khẩu cho tài khoản mẫu>"
dotnet run --urls http://localhost:5080
```

- Chuỗi kết nối nằm trong `appsettings.Development.json` (mặc định `.\SQLEXPRESS`, CSDL `SweetMartDb`). Lần chạy đầu sẽ tự áp dụng migration và nạp dữ liệu mẫu.
- Swagger: http://localhost:5080/swagger

**2. Frontend** (cổng 5173, tự chuyển tiếp `/api` sang cổng 5080)

```bash
cd frontend
npm install
npm run dev
```

Mở http://localhost:5173

**3. Kiểm thử**

```bash
dotnet test                                   # tại thư mục SweetMart – 32 unit test
PYTHONUTF8=1 python docs/cong-cu-tai-lieu/smoke.py
                                              # kiểm thử tích hợp end-to-end, API phải đang chạy ở cổng 5080
                                              # (mật khẩu mẫu lấy từ SEED_PASSWORD hoặc user-secrets)
```

### Tài khoản mẫu

| Email | Vai trò | Quyền |
|---|---|---|
| `khachhang@sweetmart.test` | Khách hàng | Mua hàng, xem đơn, đánh giá |
| `nhanvien@sweetmart.test` | Nhân viên | Xử lý đơn, tạo vận đơn GHN, nhập lô |
| `quanly@sweetmart.test` | Quản lý | + Sản phẩm, mã giảm giá, báo cáo doanh thu |
| `quantri@sweetmart.test` | Quản trị | Quản lý tài khoản nhân viên |

Mật khẩu: giá trị `Seed:DefaultPassword` đã đặt bằng user‑secrets (hoặc `SEED_PASSWORD` trong `.env` khi chạy Docker).
Mã giảm giá mẫu: `CHAOBAN` (giảm 20.000 ₫ cho đơn từ 150.000 ₫), `TET2027` (giảm 10%, tối đa 100.000 ₫, đơn từ 300.000 ₫).

## Cấu hình khóa tích hợp

Không đưa khóa thật lên Git. Khi chạy trên máy, dùng **user‑secrets**:

```bash
cd backend/SweetMart.Api
dotnet user-secrets init
dotnet user-secrets set "VnPay:TmnCode"    "<mã website sandbox>"
dotnet user-secrets set "VnPay:HashSecret" "<chuỗi bí mật sandbox>"
dotnet user-secrets set "Ghn:Token"        "<token GHN dev>"
dotnet user-secrets set "Ghn:ShopId"       "<shop id>"
dotnet user-secrets set "Ghn:WebhookToken" "<chuỗi ngẫu nhiên>"
dotnet user-secrets set "Smtp:User"        "<gmail>"
dotnet user-secrets set "Smtp:Password"    "<app password>"
dotnet user-secrets set "Smtp:From"        "SweetMart <gmail>"
```

- VNPay sandbox: đăng ký tại https://sandbox.vnpayment.vn/devreg/ . IPN URL cần khai báo: `https://<domain công khai>/api/payments/vnpay/ipn`
  (khi chạy trên máy có thể dùng ngrok / cloudflared để có domain công khai).
- GHN dev: https://5sao.ghn.dev . Webhook URL: `https://<domain>/api/shipping/ghn-webhook/<Ghn:WebhookToken>`.

## Chạy bằng Docker

```bash
cp .env.example .env      # điền DB_PASSWORD, JWT_KEY, SEED_PASSWORD (và khóa VNPay/GHN/SMTP nếu có)
docker compose up -d --build
```

Mở http://localhost:8080 . Nginx phục vụ React và chuyển `/api/*` sang container API; API tự tạo CSDL trong container SQL Server.

## CI (GitLab CI/CD)

Repo chính: https://gitlab.com/sweetmart-btl/SweetMart . `.gitlab-ci.yml` chạy khi push lên `main`, `develop`, `feature/**` và khi mở Merge Request:
1. **backend** – image .NET SDK 9: restore, build, chạy 32 unit test, lưu kết quả `.trx` làm artifact
2. **frontend** – image Node 22: `npm ci`, lint, build
3. **docker** – Docker-in-Docker build image API và Web (chỉ trên `main`/`develop`, sau khi 2 job trên đạt)

Bản sao trên GitHub (https://github.com/duy102230-ai/SweetMart) giữ file `.github/workflows/ci.yml` tương đương cho GitHub Actions.

## Các luồng nghiệp vụ chính

- Tìm kiếm không dấu, lọc theo danh mục/giá, sắp xếp bán chạy.
- Giỏ hàng chặn vượt tồn khả dụng (chỉ tính lô còn hạn).
- Đặt hàng trong transaction: giữ kho theo **FEFO** (lô hết hạn trước xuất trước) với khóa `UPDLOCK`, áp mã giảm giá, tính phí GHN (miễn phí từ 300.000 ₫), COD tối đa 2.000.000 ₫.
- Đơn VNPay không thanh toán trong 15 phút sẽ tự hủy và hoàn kho (job nền).
- Máy trạng thái đơn: Chờ thanh toán → Chờ xác nhận → Đã xác nhận → Đang đóng gói → Đang giao → Đã giao / Giao thất bại; hủy đơn hoàn kho và hoàn lượt mã giảm giá.
- Báo cáo doanh thu theo ngày, top sản phẩm, đơn theo trạng thái.
