# Catálogo de Composições (A*)

Vocabulário composicional compartilhado entre `gp2-art-director` (escolhe), `gp2-html-designer` (executa) e `gp2-html-reviewer` (confere variedade).

Cada arquétipo é um **esqueleto inicial** — o designer adapta coords exatas mas mantém anchors gerais. Desvios devem ser justificados em `notes.md`. O reviewer aceita desvios documentados; flagra desvio silencioso.

**Regras de uso (art-director):**
- Carrosséis com ≥3 slides usam ≥2 arquétipos distintos.
- Carrosséis com ≥5 slides usam ≥3 arquétipos distintos.
- Slide CTA final tipicamente em `A6-cta-button-anchored` ou variante.
- Slide capa tipicamente em `A1`, `A2`, `A10` ou `A12`.

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

## Como o reviewer usa o catálogo

- Confere que cada slide tem **um** A* declarado no `visual-plan.md`.
- Confere diversidade (regra de ≥2/≥3 arquétipos por tamanho de carrossel).
- Para cada slide, confere que os anchors do A* declarado têm contraparte plausível no HTML (não exige px exato — exige que `headline-zone` esteja onde a tabela define, com tolerância ±5% do canvas).
- Desvio silencioso (HTML não bate com A* sem nota) → finding `archetype-mismatch` severity blocker.
- Desvio documentado em `notes.md` com razão válida → aceito.
