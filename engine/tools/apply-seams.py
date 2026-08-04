#!/usr/bin/env python3
"""Injeta as costuras (seams.json, coordenadas de fita) nos slide-N.json convertidos.

Cada costura vira UM objeto em cada slide vizinho, com centro exatamente na
fronteira (metade fora do canvas — o Fabric clipa). Encaixe exato por construção.
Uso: python engine/tools/apply-seams.py <run-dir>   (espera output/ e seams.json)
"""
import json, sys
from pathlib import Path

run = Path(sys.argv[1])
seams_f = run / "seams.json"
out = run / "output"
if not seams_f.exists():
    print("sem seams.json — nada a aplicar"); sys.exit(0)
seams = json.loads(seams_f.read_text(encoding="utf-8"))
pack_slug = None
for sl in sorted(out.glob("slide-*.json")):
    d = json.loads(sl.read_text(encoding="utf-8"))
    if pack_slug is None:
        pack_slug = (d.get("_meta", {}).get("sourceClaudeDesign", "").split(":") + [None])[1]
repo = Path(__file__).resolve().parents[2]
pack = json.loads((repo / "packs" / pack_slug / "pack.json").read_text(encoding="utf-8"))
tok = pack["tokens"]

def obj(sm, cx):
    if sm["shape"] == "image":
        import base64
        src = "data:image/png;base64," + base64.b64encode((repo / "packs" / pack_slug / "assets" / sm["asset"]).read_bytes()).decode()
        return {"type": "ClippableImage", "name": "Costura", "left": cx, "top": sm["cy"],
                "originX": "center", "originY": "center", "width": sm["d"], "height": sm["d"],
                "topLeft": 0, "topRight": 0, "bottomRight": 0, "bottomLeft": 0,
                "crossOrigin": "anonymous", "src": src, "imageType": "userAsset"}
    tone = tok.get(sm.get("tone", "wm"), tok["wm"])
    ring = sm["shape"] == "ring"
    o = {"type": "roundedRect", "name": "Costura", "left": cx, "top": sm["cy"],
         "originX": "center", "originY": "center", "width": sm["d"], "height": sm["d"],
         "topLeft": 50, "topRight": 50, "bottomRight": 50, "bottomLeft": 50,
         "fill": "transparent" if ring else tone}
    if ring:
        o["stroke"] = tone; o["strokeWidth"] = sm.get("stroke", 4)
    return o

count = 0
for sm in seams:
    b = sm["boundary"]
    left_sl = out / f"slide-{b}.json"
    right_sl = out / f"slide-{b+1}.json"
    for f, cx in ((left_sl, 1080), (right_sl, 0)):
        if not f.exists(): continue
        d = json.loads(f.read_text(encoding="utf-8"))
        d["objects"].append(obj(sm, cx))
        f.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        count += 1
print(f"{len(seams)} costura(s) -> {count} objeto(s) injetado(s)")
