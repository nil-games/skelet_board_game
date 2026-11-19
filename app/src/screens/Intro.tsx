import { useEffect, useLayoutEffect, useRef } from 'preact/hooks';
import { play, stop } from '../sound';
import type { GameData } from '../data';
import { eventById } from '../data';
import type { Game } from '../engine/game';
import { ART_SHARE, drawWater, fitToLines, hashString, plankClip, waveSlope, waveY } from './introArt';

/** Стартовый экран эпизода: картинка, вода с волной, название на обломке палубной доски, описание, компас «дальше». */
export function Intro({ g, d, onNext }: { g: Game; d: GameData; onNext: () => void }) {
  const sc = g.scene!;
  const ev = eventById(d, sc.eventId) ?? d.battles[sc.eventId];
  const rootRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const h2Ref = useRef<HTMLHeadingElement>(null);
  const btnRef = useRef<HTMLButtonElement>(null);

  // доска по ширине строк — после загрузки шрифта и при повороте экрана
  useLayoutEffect(() => {
    const h = h2Ref.current;
    if (!h) return;
    const fit = () => fitToLines(h);
    fit();
    document.fonts?.ready.then(fit);
    window.addEventListener('resize', fit);
    return () => window.removeEventListener('resize', fit);
  }, [sc.eventId]);

  // звук вступления: играет, пока экран открыт; «Дальше» плавно обрывает его
  useEffect(() => { play('intro'); return () => stop('intro'); }, [sc.eventId]);

  // вода: анимация; при «уменьшить движение» — один неподвижный кадр
  useEffect(() => {
    const cv = canvasRef.current;
    const root = rootRef.current;
    if (!cv || !root) return;
    const ctx = cv.getContext('2d');
    if (!ctx) return;
    let w = 0;
    let h = 0;
    const resize = () => {
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      w = root.clientWidth;
      h = root.clientHeight;
      cv.width = Math.round(w * dpr);
      cv.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(root);
    const still = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    let raf = 0;
    const frame = (ms: number) => {
      const t = ms / 1000;
      drawWater(ctx, w, h, t);
      const mid = h * ART_SHARE;
      const xt = w * 0.42;
      const xb = w - 45;
      const yt = waveY(mid, xt, t) - mid;
      const yb = waveY(mid, xb, t) - mid;
      const at = (Math.atan(waveSlope(mid, xt, t)) * 180) / Math.PI;
      const ab = (Math.atan(waveSlope(mid, xb, t)) * 180) / Math.PI;
      if (titleRef.current) titleRef.current.style.transform = `translateY(calc(-50% + ${(yt * 0.85).toFixed(2)}px)) rotate(${(at * 0.7 - 1).toFixed(2)}deg)`;
      if (btnRef.current) btnRef.current.style.transform = `translateY(calc(-50% + ${(yb * 0.85).toFixed(2)}px)) rotate(${(ab * 1.2).toFixed(2)}deg)`;
      if (!still) raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); ro.disconnect(); };
  }, [sc.eventId]);

  if (!ev) return null;
  const terrain = d.terrains.find((t) => t.key === sc.terrain);
  const kicker = sc.kind === 'port' ? `Порт · остров №${sc.island}` : sc.kind === 'battle' ? 'Бой' : sc.island ? `Остров №${sc.island}` : terrain?.name;
  const long = ev.title.length > 24;
  return (
    <div class="intro" ref={rootRef}>
      {ev.image ? (
        <img class="intro-img" src={import.meta.env.BASE_URL + ev.image} alt="" />
      ) : (
        <div class="intro-noart" aria-hidden="true">{sc.kind === 'port' || sc.island ? '△' : terrain?.sym}</div>
      )}
      <canvas class="intro-water" ref={canvasRef} aria-hidden="true" />
      {kicker && <span class="intro-kicker">{kicker}</span>}
      <div class="intro-title" ref={titleRef}>
        <div class={'intro-plank' + (long ? ' long' : '')} style={{ '--clip': plankClip(hashString(ev.id + ev.title)) }}>
          <h2 ref={h2Ref}>{ev.title.replace(/-/g, '‑')}</h2>
        </div>
      </div>
      <div class="intro-body"><p>{ev.flavor}</p></div>
      <button class="intro-next" data-snd="intro-next" ref={btnRef} onClick={onNext} aria-label="Дальше">
        <CompassIcon />
      </button>
    </div>
  );
}

/** Временный компас: потом заменить на свою картинку (стрелку лучше отдельным слоем). */
function CompassIcon() {
  return (
    <svg viewBox="0 0 100 100" aria-hidden="true">
      <circle cx="50" cy="50" r="46" fill="#c9963a" stroke="#0b0806" stroke-width="3.2" />
      <circle cx="50" cy="50" r="38.5" fill="#152a30" stroke="#0b0806" stroke-width="2.6" />
      <path d="M50 17 L54 46 L83 50 L54 54 L50 83 L46 54 L17 50 L46 46 Z" fill="rgba(226, 182, 94, .22)" stroke="rgba(226, 182, 94, .45)" stroke-width="1" />
      <path d="M42 50 L50 40.5 L89 50 L50 59.5 Z" fill="#c81d0e" stroke="#0b0806" stroke-width="2.4" stroke-linejoin="round" />
      <circle cx="50" cy="50" r="5.2" fill="#e8c06a" stroke="#0b0806" stroke-width="2" />
    </svg>
  );
}
