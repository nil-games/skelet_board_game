# -*- coding: utf-8 -*-
"""Бумажная замена приложения: Книга событий + Листы игры (корабельный журнал, листы скелетов)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from content import *
from icons import img as sk_img, entity_html, NAMES as ICON_NAMES
from tutorial import tutorial

OUT = os.path.join(os.path.dirname(__file__), '..')
TIER4 = ['≤3', '4–6', '7–9', '10+']
TIER3 = ['≤3', '4–6', '7+']
CSS = """
@page{size:A4;margin:12mm}
body{font-family:'Segoe UI',Arial,sans-serif;font-size:10pt;color:#111;margin:0;line-height:1.3}
h1{font-family:Georgia,serif;font-size:22pt;margin:0 0 4mm}
h2{font-family:Georgia,serif;font-size:14pt;margin:5mm 0 2mm;border-bottom:1.5px solid #111}
h3{font-size:11pt;margin:3mm 0 1mm}
.sk{vertical-align:-0.9mm;margin:0 0 0 1.2mm}
.ev{border:1.5px solid #111;border-radius:3mm;padding:3mm 4mm;margin:0 0 5mm;break-inside:avoid}
.ev .hd{font-family:Georgia,serif;font-size:13pt;font-weight:bold}
.sym{font-family:'Segoe UI Symbol','Segoe UI Emoji',sans-serif}
.read{background:#f2f2f2;border-radius:2mm;padding:2mm 3mm;margin:2mm 0}
.warn{font-style:italic}
.lock{font-size:8.5pt;color:#555;margin:2mm 0 1mm}
table{border-collapse:collapse;width:100%;font-size:9pt}
td,th{border:1px solid #888;padding:1mm 1.6mm;vertical-align:top}
th{background:#e6e6e6;text-align:left}
.cap{white-space:nowrap}
.tbl td.n{width:5mm;text-align:center;font-weight:bold}
small{color:#555}
.pb{break-before:page}
.say{background:#fff7d6;border-left:4px solid #d9a400;padding:2mm 3mm;margin:2mm 0}
.teach{background:#e8f0fb;border-left:4px solid #3566b0;padding:2mm 3mm;margin:2mm 0}
.ok{background:#e4f5e4;border-left:4px solid #3a8a3a;padding:2mm 3mm;margin:2mm 0}
.box{display:inline-block;width:5.5mm;height:5.5mm;border:1px solid #111;margin-right:0.8mm;text-align:center;line-height:5.5mm;font-size:8pt;vertical-align:middle}
.box.f{background:#111;color:#fff}
.box.x{background:repeating-linear-gradient(45deg,#ccc,#ccc 1.2px,#fff 1.2px,#fff 3px)}
.sheet{border:1.5px solid #111;border-radius:3mm;padding:3mm 4mm;margin-bottom:5mm;break-inside:avoid}
.row{display:flex;align-items:center;margin:1.2mm 0}
.row b{display:inline-block;width:25mm}
"""


ENT = {'H': 'Корпус', 'R': 'Ром', 'C': 'Команда', 'M': 'Ропот', 'D': 'Опасность', 'F': 'Слава', 'L': 'Удача', 'T': 'Сокровища',
       'S': 'Искры', 'mv': 'ход', 'sc': 'разведка', 'catch': 'улов', 'RT': 'Ром', 'pick': 'Ром/Сокровища/Корпус', 'BL': 'метка', 'CU': 'метка'}


def entities(a):
    keys = []
    for t in a['tiers']:
        keys += list(t.keys())
    for ch in a.get('choices', []):
        keys += list(ch[1].keys())
    if a.get('cost'):
        keys += list(a['cost'].keys())
    out = []
    names = []
    for k in keys:
        if k in ENT and ENT[k] not in names:
            names.append(ENT[k])
            out.append(entity_html(k))
    return out


def tier_rows(a):
    t = a['tiers']
    tx = a.get('texts') or [''] * len(t)
    if a.get('choices'):
        rows = ''.join('<tr><td class="cap"><b>%s</b></td><td>%s <small>%s</small></td></tr>' % (lab, txt, fx(eff)) for lab, eff, txt in a['choices'])
        return rows
    if len(t) == 1:
        return '<tr><td colspan="2">%s <small>%s</small></td></tr>' % (tx[0], fx(t[0]))
    labels = TIER3 if len(t) == 3 else TIER4
    return ''.join('<tr><td class="cap">%s</td><td>%s <small>%s</small></td></tr>' % (l, x, fx(e)) for l, x, e in zip(labels, tx, t))


def event_block(ev, kind='sea', anchor=False):
    sym = HINT_SYMBOL.get(ev.get('hint'), '')
    cells = ev['cells']
    top = 7 if kind == 'sea' else 4
    blocked = [n for n in range(1, top + 1) if n not in cells]
    mand = [n for n, a in cells.items() if a['mandatory']]
    alarm = [n for n, a in cells.items() if a.get('alarm')]
    h = ['<div class="ev"%s><div class="hd"><span class="sym">%s</span> %s <small>[%s]</small></div>' % (' id="ev-%s"' % ev['id'] if anchor else '', sym, ev['title'], ev['id'])]
    if kind == 'sea':
        h[0] = h[0].replace('</div>', ' <small>Тип: %s</small></div>' % ('цикл: круг повторяется, пока корабль не уйдёт' if ev.get('flow') == 'loop' else 'проходной: после раунда корабль уходит сам'), 1)
    h.append('<div class="read"><b>Читать вслух.</b> %s' % ev['flavor'])
    if ev['warn'] != '—':
        h.append('<div class="warn">Предупреждение: %s</div>' % ev['warn'])
    marks = ['Заблокированы (✗): %s' % (', '.join(map(str, blocked)) or 'нет')]
    if mand:
        marks.append('<b>Обязательны («!»): %s</b> (любой игрок обязан поставить туда кубик)' % ', '.join(map(str, mand)))
    if alarm:
        marks.append('<b>Тревожные (⚠): %s</b> (штраф, если никто не выберет)' % ', '.join(map(str, alarm)))
    h.append('<div class="lock">%s</div>' % ' · '.join(marks))
    if kind == 'port':
        h.append('<div class="lock"><b>Рыба:</b> этот порт %s.</div>' % ev.get('fish', 'платит по цене'))
        h.append('<div class="lock">В этом порту: Магазин (слот 5) — %s · Игорный дом (слот 6) — %s</div>' % ('есть' if ev.get('shop') else '<b>нет</b>', 'есть' if ev.get('casino') else '<b>нет</b>'))
    h.append('<table class="tbl"><tr><th>№</th><th>Действие (читать при выборе)</th><th>Тип · что затрагивает</th></tr>')
    for n in sorted(cells):
        a = cells[n]
        if a.get('choices'):
            typ = 'выбор'
        elif a['skill']:
            typ = 'проверка: %s' % SKILLS[a['skill']]
        else:
            typ = 'без проверки'
        ent = entities(a)
        h.append('<tr><td class="n">%s</td><td>%s%s%s%s%s</td><td><small>%s%s</small></td></tr>' % (
            n, a['title'], sk_img(a['skill']) if a['skill'] else '', ' <b>!</b>' if a['mandatory'] else '', ' <b>⚠</b>' if a.get('alarm') else '',
            (' <i>(открывается, если у кого-то из команды есть: %s)</i>' % a['req'] if a.get('req') else '') + (' <i>(открыт, только если Команда ≥ %d)</i>' % a['crew_req'] if a.get('crew_req') else ''),
            typ, ' · ' + ' &nbsp; '.join(ent) if ent else ''))
    h.append('</table></div>')
    h.append('<div class="lock">🔒 Результаты: читать только в фазе действий, когда слот разыгрывается (кубик бросают, если действие — проверка).</div>')
    h.append('<table><tr><th>№ · тип</th><th>Исходы (что произошло · числа)</th></tr>')
    for n in sorted(cells):
        a = cells[n]
        typ = 'выбор' if a.get('choices') else ((sk_img(a['skill']) + ' ' + SKILLS[a['skill']]) if a['skill'] else 'без проверки')
        extra = ''
        if a.get('note'):
            extra += '<small>%s</small><br>' % a['note']
        if a.get('excl'):
            extra += '<small><b>Взаимоисключение:</b> %s</small>' % a['excl']
        h.append('<tr><td class="cap">%s · %s</td><td><table>%s</table>%s</td></tr>' % (n, typ, tier_rows(a), extra))
    h.append('</table>')
    if alarm:
        h.append('<div><b>Тревожные слоты.</b> В конце фазы действий, если на слоте нет ни одного кубика: %s.</div>' % '; '.join(
            'слот %d — %s' % (n, cells[n]['alarm']) for n in alarm))
    if ev.get('end'):
        h.append('<div><b>В конце раунда:</b> %s</div>' % ev['end'])
    if kind == 'port':
        h.append('<div class="lock"><b>После порта:</b> корабль остаётся в порту, пока группа не решит выйти. Закончив порт (в свободном плавании хватит одного раунда), вернитесь на Карту и проведите линию в соседнюю клетку.</div>')
    elif ev.get('flow') == 'loop':
        h.append('<div class="lock"><b>После раунда:</b> если слотом «Штурвал» корабль не вышел из клетки (нет исхода с Ходом), он остаётся: следующий раунд читайте этот же эпизод (новый круг, цена круга указана выше). Если вышел, вернитесь на Карту и проведите линию.</div>')
    else:
        h.append('<div class="lock"><b>После раунда:</b> корабль <b>уходит из клетки сам, что бы ни случилось</b>. Вернитесь на Карту и проведите линию в соседнюю клетку (куда, решает группа; учитывайте разведку).</div>')
    h.append('</div>')
    return ''.join(h)



import re as _re
PAGES = {}
TITLES = {}


def pg(i):
    return '<a href="#ev-%s">стр. %s</a>' % (i, PAGES.get(i, '?'))


def short(t, n=96):
    first = _re.split(r'(?<=[.!?])\s', t)[0]
    return first if len(first) <= n else first[:n - 1].rstrip() + '…'


def flow_name(e):
    return 'цикл' if e.get('flow') == 'loop' else 'проходной'


def battle_block(b):
    import content
    cls = b['cls']
    u, ds = content.ENEMY_DAMAGE[cls]
    reward = content.BATTLE_REWARD[cls]
    h = ['<div class="ev" id="ev-%s"><div class="hd"><span class="sym">⚓</span> %s <small>[%s] · Тип: бой (Борт), враг: %s</small></div>' % (b['id'], b['title'], b['id'], cls)]
    h.append('<div class="read"><b>Читать вслух.</b> %s<div class="warn">Предупреждение: %s</div></div>' % (b['flavor'], b['warn']))
    h.append('<table><tr><th>Скелетов (ходов за круг)</th><th>Корпус врага</th><th>Руль S</th><th>Урон врага</th></tr>')
    for n, (hull, s_) in content.ENEMY_BY_N.items():
        h.append('<tr><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (n, hull + b.get('hull_bonus', 0), s_ + ds, u))
    h.append('</table>')
    h.append('<div><b>Особенность:</b> %s</div>' % b['special'])
    h.append('<div><b>Порядок:</b> идите на страницу <b>Борт</b> (буклет, стр. 3). Правила боя — раздел «Морской бой «Залп»» ниже (и урок 4 Обучения).</div>')
    h.append('<div><b>Награда:</b> победа — Сокровища +%d каждому скелету; ничья (враг отступил) — Сокровища +%d каждому; поражение — игра окончена.</div>' % (reward, reward // 2))
    h.append('<div class="lock"><b>После боя:</b> корабль <b>уходит из клетки сам</b>. Вернитесь на Карту и проведите линию в соседнюю клетку.</div></div>')
    return ''.join(h)


def block_by_id(i):
    import content
    for b in content.BATTLES:
        if b['id'] == i:
            return battle_block(b)
    for e in content.EVENTS:
        if e['id'] == i:
            return event_block(e, anchor=True)
    for p in content.PORTS:
        if p['id'] == i:
            return event_block(p, 'port', anchor=True)
    raise KeyError(i)


def row(d, i, kind, text):
    return '<tr><td class="n">%s</td><td><b>%s</b> <small>%s</small></td><td>%s</td><td><small>%s</small></td><td>%s</td></tr>' % (d, TITLES[i], i, kind, text, pg(i))


def lists_html():
    import content
    for e in content.EVENTS:
        TITLES[e['id']] = e['title']
    for b in content.BATTLES:
        TITLES[b['id']] = b['title']
    for p in content.PORTS:
        TITLES[p['id']] = p['title']
    desc = {e['id']: short(e['flavor']) for e in content.EVENTS}
    desc.update({b['id']: short(b['flavor']) for b in content.BATTLES})
    kinds = {e['id']: flow_name(e) for e in content.EVENTS}
    kinds.update({b['id']: 'бой, враг %s' % b['cls'] for b in content.BATTLES})
    h = ['<h2 id="lists">Списки событий (бросок d6)</h2>']
    h.append('<p><b>Как выбрать событие.</b> Корабль вошёл в клетку: если значка нет, бросьте d6 на <b>тип местности</b> и нарисуйте значок. Затем бросьте d6 по <b>списку этого типа</b> ниже: выпавший номер — событие. Номера страниц нажимаются: переходят в нужный раздел.</p>')
    h.append('<table><tr><th>d6</th><th>Значок</th><th>Тип</th><th>Список</th></tr>')
    names = {'s': 'штиль', 'sp': 'особый штиль (читает список штиля)', 'st': 'шторм', 'sh': 'корабль', 'f': 'туман', 'i': 'остров'}
    anchors = {'s': 'list-s', 'sp': 'list-s', 'st': 'list-st', 'sh': 'list-sh', 'f': 'list-f', 'i': 'list-i'}
    for a, b, code, sy, nm in content.HINT_TABLE:
        h.append('<tr><td>%s</td><td><span class="sym">%s</span></td><td>%s</td><td><a href="#%s">к списку</a></td></tr>' % (str(a) if a == b else '%d–%d' % (a, b), sy, names[code], anchors[code]))
    h.append('</table>')

    def table(anchor, title, ids, note=''):
        t = ['<h3 id="%s">%s</h3>' % (anchor, title)]
        if note:
            t.append('<p><small>%s</small></p>' % note)
        t.append('<table><tr><th>d6</th><th>Событие</th><th>Тип</th><th>О чём</th><th>Страница</th></tr>')
        for k, i in enumerate(ids):
            t.append(row(k + 1, i, kinds.get(i, 'порт'), desc.get(i, '')))
        t.append('</table>')
        return ''.join(t)
    P = content.POOLS
    h.append(table('list-s', '☀ Штиль и особый штиль', P['s'], 'На штиле и особом штиле работает слот 7 «Рыбалка». У особого штиля свой улов (регион задаёт сценарий).'))
    h.append(table('list-st', 'ϟ Шторм', P['st'], 'Все шторма — циклы: корабль уходит только слотом «Штурвал»; новый круг стоит Ропот +1 и Корпус −1.'))
    h.append(table('list-f', '☁ Туман', P['f']))
    h.append(table('list-sh', '⚓ Корабль', P['sh'], 'Чаще всего бой (Борт). Остальное — мирные встречи на Палубе: переговоры, торговля, погоня.'))
    h.append('<h3 id="list-i">△ Остров</h3><p>Первый заход: присвойте острову номер (△ с цифрой внутри) и бросьте d6: <b>1–4 — порт</b> (дальше d6 по таблице портов), <b>5–6 — необитаемый остров</b> (дальше d6 по списку необитаемых). Повторный заход: найдите номер в Журнале островов.</p>')
    port_ids = [x[2] for x in content.PORT_TABLE]
    pdesc = {p['id']: 'Магазин: %s · Игорный дом: %s · Рыба: %s' % ('есть' if p.get('shop') else 'нет', 'есть' if p.get('casino') else 'нет', p.get('fish', '')) for p in content.PORTS}
    t = ['<h4>Порты (d6)</h4><table><tr><th>d6</th><th>Порт</th><th>Тип</th><th>Что есть</th><th>Страница</th></tr>']
    for k, i in enumerate(port_ids):
        t.append(row(k + 1, i, 'порт', pdesc[i]))
    t.append('</table>')
    h.append(''.join(t))
    wild = ['<h4>Необитаемые острова (d6)</h4><table><tr><th>d6</th><th>Событие</th><th>Тип</th><th>О чём</th><th>Страница</th></tr>']
    for k, i in enumerate(P['i_wild']):
        wild.append(row(k + 1, i, kinds[i], desc[i]))
    wild.append('</table>')
    h.append(''.join(wild))
    return ''.join(h)


def events_html():
    import content
    P = content.POOLS
    out = []
    for n, (key, title) in enumerate((('s', 'Штиль и особый штиль'), ('st', 'Шторм'), ('f', 'Туман'), ('sh', 'Корабль'), ('i_wild', 'Необитаемые острова'))):
        out.append('<h2 class="%s" id="grp-%s">Каталог: %s</h2>' % ('pb' if n == 0 else '', key, title))
        for i in P[key]:
            out.append(block_by_id(i))
    return ''.join(out)


def ports_html():
    import content
    return ''.join(block_by_id(i) for _, _, i in content.PORT_TABLE)


def book(pages=None):
    global PAGES
    PAGES = pages or {}
    h = ['<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Книга событий — прототип</title><style>%s</style></head><body>' % CSS]
    h.append('<h1>Книга событий</h1><p>Бумажная замена приложения для прототипа «Всем костям на борт!». Её читает <b>Писарь</b>.</p>')
    h.append(lists_html())
    h.append('<h2>Как пользоваться</h2><ol>'
             '<li>В начале раунда в море определите <b>эпизод</b> (списки в начале книги) и перейдите на его страницу.</li>'
             '<li>Прочтите блок «Читать вслух»: название, описание, предупреждение. Объявите <b>заблокированные</b> слоты (✗), <b>обязательные</b> («!») и <b>тревожные</b> (⚠), затем названия действий и их типы.</li>'
             '<li>Игроки выбирают слоты. <b>Кубик на слоте — фигурка-маркер, его не бросают.</b> Результаты не читайте.</li>'
             '<li>В фазе действий слоты разыгрываются по номерам. Если действие — <b>проверка</b>, игрок <b>сначала получает +1 к этому навыку</b> (закрашивает клетку), затем бросает свой кубик, прибавляет навык и бонусы, и вы читаете исход. Если проверки нет, исход читается сразу. Сложность проверки (пороги исходов) заранее не показывается.</li>'
             '<li>Записывайте изменения шкал в Корабельный журнал. В конце раунда: тревожные слоты → «В конце раунда» эпизода → если Ром 0: Ропот +1 → края шкал.</li></ol>')
    h.append('<h3>Типы действий и подсказки в списке</h3><ul>'
             '<li><b>Проверка</b>: заранее известно только, <i>проверка какого навыка</i>. Исходы узнаются при выполнении.</li>'
             '<li><b>Без проверки</b>: просто применяется (изменить шкалу, дать предмет, улов, метку в Судовой журнал).</li>'
             '<li><b>Выбор</b>: небольшая развилка с несколькими вариантами (кратко: что выберете, то и произойдёт).</li>'
             '<li>В списке рядом с названием стоит, <b>каких сущностей</b> касается действие (Ром, Ропот, Сокровища…), но <b>не сказано, прибавляется оно или убавляется</b>.</li>'
             '<li><b>Взаимоисключение</b>: некоторые действия отменяют остальные (например, «побег», если он сработал: слоты после него не разыгрываются).</li>'
             '<li><b>Тревожный слот (⚠)</b>: не обязателен, но если на нём нет ни одного кубика, в конце фазы действий наступает указанный штраф. <b>Обязательный слот («!»)</b> другой: кто-то из игроков <i>обязан</i> поставить туда кубик, ситуации «никто не поставил» не бывает.</li></ul>')
    h.append('<h2>Как тестировать</h2><ol><li>Распечатайте: <b>Буклет</b>, <b>Буклет персонажей</b>, <b>Листы игры</b>, <b>Лист теста</b> и эту <b>Книгу</b>.</li><li>Сыграйте <b>Обучение</b> (40–60 мин).</li><li>Сыграйте <b>свободное плавание</b> (60–90 мин) без сценария: эпизоды определяются случайно.</li><li>Заполняйте <b>Лист теста</b> по ходу: раунды, шкалы, замечания.</li></ol>')
    h.extend(tutorial(event_block))
    h.append('<h2>Определение эпизода</h2>')
    h.append('<p><b>Эпизод по значку клетки.</b> Корабль не ставят на карту: ход — <b>линия</b> из клетки в клетку, корабль находится там, где заканчивается последняя линия. Эпизод <b>каждый раз</b> берётся из пула типа местности (значок в клетке): новая клетка и повторный заход ничем не отличаются. Если значка в клетке нет, бросьте d6 на значок и нарисуйте его. Затем d6 по <b>списку этого типа</b> в начале книги (в каждом списке 6 событий): выпавший номер — событие.</p><p><b>Два вида эпизодов.</b> <b>Проходной</b> (в разделе «Тип: проходной»): один раунд, после него корабль <b>сам уходит</b> в соседнюю клетку по решению группы (учитывайте разведку), слот 1 заблокирован. <b>Цикл</b> («Тип: цикл»): если корабль не покинул клетку, <b>следующий раунд читайте тот же эпизод</b> (новый круг), пока кто-то не уведёт корабль слотом 1 «Штурвал» (исход с Ходом). За новый круг без штурвала обычно штраф из «В конце раунда».</p><p><b>Порт.</b> Когда корабль входит в клетку порта, бросьте d6 на тип порта: <b>1–3 Рыночный порт · 4–5 Захолустная пристань · 6 Бухта контрабандистов</b> (разделы «Порт» ниже).</p>')
    h.append('<h2>Острова (номер, порт или необитаемый)</h2><p>При <b>первом</b> заходе на остров (значок △): бросьте d6. <b>1–4 — порт</b> (дальше d6 по таблице портов в начале книги), <b>5–6 — необитаемый остров</b> (дальше d6 по списку необитаемых островов там же). Присвойте острову следующий свободный <b>номер</b> (1, 2, 3…), впишите его цифрой внутрь треугольника △ на карте (△ с цифрой 1, 2, 3…) и запишите в <b>Журнал островов</b> (Корабельный журнал): номер, клетка, что это. Остров №1 — порт назначения.</p><p><b>Повторный заход:</b> найдите номер на карте, откройте Журнал островов и читайте <b>тот же</b> порт или остров (для необитаемого острова: найденное в прошлый раз второй раз не находится). В приложении Писарь вводит номер острова.</p>')
    h.append('<h2 class="pb">Свободное плавание: подготовка</h2><ol>'
             '<li>Сотрите карту и Судовой журнал. Шкалы: <b>Корпус 7 · Команда 6 · Ром 5 · Ропот 0</b>. Скелеты: все разные, Слава/Удача/Сокровища/Искры 0 (снаряжение и улов стёрты).</li>'
             '<li>Корабль стоит на <b>A4</b> (маршрут начинается здесь, рисовать пока нечего). Порт назначения <b>G3</b> — это <b>остров №1</b> (Рыночный порт): нарисуйте треугольник △ с цифрой 1 внутри и запишите остров в Журнал островов. Путь по прямой <b>6 клеток</b>.</li>'
             '<li><b>Каждый раунд в море:</b> (1) посмотрите клетку корабля (где кончается последняя линия): если значка нет, бросьте d6 на значок и нарисуйте его, затем d6 на вариант 1–3 / 4–6 → эпизод; если идёт цикл (корабль не ушёл), читайте тот же эпизод. (2) Писарь читает эпизод, объявляет слоты (✗, «!»). (3) Планирование: порядок по Славе. (4) Действия по номерам 1 → 7, проверка d6 + навык. (5) Конец раунда: «В конце раунда» эпизода → если Ром 0: Ропот +1 → края шкал. (6) Писарь передаёт книгу.</li>'
             '<li><b>Воспоминания:</b> в конце каждого третьего раунда в море (3, 6, 9) — раздел «Воспоминания (флешбек)».</li>'
             '<li><b>Победа:</b> корабль вошёл в G3. Сыграйте один раунд порта (разделы «Порт», «Магазин», «Игорный дом»), затем подведите итог: шкалы, Искры, Слава, Сокровища. Отметьте итог в Листе теста.</li>'
             '<li><b>Поражение:</b> любой край шкалы (Корпус 0, Команда 0) или Ропот ≥ Команды.</li></ol>')
    h.append('<h2>Ром и Жажда</h2><p><b>Жажда</b> по Команде: 1–3 → 1, 4–7 → 2, 8–10 → 3. <b>Раздача рома</b> (обязательный слот-выбор): налить всем — Ром −Жажда, Ропот −1; зажать — Ропот +1; пустить к бочке — Ром −(Жажда+2), выбравший Слава +2. Если Рома не хватает, выпивают остаток. <b>Собрать обломки:</b> ≤3 — 1 вариант, 4–6 — 2, 7+ — 3; варианты: Ром +1 (можно несколько раз), Сокровища +1, Корпус +1. Рыбалка даёт только рыбу на продажу.</p>')
    h.append('<h2 class="pb">Стандарт конца раунда</h2><ol><li>Эффект раздела «В конце раунда».</li><li>Если Ром = 0: <b>Ропот +1</b> (трезвая тоска). Пассивной Жажды нет.</li><li>Эпизод-цикл: если корабль не ушёл — цена нового круга (Ропот +1; в шторме и водовороте ещё Корпус −1).</li><li>Края шкал: Корпус/Команда 0 или Ропот ≥ Команды → поражение. Ром на краях не проигрывает (10 — потолок).</li><li>По желанию (если Ром > 0): <b>Разведка за ром</b> (Ром −1: сначала выберите до 2 пустых клеток вокруг корабля, затем d6 на первую, d6 на вторую и зарисуйте выпавшее) и/или <b>Полный вперёд</b> (Ром −1: при уходе корабль проводит 2 линии).</li><li>Передать телефон Писарю слева; убрать кубики и блокировки.</li></ol>')
    h.append(events_html())
    h.append('<h2 class="pb">Порты (пул типов)</h2><p><small>Порт-раунд: слоты 1–4 по типу порта, ячейки 5 (магазин) и 6 (игорный дом) только если они есть в этом порту. Бросьте d6 на тип порта: 1 Рыночный · 2 Верфь Адмиральской Вдовы · 3 Захолустная пристань · 4 Бухта контрабандистов · 5 Плавучее казино · 6 Рыбацкая деревня. В свободном плавании достаточно одного раунда в порту, затем итог.</small></p>')
    h.append(ports_html())
    h.append('<h2>Игорный дом (ячейка 6)</h2><p>%s</p>' % BET_RULES)
    h.append('<h3>Шуллерские штучки (улучшения игорного дома)</h3><p>Покупаются за Сокровища в игорном доме. Куплено — ставьте ✓ в буклете; использованное зачёркивайте. Улучшения из событий вписывайте в пустые строки. '+CASINO_RULE+'</p><table><tr><th>Название</th><th>Цена</th><th>Эффект</th></tr>')
    for nm, pr, ef in CASINO_UPGRADES:
        h.append('<tr><td>%s</td><td>%dД</td><td>%s</td></tr>' % (nm, pr, ef))
    h.append('</table>')
    h.append('<h2>Магазин (ячейка 5)</h2><p>Колонка «Всегда в наличии» (бывший «Корабль») доступна целиком. На каждый из столбцов «Снаряжение», «Диковинки», «Бой» и «Услуги» бросьте d6: выпавший номер — товар в наличии в этом столбце. Игроки свободно передают друг другу монеты и предметы и могут скидываться (пока корабль на карте). Игрок на слоте Магазина <b>покупает и продаёт сколько угодно</b>, пока хватает монет (своих или скинутых). Товары из столбцов с d6 — в одном экземпляре, «Всегда в наличии» — без ограничений (рыба продаётся отдельно, см. Рыбалку). Цена — число в монете (в Сокровищах). Продажа: половина цены, округлите вниз, не меньше 1 (продавать можно Снаряжение, Диковинки и улов, но не боевые улучшения и не шуллерские штучки). Магазин есть не во всех портах. Снаряжение действует только на купившего; впишите его в заметки листа. Диковинка: у каждой диковинки свой разовый эффект (см. столбец «Диковинки»), либо её сжигают в <b>Поминках</b> в порту (сколько Искр — сказано на Поминках). Дорогие диковинки дают больше Искр: на них копят или покупают несколько дешёвых за несколько визитов.</p><table><tr>')
    for cn, _ in SHOP:
        h.append('<th>%s</th>' % cn)
    h.append('</tr><tr>')
    for cn, items in SHOP:
        h.append('<td><table>')
        for i, (nm, pr, ef) in enumerate(items):
            h.append('<tr><td class="n">%d</td><td>%s <small>(%dД)</small><br><small>%s</small></td></tr>' % (i + 1, nm, pr, ef))
        h.append('</table></td>')
    h.append('</tr></table><p><small>Подробные описания всех предметов — в файле «Каталог_предметов.md» (в приложении их будут открывать по нажатию).</small></p><p><small>Условия-предметы: некоторые эпизоды открывают действие в слоте 6, если у кого-то из команды есть нужное снаряжение или диковинка (см. пометки в эпизодах).</small></p>')
    h.append('<h2>Рыбалка (слот 7 на Палубе)</h2><p>Слот 7 открыт только во время штиля и особого штиля. Игрок проводит проверку Мормышки: ≤3 — ничего; 4–6 — один бросок d6; 7–9 — два броска d6, выберите один улов; 10+ — два броска, берите оба. Столбец таблицы — регион: «Штиль» на обычном штиле; на особом штиле сценарий называет регион (Янтарная мель, Звёздная заводь, Костяные мангры — примеры). Строка — выпавший d6 (1–2, 3–4, 5–6). Отметьте улов ✓ в буклете: рыба на корабле. Рыба — это <b>товар</b>: продайте её в порту за цену в монете (любую выбранную рыбу, не обязательно всю; непроданная рыба остаётся на корабле — пригодится для квестов NPC) и зачеркните ✗. <b>Рыночный порт</b> платит по цене, <b>Захолустная пристань</b> (рыбаки) — на 1 меньше (минимум 1), <b>Рыбацкая деревня</b> — на 1 больше; <b>Бухта контрабандистов</b>, <b>Верфь</b> и <b>Плавучее казино</b> рыбу не берут. Другой пользы у рыбы нет.</p><table><tr><th>d6</th>')
    for hd, full, items in CATCH:
        h.append('<th>%s</th>' % full)
    h.append('</tr>')
    for r, lab in enumerate(['1–2', '3–4', '5–6']):
        h.append('<tr><td class="n">%s</td>%s</tr>' % (lab, ''.join('<td>%s <small>(%d мон.)</small></td>' % (items[r][0], items[r][1]) for hd, full, items in CATCH)))
    h.append('</table>')
    h.append('<h2>Воспоминания (флешбек)</h2><p><b>Когда.</b> После <b>каждого третьего эпизода</b> в море (3-й, 6-й, 9-й раунд в море; считайте по счётчику раундов в Корабельном журнале; в портах не считаем). В конце такого раунда, после конца раунда, наступает событие «Воспоминания».</p><p><b>Кто участвует.</b> Каждый скелет, у которого есть <b>обведённая, но ещё не пережитая Искра</b>. Искра появляется, когда закрашена клетка навыка со значком ✦ или на Поминках/событиях.</p><p><b>Как проходит.</b> Каждый такой скелет по очереди переживает флешбек: в приложении Писарь читает фрагмент из прошлого скелета и игрок делает несколько нарративных выборов. После этого Искра <b>зачёркивается</b> (пережита). Когда пережиты все пять Искр, скелет упокоился.</p><div class=\"teach\"><b>Заглушка для прототипа.</b> Истории пока не написаны. Игрок сам придумывает флешбек в 1–2 предложениях (как он умер, чего не закончил). Затем выбирает: <b>Гордость</b> — Ропот −1 кораблю, или <b>Стыд</b> — Слава +1 ему лично. Зачеркните Искру.</div>')
    h.append('<h2>Морской бой «Залп» (Борт)</h2><p>В коробке <b>6 кубиков</b>. В бою ходящий всегда бросает <b>ровно 5 кубиков</b> (как в Yahtzee). Бой идёт кругами: каждый скелет ходит <b>один раз</b> (по Славе). <b>Враг</b> подбирается под число скелетов N: Корпус и Руль S (4 → 12 и 10, 5 → 14 и 8, 6 → 17 и 6); урон по классу: слабый 1, обычный 2, сильный 3 (и Руль на 1 выше).</p><ol><li><b>Бросок.</b> Ходящий бросает 5 кубиков.</li><li><b>Переброс.</b> Один раз любое число из них (+1 за каждую Удачу).</li><li><b>Распределение.</b> Каждый кубик на одну станцию или не используется: <b>Пушки</b> — одинаковые: 2→1, 3→3, 4→5, 5→8 урона (Шмаляние); <b>Таран</b> — стрит: 3→2, 4→4, 5→6 (Кальций); <b>Руль</b> — сумма ≥ S: ответный залп мимо (Мозжечок); <b>Трюм</b> — каждый кубик 1–2: Корпус +1 (Мормышка).</li><li><b>Бонус навыка.</b> Навык станции у ходящего ≥3 и станция сработала: +1 к эффекту.</li><li><b>Враг стреляет после каждого хода:</b> если Руль не сработал, Корпус −U.</li><li><b>Слава +1</b> ходящему, нанёсшему 3 урона и больше.</li></ol><p><b>Исход.</b> Корпус врага 0 — победа (полная награда). Корпус корабля 0 — поражение. После круга оба на плаву — ничья: враг отступает, награда половинная. Награда зависит от врага: слабый — Сокровища +3 (ничья +1), обычный — +4 (+2), сильный — +6 (+3) каждому скелету.</p>')
    h.append('</body></html>')
    return ''.join(h)


from chars_data import CHARS as _CH, CELLS as _CELLS, star_cells as _SC, KEYS as _KEYS
ARCH = [(c['name'], c['cap'], {k: _SC(c['cap'][k]) for k in _KEYS}) for c in _CH] + [('(пустой)', dict.fromkeys(_KEYS, 6), {})]


def boxes(n, filled=0, star=None, xs=()):
    out = []
    for i in range(1, n + 1):
        cls = 'f' if i <= filled else ''
        out.append('<span class="box %s">%s</span>' % (cls, '✦' if star == i else ''))
    return ''.join(out)


def player_sheet(name, start, stars):
    h = ['<div class="sheet"><div class="hd" style="font-family:Georgia;font-size:13pt;font-weight:bold">Лист скелета — %s</div>' % name]
    h.append('<div class="row"><b>Имя:</b> ______________________  <b style="margin-left:6mm;width:auto">Кубик (цвет):</b> ________</div>')
    for k, nm in SKILLS.items():
        star = stars.get(k)
        cells = ''
        for i in range(1, _CELLS + 1):
            blocked = i > start.get(k, 0)
            cells += '<span class="box" style="%s">%s</span>' % ('' if blocked else '', '✕' if blocked else ('✦' if (star and i in star) else ''))
        h.append('<div class="row"><b>%s</b>%s</div>' % (sk_img(k, 4.2) + ' ' + nm, cells))
    h.append('<div class="row"><b>Слава</b>%s</div>' % ''.join('<span class="box">%d</span>' % i for i in range(10)))
    h.append('<div class="row"><b>Удача (max 3)</b>%s</div>' % ''.join('<span class="box">%d</span>' % i for i in range(4)))
    h.append('<div class="row"><b>Сокровища</b>%s</div>' % ''.join('<span class="box">%d</span>' % i for i in range(0)) + ' ________ (без предела)')
    h.append('<div class="row"><b>Искры (max 5)</b>%s</div>' % ''.join('<span class="box">%d</span>' % i for i in range(6)))
    h.append('<small>Старта нет: закрашивайте клетки при прокачке. ✕ — потолок скелета (клетка недоступна). ✦ — клетка с Искрой при получении навыка. Отмечайте значение карандашом (обводите/зачёркивайте число).</small></div>')
    return ''.join(h)


def ship_log():
    h = ['<div class="sheet"><div class="hd" style="font-family:Georgia;font-size:13pt;font-weight:bold">Корабельный журнал</div>']
    h.append('<div class="row"><b>Корабль:</b> ______________________ <b style="margin-left:6mm;width:auto">Рейс №</b> ____ <b style="margin-left:6mm;width:auto">Раунд:</b> ____</div>')
    for key in ('H', 'C', 'R', 'M'):
        sh = SHIP[key]
        cells = ''
        for v in range(0, 11):
            if key == 'D' and v > 6:
                continue
            cls = ''
            lab = str(v)
            if (sh['lo'] is not None and sh['lose_lo'] and v <= sh['lo']) or (sh['hi'] is not None and sh['lose_hi'] and v >= sh['hi']):
                cls = 'x'
            if v == sh['start']:
                cls += ' f'
            cells += '<span class="box %s">%s</span>' % (cls, lab)
        h.append('<div class="row"><b>%s</b>%s</div>' % (sk_img(key, 4.0) + ' ' + sh['name'], cells))
    h.append('<small>Штриховка — поражение. Чёрная — старт. Отмечайте текущее значение карандашом. Ром 0 — не поражение, но в конце каждого раунда Ропот +1; Ропот ≥ Команды — бунт (поражение); Ром 10 — потолок. Жажда: Команда 1–3 → 1, 4–7 → 2, 8–10 → 3.</small>')
    h.append('<h3>Рейс</h3><div>Координаты старта: ____ Порт назначения: ____ · Пройдено клеток: ____</div>')
    h.append('<h3>Журнал островов</h3><table><tr><th>№</th><th>Клетка</th><th>Что это (порт 1/2/3 или необитаемый I1/I2)</th><th>Заметки</th></tr>' + ''.join('<tr><td>%d</td><td></td><td></td><td></td></tr>' % i for i in range(1, 7)) + '</table>')
    h.append('<h3>Заметки</h3><div style="height:40mm;border:1px dashed #888"></div></div>')
    return ''.join(h)


def sheets():
    h = ['<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Листы игры — прототип</title><style>%s</style></head><body>' % CSS]
    h.append('<h1>Листы игры</h1><p>Бумажная замена приложения: корабельный журнал и листы скелетов. Печатайте на A4, обводите значения карандашом.</p>')
    h.append(ship_log())
    h.append('<div class="pb"></div>')
    for i, (nm, st, stars) in enumerate(ARCH):
        h.append(player_sheet(nm, st, stars))
        if i % 3 == 2:
            h.append('<div class="pb"></div>')
    h.append('</body></html>')
    return ''.join(h)


def testsheet():
    h = ['<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Лист теста</title><style>%s</style></head><body>' % CSS]
    h.append('<h1>Лист теста</h1><div class="row"><b>Дата:</b> ________ <b style="margin-left:6mm;width:auto">Игроков:</b> ____ <b style="margin-left:6mm;width:auto">Скелетов:</b> ____ <b style="margin-left:6mm;width:auto">Режим:</b> Обучение / Плавание</div>')
    h.append('<h2>Журнал раундов</h2><table><tr><th>№</th><th>Клетка</th><th>Эпизод</th><th>Выбор игроков (слоты)</th><th>Корпус</th><th>Команда</th><th>Ром</th><th>Ропот</th><th>Опасн.</th><th>Заметки</th></tr>')
    for i in range(1, 17):
        h.append('<tr style="height:9mm"><td>%d</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>' % i)
    h.append('</table><h2 class="pb">Итог</h2><div class="row"><b>Результат:</b> победа / поражение &nbsp; <b style="width:auto">Причина:</b> ______________________ &nbsp; <b style="width:auto">Раундов:</b> ____ &nbsp; <b style="width:auto">Время:</b> ____ мин</div>')
    h.append('<h2>Оценки (1 — плохо, 5 — отлично)</h2><table><tr><th>Вопрос</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>Комментарий</th></tr>')
    qs = ['Понятны ли слоты (личные / общие / обязательные / заблокированные)?',
          'Интересно ли выбирать слоты по названию действия?',
          'Проверка d6 + навык: приятно ли, не давит ли навык кубик?',
          'Хватает ли места под кубики на Палубе (слоты 1–6) и в Порту?',
          'Читаем ли мелкий текст буклета?',
          'Карта: понятны ли ход, разведка, значки, рутина?',
          'Рыбалка и особый штиль: интересно ли?',
          'Магазин: хватает ли разнообразия, нормальные ли цены?',
          'Игорный дом (ставки, шуллерские штучки): интересно ли?',
          'Борт (бой на кубиках): интересно ли?',
          'Судовой журнал: понятна ли механика ключевых слов?',
          'Баланс шкал (Корпус, Команда, Ром, Ропот): хватает ли напряжения?',
          'Ощущается ли полукооперативность (Слава, Сокровища, Искры)?',
          'Длина раунда и партии нормальная?',
          'Обучение: достаточно ли понятно показывает все развороты?']
    for q in qs:
        h.append('<tr style="height:9mm"><td>%s</td>%s<td></td></tr>' % (q, '<td></td>' * 5))
    h.append('</table><h2>Что сломалось / непонятно / хочется поменять</h2><div style="height:70mm;border:1px dashed #888"></div></body></html>')
    return ''.join(h)


if __name__ == '__main__':
    with open(os.path.join(OUT, 'Лист_теста.html'), 'w', encoding='utf-8') as f:
        f.write(testsheet())
    with open(os.path.join(OUT, 'Книга_событий.html'), 'w', encoding='utf-8') as f:
        f.write(book())
    with open(os.path.join(OUT, 'Листы_игры.html'), 'w', encoding='utf-8') as f:
        f.write(sheets())
    print('ok')
