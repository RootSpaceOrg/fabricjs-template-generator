# Judge — pais-2026

QA do render vigente (`strip.png`, 2026-08-06) contra `packs/emotive-fullbleed-lettering/reference.png`.

## Regras duras (R1–R6)

| Regra | Veredito | Evidência verificável |
|---|---|---|
| R1 avatar | ok | Não há slot de pessoa/avatar; a única imagem de slot é `logo` em S1. Pai e filho são parte da foto editorial de fundo, não placeholders. |
| R2 corte | ok | S1: copy, telefone, @, data e logo ficam integralmente dentro do canvas; lettering e sparkles não cortam leitura. |
| R3 fundos | n/a | Peça única: alternância de fundos não se aplica. A foto funde no gradiente primary do topo ao rodapé conforme o pack. |
| R4 área morta | ok | A foto emocional, lettering central, copy e rodapé institucional distribuem as âncoras sem vazio visual dominante. |
| R5 UI-decor | ok | Sparkles e lettering 3D são ornamento temático; não imitam UI. |
| R6 contraste | ok | Copy, data e rodapé claros permanecem legíveis sobre primary azul; lettering cream tem contraste suficiente na faixa do gradiente. |

## QA do pack

- Rostos de pai e filho estão naturais, nítidos e totalmente livres de lettering, sparkles e overlay denso; a emoção continua sendo o foco da foto.
- Lettering `PAIS` cream, script cobre e bigode 3D são legíveis e inteiros; o objeto temático cruza a letra A sem esconder a palavra.
- O gradiente cobre a base e funde foto/cor sem faixa dura; o terço inferior neutro da foto funciona como transição para a primary.
- Sparkles cream são discretos, ficam afastados dos rostos e reforçam o registro comemorativo.

## QA narrativo

- Em peça única comemorativa, o gancho é a cena afetiva pai-filho; a homenagem curta não vira anúncio ou promessa.
- Não há imperativo sem mecanismo, alegação de saúde ou benefício clínico. A mensagem de reconhecimento é apropriada para Dia dos Pais e o rodapé mantém o template reutilizável por clínica.
- Não existe redundância por se tratar de uma única peça; copy e identidade visual entregam o mesmo valor emocional sem competir.

**QA: PASS**
