# Judge — gram-teste-1

QA do render vigente (`strip.png`, 2026-08-06), comparado a `clinical-photo-editorial/reference.png`.

## Regras duras (R1–R6)

| Regra | Veredito | Evidência |
|---|---|---|
| R1 avatar | ok | Slide 1 usa o placeholder canônico `professionalPhoto`. |
| R2 corte | ok | Não há texto de leitura cortado por fronteira ou canvas. |
| R3 fundos | ok | Paper nos slides 1, 2 e 4–6; accent no slide 3. |
| R4 área morta | ok | Cada slide tem âncora dominante: capa/figura, citação, mecanismo, solução, fecho ou CTA/foto. |
| R5 UI-decor | ok | Stamps e CTA têm função editorial; não há decor que imite UI. |
| R6 contraste | ok | Teal sobre paper e branco sobre accent permanecem legíveis. |

## QA do pack

- A capa usa display duo-tom, slot profissional e bokeh de ponteira PBM na borda, alinhada ao registro da referência.
- Foto paisagem contínua cruza a fronteira 4|5 pela `.fita-layer`, em área inferior sem encobrir copy.
- Decors são específicos de PBM, gerados para a run, com transparência e bokeh profundo.

## QA narrativo — CONTEXT.md §3b + gramática LaserPro

- **Gancho com tensão:** slide 1 valida a dúvida concreta de sair da sessão sem saber o que esperar; não é anúncio de pauta.
- **Zero redundância:** slides 2–5 avançam, respectivamente, de clichê/culpa para mecanismo, possibilidades modais e fecho emocional.
- **Mecanismo:** slide 3 traduz “luz não ionizante” como luz que não altera o DNA; nenhuma instrução clínica é apresentada sem contexto.
- **Especificidade:** PBM, luz não ionizante, parâmetros e protocolo individual tornam a copy exclusiva de laserterapia clínica.
- **CTA conectado:** slide 6 pede comentário e salvamento para retomar a conversa antes da próxima sessão, consequência direta do guia entregue.

**QA: PASS**
