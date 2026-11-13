# -*- coding: utf-8 -*-
import re
# ---------------------------------------------------------------- content.py
p = 'content.py'
s = open(p, encoding='utf-8').read()
a = s.index("HINT_TABLE = [")
b = s.index("# ----------------------------------------------------------------- ШКАЛЫ")
s = s[:a] + """HINT_TABLE = [(1, 1, 's', '~', 'Штиль'), (2, 2, 'sp', '⌇', 'Особый штиль'), (3, 3, 'st', 'ϟ', 'Шторм'),
              (4, 4, 'sh', '⚓', 'Корабль'), (5, 5, 'f', '☁', 'Туман'), (6, 6, 'i', '▲', 'Остров')]
HINT_SYMBOL = {'s': '~', 'sp': '⌇', 'st': 'ϟ', 'sh': '⚓', 'f': '☁', 'i': '▲'}

""" + s[b:]
# два новых эпизода для особого штиля — перед РУТИНОЙ
marker = "ROUTINE = dict("
new_ev = '''
EVENTS += [
    dict(id='SP1', hint='sp', title='Зеркальное море',
         flavor='Штиль такой полный, что море превращается в зеркало. В нём отражается ваш корабль, только отражение не повторяет ваши движения: оно машет вам первым и, кажется, ждёт ответа.',
         warn='Не отвечайте на приветствия двойника.',
         cells={
             1: act('Скользить по зеркалу', 'helm', [{}, {'mv': 1}, {'mv': 1, 'F': 1}]),
             2: act('Присмотреться к двойнику', 'nose', [{'M': -1}, {'sc': 1}, {'sc': 2, 'L': 1}]),
             3: act('Скорчить рожу двойнику', 'scare', [{'F': -1}, {'M': 1}, {'M': 1, 'F': 1}]),
             5: act('Выудить из зеркала то, что в нём плавает', 'grab', [{'H': -1}, {'T': 1}, {'T': 2}]),
             8: REST,
         }, end=None),
    dict(id='SP2', hint='sp', title='Ромовый дождь',
         flavor='С чистого неба начинает капать ром. Команда ложится на спину и открывает рты. Квартирмейстер напоминает, что ром — это не питьё, а образ жизни.',
         warn='Лишнее выходит боком, и не только через рёбра.',
         cells={
             1: act('Выплыть из-под дождя', 'helm', [{'R': 1}, {'mv': 1}, {'mv': 1}]),
             2: act('Устроить пляски под дождём', 'bone', [{'H': -1}, {'M': 1}, {'M': 2}]),
             3: act('Запретить пить из соображений дисциплины', 'scare', [{'M': -1}, {'R': -1}, {'R': -1, 'M': 1}]),
             5: act('Подставлять бочки', 'grab', [{'R': 1}, {'R': 2}, {'R': 3}]),
             8: fixed('Просто выпить', {'R': 1, 'M': 1}),
         }, end=None),
]

'''
i = s.index(marker)
s = s[:i] + new_ev + s[i:]
open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- build_book.py
p = 'build_book.py'
b = open(p, encoding='utf-8').read()
b = b.replace("names = {'s': 'S1, S2', 'st': 'ST1, ST2',", "names = {'s': 'S1, S2', 'sp': 'SP1, SP2', 'st': 'ST1, ST2',")
open(p, 'w', encoding='utf-8').write(b)

# ---------------------------------------------------------------- parts_new.py
p = 'parts_new.py'
s = open(p, encoding='utf-8').read()

icons = '''
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

'''
s = s.replace("def wrap(s, n):", icons + "\ndef wrap(s, n):", 1)

# --- подсказки на карте: 6 значков в две строки по три
a = s.index("    side.append(T(0, 15.2, 'Значок клетки (бросок d6):'")
b = s.index("    side.append('</g>')", a)
s = s[:a] + """    side.append(T(0, 16.0, 'Значок клетки (бросок d6):', 6, weight='bold'))
    segs = [('1', 'wave', 'штиль'), ('2', 'zig', 'особый штиль'), ('3', 'bolt', 'шторм'),
            ('4', None, 'корабль'), ('5', None, 'туман'), ('6', None, 'остров')]
    txt = {'4': '⚓', '5': '☁', '6': '▲'}
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
    side.append(T(0, 1.4, 'Новая клетка: ✓ + эпизод. С ✓ — рутина.', 5.5, fill=GRAY))
""" + s[b:]

# --- судовой журнал: цифры 1-6 сверху, значки сбоку
a = s.index("def back_panel")
s = s[:a] + '''def back_panel(x0, y0):
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
    return '\\n'.join(o)
'''
open(p, 'w', encoding='utf-8').write(s)
print('ok')
