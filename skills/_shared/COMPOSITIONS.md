# Catálogo de Composições (A*)

Vocabulário composicional compartilhado entre `gp2-art-director` (escolhe), `gp2-html-designer` (executa) e `gp2-html-reviewer` (confere variedade).

Cada arquétipo é um **esqueleto inicial** — o designer adapta coords exatas mas mantém anchors gerais. Desvios devem ser justificados em `notes.md`. O reviewer aceita desvios documentados; flagra desvio silencioso.

**Regras de uso (art-director):**
- Carrosséis com ≥3 slides usam ≥2 arquétipos distintos.
- Carrosséis com ≥5 slides usam ≥3 arquétipos distintos.
- Slide CTA final tipicamente em `A6-cta-button-anchored` ou variante.
- Slide capa tipicamente em `A1`, `A2`, `A10`, `A12` ou `A14` (este último quando a capa precisa combinar foto contextual + profissional + hook tipográfico).
- Slide de miolo editorial com numeração ostentatória tipicamente em `A13` (combinado com M11).
- **Exceção reference-driven:** em `reference-driven mode`, se a referência tem identidade composicional que nenhum A1–A14 reproduz fielmente, declare `A0-custom-from-reference` (ver abaixo) com anchors derivados da própria referência. Quando ≥2 slides usam A0, a regra de diversidade ≥2/≥3 arquétipos é **suspensa** — fidelidade à referência prevalece sobre variedade composicional.

**Convenção dos diagramas:** grid abstraído 1080×1350 → ASCII ~14 colunas × 12 linhas. `[FOTO]` = slot de imagem; `■` = bloco de cor primary; `─` = fio decorativo; `→` = swipe arrow.

---

## A1 — hero-split

```
+----------------------------+
| EYEBROW · 01               |
|                            |
| TÍTULO MASSIVO             |
| EM 2 LINHAS                |
|                            |
| corpo curto explicativo    |
|                            |
|                  [FOTO PRO]|
|                  [        ]|
|                  [        ]|
| @handle  ──────────────  → |
+----------------------------+
```

**Anchors:**
- `headline-zone`: x=6–55%, y=20–55%
- `image-zone`: x=58–94%, y=18–88% (foto profissional cutout, ancorada na base)
- `eyebrow-zone`: x=6–40%, y=10–14%
- `cta-zone`: rodapé full-width

**Quando usar:** capa de carrossel com profissional/marca; slide de apresentação.
**Tom:** editorial, minimal.
**Pareamento bom:** vai bem antes de A3, A5, A7. Forte como abertura.
**Anti-uso:** slides puramente educativos sem rosto; CTAs (use A6).

---

## A2 — full-bleed-text-bottom

```
+----------------------------+
| [                        ] |
| [                        ] |
| [    FOTO FULL-BLEED     ] |
| [                        ] |
| [    overlay darken      ] |
| [                        ] |
| ============================
| EYEBROW                    |
| TÍTULO SOBRE OVERLAY       |
| corpo curto                |
| @handle              →     |
+----------------------------+
```

**Anchors:**
- `image-zone`: full-bleed 0–100%, 0–100% (com `data-darken="bottom"`)
- `headline-zone`: x=6–80%, y=68–88% (sobre overlay)
- `eyebrow-zone`: x=6–40%, y=63–67%
- `cta-zone`: rodapé

**Quando usar:** capa dramática com foto contextual forte; abertura emocional.
**Tom:** editorial, maximal.
**Pareamento bom:** abre carrossel de storytelling; pareia bem com A10 ou A4 nos slides seguintes.
**Anti-uso:** conteúdo denso (overlay reduz legibilidade); slides educativos com muitos dados.

---

## A3 — editorial-eyebrow-stack

```
+----------------------------+
|                            |
| EYEBROW MAIÚSCULO · TRACK  |
| ──────────────────────     |
|                            |
| Headline em duas           |
| linhas confortáveis        |
|                            |
| Body em parágrafo curto    |
| com 2-3 linhas calmas      |
| que sustentam o título.    |
|                            |
| @handle              01/07 |
+----------------------------+
```

**Anchors:**
- `eyebrow-zone`: x=6–80%, y=20–24%
- `fio-zone`: x=6–40%, y=26–27% (1–2px)
- `headline-zone`: x=6–80%, y=32–55%
- `body-zone`: x=6–75%, y=60–82%

**Quando usar:** slide educativo de miolo; quando o conteúdo é só tipografia editorial sem imagem.
**Tom:** editorial, minimal.
**Pareamento bom:** alterna com A5, A7, A8; vai bem em sequência (slides 2–4).
**Anti-uso:** slide capa (frio demais sem âncora visual); CTA.

---

## A4 — quote-centered-fios

```
+----------------------------+
|                            |
|         ── 01 ──           |
|                            |
|                            |
|     "Citação curta         |
|      em duas linhas        |
|       e forte como         |
|        um soco."           |
|                            |
|       — Autor / Fonte      |
|                            |
| @handle              →     |
+----------------------------+
```

**Anchors:**
- `quote-zone`: x=15–85%, y=35–65%, centered
- `number-zone`: x=42–58%, y=22–28% entre fios
- `attribution-zone`: x=30–70%, y=70–75%

**Quando usar:** slide de citação/prova social; momento de quebra no carrossel.
**Tom:** editorial, minimal.
**Pareamento bom:** entre slides densos como respiro; após A1 ou antes de A6.
**Anti-uso:** capa; conteúdo denso multi-ponto.

---

## A5 — listicle-numbered-row

```
+----------------------------+
| EYEBROW                    |
| ──────                     |
| 3 sinais que…              |
|                            |
| ╔══╗  Item um curto e      |
| ║01║  direto sem rodeio    |
| ╚══╝                       |
|                            |
| ╔══╗  Item dois também     |
| ║02║  curto e direto       |
| ╚══╝                       |
|                            |
| @handle              →     |
+----------------------------+
```

**Anchors:**
- `eyebrow-zone`: x=6–40%, y=8–12%
- `headline-zone`: x=6–80%, y=18–28%
- `item-zone-N`: x=6–94%, y=35+15×(N-1)%, altura ~13%
  - `item-number`: x=6–18% (square box, primary fill)
  - `item-text`: x=22–90%

**Quando usar:** slide com 2–4 itens enumerados; meio de carrossel listicle.
**Tom:** minimal, didático.
**Pareamento bom:** sequência A1 → A5 → A5 (proibido — viola low-diversity) — alternar com A3 ou A7. Em listicle longo, usar 1 slide A5 por chunk de 2–3 itens.
**Anti-uso:** quando o item exige imagem própria (use A8 ou A11); CTA.

---

## A6 — cta-button-anchored

```
+----------------------------+
|                            |
|   ■■■■■■■■■■■■■■■■■■■■■■■  |
|   ■                      ■  |
|   ■   FUNDO PRIMARY      ■  |
|   ■                      ■  |
|   ■■■■■■■■■■■■■■■■■■■■■■■  |
|                            |
| Pronto para começar?       |
|                            |
|   [  AGENDE AGORA  → ]     |
|                            |
| @handle              link  |
+----------------------------+
```

**Anchors:**
- `background-zone`: full slide, `data-variable="primary" data-variable-target="background"` + `data-darken` opcional
- `headline-zone`: x=10–90%, y=45–60%, fonte clara
- `cta-button-zone`: x=20–80%, y=68–80%, fundo neutro/secondary
- `cta-meta-zone`: x=6–94%, y=88–94%

**Quando usar:** **slide final** do carrossel; ponto de conversão.
**Tom:** maximal (cor brand forte).
**Pareamento bom:** último slide, sempre. Antecede direto com A3, A5 ou A8.
**Anti-uso:** capa (queima impacto cedo); miolo.

---

## A7 — data-spotlight

```
+----------------------------+
| EYEBROW                    |
|                            |
|                            |
|     7 5 %                  |
|     ───                    |
|                            |
| dos pacientes que ouvem    |
| esta orientação melhoram   |
| em até 30 dias             |
|                            |
| fonte: estudo X, 2024      |
| @handle              →     |
+----------------------------+
```

**Anchors:**
- `eyebrow-zone`: x=6–40%, y=10–14%
- `data-zone`: x=6–60%, y=22–48%, número massivo (display 240–360px)
- `data-fio`: x=6–25%, y=48–49%
- `context-zone`: x=6–90%, y=55–75%
- `source-zone`: x=6–60%, y=82–86%, caption

**Quando usar:** slide de dado/estatística no meio do carrossel.
**Tom:** editorial, minimal.
**Pareamento bom:** após A3 (educativo); antes de A4 (citação) ou A6 (CTA).
**Anti-uso:** quando não há número concreto; capa.

---

## A8 — overlap-image-text

```
+----------------------------+
| EYEBROW                    |
| Headline em                |
| duas linhas                |
|                            |
| ┌────────────────────┐     |
| │                    │     |
| │  [FOTO CONTEXTUAL] │     |
| │                    │     |
| │                    │     |
| └────┐               │     |
|      │ caption sobre │     |
|      │ a foto        │     |
| @handle ─────────────  →   |
+----------------------------+
```

**Anchors:**
- `eyebrow-zone`: x=6–40%, y=8–12%
- `headline-zone`: x=6–75%, y=15–32%
- `image-zone`: x=15–88%, y=38–80%
- `overlap-caption-zone`: x=6–48%, y=70–82% (sobrepõe canto inferior esquerdo da foto)

**Quando usar:** miolo com foto contextual + texto curto que se ancora visualmente.
**Tom:** editorial.
**Pareamento bom:** após A3; antes de A6.
**Anti-uso:** foto profissional cutout (use A1 ou A12); slides sem imagem disponível.

---

## A9 — comparison-split

```
+----------------------------+
| EYEBROW · comparação       |
|                            |
| ┌──────────┬─────────────┐ |
| │  ANTES   │  DEPOIS     │ |
| │          │             │ |
| │ [imagem] │  [imagem]   │ |
| │          │             │ |
| │ ponto A1 │  ponto B1   │ |
| │ ponto A2 │  ponto B2   │ |
| │ ponto A3 │  ponto B3   │ |
| └──────────┴─────────────┘ |
|                            |
| @handle              →     |
+----------------------------+
```

**Anchors:**
- `eyebrow-zone`: x=6–60%, y=8–12%
- `left-column`: x=6–46%, y=18–82%, header + image + body
- `right-column`: x=54–94%, y=18–82%, header + image + body
- `divider`: x=49–51%, y=18–82% (fio vertical sutil)

**Quando usar:** slide explícito de comparação A vs B / antes vs depois / opção 1 vs 2.
**Tom:** minimal, didático.
**Pareamento bom:** único na sequência; antecede A6.
**Anti-uso:** mais de 2 itens (use A5 ou A11); conteúdo não-comparável.

---

## A10 — headline-massive-solo

```
+----------------------------+
|                            |
|                            |
|                            |
|  HEADLINE                  |
|  GIGANTE                   |
|  EM TRÊS                   |
|  LINHAS                    |
|                            |
|                            |
|                            |
| @handle              01/07 |
+----------------------------+
```

**Anchors:**
- `headline-zone`: x=6–90%, y=25–75%, display 120–160px peso 800
- `meta-zone`: rodapé x=6–94%, y=88–94%

**Quando usar:** capa de carrossel quote-driven ou conceitual; slide de hook puramente tipográfico.
**Tom:** editorial maximal (sem decoração concorrente).
**Pareamento bom:** abre carrossel; emparelha forte com A3 ou A4 no slide seguinte.
**Anti-uso:** miolo (carente de variação); CTA (use A6); quando o título é curto demais (vira vazio).

---

## A11 — bento-2x2

```
+----------------------------+
| EYEBROW                    |
| Title curto                |
|                            |
| ┌───────────┬────────────┐ |
| │  item 1   │   item 2   │ |
| │  [icon]   │   [icon]   │ |
| ├───────────┼────────────┤ |
| │  item 3   │   item 4   │ |
| │  [icon]   │   [icon]   │ |
| └───────────┴────────────┘ |
|                            |
| @handle              →     |
+----------------------------+
```

**Anchors:**
- `eyebrow-zone`: x=6–40%, y=6–10%
- `headline-zone`: x=6–80%, y=12–22%
- `bento-zone`: x=6–94%, y=28–86%, grid 2×2 com gap ~24px
  - cada `cell`: ícone (32–48px) no topo + texto curto

**Quando usar:** slide com 4 pontos paralelos (benefícios, features, princípios).
**Tom:** minimal, denso.
**Pareamento bom:** miolo entre A3 e A6.
**Anti-uso:** menos de 4 itens (use A5); mais de 4 (use múltiplos A5); conteúdo sequencial (não paralelo).

---

## A12 — photo-with-floating-caption

```
+----------------------------+
| [                        ] |
| [   FOTO COVER 60%       ] |
| [                        ] |
| [   ┌──────────────┐     ] |
| [   │ EYEBROW      │     ] |
| [   │ Caption fina │     ] |
| [   │ flutuando    │     ] |
| [   └──────────────┘     ] |
| [                        ] |
| (foto continua sob legenda)|
|                            |
| @handle              →     |
+----------------------------+
```

**Anchors:**
- `image-zone`: full-bleed 0–100%, 0–80%
- `floating-caption-zone`: x=8–50%, y=40–70%, card de fundo neutro com `box-shadow` discreta
- `cta-zone`: rodapé sobre extensão da foto (com `data-darken="bottom"` se necessário)

**Quando usar:** capa com foto editorial forte + necessidade de gancho textual ancorado.
**Tom:** editorial.
**Pareamento bom:** alternativa a A1/A2 como abertura; antecede A3 ou A7.
**Anti-uso:** quando o card flutuante esconderia o ponto focal da foto; CTA.

---

## A13 — editorial-numbered-context

```
+----------------------------+
| [02]  O PROBLEMA ─────     |
|                            |
|                            |
| Headline serifa            |
| em duas linhas.            |
|                            |
| Body curto em 2-3 linhas   |
| que sustenta o título e    |
| introduz a foto abaixo.    |
|                            |
| [   FOTO CONTEXTUAL   ]    |
| [   full-width        ]    |
| [                     ]    |
| ──────────────────────     |
| @handle           02 / 05  |
+----------------------------+
```

**Anchors:**
- `slide-number-box`: x=6–14%, y=6–11% (quadrado preenchido com primary, número display branco)
- `eyebrow-zone`: x=16–60%, y=7–10% (UPPERCASE tracking +12%, com fio horizontal curto à direita do label)
- `headline-zone`: x=6–80%, y=17–35% (display serif 88–110px peso 400–600)
- `body-zone`: x=6–80%, y=42–55% (sans 22–26px peso 400 line-height 1.5)
- `contextual-image-zone`: x=6–94%, y=58–82% (full-width retangular, sem border-radius ou bem sutil)
- `footer-fio`: x=6–94%, y=88% (fio horizontal 1px)
- `footer-zone`: x=6–94%, y=90–94% (`@handle` à esquerda, `NN / NT` à direita, sans 14–16px)

**Quando usar:** slide de miolo de carrossel editorial com numeração ostentatória (M11) + foto contextual obrigatória. Combina forte com sequências didáticas que precisam de respiração visual entre slides educativos densos.
**Tom:** editorial, calmo, premium.
**Pareamento bom:** vai bem em sequências de 4-6 slides usando o mesmo padrão; combina com A10 na capa e A6 no CTA. Quando usado em ≥2 slides do mesmo carrossel, o slide-number-box vira identidade visual da peça.
**Anti-uso:** capa (slide 01 fica raso — use A1, A2 ou A10); CTA; carrosséis sem foto contextual disponível por slide.

---

## A14 — rich-hero-cutout

```
+----------------------------+
|                            |
| ▓ EYEBROW PILL ▓           |
|                            |
| ┌────────────────────────┐ |
| │                        │ |
| │  FOTO CONTEXTUAL       │ |
| │  border-radius 24px    │ |
| │                        │ |
| └────────────────────────┘ |
|                            |
| ─── (fio brand curto)      |
| Headline bold              |
| com [span colorido]        |
| em 2-3 linhas.             |
|                            |
| Body curto em 2-3 linhas.  |
|                            |
| ┌─────┐         [FOTO PRO] |
| │LOGO │         [        ] |
| └─────┘         [        ] |
+----------------------------+
```

**Anchors:**
- `eyebrow-pill-zone`: x=6–35%, y=4–10% (background sólido primary/secondary, texto branco UPPERCASE)
- `contextual-image-zone`: x=4–96%, y=12–48% (border-radius 16–24px, dashed border opcional para indicar substituível)
- `accent-fio-zone`: x=6–18%, y=51% (fio horizontal 3-4px, primary ou secondary)
- `headline-zone`: x=4–62%, y=54–72% (sans bold 70–90px peso 800, span com cor brand interno)
- `body-zone`: x=4–62%, y=74–84% (sans 22–24px peso 400)
- `logo-zone`: x=4–18%, y=86–96% (box neutro com border, "SEU LOGO VAI AQUI")
- `professional-photo-zone`: x=68–100%, y=58–100% (cutout PNG, **ancorado bottom-right** — `top + height = data-height` E `left + width = data-width`)

**Quando usar:** capa rica de carrossel saúde/serviço com profissional + foto contextual + headline forte. Slide-1 ideal quando o brief pede confiança máxima (presença humana) + contexto visual (equipamento, ambiente, asset) + hook tipográfico.
**Tom:** maximal (3 zonas visuais + 2 textuais).
**Pareamento bom:** abre carrossel; antecede A3, A5 ou A7. Pareia com A6 no CTA final.
**Anti-uso:** miolo (excesso de elementos cria fadiga); carrosséis minimalistas; quando a foto contextual e a foto profissional disputam o ponto focal — escolha um (A1) ou outro (A12).
**Atenção:** a foto profissional aqui **deve** seguir as regras de ancoragem em [`../gp2-html-designer/references/professional-photo-placements.md`](../gp2-html-designer/references/professional-photo-placements.md): `top + height = data-height` (zero margem inferior) E `left + width = data-width` (encostado na direita). Caso contrário, vira finding "voando" no reviewer.

---

## A0 — custom-from-reference (reference-driven mode only)

Arquétipo de escape. **Não tem layout pré-definido** — o art-director declara os anchors caso a caso, derivando-os diretamente da referência visual.

**Quando usar:**
- Modo `reference-driven` apenas.
- A referência tem identidade composicional que nenhum A1–A14 reproduz sem achatar (ex: tipografia diagonal, grid 3 colunas, texto em arco, headline com bleed intencional, número editorial ocupando 60% do slide, layout que repete propositalmente em todos os slides).
- O art-director avalia: "se eu mapear isso pra A3/A8/A10, perco o que define a peça?" Se sim → A0.

**Como declarar no `visual-plan.md`:**

```markdown
### Slide N — <papel> (background: ...)
- **Arquétipo:** A0-custom-from-reference
- **Anchors (derivados da referência):**
  - `<nome-zone-1>`: x=N–N%, y=N–N% — <o que vai aqui>
  - `<nome-zone-2>`: x=N–N%, y=N–N% — <o que vai aqui>
  - ...
- **Justificativa de A0:** <1-2 linhas: por que A1–A14 achatariam>
- **Gradientes:** ...
- **Copy orientativo:** ...
- **Notas de execução:** ...
```

**Regras:**
- A0 só é válido em reference-driven mode. Em free mode, escolha A1–A14.
- Anchors declarados em A0 substituem o catálogo para fins de validação do reviewer (compara HTML contra os anchors declarados, não contra A1–A14).
- Quando A0 aparece em ≥2 slides, a regra de diversidade ≥2/≥3 arquétipos é suspensa (mono-arquétipo é fidelidade à referência, não preguiça).
- A0 não dispensa as regras técnicas hard do reviewer (contraste, overflow, ancoragem de foto profissional, data-variable, etc.).

**Anti-uso:**
- Free mode (sem referência). Sem âncora externa, A0 vira "designer faz o que quer" — use o catálogo.
- Quando a referência claramente cabe em A1–A14 com ajuste de coords (≤15% de desvio dos anchors da tabela). Use o A* mais próximo e documente o ajuste em `notes.md` — A0 não é atalho para evitar o catálogo.

---

## Como o reviewer usa o catálogo

- Confere que cada slide tem **um** A* declarado no `visual-plan.md`.
- Confere diversidade (regra de ≥2/≥3 arquétipos por tamanho de carrossel). **Exceção:** suspensa quando ≥2 slides usam A0 em reference-driven mode.
- Para cada slide, confere que os anchors do A* declarado têm contraparte plausível no HTML (não exige px exato — exige que `headline-zone` esteja onde a tabela define, com tolerância ±5% do canvas).
- Para A0: compara HTML contra os anchors declarados pelo art-director no `visual-plan.md` (não contra o catálogo). Tolerância ±5% também.
- Desvio silencioso (HTML não bate com A* sem nota) → finding `archetype-mismatch` severity blocker.
- Desvio documentado em `notes.md` com razão válida → aceito.
