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
  compose   fita.html (fita inteira: N sections + .fita-layer de travessias)
            gates: data-pack == pack da run · N dentro de pack.slides.min/max ·
            data-role por seção (1ª=abertura, última=fechamento, meio=item)
  render    strip.png mais novo que fita.html (engine/assemble.js)
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
        # Pesquisa do tema ANTES do dossiê. O knowledge do negócio é geral —
        # conhece o nicho, não o assunto — e sem material específico o dossiê
        # sai correto e genérico: serve a qualquer tema do setor e não ensina
        # nada a quem já conhece o básico (veredito do Gustavo, 2026-08-11).
        ctx = d / "contexto.md"
        if not ctx.exists():
            miss.append("contexto.md — pesquise o tema antes do dossiê (mecanismo, o que a "
                        "pessoa já tentou, erro comum, limite), com origem de cada afirmação")
        else:
            texto = ctx.read_text(encoding="utf-8", errors="replace")
            for campo in ("MECANISMO", "LIMITE"):
                if campo not in texto:
                    miss.append(f"contexto.md sem `{campo}:` — sem ele o dossiê não tem o que "
                                f"o leitor ainda não sabe")

        dossie = d / "dossie.md"
        if not dossie.exists():
            miss.append("dossie.md (storyline/copy — CONTEXT.md continua válido)")
        else:
            # O dossiê decide a imagem e a âncora de cada slide, não só a copy.
            # Sem isto ele entrega tese curta boiando no vazio (reprova no gate
            # de densidade) e conceito abstrato para a foto (vira imagem
            # genérica) — os dois defeitos nascem aqui, não na composição.
            texto = dossie.read_text(encoding="utf-8", errors="replace")
            for campo, porque in (("IMAGEM", "o objeto concreto do tema que cada slide mostra"),
                                  ("PESO", "o que ancora o slide além do texto")):
                if campo not in texto:
                    miss.append(f"dossie.md sem `{campo}:` por slide — {porque}")

    elif stage == "compose":
        # A imagem decide se o post presta, e nenhum gate consegue olhar o
        # PIXEL. O que dá para exigir é a intenção declarada antes de gerar:
        # o que a foto MOSTRA e qual PROBLEMA da peça ela torna visível.
        # Sem isso o prompt vira o clima do post e sai foto bonita e muda
        # (2026-08-11: quatro packs, mesmo tema, quatro capas de almofada).
        img = d / "imagens.md"
        if any((d / "assets").glob("*.png")) or any((d / "assets").glob("*.jpg")):
            if not img.exists():
                miss.append("imagens.md — declare por imagem: MOSTRA (objeto/gesto concreto) "
                            "e PROBLEMA (o que da peça ela torna visível), antes de gerar")
            else:
                texto = img.read_text(encoding="utf-8", errors="replace")
                for campo in ("MOSTRA", "PROBLEMA"):
                    if campo not in texto:
                        miss.append(f"imagens.md sem `{campo}:` — a foto precisa dizer o assunto, "
                                    f"não o clima")

        fita = d / "fita.html"
        if not fita.exists():
            miss.append("fita.html (fita inteira: N sections + .fita-layer — CATALOG.md §Esqueleto)")
        else:
            html = fita.read_text(encoding="utf-8", errors="replace")
            if f'data-pack="{state["pack"]}"' not in html:
                miss.append(f"fita.html: data-pack ≠ pack da run ({state['pack']})")
            roles = re.findall(r'<section[^>]*class="slide"[^>]*data-role="([^"]+)"', html) \
                or re.findall(r'<section[^>]*data-role="([^"]+)"[^>]*class="slide"', html)
            n_sec = len(re.findall(r'<section[^>]*class="slide"', html))
            if n_sec == 0:
                miss.append("fita.html sem <section class=\"slide\">")
            else:
                pk = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
                lo, hi = pk.get("slides", {}).get("min", 1), pk.get("slides", {}).get("max", 12)
                if not (lo <= n_sec <= hi):
                    miss.append(f"fita com {n_sec} slides — pack pede {lo}..{hi}")
                if len(roles) != n_sec:
                    miss.append("toda <section class=\"slide\"> precisa de data-role (abertura|item|fechamento; peça única = unica)")
                elif n_sec == 1:
                    if roles[0] != "unica":
                        miss.append("peça única: a seção deve ter data-role=\"unica\"")
                else:
                    if roles[0] != "abertura":
                        miss.append("1ª seção deve ter data-role=\"abertura\"")
                    if roles[-1] != "fechamento":
                        miss.append("última seção deve ter data-role=\"fechamento\"")
                    if any(r not in ("abertura", "item", "fechamento") for r in roles):
                        miss.append("data-role inválido (use abertura|item|fechamento)")

    elif stage == "render":
        strip = d / "strip.png"
        fita = d / "fita.html"
        if not strip.exists():
            miss.append("strip.png (node engine/assemble.js <run-dir>)")
        elif fita.exists() and strip.stat().st_mtime <= fita.stat().st_mtime:
            miss.append("strip.png ANTERIOR à fita.html — re-renderize (assemble.js)")

    elif stage == "convert":
        out = d / "output"
        if not (out / "slide-1.json").exists():
            miss.append("output/slide-1.json (node engine/convert.js <run-dir> output/)")
        else:
            # JSON mais VELHO que a fita = correção que não foi convertida. A
            # conservação de elId abaixo não pega: os ids continuam os mesmos
            # quando só o texto ou a posição mudam. O `render` já cobrava isso
            # do strip.png; o convert não cobrava nada, e o upload publicava o
            # JSON velho enquanto o strip mostrava a versão nova.
            fita = d / "fita.html"
            if fita.exists() and (out / "slide-1.json").stat().st_mtime < fita.stat().st_mtime:
                miss.append("output/ ANTERIOR à fita.html — reconverta (engine/convert.js); "
                            "senão a plataforma recebe a versão pré-correção")
            html_ids: set = set(re.findall(r'data-el-id="([^"]+)"',
                (d / "fita.html").read_text(encoding="utf-8", errors="replace")))
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


def cmd_new(slug: str, env: str, pack: str, n: int, business_type: str = ""):
    d = _dir(slug)
    if (d / "run.json").exists():
        sys.exit(f"run já existe: use `status {slug}` para retomar")
    if not (REPO / "packs" / pack / "pack.json").exists():
        sys.exit(f"pack inexistente: packs/{pack}/pack.json")
    (d / "slides").mkdir(parents=True, exist_ok=True)
    _save(slug, {
        "slug": slug, "env": env, "pack": pack, "n": n,
        # nicho do negócio, quando conhecido na criação. Tem precedência sobre o
        # que o resolve infere do assunto: quem pediu a run sabe o nicho, o
        # resolve só casa um texto com o catálogo.
        **({"business_type": business_type} if business_type else {}),
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
    state["history"].append({"stage": state["stage"], "at": time.strftime("%Y-%m-%d %H:%M:%S")})
    state["stage"] = STAGES[idx + 1]
    _save(slug, state)
    print(f"OK -> estágio atual: {state['stage']}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    np_ = sub.add_parser("new"); np_.add_argument("slug"); np_.add_argument("--env", required=True, choices=["dev", "prod"]); np_.add_argument("--pack", required=True); np_.add_argument("--n", type=int, default=8)
    np_.add_argument("--business-type", default="", help="nicho canônico (ver knowledge/business-types.json)")
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
        cmd_new(a.slug, a.env, a.pack, a.n, a.business_type)
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
