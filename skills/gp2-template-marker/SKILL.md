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
└── template-summary.md    ← arco + papel de cada slide, sem cabeçalhos (vira description literal no Supabase)
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
   - Leia `visual-plan.md` inteiro: extraia, **por slide**, (a) o copy orientativo e o elemento-chave e (b) o **arquétipo composicional** declarado em `## Plano de slides` (`Arquétipo: A<N> — <slug>`). O arquétipo é a chave para entender a **estrutura interna da lâmina** — quantos itens, se é lista, grade, comparação, passo-a-passo.
   - Para cada arquétipo citado, abra a seção `A<N>` correspondente em [`../_shared/COMPOSITIONS.md`](../_shared/COMPOSITIONS.md) e leia os **slots nomeados** dele (ex: A5 define `item-zone-N`, `item-number`, `item-text`; A11 define grade 2×2 `item 1..4`; A9 define lados A e B). Esses nomes são o papel de cada elemento na composição — você vai usá-los no passo 3c e no passo 4.
   - Os textos reais no HTML são o melhor sinal do formato esperado — leia-os antes de escrever qualquer `data-te-description`.
   - Monte internamente um mapa: `slide N → papel narrativo (brief) → arquétipo + slots (visual-plan + COMPOSITIONS) → elemento-chave → textos reais (HTML)`. Use esse mapa nos passos 3c e 4.

3c. **Pré-análise composicional da lâmina (obrigatório, antes de marcar):** para cada slide, identifique o **padrão da lâmina** e mapeie cada elemento templated ao seu **slot** dentro do padrão. Isto é o que evita o "genérico ruim": sem este passo, 3 itens de um checklist saem com 3 descriptions idênticas e o LLM downstream não sabe que formam uma sequência ordenada.
   - **Nomeie o padrão** do slide (derive do arquétipo do passo 3b, confirme pelos textos reais do HTML):
     - **checklist / lista numerada** (A5, A13) — título/cabeçalho + N itens em sequência;
     - **grade / bento** (A11) — N células equivalentes numa grade;
     - **comparação** (A9) — lado A vs lado B + veredicto;
     - **passo-a-passo** (tutorial) — N passos ordenados;
     - **capa** (A1, A2, A10, A12, A14) — gancho + apoio;
     - **dado / prova** (A7) — número grande + caption;
     - **CTA** (A6) — chamada + contato;
     - **livre** — se nenhum padrão claro, trate cada elemento pelo seu papel narrativo isolado.
   - **Atribua a cada elemento templated seu papel na composição**, incluindo, quando o slot se repete:
     - `índice` e `contagem` — ex: "item 1 de 3", "célula 2 de 4", "passo 3 de 5";
     - **relação pai/filho** — ex: "cabeçalho que governa a lista de 3 itens abaixo", "número que rotula o item 2";
     - **lado / ordem** — ex: "lado A da comparação", "veredicto após A e B".
   - Esse papel na composição é o **4º componente da fórmula** (ver "fórmula dos 5 componentes" abaixo) e é o que diferencia slots repetidos **dentro da mesma lâmina**.

4. **Caminhe slide por slide** (cada `<section class="slide">`) e para cada elemento decida na hora:
   - **Papel narrativo do slide** (capa/abertura, miolo educativo, prova/dado, CTA, fechamento). Use o mapa do passo 3b para confirmar o papel.
   - **Papel do elemento** dentro do slide (gancho, título, subtítulo, corpo, prova, CTA-label, foto contextual, foto profissional, logo, brand-handle, decoração). Use isso para escolher entre `data-template-element`, `data-text-type`, `data-static`, `data-image-type`.
   - **Para cada elemento `data-template-element="true"`**, siga obrigatoriamente:
     1. Consulte `references/element-descriptions.md` → escolha o role canônico mais próximo.
     2. **Texto**: derive `ex1` do texto real do elemento no HTML, generalizando vertical e tema. O texto é pista de **formato e comprimento**, não de tema. Ex: "Seu conhecimento clínico está virando pacientes?" → `'Seu conhecimento está virando resultados?'` (manteve formato pergunta + comprimento; trocou "clínico/pacientes" por termos cross-vertical).
     3. **Imagem**: **ignore o tema do placeholder**. O placeholder (foto que o designer colocou no slot) é só preview visual para validar o layout — não dita o conteúdo real. O role da imagem vem do **papel do slide** (capa? prova? CTA?), não do que está dentro do `<img>`. Anti-pattern explícito: placeholder de café+mesa virando `"formato foto de mesa/objeto; sem pessoa em destaque"` é proibido. A description fixa **função no slide** + **bounds técnicas** (sem texto na imagem, sem watermark, editorial natural), deixando tema e enquadramento abertos.
     4. **Insira o papel na composição** (do passo 3c) como componente da description: `cabeçalho que governa a lista`, `item 1 de 3 de uma lista sequencial`, `célula 2 de 4 de uma grade`, `lado A da comparação`, `passo 3 de 5`. **Este componente é obrigatório sempre que o slot se repete na mesma lâmina** — é ele que diferencia item 1, item 2 e item 3. Sem ele, slots repetidos saem idênticos e quebram a sequência.
     5. Adicione hint de sequência quando o elemento funciona em par narrativo com vizinhos: `após eyebrow categórico; seguido de corpo educativo`.
     6. Adicione 2 exemplos **cross-vertical** adicionais cobrindo variação saudável. Mistura intencional entre nichos — nunca 3 exemplos do mesmo vertical (saúde, pet, beleza).
     7. **Bounds são técnicas/estruturais, não temáticas — e nunca contagem de char.** `"2 linhas"`, `"em CAPS"`, `"editorial natural"` — sim. `"até 60 chars"` — **não** (mora no `data-te-max-chars`; ver regra abaixo). `"sem pessoa"`, `"foco em objeto"`, `"vista de cima"` — não (a menos que o aspect ratio do slot **realmente** force esse enquadramento).
     8. A description resultante **deve seguir a fórmula dos 5 componentes** — nunca escreva prosa descritiva.
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
> **Antes de marcar, verifique ancoragem**: a `<img data-image-type="professionalPhoto">` deve satisfazer **uma das duas condições** (fotos de usuário são busto/tronco — sem ancoragem a figura parece flutuar): (1) `top + height ≥ canvas_height − 8px` (slot encosta na borda inferior real, zero margem), OU (2) outro elemento visível tem bottom dentro de ±8px do bottom do slot E sobrepõe ≥40% da largura do slot horizontalmente. **Adicionalmente**: o slot precisa encostar numa borda lateral (`left ≤ 8px` ou `left + width ≥ canvas_width − 8px`) — cutout centralizado horizontalmente também é REVISE. Se qualquer condição falhar, devolva ao designer com `REVISE` antes de marcar.

## Regras críticas

- **`data-te-description` NUNCA é prosa descritiva.** Sempre a fórmula de 5 componentes (role / formato / bound / papel na composição / exemplos). Se você está escrevendo uma frase como "texto neutro e adaptável para qualquer nicho, com linguagem concreta e sem jargão" ou "título intermediário adaptável para qualquer área de atuação" — pare. Isso é o anti-pattern que quebra o LLM downstream. Use o catálogo + fórmula + exemplos derivados do texto real.

  ```
  ❌ PROIBIDO:
  "Slide 4 título: texto neutro e adaptável para qualquer nicho, com linguagem concreta e sem jargão."
  "Título intermediário adaptável para qualquer área de atuação."
  "Corpo de texto explicativo sobre o tema do slide."

  ✅ CORRETO:
  "Título da lâmina intermediária; formato afirmação direta OU inversão de expectativa;
 1 frase em 2 linhas; após eyebrow categórico; seguido de corpo educativo;
  ex: 'Paciente não compra expertise', 'O corpo fala antes de doer', 'Resultado não é só número'"
  ```

- **Inline `<span>` dentro de texto editável é estilo, não elemento separado.** Marque o `<h1>`/`<p>` pai como `data-template-element`, e o `<span>` interno só tem `style` (e opcional `data-variable` se a cor é brand). O converter vai virar `textbox.styles[lineIndex][charIndex]`.
- **Neutros não viram brand variables.** Branco, off-white, cinza, preto de body — ficam literais.
- **Acentos brand sem `data-variable` são bug.** Se há um botão laranja no design e a marca é azul, o usuário vai abrir o template no editor e o botão continua laranja. Isso quebra a promessa do produto.
- **Conservador no editável.** Quando em dúvida entre static e template-element, escolha static.
- **`data-te-description` é genérico no role, mas contextualizado nos exemplos.** Não escreva "Título sobre laserterapia premium" — escreva seguindo a fórmula `<role>; formato '<máscara>'; <bound>; <papel na composição>; ex: '<a>', '<b>', '<c>'`. Catálogo canônico em [`references/element-descriptions.md`](./references/element-descriptions.md). Template vai ser usado por dezenas de nichos; descriptions são reutilizáveis. **Porém:** use o **texto atual do elemento** como primeiro exemplo (generalizado), e descreva a **relação com elementos vizinhos** (anterior/posterior) para que o LLM entenda a sequência narrativa (ver regras de contextualização abaixo).
- **`data-te-max-chars` calculado pelo box, não pelo texto atual.** Estimativa: `floor((width × lines) / (fontSize × 0.6))`. Arredonde para cima na próxima dezena.
- **Repetidos entre slides usam mesma classificação.** Logo aparece em 5 slides? Todos com mesmo `data-image-type="brandLogo"`. Se o conteúdo deve ser o mesmo (logo, handle, foto profissional), use `data-te-link-id="logo"` (mesmo slug) em todos.
- **Preserve `text-transform`.** Se CSS tem `text-transform: uppercase`, adicione `data-te-text-case="uppercase"` para que o converter mantenha a intenção quando o AI preencher.

## `data-te-description` — fórmula dos 5 componentes

A description **vai literal no prompt do LLM gerador de copy** da lambda de geração de copy da plataforma. Description vaga gera output inconsistente entre slides; description estruturada com formato, **papel na composição** e exemplos guia o LLM para output consistente.

**Toda description segue a fórmula:**

```
<role narrativo>; formato '<máscara>'; <bound 1>; <papel na composição>; <bound 2>; ex: '<ex1>', '<ex2>', '<ex3>'
```

O **`<papel na composição>`** é o componente que diz **quem o elemento é dentro da estrutura da lâmina** (vem do passo 3c): `cabeçalho que governa a lista`, `item 1 de 3 de uma lista sequencial`, `célula 2 de 4 de uma grade`, `lado A da comparação`, `passo 3 de 5`. Ele é **obrigatório sempre que o slot se repete na mesma lâmina** (itens de checklist, células de grade, passos de tutorial) e **recomendado** quando o elemento tem relação pai/filho clara (título que governa uma lista). Para slots únicos sem repetição (um único título de capa, um único CTA), o componente pode ser omitido ou reduzido ao papel narrativo já presente.

> ⚠️ **Bounds NÃO repetem o número de caracteres.** O limite de chars é responsabilidade **exclusiva** do atributo `data-te-max-chars` (calculado pela caixa). **NUNCA** escreva `até 60 chars`, `30-70 chars`, `máximo 42 caracteres` dentro da `data-te-description`. Isso cria dois números concorrentes que quase sempre divergem do `data-te-max-chars` real (medido: 26 conflitos num único template de produção) — o LLM segue o número da prosa e a validação técnica rejeita. Os `<bound>` da description são **estruturais/de formato**: `1 linha`, `1 frase em 2-3 linhas`, `em CAPS`, `sem ponto final`. O comprimento vem do `data-te-max-chars`. A lambda de copy hoje remove defensivamente qualquer número de chars que escape para a description, mas a origem (aqui) não deve gerá-lo.

**Catálogo canônico de descriptions por role:** [`references/element-descriptions.md`](./references/element-descriptions.md). Cobre eyebrow numerado, eyebrow simples, hook, subtítulo, corpo educativo, bullet, dado numérico, caption, citação, CTA, linha de contato, foto contextual, foto profissional, logo. **Sempre consulte primeiro o catálogo** antes de compor uma description nova.

**Exemplo (eyebrow numerado em todo slide do carrossel):**

✅ Boa — formato + 3 exemplos genéricos:
```
Eyebrow editorial da lâmina; formato 'NN / TEMA' onde NN é o número
sequencial do slide e TEMA é categoria curta em CAPS;
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

1. **Slots equivalentes em SLIDES DIFERENTES recebem a mesma string — mas slots repetidos DENTRO da mesma lâmina NÃO.** Esta regra tem duas faces:
   - **Cross-slide (mesma string):** eyebrow do slide 1, slide 3 e slide 5 → mesma description. O LLM diferencia pelo contexto da página (mensagem-chave da narrative arc, que ele já vê separadamente).
   - **Within-slide (string varia pelo papel na composição):** item 1, item 2 e item 3 de um checklist na **mesma** lâmina **não** recebem strings idênticas. Eles compartilham role, formato e exemplos, mas o componente `<papel na composição>` muda: `item 1 de 3 de uma lista sequencial` / `item 2 de 3 ...` / `item 3 de 3 ...`. Aqui o LLM **não** tem contexto separado para diferenciar — a única pista de que formam uma sequência ordenada está na description. Aplicar a mesma string a slots repetidos na mesma lâmina é o anti-pattern que você está corrigindo.
   - **Exceção (título de miolo que governa estrutura distinta):** "mesma string cross-slide" vale para slots **genuinamente equivalentes** (eyebrow, page-counter). Um **título de miolo NÃO é genuinamente equivalente** quando cada slide tem uma estrutura/função diferente (slide de checklist vs. slide de comparação vs. slide de alerta). Aí a mensagem-chave da página, sozinha, não impede o LLM de gerar o **mesmo título em dois slides** (sintoma real observado: "SINAIS DE SOBRECARGA" repetido nos slides 1 e 2). Para títulos de miolo, embuta no `<papel na composição>` a **função do slide na narrativa** — `cabeçalho que governa a lista de N itens`, `título do slide de comparação A vs B`, `título do slide de alerta` — derivada do `brief.md`. Isso dá ao LLM o sinal que falta para diferenciar títulos entre slides.
2. **Exemplos NUNCA citam o vertical atual do template.** O template vai ser usado em dezenas de verticais diferentes; descriptions são reutilizáveis. Use exemplos de formato (`'01 / DOR'`, `'03 / O ESTUDO'`), não de conteúdo específico de vertical (`'01 / FISIOTERAPIA'`).
3. **Formato e conteúdo são coisas diferentes.** `formato 'NN / TEMA'` é estrutura; `ex:` mostra como aplicar.
4. **3 exemplos é o sweet spot.** 1 vira regra rígida, 5+ vira ruído. 3 cobrem variação curto/médio/longo.
5. **Sweet spot de tamanho da própria description: ≈200-300 caracteres.** (Isto é sobre o comprimento da *description* em si — não um bound do campo, que mora no `data-te-max-chars`.) Cada description vai pra cada elemento de cada template no prompt do LLM — pesar tokens importa.
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
seguido de corpo educativo; ex: 'Seu conhecimento está
virando resultados?', 'Você sabe o que seu paciente realmente busca?',
'O que faz um conteúdo converter de verdade?'
```

❌ Ruim — exemplos desconexos do contexto real:
```
Gancho principal da lâmina; formato pergunta provocativa; 1 frase;
ex: 'Sua ideia ficou clara?', 'O erro está no recorte',
'Mostre o próximo passo'
```

**Exemplo completo — lâmina de CHECKLIST (1 título + 3 itens):**

Padrão da lâmina (passo 3c): **checklist** — arquétipo A5-listicle-numbered-row. Slots: `título` (cabeçalho que governa a lista) + `item 1..3` (cada um com número + texto). Textos reais no HTML: título "Use este roteiro antes de criar qualquer peça."; item 1 "Qual percepção eu quero elevar?"; item 2 "Qual critério prova que existe método?"; item 3 "Qual convite faz sentido agora?".

✅ Correto — título carrega o papel de cabeçalho; cada item carrega seu índice na sequência:

Título (cabeçalho):
```
Título da lâmina de checklist; formato afirmação que introduz uma lista
de verificação; 1 frase em até 2 linhas; cabeçalho que governa a lista
de 3 itens abaixo; ex: 'Use este roteiro antes de começar',
'Confira antes de publicar', 'O que validar em cada etapa'
```

Item 1:
```
Item de checklist; formato pergunta curta de verificação OU instrução
objetiva; 1 linha; item 1 de 3 de uma lista sequencial — abre a
progressão; ex: 'Qual percepção eu quero elevar?',
'Defini o objetivo principal?', 'O ambiente está pronto?'
```

Item 2 (mesma role/formato/exemplos do item 1; muda só o papel na composição):
```
Item de checklist; formato pergunta curta de verificação OU instrução
objetiva; 1 linha; item 2 de 3 de uma lista sequencial — desenvolve o
critério central; ex: 'Qual percepção eu quero elevar?',
'Defini o objetivo principal?', 'O ambiente está pronto?'
```

Item 3:
```
Item de checklist; formato pergunta curta de verificação OU instrução
objetiva; 1 linha; item 3 de 3 de uma lista sequencial — fecha com o
próximo passo; ex: 'Qual percepção eu quero elevar?',
'Defini o objetivo principal?', 'O ambiente está pronto?'
```

❌ Errado — as 3 strings idênticas que o template original produzia (o LLM não sabe que formam uma sequência ordenada, nem quantos itens são):
```
Texto editável de apoio; formato frase curta conectada ao assunto
da lâmina; ex: 'Diagnóstico', 'Critério',
'explique o ponto principal'
```
(aplicada igual ao item 1, 2 e 3 — sem índice, sem contagem, sem cabeçalho)

> **Numeração visual (`1`, `2`, `3`) é estática**, não template-element: o número do item não muda por post, é `data-static="true"`. O que muda é o **texto** de cada item — esse sim leva `data-template-element` com o índice na composição.

## `template-summary.md` (vira `description` do Supabase verbatim)

O conteúdo deste arquivo é enviado **literal** como `description` da linha em `public.templates` pelo `gp2-template-uploader`. Não há reescrita downstream — o que você escreve aqui é o que aparece no editor e no embedding.

Formato exato (sem cabeçalhos, sem H1, sem seções):

```markdown
<2-3 linhas explicando o arco do post: o que o template quer fazer o leitor entender/sentir/agir, ponta-a-ponta.>

Slide 1: <papel narrativo curto>
Slide 2: <...>
Slide N: <CTA / fechamento>
```

Regras:

- **Não** escreva `# Resumo do template —`, `# Template summary —`, `## Arco`, `## Por slide`, `Descrição Geral:`, `Propósito do template:`, `Modelo adaptável:` ou qualquer outro cabeçalho. Eles viram lixo no Supabase.
- **Não** mencione nome de plataforma.
- **Não** detalhe campos editáveis — isso é metadado, não conteúdo da descrição.
- Use os papéis narrativos reais do `brief.md` (passo 3b) para cada slide; não invente papéis genéricos.
- Mantenha curto: 2-3 linhas de arco + 1 linha por slide. Templates têm um motivo para existir; a descrição deve refletir esse motivo de forma direta.

## Audit

```bash
python3 ../../scripts/audit-template-markup.py artifacts/gp2-template-marker/<slug>/
```

O script gera `marker-audit.json` + `marker-audit.md`. Loop máximo: **2 fixes**. Se ainda falhar, escale para o orquestrador.

Além das checagens de forma (atributos, classes, gradientes), o audit agora **reprova (FAIL)** problemas de **coerência composicional** — exatamente os que produziam copy ruim downstream. Se algum disparar, o erro está no passo 3c, não no layout:

- **Índice/contagem incoerente** — `item N de M` cujo M não bate com o nº real de slots irmãos no slide, ou índices que **reiniciam** (`1,2,3,1,2,3`) dentro do mesmo slide. Reinício = dois grupos marcados como um (provável comparação tratada como lista). Numa comparação legítima, marque cada lado com `lado A/lado B` — aí o audit valida cada lado como sequência própria.
- **Descriptions byte-idênticas em slots da mesma lâmina** — itens de checklist/grade com a mesma string. Devem diferir no componente `<papel na composição>` (`item 1 de N` / `item 2 de N` …).
- **Comparação sem `lado A/B`** — slide com slots paralelos mas sem `lado A da comparação` / `lado B da comparação` / `veredicto`.
- **Imagem sem papel narrativo** — `data-te-description` de imagem que não declara a função no slide (`imagem de capa/abertura`, `de prova`, `de fechamento/CTA`, `apoio contextual da lâmina`).
- **Imagem com tema/cena travado** — description que fixa o assunto do placeholder (joelho, mitocôndria, café, mesa, glow neon, sci-fi…). Mantenha só o **registro de estilo** (`dark premium editorial`) e deixe o **tema aberto**. Ver `references/element-descriptions.md` §"Foto contextual".

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
