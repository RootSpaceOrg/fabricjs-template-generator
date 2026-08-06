# Judge — gram-teste-1

Rejulgamento QA do render vigente após o swap de `strip.png` (2026-08-06), contra `clinical-photo-editorial/reference.png`.

## Regras duras (R1–R6)

| Regra | Veredito | Evidência verificável |
|---|---|---|
| R1 avatar | ok | Slides 1 e 6 usam `professionalPhoto`; a procedência é o placeholder canônico `professional-photo-1.png` no `fita.html`. |
| R2 corte | ok | Slides 1–6: nenhum texto de leitura ou slot editável cruza a borda do canvas. |
| R3 fundos | ok | Paper nos slides 1, 2 e 4–6; fundo accent no slide 3 — há mudança real de fundo. |
| R4 área morta | ok | Slides 1–6 têm âncora dominante: dupla texto/foto, quote-card, mecanismo, bullets, fecho e CTA/foto. |
| R5 UI-decor | ok | Slides 1 e 6 usam stamps/CTA editoriais; não há pill, toggle ou botão ornamental simulando interface. |
| R6 contraste | ok | Teal sobre paper (1, 4–6), texto claro sobre accent (3) e card sobre overlay (2) seguem legíveis. |

## QA do pack

- Capa (S1) preserva display duo-tom entrelaçado ao slot profissional, com bokeh de ponteira PBM em borda limpa.
- S2 é o único full-bleed + overlay + card alert; o card respira e não tem texto cortado.
- A foto paisagem vigente atravessa S4|S5 pela `.fita-layer` de modo equilibrado, em rodapé limpo e sem cobrir texto.
- Decors PBM continuam específicos da run, transparentes e com bokeh profundo; nenhum toca CTA, logo ou `professionalPhoto`.
- S6 fecha com `professionalPhoto`, espelhando a abertura.

## QA narrativo — CONTEXT.md §3b + gramática LaserPro

- **Gancho com tensão:** S1 nomeia a insegurança concreta de sair da sessão pensando “será que era isso?”, não anuncia uma pauta.
- **Progressão sem redundância:** S2 desmonta o clichê/culpa; S3 traduz o mecanismo; S4 apresenta possibilidades modais; S5 devolve clareza; S6 converte o guia em comentário/salvamento.
- **Mecanismo:** S3 traduz “luz não ionizante” para “luz que não altera o DNA”; não há imperativo clínico sem contexto.
- **Especificidade:** PBM, parâmetros e protocolo individual vinculam a peça à fotobiomodulação clínica.
- **CTA conectado:** S6 pede comentário e salvamento para retomar a conversa antes da próxima sessão — continuação direta da clareza prometida no fecho.

**QA: PASS**
