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

**Foto do par contínuo:** obrigatoriamente PAISAGEM larga (>=1792x1024) — cada slide mostra uma faixa vertical estreita; foto estreita faz as duas faixas coincidirem (repetição). O crop right continua exatamente onde o left parou.
**Decor:** blur gaussiano FORTE (objeto claramente fora de foco, bokeh fotográfico) e tema inequívoco da vertical — nitidez ou objeto genérico = reprovado.

**Decor (regra de composição):** GRANDE (área de grid ampla), sempre COLADO numa borda do slide para ser cortado por ela (impressão de 'voar'), com rotação leve (10–20°) e blur gaussiano MUITO forte (objeto quase abstrato, não rouba foco de título/foto). Nunca pequeno e solto no meio do canvas.
