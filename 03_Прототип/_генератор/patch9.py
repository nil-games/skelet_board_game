# -*- coding: utf-8 -*-
import re
# ---------------------------------------------------------------- content.py
p = 'content.py'
s = open(p, encoding='utf-8').read()
# fx: улов
s = s.replace("        if k == 'mv':\n            out.append('Ход %d' % v)",
              "        if k == 'catch':\n            out.append('Улов: столбец %d (d6)' % v)\n        elif k == 'mv':\n            out.append('Ход %d' % v)")
a = s.index("FISH = act(")
b = s.index("for _e in EVENTS:\n    if _e['hint'] in ('s', 'sp'):")
s = s[:a] + """FISH = act('Порыбачить', 'grab', [{'catch': 1}, {'catch': 2}, {'catch': 3}, {'catch': 4}],
           note='Слот 7 доступен только в штиле и особом штиле. Итог проверки выбирает столбец таблицы улова, d6 — строку. В особом штиле улов определяет сценарий.')
""" + s[b:]
a = s.index("ROUTINE['cells'][7] = act(")
b = s.index("\n", s.index("note='Слот 7 доступен только в штиле и особом штиле.')", a))
s = s[:a] + """ROUTINE['cells'][7] = act('Порыбачить (только если клетка — штиль или особый штиль)', 'grab',
                          [{'catch': 1}, {'catch': 2}, {'catch': 3}, {'catch': 4}],
                          note='Слот 7 доступен только в штиле и особом штиле.')

# Таблица улова (слот 7 «Рыбалка»). Столбец — итог проверки Хватки, строка — d6 (1–2 / 3–4 / 5–6).
# Улов остаётся на корабле (✓ в буклете), пока его не используют: тогда ✗ и эффект.
CATCH = [
    ('≤3', [('Сапог', 'Дух +1 (смешно)'), ('Водоросль', 'Ром +1 (бродит)'), ('Консерва', 'Добыча +1')]),
    ('4–6', [('Окунь', 'Ром +2'), ('Камбала', 'Ром +2'), ('Кальмар', 'Корпус +1 (чернила — клей)')]),
    ('7–9', [('Тунец', 'Ром +3'), ('Осьминог', 'Команда +1 (записался)'), ('Меч-рыба', 'Станция Таран +1 урона в ближайшем бою')]),
    ('10+', [('Золотрыбка', 'Удача +2 (желание)'), ('Русалка', 'Слава +3'), ('Кракенёнок', 'Опасность −2 (подружились)')]),
]""" + s[b:]
open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- sim.py
p = 'sim.py'
s = open(p, encoding='utf-8').read()
s = s.replace("    for k, v in eff.items():\n        if k in ('mv', 'sc', 'F', 'L', 'T', 'S'):",
              "    for k, v in eff.items():\n        if k == 'catch':\n            s += 0.7\n            continue\n        if k in ('mv', 'sc', 'F', 'L', 'T', 'S'):")
open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- build_book.py
p = 'build_book.py'
s = open(p, encoding='utf-8').read()
if 'Таблица улова' not in s:
    i = s.index("    h.append('<h2>Морской бой")
    s = s[:i] + """    h.append('<h2>Рыбалка (слот 7 на Палубе)</h2><p>Слот 7 открыт только во время штиля и особого штиля. Игрок проводит проверку Хватки: итог выбирает <b>столбец</b> таблицы улова, d6 — <b>строку</b> (1–2, 3–4, 5–6). Отметьте улов ✓ в буклете: он на корабле. Использовать можно в любой момент: зачеркните ✗ и получите эффект. В особом штиле сценарий может заменить таблицу.</p><table><tr><th>Итог</th><th>d6 1–2</th><th>d6 3–4</th><th>d6 5–6</th></tr>')
    for tier, items in CATCH:
        h.append('<tr><td><b>%s</b></td>%s</tr>' % (tier, ''.join('<td>%s<br><small>%s</small></td>' % (nm, ef) for nm, ef in items)))
    h.append('</table>')
""" + s[i:]
open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- parts_new.py
p = 'parts_new.py'
s = open(p, encoding='utf-8').read()
s = s.replace("from content import BETS, SHOP", "from content import BETS, SHOP, CATCH")
# монета
s = s.replace("def wrap(s, n):", '''def coin(x, y, n):
    """Монета с ценой внутри."""
    return C(x, y, 2.0, 0.35) + T(x, y + 0.62, str(n), 4.6, 'middle', 'bold')


def wrap(s, n):''', 1)
s = s.replace("            o.append(T(cx + cwid - 0.8, yy + 3.3, '%dД' % pr, 5.0, 'end', 'bold'))",
              "            o.append(coin(cx + cwid - 2.6, yy + 2.3, pr))")
s = s.replace("            o.append(T(gx + gw - 0.8, yy + 2.5, '%dД' % pr, 5.0, 'end', 'bold'))",
              "            o.append(coin(gx + gw - 2.6, yy + 2.1, pr))")
# палуба: рыбалка по образцу магазина
a = s.index("    # слоты: слева личные 1-3")
b = s.index("    return '\\n'.join(o)", a)
new = '''    # слоты: слева личные 1-3 (круг), справа общие 4-6 (пунктир под 2 кубика)
    top = y0 + 17.6
    sh = 16.9
    gap = 1.2
    cw = (pw - 1.2) / 2
    for i in range(3):
        y = top + i * (sh + gap)
        o.append(C(left + cw / 2 + 2.0, y + sh / 2, 8.3, 0.55))
        o.append(badge(left + 4.4, y + 4.6, i + 1, 3.3, 10))
        rx = left + cw + 1.2
        o.append(R(rx, y, cw, sh, 1.8, 0.4, dash='1.8 1.3'))
        o.append(badge(rx + 4.4, y + 4.6, i + 4, 3.3, 10))
    # слот 7: Рыбалка — пунктирная ячейка (номер, название, условие) + таблица улова
    fy = top + 3 * sh + 2 * gap + 1.4
    o.append(R(left, fy, pw, 10.6, 1.6, 0.4, dash='1.8 1.3'))
    o.append(badge(left + 4.4, fy + 5.3, 7, 3.3, 10))
    o.append(T(left + 10.0, fy + 6.6, 'РЫБАЛКА', 8, weight='bold', family=SERIF, ls=0.3))
    o.append(T(left + 36.0, fy + 4.6, 'Доступно во время штиля', 5.2, fill=GRAY))
    o.append(T(left + 36.0, fy + 7.8, 'и ос. штиля', 5.2, fill=GRAY))
    ty = fy + 11.6
    lw = 6.0
    colw = (pw - lw) / 4
    rh = 4.6
    o.append(R(left, ty, pw, 4.6, 0.3, 0.3, '#ddd'))
    o.append(T(left + lw / 2, ty + 3.3, 'd6', 5.0, 'middle', 'bold'))
    for ci, (tier, items) in enumerate(CATCH):
        cx = left + lw + ci * colw
        o.append(T(cx + colw / 2, ty + 3.3, tier, 5.2, 'middle', 'bold'))
    for ri, lab in enumerate(['1–2', '3–4', '5–6']):
        yy = ty + 4.6 + ri * rh
        o.append(R(left, yy, lw, rh, 0.2, 0.2, stroke=GRAY))
        o.append(T(left + lw / 2, yy + 3.3, lab, 4.8, 'middle', 'bold'))
        for ci, (tier, items) in enumerate(CATCH):
            cx = left + lw + ci * colw
            o.append(R(cx, yy, colw, rh, 0.2, 0.2, stroke=GRAY))
            o.append(R(cx + 0.7, yy + 0.9, 2.8, 2.8, 0.4, 0.3))
            o.append(T(cx + 4.2, yy + 3.3, items[ri][0], 5.0))
'''
s = s[:a] + new + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
