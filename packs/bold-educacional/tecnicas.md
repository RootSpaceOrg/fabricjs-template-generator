# Técnicas — bold-educacional

Estilo de TOPO de funil com duas caras que se alternam na mesma fita:
**capa meme scroll-stop** e **slides statement chapados**. A cor saturada
dominante é a PRIMARY do usuário (fundos chapados e tarjas).

## Como este estilo resolve cada formato

O dossiê declara o formato de cada slide e o papel de cada pedaço
(`eyebrow` / `tese` / `apoio` / `itens`); aqui está o tratamento deste pack.
Tese e apoio são **um bloco de leitura** — apoio solto no rodapé é defeito.

| Formato que chega | Tratamento |
|---|---|
| `gancho` | capa meme (abaixo), tese na headline empilhada e apoio na tarja |
| `tese+ressalva` | statement chapado: tese gigante + ressalva no mini-parágrafo |
| `mito-verdade` | par de statements — mito em chapado, verdade no seguinte |
| `enumerado` (2–4) | statement com os itens em lista curta, um por linha |
| `dado` / `citacao` | statement chapado com o número em destaque + fonte no apoio |
| `cta` | fechamento com headline curta + CTA em tarja |

`resolve_mal` (ver `pack.json`): narrativa longa, tabela, passo-a-passo com
muito detalhe por passo.

## Capa meme (scroll-stop)

1. Foto full-bleed INUSITADA (`ds-photo` 1/1/13/13 static+layer): animal com
   adereço humano numa cena absurda-mas-fotográfica (gato de óculos lendo na
   banheira, cachorro de óculos com taça no barco). Gerada por run, ligada ao
   TEMA por um objeto (livro, notebook, jaleco…). Realista, nunca cartoon.
2. Byline no topo centro (`ds-eyebrow` com `data-text-type="instagramHandle"`): a plataforma preenche com o handle do usuário.
3. Headline sans-BOLD branca empilhada (`ds-headline` com `<br>` e
   `data-case="sentence"` — este pack NUNCA usa uppercase em headline, rows
   ~2–5, central): frase de curiosidade, 3 linhas, quebras pensadas.
4. Sub-headline em TARJA (`ds-cta data-square data-variable="primary"` — cantos retos, recolorida pela marca):
   1–2 linhas de promessa concreta, fundo accent (recolorido pela primary).
5. O assunto da foto ocupa o meio-baixo SEM texto por cima.
6. **Contraste da headline segue a parede**: fundo claro da foto → texto ink;
   fundo escuro/saturado → texto paper. Nunca cream sobre parede clara.

## Statement chapado (miolo/tese)

1. Section `data-invert data-variable="primary"` (fundo inteiro na cor do
   usuário).
2. Frase-tese GIGANTE em paper/cream (`ds-headline size="lg"`, rows 4–11,
   esquerda, quebras dramáticas — hifenização manual quando valorizar).
3. Mini-parágrafo de apoio no topo (`ds-body` com `<b>` nos trechos-chave).
4. **Objeto de colagem 3D** (`ds-photo` RGBA static+layer, lado direito,
   pode sangrar pela borda/topo): crachá pendurado com foto, polaroid com
   clipe, etiqueta — sempre com a "foto da pessoa" = professionalPhoto quando
   possível, senão objeto do tema.
   **Sangra para fora da FITA, não na emenda** (veredito 2026-08-09): overhang
   `br`/`tr`/`r` num slide que tem vizinho à direita corta a colagem no meio da
   fita e ela não continua do outro lado. No miolo, prefira `b` (base) ou o
   lado externo; travessia real vai na `.fita-layer`.
5. Handles discretos nos cantos (`ds-body` pequeno, textType instagramHandle).

## Miolo com objeto de conteúdo (fitas longas)

O miolo repete a linguagem da capa em outra chave — nunca vira texto solto no
grid. Tratamentos do pack, para alternar:

- **Cartão-lembrete COMPACTO** (`ds-card data-elevated` sobre a foto): eyebrow
  do tema + frase em sentence case com a palavra-chave em `<b>` + body curto.
  **Tudo alinhado à ESQUERDA** (veredito 2026-08-08): eyebrow, headline e body
  na mesma margem — nada centralizado dentro do cartão.
  REGRA DE OURO (veredito 2026-08-07): **o cartão se ajusta ao texto, o texto
  nunca flutua no cartão** — e "ajustar" inclui CABER: o padding de 40px tem
  que sobrar embaixo. Body de 5+ linhas pede 7 linhas de grid; se o texto
  encosta na base, aumente a área ou corte o texto, nunca deixe justo — dimensione a área pelo conteúdo (tipicamente 4–6
  linhas de grid, ~7–9 colunas), NUNCA um retângulo grande com vazio embaixo.
  Posicione ASSIMÉTRICO (encostado num terço, sangrando ou não), deixando a
  foto respirar em pelo menos 40% do slide — o cartão é um objeto sobre a
  cena, não um painel que cobre o slide. Sem CTA dentro (CTA é ação).
- **Statement chapado** (`data-invert data-variable="primary"`).
- **Citação em caixa** (`ds-card` claro sobre fundo chapado, texto grande).
- **Lista em bloco** (`ds-block` com 2–3 filhos curtos).

**Foto de cena não é decor** (veredito 2026-08-09): asset gerado que não achou
lugar não vira quadradinho no canto. Ou a foto ocupa um terço/metade do slide
carregando conteúdo, ou fica de fora. Quem preenche canto neste pack é a
colagem 3D (RGBA, recortada) — não uma fotografia.

Régua (ver knowledge/design/geral.md): 3 slides = 1 miolo direto · 5 slides =
2+ miolos com objeto de conteúdo · 7+ = 3 tratamentos diferentes e o recurso da
capa repetido 2×.

## Citacao em caixa (miolo)

A fala do paciente vira o objeto do slide: cartao claro sobre o chapado da
primary, com a fala em sentence case e a **resposta profissional logo abaixo,
no mesmo bloco de leitura** — nunca separadas por vao. Numero grande em paper
ancora o rodape; colagem 3D sangra pelo canto oposto.

## Lista em bloco (miolo leve)

2-3 itens de UMA linha num `ds-block` de acento, com eyebrow e tese acima.
E o tratamento mais leve do pack — serve de respiro entre dois slides densos.
Colagem no canto inferior fecha a composicao.

## Numero-dado (miolo)

Quando o conteudo e um numero, o dado E a composicao: `ds-number data-size="lg"`
grande no acento, a leitura do que ele significa colada abaixo (numero e frase
sao UM bloco: "6 a 12" + "sessoes e a faixa mais estudada") e a ressalva em
seguida. Exige colagem de ancora no rodape — so numero e texto deixa vao.

## Leis do estilo

- **Hierarquia de tamanho**: display 72–104px e corpo 40px — o salto máximo é
  ~2,5×. Corpo abaixo de 40px neste pack é defeito (texto de explicação vira
  legenda e quebra a leitura). Eyebrow 26px, tarja 32px.
- **Contraste dentro de caixas**: cartão claro → texto ink/muted; bloco de
  acento → texto paper. Texto claro sobre cartão claro (ou muted sobre acento)
  é defeito — o `data-tone` acompanha o FUNDO DA CAIXA, não o do slide.

- Tipografia é a estrela: máximo 2 pesos (800 display, 500 texto), nunca
  itálico decorativo, quebras de linha SEMPRE intencionais.
- 1 tarja por slide no máximo; tarja nunca com mais de 2 linhas; tarja e
  qualquer caixa cheia SEMPRE com `data-variable="primary"`.
- Meme = absurdo fotográfico com dignidade (luz real, film look) — nunca
  clipart, nunca cartoon, nunca rosto humano deformado.
- Statement nunca divide atenção: ou colagem OU iconografia de margem, não os
  dois grandes. **Vale para watermark também** (veredito 2026-08-09): watermark
  gigante e colagem são âncoras de canto e brigam pelo mesmo papel — uma por
  canto. Watermark que repete palavra já visível no slide é enfeite; ou traz
  palavra nova, ou sai.
- Fita típica: capa meme → 2–4 statements/explicações alternando chapado e
  paper → fechamento com CTA em tarja. Fundos DEVEM alternar (R3 vale aqui).
