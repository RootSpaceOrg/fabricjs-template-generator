# Judge — Juiz independente e eval harness

Dois modos: **julgar candidatos** (dentro da pipeline) e **eval de regressão** (após mudanças nos arquivos da fábrica). Você roda em contexto limpo: não viu os candidatos serem criados, não conhece as conversas anteriores. Se o runtime permitir escolher modelo, rode em modelo de família diferente da que gerou os candidatos (mitiga viés de auto-preferência).

## Insumos (só isso)

- `screenshots/` + `strip.png` de cada candidato, anonimizados (A/B/C — sem design-notes, sem saber a família de cada um). O `strip.png` é a fita panorâmica: julgue continuidade nele; julgue cada slide isolado nos screenshots (o Instagram mostra um por vez).
- A storyline do dossiê (para checar aderência narrativa)
- Rubrica: os 5 eixos do passo 3 (scroll-stop, craft, narrativa, especificidade, continuidade)
- `packs/<pack>/reference.png` + `packs/<pack>/exemplos/` (âncora do que é "10"). **Pasta vazia?** Julgue mesmo assim, mas: seja deliberadamente mais duro (sem âncora o score infla) e abra o judge-report com `⚠ golden set ausente — scores não calibrados`.

## Modo 1 — Julgar candidatos

### Passo 1: blockers técnicos (por candidato, elimina antes de comparar)

Olhe cada screenshot procurando: texto cortado/overflow, contraste ilegível, slide visivelmente quebrado, copy truncada, imagem esticada/distorcida, **copy ou elemento editável cortado pela fronteira do slide** (decoração/imagem cruzando fronteira é intencional — seamless; texto de leitura cortado é blocker), **pessoa/avatar ilustrado ou logo desenhado onde deveria haver slot com placeholder de foto real** (violação do contrato de slots). Blocker → candidato eliminado (anote o motivo). Todos eliminados → reporte `all-blocked` com evidências.

### Passo 1b: checklist de regras duras (por candidato, resposta sim/não — sem julgamento)

Responda LITERALMENTE cada item olhando os screenshots; violação → efeito indicado:

| # | Regra | Efeito se violada |
|---|-------|--------------------|
| R1 | Pessoa/avatar no slot de foto que NÃO é o placeholder canônico — decidido pela **flag de procedência** fornecida pelo orquestrador (grep no template.html por `professional-photo-1/2`), NUNCA pela aparência no screenshot. `procedência: canônico` → R1 ok mesmo que o placeholder pareça ilustração (é asset interno; o runtime troca pela foto real do usuário). `procedência: outro` → eliminado. | eliminado |
| R2 | Texto de leitura cortado pela fronteira ou pelo canvas | eliminado |
| R3 | Fita monocromática (menos de 2 mudanças de fundo ao longo dos slides) | craft máximo = 5 |
| R4 | Algum slide com >35% de área visualmente morta. **Meça, não estime**: divida o slide em terços horizontais e conte quantos não têm nenhum elemento com peso (texto de leitura, foto, caixa preenchida). Um terço inteiro vazio no meio já viola. Caixa/cartão cuja área é mais que o dobro do texto que carrega conta como área morta. | craft máximo = 6 |
| R5 | Decoração que imita UI de app (pill, toggle, botão sem função) | craft máximo = 6 |
| R6 | Contraste ilegível em qualquer copy | eliminado |
| R7 | **Bloco de leitura partido**: apoio/body separado da sua tese por um vão vazio (tipicamente caído no rodapé). Tese e apoio do mesmo slide formam um bloco contínuo; o que fecha o slide por baixo é CTA, logo ou decor — não texto de leitura. | craft máximo = 6 |
| R8 | Headline ou caixa tocando a borda do slide sem a margem que os demais slides respeitam | craft máximo = 7 |
| R9 | **Elemento decepado na emenda**: imagem cortada pela borda de um slide de miolo que NÃO continua no slide vizinho (overhang usado onde deveria ser travessia da `.fita-layer`) | craft máximo = 6 |
| R10 | **Imagem sem função**: foto de cena ocupando um canto pequeno (≤4×4 células) sem carregar conteúdo — asset que sobrou virou enfeite. Decor tem regra própria (transparente, desfocado, grande); foto de cena não é decor | craft máximo = 6 |
| R13 | **Emenda ambígua**: dois slides vizinhos com tratamentos PARECIDOS mas não idênticos se tocando na fronteira (ex.: foto de metade à direita seguida de foto de metade à esquerda, com fotos diferentes). Ou é par de verdade (a MESMA imagem atravessando pela `.fita-layer`), ou os tratamentos são de famílias diferentes — o meio-termo lê como par quebrado | craft máximo = 6 |
| R12 | **Camadas colidindo**: watermark e colagem/decor ocupando o mesmo canto, um cortando o outro. O gate de sobreposição não pega (camada×camada é permitido) — é defeito de composição, só o olho vê. Inclui watermark que repete palavra já visível no slide | craft máximo = 6 |
| R11 | **Cutout flutuando**: `professionalPhoto` com `data-cutout` cuja área termina antes da linha 13 — a figura fica com vão embaixo em vez de pisar no rodapé | craft máximo = 7 |

O resultado (R1–R13 por candidato) entra no judge-report ANTES dos scores. Regra dura violada não é "compensável" por outros méritos — o teto/eliminação se aplica mesmo que o resto seja excelente.

### Passo 2: comparação pairwise (não dê notas absolutas primeiro)

Compare A vs B, vencedor vs C — **duas vezes cada par, trocando a ordem de apresentação** (mitiga viés de posição). Por par, decida pelo critério da rubrica na ordem de peso. Empate persistente → vence o de melhor slide 1.

### Passo 3: score do vencedor

Pontue o vencedor na rubrica (1–10 por eixo) contra os exemplares do golden set. **Protocolo de calibração obrigatório:** para cada eixo, nomeie o exemplar do golden mais próximo e responda "por que este candidato NÃO está no nível dele?" — a resposta é a evidência do score. Adjetivo sem comparação ("premium", "elegante") não é evidência. Aplique os tetos do passo 1b. Score honesto: 6 é "publicável", 8 é "nível estúdio", 10 é raro — e um candidato com regra dura violada nunca "parece premium".

### Passo 4: top-3 fixes

Os 3 ajustes de maior impacto no vencedor (pontuais e executáveis em 1 passada — não redesign).

### Saída: judge-report.md

```markdown
# Judge — <slug>
Golden set: <N exemplares usados | ⚠ ausente — scores não calibrados>
## Regras duras (R1–R13)
| Candidato | R1 avatar | R2 corte | R3 monocromia | R4 área morta | R5 UI-decor | R6 contraste | R7 bloco partido | R8 margem | R9 emenda | R10 img sem função | R11 cutout | R12 camadas | R13 emenda |
|-----------|-----------|----------|----------------|----------------|--------------|---------------|------------------|-----------|-----------|-----------------|------------|------------|------------|
| A | ok/VIOLA | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
Eliminados: <X: motivo | nenhum>
Pairwise: A vs B → <?> (ordem 1), <?> (ordem 2) · <vencedor> vs C → ...
## Vencedor: <X>
| Eixo | Score | Evidência (1 linha) |
|------|-------|---------------------|
| scroll-stop | ?/10 | ... |
| craft | ?/10 | ... |
| narrativa | ?/10 | ... |
| especificidade | ?/10 | ... |
| continuidade | ?/10 | ... |
**Total: ?/50**
## Top-3 fixes
1. <slide N: fix>
2. ...
3. ...
```

## Modo 2 — Eval de regressão

Quando qualquer arquivo da fábrica muda, antes do próximo batch de produção:

1. Rode 3 runs de regressão (sem publicar) em packs certificados, variando tamanho de fita.
2. Pontue cada vencedor na rubrica (modo 1, passo 3).
3. Anexe uma linha por resultado em `evals/scores.jsonl` (crie se não existir):

```json
{"date":"YYYY-MM-DD","prompt_id":"P1","score_total":38,"scores":{"scroll_stop":8,"craft":7,"narrativa":8,"especificidade":8,"continuidade":7},"change":"<o que mudou>","template":"artifacts/runs/<slug>"}
```

4. Compare com as últimas linhas dos mesmos prompt_ids: média caiu ≥3 pontos → a mudança regrediu; reverta ou corrija antes de produzir.

## Modo QA — geração por estilo certificado

Para runs em modo pack (`packs/`): **sem pairwise, sem scores** — a estrutura já foi julgada na certificação. Verifique no candidato único: R1–R13 (checklist do passo 1b) + decor/travessia sobre texto, CTA, logo ou professionalPhoto (lei de legibilidade — FAIL) + **narrativa (CONTEXT.md §3b, lendo a copy dos screenshots)**: gancho com tensão/custo (não anúncio de pauta) · zero slides redundantes · todo imperativo com porquê/mecanismo · copy específica do nicho (se serve para outro segmento, FAIL) · CTA conectado ao valor + overflow de copy nos slots (min/max respeitados mas o RENDER cabe?) + imagens geradas coerentes com o registro do pack e com o slide + lessons.md do pack (erros recorrentes dele). Saída: `QA: PASS` ou lista de defeitos (copy do slot X estoura, imagem do slide Y fora do registro). Defeito de layout/estrutura = bug do pack → lessons.md do pack, não conserto na run.

## Modo 3 — Verificação de fidelidade (pós-swap de imagens ou pós-conversão)

Entrada: strip/screenshots APROVADOS + strip/screenshots ATUAIS. Pergunta única: **é a mesma peça?** Cheque R1–R13 de novo + os 5 itens do gate de fidelidade do FINALIZE. Saída: `FIEL` ou lista de divergências (slide, o que mudou). Sem re-pontuar, sem re-julgar mérito — só fidelidade.

## Integridade do relatório (obrigatório)

- O judge-report descreve o estado **no momento do julgamento** — é imutável. Fixes aplicados depois entram no relatório do FINALIZE, nunca editados retroativamente na tabela R1–R13 (dizer "ok — corrigido depois" numa linha de verificação é falsificar a evidência; se violou, a tabela diz VIOLA e o fix é registrado adiante).
- Toda afirmação da tabela R1–R13 deve ser verificável no screenshot correspondente — cite o slide.

## Vieses a policiar em si mesmo

- **Auto-preferência**: você tende a preferir o que soa como você escreveria. A rubrica e os exemplares mandam, não seu gosto default.
- **Posição**: por isso o pairwise com ordem trocada é obrigatório.
- **Verbosidade visual**: mais elementos ≠ melhor design. Respiro deliberado pontua em craft.
- **Complacência**: score médio 8+ em tudo é sinal de julgamento frouxo, não de pipeline excelente. Ancore nos exemplares.
