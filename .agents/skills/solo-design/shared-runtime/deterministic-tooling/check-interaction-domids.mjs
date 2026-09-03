#!/usr/bin/env node

/**
 * Pre-check that all required domIds declared in runtime-orchestration-summary.json
 * actually exist in the corresponding HTML files.
 *
 * Usage: node check-interaction-domids.mjs <design-project-path> [--json]
 *
 * Exit codes: 0 = all domIds found, 1 = missing domIds detected
 */

import fs from 'node:fs';
import path from 'node:path';

const INVALID_DOMID_CHARS = /[:"'<>&\s]/;

function parseArgs(argv) {
  let designDir = null;
  let json = false;
  const errors = [];

  for (const arg of argv) {
    if (arg === '--json') {
      json = true;
    } else if (arg.startsWith('--')) {
      errors.push(`Unknown flag: ${arg}`);
    } else if (!designDir) {
      designDir = arg;
    } else {
      errors.push(`Unexpected argument: ${arg}`);
    }
  }

  if (!designDir) errors.push('Missing design project path');
  return { designDir: designDir ? path.resolve(designDir) : null, json, errors };
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function extractDomIdsFromHtml(htmlContent) {
  const found = new Set();
  const regex = /data-dom-id=["']([^"']+)["']/g;
  let match;
  while ((match = regex.exec(htmlContent)) !== null) {
    found.add(match[1]);
  }
  return found;
}

async function mapLimit(items, limit, worker) {
  const results = new Array(items.length);
  let nextIndex = 0;
  async function runWorker() {
    while (nextIndex < items.length) {
      const currentIndex = nextIndex;
      nextIndex += 1;
      results[currentIndex] = await worker(items[currentIndex], currentIndex);
    }
  }
  const workers = Array.from({ length: Math.min(limit, items.length) }, () => runWorker());
  await Promise.all(workers);
  return results;
}

async function main() {
  const { designDir, json, errors: argErrors } = parseArgs(process.argv.slice(2));
  if (argErrors.length > 0) {
    for (const error of argErrors) console.error(`[ERROR] ${error}`);
    process.exit(1);
  }

  const summaryPath = path.join(designDir, 'runtime-orchestration-summary.json');
  if (!fs.existsSync(summaryPath)) {
    const result = { success: false, errors: ['runtime-orchestration-summary.json not found'], missing: [], invalidIds: [] };
    if (json) console.log(JSON.stringify(result, null, 2));
    else console.error('[ERROR] runtime-orchestration-summary.json not found');
    process.exit(1);
  }

  const summary = readJson(summaryPath);
  const pages = Array.isArray(summary.pages) ? summary.pages : [];
  const pageResults = await mapLimit(pages, 8, async page => {
    const domIdsRequired = Array.isArray(page.domIdsRequired) ? page.domIdsRequired : [];
    const pageResult = { missing: [], invalidIds: [], errors: [] };
    if (domIdsRequired.length === 0) return pageResult;

    for (const domId of domIdsRequired) {
      if (INVALID_DOMID_CHARS.test(domId)) {
        pageResult.invalidIds.push({ pageNodeId: page.nodeId, domId, reason: 'contains invalid characters — use slug format' });
      }
    }

    const htmlSrc = page.htmlSrc;
    if (!htmlSrc) {
      pageResult.errors.push(`page ${page.nodeId}: htmlSrc is missing`);
      return pageResult;
    }

    const htmlPath = path.join(designDir, htmlSrc);
    let htmlContent;
    try {
      htmlContent = await fs.promises.readFile(htmlPath, 'utf8');
    } catch (error) {
      pageResult.errors.push(
        error?.code === 'ENOENT'
          ? `page ${page.nodeId}: HTML file not found: ${htmlSrc}`
          : `page ${page.nodeId}: failed to read HTML file ${htmlSrc}: ${error.message}`
      );
      return pageResult;
    }

    const foundDomIds = extractDomIdsFromHtml(htmlContent);

    for (const domId of domIdsRequired) {
      if (!foundDomIds.has(domId)) {
        pageResult.missing.push({ pageNodeId: page.nodeId, htmlSrc, domId });
      }
    }
    return pageResult;
  });

  const missing = pageResults.flatMap(result => result.missing);
  const invalidIds = pageResults.flatMap(result => result.invalidIds);
  const errors = pageResults.flatMap(result => result.errors);

  const success = missing.length === 0 && invalidIds.length === 0 && errors.length === 0;

  const result = {
    success,
    checkedPages: pages.filter(p => Array.isArray(p.domIdsRequired) && p.domIdsRequired.length > 0).length,
    totalDomIdsChecked: pages.reduce((sum, p) => sum + (Array.isArray(p.domIdsRequired) ? p.domIdsRequired.length : 0), 0),
    missingCount: missing.length,
    invalidIdCount: invalidIds.length,
    missing,
    invalidIds,
    errors,
  };

  if (json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    if (success) {
      console.log(`[OK] All ${result.totalDomIdsChecked} required domId(s) found in HTML`);
    } else {
      if (missing.length > 0) {
        console.error(`[FAIL] ${missing.length} missing domId(s):`);
        for (const m of missing) console.error(`  - ${m.domId} not found in ${m.htmlSrc} (page: ${m.pageNodeId})`);
      }
      if (invalidIds.length > 0) {
        console.error(`[FAIL] ${invalidIds.length} invalid domId format(s):`);
        for (const inv of invalidIds) console.error(`  - "${inv.domId}" in page ${inv.pageNodeId}: ${inv.reason}`);
      }
      for (const err of errors) console.error(`[ERROR] ${err}`);
    }
  }

  process.exit(success ? 0 : 1);
}

main().catch(error => {
  console.error(`[ERROR] ${error?.stack || error?.message || String(error)}`);
  process.exit(1);
});
