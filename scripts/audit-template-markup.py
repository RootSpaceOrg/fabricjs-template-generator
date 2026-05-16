#!/usr/bin/env python3
"""Audit GetPosts marked HTML before Fabric conversion.

Usage:
  python3 audit-template-markup.py <artifact-folder-or-template.html>
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VALID_IMAGE_TYPES = {"brandLogo", "professionalPhoto", "userAsset"}
VALID_TEXT_TYPES = {"instagramHandle", "instagramName", "phone", "address"}
VALID_VARIABLES = {"primary", "secondary"}
VALID_VARIABLE_TARGETS = {"fill", "stroke", "background"}
THEME_SPECIFIC_DESCRIPTION_RE = re.compile(
    r"\b(laserterapia|laser|joelho|paciente|cl[ií]nica|cl[ií]nico|sa[uú]de|consulta|consult[oó]rio|tratamento|terapia|premium|nicho|tema|foco\s+em|tom\s+premium)\b",
    re.I,
)

class Node:
    def __init__(self, tag, attrs, line, parent=None):
        self.tag = tag
        self.attrs = dict(attrs)
        self.line = line
        self.text = ""
        self.parent = parent
        self.children = []

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        parent = self.stack[-1] if self.stack else None
        node = Node(tag, attrs, self.getpos()[0], parent)
        if parent:
            parent.children.append(node)
        self.nodes.append(node)
        if tag not in {"img", "meta", "link", "br", "hr", "input"}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self.stack:
            self.stack[-1].text += data

def read_html(arg: str) -> Path:
    p = Path(arg)
    if p.is_dir():
        p = p / "template.html"
    if not p.exists():
        raise SystemExit(f"template.html not found: {p}")
    return p

def truthy(v: str | None) -> bool:
    return str(v).lower() == "true"

def textish(node: Node) -> bool:
    return node.tag in {"h1", "h2", "h3", "h4", "p", "span", "div", "strong", "em"} and bool(node.text.strip())

def has_editable_ancestor(node: Node) -> bool:
    p = node.parent
    while p:
        if truthy(p.attrs.get("data-template-element")):
            return True
        p = p.parent
    return False

def is_inline_text_run(node: Node) -> bool:
    return node.tag in {"span", "strong", "em"} and has_editable_ancestor(node) and bool(node.text.strip())

def theme_specific_description(value: str | None) -> bool:
    return bool(value and THEME_SPECIFIC_DESCRIPTION_RE.search(" ".join(value.split())))

def main() -> int:
    html_path = read_html(sys.argv[1] if len(sys.argv) > 1 else "")
    html = html_path.read_text(encoding="utf-8")
    parser = Parser()
    parser.feed(html)
    nodes = parser.nodes
    issues = []
    warnings = []

    def issue(node, msg):
        issues.append({"line": node.line, "tag": node.tag, "message": msg})

    def warn(node, msg):
        warnings.append({"line": node.line, "tag": node.tag, "message": msg})

    if not re.search(r'<html\b[^>]*data-template-name=', html):
        issues.append({"line": 1, "tag": "html", "message": "Missing data-template-name on <html>."})
    if not re.search(r'<html\b[^>]*data-segment=', html):
        warnings.append({"line": 1, "tag": "html", "message": "Missing data-segment on <html>."})
    if 'name="hm-fonts"' not in html and "name='hm-fonts'" not in html:
        warnings.append({"line": 1, "tag": "meta", "message": "Missing <meta name=\"hm-fonts\">."})

    duplicate_style = len(re.findall(r'<[^>]*\bstyle="[^"]*"[^>]*\bstyle="', html))
    if duplicate_style:
        issues.append({"line": 0, "tag": "html", "message": f"Found {duplicate_style} elements with duplicate style attributes."})

    # Inline CSS enforcement: <style> blocks are forbidden (converter can't read class-based styles)
    style_blocks = re.findall(r'<style\b[^>]*>(.*?)</style>', html, re.S | re.I)
    for block in style_blocks:
        # Allow minimal reset only (* { margin:0; box-sizing:border-box })
        stripped = re.sub(r'/\*.*?\*/', '', block, flags=re.S).strip()
        lines = [l.strip() for l in stripped.split('\n') if l.strip() and not l.strip().startswith('//')]
        # If it's more than a basic reset, it's a problem
        if any(prop in stripped for prop in ['background', 'color:', 'font-', 'border', 'width:', 'height:', 'position', 'left:', 'top:', 'gradient']):
            issues.append({"line": 0, "tag": "style", "message": "Found <style> block with layout/visual CSS. All styles MUST be inline (style=\"...\"). The converter cannot read class-based styles — gradients, positions, and colors in <style> blocks are lost during conversion."})

    # Brand gradients eliminated: data-variable-stops is now forbidden
    for n in nodes:
        if n.attrs.get("data-variable-stops"):
            issue(n, "data-variable-stops is no longer supported. Brand gradients are eliminated. Use solid background with data-variable='primary' data-variable-target='background' + data-darken for depth.")

    # Gradient determinism: elements with CSS gradient must have data-darken OR data-gradient
    GRADIENT_RE = re.compile(r'(linear|radial)-gradient\s*\(', re.I)
    VALID_DARKEN_PRESETS = {"bottom", "top", "right", "left", "diagonal-se", "diagonal-ne", "vignette", "vignette-top-left"}
    for n in nodes:
        style_val = n.attrs.get("style", "")
        if not GRADIENT_RE.search(style_val):
            continue
        has_darken = n.attrs.get("data-darken")
        has_gradient = n.attrs.get("data-gradient")
        if not has_darken and not has_gradient:
            issue(n, "Element has CSS gradient in style but missing data-darken or data-gradient. Use data-darken='<preset>' for darkening overlays, or data-gradient JSON for custom overlays.")
            continue
        # Validate data-darken
        if has_darken:
            if has_darken not in VALID_DARKEN_PRESETS:
                issue(n, f"data-darken='{has_darken}' is not a valid preset. Valid: {', '.join(sorted(VALID_DARKEN_PRESETS))}")
            opacity_str = n.attrs.get("data-darken-opacity", "")
            if opacity_str:
                try:
                    opacity_val = float(opacity_str)
                    if not (0.1 <= opacity_val <= 1.0):
                        issue(n, f"data-darken-opacity={opacity_str} must be between 0.1 and 1.0.")
                except ValueError:
                    issue(n, f"data-darken-opacity='{opacity_str}' is not a valid number.")
            else:
                issue(n, "Element with data-darken is missing data-darken-opacity (required, 0.1-1.0).")
        # Validate data-gradient JSON (for custom overlays only)
        if has_gradient and not has_darken:
            try:
                grad = json.loads(has_gradient)
                if not isinstance(grad, dict):
                    issue(n, "data-gradient: value must be a JSON object.")
                    continue
                if grad.get("type") not in ("linear", "radial"):
                    issue(n, "data-gradient: type must be 'linear' or 'radial'.")
                if not isinstance(grad.get("coords"), dict):
                    issue(n, "data-gradient: missing or invalid 'coords' object.")
                stops = grad.get("colorStops")
                if not isinstance(stops, list) or len(stops) == 0:
                    issue(n, "data-gradient: missing or empty 'colorStops' array.")
            except (json.JSONDecodeError, TypeError):
                issue(n, "data-gradient: value is not valid JSON.")

    slides = [n for n in nodes if n.tag == "section" and "slide" in n.attrs.get("class", "")]
    if not slides:
        issues.append({"line": 0, "tag": "section", "message": "No section.slide found."})
    for slide in slides:
        if not slide.attrs.get("data-width") or not slide.attrs.get("data-height"):
            issue(slide, "section.slide missing data-width/data-height.")

    editable = [n for n in nodes if truthy(n.attrs.get("data-template-element"))]
    static = [n for n in nodes if truthy(n.attrs.get("data-static"))]
    imgs = [n for n in nodes if n.tag == "img"]
    text_types = [n for n in nodes if n.attrs.get("data-text-type")]
    variables = [n for n in nodes if n.attrs.get("data-variable")]

    for n in editable:
        if truthy(n.attrs.get("data-static")):
            issue(n, "Element cannot be both data-template-element=true and data-static=true.")
        if n.attrs.get("data-text-type"):
            issue(n, "Business profile text cannot also be a template element.")
        if n.tag == "img":
            if not n.attrs.get("data-te-description"):
                issue(n, "Editable image missing data-te-description.")
            elif theme_specific_description(n.attrs.get("data-te-description")):
                issue(n, "Editable image data-te-description is theme/style-specific. Use a generic role description that works for any theme.")
            if n.attrs.get("data-image-type") != "userAsset":
                warn(n, "Editable image is usually data-image-type=userAsset.")
        elif textish(n):
            if is_inline_text_run(n):
                issue(n, "Inline span/strong/em inside editable text must not be data-template-element. Mark only the parent textbox; converter must turn inline runs into Fabric textbox.styles.")
            if not n.attrs.get("data-te-description"):
                issue(n, "Editable text missing data-te-description.")
            elif theme_specific_description(n.attrs.get("data-te-description")):
                issue(n, "Editable text data-te-description is theme/style-specific. Use a generic role description that works for any theme.")
            if not n.attrs.get("data-te-max-chars"):
                issue(n, "Editable text missing data-te-max-chars.")
            else:
                try:
                    if int(n.attrs["data-te-max-chars"]) <= 0:
                        issue(n, "data-te-max-chars must be positive.")
                except ValueError:
                    issue(n, "data-te-max-chars must be an integer.")

    for n in imgs:
        img_type = n.attrs.get("data-image-type")
        if not img_type:
            issue(n, "<img> missing data-image-type.")
        elif img_type not in VALID_IMAGE_TYPES:
            issue(n, f"Invalid data-image-type: {img_type}.")
        if img_type in {"brandLogo", "professionalPhoto"} and not truthy(n.attrs.get("data-static")):
            warn(n, f"{img_type} is normally data-static=true unless explicitly content-generated.")
        if img_type == "userAsset" and not truthy(n.attrs.get("data-template-element")):
            warn(n, "userAsset image is usually data-template-element=true.")

    for n in text_types:
        tt = n.attrs.get("data-text-type")
        if tt not in VALID_TEXT_TYPES:
            issue(n, f"Invalid data-text-type: {tt}.")
        if not truthy(n.attrs.get("data-static")):
            issue(n, "data-text-type element must also have data-static=true.")
        if truthy(n.attrs.get("data-template-element")):
            issue(n, "data-text-type element cannot be template element.")

    for n in nodes:
        if is_inline_text_run(n):
            if n.attrs.get("data-text-type"):
                issue(n, "Inline text run cannot have data-text-type; mark the parent/profile textbox instead.")
            if truthy(n.attrs.get("data-static")):
                issue(n, "Inline text run inside editable text should not be data-static; it is a style range inside the parent textbox.")
            if n.attrs.get("data-review-id"):
                warn(n, "Inline styled span has data-review-id. Prefer no data-review-id on child spans unless debugging; it must still convert to parent textbox.styles, never a separate object.")
            if n.attrs.get("data-variable") and n.attrs.get("data-variable-target", "fill") != "fill":
                issue(n, "Inline text color variables should use data-variable-target=fill.")

    for n in variables:
        var = n.attrs.get("data-variable")
        target = n.attrs.get("data-variable-target", "fill")
        if var not in VALID_VARIABLES:
            issue(n, f"Invalid data-variable: {var}.")
        if target not in VALID_VARIABLE_TARGETS:
            issue(n, f"Invalid data-variable-target: {target}.")

    # Heuristic: content-like text that is neither editable nor profile/static may be forgotten.
    chrome_words = {"✓", "1", "2", "3", "4", "5", "cta", "primeiro", "importante"}
    for n in nodes:
        txt = " ".join(n.text.split()).strip()
        if not txt or len(txt) < 8:
            continue
        if n.tag in {"style", "script", "title"}:
            continue
        if truthy(n.attrs.get("data-template-element")) or truthy(n.attrs.get("data-static")) or n.attrs.get("data-text-type") or n.attrs.get("data-variable") or is_inline_text_run(n):
            continue
        if txt.lower() in chrome_words:
            continue
        # Parent containers often accumulate child text; only warn when direct text-like tags.
        if n.tag in {"h1", "h2", "h3", "p", "span", "strong"}:
            warn(n, f"Text may be unclassified: {txt[:80]!r}.")

    result = {
        "status": "FAIL" if issues else "PASS",
        "file": str(html_path),
        "summary": {
            "slides": len(slides),
            "editable": len(editable),
            "static": len(static),
            "images": len(imgs),
            "textTypes": len(text_types),
            "variables": len(variables),
            "issues": len(issues),
            "warnings": len(warnings),
        },
        "issues": issues,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if issues else 0

if __name__ == "__main__":
    sys.exit(main())
