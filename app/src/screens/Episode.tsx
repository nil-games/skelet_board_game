import { useEffect, useState } from 'preact/hooks';
import type { ComponentChildren } from 'preact';
import type { GameData, Slot } from '../data';
import { slotEntities } from '../engine/effects';
import { currentEvent, endPreview, slotState, type Game } from '../engine/game';
import { fmtEff } from '../engine/effects';
import { Entities, Icon, ResultCard } from '../ui';
import { CatchTable, ShopRef, CasinoRef } from './Reference';
import { play } from '../sound';

interface Props {
  g: Game;
  d: GameData;
  onStart: () => void;
  onTimeout: () => void;
  onPlay: (slot: number, pick: number, picks?: string[]) => void;
  onEnd: () => void;
  onBuy: (name: string, eff: Record<string, number>) => void;
  onCloseResult: () => void;
}

export function Episode({ g, d, onStart, onTimeout, onPlay, onEnd, onBuy, onCloseResult }: Props) {
  const ev = currentEvent(g, d)!;
  const sc = g.scene!;
  const acting = g.step === 'actions';
  const [open, setOpen] = useState<number | null>(null);
  const [confirm, setConfirm] = useState(false);
  const [extra, setExtra] = useState<'shop' | 'casino' | null>(null);
  useEffect(() => { setOpen(null); setConfirm(false); }, [g.step, sc.circle, sc.eventId]);

  const isPort = sc.kind === 'port';
  const head = isPort ? `Порт · остров №${sc.island}` : sc.island ? `Остров №${sc.island}` : d.terrains.find((t) => t.key === sc.terrain)?.name;

  return (
    <section class="episode">
      <p class="kicker">{head}{ev.flow === 'loop' ? ` · цикл, круг ${sc.circle}` : ''}{isPort && sc.circle > 1 ? ` · раунд ${sc.circle}` : ''}</p>
      <h2>{ev.title}</h2>
      {ev.warn && <p class="warn">⚠ {ev.warn}</p>}
      {isPort && ev.fish && <p class="note">Рыба здесь: {ev.fish}.</p>}

      {!acting && <Planning g={g} onStart={onStart} onTimeout={onTimeout} />}

      <ol class="slots">
        {slotNumbers(isPort, ev.slots).map((n) => {
          const s = ev.slots.find((x) => x.n === n);
          if (!s) return <li key={n} class="slot blocked"><div class="slot-head"><span class="num">{n}</span><span class="title">✗ заблокирован<span class="why">{n === 7 ? 'рыбалка только в штиль' : 'отметьте ✗ на буклете'}</span></span></div></li>;
          return (
            <SlotCard key={n} g={g} d={d} s={s} acting={acting} open={open === n} onToggle={() => setOpen(open === n ? null : n)}
              onPlay={(a, b, c) => { onPlay(a, b, c); if (!s.shared) setOpen(null); }}
              result={g.last?.slot === n && acting ? <ResultCard r={g.last} onClose={onCloseResult} /> : null} />
          );
        })}
        {isPort && (
          <>
            <li class={'slot shared' + (ev.shop ? '' : ' blocked')}>
              <button class="slot-head" disabled={!ev.shop} onClick={() => setExtra(extra === 'shop' ? null : 'shop')}>
                <span class="num">5</span><span class="title">Магазин</span>
                {!ev.shop && <span class="why">в этом порту нет</span>}
              </button>
              {g.last?.slot === 5 && acting && <div class="slot-result"><ResultCard r={g.last} onClose={onCloseResult} /></div>}
              {extra === 'shop' && <div class="slot-body"><ShopRef d={d} onBuy={acting ? onBuy : undefined} /></div>}
            </li>
            <li class={'slot shared' + (ev.casino ? '' : ' blocked')}>
              <button class="slot-head" data-snd="casino" disabled={!ev.casino} onClick={() => setExtra(extra === 'casino' ? null : 'casino')}>
                <span class="num">6</span><span class="title">Игорный дом</span>
                {!ev.casino && <span class="why">в этом порту нет</span>}
              </button>
              {extra === 'casino' && <div class="slot-body"><CasinoRef d={d} /></div>}
            </li>
          </>
        )}
      </ol>

      {acting && !confirm && <button class="primary wide" onClick={() => setConfirm(true)}>Завершить действия</button>}
      {acting && confirm && <EndConfirm g={g} d={d} onCancel={() => setConfirm(false)} onEnd={onEnd} />}
      {ev.endText && <p class="endtext"><b>В конце раунда:</b> {ev.endText}</p>}
    </section>
  );
}

function slotNumbers(isPort: boolean, slots: Slot[]): number[] {
  const max = isPort ? 4 : 7;
  const ns = new Set<number>(slots.map((s) => s.n));
  for (let i = 1; i <= max; i++) ns.add(i);
  return [...ns].sort((a, b) => a - b);
}

function Planning({ g, onStart, onTimeout }: { g: Game; onStart: () => void; onTimeout: () => void }) {
  const [left, setLeft] = useState<number | null>(null);
  useEffect(() => {
    if (left === null) return;
    if (left === 0) { play('timeout'); return; }
    play('tick');
    const t = setTimeout(() => setLeft(left - 1), 1000);
    return () => clearTimeout(t);
  }, [left]);
  return (
    <div class="planning">
      <p class="hint">Планирование: по убыванию Славы каждый ставит кубик на слот. Исходы не читаются до фазы действий.</p>
      {g.timerOn && (
        <div class="timer">
          {left === null && <button onClick={() => setLeft(60)}>⏱ Таймер 60 с</button>}
          {left !== null && left > 0 && <span class={'count' + (left <= 10 ? ' low' : '')}>{left}</span>}
          {left === 0 && <button class="bad" onClick={() => { onTimeout(); setLeft(null); }}>Время вышло: Ропот +1</button>}
          {left !== null && left > 0 && <button class="ghost" onClick={() => setLeft(null)}>стоп</button>}
        </div>
      )}
      <button class="primary wide" data-snd="dice" onClick={onStart}>Кубики расставлены → действия</button>
    </div>
  );
}

function SlotCard({ g, d, s, acting, open, onToggle, onPlay, result }: { g: Game; d: GameData; s: Slot; acting: boolean; open: boolean; onToggle: () => void; onPlay: Props['onPlay']; result: ComponentChildren }) {
  const st = slotState(g, s);
  const [picking, setPicking] = useState<{ idx: number; n: number; picks: string[] } | null>(null);
  const effs = [...s.outcomes.map((o) => o.eff), ...(s.choices ?? []).map((c) => c.eff), s.cost ?? {}];
  const disabled = !!st.blocked || st.excluded;
  const personalDone = !s.shared && st.plays > 0;
  const cls = ['slot', s.shared ? 'shared' : 'personal', disabled ? 'blocked' : '', st.plays ? 'played' : ''].join(' ');

  const choose = (idx: number) => {
    const eff = s.choices ? s.choices[idx].eff : s.outcomes[idx].eff;
    if (eff.pick) setPicking({ idx, n: eff.pick, picks: [] });
    else onPlay(s.n, idx);
  };
  const addPick = (k: string) => {
    if (!picking) return;
    const picks = [...picking.picks, k];
    if (picks.length >= picking.n) { setPicking(null); onPlay(s.n, picking.idx, picks); }
    else setPicking({ ...picking, picks });
  };

  return (
    <li class={cls}>
      <button class="slot-head" onClick={onToggle} disabled={!acting || disabled}>
        <span class="num">{s.n}</span>
        <span class="title">
          {s.title}
          <span class="marks">
            {st.mandatory && <b class="mand" title="обязательный">!</b>}
            {s.alarm && <b class="alarm" title={'если пуст: ' + s.alarm.text}>⚠</b>}
            {s.skill && <Icon k={s.skill} size={18} title={d.skills[s.skill]} />}
            <Entities keys={slotEntities(effs)} />
          </span>
          {st.blocked && <span class="why">✗ {st.blocked}</span>}
          {st.excluded && <span class="why">не разыгрывается в этом раунде</span>}
          {s.req && !st.blocked && <span class="why">нужно у кого-то: {s.req}</span>}
        </span>
        {st.plays > 0 && <span class="count">{s.shared ? '×' + st.plays : '✓'}</span>}
      </button>
      {result && <div class="slot-result">{result}</div>}
      {open && acting && !disabled && (
        <div class="slot-body">
          {s.note && <p class="note">{s.note}</p>}
          {s.cost && <p class="note">Сначала: {fmtEff(s.cost)}.</p>}
          {personalDone && <p class="note">Личный слот уже отыгран. Отыграть ещё раз, только если на нём правда второй кубик.</p>}
          {picking ? (
            <div class="picker">
              <p>Обломки: выберите {picking.n - picking.picks.length} из вариантов {picking.picks.length ? `(выбрано: ${picking.picks.map((k) => ({ R: 'Ром', T: 'Сокровища', H: 'Корпус' })[k]).join(', ')})` : ''}</p>
              <div class="row">
                <button data-snd="choice" onClick={() => addPick('R')}><Icon k="R" /> Ром +1</button>
                <button data-snd="choice" onClick={() => addPick('T')}><Icon k="T" /> Сокровища +1</button>
                <button data-snd="choice" onClick={() => addPick('H')}><Icon k="H" /> Корпус +1</button>
              </div>
              <button class="ghost" onClick={() => setPicking(null)}>отмена</button>
            </div>
          ) : s.choices ? (
            <div class="row">{s.choices.map((c, i) => <button key={i} data-snd="choice" onClick={() => choose(i)}>{c.label}</button>)}</div>
          ) : s.skill ? (
            <>
              <p class="hint">Бросок d6 + {d.skills[s.skill]} (+1 за прокачку перед проверкой, + Снаряжение) =</p>
              <div class="row tiers">{s.outcomes.map((o, i) => <button key={i} data-snd="choice" onClick={() => choose(i)}>{o.label}</button>)}</div>
            </>
          ) : (
            <button class="wide" data-snd="choice" onClick={() => choose(0)}>Выполнить</button>
          )}
          {s.n === 7 && <CatchTable d={d} />}
          <p class="hint small">{s.shared ? 'Общий слот: отыграйте каждый кубик по очереди (по убыванию Славы).' : 'Личный слот.'}</p>
        </div>
      )}
    </li>
  );
}

function EndConfirm({ g, d, onCancel, onEnd }: { g: Game; d: GameData; onCancel: () => void; onEnd: () => void }) {
  const items = endPreview(g, d);
  const ev = currentEvent(g, d)!;
  const loopStay = ev.flow === 'loop' && !g.scene!.shipLeft;
  return (
    <div class="confirm">
      <h4>Конец раунда</h4>
      {items.length === 0 && <p>Штрафов за пустые слоты нет.</p>}
      <ul>{items.map((it, i) => <li key={i}>{it.text}: <b>{fmtEff(it.eff)}</b></li>)}</ul>
      {ev.end.crewBelow.map((c, i) => <p key={i} class="note">Если Команда &lt; {c.n}: {fmtEff(c.eff)}.</p>)}
      {loopStay && ev.circle && <p class="note">Корабль не покинул клетку: новый круг ({fmtEff(ev.circle)}).</p>}
      {g.ship.R === 0 && <p class="note">Ром 0: трезвая тоска, Ропот +1.</p>}
      <p class="hint small">Пустыми считаются слоты, которые не нажимали. Всё верно?</p>
      <div class="row">
        <button class="ghost" onClick={onCancel}>Назад</button>
        <button class="primary" onClick={onEnd}>Подтвердить</button>
      </div>
    </div>
  );
}
