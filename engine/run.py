#!/usr/bin/env python3
"""Runner da fábrica — estados e gates mecânicos.

O agente executa o trabalho de cada estágio; o runner só avança quando o gate
EXECUTA e passa. Estado em artifacts/runs/<slug>/run.json; retomável.

Comandos:
  new <slug> --env dev|prod --pack <pack> [--n 8]   cria a run
  status <slug>        estágio atual + o que falta
  advance <slug>       executa gates do estágio e avança
  set <slug> <k> <v>   grava fato (winner, template_id...)
  show <slug> | list

Estágios e gates (artefatos relativos a artifacts/runs/<slug>/):
  resolve   resolve.json ok=true (engine/tools/resolve_tenant.py)
  context   dossie.md
  compose   draw.json (sorteio de recipes; "pares": [[i,i+1]] p/ par contínuo)
            + slides/slide-N.html
            gates: recipes existem no pack · nunca duas iguais adjacentes ·
            data-recipe do HTML == draw.json · data-pack == pack da run ·
            par contínuo declarado e com data-pos left/right nos vizinhos
  render    strip.png mais novo que todo slide-N.html (engine/assemble.js)
  convert   output/ via engine/convert.js · conservação data-el-id↔elId ·
            engine/tools/validate-slides.js exit 0
  judge     judge-report.md com PASS explícito (FAIL/all-blocked nega)
  finalize  fidelity.md com `VEREDITO: FIEL` e sem [ ]
  upload    template_id definido
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE = REPO / "artifacts" / "runs"

STAGES = ["resolve", "context", "compose", "render", "convert", "judge", "finalize", "upload", "done"]


def _dir(slug: str) -> Path:
    return BASE / slug


def _load(slug: str) -> dict:
    f = _dir(slug) / "run.json"
    if not f.exists():
        sys.exit(f"run inexistente: {f} — use `new {slug} --env dev|prod --pack <pack>`")
    return json.loads(f.read_text(encoding="utf-8"))


def _save(slug: str, state: dict) -> None:
    (_dir(slug) / "run.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _slide_files(d: Path) -> list[Path]:
    sd = d / "slides"
    if not sd.exists():
        return []
    return sorted(sd.glob("slide-*.html"), key=lambda p: int(re.search(r"\d+", p.name).group()))


def missing_for(slug: str, state: dict) -> list[str]:
    d = _dir(slug)
    stage = state["stage"]
    pack_dir = REPO / "packs" / state["pack"]
    miss: list[str] = []

    if stage == "resolve":
        f = d / "resolve.json"
        if not f.exists():
            miss.append("resolve.json (stdout do engine/tools/resolve_tenant.py; exit 0)")
        elif not json.loads(f.read_text(encoding="utf-8")).get("ok"):
            miss.append("resolve.json com ok=true (o atual tem ok=false)")

    elif stage == "context":
        if not (d / "dossie.md").exists():
            miss.append("dossie.md (storyline/copy — CONTEXT.md continua válido)")

    elif stage == "compose":
        draw_f = d / "draw.json"
        slides = _slide_files(d)
        if not draw_f.exists():
            miss.append('draw.json (sorteio: {"recipes": ["capa", "item-a", ...]})')
        if not slides:
            miss.append("slides/slide-1.html ... (1 arquivo por slide)")
        if draw_f.exists() and slides:
            draw = json.loads(draw_f.read_text(encoding="utf-8")).get("recipes", [])
            if len(draw) != len(slides):
                miss.append(f"draw.json tem {len(draw)} recipes mas há {len(slides)} slides")
            for r in set(draw):
                if not (pack_dir / "recipes" / f"{r}.json").exists():
                    miss.append(f"recipe inexistente no pack: {r}")
            for a, b in zip(draw, draw[1:]):
                if a == b:
                    miss.append(f"recipes iguais adjacentes ({a}) — variação é recombinação, nunca repetição vizinha")
            draw_obj = json.loads(draw_f.read_text(encoding="utf-8"))
            htmls: list[str] = []
            pos_by_slide: list[set] = []
            for i, sf in enumerate(slides):
                html = sf.read_text(encoding="utf-8", errors="replace")
                htmls.append(html)
                m = re.search(r'data-recipe="([^"]+)"', html)
                if i < len(draw) and (not m or m.group(1) != draw[i]):
                    miss.append(f"{sf.name}: data-recipe={m.group(1) if m else '∅'} ≠ draw.json[{i}]={draw[i]}")
                if f'data-pack="{state["pack"]}"' not in html:
                    miss.append(f"{sf.name}: data-pack ≠ pack da run ({state['pack']})")
                pos_by_slide.append(set(re.findall(r'data-pos="([^"]+)"', html)))

            # espelhamento: chave obrigatória; slide espelhado tem o grid-area do
            # 1º componente da recipe espelhado de verdade (C' = 14 - C, invertidos)
            esp = draw_obj.get("espelhados")
            if esp is None:
                miss.append('draw.json sem "espelhados" (lista de slides 1-based; pode ser vazia) — eixo de variância é parte do plano da fita')
            else:
                for i in esp:
                    if not (1 <= i <= len(slides)) or i - 1 >= len(draw):
                        miss.append(f"espelhados: slide {i} fora da fita")
                        continue
                    rf = pack_dir / "recipes" / f"{draw[i-1]}.json"
                    if not rf.exists():
                        continue
                    comp = next((c for c in json.loads(rf.read_text(encoding="utf-8"))["components"] if "area" in c), None)
                    if comp:
                        r1, c1, r2, c2 = [x.strip() for x in comp["area"].split("/")]
                        mirrored = f"{r1} / {14 - int(c2)} / {r2} / {14 - int(c1)}"
                        if mirrored not in htmls[i - 1]:
                            miss.append(f"slide-{i} declarado espelhado mas o grid-area não confere (1º componente esperado \"{mirrored}\")")

            # variância entre gerações: draw idêntico a run anterior do pack é reprovado
            key = ",".join(draw) + "|" + ",".join(str(x) for x in sorted(esp or []))
            log_f = pack_dir / "draws.log"
            if log_f.exists() and key in log_f.read_text(encoding="utf-8").splitlines():
                miss.append("draw idêntico a uma geração anterior deste pack (packs/<pack>/draws.log) — re-sorteie ordem do miolo e/ou espelhamentos")

            # par contínuo: declarado em draw.json "pares", slides vizinhos, e as duas
            # janelas embutidas DEVEM ser o split-pair.py da foto declarada (pixel a pixel)
            pares = draw_obj.get("pares", [])
            declared: set = set()
            for p in pares:
                foto = p.get("foto") if isinstance(p, dict) else None
                a, b = (p.get("slides", [0, 0]) if isinstance(p, dict) else p)
                declared |= {a, b}
                if b != a + 1:
                    miss.append(f"par {a},{b}: slides não são vizinhos")
                    continue
                if a < 1 or b > len(slides):
                    miss.append(f"par {a},{b}: fora da fita (1..{len(slides)})")
                    continue
                if "left" not in pos_by_slide[a - 1]:
                    miss.append(f"par {a},{b}: slide-{a} sem imagem data-pos=\"left\"")
                if "right" not in pos_by_slide[b - 1]:
                    miss.append(f"par {a},{b}: slide-{b} sem imagem data-pos=\"right\"")
                if not foto:
                    miss.append(f'par {a},{b}: declare "foto" (ex: {{"slides":[{a},{b}],"foto":"assets/x-wide.png"}}) — as janelas são verificadas contra ela')
                    continue
                fpath = d / foto
                if not fpath.exists():
                    miss.append(f"par {a},{b}: foto declarada inexistente: {foto}")
                    continue
                try:
                    import base64
                    import io

                    from PIL import Image
                except ImportError:
                    miss.append("pillow ausente no runner — pip install pillow (verificação do par)")
                    continue
                src = Image.open(fpath)
                W, H = src.size
                cx = W // 2

                def _half(idx: int, pos: str):
                    h = htmls[idx - 1]
                    mm = re.search(rf'data-pos="{pos}"[^>]*?src="data:image/[a-z]+;base64,([^"]+)"', h) \
                        or re.search(rf'src="data:image/[a-z]+;base64,([^"]+)"[^>]*?data-pos="{pos}"', h)
                    return Image.open(io.BytesIO(base64.b64decode(mm.group(1)))) if mm else None

                half_l, half_r = _half(a, "left"), _half(b, "right")
                if half_l and half_r:
                    cw = half_l.size[0]
                    ok_l = half_l.size[1] == H and src.crop((cx - cw, 0, cx, H)).tobytes() == half_l.convert(src.mode).tobytes()
                    ok_r = half_r.size == half_l.size and src.crop((cx, 0, cx + cw, H)).tobytes() == half_r.convert(src.mode).tobytes()
                    if not (ok_l and ok_r):
                        miss.append(f"par {a}|{b}: janelas embutidas NÃO são o split-pair da foto declarada — rode engine/tools/split-pair.py {foto} e embuta as duas metades (foto inteira nos dois slides = reprovado)")
            for i, poss in enumerate(pos_by_slide, 1):
                if poss and i not in declared:
                    miss.append(f"slide-{i}: data-pos sem par declarado em draw.json \"pares\"")

    elif stage == "render":
        strip = d / "strip.png"
        slides = _slide_files(d)
        if not strip.exists():
            miss.append("strip.png (node engine/assemble.js <slides-dir>)")
        elif slides and strip.stat().st_mtime <= max(s.stat().st_mtime for s in slides):
            miss.append("strip.png ANTERIOR aos slides — re-renderize (assemble.js)")

    elif stage == "convert":
        out = d / "output"
        if not (out / "slide-1.json").exists():
            miss.append("output/slide-1.json (node engine/convert.js slides/ output/)")
        else:
            html_ids: set = set()
            for sf in _slide_files(d):
                html_ids |= set(re.findall(r'data-el-id="([^"]+)"', sf.read_text(encoding="utf-8", errors="replace")))
            json_ids: set = set()
            for jf in out.glob("slide-*.json"):
                json_ids |= set(re.findall(r'"elId"\s*:\s*"([^"]+)"', jf.read_text(encoding="utf-8", errors="replace")))
            lost = sorted(html_ids - json_ids)
            invented = sorted(json_ids - html_ids)
            if lost:
                miss.append(f"conservação: {len(lost)} data-el-id sem objeto (perdidos): {lost[:6]}")
            if invented:
                miss.append(f"conservação: {len(invented)} elId inventados: {invented[:6]}")
            try:
                r = subprocess.run(
                    ["node", str(REPO / "engine" / "tools" / "validate-slides.js"), str(out)],
                    capture_output=True, text=True, timeout=180,
                    encoding="utf-8", errors="replace",
                )
                if r.returncode != 0:
                    tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-4:]
                    miss.append("validate-slides.js FALHOU: " + " | ".join(tail))
            except FileNotFoundError:
                miss.append("node não encontrado — validate-slides.js é gate obrigatório")
            except subprocess.TimeoutExpired:
                miss.append("validate-slides.js excedeu 180s")

    elif stage == "judge":
        jr = d / "judge-report.md"
        if not jr.exists():
            miss.append("judge-report.md")
        else:
            t = jr.read_text(encoding="utf-8", errors="replace")
            if re.search(r"QA:\s*FAIL|all-blocked", t, re.IGNORECASE):
                miss.append("judge-report FAIL/all-blocked — corrija o HTML, re-renderize e RE-JULGUE (substitua o report)")
            elif "PASS" not in t:
                miss.append("judge-report sem PASS explícito")
            strip = d / "strip.png"
            if strip.exists() and jr.stat().st_mtime < strip.stat().st_mtime:
                miss.append("judge-report é ANTERIOR ao strip.png atual — re-julgue o render vigente")

    elif stage == "finalize":
        fid = d / "fidelity.md"
        if not fid.exists():
            miss.append("fidelity.md (gate de fidelidade visual JSON vs strip)")
        else:
            t = fid.read_text(encoding="utf-8", errors="replace")
            if "VEREDITO: FIEL" not in t:
                miss.append("fidelity.md sem `VEREDITO: FIEL` — divergiu? corrija a etapa culpada, não avance")
            if "[ ]" in t:
                miss.append("fidelity.md com checklist não verificado ([ ])")

    elif stage == "upload":
        if not state.get("template_id"):
            miss.append("template_id não definido (use `set <slug> template_id <id>` após o uploader)")

    return miss


def cmd_new(slug: str, env: str, pack: str, n: int):
    d = _dir(slug)
    if (d / "run.json").exists():
        sys.exit(f"run já existe: use `status {slug}` para retomar")
    if not (REPO / "packs" / pack / "pack.json").exists():
        sys.exit(f"pack inexistente: packs/{pack}/pack.json")
    (d / "slides").mkdir(parents=True, exist_ok=True)
    _save(slug, {
        "slug": slug, "env": env, "pack": pack, "n": n,
        "stage": "resolve",
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "history": [],
    })
    print(f"run criada: {d}/run.json | env={env} | pack={pack} | n={n} | estágio: resolve")
    print(f"IMPORTANTE: todo comando desta run usa --env {env}. Sem exceção.")


def cmd_status(slug: str):
    state = _load(slug)
    miss = missing_for(slug, state)
    print(f"run: {slug} | env={state['env']} | pack={state['pack']} | estágio: {state['stage']}")
    if state.get("template_id"):
        print(f"template_id: {state['template_id']}")
    if state["stage"] == "done":
        print("run CONCLUÍDA.")
    elif miss:
        print("faltando para avançar:")
        for m in miss:
            print(f"  - {m}")
    else:
        print(f"gates OK — rode `advance {slug}`.")


def cmd_advance(slug: str):
    state = _load(slug)
    if state["stage"] == "done":
        sys.exit("run já concluída.")
    miss = missing_for(slug, state)
    if miss:
        print(f"NEGADO — estágio '{state['stage']}' incompleto:")
        for m in miss:
            print(f"  - {m}")
        sys.exit(1)
    idx = STAGES.index(state["stage"])
    if state["stage"] == "compose":
        # registra o draw aprovado — gerações futuras não podem repetir (variância)
        draw_obj = json.loads((_dir(slug) / "draw.json").read_text(encoding="utf-8"))
        key = ",".join(draw_obj.get("recipes", [])) + "|" + ",".join(
            str(x) for x in sorted(draw_obj.get("espelhados") or []))
        with open(REPO / "packs" / state["pack"] / "draws.log", "a", encoding="utf-8") as fh:
            fh.write(key + "\n")
    state["history"].append({"stage": state["stage"], "at": time.strftime("%Y-%m-%d %H:%M:%S")})
    state["stage"] = STAGES[idx + 1]
    _save(slug, state)
    print(f"OK -> estágio atual: {state['stage']}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    np_ = sub.add_parser("new"); np_.add_argument("slug"); np_.add_argument("--env", required=True, choices=["dev", "prod"]); np_.add_argument("--pack", required=True); np_.add_argument("--n", type=int, default=8)
    for c in ("status", "advance", "show"):
        sub.add_parser(c).add_argument("slug")
    st = sub.add_parser("set"); st.add_argument("slug"); st.add_argument("key"); st.add_argument("value")
    sub.add_parser("list")
    a = p.parse_args()
    if a.cmd == "list":
        for rj in sorted(BASE.glob("*/run.json")):
            s = json.loads(rj.read_text(encoding="utf-8"))
            last = s["history"][-1]["at"] if s.get("history") else s.get("created", "?")
            flag = "" if s["stage"] == "done" else "  <- INCOMPLETA"
            print(f"{s['slug']:32} {s['env']:4} {s.get('pack', '?'):28} {s['stage']:10} {last}{flag}")
        return
    if a.cmd == "new":
        cmd_new(a.slug, a.env, a.pack, a.n)
    elif a.cmd == "status":
        cmd_status(a.slug)
    elif a.cmd == "advance":
        cmd_advance(a.slug)
    elif a.cmd == "set":
        state = _load(a.slug)
        if a.key in ("env", "pack"):
            sys.exit(f"{a.key} é imutável após `new` — crie outra run.")
        state[a.key] = a.value
        _save(a.slug, state)
        print(f"{a.key} = {a.value}")
    elif a.cmd == "show":
        print(json.dumps(_load(a.slug), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
