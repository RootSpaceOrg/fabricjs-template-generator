# Catálogo de Style Presets (estilos nomeados)

Vocabulário compartilhado entre `gp2-request-interpreter` (detecta o gatilho), `gp2-art-director` (trava o vocabulário visual), `gp2-html-designer` (executa respeitando as restrições hard) e `gp2-html-reviewer` (confere).

Um **style preset** é uma direção de arte nomeada e opinativa que o usuário pode ativar explicitamente por palavra-chave. Quando ativo, o preset **sobrescreve** decisões que normalmente seriam livres (escolha de família estética, alternância de background, moves) — é uma restrição hard, não uma sugestão.

**Diferença para "aesthetic family":** a família estética (`gp2-html-designer/references/aesthetic-families.md`) é uma escolha **livre** do art-director quando não há direção forte. Um style preset é uma escolha **forçada pelo usuário** que trava o conjunto inteiro (família + paleta + background + arquétipos + moves) antes do art-director começar.

**Regra geral:** sem gatilho de estilo no brief (`## Estilo: nenhum`), nenhum preset se aplica e a pipeline se comporta como sempre. Presets são opt-in.

---

## `editorial-premium`

Destilação generalizada (multi-nicho) de uma direção de arte editorial premium — revista médica/autoridade, clean, sofisticada. Inspirado num prompt de direção de arte clínica, mas **sem amarrar a nenhum nicho** (não há "aparelho laser", jargão clínico nem ícone de saúde). Funciona para qualquer marca premium que queira posicionamento editorial.

### Gatilhos (detectados pelo interpreter)

Substring, case-insensitive, no pedido do usuário:

- `laserpro`
- `estilo laserpro`
- `modo laserpro`
- `editorial premium`
- `estilo editorial premium`

Qualquer um → `estilo: editorial-premium` no `brief.md`.

### Regras hard do preset

| Dimensão | Regra |
|----------|-------|
| **Fundo** | **Sempre claro** — off-white quente (`#FFFFFF` a `#FAF8F5`). **Proibido** slide com fundo escuro (DARK) ou fundo brand sólido full-bleed. Isto **sobrescreve** a alternância de background da sequência narrativa do brief. |
| **Paleta** | **1 acento de marca** (primary) usado em pontos cirúrgicos (eyebrow, fio, número, palavra-chave, botão CTA). Secondary **opcional**, só como destaque de palavra-chave inline. Neutros = cinzas suaves **quentes** apenas de apoio. Nunca cinza frio (`#CCC`/`#999`). |
| **Gradientes** | **Proibidos gradientes fortes.** Sem `data-darken` pesado. No máximo overlay sutil. Nunca brand hex em `linear-gradient`. Sombras sempre sutis (`rgba(0,0,0,0.04–0.10)`) ou nenhuma — nunca sombra pesada. |
| **Tipografia** | Display condensada/editorial peso alto (700–900) + body sans neutra. **Headlines MUITO grandes.** Kerning negativo no display (−1% a −3%). Eyebrow UPPERCASE com tracking aberto (+8% a +20%). Possibilidade de palavras-chave gigantes e texto vertical. |
| **Hierarquia** | **1 elemento dominante por slide.** Leitura em < 3s. Sem competição entre dois focos visuais no mesmo slide. |
| **Respiro** | Margem útil **ampla (≥ 80px)** em todas as bordas. Muito espaço em branco deliberado. **Evitar** bloco de texto centralizado denso. |
| **Composição** | Assimetria elegante, colunas, fios finos (1–3px), blocos desalinhados estrategicamente. **Proibido:** "card de Canva", card-spam, nested cards, slides genéricos, caixas comuns com border+radius+shadow. |
| **Foto profissional / avatar** | Reservar slot `professionalPhoto` (B1) na **capa (slide 1)** e na **última lâmina (CTA)**. **Nunca centralizado** — sempre numa lateral. Generalizado: cutout PNG editorial, sem elementos de nicho. |
| **Logo** | Capa + CTA, numa extremidade (default canônico já existente). |

### Allowlist de arquétipos (de `COMPOSITIONS.md`)

Use **apenas** estes; cada um já é compatível com fundo claro e respiro amplo:

- **Capa:** `A1-hero-split`, `A10-headline-massive-solo`, `A12-photo-with-floating-caption`
- **Miolo:** `A3-editorial-eyebrow-stack`, `A4-quote-centered-fios`, `A7-data-spotlight`, `A13-editorial-numbered-context`
- **CTA:** `A6-cta-button-anchored` — **com a ressalva**: o fundo do A6 normalmente é brand sólido full-bleed; sob este preset, o CTA permanece **fundo claro** e o brand aparece só no botão/acentos. Documentar esse desvio no `visual-plan.md`.

**Banidos** sob este preset (exigem fundo escuro/brand full-bleed como dominante ou gesto agressivo): `A2-full-bleed-text-bottom`, `A14-rich-hero-cutout` como dominante de cor brand.

A regra de diversidade composicional (≥2/≥3 arquétipos) continua valendo.

### Allowlist de carousel moves (de `CAROUSEL_MOVES.md`)

Escolha **1–2** entre:

- `M8-fio-tipografico` — fio fino editorial (o mais seguro, casa perfeito).
- `M9-edge-numbering` — numeração discreta `01/07` no rodapé.
- `M2-numero-ostentatorio` — número grande **discreto** (cor neutra de baixa saturação ou primary sutil, não bloco de cor cheio).
- `M5-quote-pull` — slide de citação tipográfica massiva (respiro).

**Evitar** sob este preset (quebram o "minimalismo clínico"): `M7-color-block-shift`, `M10-headline-overflow`, `M3-bleed-entre-slides` agressivo. `M4-cta-arrow-ritualistico` é aceitável apenas **discreto** (seta fina neutra), não como bloco.

### O que o preset sobrescreve do comportamento default

| Comportamento default | Sob `editorial-premium` |
|-----------------------|--------------------------|
| Art-director escolhe família estética livremente | **Travado** em editorial premium (display editorial + body sans, paleta clara, 1 acento). |
| Alternância de background por sequência (LIGHT/DARK/Brand) | **Sobrescrita** — todos os slides claros. Sem DARK, sem Brand full-bleed. |
| CTA (A6) com fundo brand sólido full-bleed | Fundo **claro**; brand só no botão/acentos. |
| Art-director pode escolher qualquer A*/M* | Restrito às allowlists acima. |

### Interação com Modo / Fidelidade

O preset é **ortogonal** ao Modo (`free`/`reference-driven`) e à Fidelidade (`recreate`/`inspired`/`free`):

- **Free mode + preset:** art-director deriva paleta do segmento mas obedece "fundo sempre claro, 1 acento".
- **Reference-driven mode + preset:** o **preset tem prioridade** sobre direção conflitante da referência. Ex: referência com fundo escuro ou gradiente forte → o preset força fundo claro e remove o gradiente. O art-director ainda herda da referência o que **não** conflita (ex: escolha tipográfica, posição de elementos), mas documenta cada conflito resolvido a favor do preset em `## Notas para o designer`.

---

## Como adicionar um novo preset

1. Adicione uma seção `## <slug>` aqui com gatilhos + regras hard + allowlists + tabela de sobrescritas.
2. Adicione o slug à tabela de detecção em `gp2-request-interpreter/SKILL.md → ## Estilo`.
3. Nenhuma outra skill precisa mudar — o art-director lê este arquivo e o designer/reviewer herdam via `visual-plan.md → ## Estilo aplicado`.
