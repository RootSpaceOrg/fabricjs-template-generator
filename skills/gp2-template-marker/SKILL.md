---
name: gp2-template-marker
description: "Anota o HTML aprovado com data-template-element, data-te-*, data-image-type, data-text-type, data-variable, data-static. Absorve o antigo context-analyzer: a análise narrativa acontece on-the-fly enquanto o marker decide cada elemento, em vez de gerar um context-analysis.json separado. Roda audit-template-markup.py como gate. Use após gp2-html-reviewer (PASS), antes de gp2-template-converter."
---

# gp2-template-marker

Adiciona os atributos `data-*` ao `template.html` aprovado para que o `gp2-template-converter` possa emitir Fabric JSON com elementos editáveis, variáveis de perfil e estáticos corretamente classificados.

## Mudança vs v1: context-analyzer absorvido

A v1 tinha duas skills sequenciais:
- `getposts-context-analyzer` → escrevia `context-analysis.json` rotulando cada elemento.
- `getposts-template-marker` → lia o JSON e copiava as descrições para `data-te-description`.

Na auditoria detectamos que o context-analyzer só rotulava post-hoc: o marker imediatamente consumia tudo. Manter as duas era cerimônia. A v2 **funde**: o marker decide o papel narrativo de cada elemento na hora em que aplica `data-te-description`.

Saída substituta: em vez de `context-analysis.json`, o marker emite `template-summary.md` curto (3-5 linhas) descrevendo o arco do post + papel de cada slide. Isso é o que o uploader v1 vai consumir como `--description-hint` (no v1 era extraído do context-analysis).

## Boundary

Faz:

- adiciona `data-template-element`, `data-te-*`, `data-image-type`, `data-text-type`, `data-variable`, `data-static`, `data-segment`;
- preserva integralmente o design visual aprovado (não muda layout, copy, cor, fonte);
- classifica cada elemento por papel semântico **e** narrativo;
- valida com `audit-template-markup.py` antes de declarar pronto;
- emite `template-summary.md` para o uploader.

Não faz:

- redesenhar o template;
- reescrever copy (exceto labels claramente inseguros);
- converter para Fabric JSON;
- subir para S3/Supabase;
- marcar elementos decorativos como editáveis só porque são visíveis.

## Inputs

```
artifacts/gp2-request-interpreter/<slug>/brief.md        ← arco narrativo por slide
artifacts/gp2-art-director/<slug>/visual-plan.md         ← copy orientativo e elemento-chave por slide
artifacts/gp2-html-designer/<slug>/
├── template.html          ← aprovado pelo gp2-html-reviewer (PASS)
├── screenshots/
└── notes.md
```

E `html-review.json` com status `PASS`.

## Output

```
artifacts/gp2-template-marker/<slug>/
├── template.html          ← cópia marcada (NUNCA edite a original do designer)
├── marker-audit.json      ← saída do audit-template-markup.py
├── marker-audit.md        ← versão humana do audit
└── template-summary.md    ← arco narrativo (3-5 linhas) para o uploader
```

## Workflow

1. Confirme `html-review.json.status === "PASS"`. Se não, recuse e devolva ao reviewer.
2. Copie `template.html` para `artifacts/gp2-template-marker/<slug>/template.html`. A original do designer fica intocada.
3. Garanta o cabeçalho do template está correto:
   - `<html lang="pt-BR" data-template-name="..." data-segment="...">` (slug do vertical inferido do brief — kebab-case).
   - `<meta charset="utf-8">`.
   - `<meta name="hm-fonts" content="Fonte1,Fonte2">` listando todas as famílias usadas no CSS.
   - Opcional: `<meta name="hm-detected-primary" content="#...">` e `secondary` se você quiser fixar e pular auto-detecção.
3b. **Leia o contexto antes de marcar qualquer elemento** — este passo é obrigatório:
   - Leia `brief.md` inteiro: extraia o arco narrativo por slide (papel de cada lâmina: capa, educativo, prova, CTA…) e o segmento/tom do template.
   - Leia `visual-plan.md` inteiro: extraia o copy orientativo e o elemento-chave por slide.
   - Os textos reais no HTML são o melhor sinal do formato esperado — leia-os antes de escrever qualquer `data-te-description`.
   - Monte internamente um mapa: `slide N → papel narrativo (brief) → elemento-chave (visual-plan) → textos reais (HTML)`. Use esse mapa no passo 4 para derivar descriptions que reflitam o contexto do template.

4. **Caminhe slide por slide** (cada `<section class="slide">`) e para cada elemento decida na hora:
   - **Papel narrativo do slide** (capa/abertura, miolo educativo, prova/dado, CTA, fechamento). Use o mapa do passo 3b para confirmar o papel.
   - **Papel do elemento** dentro do slide (gancho, título, subtítulo, corpo, prova, CTA-label, foto contextual, foto profissional, logo, brand-handle, decoração). Use isso para escolher entre `data-template-element`, `data-text-type`, `data-static`, `data-image-type`.
   - **Para cada elemento `data-template-element="true"`**, siga obrigatoriamente:
     1. Consulte `references/element-descriptions.md` → escolha o role canônico mais próximo.
     2. Derive `ex1` do texto real do elemento no HTML (generalizado — sem referência ao vertical específico). Ex: "Seu conhecimento clínico está virando pacientes?" → `'Seu conhecimento está virando resultados?'`
     3. Adicione hint de sequência quando o elemento funciona em par narrativo com vizinhos: `após eyebrow categórico; seguido de corpo educativo`.
     4. Adicione 2 exemplos genéricos adicionais cobrindo variação de formato.
     5. A description resultante **deve seguir a fórmula** — nunca escreva prosa descritiva.
5. Aplique a classificação (ver tabela abaixo).
6. Mapeie cores de marca: cada elemento cuja cor (fill/stroke/background) deve trocar com o preset da marca recebe `data-variable="primary|secondary"` + opcional `data-variable-target`.
6b. **Valide atributos `data-darken` (safety net obrigatória):**
   - Caminhe todos os elementos com `linear-gradient(` ou `radial-gradient(` no `style`.
     - Tem `data-darken` válido + `data-darken-opacity` (0.1–1.0) → OK.
     - Tem `data-gradient` JSON (fallback de overlay custom) → OK.
     - Caso contrário → o marker **adiciona** `data-darken` + `data-darken-opacity`, inferindo a direção do CSS. Lookup CSS → preset em [`../_shared/GRADIENT_SYSTEM.md`](../_shared/GRADIENT_SYSTEM.md) §"Mapeamento CSS → preset". Log em `marker-audit.md`.
   - **`<section>` com gradiente CSS usando cores brand hex** (não transparent/rgba) → **FAIL**. Devolva ao designer. Background brand = cor sólida `primary` + div overlay com `data-darken`. Não prosseguir.
   - **`data-variable-stops` presente** → remova e substitua por `data-variable="primary" data-variable-target="background"` na section + `data-darken` no overlay (legado).
7. Rode o audit:

```bash
python3 ../../scripts/audit-template-markup.py artifacts/gp2-template-marker/<slug>/
```

8. Se audit retornar erros, corrija e rode de novo. **Não re-renderize screenshots** — a marcação de `data-*` não muda o render. Se você está em dúvida, abra o HTML no navegador uma vez, mas o reviewer não precisa rodar de novo.
9. Escreva `template-summary.md` com 3-5 linhas: arco do post + papel de cada slide.

## Tabela de classificação

| Elemento | Atributos a aplicar |
|----------|---------------------|
| Texto que muda por post (título, gancho, subtítulo, corpo, bullet, dado) | `data-template-element="true"` + `data-te-description="..."` + `data-te-max-chars="N"` |
| Texto de perfil de marca (`@handle`, `Sua Clínica`, `(11) ...`, endereço) | `data-text-type="instagramHandle\|instagramName\|phone\|address"` + `data-static="true"` |
| Logo da marca | `<img data-image-type="brandLogo" data-static="true">` |
| Foto profissional do usuário | `<img data-image-type="professionalPhoto" data-static="true">` (foto fica no perfil; trocada via profile, não AI) |
| Foto profissional cutout PNG (default da v2) | mesma classificação acima — `data-static="true"` + `data-image-type="professionalPhoto"`. **Não** marque como template-element mesmo quando o `src` é um data URL base64 longo. |
| Foto/imagem que varia por post (gerada por IA, escolhida pelo usuário) | `<img data-image-type="userAsset" data-template-element="true" data-te-description="..." data-te-remove-bg="false">` |
| CTA-label fixo ("Arraste →", "Saiba mais", "@") | `data-static="true"` |
| Numeração / progresso / etiquetas decorativas estáticas | `data-static="true"` |
| Formas decorativas (linhas, faixas, fundos, divisores) | nada (auto-detect como decoração) ou `data-static="true"` se ambíguo |
| Overlay de legibilidade sobre foto (`<div>` com `linear-gradient` transparente→preto) | `data-static="true"` (nunca template-element; o converter emite como `roundedRect` com fill gradient) |
| Fundo de slide Brand com escurecimento (section com `data-variable` + div overlay com `data-darken`) | section: `data-variable="primary" data-variable-target="background"` + overlay div: `data-darken="<preset>" data-darken-opacity="<N>"` + `data-static="true"` |
| Acento de cor que troca com preset (botão, headline colorido, faixa) | `data-variable="primary\|secondary"` + opcional `data-variable-target="fill\|stroke\|background"` |
| Slide background sólido brand | no `<section>`: `data-variable="primary"` + `data-variable-target="background"` |
| Span dentro de título com cor diferente | `<span data-variable="..." style="color:...">` (não é elemento separado!) |

> **Nota sobre `professionalPhoto` cutout PNG:** quando a `<img data-image-type="professionalPhoto">` usa `object-fit: contain` e `object-position: bottom center` (PNG cutout transparente — ver [`gp2-html-designer/references/professional-photo-placements.md`](../gp2-html-designer/references/professional-photo-placements.md)), a classificação no marker **não muda** — continua `data-static="true"`. Mas o converter precisa emitir o `ClippableImage` em modo cutout: `originWidth/Height` = dimensões naturais do PNG (não do slot), `width === originWidth`, `cropX/Y = 0`, `originY: "bottom"`. Ver `gp2-template-converter/SKILL.md` §"ClippableImage cutout (CRÍTICO)". O reviewer (`scripts/review-fabric-json.py`) tem check deterministica que flagra cutout mal-emitido (`width !== originWidth` com `cropX/Y = 0`).
>
> **Antes de marcar, confirme**: o slot da `<img>` cutout no HTML tem aspect ratio `width/height` entre `0.55` e `1.10` (PNG cutout é ~3:4 = 0.78). Se estiver fora, devolva ao designer com `REVISE` indicando o ratio observado. Slots muito altos (ex: `540×1200` = 0.45) ou muito largos (ex: `540×400` = 1.35) deixam metade do slot vazia e induzem o converter a erro — sintoma observado em produção: figura cobrindo só metade do slot no editor com a face cortada.
>
> **Antes de marcar, verifique ancoragem**: a `<img data-image-type="professionalPhoto">` deve satisfazer **uma das duas condições** (fotos de usuário são busto/tronco — sem ancoragem a figura parece flutuar): (1) `top + height ≥ canvas_height − 80px` (borda inferior do slide), OU (2) outro elemento visível sobrepõe o terço inferior do slot. Se nenhuma condição for satisfeita, devolva ao designer com `REVISE` antes de marcar.

## Regras críticas

- **`data-te-description` NUNCA é prosa descritiva.** Sempre a fórmula de 4 componentes. Se você está escrevendo uma frase como "texto neutro e adaptável para qualquer nicho, com linguagem concreta e sem jargão" ou "título intermediário adaptável para qualquer área de atuação" — pare. Isso é o anti-pattern que quebra o LLM downstream. Use o catálogo + fórmula + exemplos derivados do texto real.

  ```
  ❌ PROIBIDO:
  "Slide 4 título: texto neutro e adaptável para qualquer nicho, com linguagem concreta e sem jargão."
  "Título intermediário adaptável para qualquer área de atuação."
  "Corpo de texto explicativo sobre o tema do slide."

  ✅ CORRETO:
  "Título da lâmina intermediária; formato afirmação direta OU inversão de expectativa;
  1 frase em 2 linhas; após eyebrow categórico; seguido de corpo educativo; 30-60 chars;
  ex: 'Paciente não compra expertise', 'O corpo fala antes de doer', 'Resultado não é só número'"
  ```

- **Inline `<span>` dentro de texto editável é estilo, não elemento separado.** Marque o `<h1>`/`<p>` pai como `data-template-element`, e o `<span>` interno só tem `style` (e opcional `data-variable` se a cor é brand). O converter vai virar `textbox.styles[lineIndex][charIndex]`.
- **Neutros não viram brand variables.** Branco, off-white, cinza, preto de body — ficam literais.
- **Acentos brand sem `data-variable` são bug.** Se há um botão laranja no design e a marca é azul, o usuário vai abrir o template no editor e o botão continua laranja. Isso quebra a promessa do produto.
- **Conservador no editável.** Quando em dúvida entre static e template-element, escolha static.
- **`data-te-description` é genérico no role, mas contextualizado nos exemplos.** Não escreva "Título sobre laserterapia premium" — escreva seguindo a fórmula `<role>; formato '<máscara>'; <bound>; ex: '<a>', '<b>', '<c>'`. Catálogo canônico em [`references/element-descriptions.md`](./references/element-descriptions.md). Template vai ser usado por dezenas de nichos; descriptions são reutilizáveis. **Porém:** use o **texto atual do elemento** como primeiro exemplo (generalizado), e descreva a **relação com elementos vizinhos** (anterior/posterior) para que o LLM entenda a sequência narrativa (ver regras de contextualização abaixo).
- **`data-te-max-chars` calculado pelo box, não pelo texto atual.** Estimativa: `floor((width × lines) / (fontSize × 0.6))`. Arredonde para cima na próxima dezena.
- **Repetidos entre slides usam mesma classificação.** Logo aparece em 5 slides? Todos com mesmo `data-image-type="brandLogo"`. Se o conteúdo deve ser o mesmo (logo, handle, foto profissional), use `data-te-link-id="logo"` (mesmo slug) em todos.
- **Preserve `text-transform`.** Se CSS tem `text-transform: uppercase`, adicione `data-te-text-case="uppercase"` para que o converter mantenha a intenção quando o AI preencher.

## `data-te-description` — fórmula dos 4 componentes

A description **vai literal no prompt do LLM gerador de copy** (`healthmarket-lambda-ai-idea-to-template/copy_processor.py:_format_elements_context`). Description vaga gera output inconsistente entre slides; description estruturada com formato e exemplos guia o LLM para output consistente.

**Toda description segue a fórmula:**

```
<role narrativo>; formato '<máscara>'; <bound 1>; <bound 2>; ex: '<ex1>', '<ex2>', '<ex3>'
```

**Catálogo canônico de descriptions por role:** [`references/element-descriptions.md`](./references/element-descriptions.md). Cobre eyebrow numerado, eyebrow simples, hook, subtítulo, corpo educativo, bullet, dado numérico, caption, citação, CTA, linha de contato, foto contextual, foto profissional, logo. **Sempre consulte primeiro o catálogo** antes de compor uma description nova.

**Exemplo (eyebrow numerado em todo slide do carrossel):**

✅ Boa — formato + 3 exemplos genéricos:
```
Eyebrow editorial da lâmina; formato 'NN / TEMA' onde NN é o número
sequencial do slide e TEMA é categoria curta em CAPS; até 30 chars;
ex: '01 / DOR CRÔNICA', '03 / O ESTUDO', '07 / PRÓXIMO PASSO'
```

❌ Ruim — sem formato, sem exemplos:
```
Eyebrow editorial da lâmina; rótulo curto de seção
```

❌ Ruim — específica do nicho do template atual:
```
Eyebrow sobre laserterapia premium; rótulo da clínica do Dr. João
```

**Regras invioláveis:**

1. **Slots equivalentes em slides diferentes recebem a mesma string.** Eyebrow do slide 1, slide 3 e slide 5 → mesma description. O LLM diferencia pelo contexto da página (mensagem-chave da narrative arc, que ele já vê separadamente).
2. **Exemplos NUNCA citam o vertical atual do template.** O template vai ser usado em dezenas de verticais diferentes; descriptions são reutilizáveis. Use exemplos de formato (`'01 / DOR'`, `'03 / O ESTUDO'`), não de conteúdo específico de vertical (`'01 / FISIOTERAPIA'`).
3. **Formato e conteúdo são coisas diferentes.** `formato 'NN / TEMA'` é estrutura; `ex:` mostra como aplicar.
4. **3 exemplos é o sweet spot.** 1 vira regra rígida, 5+ vira ruído. 3 cobrem variação curto/médio/longo.
5. **Sweet spot de tamanho: 200-300 chars por description.** Cada description vai pra cada elemento de cada template no prompt do LLM — pesar tokens importa.
6. **Quando em dúvida, escolha o role canônico mais próximo do catálogo** em vez de inventar.

**Regras de contextualização (NEW — evita descriptions desconexas):**

7. **Use o texto atual do elemento para derivar o primeiro exemplo.** O texto no HTML é o melhor sinal do formato esperado. Generalize-o (remova referências ao vertical) e use como `ex1`. Depois adicione 2 exemplos genéricos. Ex: se o texto é "Seu conhecimento clínico está virando pacientes?", o ex1 fica `'Seu conhecimento está virando resultados?'` (generalizado) e não um exemplo desconexo como `'O erro está no recorte'`.

8. **Descreva a relação com vizinhos.** Quando o elemento funciona como par narrativo com o anterior ou posterior (eyebrow→título, título→subtítulo, dado→caption), adicione um hint de sequência na description: `após eyebrow categórico; seguido de subtítulo de apoio`. Isso ajuda o LLM a manter coerência entre elementos adjacentes.

**Exemplo de description contextualizada:**

Texto no HTML: `"Seu conhecimento clínico está virando pacientes?"`
Eyebrow acima: `"conteúdo clínico"` | Subtítulo abaixo: body educativo

✅ Boa — usa o texto real generalizado + relação com vizinhos:
```
Gancho principal da lâmina; formato pergunta provocativa OU afirmação
que gera curiosidade; 1 frase em 2-3 linhas; após eyebrow categórico;
seguido de corpo educativo; 50-90 chars; ex: 'Seu conhecimento está
virando resultados?', 'Você sabe o que seu paciente realmente busca?',
'O que faz um conteúdo converter de verdade?'
```

❌ Ruim — exemplos desconexos do contexto real:
```
Gancho principal da lâmina; formato pergunta provocativa; 1 frase;
ex: 'Sua ideia ficou clara?', 'O erro está no recorte',
'Mostre o próximo passo'
```

## `template-summary.md` (substitui context-analysis.json para o uploader)

Formato exato:

```markdown
# Resumo do template — <título>

## Arco
<2-3 linhas: o que o post quer fazer o leitor entender/sentir/agir, ponta-a-ponta>

## Por slide
- Slide 1: <papel narrativo curto>
- Slide 2: <...>
- Slide N: <CTA / fechamento>
```

Mantenha curto. O uploader vai usar isso para gerar a descrição que aparece no Supabase. Não detalhe campos editáveis — isso é metadado, não conteúdo da descrição.

Use os papéis narrativos reais do `brief.md` (passo 3b) para descrever cada slide — não invente papéis genéricos. O template tem um motivo para existir; a descrição deve refletir esse motivo.

## Audit

```bash
python3 ../../scripts/audit-template-markup.py artifacts/gp2-template-marker/<slug>/
```

O script gera `marker-audit.json` + `marker-audit.md`. Loop máximo: **2 fixes**. Se ainda falhar, escale para o orquestrador.

## Resposta final ao orquestrador

```markdown
HTML marcado: `<path>/template.html`
Audit: PASS|FAIL
Campos editáveis: <N>
Imagens: brandLogo=<n>, professionalPhoto=<n>, userAsset=<n>
Perfil de marca: handle=<n>, name=<n>, phone=<n>, address=<n>
Cores brand: primary=<n elementos>, secondary=<n>
Resumo narrativo: `<path>/template-summary.md`
Próximo passo: gp2-template-converter
```
