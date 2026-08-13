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
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
UPLOADER = Path(__file__).resolve().parent / "import-template.py"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("slug")
    p.add_argument("--name", default=None,
                   help="nome do template; sem isto usa o H1 do template-summary.md")
    p.add_argument("--tags", default="", help="tags extras além das automáticas")
    p.add_argument("--env", choices=["dev", "prod"], default=None,
                   help="ambiente de DESTINO; sem isto usa o env da run")
    p.add_argument("--tenant", default=None, help="tenant de destino (default: o da run)")
    p.add_argument("--vertical", default=None, help="vertical de destino (default: a da run)")
    p.add_argument("--execute", action="store_true")
    a = p.parse_args()

    d = REPO / "artifacts" / "runs" / a.slug
    state = json.loads((d / "run.json").read_text(encoding="utf-8"))
    resolve = json.loads((d / "resolve.json").read_text(encoding="utf-8"))
    if not resolve.get("ok"):
        sys.exit("resolve.json com ok=false — não há tenant/business_type válidos")

    # DESTINO ≠ ambiente da run. O resolve.json foi gerado contra o env de
    # criação: ele traz o tenantId/verticalId lidos do DynamoDB DAQUELE
    # ambiente. Publicar em outro exige re-resolver lá — o tenant pode não
    # existir, e publicar com o id errado grava template órfão em produção.
    env = a.env or state["env"]
    if resolve.get("offline") or env != state["env"] or a.tenant or a.vertical:
        alvo_tenant = a.tenant or resolve["tenantId"]
        alvo_vertical = a.vertical or resolve["verticalId"]
        r = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "resolve_tenant.py"),
             "--tenant", alvo_tenant, "--vertical", alvo_vertical, "--env", env,
             "--subject", (resolve.get("matchedBusinessType") or {}).get("value", "")],
            capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"resolve em {env} falhou para {alvo_tenant}/{alvo_vertical}:\n{r.stderr.strip()}")
        novo = json.loads(r.stdout)
        if not novo.get("ok"):
            sys.exit(f"{alvo_tenant}/{alvo_vertical} não existe em {env} "
                     f"({novo.get('message', 'sem tenantConfig')}) — publicação recusada")
        resolve = novo
        # grava o resolve do DESTINO: é dele que sai o domain do link do editor
        # no portal. Sem isto, publicar em prod deixaria o link apontando para
        # o ambiente errado (ou para lugar nenhum, com o resolve offline).
        if a.execute:
            (d / "resolve.json").write_text(
                json.dumps(novo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if state.get("stage") not in ("finalize", "upload", "done"):
        sys.exit(
            f"run está em '{state.get('stage')}' — upload permitido só em finalize "
            "(upload de teste, necessário pro gate de fidelidade no editor) ou upload (final)"
        )

    bt_value = (resolve.get("matchedBusinessType") or {}).get("value")
    if not bt_value:
        sys.exit("resolve.json sem matchedBusinessType.value — refaça o resolve com --subject")
    tenant, vertical = resolve["tenantId"], resolve["verticalId"]

    # O upload publica o output/, não a fita.html. Depois de uma correção o
    # agente costuma reescrever o HTML e re-renderizar o strip, mas esquecer o
    # convert — e aí sobe o JSON velho: a plataforma mostra a versão anterior ao
    # feedback enquanto o strip mostra a nova. Aconteceu duas vezes seguidas
    # (fissura4-clinical e -bold, 2026-08-12), e não havia gate nenhum.
    fita = d / "fita.html"
    slide1 = d / "output" / "slide-1.json"
    if fita.exists() and slide1.exists() and slide1.stat().st_mtime < fita.stat().st_mtime:
        sys.exit(
            f"output/ é ANTERIOR à fita.html — o JSON não tem as últimas correções.\n"
            f"  fita.html:          {time.strftime('%H:%M:%S', time.localtime(fita.stat().st_mtime))}\n"
            f"  output/slide-1.json:{time.strftime('%H:%M:%S', time.localtime(slide1.stat().st_mtime))}\n"
            f"Rode: node engine/convert.js artifacts/runs/{a.slug} "
            f"artifacts/runs/{a.slug}/output --slug {a.slug}"
        )

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
        "--env", env,
    ]
    if a.execute:
        cmd.append("--execute")

    origem = "" if env == state["env"] else f" (run criada em {state['env']})"
    print(f"env={env}{origem} business_type={bt_value} tenant={tenant}/{vertical} "
          f"tags={','.join(tags)} {'EXECUTE' if a.execute else 'DRY-RUN'}")
    r = subprocess.run(cmd)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
