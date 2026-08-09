# Certificação — bold-educacional v4

Data: 2026-08-09 · Protocolo: PACKS.md §4 (3 runs em **3, 5 e 7 slides**) · Ambiente: dev

**Marco:** primeira certificação com a criação **fatiada em 6 turnos** (dossiê →
imagens → abertura → miolo → fechamento+render → judge). As três fitas correram
ponta a ponta sem nenhum job enfileirado à mão — antes, 5 runs exigiram 12
intervenções manuais.

## As 3 fitas da prova

| Run | Slides | Tema | Template dev | Judge | Fidelidade |
|-----|--------|------|--------------|-------|------------|
| cert-bold-v2-mito-3 | 3 | "laser é só para dor aguda?" | `4xLNwys9mQAkfL6Hvx5qy` | QA: PASS | FIEL |
| cert-bold-v3-mito-5 | 5 | mesmo tema, outra fita | `TyWivbiQNm3ByrPJ_IkCk` | QA: PASS | FIEL |
| cert-bold-v2-sessoes-7 | 7 | o que muda entre a 1ª e a 6ª sessão | `DfoukJka-RVCN3BIaKHa8` | QA: PASS | FIEL |

As duas primeiras são do **mesmo tema** de propósito — é o que prova variância.
Saíram com estruturas diferentes: a de 3 vai direto ao statement; a de 5 abre
mito→verdade e usa enumerado numerado, cartão e watermark.

Aprovadas pelo Gustavo em 2026-08-09, com os três templates abertos no editor.

## O que esta certificação provou (e como)

Ela nasceu de uma reprovação: na primeira rodada o Gustavo apontou três defeitos
que o judge tinha deixado passar. Cada um virou lei, e a rodada seguinte foi o
teste do conhecimento — **os três não se repetiram em nenhuma das fitas**:

| Defeito (rodada 1) | Virou | Resultado (rodada 2) |
|---|---|---|
| Colagem decepada na emenda (overhang onde devia ser travessia) | R9 + lei em geral.md | não repetiu |
| Foto de cena como decor de canto | R10 + nota no tecnicas.md | não repetiu |
| `professionalPhoto` flutuando (área terminando antes da linha 13) | R11 + nota no CATALOG | não repetiu |

A rodada 2 trouxe um defeito novo (watermark e colagem disputando o mesmo canto,
que o gate não pega porque camada×camada é permitido) → virou **R12**, e a
rodada 3 da fita de 5 o evitou.

## Ressalva registrada

A fita de 5 (v3) tem os slides 2 e 3 com o mesmo "?" gigante na mesma posição —
falta de variância *dentro* da fita, que virou lei em `geral.md` depois desta
certificação. Aprovada com a ressalva anotada.

**Padrão observado nas três rodadas:** um defeito diferente por vez, nenhum
repetido. É ruído de geração por LLM, não degradação do pack. Daí a regra
prática registrada em `lessons.md`: certificar com a melhor de N, não perseguir
a fita perfeita.

## Exemplares do pack nesta versão

6 padrões documentados, cada um com HTML como fonte (`exemplos/*.html`) e imagem
derivada por `engine/tools/build-exemplos.js`: capa meme, statement chapado,
miolo com objeto de conteúdo, citação em caixa, lista em bloco e número-dado.
Os três últimos nasceram nesta rodada, para cumprir a régua de 4–5 tratamentos
de miolo (PACKS.md §3).
