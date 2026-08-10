# Imagens — editorial-cards-continuos

**Registro:** editorial de revista, cinematográfico, luz natural forte. Este
pack usa POUCAS imagens — em geral só a capa. O peso visual vem dos cartões e
da tipografia, não de fotografia em todo slide.

## Cor: sem dominante, mas com caráter

A foto não carrega a cor da marca (quem veste é o cartão de acento e a
marcação). Mas **cor neutra não é imagem neutra**: luz dramática, gesto e
matéria são o que fazem a capa segurar o scroll.

- **Luz natural com direção** — janela lateral, sol rasante, sombra longa.
- **Pessoa em gesto real** — sentada, apoiada, em movimento parado; nunca pose
  de catálogo. Sem rosto identificável.
- **Matéria quente** — madeira, tecido, couro, concreto. A superfície aparece.
- **Penumbra com ponto de luz**, não escuridão chapada: a capa é escura porque
  o texto claro vive sobre ela, e precisa de área calma no terço inferior.
- Um acento de cor da cena é bem-vindo (madeira, âmbar, verde-oliva) desde que
  nenhuma cor domine a ponto de brigar com a marca.

| Slot | Fórmula |
|------|---------|
| foto da capa | "{conceito} — pessoa em gesto natural em ambiente com madeira e tecido, luz de janela lateral forte com sombra longa, penumbra quente, editorial cinematográfico, ÁREA CALMA E ESCURA no terço inferior para texto claro, sem rosto identificável, sem texto" — retrato 1024x1536 |
| marcação (assinatura) | NÃO se gera: `cp packs/editorial-cards-continuos/assets/marcacao-elipse.svg artifacts/runs/<slug>/assets/`. Elipse manuscrita sobre a palavra-chave da capa |
| foto em cartão (opcional) | só quando o conteúdo pedir prova visual: "{conceito}, detalhe fechado, luz direcional, textura visível, editorial, sem texto" — ocupa o topo do cartão, nunca o cartão inteiro |
| logo / foto_profissional | **este pack NÃO usa** — ver abaixo |

**Dois testes antes de aprovar a capa:**
1. O texto claro do terço inferior fica legível? Se a foto tem alto contraste
   ali, gere de novo com a área calma.
2. A foto seguraria sozinha num feed? Se é ambiente vazio e bem iluminado por
   igual, falta gesto e direção de luz.

## Este pack não tem logo nem foto do profissional

`professionalPhoto` e `logo` existem no motor, mas **não neste estilo**. Todo
conteúdo aqui vive dentro de um cartão, e a `.fita-layer` pinta por cima dos
slides: um slot solto na `<section>` fica atrás dos cartões ou colado na borda
do slide, comendo o gap entre eles.

A identidade do profissional aparece pelo **@ no rodapé da capa** e pelo **site
no cartão de fechamento** — texto, não imagem. É a assinatura do estilo
editorial: a marca fala pela tipografia e pela cor do cartão de acento.

Se um dia o pack precisar de logo, ele entra COMO CONTEÚDO DE CARTÃO, com
`grid-area` dentro dos limites dele — nunca solto na section.
