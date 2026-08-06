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
   do tema entrelaçados nas letras. Ocupa a faixa central-inferior (rows ~5–10),
   grande, pode sangrar levemente nas laterais. NUNCA texto editável — é arte.
4. **Sparkles/ornamentos**: RGBA gerada (estrelas 4 pontas cream, brilhos),
   1–3 pontos discretos em volta do lettering; nunca sobre rostos.
5. **Data pequena** (`ds-eyebrow` static): "09 AGOSTO".
6. **Copy curta** (`ds-body` editável, tone ink, centralizada, rows ~10–11):
   2–3 linhas de homenagem — dentro do compliance, sem promessa.
7. **Rodapé institucional** (row 12): `ds-slot` logo + `ds-body` com
   `data-text-type="phone"` e `data-text-type="instagramHandle"` — compacto,
   branco, discreto.

## Leis do estilo

- Rostos NUNCA cobertos por lettering/overlay denso — a emoção é o scroll-stop.
- Lettering legível contra o gradiente: cream sobre primary escura.
- Máximo 1 palavra-conceito no lettering (a data); a copy curta faz o resto.
- O gradiente cobre no mínimo os 40% inferiores; topo da foto respira sem véu.
- Peça única não tem travessia; se estender a 2–3 slides, manter o mesmo
  gradiente nos internos, com lettering só na capa.
