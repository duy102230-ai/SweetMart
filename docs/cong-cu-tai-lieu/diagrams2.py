import sys
from diagrams import *  # noqa  (helpers + OUT from argv)
from matplotlib.patches import FancyBboxPatch, Ellipse, Circle, Polygon, Rectangle


# ---------------------------------------------------------------- generic activity
def activity_generic(name, steps, width=9.6):
    """steps: ('a', text) | ('d', question, side_text, end_text)  -> 'Không' goes right to side box then to end."""
    X, S, SE = 3.5, 7.0, 9.0
    gap = 0.9
    H = 1.0 + gap * (len(steps) + 1) + 0.6
    fig, ax = new(width, H)
    y = H - 0.4
    ax.add_patch(Circle((X, y), 0.14, fc=NAVY))
    prev = y - 0.14
    y -= gap
    for st in steps:
        if st[0] == 'a':
            box(ax, X, y, 3.3, 0.56, st[1], fs=8.5, r=0.2)
            arrow(ax, (X, prev), (X, y + 0.28))
            prev = y - 0.28
        else:
            _, q, side, endt = st
            ax.add_patch(Polygon([(X, y + 0.4), (X + 1.35, y), (X, y - 0.4), (X - 1.35, y)], fc='#FFF4EC', ec=ORANGE, lw=1.2))
            ax.text(X, y, q, ha='center', va='center', fontsize=8, color=NAVY)
            arrow(ax, (X, prev), (X, y + 0.4))
            box(ax, S, y, 2.6, 0.66, side, fs=8, r=0.2)
            arrow(ax, (X + 1.35, y), (S - 1.3, y), 'Không', loff=(0, 0.16))
            ax.add_patch(Circle((SE, y), 0.16, fc='white', ec=NAVY, lw=1.2)); ax.add_patch(Circle((SE, y), 0.09, fc=NAVY))
            arrow(ax, (S + 1.3, y), (SE - 0.17, y))
            if endt:
                ax.text(SE, y - 0.32, endt, ha='center', fontsize=7, color=GREY)
            prev = y - 0.4
            ax.text(X + 0.12, y - 0.55, 'Có', fontsize=7.5, color=NAVY)
        y -= gap
    ax.add_patch(Circle((X, y + 0.1), 0.17, fc='white', ec=NAVY, lw=1.3)); ax.add_patch(Circle((X, y + 0.1), 0.1, fc=NAVY))
    arrow(ax, (X, prev), (X, y + 0.27))
    save(fig, name)


# ---------------------------------------------------------------- generic sequence
def sequence_generic(name, parts, msgs, width=10.5):
    n = len(parts)
    xs = [0.9 + i * (width - 1.8) / (n - 1) for i in range(n)]
    rows = sum(0.55 if a == b else 0.5 for a, b, *_ in msgs)
    H = rows + 1.6
    fig, ax = new(width, H)
    top = H - 0.4
    for p, x in zip(parts, xs):
        box(ax, x, top, 1.6, 0.6, p, fc=LIGHT, ec=TEAL, fs=8.5, bold=True, r=0.05)
        ax.plot([x, x], [top - 0.3, 0.2], color=GREY, lw=0.9, ls=(0, (4, 3)))
    y = top - 0.8
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
    save(fig, name)


def acts():
    activity_generic('activity_xacnhan.png', [
        ('a', 'Nhân viên mở danh sách đơn "Chờ xác nhận"'),
        ('a', 'Chọn đơn, xem sản phẩm, địa chỉ, ghi chú'),
        ('d', 'Thông tin giao\nhàng hợp lệ?', 'Gọi khách xác minh;\nhủy đơn kèm lý do', 'Đã hủy'),
        ('a', 'Hệ thống kiểm tra lô đã giữ (FEFO, còn hạn)'),
        ('d', 'Đủ hàng\ncòn hạn?', 'Hủy đơn, hoàn tồn kho,\nemail báo khách', 'Đã hủy'),
        ('a', 'Nhân viên nhấn "Xác nhận đơn"'),
        ('a', 'Cập nhật "Đã xác nhận", ghi LichSuDonHang'),
        ('a', 'Gửi email thông báo cho khách'),
    ])
    activity_generic('activity_thanhtoan.png', [
        ('a', 'Khách chọn VNPay, nhấn "Thanh toán"'),
        ('a', 'Tạo đơn "Chờ thanh toán", giữ tồn kho'),
        ('a', 'Backend tạo URL thanh toán, ký HMAC-SHA512'),
        ('a', 'Khách thanh toán trên cổng VNPay'),
        ('a', 'VNPay gửi IPN về Backend'),
        ('d', 'Chữ ký và số\ntiền hợp lệ?', 'Từ chối (RspCode 97/04),\nghi log cảnh báo', 'Bỏ qua'),
        ('d', 'Giao dịch\nthành công?', 'Giữ "Chờ thanh toán";\nquá 15 phút tự hủy', 'Đã hủy'),
        ('a', 'Lưu ThanhToan, đơn chuyển "Chờ xác nhận"'),
        ('a', 'Hiển thị kết quả, gửi email cho khách'),
    ])
    activity_generic('activity_giaohang.png', [
        ('a', 'Nhân viên đóng gói đơn "Đã xác nhận"'),
        ('a', 'Cập nhật trạng thái "Đang đóng gói"'),
        ('a', 'Nhấn "Tạo vận đơn" – hệ thống gọi GHN API'),
        ('d', 'Tạo vận đơn\nthành công?', 'Báo lỗi, thử lại sau\nhoặc tạo trên trang GHN', 'Chờ xử lý'),
        ('a', 'Lưu mã vận đơn, đơn "Đang giao"'),
        ('a', 'GHN cập nhật trạng thái giao (webhook)'),
        ('d', 'Giao hàng\nthành công?', '"Giao thất bại", nhận\nhàng hoàn, cộng lại kho', 'Đã hủy'),
        ('a', 'Đơn "Đã giao", ghi nhận tiền COD (nếu có)'),
    ])


def seqs():
    sequence_generic('sequence_dathang.png', ['Khách hàng', 'Frontend\n(ReactJS)', 'Backend API', 'CSDL\n(SQL Server)', 'GHN API'], [
        (0, 1, 'Mở giỏ hàng, nhấn "Đặt hàng"', False),
        (1, 2, 'POST /api/shipping/fee (địa chỉ, khối lượng)', False),
        (2, 4, 'Gọi API tính phí vận chuyển', False),
        (4, 2, 'Phí ship', True),
        (2, 1, 'Phí ship (áp BR-04 miễn phí ≥ 300.000đ)', True),
        (0, 1, 'Nhập mã giảm giá, chọn COD, xác nhận', False),
        (1, 2, 'POST /api/orders', False),
        (2, 2, 'Kiểm tra mã giảm giá (BR-05), hạn mức COD (BR-06)', False),
        (2, 3, 'BEGIN TRAN: kiểm tra tồn lô còn hạn, trừ giữ hàng (FEFO)', False),
        (2, 3, 'INSERT DonHang, ChiTietDonHang, PhanBoLo; xóa GioHang; COMMIT', False),
        (3, 2, 'MaDH', True),
        (2, 2, 'Gửi email xác nhận (bất đồng bộ)', False),
        (2, 1, '201 Created { orderCode, status: "Chờ xác nhận" }', True),
        (1, 0, 'Hiển thị "Đặt hàng thành công"', True),
    ])
    sequence_generic('sequence_xacnhan.png', ['Nhân viên', 'Trang quản trị', 'Backend API', 'CSDL\n(SQL Server)', 'GHN API'], [
        (0, 1, 'Chọn đơn "Chờ xác nhận"', False),
        (1, 2, 'GET /api/admin/orders/{id}', False),
        (2, 3, 'Truy vấn đơn, chi tiết, lô đã giữ', False),
        (3, 2, 'Dữ liệu đơn', True),
        (2, 1, '200 OK', True),
        (0, 1, 'Nhấn "Xác nhận đơn"', False),
        (1, 2, 'PUT /api/admin/orders/{id}/status', False),
        (2, 2, 'Kiểm tra quyền + trạng thái hợp lệ (BR-08)', False),
        (2, 3, 'UPDATE DonHang; INSERT LichSuDonHang', False),
        (2, 1, '200 OK – "Đã xác nhận"', True),
        (0, 1, 'Đóng gói xong, nhấn "Tạo vận đơn"', False),
        (1, 2, 'POST /api/admin/orders/{id}/shipment', False),
        (2, 4, 'Tạo đơn giao hàng (địa chỉ, COD, khối lượng)', False),
        (4, 2, 'Mã vận đơn', True),
        (2, 3, 'Lưu MaVanDonGHN, trạng thái "Đang giao"', False),
        (2, 1, '200 OK', True),
        (1, 0, 'Hiển thị mã vận đơn, in phiếu giao', True),
    ])
    sequence_generic('sequence_baocao.png', ['Quản lý', 'Trang quản trị', 'Backend API', 'CSDL\n(SQL Server)'], [
        (0, 1, 'Chọn "Báo cáo", khoảng thời gian', False),
        (1, 2, 'GET /api/admin/reports/revenue?from=&to=', False),
        (2, 2, 'Kiểm tra JWT, vai trò = Quản lý', False),
        (2, 3, 'Tổng hợp đơn "Đã giao" theo ngày', False),
        (3, 2, 'Doanh thu theo ngày', True),
        (2, 3, 'Top 10 sản phẩm bán chạy, lô cận date', False),
        (3, 2, 'Kết quả', True),
        (2, 2, 'Tính tổng, so sánh kỳ trước', False),
        (2, 1, '200 OK (JSON)', True),
        (1, 0, 'Hiển thị biểu đồ, bảng, nút xuất Excel', True),
    ], width=9)


# ---------------------------------------------------------------- DFD level 0
def dfd0():
    fig, ax = new(11.5, 9.2)
    def proc(x, y, n, t):
        ax.add_patch(Circle((x, y), 0.78, fc=LIGHT, ec=TEAL, lw=1.5))
        ax.text(x, y, f'{n}\n{t}', ha='center', va='center', fontsize=8.2, color=NAVY, fontweight='bold')
    def store(x, y, t):
        ax.add_patch(Rectangle((x - 1.0, y - 0.22), 2.0, 0.44, fc='white', ec='none'))
        ax.plot([x - 1.0, x + 1.0], [y + 0.22, y + 0.22], color=NAVY, lw=1.2); ax.plot([x - 1.0, x + 1.0], [y - 0.22, y - 0.22], color=NAVY, lw=1.2)
        ax.plot([x - 1.0, x - 1.0], [y - 0.22, y + 0.22], color=NAVY, lw=1.2)
        ax.text(x - 0.9, y, t, ha='left', va='center', fontsize=8, color=NAVY)
    def ent(x, y, t):
        box(ax, x, y, 1.7, 0.7, t, ec=NAVY, fs=8.5, bold=True, r=0.02)
    P = {1: (3.3, 7.9), 2: (8.2, 7.9), 3: (3.3, 5.0), 5: (8.2, 5.0), 4: (3.3, 2.1), 6: (8.2, 2.1)}
    proc(*P[1], 1, 'Quản lý\ntài khoản'); proc(*P[2], 2, 'Quản lý SP\n& kho (lô)'); proc(*P[3], 3, 'Giỏ hàng\n& đặt hàng')
    proc(*P[4], 4, 'Thanh toán'); proc(*P[5], 5, 'Xử lý đơn\n& giao hàng'); proc(*P[6], 6, 'Báo cáo\nthống kê')
    store(5.75, 8.5, 'D1 NguoiDung'); store(5.75, 6.7, 'D2 SanPham, LoHang'); store(5.75, 4.4, 'D3 DonHang'); store(5.75, 3.3, 'D5 KhuyenMai')
    store(5.75, 1.4, 'D4 ThanhToan')
    ent(0.95, 5.0, 'Khách hàng'); ent(10.65, 6.5, 'Nhân viên /\nQuản lý'); ent(10.65, 3.6, 'GHN'); ent(0.95, 1.2, 'VNPay'); ent(0.95, 8.4, 'Quản trị')
    A = lambda p, q, t=None, lo=(0, 0): arrow(ax, p, q, t, loff=lo, fs=7)
    A((1.8, 8.4), (2.55, 8.15), 'Tài khoản NV', (0, 0.2))
    A((1.5, 5.35), (2.65, 7.4), 'Đăng ký,\nđăng nhập', (-0.35, 0))
    A((1.8, 5.0), (2.52, 5.0))
    ax.text(2.1, 5.22, 'Giỏ, đơn', fontsize=7, color=NAVY, ha='center')
    A((2.65, 4.55), (1.8, 4.75), 'Hóa đơn, trạng thái', (-0.1, -0.35))
    A((1.5, 4.65), (2.75, 2.65), 'Chọn VNPay', (-0.3, 0))
    A((2.6, 1.85), (1.8, 1.35), 'Yêu cầu TT', (0.05, 0.22))
    A((1.8, 1.05), (2.6, 1.6), 'IPN', (0.1, -0.2))
    A((4.08, 8.1), (4.75, 8.4)); A((4.75, 8.55), (4.08, 8.3))
    A((6.75, 8.4), (7.42, 8.1)); A((7.45, 7.6), (6.75, 6.8), 'Nhập lô', (0.2, 0.1))
    A((4.75, 6.65), (3.85, 5.6), 'Giá, tồn kho', (-0.2, 0.15))
    A((4.08, 5.0), (4.75, 4.45), 'Đơn mới', (0, 0.12))
    A((4.75, 3.3), (4.05, 4.65), 'Mã KM', (0.15, -0.1))
    A((4.08, 2.1), (4.75, 1.45)); A((4.08, 2.4), (4.75, 4.2), 'Cập nhật TT đơn', (-0.8, 0.35))
    A((6.75, 4.45), (7.42, 4.85)); A((7.42, 5.25), (6.75, 6.55), 'Hoàn kho', (0.1, 0.15))
    A((9.8, 6.3), (8.95, 5.3), 'Xác nhận,\ncập nhật', (0.35, 0.1))
    A((9.8, 6.75), (8.95, 7.75), 'Thông tin SP, lô', (0.2, 0.2))
    A((8.95, 4.8), (9.8, 3.8), 'Tạo vận đơn', (0.15, 0.2)); A((9.8, 3.4), (8.85, 4.55), 'Trạng thái giao', (0.25, -0.35))
    A((6.75, 4.3), (7.5, 2.5), 'Đơn đã giao', (0.4, 0)); A((6.75, 1.4), (7.42, 1.9))
    A((8.95, 2.1), (9.8, 6.15), 'Báo cáo', (-0.2, -1.3))
    save(fig, 'dfd_muc0.png')


# ---------------------------------------------------------------- CLASS
def classdiag():
    fig, ax = new(12, 9.9)
    C = {}
    def cls(k, name, attrs, meths, cx, top, w=2.7):
        lh = 0.23
        h = 0.36 + lh * len(attrs) + 0.1 + lh * len(meths) + 0.1
        ax.add_patch(Rectangle((cx - w / 2, top - h), w, h, fc='white', ec=TEAL, lw=1.3))
        ax.add_patch(Rectangle((cx - w / 2, top - 0.36), w, 0.36, fc=TEAL, ec=TEAL))
        ax.text(cx, top - 0.18, name, ha='center', va='center', fontsize=8.8, color='white', fontweight='bold')
        y = top - 0.36 - 0.05
        for a in attrs:
            ax.text(cx - w / 2 + 0.08, y - lh / 2, '- ' + a, fontsize=7.4, va='center', color=NAVY); y -= lh
        y -= 0.05; ax.plot([cx - w / 2, cx + w / 2], [y, y], color=TEAL, lw=1); y -= 0.05
        for m in meths:
            ax.text(cx - w / 2 + 0.08, y - lh / 2, '+ ' + m, fontsize=7.4, va='center', color=ORANGE); y -= lh
        C[k] = (cx - w / 2, top - h, w, h)
    c1, c2, c3, c4 = 1.45, 4.5, 7.55, 10.55
    cls('ND', 'NguoiDung', ['maND: int', 'hoTen: string', 'email: string', 'matKhauHash: string', 'vaiTro: VaiTro'],
        ['dangNhap()', 'doiMatKhau()'], c1, 9.5)
    cls('DC', 'DiaChi', ['maDC: int', 'nguoiNhan: string', 'soDienThoai: string', 'diaChiChiTiet: string'], ['datMacDinh()'], c1, 6.6)
    cls('KM', 'KhuyenMai', ['maCode: string', 'loaiGiam: enum', 'giaTriGiam: decimal', 'donToiThieu: decimal', 'ngayKetThuc: date'],
        ['kiemTraHopLe(don)', 'tinhTienGiam(tong)'], c1, 4.1)
    cls('GH', 'GioHang', ['maND: int', 'dsSanPham: List'], ['themSanPham()', 'capNhatSoLuong()', 'tinhTamTinh()'], c2, 9.5)
    cls('DH', 'DonHang', ['maDH: int', 'ngayDat: datetime', 'tongThanhToan: decimal', 'phuongThucTT: enum', 'trangThai: enum', 'maVanDonGHN: string'],
        ['tinhTongTien()', 'capNhatTrangThai()', 'huyDon()'], c2, 7.4)
    cls('TT', 'ThanhToan', ['maTT: int', 'soTien: decimal', 'maGiaoDichVNPay: string', 'trangThai: enum'], ['xacThucChuKy()'], c2, 3.6)
    cls('CT', 'ChiTietDonHang', ['soLuong: int', 'donGia: decimal'], ['thanhTien()'], c3, 7.4)
    cls('PB', 'PhanBoLo', ['maLo: int', 'soLuong: int'], [], c3, 5.45)
    cls('DG', 'DanhGia', ['soSao: int', 'noiDung: string', 'ngayDanhGia: date'], ['guiDanhGia()'], c3, 9.5)
    cls('LS', 'LichSuDonHang', ['trangThaiCu: enum', 'trangThaiMoi: enum', 'thoiGian: datetime'], [], c3, 3.3)
    cls('DM', 'DanhMuc', ['maDM: int', 'tenDanhMuc: string'], ['layDanhMucCon()'], c4, 9.5)
    cls('SP', 'SanPham', ['maSP: int', 'tenSP: string', 'giaBan: decimal', 'khoiLuong: string', 'trangThai: enum'],
        ['tonKhaDung()', 'layLoFEFO(soLuong)'], c4, 7.9)
    cls('LO', 'LoHang', ['maLo: int', 'soLuongTon: int', 'hanSuDung: date'], ['conHan()', 'laCanDate()'], c4, 4.6)

    def side(k, s, f=0.5):
        x, y, w, h = C[k]
        return {'L': (x, y + h * f), 'R': (x + w, y + h * f), 'T': (x + w * f, y + h), 'B': (x + w * f, y)}[s]
    def rel(a, sa, b, sb, fa=0.5, fb=0.5, la='1', lb='*', comp=False):
        p, q = side(a, sa, fa), side(b, sb, fb)
        ax.plot([p[0], q[0]], [p[1], q[1]], color=NAVY, lw=1)
        if comp:
            dx, dy = q[0] - p[0], q[1] - p[1]; n = (dx * dx + dy * dy) ** .5; ux, uy = dx / n, dy / n
            pts = [p, (p[0] + ux * 0.16 - uy * 0.08, p[1] + uy * 0.16 + ux * 0.08), (p[0] + ux * 0.32, p[1] + uy * 0.32),
                   (p[0] + ux * 0.16 + uy * 0.08, p[1] + uy * 0.16 - ux * 0.08)]
            ax.add_patch(Polygon(pts, fc=NAVY, ec=NAVY))
        for pt, lab, o in ((p, la, q), (q, lb, p)):
            dx, dy = o[0] - pt[0], o[1] - pt[1]; n = max((dx * dx + dy * dy) ** .5, 1e-6)
            ax.text(pt[0] + dx / n * 0.42, pt[1] + dy / n * 0.42 + 0.1, lab, fontsize=8, color=ORANGE, fontweight='bold', ha='center')
    rel('ND', 'B', 'DC', 'T', comp=True)
    rel('ND', 'R', 'GH', 'L', 0.75, 0.6, lb='1', comp=True)
    rel('ND', 'R', 'DH', 'L', 0.3, 0.8)
    rel('KM', 'R', 'DH', 'L', 0.6, 0.3, la='0..1')
    rel('DH', 'R', 'CT', 'L', 0.6, 0.6, lb='1..*', comp=True)
    rel('DH', 'B', 'TT', 'T', lb='0..*')
    rel('DH', 'R', 'LS', 'L', 0.12, 0.6, comp=True)
    rel('CT', 'R', 'SP', 'L', 0.55, 0.3, la='*', lb='1')
    rel('DG', 'R', 'SP', 'L', 0.4, 0.88, la='*', lb='1')
    xa, ya, wa, ha = C['ND']; xb, yb, wb, hb = C['DG']
    ax.plot([xa + wa*0.5, xa + wa*0.5, xb + wb*0.5, xb + wb*0.5], [ya+ha, ya+ha+0.25, ya+ha+0.25, yb+hb], color=NAVY, lw=1)
    ax.text(xa + wa*0.5 + 0.1, ya+ha+0.05, '1', fontsize=8, color=ORANGE, fontweight='bold'); ax.text(xb + wb*0.5 + 0.1, yb+hb+0.05, '*', fontsize=8, color=ORANGE, fontweight='bold')
    rel('DM', 'B', 'SP', 'T')
    rel('SP', 'B', 'LO', 'T', comp=True)
    rel('CT', 'B', 'PB', 'T', lb='1..*', comp=True)
    rel('PB', 'R', 'LO', 'L', 0.5, 0.6, la='*', lb='1')
    ax.text(0.2, 0.15, 'Chú thích: hình thoi đặc = quan hệ hợp thành (composition), đường thẳng = liên kết (association); - thuộc tính, + phương thức',
            fontsize=8, color=GREY)
    save(fig, 'class.png')


# ---------------------------------------------------------------- STATE payment
def state_tt():
    fig, ax = new(10.5, 4.6)
    ax.set_ylim(0.1, 4.6)
    def st(x, y, t, fc='white', ec=TEAL):
        box(ax, x, y, 2.0, 0.62, t, fc=fc, ec=ec, fs=8.5, bold=True, r=0.25)
    ax.add_patch(Circle((0.35, 2.3), 0.13, fc=NAVY))
    st(2.1, 3.6, 'Chờ thanh toán\n(VNPay)'); st(2.1, 1.0, 'Chưa thu tiền\n(COD)')
    st(5.4, 3.6, 'Đã thanh toán', fc=LIGHT); st(5.4, 1.0, 'Đã thu tiền COD', fc=LIGHT)
    st(8.7, 3.6, 'Đã hoàn tiền', fc=PINK, ec=ORANGE); st(8.7, 2.3, 'Thất bại / Hết hạn', fc=PINK, ec=ORANGE); st(8.7, 1.0, 'Không thu được', fc=PINK, ec=ORANGE)
    ax.plot([0.35, 0.35], [1.0, 3.6], color=NAVY, lw=1.1)
    ax.plot([0.35, 0.35], [2.17, 2.3], color=NAVY)
    arrow(ax, (0.35, 3.6), (1.1, 3.6), 'VNPay', loff=(0, 0.17)); arrow(ax, (0.35, 1.0), (1.1, 1.0), 'COD', loff=(0, 0.17))
    arrow(ax, (3.1, 3.6), (4.4, 3.6), 'IPN thành công', loff=(0, 0.18))
    arrow(ax, (3.1, 3.4), (7.7, 2.4), 'IPN lỗi / quá 15 phút', loff=(0.3, 0.05))
    arrow(ax, (6.4, 3.6), (7.7, 3.6), 'Đơn bị hủy sau\nkhi đã trả tiền', loff=(0, 0.3))
    arrow(ax, (3.1, 1.0), (4.4, 1.0), 'Giao thành công,\nNV xác nhận thu', loff=(0, 0.3))
    ax.plot([2.1, 2.1, 8.7], [0.69, 0.3, 0.3], color=NAVY, lw=1.1); arrow(ax, (8.7, 0.3), (8.7, 0.69))
    ax.text(5.4, 0.42, 'Giao thất bại', fontsize=7.5, ha='center', color=NAVY)
    save(fig, 'state_thanhtoan.png')


# ---------------------------------------------------------------- USER FLOW
def userflow():
    fig, ax = new(11, 3.8)
    r1 = ['Trang chủ', 'Danh mục /\nTìm kiếm', 'Chi tiết\nsản phẩm', 'Thêm vào\ngiỏ hàng', 'Giỏ hàng']
    r2 = ['Theo dõi\nđơn hàng', 'Kết quả\nđặt hàng', 'Thanh toán\nVNPay / COD', 'Checkout: địa chỉ,\nship, mã giảm giá', 'Đăng nhập\n(nếu chưa)']
    xs = [1.0 + i * 2.25 for i in range(5)]
    for i, (t, x) in enumerate(zip(r1, xs)):
        box(ax, x, 3.0, 1.75, 0.75, t, fs=8.3, fc=LIGHT if i in (0, 4) else 'white', r=0.15)
        if i: arrow(ax, (xs[i - 1] + 0.88, 3.0), (x - 0.88, 3.0))
    for i, (t, x) in enumerate(zip(r2, xs)):
        box(ax, x, 1.0, 1.75, 0.75, t, fs=8.3, fc=LIGHT if i == 0 else 'white', ec=ORANGE if i == 4 else TEAL, r=0.15)
        if i: arrow(ax, (x - 0.88, 1.0), (xs[i - 1] + 0.88, 1.0))
    arrow(ax, (xs[4], 2.62), (xs[4], 1.38), '"Đặt hàng"', loff=(0.55, 0))
    save(fig, 'userflow.png')


# ---------------------------------------------------------------- WIREFRAMES
def wf_frame(w, h, title):
    fig, ax = new(w, h)
    ax.add_patch(Rectangle((0.1, 0.1), w - 0.2, h - 0.2, fc='white', ec=NAVY, lw=1.5))
    ax.add_patch(Rectangle((0.1, h - 0.45), w - 0.2, 0.35, fc='#E5E7EB', ec=NAVY, lw=1))
    for i, c in enumerate(('#D64545', '#E0B03A', '#2E9E5B')):
        ax.add_patch(Circle((0.3 + i * 0.18, h - 0.275), 0.055, fc=c, ec='none'))
    ax.text(w / 2, h - 0.275, title, ha='center', va='center', fontsize=8, color=GREY)
    return fig, ax


def wbox(ax, x, y, w, h, t='', fc='#F3F4F6', fs=7.5, bold=False, ec='#9CA3AF', tc='#374151'):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1))
    if t:
        ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=fs, color=tc, fontweight='bold' if bold else 'normal')


def img_ph(ax, x, y, w, h):
    wbox(ax, x, y, w, h, fc='#E5E7EB')
    ax.plot([x, x + w], [y, y + h], color='#9CA3AF', lw=0.8); ax.plot([x, x + w], [y + h, y], color='#9CA3AF', lw=0.8)


def header(ax, W, y):
    wbox(ax, 0.3, y, 1.4, 0.4, 'SweetMart', fc='white', bold=True, fs=9, ec='white', tc='#E85D8A')
    wbox(ax, 2.0, y, 4.6, 0.4, 'Tìm bánh kẹo, thương hiệu...   [Tìm]', fc='white', fs=7.5)
    wbox(ax, W - 2.6, y, 1.1, 0.4, 'Tài khoản', fc='white'); wbox(ax, W - 1.35, y, 1.0, 0.4, 'Giỏ (3)', fc='#FCE8EF')


def wf_home():
    W, H = 10, 7.2
    fig, ax = wf_frame(W, H, 'sweetmart.vn  –  Trang chủ')
    header(ax, W, H - 1.05)
    wbox(ax, 0.3, H - 1.5, W - 0.6, 0.3, 'Bánh quy   ·   Kẹo   ·   Socola   ·   Bánh ngọt   ·   Hộp quà Tết   ·   Khuyến mãi', fc='white')
    img_ph(ax, 0.3, H - 3.2, W - 0.6, 1.55); ax.text(W / 2, H - 2.42, 'BANNER KHUYẾN MÃI (slider)', ha='center', fontsize=9, color='#374151', fontweight='bold',
                                                     bbox=dict(fc='white', ec='none'))
    ax.text(0.3, H - 3.5, 'Sản phẩm bán chạy', fontsize=9, fontweight='bold', color=NAVY)
    for i in range(5):
        x = 0.3 + i * 1.9
        wbox(ax, x, 0.55, 1.75, 2.55, fc='white')
        img_ph(ax, x + 0.1, 1.75, 1.55, 1.25)
        ax.text(x + 0.1, 1.5, 'Tên sản phẩm', fontsize=7.5, color='#374151'); ax.text(x + 0.1, 1.25, '85.000đ', fontsize=8, color='#E85D8A', fontweight='bold')
        wbox(ax, x + 0.1, 0.65, 1.55, 0.35, 'Thêm vào giỏ', fc='#FCE8EF')
    wbox(ax, 0.3, 0.15, W - 0.6, 0.3, 'Footer: địa chỉ cửa hàng · hotline · chính sách đổi trả · giao hàng', fc='#F3F4F6')
    save(fig, 'wf_trangchu.png')


def wf_detail():
    W, H = 10, 6.4
    fig, ax = wf_frame(W, H, 'sweetmart.vn/san-pham/banh-quy-bo  –  Chi tiết sản phẩm')
    header(ax, W, H - 1.05)
    ax.text(0.3, H - 1.4, 'Trang chủ > Bánh quy > Bánh quy bơ', fontsize=7.5, color=GREY)
    img_ph(ax, 0.3, 1.9, 3.8, 3.0)
    for i in range(4): img_ph(ax, 0.3 + i * 0.97, 1.15, 0.85, 0.6)
    x = 4.5
    ax.text(x, H - 1.85, 'Bánh quy bơ hộp thiếc 454g', fontsize=11, fontweight='bold', color=NAVY)
    ax.text(x, H - 2.25, '4,5/5 sao (24 đánh giá)   ·   Thương hiệu: ...', fontsize=8, color=GREY)
    ax.text(x, H - 2.75, '165.000đ', fontsize=13, fontweight='bold', color='#E85D8A')
    ax.text(x, H - 3.15, 'HSD lô gần nhất: 12/2027   ·   Còn 36 hộp', fontsize=8, color='#2E9E5B')
    wbox(ax, x, 2.45, 1.6, 0.4, '–     1     +', fc='white')
    wbox(ax, x, 1.8, 2.6, 0.45, 'THÊM VÀO GIỎ HÀNG', fc='#E85D8A', tc='white', bold=True, ec='#E85D8A')
    wbox(ax, x + 2.8, 1.8, 2.0, 0.45, 'Mua ngay', fc='white')
    wbox(ax, 0.3, 0.2, W - 0.6, 0.75, 'Tab: Mô tả sản phẩm  |  Thành phần & bảo quản  |  Đánh giá của khách hàng', fc='#F3F4F6')
    save(fig, 'wf_chitiet.png')


def wf_checkout():
    W, H = 10, 6.6
    fig, ax = wf_frame(W, H, 'sweetmart.vn/thanh-toan  –  Checkout')
    header(ax, W, H - 1.05)
    ax.text(0.3, H - 1.5, 'Thông tin giao hàng', fontsize=9, fontweight='bold', color=NAVY)
    wbox(ax, 0.3, H - 2.2, 5.6, 0.5, '(•) Nguyễn Văn A – 09xx – 12 Lạch Tray, Hải Phòng (mặc định)      [Đổi]', fc='white', fs=7.5)
    ax.text(0.3, H - 2.6, 'Phương thức thanh toán', fontsize=9, fontweight='bold', color=NAVY)
    wbox(ax, 0.3, H - 3.25, 5.6, 0.45, '( ) Thanh toán khi nhận hàng (COD) – tối đa 2.000.000đ', fc='white')
    wbox(ax, 0.3, H - 3.8, 5.6, 0.45, '(•) Thanh toán online qua VNPay (thẻ ATM, QR, Visa)', fc='#FCE8EF')
    ax.text(0.3, H - 4.2, 'Ghi chú cho cửa hàng', fontsize=9, fontweight='bold', color=NAVY)
    wbox(ax, 0.3, 0.6, 5.6, 1.6, 'Ví dụ: gói quà sinh nhật, giao giờ hành chính...', fc='white')
    x = 6.3
    wbox(ax, x, 0.6, 3.4, H - 1.85, fc='#F9FAFB')
    ax.text(x + 0.15, H - 1.55, 'Đơn hàng (3 sản phẩm)', fontsize=9, fontweight='bold', color=NAVY)
    for i, (a, b) in enumerate((('Tạm tính', '345.000đ'), ('Phí vận chuyển (GHN)', '0đ'), ('Mã giảm giá', '–20.000đ'))):
        ax.text(x + 0.15, H - 2.2 - i * 0.4, a, fontsize=8, color='#374151'); ax.text(x + 3.25, H - 2.2 - i * 0.4, b, fontsize=8, ha='right', color='#374151')
    wbox(ax, x + 0.15, H - 3.75, 2.1, 0.38, 'Nhập mã giảm giá', fc='white'); wbox(ax, x + 2.35, H - 3.75, 0.9, 0.38, 'Áp dụng')
    ax.plot([x + 0.15, x + 3.25], [H - 4.0, H - 4.0], color='#9CA3AF')
    ax.text(x + 0.15, H - 4.4, 'Tổng thanh toán', fontsize=9, fontweight='bold', color=NAVY)
    ax.text(x + 3.25, H - 4.4, '325.000đ', fontsize=10, ha='right', fontweight='bold', color='#E85D8A')
    wbox(ax, x + 0.15, 0.8, 3.1, 0.5, 'XÁC NHẬN ĐẶT HÀNG', fc='#E85D8A', tc='white', bold=True, ec='#E85D8A')
    save(fig, 'wf_checkout.png')


def wf_admin():
    W, H = 10, 6.4
    fig, ax = wf_frame(W, H, 'sweetmart.vn/admin/don-hang  –  Quản lý đơn hàng')
    wbox(ax, 0.1, 0.1, 1.9, H - 0.55, fc='#1B2F4B', ec='#1B2F4B')
    for i, t in enumerate(['Dashboard', 'Đơn hàng', 'Sản phẩm', 'Danh mục', 'Kho & lô hàng', 'Khuyến mãi', 'Khách hàng', 'Báo cáo', 'Người dùng']):
        ax.text(0.3, H - 0.9 - i * 0.48, t, fontsize=8, color='white' if i != 1 else '#F9A8C5', fontweight='bold' if i == 1 else 'normal')
    x0 = 2.25
    ax.text(x0, H - 0.85, 'Quản lý đơn hàng', fontsize=11, fontweight='bold', color=NAVY)
    for i, t in enumerate(['Chờ xác nhận (5)', 'Đã xác nhận', 'Đang đóng gói', 'Đang giao', 'Đã giao', 'Đã hủy']):
        wbox(ax, x0 + i * 1.25, H - 1.5, 1.2, 0.35, t, fc='#FCE8EF' if i == 0 else 'white', fs=7)
    wbox(ax, x0, H - 2.0, 3.0, 0.35, 'Tìm mã đơn, SĐT khách...', fc='white', fs=7); wbox(ax, x0 + 3.1, H - 2.0, 1.6, 0.35, 'Từ ngày – đến ngày', fc='white', fs=7)
    cols = ['Mã đơn', 'Khách hàng', 'Ngày đặt', 'Tổng tiền', 'PTTT', 'Thao tác']
    cw = [1.0, 1.6, 1.2, 1.1, 0.9, 1.65]
    y = H - 2.55
    xx = x0
    for c, w in zip(cols, cw):
        wbox(ax, xx, y, w, 0.35, c, fc='#E5E7EB', bold=True, fs=7); xx += w
    for r in range(5):
        y -= 0.42; xx = x0
        vals = [f'SM00012{r}', 'Nguyễn Văn ...', '25/11/2026', f'{(r + 2) * 65}.000đ', ['COD', 'VNPay'][r % 2], '']
        for v, w in zip(vals, cw):
            wbox(ax, xx, y, w, 0.42, v, fc='white', fs=7); xx += w
        wbox(ax, xx - cw[-1] + 0.08, y + 0.07, 0.7, 0.28, 'Xác nhận', fc='#2E9E5B', tc='white', fs=6.5, ec='#2E9E5B')
        wbox(ax, xx - cw[-1] + 0.85, y + 0.07, 0.7, 0.28, 'Hủy', fc='white', fs=6.5)
    ax.text(x0, 0.35, '‹ 1 2 3 ›', fontsize=8, color=GREY)
    save(fig, 'wf_admin.png')


if __name__ == '__main__':
    erd(); acts(); seqs(); dfd0(); classdiag(); state_tt(); userflow(); wf_home(); wf_detail(); wf_checkout(); wf_admin()
    print('done2')
