// Сохранения (только на устройстве): текущая партия + история для отмены, список сохранённых партий.
import type { Game } from './engine/game';

const KEY_CUR = 'vkb.current';
const KEY_HIST = 'vkb.history';
const KEY_SLOTS = 'vkb.saves';
const HIST_MAX = 80;

function read<T>(k: string, def: T): T {
  try {
    const s = localStorage.getItem(k);
    return s ? (JSON.parse(s) as T) : def;
  } catch {
    return def;
  }
}
function write(k: string, v: unknown) {
  try {
    if (v === null) localStorage.removeItem(k);
    else localStorage.setItem(k, JSON.stringify(v));
  } catch {
    /* хранилище недоступно — партия живёт до перезагрузки */
  }
}

export interface Saved { id: string; title: string; at: number; game: Game }

export const store = {
  loadCurrent: () => read<Game | null>(KEY_CUR, null),
  loadHistory: () => read<Game[]>(KEY_HIST, []),
  saveCurrent(g: Game | null, hist: Game[]) {
    write(KEY_CUR, g);
    write(KEY_HIST, g ? hist.slice(-HIST_MAX) : null);
  },
  listSaves: () => read<Saved[]>(KEY_SLOTS, []),
  putSave(g: Game) {
    const all = read<Saved[]>(KEY_SLOTS, []);
    const id = String(g.createdAt);
    const rec: Saved = { id, title: `«${g.shipName}», раунд ${g.round}`, at: Date.now(), game: g };
    write(KEY_SLOTS, [rec, ...all.filter((s) => s.id !== id)].slice(0, 12));
  },
  deleteSave(id: string) {
    write(KEY_SLOTS, read<Saved[]>(KEY_SLOTS, []).filter((s) => s.id !== id));
  },
  HIST_MAX,
};

export function downloadJson(name: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
