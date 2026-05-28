#!/usr/bin/env node
/**
 * Open a template in the full editor of the platform and click
 * "Salvar Alterações" so the product generates/refreshes thumbnails.
 *
 * This script intentionally receives credentials through CLI/env and never prints
 * passwords. It uses Playwright + Chromium when available in the runtime.
 */

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const out = { baseUrl: 'https://d3iy4qbtnfohd6.cloudfront.net', headless: true };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    const next = argv[i + 1];
    if (a === '--template-id') out.templateId = argv[++i];
    else if (a === '--email') out.email = argv[++i];
    else if (a === '--password') out.password = argv[++i];
    else if (a === '--base-url') out.baseUrl = argv[++i];
    else if (a === '--out-dir') out.outDir = argv[++i];
    else if (a === '--headed') out.headless = false;
    else if (a === '--help' || a === '-h') {
      console.log('Usage: save-template-in-editor.js --template-id ID --email EMAIL --password PASSWORD [--base-url URL] [--out-dir DIR] [--headed]');
      process.exit(0);
    }
  }
  return out;
}

function loadPlaywright() {
  const candidates = [
    'playwright',
    '/tmp/pw-run/node_modules/playwright',
    '/root/.openclaw/workspace/reel01/node_modules/playwright-core',
  ];
  if (process.env.GP2_PLAYWRIGHT_DIR) candidates.unshift(process.env.GP2_PLAYWRIGHT_DIR);
  for (const candidate of candidates) {
    try {
      return require(candidate);
    } catch (_) { }
  }
  throw new Error('Playwright not found. Run `npm install` + `npx playwright install chromium` in fabricjs-template-generator/, or set GP2_PLAYWRIGHT_DIR to the absolute path of an installed playwright package.');
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args.templateId) throw new Error('--template-id is required');
  if (!args.email) throw new Error('--email is required');
  if (!args.password) throw new Error('--password is required');

  const { chromium } = loadPlaywright();
  const outDir = args.outDir || path.join(process.cwd(), 'post-upload-editor-save', args.templateId);
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ headless: args.headless });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const events = [];
  page.on('response', r => {
    if (r.url().includes('/api/')) events.push({ type: 'res', status: r.status(), url: r.url() });
  });
  page.on('console', m => events.push({ type: 'console', level: m.type(), text: m.text().slice(0, 600) }));
  page.on('pageerror', e => events.push({ type: 'pageerror', text: String(e).slice(0, 1000) }));

  async function snapshot(name) {
    const text = await page.locator('body').innerText().catch(() => '');
    fs.writeFileSync(path.join(outDir, `${name}.txt`), text);
    await page.screenshot({ path: path.join(outDir, `${name}.png`), fullPage: false }).catch(() => { });
    events.push({ type: 'state', name, url: page.url(), text: text.slice(0, 1000) });
  }

  const base = args.baseUrl.replace(/\/$/, '');
  await page.goto(`${base}/auth/login`, { waitUntil: 'domcontentloaded' });
  const inputs = page.locator('input');
  await inputs.nth(0).fill(args.email);
  await inputs.nth(1).fill(args.password);
  await Promise.all([
    page.waitForResponse(r => r.url().includes('/api/user_info') && r.status() === 200, { timeout: 30000 }),
    page.locator('button[type=submit]').click({ force: true }),
  ]);

  const editorUrl = `${base}/editor/${args.templateId}`;
  await page.goto(editorUrl, { waitUntil: 'domcontentloaded' });
  await page.waitForLoadState('networkidle', { timeout: 45000 }).catch(() => { });
  await page.waitForTimeout(8000);
  await snapshot('01-editor-loaded');

  const body = await page.locator('body').innerText().catch(() => '');
  if (/Entre na sua conta|Bem-vindo de volta|User not logged in/i.test(body)) {
    throw new Error('Editor did not open authenticated session. Login expired or failed.');
  }
  if (!/Salvar Alterações|Compartilhar|Prévia|layers|Camadas/i.test(body)) {
    throw new Error('Editor UI did not appear; cannot safely click save.');
  }

  const saveButton = page.getByRole('button', { name: /Salvar Alterações/i }).first();
  if (!(await saveButton.count().catch(() => 0))) {
    throw new Error('Could not find "Salvar Alterações" button.');
  }

  const saveResponse = page.waitForResponse(
    r => r.url().includes('/api/') && ['POST', 'PUT', 'PATCH'].includes(r.request().method()) && r.status() >= 200 && r.status() < 300,
    { timeout: 30000 }
  ).catch(() => null);
  await saveButton.click({ force: true });
  const response = await saveResponse;
  await page.waitForLoadState('networkidle', { timeout: 45000 }).catch(() => { });
  await page.waitForTimeout(5000);
  await snapshot('02-after-save');

  const result = {
    templateId: args.templateId,
    editorUrl,
    clickedSave: true,
    saveResponse: response ? { status: response.status(), url: response.url() } : null,
    outDir,
    events,
  };
  fs.writeFileSync(path.join(outDir, 'result.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify({ templateId: args.templateId, clickedSave: true, saveResponse: result.saveResponse, outDir }, null, 2));
  await browser.close();
}

main().catch(err => {
  const args = parseArgs(process.argv);
  const outDir = args.outDir || path.join(process.cwd(), 'post-upload-editor-save', args.templateId || 'unknown-template');
  try {
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(path.join(outDir, 'result.json'), JSON.stringify({
      templateId: args.templateId || null,
      clickedSave: false,
      error: String(err && err.message ? err.message : err),
      outDir,
    }, null, 2));
  } catch (_) { }
  console.error(JSON.stringify({ error: String(err && err.message ? err.message : err), outDir }, null, 2));
  process.exit(1);
});
