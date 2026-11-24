# -*- coding: utf-8 -*-
"""Блоки буклета v3: палуба (слоты по краям + арт), карта 7x6, порт (2x2 + магазин + игорный дом), боевой планшет.
Минимальный размер текста: 5 pt (на печати читаемо), основной 5.5-6 pt."""
import math
from build_zine import T, R, L, C, OUT_PAD, IN_PAD, PW, PH, INK, GRAY, SERIF, SANS, SYM
from content import BETS, SHOP, CATCH
from icons import svg_image

UPG = [('Не считается!', 'переброс 1-го провала', 1), ('Большой палец', 'переброс обоих', 2),
       ('Поручитель', 'вернуть ставку', 2), ('Всё или ничего', 'прибыль ×2', 3),
       ('Кость в рукаве', 'переброс 1 кубика', 5)]



def ico(kind, cx, cy, k=1.0, sw=0.45, col=INK):
    """Простые линейные значки (размер ~7 мм при k=1)."""
    o = []
    st = 'fill="none" stroke="%s" stroke-width="%.2f" stroke-linecap="round" stroke-linejoin="round"' % (col, sw)
    def P(d):
        return '<path d="%s" %s transform="translate(%.2f %.2f) scale(%.3f)"/>' % (d, st, cx, cy, k)
    def Cc(x, y, r, fill=False):
        return '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s" stroke="%s" stroke-width="%.2f" transform="translate(%.2f %.2f) scale(%.3f)"/>' % (
            x, y, r, col if fill else 'none', col, sw / k, cx, cy, k)
    if kind == 'wave':       # тильда: штиль
        o.append(P('M-3.5 0 q1.75 -2.4 3.5 0 t3.5 0'))
    elif kind == 'zig':      # ломаная линия: особый штиль
        o.append(P('M-3.5 1.2 L-1.8 -1.2 L0 1.2 L1.8 -1.2 L3.5 1.2'))
    elif kind == 'bolt':     # молния: шторм
        o.append(P('M0.8 -3.6 L-2 0.4 L0 0.4 L-0.8 3.6 L2.2 -0.6 L0.2 -0.6 Z'))
    elif kind == 'cross':    # крест: провал
        o.append(P('M-2.6 -2.6 L2.6 2.6 M2.6 -2.6 L-2.6 2.6'))
    elif kind == 'helm':     # штурвал
        o.append(Cc(0, 0, 2.0))
        o.append(Cc(0, 0, 0.6, True))
        o.append(P(''.join('M%.2f %.2f L%.2f %.2f ' % (0.6 * math.cos(a), 0.6 * math.sin(a), 3.6 * math.cos(a), 3.6 * math.sin(a))
                           for a in [i * math.pi / 4 for i in range(8)])))
    elif kind == 'sun':
        o.append(Cc(0, 0, 1.5))
        o.append(P(''.join('M%.2f %.2f L%.2f %.2f ' % (2.4 * math.cos(a), 2.4 * math.sin(a), 3.6 * math.cos(a), 3.6 * math.sin(a))
                           for a in [i * math.pi / 4 for i in range(8)])))
    elif kind == 'moon':
        o.append(P('M1.4 -3.2 A3.4 3.4 0 1 0 3.2 1.6 A2.8 2.8 0 0 1 1.4 -3.2 Z'))
    elif kind == 'skull':
        o.append(P('M-2.8 0.6 A3 3.2 0 1 1 2.8 0.6 L2.2 2.2 L1.6 2.2 L1.6 3.4 L-1.6 3.4 L-1.6 2.2 L-2.2 2.2 Z'))
        o.append(Cc(-1.2, -0.4, 0.7, True))
        o.append(Cc(1.2, -0.4, 0.7, True))
        o.append(P('M-0.3 1.2 L0.3 1.2 M-0.5 2.6 L-0.5 3.4 M0.5 2.6 L0.5 3.4'))
    elif kind == 'parrot':
        o.append(Cc(-0.4, -2.0, 1.4))
        o.append(Cc(-0.8, -2.3, 0.3, True))
        o.append(P('M-1.6 -2.5 Q-3.8 -2.2 -3.2 -0.6 Q-2.6 -1.2 -1.6 -1.3'))
        o.append(P('M0.4 -0.7 Q2.8 0.2 2.0 3.2 L0 2.6 Q-1.2 1.2 -1.0 -0.4'))
        o.append(P('M1.2 2.9 L2.6 4.4 M0.6 2.7 L1.1 4.6'))
    elif kind == 'goblin':
        o.append(Cc(0, 0.6, 2.2))
        o.append(P('M-2.1 -0.2 L-4.0 -2.0 L-2.0 1.2 M2.1 -0.2 L4.0 -2.0 L2.0 1.2'))
        o.append(Cc(-0.9, 0.1, 0.4, True))
        o.append(Cc(0.9, 0.1, 0.4, True))
        o.append(P('M-1.3 1.8 L-0.6 1.1 L0 1.8 L0.6 1.1 L1.3 1.8'))
    elif kind == 'mage':
        o.append(P('M0 -4.2 L-2.2 0.2 L2.2 0.2 Z M-3.2 0.2 L3.2 0.2'))
        o.append(Cc(0, 1.8, 1.3))
        o.append(P('M-1.0 2.9 L0 4.2 L1.0 2.9'))
        o.append(P('M-0.4 -1.4 L0.4 -1.4 M0 -1.8 L0 -1.0'))
    return ''.join(o)


def coin(x, y, n):
    """Монета с ценой внутри."""
    return C(x, y, 1.65, 0.35) + T(x, y + 0.55, str(n), 4.2, 'middle', 'bold')


def wrap(s, n):
    words, cur, rows = s.split(' '), '', []
    for w_ in words:
        if len((cur + ' ' + w_).strip()) > n:
            rows.append(cur)
            cur = w_
        else:
            cur = (cur + ' ' + w_).strip()
    rows.append(cur)
    return rows


def badge(x, y, n, r=3.6, pt=11):
    return C(x, y, r, fill=INK, stroke=INK) + T(x, y + pt * 0.3528 * 0.36, str(n), pt, 'middle', 'bold', '#fff', SERIF)


# ------------------------------------------------------------------ палуба
def deck_spread(x0, y0):
    o = []
    sh = 22.0
    gap = (PH - 2 * OUT_PAD - 4 * sh) / 3
    # левая колонка: личные слоты 1-4 (кружок под кубик)
    lx, lw = x0 + OUT_PAD, 27.0
    for i in range(4):
        y = y0 + OUT_PAD + i * (sh + gap)
        o.append(R(lx, y, lw, sh, 1.8, 0.4))
        o.append(badge(lx + 5.0, y + 5.4, i + 1))
        o.append(C(lx + lw - 9.6, y + sh / 2 + 0.6, 8.2, 0.55))
    # правая колонка: общие слоты 5-8 (пунктир под несколько кубиков)
    rw = 43.0
    rx = x0 + 2 * PW - OUT_PAD - rw
    for i in range(4):
        y = y0 + OUT_PAD + i * (sh + gap)
        o.append(R(rx, y, rw, sh, 1.8, 0.4))
        o.append(badge(rx + 5.0, y + 5.4, i + 5))
        o.append(R(rx + 10.4, y + 1.3, rw - 11.7, sh - 2.6, 1.6, 0.4, dash='1.8 1.3'))
    # центр: арт палубы (вид сверху)
    cx = x0 + PW  # спина разворота
    o.append(T(cx, y0 + OUT_PAD + 5.0, 'ПАЛУБА', 17, 'middle', 'bold', family=SERIF, ls=0.8))
    o.append(T(cx, y0 + OUT_PAD + 10.0, 'Эпизод → Выбор → Действия 1–7 → Конец', 5.5, 'middle', fill=GRAY))
    t = y0 + 19.0
    b = y0 + 95.0
    hull = ('M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f L%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f Z' % (
        cx, t, cx + 23, t + 12, cx + 26, b - 38, cx + 21, b, cx - 21, b, cx - 26, b - 38, cx - 23, t + 12, cx, t))
    o.append('<clipPath id="hullclip"><path d="%s"/></clipPath>' % hull)
    o.append('<path d="%s" fill="#f1f1f1" stroke="%s" stroke-width="0.7"/>' % (hull, INK))
    planks = ''.join('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#999" stroke-width="0.25"/>' % (cx - 40, yy, cx + 40, yy)
                     for yy in [t + 4 + k * 4.2 for k in range(int((b - t) / 4.2))])
    o.append('<g clip-path="url(#hullclip)">%s</g>' % planks)
    o.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.7"/>' % (hull, INK))
    # бушприт
    o.append(L(cx, t - 2.5, cx, t + 4, 0.7))
    # мачта и рея
    my = t + 30
    o.append(L(cx - 15, my, cx + 15, my, 0.8))
    o.append(C(cx, my, 3.3, 0.7, '#fff'))
    o.append(C(cx, my, 1.0, 0.3, INK, INK))
    # череп-флаг на рее
    o.append(C(cx + 9, my - 5.2, 2.3, 0.4, '#fff'))
    o.append(C(cx + 8.2, my - 5.5, 0.6, 0.2, INK, INK))
    o.append(C(cx + 9.8, my - 5.5, 0.6, 0.2, INK, INK))
    # люк
    o.append(R(cx - 6, my + 12, 12, 8, 0.8, 0.5, '#fff'))
    for k in range(3):
        o.append(L(cx - 6, my + 14.6 + k * 2.4, cx + 6, my + 14.6 + k * 2.4, 0.2, GRAY))
    # пушки по бортам
    for yy in (my - 4, my + 8, my + 21):
        o.append(R(cx - 25.5 + (0 if yy > my - 6 else 1.5), yy, 6.5, 2.6, 0.6, 0.45, '#fff'))
        o.append(R(cx + 19.0 - (0 if yy > my - 6 else 1.5), yy, 6.5, 2.6, 0.6, 0.45, '#fff'))
    # бочки
    for dx in (-13, 13):
        o.append(C(cx + dx, b - 21, 3.3, 0.5, '#fff'))
        o.append(C(cx + dx, b - 21, 1.5, 0.25, GRAY))
    # штурвал
    wy = b - 9
    o.append(C(cx, wy, 5.6, 0.6, '#fff'))
    o.append(C(cx, wy, 1.4, 0.4, INK, INK))
    for k in range(8):
        a = math.radians(k * 45)
        o.append(L(cx + 1.4 * math.cos(a), wy + 1.4 * math.sin(a), cx + 7.2 * math.cos(a), wy + 7.2 * math.sin(a), 0.4))
    o.append(T(cx, y0 + PH - OUT_PAD + 0.6, 'Конец раунда: Ром 0 → Ропот +1', 6, 'middle', 'bold'))
    return '\n'.join(o)


# ------------------------------------------------------------------ карта
def map_spread(x0, y0, cols=7, rows=6, w=15.4):
    o = []
    h = 2 * w / math.sqrt(3)
    Rr = h / 2
    gx = x0 + OUT_PAD + 3.5
    gy = y0 + OUT_PAD + 8.0
    o.append(T(x0 + OUT_PAD, y0 + 10.0, 'КАРТА', 14, weight='bold', family=SERIF, ls=0.6))
    o.append(T(x0 + OUT_PAD + 34, y0 + 9.6, 'Ход — линия из клетки в клетку. Значки — карандашом.', 5.6, fill=GRAY))
    tx = x0 + PW * 2 - OUT_PAD
    side = ['<g transform="translate(%.2f %.2f) rotate(90)">' % (tx, y0 + OUT_PAD + 1)]
    side.append(T(0, 16.0, 'Значок клетки (бросок d6):', 6, weight='bold'))
    segs = [('1', 'wave', 'штиль'), ('2', 'zig', 'особый штиль'), ('3', 'bolt', 'шторм'),
            ('4', None, 'корабль'), ('5', None, 'туман'), ('6', None, 'остров')]
    txt = {'4': '⚓', '5': '☁', '6': '△'}
    for i, (d, kind, nm) in enumerate(segs):
        u = (i % 3) * 31.0
        ly = 11.6 if i < 3 else 8.0
        side.append(T(u, ly, d, 5.6, fill=GRAY))
        if kind:
            side.append(ico(kind, u + 6.2, ly - 1.1, 0.55, 0.5))
        else:
            side.append(T(u + 4.6, ly + 0.4, txt[d], 7.5, family=SYM))
        side.append(T(u + 9.6, ly, nm, 5.6))
    side.append(T(0, 4.6, 'Разведка: d6 → значок карандашом.', 5.5, fill=GRAY))
    side.append(T(0, 1.4, 'Значок клетки задаёт пул эпизодов.', 5.5, fill=GRAY))
    side.append('</g>')
    o.append(''.join(side))
    for r in range(1, rows + 1):
        for c in range(cols):
            cx = gx + w / 2 + c * w + (w / 2 if r % 2 == 0 else 0)
            cy = gy + Rr + (r - 1) * 0.75 * h
            pts = ' '.join('%.2f,%.2f' % (cx + Rr * math.cos(math.radians(a)), cy + Rr * math.sin(math.radians(a)))
                           for a in (-90, -30, 30, 90, 150, 210))
            o.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="0.35"/>' % (pts, INK))
            o.append(T(cx, cy + Rr * 0.74, '%s%d' % ('ABCDEFG'[c], r), 4.6, 'middle', fill=GRAY))
    for c in range(cols):
        o.append(T(gx + w / 2 + c * w, gy - 0.8, 'ABCDEFG'[c], 6.5, 'middle', 'bold'))
    for r in range(1, rows + 1):
        o.append(T(gx - 1.9, gy + Rr + (r - 1) * 0.75 * h + 1.0, str(r), 6.5, 'middle', 'bold'))
    return '\n'.join(o)


# ------------------------------------------------------------------ порт
def port_spread(x0, y0):
    o = []
    spine = x0 + PW
    # ---- левая страница: 4 слота в 2 колонки (1,3 | 2,4)
    o.append(T(x0 + OUT_PAD, y0 + 11.4, 'ПОРТ', 17, weight='bold', family=SERIF, ls=0.6))
    o.append(T(x0 + OUT_PAD, y0 + 15.2, 'В порту Ром не убывает: тут пьют за свои', 6, fill=GRAY))
    cw = (PW - OUT_PAD - IN_PAD - 1.2) / 2
    sh = 17.6
    top = y0 + 18.4
    pos = {1: (0, 0), 3: (0, 1), 2: (1, 0), 4: (1, 1)}
    for n, (c, r) in pos.items():
        x = x0 + OUT_PAD + c * (cw + 1.2)
        y = top + r * (sh + 1.2)
        if n <= 3:
            o.append(C(x + cw / 2, y + sh / 2, 8.3, 0.55))
            o.append(badge(x + 4.4, y + 4.6, n, 3.3, 10))
        else:
            o.append(R(x, y, cw, sh, 1.8, 0.4, dash='1.8 1.3'))
            o.append(badge(x + 4.4, y + 4.6, n, 3.3, 10))
    # ---- правая страница: магазин (5 столбцов в 2 блока) + колонка «Шуллерские штучки» игорного дома
    rx = spine + IN_PAD
    rw = PW - OUT_PAD - IN_PAD
    y = y0 + OUT_PAD
    o.append(T(rx, y + 5.0, 'МАГАЗИН', 9, weight='bold', family=SERIF, ls=0.4))
    zx = rx + 38
    o.append(R(zx, y + 0.4, rw - 38, 8.8, 1.6, 0.4, dash='1.8 1.3'))
    o.append(badge(zx + 4.4, y + 4.8, 5, 3.3, 10))
    colx = [rx, rx + 27.0, rx + 27.0 + 19.6]
    colws = [25.0, 19.6, 19.65]
    o.append(T(colx[1] + 19.6, y + 12.4, 'Кинь d6 на каждый столбец,', 5.2, 'middle', fill=GRAY))
    o.append(T(colx[1] + 19.6, y + 15.2, 'чтобы узнать, что в наличии', 5.2, 'middle', fill=GRAY))

    def shop_col(cx, cwid, ty, ci, head):
        o.append(R(cx, ty, cwid, 4.6, 0.3, 0.3, '#ddd'))
        ik = {'СНАРЯЖЕНИЕ': 'gear', 'ДИКОВИНКИ': 'curio', 'БОЙ': 'battle'}.get(head)
        if ik:
            o.append(svg_image(ik, cx + 2.5, ty + 2.35, 3.9))
            o.append(T(cx + 4.8, ty + 3.4, head, 4.9, 'start', 'bold'))
        else:
            o.append(T(cx + cwid / 2, ty + 3.4, head, 5.0, 'middle', 'bold'))
        for ri, (nm, pr, ef) in enumerate(SHOP[ci][1]):
            yy = ty + 4.6 + ri * 4.6
            o.append(R(cx, yy, cwid, 4.6, 0.2, 0.2, stroke=GRAY))
            o.append(T(cx + 0.9, yy + 3.3, str(ri + 1), 5.2, weight='bold'))
            o.append(T(cx + 3.6, yy + 3.3, nm, 4.0 if len(nm) > 14 else (4.3 if len(nm) > 11 else 5.0)))
            o.append(coin(cx + cwid - 2.2, yy + 2.3, pr))

    ty1 = y + 17.0
    for ci in range(3):
        shop_col(colx[ci], colws[ci], ty1, ci, SHOP[ci][0])
    # блок 2: слева «Шуллерские штучки» (игорный дом), справа от чёрной границы — БОЙ и УСЛУГИ
    ty2 = ty1 + 4.6 + 6 * 4.6 + 4.6
    gw = 26.0
    vx = rx + gw + 1.5
    # чёрная граница: от слотов через разворот, затем вниз
    sy_line = y0 + 55.5
    o.append('<polyline points="%.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="none" stroke="%s" stroke-width="0.9"/>' % (
        x0 + OUT_PAD, sy_line, vx, sy_line, vx, y0 + PH - OUT_PAD, INK))
    w2 = (rx + rw - vx - 1.5) / 2
    o.append(T(vx + 1.5, ty2 - 1.4, 'Бой, Услуги: тоже d6', 5.0, fill=GRAY))
    shop_col(vx + 1.5, w2, ty2, 3, SHOP[3][0])
    shop_col(vx + 1.5 + w2, w2, ty2, 4, SHOP[4][0])
    gx = rx
    o.append(R(gx, ty2, gw, 4.6, 0.3, 0.3, '#ddd'))
    o.append(svg_image('shuller', gx + 2.5, ty2 + 2.35, 3.9))
    o.append(T(gx + 4.8, ty2 + 3.4, 'ШУЛЛЕРСКИЕ ШТУЧКИ', 4.9, 'start', 'bold'))
    yy = ty2 + 4.6
    for i in range(7):
        rh = 5.4 if i < len(UPG) else 4.4
        o.append(R(gx, yy, gw, rh, 0.2, 0.2, stroke=GRAY))
        o.append(R(gx + 0.7, yy + 0.8, 2.8, 2.8, 0.4, 0.3))
        if i < len(UPG):
            nm, ef, pr = UPG[i]
            o.append(T(gx + 4.4, yy + 2.5, nm, 5.0, weight='bold'))
            o.append(coin(gx + gw - 2.2, yy + 2.1, pr))
            o.append(T(gx + 4.4, yy + 5.0, ef, 5.0, fill=GRAY))
        else:
            o.append(T(gx + 4.4, yy + 3.2, 'из событий', 5.0, fill=GRAY))
        yy += rh

    # ---- левая страница, низ: игорный дом (ячейка 6) и ставки
    sy = y0 + 55.5
    lx = x0 + OUT_PAD
    lw = PW - OUT_PAD - IN_PAD
    o.append(T(lx, sy + 6.0, 'ИГОРНЫЙ ДОМ', 8.5, weight='bold', family=SERIF, ls=0.3))
    o.append(T(lx, sy + 9.6, 'Каждый участник делает', 5.2, fill=GRAY))
    o.append(T(lx, sy + 12.2, 'одну ставку за посещение:', 5.2, fill=GRAY))
    o.append(T(lx, sy + 14.8, 'до 2 Сокровищ.', 5.2, fill=GRAY))
    zx = lx + 33.5
    zw = lw - 33.5
    o.append(R(zx, sy + 1.2, zw, 14.4, 1.6, 0.4, dash='1.8 1.3'))
    o.append(badge(zx + 4.4, sy + 5.2, 6, 3.3, 10))
    tx = zx + 9.0
    for k, ln in enumerate(['2d6: 6, 7, 8 — проигрыш.', 'Иначе: выплата ×2.', 'Забрать или бросить ещё.', 'Каждый успех: ×3, ×4…', 'Проигрыш: выплата 0.']):
        o.append(T(tx if k > 0 or True else zx, sy + 4.4 + k * 2.45 if k < 3 else sy + 4.4 + k * 2.45 + 0.3, ln, 5.0, fill=GRAY))
    ry0 = sy + 17.0
    rh = 5.2
    for i, (ratio, name, short, full) in enumerate(BETS):
        yy = ry0 + i * rh
        o.append(R(lx, yy, lw, rh, 0.8, 0.3, dash='1.4 1.0'))
        o.append(T(lx + 1.2, yy + 3.7, '(№%d)' % (i + 1), 5.0, weight='bold'))
        o.append(T(lx + 8.6, yy + 3.9, ratio, 8.5, weight='bold', family=SERIF))
        o.append(T(lx + 19.6, yy + 3.7, name, 5.0, weight='bold'))
        o.append(T(lx + lw - 1.0, yy + 3.7, short, 5.0, 'end', fill=GRAY))
    return '\n'.join(o)


# ------------------------------------------------------------------ боевой планшет (горизонтально)
def battle_panel(x0, y0):
    """Планшет повёрнут на 90° (книгу при бое поворачивают против часовой). Локально: 95 x 66 мм.
    Бой: общий пул кубиков, ход как в Yahtzee (бросок, 1 переброс, раскладка по станциям), враг стреляет после каждого хода."""
    W = PH - 2 * OUT_PAD
    o = []
    o.append(T(0, 5.6, 'БОРТ', 11, weight='bold', family=SERIF, ls=0.2))
    # поля врага
    ex = 22.0
    o.append(T(ex, 5.0, 'ВРАГ:', 6.0, weight='bold'))
    for lab, bx, bw in (('Корпус', ex + 11.0, 9.0), ('Урон', ex + 30.0, 5.5), ('Руль S', ex + 44.0, 5.5)):
        o.append(T(bx, 5.0, lab, 5.2))
        lw_ = 8.6 if lab == 'Корпус' else (5.6 if lab == 'Урон' else 8.4)
        o.append(R(bx + lw_, 0.6, bw, 5.4, 0.6, 0.35))
    stations = [
        ('ПУШКИ', 'eye', '≥3: +1', ['Пара и больше одинаковых:', '2·3·4·5 → урон 1·3·5·8']),
        ('ТАРАН', 'bone', '≥3: +1', ['Стрит подряд:', '3·4·5 → урон 2·4·6']),
        ('РУЛЬ', 'helm', '≥3: +1', ['Сумма кубиков ≥ S:', 'залп врага мимо']),
        ('ТРЮМ', 'grab', '≥3: +1', ['Каждый кубик 1–2:', 'Корпус +1 за кубик']),
    ]
    sw, sh, g = (W - 0.8) / 2, 16.5, 1.2
    gy = 8.0
    for i, (nm, sk, bonus, req) in enumerate(stations):
        c, r = i % 2, i // 2
        x, y = c * (sw + g), gy + r * (sh + g)
        o.append(R(x, y, sw, sh, 1.6, 0.4, dash='1.8 1.3'))
        o.append(badge(x + 3.8, y + 4.2, i + 1, 2.9, 8.5))
        o.append(T(x + 8.4, y + 5.2, nm, 7.0, weight='bold', family=SERIF))
        o.append(svg_image(sk, x + sw - 11.8, y + 4.4, 4.0))
        o.append(T(x + sw - 9.2, y + 5.4, bonus, 5.2, fill=GRAY))
        for k, line in enumerate(req):
            o.append(T(x + 2.0, y + 10.6 + k * 3.2, line, 5.4, weight='bold' if k == 1 else 'normal'))
    ry0 = gy + 2 * sh + g + 1.0
    o.append(T(0, ry0 + 2.4, 'Круг: каждый скелет ходит 1 раз: бросок 5 кубиков, 1 переброс, кубики на станции.', 4.9, fill=GRAY))
    o.append(T(0, ry0 + 5.0, 'Враг стреляет после КАЖДОГО хода. Враг 0 — победа · корабль 0 — поражение · иначе ничья (½).', 4.9, fill=GRAY))
    ry = ry0 + 6.6
    rh = 66.0 - ry
    o.append(R(0, ry, W, rh, 1.6, 0.4, dash='1.8 1.3'))
    o.append(T(2.0, ry + 4.2, 'УЛУЧШЕНИЯ КОРАБЛЯ НА БОЙ', 5.6, weight='bold'))
    o.append(T(W - 2.0, ry + 4.2, '✓ есть · ✗ потрачено', 5.0, 'end', fill=GRAY, family=SYM))
    ents = ['Смазка: Пушки +1', 'Парусина: Руль +2', '', '', '', '']
    for i, t in enumerate(ents):
        cc, rr = i // 3, i % 3
        ex2 = 2.0 + cc * (W / 2)
        ey = ry + 5.4 + rr * 3.6
        o.append(R(ex2, ey, 2.8, 2.8, 0.4, 0.3))
        if t:
            o.append(T(ex2 + 4.0, ey + 2.4, t, 5.0))
        else:
            o.append(T(ex2 + 4.0, ey + 2.4, 'из событий:', 4.8, fill=GRAY))
            o.append(L(ex2 + 17.5, ey + 2.6, ex2 + W / 2 - 3.5, ey + 2.6, 0.25, GRAY))
    gx0 = x0 + IN_PAD
    gy1 = y0 + PH - OUT_PAD
    return '<g transform="translate(%.2f %.2f) rotate(-90)">%s</g>' % (gx0, gy1, chr(10).join(o))


# ------------------------------------------------------------------ палуба
def deck_spread(x0, y0):
    o = []
    sh = 22.0
    gap = (PH - 2 * OUT_PAD - 4 * sh) / 3
    # левая колонка: личные слоты 1-4 (кружок под кубик)
    lx, lw = x0 + OUT_PAD, 27.0
    for i in range(4):
        y = y0 + OUT_PAD + i * (sh + gap)
        o.append(R(lx, y, lw, sh, 1.8, 0.4))
        o.append(badge(lx + 5.0, y + 5.4, i + 1))
        o.append(C(lx + lw - 9.6, y + sh / 2 + 0.6, 8.2, 0.55))
    # правая колонка: общие слоты 5-8 (пунктир под несколько кубиков)
    rw = 43.0
    rx = x0 + 2 * PW - OUT_PAD - rw
    for i in range(4):
        y = y0 + OUT_PAD + i * (sh + gap)
        o.append(R(rx, y, rw, sh, 1.8, 0.4))
        o.append(badge(rx + 5.0, y + 5.4, i + 5))
        o.append(R(rx + 10.4, y + 1.3, rw - 11.7, sh - 2.6, 1.6, 0.4, dash='1.8 1.3'))
    # центр: арт палубы (вид сверху)
    cx = x0 + PW  # спина разворота
    o.append(T(cx, y0 + OUT_PAD + 5.0, 'ПАЛУБА', 17, 'middle', 'bold', family=SERIF, ls=0.8))
    o.append(T(cx, y0 + OUT_PAD + 10.0, 'Эпизод → Выбор → Действия 1–7 → Конец', 5.5, 'middle', fill=GRAY))
    t = y0 + 19.0
    b = y0 + 95.0
    hull = ('M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f L%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f Z' % (
        cx, t, cx + 23, t + 12, cx + 26, b - 38, cx + 21, b, cx - 21, b, cx - 26, b - 38, cx - 23, t + 12, cx, t))
    o.append('<clipPath id="hullclip"><path d="%s"/></clipPath>' % hull)
    o.append('<path d="%s" fill="#f1f1f1" stroke="%s" stroke-width="0.7"/>' % (hull, INK))
    planks = ''.join('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#999" stroke-width="0.25"/>' % (cx - 40, yy, cx + 40, yy)
                     for yy in [t + 4 + k * 4.2 for k in range(int((b - t) / 4.2))])
    o.append('<g clip-path="url(#hullclip)">%s</g>' % planks)
    o.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.7"/>' % (hull, INK))
    # бушприт
    o.append(L(cx, t - 2.5, cx, t + 4, 0.7))
    # мачта и рея
    my = t + 30
    o.append(L(cx - 15, my, cx + 15, my, 0.8))
    o.append(C(cx, my, 3.3, 0.7, '#fff'))
    o.append(C(cx, my, 1.0, 0.3, INK, INK))
    # череп-флаг на рее
    o.append(C(cx + 9, my - 5.2, 2.3, 0.4, '#fff'))
    o.append(C(cx + 8.2, my - 5.5, 0.6, 0.2, INK, INK))
    o.append(C(cx + 9.8, my - 5.5, 0.6, 0.2, INK, INK))
    # люк
    o.append(R(cx - 6, my + 12, 12, 8, 0.8, 0.5, '#fff'))
    for k in range(3):
        o.append(L(cx - 6, my + 14.6 + k * 2.4, cx + 6, my + 14.6 + k * 2.4, 0.2, GRAY))
    # пушки по бортам
    for yy in (my - 4, my + 8, my + 21):
        o.append(R(cx - 25.5 + (0 if yy > my - 6 else 1.5), yy, 6.5, 2.6, 0.6, 0.45, '#fff'))
        o.append(R(cx + 19.0 - (0 if yy > my - 6 else 1.5), yy, 6.5, 2.6, 0.6, 0.45, '#fff'))
    # бочки
    for dx in (-13, 13):
        o.append(C(cx + dx, b - 21, 3.3, 0.5, '#fff'))
        o.append(C(cx + dx, b - 21, 1.5, 0.25, GRAY))
    # штурвал
    wy = b - 9
    o.append(C(cx, wy, 5.6, 0.6, '#fff'))
    o.append(C(cx, wy, 1.4, 0.4, INK, INK))
    for k in range(8):
        a = math.radians(k * 45)
        o.append(L(cx + 1.4 * math.cos(a), wy + 1.4 * math.sin(a), cx + 7.2 * math.cos(a), wy + 7.2 * math.sin(a), 0.4))
    o.append(T(cx, y0 + PH - OUT_PAD + 0.6, 'Конец раунда: Ром 0 → Ропот +1', 6, 'middle', 'bold'))
    return '\n'.join(o)


# ------------------------------------------------------------------ карта
def map_spread(x0, y0, cols=7, rows=6, w=15.4):
    o = []
    h = 2 * w / math.sqrt(3)
    Rr = h / 2
    gx = x0 + OUT_PAD + 3.5
    gy = y0 + OUT_PAD + 8.0
    o.append(T(x0 + OUT_PAD, y0 + 10.0, 'КАРТА', 14, weight='bold', family=SERIF, ls=0.6))
    o.append(T(x0 + OUT_PAD + 34, y0 + 9.6, 'Ход — линия из клетки в клетку. Значки — карандашом.', 5.6, fill=GRAY))
    tx = x0 + PW * 2 - OUT_PAD
    side = ['<g transform="translate(%.2f %.2f) rotate(90)">' % (tx, y0 + OUT_PAD + 1)]
    side.append(T(0, 16.0, 'Значок клетки (бросок d6):', 6, weight='bold'))
    segs = [('1', 'wave', 'штиль'), ('2', 'zig', 'особый штиль'), ('3', 'bolt', 'шторм'),
            ('4', None, 'корабль'), ('5', None, 'туман'), ('6', None, 'остров')]
    txt = {'4': '⚓', '5': '☁', '6': '△'}
    for i, (d, kind, nm) in enumerate(segs):
        u = (i % 3) * 31.0
        ly = 11.6 if i < 3 else 8.0
        side.append(T(u, ly, d, 5.6, fill=GRAY))
        if kind:
            side.append(ico(kind, u + 6.2, ly - 1.1, 0.55, 0.5))
        else:
            side.append(T(u + 4.6, ly + 0.4, txt[d], 7.5, family=SYM))
        side.append(T(u + 9.6, ly, nm, 5.6))
    side.append(T(0, 4.6, 'Разведка: d6 → значок карандашом.', 5.5, fill=GRAY))
    side.append(T(0, 1.4, 'Значок клетки задаёт пул эпизодов.', 5.5, fill=GRAY))
    side.append('</g>')
    o.append(''.join(side))
    for r in range(1, rows + 1):
        for c in range(cols):
            cx = gx + w / 2 + c * w + (w / 2 if r % 2 == 0 else 0)
            cy = gy + Rr + (r - 1) * 0.75 * h
            pts = ' '.join('%.2f,%.2f' % (cx + Rr * math.cos(math.radians(a)), cy + Rr * math.sin(math.radians(a)))
                           for a in (-90, -30, 30, 90, 150, 210))
            o.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="0.35"/>' % (pts, INK))
            o.append(T(cx, cy + Rr * 0.74, '%s%d' % ('ABCDEFG'[c], r), 4.6, 'middle', fill=GRAY))
    for c in range(cols):
        o.append(T(gx + w / 2 + c * w, gy - 0.8, 'ABCDEFG'[c], 6.5, 'middle', 'bold'))
    for r in range(1, rows + 1):
        o.append(T(gx - 1.9, gy + Rr + (r - 1) * 0.75 * h + 1.0, str(r), 6.5, 'middle', 'bold'))
    return '\n'.join(o)


# ------------------------------------------------------------------ порт
def port_spread(x0, y0):
    o = []
    spine = x0 + PW
    # ---- левая страница: 4 слота в 2 колонки (1,3 | 2,4)
    o.append(T(x0 + OUT_PAD, y0 + 11.4, 'ПОРТ', 17, weight='bold', family=SERIF, ls=0.6))
    o.append(T(x0 + OUT_PAD, y0 + 15.2, 'В порту Ром не убывает: тут пьют за свои', 6, fill=GRAY))
    cw = (PW - OUT_PAD - IN_PAD - 1.2) / 2
    sh = 17.6
    top = y0 + 18.4
    pos = {1: (0, 0), 3: (0, 1), 2: (1, 0), 4: (1, 1)}
    for n, (c, r) in pos.items():
        x = x0 + OUT_PAD + c * (cw + 1.2)
        y = top + r * (sh + 1.2)
        if n <= 3:
            o.append(C(x + cw / 2, y + sh / 2, 8.3, 0.55))
            o.append(badge(x + 4.4, y + 4.6, n, 3.3, 10))
        else:
            o.append(R(x, y, cw, sh, 1.8, 0.4, dash='1.8 1.3'))
            o.append(badge(x + 4.4, y + 4.6, n, 3.3, 10))
    # ---- правая страница: магазин (5 столбцов в 2 блока) + колонка «Шуллерские штучки» игорного дома
    rx = spine + IN_PAD
    rw = PW - OUT_PAD - IN_PAD
    y = y0 + OUT_PAD
    o.append(T(rx, y + 5.0, 'МАГАЗИН', 9, weight='bold', family=SERIF, ls=0.4))
    zx = rx + 38
    o.append(R(zx, y + 0.4, rw - 38, 8.8, 1.6, 0.4, dash='1.8 1.3'))
    o.append(badge(zx + 4.4, y + 4.8, 5, 3.3, 10))
    colx = [rx, rx + 27.0, rx + 27.0 + 19.6]
    colws = [25.0, 19.6, 19.65]
    o.append(T(colx[1] + 19.6, y + 12.4, 'Кинь d6 на каждый столбец,', 5.2, 'middle', fill=GRAY))
    o.append(T(colx[1] + 19.6, y + 15.2, 'чтобы узнать, что в наличии', 5.2, 'middle', fill=GRAY))

    def shop_col(cx, cwid, ty, ci, head):
        o.append(R(cx, ty, cwid, 4.6, 0.3, 0.3, '#ddd'))
        ik = {'СНАРЯЖЕНИЕ': 'gear', 'ДИКОВИНКИ': 'curio', 'БОЙ': 'battle'}.get(head)
        if ik:
            o.append(svg_image(ik, cx + 2.5, ty + 2.35, 3.9))
            o.append(T(cx + 4.8, ty + 3.4, head, 4.9, 'start', 'bold'))
        else:
            o.append(T(cx + cwid / 2, ty + 3.4, head, 5.0, 'middle', 'bold'))
        for ri, (nm, pr, ef) in enumerate(SHOP[ci][1]):
            yy = ty + 4.6 + ri * 4.6
            o.append(R(cx, yy, cwid, 4.6, 0.2, 0.2, stroke=GRAY))
            o.append(T(cx + 0.9, yy + 3.3, str(ri + 1), 5.2, weight='bold'))
            o.append(T(cx + 3.6, yy + 3.3, nm, 4.0 if len(nm) > 14 else (4.3 if len(nm) > 11 else 5.0)))
            o.append(coin(cx + cwid - 2.2, yy + 2.3, pr))

    ty1 = y + 17.0
    for ci in range(3):
        shop_col(colx[ci], colws[ci], ty1, ci, SHOP[ci][0])
    # блок 2: слева «Шуллерские штучки» (игорный дом), справа от чёрной границы — БОЙ и УСЛУГИ
    ty2 = ty1 + 4.6 + 6 * 4.6 + 4.6
    gw = 26.0
    vx = rx + gw + 1.5
    # чёрная граница: от слотов через разворот, затем вниз
    sy_line = y0 + 55.5
    o.append('<polyline points="%.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="none" stroke="%s" stroke-width="0.9"/>' % (
        x0 + OUT_PAD, sy_line, vx, sy_line, vx, y0 + PH - OUT_PAD, INK))
    w2 = (rx + rw - vx - 1.5) / 2
    o.append(T(vx + 1.5, ty2 - 1.4, 'Бой, Услуги: тоже d6', 5.0, fill=GRAY))
    shop_col(vx + 1.5, w2, ty2, 3, SHOP[3][0])
    shop_col(vx + 1.5 + w2, w2, ty2, 4, SHOP[4][0])
    gx = rx
    o.append(R(gx, ty2, gw, 4.6, 0.3, 0.3, '#ddd'))
    o.append(svg_image('shuller', gx + 2.5, ty2 + 2.35, 3.9))
    o.append(T(gx + 4.8, ty2 + 3.4, 'ШУЛЛЕРСКИЕ ШТУЧКИ', 4.9, 'start', 'bold'))
    yy = ty2 + 4.6
    for i in range(7):
        rh = 5.4 if i < len(UPG) else 4.4
        o.append(R(gx, yy, gw, rh, 0.2, 0.2, stroke=GRAY))
        o.append(R(gx + 0.7, yy + 0.8, 2.8, 2.8, 0.4, 0.3))
        if i < len(UPG):
            nm, ef, pr = UPG[i]
            o.append(T(gx + 4.4, yy + 2.5, nm, 5.0, weight='bold'))
            o.append(coin(gx + gw - 2.2, yy + 2.1, pr))
            o.append(T(gx + 4.4, yy + 5.0, ef, 5.0, fill=GRAY))
        else:
            o.append(T(gx + 4.4, yy + 3.2, 'из событий', 5.0, fill=GRAY))
        yy += rh

    # ---- левая страница, низ: игорный дом (ячейка 6) и ставки
    sy = y0 + 55.5
    lx = x0 + OUT_PAD
    lw = PW - OUT_PAD - IN_PAD
    o.append(T(lx, sy + 6.0, 'ИГОРНЫЙ ДОМ', 8.5, weight='bold', family=SERIF, ls=0.3))
    o.append(T(lx, sy + 9.6, 'Каждый участник делает', 5.2, fill=GRAY))
    o.append(T(lx, sy + 12.2, 'одну ставку за посещение:', 5.2, fill=GRAY))
    o.append(T(lx, sy + 14.8, 'до 2 Сокровищ.', 5.2, fill=GRAY))
    zx = lx + 33.5
    zw = lw - 33.5
    o.append(R(zx, sy + 1.2, zw, 14.4, 1.6, 0.4, dash='1.8 1.3'))
    o.append(badge(zx + 4.4, sy + 5.2, 6, 3.3, 10))
    tx = zx + 9.0
    for k, ln in enumerate(['2d6: 6, 7, 8 — проигрыш.', 'Иначе: выплата ×2.', 'Забрать или бросить ещё.', 'Каждый успех: ×3, ×4…', 'Проигрыш: выплата 0.']):
        o.append(T(tx if k > 0 or True else zx, sy + 4.4 + k * 2.45 if k < 3 else sy + 4.4 + k * 2.45 + 0.3, ln, 5.0, fill=GRAY))
    ry0 = sy + 17.0
    rh = 5.2
    for i, (ratio, name, short, full) in enumerate(BETS):
        yy = ry0 + i * rh
        o.append(R(lx, yy, lw, rh, 0.8, 0.3, dash='1.4 1.0'))
        o.append(T(lx + 1.2, yy + 3.7, '(№%d)' % (i + 1), 5.0, weight='bold'))
        o.append(T(lx + 8.6, yy + 3.9, ratio, 8.5, weight='bold', family=SERIF))
        o.append(T(lx + 19.6, yy + 3.7, name, 5.0, weight='bold'))
        o.append(T(lx + lw - 1.0, yy + 3.7, short, 5.0, 'end', fill=GRAY))
    return '\n'.join(o)


# ------------------------------------------------------------------ боевой планшет (горизонтально)
# ------------------------------------------------------------------ палуба (одна страница, слоты 1-8 на фоне корабля)
def deck_page(x0, y0):
    o = []
    left = x0 + OUT_PAD
    pw = PW - OUT_PAD - IN_PAD
    cx = left + pw / 2
    t, b = y0 + 15.0, y0 + PH - OUT_PAD
    # фон: корабль сверху (нос вверху), светло, чтобы не мешать слотам
    hull = ('M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f L%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f Z' % (
        cx, t, cx + 33, t + 14, cx + 35, b - 40, cx + 30, b, cx - 30, b, cx - 35, b - 40, cx - 33, t + 14, cx, t))
    o.append('<clipPath id="hullclip2"><path d="%s"/></clipPath>' % hull)
    o.append('<path d="%s" fill="#f4f4f4" stroke="#aaa" stroke-width="0.7"/>' % hull)
    planks = ''.join('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#ddd" stroke-width="0.3"/>' % (cx - 40, yy, cx + 40, yy)
                     for yy in [t + 4 + k * 4.2 for k in range(int((b - t) / 4.2))])
    o.append('<g clip-path="url(#hullclip2)">%s</g>' % planks)
    o.append(L(cx, t - 3, cx, t + 4, 0.7, '#aaa'))
    my = t + 38
    o.append(L(cx - 24, my, cx + 24, my, 0.8, '#bbb'))
    o.append(C(cx, my, 3.4, 0.7, '#fff', '#bbb'))
    o.append(C(cx + 14, my - 6, 2.4, 0.4, '#fff', '#bbb'))
    o.append(C(cx + 13.2, my - 6.3, 0.6, 0.2, '#bbb', '#bbb'))
    o.append(C(cx + 14.8, my - 6.3, 0.6, 0.2, '#bbb', '#bbb'))
    o.append(T(left, y0 + OUT_PAD + 7.5, 'ПАЛУБА', 17, weight='bold', family=SERIF, ls=0.8))
    # слоты: слева личные 1-3 (круг), справа общие 4-6 (пунктир под 2 кубика), сгруппированы выше
    top = y0 + 15.4
    sh = 17.2
    gap = 1.0
    cw = (pw - 1.2) / 2
    for i in range(3):
        y = top + i * (sh + gap)
        o.append(C(left + cw / 2 + 2.0, y + sh / 2, 8.1, 0.55))
        o.append(badge(left + 4.4, y + 4.6, i + 1, 3.3, 10))
        rx = left + cw + 1.2
        o.append(R(rx, y, cw, sh, 1.8, 0.4, dash='1.8 1.3'))
        o.append(badge(rx + 4.4, y + 4.6, i + 4, 3.3, 10))
    # слот 7: Рыбалка — пунктирная ячейка + таблица улова (как магазин): Штиль и регионы особого штиля
    fy = top + 3 * sh + 2 * gap + 1.0
    o.append(R(left, fy, pw, 9.6, 1.6, 0.4, dash='1.8 1.3'))
    o.append(badge(left + 4.4, fy + 4.8, 7, 3.3, 10))
    o.append(T(left + 10.0, fy + 6.2, 'РЫБАЛКА', 8, weight='bold', family=SERIF, ls=0.3))
    o.append(T(left + 31.0, fy + 4.0, 'Доступно во время штиля и ос. штиля', 5.0, fill=GRAY))
    o.append(T(left + 31.0, fy + 7.4, 'МЕЛЬ–МАНГРЫ: регионы ос. штиля', 5.0, fill=GRAY))
    ty = fy + 10.6
    lw = 6.0
    colw = (pw - lw) / 4
    rh = 4.6
    o.append(R(left, ty, pw, 4.4, 0.3, 0.3, '#ddd'))
    o.append(T(left + lw / 2, ty + 3.2, 'd6', 5.0, 'middle', 'bold'))
    for ci, (hd, full, items) in enumerate(CATCH):
        cx = left + lw + ci * colw
        o.append(T(cx + colw / 2, ty + 3.2, hd, 5.0, 'middle', 'bold'))
    for ri, lab in enumerate(['1–2', '3–4', '5–6']):
        yy = ty + 4.4 + ri * rh
        o.append(R(left, yy, lw, rh, 0.2, 0.2, stroke=GRAY))
        o.append(T(left + lw / 2, yy + 3.3, lab, 4.8, 'middle', 'bold'))
        for ci, (hd, full, items) in enumerate(CATCH):
            cx = left + lw + ci * colw
            o.append(R(cx, yy, colw, rh, 0.2, 0.2, stroke=GRAY))
            o.append(R(cx + 0.7, yy + 0.9, 2.8, 2.8, 0.4, 0.3))
            o.append(T(cx + 4.0, yy + 3.3, items[ri][0], 4.7))
            o.append(coin(cx + colw - 2.1, yy + rh / 2, items[ri][1]))
    return '\n'.join(o)


# ------------------------------------------------------------------ оборот: памятка и журнал рейсов
def back_panel(x0, y0):
    """Судовой журнал: «ключевые слова». Сверху цифры 1-6, слева значки (строки)."""
    o = []
    x = x0 + IN_PAD
    wd = PW - IN_PAD - OUT_PAD
    y = y0 + OUT_PAD
    o.append(T(x, y + 5.0, 'СУДОВОЙ ЖУРНАЛ', 9, weight='bold', family=SERIF, ls=0.3))
    o.append(T(x, y + 9.2, 'Событие даёт символ: закрасьте клетку', 5.2, fill=GRAY))
    o.append(T(x, y + 11.9, 'в строке этого значка. Другие события', 5.2, fill=GRAY))
    o.append(T(x, y + 14.6, 'проверяют, сколько клеток закрашено.', 5.2, fill=GRAY))
    top = y + 17.5
    ncols, nrows = 6, 8
    wl = 13.0
    cw = (wd - wl) / ncols
    hh, rh = 8.0, 8.5
    kinds = ['cross', 'helm', 'sun', 'moon', 'skull', 'parrot', 'goblin', 'mage']
    o.append(R(x, top, wd, hh + nrows * rh, 1.0, 0.5))
    o.append(R(x, top, wd, hh, 1.0, 0.5, '#e8e8e8'))
    for i in range(ncols):
        o.append(T(x + wl + i * cw + cw / 2, top + 5.8, str(i + 1), 9, 'middle', 'bold', family=SERIF))
    for r, kd in enumerate(kinds):
        yy = top + hh + r * rh
        o.append(L(x, yy, x + wd, yy, 0.25, GRAY))
        o.append(ico(kd, x + wl / 2, yy + rh / 2, 1.0, 0.5))
    for i in range(ncols + 1):
        xx = x + wl + i * cw
        o.append(L(xx, top, xx, top + hh + nrows * rh, 0.5 if i == 0 else 0.3, INK if i == 0 else GRAY))
    return '\n'.join(o)
