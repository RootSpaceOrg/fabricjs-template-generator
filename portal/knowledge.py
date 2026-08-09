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
            "certs": sorted(p.name for p in cert.glob("*-strip.*")) if cert.exists() else [],
        })
    return out


def _padroes(d) -> list[dict]:
    """Padrões de composição do pack: as imagens de exemplos/, com a legenda que
    o tecnicas.md já dá para cada uma (a tabela 'como este estilo resolve').

    A prova das três provas (capa/miolo/CTA) mora aqui — PACKS.md §3.
    """
    import re
    ex = d / "exemplos"
    if not ex.exists():
        return []
    tec = (d / "tecnicas.md").read_text(encoding="utf-8", errors="replace") \
        if (d / "tecnicas.md").is_file() else ""
    # Cada pack documenta como quer; aceitamos as duas formas em uso:
    # 1) tabela com codigo — "| **E1** titulo | descricao |" (clinical)
    legendas = {}
    for linha in tec.splitlines():
        m = re.match(r"\|\s*\*\*([A-Z]\d+[a-z]?)\*\*\s*([^|]*)\|([^|]*)\|", linha)
        if m:
            legendas[m.group(1)] = (m.group(2).strip(), m.group(3).strip())
    # 2) secoes — "## Capa meme (scroll-stop)" casa com ref-capa-meme.png (bold)
    import unicodedata

    def slugify(s: str) -> str:
        # sem acento: o nome do arquivo é ASCII, o título do .md não
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
        return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

    # 1b) tabela por NOME — "| **card-ancorado** | composicao | bom para | ... |"
    #     o negrito casa direto com o arquivo ref-card-ancorado.html
    por_nome = {}
    for linha in tec.splitlines():
        m = re.match(r"\|\s*\*\*([a-z][a-z0-9-]+)\*\*\s*\|([^|]*)\|", linha)
        if m:
            por_nome[m.group(1)] = (m.group(1).replace("-", " "), m.group(2).strip())

    secoes = {}
    for titulo in re.findall(r"^## (.+)$", tec, re.M):
        chave = slugify(titulo.split("(")[0])
        primeira = ""
        bloco = tec.split(f"## {titulo}", 1)[-1].strip().splitlines()
        for ln in bloco:
            if ln.strip() and not ln.startswith("#"):
                primeira = re.sub(r"[*`]|\d+\.\s*", "", ln).strip()
                break
        secoes[chave] = (titulo.strip(), primeira[:180])

    def casa_secao(stem: str):
        nome = re.sub(r"^(ref|ex)-|-\d+$", "", slugify(stem))
        for chave, val in secoes.items():
            if nome and (nome in chave or chave.startswith(nome)):
                return val
        return None
    out = []
    for img in sorted(ex.rglob("*")):
        if img.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        cod = img.stem.split("-")[0].upper()
        titulo, desc = legendas.get(cod, ("", ""))
        if not titulo:
            nome = re.sub(r"^(ref|ex)-", "", slugify(img.stem))
            achou = por_nome.get(nome) or casa_secao(img.stem)
            if not achou:
                continue  # asset de teste (foto-larga, decor…) — não é padrão
            cod, (titulo, desc) = "", achou
        elif img.stem.upper() in (cod + "A", cod + "B"):
            continue  # metades de um par: a vista conjunta já representa
        out.append({"rel": str(img.relative_to(ex)).replace("\\", "/"),
                    "cod": cod, "titulo": titulo, "desc": desc})
    return out


def pack_detalhe(slug: str) -> dict | None:
    """Pack + certificação completa (fitas com strip, judge e dossiê)."""
    import json
    d = FACTORY / "packs" / slug
    f = d / "pack.json"
    if not f.is_file():
        return None
    meta = json.loads(f.read_text(encoding="utf-8"))
    cert = d / "certification"
    fitas = []
    if cert.exists():
        # strip.png ou .jpg: a certificação guarda comprimido (16MB -> 1.4MB)
        for strip in sorted(cert.glob("*-strip.*")):
            base = strip.stem[:-len("-strip")]
            fitas.append({
                "nome": base, "strip": strip.name,
                "judge": (cert / f"{base}-judge-report.md").read_text(encoding="utf-8", errors="replace")
                if (cert / f"{base}-judge-report.md").exists() else "",
                "dossie": (cert / f"{base}-dossie.md").read_text(encoding="utf-8", errors="replace")
                if (cert / f"{base}-dossie.md").exists() else "",
                "fidelity": (cert / f"{base}-fidelity.md").read_text(encoding="utf-8", errors="replace")
                if (cert / f"{base}-fidelity.md").exists() else "",
            })
    ev = cert / "evidencia.md"
    return {
        "slug": slug, "meta": meta, "status": meta.get("status", "?"),
        "familia": meta.get("familia", ""), "versao": meta.get("version"),
        "certificado_em": meta.get("certificado_em"),
        "assinaturas": meta.get("assinaturas", []),
        "tokens": meta.get("tokens", {}), "fit": meta.get("fit", {}),
        "slides": meta.get("slides", {}),
        "tem_reference": (d / "reference.png").exists(),
        "arquivos": [{"rel": str(x.relative_to(FACTORY)).replace("\\", "/"), "nome": x.name}
                     for x in sorted(d.glob("*.md"))],
        "exemplos": sorted(x.name for x in (d / "exemplos").glob("*")) if (d / "exemplos").exists() else [],
        "padroes": _padroes(d),
        "evidencia": ev.read_text(encoding="utf-8", errors="replace") if ev.exists() else "",
        "fitas": fitas,
    }


def queue() -> list[dict]:
    d = FACTORY / "pack-queue"
    if not d.exists():
        return []
    return [{"nome": p.name, "tamanho": f"{p.stat().st_size//1024} KB"}
            for p in sorted(d.iterdir()) if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
