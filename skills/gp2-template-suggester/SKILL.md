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

## Image mode — texto puro × texto+acentos × imagem-pesado

Pesquisa 2026 mostra que carrosséis **mixed-media** (texto + imagens estratégicas) têm 29% mais engajamento que carrosséis de texto puro ou só imagem ([Carouselli 2026 benchmark](https://carouselli.com/blog/instagram-carousel-engagement)). Templates puramente textuais entregam pior — e era exatamente o que estava acontecendo no batch de 10 que veio sem nenhuma imagem ilustrativa.

A skill agora decide explicitamente um `image_mode` por sugestão, repassa pro prompt do gp2-pipeline com instruções concretas de slots de imagem, e garante distribuição no batch (não pode ser 100% `text-only`).

### Os 3 modos

| Modo | Descrição | Slots de imagem por slide | Quando usar |
|------|-----------|---------------------------|-------------|
| `text-only` | Composição puramente tipográfica. Apenas formas geométricas, padrões e cor compõem o visual. | 0 imagens `userAsset` no template marcado. | Frameworks que vivem de tipografia bold (declarações, contrarian, stats). Use no MÁXIMO 30% do batch. |
| `text-with-accents` | Texto dominante + 1 imagem `userAsset` opcional em 2-3 slides como apoio (não como protagonista). | 1 slot `userAsset` em ~40% dos slides (capa + 1-2 internos). | Default da maioria dos frameworks. Versátil, multi-nicho fácil. |
| `image-heavy` | Imagem é protagonista; texto orbita ela. Cada slide tem 1 imagem grande, texto curto sobreposto ou ao lado. | 1 slot `userAsset` em quase todos os slides (≥70%). | Frameworks visuais (case-study, before-after, behind-the-scenes). |

**Importante:** todos os slots de imagem são `data-image-type="userAsset"` — o cliente final substitui pela imagem dele no editor. Nunca `professionalPhoto`. O template provê só os retângulos/posições + uma imagem placeholder neutra (cor sólida, padrão abstrato, ou foto stock genérica).

### Mapeamento framework → image_mode

Cada framework tem **modo preferido** e **modos compatíveis**:

| Framework | Preferido | Aceitáveis | Não usar |
|-----------|-----------|-----------|----------|
| `listicle` | text-with-accents | text-only, image-heavy | — |
| `myth-vs-truth` | text-with-accents | text-only | image-heavy |
| `step-by-step` | text-with-accents | image-heavy | text-only |
| `problem-agitate-solve` | text-with-accents | text-only | image-heavy |
| `contrarian-take` | text-only | text-with-accents | image-heavy |
| `framework-reveal` | text-with-accents | text-only | image-heavy |
| `mistakes-to-avoid` | text-with-accents | text-only, image-heavy | — |
| `case-study-narrative` | image-heavy | text-with-accents | text-only |
| `before-after-transformation` | image-heavy | text-with-accents | text-only |
| `cheat-sheet` | text-only | text-with-accents | image-heavy |
| `data-driven-insight` | text-only | text-with-accents | image-heavy |
| `vulnerable-story` | text-with-accents | image-heavy, text-only | — |
| `behind-the-scenes` | image-heavy | text-with-accents | text-only |
| `mini-faq` | text-with-accents | text-only | image-heavy |

### Política de distribuição no batch

Ao montar um batch de N sugestões:

- **Máximo 30% de `text-only`** no batch (com arredondamento pra baixo).
- **Mínimo 30% deve incluir imagem** (`text-with-accents` ou `image-heavy`).
- Se N ≥ 5, **pelo menos 1 deve ser `image-heavy`**.

Exemplos:
- N=3: máx 1 text-only, ao menos 1 com imagem (idealmente 1 text-only + 2 text-with-accents)
- N=5: máx 1 text-only, ao menos 1 image-heavy (ex: 1+3+1)
- N=10: máx 3 text-only, ao menos 2 image-heavy (ex: 2+5+3)

Se a rotação por objetivo + framework te empurrar pra um mix que viole essa regra, **troque o framework**, não o modo (porque o modo errado num framework errado entrega resultado ruim).

### Histórico

A skill registra `image_mode` no histórico junto com framework e theme — pra também rotacionar modos (evita 3 sugestões seguidas de `image-heavy` no mesmo objetivo).

## Hook do Slide 1 — onde mora a vida do template

O Slide 1 é o gate algorítmico do Instagram: se ele não para o scroll, o resto não importa. A skill **sempre** especifica uma das fórmulas de hook validadas para o framework escolhido. Ver [`references/hook-formulas.md`](references/hook-formulas.md) para o catálogo completo.

## Workflow da skill

1. **Carregar histórico** (`scripts/suggestion-history.py list <objetivo>`)
   - Lê as últimas N sugestões por objetivo (default keep=20).
   - Lista fica disponível como contexto pra não repetir framework+tema próximos.

2. **Decidir o batch** (default 3 sugestões):
   - Distribua entre objetivos diferentes. Ex: batch de 3 → 1 aquisicao + 1 posicionamento + 1 educacao.
   - Para cada sugestão, escolha framework compatível com o objetivo (ver tabela acima).
   - **Para cada sugestão, escolha `image_mode`** respeitando a tabela de mapeamento e a política de distribuição do batch (ver "Image mode" acima — máx 30% text-only, mínimo 30% com imagem, e se N≥5 ao menos 1 image-heavy).
   - Proponha um tema **atemporal**, **neutro a vertical**, **acionável** (ver "Critérios de tema" abaixo).
   - Confirme contra o histórico: nenhuma combinação framework+tema deve sobrepor semanticamente com as últimas 20 do mesmo objetivo. Também evite repetir o mesmo `image_mode` 3× seguidas no mesmo objetivo. Se sobrepor, gere outro tema ou troque o framework.

3. **Materializar cada sugestão como prompt do gp2-pipeline**:
   - Use o template de prompt em "Prompt template para gp2-pipeline" abaixo.
   - Cada sugestão é um prompt completo e autocontido (sub-agent não vê esta skill).

4. **Disparar em paralelo**:
   - Para cada sugestão, spawne um sub-agent com `Agent` tool (`subagent_type: general-purpose`) **na mesma mensagem** (todas as chamadas Agent em um único bloco de tool_use, sem aguardar entre elas).
   - Cada sub-agent recebe **apenas** o prompt da sua sugestão + instrução de rodar `gp2-pipeline`. Não passe esta skill inteira.

5. **Registrar no histórico** (`scripts/suggestion-history.py append <objetivo>`):
   - Salve cada sugestão **antes** ou **junto** com o dispatch, não depois — assim mesmo se a pipeline falhar, o histórico evita repetir o mesmo tema na próxima rodada.

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
Image mode: <IMAGE_MODE>            # text-only | text-with-accents | image-heavy
Tema: <TEMA EM 1 FRASE CLARA>

Diretrizes multi-nicho (obrigatórias):
- A copy de TODOS os slides deve ser neutra a vertical. Qualquer profissional/marca de qualquer nicho deve adaptar este template trocando apenas os campos editáveis (data-template-element).
- Não use jargão de nicho nenhum. Evite "paciente", "cliente", "aluno", "tutor", "consultório", "loja", "academia". Prefira "pessoas", "você", "seu público".
- NÃO inclua professionalPhoto (data-image-type="professionalPhoto"). Templates multi-nicho não amarram a avatar específico de pessoa.
- IMAGENS userAsset SÃO PERMITIDAS E ENCORAJADAS conforme o image_mode definido acima. "Sem professionalPhoto" ≠ "sem imagens nenhuma". userAsset é genérico — cliente final substitui pela imagem dele.
- Sem ícones, símbolos ou metáforas visuais de setor (sem cruz médica, sem patinha, sem haltere, sem batom, etc.). Ícones abstratos (números, setas, check/X, gráficos, padrões) são livres.
- CTA do último slide deve ser genérico: "Salve este post", "Compartilhe", "Comente <palavra>", "Siga para mais", "Marque alguém que precisa ler". Nunca CTA de serviço.

Estrutura sugerida:
- Formato: Instagram feed 1080×1350.
- Carrossel de <N> slides (sugerido pelo framework).
- Sequência narrativa: <SEQUÊNCIA derivada do framework — ex: Listicle, Tutorial, Comparação, Problema-Solução, Standard>.
- Hook do Slide 1: <FÓRMULA + 1 LINHA DE COPY EXEMPLO>. Esta é só uma sugestão de copy do hook — o designer pode refinar mantendo a fórmula.
- Brand colors: primary + secondary (multi-nicho aproveita as duas cores swappable do usuário).
- Carousel chrome: auto.
- Tom: <TOM coerente com o objetivo — neutro, inspirador, educativo, contrarian, etc.>.

Imagens no template (CRÍTICO — siga literalmente o image_mode acima):

<INSERIR UM DOS 3 BLOCOS ABAIXO conforme o image_mode escolhido:>

[Se image_mode = text-only]
- ZERO imagens userAsset no template. Composição é 100% tipográfica + formas geométricas + cor.
- Pode usar elementos vetoriais decorativos (barras, círculos, padrões, divisores) como apoio visual.
- Não inclua nenhum elemento <img> com data-image-type="userAsset".
- Justificativa: este framework vive de tipografia bold e contraste cromático; imagem aqui dilui a força.

[Se image_mode = text-with-accents]
- Inclua imagens userAsset em ~40% dos slides — tipicamente: capa (Slide 1) + 1 ou 2 slides internos como acento.
- Imagens devem ser RETÂNGULOS NEUTROS no template (cor sólida, padrão abstrato, ou foto stock genérica de cenário/objeto neutro — NUNCA pessoa específica).
- Cada <img> deve ter:
  - data-image-type="userAsset"
  - data-template-element="true"
  - data-te-description descrevendo o tipo de imagem ideal ("imagem de apoio ao tema; pode ser cenário, objeto ou textura — não amarrar a pessoa")
- Texto continua dominante (≤50 palavras por slide); imagens são apoio, não protagonistas.
- Justificativa: mixed-media entrega 29% mais engajamento que text-only puro (Carouselli 2026).

[Se image_mode = image-heavy]
- Inclua imagens userAsset em ≥70% dos slides — idealmente todos exceto capa de fechamento/CTA.
- Imagem ocupa pelo menos 50% da área de cada slide onde aparece (não acento — protagonista).
- Texto orbita a imagem: sobreposto com overlay, em barra lateral, ou abaixo em bloco compacto.
- Cada <img> deve ter:
  - data-image-type="userAsset"
  - data-template-element="true"
  - data-te-description orientando o tipo de cena ideal sem amarrar a vertical ("cenário antes/depois neutro", "imagem de processo/objeto representando a etapa", etc.)
- Placeholders no template devem ser imagens neutras (cor sólida com label "imagem aqui", padrão abstrato, ou stock genérico) — o cliente final substitui.
- Justificativa: frameworks visuais (case-study, before-after, behind-the-scenes) precisam da imagem como evidência narrativa.

Use o art-director livre para decidir família estética, paleta hex e movimento memorável.

Ambiente: <AMBIENTE>          # "prod" ou "dev" — passe ao uploader como --env <AMBIENTE>

Suba como sempre (status=review, scope=platform, owner_user_id=templateGenerator, business_type vazio). Use o ambiente acima — se for "dev", o comando final do uploader deve incluir `--env dev`; se "prod", omita a flag.
```

## Spawn paralelo de sub-agents

Quando for disparar:

- Uma única mensagem com **N chamadas Agent paralelas**.
- Cada Agent recebe `subagent_type: general-purpose` e prompt = o texto acima preenchido.
- Cada Agent rodará `gp2-pipeline` no seu próprio workspace de artifacts (slug único por template).

Exemplo de disparo (N=3, em uma única resposta):

```
Agent(description="Gerar template aquisição", prompt="<prompt sugestão 1>", subagent_type="general-purpose")
Agent(description="Gerar template posicionamento", prompt="<prompt sugestão 2>", subagent_type="general-purpose")
Agent(description="Gerar template educacao", prompt="<prompt sugestão 3>", subagent_type="general-purpose")
```

## Histórico local

Localização: `skills/gp2-template-suggester/history/<objetivo>.json`

Cada arquivo é uma lista rotativa das últimas 20 sugestões daquele objetivo:

```json
[
  {
    "ts": "2026-05-24T14:32:11Z",
    "framework": "listicle",
    "theme": "5 erros ao começar um projeto novo",
    "hook_formula": "numerical-mistake-list",
    "image_mode": "text-with-accents",
    "template_id": "abc123",
    "status": "dispatched"
  }
]
```

Comandos:

```bash
# Listar últimas N do objetivo
python skills/gp2-template-suggester/scripts/suggestion-history.py list <objetivo>

# Acrescentar (mantém só as últimas 20)
python skills/gp2-template-suggester/scripts/suggestion-history.py append <objetivo> \
  --framework <fw> --theme "<tema>" --hook <formula> --image-mode <modo> [--template-id <id>]
```

Quando consultar para evitar repetição, considere semanticamente próximo (não exato):
- "5 erros ao começar algo novo" ≈ "7 erros que iniciantes cometem" → repetição.
- "5 erros ao começar algo novo" ≠ "5 sinais de que você precisa mudar de rumo" → ok, frameworks parecidos mas ângulos distintos.

## Política de iteração

| Etapa | Tentativas |
|-------|-----------|
| Gerar tema válido (passa critérios) | máx 3 por sugestão, antes de fallback para framework diferente |
| Sub-agent gp2-pipeline | governado pela política do próprio gp2-pipeline (não rein重ente aqui) |
| Falha de sub-agent | reporte no relatório final, não retente automaticamente |

## Resposta final ao usuário

Sempre reporte em formato consolidado:

```markdown
## Batch Pipeline 1 — <N> sugestões · ambiente: <prod|dev>

### Sugestão 1: <framework> · <objetivo> · <image_mode>
- Tema: <tema>
- Hook fórmula: <formula>
- Template ID: <id ou "FALHOU - <motivo>">
- Gates: <PASS|FAIL por gate, ou "ver evidências em artifacts/<slug>/">

### Sugestão 2: ...
### Sugestão 3: ...

### Consolidado
- Ambiente: <prod|dev>
- Sugestões dispatched: <N>
- Distribuição image_mode: <X text-only · Y text-with-accents · Z image-heavy>  ← deve respeitar política (máx 30% text-only; se N≥5 ao menos 1 image-heavy)
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
