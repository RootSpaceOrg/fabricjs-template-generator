# Técnicas — clinical-photo-editorial

Dinâmicas do estilo, destiladas dos vereditos (lessons.md guarda o histórico).
São TÉCNICAS, não coordenadas: o designer aplica com julgamento, variando entre
gerações. Exemplos concretos em `exemplos/` (esqueletos aprovados — ponto de
partida, nunca fôrma).

## Assinaturas (o que faz a peça ser DESTE pack)

1. Tipografia display teal GIGANTE em duo-tom (palavra-chave no accent),
   entrelaçada com o cutout do profissional na capa.
2. Objetos do tema DESFOCADOS (bokeh de primeiro plano) como decoração
   assimétrica fundindo no papel menta.
3. Composição assimétrica em camadas; pills outline; clean robusto.

## Técnicas de composição

- **Duo-tom entrelaçado (capa)**: headline `size="lg"` com span accent,
  `data-layer`, cruzando o cutout do profissional — texto e figura em camadas.
- **Par de fotos contínuas**: UMA foto paisagem (sujeito perto do centro)
  posicionada na `.fita-layer` sobre a fronteira de dois slides de miolo — a
  emenda corta a foto, cada slide fica com uma janela e a leitura flui.
  Os dois slides cedem a mesma borda (foto à direita do A, à esquerda do B).
- **Decor voando**: decor com `data-overhang` (ou na fita-layer), grande,
  cortado pela borda, rotação leve (10–20°). Capa 1–2 decors; miolo 0–1;
  nunca sobre texto/CTA/logo/professionalPhoto; só em background limpo.
- **Card sobre foto imersiva**: slide de miolo com foto full-bleed e `ds-card`
  respirando (flex+gap do motor) — número, headline e body dentro do card.
- **Fundos alternando**: papel menta na maioria, 1 slide invertido (accent)
  como respiro/CTA — nunca fita monocromática.
- **Stamps/pills**: eyebrow em `ds-stamp` outline; CTA em `ds-cta` pill cheia.

## Regras de imagem (ver images.md para fórmulas de prompt)

- Fotos: clínicas, cinematográficas, tons teal/verde profundo coerentes com a
  paleta; sem rostos identificáveis em fotos geradas.
- Decors: objeto do tema (aparelho, óculos, instrumento), transparente,
  desfoque profundo nascido na geração, inteiro com margem nas 4 bordas,
  gerado POR POST (exemplares de `assets/` são só da certificação).

## O que já foi reprovado (não repetir)

- Formas abstratas (ds-shape) neste pack — personalidade vem dos bokehs.
- Decor nítido, pequeno, solto no meio do canvas, ou de fundo chapado.
- Blur aplicado em pós-processo (PIL) — degrada; blur nasce na geração.
- Texto grudado em card sem respiro; bokeh sobre outras imagens.
- Duas gerações com o mesmo esqueleto (variância é dever).

- **Número/watermark gigante atrás de texto**: é CAMADA — sempre `data-layer` no elemento de trás (erro recorrente 2×: convert rejeita sobreposição não declarada).
