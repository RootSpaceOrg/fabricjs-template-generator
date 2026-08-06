# Judge — cert-fibro-1

QA do render vigente (`strip.png`, 2026-08-06) contra `clinical-photo-editorial/reference.png` e `exemplos/fita-aprovada-gram-teste-1.png`.

## Regras duras (R1–R6)

| Regra | Veredito | Evidência verificável |
|---|---|---|
| R1 avatar | ok | S1 e S6 usam `professionalPhoto` com placeholder canônico no `fita.html`. |
| R2 corte | ok | S1–S6: não há texto de leitura ou slot editável cortado pela borda do slide/canvas. |
| R3 fundos | ok | Há paper (S1, S4–S6), foto full-bleed (S2) e fundo accent (S3). |
| R4 área morta | **VIOLA** | S5 deixa grande bloco inferior direito e base sem âncora; a área visualmente morta supera 35% do slide. Craft fica limitado a 6. |
| R5 UI-decor | ok | Stamps e CTA têm função editorial; não há elemento decorativo imitando interface. |
| R6 contraste | ok | Texto teal sobre paper, texto claro sobre accent e card de S2 sobre overlay são legíveis. |

## QA do pack e imagens

- S1 preserva o duo-tom entrelaçado ao `professionalPhoto`; S2 é o único full-bleed + overlay + card; S3|S4 usa travessia em rodapé equilibrada; S6 fecha com `professionalPhoto`.
- A travessia S3|S4 permanece em fundo limpo e não encobre copy.
- **Defeito:** o decor de S5 apresenta contorno/halo magenta visível no canto superior direito. A paleta de referência é teal/paper; o resíduo de chroma não pertence ao registro clínico-editorial nem parece bokeh natural.

## QA narrativo — CONTEXT.md §3b + gramática LaserPro

- S1 usa frase ouvida entre aspas como tensão concreta; S2 acolhe e desculpabiliza sem culpabilizar a pessoa.
- S3 traduz o mecanismo (amplificação de sinais de dor pelo sistema nervoso) e avança a história; S4 mantém a PBM como complemento e preserva o acompanhamento clínico como essencial.
- S5 produz pertencimento, e S6 conecta comentário/salvamento à validação oferecida. A copy é específica de fibromialgia e não faz promessas clínicas.

## Defeitos a corrigir antes de novo render

1. **S5:** redistribuir a composição para que o espaço abaixo do corpo seja intencionalmente ocupado por uma âncora editorial ou foto, sem transformar o slide em ruído. É defeito de layout/estrutura do pack para este tipo de fecho.
2. **S5 decor:** regenerar o bokeh sem chroma residual/halo magenta; usar somente o registro teal/paper e validar o alpha no render.

**QA: FAIL**
