import { useEffect } from 'preact/hooks';
import enemies from '../engine/board.json';
import { endRound, type Game } from '../engine/game';
import { defeat } from '../engine/effects';
import type { GameData } from '../data';

interface Cell {
  s: number; n: string; k: string; v: number; amt?: number; hidden?: number | boolean;
  fly?: number; dodge?: number; thorns?: number; chain?: string; esc?: number;
}
interface Enemy { n: string; cls: string; base: number; chargeDmg: number; bribe: number; intents: (string | number)[][]; cells: Cell[] }
interface Board {
  version: 1; status: string; turn: number; round: number; closed: number[];
  charge: number; intent: string; skip: boolean; rage: boolean; note: string;
}
const kinds: Record<string,string> = {heart:'Жизнь', armor:'Броня', shield:'Щит', dmg:'Урон', fire:'Пожар', loot:'Добыча', weak:'Слабое место', prisoner:'Пленник', holy:'Святая вода', mast:'Мачта'};
const outcomes: Record<string,string> = {win:'Победа', draw:'Враг ушёл', bribed:'Откупились', escaped:'Сбежали', lose:'Поражение'};
function rollIntent(enemy: Enemy) {
  let roll = Math.random() * enemy.intents.reduce((sum, [,weight]) => sum + Number(weight), 0);
  return String(enemy.intents.find(([,weight]) => (roll -= Number(weight)) < 0)![0]);
}
function initial(): Board {
  return {version:1,status:'pre',turn:0,round:1,closed:[],charge:0,intent:'',skip:false,rage:false,note:''};
}

export function BoardEncounter({g,d,onChange}: {g:Game; d:GameData; onChange:(game:Game)=>void}) {
  const scene = g.scene!;
  const enemy: Enemy = enemies[scene.eventId as keyof typeof enemies];
  const saved = scene.board ? JSON.parse(scene.board) : initial();
  // Ранее состояние боя содержало также цифровые кубики и отдельные шкалы корабля.
  useEffect(() => {
    if (saved.version === 1) return;
    const board: Board = {...initial(), status:saved.status === 'loss' ? saved.pendingLoss : saved.status,
      turn:saved.turn,round:saved.round,charge:saved.charge,intent:saved.intent,skip:!!saved.t?.skip,
      closed:saved.cells.filter((c: Cell & {closed:boolean})=>c.closed).map((c:Cell)=>c.s),
      rage:saved.cells.some((c:Cell)=>enemy.cells.some(original=>original.s===c.s && original.hidden) && !c.hidden),
      note:saved.crew.map((c:{n:string;loot:number;startLoot:number;luck:number;startLuck:number;bless:boolean})=>
        c.n+' · изменение Сокровищ '+(c.loot-c.startLoot)+', Удачи '+(c.luck-c.startLuck)+(c.bless?', Благословение':'')).join(' / ')};
    onChange({...g, ship:{...g.ship,H:Math.max(0,saved.hull),R:saved.rum,C:saved.team,M:saved.murmur},scene:{...scene,board:JSON.stringify(board)}});
  }, [scene.board]);
  if (saved.version !== 1) return null;
  const b: Board = saved;
  const ship = {...g.ship};
  const who = g.players[b.turn].name;
  const open = (c:Cell) => (!c.hidden || b.rage) && !b.closed.includes(c.s);
  const active = (kind:string) => enemy.cells.filter(c=>c.k===kind && open(c));
  const volley = enemy.base + active('dmg').reduce((sum,c)=>sum+(c.amt ?? 1),0);
  const intent: Record<string,string> = {volley:'Залп · Корпус −'+volley, charge:'Заряд '+(b.charge+1)+'/3'+(b.charge===2?' · Корпус −'+enemy.chargeDmg:''), board:'Абордаж · Команда −1', repair:'Ремонт одной клетки',tax:'Налог · каждый теряет 1 Сокровище'};

  function commit(note:string) {
    b.note=note;
    const reason=defeat(ship);
    const next:Game={...g,ship,scene:{...scene,board:JSON.stringify(b)},log:[...g.log,{round:g.round,text:note}]};
    onChange(reason ? {...next,step:'over',over:{win:false,reason}} : next);
  }
  function begin() { b.status='play'; b.intent=rollIntent(enemy); commit('Бой начался.'); }
  function close(c:Cell) {
    b.closed.push(c.s);
    let note='Закрыта клетка «'+c.n+'».';
    if(c.k==='loot') note+=' Каждый отмечает Сокровища +'+c.amt+' на листе.';
    if(c.k==='weak') note+=' Следующий удар в этом ходу +2.';
    if(c.k==='prisoner') ship.C=Math.min(10,ship.C+1);
    if(c.thorns) ship.H=Math.max(0,ship.H-1);
    const hearts=enemy.cells.filter(x=>x.k==='heart');
    const left=active('heart').length;
    if(left*2<=hearts.length) b.rage=true;
    if(!left) b.status='win';
    commit(note);
  }
  function endTurn() {
    const anchors=enemy.cells.filter(c=>c.chain);
    if(anchors.some(open)) b.closed=b.closed.filter(s=>!anchors.some(c=>c.s===s));
    let note=b.skip?'Манёвр сорвал намерение.':intent[b.intent]+'.';
    if(!b.skip) {
      if(b.intent==='volley') {
        ship.H=Math.max(0,ship.H-volley);
        if(active('holy').length) note+=' '+who+' отмечает Благословение.';
      }
      if(b.intent==='board') ship.C=Math.max(0,ship.C-1);
      if(b.intent==='charge' && ++b.charge===3) { b.charge=0; ship.H=Math.max(0,ship.H-enemy.chargeDmg); }
      if(b.intent==='repair') {
        const targets=enemy.cells.filter(c=>b.closed.includes(c.s) && c.k!=='heart');
        const target=targets[Math.floor(Math.random()*targets.length)];
        if(target){ b.closed=b.closed.filter(s=>s!==target.s); note+=' Открыта клетка «'+target.n+'».'; }
      }
    }
    b.turn=(b.turn+1)%g.players.length;
    if(!b.turn){
      ship.H=Math.max(0,ship.H-active('fire').length);
      if(active('mast').some(c=>b.round>=c.esc!)) b.status='draw';
      b.round++;
    }
    b.skip=false; b.intent=rollIntent(enemy); commit(note);
  }
  function escape(status:string){
    ship.M=Math.min(10,ship.M+1); b.status=status; commit('Попытка побега · Ропот +1.');
  }
  return <section>
    <p class="kicker">Морской бой · {enemy.cls}</p><h2>{enemy.n}</h2>
    {b.status==='pre' && <>
      <button class="primary wide" onClick={begin}>Вступить в бой</button>
      <button class="wide" onClick={()=>{b.status='bribed';commit('Отметьте откуп на листах.')}}>Откупиться · {enemy.bribe*g.players.length} Сокровищ с экипажа</button>
      <details><summary>Сбежать</summary><p>Бросьте d6 и прибавьте Мозжечок. Отметьте результат.</p>
        {(['caught','escape','escaped'] as const).map((s,i)=><button onClick={()=>escape(s)}>{['≤6 · настигли','7–9 · с потерями','10+ · ушли'][i]}</button>)}</details></>}
    {['escape','caught'].includes(b.status) && <><p>Выберите потери при побеге.</p>{['Корпус −2','Команда −1'].map((label,i)=><button onClick={()=>{
      if(i) ship.C--; else ship.H=Math.max(0,ship.H-2);
      if(b.status==='caught') begin(); else {b.status='escaped';commit('Сбежали. '+label);}
    }}>{label}</button>)}</>}
    {b.status==='play' && <><p>Круг {b.round} · Ходит {who}</p><p class="note"><b>Намерение врага</b><br/>{b.skip?'Сорвано Манёвром':intent[b.intent]}</p>
      <p class="hint">Разыграйте станции в буклете. Коснитесь клетки, которую удалось закрыть.</p></>}
    {b.note && <p aria-live="polite">{b.note}</p>}
    <div class="enemy-grid">{Array.from({length:12},(_,s)=>{
      const c=enemy.cells.find(x=>x.s===s);
      if(!c || (c.hidden && !b.rage)) return <span key={s}/>;
      const closed=b.closed.includes(s);
      const armored=active('armor').some(a=>Math.abs(Math.floor(a.s/4)-Math.floor(s/4))+Math.abs(a.s%4-s%4)===1);
      return <button key={s} class="enemy-cell" disabled={closed || b.status!=='play'} onClick={()=>close(c)}>
        <b>{closed?'✓ ':''}{c.n}</b><small>{kinds[c.k]}{c.amt?' +'+c.amt:''}</small><small>Прочность {c.v}</small>
        <small>{[armored?'Под бронёй':'',c.fly?'Летучая':'',c.dodge?'Вёрткая':'',c.chain?'Цепь':'',c.thorns?'Шипы':'',c.esc?'Уход в конце круга '+c.esc:''].filter(Boolean).join(' · ')}</small>
      </button>;
    })}</div>
    {b.status==='play' && <><label class="check"><input type="checkbox" checked={b.skip} onChange={()=>{b.skip=!b.skip;commit(b.skip?'Манёвр отмечен.':'Манёвр отменён.')}}/> Манёвр сорвал намерение</label><button class="primary wide" onClick={endTurn}>Завершить ход</button></>}
    {outcomes[b.status] && <><h3>{outcomes[b.status]}</h3><button class="primary wide" onClick={()=>onChange(endRound({...g,scene:{...scene,board:undefined},log:[...g.log,{round:g.round,text:enemy.n+' · '+outcomes[b.status]}]},d))}>Завершить встречу</button></>}
  </section>;
}
