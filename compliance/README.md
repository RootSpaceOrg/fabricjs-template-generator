# Compliance — curado por humano, nunca pesquisado pelo modelo

1 arquivo por vertical (`health.md`, `beauty.md`, ...) com as regras de publicidade dos conselhos profissionais (CFM, CFO, CFN, CFBM...) que limitam a copy. Fonte: resoluções oficiais, revisadas por humano — o modelo NUNCA atualiza estes arquivos por pesquisa própria (não é audit-grade).

Formato sugerido:

```markdown
---
vertical: health
reviewed_by: <nome>
reviewed_at: <YYYY-MM-DD>
sources: [<links das resoluções>]
---
## Proibido afirmar
- promessa/garantia de resultado ("elimina de vez", "resultado garantido")
- "sem dor", "sem risco", "100% seguro"
- antes/depois de paciente real sem os requisitos do conselho
- preço/desconto como chamariz (varia por conselho — ver fonte)
## Obrigatório
- <ex: responsável técnico quando aplicável>
## Zona cinza (evitar)
- superlativos ("o melhor", "único")
```

**Enquanto o arquivo da vertical não existir**, o `CONTEXT.md` aplica a regra conservadora (sem promessa de resultado, sem comparação de superioridade, sem preço) e reporta a ausência.
