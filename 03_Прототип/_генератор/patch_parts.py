# -*- coding: utf-8 -*-
import re
p = 'parts_new.py'
s = open(p, encoding='utf-8').read()

# ---------- правая страница порта
a = s.index("    # ---- правая страница")
b = s.index("def battle_panel")
right = '''    # ---- правая страница: игорный дом (ячейка 5) и магазин (ячейка 6)
    rx = spine + IN_PAD
    rw = PW - OUT_PAD - IN_PAD
    y = y0 + OUT_PAD

    def zone(sy, num, label):
        zx = rx + 33
        o.append(R(zx, sy + 1.2, rw - 33, 11.5, 1.4, 0.35, dash='1.6 1.2'))
        o.append(C(zx + 3.0, sy + 4.2, 2.3, fill=INK, stroke=INK))
        o.append(T(zx + 3.0, sy + 5.3, str(num), 5.6, 'middle', 'bold', '#fff', SERIF))
        o.append(T(zx + 8, sy + 5.0, label, 4.0, weight='bold'))

    o.append(T(rx, y + 5.0, 'ИГОРНЫЙ ДОМ', 9, weight='bold', family=SERIF, ls=0.4))
    for k, line in enumerate(['Ставки выбирают сами игроки,', 'которые пошли в игорный дом.', 'Ставка 1 Добыча на исход.', 'Бросок 2d6: свой кубик + запасной.']):
        o.append(T(rx, y + 8.2 + k * 1.9, line, 3.5, fill=GRAY))
    zone(y, 5, 'пойти в игорный дом')
    ty = y + 16.5
    rh = 7.6
    for i, (n, ratio, name, cond) in enumerate(BETS):
        yy = ty + i * rh
        o.append(R(rx, yy, rw, rh, 0.6, 0.3))
        o.append(T(rx + 1.4, yy + 5.2, ratio, 9, weight='bold', family=SERIF))
        o.append(T(rx + 13.5, yy + 2.9, name, 4.4, weight='bold'))
        for k, line in enumerate(wrap(cond, 80)[:2]):
            o.append(T(rx + 13.5, yy + 5.1 + k * 1.8, line, 3.2, fill=GRAY))
    sy = ty + 5 * rh + 1.2
    o.append(L(rx, sy - 0.4, rx + rw, sy - 0.4, 0.5))
    o.append(T(rx, sy + 5.0, 'МАГАЗИН', 9, weight='bold', family=SERIF, ls=0.4))
    for k, line in enumerate(['Бросьте свой кубик 3 раза.', 'Числа — товары в наличии:', 'бросок 1 → колонка 1 и т.д.', 'Цена — в Добыче (Д).']):
        o.append(T(rx, sy + 7.8 + k * 1.9, line, 3.5, fill=GRAY))
    zone(sy, 6, 'зайти в магазин')
    ty = sy + 14.6
    colw = rw / 3
    for ci, (cname, items) in enumerate(SHOP):
        cx = rx + ci * colw
        o.append(R(cx, ty, colw, 3.6, 0.3, 0.3, '#ddd'))
        o.append(T(cx + colw / 2, ty + 2.7, cname, 3.8, 'middle', 'bold'))
        for ri, (nm, pr) in enumerate(items):
            yy = ty + 3.6 + ri * 3.5
            o.append(R(cx, yy, colw, 3.5, 0.2, 0.2, stroke=GRAY))
            o.append(T(cx + 1.0, yy + 2.5, str(ri + 1), 3.8, weight='bold'))
            o.append(T(cx + 3.4, yy + 2.5, nm, 3.5))
            o.append(T(cx + colw - 0.9, yy + 2.5, '%dД' % pr, 3.6, 'end', 'bold'))
    return '\\n'.join(o)


'''
s = s[:a] + right + s[b:]

# ---------- боевой планшет, горизонтально
a = s.index("def battle_panel")
battle = '''def battle_panel(x0, y0):
    """Планшет повёрнут на 90° (читается, если книгу повернуть против часовой). Локально: 95 x 66 мм."""
    W, H = PH - 2 * OUT_PAD, PW - IN_PAD - OUT_PAD
    o = []
    o.append(T(0, 5.2, 'БОЕВОЙ ПЛАНШЕТ', 9, weight='bold', family=SERIF, ls=0.4))
    o.append(T(38, 4.8, 'Корабль игроков. Враг, его Корпус, уклонение и урон — в приложении.', 3.6, fill=GRAY))
    stations = [
        ('ПУШКИ', 'Глазомер', 'Пара и больше одинаковых', '2→1 · 3→3 · 4→5 · 5→8 урона'),
        ('ТАРАН', 'Костяк', 'Стрит от 3 подряд', '3→2 · 4→4 · 5→6 урона'),
        ('РУЛЬ', 'Курс', 'Сумма ≥ уклонения врага', '→ залп врага мимо'),
        ('ТРЮМ', 'Хватка', 'Каждый кубик 1–2', '→ Корпус +1 за кубик'),
    ]
    sw, sh, g = (W - 0.8) / 2, 18.0, 0.8
    gy = 7.0
    for i, (nm, sk, req, eff) in enumerate(stations):
        c, r = i % 2, i // 2
        x, y = c * (sw + g), gy + r * (sh + g)
        o.append(R(x, y, sw, sh, 1.4, 0.35))
        o.append(C(x + 3.3, y + 3.3, 2.4, fill=INK, stroke=INK))
        o.append(T(x + 3.3, y + 4.3, str(i + 1), 6.5, 'middle', 'bold', '#fff', SERIF))
        o.append(T(x + 7.0, y + 4.2, nm, 6, weight='bold', family=SERIF))
        o.append(T(x + 7.0, y + 6.6, sk, 3.6, fill=GRAY))
        for k, line in enumerate(wrap(req, 22)[:2]):
            o.append(T(x + 1.4, y + 9.6 + k * 1.8, line, 3.3))
        for k, line in enumerate(wrap(eff, 24)[:2]):
            o.append(T(x + 1.4, y + 13.6 + k * 1.8, line, 3.2, fill=GRAY))
        o.append(R(x + sw - 32.6, y + 0.9, 31.8, sh - 1.8, 1.4, 0.35, dash='1.6 1.2'))
    ry = gy + 2 * sh + g + 1.0
    o.append(R(0, ry, W, 16.4, 1.4, 0.35, dash='1.6 1.2'))
    o.append(T(1.6, ry + 3.4, 'ПАЛУБА БОЯ', 4.6, weight='bold'))
    o.append(T(1.6, ry + 6.0, 'бросок: все кубики сюда', 3.5, fill=GRAY))
    o.append(T(W - 1.6, ry + 3.4, 'свой кубик: до 2 перебросов (+1 за Удачу)', 3.5, 'end', fill=GRAY))
    o.append(T(0, ry + 19.4, 'Навык станции ≥3 у владельца кубика: +1 к эффекту. Кубик в успехе: Слава +1 владельцу.', 3.3, fill=GRAY))
    gx0 = x0 + IN_PAD
    gy1 = y0 + PH - OUT_PAD
    return '<g transform="translate(%.2f %.2f) rotate(-90)">%s</g>' % (gx0, gy1, '\\n'.join(o))
'''
s = s[:a] + battle
open(p, 'w', encoding='utf-8').write(s)
print('patched')
