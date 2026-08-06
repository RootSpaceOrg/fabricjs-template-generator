# Judge — var-teste-2

QA do render vigente (`strip.png`, 2026-08-05).

## Regras duras (R1–R6)

| Regra | Veredito | Evidência |
|---|---|---|
| R1 avatar | ok | Slide 1 usa o placeholder canônico `professionalPhoto`. |
| R2 corte | ok | Nenhum texto de leitura é cortado por canvas ou fronteira. |
| R3 fundos | ok | Paper nos slides 1 e 3–6; accent no slide 2. |
| R4 área morta | ok | Respiro orientado por headline, foto contínua e CTA. |
| R5 UI-decor | ok | Pills são stamp e CTA funcionais. |
| R6 contraste | ok | Copy teal no paper e branca no accent permanece legível. |

## QA do pack

- Os decors de óculos agora têm transparência limpa, sem fundo de chroma-key visível (slides 1 e 6).
- Foto paisagem nova cruza a fronteira 2|3 via `.fita-layer`, sem encobrir texto.
- A estrutura difere da var-teste-1: 6 slides, capa espelhada, ordem de miolo distinta, foto contínua na abertura do miolo e fechamento em paper.
- Copy educativa e CTA de meio de funil permanecem dentro do recorte de depilação a laser e do compliance.

**QA: PASS**
