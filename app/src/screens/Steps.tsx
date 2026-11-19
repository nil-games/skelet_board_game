import { useState } from 'preact/hooks';
import type { GameData } from '../data';
import { eventById } from '../data';
import { battleReward, battleSetup, nextOptions, type BattleUpgrades, type Game, type Next, type TurnInput } from '../engine/game';
import { Stepper } from '../ui';

export function MapStep({ g, d, onCell, onIsland }: { g: Game; d: GameData; onCell: (t: string) => void; onIsland: (no: number | null) => void }) {
  const sea = d.terrains.filter((t) => t.key !== 'i');
  return (
    <section>
      <h2>Карта</h2>
      <p class="hint">Где корабль закончил движение? Пустая клетка: бросьте d6 и нарисуйте значок ({d.terrains.map((t) => `${t.d6} ${t.sym}`).join(' · ')}).</p>
      <div class="grid2">
        {sea.map((t) => (
          <button key={t.key} class="cell" onClick={() => onCell(t.key)}><span class="sym">{t.sym}</span>{t.name}</button>
        ))}
      </div>
      <h3>△ Острова</h3>
      <div class="grid2">
        <button class="cell" onClick={() => onIsland(null)}><IslandMark no="?" />Новый остров</button>
        {g.islands.map((i) => (
          <button key={i.no} class="cell" onClick={() => onIsland(i.no)}>
            <IslandMark no={i.no} />{eventById(d, i.id)?.title}{g.mode === 'free' && i.no === 1 ? ' (цель)' : ''}
          </button>
        ))}
      </div>
      <h3>Сценарные клетки</h3>
      <p class="hint small">В свободном плавании их нет. Появятся вместе со сценариями.</p>
    </section>
  );
}

function IslandMark({ no }: { no: number | string }) {
  return (
    <svg class="isl" viewBox="0 0 40 34" width="40" height="34" aria-hidden="true">
      <path d="M20 2 L38 32 L2 32 Z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" />
      <text x="20" y="28" text-anchor="middle" font-size="14" font-weight="700" fill="currentColor">{no}</text>
    </svg>
  );
}

export function BattlePrep({ g, d, onStart }: { g: Game; d: GameData; onStart: (u: BattleUpgrades) => void }) {
  const b = d.battles[g.scene!.eventId];
  const s = battleSetup(d, b.id, g.players.length);
  const [up, setUp] = useState<BattleUpgrades>({ brander: false, shields: false, tooth: false });
  const tog = (k: keyof BattleUpgrades) => setUp({ ...up, [k]: !up[k] });
  return (
    <section>
      <p class="kicker">Корабль · бой · враг {b.cls}</p>
      <h2>{b.title}</h2>
      {b.warn && <p class="warn">⚠ {b.warn}</p>}
      {b.special && <p class="note"><b>Особенность:</b> {b.special}</p>}
      <div class="stats">
        <span>Корпус врага <b>{s.hull}</b></span><span>Урон <b>{s.dmg}</b></span><span>Руль S <b>{s.helm}</b></span>
      </div>
      <p class="hint">Награда: победа — Сокровища +{s.reward} каждому скелету, ничья — +{Math.floor(s.reward / 2)}. Переверните буклет на «Борт».</p>
      <h4>Улучшения на бой (если куплены)</h4>
      <label class="check"><input type="checkbox" checked={up.brander} onChange={() => tog('brander')} /> Брандер: враг сразу −1</label>
      <label class="check"><input type="checkbox" checked={up.shields} onChange={() => tog('shields')} /> Щиты: первый залп −1</label>
      <label class="check"><input type="checkbox" checked={up.tooth} onChange={() => tog('tooth')} /> Зуб кита (диковинка): враг −2</label>
      <p class="hint small">Смазка, Парусина, Медный нос, Смола учитывайте сами при подсчёте хода.</p>
      <button class="primary wide" data-snd="battle-start" onClick={() => onStart(up)}>К бою!</button>
    </section>
  );
}

export function BattleView({ g, d, onTurn, onFinish }: { g: Game; d: GameData; onTurn: (t: TurnInput) => void; onFinish: () => void }) {
  const b = g.battle!;
  const def = d.battles[b.id];
  const [t, setT] = useState<TurnInput>({ damage: 0, dodge: false, repair: 0 });
  const who = g.players[b.turn]?.name;
  return (
    <section>
      <p class="kicker">Бой · {def.title}</p>
      <div class="bars">
        <div><span>Враг</span><meter min={0} max={b.enemyMax} value={b.enemyHull} /><b>{b.enemyHull}/{b.enemyMax}</b></div>
        <div><span>Мы</span><meter min={0} max={10} value={g.ship.H} /><b>{g.ship.H}</b></div>
      </div>
      <p class="hint">Урон врага {b.dmg}{b.shields ? ' (первый залп −1: Щиты)' : ''}, Руль S = {b.helm}.</p>
      {!b.result ? (
        <div class="turn">
          <h3>Ход {b.turn + 1} из {b.turns}: {who}</h3>
          <p class="hint small">5 кубиков, 1 переброс, раскладка по станциям. Введите итог:</p>
          <div class="field"><span>Урон врагу (Пушки + Таран)</span><Stepper value={t.damage} onChange={(v) => setT({ ...t, damage: v })} /></div>
          <label class="check"><input type="checkbox" checked={t.dodge} onChange={() => setT({ ...t, dodge: !t.dodge })} /> Руль: сумма ≥ {b.helm} (залп мимо)</label>
          <div class="field"><span>Трюм: Корпус +</span><Stepper value={t.repair} max={5} onChange={(v) => setT({ ...t, repair: v })} /></div>
          <button class="primary wide" data-snd="hit" onClick={() => { onTurn(t); setT({ damage: 0, dodge: false, repair: 0 }); }}>Завершить ход</button>
        </div>
      ) : (
        <div class="turn">
          <h3>{b.result === 'win' ? 'Победа!' : b.result === 'draw' ? 'Ничья: враг отступил' : 'Поражение'}</h3>
          {b.result !== 'lose' && <p>Каждый скелет: Сокровища +{battleReward(g, d)}.</p>}
          <button class="primary wide" onClick={onFinish}>Дальше</button>
        </div>
      )}
      <ul class="blog">{b.log.slice().reverse().map((l, i) => <li key={i}>{l}</li>)}</ul>
    </section>
  );
}

export function Flashback({ g, onChoice, onDone }: { g: Game; onChoice: (player: string, c: 'pride' | 'shame') => void; onDone: () => void }) {
  const [done, setDone] = useState<string[]>([]);
  const [who, setWho] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  if (who) {
    return (
      <section class="private">
        {!ready ? (
          <>
            <h2>Передайте телефон</h2>
            <p class="big">{who}</p>
            <button class="primary wide" onClick={() => setReady(true)}>Я {who}, читаю</button>
            <button class="ghost wide" onClick={() => setWho(null)}>Назад</button>
          </>
        ) : (
          <>
            <h2>Воспоминание</h2>
            <p class="read">Искра вспыхивает, и вы вспоминаете обрывок прошлой жизни. (Истории пока не написаны: расскажите в 1–2 предложениях, как вы умерли или чего не закончили.)</p>
            <p>Что вы чувствуете?</p>
            <button class="wide" onClick={() => { onChoice(who, 'pride'); setDone([...done, who]); setWho(null); setReady(false); }}>Гордость — Ропот −1 кораблю</button>
            <button class="wide" onClick={() => { onChoice(who, 'shame'); setDone([...done, who]); setWho(null); setReady(false); }}>Стыд — Слава +1 себе</button>
          </>
        )}
      </section>
    );
  }
  return (
    <section>
      <h2>Воспоминания</h2>
      <p class="hint">У кого есть обведённая, но не пережитая Искра? Каждый такой скелет переживает флешбек.</p>
      <ul class="players">
        {g.players.map((p) => (
          <li key={p.name}>
            <span class="dot" style={{ background: p.color }} /> {p.name}
            {done.includes(p.name) ? <span class="ok">✓ пережито</span> : <button onClick={() => setWho(p.name)}>Вспомнить</button>}
          </li>
        ))}
      </ul>
      <button class="primary wide" onClick={onDone}>Дальше</button>
    </section>
  );
}

export function After({ g, d, onNext, onSpend }: { g: Game; d: GameData; onNext: (n: Next) => void; onSpend: (k: 'scout' | 'speed') => void }) {
  const opts = nextOptions(g, d);
  const canSpend = g.ship.R > 0;
  return (
    <section>
      <h2>Конец раунда</h2>
      <div class="row">
        <button data-snd="rum" disabled={!canSpend} onClick={() => onSpend('scout')}>Разведка за ром (Ром −1)</button>
        {opts.includes('leave') && <button data-snd="rum" disabled={!canSpend || g.fullSpeed} onClick={() => onSpend('speed')}>Полный вперёд (Ром −1)</button>}
      </div>
      {!canSpend && <p class="hint small">Ром 0: траты по желанию недоступны.</p>}
      {opts.includes('circle') && (
        <>
          <p class="note">Корабль не покинул клетку: следующий раунд — тот же эпизод, новый круг.</p>
          <button class="primary wide" onClick={() => onNext('circle')}>Новый круг</button>
        </>
      )}
      {opts.includes('port') && <button class="wide" onClick={() => onNext('port')}>Ещё раунд в порту</button>}
      {opts.includes('leave') && (
        <>
          <p class="note">{g.scene?.kind === 'port' ? 'Отплыть: проведите линию из порта в соседнюю клетку.' : `Корабль уходит: проведите ${g.fullSpeed ? '2 линии' : 'линию'} в соседнюю клетку (учитывайте разведку).`}</p>
          <button class="primary wide" onClick={() => onNext('leave')}>{g.scene?.kind === 'port' ? 'Отплыть' : 'На карту'}</button>
        </>
      )}
    </section>
  );
}
