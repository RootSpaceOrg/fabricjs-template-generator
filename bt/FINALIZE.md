# bt-finalize — Imagens, marcação, conversão e publicação

Entrada: candidato vencedor pós-fixes (`template.html` + `design-notes.md` + screenshots finais). Reusa a maquinaria determinística da pipeline genérica — não reimplemente nada dela.

## 1. Imagens geradas

Para cada linha `generate` da tabela de imagens do `design-notes.md`:

1. **Gere na ordem: hero primeiro.** Prompt = assunto do slide + `registro visual` do design-notes + dimensões do slot. Sem texto renderizado na imagem.
2. **Demais imagens**: gere como variação/mesma sessão do hero (mesmo registro, mesma luz) — imagens de um carrossel são uma família, não avulsas.
3. Ferramenta: a tool de imagem do runtime. Fallback sem tool: `--prompt` do script (exige `OPENAI_API_KEY`).
4. Suba e valide:

```bash
python bt/scripts/generate-image.py --file artifacts/bt/<slug>/images/<nome>.png \
  --s3-key "editor_templates/{template_id}/assets/<nome>.png" --env <env>
curl -sI <url>   # exige 200; senão --public-base <CDN> e reporte
```

5. Troque o src no `template.html` (era picsum stand-in) e re-renderize screenshots.
6. Falhou 2×? Pare e reporte — nunca publique com stand-in/placeholder.

## 2. Marcação

Rode `skills/gp2-template-marker/` no `template.html` final. O marker aplica `data-template-element`/`data-image-type`/`data-text-type`/`data-variable` (use o mapeamento do design-notes.md como guia) e emite `template-summary.md`. Audite com `scripts/audit-template-markup.py` (máx 2 fixes).

## 3. Conversão Fabric

Rode `skills/gp2-template-converter/`: emite `output/slide-N.json` + `manifest.json`, roda `scripts/center-clippable-images.js`, self-validation (máx 2 fixes). Gate final:

```bash
node scripts/validate-slides.js artifacts/bt/<slug>/output/   # exige exit 0
```

## 4. Upload

```bash
python skills/gp2-template-uploader/scripts/import-template.py artifacts/bt/<slug>/ \
  --name "<nome>" \
  --template-type userReady \
  --business-type "<slug canônico>" \
  --tags "<business_type>,funil-<etapa>,<tema>" \
  --tenant-id <t> --vertical-id <v> --scope vertical \
  --description-hint "$(cat .../template-summary.md)" \
  --env <env> --execute
```

`status review` + `owner_user_id templateGenerator` (default do script). Dry-run primeiro; inspecione o payload.

## 5. Pós-publicação

- Anexe o score do judge em `bt/evals/scores.jsonl` (linha com `"prompt_id":"prod"`).
- Quando o humano rejeitar um template na tela de revisão, registre o motivo em `bt/evals/lessons.md` (`- <data> <template_id>: <motivo em 1 linha>`) — é o loop de feedback; lições recorrentes viram edição em `DESIGN.md`/`CONTEXT.md` (e a edição roda a regressão).
