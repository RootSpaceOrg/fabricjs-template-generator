#!/usr/bin/env python3
"""Generate an image with OpenAI (gpt-image-1) and optionally upload it to the
templates S3 bucket, printing the public URL to use as ClippableImage src.

Reuses ENV_CONFIG / assume_role from gp2-template-uploader's import-template.py.
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import os
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UPLOADER = REPO_ROOT / "skills" / "gp2-template-uploader" / "scripts" / "import-template.py"

OPENAI_URL = "https://api.openai.com/v1/images/generations"
VALID_SIZES = {"1024x1024", "1024x1536", "1536x1024"}


def load_uploader_module():
    spec = importlib.util.spec_from_file_location("gp2_uploader", UPLOADER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_api_key(key_file: str | None) -> str:
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    if key_file:
        text = Path(key_file).read_text().strip()
        # accept either a raw key or an env-style file with OPENAI_API_KEY=...
        for line in text.splitlines():
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
        return text
    sys.exit("No OpenAI key: set OPENAI_API_KEY or pass --key-file")


def generate(prompt: str, size: str, key: str) -> bytes:
    body = json.dumps(
        {"model": "gpt-image-1", "prompt": prompt, "size": size, "quality": "high"}
    ).encode()
    req = urllib.request.Request(
        OPENAI_URL,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.load(resp)
    return base64.b64decode(data["data"][0]["b64_json"])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", default=None, help="Pre-generated image (e.g. by the agent runtime); skips OpenAI")
    p.add_argument("--prompt", default=None, help="Fallback: generate via OpenAI gpt-image-1")
    p.add_argument("--size", default="1024x1536", choices=sorted(VALID_SIZES))
    p.add_argument("--out", default=None, help="Local PNG output path (required with --prompt)")
    p.add_argument("--key-file", default=None, help="File containing the OpenAI key")
    p.add_argument("--s3-key", default=None, help="S3 key; omit to skip upload")
    p.add_argument("--env", choices=["dev", "prod"], default="prod")
    p.add_argument(
        "--public-base",
        default=None,
        help="Public base URL for the bucket (CDN). Default: S3 virtual-host URL",
    )
    args = p.parse_args()

    if args.file:
        png = Path(args.file).read_bytes()
        print(f"local: {args.file} ({len(png)} bytes)")
    elif args.prompt:
        if not args.out:
            sys.exit("--out is required with --prompt")
        png = generate(args.prompt, args.size, get_api_key(args.key_file))
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(png)
        print(f"local: {out} ({len(png)} bytes)")
    else:
        sys.exit("Pass --file (pre-generated image) or --prompt (OpenAI fallback)")

    if not args.s3_key:
        return

    up = load_uploader_module()
    cfg = up.ENV_CONFIG[args.env]
    import boto3

    s3 = boto3.client("s3", region_name=cfg["aws_region"], **up.assume_role(cfg))
    content_types = {".png": "image/png", ".svg": "image/svg+xml", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
    ext = Path(args.s3_key).suffix.lower()
    s3.put_object(
        Bucket=cfg["s3_bucket"],
        Key=args.s3_key,
        Body=png,
        ContentType=content_types.get(ext, "image/png"),
        CacheControl="public, max-age=31536000, immutable",
    )
    base = args.public_base or (
        f"https://{cfg['s3_bucket']}.s3.{cfg['aws_region']}.amazonaws.com"
    )
    print(f"url: {base.rstrip('/')}/{args.s3_key}")


if __name__ == "__main__":
    main()
