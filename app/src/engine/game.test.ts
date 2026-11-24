import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import type { GameData } from '../data';
import { applyShip, thirst } from './effects';
import * as E from './game';

const d: GameData = JSON.parse(readFileSync(new URL('../../public/game_data.json', import.meta.url), 'utf-8'));
const players = (n: number) => Array.from({ length: n }, (_, i) => ({ name: `P${i + 1}` }));
const seq = (...xs: number[]) => { let i = 0; return () => xs[i++ % xs.length]; };
const fresh = (n = 4) => E.newGame(d, { shipName: 'Тест', players: players(n) });
const withEvent = (id: string, terrain = 's'): E.Game => ({ ...fresh(), scene: { kind: 'sea' as const, eventId: id, terrain, island: null, circle: 1, plays: [], shipLeft: false, exclFrom: null }, step: 'actions' as const });

describe('шкалы', () => {
  it('старт и границы 0–10', () => {
    const g = fresh();
    expect(g.ship).toEqual({ H: 7, C: 6, R: 5, M: 0 });
    expect(applyShip(d, g.ship, { R: 20, M: -5 }).ship).toMatchObject({ R: 10, M: 0 });
  });
  it('жажда по команде и раздача рома', () => {
    expect(thirst(d, 3)).toBe(1);
    expect(thirst(d, 6)).toBe(2);
    expect(thirst(d, 9)).toBe(3);
    expect(applyShip(d, { H: 7, C: 6, R: 5, M: 2 }, { RT: 0, M: -1 }).ship).toMatchObject({ R: 3, M: 1 });
    expect(applyShip(d, { H: 7, C: 6, R: 3, M: 2 }, { RT: 2 }).ship.R).toBe(0);
  });
});

describe('выбор эпизода', () => {
  it('пул без повторов, пока не исчерпан', () => {
    let g = fresh();
    const seen = new Set<string>();
    for (let i = 0; i < 6; i++) {
      const r = E.drawFromPool(g, d, 's', Math.random);
      seen.add(r.id);
      g = { ...g, used: r.used };
    }
    expect(seen.size).toBe(6);
  });
  it.each([['sh', 80], ['f', 50]] as const)('%s выбирает тип встречи до вытягивания карты', (terrain, percent) => {
    let g = fresh();
    let fights = 0;
    const cycle = new Set<string>();
    for (let i = 0; i < 100; i++) {
      g = E.enterCell(g, d, terrain, seq(i / 100, 0));
      const id = g.scene!.eventId;
      if (i < percent) {
        expect(g.step).toBe('battle-prep');
        expect(cycle.has(id)).toBe(false);
        cycle.add(id);
        if (cycle.size === Object.keys(d.battles).length) cycle.clear();
        fights++;
      } else {
        expect(g.step).toBe('plan');
        expect(d.pools[terrain]).toContain(id);
      }
    }
    expect(fights).toBe(percent);
  });
  it('особый штиль берёт эпизоды штиля, корабль может начать бой', () => {
    const g = E.enterCell(fresh(), d, 'sp', seq(0));
    expect(d.pools.s).toContain(g.scene!.eventId);
    const b = E.enterCell(fresh(), d, 'sh', seq(0));
    expect(b.step).toBe('battle-prep');
  });
  it('остров: новый получает номер, повторный заход — тот же', () => {
    let g = E.enterIsland(fresh(), d, null, seq(0, 0)); // d6=1 → порт, d6=1 → первый тип порта
    expect(g.islands.map((i) => i.no)).toEqual([1, 2]);
    expect(g.scene!.kind).toBe('port');
    const id = g.scene!.eventId;
    g = E.enterIsland({ ...g, step: 'map' }, d, 2, Math.random);
    expect(g.scene!.eventId).toBe(id);
  });
  it('порт назначения №1 — победа в свободном плавании', () => {
    const g = E.enterIsland(fresh(), d, 1, Math.random);
    expect(g.over?.win).toBe(true);
  });
});

describe('стартовый экран эпизода', () => {
  it('новый эпизод открывается со стартовым экраном, стрелка его закрывает, новый круг — без него', () => {
    const g = E.enterCell(fresh(), d, 'st', seq(0));
    expect(g.scene!.intro).toBe(true);
    const g2 = E.closeIntro(g);
    expect(g2.scene!.intro).toBe(false);
    expect(E.goNext({ ...g2, step: 'after' }, 'circle').scene!.intro).toBe(false);
  });
});

describe('слоты и конец раунда', () => {
  it('исход применяет корабельное, личное отдаёт игрокам', () => {
    const g = E.playSlot(withEvent('S1'), d, 2, 2); // «Выписать чайкам штраф», 7+: F+1, T+1
    expect(g.last!.personal).toEqual({ F: 1, T: 1 });
    expect(g.scene!.plays).toHaveLength(1);
  });
  it('стоимость слота списывается до исхода', () => {
    const g = E.playSlot(withEvent('S1'), d, 4, 1); // Откупиться: сначала Ром −1, затем M −1
    expect(g.ship.R).toBe(4);
  });
  it('пустой тревожный слот — штраф', () => {
    const g = E.endRound(withEvent('ST1', 'st'), d);
    // ST1: ⚠ Ром −2, нет штурвала Корпус −2, новый круг Ропот +1 Корпус −1
    expect(g.ship).toEqual({ H: 4, C: 6, R: 3, M: 1 });
    expect(g.step).toBe('after');
    expect(E.nextOptions(g, d)).toEqual(['circle']);
  });
  it('штурвал с Ходом уводит корабль: нового круга нет', () => {
    let g = E.playSlot(withEvent('ST1', 'st'), d, 1, 3); // Ход 2
    g = E.playSlot(g, d, 5, 1);
    g = E.endRound(g, d);
    expect(g.ship).toEqual({ H: 7, C: 6, R: 5, M: 0 });
    expect(E.nextOptions(g, d)).toEqual(['leave']);
  });
  it('раздача рома заблокирована на втором круге цикла', () => {
    const g = withEvent('ST2', 'st');
    const rum = d.events.ST2.slots.find((s) => s.n === 2)!;
    expect(E.slotState(g, rum).blocked).toBeNull();
    expect(E.slotState({ ...g, scene: { ...g.scene!, circle: 2 } }, rum).blocked).not.toBeNull();
  });
  it('обломки: выбор по вариантам', () => {
    const g = E.playSlot(withEvent('F2', 'f'), d, 4, 2, ['R', 'R', 'T']);
    expect(g.ship.R).toBe(7);
    expect(g.last!.personal).toEqual({ T: 1 });
  });
  it('трезвая тоска и бунт', () => {
    const g = { ...withEvent('S1'), ship: { H: 7, C: 3, R: 0, M: 2 } };
    const r = E.endRound(g, d);
    expect(r.over?.win).toBe(false);
    expect(r.over?.reason).toMatch(/Бунт/);
  });
  it('каждый третий морской раунд — воспоминания', () => {
    const g = { ...withEvent('S1'), seaRounds: 2 };
    expect(E.endRound(g, d).step).toBe('flashback');
  });
  it('excl: удачный побег отменяет остальные слоты', () => {
    let g = withEvent('SH2', 'sh');
    g = E.playSlot(g, d, 1, 2);
    const s3 = d.events.SH2.slots.find((s) => s.n === 3)!;
    expect(E.slotState(g, s3).excluded).toBe(true);
  });
});

describe('бой', () => {
  const battleGame = (n: number, id = 'B2') => {
    const g = { ...fresh(n), scene: { kind: 'battle' as const, eventId: id, terrain: 'sh', island: null, circle: 1, plays: [], shipLeft: false, exclFrom: null }, step: 'battle-prep' as const };
    return E.startBattle(g, d, { brander: false, shields: false, tooth: false });
  };
  it('враг подбирается по числу скелетов', () => {
    expect(battleGame(4).battle).toMatchObject({ enemyHull: 12, helm: 10, dmg: 2, turns: 4 });
    expect(battleGame(6).battle).toMatchObject({ enemyHull: 17, helm: 6 });
    expect(battleGame(5, 'B3').battle).toMatchObject({ enemyHull: 17, helm: 9, dmg: 3 });
  });
  it('залп, руль, ничья и половина награды', () => {
    let g = battleGame(4, 'B1');
    g = E.battleTurn(g, d, { damage: 3, dodge: false, repair: 0 });
    expect(g.ship.H).toBe(6);
    expect(g.last!.notes.join(' ')).toMatch(/Слава \+1/);
    for (let i = 0; i < 3; i++) g = E.battleTurn(g, d, { damage: 1, dodge: true, repair: 0 });
    expect(g.battle!.result).toBe('draw');
    expect(E.battleReward(g, d)).toBe(1);
  });
  it('победа, когда Корпус врага 0', () => {
    let g = battleGame(4, 'B1');
    g = E.battleTurn(g, d, { damage: 12, dodge: false, repair: 0 });
    expect(g.battle!.result).toBe('win');
    expect(g.ship.H).toBe(7);
    expect(E.battleReward(g, d)).toBe(3);
    expect(E.finishBattle(g, d).step).toBe('after');
  });
});
