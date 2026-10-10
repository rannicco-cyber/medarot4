#!/usr/bin/env python3
"""(Text cells are blank, the VWF overlay in static_labels_table.asm draws the names.)
Battle skill labels (8x1 tilemaps 00F1..00FE): Finnish skill name followed by the original icon cells,
which move right with the longer name.  Writes new attribmap files where the icon cells moved and
re-points the matching INCBIN in game/src/version/attribmap_table.asm."""
import re,os,shutil
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
BK='gfx/_backup_static'; os.makedirs(BK,exist_ok=True)
def enc(s):
    m={'ä':2,'ö':4,'Ä':1,'Ö':3}
    return [m.get(c,ord(c)) for c in s]
# Text cells before the icon are always 6 (48 px): the text is drawn at run time by set_static_labels.py (SKILL).
T6='      '
LAB={'00F1':(T6,3,[('F1','00E1'),('F2','00F2')]),'00F3':(T6,2,[('F3','00F3')]),
 '00F4':(T6,5,[('F4','00F4')]),'00F5':(T6,5,[('F5','00F4')]),
 '00F6':(T6,3,[('F6','00F2')]),'00F7':(T6,3,[('F7','00F2')]),'00F8':(T6,3,[('F8','00F2')]),
 '00F9':(T6,4,[('F9','00F9')]),'00FA':(T6,4,[('FA','00F9')]),'00FB':(T6,4,[('FB','00F9')]),
 '00FD':(T6,3,[('FD','00F2')]),'00FE':(T6,3,[('FE','00F2')])}
def rd(p):
    L=open(p,encoding='latin-1').read().split('\n')
    return L[0],[int(x,16) for x in re.findall(r'\\x([0-9a-fA-F]{2})',L[1])],L[-1]==''
def wr(p,h,row,tr):
    open(p,'w',encoding='latin-1',newline='').write(h+'\n'+''.join('\\x%02x'%v for v in row)+('\n' if tr else ''))
asm=open('game/src/version/attribmap_table.asm',encoding='utf-8').read()
made={}
for tm,(text,k,idx) in LAB.items():
    if not os.path.exists(f'{BK}/{tm}.txt'): shutil.copy(f'gfx/tilemaps/{tm}.txt',f'{BK}/{tm}.txt')
    h,row,tr=rd(f'{BK}/{tm}.txt')
    new=([0]*len(text)+row[k:]+[0]*8)[:8]   # text cells stay blank: drawn with the menu VWF (set_static_labels.py SKILL)
    wr(f'gfx/tilemaps/{tm}.txt',h,new,tr)
    for label,af in idx:
        ah,arow,atr=rd(f'gfx/attribmaps/{af}.txt')
        nat=([0x0F]*len(text)+arow[k:]+[0x0F]*8)[:8]
        if nat==arow: continue
        key=tuple(nat)
        if key not in made:
            name='B%02X%d'%(len(made)+1,len(text))   # no underscore: common (unversioned) attribmap
            wr(f'gfx/attribmaps/{name}.txt',ah,nat,atr); made[key]=name
        name=made[key]
        asm,n=re.subn(r'(Attribmap00_%s::\n\s*INCBIN "\./build/attribmaps/)\w+(\.map")'%label,r'\g<1>%s\g<2>'%name,asm)
        assert n==1,label
open('game/src/version/attribmap_table.asm','w',encoding='utf-8',newline='').write(asm)
print('done',made)
