INCLUDE "game/src/common/constants.asm"
INCLUDE "game/src/common/macros.asm"

; Medarot name plates on the Medarot equipment and archive screens. Banks 07 and 01 each
; carry a copy of a small routine that centres a name in a field of n cells and writes one
; tile id per letter ($5F69 in bank 07, $53D1 in bank 01, one caller each). Both calls now go
; to NamePlateVWF, which draws the name with the menu VWF instead.

SECTION "Name Plate VWF Bank 0", ROM0[$3E60]
NamePlateVWF::
  ; a = field width in cells, hl = first cell of the field, bc = string in RAM
  push de
  push hl
  call PutStringVWFOffset ; a = offset in whole cells, the rest is pixel padding
  ld e, a
  ld d, 0
  add hl, de
  call PutStringVWFCentered
  pop hl
  pop de
  ret

SECTION "Name Plate Site 07_596D", ROMX[$596D], BANK[$07]
  call NamePlateVWF

SECTION "Name Plate Site 01_53CD", ROMX[$53CD], BANK[$01]
  call NamePlateVWF

; Medarot name above the status panels (bank 02, the routine at $4D7C that the status, medal list and
; parts screens call with hl = $984B or $992B). It right aligned the name in 8 cells with $290E and
; wrote it with $28E0. The 15 bytes from "ld a, 8" to the jump now pop the cell and call NamePlateVWF.
SECTION "Name Plate Site 02_4D96", ROMX[$4D96], BANK[$02]
  pop hl
  ld a, 8
  jp NamePlateVWF
  ds 9, $00

; Medarot name plate of the Medarot status screen (the box at the top left, 8 cells at $9821). The routine at
; 07:5926 ends with a jump to the fixed-width centring routine $5F69 (a = 8, hl = first cell, bc = name).
SECTION "Name Plate Site 07_594B", ROMX[$594B], BANK[$07]
  jp NamePlateVWF
