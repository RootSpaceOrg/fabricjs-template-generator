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
   - `<html lang="pt-BR" data-template-name="..." data-segment="...">` (8 segmentos HealthMarket).
   - `<meta charset="utf-8">`.
   - `<meta name="hm-fonts" content="Fonte1,Fonte2">` listando todas as famílias usadas no CSS.
   - Opcional: `<meta name="hm-detected-primary" content="#...">` e `secondary` se você quiser fixar e pular auto-detecção.
4. **Caminhe slide por slide** (cada `<section class="slide">`) e para cada elemento decida na hora:
   - **Papel narrativo do slide** (capa/abertura, miolo educativo, prova/dado, CTA, fechamento). Use isso para escrever o `data-te-description`.
   - **Papel do elemento** dentro do slide (gancho, título, subtítulo, corpo, prova, CTA-label, foto contextual, foto profissional, logo, brand-handle, decoração). Use isso para escolher entre `data-template-element`, `data-text-type`, `data-static`, `data-image-type`.
5. Aplique a classificação (ver tabela abaixo).
6. Mapeie cores de marca: cada elemento cuja cor (fill/stroke/background) deve trocar com o preset da marca recebe `data-variable="primary|secondary"` + opcional `data-variable-target`.
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
| Carousel chrome — track, fill, counter "N/T" da progress bar | `data-static="true"` (designer já deve ter marcado; confirme) |
| Carousel chrome — fill da progress bar em slide LIGHT | `data-static="true"` + `data-variable="primary" data-variable-target="background"` (track e counter não recebem variable) |
| Carousel chrome — swipe arrow (background sutil + chevron SVG) | `data-static="true"` (em todos os slides exceto o último) |
| Formas decorativas (linhas, faixas, fundos, divisores) | nada (auto-detect como decoração) ou `data-static="true"` se ambíguo |
| Acento de cor que troca com preset (botão, headline colorido, faixa) | `data-variable="primary\|secondary"` + opcional `data-variable-target="fill\|stroke\|background"` |
| Slide background colorido brand | no `<section>`: `data-variable="primary"` + `data-variable-target="background"` |
| Span dentro de título com cor diferente | `<span data-variable="..." style="color:...">` (não é elemento separado!) |

> **Nota sobre `professionalPhoto` cutout PNG:** quando a `<img data-image-type="professionalPhoto">` usa `object-fit: contain` e `object-position: bottom center` (PNG cutout transparente — ver [`gp2-html-designer/references/professional-photo-placements.md`](../gp2-html-designer/references/professional-photo-placements.md)), a classificação no marker **não muda** — continua `data-static="true"`. Mas o converter precisa emitir o `ClippableImage` em modo cutout: `originWidth/Height` = dimensões naturais do PNG (não do slot), `width === originWidth`, `cropX/Y = 0`, `originY: "bottom"`. Ver `gp2-template-converter/SKILL.md` §"ClippableImage cutout (CRÍTICO)". O reviewer (`scripts/review-fabric-json.py`) tem check deterministica que flagra cutout mal-emitido (`width !== originWidth` com `cropX/Y = 0`).
>
> **Antes de marcar, confirme**: o slot da `<img>` cutout no HTML tem aspect ratio `width/height` entre `0.55` e `1.10` (PNG cutout é ~3:4 = 0.78). Se estiver fora, devolva ao designer com `REVISE` indicando o ratio observado. Slots muito altos (ex: `540×1200` = 0.45) ou muito largos (ex: `540×400` = 1.35) deixam metade do slot vazia e induzem o converter a erro — sintoma observado em produção: figura cobrindo só metade do slot no editor com a face cortada.

## Regras críticas

- **Inline `<span>` dentro de texto editável é estilo, não elemento separado.** Marque o `<h1>`/`<p>` pai como `data-template-element`, e o `<span>` interno só tem `style` (e opcional `data-variable` se a cor é brand). O converter vai virar `textbox.styles[lineIndex][charIndex]`.
- **Neutros não viram brand variables.** Branco, off-white, cinza, preto de body — ficam literais.
- **Acentos brand sem `data-variable` são bug.** Se há um botão laranja no design e a marca é azul, o usuário vai abrir o template no editor e o botão continua laranja. Isso quebra a promessa do produto.
- **Conservador no editável.** Quando em dúvida entre static e template-element, escolha static.
- **`data-te-description` é genérico, não específico.** Não escreva "Título sobre laserterapia premium". Escreva "Título principal da lâmina de abertura; apresenta a dor ou promessa central em formato de gancho curto". O template vai ser usado por dezenas de nichos.
- **`data-te-max-chars` calculado pelo box, não pelo texto atual.** Estimativa: `floor((width × lines) / (fontSize × 0.6))`. Arredonde para cima na próxima dezena.
- **Repetidos entre slides usam mesma classificação.** Logo aparece em 5 slides? Todos com mesmo `data-image-type="brandLogo"`. Se o conteúdo deve ser o mesmo (logo, handle, foto profissional), use `data-te-link-id="logo"` (mesmo slug) em todos.
- **Preserve `text-transform`.** Se CSS tem `text-transform: uppercase`, adicione `data-te-text-case="uppercase"` para que o converter mantenha a intenção quando o AI preencher.

## Boas vs. más descrições (`data-te-description`)

✅ Boas (genéricas, reutilizáveis):
- "Título principal da lâmina 1; apresenta a dor ou promessa central em formato de gancho curto"
- "Eyebrow acima do título; rótulo curto que categoriza o tema do post"
- "Subtítulo de apoio ao gancho; complementa a promessa em uma linha"
- "Corpo de conteúdo da lâmina educativa; explica o conceito ou apresenta as evidências"
- "Label do CTA final; ação explícita que o leitor deve tomar"

❌ Ruins (específicas demais):
- "Título sobre laserterapia premium"
- "Tema: clínica de joelho — manter tom acolhedor"
- "Foto da clínica do Dr. João"
- "Texto explicando os 3 benefícios do whey"

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
