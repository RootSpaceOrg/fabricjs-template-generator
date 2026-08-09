# Imagens — clinical-photo-editorial

**Registro:** clínica premium, editorial, cinematográfico. Luz direcional suave,
sombra presente, profundidade rasa; NUNCA estourado, nunca resultado clínico
real, nunca banco de imagens genérico. O pack não guarda assets — TODA run gera
fotos/decors na hora, específicos do tema, em `artifacts/runs/<slug>/assets/`.

## Cor nas imagens: neutra, com personalidade

A foto **não carrega a cor da marca** — quem veste a marca é o texto e as caixas
(`data-variable`). Foto em cor fixa do pack destoa assim que o cliente não tem
aquela paleta: uma cena verde-petróleo numa peça roxa parece erro de montagem.

Isso **não** significa foto branca, bege ou sem graça. A personalidade vem de:

- **Luz**: direcional, lateral, com sombra desenhada — não iluminação chapada.
- **Profundidade**: foco raso, fundo desfocado, primeiro plano presente.
- **Matéria**: superfícies reais (tecido, metal escovado, vidro, pele), textura
  visível.
- **Enquadramento**: detalhe fechado ou ambiente amplo em penumbra — nunca o
  "plano médio de catálogo".
- **Neutro escuro ou neutro claro**, com no máximo um desvio sutil de
  temperatura — o suficiente para não parecer laboratório fotográfico.

Se a marca for muito saturada, puxe a foto para o neutro mais frio ou mais
quente **na direção oposta**, para a cor da marca ressaltar em vez de brigar.

| Slot | Fórmula |
|------|---------|
| decor | OBJETO DO TEMA (aparelho, óculos, instrumento) JÁ GERADO extremamente fora de foco ("extremely out of focus, dreamy bokeh, barely recognizable"), fundo 100% transparente (RGBA), objeto INTEIRO com margem generosa nas 4 bordas. Blur em pós-processo (PIL) é PROIBIDO. Nitidez, objeto genérico ou fundo chapado = reprovado |
| foto de miolo | "detalhe de ambiente/procedimento clínico premium — {conceito} — **paleta neutra dessaturada**, luz direcional suave com sombra presente, profundidade rasa, editorial, sem pessoas identificáveis, sem texto" |
| foto imersiva (full-bleed) | "ambiente clínico amplo em penumbra premium, **tons neutros escuros**, luz pontual suave criando contraste, sem texto" |
| foto do par contínuo | paisagem larga (>=1792x1024), sujeito perto do CENTRO — vai INTEIRA na `.fita-layer` sobre a fronteira; a emenda corta a foto |
| foto_profissional | slot da plataforma (placeholder canônico no render) |
| **arcos (assinatura)** | NÃO se gera: `cp packs/clinical-photo-editorial/assets/arcos.svg artifacts/runs/<slug>/assets/`. Geometria fixa do estilo — dois arcos de traço fino em oposição diagonal, cortados pelas bordas. Vai na capa e no fechamento |

**Composição do decor:** grande, colado numa borda (cortado por ela — "voando"),
rotação leve (10–20°); nunca pequeno/solto no meio do canvas; nunca sobre
professionalPhoto, texto, CTA ou logo — só background limpo.

**Teste antes de aprovar um asset:** imagine a peça com uma marca roxa e outra
laranja. Se a foto brigar com alguma das duas, ela está colorida demais.
