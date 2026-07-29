# Evals — regressão e golden set

## Golden set (`golden/`)

10–20 screenshots de carrosséis de **nível profissional** (1080×1350), nomeados `<familia-estetica>-<n>.png` — reais de contas fortes do nicho, conversões do Claude Design, ou vencedores excepcionais desta pipeline promovidos manualmente. São a âncora do "10" na rubrica. **Curadoria é humana**: o Gustavo adiciona/remove; a pipeline nunca edita esta pasta.

## Prompts fixos de regressão

Rodar os 5 sempre que arquivos de `bt/` mudarem (modo 2 do `JUDGE.md` — sem publicar):

| id | Prompt |
|----|--------|
| P1 | "5 mitos sobre depilação a laser" · laserterapia · topo |
| P2 | "como funciona a primeira sessão de laserterapia" · laserterapia · meio |
| P3 | "quanto custa e quanto dura: as 6 objeções antes de fechar" · laserterapia · fundo |
| P4 | "por que dieta da moda engorda de volta" · nutricionista · topo |
| P5 | "checklist antes de escolher seu dentista" · dentista · meio |

## Histórico (`scores.jsonl`)

1 linha JSON por avaliação (schema no `JUDGE.md`). Regra: média dos 5 prompts caiu ≥3 pontos vs rodada anterior → a mudança regrediu; reverter ou corrigir antes de produção.

## Lições (`lessons.md`)

1 linha por rejeição humana na tela de revisão: `- <data> <template_id>: <motivo>`. Motivo que aparece 3× → vira edição em `DESIGN.md`/`CONTEXT.md` (e a edição roda esta regressão).
