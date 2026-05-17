---
name: gp2-html-reviewer
description: "Critique do HTML produzido por gp2-html-designer antes do marker. Gate determinístico (técnico via script) + julgamento visual baseado no visual-plan.md do art-director. Sem Impeccable. Use após gp2-html-designer, antes de gp2-template-marker. Não gera HTML, não converte Fabric, não publica."
---

# gp2-html-reviewer

Critica o `template.html` final do designer (Passo 3 high-fi) antes de seguir para o marker.

## Princípio

O reviewer tem **duas responsabilidades separadas**:

1. **Gate técnico determinístico** — o script `review-html-design.py` detecta problemas mecânicos (overflow, texto cortado, sobreposição não-intencional, fontes faltando, etc.). Qualquer finding crítico bloqueia. Warnings do script também precisam de atenção, mas o reviewer pode aceitá-los com justificativa quando são consequência de uma escolha de design consciente documentada em `notes.md`.

2. **Julgamento visual do agente baseado no visual-plan** — inspecionar os screenshots e decidir se o designer executou o plano do art-director corretamente e com qualidade suficiente. O critério não é genérico ("parece bom?") — é específico ("o plano dizia A3 split assimétrico para o slide 2; está assim?"). Isso evita tanto templates fracos quanto templates fortes que fogem do plano definido.

Sem Impeccable. Sem ferramentas externas de julgamento visual. Apenas o script técnico + o agente comparando screenshots × visual-plan.

## Inputs

```
artifacts/gp2-art-director/<slug>/visual-plan.md   ← plano do art-director (LEIA PRIMEIRO)
artifacts/gp2-html-designer/<slug>/
├── template.html          ← high-fi final
├── screenshots/slide-N.png
└── notes.md               ← divergências documentadas pelo designer
```

Se faltar screenshots, renderize antes:

```bash
node ../../scripts/render-html-screenshots.js artifacts/gp2-html-designer/<slug>/
```

## Workflow

1. **Leia `visual-plan.md` inteiro.** Este é o plano que o designer deveria ter executado. Internalize: família estética, hexs de primary/secondary, tipo compositivo de cada slide (A1–A8), instrução do movimento memorável, tabela de data-variable.
2. Leia `notes.md` para entender divergências documentadas pelo designer (fonte substituída, ajuste de composição, etc.).
3. **Detecte o modo:** verifique se `visual-plan.md` tem `## Modo` = `reference-driven`. Se sim, o plano contém vocabulário visual extraído da referência — check adicional de aderência.
4. Rode o preflight determinístico:

```bash
python3 ../../scripts/review-html-design.py artifacts/gp2-html-designer/<slug>/
```

O script gera `html-review.json` + `html-review.md`. Leia os findings antes de prosseguir.

5. Inspecione visualmente cada `screenshots/slide-N.png` comparando com o visual-plan (ver critérios abaixo).
6. **Em reference-driven mode:** compare screenshots × seção "Vocabulário visual (extraído da referência)" do `visual-plan.md`. Acuse drift como finding técnico se:
   - Hexs aplicados não batem com a paleta declarada no plano (tolerância: ΔE > 10 sem documentação em notes.md).
   - Família tipográfica está em categoria diferente da declarada (serifa ↔ sans, condensada ↔ regular) sem documentação.
   - Movimento memorável declarado não está visível.
   - Elementos editoriais listados no plano estão ausentes.
   - Se divergiu **e** documentou em `notes.md`, trate como warning, não bloqueio.
7. Decida o status final:

| Status | Quando |
|--------|--------|
| `PASS` | zero findings técnicos críticos. Warnings do script aceitos com justificativa. Design tem qualidade visual suficiente para avançar. |
| `REVISE` | qualquer finding técnico crítico, ou design visualmente fraco/genérico que o agente julga insuficiente para publicar. |
| `FAIL` | direção do design é fundamentalmente errada; reabrir no `gp2-html-designer` (ou interpreter se o brief estava errado). |

## Findings técnicos (HARD-GATE — sempre bloqueiam)

- Texto fora do canvas (left/top + width/height ultrapassa data-width/height).
- Sobreposição não-intencional entre conteúdo e conteúdo (texto sobre texto, foto sobre título).
- Contraste WCAG AA < 4.5:1 para body, < 3.0:1 para títulos grandes (>= 24pt).
- Texto cortado (overflow vertical dentro do `<p>`/`<h*>`).
- `<img>` sem `src` ou com `src` quebrado.
- Slide sem conteúdo principal identificável.
- Fonte usada no CSS ausente do `<meta name="hm-fonts">`.
- Placeholder de imagem complexo (texto, anatomia, ícones) — viola CLAUDE_DESIGN_RULES seção 6.
- Pseudo-elementos `::before`/`::after`, `@keyframes`, `mix-blend-mode`, `backdrop-filter` complexo.
- Posicionamento via flex/grid dentro de `.slide` (deveria ser absoluto).
- `box-shadow` com cor brand (`rgba(R,G,B,A)` onde RGB ≠ 0,0,0 e a cor corresponde a primary/secondary da paleta) — sombras devem ser neutras (`rgba(0,0,0,N)`) para adaptabilidade de paleta.
- `<section class="slide">` sem `data-width` / `data-height`.
- `<img data-image-type="professionalPhoto">` (ou `class="professional-photo"`) com `object-fit: cover` ou `border-radius` arredondado quando o brief não pediu avatar circular — perde o efeito do cutout PNG e quebra o anchor `bottom-center` do runtime. Esperado: `object-fit: contain; object-position: bottom center; border-radius: 0;` (ver [`gp2-html-designer/references/professional-photo-placements.md`](../gp2-html-designer/references/professional-photo-placements.md)).
- `<img data-image-type="professionalPhoto">` posicionada de forma que a face da figura (zona superior do slot, ~30% da altura) é coberta por texto ou outro elemento visível — leitor não consegue avaliar confiança.
- `<img data-image-type="professionalPhoto">` (cutout) com slot cuja proporção (`width / height`) diverge muito da proporção natural do PNG placeholder (~3:4 ≈ `0.78`). **Tolerância**: `0.55–1.10`. Fora dessa faixa, o `object-fit: contain` deixa metade do slot vazio e o converter facilmente erra a emissão Fabric (sintoma: figura cobrindo só metade do slot no editor). Exemplos: slot `540×1200` (ratio `0.45`) é alto demais; slot `540×400` (ratio `1.35`) é largo demais. **Fix**: ajustar `width`/`height` da `<img>` para uma proporção entre `9:16` e `1:1` (ratio `0.56`–`1.00`) que respeite a figura inteira sem ficar com áreas vazias dominantes. Ver [`gp2-html-designer/references/professional-photo-placements.md`](../gp2-html-designer/references/professional-photo-placements.md) para slots aprovados por canvas.
- `<img data-image-type="professionalPhoto">` "voando" — figura posicionada sem ancoragem inferior nem sobreposição na parte de baixo. Como fotos de usuário são busto/tronco (não corpo inteiro), deixar espaço vazio abaixo da figura parece que a pessoa não tem pernas. **Hard-gate**: toda `professionalPhoto` deve satisfazer **uma das duas condições**: (1) `top + height ≥ canvas_height − 80px` (ancorada na borda inferior do slide com margem máxima de 80px), OU (2) outro elemento visível (faixa de cor, foto contextual, bloco CTA, rodapé) sobrepõe o terço inferior do slot (`top + height * 0.67`). Se nenhuma condição for satisfeita, devolva `REVISE` com instrução de reposicionar ou remover a foto. Ver [`gp2-html-designer/references/professional-photo-placements.md`](../gp2-html-designer/references/professional-photo-placements.md) §"Princípios".

## Aderência ao visual-plan (somente reference-driven, HARD-GATE quando não documentado em notes.md)

- Hexs aplicados não batem com paleta declarada no visual-plan (ΔE > 10 sem documentação).
- Família tipográfica em categoria diferente da declarada (serifa ↔ sans, condensada ↔ regular) sem documentação.
- Movimento memorável declarado ausente do design.
- Elementos editoriais listados no visual-plan ausentes (eyebrow numerado faltando, fios horizontais ausentes, etc.).
- Tratamento de foto profissional difere do visual-plan (plano pediu retangular editorial, designer usou avatar circular).

## Critérios de julgamento visual baseados no visual-plan

O agente compara os screenshots com o `visual-plan.md`. A pergunta não é "parece bom?" — é "o designer executou o plano corretamente e com qualidade?"

### Checklist de fidelidade ao plano (verificar slide por slide)

Para cada slide, abra o screenshot e compare com o plano:

| Critério | PASS se… | REVISE se… |
|----------|----------|------------|
| **Tipo compositivo** | O slide usa o código A1–A8 definido no plano (zona de headline, zona de imagem, densidade) | O layout é diferente do planejado sem justificativa em notes.md |
| **Paleta** | Os hexs de primary/secondary do plano estão aplicados corretamente; slides LIGHT/DARK/Brand usam os neutros/fundos definidos | Paleta diferente do plano; cinzas frios genéricos em vez dos neutros do plano |
| **Movimento memorável** | A instrução composicional do plano foi executada (posição, tamanho, cor, spacing conforme especificado) | Elemento ausente ou executado de forma diferente do que a instrução descreve |
| **data-variable** | Elementos da tabela de mapeamento têm os atributos `data-variable` / `data-variable-target` no HTML | Elementos brand-color sem atributo de variável |
| **Diversidade compositiva** | Slides consecutivos têm layouts visivelmente distintos; não é "mesmo layout com texto diferente" | 3+ slides consecutivos com composição idêntica ou quase idêntica |

### Checklist de qualidade de execução

| Critério | PASS se… | REVISE se… |
|----------|----------|------------|
| **Hierarquia** | Título → subtítulo → corpo é instantâneo em cada slide | Tudo parece do mesmo peso; o olho não sabe por onde começar |
| **Tipografia** | Pelo menos dois pesos ou famílias distintos; tamanhos seguem escala com intenção | Uma só família, um só peso, tamanhos arbitrários |
| **Identidade visual** | O carrossel tem uma assinatura reconhecível pela execução do plano | Parece template genérico — o plano não foi executado com fidelidade suficiente |
| **Fidelidade ao brief** | O design reflete o tom e vertical pedido | O design poderia ser de qualquer vertical sem nenhuma adaptação ao contexto |

### Como ponderar divergências documentadas

- Divergência documentada em `notes.md` com justificativa técnica válida (fonte indisponível, contraste obrigou ajuste) → trate como **warning**, não bloqueio.
- Divergência não documentada → trate como **finding técnico** (mesmo que pareça visualmente ok — a rastreabilidade importa).
- Divergência que melhora objetivamente o resultado → aceite, documente no `html-review.md`, e instrua o designer a atualizar o `notes.md`.

A pergunta-chave é: **"O designer executou o plano do art-director e o resultado está publicável?"**

## Output

Sobrescreva `html-review.json`:

```json
{
  "status": "PASS|REVISE|FAIL",
  "technicalFindings": [
    { "slide": 1, "issue": "...", "severity": "blocker", "fix": "..." }
  ],
  "planFidelity": {
    "verdict": "faithful|partial|diverged",
    "divergences": [
      { "slide": 2, "expected": "composição A3 split assimétrico", "found": "composição A2 split 50/50", "documented": false }
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
- Slide 2: título sai 30px do canvas direito → reduzir width do `<h1>` para 960px ou font-size para 88px.

## Fidelidade ao plano (visual-plan.md)
- Composições: slide 1 A1 ✓ | slide 2 A3 → implementado como A2 (não documentado) | slide 3 A2 ✓
- Paleta: hexs corretos em todos os slides ✓
- Movimento memorável: instrução executada ✓
- data-variable: 3 de 5 elementos marcados — faltou fundo do slide 3 Brand e eyebrow do slide 2

## Julgamento de execução
- Hierarquia: forte — título > subtítulo > corpo instantâneo.
- Diversidade compositiva: adequada — 3 tipos diferentes de composição.
- Veredito: publicável com correções dos data-variable faltantes.

## Próximo passo
- PASS → gp2-template-marker
- REVISE → gp2-html-designer com lista acima
- FAIL → reabrir com gp2-art-director (plano ruim) ou gp2-request-interpreter (brief errado)
```

## Loop de revisão

Máximo **2 revisões**. Após o segundo `REVISE` ainda falhar, devolva `FAIL` e escale para o orquestrador anotar bloqueio.

## Resposta final ao orquestrador

```markdown
Revisão HTML: PASS|REVISE|FAIL
Artifact: <path>
Findings técnicos: <N> críticos, <M> warnings
Fidelidade ao plano: faithful|partial|diverged (<N> divergências — <M> documentadas)
data-variable: <N> de <total> elementos marcados corretamente
Julgamento de execução: strong|adequate|weak
Evidência: <path>/html-review.md
Próximo passo: gp2-template-marker | gp2-html-designer (revisão) | gp2-art-director (plano inadequado) | gp2-request-interpreter (brief errado)
```

## O que esta skill NÃO faz

- Não gera HTML novo. Apenas critica.
- Não aplica correções; produz lista para o designer.
- Não roda o validador Fabric (`validate-slides.js`) — esse é o `gp2-template-converter`.
- Não decide se o template tem mercado/funcionalidade — só visual + estrutural.
- Não usa Impeccable nem nenhuma ferramenta externa de julgamento visual — apenas script técnico + agente lendo screenshots × visual-plan.
