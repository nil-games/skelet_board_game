# -*- coding: utf-8 -*-
p = 'sim.py'
s = open(p, encoding='utf-8').read()


def rep(a, b):
    global s
    if a not in s:
        print('НЕТ:', a[:60])
    s = s.replace(a, b)


rep("    visited_new = True\n", "    cur = None\n")
rep("        ev = rng.choice(EVENTS) if visited_new else ROUTINE\n", "        ev = cur or rng.choice(EVENTS)\n")
a = s.index("        # концовка раунда эпизода")
b = s.index("        st['R'] -= THIRST(len(players))  # жажда")
s = s[:a] + """        # концовка раунда эпизода
        if ev['id'] in ('ST1', 'ST2') and 1 not in taken:
            st['H'] -= 2
        if ev['id'] == 'F1' and 1 not in taken:
            st['R'] -= 1
        if ev['id'] == 'SH2':
            st['D'] += 1
        if ev['id'] == 'F2':
            st['R'] -= 1
        if ev['id'] in ('S1', 'S2') and 4 not in taken:
            st['D' if False else 'M'] -= 1 if ev['id'] == 'S2' else 0
            if ev['id'] == 'S1':
                st['R'] -= 1
""" + s[b:]
rep("        pos += st['mv']\n        visited_new = st['mv'] > 0\n        st['mv'] = 0\n",
    "        if ev.get('flow') == 'loop':\n            if st['mv'] > 0:\n                pos += st['mv']\n                cur = None\n            else:\n                cur = ev\n        else:\n            pos += 1\n            cur = None\n        st['mv'] = 0\n")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
