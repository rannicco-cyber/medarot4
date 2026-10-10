"""Medarot 4 Finnish text tools: encoding, VWF widths, D3-only layout and checks.

Width model (game/src/patch/vwf.asm, VWFAutoNL):
  each glyph advances width[font][code] + 1 px, a space ($00) advances 3 px.
  At every space the engine measures   x_before_space + 3 + next_word
  and inserts its own <D3> when that is > $89 (137).  So a laid-out line is
  safe when the sum of all advances on it is <= 137 (17 tiles = 136 px visible).
  <D3> on line 1 = new line, on line 2 = wait for A + new page.
"""
import csv
import io
import os
import re

LIMIT = 0x89          # VWFAutoNL threshold
MENU_LIMIT = 72 + 1   # choice menu option: 9 tiles of text (+ trailing gap)
DEFAULT_BUF = 48      # 8 characters x (5 + 1) px, the name-entry maximum

BUF_BUDGET = {
    "BUF03": 48,      # player name (name entry caps at 8 characters)
    "BUF15": 48,      # partner medal name (same name entry)
    "BUF06": 30,      # numbers / money
    "BUF07": 15,      # item count
    "BUF10": 25, "BUF11": 25, "BUF12": 25,   # scores / ranks
}


def _load_widths(vwf_asm):
    tables = []
    cur = None
    for line in open(vwf_asm, encoding="utf-8"):
        s = line.split(";", 1)[0].strip()
        if re.match(r"^VWFDraw\w*LetterTable::", s):
            cur = []
            tables.append(cur)
            continue
        if cur is not None and s.startswith("db "):
            cur.extend(int(v) for v in s[3:].split(","))
            if len(cur) >= 256:
                cur = None
        elif cur is not None and s and not s.startswith("db"):
            cur = None
    assert tables and all(len(t) == 256 for t in tables), [len(t) for t in tables]
    return tables


def _load_chars(vwf_lst):
    tbl = {}
    off = 0
    for line in open(vwf_lst, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line:
            continue
        if line.startswith("|") and len(line) > 1:
            off = int(line[1:], 16)
            continue
        tbl[off] = line
        off += 1
    tbl[0] = " "                       # dialog2bin encodes spaces as $00
    rev = {}
    for code, ch in tbl.items():
        rev[ch] = code
    return rev


class Font:
    def __init__(self, repo):
        self.widths = _load_widths(os.path.join(repo, "game/src/patch/vwf.asm"))
        self.chars = _load_chars(os.path.join(repo, "scripts/res/tilesets/VWF.lst"))

    def adv(self, ch, font=0):
        code = self.chars.get(ch)
        if code is None:
            raise KeyError(ch)
        return self.widths[font][code] + 1


# ---------------------------------------------------------------- tokens

TOKEN = re.compile(r"<[^>]*>|.", re.S)


def tokens(text):
    return TOKEN.findall(text)


def word_width(font, word, fontno=0, buf_budget=None):
    """Advance of a run of tokens without spaces."""
    w = 0
    last_buf = 0
    for t in tokens(word):
        if t.startswith("<"):
            if t.startswith("<&"):
                name = t[2:-1]
                last_buf = (buf_budget or BUF_BUDGET).get(name, DEFAULT_BUF)
                w += last_buf
            elif t.startswith("<#w"):
                w += int(t[3:-1]) - last_buf
                last_buf = 0
            elif t.startswith("<f"):
                fontno = int(t[2:-1], 16)
            continue
        w += font.adv(t, fontno)
    return w


# ---------------------------------------------------------------- check

def check(font, text, menu=False):
    """Simulate the engine on a translated string.
    Returns (problems, lines) where lines = [(page, line, width, text)]."""
    problems = []
    lines = []
    if text.startswith("@") or text in ("", "<FINAL>"):
        return problems, lines
    body = text[len("<NOTERM:"):-1] if text.startswith("<NOTERM:") else text
    page, line, x, buf, fontno = 1, 1, 0, "", 0
    last_buf = 0
    toks = tokens(body)

    def end_line():
        lines.append((page, line, x, buf))
        limit = MENU_LIMIT if menu else LIMIT
        if x > limit:
            problems.append(f"p{page} l{line}: {x}px > {limit}: {buf}")

    i = 0
    while i < len(toks):
        t = toks[i]
        if t in ("<D3>", "<CD>", "<CF>", "<D1>"):
            end_line()
            if t == "<CD>" and line == 2 and not menu:
                problems.append(f"p{page}: <CD> on line 2 redraws over line 2")
            if t == "<D3>":
                if line == 1 and not menu:
                    line = 2
                elif not menu:
                    page, line = page + 1, 1
            elif t == "<CD>":
                line = 2
            else:
                page, line = page + 1, 1
            x, buf = 0, ""
        elif t.startswith("<*"):
            break
        elif t.startswith("<"):
            if t.startswith("<&"):
                last_buf = BUF_BUDGET.get(t[2:-1], DEFAULT_BUF)
                x += last_buf
            elif t.startswith("<#w"):
                x += int(t[3:-1]) - last_buf
                last_buf = 0
            elif t.startswith("<f"):
                fontno = int(t[2:-1], 16)
            elif t.startswith("<K") or t.startswith("<$"):
                problems.append(f"raw code {t}")
            buf += t if t.startswith("<&") else ""
        elif t == " ":
            # engine's own wrap check at this space
            j = i + 1
            word = ""
            while j < len(toks) and toks[j] != " " and not re.match(r"<(D3|CD|CF|D1|\*..)>", toks[j]):
                word += toks[j]
                j += 1
            ww = word_width(font, word, fontno)
            if not menu and x + 3 + ww > LIMIT:
                problems.append(f"p{page} l{line}: engine would wrap before '{word}' ({x}+3+{ww})")
            x += font.adv(" ")
            buf += " "
        else:
            try:
                x += font.adv(t, fontno)
            except KeyError:
                problems.append(f"no glyph for {t!r}")
            buf += t
        i += 1
    if buf or x:
        end_line()
    return problems, lines


# ---------------------------------------------------------------- JP structure

PAGE_SPLIT = re.compile(r"<CF><D1>|<CF>|<D1>")
PREFIX = re.compile(r"^((?:<@[^>]*>|<S..>)*)")
SUFFIX = re.compile(r"((?:<S..>)*(?:<\*..>)?)$")


def jp_separators(original):
    return PAGE_SPLIT.findall(original)


def speaker_of(prefix):
    """Speaker key from a page's portrait code: (side, id) or (side, FF, npc)."""
    m = None
    for m in re.finditer(r"<@(\w\w),([0-9A-Fa-f]{2}),([0-9A-Fa-f]{2})>", prefix):
        pass
    if not m:
        return None
    side, pid, expr = m.group(1).upper(), m.group(2).upper(), m.group(3).upper()
    if side == "CC":
        return ("CC",)
    return (side[0], pid, expr) if pid == "FF" else (side[0], pid)


def jp_pages(original):
    """Split a JP original into pages: [(prefix, body, suffix)]; body keeps <CD> and <&..>."""
    pages = []
    parts = PAGE_SPLIT.split(original)
    for k, p in enumerate(parts):
        pre = PREFIX.match(p).group(1)
        rest = p[len(pre):]
        suf = SUFFIX.search(rest).group(1) if k == len(parts) - 1 else ""
        body = rest[: len(rest) - len(suf)] if suf else rest
        pages.append((pre, body, suf))
    return pages


def is_menu(original):
    return bool(re.search(r"<CD>$", original)) and "<@" not in original


def is_trailing_cd(original):
    return bool(re.search(r"<CD>(<S..>)*<\*..>$", original))


# ---------------------------------------------------------------- layout

def wrap_page(font, text, start_line=1):
    """Greedy-wrap one page of Finnish. Returns (layout_text, end_line, lines).
    '\\n' in text forces a line break."""
    out = []
    line = start_line
    lines = []
    for para_no, para in enumerate(text.split("\n")):
        if para_no:
            out.append("<D3>")
            line = 2 if line == 1 else 1
        words = [w for w in para.split(" ") if w != ""]
        x = 0
        cur = []
        for w in words:
            ww = word_width(font, w)
            if cur and x + 3 + ww > LIMIT:
                lines.append((x, " ".join(cur)))
                out.append(" ".join(cur))
                out.append("<D3>")
                line = 2 if line == 1 else 1
                cur, x = [], 0
            if not cur:
                if ww > LIMIT:
                    raise ValueError(f"word too long ({ww}px): {w}")
                cur, x = [w], ww
            else:
                cur.append(w)
                x += 3 + ww
        if cur:
            lines.append((x, " ".join(cur)))
            out.append(" ".join(cur))
    return "".join(out), line, lines


def assemble(font, original, fi_pages, menu_opts=None):
    """Build the Translated string from JP structure + Finnish page texts.
    fi_pages: list of Finnish strings, one per JP page ('' keeps the page empty).
    Placeholders: {BUF03} -> <&BUF03>, {R}..{/R} -> <D4> red text toggles."""
    def conv(s):
        s = re.sub(r"\{(BUF[0-9A-F]{2})\}", r"<&\1>", s)
        s = s.replace("{R}", "<D4>").replace("{/R}", "<D4>")
        return s

    if is_menu(original):
        opts = menu_opts if menu_opts is not None else fi_pages
        return "".join(conv(o) + "<D3>" for o in opts)

    jp = jp_pages(original)
    if len(fi_pages) != len(jp):
        raise ValueError(f"{len(jp)} JP pages but {len(fi_pages)} Finnish pages")
    out = []
    line, has_text = 1, False
    for k, ((pre, _body, suf), fi) in enumerate(zip(jp, fi_pages)):
        if k:
            # page break: finish the current page so the next one starts fresh
            if has_text:
                out.append("<D3>" if line == 2 else "<D3><D3>")
            line, has_text = 1, False
        out.append(pre)
        fi = conv(fi.strip())
        if fi:
            txt, line, _ = wrap_page(font, fi, 1)
            out.append(txt)
            has_text = True
        if suf:
            if is_trailing_cd(original) and k == len(jp) - 1:
                out.append("<D3>")
            out.append(suf)
    return "".join(out)


class Flow:
    """Word-by-word layout from any (line, x) position, D3 breaks only."""

    def __init__(self, font):
        self.font = font
        self.out = []
        self.line = 1
        self.x = 0

    def newline(self):
        self.out.append("<D3>")
        self.line = 2 if self.line == 1 else 1
        self.x = 0

    def page_break(self):
        """Finish the current box so the next text starts a fresh one."""
        if self.x == 0 and self.line == 1:
            return
        if self.line == 1:
            self.newline()
        self.newline()

    def code(self, c):
        self.out.append(c)

    def text(self, s):
        for p_no, para in enumerate(s.split("\n")):
            if p_no:
                self.newline()
            for w in [w for w in para.split(" ") if w]:
                ww = word_width(self.font, w)
                if ww > LIMIT:
                    raise ValueError(f"word too long ({ww}px): {w}")
                if self.x == 0:
                    self.out.append(w)
                    self.x = ww
                elif self.x + 3 + ww <= LIMIT:
                    self.out.append(" " + w)
                    self.x += 3 + ww
                else:
                    self.newline()
                    self.out.append(w)
                    self.x = ww

    def result(self):
        return "".join(self.out)


def conv_placeholders(s):
    s = s.replace("\\n", "\n")          # literal \n in answer files = forced line break
    s = re.sub(r"\{(BUF[0-9A-F]{2})#(\d+)\}", r"<&\1><#w\2>", s)   # {BUF02#15}: width budget
    s = re.sub(r"\{(BUF[0-9A-F]{2})\}", r"<&\1>", s)
    return s.replace("{R}", "<D4>").replace("{/R}", "<D4>")


def assemble_flow(font, original, fi_pages):
    """Same-speaker pages flow on; a new box starts at a speaker change,
    a lone <CF>, a portrait clear (<@CC..>) and a trailing break."""
    if is_menu(original):
        return "".join(conv_placeholders(o) + "<D3>" for o in fi_pages)
    jp = jp_pages(original)
    seps = jp_separators(original)
    if len(fi_pages) != len(jp):
        raise ValueError(f"{len(jp)} JP pages but {len(fi_pages)} Finnish pages")
    fl = Flow(font)
    speaker = None
    for k, ((pre, body, suf), fi) in enumerate(zip(jp, fi_pages)):
        fi = conv_placeholders(fi.strip())
        spk = speaker_of(pre)
        if k:
            changed = spk is not None and spk != ("CC",) and spk != speaker
            hard = (seps[k - 1] == "<CF>" or spk == ("CC",) or changed
                    or (not body.strip() and not fi))
            if hard and not fi and body.strip():
                if changed:
                    raise ValueError(f"page {k}: new speaker but no Finnish text")
                hard = False          # text merged into the previous page
            if hard:
                fl.page_break()
        if spk is not None and spk != ("CC",):
            speaker = spk
        if pre:
            fl.code(pre)
        if fi:
            fl.text(fi)
        if suf:
            if is_trailing_cd(original) and k == len(jp) - 1 and fl.line == 1:
                fl.newline()      # JP ends with a newline; on line 2 a D3 would become a page wait
            fl.code(suf)
    return fl.result()


# ---------------------------------------------------------------- CSV io

def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def line_ending(path):
    data = open(path, "rb").read()
    return "\r\n" if b"\r\n" in data else "\n"


def write_csv(path, rows, eol="\n", bom=True):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator=eol)
    for r in rows:
        w.writerow(r)
    with open(path, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as f:
        f.write(buf.getvalue())
