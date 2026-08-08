#!/usr/bin/env python3
"""Ponte Telegram do portal: notifica fita pronta e recebe veredito por botão.

Bot PRÓPRIO do portal (webhook) — o bot do OpenClaw usa polling e os dois não
convivem no mesmo token. Config em /root/portal/telegram.json:

    {"token": "...", "chat_id": 2127960807, "secret": "<aleatório>",
     "base": "https://fabrica.kultivai.com.br"}
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

CONF = Path("/root/portal/telegram.json")


def conf() -> dict:
    return json.loads(CONF.read_text(encoding="utf-8")) if CONF.exists() else {}


def ativo() -> bool:
    c = conf()
    return bool(c.get("token") and c.get("chat_id"))


def _api(metodo: str, dados: dict, arquivo: Path | None = None) -> dict:
    c = conf()
    url = f"https://api.telegram.org/bot{c['token']}/{metodo}"
    if arquivo is None:
        req = urllib.request.Request(
            url, data=json.dumps(dados).encode(), headers={"Content-Type": "application/json"})
    else:  # multipart mínimo para sendPhoto
        b = "----portal" + str(abs(hash(str(arquivo))))
        corpo = b""
        for k, v in dados.items():
            corpo += (f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n"
                      f"{v if isinstance(v, str) else json.dumps(v)}\r\n").encode()
        corpo += (f"--{b}\r\nContent-Disposition: form-data; name=\"photo\"; "
                  f"filename=\"{arquivo.name}\"\r\nContent-Type: image/png\r\n\r\n").encode()
        corpo += arquivo.read_bytes() + f"\r\n--{b}--\r\n".encode()
        req = urllib.request.Request(url, data=corpo,
                                     headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def notificar_fita(slug: str, strip: Path | None, resumo: str, template_url: str | None = None) -> bool:
    """Manda o strip com botões Aprovar/Reprovar. Silencioso se não configurado."""
    if not ativo():
        return False
    c = conf()
    botoes = [[{"text": "✓ Aprovar", "callback_data": f"ok:{slug}"},
               {"text": "✕ Reprovar", "callback_data": f"no:{slug}"}],
              [{"text": "Abrir no portal", "url": f"{c.get('base','')}/run/{slug}"}]]
    if template_url:
        botoes[1].append({"text": "Editor", "url": template_url})
    legenda = f"*{slug}*\n{resumo}"
    dados = {"chat_id": str(c["chat_id"]), "caption": legenda, "parse_mode": "Markdown",
             "reply_markup": {"inline_keyboard": botoes}}
    try:
        if strip and strip.exists() and strip.stat().st_size < 9_000_000:
            _api("sendPhoto", dados, strip)
        else:
            _api("sendMessage", {**dados, "text": legenda})
        return True
    except Exception:
        return False


def responder(callback_id: str, texto: str) -> None:
    try:
        _api("answerCallbackQuery", {"callback_query_id": callback_id, "text": texto})
    except Exception:
        pass


def mandar(texto: str) -> bool:
    if not ativo():
        return False
    try:
        _api("sendMessage", {"chat_id": str(conf()["chat_id"]), "text": texto,
                             "parse_mode": "Markdown"})
        return True
    except Exception:
        return False


def registrar_webhook() -> dict:
    """Aponta o bot para /tg/webhook do portal, com secret_token."""
    c = conf()
    return _api("setWebhook", {
        "url": f"{c['base']}/tg/webhook",
        "secret_token": c["secret"],
        "allowed_updates": ["callback_query", "message"],
    })
