#!/usr/bin/env node
/**
 * center-clippable-images.js
 *
 * Pós-processo determinístico que reaplica, em cada `ClippableImage` dos
 * slide JSONs emitidos pelo gp2-template-converter, o mesmo cover-crop
 * centralizado que o editor da plataforma executa quando o usuário troca
 * a imagem do slot.
 *
 * O converter deve emitir cada ClippableImage com:
 *   - `src`                URL absoluta da imagem
 *   - `left`, `top`        posição Fabric center (já no sistema do canvas)
 *   - `width`, `height`    dimensões do FRAME VISUAL no HTML (slot)
 *   - `topLeft/topRight/bottomRight/bottomLeft`  cantos em %
 *   - `originX: "center"`, `originY: "center"`
 *   - `imageType`, `isTemplateElement`, `templateElement`, etc.
 *
 * Crop, scale e originWidth/originHeight são responsabilidade DESTE script.
 *
 * Algoritmo (espelha replaceImage cegamente):
 *   1. visualWidth  = width  * (scaleX ?? 1)   ← antes da troca
 *      visualHeight = height * (scaleY ?? 1)
 *   2. Lê naturalWidth/naturalHeight da imagem:
 *      - data: URLs → decode base64 + magic bytes (PNG/JPEG/WebP/GIF) sem browser
 *      - http(s) URLs → fetch + magic bytes sem browser
 *      - Playwright como fallback opcional (formatos exóticos / quando disponível)
 *   3. objectAspect = visualW / visualH
 *      imageAspect  = naturalW / naturalH
 *   4. if (imageAspect > objectAspect):
 *          cropH = naturalH; cropW = cropH * objectAspect
 *      else:
 *          cropW = naturalW; cropH = cropW / objectAspect
 *      cropX = (naturalW - cropW) / 2
 *      cropY = (naturalH - cropH) / 2
 *      scale = visualW / cropW
 *   5. Patch:
 *      { originWidth: naturalW, originHeight: naturalH,
 *        width: cropW, height: cropH,
 *        cropX, cropY, scaleX: scale, scaleY: scale }
 *
 * Idempotente: rodar duas vezes produz o mesmo JSON (visualW/H é recalculado
 * sempre a partir do estado atual, que vira invariante após a primeira passada).
 *
 * Uso:
 *   node scripts/center-clippable-images.js artifacts/gp2-template-converter/<slug>/output/
 *
 * Saída: rewrite in-place dos slide-*.json + relatório no stdout.
 */

const fs = require('fs');
const path = require('path');

function loadPlaywright() {
  const candidates = ['playwright', '/tmp/pw-run/node_modules/playwright'];
  if (process.env.GP2_PLAYWRIGHT_DIR) candidates.unshift(process.env.GP2_PLAYWRIGHT_DIR);
  for (const candidate of candidates) {
    try { return require(candidate); } catch (_) {}
  }
  return null;
}

/**
 * Lê width/height de um Buffer de imagem decodificando magic bytes.
 * Suporta PNG, JPEG, WebP (VP8/VP8L/VP8X), GIF. Retorna null se não reconhecer.
 */
function imageSizeFromBuffer(buf) {
  if (buf.length < 24) return null;

  // PNG: \x89PNG\r\n\x1a\n + IHDR(width:uint32be, height:uint32be) em offset 16
  if (buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47) {
    return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
  }

  // GIF: 'GIF87a' | 'GIF89a' + width:uint16le + height:uint16le em offset 6
  if (buf[0] === 0x47 && buf[1] === 0x49 && buf[2] === 0x46) {
    return { width: buf.readUInt16LE(6), height: buf.readUInt16LE(8) };
  }

  // WebP: 'RIFF' .... 'WEBP'
  if (buf[0] === 0x52 && buf[1] === 0x49 && buf[2] === 0x46 && buf[3] === 0x46 &&
      buf[8] === 0x57 && buf[9] === 0x45 && buf[10] === 0x42 && buf[11] === 0x50) {
    const fourcc = buf.slice(12, 16).toString('ascii');
    if (fourcc === 'VP8 ') {
      // bytes 26-29 contém width|height (14 bits cada, little endian, low 2 bits ignored)
      const w = buf.readUInt16LE(26) & 0x3fff;
      const h = buf.readUInt16LE(28) & 0x3fff;
      return { width: w, height: h };
    }
    if (fourcc === 'VP8L') {
      const b0 = buf[21], b1 = buf[22], b2 = buf[23], b3 = buf[24];
      const w = 1 + (((b1 & 0x3f) << 8) | b0);
      const h = 1 + (((b3 & 0x0f) << 10) | (b2 << 2) | ((b1 & 0xc0) >> 6));
      return { width: w, height: h };
    }
    if (fourcc === 'VP8X') {
      // canvas width/height são uint24le em offsets 24 e 27, valor +1
      const w = 1 + (buf[24] | (buf[25] << 8) | (buf[26] << 16));
      const h = 1 + (buf[27] | (buf[28] << 8) | (buf[29] << 16));
      return { width: w, height: h };
    }
  }

  // JPEG: \xff\xd8 ... SOF0/1/2 marker (\xff\xc0-\xc3, \xc5-\xc7, \xc9-\xcb, \xcd-\xcf)
  if (buf[0] === 0xff && buf[1] === 0xd8) {
    let i = 2;
    while (i < buf.length - 9) {
      if (buf[i] !== 0xff) return null;
      const marker = buf[i + 1];
      if (marker === 0xd8 || marker === 0xd9) { i += 2; continue; }
      // Standalone markers (no length): 0xd0-0xd7, 0x01
      if ((marker >= 0xd0 && marker <= 0xd7) || marker === 0x01) { i += 2; continue; }
      const segLen = buf.readUInt16BE(i + 2);
      const isSOF =
        (marker >= 0xc0 && marker <= 0xc3) ||
        (marker >= 0xc5 && marker <= 0xc7) ||
        (marker >= 0xc9 && marker <= 0xcb) ||
        (marker >= 0xcd && marker <= 0xcf);
      if (isSOF) {
        const h = buf.readUInt16BE(i + 5);
        const w = buf.readUInt16BE(i + 7);
        return { width: w, height: h };
      }
      i += 2 + segLen;
    }
  }

  return null;
}

function parseDataUrl(src) {
  // data:image/<fmt>;base64,<data>
  const m = src.match(/^data:image\/[a-zA-Z+.-]+;base64,(.+)$/);
  if (!m) return null;
  try { return Buffer.from(m[1], 'base64'); } catch (_) { return null; }
}

function fetchBufferHttp(url) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https:') ? require('https') : require('http');
    const req = lib.get(url, (res) => {
      if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        res.resume();
        const next = new URL(res.headers.location, url).toString();
        resolve(fetchBufferHttp(next));
        return;
      }
      if (res.statusCode !== 200) {
        res.resume();
        reject(new Error(`HTTP ${res.statusCode} for ${url}`));
        return;
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks)));
      res.on('error', reject);
    });
    req.on('error', reject);
    req.setTimeout(30000, () => {
      req.destroy(new Error(`timeout fetching ${url}`));
    });
  });
}

function parseArgs(argv) {
  const args = { dir: null, dryRun: false };
  const positional = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--dry-run') args.dryRun = true;
    else positional.push(a);
  }
  args.dir = positional[0];
  return args;
}

function listSlideFiles(dir) {
  return fs.readdirSync(dir)
    .filter(f => /^slide-\d+\.json$/i.test(f))
    .sort((a, b) => {
      const na = parseInt(a.match(/\d+/)[0], 10);
      const nb = parseInt(b.match(/\d+/)[0], 10);
      return na - nb;
    })
    .map(f => path.join(dir, f));
}

function isClippableImage(obj) {
  return obj && obj.type === 'ClippableImage' && typeof obj.src === 'string';
}

function walkObjects(slideJson, visitor) {
  if (!slideJson || !Array.isArray(slideJson.objects)) return;
  for (const obj of slideJson.objects) {
    visitor(obj);
  }
}

async function measureNaturalSize(url) {
  // 1) data URL → decode base64 → magic bytes
  if (url.startsWith('data:')) {
    const buf = parseDataUrl(url);
    if (!buf) return { ok: false, error: 'invalid data URL' };
    const dims = imageSizeFromBuffer(buf);
    if (!dims) return { ok: false, error: 'unrecognized data URL image format' };
    return { ok: true, naturalWidth: dims.width, naturalHeight: dims.height, source: 'data-url' };
  }

  // 2) http(s) URL → baixa direto + magic bytes (sem browser)
  if (url.startsWith('http:') || url.startsWith('https:')) {
    try {
      const buf = await fetchBufferHttp(url);
      const dims = imageSizeFromBuffer(buf);
      if (dims) return { ok: true, naturalWidth: dims.width, naturalHeight: dims.height, source: 'http' };
      return { ok: false, error: 'unrecognized image format from http fetch' };
    } catch (err) {
      return { ok: false, error: String(err && err.message || err) };
    }
  }

  return { ok: false, error: `unsupported URL scheme: ${url.slice(0, 32)}` };
}

async function measureNaturalSizeBatch(urls, playwrightFallback) {
  const cache = new Map();
  const unique = [...new Set(urls)];
  if (unique.length === 0) return cache;

  // Pass 1: tenta sem browser (data URL ou http+magic-bytes)
  const needsBrowser = [];
  for (const url of unique) {
    const dims = await measureNaturalSize(url);
    if (dims.ok) {
      cache.set(url, dims);
    } else {
      needsBrowser.push({ url, prevError: dims.error });
    }
  }

  // Pass 2: fallback Playwright para URLs que falharam (formato exótico, etc.)
  if (needsBrowser.length > 0) {
    if (!playwrightFallback) {
      for (const { url, prevError } of needsBrowser) {
        cache.set(url, { ok: false, error: `${prevError} (no Playwright fallback available — \`npm install\` + \`npx playwright install chromium\` to enable)` });
      }
      return cache;
    }
    const browser = await playwrightFallback.chromium.launch();
    try {
      const context = await browser.newContext({ ignoreHTTPSErrors: true });
      const page = await context.newPage();
      for (const { url, prevError } of needsBrowser) {
        try {
          const dims = await page.evaluate((src) => new Promise((resolve) => {
            const img = new Image();
            img.crossOrigin = 'anonymous';
            img.onload = () => resolve({
              ok: true,
              naturalWidth: img.naturalWidth,
              naturalHeight: img.naturalHeight,
            });
            img.onerror = (e) => resolve({ ok: false, error: String(e && e.message || e) });
            img.src = src;
          }), url);
          if (dims.ok) cache.set(url, { ...dims, source: 'playwright' });
          else cache.set(url, { ok: false, error: `${prevError}; playwright: ${dims.error}` });
        } catch (err) {
          cache.set(url, { ok: false, error: `${prevError}; playwright threw: ${String(err && err.message || err)}` });
        }
      }
      await context.close();
    } finally {
      await browser.close();
    }
  }

  return cache;
}

function recalcCenterCrop(obj, naturalW, naturalH) {
  const currentScaleX = obj.scaleX != null ? obj.scaleX : 1;
  const currentScaleY = obj.scaleY != null ? obj.scaleY : 1;
  const currentW = obj.width != null ? obj.width : naturalW;
  const currentH = obj.height != null ? obj.height : naturalH;

  const visualWidth  = currentW * currentScaleX;
  const visualHeight = currentH * currentScaleY;

  const objectAspect = visualWidth / visualHeight;
  const imageAspect  = naturalW / naturalH;

  let cropW, cropH;
  if (imageAspect > objectAspect) {
    cropH = naturalH;
    cropW = cropH * objectAspect;
  } else {
    cropW = naturalW;
    cropH = cropW / objectAspect;
  }

  const cropX = (naturalW - cropW) / 2;
  const cropY = (naturalH - cropH) / 2;
  const scale = visualWidth / cropW;

  return {
    originWidth: naturalW,
    originHeight: naturalH,
    width: cropW,
    height: cropH,
    cropX,
    cropY,
    scaleX: scale,
    scaleY: scale,
    originX: 'center',
    originY: 'center',
  };
}

function applyPatch(obj, patch) {
  for (const k of Object.keys(patch)) {
    obj[k] = patch[k];
  }
}

async function run() {
  const { dir, dryRun } = parseArgs(process.argv.slice(2));
  if (!dir) {
    console.error('usage: node scripts/center-clippable-images.js <output-dir> [--dry-run]');
    process.exit(2);
  }
  if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) {
    console.error(`[error] not a directory: ${dir}`);
    process.exit(2);
  }

  const slideFiles = listSlideFiles(dir);
  if (slideFiles.length === 0) {
    console.error(`[error] no slide-*.json files in ${dir}`);
    process.exit(2);
  }

  // 1) Carrega todos os slides e coleta URLs únicas.
  const slides = slideFiles.map(file => ({
    file,
    json: JSON.parse(fs.readFileSync(file, 'utf8')),
  }));

  const urls = [];
  for (const { json } of slides) {
    walkObjects(json, (obj) => { if (isClippableImage(obj)) urls.push(obj.src); });
  }

  if (urls.length === 0) {
    console.log('[ok] nenhum ClippableImage encontrado — nada a fazer.');
    return;
  }

  // 2) Mede natural size de cada URL. Primeiro tenta decode direto (data URL ou
  //    HTTP+magic-bytes); só usa Playwright como fallback se disponível.
  const playwright = loadPlaywright();
  const sizes = await measureNaturalSizeBatch(urls, playwright);

  // 3) Aplica patch e reescreve cada slide.
  const report = [];
  let totalPatched = 0;
  let totalSkipped = 0;

  for (const { file, json } of slides) {
    let patched = 0;
    let skipped = 0;
    walkObjects(json, (obj) => {
      if (!isClippableImage(obj)) return;
      const dims = sizes.get(obj.src);
      if (!dims || !dims.ok) {
        skipped++;
        report.push({ file: path.basename(file), src: obj.src, status: 'SKIP', reason: dims && dims.error || 'no dims' });
        return;
      }
      const patch = recalcCenterCrop(obj, dims.naturalWidth, dims.naturalHeight);
      applyPatch(obj, patch);
      patched++;
      report.push({
        file: path.basename(file),
        src: obj.src,
        status: 'OK',
        natural: `${dims.naturalWidth}x${dims.naturalHeight}`,
        crop: `${Math.round(patch.cropX)},${Math.round(patch.cropY)} ${Math.round(patch.width)}x${Math.round(patch.height)}`,
        scale: patch.scaleX.toFixed(4),
      });
    });
    if (!dryRun && patched > 0) {
      fs.writeFileSync(file, JSON.stringify(json, null, 2) + '\n', 'utf8');
    }
    totalPatched += patched;
    totalSkipped += skipped;
  }

  // 4) Relatório.
  console.log('');
  console.log(`center-clippable-images: ${dryRun ? '[DRY RUN] ' : ''}slides=${slides.length} patched=${totalPatched} skipped=${totalSkipped}`);
  for (const r of report) {
    if (r.status === 'OK') {
      console.log(`  [ok]   ${r.file}  natural=${r.natural}  crop=${r.crop}  scale=${r.scale}`);
    } else {
      console.log(`  [skip] ${r.file}  ${r.src}  (${r.reason})`);
    }
  }

  process.exit(totalSkipped > 0 ? 1 : 0);
}

run().catch((err) => {
  console.error('[fatal]', err && err.stack || err);
  process.exit(2);
});
