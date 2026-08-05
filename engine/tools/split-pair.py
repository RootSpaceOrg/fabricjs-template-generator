#!/usr/bin/env python3
"""Par contínuo: corta de UMA foto paisagem as duas janelas verticais adjacentes
ao centro (aspect do frame), uma por slide vizinho — a emenda cai no sujeito.

Uso: python engine/tools/split-pair.py <foto.png> <outL.png> <outR.png> --frame 450x1350
Falha se a foto não for larga o bastante para duas janelas distintas — a
correção é regenerar a foto mais larga (>=1792x1024), nunca aceitar repetição.
"""
import argparse
import sys

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("photo")
ap.add_argument("out_left")
ap.add_argument("out_right")
ap.add_argument("--frame", required=True, help="WxH do frame no slide, ex: 450x1350")
a = ap.parse_args()

fw, fh = (int(v) for v in a.frame.lower().split("x"))
im = Image.open(a.photo)
W, H = im.size
cw = round(H * fw / fh)
if W < 2 * cw:
    sys.exit(f"REJEITADO — foto {W}x{H} estreita demais para 2 janelas de {cw}px "
             f"(precisa >= {2*cw}px de largura): regenere a foto mais larga/paisagem")
cx = W // 2
im.crop((cx - cw, 0, cx, H)).save(a.out_left)
im.crop((cx, 0, cx + cw, H)).save(a.out_right)
print(f"janelas {cw}x{H}: left [{cx-cw},{cx}] right [{cx},{cx+cw}] de {W}x{H}")
