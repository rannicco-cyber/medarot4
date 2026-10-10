INCLUDE "game/src/common/constants.asm"
INCLUDE "game/src/common/macros.asm"

; Bank 09 code from $599F on sits 1 byte lower in Kuwagata (see wrappers.asm).
DEF cCMOFFSET EQU 0
INCLUDE "./game/src/version/choice_menu.asm"
