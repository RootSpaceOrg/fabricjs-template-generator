# Técnicas — emotive-fullbleed-lettering

Estilo de PEÇA ÚNICA (data comemorativa; `data-role="unica"`), pode estender a
2–3 slides quando a data pedir história. A cor dominante é a PRIMARY DO USUÁRIO
— a peça inteira se veste da marca.

## Anatomia da peça (de trás pra frente, ordem no DOM)

1. **Foto emocional full-bleed** (`ds-photo` 1/1/13/13, static+layer): pessoas
   reais no momento da data (pai e filho, mãe e bebê…), luz quente, emoção
   genuína. O TERÇO INFERIOR da foto deve ser "sacrificável" (vira cor).
2. **Overlay-gradiente da primary** (`ds-block data-overlay-gradient="primary"`
   + `data-layer`, 1/1/13/13): transparente no topo → primary sólida no rodapé.
   É o que funde foto e marca — a plataforma recolore por stop.
3. **Lettering-arte** (`ds-photo` static+layer, RGBA gerada por run): a palavra
   da data em display gigante cream + versão script sobreposta + 1–2 OBJETOS 3D
   do tema entrelaçados nas letras. Ocupa a faixa central (rows 4–11, quase
   largura total — veredito 2026-08-06: lettering GRANDE domina a peça),
   pode sangrar levemente nas laterais. NUNCA texto editável — é arte.
4. **Sparkles/ornamentos**: RGBA gerada (estrelas 4 pontas cream, brilhos),
   1–3 pontos discretos em volta do lettering; nunca sobre rostos.
5. **Data pequena** (`ds-eyebrow` static): "09 AGOSTO".
6. **Copy curta** (`ds-body` editável, tone ink, centralizada, rows ~10–11):
   2–3 linhas de homenagem — dentro do compliance, sem promessa.
7. **Rodapé institucional** (veredito 2026-08-06): data + copy + linha
   telefone/instagram sobem (rows ~9–11) e o **logo fica sozinho, CENTRALIZADO
   na base** (row 12, cols 6–8, `data-inset="bottom"` para não grudar na borda) — nunca espremido no canto.

## Extensao para 2-3 slides

Quando a data pede historia, a peca vira 2-3 slides. O interno NAO repete o
lettering (ele e a assinatura da capa): mantem a mesma foto e o mesmo
gradiente da primary, e leva a mensagem em texto — headline em sentence case
centralizada na faixa de cor, apoio curto abaixo, logo sozinho na base.
A continuidade visual vem do gradiente, nao da repeticao do lettering.

Exemplar: `exemplos/ref-extensao.jpg` (o interno) ao lado de
`exemplos/ref-anatomia-da-peca.jpg` (a peca unica completa).

## Leis do estilo

- Rostos NUNCA cobertos por lettering/overlay denso — a emoção é o scroll-stop.
- Lettering legível contra o gradiente: cream sobre primary escura.
- Máximo 1 palavra-conceito no lettering (a data); a copy curta faz o resto.
- O gradiente cobre no mínimo os 40% inferiores; topo da foto respira sem véu.
- Peça única não tem travessia; se estender a 2–3 slides, manter o mesmo
  gradiente nos internos, com lettering só na capa.
