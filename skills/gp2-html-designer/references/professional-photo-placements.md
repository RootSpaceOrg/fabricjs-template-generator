# Professional photo — posições estratégicas (cutout PNG)

Catálogo de 3 padrões prontos para `<img data-image-type="professionalPhoto">` em templates HealthMarket. Todos assumem PNG cutout (fundo transparente) — placeholders em [`./placeholders/`](./placeholders/).

## Princípios

- **Sempre `object-fit: contain`** (nunca `cover`): cutout precisa preservar a figura inteira. `cover` recortaria pés/cabeça e quebraria o efeito.
- **Sempre `object-position: bottom center`**: o runtime do HealthMarket (`image-variable.ts:92-94`) ancora `bottom-center` por padrão para `professionalPhoto`. O HTML deve refletir o mesmo anchor para evitar surpresa visual quando o usuário sobe sua foto real.
- **Sempre `border-radius: 0`**: cutout perde sentido em slot circular/arredondado. Avatar circular é exceção que precisa de pedido explícito (ver "Avatar circular" no fim).
- **Evite cobrir a face**: a face fica na zona superior (~30% do slot). Não posicione textos ou outros elementos sobre ela.
- **Aspect ratio do slot ≈ aspect ratio do PNG (~3:4 = `0.78`)**: o `gp2-html-reviewer` flagra slots com ratio fora de `0.55–1.10` como finding técnico. Por quê: com `object-fit: contain`, slots muito altos (ratio < 0.55) ou muito largos (ratio > 1.10) deixam metade do slot vazia e tornam fácil para o converter calcular `originWidth/Height` errado (sintoma típico: figura cobrindo só metade do slot no editor). Faixa saudável: `9:16` (0.56) até `1:1` (1.00). Para "ocupar mais espaço visual", aumente proporcionalmente width E height — não estique só uma das dimensões.

## Posição 1 — Hero cover full-figure (capa)

Foto ocupa metade do slide 1 (~50% da largura, ~88% da altura), texto na coluna oposta. Aproveita o cutout para a figura "respirar" sem moldura.

**Quando usar**: capa de carrossel de apresentação ("Conheça o Dr. João"), slide hero de single-post sobre o profissional, qualquer abertura onde a presença humana é o protagonista visual.

```html
<!-- Slide 1 (capa) — canvas 1080x1350 -->
<section class="slide" data-width="1080" data-height="1350"
         style="position:relative; width:1080px; height:1350px; background:#F4ECE2;">

  <!-- Coluna esquerda: gancho + subtítulo -->
  <p style="position:absolute; left:60px; top:120px; width:480px;
            font-family:'Inter'; font-size:18px; font-weight:600;
            color:rgba(0,0,0,0.45); letter-spacing:2px; text-transform:uppercase;">
    Especialista em joelho
  </p>
  <h1 style="position:absolute; left:60px; top:200px; width:480px;
             font-family:'Playfair Display'; font-size:88px; font-weight:700;
             color:#1A1A1A; line-height:1.0; letter-spacing:-2px;">
    Dr. João Silva
  </h1>
  <p style="position:absolute; left:60px; top:760px; width:480px;
            font-family:'Inter'; font-size:24px; font-weight:400;
            color:#3A3A3A; line-height:1.4;">
    20 anos cuidando da sua mobilidade com fisioterapia ortopédica especializada.
  </p>

  <!-- Coluna direita: foto profissional cutout. Slot 540x720 (ratio 0.75 ≈ PNG cutout 3:4). -->
  <img class="professional-photo" alt="Foto profissional"
       data-image-type="professionalPhoto"
       style="position:absolute; left:540px; top:560px; width:540px; height:720px;
              object-fit:contain; object-position:bottom center; border-radius:0;"
       src="data:image/png;base64,<conteúdo de professional-photo-1.b64.txt>">
</section>
```

**Dimensões para canvas 1080×1350:**
- Slot da foto: `left:540px; top:560px; width:540px; height:720px` (50% × 53%, ratio 0.75 ✓).
- Texto: coluna esquerda em `left: 60px–520px`, deixando ~20px de gap entre as colunas.
- O slot é colado no rodapé (`top + height = 1280`, deixando 70px do bottom). A figura sai do slot pela borda inferior porque `object-position: bottom center` ancora os pés no `bottom` do slot.
- **Não use slot 540×1200**: ratio 0.45 está fora da faixa `0.55–1.10` aceita pelo reviewer e o cutout fica espremido na metade superior do slot.

**Para canvas 1080×1080 (feed quadrado):** slot `540×720` em `top:300`.
**Para canvas 1080×1920 (stories/reels):** slot `540×720` em `top:1120`. Mantenha o slot em `~720` independente do canvas — é o tamanho que respeita o cutout. Para "figura maior", aumente proporcional: `600×800` (ratio 0.75) ou `720×960`.

## Posição 2 — CTA final lateral (slide de fechamento)

Foto ~37% da largura, altura ~67% do canvas, à direita do CTA. Aumenta confiança no momento da decisão ("Agende com Dr. João" → vê a foto do Dr. João).

**Quando usar**: último slide de carrossel com CTA pessoal ("Agende sua consulta", "Marque sua avaliação", "Fale comigo"), qualquer fechamento onde o nome do profissional aparece.

```html
<!-- Slide N (CTA) — canvas 1080x1350 -->
<section class="slide" data-width="1080" data-height="1350"
         style="position:relative; width:1080px; height:1350px; background:#1A1A1A;">

  <!-- Coluna esquerda: CTA -->
  <p style="position:absolute; left:60px; top:300px; width:560px;
            font-family:'Inter'; font-size:16px; font-weight:600;
            color:#F4ECE2; letter-spacing:2px; text-transform:uppercase;">
    Próximo passo
  </p>
  <h2 style="position:absolute; left:60px; top:380px; width:560px;
             font-family:'Playfair Display'; font-size:96px; font-weight:700;
             color:#FFFFFF; line-height:0.95; letter-spacing:-3px;">
    Agende sua consulta
  </h2>
  <p style="position:absolute; left:60px; top:780px; width:560px;
            font-family:'Inter'; font-size:22px; font-weight:400;
            color:#D4D4D4; line-height:1.4;">
    Atendimento presencial e online.<br>WhatsApp (11) 90000-0000.
  </p>

  <!-- Coluna direita: foto profissional. Slot 400x540 (ratio 0.74 ≈ PNG cutout 3:4). -->
  <img class="professional-photo" alt="Foto profissional"
       data-image-type="professionalPhoto"
       style="position:absolute; left:660px; top:740px; width:400px; height:540px;
              object-fit:contain; object-position:bottom center; border-radius:0;"
       src="data:image/png;base64,<conteúdo de professional-photo-N.b64.txt>">
</section>
```

**Dimensões para canvas 1080×1350:**
- Slot da foto: `left:660px; top:740px; width:400px; height:540px` (37% × 40%, ratio 0.74 ✓).
- Texto à esquerda em `left: 60–620px`.
- Slot colado no rodapé (`top + height = 1280`, deixando 70px). Figura ancorada nos pés via `object-position: bottom center`, criando alinhamento natural entre o "Agende" e a presença humana.
- **Não use slot 400×900**: ratio 0.44 está fora da faixa aceita.

## Posição 3 — Overlap sobre foto contextual de apoio

Foto profissional pequena (~26% largura, ~53% altura) sobreposta no canto da imagem contextual maior (clínica, ambiente, asset gerado por IA). Cria a sensação de "presença humana ancorando a cena".

**Quando usar**: slides onde há foto de ambiente ou asset visual que ganha com presença humana (mostrar a clínica + quem atende, mostrar um equipamento + quem opera, mostrar o consultório + quem recebe).

```html
<!-- Slide 3 (educativo com prova visual) — canvas 1080x1350 -->
<section class="slide" data-width="1080" data-height="1350"
         style="position:relative; width:1080px; height:1350px; background:#FFFFFF;">

  <!-- Texto na metade superior -->
  <h3 style="position:absolute; left:60px; top:120px; width:960px;
             font-family:'Playfair Display'; font-size:64px; font-weight:700;
             color:#1A1A1A; line-height:1.05; letter-spacing:-1.5px;">
    Atendimento humanizado em ambiente acolhedor
  </h3>
  <p style="position:absolute; left:60px; top:380px; width:960px;
            font-family:'Inter'; font-size:22px; font-weight:400;
            color:#3A3A3A; line-height:1.45;">
    Estrutura completa, equipamentos modernos e equipe especializada para cuidar
    de você do início ao fim do tratamento.
  </p>

  <!-- Foto contextual de apoio (userAsset) na metade inferior -->
  <img class="contextual-image" alt="Imagem de apoio"
       data-image-type="userAsset"
       style="position:absolute; left:60px; top:680px; width:960px; height:600px;
              object-fit:cover; border-radius:24px;"
       src="<URL ou placeholder diagonal SVG>">

  <!-- Foto profissional sobreposta. Slot 300x400 (ratio 0.75 ≈ PNG cutout 3:4). -->
  <img class="professional-photo" alt="Foto profissional"
       data-image-type="professionalPhoto"
       style="position:absolute; left:740px; top:880px; width:300px; height:400px;
              object-fit:contain; object-position:bottom center; border-radius:0;
              z-index:2;"
       src="data:image/png;base64,<conteúdo de professional-photo-N.b64.txt>">
</section>
```

**Dimensões para canvas 1080×1350:**
- Foto contextual (userAsset): `left:60px; top:680px; width:960px; height:600px` (89% × 44%).
- Foto profissional sobreposta: `left:740px; top:880px; width:300px; height:400px` (28% × 30%, ratio 0.75 ✓).
  - O `top: 880px` da foto profissional é **acima** do bottom da foto contextual (`top + height = 1280`), e ambas terminam na mesma linha de base — é assim que a figura "sai" pelo topo do retângulo da foto contextual.
- `z-index: 2` na foto profissional (foto contextual fica em `z-index: auto = 0`).
- **Não use slot 280×720**: ratio 0.39 fora da faixa aceita.

**Variação: overlap no canto esquerdo** — mudar `left:760px` para `left:40px` (ou `left:0` para sangrar até a borda).

## Avatar circular (exceção)

**Só** se a referência ou o brief explicitamente pedir avatar circular (ex: bloco de assinatura no rodapé, citação com "selo" do autor). Nesse caso, abandone o cutout e use crop tradicional:

```html
<img class="professional-photo professional-photo--circle" alt="Foto profissional"
     data-image-type="professionalPhoto"
     style="position:absolute; left:60px; top:1180px; width:140px; height:140px;
            object-fit:cover; border-radius:50%;"
     src="data:image/png;base64,<conteúdo de professional-photo-N.b64.txt>">
```

Note: nesse caso `object-fit: cover` é correto (avatar circular não preserva figura inteira) e o crop vai cortar a foto na altura do peito. O placeholder mostra esse efeito visualmente — se ficou ruim, considere voltar para uma das 3 posições cutout.

## Combinações comuns por tipo de carrossel

| Sequência | Recomendação |
|-----------|--------------|
| Standard 7 slides | Posição 1 (slide 1) + Posição 2 (slide 7); slides 2-6 sem foto profissional |
| Tutorial 7 slides | Posição 1 (slide 1) + Posição 3 (slide 5 ou 6, mostrando equipamento) + Posição 2 (slide 7) |
| Listicle 5-10 slides | Posição 2 (último slide); evite distrair o conteúdo dos itens |
| Comparação 5 slides | Sem foto profissional na maioria dos casos (a comparação é o protagonista); avatar circular pequeno no rodapé do veredicto se assinatura for relevante |
| Single-post | Posição 1 ou Posição 3 dependendo do tema |

## Anti-patterns

- **Usar `object-fit: cover` em cutout**: corta pés/cabeça, perde o efeito.
- **Usar `border-radius` arredondado em cutout**: o fundo arredondado aparece "em cima" da figura sem fundo, ficando estranho.
- **Slot pequeno demais para mostrar a figura inteira**: se o slot tem `height < 600px` em canvas 1350, reconsidere se a foto profissional é realmente necessária aqui — pode ser um caso de avatar circular ou nenhuma foto.
- **Texto sobre a face**: gancho/título passando pela zona superior do slot. Reposicione.
- **Mais de uma foto profissional por slide** (exceto template "Conheça nossa equipe"): polui a composição.
