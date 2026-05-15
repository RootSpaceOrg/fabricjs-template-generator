---
name: gp2-html-reviewer
description: "Critique do HTML produzido por gp2-html-designer antes do marker. Gate determinístico (técnico) + julgamento visual do agente. Use após gp2-html-designer, antes de gp2-template-marker. Não gera HTML, não converte Fabric, não publica."
---

# gp2-html-reviewer

Critica o `template.html` final do designer (Passo 3 high-fi) antes de seguir para o marker.

## Princípio

O reviewer tem **duas responsabilidades separadas**:

1. **Gate técnico determinístico** — o script `review-html-design.py` detecta problemas mecânicos (overflow, texto cortado, sobreposição não-intencional, fontes faltando, etc.). Qualquer finding crítico bloqueia. Warnings do script também precisam de atenção, mas o reviewer pode aceitá-los com justificativa quando são consequência de uma escolha de design consciente documentada em `notes.md`.

2. **Julgamento visual do agente** — inspecionar os screenshots e decidir se o design tem qualidade suficiente para avançar. Aqui o agente usa seu próprio critério; não depende de ferramentas externas. O objetivo é evitar templates que passam no gate técnico mas estão visualmente fracos, genéricos ou mal executados.

## Inputs

```
artifacts/gp2-html-designer/<slug>/
├── template.html          ← high-fi final
├── screenshots/slide-N.png
└── notes.md               ← decisões do designer (família estética, movimento memorável)
```

Se faltar screenshots, renderize antes:

```bash
node ../../scripts/render-html-screenshots.js artifacts/gp2-html-designer/<slug>/
```

## Workflow

1. Leia `notes.md` para entender as escolhas conscientes do designer.
2. **Detecte o modo:** verifique se `artifacts/gp2-request-interpreter/<slug>/reference-spec.md` existe. Se sim, é reference-driven — você precisa checar aderência ao spec além das checagens normais.
3. Rode o preflight determinístico:

```bash
python3 ../../scripts/review-html-design.py artifacts/gp2-html-designer/<slug>/
```

Esse script gera `html-review.json` + `html-review.md` e roda o gate Impeccable internamente.

4. Inspecione visualmente cada `screenshots/slide-N.png` aplicando os critérios de julgamento visual abaixo.
5. **Em reference-driven mode:** compare screenshots × `reference-spec.md`. Acuse drift como finding técnico se:
   - Hexs aplicados não batem com a paleta declarada (tolerância: ΔE > 10 entre cor aplicada e cor do spec).
   - Família tipográfica usada está em categoria diferente da declarada (ex: spec pediu serifa display, designer usou sans).
   - Movimento memorável declarado não está visível.
   - Elementos editoriais listados no spec estão ausentes.
   - Se o designer divergiu **e** documentou em `notes.md` (ex: "Bebas Neue indisponível, usei Anton"), trate como warning, não bloqueio.
6. Decida o status final:

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
- `<section class="slide">` sem `data-width` / `data-height`.
- `<img data-image-type="professionalPhoto">` (ou `class="professional-photo"`) com `object-fit: cover` ou `border-radius` arredondado quando o brief não pediu avatar circular — perde o efeito do cutout PNG e quebra o anchor `bottom-center` do runtime. Esperado: `object-fit: contain; object-position: bottom center; border-radius: 0;` (ver [`gp2-html-designer/references/professional-photo-placements.md`](../gp2-html-designer/references/professional-photo-placements.md)).
- `<img data-image-type="professionalPhoto">` posicionada de forma que a face da figura (zona superior do slot, ~30% da altura) é coberta por texto ou outro elemento visível — leitor não consegue avaliar confiança.
- `<img data-image-type="professionalPhoto">` (cutout) com slot cuja proporção (`width / height`) diverge muito da proporção natural do PNG placeholder (~3:4 ≈ `0.78`). **Tolerância**: `0.55–1.10`. Fora dessa faixa, o `object-fit: contain` deixa metade do slot vazio e o converter facilmente erra a emissão Fabric (sintoma: figura cobrindo só metade do slot no editor). Exemplos: slot `540×1200` (ratio `0.45`) é alto demais; slot `540×400` (ratio `1.35`) é largo demais. **Fix**: ajustar `width`/`height` da `<img>` para uma proporção entre `9:16` e `1:1` (ratio `0.56`–`1.00`) que respeite a figura inteira sem ficar com áreas vazias dominantes. Ver [`gp2-html-designer/references/professional-photo-placements.md`](../gp2-html-designer/references/professional-photo-placements.md) para slots aprovados por canvas.
- `<img data-image-type="professionalPhoto">` "voando" — figura posicionada sem ancoragem inferior nem sobreposição na parte de baixo. Como fotos de usuário são busto/tronco (não corpo inteiro), deixar espaço vazio abaixo da figura parece que a pessoa não tem pernas. **Hard-gate**: toda `professionalPhoto` deve satisfazer **uma das duas condições**: (1) `top + height ≥ canvas_height − 80px` (ancorada na borda inferior do slide com margem máxima de 80px), OU (2) outro elemento visível (faixa de cor, foto contextual, bloco CTA, rodapé) sobrepõe o terço inferior do slot (`top + height * 0.67`). Se nenhuma condição for satisfeita, devolva `REVISE` com instrução de reposicionar ou remover a foto. Ver [`gp2-html-designer/references/professional-photo-placements.md`](../gp2-html-designer/references/professional-photo-placements.md) §"Princípios".

## Aderência ao spec (somente reference-driven, HARD-GATE quando não documentado em notes.md)

- Hexs aplicados não batem com paleta declarada (ΔE > 10 sem documentação).
- Família tipográfica em categoria diferente da declarada (serifa ↔ sans, condensada ↔ regular) sem documentação.
- Movimento memorável declarado ausente do design.
- Elementos editoriais listados no spec ausentes (eyebrow numerado faltando, fios horizontais ausentes, etc.).
- Tratamento de foto profissional difere do spec (spec pediu retangular editorial, designer usou avatar circular).

## Critérios de julgamento visual do agente

O agente olha para os screenshots e se pergunta:

| Critério | PASS se… | REVISE se… |
|----------|----------|------------|
| **Identidade visual** | O carrossel tem uma assinatura reconhecível (família estética, paleta, movimento memorável) | Parece um template genérico sem personalidade — poderia ser de qualquer ferramenta |
| **Hierarquia** | Título → subtítulo → corpo é instantâneo em cada slide | Tudo parece do mesmo peso; o olho não sabe por onde começar |
| **Ritmo do carrossel** | Slides têm composições visualmente distintas entre si; capa, miolo e CTA são reconhecíveis pelo layout | Todos os slides parecem o mesmo layout com texto diferente |
| **Movimento memorável** | Existe ao menos um elemento editorial consistente e não-genérico (eyebrow numerado, fio horizontal, número de slide gigante, etc.) | O design poderia ter sido feito no Canva sem nenhuma escolha editorial própria |
| **Tipografia** | Pelo menos dois pesos ou famílias distintos; tamanhos seguem escala com intenção | Uma só família, um só peso, tamanhos arbitrários |
| **Fidelidade ao brief** | O design reflete o tom e conteúdo pedido | O design poderia ser de qualquer nicho de saúde sem nenhuma adaptação |

O agente não precisa atingir todos os critérios para dar PASS — precisa ter uma visão de conjunto. Um design fortemente intencional pode ser incomum em alguns critérios e ainda assim ser forte. A pergunta-chave é: **"Eu publicaria isso no HealthMarket?"**

## Output

Sobrescreva `html-review.json` com a classificação, incluindo o campo `intentional`:

```json
{
  "status": "PASS|REVISE|FAIL",
  "technicalFindings": [
    { "slide": 1, "issue": "...", "severity": "blocker", "fix": "..." }
  ],
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

## Julgamento visual
- Identidade: forte — eyebrow numerado + tipografia display serif consistente em todos os slides.
- Ritmo: adequado — capa / miolo educativo / CTA têm layouts distintos.
- Veredito: publicável.

## Próximo passo
- PASS → gp2-template-marker
- REVISE → gp2-html-designer com lista acima
- FAIL → reabrir brief com gp2-request-interpreter
```

## Loop de revisão

Máximo **2 revisões**. Após o segundo `REVISE` ainda falhar, devolva `FAIL` e escale para o orquestrador anotar bloqueio.

## Resposta final ao orquestrador

```markdown
Revisão HTML: PASS|REVISE|FAIL
Artifact: <path>
Findings técnicos: <N>
Findings estilísticos: <N> (sendo <M> intencionais)
Evidência: <path>/html-review.md
Próximo passo: gp2-template-marker | gp2-html-designer (revisão) | gp2-request-interpreter (fail)
```

## O que esta skill NÃO faz

- Não gera HTML novo. Apenas critica.
- Não aplica correções; produz lista para o designer.
- Não roda o validador Fabric (`validate-slides.js`) — esse é o `gp2-template-converter`.
- Não decide se o template tem mercado/funcionalidade — só visual + estrutural.
