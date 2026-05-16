---
name: gp2-pipeline
description: "Orchestrator da Pipeline GetPosts v2. Roda em sequência: gp2-request-interpreter → gp2-art-director → gp2-html-designer → gp2-html-reviewer → gp2-template-marker → gp2-template-converter → gp2-template-uploader → editor save/thumbnails. Aplica iteration policy, decide quando seguir/refazer/escalar, e consolida evidências. Pipeline agnóstica a vertical — funciona para qualquer segmento de marca. Use sempre que o usuário pedir para criar um template de social media de ponta a ponta."
---

# gp2-pipeline

Orchestrator oficial da Pipeline GetPosts v2.

## Quando usar

Sempre que o usuário pedir para criar um template de social media completo (post, carrossel, story) e quiser ele publicado no editor. Frases-gatilho:

- "cria um carrossel sobre…"
- "faz um post para [qualquer vertical]…"
- "gera um template de…"
- "publica como draft…"

## Sequência oficial

```
1. gp2-request-interpreter          → brief.md (conteúdo/intenção; em reference-driven mode, marca que há referência visual)
2. gp2-art-director                 → visual-plan.md (família, paleta, composição por slide, movimento memorável, mapeamento data-variable; em reference-driven mode, analisa a(s) imagem(ns) de referência e extrai o vocabulário visual completo)
3. gp2-html-designer                → template.html (3 renders: low/mid/high-fi executando o visual-plan)
4. gp2-html-reviewer                → PASS|REVISE|FAIL (gate técnico + fidelidade ao visual-plan)
5. gp2-template-marker              → template.html marcado + template-summary.md
6. gp2-template-converter           → slide-N.json + manifest.json (inclui self-validation pós-emissão)
7. gp2-template-uploader            → upload S3 + Supabase
8. editor save/thumbnails           → via flag --execute --generate-thumbnails do uploader
9. Cleanup de artifacts             → apaga pasta artifacts/<slug>/ após upload confirmado
10. Relatório consolidado
```

## Iteration policy

| Etapa | Loop interno | Loop externo (orquestrador) |
|-------|--------------|----------------------------|
| Art-director | — | reexecuta se plano estiver incompleto (raro) |
| Designer (low/mid/high-fi) | passos fixos; refaz 1× cada passo se auto-check falhar | — |
| HTML reviewer | — | máx 2 revisões antes de FAIL; se reviewer apontar problema de plano → volta ao art-director |
| Marker audit | — | máx 2 fixes antes de escalar |
| Converter (self-validation) | — | máx 2 fixes antes de escalar |
| Editor save/thumbnails | — | 1 retry após reload/login |

Ao exceder qualquer teto, pare e reporte:

```
[blocked] gate: <nome>
last error: <descrição>
artifacts: <lista de paths>
```

## Gates obrigatórios para upload

Upload **só** acontece quando todos abaixo são verdadeiros:

- `gp2-art-director` produziu `visual-plan.md` completo (família, paleta, plano de slides, movimento memorável, mapeamento data-variable; em reference-driven mode, inclui vocabulário visual extraído da referência);
- `gp2-html-reviewer.status === "PASS"` (findings técnicos críticos = 0; fidelidade ao plano: faithful ou partial com divergências documentadas; execução: adequada ou forte);
- `gp2-template-marker` audit: `PASS`;
- `gp2-template-converter` validator (`validate-slides.js`): exit 0 + self-validation pós-emissão sem criticals;
- nenhuma incompatibilidade catastrófica conhecida com o editor.

Se algum falha:
- Em casos seguros (mecânicos, óbvios), revise automaticamente dentro do loop.
- Em casos que precisam de decisão criativa do usuário, pergunte. Não invente direção.
- Se o HTML reviewer apontar `planFidelity: "diverged"` com divergências não documentadas → devolva ao designer com instrução específica (não ao art-director, a menos que o plano seja o problema).

## Cleanup de artifacts

Após upload confirmado (template ID retornado + S3 keys carregadas + Supabase inserido), apague a pasta de artifacts do slug:

```bash
Remove-Item -Recurse -Force artifacts/<slug>
```

Ou em bash:

```bash
rm -rf artifacts/<slug>
```

**Condições para apagar:**
- Upload retornou template ID (não dry-run).
- Supabase insert confirmado (não falhou).
- Se o editor save/thumbnails falhou mas upload completou, apague mesmo assim — o thumbnail pode ser regerado abrindo o editor manualmente.

**Não apague se:**
- Upload falhou (AccessDenied, Supabase error, etc.) — artifacts são a única evidência para debug.
- Dry-run (sem `--execute`) — nunca apague em dry-run.

Em **batch**, apague slug por slug individualmente à medida que cada um confirma upload. Não agrupe.

## Standing rule do Gustavo

Quando os gates passam, suba **automaticamente** com:

- `template_type: ai`
- `status: draft`
- `user_id: public`

Em seguida, abra o editor (via `--execute --generate-thumbnails` do uploader) e clique "Salvar Alterações" para gerar thumbnails. Não pergunte confirmação — é a regra padrão.

## Comando de upload

```bash
GETPOSTS_EDITOR_PASSWORD='<password>' \
python skills/gp2-template-uploader/scripts/import-template.py \
  artifacts/gp2-template-converter/<slug>/ \
  --name "<Nome do Template>" \
  --business-type multi-nicho \
  --tags "<tag1,tag2>" \
  --description-hint "$(cat artifacts/gp2-template-marker/<slug>/template-summary.md)" \
  --status draft \
  --user-id public \
  --execute \
  --generate-thumbnails
```

Use sempre `--description-hint` apontando para o `template-summary.md` produzido pelo marker. Consulte `skills/gp2-template-uploader/SKILL.md` para detalhes de dry-run, blockers e checklist.

**Nunca exiba secrets em log.** Senha sempre via env var.

## Batch (vários templates)

Quando o usuário pede N templates de uma vez:

- spawn um sub-agent isolado por template (use Agent tool com `subagent_type: general-purpose`);
- dê a cada sub-agent só o pedido específico + esta SKILL.md;
- mantenha pastas de artifacts separadas (`artifacts/<stage>/<slug-1>/`, `<slug-2>/`, ...);
- consolide IDs e evidências ao final.

## Evidência a reportar

Por template processado:

- template ID (do Supabase);
- nome;
- contagem de slides;
- art-director: família estética + composições usadas (A1–A8 por slide);
- HTML reviewer status + findings técnicos + fidelidade ao plano + data-variable cobertura;
- marker audit status;
- converter validator status (exit code);
- upload status;
- thumbnail/editor save status;
- pasta de artifacts;
- paths de evidência (screenshots, visual-plan.md, html-review.md, `template-summary.md`).

## Estrutura de artifacts esperada

```
artifacts/
├── gp2-request-interpreter/<slug>/
│   └── brief.md               ← conteúdo/intenção (sem reference-spec.md — análise visual migrou para art-director)
├── gp2-art-director/<slug>/
│   └── visual-plan.md         ← família, paleta, composição por slide, movimento, data-variable (em reference-driven: inclui vocabulário visual extraído da referência)
├── gp2-html-designer/<slug>/
│   ├── template.html
│   ├── template-v1.html, template-v2.html
│   ├── screenshots/
│   └── notes.md               ← divergências do plano documentadas
├── gp2-template-marker/<slug>/
│   ├── template.html (marcado)
│   ├── marker-audit.json/.md
│   └── template-summary.md
└── gp2-template-converter/<slug>/
    ├── output/slide-N.json
    ├── manifest.json
    └── conversion-report.md
```

## Política de qualidade

- **Não suba template com design fraco**, mesmo que todos os gates técnicos passem. Se você (orquestrador) olhar para os screenshots high-fi do designer e perceber que está medíocre, devolva ao designer com instrução clara em vez de prosseguir.
- **Não force secondary brand color** quando o brief decidiu por primária somente.
- **Não invente skills** que não estão na lista oficial. A v2 tem 7 skills (incluindo gp2-art-director). Se você sente falta de uma 8ª, é provavelmente cerimônia.
- **Não pule o art-director** mesmo que o pedido pareça simples. Sem visual-plan.md, o designer cai de volta no modo v1 (viés de repetição, cores sem papel explícito, data-variable descobertos pelo marker).

## Resposta final por template

```markdown
## Template: <nome>

- **ID:** <Supabase template ID>
- **Slides:** <N>
- **Artifact:** `artifacts/.../<slug>/`

### Direção criativa (art-director)
- Família estética: <nome>
- Paleta: primary `<hex>` / secondary `<hex>`
- Composições: slide1=<A?>, slide2=<A?>, ... (diversidade: <N> tipos distintos)
- Movimento memorável: <nome>
- data-variable mapeados: <N> elementos

### Gates
- Art-director: PASS (visual-plan.md completo)
- HTML reviewer: PASS (técnicos: 0, fidelidade ao plano: faithful, execução: forte)
- Marker audit: PASS
- Converter validator: PASS (exit 0)
- Upload: OK
- Thumbnails: OK
- Cleanup: OK (artifacts/<slug>/ removido)

### Evidências
_(artifacts removidos após upload — template acessível pelo ID acima no editor)_
```

Em batch, consolide todos os blocos com totais ao final.
