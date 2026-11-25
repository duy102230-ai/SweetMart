import sys, os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

IMG, OUT = sys.argv[1], sys.argv[2]
FONT = 'Times New Roman'
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for m in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'):
    setattr(sec, m, Cm(2.54))
TEXTW = 15.9


def set_font(style, size, bold=None, color=None):
    style.font.name = FONT; style.font.size = Pt(size)
    if bold is not None: style.font.bold = bold
    style.font.color.rgb = color or RGBColor(0, 0, 0)
    rpr = style.element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.append(rf)
    for a in list(rf.attrib):
        if 'Theme' in a or 'theme' in a: del rf.attrib[a]
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        rf.set(qn(a), FONT)


set_font(doc.styles['Normal'], 13)
pf = doc.styles['Normal'].paragraph_format; pf.space_after = Pt(4); pf.line_spacing = 1.2
for lv in (1, 2, 3, 4):
    s = doc.styles[f'Heading {lv}']; set_font(s, 13, bold=True); s.font.italic = False
    s.paragraph_format.space_before = Pt(10 if lv == 1 else 6); s.paragraph_format.space_after = Pt(4)
    s.paragraph_format.keep_with_next = True
set_font(doc.styles['Heading 1'], 14, bold=True)

cnt = {'hinh': 0, 'bang': 0}


def runs(p, text, size=None):
    for i, part in enumerate(text.split('**')):
        if part:
            r = p.add_run(part); r.bold = (i % 2 == 1)
            if size: r.font.size = Pt(size)
    return p


def H(level, text):
    doc.add_heading(text, level=level)


def P(text, indent=True):
    p = doc.add_paragraph(); runs(p, text)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent: p.paragraph_format.first_line_indent = Cm(1)
    return p


def BL(items, sym='–', level=0):
    for it in items:
        p = doc.add_paragraph(); runs(p, f'{sym}\t' + it)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        left = 1.0 + level * 0.75
        p.paragraph_format.left_indent = Cm(left); p.paragraph_format.first_line_indent = Cm(-0.5)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(left))
        p.paragraph_format.space_after = Pt(2)


def NUM(items):
    for i, it in enumerate(items, 1):
        P(f'{i}. ' + it)


def caption(prefix, text):
    cnt[prefix] += 1
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f'{"Hình" if prefix == "hinh" else "Bảng"} {cnt[prefix]}. {text}'); r.italic = True; r.font.size = Pt(12)
    return p


def set_widths(t, widths):
    t.autofit = False
    tblPr = t._tbl.tblPr
    for tag in ('w:tblW', 'w:tblLayout'):
        el = tblPr.find(qn(tag))
        if el is not None: tblPr.remove(el)
    tw = OxmlElement('w:tblW'); tw.set(qn('w:w'), str(int(sum(widths) * 567))); tw.set(qn('w:type'), 'dxa'); tblPr.append(tw)
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)
    for i, gc in enumerate(t._tbl.tblGrid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(widths[i] * 567)))
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)


def T(headers, rows, widths, title=None, fs=12, center_cols=()):
    if title: caption('bang', title)
    t = doc.add_table(rows=1, cols=len(headers)); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ''; p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.bold = True; r.font.size = Pt(fs)
        tcPr = c._tc.get_or_add_tcPr(); sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:fill'), 'D9E2F3'); tcPr.append(sh)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            c = cells[i]; c.text = ''
            for li, line in enumerate(str(v).split('\n')):
                p = c.paragraphs[0] if li == 0 else c.add_paragraph()
                runs(p, line, size=fs); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.05
                if i in center_cols: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    trPr = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement('w:tblHeader'); th.set(qn('w:val'), 'true'); trPr.append(th)
    set_widths(t, widths)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def IMGF(name, title, width=15.5):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(os.path.join(IMG, name), width=Cm(width))
    caption('hinh', title)


def UC(code, name, fields):
    BL([f'**{name} ({code})**'], sym='●')
    keys = ['Mã Use Case', 'Tên Use Case', 'Tác nhân', 'Yêu cầu liên quan', 'Mô tả', 'Mục đích (Goal)',
            'Bắt đầu thực hiện (Trigger)', 'Tiền điều kiện (Preconditions)', 'Luồng chính', 'Luồng ngoại lệ', 'Hậu điều kiện (Postconditions)']
    vals = [code + '.', name + '.'] + fields
    for k, v in zip(keys, vals):
        P(f'**{k}:** {v}')


def STORY(n, code, title, text, acs):
    P(f'{n}. **User Story – {title} ({code}):** {text}')
    for name, g, w, t in acs:
        BL([f'**{name}**'], sym='–')
        BL([f'Cho trước: {g}', f'Khi: {w}', f'Thì: {t}'], sym='+', level=1)


# =====================================================================================
#                                    BƯỚC 1
# =====================================================================================
H(1, 'BƯỚC 1. KHỞI TẠO DỰ ÁN')
H(2, '1. Khảo sát')
H(3, '1.1. Mục đích và phạm vi')
H(4, '1.1.1. Mục đích khảo sát')
P('Hoạt động khảo sát nhằm tìm hiểu quy trình bán hàng, quản lý hàng hóa và xử lý đơn hàng hiện tại (As-Is) của cửa hàng bánh kẹo SweetMart. '
  'Qua đó, nhóm xác định những khó khăn, hạn chế trong cách làm thủ công hiện nay và đề xuất quy trình mới (To-Be) thông qua việc xây dựng website bán bánh kẹo, '
  'phù hợp với quy mô và nhu cầu thực tế của cửa hàng.')
P('Nội dung khảo sát tập trung vào các hoạt động: giới thiệu sản phẩm, quản lý giá bán, kiểm tra tồn kho và **hạn sử dụng theo từng lô hàng**, tiếp nhận và xử lý đơn hàng, '
  'thanh toán, giao hàng, chạy chương trình khuyến mãi và thống kê doanh thu. Đây là những đặc thù của ngành hàng bánh kẹo – hàng thực phẩm đóng gói có hạn sử dụng, '
  'bán chạy theo mùa (Tết, Trung thu, 1/6, Giáng sinh) và thường được mua làm quà.')
P('Bên cạnh việc xác định các chức năng cần có, khảo sát còn làm rõ **nhu cầu tích hợp với hệ thống bên ngoài** – trọng tâm của môn Đồ án tích hợp hệ thống: '
  'cổng thanh toán trực tuyến (VNPay), đơn vị vận chuyển (Giao Hàng Nhanh – GHN) và dịch vụ gửi email, nhằm giảm thao tác nhập lại dữ liệu và đối chiếu thủ công.')
H(4, '1.1.2. Phạm vi khảo sát')
P('**a. Trong phạm vi**', indent=False)
P('Dự án tập trung khảo sát hoạt động kinh doanh và quản lý tại một cửa hàng SweetMart, bao gồm:')
BL(['**Trong phạm vi:** quản lý danh mục, sản phẩm bánh kẹo (hình ảnh, giá bán, khối lượng, thương hiệu); nhập kho theo lô và hạn sử dụng; đăng ký, đăng nhập; '
    'tìm kiếm, giỏ hàng, đặt hàng; thanh toán COD và thanh toán trực tuyến qua VNPay; tính phí và tạo vận đơn qua GHN; xử lý và theo dõi trạng thái đơn hàng; '
    'mã giảm giá; đánh giá sản phẩm; gửi email thông báo; báo cáo doanh thu, tồn kho và hàng cận hạn sử dụng; phân quyền người dùng.',
    '**Ngoài phạm vi:** sản xuất bánh, quản lý nhà cung cấp và công nợ, kế toán – hóa đơn điện tử, tính lương nhân viên, nhiều chi nhánh/nhiều kho, '
    'ứng dụng di động native, ví điện tử khác (MoMo, ZaloPay), chương trình tích điểm thành viên.'])
H(4, '1.1.3. Các bên liên quan')
P('Các bên liên quan đến hoạt động kinh doanh và sử dụng website SweetMart bao gồm:')
T(['Bên liên quan', 'Số lượng', 'Vai trò và trách nhiệm'],
  [['Chủ cửa hàng (Quản lý)', '1 người', 'Quản lý sản phẩm, giá bán, khuyến mãi, theo dõi báo cáo doanh thu, tồn kho; phê duyệt và nghiệm thu hệ thống.'],
   ['Nhân viên bán hàng', '2 người', 'Tiếp nhận, xác nhận, hủy đơn; tư vấn khách; đóng gói, tạo vận đơn và theo dõi giao hàng.'],
   ['Nhân viên kho', '1 người', 'Nhập hàng theo lô (số lượng, ngày sản xuất, hạn sử dụng), kiểm kê, xử lý hàng cận date.'],
   ['Quản trị hệ thống', '1 người (thành viên nhóm)', 'Tạo tài khoản nội bộ, phân quyền, cấu hình khóa tích hợp, sao lưu dữ liệu.'],
   ['Khách hàng', 'Không cố định', 'Tìm kiếm, xem sản phẩm, đặt hàng, thanh toán, theo dõi đơn và đánh giá sản phẩm.'],
   ['Đối tác tích hợp', 'VNPay, GHN, dịch vụ Email', 'Cung cấp API thanh toán, vận chuyển và gửi email cho hệ thống.']],
  [3.6, 2.8, 9.5])
P('Mỗi nhân viên được cấp một tài khoản riêng để hệ thống ghi nhận được ai đã xác nhận, hủy hay cập nhật đơn hàng. Chủ cửa hàng dùng tài khoản Quản lý; '
  'tài khoản Quản trị chỉ dùng cho việc vận hành kỹ thuật.')
H(4, '1.1.4. Phương pháp khảo sát')
P('Nhóm thực hiện khảo sát bằng phương pháp **phỏng vấn** chủ cửa hàng và nhân viên (thành viên đóng vai Product Owner đại diện cho chủ cửa hàng), kết hợp **quan sát** một ca bán hàng '
  'và quá trình xử lý đơn online qua Facebook, Zalo. Ngoài ra, nhóm lập **phiếu khảo sát trực tuyến** (Google Form) dành cho khách hàng về thói quen mua bánh kẹo online '
  'và phương thức thanh toán ưa thích, đồng thời tham khảo các website bán lẻ thực phẩm phổ biến để xác định những chức năng chuẩn.')
P('Trước khi khảo sát, nhóm chuẩn bị bộ câu hỏi về: cách nhận đơn, cách kiểm tra tồn kho và hạn sử dụng, cách đối chiếu thanh toán, cách giao hàng, '
  'nhu cầu khuyến mãi và báo cáo. Trong quá trình khảo sát, nhóm ghi nhận các bước thực hiện, thời gian xử lý và những tình huống thường xảy ra sai sót.')
P('Sau khi khảo sát, nhóm tổng hợp các vấn đề còn tồn tại trong quy trình hiện tại (As-Is), làm cơ sở xác định các điểm đau (Pain Points) và đề xuất quy trình mới (To-Be).')

H(3, '1.2. Hiện trạng (As-Is)')
P('Hiện tại, SweetMart bán hàng trực tiếp tại quầy và nhận đơn qua Fanpage Facebook, Zalo. Thông tin sản phẩm, giá bán, đơn hàng và tồn kho được ghi chép bằng sổ tay và file Excel; '
  'hạn sử dụng chỉ được kiểm tra khi nhân viên nhìn trực tiếp trên bao bì. Việc đối chiếu chuyển khoản và tạo đơn giao hàng đều làm thủ công.')
H(4, '1.2.1. Quy trình bán hàng hiện tại')
NUM(['Khách hàng xem hình ảnh sản phẩm trên Fanpage, Zalo hoặc đến trực tiếp cửa hàng. Khi có nhu cầu, khách nhắn tin hỏi giá, khối lượng, hạn sử dụng và tình trạng còn hàng.',
     'Nhân viên tiếp nhận tin nhắn, kiểm tra kệ hàng hoặc file Excel để xác nhận còn hàng, xem hạn sử dụng trên bao bì rồi báo giá cho khách.',
     'Khách chốt sản phẩm, số lượng; nhân viên báo thêm phí giao hàng ước tính và thời gian giao. Nếu khách mua làm quà, nhân viên ghi chú yêu cầu gói quà.',
     'Nhân viên ghi họ tên, số điện thoại, địa chỉ, sản phẩm, số lượng vào sổ hoặc file Excel đơn hàng.',
     'Khách chọn thanh toán khi nhận hàng (COD) hoặc chuyển khoản. Với chuyển khoản, nhân viên phải mở ứng dụng ngân hàng, dò sao kê theo nội dung chuyển khoản để đối chiếu.',
     'Nhân viên lấy hàng, đóng gói, sau đó mở ứng dụng của đơn vị vận chuyển và nhập lại toàn bộ thông tin người nhận để tạo đơn giao hàng.',
     'Khi khách hỏi tình trạng đơn, nhân viên phải tra mã vận đơn trên ứng dụng vận chuyển rồi nhắn lại cho khách.',
     'Cuối ngày, nhân viên trừ số lượng đã bán trong file Excel; cuối tháng, chủ cửa hàng tự tổng hợp doanh thu và kiểm kê hàng hết hạn để hủy.'])
H(4, '1.2.2. Điểm đau (Pain points) ghi nhận khi khảo sát')
T(['Mã', 'Vấn đề', 'Bước', 'Hậu quả'],
  [['P01', 'Phản hồi tin nhắn chậm, phụ thuộc người trực (30–60 phút giờ cao điểm)', '1, 2', 'Mất khách, nhất là mùa Tết, Trung thu'],
   ['P02', 'Tồn kho chỉ cập nhật cuối ngày, không đồng bộ giữa quầy và online', '2, 8', 'Bán hàng đã hết, sai lệch số liệu'],
   ['P03', 'Không quản lý hạn sử dụng theo lô, không có cảnh báo cận date', '2, 8', 'Hàng hết hạn phải hủy; rủi ro an toàn thực phẩm'],
   ['P04', 'Ghi đơn thủ công bằng sổ/Excel', '4', 'Sót đơn, ghi sai số lượng, địa chỉ'],
   ['P05', 'Đối chiếu chuyển khoản thủ công qua sao kê', '5', 'Tốn thời gian, nhầm đơn, xác nhận chậm'],
   ['P06', 'Nhập lại thông tin khi tạo đơn giao hàng', '6', 'Sai địa chỉ, giao chậm'],
   ['P07', 'Khách không tự theo dõi được đơn', '7', 'Nhân viên mất thời gian trả lời'],
   ['P08', 'Không có báo cáo doanh thu, sản phẩm bán chạy', '8', 'Khó quyết định nhập hàng và khuyến mãi']],
  [1.3, 6.8, 1.5, 6.3], center_cols=(0, 2))
P('Qua khảo sát, có thể thấy khó khăn của cửa hàng chủ yếu xuất phát từ việc quản lý thông tin sản phẩm, hạn sử dụng, đơn hàng và thanh toán bằng phương pháp thủ công, '
  'đồng thời các hệ thống liên quan (ngân hàng, đơn vị vận chuyển) không được kết nối với nhau nên dữ liệu phải nhập lại nhiều lần.')

H(3, '1.3. Quy trình đề xuất (To-Be)')
H(4, '1.3.1. Tổng quan giải pháp')
P('Dựa trên những khó khăn trong quy trình hiện tại, nhóm đề xuất xây dựng **website bán bánh kẹo SweetMart** gồm hai khu vực: website cho khách hàng và trang quản trị cho cửa hàng. '
  'Website quản lý tập trung sản phẩm, tồn kho theo lô – hạn sử dụng, đơn hàng, thanh toán và khuyến mãi trên một cơ sở dữ liệu duy nhất.')
P('Khách hàng có thể tìm kiếm, xem chi tiết sản phẩm (kèm hạn sử dụng lô gần nhất), thêm vào giỏ hàng, đặt hàng, áp mã giảm giá, thanh toán COD hoặc VNPay và theo dõi trạng thái đơn. '
  'Hệ thống **tích hợp VNPay** để tự động xác nhận thanh toán, **tích hợp GHN** để tính phí và tạo vận đơn, **tích hợp dịch vụ email** để gửi thông báo, '
  'nhờ đó loại bỏ các bước đối chiếu và nhập lại thủ công.')
H(4, '1.3.2. Quy trình hoạt động đề xuất')
NUM(['Khách hàng truy cập website, tìm kiếm theo tên, danh mục, thương hiệu, khoảng giá; xem hình ảnh, giá, khối lượng, hạn sử dụng và tình trạng còn hàng mà không cần nhắn tin hỏi.',
     'Khách thêm sản phẩm vào giỏ hàng; hệ thống kiểm tra số lượng không vượt tồn kho còn hạn.',
     'Khách đăng nhập, chọn địa chỉ giao hàng; hệ thống gọi GHN API để tính phí vận chuyển, khách nhập mã giảm giá (nếu có) và chọn phương thức thanh toán.',
     'Hệ thống tạo đơn với mã đơn duy nhất, giữ tồn kho theo nguyên tắc lô hết hạn trước xuất trước (FEFO) và gửi email xác nhận.',
     'Nếu chọn VNPay, khách được chuyển sang cổng VNPay để thanh toán; VNPay gửi kết quả (IPN) về hệ thống và trạng thái thanh toán được cập nhật tự động.',
     'Nhân viên nhận đơn trên trang quản trị, kiểm tra thông tin và xác nhận đơn.',
     'Nhân viên đóng gói, nhấn "Tạo vận đơn" – hệ thống gửi thông tin sang GHN và lưu mã vận đơn, đơn chuyển sang "Đang giao".',
     'Trạng thái giao hàng được GHN cập nhật về hệ thống; khách theo dõi đơn trong tài khoản: Chờ xác nhận → Đã xác nhận → Đang đóng gói → Đang giao → Đã giao.',
     'Hệ thống tự động tổng hợp doanh thu, sản phẩm bán chạy, tồn kho và cảnh báo các lô sắp hết hạn để chủ cửa hàng ra quyết định nhập hàng, khuyến mãi xả hàng.'])
H(4, '1.3.3. Thay đổi về vai trò')
BL(['**Chủ cửa hàng (Quản lý):** quản lý sản phẩm, giá, khuyến mãi; xem báo cáo được tổng hợp tự động thay vì thống kê thủ công cuối tháng.',
    '**Nhân viên bán hàng:** không còn trực tin nhắn để báo giá, đối chiếu sao kê hay nhập lại địa chỉ; tập trung xác nhận, đóng gói và theo dõi đơn trên một màn hình.',
    '**Nhân viên kho:** nhập hàng theo lô có hạn sử dụng; nhận danh sách cảnh báo cận date thay vì kiểm tra bằng mắt.',
    '**Quản trị hệ thống:** vai trò mới – quản lý tài khoản, phân quyền, khóa tích hợp và sao lưu.',
    '**Khách hàng:** chủ động tìm hiểu, đặt hàng, thanh toán và theo dõi đơn 24/7 mà không cần liên hệ cửa hàng.'])

H(2, '2. Hướng đi')
H(3, '2.1. Phát biểu vấn đề (Problem Statement)')
P('Cửa hàng SweetMart chưa có hệ thống thống nhất để bán hàng trực tuyến và quản lý hàng hóa có hạn sử dụng. Đơn hàng nhận qua tin nhắn, tồn kho và hạn sử dụng ghi bằng Excel, '
  'thanh toán và giao hàng phải đối chiếu, nhập liệu thủ công trên các hệ thống rời rạc. Điều này khiến cửa hàng phản hồi khách chậm, tồn kho sai lệch, có hàng hết hạn phải hủy '
  'và chủ cửa hàng thiếu số liệu để ra quyết định.')
P('Vì vậy, dự án hướng đến xây dựng website bán bánh kẹo kết hợp quản lý kho theo lô – hạn sử dụng và tích hợp thanh toán VNPay, vận chuyển GHN, email, '
  'giúp tự động hóa luồng "đặt hàng – thanh toán – giao hàng" và cung cấp báo cáo cho chủ cửa hàng.')
H(3, '2.2. Đặt mục tiêu đo được (SMART Goals)')
P('Dựa trên các vấn đề đã xác định, dự án đặt ra các mục tiêu cần đạt trong vòng 3 tháng sau khi website được đưa vào sử dụng:')
T(['Mã', 'Mục tiêu', 'Chỉ tiêu đo lường', 'Vấn đề liên quan'],
  [['G01', 'Rút ngắn thời gian xử lý đơn', 'Thời gian từ lúc khách đặt đến khi đơn được xác nhận ≤ 10 phút trong giờ làm việc (hiện tại 30–60 phút)', 'P01, P04'],
   ['G02', 'Tồn kho chính xác', 'Sai lệch giữa tồn kho hệ thống và kiểm kê thực tế < 2%', 'P02'],
   ['G03', 'Giảm hàng hết hạn phải hủy', 'Giá trị hàng hủy do hết hạn giảm ≥ 50% so với trước khi dùng hệ thống', 'P03'],
   ['G04', 'Tự động đối soát thanh toán', '100% đơn thanh toán VNPay được xác nhận tự động, không cần dò sao kê', 'P05'],
   ['G05', 'Loại bỏ nhập lại thông tin giao hàng', '100% vận đơn được tạo từ hệ thống qua GHN API', 'P06, P07'],
   ['G06', 'Có số liệu kinh doanh', 'Báo cáo doanh thu, top sản phẩm, tồn kho xem được trong ≤ 5 giây, theo ngày/tuần/tháng', 'P08']],
  [1.3, 4, 7.6, 3], center_cols=(0, 3))
H(3, '2.3. Đánh giá tính khả thi (Feasibility Assessment)')
BL(['**Khả thi về kỹ thuật (Technical): Cao.** Website được xây dựng bằng ReactJS, ASP.NET Core Web API và SQL Server – các công nghệ phổ biến, nhóm đã học. '
    'VNPay và GHN đều cung cấp môi trường thử nghiệm (sandbox) miễn phí, có tài liệu API rõ ràng. Phần rủi ro nhất (tích hợp) sẽ được kiểm chứng sớm bằng PoC.',
    '**Khả thi về vận hành (Operational): Cao.** Cửa hàng quy mô nhỏ, nhân viên đã quen dùng điện thoại, máy tính và mạng xã hội; giao diện quản trị đơn giản, có hướng dẫn sử dụng.',
    '**Khả thi về kinh tế (Financial): Tốt.** Sử dụng công cụ miễn phí (GitLab, Docker, Visual Studio Code); chi phí chủ yếu là tên miền và máy chủ (khoảng 1–2 triệu đồng/năm). '
    'Phí giao dịch VNPay chỉ phát sinh khi có doanh thu.',
    '**Khả thi về thời gian (Schedule): Đạt.** Dự án thực hiện trong 15 tuần theo Scrum: Sprint 0 (2 tuần), 5 Sprint × 2 tuần và 3 tuần hoàn thiện, bảo vệ.'])
H(3, '2.4. Đánh giá rủi ro và biện pháp khắc phục')
T(['Mã', 'Rủi ro', 'Mức độ', 'Biện pháp khắc phục'],
  [['R01', 'Tích hợp VNPay lỗi: sai chữ ký, không nhận được IPN, sandbox thay đổi', 'Cao', 'Làm PoC trong Sprint 0; tách lớp VNPayClient; ghi log toàn bộ request/response; có màn hình đối soát thủ công dự phòng'],
   ['R02', 'GHN API không phản hồi hoặc thay đổi', 'Trung bình', 'Dùng phí ship mặc định khi lỗi; cho phép nhân viên tạo vận đơn thủ công và nhập mã'],
   ['R03', 'Hai khách cùng mua sản phẩm chỉ còn ít hàng → bán vượt tồn kho', 'Cao', 'Trừ tồn kho trong transaction, khóa bản ghi lô hàng; kiểm thử đồng thời'],
   ['R04', 'Bán nhầm lô đã hết hạn', 'Cao', 'Xuất kho theo FEFO, loại lô hết hạn khỏi tồn khả dụng, cảnh báo cận date'],
   ['R05', 'Lộ thông tin khách hàng, mật khẩu, khóa bí mật tích hợp', 'Cao', 'Băm mật khẩu bcrypt, HTTPS, JWT; khóa bí mật lưu ở biến môi trường, không đưa lên Git'],
   ['R06', 'Thành viên chưa vững công nghệ', 'Trung bình', 'Học trong Sprint 0, lập trình cặp, review code qua Merge Request'],
   ['R07', 'Phình phạm vi (thêm ví điện tử, tích điểm...)', 'Trung bình', 'Product Owner chốt MVP; yêu cầu mới đưa vào Backlog, xếp ưu tiên MoSCoW'],
   ['R08', 'Trễ tiến độ do lịch thi, môn học khác', 'Trung bình', 'Sprint 2 tuần, họp Daily Scrum, theo dõi Burndown; dự phòng 3 tuần cuối'],
   ['R09', 'Xung đột mã nguồn, mất code', 'Thấp', 'GitLab, nhánh theo tính năng, Merge Request, CI'],
   ['R10', 'Thiếu dữ liệu sản phẩm mẫu (ảnh, giá, hạn sử dụng)', 'Thấp', 'PO chuẩn bị 50–100 sản phẩm mẫu trong Sprint 1'],
   ['R11', 'Triển khai lên máy chủ lỗi sát ngày bảo vệ', 'Trung bình', 'Đóng gói Docker từ Sprint 2; triển khai thử mỗi Sprint'],
   ['R12', 'Email xác nhận rơi vào thư rác hoặc bị giới hạn gửi', 'Thấp', 'Dùng SMTP có xác thực, gửi bất đồng bộ; thông tin đơn vẫn xem được trên website']],
  [1.3, 5.6, 2.2, 6.8], center_cols=(0, 2))

H(2, '3. Định hình sản phẩm và dự án (Product & Project Definition)')
H(3, '3.1. Tầm nhìn sản phẩm (Product Vision)')
P('Website SweetMart được xây dựng nhằm mang đến cho khách hàng yêu thích bánh kẹo một nơi mua sắm trực tuyến **nhanh, minh bạch về giá và hạn sử dụng**: '
  'khách tự tìm sản phẩm, đặt hàng, thanh toán online và theo dõi đơn 24/7.')
P('Đối với cửa hàng, website là hệ thống quản lý tập trung sản phẩm, kho theo lô – hạn sử dụng, đơn hàng, khuyến mãi và doanh thu; được **kết nối trực tiếp với VNPay, GHN và email** '
  'để tự động hóa thanh toán, giao hàng và thông báo. Khác với việc bán qua tin nhắn mạng xã hội, SweetMart giảm tối đa thao tác thủ công, hạn chế hàng hết hạn và giúp chủ cửa hàng ra quyết định dựa trên số liệu.')
H(3, '3.2. Phạm vi MVP')
P('Để sớm đưa website vào sử dụng và kiểm chứng hiệu quả, dự án được chia thành hai giai đoạn. MVP (Giai đoạn 1) tập trung vào luồng cốt lõi '
  '"tìm sản phẩm → đặt hàng → thanh toán → giao hàng" cùng phần quản lý kho theo hạn sử dụng – điểm đau lớn nhất của cửa hàng.')
P('Các chức năng trong MVP (Giai đoạn 1):')
BL(['**Quản lý tài khoản:** đăng ký, đăng nhập, quên mật khẩu, sổ địa chỉ; phân quyền Khách hàng, Nhân viên, Quản lý, Quản trị.',
    '**Quản lý sản phẩm:** danh mục, sản phẩm, hình ảnh, giá bán, khối lượng, thương hiệu.',
    '**Quản lý kho theo lô:** nhập lô có ngày sản xuất, hạn sử dụng; xuất kho FEFO; cảnh báo lô cận date và sản phẩm sắp hết.',
    '**Tìm kiếm và mua hàng:** tìm kiếm, lọc, xem chi tiết, giỏ hàng, đặt hàng, áp mã giảm giá.',
    '**Thanh toán:** COD và thanh toán trực tuyến qua VNPay (tự động xác nhận bằng IPN).',
    '**Vận chuyển:** tính phí và tạo vận đơn qua GHN API; cập nhật trạng thái giao.',
    '**Quản lý đơn hàng:** xác nhận, hủy, cập nhật trạng thái; khách theo dõi và hủy đơn chờ xác nhận.',
    '**Thông báo và báo cáo:** email xác nhận đơn; báo cáo doanh thu, top sản phẩm, tồn kho.'])
P('Các chức năng dự kiến phát triển sau MVP (Giai đoạn 2):')
BL(['Thanh toán qua ví điện tử MoMo, ZaloPay.', 'Chương trình tích điểm, hạng thành viên.', 'Gợi ý sản phẩm theo lịch sử mua hàng.',
    'Bán tại quầy (POS) dùng chung kho với website.', 'Thông báo qua SMS/Zalo OA.', 'Ứng dụng di động.'])
H(3, '3.3. Bằng chứng khái niệm (Proof of Concept – PoC)')
P('Đối với SweetMart, vấn đề kỹ thuật cần kiểm chứng sớm là **khả năng tích hợp với hệ thống bên ngoài** (VNPay, GHN) và **giữ tồn kho chính xác theo lô hạn sử dụng** khi có nhiều đơn đồng thời. '
  'Đây là các nội dung gắn với rủi ro R01, R02, R03, R04.')
P('**Mục tiêu PoC:** chứng minh hệ thống có thể tạo và xác thực giao dịch VNPay, gọi được API của GHN, và không bán vượt tồn kho hoặc bán lô đã hết hạn.')
P('**Kịch bản thực hiện (Test Case):**', indent=False)
BL(['**Kịch bản 1 – Thanh toán VNPay sandbox:** tạo đơn SM000001 trị giá 250.000đ, chọn VNPay; hệ thống tạo URL có chữ ký HMAC-SHA512, thanh toán bằng thẻ test của VNPay; '
    'IPN gửi về được xác thực chữ ký, đúng số tiền, đơn chuyển sang "Chờ xác nhận".',
    '**Kịch bản 2 – IPN giả mạo:** gửi IPN với chữ ký sai hoặc số tiền khác; hệ thống phải từ chối (RspCode 97/04) và không cập nhật đơn.',
    '**Kịch bản 3 – GHN API:** gọi API tính phí cho địa chỉ tại Hải Phòng với gói 1 kg và tạo một đơn giao hàng thử; hệ thống nhận về phí ship và mã vận đơn.',
    '**Kịch bản 4 – Hai khách đặt cùng lúc:** sản phẩm "Kẹo dẻo trái cây 200g" chỉ còn 1 gói; hai khách đặt đồng thời; chỉ một đơn thành công, tồn kho không âm.',
    '**Kịch bản 5 – Xuất kho FEFO:** sản phẩm có lô A (HSD 01/2027, còn 3) và lô B (HSD 06/2027, còn 10); khách đặt 5 gói → hệ thống lấy 3 từ lô A, 2 từ lô B; lô đã hết hạn không được tính vào tồn.'])
P('**Tiêu chí PoC đạt yêu cầu:**', indent=False)
BL(['Giao dịch VNPay hợp lệ được xác nhận tự động; giao dịch giả mạo bị từ chối.', 'Gọi GHN API thành công, lưu được mã vận đơn.',
    'Không có đơn nào làm tồn kho âm; lô hết hạn không được xuất bán.', 'Toàn bộ request/response tích hợp được ghi log để truy vết.'])
H(3, '3.4. Tuyên ngôn dự án (Project Charter)')
T(['Hạng mục', 'Nội dung'],
  [['Tên dự án', 'Website bán bánh kẹo SweetMart'],
   ['Mục đích', 'Số hóa quy trình bán hàng trực tuyến; quản lý tập trung sản phẩm, kho theo lô – hạn sử dụng, đơn hàng, khuyến mãi; tích hợp thanh toán, vận chuyển và email'],
   ['Mục tiêu', 'G01–G06 (mục 2.2)'],
   ['Phạm vi', 'Theo phạm vi MVP (mục 3.2)'],
   ['Mô hình phát triển', 'Agile / Scrum, Sprint 2 tuần'],
   ['Thời gian', '15 tuần: Sprint 0 (tuần 1–2), Sprint 1–5 (tuần 3–12), bàn giao và bảo vệ (tuần 13–15)'],
   ['Nhóm dự án', 'Product Owner: [Thành viên 1] · Scrum Master: [Thành viên 2] · Developers: [Thành viên 3], [Thành viên 4], [Thành viên 5]'],
   ['Công nghệ', 'ReactJS · ASP.NET Core Web API · SQL Server · Docker · GitLab'],
   ['Hệ thống tích hợp', 'VNPay (thanh toán), GHN (vận chuyển), SMTP (email)'],
   ['Mốc chính', 'Tuần 2: chốt Backlog, kiến trúc, ERD · Tuần 8: demo giữa kỳ (đặt hàng + VNPay) · Tuần 12: phát hành v1.0 · Tuần 15: bảo vệ'],
   ['Tiêu chí thành công', 'Toàn bộ User Story Must have đạt Definition of Done; kịch bản PoC đạt; UAT được Product Owner chấp nhận'],
   ['Rủi ro chính', 'R01, R03, R04, R05 (mục 2.4)']],
  [3.8, 12.1])

# =====================================================================================
#                                    BƯỚC 2
# =====================================================================================
doc.add_page_break()
H(1, 'BƯỚC 2. ĐẶC TẢ YÊU CẦU HỆ THỐNG (REQUIREMENTS)')
H(2, '1. Phân loại yêu cầu hệ thống')
H(3, '1.1. Yêu cầu chức năng (Functional Requirements – FR)')
P('Yêu cầu chức năng xác định những việc website SweetMart phải thực hiện để đáp ứng nhu cầu mua sắm của khách hàng và hỗ trợ cửa hàng quản lý bán hàng, kho và tích hợp với hệ thống bên ngoài.')
FR = [
    ('Nhóm 1. Quản lý tài khoản và phân quyền', [
        'FR01 – Đăng ký, đăng nhập, quên mật khẩu: khách hàng đăng ký bằng email, đăng nhập, đăng xuất và đặt lại mật khẩu qua email.',
        'FR02 – Quản lý hồ sơ và sổ địa chỉ: khách hàng cập nhật thông tin cá nhân, lưu nhiều địa chỉ giao hàng, chọn địa chỉ mặc định.',
        'FR03 – Phân quyền và quản lý tài khoản nội bộ: hệ thống phân quyền theo bốn vai trò Khách hàng, Nhân viên, Quản lý, Quản trị; Quản trị tạo, khóa, mở tài khoản nhân viên.']),
    ('Nhóm 2. Quản lý sản phẩm', [
        'FR04 – Quản lý danh mục và sản phẩm: Quản lý thêm, sửa, ẩn danh mục (có danh mục cha – con) và sản phẩm (tên, thương hiệu, giá, khối lượng, đơn vị tính, mô tả, hình ảnh).',
        'FR05 – Tìm kiếm, lọc và xem chi tiết: khách tìm theo tên (không phân biệt dấu), lọc theo danh mục, thương hiệu, khoảng giá, sắp xếp; xem chi tiết kèm hạn sử dụng lô gần nhất và tình trạng còn hàng.']),
    ('Nhóm 3. Quản lý kho theo lô và hạn sử dụng', [
        'FR06 – Nhập kho theo lô: nhân viên kho nhập lô hàng với số lượng, ngày sản xuất, hạn sử dụng; tồn kho sản phẩm tự cộng.',
        'FR07 – Giữ và xuất kho theo FEFO: khi tạo đơn, hệ thống giữ hàng từ lô có hạn sử dụng gần nhất còn hạn; hoàn lại khi đơn bị hủy hoặc giao thất bại.',
        'FR08 – Cảnh báo cận date và sắp hết hàng: liệt kê lô còn ≤ 30 ngày hạn sử dụng, sản phẩm có tồn dưới ngưỡng.']),
    ('Nhóm 4. Giỏ hàng và đặt hàng', [
        'FR09 – Quản lý giỏ hàng: thêm, sửa số lượng, xóa sản phẩm; lưu giỏ theo tài khoản; kiểm tra không vượt tồn kho.',
        'FR10 – Đặt hàng: chọn địa chỉ, xem phí ship, chọn phương thức thanh toán, ghi chú (gói quà...), tạo đơn có mã duy nhất.',
        'FR11 – Áp dụng mã giảm giá: kiểm tra điều kiện mã (thời hạn, số lượt, giá trị đơn tối thiểu) và tính tiền giảm.']),
    ('Nhóm 5. Thanh toán (tích hợp VNPay)', [
        'FR12 – Thanh toán khi nhận hàng (COD): ghi nhận đơn COD, nhân viên xác nhận đã thu tiền khi giao thành công.',
        'FR13 – Thanh toán trực tuyến VNPay: tạo URL thanh toán có chữ ký, chuyển khách sang VNPay, nhận và xác thực IPN, cập nhật trạng thái thanh toán tự động.']),
    ('Nhóm 6. Xử lý đơn hàng và giao hàng (tích hợp GHN)', [
        'FR14 – Xử lý đơn hàng: nhân viên xác nhận, hủy (kèm lý do), cập nhật trạng thái; mọi thay đổi được lưu lịch sử.',
        'FR15 – Tính phí và tạo vận đơn GHN: gọi GHN API tính phí khi đặt hàng, tạo vận đơn khi đóng gói xong, nhận cập nhật trạng thái giao.',
        'FR16 – Theo dõi và hủy đơn của khách: khách xem lịch sử, trạng thái, mã vận đơn; hủy được đơn đang "Chờ xác nhận".']),
    ('Nhóm 7. Khuyến mãi, đánh giá và thông báo', [
        'FR17 – Quản lý mã giảm giá: Quản lý tạo mã theo % hoặc số tiền, đơn tối thiểu, thời hạn, số lượt.',
        'FR18 – Đánh giá sản phẩm: khách đánh giá 1–5 sao và bình luận cho sản phẩm trong đơn đã giao.',
        'FR19 – Gửi email thông báo: email xác nhận đơn, thay đổi trạng thái đơn, đặt lại mật khẩu.']),
    ('Nhóm 8. Báo cáo thống kê', [
        'FR20 – Báo cáo doanh thu: doanh thu theo ngày, tuần, tháng; số đơn theo trạng thái; top sản phẩm bán chạy.',
        'FR21 – Báo cáo tồn kho: tồn theo sản phẩm, theo lô; danh sách lô cận date, hàng đã hết hạn.']),
]
for g, items in FR:
    P(f'**{g}**', indent=False)
    for it in items:
        code, rest = it.split(':', 1)
        P(f'**{code}:**{rest}')
H(3, '1.2. Yêu cầu phi chức năng (Non-Functional Requirements – NFR)')
P('Yêu cầu phi chức năng xác định các tiêu chí về hiệu năng, bảo mật, độ tin cậy của tích hợp và khả năng sử dụng, bảo đảm website đáp ứng các chức năng trong điều kiện vận hành thực tế.')
T(['Mã', 'Nhóm yêu cầu', 'Nội dung và tiêu chí'],
  [['NFR01', 'Hiệu năng', 'Trang danh sách, chi tiết sản phẩm tải ≤ 3 giây; 95% API phản hồi ≤ 1 giây (không tính thời gian chờ VNPay, GHN).'],
   ['NFR02', 'Khả năng chịu tải', 'Phục vụ đồng thời ≥ 100 người dùng không phát sinh lỗi (kiểm tra bằng k6/JMeter).'],
   ['NFR03', 'Bảo mật dữ liệu', 'Mật khẩu băm bcrypt; truyền dữ liệu qua HTTPS; không lưu thông tin thẻ ngân hàng.'],
   ['NFR04', 'Bảo mật ứng dụng', 'Chống SQL Injection, XSS, CSRF; khóa đăng nhập 15 phút sau 5 lần sai liên tiếp.'],
   ['NFR05', 'Phân quyền', 'Kiểm tra quyền ở phía máy chủ cho mọi API; khách chỉ xem/sửa dữ liệu của mình; truy cập trái quyền trả về lỗi 403.'],
   ['NFR06', 'Độ tin cậy tích hợp', 'IPN VNPay xử lý idempotent (nhận trùng không ghi nhận hai lần); gọi GHN có timeout 10 giây và thử lại; lỗi tích hợp không làm mất đơn.'],
   ['NFR07', 'Truy vết', 'Ghi log mọi request/response với VNPay, GHN và các thao tác đổi trạng thái đơn, lưu tối thiểu 90 ngày.'],
   ['NFR08', 'Bảo mật tích hợp', 'Khóa bí mật VNPay, token GHN, mật khẩu SMTP lưu trong biến môi trường, không đưa vào mã nguồn.'],
   ['NFR09', 'Khả dụng', 'Giao diện responsive trên điện thoại (≥ 360px), máy tính bảng và máy tính.'],
   ['NFR10', 'Dễ sử dụng', 'Khách mới hoàn tất một đơn hàng trong ≤ 3 phút mà không cần hướng dẫn.'],
   ['NFR11', 'Tính sẵn sàng', 'Thời gian hoạt động ≥ 99%; sao lưu cơ sở dữ liệu hằng ngày, giữ 7 bản gần nhất.'],
   ['NFR12', 'Tương thích', 'Hoạt động tốt trên Chrome, Edge, Firefox, Safari phiên bản mới.']],
  [1.7, 3.4, 10.8], center_cols=(0,))
H(3, '1.3. Quy tắc nghiệp vụ (Business Rules – BR)')
P('Quy tắc nghiệp vụ xác định các điều kiện cần tuân thủ khi bán hàng, quản lý kho, thanh toán và xử lý đơn trên website SweetMart, được xây dựng từ kết quả khảo sát và đặc thù hàng thực phẩm có hạn sử dụng.')
BL(['**BR01 – Quy tắc hạn sử dụng:** không bán lô hàng đã hết hạn; lô hết hạn không được tính vào tồn kho khả dụng.',
    '**BR02 – Quy tắc xuất kho FEFO:** khi giữ hàng cho đơn, ưu tiên lô có hạn sử dụng gần nhất (First Expired, First Out).',
    '**BR03 – Quy tắc cận date:** lô còn ≤ 30 ngày hạn sử dụng được đánh dấu "cận date" và hiển thị cảnh báo cho nhân viên, quản lý.',
    '**BR04 – Quy tắc tồn kho:** số lượng đặt không vượt tổng tồn khả dụng; tồn kho được giữ khi tạo đơn và hoàn lại khi đơn bị hủy hoặc giao thất bại.',
    '**BR05 – Quy tắc phí vận chuyển:** phí ship lấy từ GHN; miễn phí cho đơn có tiền hàng sau giảm từ 300.000đ.',
    '**BR06 – Quy tắc mã giảm giá:** mỗi đơn dùng tối đa 1 mã; mỗi khách dùng một mã tối đa 1 lần; mã phải còn hạn, còn lượt và đơn đạt giá trị tối thiểu.',
    '**BR07 – Quy tắc COD:** đơn COD có tổng thanh toán tối đa 2.000.000đ; đơn lớn hơn phải thanh toán trực tuyến.',
    '**BR08 – Quy tắc thanh toán VNPay:** chỉ ghi nhận thanh toán khi IPN hợp lệ (đúng chữ ký, đúng mã đơn, đúng số tiền); đơn không thanh toán trong 15 phút bị hủy tự động.',
    '**BR09 – Quy tắc hủy đơn:** khách chỉ được hủy đơn ở trạng thái "Chờ xác nhận"; sau đó chỉ nhân viên được hủy và phải ghi lý do; đơn đã thanh toán bị hủy sẽ được hoàn tiền.',
    '**BR10 – Quy tắc chuyển trạng thái:** đơn đi theo thứ tự Chờ xác nhận → Đã xác nhận → Đang đóng gói → Đang giao → Đã giao; không được bỏ qua bước.',
    '**BR11 – Quy tắc giá:** đơn giá trong đơn hàng được lưu tại thời điểm đặt, không đổi khi giá sản phẩm thay đổi.',
    '**BR12 – Quy tắc đánh giá:** khách chỉ đánh giá sản phẩm có trong đơn "Đã giao" của mình, mỗi sản phẩm trong một đơn đánh giá một lần.',
    '**BR13 – Quy tắc bảo mật và phân quyền:** khách chỉ truy cập thông tin của mình; nhân viên không xem được báo cáo doanh thu; chỉ Quản trị được tạo tài khoản và phân quyền.'])

H(2, '2. Tổ chức yêu cầu (Product Backlog & MoSCoW)')
H(3, '2.1. Danh sách Product Backlog')
PB = [
    ['E1. Tài khoản và phân quyền', 'US01', 'Là khách hàng, tôi muốn đăng ký và đăng nhập để đặt hàng và theo dõi đơn của mình.', 'Must have'],
    ['', 'US02', 'Là khách hàng, tôi muốn đặt lại mật khẩu qua email khi quên.', 'Should have'],
    ['', 'US03', 'Là quản trị, tôi muốn tạo tài khoản nhân viên và phân quyền để mỗi người chỉ dùng chức năng của mình.', 'Must have'],
    ['', 'US04', 'Là khách hàng, tôi muốn lưu nhiều địa chỉ giao hàng để đặt hàng nhanh hơn.', 'Could have'],
    ['E2. Sản phẩm', 'US05', 'Là quản lý, tôi muốn quản lý danh mục và sản phẩm để thông tin trên website luôn đúng.', 'Must have'],
    ['', 'US06', 'Là khách hàng, tôi muốn xem sản phẩm theo danh mục để chọn bánh kẹo phù hợp.', 'Must have'],
    ['', 'US07', 'Là khách hàng, tôi muốn tìm kiếm, lọc và xem chi tiết sản phẩm (kèm hạn sử dụng) để quyết định mua.', 'Must have'],
    ['E3. Kho và hạn sử dụng', 'US08', 'Là nhân viên kho, tôi muốn nhập kho theo lô có hạn sử dụng để quản lý hàng chính xác.', 'Must have'],
    ['', 'US09', 'Là quản lý, tôi muốn hệ thống giữ hàng theo FEFO khi có đơn để không bán vượt tồn kho hay bán hàng hết hạn.', 'Must have'],
    ['', 'US10', 'Là quản lý, tôi muốn nhận cảnh báo lô cận date và hàng sắp hết để xử lý kịp thời.', 'Should have'],
    ['E4. Giỏ hàng và đặt hàng', 'US11', 'Là khách hàng, tôi muốn thêm, sửa, xóa sản phẩm trong giỏ để chuẩn bị đặt hàng.', 'Must have'],
    ['', 'US12', 'Là khách hàng, tôi muốn đặt hàng và thanh toán khi nhận hàng (COD).', 'Must have'],
    ['', 'US13', 'Là khách hàng, tôi muốn xem trạng thái và hủy đơn đang chờ xác nhận.', 'Must have'],
    ['', 'US14', 'Là khách hàng, tôi muốn nhập mã giảm giá khi đặt hàng để được giảm tiền.', 'Should have'],
    ['E5. Tích hợp thanh toán và vận chuyển', 'US15', 'Là khách hàng, tôi muốn thanh toán qua VNPay để trả tiền ngay khi đặt hàng.', 'Must have'],
    ['', 'US16', 'Là khách hàng, tôi muốn phí vận chuyển được tính tự động theo địa chỉ để biết tổng tiền chính xác.', 'Should have'],
    ['', 'US17', 'Là nhân viên, tôi muốn tạo vận đơn GHN từ đơn hàng để không phải nhập lại địa chỉ.', 'Should have'],
    ['', 'US18', 'Là khách hàng, tôi muốn nhận email xác nhận và thông báo trạng thái đơn.', 'Should have'],
    ['E6. Xử lý đơn hàng', 'US19', 'Là nhân viên, tôi muốn xem, xác nhận hoặc hủy đơn mới để xử lý kịp thời.', 'Must have'],
    ['', 'US20', 'Là nhân viên, tôi muốn cập nhật đóng gói, giao hàng, hoàn tất và ghi nhận tiền COD.', 'Must have'],
    ['E7. Khuyến mãi và đánh giá', 'US21', 'Là quản lý, tôi muốn tạo mã giảm giá có điều kiện để chạy khuyến mãi dịp lễ, xả hàng cận date.', 'Should have'],
    ['', 'US22', 'Là khách hàng, tôi muốn đánh giá sản phẩm đã mua.', 'Could have'],
    ['E8. Báo cáo', 'US23', 'Là quản lý, tôi muốn xem báo cáo doanh thu và sản phẩm bán chạy.', 'Should have'],
    ['', 'US24', 'Là quản lý, tôi muốn xem báo cáo tồn kho theo lô và hàng hết hạn.', 'Should have'],
    ['Ngoài phạm vi', 'US25', 'Là khách hàng, tôi muốn thanh toán bằng ví MoMo/ZaloPay và tích điểm thành viên.', "Won't have"],
]
caption('bang', 'Product Backlog của website SweetMart')
T(['Epic', 'Mã Story', 'User Story / Chức năng', 'Ưu tiên'], PB, [3.6, 1.7, 8.2, 2.4], center_cols=(1, 3))
H(3, '2.2. Rà soát và hoàn thiện Product Backlog (Refinement)')
P('Quá trình Refinement tập trung vào các nội dung:')
BL(['**Kiểm tra yêu cầu:** đối chiếu các User Story với FR01–FR21, NFR01–NFR12, BR01–BR13 và quy trình To-Be ở Bước 1.',
    '**Làm rõ nghiệp vụ:** thống nhất cách giữ hàng theo FEFO, điều kiện mã giảm giá, hạn mức COD và thời gian chờ thanh toán VNPay, nhằm khắc phục các điểm đau P02–P06.',
    '**Điều chỉnh mức ưu tiên:** 13 Story Must have phục vụ trực tiếp mục tiêu G01–G05 được làm trước; 9 Story Should have làm sau khi luồng chính ổn định; '
    '2 Story Could have làm nếu còn thời gian; US25 thuộc Won\'t have của giai đoạn này.',
    '**Đánh giá tính khả thi:** ước lượng độ lớn, xác định phụ thuộc (US15 cần US12; US17 cần US19; US09 cần US08) để sắp thứ tự.',
    '**Phân bổ dự kiến theo Sprint:** Sprint 1 – thiết lập dự án, US01, US03, US05, US06; Sprint 2 – US07, US08, US09, US11; Sprint 3 – US12, US13, US15, US19 (demo giữa kỳ); '
    'Sprint 4 – US10, US14, US16, US17, US18, US20; Sprint 5 – US02, US21, US23, US24 (thêm US04, US22 nếu còn thời gian) và sửa lỗi, đóng gói. Chi tiết ước lượng ở Bước 4.',
    '**Chuẩn bị kiểm thử:** viết Acceptance Criteria cho các Story ưu tiên, đặc biệt các chức năng gắn với rủi ro R01, R03, R04 và các kịch bản PoC ở mục 3.3 Bước 1.'])

H(2, '3. Đặc tả chi tiết (User Story & Acceptance Criteria)')
STORY(1, 'US01', 'Đăng ký và đăng nhập', 'Là khách hàng, tôi muốn đăng ký và đăng nhập để đặt hàng và theo dõi đơn của mình.', [
    ('AC1 – Đăng ký hợp lệ', 'Email chưa được đăng ký, mật khẩu từ 8 ký tự có chữ và số.', 'Khách nhập đầy đủ thông tin và chọn "Đăng ký".', 'Hệ thống tạo tài khoản vai trò Khách hàng và tự đăng nhập.'),
    ('AC2 – Email đã tồn tại', 'Email đã được đăng ký trước đó.', 'Khách dùng email đó để đăng ký.', 'Hệ thống báo "Email đã được sử dụng" và không tạo tài khoản.'),
    ('AC3 – Đăng nhập sai nhiều lần', 'Khách đã nhập sai mật khẩu 5 lần liên tiếp.', 'Khách đăng nhập lần thứ 6.', 'Hệ thống tạm khóa đăng nhập 15 phút và thông báo cho khách.')])
STORY(2, 'US03', 'Phân quyền truy cập', 'Là quản trị, tôi muốn tạo tài khoản nhân viên và phân quyền để mỗi người chỉ dùng chức năng của mình.', [
    ('AC1 – Tạo tài khoản nhân viên', 'Quản trị đã đăng nhập.', 'Quản trị nhập thông tin và chọn vai trò "Nhân viên".', 'Tài khoản được tạo; nhân viên đăng nhập chỉ thấy menu đơn hàng, kho.'),
    ('AC2 – Nhân viên xem doanh thu', 'Người dùng đăng nhập bằng tài khoản Nhân viên.', 'Truy cập đường dẫn báo cáo doanh thu.', 'Hệ thống trả lỗi 403 và thông báo không có quyền.'),
    ('AC3 – Khách xem đơn của người khác', 'Khách A đã đăng nhập.', 'Khách A mở đường dẫn chi tiết đơn của khách B.', 'Hệ thống từ chối truy cập.')])
STORY(3, 'US05', 'Quản lý sản phẩm', 'Là quản lý, tôi muốn quản lý danh mục và sản phẩm để thông tin trên website luôn đúng.', [
    ('AC1 – Thêm sản phẩm hợp lệ', 'Quản lý đã đăng nhập.', 'Nhập tên, danh mục, giá > 0, khối lượng, ít nhất 1 ảnh và chọn "Lưu".', 'Sản phẩm được tạo và hiển thị trên website.'),
    ('AC2 – Dữ liệu không hợp lệ', 'Quản lý đang thêm sản phẩm.', 'Bỏ trống tên hoặc nhập giá ≤ 0.', 'Hệ thống báo lỗi tại trường tương ứng, không lưu.'),
    ('AC3 – Đổi giá', 'Sản phẩm đã có trong các đơn cũ.', 'Quản lý đổi giá bán và lưu.', 'Website hiển thị giá mới; đơn giá trong các đơn cũ không đổi (BR11).')])
STORY(4, 'US07', 'Tìm kiếm và xem chi tiết sản phẩm', 'Là khách hàng, tôi muốn tìm kiếm, lọc và xem chi tiết sản phẩm để quyết định mua.', [
    ('AC1 – Tìm không dấu', 'Có sản phẩm "Bánh quy bơ Danisa".', 'Khách gõ "banh quy bo".', 'Kết quả có sản phẩm trên.'),
    ('AC2 – Lọc theo giá', 'Khách chọn khoảng giá 50.000–100.000đ.', 'Áp dụng bộ lọc.', 'Chỉ hiển thị sản phẩm có giá trong khoảng.'),
    ('AC3 – Xem hạn sử dụng', 'Sản phẩm có 2 lô còn hạn.', 'Khách mở trang chi tiết.', 'Hiển thị hạn sử dụng của lô gần nhất và tổng số lượng còn hàng.')])
STORY(5, 'US08', 'Nhập kho theo lô', 'Là nhân viên kho, tôi muốn nhập kho theo lô có hạn sử dụng để quản lý hàng chính xác.', [
    ('AC1 – Nhập lô hợp lệ', 'Sản phẩm "Socola sữa 100g" đang tồn 20.', 'Nhân viên nhập lô 50 hộp, HSD 30/06/2027.', 'Tạo lô mới; tồn khả dụng của sản phẩm thành 70.'),
    ('AC2 – Hạn sử dụng không hợp lệ', 'Nhân viên đang nhập lô.', 'Nhập HSD nhỏ hơn hoặc bằng ngày hiện tại.', 'Hệ thống báo "Hạn sử dụng không hợp lệ" và không lưu.')])
STORY(6, 'US09', 'Giữ hàng theo FEFO', 'Là quản lý, tôi muốn hệ thống giữ hàng theo FEFO khi có đơn để không bán vượt tồn kho hay bán hàng hết hạn.', [
    ('AC1 – Lấy lô gần hết hạn trước', 'Lô A (HSD 01/2027) còn 3, lô B (HSD 06/2027) còn 10.', 'Khách đặt 5 sản phẩm.', 'Hệ thống giữ 3 từ lô A và 2 từ lô B.'),
    ('AC2 – Bỏ qua lô hết hạn', 'Lô C đã hết hạn còn 4, lô B còn 1.', 'Khách đặt 2 sản phẩm.', 'Hệ thống báo chỉ còn 1 sản phẩm.'),
    ('AC3 – Hai đơn đồng thời', 'Sản phẩm chỉ còn 1 gói.', 'Hai khách đặt cùng lúc.', 'Chỉ một đơn thành công, tồn kho không âm.'),
    ('AC4 – Hoàn kho khi hủy', 'Một đơn đã giữ 2 sản phẩm của lô A.', 'Đơn bị hủy.', 'Lô A được cộng lại 2 và lịch sử hủy được lưu.')])
STORY(7, 'US11', 'Quản lý giỏ hàng', 'Là khách hàng, tôi muốn thêm, sửa, xóa sản phẩm trong giỏ để chuẩn bị đặt hàng.', [
    ('AC1 – Thêm sản phẩm', 'Sản phẩm còn hàng.', 'Khách chọn "Thêm vào giỏ".', 'Giỏ hàng cập nhật số lượng và tạm tính.'),
    ('AC2 – Vượt tồn kho', 'Sản phẩm chỉ còn 5.', 'Khách sửa số lượng thành 8.', 'Hệ thống báo "Chỉ còn 5 sản phẩm" và giữ số lượng ở 5.'),
    ('AC3 – Lưu giỏ', 'Khách đã đăng nhập, giỏ có hàng.', 'Khách đăng xuất rồi đăng nhập lại.', 'Giỏ hàng vẫn giữ nguyên.')])
STORY(8, 'US12', 'Đặt hàng COD', 'Là khách hàng, tôi muốn đặt hàng và thanh toán khi nhận hàng.', [
    ('AC1 – Đặt hàng thành công', 'Giỏ có hàng, đủ tồn kho, địa chỉ hợp lệ, tổng ≤ 2.000.000đ.', 'Khách chọn COD và nhấn "Xác nhận đặt hàng".', 'Tạo đơn "Chờ xác nhận", giữ tồn kho, xóa giỏ, hiển thị mã đơn và gửi email.'),
    ('AC2 – Vượt hạn mức COD', 'Tổng thanh toán là 2.350.000đ.', 'Khách chọn COD.', 'COD bị vô hiệu, hệ thống gợi ý thanh toán VNPay (BR07).'),
    ('AC3 – Miễn phí vận chuyển', 'Tiền hàng sau giảm là 320.000đ.', 'Khách xem trang thanh toán.', 'Phí vận chuyển hiển thị 0đ (BR05).')])
STORY(9, 'US15', 'Thanh toán VNPay', 'Là khách hàng, tôi muốn thanh toán qua VNPay để trả tiền ngay khi đặt hàng.', [
    ('AC1 – Thanh toán thành công', 'Đơn ở trạng thái "Chờ thanh toán".', 'Khách thanh toán thành công, VNPay gửi IPN hợp lệ.', 'Hệ thống lưu giao dịch, đơn chuyển "Chờ xác nhận", khách thấy trang thành công.'),
    ('AC2 – IPN sai chữ ký hoặc sai số tiền', 'Hệ thống nhận IPN cho đơn SM000123.', 'Chữ ký không đúng hoặc số tiền khác tổng đơn.', 'Hệ thống từ chối, không cập nhật đơn và ghi log cảnh báo.'),
    ('AC3 – Không thanh toán', 'Khách đóng trang VNPay.', 'Quá 15 phút không có IPN thành công.', 'Đơn tự động hủy và hoàn tồn kho (BR08).'),
    ('AC4 – IPN gửi trùng', 'Đơn đã được ghi nhận thanh toán.', 'VNPay gửi lại IPN lần hai.', 'Hệ thống không ghi nhận trùng giao dịch và phản hồi RspCode = 02 (đơn đã được xác nhận) theo đặc tả VNPay để VNPay ngừng gửi lại.')])
STORY(10, 'US19', 'Xác nhận và hủy đơn', 'Là nhân viên, tôi muốn xem, xác nhận hoặc hủy đơn mới để xử lý kịp thời.', [
    ('AC1 – Xác nhận đơn', 'Đơn ở trạng thái "Chờ xác nhận".', 'Nhân viên chọn "Xác nhận".', 'Đơn chuyển "Đã xác nhận", lưu lịch sử người thực hiện và gửi email cho khách.'),
    ('AC2 – Hủy đơn', 'Khách đổi ý, gọi điện báo hủy.', 'Nhân viên chọn "Hủy" và nhập lý do.', 'Đơn chuyển "Đã hủy", tồn kho được hoàn lại.'),
    ('AC3 – Chuyển trạng thái sai thứ tự', 'Đơn đang "Chờ xác nhận".', 'Nhân viên chọn "Đang giao".', 'Hệ thống từ chối vì chưa qua bước xác nhận, đóng gói (BR10).')])

# =====================================================================================
#                                    BƯỚC 3
# =====================================================================================
doc.add_page_break()
H(1, 'BƯỚC 3. THIẾT KẾ HỆ THỐNG (SYSTEM DESIGN)')
H(2, '1. Thiết kế chức năng hệ thống')
H(3, '1.1. Sơ đồ Use Case tổng quát')
IMGF('usecase.png', 'Sơ đồ Use Case tổng quát của website SweetMart')
P('Hệ thống có năm tác nhân bên trong (Khách vãng lai, Khách hàng, Nhân viên bán hàng, Quản lý cửa hàng, Quản trị hệ thống) và hai hệ thống bên ngoài tham gia trực tiếp vào use case '
  '(VNPay, GHN). Khách hàng kế thừa toàn bộ chức năng của Khách vãng lai; Quản lý kế thừa chức năng của Nhân viên. Use case "Thanh toán online" mở rộng (extend) use case "Đặt hàng" '
  'khi khách chọn VNPay.')
T(['Mã', 'Use Case', 'Mã', 'Use Case'],
  [['UC01', 'Xem và tìm kiếm sản phẩm', 'UC08', 'Xác nhận và xử lý đơn hàng'],
   ['UC02', 'Đăng ký / Đăng nhập', 'UC09', 'Tạo vận đơn GHN, theo dõi giao hàng'],
   ['UC03', 'Quản lý giỏ hàng', 'UC10', 'Quản lý kho và hạn sử dụng'],
   ['UC04', 'Đặt hàng', 'UC11', 'Quản lý sản phẩm và danh mục'],
   ['UC05', 'Thanh toán online (VNPay)', 'UC12', 'Quản lý khuyến mãi'],
   ['UC06', 'Theo dõi / Hủy đơn hàng', 'UC13', 'Xem báo cáo thống kê'],
   ['UC07', 'Đánh giá sản phẩm', 'UC14', 'Quản lý tài khoản và phân quyền']],
  [1.6, 6.3, 1.6, 6.4], title='Danh sách Use Case', center_cols=(0, 2))
H(3, '1.2. Đặc tả các Use Case chính')
UC('UC02', 'Đăng nhập', [
    'Khách hàng, Nhân viên, Quản lý, Quản trị.', 'FR01, FR03, NFR04, NFR05, BR13.',
    'Người dùng đăng nhập bằng email và mật khẩu để sử dụng chức năng theo vai trò.',
    'Xác thực người dùng, bảo vệ thông tin và bảo đảm chức năng được truy cập đúng quyền.',
    'Người dùng chọn "Đăng nhập" trên website hoặc truy cập trang quản trị.',
    'Người dùng đã có tài khoản đang hoạt động.',
    'Người dùng nhập email, mật khẩu. Hệ thống kiểm tra thông tin, so sánh mật khẩu đã băm, xác định vai trò và cấp mã truy cập (JWT). '
    'Khách hàng được chuyển về trang chủ; Nhân viên, Quản lý, Quản trị được chuyển tới trang quản trị với menu tương ứng.',
    'Sai email hoặc mật khẩu: hệ thống báo "Email hoặc mật khẩu không đúng". Sai 5 lần liên tiếp: khóa đăng nhập 15 phút. Tài khoản bị khóa: thông báo liên hệ cửa hàng.',
    'Thành công: người dùng đăng nhập và truy cập theo vai trò. Thất bại: không cấp quyền truy cập.'])
UC('UC11', 'Quản lý sản phẩm và danh mục', [
    'Quản lý cửa hàng.', 'FR04, cung cấp dữ liệu cho FR05; BR11.',
    'Quản lý thêm, sửa, ẩn danh mục và sản phẩm bánh kẹo cùng hình ảnh, giá, khối lượng, thương hiệu.',
    'Thông tin sản phẩm đầy đủ, thống nhất, giúp khách dễ tìm và chọn mua.',
    'Quản lý chọn "Sản phẩm" trên trang quản trị.',
    'Quản lý đã đăng nhập.',
    'Quản lý xem danh sách sản phẩm, chọn thêm mới hoặc chỉnh sửa, nhập thông tin và tải ảnh lên. Hệ thống kiểm tra dữ liệu bắt buộc, lưu sản phẩm và cập nhật trên website.',
    'Thiếu thông tin hoặc giá không hợp lệ: hệ thống báo lỗi. Sản phẩm đã phát sinh đơn hàng chỉ được ẩn, không được xóa.',
    'Thông tin sản phẩm được cập nhật trên website và trang quản trị; đơn giá trong đơn cũ không đổi.'])
UC('UC10', 'Quản lý kho và hạn sử dụng', [
    'Nhân viên kho, Quản lý.', 'FR06, FR07, FR08; BR01, BR02, BR03.',
    'Nhân viên nhập hàng theo lô kèm hạn sử dụng; hệ thống tính tồn khả dụng và cảnh báo lô cận date.',
    'Kiểm soát chính xác số lượng và hạn sử dụng, hạn chế hàng hết hạn.',
    'Nhân viên chọn "Kho & lô hàng" → "Nhập lô".',
    'Nhân viên đã đăng nhập; sản phẩm đã tồn tại.',
    'Nhân viên chọn sản phẩm, nhập số lượng, ngày sản xuất, hạn sử dụng và lưu. Hệ thống tạo lô, cộng tồn kho. Hằng ngày, hệ thống quét các lô còn ≤ 30 ngày hạn để hiển thị cảnh báo.',
    'Hạn sử dụng không hợp lệ hoặc số lượng ≤ 0: hệ thống từ chối lưu.',
    'Lô mới được ghi nhận; tồn khả dụng và danh sách cận date được cập nhật.'])
UC('UC04', 'Đặt hàng', [
    'Khách hàng; GHN (hệ thống ngoài).', 'FR09, FR10, FR11, FR15; BR02, BR04, BR05, BR06, BR07, BR11.',
    'Khách hàng tạo đơn từ các sản phẩm trong giỏ.',
    'Giúp khách đặt hàng nhanh; cửa hàng nhận đủ thông tin, không bán vượt tồn kho.',
    'Khách nhấn "Đặt hàng" tại giỏ hàng.',
    'Khách đã đăng nhập; giỏ có ít nhất một sản phẩm đang bán.',
    'Hệ thống kiểm tra tồn kho; khách chọn địa chỉ; hệ thống gọi GHN tính phí, áp BR05; khách nhập mã giảm giá, chọn phương thức thanh toán và xác nhận. '
    'Hệ thống tạo đơn có mã duy nhất, giữ hàng theo FEFO trong một giao dịch (transaction), xóa giỏ và gửi email. Nếu chọn VNPay, tiếp tục UC05.',
    'Không đủ hàng: báo sản phẩm hết, quay lại giỏ. Mã giảm giá không hợp lệ: báo lý do. GHN lỗi: dùng phí mặc định 30.000đ và ghi log. Vượt hạn mức COD: yêu cầu chọn VNPay.',
    'Đơn được tạo ở trạng thái "Chờ xác nhận" (COD) hoặc "Chờ thanh toán" (VNPay); tồn kho được giữ.'])
UC('UC05', 'Thanh toán online qua VNPay', [
    'Khách hàng; VNPay (hệ thống ngoài).', 'FR13; BR08; NFR03, NFR06, NFR07.',
    'Khách thanh toán đơn hàng trên cổng VNPay; hệ thống nhận kết quả và cập nhật tự động.',
    'Tự động xác nhận thanh toán, không cần đối chiếu sao kê.',
    'Khách chọn VNPay và xác nhận đặt hàng.',
    'Đơn đã tạo ở trạng thái "Chờ thanh toán".',
    'Hệ thống tạo URL thanh toán có chữ ký HMAC-SHA512 và chuyển khách sang VNPay. Khách thanh toán. VNPay gửi IPN về hệ thống; hệ thống kiểm tra chữ ký, mã đơn, số tiền, '
    'lưu giao dịch, chuyển đơn sang "Chờ xác nhận" và phản hồi mã 00. VNPay đưa khách về trang kết quả.',
    'Chữ ký sai: phản hồi mã 97, không cập nhật. Sai số tiền: mã 04. IPN trùng: không ghi nhận lại. Khách hủy hoặc quá 15 phút: đơn bị hủy tự động, hoàn kho.',
    'Thành công: giao dịch được lưu, đơn chờ nhân viên xác nhận. Thất bại: đơn không được ghi nhận đã thanh toán.'])
UC('UC08', 'Xác nhận và xử lý đơn hàng', [
    'Nhân viên bán hàng, Quản lý.', 'FR14; BR09, BR10.',
    'Nhân viên kiểm tra đơn mới, xác nhận hoặc hủy, cập nhật các trạng thái xử lý.',
    'Đơn được tiếp nhận chính xác, đúng thứ tự, có lịch sử truy vết.',
    'Nhân viên chọn một đơn ở tab "Chờ xác nhận".',
    'Nhân viên đã đăng nhập, có quyền xử lý đơn.',
    'Nhân viên xem thông tin người nhận, sản phẩm, ghi chú; hệ thống hiển thị các lô đã giữ. Nhân viên chọn "Xác nhận"; hệ thống kiểm tra thứ tự trạng thái, cập nhật đơn, '
    'ghi lịch sử và gửi email cho khách.',
    'Thông tin giao hàng không hợp lệ: nhân viên liên hệ khách, có thể hủy kèm lý do (hoàn kho). Chuyển trạng thái sai thứ tự: hệ thống từ chối.',
    'Đơn ở trạng thái mới, lịch sử xử lý được lưu.'])
UC('UC09', 'Tạo vận đơn GHN và theo dõi giao hàng', [
    'Nhân viên bán hàng; GHN (hệ thống ngoài).', 'FR15, FR12; BR10.',
    'Nhân viên tạo vận đơn trên GHN trực tiếp từ hệ thống; trạng thái giao được cập nhật về đơn hàng.',
    'Không nhập lại địa chỉ; khách và cửa hàng theo dõi được tiến độ giao.',
    'Nhân viên nhấn "Tạo vận đơn" ở đơn "Đang đóng gói".',
    'Đơn đã xác nhận và đóng gói xong.',
    'Hệ thống gửi thông tin người nhận, khối lượng, tiền thu hộ (COD) sang GHN, nhận mã vận đơn, lưu vào đơn và chuyển "Đang giao". Khi GHN báo giao thành công, '
    'đơn chuyển "Đã giao" và tiền COD được ghi nhận.',
    'GHN lỗi: báo lỗi, cho thử lại hoặc nhập mã vận đơn thủ công. Giao thất bại: đơn chuyển "Giao thất bại", hàng hoàn được cộng lại kho.',
    'Đơn có mã vận đơn và trạng thái giao hàng chính xác.'])
UC('UC13', 'Xem báo cáo thống kê', [
    'Quản lý cửa hàng.', 'FR20, FR21; BR13; NFR05.',
    'Quản lý xem doanh thu, đơn hàng, sản phẩm bán chạy và tồn kho được tổng hợp tự động.',
    'Hỗ trợ ra quyết định nhập hàng, khuyến mãi mà không phải thống kê thủ công.',
    'Quản lý chọn "Báo cáo" trên trang quản trị.',
    'Quản lý đã đăng nhập.',
    'Quản lý chọn khoảng thời gian; hệ thống kiểm tra quyền, tổng hợp doanh thu từ các đơn "Đã giao", top sản phẩm, tồn kho theo lô và hiển thị biểu đồ, bảng; cho phép xuất Excel.',
    'Không có dữ liệu: thông báo phù hợp. Người không phải Quản lý truy cập: từ chối.',
    'Quản lý xem được báo cáo theo khoảng thời gian đã chọn.'])

H(3, '1.3. Sơ đồ hoạt động (Activity Diagram)')
P('**a. Sơ đồ hoạt động đặt hàng trực tuyến**', indent=False)
IMGF('activity_dathang.png', 'Sơ đồ hoạt động đặt hàng trực tuyến', 12)
P('Sơ đồ mô tả quá trình khách hàng từ giỏ hàng đến khi đặt hàng thành công: kiểm tra đăng nhập, kiểm tra tồn kho, nhập địa chỉ, tính phí ship qua GHN, áp mã giảm giá và chọn phương thức thanh toán. '
  'Nếu thanh toán VNPay không thành công, khách được quay lại chọn phương thức khác.')
P('**b. Sơ đồ hoạt động xác nhận đơn hàng**', indent=False)
IMGF('activity_xacnhan.png', 'Sơ đồ hoạt động xác nhận đơn hàng', 11.5)
P('Nhân viên kiểm tra thông tin giao hàng và tình trạng lô hàng đã giữ trước khi xác nhận. Nếu thông tin không hợp lệ hoặc lô hàng không còn đủ, đơn bị hủy, tồn kho được hoàn lại và khách nhận email thông báo.')
P('**c. Sơ đồ hoạt động thanh toán VNPay**', indent=False)
IMGF('activity_thanhtoan.png', 'Sơ đồ hoạt động thanh toán qua VNPay', 11.5)
P('Kết quả thanh toán chỉ được ghi nhận từ IPN – kênh giao tiếp trực tiếp giữa máy chủ VNPay và máy chủ SweetMart – sau khi kiểm tra chữ ký và số tiền. Đây là điểm kiểm soát chính của phần tích hợp thanh toán.')
P('**d. Sơ đồ hoạt động đóng gói và giao hàng**', indent=False)
IMGF('activity_giaohang.png', 'Sơ đồ hoạt động đóng gói và giao hàng qua GHN', 11.5)
P('Sau khi đóng gói, nhân viên tạo vận đơn GHN từ hệ thống. Trạng thái giao hàng được GHN cập nhật về; nếu giao thất bại, hàng hoàn được cộng lại kho.')

H(3, '1.4. Sơ đồ luồng dữ liệu (DFD)')
P('Sơ đồ mức ngữ cảnh mô tả việc trao đổi dữ liệu giữa website SweetMart với các tác nhân bên ngoài, gồm khách hàng, nhân viên/quản lý, quản trị và ba hệ thống tích hợp: VNPay, GHN, dịch vụ email.')
IMGF('dfd_context.png', 'Sơ đồ luồng dữ liệu mức ngữ cảnh của website SweetMart')
P('Sơ đồ DFD mức 0 phân chia hệ thống thành sáu tiến trình: (1) quản lý tài khoản, (2) quản lý sản phẩm và kho theo lô, (3) giỏ hàng và đặt hàng, (4) thanh toán, '
  '(5) xử lý đơn và giao hàng, (6) báo cáo thống kê; cùng năm kho dữ liệu D1–D5.')
IMGF('dfd_muc0.png', 'Sơ đồ luồng dữ liệu mức 0 của website SweetMart')

H(3, '1.5. Sơ đồ tuần tự (Sequence Diagram)')
P('**a. Sơ đồ tuần tự đặt hàng trực tuyến (COD)**', indent=False)
IMGF('sequence_dathang.png', 'Sơ đồ tuần tự đặt hàng trực tuyến')
P('Backend gọi GHN để tính phí, kiểm tra mã giảm giá và hạn mức COD, sau đó trừ giữ tồn kho và tạo đơn trong cùng một transaction để bảo đảm không bán vượt số lượng; email được gửi bất đồng bộ để không làm chậm phản hồi.')
P('**b. Sơ đồ tuần tự thanh toán VNPay**', indent=False)
IMGF('sequence_vnpay.png', 'Sơ đồ tuần tự thanh toán trực tuyến qua VNPay')
P('Sơ đồ thể hiện hai kênh trả kết quả của VNPay: IPN (máy chủ – máy chủ) dùng để cập nhật dữ liệu, và ReturnUrl (qua trình duyệt) chỉ dùng để hiển thị kết quả cho khách.')
P('**c. Sơ đồ tuần tự xác nhận đơn và tạo vận đơn GHN**', indent=False)
IMGF('sequence_xacnhan.png', 'Sơ đồ tuần tự xác nhận đơn hàng và tạo vận đơn GHN')
P('Mỗi lần đổi trạng thái, Backend kiểm tra quyền và thứ tự hợp lệ rồi ghi thêm một bản ghi LichSuDonHang. Khi tạo vận đơn, Backend gửi thông tin sang GHN và lưu mã vận đơn trả về.')
P('**d. Sơ đồ tuần tự xem báo cáo doanh thu**', indent=False)
IMGF('sequence_baocao.png', 'Sơ đồ tuần tự xem báo cáo doanh thu', 13.5)
P('Hệ thống kiểm tra vai trò Quản lý trước khi truy vấn, tổng hợp doanh thu từ các đơn "Đã giao" và trả dữ liệu dạng JSON để trang quản trị vẽ biểu đồ.')

H(3, '1.6. Sơ đồ lớp (Class Diagram)')
IMGF('class.png', 'Sơ đồ lớp của website SweetMart')
P('Sơ đồ lớp thể hiện các lớp nghiệp vụ chính cùng thuộc tính và phương thức. Một số phương thức quan trọng: SanPham.layLoFEFO() chọn lô để giữ hàng, LoHang.laCanDate() kiểm tra cận hạn, '
  'KhuyenMai.kiemTraHopLe() kiểm tra BR06, DonHang.capNhatTrangThai() kiểm tra BR10, ThanhToan.xacThucChuKy() kiểm tra chữ ký IPN của VNPay.')

H(3, '1.7. Sơ đồ trạng thái (State Machine Diagram)')
P('**a. Sơ đồ trạng thái đơn hàng**', indent=False)
IMGF('state_donhang.png', 'Sơ đồ trạng thái đơn hàng của website SweetMart')
P('Đơn thanh toán VNPay bắt đầu ở "Chờ thanh toán", đơn COD bắt đầu ở "Chờ xác nhận". Từ "Chờ xác nhận", đơn đi tuần tự Đã xác nhận → Đang đóng gói → Đang giao → Đã giao. '
  'Đơn có thể bị hủy ở "Chờ xác nhận" (khách hoặc nhân viên) và "Đã xác nhận" (nhân viên, hoàn kho); đơn giao thất bại được hoàn hàng về kho và chuyển "Đã hủy".')
P('Sơ đồ được xây dựng từ UC04, UC05, UC08, UC09, FR14 và các quy tắc BR08, BR09, BR10, giúp hệ thống kiểm soát thứ tự chuyển trạng thái và tránh cập nhật sai.')
P('**b. Sơ đồ trạng thái thanh toán**', indent=False)
IMGF('state_thanhtoan.png', 'Sơ đồ trạng thái thanh toán của website SweetMart')
P('Trạng thái thanh toán được quản lý tách biệt với trạng thái đơn hàng. Với VNPay, thanh toán chuyển sang "Đã thanh toán" khi nhận IPN hợp lệ, hoặc "Thất bại / Hết hạn" khi IPN báo lỗi hay quá 15 phút; '
  'nếu đơn đã thanh toán bị hủy, thanh toán chuyển sang "Đã hoàn tiền". Với COD, tiền chỉ được ghi nhận "Đã thu" khi giao hàng thành công.')

H(2, '2. Thiết kế cơ sở dữ liệu')
H(3, '2.1. Sơ đồ thực thể – liên kết (ERD)')
P('Dựa trên yêu cầu chức năng và sơ đồ lớp, nhóm xác định 15 thực thể dữ liệu. Các quan hệ nhiều – nhiều được tách thành bảng trung gian (GioHang, ChiTietDonHang); '
  'bảng LoHang tách khỏi SanPham để một sản phẩm có nhiều lô với hạn sử dụng khác nhau; bảng PhanBoLo ghi nhận mỗi dòng hàng trong đơn được lấy từ lô nào và bao nhiêu, '
  'vì theo FEFO một sản phẩm trong cùng một đơn có thể phải lấy từ nhiều lô.')
IMGF('erd.png', 'Sơ đồ thực thể – liên kết (ERD) của website SweetMart')
caption('bang', 'Danh sách thực thể và thuộc tính trong ERD')
T(['STT', 'Thực thể', 'Thuộc tính chính', 'Khóa chính'],
  [['1', 'VaiTro', 'tenVaiTro', 'maVaiTro'],
   ['2', 'NguoiDung', 'hoTen, email, matKhauHash, soDienThoai, trangThai, maVaiTro', 'maND'],
   ['3', 'DiaChi', 'nguoiNhan, soDienThoai, diaChiChiTiet, macDinh', 'maDC'],
   ['4', 'DanhMuc', 'tenDanhMuc, maDMCha', 'maDM'],
   ['5', 'SanPham', 'tenSP, thuongHieu, giaBan, donViTinh, khoiLuong, moTa, trangThai', 'maSP'],
   ['6', 'HinhAnhSP', 'duongDan', 'maHA'],
   ['7', 'LoHang', 'soLuongNhap, soLuongTon, ngaySanXuat, hanSuDung, ngayNhap', 'maLo'],
   ['8', 'GioHang', 'soLuong', 'maND + maSP'],
   ['9', 'KhuyenMai', 'maCode, loaiGiam, giaTriGiam, donToiThieu, ngayBatDau, ngayKetThuc, soLuotConLai', 'maKM'],
   ['10', 'DonHang', 'ngayDat, tongTienHang, phiVanChuyen, tienGiam, tongThanhToan, phuongThucTT, diaChiGiao, maVanDonGHN, trangThai', 'maDH'],
   ['11', 'ChiTietDonHang', 'soLuong, donGia', 'maDH + maSP'],
   ['12', 'PhanBoLo', 'soLuong (số lượng lấy từ lô)', 'maDH + maSP + maLo'],
   ['13', 'ThanhToan', 'soTien, maGiaoDichVNPay, trangThai, thoiGian', 'maTT'],
   ['14', 'LichSuDonHang', 'trangThaiCu, trangThaiMoi, nguoiThucHien, thoiGian, ghiChu', 'maLS'],
   ['15', 'DanhGia', 'soSao, noiDung, ngayDanhGia', 'maDG']],
  [1.2, 3.3, 8.8, 2.6], center_cols=(0,))
caption('bang', 'Mối quan hệ giữa các thực thể')
T(['STT', 'Thực thể 1', 'Quan hệ', 'Thực thể 2', 'Mô tả'],
  [['1', 'VaiTro', '1 – n', 'NguoiDung', 'Mỗi người dùng có một vai trò'],
   ['2', 'NguoiDung', '1 – n', 'DiaChi', 'Một khách lưu nhiều địa chỉ'],
   ['3', 'NguoiDung', '1 – n', 'DonHang', 'Một khách đặt nhiều đơn'],
   ['4', 'NguoiDung', 'n – n', 'SanPham', 'Qua bảng GioHang'],
   ['5', 'DanhMuc', '1 – n', 'SanPham', 'Một danh mục có nhiều sản phẩm; danh mục có danh mục cha'],
   ['6', 'SanPham', '1 – n', 'HinhAnhSP', 'Một sản phẩm có nhiều ảnh'],
   ['7', 'SanPham', '1 – n', 'LoHang', 'Một sản phẩm có nhiều lô, mỗi lô có hạn sử dụng riêng'],
   ['8', 'DonHang', 'n – n', 'SanPham', 'Qua bảng ChiTietDonHang'],
   ['9', 'ChiTietDonHang', '1 – n', 'PhanBoLo', 'Một dòng hàng có thể được lấy từ nhiều lô (FEFO)'],
   ['10', 'LoHang', '1 – n', 'PhanBoLo', 'Một lô cấp hàng cho nhiều đơn; dùng để hoàn đúng lô khi hủy'],
   ['11', 'KhuyenMai', '1 – n', 'DonHang', 'Một đơn dùng tối đa một mã (có thể không dùng)'],
   ['12', 'DonHang', '1 – n', 'ThanhToan', 'Một đơn có thể có nhiều lần giao dịch (thất bại, thành công, hoàn tiền)'],
   ['13', 'DonHang', '1 – n', 'LichSuDonHang', 'Mọi lần đổi trạng thái được lưu lại'],
   ['14', 'NguoiDung', '1 – n', 'DanhGia', 'Khách viết nhiều đánh giá'],
   ['15', 'SanPham', '1 – n', 'DanhGia', 'Một sản phẩm có nhiều đánh giá']],
  [1.2, 2.9, 1.7, 3.2, 6.9], center_cols=(0, 2))
P('Cơ sở dữ liệu được chuẩn hóa đến dạng chuẩn 3 (3NF): mỗi bảng có khóa chính, không có thuộc tính lặp; thuộc tính phụ thuộc đầy đủ vào khóa và không phụ thuộc bắc cầu. '
  'Riêng donGia và diaChiGiao trong đơn hàng được lưu cố định tại thời điểm đặt để giữ đúng lịch sử giao dịch (BR11). Nhóm chọn cơ sở dữ liệu quan hệ SQL Server vì dữ liệu có cấu trúc rõ ràng '
  'và cần transaction khi giữ tồn kho, tạo đơn.')
H(3, '2.2. Cấu trúc bảng và ràng buộc dữ liệu (Data Dictionary)')
P('Dựa trên ERD, nhóm xác định các bảng dữ liệu phục vụ những chức năng chính. Mỗi bảng có khóa chính (PK) để định danh bản ghi và khóa ngoại (FK) để liên kết với bảng khác.')
caption('bang', 'Danh sách các bảng dữ liệu của website SweetMart')
T(['STT', 'Tên bảng', 'Chức năng'],
  [['1', 'VaiTro', 'Danh sách vai trò: Khách hàng, Nhân viên, Quản lý, Quản trị'],
   ['2', 'NguoiDung', 'Tài khoản đăng nhập của khách và nhân viên'],
   ['3', 'DiaChi', 'Sổ địa chỉ giao hàng của khách'],
   ['4', 'DanhMuc', 'Danh mục sản phẩm (bánh quy, kẹo, socola, hộp quà...)'],
   ['5', 'SanPham', 'Thông tin sản phẩm bánh kẹo'],
   ['6', 'HinhAnhSP', 'Hình ảnh sản phẩm'],
   ['7', 'LoHang', 'Lô hàng nhập kho, số lượng tồn và hạn sử dụng'],
   ['8', 'GioHang', 'Sản phẩm trong giỏ của khách'],
   ['9', 'KhuyenMai', 'Mã giảm giá và điều kiện áp dụng'],
   ['10', 'DonHang', 'Thông tin đơn hàng, thanh toán, vận đơn GHN'],
   ['11', 'ChiTietDonHang', 'Sản phẩm, số lượng, đơn giá trong đơn'],
   ['12', 'PhanBoLo', 'Số lượng của từng dòng hàng được giữ từ lô nào (FEFO, hoàn kho)'],
   ['13', 'ThanhToan', 'Giao dịch thanh toán VNPay / thu COD'],
   ['14', 'LichSuDonHang', 'Lịch sử thay đổi trạng thái đơn'],
   ['15', 'DanhGia', 'Đánh giá sản phẩm của khách']],
  [1.2, 3.6, 11.1], center_cols=(0,))
P('**a. Nhóm bảng người dùng**', indent=False)
BL(['**VaiTro:** maVaiTro (PK), tenVaiTro.',
    '**NguoiDung:** maND (PK), maVaiTro (FK), hoTen, email (duy nhất), matKhauHash, soDienThoai, trangThai, ngayTao. Phục vụ đăng nhập và phân quyền.',
    '**DiaChi:** maDC (PK), maND (FK), nguoiNhan, soDienThoai, diaChiChiTiet, maQuanHuyenGHN, maPhuongXaGHN, macDinh. Mã quận/phường theo GHN dùng để tính phí và tạo vận đơn.'])
P('**b. Nhóm bảng sản phẩm và kho**', indent=False)
BL(['**DanhMuc:** maDM (PK), tenDanhMuc, maDMCha (FK tự tham chiếu).',
    '**SanPham:** maSP (PK), maDM (FK), tenSP, thuongHieu, giaBan, donViTinh, khoiLuong, moTa, trangThai.',
    '**HinhAnhSP:** maHA (PK), maSP (FK), duongDan.',
    '**LoHang:** maLo (PK), maSP (FK), soLuongNhap, soLuongTon, ngaySanXuat, hanSuDung, ngayNhap. Là cơ sở cho FEFO và cảnh báo cận date.'])
P('**c. Nhóm bảng giỏ hàng, khuyến mãi và đơn hàng**', indent=False)
BL(['**GioHang:** maND (PK, FK), maSP (PK, FK), soLuong.',
    '**KhuyenMai:** maKM (PK), maCode (duy nhất), loaiGiam (phần trăm / số tiền), giaTriGiam, donToiThieu, ngayBatDau, ngayKetThuc, soLuotConLai.',
    '**DonHang:** maDH (PK), maND (FK), maKM (FK, có thể rỗng), ngayDat, tongTienHang, phiVanChuyen, tienGiam, tongThanhToan, phuongThucTT (COD/VNPAY), diaChiGiao, ghiChu, maVanDonGHN, trangThai.',
    '**ChiTietDonHang:** maDH (PK, FK), maSP (PK, FK), soLuong, donGia.',
    '**PhanBoLo:** maDH (PK, FK), maSP (PK, FK), maLo (PK, FK → LoHang), soLuong. Khóa (maDH, maSP) tham chiếu ChiTietDonHang. '
    'Khi một sản phẩm phải lấy từ 2 lô (ví dụ 3 gói lô A + 2 gói lô B), ChiTietDonHang vẫn chỉ có một dòng 5 gói, còn PhanBoLo có hai dòng; nhờ đó khóa chính không bị trùng và việc hoàn kho cộng lại đúng từng lô.'])
P('**d. Nhóm bảng thanh toán, lịch sử và đánh giá**', indent=False)
BL(['**ThanhToan:** maTT (PK), maDH (FK), soTien, maGiaoDichVNPay (duy nhất), maNganHang, trangThai, thoiGian, duLieuIPN.',
    '**LichSuDonHang:** maLS (PK), maDH (FK), trangThaiCu, trangThaiMoi, nguoiThucHien (FK → NguoiDung), thoiGian, ghiChu.',
    '**DanhGia:** maDG (PK), maND (FK), maSP (FK), maDH (FK), soSao, noiDung, ngayDanhGia.'])
P('**Các ràng buộc dữ liệu chính**', indent=False)
BL(['**Khóa dữ liệu:** mỗi bảng có khóa chính; khóa ngoại phải tham chiếu bản ghi hợp lệ.',
    '**Tài khoản:** email không trùng; mật khẩu lưu dạng băm; vai trò bắt buộc.',
    '**Sản phẩm và kho:** giaBan > 0; soLuongTon ≥ 0; hanSuDung > ngayNhap; số lượng đặt > 0 và không vượt tồn khả dụng của các lô còn hạn.',
    '**Khuyến mãi:** maCode duy nhất; ngayKetThuc > ngayBatDau; soLuotConLai ≥ 0.',
    '**Đơn hàng:** mỗi đơn có ít nhất một dòng chi tiết; tongThanhToan = tongTienHang + phiVanChuyen − tienGiam; phuongThucTT chỉ nhận COD hoặc VNPAY.',
    '**Thanh toán:** maGiaoDichVNPay duy nhất để không ghi nhận trùng IPN; số tiền phải bằng tổng thanh toán của đơn.',
    '**Đánh giá:** soSao từ 1 đến 5; mỗi (maDH, maSP) chỉ có một đánh giá.'])

H(2, '3. Thiết kế phân quyền')
P('Hệ thống có bốn vai trò đăng nhập: Khách hàng, Nhân viên, Quản lý và Quản trị (khách vãng lai chỉ xem sản phẩm). Ma trận CRUD dưới đây là cơ sở để kiểm tra thiếu sót và thiết kế phân quyền API.')
caption('bang', 'Ma trận phân quyền CRUD của website SweetMart')
T(['Chức năng / Dữ liệu', 'Quản lý', 'Nhân viên', 'Quản trị', 'Khách hàng', 'Khách vãng lai'],
  [['Danh mục, sản phẩm', 'C R U D', 'R', 'R', 'R', 'R'],
   ['Lô hàng, tồn kho', 'C R U D', 'C R U', 'R', 'R¹', 'R¹'],
   ['Giỏ hàng', '—', '—', '—', 'C R U D³', '—'],
   ['Đơn hàng', 'R U D', 'R U', 'R', 'C R U²³', '—'],
   ['Thanh toán', 'R U', 'R U⁴', 'R', 'C R³', '—'],
   ['Vận đơn GHN', 'C R U', 'C R U', 'R', 'R³', '—'],
   ['Lịch sử đơn hàng', 'R', 'R', 'R', 'R³', '—'],
   ['Khuyến mãi', 'C R U D', 'R', 'R', 'R', 'R'],
   ['Đánh giá', 'R D', 'R', 'R D', 'C R U³', 'R'],
   ['Thông tin khách hàng', 'R', 'R', 'R U', 'R U³', 'C (đăng ký)'],
   ['Báo cáo doanh thu, tồn kho', 'R', '—', '—', '—', '—'],
   ['Tài khoản, vai trò', 'R', '—', 'C R U D', '—', '—'],
   ['Cấu hình tích hợp (VNPay, GHN, SMTP)', '—', '—', 'R U', '—', '—']],
  [4.9, 2.3, 2.1, 2.1, 2.4, 2.1], center_cols=(1, 2, 3, 4, 5), fs=11.5)
P('Chú thích: C (Create) – Tạo mới; R (Read) – Xem; U (Update) – Cập nhật; D (Delete) – Xóa; "—" – Không có quyền. '
  '¹ Chỉ xem tình trạng còn hàng và hạn sử dụng gần nhất, không xem dữ liệu kho nội bộ. ² Khách chỉ được hủy đơn đang "Chờ xác nhận". '
  '³ Chỉ dữ liệu của chính khách. ⁴ Nhân viên chỉ xác nhận thu tiền COD; trạng thái VNPay do hệ thống cập nhật từ IPN. Xóa đơn hàng là xóa mềm (đánh dấu).', indent=False)
P('**Nguyên tắc phân quyền**', indent=False)
BL(['**Quản lý:** quản lý sản phẩm, kho, khuyến mãi, đơn hàng; là vai trò duy nhất xem báo cáo doanh thu.',
    '**Nhân viên:** xác nhận, xử lý đơn, nhập kho, tạo vận đơn, xác nhận thu COD; không sửa giá, không xem doanh thu.',
    '**Quản trị:** quản lý tài khoản, vai trò, cấu hình khóa tích hợp và sao lưu; không thao tác nghiệp vụ bán hàng.',
    '**Khách hàng:** quản lý tài khoản, giỏ hàng, đơn hàng và đánh giá của chính mình.',
    'Quyền được kiểm tra ở phía máy chủ (Backend) dựa trên vai trò trong JWT, không chỉ dựa vào ẩn/hiện chức năng trên giao diện. Các thao tác quan trọng (xác nhận, hủy đơn, xác nhận thu tiền) được ghi lịch sử.'])

H(2, '4. Thiết kế kiến trúc hệ thống')
P('Nhóm lựa chọn kiến trúc ba lớp: giao diện người dùng (Frontend), xử lý nghiệp vụ (Backend) và cơ sở dữ liệu (Database); bổ sung **lớp tích hợp (Integration Adapters)** '
  'để kết nối với các hệ thống bên ngoài.')
P('**a. Lớp giao diện người dùng (Frontend)**', indent=False)
P('Frontend xây dựng bằng ReactJS dạng ứng dụng một trang (SPA), responsive, gồm hai khu vực:')
BL(['**Website khách hàng:** xem, tìm kiếm sản phẩm, giỏ hàng, đặt hàng, thanh toán, theo dõi đơn, đánh giá.',
    '**Trang quản trị:** quản lý sản phẩm, kho theo lô, đơn hàng, vận đơn, khuyến mãi, báo cáo, tài khoản – hiển thị theo vai trò.'])
P('**b. Lớp xử lý nghiệp vụ (Backend)**', indent=False)
P('Backend là ASP.NET Core Web API, tiếp nhận yêu cầu REST/JSON từ Frontend, kiểm tra dữ liệu và quy tắc nghiệp vụ trước khi truy cập cơ sở dữ liệu. Các chức năng xử lý chính:')
BL(['Xác thực JWT, kiểm tra quyền theo vai trò.', 'Quản lý sản phẩm, danh mục, lô hàng; tính tồn khả dụng, FEFO, cảnh báo cận date.',
    'Xử lý giỏ hàng, mã giảm giá, tạo đơn và giữ tồn kho trong transaction.', 'Quản lý vòng đời trạng thái đơn và lịch sử.',
    'Tổng hợp báo cáo doanh thu, tồn kho.', 'Tác vụ định kỳ: hủy đơn quá hạn thanh toán, quét lô cận date.'])
P('**c. Lớp tích hợp (Integration Adapters)**', indent=False)
BL(['**VNPayClient:** tạo URL thanh toán, ký và xác thực chữ ký HMAC-SHA512, xử lý IPN.',
    '**GhnClient:** gọi API tính phí, tạo đơn giao hàng, nhận cập nhật trạng thái (webhook).',
    '**EmailSender:** gửi email qua SMTP theo hàng đợi, không chặn luồng xử lý chính.',
    'Mỗi adapter có giao diện (interface) riêng, có thể thay bằng bản giả lập (mock) khi kiểm thử hoặc khi đối tác bảo trì; khóa bí mật đọc từ biến môi trường.'])
P('**d. Lớp cơ sở dữ liệu (Database)**', indent=False)
P('SQL Server lưu tập trung tài khoản, sản phẩm, lô hàng, giỏ hàng, đơn hàng, thanh toán, lịch sử, khuyến mãi, đánh giá. Backend truy cập qua Entity Framework Core; '
  'hình ảnh sản phẩm lưu ở dịch vụ lưu trữ ảnh, cơ sở dữ liệu chỉ lưu đường dẫn.')
P('**e. Giao tiếp giữa các thành phần**', indent=False)
P('Frontend gửi yêu cầu HTTPS đến Backend qua Nginx; Backend kiểm tra quyền, quy tắc nghiệp vụ, đọc/ghi cơ sở dữ liệu và khi cần thì gọi VNPay, GHN, SMTP qua lớp tích hợp. '
  'Ví dụ, khi khách đặt hàng VNPay: Backend gọi GHN tính phí, tạo đơn và giữ tồn kho, sinh URL VNPay; sau đó VNPay gọi IPN về Backend để cập nhật thanh toán. '
  'Toàn bộ hệ thống được đóng gói Docker và triển khai trên máy chủ VPS.')
IMGF('architecture.png', 'Sơ đồ kiến trúc tổng thể của website SweetMart')
P('Kiến trúc này tách rõ giao diện, nghiệp vụ, dữ liệu và tích hợp; thay đổi ở đối tác bên ngoài chỉ ảnh hưởng tới adapter tương ứng, thuận lợi cho bảo trì và mở rộng (ví dụ thêm MoMo ở Giai đoạn 2).')

H(2, '5. Thiết kế giao diện người dùng (UI/UX)')
H(3, '5.1. Sơ đồ cấu trúc website (Sitemap)')
IMGF('sitemap.png', 'Sơ đồ cấu trúc website SweetMart', 14.5)
P('Sitemap chia thành hai khu vực: website khách hàng (trang chủ, danh mục, tìm kiếm, chi tiết, giỏ hàng, thanh toán, tài khoản, khuyến mãi, giới thiệu) '
  'và trang quản trị /admin (dashboard, đơn hàng, sản phẩm, danh mục, kho và lô hàng, khuyến mãi, khách hàng, báo cáo, người dùng và phân quyền). Menu trang quản trị hiển thị theo vai trò.')
H(3, '5.2. Luồng người dùng (User Flow)')
IMGF('userflow.png', 'Luồng người dùng chính: từ tìm sản phẩm đến theo dõi đơn hàng')
P('Luồng chính của khách gồm 10 bước từ trang chủ đến theo dõi đơn. Hệ thống chỉ yêu cầu đăng nhập khi khách bắt đầu đặt hàng để không cản trở việc xem sản phẩm; '
  'trang Checkout gom địa chỉ, phí ship, mã giảm giá và phương thức thanh toán trên một màn hình để khách hoàn tất đơn trong ≤ 3 phút (NFR10).')
H(3, '5.3. Thiết kế bố cục giao diện (Wireframe)')
IMGF('wf_trangchu.png', 'Wireframe trang chủ', 14.5)
IMGF('wf_chitiet.png', 'Wireframe trang chi tiết sản phẩm', 14.5)
IMGF('wf_checkout.png', 'Wireframe trang thanh toán (Checkout)', 14.5)
IMGF('wf_admin.png', 'Wireframe trang quản trị – Quản lý đơn hàng', 14.5)
P('Wireframe thể hiện bố cục khung của các màn hình quan trọng nhất. Trang chi tiết hiển thị hạn sử dụng lô gần nhất và số lượng còn – thông tin khách thường phải nhắn tin hỏi trong quy trình cũ; '
  'trang Checkout hiển thị rõ hạn mức COD và tổng tiền sau phí ship, giảm giá; trang quản trị đơn hàng nhóm đơn theo tab trạng thái để nhân viên xử lý nhanh.')
H(3, '5.4. Thiết kế Mockup, Prototype và Design System')
P('Từ wireframe, nhóm dựng mockup và prototype có thể bấm thử trên Figma cho các luồng: đặt hàng COD, thanh toán VNPay, xác nhận đơn và tạo vận đơn. Prototype được dùng trong Sprint Review để Product Owner góp ý trước khi lập trình.')
caption('bang', 'Design System của website SweetMart')
T(['Thành phần', 'Quy định'],
  [['Màu chủ đạo', 'Hồng dâu #E85D8A – nút chính, giá bán, điểm nhấn thương hiệu'],
   ['Màu phụ', 'Nâu socola #6B3E26 (tiêu đề), kem #FFF8F0 (nền), xanh lá #2E9E5B (thành công, còn hàng), đỏ #D64545 (lỗi, cận date)'],
   ['Kiểu chữ', 'Be Vietnam Pro: tiêu đề 24–32px đậm; nội dung 16px; chú thích 14px'],
   ['Nút bấm', 'Bo góc 8px; nút chính nền hồng chữ trắng; nút phụ viền hồng; hover tối hơn 10%'],
   ['Thẻ sản phẩm', 'Ảnh tỷ lệ 1:1, tên tối đa 2 dòng, giá màu hồng đậm, nhãn "Giảm giá" / "Sắp hết hạn"'],
   ['Biểu mẫu', 'Nhãn phía trên ô nhập; thông báo lỗi màu đỏ ngay dưới ô'],
   ['Responsive', '< 640px: 2 cột sản phẩm; 640–1024px: 3 cột; > 1024px: 4–5 cột'],
   ['Biểu tượng', 'Bộ icon Lucide, nét 1.5px']],
  [3.6, 12.3])

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'buoc45.py'), encoding='utf-8').read())

doc.save(OUT)
print('saved', cnt)
