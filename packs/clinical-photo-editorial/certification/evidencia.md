# Certificação — clinical-photo-editorial v7

Data: 2026-08-09 · Protocolo: PACKS.md §4 · Ambiente: dev
**Status: aguardando aprovação do Gustavo** (o pack está em `draft`)

Substitui a certificação v6 (2026-08-06), cujos artefatos foram removidos: eles
descreviam um pack de paleta fixa verde, que não existe mais.

## As 3 fitas da prova

| Run | Slides | Primary de teste | Judge | Arcos | Transições declaradas |
|-----|--------|------------------|-------|-------|----------------------|
| cert-clin-v4b-joelho-5 | 5 | `#2E8C7F` teal | QA: PASS | 2 | 3 |
| cert-clin-v4-joelho-6 | 6 | `#7B3FA0` roxo | QA: PASS | 2 | 4 |
| cert-clin-v4-primeira-7 | 7 | `#C2410C` laranja | QA: PASS | 2 | 6 |

As duas primeiras são do MESMO tema (variância); a de 7 é tema diferente.
**Cada fita renderizada com uma marca distinta** — é a prova de Marca do §3,
que este pack não tinha como passar antes.

## O que mudou entre a v6 e esta

Três fases, cada uma nascida de um veredito do Gustavo:

**1. Transição na emenda.** O `tecnicas.md` descrevia slides ISOLADOS, e o
designer escolhia o tratamento sem olhar o vizinho — daí dois slides com
foto-metade espelhada, que leem como par quebrado. Agora ele responde, por
slide, *"sou continuação ou mudança de padrão?"* e escreve a resposta como
comentário no HTML. Virou R13 no judge.

**2. `primary`/`accent` em vez de `primary`/`secondary`.** A fábrica nomeia
pelo PAPEL; o conversor traduz `accent` → `secondary`, que é como a plataforma
guarda. Nada mudou no frontend.

**3. Pack adaptável** (`adaptavel: true`). A paleta estrutural era inteira
verde — `paper`, `ink`, `muted` e `wm` eram variações de teal — e as fórmulas
de imagem pediam "tons verde-petróleo". Numa marca roxa isso saía como
verde-escuro brigando com roxo, e foto esverdeada contra UI roxa. Tokens agora
neutros; fotos em paleta neutra dessaturada, com personalidade vindo de luz,
matéria e enquadramento.

## Gates que nasceram desta certificação

O padrão que se repetiu: **lei escrita não pega, gate mecânico pega de
primeira**. Três defeitos viraram verificação automática:

- **Texto transbordando a célula** — a headline da capa caiu sobre o apoio, e
  as áreas declaradas não se cruzavam (o gate de sobreposição não tinha o que
  pegar). Agora o convert compara `scrollHeight` com `clientHeight`.
- **Assinatura que não chega na run** — os arcos existiam no `tecnicas.md`
  desde o começo e **nenhuma fita os usava**: o SVG só estava em `exemplos/`,
  o `images.md` não o mencionava e a fatia da abertura não pedia as
  assinaturas. Criou-se `assets/` no pack (PACKS.md §2a).
- **Deploy silencioso** — o portal roda de uma cópia; `git pull` não a
  atualiza. Uma certificação inteira rodou sem a lei de transição por isso.
  Agora `portal/deploy.sh` verifica com `diff`.

## Ressalvas registradas

- **Fita de 5, slide 5**: a headline do fechamento encosta no CTA, sem respiro.
- A `reference.png` do pack continua sendo **uma capa**. O miolo tem estrutura
  (os 8 padrões em `exemplos/`) mas a assinatura visual dele foi inventada, não
  extraída de referência. É a pendência aberta mais antiga do pack.
