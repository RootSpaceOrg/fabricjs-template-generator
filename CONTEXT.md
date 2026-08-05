# Copy Specialist — Dossiê, funil e storyline

Conhecimento em camadas (o específico vence): **este arquivo (geral)** →
`knowledge/copy/negocios/<business_type>.md` (por negócio) → pedido do usuário.

Produz `artifacts/runs/<slug>/brief.md`. É aqui que a copy nasce — e onde o slop morre ou nasce. Nada de copy de cabeça.

## 1. Dossiê do business_type

Arquivo: `knowledge/copy/negocios/<slug>.md` (slug canônico do resolve_tenant).

- Existe e `updated:` ≤30 dias → use direto.
- Senão → pesquise na web e escreva/atualize:

```markdown
---
business_type: <slug>
updated: <YYYY-MM-DD>
---
## Público e dores            ← quem contrata, o que dói, objeções
## Mitos e dúvidas frequentes  ← matéria-prima de gancho
## Jargão do nicho            ← como o profissional fala
## Ângulos que performam       ← HIPÓTESES da web; troque por dados da plataforma quando existirem
## Sazonalidade               ← datas/campanhas do nicho
```

**Regras de pesquisa:** priorize fontes primárias (conselhos profissionais, publicações científicas, dados de mercado) sobre blogs de marketing — a web aberta está cheia do mesmo slop que queremos evitar; conteúdo de listicle é hipótese, nunca verdade. Registre a fonte de cada afirmação não-óbvia.

**Compliance NÃO vai no dossiê**: vem de `compliance/<vertical>.md` (curado por humano). Se o arquivo da vertical não existe, avise no relatório e aplique a regra conservadora: nenhuma promessa de resultado, nenhuma comparação de superioridade, nenhum preço.

## 2. Funil

Classifique a etapa (ou aceite a declarada). Conflito ideia×etapa → aponte em 1 linha e proponha o ângulo certo; não gere peça de funil confuso.

| Etapa | Papel | CTA típico | Sabor que performa |
|-------|-------|-----------|--------------------|
| `topo` | atrair quem não conhece | "Salve", "Compartilhe", "Siga" | listicle / mito-vs-verdade (gera comentário) |
| `meio` | educar, construir confiança | "Comente <palavra>", "Chama no direct" | tutorial / como-funciona (gera save) |
| `fundo` | converter quem considera | "Agende sua avaliação", "Chame no WhatsApp" | case / prova / FAQ de objeções (gera share) |

Frameworks narrativos detalhados: `references-frameworks.md` (reuse; o framework dá o sabor, a espinha dá a ordem).

## 3. Storyline — espinha obrigatória

```
GANCHO → PROBLEMA → EXPLICAÇÃO → SOLUÇÃO → [RECAP] → CTA
```

| Beat | Slides | Fonte |
|------|--------|-------|
| Gancho | 1 | mitos/dúvidas — headline 5–8 palavras + curiosidade que só se resolve swipando |
| Problema | 1–2 | dores — o leitor se reconhece |
| Explicação | 2–4 | jargão traduzido — onde a autoridade se constrói |
| Solução | 1–2 | dentro do compliance |
| Recap | penúltimo, se ≥7 slides | takeaway salvável em 1 frase |
| CTA | último | específico e conectado ao valor ("Salve para consultar antes da 1ª sessão" ✅ / "link na bio" ❌) |

**Princípio herói/guia (universal, todo arco):** o LEITOR é o herói da história; o profissional é o guia que dá o plano. A copy nunca posiciona o serviço como salvador ("só eu resolvo") — posiciona como caminho. Além de tom melhor, é o que mantém a peça dentro do compliance (sem autopromoção, sem promessa).

**Arcos alternativos sancionados** (a espinha acima é o default; escolha um destes quando servir melhor a etapa — nunca invente um quarto):

| Arco | Estrutura | Quando usar |
|------|-----------|-------------|
| `antes-depois-ponte` | onde a pessoa está → onde quer chegar → o serviço como PONTE | fundo/prova: mostra resultado sem prometer resultado (o caminho é a oferta) — o arco mais seguro para compliance de saúde |
| `premissa-provocacao-prova` | ideia forte → provoca a lógica comum → prova com dado/exemplo/metáfora | meio/posicionamento: autoridade com ponto de vista |
| `conflito-virada-licao` | dilema real → quebra de expectativa → aprendizado | retenção/humanização (equivale ao vulnerable-story da taxonomia) |

**Regras (valem para QUALQUER arco):** 1 carrossel = 1 ideia. Todo slide termina em open loop puxando o próximo. Beat não se mistura. Etapa do funil dosa os beats, nunca reordena o arco escolhido. 6–13 slides (8–12 educação profunda, 5–6 peça rápida). 1–2 frases por slide além da headline. Herói/guia sempre. Declare o arco escolhido na storyline e no relatório. Métrica servida: swipe-through ≥70%.

## 3b. Leis de qualidade da copy (valem para QUALQUER negócio — viram check do judge)

Vereditos de 2026-08-05 (var-teste-1/2) destilados em lei geral:

1. **Gancho com custo ou tensão, nunca anúncio de pauta.** "Primeira sessão feita." apenas declara o tema. "O que você faz nas próximas 48h decide metade do resultado" dá preço a ignorar o post. Todo gancho responde: por que o leitor NÃO pode pular isso?
2. **História, não checklist.** Item de lista sem problema reconhecível antes e sem explicação depois é slop. A espinha (§3) é obrigatória de verdade: problema em que o leitor se vê → explicação que constrói autoridade → instrução.
3. **Instrução sempre com mecanismo.** "Evite sol" não ensina; "a área tratada fica fotossensível por X, então evite sol por Y dias" soa profissional. Todo imperativo carrega um porquê — é onde a autoridade nasce.
4. **Zero redundância entre slides.** Dois slides dizendo o mesmo com palavras diferentes = fita inchada; corte e aprofunde. Cada slide adiciona informação nova, e o open loop do fim de cada slide é real (pergunta/promessa que o próximo resolve).
5. **Especificidade de nicho é obrigatória.** Se a copy serve igual para outro procedimento/segmento, ela reprova. Jargão e fatos do dossiê do negócio DEVEM aparecer — copy intercambiável é o sintoma nº 1 de slop.
6. **CTA conectado ao valor entregue.** "Consulte sua clínica" é burocracia; o CTA nasce do que a peça acabou de dar ("Salve para consultar antes da 1ª sessão" só funciona se o guia mereceu save).

## 4. Doutrina de design (entra no brief)

- Jargão do nicho encorajado; CTA de serviço permitido; `professionalPhoto` permitido quando o negócio vende confiança pelo rosto; iconografia do setor permitida.
- **Composição autoral**: o designer desenha os anchors a partir do conteúdo; catálogo A1–A14 é inspiração, não jaula.
- **Editabilidade obrigatória**: outro profissional do MESMO nicho adapta a peça no editor (slots `data-*` normais).

## Saída: brief.md

```markdown
# Brief — <título>
## Business
business_type: <slug> · tenant: <t> · vertical: <v> · funil: <etapa> · objetivo: <obj> · framework: <fw>
## Storyline
S1 (gancho): <linha> → open loop: <pergunta que puxa S2>
S2 (problema): ...
...
## Copy por slide
<copy real, densidade final, jargão do dossiê, dentro do compliance>
## Compliance aplicado
<regras do arquivo curado que limitam esta peça — ou "arquivo ausente: regra conservadora">
## Formato
1080×1350 · <N> slides · brand colors primary+secondary swappable
## Referência visual / estilo
<anexo ou regras textuais do usuário — ou "nenhum">
## Doutrina de design
<bloco da seção 4>
```
