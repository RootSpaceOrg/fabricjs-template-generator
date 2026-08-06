# Judge — setembro-amarelo

QA do render vigente (`strip.png`, 2026-08-06) contra `packs/emotive-fullbleed-lettering/reference.png`.

## Regras duras (R1–R6)

| Regra | Veredito | Evidência verificável |
|---|---|---|
| R1 avatar | ok | Não há slot de pessoa/avatar; as duas adultas estão na foto editorial de fundo. O único slot é `logo`. |
| R2 corte | ok | S1 mantém lettering, copy, data, contatos e logo integralmente dentro do canvas. |
| R3 fundos | n/a | Peça única: alternância de fundos não se aplica. O overlay faz a transição foto→primary. |
| R4 área morta | ok | Cena de conversa, lettering, informação da campanha, mensagem e rodapé equilibram a área visual. |
| R5 UI-decor | ok | Ribbon e sparkles são ornamentos da campanha; não há UI simulada. |
| R6 contraste | ok | Texto claro e lettering amarelo/cobre se mantêm legíveis na primary azul profunda. |

## QA do pack e narrativa

- Os rostos e o gesto de mão no ombro ficam inteiramente livres de sparkle, lettering e overlay denso; a conversa acolhedora é o foco humano.
- “SETEMBRO amarelo” é legível; fita amarela inteira no O e sparkles discretos reforçam a campanha sem poluir a foto.
- Gradiente funde o banco/foto à primary sem degrau visível. Logo com `data-inset="bottom"` e contatos laterais têm respiro adequado.
- A copy convoca escuta, cuidado e presença em tom acolhedor, sem oferta, promessa de resultado clínico, imperativo sem contexto ou redundância. Em peça única de conscientização, a campanha é o recorte específico.

**QA: PASS**
