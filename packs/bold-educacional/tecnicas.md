# Técnicas — bold-educacional

Estilo de TOPO de funil com duas caras que se alternam na mesma fita:
**capa meme scroll-stop** e **slides statement chapados**. A cor saturada
dominante é a PRIMARY do usuário (fundos chapados e tarjas).

## Capa meme (scroll-stop)

1. Foto full-bleed INUSITADA (`ds-photo` 1/1/13/13 static+layer): animal com
   adereço humano numa cena absurda-mas-fotográfica (gato de óculos lendo na
   banheira, cachorro de óculos com taça no barco). Gerada por run, ligada ao
   TEMA por um objeto (livro, notebook, jaleco…). Realista, nunca cartoon.
2. Byline no topo centro (`ds-eyebrow` com `data-text-type="instagramHandle"`): a plataforma preenche com o handle do usuário.
3. Headline sans-BOLD branca empilhada (`ds-headline` com `<br>` e
   `data-case="sentence"` — este pack NUNCA usa uppercase em headline, rows
   ~2–5, central): frase de curiosidade, 3 linhas, quebras pensadas.
4. Sub-headline em TARJA (`ds-cta data-square data-variable="primary"` — cantos retos, recolorida pela marca):
   1–2 linhas de promessa concreta, fundo accent (recolorido pela primary).
5. O assunto da foto ocupa o meio-baixo SEM texto por cima.
6. **Contraste da headline segue a parede**: fundo claro da foto → texto ink;
   fundo escuro/saturado → texto paper. Nunca cream sobre parede clara.

## Statement chapado (miolo/tese)

1. Section `data-invert data-variable="primary"` (fundo inteiro na cor do
   usuário).
2. Frase-tese GIGANTE em paper/cream (`ds-headline size="lg"`, rows 4–11,
   esquerda, quebras dramáticas — hifenização manual quando valorizar).
3. Mini-parágrafo de apoio no topo (`ds-body` com `<b>` nos trechos-chave).
4. **Objeto de colagem 3D** (`ds-photo` RGBA static+layer, lado direito,
   pode sangrar pela borda/topo): crachá pendurado com foto, polaroid com
   clipe, etiqueta — sempre com a "foto da pessoa" = professionalPhoto quando
   possível, senão objeto do tema.
5. Handles discretos nos cantos (`ds-body` pequeno, textType instagramHandle).

## Leis do estilo

- Tipografia é a estrela: máximo 2 pesos (800 display, 500 texto), nunca
  itálico decorativo, quebras de linha SEMPRE intencionais.
- 1 tarja por slide no máximo; tarja nunca com mais de 2 linhas; tarja e
  qualquer caixa cheia SEMPRE com `data-variable="primary"`.
- Meme = absurdo fotográfico com dignidade (luz real, film look) — nunca
  clipart, nunca cartoon, nunca rosto humano deformado.
- Statement nunca divide atenção: ou colagem OU iconografia de margem, não os
  dois grandes.
- Fita típica: capa meme → 2–4 statements/explicações alternando chapado e
  paper → fechamento com CTA em tarja. Fundos DEVEM alternar (R3 vale aqui).
