"""python3 jp.py NN rowid... -> show Original + English for rows"""
import sys, re
sys.path.insert(0, '.')
import ws, fi_text as F
nn = sys.argv[1]
rows = F.read_csv(ws.section_path(nn))
h = rows[0]
oi = h.index("Original")
ei = h.index("English") if "English" in h else None
want = set(sys.argv[2:])
for r in rows[1:]:
    if r and r[0] in want or (r and r[0].lstrip('0') in {w.lstrip('0') for w in want}):
        print('@' + r[0], '|', r[ei] if ei is not None else '')
        print('   ', r[oi])
