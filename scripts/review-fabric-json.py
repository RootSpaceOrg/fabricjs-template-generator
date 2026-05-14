#!/usr/bin/env python3
"""Lightweight Fabric JSON result reviewer for GetPosts templates.

This script audits generated slide-N.json files for geometry/metadata risks that often
cause HTML → Fabric visual drift. It does not render pixels; it is a deterministic
pre-upload reviewer. When review-manifest.json with expected boxes is present, it also
compares expected vs actual boxes by reviewId.

When HTML/product render images are available, it can also run a pixel-level visual
export review. PNG and JPEG are both accepted. The comparison uses ffmpeg to normalize
images to raw RGB bytes, so it does not require Pillow/canvas/pngjs.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

POSITION_TOL = 8
SIZE_TOL = 10
FONT_TOL = 2
SUPPORTED_IMAGE_EXTS = ('.png', '.jpg', '.jpeg')
GENERIC_NAME_RE = re.compile(r'^(?:s\d+[-_]obj[-_]\d+(?:[-_]text)?|object\s*\d+|layer\s*\d+|textbox\s*\d+|rect\s*\d+|image\s*\d+)$', re.I)
TECHNICAL_NAME_RE = re.compile(r'\bs\d+[-_]obj[-_]\d+|\btext[-_]text\b', re.I)
SLIDE_PREFIX_RE = re.compile(r'^\s*slide\s*\d+\s*[—\-:]\s*', re.I)
THEME_SPECIFIC_DESCRIPTION_RE = re.compile(
    r'\b(laserterapia|laser|joelho|paciente|cl[ií]nica|cl[ií]nico|sa[uú]de|consulta|consult[oó]rio|tratamento|terapia|premium|nicho|tema|foco\s+em|tom\s+premium)\b',
    re.I,
)


def issue(level: str, slide: str, obj: str, msg: str) -> dict[str, str]:
    return {"level": level, "slide": slide, "object": obj, "message": msg}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def normalize_text(value: Any) -> str:
    return re.sub(r'\s+', ' ', str(value or '')).strip()


def parse_solid_color(value: Any) -> tuple[int, int, int, float] | None:
    """Parse simple solid CSS/Fabric colors for semantic redundancy checks."""
    if not isinstance(value, str):
        return None
    v = value.strip().lower()
    if not v or 'gradient' in v:
        return None
    m = re.fullmatch(r'#([0-9a-f]{3}|[0-9a-f]{6})', v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
    m = re.fullmatch(r'rgba?\(([^)]+)\)', v)
    if m:
        parts = [p.strip() for p in m.group(1).split(',')]
        if len(parts) in {3, 4}:
            try:
                r, g, b = [int(float(parts[i])) for i in range(3)]
                a = float(parts[3]) if len(parts) == 4 else 1.0
                return (r, g, b, a)
            except ValueError:
                return None
    named = {
        'white': (255, 255, 255, 1.0),
        'black': (0, 0, 0, 1.0),
        'transparent': (0, 0, 0, 0.0),
    }
    return named.get(v)


def same_solid_color(a: Any, b: Any, tol: int = 2) -> bool:
    ca = parse_solid_color(a)
    cb = parse_solid_color(b)
    if not ca or not cb:
        return False
    if abs(ca[3] - cb[3]) > 0.01:
        return False
    return all(abs(ca[i] - cb[i]) <= tol for i in range(3))


def valid_variable_config(cfg: Any) -> bool:
    return (
        isinstance(cfg, dict)
        and cfg.get('type') == 'solid'
        and cfg.get('variable') in {'primary', 'secondary'}
        and isinstance(cfg.get('alpha'), (int, float))
        and 0 <= float(cfg.get('alpha')) <= 1
    )


def has_variable_config(value: Any, variable: str, target: str = 'fill') -> bool:
    key = f'{target}VariableConfig'
    if isinstance(value, dict):
        cfg = value.get(key)
        if isinstance(cfg, dict) and cfg.get('variable') == variable and valid_variable_config(cfg):
            return True
        return any(has_variable_config(v, variable, target) for v in value.values())
    if isinstance(value, list):
        return any(has_variable_config(v, variable, target) for v in value)
    return False


class HtmlReviewNode:
    def __init__(self, tag: str, attrs: dict[str, str], line: int, slide: int, parent_review_id: str | None):
        self.tag = tag
        self.attrs = attrs
        self.line = line
        self.slide = slide
        self.review_id = attrs.get('data-review-id')
        self.parent_review_id = parent_review_id
        self.text = ''


class ReviewHtmlParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes: list[HtmlReviewNode] = []
        self.stack: list[HtmlReviewNode] = []
        self.slide = 0

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]):
        attrs = {k: (v or '') for k, v in attrs_list}
        klass = attrs.get('class', '')
        if tag == 'section' and 'slide' in klass:
            self.slide += 1
        parent_review_id = next((n.review_id for n in reversed(self.stack) if n.review_id), None)
        node = HtmlReviewNode(tag, attrs, self.getpos()[0], self.slide, parent_review_id)
        self.nodes.append(node)
        if tag not in {'img', 'meta', 'link', 'br', 'hr', 'input'}:
            self.stack.append(node)

    def handle_endtag(self, tag: str):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data: str):
        for node in self.stack:
            node.text += data


def parse_source_html(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {'byReviewId': {}, 'childTextRuns': {}}
    parser = ReviewHtmlParser()
    parser.feed(path.read_text(encoding='utf-8'))
    by_id: dict[str, dict[str, Any]] = {}
    child_runs: dict[str, list[dict[str, Any]]] = {}
    text_tags = {'h1', 'h2', 'h3', 'h4', 'p', 'span', 'strong', 'em', 'div'}
    for n in parser.nodes:
        text = normalize_text(n.text)
        meta = {
            'tag': n.tag,
            'line': n.line,
            'slide': n.slide,
            'text': text,
            'parentReviewId': n.parent_review_id,
            'hasInlineStyle': bool(n.attrs.get('style')),
            'hasVariable': bool(n.attrs.get('data-variable')),
            'variable': n.attrs.get('data-variable'),
            'variableTarget': n.attrs.get('data-variable-target') or 'fill',
        }
        if n.review_id:
            by_id[n.review_id] = meta
        # Inline text runs do not need their own data-review-id. Claude Design's
        # contract says spans inside a text element become Fabric textbox.styles
        # ranges, not separate objects. Track them even without review ids.
        if n.parent_review_id and n.tag in text_tags and text:
            run_id = n.review_id or f'{n.parent_review_id}::inline-{n.tag}-{n.line}'
            child_runs.setdefault(n.parent_review_id, []).append(meta | {'reviewId': run_id, 'hasOwnReviewId': bool(n.review_id)})
    return {'byReviewId': by_id, 'childTextRuns': child_runs}


def find_output(path: Path) -> Path:
    if (path / 'output').exists():
        return path / 'output'
    return path


def slide_files(folder: Path) -> list[Path]:
    files = sorted(folder.glob('slide-*.json'), key=lambda p: int(p.stem.split('-')[-1]))
    if not files:
        raise SystemExit(f'No slide-N.json files found in {folder}')
    return files


def natural_slide_key(path: Path) -> int:
    m = re.search(r'(?:slide-|slide_)?(\d+)', path.stem, re.I)
    return int(m.group(1)) if m else 10**9


def image_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGE_EXTS],
        key=lambda p: (natural_slide_key(p), p.name),
    )


def find_visual_dirs(root: Path, html_dir: str | None, product_dir: str | None) -> tuple[Path | None, Path | None]:
    html = Path(html_dir).resolve() if html_dir else root / 'review' / 'html'
    product = Path(product_dir).resolve() if product_dir else root / 'review' / 'product'
    return (html if html.exists() else None, product if product.exists() else None)


def ffprobe_size(path: Path) -> tuple[int, int]:
    cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', str(path)
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    w, h = out.split('x')
    return int(w), int(h)


def ffmpeg_raw_rgb(path: Path, width: int, height: int) -> bytes:
    vf = f'scale={width}:{height}:flags=lanczos,format=rgb24'
    cmd = ['ffmpeg', '-v', 'error', '-i', str(path), '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    return subprocess.check_output(cmd)


def write_diff_png(diff_rgb: bytes, width: int, height: int, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        'ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{width}x{height}', '-i', '-', str(out_path)
    ]
    subprocess.run(cmd, input=diff_rgb, check=True)


def compare_images(
    html_img: Path,
    product_img: Path,
    diff_path: Path,
    warn_mae: float,
    fail_mae: float,
    warn_pct: float,
    fail_pct: float,
) -> dict[str, Any]:
    width, height = ffprobe_size(html_img)
    product_width, product_height = ffprobe_size(product_img)
    a = ffmpeg_raw_rgb(html_img, width, height)
    b = ffmpeg_raw_rgb(product_img, width, height)
    if len(a) != len(b):
        raise RuntimeError(f'normalized byte length mismatch: {html_img} vs {product_img}')

    total_abs = 0
    total_sq = 0
    max_delta = 0
    changed_pixels = 0
    px_count = width * height
    diff = bytearray(len(a))
    for i in range(0, len(a), 3):
        dr = abs(a[i] - b[i])
        dg = abs(a[i + 1] - b[i + 1])
        db = abs(a[i + 2] - b[i + 2])
        d = max(dr, dg, db)
        total_abs += dr + dg + db
        total_sq += dr * dr + dg * dg + db * db
        max_delta = max(max_delta, d)
        if d > 30:
            changed_pixels += 1
        # Amplified magenta/cyan-ish diff over white background for quick inspection.
        amp = min(255, d * 4)
        diff[i] = amp
        diff[i + 1] = max(0, 255 - amp)
        diff[i + 2] = amp
    mae = total_abs / len(a)
    rmse = math.sqrt(total_sq / len(a))
    changed_pct = changed_pixels * 100 / px_count
    write_diff_png(bytes(diff), width, height, diff_path)

    level = 'pass'
    if mae >= fail_mae or changed_pct >= fail_pct:
        level = 'fail'
    elif mae >= warn_mae or changed_pct >= warn_pct or (product_width, product_height) != (width, height):
        level = 'warning'
    return {
        'html': str(html_img),
        'product': str(product_img),
        'diff': str(diff_path),
        'width': width,
        'height': height,
        'productWidth': product_width,
        'productHeight': product_height,
        'mae': round(mae, 4),
        'rmse': round(rmse, 4),
        'changedPixelsPct': round(changed_pct, 4),
        'maxDelta': max_delta,
        'level': level,
    }


def review_visual_exports(root: Path, html_dir: str | None, product_dir: str | None, args: argparse.Namespace) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    issues: list[dict[str, str]] = []
    results: list[dict[str, Any]] = []
    html_path, product_path = find_visual_dirs(root, html_dir, product_dir)
    if not html_path or not product_path:
        if args.visual_required:
            missing = []
            if not html_path:
                missing.append(str(Path(html_dir).resolve() if html_dir else root / 'review' / 'html'))
            if not product_path:
                missing.append(str(Path(product_dir).resolve() if product_dir else root / 'review' / 'product'))
            issues.append(issue('critical', 'visual', 'exports', f'visual review required but missing image folder(s): {", ".join(missing)}'))
        return issues, results

    if shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None:
        issues.append(issue('critical', 'visual', 'ffmpeg', 'ffmpeg/ffprobe required for PNG/JPEG visual comparison'))
        return issues, results

    html_images = image_files(html_path)
    product_images = image_files(product_path)
    if not html_images or not product_images:
        issues.append(issue('critical' if args.visual_required else 'warning', 'visual', 'exports', 'visual folders exist but contain no PNG/JPEG slide images'))
        return issues, results
    if len(html_images) != len(product_images):
        issues.append(issue('critical', 'visual', 'slide-count', f'HTML/product image count mismatch: {len(html_images)} vs {len(product_images)}'))

    diff_dir = root / 'review' / 'diff'
    for idx, (html_img, product_img) in enumerate(zip(html_images, product_images), start=1):
        diff_path = diff_dir / f'slide-{idx}.png'
        try:
            result = compare_images(
                html_img,
                product_img,
                diff_path,
                args.visual_warn_mae,
                args.visual_fail_mae,
                args.visual_warn_pct,
                args.visual_fail_pct,
            )
        except Exception as exc:
            issues.append(issue('critical', f'slide-{idx}', 'visual', f'visual comparison failed: {exc}'))
            continue
        results.append(result)
        if (result['productWidth'], result['productHeight']) != (result['width'], result['height']):
            issues.append(issue('warning', f'slide-{idx}', 'visual-dimensions', f'product export dimensions {result["productWidth"]}x{result["productHeight"]} differ from HTML {result["width"]}x{result["height"]}; comparison was normalized'))
        if result['level'] == 'fail':
            issues.append(issue('critical', f'slide-{idx}', 'visual-drift', f'pixel drift above fail threshold: MAE={result["mae"]}, changed>{30}={result["changedPixelsPct"]}%'))
        elif result['level'] == 'warning':
            issues.append(issue('warning', f'slide-{idx}', 'visual-drift', f'pixel drift above warning threshold: MAE={result["mae"]}, changed>{30}={result["changedPixelsPct"]}%'))
    return issues, results


def fabric_box(obj: dict[str, Any]) -> dict[str, float] | None:
    left = obj.get('left'); top = obj.get('top')
    width = obj.get('width'); height = obj.get('height')
    if not all(isinstance(v, (int, float)) for v in [left, top, width]):
        return None
    if not isinstance(height, (int, float)):
        # Textbox often lacks height. Estimate for review only.
        if obj.get('type') == 'textbox':
            text = str(obj.get('text') or '')
            lines = max(1, text.count('\n') + 1)
            font = float(obj.get('fontSize') or 32)
            lh = float(obj.get('lineHeight') or 1.2)
            height = lines * font * lh
        else:
            return None
    return {
        'left': float(left) - float(width) / 2,
        'top': float(top) - float(height) / 2,
        'width': float(width),
        'height': float(height),
        'centerLeft': float(left),
        'centerTop': float(top),
    }


def overlap_ratio(a: dict[str, float] | None, b: dict[str, float] | None) -> float:
    if not a or not b:
        return 0.0
    ax2 = a['left'] + a['width']; ay2 = a['top'] + a['height']
    bx2 = b['left'] + b['width']; by2 = b['top'] + b['height']
    iw = max(0.0, min(ax2, bx2) - max(a['left'], b['left']))
    ih = max(0.0, min(ay2, by2) - max(a['top'], b['top']))
    inter = iw * ih
    small = max(1.0, min(a['width'] * a['height'], b['width'] * b['height']))
    return inter / small


def is_decorative_text(text: str) -> bool:
    t = normalize_text(text)
    return t in {'✓', '✔', '→', '•'} or bool(re.fullmatch(r'\d{1,2}', t))


def is_theme_specific_description(text: Any) -> bool:
    return bool(THEME_SPECIFIC_DESCRIPTION_RE.search(normalize_text(text)))


def base_review_id(value: Any) -> str:
    rid = str(value or '')
    return rid[:-5] if rid.endswith('-text') else rid


def review_object_semantics(path: Path, data: dict[str, Any], objects: list[dict[str, Any]], html_info: dict[str, Any] | None, issues: list[dict[str, str]]) -> None:
    """Review whether emitted Fabric objects make semantic/layer sense.

    This catches valid-but-bad conversions, especially splitting inline HTML spans
    into independent textboxes instead of one textbox with Fabric styles ranges.
    """
    textboxes = [o for o in objects if o.get('type') == 'textbox']
    by_review_id = {o.get('reviewId'): o for o in objects if o.get('reviewId')}
    for o in objects:
        rid = o.get('reviewId')
        if isinstance(rid, str) and rid.endswith('-text'):
            by_review_id.setdefault(rid[:-5], o)
    slide_match = re.search(r'slide-(\d+)', path.name)
    slide_no = int(slide_match.group(1)) if slide_match else None
    canvas_w = data.get('width') or data.get('canvasWidth') or 1080
    canvas_h = data.get('height') or data.get('canvasHeight') or 1350
    canvas_bg = data.get('background') or data.get('backgroundColor')
    child_pairs: set[tuple[str, str]] = set()
    if html_info:
        by_html_id = html_info.get('byReviewId') or {}
        # Every HTML data-variable must survive as Fabric variable metadata. This is
        # essential for user brand adaptation in the editor.
        for rid, meta in by_html_id.items():
            variable = meta.get('variable')
            if not variable:
                continue
            if slide_no and meta.get('slide') != slide_no:
                continue
            target = meta.get('variableTarget') or 'fill'
            parent_id = meta.get('parentReviewId')
            obj = by_review_id.get(rid)
            parent_obj = by_review_id.get(parent_id) if parent_id else None
            if parent_obj and meta.get('tag') in {'span', 'strong', 'em'}:
                if not has_variable_config(parent_obj.get('styles') or {}, variable, target):
                    issues.append(issue(
                        'critical',
                        path.name,
                        f'{parent_id} / {rid}',
                        f'HTML inline color variable {variable!r} was not mapped into Fabric textbox.styles as {target}VariableConfig.',
                    ))
            elif obj:
                fabric_target = 'fill' if target == 'background' and obj.get('type') != 'canvas' else target
                if not has_variable_config(obj, variable, fabric_target):
                    issues.append(issue(
                        'critical',
                        path.name,
                        rid,
                        f'HTML data-variable={variable!r} target={target!r} missing Fabric {fabric_target}VariableConfig on the matching object.',
                    ))
            elif target == 'background' and has_variable_config(data, variable, 'background'):
                pass
            else:
                issues.append(issue(
                    'critical',
                    path.name,
                    rid,
                    f'HTML data-variable={variable!r} target={target!r} has no matching Fabric object or root variable config.',
                ))
        for parent_id, runs in (html_info.get('childTextRuns') or {}).items():
            parent_meta = by_html_id.get(parent_id) or {}
            if slide_no and parent_meta.get('slide') != slide_no:
                continue
            for run in runs:
                child_pairs.add((parent_id, str(run.get('reviewId') or '')))

    for obj in objects:
        name = normalize_text(obj.get('name'))
        oid = obj.get('reviewId') or name or '<unnamed>'
        if not name:
            continue
        if SLIDE_PREFIX_RE.search(name):
            issues.append(issue('critical', path.name, oid, 'layer name must not include redundant slide prefix like “Slide 1 —”. Use only the semantic object role.'))
        # Layer names should be human-reviewable, not only converter internals.
        semantic_suffix = name.split('—', 1)[1].strip() if '—' in name else ''
        if GENERIC_NAME_RE.match(name) or (not semantic_suffix and TECHNICAL_NAME_RE.search(name)):
            issues.append(issue('warning', path.name, oid, 'layer name is generic/technical; use a semantic Portuguese name'))
        elif semantic_suffix and len(semantic_suffix) < 6:
            issues.append(issue('warning', path.name, oid, 'layer name has a semantic suffix but it is too vague/short'))

        opacity = obj.get('opacity', 1)
        if isinstance(opacity, (int, float)) and opacity <= 0.01:
            issues.append(issue('warning', path.name, oid, 'object is effectively invisible; remove unless intentionally hidden'))
        if obj.get('type') == 'textbox':
            txt = normalize_text(obj.get('text'))
            if not txt:
                issues.append(issue('critical', path.name, oid, 'empty textbox should not be emitted'))
            if is_decorative_text(txt) and not obj.get('textType') and not obj.get('isTemplateElement'):
                issues.append(issue('warning', path.name, oid, f'decorative text {txt!r} may be better as static icon/shape or clearly named static layer'))
        for key in ['fillVariableConfig', 'strokeVariableConfig', 'backgroundVariableConfig']:
            if key in obj and not valid_variable_config(obj.get(key)):
                issues.append(issue('critical', path.name, oid, f'{key} must be {{type:"solid", variable:"primary|secondary", alpha:0..1}}'))
        if obj.get('isTemplateElement'):
            desc = (obj.get('templateElement') or {}).get('description')
            if not desc:
                issues.append(issue('critical', path.name, oid, 'template element missing generic templateElement.description'))
            elif is_theme_specific_description(desc):
                issues.append(issue(
                    'critical',
                    path.name,
                    oid,
                    f'templateElement.description is theme/style-specific: {desc!r}. Use a clear generic role description that works for any theme.',
                ))
        if obj.get('type') in {'roundedRect', 'rect'}:
            box = fabric_box(obj)
            fill = obj.get('fill')
            opacity = obj.get('opacity', 1)
            covers_canvas = False
            if box and isinstance(canvas_w, (int, float)) and isinstance(canvas_h, (int, float)):
                covers_canvas = (
                    box['left'] <= 2 and box['top'] <= 2 and
                    box['width'] >= float(canvas_w) - 4 and box['height'] >= float(canvas_h) - 4
                )
            if covers_canvas and isinstance(opacity, (int, float)) and opacity >= 0.99 and same_solid_color(fill, canvas_bg):
                issues.append(issue(
                    'critical',
                    path.name,
                    oid,
                    'redundant full-canvas background object: fill matches canvas background. Remove this layer and keep the color only on the Fabric canvas background.',
                ))

    # Duplicate/subset textboxes: common symptom of HTML span → extra Fabric textbox.
    for i, a in enumerate(textboxes):
        ta = normalize_text(a.get('text'))
        if len(ta) < 3 or is_decorative_text(ta):
            continue
        box_a = fabric_box(a)
        for b in textboxes[i + 1:]:
            tb = normalize_text(b.get('text'))
            if len(tb) < 3 or is_decorative_text(tb) or ta == tb:
                continue
            longer, shorter = (a, b) if len(ta) >= len(tb) else (b, a)
            long_text, short_text = (ta, tb) if len(ta) >= len(tb) else (tb, ta)
            pair = (base_review_id(longer.get('reviewId')), base_review_id(shorter.get('reviewId')))
            if pair in child_pairs:
                continue
            if short_text in long_text and overlap_ratio(fabric_box(longer), fabric_box(shorter)) > 0.35:
                issues.append(issue(
                    'critical',
                    path.name,
                    f'{longer.get("reviewId") or longer.get("name")} / {shorter.get("reviewId") or shorter.get("name")}',
                    f'redundant split textbox: {short_text!r} is already inside {long_text!r}; inline span styling must be represented in one textbox.styles range, not a second textbox',
                ))

    if not html_info:
        return
    child_runs = html_info.get('childTextRuns') or {}
    by_html_id = html_info.get('byReviewId') or {}
    for parent_id, runs in child_runs.items():
        parent_meta = by_html_id.get(parent_id) or {}
        if slide_no and parent_meta.get('slide') != slide_no:
            continue
        parent_obj = by_review_id.get(parent_id)
        if not parent_obj or parent_obj.get('type') != 'textbox':
            continue
        parent_text = normalize_text(parent_obj.get('text'))
        parent_styles = parent_obj.get('styles') or {}
        for run in runs:
            rid = run.get('reviewId')
            run_text = normalize_text(run.get('text'))
            if not run_text or run_text not in parent_text:
                continue
            child_obj = by_review_id.get(rid)
            if child_obj and child_obj.get('type') == 'textbox':
                issues.append(issue(
                    'critical',
                    path.name,
                    f'{parent_id} / {rid}',
                    f'HTML inline text run {rid} ({run_text!r}) became a separate textbox. Keep a single textbox {parent_id!r} and encode the span color/weight in Fabric textbox.styles.',
                ))
            elif run.get('variable') and not has_variable_config(parent_styles, str(run.get('variable')), str(run.get('variableTarget') or 'fill')):
                issues.append(issue(
                    'critical',
                    path.name,
                    parent_id,
                    f'HTML inline variable run {rid} ({run_text!r}) missing Fabric styles {run.get("variableTarget") or "fill"}VariableConfig for {run.get("variable")!r}.',
                ))
            elif (run.get('hasInlineStyle') or run.get('hasVariable')) and not parent_styles:
                issues.append(issue(
                    'warning',
                    path.name,
                    parent_id,
                    f'HTML inline styled run {rid} ({run_text!r}) appears merged but parent textbox has empty styles; verify Fabric styles preserve span color/weight.',
                ))

    # Missing or extra review ids for HTML-bearing objects.
    for rid, meta in by_html_id.items():
        if slide_no and meta.get('slide') != slide_no:
            continue
        if meta.get('tag') not in {'h1', 'h2', 'h3', 'h4', 'p', 'span', 'strong', 'em'}:
            continue
        if meta.get('text') and rid not in by_review_id:
            parent_id = meta.get('parentReviewId')
            parent = by_review_id.get(parent_id) if parent_id else None
            if parent and normalize_text(meta.get('text')) in normalize_text(parent.get('text')):
                continue  # child inline run may be represented by parent styles
            issues.append(issue('warning', path.name, rid, 'HTML data-review-id with text has no matching Fabric object; verify it was intentionally merged or dropped'))


def compare_expected(slide_name: str, objects: list[dict[str, Any]], expected: dict[str, Any], issues: list[dict[str, str]]):
    by_id = {o.get('reviewId'): o for o in objects if o.get('reviewId')}
    for rid, exp in expected.items():
        obj = by_id.get(rid)
        if not obj:
            issues.append(issue('critical', slide_name, rid, 'expected reviewId missing from Fabric JSON'))
            continue
        box = fabric_box(obj)
        if not box:
            issues.append(issue('warning', slide_name, rid, 'cannot compute Fabric box for comparison'))
            continue
        for key in ['left', 'top', 'width', 'height']:
            if key not in exp:
                continue
            delta = box[key] - float(exp[key])
            tol = POSITION_TOL if key in ['left', 'top'] else max(SIZE_TOL, abs(float(exp[key])) * 0.02)
            if abs(delta) > tol:
                level = 'critical' if abs(delta) > tol * 2 else 'warning'
                issues.append(issue(level, slide_name, rid, f'{key} drift: expected {exp[key]}, got {round(box[key],2)} ({round(delta,2)} px)'))
        if obj.get('type') == 'textbox':
            for key in ['fontSize', 'lineHeight']:
                if key in exp and isinstance(obj.get(key), (int, float)):
                    delta = float(obj[key]) - float(exp[key])
                    tol = FONT_TOL if key == 'fontSize' else 0.05
                    if abs(delta) > tol:
                        issues.append(issue('warning', slide_name, rid, f'{key} drift: expected {exp[key]}, got {obj[key]} ({round(delta,2)})'))


def check_clippable_image_geometry(slide_name: str, name: str, obj: dict[str, Any], issues: list[dict[str, str]]) -> None:
    """Catch the most common cutout-vs-cover misemission for ClippableImage.

    For professionalPhoto cutouts (object-fit: contain) the converter must:
      - set originWidth/Height to the SOURCE PNG's natural size (not the slot)
      - leave cropX/cropY at 0 and width === originWidth, height === originHeight
        (because contain has NO crop)
      - use originY in {"top","bottom"} when object-position dictates an anchor

    For cropped images (object-fit: cover, border-radius, data-image-crop) the
    width/height represent the crop on the source — typically smaller than
    originWidth/Height and with non-zero cropX or cropY.

    The cheap check we run here: when the object is flagged as cutout-style
    (imageType professionalPhoto + cropX/cropY both 0), require width === originWidth
    and height === originHeight. If they diverge, the converter likely treated the
    slot as the frame (the bug observed in production), which produces the symptom
    'figure renders ~half the slot, anchored to the top'.
    """
    image_type = obj.get('imageType')
    crop_x = obj.get('cropX')
    crop_y = obj.get('cropY')
    width = obj.get('width')
    height = obj.get('height')
    origin_w = obj.get('originWidth')
    origin_h = obj.get('originHeight')

    # Numeric guard
    nums = [width, height, origin_w, origin_h]
    if not all(isinstance(v, (int, float)) for v in nums):
        return

    # Heuristic: cutout = no crop applied
    looks_like_cutout = (
        image_type == 'professionalPhoto'
        and isinstance(crop_x, (int, float)) and crop_x == 0
        and isinstance(crop_y, (int, float)) and crop_y == 0
    )
    if looks_like_cutout:
        # In contain (cutout) the frame IS the natural image — width must equal originWidth.
        if abs(width - origin_w) > 0.5 or abs(height - origin_h) > 0.5:
            issues.append(issue(
                'critical', slide_name, name,
                f'ClippableImage cutout mismatch: width/height ({width}x{height}) must equal '
                f'originWidth/originHeight ({origin_w}x{origin_h}) when cropX/Y=0. '
                f'Likely cause: converter treated the HTML slot as the frame instead of the PNG natural size. '
                f'Fix: read naturalWidth/naturalHeight of the source PNG and use those for both '
                f'width/height and originWidth/originHeight; position via scaleX/scaleY + originY.'
            ))
        # originY must reflect object-position; "center" with bottom-anchored placements is a smell
        # but only a warning — the runtime swap with anchor:'bottom-center' will still center the
        # user's photo correctly, just not match the placeholder render exactly.
        if obj.get('originY') == 'center':
            issues.append(issue(
                'warning', slide_name, name,
                'ClippableImage cutout uses originY:"center"; if HTML had object-position:"bottom*", '
                'emit originY:"bottom" so placeholder render matches the runtime bottom-center anchor.'
            ))

    # Catch obvious cover bugs too: if cropX/Y are 0 but width !== originWidth on a non-cutout image,
    # something is off (cover with cropX=0 means the crop window starts at the source edge).
    elif (
        isinstance(crop_x, (int, float)) and crop_x == 0
        and isinstance(crop_y, (int, float)) and crop_y == 0
        and (abs(width - origin_w) > 0.5 or abs(height - origin_h) > 0.5)
    ):
        issues.append(issue(
            'warning', slide_name, name,
            f'ClippableImage with cropX/Y=0 but width/height ({width}x{height}) != '
            f'originWidth/Height ({origin_w}x{origin_h}). For cover crops, cropX or cropY '
            f'should be non-zero to recenter. Verify the HTML used object-fit:cover not contain.'
        ))


def review_slide(path: Path, expected_slide: dict[str, Any] | None, html_info: dict[str, Any] | None = None) -> tuple[list[dict[str, str]], dict[str, int]]:
    data = load_json(path)
    issues: list[dict[str, str]] = []
    objects = data.get('objects') or []
    stats = {'objects': len(objects), 'reviewIds': 0, 'templateElements': 0}

    if data.get('version') != '5.5.2':
        issues.append(issue('critical', path.name, 'root', f'version must be 5.5.2, got {data.get("version")}'))
    if data.get('backgroundVariableConfig') and not valid_variable_config(data.get('backgroundVariableConfig')):
        issues.append(issue('critical', path.name, 'root', 'backgroundVariableConfig must be {type:"solid", variable:"primary|secondary", alpha:0..1}'))
    if not isinstance(objects, list):
        issues.append(issue('critical', path.name, 'root', 'objects must be an array'))
        return issues, stats

    seen_names = set()
    for idx, obj in enumerate(objects):
        name = obj.get('name') or f'objects[{idx}]'
        if obj.get('reviewId'):
            stats['reviewIds'] += 1
        if obj.get('isTemplateElement') is True:
            stats['templateElements'] += 1
        if not obj.get('name'):
            issues.append(issue('critical', path.name, name, 'missing object name'))
        if name in seen_names:
            issues.append(issue('warning', path.name, name, 'duplicate object name makes review harder; prefer unique names/reviewId'))
        seen_names.add(name)
        # Origin rule: most objects must be center/center.
        # Exception: ClippableImage cutout (object-fit: contain) honours object-position
        # via originY in {"top","bottom","center"} and originX in {"left","right","center"}.
        # The runtime image-variable.ts:117-121 understands these anchors.
        if obj.get('type') == 'ClippableImage':
            if obj.get('originX') not in ('left', 'center', 'right'):
                issues.append(issue('critical', path.name, name, f'ClippableImage originX must be left|center|right, got {obj.get("originX")!r}'))
            if obj.get('originY') not in ('top', 'center', 'bottom'):
                issues.append(issue('critical', path.name, name, f'ClippableImage originY must be top|center|bottom, got {obj.get("originY")!r}'))
        else:
            if obj.get('originX') != 'center' or obj.get('originY') != 'center':
                issues.append(issue('critical', path.name, name, 'origin must be center/center'))
        if obj.get('type') == 'textbox':
            if 'styles' not in obj:
                issues.append(issue('critical', path.name, name, 'textbox missing styles'))
            if not isinstance(obj.get('fontSize'), (int, float)):
                issues.append(issue('critical', path.name, name, 'textbox missing numeric fontSize'))
            if isinstance(obj.get('lineHeight'), (int, float)) and obj['lineHeight'] < 1:
                issues.append(issue('critical', path.name, name, 'lineHeight below 1.0'))
            if isinstance(obj.get('charSpacing'), (int, float)) and obj['charSpacing'] < -150:
                issues.append(issue('critical', path.name, name, 'charSpacing below -150'))
            if obj.get('isTemplateElement') and not obj.get('templateElement', {}).get('description'):
                issues.append(issue('critical', path.name, name, 'template textbox missing templateElement.description'))
            if obj.get('textType') and obj.get('isTemplateElement'):
                issues.append(issue('critical', path.name, name, 'textType and isTemplateElement are mutually exclusive'))
        if obj.get('type') == 'ClippableImage':
            for field in ['src', 'originWidth', 'originHeight', 'cropX', 'cropY', 'imageType']:
                if field not in obj:
                    issues.append(issue('critical', path.name, name, f'ClippableImage missing {field}'))
            check_clippable_image_geometry(path.name, name, obj, issues)
        box = fabric_box(obj)
        if obj.get('type') != 'textbox' and box is None:
            issues.append(issue('warning', path.name, name, 'cannot compute object box; width/height/left/top incomplete'))

    review_object_semantics(path, data, objects, html_info, issues)

    if expected_slide:
        compare_expected(path.name, objects, expected_slide.get('objects', {}), issues)
    else:
        important = [o for o in objects if o.get('isTemplateElement') or o.get('textType') or o.get('type') in ['textbox', 'ClippableImage', 'image']]
        missing_ids = [o.get('name', '<unnamed>') for o in important if not o.get('reviewId')]
        if missing_ids:
            issues.append(issue('warning', path.name, 'reviewId', f'{len(missing_ids)} important objects have no reviewId; geometry fidelity review is limited'))

    return issues, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('template_folder', help='Template artifact folder or output folder')
    ap.add_argument('--expected', help='Optional review-manifest.json with expected boxes by slide/reviewId')
    ap.add_argument('--source-html', help='Optional source/marked template.html for semantic reviewId/text-run audit; defaults to <template_folder>/template.html when present')
    ap.add_argument('--html-renders', help='Folder with source HTML slide renders; defaults to <template_folder>/review/html')
    ap.add_argument('--product-exports', help='Folder with real product/editor exports; defaults to <template_folder>/review/product')
    ap.add_argument('--visual', action='store_true', help='Run visual comparison when PNG/JPEG render folders are present')
    ap.add_argument('--visual-required', action='store_true', help='Fail if visual render/export folders are missing')
    ap.add_argument('--visual-warn-mae', type=float, default=8.0, help='Mean absolute pixel drift warning threshold')
    ap.add_argument('--visual-fail-mae', type=float, default=18.0, help='Mean absolute pixel drift fail threshold')
    ap.add_argument('--visual-warn-pct', type=float, default=5.0, help='Percent pixels with channel delta > 30 warning threshold')
    ap.add_argument('--visual-fail-pct', type=float, default=15.0, help='Percent pixels with channel delta > 30 fail threshold')
    args = ap.parse_args()

    root = Path(args.template_folder).resolve()
    output = find_output(root)
    expected = load_json(Path(args.expected)) if args.expected else None
    source_html = Path(args.source_html).resolve() if args.source_html else (root / 'template.html')
    html_info = parse_source_html(source_html if source_html.exists() else None)

    all_issues: list[dict[str, str]] = []
    total = {'objects': 0, 'reviewIds': 0, 'templateElements': 0}
    for sf in slide_files(output):
        exp_slide = None
        if expected:
            exp_slide = (expected.get('slides') or {}).get(sf.name)
        issues, stats = review_slide(sf, exp_slide, html_info)
        all_issues.extend(issues)
        for k, v in stats.items():
            total[k] += v

    visual_results: list[dict[str, Any]] = []
    if args.visual or args.visual_required or args.html_renders or args.product_exports:
        visual_issues, visual_results = review_visual_exports(root, args.html_renders, args.product_exports, args)
        all_issues.extend(visual_issues)

    critical = [i for i in all_issues if i['level'] == 'critical']
    warnings = [i for i in all_issues if i['level'] == 'warning']
    status = 'FAIL' if critical else ('PASS_WITH_WARNINGS' if warnings else 'PASS')

    report = {
        'status': status,
        'summary': {
            'slides': len(slide_files(output)),
            **total,
            'critical': len(critical),
            'warnings': len(warnings),
        },
        'issues': all_issues,
        'visualReview': {
            'enabled': bool(args.visual or args.visual_required or args.html_renders or args.product_exports),
            'accepts': list(SUPPORTED_IMAGE_EXTS),
            'thresholds': {
                'warnMae': args.visual_warn_mae,
                'failMae': args.visual_fail_mae,
                'warnChangedPixelsPct': args.visual_warn_pct,
                'failChangedPixelsPct': args.visual_fail_pct,
            },
            'results': visual_results,
        },
    }
    report_path = root / 'review-report.json' if root != output else output / 'review-report.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))

    md = [f'# Result Review — {root.name}', '', f'Status: {status}', '', '## Summary']
    for k, v in report['summary'].items():
        md.append(f'- {k}: {v}')
    md += ['', '## Issues']
    if all_issues:
        for i in all_issues:
            md.append(f"- [{i['level']}] {i['slide']} / {i['object']}: {i['message']}")
    else:
        md.append('- No issues found.')
    if visual_results:
        md += ['', '## Visual export review']
        for idx, v in enumerate(visual_results, start=1):
            md.append(f"- Slide {idx}: {v['level'].upper()} — MAE {v['mae']}, RMSE {v['rmse']}, changed pixels {v['changedPixelsPct']}%, diff `{v['diff']}`")
    md_path = report_path.with_suffix('.md')
    md_path.write_text('\n'.join(md))

    print(json.dumps({'status': status, 'report': str(report_path), 'markdown': str(md_path), 'summary': report['summary']}, ensure_ascii=False, indent=2))
    if status == 'FAIL':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
