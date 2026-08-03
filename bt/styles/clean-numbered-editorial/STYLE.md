---
style: clean-numbered-editorial
status: draft            # vira `certificado` só após o protocolo completo + aprovação do Gustavo
reference: reference.png # colar a imagem-âncora (carrossel branco numerado com acento vermelho)
familia: editorial clean / listicle expert
funil: meio (educação/autoridade); topo se o tema for erro/mito
slides: 6–10
---

# clean-numbered-editorial

Listicle de especialista em fundo claro: **um erro/ponto numerado por slide**, acento único vibrante, palavra-watermark gigante ao fundo, colagem leve de evidências (prints, fotos pequenas, carimbos). Denso mas respirado — autoridade sem peso.

## Tokens

| Token | Valor |
|-------|-------|
| Fundo | off-white `#F5F4F2` (LITERAL — nunca data-variable) |
| Acento | `data-variable="primary"` — no ref: vermelho `#E8291C`; números, setas, sublinhados, carimbos, blocos de destaque |
| Texto | near-black `#141414`; secundário `#5A5A5A` |
| Display | sans condensada bold UPPERCASE (Oswald/Archivo Expanded 700), 40–54px |
| Body | sans neutra 400 (Inter), 26–30px |
| Número do slide | `[N]` entre colchetes, no acento, 48–64px, topo do slide |
| Watermark | palavra-tema do slide em 200–300px, cinza `#E4E2DE` (~8% visível), atravessando o fundo (pode cruzar fronteira — dispositivo de continuidade) |
| Carimbos/badges | pill outline no acento, rotacionada -8° a +6°, texto UPPERCASE pequeno — máx 2 por slide, decoração editorial (não UI) |
| Evidência visual | 1 por slide de miolo: print emoldurado, foto P&B pequena, ou ícone-objeto; com marca ✓/✗ no acento quando couber |

## Papéis de slide (receitas)

### capa (slide 1)
- Número-total gigante no acento ("9") + título do listicle em 2–3 linhas UPPERCASE.
- `instagramProfilePicture` (avatar ~64px) + `instagramName`/`instagramHandle` na base.
- 1 elemento gráfico do acento (círculo/proibido/carimbo) meio-cortado pela borda.

### item (miolo — papel repetível 4–8×)
- `[N]` no acento no topo + headline do erro/ponto UPPERCASE 1–3 linhas.
- Body 2–4 linhas explicando; 1 trecho pode ganhar fundo do acento (bloco destacado, texto branco).
- Watermark da palavra-tema atrás; 1 evidência visual posicionada assimetricamente (alterna esq/dir entre slides).

### cta (último)
- Recap em 1 frase + pedido único (comentar palavra / salvar / seguir — conforme funil).
- Prova social leve como evidência (print de depoimento emoldurado) se disponível como imagem gerada conceitual.

## Slots

| Slot | Tipo | Limites |
|------|------|---------|
| `capa_total` | copy | número 1–2 chars |
| `capa_titulo` | copy | 40–80 chars, UPPERCASE |
| `item_headline` (por item) | copy | 25–70 chars, UPPERCASE |
| `item_body` (por item) | copy | 80–200 chars |
| `item_watermark` (por item) | copy | 1 palavra, 6–14 chars |
| `cta_recap` + `cta_pedido` | copy | 60–140 chars total |
| `item_evidencia` (por item) | imagem gerada | `data-bt-generate="<CONCEITO do item> como foto still editorial minimalista OU mockup de interface limpo, fundo neutro claro, sem texto legível"` |
| avatar/nome/handle | slots plataforma | `instagramProfilePicture`, `instagramName`, `instagramHandle` |

## Continuidade
- Watermark atravessando fronteiras (palavra começa num slide e termina no outro) — dispositivo principal.
- Sistema `[N]` + acento + carimbos = identidade que costura sem monotonia.
- Ritmo tonal: base clara constante com 1 slide de "respiro invertido" opcional (fundo do acento, texto branco) no meio da fita — bloco opcional do blueprint.

## Riscos conhecidos (validar na certificação)
- Densidade: R4 vigia área morta, mas o risco aqui é o oposto — poluição; máx 1 evidência + 2 carimbos por slide é regra dura.
- Watermark cruzando fronteira: conferir no slice que o corte cai bonito (ajustar tracking da palavra no blueprint).
- Prints/mockups gerados não podem imitar UI real de plataforma (Instagram/LinkedIn) a ponto de parecer print verdadeiro de terceiro.
