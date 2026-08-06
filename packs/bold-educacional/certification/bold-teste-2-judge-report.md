# Judge — bold-teste-2

QA: PASS

Golden set: `packs/bold-educacional/reference.png` + `packs/bold-educacional/exemplos/ref-capa-meme-2.png` e `ref-statement.png`.

## Regras duras (R1–R6)

| Regra | Resultado | Evidência |
|---|---|---|
| R1 avatar | ok | Não há slot `professionalPhoto`; o único elemento pessoal é o logo canônico no S3. |
| R2 corte | ok | Copy, CTA e logo inteiros em S1–S3. |
| R3 monocromia | ok | S1 foto menta, S2 paper e S3 vermelho primário. |
| R4 área morta | ok | O respiro do S2 estrutura o mecanismo e é ancorado pela polaroid; nenhum slide excede área morta material. |
| R5 UI-decor | ok | Tarjas são elementos de leitura/CTA do pack, não imitação de UI. |
| R6 contraste | ok | Preto sobre menta/paper e cream sobre vermelho estão legíveis. |

## Check narrativo e de registro

- S1 abre com tensão específica (o mito de que laser queima), em headline sentence-case legível e uma única tarja concreta.
- S2 destrava a crença pelo mecanismo: baixa intensidade, efeito celular e não térmico; a polaroid está inteira, sem cobrir copy.
- S3 fecha a consequência para a consulta e CTA útil para salvar, com logo respirando e sem sobreposição.
- Golden retriever com óculos e prancheta é meme fotográfico, digno e coerente com o tema; não há cartoon ou deformação.
- A alternância foto → paper → chapado segue o pack e não há overflow nos slots.
