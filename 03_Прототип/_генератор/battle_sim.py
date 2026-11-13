# -*- coding: utf-8 -*-
"""Симуляция боя Борта (v0.19): ходящий всегда бросает 5 кубиков.
Таблица врага под N скелетов (Корпус, Руль S; урон 1/2/3, у сильного S+1): 4 → 12/10, 5 → 14/8, 6 → 17/6.
Бой в стиле Yahtzee: 5 кубиков, 1 переброс любого числа кубиков, распределение по станциям, ответный залп врага.
Считаем: средний урон за ход, исход круга (все игроки по одному разу) при разных параметрах врага."""
import itertools, random, statistics, collections, sys
from functools import lru_cache

CANNON = {2: 1, 3: 3, 4: 5, 5: 8}           # урон по числу одинаковых
RAM = {3: 2, 4: 4, 5: 6}                     # урон по длине стрита
STATIONS = 4                                  # 0 пушки, 1 таран, 2 руль, 3 трюм, 4 не используется


def best_run(vals):
    s = sorted(set(vals))
    best = cur = 0
    prev = None
    for v in s:
        cur = cur + 1 if prev is not None and v == prev + 1 else 1
        best = max(best, cur)
        prev = v
    return best


def station_value(kind, vals, S):
    if kind == 0:
        c = max(collections.Counter(vals).values()) if vals else 0
        return CANNON.get(c, 0), 0, 0
    if kind == 1:
        r = best_run(vals) if vals else 0
        return RAM.get(r, 0), 0, 0
    if kind == 2:
        return 0, 0, 1 if vals and sum(vals) >= S else 0
    if kind == 3:
        return 0, sum(1 for v in vals if v <= 2), 0
    return 0, 0, 0


@lru_cache(None)
def best_alloc(dice, S, U, w_rep, w_dodge):
    """Лучшее распределение 5 кубиков (отсортированный кортеж): (полезность, урон, ремонт, увернулись)."""
    best = (-1, 0, 0, 0)
    for assign in itertools.product(range(5), repeat=5):
        groups = [[] for _ in range(4)]
        for d, a in zip(dice, assign):
            if a < 4:
                groups[a].append(d)
        dmg = rep = dodge = 0
        for k in range(4):
            a, b, c = station_value(k, groups[k], S)
            dmg += a; rep += b; dodge += c
        u = dmg + w_rep * rep + w_dodge * dodge * U
        if u > best[0]:
            best = (u, dmg, rep, dodge)
    return best


def turn(rng, S, U, w_rep=0.5, w_dodge=0.6, bonus=0):
    dice = [rng.randint(1, 6) for _ in range(5)]
    # решение о переброске: перебор подмножеств, ожидание по случайной выборке (быстро)
    def value(ds):
        return best_alloc(tuple(sorted(ds)), S, U, w_rep, w_dodge)[0]
    best_set, best_val = (), value(dice)
    base = best_val
    for mask in range(1, 32):
        idx = [i for i in range(5) if mask >> i & 1]
        tot = 0
        n = 60
        for _ in range(n):
            d2 = dice[:]
            for i in idx:
                d2[i] = rng.randint(1, 6)
            tot += value(d2)
        ev = tot / n
        if ev > best_val + 1e-9:
            best_val, best_set = ev, tuple(idx)
    for i in best_set:
        dice[i] = rng.randint(1, 6)
    u, dmg, rep, dodge = best_alloc(tuple(sorted(dice)), S, U, w_rep, w_dodge)
    return dmg + bonus * (1 if dmg else 0), rep, dodge


def battle_round(rng, N, E, U, S, ship, bonus):
    """Один круг: каждый из N игроков ходит один раз. Возвращает (исход, корпус корабля, корпус врага)."""
    e, h = E, ship
    for _ in range(N):
        dmg, rep, dodge = turn(rng, S, U, bonus=bonus)
        e -= dmg
        h = min(10, h + rep)
        if e <= 0:
            return 'победа', h, e
        if not dodge:
            h -= U
        if h <= 0:
            return 'поражение', h, e
    return 'ничья', h, e


if __name__ == '__main__':
    rng = random.Random(1)
    S = 14
    print('средний урон за ход (оптимизируем урон + ремонт 0.5 + уклонение 0.6·U):')
    for U in (1, 2):
        ds = [turn(rng, S, U) for _ in range(600)]
        print('  U=%d: урон %.2f, ремонт %.2f, уклонение %.0f%%' % (U, statistics.mean(x[0] for x in ds), statistics.mean(x[1] for x in ds), 100 * statistics.mean(x[2] for x in ds)))
