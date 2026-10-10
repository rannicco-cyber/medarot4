#!/bin/bash
# usage: d2b.sh NN...   validate built CSVs with the repo's dialog2bin (output to scratch only)
S=/tmp/claude-0/-home-claude/c58ed6a5-6ce9-52b0-a0d6-179850a4c8c5/scratchpad
R=/mnt/user-data/uploads/medarot4-tr_loc_FI
cd $R || exit 1
for n in "$@"; do for v in kabuto kuwagata; do
  python3 scripts/dialog2bin.py $S/d2b/$n.$v.bin $S/work/out/TextSection$n.csv scripts/res/ptrs.tbl Translated $v >$S/d2b/out.txt 2>$S/d2b/err.txt || { echo "FAIL $n $v"; tail -4 $S/d2b/err.txt; }
done; done
