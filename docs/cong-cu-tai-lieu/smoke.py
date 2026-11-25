import json, os, pathlib, subprocess, sys, time, urllib.request, urllib.error
B = 'http://localhost:5080'

def mat_khau_mau():
    """Mật khẩu tài khoản mẫu: biến môi trường SEED_PASSWORD, nếu không có thì đọc user-secrets của SweetMart.Api."""
    if os.environ.get('SEED_PASSWORD'):
        return os.environ['SEED_PASSWORD']
    api = pathlib.Path(__file__).resolve().parents[2] / 'backend' / 'SweetMart.Api'
    out = subprocess.run(['dotnet', 'user-secrets', 'list', '--project', str(api)], capture_output=True, text=True, encoding='utf-8').stdout
    for line in out.splitlines():
        if line.startswith('Seed:DefaultPassword = '):
            return line.split(' = ', 1)[1]
    sys.exit('Không tìm thấy mật khẩu mẫu: đặt SEED_PASSWORD hoặc dotnet user-secrets set "Seed:DefaultPassword" ...')

PW = mat_khau_mau()

def call(method, path, body=None, token=None):
    req = urllib.request.Request(B + path, method=method, data=json.dumps(body).encode() if body is not None else None)
    req.add_header('Content-Type', 'application/json')
    if token: req.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(req) as r:
            t = r.read().decode(); return r.status, (json.loads(t) if t else None)
    except urllib.error.HTTPError as e:
        t = e.read().decode(); return e.code, (json.loads(t) if t else None)

def login(email):
    s, r = call('POST', '/api/auth/login', {'email': email, 'matKhau': PW}); assert s == 200, (s, r); return r['token']

ok = lambda name, cond, extra='': print(('PASS ' if cond else 'FAIL ') + name, extra)
nv, ql = login('nhanvien@sweetmart.test'), login('quanly@sweetmart.test')
# Mỗi lần chạy đăng ký một khách mới để chạy lại được nhiều lần (mã CHAOBAN chỉ dùng 1 lần/khách)
email = f'smoke{int(time.time())}@sweetmart.test'
s, r = call('POST', '/api/auth/register', {'email': email, 'matKhau': 'Smoke12345', 'hoTen': 'Khách kiểm thử', 'soDienThoai': '0900000009'})
ok('Đăng ký tài khoản khách', s == 200 and r['vaiTro'] == 'KhachHang', email)
kh = r['token']
s, r = call('POST', '/api/addresses', {'nguoiNhan': 'Khách kiểm thử', 'soDienThoai': '0900000009', 'diaChiChiTiet': '484 Lạch Tray, Lê Chân, Hải Phòng',
                                       'maQuanHuyenGHN': 1588, 'maPhuongXaGHN': '30210', 'macDinh': True}, kh)
ok('Thêm địa chỉ giao hàng', s == 200 and r['macDinh'], r.get('maDC'))

s, r = call('GET', '/api/products?keyword=banh%20quy%20bo')
ok('Tìm kiếm không dấu "banh quy bo"', s == 200 and r['total'] >= 1, [i['tenSP'] for i in r['items']])
sp = r['items'][0]
s, d = call('GET', f"/api/products/{sp['maSP']}")
ok('Chi tiết có HSD lô gần nhất', s == 200 and d['hanSuDungGanNhat'] is not None, f"HSD {d['hanSuDungGanNhat']}, tồn {d['tonKhaDung']}")

s, r = call('PUT', '/api/cart/items', {'maSP': sp['maSP'], 'soLuong': 500}, kh)
ok('Giỏ hàng chặn vượt tồn kho (BR04)', s == 409 and r.get('code') == 'OUT_OF_STOCK', r)
s, _ = call('PUT', '/api/cart/items', {'maSP': sp['maSP'], 'soLuong': 2}, kh)
s, addr = call('GET', '/api/addresses', token=kh)
mdc = addr[0]['maDC']
s, pv = call('POST', '/api/orders/preview', {'maDC': mdc, 'maCode': 'CHAOBAN'}, kh)
ok('Tính tạm tiền + mã CHAOBAN', s == 200 and pv['tienGiam'] == 20000, pv)
s, don = call('POST', '/api/orders', {'maDC': mdc, 'phuongThucTT': 'COD', 'maCode': 'CHAOBAN', 'ghiChu': 'Gói quà'}, kh)
ok('Đặt hàng COD', s == 201 and don['trangThai'] == 'ChoXacNhan', don)
s, d2 = call('GET', f"/api/products/{sp['maSP']}")
ok('Tồn kho giảm sau đặt', d2['tonKhaDung'] == d['tonKhaDung'] - 2, f"{d['tonKhaDung']} -> {d2['tonKhaDung']}")

call('PUT', '/api/cart/items', {'maSP': sp['maSP'], 'soLuong': 1}, kh)
s, don2 = call('POST', '/api/orders', {'maDC': mdc, 'phuongThucTT': 'VNPAY'}, kh)
ok('Đặt hàng VNPay trả paymentUrl có chữ ký', s == 201 and 'vnp_SecureHash=' in (don2['paymentUrl'] or ''), don2['trangThai'])

if 'maDH' not in don: sys.exit('Dừng: không tạo được đơn COD')
mid = don['maDH']
s, _ = call('GET', '/api/admin/reports/revenue', token=nv)
ok('Nhân viên xem doanh thu bị chặn (403)', s == 403, s)
s, r = call('PUT', f'/api/admin/orders/{mid}/status', {'trangThaiMoi': 'DaGiao'}, nv)
ok('Chuyển trạng thái sai thứ tự bị chặn', s == 409, r)
for st in ('DaXacNhan', 'DangDongGoi'):
    s, r = call('PUT', f'/api/admin/orders/{mid}/status', {'trangThaiMoi': st}, nv); ok(f'NV chuyển {st}', s == 200, r)
s, r = call('POST', f'/api/admin/orders/{mid}/shipment', token=nv)
ok('Tạo vận đơn GHN (giả lập)', s == 200 and r['trangThai'] == 'DangGiao', r)
s, r = call('PUT', f'/api/admin/orders/{mid}/status', {'trangThaiMoi': 'DaGiao'}, nv)
ok('Giao thành công', s == 200, r)
s, r = call('POST', '/api/reviews', {'maDH': mid, 'maSP': sp['maSP'], 'soSao': 5, 'noiDung': 'Bánh ngon'}, kh)
ok('Đánh giá sản phẩm đã giao', s == 201, r)
s, r = call('GET', f'/api/orders/{mid}', token=kh)
ok('Khách xem lịch sử đơn', s == 200 and len(r['lichSu']) == 5, [h['trangThaiMoi'] for h in r['lichSu']])
s, r = call('GET', '/api/admin/reports/revenue', token=ql)
ok('Quản lý xem báo cáo', s == 200 and r['tongSoDon'] >= 1, {k: r[k] for k in ('tongDoanhThu', 'tongSoDon')})
s, r = call('GET', '/api/admin/batches?canDate=true', token=nv)
ok('Danh sách lô cận date', s == 200 and len(r) >= 1, [(x['tenSP'], x['hanSuDung']) for x in r][:4])
s, r = call('GET', '/api/payments/vnpay/ipn?vnp_TxnRef=1&vnp_Amount=100&vnp_SecureHash=abc')
ok('IPN giả mạo bị từ chối (97)', r == {'RspCode': '97', 'Message': 'Invalid signature'}, r)
s, r = call('POST', '/api/auth/login', {'email': email, 'matKhau': 'sai-mat-khau-1'})
ok('Đăng nhập sai mật khẩu bị từ chối', s in (400, 401), s)
