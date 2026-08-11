# Imagens — clinical-photo-editorial

**Registro:** clínica premium, editorial, cinematográfico. NUNCA estourado,
nunca resultado clínico real, nunca banco de imagens genérico. O pack não guarda
assets — TODA run gera fotos/decors na hora, específicos do tema, em
`artifacts/runs/<slug>/assets/`.

## Cor neutra ≠ imagem neutra

A foto **não carrega a cor da marca** — quem veste a marca é o texto e as caixas
(`data-variable`). Cena verde-petróleo numa peça roxa parece erro de montagem.

Mas isso é sobre **cor**, não sobre energia. Pedir "neutro dessaturado, penumbra,
tons escuros" tudo junto produz foto séria e apagada, sem personalidade
(veredito 2026-08-09) — o oposto de editorial premium.

**O que dá personalidade sem cravar cor:**

- **Luz com direção e drama** — recorte lateral forte, contraluz, faixa de sol,
  reflexo no metal. Contraste alto é bem-vindo; o que não pode é a cor dominar.
- **Cena com vida** — mãos em movimento, gesto interrompido, objeto em uso.
  Bancada arrumada e vazia é catálogo, não editorial.
- **Matéria e textura** — tecido, madeira, vidro, metal escovado, pele. A
  superfície precisa se ver.
- **Ângulo autoral** — muito fechado (macro) ou muito aberto; nunca o plano
  médio de folheto.
- **Um acento de cor da CENA** é permitido e desejável: madeira quente, um
  âmbar, azul-noite, o brilho de um aparelho. O que se evita é uma cor
  **dominante** que compita com a marca — não é o mesmo que tirar toda a cor.

**Régua**: a foto pode ter caráter forte desde que a marca continue sendo o
elemento mais colorido da peça.

| Slot | Fórmula |
|------|---------|
| decor | OBJETO DO TEMA (aparelho, óculos, instrumento) JÁ GERADO extremamente fora de foco ("extremely out of focus, dreamy bokeh, barely recognizable"), fundo 100% transparente (RGBA), objeto INTEIRO com margem generosa nas 4 bordas. Blur em pós-processo (PIL) é PROIBIDO. Nitidez, objeto genérico ou fundo chapado = reprovado |
| foto de miolo | "{conceito: o OBJETO/gesto do tema, nomeado — não o clima} em ambiente clínico premium — **mãos/gesto em ação**, luz direcional forte com recorte, textura visível, profundidade rasa, ângulo autoral (macro ou amplo), editorial cinematográfico; cor da cena livre desde que nenhuma domine; sem pessoas identificáveis, sem texto" |
| foto imersiva (full-bleed) | "ambiente clínico amplo, **luz dramática com fonte visível** (janela, luminária, reflexo), atmosfera, profundidade; editorial premium, sem texto" |
| foto do par contínuo | paisagem larga (>=1792x1024), sujeito perto do CENTRO — vai INTEIRA na `.fita-layer` sobre a fronteira; a emenda corta a foto |
| arcos (assinatura) | NÃO se gera: `cp packs/clinical-photo-editorial/assets/arcos.svg artifacts/runs/<slug>/assets/`. Geometria fixa do estilo — dois arcos de traço fino em oposição diagonal, cortados pelas bordas. Vai na capa e no fechamento |
| foto_profissional | slot da plataforma (placeholder canônico no render) |

**Composição do decor:** grande, colado numa borda (cortado por ela — "voando"),
rotação leve (10–20°); nunca pequeno/solto no meio do canvas; nunca sobre
professionalPhoto, texto, CTA ou logo — só background limpo.

**Dois testes antes de aprovar um asset:**
1. Imagine a peça com marca roxa e com laranja — a foto briga com alguma?
   Então tem cor dominante demais.
2. A foto seguraria sozinha num feed? Se é bancada arrumada com luz chapada,
   está neutra demais — falta gesto, luz ou ângulo.

## O conceito nomeia o assunto

Ver `knowledge/design/geral.md` — `{conceito}` é o objeto ou gesto DO TEMA, não
o clima do post. Teste: leia o prompt sem o nome do tema; se ainda serve a
qualquer assunto, ele está vago.
