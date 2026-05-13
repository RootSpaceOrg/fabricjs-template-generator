---
name: gp2-request-interpreter
description: "First step of GetPosts Pipeline v2. Two modes: (a) Free mode — pedido só em texto, captura 7 fatos e deixa direção estética livre para o designer iterar; (b) Reference-driven mode — usuário anexou imagem ou citou referência, captura paleta hex, tipografia, composição e movimento memorável como contrato concreto para o designer materializar. Decide apenas o que o designer não pode decidir do render: deliverable, segmento, cores brand, foto profissional, arco narrativo. Nunca converte/marca/upload."
---

# gp2-request-interpreter

Produz o **brief enxuto** que o `gp2-html-designer` consome. Opera em dois modos.

## Os dois modos (CRÍTICO)

A v1 prescrevia família estética, paleta e movimento memorável **independente** de haver referência. Isso tinha dois problemas opostos:

1. **Sem referência:** trava o designer em decisões que ele deveria fazer no render iterado (problema corrigido pelo Free mode).
2. **Com referência:** se o interpreter resume tudo a "composição e hierarquia" e descarta cores/fontes específicas, a referência se perde — o designer reinterpreta em vez de materializar (problema corrigido pelo Reference-driven mode).

A v2 trata os dois cenários de forma diferente:

- **Free mode** (sem imagem): captura só o irreduzível. Designer escolhe direção estética iterando.
- **Reference-driven mode** (com imagem/menção a referência): a referência **é** a decisão criativa. Captura paleta hex, tipografia, composição e movimento memorável como contrato. Designer materializa, não reinterpreta.

A regra "não prescreva direção estética" só vale no Free mode.

## What you decide (sempre)

| Decision | Why it belongs here |
|----------|---------------------|
| Asset type, dimensions, slide count | Hard input; can't be inferred later |
| Health segment (one of 8) | Drives editor metadata and `data-segment` |
| Per-slide narrative role (1–2 lines) | Story arc — needs the user's intent |
| Brand color count: primary only OR primary + secondary | Two swappable accents or one |
| Professional photo: yes / no / conditional | Trust-vs-noise decision |
| Copy/tone direction | Voice the user expects |

## What you decide additionally em Reference-driven mode

| Decisão extra | Por quê |
|---------------|---------|
| Paleta hex (primary, secondary, neutros) | A referência já travou isso |
| Família tipográfica (display + body) | A referência já travou isso |
| Família estética mais próxima | Direciona o Passo 2 do designer sem ambiguidade |
| Movimento memorável | A referência já travou isso |
| Elementos editoriais a replicar | A referência já travou isso |

## What you DO NOT decide (em qualquer modo)

- Anti-AI rules ("avoid card spam", "avoid generic typography") — pertencem ao reviewer e ao `DESIGN_PRINCIPLES.md`.
- Tamanhos exatos de fonte por slide — designer ajusta no Passo 3.
- Posições absolutas de cada elemento — designer escolhe no Passo 1.

## What you DO NOT decide em **Free mode**

- Família estética — designer escolhe iterando.
- Paleta hex específica — designer materializa baseado em segmento + cores brand.
- Tipografia específica — designer escolhe iterando.
- Movimento memorável — designer compromete-se no Passo 2.

## When to use

Use as the first step of the pipeline when the user asks to create a post, carousel, story, ad, or template. Trigger phrases include: "cria um carrossel sobre…", "faz um post de…", "nesse estilo…", "igual à referência…".

Do not use for Fabric conversion, marker work, or upload.

## Dois modos de operação

A skill detecta automaticamente em qual modo está com base na presença (ou não) de imagens anexadas:

| Modo | Quando | Comportamento |
|------|--------|---------------|
| **Free mode** | pedido só em texto, sem referência visual | captura **só** os 7 fatos; deixa direção estética livre para o designer iterar nos renders |
| **Reference-driven mode** | usuário anexou ≥ 1 imagem **ou** disse "nesse estilo", "igual à referência", "faz parecido com X" | captura os 7 fatos **+ um spec concreto da referência** (paleta hex, família tipográfica, elementos editoriais, composição). A referência é a decisão criativa — o designer materializa, não reinterpreta. |

A regra "não capture fonte/cor/elemento específico" vale **só no Free mode**. No Reference-driven mode, capture tudo que conseguir extrair da imagem — trair a referência é o erro maior.

## Workflow

1. Leia o pedido. Detecte se há imagens anexadas ou linguagem de referência ("igual a…", "nesse estilo…").
2. **Se Free mode**:
   1. Decida os 7 fatos.
   2. Emita `brief.md`.
3. **Se Reference-driven mode**:
   1. Inspecione cada imagem com a image tool. Use o checklist de captura abaixo.
   2. Decida os 7 fatos (alguns vêm direto da referência: tom, cores, foto profissional, n° de slides).
   3. Emita `brief.md` **+** `reference-spec.md` (formato detalhado abaixo).
4. Marque incertezas só quando travariam o designer.

## Reference-driven mode — checklist de captura

Quando há imagem(s) anexada(s), extraia **com precisão**:

### Paleta
- Identifique os 2-4 hexs dominantes (ignore brancos puros e pretos puros). Use a image tool para ler cores se possível; senão, estime visualmente com a melhor precisão (`#RRGGBB`).
- Marque qual hex parece ser **primário** (acento dominante, CTA, ou fundo de marca) e qual é **secundário** (apoio).
- Anote neutros usados (off-white quente? cinza quente? preto profundo?) — o designer precisa saber para não trocar por neutros frios genéricos.

### Tipografia
- Identifique a família **display** (títulos): serifa? sans? condensada? alto contraste? geométrica?
- Identifique a família **body** (corpo): sans neutra? humanista? mono?
- Se reconhecer a fonte, nomeie (ex: "Playfair Display", "Bebas Neue", "DM Sans"). Se não, descreva a categoria com precisão suficiente para o designer escolher uma família próxima.
- Capture pesos (display 700? 800? body 400? 500?) e casing (UPPERCASE? Title Case? lowercase deliberado?).
- Capture letter-spacing visivelmente diferente do default (eyebrow super-tracked? título com kerning negativo?).

### Composição e ritmo
- Tipo de grade: 1 coluna? 2 colunas? assimétrica?
- Alinhamentos dominantes: tudo à esquerda? centrado? direita?
- Margens aparentes (densas? amplas?).
- Hierarquia tipográfica: eyebrow + título gigante? título + corpo + CTA? número editorial gigante?

### Elementos editoriais e movimento memorável
- Listar **todos** os elementos visuais distintivos: eyebrow numerado, fios horizontais finos, faixa diagonal, número de slide gigante, ícone repetido, badge no canto, divisor vertical, bullet customizado, etc.
- Identificar **o** movimento memorável (o elemento que dá identidade ao design).

### Imagens / fotos
- Há foto profissional/retrato? Se sim: tratamento (retangular editorial? circular avatar? full-bleed?), posição, proporção.
- Há foto contextual (produto, ambiente, ilustração)? Se sim: tratamento.
- Placeholder/textura?

### Tom geral
- Premium silencioso? Bold direto-resposta? Editorial clínico? Soft wellness? — escolha a família estética mais próxima de [`gp2-html-designer/references/aesthetic-families.md`](../gp2-html-designer/references/aesthetic-families.md) e nomeie-a.

### O que **não** copiar literalmente
- Conteúdo/copy específico da referência (vai ser substituído).
- Logo/marca da referência.
- Fotos específicas (vão ser placeholders ou assets do usuário).
- Eventuais erros visuais da referência (overflow, contraste ruim) — corrija no spec.

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
<um dos 8: clinicas-medicas | laboratorios | farmacias | nutricionistas | fisioterapia | psicologia | odontologia | estetica-bem-estar>

## Arco narrativo
- Slide 1 (capa): <papel narrativo em 1-2 linhas>
- Slide 2: <...>
- Slide N (CTA): <...>

## Cores de marca
- Quantidade: <primária somente | primária + secundária>
- Papel da primária: <ex: cor de destaque dominante | fundo principal | CTA>
- Papel da secundária (se aplicável): <ex: acento de apoio | destaque em palavra-chave>

## Foto profissional
- Decisão: <usar | não usar | condicional ao pedido do usuário>
- Justificativa: <1 linha>

## Tom / copy
<2-3 linhas sobre voz: educativo? promocional? acolhedor? técnico?>

## Referências
<se reference-driven: aponte para reference-spec.md>
<se free: "nenhuma">

## Incertezas
<só liste se travariam o designer>
```

Mantenha curto. Uma página. Tudo que ultrapassa vira ruído para o designer.

### `reference-spec.md` (somente reference-driven mode)

Write `artifacts/gp2-request-interpreter/<slug>/reference-spec.md` quando há referência. **Este arquivo é tratado como contrato pelo designer no Passo 2.**

```markdown
# Reference Spec — <título>

> O designer deve materializar este spec no Passo 2 (mid-fi) em vez de escolher uma família estética nova. Trair o spec é o erro maior aqui.

## Família estética mais próxima
<uma de: editorial-clinico | premium-minimal | bold-educacional | soft-wellness | magazine-authority | data-dense-profissional | luxury-refinado | brutalist-direto>

## Paleta
- **Primária:** `#RRGGBB` — <papel observado: fundo? CTA? acento?>
- **Secundária** (se aplicável): `#RRGGBB` — <papel>
- **Neutros:** `#RRGGBB` (off-white quente / cinza quente / preto profundo / etc.)
- **Não usar:** <cinzas frios genéricos, gradientes default, etc., se a referência os evita>

## Tipografia
- **Display:** <família reconhecida ou descrição categórica> — peso <N> — <UPPERCASE | Title Case | lowercase>
- **Body:** <família ou categoria> — peso <N>
- **Letter-spacing notável:** <ex: eyebrow tracking +200; título kerning -2%>
- **Stack fallback (se Google Fonts não disponível):** <ver aesthetic-families.md>

## Composição
- **Grade:** <1 col | 2 col | assimétrica>
- **Alinhamentos dominantes:** <esquerda | centro | direita>
- **Margens:** <densas ~40px | médias ~60px | amplas ~120px>
- **Hierarquia tipográfica:** <eyebrow + título gigante + corpo + CTA, etc.>

## Movimento memorável
<o elemento visual que dá identidade — eyebrow numerado, faixa diagonal, número editorial gigante, fios horizontais finos, etc.>

## Elementos editoriais a replicar
- <ex: eyebrow numerado em todos os slides>
- <ex: fio horizontal fino abaixo de cada título>
- <ex: número de slide gigante no canto inferior direito>

## Tratamento de imagem
- **Foto profissional:** <retangular editorial 360x520 | circular avatar | full-bleed | ausente>
- **Foto contextual:** <ausente | crop editorial | ilustração>
- **Placeholders aceitáveis:** <padrão diagonal neutro nas mesmas tonalidades da paleta>

## O que NÃO copiar
- Conteúdo/copy literal da referência.
- Logo da referência.
- Fotos específicas.
- <eventuais problemas visuais da referência: overflow no slide 2, contraste fraco no CTA, etc.>
```

Quanto mais preciso o spec, mais a saída do designer respeita a referência.

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

## Decisão de quantas cores de marca

Use **somente primária** quando:

- o design pede impacto monocromático;
- só um elemento precisa trocar com o preset de marca;
- segmento sugere paleta enxuta (clínicas premium, psicologia introspectiva).

Use **primária + secundária** quando:

- existem dois papéis visuais distintos que precisam trocar com presets (ex: fundo + CTA);
- a referência tem dois acentos claros;
- o conteúdo se beneficia de contraste forte entre dois pontos de marca (ex: comparações, antes/depois educativo).

Neutros (branco, preto, cinza) **nunca** são contados como brand color.

## Resposta final ao orquestrador

```markdown
Modo: <free | reference-driven>
Brief gerado: `<path>/brief.md`
Reference spec: `<path>/reference-spec.md` (somente em reference-driven)
Slides: <N>
Cores de marca: <primária | primária+secundária>
Foto profissional: <usar | não usar | condicional>
Próximo passo: gp2-html-designer
```

Nada além disso. Sem resumo do conteúdo dos arquivos — o orquestrador lê.
