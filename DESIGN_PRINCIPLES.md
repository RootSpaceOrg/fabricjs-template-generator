# Design Principles — Protocolo de 3 Renders

Este documento é o **manual obrigatório** do `gp2-html-designer`. O objetivo é levar a qualidade de design ao patamar do Claude Design, dentro de uma única skill, sem depender do Anthropic Labs.

## Princípio central

A v1 falhou porque o designer recebia um brief textual e escrevia HTML "às cegas" — só via o resultado depois, quando o `html-reviewer` rodava. Claude Design ganha porque o autor itera **no DOM renderizado** durante o design.

A v2 reproduz isso explicitando três passos com render obrigatório dentro do designer. O LLM passa a operar sobre evidência visual em vez de só texto.

## Os três passos

### Passo 1 — Esboço estrutural (low-fi)

**Objetivo:** travar layout, hierarquia, ritmo do carrossel.

Entrega:

- `template-v1.html` com:
  - `<section class="slide" data-width data-height>` por slide, posicionamento absoluto correto;
  - **caixas cinzas neutras** (`#E5E5E5`) no lugar de fotos, ícones, blocos coloridos;
  - tipografia provisória em uma única família neutra (Aptos, Segoe UI, system-ui);
  - **sem cor de marca**, sem gradientes, sem texturas;
  - copy real do brief (não Lorem Ipsum) para sentir densidade textual de verdade.
- Render headless via `scripts/render-html-screenshots.js` para `screenshots/v1-slide-N.png`.

Auto-check obrigatório olhando os screenshots:

| Checagem | Critério |
|----------|----------|
| Hierarquia | título > subtítulo > corpo é instantaneamente identificável |
| Alinhamento | nada flutuando; tudo encaixa numa grade implícita |
| Densidade | nenhum slide tem texto sobrando ou apertado contra borda |
| Ritmo do carrossel | capa, miolo e CTA têm composições visualmente distintas |
| Áreas de respiração | margem útil >= 60px em todas as bordas |

Se algum critério falhar: refaz **uma vez** (v1.1). Se ainda falhar na segunda, anota em `notes.md` e segue mesmo assim — o reviewer pega.

### Passo 2 — Atmosfera visual (mid-fi)

**Objetivo:** transformar layout funcional em design com personalidade.

Aplicar em cima do `template-v1.html`:

- **Paleta de marca** com primary/secondary cumprindo papéis explícitos (fundo? acento? CTA? destaque tipográfico?). Neutros (brancos, pretos, cinzas) **não** são tratados como brand variables.
- **Tipografia distintiva**: parear display + body com personalidade. Evite uma única família genérica. Sugestões em [`skills/gp2-html-designer/references/aesthetic-families.md`](./skills/gp2-html-designer/references/aesthetic-families.md).
- **Texturas e elementos editoriais**: divisores, faixas coloridas, numeração editorial, etiquetas, linhas finas, sangrias deliberadas. Use no máximo um "movimento memorável" por carrossel (eyebrow numerado, faixa diagonal, etc.).
- **Fotos reais ou placeholders válidos**: uma `<img>` por região de imagem. Placeholders só padrão diagonal neutro (ver `skills/_shared/HTML_TECHNICAL_SPEC.md` §"Atributos `data-*` reconhecidos" — `data-image-type`). Sem ilustrações CSS fingindo foto.

Entrega: `template-v2.html` + `screenshots/v2-slide-N.png`.

Auto-check:

| Checagem | Critério |
|----------|----------|
| Contraste | texto sobre fundo tem contraste WCAG AA (>= 4.5 para texto normal) |
| Line-height | corpo de texto >= 1.3; títulos podem ser mais apertados |
| Consistência cromática | mesma paleta em todos os slides; primary aparece em papel consistente |
| Sem AI tells | não é tudo centralizado, não é card-spam, tipografia tem peso |
| Movimento memorável | o carrossel tem um elemento visual que cria identidade |

Refaz **uma vez** se falhar (v2.1).

### Passo 3 — Polimento (high-fi)

**Objetivo:** ajustes finos que separam design "ok" de design "publicável".

Em cima do `template-v2.html`:

- **Tipografia**: pesos certos em pontos críticos (display 700-800, body 400-500), letter-spacing negativo em títulos grandes (-1% a -3%), tamanhos truncados para evitar quebras esquisitas.
- **Micro-alinhamentos**: pixel-perfect entre elementos relacionados (eyebrow alinhado com início do título, etc.).
- **Espaçamento vertical**: aplicar ritmo (4px, 8px, 16px, 24px, 48px) em vez de números aleatórios.
- **Hierarquia tonal**: aplicar opacidades sutis em textos secundários (80%, 65%) quando faz sentido para profundidade.
- **Garantir** que todas as regras de [`skills/_shared/HTML_TECHNICAL_SPEC.md`](./skills/_shared/HTML_TECHNICAL_SPEC.md) ainda são respeitadas (posição absoluta, `<img>` por imagem, sem flex/grid no canvas, sem `::before`/`::after`).

Entrega final: `template.html` (sem sufixo) + `screenshots/slide-N.png` (sem sufixo). Esses são os arquivos consumidos pelo `gp2-html-reviewer`.

`notes.md` opcional registrando decisões marcantes (família estética escolhida, papel de primary/secondary, movimento memorável usado).

## Regras de HTML invioláveis em todos os 3 passos

Estas vêm direto da spec técnica em [`skills/_shared/HTML_TECHNICAL_SPEC.md`](./skills/_shared/HTML_TECHNICAL_SPEC.md):

1. Uma `<section class="slide" data-width="N" data-height="M">` por slide.
2. Posicionamento absoluto para tudo dentro de `.slide`. **Sem flex/grid no canvas.**
3. Uma `<img>` por região de imagem real. Sem ilustração CSS fingindo foto.
4. Sem pseudo-elementos (`::before`, `::after`).
5. Sem CSS animations / `@keyframes`.
6. Sem `mix-blend-mode`, `backdrop-filter`, `mask-image` complexo.
7. Pesos de fonte explícitos (400, 600, 700) — nunca só `bold`.
8. Línguas/copy em português (verbatim do brief).
9. `<meta name="hm-fonts" content="Fonte1,Fonte2">` no `<head>`.
10. `<html data-template-name="..." data-segment="...">` (segmento é um dos suportados pela plataforma).

## O que o designer não faz

- Não aplica `data-template-element`, `data-variable`, `data-image-type`, `data-text-type`, `data-static`. Isso é do `gp2-template-marker`.
- Não gera Fabric JSON.
- Não faz upload.
- Não cria scripts/builds/dependências externas.

## Famílias estéticas como ponto de partida

Quando o brief não dá direção forte, o designer escolhe **uma** família de [`references/aesthetic-families.md`](./skills/gp2-html-designer/references/aesthetic-families.md):

- Editorial clínico
- Premium minimal
- Bold educacional
- Soft wellness
- Magazine authority
- Data-dense profissional
- Luxury refinado
- Brutalist direto

A família escolhida vira a base do Passo 2 (tipografia + paleta + atmosfera).
