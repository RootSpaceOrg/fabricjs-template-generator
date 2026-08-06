# Criar e certificar packs — protocolo operacional

Um pack nasce de uma referência aprovada e vira dados que o motor carrega. Este é o processo completo; nada de pack entra na fábrica fora dele.

## 1. Origem

- **`pack-queue/`**: referências visuais já aprovadas pelo Gustavo (pins, peças de agência, vencedores excepcionais). Escolha uma (ou o Gustavo indica) e mova-a para `packs/<slug>/reference.png`.
- Slug: kebab-case descrevendo a estética, não o nicho (`clinical-photo-editorial`, não `dentista-vermelho`).

## 2. Extração (referência → dados)

Olhando SÓ a reference.png + o [`engine/CATALOG.md`](engine/CATALOG.md):

**0. Assinaturas primeiro (o passo que decide se o pack vai parecer a referência):** antes de qualquer token, liste as **2–3 assinaturas visuais** da referência — o que a torna ELA e não um template qualquer (ex: "tipografia entrelaçada com o cutout do profissional", "verde profundo dramático com luz baixa", "botão dominante como único elemento claro"). Cada assinatura DEVE mapear para recipe+componentes concretos; assinatura que o catálogo não expressa → pare e acione a §6. **Pack extraído sem as assinaturas capturadas é pack de outra coisa** — vai reprovar na certificação por infidelidade, não perca a run.

1. **`pack.json`** — tokens exatos (hexs, famílias/tamanhos, radius), `fit` (funil × verticais), range de slides, `variables` (**só as que algum componente vai usar** — nunca declare por preencher). **Paleta é FECHADA**: todo hex sampleado da referência; cor que não está nos tokens não existe no pack — recipes e slides não podem introduzir cor nova (candidato a verificação mecânica no convert: fill fora dos tokens = rejeição).
2. **`tecnicas.md`** — as dinâmicas do estilo escritas como TÉCNICA (par contínuo, decor voando, duo-tom, alternância de fundos…): o que aplicar, quando e o que já foi reprovado. É o coração do pack.
2b. **`exemplos/`** — esqueletos/fitas aprovados como ponto de partida (nunca fôrma; duas gerações com o mesmo esqueleto são defeito).
3. **`images.md`** — fórmulas de prompt por slot de imagem (estilo/luz/registro, nunca assunto) + o que é slot de plataforma vs gerada.
4. **`lessons.md`** — inicia com as lições herdadas RELEVANTES (as que viraram estrutura, anote como estrutura; não copie história morta).
5. `status: draft` no pack.json.

## 3. Construção e validação — POR FITA, ponta a ponta

**Quem cria packs é o criador de packs** (Claude/Fable na sessão de trabalho com o Gustavo, com render validado via SSH) — não o agente de produção. O agente de produção só OPERA packs certificados (copy + imagens + sorteio).

O criador constrói o pack completo (tokens, tecnicas.md, images.md, exemplos) e produz a FITA de certificação de uma vez — exercitando as técnicas do estilo — iterando contra render real até estar fiel às referências. **A validação do Gustavo é sobre a fita renderizada** (composição geral, lado a lado com as referências): sem checkpoint de slides isolados. Renders por recipe são ferramenta interna de diagnóstico do criador, não gate.

Técnica que exigir componente fora do catálogo → §6 (mudança de motor, com aval do Gustavo).

## 4. Certificação (a run que prova o pack)

1. **Três runs completas** (`run.py new cert-<slug>-N --env dev --pack <slug>`) em **TAMANHOS DIFERENTES de fita — 3, 5 e 7 slides** (packs de peça única: 1 peça + variações): duas do MESMO tema e uma de tema diferente — certificação v2 prova, além da fidelidade, a **variância**, o **fôlego do miolo em fita longa** (7 slides sem cair em texto solto) (as duas do mesmo tema não podem sair com o mesmo esqueleto) e a robustez das técnicas (par contínuo/travessias emendando na fita).
2. Corredor inteiro até fidelidade no editor + upload de teste (fluxo do README §Fluxo).
3. Preencher `certification/`: strip.png final, screenshots do editor, template_id de teste, sha dos arquivos do pack, data.
4. **Aprovação do Gustavo** comparando plataforma × reference.png. Só ele muda `status: draft → certificado`.
5. Commit + push do pack completo (o pack é código-fonte da fábrica).

## 5. Vida do pack

- Lessons por pack; 2× recorrente → vira técnica/lei em tecnicas.md → **re-certificar** (versão +1, nova entrada em certification/).
- 3+ lessons estruturais sem correção → volta a `draft` (sai da fábrica).
- Melhorias de motor NUNCA entram disfarçadas de correção de pack (e vice-versa).

## 6. Quando o pack pede o que o catálogo não tem

Componente novo é mudança de MOTOR (CATALOG.md + design-system.css + convert.js juntos — os três ou nenhum) e exige pedido explícito ao Gustavo. A pergunta antes de propor: "dá pra expressar com os componentes existentes em outra área/camada?" — quase sempre dá.

## Checklist de entrada na fábrica

- [ ] reference.png aprovada na origem
- [ ] pack.json sem variáveis/tokens fantasma
- [ ] tecnicas.md cobrindo as assinaturas; exemplos/ com pelo menos 1 fita aprovada
- [ ] certificação: 3 fitas (2 mesmo tema c/ variância + 1 tema novo), fidelidade FIEL, template de teste no ar
- [ ] aprovação explícita do Gustavo (status: certificado)
- [ ] commit + push
