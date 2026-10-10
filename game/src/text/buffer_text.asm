INCLUDE "game/src/common/constants.asm"
INCLUDE "game/src/common/macros.asm"

SECTION "List Text Buffering", WRAM0[$C540]
W_ListItemIndexForBuffering:: ds 1
W_ListItemInitialOffsetForBuffering:: ds 1
W_ListItemBufferArea:: ds $C

SECTION "Buffer Text From List", ROM0[$299C]
BufferTextFromList::
  ; Arguments
  ;   b = pointer list index (idx)
  ;   c = max length (for old buffer)
  ;   [W_ListItemIndexForBuffering]
  ;   [W_ListItemInitialOffsetForBuffering]

  push bc ; keep the old buffer length for the translated list hook below
  ld a, BANK(BufferTextFromList_OldListHelper)
  rst $10
  call BufferTextFromList_OldListHelper
  jr z, .skipCopyIntoOldBuffer

  ; Get list pointer location.
  rst $10
  ld a, [W_ListItemIndexForBuffering]
  ld e, a
  ; d should already be 0.
  add hl, de
  add hl, de
  
  ; Get list item address.
  ld a, [hli]
  ld h, [hl]
  ld l, a
  ld a, [W_ListItemInitialOffsetForBuffering]
  ld e, a
  ; d should already be 0.
  add hl, de
  ld de, W_ListItemBufferArea

.copyLoop
  ld a, [hli]
  ld [de], a
  inc de
  dec c
  jr nz, .copyLoop

  ld a, BANK(BufferTextFromList_NewListHelper)
  rst $10

.skipCopyIntoOldBuffer
  call BufferTextFromList_NewListHelper
  rst $10
  ld de, W_NewListItemBufferArea
  ld c, $16 ; never copy more than the buffer holds ($17 bytes with the terminator)

.newCopyLoop
  ld a, [hli]
  
  cp $CB
  jr z, .addTerminator
  
  ld [de], a
  inc de
  dec c
  jr nz, .newCopyLoop

.addTerminator
  ld a, $CB
  ld [de], a
  ; Translated lists: overwrite the old (kana coded) buffer with the VWF/ASCII
  ; coded text so that dialogs and fixed-tile menus both see Latin characters.
  ; b = 1 if the list is translated (returned by BufferTextFromList_NewListHelper).
  pop de ; e = old buffer length
  ld a, b
  or a
  ret z
  cp 2
  jr nz, .hookGo
  ; Flag 2 (parts): the field at offset 0 is the model number. The part screens
  ; draw it with the orange kana-page glyph codes, so keep the old bytes there.
  ld a, [W_ListItemInitialOffsetForBuffering]
  or a
  ret z

.hookGo
  ld b, e
  ; Names may use the whole old buffer ($C bytes), not just the caller's length:
  ; the readers stop at the terminator. A single byte is a binary field (flags).
  ld a, b
  cp 2
  jr c, .hookLengthSet
  ld b, $C

.hookLengthSet
  ld hl, W_NewListItemBufferArea
  ld de, W_ListItemBufferArea
  ld a, b
  dec a
  jr nz, .hookCopy
  ; Single byte request: a binary field (flags etc.), copy it as is.
  ld a, [hl]
  ld [de], a
  ret

.hookCopy
  ld a, [hli]
  cp $CB
  jr z, .hookTerm
  dec b
  jr z, .hookForceTerm ; last slot: never copy a char there, always terminate
  ld [de], a
  inc de
  jr .hookCopy

.hookForceTerm
  ld a, $CB
  ld [de], a
  ret

.hookTerm
  ld [de], a
  inc de
  dec b
  ret z
  xor a
.hookPad
  ld [de], a
  inc de
  dec b
  jr nz, .hookPad
  ret

  padend $2A1A

SECTION "Buffer Text From List Pointer Bank Code", ROMX[$7C00], BANK[$D6]
BufferTextFromList_OldListHelper::
  ; Get list pointer table address.
  ld hl, ListPointerTable
  ld d, 0
  ld e, b
  add hl, de
  add hl, de
  add hl, de
  ld a, [hli]
  ; Don't copy from old buffer if bank is set to 0.
  or a
  ret z
  ld e, a
  ld a, [hli]
  ld h, [hl]
  ld l, a
  ld a, e
  ; We are assuming that the flags are untouched since the "or a" above. If not then add another "or a" here.
  ret

; Look in version folders for ListPointerTable

BufferTextFromList_NewListHelper::
  ; Get list pointer table address.
  ld hl, NewListPointerTable
  ld d, 0
  ld e, b
  add hl, de
  add hl, de
  ld a, [hli]
  ld h, [hl]
  ld l, a
  
  ; Get list pointer location.
  ld a, [W_ListItemIndexForBuffering]
  ld e, a
  ; d should already be 0.
  add hl, de
  add hl, de
  add hl, de

  ; Get list item address.
  ld a, [hli]
  ld c, a
  ld a, [hli]
  ld h, [hl]
  ld l, a
  ld a, [W_ListItemInitialOffsetForBuffering]
  ld e, a
  ; d should already be 0.
  add hl, de
  ; Return in b whether this list has been translated.
  push hl
  ld hl, TranslatedListFlags
  ld e, b
  ld d, 0
  add hl, de
  ld b, [hl]
  pop hl
  ld a, c
  ld c, $16
  ret

; One byte per pointer list index. 1 = the new (VWF coded) text replaces the
; old kana text in the old buffer (2 = same, but not the model number field at
; offset 0, used by the parts lists). Set a list to 1 once its ptrlist is translated.
TranslatedListFlags::
  db 0 ; 00 Unknown00
  db 2 ; 01 PartsHead
  db 2 ; 02 PartsRArm
  db 2 ; 03 PartsLArm
  db 2 ; 04 PartsLegs
  db 1 ; 05 Attributes
  db 1 ; 06 Skills
  db 1 ; 07 Movement
  db 0 ; 08 Unknown08
  db 1 ; 09 Personalities
  db 1 ; 0A Medaforce
  db 1 ; 0B Medals
  db 0 ; 0C Unknown0C
  db 1 ; 0D Items
  db 0 ; 0E Unknown0E
  db 0 ; 0F
  db 0 ; 10
  db 1 ; 11 Terrain
  db 1 ; 12 Attacks
  db 1 ; 13 EncounterNames
  db 0 ; 14 Unknown12
  db 1 ; 15 Medarots
  db 1 ; 16 Medarotters
  db 1 ; 17 Medarotters2
  db 0 ; 18 Unknown16
  db 0 ; 19 Unknown17
  db 0 ; 1A Unknown18 (default medal names, read from the new buffer directly)
  db 1 ; 1B MusicTitles

NewListPointerTable::
  dw PtrListUnknown00
  dw PtrListPartsHead
  dw PtrListPartsRArm
  dw PtrListPartsLArm
  dw PtrListPartsLegs
  dw PtrListAttributes
  dw PtrListSkills
  dw PtrListMovement
  dw PtrListUnknown08
  dw PtrListPersonalities
  dw PtrListMedaforce
  dw PtrListMedals
  dw PtrListUnknown0C
  dw PtrListItems
  dw PtrListUnknown0E
  dw $0000
  dw $0000
  dw PtrListTerrain
  dw PtrListAttacks
  dw PtrListEncounterNames
  dw PtrListUnknown12
  dw PtrListMedarots
  dw PtrListMedarotters
  dw PtrListMedarotters2
  dw PtrListUnknown16
  dw PtrListUnknown17
  dw PtrListUnknown18
  dw PtrListMusicTitles

; List includes are defined in version/ptrlist_data.asm
