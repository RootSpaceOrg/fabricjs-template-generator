# Famílias estéticas — referência do gp2-html-designer

Escolha **uma** família no Passo 2 (mid-fi) e comprometa-se com ela ao longo do carrossel inteiro. Cada família é uma combinação coerente de tipografia + paleta + composição. As sugestões são pontos de partida, não jaula: adapte ao segmento e à referência do brief.

Anote a escolhida em `notes.md`.

---

## Editorial clínico

Visual de revista médica premium. Bom para marcas técnicas ou reguladas que querem se posicionar como autoridade (saúde, finanças, educação, jurídico).

- **Tipografia:** display serifa moderna (Playfair Display, DM Serif Display) + body sans neutra (Inter, DM Sans).
- **Paleta:** brancos cremosos (#F7F3EE), pretos profundos (#1A1A1A), um único acento de marca em pontos cirúrgicos.
- **Composição:** muita respiração, grades implícitas de 12 colunas, texto justificado quando faz sentido, fios horizontais finos como divisores.
- **Movimento memorável:** numeração editorial gigante no canto, eyebrow em caixa alta com tracking aberto, fios horizontais como divisores.

## Premium minimal

Estética Apple-like, refinada. Bom para estética/bem-estar, psicologia premium.

- **Tipografia:** sans geométrica leve (Manrope, DM Sans, Inter weight 300-500) sem display contrastante.
- **Paleta:** brancos puros, cinzas quentes (#F5F5F0), um único acento de marca em volume mínimo (< 10% do canvas).
- **Composição:** assimetria deliberada, blocos amplos de respiração, tipografia centralizada vertical mas alinhada à esquerda.
- **Movimento memorável:** uma linha vertical fina dividindo eyebrow e título, ou um único elemento gráfico minimalista (círculo, triângulo) repetido.

## Bold educacional

Visual de conta de educação no Instagram (Anitta-ensina-tudo, escolas modernas). Bom para conteúdo informativo com hook forte.

- **Tipografia:** display sans condensada pesada (Anton, Bebas Neue, Inter 800-900) + body sans neutra.
- **Paleta:** primary saturada dominante (60%+ do canvas), neutros, sem secondary geralmente.
- **Composição:** título oversized cortando a margem, sangrias deliberadas, fundo de cor sólida primary.
- **Movimento memorável:** título oversized cortando bordas, numeração de slide enorme, contraste agressivo entre slides.

## Soft wellness

Estética spa/yoga/lifestyle. Bom para marcas com apelo emocional e visual orgânico (bem-estar, gastronomia natural, moda slow, turismo).

- **Tipografia:** display serifa orgânica (Cormorant Garamond, Crimson Pro) + body sans suave (Lato, Open Sans, Nunito 300-400).
- **Paleta:** tons terra (bege, oliva, ferrugem suave), brancos quentes (#FAF8F5), acentos primary em verde-musgo / coral pessego / vinho suave.
- **Composição:** respiração ampla, alinhamentos centrais aceitáveis, fotos com tratamento natural (sem filtro frio).
- **Movimento memorável:** elementos orgânicos (folhagem em ilustração simples, textura de papel sutil, traço manual fino).

## Magazine authority

Vibe Vogue/Monocle/Wired. Bom para conteúdo de autoridade com personalidade.

- **Tipografia:** display serifa de personalidade (Playfair Display 900, DM Serif Display) ou condensada de alto contraste + body sans editorial (Source Sans, Inter).
- **Paleta:** preto + branco + um único acento forte. Sem cinza intermediário.
- **Composição:** grades pesadas, alinhamentos rigorosos, cabeçalhos com hierarquia explícita (eyebrow tiny + título gigante).
- **Movimento memorável:** eyebrow micro com tracking enorme acima do título, indicador de página/seção, número de issue.

## Data-dense profissional

Visual de relatório/whitepaper/insight. Bom para laboratórios, conteúdo técnico.

- **Tipografia:** sans funcional (IBM Plex Sans, Inter) display + body, com mono pequeno para números (IBM Plex Mono).
- **Paleta:** branco + grafite (#222) + primary técnica (azul-petróleo, verde-laboratório). Secondary geralmente em vermelho-acento para alertas/destaque.
- **Composição:** colunas explícitas, labels minúsculos sobre números/dados grandes, fios para separar zonas.
- **Movimento memorável:** chamada de dado em tamanho gigante com label minúsculo acima, indicadores de tendência (setas finas).

## Luxury refinado

Visual de luxo silencioso (silent luxury). Bom para marcas premium de nicho (joalheria, arquitetura, moda alto padrão, serviços exclusivos).

- **Tipografia:** serifa de alto contraste (Bodoni Moda, Cormorant SC) + sans extra-light (Manrope 200-300).
- **Paleta:** off-whites, dourados muito sutis, pretos profundos. Sem cor saturada.
- **Composição:** muita respiração, alinhamentos centrais quando faz sentido, espaço deliberado entre elementos.
- **Movimento memorável:** monograma/iniciais como elemento gráfico, fios dourados finos, tipografia em itálico discreto.

## Brutalist direto

Visual direto-resposta com personalidade marcada. Bom para promoções, datas comemorativas, posts de venda.

- **Tipografia:** display ultra-pesada (Arial Black, Impact, Bebas Neue) + body sans direta.
- **Paleta:** primary saturada brutalista (amarelo, magenta, vermelho), pretos pesados, neutros mínimos.
- **Composição:** blocos sólidos de cor, contrastes extremos, alinhamentos firmes à esquerda, sem refinamento.
- **Movimento memorável:** bloco gigante de cor com texto branco/preto chapado, CTA inegável (botão grande), repetição de elemento gráfico.

---

## Stacks de fonte safe (offline)

Quando o ambiente não permite Google Fonts e você precisa de fallback do sistema:

| Família estética | Display | Body |
|------------------|---------|------|
| Editorial clínico / Magazine | Georgia, "Times New Roman" | Aptos, "Segoe UI" |
| Premium minimal | Aptos Display, Aptos | Aptos, "Segoe UI" |
| Bold educacional | "Arial Black", Impact | Aptos, "Segoe UI" |
| Soft wellness | Georgia, "Trebuchet MS" | "Segoe UI", "Helvetica Neue" |
| Luxury refinado | Georgia, "Times New Roman" | "Trebuchet MS", "Segoe UI" |
| Brutalist | "Arial Black", Impact | Arial, "Helvetica Neue" |

Quando possível, **importe Google Fonts** via `<link>` no `<head>` — a qualidade é muito maior que os stacks do sistema. O editor resolve fontes na carga.

---

## Anti-padrões a evitar (qualquer família)

- **Uma única família genérica** (Inter/Arial/Roboto) cobrindo display + body. Sempre pareie.
- **Tudo centralizado** sem intenção compositiva.
- **Card spam**: caixas com `border` + `border-radius` + `box-shadow` repetidas como decoração.
- **Nested cards**: cartão dentro de cartão dentro de cartão.
- **Gradientes default** roxo→rosa sem razão.
- **Cinzas frios** (#CCCCCC) em vez de cinzas quentes (#F0EBE3) — frios envelhecem o design.
- **Border-radius `50%`** em fotos quando o brief não pediu avatar (preferir crop editorial retangular).
- **Shadows pesadas** (`box-shadow: 0 20px 60px rgba(0,0,0,0.3)`) — preferir sutis ou nenhuma.

Se o auto-check do Passo 2 acusar algum desses, é o tipo de coisa que justifica refazer.
