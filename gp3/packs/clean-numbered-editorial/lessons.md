# Lessons — clean-numbered-editorial (pack gp3)

Herdadas do bt/styles/clean-numbered-editorial (pagas com sangue, viraram estrutura do pack):

- Evidência visual obrigatória em todo item de miolo → campo `ds-photo` presente em item-a/b/c (não é opcional na recipe).
- `professionalPhoto` obrigatório na capa e no CTA → `ds-slot` fixo nas recipes capa/cta.
- Itens uniformes = assinatura de conteúdo IA → 3 variantes + respiro, gate mecânico do runner proíbe recipes iguais adjacentes.
- Watermark: 1 palavra por fronteira, respiro ≥120px entre palavras — **costura cross-slide ainda não existe no gp3 v1** (assemble.js, ponytail: adicionar camada de costura quando certificar); watermarks por enquanto vivem dentro do próprio slide.
- Fundo neutro é LITERAL, nunca data-variable (causa do dark-vs-light) → tokens do pack; só o acento é `data-variable="primary"`.
- Placeholder canônico de professionalPhoto: `gp3/engine/assets/professional-photo-1/2.b64.txt`; recomendação aberta de trocar por cutout de foto real (falso alarme recorrente no judge).

- 2026-08-04 (auditoria anti-resíduo gp2): pack declarava `secondary: #141414` (= ink) sem nenhuma recipe usar — e o motor tinha fallback `|| tokens.ink` pro secondary (chute estético no motor). Ambos removidos: variável de marca só existe se um componente a usa; motor nunca inventa cor.

Novas lessons do pack gp3: registrar aqui com data; 2× recorrente → corrigir recipe e re-certificar.
