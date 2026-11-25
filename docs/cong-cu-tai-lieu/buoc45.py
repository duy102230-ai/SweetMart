# -*- coding: utf-8 -*-
# Nội dung Bước 4 (Lập kế hoạch) và Bước 5 (Lập trình).
# File này được build2.py nạp bằng exec() nên dùng chung các hàm H, P, BL, T, IMGF, caption, doc...

from docx.shared import Pt, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def CODE(text, title=None):
    """Đoạn mã nguồn minh họa: font Consolas 10, nền xám nhạt, có viền trái."""
    if title:
        P(f'**{title}**', indent=False)
    t = doc.add_table(rows=1, cols=1); t.alignment = 1
    c = t.rows[0].cells[0]; c.text = ''
    tcPr = c._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:fill'), 'F3F4F6'); tcPr.append(sh)
    borders = OxmlElement('w:tcBorders')
    for side in ('top', 'left', 'bottom', 'right'):
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), '18' if side == 'left' else '4')
        b.set(qn('w:color'), 'E85D8A' if side == 'left' else 'D1D5DB'); borders.append(b)
    tcPr.append(borders)
    for i, line in enumerate(text.strip('\n').split('\n')):
        p = c.paragraphs[0] if i == 0 else c.add_paragraph()
        p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
        r = p.add_run(line if line else ' '); r.font.size = Pt(9); r.font.name = 'Consolas'
        r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'Consolas')
    set_widths(t, [TEXTW])
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


# =====================================================================================
#                                    BƯỚC 4
# =====================================================================================
doc.add_page_break()
H(1, 'BƯỚC 4. LẬP KẾ HOẠCH (PLANNING)')
P('Bước 4 chuyển Product Backlog đã thống nhất ở Bước 2 và thiết kế ở Bước 3 thành kế hoạch thực hiện cụ thể. Theo khung Scrum, kế hoạch gồm hai mức: '
  '**kế hoạch phát hành (Release Plan)** cho toàn dự án và **kế hoạch Sprint (Sprint Planning)** chi tiết cho từng Sprint 2 tuần. '
  'Kế hoạch không cố định mà được điều chỉnh sau mỗi Sprint Review dựa trên tốc độ thực tế (velocity) và phản hồi của Product Owner.')

H(2, '1. Tổ chức nhóm và nhịp làm việc Scrum')
H(3, '1.1. Vai trò trong nhóm')
caption('bang', 'Vai trò và trách nhiệm của các thành viên')
T(['Vai trò', 'Thành viên', 'Trách nhiệm chính'],
  [['Product Owner (PO)', '[Thành viên 1] (TV1)', 'Đại diện chủ cửa hàng; sắp xếp ưu tiên Product Backlog; viết và xác nhận Acceptance Criteria; nghiệm thu Increment trong Sprint Review'],
   ['Scrum Master (SM)', '[Thành viên 2] (TV2)', 'Điều phối các sự kiện Scrum; gỡ vướng mắc; theo dõi Burndown; kiêm lập trình phân quyền, danh mục'],
   ['Developer – Backend', '[Thành viên 4] (TV4)', 'API nghiệp vụ, CSDL (migration), tích hợp VNPay, GHN, Email'],
   ['Developer – Frontend', '[Thành viên 3] (TV3)', 'Giao diện React: website khách hàng và trang quản trị'],
   ['Developer – DevOps / Test', '[Thành viên 5] (TV5)', 'Repo Git, CI, Docker; viết unit test và kịch bản kiểm thử tích hợp']],
  [3.8, 3.4, 8.7])
H(3, '1.2. Các sự kiện Scrum')
caption('bang', 'Lịch các sự kiện Scrum trong mỗi Sprint 2 tuần')
T(['Sự kiện', 'Thời điểm', 'Thời lượng', 'Đầu ra'],
  [['Sprint Planning', 'Ngày đầu Sprint', '≤ 2 giờ', 'Sprint Goal, Sprint Backlog, danh sách task có người nhận'],
   ['Daily Scrum', 'Mỗi tối (họp trực tuyến)', '15 phút', 'Mỗi người trả lời: hôm qua làm gì, hôm nay làm gì, vướng gì; cập nhật bảng công việc'],
   ['Backlog Refinement', 'Giữa Sprint', '45 phút', 'Story của Sprint sau được làm rõ, ước lượng, đạt Definition of Ready'],
   ['Sprint Review', 'Ngày cuối Sprint', '1 giờ', 'Demo Increment cho PO; PO chấp nhận / trả lại Story; cập nhật Backlog'],
   ['Sprint Retrospective', 'Sau Sprint Review', '45 phút', '1–2 cải tiến cụ thể cho Sprint sau (ví dụ: review PR trong 24 giờ)']],
  [3.4, 3.6, 2.2, 6.7])
P('Công cụ hỗ trợ: **GitHub Projects** (bảng Scrum, gắn Issue với Pull Request), **GitHub Issues** (User Story, task, lỗi), **Figma** (wireframe, prototype), '
  '**Google Meet / Zalo** (Daily Scrum), **Google Drive** (tài liệu, biên bản họp).')

H(2, '2. Kế hoạch phát hành (Release Plan)')
P('Dự án kéo dài 15 tuần: Sprint 0 (tuần 1–2) dành cho khởi tạo, đặc tả yêu cầu, thiết kế và PoC tích hợp VNPay; 5 Sprint phát triển (tuần 3–12); '
  '3 tuần cuối dành cho kiểm thử chấp nhận (UAT), hoàn thiện tài liệu và bảo vệ. Mỗi mốc phát hành là một Increment chạy được, triển khai lên môi trường thử để PO kiểm tra.')
IMGF('roadmap.png', 'Lộ trình phát hành (Roadmap) của dự án SweetMart')
caption('bang', 'Các mốc phát hành')
T(['Phiên bản', 'Tuần', 'Sau Sprint', 'Nội dung phát hành', 'Mục tiêu nghiệp vụ'],
  [['v0.1', '6', 'Sprint 1–2', 'Tài khoản, phân quyền, quản lý sản phẩm, tìm kiếm không dấu, nhập kho theo lô, FEFO, giỏ hàng', 'G01, G02'],
   ['v0.2', '8', 'Sprint 3', 'Đặt hàng COD, thanh toán VNPay (IPN), theo dõi / hủy đơn, xác nhận đơn – **demo giữa kỳ**', 'G03, G04'],
   ['v0.3', '10', 'Sprint 4', 'Phí ship và vận đơn GHN, email thông báo, mã giảm giá, cảnh báo cận date, quy trình giao hàng', 'G04, G05'],
   ['v1.0', '12', 'Sprint 5', 'Báo cáo doanh thu và tồn kho, quên mật khẩu, mã giảm giá cho quản lý, sổ địa chỉ, đánh giá; đóng gói Docker', 'G06'],
   ['Bảo vệ', '15', '—', 'UAT với PO, sửa lỗi, tài liệu cuối, slide bảo vệ', 'Toàn bộ']],
  [1.7, 1.2, 2.2, 8.0, 2.8], center_cols=(0, 1, 2, 4))

H(2, '3. Ước lượng Product Backlog')
P('Nhóm ước lượng bằng **Planning Poker** với thang Story Point Fibonacci 1, 2, 3, 5, 8, 13. Story Point thể hiện **độ lớn tương đối** (khối lượng, độ phức tạp, rủi ro), '
  'không phải số giờ. Story chuẩn để so sánh là US11 – Giỏ hàng = 3 SP. Mỗi thành viên giơ thẻ cùng lúc; nếu chênh lệch lớn, người chọn cao nhất và thấp nhất giải thích rồi bỏ phiếu lại. '
  'Story từ 13 SP trở lên phải tách nhỏ trước khi đưa vào Sprint.')
caption('bang', 'Ước lượng Story Point và phân bổ Sprint')
T(['Mã', 'User Story (rút gọn)', 'Ưu tiên', 'SP', 'Sprint', 'Lý do ước lượng'],
  [['TS0', 'Thiết lập dự án: repo, CI, Docker SQL Server, khung API và React', '—', '3', '1', 'Việc kỹ thuật bắt buộc trước khi làm Story'],
   ['US01', 'Đăng ký, đăng nhập', 'Must', '5', '1', 'JWT, băm mật khẩu, khóa sau 5 lần sai'],
   ['US03', 'Tạo tài khoản nhân viên, phân quyền', 'Must', '3', '1', 'Dùng lại cơ chế JWT của US01'],
   ['US05', 'Quản lý danh mục, sản phẩm', 'Must', '5', '1', 'CRUD + ảnh + ngừng bán (xóa mềm)'],
   ['US06', 'Xem sản phẩm theo danh mục', 'Must', '5', '1', 'Phân trang, danh mục cha – con'],
   ['US07', 'Tìm kiếm, lọc, xem chi tiết (kèm HSD)', 'Must', '5', '2', 'Tìm không dấu, tính HSD lô gần nhất'],
   ['US08', 'Nhập kho theo lô', 'Must', '5', '2', 'Ràng buộc NSX, HSD'],
   ['US09', 'Giữ hàng theo FEFO', 'Must', '8', '2', 'Transaction, khóa dòng, nhiều lô – rủi ro cao'],
   ['US11', 'Giỏ hàng', 'Must', '3', '2', 'Story chuẩn'],
   ['US12', 'Đặt hàng COD', 'Must', '8', '3', 'Tính tiền, giữ kho, lưu đơn, lịch sử'],
   ['US13', 'Xem trạng thái, hủy đơn', 'Must', '3', '3', 'Hoàn kho đúng lô'],
   ['US15', 'Thanh toán VNPay', 'Must', '8', '3', 'Ký HMAC-SHA512, IPN, chống trùng – rủi ro R01'],
   ['US19', 'Xác nhận, hủy đơn (nhân viên)', 'Must', '3', '3', 'Máy trạng thái đơn'],
   ['US10', 'Cảnh báo cận date, sắp hết hàng', 'Should', '3', '4', 'Truy vấn theo HSD'],
   ['US14', 'Nhập mã giảm giá', 'Should', '3', '4', 'Điều kiện đơn tối thiểu, lượt dùng'],
   ['US16', 'Tính phí ship GHN', 'Should', '3', '4', 'Gọi API fee, phương án dự phòng'],
   ['US17', 'Tạo vận đơn GHN', 'Should', '5', '4', 'API create, webhook trạng thái'],
   ['US18', 'Email xác nhận, thông báo', 'Should', '3', '4', 'SMTP, gửi nền'],
   ['US20', 'Đóng gói, giao, hoàn tất, thu COD', 'Must', '3', '4', 'Mở rộng máy trạng thái'],
   ['US02', 'Quên mật khẩu qua email', 'Should', '2', '5', 'Token đặt lại có hạn'],
   ['US21', 'Quản lý mã giảm giá', 'Should', '3', '5', 'CRUD + kiểm tra ngày, phần trăm'],
   ['US23', 'Báo cáo doanh thu, bán chạy', 'Should', '5', '5', 'Tổng hợp theo ngày, biểu đồ'],
   ['US24', 'Báo cáo tồn kho theo lô', 'Should', '3', '5', 'Lọc cận date, hết hạn'],
   ['US04', 'Sổ địa chỉ', 'Could', '2', '5', 'Làm nếu còn thời gian'],
   ['US22', 'Đánh giá sản phẩm', 'Could', '2', '5', 'Làm nếu còn thời gian']],
  [1.3, 5.1, 1.5, 1.0, 1.7, 5.3], center_cols=(0, 2, 3, 4), fs=11)
P('Tổng khối lượng: **101 Story Point**, trung bình khoảng 20 SP mỗi Sprint. US25 (ví MoMo, tích điểm) thuộc nhóm Won\'t have nên không ước lượng.')

H(2, '4. Kế hoạch các Sprint')
caption('bang', 'Sprint Goal và khối lượng từng Sprint')
T(['Sprint', 'Tuần', 'Sprint Goal', 'Story', 'SP'],
  [['0', '1–2', 'Chốt yêu cầu, kiến trúc, ERD; PoC ký và xác thực chữ ký VNPay sandbox', 'Bước 1–3, PoC', '—'],
   ['1', '3–4', 'Người dùng đăng nhập theo vai trò; quản lý đưa sản phẩm lên và khách xem được theo danh mục', 'TS0, US01, US03, US05, US06', '21'],
   ['2', '5–6', 'Khách tìm được sản phẩm, thấy hạn dùng và bỏ vào giỏ; kho quản lý theo lô và giữ hàng FEFO', 'US07, US08, US09, US11', '21'],
   ['3', '7–8', 'Khách đặt hàng COD hoặc VNPay trọn vẹn; nhân viên xác nhận đơn (demo giữa kỳ)', 'US12, US13, US15, US19', '22'],
   ['4', '9–10', 'Đơn được giao qua GHN và khách nhận email ở mỗi bước; áp dụng được mã giảm giá', 'US10, US14, US16, US17, US18, US20', '20'],
   ['5', '11–12', 'Quản lý có báo cáo để ra quyết định; hoàn thiện, đóng gói phát hành v1.0', 'US02, US21, US23, US24, US04, US22', '17']],
  [1.4, 1.4, 7.4, 4.5, 1.2], center_cols=(0, 1, 4))
P('Thứ tự Sprint tôn trọng phụ thuộc đã xác định ở Bước 2: US09 (FEFO) cần US08 (nhập lô); US12 (đặt hàng) cần US09 và US11; US15 (VNPay) cần US12; US17 (vận đơn GHN) cần US19. '
  'Các Story gắn với rủi ro cao (US09, US15) được đặt sớm để còn thời gian xử lý nếu phát sinh vấn đề. Sprint 5 có khối lượng thấp hơn để dành thời gian sửa lỗi và đóng gói.')

H(2, '5. Sprint Planning chi tiết – Sprint 1')
P('**Sprint Goal:** "Người dùng đăng nhập theo vai trò; quản lý đưa sản phẩm lên và khách xem được theo danh mục". Nhóm chọn 21 SP (bằng năng lực ước tính của 4 Developer trong 2 tuần, '
  'mỗi người khoảng 10–12 giờ/tuần cho đồ án) và chia Story thành các task không quá 1 ngày làm việc:')
caption('bang', 'Sprint Backlog của Sprint 1')
T(['Task', 'Mô tả', 'Story', 'Người nhận', 'Giờ'],
  [['T01', 'Khởi tạo repo GitHub (main, develop), GitHub Actions, Docker SQL Server', 'TS0', 'TV5', '6'],
   ['T02', 'API đăng ký, đăng nhập, phát JWT, khóa 15 phút sau 5 lần sai', 'US01', 'TV4', '8'],
   ['T03', 'Trang đăng ký / đăng nhập, lưu phiên, chặn trang theo vai trò', 'US01', 'TV3', '6'],
   ['T04', 'Phân quyền [Authorize(Roles)], API tạo tài khoản nhân viên, khóa tài khoản', 'US03', 'TV2', '6'],
   ['T05', 'API CRUD sản phẩm, ảnh, ngừng bán', 'US05', 'TV4', '8'],
   ['T06', 'API GET /products phân trang, lọc theo danh mục', 'US06', 'TV4', '5'],
   ['T07', 'API danh mục (cha – con), migration và dữ liệu mẫu', 'US05', 'TV2', '4'],
   ['T08', 'Form quản lý sản phẩm, danh mục (trang quản trị)', 'US05', 'TV3', '8'],
   ['T09', 'Trang danh sách sản phẩm theo danh mục', 'US06', 'TV3', '6'],
   ['T10', 'Unit test tài khoản, phân quyền; kiểm thử API sản phẩm', 'US01, US05', 'TV5', '6']],
  [1.2, 8.3, 2.0, 2.2, 1.2], center_cols=(0, 2, 3, 4))

H(2, '6. Điều kiện công việc: Definition of Ready và Definition of Done')
caption('bang', 'Definition of Ready (DoR) và Definition of Done (DoD) của nhóm')
T(['Definition of Ready – Story được đưa vào Sprint khi', 'Definition of Done – Story được coi là xong khi'],
  [['• Viết đúng mẫu "Là… tôi muốn… để…"\n• Có Acceptance Criteria dạng Cho trước / Khi / Thì\n• Đã ước lượng Story Point, không quá 8 SP\n'
    '• Có wireframe nếu có giao diện\n• Đã rõ API đối tác cần dùng (VNPay, GHN) và có tài khoản sandbox\n• Không còn phụ thuộc chưa xong',
    '• Mã nguồn trên nhánh feature, đã tạo Pull Request vào develop\n• Ít nhất 1 thành viên khác review và chấp thuận\n• Unit test cho quy tắc nghiệp vụ mới, CI xanh (build + test + lint)\n'
    '• Đạt toàn bộ Acceptance Criteria khi chạy thử trên môi trường thử\n• Không ghi khóa bí mật vào mã nguồn\n• Cập nhật README / Swagger / tài liệu liên quan\n• PO chấp nhận trong Sprint Review']],
  [7.95, 7.95], fs=11.5)
P('Một Story chưa kiểm thử hoặc chưa được PO chấp nhận thì không tính vào velocity, được đưa trở lại Product Backlog để sắp xếp cho Sprint sau.')

H(2, '7. Theo dõi tiến độ')
H(3, '7.1. Bảng Scrum (Scrum Board)')
P('Mỗi task là một thẻ trên GitHub Projects, đi qua các cột **To Do → In Progress → Code Review → Testing → Done**. Mỗi thành viên không giữ quá 2 thẻ ở cột In Progress cùng lúc '
  'để hạn chế làm dở dang. Thẻ được liên kết với Pull Request; cấu hình tự động của GitHub Projects chuyển thẻ sang Testing khi PR được merge.')
IMGF('scrumboard.png', 'Bảng Scrum giữa Sprint 1 (minh họa)')
H(3, '7.2. Biểu đồ Burndown và Velocity')
P('Burndown Chart thể hiện số Story Point còn lại theo từng ngày làm việc so với đường lý tưởng. Đường thực tế nằm trên đường lý tưởng là dấu hiệu chậm tiến độ; '
  'Scrum Master nêu vấn đề trong Daily Scrum để cả nhóm hỗ trợ hoặc PO thương lượng bớt phạm vi.')
IMGF('burndown.png', 'Burndown Chart Sprint 1 (minh họa)', 13.5)
P('**Velocity** là tổng SP của các Story đạt DoD trong một Sprint. Sau mỗi Sprint Review, nhóm ghi velocity thực tế và dùng trung bình của các Sprint gần nhất để chọn khối lượng cho Sprint tiếp theo; '
  'nếu velocity thấp hơn kế hoạch, các Story Could have (US04, US22) sẽ là phần được cắt đầu tiên.')
H(3, '7.3. Kế hoạch ứng phó rủi ro trong quá trình thực hiện')
caption('bang', 'Hoạt động phòng ngừa rủi ro gắn với kế hoạch Sprint')
T(['Rủi ro', 'Hoạt động trong kế hoạch', 'Thời điểm'],
  [['R01 – Tích hợp VNPay lỗi', 'PoC ký và xác thực chữ ký ở Sprint 0; US15 đặt ở Sprint 3 (trước demo); ghi log toàn bộ IPN', 'Sprint 0, 3'],
   ['R03 – Bán vượt tồn / sai lô', 'US09 làm sớm ở Sprint 2, có unit test cho FEFO, lô hết hạn, hoàn kho', 'Sprint 2'],
   ['R04 – GHN không phản hồi', 'Tách IGhnClient, có bản giả lập để các Sprint khác không bị chặn; phí ship mặc định khi GHN lỗi', 'Sprint 4'],
   ['R06 – Thành viên chưa vững công nghệ', 'Lập trình cặp cho Story 8 SP; review PR bắt buộc', 'Mọi Sprint'],
   ['R08 – Trễ tiến độ do lịch thi', 'Sprint 5 nhẹ hơn; 3 tuần dự phòng cuối; cắt Story Could have trước', 'Sprint 5'],
   ['R11 – Triển khai lỗi sát ngày bảo vệ', 'Đóng gói Docker Compose, chạy thử triển khai cuối mỗi Sprint', 'Từ Sprint 2']],
  [4.2, 9.0, 2.7])


# =====================================================================================
#                                    BƯỚC 5
# =====================================================================================
doc.add_page_break()
H(1, 'BƯỚC 5. LẬP TRÌNH (IMPLEMENTATION)')
P('Bước 5 hiện thực thiết kế ở Bước 3 thành mã nguồn chạy được theo kế hoạch Sprint ở Bước 4. Nhóm làm theo thứ tự **CSDL (migration) → Backend / API → Frontend → tích hợp hệ thống ngoài**; '
  'mọi thay đổi đi qua Git, Pull Request và CI. Đầu ra của bước này gồm: mã nguồn trên Git, unit test, pipeline CI, Dockerfile và README hướng dẫn chạy.')

H(2, '1. Môi trường và công nghệ')
caption('bang', 'Công nghệ sử dụng trong dự án')
T(['Thành phần', 'Công nghệ', 'Vai trò'],
  [['Backend', 'ASP.NET Core 9 Web API (C#)', 'REST API, xác thực JWT, nghiệp vụ, tích hợp'],
   ['Truy cập dữ liệu', 'Entity Framework Core 9 + SQL Server 2022 / Express', 'Code First, migration, transaction'],
   ['Bảo mật', 'JWT Bearer, BCrypt, phân quyền theo vai trò', 'Đăng nhập, băm mật khẩu, [Authorize(Roles)]'],
   ['Frontend', 'React 19 + Vite 6, React Router 6', 'SPA cho khách hàng và trang quản trị'],
   ['Tài liệu API', 'Swagger (Swashbuckle)', 'Thử API trực tiếp tại /swagger'],
   ['Kiểm thử', 'xUnit + SQLite in-memory; script Python', 'Unit test nghiệp vụ; kiểm thử tích hợp đầu – cuối'],
   ['Tích hợp', 'VNPay 2.1.0 (sandbox), GHN API v2 (dev), SMTP Gmail', 'Thanh toán, vận chuyển, email'],
   ['Đóng gói, CI', 'Docker, Docker Compose, Nginx, GitHub Actions', 'Build, test tự động, triển khai'],
   ['Công cụ', 'Visual Studio 2022 / VS Code, Git, GitHub, Postman', 'Lập trình, quản lý mã nguồn, thử API']],
  [3.2, 6.4, 6.3])

H(2, '2. Quy trình làm việc với Git')
P('Nhóm dùng mô hình nhánh rút gọn từ Git Flow:')
BL(['**main:** chỉ chứa mã đã phát hành (v0.1, v0.2, v1.0), được gắn tag; không commit trực tiếp.',
    '**develop:** nhánh tích hợp của Sprint; mọi Pull Request (PR) đều merge vào đây sau khi CI xanh và được review.',
    '**feature/USxx-ten-ngan:** mỗi Story hoặc task một nhánh, tách từ develop, ví dụ feature/US12-dat-hang-cod, feature/US15-thanh-toan-vnpay.',
    '**fix/...:** sửa lỗi phát hiện khi kiểm thử; lỗi khẩn trên bản phát hành sửa ở hotfix/... rồi merge về cả main và develop.'])
IMGF('gitflow.png', 'Luồng nhánh Git khi phát triển US12 và US15')
P('Commit viết theo quy ước **Conventional Commits** để dễ đọc lịch sử: feat(order): tạo đơn COD; fix(payment): IPN trả 02 khi gửi trùng; test(inventory): FEFO bỏ qua lô hết hạn; '
  'docs: cập nhật README. Mỗi PR mô tả Story liên quan, cách kiểm tra, ảnh chụp giao diện (nếu có) và phải có ít nhất một người khác chấp thuận trước khi merge (squash merge).')

H(2, '3. Cấu trúc mã nguồn')
CODE('''SweetMart/
├── backend/SweetMart.Api/
│   ├── Controllers/    # Auth, Catalog, Cart, Orders, Payments (VNPay),
│   │                   # Shipping (GHN), Admin/* (đơn, kho, SP, mã giảm giá, báo cáo)
│   ├── Services/       # DonHang, TonKho (FEFO), ThanhToan (IPN), KhuyenMai,
│   │                   # Auth, BaoCao, OrderStateMachine
│   ├── Integrations/   # VnPay.cs, Ghn.cs (+ FakeGhnClient), Email.cs (EmailQueue)
│   ├── Background/     # HuyDonQuaHanService – hủy đơn VNPay quá 15 phút
│   ├── Domain/         # Entities, Enums, BusinessRules
│   ├── Data/           # AppDbContext, Migrations, DbSeeder
│   └── Dtos/, Common/  # DTO + kiểm tra dữ liệu, xử lý lỗi, tìm không dấu
├── backend/SweetMart.Tests/   # 32 unit test (xUnit)
├── frontend/src/
│   ├── pages/          # TrangChu, ChiTietSanPham, GioHang, ThanhToan,
│   │                   # KetQuaThanhToan, DonCuaToi, ChiTietDon, TaiKhoan
│   ├── pages/admin/    # DonHang, Kho, SanPham, KhuyenMai, BaoCao, NguoiDung
│   └── api.js, auth.jsx  # gọi API kèm JWT, phân quyền phía giao diện
├── database/schema.sql # script tạo CSDL sinh từ migration
└── docker-compose.yml, .github/workflows/ci.yml, README.md''', 'Hình thức tổ chức thư mục:')
P('Backend tổ chức theo lớp: **Controller** chỉ nhận yêu cầu và trả kết quả; **Service** chứa toàn bộ quy tắc nghiệp vụ; **Integration** đóng gói giao thức với đối tác; '
  '**Data** lo truy cập CSDL. Cách tách này giúp viết unit test cho Service mà không cần chạy web, và thay đối tác (ví dụ thêm MoMo) chỉ ảnh hưởng thư mục Integrations.')

H(2, '4. Cài đặt cơ sở dữ liệu')
P('CSDL được tạo theo hướng **Code First**: các lớp thực thể trong Domain/Entities.cs ánh xạ đúng 15 bảng ở thiết kế Bước 3 (kể cả bảng PhanBoLo). '
  'AppDbContext cấu hình khóa chính ghép (GioHang, ChiTietDonHang, PhanBoLo), chỉ mục duy nhất (email, maCode, maGiaoDichVNPay), chỉ mục (TrangThai, NgayDat) để job hủy đơn và trang quản trị lọc nhanh, '
  'kiểu decimal(12,0) cho các cột tiền. Migration KhoiTaoCSDL được áp dụng tự động khi ứng dụng khởi động; script database/schema.sql sinh từ migration để có thể tạo CSDL thủ công.')
caption('bang', 'Ràng buộc nghiệp vụ được cài đặt ở tầng dữ liệu và tầng Service')
T(['Quy tắc', 'Cách cài đặt'],
  [['BR01, BR02 – FEFO, không bán lô hết hạn', 'TonKhoService.GiuHangAsync lọc lô HanSuDung > hôm nay, sắp xếp theo HanSuDung tăng dần'],
   ['BR04 – Không vượt tồn khả dụng', 'Kiểm tra khi thêm giỏ hàng (409 OUT_OF_STOCK) và kiểm tra lại trong transaction khi đặt'],
   ['BR05 – Miễn phí ship từ 300.000 ₫', 'BusinessRules.MienPhiShipTu; dưới mức thì gọi GHN tính phí'],
   ['BR07 – COD tối đa 2.000.000 ₫', 'Từ chối đơn COD vượt hạn mức (COD_LIMIT_EXCEEDED); giao diện tự chọn VNPay'],
   ['BR08 – Hủy đơn VNPay sau 15 phút', 'vnp_ExpireDate = +15 phút; HuyDonQuaHanService chạy mỗi phút'],
   ['BR10 – Không bỏ qua bước trạng thái', 'OrderStateMachine khai báo các chuyển hợp lệ; sai thứ tự trả 409 INVALID_TRANSITION'],
   ['BR11 – Giữ đơn giá lúc đặt', 'ChiTietDonHang.DonGia và DonHang.DiaChiGiao được sao chép khi tạo đơn'],
   ['BR12 – Mỗi sản phẩm/đơn đánh giá một lần', 'Chỉ mục duy nhất (MaDH, MaSP) trên DanhGia; kiểm tra đơn ở trạng thái Đã giao']],
  [5.0, 10.9])

H(2, '5. Cài đặt Backend – các nghiệp vụ trọng tâm')
H(3, '5.1. Danh sách API')
caption('bang', 'Các nhóm API REST chính')
T(['Nhóm', 'Phương thức và đường dẫn', 'Quyền'],
  [['Tài khoản', 'POST /api/auth/register · /login · /forgot-password · /reset-password', 'Công khai'],
   ['Sản phẩm', 'GET /api/categories · /api/products?keyword&categoryId&sort&page · /api/products/{id} · /{id}/reviews', 'Công khai'],
   ['Giỏ hàng', 'GET /api/cart · PUT /api/cart/items · DELETE /api/cart/items/{maSP}', 'Khách hàng'],
   ['Địa chỉ', 'GET, POST /api/addresses · DELETE /api/addresses/{id}', 'Khách hàng'],
   ['Đơn hàng', 'POST /api/orders/preview · POST /api/orders · GET /api/orders/my · GET /{id} · PUT /{id}/cancel', 'Khách hàng'],
   ['Đánh giá', 'POST /api/reviews', 'Khách hàng'],
   ['VNPay', 'GET /api/payments/vnpay/ipn (VNPay gọi) · GET /api/payments/vnpay/return', 'Công khai, xác thực chữ ký'],
   ['GHN', 'POST /api/shipping/ghn-webhook/{token}', 'Token bí mật'],
   ['QT – Đơn hàng', 'GET /api/admin/orders · PUT /{id}/status · PUT /{id}/cancel · POST /{id}/shipment', 'Nhân viên, Quản lý'],
   ['QT – Kho', 'GET, POST /api/admin/batches · GET /api/admin/batches/low-stock', 'Nhân viên, Quản lý'],
   ['QT – Sản phẩm', 'GET, POST, PUT, DELETE /api/admin/products · /api/admin/categories', 'Quản lý'],
   ['QT – Khuyến mãi, báo cáo', 'GET, POST, PUT /api/admin/vouchers · GET /api/admin/reports/revenue', 'Quản lý'],
   ['QT – Người dùng', 'GET, POST /api/admin/users · PUT /{id}/active', 'Quản trị']],
  [3.0, 9.6, 3.3], fs=11)
P('Lỗi nghiệp vụ được trả về thống nhất dạng {"code": "...", "message": "..."} với mã HTTP phù hợp (400, 403, 404, 409, 422, 502) để Frontend hiển thị thông báo tiếng Việt; '
  'lỗi không lường trước được ghi log và trả thông báo chung, không lộ chi tiết hệ thống.')
H(3, '5.2. Đặt hàng và giữ tồn kho theo FEFO')
P('Toàn bộ việc tạo đơn nằm trong **một transaction**: tính tiền (tiền hàng, mã giảm giá, phí GHN) → với từng sản phẩm trong giỏ, giữ hàng từ các lô còn hạn có HSD gần nhất → '
  'lưu DonHang, ChiTietDonHang, PhanBoLo, LichSuDonHang → trừ lượt mã giảm giá → xóa giỏ. Nếu bất kỳ bước nào lỗi, transaction rollback nên tồn kho không bị trừ dở dang. '
  'Trên SQL Server, các dòng lô được đọc với gợi ý khóa **UPDLOCK, ROWLOCK** để hai khách đặt cùng lúc không trừ trùng một lô.')
CODE('''var cacLo = await db.LoHang
    .FromSqlInterpolated(
        $"SELECT * FROM LoHang WITH (UPDLOCK, ROWLOCK) WHERE MaSP = {maSP}")
    .Where(l => l.SoLuongTon > 0 && l.HanSuDung > homNay)  // BR02: bỏ lô hết hạn
    .OrderBy(l => l.HanSuDung).ThenBy(l => l.MaLo)          // BR01: FEFO
    .ToListAsync(ct);
if (cacLo.Sum(l => l.SoLuongTon) < soLuong)
    throw new BusinessException("OUT_OF_STOCK", "Không đủ hàng.", 409);
foreach (var lo in cacLo)
{
    if (conLai == 0) break;
    var lay = Math.Min(conLai, lo.SoLuongTon);
    lo.SoLuongTon -= lay; conLai -= lay;
    ketQua.Add(new PhanBo(lo.MaLo, lay));         // lưu vào bảng PhanBoLo
}''', 'Trích TonKhoService.GiuHangAsync:')
P('Khi đơn bị hủy hoặc giao thất bại, TonKhoService.HoanKhoAsync đọc bảng PhanBoLo của đơn và cộng trả đúng số lượng vào từng lô; lượt dùng mã giảm giá cũng được hoàn lại.')
H(3, '5.3. Máy trạng thái đơn hàng và job nền')
P('Lớp OrderStateMachine khai báo các chuyển trạng thái hợp lệ đúng như sơ đồ trạng thái ở Bước 3. Mọi thay đổi trạng thái (của nhân viên, của VNPay qua IPN, của GHN qua webhook, của job nền) '
  'đều đi qua DonHangService để được kiểm tra, ghi LichSuDonHang (người thực hiện, thời gian, ghi chú) và gửi email cho khách. Riêng trạng thái "Đang giao" chỉ đạt được qua thao tác '
  '"Tạo vận đơn GHN" để bảo đảm đơn đang giao luôn có mã vận đơn. Job nền HuyDonQuaHanService chạy mỗi phút, hủy các đơn "Chờ thanh toán" quá 15 phút và hoàn kho.')

H(2, '6. Cài đặt tích hợp hệ thống')
P('Đây là phần trọng tâm của đồ án. Mỗi đối tác được đóng gói thành một **adapter** riêng trong thư mục Integrations, cấu hình đọc từ appsettings / biến môi trường / user-secrets. '
  'Khi chưa có khóa thật, Program.cs tự đăng ký bản giả lập (FakeGhnClient, LogEmailSender) nên cả nhóm vẫn chạy được đầy đủ luồng nghiệp vụ trên máy cá nhân.')
caption('bang', 'Tổng hợp các điểm tích hợp')
T(['Đối tác', 'Chiều gọi', 'Điểm tích hợp', 'Bảo mật / độ tin cậy'],
  [['VNPay', 'SweetMart → VNPay (chuyển hướng trình duyệt)', 'URL vpcpay.html có tham số vnp_* và vnp_SecureHash', 'HMAC-SHA512 với HashSecret; hết hạn 15 phút'],
   ['VNPay', 'VNPay → SweetMart (máy chủ – máy chủ)', 'GET /api/payments/vnpay/ipn', 'Kiểm tra chữ ký, mã đơn, số tiền; chống ghi nhận trùng'],
   ['VNPay', 'Trình duyệt → SweetMart', 'GET /api/payments/vnpay/return', 'Chỉ hiển thị; không cập nhật dữ liệu'],
   ['GHN', 'SweetMart → GHN', 'POST /v2/shipping-order/fee, /create', 'Header Token, ShopId; timeout 10 giây; phương án dự phòng'],
   ['GHN', 'GHN → SweetMart', 'POST /api/shipping/ghn-webhook/{token}', 'Token bí mật trong URL; chỉ nhận chuyển trạng thái hợp lệ'],
   ['Email', 'SweetMart → SMTP', 'smtp.gmail.com:587 (TLS)', 'App Password; gửi nền, lỗi không làm hỏng đơn']],
  [1.8, 4.2, 5.2, 4.7], fs=11)
H(3, '6.1. Thanh toán VNPay')
P('**a. Tạo URL thanh toán.** Khi khách chọn VNPay, sau khi đơn được tạo ở trạng thái "Chờ thanh toán", VnPayClient dựng bộ tham số theo đặc tả 2.1.0: vnp_Amount = số tiền × 100, '
  'vnp_TxnRef = mã đơn, vnp_CreateDate và vnp_ExpireDate (giờ Việt Nam, +15 phút), vnp_ReturnUrl trỏ về trang kết quả của Frontend. Tham số được **sắp xếp theo tên**, mã hóa URL, '
  'nối thành chuỗi rồi ký HMAC-SHA512 bằng HashSecret; chữ ký gắn vào tham số vnp_SecureHash. Frontend nhận paymentUrl và chuyển trình duyệt sang cổng VNPay.')
CODE('''// thamSo là SortedDictionary nên đã được sắp xếp theo tên tham số
var query = string.Join("&", thamSo
    .Where(x => !string.IsNullOrEmpty(x.Value))
    .Select(x => $"{WebUtility.UrlEncode(x.Key)}={WebUtility.UrlEncode(x.Value)}"));
return $"{BaseUrl}?{query}&vnp_SecureHash={HmacSha512(HashSecret, query)}";''', 'Trích VnPayClient.TaoUrlThanhToan:')
P('**b. Xử lý IPN.** IPN là nơi **duy nhất** cập nhật trạng thái thanh toán, vì ReturnUrl đi qua trình duyệt nên có thể bị khách đóng trang hoặc sửa tham số. '
  'ThanhToanService.XuLyIpnAsync kiểm tra lần lượt và trả mã phản hồi theo đặc tả VNPay:')
caption('bang', 'Các bước kiểm tra IPN và mã phản hồi')
T(['Thứ tự', 'Kiểm tra', 'Nếu sai, trả về'],
  [['1', 'Chữ ký vnp_SecureHash (tính lại HMAC, so sánh thời gian hằng FixedTimeEquals)', 'RspCode 97 – Invalid signature'],
   ['2', 'vnp_TxnRef là mã đơn tồn tại', 'RspCode 01 – Order not found'],
   ['3', 'vnp_Amount bằng tổng thanh toán × 100', 'RspCode 04 – Invalid amount'],
   ['4', 'Đơn còn ở "Chờ thanh toán" (chưa xử lý IPN trước đó)', 'RspCode 02 – Order already confirmed'],
   ['5', 'Hợp lệ: lưu giao dịch ThanhToan (kèm toàn bộ dữ liệu IPN); nếu vnp_ResponseCode và vnp_TransactionStatus = 00 thì đơn chuyển "Chờ xác nhận", thanh toán "Đã thanh toán", gửi email', 'RspCode 00 – Confirm Success']],
  [1.6, 9.6, 4.7], center_cols=(0,))
P('Thanh toán thất bại vẫn trả 00 (đã nhận thông báo) nhưng đơn giữ "Chờ thanh toán" để job nền hủy sau 15 phút. Mã phản hồi được trả đúng tên khóa RspCode / Message '
  '(phân biệt hoa thường) vì VNPay đọc chính xác các khóa này; lỗi trả sai tên khóa (rspCode) do bộ chuyển JSON mặc định đổi sang camelCase đã được phát hiện nhờ kiểm thử tích hợp và được sửa bằng cách trả về Dictionary giữ nguyên tên khóa.')
P('**c. Trang kết quả.** Khi VNPay chuyển khách về /thanh-toan/ket-qua, Frontend gửi nguyên tham số lên /api/payments/vnpay/return; Backend chỉ xác thực chữ ký và trả về hopLe, thanhCong, '
  'mã đơn để hiển thị thông báo – không thay đổi dữ liệu.')
H(3, '6.2. Vận chuyển GHN')
BL(['**Tính phí:** khi khách chọn địa chỉ ở trang Checkout, Backend gọi /v2/shipping-order/fee với quận/phường gửi (cửa hàng) và nhận (mã GHN lưu trong DiaChi), khối lượng = tổng KhoiLuongGram × số lượng, '
    'giá trị khai báo bảo hiểm. Đơn từ 300.000 ₫ sau giảm giá không gọi GHN (miễn phí). Nếu GHN lỗi hoặc quá 10 giây, hệ thống dùng phí mặc định 30.000 ₫ và ghi log cảnh báo để khách vẫn đặt được hàng (NFR06).',
    '**Tạo vận đơn:** nhân viên bấm "Tạo vận đơn GHN" cho đơn "Đang đóng gói"; Backend gọi /v2/shipping-order/create với thông tin người nhận lấy từ đơn, tiền thu hộ = tổng thanh toán nếu là COD (0 nếu đã trả VNPay), '
    'client_order_code = mã đơn SweetMart. Thành công thì lưu MaVanDonGHN, đơn chuyển "Đang giao"; thất bại trả lỗi 502 GHN_ERROR để nhân viên thử lại, đơn không bị đổi trạng thái.',
    '**Webhook:** GHN gọi /api/shipping/ghn-webhook/{token} khi vận đơn đổi trạng thái; "delivered" → Đã giao (đơn COD ghi nhận đã thu tiền), "returned / delivery_fail" → Giao thất bại (hoàn kho). '
    'Token sai trả 401; trạng thái không hợp lệ theo máy trạng thái bị bỏ qua.'])
H(3, '6.3. Email thông báo')
P('DonHangService gửi email khi đặt hàng thành công, thanh toán thành công và mỗi lần đổi trạng thái; AuthService gửi liên kết đặt lại mật khẩu. Email được đưa vào **EmailQueue** và gửi ở luồng nền, '
  'nên thời gian phản hồi API không phụ thuộc máy chủ SMTP; lỗi gửi chỉ ghi log, không làm hỏng giao dịch (rủi ro R12). Khi chưa cấu hình SMTP, LogEmailSender ghi nội dung email ra log để kiểm tra.')
H(3, '6.4. Quản lý khóa bí mật')
BL(['Không ghi TmnCode, HashSecret, GHN Token, mật khẩu SMTP, khóa JWT thật vào mã nguồn; appsettings.json chỉ để trống.',
    'Trên máy lập trình dùng **dotnet user-secrets**; khi chạy Docker dùng file .env (đã đưa vào .gitignore, có .env.example làm mẫu).',
    'Ứng dụng từ chối khởi động nếu khóa JWT ngắn hơn 32 ký tự; dữ liệu mẫu từ chối tạo nếu thiếu mật khẩu mẫu.'])

H(2, '7. Cài đặt Frontend')
P('Frontend là ứng dụng React một trang. Tệp api.js gói lời gọi fetch: tự gắn header Authorization: Bearer <JWT>, chuyển lỗi {code, message} của Backend thành thông báo tiếng Việt, '
  'tự đăng xuất khi gặp 401. Khi chạy dev, Vite chuyển tiếp /api sang Backend; khi chạy Docker, Nginx đảm nhận việc này nên Frontend và API dùng chung một tên miền, không cần cấu hình CORS.')
caption('bang', 'Các màn hình đã cài đặt')
T(['Khu vực', 'Màn hình (đường dẫn)', 'Story'],
  [['Khách hàng', 'Trang chủ: danh mục, lọc giá, sắp xếp, phân trang, tìm không dấu (/)', 'US06, US07'],
   ['', 'Chi tiết sản phẩm: tồn kho, HSD lô xuất trước, đánh giá (/san-pham/:id)', 'US07, US22'],
   ['', 'Giỏ hàng (/gio-hang)', 'US11'],
   ['', 'Đặt hàng: sổ địa chỉ, phí GHN, mã giảm giá, COD / VNPay (/thanh-toan)', 'US04, US12, US14, US15, US16'],
   ['', 'Kết quả VNPay (/thanh-toan/ket-qua)', 'US15'],
   ['', 'Đơn của tôi, chi tiết đơn, hủy đơn, đánh giá (/don-hang)', 'US13, US22'],
   ['', 'Đăng nhập, đăng ký, quên / đặt lại mật khẩu', 'US01, US02'],
   ['Quản trị', 'Đơn hàng: tab theo trạng thái, tìm kiếm, chuyển trạng thái, tạo vận đơn GHN, hủy (/quan-tri/don-hang)', 'US17, US19, US20'],
   ['', 'Kho & lô hàng: cận date, hết hạn, nhập lô, sắp hết hàng (/quan-tri/kho)', 'US08, US10, US24'],
   ['', 'Sản phẩm & danh mục (/quan-tri/san-pham)', 'US05'],
   ['', 'Mã giảm giá (/quan-tri/khuyen-mai)', 'US21'],
   ['', 'Báo cáo doanh thu: thẻ số liệu, biểu đồ theo ngày, top sản phẩm (/quan-tri/bao-cao)', 'US23'],
   ['', 'Người dùng: tạo tài khoản nội bộ, khóa / mở khóa (/quan-tri/nguoi-dung)', 'US03']],
  [2.4, 10.0, 3.5], fs=11)
P('Menu trang quản trị hiển thị theo vai trò (Nhân viên chỉ thấy Đơn hàng và Kho; Quản lý thấy thêm Sản phẩm, Mã giảm giá, Báo cáo; Quản trị chỉ thấy Người dùng). '
  'Việc ẩn menu chỉ để tiện dùng – quyền thật luôn được Backend kiểm tra lại.')
P('**Một số giao diện đã hoàn thành:**', indent=False)
IMGF('ui_trangchu.jpg', 'Giao diện trang chủ', 14.5)
IMGF('ui_chitiet.jpg', 'Giao diện chi tiết sản phẩm – hiển thị tồn kho và hạn sử dụng lô xuất trước', 14.5)
IMGF('ui_checkout.jpg', 'Giao diện đặt hàng – áp dụng mã TET2027, miễn phí vận chuyển', 14.5)
IMGF('ui_donhang.jpg', 'Giao diện chi tiết đơn hàng của khách – lịch sử trạng thái và mã vận đơn GHN', 14.5)
IMGF('ui_admin_donhang.jpg', 'Trang quản trị – quản lý đơn hàng theo trạng thái', 14.5)
IMGF('ui_kho.jpg', 'Trang quản trị – kho theo lô, cảnh báo cận date', 14.5)
IMGF('ui_baocao.jpg', 'Trang quản trị – báo cáo doanh thu', 14.5)

H(2, '8. Unit test và kiểm thử của lập trình viên')
P('Theo DoD, quy tắc nghiệp vụ mới phải có unit test. Dự án SweetMart.Tests dùng xUnit và CSDL SQLite in-memory (mỗi test một CSDL riêng), gồm **23 phương thức test với 32 trường hợp**, '
  'hiện **đạt 32/32**:')
caption('bang', 'Nhóm unit test và quy tắc được kiểm tra')
T(['Nhóm', 'Các test chính', 'Quy tắc'],
  [['Tồn kho (3)', 'GiuHang_LayLoGanHetHanTruoc, GiuHang_BoQuaLoHetHan, HoanKho_CongLaiDungLo', 'BR01, BR02, BR04'],
   ['Khuyến mãi (4 phương thức)', 'TinhTienGiam (theo %, số tiền, giảm tối đa), MaHetHan_BiTuChoi, ChuaDatGiaTriToiThieu_BiTuChoi, MoiKhachChiDungMotLan', 'BR06'],
   ['Đặt hàng (4)', 'TaoDonCOD_ThanhCong, DuoiNguongMienPhi_TinhPhiShip_TuDuoi300k, VuotHanMucCOD_BiTuChoi, DoiGiaSanPham_KhongAnhHuongDonCu', 'BR05, BR07, BR11'],
   ['Trạng thái đơn (4)', 'KhachKhongHuyDuocDonDaXacNhan, ChuyenTrangThaiSaiThuTu_BiTuChoi, GiaoThanhCong_DonCOD_GhiNhanDaThuTien, OrderStateMachine_KiemTraChuyenTrangThai', 'BR09, BR10'],
   ['VNPay (5)', 'UrlThanhToan_CoChuKyHopLe_VaPhatHienSuaDoi, Ipn_HopLe_CapNhatDonDaThanhToan, Ipn_SaiChuKy_TraVe97, Ipn_SaiSoTien_TraVe04, Ipn_GuiLai_KhongGhiNhanTrung', 'BR08, US15'],
   ['Tài khoản, tìm kiếm (3)', 'DangNhapSai5Lan_BiKhoa15Phut, DangKy_EmailTrung_BiTuChoi, BoDau_TimKiemKhongDau', 'NFR04, FR05']],
  [3.3, 9.9, 2.7], fs=11)
P('Ngoài unit test, script **smoke.py** chạy kiểm thử tích hợp đầu – cuối trên API thật (SQL Server) với 21 bước: đăng ký → thêm địa chỉ → tìm kiếm không dấu → chặn vượt tồn → '
  'tính tiền với mã CHAOBAN → đặt COD → kiểm tra tồn giảm → đặt VNPay có chữ ký → kiểm tra phân quyền 403 → chặn chuyển trạng thái sai → xác nhận, đóng gói, tạo vận đơn GHN, giao thành công → '
  'đánh giá → xem lịch sử → báo cáo → lô cận date → IPN giả mạo bị từ chối (97) → đăng nhập sai bị từ chối. Kết quả lần chạy gần nhất: **21/21 đạt**. '
  'Kiểm thử hệ thống và kiểm thử chấp nhận chi tiết được trình bày ở Bước 6.')

H(2, '9. Tích hợp liên tục (CI) và đóng gói')
P('Pipeline GitHub Actions (.github/workflows/ci.yml) chạy mỗi khi push hoặc mở PR vào main, develop, feature/**:')
BL(['**Job backend:** cài .NET 9 → restore → build Release → chạy 32 unit test → lưu kết quả .trx làm bằng chứng.',
    '**Job frontend:** cài Node 22 → npm ci → lint (ESLint) → build.',
    '**Job docker:** chỉ chạy trên main / develop sau khi hai job trên đạt; build image API và Web để bảo đảm Dockerfile luôn dùng được.'])
IMGF('cicd.png', 'Quy trình CI/CD của dự án')
P('Nếu một bước lỗi, pipeline báo đỏ và PR không được merge (theo DoD). Bước triển khai tự động lên môi trường staging được bổ sung ở Bước 7 (Triển khai).')
P('**Đóng gói Docker:** docker-compose.yml gồm 3 dịch vụ: **db** (SQL Server 2022, có healthcheck), **api** (ASP.NET Core, chỉ khởi động khi db sẵn sàng, tự áp dụng migration), '
  '**web** (Nginx phục vụ bản build React và chuyển tiếp /api sang api). Chỉ cần sao chép .env.example thành .env, điền mật khẩu, khóa rồi chạy docker compose up -d --build. '
  'README.md hướng dẫn đầy đủ cách chạy trên máy, chạy test, cấu hình khóa VNPay / GHN / SMTP và tài khoản mẫu.')

H(2, '10. Kết quả Bước 5')
caption('bang', 'Đối chiếu đầu ra Bước 5 với yêu cầu của bài giảng')
T(['Đầu ra yêu cầu', 'Kết quả của nhóm'],
  [['Mã nguồn trên Git', 'Repo gồm backend (ASP.NET Core 9), frontend (React), database, docs; nhánh main / develop / feature'],
   ['Lịch sử Pull Request', 'Quy ước mỗi Story một nhánh feature, merge vào develop qua PR có review (mục 2)'],
   ['Unit test', '32 unit test nghiệp vụ, đạt 32/32; thêm kiểm thử tích hợp smoke.py đạt 21/21'],
   ['Pipeline CI', 'GitHub Actions: build + test Backend, lint + build Frontend, build Docker image'],
   ['README', 'Hướng dẫn chạy dev, chạy Docker, cấu hình khóa tích hợp, tài khoản mẫu'],
   ['Tích hợp hệ thống', 'VNPay (URL ký HMAC-SHA512, IPN, ReturnUrl), GHN (phí, vận đơn, webhook), Email SMTP (hàng đợi nền); có bản giả lập khi chưa có khóa']],
  [4.2, 11.7])
P('Việc còn lại để chuyển sang các bước sau: đăng ký tài khoản sandbox VNPay và GHN dev để chạy thử với khóa thật (cần tên miền công khai cho IPN, ví dụ dùng ngrok); '
  'kiểm thử hệ thống và UAT với Product Owner (Bước 6); triển khai lên máy chủ (Bước 7).')
