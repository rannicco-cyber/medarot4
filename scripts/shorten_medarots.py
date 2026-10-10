#!/usr/bin/env python3
"""Medarot names (list 15) are copied into 9 byte dialog buffers (BUF00-02), so they must be at
most 8 characters. Applies the short forms to text/fi_work/names/Medarots.txt (index -> name)."""
import re
S="""3 FlyFalco|4 YngSparr|6 BlkRover|7 SemiCica|8 HdLocust|9 StalBoat|13 NervBird|14 ChairPix|15 BloodStk|16 WhtGrous|17 MedaJupi|18 BeatBrth|19 NeoSakur|20 FlySquir|21 Shrimprs|22 LimboMam|24 GODeath|26 Changeln|28 ChgGargo|29 HoodWtch|30 FloatSpn|31 CryBansh|33 GodEmper|34 Naturaly|35 Trilobit|36 ManMamth|39 HamAnemo|40 Herokerb|41 Durahors|45 LitlDeer|47 Stidriar|48 LinkCrkt|49 MedaEart|52 Smilodon|53 WarBunni|55 ArcBeetl|57 Ambigus2|58 AsltTyrn|60 PrplKala|61 WireAlie|62 DashRapt|63 FrilFril|64 BlckStag|66 Prem 2K|71 LiteChee|72 StryWolf|73 VaporRai|74 Saikachi|76 BlckBeet|78 BrnBison|80 AutoCrus|81 PassGhou|82 LastSail|83 BraveNrs|85 GallLady|86 BunnyMin|89 HollyOrc|90 RoyalMai|91 PrimLotu|92 HoneyFrc|95 MedaCome|96 MedaUran|97 MedaNept|98 MedaPlut|100 DarkPant|104 ByeByeKo|105 Contract|106 GradeKab|107 ChildSit|108 HiGiraff|109 HumpCame|112 Centiped|113 HairyIns|114 BravePol|115 BraveRes|116 BraveFir|118 PotatoIn|119 MedaVenu|120 EarthBra|121 LickTurt|124 AtckTrik|125 EleRange|126 MiracSew|127 DengrRol|128 LandReac|129 MedaSatu|130 BlueHaun|131 SoftAmoe|133 ShineSea|136 Chronofo|138 BustRoya|139 SeaCatch|140 SeaMonst|141 WaterBea|142 OilSlide|143 CozyHors|145 DolDolph|149 MedaMerc|152 AirWyver|154 WintGull|155 Windmilt|156 CrocoPro|157 UnderLoc|161 SporPara|165 GrasPitc|167 AirCenta|178 ThredDog|179 BadHacke|183 TyrlBeet|185 ArcBeetD|187 GotsHari|188 Blossoma|191 BallPand|193 LeakDrak|196 GrtFathr|198 GreekHea|199 Chibemot|200 DaruDaru|201 RockLnch|203 SecretSh|204 Attracto|206 MiliLevi|210 ClearPur|211 BettyBea|212 MistyGho|214 BeastMst|215 RedMatad|216 Kanehach|218 FlwrChar|222 BlackMai|226 GoofBull|227 WondrAng|230 PrimBaby|231 NatrlClr|232 TaraCrab|233 RabiWomb|235 StoneMir|237 GrtMothr|238 ArmaPala|239 KaoLante|240 GentlHrt|241 UnknwEgg|245 BottomFl|249 ShinSabe"""
M={int(a):b for a,b in (x.split(' ',1) for x in S.split('|'))}
p='text/fi_work/names/Medarots.txt'
raw=open(p,encoding='utf-8').read()
L=raw.split('\n')
for i,n in M.items():
    assert len(n)<=8,(i,n)
    L[i]=n
bad=[(i,x) for i,x in enumerate(L) if len(x.rstrip('\r'))>8]
assert not bad,bad
seen={}
for i,x in enumerate(L):
    x=x.rstrip('\r')
    if x and x in seen: print('dup',x,seen[x],i)
    seen[x]=i
open(p,'w',encoding='utf-8').write('\n'.join(L))
print(len(M),'shortened')
