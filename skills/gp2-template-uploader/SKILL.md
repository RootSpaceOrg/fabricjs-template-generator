---
name: gp2-template-uploader
description: "Upload final da Pipeline GetPosts v2: lê slide-N.json + manifest.json do converter, gera descrição narrativa a partir do template-summary.md do marker, faz upload para S3 e insere em public.templates no Supabase. Suporta ambientes dev e prod (default: prod). Use após gp2-template-converter (validator exit 0)."
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

**Standing rule do Gustavo:** quando HTML reviewer e Fabric validator passam, suba automaticamente com `template_type: ai`, `status: draft`, `owner_user_id: templateGenerator`, `scope: platform`. Ambiente padrão: **prod**. Não pergunte confirmação — é a regra padrão.

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

## Ambientes (dev / prod)

Default: **prod** (quando o usuário não especifica).

| Setting | dev | prod (default) |
|---------|-----|----------------|
| AWS env file | `aws-credentials-template-generator-mkt-platform-dev.env` | `aws-credentials-template-generator-mkt-platform-prod.env` |
| Role ARN | `arn:aws:iam::656032436386:role/TemplateGenerator` | `arn:aws:iam::692046683598:role/TemplateGenerator` |
| SSM parameter | `/default/supabase-database-credentials` | `/default/supabase-database-credentials` |
| S3 bucket | `mkt-platform-templates-dev` | `mkt-platform-templates-prod` |

- AWS region: `sa-east-1` (ambos)
- Supabase table: `public.templates` (ambos)
- Credentials path: `/root/.openclaw/workspace/secrets/<env file acima>`

Selecione com `--environment dev` ou `--env dev`. Sem flag = prod.

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
  "metadata": {},
  "images": [
    { "order": "0", "imageId": "0" },
    { "order": "1", "imageId": "1" }
  ],
  "description": "Descrição Geral:\n...",
  "status": "draft",
  "template_type": "ai",
  "owner_user_id": "templateGenerator",
  "created_by": "templateGenerator",
  "content_type": "instagram-feed",
  "business_type": "",
  "tags": ["tag1", "tag2"],
  "scope": "platform"
}
```

Campos opcionais (omitidos = null no DB):
- `tenant_id` — preencher quando o usuário especificar tenant
- `vertical_id` — preencher quando o usuário especificar vertical

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

Default é dry-run em **prod**. Inspecione o payload antes de executar. Para gravar em produção:

```bash
python skills/gp2-template-uploader/scripts/import-template.py \
  artifacts/gp2-template-converter/<slug>/ \
  --name "Nome do Template" \
  --business-type multi-nicho \
  --tags "tag1,tag2" \
  --description-hint "$(cat artifacts/gp2-template-marker/<slug>/template-summary.md)" \
  --status draft \
  --execute
```

Para gravar em **dev**:

```bash
python skills/gp2-template-uploader/scripts/import-template.py \
  artifacts/gp2-template-converter/<slug>/ \
  --name "Nome do Template" \
  --env dev \
  --execute
```

## Checklist antes de `--execute`

Reporte antes de executar:

- ambiente (dev ou prod);
- nome do template;
- número de slides;
- S3 bucket e padrão de chave;
- campos do Supabase (exceto secrets), confirmando `owner_user_id: templateGenerator`, `scope: platform` e `status: draft`;
- resumo da descrição gerada;
- resultado do validador.

Após execução, reporte:

- template ID inserido;
- chaves S3 carregadas;
- status do insert no Supabase;
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
Environment: dev | prod
Template ID: <id>
Slides: <N>
S3 keys: <lista>
Supabase: inserido | falhou — <motivo>
Cleanup: aguardando orquestrador | (uploader não apaga — responsabilidade do gp2-pipeline)
```

O uploader **não** apaga artifacts — ele só reporta o resultado. A limpeza é responsabilidade do orquestrador (`gp2-pipeline`) após receber o template ID confirmado.
