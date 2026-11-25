import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Circle, Polygon, Rectangle

plt.rcParams['font.family'] = 'Segoe UI'
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

TEAL = '#0F7C80'; ORANGE = '#E07B39'; NAVY = '#1B2F4B'; LIGHT = '#E6F2F2'; PINK = '#FCE8EF'; GREY = '#6B7280'


def new(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis('off')
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=220, bbox_inches='tight', pad_inches=0.08, facecolor='white')
    plt.close(fig)


def box(ax, x, y, w, h, t, fc='white', ec=TEAL, fs=9, bold=False, tc=NAVY, r=0.08, lw=1.3, ls='-'):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle=f'round,pad=0,rounding_size={r}',
                                fc=fc, ec=ec, lw=lw, ls=ls))
    ax.text(x, y, t, ha='center', va='center', fontsize=fs, color=tc, fontweight='bold' if bold else 'normal', wrap=True)


def arrow(ax, p1, p2, label=None, dashed=False, color=NAVY, style='-|>', fs=7.5, loff=(0, 0), lw=1.1):
    ax.annotate('', xy=p2, xytext=p1, arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                                      linestyle=(0, (4, 3)) if dashed else '-', shrinkA=0, shrinkB=0,
                                                      mutation_scale=11))
    if label:
        mx, my = (p1[0] + p2[0]) / 2 + loff[0], (p1[1] + p2[1]) / 2 + loff[1]
        ax.text(mx, my, label, fontsize=fs, ha='center', va='center', color=NAVY,
                bbox=dict(fc='white', ec='none', pad=1.2))


def line(ax, p1, p2, color=NAVY, lw=1.0):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw)


def actor(ax, x, y, name, fs=8.5):
    ax.add_patch(Circle((x, y + 0.42), 0.13, fc='white', ec=NAVY, lw=1.2))
    line(ax, (x, y + 0.29), (x, y - 0.08), lw=1.2)
    line(ax, (x - 0.22, y + 0.17), (x + 0.22, y + 0.17), lw=1.2)
    line(ax, (x, y - 0.08), (x - 0.17, y - 0.36), lw=1.2)
    line(ax, (x, y - 0.08), (x + 0.17, y - 0.36), lw=1.2)
    ax.text(x, y - 0.55, name, ha='center', va='center', fontsize=fs, color=NAVY, fontweight='bold')


# ---------------------------------------------------------------- 1. USE CASE
def usecase():
    fig, ax = new(10.5, 8)
    ax.add_patch(Rectangle((2.45, 0.35), 5.6, 7.3, fc='#F7FBFB', ec=TEAL, lw=1.5))
    ax.text(5.25, 7.42, 'Hệ thống Website SweetMart', ha='center', fontsize=10.5, color=TEAL, fontweight='bold')
    L = ['Xem & tìm kiếm\nsản phẩm', 'Đăng ký /\nĐăng nhập', 'Quản lý giỏ hàng', 'Đặt hàng',
         'Thanh toán online\n(VNPay)', 'Theo dõi /\nHủy đơn hàng', 'Đánh giá sản phẩm']
    R = ['Xác nhận &\nxử lý đơn hàng', 'Tạo vận đơn\n(GHN)', 'Quản lý kho\n& hạn sử dụng', 'Quản lý sản phẩm\n& danh mục',
         'Quản lý\nkhuyến mãi', 'Xem báo cáo\nthống kê', 'Quản lý tài khoản\n& phân quyền']
    xl, xr, ew, eh = 4.0, 6.5, 2.2, 0.66
    yl = [6.75 - i * 0.98 for i in range(len(L))]
    yr = [6.75 - i * 0.98 for i in range(len(R))]
    for t, y in zip(L, yl):
        ax.add_patch(Ellipse((xl, y), ew, eh, fc='white', ec=TEAL, lw=1.2)); ax.text(xl, y, t, ha='center', va='center', fontsize=8.3, color=NAVY)
    for t, y in zip(R, yr):
        ax.add_patch(Ellipse((xr, y), ew, eh, fc='white', ec=ORANGE, lw=1.2)); ax.text(xr, y, t, ha='center', va='center', fontsize=8.3, color=NAVY)
    # actors left
    actor(ax, 0.9, 6.3, 'Khách vãng lai')
    actor(ax, 0.9, 3.3, 'Khách hàng\n(thành viên)')
    ax.add_patch(FancyBboxPatch((0.25, 0.55), 1.3, 0.6, boxstyle='round,pad=0,rounding_size=0.05', fc=PINK, ec=ORANGE))
    ax.text(0.9, 0.85, '«hệ thống»\nVNPay', ha='center', va='center', fontsize=8, color=NAVY)
    for i in (0, 1):
        line(ax, (1.15, 6.4), (xl - ew / 2, yl[i]))
    for i in (2, 3, 5, 6):
        line(ax, (1.15, 3.4), (xl - ew / 2, yl[i]))
    line(ax, (1.55, 0.95), (xl - ew / 2 + 0.1, yl[4] - 0.15))
    # generalization KH -> KVL
    arrow(ax, (0.9, 4.15), (0.9, 5.5), style='-|>', color=NAVY)
    ax.text(0.98, 4.9, 'kế thừa', fontsize=7, color=GREY, rotation=90, va='center')
    # extend
    arrow(ax, (xl, yl[4] + eh / 2), (xl, yl[3] - eh / 2), dashed=True, style='->', color=GREY)
    ax.text(xl + 0.08, (yl[4] + yl[3]) / 2, '«extend»', fontsize=7, color=GREY, va='center')
    # actors right
    actor(ax, 9.6, 6.3, 'Nhân viên\nbán hàng')
    actor(ax, 9.6, 3.6, 'Quản lý\ncửa hàng')
    actor(ax, 9.6, 1.2, 'Quản trị\nhệ thống')
    for i in (0, 1, 2):
        line(ax, (9.35, 6.4), (xr + ew / 2, yr[i]))
    for i in (2, 3, 4, 5):
        line(ax, (9.35, 3.7), (xr + ew / 2, yr[i]))
    line(ax, (9.35, 1.3), (xr + ew / 2, yr[6]))
    arrow(ax, (9.6, 4.45), (9.6, 5.3), style='-|>')
    ax.text(9.68, 5.05, 'kế thừa', fontsize=7, color=GREY, rotation=90, va='center')
    save(fig, 'usecase.png')


# ---------------------------------------------------------------- 2. ACTIVITY
def activity():
    fig, ax = new(9, 12.2)
    X, S = 3.6, 7.3
    def act(x, y, t, w=2.9, h=0.56, fc='white'):
        box(ax, x, y, w, h, t, fc=fc, fs=8.5, r=0.2)
    def dec(x, y, t):
        ax.add_patch(Polygon([(x, y + 0.42), (x + 1.25, y), (x, y - 0.42), (x - 1.25, y)], fc='#FFF4EC', ec=ORANGE, lw=1.2))
        ax.text(x, y, t, ha='center', va='center', fontsize=8, color=NAVY)
    ax.add_patch(Circle((X, 11.9), 0.14, fc=NAVY))
    act(X, 11.25, 'Khách xem giỏ hàng, nhấn "Đặt hàng"')
    dec(X, 10.35, 'Đã đăng nhập?')
    act(S, 10.35, 'Đăng nhập / Đăng ký', w=2.4)
    dec(X, 9.3, 'Còn đủ tồn kho?')
    act(S, 9.3, 'Báo hết hàng,\nquay lại giỏ hàng', w=2.4, h=0.66)
    act(X, 8.3, 'Chọn / nhập địa chỉ giao hàng')
    act(X, 7.45, 'Hệ thống gọi GHN API tính phí ship')
    act(X, 6.6, 'Nhập mã giảm giá (tùy chọn)')
    act(X, 5.75, 'Chọn phương thức thanh toán')
    dec(X, 4.8, 'Thanh toán\nonline?')
    act(S, 4.8, 'Chuyển hướng sang\nVNPay, khách thanh toán', w=2.4, h=0.66)
    dec(S, 3.65, 'Thành công?')
    act(S, 2.6, 'Báo lỗi, cho chọn lại\nphương thức', w=2.4, h=0.66)
    act(X, 3.65, 'Tạo đơn hàng, giữ tồn kho\n(trạng thái theo PTTT)', h=0.66)
    act(X, 2.6, 'Xóa giỏ hàng, gửi email xác nhận')
    act(X, 1.75, 'Hiển thị trang "Đặt hàng thành công"')
    ax.add_patch(Circle((X, 1.0), 0.17, fc='white', ec=NAVY, lw=1.3)); ax.add_patch(Circle((X, 1.0), 0.1, fc=NAVY))
    v = lambda a, b, lab=None: arrow(ax, (X, a), (X, b), label=lab, loff=(0.28, 0))
    v(11.76, 11.53); v(10.97, 10.77); arrow(ax, (X, 9.93), (X, 9.72)); ax.text(X - 0.3, 10.0, 'Có', fontsize=7.5, color=NAVY, ha='center');v(8.88, 8.58, 'Có'); v(8.02, 7.73); v(7.17, 6.88); v(6.32, 6.03)
    v(5.47, 5.22); v(4.38, 3.98, 'Không (COD)'); v(3.32, 2.88); v(2.32, 2.03); v(1.47, 1.17)
    arrow(ax, (X + 1.25, 10.35), (S - 1.2, 10.35), label='Chưa', loff=(0, 0.15))
    line(ax, (S, 10.07), (S, 9.85)); arrow(ax, (S, 9.85), (X + 0.03, 9.85))
    arrow(ax, (X + 1.25, 9.3), (S - 1.2, 9.3), label='Không', loff=(0, 0.15))
    arrow(ax, (X + 1.25, 4.8), (S - 1.2, 4.8), label='Có', loff=(0, 0.15))
    arrow(ax, (S, 4.47), (S, 4.07))
    arrow(ax, (S - 1.25, 3.65), (X + 1.45, 3.65), label='Có', loff=(0, 0.15))
    arrow(ax, (S, 3.23), (S, 2.93), label='Không', loff=(0.35, 0))
    # loop back from error to choose payment
    line(ax, (S + 1.2, 2.6), (8.75, 2.6)); line(ax, (8.75, 2.6), (8.75, 5.75)); arrow(ax, (8.75, 5.75), (X + 1.45, 5.75))
    save(fig, 'activity_dathang.png')


# ---------------------------------------------------------------- 3. DFD context
def dfd():
    fig, ax = new(10.5, 6.6)
    cx, cy = 5.25, 3.3
    ax.add_patch(Circle((cx, cy), 1.05, fc=LIGHT, ec=TEAL, lw=1.8))
    ax.text(cx, cy, '0\nHệ thống\nSweetMart', ha='center', va='center', fontsize=10, color=NAVY, fontweight='bold')
    ents = {'KH': (1.2, 5.6, 'Khách hàng'), 'NV': (9.3, 5.6, 'Nhân viên /\nQuản lý'), 'QT': (9.3, 3.3, 'Quản trị\nhệ thống'),
            'VN': (1.2, 1.0, 'Cổng VNPay'), 'GHN': (5.25, 0.55, 'Giao Hàng Nhanh\n(GHN)'), 'EM': (9.3, 1.0, 'Dịch vụ Email\n(SMTP)')}
    for k, (x, y, t) in ents.items():
        box(ax, x, y, 1.9, 0.75, t, fc='white', ec=NAVY, fs=8.5, bold=True, r=0.02)
    arrow(ax, (2.15, 5.75), (cx - 0.55, cy + 0.95), 'Thông tin đăng ký, giỏ hàng,\nđơn đặt hàng, đánh giá', loff=(-0.1, 0.35))
    arrow(ax, (cx - 0.85, cy + 0.6), (2.15, 5.3), 'Danh sách SP, hóa đơn,\ntrạng thái đơn', loff=(0.2, -0.38))
    arrow(ax, (8.35, 5.75), (cx + 0.55, cy + 0.95), 'Thông tin SP, nhập kho,\nxác nhận đơn, khuyến mãi', loff=(0.1, 0.35))
    arrow(ax, (cx + 0.85, cy + 0.6), (8.35, 5.3), 'Danh sách đơn,\nbáo cáo doanh thu, tồn kho', loff=(-0.2, -0.38))
    arrow(ax, (8.35, 3.4), (cx + 1.05, cy + 0.1), 'Tài khoản, phân quyền', loff=(0, 0.17))
    arrow(ax, (cx + 1.05, cy - 0.12), (8.35, 3.18), 'Nhật ký hệ thống', loff=(0, -0.17))
    arrow(ax, (cx - 0.8, cy - 0.7), (2.15, 1.2), 'Yêu cầu thanh toán', loff=(0.15, 0.2))
    arrow(ax, (2.15, 0.85), (cx - 0.55, cy - 0.95), 'Kết quả giao dịch (IPN)', loff=(-0.25, -0.42))
    arrow(ax, (cx - 0.15, cy - 1.05), (cx - 0.15, 0.93), 'Tạo vận đơn,\ntính phí', loff=(-0.6, 0.2))
    arrow(ax, (cx + 0.15, 0.93), (cx + 0.15, cy - 1.05), 'Mã vận đơn,\ntrạng thái giao', loff=(0.8, 0))
    arrow(ax, (cx + 0.8, cy - 0.7), (8.35, 1.1), 'Email xác nhận đơn,\nquên mật khẩu', loff=(0.1, 0.3))
    save(fig, 'dfd_context.png')


# ---------------------------------------------------------------- 4. SEQUENCE
def sequence():
    fig, ax = new(10.5, 8.6)
    parts = ['Khách hàng', 'Frontend\n(ReactJS)', 'Backend API', 'CSDL\n(SQL Server)', 'Cổng VNPay']
    xs = [0.9, 3.0, 5.25, 7.5, 9.6]
    top = 8.2
    for p, x in zip(parts, xs):
        box(ax, x, top, 1.6, 0.6, p, fc=LIGHT, ec=TEAL, fs=8.5, bold=True, r=0.05)
        ax.plot([x, x], [top - 0.3, 0.2], color=GREY, lw=0.9, ls=(0, (4, 3)))
    msgs = [
        (0, 1, 'Chọn VNPay, nhấn "Thanh toán"', False),
        (1, 2, 'POST /api/orders  (giỏ hàng, địa chỉ, PTTT)', False),
        (2, 3, 'Kiểm tra tồn kho, tạo đơn "Chờ thanh toán"', False),
        (3, 2, 'MaDH', True),
        (2, 2, 'Tạo URL thanh toán + chữ ký HMAC-SHA512', False),
        (2, 1, '201 Created { paymentUrl }', True),
        (1, 4, 'Chuyển hướng tới paymentUrl', False),
        (0, 4, 'Nhập thẻ / quét QR, xác nhận OTP', False),
        (4, 2, 'IPN: kết quả giao dịch (server-to-server)', False),
        (2, 2, 'Xác thực chữ ký, đối chiếu số tiền', False),
        (2, 3, 'Lưu ThanhToan, cập nhật đơn "Chờ xác nhận"', False),
        (2, 4, 'Phản hồi RspCode = 00', True),
        (4, 1, 'Redirect về ReturnUrl kèm kết quả', True),
        (1, 0, 'Hiển thị "Thanh toán thành công"', True),
    ]
    y = 7.4
    for a, b, t, ret in msgs:
        if a == b:
            x = xs[a]
            ax.plot([x, x + 0.45, x + 0.45], [y + 0.1, y + 0.1, y - 0.15], color=NAVY, lw=1)
            arrow(ax, (x + 0.45, y - 0.15), (x + 0.02, y - 0.15))
            ax.text(x + 0.55, y - 0.02, t, fontsize=7.6, va='center', color=NAVY)
            y -= 0.55
            continue
        arrow(ax, (xs[a], y), (xs[b], y), dashed=ret)
        ax.text((xs[a] + xs[b]) / 2, y + 0.12, t, fontsize=7.6, ha='center', va='bottom', color=NAVY)
        y -= 0.5
    save(fig, 'sequence_vnpay.png')


# ---------------------------------------------------------------- 5. STATE MACHINE
def state():
    fig, ax = new(10.5, 5.4)
    def st(x, y, t, fc='white', ec=TEAL):
        box(ax, x, y, 1.75, 0.62, t, fc=fc, ec=ec, fs=8.5, bold=True, r=0.25)
    ax.add_patch(Circle((0.35, 4.3), 0.13, fc=NAVY))
    st(1.7, 4.3, 'Chờ thanh toán'); st(1.7, 2.5, 'Chờ xác nhận')
    st(4.1, 2.5, 'Đã xác nhận'); st(6.3, 2.5, 'Đang đóng gói'); st(8.6, 2.5, 'Đang giao')
    st(8.6, 4.5, 'Đã giao\n(Hoàn tất)', fc=LIGHT); st(4.1, 0.6, 'Đã hủy', fc=PINK, ec=ORANGE); st(8.6, 0.6, 'Giao thất bại', fc='#FFF4EC', ec=ORANGE)
    ax.add_patch(Circle((10.15, 4.5), 0.16, fc='white', ec=NAVY)); ax.add_patch(Circle((10.15, 4.5), 0.09, fc=NAVY))
    arrow(ax, (0.48, 4.3), (0.82, 4.3), 'online', loff=(0, 0.22))
    ax.plot([0.35, 0.35], [4.17, 2.5], color=NAVY, lw=1.1); arrow(ax, (0.35, 2.5), (0.82, 2.5), 'COD', loff=(-0.05, 0.2))
    arrow(ax, (1.7, 3.99), (1.7, 2.81), 'VNPay báo\nthành công', loff=(0.55, 0))
    ax.plot([2.58, 5.2, 5.2, 4.75], [4.3, 4.3, 1.2, 1.2], color=NAVY, lw=1.1); arrow(ax, (4.75, 1.2), (4.75, 0.91))
    ax.text(3.9, 4.55, 'Quá 15 phút / thanh toán lỗi', fontsize=7.5, ha='center', color=NAVY)
    arrow(ax, (2.58, 2.5), (3.22, 2.5), 'NV xác\nnhận', loff=(0, 0.38))
    arrow(ax, (4.98, 2.5), (5.42, 2.5)); arrow(ax, (7.18, 2.5), (7.72, 2.5), 'Tạo vận\nđơn GHN', loff=(0, 0.38))
    arrow(ax, (8.6, 2.81), (8.6, 4.19), 'Giao thành\ncông', loff=(0.55, 0))
    arrow(ax, (8.6, 2.19), (8.6, 0.91), 'Khách không\nnhận', loff=(0.6, 0))
    arrow(ax, (9.48, 4.5), (9.99, 4.5))
    arrow(ax, (1.7, 2.19), (3.3, 0.75), 'Khách / NV\nhủy', loff=(-0.35, -0.2))
    arrow(ax, (4.1, 2.19), (4.1, 0.91), 'NV hủy\n(hoàn kho)', loff=(-0.5, 0))
    arrow(ax, (7.72, 0.6), (4.98, 0.6), 'Hoàn hàng về kho', loff=(0, 0.17))
    save(fig, 'state_donhang.png')


# ---------------------------------------------------------------- 6. ERD
def erd():
    fig, ax = new(11.5, 10.6)
    T = {}
    def table(key, name, fields, cx, top, w=2.45):
        lh = 0.25
        h = 0.36 + lh * len(fields) + 0.08
        ax.add_patch(Rectangle((cx - w / 2, top - h), w, h, fc='white', ec=TEAL, lw=1.3))
        ax.add_patch(Rectangle((cx - w / 2, top - 0.36), w, 0.36, fc=TEAL, ec=TEAL))
        ax.text(cx, top - 0.18, name, ha='center', va='center', fontsize=8.8, color='white', fontweight='bold')
        for i, f in enumerate(fields):
            c = ORANGE if f.startswith('PK') else (TEAL if f.startswith('FK') else NAVY)
            ax.text(cx - w / 2 + 0.08, top - 0.36 - lh * (i + 0.6), f, fontsize=7.6, va='center', color=c,
                    fontweight='bold' if f[:2] in ('PK', 'FK') else 'normal')
        T[key] = (cx - w / 2, top - h, w, h)
    c1, c2, c3, c4 = 1.35, 4.25, 7.2, 10.1
    table('VT', 'VaiTro', ['PK MaVaiTro', 'TenVaiTro'], c1, 10.5)
    table('DC', 'DiaChi', ['PK MaDC', 'FK MaND', 'NguoiNhan', 'SoDienThoai', 'DiaChiChiTiet', 'MacDinh'], c1, 8.6)
    table('KM', 'KhuyenMai', ['PK MaKM', 'MaCode (UQ)', 'LoaiGiam', 'GiaTriGiam', 'DonToiThieu', 'NgayBatDau', 'NgayKetThuc', 'SoLuotConLai'], c1, 5.6)
    table('ND', 'NguoiDung', ['PK MaND', 'FK MaVaiTro', 'HoTen', 'Email (UQ)', 'MatKhauHash', 'SoDienThoai', 'TrangThai'], c2, 10.5)
    table('DH', 'DonHang', ['PK MaDH', 'FK MaND', 'FK MaKM', 'NgayDat', 'TongTienHang', 'PhiVanChuyen', 'TienGiam', 'TongThanhToan',
                            'PhuongThucTT', 'DiaChiGiao', 'MaVanDonGHN', 'TrangThai'], c2, 7.2)
    table('TT', 'ThanhToan', ['PK MaTT', 'FK MaDH', 'SoTien', 'MaGiaoDichVNPay', 'TrangThai', 'ThoiGian'], c2, 2.6)
    table('GH', 'GioHang', ['PK,FK MaND', 'PK,FK MaSP', 'SoLuong'], c3, 10.5)
    table('DG', 'DanhGia', ['PK MaDG', 'FK MaND', 'FK MaSP', 'SoSao (1–5)', 'NoiDung', 'NgayDanhGia'], c3, 8.9)
    table('CT', 'ChiTietDonHang', ['PK,FK MaDH', 'PK,FK MaSP', 'SoLuong', 'DonGia'], c3, 5.6)
    table('PB', 'PhanBoLo', ['PK,FK MaDH', 'PK,FK MaSP', 'PK,FK MaLo', 'SoLuong'], c3, 3.55)
    table('DM', 'DanhMuc', ['PK MaDM', 'TenDanhMuc', 'FK MaDMCha'], c4, 10.5)
    table('SP', 'SanPham', ['PK MaSP', 'FK MaDM', 'TenSP', 'ThuongHieu', 'GiaBan', 'DonViTinh', 'KhoiLuong', 'MoTa', 'TrangThai'], c4, 8.6)
    table('HA', 'HinhAnhSP', ['PK MaHA', 'FK MaSP', 'DuongDan'], c4, 5.45)
    table('LO', 'LoHang', ['PK MaLo', 'FK MaSP', 'SoLuongNhap', 'SoLuongTon', 'NgaySanXuat', 'HanSuDung', 'NgayNhap'], c4, 3.95)
    table('LS', 'LichSuDonHang', ['PK MaLS', 'FK MaDH', 'FK NguoiThucHien', 'TrangThaiCu', 'TrangThaiMoi', 'ThoiGian', 'GhiChu'], c1, 2.95)

    def side(k, s, frac=0.5):
        x, y, w, h = T[k]
        return {'L': (x, y + h * frac), 'R': (x + w, y + h * frac), 'T': (x + w * frac, y + h), 'B': (x + w * frac, y)}[s]

    def rel(a, sa, b, sb, fa=0.5, fb=0.5, la='1', lb='n'):
        p, q = side(a, sa, fa), side(b, sb, fb)
        ax.plot([p[0], q[0]], [p[1], q[1]], color=NAVY, lw=1.0)
        for pt, lab, other in ((p, la, q), (q, lb, p)):
            dx, dy = other[0] - pt[0], other[1] - pt[1]
            n = max((dx ** 2 + dy ** 2) ** 0.5, 1e-6)
            ax.text(pt[0] + dx / n * 0.18 + (0.07 if abs(dy) > abs(dx) else 0), pt[1] + dy / n * 0.18 + (0.08 if abs(dx) >= abs(dy) else 0),
                    lab, fontsize=8, color=ORANGE, fontweight='bold', ha='center', va='center')
    rel('VT', 'R', 'ND', 'L', 0.5, 0.75)
    rel('ND', 'L', 'DC', 'R', 0.35, 0.6)
    rel('ND', 'B', 'DH', 'T')
    rel('KM', 'R', 'DH', 'L', 0.5, 0.35, la='0..1')
    rel('DH', 'B', 'TT', 'T')
    rel('DH', 'R', 'CT', 'L', 0.5, 0.5)
    rel('ND', 'R', 'GH', 'L', 0.8, 0.5)
    rel('ND', 'R', 'DG', 'L', 0.25, 0.6)
    rel('SP', 'L', 'GH', 'R', 0.92, 0.4)
    rel('SP', 'L', 'DG', 'R', 0.55, 0.5)
    rel('SP', 'L', 'CT', 'R', 0.12, 0.7)
    rel('DM', 'B', 'SP', 'T')
    rel('SP', 'B', 'HA', 'T', 0.3, 0.3)
    rel('CT', 'B', 'PB', 'T')
    rel('LO', 'L', 'PB', 'R', 0.6, 0.5)
    rel('DH', 'L', 'LS', 'R', 0.08, 0.75)
    # SanPham - LoHang: route on right side
    xs, ys, ws, hs = T['SP']; xl, yl, wl, hl = T['LO']
    X = xs + ws + 0.15
    ax.plot([xs + ws, X, X, xl + wl], [ys + 0.3, ys + 0.3, yl + hl - 0.3, yl + hl - 0.3], color=NAVY, lw=1.0)
    ax.text(xs + ws + 0.05, ys + 0.42, '1', fontsize=8, color=ORANGE, fontweight='bold')
    ax.text(xl + wl + 0.05, yl + hl - 0.18, 'n', fontsize=8, color=ORANGE, fontweight='bold')
    # DanhMuc self relation
    xd, yd, wd, hd = T['DM']
    ax.plot([xd + wd, xd + wd + 0.15, xd + wd + 0.15, xd + wd], [yd + hd - 0.6, yd + hd - 0.6, yd + 0.15, yd + 0.15], color=NAVY, lw=1.0)
    ax.text(1.0, 0.3, 'Chú thích:  PK = khóa chính   FK = khóa ngoại   UQ = duy nhất   1 / n = bản số quan hệ',
            fontsize=8, color=GREY)
    save(fig, 'erd.png')


# ---------------------------------------------------------------- 7. ARCHITECTURE
def architecture():
    fig, ax = new(10.5, 6.4)
    ax.add_patch(FancyBboxPatch((0.2, 4.6), 2.6, 1.6, boxstyle='round,pad=0,rounding_size=0.1', fc=PINK, ec=ORANGE, lw=1.3))
    ax.text(1.5, 5.85, 'Tầng trình bày', fontsize=9, color=ORANGE, fontweight='bold', ha='center')
    box(ax, 1.5, 5.1, 2.2, 0.7, 'Trình duyệt (PC / Mobile)\nReactJS SPA – responsive', fs=8.3)
    ax.add_patch(FancyBboxPatch((3.4, 0.4), 3.9, 5.8, boxstyle='round,pad=0,rounding_size=0.1', fc='#F7FBFB', ec=TEAL, lw=1.3))
    ax.text(5.35, 5.85, 'Tầng nghiệp vụ – Backend API (ASP.NET Core)', fontsize=9, color=TEAL, fontweight='bold', ha='center')
    box(ax, 5.35, 5.15, 3.4, 0.55, 'Nginx reverse proxy · HTTPS', fs=8.3, fc=LIGHT)
    box(ax, 5.35, 4.35, 3.4, 0.6, 'Controllers (REST API)\nXác thực JWT · Phân quyền theo vai trò', fs=8.1)
    box(ax, 5.35, 3.45, 3.4, 0.6, 'Services (nghiệp vụ)\nĐơn hàng · Kho · Khuyến mãi · Báo cáo', fs=8.1)
    box(ax, 5.35, 2.55, 3.4, 0.6, 'Integration Adapters\nVNPayClient · GhnClient · EmailSender', fs=8.1, ec=ORANGE)
    box(ax, 5.35, 1.65, 3.4, 0.6, 'Repositories (Entity Framework Core)', fs=8.1)
    box(ax, 5.35, 0.85, 3.4, 0.5, 'Docker container trên VPS / Cloud', fs=7.8, fc=LIGHT)
    ax.add_patch(FancyBboxPatch((0.2, 0.4), 2.6, 3.6, boxstyle='round,pad=0,rounding_size=0.1', fc='white', ec=NAVY, lw=1.3))
    ax.text(1.5, 3.65, 'Tầng dữ liệu', fontsize=9, color=NAVY, fontweight='bold', ha='center')
    box(ax, 1.5, 2.6, 2.2, 0.8, 'SQL Server\n(CSDL quan hệ)', fs=8.5, fc=LIGHT)
    box(ax, 1.5, 1.2, 2.2, 0.7, 'Lưu trữ ảnh sản phẩm\n(Cloudinary / thư mục tĩnh)', fs=7.8)
    ax.add_patch(FancyBboxPatch((7.9, 0.4), 2.4, 5.8, boxstyle='round,pad=0,rounding_size=0.1', fc='#FFF8F2', ec=ORANGE, lw=1.3))
    ax.text(9.1, 5.85, 'Hệ thống bên ngoài', fontsize=9, color=ORANGE, fontweight='bold', ha='center')
    box(ax, 9.1, 4.6, 2.0, 0.7, 'VNPay\n(sandbox)', fs=8.5)
    box(ax, 9.1, 3.2, 2.0, 0.7, 'GHN API\n(phí ship, vận đơn)', fs=8.3)
    box(ax, 9.1, 1.8, 2.0, 0.7, 'SMTP / Gmail\n(email)', fs=8.3)
    arrow(ax, (2.6, 5.15), (3.65, 5.15), 'HTTPS\nJSON', style='<|-|>', loff=(0, 0.3))
    arrow(ax, (3.65, 1.65), (2.6, 2.45), 'EF Core', style='<|-|>', loff=(0, 0.2))
    arrow(ax, (3.65, 1.55), (2.6, 1.2), style='<|-|>')
    arrow(ax, (7.05, 2.7), (8.1, 4.5), 'REST', style='<|-|>', loff=(-0.1, 0.1))
    arrow(ax, (7.05, 2.6), (8.1, 3.2), style='<|-|>')
    arrow(ax, (7.05, 2.45), (8.1, 1.85), style='-|>')
    for yy in (4.65, 3.75, 2.85, 1.95):
        arrow(ax, (5.35, yy), (5.35, yy - 0.0), style='-')
    for a, b in ((4.88, 4.65), (4.05, 3.75), (3.15, 2.85), (2.25, 1.95)):
        arrow(ax, (5.35, a), (5.35, b))
    save(fig, 'architecture.png')


# ---------------------------------------------------------------- 8. SITEMAP
def sitemap():
    fig, ax = new(10.8, 6.6)
    box(ax, 2.9, 6.1, 2.4, 0.55, 'Website khách hàng', fc=TEAL, ec=TEAL, tc='white', bold=True, fs=9)
    box(ax, 8.2, 6.1, 2.4, 0.55, 'Trang quản trị (/admin)', fc=ORANGE, ec=ORANGE, tc='white', bold=True, fs=9)
    left = [('Trang chủ', []), ('Danh mục sản phẩm', ['Chi tiết sản phẩm', 'Đánh giá']), ('Tìm kiếm & lọc', []),
            ('Giỏ hàng', ['Thanh toán (Checkout)', 'Kết quả đặt hàng']), ('Tài khoản', ['Hồ sơ · Địa chỉ', 'Lịch sử đơn hàng']),
            ('Khuyến mãi', []), ('Giới thiệu · Liên hệ', [])]
    y = 5.3
    ax.plot([0.35, 0.35], [5.83, 5.3 - 0.62 * 9], color=GREY, lw=0)
    trunk_top = 5.83
    ys = []
    for name, kids in left:
        box(ax, 1.65, y, 2.2, 0.38, name, fs=8.3, r=0.05)
        ys.append(y)
        ky = y
        for k in kids:
            box(ax, 4.4, ky, 2.2, 0.38, k, fs=8, r=0.05, fc=LIGHT)
            line(ax, (2.75, y), (3.3, ky), color=GREY)
            ky -= 0.46
        y -= max(1, len(kids)) * 0.46 + 0.1
    line(ax, (0.35, 5.83), (0.35, ys[-1]), color=GREY)
    line(ax, (0.35, 5.83), (1.7, 5.83), color=GREY)
    for yy in ys:
        line(ax, (0.35, yy), (0.55, yy), color=GREY)
    right = ['Dashboard tổng quan', 'Quản lý đơn hàng', 'Quản lý sản phẩm', 'Danh mục', 'Kho & lô hàng (HSD)',
             'Khuyến mãi / mã giảm giá', 'Khách hàng', 'Báo cáo thống kê', 'Người dùng & phân quyền']
    y = 5.3
    for name in right:
        box(ax, 8.6, y, 2.6, 0.42, name, fs=8.3, r=0.05)
        line(ax, (6.95, y), (7.3, y), color=GREY)
        y -= 0.58
    line(ax, (6.95, 5.83), (6.95, y + 0.58), color=GREY)
    line(ax, (6.95, 5.83), (7.0, 5.83), color=GREY)
    save(fig, 'sitemap.png')


if __name__ == '__main__':
    for f in (usecase, activity, dfd, sequence, state, erd, architecture, sitemap):
        f()
    print('done')
