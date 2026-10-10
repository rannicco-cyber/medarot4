import re,os
os.chdir('/'.join(os.path.abspath(__file__).split('/')[:-3]))
for f in 'abcde':
    exec(open(f'text/fi_work/mnm_{f}.py',encoding='utf-8').read())
miss=set()
for n in ['Medarotters','Medarotters2','EncounterNames','Medaforce','MusicTitles']:
    out=[]
    for ln in open(f'text/fi_work/ptrlists_ja/{n}.txt',encoding='utf-8-sig').read().split('\n')[1:]:
        m=re.match(r'^(\d+),(.*)$',ln)
        if not m: continue
        i=int(m.group(1)); jp=m.group(2).rsplit(',',1)[-1].strip()
        while len(out)<i: out.append('')
        if n=='MusicTitles':
            t=MUS.get(jp)
            if t is None:
                t=jp
                if re.search(r'[^\x00-\x7f]',jp): miss.add(jp)
        else:
            t=M.get(jp)
            if t is None: miss.add(jp); t=jp
        out.append(t)
    open(f'text/fi_work/names/{n}.txt','w',encoding='utf-8').write('\n'.join(out)+'\n')
    print(n,len(out))
print('MISSING',miss)
