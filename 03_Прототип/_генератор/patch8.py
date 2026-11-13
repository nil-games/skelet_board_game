# -*- coding: utf-8 -*-
import re
# ---------------------------------------------------------------- content.py
p = 'content.py'
s = open(p, encoding='utf-8').read()
if '_remap' not in s:
    marker = "HAZARDS = ["
    code = '''
# --- v13: палуба = 6 слотов (1–3 личные, 4–6 общие) + слот 7 «Рыбалка» (только штиль и особый штиль).
# Прежние номера 5, 6, 7(по условию), 8(Перекур) переносятся в 4, 5, 6, 6. Перекур пропадает, если слот 6 занят условием-предметом.
ROUTINE['cells'].pop(3, None)   # рыбалка теперь отдельный слот 7


def _remap(ev):
    c = ev['cells']
    gated = 7 in c and c[7].get('req')
    new = {}
    for n, a in c.items():
        if n == 8 and gated:
            continue
        new[{5: 4, 6: 5, 7: 6, 8: 6}.get(n, n)] = a
    ev['cells'] = new


for _e in EVENTS + [ROUTINE]:
    _remap(_e)

FISH = act('Порыбачить', 'grab', [{}, {'R': 1}, {'R': 1, 'T': 1}],
           note='Слот 7 доступен только в штиле и особом штиле. Улов в особом штиле определяет сценарий.')
for _e in EVENTS:
    if _e['hint'] in ('s', 'sp'):
        _e['cells'][7] = FISH
ROUTINE['cells'][7] = act('Порыбачить (только если клетка — штиль или особый штиль)', 'grab', [{}, {'R': 1}, {'R': 1, 'T': 1}],
                          note='Слот 7 доступен только в штиле и особом штиле.')

'''
    i = s.index(marker)
    s = s[:i] + code + s[i:]
open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- sim.py
p = 'sim.py'
s = open(p, encoding='utf-8').read()
s = s.replace("if n <= 4 and n in taken", "if n <= 3 and n in taken")
open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- build_book.py
p = 'build_book.py'
s = open(p, encoding='utf-8').read()
s = s.replace("blocked = [n for n in range(1, 9) if n not in cells]", "blocked = [n for n in range(1, 8 if kind == 'sea' else 5) if n not in cells]")
open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- parts_new.py: палуба
p = 'parts_new.py'
s = open(p, encoding='utf-8').read()
a = s.index("    # слоты: слева личные 1-4")
b = s.index("    return '\\n'.join(o)", a)
new = '''    # слоты: слева личные 1-3 (круг), справа общие 4-6 (пунктир под 2 кубика)
    top = y0 + 18.0
    sh = 18.2
    gap = 1.4
    cw = (pw - 1.2) / 2
    for i in range(3):
        y = top + i * (sh + gap)
        o.append(C(left + cw / 2, y + sh / 2, 8.3, 0.55))
        o.append(badge(left + 4.4, y + 4.6, i + 1, 3.3, 10))
        rx = left + cw + 1.2
        o.append(R(rx, y, cw, sh, 1.8, 0.4, dash='1.8 1.3'))
        o.append(badge(rx + 4.4, y + 4.6, i + 4, 3.3, 10))
    # слот 7: Рыбалка (общий, пунктир на всю ширину)
    fy = top + 3 * (sh + gap) + 1.0
    fh = y0 + PH - OUT_PAD - fy
    o.append(R(left, fy, pw, fh, 1.8, 0.4, dash='1.8 1.3'))
    o.append(badge(left + 4.4, fy + 4.6, 7, 3.3, 10))
    o.append(T(left + 10.0, fy + 5.4, 'РЫБАЛКА', 8, weight='bold', family=SERIF, ls=0.3))
    o.append(T(left + 2.4, fy + 11.0, 'Доступно во время штиля', 5.4, fill=GRAY))
    o.append(T(left + 2.4, fy + 14.0, 'и ос. штиля', 5.4, fill=GRAY))
'''
s = s[:a] + new + s[b:]
open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- build_chars.py: памятка
p = 'build_chars.py'
s = open(p, encoding='utf-8').read()
s = s.replace("Действия 1–8", "Действия 1–7")
open(p, 'w', encoding='utf-8').write(s)
p = 'parts_new.py'
s = open(p, encoding='utf-8').read()
s = s.replace("Действия 1–8", "Действия 1–7")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
