#!/usr/bin/env python3
"""Finnish replies of the Medarot talk screen (START: Kumppani). The reply is copied into BUF13 ($CCB1) from
bank F7: six personality tables (pointers at $555A -> one table of 32 pointers each, one reply per question
of TextSection15). The original strings are Japanese; the pointer tables are rewritten here and the
Finnish strings go to the free space at the end of the bank. BUF13 has 31 bytes ($CCB1-$CCCF), so each
reply is at most 29 letters. Writes game/src/version/kabuto/talk_replies.asm."""
import os,sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
sys.path.insert(0,'scripts')
from common import utils, tilesets
cm=utils.reverse_dict(tilesets.get_tileset('VWF',override_offset=0x0))
cm[' ']=0x20
TABLES=[0x556C,0x5786,0x597A,0x5BB9,0x5DE6,0x601C,0x623D,0x6446,0x664B]
R=[
# 0: Metabee, cocky
["Ihan super tyytyväinen!","Kyllä sä osaat kun yrität","Tää kelpaa kai mulle","Ei tää nyt oikein riitä...",
 "Hei... tosissaanko sä?","Aivan huippua!","Ihan hyvä fiilis, eikö?","...Joo, voi olla",
 "Jotain vaan puuttuu","Ei tää nyt hyvä oo, eihän?","Ei tarttis edes kysyä!","Totta kai!",
 "Mistä mä tiedän?","Ei kyllä siltä vaikuta","Ei todellakaan vaikuta!","Täydellistä! Ei valittamista!",
 "Tällä me pärjätään!","Kokeile yksi kerrallaan","Mieti nyt vähän, pyydän...","Ei tästä oo mitään apua...",
 "Hyvältä näyttää!","Joo, kyllä tää onnistuu?","Ei sillä oo väliä","Mua ei kiinnosta...",
 "...Huoh, mikä pettymys","Tuo! Tuo on hyvä! Varmasti!","En voi ottaa tosissani","Mitä sä oikein höpiset...",
 "...Mitä mä tohon sanoisin","Pitää robotella enemmän!","Unessa voitin urheilukisan!","Pitäis kokeilla jotain uutta"],
# 1: stern soldier
["Tila on tyydyttävä","Eipä hullumpaa lainkaan","Tämä on vielä siedettävää","Vielä pitää yrittää enemmän",
 "Ei tämä ole ollenkaan hyvä","Ei ongelmia lainkaan","Yllättävän hyvä tunnelma","Suunnilleen kohtalaista",
 "Ei se pidä paikkaansa","Turha edes vastata","Ilman muuta, turha kysyä","Niin, kai se on niin",
 "Onkohan se noin?","En usko niin","En lainkaan usko niin","Aivan täydellistä",
 "Ei pitäisi olla ongelmia","Onko tämä sinusta ihan ok?","Kysy omalta sydämeltäsi","Eihän sellainen voi olla!",
 "Tästä ei ole huomautettavaa","Mielestäni varsin hyvä","Vaikea kysymys","Ei kovin hyvä",
 "Tämä on aivan kehnoa","Mielestäni huippusuoritus","Sanon suoraan: surkea","...Sanoitko jotain?",
 "Erinomaista","Onko mitään virkistävää?","Uni, jossa taistelin kanssasi","Älä lannistu vaikeuksissa!"],
# 2: rascal
["Hitto, olet loistava, pomo!","Tän voisin melkein hyväksyä","No jaa, kelpaa se","Tee nyt jotain tälle, jooko?",
 "Pomo, ei sua kiinnosta, vai?","Tää on ihan huikeeta!","Hyvä jos susta tuntuu","Menettelee vaan",
 "Älä nyt tuollaista kysy!","Jos noin luulet, oot hölmö!","Totta kai, ei tartte kysyä","No joo, kai niin",
 "Mistäs minä tiedän?","Ihan sama...","Mä ajattelen mitä haluan","Ei tässä oo valittamista",
 "Vaikuttaa ihan hyvältä","Miks sä sellaista kysyt?","Ei kuulu mulle!","Ei, ei! Ei kelpaa!",
 "Tykkään tästä oikeesti","Hyvähän tää on!","Ei kumpaakaan oikein","Tee nyt jotain, jooko",
 "Et sä tajua mitään, pomo","Hyvä hyvä, ihan jees!","Ei jaksa, kotiin vaan","Ei se mulle kuulu, eihän?",
 "Mulla menee kuten aina","Puuhun kiipeämään!","Unessa oli paljon robotteja","Älä laita outoja osia!"],
# 3: old man
["Tämäpä on ihailtavaa!","Hmm! Hyvältä näyttää","No, kai tämä kelpaa","Hiukan hutaistu, eikö?",
 "Tähän ei pidä tyytyä","Tämän parempaa ei ole!","Ei vaikuta ongelmilta","Minun mielestäni... hmm",
 "Ei se hyvältä näytä","Tämä ei lupaa hyvää","Aivan niin! Ei huolta!","Totta kai, totta kai!",
 "Kaipa niin saattaa olla","En minä tiedä","Eipä taida olla niin","Ei tästä voi valittaa!",
 "Hyvin kai tämä menee","Vielä on parantamisen varaa","Onkohan tämä oikein hyvä...","Eihän näin... voi voi",
 "Minusta tämä on hyvä!","Kyllä tämä hyvältä tuntuu","Kokeile vaikka kaikenlaista","En minä sano mitään",
 "Lopeta tämä, pyydän...","Mahtavaa, sanat loppuvat!","Päätä huimaa, kaadun...","Vaikka noin sanotkin...",
 "Ei näytä olevan vikaa","Niinpä niin...","Uneksin olevani nuori taas","Osia on liikaa muistaa"],
# 4: lady
["Aivan ihanaa!","Se on ahkeruutesi ansiota","Matkaa on vielä jäljellä","Yritetään vielä vähän lisää",
 "Voi voi, tämä on hankalaa...","Kyllä, todella!","Suloisen ihana tunnelma","Öh... minusta se on hyvä",
 "Jokin tuntuu olevan pielessä","En tiedä mitä tekisin...","Kyllä! Ehdottomasti!","Kyllä, minusta niin",
 "En oikein ymmärrä","Niinkö... luuletko?","Anteeksi, minä...","Luotan sinuun täysin",
 "Minusta se on hyvä","Eiköhän se onnistu?","Jokin jää vähän vaivaamaan","En ole yhtään varma...",
 "Todella hyvä tunnelma","Ei tarvitse huolehtia","Mitäköhän tämä on?","Onkohan tämä näin hyvä...?",
 "Ei se ole hyvä...","En kestä, ihanaa!","Minusta tämä on aivan liikaa","Mistä oikein on kyse?",
 "Vointi? ...En oikein tiedä","Kunhan olen kanssasi","Unohdan ne aamulla...","Voi, se on noloa..."],
# 5: boy
["Mahtavaa! Ei valittamista!","Tyytyväinen, tyytyväinen!","Mustakin tää on ihan ok","Yritetään vähän enemmän!",
 "En tykkää tästä!","Joo! Täydellistä!","Hyvä! Tällainen fiilis!","Aika hyvä fiilis?",
 "Ei kyllä oikein tää...","Hmm... ei kai kelpaa...","Joo! Tietysti!","Joo, mustakin niin",
 "Kai se niin on?","En mä noista ymmärrä","Ei se ole niin!","Täydellinen yhdistelmä!",
 "Ei hätää! Ole itsevarma!","Ei ole huono","Mua vähän pelottaa...","Mieti vielä paremmin",
 "Ei ihme, että valitsin sut!","Juuri tällaista!","Tää? Häh? Niinkö?","Mä en ihan tykkää tästä",
 "Ihan kauheaa!","Mä tykkään tästä tosi paljon","Ei! Ei! Ei kelpaa!","En mä tajua vaikeita juttuja",
 "Entäs sä? Miten sulla menee?","Hmm, en tiedä...","Uin unessa kalana!","Voiko pilviä syödä?"],
# 6: smug, cool ("fufun", "jan")
["Hehheh! Ei hassumpaa!","No, aika hyvä on, eiks?","Voi ollakin hyvä, mutta...","Yritä nyt vähän tosissaan...",
 "Sä oot ihan kiva tyyppi...","Ihan huikeeta, sanoisin!","Niinpä tietysti...","Joo, ihan ok kai",
 "Fiilis ei ehkä natsaa...","Ei hyvä, ei yhtään!","Tottakai, ihan selvä!","Joo joo, kai...",
 "Haluatko että vastaan?","En oo koskaan vastannut tohon","Ei ei ei, ei yhtään!","Siis jätätkö kaiken mulle?",
 "Tää taitaa olla ihan ok","Ehkä, ehkä ei...","Tee ihan mitä haluat vaan","Ei tää onnistu yhtään",
 "Hyvä hyvä, ihan jees!","Aika taitavaa, täytyy myöntää","Onko tää jonkun jäljitelmää?","Jotenkin ikävä fiilis tässä",
 "Voi ei, ihan kamalaa...","Sä oot ihan huippu, ehkä!","Lopeta jo! Mä suutun kohta!","Häh? Mitä se on?",
 "Istuessa alkaa väsyttää","Tee mitä haluat...","Joku taisi sanoa noin...","Aurinkoa vois ottaa joskus"],
# 7: rough and tough, Metabee style
["Aivan mahtavaa, jätkä!","No niinpä, kyllä se onnistuu!","Ihan kelpo, eikö!","Onko toi muka tarpeeks?!",
 "Ei voi olla totta, hei!","Täydellinen, jee!","Tällä pärjätään kyllä!","Ei hyvä eikä huono",
 "Voi voi, anna jo olla!","Eihän se nyt noin ole!","Mitä sä höpiset, tottakai!","Niin! Katsomalla sen näkee!",
 "Niinhän se taitaa olla!","Älä puhu pötyä, kuule!","Ei, ei yhtään!","Vau, sait mut sanattomaksi!",
 "Tällaisena se kelpaa kyllä!","Tämmöstäkö se on?","Mietin kyllä tuota...","Hei, yritä nyt tosissasi!",
 "Ei mulla oo valittamista!","Hyvä, hyvä!!","Ihan tavallista","Tee nyt jotain tälle...",
 "Et kai aio jatkaa näin?","Jes, nyt se alkaa sujua!","Ihan surkeeta, kaveri!","Mitä sä oikein horiset!",
 "Ihan huippukunnossa!!","Robotteluahan se, tietty!!","Unessa satoi vesimelonia!","Me ollaan paras kopla, jee!"],
# 8: haughty, stern
["Hmph, ei hassumpaa minulta","Ei minulla ole valittamista","Tunnustan voimasi","Yrität tosissasi, näkyy",
 "Älä ärsytä minua","En hyväksy enempää tästä","En pidä tästä lainkaan","Ei tämä ihan huono ole",
 "Älä sano tuollaista","...Hmph!","Etkö jo itse tiedä?","Niin kai, no",
 "Ei se ole häirinnyt","Tuo kyllä tehosi minuun","Älä kysy turhia","Näyttää hyvältä, helpotti",
 "Tällaista se lienee","Tällä siis mennään!","Riippuu vastauksestasi","Pidätkö tätä riittävänä?!",
 "Hyvältä tuntuu","En sano ettei kelpaisi","Kokeile vastata paremmin","Ja sinäkö medarotisti?",
 "Sanat loppuvat kesken","Minulla on tiukat vaatimukset","......","Ei kuulu minulle",
 "Ei huono","Ei mitään erityistä...","Nukuin päiväunia unessa","Haluatko olla kanssani?"],
]
def enc(s):
    out=[]
    for ch in s:
        m={'ä':2,'ö':4,'Ä':1,'Ö':3}
        if ch in m: out.append(m[ch])
        elif ch in cm: out.append(cm[ch])
        else: sys.exit('no VWF code for %r in %r'%(ch,s))
    return out
asm=['; Generated by scripts/gen_talk_replies.py, do not edit. See that script.','']
NT=len(TABLES)
for g,tab in enumerate(TABLES):
    assert len(R[g])==32,(g,len(R[g]))
    asm.append('SECTION "Talk Reply Pointers %d", ROMX[$%04X], BANK[$F7]'%(g,tab))
    for k in range(32): asm.append('  dw TalkReply_%d_%02d'%(g,k))
asm.append('')
# Free space for the texts: the original Japanese strings behind each pointer table (a table is 64 bytes, its
# strings follow up to the next table; the last block ends where the particle table at $6830 starts) and the
# unused end of the bank.
CH=[]
for i,t in enumerate(TABLES):
    end=TABLES[i+1] if i+1<NT else 0x6830
    CH.append([t+64,end])
CH.append([0x6D13,0x8000])
items=[]
for g in range(NT):
    for k in range(32):
        st=R[g][k]; b=enc(st)
        if len(b)>29: sys.exit('too long (%d) %d/%d %r'%(len(b),g,k,st))
        items.append((g,k,st,b))
place=[[] for _ in CH]
for it in items:
    n=len(it[3])+1
    for c in CH:
        pass
    for ci,c in enumerate(CH):
        if c[1]-c[0]>=n:
            place[ci].append(it); c[0]+=n; break
    else: sys.exit('out of space')
total=sum(len(it[3])+1 for it in items)
print('texts',total,'bytes in',len(CH),'blocks')
for ci,pl in enumerate(place):
    if not pl: continue
    start=(TABLES[ci]+64) if ci<NT else 0x6D13
    asm.append('SECTION "Talk Reply Texts %d", ROMX[$%04X], BANK[$F7]'%(ci,start))
    for (g,k,st,b) in pl:
        asm.append('TalkReply_%d_%02d: db %s, $CB ; %s'%(g,k,', '.join('$%02X'%x for x in b),st))
asm.append('')
asm.append('; BUF14 holds the skill name at $CCA0. The two particle strings of the Japanese text were copied to $CCA6 and')
asm.append('; $CCAA after it, which cut off skill names of six letters or more. Nothing reads them: the copies become no-ops.')
for a in (0x4B16,0x4B2A,0x50A9,0x50BD):
    asm.append('SECTION "Talk Particle Copy %04X", ROMX[$%04X], BANK[$F7]'%(a,a)); asm.append('  nop')
open('game/src/version/kabuto/talk_replies.asm','w',encoding='utf-8',newline='\n').write('\n'.join(asm)+'\n')
