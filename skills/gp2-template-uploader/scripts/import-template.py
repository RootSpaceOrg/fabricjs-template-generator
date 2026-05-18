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
import requests

ENV_CONFIG = {
    "dev": {
        "aws_env_path": Path(
            "/root/.openclaw/workspace/secrets/aws-credentials-template-generator-mkt-platform-dev.env"
        ),
        "role_arn": "arn:aws:iam::656032436386:role/TemplateGeneratorRole",
        "aws_region": "sa-east-1",
        "ssm_parameter": "/default/supabase-database-credentials",
        "s3_bucket": "mkt-platform-templates-dev",
    },
    "prod": {
        "aws_env_path": Path(
            "/root/.openclaw/workspace/secrets/aws-credentials-template-generator-mkt-platform-prod.env"
        ),
        "role_arn": "arn:aws:iam::692046683598:role/TemplateGeneratorRole",
        "aws_region": "sa-east-1",
        "ssm_parameter": "/default/supabase-database-credentials",
        "s3_bucket": "mkt-platform-templates-prod",
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


def load_supabase_credentials(
    aws_kwargs: dict[str, str], env_config: dict[str, Any]
) -> tuple[str, str]:
    ssm = boto3.client("ssm", region_name=env_config["aws_region"], **aws_kwargs)
    raw = ssm.get_parameter(Name=env_config["ssm_parameter"], WithDecryption=True)[
        "Parameter"
    ]["Value"]
    data = json.loads(raw)
    url = data.get("url") or data.get("supabaseUrl") or data.get("SUPABASE_URL")
    key = (
        data.get("key")
        or data.get("anonKey")
        or data.get("publishableKey")
        or data.get("apiKey")
    )
    if not url or not key:
        raise RuntimeError(
            f'Incomplete Supabase credentials in {env_config["ssm_parameter"]}'
        )
    return url.rstrip("/"), key


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


def iter_template_elements(slide: dict[str, Any]):
    for obj in slide.get("objects") or []:
        if obj.get("isTemplateElement") is True:
            yield obj


def describe_obj(obj: dict[str, Any]) -> str:
    name = obj.get("name") or obj.get("type") or "Elemento"
    te = obj.get("templateElement") or {}
    desc = te.get("description") or ""
    if obj.get("type") == "textbox":
        sample = str(obj.get("text") or "").replace("\n", " / ")
        max_chars = te.get("maxChars")
        extra = (
            f" Limite sugerido: até {max_chars} caracteres."
            if isinstance(max_chars, int)
            else ""
        )
        return f'{name}: campo de texto editável. {desc} Exemplo atual: "{sample}".{extra}'.strip()
    if obj.get("type") in ("image", "ClippableImage"):
        image_type = obj.get("imageType") or "userAsset"
        return f"{name}: imagem editável do tipo {image_type}. {desc}".strip()
    return f"{name}: elemento editável. {desc}".strip()


def build_story_arc(context: dict[str, Any]) -> str:
    slides = context.get("slides") if isinstance(context, dict) else None
    if not isinstance(slides, list) or not slides:
        return ""
    lines = []
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        number = slide.get("slideNumber") or len(lines) + 1
        role = slide.get("slideRole") or "papel narrativo"
        function = (
            slide.get("storyFunction") or slide.get("readerQuestionAnswered") or ""
        )
        if function:
            lines.append(f"- Slide {number} — {role}: {function}")
    return "\n".join(lines)


def infer_narrative_model(
    context: dict[str, Any], slides: list[tuple[Path, dict[str, Any]]]
) -> str:
    upload_guidance = (
        context.get("uploadGuidance")
        if isinstance(context.get("uploadGuidance"), dict)
        else {}
    )
    overall = context.get("overall") if isinstance(context.get("overall"), dict) else {}
    for key in ("narrativeModel", "modelName", "storyModel"):
        value = upload_guidance.get(key) or overall.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().strip('"""')
    roles = []
    for slide in context.get("slides") or []:
        if isinstance(slide, dict) and slide.get("slideRole"):
            roles.append(str(slide["slideRole"]).lower())
    if roles and "cta" in roles and any(r in roles[0] for r in ("hook", "gancho")):
        return "Do problema percebido à decisão de agir"
    if len(slides) >= 4:
        return "Da atenção inicial ao próximo passo"
    return "Mensagem adaptável com progressão narrativa clara"


def build_slide_structure(slide: dict[str, Any]) -> str:
    elements = slide.get("elements") if isinstance(slide.get("elements"), list) else []
    suggestions = []
    for el in elements:
        if not isinstance(el, dict):
            continue
        role = (
            el.get("storytellingRole")
            or el.get("markerDescriptionSuggestion")
            or el.get("childRole")
        )
        if isinstance(role, str) and role.strip():
            suggestions.append(role.strip().rstrip("."))
    if suggestions:
        return "; ".join(suggestions[:3]) + "."
    question = slide.get("readerQuestionAnswered")
    if isinstance(question, str) and question.strip():
        return f"Conteúdo organizado para responder: {question.strip()}"
    return "Estrutura adaptável conforme a função narrativa da lâmina."


def build_narrative_arc(context: dict[str, Any], slide_count: int) -> str:
    slides = context.get("slides") if isinstance(context, dict) else None
    if not isinstance(slides, list) or not slides:
        return "\n".join(
            f"{idx}. Lâmina {idx} — Etapa narrativa {idx}\nFunção: avançar a mensagem principal do template.\nEstrutura: adaptar título, explicação e chamada conforme o objetivo do post."
            for idx in range(1, slide_count + 1)
        )

    blocks = []
    for idx, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            continue
        number = slide.get("slideNumber") or idx
        role = slide.get("slideRole") or "etapa narrativa"
        function = (
            slide.get("storyFunction")
            or slide.get("readerQuestionAnswered")
            or "avançar a história do template de forma clara."
        )
        structure = build_slide_structure(slide)
        blocks.append(
            f"{number}. Lâmina {number} — {role}\nFunção: {function}\nEstrutura: {structure}"
        )
    return "\n\n".join(blocks)


def build_description(
    name: str,
    slides: list[tuple[Path, dict[str, Any]]],
    user_hint: str | None = None,
    context: dict[str, Any] | None = None,
) -> str:
    context = context or {}

    # v2: if context has a _summary (from template-summary.md), use it as the narrative backbone
    summary_md = context.get("_summary", "")
    if summary_md and user_hint:
        hint = user_hint.strip()
        return (
            "Descrição Geral:\n"
            f'Modelo adaptável: "Template HealthMarket — {name}"\n\n'
            f"Propósito do template:\n{hint}\n\n"
            f"Arco narrativo:\n{summary_md.strip()}\n\n"
            f"Layout e estrutura:\nTemplate com {len(slides)} slide(s), preparado para publicação em redes sociais. "
            "Composição guia a leitura em etapas com hierarquia visual clara, ritmo narrativo e fechamento com próximo passo.\n\n"
            "Uso recomendado:\nUse quando precisar conduzir a audiência por uma sequência clara de reconhecimento, compreensão e convite para agir."
        )

    overall = context.get("overall") if isinstance(context.get("overall"), dict) else {}
    upload_guidance = (
        context.get("uploadGuidance")
        if isinstance(context.get("uploadGuidance"), dict)
        else {}
    )
    hint = (user_hint or "").strip()
    purpose = (
        hint
        or overall.get("postPurpose")
        or upload_guidance.get("semanticSummary")
        or f'criar um template editável chamado "{name}" para conteúdo de marketing digital.'
    )
    narrative_model = infer_narrative_model(context, slides)
    story_arc = build_narrative_arc(context, len(slides))
    recommended = (
        upload_guidance.get("useRecommendedFor")
        or overall.get("audienceIntent")
        or (
            "Use este template quando o usuário precisar conduzir a audiência por uma sequência clara: reconhecimento do problema, compreensão do contexto, percepção de importância e convite para agir."
        )
    )

    return (
        "Descrição Geral:\n"
        f'Modelo adaptável: "{narrative_model}"\n\n'
        f"Propósito do template:\n{purpose}\n\n"
        "Layout e estrutura:\n"
        f"Template com {len(slides)} slide(s), preparado para publicação em redes sociais. "
        "A composição foi pensada para guiar a leitura em etapas, preservando hierarquia visual clara, ritmo narrativo e fechamento com próximo passo.\n\n"
        + f"Dinâmica do carrossel:\n{story_arc}\n\n"
        + "Uso recomendado:\n"
        + f"{recommended}"
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
        "template_type": "ai",
        "owner_user_id": args.owner_user_id,
        "created_by": "templateGenerator",
        "content_type": args.content_type,
        "business_type": args.business_type or "",
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


def insert_template(
    supabase_url: str, supabase_key: str, payload: dict[str, Any], dry_run: bool
):
    if dry_run:
        return {"dryRun": True, "payload": payload}
    res = requests.post(
        f"{supabase_url}/rest/v1/templates",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json=payload,
        timeout=30,
    )
    if not res.ok:
        raise RuntimeError(
            f"Supabase insert failed: HTTP {res.status_code}: {res.text[:1000]}"
        )
    try:
        return res.json()
    except Exception:
        return {"status": res.status_code, "text": res.text}


def main():
    parser = argparse.ArgumentParser(
        description="Import GetPosts v2 generated template JSONs into S3 + Supabase."
    )
    parser.add_argument(
        "path", help="Folder containing output/slide-N.json or slide-N.json files"
    )
    parser.add_argument("--name", help="Template name")
    parser.add_argument(
        "--template-id",
        default=None,
        help="Optional template id; default generates nanoid-like id",
    )
    parser.add_argument(
        "--business-type",
        default="",
        help="metadata.businessType, e.g. physiotherapy, laserterapy",
    )
    parser.add_argument("--content-type", default="instagram-feed")
    parser.add_argument("--tags", default="")
    parser.add_argument("--status", default="draft")
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
    supabase_url, supabase_key = load_supabase_credentials(aws_kwargs, env)

    keys = upload_slides(
        s3, slides, template_id, args.s3_key_template, env["s3_bucket"], dry_run
    )
    result = insert_template(supabase_url, supabase_key, payload, dry_run)

    safe_output = {
        "mode": "dry-run" if dry_run else "executed",
        "environment": args.environment,
        "templateId": template_id,
        "name": payload["name"],
        "slides": len(slides),
        "s3Bucket": env["s3_bucket"],
        "s3Keys": keys,
        "supabasePayload": payload if dry_run else {"inserted": True, "result": result},
        "contextSource": context.get("_sourcePath") if context else None,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(safe_output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
