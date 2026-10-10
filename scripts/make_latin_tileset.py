#!/usr/bin/env python3
"""Build Tileset98004 as an ASCII-ordered Latin 8x8 font (tile id == VWF/ASCII code).
usage: make_latin_tileset.py <font.1bpp.png> <out.png> [fontname]"""
import sys
from PIL import Image
font=Image.open(sys.argv[1]).convert('L')
assert font.size==(128,64)
out=Image.new('L',(64,128),255)
for code in range(128):
    fx,fy=(code%16)*8,(code//16)*8
    cell=font.crop((fx,fy,fx+8,fy+8))
    # codes 0x0B-0x1D are '?' placeholder boxes in the VWF font: leave blank
    if 0x0B<=code<=0x1D or code==0 or code==0x20: cell=Image.new('L',(8,8),255)
    ox,oy=(code%8)*8,(code//8)*8
    out.paste(cell,(ox,oy))
out=out.point(lambda v:0 if v<128 else 255)
out.save(sys.argv[2])
