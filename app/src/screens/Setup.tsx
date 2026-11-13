import { useState } from 'preact/hooks';
import type { Player } from '../engine/game';
import type { Saved } from '../store';

const COLORS = [
  { c: '#c0392b', n: 'красный' }, { c: '#2c6fb7', n: 'синий' }, { c: '#2e8b57', n: 'зелёный' },
  { c: '#e1b12c', n: 'жёлтый' }, { c: '#f2efe6', n: 'белый' }, { c: '#222222', n: 'чёрный' },
];

export function Home({ hasCurrent, saves, onContinue, onNew, onLoad, onDelete, onImport }: {
  hasCurrent: boolean; saves: Saved[]; onContinue: () => void; onNew: () => void; onLoad: (s: Saved) => void; onDelete: (id: string) => void; onImport: (f: File) => void;
}) {
  return (
    <section class="home">
      <h1>Всем костям на борт!</h1>
      <p class="hint">Приложение лежит рядом с буклетом: книга эпизодов, планшет корабля и справочник.</p>
      {hasCurrent && <button class="primary wide" onClick={onContinue}>Продолжить партию</button>}
      <button class="wide" onClick={onNew}>Новая партия</button>
      {saves.length > 0 && (
        <>
          <h3>Сохранения</h3>
          <ul class="saves">
            {saves.map((s) => (
              <li key={s.id}>
                <button onClick={() => onLoad(s)}>{s.title}<small>{new Date(s.at).toLocaleString('ru-RU')}</small></button>
                <button class="ghost" onClick={() => confirm('Удалить сохранение?') && onDelete(s.id)} aria-label="Удалить">🗑</button>
              </li>
            ))}
          </ul>
        </>
      )}
      <label class="file">Загрузить из файла<input type="file" accept="application/json" onChange={(e) => { const f = (e.target as HTMLInputElement).files?.[0]; if (f) onImport(f); }} /></label>
    </section>
  );
}

export function Setup({ onStart, onCancel }: { onStart: (cfg: { shipName: string; players: Player[]; timerOn: boolean }) => void; onCancel: () => void }) {
  const [n, setN] = useState(4);
  const [ship, setShip] = useState('Блюющий скелет');
  const [timerOn, setTimerOn] = useState(true);
  const [players, setPlayers] = useState<Player[]>(COLORS.map((c, i) => ({ name: `Скелет ${i + 1}`, color: c.c })));
  const upd = (i: number, p: Partial<Player>) => setPlayers(players.map((x, j) => (j === i ? { ...x, ...p } : x)));
  return (
    <section>
      <h2>Новая партия</h2>
      <div class="field"><span>Режим</span>
        <select disabled><option>Свободное плавание</option></select>
      </div>
      <p class="hint small">Обучение и сценарии появятся позже. Свободное плавание: старт A4, порт назначения G3 — остров №1, Рыночный порт.</p>
      <div class="field"><span>Название корабля</span><input value={ship} onInput={(e) => setShip((e.target as HTMLInputElement).value)} /></div>
      <div class="field"><span>Скелетов на борту</span>
        <span class="seg">{[4, 5, 6].map((k) => <button key={k} class={k === n ? 'sel' : ''} onClick={() => setN(k)}>{k}</button>)}</span>
      </div>
      <p class="hint small">Игроков меньше четырёх — кто-то ведёт двух скелетов (на борту всегда минимум 4).</p>
      <h4>Скелеты (имя и цвет кубика)</h4>
      {players.slice(0, n).map((p, i) => (
        <div class="player-row" key={i}>
          <input value={p.name} onInput={(e) => upd(i, { name: (e.target as HTMLInputElement).value })} />
          <span class="colors">
            {COLORS.map((c) => (
              <button key={c.c} class={'dot' + (p.color === c.c ? ' sel' : '')} style={{ background: c.c }} title={c.n} aria-label={c.n} onClick={() => upd(i, { color: c.c })} />
            ))}
          </span>
        </div>
      ))}
      <label class="check"><input type="checkbox" checked={timerOn} onChange={() => setTimerOn(!timerOn)} /> Таймер планирования (60 с)</label>
      <div class="row">
        <button class="ghost" onClick={onCancel}>Назад</button>
        <button class="primary" onClick={() => onStart({ shipName: ship, players: players.slice(0, n).map((p, i) => ({ ...p, name: p.name.trim() || `Скелет ${i + 1}` })), timerOn })}>Отчалить</button>
      </div>
    </section>
  );
}
