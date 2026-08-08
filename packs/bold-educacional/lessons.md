# Lessons — bold-educacional

- 2026-08-06 (nascimento): extraído de 3 referências curadas (2× capa meme
  Vick Machado + 1× statement chapado Thay Brasil). Aposta: o estilo se compõe
  inteiro com o motor existente (tarja = ds-cta com radius baixo do pack;
  chapado = data-invert variável; meme e colagem = RGBA geradas) — zero motor
  novo.
- 2026-08-06 (fita 1 aprovada pelo Gustavo, 'ficou legal'): capa meme + statement chapado + fechamento paper validados. Vereditos absorvidos na 1a iteracao: sentence case obrigatorio (data-case), tarja quadrada (data-square), CTA nunca estoura a tarja.
- 2026-08-07 (dois bugs pegos pelo Gustavo no editor): (a) textbox do chip herdava o data-variable do rect — corrigido no motor (convert.js: variavel pertence so ao rect); (b) byline da capa sem textType — agora instagramHandle. Licao de processo: conferir no JSON *quais* objetos receberam fillVariableConfig, nao so se existe.
- 2026-08-07 (bold-arco-1 APROVADA — primeira fita 100% composta pelo agente): dossie com arco real do acervo (validacao da dor invisivel) + 6 voltas de critica do revisor. Leis nascidas aqui: caixa se ajusta ao conteudo E precisa CABER (padding nos 4 lados); CTA e acao, nunca enfeite; cartao-lembrete compacto, assimetrico, com respiro das bordas; foto de miolo gerada JA pensando no cartao (assunto num terco, area calma no outro). Motor consertado: padding da pill, cartao ancorado no topo, veu ink, z-index do cartao sobre o veu, data-tone=ink, heranca de cor em bloco/chip.
- 2026-08-07 (corredor QA): Gustavo aprovou as três fitas `bold-arco-1` (7 slides), `bold-arco-3` (3) e `bold-arco-5` (5). Checagem QA confirmou arco narrativo específico, CTAs conectados ao valor e registro meme → objeto de conteúdo/statement → fechamento. Em `bold-arco-5`, headline display de 3 linhas recebeu 4 linhas de grid e o body foi deslocado abaixo: a regra de reservar uma linha de grid por linha display evita transbordamento que o conversor não detecta.
- 2026-08-07: PACK CERTIFICADO (v3) — 3 fitas (3/5/7 slides) compostas pelo agente, aprovadas pelo Gustavo. Terceiro estilo em producao.
- 2026-08-08 (run-escolha-um-tema-para-tod, aprovado pelo Gustavo): no fechamento com CTA + logo + `professionalPhoto`, não basta separar linhas de grid: o `data-inset="bottom"` do logo pode invadir a CTA. Reserve colunas independentes para CTA e logo e confirme no `convert.js`. `professionalPhoto` não usa `data-circle`/border radius; preservar o recorte canônico do runtime.
