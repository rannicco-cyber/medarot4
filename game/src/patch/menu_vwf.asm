INCLUDE "game/src/common/constants.asm"
INCLUDE "game/src/common/macros.asm"

; VWF for fixed-length menu strings (item names, part names, ...).
;
; PutStringFixedLength (ROM0, text/map_text.asm) used to write one tile id per
; character. It now calls MenuVWFDrawField, which draws the string with the
; VWF font into a few free tiles in VRAM bank 1 and maps those tiles instead.
; A field of n tiles then fits about 1.4x as many characters.
;
; The fixed-text font (tileset 98004) is loaded into VRAM bank 1 at $9000 and
; the text cells have the bank 1 attribute. The tile pool is the first part of
; that page (tile ids $01-$3E). The Latin letters at $3F-$7F stay intact for
; static labels (Yes/No box, ...). Tile $00 stays blank.
;
; Which pool tiles are free is read back from the tilemaps themselves ($9800 and
; $9C00 share the tiles, so both are scanned), so screens
; that redraw only some of their fields (swapping parts, scrolling lists)
; never take tiles that other fields still show:
;   - A field whose first n cells already hold n consecutive pool tile ids
;     is a redraw: it reuses those tiles.
;   - Otherwise every visible cell (20x18) that holds a pool tile id marks that
; (with a window layer at 0,0 and a scrolled background both are covered)
;     tile as used, and the field takes the first run of n free tiles.

DEF M_MenuVWFPoolStart EQU $01
DEF M_MenuVWFPoolLimit EQU $3F ; tile ids used are below this
DEF M_MenuVWFPoolSize  EQU M_MenuVWFPoolLimit - M_MenuVWFPoolStart
DEF M_MenuVWFScanWidth  EQU 21 ; 20 cells plus the one a pixel scroll shows
DEF M_MenuVWFScanHeight EQU 19
DEF M_MenuVWFBitmapCachedMagic EQU $A5

DEF W_MenuVWFBitmap EQU $CCDC ; 8 bytes, one bit per pool tile, only used while allocating

SECTION "Menu VWF Functions", ROMX[$6000], BANK[$C4]
MenuVWFReadCell::
  ; a = [hl] from VRAM bank 0 once it is readable. Preserves everything else.
  di

.wfb
  ldh a, [H_LCDStat]
  and 2
  jr nz, .wfb
  ld a, [hl]
  ei
  ret

MenuVWFReadAttr::
  ; a = tilemap attribute at hl (VRAM bank 1). Preserves everything else.
  VRAMSwitchToBank1
  call MenuVWFReadCell
  push af
  VRAMSwitchToBank0
  pop af
  ret

MenuVWFMarkBit::
  ; a = bit index in the pool bitmap. Preserves bc, hl.
  push hl
  push bc
  ld c, a
  srl a
  srl a
  srl a
  ld hl, W_MenuVWFBitmap
  add l
  ld l, a
  ld a, c
  and 7
  ld b, a
  inc b
  xor a
  scf

.shift
  rla
  dec b
  jr nz, .shift
  or [hl]
  ld [hl], a
  pop bc
  pop hl
  ret

MenuVWFTestBit::
  ; a = bit index in the pool bitmap. Returns nz if the bit is set. Preserves bc, hl.
  push hl
  push bc
  ld c, a
  srl a
  srl a
  srl a
  ld hl, W_MenuVWFBitmap
  add l
  ld l, a
  ld a, c
  and 7
  ld b, a
  inc b
  xor a
  scf

.shift
  rla
  dec b
  jr nz, .shift
  and [hl]
  pop bc
  pop hl
  ret

DEF W_MenuVWFScanCol EQU $CCEE ; column of the cell being scanned
DEF W_MenuVWFScanStartCol EQU $CCF1 ; first column of the region being scanned
DEF W_MenuVWFBitmapCached EQU $CCF2 ; = M_MenuVWFBitmapCachedMagic while a screen draw owns the bitmap
DEF W_MenuVWFPoolBase EQU $CCF3 ; added to the tile ids the allocator returns: $3E while a pop-up menu draws its labels into the upper
                                ; tiles ($3F-$7C, see static_labels.asm), 0 otherwise

MenuVWFScanPass::
  ; a = high byte of a tilemap ($98 or $9C). Marks the pool tiles that the visible
  ; cells of it show, starting at the scroll position, so screens drawn while the
  ; background is scrolled (the pause menu over the map) are scanned where they
  ; really are. Preserves d, clobbers everything else.
  push de
  ld e, a ; e = base
  ld a, [W_ShadowREG_SCX]
  srl a
  srl a
  srl a
  and $1F
  ld [W_MenuVWFScanStartCol], a
  ld a, [W_ShadowREG_SCY]
  srl a
  srl a
  srl a
  and $1F
  ld d, a ; d = row, 0-31
  jr MenuVWFScanRegion

MenuVWFScanOrigin::
  ; Same, but for the part of the map that starts at 0,0. That is what the window
  ; layer shows (the pause menu panel, message boxes) whatever the scroll position is.
  push de
  ld e, a
  xor a
  ld [W_MenuVWFScanStartCol], a
  ld d, a

MenuVWFScanRegion:
  ld c, M_MenuVWFScanHeight

.row
  ld a, d
  ld l, a
  ld h, 0
  add hl, hl
  add hl, hl
  add hl, hl
  add hl, hl
  add hl, hl
  ld a, e
  add h
  ld h, a ; hl = start of the row
  ld a, [W_MenuVWFScanStartCol]
  ld [W_MenuVWFScanCol], a
  ld b, M_MenuVWFScanWidth

.col
  push hl
  ld a, [W_MenuVWFScanCol]
  add l ; the low 5 bits of l are 0 here
  ld l, a
  call MenuVWFReadCell
  push bc
  ld b, a
  ld a, [W_MenuVWFPoolBase] ; the pool is the 62 tiles above the base (0 or $3E)
  cpl
  inc a
  add b
  pop bc
  sub M_MenuVWFPoolStart
  cp M_MenuVWFPoolSize
  jr nc, .nextCell
  push af
  call MenuVWFReadAttr
  bit 3, a ; only cells that show a VRAM bank 1 tile use the pool
  jr z, .notBank1
  pop af
  call MenuVWFMarkBit
  jr .nextCell

.notBank1
  pop af

.nextCell
  pop hl
  ld a, [W_MenuVWFScanCol]
  inc a
  and $1F
  ld [W_MenuVWFScanCol], a
  dec b
  jr nz, .col
  ld a, d
  inc a
  and $1F
  ld d, a
  dec c
  jr nz, .row
  pop de
  ret

MenuVWFScanAll::
  ; Clears the bitmap and marks every pool tile that any layer shows: both tilemaps
  ; at the scroll position and, when scrolled, both again from 0,0 (window layer).
  ; Preserves d.
  push de
  ld hl, W_MenuVWFBitmap
  ld b, 8
  xor a

.clearBitmap
  ld [hli], a
  dec b
  jr nz, .clearBitmap
  ld a, $98
  call MenuVWFScanPass
  ld a, $9C
  call MenuVWFScanPass
  ld a, [W_ShadowREG_SCX]
  ld b, a
  ld a, [W_ShadowREG_SCY]
  or b
  jr z, .done
  ld a, $98
  call MenuVWFScanOrigin
  ld a, $9C
  call MenuVWFScanOrigin

.done
  pop de
  ret

MenuVWFAllocate::
  ; hl = tilemap address of the field, d = width in tiles.
  ; Returns e = first tile of the field. Preserves bc, d, hl.
  push bc
  push hl
  VRAMSwitchToBank0

  ; A redraw of an existing field? The first d cells hold d consecutive pool ids.
  ld b, d
  call MenuVWFReadCell
  cp M_MenuVWFPoolStart
  jr c, .scan
  ld c, a
  ld e, a
  add d
  jr c, .scan
  cp M_MenuVWFPoolLimit + 1
  jr nc, .scan

.verify
  dec b
  jr z, .done
  inc hl
  inc c
  call MenuVWFReadCell
  cp c
  jr z, .verify

.scan
  ; Mark every pool tile that is shown on the screen, unless a screen draw
  ; (StaticLabelsRun) scanned already and keeps the bitmap up to date.
  ld a, [W_MenuVWFBitmapCached]
  cp M_MenuVWFBitmapCachedMagic
  jr z, .haveBitmap
  call MenuVWFScanAll

.haveBitmap
  ; First run of d free tiles.
  ld e, 0

.candidate
  ld a, e
  add d
  cp M_MenuVWFPoolSize + 1
  jr nc, .noFit
  ld b, d
  ld c, e

.checkBits
  ld a, c
  call MenuVWFTestBit
  jr nz, .conflict
  inc c
  dec b
  jr nz, .checkBits
  ld a, [W_MenuVWFBitmapCached]
  cp M_MenuVWFBitmapCachedMagic
  jr nz, .notCached
  ld b, d ; keep the bitmap current for the next label of the same screen
  ld c, e

.markTaken
  ld a, c
  call MenuVWFMarkBit
  inc c
  dec b
  jr nz, .markTaken

.notCached
  ld a, [W_MenuVWFPoolBase]
  add e
  add M_MenuVWFPoolStart
  ld e, a
  jr .done

.conflict
  ld a, c
  inc a
  ld e, a
  jr .candidate

.noFit
  ld e, M_MenuVWFPoolStart

.done
  pop hl
  pop bc
  ret

MenuVWFDrawField::
  ; d = field width in tiles
  ; bc = string, terminated by $CB
  ; hl = tilemap address of the first tile of the field
  push hl
  call MenuVWFAllocate ; e = first tile

  ; Drawing state, as the choice menu sets it up.
  ld a, e
  ld [W_VWFTileBaseIdx], a
  ld a, d
  ld [W_VWFTileLength], a
  xor a
  ld [W_VWFTilesDrawn], a
  ld [W_VWFLetterShift], a
  ld [W_VWFOldTileMode], a
  ld [W_VWFTextLength], a
  ld [W_VWFDiscardSecondTile], a
  ld [W_VWFCurrentFont], a

  ; Measure the string. Switch to the narrow font if it doesn't fit.
  push de
  push bc
  ld d, 0 ; d = width in pixels, including the gap after the last letter

.measure
  ld a, [bc]
  cp $CB
  jr z, .measured
  inc bc
  and $7F
  ld l, a
  ld h, HIGH(VWFDrawLetterTable)
  ld a, [hl]
  inc a
  add d
  jr nc, .keepWidth
  ld a, $FF

.keepWidth
  ld d, a
  jr .measure

.measured
  pop bc
  pop hl ; h = width in tiles, l = first tile
  ld a, h
  add a
  add a
  add a
  inc a ; the gap after the last letter isn't drawn
  cp d
  jr nc, .fits
  ld a, 1
  ld [W_VWFCurrentFont], a

.fits
  ld d, h
  ld e, l

  ; Clear the tiles of the field (VRAM bank 1).
  push de
  push bc
  ld a, e
  call VWFTileIdx2Ptr
  ld b, d
  call VWFEmptyDrawingRegion
  ld hl, W_VWFCompositeArea
  ld b, $10
  xor a

.clearComposite
  ld [hli], a
  dec b
  jr nz, .clearComposite
  pop bc
  pop de

  ; Draw the letters.
.draw
  ld a, [bc]
  inc bc
  cp $CB
  jr z, .drawn
  and $7F
  ld [W_VWFCurrentLetter], a
  push bc
  push de
  call VWFWriteCharLimited
  pop de
  pop bc
  jr .draw

.drawn
  ; Map the field's tiles.
  pop hl
  ld b, d
  ld c, e

.mapLoop
  di

.wfb
  ldh a, [H_LCDStat]
  and 2
  jr nz, .wfb
  ld [hl], c
  ei
  VRAMSwitchToBank1
  di

.wfbAttribute
  ldh a, [H_LCDStat]
  and 2
  jr nz, .wfbAttribute
  set 3, [hl] ; show the tile from VRAM bank 1
  ei
  VRAMSwitchToBank0
  inc hl
  inc c
  dec b
  jr nz, .mapLoop
  xor a
  ld [W_VWFCurrentFont], a
  ret


; ---------------------------------------------------------------------------
; Names drawn into fixed cells (Robattler names, terrain, battle part names, ...).
;
; The game centres a name by working out how many cells the string needs
; (GetTileBasedCentringOffset, $290E) and then writes one tile id per character
; (PutStringVariableLength, $28E0) at hl + offset. The patched call sites call
; the routines below instead, so the same cells get VWF text:
;
;   PutStringVWFOffset   replaces the call to $290E. a = field width in cells,
;                        bc = string. Returns the offset in whole cells and
;                        remembers the remaining 0-7 pixels for the draw call.
;   PutStringVWFCentered replaces the call to $28E0. If PutStringVWFOffset ran
;                        just before, the text is drawn in as many cells as it
;                        needs, starting with that pixel padding. Otherwise
;                        (HUD buffers that are already padded to the field
;                        width with $00 bytes) the text is centred in the n
;                        cells that the string would have written.
;   PutStringVWFLeft     like PutStringVWFCentered, but for fields without
;                        centring: text starts at the left edge of the first
;                        cell and the cells the old string covered are cleared.
;
; Strings may be in any bank, they are copied to RAM first because the VWF code
; runs in another bank. $00 bytes in a string are padding and stay blank.

DEF M_MenuVWFCenterMaxCells EQU 22 ; W_NewListItemBufferArea is $17 bytes, including the terminator

DEF W_MenuVWFPendingPad   EQU $CCE4 ; 0 = none, otherwise the pixel padding + 1
DEF W_MenuVWFPendingWidth EQU $CCE5 ; field width in cells, 0 = use the string length
DEF W_MenuVWFPadPx        EQU $CCE6

SECTION "Menu VWF Centred Bank 0 Functions", ROM0[$3FBB]
PutStringVWFLeft::
  ld a, 1
  ld [W_MenuVWFPendingPad], a
  xor a
  ld [W_MenuVWFPendingWidth], a
  ; continues below

PutStringVWFCentered::
  push de
  push hl
  ld hl, W_NewListItemBufferArea
  ld d, M_MenuVWFCenterMaxCells

.copy
  ld a, [bc]
  inc bc
  cp $CB
  jr z, .copied
  ld [hli], a
  dec d
  jr nz, .copy

.copied
  ld a, $CB
  ld [hl], a
  pop hl
  ld bc, W_NewListItemBufferArea
  ld a, [W_CurrentBank]
  push af
  ld a, BANK(MenuVWFDrawCentered)
  call VWFLowBankswitch
  call MenuVWFDrawCentered
  pop af
  call VWFLowBankswitch
  pop de
  ret

SECTION "Menu VWF Offset Bank 0 Functions", ROM0[$3C80]
PutStringVWFOffset::
  ; a = field width in cells, bc = string. Returns a = offset in cells. Preserves bc, de, hl.
  push hl
  push bc
  push de
  ld e, a
  ld hl, W_NewListItemBufferArea
  ld d, M_MenuVWFCenterMaxCells

.copy
  ld a, [bc]
  inc bc
  cp $CB
  jr z, .copied
  ld [hli], a
  dec d
  jr nz, .copy

.copied
  ld a, $CB
  ld [hl], a
  ld a, [W_CurrentBank]
  push af
  ld a, BANK(MenuVWFCenterOffset)
  call VWFLowBankswitch
  ld a, e
  ld bc, W_NewListItemBufferArea
  call MenuVWFCenterOffset
  ld e, a
  pop af
  call VWFLowBankswitch
  ld a, e
  pop de
  pop bc
  pop hl
  ret

SECTION "Menu VWF Centred Functions", ROMX[$6440], BANK[$C4]
MenuVWFMeasure::
  ; bc = string in RAM. Returns d = number of bytes before $CB,
  ; e = text width in pixels including the gap after each letter ($00 bytes are padding).
  ; Preserves bc and hl.
  push bc
  push hl
  ld d, 0
  ld e, 0

.loop
  ld a, [bc]
  cp $CB
  jr z, .done
  inc bc
  inc d
  and a
  jr z, .loop
  and $7F
  ld l, a
  ld h, HIGH(VWFDrawLetterTable)
  ld a, [hl]
  inc a
  add e
  jr nc, .keepWidth
  ld a, $FF

.keepWidth
  ld e, a
  jr .loop

.done
  pop hl
  pop bc
  ret

MenuVWFCenterOffset::
  ; a = field width in cells, bc = string in RAM. Returns a = offset in cells and
  ; leaves the remaining pixel padding for MenuVWFDrawCentered.
  ld [W_MenuVWFPendingWidth], a
  xor a
  ld [W_MenuVWFPendingPad], a
  call MenuVWFMeasure
  ld a, e
  and a
  jr z, .noText
  ld a, [W_MenuVWFPendingWidth]
  add a
  add a
  add a
  inc a
  sub e
  jr nc, .hasPad
  xor a

.hasPad
  srl a ; a = total padding in pixels
  ld c, a
  and 7
  inc a
  ld [W_MenuVWFPendingPad], a
  ld a, c
  srl a
  srl a
  srl a
  ret

.noText
  ld a, [W_MenuVWFPendingWidth]
  sub d
  jr nc, .half
  xor a

.half
  srl a
  ret

MenuVWFDrawCentered::
  ; hl = tilemap address of the field, bc = string in RAM. Clobbers everything but de.
  ld a, [W_MenuVWFPendingPad]
  ld [W_MenuVWFPadPx], a
  xor a
  ld [W_MenuVWFPendingPad], a
  call MenuVWFMeasure
  ld a, d
  and a
  ret z ; empty string, nothing to draw
  cp M_MenuVWFCenterMaxCells + 1
  jr nc, .plain
  ld a, e
  and a
  jr nz, .hasText

.plain
  jp PutStringVariableLength ; only padding, or too long: the old way

.hasText
  ld a, [W_MenuVWFPadPx]
  and a
  jr nz, .pending

  ; Centre the text in the d cells: pad = (cells * 8 + 1 - e) / 2 pixels in front
  ; of it. If it is wider than that, use the narrow font and no padding.
  ld a, d
  add a
  add a
  add a
  inc a
  sub e
  ld e, 0 ; e = font (does not change the flags)
  jr nc, .classicFits
  inc e
  xor a
  jr .padKnown

.classicFits
  srl a
  jr .padKnown

.pending
  ; The offset call left the padding (0-7 pixels). The text starts in the cell at hl.
  dec a
  ld c, a ; c = padding
  ld a, [W_MenuVWFPendingWidth]
  and a
  jr z, .cellsKnown ; no field width: the cells are those of the old string
  ld b, a ; b = field width
  ld a, c
  add e
  add 6
  srl a
  srl a
  srl a ; (padding + width + 6) / 8 = cells needed
  jr nz, .haveCells
  inc a

.haveCells
  cp b
  jr c, .setCells
  ld a, b

.setCells
  ld d, a

.cellsKnown
  ld a, c
  add e
  ld b, a ; b = padding + text width including the last gap
  ld a, d
  add a
  add a
  add a
  inc a
  sub b
  ld e, 0
  jr nc, .pendingFits
  inc e ; too wide for the cells: narrow font

.pendingFits
  ld a, c

.padKnown
  ; a = padding in pixels, e = font, d = cells, hl = tilemap address
  ld [W_VWFLetterShift], a ; the full padding for now
  ld a, e
  ld [W_VWFCurrentFont], a
  call MenuVWFAllocate ; e = first tile
  ld a, [W_VWFLetterShift]
  ld c, a
  and 7
  ld [W_VWFLetterShift], a
  ld a, c
  srl a
  srl a
  srl a
  ld [W_VWFTilesDrawn], a
  ld a, e
  ld [W_VWFTileBaseIdx], a
  ld a, d
  ld [W_VWFTileLength], a
  xor a
  ld [W_VWFOldTileMode], a
  ld [W_VWFTextLength], a
  ld [W_VWFDiscardSecondTile], a
  ld bc, W_NewListItemBufferArea

  ; Clear the tiles of the field (VRAM bank 1) and the composite area.
  push hl
  push de
  push bc
  ld a, e
  call VWFTileIdx2Ptr
  ld b, d
  call VWFEmptyDrawingRegion
  ld hl, W_VWFCompositeArea
  ld b, $10
  xor a

.clearComposite
  ld [hli], a
  dec b
  jr nz, .clearComposite
  pop bc
  pop de

.draw
  ld a, [bc]
  inc bc
  cp $CB
  jr z, .drawn
  and a
  jr z, .draw
  and $7F
  ld [W_VWFCurrentLetter], a
  push bc
  push de
  call VWFWriteCharLimited
  pop de
  pop bc
  jr .draw

.drawn
  ; Map the field's tiles.
  pop hl
  ld b, d
  ld c, e

.mapLoop
  di

.wfb
  ldh a, [H_LCDStat]
  and 2
  jr nz, .wfb
  ld [hl], c
  ei
  VRAMSwitchToBank1
  di

.wfbAttribute
  ldh a, [H_LCDStat]
  and 2
  jr nz, .wfbAttribute
  set 3, [hl] ; show the tile from VRAM bank 1
  ei
  VRAMSwitchToBank0
  inc hl
  inc c
  dec b
  jr nz, .mapLoop
  xor a
  ld [W_VWFCurrentFont], a
  ret

SECTION "Menu VWF Right Bank 0 Functions", ROM0[$3CD0]
PutStringVWFRight::
  push hl
  push af
  ld hl, W_NewListItemBufferArea
  ld d, M_MenuVWFCenterMaxCells

.copy
  ld a, [bc]
  inc bc
  cp $CB
  jr z, .copied
  ld [hli], a
  dec d
  jr nz, .copy

.copied
  ld a, $CB
  ld [hl], a
  ld a, [W_CurrentBank]
  pop de ; d = field width (from a)
  push af ; bank to restore
  ld a, BANK(MenuVWFRightOffset)
  call VWFLowBankswitch
  ld a, d
  ld bc, W_NewListItemBufferArea
  call MenuVWFRightOffset ; a = number of cells in front of the text
  ld e, a
  pop af
  push de
  call VWFLowBankswitch
  pop de
  pop hl ; field start
  ld a, e
  and a
  jr z, .draw
  ld b, a

.blank
  di

.waitBlank
  ldh a, [H_LCDStat]
  and 2
  jr nz, .waitBlank
  ld [hl], 0
  ei
  VRAMSwitchToBank1
  di

.waitBlankAttribute
  ldh a, [H_LCDStat]
  and 2
  jr nz, .waitBlankAttribute
  res 3, [hl] ; plain tile from VRAM bank 0 again
  ei
  VRAMSwitchToBank0
  inc hl
  dec b
  jr nz, .blank

.draw
  ld bc, W_NewListItemBufferArea
  jp PutStringVWFCentered

SECTION "Menu VWF Right Functions", ROMX[$6400], BANK[$C4]
MenuVWFRightOffset::
  ; a = field width in cells, bc = string in RAM. Returns a = number of cells in
  ; front of the text and leaves the remaining pixel padding (0-7) for
  ; MenuVWFDrawCentered. An empty string returns the whole width (all blank).
  ld [W_MenuVWFPendingWidth], a
  xor a
  ld [W_MenuVWFPendingPad], a
  call MenuVWFMeasure
  ld a, e
  and a
  jr z, .noText
  ld a, [W_MenuVWFPendingWidth]
  add a
  add a
  add a
  inc a
  sub e
  jr nc, .hasPad
  xor a

.hasPad
  ld c, a ; c = padding in pixels in front of the text
  and 7
  inc a
  ld [W_MenuVWFPendingPad], a
  ld a, c
  srl a
  srl a
  srl a
  ret

.noText
  ld a, [W_MenuVWFPendingWidth]
  ret

SECTION "Menu VWF String Copy Bank 0 Functions", ROM0[$3D80]
MenuVWFStringToRam::
  ; bc = string ($CB terminated). A string in ROM (below $8000) is copied to
  ; W_NewListItemBufferArea first and bc is pointed there: the VWF code runs in another
  ; bank, so it can't read strings that live in the bank of the caller (Mr Kitama's
  ; glossary list, ...). RAM strings are left alone. Preserves d and hl.
  ld a, b
  cp $80
  ret nc
  push hl
  push de
  ld hl, W_NewListItemBufferArea
  ld e, M_MenuVWFCenterMaxCells

.copy
  ld a, [bc]
  inc bc
  cp $CB
  jr z, .copied
  ld [hli], a
  dec e
  jr nz, .copy

.copied
  ld a, $CB
  ld [hl], a
  ld bc, W_NewListItemBufferArea
  pop de
  pop hl
  ret
