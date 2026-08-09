# Design — conhecimento geral (vale para QUALQUER pack)

Camadas de conhecimento do designer, da base para o topo (o mais específico
vence): **este arquivo** → `packs/<slug>/` (tecnicas.md, exemplos/, tokens,
lessons.md) → dossiê da run. O que é lei mecânica está no CATALOG e nos gates;
aqui estão as leis de gosto que valem em todo estilo.

`esqueletos/` ao lado deste arquivo é **catálogo de estudo para quem cria pack**
(`PACKS.md` §3) — composições que já funcionaram, com as cores de um pack
específico apenas porque nasceram lá. Não é biblioteca de layout para produção:
em run, o tratamento vem do `tecnicas.md` do pack em uso.

## Legibilidade (inegociável)

- Texto NUNCA sob decor, foto ou travessia — texto vive em background limpo.
- CTA, logo e foto de perfil sempre desobstruídos.
- Contraste de leitura em todo texto (o judge elimina por contraste, R6).
- Texto de leitura nunca cortado por fronteira de slide ou pelo canvas (R2);
  atravessar fronteira é privilégio de decoração/imagem/watermark.

## Hierarquia e respiro

- 1 elemento dominante por slide (headline OU foto OU número — não empate).
- Respiro deliberado pontua; slide >35% de área morta é defeito (R4) — a
  diferença entre respiro e área morta é intenção: o vazio aponta para o foco.
- Grid de 12: margens generosas (1 coluna nas laterais no mínimo), alinhamentos
  consistentes dentro do slide.

## Fita (a unidade de design)

- A fita é UMA peça: leitura contínua, fundos alternando (R3: mínimo 2 mudanças
  de fundo na fita), transições intencionais nas fronteiras.
- Elementos de travessia (fita-layer) criam continuidade: foto sobre a emenda
  de dois slides, decor cruzando, watermark varrendo. Sempre estáticos, sempre
  sobre backgrounds limpos dos DOIS lados.
- Variância é dever: duas gerações do mesmo pack nunca saem com o mesmo
  esqueleto — varie ordem, lados, quantidade de slides, presença de decors.

## Fotos e decors

- Foto editável vive inteira dentro de um slide; foto de continuidade
  (travessia) é estática e paisagem, com o sujeito perto da emenda.
- Decor = objeto do TEMA do post, gerado por post (nunca banco/estoque),
  fundo transparente, desfoque profundo NASCIDO NA GERAÇÃO (pós-processo de
  blur é proibido), inteiro no arquivo com margem nas 4 bordas.
- Decor se posiciona grande, cortado por uma borda do slide (ou da fita),
  com leve rotação — nunca pequeno e solto no meio do canvas.

## Slots da plataforma

- `professionalPhoto` usa o placeholder canônico do motor (o runtime troca pela
  foto real); pessoa/avatar desenhado no lugar é violação (R1).
- Elementos editáveis respeitam min/max de caracteres e fazem sentido para
  OUTRO profissional do mesmo nicho adaptar no editor.

## Cor da marca em caixas

Todo elemento em cor de acento leva `data-variable="primary"` — caixa cheia
(tarja, pill de CTA, bloco, overlay), forma, número gigante, **e a palavra
destacada do duo-tom** (`<span data-tone="accent" data-variable="primary">`, que
vira `fillVariableConfig` por caractere). Acento cravado sem variável é defeito:
a peça inteira deve se vestir da primary.

**Duo-tom = uma cor, dois pesos.** Duas palavras em cores diferentes tendem a
usar `primary` + `secondary`, mas na maioria dos tenants a secondary é uma cor
bem diferente — o par sai desconexo. O caminho é a MESMA variável com
`data-variable-alpha` no span (0.85 mantém presença; abaixo de 0.7 a segunda
palavra perde peso contra o papel). Assim as duas palavras acompanham a marca.

**O que NÃO se variabiliza**: `ink`, `paper`, `muted` e `wm` são a paleta
estrutural do estilo (o papel menta do clinical, o cream do bold). Se
recolorissem, o pack perderia identidade e viraria "qualquer pack na cor do
cliente" — o que se veste da marca é o ACENTO, não o fundo do estilo.

## Miolo não é versão pobre da capa

Fita longa (5+ slides) tende a virar "capa caprichada + miolos de texto solto"
— defeito. O miolo REPETE A LINGUAGEM da capa em outra chave: os mesmos
recursos visuais (caixas, cartões, tarjas, colagens, sobreposição) reaparecem
carregando o conteúdo, variando qual deles domina cada slide.

Régua prática por tamanho de fita:
- **3 slides**: capa + 1 miolo + fechamento — o miolo pode ser mais direto.
- **5 slides**: pelo menos 2 miolos com "objeto de conteúdo" (cartão/caixa/
  destaque), nunca 3 slides seguidos só com texto no grid nu.
- **7+ slides**: alterne no mínimo 3 tratamentos diferentes ao longo do miolo
  (ex.: cartão empilhado → statement chapado → citação em caixa → lista em
  bloco), e repita o recurso-assinatura da capa pelo menos 2 vezes.

## Hierarquia de corpo vs display

O corpo de texto acompanha a escala do display: salto maior que ~2,5× entre
headline e body faz a explicação parecer legenda. Se a headline é 100px, o
corpo vive em 36–44px. Vale dentro de cartões e blocos também — texto em caixa
segue a mesma régua, não encolhe por estar "dentro de algo".

## CTA é ação, não enfeite

Pill/tarja de CTA só existe onde há ação real do leitor: capa (arrasta),
fechamento (salvar, comentar, compartilhar). Cartão de miolo com "botão" que
não leva a nada vira UI decorativa (o judge reprova em R5) e rouba autoridade
da peça. Rótulo de seção dentro de cartão = eyebrow/stamp.

## Caixa se ajusta ao conteúdo

Cartão/bloco de texto tem a altura do que carrega — nem sobrando (vazio
interno) nem faltando (texto encostando na borda). O padding do container é
inegociável nos QUATRO lados: se o conteúdo o consome, a caixa cresce. Caixa grande com texto no
topo e vazio embaixo é defeito (o vazio dentro de uma borda lê como erro, não
como respiro). Se sobra espaço: encolha a caixa, não espalhe o texto. Respiro
pertence ao slide (em volta da caixa), não ao interior dela.

## Texto transborda a célula (o gate não pega)

O conversor só rejeita sobreposição de ÁREAS declaradas — texto que estoura a
própria célula e invade a vizinha passa batido e só aparece no render. Régua:
headline display (100px+) cabe ~1 linha por linha de grid (112px); com 3 linhas
reserve 4 linhas de grid. Se o texto encavalar no render, aumente a área ou
corte a copy — nunca confie no gate para isso.

## Formato de copy pede tratamento visual

O framework escolhido (`knowledge/copy/frameworks.md`) tem consequência de
design — o designer lê o dossiê e responde a ele:

- **Listicle / passo-a-passo**: hierarquia visual IGUAL entre os itens (o
  leitor compara); numeração consistente.
- **Mito × verdade / erro → correção**: pares precisam de marcação simétrica
  (badge, cor, posição) — é o ritmo de revelação que segura o swipe.
- **Cheat-sheet**: densidade alta é o produto, mas exige hierarquia forte
  (agrupamento, pesos, respiro) para não virar muralha ilegível.
- **Antes/depois**: comparação lado a lado é lida instantaneamente — evite
  separar em slides distantes.
- **Case-study / vulnerável**: a peça pede foto/atmosfera, não infográfico.

## Alinhamento dentro de caixas

Cartão/bloco tem coluna de leitura própria: eyebrow, headline e corpo começam
na MESMA margem esquerda. Centralizar texto dentro de caixa quebra a coluna e
faz o olho procurar o início de cada linha. Centralização é recurso de slide
inteiro (capa, fechamento), não de conteúdo dentro de container.

## Slide vazio é defeito (não é minimalismo)

Headline no topo + uma linha de apoio + 60% de fundo liso não é respiro: é
slide inacabado. Todo slide precisa de PELO MENOS DOIS elementos com peso —
headline + (foto | cartão | bloco | colagem | número gigante | lista). Se o
conteúdo daquele slide não sustenta dois elementos, ele não deveria existir:
funda com o vizinho e faça uma fita mais curta.

Fita longa com slides vazios é pior que fita curta densa. Antes de pedir 7
slides, confira se há conteúdo para 7.

## Avatar ilustrado nunca substitui o slot da plataforma

Pessoa "genérica" gerada por IA (3D, cartoon, render) no lugar de
`professionalPhoto` é violação R1 do judge: o runtime troca o slot pela foto
real do usuário, então a peça precisa usar o placeholder canônico do motor
(engine/assets/professional-photo-*.b64.txt). Ilustração de pessoa só entra se
o pack pedir explicitamente como elemento decorativo — nunca como o profissional.

## A célula do grid é espaço máximo, não altura

`grid-area` reserva a área; ele NÃO é a forma da caixa. Cartão com três linhas
numa célula de meia altura vira 60% de vão — o defeito mais recorrente do
miolo. Use `data-fit="start|end"` em `ds-card`/`ds-block` sempre que o texto for
curto para a área: a caixa encolhe até o conteúdo e ancora onde você escolher
(`end` = encostada no rodapé da célula).

Corolário: quando a composição INTEIRA é feita de caixas, `data-fit` sozinho
não salva — encolher as duas abre buraco entre elas. Aí o conserto é
aproximá-las no grid, não deixá-las esticadas.

## Elemento da .fita-layer só ocupa coluna sem texto

A camada de travessia pinta POR CIMA de todos os slides que cruza. Foto que
atravessa a emenda precisa ficar nas colunas onde nenhum dos dois vizinhos tem
texto de leitura — caso contrário cobre a headline do slide anterior ou do
seguinte. Na prática: a leitura vai para as bordas externas do par e a imagem
fica no miolo da emenda.

## SVG é geometria, nunca imagem

Forma que o CSS não expressa (arco parcial, curva que entra e sai do quadro,
moldura de recorte irregular) vai num arquivo `.svg` carregado por
`<img class="ds-photo">` — ver a regra completa no CATALOG. É o que permite a
"profundidade de papel" de fundos com arcos finos.

O que NÃO pode virar SVG: ilustração, figura, ícone desenhado, textura, cena.
Já houve problema com imagem em SVG na plataforma — imagem é PNG/JPG gerado.
Régua: se o arquivo tem mais que formas simples com traço/preenchimento
chapado, é imagem no lugar errado.

Arcos e formas de fundo trabalham **em oposição** (um no canto superior de um
lado, outro no inferior do lado oposto): dois no mesmo quadrante embaralham a
leitura em vez de dar profundidade.

## Overhang sangra para fora da fita, não na emenda

`data-overhang` empurra a imagem para fora do SLIDE e a borda corta. No primeiro
e no último slide isso sangra para fora da peça — efeito desejado. **No miolo, o
lado que encosta no vizinho vira imagem decepada**: o leitor vê metade de uma
polaroid no fim de um slide e nada no começo do próximo.

Régua: overhang para a borda EXTERNA da fita (esquerda no primeiro slide,
direita no último) ou para topo/base em qualquer um. Para atravessar a emenda de
verdade, o elemento vai na `.fita-layer` — é o único jeito de continuar do
outro lado.

## Foto não é decor de canto

Imagem sem função narrativa encaixada num canto porque "sobrou espaço" é
defeito, mesmo sendo uma foto boa. Decor tem regra (objeto do tema, transparente,
desfocado, grande, cortado pela borda); foto de cena **não é decor** — ela ocupa
um terço/metade do slide e carrega conteúdo, ou não entra.

Sintoma típico: asset gerado que não achou lugar e foi parar num quadrado de 3×3
células no canto inferior. Se a foto não tem papel no slide, o slide não precisa
dela — e se o slide ficou vazio sem ela, o problema é a copy, não a imagem.

## Cutout ancora na base DA ÁREA

`data-cutout` alinha a figura na base da célula do grid, não na do slide. Área
que termina na linha 11 ou 12 deixa a pessoa flutuando com um vão embaixo. Para
o profissional "pisar" no rodapé, a área precisa ir até a linha 13.

## Duas camadas não disputam o mesmo canto

O gate de sobreposição libera `data-layer` sobrepor qualquer coisa — inclusive
outra camada. Isso é necessário (texto sobre véu sobre foto), mas abre espaço
para watermark e colagem caírem no mesmo canto, um cortando o outro.

Camada ainda tem lugar: watermark gigante e colagem/decor são âncoras de canto
e **brigam pelo mesmo papel**. Escolha uma por canto — e se a fita já tem a
colagem como assinatura, o watermark provavelmente não é necessário.

Watermark que repete uma palavra já visível no slide é enfeite, não camada de
profundidade: ou traz uma palavra nova (o número da etapa, o conceito), ou sai.

## Repetir o mesmo elemento no mesmo canto é falta de variância

Variância não é só entre fitas — é dentro da fita. Dois slides seguidos com o
mesmo recurso (mesmo watermark, mesmo símbolo, mesma colagem) na mesma posição
lê como template repetido, mesmo quando o texto muda. Se o recurso volta, muda
de canto, de escala ou de papel.
