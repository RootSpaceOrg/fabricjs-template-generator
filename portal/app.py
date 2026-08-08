#!/usr/bin/env python3
"""Portal de backoffice da fábrica de templates.

Runs · Fila · Packs · Conhecimento. Lê o estado do disco e dispara os mesmos
comandos do fluxo manual. O disco é a verdade; o SQLite guarda fila e vereditos.
Ver PLAN-portal.md.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

import knowledge as kb
import telegram as tg
from jobs import FACTORY, RUNS, db, enfileirar, registrar_veredito

HERE = Path(__file__).parent
app = FastAPI(title="Fábrica — backoffice")
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")

STAGES = ["resolve", "context", "compose", "render", "convert", "judge", "finalize", "upload", "done"]


def _editor_url(slug: str, tid: str | None) -> str | None:
    """URL do editor: o domínio vem do resolve.json da run (muda por vertical)."""
    if not tid:
        return None
    try:
        r = json.loads((RUNS / slug / "resolve.json").read_text(encoding="utf-8"))
        dom = r.get("domain")
    except Exception:
        dom = None
    return f"https://{dom}/editor/{tid}" if dom else None


# ── helpers ────────────────────────────────────────────────────────────────
def _read(p: Path, limit: int | None = None) -> str:
    if not p.exists():
        return ""
    t = p.read_text(encoding="utf-8", errors="replace")
    return t[:limit] if limit else t


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _age(ts: float) -> str:
    m = (datetime.now().timestamp() - ts) / 60
    return f"{int(m)} min" if m < 60 else (f"{int(m//60)} h" if m < 1440 else f"{int(m//1440)} d")


def _runs() -> list[dict]:
    out = []
    if not RUNS.exists():
        return out
    for d in sorted(RUNS.iterdir()):
        f = d / "run.json"
        if not f.is_file() or d.name.startswith("_"):
            continue
        try:
            st = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        strip = d / "strip.png"
        mt = max(f.stat().st_mtime, strip.stat().st_mtime if strip.exists() else 0)
        judge = _read(d / "judge-report.md")
        out.append({"slug": d.name, "stage": st.get("stage", "?"), "pack": st.get("pack", "?"),
                    "env": st.get("env"), "template_id": st.get("template_id"), "n": st.get("n"),
                    "has_strip": strip.exists(), "mtime": mt, "age": _age(mt),
                    "qa": "PASS" if "QA: PASS" in judge else ("FAIL" if "QA: FAIL" in judge else None),
                    "title": (re.search(r'data-template-name="([^"]+)"', _read(d / "fita.html", 4000)) or [None, ""])[1]})
    return sorted(out, key=lambda r: r["mtime"], reverse=True)


def _cls(r: dict) -> tuple[str, str]:
    if r["stage"] == "done":
        return "s-done", "done"
    if r["stage"] in ("judge", "finalize", "upload"):
        return "s-wait", r["stage"]
    return ("s-old", r["stage"]) if r["age"].endswith("d") else ("s-run", r["stage"])


def _page(title: str, aba: str, head: str, body: str) -> str:
    with db() as c:
        pend = c.execute("SELECT COUNT(*) n FROM jobs WHERE status IN ('pending','running')").fetchone()["n"]
    tabs = [("/", "runs", "Runs"), ("/fila", "fila", "Fila"), ("/packs", "packs", "Packs"),
            ("/conhecimento", "kb", "Conhecimento")]
    nav = "".join(
        f'<a href="{u}" class="{"on" if k == aba else ""}">{n}'
        f'{f"<span class=badge>{pend}</span>" if k == "fila" and pend else ""}</a>' for u, k, n in tabs)
    return f'''<!doctype html><html lang="pt-br"><head><meta charset="utf-8"><title>{title}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="/static/portal.css"></head><body>
<div class="top"><div class="top-in"><span class="brand"><span class="dot"></span>Fábrica</span>
<nav class="tabs">{nav}</nav><span class="right">kultivai</span></div></div>
<div class="wrap"><div class="pagehead">{head}</div>{body}</div></body></html>'''


# ── runs ───────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def index():
    rows = _runs()
    cards = []
    for r in rows:
        cls, label = _cls(r)
        idx = STAGES.index(r["stage"]) if r["stage"] in STAGES else 0
        bar = "".join(f'<div class="step {"fin" if r["stage"]=="done" else ("on" if i<=idx else "")}"></div>'
                      for i in range(len(STAGES) - 1))
        thumb = f'<img class="thumb" src="/run/{r["slug"]}/strip.png" loading="lazy">' if r["has_strip"] else ""
        tpl = f'<span class="tid" title="template_id">{r["template_id"]}</span>' if r["template_id"] else ""
        qa = f'<span class="pill s-{"done" if r["qa"]=="PASS" else "old"}">QA {r["qa"]}</span>' if r["qa"] else ""
        cards.append(f'''<a class="card" href="/run/{r['slug']}">{thumb}<div class="body">
<h3>{r['slug']}</h3><div class="sub">{_esc(r['title']) or '—'}</div>
<div class="meta"><span class="pill {cls}">{label}</span>{qa}<span>{r['pack']}</span>
<span>{r['n'] or '?'} slides</span><span>{r['age']}</span>{tpl}</div><div class="bar">{bar}</div></div></a>''')
    head = f'<h1>Runs</h1><span class="sub">{len(rows)} execuções</span>'
    return _page("Runs", "runs", head, f'<div class="grid">{"".join(cards) or "<p class=empty>Sem runs.</p>"}</div>')


@app.get("/run/{slug}/strip.png")
def strip(slug: str):
    p = RUNS / slug / "strip.png"
    if not p.exists():
        raise HTTPException(404)
    return FileResponse(p, headers={"Cache-Control": "no-cache"})


@app.get("/run/{slug}", response_class=HTMLResponse)
def run_detail(slug: str):
    d = RUNS / slug
    if not (d / "run.json").exists():
        raise HTTPException(404)
    st = json.loads((d / "run.json").read_text(encoding="utf-8"))
    strip_html = f'<div class="strip"><img src="/run/{slug}/strip.png"></div>' if (d / "strip.png").exists() else ""
    with db() as c:
        jobs = c.execute("SELECT * FROM jobs WHERE slug=? ORDER BY id DESC LIMIT 5", (slug,)).fetchall()
        vers = c.execute("SELECT * FROM vereditos WHERE slug=? ORDER BY id DESC LIMIT 5", (slug,)).fetchall()
    jl = "".join(f'<tr><td>#{j["id"]}</td><td>{j["tipo"]}</td>'
                 f'<td><span class="pill s-{"done" if j["status"]=="done" else ("fail" if j["status"]=="failed" else "run")}">{j["status"]}</span></td>'
                 f'<td><details><summary>log</summary><pre>{_esc((j["log"] or "—")[-3000:])}</pre></details></td></tr>' for j in jobs)
    vl = "".join(f'<tr><td class="sub">{v["criado_em"][5:16]}</td>'
                 f'<td><span class="pill s-{"done" if v["veredito"]=="aprovado" else "old"}">{v["veredito"]}</span></td>'
                 f'<td>{_esc(v["texto"]) or "—"}</td><td class="sub">{v["origem"]}</td></tr>' for v in vers)
    tid = st.get("template_id")
    url = _editor_url(slug, tid)
    if tid:
        copiar = f"navigator.clipboard.writeText('{tid}');this.textContent='copiado'"
        link = (f'<a class="btn sm" href="{url}" target="_blank" rel="noopener">abrir no editor &#8599;</a>'
                if url else '<span class="sub">(domínio não resolvido)</span>')
        tpl_html = (f'<code class="tid">{tid}</code>{link}'
                    f'<button class="sm" onclick="{copiar}">copiar id</button>')
    else:
        tpl_html = '<span class="sub">sem template publicado</span>'
    head = (f'<h1>{slug}</h1><span class="sub">{st.get("pack")} · estágio {st.get("stage")} · '
            f'env {st.get("env")}</span>{tpl_html}<a class="sub" href="/">← runs</a>')
    body = f'''{strip_html}
<div class="acts">
<form class="inline" method="post" action="/run/{slug}/job/corredor"><button class="primary">▶ Rodar corredor</button></form>
<form class="inline" method="post" action="/run/{slug}/job/advance"><button>⏭ Avançar estágio</button></form>
<form class="inline" method="post" action="/run/{slug}/job/upload"><button>⬆ Publicar em dev</button></form>
<form class="inline" method="post" action="/run/{slug}/veredito"><input type="hidden" name="veredito" value="aprovado"><button class="ok">✓ Aprovar</button></form>
{'<form class="inline" method="post" action="/run/' + slug + '/notificar"><button>✈ Enviar ao Telegram</button></form>' if tg.ativo() else ''}
</div>
<form method="post" action="/run/{slug}/veredito" style="margin-bottom:18px">
<input type="hidden" name="veredito" value="reprovado">
<textarea name="texto" placeholder="Feedback de revisão — vira turno para o agente corrigir (ex.: slide 3: headline transborda a célula, aumente a área)"></textarea>
<div style="margin-top:8px"><button class="bad">✕ Reprovar e enviar ao agente</button></div></form>
<div class="cols">
<div><p class="h2">Dossiê</p><pre>{_esc(_read(d / "dossie.md")) or "—"}</pre></div>
<div><p class="h2">Judge</p><pre>{_esc(_read(d / "judge-report.md")) or "—"}</pre>
<p class="h2" style="margin-top:14px">Fidelidade</p><pre>{_esc(_read(d / "fidelity.md")) or "—"}</pre></div></div>
<p class="h2" style="margin-top:22px">Vereditos</p><div class="list"><table>{vl or '<tr><td class="empty">nenhum</td></tr>'}</table></div>
<p class="h2" style="margin-top:22px">Jobs desta run</p><div class="list"><table>{jl or '<tr><td class="empty">nenhum</td></tr>'}</table></div>'''
    return _page(slug, "runs", head, body)


@app.post("/run/{slug}/job/{tipo}")
def criar_job(slug: str, tipo: str):
    if not (RUNS / slug / "run.json").exists():
        raise HTTPException(404)
    enfileirar(tipo, slug)
    return RedirectResponse(f"/run/{slug}", status_code=303)


@app.post("/run/{slug}/veredito")
def veredito(slug: str, veredito: str = Form(...), texto: str = Form("")):
    if veredito == "aprovado":
        _aprovar(slug, "portal")
        return RedirectResponse(f"/run/{slug}", status_code=303)
    registrar_veredito(slug, veredito, texto)
    if veredito == "reprovado" and texto.strip():
        enfileirar("agente", slug,
                   f"REVISAO da run {slug} na fabrica (git pull --rebase antes; copy/dossie so mudam se o "
                   f"feedback pedir). Feedback do Gustavo:\n\n{texto.strip()}\n\n"
                   f"Corrija o fita.html de artifacts/runs/{slug}, rode "
                   f"'node engine/assemble.js artifacts/runs/{slug}' e confirme. NAO avance estagio.")
    return RedirectResponse(f"/run/{slug}", status_code=303)


# ── fila ───────────────────────────────────────────────────────────────────
@app.get("/fila", response_class=HTMLResponse)
def fila():
    with db() as c:
        jobs = c.execute("SELECT * FROM jobs ORDER BY id DESC LIMIT 60").fetchall()
    tpls = {r["slug"]: r["template_id"] for r in _runs()}

    def _tpl_cell(slug: str) -> str:
        tid = tpls.get(slug)
        u = _editor_url(slug, tid)
        if not tid:
            return '<span class="sub">—</span>'
        return (f'<a class="tid" href="{u}" target="_blank" rel="noopener" title="{tid}">abrir &#8599;</a>'
                if u else f'<span class="tid">{tid[:8]}…</span>')

    rows = "".join(f'''<tr><td>#{j["id"]}</td><td>{j["tipo"]}</td><td><a href="/run/{j["slug"]}">{j["slug"]}</a></td>
<td>{_tpl_cell(j["slug"])}</td>
<td><span class="pill s-{"done" if j["status"]=="done" else ("fail" if j["status"]=="failed" else ("run" if j["status"]=="running" else "wait"))}">{j["status"]}</span></td>
<td class="sub">{(j["criado_em"] or "")[5:16]}</td>
<td><details><summary>detalhes</summary><pre>{_esc((j["log"] or "—")[-3000:])}</pre>
{f'<p class="h2" style="margin-top:10px">prompt</p><pre>{_esc(j["payload"][:1200])}</pre>' if j["payload"] else ""}</details></td>
<td><form class="inline" method="post" action="/fila/{j["id"]}/reenfileirar"><button class="sm">↻</button></form></td></tr>''' for j in jobs)
    head = '<h1>Fila</h1><span class="sub">worker serial · um turno por vez · lock compartilhado com o SSH</span>'
    body = f'<div class="list"><table><tr><th>id</th><th>tipo</th><th>run</th><th>template</th><th>status</th><th>criado</th><th>detalhes</th><th></th></tr>{rows or "<tr><td class=empty>fila vazia</td></tr>"}</table></div>'
    return _page("Fila", "fila", head, body)


@app.post("/fila/{job_id}/reenfileirar")
def reenfileirar(job_id: int):
    with db() as c:
        j = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if j:
            enfileirar(j["tipo"], j["slug"], j["payload"] or "")
    return RedirectResponse("/fila", status_code=303)


# ── packs ──────────────────────────────────────────────────────────────────
@app.get("/packs", response_class=HTMLResponse)
def packs_view(ok: str = ""):
    ps = kb.packs()
    cards = []
    for p in ps:
        cls = "s-done" if p["status"] == "certificado" else "s-draft"
        certs = (f'<div class="meta"><span class="sub">certificação: {len(p["certs"])} fitas</span></div>'
                 if p["certs"] else "")
        ref = f'<img class="thumb" src="/packs/{p["slug"]}/reference.png" loading="lazy">' if p["tem_reference"] else ""
        cards.append(f'''<a class="card" href="/packs/{p['slug']}">{ref}<div class="body">
<h3>{p['slug']}</h3><div class="sub">{_esc(p['familia'])}</div>
<div class="meta"><span class="pill {cls}">{p['status']}</span><span>v{p['versao']}</span>
<span>{p['funil'] or '—'}</span><span>{p['slides']} slides</span>
{f"<span>desde {p['certificado_em']}</span>" if p['certificado_em'] else ""}</div>
{certs}</div></a>''')
    q = kb.queue()
    qrows = "".join(f'''<div class="row"><img src="/queue/{i["nome"]}" style="width:74px;height:52px;object-fit:cover;border-radius:6px;background:#0b0d11">
<div><div class="name">{i["nome"]}</div><div class="path">pack-queue/ · {i["tamanho"]}</div></div>
<div class="spacer"></div><a class="btn sm" href="/queue/{i["nome"]}" target="_blank">abrir</a></div>''' for i in q)
    flash = '<div class="flash">Salvo e commitado no repositório.</div>' if ok else ""
    head = f'<h1>Packs</h1><span class="sub">{len(ps)} packs · {len(q)} referências na fila</span>'
    body = f'''{flash}<div class="grid">{"".join(cards)}</div>
<p class="h2" style="margin-top:26px">Pack-queue — referências aguardando virar pack</p>
<div class="list">{qrows or '<p class="empty">Fila vazia.</p>'}</div>'''
    return _page("Packs", "packs", head, body)


@app.get("/packs/{slug}", response_class=HTMLResponse)
def pack_view(slug: str):
    p = kb.pack_detalhe(slug)
    if not p:
        raise HTTPException(404)
    cls = "s-done" if p["status"] == "certificado" else "s-draft"
    ref = (f'<div class="ref"><img src="/packs/{slug}/reference.png"></div>'
           if p["tem_reference"] else "")
    ass = "".join(f"<li>{_esc(a)}</li>" for a in p["assinaturas"])
    toks = "".join(
        f'<span class="pill s-draft" style="font-family:ui-monospace">{k}: {v}</span> '
        for k, v in list(p["tokens"].items())[:10] if k in
        ("paper", "ink", "muted", "accent", "accent-ink", "font-display", "font-body"))
    files = "".join(f'<a class="btn sm" href="/conhecimento/editar?rel={f["rel"]}">{f["nome"]}</a> '
                    for f in p["arquivos"])
    fitas = "".join(f'''<div class="fita-card">
<div class="meta" style="margin-bottom:10px"><strong style="font-size:14.5px">{f["nome"]}</strong>
{f'<span class="pill s-done">QA PASS</span>' if "QA: PASS" in f["judge"] else ('<span class="pill s-old">QA FAIL</span>' if "QA: FAIL" in f["judge"] else "")}
<span class="spacer"></span>
<button class="sm" onclick="this.closest('.fita-card').querySelector('.strip').classList.toggle('zoom')">⤢ zoom</button></div>
<div class="strip"><img src="/packs/{slug}/cert/{f["strip"]}" loading="lazy"></div>
<div class="cols" style="margin-top:10px">
<div><details><summary>dossiê</summary><pre>{_esc(f["dossie"]) or "—"}</pre></details></div>
<div><details><summary>judge</summary><pre>{_esc(f["judge"]) or "—"}</pre></details></div></div></div>'''
        for f in p["fitas"])
    ev = (f'<p class="h2" style="margin-top:24px">Evidência</p><pre>{_esc(p["evidencia"])}</pre>'
          if p["evidencia"] else "")
    exemplos = ("".join(f'<span class="pill s-draft">{e}</span> ' for e in p["exemplos"])
                or '<span class="sub">nenhum</span>')
    head = (f'<h1>{slug}</h1><span class="pill {cls}">{p["status"]}</span>'
            f'<span class="sub">v{p["versao"]}'
            f'{" · certificado em " + p["certificado_em"] if p["certificado_em"] else ""}</span>'
            f'<a class="sub" href="/packs">← packs</a>')
    body = f'''<div class="cols ficha">
<div>{ref}</div>
<div><p class="h2">Família</p><p style="margin-top:0">{_esc(p["familia"])}</p>
<p class="h2" style="margin-top:16px">Assinaturas</p><ul style="margin:0;padding-left:18px;font-size:14px">{ass}</ul>
<p class="h2" style="margin-top:16px">Fit</p>
<div class="meta"><span>funil: {", ".join(p["fit"].get("funil", [])) or "—"}</span>
<span>verticais: {", ".join(p["fit"].get("verticais", [])) or "—"}</span>
<span>slides: {p["slides"].get("min", "?")}–{p["slides"].get("max", "?")}</span></div>
<p class="h2" style="margin-top:16px">Tokens</p><div class="meta">{toks}</div>
<p class="h2" style="margin-top:16px">Exemplos</p><div class="meta">{exemplos}</div>
<p class="h2" style="margin-top:16px">Conhecimento do pack</p>
<div class="meta">{files}<a class="btn sm" href="/conhecimento/editar?rel=packs/{slug}/pack.json">pack.json</a></div>
</div></div>
<p class="h2" style="margin-top:26px">Certificação — {len(p["fitas"])} fitas de prova</p>
{fitas or '<p class="empty">Este pack ainda não tem certificação.</p>'}
{ev}'''
    return _page(slug, "packs", head, body)


@app.get("/packs/{slug}/cert/{nome}")
def pack_cert_img(slug: str, nome: str):
    p = (FACTORY / "packs" / slug / "certification" / nome).resolve()
    if not str(p).startswith(str((FACTORY / "packs").resolve())) or not p.exists():
        raise HTTPException(404)
    return FileResponse(p)


@app.get("/packs/{slug}/reference.png")
def pack_ref(slug: str):
    p = FACTORY / "packs" / slug / "reference.png"
    if not p.exists():
        raise HTTPException(404)
    return FileResponse(p)


@app.get("/queue/{nome}")
def queue_img(nome: str):
    p = (FACTORY / "pack-queue" / nome).resolve()
    if not str(p).startswith(str((FACTORY / "pack-queue").resolve())) or not p.exists():
        raise HTTPException(404)
    return FileResponse(p)


# ── conhecimento ───────────────────────────────────────────────────────────
@app.get("/conhecimento", response_class=HTMLResponse)
def kb_view(ok: str = ""):
    grupos = kb.arvore()
    secoes = []
    for g, itens in grupos.items():
        rows = "".join(f'''<div class="row"><div><div class="name">{i["nome"]}</div>
<div class="path">{i["rel"]}</div></div><div class="spacer"></div>
<span class="sub">{i["linhas"]} linhas</span>
<a class="btn sm" href="/conhecimento/editar?rel={i["rel"]}">editar</a></div>''' for i in itens)
        secoes.append(f'<p class="h2" style="margin-top:22px">{g}</p><div class="list">{rows}</div>')
    flash = '<div class="flash">Salvo e commitado no repositório.</div>' if ok else ""
    head = ('<h1>Conhecimento</h1><span class="sub">o que os agentes leem — editar aqui commita e '
            'envia para o repositório</span>')
    return _page("Conhecimento", "kb", head, flash + "".join(secoes))


@app.get("/conhecimento/editar", response_class=HTMLResponse)
def kb_edit(rel: str):
    try:
        conteudo = kb.ler(rel)
    except ValueError as e:
        raise HTTPException(400, str(e))
    head = (f'<h1>{rel.split("/")[-1]}</h1><span class="sub">{rel}</span>'
            f'<a class="sub" href="/conhecimento">← conhecimento</a>')
    body = f'''<form method="post" action="/conhecimento/salvar">
<input type="hidden" name="rel" value="{rel}">
<textarea class="editor" name="conteudo" spellcheck="false">{_esc(conteudo)}</textarea>
<div class="acts" style="margin-top:12px">
<input type="text" name="msg" placeholder="mensagem do commit (opcional)" style="max-width:420px">
<button class="primary">Salvar, commitar e enviar</button>
<a class="btn" href="/conhecimento">Cancelar</a></div></form>'''
    return _page(rel, "kb", head, body)


@app.post("/conhecimento/salvar")
def kb_save(rel: str = Form(...), conteudo: str = Form(...), msg: str = Form("")):
    try:
        ok, out = kb.salvar(rel, conteudo, msg or None)
    except ValueError as e:
        raise HTTPException(400, str(e))
    destino = "/packs" if rel.startswith("packs/") else "/conhecimento"
    return RedirectResponse(f"{destino}?ok=1" if ok else f"{destino}", status_code=303)


def _aprovar(slug: str, origem: str) -> str:
    """Registra o veredito e avança — com dois gates:
    (1) só avança se o judge deu PASS; (2) nunca ultrapassa finalize
    (publicar em dev é sempre decisão explícita e separada)."""
    registrar_veredito(slug, "aprovado", origem=origem)
    d = RUNS / slug
    try:
        st = json.loads((d / "run.json").read_text(encoding="utf-8"))
    except Exception:
        return "Aprovado — run sem estado legível, nada avançado."
    estagio = st.get("stage")
    judge = _read(d / "judge-report.md")
    if estagio in ("upload", "done"):
        return f"Aprovado ✓ (já está em {estagio})"
    if estagio == "finalize":
        return "Aprovado ✓ — parado antes do upload: publicar é decisão separada."
    if "QA: PASS" not in judge:
        motivo = "judge reprovou (QA: FAIL)" if "QA: FAIL" in judge else "ainda não há judge-report"
        return f"Aprovado ✓ mas NÃO avancei: {motivo}."
    enfileirar("advance", slug)
    return f"Aprovado ✓ — avanço enfileirado (de {estagio}; paro antes do upload)."


# ── telegram ───────────────────────────────────────────────────────────────
AGUARDANDO: dict[str, str] = {}  # chat_id -> slug esperando texto de reprovação


@app.post("/tg/webhook")
async def tg_webhook(request: Request):
    c = tg.conf()
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != c.get("secret"):
        raise HTTPException(403, "secret inválido")
    upd = await request.json()

    if cb := upd.get("callback_query"):
        chat = str(cb.get("message", {}).get("chat", {}).get("id", ""))
        if chat != str(c.get("chat_id")):
            return {"ok": True}
        acao, _, slug = (cb.get("data") or "").partition(":")
        if acao == "ok":
            msg = _aprovar(slug, "telegram")
            tg.responder(cb["id"], "Aprovado ✓")
            tg.mandar(f"*{slug}*: {msg}")
        elif acao == "no":
            AGUARDANDO[chat] = slug
            tg.responder(cb["id"], "Responda com o que corrigir")
            tg.mandar(f"O que corrigir em *{slug}*? Responda nesta conversa "
                      f"— vira turno de revisão para o agente.")
        return {"ok": True}

    if msg := upd.get("message"):
        chat = str(msg.get("chat", {}).get("id", ""))
        texto = (msg.get("text") or "").strip()
        if chat == str(c.get("chat_id")) and texto and chat in AGUARDANDO:
            slug = AGUARDANDO.pop(chat)
            registrar_veredito(slug, "reprovado", texto, origem="telegram")
            enfileirar("agente", slug,
                       f"REVISAO da run {slug} na fabrica (git pull --rebase antes; copy/dossie so "
                       f"mudam se o feedback pedir). Feedback do Gustavo:\n\n{texto}\n\n"
                       f"Corrija o fita.html de artifacts/runs/{slug}, rode "
                       f"'node engine/assemble.js artifacts/runs/{slug}' e confirme. NAO avance estagio.")
            tg.mandar(f"Feedback registrado. Turno de revisão de *{slug}* na fila.")
    return {"ok": True}


@app.post("/run/{slug}/notificar")
def notificar(slug: str):
    d = RUNS / slug
    if not (d / "run.json").exists():
        raise HTTPException(404)
    st = json.loads((d / "run.json").read_text(encoding="utf-8"))
    judge = _read(d / "judge-report.md")
    qa = "QA PASS" if "QA: PASS" in judge else ("QA FAIL" if "QA: FAIL" in judge else "sem judge")
    resumo = f"{st.get('pack')} · {st.get('n') or '?'} slides · estágio {st.get('stage')} · {qa}"
    tg.notificar_fita(slug, d / "strip.png", resumo,
                      _editor_url(slug, st.get("template_id")))
    return RedirectResponse(f"/run/{slug}", status_code=303)


@app.get("/health")
def health():
    with db() as c:
        p = c.execute("SELECT COUNT(*) n FROM jobs WHERE status='pending'").fetchone()["n"]
    return {"ok": True, "runs": len(_runs()), "jobs_pendentes": p, "packs": len(kb.packs())}
