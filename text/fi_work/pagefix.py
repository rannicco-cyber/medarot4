"""python3 pagefix.py NN 'old line' 'new line' ['old' 'new' ...]  -- replace whole answer lines in work/fi_NN.txt"""
import sys
nn = sys.argv[1]
p = f'/tmp/claude-0/-home-claude/c58ed6a5-6ce9-52b0-a0d6-179850a4c8c5/scratchpad/work/fi_{nn}.txt'
lines = open(p, encoding='utf-8').read().split('\n')
pairs = sys.argv[2:]
for a, b in zip(pairs[::2], pairs[1::2]):
    hits = [i for i, l in enumerate(lines) if l == a]
    if not hits:
        print('NOT FOUND:', a); continue
    for i in hits:
        lines[i] = b
open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print('ok')
