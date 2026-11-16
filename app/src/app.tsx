import { useEffect, useState } from 'preact/hooks';
import { eventById, loadData, type GameData } from './data';
import * as E from './engine/game';
import type { Game } from './engine/game';
import { downloadJson, store, type Saved } from './store';
import { ResultCard, Sheet, ShipBar } from './ui';
import { Episode } from './screens/Episode';
import { Journal } from './screens/Journal';
import { Reference } from './screens/Reference';
import { Home, Setup } from './screens/Setup';
import { Intro } from './screens/Intro';
import { After, BattlePrep, BattleView, Flashback, MapStep } from './screens/Steps';

type View = 'home' | 'setup' | 'game';

export function App() {
  const [d, setD] = useState<GameData | null>(null);
  const [loadErr, setLoadErr] = useState<string | null>(null);
  const [g, setG] = useState<Game | null>(() => store.loadCurrent());
  const [hist, setHist] = useState<Game[]>(() => store.loadHistory());
  const [view, setView] = useState<View>('home');
  const [sheet, setSheet] = useState<null | 'ref' | 'journal' | 'menu'>(null);
  const [saves, setSaves] = useState<Saved[]>(() => store.listSaves());

  useEffect(() => { loadData().then(setD, (e) => setLoadErr(String(e))); }, []);
  useEffect(() => { store.saveCurrent(g, hist); }, [g, hist]);

  if (loadErr) return <main><p class="warn">{loadErr}</p></main>;
  if (!d) return <main><p class="hint">Загрузка…</p></main>;

  /** Действие с историей для отмены. */
  const act = (f: (g: Game) => Game) => {
    if (!g) return;
    const ng = f(g);
    if (ng === g) return;
    setHist([...hist, g].slice(-store.HIST_MAX));
    setG(ng);
  };
  const undo = () => {
    if (!hist.length) return;
    setG(hist[hist.length - 1]);
    setHist(hist.slice(0, -1));
  };
  const startGame = (ng: Game) => { setG(ng); setHist([]); setView('game'); setSheet(null); };

  if (view === 'home' || !g && view === 'game') {
    return (
      <main>
        <Home
          hasCurrent={!!g}
          saves={saves}
          onContinue={() => setView('game')}
          onNew={() => setView('setup')}
          onLoad={(s) => startGame(s.game)}
          onDelete={(id) => { store.deleteSave(id); setSaves(store.listSaves()); }}
          onImport={async (f) => {
            try { startGame(JSON.parse(await f.text()) as Game); } catch { alert('Это не файл сохранения.'); }
          }}
        />
        <p class="ver">контент {d.version}</p>
      </main>
    );
  }
  if (view === 'setup' || !g) {
    return (
      <main>
        <Setup
          onCancel={() => setView('home')}
          onStart={(cfg) => {
            if (g && !confirm('Начать новую партию? Текущая останется только если вы её сохранили.')) return;
            startGame({ ...E.newGame(d, cfg), timerOn: cfg.timerOn });
          }}
        />
      </main>
    );
  }

  const rng = Math.random;
  const stale = g.contentVersion !== d.version;
  const missing = g.scene && !eventById(d, g.scene.eventId) && !d.battles[g.scene.eventId];

  if (g.scene?.intro && !missing && (g.step === 'plan' || g.step === 'battle-prep')) {
    return <Intro g={g} d={d} onNext={() => act(E.closeIntro)} />;
  }

  return (
    <main class="game">
      <header class="top">
        <ShipBar ship={g.ship} onAdjust={(k, dl) => act((x) => E.adjust(x, k, dl))} />
        <nav>
          <button onClick={undo} disabled={!hist.length} title="Отменить последний шаг">↶ Отмена</button>
          <span class="round">Раунд {g.round}</span>
          <button onClick={() => setSheet('ref')} aria-label="Справка">📖</button>
          <button onClick={() => setSheet('journal')} aria-label="Судовой журнал">📜</button>
          <button onClick={() => setSheet('menu')} aria-label="Меню">☰</button>
        </nav>
      </header>

      {stale && <p class="note small">Тексты игры обновились после начала партии. Партия продолжается{missing ? ', но текущий эпизод удалён: отмените шаг или вернитесь на карту через меню' : ''}.</p>}
      {g.last && g.step !== 'over' && !(g.last.slot && g.step === 'actions') && <ResultCard r={g.last} onClose={() => setG({ ...g, last: null })} />}

      {g.step === 'map' && <MapStep g={g} d={d} onCell={(t) => act((x) => E.enterCell(x, d, t, rng))} onIsland={(no) => act((x) => E.enterIsland(x, d, no, rng))} />}
      {(g.step === 'plan' || g.step === 'actions') && g.scene && !missing && (
        <Episode
          g={g} d={d}
          onStart={() => act(E.startActions)}
          onTimeout={() => act((x) => E.planTimeout(x, d))}
          onPlay={(s, p, picks) => act((x) => E.playSlot(x, d, s, p, picks))}
          onEnd={() => act((x) => E.endRound(x, d))}
          onBuy={(n, eff) => act((x) => E.buyShip(x, d, n, eff))}
          onCloseResult={() => setG({ ...g, last: null })}
        />
      )}
      {g.step === 'battle-prep' && <BattlePrep g={g} d={d} onStart={(u) => act((x) => E.startBattle(x, d, u))} />}
      {g.step === 'battle' && g.battle && <BattleView g={g} d={d} onTurn={(t) => act((x) => E.battleTurn(x, d, t))} onFinish={() => act((x) => E.finishBattle(x, d))} />}
      {g.step === 'flashback' && <Flashback g={g} onChoice={(p, c) => act((x) => E.flashbackChoice(x, d, p, c))} onDone={() => act(E.finishFlashback)} />}
      {g.step === 'after' && <After g={g} d={d} onNext={(n) => act((x) => E.goNext(x, n))} onSpend={(k) => act((x) => E.spendRum(x, d, k))} />}
      {g.step === 'over' && g.over && (
        <section class={'over ' + (g.over.win ? 'win' : 'lose')}>
          <h2>{g.over.win ? 'Победа!' : 'Конец рейса'}</h2>
          <p class="big">{g.over.reason}</p>
          {g.over.win && <p>Каждый читает концовку по числу пережитых Искр: 5 — Упокоился, 3–4 — Остался, 0–2 — Развеялся. Начинает самый славный.</p>}
          {!g.over.win && hist.length > 0 && <button class="wide" onClick={undo}>↶ Ошиблись вводом? Отменить шаг</button>}
          {g.over.win && g.scene?.kind === 'port' && <button class="wide" onClick={() => act(E.continueAfterWin)}>Играть дальше в порту</button>}
          <button class="primary wide" onClick={() => setView('setup')}>Новая партия</button>
        </section>
      )}

      {sheet === 'ref' && <Sheet title="Справка" onClose={() => setSheet(null)}><Reference d={d} /></Sheet>}
      {sheet === 'journal' && <Sheet title="Судовой журнал" onClose={() => setSheet(null)}><Journal g={g} onSet={(r, v) => act((x) => E.setJournal(x, r, v))} /></Sheet>}
      {sheet === 'menu' && (
        <Sheet title={`«${g.shipName}»`} onClose={() => setSheet(null)}>
          <label class="check"><input type="checkbox" checked={g.timerOn} onChange={() => setG({ ...g, timerOn: !g.timerOn })} /> Таймер планирования</label>
          <button class="wide" onClick={() => { store.putSave(g); setSaves(store.listSaves()); alert('Сохранено на этом телефоне.'); }}>Сохранить в список</button>
          <button class="wide" onClick={() => downloadJson(`партия-${g.shipName}-р${g.round}.json`, g)}>Сохранить в файл</button>
          {g.step !== 'map' && g.step !== 'over' && <button class="wide" onClick={() => { if (confirm('Бросить эпизод и вернуться на карту?')) { act((x) => ({ ...x, scene: null, battle: null, step: 'map', last: null })); setSheet(null); } }}>Вернуться на карту</button>}
          <button class="wide" onClick={() => { setView('home'); setSheet(null); }}>Главное меню</button>
          <p class="ver">контент {d.version} · сохранение {g.contentVersion}</p>
        </Sheet>
      )}
    </main>
  );
}
