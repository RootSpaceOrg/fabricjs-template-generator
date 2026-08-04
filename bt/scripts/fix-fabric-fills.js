#!/usr/bin/env node
/**
 * Corrige fills dos slide-N.json lendo as cores REAIS do template.html (computed
 * styles via Playwright). Embrião do converter determinístico: casa textboxes por
 * conteúdo de texto e rects por geometria, e aplica cor/fundo verdadeiros.
 *
 * Uso: node bt/scripts/fix-fabric-fills.js <template.html> <output-dir>
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const norm = (s) => (s || "").replace(/\s+/g, " ").trim().toUpperCase().slice(0, 40);

(async () => {
  const [tpl, outDir] = process.argv.slice(2);
  if (!tpl || !outDir) {
    console.error("uso: node fix-fabric-fills.js <template.html> <output-dir>");
    process.exit(2);
  }
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 1500 } });
  await page.goto("file://" + path.resolve(tpl), { waitUntil: "networkidle" });

  const slides = await page.evaluate(() => {
    const out = [];
    for (const sec of document.querySelectorAll("section.slide")) {
      const sr = sec.getBoundingClientRect();
      const cs = getComputedStyle(sec);
      const texts = [];
      const shapes = [];
      const walk = (el) => {
        const s = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        const ownText = [...el.childNodes]
          .filter((n) => n.nodeType === 3)
          .map((n) => n.textContent)
          .join(" ");
        if (ownText.trim())
          texts.push({ text: ownText, color: s.color });
        else if (el.children.length && el.innerText && el.innerText.trim() && el.tagName !== "SECTION") {
          // container cujo texto vem de filhos — ainda útil como fallback
          texts.push({ text: el.innerText, color: s.color, weak: true });
        }
        if (s.backgroundColor && s.backgroundColor !== "rgba(0, 0, 0, 0)" && el.tagName !== "IMG")
          shapes.push({
            left: r.left - sr.left + r.width / 2,
            top: r.top - sr.top + r.height / 2,
            w: r.width, h: r.height, bg: s.backgroundColor,
          });
        for (const c of el.children) walk(c);
      };
      for (const c of sec.children) walk(c);
      out.push({ bg: cs.backgroundColor, texts, shapes });
    }
    return out;
  });
  await browser.close();

  const rgb2hex = (c) => {
    const m = c.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if (!m) return c;
    return "#" + [m[1], m[2], m[3]].map((v) => (+v).toString(16).padStart(2, "0")).join("").toUpperCase();
  };

  const files = fs.readdirSync(outDir).filter((f) => /^slide-\d+\.json$/.test(f))
    .sort((a, b) => parseInt(a.match(/\d+/)) - parseInt(b.match(/\d+/)));
  const transparent = (c) => !c || /rgba\(\s*0,\s*0,\s*0,\s*0\s*\)/.test(c) || c === "transparent";

  files.forEach((f, i) => {
    const info = slides[i];
    if (!info) return;
    const doc = JSON.parse(fs.readFileSync(path.join(outDir, f), "utf-8"));
    let fixedT = 0, fixedS = 0;
    // fundo real: root da section OU (root transparente) o shape full-size (div de bg do montador)
    let slideBg = info.bg;
    if (transparent(slideBg)) {
      const full = info.shapes.find((s) => s.w >= 1070 && s.h >= 1340);
      slideBg = full ? full.bg : "rgb(255,255,255)";
    }
    info.bg = slideBg;
    doc.background = rgb2hex(slideBg);
    for (const o of doc.objects || []) {
      if (o.type === "textbox" && o.text) {
        const key = norm(o.text);
        const hit = info.texts.find((t) => norm(t.text).startsWith(key) || key.startsWith(norm(t.text)));
        if (hit) { o.fill = rgb2hex(hit.color); fixedT++; }
      } else if ((o.type === "roundedRect" || o.type === "rect") && o.width && o.height) {
        // full-canvas = fundo do slide
        if (o.width >= 1070 && o.height >= 1340) { o.fill = rgb2hex(info.bg); fixedS++; continue; }
        const hit = info.shapes.find((s) =>
          Math.abs(s.w - o.width) < 12 && Math.abs(s.h - o.height) < 12 &&
          Math.abs(s.left - o.left) < 20 && Math.abs(s.top - o.top) < 20
        ) || info.shapes.find((s) => Math.abs(s.w - o.width) < 12 && Math.abs(s.h - o.height) < 12);
        if (hit) { o.fill = rgb2hex(hit.bg); fixedS++; }
      }
    }
    fs.writeFileSync(path.join(outDir, f), JSON.stringify(doc), "utf-8");
    console.log(`${f}: bg=${doc.background} · ${fixedT} textos + ${fixedS} formas corrigidos`);
  });
})();
