#!/usr/bin/env python3
"""apply_names.py <List> : rebuild text/ptrlists/<List>.txt from the Japanese original
(text/fi_work/ptrlists_ja/<List>.txt) using one translated name per line from
text/fi_work/names/<List>.txt (line N = list index N). Model/prefix/flag fields are kept."""
import sys,re
name=sys.argv[1]
src=open(f'text/fi_work/ptrlists_ja/{name}.txt',encoding='utf-8-sig').read().split('\n')
tr=[l.rstrip('\r') for l in open(f'text/fi_work/names/{name}.txt',encoding='utf-8').read().split('\n')]
while tr and tr[-1]=='': tr.pop()
header=src[0]
cols=eval(header.lstrip('﻿'))[1]
out=[];n=0
for ln in src:
    m=re.match(r'^(\d+),(.*)$',ln)
    if not m:
        out.append(ln); continue
    i=int(m.group(1)); rest=m.group(2)
    if i>=len(tr): out.append(ln); continue
    t=tr[i]
    assert ',' not in t,(name,i,t)
    if name.startswith('Parts'):
        model,_,tail=rest.partition(',')
        flags=tail.rsplit(',',1)[1]
        assert len(t)<=8,(name,i,t)
        ln=f"{i},{model},{t}\\xcb,{flags}"
    elif name in('Medarotters','Medarotters2','Medaforce'):
        prefix=rest.split(',',1)[0]
        assert len(t)<=11,(name,i,t)
        ln=f"{i},{prefix},{t}"
    else:
        assert len(t)<=11,(name,i,t)
        ln=f"{i},{t}"
    n+=1; out.append(ln)
bom=open(f'text/fi_work/ptrlists_ja/{name}.txt','rb').read(3)==bytes([0xef,0xbb,0xbf])
open(f'text/ptrlists/{name}.txt','wb').write((bytes([0xef,0xbb,0xbf]) if bom else b'')+'\n'.join(out).encode('utf-8'))
print(name,n,'names applied')
