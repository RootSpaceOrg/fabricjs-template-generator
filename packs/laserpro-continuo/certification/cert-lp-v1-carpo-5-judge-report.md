# Judge — cert-lp-v1-carpo-5

Golden set: 7 exemplares HTML do pack `laserpro-continuo` usados (`ref-estrutura`, `ref-sintomas-travessia`, `ref-beneficios-cartao`, `ref-faixa-de-foto`, `ref-capa-e-fechamento`, `ref-destaque-na-marca`, `ref-cartao-na-marca`). Avaliação do render vigente: `strip.png` e `slide-1.png` a `slide-5.png`.

## Regras duras (R1–R13)

| Candidato | R1 avatar | R2 corte | R3 monocromia | R4 área morta | R5 UI-decor | R6 contraste | R7 bloco partido | R8 margem | R9 emenda | R10 img sem função | R11 cutout | R12 camadas | R13 emenda |
|-----------|-----------|----------|---------------|---------------|------------|--------------|------------------|-----------|-----------|-------------------|------------|-------------|------------|
| A | ok — placeholders canônicos em S1/S5 | ok — copy dentro do canvas | ok — acento→branco | ok — todos os terços têm leitura, recorte, faixa ou marca | ok — CTA só em S1/S5 | ok — claro no acento, ink/acento no branco | ok — tese+apoio contíguos | ok — textos respeitam o inset | ok — recorte retrato é travessia real S2→S3 | ok — dedos em garra e punho explicam o sintoma; S4 mostra o recurso citado | ok — slots S1/S5 chegam à base | ok — watermarks ficam atrás e variam por trecho | ok — uma única PNG RGBA retrato liga S2 e S3 |

Eliminados: nenhum.

## QA de narrativa e registro

- O gancho de S1 usa custo concreto (dormência noturna recorrente) em vez de anunciar o tema; S2 nomeia os sinais, S3 traduz o nervo mediano, S4 delimita a técnica e S5 pede uma ação coerente com a informação recebida.
- A imagem do problema vem antes do aparelho. O único aparelho aparece em S4, como faixa clínica com o formato correto: corpo branco curvo sem fio, haste com esfera, display e pedestal; não há caneta com cabo, depilação ou efeito sci-fi.
- O recorte do punho é PNG RGBA retrato (1024×1536), com dedos em garra, punho marcado e antebraço vertical; está centralizado para a travessia S2→S3 e alcança a borda de baixo. A foto de faixa não sangra as laterais.
- `PUNHO` é o par acento/claro na emenda de fundos diferentes S1→S2; os demais watermarks atravessam somente trechos de fundo branco com `data-ghost` simples. Não há slide de destaque inteiro em cor de marca além da capa obrigatória.
- Copy específica: punho, nervo mediano, túnel do carpo e parâmetros de fotobiomodulação complementar; sem diagnóstico, promessa ou número de sessões.

QA: PASS
