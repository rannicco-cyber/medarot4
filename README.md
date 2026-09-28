# Medarot 4 Dialogue Editor

A browser-based translation workspace for the **Medarot 4** TextSection
CSV files.

The current editor is **v18** and provides a live Medarot 4-style text
preview, CSV editing, validation, project-file management, and character
portrait rendering.

## Features

### Translation workspace

-   Load multiple `.csv` translation files.
-   Open an entire project folder through the browser\'s folder picker.
-   Browse loaded CSV files from the project sidebar.
-   Filter project files by filename/path.
-   Browse entries with index, ROM pointer, original text, and
    translated text.
-   Search entries by index, pointer, original text, or translation.
-   Filter entries by All, Untranslated, Translated, or With
    diagnostics.
-   Navigate between entries with Previous / Next.
-   Edit the `Translated` column directly.
-   Apply edits or Apply + recheck.
-   Download individual edited CSV files or all modified CSV files.

### Live M4 preview

The preview uses embedded Medarot 4 font data and VWF width tables.

Supported font selectors include Normal, Narrow, Bold, Robotic, and
Robotic Bold.

Supported dialogue controls include:

-   `<CD>` --- line break
-   `<CF>` --- new page / input
-   `<D1>` --- new page without CF input
-   `<D3>` --- context-dependent line/page break
-   `<fXX>` --- font selection
-   `<@...>` --- portrait/position controls
-   `<&...>` --- dynamic buffer controls
-   `<D0...>` --- dynamic subtext
-   `<D2>`--`<D5>` and `<*>` --- additional control codes

The preview also calculates text width using the embedded M4
character-width tables.

### Character portraits

The v18 build includes Medarot 4 character portrait rendering.

Examples:

``` text
<@LL,00,05>
<@LR,00,05>
<@RL,00,05>
<@RR,00,05>
```

Placement codes are interpreted as:

-   `LL` --- left side, normal facing
-   `LR` --- left side, mirrored
-   `RL` --- right side, normal facing
-   `RR` --- right side, mirrored

Portrait graphics are extracted from the original Kabuto ROM using the
game\'s portrait lookup rules and embedded into the HTML editor. The ROM
is therefore not required at runtime.

Portraits use the game\'s 32×32 arrangement and are rendered above the
dialogue box with the portrait background transparent.

### Validation and diagnostics

The scanner checks translation text against M4 rendering constraints.

It can report:

-   text-width violations
-   excessive line count
-   unsupported glyphs
-   malformed or unknown control codes
-   literal newlines inside CSV fields
-   control-code events
-   dynamic text whose width cannot be measured statically

The scanner uses the M4 `$89` text-width threshold.

Diagnostics can be inspected per entry, while the full diagnostic
scanner is available from the Tools drawer. A diagnostic report can also
be exported as CSV.

### Find & Replace {#find--replace}

The Tools drawer includes Find & Replace for the `Translated` column.

Options include case-sensitive matching, case-insensitive matching, and
capitalization preservation.

Replacement changes are applied across loaded CSV files and affected
files are marked as modified.

## Quick controls

Quick insertion buttons are provided for:

``` text
<CD>
<D3>
<CF>
<D1>
```

`Ctrl+Enter` / `Cmd+Enter` applies the current entry with rechecking.

## Typical workflow

1.  Open the editor in a modern browser.
2.  Choose **Open project folder** and select the directory containing
    the TextSection CSV files, or load individual CSV files.
3.  Select a CSV from **Project files**.
4.  Select an entry from **Translation entries**.
5.  Edit the translation.
6.  Use the live M4 preview while editing.
7.  Check the validation badge/details for width, glyph, or control-code
    issues.
8.  Use **Apply + recheck** when the entry is ready.
9.  Download the modified CSV files.
10. Rebuild and test the ROM separately.

## Browser use

The editor is a self-contained HTML application intended to run directly
in a modern browser without a server.

For GitHub Pages, naming the application file `index.html` allows it to
be served as the repository site\'s main page.

## Project context

This tool is intended specifically for the Medarot 4 translation
workflow and its TextSection CSV format. It reproduces the relevant M4
text-rendering behaviour closely enough to catch common
translation-width and control-code problems before rebuilding the ROM.

The portrait data and M4 rendering assets are embedded in the editor
itself.

## Status

**Current version: v18**

The current v18 build includes the corrected character portrait renderer
and live portrait-aware M4 preview.

The editor is a translation/development tool, not a replacement for
testing the final compiled ROM. The rebuilt ROM should still be tested
in an emulator or on appropriate hardware.
