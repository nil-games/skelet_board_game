# -*- coding: utf-8 -*-
"""Экспорт контента игры для веб-приложения: app/public/game_data.json + иконки.

Единый источник правды — content.py (тот же, что собирает буклет и Книгу событий).
Перед записью данные проверяются: при ошибке файл НЕ перезаписывается, скрипт печатает список проблем и
выходит с кодом 1. Текстовые штрафы («Ром −2», «Если никто не выбрал слот 1: Корпус −2. …») разбираются
в структуру; если фразу разобрать не удалось, это тоже ошибка — значит, нужно дописать правило разбора.

Запуск: python export_app.py
"""
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import content as C  # noqa: E402
from icons import ICONS  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
APP_PUBLIC = os.path.join(ROOT, 'app', 'public')
OUT = os.path.join(APP_PUBLIC, 'game_data.json')
ICON_SRC = os.path.join(ROOT, 'Ресурсы для игры', 'Картинки')
ICON_DST = os.path.join(APP_PUBLIC, 'icons')
ART_SRC = os.path.join(ROOT, 'Ресурсы для игры', 'Картинки', 'Картинки ивентов')
ART_DST = os.path.join(APP_PUBLIC, 'art')
ART_WIDTH = 768          # ширина для телефона; исходники 1024×1536 весят по 3 МБ

errors = []


def err(where, msg):
    errors.append('%s: %s' % (where, msg))


# ------------------------------------------------------------------ эффекты
SHIP_KEYS = {'H', 'C', 'R', 'M', 'D'}
PERSONAL_KEYS = {'F', 'L', 'T', 'S', 'BL', 'CU'}
SPECIAL_KEYS = {'mv', 'sc', 'catch', 'pick', 'RT'}
KNOWN_KEYS = SHIP_KEYS | PERSONAL_KEYS | SPECIAL_KEYS
NAME_TO_KEY = {v: k for k, v in C.EFFECT_NAMES.items()}
NAME_TO_KEY.update({'Искры': 'S', 'Искру': 'S'})


def check_eff(where, eff):
    if not isinstance(eff, dict):
        err(where, 'эффект не словарь: %r' % (eff,))
        return {}
    for k, v in eff.items():
        if k not in KNOWN_KEYS:
            err(where, 'неизвестный ключ эффекта %r' % k)
        if not isinstance(v, int):
            err(where, 'значение эффекта %s не целое: %r' % (k, v))
    return dict(eff)


EFF_RX = re.compile(r'^\s*([А-ЯЁа-яё]+)\s*([+−-])\s*(\d+)\s*$')


def parse_eff_text(where, text):
    """«Ром −2, Корпус −1» → {'R': -2, 'H': -1}."""
    out = {}
    for part in re.split(r',\s*|\s+и\s+', text.strip().rstrip('.')):
        if not part.strip():
            continue
        m = EFF_RX.match(part)
        if not m or m.group(1) not in NAME_TO_KEY:
            err(where, 'не разобрать эффект %r' % part)
            continue
        sign = 1 if m.group(2) == '+' else -1
        out[NAME_TO_KEY[m.group(1)]] = sign * int(m.group(3))
    return out


def parse_end(where, text, ev):
    """Разбор «В конце раунда»: штраф без штурвала, условия по Команде, постоянный эффект.
    Цена нового круга берётся из ev['circle'] (а текст сверяется с ней)."""
    res = {'noHelm': None, 'always': None, 'crewBelow': [], 'circle': None}
    if not text:
        return res
    rest = text
    m = re.search(r'Если никто не выбрал слот 1:\s*([^.(]+?)\s*(\([^)]*\))?\.\s*', rest)
    if m:
        res['noHelm'] = {'eff': parse_eff_text(where, m.group(1)), 'note': (m.group(2) or '').strip('() ') or None}
        rest = rest.replace(m.group(0), '', 1)
    m = re.search(r'Если корабль не покинул клетку:\s*(.+?),?\s*и следующий раунд читайте этот же эпизод \(новый круг\)\.\s*', rest)
    if m:
        res['circle'] = parse_eff_text(where, m.group(1))
        if ev.get('circle') is not None and res['circle'] != ev['circle']:
            err(where, 'цена круга в тексте %r не совпадает с circle %r' % (res['circle'], ev['circle']))
        rest = rest.replace(m.group(0), '', 1)
    for m in list(re.finditer(r'Если Команда < (\d+):\s*([^.(]+?)\s*(\([^)]*\))?\.\s*', rest)):
        res['crewBelow'].append({'n': int(m.group(1)), 'eff': parse_eff_text(where, m.group(2)), 'note': (m.group(3) or '').strip('() ') or None})
        rest = rest.replace(m.group(0), '', 1)
    m = re.search(r'^\s*([^.]+?)\s+дополнительно\.\s*', rest)
    if m:
        res['always'] = parse_eff_text(where, m.group(1))
        rest = rest.replace(m.group(0), '', 1)
    if rest.strip():
        err(where, 'не разобран текст конца раунда: %r' % rest.strip())
    return res


# ------------------------------------------------------------------ слоты
TIER_LABELS = {1: [None], 3: ['≤3', '4–6', '7+'], 4: ['≤3', '4–6', '7–9', '10+']}
SHARED_SEA = {4, 5, 6, 7}      # Палуба: 1–3 личные (круг), 4–7 общие (пунктир)
SHARED_PORT = {4, 5, 6}        # Порт: 1–3 личные, 4 общий, 5 Магазин, 6 Игорный дом
EXCL_RX = re.compile(r'Если исход (≤3|4–6|7\+|7–9|10\+):\s*(.+)')


def export_slot(where, n, cell, shared_set):
    tiers = cell.get('tiers') or []
    choices = cell.get('choices')
    texts = cell.get('texts') or []
    s = {
        'n': n,
        'title': cell['title'],
        'skill': cell.get('skill'),
        'shared': n in shared_set and not cell.get('mandatory'),
        'mandatory': bool(cell.get('mandatory')),
        'req': cell.get('req'),
        'crewReq': cell.get('crew_req'),
        'cost': check_eff(where + ' cost', cell['cost']) if cell.get('cost') else None,
        'note': cell.get('note'),
        'alarm': None,
        'excl': None,
        'outcomes': [],
        'choices': None,
    }
    if not cell.get('title'):
        err(where, 'нет названия')
    if s['skill'] and s['skill'] not in C.SKILLS:
        err(where, 'неизвестный навык %r' % s['skill'])
    if choices:
        s['choices'] = []
        for i, ch in enumerate(choices):
            lab, eff, txt = ch
            if not lab or not txt:
                err(where, 'выбор %d без названия или текста' % i)
            s['choices'].append({'label': lab, 'eff': check_eff('%s выбор %d' % (where, i), eff), 'text': txt})
    else:
        if len(tiers) not in TIER_LABELS:
            err(where, 'число исходов %d (нужно 1, 3 или 4)' % len(tiers))
        if len(texts) != len(tiers):
            err(where, 'исходов %d, а текстов %d' % (len(tiers), len(texts)))
        if s['skill'] is None and len(tiers) != 1:
            err(where, 'действие без проверки должно иметь 1 исход')
        if s['skill'] is not None and len(tiers) == 1:
            err(where, 'проверка навыка с единственным исходом')
        labels = TIER_LABELS.get(len(tiers), [None] * len(tiers))
        for i, t in enumerate(tiers):
            txt = texts[i] if i < len(texts) else ''
            if not txt:
                err(where, 'пустой текст исхода %d' % i)
            s['outcomes'].append({'label': labels[i], 'eff': check_eff('%s исход %d' % (where, i), t), 'text': txt})
    if cell.get('alarm'):
        s['alarm'] = {'text': cell['alarm'], 'eff': parse_eff_text(where + ' alarm', cell['alarm'])}
    if cell.get('excl'):
        m = EXCL_RX.match(cell['excl'])
        labels = [o['label'] for o in s['outcomes']]
        if not m or m.group(1) not in labels:
            err(where, 'не разобран excl %r' % cell['excl'])
        else:
            s['excl'] = {'fromOutcome': labels.index(m.group(1)), 'text': m.group(2)}
    return s


def export_event(e, kind):
    where = e['id']
    shared = SHARED_PORT if kind == 'port' else SHARED_SEA
    for f in ('title', 'flavor'):
        if not e.get(f):
            err(where, 'пустое поле %s' % f)
    slots = [export_slot('%s/слот %s' % (where, n), int(n), cell, shared) for n, cell in sorted(e['cells'].items(), key=lambda x: int(x[0]))]
    mand = [s['n'] for s in slots if s['mandatory']]
    if any(n not in (1, 2) for n in mand):
        err(where, 'обязательный слот не на 1–2: %r' % mand)
    out = {
        'id': e['id'], 'kind': kind, 'hint': e.get('hint'), 'title': e['title'], 'flavor': e['flavor'],
        'warn': e.get('warn') if e.get('warn') not in (None, '—') else None,
        'flow': e.get('flow') or ('port' if kind == 'port' else 'auto'),
        'slots': slots,
        'endText': e.get('end'),
        'end': parse_end(where + '/конец', e.get('end'), e),
    }
    if out['flow'] == 'loop':
        out['circle'] = e.get('circle') or out['end']['circle']
        if not out['circle']:
            err(where, 'цикл без цены нового круга')
        if 1 not in [s['n'] for s in slots]:
            err(where, 'цикл без слота 1 «Штурвал»')
    if kind == 'port':
        out.update({'shop': bool(e.get('shop')), 'casino': bool(e.get('casino')), 'fish': e.get('fish')})
    return out


# ------------------------------------------------------------------ сборка
def build():
    events = {}
    for e in C.EVENTS:
        events[e['id']] = export_event(e, 'sea')
    ports = {}
    for p in C.PORTS:
        ports[p['id']] = export_event(p, 'port')
    battles = {}
    for b in C.BATTLES:
        if b['cls'] not in C.ENEMY_DAMAGE:
            err(b['id'], 'неизвестный класс врага %r' % b['cls'])
        battles[b['id']] = {'id': b['id'], 'title': b['title'], 'cls': b['cls'], 'special': b.get('special'),
                            'flavor': b['flavor'], 'warn': b.get('warn'), 'hullBonus': b.get('hull_bonus', 0)}

    pools = {k: list(v) for k, v in C.POOLS.items()}
    for k, ids in pools.items():
        for i in ids:
            if i not in events and i not in battles:
                err('POOLS/' + k, 'нет события %s' % i)
    port_table = [pid for _, _, pid in sorted(C.PORT_TABLE)]
    for pid in port_table:
        if pid not in ports:
            err('PORT_TABLE', 'нет порта %s' % pid)
    used = set(i for v in pools.values() for i in v) | set(port_table)
    for i in list(events) + list(ports) + list(battles):
        if i not in used:
            err(i, 'событие не входит ни в один пул')

    terrains = [{'d6': a, 'key': k, 'sym': sym, 'name': nm} for a, _, k, sym, nm in C.HINT_TABLE]

    shop = []
    for col, items in C.SHOP:
        shop.append({'col': col, 'items': [{'name': n, 'price': p, 'text': t} for n, p, t in items]})

    data = {
        'ship': {k: v for k, v in C.SHIP.items()},
        'thirst': [{'crewFrom': a, 'crewTo': b, 'rum': r} for a, b, r in C.THIRST],
        'press': C.PRESS_CFG,
        'skills': C.SKILLS,
        'effectNames': dict(C.EFFECT_NAMES, S='Искры', mv='Ход', sc='Разведка', catch='Улов', pick='Обломки', RT='Раздача рома'),
        'terrains': terrains,
        'pools': pools,
        'islandPortChance': 4,          # d6 1–4: порт, 5–6: необитаемый
        'portTable': port_table,
        'events': events,
        'ports': ports,
        'battles': battles,
        'enemyByN': {k: {'hull': v[0], 'helm': v[1]} for k, v in C.ENEMY_BY_N.items()},
        'enemyDamage': {k: {'dmg': v[0], 'helmPlus': v[1]} for k, v in C.ENEMY_DAMAGE.items()},
        'battleReward': C.BATTLE_REWARD,
        'shop': shop,
        'catch': [{'key': k, 'name': nm, 'fish': [{'name': f, 'price': p} for f, p in fs]} for k, nm, fs in C.CATCH],
        'curios': {n: {'price': v[0], 'sparks': v[1], 'text': v[2]} for n, v in C.CURIO_INFO.items()},
        'casinoUpgrades': [{'name': n, 'price': p, 'text': t} for n, p, t in C.CASINO_UPGRADES],
        'bets': [{'ratio': r, 'name': n, 'short': s, 'text': f} for r, n, s, f in C.BETS],
        'betRules': C.BET_RULES,
        'casinoRule': C.CASINO_RULE,
        'fishSlot': export_slot('FISH', 7, C.FISH, SHARED_SEA),
        'flashbackEvery': 3,
    }
    # особые проверки
    if set(data['ship']) - {'H', 'C', 'R', 'M', 'D'}:
        err('SHIP', 'неизвестные шкалы')
    for t in terrains:
        if t['key'] != 'i' and t['key'] not in pools and t['key'] != 'sp':
            err('terrains', 'нет пула для значка %s' % t['key'])
    return data


def copy_icons():
    os.makedirs(ICON_DST, exist_ok=True)
    for key, (folder, name) in ICONS.items():
        src = os.path.join(ICON_SRC, folder, name + '.png')
        if not os.path.exists(src):
            err('icons', 'нет файла %s' % src)
            continue
        shutil.copyfile(src, os.path.join(ICON_DST, key + '.png'))


def export_art(data):
    """Картинки ивентов: файл «<ID> <название>.png» → art/<ID>.webp, поле image у события/порта/боя.
    Файлы без ID в начале имени пропускаются (печатается предупреждение), картинка не обязательна."""
    os.makedirs(ART_DST, exist_ok=True)
    targets = {}
    for group in ('events', 'ports', 'battles'):
        for i, e in data[group].items():
            targets[i] = e
            e['image'] = None
    warnings = []
    # уже сконвертированные картинки (в репозитории лежат только они; исходники PNG тяжёлые)
    for eid, e in targets.items():
        if os.path.exists(os.path.join(ART_DST, eid + '.webp')):
            e['image'] = 'art/%s.webp' % eid
    if not os.path.isdir(ART_SRC):
        return warnings
    for fn in sorted(os.listdir(ART_SRC)):
        if not fn.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            continue
        m = re.match(r'^([A-Z]+\d+)(?![0-9A-Za-z])', fn)
        if not m or m.group(1) not in targets:
            warnings.append('картинка без известного ID в начале имени, пропущена: %s' % fn)
            continue
        eid = m.group(1)
        src = os.path.join(ART_SRC, fn)
        dst = os.path.join(ART_DST, eid + '.webp')
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
            from PIL import Image
            im = Image.open(src).convert('RGB')
            if im.width > ART_WIDTH:
                im = im.resize((ART_WIDTH, round(im.height * ART_WIDTH / im.width)), Image.LANCZOS)
            im.save(dst, 'WEBP', quality=80, method=6)
        targets[eid]['image'] = 'art/%s.webp' % eid
    return warnings


def main():
    data = build()
    if errors:
        print('ЭКСПОРТ ОТМЕНЁН, ошибок: %d' % len(errors))
        for e in errors:
            print('  -', e)
        sys.exit(1)
    warnings = export_art(data)
    body = json.dumps(data, ensure_ascii=False, sort_keys=True)
    data['version'] = hashlib.sha1(body.encode('utf-8')).hexdigest()[:10]
    os.makedirs(APP_PUBLIC, exist_ok=True)
    copy_icons()
    if errors:
        print('ЭКСПОРТ ОТМЕНЁН:', *errors, sep='\n  - ')
        sys.exit(1)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    for w in warnings:
        print('  ! ' + w)
    print('картинок: %d' % sum(1 for g in ('events', 'ports', 'battles') for e in data[g].values() if e['image']))
    print('ok: %s (версия %s) событий %d, портов %d, боёв %d' % (OUT, data['version'], len(data['events']), len(data['ports']), len(data['battles'])))


if __name__ == '__main__':
    main()
