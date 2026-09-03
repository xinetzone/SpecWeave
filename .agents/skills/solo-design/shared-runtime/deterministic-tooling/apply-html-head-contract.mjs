/**
 * Generate an HTML page skeleton from a Design Library CSS file,
 * eliminating the token cost of having a sub-Agent hand-fill a template.
 *
 * The CSS content is INLINED into <style id="theme-vars"> (not linked via <link>)
 * because the canvas SDK renders pages in iframe srcdoc mode where external
 * relative paths cannot be resolved.
 *
 * Mode 1 - Generate a new HTML skeleton:
 *   node apply-html-head-contract.mjs <css-file-or-library-dir> <output-html> [--title="Page Title"] [--lang=zh-CN] [--prefix=volcano] [--theme=dark] [--charts]
 *   Refuses to overwrite an existing file with non-empty <main>. Use --force-skeleton only for an intentional reset.
 *
 * Mode 2 - Replace the <head> in existing HTML (keep <main> content unchanged):
 *   node apply-html-head-contract.mjs <css-file-or-library-dir> <existing-html> --replace-head [--prefix=volcano] [--charts]
 *   Multiple files: node apply-html-head-contract.mjs <css-file-or-library-dir> page1.html page2.html --replace-head
 *   Non-infrastructure custom <style> blocks found in the old <head> are moved
 *   to the end of <body>, keeping <head> owned by this script.
 *
 * Exit codes: 0 = success, 1 = failure
 */

import fs from 'node:fs';
import path from 'node:path';

const MAX_EXISTING_HTML_BYTES = 2 * 1024 * 1024;

/**
 * Build @font-face blocks from css.json font.assets.
 * Only generates for custom fonts (source: 'custom') using relative zipPath.
 * Skips fonts that already have a matching @font-face in the CSS content.
 */
function buildFontFaceFromAssets(cssDir, cssContent) {
  const cssJsonPath = path.join(cssDir, 'css.json');
  if (!fs.existsSync(cssJsonPath)) return '';

  let cssJson;
  try {
    cssJson = JSON.parse(fs.readFileSync(cssJsonPath, 'utf8'));
  } catch (_) {
    return '';
  }

  const assets = cssJson?.font?.assets;
  if (!assets || typeof assets !== 'object') return '';

  const blocks = [];
  for (const [name, rawAsset] of Object.entries(assets)) {
    const asset = typeof rawAsset === 'string' ? { url: rawAsset } : rawAsset;
    if (!asset) continue;

    const family = asset.family || name;

    // Skip if CSS already contains @font-face for this family
    if (cssContent.includes(`font-family: '${family}'`) || cssContent.includes(`font-family: "${family}"`)) {
      continue;
    }

    let src;
    if (asset.source === 'custom' && asset.zipPath) {
      // Custom font: inline as base64 data URI (iframe srcdoc cannot resolve relative paths)
      src = buildFontSrcForCustomAsset(cssDir, asset, name);
      if (!src) continue;
    } else if (asset.url) {
      // Builtin font: use absolute URL
      const format = asset.format || fontFormatFromUrl(asset.url);
      src = `url('${asset.url}')${format ? ` format('${format}')` : ''}`;
    } else {
      continue;
    }

    let descriptor = `  font-family: '${family}';\n  src: ${src};`;
    if (asset.weight) descriptor += `\n  font-weight: ${asset.weight};`;
    if (asset.style) descriptor += `\n  font-style: ${asset.style};`;
    descriptor += `\n  font-display: swap;`;

    blocks.push(`@font-face {\n${descriptor}\n}`);
  }

  return blocks.length > 0 ? blocks.join('\n') + '\n\n' : '';
}

function fontFormatFromUrl(url) {
  if (!url) return '';
  if (url.endsWith('.woff2')) return 'woff2';
  if (url.endsWith('.woff')) return 'woff';
  if (url.endsWith('.ttf')) return 'truetype';
  if (url.endsWith('.otf')) return 'opentype';
  return '';
}

function fontMimeFromFormat(format) {
  return {
    woff2: 'font/woff2',
    woff: 'font/woff',
    truetype: 'font/ttf',
    opentype: 'font/otf',
  }[format] || 'application/octet-stream';
}

function buildFontSrcForCustomAsset(cssDir, asset, name = '') {
  const fontPath = path.resolve(cssDir, asset.zipPath);
  const format = asset.format || fontFormatFromUrl(asset.zipPath);

  if (!fs.existsSync(fontPath)) {
    console.error(`Warning: custom font file not found for "${name || asset.family || 'unknown'}": ${asset.zipPath}`);
    return null;
  }

  const stat = fs.statSync(fontPath);
  if (stat.size > 20 * 1024 * 1024) {
    console.warn(`Warning: font file too large (${(stat.size / 1024 / 1024).toFixed(1)}MB), skipping: ${asset.zipPath}`);
    return null;
  }

  try {
    const data = fs.readFileSync(fontPath).toString('base64');
    return `url('data:${fontMimeFromFormat(format)};base64,${data}')${format ? ` format('${format}')` : ''}`;
  } catch (error) {
    console.error(`Warning: failed to read custom font for "${name || asset.family || 'unknown'}": ${asset.zipPath}`, error.message);
    return null;
  }
}

function parseArgs(argv) {
  const positional = [];
  const errors = [];
  const knownValueFlags = new Set(['--title', '--lang', '--prefix', '--theme']);
  const knownBooleanFlags = new Set(['--replace-head', '--charts', '--force-skeleton']);
  const unsupportedCommonFlags = ['--project', '--page', '--css', '--html', '--output'];
  let title = 'Untitled';
  let lang = 'en';
  let prefix = '';
  let theme = 'light';
  let themeExplicit = false;
  let replaceHead = false;
  let charts = false;
  let forceSkeleton = false;

  for (const arg of argv) {
    if (arg.startsWith('--title=')) {
      title = arg.slice('--title='.length);
    } else if (arg.startsWith('--lang=')) {
      lang = arg.slice('--lang='.length);
    } else if (arg.startsWith('--prefix=')) {
      prefix = arg.slice('--prefix='.length);
    } else if (arg.startsWith('--theme=')) {
      theme = arg.slice('--theme='.length);
      themeExplicit = true;
    } else if (arg === '--replace-head') {
      replaceHead = true;
    } else if (arg === '--charts') {
      charts = true;
    } else if (arg === '--force-skeleton') {
      forceSkeleton = true;
    } else if (knownValueFlags.has(arg)) {
      errors.push(`Invalid ${arg} syntax. Use ${arg}=value, for example ${arg}="Page Title".`);
    } else if (unsupportedCommonFlags.some((flag) => arg === flag || arg.startsWith(`${flag}=`))) {
      errors.push(`Unsupported flag ${arg}. Correct usage: node apply-html-head-contract.mjs <css-file-or-library-dir> <output-html> [--title="Page Title"] [--lang=zh-CN] [--prefix=brand] [--charts].`);
    } else if (arg.startsWith('--') && !knownBooleanFlags.has(arg) && ![...knownValueFlags].some((flag) => arg.startsWith(`${flag}=`))) {
      errors.push(`Unknown flag ${arg}.`);
    } else {
      positional.push(arg);
    }
  }

  return { positional, title, lang, prefix, theme, themeExplicit, replaceHead, charts, forceSkeleton, errors };
}

function resolveCSSPath(input) {
  const resolved = path.resolve(input);
  if (fs.existsSync(resolved) && fs.statSync(resolved).isDirectory()) {
    const cssPath = path.join(resolved, 'colors_and_type.css');
    if (!fs.existsSync(cssPath)) {
      console.error('Error: colors_and_type.css not found in directory');
      console.error('  Directory:', resolved);
      process.exit(1);
    }
    return cssPath;
  }
  if (!fs.existsSync(resolved)) {
    console.error('Error: CSS file not found');
    console.error('  Path:', resolved);
    process.exit(1);
  }
  return resolved;
}

function collectRootBodies(cssContent) {
  return [...cssContent.matchAll(/:root\s*\{([^}]*)\}/gs)]
    .map(match => match[1])
    .join('\n');
}

function collectThemeInlineBodies(cssContent) {
  return [...cssContent.matchAll(/@theme\s+inline\s*\{([^}]*)\}/gs)]
    .map(match => match[1])
    .join('\n');
}

function collectThemeInlineMappings(cssContent) {
  const themeBody = collectThemeInlineBodies(cssContent);
  const color = new Map();
  const radius = new Map();
  for (const match of themeBody.matchAll(/--color-([a-zA-Z0-9-]+)\s*:\s*var\((--[a-zA-Z0-9-]+)\)/g)) {
    color.set(match[1], match[2]);
  }
  for (const match of themeBody.matchAll(/--radius-([a-zA-Z0-9-]+)\s*:\s*var\((--[a-zA-Z0-9-]+)\)/g)) {
    radius.set(match[1], match[2]);
  }
  return { color, radius };
}

function collectCssCustomProperties(cssContent) {
  const rootBodies = collectRootBodies(cssContent);
  const source = rootBodies || cssContent;
  return new Set([...source.matchAll(/--([a-zA-Z0-9-]+)\s*:/g)].map(match => match[1]));
}

function firstExistingVar(varNames, allVars) {
  const found = varNames.find(name => allVars.has(name));
  return found ? `var(--${found})` : null;
}

function detectPrefix(cssContent) {
  const rootBody = collectRootBodies(cssContent);
  const source = rootBody || collectThemeInlineBodies(cssContent);
  if (!source) return null;

  if (/--background\s*:/.test(source) && /--foreground\s*:/.test(source)) {
    return null;
  }

  const allFirstSegments = [...source.matchAll(/--([a-zA-Z][a-zA-Z0-9]*)-/g)].map(m => m[1]);
  if (allFirstSegments.length === 0) return null;

  const semanticPattern = /--([a-zA-Z][a-zA-Z0-9]*)-(?:primary|background|foreground|surface|radius|shadow)/g;
  const semanticHits = [...source.matchAll(semanticPattern)].map(m => m[1]);

  if (semanticHits.length > 0) {
    return semanticHits[0];
  }

  const frequency = {};
  for (const seg of allFirstSegments) frequency[seg] = (frequency[seg] || 0) + 1;
  const sorted = Object.entries(frequency).sort((a, b) => b[1] - a[1]);
  return sorted[0][0];
}

const THEME_COLOR_TOKENS = [
  'background', 'foreground', 'card', 'card-foreground',
  'popover', 'popover-foreground', 'primary', 'primary-foreground',
  'secondary', 'secondary-foreground', 'muted', 'muted-foreground',
  'accent', 'accent-foreground', 'destructive', 'destructive-foreground',
  'border', 'input', 'ring',
  'chart-1', 'chart-2', 'chart-3', 'chart-4', 'chart-5',
  'sidebar', 'sidebar-foreground', 'sidebar-primary',
  'sidebar-primary-foreground', 'sidebar-accent', 'sidebar-accent-foreground',
];

const ALIAS_TO_SEMANTIC = {
  bg: 'background',
  fg: 'foreground',
  rule: 'border',
  link: 'ring',
};

const REQUIRED_THEME_COLOR_MAPPINGS = [
  'background',
  'foreground',
  'card',
  'primary',
  'border',
  'muted',
];

const REQUIRED_RADIUS_MAPPINGS = ['sm', 'md', 'lg'];

/**
 * Resolve Tailwind semantic tokens to actual CSS custom properties.
 */
function resolveThemeTokenMappings(cssContent, prefix) {
  const rootBody = collectRootBodies(cssContent);
  const source = rootBody || collectThemeInlineBodies(cssContent) || cssContent;
  const inlineMappings = collectThemeInlineMappings(cssContent);
  const allVarNames = collectCssCustomProperties(cssContent);
  const color = new Map(inlineMappings.color);
  const radius = new Map(inlineMappings.radius);
  const mapped = new Set();
  for (const token of color.keys()) mapped.add(token);

  if (prefix) {
    const varPattern = new RegExp(`--${prefix}-([a-zA-Z0-9-]+)`, 'g');
    const semanticNames = new Set();
    let match;
    while ((match = varPattern.exec(source)) !== null) {
      semanticNames.add(match[1]);
    }
    for (const token of THEME_COLOR_TOKENS) {
      if (semanticNames.has(token)) {
        color.set(token, `--${prefix}-${token}`);
        mapped.add(token);
      }
    }
    for (const [shortName, twToken] of Object.entries(ALIAS_TO_SEMANTIC)) {
      if (semanticNames.has(shortName) && !mapped.has(twToken)) {
        color.set(twToken, `--${prefix}-${shortName}`);
        mapped.add(twToken);
      }
    }
    for (const token of THEME_COLOR_TOKENS) {
      if (mapped.has(token)) continue;
      if (allVarNames.has(token)) {
        color.set(token, `--${token}`);
        mapped.add(token);
        continue;
      }
      if (allVarNames.has(`color-${token}`)) {
        color.set(token, `--color-${token}`);
        mapped.add(token);
      }
    }
    const prefixedRadiusDirect = { 'radius-sm': 'sm', 'radius-md': 'md', 'radius-lg': 'lg', 'radius-xl': 'xl' };
    const prefixedRadiusFallback = { 'radius-small': 'sm', 'radius-medium': 'md', 'radius-large': 'lg', 'radius-xlarge': 'xl' };
    for (const [cssName, twName] of Object.entries(prefixedRadiusDirect)) {
      if (semanticNames.has(cssName)) {
        radius.set(twName, `--${prefix}-${cssName}`);
      }
    }
    for (const [cssName, twName] of Object.entries(prefixedRadiusFallback)) {
      if (semanticNames.has(cssName) && !radius.has(twName)) {
        radius.set(twName, `--${prefix}-${cssName}`);
      }
    }
  } else {
    for (const token of THEME_COLOR_TOKENS) {
      if (allVarNames.has(token)) {
        color.set(token, `--${token}`);
        mapped.add(token);
        continue;
      }
      if (allVarNames.has(`color-${token}`)) {
        color.set(token, `--color-${token}`);
        mapped.add(token);
      }
    }

    for (const [shortName, twToken] of Object.entries(ALIAS_TO_SEMANTIC)) {
      if (allVarNames.has(shortName) && !mapped.has(twToken)) {
        color.set(twToken, `--${shortName}`);
      }
    }

    const radiusDirect = { 'radius-sm': 'sm', 'radius-md': 'md', 'radius-lg': 'lg', 'radius-xl': 'xl' };
    const radiusFallback = { 'radius-small': 'sm', 'radius-medium': 'md', 'radius-large': 'lg', 'radius-xlarge': 'xl' };
    for (const [cssName, twName] of Object.entries(radiusDirect)) {
      if (allVarNames.has(cssName)) {
        radius.set(twName, `--${cssName}`);
      }
    }
    for (const [cssName, twName] of Object.entries(radiusFallback)) {
      if (allVarNames.has(cssName) && !radius.has(twName)) {
        radius.set(twName, `--${cssName}`);
      }
    }
  }

  return { color, radius };
}

function formatExpectedSemanticVariables(prefix, missingColors, missingRadius) {
  const colorExamples = missingColors.map((token) => {
    if (prefix) return `--${prefix}-${token}`;
    return `--${token} or --color-${token}`;
  });
  const radiusExamples = missingRadius.map((token) => {
    if (prefix) {
      const longName = { sm: 'small', md: 'medium', lg: 'large', xl: 'xlarge' }[token] || token;
      return `--${prefix}-radius-${token} or --${prefix}-radius-${longName}`;
    }
    const longName = { sm: 'small', md: 'medium', lg: 'large', xl: 'xlarge' }[token] || token;
    return `--radius-${token} or --radius-${longName}`;
  });

  return [...colorExamples, ...radiusExamples].join(', ');
}

function validateThemeMappings(cssContent, prefix, context = 'CSS') {
  const mappings = resolveThemeTokenMappings(cssContent, prefix);
  const missingColors = REQUIRED_THEME_COLOR_MAPPINGS.filter((token) => !mappings.color.has(token));
  const presentRadiusCount = REQUIRED_RADIUS_MAPPINGS.filter((token) => mappings.radius.has(token)).length;
  const missingRadius = presentRadiusCount >= 2
    ? []
    : REQUIRED_RADIUS_MAPPINGS.filter((token) => !mappings.radius.has(token));

  if (missingColors.length > 0 || missingRadius.length > 0) {
    const prefixLabel = prefix || 'prefixless';
    const expected = formatExpectedSemanticVariables(prefix, missingColors, missingRadius);
    throw new Error(
      `CSS semantic theme mapping failed for ${context} (prefix: ${prefixLabel}). ` +
      `Missing semantic mappings: ${[...missingColors, ...missingRadius.map((token) => `radius-${token}`)].join(', ')}. ` +
      `Define semantic aliases before dispatching page generation. Expected variables include: ${expected}.`
    );
  }

  return mappings;
}

/**
 * Build @theme inline block that bridges brand-prefixed CSS variables
 * to Tailwind v4 semantic color/radius tokens.
 */
function buildThemeInline(cssContent, prefix, mappings = resolveThemeTokenMappings(cssContent, prefix)) {
  const lines = [];

  for (const [token, varName] of mappings.color.entries()) {
    lines.push(`    --color-${token}: var(${varName});`);
  }
  for (const [token, varName] of mappings.radius.entries()) {
    lines.push(`    --radius-${token}: var(${varName});`);
  }

  if (lines.length === 0) return '';
  return `@theme inline {\n${lines.join('\n')}\n  }`;
}

/**
 * Runtime fallback for Tailwind semantic color classes.
 *
 * Canvas renders pages through iframe srcdoc. If Tailwind browser runtime does
 * not compile @theme inline in time, semantic classes such as text-foreground
 * and bg-card otherwise degrade to browser defaults. This fallback mirrors the
 * same semantic token mapping; it does not redefine layout utilities.
 */
function buildSemanticFallbackCSS(cssContent, prefix, mappings = resolveThemeTokenMappings(cssContent, prefix)) {
  const colorMappings = mappings.color;
  const lines = [];

  for (const [token, varName] of colorMappings.entries()) {
    lines.push(`      .bg-${token} { background-color: var(${varName}); }`);
    lines.push(`      .text-${token} { color: var(${varName}); }`);
    lines.push(`      .border-${token} { border-color: var(${varName}); }`);
    lines.push(`      .ring-${token} { --tw-ring-color: var(${varName}); }`);
  }

  if (lines.length === 0) return '';
  return lines.join('\n');
}

/**
 * Find the best background and foreground CSS variables from the actual CSS content.
 * Searches for common naming patterns in priority order.
 */
function findBodyVars(cssContent, prefix) {
  const allVars = collectCssCustomProperties(cssContent);
  if (allVars.size === 0) {
    return { bg: '#ffffff', fg: '#0f172a' };
  }

  const bgCandidates = prefix
    ? [
        `${prefix}-background`,
        `${prefix}-bg`,
        `${prefix}-bg-primary`,
        `${prefix}-bg-base`,
        `${prefix}-surface`,
        'color-background',
        'background',
        'bg',
        'surface'
      ]
    : ['color-background', 'background', 'bg', 'bg-base-default', 'bg-base', 'surface'];

  const fgCandidates = prefix
    ? [
        `${prefix}-foreground`,
        `${prefix}-fg`,
        `${prefix}-text-primary`,
        `${prefix}-text-default`,
        'color-foreground',
        'foreground',
        'fg',
        'text-primary',
        'text-default'
      ]
    : ['color-foreground', 'foreground', 'fg', 'text-primary', 'text-default'];

  return {
    bg: firstExistingVar(bgCandidates, allVars) || '#ffffff',
    fg: firstExistingVar(fgCandidates, allVars) || '#0f172a'
  };
}

/**
 * Load components.css from the Library directory if present.
 * Returns the CSS content string, or empty string if not found.
 */
function loadComponentsCSS(cssDir) {
  if (!cssDir) return '';
  const compPath = path.join(cssDir, 'components.css');
  if (!fs.existsSync(compPath)) return '';
  const content = fs.readFileSync(compPath, 'utf-8').trim();
  if (!content) return '';
  console.log('[INFO] Found components.css, inlining as <style id="component-vars">');
  return content;
}

function buildHead(cssContent, prefix, title, lang, cssDir, charts) {
  const mappings = validateThemeMappings(cssContent, prefix, 'apply-html-head-contract.mjs');
  const themeInline = buildThemeInline(cssContent, prefix, mappings);
  const semanticFallback = buildSemanticFallbackCSS(cssContent, prefix, mappings);
  if (!themeInline || !semanticFallback) {
    throw new Error(
      `CSS semantic theme mapping failed for apply-html-head-contract.mjs (prefix: ${prefix || 'prefixless'}). ` +
      'Generated @theme inline or semantic-token-fallback is empty.'
    );
  }
  const { bg, fg } = findBodyVars(cssContent, prefix);
  const fontFaceBlocks = cssDir ? buildFontFaceFromAssets(cssDir, cssContent) : '';
  const componentCSS = loadComponentsCSS(cssDir);
  const componentBlock = componentCSS
    ? `\n    <style id="component-vars">\n${componentCSS}\n    </style>`
    : '';
  const semanticFallbackBlock = semanticFallback
    ? `\n    <style id="semantic-token-fallback">\n${semanticFallback}\n    </style>`
    : '';

  return `<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <style id="theme-vars">
${fontFaceBlocks}${cssContent}
    </style>${componentBlock}
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.3.1/dist/index.global.js"></script>
    <script src="https://unpkg.com/lucide@1.8.0/dist/umd/lucide.min.js"></script>
${charts ? '    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"></script>\n' : ''}    <style type="text/tailwindcss">
  ${themeInline}
  @layer base {
    body { background: ${bg}; color: ${fg}; }
    td, th { @apply break-words; word-break: break-all; word-break: auto-phrase; }
    th { @apply whitespace-nowrap; }
  }
    </style>${semanticFallbackBlock}
    <style>
      .no-scrollbar::-webkit-scrollbar { display: none; }
      .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
      [data-icon] {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        -webkit-mask-size: contain;
        mask-size: contain;
        -webkit-mask-repeat: no-repeat;
        mask-repeat: no-repeat;
        -webkit-mask-position: center;
        mask-position: center;
        background-color: currentColor;
      }
    </style>
</head>`;
}

function buildHTML(cssContent, prefix, title, lang, theme, cssDir, charts) {
  const head = buildHead(cssContent, prefix, title, lang, cssDir, charts);
  return `<!DOCTYPE html>
<html lang="${lang}" class="${theme}">
${head}
<body class="min-h-screen font-sans antialiased">
    <main>
    </main>
    <script>lucide.createIcons();</script>
</body>
</html>
`;
}

function extractMainContent(html) {
  const match = String(html || '').match(/<main\b[^>]*>([\s\S]*?)<\/main>/i);
  return match ? match[1] : null;
}

function hasMeaningfulMainContent(html) {
  const main = extractMainContent(html);
  if (main === null) return false;

  const cleaned = main
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<script\b[\s\S]*?<\/script>/gi, '')
    .replace(/<style\b[\s\S]*?<\/style>/gi, '')
    .trim();
  if (cleaned.length === 0) return false;

  if (/<\s*(img|svg|canvas|video|picture|iframe|table|section|article|ul|ol|li|button|input|select|textarea)\b/i.test(cleaned)) {
    return true;
  }
  if (/<[^>]+>/.test(cleaned)) {
    return true;
  }

  const stripped = cleaned
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/gi, '')
    .trim();
  return stripped.length > 0;
}

function readExistingHtmlFile(htmlPath, context) {
  let stat;
  try {
    stat = fs.statSync(htmlPath);
  } catch (error) {
    console.error(`[ERROR_CODE] ${context}_stat_failed`);
    console.error('Error: failed to inspect existing HTML file.');
    console.error('  File:', htmlPath);
    console.error('  Reason:', error.message);
    return null;
  }
  if (!stat.isFile()) {
    console.error(`[ERROR_CODE] ${context}_not_file`);
    console.error('Error: refusing to inspect an existing path that is not a file.');
    console.error('  File:', htmlPath);
    return null;
  }
  if (stat.size > MAX_EXISTING_HTML_BYTES) {
    console.error(`[ERROR_CODE] ${context}_too_large`);
    console.error(`Error: refusing to inspect existing HTML larger than ${MAX_EXISTING_HTML_BYTES} bytes.`);
    console.error('  File:', htmlPath);
    console.error('  Move large inline assets to assets/ before re-running this command.');
    return null;
  }

  try {
    return fs.readFileSync(htmlPath, 'utf-8');
  } catch (error) {
    console.error(`[ERROR_CODE] ${context}_read_failed`);
    console.error('Error: failed to read existing HTML file.');
    console.error('  File:', htmlPath);
    console.error('  Reason:', error.message);
    return null;
  }
}

function canWriteSkeleton(outputFile, forceSkeleton) {
  if (forceSkeleton || !fs.existsSync(outputFile)) return true;

  const existing = readExistingHtmlFile(outputFile, 'existing_output');
  if (existing === null) {
    console.error('  Use --force-skeleton only if you intentionally want to reset this file.');
    return false;
  }
  const hasHead = /<head[\s\S]*?<\/head>/i.test(existing);
  const hasMain = /<main\b[\s\S]*?<\/main>/i.test(existing);
  if (!hasHead || !hasMain) return true;
  if (!hasMeaningfulMainContent(existing)) return true;

  console.error('[ERROR_CODE] non_empty_main_overwrite_refused');
  console.error('Error: refusing to overwrite existing HTML with non-empty <main>.');
  console.error('  File:', outputFile);
  console.error('  Use --replace-head to preserve body content, or --force-skeleton to intentionally reset.');
  return false;
}

function assertGeneratedSkeleton(htmlFile, content) {
  if (!content || content.trim().length === 0) {
    throw new Error(`fill-html-head generated empty skeleton: ${htmlFile}`);
  }
  if (!/<main\b[^>]*>[\s\S]*<\/main>/i.test(content)) {
    throw new Error(`fill-html-head generated skeleton without <main>: ${htmlFile}`);
  }
  if (!/id=["']theme-vars["']/.test(content)) {
    throw new Error(`fill-html-head generated skeleton without theme-vars: ${htmlFile}`);
  }
}

function ensureHtmlThemeClass(content, fallbackTheme, themeExplicit) {
  const theme = fallbackTheme === 'dark' ? 'dark' : 'light';
  return content.replace(/<html\b([^>]*)>/i, (htmlTag, attrs = '') => {
    const classMatch = attrs.match(/\bclass=(["'])([^"']*)\1/i);
    if (classMatch) {
      const currentClasses = classMatch[2].split(/\s+/).filter(Boolean);
      if (!themeExplicit && currentClasses.some(token => /^(?:light|dark)$/i.test(token))) {
        return htmlTag;
      }
      const nextClass = currentClasses
        .filter(token => token && !/^(?:light|dark)$/i.test(token))
        .concat(theme)
        .join(' ');
      return htmlTag.replace(classMatch[0], `class=${classMatch[1]}${nextClass}${classMatch[1]}`);
    }
    return `<html${attrs} class="${theme}">`;
  });
}

function replaceHeadInFile(htmlPath, cssContent, prefix, cssDir, charts, theme, themeExplicit) {
  const content = readExistingHtmlFile(htmlPath, 'replace_head_input');
  if (content === null) return false;
  const headMatch = content.match(/<head[\s\S]*?<\/head>/i);
  if (!headMatch) {
    console.error('Error: <head> tag not found');
    console.error('  File:', htmlPath);
    return false;
  }

  // Detect custom style blocks in head that would be lost
  const customStylesInHead = detectCustomStylesInHead(headMatch[0]);

  const titleMatch = content.match(/<title>(.*?)<\/title>/i);
  const title = titleMatch ? titleMatch[1] : 'Untitled';
  const langMatch = content.match(/<html[^>]*\slang="([^"]+)"/i);
  const lang = langMatch ? langMatch[1] : 'en';

  let newHead;
  try {
    newHead = buildHead(cssContent, prefix, title, lang, cssDir, charts);
  } catch (error) {
    console.error('Error:', error.message);
    console.error('  File:', htmlPath);
    return false;
  }

  let result = ensureHtmlThemeClass(
    content.replace(/<head[\s\S]*?<\/head>/i, newHead),
    theme,
    themeExplicit
  );
  if (customStylesInHead.length > 0) {
    const moved = moveCustomStylesToBodyEnd(result, customStylesInHead);
    if (!moved) {
      console.error('Error: custom <style> blocks were found in <head>, but </body> was not found for relocation.');
      console.error('  File:', htmlPath);
      console.error('  Fix: move custom <style> blocks before </body>, then re-run --replace-head.');
      return false;
    }
    result = moved;
    console.log('[WARN] Moved', customStylesInHead.length, 'custom style block(s) from <head> to <body>:', htmlPath);
  }

  const beforeMain = extractMainContent(content);
  const afterMain = extractMainContent(result);
  if (beforeMain !== afterMain) {
    console.error('[ERROR_CODE] replace_head_changed_main');
    console.error('Error: --replace-head changed <main> content; refusing to write.');
    console.error('  File:', htmlPath);
    return false;
  }

  fs.writeFileSync(htmlPath, result, 'utf-8');

  console.log('[MODE] replace-head');
  return true;
}

function moveCustomStylesToBodyEnd(content, customStyles) {
  if (!/<\/body>/i.test(content)) {
    return null;
  }

  const missingStyles = customStyles.filter((styleBlock) => !content.includes(styleBlock));
  if (missingStyles.length === 0) {
    return content;
  }

  const injection = '\n' + missingStyles.map((styleBlock) => '    ' + styleBlock).join('\n') + '\n';
  return content.replace(/<\/body>/i, `${injection}</body>`);
}

/**
 * Detect non-infrastructure <style> blocks in <head>.
 * Infrastructure blocks (generated by this script) are excluded.
 */
function detectCustomStylesInHead(headHtml) {
  const styleRegex = /<style[^>]*>[\s\S]*?<\/style>/gi;
  const matches = headHtml.match(styleRegex) || [];

  return matches.filter(block => {
    // Exclude theme-vars (will be regenerated by this script)
    if (/id=["']theme-vars["']/i.test(block)) return false;
    // Exclude component-vars (will be regenerated by this script)
    if (/id=["']component-vars["']/i.test(block)) return false;
    // Exclude semantic-token-fallback (will be regenerated by this script)
    if (/id=["']semantic-token-fallback["']/i.test(block)) return false;
    // Exclude tailwindcss type (will be regenerated by this script)
    if (/type=["']text\/tailwindcss["']/i.test(block)) return false;
    // Exclude blocks that only contain no-scrollbar and/or [data-icon] rules
    if (/\.no-scrollbar/.test(block) || /\[data-icon\]/.test(block)) {
      const inner = block.replace(/<style[^>]*>/i, '').replace(/<\/style>/i, '').trim();
      const stripped = inner
        .replace(/\.no-scrollbar[^}]*\{[^}]*\}/g, '')
        .replace(/\[data-icon\][^}]*\{[^}]*\}/g, '')
        .trim();
      if (stripped.length === 0) return false;
    }
    // Exclude empty style blocks
    const inner = block.replace(/<style[^>]*>/i, '').replace(/<\/style>/i, '').trim();
    if (inner.length === 0) return false;
    return true;
  });
}

function printUsage(replaceHead = false) {
  console.error('========================================');
  console.error('Usage');
  console.error('========================================');
  console.error('');
  console.error(replaceHead
    ? 'Mode: Replace <head> in existing HTML'
    : 'Mode: Generate new HTML skeleton');
  console.error('');
  console.error(replaceHead
    ? 'Command: node apply-html-head-contract.mjs <css-file-or-library-dir> <html-file> [html-file2 ...] --replace-head [--prefix=volcano] [--charts]'
    : 'Command: node apply-html-head-contract.mjs <css-file-or-library-dir> <output-html> [--title="Page Title"] [--lang=zh-CN] [--prefix=volcano] [--charts] [--force-skeleton]');
  console.error('');
}

function looksLikeHtml(filePath) {
  return /\.html?$/i.test(filePath || '');
}

function looksLikeCss(filePath) {
  return /\.css$/i.test(filePath || '');
}

function main() {
  const { positional, title, lang, prefix: userPrefix, theme, themeExplicit, replaceHead, charts, forceSkeleton, errors } = parseArgs(process.argv.slice(2));

  if (errors.length > 0) {
    errors.forEach((error) => console.error(`[ERROR] ${error}`));
    printUsage(replaceHead);
    process.exit(1);
  }

  if (positional.length < 2) {
    printUsage(replaceHead);
    process.exit(1);
  }

  if (!replaceHead && looksLikeHtml(positional[0]) && looksLikeCss(positional[1])) {
    console.error('[ERROR] CSS and HTML arguments look swapped.');
    console.error('Correct: node apply-html-head-contract.mjs <colors_and_type.css> <output.html> --title="..." --prefix=...');
    printUsage(false);
    process.exit(1);
  }

  if (replaceHead && positional.slice(1).some((filePath) => !looksLikeHtml(filePath))) {
    console.error('[ERROR] --replace-head only accepts HTML files after the CSS/library path.');
    printUsage(true);
    process.exit(1);
  }

  const cssPath = resolveCSSPath(positional[0]);
  const cssContent = fs.readFileSync(cssPath, 'utf-8');
  const cssDir = path.dirname(cssPath);
  const prefix = userPrefix || detectPrefix(cssContent);

  console.log('========================================');
  console.log(replaceHead ? 'Replacing HTML <head>' : 'Generating HTML skeleton');
  console.log('========================================');
  console.log('CSS file:', cssPath);
  console.log('Brand prefix:', prefix || '(none — prefixless mode)');

  if (replaceHead) {
    const htmlFiles = positional.slice(1).map((f) => path.resolve(f));
    console.log('Files to process:', htmlFiles.length);
    console.log('');

    let failCount = 0;
    let successCount = 0;

    for (const htmlFile of htmlFiles) {
      if (!fs.existsSync(htmlFile)) {
        console.error('[SKIP] File not found:', htmlFile);
        failCount++;
        continue;
      }
      const ok = replaceHeadInFile(htmlFile, cssContent, prefix, cssDir, charts, theme, themeExplicit);
      if (ok) {
        console.log('[OK] Success:', htmlFile);
        successCount++;
      } else {
        failCount++;
      }
    }

    console.log('');
    console.log('========================================');
    console.log('Processing complete');
    console.log('----------------------------------------');
    console.log('Success:', successCount, 'file(s)');
    console.log('Failed:', failCount, 'file(s)');
    console.log('========================================');
    if (failCount > 0) process.exit(1);
  } else {
    const outputFile = path.resolve(positional[1]);
    const outputDir = path.dirname(outputFile);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    console.log('Output file:', outputFile);
    console.log('Page title:', title);
    console.log('Language:', lang);
    console.log('');

    if (!canWriteSkeleton(outputFile, forceSkeleton)) {
      process.exit(1);
    }

    let html;
    try {
      html = buildHTML(cssContent, prefix, title, lang, theme, cssDir, charts);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
    try {
      assertGeneratedSkeleton(outputFile, html);
    } catch (error) {
      console.error('[ERROR_CODE] invalid_generated_skeleton');
      console.error('Error:', error.message);
      process.exit(1);
    }
    fs.writeFileSync(outputFile, html, 'utf-8');

    console.log('[MODE] skeleton');
    console.log('[OK] HTML skeleton generated');
    console.log('========================================');
  }
}

main();
