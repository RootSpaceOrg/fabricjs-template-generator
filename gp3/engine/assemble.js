#!/usr/bin/env node
/**
 * GP3 — assembler mecânico: slides isolados → fita de preview.
 *
 * Lê <slides-dir>/slide-N.html, monta strip.html (sections lado a lado, tokens
 * do pack injetados) e renderiza strip.png + slide-N.png via Playwright.
 *
 * Uso: node gp3/engine/assemble.js <slides-dir> [outdir=<slides-dir>/..]
 *
 * ponytail: camada de costura (watermark cruzando fronteira) fica fora da v1 —
 * adicionar quando o pack 1 certificar e a costura virar requisito real.
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const REPO = path.resolve(__dirname, "..", "..");

(async () => {
  const [slidesDir, outArg] = process.argv.slice(2);
  if (!slidesDir) { console.error("uso: node gp3/engine/assemble.js <slides-dir> [outdir]"); process.exit(2); }
  const outDir = outArg || path.resolve(slidesDir, "..");
  const files = fs.readdirSync(slidesDir).filter((f) => /^slide-\d+\.html$/.test(f))
    .sort((a, b) => parseInt(a.match(/\d+/)[0]) - parseInt(b.match(/\d+/)[0]));
  if (!files.length) { console.error(`nenhum slide-N.html em ${slidesDir}`); process.exit(2); }

  const htmls = files.map((f) => fs.readFileSync(path.join(slidesDir, f), "utf-8"));
  const packSlug = (htmls[0].match(/data-pack="([^"]+)"/) || [])[1];
  if (!packSlug) { console.error("REJEITADO — <html> sem data-pack"); process.exit(1); }
  const pack = JSON.parse(fs.readFileSync(path.join(REPO, "gp3", "packs", packSlug, "pack.json"), "utf-8"));
  const tokensCss = ":root{" + Object.entries(pack.tokens).map(([k, v]) => `--${k}:${v}`).join(";") + "}";

  const sections = htmls.map((h) => {
    const m = h.match(/<section[\s\S]*<\/section>/);
    if (!m) { console.error("slide sem <section class=\"slide\">"); process.exit(1); }
    return m[0];
  });
  const head = (htmls[0].match(/<html[^>]*>/) || ["<html>"])[0];
  const dsHref = "file:///" + path.join(REPO, "gp3", "engine", "design-system.css").replace(/\\/g, "/");
  const strip = `<!doctype html>${head}<head><meta charset="utf-8">
<link rel="stylesheet" href="${dsHref}">
${pack.fonts && pack.fonts.css ? `<link rel="stylesheet" href="${pack.fonts.css}">` : ""}
<style>${tokensCss} body{margin:0} #strip{display:flex;width:max-content}</style>
</head><body><div id="strip">${sections.join("\n")}</div></body></html>`;
  const stripPath = path.join(outDir, "strip.html");
  fs.writeFileSync(stripPath, strip, "utf-8");

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 1500 } });
  await page.goto("file://" + path.resolve(stripPath), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.locator("#strip").screenshot({ path: path.join(outDir, "strip.png") });
  const secs = page.locator("section.slide");
  for (let i = 0; i < files.length; i++)
    await secs.nth(i).screenshot({ path: path.join(outDir, `slide-${i + 1}.png`) });
  await browser.close();
  console.log(`strip.png + ${files.length} slide-N.png em ${outDir}`);
})();
