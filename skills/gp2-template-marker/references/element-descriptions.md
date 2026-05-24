# Element descriptions — catálogo canônico para `data-te-description`

Catálogo de descriptions canônicas por papel narrativo. O marker consulta este arquivo na hora de emitir `data-te-description` em cada `data-template-element="true"`.

## Por que existe

A `description` que você escreve aqui é injetada **literal** no prompt do LLM gerador de copy do `healthmarket-lambda-ai-idea-to-template` (`copy_processor.py:_format_elements_context`). O LLM recebe assim:

```
## Página 1 — mensagem-chave: dor crônica
- [Index: 5] [TIPO=textbox] <sua description aqui> [maxChars: 41]
```

Description vaga ("Eyebrow editorial") deixa o LLM adivinhar o formato. Description estruturada com formato e exemplos guia o LLM para output consistente entre slides.

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
| **Exemplos** | 3 exemplos curtos cobrindo variação saudável de formato (NUNCA do nicho atual do template) | "ex: '01 / DOR', '03 / O ESTUDO', '07 / CTA'" |

**Sweet spot**: 200-300 chars por description. Cada description vai pra cada elemento de cada template no prompt do LLM — pesar tokens importa.

## Anti-patterns — descriptions que QUEBRAM o LLM downstream

Antes de escrever qualquer `data-te-description`, verifique se você está caindo em um desses anti-patterns:

| Anti-pattern | Por que quebra | Exemplo ruim | Exemplo correto |
|-------------|----------------|--------------|-----------------|
| **Prosa descritiva sem fórmula** | O LLM não sabe o formato esperado, nem o tamanho, nem os examples — gera output inconsistente entre slides | `"Slide 4 título: texto neutro e adaptável para qualquer nicho, com linguagem concreta e sem jargão."` | `"Título da lâmina intermediária; formato afirmação direta OU inversão; 1 frase em 2 linhas; 30-60 chars; ex: 'O corpo fala antes de doer', ..."` |
| **Role sem exemplos** | Sem exemplos, o LLM adivinha o estilo — vira inconsistência | `"Eyebrow editorial da lâmina; rótulo curto de seção"` | `"Eyebrow editorial; formato 'NN / TEMA'; até 30 chars; ex: '01 / DOR CRÔNICA', '03 / O ESTUDO', '07 / PRÓXIMO PASSO'"` |
| **Exemplos do vertical atual** | O template vai ser usado em dezenas de verticais — exemplos específicos de saúde travam o LLM em outros contextos | `"ex: '01 / FISIOTERAPIA', '03 / COLUNA CERVICAL'"` | `"ex: '01 / DOR CRÔNICA', '03 / O ESTUDO', '07 / PRÓXIMO PASSO'"` |
| **ex1 genérico ignorando o texto real** | O primeiro exemplo deve derivar do texto real no HTML (generalizado) — inventar do zero descarta a melhor pista disponível | Texto real: `"Seu conhecimento clínico está virando pacientes?"` → ex1 inventado: `"Sua ideia ficou clara?"` | ex1 derivado: `"Seu conhecimento está virando resultados?"` |
| **Título do template como description** | A description é o prompt para o LLM gerar copy, não uma label do elemento | `"Título do slide sobre mitos de produtividade"` | `"Título da lâmina intermediária; formato afirmação que desmonta crença; ..."` |

**Regra de ouro:** se você remover a description e o LLM não souber o *formato*, o *tamanho* e o *estilo* do que deve gerar — a description está errada.

---

## Regras invioláveis

1. **Exemplos são genéricos, não do vertical atual.** Template é de qualquer nicho? Exemplos do eyebrow continuam `'01 / DOR', '03 / O ESTUDO', '07 / PRÓXIMO PASSO'` — nunca `'01 / FISIOTERAPIA'` ou qualquer referência ao vertical específico. O template vai ser usado em dezenas de verticais; descriptions são reutilizáveis.
2. **Formato e conteúdo são coisas diferentes.** `formato 'NN / TEMA'` define a estrutura. `ex:` mostra como aplicar. Nunca escrever `formato 'NN / nutrição'` (mistura).
3. **3 exemplos é o sweet spot.** 1 vira regra rígida. 5+ vira ruído. 3 cobrem curto/médio/longo.
4. **Mesma description para slots equivalentes.** Eyebrow no slide 1 e eyebrow no slide 5 recebem **a mesma string**. O número do slide vem do contexto da página (mensagem-chave da narrative arc), que o LLM já vê separadamente.
5. **Quando em dúvida, escolha a description menor do catálogo.** Não invente um role novo — use o role canônico mais próximo.

---

## Catálogo

### Eyebrow numerado

Pequeno rótulo acima do título com numeração sequencial. ALL CAPS. Geralmente em cor primary brand. Movimento memorável comum em estética editorial e magazine.

```
Eyebrow editorial da lâmina; formato 'NN / TEMA' onde NN é o número
sequencial do slide (01, 02, 03...) e TEMA é categoria curta em CAPS;
até 30 chars total; ex: '01 / DOR CRÔNICA', '03 / O ESTUDO',
'07 / PRÓXIMO PASSO'
```

### Eyebrow simples (sem numeração)

Rótulo categórico curto, sem número. ALL CAPS. Categoriza o tema do slide ou do post.

```
Eyebrow categórico; formato 'TEMA EM CAPS' sem numeração; rótulo curto
que categoriza o slide; até 25 chars; ex: 'EM 5 PASSOS',
'PARA VOCÊ', 'TEMA CENTRAL'
```

### Hook do Slide 1

Primeira frase do carrossel. Mata ou salva o engagement. Geralmente serif italic display em 2-3 linhas. Uma das 5 fórmulas: pergunta provocativa, afirmação polêmica, número + benefício, resultado concreto, inversão de expectativa.

```
Hook principal do carrossel (slide 1); formato pergunta provocativa OU
afirmação que gera curiosidade OU número + benefício; 1 frase em 2-3
linhas; 50-90 chars; ex: 'Você não precisa sentir dor para começar a se
cuidar', '5 sinais de que seu sono pede atenção', 'O que ninguém te
conta sobre ansiedade matinal'
```

### Subtítulo de apoio ao hook (slide 1)

Linha curta abaixo do hook que complementa a promessa. Sans-serif body.

```
Subtítulo de apoio ao hook do slide 1; formato frase corrida que
complementa a promessa; 1 linha; 40-70 chars; ex: 'Por Dra. Ana Lima',
'Um guia em 5 passos práticos', 'Baseado em anos de experiência'
```

### Título de slide intermediário (subtítulo da lâmina)

Headline de slide do miolo. Geralmente serif italic em 2 linhas. Marca a transição/conceito do slide.

```
Título da lâmina intermediária; formato afirmação OU pergunta curta;
1 frase em 2 linhas; 30-60 chars; ex: 'O corpo fala antes de doer',
'Pequenos ajustes, grandes mudanças', 'Por que isso funciona?'
```

### Corpo educativo (texto longo do miolo)

Parágrafo explicativo do slide. Sans-serif body, multi-linhas. Conceito ou evidência.

```
Corpo educativo da lâmina; formato 1 parágrafo de 3-4 linhas curtas
explicando o conceito do slide; 150-280 chars; tom acessível sem
jargão; ex: 'Tensão crônica, sono fragmentado e ansiedade matinal são
sinais de que o sistema nervoso pede atenção. A boa notícia: você não
precisa esperar um colapso para agir.'
```

### Bullet de lista educativa

Item curto de uma lista (Listicle, Tutorial). Geralmente sans-serif weight 600 na primeira palavra.

```
Item de lista educativa; formato '<verbo|substantivo curto>: <explicação
em 1 linha>' OU somente afirmação curta; até 100 chars; ex: 'Hidrate-se:
2L de água ao longo do dia', 'Sono profundo recupera o sistema nervoso',
'Pratique 20min de movimento'
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
pacientes relataram melhora significativa após 8 semanas', 'mais rápido
que tratamentos convencionais comprovam estudos recentes'
```

### Pull-quote / citação

Trecho de fala de paciente, autoridade ou frase de impacto. Geralmente entre aspas tipográficas, serif italic, com aspa decorativa visível.

```
Citação de impacto; formato frase entre aspas em 1ª pessoa OU afirmação
forte sem aspas; 1-2 linhas; 60-110 chars; ex: 'Eu não sabia que dor
crônica tinha tratamento', 'A diferença foi sentir o corpo de novo',
'Voltei a confiar no meu sono'
```

### CTA principal (último slide)

Chamada de ação final. Verbo no imperativo + objeto direto. Display médio.

```
CTA principal do último slide; formato verbo no imperativo + objeto
direto; 1 frase em 2-3 linhas; 30-60 chars; ex: 'Agende sua primeira
consulta', 'Marque sua avaliação gratuita', 'Fale comigo no WhatsApp'
```

### Linha de contato (telefone, link, handle)

Suporte ao CTA com canal de contato. Sans-serif body pequeno.

```
Linha de contato no slide CTA; formato '<canal> <valor>' OU somente
valor formatado; até 35 chars; ex: 'WhatsApp (11) 9 0000-0000',
'@drabeatrizlima', 'agende.com.br/draana'
```

### Label estática (chrome do template)

Rótulo fixo que **não muda por post**. Geralmente NÃO recebe `data-template-element` — mas se receber por exceção (ex: campanha que troca o label), use:

```
Label estática do template; formato curto e direto; até 20 chars;
ex: 'Saiba mais', 'Continue lendo', 'Arraste →'
```

### Foto contextual (userAsset, retangular)

Imagem de apoio que muda por post. Editorial natural, sem texto na imagem.

```
Imagem de apoio contextual da lâmina; tema deve refletir a mensagem-
chave do slide; estilo editorial natural com luz suave; sem texto na
imagem; ex: 'mãos do profissional segurando estetoscópio com luz
natural', 'paciente em atendimento close-up sereno', 'still life de
copo d'água com luz da manhã'
```

### Foto profissional (cutout PNG)

Foto do profissional com fundo transparente. Mesma foto pode aparecer em múltiplos slides — use `data-te-link-id="professionalPhoto"` para vincular.

```
Foto cutout do profissional; figura inteira sobre fundo transparente
(removeBackground=true); enquadramento até a cintura ou corpo todo;
expressão acolhedora e olhar para a câmera; ex: 'médica de jaleco
branco sorrindo postura formal', 'nutricionista casual blazer braços
cruzados acolhedor', 'fisioterapeuta em pé com olhar confiante'
```

### Logo da marca

Marca da clínica/profissional. Não muda por post (`data-static="true"`) mas a description ajuda quando há variantes (horizontal, monograma).

```
Logo da clínica/marca; preserva proporção original; sem efeitos;
ex: 'Clínica Vita logo horizontal', 'Dr. Marca monograma circular',
'Selo brand quadrado para canto inferior'
```

---

## Como o marker usa este catálogo

1. Ao caminhar pelos slides, o marker identifica o role de cada elemento (eyebrow, hook, corpo, dado etc).
2. Para cada elemento `data-template-element="true"`, **usa o catálogo como base** e **contextualiza** com o texto real do elemento e seus vizinhos:
   a. Escolha o role canônico mais próximo do catálogo.
   b. **Derive o primeiro exemplo do texto atual** do elemento (generalizado — sem referência ao vertical específico do template). O texto no HTML é o melhor sinal do formato que o LLM deve produzir.
   c. **Adicione hint de sequência narrativa** quando o elemento funciona em par com vizinhos: `após eyebrow categórico; seguido de subtítulo de apoio`. Isso mantém coerência entre elementos adjacentes no prompt do LLM.
   d. Adicione 2 exemplos genéricos adicionais para cobrir variação.
3. Se um role não bate exatamente com nenhum do catálogo, o marker compõe seguindo a fórmula dos 4 componentes.
4. Para slots equivalentes em slides diferentes (ex: eyebrow do slide 1, slide 3, slide 5), aplica **a mesma string**. O LLM diferencia pelo contexto da página.

### Exemplo de contextualização

Texto no HTML: `"Paciente não compra 'técnica'."`
Eyebrow acima: `"insight"` | Corpo abaixo: `"Ele entende dor, segurança, clareza e próximo passo."`

Description contextualizada (baseada no catálogo "Título de slide intermediário"):
```
Título da lâmina intermediária; formato afirmação direta OU inversão de
expectativa; 1 frase em 2 linhas; após eyebrow categórico; seguido de
corpo educativo de apoio; 30-60 chars; ex: 'Paciente não compra
expertise', 'O corpo fala antes de doer', 'Resultado não é só número'
```

Note: o primeiro exemplo (`'Paciente não compra expertise'`) é derivado do texto real generalizado, não inventado do zero.

## Como o LLM consome (referência)

O `copy_processor._format_elements_context` (linha 770 da lambda `healthmarket-lambda-ai-idea-to-template`) monta:

```
## Página 1 — mensagem-chave: dor crônica do joelho
- [Index: 5] [TIPO=textbox] Eyebrow editorial da lâmina; formato 'NN / TEMA'... [maxChars: 30]
- [Index: 8] [TIPO=textbox] Hook principal do carrossel; formato pergunta... [maxChars: 90]

## Página 2 — mensagem-chave: o estudo que mudou tudo
- [Index: 12] [TIPO=textbox] Eyebrow editorial da lâmina; formato 'NN / TEMA'... [maxChars: 30]
- [Index: 15] [TIPO=textbox] Título da lâmina intermediária; formato afirmação... [maxChars: 60]
```

Mesmo eyebrow, descriptions idênticas, mas o LLM gera `'01 / DOR CRÔNICA'` no slide 1 e `'02 / O ESTUDO'` no slide 2 porque a mensagem-chave da página dá o tema e o formato `'NN / TEMA'` trava a estrutura.
