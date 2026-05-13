#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

function loadPlaywright() {
  for (const candidate of ['playwright', '/tmp/pw-run/node_modules/playwright']) {
    try { return require(candidate); } catch (_) {}
  }
  throw new Error('Playwright not found. Expected playwright or /tmp/pw-run/node_modules/playwright.');
}

async function main() {
  const artifact = process.argv[2];
  if (!artifact) throw new Error('Usage: render-html-screenshots.js <artifact-folder>');
  const html = path.join(artifact, 'template.html');
  if (!fs.existsSync(html)) throw new Error(`template.html not found: ${html}`);
  const out = path.join(artifact, 'screenshots');
  fs.mkdirSync(out, { recursive: true });
  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(html), { waitUntil: 'load' });
  await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(1000);
  const count = await page.locator('section.slide').count();
  if (!count) throw new Error('No section.slide elements found.');
  const files = [];
  for (let i = 0; i < count; i++) {
    const file = path.join(out, `slide-${i + 1}.png`);
    await page.locator('section.slide').nth(i).screenshot({ path: file });
    files.push(file);
  }
  await browser.close();
  const result = { artifact: path.resolve(artifact), slideCount: count, outDir: out, files };
  fs.writeFileSync(path.join(out, 'render-result.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
}
main().catch(err => { console.error(JSON.stringify({ error: String(err.message || err) }, null, 2)); process.exit(1); });
