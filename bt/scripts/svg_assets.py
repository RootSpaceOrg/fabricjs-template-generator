#!/usr/bin/env python3
"""Assets SVG da biblioteca bt como objetos Fabric NATIVOS (path), não raster.

Dois comandos:

  build                      Parseia cada SVG de bt/references/assets/ e emite
                             <nome>.fabric.json ao lado (path commands absolutos,
                             bbox real, modo de pintura). Rodar quando a
                             biblioteca mudar; outputs são commitados.

  swap <dir-dos-slides>      Pós-processo da conversão (ANTES do
                             center-clippable-images): em cada slide-N.json,
                             substitui objetos de imagem cujo src aponta para um
                             asset da biblioteca (arquivo local ou cópia
                             recolorida) pelo path nativo equivalente, mantendo
                             left/top/angle/opacity/escala do frame e lendo a
                             cor (stroke/fill) do próprio arquivo SVG apontado.

Só stdlib. Suporta o subset de SVG usado pela biblioteca:
path[d] com M/m L/l C/c S/s H/h V/v Z/z, circle, g (herda stroke/fill).
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parents[1] / "references" / "assets"
KAPPA = 0.5522847498


# ---------------------------------------------------------------- d parser

def _tokens(d: str):
    for t in re.findall(r"[MmLlCcSsHhVvZz]|-?\d*\.?\d+(?:e-?\d+)?", d):
        yield t


def parse_path_d(d: str) -> list[list]:
    """d string -> fabric-style absolute commands [[\"M\",x,y],[\"C\",...],[\"L\",..],[\"Z\"]]."""
    out: list[list] = []
    cx = cy = sx = sy = 0.0
    last_c2 = None  # last cubic control point (for S/s reflection)
    it = list(_tokens(d))
    i = 0
    cmd = None
    while i < len(it):
        t = it[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t
            i += 1
            if cmd in "Zz":
                out.append(["Z"])
                cx, cy = sx, sy
                last_c2 = None
            continue
        # implicit command repetition uses current cmd
        def num(k):
            return float(it[i + k])

        if cmd in "Mm":
            x, y = num(0), num(1)
            if cmd == "m":
                x, y = cx + x, cy + y
            out.append(["M", x, y])
            cx, cy, sx, sy = x, y, x, y
            i += 2
            cmd = "L" if cmd == "M" else "l"  # subsequent pairs are lineto
            last_c2 = None
        elif cmd in "Ll":
            x, y = num(0), num(1)
            if cmd == "l":
                x, y = cx + x, cy + y
            out.append(["L", x, y])
            cx, cy = x, y
            i += 2
            last_c2 = None
        elif cmd in "Hh":
            x = num(0)
            if cmd == "h":
                x = cx + x
            out.append(["L", x, cy])
            cx = x
            i += 1
            last_c2 = None
        elif cmd in "Vv":
            y = num(0)
            if cmd == "v":
                y = cy + y
            out.append(["L", cx, y])
            cy = y
            i += 1
            last_c2 = None
        elif cmd in "Cc":
            x1, y1, x2, y2, x, y = (num(k) for k in range(6))
            if cmd == "c":
                x1, y1, x2, y2, x, y = cx + x1, cy + y1, cx + x2, cy + y2, cx + x, cy + y
            out.append(["C", x1, y1, x2, y2, x, y])
            cx, cy, last_c2 = x, y, (x2, y2)
            i += 6
        elif cmd in "Ss":
            x2, y2, x, y = (num(k) for k in range(4))
            if cmd == "s":
                x2, y2, x, y = cx + x2, cy + y2, cx + x, cy + y
            if last_c2 is not None:
                x1, y1 = 2 * cx - last_c2[0], 2 * cy - last_c2[1]
            else:
                x1, y1 = cx, cy
            out.append(["C", x1, y1, x2, y2, x, y])
            cx, cy, last_c2 = x, y, (x2, y2)
            i += 4
        else:
            raise ValueError(f"comando SVG não suportado: {cmd}")
    return out


def circle_to_cmds(cx: float, cy: float, r: float) -> list[list]:
    k = KAPPA * r
    return [
        ["M", cx - r, cy],
        ["C", cx - r, cy - k, cx - k, cy - r, cx, cy - r],
        ["C", cx + k, cy - r, cx + r, cy - k, cx + r, cy],
        ["C", cx + r, cy + k, cx + k, cy + r, cx, cy + r],
        ["C", cx - k, cy + r, cx - r, cy + k, cx - r, cy],
        ["Z"],
    ]


def bbox(cmds: list[list]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    px = py = 0.0
    for c in cmds:
        if c[0] == "M" or c[0] == "L":
            px, py = c[1], c[2]
            xs.append(px), ys.append(py)
        elif c[0] == "C":
            x0, y0 = px, py
            for t in (i / 10 for i in range(11)):
                mt = 1 - t
                x = mt**3 * x0 + 3 * mt**2 * t * c[1] + 3 * mt * t**2 * c[3] + t**3 * c[5]
                y = mt**3 * y0 + 3 * mt**2 * t * c[2] + 3 * mt * t**2 * c[4] + t**3 * c[6]
                xs.append(x), ys.append(y)
            px, py = c[5], c[6]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------- build

SVG_NS = "{http://www.w3.org/2000/svg}"


def _paint_of(el, inherited):
    stroke = el.get("stroke", inherited.get("stroke"))
    fill = el.get("fill", inherited.get("fill"))
    sw = el.get("stroke-width", inherited.get("stroke-width"))
    return {"stroke": stroke, "fill": fill, "stroke-width": sw}


def build_asset(svg_path: Path) -> dict:
    root = ET.parse(svg_path).getroot()
    cmds: list[list] = []
    paint = {"stroke": None, "fill": None, "stroke-width": None}

    def walk(el, inherited):
        nonlocal cmds, paint
        p = _paint_of(el, inherited)
        tag = el.tag.replace(SVG_NS, "")
        if tag == "path":
            cmds += parse_path_d(el.get("d"))
            paint = p
        elif tag == "circle":
            cmds += circle_to_cmds(float(el.get("cx")), float(el.get("cy")), float(el.get("r")))
            paint = p
        for child in el:
            walk(child, p)

    walk(root, {})
    x0, y0, x1, y1 = bbox(cmds)
    stroked = paint["stroke"] not in (None, "none")
    sw = float(paint["stroke-width"] or 0) if stroked else 0
    # bbox de geometria + metade do stroke em cada lado
    pad = sw / 2
    return {
        "name": svg_path.stem,
        "path": cmds,
        "left": x0 - pad,
        "top": y0 - pad,
        "width": (x1 - x0) + sw,
        "height": (y1 - y0) + sw,
        "paint": "stroke" if stroked else "fill",
        "strokeWidth": sw,
        "defaultColor": (paint["stroke"] if stroked else paint["fill"]) or "#111111",
    }


def cmd_build():
    for svg in sorted(ASSETS_DIR.glob("*.svg")):
        data = build_asset(svg)
        out = svg.with_suffix(".fabric.json")
        out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"{svg.name}: bbox {data['width']:.0f}x{data['height']:.0f} "
              f"({len(data['path'])} cmds, {data['paint']}) -> {out.name}")


# ---------------------------------------------------------------- swap

def _color_from_svg(svg_file: Path) -> str | None:
    try:
        m = re.search(r'(?:stroke|fill)="(#[0-9A-Fa-f]{3,8})"', svg_file.read_text(encoding="utf-8"))
        return m.group(1) if m else None
    except OSError:
        return None


def _asset_for_src(src: str) -> tuple[dict, str | None] | None:
    m = re.search(r"([A-Za-z0-9_-]+)\.svg", src or "")
    if not m:
        return None
    stem = m.group(1)
    # cópia recolorida usa sufixo livre; casa pelo prefixo do catálogo
    for fj in ASSETS_DIR.glob("*.fabric.json"):
        if stem == fj.stem.replace(".fabric", "") or stem.startswith(fj.stem.replace(".fabric", "")):
            data = json.loads(fj.read_text(encoding="utf-8"))
            local = re.sub(r"^file:///", "", src)
            color = _color_from_svg(Path(local)) if local else None
            return data, color
    return None


def swap_in_objects(objects: list, swapped: list) -> None:
    for idx, obj in enumerate(objects):
        if not isinstance(obj, dict):
            continue
        if "Image" in str(obj.get("type", "")) or obj.get("type") == "image":
            hit = _asset_for_src(obj.get("src", ""))
            if not hit:
                continue
            asset, color = hit
            color = color or asset["defaultColor"]
            frame_w = obj.get("width") or asset["width"]
            frame_h = obj.get("height") or asset["height"]
            path_obj = {
                "type": "path",
                "path": asset["path"],
                "width": asset["width"],
                "height": asset["height"],
                "pathOffset": {
                    "x": asset["left"] + asset["width"] / 2,
                    "y": asset["top"] + asset["height"] / 2,
                },
                "left": obj.get("left", 0),
                "top": obj.get("top", 0),
                "originX": obj.get("originX", "center"),
                "originY": obj.get("originY", "center"),
                "scaleX": (frame_w / asset["width"]) * obj.get("scaleX", 1),
                "scaleY": (frame_h / asset["height"]) * obj.get("scaleY", 1),
                "angle": obj.get("angle", 0),
                "opacity": obj.get("opacity", 1),
                "fill": color if asset["paint"] == "fill" else "",
                "stroke": color if asset["paint"] == "stroke" else None,
                "strokeWidth": asset["strokeWidth"],
                "strokeLineCap": "round",
                "selectable": True,
                "btAsset": asset["name"],
            }
            objects[idx] = path_obj
            swapped.append(asset["name"])
        elif isinstance(obj.get("objects"), list):
            swap_in_objects(obj["objects"], swapped)


def cmd_swap(slides_dir: str):
    d = Path(slides_dir)
    files = sorted(d.glob("slide-*.json"))
    if not files:
        print(f"nenhum slide-*.json em {d}")
        sys.exit(1)
    total = []
    for f in files:
        doc = json.loads(f.read_text(encoding="utf-8"))
        objects = doc.get("objects") or doc.get("canvasJson", {}).get("objects")
        swapped: list = []
        if objects:
            swap_in_objects(objects, swapped)
        if swapped:
            f.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        total += swapped
        print(f"{f.name}: {len(swapped)} asset(s) -> path nativo {swapped or ''}")
    print(f"total: {len(total)}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        cmd_build()
    elif len(sys.argv) >= 3 and sys.argv[1] == "swap":
        cmd_swap(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(2)
