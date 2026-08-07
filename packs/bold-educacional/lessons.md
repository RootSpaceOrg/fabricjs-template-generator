# Lessons — bold-educacional

- 2026-08-06 (nascimento): extraído de 3 referências curadas (2× capa meme
  Vick Machado + 1× statement chapado Thay Brasil). Aposta: o estilo se compõe
  inteiro com o motor existente (tarja = ds-cta com radius baixo do pack;
  chapado = data-invert variável; meme e colagem = RGBA geradas) — zero motor
  novo.
- 2026-08-06 (fita 1 aprovada pelo Gustavo, 'ficou legal'): capa meme + statement chapado + fechamento paper validados. Vereditos absorvidos na 1a iteracao: sentence case obrigatorio (data-case), tarja quadrada (data-square), CTA nunca estoura a tarja.
- 2026-08-07 (dois bugs pegos pelo Gustavo no editor): (a) textbox do chip herdava o data-variable do rect — corrigido no motor (convert.js: variavel pertence so ao rect); (b) byline da capa sem textType — agora instagramHandle. Licao de processo: conferir no JSON *quais* objetos receberam fillVariableConfig, nao so se existe.
- 2026-08-07 (bold-arco-1 APROVADA — primeira fita 100% composta pelo agente): dossie com arco real do acervo (validacao da dor invisivel) + 6 voltas de critica do revisor. Leis nascidas aqui: caixa se ajusta ao conteudo E precisa CABER (padding nos 4 lados); CTA e acao, nunca enfeite; cartao-lembrete compacto, assimetrico, com respiro das bordas; foto de miolo gerada JA pensando no cartao (assunto num terco, area calma no outro). Motor consertado: padding da pill, cartao ancorado no topo, veu ink, z-index do cartao sobre o veu, data-tone=ink, heranca de cor em bloco/chip.
