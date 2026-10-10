#!/usr/bin/env python3
"""Finnish text for the fixed-tile (non-dialog) labels in gfx/tilemaps, in the Latin tileset 98004
(tile id = ASCII; 02 = a-umlaut, 04 = o-umlaut).  Always rebuilds from gfx/_backup_static (first run copies).
SPECS: (tilemap, row, col_from, col_to_inclusive, text).  Cells of the span are cleared first; their
attribute is forced to bank 1 (bit 3) if it was not already, in every attribmap file used by the tilemap."""
import re,os,shutil,sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
exec(open('scripts/scan_static_labels2.py').read().split("out=[]")[0])   # attrs: tilemap file -> [attribmap files]
BK='gfx/_backup_static'
attrs['018B']=['0189']
attrs['0457']=['0457']   # the ability screen has its own copy of attribmap 04_52 (the pop-up menus 0452..0456 keep 0452)   # the scan's tilemap->attribmap guess is wrong here: the shop code loads attribmap 0189 for tilemap 018B
def enc(s):
    m={'ä':2,'ö':4,'Ä':1,'Ö':3}
    return [m.get(c,ord(c)) for c in s]
STAT={'装甲':'Panssari','成功':'Osuma','威力':'Teho','回数':'Kerrat','充填':'Lataus','放熱':'Jäähdyt',
      '推進':'Työntö','機動':'Liike','防御':'Puolust.','近接':'Lähi','遠隔':'Kauko'}
# Tilemaps whose labels are drawn with the menu VWF at run time (game/src/version/kabuto/static_labels.asm).
# Their label cells stay blank in the tilemap, the text goes into static_labels_table.asm.
OVERLAY={'0012','0175','018B','000B','0433','0401','0406','0407','0050','0420','04A3','04B1','04B3','0444','005E','0451','0452','0453','0454','0455','0456','0457','0047','004A','0421','009D','00B1'}
# Battle skill labels (INFO. box): the names go through the menu VWF too. set_battle_labels.py lays out the
# tilemaps (blank text cells, icon cells moved right), so these are skipped when the tilemaps are rewritten.
SKILL={'00F1':'Lyönti','00F3':'Ammunta','00F4':'Raivo','00F5':'Tähtäys','00F6':'Suojaus','00F7':'Asennus','00F8':'Korjaus',
       '00F9':'Erikois','00FA':'Rohkaisu','00FB':'Häirintä','00FD':'Muutos','00FE':'Voima'}   # the names of the glossary, 6 cells of text (48 px) before the icon
OVERLAY|=set(SKILL)
S=[]
# Baked tiles replaced before the labels go on: (tilemap, row, col_from, col_to, tile id)
FIX={'0457':[(0,3,7,0x14),(1,2,8,0x21),(0,17,17,0x01)]}   # ability screen: blank orange title tab (the kana of the title were baked into 10 tiles)
def a(tm,items):
    for it in items: S.append((tm,)+tuple(it))   # (row, col_from, col_to, text[, palette]): the palette overrides the one of the cells
a('0012',[(2,2,6,'Kello'),(4,2,6,'Esine'),(6,2,6,'Kulku'),(8,2,6,'Tallenna')])
a('0175',[(1,10,12,'Raha'),(2,2,7,'Osta osia'),(4,2,7,'Myy osia'),(6,2,7,'Poistu')])   # shop: buy parts / sell parts / quit
a('018B',[(2,2,8,'Maalaa'),(4,2,8,'Palauta väri'),(6,2,8,'Selitys'),(8,2,8,'Poistu')])   # paint shop: paint / restore colour / explanation / quit
# Yes/No box (000B is the box alone, 0433 is the "Medachange?" question with the box on its right).
a('000B',[(1,2,4,'Kyllä'),(3,2,4,'Ei')])
a('0433',[(1,1,12,'Medamuutos?'),(1,16,18,'Kyllä'),(3,16,18,'Ei')])
# Medarot select screen hint boxes (set_hint_tilemaps.py wrote them as fixed-width Latin text, now VWF overlay).
a('0401',[(0,0,17,'SELECT: vaihda'),(2,0,17,'START: keskustele')])
a('0406',[(0,0,17,'START: Kumppani')]); a('0407',[(0,0,17,'START: Medabotit')])
a('0050',[(14,1,15,'Tallennetaanko?')])   # the Yes/No box covers the cells from column 14 on
a('005E',[(1,2,6,'Tila'),(2,2,6,'Katso'),(3,2,6,'Rotaatio'),(4,2,6,'Auto')])
a('00B5',[(2,3,10,'Huvikisa'),(4,3,10,'Tosikisa'),(6,2,10,'Osavaihto'),(8,3,10,'Lahjoita'),(10,3,10,'Katkaise')])
a('00C3',[(1,2,6,'Käsin'),(3,2,6,'Auto')])
a('010B',[(1,2,4,'Ota'),(3,1,4,'Pois')])
a('011C',[(4,3,18,'Musiikki'),(8,3,18,'Tehosteet'),(12,3,18,'Poista tallennus'),(15,3,18,'Lopeta')])
a('0124',[(11,2,18,'Tallennus rikki'),(13,2,18,'Aloita peli'),(15,2,18,'uudelleen.')])
a('0202',[(1,2,5,'Näe'),(3,2,5,'Vaih'),(5,2,5,'Pois')])
for f in ('041C','041D','041F'):
    pass
a('041C',[(1,12,19,STAT['装甲']),(3,12,19,STAT['成功']),(5,12,19,STAT['威力']),(7,12,19,'Kerrat'),(12,4,9,'Lajit.')])
a('041D',[(1,12,19,STAT['装甲']),(3,12,19,STAT['成功']),(5,12,19,STAT['威力']),(7,12,19,STAT['充填']),(9,12,19,STAT['放熱']),(12,4,9,'Lajit.')])
a('041F',[(1,12,19,STAT['装甲']),(3,12,19,STAT['推進']),(5,12,19,STAT['機動']),(7,12,19,STAT['防御']),(9,12,19,STAT['近接']),(11,12,19,STAT['遠隔']),(12,4,9,'Lajit.')])
attrs['0047']=[]; attrs['004A']=[]   # 1x7 tilemaps that swap the SELECT hint on the Medarot status screen; they share attribmap 003A with other uses, the label draw sets the bank bit itself
a('0420',[(4,2,5,'Tyyppi/'),(6,5,8,'Muunna')]); a('0047',[(0,3,6,'Muunna')]); a('004A',[(0,3,6,'Paluu')])   # Medarot status screen: SELECT hint (the SELECT badge stays a graphic)
a('0421',[(8,3,12,'Muunnostiedot'),(4,10,12,'Muoto')])   # transformation panel (SELECT view): A hint at the bottom, "transformation" under the type name
a('009D',[(0,0,2,'Siirto')]); a('00B1',[(0,0,2,'Voima')])   # transformation type names (Shift, Power) above it
a('04A3',[(4,2,5,'Tyyppi/'),(1,2,8,'Arkisto'),(9,8,13,'/Botti')])
a('04B1',[(8,13,16,'Tyyppi/')]); a('04B3',[(5,13,16,'Tyyppi/')])
a('0423',[(1,2,9,'Johtaja'),(2,2,9,'Botti 2'),(3,2,9,'Botti 3')])
a('0431',[(1,2,9,'Botti 1'),(2,2,9,'Botti 2'),(3,2,9,'Botti 3')])
a('0432',[(1,2,9,'Botti')])
a('0435',[(1,2,9,'Johtaja')]); a('0436',[(1,2,9,'Johtaja'),(2,2,9,'Botti 2')])
a('0437',[(8,2,8,'Drive A'),(9,2,8,'Drive B'),(10,2,8,'Drive C')])
a('0441',[(1,2,9,STAT['装甲']),(3,2,9,STAT['推進']),(5,2,9,STAT['機動']),(7,2,9,STAT['防御']),(9,2,9,STAT['近接']),(11,2,9,STAT['遠隔'])])
a('0442',[(1,2,9,STAT['成功']),(3,2,9,STAT['威力']),(5,2,9,'Kerrat')])
a('0443',[(1,2,9,STAT['成功']),(3,2,9,STAT['威力']),(5,2,9,STAT['充填']),(7,2,9,STAT['放熱'])])
a('0444',[(1,3,9,'Mitalit'),(11,11,15,'Taso/'),(13,11,18,'Seur. tasoon'),(16,11,16,'Medabot/')])   # medal list: title and the green kana of the Medarot panel (level / next level / Medarot)
M45={'のうりょく':'Kyky','メダフォース':'Voima','ローテ':'Rotaatio','じゅくれんど':'Taito','メダリア':'Medalia','もどる':'Paluu'}
a('0457',[(0,13,16,'Valikko',3|0x80),(4,11,15,'Taso/',2),(6,11,18,'Seur. tasoon',2),(9,11,16,'Medabot/',2),(0,4,6,'Kyky',4),(1,4,6,'Kyky',4|0x40)])   # ability screen: (A) menu hint and the kana of the Medarot panel
a('0451',[(2,2,7,'Kyky'),(4,2,7,'Voima'),(6,2,7,'Rotaatio'),(8,2,7,'Taito'),(10,2,7,'Medalia')])
a('0452',[(2,2,7,'Voima'),(4,2,7,'Rotaatio'),(6,2,7,'Taito'),(8,2,7,'Medalia'),(10,2,7,'Paluu')])
a('0453',[(2,2,7,'Rotaatio'),(4,2,7,'Taito'),(6,2,7,'Medalia'),(8,2,7,'Kyky'),(10,2,7,'Paluu')])
a('0454',[(2,2,7,'Taito'),(4,2,7,'Medalia'),(6,2,7,'Kyky'),(8,2,7,'Voima'),(10,2,7,'Paluu')])
a('0455',[(2,2,7,'Medalia'),(4,2,7,'Kyky'),(6,2,7,'Voima'),(8,2,7,'Rotaatio'),(10,2,7,'Paluu')])
a('0456',[(2,2,7,'Kyky'),(4,2,7,'Voima'),(6,2,7,'Rotaatio'),(8,2,7,'Taito'),(10,2,7,'Paluu')])
a('00E1',[(0,0,7,'MFlataus')]); a('00FC',[(0,1,7,'Ei voi')]); a('00FF',[(0,2,7,'Ei voi')])
a('0183',[(14,1,4,'Yht:'),(14,11,18,'Myydään?'),(16,1,4,'Raha'),(16,11,14,'Omat')]); a('0182',[(1,8,11,'Omat')])
for _tm,_t in SKILL.items(): a(_tm,[(0,0,5,_t)])
a('0461',[(4,11,18,'MF-kulu'),(7,11,18,'Taito'),(8,13,18,'/Osuma'),(11,11,18,'Teho')])
POPUP={'0451','0452','0453','0454','0455','0456','0421','009D','00B1'}   # pop-up menus: their labels go into the upper pool tiles (static_labels.asm)
def write_overlay_table():
    sys.path.insert(0,'scripts')
    from common import utils, tilesets
    cm=utils.reverse_dict(tilesets.get_tileset('VWF',override_offset=0x0))
    cm[' ']=0x20   # code 0 is padding in the menu VWF, $20 is a real space
    src=open('game/src/patch/vwf.asm',encoding='utf-8').read()
    def tab(name):
        blk=src.split(name+'::')[1]
        rows=re.findall(r'^\s*db ([0-9, ]+) ;',blk,re.M)[:16]
        return [int(x) for r in rows for x in r.split(',')]
    wide,narrow=tab('VWFDrawLetterTable'),tab('VWFDrawNarrowLetterTable')
    out=['; Generated by scripts/set_static_labels.py, do not edit. See static_labels.asm.','',
         'SECTION "Static Labels Table", ROMX[$6A00], BANK[$C4]','StaticLabelTable::']
    strings=[]
    for tm in sorted(OVERLAY):
        L=[x for x in S if x[0]==tm]
        # The decompress calls name a tilemap by (group, index); several indices can share one tilemap file.
        keys=sorted((int(bk,16),ix) for (bk,ix),l in TT.items() if l and TL.get(l)==tm)
        if not keys: print('no (group,index) for tilemap',tm); sys.exit(1)
        for kg,ki in keys:
            out.append('  db $%02X, $%02X, %d ; %s'%(kg,ki,len(L)|(0x80 if tm in POPUP else 0),tm))
            for k,(t,r,c0,c1,text,*_pp) in enumerate(L):
                flag=(0x80 if (_pp and _pp[0]&0x80) else 0)|(0x40 if (_pp and _pp[0]&0x40) else 0)
                codes=[cm[c] if c in cm else sys.exit('no VWF code for %r in %r'%(c,text)) for c in text]
                wpx=sum(wide[c]+1 for c in codes); npx=sum(narrow[c]+1 for c in codes); n=c1-c0+1
                if npx>n*8+1: print('TOO WIDE even narrow',tm,text,npx,'>',n*8+1); sys.exit(1)
                if wpx>n*8+1 and (kg,ki)==keys[0]: print('narrow font used',tm,text,wpx,'px >',n*8+1)
                lab='StaticLabel_%s_%d'%(tm,k)
                out.append('  db %d, %d, %d ; %s'%(r,c0,n|flag,text)); out.append('  dw %s'%lab)
                if (kg,ki)==keys[0]: strings.append((lab,codes,text))
    out.append('  db $FF'); out.append('')
    for lab,codes,text in strings:
        out.append('%s: db %s, $CB ; %s'%(lab,', '.join('$%02X'%c for c in codes),text))
    open('game/src/version/kabuto/static_labels_table.asm','w',encoding='utf-8',newline='\n').write('\n'.join(out)+'\n')
if __name__=='__main__':
    os.makedirs(BK,exist_ok=True); os.makedirs(BK+'/attr',exist_ok=True)
    for tm in sorted({s[0] for s in S}):
        p=f'gfx/tilemaps/{tm}.txt'
        if not os.path.exists(f'{BK}/{tm}.txt'): shutil.copy(p,f'{BK}/{tm}.txt')
        for af in dict.fromkeys(x for x in attrs.get(tm,[]) if x):
            if not os.path.exists(f'{BK}/attr/{af}.txt'): shutil.copy(f'gfx/attribmaps/{af}.txt',f'{BK}/attr/{af}.txt')
    def rdf(p):
        L=open(p,encoding='latin-1').read().split('\n')
        return L[0],[[int(x,16) for x in re.findall(r'\\x([0-9a-fA-F]{2})',r)] for r in L[1:] if r.strip()],L[-1]==''
    def wrf(p,h,R,trail):
        open(p,'w',encoding='latin-1',newline='').write('\n'.join([h]+[''.join('\\x%02x'%v for v in r) for r in R])+('\n' if trail else ''))
    state={}
    for tm in sorted({s[0] for s in S} - set(SKILL)):
        h,R,tr=rdf(f'{BK}/{tm}.txt'); AF={}
        for fr,fc0,fc1,fv in FIX.get(tm,[]):
            for fc in range(fc0,fc1+1): R[fr][fc]=fv
        for af in dict.fromkeys(x for x in attrs.get(tm,[]) if x):
            AF[af]=rdf(f'{BK}/attr/{af}.txt')
        for t,r,c0,c1,text,*pp in [s for s in S if s[0]==tm]:
            n=c1-c0+1; ids=enc(text)
            if tm not in OVERLAY and len(ids)>n: print('TOO LONG',tm,r,c0,c1,text,len(ids),n); sys.exit(1)
            if c1>=len(R[r]): print('OUT OF ROW',tm,r,c1,len(R[r])); sys.exit(1)
            for i in range(n): R[r][c0+i]=0 if tm in OVERLAY else (ids[i] if i<len(ids) else 0)
            for af,(ah,AR,atr) in AF.items():
                if r<len(AR):
                    for i in range(n):
                        if c0+i<len(AR[r]) and not AR[r][c0+i]&8:
                            AR[r][c0+i]=(AR[r][c0+i] | 8) if tm in OVERLAY else (AR[r][c0] | 8 if AR[r][c0]&8 else 0x0F)   # overlay: keep the palette the cell had
                        if pp and c0+i<len(AR[r]): AR[r][c0+i]=(AR[r][c0+i]&~7)|(pp[0]&7)|8
        if tm=='0457' and '0457' in AF: AF['0457'][1][0][17]=4   # the cell right of the recoloured Valikko label is a plain black background cell
        wrf(f'gfx/tilemaps/{tm}.txt',h,R,tr)
        for af,(ah,AR,atr) in AF.items(): wrf(f'gfx/attribmaps/{af}.txt',ah,AR,atr)
    write_overlay_table()
    print('ok',len(S),'labels')
