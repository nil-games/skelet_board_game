import type { Eff, GameData } from '../data';

export const SHIP_KEYS = ['H', 'C', 'R', 'M'] as const;
export type ShipKey = (typeof SHIP_KEYS)[number];
export type Ship = Record<ShipKey, number>;
export const PERSONAL_KEYS = ['F', 'L', 'T', 'S', 'BL', 'CU'];

const NAMES: Record<string, string> = {
  H: 'Корпус', C: 'Команда', R: 'Ром', M: 'Ропот', D: 'Опасность', F: 'Слава', L: 'Удача', T: 'Сокровища', S: 'Искры',
  BL: 'Благословение', CU: 'Проклятие', mv: 'Ход', sc: 'Разведка', catch: 'Улов', pick: 'Обломки', RT: 'Раздача рома',
};
export const effName = (k: string) => NAMES[k] ?? k;

export function clamp(v: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, v));
}

export function thirst(d: GameData, crew: number): number {
  for (const t of d.thirst) if (crew >= t.crewFrom && crew <= t.crewTo) return t.rum;
  return crew <= 0 ? 0 : d.thirst[d.thirst.length - 1].rum;
}

export function sumEff(...effs: (Eff | null | undefined)[]): Eff {
  const o: Eff = {};
  for (const e of effs) if (e) for (const [k, v] of Object.entries(e)) o[k] = (o[k] ?? 0) + v;
  return o;
}

/** Применить эффект к шкалам корабля. RT (раздача рома): Ром −(Жажда + RT), сколько есть. */
export function applyShip(d: GameData, ship: Ship, eff: Eff): { ship: Ship; delta: Eff } {
  const s = { ...ship };
  const delta: Eff = {};
  const add = (k: ShipKey, v: number) => {
    const before = s[k];
    s[k] = clamp(s[k] + v, 0, 10);
    if (s[k] !== before) delta[k] = (delta[k] ?? 0) + (s[k] - before);
  };
  for (const [k, v] of Object.entries(eff)) {
    if (k === 'RT') add('R', -(thirst(d, s.C) + v));
    else if ((SHIP_KEYS as readonly string[]).includes(k)) add(k as ShipKey, v);
  }
  return { ship: s, delta };
}

export function personalPart(eff: Eff): Eff {
  const o: Eff = {};
  for (const [k, v] of Object.entries(eff)) if (PERSONAL_KEYS.includes(k) && v) o[k] = v;
  return o;
}

const sign = (v: number) => (v > 0 ? '+' + v : '−' + Math.abs(v));

/** «Корпус −1, Слава +1». BL/CU — метки, без числа. */
export function fmtEff(eff: Eff): string {
  const parts: string[] = [];
  for (const [k, v] of Object.entries(eff)) {
    if (!v && k !== 'RT') continue;
    if (k === 'BL' || k === 'CU') parts.push(effName(k));
    else if (k === 'mv') parts.push(`Ход ${v}`);
    else if (k === 'sc') parts.push(`Разведка ${v}`);
    else if (k === 'catch') parts.push(`Улов: ${v} ${v === 1 ? 'заброс' : 'заброса'}`);
    else if (k === 'pick') parts.push(`Обломки: выбор ×${v}`);
    else if (k === 'RT') parts.push(v ? `Раздача рома (Жажда +${v})` : 'Раздача рома');
    else parts.push(`${effName(k)} ${sign(v)}`);
  }
  return parts.join(', ');
}

/** Ключи сущностей, которые затрагивает слот (подсказка без знаков). */
export function slotEntities(eff: Eff[]): string[] {
  const keys = new Set<string>();
  for (const e of eff) for (const [k, v] of Object.entries(e)) if (v || k === 'RT') keys.add(k === 'RT' ? 'R' : k);
  const order = ['H', 'C', 'R', 'M', 'F', 'L', 'T', 'S', 'BL', 'CU', 'mv', 'sc', 'catch', 'pick'];
  return order.filter((k) => keys.has(k));
}

export function defeat(ship: Ship): string | null {
  if (ship.H <= 0) return 'Затонули (снова): Корпус 0';
  if (ship.C <= 0) return 'Разошлась команда: Команда 0';
  if (ship.M >= ship.C) return 'Бунт мертвецов: Ропот догнал Команду';
  return null;
}
