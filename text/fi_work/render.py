"""python3 render.py NN rowid... -> show boxes of built rows"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fi_text as F
import ws
font = F.Font(ws.REPO)
nn = sys.argv[1]
rows = {r[0]: r for r in F.read_csv(os.path.join(ws.OUT, f"TextSection{nn}.csv"))[1:] if r}
for rid in sys.argv[2:]:
    r = rows[rid]
    _, lines = F.check(font, r[3], menu=F.is_menu(r[2]))
    print(f"== {rid}")
    cur = None
    for p, l, w, t in lines:
        if p != cur:
            print(f"  [box {p}]")
            cur = p
        print(f"    {w:3d} {t}")
