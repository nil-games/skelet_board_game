# -*- coding: utf-8 -*-
"""Грубая симуляция баланса свободного плавания: сколько раундов живёт корабль.
Игроки жадные: каждый выбирает ячейку с лучшей оценкой пользы для текущих шкал."""
import random, statistics, sys
sys.path.insert(0, '.')
from content import *

import os
NOISE = float(os.environ.get('NOISE', '0'))
GOAL = int(sys.argv[1]) if len(sys.argv) > 1 else 8
W = {'H': 1.0, 'C': 1.6, 'R': 0.8, 'M': 0.8, 'D': -1.1, 'F': 0.3, 'L': 0.3, 'T': 0.4, 'S': 0.7, 'mv': 0.9, 'sc': 0.15}


def tier_index(total, n):
    if n == 1:
        return 0
    if n == 3:
        return 0 if total <= 3 else 1 if total <= 6 else 2
    return 0 if total <= 3 else 1 if total <= 6 else 2 if total <= 9 else 3


def need_weight(st, k):
    # чем ближе шкала к краю гибели, тем ценнее
    sh = SHIP[k]
    v = st[k]
    w = 1.0
    if sh['lo'] is not None and v <= sh['lo'] + 3:
        w += (sh['lo'] + 4 - v) * 0.5
    if sh['hi'] is not None and k != 'D' and v >= sh['hi'] - 3:
        w -= 0.0
        w = -w if True else w
    return w


def score(st, eff):
    s = 0
    for k, v in eff.items():
        if k == 'catch':
            s += 1.2 * v
            continue
        if k == 'RT':
            s += score(st, {'R': -min(st['R'], thirst(st['C']) + v)})
            continue
        if k in ('BL', 'CU'):
            continue
        if k == 'pick':
            s += v * max(score(st, {'R': 1}), score(st, {'H': 1}), score(st, {'T': 1}))
            continue
        if k in ('mv', 'sc', 'F', 'L', 'T', 'S'):
            s += W[k] * v
        elif k == 'D':
            s += W['D'] * v * (1 + st['D'] * 0.4)
        elif k == 'M':
            gap = st['C'] - st['M']
            urg = 1 + max(0, 4 - gap) * 0.6
            s += -W['M'] * v * urg
        else:
            sh = SHIP[k]
            if k == 'C':
                gap = st['C'] - st['M']
                s += W['C'] * v * (1 + max(0, 4 - gap) * 0.6)
                continue
            dist = min(st[k] - sh['lo'], (sh['hi'] - st[k]) if sh['hi'] is not None and k == 'M' else 99)
            urgency = 1 + max(0, 4 - dist) * 0.6
            # для шкал с двумя краями: перегрузка вверх вредит
            if k == 'M' and st[k] + v >= sh['hi'] - 1 and v > 0:
                urgency = -1
            if k == 'R' and st[k] >= sh['hi'] and v > 0:
                urgency = 0
            if k == 'M' and st[k] >= sh['hi'] - 3 and v < 0:
                urgency = 1.5
            s += W[k] * v * urgency
    return s


def exp_eff(a, skill, st):
    tiers = a['tiers']
    n = len(tiers)
    tot = 0
    for d in range(1, 7):
        t = tiers[tier_index(d + skill, n)]
        tot += score(st, t)
    return tot / 6 + (score(st, a['cost']) if a['cost'] else 0)


def apply(st, eff):
    for k, v in eff.items():
        if k == 'catch':
            st['T'] = st.get('T', 0) + 2 * v
            continue
        if k == 'RT':
            st['R'] = max(0, st['R'] - thirst(st['C']) - v)
            continue
        if k in ('BL', 'CU'):
            continue
        if k == 'pick':
            for _ in range(v):
                k2 = 'R' if st['R'] <= 5 else ('H' if st['H'] <= 5 else 'T')
                st[k2] = st.get(k2, 0) + 1
            continue
        if k in ('mv', 'sc'):
            st[k] = st.get(k, 0) + v
        elif k in st:
            st[k] += v


def check(st):
    for k, sh in SHIP.items():
        if sh['lo'] is not None and sh['lose_lo'] and st[k] <= sh['lo'] and k != 'D':
            return sh['lose_lo']
        if sh['hi'] is not None and sh['lose_hi'] and st[k] >= sh['hi']:
            return sh['lose_hi']
    if st['M'] >= st['C']:
        return SHIP['M']['lose_vs_crew']
    return None


import collections
stats = collections.Counter(); stats['choice'] = collections.Counter()


BYID = {e['id']: e for e in EVENTS}
TYPE_TABLE = {1: 's', 2: 's', 3: 'st', 4: 'sh', 5: 'f', 6: 'i'}


def pick_event(rng, st):
    """Тип местности d6 → d6 по пулу. Остров: 1–4 порт (раунд без событий), 5–6 необитаемый остров. Бой — упрощённо: Корпус −1, Сокровища +2."""
    kind = TYPE_TABLE[rng.randint(1, 6)]
    if kind == 'i':
        if rng.randint(1, 6) <= 4:
            return dict(id='PORT', hint='i', title='порт', flow='auto', cells={}, end=None, port=True)
        return BYID[POOLS['i_wild'][rng.randint(0, 5)]]
    eid = POOLS[kind][rng.randint(0, 5)]
    if eid.startswith('B'):
        return dict(id=eid, hint='sh', title='бой', flow='auto', cells={}, end=None, battle=True)
    return BYID[eid]


def run(players, rng, verbose=False, max_rounds=40, mode='sea'):
    players = [dict(p) for p in players]
    st = {k: v['start'] for k, v in SHIP.items()}
    pos = 0.0
    seen_hazard = set()
    cur = None
    handed = False
    stats['rounds'] += 0
    for rnd in range(1, max_rounds + 1):
        st['mv'] = 0
        if cur is None:
            handed = False
        ev = cur or pick_event(rng, st)
        taken = {}
        order = list(range(len(players)))
        rng.shuffle(order)
        for pi in (order if ev['cells'] else []):
            sk = players[pi]
            best, bc = None, -9e9
            for n, a in ev['cells'].items():
                if a.get('req'):
                    continue
                if a.get('crew_req') and st['C'] < a['crew_req']:
                    continue
                if n <= 3 and n in taken and a['skill'] is not None:
                    continue
                if a['title'] == 'Раздача рома' and (handed or n in taken):
                    continue
                if a.get('choices'):
                    base = max(score(st, e) for _, e, _ in a['choices'])
                else:
                    base = None
                sc = (base if base is not None else exp_eff(a, (min(sk['_cap'].get(a['skill'], 0), sk.get(a['skill'], 0) + 1) + sk['_gear'].get(a['skill'], 0)) if a['skill'] else 0, st)) + (6 if a['mandatory'] and n not in taken else 0) + (2.5 if a.get('alarm') and n not in taken else 0) + (2.0 if ev.get('flow') == 'loop' and n == 1 and 1 not in taken else 0)
                sc += rng.gauss(0, NOISE)   # игроки не видят исходов: шум оценки
                if sc > bc:
                    best, bc = n, sc
            taken.setdefault(best, []).append(pi)
        for n in sorted(taken):
            a = ev['cells'][n]
            for pi in taken[n]:
                sk = players[pi]
                d = rng.randint(1, 6)
                if a['skill']:
                    sk[a['skill']] = min(sk['_cap'].get(a['skill'], 0), sk.get(a['skill'], 0) + 1)
                lvl = (sk.get(a['skill'], 0) + sk['_gear'].get(a['skill'], 0)) if a['skill'] else 0
                if a['cost']:
                    apply(st, a['cost'])
                if a.get('choices'):
                    eff = max((e for _, e, _ in a['choices']), key=lambda e: score(st, e))
                    stats['choice'][[c[0] for c in a['choices'] if c[1] is eff][0]] += 1
                    handed = True
                else:
                    eff = a['tiers'][tier_index(d + lvl, len(a['tiers']))]
                r0 = st['R']
                apply(st, eff)
                if st['R'] > r0:
                    stats['rum_gain'] += st['R'] - r0
                elif st['R'] < r0:
                    stats['rum_loss'] += r0 - st['R']
        if ev.get('battle'):
            st['H'] -= 1
            st['T'] = st.get('T', 0) + 2
        # концовка раунда эпизода
        if ev['id'] in ('ST1', 'ST2') and 1 not in taken:
            st['H'] -= 2
        if ev['id'] == 'F1' and 1 not in taken:
            st['R'] -= 1
        if ev['id'] == 'SH2':
            st['D'] += 1
        if ev['id'] == 'F2':
            st['R'] -= 1
        for n, a in ev['cells'].items():
            if a.get('alarm') and n not in taken:
                k = {'Ром': 'R', 'Ропот': 'M', 'Корпус': 'H'}[a['alarm'].split()[0]]
                sign, num = a['alarm'].split()[1][0], int(a['alarm'].split()[1][1:])
                st[k] += num if sign == '+' else -num
        st['R'] = max(0, min(10, st['R']))
        st['M'] = max(0, min(10, st['M']))
        if st['R'] == 0:
            st['M'] += 1   # трезвая тоска: Ропот +1
            stats['rum0'] += 1
        stats['rounds'] += 1
        for hz in HAZARDS:
            if st['D'] >= hz['at'] and hz['id'] not in seen_hazard:
                seen_hazard.add(hz['id'])
                apply(st, hz['eff'])
        for k, sh in SHIP.items():
            if sh['hi'] is not None:
                st[k] = min(st[k], sh['hi']) if k in ('H', 'C') else st[k]
        r = check(st)
        if r:
            return rnd, r, pos
        if ev.get('flow') == 'loop':
            if st['mv'] > 0:
                pos += st['mv']
                cur = None
            else:
                cur = ev
                apply(st, ev.get('circle') or {})   # цена нового круга
                r = check(st)
                if r:
                    return rnd, r, pos
        else:
            pos += 1
            cur = None
        st['mv'] = 0
        if pos >= GOAL:
            return rnd, 'ДОШЛИ', pos
    stats['stuck_' + (cur or {'id': '-'})['id']] += 1
    return max_rounds, 'ВЫЖИЛИ', pos


import os
CAPS = [  # nose bone grab eye scare helm
    (2, 6, 3, 3, 4, 2), (4, 2, 3, 2, 3, 6), (3, 3, 2, 2, 6, 4),
    (3, 3, 2, 6, 2, 4), (4, 3, 6, 2, 2, 3), (3, 3, 5, 2, 4, 3)]
KEYS = ['nose', 'bone', 'grab', 'eye', 'scare', 'helm']


def players_for(n, gear=False):
    out = []
    for c in CAPS[:n]:
        cap = dict(zip(KEYS, c))
        main = max(cap, key=cap.get)
        out.append({'_cap': cap, '_gear': {main: 2} if gear else {}})
    return out


if __name__ == '__main__':
    rng = random.Random(7)
    GEAR = os.environ.get('GEAR', '0') == '1'
    print('снаряжение +2 на главный навык:', GEAR)
    for n in (4, 5, 6):
        res = [run(players_for(n, GEAR), rng) for _ in range(4000)]
        rounds = [r[0] for r in res]
        causes = {}
        for r in res:
            causes[r[1]] = causes.get(r[1], 0) + 1
        print('  Ром: получено %.1f, потрачено %.1f за партию; раундов на нуле %.1f%%; раздачи %s' % (stats['rum_gain'] / len(res), stats['rum_loss'] / len(res), 100 * stats['rum0'] / max(1, stats['rounds']), dict(stats['choice'])))
        for _k in ('rum_gain', 'rum_loss', 'rum0', 'rounds'):
            stats[_k] = 0
        stats['choice'] = collections.Counter()
        print('игроков', n, 'раундов ср.', round(statistics.mean(rounds), 1), 'мед.', statistics.median(rounds))
        for c, v in sorted(causes.items(), key=lambda x: -x[1]):
            print('   %-45s %5.1f%%' % (c, 100 * v / len(res)))
