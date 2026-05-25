# Catálogo de Carousel Moves (M*)

Moves canônicos para carrossel Instagram — elementos de identidade visual que dão coerência e atitude editorial ao conjunto, sem competir com o conteúdo.

Vocabulário compartilhado entre `gp2-art-director` (escolhe 1–2 por carrossel), `gp2-html-designer` (executa no Passo 3 high-fi) e `gp2-html-reviewer` (confere presença).

**Regras de uso (art-director):**
- Escolha **1–2 moves por carrossel** (mais que isso polui).
- Move declarado deve ter evidência visual em **pelo menos 1 slide** (idealmente em ≥50% dos slides quando faz sentido).
- Combine moves com tom do brief: minimal → M8/M9; editorial → M2/M5; ousado → M10/M7.

**Regras de uso (reviewer):**
- Move declarado mas ausente do HTML → finding `move-missing` (blocker).
- Move presente no HTML mas não declarado → aceito (designer pode adicionar delight).

---

## M1 — hook-visual

**Descrição:** slide 1 abre com **face crop fechado** (rosto humano ocupando ≥40% do slide) + título massivo curto. O olho prende no rosto, lê o título, segue para o slide 2. Replica o gancho visual de Reels/TikTok.

**Quando funciona:** carrosséis com profissional reconhecível, conteúdo pessoal, depoimento.
**Quando não funciona:** marcas sem porta-voz, conteúdo abstrato/conceitual.

**`data-*` envolvidos:** `<img data-image-type="professionalPhoto">` ocupando coluna lateral ou superior; `<h1>` adjacente massivo.

**Exemplo (slide 1 com A1-hero-split + M1):**
```html
<img data-image-type="professionalPhoto"
     style="position:absolute; left:540px; top:80px; width:540px; height:1200px;
            object-fit:contain; object-position:bottom center;"
     src="data:image/png;base64,...">
<h1 style="position:absolute; left:60px; top:280px; width:460px;
           font:800 110px/0.95 'Playfair Display';">
  Sua rotina<br>está sabotando<br>você?
</h1>
```

**Combina com arquétipos:** A1, A12.

---

## M2 — numero-ostentatorio

**Descrição:** número de slide aparece como **ornamento gigante** (300–500px) numa posição calculada — geralmente canto superior direito ou esquerdo, em cor brand ou neutro contrastante. Vira identidade do carrossel.

**Quando funciona:** listicle, tutorial, sequência didática.
**Quando não funciona:** carrossel single-post; quando o número compete com o título.

**`data-*` envolvidos:** `<div data-static="true">` posicionado no canto, fonte display peso 800–900, opcionalmente `data-variable="secondary"` ou cor neutra de baixa saturação.

**Exemplo:**
```html
<div data-static="true"
     style="position:absolute; right:40px; top:40px;
            font:900 380px/0.85 'Playfair Display';
            color:#F0EBE2; letter-spacing:-12px;">
  03
</div>
```

**Combina com arquétipos:** A3, A5, A7, A8.

---

## M3 — bleed-entre-slides

**Descrição:** elemento visual **continua entre dois slides consecutivos** — uma forma, uma linha, ou um bloco de cor sai pela borda direita do slide N e "aparece" começando pela esquerda do slide N+1. Cria sensação de continuidade.

**Quando funciona:** carrosséis de storytelling, antes/depois, processos sequenciais.
**Quando não funciona:** slides independentes (educativo solto); quando a leitura é não-linear.

**`data-*` envolvidos:** `<div data-static="true">` com `position:absolute` ultrapassando `width` do slide; ou shapes/fios em zonas coincidentes.

**Exemplo (slide N e N+1):**
```html
<!-- Slide N (final direito) -->
<div data-static="true" data-variable="primary"
     style="position:absolute; right:-80px; top:600px; width:240px; height:60px;
            background:#E0005A;"></div>

<!-- Slide N+1 (início esquerdo, mesma altura/cor) -->
<div data-static="true" data-variable="primary"
     style="position:absolute; left:-80px; top:600px; width:240px; height:60px;
            background:#E0005A;"></div>
```

**Combina com arquétipos:** A1↔A3, A8↔A9, A7↔A4.

---

## M4 — cta-arrow-ritualistico

**Descrição:** seta de swipe (`→` ou chevron SVG) na **mesma posição em todos os slides exceto o último**, em cor consistente. Sinal de navegação que vira identidade.

**Quando funciona:** sempre; é o move mais seguro de aplicar.
**Quando não funciona:** carrossel single-post; quando o art-director já escolheu M6-reveal-progressivo no mesmo template (combinar barra de progresso + seta no rodapé pode poluir).

**`data-*` envolvidos:** `<div data-static="true">` no canto inferior direito; mesma coord em todos os slides exceto o último.

**Exemplo:**
```html
<div data-static="true"
     style="position:absolute; right:60px; bottom:60px;
            font:600 32px 'Inter'; color:#1C1A18;">
  Arraste →
</div>
```

**Combina com arquétipos:** todos exceto A6 (último slide).

---

## M5 — quote-pull

**Descrição:** um slide do meio do carrossel é dedicado a uma **citação tipográfica massiva** — texto único, centralizado, 80–120px, sem competição visual. Vira respiro e ponto de prova.

**Quando funciona:** carrosséis longos (≥6 slides) que precisam de quebra de ritmo.
**Quando não funciona:** carrosséis curtos (≤4); quando não há frase forte para destacar.

**`data-*` envolvidos:** slide inteiro em `A4-quote-centered-fios` ou `A10-headline-massive-solo`; texto sem `data-template-element` quando a citação é parte do design fixo.

**Exemplo (slide isolado):**
```html
<section class="slide" data-width="1080" data-height="1350"
         style="position:relative; background:#F5F3EF;">
  <p style="position:absolute; left:120px; top:480px; width:840px;
            font:400 96px/1.05 'Playfair Display'; font-style:italic;
            text-align:center; color:#1C1A18;">
    "A consistência<br>vence o talento<br>todos os dias."
  </p>
</section>
```

**Combina com arquétipos:** A4, A10.

---

## M6 — reveal-progressivo

**Descrição:** o carrossel **revela informação gradualmente** — slide 1 mostra apenas o gancho, slide 2 adiciona contexto, slide 3 mostra solução, etc. O design suporta isso com **elementos que crescem ou se completam** ao longo dos slides (ex: número que vai de 1 a 5, barra que enche, ilustração que se monta).

**Quando funciona:** tutoriais, sequências de revelação, contagem regressiva.
**Quando não funciona:** conteúdo paralelo (use M2); quando os slides são independentes.

**`data-*` envolvidos:** elementos com `data-static="true"` que mudam de tamanho/preenchimento por slide; opcionalmente progress bar customizado.

**Exemplo (barra que enche slide a slide):**
```html
<!-- Slide 2 de 5 -->
<div data-static="true"
     style="position:absolute; left:60px; bottom:80px; width:960px; height:4px;
            background:#E8E2D8;">
  <div data-variable="primary"
       style="width:40%; height:4px; background:#E0005A;"></div>
</div>
```

**Combina com arquétipos:** A3 + A5 + A7 em sequência.

---

## M7 — color-block-shift

**Descrição:** bloco sólido de cor primary aparece em **posição/tamanho variável** a cada slide — slide 1 com bloco no topo, slide 2 lateral, slide 3 rodapé. Cria dinâmica visual sem precisar de fotos.

**Quando funciona:** carrosséis sem fotos, brand-forward, conteúdo conceitual.
**Quando não funciona:** quando há foto dominante em todos os slides; quando o tom é minimal/quieto.

**`data-*` envolvidos:** `<div data-variable="primary" data-variable-target="background" data-static="true">` em coords diferentes por slide.

**Exemplo:**
```html
<!-- Slide 1: bloco superior direito -->
<div data-static="true" data-variable="primary" data-variable-target="background"
     style="position:absolute; right:0; top:0; width:380px; height:380px; background:#E0005A;"></div>

<!-- Slide 2: bloco inferior esquerdo -->
<div data-static="true" data-variable="primary" data-variable-target="background"
     style="position:absolute; left:0; bottom:0; width:540px; height:280px; background:#E0005A;"></div>
```

**Combina com arquétipos:** A3, A4, A10.

---

## M8 — fio-tipografico

**Descrição:** **fio horizontal fino** (1–3px) abaixo de cada eyebrow ou título, na largura do texto ou pouco maior. Identidade editorial discreta, presente em todos os slides.

**Quando funciona:** sempre; é o move minimal mais seguro.
**Quando não funciona:** quando o design já é muito ornamental (concorre com outros decoradores).

**`data-*` envolvidos:** `<div data-static="true">` ou `<hr>` com `data-variable="primary"` opcional.

**Exemplo:**
```html
<div data-static="true" data-variable="primary"
     style="position:absolute; left:60px; top:280px; width:160px; height:2px;
            background:#E0005A;"></div>
```

**Combina com arquétipos:** A3, A5, A7, A9.

---

## M9 — edge-numbering

**Descrição:** numeração discreta `01/07`, `02/07`, etc. em **posição fixa** (canto inferior direito ou esquerdo), 14–18px, cor neutra de baixa intensidade. Ajuda orientação sem dominar.

**Quando funciona:** carrosséis ≥5 slides; alternativa minimal e elegante a barra de progresso (use M6 se a progressão for o ponto; M9 quando só orientação discreta basta).
**Quando não funciona:** carrossel ≤3 slides; quando já tem M2 (numero ostentatorio) — duplicaria.

**`data-*` envolvidos:** `<div data-static="true">` no rodapé.

**Exemplo:**
```html
<div data-static="true"
     style="position:absolute; right:60px; bottom:50px;
            font:500 16px 'Inter'; letter-spacing:0.08em;
            color:#8B8478;">
  03 / 07
</div>
```

**Combina com arquétipos:** todos exceto A6.

---

## M10 — headline-overflow

**Descrição:** título intencionalmente **extrapola a borda** do slide (vaza pela esquerda, direita ou inferior). Gesto editorial provocativo — sugere que o conteúdo é maior do que o slide consegue conter.

**Quando funciona:** brand-forward, conteúdo provocativo, hooks fortes.
**Quando não funciona:** marcas conservadoras; conteúdo institucional/clínico onde o gesto parece descontrolado.

**`data-*` envolvidos:** `<h1>` com `left` negativo OU `width` maior que o canvas + `overflow:hidden` no `<section>`.

**Exemplo:**
```html
<h1 style="position:absolute; left:-40px; top:380px; width:1200px;
           font:900 200px/0.85 'Inter'; letter-spacing:-8px;
           color:#1C1A18;">
  ROTINA<br>SABOTADA
</h1>
```

**Combina com arquétipos:** A10, A2.

---

## Como o reviewer confere os moves

Para cada move M* declarado em `visual-plan.md → ## Carousel moves`:

1. Identifique o critério visual do move (face crop ≥40%, número ≥300px, fio ≤3px, etc.).
2. Procure no HTML dos slides indicados (e dos screenshots renderizados).
3. Se ausente em **todos** os slides onde deveria aparecer → finding `move-missing` severity blocker.
4. Se presente parcialmente → `moveExecution: "partial"` com lista do que faltou.
5. Se presente conforme declarado → `moveExecution: "complete"`.

Move **não-declarado mas presente** no HTML = bônus (delight detail). Não é finding.
