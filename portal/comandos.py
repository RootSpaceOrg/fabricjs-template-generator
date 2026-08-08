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


def _cabeca(slug: str, pedido: str, tema: str, tenant: str, vertical: str,
            env: str, business: str, n: str, pack: str | None) -> str:
    """Contexto comum a todas as fatias."""
    return (
        f"Run {slug} da fabrica (git pull --rebase antes).\n"
        f'PEDIDO DO GUSTAVO: "{pedido or tema}"\n'
        f"CONTEXTO (ja definido - use, nao pergunte): tenant={tenant} - vertical={vertical} - "
        f"env={env}"
        f"{' - business_type=' + business if business else ' - business_type: infira do tema'}"
        f"{' - slides=' + n if n else ''}"
        f"{' - pack=' + pack if pack else ' - pack: ESCOLHA VOCE'}\n"
        f"TEMA: {tema}\n\n"
    )


def fatias_nova(slug: str, pack: str | None, tema: str, pedido: str = "",
                tenant: str = "kultivai", vertical: str = "health",
                env: str = "dev", business: str = "", n: str = "") -> list[str]:
    """A criacao vira 6 turnos curtos - a janela do agente nao aguenta tudo junto.

    dossie / imagens / abertura / miolo / fechamento+render / judge ate PASS.
    Compor a fita inteira nao cabia numa janela: por isso ela vem em 3 pedacos.
    Cada fatia comeca relendo o estado do disco, entao e retomavel.
    """
    ctx = _cabeca(slug, pedido, tema, tenant, vertical, env, business, n, pack)
    escolha = ("" if pack else
               "Antes de tudo ESCOLHA o pack: compare packs/*/pack.json (certificados; olhe "
               "fit.melhor_em e assinaturas) com o tema e justifique em 1 linha no dossie. "
               "O fit e CONSELHO, nao regra - nao bloqueie a run por causa dele.\n")
    pk = pack or "<o pack escolhido>"

    f1 = (ctx + escolha +
          f"FATIA 1 de 6 - SO O DOSSIE. Nao componha, nao gere imagem.\n"
          f"1. python3 engine/run.py new {slug} --env {env} --pack {pk} "
          f"--n {n or '<dentro do range do pack>'} (se a run ja existir, siga);\n"
          f"2. resolve: python3 engine/tools/resolve_tenant.py --tenant {tenant} "
          f"--vertical {vertical} --env {env}"
          f"{' --subject ' + business if business else ' --subject <nicho do tema>'}"
          f" > artifacts/runs/{slug}/resolve.json;\n"
          f"3. escreva artifacts/runs/{slug}/dossie.md com OBJETIVO, FRAMEWORK "
          f"(knowledge/copy/frameworks.md), ARCO (gramatica em knowledge/copy/negocios/), "
          f"open loop por slide e a copy final de cada slide (CONTEXT.md 3b);\n"
          f"4. advance ate 'compose' e PARE. Responda em 3 linhas.")

    f2 = (ctx +
          f"FATIA 2 de 6 - SO AS IMAGENS. O dossie ja existe (leia-o).\n"
          f"Gere em artifacts/runs/{slug}/assets/ as fotos e colagens/decors que a fita vai usar, "
          f"seguindo packs/{pk}/images.md (foto de miolo pensada para receber cartao; decor "
          f"transparente com blur na geracao; NUNCA gere pessoa para o slot professionalPhoto - "
          f"esse slot usa o placeholder canonico do motor). Liste os arquivos e PARE.")

    regras = (f"Siga engine/CATALOG.md, packs/{pk}/tecnicas.md (ANATOMIA POR TIPO DE SLIDE: "
              f"nenhum slide e so texto - minimo 2 elementos com peso) e "
              f"knowledge/design/geral.md. PROIBIDO copiar/adaptar fita.html de outra run - "
              f"olhar exemplo do pack e permitido, copiar nao.\n")

    f3a = (ctx + regras +
           f"FATIA 3 de 6 - SO A ABERTURA. Dossie e assets ja existem (leia dossie.md, "
           f"liste assets/).\n"
           f"Crie artifacts/runs/{slug}/fita.html com o esqueleto (head + main.fita) e "
           f"APENAS a <section data-role=\"abertura\">. Nao escreva os outros slides ainda. "
           f"Nao rode assemble. Responda em 2 linhas.")

    f3b = (ctx + regras +
           f"FATIA 4 de 6 - SO O MIOLO. O fita.html ja existe com a abertura (leia-o).\n"
           f"Acrescente as <section data-role=\"item\"> do miolo conforme o dossie "
           f"(a fita tem {n or 'o total definido em run.json'} slides no total, contando "
           f"abertura e fechamento). VARIE o tratamento entre elas (foto, chapado, card sobre "
           f"foto, lista) - nao repita o mesmo esqueleto. Nao rode assemble. Responda em 2 linhas.")

    f3c = (ctx + regras +
           f"FATIA 5 de 6 - FECHAMENTO E RENDER. O fita.html ja tem abertura e miolo (leia-o).\n"
           f"1. acrescente a <section data-role=\"fechamento\"> (espelha a abertura: "
           f"professionalPhoto + CTA + logo);\n"
           f"2. rode 'node engine/assemble.js artifacts/runs/{slug}';\n"
           f"3. responda so com o caminho do strip.png.")

    f4 = (ctx +
          f"FATIA 6 de 6 - CORREDOR E JUDGE ATE PASSAR.\n"
          f"FATIA 4 de 4 - CORREDOR E JUDGE ATE PASSAR.\n"
          f"1. 'node engine/convert.js artifacts/runs/{slug} artifacts/runs/{slug}/output "
          f"--slug {slug}' - rejeicao = corrija o HTML e repita (nunca edite JSON);\n"
          f"2. avance ate judge e julgue (JUDGE.md modo QA + check narrativo);\n"
          f"3. FAIL = corrija o fita.html, re-renderize, reconverta e RE-JULGUE (max 3 voltas);\n"
          f"4. PARE no judge com PASS - nao escreva fidelity nem publique (isso e do Gustavo).\n"
          f"Reporte o veredito e quantas voltas precisou.")

    return [f1, f2, f3a, f3b, f3c, f4]


def prompt_nova(slug: str, pack: str | None, tema: str, pedido: str = "",
                tenant: str = "kultivai", vertical: str = "health",
                env: str = "dev", business: str = "", n: str = "") -> str:
    """Compat: primeira fatia (o encadeamento é feito por quem enfileira)."""
    return fatias_nova(slug, pack, tema, pedido, tenant, vertical, env, business, n)[0]


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
        pai = None
        for fatia in fatias_nova(slug, pack, tema, pedido=resto, business="laserterapy"):
            pai = enfileirar("agente", slug, fatia, pai=pai)
        aviso = ("\n\n⚠️ Você mencionou *prod*: a run vai para dev; publicar em produção "
                 "exige confirmação separada.") if re.search(r"\bprod", resto, re.I) else ""
        quem = f"pack `{pack}`" if pack else "_pack a escolher pelo agente_"
        return (f"Run `{slug}` enfileirada — {quem}, ambiente dev.\n"
                f"Pedido: _{tema}_{aviso}\n\n"
                f"O agente confirma o que entendeu e eu aviso quando a fita ficar pronta.")

    return f"Comando desconhecido.\n\n{AJUDA}"
