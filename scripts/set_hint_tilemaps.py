#!/usr/bin/env python3
"""Finnish fixed-width (Latin tileset 98004) text for the small SELECT/START hint tilemaps.
Tile id = ASCII, 01-0A = AE-ligature/umlaut set (a-umlaut = 02, o-umlaut = 04)."""
import re,sys
def enc(s):
    m={'ä':2,'ö':4,'Ä':1,'Ö':3}
    return [m.get(c,ord(c)) for c in s]
def rd(p):
    raw=open(p,'rb').read().decode('latin-1')
    return raw
def rows(p):
    L=open(p,encoding='latin-1').read().split('\n')
    hdr=L[0]; body=[r for r in L[1:] if r!='']
    return hdr,[[int(x,16) for x in re.findall(r'\\x([0-9a-fA-F]{2})',r)] for r in body],L
def wr(p,hdr,R,orig):
    trail=orig[-1]==''   # keep original trailing-newline style
    out=[hdr]+[''.join('\\x%02x'%v for v in r) for r in R]
    open(p,'w',encoding='latin-1',newline='').write('\n'.join(out)+('\n' if trail else ''))
def put(R,row,col,text):
    ids=enc(text)
    for i,v in enumerate(ids): R[row][col+i]=v
def setattr_all(p,val):
    hdr,R,orig=rows(p)
    R=[[val]*len(r) for r in R]
    wr(p,hdr,R,orig)
def tm(name,edits):
    p=f'gfx/tilemaps/{name}.txt'
    hdr,R,orig=rows(p)
    for row,col,text in edits:
        n=len(enc(text))
        R[row][col:col+max(n,0)]=R[row][col:col+n]
        put(R,row,col,text)
    wr(p,hdr,R,orig)
def clear(name,row,c0,c1):
    p=f'gfx/tilemaps/{name}.txt'
    hdr,R,orig=rows(p)
    for c in range(c0,c1): R[row][c]=0
    wr(p,hdr,R,orig)
# 0401 (Medabotti select hint): SELECT = swap, START = talk
clear('0401',0,0,18); clear('0401',2,0,18)
tm('0401',[(0,0,'SELECT: vaihda'),(2,0,'START: keskustele')])
setattr_all('gfx/attribmaps/0401.txt',0x0F)
# 0406 / 0407 (shared attribmap 0406)
clear('0406',0,0,18); clear('0407',0,0,18)
tm('0406',[(0,0,'START: Kumppani')]); tm('0407',[(0,0,'START: Medabotit')])
setattr_all('gfx/attribmaps/0406.txt',0x0F)
# 0481 framed rotation box
clear('0481',1,1,19); clear('0481',3,1,19)
tm('0481',[(1,1,'START:'),(3,1,'Rotaation vaihto')])
