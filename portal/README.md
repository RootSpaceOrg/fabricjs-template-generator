# Portal de backoffice

Cockpit da fábrica: ver runs, disparar corredor/turnos, aprovar ou reprovar com
feedback, gerir packs e **editar o conhecimento com commit automático**.

Plano e decisões: [../PLAN-portal.md](../PLAN-portal.md).

| Arquivo | Papel |
|---|---|
| `app.py` | FastAPI: telas Runs, Fila, Packs, Conhecimento |
| `jobs.py` | fila SQLite + worker serial (tipos fechados: corredor/advance/upload/agente) |
| `knowledge.py` | leitura/edição do conhecimento com git commit+push (whitelist de caminhos) |
| `static/portal.css` | estilo |

## Deploy (VPS)

```bash
rsync -a portal/ root@vps:/root/portal/        # ou sftp
systemctl restart factory-portal factory-worker
```

Serviços: `factory-portal` (uvicorn 127.0.0.1:8090) e `factory-worker` (fila).
Caddy publica em `fabrica.kultivai.com.br` com basic auth; UFW libera 80/443
só para IPs do Cloudflare. Senha em `/root/portal/.senha` (não versionada).
