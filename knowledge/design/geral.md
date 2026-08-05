# Design — conhecimento geral (vale para QUALQUER pack)

Camadas de conhecimento do designer, da base para o topo (o mais específico
vence): **este arquivo** → `packs/<slug>/` (tecnicas.md, exemplos/, tokens,
lessons.md) → dossiê da run. O que é lei mecânica está no CATALOG e nos gates;
aqui estão as leis de gosto que valem em todo estilo.

## Legibilidade (inegociável)

- Texto NUNCA sob decor, foto ou travessia — texto vive em background limpo.
- CTA, logo e foto de perfil sempre desobstruídos.
- Contraste de leitura em todo texto (o judge elimina por contraste, R6).
- Texto de leitura nunca cortado por fronteira de slide ou pelo canvas (R2);
  atravessar fronteira é privilégio de decoração/imagem/watermark.

## Hierarquia e respiro

- 1 elemento dominante por slide (headline OU foto OU número — não empate).
- Respiro deliberado pontua; slide >35% de área morta é defeito (R4) — a
  diferença entre respiro e área morta é intenção: o vazio aponta para o foco.
- Grid de 12: margens generosas (1 coluna nas laterais no mínimo), alinhamentos
  consistentes dentro do slide.

## Fita (a unidade de design)

- A fita é UMA peça: leitura contínua, fundos alternando (R3: mínimo 2 mudanças
  de fundo na fita), transições intencionais nas fronteiras.
- Elementos de travessia (fita-layer) criam continuidade: foto sobre a emenda
  de dois slides, decor cruzando, watermark varrendo. Sempre estáticos, sempre
  sobre backgrounds limpos dos DOIS lados.
- Variância é dever: duas gerações do mesmo pack nunca saem com o mesmo
  esqueleto — varie ordem, lados, quantidade de slides, presença de decors.

## Fotos e decors

- Foto editável vive inteira dentro de um slide; foto de continuidade
  (travessia) é estática e paisagem, com o sujeito perto da emenda.
- Decor = objeto do TEMA do post, gerado por post (nunca banco/estoque),
  fundo transparente, desfoque profundo NASCIDO NA GERAÇÃO (pós-processo de
  blur é proibido), inteiro no arquivo com margem nas 4 bordas.
- Decor se posiciona grande, cortado por uma borda do slide (ou da fita),
  com leve rotação — nunca pequeno e solto no meio do canvas.

## Slots da plataforma

- `professionalPhoto` usa o placeholder canônico do motor (o runtime troca pela
  foto real); pessoa/avatar desenhado no lugar é violação (R1).
- Elementos editáveis respeitam min/max de caracteres e fazem sentido para
  OUTRO profissional do mesmo nicho adaptar no editor.
