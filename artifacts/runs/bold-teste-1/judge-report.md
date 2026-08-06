# Judge — bold-teste-1

QA do render vigente (`strip.png`, 2026-08-06) contra `packs/bold-educacional/reference.png` e exemplos do pack.

## Regras duras (R1–R6)

| Regra | Veredito | Evidência verificável |
|---|---|---|
| R1 avatar | ok | Não há slot de pessoa/avatar; S3 usa somente o slot `logo`. Gato e crachá são assets editoriais estáticos. |
| R2 corte | ok | S1–S3: headline, corpo, CTA, handles e logo ficam dentro do canvas; o crachá de S2 está inteiro. |
| R3 fundos | ok | S1 é foto teal, S2 é primary vermelha e S3 é paper; há duas mudanças reais de fundo. |
| R4 área morta | ok | S1 usa foto+meme+tarja, S2 combina statement+crachá e S3 usa fechamento+tarja+logo; o respiro é deliberado, sem vazio dominante. |
| R5 UI-decor | ok | Crachá é objeto editorial de colagem e tarjas têm função de promessa/CTA; não há UI simulada. |
| R6 contraste | ok | Texto claro sobre foto/primary, ink sobre paper e copy das tarjas têm leitura direta. |

## QA do pack

- Headlines de S1–S3 usam `data-case="sentence"`, aparecem em sentence case e mantêm quebras legíveis.
- S1 e S3 têm exatamente uma tarja cada; S2 não usa tarja. Nenhuma excede duas linhas.
- O gato de jaleco/óculos é absurdo fotográfico, mas digno: flash, grão e luz teal mantêm registro analógico-realista, sem traço de cartoon ou deformação.
- A colagem do crachá em S2 está inteira, distante do corpo e do statement; não há segunda âncora grande concorrendo.
- Fundos foto → primary → paper alternam conforme a técnica do pack.

## QA narrativo

- S1 abre com curiosidade específica (“3 mitos sobre laser...”), S2 traduz o mecanismo de luz não ionizante e S3 transforma o aprendizado em salvamento/comentário; não há redundância.
- O gancho e o mecanismo são específicos de laserterapia. Não há promessa de resultado, imperativo clínico sem porquê ou alegação incompatível.
- CTA de S3 está conectado ao valor entregue: salvar para retornar quando o medo aparecer e comentar para aprofundar a explicação.

**QA: PASS**
