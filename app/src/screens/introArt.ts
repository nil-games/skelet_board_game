// Графика стартового экрана: вода из трёх слоёв и обломанная доска под название.
// Всё рисуется кодом, без картинок, чтобы не зависеть от разрешения экрана.

const TAU = Math.PI * 2;
export const ART_SHARE = 0.64; // доля высоты экрана под картинку; на этой высоте — вода и название

const C_TOP = [43, 78, 87];
const C_MID = [22, 41, 47];
const C_LOW = [9, 17, 20];
const rgba = (c: number[], a: number) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

/** Высота воды: основной гребень (сумма двух длинных волн разной скорости + общее «дыхание»). */
export function waveY(mid: number, x: number, t: number) {
  return mid + 4 * Math.sin(t * 0.55) + 7 * Math.sin((TAU * x) / 520 - t * 0.7) + 4 * Math.sin((TAU * x) / 310 + t * 0.45 + 1.3);
}
const backY = (mid: number, x: number, t: number) =>
  mid - 9 + 3 * Math.sin(t * 0.5 + 2) + 6 * Math.sin((TAU * x) / 430 - t * 0.5 + 2.2) + 3 * Math.sin((TAU * x) / 260 + t * 0.6);
const farY = (mid: number, x: number, t: number) =>
  mid - 19 + 2.5 * Math.sin(t * 0.4 + 4) + 5 * Math.sin((TAU * x) / 600 + t * 0.35 + 0.7) + 2.5 * Math.sin((TAU * x) / 220 - t * 0.5);
export const waveSlope = (mid: number, x: number, t: number) => (waveY(mid, x + 4, t) - waveY(mid, x - 4, t)) / 8;

const STEP = 5;
type F = (mid: number, x: number, t: number) => number;
function trace(c: CanvasRenderingContext2D, f: F, mid: number, w: number, t: number, dy = 0) {
  for (let x = 0; x <= w + STEP; x += STEP) {
    const y = f(mid, x, t) + dy;
    if (x) c.lineTo(x, y);
    else c.moveTo(0, y);
  }
}
function glowLine(c: CanvasRenderingContext2D, f: F, mid: number, w: number, t: number, blur: number, shadow: number, color: string, width: number) {
  c.save();
  c.beginPath();
  trace(c, f, mid, w, t);
  c.filter = `blur(${blur}px)`;
  c.shadowColor = 'rgba(120, 245, 225, .8)';
  c.shadowBlur = shadow;
  c.strokeStyle = color;
  c.lineWidth = width;
  c.lineCap = 'round';
  c.stroke();
  c.restore();
}

/** Кадр воды. w, h — размер холста в CSS-пикселях. */
export function drawWater(c: CanvasRenderingContext2D, w: number, h: number, t: number) {
  const mid = h * ART_SHARE;
  const mean = mid + 4 * Math.sin(t * 0.55);
  c.clearRect(0, 0, w, h);

  // низ картинки уходит в цвет воды; край дымки повторяет волну
  c.beginPath();
  trace(c, waveY, mid, w, t, -170);
  for (let x = Math.ceil(w / STEP) * STEP; x >= 0; x -= STEP) c.lineTo(x, waveY(mid, x, t) + 1);
  c.closePath();
  let g = c.createLinearGradient(0, mean - 170, 0, mean);
  g.addColorStop(0, rgba(C_TOP, 0));
  g.addColorStop(0.45, rgba(C_TOP, 0.3));
  g.addColorStop(0.8, rgba(C_TOP, 0.65));
  g.addColorStop(1, rgba(C_TOP, 0.8));
  c.fillStyle = g;
  c.fill();

  // дальний слой
  c.beginPath();
  trace(c, farY, mid, w, t);
  c.lineTo(w, h);
  c.lineTo(0, h);
  c.closePath();
  g = c.createLinearGradient(0, mean - 24, 0, mean + 10);
  g.addColorStop(0, 'rgba(80, 150, 155, .32)');
  g.addColorStop(1, 'rgba(43, 78, 87, .7)');
  c.fillStyle = g;
  c.fill();
  glowLine(c, farY, mid, w, t, 1.4, 8, 'rgba(150, 250, 235, .16)', 2);

  // средний слой
  c.beginPath();
  trace(c, backY, mid, w, t);
  c.lineTo(w, h);
  c.lineTo(0, h);
  c.closePath();
  g = c.createLinearGradient(0, mean - 14, 0, mean + 30);
  g.addColorStop(0, 'rgba(70, 140, 145, .55)');
  g.addColorStop(1, rgba(C_TOP, 0.9));
  c.fillStyle = g;
  c.fill();
  glowLine(c, backY, mid, w, t, 1.2, 10, 'rgba(150, 250, 235, .28)', 2.4);

  // передний слой: светлее у гребня, темнеет вниз
  c.beginPath();
  trace(c, waveY, mid, w, t);
  c.lineTo(w, h);
  c.lineTo(0, h);
  c.closePath();
  const span = Math.max(1, h - mean);
  g = c.createLinearGradient(0, mean - 12, 0, h);
  g.addColorStop(0, 'rgb(52, 96, 104)');
  g.addColorStop(Math.min(0.9, 28 / span), rgba(C_TOP, 1));
  g.addColorStop(Math.min(0.95, 130 / span), rgba(C_MID, 1));
  g.addColorStop(1, rgba(C_LOW, 1));
  c.fillStyle = g;
  c.fill();
  glowLine(c, waveY, mid, w, t, 1, 16, 'rgba(130, 250, 232, .55)', 3);
  glowLine(c, waveY, mid, w, t, 0.7, 0, 'rgba(225, 255, 250, .45)', 1.4);
}

// ---------------------------------------------------------------- доска
function rnd(seed: number) {
  let x = seed % 2147483647 || 1;
  return () => (x = (x * 16807) % 2147483647) / 2147483647;
}
/** Край облома сверху вниз: [глубина px, y %]. Дерево ломается вдоль волокон: щепы, ступеньки, сколы. */
function edge(r: () => number): [number, number][] {
  const pts: [number, number][] = [[r() * 5, 0]];
  let y = 0;
  while (y < 100) {
    const step = 9 + r() * 22;
    y = Math.min(100, y + step);
    const kind = r();
    if (kind < 0.35) {
      const base = 5 + r() * 6;
      pts.push([base, y - step * 0.8], [r() * 2, y - step * 0.55], [base + 2, y - step * 0.35]);
    } else if (kind < 0.7) {
      const d = r() * 11;
      pts.push([d, y - step * 0.6], [d + (r() - 0.5) * 4, y]);
    } else {
      pts.push([4 + r() * 10, y]);
    }
  }
  pts.push([r() * 6, 100]);
  return pts;
}
export function hashString(s: string) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619);
  return (h >>> 0) % 2147483646 + 1;
}
/** clip-path обломанной доски; один и тот же для одного названия. */
export function plankClip(seed: number) {
  const r = rnd(seed);
  const L = edge(r);
  const R = edge(r);
  const top: string[] = [];
  const bot: string[] = [];
  for (let i = 1; i < 6; i++) {
    top.push(`${((i * 100) / 6 + (r() - 0.5) * 6).toFixed(1)}% ${(r() * 3).toFixed(1)}px`);
    bot.push(`${(100 - (i * 100) / 6 + (r() - 0.5) * 6).toFixed(1)}% calc(100% - ${(r() * 3).toFixed(1)}px)`);
  }
  const pts = [
    ...top,
    ...R.map(([d, y]) => `calc(100% - ${d.toFixed(1)}px) ${y.toFixed(1)}%`),
    ...bot,
    ...L.slice().reverse().map(([d, y]) => `${d.toFixed(1)}px ${y.toFixed(1)}%`),
  ];
  return `polygon(${pts.join(', ')})`;
}

/** Ширина блока по самой длинной строке (после переноса блок иначе берёт всю доступную ширину). */
export function fitToLines(el: HTMLElement) {
  el.style.width = '';
  const r = document.createRange();
  r.selectNodeContents(el);
  const lines = new Map<number, [number, number]>();
  for (const rc of r.getClientRects()) {
    const k = Math.round(rc.top);
    const cur = lines.get(k);
    lines.set(k, cur ? [Math.min(cur[0], rc.left), Math.max(cur[1], rc.right)] : [rc.left, rc.right]);
  }
  let w = 0;
  for (const [a, b] of lines.values()) w = Math.max(w, b - a);
  if (w) el.style.width = Math.ceil(w + 2) + 'px';
}
