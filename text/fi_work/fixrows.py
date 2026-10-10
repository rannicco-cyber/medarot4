"""python3 fixrows.py NN 'rowid' 'page1' 'page2' ... [-- 'rowid' ...]"""
import re, sys
nn = sys.argv[1]
args = sys.argv[2:]
fix = {}
cur = None
for a in args:
    if a == '--':
        cur = None
        continue
    if cur is None:
        cur = a
        fix[cur] = []
    else:
        fix[cur].append(a)
p = f'/tmp/claude-0/-home-claude/c58ed6a5-6ce9-52b0-a0d6-179850a4c8c5/scratchpad/work/fi_{nn}.txt'
s = open(p, encoding='utf-8').read()
blocks = re.split(r'(?m)^(?=@)', s)
out = []
seen = set()
for b in blocks:
    if not b.strip():
        continue
    rid = b[1:].split()[0]
    if rid in fix:
        b = '@' + rid + '\n' + '\n'.join(fix[rid]) + '\n'
        seen.add(rid)
    out.append(b)
for rid in fix:
    if rid not in seen:
        out.append('@' + rid + '\n' + '\n'.join(fix[rid]) + '\n')
open(p, 'w', encoding='utf-8').write(''.join(out))
print('fixed', ', '.join(fix))
