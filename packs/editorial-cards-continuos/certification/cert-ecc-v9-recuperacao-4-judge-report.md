# Judge — cert-ecc-v9-recuperacao-4

Modo: QA de pack certificado · referência: `packs/editorial-cards-continuos/reference.png` e 4 exemplares do pack.

## Regras duras (R1–R13)

| Candidato | R1 avatar | R2 corte | R3 monocromia | R4 área morta | R5 UI-decor | R6 contraste | R7 bloco partido | R8 margem | R9 emenda | R10 img sem função | R11 cutout | R12 camadas | R13 emenda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Único | ok — sem slots | ok — S1–S4 | ok — foto/creme/primary/creme | ok — cartões carregam número, tese e apoio | ok — pills apenas em ações | ok — S1–S4 | ok — apoio segue a tese em S2–S4 | ok | ok — cartões são travessias da fita-layer | ok — uma foto de capa com função | ok — sem cutout | ok | ok — transição cartão creme→primary intencional |

## QA narrativo e visual

- Gancho (S1) tem tensão concreta: usar dor como placar pode custar o próximo treino; a foto mostra exatamente o pós-série, sem equipamento de PBM ou cena genérica.
- A sequência não é redundante: S2 nomeia o ciclo de carga irregular; S3 traduz o efeito da sessão repetida; S4 transforma a tese em ação prudente.
- A especificidade vem do mecanismo “o corpo reconhece a mesma carga”, não de uma lista genérica de autocuidado. Não há promessa de recuperação, desempenho, prazo ou tratamento.
- A primary `#2E5FA3` aparece somente em elementos declarados variáveis: elipse da capa, número do cartão claro, cartão de S3 e CTAs. O número do cartão azul é `paper` para contraste.
- Render e conversão revisados: nenhum texto truncado, nenhuma colisão, nenhuma imagem repetida, logo ou `professionalPhoto`.

QA: PASS
