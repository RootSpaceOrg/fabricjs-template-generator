---
name: gp2-html-reviewer
description: "Critique do HTML produzido por gp2-html-designer antes do marker. Gate determinístico (técnico via script) + julgamento visual de qualidade e coerência. Usa o visual-plan.md como referência de paleta e data-variable, mas não exige fidelidade composicional estrita. Use após gp2-html-designer, antes de gp2-template-marker. Não gera HTML, não converte Fabric, não publica."
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
artifacts/gp2-art-director/<slug>/visual-plan.md   ← paleta e data-variable de referência
artifacts/gp2-html-designer/<slug>/
├── template.html          ← high-fi final
├── screenshots/slide-N.png
└── notes.md               ← decisões e divergências documentadas pelo designer
```

Se faltar screenshots, renderize antes:

```bash
node ../../scripts/render-html-screenshots.js artifacts/gp2-html-designer/<slug>/
```

## Workflow

1. **Leia `visual-plan.md`** para extrair: hexs de primary/secondary, neutros, mapeamento de data-variable. Não use o plano para checar composição — use para checar paleta e variáveis.
2. Leia `notes.md` para entender decisões de design e divergências documentadas pelo designer.
3. Rode o gate técnico:

```bash
python3 ../../scripts/review-html-design.py artifacts/gp2-html-designer/<slug>/
```

O script gera `html-review.json` + `html-review.md`. Leia os findings.

4. Inspecione visualmente cada `screenshots/slide-N.png` (ver critérios abaixo).
5. Decida o status final.

| Status | Quando |
|--------|--------|
| `PASS` | zero findings técnicos críticos. Design tem qualidade visual suficiente para avançar. |
| `REVISE` | qualquer finding técnico crítico, OU design visualmente fraco/genérico que o agente julga insuficiente para publicar. |
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
- `<img data-image-type="professionalPhoto">` "voando" — figura sem ancoragem inferior nem sobreposição no terço inferior. Condições válidas: (1) `top + height ≥ canvas_height − 80px`, OU (2) outro elemento visível sobrepõe o terço inferior do slot.
- Elemento com `linear-gradient` ou `radial-gradient` sem `data-darken` (e sem `data-glow`) — gradiente será perdido no conversor.
- Cores brand hex em gradientes lineares — fundo brand = sólido + overlay neutro.

## Checklist de data-variable (HARD-GATE quando ausente)

Compare o HTML com o mapeamento de data-variable do visual-plan:
- Elementos listados no mapeamento têm `data-variable` + `data-variable-target` aplicados?
- Overlays de escurecimento sobre fundo brand têm `data-darken` + `data-darken-opacity`?
- Glows atmosféricos têm `data-glow` + `data-glow-variable` + `data-glow-alpha`?

Se um elemento mapeado não tem o atributo — é finding crítico.

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
    { "slide": 1, "issue": "...", "severity": "blocker", "fix": "..." }
  ],
  "dataVariableCheck": {
    "verdict": "complete|partial|missing",
    "issues": [
      { "element": "...", "expected": "data-variable=\"primary\"", "found": "ausente" }
    ]
  },
  "visualJudgment": {
    "verdict": "strong|adequate|weak",
    "notes": "..."
  }
}
```

E `html-review.md` para humanos:

```markdown
# Revisão HTML — <slug>

**Status:** PASS|REVISE|FAIL

## Findings técnicos (bloqueantes)
- Slide 2: título sai 30px do canvas direito → reduzir width do `<h1>` para 960px.

## data-variable
- Fundo slide 3 brand: sem data-variable → adicionar `data-variable="primary" data-variable-target="background"` na `<section>`.
- Demais: OK.

## Julgamento visual
- Hierarquia: forte — título > subtítulo > corpo instantâneo.
- Diversidade: adequada — 4 composições distintas em 6 slides.
- Coerência: boa — paleta consistente, movimento decorativo presente.
- Tom: alinhado com o segmento do brief.
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
Findings técnicos: <N> críticos, <M> warnings
data-variable: <N> de <total> elementos mapeados com atributos corretos
Julgamento visual: strong|adequate|weak
Evidência: <path>/html-review.md
Próximo passo: gp2-template-marker | gp2-html-designer (revisão) | gp2-art-director | gp2-request-interpreter
```

## O que esta skill NÃO faz

- Não gera HTML novo. Apenas critica.
- Não aplica correções; produz lista para o designer.
- Não roda o validador Fabric (`validate-slides.js`) — esse é o `gp2-template-converter`.
- Não exige fidelidade composicional estrita ao visual-plan — avalia qualidade do resultado.
