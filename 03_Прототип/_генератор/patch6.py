# -*- coding: utf-8 -*-
p = 'parts_new.py'
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    if a not in s:
        print('НЕТ:', a[:70])
    s = s.replace(a, b)

# --- цифры слотов: белая цифра в чёрном кружке
rep("            o.append(T(x + cw / 2, y + sh / 2 + 2.2, str(n), 13, 'middle', 'bold', INK, SERIF))",
    "            o.append(badge(x + 4.4, y + 4.6, n, 3.3, 10))")
rep("            o.append(T(x + 2.4, y + 5.6, str(n), 13, weight='bold', family=SERIF))",
    "            o.append(badge(x + 4.4, y + 4.6, n, 3.3, 10))")
rep("    o.append(T(zx + 2.4, y + 6.2, '5', 12, weight='bold', family=SERIF))",
    "    o.append(badge(zx + 4.4, y + 4.8, 5, 3.3, 10))")
rep("    o.append(T(zx + 2.4, sy + 8.4, '6', 12, weight='bold', family=SERIF))\n    o.append(T(zx + 8.6, sy + 8.4, '2d6', 6, weight='bold'))",
    "    o.append(badge(zx + 4.4, sy + 5.4, 6, 3.3, 10))\n    o.append(T(zx + 9.6, sy + 6.6, '2d6', 6, weight='bold'))")
rep("        o.append(T(x + 2.0, y + 5.6, str(i + 1), 9, weight='bold', family=SERIF))\n        o.append(T(x + 6.6, y + 5.4, nm, 7.0, weight='bold', family=SERIF))",
    "        o.append(badge(x + 3.8, y + 4.4, i + 1, 2.9, 8.5))\n        o.append(T(x + 8.4, y + 5.4, nm, 7.0, weight='bold', family=SERIF))")
rep("        o.append(T(left + cw / 2, y + sh / 2 + 2.2, str(i + 1), 13, 'middle', 'bold', INK, SERIF))",
    "        o.append(badge(left + 4.4, y + 4.6, i + 1, 3.3, 10))")
rep("        o.append(T(rx + 2.4, y + 5.6, str(i + 5), 13, weight='bold', family=SERIF))",
    "        o.append(badge(rx + 4.4, y + 4.6, i + 5, 3.3, 10))")

# --- оборот: судовой журнал (ключевые слова)
a = s.index("def back_panel")
s = s[:a] + '''def back_panel(x0, y0):
    """Судовой журнал: таблица «ключевых слов». Слева номера строк, сверху значки-столбцы."""
    o = []
    x = x0 + IN_PAD
    wd = PW - IN_PAD - OUT_PAD
    y = y0 + OUT_PAD
    o.append(T(x, y + 5.0, 'СУДОВОЙ ЖУРНАЛ', 9, weight='bold', family=SERIF, ls=0.3))
    o.append(T(x, y + 9.2, 'Событие даёт символ: закрасьте клетку', 5.2, fill=GRAY))
    o.append(T(x, y + 11.9, 'в его столбце. Другие события проверяют', 5.2, fill=GRAY))
    o.append(T(x, y + 14.6, 'сколько клеток закрашено.', 5.2, fill=GRAY))
    top = y + 17.5
    ncols, nrows = 6, 8
    w0 = 8.0
    cw = (wd - w0) / ncols
    hh, rh = 10.0, 8.3
    icons = ['☠', '⚓', '☾', '♥', '⚑', '✦']
    o.append(R(x, top, wd, hh + nrows * rh, 1.0, 0.5))
    o.append(R(x, top, wd, hh, 1.0, 0.5, '#e8e8e8'))
    for i, ic in enumerate(icons):
        cx = x + w0 + i * cw
        o.append(T(cx + cw / 2, top + 7.2, ic, 12, 'middle', family=SYM))
    for r in range(1, nrows + 1):
        yy = top + hh + (r - 1) * rh
        o.append(L(x, yy, x + wd, yy, 0.25, GRAY))
        o.append(T(x + w0 / 2, yy + 5.6, str(r), 8, 'middle', 'bold', family=SERIF))
    for i in range(ncols + 1):
        o.append(L(x + w0 + (i - 1) * cw if i else x + w0, top, x + w0 + (i - 1) * cw if i else x + w0, top + hh + nrows * rh, 0.3 if i else 0.5, GRAY if i else INK))
    return '\\n'.join(o)
'''
open(p, 'w', encoding='utf-8').write(s)

# --- буклет персонажей: памятка на последней странице
p = 'build_chars.py'
s = open(p, encoding='utf-8').read()
a = s.index("def back(x0, y0):")
b = s.index("def build():")
s = s[:a] + '''def back(x0, y0):
    """Памятка игры (страница 8 буклета персонажей)."""
    o = []
    x = x0 + IN_PAD
    y = y0 + OUT_PAD + 4.0
    o.append(T(x, y, 'ПАМЯТКА', 9, weight='bold', family=SERIF, ls=0.4))
    items = [('РАУНД', 'Эпизод → Выбор (по Славе) → Действия 1–8 → Конец'),
             ('ПРОВЕРКА', 'd6 + навык + бонусы: ≤3 · 4–6 · 7–9 · 10+'),
             ('УДАЧА', '−1 Удачи = перебросить свой кубик'),
             ('КОНЕЦ РАУНДА', 'Ром −1 · пороги Опасности 3 и 5 · края шкал'),
             ('ХОД И РАЗВЕДКА', 'Ход — на соседнюю клетку; разведка — d6 → значок'),
             ('МАГАЗИН', 'd6 на каждый столбец, кроме «Всегда в наличии»'),
             ('ИГОРНЫЙ ДОМ', 'ставка — Добыча; 7/11 победа, 2/3/12 проигрыш'),
             ('БОЙ', 'бросок, 2 переброса, кубики на станции Борта'),
             ('ПОРАЖЕНИЕ', 'Корпус/Команда 0 · Ром, Дух 0 или 10 · Опасность 6')]
    y += 3.0
    for k, v in items:
        o.append(T(x, y + 2.0, k, 5.4, weight='bold'))
        o.append(T(x, y + 5.2, v, 5.4))
        y += 8.6
    return '\\n'.join(o)


''' + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
