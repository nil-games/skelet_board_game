# -*- coding: utf-8 -*-
"""Буклет персонажей: тот же формат (A4, 8 панелей). Страницы 2–7: по одному скелету на страницу.
Обложка (1) и оборот (8) свободны от персонажей."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from build_zine import *
from content import SKILLS
from parts_new import ico
from icons import svg_image

from chars_data import CHARS, CELLS, star_cells

SK_ORDER = ['nose', 'bone', 'grab', 'eye', 'scare', 'helm']
# предметы снаряжения из магазина (+1 к проверкам навыка)
GEAR = {'nose': 'Лупа', 'bone': 'Кастеты', 'grab': 'Крюк', 'eye': 'Прицел', 'scare': 'Повязка на глаз', 'helm': 'Компас'}


GEAR_ACC = {'nose': 'Лупу', 'bone': 'Кастеты', 'grab': 'Крюк', 'eye': 'Прицел', 'scare': 'Повязку на глаз', 'helm': 'Компас'}


def sk_icon(kind, cx, cy, k=0.56, sw=0.55):
    """Иконка навыка из папки «Значки навыков» (она же — символ проверки в выборах событий)."""
    return svg_image(kind, cx, cy, 4.7)


def wrap_text(s, n):
    rows, cur = [], ''
    for w_ in s.split(' '):
        if len((cur + ' ' + w_).strip()) > n:
            rows.append(cur)
            cur = w_
        else:
            cur = (cur + ' ' + w_).strip()
    if cur:
        rows.append(cur)
    return rows


def box(x, y, s, n=None, filled=False, star=False, blocked=False, fs=5.0):
    if blocked:
        return (R(x, y, s, s, 0.4, 0.3, 'none', INK) + L(x + 0.5, y + 0.5, x + s - 0.5, y + s - 0.5, 0.3, INK)
                + L(x + s - 0.5, y + 0.5, x + 0.5, y + s - 0.5, 0.3, INK))
    o = [R(x, y, s, s, 0.4, 0.3, INK if filled else 'none')]
    if star:
        o.append(T(x + s / 2, y + s * 0.8, '✦', 5.2, 'middle', fill=INK, family=SYM))
    elif n is not None:
        o.append(T(x + s / 2, y + s * 0.72, str(n), fs, 'middle', fill=GRAY, family=SANS))
    return ''.join(o)


def char_page(x0, y0, ch, idx):
    o = []
    left = (idx % 2 == 0)
    xl = x0 + (OUT_PAD if left else IN_PAD)
    wd = PW - OUT_PAD - IN_PAD
    y = y0 + OUT_PAD
    half = 33.0                       # левая половина шапки
    # --- шапка: слева номер, название, описание, имя; справа рамка «Портрет»
    o.append(C(xl + 3.6, y + 4.0, 3.6, fill=INK))
    o.append(T(xl + 3.6, y + 5.9, str(idx + 1), 10, 'middle', 'bold', '#fff', SERIF))
    nm = ch['name'].upper()
    fs = min(9.5, (half - 9.0) / (len(nm) * 0.82 * PT))
    o.append(T(xl + 8.2, y + 4.5, nm, fs, weight='bold', family=SERIF))
    ty = y + 9.9
    for row in wrap_text(ch['tag'], 28):
        o.append(T(xl, ty, row, 5.2, fill=GRAY, italic=True))
        ty += 2.5
    o.append(T(xl, y + 17.2, 'Имя:', 6.2, weight='bold'))
    o.append(L(xl + 7, y + 17.2, xl + half, y + 17.2, 0.3))
    px = xl + half + 1.5
    o.append(R(px, y, wd - half - 1.5, 19.0, 1.2, 0.3, dash='1.2 1'))
    o.append(T(px + (wd - half - 1.5) / 2, y + 10.5, 'Портрет', 5.6, 'middle', fill=GRAY, italic=True))
    # --- навыки
    y += 22.0
    o.append(T(xl, y, 'НАВЫКИ', 6.2, weight='bold', ls=0.3))
    o.append(T(xl + 17.5, y, '✕ недоступно · ✦ искра', 4.8, fill=GRAY, family=SYM))
    gx = xl + 45.2
    o.append(T(gx, y, 'СНАРЯЖЕНИЕ', 5.0, fill=GRAY, weight='bold'))
    y += 1.6
    s = 3.6
    pitch = 4.5
    cap = ch['cap']
    stars = star_cells(0)
    for k in SK_ORDER:
        o.append(sk_icon(k, xl + 2.5, y + s / 2 + 0.05, k=0.5))
        o.append(T(xl + 5.6, y + 3.0, SKILLS[k], 5.7))
        for i in range(1, CELLS + 1):
            bx = xl + 18.3 + (i - 1) * (s + 0.55)
            o.append(box(bx, y, s, star=(i in star_cells(cap[k]) and i <= cap[k]), blocked=i > cap[k]))
        o.append(T(gx, y + 3.0, '+2 за ' + GEAR_ACC[k], 4.8 if len(GEAR_ACC[k]) > 9 else 5.0))
        o.append(box(xl + wd - s, y, s))
        y += pitch
    y += 3.6
    # --- счётчики: подпись над квадратом
    o.append(T(xl, y, 'СЧЁТЧИКИ', 6.2, weight='bold', ls=0.2))
    o.append(T(xl + 20.5, y, 'метка: ✓ ставят, при срабатывании снимают', 4.6, fill=GRAY, italic=True, family=SYM))
    y += 3.4
    cw = wd / 4
    sq = 12.0
    for i, (name, ik) in enumerate((('Слава', 'F'), ('Удача', 'L'), ('Сокровища', 'T'), ('Искры', None))):
        cx = xl + i * cw
        if ik:
            o.append(svg_image(ik, cx + 2.0, y - 1.5, 3.9))
        else:
            o.append(T(cx + 0.2, y, '✦', 6.0, family=SYM))
        o.append(T(cx + 4.7, y, name, 5.2))
        o.append(R(cx + 0.2, y + 0.9, sq, sq, 0.7, 0.35))
    y += 0.9 + sq + 2.4
    for i, (name, desc) in enumerate((('Благословение', ('обязательно в следующей', 'проверке: 2 кубика, худший')), ('Проклятие', ('обязательно в следующей', 'проверке: 2 кубика, лучший')))):
        cx = xl + i * (half + 1.5)
        o.append(R(cx + 0.2, y, 5.0, 5.0, 0.6, 0.35))
        o.append(T(cx + 6.6, y + 2.2, name, 5.4, weight='bold'))
        o.append(T(cx + 6.6, y + 4.6, desc[0], 4.6, fill=GRAY))
        o.append(T(cx + 6.6, y + 6.9, desc[1], 4.6, fill=GRAY))
        o.append(svg_image('BL' if i == 0 else 'CU', cx + half - 3.2, y + 2.4, 5.4))
    y += 10.2
    # --- заметки (слева) и предметы (справа)
    o.append(T(xl, y, 'ЗАМЕТКИ', 6.2, weight='bold'))
    o.append(T(xl + 12.5, y, 'слова для флешбеков', 4.8, fill=GRAY, italic=True))
    o.append(T(xl + half + 1.5, y, 'ПРЕДМЕТЫ', 6.2, weight='bold'))
    y += 1.4
    bottom = y0 + PH - OUT_PAD
    n = max(3, int((bottom - y) // 3.7))
    step = (bottom - y) / n
    for j in range(n):
        ly = y + step * (j + 1) - 0.4
        o.append(T(xl, ly - 0.5, str(j + 1), 4.8, fill=GRAY))
        o.append(L(xl + 3.0, ly, xl + half, ly, 0.25, '#888'))
        o.append(L(xl + half + 1.5, ly, xl + wd, ly, 0.25, '#888'))
    return '\n'.join(o), bottom - y0


def cover(x0, y0):
    cx = x0 + PW / 2
    o = [R(x0 + 4, y0 + 5, PW - 9, PH - 10, 2.0, 0.6), R(x0 + 5.3, y0 + 6.3, PW - 11.6, PH - 12.6, 1.4, 0.25)]
    o.append(T(cx, y0 + 25, 'СКЕЛЕТЫ', 17, 'middle', 'bold', family=SERIF, ls=1))
    o.append(T(cx, y0 + 35, 'НА БОРТУ', 17, 'middle', 'bold', family=SERIF, ls=1))
    o.append(C(cx, y0 + 62, 11, 0.5))
    o.append(R(cx - 6, y0 + 70, 12, 7, 1.2, 0.4))
    o.append(C(cx - 4.2, y0 + 60, 2.6, 0.4, INK)); o.append(C(cx + 4.2, y0 + 60, 2.6, 0.4, INK))
    o.append(L(cx, y0 + 64, cx, y0 + 67, 0.4))
    for i in range(5):
        o.append(L(cx - 4 + i * 2, y0 + 70, cx - 4 + i * 2, y0 + 77, 0.3))
    o.append(T(cx, y0 + 92, 'Листы скелетов · 6 персонажей', 6, 'middle', italic=True))
    o.append(T(cx, y0 + 96.5, 'Прототип v0.1 · к игре «Всем костям на борт!»', 5.2, 'middle', fill=GRAY))
    return '\n'.join(o)


def arrow(x1, y1, x2, y2, tip=1.0):
    """Линия со стрелкой (наконечник — маленький треугольник, направление по последнему отрезку)."""
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    px, py = x2 - tip * math.cos(ang), y2 - tip * math.sin(ang)
    nx, ny = -math.sin(ang) * tip * 0.5, math.cos(ang) * tip * 0.5
    return L(x1, y1, px, py, 0.35) + '<polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="%s"/>' % (x2, y2, px + nx, py + ny, px - nx, py - ny, INK)


def scheme(x, y, w):
    """Схема: Карта → (Палуба | Порт | Борт) → Карта. Высота ~22 мм."""
    o = []
    bw, bh = 17.0, 5.0
    cx = x + w / 2
    xs = [x + bw / 2 + 0.5, cx, x + w - bw / 2 - 0.5]
    top, mid, bot = y, y + 8.5, y + 17.0
    for bx, by_, name in ((cx, top, 'Карта'), (xs[0], mid, 'Палуба'), (xs[1], mid, 'Порт'), (xs[2], mid, 'Борт'), (cx, bot, 'Карта')):
        o.append(R(bx - bw / 2, by_, bw, bh, 0.8, 0.35))
        o.append(T(bx, by_ + 3.5, name, 5.6, 'middle', 'bold'))
    # верхняя Карта → три страницы
    o.append(L(cx - bw / 2, top + bh / 2, xs[0], top + bh / 2, 0.35) + arrow(xs[0], top + bh / 2, xs[0], mid))
    o.append(arrow(cx, top + bh, cx, mid))
    o.append(L(cx + bw / 2, top + bh / 2, xs[2], top + bh / 2, 0.35) + arrow(xs[2], top + bh / 2, xs[2], mid))
    # три страницы → нижняя Карта
    o.append(L(xs[0], mid + bh, xs[0], bot + bh / 2, 0.35) + arrow(xs[0], bot + bh / 2, cx - bw / 2, bot + bh / 2))
    o.append(arrow(cx, mid + bh, cx, bot))
    o.append(L(xs[2], mid + bh, xs[2], bot + bh / 2, 0.35) + arrow(xs[2], bot + bh / 2, cx + bw / 2, bot + bh / 2))
    return chr(10).join(o)


def back(x0, y0):
    """Памятка игры (страница 8 буклета персонажей): схема «Карта → Палуба / Порт / Борт → Карта» и краткие правила."""
    o = []
    x = x0 + IN_PAD
    wd = PW - OUT_PAD - IN_PAD
    y = y0 + OUT_PAD + 3.6
    o.append(T(x, y, 'ПАМЯТКА', 8.5, weight='bold', family=SERIF, ls=0.4))
    o.append(scheme(x, y + 2.2, wd))
    y += 2.2 + 25.6
    o.append(T(x, y, 'Тип клетки → приложение даёт событие и страницу.', 4.8, fill=GRAY))
    o.append(T(x, y + 2.4, 'Остров получает номер (цифра в △): по нему вернётесь.', 4.8, fill=GRAY))
    items = [('РАУНД', 'Эпизод → Выбор (по Славе) → Действия 1–7 → Конец'),
             ('ПРОВЕРКА', 'd6 + навык + бонусы: ≤3 · 4–6 · 7–9 · 10+'),
             ('УДАЧА', '−1 Удачи = перебросить свой кубик'),
             ('КОНЕЦ РАУНДА', 'Ром 0 → Ропот +1 · края шкал'),
             ('ЖАЖДА', 'Команда 1–3 → 1 · 4–7 → 2 · 8–10 → 3'),
             ('ХОД · РАЗВЕДКА', 'ход бесплатно; разведка и полный вперёд: Ром −1'),
             ('ИГОРНЫЙ ДОМ', 'ставка ≤2 (№4–5: ≤1); 7/11 победа, 2/3/12 проигрыш'),
             ('ПОРАЖЕНИЕ', 'Корпус/Команда 0 · Ропот ≥ Команды')]
    y += 5.0
    for k, v in items:
        o.append(T(x, y + 2.0, k, 5.4, weight='bold'))
        o.append(T(x, y + 4.5, v, 5.0))
        y += 6.4
    return chr(10).join(o)


def build():
    top = []
    for i, ch in enumerate(CHARS[:4]):   # страницы 2,3,4,5 до поворота слева направо
        top.append(char_page(PW * i, 0, ch, i)[0])
    bottom = []
    for j, ch in enumerate(CHARS[4:]):   # страницы 6,7
        bottom.append(char_page(PW * j, 0, ch, 4 + j)[0])
    bottom.append(back(PW * 2, 0))
    bottom.append(cover(PW * 3, 0))
    marks = []
    for xv in (PW, PW * 2, PW * 3):
        marks.append(L(xv, 0, xv, 2.2, 0.2, '#999'))
        marks.append(L(xv, 207.8, xv, 210, 0.2, '#999'))
    marks.append(L(0, 105, 2.2, 105, 0.2, '#999'))
    marks.append(L(294.8, 105, 297, 105, 0.2, '#999'))
    marks.append(L(PW, 105, PW * 3, 105, 0.35, '#888', '1.2 1.2'))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210">'
           '<rect width="297" height="210" fill="#fff"/><g transform="rotate(180 148.5 52.5)">%s</g>'
           '<g transform="translate(0 105)">%s</g>%s</svg>') % ('\n'.join(top), '\n'.join(bottom), '\n'.join(marks))
    return ('<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Буклет персонажей</title>'
            '<style>@page{size:A4 landscape;margin:0}html,body{margin:0;padding:0;background:#fff}svg{display:block}'
            '@media screen{body{background:#ccc}svg{margin:10px auto;box-shadow:0 0 6px #666}}</style></head><body>%s</body></html>') % svg


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '..', 'Буклет_персонажей_A4.html')
    open(out, 'w', encoding='utf-8').write(build())
    print('ok', max(char_page(0, 0, c, i)[1] for i, c in enumerate(CHARS)), 'мм высота (лимит %d)' % (PH - OUT_PAD))
