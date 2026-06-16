---
name: gp2-art-director
description: "Segunda etapa da Pipeline v2 (após gp2-request-interpreter, antes de gp2-html-designer). Define a direção visual do template: paleta com hexs concretos, escala tipográfica resolvida, um arquétipo composicional A* por slide (catálogo _shared/COMPOSITIONS.md), 1-2 carousel moves M* (catálogo _shared/CAROUSEL_MOVES.md) e mapeamento data-variable. Em free mode inventa; em reference-driven mode extrai da(s) imagem(ns). Quando o brief tem um style preset (## Estilo), trava o vocabulário visual nas regras do preset (catálogo _shared/STYLE_PRESETS.md), sobrescrevendo escolha livre de família e alternância de background. Produz visual-plan.md como orientação para o designer — não como contrato rígido. Também opera em modo de resposta quando o designer reporta status: blocked-on-art-director. Não escreve HTML."
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

### 1a. Detecte o style preset

Leia `brief.md → ## Estilo`. Se ≠ `nenhum`, abra [`../_shared/STYLE_PRESETS.md`](../_shared/STYLE_PRESETS.md) no preset indicado e trate as **regras hard do preset como restrições que se sobrepõem a todas as suas escolhas livres** ao longo deste workflow:

- **Família estética travada** — não escolha livremente de `../gp2-html-designer/references/aesthetic-families.md`; use a direção do preset.
- **Paleta** — derive do segmento (free) ou extraia da referência (reference-driven), mas obedeça às regras de paleta do preset (ex: `editorial-premium` → fundo sempre claro, 1 acento de marca cirúrgico).
- **Alternância de background** — se o preset restringe (ex: `editorial-premium` proíbe DARK/Brand full-bleed), **sobrescreva** a alternância da sequência narrativa do brief: todos os slides seguem a regra do preset.
- **Arquétipos e moves** — restritos à allowlist do preset (a regra de diversidade ≥2/≥3 continua valendo dentro da allowlist).
- **Logo / foto profissional** — siga a regra do preset (ex: `editorial-premium` → capa + CTA, nunca centralizado).
- **Conflito com a referência** (reference-driven) — o **preset tem prioridade**. Onde a referência conflita com o preset (ex: fundo escuro, gradiente forte), resolva a favor do preset e documente cada conflito em `## Notas para o designer`.

Registre `## Estilo aplicado: <slug | nenhum>` no topo do `visual-plan.md` (ver templates abaixo) — é assim que o designer e o reviewer herdam o sinal.

Se `## Estilo: nenhum`, ignore esta etapa: comportamento livre normal.

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

**Regra de ouro:** para cada imagem da referência, classifique em UM dos 4 buckets abaixo. Para elementos não-imagem (handle, hashtag, métrica, badge), continue usando SLOT/RUÍDO da tabela anterior.

**Caso especial — composição "post estilo rede social":** quando a referência reproduz o layout de um post de Instagram/Twitter (avatar circular + nome + handle no header, conteúdo no centro, métricas no footer), o header é uma **composição de slots** (`instagramProfilePicture` + `instagramName` + `instagramHandle`) — não é ruído. Preserve a estrutura, mapeie os 3 slots, descarte só o que não tem slot (selo verificado, métricas de plataforma).

#### Imagens / fotos / vetores — classificação em 4 buckets

Esta etapa é **crítica** para evitar que o designer caia na armadilha de gerar SVG/base64 ad-hoc para elementos que não conseguimos reproduzir. O art-director é quem está olhando a referência e tem informação para decidir. O designer só executa.

| Bucket | Quando aplicar | O que declarar no `visual-plan.md` |
|--------|----------------|-------------------------------------|
| **B1 — slot da plataforma** | Elemento mapeia 1-pra-1 em um slot da tabela oficial: `brandLogo`, `professionalPhoto`, `instagramProfilePicture`. Conteúdo será preenchido pelo usuário em runtime. | `data-image-type="<tipo>"` + posição |
| **B2 — imagem genérica buscável** | Foto contextual reproduzível por imagem de banco público — cenário/objeto/ambiente genérico que o `picsum.photos` consegue entregar de forma estável (mesa de escritório, consultório, bolsa de água quente, prato de comida, dispositivo médico genérico, etc.). | `userAsset` + URL `picsum.photos/id/{N}/{w}/{h}` sugerida (`{N}` determinístico — sem `?random`) + alt curto |
| **B3 — imagem específica não-reproduzível (placeholder obrigatório)** | Elemento visual específico da referência que **não** existe em banco público e **não** é slot — laço de campanha (Março Amarelo, Outubro Rosa), ícone de marca específica, ilustração customizada, mascote, vetor temático, símbolo de instituição, infográfico autoral. | `userAsset` + flag `image-source: placeholder-required` + motivo curto (1 linha — ex: "símbolo Março Amarelo não disponível em CDN público; placeholder genérico no template") |
| **B4 — ruído (NÃO replicar)** | Elemento pertence à marca/plataforma de origem da referência: logo de outra marca, métricas de UI, selo verificado, handle "@" de outra conta, marca d'água, crédito de designer, QR code, ícones de nicho em template multi-nicho. | Lista "NÃO replicar" no visual-plan; designer **não** inclui no HTML |

**Checklist por tipo de imagem (responda B1 / B2 / B3 / B4 para cada item presente na referência):**

- [ ] **Avatar circular pequeno** em header de post (≤80px, formato perfil de rede social)? → **B1** (`instagramProfilePicture`). **NÃO confundir com `professionalPhoto`.**
- [ ] **Foto de pessoa em primeiro plano como hero** (cutout PNG editorial, retrato grande dominante)? → **B1** (`professionalPhoto`) — NÃO em multi-nicho.
- [ ] **Logo retangular/quadrado da marca** do usuário? → **B1** (`brandLogo`). Logo de marca de origem (não-usuário) → **B4**.
- [ ] **Foto contextual genérica** (ambiente, espaço, equipamento, objeto, asset comum)? → **B2** se reproduzível por picsum; **B3** se exigir cenário muito específico (ex: "consultório com identidade visual XYZ").
- [ ] **Foto de produto** isolado em cenário neutro? → **B2** se produto genérico (notebook, óculos, livro); **B3** se produto específico da marca de origem.
- [ ] **Ilustração ou vetor** com estilo definido (flat, line, 3D, abstrato)? → **B3** quase sempre (ilustração específica de marca/campanha). Apenas **B2** se for forma geométrica neutra reproduzível por picsum.
- [ ] **Símbolo de campanha** (laço Março Amarelo, Outubro Rosa, fita Setembro Amarelo, mascote institucional, infográfico autoral)? → **B3** sempre. Nunca tentar `picsum`; nunca gerar SVG inline ad-hoc.
- [ ] **Ícone** pictográfico funcional (setas, check, números, lupa)? OK como decoração CSS/SVG simples (não é imagem); ícone simbólico de nicho (cruz médica, patinha, haltere) → **B4** em multi-nicho.
- [ ] Tratamento aplicado (filtro, dessaturação, duotone, overlay colorido)? Note no bucket correspondente.

**Heurística rápida B2 vs B3:** se você consegue descrever o conteúdo da imagem em 3-5 palavras genéricas que casariam com QUALQUER foto de banco ("mulher sorrindo em escritório", "mesa com café e notebook"), é B2. Se a descrição precisa nomear um símbolo, marca, campanha ou conceito visual específico ("laço amarelo de conscientização", "logo Instagram cinza", "infográfico de pirâmide alimentar"), é B3.

**Regra hard (multi-nicho do `gp2-template-suggester`):** `professionalPhoto` cai automaticamente para B4 (descartar) e qualquer ícone de nicho cai para B4.

**CTAs e botões:**
- [ ] Há botão CTA explícito? Em qual slide? Texto e estilo (pill? retangular? ghost?)
- [ ] Texto do CTA é genérico ("Salve", "Compartilhe") ou de serviço ("Agende", "Compre")?

**Sinais de navegação / chrome de carrossel:**
- [ ] Progress bar visível?
- [ ] Numeração `01/07` ou similar?
- [ ] Seta de swipe "Arraste →"?

#### Síntese após a checklist

Após preencher a checklist, escreva 5 listas distintas:

1. **Vocabulário visual a herdar** (o que a referência ensina que vale replicar): paleta, tipografia, composição, elementos editoriais, tratamento de imagem.

2. **B1 — Slots da plataforma identificados (REPLICAR como atributos editáveis):** lista cada imagem da referência que mapeia num slot oficial, com o atributo HTML correto e a posição. Formato: `- <elemento da referência> → data-image-type="<tipo>" em <slide N>, posição <descrição>`. Exemplo: `- Avatar circular do header → data-image-type="instagramProfilePicture" em slide 1, posição header-left ~64px circular`.

3. **B2 — Imagens genéricas buscáveis (`userAsset` + URL picsum):** lista cada imagem contextual reproduzível por banco público, com URL `picsum.photos/id/{N}/{w}/{h}` sugerida. Formato: `- <descrição genérica da imagem> → userAsset, src="https://picsum.photos/id/{N}/{w}/{h}" em <slide N>, posição <descrição>`. Escolha um `{N}` determinístico (sem `?random`) coerente com o conteúdo (ex: `id/1015` para natureza, `id/96` para pessoa).

4. **B3 — Imagens específicas não-reproduzíveis (placeholder obrigatório):** lista cada imagem específica que não existe em banco e não é slot, com motivo curto. Formato: `- <descrição> → userAsset, image-source: placeholder-required em <slide N>. Motivo: <símbolo de campanha sem CDN | ilustração autoral | mascote institucional | infográfico específico>`. O designer **deve** usar `references/placeholders/image-placeholder.b64.txt` para esses slots — gerar SVG inline é violação.

5. **B4 — Ruídos a descartar (NÃO replicar):** o que a referência tem mas NÃO entra no template porque não mapeia em bucket B1-B3 e pertence à marca/plataforma de origem. Formato: `- NÃO replicar: <ruído> visto em <slide N da referência>. Motivo: <pertence à marca de origem | UI de plataforma de origem | viola multi-nicho | copy específica de nicho>`. Em batch multi-nicho do `gp2-template-suggester`, descarte também `professionalPhoto` (vai para B4 automaticamente).

**Distinção crítica:** "post estilo Instagram/Twitter" tem header com avatar+nome+handle. Esses 3 elementos são **B1 (slots)**, não B4 (ruídos). O selo verificado azul ao lado do nome **é** B4 (UI da plataforma de origem). Não jogue o header inteiro fora — preserve a estrutura e mapeie os slots.

---

### 1c. Decisão de fidelidade composicional — REFERENCE-DRIVEN MODE ONLY

Antes de planejar slides, decida explicitamente: a identidade composicional da referência **cabe no catálogo A1–A14** com ajuste, ou **exige A0-custom-from-reference**?

**Gatilho determinístico — leia `brief.md → ## Fidelidade`:**

| `Fidelidade` no brief | Default composicional |
|----------------------|----------------------|
| `recreate` | **A0-custom-from-reference é default em TODOS os slides.** Cair em A1–A14 só com justificativa explícita por slide em `## Notas para o designer` (ex: "Slide 3 cabe em A5 sem desvio porque a referência usa exatamente a estrutura listicle numerada de A5 — anchors batem ≤5%"). Sem justificativa documentada, mantenha A0. |
| `inspired` | Catálogo A1–A14 default. A0 só quando ≥15% de desvio dos anchors ou quando a referência claramente repete um padrão único irrepetível no catálogo. |
| `free` | Catálogo. A0 não disponível (free mode não tem referência). |

Depois do gatilho acima, aplique também os critérios visuais abaixo (úteis principalmente em `inspired`, e como sanity check em `recreate`):

**Use catálogo (A1–A14) quando:**
- A composição da referência mapeia razoavelmente em algum A* (≤15% de desvio dos anchors da tabela).
- A identidade da peça está mais na paleta/tipografia/elementos editoriais do que na composição em si.
- Ajustar coords dentro de um A* preserva o que define a referência.

**Use A0-custom-from-reference quando:**
- `Fidelidade: recreate` no brief (default obrigatório acima).
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

## Estilo aplicado
<editorial-premium | nenhum>

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

## Imagens declaradas

Em free mode, declare aqui cada imagem que cada slide vai conter, classificada em bucket B1–B3 (não há B4 em free — não existe referência para descartar). Designer consome esta tabela e não inventa imagens fora dela.

| Slide | Conteúdo da imagem | Bucket | Atributo HTML / src sugerido | Motivo (B3) / Posição |
|-------|-------------------|--------|------------------------------|------------------------|
| 1 | <ex: foto profissional> | B1 | `data-image-type="professionalPhoto"` | <hero cover, ~46% width> |
| 3 | <ex: foto contextual de consultório> | B2 | `userAsset`, `src="https://picsum.photos/id/96/580/360"` | <top-right, ~580×360> |

- B1: usar quando o brief pediu foto profissional / logo / avatar social.
- B2: usar para qualquer foto contextual genérica (designer aplica picsum determinístico).
- B3: usar quando o art-director decide que o slide precisa de uma ilustração específica que o picsum não entrega — placeholder genérico (`image-placeholder.b64.txt`).

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

## Estilo aplicado
<editorial-premium | nenhum>

## Análise da referência

<Cole aqui a checklist completa da etapa 1b preenchida (todos os itens marcados sim/não/qual). Esta seção é OBRIGATÓRIA em reference-driven mode e serve como rastreabilidade do que foi observado vs. herdado.>

### Síntese
- **Vocabulário visual a herdar:** <resumo em 2-4 linhas: paleta, tipografia, composição, elementos editoriais>
- **B1 — slots da plataforma:** <lista resumida — ex: professionalPhoto slide 1+6, brandLogo slide 2+6>
- **B2 — imagens buscáveis (picsum):** <lista resumida — ex: foto contextual slide 3 (mulher com bolsa quente), slide 4 (dispositivo médico)>
- **B3 — imagens placeholder-required:** <lista resumida — ex: laço Março Amarelo nos slides 1-6, infográfico autoral slide 5>
- **B4 — ruídos a descartar:** <lista crua — ex: handle "errata pra todo", selo verificado, métricas de UI>

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

### Imagens declaradas

Tabela determinística que o designer **deve** consumir antes de qualquer decisão de imagem. Cada linha = 1 imagem da referência classificada em 1 bucket B1–B4. Designer não revisita; apenas executa.

| Slide | Elemento da referência | Bucket | Atributo HTML / src sugerido | Motivo (B3) / Posição |
|-------|-----------------------|--------|------------------------------|------------------------|
| 1 | <ex: foto profissional cutout> | B1 | `data-image-type="professionalPhoto"` | <posição: bottom-left, ~46% width × 78% height> |
| 3 | <ex: mulher com bolsa quente> | B2 | `userAsset`, `src="https://picsum.photos/id/96/580/360"` | <posição: top-right, ~580×360> |
| 1-6 | <ex: laço Março Amarelo> | B3 | `userAsset`, `image-source: placeholder-required` | <motivo: símbolo de campanha sem CDN; placeholder genérico>, posição variável por slide |
| 2 | <ex: handle "errata pra todo"> | B4 | — (não replicar) | <motivo: handle de marca de origem> |

**Regras:**
- Toda imagem visível na referência **deve** estar nesta tabela. Designer não pode adicionar imagem que não está aqui.
- B1: declare `data-image-type` exato. Não escolha URL — o slot é preenchido pelo usuário em runtime.
- B2: escolha um `id` determinístico do `picsum.photos` (sem `?random`, sem `source.unsplash`). Mesma URL = mesma imagem.
- B3: **nunca** sugira URL nem SVG. Apenas declare `image-source: placeholder-required` + motivo curto. Designer usa `references/placeholders/image-placeholder.b64.txt` automaticamente.
- B4: não entra no HTML. Apenas registra que foi visto e descartado.

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
Estilo aplicado: <editorial-premium | nenhum>
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
Estilo aplicado: <editorial-premium | nenhum>
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
