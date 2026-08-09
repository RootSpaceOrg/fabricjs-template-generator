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

| | Composição | Problema que resolve |
|---|---|---|
| **E1** | figura toma a metade direita inteira do topo ao rodapé, sangrando pela borda; leitura na metade esquerda; número grande de âncora embaixo | slide que precisa de foto E texto sem que nenhum dos dois vire enfeite |
| **E2** | slide todo é foto; texto numa faixa sólida no terço inferior, encostada em três bordas | foto que precisa respirar inteira, com leitura garantida por contraste |
| **E3** | número grande + item, ritmo regular do topo ao rodapé — a lista É a composição | enumerado que senão vira bullet solto no meio do slide |
| **E4** | foto nos dois terços de cima, cartão compacto encostado na margem inferior | dois blocos (imagem + leitura) sem nada flutuando no meio |
| **E5** | tipografia gigante como protagonista, decors cortados pelas bordas | tese curta que precisa de peso sem foto |
| **E6a+E6b** | par: a MESMA foto atravessa a emenda pela `.fita-layer`, a leitura troca de lado | duas etapas de uma ideia, com continuidade real entre slides |

## Ver renderizado

O HTML de origem vive na cópia do clinical (é o pack cujos tokens ela usa),
junto dos assets de teste — aqui ficam só as imagens, que é o que se estuda:

```
node engine/assemble.js packs/clinical-photo-editorial/exemplos/miolos/esqueletos.html <outdir>
```

## Duas leis que saíram daqui

Estão em `../geral.md` e valem para qualquer pack: **a célula do grid é espaço
máximo, não altura** (daí o `data-fit`) e **elemento da `.fita-layer` só ocupa
coluna sem texto**. Ambas apareceram compondo estes seis — é o tipo de coisa que
só o render mostra.
