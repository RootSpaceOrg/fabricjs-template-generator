# Esqueletos de miolo — catálogo de estudo

Seis composições que já funcionaram, para **ler enquanto se define um pack
novo** (`PACKS.md` §3). Não são fallback de produção nem componente do motor:
são a resposta de um estilo a um problema de composição, mostrada para ajudar
você a encontrar a resposta do SEU estilo.

**As cores são ilustrativas.** Foram renderizadas com os tokens do
clinical-photo-editorial (verde, Anton/Manrope) porque nasceram lá. O que está
em estudo é a **estrutura** — proporção, ancoragem, onde a leitura mora, como o
peso se distribui. A identidade visual é justamente o que cada pack traz de
próprio.

A pergunta certa ao olhar não é "vou usar o E3?", e sim "como o meu estilo
resolve um enumerado?".

Os exemplares vivem em  (um HTML por
padrão, imagem derivada pelo build). Aqui fica só a leitura do que cada um
resolve — quem quiser ver renderizado abre a galeria do pack no portal.

| | Composição | Problema que resolve |
|---|---|---|
| **foto-metade-sangrando** | figura toma a metade direita inteira do topo ao rodapé, sangrando pela borda; leitura na metade esquerda; número grande de âncora embaixo | slide que precisa de foto E texto sem que nenhum dos dois vire enfeite |
| **full-bleed-com-faixa** | slide todo é foto; texto numa faixa sólida no terço inferior, encostada em três bordas | foto que precisa respirar inteira, com leitura garantida por contraste |
| **enumerado-numerado** | número grande + item, ritmo regular do topo ao rodapé — a lista É a composição | enumerado que senão vira bullet solto no meio do slide |
| **card-ancorado** | foto nos dois terços de cima, cartão compacto encostado na margem inferior | dois blocos (imagem + leitura) sem nada flutuando no meio |
| **display-com-decor** | tipografia gigante como protagonista, decors cortados pelas bordas | tese curta que precisa de peso sem foto |
| **par-espelhado** | par: a MESMA foto atravessa a emenda pela `.fita-layer`, a leitura troca de lado | duas etapas de uma ideia, com continuidade real entre slides |

## Ver renderizado

```
node engine/tools/build-exemplos.js clinical-photo-editorial
```

## Duas leis que saíram daqui

Estão em `../geral.md` e valem para qualquer pack: **a célula do grid é espaço
máximo, não altura** (daí o `data-fit`) e **elemento da `.fita-layer` só ocupa
coluna sem texto**. Ambas apareceram compondo estes seis — é o tipo de coisa que
só o render mostra.
