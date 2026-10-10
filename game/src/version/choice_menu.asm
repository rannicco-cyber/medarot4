; Choice menu (script command, bank 09 state machine at $5BEE in Kabuto).
; State 3 printed the options through the main script (CrossBank $27);
; the VWF build draws them with ChoiceMenuDrawText (patch/choice_menu.asm).
; a = text table index and bc = line are already set up by the call to $740A.
SECTION "Choice Menu Draw Hook", ROMX[$5C83+cCMOFFSET], BANK[$09]
  call ChoiceMenuDrawText ; was ld a, $27 / call CrossBankCall
  nop
  nop
