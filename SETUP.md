# Setup local — GetPosts Pipeline v2

Esta pipeline roda em **Linux** (VPS, openclaw) e **Windows**. Os comandos abaixo usam sintaxe portável (npm/pip); onde a sintaxe difere por OS, o passo é anotado.

## Pré-requisitos

| Tool | Versão mínima | Como checar |
|------|---------------|-------------|
| Python | 3.8+ | `python --version` |
| Node.js | 14+ | `node --version` |
| npm | bundled com Node | `npm --version` |
| ffmpeg (opcional, só para `review-fabric-json.py --visual`) | qualquer recente | `ffmpeg -version` |

Se faltar algum: instale via fonte oficial (python.org, nodejs.org, ffmpeg.org). No Windows o instalador oficial do Node.js já adiciona ao PATH; em alguns Linux pode ser necessário usar `nvm`/distro package manager.

---

## 1. Dependências Python

A partir da raiz da pipeline (`fabricjs-template-generator/`):

```bash
pip install -r requirements.txt
```

A única dependência externa é `boto3` (usado pelo uploader). Os outros scripts Python são stdlib-only.

**Validar:**
```bash
python -c "import boto3; print('boto3', boto3.__version__)"
```
Esperado: imprime versão sem erro.

---

## 2. Dependências Node + Playwright browser

```bash
npm install
npx playwright install chromium
```

- `npm install` baixa o pacote `playwright` para `./node_modules/`.
- `npx playwright install chromium` baixa o binário do Chromium (~150MB) usado em modo headless pelos scripts de render e thumbnail.

**Validar:**
```bash
npm run check-playwright
```
Esperado: imprime `playwright OK` sem erro. Se falhar com "Browser not found", rode `npx playwright install chromium` novamente.

---

## 3. Smoke test dos scripts standalone

```bash
# Validador de Fabric JSON (puro Node, sem deps)
node scripts/validate-slides.js

# Audit de HTML markup (Python stdlib)
python scripts/audit-template-markup.py
```

Ambos devem reclamar de argumento faltante (mensagem de usage). Se reclamarem de import/módulo, há problema de setup.

---

## 4. Credenciais AWS (apenas se for fazer upload via `gp2-template-uploader`)

Os scripts dos passos 1–3 não precisam de AWS. **Pule para o passo 5 se você só vai gerar templates sem subir para Supabase/S3.**

### Onde os arquivos `.env` ficam

Por default, `import-template.py` lê dois arquivos de:

```
/root/.openclaw/workspace/secrets/
├── aws-credentials-template-generator-mkt-platform-dev.env
└── aws-credentials-template-generator-mkt-platform-prod.env
```

Em **Windows** ou em **VPS Linux sem esse path**, defina a variável `GP2_SECRETS_DIR` apontando para onde você guarda os arquivos:

**Linux/VPS:**
```bash
export GP2_SECRETS_DIR="$HOME/.gp2/secrets"
mkdir -p "$GP2_SECRETS_DIR"
```

**Windows PowerShell:**
```powershell
$env:GP2_SECRETS_DIR = "$env:USERPROFILE\.gp2\secrets"
New-Item -ItemType Directory -Force -Path $env:GP2_SECRETS_DIR | Out-Null
```

### Formato de cada arquivo `.env`

```
AWS_ACCESS_KEY_ID=<chave-iam-do-template-generator>
AWS_SECRET_ACCESS_KEY=<segredo-iam>
```

A identidade IAM precisa ter permissão `sts:AssumeRole` para `arn:aws:iam::<account>:role/TemplateGeneratorRole` (account 656032436386 em dev / 692046683598 em prod). Quem fornece as credenciais é o admin da conta AWS da plataforma.

### Validar

```bash
python skills/gp2-template-uploader/scripts/import-template.py --check-credentials --env dev
```

Esperado: imprime JSON com `status: "ok"`, role ARN assumida, e `expiration` em ISO 8601. Sem isso o uploader não vai funcionar — não toque em S3/Lambda enquanto este passo não passar.

Repita para prod se for usar prod (`--env prod`).

---

## 5. Persistir variáveis de ambiente (opcional)

Crie um `.env` na raiz da pipeline (não comitado — está no `.gitignore`):

```
GP2_SECRETS_DIR=/home/user/.gp2/secrets
# GP2_PLAYWRIGHT_DIR=
```

Para que `.env` seja carregado automaticamente:
- **Linux/macOS:** use [`direnv`](https://direnv.net/) (`brew install direnv` ou via gestor de pacotes).
- **Windows PowerShell:** adicione um trecho ao seu perfil (`$PROFILE`) que lê o arquivo.

Sem isso, defina as vars manualmente em cada sessão de shell antes de rodar a pipeline.

---

## Checklist final

- [ ] `python --version` ≥ 3.8
- [ ] `node --version` ≥ 14
- [ ] `pip install -r requirements.txt` rodou sem erro
- [ ] `python -c "import boto3"` OK
- [ ] `npm install` rodou sem erro
- [ ] `npx playwright install chromium` rodou sem erro
- [ ] `npm run check-playwright` imprime `playwright OK`
- [ ] (Se for fazer upload) `GP2_SECRETS_DIR` aponta para diretório com os 2 env files
- [ ] (Se for fazer upload) `--check-credentials --env dev` retorna status OK
- [ ] (Se for fazer upload) `--check-credentials --env prod` retorna status OK

Com esse checklist verde, qualquer skill da pipeline (designer, reviewer, marker, converter, uploader) tem todas as dependências de runtime que precisa.

---

## Solução de problemas

**`render-html-screenshots.js` falha com "Playwright not found":**
1. Confirme que rodou `npm install` dentro de `fabricjs-template-generator/`.
2. Confirme que rodou `npx playwright install chromium`.
3. Se Playwright está em outro local (ex: instalação global), defina `GP2_PLAYWRIGHT_DIR=/caminho/absoluto/para/node_modules/playwright`.

**`import-template.py` falha com "AWS env file not found":**
1. Confirme que `GP2_SECRETS_DIR` está definido na sessão de shell atual.
2. Confirme que os dois arquivos `.env` existem nesse diretório.
3. Rode `--check-credentials` para diagnosticar.

**`import-template.py` falha com `botocore.exceptions.ClientError: AccessDenied`:**
- A identidade IAM nas credenciais não tem `sts:AssumeRole` para o role esperado.
- Verifique com o admin da conta.
