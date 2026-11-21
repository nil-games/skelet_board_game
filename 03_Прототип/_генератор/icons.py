# -*- coding: utf-8 -*-
"""Иконки: папка «Ресурсы для игры/Картинки» в корне проекта (PNG 512×512, чёрные на прозрачном).
Подпапки: «Значки навыков», «Параметры корабля», «Счётчики», «Предметы». Пути относительные от HTML в 03_Прототип/."""
from urllib.parse import quote

ROOT = '../' + quote('Ресурсы для игры') + '/' + quote('Картинки') + '/'
SK = 'Значки навыков'
PAR = 'Параметры корабля'
CNT = 'Счётчики'
ITM = 'Предметы'

# ключ → (папка, файл)
ICONS = {
    'nose': (SK, 'Вездесуй'), 'bone': (SK, 'Кальций'), 'grab': (SK, 'Мормышка'),
    'eye': (SK, 'Шмаляние'), 'scare': (SK, 'Понты'), 'helm': (SK, 'Мозжечок'),
    'H': (PAR, 'Корпус'), 'C': (PAR, 'Команда'), 'R': (PAR, 'Ром'), 'M': (PAR, 'Ропот'), 'D': (PAR, 'Опасность'), 'map': (PAR, 'Карта'),
    'F': (CNT, 'Слава'), 'L': (CNT, 'Удача'), 'T': (CNT, 'Сокровища'), 'BL': (CNT, 'Благословение'), 'CU': (CNT, 'Проклятие'),
    'gear': (ITM, 'Снаряжение'), 'curio': (ITM, 'Диковинка'), 'fish': (ITM, 'Рыба (Рыбалка)'), 'battle': (ITM, 'Улучшение на бой'), 'shuller': (ITM, 'Шуллерская штучка'),
}
# ключи эффектов события → ключ иконки
EFFECT_ICON = {'H': 'H', 'C': 'C', 'R': 'R', 'M': 'M', 'D': 'D', 'F': 'F', 'L': 'L', 'T': 'T', 'BL': 'BL', 'CU': 'CU', 'RT': 'R', 'catch': 'fish', 'mv': 'map', 'sc': 'map'}
NAMES = {'H': 'Корпус', 'C': 'Команда', 'R': 'Ром', 'M': 'Ропот', 'D': 'Опасность', 'F': 'Слава', 'L': 'Удача', 'T': 'Сокровища',
         'BL': 'Благословение', 'CU': 'Проклятие', 'S': 'Искры', 'mv': 'ход', 'sc': 'разведка', 'catch': 'улов', 'RT': 'Ром', 'pick': 'обломки'}


def url(key):
    d, f = ICONS[key]
    return ROOT + quote(d) + '/' + quote(f) + '.png'


def img(key, h_mm=3.6):
    """HTML-картинка (Книга событий, листы)."""
    return '<img class="sk" src="%s" style="height:%.1fmm">' % (url(key), h_mm)


def svg_image(key, cx, cy, size=4.6):
    """SVG-картинка (мм), центр (cx, cy)."""
    return '<image href="%s" x="%.2f" y="%.2f" width="%.2f" height="%.2f"/>' % (url(key), cx - size / 2, cy - size / 2, size, size)


def entity_html(eff_key, h_mm=3.2):
    """Иконка + название сущности (эффект события): для подсказки в списке слотов."""
    nm = NAMES.get(eff_key, eff_key)
    if eff_key == 'S':
        return '✦ %s' % nm
    if eff_key == 'pick':
        return '%s %s %s %s' % (img('R', h_mm), img('T', h_mm), img('H', h_mm), nm)
    k = EFFECT_ICON.get(eff_key)
    return ('%s %s' % (img(k, h_mm), nm)) if k else nm
