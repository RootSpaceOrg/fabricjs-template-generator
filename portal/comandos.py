#!/usr/bin/env python3
"""Comandos de chat da fábrica — fechados, sem interpretação livre.

Usados pelo bot do portal (Telegram). Mesma lista serve de referência para o
agente do OpenClaw responder aos mesmos comandos.
"""
from __future__ import annotations

import re
from pathlib import Path

import knowledge as kb
from jobs import RUNS, enfileirar

AJUDA = (
    "*Fábrica — comandos*\n"
    "`/nova <pack> <tema>` — cria a run; o agente escreve o dossiê e compõe a fita\n"
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


def prompt_nova(slug: str, pack: str, tema: str) -> str:
    return (
        f"NOVA RUN pedida pelo Gustavo no Telegram (fabrica; git pull --rebase antes). "
        f"Leia README.md, CONTEXT.md, engine/CATALOG.md, knowledge/copy/frameworks.md, "
        f"knowledge/copy/negocios/ (o dossie do negocio do tema), knowledge/design/geral.md e "
        f"packs/{pack}/tecnicas.md + images.md + lessons.md.\n\n"
        f"Comando inicial: python3 engine/run.py new {slug} --env dev --pack {pack} "
        f"--n <numero de slides que o tema pedir, dentro do range do pack>.\n"
        f"TEMA: {tema}\n\n"
        f"VOCE e o copy specialist E o designer desta run:\n"
        f"1. resolve (engine/tools/resolve_tenant.py) e context: dossie.md declarando OBJETIVO, "
        f"FRAMEWORK (knowledge/copy/frameworks.md), ARCO (gramatica do acervo) e o open loop de cada slide;\n"
        f"2. gere as imagens do tema (fotos e colagens/decors) com sua ferramenta de imagem, "
        f"seguindo images.md do pack;\n"
        f"3. compose: UM fita.html seguindo o CATALOG e as tecnicas do pack (miolo com objeto de "
        f"conteudo, hierarquia, contraste pelo fundo da caixa, CTA so onde ha acao);\n"
        f"4. rode 'node engine/assemble.js artifacts/runs/{slug}' e PARE ai.\n\n"
        f"O corredor (convert/judge) e a revisao vem depois. Reporte o caminho do strip.png."
    )


def executar(texto: str) -> str:
    """Interpreta um comando e devolve a resposta em Markdown."""
    cmd, _, resto = texto.partition(" ")
    cmd, resto = cmd.lower().lstrip("/").split("@")[0], resto.strip()

    if cmd in ("ajuda", "help", "start"):
        return AJUDA

    if cmd == "packs":
        linhas = [
            f"{'✅' if p['status'] == 'certificado' else '🟡'} `{p['slug']}`\n   {p['familia'][:70]}"
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
        pack, _, tema = resto.partition(" ")
        tema = tema.strip()
        certificados = {p["slug"] for p in kb.packs() if p["status"] == "certificado"}
        if not pack or not tema:
            return "Use `/nova <pack> <tema>`\nEx.: `/nova bold-educacional laser dói? o mito`"
        if pack not in certificados:
            disp = ", ".join(f"`{s}`" for s in sorted(certificados)) or "nenhum"
            return f"`{pack}` não é um pack certificado.\nDisponíveis: {disp}"
        slug = slug_novo(pack, tema)
        enfileirar("agente", slug, prompt_nova(slug, pack, tema))
        return (f"Run `{slug}` enfileirada — pack `{pack}`.\n"
                f"Tema: _{tema}_\n\nAviso aqui quando a fita estiver pronta.")

    return f"Comando desconhecido.\n\n{AJUDA}"
