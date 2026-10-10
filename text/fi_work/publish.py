"""Copy finished sections + work files to the outputs folder and print the commit list."""
import json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
O = '/mnt/user-data/outputs/fi_translation'
DEV = r'C:\Users\Lenovo\Desktop\medarot4-tr_loc_FI'
mt = json.load(open(os.path.join(HERE, 'work/mtimes.json')))
os.makedirs(O + '/dialog', exist_ok=True); os.makedirs(O + '/fi_work', exist_ok=True)
files = []
done = []
pf = os.path.join(HERE, 'work/progress.txt')
if os.path.exists(pf):
    done = open(pf).read().split()
for nn in sys.argv[1:]:
    shutil.copy(os.path.join(HERE, f'work/out/TextSection{nn}.csv'), f'{O}/dialog/TextSection{nn}.csv')
    has_fi = os.path.exists(os.path.join(HERE, f'work/fi_{nn}.txt'))
    if has_fi:
        shutil.copy(os.path.join(HERE, f'work/fi_{nn}.txt'), f'{O}/fi_work/fi_{nn}.txt')
    e = {"devicePath": DEV + rf'\text\dialog\TextSection{nn}.csv', "stagedPath": f'{O}/dialog/TextSection{nn}.csv'}
    if nn in mt and nn not in done: e["expectedMtimeMs"] = mt[nn]   # first write only
    files.append(e)
    if has_fi:
        files.append({"devicePath": DEV + rf'\text\fi_work\fi_{nn}.txt', "stagedPath": f'{O}/fi_work/fi_{nn}.txt'})
    if nn not in done: done.append(nn)
done = sorted(set(done))
open(pf, 'w').write(' '.join(done) + '\n')
shutil.copy(pf, f'{O}/fi_work/progress.txt')
for f in ('work/tm.json', 'work/glossary.md', 'fi_text.py', 'ws.py', 'render.py', 'fixrows.py', 'pagefix.py', 'publish.py', 'joinfix.py', 'd2b.sh', 'chk09.py', 'jp.py'):
    shutil.copy(os.path.join(HERE, f), f'{O}/fi_work/' + os.path.basename(f))
    files.append({"devicePath": DEV + r'\text\fi_work' + '\\' + os.path.basename(f), "stagedPath": f'{O}/fi_work/' + os.path.basename(f)})
files.append({"devicePath": DEV + r'\text\fi_work\progress.txt', "stagedPath": f'{O}/fi_work/progress.txt'})
print(json.dumps(files))
