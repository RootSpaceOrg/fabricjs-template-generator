---
name: template-factory
description: "Cria templates finais específicos de negócio (business_type da plataforma: laserterapia, dentista, nutricionista, etc.) publicados como template_type=userReady, via fábrica de templates: motor sem estética (design system fechado + conversor determinístico) + packs de design certificados. Use quando o usuário pedir 'template para <negócio>', 'template específico de <nicho>', 'carrossel de <tema> para <business_type>', ou mencionar a fábrica/pack."
---

# template-factory

Toda a fábrica vive na raiz do repo — este arquivo é só o gatilho.

1. Leia [`README.md`](../../README.md) (fluxo da run) e siga o runner: `python engine/run.py new <slug> --env dev --pack <pack certificado>`.
2. Doutrinas por estágio: [`CONTEXT.md`](../../CONTEXT.md) (copy specialist; + `knowledge/copy/negocios/<business>.md`) · [`engine/CATALOG.md`](../../engine/CATALOG.md) (designer: fita.html única — você NUNCA escreve CSS; + `knowledge/design/geral.md` + `packs/<pack>/tecnicas.md`) · [`JUDGE.md`](../../JUDGE.md) (QA) · [`PACKS.md`](../../PACKS.md) (criar/certificar packs).
   Variância é dever: gerações do mesmo pack nunca repetem o esqueleto (exemplos são partida, não fôrma).
3. Defaults: tenant `kultivai`, vertical `health`, ambiente **dev**. Packs disponíveis: `packs/` (só `status: certificado` gera produção).
4. Loop de qualidade: o criador de packs (Claude) revisa cada fita renderizada ANTES do Gustavo — devolve críticas (arco narrativo, hierarquia, contraste, leis do pack) e você REGENERA a fita; só sobe para o Gustavo o que passou nessa peneira.
5. Leis: advance aceito = próximo estágio imediatamente; JSON nunca se edita (rejeição → regenera HTML); conhecimento commitado via git (pull no início, push de dossiês/lessons ao final); env imutável; aprovação final é do Gustavo. Lições: `evals/lessons.md` (globais) + `packs/<pack>/lessons.md`.
