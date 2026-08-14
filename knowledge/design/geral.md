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

### Cada slide responde ao anterior (a pergunta obrigatória)

Um carrossel é uma coisa só. Compor slide isolado — escolher o tratamento
olhando só o formato daquele conteúdo — produz fita que parece pasta de imagens
soltas, mesmo quando cada slide é bonito.

Antes de compor QUALQUER slide de miolo, responda: **sou continuação do
anterior ou mudança de padrão?** As duas são válidas; o defeito é não decidir.

- **Continuação** — repito a estrutura do vizinho e mudo só o conteúdo (mesmo
  lado da foto, mesma âncora, mesma família de tratamento). Serve para passos
  de uma sequência, itens de uma lista longa, antes/depois. Se for continuação
  de verdade, considere fazer disso um **par**: foto atravessando a emenda pela
  `.fita-layer`, número dando o ritmo, leitura no mesmo lugar.
- **Mudança de padrão** — quebro deliberadamente: fundo inverte, o tratamento
  muda de família (foto → chapado → cartão), a âncora troca de canto. Serve
  para virada de argumento, respiro depois de dois slides densos, entrada do
  fechamento.

**O defeito clássico** (veredito 2026-08-09, clinical): dois slides seguidos com
foto vertical de metade, uma à direita e a seguinte à esquerda. Não é par (as
fotos são diferentes, nada atravessa) nem mudança (é o mesmo tratamento
espelhado). Lê como par espelhado quebrado. Quando duas fotos se encostam na
emenda, ou elas são A MESMA atravessando, ou os tratamentos precisam ser de
famílias diferentes.

Régua rápida na emenda: olhe as duas metades que se tocam. Se forem parecidas
mas não idênticas, está errado — aproxime (vire par) ou afaste (mude o
tratamento).

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

**Duas variáveis, nomeadas pelo papel**: `primary` (a cor principal da marca) e
`accent` (a cor de destaque). O conversor traduz `accent` → `secondary` no JSON,
que é como a plataforma guarda — no HTML você pensa em papel, não em ordem.

Todo elemento colorido leva variável — caixa cheia (tarja, pill de CTA, bloco,
overlay), forma, número gigante, headline e **a palavra destacada do duo-tom**
(que vira `fillVariableConfig` por caractere). Cor cravada sem variável é
defeito: a peça inteira deve se vestir da marca.

Qual das duas usar: `primary` é o corpo da identidade (fundos chapados, a
headline, o CTA principal); `accent` é o realce que pontua (o destaque do
duo-tom, um número, uma tarja secundária). Na dúvida, `primary` — usar `accent`
onde não há hierarquia de destaque só cria uma segunda cor sem motivo.

**Duo-tom = uma cor, dois pesos — as DUAS palavras no accent.** Duas palavras em
cores diferentes tendem a usar `primary` + `secondary`, mas na maioria dos
tenants a secondary é bem diferente e o par sai desconexo. O caminho é a MESMA
variável, com `data-variable-alpha` no span dando o segundo peso (~0.6 quando as
duas palavras são accent).

O erro sutil: deixar a primeira palavra em `ink` e variabilizar só a segunda.
Parece certo enquanto a marca lembra o ink do pack, e desmonta quando não lembra
— verde-escuro + roxo não é duo-tom, são duas cores brigando.

**Teste obrigatório de marca**: renderize com uma cor bem diferente da do pack e
veja se a peça inteira acompanha.

```
node engine/assemble.js <fita.html> <outdir> --primary=#7B3FA0
```

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

## Texto transborda a célula (AGORA o gate pega)

O conversor rejeita texto cujo conteúdo é mais alto que a célula declarada
(filho direto do grid do slide; dentro de cartão/bloco a caixa cresce e não
conta). Antes isso passava batido e só aparecia no render — foi assim que uma
capa saiu com a headline por cima do apoio. Régua para não esbarrar no gate:
headline display (100px+) cabe ~1 linha por linha de grid (112px); com 3 linhas
reserve 4 linhas de grid **e uma de folga** — 4 linhas de display em 4 linhas
de grid não cabe, o arredondamento do line-height estoura. Se o convert
rejeitar, aumente a área ou corte a copy; nunca empurre o texto para caber.

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

## Conteúdo não encosta na borda da caixa que o contém

Texto, número ou chip colado na borda do cartão lê como erro de montagem — a
caixa existe para dar margem, e sem margem ela vira moldura. Num pack com
travessia é pior: a borda geométrica do cartão fica FORA do slide visível, então
"alinhado com a borda" significa **cortado**.

Vale igual entre irmãos: headline e apoio que compartilham uma linha de grid se
tocam; texto e foto vizinhos pedem uma linha inteira de intervalo.

Gate mecânico em `convert.js` (24px mínimo) — foi preciso um humano apontar duas
vezes antes de existir.

## O gate tem que ser testado com uma violação de verdade

Gate que nunca foi visto rejeitando é decoração. Três exemplos só desta sessão:
um usava `doc` em vez de `document` e morria em silêncio; outro ficava DEPOIS
do `return` do bloco de imagens, então nunca via foto alguma; o terceiro
checava "está contido no cartão" e por isso deixava passar justamente o
elemento que TRANSBORDAVA — a violação mais grave era a única que escapava.

Escreva o gate, quebre um exemplar de propósito, veja a rejeição sair com o
`data-el-id` certo, só então conserte o exemplar.

## A caixa não cresce para o conteúdo caber

Cartão que ganha uma linha a mais porque tem foto denuncia a montagem: a régua
muda de slide para slide e a fita perde o ritmo. Quem cede é o conteúdo — foto
menor, copy mais curta, elemento removido —, nunca a caixa.

Corolário: se um registro não cabe na caixa padrão nem cortando conteúdo, ele
não é uma variação daquele pack.

## Imagem em faixa fina é enfeite, não foto

Uma foto que ocupa uma tira estreita do cartão não deixa ler o assunto: o
cartão fica com cara de texto com decoração. Piso de 30% da ÁREA do container —
por área, não por altura, senão a regra serve à foto larga e trai a vertical.

Consequência prática: quando a foto cresce, a copy encurta. A caixa não cresce
junto (ver a lei acima).

## Cada imagem da fita é de um lugar só

Reaproveitar a foto da capa no miolo, ou repetir a mesma entre dois slides,
denuncia a montagem: quem passa o dedo vê a mesma cena de novo e a fita perde a
progressão. Assets de assinatura (SVG do pack) são a exceção — eles existem
para repetir.

Se o tema não rende imagens distintas o bastante, use MENOS slides com foto.
Repetir para preencher é pior do que não ter.

## Cor do CSS não vira variável de marca sozinha

`color: var(--accent)` pinta o elemento no render, mas na conversão vira cor
LITERAL: no editor ele fica fixo enquanto os irmãos acompanham a marca. Quem
gera `fillVariableConfig` é `data-variable`, e só ele.

Regra prática: todo elemento que existe PARA ser o acento (número, marcação,
regra, chip) declara `data-variable`. Se ele deve permanecer claro sobre um
fundo de marca, aí sim é `data-tone` — a distinção é "veste a marca" contra
"contrasta com ela".

## `{conceito}` é o ASSUNTO, não o clima

As fórmulas de imagem dos packs trazem `{conceito}` como placeholder, e todas as
regras ao redor dele são de estilo — luz, textura, ângulo. Sem uma regra sobre o
CONTEÚDO, o preenchimento vira o clima do post ("cuidado", "acolhimento",
"constância") e a foto sai bonita e muda: serve a qualquer tema.

Sintoma de 2026-08-11: quatro packs, mesmo tema (laserterapia em fissura
mamária), quatro capas quase idênticas de almofada + toalha + copo d'água.
Nenhuma mostrava laser, mamilo, atendimento — nem o assunto, nem o recurso.
Uma delas trouxe uma capivara de roupão, clichê do gerador.

**Regra:** `{conceito}` nomeia o objeto ou a cena do tema — o aparelho em uso, a
região tratada em contexto respeitoso, o gesto específico daquele procedimento.
Se a foto serviria para outro assunto sem trocar uma palavra, o conceito estava
vago.

**Teste antes de gerar:** leia o prompt sem o nome do tema. Ainda dá para dizer
do que o post fala? Se não, volte e nomeie o assunto.

**Tema sensível não é exceção, é cuidado de enquadramento.** Amamentação, corpo,
dor íntima: a saída é o entorno específico (aparelho de laser na bancada da
consulta, mão da profissional ajustando o equipamento, a caneta de aplicação),
não a fuga para o genérico.

## Slide de miolo com texto solto no vazio

Um miolo em que o texto flutua num slide grande e nada mais o ancora lê como
rascunho — mesmo quando a copy é suficiente. Medido em 2026-08-11: um slide com
223 caracteres ocupava 24% da área e parecia vazio, enquanto outro com 62
caracteres ocupava 80% e parecia resolvido.

O defeito é de **composição**, não de conteúdo. E a regra antiga ("mínimo 2
elementos com peso") não pega: aquele slide tinha 4.

Piso de **30% da área** com conteúdo, gate no conversor, só para `data-role="item"`
— capa e fechamento têm ritmo próprio (full-bleed, CTA isolado).

Saídas quando o gate acusa: ancorar com foto, caixa ou tarja; aumentar a escala
do texto; ou juntar dois slides magros em um. Encher de texto é a pior delas.

## A imagem mostra o PROBLEMA, não a ferramenta

Corrigir "conceito abstrato" empurrando para "objeto concreto do tema" tem um
efeito colateral: toda foto vira o equipamento. A peça fica sobre o que o
profissional VENDE em vez de sobre o que a pessoa SENTE — e quem rola o feed
não se reconhece num aparelho.

Referência que o Gustavo trouxe (2026-08-12): capa de peça real sobre fissura
mamária mostra a mãe amamentando e o desconforto no corpo. O aparelho aparece
uma vez, pequeno, ao lado. Nossa rodada tinha 5 de 6 imagens de equipamento.

**Regra por funil:**

| Funil | O que a imagem mostra |
|---|---|
| topo / meio | o PROBLEMA e a vida de quem o vive — o gesto de dor, a rotina interrompida, a cena onde o sintoma aparece |
| fundo | aí sim o recurso: o aparelho, o atendimento, o antes de começar |

**Na prática, numa peça de topo/meio:** no máximo UMA imagem de equipamento, e
não na capa. A capa mostra a pessoa ou a situação.

**Como mostrar o problema sem expor ninguém:** o gesto (mão que protege a
região, ombro tenso, postura de quem evita mover), o contexto (a cadeira do
trabalho, a cama de madrugada, a cozinha às três da manhã), o objeto do
cotidiano que denuncia a rotina. Tema sensível se resolve por enquadramento —
recorte, fora de foco, de costas —, não trocando a pessoa por um aparelho.

## "Sem rosto" produz pessoa mutilada

Pedir ao gerador que a pessoa não tenha rosto é pedir um defeito: ele apaga a
cabeça ou corta no lugar errado. Em 2026-08-12 uma capa saiu com a mulher
literalmente sem cabeça — sentada, mão no peito, e nada acima dos ombros.

Se o rosto não deve aparecer, peça um **enquadramento** que naturalmente o
exclua: close nas mãos, pessoa de costas, cortada pela borda do quadro, vista
de cima. O enquadramento é decisão de fotografia; "sem rosto" é uma amputação.

E antes disso, confira se o rosto é mesmo proibido — em saúde,
`compliance/health.md` veda simular paciente ou resultado, não mostrar gente.
Regra herdada sem checar a fonte custou clareza sem comprar segurança.

## Índice repetido entre slides quebra a sequência

Dois slides seguidos com o mesmo "01" fazem o leitor achar que voltou. O número
existe para dizer ONDE ele está: ou numera de verdade (01, 02, 03) ou não
aparece.

Veredito do Gustavo (2026-08-12), sobre uma fita em que os slides 2 e 3 traziam
ambos o índice 01: *"vale tirar do slide 3 e manter só no 2"*.

Quando o miolo mistura registros (um slide de lista, outro de tese), a saída é
numerar só os que formam série — e deixar os demais sem número, em vez de
repetir o último.

## Imagem que atravessa a emenda tem duas exigências próprias

Uma foto na `.fita-layer` que cruza a fronteira entre slides não é uma foto
comum, e falha de dois jeitos que nenhum outro elemento tem:

**Fundo removido.** Ela entra por cima de dois slides que podem ter fundos
diferentes. Com fundo próprio vira um retângulo colado — e o retângulo denuncia
a emenda em vez de escondê-la. PNG com alpha de verdade; JPG nunca. Gate no
conversor lê o colorType do PNG, porque "salvei como PNG" não garante alpha.

**Sujeito no centro, com folga nas laterais.** A emenda corta a imagem ao meio.
Se o assunto encostar numa borda, um dos slides recebe só fundo vazio e a
travessia deixa de existir — o leitor vê duas imagens, não uma contínua.

Teste antes de aceitar a imagem: tape a metade direita — o que sobra ainda diz
alguma coisa? E a metade esquerda? Se uma delas vira vazio, gere de novo.

## Antes de afrouxar um gate, quebre o exemplar que o criou

Um gate reprovou o laserpro por algo que era a assinatura do pack: o aparelho
cruzando o cartão de propósito. A leitura óbvia — "o gate está errado, isento
quem está na `.fita-layer`" — passou nos testes e estava errada. No
`editorial-cards-continuos` o cartão E o conteúdo dele vivem os dois na
`.fita-layer`: aquele filtro desligava dois gates justamente no pack que os fez
nascer, e o render continuava bonito, porque gate desligado não deixa rastro.

O que revelou foi quebrar o exemplar de propósito e ver que o defeito passava.

**A regra:** afrouxar gate exige duas provas, não uma. Que o caso legítimo
passa, e que **a violação original ainda é rejeitada** — colando um elemento na
borda do cartão e conferindo o `data-el-id` na saída. Sem a segunda, "passou"
não distingue gate consertado de gate desligado.

E prefira o critério que descreve a geometria, não a árvore do documento. Aqui
o certo era **contenção** (conteúdo de cartão cabe dentro do cartão; travessia
cruza sem caber), não parentesco — a mesma `.fita-layer` hospeda os dois papéis.

## Escala de texto se mede na referência, não se herda do token

Um pack recriado a partir de referência saiu com "reducionismo desnecessário":
texto pequeno demais, cartão grande e vazio. A causa não foi descuido de
composição — foi ter herdado `fs-body` de outro pack em vez de medir.

O método que resolveu, e que serve para qualquer pack com referência visual:

1. Varra a referência procurando faixas escuras na coluna de texto — cada faixa
   é uma linha de glifos. Anote a altura de cada uma como **porcentagem da
   altura do slide**, não em px: a referência quase nunca está em 1080x1350.
2. Faça o mesmo no render nativo do seu exemplar (o JPG de miniatura do portal
   é 8x menor — medir nele mede o thumbnail, não a peça).
3. O fator entre altura de glifo medida e `fontSize` declarado fica em torno de
   **0,83**. Com ele, `fontSize = (% alvo × altura do slide) / 0,83`.

Na lâmina do laserpro a lista ocupava 2,0–2,8% e a minha 1,6–2,1% — 25% menor,
o suficiente para a peça inteira parecer encolhida sem nenhum elemento estar
obviamente errado.

**E confira o inventário de elementos, não só o tamanho deles.** O mesmo slide
tinha perdido a headline na reescrita. Cartão maior + conteúdo menor + um
elemento a menos é a receita do vazio: nenhuma das três coisas isolada chama
atenção, e juntas a peça fica visivelmente pobre ao lado da referência.

## Recorte incompleto sangra pela borda; não flutua no meio do quadro

Uma foto recortada que mostra um **fragmento** — um antebraço sem o corpo, uma
mão sem o resto do braço — precisa ser cortada pela borda do slide, entrando por
ela. Se ficar com folga transparente em volta, o fragmento vira um adesivo
solto: o olho procura onde o braço termina e encontra ar, o que denuncia o
recorte em vez de escondê-lo.

Na referência do laserpro o antebraço vai até a última linha do slide. O nosso
parava a 11% da base — e os 11% eram exatamente a **margem transparente da
própria imagem**: o gerador centralizou o assunto no quadro, como faz com foto
de objeto.

**Ao gerar recorte de fragmento**, peça o assunto encostando na borda por onde
ele "continua fora da cena", e confira no PNG: as linhas de alpha opaco têm que
ir até a primeira ou a última linha do arquivo, conforme o lado que sangra.
Margem transparente daquele lado é defeito, não folga de segurança.

Isso convive com a regra da travessia (sujeito no terço central **horizontal**,
para a emenda não cortar o assunto): uma coisa é o eixo que a emenda corta, a
outra é o eixo por onde o fragmento sai da cena.

## "O texto parece mais leve" pode ser cor, não peso

Um texto que lê como mais fraco que a referência tem duas causas possíveis, e
elas pedem correções opostas: `font-weight` baixo demais, ou a cor do `ink`
clara demais. Ajustar peso quando o problema é cor engorda a letra sem escurecê-la
— fica pesado e ainda cinza.

O jeito de saber é medir o **pixel mais escuro** do glifo nos dois, referência e
render. O núcleo de uma letra chega à cor cheia; se o seu satura num valor mais
claro, é o token, não o peso.

No laserpro a lâmina dava `(0,0,0)` e o nosso `(47,47,47)` — exatamente
`#2F2F2F`, o valor do token `ink`. Nenhum ajuste de `font-weight` chegaria lá.

Vale também para o inverso: se o pixel mais escuro bate mas o texto ainda parece
diferente, aí sim é peso ou tracking.

## Folga de borda mora no design system, não no HTML do pack

Cartão colado na extremidade do slide precisa de uma nesga de folga — 2.8% (30px
em 1080) na referência do laserpro. A coluna seguinte do grid dá 8.3%, folga
demais, e a whitelist de estilo inline aceita só `grid-area` (e deve mesmo, senão
cada pack inventa o seu CSS).

A saída é um modificador no design system: `data-inset-left` / `data-inset-right`.
Quando um ajuste de espaçamento não cabe na grade, ele vira token compartilhado —
não estilo inline no exemplar.

## A travessia mostra uma PARTE, nunca uma pessoa inteira

A imagem que atravessa a emenda é um elemento gráfico, não uma fotografia de
cena. Pessoa inteira — rosto, tronco, calça, sapato — vira um recorte de banco
de imagens plantado no meio da peça: o leitor lê "foto de stock", não
"continuação do assunto". Numa fita editorial isso quebra o registro inteiro.

**O que pode atravessar:**

- **Uma parte do corpo, ligada ao tema.** A mão, os dedos, o punho, o antebraço,
  o joelho, a perna, a nuca, o ombro. O suficiente para mostrar onde dói, nada
  além disso.
- **Um objeto do tema.** O aparelho, o instrumento, a ferramenta que o negócio
  usa — desde que sozinho, sem cena em volta.

**O que não pode:**

- Pessoa de corpo inteiro, ou qualquer enquadramento que inclua o rosto.
- Duas ou mais pessoas.
- Cena com cenário (mesa, cadeira, consultório ao fundo).

O rosto não é proibido no pack — a foto do profissional é um slot e existe para
isso. O que não pode é ele aparecer na travessia, onde a imagem é textura de
composição.

## Travessia é sempre VERTICAL, e o assunto aponta ao longo dela

O slide é 1080×1350, mais alto que largo, e a travessia ocupa a altura inteira.
Uma imagem em paisagem, deitada nesse espaço, ou fica minúscula ou é cortada
pelas laterais — some justamente a parte que interessa.

- **Formato retrato**, 1024×1536 ou proporção equivalente. Nunca paisagem.
- **O membro acompanha o eixo vertical.** Braço apontando para cima, antebraço
  entrando por baixo, perna de pé. Um braço deitado na horizontal dentro de um
  quadro vertical desperdiça a altura e volta ao mesmo problema.
- **Sujeito no terço central horizontal**: a emenda corta a imagem ao meio, e o
  assunto precisa sobreviver ao corte nos dois lados.
- **Sangra pela borda por onde o fragmento sai da cena** (base, em geral).

Há gate no conversor para o formato e para a sangria. O "é uma parte, não uma
pessoa" ainda depende de olhar — mas o formato retrato já elimina boa parte dos
enquadramentos que trazem a pessoa inteira junto.

## A imagem de travessia é o ponto cego da revisão

Nesta sessão a travessia falhou de quatro jeitos diferentes, e **nenhum** foi
pego por gate ou pelo judge na primeira vez:

| Defeito | Como apareceu |
|---|---|
| JPG sem alpha | retângulo colado sobre a emenda |
| margem transparente na base | o fragmento boiando, faixa de vazio no slide |
| formato paisagem | assunto minúsculo num slide vertical |
| pessoa inteira no lugar de uma parte | recorte de banco de imagens plantado na peça |
| a mesma imagem em duas fitas | prova de variância esvaziada |

Os três primeiros viraram gate. Os dois últimos ainda dependem de olhar — e o
da pessoa inteira só apareceu porque um humano viu a fita renderizada.

**O que aprender daqui:** ao revisar uma fita, a travessia merece uma passada
própria, separada da leitura da composição. Abra o PNG, não só o strip: formato,
canal alpha, o que a imagem mostra, e se ela se repete em outra fita da mesma
leva. O strip esconde os quatro — no thumbnail tudo parece uma foto qualquer no
meio da peça.

**E cuidado com o gate que olha só para dentro.** O gate de imagem repetida
compara as imagens de UMA fita; duas fitas da mesma certificação saíram com o
mesmo arquivo byte a byte e ele não viu. Gate de escopo estreito dá a sensação
de cobertura que não existe.
