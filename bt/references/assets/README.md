# Biblioteca de assets decorativos (SVG)

Vetores orgânicos que CSS não desenha e o contrato proíbe simular (sem pseudo-elementos, sem clip-path exótico). Uso: dispositivos de continuidade e acentos decorativos — **sempre estáticos** (nunca editáveis pelo usuário final).

## Hierarquia de decisão do designer (nesta ordem)

1. **CSS puro primeiro** — bloco de cor, arco (`border-radius`), círculo, diagonal (`transform: rotate` em div), linha reta, tipografia gigante. Cobre a maioria dos dispositivos.
2. **Esta biblioteca** — traço orgânico: onda, rabisco, blob, contornos, grade de pontos.
3. **Imagem gerada** — textura/elemento único que nem CSS nem a biblioteca entregam.

Nunca: SVG inline inventado na hora, ilustração CSS fingindo desenho.

## Catálogo

| Arquivo | O quê | Dimensões | Uso típico |
|---------|-------|-----------|------------|
| `wave-line-1.svg` | onda contínua fina | 2400×200 | fio condutor atravessando a fita inteira |
| `squiggle-1.svg` | rabisco orgânico | 600×600 | acento de canto, energia num slide de gancho |
| `contour-lines-1.svg` | contornos concêntricos | 800×800 | textura de fundo (baixa opacidade), meio-fora do canvas |
| `blob-1.svg` | forma orgânica cheia | 600×600 | fundo de destaque numérico, âncora de foto |
| `dots-grid-1.svg` | grade de pontos | 400×400 | textura editorial de apoio |
| `plus-signs-1.svg` | sinais + espalhados | 300×300 | acento minimalista |
| `underline-scribble-1.svg` | sublinhado à mão | 800×120 | destacar 1 palavra da headline |
| `ring-1.svg` | anel de traço grosso | 600×600 | moldura de número/palavra, meio na fronteira |

## Assets viram vetor NATIVO no Fabric (não raster)

Cada `.svg` tem um `<nome>.fabric.json` pré-computado ao lado (gerado por `python bt/scripts/svg_assets.py build` — rodar só quando a biblioteca mudar). No FINALIZE, `svg_assets.py swap` substitui o objeto de imagem emitido pelo converter pelo **`path` Fabric nativo**: recolorível no editor, nítido em qualquer escala, **sem upload S3 de asset**.

**Uso no HTML do candidato:**
- `<img src="file:///...caminho.../wave-line-1.svg">` com width/height explícitos. Opacidade/rotação/escala via CSS no `<img>` — o swap preserva.
- **Recolorir**: copie o SVG para os artifacts do candidato mantendo o prefixo do nome (`wave-line-1-verde.svg`), troque o hex de `stroke`/`fill`. O swap lê a cor do arquivo apontado pelo src.
- A cor final é a do arquivo; se precisar de decoração que troca com a marca do usuário (`data-variable`), use bloco CSS, não asset (o marker não marca assets).

**Ordem no FINALIZE (importa):** conversão → `svg_assets.py swap <dir-dos-slides>` → `center-clippable-images.js` (o swap remove os src `file://` antes que o centralizador tente baixá-los).

## Crescendo a biblioteca

Faltou um traço que um design pedia? Registre em `bt/evals/lessons.md` (`asset faltante: <descrição>`) — novos assets entram aqui por curadoria, com o mesmo padrão de nome `<tipo>-<n>.svg`.
