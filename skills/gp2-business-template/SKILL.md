---
name: gp2-business-template
description: "Cria templates finais específicos de negócio (business_type da plataforma: laserterapia, dentista, nutricionista, etc.) publicados como template_type=userReady, via fábrica gp3: motor sem estética (design system fechado + conversor determinístico) + packs de design certificados. Use quando o usuário pedir 'template para <negócio>', 'template específico de <nicho>', 'carrossel de <tema> para <business_type>', ou mencionar gp3/pack. NÃO use para catálogo genérico multi-nicho (isso é gp2-template-suggester)."
---

# gp2-business-template → fábrica gp3

Toda a fábrica vive em [`gp3/`](../../gp3/README.md) — este arquivo é só o gatilho.

1. Leia [`gp3/README.md`](../../gp3/README.md) (fluxo da run) e siga o runner: `python gp3/engine/run.py new <slug> --env dev --pack <pack certificado>`.
2. Doutrinas por estágio: [`gp3/CONTEXT.md`](../../gp3/CONTEXT.md) (dossiê/funil/espinha) · [`gp3/engine/CATALOG.md`](../../gp3/engine/CATALOG.md) (componentes — você NUNCA escreve CSS) · [`gp3/JUDGE.md`](../../gp3/JUDGE.md) (QA) · [`gp3/PACKS.md`](../../gp3/PACKS.md) (criar/certificar packs).
3. Defaults: tenant `kultivai`, vertical `health`, ambiente **dev**. Packs disponíveis: `gp3/packs/` (só `status: certificado` gera produção).
4. Leis: advance aceito = próximo estágio imediatamente; JSON nunca se edita (rejeição → regenera HTML); conhecimento commitado via git (pull no início, push de dossiês/lessons ao final); env imutável; aprovação final é do Gustavo.

O fluxo bt/ foi aposentado em 2026-08-04 — histórico no git e lições em `gp3/evals/lessons.md`.
