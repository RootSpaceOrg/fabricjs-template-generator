# Imagens - clinical-photo-editorial (v3, referencia unica)

**Registro:** clinica premium; papel menta #E9F3F1; teal profundo; luz suave; NUNCA estourado; nunca resultado clinico real.

| Slot | Formula |
|------|---------|
| decor (assets/decor-*.png) | OBJETO DO TEMA desfocado com FUNDO TRANSPARENTE (ex.: aparelho de laser genérico em bokeh) — nunca fundo chapado ("bolha"); gerar por vertical/tema |
| decor legado (decor-blur-N) | "objeto cirurgico (touca/mascara/gaze) COMPLETAMENTE desfocado, bokeh de primeiro plano, sobre fundo liso verde-menta #E9F3F1, luz suave, sem texto, 800x800" — regenerar so quando o pack pedir variacao |
| item_foto (A/B) | "detalhe de ambiente clinico premium - {conceito} - tons verde-petroleo, luz direcional suave, editorial, sem pessoas identificaveis, sem texto" |
| item_foto (C) | "ambiente clinico amplo em penumbra premium, tons teal, luz pontual suave, sem texto" |
| foto_profissional | slot da plataforma (placeholder canonico no render) |

**Par contínuo (A seguido de B):** as duas recipes recebem a MESMA imagem; A mostra a metade esquerda (`pos=left`), B a direita (`pos=right`) — transição suave entre os slides.
