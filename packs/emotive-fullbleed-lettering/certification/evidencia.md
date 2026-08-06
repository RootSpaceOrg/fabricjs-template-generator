# Certificação — emotive-fullbleed-lettering v1 (fita-v2, peça única)

Data: 2026-08-06 · Protocolo: PACKS.md §4 (3 runs) · Ambiente: dev

## As 3 peças da prova

| Run | Tema | Template dev | Judge | Observação |
|-----|------|--------------|-------|------------|
| pais-2026 | Dia dos Pais (sofá) | `wbOJlMz0bSsz1TPfOEBeS` | QA: PASS | peça 1 — aprovada pelo Gustavo na PLATAFORMA ("ficou certinho": gradiente recoloriu com o preset) |
| pais-2026-b | Dia dos Pais — MESMO tema (aviãozinho) | `-6sw4mOkeIFRHCz3LpLvM` | QA: PASS | variância provada: cena, lettering (gravata/paizão) e copy distintos |
| setembro-amarelo | Setembro Amarelo — tema NOVO (campanha) | `UcKvSkZ9WfIWTsWjxBMS-` | QA: PASS | o estilo generaliza para conscientização, não só comemoração |

Capacidades novas do motor exercitadas: `data-overlay-gradient` (gradiente com
fillVariableConfig por stop — recolorido pela primary do usuário, validado na
plataforma), peça única (`data-role="unica"`), `data-inset` (respiro da borda).
Ajuste final pós-judge por veredito do Gustavo: lettering ampliado (rows 4–11)
nas 3 peças — re-render + re-upload registrados nos strips desta pasta.

## SHA-256 (16) dos arquivos do pack nesta versão

| Arquivo | sha |
|---------|-----|
| images.md | `465e797eb1205c72` |
| lessons.md | `7ba968190f0f5fe7` |
| pack.json | `67737c71f7f90b54` |
| reference.png | `897faa0d8a62e23c` |
| tecnicas.md | `78523cb21b46744c` |

## Carimbo

- [ ] Aprovação do Gustavo → `pack.json` `status: draft → certificado`
