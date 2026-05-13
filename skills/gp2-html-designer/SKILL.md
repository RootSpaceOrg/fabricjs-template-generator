---
name: gp2-html-designer
description: "Coração da Pipeline v2: gera HTML/CSS para posts e carrosséis HealthMarket em 3 iterações renderizadas (low-fi → mid-fi → high-fi). Cada passo emite um snapshot, roda render headless via Playwright, faz auto-check sobre os screenshots, e refaz uma vez se falhar. Reproduz o loop visual do Claude Design dentro do openclaw. Não aplica data-template-element/data-variable (isso é do marker), não converte para Fabric, não publica. Use após gp2-request-interpreter, antes de gp2-html-reviewer."
---

# gp2-html-designer

Geração de HTML/CSS para templates HealthMarket usando o **protocolo de 3 renders** descrito em [`../../DESIGN_PRINCIPLES.md`](../../DESIGN_PRINCIPLES.md).

## Princípio

O design ruim da pipeline v1 não vem de regras erradas — vem de o designer escrever HTML sem nunca ver o que produziu até o reviewer fechar o ciclo. Claude Design ganha porque o autor itera no DOM renderizado durante o design.

A v2 explicita esse loop: low-fi → render → mid-fi → render → high-fi → render. O LLM passa a operar sobre evidência visual.

## Inputs

- `brief.md` produzido por `gp2-request-interpreter` (ou pedido direto do usuário, se claro).
- **`reference-spec.md`** (somente em reference-driven mode) — contrato concreto extraído da imagem de referência: paleta hex, tipografia, composição, movimento memorável, elementos editoriais.
- Opcionalmente: imagens de referência anexadas pelo usuário (já analisadas pelo interpreter, mas você pode re-inspecionar para conferir detalhes).

Se nenhum brief existe e o pedido é claro, monte um brief mentalmente e siga.

## Dois modos (reflexo do interpreter)

| Modo do brief | Comportamento do designer |
|---------------|---------------------------|
| **Free mode** | Você **escolhe** família estética, paleta, tipografia, movimento memorável durante o Passo 2. As 3 iterações servem para descobrir a melhor direção. |
| **Reference-driven mode** | `reference-spec.md` é **contrato**. Você materializa o spec — não escolhe direção alternativa. As 3 iterações servem para executar bem o spec, não para reinterpretar. |

Detecte o modo lendo o campo `## Modo` do `brief.md` ou checando se `reference-spec.md` existe na pasta. Se houver dúvida, trate como reference-driven (mais conservador).

**Como respeitar o `reference-spec.md`:**
- Use os hexs exatos da paleta. Não substitua por "tons próximos".
- Use as famílias tipográficas nomeadas (ou a categoria descrita) — display + body. Se a fonte não estiver disponível, escolha a mais próxima da mesma categoria.
- Aplique o **movimento memorável** declarado em todos os slides relevantes.
- Replique os elementos editoriais listados (eyebrow numerado? fios? número de slide gigante?).
- Honre o tratamento de imagem (retangular editorial, circular, full-bleed, etc.).
- Trair o spec é aceitável só se: (a) viola alguma regra técnica do `CLAUDE_DESIGN_RULES.md`, ou (b) a referência tinha um problema visível (overflow, contraste fraco) que o spec já marcou como "não copiar".

## Output esperado

```
artifacts/gp2-html-designer/<slug>/
├── template.html                ← versão final (high-fi)
├── template-v1.html             ← low-fi
├── template-v2.html             ← mid-fi
├── screenshots/
│   ├── v1-slide-1.png
│   ├── v2-slide-1.png
│   └── slide-1.png              ← final
└── notes.md                     ← decisões marcantes (família estética, papel cores, movimento memorável)
```

## Protocolo de 3 passos (OBRIGATÓRIO)

### Passo 1 — Esboço estrutural (low-fi)

Objetivo: travar layout, hierarquia e ritmo do carrossel **antes** de pensar em estética.

Escreva `template-v1.html` com:

- `<!doctype html>` + `<html lang="pt-BR" data-template-name="<nome>" data-segment="<segmento>">`.
- `<meta charset="utf-8">` + `<meta name="hm-fonts" content="...">` (mesmo provisório).
- Uma `<section class="slide" data-width="W" data-height="H">` por slide, com `style="position:relative; width:Wpx; height:Hpx; background:#FFFFFF;"`.
- Posicionamento absoluto para todo elemento visual dentro de `.slide` (`position: absolute; left/top/width/height`).
- **Caixas cinzas placeholder** `#E5E5E5` no lugar de áreas de foto, ícone, bloco colorido.
- Tipografia provisória: uma única família neutra (Aptos, Segoe UI, system-ui).
- **Copy real do brief** em cada slide (nada de Lorem Ipsum — você precisa sentir densidade real).
- **Zero cor de marca, zero gradiente, zero textura.**

Renderize com:

```bash
node ../../scripts/render-html-screenshots.js artifacts/gp2-html-designer/<slug>/
```

(Importante: o script espera `template.html`. No passo 1, copie temporariamente `template-v1.html` → `template.html` antes de renderizar, depois renomeie. Alternativa: rode o script apontando para uma pasta temporária.)

Olhe os screenshots e auto-check:

| Critério | OK se… |
|----------|--------|
| Hierarquia | título > subtítulo > corpo é instantâneo |
| Alinhamento | tudo encaixa numa grade implícita |
| Densidade | ningum slide tem texto cortado ou apertado contra borda |
| Ritmo | capa, miolo, CTA têm composições visualmente distintas |
| Respiração | margem útil ≥ 60px em todas as bordas (canvas 1080) |

Se algo falhar, refaça **uma vez** (template-v1.1.html). Se ainda falhar, anote em `notes.md` e siga.

### Passo 2 — Atmosfera visual (mid-fi)

Objetivo: transformar layout funcional em design com personalidade.

**Free mode:** escolha **uma família estética** de [`references/aesthetic-families.md`](./references/aesthetic-families.md) baseada no segmento + tom do brief. Comprometa-se com ela e anote em `notes.md` (qual escolheu e por quê).

**Reference-driven mode:** **não escolha família** — use a que está em `reference-spec.md`. Carregue o spec inteiro como contrato. Anote em `notes.md` quaisquer divergências menores (ex: "spec pediu Bebas Neue mas usei Anton porque a primeira não está no Google Fonts").

Em cima do `template-v1.html`, gere `template-v2.html` aplicando:

- **Paleta de marca:**
  - Free mode: você escolhe os hexs respeitando os papéis declarados no brief. Neutros (branco, preto, cinza) **nunca** são tratados como brand variables.
  - Reference-driven mode: use os **hexs exatos** do spec. Não substitua por "tons próximos". Os neutros do spec (off-white quente, cinza quente, etc.) também são literais — não troque por neutros frios genéricos.
- **Tipografia:**
  - Free mode: pareie display + body distintivos. Pesos explícitos (400, 600, 700, 800 — nunca só `bold`).
  - Reference-driven mode: use as famílias nomeadas no spec (display + body). Se uma fonte não estiver disponível, escolha a mais próxima da mesma categoria e anote em `notes.md`.
- **Texturas e elementos editoriais:**
  - Free mode: escolha **um único** movimento memorável e aplique consistentemente.
  - Reference-driven mode: replique **todos** os elementos editoriais listados no spec (eyebrow numerado, fios, número de slide, etc.) e use o movimento memorável declarado.
- **Fotos**: uma `<img>` por região de imagem real. Se não tem asset real, use placeholder com padrão diagonal neutro **na mesma família tonal da paleta** (ver "Placeholder de imagem" abaixo). **Nunca** divs ou SVG complexo fingindo foto.
- **Foto profissional**: respeite a decisão do brief + tratamento do spec (retangular editorial, circular avatar, full-bleed). Se reference-driven mode pediu retangular editorial 360×520, mantenha proporção e tratamento.

Renderize e auto-check:

| Critério | OK se… |
|----------|--------|
| Contraste | texto sobre fundo respeita WCAG AA (≥ 4.5:1 para body) |
| Line-height | corpo ≥ 1.3; títulos podem ser 1.0–1.2 |
| Consistência cromática | mesma paleta em todos os slides; primary tem papel consistente |
| Tipografia | display ≠ body; pesos explícitos; sem usar Inter/Arial/Roboto como única família |
| Movimento memorável | o carrossel tem identidade — não parece template Canva |
| **Aderência ao spec** (só reference-driven) | hexs batem com o spec; tipografia bate com o spec; movimento memorável presente; elementos editoriais do spec todos aplicados |
| Sem AI tells | não é tudo centralizado; não é card-spam; não é nested card |

Refaça **uma vez** (template-v2.1.html) se falhar. Se ainda falhar, anote e siga.

### Passo 3 — Polimento (high-fi)

Objetivo: detalhes finos que separam design "ok" de "publicável".

Em cima de `template-v2.html`, escreva `template.html` aplicando:

- **Tipografia fina**: letter-spacing negativo (-1% a -3%) em títulos grandes; pesos certos em pontos críticos (display 700-800, body 400-500); tamanhos ajustados para evitar quebras esquisitas.
- **Micro-alinhamentos**: pixel-perfect entre elementos relacionados (eyebrow alinhado com início do título, etc.).
- **Ritmo vertical**: aplicar escala 4/8/16/24/48/96 em vez de números aleatórios.
- **Profundidade tonal**: opacidades sutis (80%, 65%) em textos secundários quando faz sentido.
- **Verificação final** das regras invioláveis de HTML (ver abaixo).

Renderize uma última vez. Os screenshots em `screenshots/slide-N.png` (sem sufixo) são o que vai para o reviewer.

## Regras de HTML invioláveis (todos os 3 passos)

Vêm direto de [`../../CONTRACT.md`](../../CONTRACT.md) que aponta para `CLAUDE_DESIGN_RULES.md`:

1. Uma `<section class="slide" data-width="N" data-height="M">` por slide.
2. `position: absolute` com `left/top/width/height` em px dentro de `.slide`. **Sem flex/grid no canvas.**
3. Uma `<img>` por região de imagem real. **Sem CSS shapes simulando foto** (nada de `<div class="fake-person"><div class="head"></div></div>`).
4. Sem pseudo-elementos (`::before`, `::after`).
5. Sem `@keyframes`/animations.
6. Sem `mix-blend-mode`, `backdrop-filter`, `mask-image` complexo.
7. Pesos de fonte explícitos (400, 600, 700) — **nunca só `bold`**.
8. Copy em português, verbatim do brief.
9. `<meta name="hm-fonts" content="Fonte1,Fonte2">` no `<head>` listando **todas** as famílias usadas.
10. `<html data-template-name="..." data-segment="...">` com um dos 8 segmentos HealthMarket.
11. Rotação só via `transform: rotate(Ndeg)` (origin default 50% 50%).

## Placeholder de imagem (quando não há asset real)

Use apenas **padrão diagonal simples** via SVG inline base64. Exemplo:

```html
<img class="image-placeholder" alt="Imagem a substituir"
     style="position:absolute; left:60px; top:60px; width:480px; height:640px; object-fit:cover;"
     src="data:image/svg+xml;base64,<base64 do svg abaixo>">
```

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="480" height="640" viewBox="0 0 480 640">
  <rect width="480" height="640" fill="#F7EFE5"/>
  <path d="M-120 600 L520 -120 M0 680 L640 0 M120 760 L760 80"
        stroke="#E7C9AA" stroke-width="18" opacity="0.45"/>
</svg>
```

Inaceitável (nunca faça):

```html
<div class="fake-person">
  <div class="head"></div>
  <div class="body"></div>
</div>
```

## Fotos profissionais (quando o brief pediu)

Tratamento padrão: crop **retangular/editorial**, com pouco ou nenhum `border-radius`. Avatar circular **só** se a referência/pedido pedir explicitamente.

Marque com classe e alt semânticos:

```html
<img class="professional-photo" alt="Foto profissional"
     style="position:absolute; left:610px; top:170px; width:360px; height:520px;
            object-fit:cover; border-radius:0;"
     src="<URL ou placeholder>">
```

## Famílias tipográficas seguras

Use Google Fonts via `<link>` no `<head>`. Quando preferir stack do sistema, sugestões em [`references/aesthetic-families.md`](./references/aesthetic-families.md). **Nunca** use Inter/Arial/Roboto/system-ui como **única** família para o design todo — emparelhe.

## O que esta skill NÃO faz

- Não adiciona `data-template-element`, `data-variable`, `data-image-type`, `data-text-type`, `data-static`. Isso é trabalho do `gp2-template-marker`.
- Não gera Fabric JSON.
- Não faz upload.
- Não inventa scripts/frameworks/dependências externas.
- Não cria múltiplos arquivos HTML por slide — sempre **um** `template.html` com todas as `<section class="slide">`.

## Resposta final ao orquestrador

```markdown
Modo: <free | reference-driven>
HTML gerado em: `<path>/template.html`
Slides: <N>
Formato: <W>x<H>
Família estética: <ex: editorial clínico — escolhida | herdada do spec>
Movimento memorável: <ex: eyebrow numerado>
Cores de marca aplicadas: <primária somente | primária+secundária>
Foto profissional: <usada | não usada | reservada>
Aderência ao spec: <N/A em free mode | total | parcial — ver notes.md>
Screenshots: <path>/screenshots/slide-N.png
Notes: <path>/notes.md
Próximo passo: gp2-html-reviewer
```

## Quando refazer dentro do mesmo passo

- Passo 1 falhou no auto-check → refaz uma vez.
- Passo 2 falhou no auto-check → refaz uma vez.
- Passo 3 não tem refazer interno; se você notar problema visual grave, recomece do Passo 2.

Em todos os casos, registre o motivo em `notes.md` para o reviewer saber o que foi tentado.
