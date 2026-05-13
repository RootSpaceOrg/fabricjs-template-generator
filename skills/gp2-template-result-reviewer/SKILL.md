---
name: gp2-template-result-reviewer
description: "Verifica fidelidade entre o HTML aprovado e o Fabric JSON gerado pelo gp2-template-converter. Roda validate-slides.js (estrutura) + review-fabric-json.py (drift HTML→Fabric, spans duplicados, nomes fracos, metadados ausentes, brand color preserveda). Decide PASS/FAIL antes do uploader. Use após gp2-template-converter, antes do uploader v1 (getposts-template-uploader). Pixel diff opcional quando screenshots do editor estão disponíveis."
---

# gp2-template-result-reviewer

Última checagem antes do upload. Garante que o Fabric JSON não tem drift relevante em relação ao HTML aprovado.

## Inputs

```
artifacts/gp2-template-converter/<slug>/
├── output/
│   ├── slide-1.json
│   └── slide-N.json
├── manifest.json
└── conversion-report.md

artifacts/gp2-template-marker/<slug>/
└── template.html         ← fonte para comparação semântica
```

## Output

```
artifacts/gp2-template-result-reviewer/<slug>/
├── review-report.json
└── review-report.md
```

## Workflow

1. Confirme `output/slide-N.json` existe e o validator do converter já passou.
2. Rode o validator estrutural de novo (defesa em profundidade):

```bash
node ../../scripts/validate-slides.js artifacts/gp2-template-converter/<slug>/output/
```

3. Rode o reviewer semântico, apontando para o HTML marcado como source:

```bash
python3 ../../scripts/review-fabric-json.py artifacts/gp2-template-converter/<slug>/ \
  --source-html artifacts/gp2-template-marker/<slug>/template.html
```

O script gera `review-report.json` + `review-report.md`.

4. Inspecione o relatório. Categorize cada item:

| Categoria | Tratamento |
|-----------|------------|
| **Bloqueante** | drift de posição > 5px, fontSize errado, missing `templateElement` em campo editável, brand color variable perdida, ClippableImage sem campos obrigatórios | `FAIL` |
| **Warning** | nome de layer genérico ("Texto 3"), descrição que ainda parece tema-específica, ambiguidade não-crítica | `PASS_WITH_WARNINGS` |
| **OK** | tudo dentro de tolerância | `PASS` |

5. Decida status:

| Status | Quando |
|--------|--------|
| `PASS` | tudo OK — upload liberado |
| `PASS_WITH_WARNINGS` | warnings leves, mas tecnicamente OK — upload com ressalva |
| `FAIL` | bloqueador encontrado — devolve ao `gp2-template-converter` |

## O que o script checa

`review-fabric-json.py` é determinístico (não renderiza pixels) e cobre:

- root/version/object básico do Fabric;
- center origin em todos os objetos;
- textbox fontSize, lineHeight, charSpacing, wrap risk;
- **spans HTML duplicados como textboxes separadas** (deveriam ser uma textbox com `styles`);
- prefixos `Slide N —` em nomes (proibido);
- descrições genéricas em `templateElement.description` (sem "laserterapia", "premium", etc.);
- textboxes vazias, com apenas check ou numerais soltos;
- backgrounds redundantes (objeto que duplica `canvas.background`);
- `ClippableImage` com campos obrigatórios (`originWidth`, `originHeight`, `cropX`, `cropY`);
- `isTemplateElement` × `textType` conflitos (mutuamente exclusivos);
- `fillVariableConfig`/`strokeVariableConfig`/`backgroundVariableConfig` preservados quando o HTML tinha `data-variable`;
- nomes duplicados entre objetos;
- comparativo opcional com `review-manifest.json` (geometria esperada).

## Pixel diff opcional

Quando o usuário relata "o HTML parece diferente do editor", e screenshots do editor estão disponíveis:

```
artifacts/gp2-template-result-reviewer/<slug>/review/
├── html/slide-N.png        ← render do template.html (use scripts/render-html-screenshots.js)
└── product/slide-N.png     ← export do editor HealthMarket
```

Rode:

```bash
python3 ../../scripts/review-fabric-json.py artifacts/gp2-template-converter/<slug>/ \
  --source-html artifacts/gp2-template-marker/<slug>/template.html \
  --visual
```

O script escreve diffs em `review/diff/slide-N.png`. Use `--visual-required` quando review visual for obrigatório (falha se as imagens não existirem).

Se browser automation/export endpoint não está disponível, **diga isso explicitamente** — não finja que o pixel review rodou.

## Loop de correção

Máximo **2 fixes** devolvidos ao converter. Se ainda falhar, escale.

Formato de correção para o converter:

```
FAIL — bloquear upload.
Slide 2 / `Título principal`: top drift +26px. Mover objeto Fabric para top - 26.
Slide 3 / `Corpo`: fontSize esperado 38, got 42. Reduzir para 38.
Slide 5 / `Foto`: ClippableImage sem cropX/cropY. Recalcular cover crop a partir das dimensões naturais.
```

## Resposta final ao orquestrador

```markdown
Result review: PASS|PASS_WITH_WARNINGS|FAIL
Slides: <N>
Validator: PASS|FAIL
Semantic: PASS|FAIL (<N> bloqueantes, <M> warnings)
Pixel diff: <rodou|não rodou — sem screenshots do editor>
Próximo passo: getposts-template-uploader (v1) | gp2-template-converter (fix) | bloquear
```

## O que NÃO fazer

- Não crie design aqui.
- Não suba o template aqui — esse é o uploader.
- Não rode validador customizado paralelo — sempre `validate-slides.js` + `review-fabric-json.py`.
- Não invente warnings para mostrar serviço — só reporte o que o script emitiu ou o que você verificou visualmente com evidência.
