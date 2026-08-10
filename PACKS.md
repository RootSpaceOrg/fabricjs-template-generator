# Criar e certificar packs — protocolo operacional

> Runbook do dia a dia (como disparar o agente, corredor, revisão prévia) em
> [OPERACAO.md](OPERACAO.md). **Criar pack é andaime: não altera em nada o
> fluxo de produção com packs já certificados.**

Um pack nasce de uma referência aprovada e vira dados que o motor carrega. Este é o processo completo; nada de pack entra na fábrica fora dele.

## 1. Origem

- **`pack-queue/`**: referências visuais já aprovadas pelo Gustavo (pins, peças de agência, vencedores excepcionais). Escolha uma (ou o Gustavo indica) e mova-a para `packs/<slug>/reference.png`.
- Slug: kebab-case descrevendo a estética, não o nicho (`clinical-photo-editorial`, não `dentista-vermelho`).

## 2. Extração (referência → dados)

Olhando SÓ a reference.png + o [`engine/CATALOG.md`](engine/CATALOG.md):

**0. Assinaturas primeiro (o passo que decide se o pack vai parecer a referência):** antes de qualquer token, liste as **2–3 assinaturas visuais** da referência — o que a torna ELA e não um template qualquer (ex: "tipografia entrelaçada com o cutout do profissional", "verde profundo dramático com luz baixa", "botão dominante como único elemento claro"). Cada assinatura DEVE mapear para recipe+componentes concretos; assinatura que o catálogo não expressa → pare e acione a §6. **Pack extraído sem as assinaturas capturadas é pack de outra coisa** — vai reprovar na certificação por infidelidade, não perca a run.

1. **`pack.json`** — tokens exatos (hexs, famílias/tamanhos, radius), `fit` (funil × verticais), range de slides, `variables` (**só as que algum componente vai usar** — nunca declare por preencher). **Paleta é FECHADA**: todo hex sampleado da referência; cor que não está nos tokens não existe no pack — recipes e slides não podem introduzir cor nova (candidato a verificação mecânica no convert: fill fora dos tokens = rejeição).
2. **`tecnicas.md`** — as dinâmicas do estilo escritas como TÉCNICA (par contínuo, decor voando, duo-tom, alternância de fundos…): o que aplicar, quando e o que já foi reprovado. É o coração do pack.
2a. **`assets/`** (se o estilo tiver geometria fixa) — SVG de arco, moldura,
divisoria: o que nao depende do tema e toda run copia. Precisa estar listado no
`images.md`, senao a run nao sabe que existe (veredito 2026-08-09: os arcos do
clinical ficaram so em `exemplos/` e nenhuma fita de certificacao os usou).
2b. **`exemplos/`** — esqueletos/fitas aprovados como ponto de partida (nunca fôrma; duas gerações com o mesmo esqueleto são defeito).
3. **`images.md`** — fórmulas de prompt por slot de imagem (estilo/luz/registro, nunca assunto) + o que é slot de plataforma vs gerada.
4. **`lessons.md`** — inicia com as lições herdadas RELEVANTES (as que viraram estrutura, anote como estrutura; não copie história morta).
5. **`adaptavel: true|false`** — a decisão que define a paleta (ver §2b).
6. `status: draft` no pack.json.

## 2b. Adaptável ou de paleta fixa (decida ANTES dos tokens)

**Default: adaptável.** ~98% dos packs precisam vestir qualquer marca — o
cliente que usa a fábrica tem a cor dele, não a da referência.

| | Adaptável (padrão) | Paleta fixa |
|---|---|---|
| `paper`/`ink`/`muted`/`wm` | **neutros**, com desvio sutil de temperatura para não virar cinza morto | cores do estilo |
| Cor da marca | entra por `data-variable` (primary/accent) em texto, caixas, números | decorativa apenas |
| Fotos | sem cor DOMINANTE (a marca é o elemento mais colorido da peça) — mas com luz dramática, gesto e ângulo autoral | podem carregar a cor do estilo |
| `fit` | qualquer marca | declare a restrição (ex. "marcas de paleta fria") |

**Adaptável não é sem graça — e "cor neutra" não é "imagem neutra".** Empilhar
"neutro + dessaturado + penumbra + sombra" nas fórmulas de imagem produz foto
séria e apagada (veredito 2026-08-09, clinical): o pêndulo passou do ponto ao
tirar a cor do estilo. O que a adaptabilidade exige é que **nenhuma cor da foto
domine** — não que a foto seja cinza. Luz dramática, gesto em ação, textura,
ângulo autoral e um acento de cor da própria cena continuam valendo.

**Prova obrigatória** (§3, prova de Marca): renderize com uma cor bem diferente
da referência. Se algo brigar — fundo esverdeado contra marca roxa, foto na cor
antiga, texto em `ink` colorido — o pack não é adaptável ainda.

## 3. Construção e validação — POR FITA, ponta a ponta

**Quem cria packs é o criador de packs** (Claude na sessão de trabalho com o Gustavo) — não o agente de produção. O agente de produção só OPERA packs certificados (copy + imagens + sorteio). A fronteira: **criar/consertar pack é trabalho de ferramenta** (local, ciclo de minutos); **gerar posts é produção** (agente, VPS, fila).

### Ciclo de trabalho

Roda **local**, com o motor real — `node engine/assemble.js <fita.html> <outdir>` renderiza em segundos, contra os ~20 minutos de uma run na VPS. O criador compõe, olha, corrige e só leva ao Gustavo o que já passou pela própria crítica.

A entrega para revisão é um **artifact** com os slides grandes, um embaixo do outro, cada um com o veredito do criador. Artifact é onde o Gustavo julga — **não é deploy**: o que vale é o commit, e o pack só muda de status pela mão dele (§4.4).

### As três provas (nenhum pack nasce sem elas)

Todo pack precisa demonstrar que sabe resolver os **três papéis**. Não basta ter uma referência bonita:

| Prova | O que tem que ficar demonstrado |
|---|---|
| **Capa** | scroll-stop com a assinatura do estilo; o slide que segura o dedo |
| **Miolo** | **4–5 tratamentos distintos** — como o estilo resolve `tese+ressalva`, `enumerado`, conteúdo com foto, citação/dado. É a prova que mais falha |
| **CTA** | fechamento que pede ação e fecha o arco, sem virar capa repetida |
| **Marca** | as 3 fitas renderizadas com primaries DIFERENTES (`--primary=#HEX` no assemble): a peça veste qualquer marca, não só a cor do placeholder do pack |

**Por que o miolo é obrigatório e explícito:** o clinical-photo-editorial foi certificado com uma `reference.png` que é UMA CAPA. Ninguém percebeu que o pack não sabia fazer miolo até ele produzir slide após slide de caixa sobre fundo chapado. Referência de capa ensina capa — nada mais.

**Exceção — pack de peça única** (`slides.max ≤ 3`, ex. emotive-fullbleed-lettering): a prova de miolo não se aplica; capa e CTA convivem na mesma peça. O que substitui a prova é demonstrar a **extensão** (como a peça vira 2–3 slides quando a data pede história) e o rodapé institucional. Declare a exceção no `tecnicas.md` do pack.

### Exemplar é HTML, imagem é derivada

Cada padrão vive em `packs/<slug>/exemplos/<nome>.html` — **um arquivo por
padrão**, que é a FONTE. Os JPGs ao lado saem de
`node engine/tools/build-exemplos.js [slug]` e existem só para o portal não
renderizar a cada request.

Por quê: imagem congela o pixel. Quando o motor muda (`data-fit`, empilhamento
sobre véus), todo JPG salvo antes passa a mostrar um estado que o motor não
produz mais — e o agente copia como se fosse aprovado. Foi o defeito do
`fita-aprovada-gram-teste-1`. Com HTML, o exemplar é executável: rode o build
depois de mexer no motor e o que regrediu aparece na hora.

**Exemplar sem HTML não conta como prova.** O nome do arquivo casa com a
entrada correspondente do `tecnicas.md` (linha de tabela em negrito ou título
de seção) — é assim que a galeria do portal monta a legenda.

Se a referência do cliente/inspiração for só de capa, o criador **inventa o miolo** e valida com o Gustavo contra a referência, iterando até encaixar no estilo. `knowledge/design/esqueletos/` é catálogo de estudo para essa hora: composições que já funcionaram, para ajudar a achar a resposta do estilo novo — as cores de lá são ilustrativas, e copiar estrutura pronta não é o objetivo.

O criador constrói o pack completo (tokens, tecnicas.md, images.md, exemplos) e produz a FITA de certificação exercitando as técnicas do estilo, iterando contra render real até estar fiel às referências. **A validação do Gustavo é sobre a fita renderizada** (composição geral, lado a lado com as referências): sem checkpoint de slides isolados.

Técnica que exigir componente fora do catálogo → §6 (mudança de motor, com aval do Gustavo).

## 3c. Slots da plataforma: declare quais o pack aceita

`slots` no `pack.json` lista os slots da plataforma que o estilo usa
(`professionalPhoto`, `logo`, `instagramProfilePicture`). **`[]` significa
nenhum**, e o conversor rejeita quem aparecer.

Sem essa declaração o agente insere logo e foto do profissional por hábito —
eles existem no motor, então nada barra. Num pack cujo conteúdo vive todo
dentro de cartão, o slot solto na `<section>` fica atrás dos cartões ou colado
na borda do slide, comendo o gap. Foi o que reprovou a primeira certificação do
editorial-cards-continuos.

Pack sem a chave aceita qualquer slot (compatibilidade com os packs antigos).

## 4. Certificação (a run que prova o pack)

1. **Três runs completas** (`run.py new cert-<slug>-N --env dev --pack <slug>`) em **TAMANHOS DIFERENTES de fita — 3, 5 e 7 slides** (packs de peça única: 1 peça + variações): duas do MESMO tema e uma de tema diferente — certificação v2 prova, além da fidelidade, a **variância**, o **fôlego do miolo em fita longa** (7 slides sem cair em texto solto) (as duas do mesmo tema não podem sair com o mesmo esqueleto) e a robustez das técnicas (par contínuo/travessias emendando na fita).
2. Corredor inteiro até fidelidade no editor + upload de teste (fluxo do README §Fluxo).
3. Preencher `certification/`: strip.png final, screenshots do editor, template_id de teste, sha dos arquivos do pack, data.
4. **Aprovação do Gustavo** comparando plataforma × reference.png — verificando as três provas do §3 (capa, miolo, CTA). Só ele muda `status: draft → certificado`.
5. Commit + push do pack completo (o pack é código-fonte da fábrica).

## 4b. O que a certificação prova (e o que não prova)

Certificar prova que o pack **gera peça boa e variada** (3 fitas, tamanhos
diferentes, judge PASS, carimbo do Gustavo). **Não** certifica por nicho nem
por etapa de funil.

O campo `fit` do `pack.json` (funil, verticais, `melhor_em`) é **conselho, não
regra**: diz onde o estilo brilha. Usar fora do fit é permitido — o dossiê só
precisa declarar por que aquele estilo serve ao pedido, e a revisão julga.
Bloquear uma run só porque o funil pedido não está no `fit` é rigidez indevida.

## 4c. Fronteira copy × design (quem decide o quê)

| Camada | Decide | NÃO decide |
|---|---|---|
| **Dossiê** (`CONTEXT.md`) | a mensagem; o **formato** de cada slide (`gancho`, `tese+ressalva`, `enumerado`…); o **papel** de cada pedaço (`eyebrow`/`tese`/`apoio`/`itens`); quantos slides; onde o CTA faz sentido | como aquilo vira layout |
| **Pack** (`tecnicas.md`) | brand (tokens) + como **este estilo** resolve cada formato + assinaturas de composição | o que a peça diz; quantos slides |

O pack **não** é só brand: as assinaturas de composição (duo-tom entrelaçado,
bokeh cortado pela borda, colagem 3D) são o que distingue um pack do outro —
sem elas, três packs com a mesma paleta produzem a mesma peça.

O campo `comporta` do `pack.json` é a ponte: diz ao copy o **orçamento de texto
por papel** e os formatos que o estilo `resolve_bem`/`resolve_mal`, para ele não
escrever o que o pack não consegue aplicar. É **orçamento, não gate** — nenhuma
validação automática barra uma headline uma palavra mais longa. Entra ali só o
que mudaria a copy se o autor soubesse; técnica de composição não entra.

## 5. Vida do pack

- Lessons por pack; 2× recorrente → vira técnica/lei em tecnicas.md → **re-certificar** (versão +1, nova entrada em certification/).
- 3+ lessons estruturais sem correção → volta a `draft` (sai da fábrica).
- Melhorias de motor NUNCA entram disfarçadas de correção de pack (e vice-versa).

## 6. Quando o pack pede o que o catálogo não tem

Componente novo é mudança de MOTOR (CATALOG.md + design-system.css + convert.js juntos — os três ou nenhum) e exige pedido explícito ao Gustavo. A pergunta antes de propor: "dá pra expressar com os componentes existentes em outra área/camada?" — quase sempre dá.

## Checklist de entrada na fábrica

- [ ] reference.png aprovada na origem
- [ ] pack.json sem variáveis/tokens fantasma
- [ ] **as três provas (§3): capa, miolo com 3+ tratamentos distintos, CTA** — referência só de capa não dispensa a prova de miolo
- [ ] tecnicas.md cobrindo as assinaturas E a tradução formato → tratamento (§4c); exemplos/ com pelo menos 1 fita aprovada
- [ ] certificação: 3 fitas (2 mesmo tema c/ variância + 1 tema novo), fidelidade FIEL, template de teste no ar
- [ ] aprovação explícita do Gustavo (status: certificado)
- [ ] commit + push
