# -*- coding: utf-8 -*-
"""v0.17: Опасность — сценарная шкала. В Обучении и свободном плавании её нет.
Из событий, портов, магазина и журнала Опасность убрана; данные об опасных событиях (X1, X2, X3) сохранены в HAZARDS_SCENARIO
для сценариев с погоней. Вызывается из content.py последним: nodanger.apply(globals())."""
import re


def _strip_d(t):
    if not isinstance(t, dict) or 'D' not in t:
        return t
    if set(t.keys()) == {'D'}:                       # единственный эффект был Опасность: заменяем на Ропот того же знака
        return {'M': t['D']}
    return {k: v for k, v in t.items() if k != 'D'}


def _clean_end(s):
    if not s:
        return s
    s = re.sub(r'Опасность [+−]\d+\.\s*', '', s).strip()
    return s or None


def apply(ns):
    for ev in ns['EVENTS'] + ns['PORTS']:
        for a in ev['cells'].values():
            a['tiers'] = [_strip_d(t) for t in a['tiers']]
            if a.get('cost'):
                a['cost'] = _strip_d(a['cost'])
            if a.get('choices'):
                a['choices'] = [(lab, _strip_d(eff), txt) for lab, eff, txt in a['choices']]
        ev['end'] = _clean_end(ev.get('end'))
        if ev.get('warn'):
            ev['warn'] = (ev['warn'].replace('Опасность растёт, пока он рядом.', 'Он не отстанет, пока вы рядом.')
                          .replace('Каждый раунд в порту — громкий. Опасность растёт.', 'Здесь всегда людно и шумно.')
                          .replace('Тут шумно по-своему: Опасность растёт быстрее. Магазина нет.', 'Тут шумно по-своему. Магазина нет.'))
    # Рыночный порт, слот 2: «Высматривать погоню» → новости (разведка)
    p1 = ns['PORTS'][0]['cells'][2]
    p1.update(title='Выведывать новости в порту', skill='nose', tiers=[{}, {'sc': 1}, {'sc': 2}],
              texts=['Новости оказались сплетнями про вас.', 'Узнали, что творится в округе.', 'Узнали всё, что творится вокруг: видно далеко.'])
    # магазин: услуги без Опасности
    svc = []
    for nm, pr, ef in ns['SHOP'][4][1]:
        if nm == 'Адвокат':
            nm, pr, ef = 'Парикмахер', 1, 'Слава +2.'
        elif nm == 'Вышибала':
            nm, pr, ef = 'Вербовщик', 3, 'Команда +2.'
        svc.append((nm, pr, ef))
    ns['SHOP'][4] = (ns['SHOP'][4][0], svc)
    # опасные события — только для сценариев
    ns['HAZARDS_SCENARIO'] = [dict(h) for h in ns['HAZARDS']]
    ns['HAZARDS'][:] = []
    ns['SHIP']['D']['scenario_only'] = True
