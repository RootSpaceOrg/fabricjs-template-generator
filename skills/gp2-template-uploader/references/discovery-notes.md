# Discovery notes — GetPosts template upload

These notes were collected from read-only inspection on 2026-05-08.

## AWS access

- Load credentials from `/root/.openclaw/workspace/secrets/aws-credentials.env`.
- Do not print credentials.
- Assume role: `arn:aws:iam::425008492512:role/TemplateSuggestionActionRole`.
- Working AWS region for Parameter Store: `sa-east-1`.
- SSM parameter: `supabase-database-credentials`.
- Parameter value is JSON with keys:
  - `url`
  - `key`

## Supabase table: public.templates

Query used:

```http
GET <supabase-url>/rest/v1/templates?select=*&template_type=eq.ai&limit=5
apikey: <key>
Authorization: Bearer <key>
```

Observed columns on `public.templates`:

- `id` string, e.g. `KLUsr-oI1xrrs1Q6jZJgs`
- `updated_at` timestamp string
- `name` string
- `width` integer
- `height` integer
- `metadata` object
- `images` array
- `description` string
- `embedding` string/vector-like value
- `status` string, observed `published`
- `template_type` string, observed `ai`
- `user_id` string, observed `public`

Observed `metadata` shape:

```json
{
  "tags": [],
  "contentType": "instagram-feed",
  "businessType": ""
}
```

Observed `images` shape:

```json
[
  { "order": "0", "imageId": "0" }
]
```

For multi-slide outputs, use one image entry per slide:

```json
[
  { "order": "0", "imageId": "0" },
  { "order": "1", "imageId": "1" }
]
```

Confirmed S3 object key pattern from Gustavo:

```text
editor_templates/{template_id}/{index}/template.json
```

Example:

```text
editor_templates/_RFWfXL-V7hi-EQ5X-gZv/0/template.json
```

## Description format (v2)

Na pipeline v2, a fonte semântica principal é o `template-summary.md` produzido pelo `gp2-template-marker` (substitui o `context-analysis.json` da v1). O `--description-hint` do script deve receber o conteúdo desse arquivo:

```bash
--description-hint "$(cat artifacts/gp2-template-marker/<slug>/template-summary.md)"
```

O script detecta automaticamente se o context é um summary markdown (campo `_summary`) ou um JSON de context-analysis (campo `slides`), e constrói a descrição de forma adequada.

Estrutura esperada da descrição:

```text
Descrição Geral:
Modelo adaptável: "<arco narrativo>"

Propósito do template:
<o que o template quer que o leitor entenda/sinta/aja>

Arco narrativo:
<conteúdo do template-summary.md>

Layout e estrutura:
<composição, número de slides, hierarquia>

Uso recomendado:
<quando usar, nicho, contexto>
```

## S3 bucket

Bucket:

- `healthmarket-templates-prod`

Read-only S3 inspection with the assumed role failed with `AccessDenied` for `ListObjectsV2`, `GetBucketLocation` and `HeadObject`. So the exact key pattern could not be confirmed from S3.

Gustavo confirmed the production key pattern. Default:

```text
editor_templates/{template_id}/{image_id}/template.json
```

This maps each `images[].imageId`/index to the S3 folder under the template id.

## Insert contract

Default insert payload:

```json
{
  "id": "<generated id>",
  "name": "<template name>",
  "width": 1080,
  "height": 1350,
  "metadata": {
    "tags": [],
    "contentType": "instagram-feed",
    "businessType": ""
  },
  "images": [
    { "order": "0", "imageId": "0" }
  ],
  "description": "Descrição Geral:\n...",
  "status": "review",
  "template_type": "ai",
  "owner_user_id": "templateGenerator",
  "scope": "platform"
}
```

Always insert new generated templates with `owner_user_id: "templateGenerator"`, `scope: "platform"` and `status: "review"`. The previous `user_id: "public"` / `status: "draft"` convention is **legacy** and must not be used.

Do not send `embedding` manually unless the backend requires it. Existing rows contain it, but it may be generated elsewhere or nullable.

Note: default dimensions are now `1080x1350` (feed retrato) to match the v2 pipeline default canvas. The script will auto-detect from manifest.json or the first slide JSON if dimensions differ.

## Post-upload thumbnail generation

Gustavo requested that, after upload, the automation can open the uploaded template in the full editor and click **Salvar Alterações** to trigger product thumbnail generation.

Confirmed editor URL pattern:

```text
https://d3iy4qbtnfohd6.cloudfront.net/editor/{template_id}
```

The uploader supports this with:

```bash
--generate-thumbnails
```

Credentials are intentionally not stored in the script. Use:

```bash
GETPOSTS_EDITOR_EMAIL='neo.full.1778158934933@example.com'
GETPOSTS_EDITOR_PASSWORD='<password>'
```

or pass `--editor-email` / `--editor-password` when appropriate. The helper writes screenshots and `result.json` to `<template-folder>/post-upload-editor-save/`.

## Safety

- Always support dry-run.
- Do not overwrite an existing template id unless explicitly requested.
- Do not log secrets.
- For live upload/insert, confirm with the user unless the standing rule applies (all gates passed).
