PR #64 review changes

1. Change the PR base branch from `tr_EN` to `master` in GitHub.
2. Keep `scripts/common/tilesets.py` compression changes.
3. Replace the current PNG/rgbgfx-based `scripts/test_tilesets.py` with the supplied test_tilesets.py.
   It only reads existing prebuilt *.malias files, decompresses them in memory,
   recompresses the decoded data, decompresses the result again, and compares
   the decompressed byte arrays.
4. Delete `scripts/test_tilesets_csv.py`.
5. Apply Makefile.patch so `make test_tilesets` runs:
      $(PYTHON) $(SCRIPT)/test_tilesets.py "$(TILESET_PREBUILT)"

The test deliberately does not require rgbgfx, PNGs, temporary folders, or any
external conversion tool.
