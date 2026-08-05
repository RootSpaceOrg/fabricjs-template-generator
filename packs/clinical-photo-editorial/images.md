# Imagens - clinical-photo-editorial (v3, referencia unica)

**Registro:** clinica premium; papel menta #E9F3F1; teal profundo; luz suave; NUNCA estourado; nunca resultado clinico real.

| Slot | Formula |
|------|---------|
| decor (assets/decor-*.png) | OBJETO DO TEMA desfocado com FUNDO TRANSPARENTE (ex.: aparelho de laser genérico em bokeh) — nunca fundo chapado ("bolha"); gerar por vertical/tema |
| decor legado (decor-blur-N) | "objeto cirurgico (touca/mascara/gaze) COMPLETAMENTE desfocado, bokeh de primeiro plano, sobre fundo liso verde-menta #E9F3F1, luz suave, sem texto, 800x800" — regenerar so quando o pack pedir variacao |
| item_foto (A/B) | "detalhe de ambiente clinico premium - {conceito} - tons verde-petroleo, luz direcional suave, editorial, sem pessoas identificaveis, sem texto" |
| item_foto (C) | "ambiente clinico amplo em penumbra premium, tons teal, luz pontual suave, sem texto" |
| foto_profissional | slot da plataforma (placeholder canonico no render) |


**Foto do par contínuo (fita-v2):** paisagem larga (>=1792x1024), sujeito perto do CENTRO — ela vai INTEIRA na `.fita-layer` sobre a fronteira dos dois slides; a emenda corta a foto (sem split, sem pré-corte).
**Decor:** blur gaussiano FORTE (objeto claramente fora de foco, bokeh fotográfico) e tema inequívoco da vertical — nitidez ou objeto genérico = reprovado.

**Decor (regra de composição):** GRANDE (área de grid ampla), sempre COLADO numa borda do slide para ser cortado por ela (impressão de 'voar'), com rotação leve (10–20°) e blur gaussiano MUITO forte (objeto quase abstrato, não rouba foco de título/foto). Nunca pequeno e solto no meio do canvas.

**Blur do decor nasce na GERAÇÃO** (prompt: 'extremely out of focus, dreamy bokeh, barely recognizable') — PROIBIDO aplicar blur em pós-processo (PIL/convert degrada e mata o realce natural do modelo). Decor NUNCA sobrepõe o professionalPhoto nem elementos de ação.

**Assets do pack são EXEMPLARES, não estoque:** os `assets/decor-*.png` existem só para certificação/validação do pack. Em produção (posts definitivos), o agente SEMPRE gera decors novos, específicos do tema/segmento do post, seguindo as regras deste arquivo (objeto do tema, inteiro com margem, dreamy bokeh na geração, fundo transparente). Reusar os exemplares do pack em post final = reprovado.
