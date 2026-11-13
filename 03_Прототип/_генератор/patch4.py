# -*- coding: utf-8 -*-
p = 'parts_new.py'
s = open(p, encoding='utf-8').read()

# ---------- 1. слоты порта 1-4: без сплошной рамки, номер внутри
a = s.index("    for n, (c, r) in pos.items():")
b = s.index("    # ---- правая страница, верх: магазин")
s = s[:a] + """    for n, (c, r) in pos.items():
        x = x0 + OUT_PAD + c * (cw + 1.2)
        y = top + r * (sh + 1.2)
        if n <= 3:
            o.append(C(x + cw / 2, y + sh / 2, 8.3, 0.55))
            o.append(T(x + cw / 2, y + sh / 2 + 2.2, str(n), 13, 'middle', 'bold', '#999', SERIF))
        else:
            o.append(R(x, y, cw, sh, 1.8, 0.4, dash='1.8 1.3'))
            o.append(T(x + 2.4, y + 5.6, str(n), 13, weight='bold', family=SERIF))
""" + s[b:]

# ---------- 2. номера зон магазина и казино: просто цифра внутри рамки
s = s.replace("    o.append(badge(zx + 4.2, y + 4.8, 5, 3.0, 10))",
              "    o.append(T(zx + 2.4, y + 6.2, '5', 12, weight='bold', family=SERIF))")
s = s.replace("    o.append(badge(zx + 4.2, sy + 6.9, 6, 3.2, 10))\n    o.append(T(zx + 9.0, sy + 8.3, '2d6', 6, weight='bold'))",
              "    o.append(T(zx + 2.4, sy + 8.0, '6', 12, weight='bold', family=SERIF))\n    o.append(T(zx + 9.0, sy + 8.0, '2d6', 6, weight='bold'))")

# ---------- 3. «Борт»
s = s.replace("'БОЕВОЙ ПЛАНШЕТ', 8.5,", "'БОРТ', 11,")
s = s.replace("o.append(T(43, 2.8, 'Пушки", "o.append(T(30, 2.8, 'Пушки").replace("o.append(T(43, 5.4, 'Таран", "o.append(T(30, 5.4, 'Таран")
s = s.replace("        o.append(badge(x + 4.0, y + 4.6, i + 1, 3.0, 8.5))\n        o.append(T(x + 8.6, y + 5.4, nm, 7.0, weight='bold', family=SERIF))",
              "        o.append(T(x + 2.0, y + 5.6, str(i + 1), 9, weight='bold', family=SERIF))\n        o.append(T(x + 6.6, y + 5.4, nm, 7.0, weight='bold', family=SERIF))")

# ---------- 4. новая страница «Палуба» и оборот
s += '''

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
    wy = b - 8
    o.append(C(cx, wy, 5.6, 0.6, '#fff', '#bbb'))
    o.append(C(cx, wy, 1.4, 0.4, '#bbb', '#bbb'))
    for k in range(8):
        a = math.radians(k * 45)
        o.append(L(cx + 1.4 * math.cos(a), wy + 1.4 * math.sin(a), cx + 7.2 * math.cos(a), wy + 7.2 * math.sin(a), 0.4, '#bbb'))
    o.append(T(left, y0 + OUT_PAD + 7.5, 'ПАЛУБА', 17, weight='bold', family=SERIF, ls=0.8))
    # слоты: слева личные 1-4 (круг), справа общие 5-8 (пунктир под 2 кубика)
    top = y0 + 19.0
    sh = 19.6
    gap = (b - top - 4 * sh) / 3
    cw = (pw - 1.2) / 2
    for i in range(4):
        y = top + i * (sh + gap)
        o.append(C(left + cw / 2, y + sh / 2, 8.3, 0.55, '#fff'))
        o.append(T(left + cw / 2, y + sh / 2 + 2.2, str(i + 1), 13, 'middle', 'bold', '#999', SERIF))
        rx = left + cw + 1.2
        o.append(R(rx, y, cw, sh, 1.8, 0.4, '#fff', dash='1.8 1.3'))
        o.append(T(rx + 2.4, y + 5.6, str(i + 5), 13, weight='bold', family=SERIF))
    return '\\n'.join(o)


# ------------------------------------------------------------------ оборот: памятка и журнал рейсов
def back_panel(x0, y0):
    o = []
    x = x0 + IN_PAD
    wd = PW - IN_PAD - OUT_PAD
    y = y0 + OUT_PAD + 3.8
    o.append(T(x, y, 'ПАМЯТКА', 8.5, weight='bold', family=SERIF, ls=0.4))
    items = [('РАУНД', 'Эпизод → Выбор → Действия 1–8 → Конец'),
             ('ПРОВЕРКА', 'd6 + навык + бонусы: ≤3 · 4–6 · 7–9 · 10+'),
             ('КОНЕЦ РАУНДА', 'Ром −1 · пороги Опасности 3 и 5'),
             ('ПОРАЖЕНИЕ', 'Корпус/Команда 0 · Ром, Дух 0 или 10 · Опасность 6')]
    y += 3.6
    for k, v in items:
        o.append(T(x, y + 2.0, k, 5.4, weight='bold'))
        o.append(T(x, y + 5.2, v, 5.4))
        y += 7.2
    y += 1.0
    o.append(L(x, y, x + wd, y, 0.5))
    y += 5.6
    o.append(T(x, y, 'ЖУРНАЛ РЕЙСОВ', 8.5, weight='bold', family=SERIF, ls=0.4))
    y += 2.4
    xs = [x, x + 6, x + 28, x + 38]
    rowh = 6.0
    nrows = int((y0 + PH - OUT_PAD - y - rowh) / rowh)
    o.append(R(x, y, wd, rowh * (nrows + 1), 0.8, 0.35))
    for i, hh in enumerate(['№', 'Корабль', 'Итог', 'Слово / артефакт']):
        o.append(T(xs[i] + 1, y + 4.2, hh, 5.0, weight='bold'))
    for i in range(1, nrows + 1):
        o.append(L(x, y + rowh * i, x + wd, y + rowh * i, 0.2, GRAY))
        o.append(T(xs[0] + 1, y + rowh * (i + 1) - 1.8, str(i), 5.0, fill=GRAY))
    for xx in xs[1:]:
        o.append(L(xx, y, xx, y + rowh * (nrows + 1), 0.2, GRAY))
    return '\\n'.join(o)
'''
open(p, 'w', encoding='utf-8').write(s)

p = 'build_zine.py'
s = open(p, encoding='utf-8').read()
s = s.replace("from parts_new import map_spread, port_spread, battle_panel, deck_spread", "from parts_new import map_spread, port_spread, battle_panel, deck_page, back_panel as back_panel2")
s = s.replace("top.append(deck_spread(0, 0))", "top.append(deck_page(0, 0))\n    top.append(battle_panel(PW, 0))")
s = s.replace("bottom.append(battle_panel(PW * 2, 0))", "bottom.append(back_panel2(PW * 2, 0))")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
