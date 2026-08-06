# Imagens — emotive-fullbleed-lettering

O pack não guarda assets — TODA run gera os seus em `artifacts/runs/<slug>/assets/`.

| Slot | Fórmula |
|------|---------|
| foto emocional | "fotografia realista e emocional de {cena da data — ex.: pai e filho brincando no sofá}, luz golden hour quente entrando pela janela, tons azulados nas sombras, cores cinematográficas, alegria genuína, closeup médio, SEM texto; terço inferior mais escuro/neutro (vai receber o gradiente)" — retrato 1080x1350+ |
| lettering-arte | "typographic art sticker, transparent background PNG: the word {PALAVRA} in huge bold rounded display letters, warm cream color, overlapped by the word {palavra} in elegant copper script calligraphy crossing it; {1–2 objetos 3D do tema, ex: glossy 3D black mustache tangled through one letter, 3D blue like-button speech bubble with white heart}; soft 3D render, studio light, tudo INTEIRO com margem nas 4 bordas, nada cortado" |
| sparkles | "set of small 4-point star sparkles and tiny glows, warm cream color, transparent background PNG, scattered composition, soft 3D" |
| logo / foto de perfil | slots da plataforma (placeholder canônico) |

**Regras:** lettering e sparkles SEMPRE RGBA transparente, tudo inteiro com
margem (verificar alpha bbox); foto sem rostos deformados (verificação visual
obrigatória — rosto estranho reprova a foto); paleta da arte = cream + acentos
quentes (cobre) + objetos do tema — a cor de marca entra pelo OVERLAY, nunca
pela arte.
