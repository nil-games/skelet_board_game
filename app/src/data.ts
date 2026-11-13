// Типы контента (game_data.json генерируется export_app.py из content.py — правьте там, не здесь).
export type Eff = Record<string, number>;

export interface Outcome { label: string | null; eff: Eff; text: string }
export interface Choice { label: string; eff: Eff; text: string }
export interface Slot {
  n: number;
  title: string;
  skill: string | null;
  shared: boolean;
  mandatory: boolean;
  req: string | null;
  crewReq: number | null;
  cost: Eff | null;
  note: string | null;
  alarm: { text: string; eff: Eff } | null;
  excl: { fromOutcome: number; text: string } | null;
  outcomes: Outcome[];
  choices: Choice[] | null;
}
export interface EndRules {
  noHelm: { eff: Eff; note: string | null } | null;
  always: Eff | null;
  crewBelow: { n: number; eff: Eff; note: string | null }[];
  circle: Eff | null;
}
export interface EventDef {
  id: string;
  kind: 'sea' | 'port';
  hint: string | null;
  title: string;
  flavor: string;
  warn: string | null;
  flow: 'auto' | 'loop' | 'port';
  slots: Slot[];
  endText: string | null;
  end: EndRules;
  circle?: Eff;
  shop?: boolean;
  casino?: boolean;
  fish?: string | null;
}
export interface BattleDef { id: string; title: string; cls: string; special: string | null; flavor: string; warn: string | null; hullBonus: number }
export interface ShipScale { name: string; start: number; lo: number | null; hi: number; scenario_only?: boolean }

export interface GameData {
  version: string;
  ship: Record<string, ShipScale>;
  thirst: { crewFrom: number; crewTo: number; rum: number }[];
  skills: Record<string, string>;
  effectNames: Record<string, string>;
  terrains: { d6: number; key: string; sym: string; name: string }[];
  pools: Record<string, string[]>;
  islandPortChance: number;
  portTable: string[];
  events: Record<string, EventDef>;
  ports: Record<string, EventDef>;
  battles: Record<string, BattleDef>;
  enemyByN: Record<string, { hull: number; helm: number }>;
  enemyDamage: Record<string, { dmg: number; helmPlus: number }>;
  battleReward: Record<string, number>;
  shop: { col: string; items: { name: string; price: number; text: string }[] }[];
  catch: { key: string; name: string; fish: { name: string; price: number }[] }[];
  curios: Record<string, { price: number; sparks: number; text: string }>;
  casinoUpgrades: { name: string; price: number; text: string }[];
  bets: { ratio: string; name: string; short: string; text: string }[];
  betRules: string;
  casinoRule: string;
  fishSlot: Slot;
  flashbackEvery: number;
}

export async function loadData(): Promise<GameData> {
  const r = await fetch(import.meta.env.BASE_URL + 'game_data.json', { cache: 'no-cache' });
  if (!r.ok) throw new Error('Не удалось загрузить game_data.json');
  return r.json();
}

export function eventById(d: GameData, id: string): EventDef | undefined {
  return d.events[id] ?? d.ports[id];
}
