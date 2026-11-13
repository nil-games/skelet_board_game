# -*- coding: utf-8 -*-
"""Простейший конвертер 01_Правила.md -> Правила.html (для печати в PDF). Поддержан набор Markdown, который мы используем."""
import os, re, html

SRC = os.path.join(os.path.dirname(__file__), '..', '..', '01_Правила.md')
OUT = os.path.join(os.path.dirname(__file__), '..', 'Правила.html')

CSS = """
@page{size:A4;margin:14mm 14mm 16mm 14mm}
body{font-family:'Segoe UI',Arial,sans-serif;font-size:9.6pt;line-height:1.38;color:#111}
h1{font-family:Georgia,serif;font-size:24pt;margin:0 0 2mm;letter-spacing:1px}
h2{font-family:Georgia,serif;font-size:13.5pt;margin:6mm 0 2mm;padding-bottom:1mm;border-bottom:1.5px solid #111;break-after:avoid}
h3{font-size:11pt;margin:4mm 0 1.2mm;break-after:avoid}
p{margin:1.6mm 0}
ul,ol{margin:1.2mm 0 1.6mm 5mm;padding-left:4mm}
li{margin:0.6mm 0}
blockquote{margin:2mm 0;padding:1.5mm 3mm;background:#f2f2f2;border-left:3px solid #888;font-size:9pt}
blockquote p{margin:0.6mm 0}
table{border-collapse:collapse;width:100%;margin:2mm 0;font-size:8.8pt;break-inside:avoid}
th,td{border:1px solid #777;padding:1mm 1.6mm;vertical-align:top}
th{background:#e4e4e4;text-align:left}
hr{border:none;border-top:1px solid #aaa;margin:3mm 0}
code{font-family:Consolas,monospace;font-size:8.6pt;background:#eee;padding:0 1mm}
"""


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)', r'<i>\1</i>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    return t


def convert(lines):
    out, i = [], 0
    n = len(lines)
    while i < n:
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.strip() == '---':
            out.append('<hr>')
            i += 1
            continue
        m = re.match(r'^(#{1,3})\s+(.*)$', ln)
        if m:
            k = len(m.group(1))
            out.append('<h%d>%s</h%d>' % (k, inline(m.group(2)), k))
            i += 1
            continue
        if ln.lstrip().startswith('>'):
            buf = []
            while i < n and lines[i].lstrip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i].rstrip()))
                i += 1
            out.append('<blockquote>' + ''.join('<p>%s</p>' % inline(b) for b in buf if b.strip()) + '</blockquote>')
            continue
        if ln.startswith('|'):
            rows = []
            while i < n and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            head, body = rows[0], [r for r in rows[2:]]
            out.append('<table><tr>' + ''.join('<th>%s</th>' % inline(c) for c in head) + '</tr>'
                       + ''.join('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in r) + '</tr>' for r in body) + '</table>')
            continue
        if re.match(r'^\s*(\d+\.|-)\s+', ln):
            stack = []   # (indent, tag)
            while i < n and re.match(r'^\s*(\d+\.|-)\s+', lines[i]):
                l2 = lines[i].rstrip()
                ind = len(l2) - len(l2.lstrip())
                tag = 'ol' if re.match(r'^\s*\d+\.', l2) else 'ul'
                txt = re.sub(r'^\s*(\d+\.|-)\s+', '', l2)
                while stack and stack[-1][0] > ind:
                    out.append('</li></%s>' % stack.pop()[1])
                if stack and stack[-1][0] == ind:
                    out.append('</li><li>%s' % inline(txt))
                else:
                    out.append('<%s><li>%s' % (tag, inline(txt)))
                    stack.append((ind, tag))
                i += 1
            while stack:
                out.append('</li></%s>' % stack.pop()[1])
            continue
        buf = [ln]
        i += 1
        while i < n and lines[i].strip() and not re.match(r'^(#|\||>|---|\s*(\d+\.|-)\s)', lines[i]):
            buf.append(lines[i].rstrip())
            i += 1
        out.append('<p>%s</p>' % inline(' '.join(buf)))
    return '\n'.join(out)


if __name__ == '__main__':
    md = open(SRC, encoding='utf-8').read().split('\n')
    body = convert(md)
    doc = ('<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Всем костям на борт! — Правила</title>'
           '<style>%s</style></head><body>%s</body></html>') % (CSS, body)
    open(OUT, 'w', encoding='utf-8').write(doc)
    print('ok', os.path.abspath(OUT))
