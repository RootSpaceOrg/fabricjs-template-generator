# Placeholders do motor

Arquivos base64 prontos para o `src` de `<img>`. Nunca gere SVG inline nem
invente imagens com CSS. Posicionamento é **sempre** `grid-area` (CATALOG.md) —
px absoluto e `position:absolute` são rejeitados pelo conversor.

| Arquivo | Uso |
|---------|-----|
| `professional-photo-1.b64.txt` | slot `professionalPhoto` — masculino, jaleco formal |
| `professional-photo-2.b64.txt` | slot `professionalPhoto` — feminino, blazer casual |
| `logo-quadrada.b64.txt` | slot `logo` (brandLogo) — quadrado neutro |
| `image-placeholder.b64.txt` | fallback genérico de `userAsset` |

Cada arquivo tem uma linha `data:image/png;base64,...` pronta para colar.

## Como usar

```html
<img class="ds-slot" data-el-id="e7" data-slot="professionalPhoto" data-cutout
     style="grid-area: 4 / 7 / 13 / 13" src="data:image/png;base64,...">
```

- `data-cutout` faz o conversor tratar a figura como recorte inteiro (contain,
  sem crop) — é o comportamento certo para foto de pessoa.
- Logo: `data-slot="logo"`, ancorado numa borda (nunca solto no meio), com
  `data-inset` quando precisar de respiro da margem.
- Escolha do perfil (1 ou 2): pelo tom do pack/peça; o designer pode trocar.

## Por que existem

Em produção o placeholder **nunca aparece**: `data-slot`/`data-image-type`
viram `imageType` no JSON e o runtime do editor substitui pela foto real do
usuário. O placeholder serve para o designer dimensionar o slot, o judge
avaliar composição (rosto coberto? slot apertado?) e o conversor validar drift.

## Custo de payload

~210 KB por placeholder no HTML da run. Aceitável: o HTML vive só durante o
corredor. (Fotos geradas por run também viajam como data-URI no JSON final —
migrar para S3 está no roadmap do README.)
