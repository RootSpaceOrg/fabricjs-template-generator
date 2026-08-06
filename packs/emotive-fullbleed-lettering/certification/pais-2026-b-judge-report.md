# Judge — pais-2026-b

QA do render vigente (`strip.png`, 2026-08-06) contra `packs/emotive-fullbleed-lettering/reference.png`.

## Regras duras (R1–R6)

| Regra | Veredito | Evidência verificável |
|---|---|---|
| R1 avatar | ok | Não há slot de pessoa/avatar; pai e filho pertencem à foto editorial de fundo. O único slot é `logo`. |
| R2 corte | ok | Copy, data, contatos e logo de S1 ficam inteiros no canvas; lettering e gravata são decor estático e não cortam leitura. |
| R3 fundos | n/a | Peça única: alternância de fundos não se aplica. Há fusão progressiva foto→primary. |
| R4 área morta | ok | Foto emocional, lettering, data, homenagem e rodapé institucional ocupam a peça sem bloco morto dominante. |
| R5 UI-decor | ok | Lettering 3D e gravata são ornamentação temática, sem simular UI. |
| R6 contraste | ok | Data, copy e contatos claros são legíveis na primary azul; lettering cream/cobre preserva contraste no gradiente. |

## QA do pack e narrativa

- Rostos naturais de pai e filho continuam completamente livres; o lettering começa abaixo da zona emocional e não disputa a cena.
- “FELIZ DIA PAIS” e “paizão” são legíveis, com gravata azul marinho inteira e semanticamente ligada ao tema; a transição da foto para a cor é gradual, sem faixa dura.
- Logo central inferior tem `data-inset="bottom"`, com contatos em zonas laterais e respiro suficiente da borda.
- A homenagem é curta, específica ao Dia dos Pais, sem promessa/alegação clínica e sem redundância. Não há imperativos soltos nem CTA desconectado em peça comemorativa única.

**QA: PASS**
