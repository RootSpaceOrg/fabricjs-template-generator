#!/usr/bin/env python3
"""Fila de execução da fábrica — tipos FECHADOS de job (nunca comando cru).

Worker serial: o OpenClaw processa um turno por vez e o corredor é pesado.
Lock em arquivo compartilhado evita competir com turnos disparados por SSH.
"""
from __future__ import annotations

import json
import os
import shlex
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path

FACTORY = Path("/root/.openclaw/workspace/external/fabricjs-template-generator")
RUNS = FACTORY / "artifacts" / "runs"
DB = Path("/root/portal/portal.db")
LOCK = Path("/root/.factory-lock")
NODE_BIN = "/root/.nvm/versions/node/v24.18.1/bin"
OPENCLAW = "/usr/lib/node_modules/openclaw/dist/index.js"

# tipos fechados: o payload nunca vira shell — só preenche templates conhecidos
TIPOS = ("corredor", "advance", "agente", "upload")

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo TEXT NOT NULL, slug TEXT NOT NULL, payload TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'pending',
  log TEXT DEFAULT '', criado_em TEXT NOT NULL,
  iniciado_em TEXT, terminado_em TEXT, pai INTEGER
);
CREATE TABLE IF NOT EXISTS vereditos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT NOT NULL, veredito TEXT NOT NULL, texto TEXT DEFAULT '',
  origem TEXT DEFAULT 'portal', criado_em TEXT NOT NULL
);
"""


def db() -> sqlite3.Connection:
    c = sqlite3.connect(DB, timeout=30)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    cols = {r["name"] for r in c.execute("PRAGMA table_info(jobs)")}
    if "pai" not in cols:
        c.execute("ALTER TABLE jobs ADD COLUMN pai INTEGER")
    return c


def enfileirar(tipo: str, slug: str, payload: str = "", pai: int | None = None) -> int:
    if tipo not in TIPOS:
        raise ValueError(f"tipo inválido: {tipo}")
    with db() as c:
        cur = c.execute(
            "INSERT INTO jobs (tipo, slug, payload, criado_em, pai) VALUES (?,?,?,?,?)",
            (tipo, slug, payload, datetime.now().isoformat(timespec="seconds"), pai))
        return cur.lastrowid


def historico(job_id: int, limite: int = 3) -> list[dict]:
    """Fio da conversa: sobe pela cadeia de 'pai' até o job original."""
    fio, atual = [], job_id
    with db() as c:
        while atual and len(fio) < limite:
            j = c.execute("SELECT id, payload, log, pai FROM jobs WHERE id=?", (atual,)).fetchone()
            if not j:
                break
            fio.append({"id": j["id"], "payload": j["payload"] or "", "log": j["log"] or ""})
            atual = j["pai"]
    return list(reversed(fio))


def registrar_veredito(slug: str, veredito: str, texto: str = "", origem: str = "portal") -> None:
    with db() as c:
        c.execute("INSERT INTO vereditos (slug, veredito, texto, origem, criado_em) VALUES (?,?,?,?,?)",
                  (slug, veredito, texto, origem, datetime.now().isoformat(timespec="seconds")))


def _env() -> dict:
    e = dict(os.environ)
    e["PATH"] = NODE_BIN + ":" + e.get("PATH", "")
    return e


def _sh(cmd: list[str], timeout: int) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, cwd=FACTORY, env=_env(), capture_output=True,
                           text=True, timeout=timeout, errors="replace")
        return r.returncode, (r.stdout + r.stderr)[-8000:]
    except subprocess.TimeoutExpired:
        return 124, f"TIMEOUT após {timeout}s"


def _corredor(slug: str) -> tuple[int, str]:
    """assemble → convert → validate. Não avança estágio: gate é do runner."""
    d = f"artifacts/runs/{slug}"
    logs = []
    for cmd, t in ((["node", "engine/assemble.js", d], 420),
                   (["node", "engine/convert.js", d, f"{d}/output", "--slug", slug], 600),
                   (["node", "engine/tools/validate-slides.js", f"{d}/output"], 240)):
        rc, out = _sh(cmd, t)
        logs.append(f"$ {' '.join(cmd[:2])}\n{out.strip()[-1500:]}")
        if rc != 0 and "validate" not in cmd[1]:
            return rc, "\n\n".join(logs)
    return 0, "\n\n".join(logs)


def _agente(slug: str, prompt: str) -> tuple[int, str]:
    """Turno one-shot do OpenClaw. Serial: o lock impede concorrência."""
    return _sh(["node", OPENCLAW, "agent", "--agent", "main", "-m", prompt], 1500)


def executar(job: sqlite3.Row) -> tuple[int, str]:
    slug, tipo, payload = job["slug"], job["tipo"], job["payload"] or ""
    if tipo == "corredor":
        return _corredor(slug)
    if tipo == "advance":
        return _sh(["python3", "engine/run.py", "advance", slug], 300)
    if tipo == "upload":
        return _sh(["python3", "engine/tools/upload.py", slug], 600)
    if tipo == "agente":
        return _agente(slug, payload)
    return 1, f"tipo desconhecido: {tipo}"


def _avisar(job: sqlite3.Row, rc: int, status: str = "done") -> None:
    """Avisa no Telegram quando o trabalho pesado termina (fita pronta ou falha)."""
    try:
        import telegram as tg
        if not tg.ativo():
            return
        slug, tipo = job["slug"], job["tipo"]
        d = RUNS / slug
        strip = d / "strip.png"
        if rc != 0:
            tg.mandar(f"⚠️ *{slug}*: job `{tipo}` falhou. Veja o log no portal.")
            return
        if status == "bloqueado":
            # o agente parou e perguntou algo — mostra a pergunta, não o log inteiro
            pergunta = (job["log"] or "").strip()
            for corte in ("[plugins]", "plugins.allow"):
                if corte in pergunta:
                    pergunta = pergunta.split(corte)[0].strip()
            tg.mandar(f"🟡 *{slug}*: o agente parou e perguntou:\n\n{pergunta[-900:]}")
            return
        if tipo in ("agente", "corredor") and strip.exists():
            st = json.loads((d / "run.json").read_text(encoding="utf-8")) if (d / "run.json").exists() else {}
            judge = (d / "judge-report.md").read_text(encoding="utf-8", errors="replace")                 if (d / "judge-report.md").exists() else ""
            qa = "QA PASS" if "QA: PASS" in judge else ("QA FAIL" if "QA: FAIL" in judge else "sem judge")
            resumo = f"{st.get('pack', '?')} · {st.get('n') or '?'} slides · {st.get('stage', '?')} · {qa}"
            tg.notificar_fita(slug, strip, resumo)
        elif tipo == "upload":
            tg.mandar(f"✅ *{slug}* publicada em dev.")
    except Exception:
        pass


def worker_loop(intervalo: int = 5) -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    while True:
        with db() as c:
            job = c.execute(
                "SELECT * FROM jobs WHERE status='pending' ORDER BY id LIMIT 1").fetchone()
        if not job:
            time.sleep(intervalo)
            continue
        # lock compartilhado com turnos disparados por SSH
        if LOCK.exists() and (time.time() - LOCK.stat().st_mtime) < 1800:
            time.sleep(intervalo)
            continue
        LOCK.write_text(f"portal job {job['id']} {datetime.now().isoformat()}")
        with db() as c:
            c.execute("UPDATE jobs SET status='running', iniciado_em=? WHERE id=?",
                      (datetime.now().isoformat(timespec="seconds"), job["id"]))
        rc, log = executar(job)
        status = "done" if rc == 0 else "failed"
        # turno de agente que era para criar a run mas não criou = bloqueado (ele perguntou algo)
        if (rc == 0 and job["tipo"] == "agente"
                and ("NOVA RUN" in (job["payload"] or "") or "FATIA 1 de" in (job["payload"] or ""))
                and not (RUNS / job["slug"] / "run.json").exists()):
            status = "bloqueado"
        # o agente sai com 0 mesmo quando ele proprio reprova a fita: o disco decide,
        # nao o exit code. Sem judge com PASS, a fatia final nao esta feita.
        if (rc == 0 and job["tipo"] == "agente" and "FATIA 4 de" in (job["payload"] or "")):
            rel = RUNS / job["slug"] / "judge-report.md"
            if "QA: PASS" not in (rel.read_text(encoding="utf-8", errors="replace")
                                  if rel.exists() else ""):
                status = "failed"
        with db() as c:
            c.execute("UPDATE jobs SET status=?, log=?, terminado_em=? WHERE id=?",
                      (status, log, datetime.now().isoformat(timespec="seconds"), job["id"]))
            if status != "done":
                # cadeia de fatias: fatia que não fechou aborta as filhas em vez de
                # deixá-las rodar sobre um estado que não existe
                c.execute("UPDATE jobs SET status='cancelado', log='fatia anterior nao concluiu' "
                          "WHERE status='pending' AND slug=? AND pai IS NOT NULL", (job["slug"],))
        LOCK.unlink(missing_ok=True)
        _avisar(job, rc, status)


if __name__ == "__main__":
    worker_loop()
