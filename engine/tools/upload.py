#!/usr/bin/env python3
"""Upload mecânico da pipeline — o agente não compõe flags, o estado compõe.

Lê run.json (env), resolve.json (tenant/vertical/business_type canônico) e
template-summary.md, e chama o import-template.py da pipeline genérica com os
parâmetros corretos (userReady, scope vertical, business_type preenchido).
A standing rule da pipeline genérica (prod/ai/platform) é ignorada por construção.

Uso:
  python engine/tools/upload.py <slug> --name "Nome do Template" [--tags extra1,extra2] [--execute]

Sem --execute = dry-run (payload impresso pelo uploader, nada gravado).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
UPLOADER = Path(__file__).resolve().parent / "import-template.py"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("slug")
    p.add_argument("--name", default=None,
                   help="nome do template; sem isto usa o H1 do template-summary.md")
    p.add_argument("--tags", default="", help="tags extras além das automáticas")
    p.add_argument("--execute", action="store_true")
    a = p.parse_args()

    d = REPO / "artifacts" / "runs" / a.slug
    state = json.loads((d / "run.json").read_text(encoding="utf-8"))
    resolve = json.loads((d / "resolve.json").read_text(encoding="utf-8"))
    if not resolve.get("ok"):
        sys.exit("resolve.json com ok=false — não há tenant/business_type válidos")
    if state.get("stage") not in ("finalize", "upload", "done"):
        sys.exit(
            f"run está em '{state.get('stage')}' — upload permitido só em finalize "
            "(upload de teste, necessário pro gate de fidelidade no editor) ou upload (final)"
        )

    bt_value = (resolve.get("matchedBusinessType") or {}).get("value")
    if not bt_value:
        sys.exit("resolve.json sem matchedBusinessType.value — refaça o resolve com --subject")
    tenant, vertical = resolve["tenantId"], resolve["verticalId"]

    summary = d / "template-summary.md"
    if not summary.exists():
        sys.exit("template-summary.md ausente na raiz da run (saída do marker)")

    # O nome vive no H1 do summary — o botão de upload do portal não tem onde
    # digitar um, e exigir --name deixava a ação quebrada por construção.
    nome = a.name
    if not nome:
        for linha in summary.read_text(encoding="utf-8").splitlines():
            if linha.startswith("# "):
                nome = linha[2:].strip()
                break
        if not nome:
            sys.exit("sem --name e template-summary.md não começa com '# Título'")

    funil = state.get("funil", "")
    tags = [bt_value] + ([f"funil-{funil}"] if funil else []) + [t for t in a.tags.split(",") if t.strip()]

    cmd = [
        sys.executable, str(UPLOADER), str(d),
        "--name", nome,
        "--template-type", "userReady",
        "--business-type", bt_value,
        "--tenant-id", tenant, "--vertical-id", vertical, "--scope", "vertical",
        "--tags", ",".join(tags),
        "--description-hint", summary.read_text(encoding="utf-8"),
        "--env", state["env"],
    ]
    if a.execute:
        cmd.append("--execute")

    print(f"env={state['env']} business_type={bt_value} tenant={tenant}/{vertical} "
          f"tags={','.join(tags)} {'EXECUTE' if a.execute else 'DRY-RUN'}")
    r = subprocess.run(cmd)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
