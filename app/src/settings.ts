// Настройки устройства (хранятся на телефоне, не в партии). Звуки по-прежнему живут в sound.ts: здесь они только отражены.
import { useEffect, useState } from 'preact/hooks';
import { setSoundOn, soundOn } from './sound';

/** Варианты таймера планирования, секунды; 0 — выключен. Менять варианты только здесь. */
export const TIMER_OPTIONS = [60, 45, 30, 0] as const;
export type TimerSec = (typeof TIMER_OPTIONS)[number];

export interface Settings {
  music: boolean;   // фоновая музыка (файлов пока нет: значение сохраняется для будущего)
  sounds: boolean;  // звуки интерфейса
  voice: boolean;   // озвучка текстов (пока нет: значение сохраняется для будущего)
  timer: TimerSec;
}

const KEY = 'vkb.settings';
const DEFAULTS: Settings = { music: true, sounds: true, voice: false, timer: 60 };

function load(): Settings {
  let s: Partial<Settings> = {};
  try { s = JSON.parse(localStorage.getItem(KEY) ?? '{}') as Partial<Settings>; } catch { /* значения по умолчанию */ }
  return {
    music: typeof s.music === 'boolean' ? s.music : DEFAULTS.music,
    sounds: soundOn(),
    voice: typeof s.voice === 'boolean' ? s.voice : DEFAULTS.voice,
    timer: (TIMER_OPTIONS as readonly number[]).includes(s.timer as number) ? (s.timer as TimerSec) : DEFAULTS.timer,
  };
}

let current = load();
const listeners = new Set<() => void>();

export const getSettings = () => current;

export function updateSettings(patch: Partial<Settings>) {
  current = { ...current, ...patch };
  if (patch.sounds !== undefined) setSoundOn(patch.sounds);
  try {
    const { sounds: _s, ...rest } = current; // звуки хранит sound.ts
    localStorage.setItem(KEY, JSON.stringify(rest));
  } catch { /* без сохранения */ }
  listeners.forEach((f) => f());
}

/** Хук: компонент перерисовывается при любом изменении настроек. */
export function useSettings(): Settings {
  const [, tick] = useState(0);
  useEffect(() => {
    const f = () => tick((n) => n + 1);
    listeners.add(f);
    return () => { listeners.delete(f); };
  }, []);
  return current;
}
