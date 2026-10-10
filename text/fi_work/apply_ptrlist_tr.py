import sys,re,io
# NOTE: the old buffer length per caller is roughly (longest Japanese name + 1), so keep names no longer than the longest original (Skills 5, Attributes 6, Personalities 5, Items 8).
# usage: apply_ptrlist_tr.py ListName   (reads translations from the dict below)
T={}
T['Items']=["Robomit.","Kartta","Radio","4 kelloa","M3-passi","Ennustus","Eväspaki","Uimapuku","Passikrt","Passipst","Ratti","Periskop","Siivet","Mekko","Piika","D-avain","Unispray","Toranasu","Eväs","MustaBOX","Haori","Rengas","H-avain","Munapakk","Byakuasu","ID-kortt","M-merkki","Todistus","Munaraha","Punakäär","Sinikäär","Keltakää","Mustakää","Yölasit","I-kengät","A-vyö","Lennokki","Nimmari"]
T['Medals']="Kuwagata,Kabuto,Dino,Ajoneuvo,Lintu,Peto,Kasvi,Meri,Mirage,Työ,Itä,Etelä,Länsi,Pohjois,Raha,Aika,Aqua,Liekki,Tuuli,Maa,Parannus,Sankari,Noita,Samurai,B-Kuwa,B-Kabuto,Kuningas,Jätkä,Rouva,Ässä,Kulttuur,Kone,Silmä,Jalokivi,Melodia,Sana".split(',')
T['Attacks']="Miekka,Vasara,Sinetase,Kivääri,Gatling,Leimaase,Laser,Säde,Ohjus,Napalm,Murto,Puristus,Tuho,Uhri,Aikaisku,Staatti,Bugi,Virus,Aalto,Pidätys,Tuli,Sulatus,Ukkonen,Jäädytys,Lasku,Kaipuu,L-isku,Murhaaja,Suoja,Täyssuoj,Alisuoja,Ilmatorj,Meritorj,Havainto,Naamio,Imeytys,Läheansa,Ampuansa,Voimaist,Havpurku,Naamipur,Kertaesto,Ensiapu,Ristisar,Risti A,Risti B,Risti C,Haittapur,Ansapurk,Voimahall,Parannus,Herätys,Elvytys,Tasoimu,Täysesto,Siunaus,Kaato,Opt.esto,Räj.esto,Painoest,Tilapurk,JatkoKor,Vähennys,Heijast,Vastaisk,Painohal,Tunnist,Pikaval,Itsekorj,Pikalat,Apulatau,Lataus,Latausim,Kaatuma,Voima+,Muutos,Muu(Nop),Muu(Voi),Muu(Til),Muu(Tuk),Muu(Par),Muu(Apu),Sinpurku,Maasto,Etupurku,Käytkiel,Sekavuus,Kertaimu,Väistkie,Puolkiel,Voimaimu,Leimaus,Houkutus".split(',')
T['Terrain']="Aavikko,Hiekkakuoppa,Piikkikuoppa,Vuoristo,Tulivuori,Laava,Metsä,Viidakko,Puumeri,Kaupunki,Stadion,Näyttämö,Vesi,Jäätikkö,Syvänmeri,Avaruus,Kyber,Mikro".split(',')
T['Skills']="Isku,Ammu,Hurja,Tähdä,Suoja,Ansa,Hoito,Erik.,Tuki,Häirä".split(',')
T['Attributes']="Nopeus,Voima,Tila,Suoja,Ansa,Hoito,Purku,Muutos,Häirä".split(',')
T['Movement']="Lento,Leijunta,Monijalka,Kaksijalka,Ajoneuvo,Tankki,Sukellus".split(',')
T['Personalities']="Nopea,Voima,Taito,Suoja,Vähen,Muuta,Arpa".split(',')
name=sys.argv[1]
p=f'text/ptrlists/{name}.txt'
src=f'text/fi_work/ptrlists_ja/{name}.txt'
raw=open(src,'rb').read().decode('utf-8')
bom=raw.startswith('﻿')
lines=raw.split('\n')
tr=T[name]; out=[]; n=0
for ln in lines:
    m=re.match(r'^(\d+),(.*)$',ln)
    if m and int(m.group(1))<len(tr):
        i=int(m.group(1)); rest=m.group(2)
        if name=='Items':
            flags=rest.rsplit(',',1)[1]
            ln=f"{i},{tr[i]}\\xcb,{flags}"
            assert len(tr[i])<=8,(i,tr[i])
        else:
            ln=f"{i},{tr[i]}"
        n+=1
    out.append(ln)
assert n==len(tr),(name,n,len(tr))
open(p,'wb').write('\n'.join(out).encode('utf-8'))
print(name,n)
