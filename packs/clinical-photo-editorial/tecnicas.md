# Técnicas — clinical-photo-editorial

Dinâmicas do estilo, destiladas dos vereditos (histórico em `lessons.md`).
São TÉCNICAS, não coordenadas: aplique com julgamento, variando entre
gerações. Exemplos em `exemplos/` (partida, nunca fôrma).

## Assinaturas (o que faz a peça ser DESTE pack)

1. Tipografia display GIGANTE na COR DA MARCA em duo-tom (a palavra-chave
   ganha o segundo peso via `data-variable-alpha`), entrelaçada com o cutout
   do profissional na capa — o texto cruza o FUNDO da figura, nunca o corpo.
2. Objetos do tema DESFOCADOS (bokeh de primeiro plano) como decoração
   assimétrica fundindo no papel neutro.
3. Composição assimétrica em camadas; pills outline; clean robusto.
4. **Arcos de circunferência em traço fino** ao fundo, cortados pelas bordas —
   a "profundidade de papel" da referência. Vêm de um SVG ao lado da fita
   (`arcos.svg`), porque `border-radius` não faz arco parcial: veja
   `exemplos/ref-capa.html`. Traço de 2–3px em `wm`/accent com opacidade baixa;
   é fundo, nunca compete com a leitura.

## Como este estilo resolve cada formato

O dossiê declara o **formato** de cada slide e o **papel** de cada pedaço
(`eyebrow` / `tese` / `apoio` / `itens`). Aqui está como o clinical trata cada
um. O tratamento é escolha sua — o que não é opcional é o conteúdo chegar
inteiro na página, com tese e apoio no MESMO bloco de leitura.

**Todo slide tem no mínimo DOIS elementos com peso**; headline sozinha em fundo
liso é slide inacabado (ver `knowledge/design/geral.md`).

| Formato que chega | Como o clinical resolve |
|---|---|
| `gancho` (capa) | `professionalPhoto` (placeholder canônico do motor) + tese `size="lg"` em duo-tom entrelaçada com o cutout + eyebrow/stamp + 1–2 decors com `data-overhang`. O apoio fica logo abaixo da tese, nunca no rodapé |
| `tese+ressalva` | slide chapado (`data-invert`): tese grande em paper + ressalva LOGO ABAIXO, mesmo bloco. Âncora: número gigante em `data-layer` ou decor |
| `enumerado` (2–3) | `ds-block` de acento com os itens, um por linha, + eyebrow. Se vier apoio junto, ele vai **acima** do bloco, colado ao eyebrow — nunca sobrando no rodapé |
| `passo` | foto do tema ocupando um terço/metade real + número + tese + apoio de 2–4 linhas. A foto é protagonista, não enfeite de canto |
| `comparacao` | dois blocos assimétricos no mesmo slide, o segundo em accent; ou par de fotos contínuas atravessando dois slides |
| `dado` / `citacao` | full-bleed + `data-overlay` + `ds-card data-elevated` compacto, dimensionado pelo texto e alinhado à esquerda |
| `cta` (fechamento) | `professionalPhoto` espelhando a capa + tese + apoio curto + `ds-cta` + logo |

## Esqueletos de miolo (exemplares, nunca fôrma)

Cada padrão é um HTML em `exemplos/` — a FONTE, renderável a qualquer momento
(`node engine/tools/build-exemplos.js clinical-photo-editorial` regera os JPGs).
São o ponto de partida do miolo enquanto a `reference.png`, que é uma capa, não
tiver companhia. **Componha livre**: varie, adapte, recombine. Duas fitas com o
mesmo esqueleto continuam sendo defeito.

| Padrão | Composição | Bom para | Cuidado |
|---|---|---|---|
| **capa** | arcos de circunferência em traço fino (SVG) cortados pelas bordas + `professionalPhoto` na metade direita + display duo-tom entrelaçando a figura + pill outline e CTA | abertura da fita | o duo-tom cruza o FUNDO da figura (o espaço entre cabeça e ombro, o ar em volta) — nunca o corpo no ponto de maior contraste: texto sobre jaleco branco fica ilegível |
| **cta** | espelha a capa: mesmos arcos, profissional à ESQUERDA e leitura à direita, com CTA e logo | fechamento da fita | a inversão é o que impede o último slide de parecer a capa repetida |
| **foto-metade-sangrando** | figura toma a metade direita inteira, do topo ao rodapé; leitura à esquerda; número grande de âncora | tese+ressalva, passo, dado | foto vertical com o sujeito no terço direito |
| **full-bleed-com-faixa** | slide todo é foto; texto numa faixa sólida no terço inferior, encostada em três bordas | tese+ressalva, citação, dado | com foto clara no rodapé a faixa precisa ser `data-tone="ink"` |
| **enumerado-numerado** | número grande + item, ritmo regular do topo ao rodapé — a lista É a composição | enumerado de 2–4 itens | é o tratamento certo de lista; não jogue bullets soltos numa caixa |
| **card-ancorado** | foto nos dois terços de cima, cartão `data-fit="end"` encostado na margem inferior | dado, citação, tese+ressalva | o `data-fit` é o que impede o cartão de esticar e criar vão |
| **display-com-decor** | tipografia gigante como protagonista, dois decors cortados pelas bordas | gancho, tese curta | exige tese de 3–5 palavras; com texto longo o efeito morre |
| **par-espelhado** | dois slides com a MESMA foto atravessando a emenda pela `.fita-layer`; leitura troca de lado | passo em 2 etapas, antes-depois, comparação | a foto só ocupa as colunas SEM texto; as coordenadas da `.fita-layer` são da FITA inteira (12 colunas por slide), não do slide |

### Como estes padrões se encaixam na fita

A tabela acima descreve slides ISOLADOS. Na fita eles convivem, e a escolha de
cada um depende do vizinho (ver `knowledge/design/geral.md` → "Cada slide
responde ao anterior"):

- **`foto-metade-sangrando` duas vezes seguidas é defeito** (veredito
  2026-08-09): uma com a foto à direita e a outra à esquerda lê como par
  espelhado quebrado. Se as duas metades se tocam na emenda, ou vira
  `par-espelhado` (a MESMA foto atravessando), ou o segundo slide muda de
  família — `enumerado-numerado`, `display-com-decor`, chapado.
- **Alternância saudável do miolo**: foto → chapado → cartão → foto. Nunca dois
  tratamentos com foto grande em sequência, a não ser como par declarado.
- **O par espelhado é um bloco de 2**, não dois slides — planeje-o no dossiê
  (duas etapas de uma mesma ideia), não improvise na composição.

**Formato que o pack resolve mal** (ver `comporta.resolve_mal` no `pack.json`):
enumerado com mais de 3 itens, tabela, número gigante acompanhado de texto
longo. Se o dossiê pedir isso, resolva com o tratamento mais próximo e registre
em `lessons.md` — não invente um layout que o estilo não tem.

**Onde o miolo desanda** (2026-08-08): o apoio desce para o rodapé e abre um vão
morto no meio do slide. Tese e apoio são um bloco só; o que fecha o slide por
baixo é CTA, logo ou decor — não texto de leitura.

## Técnicas de composição

- **Duo-tom entrelaçado (capa)**: headline `size="lg"` com span accent,
  `data-layer`, cruzando o cutout do profissional — texto e figura em camadas.
- **Par de fotos contínuas**: UMA foto paisagem (sujeito perto do centro) na
  `.fita-layer` sobre a fronteira de dois slides de miolo. Divisão EQUILIBRADA
  (40/60 no mínimo), foto GRANDE (faixa de rodapé ou meia-altura), sujeito
  perto da emenda, background limpo dos dois lados.
- **Decor voando**: decor com `data-overhang`, grande, cortado pela borda,
  rotação leve (10–20°). Capa 1–2; miolo 0–1; nunca sobre texto, CTA, logo ou
  professionalPhoto.
- **Full-bleed + overlay + card**: foto full-bleed, véu `data-overlay` e card
  compacto por cima — o slide de maior impacto; 1× por fita.
- **Fundos alternando**: papel neutro na maioria, 1 slide invertido (accent)
  como respiro — nunca fita monocromática.
- **Fechamento espelha a abertura**: o CTA leva o `professionalPhoto` como a
  capa — a fita abre e fecha com o profissional presente.

## Régua de tamanho (aprendida em 2026-08-08)

Este pack é **denso por natureza** (foto + texto + camadas). Fita longa só se
houver conteúdo real:

- **5–6 slides**: o tamanho natural do estilo.
- **7–8 slides**: só quando o tema tiver 4+ blocos de conteúdo distintos e
  pelo menos 3 tratamentos diferentes de miolo. Sem isso, faça 5 — fita curta
  densa é melhor que longa e rala.

## Regras de imagem (ver images.md para fórmulas)

- Fotos: clínicas, cinematográficas, **paleta neutra dessaturada** (a cor vem
  da marca, não da foto — ver images.md).
- **Pessoa = slot da plataforma.** O profissional é sempre
  `ds-slot data-slot="professionalPhoto"` com o placeholder canônico
  (`engine/assets/professional-photo-*.b64.txt`). Gerar avatar/ilustração de
  médico é violação R1 do judge.
- Decors: objeto do tema, transparente, desfoque profundo nascido na geração,
  inteiro com margem nas 4 bordas, gerado POR POST.

## O que já foi reprovado (não repetir)

- Formas abstratas (ds-shape) — a personalidade vem dos bokehs.
- Decor nítido, pequeno, solto no meio do canvas, ou de fundo chapado.
- Blur aplicado em pós-processo (PIL) — degrada; blur nasce na geração.
- Texto grudado em card sem respiro; bokeh sobre outras imagens.
- Duas gerações com o mesmo esqueleto (variância é dever).
- **Número/watermark gigante atrás de texto**: é CAMADA — sempre `data-layer`.
- **Avatar 3D/ilustrado no lugar do professionalPhoto** (2026-08-08).
- **Slide com headline e mais nada** — fundo liso ocupando o resto (2026-08-08).
- **Cartão grande com texto curto** — a caixa se ajusta ao conteúdo.
