# Evidência de certificação — cert-lp-v1-carpo-4

- Data: 2026-08-14
- Tema: síndrome do túnel do carpo
- Business type: `laserterapy`
- Run: 4 slides, ambiente `dev`
- Template de teste: `bG2mwcFnX2Y7BGkv5gIa6`
- Judge: `PASS`
- Fidelidade: `FIEL`

## Corredor executado

Pesquisa → dossiê → imagem RGBA → abertura → miolo → fechamento + render →
conversão → judge → upload. A imagem de travessia é PNG RGBA, centralizada e
encosta na base (0 px de margem transparente inferior); o problema aparece
antes de qualquer equipamento — esta fita não usa imagem de aparelho.

Correção pós-certificação: S3 voltou ao fundo branco e sua copy voltou a tinta;
assim, apenas a capa permanece invertida e a travessia S2→S3 fica sobre o
miolo claro contínuo.

Correção de travessia: o asset passou a ser PNG RGBA retrato (1024×1536), com
apenas mãos e antebraços verticais e o punho em vermelho translúcido; não há
pessoa inteira, rosto, roupa ou cenário.

## Evidências visuais

- `cert-lp-v1-carpo-4-strip.png`
- `cert-lp-v1-carpo-4-slide-1.png` a `cert-lp-v1-carpo-4-slide-4.png`

## Integridade do pack nesta run

| Arquivo | SHA-256 |
|---|---|
| `pack.json` | `ad7e98d984039961766aa84ac7d4f7c98d8ddaf353c38f72975ed5b2bd4a6bd0` |
| `tecnicas.md` | `0b3b3082e899c9f5bc769f0c79cbee37ebe6cbed846d7faab6d4d4725d368ba4` |
| `images.md` | `6c6aca20021eb0e6d2922896cb1467ff21294eb73944509a6cb348fb08d7c779` |
| `reference.png` | `d2591fe748a1089f1dbb50646f85daf815c437e5698f7216869417f3c3dedccf` |

`bash engine/tools/check-packs.sh` passou para todos os exemplares de todos os
packs após esta run. O status do pack permanece `draft`: a certificação completa
do pack requer as três fitas e a aprovação explícita do Gustavo, conforme
`PACKS.md` §4.
