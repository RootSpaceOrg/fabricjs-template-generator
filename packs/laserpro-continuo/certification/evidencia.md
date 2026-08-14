# Certificação — laserpro-continuo v1

Data: 2026-08-14 · Protocolo: PACKS.md §4 · Ambiente: dev
**Aprovado pelo Gustavo em 2026-08-14.** Commit do pack: `482f459`

O pack recria o estilo do LaserPro — a plataforma antiga — no motor novo. As
medidas do `tecnicas.md` saíram das seis lâminas originais em
`pack-queue/laserpro/`, não de estimativa.

## As 3 fitas da prova

| Run | Slides | Tema | Gates | Judge | Fidelidade |
|-----|--------|------|-------|-------|------------|
| cert-lp-v1-carpo-4 | 4 | túnel do carpo | passa | QA: PASS | FIEL |
| cert-lp-v1-carpo-5 | 5 | túnel do carpo | passa | QA: PASS | FIEL |
| cert-lp-v1-lombar-7 | 7 | dor lombar crônica | passa | QA: PASS | FIEL |

As duas primeiras são do MESMO tema (prova de variância) e saíram com esqueletos
diferentes: a de 4 abre pelo sintoma, a de 5 pelo despertar noturno. A de 7 é
tema diferente e prova o fôlego em fita longa — não cai em texto solto, alterna
destaque na cor, cartão vestido e o aparelho atravessando.

## Desvio do protocolo, declarado

O §4 pede fitas de **3, 5 e 7** slides. O `pack.json` declara `slides: min 4` —
a de 3 não cabe no próprio pack. Usei **4, 5 e 7**, que é o intervalo real e
mantém o que a regra quer provar: tamanho variado e fôlego em fita longa.

## O que esta certificação prova

- **Fidelidade ao estilo antigo**: elementos atravessando as emendas, palavra do
  tema em corpo gigante ao fundo, só a capa escura, professionalPhoto na capa e
  no fechamento com logo só no fechamento.
- **Adaptabilidade**: os 7 padrões de composição foram renderizados em quatro
  marcas (verde, roxo, azul, vinho) — a estrutura não muda, só a cor.
- **Sete padrões de composição** cobrindo os registros que o `pack.json` promete:
  sintomas com travessia, benefícios em cartão, faixa de foto, capa e fechamento,
  destaque na marca, cartão na marca, e a fita completa como mapa.

## Os gates que este pack fez nascer

| Gate | O defeito que o originou |
|---|---|
| travessia é PNG com alpha | JPG virava retângulo colado sobre a emenda |
| recorte sangra pela base | 11–13% de margem transparente fazia o fragmento boiar |
| travessia é retrato | 1536×1024 num slide vertical: o assunto sai minúsculo |
| decor não conta como foto repetida | `data-overhang` é adorno, e reprovava exemplar certificado |
| travessia não é conteúdo de cartão | o aparelho cruza o cartão por desenho, não por erro |

## Defeitos que o judge não pegou (e como apareceram)

Os três passaram por `QA: PASS`.

**Pessoa inteira na travessia.** Uma mulher de rosto, camiseta e jeans plantada
no meio da peça. O Gustavo apontou: *"vale ser somente partes… nunca uma pessoa
completa jogada"*. Virou regra no `geral.md` e no `images.md`, e o formato
retrato virou gate — que achou de imediato a travessia do
`clinical-photo-editorial`, pack **certificado**, com o mesmo defeito.

**A mesma imagem em duas fitas.** As travessias das fitas de 4 e 5 eram o mesmo
arquivo byte a byte (conferido por md5), o que esvaziava a prova de variância. A
de 5 recebeu uma imagem distinta. Expôs que o gate de imagem repetida olha
**dentro** de uma fita, não entre fitas da mesma leva.

**Foto lavada dentro do fundo escuro.** A fita de 4 tinha dois slides de acento
e a travessia cruzava para dentro do escuro: saturação 0,165 contra 0,368 nas
duas metades. A imagem de origem era uniforme (0,314 × 0,303), então era
composição, não geração. Corrigido para 0,225 nos dois lados.

## Ressalva registrada

O pack tem sete padrões, mas as três fitas exercitaram principalmente os de
texto e travessia. **Destaque na marca** e **cartão na marca** aparecem só na
fita de 7; os outros dois registros seguem verificados pelos exemplares, não por
fita de ponta a ponta. Foi apresentado ao Gustavo antes da aprovação.
