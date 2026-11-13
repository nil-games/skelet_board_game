import type { ComponentChildren } from 'preact';
import { useState } from 'preact/hooks';
import type { Eff } from './data';
import { effName, fmtEff, SHIP_KEYS, type Ship, type ShipKey } from './engine/effects';
import type { Result } from './engine/game';

const ICON_KEY: Record<string, string> = { RT: 'R', catch: 'fish', mv: 'map', sc: 'map' };

export function Icon({ k, size = 20, title }: { k: string; size?: number; title?: string }) {
  if (k === 'S') return <span class="spark" title={title ?? 'Искры'} style={{ fontSize: size * 0.8 }}>✦</span>;
  const key = ICON_KEY[k] ?? k;
  return <img class="icon" src={`${import.meta.env.BASE_URL}icons/${key}.png`} width={size} height={size} alt={title ?? effName(k)} title={title ?? effName(k)} />;
}

export function Entities({ keys }: { keys: string[] }) {
  return (
    <span class="entities">
      {keys.map((k) => (k === 'pick' ? <span key={k}><Icon k="R" size={16} /><Icon k="T" size={16} /><Icon k="H" size={16} /></span> : <Icon key={k} k={k} size={16} />))}
    </span>
  );
}

export function ShipBar({ ship, onAdjust }: { ship: Ship; onAdjust: (k: ShipKey, d: number) => void }) {
  const [open, setOpen] = useState<ShipKey | null>(null);
  const danger = (k: ShipKey) => (k === 'M' ? ship.M >= ship.C - 1 : k === 'R' ? ship.R === 0 : ship[k] <= 2);
  return (
    <div class="shipbar">
      {SHIP_KEYS.map((k) => (
        <button key={k} class={'scale' + (danger(k) ? ' danger' : '') + (open === k ? ' sel' : '')} onClick={() => setOpen(open === k ? null : k)} aria-label={effName(k)}>
          <Icon k={k} size={22} />
          <b>{ship[k]}</b>
          <small>{effName(k)}</small>
        </button>
      ))}
      {open && (
        <div class="adjust">
          <span>Правка: {effName(open)}</span>
          <button onClick={() => onAdjust(open, -1)}>−1</button>
          <button onClick={() => onAdjust(open, +1)}>+1</button>
          <button class="ghost" onClick={() => setOpen(null)}>✓</button>
        </div>
      )}
    </div>
  );
}

export function EffLine({ eff, prefix }: { eff: Eff; prefix: string }) {
  const t = fmtEff(eff);
  if (!t) return null;
  return <p class="effline"><span>{prefix}</span> {t}</p>;
}

export function ResultCard({ r, onClose }: { r: Result; onClose: () => void }) {
  return (
    <div class="result" role="status">
      <button class="close" onClick={onClose} aria-label="Закрыть">×</button>
      <h4>{r.title}</h4>
      {r.text && <p class="read">{r.text}</p>}
      <EffLine eff={r.ship} prefix="Корабль:" />
      <EffLine eff={r.personal} prefix="Запишите себе:" />
      {r.notes.map((n, i) => <p key={i} class="note">{n}</p>)}
    </div>
  );
}

export function Sheet({ title, onClose, children }: { title: string; onClose: () => void; children: ComponentChildren }) {
  return (
    <div class="sheet-bg" onClick={onClose}>
      <div class="sheet" onClick={(e) => e.stopPropagation()}>
        <header><h3>{title}</h3><button class="close" onClick={onClose} aria-label="Закрыть">×</button></header>
        <div class="sheet-body">{children}</div>
      </div>
    </div>
  );
}

export function Stepper({ value, onChange, min = 0, max = 30 }: { value: number; onChange: (v: number) => void; min?: number; max?: number }) {
  return (
    <span class="stepper">
      <button onClick={() => onChange(Math.max(min, value - 1))}>−</button>
      <b>{value}</b>
      <button onClick={() => onChange(Math.min(max, value + 1))}>+</button>
    </span>
  );
}
