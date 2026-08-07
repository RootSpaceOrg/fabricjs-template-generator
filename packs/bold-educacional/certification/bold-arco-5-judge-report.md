# Judge QA — bold-arco-5

Pack de referência: `packs/bold-educacional/reference.png`.

## Regras duras (R1–R6)

| Regra | Resultado | Evidência no render |
|---|---|---|
| R1 slot de foto | ok | Não há `professionalPhoto`; shiba, pulso e pulseira são `userAsset` estáticos (S1–S3). |
| R2 corte | ok | Nenhum texto editável é cortado; no S3 a headline e o body ocupam áreas separadas, sem encavalamento. |
| R3 monocromia | ok | Há cena meme/foto, statements em primary e slides paper ao longo de S1–S5. |
| R4 área morta | ok | O respiro apoia headline, cartão, colagem ou bloco de perguntas; não há slide visualmente vazio. |
| R5 UI decorativa | ok | Tarjas acionam arraste (S1) e compartilhamento (S5), sem simular UI. |
| R6 contraste | ok | Ink sobre foto/paper e paper sobre chapa primary estão legíveis em S1–S5. |

## Check QA do pack

- Narrativa: PASS — abre no mito de “laser no sangue”, traduz ILIB como aplicação transcutânea, desloca o foco para o protocolo e fecha com perguntas úteis/compartilhamento.
- Sem redundância: PASS — S2 explica o nome, S3 define a lógica, S4 transforma a lógica em checklist e S5 conclui a conversa.
- Imperativos: PASS — `arrasta` entrega explicação; `pergunte` indica objetivo/parâmetros/plano; CTA final aponta para compartilhar informação.
- Especificidade: PASS — ILIB, artéria radial, comprimento de onda, dose, frequência e objetivo terapêutico são próprios do tema.
- Copy/slots: PASS — S3 foi conferido no render atual: headline de 104px com quatro linhas de grid e body abaixo, sem transbordamento/overlap; demais slots também cabem.
- Registro do pack: PASS — capa-meme, cartão sobre foto, statement chapado com colagem e lista em bloco preservam a linguagem da referência.
- Lessons do pack: PASS — sentence case, CTA funcional, corpo na escala do display e contraste foram mantidos.

**QA: PASS**
