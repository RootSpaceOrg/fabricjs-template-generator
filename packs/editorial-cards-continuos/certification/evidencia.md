# Certificação — editorial-cards-continuos v1

Data: 2026-08-13 · Protocolo: PACKS.md §4 · Ambiente: dev
**Aprovado pelo Gustavo em 2026-08-13.** Commit do pack: `7410a05`

## As 3 fitas da prova

| Run | Slides | Primary de teste | Gates | Judge |
|-----|--------|------------------|-------|-------|
| cert-ecc-v9-recuperacao-4 | 4 | `#2E5FA3` azul | 0 rejeições | QA: PASS |
| cert-ecc-v9-recuperacao-5 | 5 | `#7B3FA0` roxo | 0 rejeições | QA: PASS |
| cert-ecc-v9-postura-7 | 7 | `#1F7A5C` verde | 0 rejeições | QA: PASS |

As duas primeiras são do MESMO tema (prova de variância); a de 7 é tema
diferente. Cada fita renderizada com uma marca distinta — o pack é
`adaptavel: true`, então o número e a elipse acompanham a cor, e o número
sobre o cartão de acento permanece claro por contraste.

## O que esta certificação prova

- **Fidelidade ao estilo**: cartões atravessando as emendas, número em faixa
  exclusiva no canto superior esquerdo, altura uniforme (linhas 2–12).
- **Adaptabilidade**: três marcas, com os elementos de acento acompanhando.
- **Fôlego em fita longa**: a de 7 slides não cai em texto solto — todos os
  miolos passam o piso de 30% de densidade.
- **Oito gates mecânicos**, todos verdes nas três fitas.

## Os gates que este pack fez nascer

Cada um veio de um defeito que passou por revisão humana e voltou:

| Gate | O defeito que o originou |
|---|---|
| altura única de cartão | cartão com foto ganhava uma linha extra e batia na base do slide |
| folga de borda (24px) | a seta encostava no canto; a margem direita era comida pela sangria |
| folga entre irmãos (12px) | número sobre foto, número sobre headline, headline sobre apoio |
| área mínima de foto (30%) | imagem em faixa fina virava enfeite, não dizia o assunto |
| imagem não repetida | a foto da capa reaparecia no miolo |
| slot não declarado | logo e professionalPhoto inseridos por hábito, comendo o gap |
| grid dentro das 12 linhas | `row-end` 14 jogava o elemento para fora do slide |
| transbordo de texto (48px) | "SESSÃO NÃO BASTA" saía cortado, e passava em todos os outros |

## Ressalvas registradas

**As três fitas usam só o registro de TEXTO.** Cada run gerou uma imagem — a da
capa. Os outros três registros (foto no topo, foto no rodapé, foto em retrato)
seguem verificados pelos exemplares em `exemplos/`, mas nenhuma fita de prova os
exercitou de ponta a ponta. Se um defeito existir só nesse caminho, esta
certificação não o pegaria.

**Copy repetida entre as fitas de 4 e 5 slides.** "REPETIÇÃO ENSINA O CORPO" e
"TREINE PARA VOLTAR" aparecem nas duas. Elas são do mesmo tema por desenho — a
prova de variância pede esqueletos diferentes, e isso foi cumprido —, mas a tese
repetida enfraquece o argumento.

Ambas foram apresentadas ao Gustavo antes da aprovação.
