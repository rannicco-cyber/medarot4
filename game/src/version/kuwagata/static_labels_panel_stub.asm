INCLUDE "game/src/common/constants.asm"
INCLUDE "game/src/common/macros.asm"

; The pause menu code (pausemenu/medawatch_core.asm) is shared by both versions and calls
; StaticLabelsPanelRedraw, which only Kabuto has (version/kabuto/static_labels.asm).
; Kuwagata has no static label VWF, so the call just shows the window layer like before.

SECTION "Static Labels Panel Redraw Stub", ROM0[$3E90]
StaticLabelsPanelRedraw::
  jp LCDCTileOverlaySetVisibility
