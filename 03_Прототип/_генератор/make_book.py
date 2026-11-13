# -*- coding: utf-8 -*-
"""Сборка Книги событий в PDF: страницы событий в списках (ссылки), нумерация страниц, закладки (оглавление).
Запуск: python make_book.py [имя_pdf]   (по умолчанию Книга_событий_v16.pdf в папке 03_Прототип)"""
import os, sys, subprocess, json, re
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fitz
import build_book
import content

OUT = Path(os.path.dirname(os.path.abspath(__file__))).parent
HTML = OUT / 'Книга_событий.html'
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
FONT = r'C:\Windows\Fonts\segoeui.ttf'


def render(pdf_path):
    subprocess.run([EDGE, '--headless', '--disable-gpu', '--no-pdf-header-footer', '--print-to-pdf=' + str(pdf_path), HTML.as_uri()],
                   check=True, timeout=240)


def ids():
    out = [e['id'] for e in content.EVENTS] + [b['id'] for b in content.BATTLES] + [p['id'] for p in content.PORTS]
    return out


def find_pages(doc):
    texts = [p.get_text() for p in doc]
    pages = {}
    for i in ids():
        mark = '[%s]' % i
        hits = [n + 1 for n, t in enumerate(texts) if mark in t]
        # блоки в Обучении тоже содержат [ID]: основной каталог идёт позже, берём последнее вхождение
        pages[i] = hits[-1] if hits else 0
    return pages


def build(pages):
    HTML.write_text(build_book.book(pages), encoding='utf-8')


def main(name):
    final = OUT / name
    tmp = OUT / '_book_tmp.pdf'
    pages = {}
    for it in range(4):
        build(pages)
        render(tmp)
        doc = fitz.open(tmp)
        newp = find_pages(doc)
        doc.close()
        print('проход %d: страниц в PDF %d' % (it + 1, len(fitz.open(tmp))), 'карта страниц %s' % ('стабильна' if newp == pages else 'изменилась'))
        if newp == pages:
            break
        pages = newp
    doc = fitz.open(tmp)
    n = len(doc)
    # нумерация страниц
    for k, page in enumerate(doc):
        rect = page.rect
        txt = 'стр. %d / %d' % (k + 1, n)
        page.insert_text((rect.width / 2 - 24, rect.height - 14), txt, fontsize=8.5, fontname='segoe', fontfile=FONT, color=(0.35, 0.35, 0.35))
    # закладки
    toc = []

    def first_page(pattern, start=0):
        for k in range(start, n):
            if pattern in doc[k].get_text():
                return k + 1
        return None
    sections = [
        ('Списки событий (бросок d6)', 'Списки событий (бросок d6)'),
        ('Обучение', 'ОБУЧЕНИЕ'),
        ('Определение эпизода и острова', 'Определение эпизода'),
        ('Свободное плавание: подготовка', 'Свободное плавание: подготовка'),
        ('Каталог: штиль', 'Каталог: Штиль и особый штиль'),
        ('Каталог: шторм', 'Каталог: Шторм'),
        ('Каталог: туман', 'Каталог: Туман'),
        ('Каталог: корабль (бои, переговоры)', 'Каталог: Корабль'),
        ('Каталог: необитаемые острова', 'Каталог: Необитаемые острова'),
        ('Порты', 'Порты (пул типов)'),
        ('Игорный дом', 'Игорный дом (ячейка 6)'),
        ('Магазин', 'Магазин (ячейка 5)'),
        ('Рыбалка', 'Рыбалка (слот 7 на Палубе)'),
        ('Воспоминания', 'Воспоминания (флешбек)'),
        ('Морской бой', 'Морской бой «Залп»'),
    ]
    for title, pat in sections:
        pgn = first_page(pat) if pat != 'ОБУЧЕНИЕ' else first_page('ОБУЧЕНИЕ')
        if pgn:
            toc.append([1, title, pgn])
            if title.startswith('Каталог') or title == 'Порты':
                key = {'Каталог: штиль': 's', 'Каталог: шторм': 'st', 'Каталог: туман': 'f', 'Каталог: корабль (бои, переговоры)': 'sh', 'Каталог: необитаемые острова': 'i_wild'}.get(title)
                lst = content.POOLS[key] if key else [x[2] for x in content.PORT_TABLE]
                for i in lst:
                    ttl = next((e['title'] for e in content.EVENTS if e['id'] == i), None) or next((b['title'] for b in content.BATTLES if b['id'] == i), None) or next(p['title'] for p in content.PORTS if p['id'] == i)
                    if pages.get(i):
                        toc.append([2, '%s [%s]' % (ttl, i), pages[i]])
    doc.set_toc(toc)
    doc.save(final, garbage=3, deflate=True)
    doc.close()
    tmp.unlink()
    json.dump(pages, open(OUT / '_generator_pages.json', 'w'), ensure_ascii=False)
    print('готово:', final, 'страниц', n)
    print({k: v for k, v in list(pages.items())[:6]})


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'Книга_событий_v16.pdf')
