"""Worksheet + build for the Finnish translation.

  python3 ws.py sheet NN          -> work/sheet_NN.txt   (rows still to translate)
  python3 ws.py build NN          -> work/out/TextSectionNN.csv + report
  python3 ws.py check FILE.csv    -> width report for any CSV

Answer file work/fi_NN.txt:
  @rowid
  one Finnish line per JP page ('+' = page left empty, text merged elsewhere)
  menus: one option per line
TM (work/tm.json): Original -> Finnish pages, reused for identical rows.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fi_text as F  # noqa: E402

REPO = "/mnt/user-data/uploads/medarot4-tr_loc_FI"
WORK = os.path.join(HERE, "work")
OUT = os.path.join(WORK, "out")
TM_PATH = os.path.join(WORK, "tm.json")
os.makedirs(OUT, exist_ok=True)


def section_path(nn):
    return f"{REPO}/text/dialog/TextSection{nn}.csv"


def load_tm():
    if os.path.exists(TM_PATH):
        return json.load(open(TM_PATH, encoding="utf-8"))
    return {}


def save_tm(tm):
    tmp = TM_PATH + ".tmp"
    json.dump(tm, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    os.replace(tmp, TM_PATH)


def needs_translation(orig):
    return bool(orig) and not orig.startswith("@") and orig != "<FINAL>"


def label(prefix):
    spk = F.speaker_of(prefix)
    if spk is None:
        return "  .."
    if spk == ("CC",):
        return "CLR "
    return (spk[0] + spk[1] + (":" + spk[2] if len(spk) > 2 else "")).ljust(4)


def jp_show(body):
    s = body.replace("<CD>", "⏎")
    return re.sub(r"<&(BUF[0-9A-F]{2})>", r"{\1}", s)


def sheet(nn):
    rows = F.read_csv(section_path(nn))
    h = rows[0]
    oi = h.index("Original")
    tm = load_tm()
    seen = set()
    out = []
    todo = 0
    for r in rows[1:]:
        if not r or r[0].startswith("#"):
            continue
        orig = r[oi]
        if not needs_translation(orig) or orig in tm or orig in seen:
            continue
        seen.add(orig)
        todo += 1
        if F.is_menu(orig):
            opts = orig.split("<CD>")[:-1]
            out.append(f"@{r[0]} MENU (each option <= 72px)")
            for o in opts:
                out.append("    " + jp_show(o))
            continue
        out.append(f"@{r[0]}")
        old_tr = r[h.index("Translated")] if len(r) > h.index("Translated") else ""
        if old_tr and not re.fullmatch(r"(<S..>)?[0-9A-F]{4,6}(<\*..>)?", old_tr):
            ref = re.sub(r"<@[^>]*>|<S..>|<\*..>", "", old_tr)
            ref = re.sub(r"<(CF><D1|CF|D1)>", " // ", ref).replace("<D3>", " ").replace("<CD>", " ")
            out.append(f"   ~ {ref[:400]}")
        seps = F.jp_separators(orig)
        for k, (pre, body, suf) in enumerate(F.jp_pages(orig)):
            mark = "|CF|" if k and seps[k - 1] == "<CF>" else ""
            tail = f"  {suf}" if suf else ""
            out.append(f"{label(pre)}{mark}| {jp_show(body)}{tail}")
    path = os.path.join(WORK, f"sheet_{nn}.txt")
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"{path}: {todo} rows to translate")


def parse_answers(path):
    ans = {}
    cur = None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("@"):
            cur = line[1:].split()[0]
            ans[cur] = []
        elif cur is not None:
            if line.strip() == "":
                continue
            ans[cur].append("" if line.strip() == "+" else line.strip())
    return ans


def build(nn, write_tm=True):
    font = F.Font(REPO)
    src = section_path(nn)
    rows = F.read_csv(src)
    h = rows[0]
    oi, ti = h.index("Original"), h.index("Translated")
    tm = load_tm()
    ans_path = os.path.join(WORK, f"fi_{nn}.txt")
    ans = parse_answers(ans_path) if os.path.exists(ans_path) else {}
    # answers -> TM
    by_id = {r[0]: r for r in rows[1:] if r}
    errors, warnings = [], []
    for rid, pages in ans.items():
        if rid not in by_id:
            errors.append(f"{rid}: no such row")
            continue
        tm[by_id[rid][oi]] = pages
    done = missing = 0
    for r in rows[1:]:
        if not r or r[0].startswith("#"):
            continue
        while len(r) <= ti:
            r.append("")
        orig = r[oi]
        if not needs_translation(orig):
            r[ti] = orig            # @0x... references and <FINAL> copy over
            continue
        if orig not in tm:
            missing += 1
            continue
        try:
            tr = F.assemble_flow(font, orig, tm[orig])
        except Exception as e:  # noqa: BLE001
            errors.append(f"{r[0]}: {e}")
            continue
        probs, lines = F.check(font, tr, menu=F.is_menu(orig))
        if probs:
            errors.append(f"{r[0]}: " + "; ".join(probs))
        if not F.is_menu(orig) and not F.jp_separators(orig) and lines:
            # one box in Japanese: must stay one box (no A-press inside UI text)
            if max(p for p, _, _, _ in lines) > 1:
                errors.append(f"{r[0]}: needs {max(p for p, _, _, _ in lines)} boxes, Japanese has 1: "
                              + " / ".join(t for _, _, _, t in lines))
        elif lines and not F.is_menu(orig):
            jp_boxes = 1 + sum(1 for sep in F.jp_separators(orig))
            fi_boxes = max(p for p, _, _, _ in lines)
            if fi_boxes > jp_boxes + max(1, jp_boxes // 4):
                warnings.append(f"{r[0]}: {fi_boxes} boxes vs {jp_boxes} in Japanese")
        r[ti] = tr
        done += 1
    eol = F.line_ending(src)
    bom = open(src, "rb").read(3) == b"\xef\xbb\xbf"
    F.write_csv(os.path.join(OUT, f"TextSection{nn}.csv"), rows, eol=eol, bom=bom)
    if write_tm and not errors:
        save_tm(tm)
    print(f"TextSection{nn}: {done} rows built, {missing} still untranslated, "
          f"{len(errors)} errors, {len(warnings)} warnings")
    for e in errors[:60]:
        print("  ERR", e)
    for w in warnings[:30]:
        print("  warn", w)
    return errors, missing


def check_file(path):
    font = F.Font(REPO)
    rows = F.read_csv(path)
    h = rows[0]
    oi, ti = h.index("Original"), h.index("Translated")
    bad = 0
    worst = 0
    nlines = 0
    for r in rows[1:]:
        if not r or r[0].startswith("#") or len(r) <= ti:
            continue
        probs, lines = F.check(font, r[ti], menu=F.is_menu(r[oi]))
        nlines += len(lines)
        worst = max([worst] + [l[2] for l in lines if not F.is_menu(r[oi])])
        if probs:
            bad += 1
            print(r[0], probs[:3])
        if re.search(r"<(CD|CF|D1)>", r[ti]) and needs_translation(r[oi]):
            bad += 1
            print(r[0], "uses CD/CF/D1")
    print(f"{os.path.basename(path)}: {nlines} lines, widest {worst}px, {bad} rows with problems")
    return bad


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sheet":
        sheet(sys.argv[2])
    elif cmd == "build":
        build(sys.argv[2])
    elif cmd == "check":
        check_file(sys.argv[2])
    elif cmd == "pages":
        # list answer pages that start a fresh box but need more than 2 lines on their own
        font = F.Font(REPO)
        nn = sys.argv[2]
        rows = {r[0]: r for r in F.read_csv(section_path(nn))[1:] if r}
        ans = parse_answers(os.path.join(WORK, f"fi_{nn}.txt"))
        for rid, pages in ans.items():
            orig = rows[rid][2] if rid in rows else ""
            if F.is_menu(orig):
                continue
            seps = F.jp_separators(orig)
            jp = F.jp_pages(orig)
            spk_prev = None
            for k, pg in enumerate(pages):
                spk = F.speaker_of(jp[k][0]) if k < len(jp) else None
                hard = (k == 0 or seps[k - 1] == "<CF>" or spk == ("CC",)
                        or (spk is not None and spk != spk_prev))
                if spk is not None and spk != ("CC",):
                    spk_prev = spk
                if not pg or not hard:
                    continue
                if k + 1 < len(pages) and not pages[k + 1]:
                    continue      # next page merged into this one on purpose
                fl = F.Flow(font)
                fl.text(F.conv_placeholders(pg))
                _, lines = F.check(font, fl.result())
                if len(lines) > 2:
                    print(f"{rid} p{k}: " + " / ".join(f"[{w}] {t}" for _, _, w, t in lines))
    elif cmd == "widows":
        # flowing groups (pages between hard breaks) whose last box is a single short line
        font = F.Font(REPO)
        nn = sys.argv[2]
        lim = int(sys.argv[3]) if len(sys.argv) > 3 else 40
        rows = {r[0]: r for r in F.read_csv(section_path(nn))[1:] if r}
        ans = parse_answers(os.path.join(WORK, f"fi_{nn}.txt"))
        for rid, pages in ans.items():
            orig = rows[rid][2] if rid in rows else ""
            if F.is_menu(orig) or not F.jp_separators(orig) and len(pages) < 2:
                continue
            seps = F.jp_separators(orig)
            jp = F.jp_pages(orig)
            groups, cur, spk_prev = [], [], None
            for k, pg in enumerate(pages):
                spk = F.speaker_of(jp[k][0]) if k < len(jp) else None
                hard = k and (k - 1 >= len(seps) or seps[k - 1] == "<CF>" or spk == ("CC",)
                              or (spk is not None and spk != spk_prev))
                if spk is not None and spk != ("CC",):
                    spk_prev = spk
                if hard and pg:
                    groups.append(cur); cur = []
                if pg:
                    cur.append(pg)
            groups.append(cur)
            for g in groups:
                if not g:
                    continue
                fl = F.Flow(font)
                fl.text(F.conv_placeholders(" ".join(g)))
                _, lines = F.check(font, fl.result())
                if len(lines) >= 3 and len(lines) % 2 == 1 and lines[-1][2] < lim:
                    print(f"{rid}: ...{lines[-2][3]} / [{lines[-1][2]}] {lines[-1][3]}")
    elif cmd == "joins":
        # soft joins where the previous page ends without punctuation and the next starts uppercase
        nn = sys.argv[2]
        rows = {r[0]: r for r in F.read_csv(section_path(nn))[1:] if r}
        ans = parse_answers(os.path.join(WORK, f"fi_{nn}.txt"))
        for rid, pages in ans.items():
            orig = rows[rid][2] if rid in rows else ""
            if F.is_menu(orig):
                continue
            seps = F.jp_separators(orig)
            jp = F.jp_pages(orig)
            spk_prev = None
            prev = None
            for k, pg in enumerate(pages):
                spk = F.speaker_of(jp[k][0]) if k < len(jp) else None
                hard = k and (k - 1 >= len(seps) or seps[k - 1] == "<CF>" or spk == ("CC",)
                              or (spk is not None and spk != spk_prev))
                if spk is not None and spk != ("CC",):
                    spk_prev = spk
                if not pg:
                    continue
                if k and not hard and prev and re.search(r"[A-Za-z0-9ÅÄÖåäö\"]$", prev) and re.match(r"[A-ZÅÄÖ{(]", pg):
                    print(f"{rid} p{k}: ...{prev[-30:]} | {pg[:30]}")
                prev = pg
    elif cmd == "w":
        font = F.Font(REPO)
        for cand in sys.argv[2:]:
            fl = F.Flow(font)
            fl.text(F.conv_placeholders(cand))
            _, lines = F.check(font, fl.result())
            print(" / ".join(f"[{w}] {t}" for _, _, w, t in lines), f"  => {len(lines)} lines")
