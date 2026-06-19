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

# --- Composition coherence (forces SKILL step 3c) -------------------------------
# Repeated-slot phrase: "item 2 de 4 de uma lista", "célula 3 de 4 de uma grade",
# "passo 1 de 5". Captures kind, index, count.
COMPOSITION_INDEX_RE = re.compile(
    r"\b(item|c[ée]lula|passo)\s+(\d+)\s+de\s+(\d+)\b",
    re.I,
)
# Comparison-side phrases that a comparison slide MUST use on its column titles.
COMPARISON_SIDE_RE = re.compile(r"\blado\s+[ab]\s+da\s+compara", re.I)
COMPARISON_VERDICT_RE = re.compile(r"\bveredicto\b", re.I)
# Narrative role an image description MUST carry (function in the slide, not theme).
IMAGE_ROLE_RE = re.compile(
    r"\b(capa|abertura|prova|fechamento|cta|apoio\s+contextual|contextual\s+da\s+l[âa]mina|mensagem-chave)\b",
    re.I,
)
# Image theme/style lock that travels the placeholder theme into the description.
# These are concrete *subjects/scene* words — never allowed (theme must stay open).
# Style registers (dark, editorial, premium…) are handled by IMAGE_STYLE_OK_RE below
# and are NOT flagged here; only locked subjects are.
IMAGE_THEME_LOCK_RE = re.compile(
    r"\b(joelho|articula[çc][ãa]o|anatomia|mitoc[ôo]ndria|c[ée]lula\b|m[úu]sculo|tend[ãa]o|"
    r"caf[ée]|mesa|caderno|x[íi]cara|escrit[óo]rio|cozinha|cl[íi]nic[ao]|consult[óo]rio|paciente|"
    r"vermelho-alaranjado|azul-ciano|neon|glow|sci-fi|hologr[áa]fic|grid\s+digital)\b",
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

def enclosing_slide(node: Node) -> Node | None:
    p = node.parent
    while p:
        if p.tag == "section" and "slide" in p.attrs.get("class", ""):
            return p
        p = p.parent
    return None

def description_role(value: str | None) -> str:
    """Coarse role key = first component of the 5-part formula (text before first ';').
    Used to group equivalent slots within a slide. Normalized + index stripped so
    'item 1 de 4...' and 'item 2 de 4...' share the same role key."""
    if not value:
        return ""
    head = value.split(";", 1)[0]
    head = COMPOSITION_INDEX_RE.sub(lambda m: f"{m.group(1).lower()} N de M", head)
    return " ".join(head.lower().split())

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
        has_glow = n.attrs.get("data-glow")
        if not has_darken and not has_gradient and not has_glow:
            issue(n, "Element has CSS gradient in style but missing data-darken, data-gradient, or data-glow. Use data-darken='<preset>' for darkening overlays, data-gradient JSON for custom overlays, or data-glow='<preset>' for atmospheric glow.")
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
        # Validate data-glow (atmospheric glow with brand color)
        VALID_GLOW_PRESETS = {"center"}
        if has_glow:
            if has_glow not in VALID_GLOW_PRESETS:
                issue(n, f"data-glow='{has_glow}' is not a valid preset. Valid: {', '.join(sorted(VALID_GLOW_PRESETS))}")
            glow_var = n.attrs.get("data-glow-variable", "")
            if glow_var not in ("primary", "secondary"):
                issue(n, f"data-glow-variable must be 'primary' or 'secondary', got '{glow_var}'")
            alpha_str = n.attrs.get("data-glow-alpha", "")
            if alpha_str:
                try:
                    alpha_val = float(alpha_str)
                    if not (0.0 <= alpha_val <= 1.0):
                        issue(n, f"data-glow-alpha={alpha_str} must be between 0.0 and 1.0.")
                except ValueError:
                    issue(n, f"data-glow-alpha='{alpha_str}' is not a valid number.")
            else:
                issue(n, "Element with data-glow is missing data-glow-alpha (required, 0.0-1.0).")
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
            desc = n.attrs.get("data-te-description")
            if not desc:
                issue(n, "Editable image missing data-te-description.")
            else:
                # NOTE: the coarse THEME_SPECIFIC regex is intentionally NOT applied to images.
                # Images are allowed to carry a STYLE register (dark/premium/editorial) as a bound;
                # only locked SUBJECTS/SCENES are forbidden (handled by IMAGE_THEME_LOCK_RE below).
                # Theme/subject of the placeholder must NOT be locked into the description.
                locked = sorted({m.group(0).lower() for m in IMAGE_THEME_LOCK_RE.finditer(" ".join(desc.split()))})
                if locked:
                    issue(n, f"Editable image data-te-description locks the placeholder theme/scene ({', '.join(locked)}). "
                              "Theme MUST stay open (reflect the slide's mensagem-chave). Keep only the visual STYLE register "
                              "(ex: 'dark premium editorial') as a bound, not the subject.")
                # Image must carry its NARRATIVE ROLE in the slide (capa/prova/CTA/apoio), not just an aesthetic.
                if not IMAGE_ROLE_RE.search(" ".join(desc.split())):
                    issue(n, "Editable image data-te-description is missing the narrative role of the slide "
                              "(ex: 'imagem de capa/abertura', 'imagem de prova', 'imagem de fechamento/CTA', 'apoio contextual da lâmina'). "
                              "The role comes from the slide's purpose, not from the placeholder photo.")
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

    # --- Composition coherence per slide (forces SKILL step 3c) ------------------
    # Group editable TEXT elements by their enclosing slide and validate that
    # repeated slots within the same slide carry a correct, non-restarting index,
    # that equivalent slots don't share a byte-identical description, and that
    # comparison layouts actually use lado A / lado B / veredicto phrasing.
    text_editable = [n for n in editable if n.tag != "img" and textish(n) and not is_inline_text_run(n)]
    by_slide: dict[int, list[Node]] = {}
    for n in text_editable:
        slide = enclosing_slide(n)
        if slide is None:
            continue
        by_slide.setdefault(id(slide), []).append(n)

    for slide in slides:
        elems = by_slide.get(id(slide), [])
        if not elems:
            continue

        # (a) Repeated-slot index/count coherence.
        #     Collect every "<kind> N de M" found among this slide's descriptions.
        #     A comparison legitimately repeats item 1..M per side, so the group key
        #     includes the side ("lado a"/"lado b"/"coluna a"/"coluna b") when present —
        #     each side is then validated as its own independent sequence.
        SIDE_RE = re.compile(r"\b(?:lado|coluna)\s+([ab])\b", re.I)
        seq: dict[str, list[tuple[int, int, Node]]] = {}
        for n in elems:
            desc = n.attrs.get("data-te-description") or ""
            side_m = SIDE_RE.search(desc)
            side = side_m.group(1).lower() if side_m else ""
            for m in COMPOSITION_INDEX_RE.finditer(desc):
                kind = m.group(1).lower().replace("é", "e")
                key = f"{kind}|{side}" if side else kind
                idx, count = int(m.group(2)), int(m.group(3))
                seq.setdefault(key, []).append((idx, count, n))
        for key, entries in seq.items():
            kind, _, side = key.partition("|")
            label = f"{kind} N de M" + (f" (lado {side.upper()})" if side else "")
            counts = {c for _, c, _ in entries}
            indices = [i for i, _, _ in entries]
            declared = next(iter(counts))
            actual = len(entries)
            # M must agree across the group and match how many slots actually exist.
            if len(counts) > 1:
                issue(slide, f"Composition '{label}' on this slide declares inconsistent M values "
                              f"({sorted(counts)}). All items of the same group must share the same total M.")
            elif declared != actual:
                issue(slide, f"Composition '{label}' declares M={declared} but the slide has {actual} "
                              f"'{kind}' slots in this group. M must equal the real number of repeated slots.")
            # Indices must be the unique sequence 1..M with no restart/gap/dup.
            if sorted(indices) != list(range(1, actual + 1)):
                issue(slide, f"Composition '{label}' indices are {indices}; expected a single "
                              f"non-restarting sequence 1..{actual}. Restarting indices (e.g. 1,2,3,1,2,3) mean two "
                              f"distinct groups were marked as one — likely a comparison/grid mislabeled as one list. "
                              f"Use 'lado A/lado B' (or separate groups) so each side is its own sequence.")

        # (b) Byte-identical descriptions on equivalent slots in the SAME slide.
        seen: dict[str, Node] = {}
        for n in elems:
            desc = n.attrs.get("data-te-description") or ""
            if not desc:
                continue
            if desc in seen:
                issue(n, "Two editable texts in the same slide share a byte-identical data-te-description. "
                          "Slots repeated within a slide must differ in the '<papel na composição>' component "
                          "(item 1 de N / item 2 de N …). Identical strings make the copy LLM duplicate content.")
            else:
                seen[desc] = n

        # (c) Comparison detection: 2 column-title-like slots sharing a role +
        #     symmetric bullet groups, but no 'lado A/B' phrasing anywhere.
        roles: dict[str, list[Node]] = {}
        for n in elems:
            roles.setdefault(description_role(n.attrs.get("data-te-description")), []).append(n)
        has_restarting_index = any(
            sorted([i for i, _, _ in entries]) != list(range(1, len(entries) + 1))
            for entries in seq.values()
        )
        slide_descs = " ".join((n.attrs.get("data-te-description") or "") for n in elems)
        looks_comparison = has_restarting_index or any(len(v) == 2 for v in roles.values() if v)
        if looks_comparison and not COMPARISON_SIDE_RE.search(slide_descs):
            # Only escalate when there's a real signal of two parallel groups.
            paired_roles = [k for k, v in roles.items() if len(v) >= 2]
            if has_restarting_index or len(paired_roles) >= 2:
                issue(slide, "Slide looks like a COMPARISON (parallel/duplicated slots or restarting indices) but no "
                              "description uses 'lado A da comparação' / 'lado B da comparação' / 'veredicto'. "
                              "Mark column titles and their bullets with the comparison composition role so the copy LLM "
                              "keeps each side coherent.")

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
    ui_label_words = {"✓", "1", "2", "3", "4", "5", "cta", "primeiro", "importante"}
    for n in nodes:
        txt = " ".join(n.text.split()).strip()
        if not txt or len(txt) < 8:
            continue
        if n.tag in {"style", "script", "title"}:
            continue
        if truthy(n.attrs.get("data-template-element")) or truthy(n.attrs.get("data-static")) or n.attrs.get("data-text-type") or n.attrs.get("data-variable") or is_inline_text_run(n):
            continue
        if txt.lower() in ui_label_words:
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
