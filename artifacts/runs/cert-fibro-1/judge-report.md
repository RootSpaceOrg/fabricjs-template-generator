# Judge — cert-fibro-1

Rejulgamento QA do render vigente após as correções de decor e composição de S5 (2026-08-06), contra `clinical-photo-editorial/reference.png` e `exemplos/fita-aprovada-gram-teste-1.png`.

## Regras duras (R1–R6)

| Regra | Veredito | Evidência verificável |
|---|---|---|
| R1 avatar | ok | S1 e S6 usam o slot `professionalPhoto` de procedência canônica no `fita.html`. |
| R2 corte | ok | S1–S6: nenhum texto de leitura, CTA ou slot editável é cortado pela fronteira/canvas. |
| R3 fundos | ok | Paper em S1 e S4–S6, foto full-bleed em S2 e fundo accent em S3 asseguram mudanças reais de fundo. |
| R4 área morta | ok | S5 foi reancorado: bokeh de luz no canto inferior, selo editorial e copy distribuem peso visual sem criar ruído; não há bloco morto dominante. |
| R5 UI-decor | ok | Stamps e CTA têm papel editorial explícito; não há pill/toggle/botão ornamental simulando interface. |
| R6 contraste | ok | Teal sobre paper (S1, S4–S6), texto claro sobre accent (S3) e card de S2 sobre overlay permanecem legíveis. |

## QA do pack e imagens

- S1 mantém a assinatura de headline duo-tom entrelaçada ao `professionalPhoto`; S2 é o único full-bleed + overlay + card alert; S3|S4 preserva a travessia paisagem equilibrada; S6 fecha com `professionalPhoto`.
- A travessia S3|S4 passa no rodapé de fundo limpo e não encobre copy, CTA ou slot profissional.
- O decor de S5 foi reemitido sem halo magenta: o bokeh está restrito ao registro teal/paper, é específico de PBM e o novo bokeh inferior ancora o fecho sem se sobrepor à copy.

## QA narrativo — CONTEXT.md §3b + gramática LaserPro

- **Gancho com tensão:** S1 usa a frase ouvida “nem parece doente” para nomear o custo concreto de uma dor invisível; não é anúncio de pauta.
- **Arco sem redundância:** S2 acolhe e desculpabiliza; S3 traduz a amplificação dos sinais de dor; S4 posiciona PBM como complemento individual sem disputar o cuidado clínico; S5 devolve pertencimento; S6 convida a continuidade.
- **Mecanismo e compliance:** S3 dá o porquê em linguagem acessível; S4 mantém acompanhamento clínico como essencial e usa “pode ser conversada” para a PBM, sem prometer resultado.
- **Especificidade:** fibromialgia, sistema nervoso, dor invisível, fotobiomodulação e parâmetros tornam a copy exclusiva do recorte.
- **CTA conectado:** “EU ME VEJO” e o salvamento são consequência direta da validação e da mensagem de pertencimento entregues na fita.

**QA: PASS**
