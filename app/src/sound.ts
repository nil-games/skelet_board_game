// Звуки интерфейса. Файлы лежат в public/sounds/<id>.mp3 и выровнены до одной громкости (−18 LUFS),
// поэтому здесь только общая громкость и выключатель. Список и описания: ../../Звуки_интерфейса.md.

export const SOUND_IDS = [
  'btn', 'btn-main', 'btn-back', 'btn-close', 'btn-denied', 'undo',
  'plus', 'minus', 'scale', 'stepper', 'murmur', 'journal',
  'step', 'sheet-open', 'sheet-close', 'tab', 'map',
  'intro', 'intro-next', 'dice', 'slot-open', 'choice', 'tick', 'timeout',
  'buy', 'rum', 'casino', 'battle-start', 'hit', 'win', 'lose', 'save',
] as const;
export type SoundId = (typeof SOUND_IDS)[number];

/** Общая громкость (0..1). Менять только здесь: все файлы уже выровнены между собой. */
const MASTER = 0.9;
const KEY = 'vkb.sound';

let on = readOn();
let ctx: AudioContext | null = null;
let master: GainNode | null = null;
const buffers = new Map<SoundId, AudioBuffer>();
const raw = new Map<SoundId, Promise<ArrayBuffer | null>>();

function readOn(): boolean {
  try { return localStorage.getItem(KEY) !== '0'; } catch { return true; }
}

export const soundOn = () => on;
export function setSoundOn(v: boolean) {
  on = v;
  try { localStorage.setItem(KEY, v ? '1' : '0'); } catch { /* без сохранения */ }
}

/** Скачиваем файлы заранее (кэш service worker отдаст их и офлайн), декодируем после первого касания. */
function fetchRaw(id: SoundId): Promise<ArrayBuffer | null> {
  let p = raw.get(id);
  if (!p) {
    p = fetch(`${import.meta.env.BASE_URL}sounds/${id}.mp3`).then((r) => (r.ok ? r.arrayBuffer() : null)).catch(() => null);
    raw.set(id, p);
  }
  return p;
}

function audio(): AudioContext | null {
  if (ctx) return ctx;
  const AC = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!AC) return null;
  ctx = new AC();
  master = ctx.createGain();
  master.gain.value = MASTER;
  master.connect(ctx.destination);
  return ctx;
}

async function decode(id: SoundId): Promise<AudioBuffer | null> {
  const have = buffers.get(id);
  if (have) return have;
  const c = audio();
  const data = await fetchRaw(id);
  if (!c || !data) return null;
  try {
    const b = await c.decodeAudioData(data.slice(0));
    buffers.set(id, b);
    return b;
  } catch {
    return null;
  }
}

const active = new Map<SoundId, { src: AudioBufferSourceNode; gain: GainNode }>();
const lastAt = new Map<SoundId, number>();

export function play(id: SoundId) {
  if (!on) return;
  const c = audio();
  if (!c || !master) return;
  // Один и тот же звук дважды за 0.4 с не играем (например, «Поражение» от боя и от экрана конца рейса).
  const now = performance.now();
  if (now - (lastAt.get(id) ?? -1e9) < 400) return;
  lastAt.set(id, now);
  if (c.state === 'suspended') void c.resume();
  const start = (buf: AudioBuffer) => {
    const src = c.createBufferSource();
    const gain = c.createGain();
    src.buffer = buf;
    src.connect(gain);
    gain.connect(master!);
    src.onended = () => { if (active.get(id)?.src === src) active.delete(id); };
    active.set(id, { src, gain });
    src.start();
  };
  const b = buffers.get(id);
  if (b) start(b);
  else void decode(id).then((buf) => { if (buf && on) start(buf); });
}

/** Плавно оборвать длинный звук (например, вступление эпизода, если нажали «Дальше»). */
export function stop(id: SoundId) {
  const a = active.get(id);
  if (!a || !ctx) return;
  active.delete(id);
  a.gain.gain.setTargetAtTime(0, ctx.currentTime, 0.04);
  setTimeout(() => { try { a.src.stop(); } catch { /* уже закончился */ } }, 250);
}

/** Те же звуки, но чуть позже: чтобы смена экрана звучала после щелчка нажатой кнопки. */
export function playLater(id: SoundId, ms = 90) {
  setTimeout(() => play(id), ms);
}

function soundFor(btn: HTMLElement): SoundId {
  const forced = btn.dataset.snd as SoundId | 'none' | undefined;
  if (forced) return forced === 'none' ? ('none' as SoundId) : forced;
  if (btn.classList.contains('close')) return btn.closest('.sheet') ? ('none' as SoundId) : 'btn-close';
  if (btn.classList.contains('primary')) return 'btn-main';
  if (btn.classList.contains('ghost')) return 'btn-back';
  if (btn.classList.contains('scale')) return 'scale';
  if (btn.classList.contains('slot-head')) return 'slot-open';
  return 'btn';
}

/** Один обработчик на всё приложение: звук выбирается по кнопке (data-snd или её класс). */
export function initSound() {
  // Файлы подтягиваем сразу, чтобы первое нажатие не ждало сеть.
  for (const id of SOUND_IDS) void fetchRaw(id);
  const wake = () => { audio(); if (ctx?.state === 'suspended') void ctx.resume(); for (const id of SOUND_IDS) void decode(id); };
  document.addEventListener('pointerdown', wake, { once: true, capture: true });

  document.addEventListener('click', (e) => {
    const btn = (e.target as HTMLElement | null)?.closest('button');
    if (!btn || (btn as HTMLButtonElement).disabled) return;
    const id = soundFor(btn);
    if ((id as string) !== 'none') play(id);
  }, true);

  // Недоступные кнопки (disabled) не дают click, поэтому ловим касание.
  document.addEventListener('pointerdown', (e) => {
    const btn = (e.target as HTMLElement | null)?.closest('button');
    if (btn && (btn as HTMLButtonElement).disabled && btn.dataset.snd !== 'none') play('btn-denied');
  }, true);
}
