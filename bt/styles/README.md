# Sistema de estilos — determinismo por blueprint certificado

A fábrica de templates: **20–30 estilos certificados × copy × imagens = milhares de templates com falha baixa.** Todo o risco estrutural (layout, marcação, conversão) é resolvido UMA vez, na criação do estilo; cada geração só varia conteúdo dentro de uma estrutura já validada.

## Anatomia de um estilo

```
bt/styles/<slug>/
├── STYLE.md                ← tokens + receitas por papel de slide + slots (o contrato)
├── reference.png           ← imagem-âncora aprovada pelo Gustavo (de onde o estilo nasceu)
├── strip-blueprint.html    ← fita paramétrica PRÉ-ANOTADA (produzida na certificação)
├── certification.md        ← evidência de que o corredor inteiro passou (ver protocolo)
└── lessons.md              ← lições DESTE estilo (1 linha por evento; ver regra abaixo)
```

**Lessons por estilo:** todo defeito, rejeição humana ou fix de run que aconteça em template gerado por um estilo vai no `lessons.md` DO estilo (`- <data> <run/template_id>: <o que> → <ação: blueprint corrigido? regra nova? nada ainda>`). O `bt/evals/lessons.md` global fica só para lições da pipeline/corredor (que afetam todos os estilos). Regras:
- Lição recorrente (2×) no mesmo estilo → corrigir o blueprint e **re-certificar** (nova entrada no certification.md).
- Estilo que acumula 3+ lições estruturais sem correção → volta para `status: draft` (sai da fábrica até consertar).
- O judge QA e o context DEVEM ler o lessons.md do estilo escolhido antes de gerar/julgar — é o histórico do que esse estilo costuma errar.

**O blueprint é a peça-chave:** um `strip.html` completo do estilo com:
- slots de copy como placeholders nomeados (`{{s1_headline}}`, `{{s3_body}}`) com min/max chars;
- slots de imagem marcados (`data-image-type` para slots de usuário; `data-bt-generate="<fórmula do prompt>"` para imagens geradas);
- **`data-template-element`, `data-te-max-chars`, `data-variable` JÁ APLICADOS** — o marker em runtime só gera as `data-te-description` da copy nova;
- blocos opcionais delimitados (`<!-- bt:optional nome -->…<!-- /bt:optional -->`) para variação de nº de slides.

## Gerar um template a partir de estilo certificado (runtime)

1. `run.py new <slug> --env <e> --n 1`; context produz storyline mapeada nos **papéis de slide** do STYLE.md.
2. **Instanciar**: preencher os placeholders do blueprint com a copy (respeitando min/max) + gerar as imagens pelas fórmulas `data-bt-generate` + fatiar/renderizar.

   **Variação dentro do estilo (obrigatória — dois templates do mesmo estilo NUNCA saem idênticos):** o blueprint é um *baralho*, não um carimbo. Ele carrega todas as variantes de layout de cada papel de slide (ex: variantes A/B/C de item + respiro invertido), e a instanciação **sorteia e declara** no design-notes.md:
   - **Sequência de variantes** dos slides repetíveis (respeitando "nunca duas iguais adjacentes") — sequência diferente da última instanciação do mesmo estilo (consulte os design-notes de runs anteriores em git, ou varie por padrão);
   - **Nº de slides** dentro do range do estilo (blocos opcionais ligados/desligados);
   - **Posição do slide invertido/acento** (quando o estilo tem);
   - **Lados/rotações** dos elementos que a variante define como alternáveis;
   - E o que já varia por natureza: copy, palavras de watermark, imagens geradas, cores da marca.

   O que NUNCA varia (é a identidade certificada): tipografia, paleta de papéis, tokens, receitas internas de cada variante, marcação `data-*`. Variação é **recombinação do que foi certificado** — nunca invenção de layout novo na run. **Artefatos vão nos caminhos que o runner espera**: `candidates/A/strip.html`, `template.html` (fatiado), `strip.png`, e `design-notes.md` (mínimo: estilo usado, mapa slot→copy, imagens geradas).
3. **Judge em modo QA** (ver `bt/JUDGE.md` § Modo QA): R1–R6 + overflow + coerência das imagens + lessons.md do estilo. Produz `judge-report.md` com `QA: PASS|FAIL`. A barra de score (30/50, craft 6) NÃO se aplica — é do modo livre; aqui o gate é o QA.
4. **Estágio fixes do runner**: se o QA passou sem defeitos, escreva `candidates/A/fixes.md` com `sem fixes — QA PASS direto` e re-renderize o strip (o runner exige strip mais novo que o judge-report). Defeito de copy/imagem → corrija o slot, re-render, re-QA. Defeito estrutural → bug do estilo (lessons.md do estilo; a run para).
5. Finalize normal — mas o marker só adiciona `data-te-description`, e a conversão de um blueprint certificado já foi provada.

Falhou algo estrutural num estilo certificado → é bug do estilo: registre em `lessons.md`, conserte o blueprint, re-certifique. Nunca remende na run.

## Protocolo de certificação (uma vez por estilo)

1. Nasce de uma referência aprovada pelo Gustavo (`reference.png`) — pin, peça de agência, ou vencedor excepcional da pipeline livre.
2. Escrever o STYLE.md (tokens exatos, receitas por papel, slots com limites).
3. Produzir o `strip-blueprint.html` no OpenClaw com loop de render (3 passos do DESIGN.md), com copy de exemplo real.
4. Rodar o corredor inteiro com a copy de exemplo: slice → marker (só descrições) → converter → `validate-slides` exit 0 → **abrir na plataforma e comparar com os screenshots** (gate de fidelidade) → registrar tudo em `certification.md`. **A instância de certificação deve exercitar TODAS as variantes de layout do blueprint** (cada variante de item aparece ≥1 vez na fita certificada) — variante não exercitada no corredor não está certificada e não pode ser sorteada em produção.
5. **Gustavo aprova visualmente** o resultado na plataforma contra a `reference.png`. Só então `status: certificado` no STYLE.md.
6. **Salvar e commitar.** O que fica na pasta do estilo após aprovação (o resto da run de certificação é descartável):

   | Arquivo | Conteúdo |
   |---------|----------|
   | `STYLE.md` | com `status: certificado` |
   | `strip-blueprint.html` | o blueprint final pré-anotado — o ativo principal |
   | `reference.png` | a âncora original |
   | `certification.md` | data, sha256 do blueprint, output dos gates (validate-slides, fidelidade), `template_id` do template de teste em dev, e o slug da run de certificação |
   | `certification-strip.png` | render final aprovado (a prova visual do que foi certificado) |
   | `lessons.md` | (segue vazio/acumulando) |

   Commit imediato: `git commit -m "style: certifica <slug>"` + push — o blueprint é código-fonte da fábrica; sem commit, a VPS e o local divergem e a certificação não é reproduzível. Re-certificações = novo commit (o histórico do estilo vive no git). Templates GERADOS pelo estilo não são commitados — vivem em S3/Supabase; `artifacts/` é workspace descartável.

## Roadmap (não construir antes da 1ª certificação provar o fluxo)

- **Fabric-blueprint**: a certificação pode salvar também os `slide-N.json` convertidos com placeholders — runtime patcharia só texto/src em vez de reconverter (elimina a conversão LLM do modo estilo por completo). Construir quando o 1º estilo estiver certificado e estável.
- **Converter determinístico** (código, Playwright → Fabric) para o modo livre.

## Regras do sistema

- Estilo não-certificado NÃO gera template de produção.
- A pipeline livre (best-of-N do DESIGN.md) continua existindo para: criar candidatos a novos estilos e pedidos fora do catálogo. É o laboratório; os estilos são a fábrica.
- Variação dentro do estilo é SÓ o que o blueprint parametriza (copy, imagens, blocos opcionais, nº de slides no range). Mudar layout/cor/fonte na run = violação.
- Cores de marca: o blueprint usa `data-variable` nos pontos certos — o mesmo estilo serve qualquer marca do tenant.
- Escolha do estilo na geração: usuário nomeia OU o context escolhe pelo fit (família × etapa do funil × vertical) declarado no STYLE.md.
