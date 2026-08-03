---
name: gp2-business-template
description: "Cria UM template final, específico de negócio (business_type da plataforma: laserterapia, dentista, nutricionista, etc.) a partir de uma ideia em linguagem natural, publicado como template_type=userReady. Pipeline best-of-N: dossiê pesquisado por nicho, storyline de funil (topo/meio/fundo), 3 candidatos de design em paralelo com composição autoral, juiz independente com rubrica, imagens geradas por IA sem placeholder. Use quando o usuário pedir 'template para <negócio>', 'template específico de <nicho>', 'carrossel de <tema> para <business_type>', ou mencionar bt-pipeline. NÃO use para catálogo genérico multi-nicho (isso é gp2-template-suggester)."
---

# gp2-business-template

Toda a pipeline vive em [`bt/`](../../bt/README.md) — este arquivo é só o gatilho.

1. Leia [`bt/PIPELINE.md`](../../bt/PIPELINE.md) e siga-o como orquestrador.
2. Os estágios que ele delega: [`bt/CONTEXT.md`](../../bt/CONTEXT.md) (dossiê + funil + storyline), [`bt/DESIGN.md`](../../bt/DESIGN.md) (candidatos em paralelo), [`bt/JUDGE.md`](../../bt/JUDGE.md) (julgamento em contexto limpo), [`bt/FINALIZE.md`](../../bt/FINALIZE.md) (imagens, marcação, conversão, upload).
3. Defaults: tenant `kultivai`, vertical `health`, ambiente **dev**. Dois modos: **estilo certificado** (`bt/styles/`, N=1 + judge QA — default quando houver estilo com fit) e **livre** (best-of-N=3 + judge pairwise — laboratório e pedidos fora do catálogo).

Regras que nunca mudam: `status review` (humano aprova), business_type sempre validado pelo `bt/scripts/resolve_tenant.py`, judge nunca é pulado, mudança em `bt/` roda a regressão de `bt/evals/` antes de produção.
