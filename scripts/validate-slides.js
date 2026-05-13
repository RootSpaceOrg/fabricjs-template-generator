#!/usr/bin/env node
/**
 * Validates slide JSONs produced by the claude-design-to-fabricjs-converter agent.
 *
 * Usage:
 *   node validate-slides.js output/carrossel-template/
 *   node validate-slides.js output/carrossel-template/slide-1.json
 *   node validate-slides.js output/                   # validates all subfolders
 */

import { readFileSync, readdirSync, statSync } from 'fs';
import { resolve, extname, basename, join } from 'path';

// ─── helpers ────────────────────────────────────────────────────────────────

// 'rect' is intentionally excluded — the editor only registers roundedRect and ClippableImage.
// A plain rect (especially with a gradient fill object) fails deserialization.
const VALID_TYPES = new Set([
  'roundedRect', 'circle', 'ellipse', 'path',
  'line', 'textbox', 'image', 'ClippableImage',
]);

const FORBIDDEN_TYPES = new Set(['rect']);

const VALID_VARIABLES = new Set(['primary', 'secondary']);
const VALID_TEXT_TYPES = new Set(['phone', 'instagramName', 'instagramHandle', 'address']);

let totalErrors = 0;
let totalWarnings = 0;

function err(file, path, msg) {
  console.error(`  ✗ [${file}] ${path}: ${msg}`);
  totalErrors++;
}

function warn(file, path, msg) {
  console.warn(`  ⚠ [${file}] ${path}: ${msg}`);
  totalWarnings++;
}

// ─── per-object validators ───────────────────────────────────────────────────

function validateGradientFill(fill, file, path) {
  if (!fill || typeof fill !== 'object') return;
  // Only validate if it looks like a gradient (has colorStops)
  if (!('colorStops' in fill)) return;

  if (fill.type !== 'linear' && fill.type !== 'radial') {
    err(file, path, `gradient type must be "linear" or "radial", got "${fill.type}"`);
  }
  if (!fill.coords || typeof fill.coords !== 'object') {
    err(file, path, 'gradient missing required field "coords"');
  } else {
    for (const k of ['x1', 'y1', 'x2', 'y2']) {
      if (typeof fill.coords[k] !== 'number')
        err(file, `${path}.coords`, `missing or non-numeric "${k}"`);
    }
    if (fill.type === 'radial') {
      for (const k of ['r1', 'r2']) {
        if (typeof fill.coords[k] !== 'number')
          err(file, `${path}.coords`, `radial gradient missing or non-numeric "${k}"`);
      }
    }
  }
  if (!Array.isArray(fill.colorStops) || fill.colorStops.length === 0) {
    err(file, path, 'gradient missing required field "colorStops" (must be a non-empty array)');
  } else {
    fill.colorStops.forEach((stop, i) => {
      if (typeof stop.offset !== 'number' || stop.offset < 0 || stop.offset > 1)
        err(file, `${path}.colorStops[${i}]`, `offset must be a number 0–1, got ${stop.offset}`);
      if (typeof stop.color !== 'string' || !stop.color)
        err(file, `${path}.colorStops[${i}]`, 'color must be a non-empty string');
    });
  }
  if (typeof fill.offsetX !== 'number')
    err(file, path, 'gradient missing required field "offsetX" (must be a number, e.g. 0)');
  if (typeof fill.offsetY !== 'number')
    err(file, path, 'gradient missing required field "offsetY" (must be a number, e.g. 0)');
  if (fill.gradientUnits !== 'percentage' && fill.gradientUnits !== 'pixels')
    err(file, path, `gradient missing required field "gradientUnits" (must be "percentage" or "pixels")`);
  if (!('gradientTransform' in fill))
    err(file, path, 'gradient missing required field "gradientTransform" (use null when no transform)');
}

function validateVariableConfig(vc, file, path) {
  if (vc.type === 'solid') {
    if (!VALID_VARIABLES.has(vc.variable))
      err(file, path, `variable must be "primary"|"secondary", got "${vc.variable}"`);
    if (typeof vc.alpha !== 'number' || vc.alpha < 0 || vc.alpha > 1)
      err(file, path, `alpha must be a number 0–1, got ${vc.alpha}`);
  } else if (vc.type === 'gradient') {
    if (!Array.isArray(vc.colorStops) || vc.colorStops.length === 0)
      err(file, path, 'gradient variableConfig must have colorStops[]');
    (vc.colorStops || []).forEach((stop, i) => {
      if (!VALID_VARIABLES.has(stop.variable))
        err(file, path + `.colorStops[${i}]`, `variable must be "primary"|"secondary"`);
    });
  } else {
    err(file, path, `unknown variableConfig type "${vc.type}"`);
  }
}

function validateTextboxStyles(styles, text, file, path) {
  if (styles === undefined || styles === null) {
    err(file, path, 'textbox is missing "styles" property — must be at least {}');
    return;
  }
  if (Array.isArray(styles)) {
    // Fabric's native toJSON() emits styles as a range array [{start,end,style}].
    // The agent should emit the map format {lineIndex:{charIndex:{...}}} so that
    // updateTemplateColors can swap per-character brand colors on the raw JSON.
    // An empty array [] is benign (no per-char styles), but a non-empty array
    // means fillVariableConfig on character spans won't be applied by updateTemplateColors.
    if (styles.length === 0) {
      warn(file, path, '"styles" is an empty array [] — emit {} instead for consistency');
    } else {
      err(file, path, '"styles" is a range array (Fabric native format) — convert to map format {lineIndex:{charIndex:{...}}} so per-character fillVariableConfig works with updateTemplateColors');
    }
    return;
  }
  if (typeof styles !== 'object') {
    err(file, path, '"styles" must be a plain object');
    return;
  }

  const lines = text.split('\n');
  for (const [lineKey, charMap] of Object.entries(styles)) {
    const lineIndex = parseInt(lineKey, 10);
    if (isNaN(lineIndex) || lineIndex < 0)
      err(file, `${path}.styles`, `invalid line key "${lineKey}"`);
    if (lineIndex >= lines.length)
      warn(file, `${path}.styles`, `line key ${lineKey} is out of range (text has ${lines.length} line(s))`);

    for (const [charKey, charStyle] of Object.entries(charMap)) {
      const charIndex = parseInt(charKey, 10);
      if (isNaN(charIndex) || charIndex < 0)
        err(file, `${path}.styles[${lineKey}]`, `invalid char key "${charKey}"`);
      const lineLen = lines[lineIndex]?.length ?? 0;
      if (charIndex >= lineLen)
        warn(file, `${path}.styles[${lineKey}]`, `char key ${charKey} is out of range (line has ${lineLen} char(s))`);
      if (charStyle.fillVariableConfig)
        validateVariableConfig(charStyle.fillVariableConfig, file, `${path}.styles[${lineKey}][${charKey}].fillVariableConfig`);
    }
  }
}

function validateObject(obj, file, index) {
  const p = `objects[${index}]`;

  // type
  if (!obj.type) {
    err(file, p, 'missing "type"');
    return;
  }
  if (FORBIDDEN_TYPES.has(obj.type))
    err(file, p, `type "${obj.type}" is not supported by the editor — use "roundedRect" (all corners 0) instead`);
  else if (!VALID_TYPES.has(obj.type))
    warn(file, p, `unknown type "${obj.type}"`);

  // name (required)
  if (!obj.name || typeof obj.name !== 'string' || obj.name.trim() === '')
    err(file, p, `missing or empty "name" (type: ${obj.type})`);

  // origin
  if (obj.originX !== 'center')
    err(file, p, `originX must be "center", got "${obj.originX}"`);
  if (obj.originY !== 'center')
    err(file, p, `originY must be "center", got "${obj.originY}"`);

  // position — left/top must be numbers
  if (typeof obj.left !== 'number') err(file, p, '"left" must be a number');
  if (typeof obj.top !== 'number') err(file, p, '"top" must be a number');

  // opacity
  if (obj.opacity !== undefined && (typeof obj.opacity !== 'number' || obj.opacity < 0 || obj.opacity > 1))
    err(file, p, `opacity must be 0–1, got ${obj.opacity}`);

  // lineHeight clamp
  if (obj.type === 'textbox' && typeof obj.lineHeight === 'number' && obj.lineHeight < 1)
    err(file, p, `lineHeight ${obj.lineHeight} is below 1.0 — must be clamped to 1.0`);

  // charSpacing clamp — values below -150 render broken in Fabric 5
  if (obj.type === 'textbox' && typeof obj.charSpacing === 'number' && obj.charSpacing < -150)
    err(file, p, `charSpacing ${obj.charSpacing} is below -150 — clamp to -150 (Fabric renders values below this incorrectly)`);

  // textbox-specific
  if (obj.type === 'textbox') {
    if (typeof obj.text !== 'string') err(file, p, '"text" must be a string');
    if (!obj.fontFamily) err(file, p, 'missing "fontFamily"');
    if (!obj.fontSize) err(file, p, 'missing "fontSize"');
    // text-transform must be baked into the text string, not stored as a property
    if (obj.textTransform && obj.textTransform !== 'none')
      err(file, p, `"textTransform: ${obj.textTransform}" must be baked into the "text" string (Fabric has no text-transform — apply .toUpperCase()/.toLowerCase() to the text value)`);
    validateTextboxStyles(obj.styles, obj.text ?? '', file, p);
  }

  // ClippableImage-specific
  if (obj.type === 'ClippableImage') {
    for (const field of ['src', 'originWidth', 'originHeight', 'cropX', 'cropY', 'imageType']) {
      if (obj[field] === undefined || obj[field] === null)
        err(file, p, `ClippableImage is missing required field "${field}"`);
    }
    for (const corner of ['topLeft', 'topRight', 'bottomRight', 'bottomLeft']) {
      if (typeof obj[corner] !== 'number')
        err(file, p, `ClippableImage missing corner radius "${corner}"`);
    }
  }

  // roundedRect corners
  if (obj.type === 'roundedRect') {
    for (const corner of ['topLeft', 'topRight', 'bottomRight', 'bottomLeft']) {
      if (typeof obj[corner] !== 'number')
        err(file, p, `roundedRect missing corner "${corner}"`);
      else if (obj[corner] < 0 || obj[corner] > 100)
        err(file, p, `roundedRect corner "${corner}" must be 0–100 (percent), got ${obj[corner]}`);
    }
  }

  // path — path array
  if (obj.type === 'path') {
    if (!Array.isArray(obj.path) || obj.path.length === 0)
      err(file, p, 'path object must have a non-empty "path" array');
  }

  // gradient fill / stroke shape
  if (obj.fill && typeof obj.fill === 'object') validateGradientFill(obj.fill, file, `${p}.fill`);
  if (obj.stroke && typeof obj.stroke === 'object') validateGradientFill(obj.stroke, file, `${p}.stroke`);

  // variable configs
  if (obj.fillVariableConfig) validateVariableConfig(obj.fillVariableConfig, file, `${p}.fillVariableConfig`);
  if (obj.strokeVariableConfig) validateVariableConfig(obj.strokeVariableConfig, file, `${p}.strokeVariableConfig`);

  // textType — validate when present
  if (obj.textType !== undefined) {
    if (obj.type !== 'textbox')
      err(file, p, `"textType" is only valid on textbox objects, got "${obj.type}"`);
    if (!VALID_TEXT_TYPES.has(obj.textType))
      err(file, p, `invalid "textType" value "${obj.textType}" — must be one of: ${[...VALID_TEXT_TYPES].join(', ')}`);
    if (obj.isTemplateElement === true)
      err(file, p, '"textType" and "isTemplateElement: true" are mutually exclusive — profile variables are never AI-fillable');
  }

  // templateElement — validate when present
  if (obj.isTemplateElement === true) {
    if (!obj.templateElement || typeof obj.templateElement !== 'object') {
      err(file, p, 'isTemplateElement is true but "templateElement" block is missing or not an object');
    } else {
      const te = obj.templateElement;
      if (typeof te.description !== 'string' || te.description.trim() === '')
        err(file, p, 'templateElement missing required field "description" (must be a non-empty string)');
      if (obj.type === 'textbox') {
        if (typeof te.minChars !== 'number')
          err(file, p, 'templateElement textbox missing required field "minChars" (number)');
        if (typeof te.maxChars !== 'number')
          err(file, p, 'templateElement textbox missing required field "maxChars" (number)');
        if (te.minChars !== undefined && te.maxChars !== undefined && te.minChars > te.maxChars)
          err(file, p, `templateElement minChars (${te.minChars}) > maxChars (${te.maxChars})`);
        if (te.textCase !== undefined && !['uppercase', 'lowercase', 'capitalize'].includes(te.textCase))
          err(file, p, `templateElement textCase must be "uppercase", "lowercase", or "capitalize", got "${te.textCase}"`);
      }
      if (obj.type === 'ClippableImage' || obj.type === 'image') {
        if (typeof te.removeBackground !== 'boolean')
          err(file, p, 'templateElement image missing required field "removeBackground" (boolean)');
      }
      if (te.linkId !== undefined && (typeof te.linkId !== 'string' || te.linkId.trim() === ''))
        err(file, p, 'templateElement "linkId" must be a non-empty string when present');
    }
  }

  // no Fabric groups
  if (obj.type === 'group')
    err(file, p, 'Fabric groups are not allowed — flatten to individual objects');
}

// ─── per-slide validator ─────────────────────────────────────────────────────

function validateSlide(filePath) {
  const shortName = basename(filePath);
  let raw;
  try {
    raw = readFileSync(filePath, 'utf8');
  } catch (e) {
    err(shortName, '', `cannot read file: ${e.message}`);
    return;
  }

  let json;
  try {
    json = JSON.parse(raw);
  } catch (e) {
    err(shortName, '', `invalid JSON: ${e.message}`);
    return;
  }

  // root shape
  if (json.version !== '5.5.2')
    err(shortName, 'version', `must be "5.5.2", got "${json.version}"`);

  if (!Array.isArray(json.objects))
    err(shortName, 'objects', 'must be an array');

  if (json._meta === undefined)
    err(shortName, '_meta', 'missing _meta block');
  else {
    if (!json._meta.sourceClaudeDesign)
      warn(shortName, '_meta.sourceClaudeDesign', 'missing source URL');
    if (json._meta.slideIndex === undefined)
      warn(shortName, '_meta.slideIndex', 'missing slideIndex');
  }

  // background — must be a hex/rgba string or a Fabric gradient object, never a CSS function string
  if (json.background !== undefined && json.background !== null && json.background !== '') {
    if (typeof json.background === 'string') {
      if (/^\s*(linear|radial|conic)-gradient\s*\(/i.test(json.background))
        err(shortName, 'background', `CSS gradient string "${json.background.slice(0, 60)}…" is not valid — background must be a hex/rgba color string or a Fabric gradient object ({type:"linear"|"radial", coords, colorStops, …})`);
    } else if (typeof json.background === 'object') {
      validateGradientFill(json.background, shortName, 'background');
    }
  }

  // backgroundVariableConfig
  if (json.backgroundVariableConfig)
    validateVariableConfig(json.backgroundVariableConfig, shortName, 'backgroundVariableConfig');

  // objects
  if (Array.isArray(json.objects)) {
    json.objects.forEach((obj, i) => validateObject(obj, shortName, i));
  }
}

// ─── manifest validator ───────────────────────────────────────────────────────

function validateManifest(filePath, expectedSlideFiles) {
  const shortName = basename(filePath);
  let json;
  try {
    json = JSON.parse(readFileSync(filePath, 'utf8'));
  } catch (e) {
    err(shortName, '', `cannot parse: ${e.message}`);
    return;
  }

  if (!json.templateName) err(shortName, 'templateName', 'missing');
  if (!json.slug) err(shortName, 'slug', 'missing');
  if (!Array.isArray(json.slides) || json.slides.length === 0)
    err(shortName, 'slides', 'must be a non-empty array');

  // cross-check: every slide file in the manifest must exist in the folder
  (json.slides || []).forEach((s, i) => {
    if (!s.file) err(shortName, `slides[${i}]`, 'missing "file"');
    else if (!expectedSlideFiles.has(s.file))
      err(shortName, `slides[${i}].file`, `"${s.file}" not found in output folder`);
    if (!s.width || !s.height)
      err(shortName, `slides[${i}]`, 'missing width/height');
  });

  if (!json.detectedColors || !json.detectedColors.primary || !json.detectedColors.secondary)
    warn(shortName, 'detectedColors', 'missing primary or secondary color entry');
}

// ─── directory walker ────────────────────────────────────────────────────────

function validateFolder(folderPath) {
  const abs = resolve(folderPath);
  let entries;
  try {
    entries = readdirSync(abs);
  } catch (e) {
    console.error(`Cannot read folder ${abs}: ${e.message}`);
    process.exit(1);
  }

  const slideFiles = entries.filter(f => /^slide-\d+\.json$/.test(f));
  const hasManifest = entries.includes('manifest.json');

  if (slideFiles.length === 0) {
    warn(basename(abs), '', 'no slide-N.json files found in folder');
    return;
  }

  console.log(`\n📁 ${abs} (${slideFiles.length} slide(s))`);

  slideFiles.sort().forEach(f => validateSlide(join(abs, f)));

  if (hasManifest) {
    validateManifest(join(abs, 'manifest.json'), new Set(slideFiles));
  } else {
    warn(basename(abs), '', 'manifest.json not found');
  }
}

// ─── entry point ─────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node validate-slides.js <path-to-folder-or-json> [...]');
  process.exit(1);
}

for (const arg of args) {
  const abs = resolve(arg);
  const stat = statSync(abs, { throwIfNoEntry: false });
  if (!stat) {
    console.error(`Path not found: ${abs}`);
    process.exit(1);
  }

  if (stat.isFile()) {
    if (basename(abs) === 'manifest.json') {
      const folder = readdirSync(resolve(abs, '..'));
      const slideFiles = new Set(folder.filter(f => /^slide-\d+\.json$/.test(f)));
      validateManifest(abs, slideFiles);
    } else if (extname(abs) === '.json') {
      console.log(`\n📄 ${abs}`);
      validateSlide(abs);
    } else {
      console.error(`Unsupported file type: ${abs}`);
    }
  } else if (stat.isDirectory()) {
    // if the folder contains slide-*.json directly → validate it as a template folder
    const entries = readdirSync(abs);
    const hasSlides = entries.some(f => /^slide-\d+\.json$/.test(f));
    if (hasSlides) {
      validateFolder(abs);
    } else {
      // treat as parent: validate each subfolder
      for (const sub of entries) {
        const subAbs = join(abs, sub);
        if (statSync(subAbs).isDirectory()) validateFolder(subAbs);
      }
    }
  }
}

// ─── summary ─────────────────────────────────────────────────────────────────

console.log('');
if (totalErrors === 0 && totalWarnings === 0) {
  console.log('✅ All checks passed.');
} else {
  if (totalErrors > 0) console.error(`❌ ${totalErrors} error(s) found.`);
  if (totalWarnings > 0) console.warn(`⚠  ${totalWarnings} warning(s) found.`);
  if (totalErrors > 0) process.exit(1);
}
