import type { GameData } from '../data';
import { eventById } from '../data';
import type { Game } from '../engine/game';

/** Стартовый экран эпизода: картинка ~2/3 экрана, название в рамке на стыке, описание (со скроллом), стрелка «дальше». */
export function Intro({ g, d, onNext }: { g: Game; d: GameData; onNext: () => void }) {
  const sc = g.scene!;
  const ev = eventById(d, sc.eventId) ?? d.battles[sc.eventId];
  if (!ev) return null;
  const terrain = d.terrains.find((t) => t.key === sc.terrain);
  const kicker = sc.kind === 'port' ? `Порт · остров №${sc.island}` : sc.kind === 'battle' ? 'Бой' : sc.island ? `Остров №${sc.island}` : terrain?.name;
  return (
    <div class="intro">
      <div class="intro-art">
        {ev.image ? (
          <img src={import.meta.env.BASE_URL + ev.image} alt="" />
        ) : (
          <div class="intro-noart" aria-hidden="true">{sc.kind === 'port' || sc.island ? '△' : terrain?.sym}</div>
        )}
        {kicker && <span class="intro-kicker">{kicker}</span>}
      </div>
      <div class="intro-text">
        <h2 class="intro-title"><span>{ev.title.replace(/-/g, '‑')}</span></h2>
        <button class="intro-next" onClick={onNext} aria-label="Дальше" />
        <div class="intro-body">
          <p>{ev.flavor}</p>
        </div>
      </div>
    </div>
  );
}
