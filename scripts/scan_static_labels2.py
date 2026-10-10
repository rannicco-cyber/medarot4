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

def parse(path,kind):
    tab={};lab={};cur=None;bank=None;idx=0
    for l in open(path):
        m=re.match(r'^SECTION "(?:Tilemap|Attribmap) Table (\w+)"',l)
        if m: bank=m.group(1);idx=0;continue
        m=re.match(r'^\s*dw (\w+)',l)
        if m and bank is not None:
            lbl=m.group(1)
            if 'Terminator' in lbl: lbl=None
            tab[(bank,idx)]=lbl;idx+=1;continue
        m=re.match(r'^(%s\w+)::'%kind,l)
        if m: cur=m.group(1)
        m=re.search(r'build/(?:tilemaps|attribmaps)/(\w+)\.map',l)
        if m and cur: lab[cur]=m.group(1);cur=None
    return tab,lab
TT,TL=parse('game/src/version/tilemap_table.asm','Tilemap')
AT,AL=parse('game/src/version/attribmap_table.asm','Attribmap')
attrs={}
for k,l in TT.items():
    if not l: continue
    f=TL.get(l); a=AT.get(k); af=AL.get(a) if a else None
    attrs.setdefault(f,[]).append(af)
def rd(p):
    return [[int(x,16) for x in re.findall(r'\\x([0-9a-fA-F]{2})',r)] for r in open(p,encoding='latin-1').read().split('\n')[1:] if r.strip()]
out=[]
for p in sorted(glob.glob('gfx/tilemaps/*.txt')):
    f=os.path.basename(p)[:-4]
    R=rd(p)
    afs=[a for a in dict.fromkeys(attrs.get(f.split('_')[0] if f not in attrs else f,[])) if a]
    af=afs[0] if afs else None
    multi=len(afs)>1
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
                if len(txt.strip())>=1: out.append((f,r,s,c-s,txt,AR is not None,af+('+' if multi else '') if af else ''))
            else: c+=1
open('_to_delete/static_scan2.txt','w',encoding='utf-8').write('\n'.join(f"{f} r{r} c{s} n{n} {'A' if a else '-'} {af} {t}" for f,r,s,n,t,a,af in out))
print(len(out),len({o[0] for o in out}))
