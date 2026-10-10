import re,sys
exec(open('scripts/scan_static_labels2.py').read().split("out=[]")[0])
for f in sys.argv[1:]:
    R=rd(f'gfx/tilemaps/{f}.txt')
    afs=[a for a in dict.fromkeys(attrs.get(f,[])) if a]
    print('==',f,len(R[0]),'x',len(R),'attrs',afs)
    AR=rd(f'gfx/attribmaps/{afs[0]}.txt') if afs else None
    for r,row in enumerate(R):
        s=''
        for c,v in enumerate(row):
            b=(AR[r][c]&8) if AR and r<len(AR) and c<len(AR[r]) else 0
            if v==0: s+='_' if b else '.'
            elif b and v in tab: s+=tab[v]
            elif b: s+='<%02X>'%v
            else: s+='[%02X]'%v
        print('%2d %s'%(r,s))
