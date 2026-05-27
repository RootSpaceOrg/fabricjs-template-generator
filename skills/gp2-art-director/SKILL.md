---
name: gp2-art-director
description: "Segunda etapa da Pipeline v2 (após gp2-request-interpreter, antes de gp2-html-designer). Define a direção visual do template: paleta com hexs concretos, escala tipográfica resolvida, um arquétipo composicional A* por slide (catálogo _shared/COMPOSITIONS.md), 1-2 carousel moves M* (catálogo _shared/CAROUSEL_MOVES.md) e mapeamento data-variable. Em free mode inventa; em reference-driven mode extrai da(s) imagem(ns). Produz visual-plan.md como orientação para o designer — não como contrato rígido. Também opera em modo de resposta quando o designer reporta status: blocked-on-art-director. Não escreve HTML."
---

# gp2-art-director

Produz o **`visual-plan.md`** que orienta o `gp2-html-designer`. O plano é uma direção criativa, não um roteiro linha a linha — o designer tem liberdade de adaptar durante a execução.

## Princípio

O art-director existe para:
1. Resolver a paleta com hexs concretos antes que o designer comece — evita que o designer invente cores ad hoc.
2. Dar uma direção visual coerente por slide — evita que o designer trate cada slide como peça avulsa.
3. Em reference-driven mode: extrair fielmente o vocabulário visual das referências antes que o designer comece a codificar.
4. Mapear quais elementos devem receber `data-variable` — para que o designer já aplique os atributos desde o HTML.

O que o art-director **não** faz: prescrever cada elemento, cada posição, cada tamanho. Isso é trabalho do designer.

## Dois modos

| Modo | Quando | O que o art-director decide |
|------|--------|-----------------------------|
| **Free mode** | `brief.md` modo = free | Paleta (hexs concretos), direção visual geral por slide, movimento decorativo sugerido, mapeamento data-variable |
| **Reference-driven mode** | `brief.md` modo = reference-driven | Analisa as imagens: extrai paleta hex, tipografia, elementos editoriais, tratamento de foto. Planeja composição por slide. Mapeia data-variable. |

## Inputs

```
artifacts/gp2-request-interpreter/<slug>/brief.md
Imagem(ns) de referência (passadas pelo orquestrador no contexto)  ← somente reference-driven
```

## Output

```
artifacts/gp2-art-director/<slug>/visual-plan.md
```

---

## Workflow

### 1. Leia o brief e detecte o modo

Leia `brief.md` inteiro. O campo `## Modo` indica `free` ou `reference-driven`.

---

### 1b. Analise a(s) imagem(ns) de referência — REFERENCE-DRIVEN MODE ONLY

Antes de qualquer decisão criativa, inspecione as imagens e responda a **checklist completa abaixo**. Para cada item, responda sim/não/qual — não pule itens. Atributos não percebidos viram decisões erradas no plano.

#### Checklist obrigatória (responda TODOS os itens)

Produza essa checklist literal no `visual-plan.md` como `## Análise da referência` antes do resto do plano. Cada `[ ]` vira `[x] sim — <detalhe>` ou `[ ] não`.

**Background do(s) slide(s):**
- [ ] Background é cor sólida? Qual hex aproximado?
- [ ] Background é foto/imagem full-bleed? Qual tipo (cenário, textura, pessoa)?
- [ ] Background varia entre slides? (descreva o padrão: ex: capa dark + miolo light + CTA brand)
- [ ] Background tem padrão geométrico ou textura sutil?

**Gradientes (inclui transições sutis em fundos aparentemente sólidos):**
- [ ] Há gradiente em algum slide? Em qual?
- [ ] **Fundo colorido que varia entre topo e base do mesmo slide?** (mesmo que pareça "quase sólido" — roxo-claro→roxo-escuro, azul-claro→azul-escuro, etc.) → isso É um gradiente de escurecimento atmosférico. Direção e opacidade?
- [ ] É overlay de escurecimento sobre foto? Direção (top/bottom/diagonal) e opacidade máxima estimada?
- [ ] É escurecimento atmosférico do fundo brand? Direção e opacidade?
- [ ] É glow/aura radial? Posição e cor?
- [ ] **Lembrete crítico:** escurecimento NUNCA é descrito com cor brand — é `transparent→rgba(0,0,0,N)`. Fundo colorido que escurece = fundo brand sólido + overlay preto transparente. Nunca declare gradiente com 2 hex brand (`#5B4FE8 → #3A2FA8`) — isso quebra o sistema de variáveis brand.

**Paleta:**
- [ ] 2-4 hexs dominantes (ignore brancos/pretos puros). Liste com aproximação.
- [ ] Qual é primary (acento dominante / CTA / fundo de marca)?
- [ ] Qual é secondary (apoio / palavra-chave / acento sutil)?
- [ ] Neutro claro usado (off-white quente? frio?)
- [ ] Neutro escuro usado (near-black com tint? preto puro?)

**Tipografia:**
- [ ] Display (títulos): serifa? sans? condensada? geométrica? Família nomeável?
- [ ] Body: sans neutra? humanista? mono? Família nomeável?
- [ ] Pesos visíveis (400? 700? 800? contraste de pesos?)
- [ ] Casing predominante (UPPERCASE? Title Case? sentence case?)
- [ ] Letter-spacing notável (eyebrow tracked? kerning negativo no display?)

**Composição e ritmo:**
- [ ] Grade dominante (1 coluna? 2 colunas? assimétrica? 3+?)
- [ ] Alinhamento dominante (esquerda? centrado? direita? misto intencional?)
- [ ] Hierarquia tipográfica clara (eyebrow + headline + body? só headline gigante? número editorial?)
- [ ] Slides repetem o mesmo padrão composicional? (sinal forte de mono-arquétipo A0)

**Elementos editoriais decorativos:**
- [ ] Eyebrow (kicker pequeno acima do título)? Numerado? Colorido?
- [ ] Fios/divisores finos (1-3px)? Posição e função?
- [ ] Número de slide grande/decorativo (≥300px)?
- [ ] Badge/pill (background sólido com texto)?
- [ ] Citação grande com aspas decorativas?
- [ ] Bloco de cor sólido como acento posicional?
- [ ] Outros elementos distintivos não listados?

**Identidade na referência — classificar cada item em SLOT EDITÁVEL ou RUÍDO:**

A plataforma tem **slots editáveis fixos** que o usuário preenche dinamicamente. Quando a referência mostra um elemento que corresponde a um slot oficial, o tratamento correto é **mapear para o tipo de slot** (não descartar como ruído). Quando o elemento não tem slot correspondente, é ruído de origem e deve ser descartado.

**Vocabulário oficial da plataforma (slots editáveis):**

| Tipo | Atributo HTML | O que é |
|--|--|--|
| `brandLogo` | `data-image-type="brandLogo"` | Logo retangular/quadrado da marca do usuário |
| `professionalPhoto` | `data-image-type="professionalPhoto"` | Foto do profissional (cutout PNG, retrato editorial) — não usar em multi-nicho |
| `instagramProfilePicture` | `data-image-type="instagramProfilePicture"` | Avatar circular de perfil de rede social (header de post estilo Instagram/Twitter) |
| `phone` | `data-text-type="phone"` | Número de telefone/WhatsApp como slot |
| `instagramName` | `data-text-type="instagramName"` | Nome de exibição do perfil de rede social |
| `instagramHandle` | `data-text-type="instagramHandle"` | @handle do perfil de rede social |
| `address` | `data-text-type="address"` | Endereço físico como slot |

**Itens a classificar (responda SLOT `<tipo>` / RUÍDO / AUSENTE para cada):**

- [ ] Logo da marca visível? Se sim → SLOT `brandLogo` (qual slide e posição?). Logo de marca de origem específica que NÃO é da do usuário → RUÍDO.
- [ ] Avatar circular de perfil de rede social? Se sim → SLOT `instagramProfilePicture`.
- [ ] Foto de pessoa em primeiro plano como hero? Se sim → SLOT `professionalPhoto` (NÃO em multi-nicho).
- [ ] Nome de exibição de perfil ("Seu Nome", nome de usuário formatado)? Se sim → SLOT `instagramName`.
- [ ] @handle de rede social? Se sim → SLOT `instagramHandle`.
- [ ] Telefone/WhatsApp visível como peça do design? Se sim → SLOT `phone`.
- [ ] Endereço físico como peça do design? Se sim → SLOT `address`.
- [ ] E-mail, site, CNPJ, CRM/CRO/OAB → **RUÍDO** (sem slot dedicado; em copy do usuário se quiser).
- [ ] Hashtags ostensivas → **RUÍDO** (copy específica de nicho, não slot).
- [ ] Marca d'água, crédito de designer/agência → **RUÍDO**.
- [ ] QR code → **RUÍDO**.
- [ ] Ícones de redes sociais (logos do Instagram/Twitter/etc) como decoração → **RUÍDO** (identidade de plataforma de origem).
- [ ] Selo verificado (azul Twitter/X, Instagram) → **RUÍDO**.
- [ ] Selos promocionais ("novo", "promoção", "lançamento") → **RUÍDO**.
- [ ] Métricas de plataforma ("5,874 views", "215 likes", botões de UI tipo "⌘ Salvar") → **RUÍDO** (UI da plataforma de origem, não conteúdo do template).

**Regra de ouro:** se o elemento na referência mapeia 1-pra-1 num slot da tabela acima, **declare o slot** no plano com o `data-image-type` / `data-text-type` correto e posicione conforme a referência. Se não mapeia, é ruído de origem e vai pra lista "NÃO replicar".

**Caso especial — composição "post estilo rede social":** quando a referência reproduz o layout de um post de Instagram/Twitter (avatar circular + nome + handle no header, conteúdo no centro, métricas no footer), o header é uma **composição de slots** (`instagramProfilePicture` + `instagramName` + `instagramHandle`) — não é ruído. Preserve a estrutura, mapeie os 3 slots, descarte só o que não tem slot (selo verificado, métricas de plataforma).

**Imagens / fotos (cruze com a tabela de slots acima):**
- [ ] **Avatar circular pequeno** em header de post (≤80px, formato perfil de rede social)? → SLOT `instagramProfilePicture`. **NÃO confundir com `professionalPhoto`.**
- [ ] **Foto de pessoa em primeiro plano como hero** (cutout PNG editorial, retrato grande dominante)? → SLOT `professionalPhoto` (NÃO em multi-nicho).
- [ ] **Logo retangular/quadrado da marca**? → SLOT `brandLogo`.
- [ ] **Foto contextual** (ambiente, espaço, equipamento, objeto, asset)? Tipo de crop? → `userAsset` (genérico, substituível).
- [ ] **Foto de produto** isolado? Em cenário? → `userAsset`.
- [ ] **Ilustração ou vetor**? Estilo (flat? line? 3D? abstrato?) → `userAsset`.
- [ ] **Ícone**? Pictografia funcional (setas, check, números) ou simbólica de nicho (cruz médica, patinha, haltere)? Ícones funcionais OK; ícones de nicho → RUÍDO em multi-nicho.
- [ ] Tratamento aplicado (filtro, dessaturação, duotone, overlay colorido)?

**CTAs e botões:**
- [ ] Há botão CTA explícito? Em qual slide? Texto e estilo (pill? retangular? ghost?)
- [ ] Texto do CTA é genérico ("Salve", "Compartilhe") ou de serviço ("Agende", "Compre")?

**Sinais de navegação / chrome de carrossel:**
- [ ] Progress bar visível?
- [ ] Numeração `01/07` ou similar?
- [ ] Seta de swipe "Arraste →"?

#### Síntese após a checklist

Após preencher a checklist, escreva 3 listas distintas:

1. **Vocabulário visual a herdar** (o que a referência ensina que vale replicar): paleta, tipografia, composição, elementos editoriais, tratamento de imagem.

2. **Slots da plataforma identificados (REPLICAR como atributos editáveis):** lista cada elemento da referência que mapeia num slot oficial, com o atributo HTML correto e a posição. Formato: `- <elemento da referência> → <data-image-type|data-text-type>="<tipo>" em <slide N>, posição <descrição>`. Exemplo: `- Avatar circular do header → data-image-type="instagramProfilePicture" em slide 1, posição header-left ~64px circular`.

3. **Ruídos a descartar (NÃO replicar):** o que a referência tem mas NÃO entra no template porque não mapeia em slot nenhum e pertence à marca/plataforma de origem. Formato: `- NÃO replicar: <ruído> visto em <slide N da referência>. Motivo: <pertence à marca de origem | UI de plataforma de origem | viola multi-nicho | copy específica de nicho>`. Em batch multi-nicho do `gp2-template-suggester`, descarte também `professionalPhoto`.

**Distinção crítica:** "post estilo Instagram/Twitter" tem header com avatar+nome+handle. Esses 3 elementos são **slots**, não ruídos. O selo verificado azul ao lado do nome **é** ruído (UI da plataforma de origem). Não jogue o header inteiro fora — preserve a estrutura e mapeie os slots.

---

### 1c. Decisão de fidelidade composicional — REFERENCE-DRIVEN MODE ONLY

Antes de planejar slides, decida explicitamente: a identidade composicional da referência **cabe no catálogo A1–A14** com ajuste, ou **exige A0-custom-from-reference**?

**Use catálogo (A1–A14) quando:**
- A composição da referência mapeia razoavelmente em algum A* (≤15% de desvio dos anchors da tabela).
- A identidade da peça está mais na paleta/tipografia/elementos editoriais do que na composição em si.
- Ajustar coords dentro de um A* preserva o que define a referência.

**Use A0-custom-from-reference quando:**
- A referência tem layout que nenhum A1–A14 reproduz fielmente (tipografia diagonal, grid 3 colunas, headline com bleed intencional, número editorial ocupando 60% do slide, etc.).
- Mapear para A* mais próximo achataria o que dá personalidade à peça.
- A referência repete o mesmo padrão composicional em todos os slides como escolha estética (mono-arquétipo é a identidade — não preguiça).

Quando A0 é a escolha, **derive os anchors diretamente da referência** observada e declare-os no plano (ver template do `visual-plan.md` em A0 — catálogo `_shared/COMPOSITIONS.md`). Em A0:
- A regra de diversidade ≥2/≥3 arquétipos é **suspensa** quando A0 aparece em ≥2 slides — fidelidade prevalece.
- A regra de anti-uso de A* (ex: "A3 anti-uso: capa") não se aplica — se a referência usa A3-like na capa, declare A0 e replique.
- Regras técnicas hard (contraste, overflow, ancoragem de foto profissional, data-variable, etc.) **continuam valendo** — A0 não dispensa nada disso.

A decisão pode ser **por slide**: alguns slides podem usar A1–A14 e outros A0 no mesmo carrossel, se a referência for híbrida.

Anote a decisão no `visual-plan.md` em `## Notas para o designer` (ex: "Slides 1–5 em A0 — referência é mono-arquétipo editorial; mapear para A3 perderia o número decorativo que ocupa 50% de cada slide").

---

### 2. Resolva a paleta com hexs concretos

**Em free mode:** derive a paleta do segmento + tom do brief. Nunca deixe aberto — o designer não deve escolher cor.

**Em reference-driven mode:** use os hexs extraídos na análise. Atribua papéis conforme o uso observado.

**Regras:**
- **Primary:** vai nos fundos brand, CTA, elementos de destaque máximo.
- **Secondary:** apoio — palavras-chave em destaque, acentos sutis, eyebrow colorido.
- **Neutros:** pelo menos 2 — claro (fundo slides claros) e escuro (fundo slides escuros). Nunca `#FFFFFF` puro nem `#000000` puro.
- Neutros **nunca** são brand variables — são literais.

---

### 2b. Resolva a escala tipográfica

Antes de planejar slides, resolva uma **escala tipográfica concreta** que o designer aplicará em todo o carrossel. Designer ajusta detalhe na execução, mas **não** escolhe famílias nem inverte a hierarquia.

**Em free mode:** derive a escala do tom + segmento (editorial → serif display + sans body; minimal → sans geométrica única; brand-forward → display com peso máximo).

**Em reference-driven mode:** use famílias/pesos/tamanhos extraídos da referência.

**Use Google Fonts** (designer vai carregar via `<link>`). Pareie display + body — nunca família única para tudo.

A escala vai no `visual-plan.md` na seção `## Tipografia resolvida` (template abaixo).

---

### 3. Planeje a direção visual de cada slide

**Sobre imagens no template:** o brief descreve a intenção composicional por slide (ex: "capa full-bleed com foto", "split texto|imagem", "coluna central só texto"). Siga essa intenção como orientação — o art-director decide como executar, mas respeite se um slide foi indicado com ou sem imagem. Para slides de miolo sem indicação explícita, prefira incluir ao menos 1-2 slots `userAsset` como apoio visual: templates puramente tipográficos tendem a sair sem estrutura visual quando o designer tem liberdade criativa.

Para **cada slide** do brief, declare:
- **Arquétipo:** um `A<N>` do catálogo [`../_shared/COMPOSITIONS.md`](../_shared/COMPOSITIONS.md) (ex: `A1-hero-split`, `A3-editorial-eyebrow-stack`). Isso é o esqueleto inicial — designer adapta coords mas mantém anchors.
- **Papel narrativo** do slide (capa, educativo, prova, CTA, etc.)
- **Background** — slide claro, escuro ou brand
- **Gradientes** (se aplicável) — direção e opacidade (`data-darken` preset)
- **Copy orientativo** — copy real do brief para este slide
- **Notas de execução** — desvios do arquétipo, elementos específicos a destacar

**Regras de diversidade composicional (HARD):**
- Carrossel com ≥3 slides usa **≥2 arquétipos distintos**.
- Carrossel com ≥5 slides usa **≥3 arquétipos distintos**.
- Slide CTA final tipicamente em `A6-cta-button-anchored`.
- Slide capa tipicamente em `A1`, `A2`, `A10` ou `A12`.
- **Exceção (reference-driven mode):** quando A0-custom-from-reference é declarado em ≥2 slides porque a referência é mono-arquétipo intencional, a regra de ≥2/≥3 arquétipos distintos é **suspensa**. Documente a decisão em `## Notas para o designer`.

---

### 4. Escolha os carousel moves

Escolha **1–2 moves** do catálogo [`../_shared/CAROUSEL_MOVES.md`](../_shared/CAROUSEL_MOVES.md) (M1–M10) que vão dar identidade ao carrossel. Para cada move escolhido, declare:
- **Slug do move** (ex: `M2-numero-ostentatorio`, `M8-fio-tipografico`).
- **Em quais slides aparece** (lista ou "todos exceto último").
- **Notas de execução** se houver detalhe específico (ex: "número em cor secondary, 380px, canto superior direito").

**Por que 1–2 só:** mais que isso polui o carrossel. M4 (cta-arrow-ritualistico) é o move mais seguro e quase sempre cabe; combine-o com 1 move com mais personalidade (M2, M5, M7, M8 ou M10).

**Orientação de navegação (substitui o antigo "carousel chrome"):**

Quando o brief sinaliza necessidade de orientação de navegação — pedido explícito do user com termos como "progress bar", "indicador", "navegação", OU carrossel com **≥6 slides + tom didático sequencial** e nenhum arquétipo do plano já incluir auto-numeração visual — considere:

- **M9-edge-numbering** (`01/07` discreto no rodapé) — opção elegante; combina com qualquer estilo (editorial, minimal, brand-forward).
- **M6-reveal-progressivo** (barra/forma que enche slide a slide) — quando o conteúdo tem progressão real (tutorial, contagem regressiva, revelação).
- **M4-cta-arrow-ritualistico** (seta "Arraste →" fixa em todos exceto o último) — pareia bem com M9 ou M6.

Em dúvida, prefira **M9** sobre barra utilitária — é mais elegante e funciona em qualquer paleta. Carrosséis curtos (≤4 slides) raramente precisam: o leitor mantém orientação naturalmente. Se o user pediu "minimalista" ou "premium clean", evite os 3 — nenhum move de navegação é melhor que chrome utilitário num design quieto.

**CUIDADO com vocabulário de cor:** Se um move envolve escurecimento, descreva como "fundo sólido primary com overlay de escurecimento neutro" — NUNCA como "gradiente vinho/magenta". Usar nomes de cor brand faz o designer implementar hex literais em vez de overlay adaptável.

---

### 4b. Defina a presença do logo (`brandLogo`)

Default canônico: **logo na capa (slide 1) e no CTA final**. Sem instrução explícita do brief, sempre declare essas duas presenças no `visual-plan.md`. Em outros slides, só inclua se houver espaço limpo natural (ex: rodapé sem competição com handle/numeração).

Para cada slide com logo, declare no `visual-plan.md`:
- **Slide:** N
- **Posição:** uma das listadas no catálogo (`Cover-header-left`, `Cover-header-right`, `Cover-footer-left`, `CTA-footer-left`, `CTA-footer-right`, `CTA-header-large`) ou descrição livre se nenhuma cabe (ex: "header direito da capa, 160px, opondo o número de slide à esquerda")
- **Tamanho aproximado:** dentro do range 80–240px

**Regras:**
- Sempre numa extremidade (esquerda OU direita); nunca centralizado.
- Header da capa OU rodapé do CTA são as posições mais seguras.
- Se a capa já tem foto profissional ocupando uma coluna inteira (A1, A12), coloque logo na coluna oposta no header.
- Se o CTA é A6 com fundo brand sólido, logo no rodapé inferior esquerdo costuma funcionar (não compete com headline ao centro).
- Se a paleta tem fundo escuro num desses slides, espere que o logo real do usuário pode não contrastar — declare uma nota em "Notas para o designer" sobre considerar caixa neutra opcional atrás do logo.

Catálogo completo de posições e snippet HTML pronto em [`../gp2-html-designer/references/placeholders/README.md`](../gp2-html-designer/references/placeholders/README.md) §"Logo da marca".

---

### 5. Mapeie os elementos que devem receber data-variable

Este mapeamento é importante para que o designer aplique os atributos desde o HTML — o marker apenas confirma.

**O que SEMPRE deve ser mapeado quando presente:**
- Fundo sólido de slides brand/CTA → `data-variable="primary" data-variable-target="background"`
- Fundo brand com escurecimento atmosférico → section com `data-variable="primary"` + `<div data-darken="..." data-darken-opacity="...">`
- Eyebrow colorido → `data-variable="secondary"` ou `"primary"`
- CTA button / bloco de destaque → `data-variable="primary" data-variable-target="background"`
- Número de slide colorido → `data-variable="primary"`
- Fio/divisor de cor brand → `data-variable="primary"` ou `"secondary"`
- Span inline com cor brand → `data-variable="secondary"`
- Fill do progress bar (slides claros) → `data-variable="primary"`

**O que NUNCA recebe data-variable:**
- Brancos, pretos, off-whites, cinzas — são literais
- Overlays de legibilidade (gradiente rgba sobre foto) — são sempre literais
- Textos em cores neutras

---

## Output: visual-plan.md

### Free mode

```markdown
# Plano Visual — <título do template>

## Modo
free

## Paleta resolvida
- **Primary:** `#RRGGBB` — <papel>
- **Secondary:** `#RRGGBB` — <papel>
- **Neutro claro:** `#RRGGBB` — usado em slides claros
- **Neutro escuro:** `#RRGGBB` — usado em slides escuros

## Tipografia resolvida
- **Display:** <família> — <Npx> — peso <W> — kerning <±N%>
- **Subtítulo:** <família> — <Npx> — peso <W>
- **Eyebrow:** <família> — <Npx> — peso <W> — tracking <+N%> — <UPPERCASE | Title Case>
- **Body:** <família> — <Npx> — peso <W>
- **Caption:** <família> — <Npx>
- **Pairing:** <DisplayFamily + BodyFamily>

## Carousel moves
- **<M?-slug>:** <em quais slides — ex: "todos exceto último"> — <nota de execução opcional>
- **<M?-slug>:** <em quais slides> — <nota>

## Logo da marca
- **Slide 1 (capa):** <posição — ex: Cover-header-left, 140px>
- **Slide N (CTA):** <posição — ex: CTA-footer-left, 140px>
- **Outros slides (opcional):** <slide M: posição + tamanho>

## Plano de slides

### Slide 1 — <papel narrativo> (background: claro/escuro/brand)
- **Arquétipo:** A<N> — <slug>
- **Gradientes:** <nenhum | overlay bottom 0.70 | escurecimento-atmosférico diagonal-se 0.80 | ...>
- **Copy orientativo:** <copy real do brief>
- **Notas de execução:** <desvios do arquétipo, elementos específicos a destacar>

### Slide 2 — <papel narrativo> (background: ...)
- **Arquétipo:** A<N> — <slug>
- ...

### Slide N (CTA) — <papel narrativo> (background: brand)
- **Arquétipo:** A6-cta-button-anchored (default para CTA)
- ...

## Mapeamento de data-variable

| Elemento | Atributo |
|----------|----------|
| Fundo slides brand/CTA | `data-variable="primary" data-variable-target="background"` |
| Overlay de escurecimento | `data-darken="<preset>" data-darken-opacity="<N>"` no `<div>` overlay |
| Eyebrow colorido | `data-variable="secondary"` |
| ... | ... |

## Notas para o designer
<Instruções específicas, anti-patterns a evitar para este template, cuidados com o segmento, foto profissional, logo (se há restrição especial de contraste).>
```

### Reference-driven mode

```markdown
# Plano Visual — <título do template>

## Modo
reference-driven

## Análise da referência

<Cole aqui a checklist completa da etapa 1b preenchida (todos os itens marcados sim/não/qual). Esta seção é OBRIGATÓRIA em reference-driven mode e serve como rastreabilidade do que foi observado vs. herdado.>

### Síntese
- **Vocabulário visual a herdar:** <resumo em 2-4 linhas: paleta, tipografia, composição, elementos editoriais>
- **Ruídos detectados na referência (NÃO replicar):** <lista crua: logo X, @handle, telefone, hashtags, etc. — repetido em "Notas para o designer" com motivo individual>

## Vocabulário visual (extraído da referência)

### Paleta (da referência)
- **Primary:** `#RRGGBB` — <papel observado>
- **Secondary:** `#RRGGBB` — <papel>
- **Neutro claro:** `#RRGGBB`
- **Neutro escuro:** `#RRGGBB`

### Elementos editoriais a replicar
- <ex: eyebrow numerado em todos os slides>
- <ex: fio horizontal fino abaixo de cada título>

### Gradientes observados
- <ex: overlay to bottom rgba(0,0,0,0.70) nos slides com foto full-bleed>
- <ex: sem gradientes>

### Tratamento de imagem observado
- **Foto profissional:** <cutout PNG | retangular editorial | circular avatar | ausente>
- **Foto contextual:** <ausente | crop editorial | etc.>

## Tipografia resolvida (da referência)
- **Display:** <família ou categoria> — <Npx> — peso <W> — kerning <±N%>
- **Subtítulo:** <família> — <Npx> — peso <W>
- **Eyebrow:** <família> — <Npx> — peso <W> — tracking <+N%> — <UPPERCASE | Title Case>
- **Body:** <família ou categoria> — <Npx> — peso <W>
- **Caption:** <família> — <Npx>
- **Pairing:** <DisplayFamily + BodyFamily>

## Carousel moves
- **<M?-slug>:** <em quais slides> — <nota — identificado na referência ou inferido>
- **<M?-slug>:** <em quais slides> — <nota>

## Logo da marca
- **Slide 1 (capa):** <posição — ex: Cover-header-right, 140px — alinhado com o que a referência mostra, ou Cover-header-left default>
- **Slide N (CTA):** <posição — ex: CTA-footer-left, 140px>
- **Outros slides (opcional):** <slide M: posição + tamanho — só se a referência mostrar>

## Decisão composicional
<catalog-mapped | custom-anchors | hybrid>
<1-2 linhas: por que essa decisão. Em custom-anchors ou hybrid, indique quais slides usam A0 e por quê.>

## Plano de slides

### Slide 1 — <papel narrativo> (background: claro/escuro/brand)
- **Arquétipo:** A<N> — <slug>   <!-- ou A0-custom-from-reference -->
- **Anchors (apenas se A0):**
  - `<nome-zone-1>`: x=N–N%, y=N–N% — <o que vai aqui>
  - `<nome-zone-2>`: x=N–N%, y=N–N% — <o que vai aqui>
- **Justificativa de A0 (apenas se A0):** <por que nenhum A1–A14 cabia>
- **Gradientes:** <nenhum | overlay bottom 0.70 | escurecimento-atmosférico diagonal-se 0.80 | etc.>
- **Copy orientativo:** <copy do brief>
- **Notas de execução:** <o que herdar da referência, o que adaptar>

### Slide 2 — ...
- **Arquétipo:** A<N> — <slug>
- ...

## Mapeamento de data-variable

| Elemento | Atributo |
|----------|----------|
| Fundo slides brand/CTA | `data-variable="primary" data-variable-target="background"` |
| Overlay de escurecimento | `data-darken="<preset>" data-darken-opacity="<N>"` |
| ... | ... |

## Notas para o designer
<O que NÃO copiar da referência (logo, copy, fotos específicas). Erros visuais da referência a corrigir. Se decisão = custom-anchors ou hybrid, explique aqui por que o catálogo achataria a referência.>
```

---

## Resposta final ao orquestrador

**Free mode:**
```markdown
Plano visual gerado: `artifacts/gp2-art-director/<slug>/visual-plan.md`
Modo: free
Paleta: primary <hex> / secondary <hex> / neutro claro <hex> / neutro escuro <hex>
Tipografia: <display> + <body>
Slides planejados: <N>
Arquétipos: slide1=A?, slide2=A?, ... (diversidade: <N> tipos distintos)
Carousel moves: <M?, M?>
Logo: capa <posição> / CTA <posição>
Elementos data-variable mapeados: <N>
Próximo passo: gp2-html-designer
```

**Reference-driven mode:**
```markdown
Plano visual gerado: `artifacts/gp2-art-director/<slug>/visual-plan.md`
Modo: reference-driven
Paleta: primary <hex> / secondary <hex> / neutro claro <hex> / neutro escuro <hex>
Tipografia: <display> + <body>
Slides planejados: <N>
Arquétipos: slide1=A?, slide2=A?, ... (diversidade: <N> tipos distintos)
Carousel moves: <M?, M?> (identificados na referência)
Logo: capa <posição> / CTA <posição>
Elementos data-variable mapeados: <N>
Próximo passo: gp2-html-designer
```

---

## Modo de resposta a pedidos do designer

Quando o orquestrador re-invoca esta skill com `status: blocked-on-art-director`, você recebe:
- `visual-plan.md` original
- `notes.md` do designer com a seção `## Pedidos ao art-director`
- Screenshots parciais do Passo 1 (se houver)

Para cada pedido:
1. Avalie se é **válido** (contradição factual, restrição técnica como copy que não cabe, contraste impossível) ou **inválido** (preferência estética do designer, dúvida que o plano já responde).
2. Se válido: edite `visual-plan.md` com a correção pontual + adicione/atualize seção `## Histórico de revisões` registrando o que mudou e por quê.
3. Se inválido: edite o `notes.md` do designer adicionando seção `## Resposta art-director` explicando por que manter o plano original.

**Patch cirúrgico, não reescrita.** Não toque em decisões não-relacionadas ao pedido.

Responda ao orquestrador:
```markdown
Modo: resposta a designer
Pedidos atendidos: <N de M>
Pedidos rejeitados: <N> — ver notes.md
Plano revisado: <yes | no>
Próximo passo: gp2-html-designer (retomar Passo <N>)
```

---

## O que esta skill NÃO faz

- Não escreve HTML. Apenas orienta.
- Não aplica `data-variable` no HTML — mapeia o que deve receber; o designer aplica.
- Não decide copy por slide — usa o copy do brief.
- Não prescreve tamanhos exatos de fonte nem posições absolutas em px.
