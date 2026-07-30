#!/usr/bin/env node
/**
 * Fatia um strip panorâmico em sections .slide para o pipeline bt.
 *
 * Entrada: strip.html com UM <div class="strip" data-slides="N"
 *          data-slide-width="1080" data-slide-height="1350"> contendo filhos
 *          diretos absolutamente posicionados com `left`/`top` inline em px.
 * Saída:  <outdir>/template.html — N <section class="slide"> (contrato do
 *          converter), cada elemento reposicionado por -i*W; elementos que
 *          cruzam a fronteira aparecem nos dois slides (offsets diferentes).
 *          <outdir>/strip.png — screenshot da fita inteira (judge de continuidade).
 *
 * Uso: node bt/scripts/slice-strip.js <strip.html> <outdir>
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

function shiftLeft(html, newLeft) {
  const px = `left:${Math.round(newLeft * 100) / 100}px`;
  if (/left\s*:\s*-?[\d.]+px/.test(html)) {
    return html.replace(/left\s*:\s*-?[\d.]+px/, px);
  }
  if (/style\s*=\s*"/.test(html)) {
    return html.replace(/style\s*=\s*"/, `style="position:absolute;${px};`);
  }
  return html.replace(/^<(\w+)/, `<$1 style="position:absolute;${px}"`);
}

(async () => {
  const [stripPath, outDir] = process.argv.slice(2);
  if (!stripPath || !outDir) {
    console.error("uso: node slice-strip.js <strip.html> <outdir>");
    process.exit(2);
  }
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 1500 } });
  await page.goto("file://" + path.resolve(stripPath), { waitUntil: "networkidle" });

  const meta = await page.evaluate(() => {
    const s = document.querySelector(".strip");
    if (!s) return null;
    const W = +s.dataset.slideWidth || 1080;
    const H = +s.dataset.slideHeight || 1350;
    const N = +s.dataset.slides || Math.round(s.getBoundingClientRect().width / W);
    const sr = s.getBoundingClientRect();
    const kids = [...s.children].map((el) => {
      const r = el.getBoundingClientRect();
      return {
        html: el.outerHTML,
        left: r.left - sr.left,
        width: r.width,
      };
    });
    return { W, H, N, kids, head: document.head.innerHTML, htmlAttrs: document.documentElement.outerHTML.match(/^<html[^>]*>/)[0] };
  });

  if (!meta) {
    console.error("ERRO: nenhum <div class='.strip'> encontrado em " + stripPath);
    await browser.close();
    process.exit(1);
  }

  const sections = [];
  for (let i = 0; i < meta.N; i++) {
    const x0 = i * meta.W;
    const els = meta.kids.filter((k) => k.left < x0 + meta.W && k.left + k.width > x0);
    const inner = els.map((k) => "  " + shiftLeft(k.html, k.left - x0)).join("\n");
    sections.push(
      `<section class="slide" data-width="${meta.W}" data-height="${meta.H}" ` +
        `style="position:relative;width:${meta.W}px;height:${meta.H}px;overflow:hidden">\n${inner}\n</section>`
    );
  }

  const out =
    `<!DOCTYPE html>\n${meta.htmlAttrs}\n<head>\n${meta.head}\n</head>\n<body>\n` +
    sections.join("\n") +
    `\n</body>\n</html>\n`;
  fs.writeFileSync(path.join(outDir, "template.html"), out, "utf-8");

  await page.locator(".strip").screenshot({ path: path.join(outDir, "strip.png") });
  await browser.close();

  console.log(`OK: ${meta.N} slides → ${path.join(outDir, "template.html")}`);
  console.log(`strip: ${path.join(outDir, "strip.png")}`);
})();
