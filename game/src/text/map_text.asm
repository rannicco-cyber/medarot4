INCLUDE "game/src/common/constants.asm"
INCLUDE "game/src/common/macros.asm"

SECTION "Text Mapping Functions", ROM0[$28E0]
PutStringVariableLength::
  ld a, [bc]
  cp $CB
  ret z
  di
  push af
  rst $20
  pop af
  ld [hli], a
  ei
  inc bc
  jr PutStringVariableLength

PutStringFixedLength::
  ; a = field width in tiles, bc = string (terminated by $CB), hl = tilemap address.
  ; The string is drawn with the VWF (patch/menu_vwf.asm).
  ld d, a
  call MenuVWFStringToRam ; the VWF code runs in another bank, strings in ROM are copied first
  ld a, [W_CurrentBank]
  push af
  ld a, BANK(MenuVWFDrawField)
  call VWFLowBankswitch
  call MenuVWFDrawField
  pop af
  jp VWFLowBankswitch

  padend $290E

SECTION "Get Tile-Based Centring Offset", ROM0[$290E]
GetTileBasedCentringOffset::
  push hl
  push bc
  push af
  ld h, 0

.loop
  ld a, [bc]
  cp $CB
  jr z, .terminatorFound
  inc bc
  inc h
  jr .loop

.terminatorFound
  pop af
  sub h
  srl a
  pop bc
  pop hl
  ret
