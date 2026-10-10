"""python3 joinfix.py NN [rowid:pK ...]  -- add '.' to the page before every flagged soft join, except listed ones.
Use rowid:pK=, to add a comma instead."""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
nn = sys.argv[1]
spec = {}
for a in sys.argv[2:]:
    k, _, v = a.partition('=')
    spec[k] = v           # '' = skip, ',' = comma
out = subprocess.run([sys.executable, os.path.join(HERE, 'ws.py'), 'joins', nn], capture_output=True, text=True).stdout
flags = [l.split(':')[0] for l in out.splitlines() if l.strip()]
p = os.path.join(HERE, f'work/fi_{nn}.txt')
lines = open(p, encoding='utf-8').read().split('\n')
# index answer lines per row
idx = {}
cur = None
for i, l in enumerate(lines):
    if l.startswith('@'):
        cur = l[1:].split()[0]; idx[cur] = []
    elif cur is not None and l.strip():
        idx[cur].append(i)
n = 0
for f in flags:
    rid, pk = f.split(' ')
    k = int(pk[1:])
    key = f'{rid}:{pk}'
    if key in spec and spec[key] == '':
        continue
    # previous non-empty page
    j = k - 1
    while j >= 0 and lines[idx[rid][j]].strip() == '+':
        j -= 1
    li = idx[rid][j]
    lines[li] = lines[li].rstrip() + (spec.get(key) or '.')
    n += 1
open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print(f'{n} pages punctuated')
