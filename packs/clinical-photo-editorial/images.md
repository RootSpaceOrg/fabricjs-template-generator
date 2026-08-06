# Imagens — clinical-photo-editorial

**Registro:** clínica premium; papel menta #E9F3F1; teal profundo; luz suave;
NUNCA estourado; nunca resultado clínico real. O pack não guarda assets — TODA
run gera fotos/decors na hora, específicos do tema, em `artifacts/runs/<slug>/assets/`.

| Slot | Fórmula |
|------|---------|
| decor | OBJETO DO TEMA (aparelho, óculos, instrumento) JÁ GERADO extremamente fora de foco ("extremely out of focus, dreamy bokeh, barely recognizable"), fundo 100% transparente (RGBA), objeto INTEIRO com margem generosa nas 4 bordas. Blur em pós-processo (PIL) é PROIBIDO. Nitidez, objeto genérico ou fundo chapado = reprovado |
| foto de miolo | "detalhe de ambiente/procedimento clínico premium — {conceito} — tons verde-petróleo, luz direcional suave, editorial, sem pessoas identificáveis, sem texto" |
| foto imersiva (full-bleed) | "ambiente clínico amplo em penumbra premium, tons teal, luz pontual suave, sem texto" |
| foto do par contínuo | paisagem larga (>=1792x1024), sujeito perto do CENTRO — vai INTEIRA na `.fita-layer` sobre a fronteira; a emenda corta a foto |
| foto_profissional | slot da plataforma (placeholder canônico no render) |

**Composição do decor:** grande, colado numa borda (cortado por ela — "voando"),
rotação leve (10–20°); nunca pequeno/solto no meio do canvas; nunca sobre
professionalPhoto, texto, CTA ou logo — só background limpo.
