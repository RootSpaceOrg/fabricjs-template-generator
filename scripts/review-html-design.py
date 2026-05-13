#!/usr/bin/env python3
"""Deterministic preflight for GetPosts HTML preview review.

Catches mechanical risks before visual judgment: missing slides, unsafe text,
edge issues, likely overlaps, unclear image/photo semantics, excessive noise,
and slide-to-slide composition discontinuity.
"""
from __future__ import annotations

import json
import base64
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

STYLE_RE = re.compile(r'([a-zA-Z-]+)\s*:\s*([^;]+)')
NUM_RE = re.compile(r'-?\d+(?:\.\d+)?')
TEXT_TAGS = {'p', 'span', 'h1', 'h2', 'h3', 'h4', 'button', 'a'}
CANVAS_TAGS = {'div', 'p', 'span', 'h1', 'h2', 'h3', 'h4', 'img', 'button', 'a', 'svg'}
IMPORTANT_ROLES = {'title', 'body', 'cta_or_label'}
IMPECCABLE_TIMEOUT_SECONDS = 90


def parse_style(style: str) -> dict[str, str]:
    return {m.group(1).strip().lower(): m.group(2).strip() for m in STYLE_RE.finditer(style or '')}


def px(value: str | None) -> float | None:
    if not value:
        return None
    m = NUM_RE.search(value)
    return float(m.group(0)) if m else None


def norm(text: str) -> str:
    return ' '.join((text or '').split())


def decode_svg_data_uri(src: str) -> str | None:
    if not src.startswith('data:image/svg+xml'):
        return None
    try:
        if ';base64,' in src:
            return base64.b64decode(src.split(';base64,', 1)[1], validate=False).decode('utf-8', errors='replace')
        if ',' in src:
            from urllib.parse import unquote
            return unquote(src.split(',', 1)[1])
    except Exception:
        return None
    return None


def placeholder_svg_complexity(svg: str) -> tuple[bool, str]:
    low = svg.lower()
    forbidden = []
    for tag in ['<text', '<filter', '<fedrop', '<image', '<foreignobject']:
        if tag in low:
            forbidden.append(tag.strip('<'))
    shape_count = len(re.findall(r'<(?:path|circle|ellipse|rect|polygon|polyline|line)\b', low))
    path_count = len(re.findall(r'<path\b', low))
    # A simple stripe placeholder is usually 1 rect + 1-3 paths/lines. More than
    # this starts pretending to be a final illustration and creates misleading previews.
    if forbidden:
        return True, f'contains forbidden placeholder SVG features: {", ".join(sorted(set(forbidden)))}'
    if shape_count > 5 or path_count > 3:
        return True, f'contains too many SVG parts for a simple placeholder ({shape_count} shapes, {path_count} paths)'
    return False, ''


@dataclass
class Issue:
    severity: str
    slide: int
    element: str
    message: str


class SlideParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slide = 0
        self.in_slide = False
        self.current: dict[str, Any] | None = None
        self.elements: list[dict[str, Any]] = []
        self.slide_counts: dict[int, int] = {}
        self.slide_dims: dict[int, tuple[float, float]] = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get('class', '')
        if tag == 'section' and 'slide' in cls.split():
            self.slide += 1
            self.in_slide = True
            self.slide_counts[self.slide] = 0
            self.slide_dims[self.slide] = (float(attrs.get('data-width') or 1080), float(attrs.get('data-height') or 1350))
            return
        if self.in_slide and tag in CANVAS_TAGS:
            style = parse_style(attrs.get('style', ''))
            elem = {
                'slide': self.slide,
                'tag': tag,
                'class': cls,
                'id': attrs.get('id') or '',
                'reviewId': attrs.get('data-review-id') or attrs.get('id') or '',
                'alt': attrs.get('alt') or '',
                'src': attrs.get('src') or '',
                'style': style,
                'text': '',
            }
            self.current = elem
            self.elements.append(elem)
            self.slide_counts[self.slide] += 1

    def handle_data(self, data):
        if self.current is not None:
            self.current['text'] += data

    def handle_endtag(self, tag):
        if tag == 'section' and self.in_slide:
            self.in_slide = False
        if self.current is not None and tag == self.current.get('tag'):
            self.current = None


def bbox(el: dict[str, Any]) -> tuple[float, float, float, float] | None:
    st = el['style']
    left, top = px(st.get('left')), px(st.get('top'))
    width, height = px(st.get('width')), px(st.get('height'))
    if None in (left, top, width, height):
        return None
    return (left, top, left + width, top + height)


def area(b: tuple[float, float, float, float]) -> float:
    return max(0, b[2] - b[0]) * max(0, b[3] - b[1])


def overlap(a, b) -> float:
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    return max(0, x2 - x1) * max(0, y2 - y1)


def center(b: tuple[float, float, float, float]) -> tuple[float, float]:
    return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)


def side_of(b: tuple[float, float, float, float], slide_w: float) -> str:
    cx, _ = center(b)
    if cx < slide_w * 0.42:
        return 'left'
    if cx > slide_w * 0.58:
        return 'right'
    return 'center'


def primary_for_role(els: list[dict[str, Any]], roles: set[str]) -> dict[str, Any] | None:
    candidates = [e for e in els if e.get('_role') in roles and bbox(e)]
    if not candidates:
        return None
    return max(candidates, key=lambda e: area(bbox(e) or (0, 0, 0, 0)))


def box_summary(el: dict[str, Any], slide_w: float) -> dict[str, Any] | None:
    b = bbox(el)
    if not b:
        return None
    return {
        'box': b,
        'side': side_of(b, slide_w),
        'width': b[2] - b[0],
        'height': b[3] - b[1],
        'cx': center(b)[0],
        'cy': center(b)[1],
    }


def is_full_bleed_background_image(el: dict[str, Any], slide_w: float, slide_h: float) -> bool:
    if el.get('tag') != 'img':
        return False
    cls = (el.get('class') or '').lower()
    b = bbox(el)
    if not b:
        return False
    covers_most = area(b) >= (slide_w * slide_h * 0.65)
    starts_near_origin = b[0] <= 8 and b[1] <= 8
    return covers_most and (starts_near_origin or 'cover' in cls or 'background' in cls)


def classify(el: dict[str, Any]) -> str:
    text = norm(el.get('text', ''))
    cls = (el.get('class') or '').lower()
    tag = el['tag']
    fs = px(el['style'].get('font-size'))
    if 'professional-photo' in cls or 'foto profissional' in (el.get('alt') or '').lower():
        return 'professional-photo'
    if tag == 'img':
        return 'image'
    if any(k in cls for k in ['cta', 'button']):
        return 'cta_or_label'
    if any(k in cls for k in ['decor', 'shape', 'chrome', 'background', 'divider']):
        return 'decor'
    if not text:
        return 'decor' if tag in {'div', 'svg'} else 'nontext'
    if tag in {'h1', 'h2'} or (fs and fs >= 42):
        return 'title'
    if len(text) <= 45 and fs and fs >= 26:
        return 'cta_or_label'
    return 'body'


def run_impeccable_detect(html: Path) -> tuple[list[Issue], list[dict[str, Any]]]:
    """Run Impeccable's deterministic anti-pattern detector as a mandatory gate.

    Any detector finding becomes a warning, which forces REVISE in this strict flow.
    If the detector cannot run, that is critical because the gate did not execute.
    """
    cmd = ['npx', '-y', 'impeccable', 'detect', str(html), '--json']
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=IMPECCABLE_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return [Issue('critical', 0, 'impeccable', f'Impeccable detect timed out after {IMPECCABLE_TIMEOUT_SECONDS}s; mandatory gate did not complete.')], []
    except FileNotFoundError:
        return [Issue('critical', 0, 'impeccable', 'npx not found; mandatory Impeccable gate cannot run.')], []

    stdout = (proc.stdout or '').strip()
    stderr = (proc.stderr or '').strip()
    output = stdout or stderr
    findings: list[dict[str, Any]] = []
    if output:
        candidate = output
        # npm/npx can prepend warnings; keep the JSON payload when possible.
        first_list = candidate.find('[')
        first_obj = candidate.find('{')
        starts = [i for i in [first_list, first_obj] if i >= 0]
        if starts:
            candidate = candidate[min(starts):]
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, list):
                findings = [f for f in parsed if isinstance(f, dict)]
            elif isinstance(parsed, dict):
                raw = parsed.get('findings') or parsed.get('issues') or []
                if isinstance(raw, list):
                    findings = [f for f in raw if isinstance(f, dict)]
        except json.JSONDecodeError:
            return [Issue('critical', 0, 'impeccable', f'Impeccable returned non-JSON output: {output[:240]}')], []

    # Impeccable exits non-zero when it finds issues. That is expected; no findings
    # with non-zero means the gate itself failed.
    if proc.returncode not in (0, 1, 2) and not findings:
        return [Issue('critical', 0, 'impeccable', f'Impeccable detect failed with exit {proc.returncode}: {output[:240]}')], []
    if proc.returncode != 0 and not findings:
        return [Issue('critical', 0, 'impeccable', f'Impeccable detect exited {proc.returncode} without parseable findings: {output[:240]}')], []

    issues: list[Issue] = []
    for idx, f in enumerate(findings, start=1):
        antipattern = str(f.get('antipattern') or f.get('rule') or f.get('id') or f'impeccable-{idx}')
        name = str(f.get('name') or antipattern)
        snippet = str(f.get('snippet') or f.get('description') or '').strip()
        msg = f'Impeccable: {name}' + (f' — {snippet}' if snippet else '')
        issues.append(Issue('warning', 0, f'impeccable:{antipattern}', msg))
    return issues, findings


def audit(artifact: Path) -> dict[str, Any]:
    html = artifact / 'template.html'
    if not html.exists():
        raise SystemExit(f'template.html not found: {html}')

    parser = SlideParser()
    parser.feed(html.read_text(encoding='utf-8', errors='replace'))
    issues: list[Issue] = []

    if parser.slide == 0:
        issues.append(Issue('critical', 0, 'document', 'No <section class="slide"> found.'))

    for slide, count in parser.slide_counts.items():
        if count < 4:
            issues.append(Issue('warning', slide, 'slide', f'Only {count} canvas-bound elements detected; check if slide is accidentally empty.'))
        if count > 90:
            issues.append(Issue('warning', slide, 'slide', f'{count} elements detected; likely too complex/noisy for later migration.'))

    by_slide: dict[int, list[dict[str, Any]]] = {}
    for idx, el in enumerate(parser.elements, start=1):
        el['_idx'] = idx
        el['_role'] = classify(el)
        sw, sh = parser.slide_dims.get(el['slide'], (1080, 1350))
        if is_full_bleed_background_image(el, sw, sh):
            el['_role'] = 'background-image'
        by_slide.setdefault(el['slide'], []).append(el)

        st = el['style']
        text = norm(el.get('text', ''))
        fs = px(st.get('font-size'))
        left, top = px(st.get('left')), px(st.get('top'))
        width, height = px(st.get('width')), px(st.get('height'))
        slide_w, slide_h = parser.slide_dims.get(el['slide'], (1080, 1350))
        eid = el.get('reviewId') or el.get('id') or f'{el["tag"]}#{idx}'
        role = el['_role']

        if el['tag'] in TEXT_TAGS and text:
            if role == 'title' and fs and fs < 42:
                issues.append(Issue('warning', el['slide'], eid, f'Title-like text font-size {fs}px is low.'))
            if role == 'body' and fs and fs < 26:
                issues.append(Issue('warning', el['slide'], eid, f'Body text font-size {fs}px may be too small.'))
            lh = st.get('line-height')
            if lh:
                val = px(lh)
                if val is not None and (('px' not in lh and val < 1.0) or ('px' in lh and fs and val < fs)):
                    issues.append(Issue('critical', el['slide'], eid, f'line-height {lh} risks clipping/overlap.'))
            if width and fs and len(text) > max(80, width / max(fs * 0.42, 1) * 2.8):
                issues.append(Issue('warning', el['slide'], eid, f'Text may be too long for box ({len(text)} chars, width {width}px).'))

        if left is not None and left < 32 and role in IMPORTANT_ROLES:
            issues.append(Issue('warning', el['slide'], eid, f'important element left {left}px is close to edge.'))
        if top is not None and top < 32 and role in IMPORTANT_ROLES:
            issues.append(Issue('warning', el['slide'], eid, f'important element top {top}px is close to edge.'))
        if left is not None and width is not None and left + width > slide_w - 32 and role in IMPORTANT_ROLES:
            issues.append(Issue('warning', el['slide'], eid, f'important element right edge {left+width:.0f}px is close/outside safe area.'))
        if top is not None and height is not None and top + height > slide_h - 32 and role in IMPORTANT_ROLES:
            issues.append(Issue('warning', el['slide'], eid, f'important element bottom edge {top+height:.0f}px is close/outside safe area.'))

        if el['tag'] == 'img':
            if not (el.get('alt') or '').strip():
                issues.append(Issue('warning', el['slide'], eid, 'Image lacks semantic alt; later role detection will be weaker.'))
            svg = decode_svg_data_uri(el.get('src') or '')
            if svg:
                complex_placeholder, reason = placeholder_svg_complexity(svg)
                if complex_placeholder:
                    issues.append(Issue('warning', el['slide'], eid, f'Image placeholder is too complex: {reason}. Use a plain diagonal/neutral pattern instead.'))
            if role == 'professional-photo':
                br = st.get('border-radius', '')
                if '50%' in br:
                    issues.append(Issue('warning', el['slide'], eid, 'Professional photo uses circular/avatar crop; prefer rectangular/editorial unless explicitly requested.'))
        if 'fake-person' in (el.get('class') or '').lower() or 'fake-clinic' in (el.get('class') or '').lower():
            issues.append(Issue('critical', el['slide'], eid, 'Fake image/person built with HTML/CSS detected; use one <img> instead.'))

    # likely unintended overlaps between important objects
    for slide, els in by_slide.items():
        important = [e for e in els if e['_role'] in IMPORTANT_ROLES | {'image', 'professional-photo'} and bbox(e)]
        for i, a in enumerate(important):
            ba = bbox(a)
            if not ba:
                continue
            for b in important[i+1:]:
                bb = bbox(b)
                if not bb:
                    continue
                ov = overlap(ba, bb)
                if ov <= 0:
                    continue
                denom = max(1.0, min(area(ba), area(bb)))
                ratio = ov / denom
                if ratio > 0.12:
                    aid = a.get('reviewId') or a.get('id') or f'{a["tag"]}#{a["_idx"]}'
                    bid = b.get('reviewId') or b.get('id') or f'{b["tag"]}#{b["_idx"]}'
                    issues.append(Issue('warning', slide, f'{aid} ↔ {bid}', f'Likely object overlap/collision ({ratio:.0%} of smaller bbox). Verify visually.'))

    # slide-to-slide composition continuity/rhythm checks
    # These are intentionally strict: if the carousel alternates image/text, repeated
    # anchors should either align consistently or be obviously deliberate.
    for slide in range(1, parser.slide):
        cur = by_slide.get(slide, [])
        nxt = by_slide.get(slide + 1, [])
        slide_w, _ = parser.slide_dims.get(slide, (1080, 1350))
        next_w, _ = parser.slide_dims.get(slide + 1, (1080, 1350))
        img_a = primary_for_role(cur, {'image', 'professional-photo'})
        img_b = primary_for_role(nxt, {'image', 'professional-photo'})
        title_a = primary_for_role(cur, {'title'})
        title_b = primary_for_role(nxt, {'title'})

        if img_a and img_b:
            sa = box_summary(img_a, slide_w)
            sb = box_summary(img_b, next_w)
            if sa and sb:
                same_side = sa['side'] == sb['side']
                alternating_sides = {sa['side'], sb['side']} == {'left', 'right'}
                top_delta = abs(sa['box'][1] - sb['box'][1])
                height_delta = abs(sa['height'] - sb['height'])
                width_delta = abs(sa['width'] - sb['width'])
                if same_side and (abs(sa['cx'] - sb['cx']) > 70 or top_delta > 90 or height_delta > 130):
                    issues.append(Issue('warning', slide + 1, 'composition-transition', f'Primary image does not align with previous slide on the same side (Δx={abs(sa["cx"]-sb["cx"]):.0f}, Δtop={top_delta:.0f}, Δh={height_delta:.0f}). Align or make the transition clearly intentional.'))
                if alternating_sides and (top_delta > 110 or height_delta > 160 or width_delta > 120):
                    issues.append(Issue('warning', slide + 1, 'composition-transition', f'Primary image alternates side from slide {slide} but crop/anchor does not mirror cleanly (Δtop={top_delta:.0f}, Δw={width_delta:.0f}, Δh={height_delta:.0f}). Adjust image position/size for a smoother transition.'))

        if title_a and title_b:
            ta = box_summary(title_a, slide_w)
            tb = box_summary(title_b, next_w)
            if ta and tb and ta['side'] == tb['side'] and abs(ta['box'][0] - tb['box'][0]) > 55:
                issues.append(Issue('warning', slide + 1, 'composition-transition', f'Title starts on same side as previous slide but x-position jumps {abs(ta["box"][0]-tb["box"][0]):.0f}px. Align title anchors or make layout change more intentional.'))

        if img_a and img_b and title_a and title_b:
            sa = box_summary(img_a, slide_w)
            sb = box_summary(img_b, next_w)
            ta = box_summary(title_a, slide_w)
            tb = box_summary(title_b, next_w)
            if sa and sb and ta and tb:
                relation_a = (sa['side'], ta['side'])
                relation_b = (sb['side'], tb['side'])
                if relation_a == relation_b and slide > 1:
                    # Repeating the exact same image/title side relationship can be fine,
                    # but it often means the carousel rhythm is static. Warn for review.
                    issues.append(Issue('warning', slide + 1, 'composition-rhythm', f'Image/title side relationship repeats previous slide ({relation_b[0]} image + {relation_b[1]} title). Vary rhythm or document why repetition is intentional.'))

    impeccable_issues, impeccable_findings = run_impeccable_detect(html)
    issues.extend(impeccable_issues)

    critical = sum(1 for i in issues if i.severity == 'critical')
    warnings = sum(1 for i in issues if i.severity == 'warning')
    # Strict gate for the new GetPosts flow: warnings are not acceptable as final output.
    # A warning means the HTML designer must adjust before approval.
    status = 'FAIL' if critical else ('REVISE' if warnings else 'PASS')
    return {
        'status': status,
        'artifact': str(artifact),
        'slides': parser.slide,
        'elements': len(parser.elements),
        'critical': critical,
        'warnings': warnings,
        'issues': [asdict(i) for i in issues],
        'roleCounts': role_counts(parser.elements),
        'impeccableFindings': impeccable_findings,
    }


def role_counts(elements: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for e in elements:
        r = e.get('_role') or classify(e)
        out[r] = out.get(r, 0) + 1
    return out


def write_reports(artifact: Path, report: dict[str, Any]) -> None:
    (artifact / 'html-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = [
        '# HTML Review', '',
        f"Status: **{report['status']}**", '',
        f"Slides: {report['slides']}",
        f"Elements: {report['elements']}",
        f"Critical: {report['critical']}",
        f"Warnings: {report['warnings']}",
        f"Impeccable findings: {len(report.get('impeccableFindings') or [])}",
        f"Role counts: `{json.dumps(report['roleCounts'], ensure_ascii=False)}`", '',
    ]
    if report['issues']:
        lines.append('## Deterministic issues')
        for i in report['issues']:
            lines.append(f"- **{i['severity'].upper()}** slide {i['slide']} / {i['element']}: {i['message']}")
    else:
        lines.append('No deterministic issues found. Agent must still visually inspect screenshots with the rubric.')
    if report['status'] == 'REVISE':
        lines.append('\n## Required action\nEvery warning above must be fixed before this HTML can pass. Do not treat warnings or Impeccable findings as acceptable polish.')
    lines.append('\n## Visual review checklist\nUse `references/html-review-rubric.md` for final PASS/REVISE/FAIL judgment. Visual concerns should also become REVISE items, not optional notes.')
    (artifact / 'html-review.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: review-html-design.py <artifact-folder>')
    artifact = Path(sys.argv[1]).resolve()
    report = audit(artifact)
    write_reports(artifact, report)
    print(json.dumps({
        'status': report['status'],
        'report': str(artifact / 'html-review.json'),
        'markdown': str(artifact / 'html-review.md'),
        'summary': {k: report[k] for k in ['slides', 'elements', 'critical', 'warnings', 'roleCounts']} | {'impeccableFindings': len(report.get('impeccableFindings') or [])},
    }, ensure_ascii=False, indent=2))
    if report['critical']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
