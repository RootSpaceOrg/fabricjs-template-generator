#!/usr/bin/env node
/**
 * Conversor fechado FITA HTML → Fabric JSON por slide (contrato: engine/CATALOG.md).
 *
 * A fita inteira é UM html (`fita.html`): N seções `section.slide` lado a lado
 * + opcional `.fita-layer` com elementos estáticos que cruzam fronteiras.
 * Elemento de travessia é emitido em TODO slide que intersecta, com o centro
 * deslocado — o Fabric clipa o que fica fora do canvas.
 *
 * Violação = rejeição apontando o data-el-id — a correção é regenerar o HTML,
 * nunca editar o JSON.
 *
 * Uso: node engine/convert.js <run-dir|fita.html> <outdir> [--slug <slug>]
 * Saída: <outdir>/slide-N.json + manifest.json (crop das imagens completado
 * pelo engine/tools/center-clippable-images.js, encadeado automaticamente).
 */

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { chromium } = require("playwright");

const REPO = path.resolve(__dirname, "..");

// src local (file://) vira data-URI — o template final não pode depender de disco
const MIME = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
  ".gif": "image/gif", ".svg": "image/svg+xml" };
const inlineSrc = (src, id) => {
  if (!src || !src.startsWith("file://")) return src;
  const p = require("url").fileURLToPath(src);
  if (!fs.existsSync(p)) {
    console.error(`REJEITADO — ${id}: src aponta arquivo inexistente: ${p}`);
    process.exit(1);
  }
  const mime = MIME[path.extname(p).toLowerCase()] || "image/png";
  return `data:${mime};base64,` + fs.readFileSync(p).toString("base64");
};

const rgb2hex = (c) => {
  const m = (c || "").match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
  if (!m) return c || null;
  if (m[4] !== undefined && parseFloat(m[4]) === 0) return null;
  return "#" + [m[1], m[2], m[3]].map((v) => (+v).toString(16).padStart(2, "0")).join("").toUpperCase();
};

(async () => {
  const args = process.argv.slice(2);
  const slugIdx = args.indexOf("--slug");
  const slug = slugIdx >= 0 ? args[slugIdx + 1] : null;
  const [inArg, outDir] = args.filter((a, i) => !a.startsWith("--") && (slugIdx < 0 || i !== slugIdx + 1));
  if (!inArg || !outDir) {
    console.error("uso: node engine/convert.js <run-dir|fita.html> <outdir> [--slug <slug>]");
    process.exit(2);
  }
  const fitaPath = inArg.endsWith(".html") ? path.resolve(inArg) : path.resolve(inArg, "fita.html");
  if (!fs.existsSync(fitaPath)) { console.error(`fita.html não encontrada: ${fitaPath}`); process.exit(2); }
  fs.mkdirSync(outDir, { recursive: true });

  const html = fs.readFileSync(fitaPath, "utf-8");
  const htmlIds = new Set([...html.matchAll(/data-el-id="([^"]+)"/g)].map((m) => m[1]));
  const packSlug = (html.match(/data-pack="([^"]+)"/) || [])[1];
  if (!packSlug) { console.error("REJEITADO — <main class=\"fita\"> sem data-pack (CATALOG.md §Esqueleto)"); process.exit(1); }
  const packDir = path.join(REPO, "packs", packSlug);
  const pack = JSON.parse(fs.readFileSync(path.join(packDir, "pack.json"), "utf-8"));
  const tokensCss = ":root{" + Object.entries(pack.tokens).map(([k, v]) => `--${k}:${v}`).join(";") + "}";

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 1500 } });
  await page.goto("file://" + fitaPath, { waitUntil: "networkidle" });
  const dsHref = "file:///" + path.join(REPO, "engine", "design-system.css").replace(/\\/g, "/");
  await page.addStyleTag({ url: dsHref });
  if (pack.fonts && pack.fonts.css) await page.addStyleTag({ url: pack.fonts.css });
  await page.addStyleTag({ content: tokensCss });
  await page.evaluate(() => document.fonts.ready);

  const data = await page.evaluate(() => {
    const TEXT = new Set(["ds-eyebrow", "ds-headline", "ds-body", "ds-number", "ds-watermark"]);
    const CHIP = new Set(["ds-stamp", "ds-cta"]);
    const SHAPE = new Set(["ds-block", "ds-card"]);
    const IMG = new Set(["ds-photo", "ds-slot"]);
    const FORBIDDEN_TAGS = new Set(["SVG", "CANVAS", "VIDEO", "IFRAME", "OBJECT", "EMBED"]);
    const fita = document.querySelector("main.fita");
    if (!fita) return { fatal: "sem <main class=\"fita\">" };
    const secEls = [...fita.querySelectorAll("section.slide")];
    if (!secEls.length) return { fatal: "fita sem <section class=\"slide\">" };
    const rejects = [];

    const attrs = (el) => {
      const a = {};
      for (const at of el.attributes) if (at.name.startsWith("data-")) a[at.name] = at.value;
      return a;
    };
    const angleOf = (s) => {
      const m = (s.transform || "").match(/matrix\(([-\d.]+),\s*([-\d.]+)/);
      return m ? Math.round(Math.atan2(parseFloat(m[2]), parseFloat(m[1])) * 180 / Math.PI * 100) / 100 : 0;
    };
    const styleOk = (el) => {
      const raw = el.getAttribute("style") || "";
      return raw.split(";").map((p) => p.trim()).filter(Boolean).every((p) => {
        const prop = p.split(":")[0].trim();
        if (prop === "grid-area") return true;
        if (prop === "transform") return /^transform:\s*rotate\([-\d.]+deg\)$/.test(p);
        return false;
      });
    };
    const runsOf = (el, s) => {
      const runs = [];
      for (const n of el.childNodes) {
        if (n.nodeType === 3 && n.textContent) runs.push({ t: n.textContent.replace(/\\+n/g, "\n"), color: s.color });
        else if (n.nodeType === 1 && n.tagName === "BR") runs.push({ t: "\n", color: s.color });
        else if (n.nodeType === 1 && (n.tagName === "SPAN" || n.tagName === "B" || n.tagName === "EM")) {
          runs.push({ t: (n.innerText || "").replace(/\\+n/g, "\n"), color: getComputedStyle(n).color });
        } else if (n.nodeType === 1) {
          rejects.push({ id: el.getAttribute("data-el-id"), reason: `filho <${n.tagName.toLowerCase()}> dentro de componente de texto (só span/b/em/br)` });
        }
      }
      return runs;
    };
    const textMeta = (el, s) => ({
      fs: parseFloat(s.fontSize),
      weight: /^\d+$/.test(s.fontWeight) ? parseInt(s.fontWeight) : s.fontWeight,
      family: s.fontFamily.split(",")[0].replace(/["']/g, "").trim(),
      color: s.color,
      align: s.textAlign === "start" ? "left" : s.textAlign,
      spacing: parseFloat(s.letterSpacing) || 0,
      lineH: s.lineHeight === "normal" ? 1.16 : Math.max(1, parseFloat(s.lineHeight) / parseFloat(s.fontSize)),
      upper: s.textTransform === "uppercase",
    });

    // walk genérico: origem (rect de referência) + destino (nodes/rects)
    const makeWalk = (originRect, nodes, rects, inLayer) => {
      const walk = (el, depth) => {
        if (FORBIDDEN_TAGS.has(el.tagName)) {
          rejects.push({ id: el.getAttribute("data-el-id") || el.tagName, reason: `tag proibida <${el.tagName.toLowerCase()}>` });
          return;
        }
        const cls = [...el.classList].find((c) => c.startsWith("ds-"));
        const id = el.getAttribute("data-el-id");
        if (!cls) { rejects.push({ id: id || el.tagName + "?", reason: "elemento sem componente ds-* do catálogo" }); return; }
        if (!TEXT.has(cls) && !CHIP.has(cls) && !SHAPE.has(cls) && !IMG.has(cls)) {
          rejects.push({ id: id || cls, reason: `classe fora do catálogo: ${cls}` }); return;
        }
        if (!id) { rejects.push({ id: cls + "?", reason: "componente sem data-el-id (lei de conservação)" }); return; }
        if (!styleOk(el)) { rejects.push({ id, reason: "inline style fora da whitelist (só grid-area e transform:rotate)" }); return; }
        if (inLayer) {
          if (!el.hasAttribute("data-static") || !(el.hasAttribute("data-layer") || cls === "ds-watermark")) {
            rejects.push({ id, reason: "fita-layer: só elementos data-static + data-layer (travessia nunca é editável)" });
            return;
          }
          if (el.hasAttribute("data-template-element")) {
            rejects.push({ id, reason: "fita-layer: elemento editável não pode cruzar fronteira" });
            return;
          }
        }
        const s = getComputedStyle(el);
        if (s.display === "none" || s.visibility === "hidden") return;
        if (s.mixBlendMode !== "normal" || (s.backdropFilter && s.backdropFilter !== "none"))
          rejects.push({ id, reason: "mix-blend-mode/backdrop-filter proibidos" });
        const bgImg = s.backgroundImage !== "none" ? s.backgroundImage : null;
        if (bgImg && /url\(/.test(bgImg)) { rejects.push({ id, reason: "background-image:url() — imagem é <img class=\"ds-photo\">" }); return; }
        if (bgImg && /(radial|conic)-gradient/.test(bgImg)) { rejects.push({ id, reason: "gradiente radial/conic não suportado" }); return; }

        const r = el.getBoundingClientRect();
        const box = {
          cx: r.left - originRect.left + r.width / 2, cy: r.top - originRect.top + r.height / 2,
          w: el.offsetWidth, h: el.offsetHeight, // unrotated
          aabbL: r.left - originRect.left, aabbR: r.right - originRect.left,
        };
        const isLayer = cls === "ds-watermark" || el.hasAttribute("data-layer");
        if (depth === 0 && !isLayer && !inLayer)
          rects.push({ id, l: box.cx - box.w / 2, t: box.cy - box.h / 2, r: box.cx + box.w / 2, b: box.cy + box.h / 2 });

        const base = { id, cls, ...box, angle: angleOf(s), opacity: parseFloat(s.opacity), attrs: attrs(el) };

        if (IMG.has(cls)) {
          if (el.tagName !== "IMG") { rejects.push({ id, reason: `${cls} deve ser <img>` }); return; }
          nodes.push({ kind: "img", ...base, src: el.currentSrc || el.src,
            radiusPx: parseFloat(s.borderTopLeftRadius) || 0, circle: el.hasAttribute("data-circle"),
            cutout: el.hasAttribute("data-cutout") });
          return;
        }
        if (TEXT.has(cls)) {
          nodes.push({ kind: "text", ...base, runs: runsOf(el, s), ...textMeta(el, s) });
          return;
        }
        if (CHIP.has(cls)) {
          nodes.push({ kind: "chip", ...base, bg: s.backgroundColor,
            borderColor: parseFloat(s.borderTopWidth) ? s.borderTopColor : null,
            borderW: parseFloat(s.borderTopWidth) || 0,
            radiusPx: parseFloat(s.borderTopLeftRadius) || 0,
            runs: runsOf(el, s), ...textMeta(el, s), text: (el.innerText || "").trim() });
          return;
        }
        nodes.push({ kind: "shape", ...base, bg: s.backgroundColor, bgImg,
          shadow: s.boxShadow && s.boxShadow !== "none" ? s.boxShadow : null,
          radiusPx: parseFloat(s.borderTopLeftRadius) || 0,
          radiiPx: [s.borderTopLeftRadius, s.borderTopRightRadius, s.borderBottomRightRadius, s.borderBottomLeftRadius].map((v) => parseFloat(v) || 0),
          borderW: Math.max(parseFloat(s.borderTopWidth) || 0, parseFloat(s.borderRightWidth) || 0, parseFloat(s.borderLeftWidth) || 0),
          borderColor: (parseFloat(s.borderTopWidth) || parseFloat(s.borderRightWidth) || parseFloat(s.borderLeftWidth)) ? (s.borderTopColor || s.borderRightColor) : null });
        for (const c of el.children) walk(c, depth + 1);
      };
      return walk;
    };

    const slides = secEls.map((sec) => {
      const sr = sec.getBoundingClientRect();
      const nodes = [], rects = [];
      const walk = makeWalk(sr, nodes, rects, false);
      for (const c of sec.children) walk(c, 0);
      for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
        const a = rects[i], b = rects[j];
        const ox = Math.min(a.r, b.r) - Math.max(a.l, b.l), oy = Math.min(a.b, b.b) - Math.max(a.t, b.t);
        if (ox > 4 && oy > 4) rejects.push({ id: `${a.id}×${b.id}`, reason: `sobreposição não declarada (${Math.round(ox)}×${Math.round(oy)}px) — use data-layer se for camada` });
      }
      const secS = getComputedStyle(sec);
      return { W: Math.round(sr.width), H: Math.round(sr.height), bg: secS.backgroundColor, nodes,
        role: sec.getAttribute("data-role") || "",
        secVar: sec.getAttribute("data-variable"), secVarTarget: sec.getAttribute("data-variable-target") };
    });

    // travessias: emitidas em todo slide intersectado, centro deslocado
    const fr = fita.getBoundingClientRect();
    const layer = fita.querySelector(".fita-layer");
    if (layer) {
      const layerNodes = [];
      const walk = makeWalk(fr, layerNodes, [], true);
      for (const c of layer.children) walk(c, 0);
      const SW = slides[0].W;
      for (const n of layerNodes) {
        let hit = false;
        for (let i = 0; i < slides.length; i++) {
          if (n.aabbR > i * SW + 1 && n.aabbL < (i + 1) * SW - 1) {
            slides[i].nodes.push({ ...n, cx: n.cx - i * SW });
            hit = true;
          }
        }
        if (!hit) rejects.push({ id: n.id, reason: "fita-layer: elemento inteiramente fora da fita" });
      }
    }

    return { slides, rejects,
      templateName: fita.getAttribute("data-template-name") || document.documentElement.getAttribute("data-template-name") || "",
      segment: fita.getAttribute("data-segment") || document.documentElement.getAttribute("data-segment") || "",
      fonts: (document.querySelector('meta[name="hm-fonts"]') || {}).content || "" };
  });
  await browser.close();

  if (data.fatal) { console.error(`REJEITADO — ${data.fatal}`); process.exit(1); }
  if (data.rejects.length) {
    console.error(`REJEITADO — ${data.rejects.length} violação(ões) do contrato (engine/CATALOG.md):`);
    for (const r of data.rejects) console.error(`  ${r.id}: ${r.reason}`);
    process.exit(1);
  }

  // ---- montagem dos objetos ----
  const pct = (px, w, h) => Math.min(50, Math.round((px / Math.max(1, Math.min(w, h))) * 100));
  const emittedIds = new Set();

  const teText = (attrs, id) => {
    const o = {};
    if (attrs["data-text-type"]) { o.textType = attrs["data-text-type"]; return o; }
    if ("data-template-element" in attrs && !("data-static" in attrs)) {
      const min = parseInt(attrs["data-te-min-chars"]), max = parseInt(attrs["data-te-max-chars"]);
      if (isNaN(min) || isNaN(max)) {
        console.error(`REJEITADO — ${id}: texto editável sem data-te-min-chars/max-chars`);
        process.exit(1);
      }
      o.isTemplateElement = true;
      o.templateElement = { description: attrs["data-te-description"] || "", minChars: min, maxChars: max };
    }
    if (attrs["data-variable"])
      o.fillVariableConfig = { type: "solid", variable: attrs["data-variable"], alpha: parseFloat(attrs["data-variable-alpha"] || "1") };
    return o;
  };
  const teImg = (attrs) => {
    const o = {};
    if ("data-template-element" in attrs && !("data-static" in attrs)) {
      o.isTemplateElement = true;
      o.templateElement = { description: attrs["data-te-description"] || "",
        removeBackground: attrs["data-te-remove-bg"] === "true" };
    }
    return o;
  };
  const textboxOf = (n, common) => {
    let text = ""; const styles = {}; let line = 0, col = 0;
    const baseFill = rgb2hex(n.color);
    for (const run of n.runs) {
      const runFill = rgb2hex(run.color);
      let t = n.upper ? run.t.toUpperCase() : run.t;
      for (const ch of t) {
        if (ch === "\n") { line++; col = 0; text += ch; continue; }
        if (runFill && runFill !== baseFill) (styles[line] ||= {})[col] = { fill: runFill };
        text += ch; col++;
      }
    }
    return { type: "textbox", name: "Texto", ...common,
      text: text.replace(/^\s+|\s+$/g, ""), width: Math.ceil(n.w) + 4,
      fill: baseFill, fontSize: Math.round(n.fs), fontWeight: n.weight,
      fontFamily: n.family, textAlign: n.align,
      lineHeight: Math.round(n.lineH * 100) / 100,
      ...(n.spacing ? { charSpacing: Math.max(-150, Math.round((n.spacing / n.fs) * 1000)) } : {}),
      styles, ...teText(n.attrs, n.id) };
  };

  function gradientFromCss(css, w, h) {
    const stops = [...css.matchAll(/rgba?\([^)]+\)/g)].map((m) => m[0]);
    const angM = css.match(/linear-gradient\(\s*([-\d.]+)deg/);
    const ang = angM ? parseFloat(angM[1]) : 180;
    const rad = ((ang - 90) * Math.PI) / 180;
    const x = Math.cos(rad), y = Math.sin(rad);
    return { type: "linear", gradientUnits: "pixels", gradientTransform: null, offsetX: 0, offsetY: 0,
      coords: { x1: w / 2 - (x * w) / 2, y1: h / 2 - (y * h) / 2, x2: w / 2 + (x * w) / 2, y2: h / 2 + (y * h) / 2 },
      colorStops: stops.map((c, idx) => {
        const m = c.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
        return { offset: idx / Math.max(1, stops.length - 1), color: `rgba(${m[1]},${m[2]},${m[3]},${m[4] !== undefined ? m[4] : 1})` };
      }) };
  }

  data.slides.forEach((sl, i) => {
    const objects = [];
    for (const n of sl.nodes) {
      emittedIds.add(n.id);
      const common = { left: Math.round(n.cx * 100) / 100, top: Math.round(n.cy * 100) / 100,
        originX: "center", originY: "center", elId: n.id,
        ...(n.angle ? { angle: n.angle } : {}), ...(n.opacity < 1 ? { opacity: n.opacity } : {}) };
      if (n.kind === "img") {
        const rp = n.circle ? 50 : pct(n.radiusPx, n.w, n.h);
        objects.push({ type: "ClippableImage", name: "Imagem", ...common, src: inlineSrc(n.src, n.id),
          width: Math.round(n.w * 100) / 100, height: Math.round(n.h * 100) / 100,
          topLeft: rp, topRight: rp, bottomRight: rp, bottomLeft: rp,
          crossOrigin: "anonymous",
          ...(n.cutout ? { cutout: true } : {}),
          imageType: n.attrs["data-image-type"] || n.attrs["data-slot"] || null,
          ...teImg(n.attrs) });
        if (!n.attrs["data-image-type"] && !n.attrs["data-slot"]) {
          console.error(`REJEITADO — slide-${i + 1} · ${n.id}: imagem sem data-image-type/data-slot`);
          process.exit(1);
        }
      } else if (n.kind === "shape") {
        const rr = (n.radiiPx || [n.radiusPx, n.radiusPx, n.radiusPx, n.radiusPx]).map((v) => pct(v, n.w, n.h));
        const shapeFill = n.bgImg ? gradientFromCss(n.bgImg, n.w, n.h) : (rgb2hex(n.bg) || "transparent");
        const gradVar = n.attrs["data-overlay-gradient"];
        const sh = n.shadow && n.shadow.match(/rgba?\([^)]+\)\s+([-\d.]+)px\s+([-\d.]+)px\s+([-\d.]+)px/);
        objects.push({ type: "roundedRect", name: "Forma", ...common,
          width: Math.round(n.w), height: Math.round(n.h),
          fill: shapeFill,
          ...(sh ? { shadow: { color: (n.shadow.match(/rgba?\([^)]+\)/) || ["rgba(0,0,0,0.28)"])[0],
            blur: parseFloat(sh[3]), offsetX: parseFloat(sh[1]), offsetY: parseFloat(sh[2]) } } : {}),
          ...(n.borderColor ? { stroke: rgb2hex(n.borderColor), strokeWidth: n.borderW } : {}),
          topLeft: rr[0], topRight: rr[1], bottomRight: rr[2], bottomLeft: rr[3],
          ...(gradVar && shapeFill && shapeFill.colorStops ? {
            fillVariableConfig: { type: "gradient",
              colorStops: shapeFill.colorStops.map((cs) => ({ variable: gradVar,
                alpha: (cs.color.match(/rgba\([^)]+,\s*([\d.]+)\)/) || [0, "1"])[1] * 1 })) },
          } : ("data-variable" in n.attrs ? { fillVariableConfig: { type: "solid", variable: n.attrs["data-variable"], alpha: 1 } } : {})) });
      } else if (n.kind === "chip") {
        const rp = pct(n.radiusPx, n.w, n.h);
        const hasFill = rgb2hex(n.bg);
        objects.push({ type: "roundedRect", name: "Forma", ...common,
          width: Math.round(n.w), height: Math.round(n.h),
          fill: hasFill || "transparent",
          ...(n.borderColor ? { stroke: rgb2hex(n.borderColor), strokeWidth: n.borderW } : {}),
          topLeft: rp, topRight: rp, bottomRight: rp, bottomLeft: rp,
          ...("data-variable" in n.attrs ? { [hasFill ? "fillVariableConfig" : "strokeVariableConfig"]: { type: "solid", variable: n.attrs["data-variable"], alpha: 1 } } : {}) });
        // o data-variable pertence ao RECT do chip; o texto nunca herda
        const chipAttrs = { ...n.attrs };
        delete chipAttrs["data-variable"];
        objects.push(textboxOf({ ...n, attrs: chipAttrs, w: n.w - n.borderW * 2 - 8, align: "center",
          runs: [{ t: n.text, color: n.color }] }, { ...common }));
      } else {
        objects.push(textboxOf(n, common));
      }
    }
    const doc = { version: "5.5.2", background: rgb2hex(sl.bg) || "#FFFFFF", objects,
      _meta: { slideIndex: i, role: sl.role, sourceClaudeDesign: `convert:${packSlug}:${data.templateName || "template"}` } };
    if (sl.secVar && sl.secVarTarget === "background")
      doc.backgroundVariableConfig = { type: "solid", variable: sl.secVar, alpha: 1 };
    fs.writeFileSync(path.join(outDir, `slide-${i + 1}.json`), JSON.stringify(doc), "utf-8");
    console.log(`slide-${i + 1}.json: ${objects.length} objetos · bg ${doc.background}`);
  });

  // lei de conservação — todo data-el-id da fita vive em >=1 slide JSON
  const lost = [...htmlIds].filter((id) => !emittedIds.has(id));
  if (lost.length) {
    console.error(`REJEITADO — conservação: ${lost.length} data-el-id sem objeto no JSON: ${lost.slice(0, 8).join(", ")}`);
    process.exit(1);
  }

  fs.writeFileSync(path.join(outDir, "manifest.json"), JSON.stringify({
    templateName: data.templateName || packSlug, slug: slug || data.templateName || packSlug,
    segment: data.segment, fonts: data.fonts, pack: packSlug, packVersion: pack.version,
    slides: data.slides.map((sl, i) => ({ file: `slide-${i + 1}.json`, width: sl.W, height: sl.H, role: sl.role })),
    detectedColors: {
      primary: (pack.variables && pack.variables.primary) || pack.tokens.accent || null,
      secondary: (pack.variables && pack.variables.secondary) || null,
    },
    generatedBy: "engine/convert.js",
  }, null, 2), "utf-8");
  console.log("manifest.json ok");

  try {
    execFileSync("node", [path.join(REPO, "engine", "tools", "center-clippable-images.js"), outDir], { stdio: "inherit" });
  } catch (e) {
    console.error("center-clippable-images falhou — crop incompleto, corrija antes de finalizar");
    process.exit(1);
  }
})();
