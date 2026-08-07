# Plano — Portal de backoffice da fábrica

Status: **PLANO — nada implementado.** Decisões do Gustavo (2026-08-07):
VPS + domínio público · portal dispara turnos (painel + fila) · aprovação
também pelo Telegram.

## 1. O que o portal é (e o que não é)

**É** o cockpit do processo de criação: ver o que o agente fez, o que está
pendente, aprovar/reprovar com feedback, enfileirar próximas tarefas e revisar
o conhecimento dos packs.

**Não é** um novo motor: ele não compõe, não converte, não julga. Ele **lê o
estado que já existe no disco** (`artifacts/runs/<slug>/run.json`, `strip.png`,
`judge-report.md`, `dossie.md`) e **dispara os mesmos comandos** que hoje eu
disparo à mão (`openclaw agent -m …`, `engine/run.py advance`, corredor).

Consequência importante: a fábrica continua funcionando sem o portal. Se ele
cair, o fluxo por SSH/Telegram segue igual.

## 2. Realidade da infra (verificado em 2026-08-07)

| Item | Estado |
|---|---|
| VPS | 2 cores, ~6 GB livres de 8, 66 GB de disco livre |
| Portas 80/443/3000/8080 | livres |
| Docker | instalado e rodando |
| OpenClaw | CLI com `cron` e `webhooks` nativos; sem cron cadastrado |
| Runtime | Node 24, Python 3.12 |

Cabe folgado. O gargalo real não é máquina: é **concorrência de turno** — o
OpenClaw processa um turno por vez, e uma run com geração de imagem leva
minutos. A fila precisa ser serial por design (ver §4).

## 3. Arquitetura mínima

```
[navegador / celular]           [Telegram]
        │ HTTPS                      │ webhook
        ▼                            ▼
   Caddy (TLS + senha)  ──►  portal (FastAPI + HTMX)
                                 │
                    ┌────────────┼─────────────┐
                    ▼            ▼             ▼
              SQLite (fila,   disco da      subprocess:
              vereditos)      fábrica       openclaw agent /
                              (runs, strips) run.py / corredor
```

- **FastAPI + HTMX + Jinja** (Python, sem build de frontend). Motivo: o
  ecossistema da fábrica já é Python/Node no VPS; HTMX evita SPA, deploy e
  bundler para um backoffice de um usuário.
- **SQLite** para fila, vereditos e histórico. Um arquivo, zero serviço.
- **Caddy** para TLS automático + basic auth (usuário único).
- **systemd** para o portal e para o worker da fila.
- Roda como serviço separado, lendo o clone do agente
  (`/root/.openclaw/workspace/external/fabricjs-template-generator`).

## 4. Fila de execução (o coração)

Tabela `jobs`: `id, tipo, slug, payload, status, tentativas, log, criado_em`.
Tipos: `compose`, `corredor`, `judge`, `upload`, `assets`, `feedback`.

- **Worker serial** (um por vez, sempre): pega o próximo `pending`, executa,
  grava log e resultado, marca `done`/`failed`. Serial porque o OpenClaw não
  paraleliza turnos e o corredor é pesado.
- **Timeout por tipo** (turno de agente ~15 min; corredor ~8 min) e retry
  manual pelo portal — nunca automático em cima de turno de LLM.
- **Idempotência**: job carrega o `slug` e o estágio esperado; se o estado do
  disco já avançou, o job vira `skipped` em vez de repetir trabalho.

## 5. Telas (5, nessa ordem de valor)

1. **Runs** — lista com estágio, pack, tema, miniatura do strip, idade. Cores
   por estado (aguardando você / rodando / travada / done).
2. **Run** — strip em tamanho real (zoom por slide), dossiê, judge-report, log
   do último turno. Botões: **Aprovar**, **Reprovar com feedback** (textarea →
   vira job `feedback` = turno de revisão para o agente), **Rodar corredor**,
   **Publicar em dev**.
3. **Fila** — jobs pendentes/rodando/falhos, com log e "reenfileirar".
4. **Packs** — cada pack com status, versão, técnicas/lessons renderizados e
   link para as fitas de certificação. Botão "iniciar novo pack" cria a
   estrutura e enfileira a peça de prova.
5. **Conhecimento** — editor simples de `knowledge/**` e `packs/*/tecnicas.md`
   com commit+push automático na gravação (o portal escreve no clone e faz git
   push; sem editor de código, só textarea + preview).

## 6. Telegram (aprovar pelo chat)

Fluxo mínimo que funciona sem inventar bot novo:

1. Portal termina um job de render → envia ao bot existente (@rgjmasterbot,
   Bot API `sendPhoto`) o strip + resumo + **botões inline** `Aprovar` /
   `Reprovar`.
2. Telegram chama o **webhook** do portal (`/tg/callback`) com a escolha.
3. `Aprovar` → registra veredito e enfileira o próximo estágio.
   `Reprovar` → o portal pede o texto ("responda com o que corrigir"), e a
   resposta vira job `feedback` (turno de revisão para o agente).

Detalhes que evitam dor: validar `secret_token` do webhook (senão qualquer um
aprova), whitelist do seu `chat_id`, e o portal como **única** fonte de
verdade do veredito (o chat é interface, não estado).

## 7. Fases (cada uma útil sozinha)

| Fase | Entrega | Esforço |
|---|---|---|
| **P1 — Visibilidade** | FastAPI + telas Runs/Run lendo o disco; Caddy+TLS+senha; systemd. Sem escrever nada. | ~meio dia |
| **P2 — Fila** | SQLite + worker serial + tela Fila; botões "rodar corredor" e "publicar dev". | ~1 dia |
| **P3 — Feedback loop** | Aprovar/Reprovar no portal → job `feedback` → turno do agente com o texto. | ~meio dia |
| **P4 — Telegram** | Envio do strip com botões inline + webhook de callback. | ~meio dia |
| **P5 — Packs & conhecimento** | Telas de pack, editor de conhecimento com commit/push, "iniciar novo pack". | ~1 dia |
| **P6 — Watchdog (opcional)** | `openclaw cron` a cada 15 min: reenfileira run parada há muito tempo; nunca avança gate sozinho. | ~2h |

## 8. Riscos (sendo realista)

- **Concorrência com meus turnos**: se eu disparar turno por SSH enquanto o
  worker dispara outro, os dois competem pelo mesmo agente. Mitigação: lock
  em arquivo compartilhado (`/root/.factory-lock`) respeitado pelos dois.
- **Segredo exposto**: portal na internet com botão que roda comando no VPS é
  superfície real. Mitigação: basic auth + IP allowlist opcional + nenhum
  campo livre virando shell (jobs são tipos fechados, nunca comando cru).
- **Divergência de estado**: portal e disco podem discordar se alguém mexer
  por fora. Mitigação: disco é a verdade; SQLite guarda só fila e vereditos.
- **Escopo escorregando**: a tentação é virar "editor de templates". Não é —
  edição visual é a plataforma KultivAi, não o backoffice.
- **Custo de manutenção**: mais um serviço no VPS para cuidar. Se em duas
  semanas você não estiver usando as telas 3–5, elas provam que não eram
  necessárias — mate-as.

## 9. Decisão pendente antes de começar

- **Domínio**: qual subdomínio usar (ex.: `fabrica.kultivai.com.br` apontando
  para o IP do VPS) — precisa de um registro A no DNS.
- **Autenticação**: basic auth (mais simples) ou senha única em cookie? Padrão
  proposto: basic auth do Caddy.
