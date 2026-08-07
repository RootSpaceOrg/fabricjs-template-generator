#!/usr/bin/env python3
"""Leitura/edição do conhecimento da fábrica com commit+push automático.

Regra de segurança: só caminhos dentro da whitelist e só .md/.json — o portal
nunca escreve em engine/ nem em artifacts/.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from jobs import FACTORY

# prefixos editáveis pelo portal (o que é conhecimento, não motor)
EDITAVEIS = ("knowledge/", "packs/", "compliance/", "evals/", "CONTEXT.md", "JUDGE.md", "PACKS.md")
EXTS = (".md", ".json")


def _seguro(rel: str) -> Path:
    p = (FACTORY / rel).resolve()
    if not str(p).startswith(str(FACTORY.resolve())):
        raise ValueError("caminho fora da fábrica")
    if not rel.startswith(EDITAVEIS) or p.suffix not in EXTS:
        raise ValueError(f"não editável: {rel}")
    return p


def ler(rel: str) -> str:
    p = _seguro(rel)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def salvar(rel: str, conteudo: str, msg: str | None = None) -> tuple[bool, str]:
    """Grava, commita e faz push. Retorna (ok, saída)."""
    p = _seguro(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(conteudo.replace("\r\n", "\n"), encoding="utf-8")
    msg = msg or f"portal: edita {rel}"
    out = []
    for cmd in (["git", "add", rel],
                ["git", "-c", "user.name=Portal", "-c", "user.email=portal@kultivai",
                 "commit", "-m", f"{msg}\n\nEditado pelo portal de backoffice."],
                ["git", "pull", "--rebase", "-q", "origin", "main"],
                ["git", "push", "-q", "origin", "main"]):
        r = subprocess.run(cmd, cwd=FACTORY, capture_output=True, text=True, timeout=180)
        out.append((r.stdout + r.stderr).strip())
        if r.returncode != 0 and cmd[1] == "commit" and "nothing to commit" in (r.stdout + r.stderr):
            return True, "sem mudanças"
        if r.returncode != 0 and cmd[1] not in ("commit",):
            return False, "\n".join(x for x in out if x)
    return True, "commitado e enviado"


def arvore() -> dict[str, list[dict]]:
    """Mapa do conhecimento por grupo, para a tela."""
    grupos: dict[str, list[dict]] = {}

    def add(grupo: str, p: Path) -> None:
        rel = str(p.relative_to(FACTORY)).replace("\\", "/")
        grupos.setdefault(grupo, []).append(
            {"rel": rel, "nome": p.name, "linhas": len(p.read_text(encoding="utf-8", errors="replace").splitlines())})

    for p in sorted((FACTORY / "knowledge" / "copy").rglob("*.md")):
        add("Copy", p)
    for p in sorted((FACTORY / "knowledge" / "design").rglob("*.md")):
        add("Design", p)
    for p in sorted((FACTORY / "compliance").glob("*.md")):
        add("Compliance", p)
    for f in ("CONTEXT.md", "JUDGE.md", "PACKS.md"):
        if (FACTORY / f).exists():
            add("Doutrina", FACTORY / f)
    ev = FACTORY / "evals" / "lessons.md"
    if ev.exists():
        add("Lições globais", ev)
    return grupos


def packs() -> list[dict]:
    out = []
    import json
    for d in sorted((FACTORY / "packs").iterdir()):
        f = d / "pack.json"
        if not f.is_file():
            continue
        meta = json.loads(f.read_text(encoding="utf-8"))
        arquivos = [{"rel": str(p.relative_to(FACTORY)).replace("\\", "/"), "nome": p.name}
                    for p in sorted(d.glob("*.md"))]
        cert = d / "certification"
        out.append({
            "slug": d.name, "status": meta.get("status", "?"), "versao": meta.get("version"),
            "familia": meta.get("familia", ""), "funil": ", ".join(meta.get("fit", {}).get("funil", [])),
            "slides": f'{meta.get("slides", {}).get("min", "?")}–{meta.get("slides", {}).get("max", "?")}',
            "certificado_em": meta.get("certificado_em"),
            "tem_reference": (d / "reference.png").exists(),
            "arquivos": arquivos, "pack_json": f"packs/{d.name}/pack.json",
            "certs": sorted(p.name for p in cert.glob("*-strip.png")) if cert.exists() else [],
        })
    return out


def queue() -> list[dict]:
    d = FACTORY / "pack-queue"
    if not d.exists():
        return []
    return [{"nome": p.name, "tamanho": f"{p.stat().st_size//1024} KB"}
            for p in sorted(d.iterdir()) if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
