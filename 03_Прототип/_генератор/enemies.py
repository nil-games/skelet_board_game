# -*- coding: utf-8 -*-
"""Бой v0.21: карта врага с отсеками (по мотивам «Спящих богов»).
Ход скелета: бросок 5d6, 1 переброс (+Ром −1 за ещё один, +Удача), затем кубики кладутся на отсеки врага (нужная комбинация),
оставшиеся — на свои станции: Руль (сумма ≥ S: залп мимо) и Трюм (два кубика 1–2: Корпус +1).
Отсек разбит, когда на нём выложена его комбинация (прочность 2 — нужно разбить дважды, разными ходами можно).
Символы: heart (разбейте все — победа), gun (пока цел: урон врага +1), loot (разбит — добыча), armor (нельзя бить, пока цел отсек-щит).
Контратака после каждого хода: урон = база + число целых пушек (если Руль не сработал).
Круг: каждый скелет ходит один раз. Все сердца разбиты — победа; корабль 0 — поражение; иначе ничья (враг уходит, добыча — из разбитых трюмов)."""
import itertools, random, collections, sys
from functools import lru_cache

COMBO_TEXT = {
    'one6': 'одна шестёрка', 'pair': 'пара', 'three': 'три одинаковых', 'two_pairs': 'две пары', 'run3': 'стрит из 3',
    'run4': 'стрит из 4', 'sum15': 'сумма ≥ 15', 'sum18': 'сумма ≥ 18', 'sum20': 'сумма ≥ 20', 'pair5': 'пара 5 или 6',
}


def combo_ok(c, vals):
    """vals — кортеж кубиков, выложенных на отсек (ровно столько, сколько нужно комбинации)."""
    n = len(vals)
    cnt = collections.Counter(vals)
    if c == 'one6':
        return n == 1 and vals[0] == 6
    if c == 'pair':
        return n == 2 and len(cnt) == 1
    if c == 'pair5':
        return n == 2 and len(cnt) == 1 and vals[0] >= 5
    if c == 'three':
        return n == 3 and len(cnt) == 1
    if c == 'two_pairs':
        return n == 4 and sorted(cnt.values()) == [2, 2]
    if c in ('run3', 'run4'):
        k = 3 if c == 'run3' else 4
        s = sorted(vals)
        return n == k and all(s[i + 1] == s[i] + 1 for i in range(k - 1))
    if c.startswith('sum'):
        return n >= 1 and sum(vals) >= int(c[3:])
    return False


# Враги: зоны (имя, комбо, тип, прочность, добыча). Прочность может зависеть от числа скелетов: dur = {4: 1, 5: 1, 6: 2}
ENEMIES = [
    dict(id='B1', title='Чайка-налётчица', cls='слабый', base=0, S=9, zones=[
        ('Клюв', 'pair', 'gun', 1, None),
        ('Левое крыло', 'run3', 'heart', {4: 1, 5: 1, 6: 2}, None),
        ('Правое крыло', 'pair', 'heart', {4: 1, 5: 2, 6: 2}, None),
        ('Зоб', 'three', 'loot', 1, 'Сокровища +2 каждому'),
    ]),
    dict(id='B2', title='Налоговая галера', cls='обычный', base=1, S=10, zones=[
        ('Вёсла-скрепки', 'pair', 'gun', 1, None),
        ('Пушка', 'three', 'gun', 1, None),
        ('Канцелярия', 'run4', 'heart', {4: 1, 5: 1, 6: 2}, None),
        ('Инспектор', 'sum18', 'heart', {4: 1, 5: 2, 6: 2}, None),
        ('Касса', 'two_pairs', 'loot', 1, 'Сокровища +3 каждому'),
    ]),
    dict(id='B3', title='Королева Ржавчина', cls='сильный', base=1, S=11, zones=[
        ('Ржавые пушки', 'pair', 'gun', 2, None),
        ('Носовое орудие', 'three', 'gun', 1, None),
        ('Ржавый панцирь', 'two_pairs', 'shield', 1, None),
        ('Корона', 'pair5', 'heart_armor', {4: 1, 5: 2, 6: 2}, None),
        ('Котёл', 'run4', 'heart', {4: 1, 5: 1, 6: 2}, None),
        ('Сундук', 'sum20', 'loot', 1, 'Сокровища +5 каждому'),
    ]),
]


def dur(z, N):
    d = z[3]
    return d[N] if isinstance(d, dict) else d


def setup(enemy, N):
    return tuple(dur(z, N) for z in enemy['zones'])   # сколько ещё ударов нужно по каждой зоне


def is_dead(enemy, hp):
    return all(h <= 0 for z, h in zip(enemy['zones'], hp) if z[2] in ('heart', 'heart_armor'))


def damage(enemy, hp):
    return enemy['base'] + sum(1 for z, h in zip(enemy['zones'], hp) if z[2] == 'gun' and h > 0)


def available(enemy, hp, i):
    z = enemy['zones'][i]
    if hp[i] <= 0:
        return False
    if z[2] == 'heart_armor':
        return all(h <= 0 for zz, h in zip(enemy['zones'], hp) if zz[2] == 'shield')
    return True


W = {'heart': 5.0, 'heart_armor': 5.0, 'gun': 3.0, 'shield': 2.5, 'loot': 1.5}


@lru_cache(None)
def best_play(eid, N, hp, dice, S):
    """Лучшая раскладка: перебираем, на какие зоны положить кубики, остаток — Руль/Трюм. Возвращает (ценность, новый hp, увернулись, ремонт)."""
    enemy = next(e for e in ENEMIES if e['id'] == eid)
    idx = list(range(len(dice)))
    zones = enemy['zones']
    best = (-1, hp, False, 0)

    def finish(rem, hp2, val):
        nonlocal best
        rv = [dice[i] for i in rem]
        dmg = damage(enemy, hp2)
        # вариант: всё на Руль, если хватает; иначе кубики 1–2 в Трюм
        opts = []
        for k in range(len(rv) + 1):
            for sub in itertools.combinations(range(len(rv)), k):
                rul = [rv[j] for j in sub]
                rest = [rv[j] for j in range(len(rv)) if j not in sub]
                dodge = sum(rul) >= S if rul else False
                rep = 1 if sum(1 for v in rest if v <= 2) >= 2 else 0
                opts.append((dodge * dmg * 0.9 + rep * 0.6, dodge, rep))
        o = max(opts)
        tot = val + o[0]
        if tot > best[0]:
            best = (tot, hp2, o[1], o[2])

    def rec(zi, rem, hp2, val):
        if zi == len(zones):
            finish(rem, hp2, val)
            return
        rec(zi + 1, rem, hp2, val)
        if not available(enemy, hp2, zi):
            return
        c = zones[zi][1]
        for k in range(1, len(rem) + 1):
            for sub in itertools.combinations(rem, k):
                if combo_ok(c, tuple(dice[i] for i in sub)):
                    h3 = list(hp2)
                    h3[zi] -= 1
                    h3 = tuple(h3)
                    gain = W[zones[zi][2]] * (1.0 if h3[zi] <= 0 else 0.6)
                    # броня открывает сердце
                    rec(zi + 1, tuple(i for i in rem if i not in sub), h3, val + gain)
    rec(0, tuple(idx), hp, 0.0)
    return best


def sval(enemy, N):
    S = enemy['S']
    return S[N] if isinstance(S, dict) else S


def turn(rng, enemy, N, hp, extra_rerolls=0):
    S = sval(enemy, N)
    dice = [rng.randint(1, 6) for _ in range(5)]
    for _ in range(1 + extra_rerolls):
        cur = best_play(enemy['id'], N, hp, tuple(sorted(dice)), S)[0]
        best_set, bv = (), cur
        for mask in range(1, 32):
            sel = [i for i in range(5) if mask >> i & 1]
            tot = 0
            for _ in range(14):
                d2 = dice[:]
                for i in sel:
                    d2[i] = rng.randint(1, 6)
                tot += best_play(enemy['id'], N, hp, tuple(sorted(d2)), S)[0]
            if tot / 14 > bv + 0.05:
                bv, best_set = tot / 14, sel
        for i in best_set:
            dice[i] = rng.randint(1, 6)
    _, hp2, dodge, rep = best_play(enemy['id'], N, hp, tuple(sorted(dice)), S)
    return hp2, dodge, rep


def battle(rng, enemy, N, ship=5, extra_rerolls=0):
    hp = setup(enemy, N)
    h = ship
    for _ in range(N):
        hp, dodge, rep = turn(rng, enemy, N, hp, extra_rerolls)
        h = min(10, h + rep)
        if is_dead(enemy, hp):
            return 'победа', h
        if not dodge:
            h -= damage(enemy, hp)
        if h <= 0:
            return 'поражение', h
    return 'ничья', h


if __name__ == '__main__':
    rng = random.Random(3)
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    print('враг            N | победа ничья поражение | Корпус после (старт 5)')
    for e in ENEMIES:
        for N in (4, 5, 6):
            c = collections.Counter(); hs = []
            for _ in range(reps):
                r, h = battle(rng, e, N); c[r] += 1; hs.append(h)
            print('%-16s %d | %3d%% %3d%% %3d%% | %.1f' % (e['title'], N, 100 * c['победа'] // reps, 100 * c['ничья'] // reps, 100 * c['поражение'] // reps, sum(hs) / reps))
