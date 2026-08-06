# Judge — var-teste-1

QA do render vigente (`strip.png`, 2026-08-05).

## Regras duras (R1–R6)

| Regra | Veredito | Evidência |
|---|---|---|
| R1 avatar | ok | slide 1 usa o placeholder canônico `professionalPhoto` do runtime. |
| R2 corte | ok | Nenhum texto de leitura atravessa fronteira ou canvas. |
| R3 fundos | ok | Papel menta nos slides 1–6 e fundo accent no fechamento. |
| R4 área morta | ok | O respiro aponta para headline, número ou foto contínua; não há slide sem âncora intencional. |
| R5 UI-decor | ok | Pills são stamp/CTA funcionais, não decoração de UI. |
| R6 contraste | ok | Teal sobre paper e branco sobre accent permanecem legíveis. |

## QA do pack

- Capa: duo-tom display entrelaçado com slot profissional; decor de aparelho gerado para esta run.
- Miolo: foto paisagem única cruza a fronteira 3|4 pela `fita-layer`; não encobre copy.
- Decors: bokeh transparente, específico de laserterapia, colado às bordas e distante de CTA/foto profissional.
- Copy: educativa, sem promessa de resultado e com CTA de meio de funil.

**QA: PASS**
