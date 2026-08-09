#!/usr/bin/env node
/**
 * Renderiza os exemplares de padrão dos packs: exemplos/*.html -> exemplos/*.jpg
 *
 * O HTML é a FONTE do padrão; a imagem é derivada e existe só para o portal não
 * ter que renderizar a cada request. Rode depois de qualquer mudança no motor —
 * o que regredir aparece na hora, em vez de ficar mentindo num JPG antigo.
 *
 * Uso: node engine/tools/build-exemplos.js [slug-do-pack]
 */

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const REPO = path.resolve(__dirname, "..", "..");
const PACKS = path.join(REPO, "packs");
const LARGURA = 760; // o portal mostra em coluna estreita; 760 sobra

(async () => {
  const alvo = process.argv[2];
  const slugs = fs.readdirSync(PACKS).filter((s) =>
    fs.existsSync(path.join(PACKS, s, "pack.json")) && (!alvo || s === alvo));
  if (!slugs.length) { console.error(`pack não encontrado: ${alvo}`); process.exit(2); }

  const { chromium } = require("playwright");
  const browser = await chromium.launch();
  let n = 0;

  for (const slug of slugs) {
    const dir = path.join(PACKS, slug, "exemplos");
    if (!fs.existsSync(dir)) continue;
    const htmls = fs.readdirSync(dir).filter((f) => f.endsWith(".html"));
    for (const arquivo of htmls) {
      const fita = path.join(dir, arquivo);
      const pack = JSON.parse(fs.readFileSync(
        path.join(PACKS, (fs.readFileSync(fita, "utf-8").match(/data-pack="([^"]+)"/) || [])[1] || slug,
                  "pack.json"), "utf-8"));
      const tokensCss = ":root{" + Object.entries(pack.tokens)
        .map(([k, v]) => `--${k}:${v}`).join(";") + "}";
      const dsHref = "file:///" + path.join(REPO, "engine", "design-system.css").replace(/\\/g, "/");

      const page = await browser.newPage({ viewport: { width: 1400, height: 1500 } });
      await page.goto("file://" + fita, { waitUntil: "networkidle" });
      await page.addStyleTag({ url: dsHref });
      if (pack.fonts && pack.fonts.css) await page.addStyleTag({ url: pack.fonts.css });
      await page.addStyleTag({ content: tokensCss + " body{margin:0}" });
      await page.evaluate(() => document.fonts.ready);

      // um exemplar = um padrão = uma section; mais de uma, vira o strip inteiro
      const secs = page.locator("main.fita section.slide");
      const total = await secs.count();
      const alvoLoc = total === 1 ? secs.first() : page.locator("main.fita");
      const png = path.join(dir, arquivo.replace(/\.html$/, ".png"));
      await alvoLoc.screenshot({ path: png });
      await page.close();

      // reduz para a largura de exibição (o PNG cheio pesa MBs por slide).
      // PIL em vez de sharp: já está no fluxo, não vale uma dependência nova.
      const jpg = png.replace(/\.png$/, ".jpg");
      execFileSync("python", ["-c", [
        "import sys; from PIL import Image",
        "im = Image.open(sys.argv[1]).convert('RGB')",
        `im.thumbnail((${LARGURA}, ${LARGURA * 4}), Image.LANCZOS)`,
        "im.save(sys.argv[2], 'JPEG', quality=84, optimize=True)",
      ].join("\n"), png, jpg], { stdio: "inherit" });
      fs.unlinkSync(png);
      console.log(`  ${slug}/${path.basename(jpg)}`);
      n++;
    }
  }

  await browser.close();
  console.log(`${n} exemplar(es) renderizado(s).`);
})();
