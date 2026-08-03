#!/usr/bin/env python3
"""Runner com estado da pipeline bt — coordenação mecânica, criação por agente.

O agente executa o trabalho de cada estágio (context, design, judge...), mas só
avança quando o artefato exigido EXISTE no disco. Estado em run.json; execução
interrompida é retomável de onde parou (`status` diz o que falta).

Comandos:
  new <slug> --env dev|prod [--n 3]     cria artifacts/bt/<slug>/ + run.json
  status <slug>                          estágio atual + artefatos faltantes
  advance <slug>                         valida artefatos do estágio atual e avança
  set <slug> <key> <value>               grava fato no run.json (winner, template_id...)
  show <slug>                            imprime o run.json

Estágios e artefatos exigidos (relativos a artifacts/bt/<slug>/):
  resolve     resolve.json  (output do resolve_tenant.py, exit 0)
  context     brief.md
  candidates  candidates/<X>/template.html + strip.png + design-notes.md  (≥1; alvo n)
  judge       judge-report.md
  fixes       winner definido (set winner <X>) + candidates/<winner>/strip.png
  finalize    output/slide-1.json + fidelity.md
  upload      template_id definido (set template_id <id>)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / "artifacts" / "bt"

STAGES = ["resolve", "context", "candidates", "judge", "fixes", "finalize", "upload", "done"]


def _dir(slug: str) -> Path:
    return BASE / slug


def _load(slug: str) -> dict:
    f = _dir(slug) / "run.json"
    if not f.exists():
        sys.exit(f"run inexistente: {f} — use `new {slug} --env dev|prod`")
    return json.loads(f.read_text(encoding="utf-8"))


def _save(slug: str, state: dict) -> None:
    (_dir(slug) / "run.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def missing_for(slug: str, state: dict) -> list[str]:
    d = _dir(slug)
    stage = state["stage"]
    miss: list[str] = []
    if stage == "resolve":
        f = d / "resolve.json"
        if not f.exists():
            miss.append("resolve.json (salve o stdout do resolve_tenant.py aqui; exit 0)")
        else:
            ok = json.loads(f.read_text(encoding="utf-8")).get("ok")
            if not ok:
                miss.append("resolve.json com ok=true (o atual tem ok=false)")
    elif stage == "context":
        if not (d / "brief.md").exists():
            miss.append("brief.md")
    elif stage == "candidates":
        found = [
            c.name
            for c in sorted((d / "candidates").glob("*"))
            if (c / "template.html").exists()
            and (c / "strip.png").exists()
            and (c / "design-notes.md").exists()
        ] if (d / "candidates").exists() else []
        n = state.get("n", 3)
        if len(found) < 1:
            miss.append(f"candidates/<X>/ completo (template.html + strip.png + design-notes.md); alvo {n}, completos: 0")
        elif len(found) < n:
            # ≥1 destrava com aviso; o alvo fica registrado
            state["candidates_ready"] = found
            miss.append(f"AVISO (não bloqueia): {len(found)}/{n} candidatos completos: {found}")
    elif stage == "judge":
        if not (d / "judge-report.md").exists():
            miss.append("judge-report.md")
    elif stage == "fixes":
        w = state.get("winner")
        if not w:
            miss.append("winner não definido (use `set <slug> winner <X>` conforme o judge-report)")
        elif not (d / "candidates" / w / "strip.png").exists():
            miss.append(f"candidates/{w}/strip.png (re-render pós-fixes)")
    elif stage == "finalize":
        if not (d / "output" / "slide-1.json").exists():
            miss.append("output/slide-1.json (conversão Fabric)")
        if not (d / "fidelity.md").exists():
            miss.append("fidelity.md (gate de fidelidade visual — checklist preenchida)")
    elif stage == "upload":
        if not state.get("template_id"):
            miss.append("template_id não definido (use `set <slug> template_id <id>` após o uploader)")
    return miss


def cmd_new(slug: str, env: str, n: int):
    d = _dir(slug)
    if (d / "run.json").exists():
        sys.exit(f"run já existe: use `status {slug}` para retomar")
    (d / "candidates").mkdir(parents=True, exist_ok=True)
    _save(slug, {
        "slug": slug,
        "env": env,
        "n": n,
        "stage": "resolve",
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "history": [],
    })
    print(f"run criado: {d}/run.json | env={env} | n={n} | estágio: resolve")
    print(f"IMPORTANTE: todo comando desta run usa --env {env}. Sem exceção.")


def cmd_status(slug: str):
    state = _load(slug)
    miss = missing_for(slug, state)
    print(f"run: {slug} | env={state['env']} | estágio atual: {state['stage']}")
    if state.get("winner"):
        print(f"winner: {state['winner']}")
    if state.get("template_id"):
        print(f"template_id: {state['template_id']}")
    blocking = [m for m in miss if not m.startswith("AVISO")]
    if state["stage"] == "done":
        print("run CONCLUÍDA.")
    elif blocking:
        print("faltando para avançar:")
        for m in miss:
            print(f"  - {m}")
    else:
        for m in miss:
            print(f"  - {m}")
        print(f"artefatos OK — rode `advance {slug}`.")


def cmd_advance(slug: str):
    state = _load(slug)
    if state["stage"] == "done":
        sys.exit("run já concluída.")
    miss = [m for m in missing_for(slug, state) if not m.startswith("AVISO")]
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


def cmd_set(slug: str, key: str, value: str):
    state = _load(slug)
    if key == "env":
        sys.exit("env é imutável após `new` — crie outra run.")
    state[key] = value
    _save(slug, state)
    print(f"{key} = {value}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    np_ = sub.add_parser("new"); np_.add_argument("slug"); np_.add_argument("--env", required=True, choices=["dev", "prod"]); np_.add_argument("--n", type=int, default=3)
    sp = sub.add_parser("status"); sp.add_argument("slug")
    ap = sub.add_parser("advance"); ap.add_argument("slug")
    st = sub.add_parser("set"); st.add_argument("slug"); st.add_argument("key"); st.add_argument("value")
    sh = sub.add_parser("show"); sh.add_argument("slug")
    a = p.parse_args()
    if a.cmd == "new":
        cmd_new(a.slug, a.env, a.n)
    elif a.cmd == "status":
        cmd_status(a.slug)
    elif a.cmd == "advance":
        cmd_advance(a.slug)
    elif a.cmd == "set":
        cmd_set(a.slug, a.key, a.value)
    elif a.cmd == "show":
        print(json.dumps(_load(a.slug), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
