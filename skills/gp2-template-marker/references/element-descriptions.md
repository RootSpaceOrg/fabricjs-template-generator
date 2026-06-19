# Element descriptions — catálogo canônico para `data-te-description`

Catálogo de descriptions canônicas por papel narrativo. O marker consulta este arquivo na hora de emitir `data-te-description` em cada `data-template-element="true"`.

## Por que existe

A `description` que você escreve aqui é injetada **literal** no prompt do LLM gerador de copy do `app-lambda-ai-idea-to-template` (`copy_processor.py:_format_elements_context`). O LLM recebe assim:

```
## Página 1 — mensagem-chave: <vinda da pipeline na hora da geração>
- [Index: 5] [TIPO=textbox] <sua description aqui> [maxChars: 41]
```

Description vaga ("Eyebrow editorial") deixa o LLM adivinhar o formato. Description estruturada com formato e exemplos guia o LLM para output consistente entre slides.

**Template é cross-vertical por design.** Pode ser usado em saúde, pet, beleza, fitness, educação, negócios, gastronomia — qualquer vertical suportado pela plataforma. Descriptions presas em um vertical (ou no conteúdo do placeholder atual) quebram o template nos outros usos.

## Anatomia da description (5 componentes)

Toda description segue a fórmula:

```
<role narrativo>; formato '<máscara>'; <bound 1>; <papel na composição>; <bound 2>; ex: '<ex1>', '<ex2>', '<ex3>'
```

| Componente | O que é | Exemplo |
|------------|---------|---------|
| **Role narrativo** | Função do elemento na lâmina | "Eyebrow editorial da lâmina" |
| **Formato** | Máscara da string em aspas simples | "formato 'NN / TEMA'" |
| **Bounds** | Restrições **estruturais/de formato** — linhas, caixa, pontuação, presença de número. **NUNCA contagem de caracteres** (isso é o `data-te-max-chars`) | "1 frase em 2 linhas" + "TEMA em CAPS" |
| **Papel na composição** | Quem o elemento é dentro da estrutura da lâmina (índice/contagem de slots repetidos, relação pai/filho, lado/ordem) | "item 1 de 3 de uma lista sequencial", "cabeçalho que governa a lista" |
| **Exemplos** | 3 exemplos curtos cobrindo variação saudável de formato (cross-vertical — nunca presos ao nicho do template atual nem ao conteúdo do placeholder) | "ex: '01 / DOR', '03 / O ESTUDO', '07 / CTA'" |

> ⚠️ **O limite de caracteres mora no `data-te-max-chars`, não na description.** Nunca escreva `até 30 chars` / `30-60 chars` / `máximo N caracteres` na `data-te-description` — o número da prosa briga com o `data-te-max-chars` (que é a fonte de verdade da validação) e quase sempre diverge. Os bounds da description são de **forma** (`1 linha`, `em CAPS`, `sem ponto final`); o **comprimento** é do `data-te-max-chars`. Os exemplos deste catálogo já seguem isso.

**Tamanho da própria description**: mantenha-a enxuta (≈200-300 caracteres). Cada description vai pra cada elemento de cada template no prompt do LLM — pesar tokens importa. (Isto é sobre o tamanho da *description*, não um bound do campo.)

### Componente "Papel na composição" (o que evita o "genérico ruim")

Este componente é o que diz **quem o elemento é dentro da lâmina**, não só o que ele é em abstrato. Sem ele, um checklist de 3 itens sai com 3 descriptions idênticas e o LLM downstream não sabe que formam uma sequência ordenada.

**É obrigatório sempre que o slot se repete na mesma lâmina** (itens de lista, células de grade, passos de tutorial, lados de comparação). É **recomendado** quando o elemento tem relação pai/filho clara. Para slots únicos (um título de capa, um único CTA), pode ser omitido.

Frases canônicas (use estas, derive do passo 3c do marker):

| Padrão da lâmina | Frase do papel na composição |
|------------------|------------------------------|
| Checklist / lista numerada | `cabeçalho que governa a lista` (no título) · `item N de M de uma lista sequencial` (em cada item) |
| Grade / bento | `célula N de M de uma grade` |
| Comparação | títulos de coluna: `lado A da comparação` · `lado B da comparação` · veredicto: `veredicto após A e B`. **Bullets dentro de uma coluna**: combine lado + índice → `item N de M de uma lista sequencial (lado A da comparação)`. Cada lado é uma sequência própria (lado A: item 1..M; lado B: item 1..M) |
| Passo-a-passo / tutorial | `passo N de M` |
| Dado + caption | `número em destaque` · `legenda que explica o número acima` |
| Capa | (geralmente omitido — slot único; use só o role narrativo) |

**Quando há índice, adicione um micro-hint da função na progressão** quando ele agrega (`item 1 de 3 — abre a progressão`, `item 3 de 3 — fecha com o próximo passo`). Não invente função onde os itens são genuinamente intercambiáveis — aí basta `item N de M`.

## Anti-patterns — descriptions que QUEBRAM o LLM downstream

Antes de escrever qualquer `data-te-description`, verifique se você está caindo em um desses anti-patterns:

| Anti-pattern | Por que quebra | Exemplo ruim | Exemplo correto |
|-------------|----------------|--------------|-----------------|
| **Prosa descritiva sem fórmula** | Sem formato, sem estrutura, sem exemplos — output inconsistente entre slides | `"Slide 4 título: texto neutro e adaptável para qualquer nicho, com linguagem concreta e sem jargão."` | `"Título da lâmina intermediária; formato afirmação direta OU inversão; 1 frase em 2 linhas; ex: 'O detalhe que ninguém vê', 'Pequeno ajuste, grande efeito', 'Resultado não é só número'"` |
| **Role sem exemplos** | Sem exemplos, o LLM adivinha o estilo — vira inconsistência | `"Eyebrow editorial da lâmina; rótulo curto de seção"` | `"Eyebrow editorial; formato 'NN / TEMA'; em CAPS; ex: '01 / PARTE UM', '03 / O MÉTODO', '07 / PRÓXIMO PASSO'"` |
| **Número de chars na description** | Briga com o `data-te-max-chars` (fonte de verdade da validação) e quase sempre diverge — o LLM segue o número da prosa e a copy é rejeitada | `"Título; 1 frase; até 60 chars; ex: ..."` | `"Título; 1 frase em 2 linhas; ex: ..."` (comprimento vem do `data-te-max-chars`) |
| **Exemplos do vertical atual** | Template vai ser usado em dezenas de verticais — exemplos amarrados a um vertical travam o LLM nos outros | `"ex: '01 / FISIOTERAPIA', '03 / COLUNA CERVICAL'"` (template de saúde) ou `"ex: 'ração premium', 'banho e tosa'"` (template de pet) | `"ex: '01 / O DIAGNÓSTICO', '03 / O MÉTODO', '07 / PRÓXIMO PASSO'"` (cross-vertical) |
| **Description que copia o placeholder** | O placeholder (texto/imagem que o designer colocou pra preencher o slot) é só preview visual — não dita o conteúdo real. Descrever o placeholder amarra o LLM nele | Placeholder é foto de café numa mesa → `"formato foto de processo, mesa ou objeto; sem pessoa em destaque; ex: 'mesa organizada', 'objeto em detalhe'"` | `"Imagem de apoio contextual; tema reflete a mensagem-chave do slide; estilo editorial; ex: 'close de mãos em ação', 'ambiente do contexto', 'still life relacionado ao tema'"` |
| **Bounds inventadas a partir do placeholder** | "Sem pessoa em destaque", "foto noturna", "objeto em plano fechado" — restrições derivadas do placeholder atual que travam o template nos outros usos | `"sem pessoa em destaque"` (porque o placeholder não tem pessoa) | Bound real: `"editorial natural; sem texto na imagem; sem watermark"` (técnica, não temática) |
| **ex1 genérico ignorando o texto real** | O primeiro exemplo deve derivar do texto real no HTML (generalizado) — inventar do zero descarta a melhor pista de **formato/comprimento**. Mas só usa o texto real como base de formato, não de tema | Texto real: `"Seu conhecimento clínico está virando pacientes?"` → ex1 inventado: `"Sua ideia ficou clara?"` (perdeu o formato pergunta longa) | ex1 derivado: `"Seu conhecimento está virando resultados?"` (mantém formato pergunta + comprimento, generaliza vertical) |
| **Título do template como description** | A description é o prompt para o LLM gerar copy, não uma label do elemento | `"Título do slide sobre mitos de produtividade"` | `"Título da lâmina intermediária; formato afirmação que desmonta crença; ..."` |
| **Slots repetidos na mesma lâmina com string idêntica** | Item 1, 2 e 3 de um checklist com a mesma description — o LLM não sabe que formam uma sequência ordenada, nem quantos são, nem qual abre/fecha. Diferente do caso cross-slide, aqui o LLM **não** tem contexto separado para diferenciar | 3 itens com `"Texto editável de apoio; formato frase curta; ex: ..."` igual nos três | Role/formato/exemplos compartilhados, mas papel na composição varia: `"... item 1 de 3 de uma lista sequencial — abre a progressão; ..."` / `"... item 2 de 3 ...; ..."` / `"... item 3 de 3 — fecha com o próximo passo; ..."` |

**Regra de ouro:** se você remover a description e o LLM não souber o *formato*, o *tamanho*, o *estilo* e — em slots repetidos — *qual posição na sequência* o elemento ocupa, a description está errada. E se a description só funciona porque o usuário vai escrever sobre o mesmo tema do placeholder — também está errada.

---

## Regras invioláveis

1. **Exemplos são cross-vertical.** Mistura intencional entre nichos: um de serviço/negócios, um de bem-estar/lifestyle, um de objeto/conceito. Nunca 3 exemplos do mesmo vertical (saúde, pet, beleza). Nunca exemplos que reciclam o placeholder atual. Template vai ser usado em dezenas de verticais; descriptions são reutilizáveis.
2. **Role descreve função, não conteúdo.** "Imagem de apoio contextual da lâmina" é função. "Foto de mesa com objetos de trabalho" é conteúdo do placeholder — não vai pra description.
3. **Bounds são técnicas/estruturais, não temáticas — e nunca contagem de char.** `"2 linhas"`, `"em CAPS"`, `"sem texto na imagem"`, `"editorial natural"` — sim. `"até 60 chars"` — **não** (mora no `data-te-max-chars`). `"sem pessoa"`, `"foco em objeto"`, `"vista de cima"` — não (a menos que o slot tenha aspect ratio que **realmente** exija esse enquadramento).
4. **Formato e conteúdo são coisas diferentes.** `formato 'NN / TEMA'` define a estrutura. `ex:` mostra como aplicar. Nunca escrever `formato 'NN / nutrição'` (mistura).
5. **3 exemplos é o sweet spot.** 1 vira regra rígida. 5+ vira ruído. 3 cobrem variação saudável (curto/médio/longo, ou close/médio/aberto para imagens).
6. **Mesma description para slots equivalentes EM SLIDES DIFERENTES — mas não para slots repetidos NA MESMA lâmina.** Eyebrow no slide 1 e eyebrow no slide 5 recebem **a mesma string** (o LLM diferencia pelo contexto da página, que ele já vê separadamente). Já item 1, item 2 e item 3 de um checklist **na mesma lâmina** compartilham role/formato/exemplos mas têm o componente `<papel na composição>` distinto (`item 1 de 3` / `item 2 de 3` / `item 3 de 3`) — aqui o LLM não tem contexto separado e a sequência só existe na description.
7. **Quando em dúvida, escolha a description menor do catálogo** em vez de inventar um role novo.

---

## Catálogo

### Eyebrow numerado

Pequeno rótulo acima do título com numeração sequencial. ALL CAPS. Geralmente em cor primary brand. Movimento memorável comum em estética editorial e magazine.

```
Eyebrow editorial da lâmina; formato 'NN / TEMA' onde NN é o número
sequencial do slide (01, 02, 03...) e TEMA é categoria curta em CAPS;
 total; ex: '01 / O PROBLEMA', '03 / O MÉTODO',
'07 / PRÓXIMO PASSO'
```

### Eyebrow simples (sem numeração)

Rótulo categórico curto, sem número. ALL CAPS. Categoriza o tema do slide ou do post.

```
Eyebrow categórico; formato 'TEMA EM CAPS' sem numeração; rótulo curto
que categoriza o slide; ex: 'EM 5 PASSOS',
'O QUE FAZER', 'TEMA CENTRAL'
```

### Hook do Slide 1

Primeira frase do carrossel. Mata ou salva o engagement. Geralmente serif italic display em 2-3 linhas. Uma das 5 fórmulas: pergunta provocativa, afirmação polêmica, número + benefício, resultado concreto, inversão de expectativa.

```
Hook principal do carrossel (slide 1); formato pergunta provocativa OU
afirmação que gera curiosidade OU número + benefício; 1 frase em 2-3
linhas; ex: 'O que você faz quando o método não funciona
mais', '5 sinais de que seu negócio pede atenção', 'O detalhe que
ninguém te conta na hora de começar'
```

### Subtítulo de apoio ao hook (slide 1)

Linha curta abaixo do hook que complementa a promessa. Sans-serif body.

```
Subtítulo de apoio ao hook do slide 1; formato frase corrida que
complementa a promessa; 1 linha; ex: 'Um guia em 5 passos
práticos', 'Baseado em casos reais de clientes', 'O que ninguém te
ensinou ainda'
```

### Título de slide intermediário (subtítulo da lâmina)

Headline de slide do miolo. Geralmente serif italic em 2 linhas. Marca a transição/conceito do slide.

```
Título da lâmina intermediária; formato afirmação direta OU pergunta
curta OU inversão de expectativa; 1 frase em 2 linhas;
ex: 'O detalhe que ninguém vê', 'Pequenos ajustes, grandes mudanças',
'Por que isso funciona?'
```

### Corpo educativo (texto longo do miolo)

Parágrafo explicativo do slide. Sans-serif body, multi-linhas. Conceito ou evidência.

```
Corpo educativo da lâmina; formato 1 parágrafo de 3-4 linhas curtas
explicando o conceito do slide; tom acessível sem
jargão; ex: 'O método que parece simples só funciona quando os
fundamentos estão no lugar. Aqui está o que costuma estar faltando
quando o resultado some.'
```

### Bullet de lista educativa

Item curto de uma lista (Listicle, Tutorial). Geralmente sans-serif weight 600 na primeira palavra.

```
Item de lista educativa; formato '<verbo|substantivo curto>: <explicação
em 1 linha>' OU somente afirmação curta; ex: 'Comece
pequeno: 1 ação concreta por dia', 'Constância vale mais que
intensidade', 'Revise o que funcionou na semana'
```

### Cabeçalho de lista (título que governa um checklist/grade)

Título que **introduz e governa** uma lista de N itens na mesma lâmina (checklist, listicle numerado, grade). Diferente de um título de capa ou de miolo: o role aqui inclui que ele encabeça itens abaixo. Use o componente `<papel na composição>` = `cabeçalho que governa a lista de N itens abaixo`.

```
Título da lâmina de checklist; formato afirmação que introduz uma lista
de verificação OU pergunta que a lista responde; 1 frase em até 2 linhas;
cabeçalho que governa a lista de N itens abaixo; ex: 'Use
este roteiro antes de começar', 'Confira antes de publicar', 'O que
validar em cada etapa'
```

### Item de checklist / lista numerada (slot repetido)

Cada item de uma lista enumerada na **mesma** lâmina. **Os N itens compartilham role, formato e exemplos — só o componente `<papel na composição>` muda** (`item N de M de uma lista sequencial`). Adicione o micro-hint de progressão quando agrega (`abre a progressão`, `fecha com o próximo passo`); omita se os itens são intercambiáveis.

```
Item de checklist; formato pergunta curta de verificação OU instrução
objetiva; 1 linha; item N de M de uma lista sequencial;
ex: 'Defini o objetivo principal?', 'O ambiente está pronto?',
'Revisei o resultado antes de publicar?'
```

Aplicado a 3 itens (note só o trecho `item N de M ...` mudando):
- Item 1: `... ; item 1 de 3 de uma lista sequencial — abre a progressão; ...`
- Item 2: `... ; item 2 de 3 de uma lista sequencial — desenvolve o critério central; ...`
- Item 3: `... ; item 3 de 3 de uma lista sequencial — fecha com o próximo passo; ...`

### Célula de grade / bento (slot repetido)

Cada célula de uma grade (A11-bento-2x2). Mesma lógica do item de checklist, mas o papel é `célula N de M de uma grade`. Células de grade costumam ser mais intercambiáveis que itens de checklist — geralmente sem micro-hint de progressão.

```
Texto de célula de grade; formato rótulo curto OU frase de 1 linha;
 célula N de M de uma grade; ex: 'Atendimento próximo',
'Resultado comprovado', 'Processo transparente'
```

### Comparação — colunas A vs B (slots repetidos por lado)

Lâmina A9: dois lados paralelos (`O RECURSO | A DECISÃO`, `ANTES | DEPOIS`, `MITO | FATO`), cada um com seu título de coluna e N bullets. **É o padrão que mais sai errado**: marcado como um único checklist, os 2N bullets recebem `item N de 2N` (contagem errada) ou índices que reiniciam (`1,2,3,1,2,3`) sem dizer a que lado pertencem. O LLM downstream então mistura os lados e a copy perde sentido.

**Regra:** cada lado é uma **sequência própria**. Os títulos de coluna levam `lado A da comparação` / `lado B da comparação`; cada bullet combina **lado + índice dentro daquele lado**.

Título da coluna A:
```
Título de coluna comparativa; formato categoria curta em CAPS; 1 linha;
lado A da comparação; ex: 'O RECURSO', 'ANTES', 'O MITO'
```
Título da coluna B:
```
Título de coluna comparativa; formato categoria curta em CAPS; 1 linha;
lado B da comparação; ex: 'A DECISÃO', 'DEPOIS', 'O FATO'
```
Bullet da coluna A (cada um — só muda o índice; M = nº de bullets **daquele lado**, não o total):
```
Item de coluna comparativa; formato frase curta de 1 linha; item 1 de 3
de uma lista sequencial (lado A da comparação); ex:
'Critério objetivo', 'Passo verificável', 'Sinal claro'
```
Bullet da coluna B: idêntico, trocando `lado A` → `lado B` e o índice. Veredicto/fechamento (se houver) usa o role de corpo educativo + `veredicto após A e B`.

> **O audit reprova (FAIL)** quando um slide parece comparação (slots paralelos ou índices reiniciando) mas nenhuma description usa `lado A/lado B`. Sempre marque os dois lados.

### Dado numérico (prova social)

Número grande de destaque. Display grande, geralmente serif italic. 1 número por slide.

```
Dado de prova social; formato 'NN%' OU 'NNx' OU número absoluto sem
unidade; máximo 1 número visível; ex: '73%',
'2.5x', '8 sem'
```

### Caption de dado

Legenda do dado numérico. Sans-serif body, multi-linhas. Explica o significado do número.

```
Legenda do dado numérico; formato frase corrida começando em minúscula;
explica em 1-2 linhas o significado do número; ex: 'dos
clientes relataram melhora significativa em poucas semanas', 'mais
rápido do que métodos convencionais segundo estudos recentes'
```

### Pull-quote / citação

Trecho de fala de cliente, autoridade ou frase de impacto. Geralmente entre aspas tipográficas, serif italic, com aspa decorativa visível.

```
Citação de impacto; formato frase entre aspas em 1ª pessoa OU
afirmação forte sem aspas; 1-2 linhas; ex: 'Eu não sabia
que tinha solução', 'A diferença foi sentir resultado de verdade',
'Voltei a confiar no processo'
```

### CTA principal (último slide)

Chamada de ação final. Verbo no imperativo + objeto direto. Display médio.

```
CTA principal do último slide; formato verbo no imperativo + objeto
direto; 1 frase em 2-3 linhas; ex: 'Agende sua primeira
conversa', 'Solicite uma avaliação gratuita', 'Fale comigo no
WhatsApp'
```

### Linha de contato (telefone, link, handle)

Suporte ao CTA com canal de contato. Sans-serif body pequeno.

```
Linha de contato no slide CTA; formato '<canal> <valor>' OU somente
valor formatado; ex: 'WhatsApp (11) 9 0000-0000',
'@seuperfil', 'seusite.com.br'
```

### Label estática (rótulo fixo do template)

Rótulo fixo que **não muda por post**. Geralmente NÃO recebe `data-template-element` — mas se receber por exceção (ex: campanha que troca o label), use:

```
Label estática do template; formato curto e direto;
ex: 'Saiba mais', 'Continue lendo', 'Arraste →'
```

### Foto contextual (userAsset, retangular)

Imagem de apoio que muda por post. A description de imagem tem **três eixos** — e o erro mais comum (visto em produção) é confundi-los:

| Eixo | O que é | Estado | Exemplo |
|------|---------|--------|---------|
| **Papel narrativo** | função da imagem no slide | **obrigatório** | `imagem de capa/abertura`, `imagem de prova`, `imagem de fechamento/CTA`, `apoio contextual da lâmina` |
| **Estilo (registro visual)** | a estética do template, que se mantém entre verticais | **preserva** | `dark premium editorial`, `claro e arejado`, `editorial natural com luz coerente` |
| **Tema (assunto/cena)** | o que aparece na imagem | **abre** (nunca trava) | reflete a **mensagem-chave** do slide — pessoa, objeto, ambiente ou conceito |

> **Por que separar estilo de tema:** o template tem uma identidade visual (ex: um carrossel dark-tech). Essa identidade é **estilo** e deve ser preservada (`dark premium editorial`) — senão a imagem gerada destoa do design. Mas o **assunto** (joelho, mitocôndria, café numa mesa) é o que o designer pôs no placeholder só pra validar layout — **nunca** vai pra description. Travar o assunto quebra o template em todos os outros usos e desconecta a imagem da mensagem-chave de cada slide.

> **Atenção ao placeholder:** o que o designer colocou no slot é só preview visual. **Não** copie o assunto do placeholder. Não adicione bounds como "sem pessoa", "foco em objeto", "anatomia translúcida" só porque o placeholder atual é assim. O gate `audit-template-markup.py` **reprova (FAIL)** descriptions de imagem que (a) travam assunto/cena do placeholder, ou (b) não declaram o papel narrativo do slide.

**Papel narrativo é obrigatório** — derive-o do `brief.md` (passo 3b): o mesmo template costuma ter imagem na capa (slide 1), no miolo de prova e no fechamento/CTA. Cada uma recebe o papel do seu slide, ainda que compartilhem estilo e bounds técnicas.

```
Imagem de capa/abertura da lâmina; tema reflete a mensagem-chave do
slide (livre — pessoa, objeto, ambiente ou conceito); estilo dark
premium editorial com luz coerente; sem texto na imagem; sem
watermark; ex: 'close de mãos em ação no contexto do tema',
'ambiente que situa a cena (espaço, paisagem, lugar)',
'still life ou objeto que simboliza o conceito'
```

Troque `de capa/abertura` por `de prova` ou `de fechamento/CTA` conforme o papel do slide, e o registro de estilo (`dark premium editorial`) pelo registro real do template. Tema e exemplos permanecem abertos.

Quando o slot tem aspect ratio extremo (panorâmico, retrato muito alto), adicione 1 bound técnica de enquadramento — não temática:

```
... ; slot panorâmico (16:9), prefira composições horizontais com
respiro nas laterais ; ex: ...
```

#### Anti-pattern real (template dark-tech em produção)

Placeholder no HTML: render 3D de joelho translúcido com glow neon (capa de um carrossel sobre dor pós-treino).

❌ Errado — trava assunto+cena do placeholder, sem papel narrativo, igual nos 3 slides com imagem:
```
Imagem; anatomia translúcida do joelho; núcleo vermelho-alaranjado;
feixes azul-ciano; glow neon; sci-fi médico; fundo escuro; sem texto;
sem watermark
```
(quebra cross-vertical, desconecta da mensagem-chave, e como é idêntica nas 3 imagens o LLM downstream não distingue capa de fechamento)

✅ Correto — papel do slide + estilo preservado + tema aberto:
```
Imagem de capa/abertura da lâmina; tema reflete a mensagem-chave do
slide (livre); estilo dark premium editorial, alto contraste, luz
cinematográfica coerente; sem texto na imagem; sem watermark; ex:
'close de detalhe que simboliza o tema', 'ambiente que situa a cena',
'objeto/conceito em destaque sobre fundo escuro'
```
(o registro "dark premium / alto contraste / cinematográfico" preserva a identidade do template; o assunto fica livre pra refletir cada slide)

### Foto profissional (cutout PNG)

Foto do profissional/protagonista com fundo transparente. Mesma foto pode aparecer em múltiplos slides — use `data-te-link-id="professionalPhoto"` para vincular.

```
Foto cutout do protagonista do post; figura inteira sobre fundo
transparente (removeBackground=true); enquadramento até a cintura
ou corpo todo; expressão acolhedora e olhar para a câmera;
ex: 'profissional em traje formal sorrindo', 'protagonista em
postura casual e confiante', 'pessoa em pé com olhar direto e
acolhedor'
```

### Logo da marca

Marca da empresa/profissional. Não muda por post (`data-static="true"`) mas a description ajuda quando há variantes (horizontal, monograma).

```
Logo da marca; preserva proporção original; sem efeitos;
ex: 'marca horizontal completa', 'monograma circular',
'selo quadrado para canto inferior'
```

---

## Como o marker usa este catálogo

1. Ao caminhar pelos slides, o marker **primeiro identifica o padrão composicional da lâmina** (passo 3c do SKILL: checklist, grade, comparação, passo-a-passo, capa, dado, CTA — derivado do arquétipo `A<N>` do `visual-plan.md` + `_shared/COMPOSITIONS.md`) e mapeia cada elemento ao seu slot dentro do padrão. Só então identifica o role de cada elemento (eyebrow, hook, corpo, dado, item de checklist, etc).
2. Para cada elemento `data-template-element="true"`:
   a. Escolha o role canônico mais próximo do catálogo.
   b. **Para textos**, derive o primeiro exemplo do texto atual do elemento — generalizando vertical e tema. O texto no HTML é a melhor pista de **formato e comprimento**, mas não de **tema**.
   c. **Para imagens**, ignore o tema do placeholder. O role da imagem vem do papel narrativo do slide (capa? prova? CTA?), não da foto que o designer colocou.
   d. **Insira o componente `<papel na composição>`** (do passo 3c): índice/contagem em slots repetidos (`item N de M`, `célula N de M`), relação pai/filho (`cabeçalho que governa a lista`), lado/ordem (`lado A da comparação`). **Obrigatório em slots repetidos na mesma lâmina.**
   e. **Adicione hint de sequência narrativa** quando o elemento funciona em par com vizinhos: `após eyebrow categórico; seguido de subtítulo de apoio`. Mantém coerência adjacente.
   f. Complete com 2 exemplos cross-vertical adicionais cobrindo variação saudável.
3. Para slots equivalentes **em slides diferentes** (ex: eyebrow do slide 1, 3, 5), aplica **a mesma string** (o LLM diferencia pelo contexto da página). Para slots repetidos **na mesma lâmina** (itens de checklist, células de grade), aplica strings que diferem **só** no componente `<papel na composição>`.
4. Se um role não bate com nenhum do catálogo, componha seguindo a fórmula dos 5 componentes — sempre com exemplos cross-vertical.

### Exemplo de contextualização (texto)

Texto no HTML: `"Paciente não compra 'técnica'."`
Eyebrow acima: `"insight"` | Corpo abaixo: `"Ele entende dor, segurança, clareza e próximo passo."`

Description contextualizada (catálogo "Título de slide intermediário"):
```
Título da lâmina intermediária; formato afirmação direta OU inversão
de expectativa; 1 frase em 2 linhas; após eyebrow categórico; seguido
de corpo educativo de apoio; ex: 'Cliente não compra
expertise', 'O detalhe que vira decisão', 'Resultado não é só número'
```

Note: ex1 (`'Cliente não compra expertise'`) deriva do texto real generalizado — manteve o formato "afirmação que inverte expectativa" e o comprimento, mas trocou "Paciente" por "Cliente" (cross-vertical).

### Exemplo de contextualização (imagem)

Placeholder no HTML: foto de café numa mesa com caderno
Papel do slide (do brief): "prova de processo — mostra a rotina prática do método"

❌ Errado — copia o placeholder:
```
Imagem contextual neutra da lâmina; formato foto de processo, mesa ou
objeto; sem pessoa em destaque; apoio visual ao conteúdo; ex: 'mesa
organizada com materiais', 'objeto de trabalho em detalhe', 'processo
visto de cima'
```

✅ Correto — descreve a função no slide, deixa o tema aberto:
```
Imagem de apoio contextual da lâmina (slide de prova de processo);
tema reflete a mensagem-chave do slide; estilo editorial natural com
luz coerente; sem texto na imagem; ex: 'close de mãos em ação',
'ambiente que situa a cena', 'still life ou objeto que simboliza o
conceito'
```

## Como o LLM consome (referência)

O `copy_processor._format_elements_context` da lambda `app-lambda-ai-idea-to-template` monta:

```
## Página 1 — mensagem-chave: <vinda da pipeline>
- [Index: 5] [TIPO=textbox] Eyebrow editorial da lâmina; formato 'NN / TEMA'... [maxChars: 30]
- [Index: 8] [TIPO=textbox] Hook principal do carrossel; formato pergunta... [maxChars: 90]

## Página 2 — mensagem-chave: <outra>
- [Index: 12] [TIPO=textbox] Eyebrow editorial da lâmina; formato 'NN / TEMA'... [maxChars: 30]
- [Index: 15] [TIPO=textbox] Título da lâmina intermediária; formato afirmação... [maxChars: 60]
```

Mesmo eyebrow, descriptions idênticas, mas o LLM gera `'01 / O PROBLEMA'` no slide 1 e `'02 / O MÉTODO'` no slide 2 porque a mensagem-chave da página dá o tema e o formato `'NN / TEMA'` trava a estrutura.
