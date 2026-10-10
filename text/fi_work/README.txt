Finnish translation work files (Claude)

  fi_text.py   width model ($89 = 137 px per line), D3 layout, checks
  ws.py        sheet NN / build NN / check FILE.csv
  glossary.md  terms and style decisions
  tm.json      translation memory: Japanese original -> Finnish pages
  fi_NN.txt    Finnish answers per section (@row, one line per JP page)

Rules in use:
  - only <D3> as line/page break; new box only at a speaker change,
    a lone <CF>, a portrait clear, or where Japanese ends with a break
  - rows that are one box in Japanese stay one box (no A-press in UI text)
  - <&BUF03>/<&BUF15> counted as 48 px; <&BUFxx><#wNN> = width budget NN px
    (<#...> is an annotation dialog2bin ignores)
  - choice menus: one option per line, each <= 72 px

Progress: see the "done" list in progress.txt
