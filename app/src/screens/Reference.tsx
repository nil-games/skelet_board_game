import { useState } from 'preact/hooks';
import type { Eff, GameData } from '../data';
import { Icon } from '../ui';

// корабельные товары: нажатие меняет шкалы (монеты игроки списывают на листах сами)
const SHIP_GOODS: Record<string, Eff> = {
  'Курочка по-карибски': { R: 1 }, 'Зеваки': { C: 1 }, 'Ремонт судна': { H: 1 }, 'Песенник': { M: -2 },
  'Бочка рома': { R: 4 }, 'Большой ремонт': { H: 4 }, 'Знахарь': { M: -3 }, 'Вербовщик': { C: 2 },
};

export function CatchTable({ d }: { d: GameData }) {
  return (
    <table class="tbl">
      <thead><tr><th>d6</th>{d.catch.map((c) => <th key={c.key}>{c.name}</th>)}</tr></thead>
      <tbody>
        {['1–2', '3–4', '5–6'].map((lab, i) => (
          <tr key={lab}><td>{lab}</td>{d.catch.map((c) => <td key={c.key}>{c.fish[i].name} ({c.fish[i].price})</td>)}</tr>
        ))}
      </tbody>
    </table>
  );
}

export function ShopRef({ d, onBuy }: { d: GameData; onBuy?: (name: string, eff: Eff) => void }) {
  return (
    <div class="shop">
      <p class="hint small">Наличие: на каждый столбец, кроме «Всегда в наличии», бросьте d6 — выпавший номер есть в продаже. Покупок сколько угодно, складчина разрешена.</p>
      {d.shop.map((col) => (
        <div key={col.col}>
          <h5>{col.col}</h5>
          <ol class="goods">
            {col.items.map((it) => (
              <li key={it.name}>
                <span class="price">{it.price}Д</span> <b>{it.name}</b> — {it.text}
                {onBuy && SHIP_GOODS[it.name] && <button class="buy" data-snd="buy" onClick={() => onBuy(it.name, SHIP_GOODS[it.name])}>купить</button>}
              </li>
            ))}
          </ol>
        </div>
      ))}
    </div>
  );
}

function TricksList({ d }: { d: GameData }) {
  return (
    <>
      <h5>Шуллерские штучки</h5>
      <p class="small">{d.casinoRule}</p>
      <ul class="goods">{d.casinoUpgrades.map((u) => <li key={u.name}><span class="price">{u.price}Д</span> <b>{u.name}</b> — {u.text}</li>)}</ul>
    </>
  );
}

export function CasinoRef({ d, withTricks = true }: { d: GameData; withTricks?: boolean }) {
  return (
    <div>
      <p class="small">Крэпс: два кубика. Первый бросок 7 или 11 — победа, 2, 3 или 12 — проигрыш, иначе число становится Целью; бросайте, пока не выпадет Цель (победа) или 7 (проигрыш).</p>
      <p class="small">{d.betRules}</p>
      <table class="tbl"><tbody>{d.bets.map((b, i) => <tr key={b.name}><td>№{i + 1}</td><td>{b.ratio}</td><td><b>{b.name}</b><br /><span class="small">{b.text}</span></td></tr>)}</tbody></table>
      {withTricks && <TricksList d={d} />}
    </div>
  );
}

const TABS = ['Основное', 'Бой', 'Игорный дом'] as const;

export function Reference({ d }: { d: GameData }) {
  const [tab, setTab] = useState<(typeof TABS)[number]>('Основное');
  return (
    <div>
      <div class="tabs">{TABS.map((t) => <button key={t} data-snd="tab" class={t === tab ? 'sel' : ''} onClick={() => setTab(t)}>{t}</button>)}</div>
      {tab === 'Основное' && (
        <div class="ref">
          <h5>Проверка</h5>
          <p>Выбрав слот с проверкой, закрасьте +1 к навыку. Бросок d6 + навык + Снаряжение (+2). Исходы: <b>≤3 · 4–6 · 7–9 · 10+</b> (у части действий ≤3 · 4–6 · 7+). Удача: 1 = 1 переброс. Благословение: 2 кубика, худший; Проклятие: 2 кубика, лучший.</p>
          <h5>Навыки</h5>
          <ul class="skills">{Object.entries(d.skills).map(([k, n]) => <li key={k}><Icon k={k} /> {n}</li>)}</ul>
          <h5>Шкалы корабля</h5>
          <p>Корпус 0 — затонули. Команда 0 — разошлась. Ропот ≥ Команды — бунт. Все шкалы 0–10.</p>
          <h5>Жажда (Раздача рома)</h5>
          <table class="tbl"><tbody>
            <tr><td>Команда</td>{d.thirst.map((t) => <td key={t.crewFrom}>{t.crewFrom}–{t.crewTo}</td>)}</tr>
            <tr><td>Жажда</td>{d.thirst.map((t) => <td key={t.crewFrom}>{t.rum}</td>)}</tr>
          </tbody></table>
          <p>Налить всем: Ром −Жажда, Ропот −1. Зажать: Ропот +1. Пустить к бочке: Ром −(Жажда+2), Слава +2 выбравшему.</p>
          <h5>Конец раунда</h5>
          <p>Пустые ⚠ слоты — штраф. Ром 0 — трезвая тоска, Ропот +1. Цикл, корабль не ушёл — новый круг (Ропот +1, в шторме ещё Корпус −1). По желанию при Роме &gt; 0: разведка за ром (−1, до 2 клеток) или «Полный вперёд» (−1, 2 линии).</p>
          <h5>Значки клеток (d6)</h5>
          <p>{d.terrains.map((t) => `${t.d6} ${t.sym} ${t.name}`).join(' · ')}</p>
        </div>
      )}
      {tab === 'Бой' && (
        <div class="ref">
          <p>Ходящий бросает 5 кубиков, один переброс любых (+1 за Удачу), раскладывает по станциям:</p>
          <ul>
            <li><b>Пушки</b> (пара+): 2→1 · 3→3 · 4→5 · 5→8 урона</li>
            <li><b>Таран</b> (стрит 3+): 3→2 · 4→4 · 5→6 урона</li>
            <li><b>Руль</b>: сумма ≥ S → залп врага мимо</li>
            <li><b>Трюм</b>: каждый кубик 1–2 → Корпус +1</li>
          </ul>
          <p>Навык станции ≥3 и станция сработала — эффект +1. Нанёс 3+ урона — Слава +1. Враг стреляет после каждого хода.</p>
        </div>
      )}
      {tab === 'Игорный дом' && <CasinoRef d={d} withTricks={false} />}
    </div>
  );
}

const cap = (t: string) => t.charAt(0) + t.slice(1).toLowerCase();

/** Справка по предметам: столбцы магазина, шуллерские штучки, рыба. */
export function ItemsRef({ d }: { d: GameData }) {
  const tabs = [...d.shop.map((c) => cap(c.col)), 'Штучки', 'Рыба'];
  const [tab, setTab] = useState(tabs[0]);
  const col = d.shop.find((c) => cap(c.col) === tab);
  return (
    <div>
      <div class="tabs">{tabs.map((t) => <button key={t} data-snd="tab" class={t === tab ? 'sel' : ''} onClick={() => setTab(t)}>{t}</button>)}</div>
      {col && (
        <>
          <p class="hint small">
            {col.col === 'ВСЕГДА В НАЛИЧИИ'
              ? 'Есть в любом магазине без ограничений.'
              : 'На этот столбец бросьте d6: выпавший номер есть в продаже, в одном экземпляре.'}
            {' '}Покупок сколько угодно, складчина разрешена. Продажа: половина цены, округлите вниз (не меньше 1).
          </p>
          <ol class="goods">
            {col.items.map((it) => (
              <li key={it.name}><span class="price">{it.price}Д</span> <b>{it.name}</b> — {it.text}</li>
            ))}
          </ol>
        </>
      )}
      {tab === 'Штучки' && <TricksList d={d} />}
      {tab === 'Рыба' && (
        <>
          <p class="small">{d.fishSlot.note}</p>
          <CatchTable d={d} />
          <p class="hint small">В скобках цена в монетах. Рыба лежит на корабле и продаётся в порту по правилам этого порта:</p>
          <ul class="goods">
            {Object.values(d.ports).map((p) => <li key={p.id}><b>{p.title}</b>: {p.fish ?? '—'}</li>)}
          </ul>
        </>
      )}
    </div>
  );
}
