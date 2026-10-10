INCLUDE "game/src/common/constants.asm"
INCLUDE "game/src/common/macros.asm"

; Battle HUD: the three Medaforce / Drive boxes. Banks 0A and 12 each hold two copies of the
; code that fills the boxes: the name is copied to $DCBA (8 cells, $00 padded, $CB terminated)
; and written as one tile id per letter with the routine at $28E0 into the map at $99C6
; (centre box), $9A0B and $9A01 (bottom boxes). The three jumps/calls to $28E0 now go to
; HudNameVWF, which draws the name with the menu VWF centred in the 8 cells instead. An
; empty box ($EE fill) keeps the old path. The "Vaihde A/B/C" labels are 8 byte table entries
; written straight into the map; HudLabelVWF copies one to $DCBA and does the same.

SECTION "HUD Name VWF", ROM0[$3F00]
HudNameVWF::
  ; hl = first cell of the box text, bc = name in RAM. Replaces a call/jp of $28E0.
  ; The copy routine right aligns names shorter than 8 letters with leading $00 bytes, so those
  ; are skipped here. An empty box ($EE fill) or a name with nothing in it keeps the old path.
  ld a, [bc]
  cp $EE
  jr z, .plain
  push bc

.skip
  ld a, [bc]
  or a
  jr nz, .got
  inc bc
  jr .skip

.got
  cp $CB
  jr z, .empty
  cp $EE
  jr z, .empty
  inc sp
  inc sp ; drop the saved bc, the name starts at the first letter
  call HudClearCells
  ld a, 8
  jp NamePlateVWF

.empty
  pop bc

.plain
  jp $28E0

HudNameVWFOffs::
  ; Bank 11 (Medarot names, left column): hl = column 0 of the box + (8 - length), bc = name.
  ; The old text was right aligned in 8 cells starting at column 0; the VWF centres it in the
  ; 8 cells of the box that start one cell to the right.
  push de
  push bc
  ld e, 0

.len
  ld a, [bc]
  cp $CB
  jr z, .got
  inc bc
  inc e
  jr .len

.got
  ld a, 8
  sub e
  jr nc, .offset
  xor a

.offset
  ld e, a
  ld a, l
  sub e
  ld l, a
  jr nc, .noBorrow
  dec h

.noBorrow
  inc hl
  pop bc
  pop de
  call HudClearCells
  ld a, 8
  jp NamePlateVWF

HudNameVWFRight::
  ; Bank 11 (right column): hl = first text cell (column 12), bc = name. The box starts one cell left.
  dec hl
  call HudClearCells
  ld a, 8
  jp NamePlateVWF

HudClearCells::
  ; Blanks the 8 map cells of a name box starting at hl (tile $00, the attributes stay).
  ; The VWF only writes the tiles under the letters, so the cells beside the text kept the
  ; ids of an earlier name and showed pieces of whatever text had used those tiles since
  ; (after an attack scene, or after leaving the vehicle mode). Preserves everything.
  push af
  push bc
  push hl
  ld b, 8

.cell
  xor a
  di
  push af
  rst $20
  pop af
  ld [hl+], a
  ei
  dec b
  jr nz, .cell
  pop hl
  pop bc
  pop af
  ret

HudLabelVWF::
  ; hl = first cell, de = 8 byte label in ROM (no terminator)
  push de
  ld bc, $DCBA
  ld a, 8

.copy
  push af
  ld a, [de]
  ld [bc], a
  inc de
  inc bc
  pop af
  dec a
  jr nz, .copy
  ld a, $CB
  ld [bc], a
  ld bc, $DCBA
  call HudNameVWF
  pop de
  ret

; --- name draw sites (bank 0A) --------------------------------------------------------
SECTION "HUD Name Site 0A_5CE1", ROMX[$5CE1], BANK[$0A]
  call HudNameVWF
SECTION "HUD Name Site 0A_5D30", ROMX[$5D30], BANK[$0A]
  jp HudNameVWF
SECTION "HUD Name Site 0A_5D4F", ROMX[$5D4F], BANK[$0A]
  jp HudNameVWF
SECTION "HUD Name Site 0A_5DDB", ROMX[$5DDB], BANK[$0A]
  call HudNameVWF
SECTION "HUD Name Site 0A_5E19", ROMX[$5E19], BANK[$0A]
  jp HudNameVWF
SECTION "HUD Name Site 0A_5E4F", ROMX[$5E4F], BANK[$0A]
  jp HudNameVWF

; --- name draw sites (bank 12) --------------------------------------------------------
SECTION "HUD Name Site 12_623D", ROMX[$623D], BANK[$12]
  call HudNameVWF
SECTION "HUD Name Site 12_628C", ROMX[$628C], BANK[$12]
  jp HudNameVWF
SECTION "HUD Name Site 12_62AB", ROMX[$62AB], BANK[$12]
  jp HudNameVWF
SECTION "HUD Name Site 12_6337", ROMX[$6337], BANK[$12]
  call HudNameVWF
SECTION "HUD Name Site 12_6375", ROMX[$6375], BANK[$12]
  jp HudNameVWF
SECTION "HUD Name Site 12_63AB", ROMX[$63AB], BANK[$12]
  jp HudNameVWF

; --- "Vaihde A/B/C" label writers (13 bytes: ld b,8 + copy loop) ------------------------
MACRO HudLabelSite
SECTION "HUD Label Site \1_\2", ROMX[\2], BANK[\1]
  call HudLabelVWF
  ds 10, $00
ENDM
  HudLabelSite $0A, $5E66
  HudLabelSite $0A, $5EC3
  HudLabelSite $0A, $5ED9
  HudLabelSite $12, $63C2
  HudLabelSite $12, $641F
  HudLabelSite $12, $6435

; --- Medarot name rows (bank 11): three boxes on each side -----------------------------
SECTION "HUD Name Site 11_491A", ROMX[$491A], BANK[$11]
  call HudNameVWFOffs
SECTION "HUD Name Site 11_4941", ROMX[$4941], BANK[$11]
  call HudNameVWFOffs
SECTION "HUD Name Site 11_4968", ROMX[$4968], BANK[$11]
  call HudNameVWFOffs
SECTION "HUD Name Site 11_4984", ROMX[$4984], BANK[$11]
  call HudNameVWFRight
SECTION "HUD Name Site 11_49A0", ROMX[$49A0], BANK[$11]
  call HudNameVWFRight
SECTION "HUD Name Site 11_49BB", ROMX[$49BB], BANK[$11]
  jp HudNameVWFRight
