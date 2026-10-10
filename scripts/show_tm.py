import re,sys
sys.argv.append('')
exec(open('scripts/scan_static_labels.py').read().split("def lab(path)")[0])
def rd(p):
    return [[int(x,16) for x in re.findall(r'\\x([0-9a-fA-F]{2})',r)] for r in open(p,encoding='latin-1').read().split('\n')[1:] if r.strip()]
import os
for f in sys.argv[1:]:
    if not f: continue
    R=rd(f'gfx/tilemaps/{f}.txt')
    print('==',f,len(R[0]),'x',len(R))
    for r,row in enumerate(R):
        print('%2d '%r+''.join((tab[v] if v in tab else ('.' if v==0 else '#')) for v in row))
