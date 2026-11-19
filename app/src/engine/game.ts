// Игровой движок: чистые функции (state, ...) => новый state. UI только вызывает их и рисует результат.
import type { Eff, EventDef, GameData, Slot } from '../data';
import { eventById } from '../data';
import { applyShip, clamp, defeat, fmtEff, personalPart, sumEff, type Ship, type ShipKey } from './effects';

export type Rng = () => number;
export const d6 = (rng: Rng) => 1 + Math.floor(rng() * 6);

export interface Player { name: string }
export interface Play { slot: number; pick: number; eff: Eff; personal: Eff; text: string; title: string }
export interface Island { no: number; kind: 'port' | 'wild'; id: string }
export interface Scene {
  kind: 'sea' | 'port' | 'battle';
  eventId: string;
  terrain: string;            // ключ значка клетки: s, sp, st, sh, f, i
  island: number | null;
  circle: number;             // номер круга (для циклов)
  plays: Play[];
  shipLeft: boolean;          // за раунд получен Ход → корабль покинул клетку
  exclFrom: number | null;    // слоты с номером больше этого не разыгрываются
  intro?: boolean;            // стартовый экран эпизода ещё не закрыт
}
export interface Battle {
  id: string;
  enemyMax: number;
  enemyHull: number;
  dmg: number;
  helm: number;
  turn: number;               // сколько ходов сделано
  turns: number;              // ходов в круге = число скелетов
  shields: boolean;           // Щиты: первый залп −1
  result: null | 'win' | 'lose' | 'draw';
  log: string[];
}
export interface EndItem { text: string; eff: Eff }
export interface Result { title: string; text: string; ship: Eff; personal: Eff; notes: string[]; slot?: number }
export type Step = 'map' | 'plan' | 'actions' | 'end' | 'battle-prep' | 'battle' | 'flashback' | 'after' | 'over';
export interface LogEntry { round: number; text: string }

export interface Game {
  schema: 1;
  contentVersion: string;
  createdAt: number;
  mode: 'free';
  shipName: string;
  players: Player[];
  ship: Ship;
  round: number;
  seaRounds: number;
  step: Step;
  scene: Scene | null;
  battle: Battle | null;
  islands: Island[];
  used: Record<string, string[]>;
  journal: number[];          // 8 строк ключевых слов, 0–6
  flags: Record<string, boolean>;
  log: LogEntry[];
  last: Result | null;
  over: { win: boolean; reason: string } | null;
  fullSpeed: boolean;
}

export const JOURNAL_ROWS = ['✗ Крест', '☸ Штурвал', '☀ Солнце', '☾ Луна', '☠ Череп', '🦜 Попугай', '👺 Гоблин', '🔮 Маг'];

export interface NewGameCfg { shipName: string; players: Player[] }

export function newGame(d: GameData, cfg: NewGameCfg): Game {
  const ship = { H: d.ship.H.start, C: d.ship.C.start, R: d.ship.R.start, M: d.ship.M.start };
  return {
    schema: 1,
    contentVersion: d.version,
    createdAt: Date.now(),
    mode: 'free',
    shipName: cfg.shipName.trim() || 'Блюющий скелет',
    players: cfg.players,
    ship,
    round: 1,
    seaRounds: 0,
    step: 'map',
    scene: null,
    battle: null,
    // свободное плавание: порт назначения — остров №1, Рыночный порт
    islands: [{ no: 1, kind: 'port', id: 'P1' }],
    used: {},
    journal: JOURNAL_ROWS.map(() => 0),
    flags: {},
    log: [{ round: 1, text: `Корабль «${cfg.shipName.trim() || 'Блюющий скелет'}» вышел в море. Скелетов: ${cfg.players.length}.` }],
    last: null,
    over: null,
    fullSpeed: false,
  };
}

const log = (g: Game, text: string): LogEntry[] => [...g.log, { round: g.round, text }];

/** Случайное событие из пула без повторов, пока пул не исчерпан. */
export function drawFromPool(g: Game, d: GameData, pool: string, rng: Rng): { id: string; used: Record<string, string[]> } {
  const all = d.pools[pool];
  const used = g.used[pool] ?? [];
  let free = all.filter((x) => !used.includes(x));
  let nextUsed = used;
  if (free.length === 0) { free = all; nextUsed = []; }
  const id = free[Math.floor(rng() * free.length)];
  return { id, used: { ...g.used, [pool]: [...nextUsed, id] } };
}

function sceneFor(eventId: string, terrain: string, island: number | null, kind: Scene['kind']): Scene {
  return { kind, eventId, terrain, island, circle: 1, plays: [], shipLeft: false, exclFrom: null, intro: true };
}

export function terrainPool(terrain: string): string {
  return terrain === 'sp' ? 's' : terrain; // особый штиль без сценария = штиль
}

/** Корабль закончил движение в клетке со значком terrain (кроме острова). */
export function enterCell(g: Game, d: GameData, terrain: string, rng: Rng): Game {
  const { id, used } = drawFromPool(g, d, terrainPool(terrain), rng);
  const name = d.terrains.find((t) => t.key === terrain)?.name ?? terrain;
  if (d.battles[id]) {
    return { ...g, used, scene: sceneFor(id, terrain, null, 'battle'), battle: null, step: 'battle-prep', last: null, log: log(g, `${name}: бой — ${d.battles[id].title}`) };
  }
  return { ...g, used, scene: sceneFor(id, terrain, null, 'sea'), step: 'plan', last: null, log: log(g, `${name}: ${d.events[id].title}`) };
}

/** Остров: no = номер уже посещённого острова или null для нового. */
export function enterIsland(g: Game, d: GameData, no: number | null, rng: Rng): Game {
  let islands = g.islands;
  let used = g.used;
  let isl: Island;
  if (no === null) {
    const next = Math.max(0, ...islands.map((i) => i.no)) + 1;
    if (d6(rng) <= d.islandPortChance) {
      isl = { no: next, kind: 'port', id: d.portTable[d6(rng) - 1] };
    } else {
      const r = drawFromPool(g, d, 'i_wild', rng);
      used = r.used;
      isl = { no: next, kind: 'wild', id: r.id };
    }
    islands = [...islands, isl];
  } else {
    const f = islands.find((i) => i.no === no);
    if (!f) return g;
    isl = f;
  }
  const ev = eventById(d, isl.id)!;
  const base = { ...g, islands, used, last: null };
  const text = `Остров №${isl.no}: ${ev.title}${no === null ? ' (открыт)' : ''}`;
  if (isl.kind === 'port') {
    const ng: Game = { ...base, scene: sceneFor(isl.id, 'i', isl.no, 'port'), step: 'plan', log: log(g, text) };
    if (g.mode === 'free' && isl.no === 1 && !g.flags.goalReached) {
      return { ...ng, flags: { ...g.flags, goalReached: true }, over: { win: true, reason: 'Корабль дошёл до порта назначения' }, step: 'over', log: log(ng, 'Цель достигнута: порт назначения!') };
    }
    return ng;
  }
  return { ...base, scene: sceneFor(isl.id, 'i', isl.no, 'sea'), step: 'plan', log: log(g, text) };
}

export function currentEvent(g: Game, d: GameData): EventDef | null {
  return g.scene && g.scene.kind !== 'battle' ? eventById(d, g.scene.eventId) ?? null : null;
}

export const isRumSlot = (s: Slot) => !!s.choices?.some((c) => 'RT' in c.eff);

/** Состояние слота в текущем раунде. */
export function slotState(g: Game, s: Slot): { blocked: string | null; mandatory: boolean; plays: number; excluded: boolean } {
  const sc = g.scene!;
  let blocked: string | null = null;
  if (s.crewReq && g.ship.C < s.crewReq) blocked = `нужна Команда ≥ ${s.crewReq}`;
  if (isRumSlot(s) && sc.circle > 1) blocked = 'раздача уже была в этом цикле';
  if (s.n === 7 && !['s', 'sp'].includes(sc.terrain)) blocked = 'рыбалка только в штиль';
  const excluded = sc.exclFrom !== null && s.n > sc.exclFrom;
  return { blocked, mandatory: s.mandatory && !blocked, plays: sc.plays.filter((p) => p.slot === s.n).length, excluded };
}

export function eventSlots(g: Game, d: GameData): Slot[] {
  const ev = currentEvent(g, d);
  return ev ? ev.slots : [];
}

/** Закрыть стартовый экран эпизода (картинка, название, описание). */
export function closeIntro(g: Game): Game {
  return g.scene ? { ...g, scene: { ...g.scene, intro: false } } : g;
}

export function startActions(g: Game): Game {
  return { ...g, step: 'actions' };
}

export function planTimeout(g: Game, d: GameData): Game {
  const { ship, delta } = applyShip(d, g.ship, { M: 1 });
  return checkOver({ ...g, ship, last: { title: 'Тайм-аут', text: 'Не успели расставить кубики.', ship: delta, personal: {}, notes: [] }, log: log(g, 'Тайм-аут планирования: Ропот +1') });
}

function checkOver(g: Game): Game {
  const why = defeat(g.ship);
  if (why) return { ...g, over: { win: false, reason: why }, step: 'over', log: log(g, 'Поражение. ' + why) };
  return g;
}

/**
 * Отыграть один кубик в слоте: pick — индекс исхода (или выбора), picks — ключи для «Обломков» (R/T/H).
 */
export function playSlot(g: Game, d: GameData, slotN: number, pick: number, picks: string[] = []): Game {
  const s = eventSlots(g, d).find((x) => x.n === slotN);
  if (!s || !g.scene) return g;
  const item = s.choices ? s.choices[pick] : s.outcomes[pick];
  if (!item) return g;
  const extra: Eff = {};
  for (const k of picks) extra[k] = (extra[k] ?? 0) + 1;
  const eff = sumEff(s.cost, item.eff, extra);
  const { ship, delta } = applyShip(d, g.ship, eff);
  const personal = personalPart(eff);
  const notes: string[] = [];
  if (eff.mv) notes.push(`Проведите на карте ${eff.mv} ${eff.mv === 1 ? 'линию' : 'линии'} хода.`);
  if (eff.sc) notes.push(`Разведка ${eff.sc}: выберите ${eff.sc} пустых клетки рядом и бросьте d6 на каждую.`);
  if (eff.catch) notes.push(`Улов: ${eff.catch === 1 ? 'один бросок d6' : eff.catch === 2 ? 'два броска d6, выберите один' : 'два броска d6, берите оба'} по таблице улова.`);
  if (eff.BL) notes.push('Поставьте ✓ Благословение (следующая проверка: 2 кубика, худший).');
  if (eff.CU) notes.push('Поставьте ✓ Проклятие (следующая проверка: 2 кубика, лучший).');
  const label = s.choices ? (s.choices[pick].label) : (s.outcomes[pick].label ?? '');
  const play: Play = { slot: slotN, pick, eff, personal, text: item.text, title: s.title };
  let exclFrom = g.scene.exclFrom;
  if (s.excl && !s.choices && pick >= s.excl.fromOutcome) { exclFrom = slotN; notes.push(s.excl.text); }
  const scene: Scene = { ...g.scene, plays: [...g.scene.plays, play], shipLeft: g.scene.shipLeft || (eff.mv ?? 0) > 0, exclFrom };
  const shipTxt = fmtEff(delta);
  return checkOver({
    ...g, ship, scene,
    last: { title: `${slotN}. ${s.title}${label ? ' — ' + label : ''}`, text: item.text, ship: delta, personal, notes, slot: slotN },
    log: log(g, `${s.title}${label ? ' (' + label + ')' : ''}${shipTxt ? ': ' + shipTxt : ''}`),
  });
}

/** Что случится в конце раунда (для экрана подтверждения). */
export function endPreview(g: Game, d: GameData): EndItem[] {
  const sc = g.scene;
  if (!sc) return [];
  const out: EndItem[] = [];
  const ev = currentEvent(g, d);
  if (ev) {
    for (const s of ev.slots) {
      const st = slotState(g, s);
      if (s.alarm && st.plays === 0 && !st.blocked && !st.excluded) out.push({ text: `⚠ Слот ${s.n} «${s.title}» пуст`, eff: s.alarm.eff });
    }
    const helm = ev.slots.find((s) => s.n === 1);
    if (ev.flow === 'loop' && ev.end.noHelm && helm && slotState(g, helm).plays === 0) {
      out.push({ text: `Никто не встал к штурвалу${ev.end.noHelm.note ? ' (' + ev.end.noHelm.note + ')' : ''}`, eff: ev.end.noHelm.eff });
    }
    if (ev.end.always) out.push({ text: 'Конец эпизода', eff: ev.end.always });
  }
  return out;
}

function applyItems(g: Game, d: GameData, items: EndItem[]): { ship: Ship; lines: string[] } {
  let ship = g.ship;
  const lines: string[] = [];
  for (const it of items) {
    const r = applyShip(d, ship, it.eff);
    ship = r.ship;
    lines.push(`${it.text}: ${fmtEff(it.eff)}`);
  }
  return { ship, lines };
}

/** Завершить действия: штрафы, конец эпизода, трезвая тоска, цена нового круга, проверка краёв. */
export function endRound(g: Game, d: GameData): Game {
  const sc = g.scene;
  if (!sc) return g;
  const ev = currentEvent(g, d);
  let { ship, lines } = applyItems(g, d, endPreview(g, d));
  const extra: EndItem[] = [];
  if (ev) for (const c of ev.end.crewBelow) if (ship.C < c.n) extra.push({ text: `Команда меньше ${c.n}${c.note ? ' (' + c.note + ')' : ''}`, eff: c.eff });
  if (ship.R === 0) extra.push({ text: 'Трезвая тоска (Ром 0)', eff: { M: 1 } });
  const loopStay = ev?.flow === 'loop' && !sc.shipLeft;
  if (loopStay && ev?.circle) extra.push({ text: 'Корабль не покинул клетку: новый круг', eff: ev.circle });
  const r2 = applyItems({ ...g, ship }, d, extra);
  ship = r2.ship;
  lines = [...lines, ...r2.lines];
  const seaRounds = sc.kind === 'port' ? g.seaRounds : g.seaRounds + 1;
  let ng: Game = {
    ...g, ship, seaRounds,
    last: lines.length ? { title: 'Конец раунда', text: '', ship: diff(g.ship, ship), personal: {}, notes: lines } : null,
    log: [...g.log, ...lines.map((t) => ({ round: g.round, text: t }))],
  };
  ng = checkOver(ng);
  if (ng.step === 'over') return ng;
  const flash = sc.kind !== 'port' && seaRounds % d.flashbackEvery === 0;
  return { ...ng, step: flash ? 'flashback' : 'after' };
}

function diff(a: Ship, b: Ship): Eff {
  const o: Eff = {};
  for (const k of Object.keys(a) as ShipKey[]) if (a[k] !== b[k]) o[k] = b[k] - a[k];
  return o;
}

export function finishFlashback(g: Game): Game {
  return { ...g, step: 'after' };
}

/** Воспоминание игрока: Гордость (Ропот −1 кораблю) или Стыд (Слава +1 себе). */
export function flashbackChoice(g: Game, d: GameData, player: string, choice: 'pride' | 'shame'): Game {
  if (choice === 'pride') {
    const { ship, delta } = applyShip(d, g.ship, { M: -1 });
    return { ...g, ship, last: { title: `Воспоминание: ${player}`, text: 'Гордость.', ship: delta, personal: {}, notes: ['Зачеркните пережитую Искру.'] }, log: log(g, `${player} вспомнил: гордость (Ропот −1)`) };
  }
  return { ...g, last: { title: `Воспоминание: ${player}`, text: 'Стыд.', ship: {}, personal: { F: 1 }, notes: ['Зачеркните пережитую Искру.'] }, log: log(g, `${player} вспомнил: стыд (Слава +1)`) };
}

/** Что дальше после раунда. */
export type Next = 'circle' | 'port' | 'leave';
export function nextOptions(g: Game, d: GameData): Next[] {
  const sc = g.scene;
  if (!sc) return ['leave'];
  if (sc.kind === 'port') return ['port', 'leave'];
  const ev = currentEvent(g, d);
  if (ev?.flow === 'loop' && !sc.shipLeft) return ['circle'];
  return ['leave'];
}

export function goNext(g: Game, next: Next): Game {
  const sc = g.scene!;
  const round = g.round + 1;
  if (next === 'circle') return { ...g, round, scene: { ...sc, circle: sc.circle + 1, plays: [], shipLeft: false, exclFrom: null }, step: 'plan', last: null };
  if (next === 'port') return { ...g, round, scene: { ...sc, circle: sc.circle + 1, plays: [], exclFrom: null }, step: 'plan', last: null };
  return { ...g, round, scene: null, battle: null, step: 'map', last: null, fullSpeed: false };
}

/** Траты рома по желанию (конец раунда, Ром > 0): разведка за ром или «Полный вперёд». */
export function spendRum(g: Game, d: GameData, kind: 'scout' | 'speed'): Game {
  if (g.ship.R <= 0) return g;
  const { ship, delta } = applyShip(d, g.ship, { R: -1 });
  const note = kind === 'scout'
    ? 'Разведка за ром: выберите до 2 пустых клеток рядом с кораблём, затем бросьте d6 на каждую.'
    : 'Полный вперёд: уходя из клетки, проведите 2 линии вместо 1.';
  return { ...g, ship, fullSpeed: g.fullSpeed || kind === 'speed', last: { title: kind === 'scout' ? 'Разведка за ром' : 'Полный вперёд', text: '', ship: delta, personal: {}, notes: [note] }, log: log(g, (kind === 'scout' ? 'Разведка за ром' : 'Полный вперёд') + ': Ром −1') };
}

/** Ручная правка шкалы. */
export function adjust(g: Game, key: ShipKey, delta: number): Game {
  const ship = { ...g.ship, [key]: clamp(g.ship[key] + delta, 0, 10) };
  return checkOver({ ...g, ship, log: log(g, `Ручная правка: ${key === 'H' ? 'Корпус' : key === 'C' ? 'Команда' : key === 'R' ? 'Ром' : 'Ропот'} ${delta > 0 ? '+' : '−'}${Math.abs(delta)}`) });
}

/** Быстрая покупка корабельного товара в порту (монеты игроки списывают сами). */
export function buyShip(g: Game, d: GameData, name: string, eff: Eff): Game {
  const { ship, delta } = applyShip(d, g.ship, eff);
  return { ...g, ship, last: { title: `Куплено: ${name}`, text: '', ship: delta, personal: {}, notes: ['Спишите монеты у тех, кто платил.'], slot: 5 }, log: log(g, `Магазин: ${name} (${fmtEff(delta) || 'без изменений'})`) };
}

export function continueAfterWin(g: Game): Game {
  return { ...g, over: null, step: 'plan' };
}

export function setJournal(g: Game, row: number, value: number): Game {
  const journal = g.journal.slice();
  journal[row] = clamp(value, 0, 6);
  return { ...g, journal };
}

// ------------------------------------------------------------------ бой
export function battleSetup(d: GameData, id: string, n: number) {
  const b = d.battles[id];
  const base = d.enemyByN[String(clamp(n, 4, 6))];
  const dm = d.enemyDamage[b.cls];
  return { hull: base.hull + (b.hullBonus || 0), helm: base.helm + dm.helmPlus, dmg: dm.dmg, reward: d.battleReward[b.cls] };
}

export interface BattleUpgrades { brander: boolean; shields: boolean; tooth: boolean }

export function startBattle(g: Game, d: GameData, up: BattleUpgrades): Game {
  const sc = g.scene!;
  const s = battleSetup(d, sc.eventId, g.players.length);
  let hull = s.hull;
  const logs: string[] = [];
  if (up.brander) { hull -= 1; logs.push('Брандер: враг −1'); }
  if (up.tooth) { hull -= 2; logs.push('Зуб кита: враг −2'); }
  const battle: Battle = { id: sc.eventId, enemyMax: s.hull, enemyHull: Math.max(0, hull), dmg: s.dmg, helm: s.helm, turn: 0, turns: g.players.length, shields: up.shields, result: null, log: logs };
  if (battle.enemyHull <= 0) battle.result = 'win';
  return { ...g, battle, step: 'battle', last: null, log: log(g, `Бой начался: ${d.battles[sc.eventId].title}, Корпус врага ${battle.enemyHull}`) };
}

export interface TurnInput { damage: number; dodge: boolean; repair: number }

export function battleTurn(g: Game, d: GameData, t: TurnInput): Game {
  const b = g.battle;
  if (!b || b.result) return g;
  const who = g.players[b.turn]?.name ?? `Скелет ${b.turn + 1}`;
  const lines: string[] = [];
  let ship = g.ship;
  const enemyHull = Math.max(0, b.enemyHull - Math.max(0, t.damage));
  if (t.damage > 0) lines.push(`${who}: урон врагу ${t.damage}`);
  if (t.repair > 0) { ship = applyShip(d, ship, { H: t.repair }).ship; lines.push(`Трюм: Корпус +${t.repair}`); }
  let shields = b.shields;
  let result: Battle['result'] = null;
  const personal: Eff = t.damage >= 3 ? { F: 1 } : {};
  if (enemyHull <= 0) {
    result = 'win';
    lines.push('Враг идёт ко дну!');
  } else if (t.dodge) {
    lines.push('Руль: залп врага мимо');
  } else {
    const dmg = Math.max(0, b.dmg - (shields ? 1 : 0));
    shields = false;
    ship = applyShip(d, ship, { H: -dmg }).ship;
    lines.push(`Залп врага: Корпус −${dmg}`);
    if (ship.H <= 0) result = 'lose';
  }
  const turn = b.turn + 1;
  if (!result && turn >= b.turns) { result = 'draw'; lines.push('Круг окончен, оба на плаву: враг отступает.'); }
  const battle: Battle = { ...b, enemyHull, turn, shields, result, log: [...b.log, ...lines] };
  const notes = [...lines];
  if (personal.F) notes.push(`${who}: Слава +1 (3+ урона за ход).`);
  return checkOver({ ...g, ship, battle, last: { title: `Ход ${turn}: ${who}`, text: '', ship: diff(g.ship, ship), personal: {}, notes }, log: [...g.log, ...lines.map((x) => ({ round: g.round, text: x }))] });
}

export function battleReward(g: Game, d: GameData): number {
  const b = g.battle;
  if (!b) return 0;
  const full = battleSetup(d, b.id, g.players.length).reward;
  return b.result === 'win' ? full : b.result === 'draw' ? Math.floor(full / 2) : 0;
}

/** После боя — обычный конец раунда (трезвая тоска и т. п.), корабль уходит. */
export function finishBattle(g: Game, d: GameData): Game {
  const r = battleReward(g, d);
  const g2 = { ...g, log: log(g, `Бой окончен: ${g.battle?.result === 'win' ? 'победа' : 'ничья'}, Сокровища +${r} каждому`) };
  return endRound(g2, d);
}
