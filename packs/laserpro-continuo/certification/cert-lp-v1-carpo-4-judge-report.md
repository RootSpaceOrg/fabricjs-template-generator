# Judge — cert-lp-v1-carpo-4

Golden set: 7 exemplares HTML do pack `laserpro-continuo` usados (`ref-estrutura`, `ref-sintomas-travessia`, `ref-beneficios-cartao`, `ref-faixa-de-foto`, `ref-capa-e-fechamento`, `ref-destaque-na-marca`, `ref-cartao-na-marca`). Avaliação do render vigente: `strip.png` e `slide-1.png` a `slide-4.png`.

## Regras duras (R1–R13)

| Candidato | R1 avatar | R2 corte | R3 monocromia | R4 área morta | R5 UI-decor | R6 contraste | R7 bloco partido | R8 margem | R9 emenda | R10 img sem função | R11 cutout | R12 camadas | R13 emenda |
|-----------|-----------|----------|---------------|---------------|-------------|--------------|------------------|-----------|-----------|-------------------|------------|-------------|------------|
| A | ok — `professional-photo-1.png` canônico em S1/S4 | ok | ok — fundos acento→branco→branco→branco | ok — cada terço tem texto, pessoa ou watermark | ok — pills só S1 arrasta e S4 CTA | ok — branco no acento; ink no miolo branco | ok — tese+apoio seguem contíguos | ok | ok — a PNG RGBA retrato é a mesma travessia S2→S3 | ok — mãos e punhos carregam os sintomas | ok — S1/S4 terminam na linha 13 | ok — palavras-fantasma ficam atrás, sem cortar copy | ok — S2/S3 são o mesmo arquivo na `.fita-layer` |

Eliminados: nenhum.

## QA de narrativa e registro

- Gancho com tensão: S1 começa pelo sintoma noturno e desmonta a explicação automática de “má circulação”; não anuncia apenas o tema.
- Progressão sem redundância: S2 reconhece sinais, S3 traduz o mecanismo do nervo mediano, S4 move para avaliação e recurso complementar.
- Especificidade: punho, nervo mediano, compressão e fotobiomodulação complementar impedem que a copy sirva para qualquer dor.
- Imagem: o único asset gerado mostra apenas mãos e antebraços, com o punho marcado antes da técnica; é PNG RGBA retrato, sujeito central e sangra na base. Não há pessoa inteira, aparelho errado nem capa com equipamento.
- Continuidade: `PUNHO` usa par acento/claro ao cruzar S1→S2; `SINTOMAS` permanece sobre o miolo branco em S3→S4. A travessia de punho conecta S2→S3 sobre branco contínuo, sem simular uma foto editável cortada.

QA: PASS
