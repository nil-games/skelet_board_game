import { JOURNAL_ROWS, type Game } from '../engine/game';

export function Journal({ g, onSet }: { g: Game; onSet: (row: number, v: number) => void }) {
  return (
    <div>
      <h5>Ключевые слова</h5>
      <p class="hint small">Нажмите клетку, чтобы закрасить строку до неё (повторное нажатие на последнюю — стереть).</p>
      <table class="journal">
        <tbody>
          {JOURNAL_ROWS.map((name, r) => (
            <tr key={r}>
              <th>{name}</th>
              {[1, 2, 3, 4, 5, 6].map((c) => (
                <td key={c}><button data-snd="journal" class={g.journal[r] >= c ? 'on' : ''} aria-label={`${name} ${c}`} onClick={() => onSet(r, g.journal[r] === c ? c - 1 : c)}>{c}</button></td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <h5>Острова</h5>
      <ul class="small">{g.islands.map((i) => <li key={i.no}>№{i.no}: {i.kind === 'port' ? 'порт' : 'необитаемый'} ({i.id})</li>)}</ul>
      <h5>Лента рейса</h5>
      <ol class="feed" reversed>
        {g.log.slice().reverse().map((l, i) => <li key={i}><small>р.{l.round}</small> {l.text}</li>)}
      </ol>
    </div>
  );
}
