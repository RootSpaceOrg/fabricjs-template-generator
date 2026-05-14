---
name: gp2-template-uploader
description: "Upload final da Pipeline GetPosts v2: lê slide-N.json + manifest.json do converter, gera descrição narrativa a partir do template-summary.md do marker, faz upload para S3, insere em public.templates no Supabase, e abre o editor para gerar thumbnails via 'Salvar Alterações'. Use após gp2-template-result-reviewer (PASS ou PASS_WITH_WARNINGS). Substitui a dependência externa da v1."
---

# gp2-template-uploader

Importa os slides Fabric.js gerados pela pipeline v2 para o produto HealthMarket.

## Safety first

Esta skill escreve em S3 e Supabase de produção. Antes de executar:

- confirme que o usuário quer upload agora, **a não ser** que a standing rule do Gustavo se aplique (gates todos passaram);
- rode dry-run primeiro;
- nunca exiba secrets em log;
- não sobrescreva um template existente a não ser que explicitamente solicitado;
- não execute se `validate-slides.js` não passou (exit 0).

**Standing rule do Gustavo:** quando HTML reviewer, Fabric validator e result reviewer passam, suba automaticamente com `template_type: ai`, `status: draft`, `user_id: public`. Abra o editor e clique "Salvar Alterações" para gerar thumbnails. Não pergunte confirmação — é a regra padrão.

## Inputs esperados

Pasta produzida pelo `gp2-template-converter`:

```text
artifacts/gp2-template-converter/<slug>/
├── output/
│   ├── slide-1.json
│   ├── slide-2.json
│   └── manifest.json
└── conversion-report.md
```

E `template-summary.md` do marker (substitui `context-analysis.json` da v1):

```text
artifacts/gp2-template-marker/<slug>/template-summary.md
```

## Endpoints de produção

- AWS env file: `/root/.openclaw/workspace/secrets/aws-credentials.env`
- Assume role: `arn:aws:iam::425008492512:role/TemplateSuggestionActionRole`
- AWS region: `sa-east-1`
- SSM parameter: `supabase-database-credentials`
- S3 bucket: `healthmarket-templates-prod`
- Supabase table: `public.templates`

Leia `references/discovery-notes.md` para detalhes do schema AWS/Supabase e caveats de S3.

## Preflight obrigatório

1. Valide os slides com o validador do repositório:

```bash
node ../../scripts/validate-slides.js artifacts/gp2-template-converter/<slug>/output/
```

2. Inspecione elementos de template:
   - Todo objeto com `isTemplateElement: true` deve ter `templateElement.description`, `minChars`, `maxChars` úteis.
   - Imagens devem ter `imageType` e `templateElement.description`.
   - Variáveis de perfil devem usar `textType` e **não** ser `isTemplateElement`.

3. Carregue `template-summary.md` do marker como `--description-hint`. A descrição final no Supabase deve priorizar o arco narrativo do post, não listar campos editáveis.

## Regra de descrição

A `description` do template deve explicar **que história o template conta** e **como cada slide move o leitor adiante**.

Não detalhe campos editáveis. Use `template-summary.md` como fonte semântica principal. Estrutura esperada:

```text
Descrição Geral:
Modelo adaptável: "<nome do arco narrativo>"

Propósito do template:
<jornada que o template suporta>.

Layout e estrutura:
<composição, hierarquia, número de slides, CTA e lógica visual>.

Dinâmica do carrossel:
- Lâmina 1 — <papel/título>
  Função: <o que este slide faz na história>.
  Estrutura: <padrão de conteúdo, não nomes de objetos>.
- Lâmina N — CTA / fechamento
  Função: ...
  Estrutura: ...

Uso recomendado:
<quando usar, nicho/campanha/contexto e resultado que apoia>.
```

Se a análise narrativa for fraca ou ausente, infira a partir dos títulos/corpo dos slides. Não liste campos editáveis a não ser para debug de upload falho.

## Schema do banco

Insert em `public.templates`:

```json
{
  "id": "<nanoid gerado>",
  "name": "<nome do template>",
  "width": 1080,
  "height": 1350,
  "metadata": {
    "tags": [],
    "contentType": "instagram-feed",
    "businessType": ""
  },
  "images": [
    { "order": "0", "imageId": "0" },
    { "order": "1", "imageId": "1" }
  ],
  "description": "Descrição Geral:\n...",
  "status": "draft",
  "template_type": "ai",
  "user_id": "public"
}
```

Para multi-slide, uma entrada `images` por `slide-N.json` com `order` e `imageId` iniciando em `"0"`. Não envie `embedding` manualmente.

## Padrão de chave S3

```text
editor_templates/{template_id}/{image_id}/template.json
```

Exemplo:

```text
editor_templates/_RFWfXL-V7hi-EQ5X-gZv/0/template.json
```

## Script de upload

```bash
python skills/gp2-template-uploader/scripts/import-template.py \
  artifacts/gp2-template-converter/<slug>/ \
  --name "Nome do Template" \
  --business-type multi-nicho \
  --tags "tag1,tag2" \
  --description-hint "$(cat artifacts/gp2-template-marker/<slug>/template-summary.md)"
```

Default é dry-run. Inspecione o payload antes de executar. Para gravar em produção:

```bash
python skills/gp2-template-uploader/scripts/import-template.py \
  artifacts/gp2-template-converter/<slug>/ \
  --name "Nome do Template" \
  --business-type multi-nicho \
  --tags "tag1,tag2" \
  --description-hint "$(cat artifacts/gp2-template-marker/<slug>/template-summary.md)" \
  --status draft \
  --user-id public \
  --execute
```

### Gerar thumbnails após upload

Após S3 upload + Supabase insert, o produto gera thumbnails abrindo o editor e clicando "Salvar Alterações":

```bash
GETPOSTS_EDITOR_PASSWORD='<password>' \
python skills/gp2-template-uploader/scripts/import-template.py \
  artifacts/gp2-template-converter/<slug>/ \
  --name "Nome do Template" \
  --business-type multi-nicho \
  --tags "tag1,tag2" \
  --description-hint "$(cat artifacts/gp2-template-marker/<slug>/template-summary.md)" \
  --execute \
  --generate-thumbnails
```

Padrões:
- editor base URL: `https://d3iy4qbtnfohd6.cloudfront.net`
- editor email: `neo.full.1778158934933@example.com` (ou `GETPOSTS_EDITOR_EMAIL`)
- senha: `GETPOSTS_EDITOR_PASSWORD` (nunca hardcode)

O helper de browser escreve screenshots/logs em:

```text
artifacts/gp2-template-converter/<slug>/post-upload-editor-save/
```

Se o editor redirecionar para `/modelos` ou o helper reportar `Editor UI did not appear`, trate como bloqueio de produto, não falha de upload. O upload já completou; investigue o editor separadamente.

## Checklist antes de `--execute`

Reporte antes de executar:

- nome do template;
- número de slides;
- S3 bucket e padrão de chave;
- campos do Supabase (exceto secrets), confirmando `user_id: public` e `status: draft`;
- resumo da descrição gerada;
- resultado do validador.

Após execução, reporte:

- template ID inserido;
- chaves S3 carregadas;
- status do insert no Supabase;
- se o thumbnail refresh rodou via editor save;
- warnings.

## Blockers

Se S3 falhar com AccessDenied:
- guarde o payload do dry-run;
- reporte a role/bucket/action que falhou;
- peça ao backend para confirmar permissões IAM e prefixo exato do S3.

Se Supabase falhar:
- reporte HTTP status e erro sanitizado;
- não repita cegamente;
- verifique RLS/service key, colunas obrigatórias e se `embedding` é mandatório.

## Resposta final ao orquestrador

```markdown
Upload: OK | FAIL
Template ID: <id>
Slides: <N>
S3 keys: <lista>
Supabase: inserido | falhou — <motivo>
Thumbnails: OK | falhou — <motivo> | skipped
```
