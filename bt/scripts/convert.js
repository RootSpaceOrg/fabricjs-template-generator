#!/usr/bin/env node
/**
 * Conversor determinístico HTML → Fabric JSON (contrato: bt/CONVERTER.md).
 *
 * O agente desenha; este script converte SEM consultar ninguém. HTML fora da
 * whitelist é REJEITADO com erro apontando o data-el-id — a correção é sempre
 * regenerar o HTML, nunca editar o JSON.
 *
 * Uso: node bt/scripts/convert.js <template.html> <outdir> [--auto-ids]
 *   --auto-ids: atribui data-el-id em ordem DOM (ponte para HTMLs pré-lei).
 * Saída: <outdir>/slide-N.json + manifest.json · exit 1 se houver rejeições.
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const rgb2hex = (c) => {
  const m = (c || "").match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
  if (!m) return c;
  if (m[4] !== undefined && parseFloat(m[4]) === 0) return null;
  return "#" + [m[1], m[2], m[3]].map((v) => (+v).toString(16).padStart(2, "0")).join("").toUpperCase();
};

(async () => {
  const args = process.argv.slice(2);
  const autoIds = args.includes("--auto-ids");
  const [tpl, outDir] = args.filter((a) => !a.startsWith("--"));
  if (!tpl || !outDir) { console.error("uso: node convert.js <template.html> <outdir> [--auto-ids]"); process.exit(2); }
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 1500 } });
  await page.goto("file://" + path.resolve(tpl), { waitUntil: "networkidle" });

  const data = await page.evaluate((autoIds) => {
    const FORBIDDEN_TAGS = new Set(["SVG", "CANVAS", "VIDEO", "IFRAME", "OBJECT", "EMBED"]);
    let seq = 0;
    const slides = [];
    const meta = {
      templateName: document.documentElement.getAttribute("data-template-name") || "",
      segment: document.documentElement.getAttribute("data-segment") || "",
      fonts: (document.querySelector('meta[name="hm-fonts"]') || {}).content || "",
    };
    for (const sec of document.querySelectorAll("section.slide")) {
      const sr = sec.getBoundingClientRect();
      const W = parseInt(sec.dataset.width) || 1080, H = parseInt(sec.dataset.height) || 1350;
      const nodes = [], rejects = [];
      let slideBg = getComputedStyle(sec).backgroundColor;

      const attrs = (el) => {
        const a = {};
        for (const at of el.attributes) if (at.name.startsWith("data-")) a[at.name] = at.value;
        return a;
      };
      const angleOf = (s) => {
        const m = (s.transform || "").match(/matrix\(([-\d.]+),\s*([-\d.]+)/);
        return m ? Math.round(Math.atan2(parseFloat(m[2]), parseFloat(m[1])) * 180 / Math.PI * 100) / 100 : 0;
      };

      const walk = (el) => {
        const s = getComputedStyle(el);
        if (s.display === "none" || s.visibility === "hidden") return;
        const r = el.getBoundingClientRect();
        const box = { cx: r.left - sr.left + r.width / 2, cy: r.top - sr.top + r.height / 2, w: r.width, h: r.height };
        let id = el.getAttribute("data-el-id");
        if (!id && autoIds) { id = "e" + (++seq); el.setAttribute("data-el-id", id); }

        if (FORBIDDEN_TAGS.has(el.tagName)) { rejects.push({ id, reason: `tag proibida <${el.tagName.toLowerCase()}>` }); return; }
        if (s.mixBlendMode !== "normal" || (s.backdropFilter && s.backdropFilter !== "none"))
          rejects.push({ id, reason: "mix-blend-mode/backdrop-filter proibidos" });

        const ownText = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join("");
        const hasOwnText = !!ownText.trim();
        const bg = s.backgroundColor;
        const bgImg = s.backgroundImage !== "none" ? s.backgroundImage : null;
        const hasBg = (bg && !/rgba\(\s*0,\s*0,\s*0,\s*0\s*\)/.test(bg)) || bgImg;
        const isImg = el.tagName === "IMG";
        const visible = isImg || hasOwnText || hasBg;

        if (visible && !id) { rejects.push({ id: el.tagName + "?", reason: "elemento visível sem data-el-id" }); return; }
        if (bgImg && !isImg) {
          if (/url\(/.test(bgImg)) { rejects.push({ id, reason: "background-image:url() — use <img>" }); return; }
          if (/(radial|conic)-gradient/.test(bgImg)) { rejects.push({ id, reason: "gradiente radial/conic não suportado" }); return; }
        }
        if (hasOwnText && s.writingMode && s.writingMode !== "horizontal-tb")
          rejects.push({ id, reason: "writing-mode vertical — use transform: rotate" });

        // fundo full-slide → background do canvas (1→0)
        if (!isImg && !hasOwnText && hasBg && box.w >= W - 12 && box.h >= H - 12) {
          slideBg = bg; return;
        }

        const base = {
          id, ...box, angle: angleOf(s), opacity: parseFloat(s.opacity),
          attrs: attrs(el),
        };

        if (isImg) {
          nodes.push({ kind: "img", ...base, src: el.currentSrc || el.src,
            radius: parseFloat(s.borderTopLeftRadius) || 0 });
        } else {
          if (hasBg) nodes.push({ kind: "shape", ...base, bg, bgImg,
            radius: parseFloat(s.borderTopLeftRadius) || 0 });
          if (hasOwnText || (el.innerText || "").trim() && ![...el.children].some((c) => (c.innerText || "").trim() && c.getBoundingClientRect().height < r.height * 0.9)) {
            // texto próprio OU container cujo texto vem só de spans inline
          }
          if (hasOwnText || ([...el.children].length && [...el.children].every((c) => c.tagName === "SPAN" || c.tagName === "BR") && (el.innerText || "").trim())) {
            const runs = [];
            for (const n of el.childNodes) {
              if (n.nodeType === 3 && n.textContent) runs.push({ t: n.textContent, color: s.color, weight: s.fontWeight });
              else if (n.nodeType === 1 && n.tagName === "BR") runs.push({ t: "\n", color: s.color, weight: s.fontWeight });
              else if (n.nodeType === 1) {
                const cs = getComputedStyle(n);
                runs.push({ t: n.innerText || n.textContent || "", color: cs.color, weight: cs.fontWeight, varAttr: n.getAttribute && n.getAttribute("data-variable") });
              }
            }
            nodes.push({ kind: "text", ...base, runs,
              fs: parseFloat(s.fontSize), weight: s.fontWeight,
              family: s.fontFamily.split(",")[0].replace(/["']/g, "").trim(),
              color: s.color, align: s.textAlign === "start" ? "left" : s.textAlign,
              spacing: parseFloat(s.letterSpacing) || 0,
              lineH: s.lineHeight === "normal" ? 1.16 : parseFloat(s.lineHeight) / parseFloat(s.fontSize) });
            return; // filhos (spans) já consumidos
          }
        }
        for (const c of el.children) walk(c);
      };
      for (const c of sec.children) walk(c);
      slides.push({ W, H, bg: slideBg, nodes, rejects,
        secVar: sec.getAttribute("data-variable"), secVarTarget: sec.getAttribute("data-variable-target") });
    }
    return { meta, slides };
  }, autoIds);
  await browser.close();

  // ---- montagem dos objetos ----
  const allRejects = [];
  const varColors = {};
  data.slides.forEach((sl, i) => {
    sl.rejects.forEach((rj) => allRejects.push({ slide: i + 1, ...rj }));
  });
  if (allRejects.length) {
    console.error(`REJEITADO — ${allRejects.length} violação(ões) do contrato (bt/CONVERTER.md):`);
    for (const r of allRejects) console.error(`  slide ${r.slide} · ${r.id}: ${r.reason}`);
    process.exit(1);
  }

  const teFields = (attrs) => {
    const o = {};
    if ("data-template-element" in attrs && !("data-static" in attrs)) {
      o.isTemplateElement = true;
      o.templateElement = { description: attrs["data-te-description"] || "" };
      if (attrs["data-te-max-chars"]) o.templateElement.maxChars = parseInt(attrs["data-te-max-chars"]);
      if (attrs["data-te-min-chars"]) o.templateElement.minChars = parseInt(attrs["data-te-min-chars"]);
    }
    if (attrs["data-image-type"]) o.imageType = attrs["data-image-type"];
    if (attrs["data-text-type"]) o.textType = attrs["data-text-type"];
    if (attrs["data-variable"]) {
      o.fillVariableConfig = { type: "solid", variable: attrs["data-variable"],
        alpha: parseFloat(attrs["data-variable-alpha"] || "1") };
    }
    return o;
  };

  data.slides.forEach((sl, i) => {
    const objects = [];
    for (const n of sl.nodes) {
      const common = { name: n.kind === "img" ? "Imagem" : n.kind === "shape" ? "Forma" : "Texto",
        left: Math.round(n.cx * 100) / 100, top: Math.round(n.cy * 100) / 100,
        originX: "center", originY: "center", btElId: n.id,
        ...(n.angle ? { angle: n.angle } : {}), ...(n.opacity < 1 ? { opacity: n.opacity } : {}) };
      if (n.kind === "img") {
        objects.push({ type: "ClippableImage", ...common, src: n.src,
          width: Math.round(n.w * 100) / 100, height: Math.round(n.h * 100) / 100,
          topLeft: n.radius, topRight: n.radius, bottomRight: n.radius, bottomLeft: n.radius,
          crossOrigin: "anonymous", ...teFields(n.attrs) });
      } else if (n.kind === "shape") {
        const fill = n.bgImg ? gradientFromCss(n.bgImg, n.w, n.h) : rgb2hex(n.bg);
        const te = teFields(n.attrs);
        if (te.fillVariableConfig && rgb2hex(n.bg)) varColors[te.fillVariableConfig.variable] ||= rgb2hex(n.bg);
        objects.push({ type: "roundedRect", ...common, width: Math.round(n.w), height: Math.round(n.h),
          fill, topLeft: n.radius, topRight: n.radius, bottomRight: n.radius, bottomLeft: n.radius, ...te });
      } else {
        // texto: base + styles por char onde difere
        let text = ""; const styles = {}; let line = 0, col = 0;
        const baseFill = rgb2hex(n.color);
        for (const run of n.runs) {
          const runFill = rgb2hex(run.color);
          for (const ch of run.t) {
            if (ch === "\n") { line++; col = 0; text += ch; continue; }
            if (runFill && runFill !== baseFill) {
              (styles[line] ||= {})[col] = { fill: runFill };
            }
            text += ch; col++;
          }
        }
        const te = teFields(n.attrs);
        if (te.fillVariableConfig && baseFill) varColors[te.fillVariableConfig.variable] ||= baseFill;
        const weight = /^\d+$/.test(n.weight) ? parseInt(n.weight) : n.weight;
        objects.push({ type: "textbox", ...common, text: text.replace(/\s+$/g, "").replace(/^\s+/g, ""),
          width: Math.ceil(n.w) + 4, fill: baseFill, fontSize: Math.round(n.fs),
          fontWeight: weight, fontFamily: n.family, textAlign: n.align,
          lineHeight: Math.round(n.lineH * 100) / 100,
          ...(n.spacing ? { charSpacing: Math.round((n.spacing / n.fs) * 1000) } : {}),
          styles, ...te });
      }
    }
    const doc = { version: "5.3.0", background: rgb2hex(sl.bg) || "#FFFFFF", objects,
      _meta: { slideIndex: i, sourceClaudeDesign: "bt-convert:" + (data.meta.templateName || "template") } };
    if (sl.secVar && sl.secVarTarget === "background")
      doc.backgroundVariableConfig = { type: "solid", variable: sl.secVar, alpha: 1 };
    fs.writeFileSync(path.join(outDir, `slide-${i + 1}.json`), JSON.stringify(doc), "utf-8");
    console.log(`slide-${i + 1}.json: ${objects.length} objetos · bg ${doc.background}`);
  });

  function gradientFromCss(css, w, h) {
    const stops = [...css.matchAll(/rgba?\([^)]+\)/g)].map((m) => m[0]);
    if (stops.length < 2) return rgb2hex(stops[0] || "rgb(0,0,0)");
    const angM = css.match(/linear-gradient\(\s*([-\d.]+)deg/);
    const ang = angM ? parseFloat(angM[1]) : 180;
    const rad = ((ang - 90) * Math.PI) / 180;
    const x = Math.cos(rad), y = Math.sin(rad);
    return { type: "linear",
      coords: { x1: w / 2 - (x * w) / 2, y1: h / 2 - (y * h) / 2, x2: w / 2 + (x * w) / 2, y2: h / 2 + (y * h) / 2 },
      colorStops: stops.map((c, idx) => {
        const m = c.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
        return { offset: idx / (stops.length - 1),
          color: `rgba(${m[1]},${m[2]},${m[3]},${m[4] !== undefined ? m[4] : 1})` };
      }) };
  }

  fs.writeFileSync(path.join(outDir, "manifest.json"), JSON.stringify({
    templateName: data.meta.templateName, segment: data.meta.segment, fonts: data.meta.fonts,
    slides: data.slides.length, width: data.slides[0]?.W || 1080, height: data.slides[0]?.H || 1350,
    detectedColors: { primary: varColors.primary || null, secondary: varColors.secondary || null },
    generatedBy: "bt/scripts/convert.js",
  }, null, 2), "utf-8");
  console.log(`manifest.json · detectedColors ${JSON.stringify(varColors)}`);
})();
