#!/usr/bin/env python3
"""Convert a PNG file to a base64 data URL string for inline use in HTML.

Used to (re)generate placeholder strings that the gp2-html-designer skill
embeds directly into template.html — applies to any placeholder asset:
professional photos, brand logos, generic image fillers, etc.

Usage:
    python generate-placeholder-base64.py \\
        --in /path/to/asset.png \\
        --out skills/gp2-html-designer/references/placeholders/asset.b64.txt

The output file contains a single line: data:image/png;base64,<base64 payload>
"""

from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--in', dest='input_path', required=True, help='Source PNG file')
    parser.add_argument('--out', dest='output_path', required=True, help='Destination .b64.txt file')
    args = parser.parse_args()

    src = Path(args.input_path)
    dst = Path(args.output_path)

    if not src.exists():
        print(f'error: input file not found: {src}', file=sys.stderr)
        return 1
    if src.suffix.lower() != '.png':
        print(f'warning: input is not a .png file ({src.suffix}); proceeding anyway', file=sys.stderr)

    payload = base64.b64encode(src.read_bytes()).decode('ascii')
    data_url = f'data:image/png;base64,{payload}'

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(data_url, encoding='ascii')

    print(f'wrote {dst} ({len(data_url):,} chars, source {src.stat().st_size:,} bytes)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
