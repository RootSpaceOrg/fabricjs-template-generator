---
name: gp2-template-suggester
description: "Sugere automaticamente N novos modelos de carrossel genéricos multi-nicho para alimentar o catálogo da plataforma KultivAi. Opera em modo autônomo: escolhe um objetivo de marketing (aquisição / posicionamento / engajamento / retenção / educação / prova social), seleciona um framework narrativo que sirva esse objetivo, propõe um tema atemporal e neutro a vertical, e dispara o gp2-pipeline em paralelo (sub-agents) para gerar cada template. Mantém histórico rotativo local por objetivo para evitar repetição. Templates resultantes entram como scope=platform, status=review, business_type vazio. Use quando o usuário pedir 'sugira templates', 'gera N carrosséis', 'roda batch de templates', ou quando o loop autônomo de Pipeline 1 disparar."
---

# gp2-template-suggester

Cérebro de sugestão da Pipeline 1. Decide **o que vale a pena criar agora** e empacota o pedido pro `gp2-pipeline`.

## Princípios

1. **Multi-nicho sempre.** Todo template proposto deve funcionar para qualquer profissional/marca de qualquer vertical depois de troca de copy. Sem jargão de setor, sem ícones de nicho, sem CTA específico ("agende sua consulta"), sem `professionalPhoto`.
2. **Objetivo primeiro, tema depois.** O objetivo de marketing determina o framework narrativo, que determina a estrutura de slides, que determina o tipo de tema que cabe. Nunca o inverso.
3. **Atemporal por padrão.** Templates entram no catálogo e ficam lá. Evite temas amarrados a data específica (a menos que o objetivo seja sazonal explícito).
4. **Variedade > repetição.** Use o histórico local para não sugerir o mesmo framework + tema próximo dentro do mesmo objetivo.
5. **Paralelize a execução.** Sempre proponha N sugestões (default 3) e dispare N sub-agents do `gp2-pipeline` em paralelo — um por template.

## Quando usar

Frases-gatilho:
- "sugira N templates"
- "gera batch de carrosséis"
- "roda Pipeline 1"
- "alimenta o catálogo"
- "preciso de templates novos pra hoje"

Se o usuário não disser N, default é **3**.

## Parâmetros aceitos no pedido

| Parâmetro | Default | Como o usuário sinaliza |
|-----------|---------|-------------------------|
| `N` (quantidade) | 3 | "sugira 5 templates", "roda batch de 10" |
| `ambiente` | `prod` | "em dev", "no dev", "--env dev", "ambiente dev" |
| `objetivos` (filtro) | todos os 6, rotacionando | "só de aquisicao", "foca em posicionamento e educacao" |
| `frameworks` (filtro) | livre dentro do objetivo | "usa só listicle e step-by-step" |
| **`referencia`** (imagem) | nenhuma | usuário anexa 1+ imagens ao pedido. Suggester repassa a mesma referência para **todas** as N sugestões; cada sub-agent roda `gp2-pipeline` em **reference-driven mode**. |

**Detecção de ambiente:** se o pedido mencionar `dev` em qualquer forma ("em dev", "ambiente dev", "no dev", "--env dev"), use `dev`. Caso contrário, **prod** (default — segue a standing rule).

**Repasse obrigatório:** o ambiente decidido aqui DEVE aparecer literalmente no prompt enviado a cada sub-agent (campo `Ambiente:` no template — ver "Prompt template para gp2-pipeline" abaixo). Sem essa linha o sub-agent default pra prod e ignora a intenção do usuário.

Não use para:
- Criar UM template específico de um pedido explícito do usuário → vá direto para `gp2-pipeline`.
- Adaptar template existente a um nicho → isso é Pipeline 2/3 (outra skill, futura).

## Objetivos de marketing suportados

A skill sempre escolhe **um** objetivo por sugestão. Lista fechada:

| Objetivo | O que entrega ao cliente final | Frameworks que servem bem |
|----------|--------------------------------|---------------------------|
| `aquisicao` | Atrai novos seguidores/leads que ainda não conhecem a marca | Hook + Listicle, Problem-Agitate-Solve, Myth-vs-Truth |
| `posicionamento` | Estabelece autoridade e ponto de vista distinto | Contrarian Take, Framework Reveal, Data-Driven Insight |
| `engajamento` | Maximiza saves/shares/comentários do público existente | Listicle salvável, Mistakes-to-Avoid, "Send to a friend who…" |
| `educacao` | Ensina algo prático que o cliente final pode aplicar | Step-by-Step Tutorial, Before-After Process, Cheat Sheet |
| `prova_social` | Mostra resultado/transformação sem parecer venda direta | Case Study Narrative, Before-After Transformation, Mini-FAQ |
| `retencao` | Reforça relacionamento com público que já segue | Behind-the-Scenes, Lessons Learned, Vulnerable Story |

A escolha do objetivo deve **rotacionar**. Em batch de N, distribua entre objetivos diferentes — não sugira 3 carrosséis de `aquisicao` no mesmo batch.

Ver detalhes completos em [`references/objectives-and-frameworks.md`](references/objectives-and-frameworks.md).

## Frameworks narrativos disponíveis

Lista fechada de **estruturas** que mapeiam para os objetivos. Cada framework define **slide count típico** e **arco narrativo** — não copy específica.

| Framework | Slides típicos | Objetivo principal | Arco |
|-----------|----------------|---------------------|------|
| `listicle` | 6-9 | engajamento, aquisição | Hook → N itens numerados → CTA |
| `myth-vs-truth` | 5-7 | aquisição, posicionamento | Hook ("X mitos que…") → mito/verdade pares → fechamento |
| `step-by-step` | 5-8 | educacao | Hook ("Como X em N passos") → 1 passo por slide → recap/CTA |
| `problem-agitate-solve` | 3-5 | aquisicao | Problema → consequência → solução → próximo passo |
| `contrarian-take` | 4-6 | posicionamento | Crença comum → "mas eis o problema" → ponto de vista → implicação |
| `framework-reveal` | 5-7 | posicionamento, educacao | Hook ("O método X") → cada componente do framework → como aplicar |
| `mistakes-to-avoid` | 5-8 | engajamento, educacao | Hook ("N erros que…") → 1 erro+correção por slide → CTA |
| `case-study-narrative` | 5-7 | prova_social | Contexto → desafio → ação → resultado → lição |
| `before-after-transformation` | 3-5 | prova_social, educacao | Estado inicial → o que mudou → estado final → como replicar |
| `cheat-sheet` | 1-3 | educacao, engajamento | Compilação visual de regras/fórmulas/atalhos salváveis |
| `data-driven-insight` | 4-6 | posicionamento | Stat surpreendente → contexto → implicação → ação |
| `vulnerable-story` | 5-7 | retencao | Hook honesto ("Eu errei em X") → narrativa → lição → convite |
| `behind-the-scenes` | 4-6 | retencao | "Como funciona X que ninguém mostra" → revelação → contexto |
| `mini-faq` | 4-6 | prova_social, educacao | "N perguntas que mais escuto sobre X" → pergunta+resposta |

Ver instruções detalhadas de cada framework (incluindo slide-by-slide content guidance e hooks recomendados) em [`references/objectives-and-frameworks.md`](references/objectives-and-frameworks.md).

## Arquétipos sugeridos por framework

O suggester recomenda arquétipos A* (catálogo [`_shared/COMPOSITIONS.md`](../_shared/COMPOSITIONS.md)) por framework. **Recomendação, não jaula** — art-director escolhe livremente, mas usa isso como ponto de partida. As regras de diversidade composicional do art-director (≥2 arquétipos em ≥3 slides; ≥3 em ≥5) sempre prevalecem.

> **Nota multi-nicho:** o suggester **não** usa `A14-rich-hero-cutout`, pois exige `professionalPhoto` (incompatível com templates de catálogo multi-nicho). A14 fica reservado para pedidos diretos do usuário via `gp2-request-interpreter` quando o brief inclui foto profissional.

| Framework | Arquétipos recomendados |
|-----------|-------------------------|
| `listicle` | capa A1/A10/A12 → miolo alternando A5 + A3 → CTA A6 |
| `myth-vs-truth` | capa A10 → A9 (comparação) → A6 |
| `step-by-step` | capa A1/A12 → miolo A13 (numerado editorial) ou A3/A8 sequencial → A7 (resultado) → A6 |
| `problem-agitate-solve` | capa A2 (dramática) → A13 (problema numerado) → A7 (dado) → A6 |
| `contrarian-take` | capa A10 → A3 + A4 (citação ancora) → A6 |
| `framework-reveal` | capa A1 → A11 (bento revelando) → A3 → A6 |
| `mistakes-to-avoid` | capa A10 → A13 (erros numerados) ou A5 → A3 → A6 |
| `case-study-narrative` | capa A2 → A8 + A12 (foto narrativa) → A7 (resultado) → A6 |
| `before-after-transformation` | A1 → A9 (antes/depois) → A6 |
| `cheat-sheet` | A1 → A11 (bento) → A6 |
| `data-driven-insight` | A2 → A7 (data spotlight) → A3 → A6 |
| `vulnerable-story` | A12 → A3 → A4 (citação clímax) → A6 |
| `behind-the-scenes` | A2 → A8 → A8 → A6 |
| `mini-faq` | A1 → A3 (Q+A por slide) → A6 |

## Moves sugeridos por objetivo

Moves M* do catálogo [`_shared/CAROUSEL_MOVES.md`](../_shared/CAROUSEL_MOVES.md). Suggester sugere 1–2 moves por objetivo; art-director decide a forma final.

| Objetivo | Moves recomendados |
|----------|--------------------|
| `aquisicao` | M1 (hook visual) + M4 (cta arrow) — gancho forte + orientação |
| `posicionamento` | M5 (quote pull) + M8 (fio tipográfico) — editorial premium |
| `engajamento` | M2 (número ostentatório) + M4 — ritmo + orientação |
| `retencao` | M3 (bleed) ou M7 (color block shift) — dinâmica visual |
| `educacao` | M11 (numero-slide-eyebrow) + M4 — numeração editorial premium + orientação. Alternativa minimal: M9 + M4. |
| `prova_social` | M5 (quote pull) + M8 — citação ancora a prova |

**Regra de variedade entre templates:** em batches grandes, evite repetir o mesmo par de moves em ≥2 templates consecutivos do mesmo objetivo. Consulte o histórico antes de finalizar a sugestão.

## Modo com referência visual

Quando o usuário anexa 1+ imagens ao pedido, o suggester opera em **modo com referência**. Comportamento:

- **A mesma referência é repassada para TODAS as N sugestões do batch.** O usuário escolheu um vocabulário visual — todo o batch herda.
- Cada sub-agent do `gp2-pipeline` recebe a referência e roda em **reference-driven mode** (interpreter detecta a imagem; art-director extrai paleta/tipografia/composição da referência).
- **Multi-nicho continua valendo.** A referência informa **só direção visual** — não muda copy, segmento, CTA, nem libera professionalPhoto. Todas as diretrizes multi-nicho do prompt template (sem jargão, sem ícone de setor, sem CTA de serviço, sem professionalPhoto) continuam obrigatórias.
- **Variedade de objetivo/framework é mantida.** O batch ainda distribui entre objetivos diferentes e usa frameworks distintos por sugestão. A referência não substitui essa rotação — ela só pinta com vocabulário visual comum.
- **Risco aceito:** os N templates do batch podem ficar visualmente parecidos entre si (mesma paleta, tipografia, vocabulário composicional). Isso é o que o usuário quis ao anexar a referência. A variedade vem do framework/copy, não do visual.

**Como o suggester repassa a referência:**
1. A imagem chega no contexto do suggester (anexada à mensagem do usuário).
2. Cada chamada `Agent` para o sub-agent deve incluir a referência no prompt (passe o path da imagem se ela foi salva localmente, ou inclua a imagem diretamente no contexto do Agent se o runtime suportar anexar imagem ao prompt do sub-agent).
3. O prompt template ganha a seção `Referência visual` (ver template atualizado abaixo) instruindo o sub-agent a rodar em reference-driven mode.

**Quando NÃO usar este modo:** se o usuário só citou uma marca por nome ("estilo Apple", "tipo Nubank") sem anexar imagem, **não invente referência**. Trate como pedido em free mode e registre o sinal estilístico em `Tom / copy` do prompt do sub-agent.

## Imagens no template

Multi-nicho usa **apenas** `userAsset` — nunca `professionalPhoto`. O cliente final substitui pelas imagens dele no editor.

**Distribuição esperada no batch:**
- Evite mais de 1 template sem nenhuma imagem em batch de 3.
- Ao menos 1 template por batch deve ter imagem em maioria dos slides.
- Slides sem imagem: composição tipográfica + elementos geométricos decorativos (barras, divisores, padrões).

Detalhes finos de posição/tratamento ficam com o art-director via arquétipos.

## Hook do Slide 1 — onde mora a vida do template

O Slide 1 é o gate algorítmico do Instagram: se ele não para o scroll, o resto não importa. A skill **sempre** especifica uma das fórmulas de hook validadas para o framework escolhido. Ver [`references/hook-formulas.md`](references/hook-formulas.md) para o catálogo completo.

## Workflow da skill

0. **Detectar referência visual.** Verifique se o usuário anexou 1+ imagens à mensagem.
   - Se sim: salve em `artifacts/gp2-template-suggester/_shared-reference/<batch-id>.<ext>` (use timestamp como batch-id), marque o batch como **modo com referência** e prepare-se para incluir a referência em todas as N sugestões.
   - Se não: modo free (comportamento padrão atual).
   - Citação textual de marca sem imagem ("estilo Apple") ≠ referência — não invente, trate como free mode.

1. **Carregar histórico** (`scripts/suggestion-history.py list <objetivo>`)
   - Lê as últimas N sugestões por objetivo (default keep=20).
   - Lista fica disponível como contexto pra não repetir framework+tema próximos.

2. **Decidir o batch** (default 3 sugestões):
   - Distribua entre objetivos diferentes. Ex: batch de 3 → 1 aquisicao + 1 posicionamento + 1 educacao.
   - Para cada sugestão, escolha framework compatível com o objetivo (ver tabela acima).
   - **Para cada sugestão, defina a intenção composicional por slide** conforme a tabela de intenção típica por framework (ver "Composição visual" acima). Respeite a regra de distribuição de imagens no batch.
   - Proponha um tema **atemporal**, **neutro a vertical**, **acionável** (ver "Critérios de tema" abaixo).
   - Confirme contra o histórico: nenhuma combinação framework+tema deve sobrepor semanticamente com as últimas 20 do mesmo objetivo. Também evite repetir o mesmo padrão composicional 3× seguido no mesmo objetivo. Se sobrepor, gere outro tema ou troque o framework.

3. **Materializar cada sugestão como prompt do gp2-pipeline**:
   - Use o template de prompt em "Prompt template para gp2-pipeline" abaixo.
   - Cada sugestão é um prompt completo e autocontido (sub-agent não vê esta skill).

4. **Disparar em paralelo**:
   - Para cada sugestão, spawne um sub-agent com `Agent` tool (`subagent_type: general-purpose`) **na mesma mensagem** (todas as chamadas Agent em um único bloco de tool_use, sem aguardar entre elas).
   - Cada sub-agent recebe **apenas** o prompt da sua sugestão + instrução de rodar `gp2-pipeline`. Não passe esta skill inteira.

5. **Registrar no histórico** (`scripts/suggestion-history.py append <objetivo>`):
   - Salve cada sugestão **antes** ou **junto** com o dispatch, não depois — assim mesmo se a pipeline falhar, o histórico evita repetir o mesmo tema na próxima rodada.
   - Inclua os arquétipos e moves sugeridos via `--archetypes "A1,A5,..."` e `--moves "M9,M4"` — esses campos alimentam a regra de variedade composicional.

6. **Aguardar resultados e consolidar relatório**:
   - Cada sub-agent retorna o template ID + status dos gates do `gp2-pipeline`.
   - Compile um relatório consolidado com sucessos, falhas e IDs.

## Critérios de tema

Um tema válido para template multi-nicho:

- **Atemporal**: "como organizar sua semana" ✅ / "metas pra dezembro" ❌
- **Universal**: "5 erros ao começar algo novo" ✅ / "5 erros ao tratar diabetes" ❌
- **Acionável**: "como dar feedback que melhora resultados" ✅ / "reflexões sobre liderança" ❌ (vago)
- **Concreto o suficiente pra um arco narrativo claro**: precisa caber no framework escolhido.
- **Sem referência cultural específica**: evite eventos esportivos, séries, memes datados.

Se você inventou um tema que ofende qualquer critério, descarte e gere outro. Não force.

## Prompt template para gp2-pipeline

Cada sugestão vira um prompt como este (substitua os `<placeholders>`):

```text
Rode gp2-pipeline com este pedido.

Crie um CARROSSEL GENÉRICO MULTI-NICHO.

Objetivo de marketing: <OBJETIVO>
Framework narrativo: <FRAMEWORK>
Tema: <TEMA EM 1 FRASE CLARA>

Referência visual: <"imagem anexada — rode em reference-driven mode, art-director extrai paleta/tipografia/composição da referência" | "nenhuma — rode em free mode">
<Se houver referência: a imagem está anexada a esta mensagem. O gp2-request-interpreter vai detectá-la e passar para o art-director.>

Diretrizes multi-nicho (obrigatórias — valem MESMO quando há referência visual):
- A copy de TODOS os slides deve ser neutra a vertical. Qualquer profissional/marca de qualquer nicho deve adaptar este template trocando apenas os campos editáveis (data-template-element).
- Não use jargão de nicho nenhum. Evite "paciente", "cliente", "aluno", "tutor", "consultório", "loja", "academia". Prefira "pessoas", "você", "seu público".
- NÃO inclua professionalPhoto (data-image-type="professionalPhoto"). Templates multi-nicho não amarram a avatar específico de pessoa. **Mesmo que a referência mostre foto profissional, NÃO replique** — substitua por foto contextual (userAsset) ou composição tipográfica.
- IMAGENS userAsset SÃO PERMITIDAS E ENCORAJADAS. "Sem professionalPhoto" ≠ "sem imagens nenhuma". userAsset é genérico — cliente final substitui pela imagem dele.
- Sem ícones, símbolos ou metáforas visuais de setor (sem cruz médica, sem patinha, sem haltere, sem batom, etc.). Ícones abstratos (números, setas, check/X, gráficos, padrões) são livres. **Mesmo que a referência tenha ícone de nicho, NÃO replique.**
- CTA do último slide deve ser genérico: "Salve este post", "Compartilhe", "Comente <palavra>", "Siga para mais", "Marque alguém que precisa ler". Nunca CTA de serviço. **Mesmo que a referência mostre CTA de serviço, substitua por CTA genérico.**
- **Da referência, herde APENAS: paleta, tipografia, composição/arquétipos, elementos editoriais decorativos, tratamento de imagem genérico.** NÃO herde: copy, logo, fotos específicas, ícones de nicho, CTAs de serviço. O art-director deve registrar em "Notas para o designer" o que NÃO copiar.

Estrutura sugerida:
- Formato: Instagram feed 1080×1350.
- Carrossel de <N> slides (sugerido pelo framework).
- Sequência narrativa: <SEQUÊNCIA derivada do framework — ex: Listicle, Tutorial, Comparação, Problema-Solução, Standard>.
- Hook do Slide 1: <FÓRMULA + 1 LINHA DE COPY EXEMPLO>. Esta é só uma sugestão de copy do hook — o designer pode refinar mantendo a fórmula.
- Brand colors: primary + secondary (multi-nicho aproveita as duas cores swappable do usuário).
- Tom: <TOM coerente com o objetivo — neutro, inspirador, educativo, contrarian, etc.>.

Arquétipos sugeridos (recomendação ao art-director — não jaula. Catálogo `_shared/COMPOSITIONS.md`):
- Slide 1: <A?>
- Slide 2: <A?>
- ...
- Slide N (CTA): A6-cta-button-anchored

Carousel moves sugeridos (recomendação ao art-director — catálogo `_shared/CAROUSEL_MOVES.md`):
- <M?-slug>: <em quais slides>
- <M?-slug>: <em quais slides>

Notas adicionais por slide (preencha só quando precisar refinar além do arquétipo declarado):
- Slide N: <ex: foto contextual de ambiente, sem pessoa específica>

Diretrizes de imagem (para o art-director e html-designer):
- Imagens são userAsset — o cliente final substitui pela imagem dele no editor. Nunca professionalPhoto em multi-nicho.
- Nos slides que têm imagem: use foto stock neutra de cenário/objeto/textura como placeholder (nunca pessoa específica, nunca ícone de setor).
- Nos slides sem imagem: composição tipográfica + elementos geométricos decorativos (barras, divisores, padrões).

Use o art-director para decidir família estética, paleta hex, escala tipográfica, e detalhe de execução dos arquétipos e moves sugeridos acima.

Ambiente: <AMBIENTE>          # "prod" ou "dev" — passe ao uploader como --env <AMBIENTE>

Suba como sempre (status=review, scope=platform, owner_user_id=templateGenerator, business_type vazio). Use o ambiente acima — se for "dev", o comando final do uploader deve incluir `--env dev`; se "prod", omita a flag.
```

## Spawn paralelo de sub-agents

Quando for disparar:

- Uma única mensagem com **N chamadas Agent paralelas**.
- Cada Agent recebe `subagent_type: general-purpose` e prompt = o texto acima preenchido.
- Cada Agent rodará `gp2-pipeline` no seu próprio workspace de artifacts (slug único por template).

**Quando houver referência visual:**
- Anexe a **mesma** imagem de referência em **todas** as N chamadas Agent — a referência é compartilhada por todo o batch.
- A referência precisa chegar no contexto do sub-agent para que o `gp2-request-interpreter` detecte e o `gp2-art-director` extraia o vocabulário visual. Se o runtime do Agent não suporta anexar imagem direto, salve a referência em `artifacts/gp2-template-suggester/_shared-reference/<batch-id>.<ext>` e inclua o path absoluto no prompt do sub-agent com instrução clara: `"Referência visual em: <path>. Leia esta imagem antes de rodar o gp2-pipeline. O interpreter deve operar em reference-driven mode."`
- O prompt template já tem a linha `Referência visual:` — preencha-a indicando que a imagem está anexada/no path X.

Exemplo de disparo (N=3, em uma única resposta):

```
Agent(description="Gerar template aquisição", prompt="<prompt sugestão 1 + referência>", subagent_type="general-purpose")
Agent(description="Gerar template posicionamento", prompt="<prompt sugestão 2 + referência>", subagent_type="general-purpose")
Agent(description="Gerar template educacao", prompt="<prompt sugestão 3 + referência>", subagent_type="general-purpose")
```

## Histórico local

Localização: `skills/gp2-template-suggester/history/<objetivo>.json`

Cada arquivo é uma lista rotativa das últimas 20 sugestões daquele objetivo:

```json
[
  {
    "ts": "2026-05-24T14:32:11Z",
    "objective": "educacao",
    "framework": "listicle",
    "theme": "5 erros ao começar um projeto novo",
    "hook_formula": "numerical-mistake-list",
    "archetypes": ["A1", "A5", "A5", "A3", "A6"],
    "moves": ["M9", "M4"],
    "template_id": "abc123",
    "status": "dispatched"
  }
]
```

Comandos:

```bash
# Listar últimas N do objetivo (também retorna contagens agregadas de archetypes/moves)
python skills/gp2-template-suggester/scripts/suggestion-history.py list <objetivo>

# Acrescentar (mantém só as últimas 20)
python skills/gp2-template-suggester/scripts/suggestion-history.py append <objetivo> \
  --framework <fw> --theme "<tema>" --hook <formula> \
  --archetypes "A1,A5,A5,A3,A6" --moves "M9,M4" \
  [--template-id <id>]
```

Quando consultar para evitar repetição, considere semanticamente próximo (não exato):
- "5 erros ao começar algo novo" ≈ "7 erros que iniciantes cometem" → repetição.
- "5 erros ao começar algo novo" ≠ "5 sinais de que você precisa mudar de rumo" → ok, frameworks parecidos mas ângulos distintos.

**Regra de variedade composicional (consulte contagens agregadas do `list`):**
- Evite repetir o mesmo arquétipo dominante (>50% dos slides) em ≥2 templates consecutivos do mesmo objetivo.
- Evite o mesmo par de moves em ≥2 templates seguidos do objetivo.
- Em conflito com o histórico, troque arquétipo de capa OU move secundário (mantém o framework e o tema).

## Política de iteração

| Etapa | Tentativas |
|-------|-----------|
| Gerar tema válido (passa critérios) | máx 3 por sugestão, antes de fallback para framework diferente |
| Sub-agent gp2-pipeline | governado pela política do próprio gp2-pipeline (não rein重ente aqui) |
| Falha de sub-agent | reporte no relatório final, não retente automaticamente |

## Resposta final ao usuário

Sempre reporte em formato consolidado:

```markdown
## Batch Pipeline 1 — <N> sugestões · ambiente: <prod|dev> · modo: <free | reference-driven>

### Sugestão 1: <framework> · <objetivo> · <intenção composicional resumida>
- Tema: <tema>
- Hook fórmula: <formula>
- Template ID: <id ou "FALHOU - <motivo>">
- Gates: <PASS|FAIL por gate, ou "ver evidências em artifacts/<slug>/">

### Sugestão 2: ...
### Sugestão 3: ...

### Consolidado
- Ambiente: <prod|dev>
- Modo: <free | reference-driven — se reference-driven, indique path da referência compartilhada>
- Sugestões dispatched: <N>
- Padrão de imagens: <X sem imagem · Y com acento · Z image-heavy>  ← deve respeitar política (máx 1 sem imagem em batch de 3; ao menos 1 image-heavy em batch ≥5)
- Templates criados com sucesso: <X>
- Falhas: <Y> (detalhes acima)
- Próximos templates entram em /revisar-templates como status=review
- Histórico atualizado: <objetivos atualizados>
```

## Não faça

- ❌ Não invente um novo objetivo fora da lista de 6.
- ❌ Não invente um novo framework fora da lista de 14 — adicione um nas references primeiro, depois use.
- ❌ Não sugira tema com nome de profissão/setor ("para advogados", "para personal trainers").
- ❌ Não use o mesmo framework duas vezes no mesmo batch (variedade).
- ❌ Não chame `gp2-pipeline` direto sem passar pelo prompt template — você perde as garantias multi-nicho.
- ❌ Não pule o registro no histórico — o loop autônomo depende dele pra não repetir.
- ❌ Não execute sub-agents em série esperando um terminar antes de spawnar o próximo. Paralelize.

## Referências

- [`references/objectives-and-frameworks.md`](references/objectives-and-frameworks.md) — taxonomia completa de objetivos, frameworks, estrutura slide-a-slide, fontes da pesquisa.
- [`references/hook-formulas.md`](references/hook-formulas.md) — catálogo de fórmulas de hook para Slide 1 com exemplos por framework.
