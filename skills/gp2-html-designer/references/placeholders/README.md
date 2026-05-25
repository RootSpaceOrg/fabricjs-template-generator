# Placeholders da pipeline

Arquivos base64 prontos para uso no `src` de `<img>`. Nunca gere SVG inline nem invente imagens com CSS.

## Arquivos

| Arquivo | Uso | Tamanho |
|---------|-----|---------|
| `image-placeholder.b64.txt` | Imagens contextuais (`userAsset`) — fallback quando URL pública não disponível | ~3.5 KB |
| `professional-photo-1.b64.txt` | Foto profissional cutout — masculino, jaleco formal | ~210 KB |
| `professional-photo-2.b64.txt` | Foto profissional cutout — feminino, blazer casual | ~205 KB |
| `logo-quadrada.b64.txt` | Logo da marca (`brandLogo`) — placeholder quadrado neutro | ~78 KB |

Cada arquivo contém uma única linha no formato `data:image/png;base64,XXXX...` pronta para colar em `src=""`.

## Quando usar cada um

O `gp2-request-interpreter` sugere o placeholder no `brief.md` com base no contexto do vertical inferido. A heurística geral:

| Perfil predominante do vertical | Placeholder sugerido |
|---------------------------------|----------------------|
| Profissional de traje formal / jaleco / uniforme técnico | photo-1 (masculino, jaleco) |
| Profissional de traje casual / blazer / lifestyle | photo-2 (feminino, casual) |
| Ambíguo ou misto | qualquer dos dois |

Se a referência anexada mostra um perfil específico, ou se a composição/tom do template pede o outro perfil, o designer pode trocar livremente.

## Como usar no HTML

Cole o conteúdo do arquivo direto no `src` da `<img>`:

```html
<img class="professional-photo" alt="Foto profissional"
     style="position:absolute; left:540px; top:80px; width:540px; height:1200px;
            object-fit:contain; object-position:bottom center; border-radius:0;"
     src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...">
```

Sempre acompanhe de:
- `object-fit: contain` (não `cover`) — preserva a figura inteira sem cortar.
- `object-position: bottom center` — alinha pés ao rodapé do slot, espelhando o anchor `bottom-center` que o runtime aplica em `image-variable.ts`.
- `border-radius: 0` — cutout perde o sentido se o slot for circular ou arredondado.

Padrões prontos de posição (hero cover, CTA lateral, overlap): ver [`../professional-photo-placements.md`](../professional-photo-placements.md).

## Logo da marca (`brandLogo`)

Use [`logo-quadrada.b64.txt`](./logo-quadrada.b64.txt) como `src` de qualquer `<img data-image-type="brandLogo">`. Em produção, o runtime do editor substitui pelo logo real do usuário (a partir do brand config).

### Onde colocar (default canônico)

Sem instrução explícita do brief, o designer **deve** colocar logo em:

1. **Slide 1 (capa)** — uma das extremidades do header ou rodapé.
2. **Último slide (CTA)** — uma das extremidades do header ou rodapé.

Em outros slides (miolo): só se houver espaço limpo sobrando, não force.

### Regras de tamanho e posição

- **Tamanho:** box quadrado entre **80px e 240px**. Default sugerido: 120–140px nas extremidades; 160–200px se for o único elemento no header da capa.
- **Sempre ancorado em uma borda real**: encosta na borda esquerda OU direita do slide (`left ≤ 32px` ou `left + width ≥ data-width − 32px`). Logo centralizado horizontalmente sem âncora cria efeito "selo solto".
- **Vertical:** prefira rodapé (`top + height ≥ data-height − 32px`) para CTA e header (`top ≤ 32px`) para capa. Logo no meio do slide compete com headline — evite.
- **Nunca** sobre headline, body ou foto profissional. Se o único espaço disponível conflita com texto, melhor não colocar logo nesse slide.
- **Object-fit:** `contain` (preserva proporção do logo do usuário) com `object-position: center`.
- **Border-radius:** `0` por default. Slot do logo é quadrado neutro — qualquer arredondamento aplicado vira parte do design do logo real do usuário, então não force.

### Padrões de posição

| Padrão | Slide | Coords (canvas 1080×1350) |
|--------|-------|---------------------------|
| **Cover-header-left** | Slide 1 | `left:60px; top:60px; width:140px; height:140px;` |
| **Cover-header-right** | Slide 1 | `left:880px; top:60px; width:140px; height:140px;` |
| **Cover-footer-left** | Slide 1 | `left:60px; top:1150px; width:140px; height:140px;` |
| **CTA-footer-left** | Último slide | `left:60px; top:1150px; width:140px; height:140px;` |
| **CTA-footer-right** | Último slide | `left:880px; top:1150px; width:140px; height:140px;` |
| **CTA-header-large** | Último slide brand-forward | `left:60px; top:80px; width:200px; height:200px;` |

### Snippet

```html
<img class="brand-logo" alt="Logo da marca"
     data-image-type="brandLogo"
     style="position:absolute; left:60px; top:1150px; width:140px; height:140px;
            object-fit:contain; object-position:center; border-radius:0;"
     src="data:image/png;base64,<conteúdo de logo-quadrada.b64.txt>">
```

O marker aplica `data-static="true"` (o logo não muda por post; muda por marca, via brand config). Reviewer flagra ausência de logo na capa OU no CTA como warning (`brand-logo-missing-on-cover-or-cta`).

## Custo de payload

Cada placeholder adiciona ~210 KB ao `template.html`. Se o template usa `professionalPhoto` em 5 slides, o HTML cresce ~1 MB. Aceitável: o HTML só vive durante a pipeline (designer/reviewer/marker/converter); o Fabric JSON final não embute base64 — ele recebe o `imageType: "professionalPhoto"` e o runtime substitui pela URL real do usuário.

## Reminder importante

`data-image-type="professionalPhoto"` é a marca semântica que faz o produto trocar a imagem pela foto real do usuário no editor (ver `image-variable.ts:33-35`). O placeholder existe **só** para:

1. O designer avaliar visualmente se o slot está bem dimensionado para uma figura humana real.
2. O reviewer detectar problemas de composição (face coberta por texto, slot apertado demais, etc.).
3. O `gp2-template-converter` (self-validation) comparar render HTML × Fabric e validar drift.

Em produção, o placeholder nunca aparece — o usuário sobe sua própria foto durante onboarding (`completion-step.component.ts:119-130`) e ela substitui o placeholder em todos os slots `professionalPhoto`.

## Regenerar os arquivos

Se as PNGs originais mudarem (ou se quiser adicionar novos placeholders):

```bash
python scripts/generate-placeholder-base64.py \
  --in /caminho/para/asset.png \
  --out skills/gp2-html-designer/references/placeholders/asset.b64.txt
```

O script é genérico — serve para professional photos, brand logos ou qualquer outro placeholder PNG.
