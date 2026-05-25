#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

function loadPlaywright() {
  for (const candidate of ['playwright', '/tmp/pw-run/node_modules/playwright']) {
    try { return require(candidate); } catch (_) {}
  }
  throw new Error('Playwright not found. Expected playwright or /tmp/pw-run/node_modules/playwright.');
}

function parseArgs(argv) {
  const args = { artifact: null, variant: null };
  const positional = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--variant' || a === '-v') {
      args.variant = argv[++i];
    } else if (a.startsWith('--variant=')) {
      args.variant = a.slice('--variant='.length);
    } else {
      positional.push(a);
    }
  }
  args.artifact = positional[0];
  return args;
}

async function main() {
  const { artifact, variant } = parseArgs(process.argv.slice(2));
  if (!artifact) {
    throw new Error('Usage: render-html-screenshots.js <artifact-folder> [--variant v1-lowfi|v2-midfi|final]');
  }

  // Variant maps to specific file + screenshots dir; no variant = default (template.html + screenshots/).
  const htmlName = variant && variant !== 'final' ? `template-${variant}.html` : 'template.html';
  const outName = variant && variant !== 'final' ? `screenshots-${variant}` : 'screenshots';

  const html = path.join(artifact, htmlName);
  if (!fs.existsSync(html)) throw new Error(`${htmlName} not found: ${html}`);
  const out = path.join(artifact, outName);
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
  const result = {
    artifact: path.resolve(artifact),
    variant: variant || 'final',
    htmlSource: html,
    slideCount: count,
    outDir: out,
    files
  };
  fs.writeFileSync(path.join(out, 'render-result.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
}
main().catch(err => { console.error(JSON.stringify({ error: String(err.message || err) }, null, 2)); process.exit(1); });
