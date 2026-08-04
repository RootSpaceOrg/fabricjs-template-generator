# Criar e certificar packs — protocolo operacional

Um pack nasce de uma referência aprovada e vira dados que o motor carrega. Este é o processo completo; nada de pack entra na fábrica fora dele.

## 1. Origem

- **`pack-queue/`**: referências visuais já aprovadas pelo Gustavo (pins, peças de agência, vencedores excepcionais). Escolha uma (ou o Gustavo indica) e mova-a para `packs/<slug>/reference.png`.
- Slug: kebab-case descrevendo a estética, não o nicho (`clean-numbered-editorial`, não `dentista-vermelho`).

## 2. Extração (referência → dados)

Olhando SÓ a reference.png + o [`engine/CATALOG.md`](engine/CATALOG.md):

**0. Assinaturas primeiro (o passo que decide se o pack vai parecer a referência):** antes de qualquer token, liste as **2–3 assinaturas visuais** da referência — o que a torna ELA e não um template qualquer (ex: "tipografia entrelaçada com o cutout do profissional", "verde profundo dramático com luz baixa", "botão dominante como único elemento claro"). Cada assinatura DEVE mapear para recipe+componentes concretos; assinatura que o catálogo não expressa → pare e acione a §6. **Pack extraído sem as assinaturas capturadas é pack de outra coisa** — vai reprovar na certificação por infidelidade, não perca a run.

1. **`pack.json`** — tokens exatos (hexs, famílias/tamanhos, radius), `fit` (funil × verticais), range de slides, `variables` (**só as que algum componente vai usar** — nunca declare por preencher), `sorteio` (papéis, regras de adjacência). **Paleta é FECHADA**: todo hex sampleado da referência; cor que não está nos tokens não existe no pack — recipes e slides não podem introduzir cor nova (candidato a verificação mecânica no convert: fill fora dos tokens = rejeição).
2. **`recipes/`** — 1 JSON por papel de slide (abertura, 2–4 variantes de miolo, fechamento, opcionais). Cada recipe = componentes do catálogo × grid areas × slots editáveis com min/max. Variedade entre variantes é POSICIONAL (áreas diferentes), não só de conteúdo — itens uniformes são assinatura de IA.
3. **`images.md`** — fórmulas de prompt por slot de imagem (estilo/luz/registro, nunca assunto) + o que é slot de plataforma vs gerada.
4. **`lessons.md`** — inicia com as lições herdadas RELEVANTES (as que viraram estrutura, anote como estrutura; não copie história morta).
5. `status: draft` no pack.json.

## 3. Construção e validação — POR FITA, ponta a ponta

**Quem cria packs é o criador de packs** (Claude/Fable na sessão de trabalho com o Gustavo, com render validado via SSH) — não o agente de produção. O agente de produção só OPERA packs certificados (copy + imagens + sorteio).

O criador constrói o pack completo (tokens, recipes, images.md) e produz a FITA de certificação de uma vez — exercitando todas as recipes — iterando contra render real até estar fiel às referências. **A validação do Gustavo é sobre a fita renderizada** (composição geral, lado a lado com as referências): sem checkpoint de slides isolados. Renders por recipe são ferramenta interna de diagnóstico do criador, não gate.

Recipe que exigir componente fora do catálogo → §6 (mudança de motor, com aval do Gustavo).

## 4. Certificação (a run que prova o pack)

1. Run completa: `run.py new cert-<slug> --env dev --pack <slug>` — fita no range máximo, **exercitando TODAS as recipes** (recipe não exercitada não certifica e não pode ser sorteada em produção).
2. Corredor inteiro até fidelidade no editor + upload de teste (fluxo do README §Fluxo).
3. Preencher `certification/`: strip.png final, screenshots do editor, template_id de teste, sha dos arquivos do pack, data.
4. **Aprovação do Gustavo** comparando plataforma × reference.png. Só ele muda `status: draft → certificado`.
5. Commit + push do pack completo (o pack é código-fonte da fábrica).

## 5. Vida do pack

- Lessons por pack; 2× recorrente → corrigir recipe → **re-certificar** (versão +1, nova entrada em certification/).
- 3+ lessons estruturais sem correção → volta a `draft` (sai da fábrica).
- Melhorias de motor NUNCA entram disfarçadas de correção de pack (e vice-versa).

## 6. Quando o pack pede o que o catálogo não tem

Componente novo é mudança de MOTOR (CATALOG.md + design-system.css + convert.js juntos — os três ou nenhum) e exige pedido explícito ao Gustavo. A pergunta antes de propor: "dá pra expressar com os componentes existentes em outra área/camada?" — quase sempre dá.

## Checklist de entrada na fábrica

- [ ] reference.png aprovada na origem
- [ ] pack.json sem variáveis/tokens fantasma
- [ ] todas as recipes com smoke individual PASS
- [ ] certificação: fita completa, todas as recipes, fidelidade FIEL, template de teste no ar
- [ ] aprovação explícita do Gustavo (status: certificado)
- [ ] commit + push
