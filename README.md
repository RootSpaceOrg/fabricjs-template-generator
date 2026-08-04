# fabricjs-template-generator

Fábrica de templates da plataforma (mkt-platform). Tudo vive em **[`gp3/`](gp3/README.md)**:
motor sem estética (design system fechado + conversor determinístico + runner) e
packs de design certificados. Arquitetura: [`gp3/ARCHITECTURE.md`](gp3/ARCHITECTURE.md).
Criar packs: [`gp3/PACKS.md`](gp3/PACKS.md).

Gatilho de agente: [`skills/gp2-business-template/SKILL.md`](skills/gp2-business-template/SKILL.md).

## Setup

```bash
pip install -r requirements.txt
npm install
npx playwright install chromium
```

Credenciais AWS: `.env` em `/root/secrets` (VPS) ou `GP2_SECRETS_DIR`.
Detalhes de ambiente: [`SETUP.md`](SETUP.md) (seções de pipeline antiga são históricas).

## História

As pipelines anteriores (gp2 genérica multi-nicho e bt/) foram aposentadas em
2026-08-04 — o conhecimento válido delas vive como estrutura no gp3 e em
`gp3/evals/lessons.md`; o código, no histórico do git.
