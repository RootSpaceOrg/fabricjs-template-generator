#!/usr/bin/env python3
"""Comandos de chat da fábrica — fechados, sem interpretação livre no parser.

O portal valida o mínimo determinístico (pack existe? é certificado?) e monta o
prompt; a interpretação do pedido é do agente.
"""
from __future__ import annotations

import re

import knowledge as kb
from jobs import RUNS, enfileirar

AJUDA = (
    "*Fábrica — comandos*\n"
    "`/nova <pedido>` — linguagem natural; cite o pack ou deixe o agente escolher\n"
    "   ex.: `/nova bold-educacional mitos sobre laser, laserterapia`\n"
    "   ex.: `/nova post de topo de funil sobre fibromialgia` (agente escolhe o estilo)\n"
    "`/packs` — packs disponíveis (✅ certificado, 🟡 draft)\n"
    "`/runs` — últimas runs e em que estágio estão\n"
    "`/ajuda` — esta lista"
)


def slug_novo(pack: str, tema: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", tema.lower()).strip("-")[:24] or "post"
    slug = f"{pack.split('-')[0]}-{base}"
    cand, n = slug, 2
    while (RUNS / cand).exists():
        cand, n = f"{slug}-{n}", n + 1
    return cand


def prompt_nova(slug: str, pack: str | None, tema: str, pedido: str = "",
                tenant: str = "kultivai", vertical: str = "health",
                env: str = "dev", business: str = "", n: str = "") -> str:
    """Prompt do turno de criação. `pack=None` = o agente escolhe o estilo."""
    cabeca = (
        f"NOVA RUN pedida pelo Gustavo (fabrica; git pull --rebase antes).\n"
        f'PEDIDO ORIGINAL (interprete): "{pedido or tema}"\n'
        f"Comece o relatorio dizendo o que voce entendeu: pack, tema, funil, slides e ambiente.\n"
        f"Se faltar algo ESSENCIAL (nicho/tema indefinido), PARE e pergunte.\n"
        f"O campo `fit` do pack.json e CONSELHO, nao regra: usar um pack fora do funil sugerido "
        f"e permitido — so justifique no dossie em 1 linha. NAO bloqueie a run por causa do fit.\n"
        f"Se o pedido mencionar producao/prod, monte em DEV assim mesmo e avise que publicar em "
        f"prod exige confirmacao explicita.\n\n"
    )

    if pack:
        leitura = (
            f"PACK: {pack}. Leia packs/{pack}/tecnicas.md + images.md + lessons.md, alem de "
            f"README.md, CONTEXT.md, engine/CATALOG.md, knowledge/copy/frameworks.md, "
            f"knowledge/copy/negocios/ (dossie do negocio do tema) e knowledge/design/geral.md.\n\n"
        )
        comando = (f"Comando inicial: python3 engine/run.py new {slug} --env {env} --pack {pack} "
                   f"--n {n or '<dentro do range do pack>'}\n")
    else:
        leitura = (
            "PACK: o Gustavo NAO escolheu — ESCOLHA VOCE. Compare os packs em packs/*/pack.json "
            "(use os certificados; olhe `fit.melhor_em` e as assinaturas) com o tema pedido e "
            "justifique a escolha no dossie em 1 linha. Depois leia tecnicas.md + images.md + "
            "lessons.md do pack escolhido, alem de README.md, CONTEXT.md, engine/CATALOG.md, "
            "knowledge/copy/frameworks.md, knowledge/copy/negocios/ e knowledge/design/geral.md.\n\n"
        )
        comando = (f"Comando inicial: python3 engine/run.py new {slug} --env {env} "
                   f"--pack <o pack que voce escolheu> --n {n or '<dentro do range do pack>'}\n")

    contexto = (
        f"CONTEXTO (definido pelo Gustavo — use, nao pergunte de novo): tenant={tenant} · "
        f"vertical={vertical} · env={env}"
        f"{' · business_type=' + business if business else ' · business_type: infira do tema'}"
        f"{' · slides=' + n if n else ''}\n"
        f"TEMA: {tema}\n\n"
    )
    resolve = (
        f"Resolve: python3 engine/tools/resolve_tenant.py --tenant {tenant} --vertical {vertical} "
        f"--env {env}"
        f"{' --subject ' + business if business else ' --subject <o nicho do tema>'}"
        f" > artifacts/runs/{slug}/resolve.json\n\n"
    )
    corpo = (
        "VOCE e o copy specialist E o designer desta run:\n"
        "1. resolve (comando acima) e context: dossie.md declarando OBJETIVO, FRAMEWORK "
        "(knowledge/copy/frameworks.md), ARCO (gramatica do acervo) e o open loop de cada slide;\n"
        "2. gere as imagens do tema (fotos e colagens/decors) seguindo images.md do pack;\n"
        "3. compose: UM fita.html seguindo o CATALOG e as tecnicas do pack (miolo com objeto de "
        "conteudo, hierarquia, contraste pelo fundo da caixa, CTA so onde ha acao);\n"
        f"4. rode 'node engine/assemble.js artifacts/runs/{slug}' e PARE ai.\n\n"
        "O corredor (convert/judge) e a revisao vem depois. Reporte o caminho do strip.png."
    )
    return cabeca + leitura + contexto + comando + resolve + corpo


def executar(texto: str) -> str:
    """Interpreta um comando e devolve a resposta em Markdown."""
    cmd, _, resto = texto.partition(" ")
    cmd, resto = cmd.lower().lstrip("/").split("@")[0], resto.strip()

    if cmd in ("ajuda", "help", "start"):
        return AJUDA

    if cmd == "packs":
        linhas = [
            f"{'✅' if p['status'] == 'certificado' else '🟡'} `{p['slug']}`\n"
            f"   {p['familia'][:70]}"
            for p in kb.packs()
        ]
        return "*Packs*\n" + "\n".join(linhas) if linhas else "Nenhum pack."

    if cmd == "runs":
        from app import _runs  # import tardio: evita ciclo
        linhas = [
            f"`{r['slug']}` — {r['stage']}" + (f" · QA {r['qa']}" if r["qa"] else "") + f" · {r['age']}"
            for r in _runs()[:8]
        ]
        return "*Últimas runs*\n" + "\n".join(linhas) if linhas else "Nenhuma run."

    if cmd == "nova":
        if not resto:
            return ("Use `/nova <pedido>`\n"
                    "Ex.: `/nova bold-educacional mitos sobre laser, laserterapia`\n"
                    "Sem citar pack, o agente escolhe o estilo pelo tema.")
        certificados = {p["slug"] for p in kb.packs() if p["status"] == "certificado"}
        pack = next((s for s in sorted(certificados, key=len, reverse=True) if s in resto), None)
        tema = resto.replace(pack, "", 1).strip(" ,-—:") if pack else resto
        if not tema:
            return f"Faltou o tema. Ex.: `/nova {pack} mitos sobre laser, laserterapia`"
        slug = slug_novo(pack or "run", tema)
        enfileirar("agente", slug, prompt_nova(slug, pack, tema, pedido=resto))
        aviso = ("\n\n⚠️ Você mencionou *prod*: a run vai para dev; publicar em produção "
                 "exige confirmação separada.") if re.search(r"\bprod", resto, re.I) else ""
        quem = f"pack `{pack}`" if pack else "_pack a escolher pelo agente_"
        return (f"Run `{slug}` enfileirada — {quem}, ambiente dev.\n"
                f"Pedido: _{tema}_{aviso}\n\n"
                f"O agente confirma o que entendeu e eu aviso quando a fita ficar pronta.")

    return f"Comando desconhecido.\n\n{AJUDA}"
