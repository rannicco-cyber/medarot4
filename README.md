# Medarot 4 — Finnish Translation (AI-assisted)

This branch, `tr_FIN_AI_assist`, is the working branch for a Finnish translation of **Medarot 4 (Kabuto)**, based on the Medabots/medarot4 disassembly and rebuild project.

The translation and engine modifications are a work in progress. The branch contains Finnish dialogue and terminology work alongside changes to text rendering, variable-width fonts (VWF), menus, naming screens, and related graphics. Not all content or gameplay has been fully translated or tested; treat builds as development builds.

## Project status

- **Target:** Medarot 4 — Kabuto version.
- **Language:** Finnish.
- **Translation status:** The current work progress file lists dialogue sections 00–54. This indicates that work has been processed for those sections, not that every line has received final proofreading or in-game verification.
- **Technical work:** Variable-width text rendering and related menu/name-entry support are under development.
- **Testing:** Rebuild and test the ROM locally as changes are made. Record rendering problems, crashes, text overflow, and untranslated text with the affected section or in-game location.

## Requirements

- An original **Medarot 4 KABUTO** ROM with SHA-1 `a62a00ee6095b3dcdf347fbb7c536b51976a109f`.
- GNU Make 4 or newer.
- Python 3.6 or newer, available as `python3`.
- The [RGBDS toolchain](https://github.com/rednex/rgbds), version 0.7.0 or newer.

The original ROM is not included in this repository. You must supply your own legally obtained copy. The upstream project also supports the Medarot 3 KUWAGATA ROM, but this branch's Finnish translation work primarily targets Medarot 4 KABUTO.

## Build the Finnish ROM

Run these commands from the repository root.

1. Place your original Medarot 4 Kabuto ROM in the root folder and name it:

   ```text
   baserom_kabuto.gbc
   ```

2. Ensure `make`, `python3`, and the RGBDS tools are installed and available on your PATH.
3. Build the ROM:

   ```bash
   make
   ```

   To use multiple build jobs, try `make -j4` (adjust the number for your system).

4. If the build succeeds, the generated ROM is:

   ```text
   medarot4_kabuto.gbc
   ```

Build outputs and local ROM files should not normally be committed. If the build fails, keep the full terminal output; the first reported assembler, linker, or script error is usually the most useful starting point for troubleshooting.

## Where the files are

- `text/dialog/` — dialogue and other game text, organized in `TextSectionNN.csv` files.
- `text/ptrlists/` — names and other strings stored in pointer-list resources, such as parts, Medarots, medals, and attacks.
- `text/fi_work/` — Finnish translation working tools, glossary, terminology lists, and progress tracking.
- `game/src/` — Game Boy assembly source, including text rendering and interface changes.
- `gfx/` — graphics, tilemaps, attribute maps, and font assets.
- `scripts/` — build and resource-processing scripts.
- `Makefile` — build rules.

## Finnish terminology and text conventions

Translation choices are tracked in [`text/fi_work/glossary.md`](text/fi_work/glossary.md). Check that glossary before introducing or changing terms.

Current established choices include:

- **Medabotti** — Medabot (Finnish inflection follows the glossary).
- **medabottaaja** — Medabotter.
- **Medakello** — Medawatch.
- **mitali** — Medal.
- **Medavoima** — Medaforce.
- **robottelu** — Robattle.

The glossary also documents movement types, battle statuses, terrain names, part terminology, dropped Japanese honorific suffixes, and conventions for name buffers. Preserve existing game control tags and CSV structure when editing text. Check text changes against in-game font widths and layout limits.

## Finnish translation work tools

The scripts in `text/fi_work/` are project-specific translation helpers. Consult each script's docstring and command-line interface before running it. Some helper scripts were originally used in a separate local or AI-assisted workflow and may contain machine-specific paths or assumptions; inspect configuration paths before using them on another computer. The standard ROM build is run from the repository root with `make`.

## Git workflow

Use the `tr_FIN_AI_assist` branch for this work. Before committing, inspect your changes:

```bash
git status
git diff --stat
git diff
```

Stage only the source, translation, and asset files intended for the commit. Avoid committing original ROMs, generated ROMs, build output, temporary backups, or unrelated test files.

```bash
git add <files-you-intend-to-commit>
git commit -m "Describe the change"
git push origin tr_FIN_AI_assist
```

## Contributions and issue reports

When reporting an issue, include:

- The exact branch and latest commit you tested.
- The build command and relevant error output.
- For in-game problems, the scene or menu, the expected behavior, and what actually happened.
- Screenshots or a save state when they help reproduce a text-rendering or graphics issue.

Keep translation wording and terminology consistent with the glossary. Separate translation corrections from engine changes where practical, so each change is easier to review and test.

## Credits and project context

This work builds on the Medabots/medarot4 disassembly and rebuild project. The Finnish translation, terminology decisions, text-rendering changes, and related branch-specific work are in progress.

Medarot and Medabots are trademarks of their respective owners. This repository is a fan translation and technical project; it is not an official release and is not affiliated with or endorsed by the rights holders.
