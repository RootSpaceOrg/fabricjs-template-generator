#!/usr/bin/env node
/**
 * Assembler mecânico: fita.html → strip.png + slide-N.png (preview).
 *
 * A fita já É o layout final (N seções lado a lado + .fita-layer de
 * travessias). Aqui só se injetam tokens/fontes do pack e renderiza.
 *
 * Uso: node engine/assemble.js <run-dir|fita.html> [outdir=<run-dir>]
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const REPO = path.resolve(__dirname, "..");

(async () => {
  const [inArg, outArg] = process.argv.slice(2);
  if (!inArg) { console.error("uso: node engine/assemble.js <run-dir|fita.html> [outdir]"); process.exit(2); }
  const fitaPath = inArg.endsWith(".html") ? path.resolve(inArg) : path.resolve(inArg, "fita.html");
  if (!fs.existsSync(fitaPath)) { console.error(`fita.html não encontrada: ${fitaPath}`); process.exit(2); }
  const outDir = outArg || path.dirname(fitaPath);

  const html = fs.readFileSync(fitaPath, "utf-8");
  const packSlug = (html.match(/data-pack="([^"]+)"/) || [])[1];
  if (!packSlug) { console.error("REJEITADO — fita sem data-pack"); process.exit(1); }
  const pack = JSON.parse(fs.readFileSync(path.join(REPO, "packs", packSlug, "pack.json"), "utf-8"));
  // --primary=#HEX simula OUTRA marca no render: os tokens do pack são só
  // placeholder, e quem tem data-variable troca de cor na plataforma. Serve
  // para provar que a peça funciona com marcas diferentes (PACKS.md §4).
  const argPrimary = (process.argv.find((a) => a.startsWith("--primary=")) || "").split("=")[1];
  const tokens = argPrimary ? { ...pack.tokens, accent: argPrimary } : pack.tokens;
  const tokensCss = ":root{" + Object.entries(tokens).map(([k, v]) => `--${k}:${v}`).join(";") + "}";
  const dsHref = "file:///" + path.join(REPO, "engine", "design-system.css").replace(/\\/g, "/");

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 1500 } });
  await page.goto("file://" + fitaPath, { waitUntil: "networkidle" });
  await page.addStyleTag({ url: dsHref });
  if (pack.fonts && pack.fonts.css) await page.addStyleTag({ url: pack.fonts.css });
  await page.addStyleTag({ content: tokensCss + " body{margin:0}" });
  await page.evaluate(() => document.fonts.ready);

  await page.locator("main.fita").screenshot({ path: path.join(outDir, "strip.png") });
  const secs = page.locator("main.fita section.slide");
  const n = await secs.count();
  for (let i = 0; i < n; i++)
    await secs.nth(i).screenshot({ path: path.join(outDir, `slide-${i + 1}.png`) });
  await browser.close();
  console.log(`strip.png + ${n} slide-N.png em ${outDir}`);
})();
