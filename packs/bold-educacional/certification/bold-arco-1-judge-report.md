# Judge QA — bold-arco-1

Pack de referência: `packs/bold-educacional/reference.png`.

## Regras duras (R1–R6)

| Regra | Resultado | Evidência no render |
|---|---|---|
| R1 slot de foto | ok | Não há `professionalPhoto`; foto e colagens são `userAsset` estáticos (S1, S2, S3 e S6). |
| R2 corte | ok | Nenhum texto editável toca ou cruza a borda em S1–S7. |
| R3 monocromia | ok | Alternância foto/paper/chapa primary em S1–S7. |
| R4 área morta | ok | Respiro tem função compositiva: foto, cartão, lista, statement ou CTA ocupam cada slide. |
| R5 UI decorativa | ok | Tarjas são convites de ação reais: arrastar (S1) e compartilhar (S7). |
| R6 contraste | ok | Ink sobre paper/foto velada e paper sobre primary permanecem legíveis em todos os slides. |

## Check QA do pack

- Narrativa: PASS — abre no custo de a dor invisível ser desacreditada, nomeia sinais e mecanismo, organiza o cuidado, posiciona a fotobiomodulação como complemento e termina em ação de consulta/compartilhamento.
- Sem redundância: PASS — S2 reconhece, S3 explica, S4 organiza o plano, S5 delimita o recurso e S6 prepara a conversa.
- Imperativos: PASS — `arrasta`, `anote`, `pergunte`, `salve` e `compartilhe` vêm conectados a informação ou preparação para a consulta.
- Especificidade: PASS — fibromialgia, sensibilização central, sono, fadiga, névoa mental e recurso complementar impedem leitura genérica para outro nicho.
- Copy/slots: PASS — texto cabe visualmente em todos os slots; nenhum overflow no render.
- Registro do pack: PASS — capa-meme fotográfica, statements em chapa primary, cartões/objeto de conteúdo e fechamento direto preservam a linguagem da referência.
- Lessons do pack: PASS — sentence case, tarjas quadradas acionáveis, contraste e caixas com conteúdo legível foram respeitados.

**QA: PASS**
