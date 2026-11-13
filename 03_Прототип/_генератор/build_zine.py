# -*- coding: utf-8 -*-
"""Генератор зин-буклета: один лист A4 (альбомный), 8 панелей, верхний ряд повёрнут на 180°.
Раскладка (на листе):  верх (вверх ногами): 5 4 3 2   низ: 6 7 8 1
Развороты: 2-3 «Палуба», 4-5 «Карта», 6-7 «Порт»; 1 — обложка, 8 — оборот (памятка + журнал рейсов).
Единицы — миллиметры. Безопасное поле от края листа 5 мм, от внутренних сгибов 3 мм.
"""
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))

SANS = "'Segoe UI', Arial, sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"
SYM = "'Segoe UI Symbol', 'Segoe UI Emoji', sans-serif"
PT = 0.3528
OUT_PAD, IN_PAD = 5.0, 3.0
PW, PH = 74.25, 105.0
INK, GRAY, LIGHT = '#111', '#777', '#ddd'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def T(x, y, s, pt=7, anchor='start', weight='normal', fill=INK, family=SANS, italic=False, ls=0):
    st = 'font-style:italic;' if italic else ''
    lsp = ' letter-spacing="%s"' % ls if ls else ''
    return ('<text x="%.2f" y="%.2f" font-size="%.2f" text-anchor="%s" font-weight="%s" fill="%s" '
            'font-family="%s" style="%s"%s>%s</text>' % (x, y, pt * PT, anchor, weight, fill, family, st, lsp, esc(s)))


def R(x, y, w, h, rx=1.2, sw=0.3, fill='none', stroke=INK, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" fill="%s" stroke="%s" stroke-width="%.2f"%s/>' % (
        x, y, w, h, rx, fill, stroke, sw, d)


def L(x1, y1, x2, y2, sw=0.3, stroke=INK, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f"%s/>' % (x1, y1, x2, y2, stroke, sw, d)


def C(cx, cy, r, sw=0.3, fill='none', stroke=INK, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s" stroke="%s" stroke-width="%.2f"%s/>' % (cx, cy, r, fill, stroke, sw, d)


# ------------------------------------------------------------------ ячейки выбора
def choice_spread(x0, y0, title, subtitle, footer, theme):
    o = []
    spine = x0 + PW
    # заголовок
    o.append(T(x0 + OUT_PAD, y0 + 11.2, title, 17, weight='bold', family=SERIF, ls=0.6))
    o.append(T(x0 + OUT_PAD, y0 + 14.8, subtitle, 5.6, fill=GRAY))
    o.append(T(spine + IN_PAD, y0 + 9.0, 'ПОРЯДОК РАУНДА', 5.6, weight='bold'))
    o.append(T(spine + IN_PAD, y0 + 12.0, '1 Эпизод  ·  2 Выбор (по убыванию Славы, 60 с)', 5.2, fill=INK))
    o.append(T(spine + IN_PAD, y0 + 14.8, '3 Действия 1→8  ·  4 Конец раунда', 5.2, fill=INK))
    top = y0 + OUT_PAD + 12.5
    ch, gap = 18.0, 1.1
    cw = PW - OUT_PAD - IN_PAD
    for i in range(8):
        n = i + 1
        page_right = i >= 4
        x = (spine + IN_PAD) if page_right else (x0 + OUT_PAD)
        y = top + (i % 4) * (ch + gap)
        personal = n <= 4
        o.append(R(x, y, cw, ch, 1.6, 0.35))
        # номер
        o.append(C(x + 5.2, y + 5.2, 3.6, fill=INK, stroke=INK))
        o.append(T(x + 5.2, y + 6.75, str(n), 11, 'middle', 'bold', fill='#fff', family=SERIF))
        # метки: обязательно / заблокировано — отмечаются карандашом
        o.append(R(x + 10.2, y + 2.0, 4.2, 4.2, 0.6, 0.3))
        o.append(T(x + 12.3, y + 5.5, '!', 7, 'middle', 'bold'))
        o.append(R(x + 15.8, y + 2.0, 4.2, 4.2, 0.6, 0.3))
        o.append(T(x + 17.9, y + 5.3, '✗', 6.5, 'middle', 'bold', family=SYM))
        o.append(T(x + 21.4, y + 3.6, 'обяз.', 3.6, fill=GRAY))
        o.append(T(x + 21.4, y + 6.0, 'блок', 3.6, fill=GRAY))
        # линия для заметки карандашом
        o.append(L(x + 10.2, y + ch - 4.2, x + 29, y + ch - 4.2, 0.25, GRAY))
        o.append(T(x + 10.2, y + ch - 1.5, 'что даёт (карандаш)', 3.5, fill=GRAY))
        zx = x + 31
        if personal:
            o.append(C(zx + 17, y + ch / 2, 8.1, 0.5))
            o.append(T(zx + 1.5, y + 3.2, 'личное', 3.5, fill=GRAY))
        else:
            o.append(R(zx + 1, y + 1.2, cw - 31 - 2, ch - 2.4, 1.6, 0.35, dash='1.6 1.2'))
            o.append(T(zx + 17.2, y + ch - 1.2, 'общее', 3.5, 'middle', fill=GRAY))
    # подвал
    o.append(T(x0 + OUT_PAD, y0 + PH - OUT_PAD + 0.2, footer, 5.2, weight='bold'))
    o.append(T(spine + IN_PAD, y0 + PH - OUT_PAD + 0.2, 'Проверка: d6 + навык 0–4 + бонусы  ·  ≤3 · 4–6 · 7–9 · 10+', 5.2, fill=INK))
    # оформление темы
    if theme == 'deck':
        for k in range(6):
            xx = x0 + OUT_PAD + 48 + k * 3.3
            o.append('<path d="M%.2f %.2f q1.65 -1.8 3.3 0" fill="none" stroke="%s" stroke-width="0.3"/>' % (xx, y0 + 10.6, INK))
    else:
        ax, ay = x0 + OUT_PAD + 58, y0 + 6.5
        o.append('<path d="M%.2f %.2f v7 M%.2f %.2f h4 M%.2f %.2f a4 4 0 0 0 8 0" fill="none" stroke="%s" stroke-width="0.4"/>' % (
            ax + 2, ay, ax, ay + 2, ax - 2, ay + 5, INK))
    # линия сгиба-корешка (тонкая подсказка)
    return '\n'.join(o)


# ------------------------------------------------------------------ карта
def map_spread(x0, y0, cols=7, rows=6, w=14.8):
    o = []
    h = 2 * w / math.sqrt(3)
    Rr = h / 2
    gx = x0 + PW * 2 - OUT_PAD - 3.0 - (cols + 0.5) * w
    gy = y0 + OUT_PAD + 5.0
    # боковая полоса (читается снизу вверх): название и подсказки
    sx, sy = x0 + OUT_PAD, y0 + PH - OUT_PAD
    side = ['<g transform="translate(%.2f %.2f) rotate(-90)">' % (sx, sy)]
    side.append(T(0, 6.2, 'КАРТА', 14, weight='bold', family=SERIF, ls=0.6))
    side.append(T(0, 11.5, 'Значок клетки (бросок d6):', 5, weight='bold'))
    segs = [('1–2', '☀', 'штиль'), ('3', '⛈', 'шторм'), ('4', '⚓', 'корабль'), ('5', '☁', 'туман'), ('6', '△', 'остров')]
    u = 0
    for d, sy_, nm in segs:
        side.append(T(u, 15.8, d, 4.6, fill=GRAY))
        side.append(T(u + (4.6 if len(d) > 1 else 2.8), 16.2, sy_, 7, family=SYM))
        side.append(T(u + (8.8 if len(d) > 1 else 7.0), 15.8, nm, 4.6))
        u += 17 if len(d) > 1 else 15
    side.append(T(0, 19.8, 'Новая клетка: ✓ + эпизод. С ✓ — рутина.', 4.4, fill=GRAY))
    side.append('</g>')
    o.append(''.join(side))
    for r in range(1, rows + 1):
        for c in range(cols):
            cx = gx + w / 2 + c * w + (w / 2 if r % 2 == 0 else 0)
            cy = gy + Rr + (r - 1) * 0.75 * h
            pts = ' '.join('%.2f,%.2f' % (cx + Rr * math.cos(math.radians(a)), cy + Rr * math.sin(math.radians(a)))
                           for a in (-90, -30, 30, 90, 150, 210))
            o.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="0.35"/>' % (pts, INK))
            o.append(T(cx, cy + Rr * 0.74, '%s%d' % ('ABCDEFG'[c], r), 3.4, 'middle', fill=GRAY))
    for c in range(cols):
        o.append(T(gx + w / 2 + c * w, gy - 0.8, 'ABCDEFG'[c], 6, 'middle', 'bold'))
    for r in range(1, rows + 1):
        o.append(T(gx - 1.9, gy + Rr + (r - 1) * 0.75 * h + 1.0, str(r), 6, 'middle', 'bold'))
    return '\n'.join(o)


# ------------------------------------------------------------------ оборот
def back_panel(x0, y0):
    o = []
    x = x0 + IN_PAD
    wd = PW - IN_PAD - IN_PAD
    y = y0 + OUT_PAD + 3.5
    o.append(T(x, y, 'ПАМЯТКА', 8.5, weight='bold', family=SERIF, ls=0.5))
    lines = [
        ('РАУНД', '1 Эпизод · 2 Выбор (по Славе) · 3 Действия 1→8 · 4 Конец'),
        ('КОНЕЦ', 'Ром 0 → Ропот +1 · края шкал'),
        ('ПРОВЕРКА', 'd6 + навык + бонусы: ≤3 · 4–6 · 7–9 · 10+'),
        ('УДАЧА', '−1 Удачи = перебросить свой кубик'),
        ('ХОД/РАЗВЕДКА', 'Ход — на соседнюю клетку; разведка — d6 → значок'),
        ('ПОРАЖЕНИЕ', 'Корпус/Команда 0 · Ропот ≥ Команды'),
    ]
    y += 4.3
    for k, v in lines:
        y += 1.4
        o.append(T(x, y, k, 4.6, weight='bold'))
        # перенос по ~34 знакам
        words, cur, row = v.split(' '), '', []
        for wd_ in words:
            if len(cur + ' ' + wd_) > 58:
                row.append(cur)
                cur = wd_
            else:
                cur = (cur + ' ' + wd_).strip()
        row.append(cur)
        for t in row:
            y += 3.0
            o.append(T(x, y, t, 4.8))
        y += 1.6
    y += 0.5
    o.append(L(x, y, x + wd, y, 0.5))
    y += 5.0
    o.append(T(x, y, 'ЖУРНАЛ РЕЙСОВ', 8.5, weight='bold', family=SERIF, ls=0.5))
    y += 3.2
    o.append(T(x, y, 'Итог: ✔ дошли / ✖ погибли. Слово или артефакт — по приложению.', 4.4, fill=GRAY))
    y += 2.2
    hdr = ['№', 'Корабль', 'Итог', 'Слово / артефакт']
    xs = [x, x + 5, x + 27, x + 36]
    rowh = 5.4
    nrows = int((y0 + PH - OUT_PAD - y - 3) / rowh)
    o.append(R(x, y, wd, rowh * (nrows + 1), 0.8, 0.35))
    for i, hh in enumerate(hdr):
        o.append(T(xs[i] + 1, y + 3.7, hh, 4.4, weight='bold'))
    for i in range(1, nrows + 1):
        o.append(L(x, y + rowh * i, x + wd, y + rowh * i, 0.2, GRAY))
        o.append(T(xs[0] + 1, y + rowh * (i + 1) - 1.5, str(i), 4.2, fill=GRAY))
    for xx in xs[1:]:
        o.append(L(xx, y, xx, y + rowh * (nrows + 1), 0.2, GRAY))
    return '\n'.join(o)


# ------------------------------------------------------------------ обложка
def cover_panel(x0, y0):
    o = []
    cx = x0 + PW / 2
    o.append(R(x0 + 4, y0 + 5, PW - 9, PH - 10, 2.0, 0.6))
    o.append(R(x0 + 5.3, y0 + 6.3, PW - 11.6, PH - 12.6, 1.4, 0.25))
    o.append(T(cx, y0 + 17, 'ВСЕМ', 19, 'middle', 'bold', family=SERIF, ls=1.2))
    o.append(T(cx, y0 + 26.5, 'КОСТЯМ', 19, 'middle', 'bold', family=SERIF, ls=1.2))
    o.append(T(cx, y0 + 36, 'НА БОРТ!', 19, 'middle', 'bold', family=SERIF, ls=1.2))
    # корабль
    s = []
    bx, by = x0 + 10, y0 + 42
    s.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Q%.1f %.1f %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="0.4"/>' % (
        bx + 3, by + 28, bx + 51, by + 28, bx + 45, by + 38, bx + 27, by + 42, bx + 9, by + 38, '#fff', INK))
    s.append(L(bx + 27, by + 4, bx + 27, by + 28, 0.6))
    s.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#fff" stroke="%s" stroke-width="0.4"/>' % (
        bx + 27, by + 6, bx + 47, by + 24, bx + 27, by + 24, INK))
    s.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#fff" stroke="%s" stroke-width="0.4"/>' % (
        bx + 25, by + 8, bx + 8, by + 24, bx + 25, by + 24, INK))
    # череп на парусе
    sx, sy = bx + 37, by + 15
    s.append(C(sx, sy, 3.2, 0.35, '#fff'))
    s.append(R(sx - 1.8, sy + 2.4, 3.6, 2.2, 0.4, 0.3, '#fff'))
    s.append(C(sx - 1.2, sy - 0.2, 0.8, 0.2, INK, INK))
    s.append(C(sx + 1.2, sy - 0.2, 0.8, 0.2, INK, INK))
    s.append('<path d="M%.1f %.1f l5 1.5 l-5 1.5 z" fill="%s"/>' % (bx + 27, by + 3.5, INK))
    # волны
    for i in range(7):
        s.append('<path d="M%.1f %.1f q2.5 -2.2 5 0 t5 0" fill="none" stroke="%s" stroke-width="0.35"/>' % (
            bx - 4 + i * 8.5, by + 40 + (i % 2) * 2.5, INK))
    o.append('\n'.join(s))
    o.append(T(cx, y0 + 90.5, 'Полукооперативная игра про скелетов', 4.8, 'middle', italic=True))
    o.append(T(cx, y0 + 94.0, '2–6 игроков · 60–90 мин · буклет + телефон + карандаш + d6', 4.2, 'middle', fill=GRAY))
    o.append(T(cx, y0 + 97.0, 'Прототип v0.1 · свободное плавание', 4.2, 'middle', fill=GRAY))
    return '\n'.join(o)


# ------------------------------------------------------------------ сборка листа
def build():
    from parts_new import map_spread, port_spread, battle_panel, deck_page, back_panel as back_panel2
    top = []   # верхний ряд, до поворота: 2 3 | 4 5
    top.append(deck_page(0, 0))
    top.append(battle_panel(PW, 0))
    top.append(map_spread(PW * 2, 0))
    bottom = []  # 6 7 | 8 | 1
    bottom.append(port_spread(0, 0))
    bottom.append(back_panel2(PW * 2, 0))
    bottom.append(cover_panel(PW * 3, 0))

    marks = []
    for xv in (PW, PW * 2, PW * 3):
        marks.append(L(xv, 0, xv, 2.2, 0.2, '#999'))
        marks.append(L(xv, 207.8, xv, 210, 0.2, '#999'))
    marks.append(L(0, 105, 2.2, 105, 0.2, '#999'))
    marks.append(L(294.8, 105, 297, 105, 0.2, '#999'))
    marks.append(L(PW, 105, PW * 3, 105, 0.35, '#888', '1.2 1.2'))
    marks.append(T(PW * 2, 104.2, '✂ разрез по центру', 3.4, 'middle', fill='#888', family=SYM))

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210">'
           '<rect width="297" height="210" fill="#fff"/>'
           '<g transform="rotate(180 148.5 52.5)">%s</g>'
           '<g transform="translate(0 105)">%s</g>%s</svg>') % ('\n'.join(top), '\n'.join(bottom), '\n'.join(marks))
    html = ('<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Всем костям на борт! — буклет A4</title>'
            '<style>@page{size:A4 landscape;margin:0}html,body{margin:0;padding:0;background:#fff}'
            'svg{display:block}@media screen{body{background:#ccc}svg{margin:10px auto;box-shadow:0 0 6px #666}}</style></head>'
            '<body>%s</body></html>') % svg
    return html


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '..', 'Буклет_A4.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(build())
    print('ok', os.path.abspath(out))
