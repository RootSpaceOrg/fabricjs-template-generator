---
name: gp2-business-template
description: "Cria UM template final, específico de negócio (business_type da plataforma: laserterapia, dentista, nutricionista, etc.) a partir de uma ideia em linguagem natural. É o oposto do gp2-template-suggester: em vez de carrossel genérico multi-nicho, produz uma peça aplicada ao negócio — jargão do nicho permitido, CTA de serviço permitido, professionalPhoto permitido, e IMAGENS GERADAS POR IA (sem placeholder) quando uma imagem específica eleva o design. Orquestra as mesmas sub-skills da pipeline v2 (interpreter → art-director → [image-gen] → html-designer → reviewer → marker → converter → uploader) sem alterar nenhuma delas. Use quando o usuário pedir 'template para <negócio>', 'template específico de <nicho>', 'template final para <ideia + negócio>'."
---

# gp2-business-template

Pega **uma ideia + um business_type** e entrega **um template final publicado** na plataforma, com a especificidade que o catálogo genérico não tem. Não altera `gp2-pipeline` nem `gp2-template-suggester` — é um orquestrador irmão que chama as mesmas sub-skills com doutrina invertida.

## Inputs

| Parâmetro | Obrigatório | Exemplo |
|-----------|-------------|---------|
| Ideia | sim | "carrossel sobre mitos da depilação a laser" |
| `business_type` | sim | `laserterapia`, `dentista`, `nutricionista` — **validado contra o cadastro real** do tenant/vertical (`resolve_tenant.py`), nunca string inventada |
| Etapa do funil | não | `topo` / `meio` / `fundo` — se o usuário não disser, a skill classifica pela ideia e declara no relatório |
| Referência visual / regras de estilo | não | imagem anexa ou texto (ex: prompt_laserpro.txt) |
| `tenant_id` / `vertical_id` / `scope` | não | default: scope=platform, tenant/vertical null |
| Ambiente | não | default **prod**; "em dev" → dev |

## Doutrina business-applied (inverte o multi-nicho do suggester)

Estas diretrizes entram no brief que vai para o interpreter/art-director/designer:

- **Jargão do nicho é ENCORAJADO.** "Paciente", "consultório", "sessão", "avaliação" — a copy deve soar como o profissional daquele negócio fala.
- **CTA de serviço PERMITIDO.** "Agende sua avaliação", "Chame no WhatsApp" são válidos; escolha o CTA que serve o objetivo da peça.
- **`professionalPhoto` PERMITIDO** quando o negócio vende confiança pelo rosto (saúde, estética). Decisão do art-director.
- **Iconografia e metáforas do setor PERMITIDAS.**
- **Tema específico > tema universal.** "5 mitos sobre depilação a laser" ✅ / "5 mitos que te impedem de crescer" ❌ (isso é trabalho do suggester).
- **Composição autoral por default.** O brief marca `Fidelidade: autoral` — o art-director desenha os anchors a partir do conteúdo (A0-custom-autoral em todos os slides); o catálogo A1–A14 é só inspiração. É isso que evita o "cheiro de template". Se o usuário anexar referência com verbo de recriação, `recreate` normal vence.
- **Editabilidade continua obrigatória**: todos os `data-template-element` / `data-variable` normais. Específico ≠ hardcoded — outro profissional do MESMO nicho ainda adapta a peça no editor.

## Memória de contexto por business_type (obrigatório antes de gerar)

Antes de qualquer etapa criativa, a skill precisa **saber do que está falando**. Nada de copy inventada de cabeça — o brief nasce de um dossiê pesquisado.

**Arquivo:** `skills/gp2-business-template/knowledge/<business_type>.md`

1. **Se o arquivo existe e `updated:` tem ≤30 dias** → use direto. Não repesquise.
2. **Se não existe ou está vencido** → pesquise na web (busca atual, não conhecimento de treino) e escreva/atualize o dossiê com estas seções:

```markdown
---
business_type: <slug>
updated: <YYYY-MM-DD>
---
## Público e dores          ← quem contrata, o que dói, objeções comuns
## Mitos e dúvidas frequentes ← matéria-prima direta para carrosséis
## Jargão do nicho          ← termos que o profissional usa (e o público entende)
## Ângulos que performam    ← formatos/temas com tração no Instagram do nicho hoje
## Restrições e compliance  ← o que NÃO pode afirmar (ex: saúde → sem promessa de resultado, regras de conselho profissional)
## Sazonalidade             ← datas/campanhas relevantes do nicho (ex: Janeiro Branco, Outubro Rosa)
```

3. **Injete o dossiê no pedido do interpreter** — a copy do brief deve citar dores/mitos/jargão reais do dossiê, e o reviewer de conteúdo é a seção de compliance: afirmação que viola `## Restrições` é blocker, corrija a copy antes de seguir.

O arquivo é memória permanente da skill: cada business_type pesquisado uma vez serve todos os templates seguintes daquele nicho por 30 dias.

## Cabeça de marketing — funil sempre

Todo template desta skill existe para mover alguém no funil. Classifique o pedido (ou aceite a etapa que o usuário declarou) e deixe a etapa amarrar as decisões:

| Etapa | Papel | Temas típicos | CTA típico | Objetivos (taxonomia do suggester) |
|-------|-------|---------------|-----------|-------------------------------------|
| `topo` | Atrair quem não conhece a marca | mitos, curiosidades, erros comuns, "sinais de que você precisa de X" | "Salve", "Compartilhe", "Siga para mais" | aquisicao, engajamento |
| `meio` | Educar e construir confiança | como funciona o tratamento/serviço, antes-e-depois de processo, bastidores, comparações honestas | "Comente <palavra>", "Me chama no direct pra saber mais" | educacao, posicionamento, retencao |
| `fundo` | Converter quem já considera | prova social, resultados, FAQ de objeções ("dói?", "quanto custa?", "quanto tempo dura?") | "Agende sua avaliação", "Chame no WhatsApp", "Link na bio" | prova_social |

- Reuse os **frameworks narrativos** do [`gp2-template-suggester`](../gp2-template-suggester/references/objectives-and-frameworks.md) compatíveis com o objetivo da etapa — a taxonomia já existe, não invente outra.
- A etapa entra: no brief (tom + CTA coerentes), nas **tags do upload** (`funil-topo` | `funil-meio` | `funil-fundo`) e no relatório final.
- Se a ideia do usuário conflita com a etapa declarada (ex: pediu "fundo" com tema de curiosidade genérica), aponte o conflito em 1 linha e proponha o ângulo que serve a etapa — não gere peça de funil confuso.

## Imagens geradas por IA (o diferencial desta skill)

A pipeline genérica usa picsum (B2) ou placeholder (B3). Aqui, **nada de placeholder**:

- Após o art-director emitir `visual-plan.md`, revise a tabela `## Imagens declaradas`:
  - Toda linha **B3 (placeholder-required)** → vira imagem gerada.
  - Linhas **B2 (picsum)** onde uma imagem sob medida elevaria claramente o slide (capa/hero, imagem conceito central) → vira imagem gerada. B2 continua válido para apoio secundário.
  - **B1 (slots: brandLogo, professionalPhoto, instagramProfilePicture)** → intocado; é preenchido pelo usuário em runtime.
- Prompt de geração = **assunto do slide** (da copy/tema, específico do negócio) + **`## Registro visual das imagens`** do visual-plan (estilo, luz, paleta) + formato/dimensões do slot. Sem texto renderizado dentro da imagem — texto é HTML.
- Gere, suba para S3 e **substitua a linha da tabela no `visual-plan.md`** pela URL final antes de chamar o designer. O designer só consome a tabela — nenhuma mudança nele.

### Como gerar

**Caminho principal: a ferramenta de geração de imagem do próprio runtime (OpenClaw).** Gere a imagem com a tool nativa usando o prompt (assunto + registro visual + dimensões), salve em `artifacts/gp2-business-template/<slug>/images/<nome>.png` e use o script só para subir e obter a URL:

```bash
python skills/gp2-business-template/scripts/generate-image.py \
  --file artifacts/gp2-business-template/<slug>/images/cover.png \
  --s3-key "editor_templates/{template_id}/assets/cover.png" \
  --env prod
```

**Fallback (runtime sem tool de imagem):** o script chama a OpenAI direto com `--prompt "<assunto + registro visual>" --size 1024x1536 --out <path>` — exige `OPENAI_API_KEY` no env ou `--key-file <path>`. Nunca logar a key.

- O script imprime a URL pública do objeto. **Valide antes de seguir** (`curl -sI <url>` → 200). Se o bucket de templates não servir público pelo host S3, passe `--public-base <base CDN>` e reporte ao usuário qual base funcionou — o gate final é o `center-clippable-images.js`, que falha se a URL não carregar.
- Gere a imagem **1 vez e reuse a URL** — não regenere a cada iteração do designer.

## Workflow

0. **Resolver tenant + business_type** (mesmo padrão da skill healthmarket-template-suggestions):

   ```bash
   python skills/gp2-business-template/scripts/resolve_tenant.py \
     --tenant <tenant> --vertical <vertical> --subject "<business_type pedido>" --env <env>
   ```

   Default sem indicação do usuário: `--tenant kultivai --vertical health`. Trate os exit codes:
   - `0` → use `matchedBusinessType.value` como slug canônico em TUDO (dossiê, tags, `--business-type` do upload).
   - `2` (tenant/config não existe) ou `3` (sem businessTypes cadastrados) → pare e reporte o `adminLink` para o usuário cadastrar. Não invente slug.
   - `4` (assunto não casa) → mostre os `businessTypes` disponíveis retornados e pergunte qual usar (ou peça cadastro via `adminLink`). Não force um match.

   Auth: `scripts/aws_auth.py` (mesmos arquivos de credenciais do uploader, role `TemplateSuggesterRole`; fallback SSO local `mkt-platform-{env}` fora do OpenClaw).

0b. **Contexto + funil** — carregue ou pesquise o dossiê `knowledge/<business_type>.md` (regra dos 30 dias acima, arquivo nomeado pelo slug canônico do passo 0). Classifique a etapa do funil (ou aceite a declarada). Escolha o objetivo + framework compatíveis com a etapa.
1. **Brief** — rode `gp2-request-interpreter` com: a ideia, a doutrina business-applied acima, o **dossiê de contexto** (dores/mitos/jargão que a copy deve usar; restrições que a copy não pode violar), a **etapa do funil + CTA coerente**, e o sinal de **composição autoral** (o brief sai com `Fidelidade: autoral`, salvo referência com verbo de recriação → `recreate`).
2. **Direção** — rode `gp2-art-director` normal (free ou reference-driven).
3. **Imagens** — aplique a seção "Imagens geradas por IA": gere, suba, patcheie o `visual-plan.md` (registre em `## Histórico de revisões` o que foi substituído).
4. **Design → validação** — rode `gp2-html-designer`, `gp2-html-reviewer`, `gp2-template-marker`, `gp2-template-converter` exatamente como o `gp2-pipeline` faz, com a mesma política de iteração (reviewer 2 revisões, marker 2 fixes, converter 2 fixes).
5. **Upload** — `import-template.py` com os campos de negócio:

```bash
python skills/gp2-template-uploader/scripts/import-template.py \
  artifacts/gp2-template-converter/<slug>/ \
  --name "<nome>" \
  --template-type userReady \
  --business-type "<matchedBusinessType.value do passo 0>" \
  --tags "<business_type>,funil-<etapa>,<tema>" \
  --tenant-id <tenantId resolvido> --vertical-id <verticalId resolvido> --scope vertical \
  --description-hint "$(cat artifacts/gp2-template-marker/<slug>/template-summary.md)" \
  --env <env> --execute
```

   Standing rule continua: `status: review`, `owner_user_id: templateGenerator`. Deltas desta skill: `template_type: userReady` (o template é final, pronto para o usuário usar direto — diferente do `ai` da pipeline genérica, que serve de matéria-prima para a IA contextualizar), `business_type` com o slug canônico, e `scope=vertical` com o tenant/vertical resolvidos no passo 0 (o usuário pode pedir `scope platform` explicitamente para catálogo global).
6. **Relatório** — template ID, business_type, **etapa do funil + objetivo + framework**, dossiê usado (data do `updated:`), imagens geradas (quantas, URLs), gates PASS/FAIL.

## Não faça

- ❌ Não altere `gp2-pipeline`, `gp2-template-suggester` nem as sub-skills — esta skill só orquestra e injeta doutrina via brief/visual-plan.
- ❌ Não use esta skill para catálogo genérico — isso é o suggester.
- ❌ Não gere imagem com texto/copy renderizado dentro dela.
- ❌ Não deixe placeholder (`image-placeholder.b64.txt`) no template final — se a geração falhar 2×, pare e reporte, não faça fallback silencioso.
- ❌ Não pule editabilidade (`data-template-element`) por o template ser "final".
- ❌ Não escreva copy sem o dossiê de contexto carregado — copy de cabeça é como nasce o "AI slop" genérico que esta skill existe para evitar.
- ❌ Não misture etapas de funil na mesma peça (tema de topo com CTA de fundo, etc.) — 1 template = 1 etapa = 1 CTA coerente.
- ❌ Não invente slug de business_type — só use `value` retornado pelo `resolve_tenant.py`. Sem match (exit 4) ou sem cadastro (exit 3), a resposta é o `adminLink`, não um chute.
