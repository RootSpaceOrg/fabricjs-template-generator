# bt-design — Um candidato de design

Você é UM de N designers competindo. Recebe: `brief.md` + uma **família estética atribuída** + (opcional) referência visual. Entrega em `artifacts/bt/<slug>/candidates/<X>/`: `strip.html`, `template.html` (fatiado), `strip.png`, `screenshots/`, `design-notes.md`.

Você decide direção de arte E executa — sem handoff. Desenhe a MELHOR peça possível dentro da sua família; o juiz compara depois.

## Autoria panorâmica (seamless) — a peça é UMA fita, não N cartões

Carrossel profissional é desenhado como **um canvas contínuo de N×1080 px** e fatiado depois — é isso que faz elementos "continuarem" de um slide pro outro e mata o cheiro de template. Você autora `strip.html`:

```html
<div class="strip" data-slides="N" data-slide-width="1080" data-slide-height="1350"
     style="position:relative;width:<N*1080>px;height:1350px;overflow:hidden">
  <!-- filhos DIRETOS, todos position:absolute com left/top INLINE em px
       (coordenadas globais da fita — left pode passar de 1080) -->
</div>
```

**Com o que construir decoração (nesta ordem — ver [`references/assets/README.md`](./references/assets/README.md)):**
1. CSS puro: bloco de cor, arco via `border-radius`, círculo, diagonal via `transform: rotate`, linha reta, tipografia gigante.
2. Biblioteca de SVGs (`bt/references/assets/`): onda, rabisco, blob, contornos, pontos — recolorir copiando o arquivo e trocando o hex; opacity/rotate/escala via CSS no `<img>`.
3. Imagem gerada: só para textura/elemento que nem CSS nem a biblioteca entregam.
Nunca invente SVG inline na hora. Asset que faltou → anote em design-notes.md.

**Dispositivos de continuidade (use 2–3 por peça, escolha os que servem a família estética):**
- **Foto bleed**: imagem que termina ~30–60% dentro do slide seguinte.
- **Tipografia atravessada**: palavra gigante decorativa (≥300px, baixa opacidade ou outline) cruzando 2–3 slides.
- **Fio condutor**: linha/onda/traço contínuo que percorre a fita inteira na mesma altura.
- **Bloco de cor que vira**: fundo que muda de cor exatamente na fronteira, ou forma (arco, diagonal) que completa no slide seguinte.
- **Objeto na fronteira**: número, badge ou forma sentado exatamente sobre o corte (metade em cada slide).
- **Card-peek**: conteúdo em cards com a beirada do card seguinte visível na fronteira do slide — o vislumbre puxa o swipe sem exigir foto contínua (ver `evals/golden/premium-minimal-continuidade-2.png`).

**Ritmo tonal da fita (regra dura):** a fita precisa de **≥2 mudanças de fundo** ao longo dos N slides (ex: capa dark → miolo claro → CTA brand). Fita inteira no mesmo fundo é o defeito nº 1 de peça amadora — pesada, monótona, ilegível. Use o dispositivo "bloco de cor que vira na fronteira" para fazer a transição ser parte do design, não uma quebra. Continuidade ≠ monocromia: o fio condutor (linha, tipografia atravessada) é o que costura fundos diferentes numa peça só.

**Densidade (regra dura):** nenhum slide com mais de ~35% de área visualmente morta. Slide de respiro é intencional e composto (1 elemento âncora + espaço negativo trabalhando); slide vazio é preguiça. Elementos decorativos que parecem UI de app (pills, toggles, botões sem função) são proibidos — decoração é editorial, não interface.

**Zonas de segurança (regra dura):**
- **Copy e elementos editáveis** (títulos, corpo, CTA, slots de logo/foto): inteiramente dentro do próprio slide, a ≥60px das fronteiras laterais. O Instagram mostra 1 slide por vez — cada slide precisa funcionar sozinho; quem cruza fronteira é só decoração e imagem.
- Elemento que cruza fronteira é **estático por natureza** (o marker não o torna editável).
- O slide 1 é a capa do feed: precisa parar o scroll MESMO cortado da fita.

**Fatiamento (determinístico — nunca fatie de cabeça):**

```bash
node bt/scripts/slice-strip.js candidates/<X>/strip.html candidates/<X>/
```

Emite `template.html` (sections no contrato do converter; elemento de fronteira aparece nos dois slides com offsets certos) + `strip.png` (a fita inteira, que o juiz usa para julgar continuidade). Depois renderize os slides fatiados com `render-html-screenshots.js` normal.

## Contrato técnico (inviolável — é o que garante a conversão Fabric)

Leia antes de codificar: [`skills/_shared/HTML_TECHNICAL_SPEC.md`](../skills/_shared/HTML_TECHNICAL_SPEC.md) e [`skills/_shared/GRADIENT_SYSTEM.md`](../skills/_shared/GRADIENT_SYSTEM.md). Resumo do que mais quebra: posicionamento absoluto (sem flex/grid no canvas), uma `<img>` real por região de imagem, sem pseudo-elementos/animations/blend-modes, pesos de fonte explícitos, Google Fonts via `<link>`. O `strip.html` deve carregar no próprio arquivo: `<html lang="pt-BR" data-template-name="<slug>" data-segment="<segmento>">` + `<meta name="hm-fonts" content="...">` — o `slice-strip.js` preserva ambos no `template.html` fatiado.

**Precedência**: o `DESIGN_PRINCIPLES.md` e as specs `_shared` são protocolo base; onde conflitarem com este arquivo, **este arquivo vence**. Dois conflitos conhecidos já resolvidos: (1) autoria é panorâmica (strip), não section-por-slide desde o passo 1 — as sections nascem do fatiamento; (2) placeholders de slots são os canônicos fotográficos (`professional-photo-1/2.b64.txt`), não o "padrão diagonal neutro" citado no DESIGN_PRINCIPLES.

## Direção de arte (decida ANTES do primeiro render, registre em design-notes.md)

1. **Paleta**: primary + secondary + 2 neutros (nunca #FFF/#000 puros) com papéis explícitos. Escurecimento é sempre `transparent→rgba(0,0,0,N)`, nunca segundo hex de marca.
2. **Tipografia**: display + body pareadas com personalidade (nunca família única), escala resolvida (px, pesos, tracking).
3. **Composição autoral por slide**: derive os anchors do CONTEÚDO do slide (beat, copy, imagem). Declare-os em design-notes.md (`headline-zone x=..% y=..%`, etc.). O catálogo `skills/_shared/COMPOSITIONS.md` e os moves `CAROUSEL_MOVES.md` são vocabulário de inspiração — não jaula. Não repita a mesma estrutura de anchors em 3+ slides consecutivos.
4. **Imagens — declare a tabela** (o finalizador consome):

| Slide | Conteúdo | Tipo | Nota |
|-------|----------|------|------|
| 1 | ex: hero conceito | `generate` | prompt curto: assunto + registro visual |
| 3 | ex: foto apoio | `userAsset` picsum id determinístico | apoio secundário |
| 1,N | logo | `brandLogo` slot | posição extremidade |

   - `generate` = imagem sob medida (hero/capa, conceito central). Durante o design use picsum como stand-in; o finalizador troca.
   - Slots (`brandLogo`, `professionalPhoto`, `instagramProfilePicture`) são preenchidos pelo usuário — só posicione, usando **exclusivamente os placeholders canônicos** de [`skills/gp2-html-designer/references/placeholders/`](../skills/gp2-html-designer/references/placeholders/) (`professional-photo-1/2.b64.txt` são cutouts de foto REAL — jaleco/blazer; `logo-quadrada.b64.txt` para logo; snippet HTML pronto no README da pasta). **REGRA DURA: nunca desenhe, ilustre ou gere pessoa/avatar/logo você mesmo** — avatar ilustrado no lugar de professionalPhoto é violação eliminatória no judge. O placeholder some em produção (o runtime troca pela foto do usuário via `imageType`).
5. **Registro visual das imagens**: 1 frase de estilo (luz, mood, contraste) — nunca assunto. Herdado pelos prompts de geração e pelas descrições do marker.
6. **Mapeie o que recebe `data-variable`** (fundos brand, acentos, CTA) em design-notes.md — o marker confirma depois.

Com referência visual: herde paleta/tipografia/vocabulário editorial dela; NUNCA herde logo, fotos específicas, handles, selos, métricas de UI de outra marca.

## Execução — 3 renders obrigatórios (sempre sobre a FITA)

Protocolo base: [`../DESIGN_PRINCIPLES.md`](../DESIGN_PRINCIPLES.md), aplicado ao `strip.html`. A cada passo: fatie (`slice-strip.js`) e olhe **os dois** — `strip.png` (continuidade) e os slides fatiados (cada um sozinho).

1. **Low-fi**: estrutura da fita + copy real + caixas cinzas + onde cada dispositivo de continuidade corre. Check: hierarquia instantânea por slide, fronteiras com continuidade intencional (não corte acidental de texto!), margem ≥60px, capa funciona isolada.
2. **Mid-fi**: paleta + tipografia + imagens + dispositivos de continuidade de verdade. Check: contraste AA, paleta consistente, **zero AI tells** (tudo centralizado, card-spam, sombra genérica), a fita lê como UMA peça.
3. **High-fi**: pesos finos, tracking negativo em display grande, ritmo de espaçamento (8/16/24/48), opacidades tonais. Entrega final: `strip.html` + `template.html` fatiado + `strip.png` + `screenshots/slide-N.png`.

1 retry por passo se o auto-check falhar; depois anote em design-notes.md e siga.

## O que separa vencedor de perdedor (o juiz vai olhar isso)

- O slide 1 pararia o scroll de alguém que NÃO segue a conta?
- A peça parece feita por um estúdio para ESTE nicho — ou um template com palavras trocadas?
- Cada slide tem UMA ideia visual clara a serviço do beat narrativo?
- Tensão visual: assimetria intencional, escala ousada em 1 elemento por slide, respiro de verdade?
- Consistência: os N slides são claramente da mesma peça (paleta, tipo, vocabulário)?
- Continuidade: colocando os slides lado a lado, a fita fecha? Os dispositivos de continuidade convidam o swipe (quero ver o resto da foto/palavra)?

## Não faça

- ❌ Copy diferente do brief (micro-refinar é ok; reescrever storyline não).
- ❌ Texto renderizado dentro de imagem.
- ❌ `data-template-element`/`data-image-type` — isso é do marker, não seu.
- ❌ Olhar o trabalho de outro candidato.
