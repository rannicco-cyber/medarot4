; Medalia (skill) names on the medal status screen: right-aligned VWF in the
; 5-cell field. Replaces the code that counted the name length and wrote
; (5 - length) blank cells, which locked the game for names longer than 5 characters.
; The bytes after the jp are dead code that is never reached.
SECTION "Medalia Name Right Aligned", ROMX[$5AA1], BANK[$02]
  ld hl, $992B
  ld bc, $C542
  ld a, 5
  jp PutStringVWFRight
