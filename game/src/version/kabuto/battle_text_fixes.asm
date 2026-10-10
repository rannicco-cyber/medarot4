; Kabuto battle / medal text fixes. See PENDING_FIXES.md.

; ---------------------------------------------------------------------------
; Names copied from the list buffer ($C542) with a fixed 6 bytes lose their $CB
; terminator when they have 6 or more characters. Copy 9 bytes (BUF01 is 9 bytes
; wide, and the list hook pads with zeros after the terminator).
SECTION "Battle Name Copy 0C", ROMX[$4EF0], BANK[$0C]
  db 9 ; was 6 (skill name -> BUF01)
SECTION "Battle Name Copy 0D", ROMX[$4748], BANK[$0D]
  db 9 ; was 6 (skill name -> BUF01)
SECTION "Battle Name Copy 17", ROMX[$4D15], BANK[$17]
  db 9 ; was 6 (skill name -> BUF01)
SECTION "Battle Name Copy 0F", ROMX[$6A1C], BANK[$0F]
  db 9 ; was 6 (terrain name -> BUF00)

; Medal name -> $C502 (8-byte name buffer).
SECTION "Medal Name Copy Length", ROMX[$6FAC], BANK[$11]
  db 8 ; was 6: copy the whole name buffer so the end marker is kept

; ---------------------------------------------------------------------------
; Body part slot names for the battle messages (BUF01 + "-osa"). Every battle
; bank has its own copy of this table of 4 entries x 8 bytes (7 characters + $CB).
; Codes are from scripts/res/tilesets/VWF.lst (ä = $02).
SECTION "Battle Slot Names 01_6B04", ROMX[$6B04], BANK[$01]
  db $50, $02, $02, $CB, 0, 0, 0, 0 ; Pää
  db $4F, $2E, $6B, $02, $73, $69, $CB, 0 ; O.käsi
  db $56, $2E, $6B, $02, $73, $69, $CB, 0 ; V.käsi
  db $4A, $61, $6C, $6B, $61, $CB, 0, 0 ; Jalka

SECTION "Battle Slot Names 0B_52F6", ROMX[$52F6], BANK[$0B]
  db $50, $02, $02, $CB, 0, 0, 0, 0 ; Pää
  db $4F, $2E, $6B, $02, $73, $69, $CB, 0 ; O.käsi
  db $56, $2E, $6B, $02, $73, $69, $CB, 0 ; V.käsi
  db $4A, $61, $6C, $6B, $61, $CB, 0, 0 ; Jalka

SECTION "Battle Slot Names 0C_5303", ROMX[$5303], BANK[$0C]
  db $50, $02, $02, $CB, 0, 0, 0, 0 ; Pää
  db $4F, $2E, $6B, $02, $73, $69, $CB, 0 ; O.käsi
  db $56, $2E, $6B, $02, $73, $69, $CB, 0 ; V.käsi
  db $4A, $61, $6C, $6B, $61, $CB, 0, 0 ; Jalka

SECTION "Battle Slot Names 0D_476F", ROMX[$476F], BANK[$0D]
  db $50, $02, $02, $CB, 0, 0, 0, 0 ; Pää
  db $4F, $2E, $6B, $02, $73, $69, $CB, 0 ; O.käsi
  db $56, $2E, $6B, $02, $73, $69, $CB, 0 ; V.käsi
  db $4A, $61, $6C, $6B, $61, $CB, 0, 0 ; Jalka

SECTION "Battle Slot Names 0E_5192", ROMX[$5192], BANK[$0E]
  db $50, $02, $02, $CB, 0, 0, 0, 0 ; Pää
  db $4F, $2E, $6B, $02, $73, $69, $CB, 0 ; O.käsi
  db $56, $2E, $6B, $02, $73, $69, $CB, 0 ; V.käsi
  db $4A, $61, $6C, $6B, $61, $CB, 0, 0 ; Jalka

SECTION "Battle Slot Names 0F_4A06", ROMX[$4A06], BANK[$0F]
  db $50, $02, $02, $CB, 0, 0, 0, 0 ; Pää
  db $4F, $2E, $6B, $02, $73, $69, $CB, 0 ; O.käsi
  db $56, $2E, $6B, $02, $73, $69, $CB, 0 ; V.käsi
  db $4A, $61, $6C, $6B, $61, $CB, 0, 0 ; Jalka

SECTION "Battle Slot Names 15_60CA", ROMX[$60CA], BANK[$15]
  db $50, $02, $02, $CB, 0, 0, 0, 0 ; Pää
  db $4F, $2E, $6B, $02, $73, $69, $CB, 0 ; O.käsi
  db $56, $2E, $6B, $02, $73, $69, $CB, 0 ; V.käsi
  db $4A, $61, $6C, $6B, $61, $CB, 0, 0 ; Jalka

SECTION "Battle Slot Names 17_4D3C", ROMX[$4D3C], BANK[$17]
  db $50, $02, $02, $CB, 0, 0, 0, 0 ; Pää
  db $4F, $2E, $6B, $02, $73, $69, $CB, 0 ; O.käsi
  db $56, $2E, $6B, $02, $73, $69, $CB, 0 ; V.käsi
  db $4A, $61, $6C, $6B, $61, $CB, 0, 0 ; Jalka


; ---------------------------------------------------------------------------
; "Vaihde A/B/C" (ドライブA..C, Drive). The Medachange HUD writes these 8 tile ids per box
; straight into the BG map ($99C6/$9A0B/$9A01), so they are ASCII tile ids of the Latin
; font (tile id == character code). 8 cells per box: "Vaihde A" (8 cells).
SECTION "Drive Labels 0A", ROMX[$5EA4], BANK[$0A]
  db "Vaihde A"
  db "Vaihde B"
  db "Vaihde C"

SECTION "Drive Labels 12", ROMX[$6400], BANK[$12]
  db "Vaihde A"
  db "Vaihde B"
  db "Vaihde C"

; Same strings printed with the tile text routine (terminated with $CB).
SECTION "Drive Labels FA", ROMX[$67C9], BANK[$FA]
  db "Vaihde", $00, "A", $CB
  db "Vaihde", $00, "B", $CB
  db "Vaihde", $00, "C", $CB

; Names used inside battle messages (VWF text). The game looked them up at 8 bytes per entry, which
; allowed 7 letters. The lookup (bank 0B $5316: de = destination, hl = destination too, a = 0..2)
; now uses 16 bytes per entry from a table in free space, so "Vaihde A" fits in the 9 byte message
; buffers (8 letters and the terminator). The 10 bytes freed by the shorter code are nops.
SECTION "Drive Names 0B", ROMX[$7C9E], BANK[$0B]
DriveNames:
  db "Vaihde A", $CB
  ds 7, $00
  db "Vaihde B", $CB
  ds 7, $00
  db "Vaihde C", $CB
  ds 7, $00

SECTION "Drive Names Lookup 0B", ROMX[$5316], BANK[$0B]
  push de
  push hl
  ld hl, DriveNames
  swap a
  ld c, a
  ld b, 0
  add hl, bc
  ds 10, $00

; Skill names (list 6) are copied into $C542 with "ld c, 6" at every call site: names of six letters
; or more lost their $CB terminator and ran on into the next buffer ("Kannustus" + the attack name).
; The copy is now 9 bytes, like the part names (8 letters + terminator).
SECTION "Skill Name Copy 0", ROMX[$5A93], BANK[$02]
  db 9
SECTION "Skill Name Copy 1", ROMX[$5C5A], BANK[$02]
  db 9
SECTION "Skill Name Copy 2", ROMX[$5C9F], BANK[$02]
  db 9
SECTION "Skill Name Copy 3", ROMX[$5CE4], BANK[$02]
  db 9
SECTION "Skill Name Copy 4", ROMX[$5DB1], BANK[$02]
  db 9
SECTION "Skill Name Copy 5", ROMX[$5E29], BANK[$02]
  db 9
SECTION "Skill Name Copy 6", ROMX[$5EA1], BANK[$02]
  db 9
SECTION "Skill Name Copy 7", ROMX[$6549], BANK[$02]
  db 9
SECTION "Skill Name Copy 8", ROMX[$6F54], BANK[$02]
  db 9
SECTION "Skill Name Copy 9", ROMX[$6F8E], BANK[$02]
  db 9
SECTION "Skill Name Copy 10", ROMX[$6FC8], BANK[$02]
  db 9
SECTION "Skill Name Copy 11", ROMX[$701C], BANK[$02]
  db 9
SECTION "Skill Name Copy 12", ROMX[$7083], BANK[$02]
  db 9
SECTION "Skill Name Copy 13", ROMX[$70EA], BANK[$02]
  db 9
SECTION "Skill Name Copy 14", ROMX[$6DB6], BANK[$04]
  db 9
SECTION "Skill Name Copy 15", ROMX[$708D], BANK[$06]
  db 9
SECTION "Skill Name Copy 16", ROMX[$4EDB], BANK[$0C]
  db 9
SECTION "Skill Name Copy 17", ROMX[$4733], BANK[$0D]
  db 9
SECTION "Skill Name Copy 18", ROMX[$4D00], BANK[$17]
  db 9
SECTION "Skill Name Copy 19", ROMX[$6525], BANK[$54]
  db 9
SECTION "Skill Name Copy 20", ROMX[$6622], BANK[$54]
  db 9
SECTION "Skill Name Copy 21", ROMX[$435C], BANK[$F7]
  db 9
SECTION "Skill Name Copy 22", ROMX[$505D], BANK[$F7]
  db 9
