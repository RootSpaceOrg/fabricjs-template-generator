# Imagens — laserpro-continuo

**Registro:** foto clínica de catálogo médico, luz clara e uniforme, com a
**região do problema sinalizada em vermelho translúcido**. Não é foto de
ambiente nem editorial: é o corpo com o sintoma marcado, do jeito que material
de clínica mostra.

## A foto de travessia (a assinatura do pack)

Uma foto atravessa a emenda entre dois slides. Isso impõe duas exigências que
nenhuma outra imagem do sistema tem:

### 1. Fundo REMOVIDO (PNG com alpha)

A foto entra por cima de dois slides que podem ter fundos diferentes (o miolo é
branco, mas a capa e o fechamento são da cor da marca). Com fundo próprio, ela
vira um retângulo colado — e o retângulo denuncia a emenda em vez de escondê-la.

- Gere em **PNG com fundo transparente** (RGBA), nunca JPG.
- Se o gerador não entregar alpha, remova o fundo antes de usar.
- Confira o alpha: um PNG salvo sem transparência passa despercebido no render
  branco e quebra no primeiro slide colorido.

### 2. O SUJEITO no centro, com folga dos dois lados

A emenda corta a imagem ao meio. Se o assunto estiver encostado numa borda, um
dos slides recebe só fundo vazio — a travessia deixa de existir.

- **Paisagem larga** (>= 1536x1024), sujeito ocupando o terço central.
- Nada essencial nos 15% de cada lateral: é o que a emenda corta.
- Teste antes de aceitar: **tape a metade direita da imagem. O que sobra ainda
  diz alguma coisa?** E a metade esquerda? Se uma das metades vira fundo vazio,
  a imagem não serve para travessia — gere de novo com o sujeito mais ao centro.

| Slot | Fórmula |
|------|---------|
| foto de travessia | "{região do corpo} com {gesto do sintoma}, área afetada destacada em vermelho translúcido, fundo REMOVIDO (transparente), sujeito centralizado com folga nas laterais, foto clínica realista, luz clara uniforme, sem texto" — **PNG paisagem** 1536x1024 |
| foto de faixa | mesma linguagem, sem travessia — pode ter fundo. Usada na tira estreita do miolo |
| aparelho | ver `knowledge/imagem/negocios/laserterapy.md` e a foto de referência ali: portátil sem fio, corpo branco fosco, haste fina com esfera, base de recarga. **Fundo removido** quando for sair por cima do cartão |
| professionalPhoto / logo | slots da plataforma — o usuário preenche. Capa e fechamento levam o profissional; logo só no fechamento |

## O conceito nomeia o assunto

Ver `knowledge/design/geral.md` — o conceito da imagem é o objeto ou gesto DO
TEMA, não o clima do post. E `knowledge/imagem/negocios/<business_type>.md` diz
o que pode e o que não pode aparecer neste negócio.

**Primeiro o problema, depois o aparelho:** em peça de topo/meio, no máximo uma
imagem de equipamento, e nunca na capa.
