import { render } from 'preact';
import { App } from './app';
import '@fontsource/yeseva-one/400.css';
import '@fontsource/pt-serif/400.css';
import '@fontsource/pt-serif/700.css';
import './style.css';

render(<App />, document.getElementById('app')!);
