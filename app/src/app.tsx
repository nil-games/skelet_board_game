import { useEffect, useRef, useState } from 'preact/hooks';
import { eventById, loadData, type GameData } from './data';
import * as E from './engine/game';
import type { Game } from './engine/game';
import { downloadJson, store, type Saved } from './store';
import { Icon, ResultCard, Sheet, ShipBar, SettingsList } from './ui';
import { playLater } from './sound';
import { Episode } from './screens/Episode';
import { Journal } from './screens/Journal';
import { ItemsRef, Reference } from './screens/Reference';
import { Home, Setup } from './screens/Setup';
import { Intro } from './screens/Intro';
import { After, BattleView, Flashback, MapStep } from './screens/Steps';

const encounterIds: Record<string, string> = { B1: 'gull', B2: 'galley', B3: 'queen' };
interface BoardResult {
  hull: number; team: number; rum: number; murmur: number; log: string[];
  crew: { n: string; loot: number; luck: number; startLoot: number; startLuck: number; bless: boolean }[];
}

type View = 'home' | 'setup' | 'game';

export function App() {
  const [d, setD] = useState<GameData | null>(null);
  const [loadErr, setLoadErr] = useState<string | null>(null);
  const [g, setG] = useState<Game | null>(() => store.loadCurrent());
  const [hist, setHist] = useState<Game[]>(() => store.loadHistory());
  const [view, setView] = useState<View>('home');
  const [sheet, setSheet] = useState<null | 'ref' | 'items' | 'journal' | 'menu'>(null);
  const [saves, setSaves] = useState<Saved[]>(() => store.listSaves());

  useEffect(() => { loadData().then(setD, (e) => setLoadErr(String(e))); }, []);
  useEffect(() => { store.saveCurrent(g, hist); }, [g, hist]);

  // Звуки смены экранов, шторок и событий партии (нажатия кнопок озвучены в sound.ts).
  const prevScreen = useRef('');
  const prevSheet = useRef<typeof sheet>(null);
  const prevM = useRef<number | null>(g?.ship.M ?? null);
  const prevBattle = useRef(g?.battle?.result ?? null);
  const quiet = useRef<Game | null>(null); // состояние, после которого Ропот молчит (отмена, ручная правка)
  useEffect(() => {
    const key = view === 'game' && g ? `${g.step}|${g.scene?.intro ? 'i' : ''}` : view;
    const prev = prevScreen.current;
    prevScreen.current = key;
    if (!prev || prev === key) return;
    if (view !== 'game' || !g) { playLater('step'); return; }
    if (g.step === 'over') { playLater(g.over?.win ? 'win' : 'lose', 150); return; }
    if (g.step === 'map') { playLater('map'); return; }
    if (g.scene?.intro || g.step === 'battle') return; // вступление играет само, бой звучит с кнопки «К бою!»
    if (prev.startsWith('plan') && g.step === 'actions') return; // уже звучат кубики
    playLater('step');
  }, [view, g?.step, g?.scene?.intro]);
  useEffect(() => {
    if (sheet && !prevSheet.current) playLater('sheet-open', 30);
    else if (!sheet && prevSheet.current) playLater('sheet-close', 30);
    prevSheet.current = sheet;
  }, [sheet]);
  useEffect(() => {
    const m = g?.ship.M ?? null;
    if (prevM.current !== null && m !== null && m > prevM.current && quiet.current !== g) playLater('murmur', 150);
    prevM.current = m;
  }, [g]);
  useEffect(() => {
    const r = g?.battle?.result ?? null;
    if (r && r !== prevBattle.current) playLater(r === 'lose' ? 'lose' : 'win', 200);
    prevBattle.current = r;
  }, [g?.battle?.result]);

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
    quiet.current = hist[hist.length - 1];
    setG(hist[hist.length - 1]);
    setHist(hist.slice(0, -1));
  };
  const startGame = (ng: Game) => { quiet.current = ng; setG(ng); setHist([]); setView('game'); setSheet(null); };

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
            startGame(E.newGame(d, cfg));
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

  if (g.step === 'battle-prep' && g.scene && !missing) {
    const scene = g.scene;
    return <iframe title="Морской бой" src="./combat.html" style={{width:'100%', height:'100dvh', border:0}} onLoad={(ev) => {
      const frame = ev.currentTarget.contentWindow as (Window & { mountCampaign: (options: object) => void });
      frame.mountCampaign({
        enemy: encounterIds[scene.eventId], players: g.players, ship: g.ship, saved: scene.board,
        save: (board: string) => setG(current => current?.scene && current.scene.eventId === scene.eventId
          ? { ...current, scene: { ...current.scene, board } } : current),
        finish: (result: BoardResult) => {
          const ship = { ...g.ship, H: Math.max(0,result.hull), C: result.team, R: result.rum, M: result.murmur };
          const entries = [...result.log].reverse().map(text => ({round:g.round,text}));
          const notes = result.crew.map(c => c.n + ' · Сокровища ' + (c.loot-c.startLoot) + ', Удача ' + (c.luck-c.startLuck) + (c.bless ? ', Благословение' : ''));
          const next = E.endRound({ ...g, ship, scene: {...scene, board:undefined}, log:[...g.log,...entries,{round:g.round,text:notes.join(' / ')}] }, d);
          act(() => ({...next, last:{title:'Отметьте на листах скелетов',text:'Изменения за бой',personal:{},ship:next.last?.ship ?? {},notes:[...notes,...(next.last?.notes ?? [])]}}));
        }
      });
    }} />;
  }

  return (
    <main class="game">
      <header class="top">
        <ShipBar ship={g.ship} onAdjust={(k, dl) => act((x) => (quiet.current = E.adjust(x, k, dl)))} />
        <nav>
          <button data-snd="undo" onClick={undo} disabled={!hist.length} title="Отменить последний шаг">↶ Отмена</button>
          <span class="round">Раунд {g.round}</span>
          <button data-snd="none" onClick={() => setSheet('ref')} aria-label="Правила">📖</button>
          <button data-snd="none" onClick={() => setSheet('items')} aria-label="Предметы и товары"><Icon k="gear" size={20} title="Предметы" /></button>
          <button data-snd="none" onClick={() => setSheet('journal')} aria-label="Судовой журнал">📜</button>
          <button data-snd="none" onClick={() => setSheet('menu')} aria-label="Меню">☰</button>
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

      {g.step === 'battle' && g.battle && <BattleView g={g} d={d} onTurn={(t) => act((x) => E.battleTurn(x, d, t))} onFinish={() => act((x) => E.finishBattle(x, d))} />}
      {g.step === 'flashback' && <Flashback g={g} onChoice={(p, c) => act((x) => E.flashbackChoice(x, d, p, c))} onDone={() => act(E.finishFlashback)} />}
      {g.step === 'after' && <After g={g} d={d} onNext={(n) => act((x) => E.goNext(x, n))} onSpend={(k) => act((x) => E.spendRum(x, d, k))} />}
      {g.step === 'over' && g.over && (
        <section class={'over ' + (g.over.win ? 'win' : 'lose')}>
          <h2>{g.over.win ? 'Победа!' : 'Конец рейса'}</h2>
          <p class="big">{g.over.reason}</p>
          {g.over.win && <p>Каждый читает концовку по числу пережитых Искр: 5 — Упокоился, 3–4 — Остался, 0–2 — Развеялся. Начинает самый славный.</p>}
          {!g.over.win && hist.length > 0 && <button class="wide" data-snd="undo" onClick={undo}>↶ Ошиблись вводом? Отменить шаг</button>}
          {g.over.win && g.scene?.kind === 'port' && <button class="wide" onClick={() => act(E.continueAfterWin)}>Играть дальше в порту</button>}
          <button class="primary wide" onClick={() => setView('setup')}>Новая партия</button>
        </section>
      )}

      {sheet === 'ref' && <Sheet title="Правила" onClose={() => setSheet(null)}><Reference d={d} /></Sheet>}
      {sheet === 'items' && <Sheet title="Предметы и товары" onClose={() => setSheet(null)}><ItemsRef d={d} /></Sheet>}
      {sheet === 'journal' && <Sheet title="Судовой журнал" onClose={() => setSheet(null)}><Journal g={g} onSet={(r, v) => act((x) => E.setJournal(x, r, v))} /></Sheet>}
      {sheet === 'menu' && (
        <Sheet title={`«${g.shipName}»`} onClose={() => setSheet(null)}>
          <SettingsList />
          <button class="wide" data-snd="save" onClick={() => { store.putSave(g); setSaves(store.listSaves()); alert('Сохранено на этом телефоне.'); }}>Сохранить в список</button>
          <button class="wide" data-snd="save" onClick={() => downloadJson(`партия-${g.shipName}-р${g.round}.json`, g)}>Сохранить в файл</button>
          {g.step !== 'map' && g.step !== 'over' && <button class="wide" onClick={() => { if (confirm('Бросить эпизод и вернуться на карту?')) { act((x) => ({ ...x, scene: null, battle: null, step: 'map', last: null })); setSheet(null); } }}>Вернуться на карту</button>}
          <button class="wide" onClick={() => { setView('home'); setSheet(null); }}>Главное меню</button>
        <p class="ver">контент {d.version} · сохранение {g.contentVersion}</p>
        </Sheet>
      )}
    </main>
  );
}
