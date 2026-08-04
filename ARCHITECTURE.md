# Fábrica de templates — Arquitetura

Geração de templates desenhada de primeiros princípios em 2026-08-04. As
rodadas anteriores entram aqui só como **restrições aprendidas** — nenhuma
estrutura antiga é herdada por inércia. O que não está neste documento não
existe na fábrica.

## Princípio único

**Motor e conteúdo nunca se misturam.** O motor (design system + conversor + runner) é fixo, genérico e sem opinião estética. Todo conhecimento de design é um **pack acoplável** — dados carregados no motor, nunca regras dentro dele.

```
┌─ MOTOR (fixo, sem estética) ─────────────────────────────┐
│  design-system.css + catálogo de componentes (interface) │
│  convert.js (função fechada HTML→Fabric)                 │
│  assembler/slicer (fita ↔ slides)                        │
│  runner (estados, gates mecânicos)                       │
└──────────────────────────────────────────────────────────┘
             ▲ carrega                    ▲ produz
┌─ PACKS (acopláveis, versionados) ─┐   ┌─ RUN ────────────┐
│  <pack>/tokens.json               │   │ copy (dossiê)     │
│  <pack>/recipes/  (composições)   │   │ imagens (fórmulas)│
│  <pack>/images.md (fórmulas)      │   │ sorteio de recipes│
│  <pack>/lessons.md                │   │ → HTML → Fabric   │
└───────────────────────────────────┘   └───────────────────┘
```

## 1. O motor

### 1a. Design system fechado (a interface entre agente e conversor)

- **Um único `design-system.css`** + catálogo formal de componentes: `ds-headline`, `ds-eyebrow`, `ds-body`, `ds-number`, `ds-watermark`, `ds-photo`, `ds-slot` (professionalPhoto/logo/avatar), `ds-stamp`, `ds-card`, `ds-block`, `ds-cta`… (lista final definida na construção).
- **O agente NÃO escreve CSS.** Escreve HTML semântico: componentes do catálogo + tokens (`--accent`, `--ink`, `--paper`…) + conteúdo. Classe fora do catálogo = rejeição na conversão.
- **Grid declarativo, não px**: cada componente ocupa uma área de grid (12 col × 12 linhas por slide); o browser resolve as coordenadas; o conversor lê o resultado computado. Sobreposição de texto vira impossível por construção (áreas não se sobrepõem, exceto camadas declaradas: watermark/foto-fundo).
- Todo componente já nasce com seus `data-*` (editabilidade, slots, variáveis de marca) e `data-el-id` — marcação não existe como etapa separada.

### 1b. Conversor fechado

- `convert.js` conhece **cada componente formalmente** (tabela componente→objeto Fabric). HTML conforme entra, JSON sai, sem consultar ninguém.
- Violação = rejeição apontando elemento → **regenera o HTML**; nunca se edita JSON. (Doutrina do Gustavo, herdada como lei.)
- Lei de conservação `data-el-id`↔`elId` verificada mecanicamente.

### 1c. Fita e estado

- Slide = arquivo isolado; fita = `assemble` (mecânico) com camada de costura; plataforma = `slice` + convert.
- Runner com estados e gates que **executam** validação (não conferem existência) — provou valor.

## 2. Os packs (conhecimento acoplável)

Um pack = um design conhecido, empacotado como DADOS:

```
packs/<slug>/
├── pack.json      ← tokens (paleta/tipografia/espacamento), fit (funil×vertical), range de slides
├── recipes/       ← composições de slide: grid areas × componentes (JSON/YAML declarativo, não HTML)
├── images.md      ← fórmulas de prompt das imagens geradas + registro visual
├── reference.png  ← âncora visual aprovada pelo Gustavo
├── certification/ ← evidência do corredor completo (1× por versão do pack)
└── lessons.md     ← histórico do pack
```

- O **html generator** (agente) recebe: pack carregado + copy + sorteio de recipes (variação = recombinação do certificado; nunca duas recipes iguais adjacentes). Ele compõe — não inventa layout, não escolhe cor, não escreve CSS.
- Packs são independentes do motor: criar/melhorar um pack nunca toca no motor; melhorar o motor beneficia todos os packs.
- Certificação por versão do pack; rejeições do Gustavo → `lessons.md` do pack; 2× recorrente → corrige recipe e re-certifica.

## 3. Papéis

| Quem | Faz | NUNCA faz |
|------|-----|-----------|
| Agente (html generator) | storyline/copy do dossiê, sorteio e preenchimento de recipes, fórmulas→prompts de imagem | CSS, layout livre, conversão, edição de JSON |
| Motor (código) | grid, conversão, montagem, gates, conservação | escolha estética |
| Judge | QA visual (R-checks, coerência de imagem, fidelidade à reference.png do pack) | régua absoluta sem âncora |
| Gustavo | referência de packs, certificação, aprovação em review, curadoria da pack-queue | — |

## 4. Restrições de design (não-negociáveis)

Padrões banidos por causarem defeito recorrente — a lista imuniza contra regressão:

- **Conversão manual por LLM** (causa raiz de infidelidade visual): a conversão HTML→Fabric é sempre código determinístico.
- **Marcação de metadados como etapa LLM separada**: `data-*` nascem no componente, nunca são adicionados depois.
- **Anchors em px escritos em prosa de spec**: posição vem do grid declarativo resolvido pelo browser.
- **Layout congelado como HTML-modelo**: composição vem de recipes declarativas (variação natural por recombinação).
- **Checklist de design em prosa como protocolo do agente**: o render de conferência valida contra o grid, não contra texto.
- **Documentos normativos de estética no motor**: todo gosto vive em pack; documento de inspiração não é norma.

## 5. O que é lei (pago com sangue)

Runner com gates executáveis · doutrina do conversor · lei de conservação · cadeia de custódia · judge com âncora obrigatória (reference.png do pack) + vereditos mecânicos no runner; curadoria visual aprovada vive em `pack-queue/` (berçário de packs) · dossiê/compliance/espinha narrativa (CONTEXT.md) · upload mecânico do estado · conhecimento sincronizado via git · env imutável · lessons por pack + globais.
