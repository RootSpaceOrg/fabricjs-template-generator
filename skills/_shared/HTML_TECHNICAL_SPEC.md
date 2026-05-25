# Spec técnica HTML — regras invioláveis

Spec compartilhada entre `gp2-html-designer`, `gp2-html-reviewer`, `gp2-template-marker` e `gp2-template-converter`. **Não duplique este conteúdo nas SKILLs** — referencie.

Para o contrato high-level e intercambialidade com Claude Design / Estratégia A, ver [`../../CONTRACT.md`](../../CONTRACT.md). Para o sistema de gradientes, ver [`./GRADIENT_SYSTEM.md`](./GRADIENT_SYSTEM.md).

## As 13 regras

1. **Estrutura por slide.** Uma `<section class="slide" data-width="N" data-height="M">` por slide. Atributos `data-width` e `data-height` em pixels, números inteiros.

2. **Posicionamento absoluto.** Todo elemento dentro do `.slide` usa `position: absolute` com `left/top/width/height` em px. **Sem flex/grid no canvas.** Wrappers internos só são permitidos se também posicionados absolutamente.

3. **CSS sempre inline.** Tudo no atributo `style=""` de cada tag. **Proibido** `<style>` block com regras de canvas, **proibido** classes CSS dependendo de `<style>`. Única exceção tolerada: reset mínimo `* { margin:0; box-sizing:border-box; }`. O converter lê estilos diretamente de `style` — bloco `<style>` impede detecção de gradientes, posições, cores e tamanhos.

4. **Imagens reais.** Uma `<img>` por região de imagem. **Sem CSS shapes simulando foto.** Atributo `data-image-type="brandLogo|professionalPhoto|userAsset"` aplicado pelo marker.

5. **Sem pseudo-elementos.** Nada de `::before`, `::after`. Tudo precisa ser um nó DOM real para o converter detectar.

6. **Sem animações.** Sem `@keyframes`, sem `animation`, sem `transition` que afete o frame final.

7. **Sem efeitos exóticos.** Sem `mix-blend-mode`, `backdrop-filter`, `mask-image` complexo. O Fabric runtime não reproduz.

8. **Pesos de fonte explícitos.** `font-weight: 400/500/600/700/800`. **Nunca só `bold`** — o conversor mapeia número, não keyword.

9. **Fontes declaradas.** `<meta name="hm-fonts" content="Fonte1,Fonte2">` no `<head>` listando **todas** as famílias usadas no CSS. Fonte usada em `style` sem aparecer no meta é erro do reviewer.

10. **Segmento e nome.** `<html lang="pt-BR" data-template-name="<slug>" data-segment="<segmento-kebab-case>">`. Slug do vertical inferido do brief (ex: `clinicas-medicas`, `ecommerce-moda`).

11. **Rotação.** Só via `transform: rotate(Ndeg)`. Sem matrizes, sem outras transformações compostas no canvas.

12. **Copy em PT-BR verbatim.** Texto dos elementos vem do brief sem reescrita. Hook do slide 1 = exatamente como escrito no brief.

13. **Gradientes via preset.** Todo elemento com `linear-gradient` ou `radial-gradient` no `style` **DEVE** ter `data-darken="<preset>"` + `data-darken-opacity` (escurecimento neutro) **OU** `data-glow="<preset>"` + `data-glow-variable` + `data-glow-alpha` (glow brand). Cores brand hex em gradientes lineares são proibidas — ver [`GRADIENT_SYSTEM.md`](./GRADIENT_SYSTEM.md).

## Esqueleto mínimo

```html
<!doctype html>
<html lang="pt-BR" data-template-name="<slug>" data-segment="<segmento>">
<head>
  <meta charset="utf-8">
  <meta name="hm-fonts" content="FonteDisplay,FonteBody">
  <link href="https://fonts.googleapis.com/css2?family=FonteDisplay:wght@700;800&family=FonteBody:wght@400;500&display=swap" rel="stylesheet">
</head>
<body style="margin:0; padding:0;">
  <section class="slide" data-width="1080" data-height="1350"
           style="position:relative; width:1080px; height:1350px; overflow:hidden; background:#F5F3EF;">
    <!-- elementos com position:absolute; left:Xpx; top:Ypx; width:Wpx; height:Hpx -->
  </section>
  <!-- demais slides -->
</body>
</html>
```

## Atributos `data-*` reconhecidos

Marcação aplicada pelo `gp2-template-marker` (designer já aplica `data-variable`, `data-darken`, `data-glow`).

| Atributo | Aplicado em | Significado |
|----------|-------------|-------------|
| `data-template-name` | `<html>` | slug interno do template |
| `data-segment` | `<html>` | vertical/segmento da marca (kebab-case) |
| `data-width`, `data-height` | `<section class="slide">` | dimensões do canvas em px |
| `data-variable` | qualquer elemento | `"primary"` ou `"secondary"` — troca com preset da marca |
| `data-variable-target` | qualquer elemento | `"fill"` / `"stroke"` / `"background"` (opcional) |
| `data-darken` | overlay div com gradient | preset de escurecimento — ver `GRADIENT_SYSTEM.md` |
| `data-darken-opacity` | overlay div com `data-darken` | `0.1`–`1.0` |
| `data-glow` | overlay div com radial gradient brand | `"center"` (único valor canônico hoje) |
| `data-glow-variable` | overlay com `data-glow` | `"primary"` / `"secondary"` |
| `data-glow-alpha` | overlay com `data-glow` | `0.0`–`1.0` |
| `data-gradient` | overlay custom (fallback) | JSON cru do gradient Fabric — raro |
| `data-image-type` | `<img>` | `"brandLogo"` / `"professionalPhoto"` / `"userAsset"` |
| `data-template-element` | texto/img que varia por post | `"true"` |
| `data-te-description` | texto/img template-element | fórmula 4 componentes (ver marker SKILL.md §`data-te-description`) |
| `data-te-max-chars` | texto template-element | inteiro |
| `data-te-remove-bg` | `<img data-image-type="userAsset">` | `"true"` / `"false"` |
| `data-text-type` | texto de perfil de marca | `"instagramHandle"` / `"instagramName"` / `"phone"` / `"address"` |
| `data-static` | qualquer elemento que não troca por post | `"true"` |

## Anti-patterns críticos (reviewer flagra como FAIL)

- `<style>` block com regras de layout — converter cego.
- Classes CSS dependendo de `<style>` (sem inline) — converter cego.
- Elementos sem `position: absolute` no canvas — coordenadas indeterminadas.
- `<img>` substituída por `<div>` com `background-image` — converter trata como shape.
- `font-weight: bold` em vez de número — mapping falha.
- Fonte no CSS mas ausente em `<meta name="hm-fonts">` — runtime quebra.
- Gradiente sem `data-darken`/`data-glow`/`data-gradient` — vira cor sólida no Fabric.
- Cores brand hex em `linear-gradient` — proibido.

## Verificações estruturais (designer auto-revisa antes de renderizar)

| Verificação | Esperado |
|-------------|----------|
| `<html data-template-name="..." data-segment="...">` | presente |
| `<meta name="hm-fonts" content="...">` | presente com todas as famílias usadas |
| Cada slide tem `<section class="slide" data-width="N" data-height="M">` | presente |
| Cada slide tem `style="position:relative; width:Npx; height:Mpx;"` | presente |
| Cada elemento interno tem `style="position:absolute; left:Xpx; top:Ypx; ..."` | presente |
| Sem `<style>` block com regras CSS no `<head>` | ausente |
| Sem `class="..."` dependendo de `<style>` block | ausente |
| Todos os gradientes têm `data-darken` ou `data-glow` ou `data-gradient` | presente |

Falha estrutural → corrija antes de renderizar screenshots; screenshots de HTML inválido não têm valor de revisão.

## Validadores

- `scripts/audit-template-markup.py` — auditoria de `data-*` no HTML marcado. Roda no `gp2-template-marker`.
- `scripts/validate-slides.js` — validação do Fabric JSON emitido. Roda no `gp2-template-converter` como self-validation pós-emissão.
- `scripts/review-fabric-json.py` — debug standalone (não é step da pipeline; reviewer usa quando precisa investigar Fabric JSON específico).

Ambos os validadores em PASS = HTML válido + Fabric JSON pronto para o editor.
