# Judge QA — bold-arco-3

Pack de referência: `packs/bold-educacional/reference.png`.

## Regras duras (R1–R6)

| Regra | Resultado | Evidência no render |
|---|---|---|
| R1 slot de foto | ok | Não há `professionalPhoto`; o basset e a foto de aplicação são `userAsset` estáticos (S1 e S2). |
| R2 corte | ok | Headline, card, CTA e logo ficam inteiros dentro do canvas em S1–S3. |
| R3 monocromia | ok | Fundo meme/foto em S1–S2 e fechamento em primary no S3. |
| R4 área morta | ok | S1 usa a cena meme, S2 equilibra foto e cartão, S3 usa statement, apoio, CTA e logo. |
| R5 UI decorativa | ok | As tarjas convidam a arrastar (S1) e salvar antes da sessão (S3). |
| R6 contraste | ok | Copy ink sobre foto/cartão e paper sobre primary mantém leitura clara. |

## Check QA do pack

- Narrativa: PASS — o medo abre a conversa, o S2 desmonta a associação equivocada com corte/calor e o S3 transforma a dúvida em perguntas práticas antes da sessão.
- Sem redundância: PASS — cada slide cumpre gancho, mecanismo e ação, respectivamente.
- Imperativos: PASS — `arrasta` promete a virada do mito; `salve` aponta para perguntas de objetivo, parâmetros e sensações.
- Especificidade: PASS — fala de laser terapêutico/fotobiomodulação, baixa intensidade, objetivo ablativo/térmico, área e protocolo.
- Copy/slots: PASS — todas as caixas e linhas cabem no render, sem overflow.
- Registro do pack: PASS — meme fotográfico, cartão sobre foto e conclusão chapada seguem o repertório calibrado pela referência.
- Lessons do pack: PASS — headlines em sentence case e CTAs quadrados permanecem acionáveis e legíveis.

**QA: PASS**
