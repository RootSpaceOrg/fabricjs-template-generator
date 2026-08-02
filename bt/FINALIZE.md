# bt-finalize — Imagens, marcação, conversão e publicação

Entrada: candidato vencedor pós-fixes (`template.html` + `design-notes.md` + screenshots finais). Reusa a maquinaria determinística da pipeline genérica — não reimplemente nada dela.

## Regra zero — cadeia de custódia

O que o judge aprovou é EXATAMENTE o que se publica. Antes de começar, calcule e registre `sha256` do `template.html` e do `strip.png` aprovados; todo passo abaixo opera sobre esses arquivos (as únicas mutações permitidas: troca de src de imagem gerada, marcação `data-*` do marker). O relatório final inclui os hashes. Redesenhar, regenerar slide ou "melhorar" qualquer coisa nesta fase é violação — se algo precisa mudar visualmente, volta pro judge, não segue adiante.

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
8. **Re-aprovação obrigatória**: com as imagens reais no lugar, re-renderize o strip e rode o judge em **modo 3 (fidelidade)** — a peça com imagens finais ainda é a peça aprovada? Imagem gerada que muda o caráter visual da fita (outra paleta, outro mood, tema desconexo) = reprova → regenere a imagem com o registro visual correto, não siga com ela.

## 2. Marcação

Rode `skills/gp2-template-marker/` no `template.html` final. O marker aplica `data-template-element`/`data-image-type`/`data-text-type` e — para `data-variable` — segue **EXATAMENTE o mapeamento declarado no design-notes.md, nada além dele**. Regras hard de variável:

- **Fundo neutro (branco, off-white, creme, cinza, near-black) é LITERAL — NUNCA vira `data-variable`.** Marcar fundo claro como variável faz o editor pintá-lo com a cor da marca e destrói o ritmo tonal aprovado (foi a causa do "dark vs light" do run 2).
- Só recebe variável o que o designer declarou: fundos brand explícitos, acentos, CTA.
- Sanity check pós-marcação: conte as variáveis aplicadas vs declaradas — divergência é erro do marker, corrija antes de seguir.

Audite com `scripts/audit-template-markup.py` (máx 2 fixes).

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

## 3b. Gate de fidelidade visual (pós-conversão — o gate que faltava no run 2)

Depois de converter e validar, renderize o resultado REAL: abra o template na plataforma (fluxo do `save-template-in-editor.js`) e capture screenshot de cada slide como o editor renderiza. Compare lado a lado com os screenshots aprovados pelo judge, slide a slide, verificando literalmente:

- [ ] Fundo de cada slide na MESMA família tonal (claro continua claro, dark continua dark)?
- [ ] professionalPhoto/brandLogo presentes e na posição aprovada?
- [ ] Imagens: mesmo conteúdo visual da fita aprovada?
- [ ] Decoração (palavras gigantes, formas, fios) nos mesmos slides e posições (±5%)?
- [ ] Tipografia: mesmas famílias, hierarquia visualmente igual?

Qualquer "não" → **NÃO reporte sucesso**: identifique a etapa que divergiu (marker → variável errada; converter → coords; swap → asset), corrija e re-passe o gate (máx 2 ciclos). Persistindo, pare e reporte com os dois screenshots lado a lado. `validate-slides` PASS não significa nada aqui — ele valida estrutura, este gate valida que a peça publicada É a peça aprovada.

> ponytail: comparação visual pelo agente por enquanto; script determinístico (SSIM por slide via Playwright) é o upgrade quando o fluxo estabilizar.

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
