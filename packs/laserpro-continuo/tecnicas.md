# Técnicas — laserpro-continuo

Recriação do estilo do LaserPro, a plataforma antiga, no motor de packs. Editorial
clínico: fundo branco, uma cor de marca, elementos que **atravessam as emendas**
e uma palavra do tema em corpo gigante ao fundo. Fala de condição clínica para
quem sente o sintoma — não para quem já decidiu tratar.

As medidas abaixo saíram das seis lâminas originais (`pack-queue/laserpro/`),
não de estimativa. Onde há número, ele foi medido; mudar sem remedir desfaz a
semelhança com a referência.

## Assinaturas (o que faz a peça ser DESTE pack)

1. **Elementos que atravessam a emenda.** Uma foto do problema sai de um slide e
   entra no próximo na mesma altura; o aparelho atravessa o slide de alto a
   baixo com a base caindo no vizinho. Quem passa o dedo vê o mesmo objeto
   continuar — é o que dá o "contínuo" do nome.
2. **Palavra do tema em corpo gigante ao fundo** (`ds-watermark`), a ~7% de
   opacidade sobre o acento e ~9% sobre o branco. Ela **varia** conforme a copy
   do trecho que atravessa: repetir a mesma palavra na fita inteira denuncia o
   template. No fechamento há também uma **vertical** na lateral.
3. **Só a capa é escura.** Fundo de acento, texto claro. Miolo e fechamento são
   brancos — o fechamento leva texto em `accent`, não invertido. Errei isso na
   primeira versão e a lâmina desmentiu.
4. **professionalPhoto na capa e no fechamento; logo SÓ no fechamento.** São os
   dois únicos slots da plataforma no pack.

## As medidas que vieram da referência

| O quê | Medida | Onde |
|---|---|---|
| Cor do texto | preto quase puro (`ink: #111111`) | núcleo do glifo na lâmina dá `(0,0,0)` |
| Corpo de texto | `fs-body: 38px` | linha ocupa 2,0–2,8% da altura do slide |
| Canto do cartão | 30px | curva se afasta ~5px em ~13px de altura |
| Contorno do cartão | linha cinza de 1px (`#B4B4B4`) | é linha, não sombra difusa |
| Folga da borda | 30px = 2,8% (`data-inset-left`) | cartão não brota da extremidade |
| Faixa de foto | colunas 2–11 (9,5% a 84,5%) | **não** sangra: é janela, não full-bleed |

**A cor do texto não é peso.** Se o texto lê como mais leve que a referência,
meça o pixel mais escuro antes de mexer em `font-weight`: com `ink` claro demais
o glifo satura num cinza e nenhum peso o escurece.

**O contorno tem que ser cor opaca.** O conversor passa a cor por `rgb2hex`, que
descarta o alfa — `rgba(0,0,0,.30)` chega ao Fabric como `#000000`, um contorno
preto duro em vez do cinza da lâmina.

## Imagens

Ver `images.md` para as regras de geração. Três coisas que o gate cobra:

- **Travessia é PNG com alpha de verdade.** JPG traz fundo e vira retângulo
  colado sobre a emenda.
- **Recorte de fragmento sangra pela base.** Um antebraço sem o corpo, o aparelho
  apoiado: eles continuam fora da cena, então saem cortados pela borda. Margem
  transparente embaixo faz o fragmento boiar — o gate reprova acima de 3%.
- **Sujeito no terço central horizontal.** A emenda corta a imagem ao meio; se o
  assunto encostar numa lateral, um dos slides recebe só vazio.

O aparelho de fotobiomodulação tem forma específica (portátil sem fio, corpo
branco curvo, haste com esfera, base em pedestal). Ver
`knowledge/imagem/negocios/laserterapy.md` — "caneta com cabo" é o aparelho
errado, e já foi gerado assim duas vezes.

## Padrões de composição (os exemplares)

A fita real **mistura** os registros. Cada exemplar em `exemplos/` é um padrão;
o portal os exibe como referência de montagem.

### ref-estrutura
A fita completa de 6 slides, na ordem das lâminas: capa → o que é → benefícios →
cartão com aparelho → faixa de foto → fechamento. Serve como mapa do pack
inteiro, não como padrão isolado.

### ref-sintomas-travessia
Sintomas em lista com a foto do problema cruzando a emenda. O registro mais
frequente — a condição se explica pelo que a pessoa **sente**, não pelo que o
aparelho faz. O texto ocupa o lado oposto da foto em cada slide.

### ref-beneficios-cartao
Benefícios na caixa branca, com o aparelho passando **por cima** dela. Sintoma
pede foto do corpo; benefício pede a caixa. O cartão leva `data-shadow-soft`, e
**não** `data-elevated`: elevated cria `z-index: 2` e o aparelho passaria por
trás, invertendo a assinatura.

### ref-faixa-de-foto
Faixa no topo, tese curta e apoio abaixo. O slide de respiro, quando a fita já
explicou a condição e precisa de pausa antes do fechamento. A faixa tem margem
dos dois lados — não sangra.

### ref-capa-e-fechamento
Os dois slides com `professionalPhoto`, lado a lado, para ver o contraste: capa
de acento com pílula "arrasta pro lado", fechamento branco com logo e instrução
de comentário.

**Cuidado com o slot do profissional:** ele ocupa da coluna 7 à 13. Texto que
avança além da coluna 7 passa por trás da pessoa e some.

## O que este pack resolve mal

- **Passo a passo longo.** Não há numeração de série; a fita não sinaliza ordem.
- **Tabela e comparação lado a lado.** O grid é de coluna única por slide.
- **Peça única.** As assinaturas dependem da emenda: um slide sozinho perde as
  travessias, que são metade do estilo.
