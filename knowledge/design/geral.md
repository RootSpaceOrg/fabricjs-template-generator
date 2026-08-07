# Design — conhecimento geral (vale para QUALQUER pack)

Camadas de conhecimento do designer, da base para o topo (o mais específico
vence): **este arquivo** → `packs/<slug>/` (tecnicas.md, exemplos/, tokens,
lessons.md) → dossiê da run. O que é lei mecânica está no CATALOG e nos gates;
aqui estão as leis de gosto que valem em todo estilo.

## Legibilidade (inegociável)

- Texto NUNCA sob decor, foto ou travessia — texto vive em background limpo.
- CTA, logo e foto de perfil sempre desobstruídos.
- Contraste de leitura em todo texto (o judge elimina por contraste, R6).
- Texto de leitura nunca cortado por fronteira de slide ou pelo canvas (R2);
  atravessar fronteira é privilégio de decoração/imagem/watermark.

## Hierarquia e respiro

- 1 elemento dominante por slide (headline OU foto OU número — não empate).
- Respiro deliberado pontua; slide >35% de área morta é defeito (R4) — a
  diferença entre respiro e área morta é intenção: o vazio aponta para o foco.
- Grid de 12: margens generosas (1 coluna nas laterais no mínimo), alinhamentos
  consistentes dentro do slide.

## Fita (a unidade de design)

- A fita é UMA peça: leitura contínua, fundos alternando (R3: mínimo 2 mudanças
  de fundo na fita), transições intencionais nas fronteiras.
- Elementos de travessia (fita-layer) criam continuidade: foto sobre a emenda
  de dois slides, decor cruzando, watermark varrendo. Sempre estáticos, sempre
  sobre backgrounds limpos dos DOIS lados.
- Variância é dever: duas gerações do mesmo pack nunca saem com o mesmo
  esqueleto — varie ordem, lados, quantidade de slides, presença de decors.

## Fotos e decors

- Foto editável vive inteira dentro de um slide; foto de continuidade
  (travessia) é estática e paisagem, com o sujeito perto da emenda.
- Decor = objeto do TEMA do post, gerado por post (nunca banco/estoque),
  fundo transparente, desfoque profundo NASCIDO NA GERAÇÃO (pós-processo de
  blur é proibido), inteiro no arquivo com margem nas 4 bordas.
- Decor se posiciona grande, cortado por uma borda do slide (ou da fita),
  com leve rotação — nunca pequeno e solto no meio do canvas.

## Slots da plataforma

- `professionalPhoto` usa o placeholder canônico do motor (o runtime troca pela
  foto real); pessoa/avatar desenhado no lugar é violação (R1).
- Elementos editáveis respeitam min/max de caracteres e fazem sentido para
  OUTRO profissional do mesmo nicho adaptar no editor.

## Cor da marca em caixas

Todo elemento de CAIXA CHEIA em cor de acento (tarja, pill de CTA, bloco,
overlay) leva `data-variable="primary"` — o conversor emite `fillVariableConfig`
e a caixa se recolore com a marca do usuário, como os fundos chapados. Acento
cravado sem variável é defeito: a peça inteira deve se vestir da primary.

## Miolo não é versão pobre da capa

Fita longa (5+ slides) tende a virar "capa caprichada + miolos de texto solto"
— defeito. O miolo REPETE A LINGUAGEM da capa em outra chave: os mesmos
recursos visuais (caixas, cartões, tarjas, colagens, sobreposição) reaparecem
carregando o conteúdo, variando qual deles domina cada slide.

Régua prática por tamanho de fita:
- **3 slides**: capa + 1 miolo + fechamento — o miolo pode ser mais direto.
- **5 slides**: pelo menos 2 miolos com "objeto de conteúdo" (cartão/caixa/
  destaque), nunca 3 slides seguidos só com texto no grid nu.
- **7+ slides**: alterne no mínimo 3 tratamentos diferentes ao longo do miolo
  (ex.: cartão empilhado → statement chapado → citação em caixa → lista em
  bloco), e repita o recurso-assinatura da capa pelo menos 2 vezes.

## Hierarquia de corpo vs display

O corpo de texto acompanha a escala do display: salto maior que ~2,5× entre
headline e body faz a explicação parecer legenda. Se a headline é 100px, o
corpo vive em 36–44px. Vale dentro de cartões e blocos também — texto em caixa
segue a mesma régua, não encolhe por estar "dentro de algo".

## CTA é ação, não enfeite

Pill/tarja de CTA só existe onde há ação real do leitor: capa (arrasta),
fechamento (salvar, comentar, compartilhar). Cartão de miolo com "botão" que
não leva a nada vira UI decorativa (o judge reprova em R5) e rouba autoridade
da peça. Rótulo de seção dentro de cartão = eyebrow/stamp.

## Caixa se ajusta ao conteúdo

Cartão/bloco de texto tem a altura do que carrega — nem sobrando (vazio
interno) nem faltando (texto encostando na borda). O padding do container é
inegociável nos QUATRO lados: se o conteúdo o consome, a caixa cresce. Caixa grande com texto no
topo e vazio embaixo é defeito (o vazio dentro de uma borda lê como erro, não
como respiro). Se sobra espaço: encolha a caixa, não espalhe o texto. Respiro
pertence ao slide (em volta da caixa), não ao interior dela.

## Texto transborda a célula (o gate não pega)

O conversor só rejeita sobreposição de ÁREAS declaradas — texto que estoura a
própria célula e invade a vizinha passa batido e só aparece no render. Régua:
headline display (100px+) cabe ~1 linha por linha de grid (112px); com 3 linhas
reserve 4 linhas de grid. Se o texto encavalar no render, aumente a área ou
corte a copy — nunca confie no gate para isso.

## Formato de copy pede tratamento visual

O framework escolhido (`knowledge/copy/frameworks.md`) tem consequência de
design — o designer lê o dossiê e responde a ele:

- **Listicle / passo-a-passo**: hierarquia visual IGUAL entre os itens (o
  leitor compara); numeração consistente.
- **Mito × verdade / erro → correção**: pares precisam de marcação simétrica
  (badge, cor, posição) — é o ritmo de revelação que segura o swipe.
- **Cheat-sheet**: densidade alta é o produto, mas exige hierarquia forte
  (agrupamento, pesos, respiro) para não virar muralha ilegível.
- **Antes/depois**: comparação lado a lado é lida instantaneamente — evite
  separar em slides distantes.
- **Case-study / vulnerável**: a peça pede foto/atmosfera, não infográfico.
