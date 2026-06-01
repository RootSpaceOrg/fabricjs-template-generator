#!/usr/bin/env python3
"""Upload GetPosts template JSON slides to S3 and insert public.templates row.

Default is dry-run. Add --execute to perform S3 uploads and Supabase insert.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import boto3

# Diretório onde estão os arquivos .env de credenciais AWS.
# Default (legado openclaw): /root/.openclaw/workspace/secrets
# Em Windows ou em VPS com layout diferente, defina GP2_SECRETS_DIR.
SECRETS_DIR = Path(
    os.environ.get("GP2_SECRETS_DIR", "/root/.openclaw/workspace/secrets")
)

ENV_CONFIG = {
    "dev": {
        "aws_env_path": SECRETS_DIR / "aws-credentials-template-generator-mkt-platform-dev.env",
        "role_arn": "arn:aws:iam::656032436386:role/TemplateGeneratorRole",
        "aws_region": "sa-east-1",
        "s3_bucket": "mkt-platform-templates-dev",
        "template_handler_lambda": "app-lambda-template-handler",
    },
    "prod": {
        "aws_env_path": SECRETS_DIR / "aws-credentials-template-generator-mkt-platform-prod.env",
        "role_arn": "arn:aws:iam::692046683598:role/TemplateGeneratorRole",
        "aws_region": "sa-east-1",
        "s3_bucket": "mkt-platform-templates-prod",
        "template_handler_lambda": "app-lambda-template-handler",
    },
}
DEFAULT_S3_KEY_TEMPLATE = "editor_templates/{template_id}/{image_id}/template.json"


def load_env_file(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"AWS env file not found: {path}")
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key] = value.strip().strip('"').strip("'")


def assume_role(env_config: dict[str, Any]):
    load_env_file(env_config["aws_env_path"])
    sts = boto3.client("sts", region_name="us-east-1")
    creds = sts.assume_role(
        RoleArn=env_config["role_arn"], RoleSessionName="openclaw-template-import"
    )["Credentials"]
    kwargs = {
        "aws_access_key_id": creds["AccessKeyId"],
        "aws_secret_access_key": creds["SecretAccessKey"],
        "aws_session_token": creds["SessionToken"],
    }
    return kwargs


def check_credentials(environment: str) -> None:
    """Validate that the AWS env file exists and that STS assume-role works.

    Does NOT touch S3 or Lambda. Used by the SETUP.md preflight to confirm
    the uploader is wired correctly before any real upload.
    """
    env_config = ENV_CONFIG[environment]
    aws_env_path = env_config["aws_env_path"]
    result: dict[str, Any] = {
        "status": "ok",
        "environment": environment,
        "secrets_dir": str(SECRETS_DIR),
        "aws_env_path": str(aws_env_path),
        "role_arn": env_config["role_arn"],
    }
    if not aws_env_path.exists():
        result["status"] = "fail"
        result["error"] = f"AWS env file not found: {aws_env_path}"
        result["hint"] = (
            "Defina GP2_SECRETS_DIR para apontar para o diretório com os arquivos "
            "aws-credentials-template-generator-mkt-platform-{dev,prod}.env, "
            "ou copie os arquivos para o caminho mostrado em aws_env_path."
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    try:
        load_env_file(aws_env_path)
        sts = boto3.client("sts", region_name="us-east-1")
        creds = sts.assume_role(
            RoleArn=env_config["role_arn"],
            RoleSessionName="openclaw-template-import-check",
        )["Credentials"]
        result["assumed_role_arn"] = creds.get("AccessKeyId") and env_config["role_arn"]
        result["expiration"] = creds["Expiration"].isoformat() if creds.get("Expiration") else None
    except Exception as exc:  # noqa: BLE001 — surface any STS / credential error.
        result["status"] = "fail"
        result["error"] = f"{type(exc).__name__}: {exc}"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def nanoid(size: int = 21) -> str:
    alphabet = string.ascii_letters + string.digits + "_-"
    return "".join(random.SystemRandom().choice(alphabet) for _ in range(size))


def find_slide_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    output = path / "output"
    folder = output if output.exists() else path
    files = sorted(
        folder.glob("slide-*.json"), key=lambda p: int(p.stem.split("-")[-1])
    )
    if not files:
        raise RuntimeError(f"No slide-N.json files found in {path} or {output}")
    return files


def load_manifest(path: Path) -> dict[str, Any]:
    candidates = (
        [path / "manifest.json", path / "output" / "manifest.json"]
        if path.is_dir()
        else [path.parent / "manifest.json"]
    )
    for candidate in candidates:
        if candidate.exists():
            return json.loads(candidate.read_text())
    return {}


def load_context_analysis(path: Path) -> dict[str, Any]:
    """Load context-analysis.json or template-summary.md from the artifact tree when present."""
    base = path if path.is_dir() else path.parent
    # v2: prefer template-summary.md from gp2-template-marker artifacts
    summary_candidates = [
        base / "template-summary.md",
        base.parent / "gp2-template-marker" / base.name / "template-summary.md",
        base.parent.parent / "gp2-template-marker" / base.name / "template-summary.md",
    ]
    for candidate in summary_candidates:
        if candidate.exists():
            return {"_sourcePath": str(candidate), "_summary": candidate.read_text()}
    # v1 fallback: context-analysis.json
    candidates = [
        base / "context-analysis.json",
        base / "output" / "context-analysis.json",
        base.parent / "context-analysis.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            data = json.loads(candidate.read_text())
            if isinstance(data, dict):
                data["_sourcePath"] = str(candidate)
                return data
    return {}


def load_slides(path: Path) -> tuple[list[tuple[Path, dict[str, Any]]], dict[str, Any]]:
    files = find_slide_files(path)
    slides = []
    for file in files:
        slides.append((file, json.loads(file.read_text())))
    manifest = load_manifest(path if path.is_dir() else files[0].parent)
    return slides, manifest


def build_description(
    name: str,
    slides: list[tuple[Path, dict[str, Any]]],
    user_hint: str | None = None,
    context: dict[str, Any] | None = None,
) -> str:
    """Description = template-summary.md verbatim.

    The marker (gp2-template-marker) is the single source of truth for the
    template's narrative description. The uploader does not rewrite, wrap, or
    enrich it — that only produces duplication and dilution.

    Precedence:
      1. context._summary (template-summary.md loaded from artifacts)
      2. user_hint (passed via --description-hint; usually the same file's content)
      3. error — on v2 the summary is mandatory.
    """
    context = context or {}
    summary_md = (context.get("_summary") or "").strip()
    if summary_md:
        return summary_md
    hint = (user_hint or "").strip()
    if hint:
        return hint
    raise RuntimeError(
        "No description source available. Expected template-summary.md from "
        "gp2-template-marker artifacts or --description-hint. Pipeline v2 "
        "requires the marker step to run before upload."
    )


def infer_dimensions(
    slides: list[tuple[Path, dict[str, Any]]], manifest: dict[str, Any]
) -> tuple[int, int]:
    mslides = manifest.get("slides") if isinstance(manifest, dict) else None
    if isinstance(mslides, list) and mslides:
        first = mslides[0]
        if first.get("width") and first.get("height"):
            return int(first["width"]), int(first["height"])
    # Try to read from first slide JSON (Fabric canvas stores width/height at root)
    if slides:
        _, first_slide = slides[0]
        w = first_slide.get("width")
        h = first_slide.get("height")
        if w and h:
            return int(w), int(h)
    return 1080, 1350


def build_payload(
    args, slides, manifest, template_id: str, description: str
) -> dict[str, Any]:
    width, height = infer_dimensions(slides, manifest)
    images = [{"order": str(i), "imageId": str(i)} for i in range(len(slides))]
    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    payload = {
        "id": template_id,
        "name": args.name or manifest.get("templateName") or template_id,
        "width": width,
        "height": height,
        "metadata": {},
        "images": images,
        "description": description,
        "status": args.status,
        "template_type": args.template_type,
        "owner_user_id": args.owner_user_id,
        "created_by": "templateGenerator",
        "content_type": args.content_type,
        "business_type": "",
        "tags": tags,
        "scope": args.scope,
    }
    if args.tenant_id:
        payload["tenant_id"] = args.tenant_id
    if args.vertical_id:
        payload["vertical_id"] = args.vertical_id
    return payload


def upload_slides(
    s3, slides, template_id: str, key_template: str, bucket: str, dry_run: bool
) -> list[str]:
    uploaded = []
    for idx, (file, _) in enumerate(slides):
        image_id = str(idx)
        key = key_template.format(
            template_id=template_id,
            image_id=image_id,
            order=image_id,
            filename=file.name,
        )
        uploaded.append(key)
        if dry_run:
            continue
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=file.read_bytes(),
            ContentType="application/json; charset=utf-8",
            CacheControl="public, max-age=31536000, immutable",
        )
    return uploaded


def build_handler_event(payload: dict[str, Any], owner_user_id: str) -> dict[str, Any]:
    """Build an API-Gateway-shaped event so APIGatewayRestResolver can route the request.

    Bypasses the real API Gateway: invokes the template-handler Lambda directly
    via boto3 with a synthetic authorizer that grants admin access to the uploader.
    """
    return {
        "httpMethod": "POST",
        "path": "/templates",
        "resource": "/templates",
        "body": json.dumps(payload, ensure_ascii=False),
        "headers": {"Content-Type": "application/json"},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "isBase64Encoded": False,
        "requestContext": {
            "httpMethod": "POST",
            "path": "/templates",
            "resourcePath": "/templates",
            "stage": "api",
            "authorizer": {
                "userId": owner_user_id,
                "role": "admin",
                "email": "",
                "name": owner_user_id,
                "tenantId": "",
                "verticalId": "",
                "sessionId": "",
                "expireOn": 0,
                "tenantStatus": "",
                "tenantDisplayName": "",
                "businessTypes": "[]",
            },
        },
    }


def invoke_template_handler(
    lambda_client,
    function_name: str,
    payload: dict[str, Any],
    owner_user_id: str,
    dry_run: bool,
):
    """Invoke template-handler Lambda directly with a synthetic API Gateway event."""
    event = build_handler_event(payload, owner_user_id)
    if dry_run:
        return {"dryRun": True, "payload": payload, "invokeEvent": event}

    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(event).encode("utf-8"),
    )

    raw = response["Payload"].read().decode("utf-8")
    if response.get("FunctionError"):
        raise RuntimeError(
            f"template-handler invoke FunctionError ({response['FunctionError']}): {raw[:1000]}"
        )

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"template-handler returned non-JSON payload: {raw[:1000]}")

    status_code = parsed.get("statusCode", 0)
    body = parsed.get("body")
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass

    if status_code >= 400:
        raise RuntimeError(
            f"template-handler returned HTTP {status_code}: {json.dumps(body)[:1000]}"
        )

    return {"statusCode": status_code, "body": body}


def main():
    parser = argparse.ArgumentParser(
        description="Import GetPosts v2 generated template JSONs into S3 + Supabase."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Folder containing output/slide-N.json or slide-N.json files",
    )
    parser.add_argument(
        "--check-credentials",
        action="store_true",
        help="Validate that the AWS env file is readable and that STS assume-role works for the target environment. Does NOT touch S3 or Lambda. Exits after printing the result.",
    )
    parser.add_argument("--name", help="Template name")
    parser.add_argument(
        "--template-id",
        default=None,
        help="Optional template id; default generates nanoid-like id",
    )
    parser.add_argument("--content-type", default="instagram-feed")
    parser.add_argument(
        "--template-type",
        default="ai",
        help="template_type column (default: ai)",
    )
    parser.add_argument("--tags", default="")
    parser.add_argument("--status", default="review")
    parser.add_argument(
        "--owner-user-id",
        default="templateGenerator",
        help="owner_user_id column (default: templateGenerator)",
    )
    parser.add_argument("--tenant-id", default=None, help="tenant_id (default: null)")
    parser.add_argument(
        "--vertical-id", default=None, help="vertical_id (default: null)"
    )
    parser.add_argument(
        "--scope",
        default="platform",
        help="scope column: platform, tenant, vertical, private (default: platform)",
    )
    parser.add_argument(
        "--environment",
        "--env",
        choices=["dev", "prod"],
        default="prod",
        help="Target environment (default: prod)",
    )
    parser.add_argument(
        "--description-hint",
        default=None,
        help="High-level purpose or template-summary.md content to include in description",
    )
    parser.add_argument("--s3-key-template", default=DEFAULT_S3_KEY_TEMPLATE)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually upload to S3 and insert into Supabase",
    )
    args = parser.parse_args()

    if args.check_credentials:
        check_credentials(args.environment)
        return

    if not args.path:
        parser.error("the following arguments are required: path (or use --check-credentials)")

    source = Path(args.path).resolve()
    slides, manifest = load_slides(source)
    context = load_context_analysis(source)
    template_id = args.template_id or nanoid()
    name = args.name or manifest.get("templateName") or template_id
    description = build_description(name, slides, args.description_hint, context)
    payload = build_payload(args, slides, manifest, template_id, description)

    dry_run = not args.execute
    env = ENV_CONFIG[args.environment]
    aws_kwargs = assume_role(env)
    s3 = boto3.client("s3", region_name=env["aws_region"], **aws_kwargs)
    lambda_client = boto3.client(
        "lambda", region_name=env["aws_region"], **aws_kwargs
    )

    keys = upload_slides(
        s3, slides, template_id, args.s3_key_template, env["s3_bucket"], dry_run
    )
    result = invoke_template_handler(
        lambda_client,
        env["template_handler_lambda"],
        payload,
        args.owner_user_id,
        dry_run,
    )

    safe_output = {
        "mode": "dry-run" if dry_run else "executed",
        "environment": args.environment,
        "templateId": template_id,
        "name": payload["name"],
        "slides": len(slides),
        "s3Bucket": env["s3_bucket"],
        "s3Keys": keys,
        "templateHandlerLambda": env["template_handler_lambda"],
        "handlerResult": payload if dry_run else result,
        "contextSource": context.get("_sourcePath") if context else None,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(safe_output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
