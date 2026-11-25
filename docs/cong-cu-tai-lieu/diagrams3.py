from diagrams import *  # noqa
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, Rectangle


def roadmap():
    fig, ax = new(11, 5.2)
    x0, wk = 2.3, 0.56
    for w in range(1, 16):
        x = x0 + (w - 1) * wk
        ax.add_patch(Rectangle((x, 0.5), wk, 4.0, fc='#F7FBFB' if w % 2 else 'white', ec='#E5E7EB', lw=0.6))
        ax.text(x + wk / 2, 4.65, str(w), ha='center', fontsize=8, color=GREY)
    ax.text(x0 - 0.1, 4.65, 'Tuần', ha='right', fontsize=8, color=GREY)
    rows = [('Sprint 0 – Khởi tạo, yêu cầu, thiết kế', 1, 2, LIGHT), ('Sprint 1 – Tài khoản, phân quyền, SP', 3, 4, 'white'),
            ('Sprint 2 – Tìm kiếm, kho lô, giỏ hàng', 5, 6, 'white'), ('Sprint 3 – Đặt hàng, VNPay, xử lý đơn', 7, 8, 'white'),
            ('Sprint 4 – GHN, email, mã giảm giá', 9, 10, 'white'), ('Sprint 5 – Báo cáo, hoàn thiện, đóng gói', 11, 12, 'white'),
            ('UAT, tài liệu, bảo vệ', 13, 15, PINK)]
    for i, (t, a, b, fc) in enumerate(rows):
        y = 4.1 - i * 0.52
        ax.text(0.1, y, t.split(' – ')[0], va='center', fontsize=8.5, color=NAVY, fontweight='bold')
        ax.add_patch(FancyBboxPatch((x0 + (a - 1) * wk + 0.03, y - 0.18), (b - a + 1) * wk - 0.06, 0.36,
                                    boxstyle='round,pad=0,rounding_size=0.06', fc=fc, ec=ORANGE if fc == PINK else TEAL, lw=1.2))
        ax.text(x0 + (b) * wk + 0.1, y, t.split(' – ')[1] if ' – ' in t else '', va='center', fontsize=7.8, color=NAVY)
    ms = [(6, 'v0.1'), (8, 'v0.2\nDemo giữa kỳ'), (10, 'v0.3'), (12, 'v1.0'), (15, 'Bảo vệ')]
    for w, t in ms:
        x = x0 + w * wk
        ax.add_patch(Polygon([(x, 0.95), (x + 0.12, 0.8), (x, 0.65), (x - 0.12, 0.8)], fc=ORANGE, ec=ORANGE))
        ax.plot([x, x], [0.95, 4.4], color=ORANGE, lw=0.8, ls=(0, (3, 3)))
        ax.text(x, 0.45, t, ha='center', va='top', fontsize=7.5, color=ORANGE, fontweight='bold')
    ax.set_ylim(-0.25, 5.0)
    save(fig, 'roadmap.png')


def burndown():
    fig, ax = plt.subplots(figsize=(8, 4.2))
    days = list(range(0, 11))
    ideal = [21 - 2.1 * d for d in days]
    actual = [21, 21, 19, 19, 16, 13, 13, 10, 6, 3, 0]
    ax.plot(days, ideal, color=GREY, ls='--', lw=1.5, label='Đường lý tưởng')
    ax.plot(days, actual, color=TEAL, marker='o', lw=2, label='Story Point còn lại (minh họa)')
    ax.set_xticks(days); ax.set_xlabel('Ngày làm việc trong Sprint 1', fontsize=9); ax.set_ylabel('Story Point còn lại', fontsize=9)
    ax.set_ylim(0, 23); ax.grid(alpha=0.3); ax.legend(fontsize=8.5, frameon=False)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.set_title('Burndown Chart – Sprint 1 (21 SP)', fontsize=10, color=NAVY, fontweight='bold')
    fig.savefig(os.path.join(OUT, 'burndown.png'), dpi=220, bbox_inches='tight', facecolor='white'); plt.close(fig)


def board():
    fig, ax = new(11, 5.6)
    cols = ['To Do', 'In Progress', 'Code Review', 'Testing', 'Done']
    cards = {
        'To Do': [('T06', 'API GET /products phân trang', 'TV4'), ('T09', 'Trang danh sách SP', 'TV3'), ('T10', 'Test API sản phẩm', 'TV5')],
        'In Progress': [('T05', 'API CRUD sản phẩm + upload ảnh', 'TV4'), ('T08', 'Form quản lý SP (admin)', 'TV3')],
        'Code Review': [('T04', 'Phân quyền [Authorize(Roles)]', 'TV2')],
        'Testing': [('T03', 'Trang đăng ký / đăng nhập', 'TV3')],
        'Done': [('T01', 'Khởi tạo repo, CI, Docker SQL', 'TV5'), ('T02', 'API đăng ký, đăng nhập JWT', 'TV4')],
    }
    w = 2.05
    for i, c in enumerate(cols):
        x = 0.15 + i * (w + 0.12)
        ax.add_patch(FancyBboxPatch((x, 0.15), w, 5.0, boxstyle='round,pad=0,rounding_size=0.08', fc='#F3F4F6', ec='#E5E7EB'))
        ax.text(x + w / 2, 4.9, f'{c} ({len(cards[c])})', ha='center', fontsize=9, fontweight='bold', color=NAVY)
        for j, (code, t, who) in enumerate(cards[c]):
            y = 4.45 - j * 1.05
            ax.add_patch(FancyBboxPatch((x + 0.1, y - 0.85), w - 0.2, 0.85, boxstyle='round,pad=0,rounding_size=0.06',
                                        fc='white', ec=TEAL if c != 'Done' else '#2E9E5B', lw=1.1))
            ax.text(x + 0.2, y - 0.17, code, fontsize=7.5, color=ORANGE, fontweight='bold')
            ax.text(x + 0.2, y - 0.45, t, fontsize=7.2, color=NAVY, wrap=True)
            ax.text(x + w - 0.2, y - 0.72, '@' + who, fontsize=7, color=GREY, ha='right')
    save(fig, 'scrumboard.png')


def gitflow():
    fig, ax = new(11, 4.2)
    lanes = [('main', 3.6, NAVY), ('develop', 2.6, TEAL), ('feature/US12-dat-hang-cod', 1.6, ORANGE), ('feature/US15-thanh-toan-vnpay', 0.6, '#8B5CF6')]
    for n, y, c in lanes:
        ax.text(0.1, y, n, va='center', fontsize=8, color=c, fontweight='bold')
    X0 = 3.2
    def dot(x, y, c): ax.add_patch(Circle((x, y), 0.1, fc=c, ec='white', lw=1.2, zorder=3))
    def ln(p, q, c): ax.plot([p[0], q[0]], [p[1], q[1]], color=c, lw=2, zorder=2)
    ln((X0, 3.6), (10.8, 3.6), NAVY); ln((X0, 2.6), (10.8, 2.6), TEAL)
    dot(X0, 3.6, NAVY); ax.text(X0, 3.85, 'v0.1', ha='center', fontsize=7.5, color=NAVY)
    ln((X0, 3.6), (X0 + 0.5, 2.6), TEAL); dot(X0 + 0.5, 2.6, TEAL)
    ln((X0 + 0.9, 2.6), (X0 + 1.3, 1.6), ORANGE); ln((X0 + 1.3, 1.6), (X0 + 3.6, 1.6), ORANGE)
    for x in (X0 + 1.3, X0 + 2.0, X0 + 2.8, X0 + 3.6): dot(x, 1.6, ORANGE)
    ln((X0 + 3.6, 1.6), (X0 + 4.1, 2.6), ORANGE); dot(X0 + 4.1, 2.6, TEAL)
    ax.text(X0 + 4.1, 2.85, 'PR #12\n(squash)', ha='center', fontsize=7, color=TEAL)
    ln((X0 + 1.6, 2.6), (X0 + 2.1, 0.6), '#8B5CF6'); ln((X0 + 2.1, 0.6), (X0 + 5.2, 0.6), '#8B5CF6')
    for x in (X0 + 2.1, X0 + 3.0, X0 + 4.3, X0 + 5.2): dot(x, 0.6, '#8B5CF6')
    ln((X0 + 5.2, 0.6), (X0 + 5.7, 2.6), '#8B5CF6'); dot(X0 + 5.7, 2.6, TEAL)
    ax.text(X0 + 5.7, 2.85, 'PR #15', ha='center', fontsize=7, color=TEAL)
    ln((X0 + 6.3, 2.6), (X0 + 6.8, 3.6), TEAL); dot(X0 + 6.8, 3.6, NAVY)
    ax.text(X0 + 6.8, 3.85, 'v0.2 (demo giữa kỳ)', ha='center', fontsize=7.5, color=NAVY)
    ax.text(X0 + 2.4, 1.85, 'feat(order): tạo đơn COD', fontsize=6.8, color=GREY)
    ax.text(X0 + 3.1, 0.85, 'feat(payment): xác thực IPN', fontsize=6.8, color=GREY)
    save(fig, 'gitflow.png')


def cicd():
    fig, ax = new(11, 3.0)
    st = [('Push / Pull Request', 'GitHub', LIGHT), ('Build Backend', 'dotnet build', 'white'), ('Unit Test', 'xUnit + coverage', 'white'),
          ('Build Frontend', 'npm ci, lint, build', 'white'), ('Docker Build', 'image api, web', 'white'), ('Deploy Staging', 'chỉ nhánh develop', PINK)]
    w = 1.6
    for i, (a, b, fc) in enumerate(st):
        x = 0.95 + i * 1.85
        box(ax, x, 1.7, w, 0.95, f'{a}\n', fc=fc, ec=ORANGE if fc == PINK else TEAL, fs=8.3, bold=True, r=0.1)
        ax.text(x, 1.5, b, ha='center', fontsize=7.3, color=GREY)
        if i: arrow(ax, (x - 1.85 + w / 2, 1.7), (x - w / 2, 1.7))
    ax.text(5.5, 0.6, 'Nếu một bước lỗi → pipeline đỏ, Pull Request không được merge (quy định trong DoD)', ha='center', fontsize=8, color=ORANGE)
    save(fig, 'cicd.png')


if __name__ == '__main__':
    roadmap(); burndown(); board(); gitflow(); cicd(); print('done3')
