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

## Anatomia da description (4 componentes)

Toda description segue a fórmula:

```
<role narrativo>; formato '<máscara>'; <bound 1>; <bound 2>; ex: '<ex1>', '<ex2>', '<ex3>'
```

| Componente | O que é | Exemplo |
|------------|---------|---------|
| **Role narrativo** | Função do elemento na lâmina | "Eyebrow editorial da lâmina" |
| **Formato** | Máscara da string em aspas simples | "formato 'NN / TEMA'" |
| **Bounds** | Restrições quantitativas (chars, linhas, presença de número) | "até 30 chars" + "TEMA em CAPS" |
| **Exemplos** | 3 exemplos curtos cobrindo variação saudável de formato (cross-vertical — nunca presos ao nicho do template atual nem ao conteúdo do placeholder) | "ex: '01 / DOR', '03 / O ESTUDO', '07 / CTA'" |

**Sweet spot**: 200-300 chars por description. Cada description vai pra cada elemento de cada template no prompt do LLM — pesar tokens importa.

## Anti-patterns — descriptions que QUEBRAM o LLM downstream

Antes de escrever qualquer `data-te-description`, verifique se você está caindo em um desses anti-patterns:

| Anti-pattern | Por que quebra | Exemplo ruim | Exemplo correto |
|-------------|----------------|--------------|-----------------|
| **Prosa descritiva sem fórmula** | Sem formato, sem tamanho, sem exemplos — output inconsistente entre slides | `"Slide 4 título: texto neutro e adaptável para qualquer nicho, com linguagem concreta e sem jargão."` | `"Título da lâmina intermediária; formato afirmação direta OU inversão; 1 frase em 2 linhas; 30-60 chars; ex: 'O detalhe que ninguém vê', 'Pequeno ajuste, grande efeito', 'Resultado não é só número'"` |
| **Role sem exemplos** | Sem exemplos, o LLM adivinha o estilo — vira inconsistência | `"Eyebrow editorial da lâmina; rótulo curto de seção"` | `"Eyebrow editorial; formato 'NN / TEMA'; até 30 chars; ex: '01 / PARTE UM', '03 / O MÉTODO', '07 / PRÓXIMO PASSO'"` |
| **Exemplos do vertical atual** | Template vai ser usado em dezenas de verticais — exemplos amarrados a um vertical travam o LLM nos outros | `"ex: '01 / FISIOTERAPIA', '03 / COLUNA CERVICAL'"` (template de saúde) ou `"ex: 'ração premium', 'banho e tosa'"` (template de pet) | `"ex: '01 / O DIAGNÓSTICO', '03 / O MÉTODO', '07 / PRÓXIMO PASSO'"` (cross-vertical) |
| **Description que copia o placeholder** | O placeholder (texto/imagem que o designer colocou pra preencher o slot) é só preview visual — não dita o conteúdo real. Descrever o placeholder amarra o LLM nele | Placeholder é foto de café numa mesa → `"formato foto de processo, mesa ou objeto; sem pessoa em destaque; ex: 'mesa organizada', 'objeto em detalhe'"` | `"Imagem de apoio contextual; tema reflete a mensagem-chave do slide; estilo editorial; ex: 'close de mãos em ação', 'ambiente do contexto', 'still life relacionado ao tema'"` |
| **Bounds inventadas a partir do placeholder** | "Sem pessoa em destaque", "foto noturna", "objeto em plano fechado" — restrições derivadas do placeholder atual que travam o template nos outros usos | `"sem pessoa em destaque"` (porque o placeholder não tem pessoa) | Bound real: `"editorial natural; sem texto na imagem; sem watermark"` (técnica, não temática) |
| **ex1 genérico ignorando o texto real** | O primeiro exemplo deve derivar do texto real no HTML (generalizado) — inventar do zero descarta a melhor pista de **formato/comprimento**. Mas só usa o texto real como base de formato, não de tema | Texto real: `"Seu conhecimento clínico está virando pacientes?"` → ex1 inventado: `"Sua ideia ficou clara?"` (perdeu o formato pergunta longa) | ex1 derivado: `"Seu conhecimento está virando resultados?"` (mantém formato pergunta + comprimento, generaliza vertical) |
| **Título do template como description** | A description é o prompt para o LLM gerar copy, não uma label do elemento | `"Título do slide sobre mitos de produtividade"` | `"Título da lâmina intermediária; formato afirmação que desmonta crença; ..."` |

**Regra de ouro:** se você remover a description e o LLM não souber o *formato*, o *tamanho* e o *estilo* do que deve gerar — a description está errada. E se a description só funciona porque o usuário vai escrever sobre o mesmo tema do placeholder — também está errada.

---

## Regras invioláveis

1. **Exemplos são cross-vertical.** Mistura intencional entre nichos: um de serviço/negócios, um de bem-estar/lifestyle, um de objeto/conceito. Nunca 3 exemplos do mesmo vertical (saúde, pet, beleza). Nunca exemplos que reciclam o placeholder atual. Template vai ser usado em dezenas de verticais; descriptions são reutilizáveis.
2. **Role descreve função, não conteúdo.** "Imagem de apoio contextual da lâmina" é função. "Foto de mesa com objetos de trabalho" é conteúdo do placeholder — não vai pra description.
3. **Bounds são técnicas/estruturais, não temáticas.** `"até 60 chars"`, `"2 linhas"`, `"sem texto na imagem"`, `"editorial natural"` — sim. `"sem pessoa"`, `"foco em objeto"`, `"vista de cima"` — não (a menos que o slot tenha aspect ratio que **realmente** exija esse enquadramento).
4. **Formato e conteúdo são coisas diferentes.** `formato 'NN / TEMA'` define a estrutura. `ex:` mostra como aplicar. Nunca escrever `formato 'NN / nutrição'` (mistura).
5. **3 exemplos é o sweet spot.** 1 vira regra rígida. 5+ vira ruído. 3 cobrem variação saudável (curto/médio/longo, ou close/médio/aberto para imagens).
6. **Mesma description para slots equivalentes.** Eyebrow no slide 1 e eyebrow no slide 5 recebem **a mesma string**. O LLM diferencia pelo contexto da página (mensagem-chave, que ele já vê separadamente).
7. **Quando em dúvida, escolha a description menor do catálogo** em vez de inventar um role novo.

---

## Catálogo

### Eyebrow numerado

Pequeno rótulo acima do título com numeração sequencial. ALL CAPS. Geralmente em cor primary brand. Movimento memorável comum em estética editorial e magazine.

```
Eyebrow editorial da lâmina; formato 'NN / TEMA' onde NN é o número
sequencial do slide (01, 02, 03...) e TEMA é categoria curta em CAPS;
até 30 chars total; ex: '01 / O PROBLEMA', '03 / O MÉTODO',
'07 / PRÓXIMO PASSO'
```

### Eyebrow simples (sem numeração)

Rótulo categórico curto, sem número. ALL CAPS. Categoriza o tema do slide ou do post.

```
Eyebrow categórico; formato 'TEMA EM CAPS' sem numeração; rótulo curto
que categoriza o slide; até 25 chars; ex: 'EM 5 PASSOS',
'O QUE FAZER', 'TEMA CENTRAL'
```

### Hook do Slide 1

Primeira frase do carrossel. Mata ou salva o engagement. Geralmente serif italic display em 2-3 linhas. Uma das 5 fórmulas: pergunta provocativa, afirmação polêmica, número + benefício, resultado concreto, inversão de expectativa.

```
Hook principal do carrossel (slide 1); formato pergunta provocativa OU
afirmação que gera curiosidade OU número + benefício; 1 frase em 2-3
linhas; 50-90 chars; ex: 'O que você faz quando o método não funciona
mais', '5 sinais de que seu negócio pede atenção', 'O detalhe que
ninguém te conta na hora de começar'
```

### Subtítulo de apoio ao hook (slide 1)

Linha curta abaixo do hook que complementa a promessa. Sans-serif body.

```
Subtítulo de apoio ao hook do slide 1; formato frase corrida que
complementa a promessa; 1 linha; 40-70 chars; ex: 'Um guia em 5 passos
práticos', 'Baseado em casos reais de clientes', 'O que ninguém te
ensinou ainda'
```

### Título de slide intermediário (subtítulo da lâmina)

Headline de slide do miolo. Geralmente serif italic em 2 linhas. Marca a transição/conceito do slide.

```
Título da lâmina intermediária; formato afirmação direta OU pergunta
curta OU inversão de expectativa; 1 frase em 2 linhas; 30-60 chars;
ex: 'O detalhe que ninguém vê', 'Pequenos ajustes, grandes mudanças',
'Por que isso funciona?'
```

### Corpo educativo (texto longo do miolo)

Parágrafo explicativo do slide. Sans-serif body, multi-linhas. Conceito ou evidência.

```
Corpo educativo da lâmina; formato 1 parágrafo de 3-4 linhas curtas
explicando o conceito do slide; 150-280 chars; tom acessível sem
jargão; ex: 'O método que parece simples só funciona quando os
fundamentos estão no lugar. Aqui está o que costuma estar faltando
quando o resultado some.'
```

### Bullet de lista educativa

Item curto de uma lista (Listicle, Tutorial). Geralmente sans-serif weight 600 na primeira palavra.

```
Item de lista educativa; formato '<verbo|substantivo curto>: <explicação
em 1 linha>' OU somente afirmação curta; até 100 chars; ex: 'Comece
pequeno: 1 ação concreta por dia', 'Constância vale mais que
intensidade', 'Revise o que funcionou na semana'
```

### Dado numérico (prova social)

Número grande de destaque. Display grande, geralmente serif italic. 1 número por slide.

```
Dado de prova social; formato 'NN%' OU 'NNx' OU número absoluto sem
unidade; máximo 1 número visível; até 4 chars de número; ex: '73%',
'2.5x', '8 sem'
```

### Caption de dado

Legenda do dado numérico. Sans-serif body, multi-linhas. Explica o significado do número.

```
Legenda do dado numérico; formato frase corrida começando em minúscula;
explica em 1-2 linhas o significado do número; 60-120 chars; ex: 'dos
clientes relataram melhora significativa em poucas semanas', 'mais
rápido do que métodos convencionais segundo estudos recentes'
```

### Pull-quote / citação

Trecho de fala de cliente, autoridade ou frase de impacto. Geralmente entre aspas tipográficas, serif italic, com aspa decorativa visível.

```
Citação de impacto; formato frase entre aspas em 1ª pessoa OU
afirmação forte sem aspas; 1-2 linhas; 60-110 chars; ex: 'Eu não sabia
que tinha solução', 'A diferença foi sentir resultado de verdade',
'Voltei a confiar no processo'
```

### CTA principal (último slide)

Chamada de ação final. Verbo no imperativo + objeto direto. Display médio.

```
CTA principal do último slide; formato verbo no imperativo + objeto
direto; 1 frase em 2-3 linhas; 30-60 chars; ex: 'Agende sua primeira
conversa', 'Solicite uma avaliação gratuita', 'Fale comigo no
WhatsApp'
```

### Linha de contato (telefone, link, handle)

Suporte ao CTA com canal de contato. Sans-serif body pequeno.

```
Linha de contato no slide CTA; formato '<canal> <valor>' OU somente
valor formatado; até 35 chars; ex: 'WhatsApp (11) 9 0000-0000',
'@seuperfil', 'seusite.com.br'
```

### Label estática (rótulo fixo do template)

Rótulo fixo que **não muda por post**. Geralmente NÃO recebe `data-template-element` — mas se receber por exceção (ex: campanha que troca o label), use:

```
Label estática do template; formato curto e direto; até 20 chars;
ex: 'Saiba mais', 'Continue lendo', 'Arraste →'
```

### Foto contextual (userAsset, retangular)

Imagem de apoio que muda por post. O role é **dar suporte visual ao conceito do slide** — não impor tema, enquadramento ou ausência de pessoa. O LLM downstream decide o conteúdo a partir da mensagem-chave da página; a description só fixa qualidade e bounds técnicas.

> **Atenção ao placeholder:** o que o designer colocou no slot (foto de mesa, de café, de pessoa caminhando) é só preview visual pra ajudar a aprovar o layout. **Não** copie o tema do placeholder pra description. Não adicione bounds como "sem pessoa" ou "foco em objeto" só porque o placeholder atual é assim.

```
Imagem de apoio contextual da lâmina; tema reflete a mensagem-chave
do slide (livre — pessoa, objeto, ambiente ou conceito); estilo
editorial natural com luz coerente; sem texto na imagem; sem
watermark; ex: 'close de mãos em ação no contexto do tema',
'ambiente que situa a cena (espaço, paisagem, lugar)',
'still life ou objeto que simboliza o conceito'
```

Quando o slot tem aspect ratio extremo (panorâmico, retrato muito alto), adicione 1 bound técnica de enquadramento — não temática:

```
... ; slot panorâmico (16:9), prefira composições horizontais com
respiro nas laterais ; ex: ...
```

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

1. Ao caminhar pelos slides, o marker identifica o role de cada elemento (eyebrow, hook, corpo, dado, foto contextual, foto profissional, etc).
2. Para cada elemento `data-template-element="true"`:
   a. Escolha o role canônico mais próximo do catálogo.
   b. **Para textos**, derive o primeiro exemplo do texto atual do elemento — generalizando vertical e tema. O texto no HTML é a melhor pista de **formato e comprimento**, mas não de **tema**.
   c. **Para imagens**, ignore o tema do placeholder. O role da imagem vem do papel narrativo do slide (capa? prova? CTA?), não da foto que o designer colocou.
   d. **Adicione hint de sequência narrativa** quando o elemento funciona em par com vizinhos: `após eyebrow categórico; seguido de subtítulo de apoio`. Mantém coerência adjacente.
   e. Complete com 2 exemplos cross-vertical adicionais cobrindo variação saudável.
3. Para slots equivalentes em slides diferentes (ex: eyebrow do slide 1, 3, 5), aplica **a mesma string**. O LLM diferencia pelo contexto da página.
4. Se um role não bate com nenhum do catálogo, componha seguindo a fórmula dos 4 componentes — sempre com exemplos cross-vertical.

### Exemplo de contextualização (texto)

Texto no HTML: `"Paciente não compra 'técnica'."`
Eyebrow acima: `"insight"` | Corpo abaixo: `"Ele entende dor, segurança, clareza e próximo passo."`

Description contextualizada (catálogo "Título de slide intermediário"):
```
Título da lâmina intermediária; formato afirmação direta OU inversão
de expectativa; 1 frase em 2 linhas; após eyebrow categórico; seguido
de corpo educativo de apoio; 30-60 chars; ex: 'Cliente não compra
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
