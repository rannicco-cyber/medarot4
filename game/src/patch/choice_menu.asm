INCLUDE "game/src/common/constants.asm"
INCLUDE "game/src/common/macros.asm"

; VWF support for the script choice menu (course select, level select, ...).
;
; The choice menu (bank 09, see version/choice_menu.asm) sizes its box by
; measuring a dialog line, then prints that line into the box through the
; main script. The original measuring routine (CrossBank $B1 -> $339E -> $33AA)
; still expects 2-byte pointer entries in low banks, so with the expanded text
; tables it measured random data and produced boxes of e.g. 238x47 tiles. The
; box backup at 15:4F14 then ran over WRAM and the stack. The main script in
; turn only renders into the message box strip, so the menu box stayed empty.
;
; This replaces both steps:
;   ChoiceMenuMeasureText - measures the line with the VWF font widths.
;   ChoiceMenuDrawText    - draws each option with the VWF into its own tiles.
;
; Limits come from the box frame graphics (box widths 6/8/10/12 only):
;   up to 9 tiles (72px) per option, longer options are clipped,
;   up to M_ChoiceMenuMaxLines options,
;   M_ChoiceMenuTileCount tiles in total for all options.
; Menu text: CD/D3 = next option, CC = end, D5 xx = font, CE xx/D2 xx/D0 xx xx
; are skipped, CF/D1/D4 are ignored.

DEF M_ChoiceMenuTileBase  EQU $A2 ; VRAM bank 1, right after the message box strip ($80-$A1)
DEF M_ChoiceMenuTileCount EQU 42  ; $A2-$CB, the old kana/kanji glyph tiles
DEF M_ChoiceMenuMaxLines  EQU 5   ; the box frame tables only cover 5 options
DEF M_ChoiceMenuMaxTokens EQU $FF ; runaway guard for unterminated text

; Original choice menu variables (bank 09 clears $C720-$C75F on entry).
DEF W_ChoiceMenuSizeClass   EQU $C722 ; measured text width in tiles (1-8)
DEF W_ChoiceMenuOptionCount EQU $C723

; Scratch, inside the choice menu's own variable block.
DEF W_ChoiceMenuLineIndex    EQU $C731
DEF W_ChoiceMenuFieldWidth   EQU $C732
DEF W_ChoiceMenuLineAddress  EQU $C736 ; big-endian, like W_MainScriptLineMappingBaseLocation
DEF W_ChoiceMenuNextTile     EQU $C739
DEF W_ChoiceMenuTilesLeft    EQU $C73B
DEF W_ChoiceMenuTokenBudget  EQU $C73D

; Results the menu reads back from the measuring step.
DEF W_ChoiceMenuMeasuredWidth EQU $C4EE
DEF W_ChoiceMenuMeasuredLines EQU $C4F0

SECTION "Choice Menu Measure Hook", ROM0[$33A5]
  call ChoiceMenuMeasureText ; was call $33AA

SECTION "Choice Menu Bank 0 Functions", ROM0[$3F80]
ChoiceMenuCallVWFBank::
  ; a is the text table index, bc is the line in that table.
  ; de is a function in the VWF bank. It is called with de = text address and
  ; the text bank in W_BankPreservation, then the caller's bank is restored.
  push de
  ld d, a
  ld a, [W_CurrentBank]
  pop hl
  push af
  push hl
  ld a, d
  call LoadTextPointer
  call VWFGetTextPointerAddress
  ld a, [hli]
  ld [W_BankPreservation], a
  ld e, [hl]
  inc hl
  ld d, [hl]
  ld a, BANK(ChoiceMenuMeasureTextVWF)
  call VWFLowBankswitch
  pop hl
  call .jumpToHL
  pop af
  jp VWFLowBankswitch

.jumpToHL
  jp hl

ChoiceMenuMeasureText::
  ; Replaces the call to $33AA in CrossBank $B1. a is the text table index, bc the line.
  ld de, ChoiceMenuMeasureTextVWF
  jr ChoiceMenuCallVWFBank

ChoiceMenuDrawText::
  ; Replaces the print through CrossBank $27 in the choice menu.
  ld de, ChoiceMenuDrawTextVWF
  jr ChoiceMenuCallVWFBank

ChoiceMenuFetchTextByte::
  ; a = [de] from the text bank, de is advanced. Returns with the VWF bank loaded.
  call VWFDrawStringSwitchToStringBank
  ld a, [de]
  inc de
  push af
  ld a, BANK(ChoiceMenuMeasureTextVWF)
  call VWFLowBankswitch
  pop af
  ret

SECTION "Choice Menu VWF Functions", ROMX[$7D00], BANK[$C4]
ChoiceMenuNextToken::
  ; Reads from de until it has a letter or a line break.
  ; Carry set: a is a letter. Carry clear: a = 0 for a line break, 1 for the end.
  call ChoiceMenuFetchTextByte
  cp $80
  ret c
  cp $CC
  jr z, .end
  cp $CD
  jr z, .lineBreak
  cp $D3
  jr z, .lineBreak
  cp $D5
  jr z, .font
  cp $CE
  jr z, .skipOne
  cp $D2
  jr z, .skipOne
  cp $D0
  jr z, .skipTwo
  cp $CF
  jr z, ChoiceMenuNextToken
  cp $D1
  jr z, ChoiceMenuNextToken
  cp $D4
  jr z, ChoiceMenuNextToken
  ; Not in the font, confine the index like VWFDrawCharLoop does.
  and $7F
  scf
  ret

.font
  call ChoiceMenuFetchTextByte
  ld [W_VWFCurrentFont], a
  jr ChoiceMenuNextToken

.skipTwo
  call ChoiceMenuFetchTextByte
.skipOne
  call ChoiceMenuFetchTextByte
  jr ChoiceMenuNextToken

.lineBreak
  xor a
  ret

.end
  ld a, 1
  or a
  ret

ChoiceMenuLetterAdvance::
  ; a is a letter, returns its width plus the 1px gap. Preserves hl.
  push hl
  ld l, a
  ld a, [W_VWFCurrentFont]
  add HIGH(VWFDrawLetterTable)
  ld h, a
  ld a, [hl]
  inc a
  pop hl
  ret

ChoiceMenuMeasureTextVWF::
  ; de is the text. Sets W_ChoiceMenuMeasuredWidth to the tiles needed by the
  ; widest option (1-8, 8 also covers 9 tiles of text) and
  ; W_ChoiceMenuMeasuredLines to the number of options.
  xor a
  ld [W_VWFCurrentFont], a
  ld b, a ; b = width of the current option in pixels
  ld c, a ; c = width of the widest option in pixels
  ld h, a ; h = options
  ld l, a ; l = token budget

.loop
  dec l
  jr z, .endOfText
  call ChoiceMenuNextToken
  jr nc, .controlCode
  call ChoiceMenuLetterAdvance
  add b
  jr nc, .noOverflow
  ld a, $FF

.noOverflow
  ld b, a
  jr .loop

.controlCode
  or a
  jr nz, .endOfText
  call .endOption
  ld a, h
  cp M_ChoiceMenuMaxLines
  jr nc, .calculateTiles
  jr .loop

.endOfText
  ld a, b
  or a
  call nz, .endOption ; an option without a trailing line break still counts

.calculateTiles
  ld a, c
  or a
  jr z, .oneTile
  dec a ; the gap after the last letter isn't drawn
  ld b, a
  srl a
  srl a
  srl a
  ld c, a
  ld a, b
  and 7
  jr z, .roundedUp
  inc c

.roundedUp
  ld a, c
  or a
  jr z, .oneTile
  cp 9
  jr c, .storeWidth
  ld a, 8
  jr .storeWidth

.oneTile
  ld a, 1

.storeWidth
  ld [W_ChoiceMenuMeasuredWidth], a
  ld a, h
  or a
  jr nz, .storeLines
  inc a

.storeLines
  cp M_ChoiceMenuMaxLines + 1
  jr c, .linesOK
  ld a, M_ChoiceMenuMaxLines

.linesOK
  ld [W_ChoiceMenuMeasuredLines], a
  ld a, 1
  ld [W_MainScriptExitMode], a ; as the original measuring routine did
  ret

.endOption
  ld a, b
  cp c
  jr c, .notWidest
  ld c, a

.notWidest
  ld b, 0
  inc h
  ret

ChoiceMenuDrawTextVWF::
  ; de is the text. Draws one option per box line, starting at
  ; W_MainScriptLineMappingBaseLocation (set up by the menu, box + $22).
  xor a
  ld [W_VWFCurrentFont], a
  ld [W_ChoiceMenuLineIndex], a
  ld a, [W_ChoiceMenuSizeClass]
  or 1 ; the box is 3 tiles wider than the text area: 3/5/7/9 tiles of text
  cp 3
  jr nc, .storeFieldWidth
  ld a, 3

.storeFieldWidth
  ld [W_ChoiceMenuFieldWidth], a
  ld a, [W_MainScriptLineMappingBaseLocation]
  ld [W_ChoiceMenuLineAddress], a
  ld a, [W_MainScriptLineMappingBaseLocation + 1]
  ld [W_ChoiceMenuLineAddress + 1], a
  ld a, M_ChoiceMenuTileBase
  ld [W_ChoiceMenuNextTile], a
  ld a, M_ChoiceMenuTileCount
  ld [W_ChoiceMenuTilesLeft], a
  ld a, M_ChoiceMenuMaxTokens
  ld [W_ChoiceMenuTokenBudget], a

.nextOption
  ; Field = text area width, limited by the tiles we have left.
  ld a, [W_ChoiceMenuTilesLeft]
  ld b, a
  ld a, [W_ChoiceMenuFieldWidth]
  cp b
  jr c, .fieldFits
  ld a, b

.fieldFits
  ld [W_VWFTileLength], a
  ld a, [W_ChoiceMenuNextTile]
  ld [W_VWFTileBaseIdx], a
  xor a
  ld [W_VWFTilesDrawn], a
  ld [W_VWFLetterShift], a
  ld [W_VWFOldTileMode], a
  ld [W_VWFTextLength], a
  ld [W_VWFDiscardSecondTile], a
  ld a, [W_VWFTileLength]
  or a
  jr z, .clearCompositeArea
  push de
  ld b, a
  ld a, [W_VWFTileBaseIdx]
  call VWFTileIdx2Ptr
  call VWFEmptyDrawingRegion
  pop de

.clearCompositeArea
  ld hl, W_VWFCompositeArea
  ld b, $10
  xor a

.clearCompositeAreaLoop
  ld [hli], a
  dec b
  jr nz, .clearCompositeAreaLoop

.nextLetter
  ld a, [W_ChoiceMenuTokenBudget]
  dec a
  ld [W_ChoiceMenuTokenBudget], a
  jr z, .forceEnd
  call ChoiceMenuNextToken
  jr nc, .endOption
  ld [W_VWFCurrentLetter], a
  push de
  call VWFWriteCharLimited
  pop de
  jr .nextLetter

.forceEnd
  ld a, 1

.endOption
  push af
  call .mapOption
  pop af
  or a
  ret nz
  ld a, [W_ChoiceMenuLineIndex]
  inc a
  ld [W_ChoiceMenuLineIndex], a
  ld b, a
  ld a, [W_ChoiceMenuOptionCount]
  cp b
  ret z
  ret c
  ld a, [W_ChoiceMenuLineAddress]
  ld h, a
  ld a, [W_ChoiceMenuLineAddress + 1]
  ld l, a
  ld bc, $40 ; two rows down, as the original line break did
  add hl, bc
  call MainScriptConstrainTilemapAddress
  ld a, h
  ld [W_ChoiceMenuLineAddress], a
  ld a, l
  ld [W_ChoiceMenuLineAddress + 1], a
  jp .nextOption

.mapOption
  ; Map the tiles the option actually covers and point their attributes at VRAM bank 1.
  ld a, [W_VWFTileLength]
  or a
  ret z
  ld b, a
  ld a, [W_VWFTextLength]
  or a
  ret z
  dec a ; the gap after the last letter isn't drawn
  add 7
  srl a
  srl a
  srl a
  cp b
  jr c, .tilesUsed
  ld a, b

.tilesUsed
  or a
  ret z
  ld b, a
  ld a, [W_ChoiceMenuNextTile]
  ld c, a
  add b
  ld [W_ChoiceMenuNextTile], a
  ld a, [W_ChoiceMenuTilesLeft]
  sub b
  ld [W_ChoiceMenuTilesLeft], a
  ld a, [W_ChoiceMenuLineAddress]
  ld h, a
  ld a, [W_ChoiceMenuLineAddress + 1]
  ld l, a

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
  set 3, [hl]
  ei
  VRAMSwitchToBank0
  inc c
  inc hl
  call Tilemap0WrapToLine
  dec b
  jr nz, .mapLoop
  ret
