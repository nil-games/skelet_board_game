# -*- coding: utf-8 -*-
"""v0.20: Книга событий: списки событий в начале (d6, страницы-ссылки), каталог по типам местности, бои, порты."""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

p = 'newcontent.py'
s = open(p, encoding='utf-8').read()
a = "dict(id='B3', title='Королева Ржавчина', cls='сильный', special='Корпус врага +3 к таблице. Награда выше.',"
if 'hull_bonus' not in s:
    assert a in s
    s = s.replace(a, a + " hull_bonus=3,")
    open(p, 'w', encoding='utf-8').write(s)

p = 'build_book.py'
s = open(p, encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, cnt)


rep("""    h = ['<div class="ev"><div class="hd"><span class="sym">%s</span> %s <small>[%s]</small></div>' % (sym, ev['title'], ev['id'])]""",
    """    h = ['<div class="ev" id="ev-%s"><div class="hd"><span class="sym">%s</span> %s <small>[%s]</small></div>' % (ev['id'], sym, ev['title'], ev['id'])]""")
rep("""    if kind == 'port':
        h.append('<div class="lock">В этом порту:""", """    if kind == 'port':
        h.append('<div class="lock"><b>Рыба:</b> этот порт %s.</div>' % ev.get('fish', 'платит по цене'))
        h.append('<div class="lock">В этом порту:""")

NEW = open('book_funcs.txt', encoding='utf-8').read()
rep("def book():\n", NEW + "\n\ndef book(pages=None):\n    global PAGES\n    PAGES = pages or {}\n")
rep("""    h.append('<h1>Книга событий</h1><p>Бумажная замена приложения для прототипа «Всем костям на борт!». Её читает <b>Писарь</b>.</p>')""",
    """    h.append('<h1>Книга событий</h1><p>Бумажная замена приложения для прототипа «Всем костям на борт!». Её читает <b>Писарь</b>.</p>')
    h.append(lists_html())""")
rep("""    h.append('<h2>Эпизоды</h2>')
    for ev in EVENTS:
        h.append(event_block(ev))
""", """    h.append(events_html())
""")
rep("""    for pt in PORTS:
        h.append(event_block(pt, 'port'))
""", """    h.append(ports_html())
""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
