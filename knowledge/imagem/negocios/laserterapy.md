---
business_type: laserterapy
updated: 2026-08-11
---

# Imagem — laserterapia (fotobiomodulação clínica)

O que pode e o que não pode APARECER numa foto deste negócio. O estilo continua
sendo do pack; isto aqui é o assunto.

## O aparelho certo

**Referência fotográfica: `referencias/laserterapy-aparelho.png`** — olhe antes
de escrever prompt de aparelho. O que estava descrito aqui ("caneta ligada por
cabo a uma unidade de mesa") era deducao minha e estava ERRADO.

O aparelho de fotobiomodulacao clinica e:

- **Portatil sem fio, formato de pistola curva**, corpo branco fosco.
- **Base de recarga** propria, em forma de pedestal — o aparelho fica de pe nela.
- **Haste metalica fina** saindo da ponta, com esfera na extremidade: e ela que
  toca a regiao. NAO e uma caneta reta com cabo.
- **Display digital pequeno** no corpo, marcando o tempo/dose, com seletor
  R / IR (vermelho e infravermelho).
- **Óculos de proteção** aparecem na cena de aplicação real e dão veracidade.
- **Cluster / matriz de LEDs** e **ILIB** (emissor no punho) existem, mas sao
  outros formatos do mesmo negocio — nao o padrao.

Para o prompt: `handheld cordless photobiomodulation device, white matte curved
body, thin metal probe with rounded tip, small digital display, charging
stand`. Nao use `laser pen with cable` — foi o que gerou o aparelho errado.

## O aparelho ERRADO (reprova a imagem)

- **Laser de depilação** — cabeçote grande, tela colorida, carrinho volumoso.
  Depilação é OUTRO business_type (ver `knowledge/copy/negocios/laserterapia.md`);
  a foto errada arrasta a peça para o negócio errado.
- **Laser cirúrgico/ablativo**, braço articulado, ambiente de centro cirúrgico.
  PBM não é ablativa.
- **Cabine de bronzeamento ou câmara de luz** de corpo inteiro.
- **Feixe verde ou azul dramático cortando a sala** — a luz de PBM é vermelha
  ou infravermelha (esta última é INVISÍVEL; o que se vê é a luz-piloto).
- Ficção de laser: raio contínuo visível no ar, faísca, efeito sci-fi.

## Primeiro o problema, depois o aparelho

Ver `knowledge/design/geral.md` — a imagem mostra o que a pessoa SENTE, não o
que o profissional usa. Numa peça de topo/meio: **no máximo uma imagem de
equipamento, e nunca na capa**.

Para este negócio, o problema aparece assim:

| Tema | O que mostrar (problema) |
|---|---|
| fissura mamária | mãe amamentando com desconforto visível na postura, mão no seio, ombro tenso; a cena da madrugada |
| dor lombar no trabalho | a pessoa se apoiando na mesa, mão nas costas ao levantar da cadeira |
| dor no joelho | mão apoiada no joelho ao descer escada, tênis parado no meio do lance |
| cicatrização | curativo no cotidiano, a rotina que continua apesar da lesão |
| mucosite | dificuldade com o alimento, copo afastado, refeição intocada |

## Enquadramentos que dizem o assunto

| Situação | O que mostrar |
|---|---|
| aplicação em curso | mão da profissional posicionando a ponteira sobre a região, luz vermelha refletindo na pele |
| preparo | ponteira, óculos de proteção e gaze sobre a bancada, unidade ao fundo com display aceso |
| parâmetro / dose | close do display com números, dedo ajustando — serve a qualquer post sobre protocolo |
| consulta | avaliação da região antes da aplicação, prancheta, conversa entre profissional e paciente |
| pós | região coberta por curativo/compressa, aparelho já recolhido |

## Temas sensíveis: o entorno, nunca a fuga

Fissura mamária, cicatriz íntima, mucosite, lesão genital — o assunto exige
respeito, e a saída **não** é a foto genérica de aconchego.

Mostre o **entorno específico do atendimento**: a caneta de aplicação na
bancada, a mão ajustando o equipamento, os óculos de proteção, o display com o
parâmetro. A cena diz "atendimento com laser" sem expor ninguém.

O que reprova nesses temas: almofada de amamentação sozinha, toalha dobrada,
copo d'água, velas, pedras, chá, bicho de pelúcia ou animal antropomorfizado.
São cenas de bem-estar que serviriam a qualquer post — e o post vira mudo.

## Pessoas

**Rosto é permitido** — ver `compliance/health.md`. O que se evita é a imagem
passar por paciente real ou por resultado, não a presença de gente.

- **Quem vive o problema**: rosto e expressão coerentes com o incômodo. É o
  que faz a leitora se reconhecer. Nada de alívio ou satisfação, que leem como
  depoimento de resultado.
- **Profissional em atendimento**: rosto ok; jaleco e luva quando a cena pedir.
- **Região sensível** (mama, região íntima): aí sim o enquadramento protege —
  recorte, de costas, coberto. Isso é sobre a REGIÃO, não sobre o rosto.

Nunca peça "sem rosto" ao gerador: ele responde apagando ou cortando a cabeça,
e a pessoa sai mutilada. Se o rosto não deve aparecer, escolha um ENQUADRAMENTO
que naturalmente o exclua (close nas mãos, de costas, cortado pela borda).

## Vocabulário para o prompt

`low level laser therapy device`, `photobiomodulation handpiece`,
`therapeutic laser pen with cable`, `red light therapy LED cluster`,
`clinical laser unit with parameter display`, `laser safety goggles`.

Evitar no prompt: `laser hair removal`, `surgical laser`, `IPL`,
`beauty machine`, `spa`, `wellness retreat`.
