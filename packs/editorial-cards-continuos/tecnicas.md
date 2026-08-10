# Técnicas — editorial-cards-continuos

Estilo editorial minimalista: a fita é uma **pilha de cartões sobre fundo
escuro**, e os cartões atravessam as emendas. Arejado por natureza — texto
curto é a assinatura, não limitação.

## Assinaturas (o que faz a peça ser DESTE pack)

1. **Cartões que atravessam a emenda.** Cada cartão ocupa quase todo o seu
   slide e sangra uma faixa estreita para dentro do vizinho à esquerda; entre
   um e outro o fundo escuro aparece como uma barra. Quem passa o dedo vê o
   cartão anterior sair de cena enquanto o próximo já está entrando.
2. **Número em serifa no canto superior DIREITO** do cartão, ancorando a
   sequência (01, 02, 03). **Discreto** — na referência ocupa 12% da largura;
   número gigante descaracteriza o estilo. Leva `data-align="right"` e
   `data-inset="top"` (o inset é o respiro do topo — sem ele o número gruda
   na borda). **O número ocupa uma faixa só dele**: se a headline dividir a
   linha com ele, as duas colidem — é o erro mais fácil de cometer aqui.
3. **Capa com marcação manuscrita**: foto full-bleed escura, serifa em itálico
   misturada a romana, e uma elipse de caneta (SVG) envolvendo a palavra-chave.

## Variações de miolo (os exemplares)

O pack tem três exemplares e a fita real **mistura** os registros — repetir o
mesmo cartão N vezes é a falha mais comum:

| Exemplar | Quando usar |
|---|---|
| `ref-estrutura-cartoes.html` | o padrão: cartão só texto. É a maioria da fita |
| `ref-miolo-cartao-com-foto.html` | item que pede prova visual (o aparelho, o detalhe, o antes/depois). Foto no TOPO do cartão, com `data-round` para casar com o raio dele; o texto fica na metade de baixo |
| `ref-miolo-foto-de-palco.html` | respiro no meio da fita: em vez do fundo escuro chapado, o slide é uma foto escura e o cartão pousa sobre ela. A cada 3–4 cartões, nunca dois seguidos |

Nas duas variações com foto o cartão é **mais alto** (linhas 2–13 em vez de
2–12) ou **mais curto** (3–11 sobre palco), mas a travessia e o gap não mudam:
a largura em colunas e o `data-half-left` são os mesmos.

**Foto de palco tem que ser escura e calma.** Ela é fundo; o cartão claro por
cima é que carrega a leitura. Foto clara ali apaga o cartão.

## Estrutura cartões (o exemplar de referência)

`exemplos/ref-estrutura-cartoes.html` é a fita de 5 slides que demonstra o pack
inteiro: capa com marcação, três cartões atravessando as emendas sobre o palco
escuro (o do meio vestindo a marca) e o cartão de fechamento que não sangra.
Renderize com `node engine/tools/build-exemplos.js editorial-cards-continuos`.

## Como a travessia funciona (o que mais erra)

Os cartões vivem na `.fita-layer`, não dentro das sections — é o único jeito de
um elemento continuar no slide seguinte. Grid contínuo: **12 colunas por
slide**, então numa fita de 5 as colunas vão de 1 a 60.

A camada leva `data-split-ok`: por padrão travessia não pode ser editável
(o conversor a duplica nos vizinhos, e dois campos dessincronizam no editor).
Neste pack o conteúdo É a travessia, e quem edita é o time de design — o
atributo declara que as duas metades são aceitáveis.

Regra prática, para uma fita de N slides com cartões do slide 2 ao N-1:

```
cartão do slide K:  grid-area: 2 / (12·(K-1) − 1) / 12 / (12·K + 1)
```

Os cartões levam `data-half-left`: mesma largura em colunas, deslizados meia
coluna (45px) para a esquerda. Gap e sangria disputam a mesma sobra — em passo
de 12 colunas, gap + sangria = largura − 12, então qualquer largura INTEIRA zera
um dos dois. A meia coluna é o que a referência faz e o que resolve.

Ou seja: começa **1 coluna antes** da fronteira do próprio slide e termina
**1 coluna depois** — é essa sobra que cria a sangria. O texto do cartão vai
DENTRO dele (filhos do `ds-card`), então acompanha.

**O último cartão (CTA) não sangra**: ele fecha a fita, então fica inteiro
dentro do próprio slide. É a parada do padrão.

**Consequência prática:** as sections de miolo ficam **vazias** (só o fundo
escuro) e todo o conteúdo — cartão, número, headline, apoio — vive na camada.
A camada pinta por cima dos slides, então texto na section sumiria por baixo
dos cartões.

## Como este estilo resolve cada formato

| Formato que chega | Tratamento |
|---|---|
| `gancho` (capa) | foto full-bleed escura + tese em serifa (itálico na 1ª linha, romana nas demais) + marcação em elipse na palavra-chave + assinatura pequena no rodapé |
| `enumerado` / `principios` | um cartão por item: número em serifa, headline de 3–5 palavras, apoio de 2–3 linhas. É o uso natural do pack |
| `tese+ressalva` | cartão com a tese grande e a ressalva no apoio, mesmo bloco |
| `manifesto` | cartões alternando creme, acento e branco, cada um com uma afirmação |
| `cta` (fechamento) | cartão branco INTEIRO no slide (sem sangrar), tese curta + 2 ações em pill outline + site |

`resolve_mal` (ver `pack.json`): passo-a-passo detalhado, dado com muitos
números, narrativa longa, tabela. O cartão comporta pouco texto — conteúdo
denso quebra o respiro que é a assinatura.

## Alternância de cor dos cartões

A sequência típica é **creme → acento → branco → creme**, com o cartão de
acento carregando `data-variable="primary"` (é ele que veste a marca). Um
cartão de acento por fita curta; em fita de 6–7 slides, dois, nunca vizinhos.

O fundo entre os cartões é escuro por padrão (`ink`), **mas o designer decide
a partir da foto da capa**: se a imagem for clara ou de temperatura quente,
puxe o fundo para o tom escuro daquela cena em vez do preto neutro — a fita
inteira fica coerente com a capa. Amostre a cor dominante da foto e escureça.

## Marcação manuscrita da capa

`assets/marcacao-elipse.svg` — copie para a run
(`cp packs/editorial-cards-continuos/assets/marcacao-elipse.svg artifacts/runs/<slug>/assets/`)
e posicione sobre as 2–3 palavras que a copy destaca, com `data-layer` e
`data-variable="primary"`.

O SVG é elipse com traço aberto, deliberadamente irregular. Se o profissional
editar o texto na plataforma, ele redimensiona a marcação no editor — não
tente fazê-la "seguir" o texto.

**Uma marcação por fita, só na capa.** Repetir mata o gesto.

## Tipografia (medida na referência, não estimada)

- **Sans (Inter)** na headline e no CTA: terminais horizontais, R de perna reta.
  Ampliar as letras da referência antes de escolher a fonte evita trocar por
  "parecida" — Archivo passa de longe, mas tem terminais oblíquos.
- **Headline em peso 500**, não 700: ela pesa pela ESCALA (78px), não pelo traço.
  Ocupa ~68% da largura do cartão em 2–3 linhas.
- **Serifa (Playfair Display)** no apoio, no número e na capa: didone, contraste
  alto, serifas finas e retas. Em **peso 500** — a serifa fina some no cartão.
- **Corpo em 38px, peso 400**: o texto vive dentro do CARTÃO (990px), não do slide, então
  pede corpo maior do que a intuição sugere.
- Capa: primeira linha em **itálico**, demais em romana.

## A borda de leitura ≠ a borda do cartão

O cartão sangra 1 coluna além da emenda, então sua borda direita geométrica
está **fora** do slide visível. Texto e número alinhados por ela saem cortados.
A margem de leitura é a borda do cartão **menos a sangria**: para um cartão que
começa em `ini`, o conteúdo vai no máximo até `ini + 8`.

## Leis do estilo

- **Respiro é o produto**: cartão com texto encostando na borda perde a razão
  de existir. Se o conteúdo não cabe em 3–5 palavras de headline, o pack está
  errado para aquele tema.
- Serifa só na capa e nos números; o corpo dos cartões é sans.
- Fundo escuro nunca recebe texto direto — texto vive dentro de cartão.
- A pill outline do rodapé do cartão é **navegação**, não CTA de ação: seta
  simples. O CTA de verdade só existe no fechamento.
