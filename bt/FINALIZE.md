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

5. Troque o src das imagens geradas no `template.html` (era picsum stand-in) e re-renderize screenshots. Assets SVG da biblioteca ficam com src `file://` local — viram vetor nativo no passo 3, não sobem pro S3.
7. Falhou 2×? Pare e reporte — nunca publique com stand-in/placeholder.

## 2. Marcação

Rode `skills/gp2-template-marker/` no `template.html` final. O marker aplica `data-template-element`/`data-image-type`/`data-text-type`/`data-variable` (use o mapeamento do design-notes.md como guia) e emite `template-summary.md`. Audite com `scripts/audit-template-markup.py` (máx 2 fixes).

## 3. Conversão Fabric

**Nota seamless:** o `template.html` fatiado tem elementos com `left` negativo ou passando de 1080 (decoração/imagem que cruza a fronteira — intencional). O Fabric renderiza clipado pelo canvas, isso é o esperado. Se `validate-slides.js` ou o self-check do converter reprovarem coordenada fora do canvas **em elemento decorativo/imagem**, não "conserte" movendo o elemento (quebra a continuidade) — reporte o caso com o objeto e a regra que reprovou, para decidirmos ajustar a tolerância do validador. Copy/editável fora do canvas é bug de verdade (zona de segurança violada no design).

Rode `skills/gp2-template-converter/` para emitir `output/slide-N.json` + `manifest.json`, **e antes do `center-clippable-images.js`** troque os assets da biblioteca por vetor nativo:

```bash
python bt/scripts/svg_assets.py swap artifacts/bt/<slug>/output/
```

Cada asset vira um objeto `type: path` (recolorível no editor, sem S3). Só então rode `center-clippable-images.js` (as imagens reais restantes) e a self-validation (máx 2 fixes). Se `validate-slides.js` reprovar o tipo `path` (validador conhece só os tipos da pipeline genérica), reporte a regra exata — decidimos a tolerância juntos; não converta o asset de volta pra raster silenciosamente. Gate final:

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
