---
name: gp2-request-interpreter
description: "First step of GetPosts Pipeline v2. Two modes: (a) Free mode — pedido só em texto, captura 7 fatos e deixa direção estética livre para o art-director decidir; (b) Reference-driven mode — usuário anexou imagem ou citou referência, captura os mesmos 7 fatos de conteúdo (pode ver a imagem para informar decisões de conteúdo como nº slides, sequência, foto profissional, chrome) mas NÃO extrai direção visual (paleta, tipografia, família, movimento) — isso é responsabilidade do gp2-art-director. Nunca converte/marca/upload."
---

# gp2-request-interpreter

Produz o **brief enxuto** que o `gp2-art-director` e `gp2-html-designer` consomem. Opera em dois modos.

## Princípio

A v2 separa **interpretação de conteúdo** (este skill) de **direção visual** (`gp2-art-director`). O interpreter captura intenção e conteúdo; o art-director decide a estética. Essa regra vale em ambos os modos (free e reference-driven).

## What you decide (sempre)

| Decision | Why it belongs here |
|----------|---------------------|
| Asset type, dimensions, slide count | Hard input; can't be inferred later |
| **Vertical / segmento de marca** (livre — inferido do pedido) | Drives editor metadata and `data-segment`; não há lista fixa de valores |
| **Sequência narrativa** (Standard / Listicle / Tutorial / Comparação / Single-post) | Determina arco do carrossel e alternância de background — ver "Sequências narrativas" abaixo |
| Per-slide narrative role (1–2 lines) | Story arc — derivado da sequência mas pode customizar |
| **Hook do Slide 1** (fórmula + 1 linha de copy) | Slide 1 mata ou salva o carrossel — ver "Hook do Slide 1" abaixo |
| **Carousel chrome** (yes / no / auto) | Progress bar + seta de swipe são UI consistente em formatos longos; opt-in respeita variedade |
| Brand color count: primary only OR primary + secondary | Two swappable accents or one |
| Professional photo: yes / no / conditional | Trust-vs-noise decision |
| Copy/tone direction | Voice the user expects |

## What you DO NOT decide (em nenhum modo)

- Família estética — art-director decide (em free inventa; em reference-driven extrai da referência).
- Paleta hex específica — art-director resolve.
- Tipografia específica — art-director decide.
- Movimento memorável — art-director escolhe/identifica.
- Anti-AI rules ("avoid card spam", "avoid generic typography") — pertencem ao reviewer e ao `DESIGN_PRINCIPLES.md`.
- Tamanhos exatos de fonte por slide — designer ajusta no Passo 3.
- Posições absolutas de cada elemento — designer escolhe no Passo 1.

## When to use

Use as the first step of the pipeline when the user asks to create a post, carousel, story, ad, or template. Trigger phrases include: "cria um carrossel sobre…", "faz um post de…", "nesse estilo…", "igual à referência…".

Do not use for Fabric conversion, marker work, or upload.

## Dois modos de operação

A skill detecta automaticamente em qual modo está com base na presença (ou não) de imagens anexadas:

| Modo | Quando | Comportamento |
|------|--------|---------------|
| **Free mode** | pedido só em texto, sem referência visual | captura **só** os 7 fatos; direção estética fica com o art-director |
| **Reference-driven mode** | usuário anexou ≥ 1 imagem **ou** disse "nesse estilo", "igual à referência", "faz parecido com X" | captura os 7 fatos de conteúdo. Pode VER a imagem para decisões de conteúdo (nº slides, sequência, foto profissional, chrome). **NÃO extrai paleta, tipografia, família ou movimento** — a análise visual completa é feita pelo `gp2-art-director`. |

## Workflow

1. Leia o pedido. Detecte se há imagens anexadas ou linguagem de referência ("igual a…", "nesse estilo…").
2. **Se Free mode**:
   1. Decida os 7 fatos.
   2. Emita `brief.md`.
3. **Se Reference-driven mode**:
   1. Olhe a(s) imagem(ns) **apenas para informar decisões de conteúdo**: quantos slides a referência sugere, qual sequência narrativa se encaixa, se usa foto profissional, se tem carousel chrome.
   2. Decida os 7 fatos.
   3. Emita `brief.md` (com modo = reference-driven). **Não emita `reference-spec.md`** — a análise visual da referência será feita pelo art-director.
4. Marque incertezas só quando travariam o art-director ou designer.

**IMPORTANTE em reference-driven mode:** NÃO extraia paleta hex, tipografia, família estética, movimento memorável ou elementos editoriais da referência. Isso é responsabilidade exclusiva do `gp2-art-director`, que receberá a(s) imagem(ns) de referência do orquestrador.

## Sequências narrativas

Em vez de inventar o arco do carrossel do zero, escolha uma das **5 sequências canônicas** abaixo. Cada uma já tem papel + background sugerido por slide. O designer no Passo 1 (low-fi) parte com esqueleto pronto.

| Sequência | N slides | Quando usar |
|-----------|----------|-------------|
| **Standard** | 7 | Educativo geral: hook → problema → solução → features → detalhes → passos → CTA. Default quando o pedido é amplo. |
| **Listicle** | 5–10 | "X dicas", "X erros", "X sinais", "X benefícios". Capa + N itens + CTA. |
| **Tutorial** | 7 | Passo-a-passo: hook → contexto/por quê → 3 passos → resultado esperado → CTA. |
| **Comparação** | 5 | A vs B: capa → opção A → opção B → veredicto → CTA. |
| **Single-post** | 1 | Posts não-carrossel: datas comemorativas, citações, anúncios, capas isoladas. |

### Detecção automática

Analise a linguagem do pedido:

| Pista no pedido | Sequência |
|-----------------|-----------|
| "5 dicas…", "7 erros…", "X sinais de…", "lista de…" | **Listicle** (N = número mencionado, ou 5–7) |
| "como fazer…", "passo a passo…", "guia para…", "tutorial…" | **Tutorial** |
| "A ou B", "X vs Y", "diferença entre…", "qual escolher…" | **Comparação** |
| "post para Dia de…", "homenagem a…", "citação…", "single post", referência a um único frame | **Single-post** |
| Educativo amplo, sem formato claro | **Standard** (default) |

Se ambíguo, fique com **Standard**. Anote a sequência escolhida e por quê em uma linha do brief.

### Alternância de background por sequência

Convenções de cor por slide (designer pode ajustar no Passo 2, mas o esqueleto vem do interpreter):

- **Standard:** LIGHT, DARK, Brand, LIGHT, DARK, LIGHT, Brand
- **Listicle:** LIGHT (capa), alternar LIGHT/DARK nos itens, Brand (CTA)
- **Tutorial:** LIGHT (hook), DARK (contexto), alternar LIGHT/DARK nos passos, DARK (resultado), Brand (CTA)
- **Comparação:** LIGHT (capa), LIGHT (A), DARK (B), Brand (veredicto), DARK (CTA)
- **Single-post:** o slide pode ser LIGHT, DARK ou Brand — escolha pelo tom do post

Onde:
- **LIGHT** = neutro claro derivado do preset da marca (off-white quente)
- **DARK** = neutro escuro derivado do preset (near-black com tint brand)
- **Brand** = primary sólido OU gradient primary→secondary (se brief decidir 2 cores)

No Free mode os hexs ficam abertos para o art-director resolver. No Reference-driven mode o art-director extrai a paleta da referência e a trava no `visual-plan.md`.

## Hook do Slide 1

O Slide 1 tem 1 segundo para parar o scroll. Entregue o hook **já escrito** no brief, não só "o papel narrativo". Use uma das 5 fórmulas:

| Fórmula | Quando funciona | Exemplo |
|---------|-----------------|---------|
| **Afirmação polêmica** | desafia crença comum do vertical | "Você está fazendo skincare errado" |
| **Número + benefício** | educativo / listicle | "7 sinais de que você precisa rever sua rotina" |
| **Pergunta que dói** | toca em dor real do público | "Por que seu negócio ainda não tem agenda cheia?" |
| **Resultado concreto** | prova social / case | "Como triplicamos os resultados em 30 dias" |
| **Inversão de expectativa** | educativo com viés contraintuitivo | "Trabalhar mais não vai melhorar sua performance" |

### Regras do hook

- **Nunca** comece com o nome da marca como headline ("Marca X apresenta…" é frio).
- O hook deve **prometer um valor** que os slides seguintes entregam — não invente promessa que o conteúdo não cumpre.
- Prefira hooks que admitam **prova visual** no slide (foto, número, frase curta) quando aplicável.
- Em **Single-post**, o hook é o ponto central da arte (ex: o título principal do post de Dia das Mães).
- Em **Tutorial** e **Listicle**, o hook do Slide 1 pode usar a estrutura "Número + benefício" ou "Pergunta que dói" alinhada ao número de itens.

## Carousel chrome (opcional)

Progress bar (3px no rodapé) + seta de swipe à direita ajudam em carrosséis longos onde o leitor pode se perder. **Não é default.** Aplicar em todo template torna a UI repetitiva e compete visualmente com o conteúdo. A escolha é feita por **avaliação qualitativa**, não tabela mecânica por sequência.

Valores possíveis para `## Carousel chrome` no brief:

| Valor | Significado |
|-------|-------------|
| `yes` | Designer adiciona progress bar + seta em todos os slides exceto o último |
| `no` | Designer **não** adiciona chrome |
| `auto` | Interpreter decide caso a caso (ver critério abaixo) |

### Como decidir em modo `auto`

**Sinais explícitos do user vencem sempre:**

| Sinal no pedido | Decisão |
|-----------------|---------|
| User pediu "progress bar", "barra de progresso", "indicador de slides", "contador", "navegação", "seta de swipe" | `yes` |
| User pediu "limpo", "minimalista", "sem distração", "premium", "clean", "sem elementos extras" | `no` |
| Reference-driven mode + a referência mostra progress bar/setas/contador "1/N" | `yes` (force, anote no brief) |
| Reference-driven mode + referência sem chrome de navegação visível | `no` (force, anote no brief) |

**Sem sinal explícito**, decida pesando 3 critérios. Aplique chrome **somente se 2 dos 3 forem verdadeiros**:

1. **Volume**: `≥ 6 slides`. Carrosséis curtos (≤ 5) o leitor mantém orientação naturalmente — Instagram já mostra os pontos no topo.
2. **Tom didático sequencial**: o conteúdo é uma progressão real (passo 1 → passo 2 → ... → passo N de um tutorial; "5 sinais que..." enumerado; "antes do exame, durante, depois"). Não é didático sequencial: educação solta sem ordem rígida, post de citação, lista de benefícios sem numeração, mensagem de marca, data comemorativa.
3. **Ausência de outros indicadores visuais de progresso**: se o template já tem número grande de slide (`01/07`, `Passo 3 de 5`, eyebrow numerado), chrome adicional é redundância. Aplique chrome só se o conteúdo não auto-numerar.

**Exemplos práticos:**

| Pedido | Slides | Análise | Decisão |
|--------|--------|---------|---------|
| "Carrossel sobre nutrição infantil" | 5 | Volume: ✗ (5). Didático: ✓. Sem auto-numeração: ✓ → 2/3, mas falha volume. | `no` |
| "Tutorial de skincare em 7 passos" | 7 | Volume: ✓ (7). Didático: ✓ (passos). Sem auto-numeração: a depender do design. | `yes` |
| "5 sinais de que você precisa de fisio" | 5 | Volume: ✗. Didático: ✓ (enumerado). Sem auto-numeração: ✗ (vai ter "01"..."05"). | `no` |
| "Comparação plano A vs plano B" | 5 | Volume: ✗. Didático: ✗ (paralelo, não sequencial). | `no` |
| "Carrossel educativo longo sobre menopausa, 8 slides" | 8 | Volume: ✓. Didático: ✓. Sem auto-numeração: ✓ provável. | `yes` |
| "Post de feliz dia das mães" | 1 | Single-post. | `no` |
| "Carrossel premium minimalista sobre estética facial" | 6 | Volume: ✓. Mas user pediu "premium minimalista" = sinal explícito. | `no` |

**Regra de proporção esperada**: em pedidos genéricos (sem sinal forte), espere ~30% dos templates terminarem com `yes`. Se você está marcando `yes` em mais que isso, está caindo no viés antigo.

**Em qualquer dúvida, prefira `no`.** Falta de chrome nunca quebra um carrossel; chrome em carrossel curto/inadequado polui sempre.

## Output

### `brief.md` (sempre)

Write `artifacts/gp2-request-interpreter/<slug>/brief.md`:

```markdown
# Brief — <título curto>

## Modo
<free | reference-driven>

## Entrega
- Tipo: <post | carrossel | story | reel cover | ad>
- Dimensões: <ex: 1080x1350>
- Slides: <N>

## Segmento
<vertical da marca inferido do pedido — slug em kebab-case, ex: clinicas-medicas, ecommerce-moda, academias, restaurantes, tech-saas, etc.>

## Sequência
<Standard | Listicle | Tutorial | Comparação | Single-post>
<por que essa escolha em 1 linha>

## Hook
- Fórmula: <Afirmação polêmica | Número + benefício | Pergunta que dói | Resultado concreto | Inversão>
- Copy: "<o hook escrito de fato em 1 linha>"

## Carousel chrome
<yes | no | auto>
<se auto, em qual valor a sequência resolve>

## Arco narrativo
- Slide 1 (capa): <papel narrativo + background sugerido (LIGHT/DARK/Brand)>
- Slide 2: <... + background>
- Slide N (CTA): <... + background>

## Cores de marca
- Quantidade: <primária somente | primária + secundária>
- Papel da primária: <ex: cor de destaque dominante | fundo principal | CTA>
- Papel da secundária (se aplicável): <ex: acento de apoio | destaque em palavra-chave>

## Foto profissional
- Decisão: <usar | não usar | condicional ao pedido do usuário>
- Justificativa: <1 linha>
- Placeholder sugerido: <professional-photo-1 (masculino, jaleco) | professional-photo-2 (feminino, casual) | n/a>
- Posição sugerida: <hero cover | CTA final | overlap sobre foto contextual | outra | n/a>

## Tom / copy
<2-3 linhas sobre voz: educativo? promocional? acolhedor? técnico?>

## Referência visual
<se reference-driven: "imagem(ns) de referência anexada(s) — análise visual será feita pelo gp2-art-director">
<se free: "nenhuma">

## Incertezas
<só liste se travariam o designer>
```

Mantenha curto. Uma página. Tudo que ultrapassa vira ruído para o designer.

## Decisão de foto profissional

Use foto profissional quando:

- o pedido explicitamente pede foto do usuário/profissional;
- o asset depende de presença humana para gerar confiança (apresentação, CTA com nome do profissional, "agendar consulta com Dr. …");
- a referência anexada usa retrato real como peça central da composição.

Não use foto profissional quando:

- o conteúdo é educacional/informativo e a foto seria ruído decorativo;
- a referência é tipográfica, infográfica ou abstrata;
- a foto reduziria a clareza do conteúdo.

Em condicional: declare a regra ("usar somente se o usuário enviar foto") para o designer reservar área correta.

### Placeholder sugerido (quando há foto profissional)

Sugira ao designer qual placeholder usar. O designer embute a base64 inline no `template.html`; em produção o runtime troca pela foto real do usuário.

Há dois placeholders disponíveis — escolha pelo perfil mais provável do profissional da marca:

| Placeholder | Perfil |
|-------------|--------|
| `professional-photo-1.b64.txt` | Masculino, traje formal/jaleco |
| `professional-photo-2.b64.txt` | Feminino, traje casual/blazer |

Inferir pelo contexto do pedido: segmentos com predominância de profissionais de jaleco (medicina, odontologia, laboratório) → photo-1; segmentos com predominância casual ou feminino (bem-estar, nutrição, psicologia, moda) → photo-2; ambíguo → qualquer um. Em **reference-driven mode**, priorize o perfil que a referência mostra e anote no brief.

### Posição sugerida

Sugira no `brief.md` qual das 3 posições estratégicas combina melhor com o pedido (catálogo completo em [`gp2-html-designer/references/professional-photo-placements.md`](../gp2-html-designer/references/professional-photo-placements.md)):

- **Hero cover full-figure** — quando o slide 1 deve apresentar o profissional/marca antes de qualquer mensagem educativa ("Conheça o Dr. João", "Sou a Dra. Maria, especialista em…").
- **CTA final lateral** — quando o último slide é "agende com" e o nome do profissional aparece na chamada.
- **Overlap sobre foto contextual** — quando há foto de ambiente/espaço/asset que ganha com presença humana ancorando a cena (mostrar o espaço + quem atende, equipamento + quem opera).
- **Outra** — defina livremente se nenhuma das 3 cabe (ex: avatar circular pequeno em assinatura).

Em templates com 2+ slots de foto profissional (ex: hero cover no slide 1 + CTA no slide N), use a mesma combinação em todos para o produto mostrar a foto real do usuário consistentemente.

## Decisão de quantas cores de marca

Use **somente primária** quando:

- o design pede impacto monocromático;
- só um elemento precisa trocar com o preset de marca;
- o vertical sugere paleta enxuta (marcas premium, serviços de alta percepção de valor).

Use **primária + secundária** quando:

- existem dois papéis visuais distintos que precisam trocar com presets (ex: fundo + CTA);
- a referência tem dois acentos claros;
- o conteúdo se beneficia de contraste forte entre dois pontos de marca (ex: comparações, antes/depois educativo).

Neutros (branco, preto, cinza) **nunca** são contados como brand color.

## Resposta final ao orquestrador

```markdown
Modo: <free | reference-driven>
Brief gerado: `<path>/brief.md`
Referência visual: <"imagem(ns) anexada(s) — análise visual no próximo passo (art-director)" | "nenhuma">
Sequência: <Standard | Listicle | Tutorial | Comparação | Single-post>
Slides: <N>
Hook: "<copy do hook em 1 linha>" (<fórmula>)
Carousel chrome: <yes | no> (resolvido)
Cores de marca: <primária | primária+secundária>
Foto profissional: <usar | não usar | condicional>
Próximo passo: gp2-art-director
```

Nada além disso. Sem resumo do conteúdo dos arquivos — o orquestrador lê.
