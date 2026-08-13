#!/usr/bin/env python3
"""
Resolve um par tenant/vertical no DynamoDB `tenantConfig` e valida `businessTypes`.

Dado um tenantId + verticalId, monta a PK `TENANT#{tenant}#VERTICAL#{vertical}`
(SK = `CONFIG`), busca o item e:
  - confirma que o item existe;
  - confirma que `businessTypes` existe e tem ao menos 1 entrada habilitada;
  - opcionalmente faz match de um assunto (--subject) contra os labels/values
    dos businessTypes, retornando o match;
  - emite o link de admin no formato
    https://{domain}/admin/plataforma/{tenantId}/{verticalId}.

Saída: JSON em stdout (sempre), para a skill consumir. Código de saída:
  0  -> tenant ok e (se --subject) match encontrado
  3  -> tenant existe mas SEM businessTypes (skill deve pedir cadastro)
  4  -> --subject informado mas nenhum businessType casa com o assunto
  2  -> tenant/config nao encontrado
  1  -> erro inesperado

Uso:
    python scripts/resolve_tenant.py --tenant kultivai --vertical health
    python scripts/resolve_tenant.py --tenant kultivai --vertical health --subject laserterapia
    python scripts/resolve_tenant.py --tenant kultivai --vertical health --env dev
"""

import argparse
import json
from pathlib import Path
import sys
import unicodedata

from botocore.exceptions import ClientError

from aws_auth import get_session

TABLE = "tenantConfig"


def _out(payload, code):
    """Imprime JSON em stdout e sai com o codigo dado."""
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    sys.exit(code)


def _norm(text):
    """lowercase + remove acentos para casamento tolerante."""
    if not text:
        return ""
    t = unicodedata.normalize("NFKD", str(text))
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t.strip().lower()


def _match(subject: str, enabled: list) -> dict | None:
    """Casa o assunto pedido com um businessType. Mesma regra nos dois modos
    (online e offline): exato por value/label, depois parcial nos dois sentidos."""
    s = _norm(subject)
    for bt in enabled:
        if _norm(bt.get("value")) == s or _norm(bt.get("label")) == s:
            return bt
    for bt in enabled:
        lv, ll = _norm(bt.get("value")), _norm(bt.get("label"))
        if s and (s in lv or s in ll or lv in s or ll in s):
            return bt
    return None


def main():
    ap = argparse.ArgumentParser(description="Resolve tenantConfig e valida businessTypes")
    ap.add_argument("--tenant", required=True, help="tenantId (ex: kultivai)")
    ap.add_argument("--vertical", required=True, help="verticalId (ex: health)")
    ap.add_argument("--subject", help="assunto pedido (ex: laserterapia) para casar com businessTypes")
    ap.add_argument("--env", default="prod", choices=["prod", "dev"], help="ambiente AWS (default: prod)")
    ap.add_argument("--offline", action="store_true",
                    help="canoniza o business_type pelo cache local, sem tocar o DynamoDB; "
                         "não resolve tenant/domain (use na criação da run)")
    ap.add_argument("--refresh", action="store_true",
                    help="lê do DynamoDB e reescreve knowledge/business-types.json")
    args = ap.parse_args()

    pk = f"TENANT#{args.tenant}#VERTICAL#{args.vertical}"

    # OFFLINE: a canonização do assunto ("fissura mamária" → laserterapy) não
    # depende do ambiente nem muda entre tenants — é a chave que liga o dossiê a
    # knowledge/imagem/negocios/<bt>.md. O tenantId/domain, esses sim são do
    # ambiente, e só importam na PUBLICAÇÃO, que os re-resolve no destino.
    # Pedir credencial AWS para começar a escrever copy era custo sem retorno.
    if args.offline:
        cache = Path(__file__).resolve().parents[2] / "knowledge" / "business-types.json"
        if not cache.exists():
            _out({"ok": False, "reason": "cache_ausente",
                  "message": f"{cache} não existe — rode com --refresh uma vez"}, 2)
        enabled = json.loads(cache.read_text(encoding="utf-8"))["businessTypes"]
        matched = _match(args.subject, enabled) if args.subject else None
        _out({"ok": bool(matched) or not args.subject,
              "offline": True,
              "tenantId": args.tenant, "verticalId": args.vertical,
              "businessTypes": enabled,
              "matchedBusinessType": matched,
              "message": None if matched or not args.subject else
                         f"'{args.subject}' não casou com nenhum business_type do cache"},
             0 if (matched or not args.subject) else 3)

    try:
        session = get_session(args.env)
        table = session.resource("dynamodb").Table(TABLE)
        resp = table.get_item(Key={"PK": pk, "SK": "CONFIG"})
    except ClientError as exc:
        _out({"ok": False, "stage": "get_item", "error": str(exc), "pk": pk}, 1)
    except Exception as exc:  # noqa: BLE001
        _out({"ok": False, "stage": "session", "error": str(exc)}, 1)

    item = resp.get("Item")
    if not item:
        _out(
            {
                "ok": False,
                "reason": "tenant_config_not_found",
                "pk": pk,
                "message": f"Nenhum tenantConfig para PK={pk} (SK=CONFIG) no ambiente {args.env}.",
            },
            2,
        )

    tenant_id = item.get("tenantId") or args.tenant
    vertical_id = item.get("verticalId") or args.vertical
    domain = item.get("domain")
    admin_link = (
        f"https://{domain}/admin/plataforma/{tenant_id}/{vertical_id}" if domain else None
    )

    business_types = item.get("businessTypes") or []
    enabled = [bt for bt in business_types if bt.get("enabled", True)]

    if not enabled:
        _out(
            {
                "ok": False,
                "reason": "no_business_types",
                "pk": pk,
                "tenantId": tenant_id,
                "verticalId": vertical_id,
                "domain": domain,
                "adminLink": admin_link,
                "message": (
                    "Este tenant/vertical nao possui businessTypes cadastrados. "
                    "Peca ao usuario para cadastrar na plataforma e retorne o link de admin."
                ),
            },
            3,
        )

    catalog = [
        {"label": bt.get("label"), "value": bt.get("value"), "emoji": bt.get("emoji")}
        for bt in enabled
    ]

    if args.refresh:
        import datetime
        cache = Path(__file__).resolve().parents[2] / "knowledge" / "business-types.json"
        cache.write_text(json.dumps({
            "_comment": "Cache dos business_type do tenantConfig. Editavel a mao; o "
                        "resolve_tenant.py so consulta o DynamoDB com --refresh.",
            "atualizado_em": datetime.date.today().isoformat(),
            "fonte": f"{tenant_id}/{vertical_id} ({args.env})",
            "businessTypes": catalog,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"cache atualizado: {cache} ({len(catalog)} tipos)", file=sys.stderr)

    matched = _match(args.subject, enabled) if args.subject else None
    if args.subject:
        if not matched:
            _out(
                {
                    "ok": False,
                    "reason": "subject_no_match",
                    "subject": args.subject,
                    "tenantId": tenant_id,
                    "verticalId": vertical_id,
                    "domain": domain,
                    "adminLink": admin_link,
                    "businessTypes": catalog,
                    "message": (
                        f"O assunto '{args.subject}' nao casa com nenhum businessType cadastrado. "
                        "Mostre os disponiveis ao usuario ou peca cadastro (use adminLink)."
                    ),
                },
                4,
            )

    _out(
        {
            "ok": True,
            "pk": pk,
            "tenantId": tenant_id,
            "verticalId": vertical_id,
            "domain": domain,
            "adminLink": admin_link,
            "businessTypes": catalog,
            "matchedBusinessType": (
                {
                    "label": matched.get("label"),
                    "value": matched.get("value"),
                    "emoji": matched.get("emoji"),
                }
                if matched
                else None
            ),
        },
        0,
    )


if __name__ == "__main__":
    main()
