import re, glob, os
base = r'F:\Projects\BoardGames\Корабль призрак'
fs = glob.glob(base + r'\*.md') + [base + r'\03_Прототип\README.md'] + [f for f in glob.glob(base + r'\03_Прототип\_генератор\*.py') if not os.path.basename(f).startswith('patch') and os.path.basename(f) not in ('ctx.py',)]
for f in fs:
    t = open(f, encoding='utf-8').read().replace('\n', ' ')
    for m in re.finditer(r'.{0,50}\b[Дд]обыч(?:а|и|е|у|ей)\b.{0,50}', t):
        print(os.path.basename(f), '|', m.group(0))
