import { readFileSync } from 'node:fs';
import { expect, it, vi } from 'vitest';
import { BoardEncounter } from './BoardEncounter';
import { newGame, enterCell, closeIntro } from '../engine/game';
import type { GameData } from '../data';

vi.mock('preact/hooks', () => ({useEffect: () => {}}));
const d: GameData = JSON.parse(readFileSync(new URL('../../public/game_data.json',import.meta.url),'utf8'));

it('проводит встречу с Чайкой по отметкам на телефоне', () => {
  const players = ['А','Б','В','Г'].map(name=>({name}));
  let game = closeIntro(enterCell(newGame(d,{shipName:'Тест',players}),d,'sh',()=>0));
  function visit(node: any): any[] {
    if (Array.isArray(node)) return node.flatMap(visit);
    if (!node || typeof node !== 'object') return [];
    return [node,...visit(node.props.children)];
  }
  function click(label: string) {
    const nodes = visit(BoardEncounter({g:game,d,onChange:next=>{game=next;}}));
    const button = nodes.find(node=>node.type==='button' &&
      (node.props.children===label || visit(node.props.children).some(child=>child.type==='b' && child.props.children.includes(label))));
    expect(button).toBeDefined();
    expect(button.props.disabled).toBeFalsy();
    button.props.onClick();
  }
  click('Вступить в бой');
  click('Перья');
  click('Завершить ход');
  expect(JSON.parse(game.scene!.board!).turn).toBe(1);
  for (const cell of ['Голова','Грудь','Крыло']) click(cell);
  expect(JSON.parse(game.scene!.board!).status).toBe('win');
  click('Завершить встречу');
  expect(game.step).toBe('after');
});
