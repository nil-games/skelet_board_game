# -*- coding: utf-8 -*-
"""v0.9: Дух заменён на Ропот (как Недовольство в «Забытых морях»).
Ропот 0–10, старт 0, только растёт от плохого и падает от хорошего. Поражение «Бунт мертвецов»: Ропот ≥ Команды.
Внутренний ключ эффекта остаётся 'M', но знак инвертирован: прежний «Дух +1» = «Ропот −1».
Вызывается из content.py последним: mood.apply(globals())."""
import re

NAME = 'Ропот'
LOSE = 'Бунт мертвецов: Ропот догнал Команду'


def flip_text(s):
    """«Дух +2» → «Ропот −2», «Дух −1» → «Ропот +1»; остальные «Дух» → «Ропот»."""
    if not isinstance(s, str):
        return s
    s = re.sub(r'Дух ([+−-])\s?(\d+)', lambda m: '%s %s%s' % (NAME, '−' if m.group(1) == '+' else '+', m.group(2)), s)
    return s.replace('Дух', NAME)


def flip_eff(d):
    if isinstance(d, dict) and 'M' in d:
        d['M'] = -d['M']


def fix_action(a):
    for t in a.get('tiers') or []:
        flip_eff(t)
    flip_eff(a.get('cost'))
    for ch in a.get('choices') or []:
        flip_eff(ch[1])
    for k in ('title', 'note', 'alarm', 'excl'):
        if a.get(k):
            a[k] = flip_text(a[k])
    if a.get('choices'):
        a['choices'] = [(lab, eff, flip_text(txt)) for lab, eff, txt in a['choices']]


def apply(ns):
    seen = set()
    for ev in ns['EVENTS'] + ns['PORTS'] + [ns['ROUTINE']]:
        for k in ('warn', 'end', 'flavor'):
            if ev.get(k):
                ev[k] = flip_text(ev[k])
        for a in ev['cells'].values():
            if id(a) in seen:       # общие объекты (Рыбалка, Поминки) — один раз
                continue
            seen.add(id(a))
            fix_action(a)
    for ev in ns['EVENTS']:
        if ev.get('warn'):
            ev['warn'] = ev['warn'].replace('Ропот растёт', 'Ропот стихает')
    for hz in ns['HAZARDS']:
        flip_eff(hz['eff'])
    for i, (col, items) in enumerate(ns['SHOP']):
        ns['SHOP'][i] = (col, [(n, p, flip_text(e)) for n, p, e in items])
    ns['CURIOS'][:] = [(n, flip_text(e)) for n, e in ns['CURIOS']]
    ns['EFFECT_NAMES']['M'] = NAME
    ns['SHIP']['M'] = dict(name=NAME, start=0, lo=None, hi=10, lose_lo=None, lose_hi=None, lose_vs_crew=LOSE)
