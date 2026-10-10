import sys; sys.path.insert(0,'.')
import fi_text as F, ws
font=F.Font(ws.REPO)
rows=F.read_csv(ws.OUT+"/TextSection"+sys.argv[1]+".csv")
ans=ws.parse_answers(ws.WORK+"/fi_"+sys.argv[1]+".txt")
tm=ws.load_tm()
for r in rows[1:]:
    if '<CD>' not in r[2] and r[2] in tm and not r[2].startswith('@'):
        _,lines=F.check(font,r[3])
        if lines and (len(lines)>1 or lines[0][2]>112): print(r[0], [(l[2],l[3]) for l in lines])
