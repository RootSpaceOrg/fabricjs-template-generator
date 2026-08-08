# Técnicas — clinical-photo-editorial

Dinâmicas do estilo, destiladas dos vereditos (histórico em `lessons.md`).
São TÉCNICAS, não coordenadas: aplique com julgamento, variando entre
gerações. Exemplos em `exemplos/` (partida, nunca fôrma).

## Assinaturas (o que faz a peça ser DESTE pack)

1. Tipografia display teal GIGANTE em duo-tom (palavra-chave no accent),
   entrelaçada com o cutout do profissional na capa.
2. Objetos do tema DESFOCADOS (bokeh de primeiro plano) como decoração
   assimétrica fundindo no papel menta.
3. Composição assimétrica em camadas; pills outline; clean robusto.

## Anatomia por tipo de slide (obrigatório — nenhum slide é só texto)

**Todo slide tem no mínimo DOIS elementos com peso.** Headline sozinha com
fundo liso é slide inacabado (ver `knowledge/design/geral.md`).

| Papel | O que o slide TEM que ter |
|---|---|
| **Abertura** | `ds-slot professionalPhoto` (cutout, placeholder canônico do motor — NUNCA pessoa gerada por IA) + headline `size="lg"` em duo-tom entrelaçada com o cutout + eyebrow/stamp + 1–2 decors do tema com `data-overhang` |
| **Item com foto** | foto do tema ocupando um terço/metade real do slide + número ou eyebrow + headline + body de 2–4 linhas. A foto é protagonista, não enfeite de canto |
| **Item chapado** (`data-invert`) | frase-tese grande em paper + mini-parágrafo de apoio LOGO ABAIXO (bloco de leitura contínuo, sem vão) + 1 decor ou número gigante como âncora |
| **Card sobre foto** | foto full-bleed + `ds-block data-overlay data-layer` + `ds-card data-elevated` COMPACTO (dimensionado pelo texto, alinhado à esquerda, assimétrico) |
| **Lista/bullets** | `ds-block` de acento com 2–3 itens curtos (uma linha cada) + eyebrow + colagem ou decor |
| **Fechamento** | `professionalPhoto` (espelha a abertura) + headline + body curto + `ds-cta` + logo |

## Técnicas de composição

- **Duo-tom entrelaçado (capa)**: headline `size="lg"` com span accent,
  `data-layer`, cruzando o cutout do profissional — texto e figura em camadas.
- **Par de fotos contínuas**: UMA foto paisagem (sujeito perto do centro) na
  `.fita-layer` sobre a fronteira de dois slides de miolo. Divisão EQUILIBRADA
  (40/60 no mínimo), foto GRANDE (faixa de rodapé ou meia-altura), sujeito
  perto da emenda, background limpo dos dois lados.
- **Decor voando**: decor com `data-overhang`, grande, cortado pela borda,
  rotação leve (10–20°). Capa 1–2; miolo 0–1; nunca sobre texto, CTA, logo ou
  professionalPhoto.
- **Full-bleed + overlay + card**: foto full-bleed, véu `data-overlay` e card
  compacto por cima — o slide de maior impacto; 1× por fita.
- **Fundos alternando**: papel menta na maioria, 1 slide invertido (accent)
  como respiro — nunca fita monocromática.
- **Fechamento espelha a abertura**: o CTA leva o `professionalPhoto` como a
  capa — a fita abre e fecha com o profissional presente.

## Régua de tamanho (aprendida em 2026-08-08)

Este pack é **denso por natureza** (foto + texto + camadas). Fita longa só se
houver conteúdo real:

- **5–6 slides**: o tamanho natural do estilo.
- **7–8 slides**: só quando o tema tiver 4+ blocos de conteúdo distintos e
  pelo menos 3 tratamentos diferentes de miolo. Sem isso, faça 5 — fita curta
  densa é melhor que longa e rala.

## Regras de imagem (ver images.md para fórmulas)

- Fotos: clínicas, cinematográficas, tons teal/verde profundo; sem rostos
  identificáveis em fotos geradas.
- **Pessoa = slot da plataforma.** O profissional é sempre
  `ds-slot data-slot="professionalPhoto"` com o placeholder canônico
  (`engine/assets/professional-photo-*.b64.txt`). Gerar avatar/ilustração de
  médico é violação R1 do judge.
- Decors: objeto do tema, transparente, desfoque profundo nascido na geração,
  inteiro com margem nas 4 bordas, gerado POR POST.

## O que já foi reprovado (não repetir)

- Formas abstratas (ds-shape) — a personalidade vem dos bokehs.
- Decor nítido, pequeno, solto no meio do canvas, ou de fundo chapado.
- Blur aplicado em pós-processo (PIL) — degrada; blur nasce na geração.
- Texto grudado em card sem respiro; bokeh sobre outras imagens.
- Duas gerações com o mesmo esqueleto (variância é dever).
- **Número/watermark gigante atrás de texto**: é CAMADA — sempre `data-layer`.
- **Avatar 3D/ilustrado no lugar do professionalPhoto** (2026-08-08).
- **Slide com headline e mais nada** — fundo liso ocupando o resto (2026-08-08).
- **Cartão grande com texto curto** — a caixa se ajusta ao conteúdo.
