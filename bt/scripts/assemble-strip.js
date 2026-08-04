#!/usr/bin/env node
/**
 * Monta a fita panorâmica a partir de slides APROVADOS — montagem é aritmética,
 * não design. Inverso do slice-strip.js.
 *
 * Cada slide de entrada: html isolado 1080×1350 (uma <section class="slide"> ou
 * body com filhos absolutos, left/top inline). O montador desloca cada elemento
 * por +i*1080 e emite o .strip. Costuras (watermarks cruzando fronteiras) vêm de
 * um seams.html opcional com elementos já em coordenadas DE FITA — copiados sem
 * deslocamento, atrás do conteúdo dos slides.
 *
 * Uso: node bt/scripts/assemble-strip.js <outdir> <slide1.html> <slide2.html> ... [--seams seams.html]
 * Emite: <outdir>/strip.html + <outdir>/strip.png
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

function shiftLeft(html, newLeft) {
  const px = `left:${Math.round(newLeft * 100) / 100}px`;
  if (/left\s*:\s*-?[\d.]+px/.test(html)) return html.replace(/left\s*:\s*-?[\d.]+px/, px);
  if (/style\s*=\s*"/.test(html)) return html.replace(/style\s*=\s*"/, `style="position:absolute;${px};`);
  return html.replace(/^<(\w+)/, `<$1 style="position:absolute;${px}"`);
}

async function readSlide(page, file) {
  await page.goto("file://" + path.resolve(file), { waitUntil: "networkidle" });
  return page.evaluate(() => {
    const root = document.querySelector(".slide") || document.body;
    const rr = root.getBoundingClientRect();
    const cs = getComputedStyle(root);
    const bg = {
      color: cs.backgroundColor,
      image: cs.backgroundImage !== "none" ? cs.backgroundImage : null,
    };
    const kids = [...root.children].map((el) => {
      const r = el.getBoundingClientRect();
      return { html: el.outerHTML, left: r.left - rr.left };
    });
    return { kids, bg, head: document.head.innerHTML,
             htmlAttrs: (document.documentElement.outerHTML.match(/^<html[^>]*>/) || ["<html>"])[0] };
  });
}

(async () => {
  const args = process.argv.slice(2);
  const seamsIdx = args.indexOf("--seams");
  let seamsFile = null;
  if (seamsIdx >= 0) { seamsFile = args[seamsIdx + 1]; args.splice(seamsIdx, 2); }
  const [outDir, ...slides] = args;
  if (!outDir || slides.length < 2) {
    console.error("uso: node assemble-strip.js <outdir> <slide1.html> <slide2.html> ... [--seams seams.html]");
    process.exit(2);
  }
  const W = 1080, H = 1350;
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 1500 } });

  let head = null, htmlAttrs = null;
  const bgs = [];
  const parts = [];
  for (let i = 0; i < slides.length; i++) {
    const s = await readSlide(page, slides[i]);
    if (!head) { head = s.head; htmlAttrs = s.htmlAttrs; }
    // fundo do root do slide vira retângulo da janela — preserva o ritmo tonal
    // e isola o fundo de cada slide na fita (nada de contaminação entre janelas)
    const bgStyle = `background-color:${s.bg.color}` + (s.bg.image ? `;background-image:${s.bg.image};background-size:cover` : "");
    bgs.push(`<div data-slide-bg="${i + 1}" style="position:absolute;left:${i * W}px;top:0;width:${W}px;height:${H}px;${bgStyle}"></div>`);
    for (const k of s.kids) parts.push(shiftLeft(k.html, k.left + i * W));
    console.log(`slide ${i + 1}: ${s.kids.length} elementos, bg ${s.bg.color} <- ${path.basename(slides[i])}`);
  }

  let seams = "";
  if (seamsFile) {
    const s = await readSlide(page, seamsFile);
    seams = s.kids.map((k) => k.html).join("\n");
    console.log(`seams: ${s.kids.length} elementos (coordenadas de fita, sem deslocamento)`);
  }

  const strip =
    `<!DOCTYPE html>\n${htmlAttrs}\n<head>\n${head}\n</head>\n<body style="margin:0">\n` +
    `<div class="strip" data-slides="${slides.length}" data-slide-width="${W}" data-slide-height="${H}" ` +
    `style="position:relative;width:${slides.length * W}px;height:${H}px;overflow:hidden">\n` +
    bgs.join("\n") + "\n" + seams + "\n" + parts.join("\n") + `\n</div>\n</body>\n</html>\n`;
  const out = path.join(outDir, "strip.html");
  fs.writeFileSync(out, strip, "utf-8");

  await page.goto("file://" + path.resolve(out), { waitUntil: "networkidle" });
  await page.locator(".strip").screenshot({ path: path.join(outDir, "strip.png") });
  await browser.close();
  console.log(`OK: ${out} (${slides.length} slides) + strip.png`);
})();
