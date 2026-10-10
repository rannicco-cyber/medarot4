#!/usr/bin/env python3
"""Scan gfx/tilemaps for fixed kana text (bank-1 cells with kana ids) -> _to_delete/static_scan.txt"""
import re,glob,os
A="アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"+"ァィゥェォッャュョ"+"あいうえおかきくけこさしすせそたちつてとなにぬねのはひふほまみむめもやゆよらるれろわをんぁぃぅぇぉっゃゅょ"
tab={}
for i,c in enumerate(A): tab[i+1]=c
tab[0x54]='へ'; tab[0x1D]='ヘ'
# fix: hiragana へ/り are written with katakana forms in this font; hiragana run has no へ/り
hira="あいうえおかきくけこさしすせそたちつてとなにぬねのはひふほまみむめもやゆよらるれろわをんぁぃぅぇぉっゃゅょ"
tab={}
for i,c in enumerate(A[:46+9]): tab[i+1]=c
for i,c in enumerate(hira): tab[0x38+i]=c
for i,c in enumerate("ガギグゲゴザジズゼゾダヂヅデドバビブベ"): tab[0x6D+i]=c
tab[0x1D]='ヘ'; tab[0x28]='リ'
for i,c in enumerate("ボパピプペポヴがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷ"): tab[0x80+i]=c
for i in range(26): tab[0x9E+i]=chr(65+i)
tab[0xB8]='?'; tab[0xB9]='!'
for i in range(10): tab[0xE0+i]=str(i)
tab[0xEE]='ー'; tab[0xEF]='・'; tab[0xED]='/'; tab[0xEC]='円'
def lab(path):
    d={};cur=None
    for l in open(path):
        m=re.match(r'^(Tilemap|Attribmap)(\w+)::',l)
        if m: cur=m.group(1)+m.group(2)
        m=re.search(r'build/(?:tilemaps|attribmaps)/(\w+)\.map',l)
        if m and cur: d[cur]=m.group(1); cur=None
    return d
T=lab('game/src/version/tilemap_table.asm'); At=lab('game/src/version/attribmap_table.asm')
byfile={}
for k,v in T.items(): byfile.setdefault(v,[]).append(k)
def rd(p):
    return [[int(x,16) for x in re.findall(r'\\x([0-9a-fA-F]{2})',r)] for r in open(p,encoding='latin-1').read().split('\n')[1:] if r.strip()]
out=[]
for p in sorted(glob.glob('gfx/tilemaps/*.txt')):
    f=os.path.basename(p)[:-4]
    R=rd(p)
    af=None
    for lb in byfile.get(f,[]):
        a=At.get(lb.replace('Tilemap','Attribmap'))
        if a: af=a;break
    AR=rd(f'gfx/attribmaps/{af}.txt') if af and os.path.exists(f'gfx/attribmaps/{af}.txt') else None
    for r,row in enumerate(R):
        c=0
        while c<len(row):
            def ok(cc):
                v=row[cc]
                if v==0 or v not in tab: return False
                if AR is not None:
                    try:
                        if not AR[r][cc]&8: return False
                    except IndexError: return False
                return True
            if ok(c):
                s=c;txt=''
                while c<len(row) and (ok(c) or (row[c]==0 and c+1<len(row) and ok(c+1) and c>s)):
                    txt+=tab[row[c]] if row[c] else ' ';c+=1
                if len(txt.strip())>=1: out.append((f,r,s,c-s,txt,AR is not None,af))
            else: c+=1
open('_to_delete/static_scan.txt','w',encoding='utf-8').write('\n'.join(f"{f} r{r} c{s} n{n} {'A' if a else '-'} {t}" for f,r,s,n,t,a,af in out))
print(len(out),len({o[0] for o in out}))
