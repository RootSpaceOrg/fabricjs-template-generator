#!/usr/bin/env python3
"""Comandos de chat da fábrica — fechados, sem interpretação livre no parser.

O portal valida o mínimo determinístico (pack existe? é certificado?) e monta o
prompt; a interpretação do pedido é do agente.
"""
from __future__ import annotations

import re

import knowledge as kb
from jobs import RUNS, enfileirar

# O corredor sempre atualiza o repo antes de rodar. artifacts/ e ignorada e so
# guarda output de run, entao sujeira ali nao e decisao do usuario — sem esta
# instrucao o agente para e pede autorizacao para o stash, e a fila trava.
PULL = ("git pull --rebase antes; se ele recusar por alteracao local em "
        "artifacts/ (pasta ignorada, so tem output de run), rode "
        "`git checkout -- artifacts` ou `git stash -u` e siga SEM perguntar")

AJUDA = (
    "*Fábrica — comandos*\n"
    "`/nova <pedido>` — linguagem natural; cite o pack ou deixe o agente escolher\n"
    "   ex.: `/nova bold-educacional mitos sobre laser, laserterapia`\n"
    "   ex.: `/nova post de topo de funil sobre fibromialgia` (agente escolhe o estilo)\n"
    "`/packs` — packs disponíveis (✅ certificado, 🟡 draft)\n"
    "`/runs` — últimas runs e em que estágio estão\n"
    "`/ajuda` — esta lista"
)


def slug_novo(pack: str, tema: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", tema.lower()).strip("-")[:24] or "post"
    slug = f"{pack.split('-')[0]}-{base}"
    cand, n = slug, 2
    while (RUNS / cand).exists():
        cand, n = f"{slug}-{n}", n + 1
    return cand


def _cabeca(slug: str, pedido: str, tema: str, tenant: str, vertical: str,
            env: str, business: str, n: str, pack: str | None) -> str:
    """Contexto comum a todas as fatias."""
    return (
        f"Run {slug} da fabrica ({PULL}).\n"
        f"DIRETORIO DE TRABALHO: /root/.openclaw/workspace/external/"
        f"fabricjs-template-generator — e o SEU clone. NAO escreva em "
        f"/root/hermes-workspace: e o clone do portal, onde os gates rodam. "
        f"Escrever la deixa a run pela metade nos dois lugares e trava a fila.\n"
        f'PEDIDO DO GUSTAVO: "{pedido or tema}"\n'
        f"CONTEXTO (ja definido - use, nao pergunte): tenant={tenant} - vertical={vertical} - "
        f"env={env}"
        f"{' - business_type=' + business if business else ' - business_type: infira do tema'}"
        f"{' - slides=' + n if n else ''}"
        f"{' - pack=' + pack if pack else ' - pack: ESCOLHA VOCE'}\n"
        f"TEMA: {tema}\n\n"
    )


def fatias_nova(slug: str, pack: str | None, tema: str, pedido: str = "",
                tenant: str = "kultivai", vertical: str = "health",
                env: str = "dev", business: str = "", n: str = "") -> list[str]:
    """A criacao vira 6 turnos curtos - a janela do agente nao aguenta tudo junto.

    pesquisa / dossie / imagens / abertura / miolo / fechamento+render / judge.
    Compor a fita inteira nao cabia numa janela: por isso ela vem em 3 pedacos.
    Cada fatia comeca relendo o estado do disco, entao e retomavel.
    """
    ctx = _cabeca(slug, pedido, tema, tenant, vertical, env, business, n, pack)
    escolha = ("" if pack else
               "Antes de tudo ESCOLHA o pack: compare packs/*/pack.json (certificados; olhe "
               "fit.melhor_em e assinaturas) com o tema e justifique em 1 linha no dossie. "
               "O fit e CONSELHO, nao regra - nao bloqueie a run por causa dele.\n")
    pk = pack or "<o pack escolhido>"

    f0 = (ctx +
          f"FATIA 1 de 7 - SO A PESQUISA DO TEMA. Nao crie a run, nao escreva dossie.\n"
          f"O conhecimento do negocio (knowledge/copy/negocios/) e GERAL: ele conhece o "
          f"nicho, nao este tema. Sem material especifico o dossie sai correto e generico - "
          f"serve a qualquer assunto do setor e nao ensina nada a quem ja conhece o basico.\n\n"
          f"Pesquise o tema e escreva artifacts/runs/{slug}/contexto.md com:\n"
          f"- MECANISMO: por que/como o recurso atua NESTE problema especifico. O detalhe "
          f"que um leigo nao sabe e que muda a compreensao dele.\n"
          f"- O QUE A PESSOA JA TENTOU: o que ela costuma fazer antes de procurar ajuda, e "
          f"por que costuma nao bastar. E daqui que sai gancho que soa verdadeiro.\n"
          f"- ERRO COMUM / MITO: a crenca errada mais frequente sobre o tema.\n"
          f"- NUMERO OU FATO ANCORA: se houver dado solido, com a fonte. Sem fonte, nao "
          f"invente - escreva 'sem dado confiavel' e siga.\n"
          f"- VOCABULARIO: como o publico CHAMA isso (o termo popular, nao o tecnico).\n"
          f"- LIMITE: o que o recurso NAO faz. E o que separa educacao de propaganda.\n\n"
          f"Fontes, nesta ordem: (1) knowledge/copy/negocios/ do proprio repo; (2) "
          f"sociedades e conselhos profissionais, consenso clinico, revisao publicada; "
          f"(3) conteudo do setor.\n"
          f"REGRAS DA PESQUISA:\n"
          f"- CITE a origem de cada afirmacao. Sem origem, nao entra.\n"
          f"- Nao copie texto: a copy da peca e sempre original.\n"
          f"- Divergencia entre fontes e informacao valiosa - registre as duas.\n"
          f"- Compliance vem antes: nada que vire promessa de cura, prazo ou resultado.\n"
          f"Responda em 3 linhas e PARE.")

    f1 = (ctx + escolha +
          f"FATIA 2 de 7 - SO O DOSSIE. Nao componha, nao gere imagem.\n"
          f"0. LEIA artifacts/runs/{slug}/contexto.md (fatia anterior) e USE o material: o "
          f"mecanismo, o que a pessoa ja tentou, o erro comum e o limite sao o que separa "
          f"um post especifico de um generico. Se o contexto trouxe um detalhe que muda a "
          f"compreensao, ele merece um slide.\n"
          f"1. python3 engine/run.py new {slug} --env {env} --pack {pk} "
          f"--n {n or '<dentro do range do pack>'}"
          f"{' --business-type ' + business if business else ' --business-type <o nicho canonico do negocio; catalogo em knowledge/business-types.json>'}"
          f" (se a run ja existir, siga);\n"
          f"2. resolve OFFLINE — canoniza o business_type pelo cache local, sem tocar a "
          f"AWS. O tenant real e resolvido so na PUBLICACAO, no ambiente de destino:\n"
          f"   python3 engine/tools/resolve_tenant.py --tenant {tenant} "
          f"--vertical {vertical} --offline"
          f"{' --subject ' + business if business else ' --subject <o NICHO do negocio, nao o tema do post: laserterapia, fisioterapia, nutricao... o catalogo esta em knowledge/business-types.json>'}"
          f" > artifacts/runs/{slug}/resolve.json;\n"
          f"3. LEIA o bloco 'comporta' de packs/{pk}/pack.json antes de escrever - ele diz o "
          f"orcamento de texto por papel e o que o estilo resolve bem/mal (orcamento, nao gate);\n"
          f"4. escreva artifacts/runs/{slug}/dossie.md no formato de 'Saida: dossie.md' do "
          f"CONTEXT.md: OBJETIVO, FRAMEWORK (knowledge/copy/frameworks.md), ARCO (gramatica em "
          f"knowledge/copy/negocios/) e, por slide, o FORMATO declarado (gancho, tese+ressalva, "
          f"enumerado, passo...) com os PAPEIS separados (eyebrow / tese / apoio / itens) mais o "
          f"open loop. Nao entregue paragrafo corrido: o designer precisa saber qual pedaco e "
          f"tese e qual e apoio;\n"
          f"5. O DOSSIE JA DECIDE O QUE A IMAGEM VAI MOSTRAR. Quem escreve so a copy entrega "
          f"slide de tese curta boiando no vazio e conceito abstrato para a foto - os dois "
          f"defeitos nascem aqui, nao na composicao. Entao, por slide, escreva tambem:\n"
          f"   - IMAGEM: o objeto/gesto CONCRETO do tema que aquele slide mostra (o aparelho, "
          f"o instrumento, a regiao em contexto, a bancada do atendimento) - ou 'sem imagem', "
          f"assumido. Nunca o clima ('acolhimento', 'cuidado'): isso vira foto generica que "
          f"serviria a qualquer assunto.\n"
          f"     ANTES de escrever qualquer IMAGEM, leia packs/{pk}/images.md E a secao de "
          f"assinaturas do packs/{pk}/tecnicas.md: cada pack tem SLOTS FIXOS, e a capa "
          f"costuma ser o mais rigido deles (um pack pede foto meme de animal, outro "
          f"full-bleed do ambiente, outro so o cutout do profissional). Pedir imagem que o "
          f"slot nao aceita e trabalho jogado fora - o designer vai ignorar. Se o slot ja "
          f"define o que aparece, escreva IMAGEM: conforme slot do pack (<qual>).\n"
          f"     A imagem mostra o PROBLEMA, nao a ferramenta. Em peca de topo/meio de "
          f"funil: no maximo UMA imagem de equipamento, e nunca na capa - a capa mostra a "
          f"pessoa ou a situacao em que a dor aparece (o gesto, a rotina interrompida, a "
          f"cena onde o sintoma acontece). So no fundo de funil o recurso vira protagonista. "
          f"Peca cheia de aparelho fala do que voce vende, nao do que a pessoa sente, e ela "
          f"nao se reconhece ali.\n"
          f"     Consulte tambem knowledge/imagem/negocios/<business_type>.md se existir - "
          f"ele diz o que pode e o que NAO pode aparecer neste negocio, traz REFERENCIA "
          f"FOTOGRAFICA do equipamento (olhe a imagem antes de descrever o aparelho) e uma "
          f"tabela de como mostrar o problema de cada tema.\n"
          f"   - PESO: o que ANCORA o slide alem do texto (foto, cartao, tarja, numero grande). "
          f"Slide de miolo precisa de 30% da area com conteudo - e gate no conversor. Tese "
          f"curta sozinha num slide grande reprova, mesmo com copy suficiente.\n"
          f"   Se um slide nao tem imagem nem ancora possivel, ele nao deveria existir: "
          f"junte com o vizinho e entregue menos slides, mais cheios.\n"
          f"6. advance ate 'compose' e PARE. Responda em 3 linhas.")

    f2 = (ctx +
          f"FATIA 3 de 7 - SO AS IMAGENS. O dossie ja existe (leia-o).\n"
          f"A imagem e o que faz o post ser bom ou ruim. O estilo vem do pack; o ASSUNTO "
          f"vem do tema, e e ele que costuma faltar.\n\n"
          f"O dossie ja declarou, por slide, o campo IMAGEM (o objeto concreto do tema) e o "
          f"PESO. PARTA DELE - nao reinvente o conceito aqui. Se algum IMAGEM do dossie "
          f"estiver abstrato ('acolhimento', 'cuidado'), corrija para o objeto concreto e "
          f"anote a troca; nao gere em cima do abstrato.\n\n"
          f"ANTES de gerar, escreva artifacts/runs/{slug}/imagens.md com uma linha por "
          f"imagem, neste formato:\n"
          f"  <arquivo> | MOSTRA: <o objeto/gesto concreto que aparece> | PROBLEMA: <o que "
          f"da peca essa imagem torna visivel> | PROMPT: <o prompt final>\n\n"
          f"Duas checagens obrigatorias, escritas no proprio arquivo:\n"
          f"1. TESTE DA TROCA DE TEMA: leia o PROMPT sem saber o tema. Da para dizer do que "
          f"o post fala? Se serviria para qualquer assunto de bem-estar, esta generico - "
          f"reescreva nomeando o objeto do tema (o aparelho, o instrumento, a regiao em "
          f"contexto, o gesto especifico daquele procedimento).\n"
          f"2. EQUILIBRIO PROBLEMA x FERRAMENTA: conte quantas imagens mostram EQUIPAMENTO e "
          f"quantas mostram o PROBLEMA/a pessoa. Em topo ou meio de funil, no maximo uma de "
          f"equipamento, e nunca na capa. Se a sua conta deu mais, reescreva: a peca esta "
          f"falando do que se vende, nao do que a pessoa sente.\n"
          f"3. VARIEDADE: duas imagens da mesma run nao repetem enquadramento nem cena. "
          f"Se as suas viraram variacoes de uma so, troque o angulo E o assunto de cada uma.\n\n"
          f"Tema sensivel (corpo, dor intima, amamentacao) NAO e desculpa para fugir para o "
          f"generico: mostre o entorno especifico - o equipamento, a bancada do atendimento, "
          f"a mao da profissional ajustando o aparelho.\n"
          f"Evite o cliche do gerador (bicho de roupao, velas, pedras de spa, chá) - se a "
          f"cena nao tem nada do tema, ela e enfeite.\n\n"
          f"LEIA knowledge/imagem/negocios/<business_type>.md se existir: e a memoria do "
          f"negocio sobre o que pode e o que NAO pode aparecer (equipamento certo x "
          f"errado, enquadramentos que dizem o assunto, como tratar tema sensivel). "
          f"Aparelho do negocio errado numa foto arrasta a peca inteira.\n"
          f"So entao gere em artifacts/runs/{slug}/assets/, seguindo packs/{pk}/images.md "
          f"(foto de miolo pensada para receber cartao; decor transparente com blur na "
          f"geracao; NUNCA gere pessoa para o slot professionalPhoto - esse slot usa o "
          f"placeholder canonico do motor).\n"
          f"Depois de gerar, ABRA cada imagem e confira que ela mostra o que voce declarou "
          f"em MOSTRA. Saiu generica ou fora do tema? Gere de novo - nao siga com ela.\n"
          f"Liste os arquivos e PARE.")

    regras = (f"Siga engine/CATALOG.md, packs/{pk}/tecnicas.md (tabela 'como este estilo resolve "
              f"cada formato': o dossie diz o FORMATO e os PAPEIS, voce escolhe o tratamento) e "
              f"knowledge/design/geral.md. Nenhum slide e so texto - minimo 2 elementos com peso. "
              f"TESE E APOIO SAO UM BLOCO DE LEITURA: apoio solto no rodape, longe da tese, e "
              f"defeito. PROIBIDO copiar/adaptar fita.html de outra run - olhar exemplo do pack "
              f"e permitido, copiar nao.\n")

    f3a = (ctx + regras +
           f"FATIA 4 de 7 - SO A ABERTURA. Dossie e assets ja existem (leia dossie.md, "
           f"liste assets/).\n"
           f"Crie artifacts/runs/{slug}/fita.html com o esqueleto (head + main.fita) e "
           f"APENAS a <section data-role=\"abertura\">. Nao escreva os outros slides ainda.\n"
           f"A CAPA CARREGA AS ASSINATURAS do pack - leia a secao 'Assinaturas' do "
           f"packs/{pk}/tecnicas.md e aplique TODAS. Se alguma exigir asset fixo (o "
           f"images.md diz quais), copie de packs/{pk}/assets/ para "
           f"artifacts/runs/{slug}/assets/ antes de referenciar.\n"
           f"Nao rode assemble. Responda em 2 linhas.")

    f3b = (ctx + regras +
           f"FATIA 5 de 7 - SO O MIOLO. O fita.html ja existe com a abertura (leia-o).\n"
           f"Acrescente as <section data-role=\"item\"> do miolo conforme o dossie "
           f"(a fita tem {n or 'o total definido em run.json'} slides no total, contando "
           f"abertura e fechamento). Para CADA slide, use o formato declarado no dossie e o "
           f"tratamento correspondente na tabela do tecnicas.md; o apoio acompanha a tese no "
           f"mesmo bloco.\n"
           f"A FITA E UMA PECA SO. Antes de escrever cada slide, responda em uma linha: "
           f"SOU CONTINUACAO DO ANTERIOR OU MUDANCA DE PADRAO? Continuacao = repito a "
           f"estrutura e mudo o conteudo (e considere virar PAR, com a mesma foto "
           f"atravessando a emenda pela fita-layer); mudanca = inverto fundo, troco a "
           f"familia do tratamento, mudo a ancora de canto. Nunca o meio-termo: dois "
           f"slides parecidos-mas-nao-iguais na emenda (foto de metade a direita seguida "
           f"de outra a esquerda) leem como par quebrado. Escreva essas respostas como "
           f"comentario HTML antes de cada section.\n"
           f"Nao rode assemble. Responda em 2 linhas.")

    f3c = (ctx + regras +
           f"FATIA 6 de 7 - FECHAMENTO E RENDER. O fita.html ja tem abertura e miolo (leia-o).\n"
           f"1. acrescente a <section data-role=\"fechamento\"> (espelha a abertura: "
           f"professionalPhoto + CTA + logo);\n"
           f"2. rode 'node engine/assemble.js artifacts/runs/{slug}';\n"
           f"3. responda so com o caminho do strip.png.")

    f4 = (ctx +
          f"FATIA 7 de 7 - CORREDOR E JUDGE ATE PASSAR.\n"
          f"1. 'node engine/convert.js artifacts/runs/{slug} artifacts/runs/{slug}/output "
          f"--slug {slug}' - rejeicao = corrija o HTML e repita (nunca edite JSON);\n"
          f"2. avance ate judge e julgue (JUDGE.md modo QA + check narrativo);\n"
          f"3. FAIL = corrija o fita.html, re-renderize, reconverta e RE-JULGUE (max 3 voltas);\n"
          f"4. PARE no judge com PASS - nao escreva fidelity nem publique (isso e do Gustavo).\n"
          f"Reporte o veredito e quantas voltas precisou.")

    return [f0, f1, f2, f3a, f3b, f3c, f4]


def prompt_nova(slug: str, pack: str | None, tema: str, pedido: str = "",
                tenant: str = "kultivai", vertical: str = "health",
                env: str = "dev", business: str = "", n: str = "") -> str:
    """Compat: primeira fatia (o encadeamento é feito por quem enfileira)."""
    return fatias_nova(slug, pack, tema, pedido, tenant, vertical, env, business, n)[0]


def executar(texto: str) -> str:
    """Interpreta um comando e devolve a resposta em Markdown."""
    cmd, _, resto = texto.partition(" ")
    cmd, resto = cmd.lower().lstrip("/").split("@")[0], resto.strip()

    if cmd in ("ajuda", "help", "start"):
        return AJUDA

    if cmd == "packs":
        linhas = [
            f"{'✅' if p['status'] == 'certificado' else '🟡'} `{p['slug']}`\n"
            f"   {p['familia'][:70]}"
            for p in kb.packs()
        ]
        return "*Packs*\n" + "\n".join(linhas) if linhas else "Nenhum pack."

    if cmd == "runs":
        from app import _runs  # import tardio: evita ciclo
        linhas = [
            f"`{r['slug']}` — {r['stage']}" + (f" · QA {r['qa']}" if r["qa"] else "") + f" · {r['age']}"
            for r in _runs()[:8]
        ]
        return "*Últimas runs*\n" + "\n".join(linhas) if linhas else "Nenhuma run."

    if cmd == "nova":
        if not resto:
            return ("Use `/nova <pedido>`\n"
                    "Ex.: `/nova bold-educacional mitos sobre laser, laserterapia`\n"
                    "Sem citar pack, o agente escolhe o estilo pelo tema.")
        certificados = {p["slug"] for p in kb.packs() if p["status"] == "certificado"}
        pack = next((s for s in sorted(certificados, key=len, reverse=True) if s in resto), None)
        tema = resto.replace(pack, "", 1).strip(" ,-—:") if pack else resto
        if not tema:
            return f"Faltou o tema. Ex.: `/nova {pack} mitos sobre laser, laserterapia`"
        slug = slug_novo(pack or "run", tema)
        pai = None
        for fatia in fatias_nova(slug, pack, tema, pedido=resto, business="laserterapy"):
            pai = enfileirar("agente", slug, fatia, pai=pai)
        aviso = ("\n\n⚠️ Você mencionou *prod*: a run vai para dev; publicar em produção "
                 "exige confirmação separada.") if re.search(r"\bprod", resto, re.I) else ""
        quem = f"pack `{pack}`" if pack else "_pack a escolher pelo agente_"
        return (f"Run `{slug}` enfileirada — {quem}, ambiente dev.\n"
                f"Pedido: _{tema}_{aviso}\n\n"
                f"O agente confirma o que entendeu e eu aviso quando a fita ficar pronta.")

    return f"Comando desconhecido.\n\n{AJUDA}"
