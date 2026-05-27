---
name: gp2-html-reviewer
description: "Critique do HTML produzido por gp2-html-designer antes do marker. Gate determinístico (técnico via review-html-design.py + anti-patterns como card-spam/nested-cards/lazy-centering/cold-gray/generic-gradient) + checks contra o visual-plan: archetype fidelity (A* declarado vs executado), move execution (M* declarado vs presente), typography conformance (escala resolvida) e reference fidelity (modo reference-driven). PASS exige ≥1 delight detail. Recebe os 3 conjuntos do designer (v1-lowfi, v2-midfi, final) para detectar regressões. Use após gp2-html-designer, antes de gp2-template-marker. Não gera HTML, não converte Fabric, não publica."
---

# gp2-html-reviewer

Critica o `template.html` final do designer antes de seguir para o marker.

## Princípio

O reviewer tem **duas responsabilidades separadas**:

1. **Gate técnico determinístico** — o script `review-html-design.py` detecta problemas mecânicos (overflow, texto cortado, sobreposição não-intencional, fontes faltando, etc.). Qualquer finding crítico bloqueia.

2. **Julgamento visual de qualidade** — inspecionar os screenshots e decidir se o template tem qualidade visual suficiente para publicar. O critério não é "executou o plano linha a linha?" — é "está publicável? tem hierarquia clara? é coerente como peça? reflete o tom do segmento?".

O designer tem liberdade criativa. O reviewer não devolve um template por ter feito escolhas diferentes das do visual-plan — devolve por qualidade insuficiente ou problemas técnicos.

## Inputs

```
artifacts/gp2-art-director/<slug>/visual-plan.md   ← paleta, tipografia resolvida, arquétipos A*, moves M*, data-variable
artifacts/gp2-html-designer/<slug>/
├── template-v1-lowfi.html       ← Passo 1 do designer
├── screenshots-v1-lowfi/slide-N.png
├── template-v2-midfi.html       ← Passo 2
├── screenshots-v2-midfi/slide-N.png
├── template.html                ← Passo 3 (high-fi final)
├── screenshots/slide-N.png
└── notes.md                     ← 3 critiques + decisões + desvios
```

Recebe os **3 conjuntos** (lowfi → midfi → final). Use a progressão para detectar regressões — se um slide tinha hierarquia forte no v1 mas perdeu identidade no high-fi, é finding `regression-in-final`.

Se faltar screenshots de algum passo, renderize antes:

```bash
node ../../scripts/render-html-screenshots.js artifacts/gp2-html-designer/<slug>/ --variant <v1-lowfi | v2-midfi | final>
```

## Workflow

1. **Leia `visual-plan.md`** para extrair: hexs de primary/secondary, neutros, **escala tipográfica resolvida**, **arquétipo A* por slide**, **moves M* declarados**, mapeamento de data-variable.
2. **Leia `notes.md`** completo — incluindo as 3 critiques do designer e quaisquer pedidos ao art-director que foram respondidos.
3. Rode o gate técnico:

```bash
python3 ../../scripts/review-html-design.py artifacts/gp2-html-designer/<slug>/
```

O script gera `html-review.json` + `html-review.md`. Leia os findings.

4. **Inspecione os 3 conjuntos de screenshots:**
   - `screenshots-v1-lowfi/` — composição estrutural por slide
   - `screenshots-v2-midfi/` — paleta + data-variable aplicados
   - `screenshots/` — final com moves e delight
   Use a progressão para detectar regressões (qualidade caiu entre N e N+1).
5. **Confira arquétipos**: para cada slide, o A* declarado tem contraparte visual no HTML final? Anchors do arquétipo estão preservados (tolerância ±5% do canvas). **Para `A0-custom-from-reference`:** compare o HTML contra os **anchors declarados pelo art-director** no `visual-plan.md` (não contra o catálogo A1–A14). Tolerância ±5% também. Se o art-director declarou A0 sem listar anchors → finding `archetype-mismatch` blocker (A0 sem anchors é decisão sem contrato).
6. **Confira moves**: cada M* declarado tem evidência visual nos slides indicados?
7. **Confira tipografia**: famílias declaradas no plano estão executadas? Pesos e tamanhos seguem a escala?
8. **Confira fidelidade à referência** (reference-driven mode apenas — ver seção dedicada).
9. **Confira delight detail**: existe ≥1 detalhe identificável?
9b. **Confira brand logo**: slide 1 (capa) E último slide (CTA) têm `<img data-image-type="brandLogo">`? Cada logo encosta numa borda lateral (`left ≤ 32` ou `left + width ≥ data-width − 32`)? Nenhum logo sobrepõe headline/body/foto? Ausências sem justificativa no `visual-plan.md` ou `notes.md` → finding `brand-logo-missing-on-cover-or-cta`.
10. Decida o status final.

| Status | Quando |
|--------|--------|
| `PASS` | zero findings técnicos críticos. Arquétipos e moves executados (ou desvios documentados). Tipografia conforme escala. ≥1 delight detail. Em reference-driven mode: paletteMatch + typographyMatch ≥ loose. |
| `REVISE` | qualquer finding crítico, OU design sem delight detail, OU arquétipo/move silenciosamente divergente, OU regressão entre passos. |
| `FAIL` | direção do design é fundamentalmente errada; reabrir no `gp2-html-designer` (ou art-director se a orientação era ruim). |

## Findings técnicos (HARD-GATE — sempre bloqueiam)

Cada item abaixo é um check acionável aplicado contra o `template.html`. Para as regras de fundo (estrutura, CSS inline, gradientes obrigatórios), ver [`../_shared/HTML_TECHNICAL_SPEC.md`](../_shared/HTML_TECHNICAL_SPEC.md) e [`../_shared/GRADIENT_SYSTEM.md`](../_shared/GRADIENT_SYSTEM.md) — esta lista é a tradução em findings concretos.

- Texto fora do canvas (left/top + width/height ultrapassa data-width/height).
- Sobreposição não-intencional entre conteúdo e conteúdo (texto sobre texto, foto sobre título).
- Contraste WCAG AA < 4.5:1 para body, < 3.0:1 para títulos grandes (≥ 24pt).
- Texto cortado (overflow vertical dentro do `<p>`/`<h*>`).
- `<img>` sem `src` ou com `src` quebrado.
- Slide sem conteúdo principal identificável.
- Fonte usada no CSS ausente do `<meta name="hm-fonts">`.
- Placeholder de imagem complexo (texto, anatomia, ícones) — viola CLAUDE_DESIGN_RULES seção 6.
- Pseudo-elementos `::before`/`::after`, `@keyframes`, `mix-blend-mode`, `backdrop-filter` complexo.
- Posicionamento via flex/grid dentro de `.slide` (deve ser absoluto).
- `box-shadow` com cor brand (`rgba(R,G,B,A)` onde RGB ≠ 0,0,0 e a cor corresponde a primary/secondary da paleta) — sombras devem ser neutras para adaptabilidade.
- Círculo/div com `opacity` parcial + `background` sólido brand (sem `radial-gradient`) pretendendo ser glow atmosférico — DEVE usar `data-glow="center"` com `radial-gradient(circle, ...)`.
- Elemento com `data-glow` faltando `data-glow-variable` ou `data-glow-alpha`.
- `data-glow-variable` com valor diferente de `primary` ou `secondary`.
- `<section class="slide">` sem `data-width` / `data-height`.
- `<img data-image-type="professionalPhoto">` com `object-fit: cover` ou `border-radius` arredondado quando o brief não pediu avatar circular. Esperado: `object-fit: contain; object-position: bottom center; border-radius: 0;`.
- `<img data-image-type="professionalPhoto">` com a face da figura coberta por texto ou elemento visível (~30% superior do slot).
- `<img data-image-type="professionalPhoto">` (cutout) com slot cuja proporção (`width / height`) está fora de `0.55–1.10`. Fora dessa faixa, `object-fit: contain` deixa metade do slot vazio e o converter erra a emissão Fabric.
- `<img data-image-type="professionalPhoto">` "voando" — figura sem ancoragem inferior real nem sobreposição alinhada com elemento abaixo. Condições válidas (uma das duas):
  1. `top + height ≥ canvas_height − 8px` (slot encosta na borda inferior real do slide, zero margem).
  2. Outro elemento visível (foto contextual, faixa de cor, bloco CTA) tem `top + height` dentro de ±8px do `top + height` do slot da foto profissional **E** sobrepõe horizontalmente ≥40% da largura do slot — ou seja, o bottom do slot da foto coincide com o bottom de um elemento ancorador. Antes a tolerância era 80px; foi endurecida porque mesmo 70px de gap renderiza visualmente como "pessoa flutuando".
- `<img data-image-type="professionalPhoto">` centralizado horizontalmente — o slot precisa encostar numa borda lateral (`left ≤ 8px` OU `left + width ≥ canvas_width − 8px`). Cutout no meio do canvas sem âncora lateral cria efeito "pessoa no meio do nada".
- Elemento com `linear-gradient` ou `radial-gradient` sem `data-darken` (e sem `data-glow`) — gradiente será perdido no conversor.
- Cores brand hex em gradientes lineares — fundo brand = sólido + overlay neutro.

### Findings novos — composição e anti-patterns

Cada finding novo carrega `code`, `slide`, `issue`, `severity`, `fix`. Detectados parcialmente pelo `review-html-design.py` (regras determinísticas), parcialmente por inspeção do agente.

- **`archetype-mismatch`** (blocker): slide cuja composição executada não corresponde ao arquétipo A* declarado no `visual-plan.md` **sem** justificativa em `notes.md`. Para `A0-custom-from-reference`, compara contra os anchors declarados pelo art-director, não contra o catálogo. A0 declarado sem anchors também cai aqui. Fix: documentar desvio com razão, voltar ao arquétipo, ou (em A0) declarar os anchors no plano.
- **`low-diversity`** (blocker): 3+ slides consecutivos com mesmo arquétipo A*. Carrossel viola regra de diversidade do art-director. Fix: trocar arquétipo de 1+ slide. **Exceção:** suspenso quando o `visual-plan.md` está em reference-driven mode E ≥2 slides usam `A0-custom-from-reference` E o plano declara `## Decisão composicional: custom-anchors` (ou `hybrid` com A0 nos slides repetidos) com justificativa — mono-arquétipo é fidelidade à referência, não preguiça.
- **`move-missing`** (blocker): move M* declarado no plano mas ausente do HTML em todos os slides indicados. Fix: aplicar o move conforme `_shared/CAROUSEL_MOVES.md`.
- **`typography-divergence`** (blocker quando família, warning quando peso/tamanho): tipografia executada não bate com a escala resolvida em `visual-plan.md` sem justificativa em `notes.md`. Fix: ajustar para escala ou documentar.
- **`card-spam`** (warning ≥3 elementos; blocker ≥4): elementos com `border` + `border-radius` + `box-shadow` simultaneamente no mesmo slide. Fix: remover ornamentação redundante.
- **`nested-cards`** (blocker): card com `border` contendo outro card com `border`. Fix: remover hierarquia desnecessária.
- **`lazy-centering`** (warning): 100% dos textos do slide com `text-align: center` E todos posicionados na coluna central. Fix: introduzir alinhamento intencional.
- **`cold-gray`** (warning): uso de `#CCCCCC`, `#999999`, `#666666` literais em fundo ou texto principal. Fix: usar neutro com tint do brief.
- **`generic-gradient`** (warning): gradiente roxo→rosa, azul→roxo ou similar sem propósito declarado. Fix: usar `data-darken` neutro ou remover.
- **`regression-in-final`** (warning): qualidade caiu entre v2-midfi e final (ex: hierarquia clara em v2 que ficou poluída no high-fi). Fix: simplificar moves/ornamentação.
- **`no-delight-detail`** (warning): nenhum detalhe identificável (ver seção §"Delight detail"). Em modo qualidade-alta, escala para blocker.
- **`brand-logo-missing-on-cover-or-cta`** (warning): ausência de `<img data-image-type="brandLogo">` no slide 1 (capa) OU no último slide (CTA), sem justificativa no `visual-plan.md → ## Logo da marca` ou em `notes.md`. Default canônico exige logo nessas duas posições. Fix: aplicar `brandLogo` numa das extremidades conforme `references/placeholders/README.md §"Logo da marca"`, ou documentar por que omitir (ex: "brief pediu visual minimal sem logo").
- **`brand-logo-not-anchored`** (warning): `<img data-image-type="brandLogo">` posicionado sem encostar em borda lateral real (`left > 32px` E `left + width < data-width − 32px`) — logo centralizado horizontalmente cria efeito "selo solto". Fix: encostar em borda esquerda ou direita conforme padrões do catálogo.
- **`brand-logo-over-content`** (blocker): `brandLogo` sobreposto a `<h1>`/`<h2>`/`<p>` (headline/body) ou a `<img data-image-type="professionalPhoto|userAsset">`. Fix: reposicionar para área limpa ou remover do slide.

## Checklist de data-variable (HARD-GATE quando ausente)

Compare o HTML com o mapeamento de data-variable do visual-plan:
- Elementos listados no mapeamento têm `data-variable` + `data-variable-target` aplicados?
- Overlays de escurecimento sobre fundo brand têm `data-darken` + `data-darken-opacity`?
- Glows atmosféricos têm `data-glow` + `data-glow-variable` + `data-glow-alpha`?

Se um elemento mapeado não tem o atributo — é finding crítico.

## Reference fidelity (reference-driven mode only)

Quando `visual-plan.md → ## Modo: reference-driven`, o reviewer compara o HTML executado contra o vocabulário visual extraído da referência (paleta, tipografia, elementos editoriais listados em "Elementos editoriais a replicar").

**Pré-check (HARD-GATE):** o `visual-plan.md` deve conter a seção `## Análise da referência` com a checklist preenchida (background, gradientes, paleta, tipografia, composição, elementos editoriais, identidade da marca presente, imagens, CTAs, navegação) E a subseção `### Síntese` com "Vocabulário visual a herdar" + "Ruídos detectados". Se ausente → finding `reference-checklist-missing` (blocker). Sem a checklist, o art-director pulou a análise sistemática e o resto da validação de fidelidade fica em areia movediça.

**Validação de slots vs ruídos:**

O `visual-plan.md` em reference-driven mode tem duas listas distintas na síntese: **slots da plataforma identificados** (replicar como `data-image-type` / `data-text-type`) e **ruídos a descartar** (não replicar).

- **Slots da plataforma:** para cada item listado como slot (ex: `instagramProfilePicture`, `instagramName`, `instagramHandle`, `brandLogo`, `phone`, `address`), confira que o HTML final **tem o atributo correto aplicado** no elemento correspondente. Slot esperado mas ausente → finding `reference-slot-missing` (blocker). Slot presente com tipo errado (ex: avatar circular marcado como `professionalPhoto` em vez de `instagramProfilePicture`) → finding `reference-slot-mistyped` (blocker).

- **Ruídos descartados:** para cada item da lista "NÃO replicar" (logo da marca de origem específica, selo verificado de plataforma, métricas de UI da plataforma como "5,874 views", hashtags de copy de nicho, marca d'água, QR code, ícones de redes sociais como decoração, selos promocionais, CTA de serviço quando o batch é multi-nicho), confira que **não aparece** no HTML final. Se aparecer → finding `reference-noise-leaked` (blocker). Esta validação é especialmente crítica para batches do `gp2-template-suggester` (multi-nicho).

**Não confunda slot com ruído:** um `instagramProfilePicture` no HTML final é **correto** quando a referência tinha avatar circular de post; só vira finding se o art-director não listou na síntese como slot. A validação é contra a síntese do plano, não contra heurística genérica.

| Check | Tight | Loose | Diverged |
|-------|-------|-------|----------|
| Paleta | hexs do HTML batem com os declarados (Δ < 5% em RGB) | hexs próximos mas distintos (Δ 5–15%) | hexs muito diferentes (Δ > 15%) |
| Tipografia | famílias declaradas executadas | famílias da mesma categoria (ex: ambas serifas display) | categoria diferente (serif → sans) |
| Elementos editoriais | todos os listados em "Elementos editoriais a replicar" presentes | maioria presente, 1 ausente | maioria ausente |

`diverged` em paleta ou tipografia **sem** justificativa em `notes.md` → finding crítico (`reference-divergence`).

## Delight detail

Para o template alcançar `PASS`, deve haver **pelo menos 1 delight detail** identificável. Lista de detalhes que contam:

- **Tracking notável** no eyebrow ou caption (`letter-spacing` ≥ +12% ou ≤ -3%).
- **Contraste de peso** — pesos 400 e 800 lado a lado intencionalmente.
- **Número editorial decorativo** — número grande (≥300px) usado como ornamento (move M2 ou similar).
- **Color block intencional** — bloco sólido brand em posição calculada, não preenchimento default.
- **Fio tipográfico fino** — divisor 1–3px sob título/eyebrow (move M8).
- **Sobreposição calculada** — overlap entre elementos com intenção compositiva (não acidente).
- **Ligadura ou ornamento tipográfico** — uso de fonte com features especiais (italic, swash, small-caps).
- **Headline-overflow** — título extrapolando borda do slide com propósito (move M10).
- **Bleed entre slides** — elemento contínuo entre slides consecutivos (move M3).

Registre quais delight details estão presentes em `html-review.json → delightDetails`. Lista vazia → finding `no-delight-detail` (default warning; blocker em modo qualidade-alta).

## Critérios de julgamento visual

O reviewer avalia qualidade e publicabilidade — não fidelidade composicional ao visual-plan.

### Checklist de qualidade (verificar slide por slide)

| Critério | PASS se… | REVISE se… |
|----------|----------|------------|
| **Hierarquia** | Título → subtítulo → corpo é instantâneo em cada slide | Tudo parece do mesmo peso; o olho não sabe por onde começar |
| **Contraste legível** | Texto é confortavelmente legível sobre o fundo | Texto raspa no fundo, especialmente em slides escuros/brand |
| **Paleta coerente** | Os hexs do visual-plan estão aplicados corretamente nos slides | Cores diferentes do plano sem documentação em notes.md |
| **Tipografia** | Pelo menos dois pesos ou famílias distintos; escalas com intenção | Uma só família, um só peso; tamanhos sem hierarquia |
| **Diversidade de layout** | Slides têm composições visivelmente distintas entre si | 3+ slides consecutivos com composição idêntica ("mesmo layout, texto diferente") |
| **Coerência visual** | O carrossel parece uma peça única com identidade reconhecível | Slides parecem desconexos; mudanças de estilo sem intenção |
| **Tom do segmento** | O design reflete o segmento e tom do brief | O design poderia ser de qualquer vertical sem nenhuma adaptação |
| **Anti-patterns** | Livre de card spam, nested cards, tudo centralizado sem intenção | Card spam repetitivo, nested cards, composição genérica de IA |
| **Delight detail** | ≥1 detalhe identificável: tracking notável, contraste forte de peso, número editorial decorativo, sobreposição calculada, color block intencional, fio tipográfico fino, ligadura/ornamento | Nenhum detalhe — template visualmente "default" de IA |

### Como ponderar divergências do visual-plan

- Divergência documentada em `notes.md` com justificativa válida → trate como **informação**, não bloqueio.
- Divergência não documentada em paleta ou data-variable → trate como **finding** (rastreabilidade importa).
- Divergência de composição não documentada → avalie pela qualidade do resultado, não pela fidelidade. Se o resultado é melhor, aceite e oriente o designer a documentar.

A pergunta-chave é: **"O template tem qualidade visual suficiente para publicar e não tem problemas técnicos?"**

## Output

Sobrescreva `html-review.json`:

```json
{
  "status": "PASS|REVISE|FAIL",
  "technicalFindings": [
    { "code": "card-spam", "slide": 1, "issue": "...", "severity": "blocker|warning", "fix": "..." }
  ],
  "dataVariableCheck": {
    "verdict": "complete|partial|missing",
    "issues": [
      { "element": "...", "expected": "data-variable=\"primary\"", "found": "ausente" }
    ]
  },
  "archetypeFidelity": {
    "verdict": "tight|loose|diverged",
    "perSlide": [
      { "slide": 1, "declared": "A1-hero-split", "executed": "A1-hero-split", "match": "tight" },
      { "slide": 2, "declared": "A3-editorial-eyebrow-stack", "executed": "A3-editorial-eyebrow-stack", "match": "tight" }
    ],
    "diversityCount": 4
  },
  "moveExecution": {
    "verdict": "complete|partial|missing",
    "declared": ["M2-numero-ostentatorio", "M4-cta-arrow-ritualistico"],
    "observed": ["M2-numero-ostentatorio", "M4-cta-arrow-ritualistico"],
    "missing": []
  },
  "typographyCheck": {
    "verdict": "tight|loose|diverged",
    "notes": "..."
  },
  "referenceFidelity": {
    "applicable": true,
    "paletteMatch": "tight|loose|diverged",
    "typographyMatch": "tight|loose|diverged",
    "editorialElementsPresent": ["eyebrow-numerado", "fio-horizontal"],
    "editorialElementsMissing": []
  },
  "delightDetails": ["tracking-eyebrow-tight", "numero-decorativo-slide-3"],
  "brandLogo": {
    "coverPresent": true,
    "ctaPresent": true,
    "otherSlides": [3],
    "anchorIssues": []
  },
  "visualJudgment": {
    "verdict": "strong|adequate|weak",
    "notes": "..."
  }
}
```

`referenceFidelity.applicable: false` quando `visual-plan.md` está em free mode.

E `html-review.md` para humanos:

```markdown
# Revisão HTML — <slug>

**Status:** PASS|REVISE|FAIL

## Findings técnicos (bloqueantes)
- [card-spam] Slide 2: 4 elementos com border+border-radius+box-shadow → remover sombra dos 2 acessórios menores.

## Findings de composição
- [archetype-mismatch] Slide 4: declarado A8-overlap-image-text, executado A3-editorial-eyebrow-stack sem nota → documentar ou voltar ao plano.

## data-variable
- Fundo slide 3 brand: sem data-variable → adicionar `data-variable="primary" data-variable-target="background"` na `<section>`.

## Arquétipos
- Diversidade: 4 tipos distintos em 6 slides ✓
- Slide 1: A1-hero-split ✓
- Slide 4: ✗ (ver finding acima)

## Moves
- M2-numero-ostentatorio: presente em slides 2, 3, 5 ✓
- M4-cta-arrow-ritualistico: presente em slides 1–5 ✓

## Tipografia
- Display: Playfair Display 700 ✓ conforme plano
- Body: Inter 400 ✓

## Reference fidelity (se reference-driven)
- Paleta: tight (todos os hexs Δ < 3% RGB)
- Tipografia: tight
- Elementos editoriais presentes: eyebrow-numerado, fio-horizontal
- Faltantes: nenhum

## Delight detail
- tracking-eyebrow-tight (eyebrow letter-spacing +14%)
- numero-decorativo-slide-3 (número 420px canto sup. direito)
- color-block-intencional (slide 5, bloco primary deslocado intencionalmente)

## Julgamento visual
- Hierarquia: forte — título > subtítulo > corpo instantâneo.
- Diversidade: adequada — 4 composições distintas em 6 slides.
- Coerência: boa — paleta consistente, moves M2+M4 presentes.
- Tom: alinhado com o segmento do brief.
- Regressão entre passos: nenhuma — high-fi acrescentou sem perder identidade do v2.
- Veredito: publicável com correção do data-variable faltante.

## Próximo passo
- PASS → gp2-template-marker
- REVISE → gp2-html-designer com lista acima
- FAIL → reabrir com gp2-art-director (orientação inadequada) ou gp2-request-interpreter (brief errado)
```

## Loop de revisão

Máximo **2 revisões**. Após o segundo `REVISE` ainda falhar, devolva `FAIL` e escale para o orquestrador.

## Resposta final ao orquestrador

```markdown
Revisão HTML: PASS|REVISE|FAIL
Artifact: <path>
Findings técnicos: <N> blockers, <M> warnings
data-variable: <N> de <total> elementos mapeados com atributos corretos
Arquétipos: <N> declarados / <N> executados (diversidade: <K> tipos distintos)
Moves: <complete | partial | missing> — observados: <lista>; faltantes: <lista>
Tipografia: <tight | loose | diverged>
Reference fidelity: <tight | loose | diverged | n/a (free mode)>
Delight details: <N> identificados
Brand logo: capa=<yes|no>, cta=<yes|no>, outros=[<slides>]
Julgamento visual: strong|adequate|weak
Evidência: <path>/html-review.md
Próximo passo: gp2-template-marker | gp2-html-designer (revisão) | gp2-art-director | gp2-request-interpreter
```

## O que esta skill NÃO faz

- Não gera HTML novo. Apenas critica.
- Não aplica correções; produz lista para o designer.
- Não roda o validador Fabric (`validate-slides.js`) — esse é o `gp2-template-converter`.
- Não exige fidelidade composicional estrita ao visual-plan — avalia qualidade do resultado.
