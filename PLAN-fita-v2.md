# Plano — Fábrica v2 (fita-first, pack como conhecimento)

Status: **PLANO APROVADO EM DISCUSSÃO — nada implementado ainda.**
Motivação: a v1 endureceu design em recipes/gates (split-pair, pares,
espelhados, draws.log) — não escala. A v2 devolve o design ao designer e
concentra a rigidez onde ela paga: contrato HTML→JSON determinístico e leis
objetivas de legibilidade.

## 1. Arquitetura-alvo (papéis)

```
pedido → resolve (script)
       → COPY SPECIALIST (LLM)  conhecimento: copy geral + por negócio
       → DESIGNER (LLM)         conhecimento: design geral + pack (estilo)
         ↳ entrega UMA fita.html (n seções + camada de travessia)
       → render (script) → convert modo-fita (script) → judge (LLM, leis+referência)
       → finalize → upload (scripts)
```

- **Pack** = skill de estilo: sabe contextualizar, guarda técnicas, boas
  práticas, feedbacks, tokens e regras que criam dinâmica DENTRO do estilo.
  Não dita coordenadas.
- **Copy specialist** = melhor ideia de carrossel: storyline, textos, briefs
  de imagem; conhecimento por tipo de negócio.
- **Designer** = interpreta pedido (+pack) e compõe a fita inteira num HTML
  com regras claras (catálogo). Par contínuo, decor cruzando emenda etc.
  viram simplesmente elementos posicionados sobre a fronteira.
- **Scripts** = tudo que não precisa de interpretação: conversão, validação,
  slicing, upload, resolvers.

## 2. Organização do conhecimento (novo)

```
knowledge/
├── copy/
│   ├── geral.md                  # leis de copy p/ qualquer negócio (funil,
│   │                             # arco narrativo, tom, compliance-pointer)
│   └── negocios/<business>.md    # dores, temas, vocabulário, CTAs típicos
│                                 # (migrar dossiês existentes de knowledge/)
├── design/
│   └── geral.md                  # leis de design p/ qualquer pack: hierarquia,
│                                 # legibilidade, respiro, tratamento de foto,
│                                 # decor nunca sobre texto/CTA/logo/foto-perfil
└── (compliance/ segue como está)

packs/<slug>/
├── pack.json          # tokens, fontes, fit, assinaturas (sem sorteio-lei)
├── reference.png      # âncora do judge
├── exemplos/          # fitas APROVADAS (png) + esqueletos html de partida
│                      # (ex-recipes, rebaixadas a exemplo não-vinculante)
├── tecnicas.md        # dinâmicas do estilo COMO TÉCNICA: par contínuo,
│                      # decor voando (overhang), duo-tom entrelaçado, costuras
├── images.md          # fórmulas de geração de imagem (mantém)
└── lessons.md         # vereditos (mantém)
```

Regra de precedência: geral < pack < lessons (mais específico vence).

## 3. Contrato da fita (CATALOG v2)

- **Um HTML por run**: `<main class="fita" data-pack data-n="N">` contendo
  `N × <section class="slide" data-role="abertura|item|fechamento">`
  (cada seção mantém o grid 12×12 e os componentes ds-* de hoje) +
  `<div class="fita-layer">` para elementos que **cruzam fronteiras**
  (grid da fita: 12·N colunas × 12 linhas).
- Elementos de travessia: só `data-static` + `data-layer` (imagem/forma/
  watermark). **Elemento editável nunca cruza fronteira** (UX do editor).
- Whitelist inline continua: `grid-area` + `transform: rotate()`.
- Morrem: `data-pos`, `seams.json`, `pares`/`espelhados`/`draws.log` no
  draw.json (draw.json inteiro morre — o plano da fita É o fita.html).

## 4. Motor (mudanças determinísticas)

| Peça | Mudança |
|------|---------|
| `convert.js` | **modo fita**: carrega fita.html, W=N·1080; cada nó é emitido em TODO slide que intersecta, com `left = cx − i·1080` (off-canvas; Fabric clipa — mecanismo já provado nas costuras). Editável fora de 1 slide único = REJEITADO. Conservação: todo `data-el-id` em ≥1 JSON. |
| `assemble.js` | simplifica: renderiza fita.html direto (strip.png + slide-N.png por recorte). |
| `run.py` | gates enxutos: fita.html única + data-pack + data-role por seção + N dentro do fit · render atual · conversão+conservação+validate · judge PASS (com checklist de leis) · fidelity · upload. **Remove** gates de pares/espelhados/draws.log. |
| morrem | `split-pair.py`, `apply-seams.py`, CSS de `data-pos`. `data-overhang` fica (útil e barato). |

## 5. O que continua rígido (de propósito)

1. Catálogo fechado + conversor com rejeição + lei de conservação.
2. Esqueleto narrativo: 1ª seção `abertura`, última `fechamento` (gate).
3. Leis de legibilidade no JUDGE.md como checklist obrigatório: texto nunca
   sob decor; CTA/logo/foto-perfil limpos; contraste; sem promessa (compliance).
4. Judge ancorado em `reference.png` + exemplos aprovados; aprovação final do
   Gustavo por fita.

## 6. Fases de execução (cada uma entregável e reversível)

- **F0 — congelar**: tag git `pre-fita-v2`. Nada quebra o que existe.
- **F1 — motor**: convert modo-fita + assemble simplificado + smoke sintético
  (fita 3 slides com objeto cruzando fronteira; comparar com o resultado que
  o apply-seams antigo produzia — mesma geometria = aprovado).
- **F2 — contrato**: CATALOG v2 + run.py v2; deletar ferramentas/gates órfãos
  (git recupera se precisar).
- **F3 — conhecimento**: criar knowledge/copy/{geral,negocios/*} e
  knowledge/design/geral; pack 1: recipes→exemplos, escrever tecnicas.md a
  partir das lessons; reescrever README/ARCHITECTURE/SKILL/PACKS.
- **F4 — prova real**: 2 gerações do MESMO tema + 1 de tema novo via OpenClaw.
  Aceite: par contínuo emendando · variância visível entre as 2 · corredor
  verde · veredito do Gustavo.
- **F5 — certificação v2**: PACKS.md atualizado (certificar = fita aprovada +
  espaço de técnicas, não recipes); decidir destino do clean-numbered-editorial
  (default: arquivado até o pack 1 certificar).

## 7. Decisões em aberto (defaults propostos)

| Decisão | Default proposto |
|---------|------------------|
| Travessia de fronteira | só camadas estáticas (imagem/forma/watermark) |
| Posicionamento na fita-layer | grid 12·N × 12 (mesma linguagem declarativa) |
| Esqueleto narrativo como gate | sim (`data-role` por seção) |
| clean-numbered-editorial | arquivar até certificar o pack 1 na v2 |
| Fotos/assets pesados | continua data-URI na v2; S3 fica pro roadmap |
