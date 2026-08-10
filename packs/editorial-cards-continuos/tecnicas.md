# Técnicas — editorial-cards-continuos

Estilo editorial minimalista: a fita é uma **pilha de cartões sobre fundo
escuro**, e os cartões atravessam as emendas. Arejado por natureza — texto
curto é a assinatura, não limitação.

## Assinaturas (o que faz a peça ser DESTE pack)

1. **Cartões que atravessam a emenda.** Cada cartão ocupa quase todo o seu
   slide e sangra uma faixa estreita para dentro do vizinho à esquerda; entre
   um e outro o fundo escuro aparece como uma barra. Quem passa o dedo vê o
   cartão anterior sair de cena enquanto o próximo já está entrando.
2. **Número em serifa** no topo do cartão, ancorando a sequência (01, 02, 03).
   **Discreto** — na referência ocupa 12% da largura do cartão; número gigante
   descaracteriza o estilo.
3. **Capa com marcação manuscrita**: foto full-bleed escura, serifa em itálico
   misturada a romana, e uma elipse de caneta (SVG) envolvendo a palavra-chave.

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
- **Corpo em 38px**: o texto vive dentro do CARTÃO (990px), não do slide, então
  pede corpo maior do que a intuição sugere.
- Capa: primeira linha em **itálico**, demais em romana.

## Leis do estilo

- **Respiro é o produto**: cartão com texto encostando na borda perde a razão
  de existir. Se o conteúdo não cabe em 3–5 palavras de headline, o pack está
  errado para aquele tema.
- Serifa só na capa e nos números; o corpo dos cartões é sans.
- Fundo escuro nunca recebe texto direto — texto vive dentro de cartão.
- A pill outline do rodapé do cartão é **navegação**, não CTA de ação: seta
  simples. O CTA de verdade só existe no fechamento.
