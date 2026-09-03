#!/usr/bin/env node

/**
 * Check that large HTML files stay within the patch discipline.
 * Files over --size-threshold with more than --max-patches SearchReplace operations
 * trigger a blocking error, guiding the agent toward section-rebuild strategy.
 *
 * Usage: node check-html-patch-discipline.mjs <design-project-path> [--json] [--size-threshold=<bytes>] [--max-patches=<N>]
 *
 * Exit codes: 0 = within discipline, 1 = discipline exceeded
 */

import fs from 'node:fs';
import path from 'node:path';

const DEFAULT_SIZE_THRESHOLD = 50 * 1024; // 50KB
const DEFAULT_MAX_PATCHES = 5;

function parseArgs(argv) {
  let designDir = null;
  let json = false;
  let sizeThreshold = DEFAULT_SIZE_THRESHOLD;
  let maxPatches = DEFAULT_MAX_PATCHES;
  const errors = [];

  for (const arg of argv) {
    if (arg === '--json') {
      json = true;
    } else if (arg.startsWith('--size-threshold=')) {
      sizeThreshold = parseInt(arg.slice('--size-threshold='.length), 10);
      if (Number.isNaN(sizeThreshold) || sizeThreshold <= 0) errors.push('Invalid --size-threshold');
    } else if (arg.startsWith('--max-patches=')) {
      maxPatches = parseInt(arg.slice('--max-patches='.length), 10);
      if (Number.isNaN(maxPatches) || maxPatches <= 0) errors.push('Invalid --max-patches');
    } else if (arg.startsWith('--')) {
      errors.push(`Unknown flag: ${arg}`);
    } else if (!designDir) {
      designDir = arg;
    } else {
      errors.push(`Unexpected argument: ${arg}`);
    }
  }

  if (!designDir) errors.push('Missing design project path');
  return { designDir: designDir ? path.resolve(designDir) : null, json, sizeThreshold, maxPatches, errors };
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function main() {
  const { designDir, json, sizeThreshold, maxPatches, errors: argErrors } = parseArgs(process.argv.slice(2));
  if (argErrors.length > 0) {
    for (const error of argErrors) console.error(`[ERROR] ${error}`);
    process.exit(1);
  }

  const summaryPath = path.join(designDir, 'runtime-orchestration-summary.json');
  if (!fs.existsSync(summaryPath)) {
    const result = { success: false, errors: ['runtime-orchestration-summary.json not found'], violations: [] };
    if (json) console.log(JSON.stringify(result, null, 2));
    else console.error('[ERROR] runtime-orchestration-summary.json not found');
    process.exit(1);
  }

  const summary = readJson(summaryPath);
  const pages = Array.isArray(summary.pages) ? summary.pages : [];
  const violations = [];
  const checkedFiles = [];

  for (const page of pages) {
    const htmlSrc = page.htmlSrc;
    if (!htmlSrc) continue;

    const htmlPath = path.join(designDir, htmlSrc);
    if (!fs.existsSync(htmlPath)) continue;

    const stat = fs.statSync(htmlPath);
    const isLarge = stat.size > sizeThreshold;

    const patchHistory = Array.isArray(page.patchHistory) ? page.patchHistory : [];
    const searchReplaceCount = patchHistory.filter(
      p => p.op === 'SearchReplace' && p.target === htmlSrc
    ).length;

    checkedFiles.push({
      htmlSrc,
      fileSize: stat.size,
      isLargeFile: isLarge,
      searchReplaceCount,
    });

    if (isLarge && searchReplaceCount > maxPatches) {
      violations.push({
        htmlSrc,
        fileSize: stat.size,
        searchReplaceCount,
        maxPatches,
        sizeThreshold,
        errorCode: 'large_html_patch_discipline_exceeded',
        nextActions: ['use section-rebuild strategy instead of line-by-line SearchReplace'],
      });
    }
  }

  const success = violations.length === 0;

  const result = {
    success,
    sizeThreshold,
    maxPatches,
    checkedFileCount: checkedFiles.length,
    violationCount: violations.length,
    violations,
    checkedFiles,
  };

  if (json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    if (success) {
      console.log(`[OK] All ${checkedFiles.length} HTML file(s) within patch discipline`);
    } else {
      for (const v of violations) {
        console.error(`[FAIL] ${v.htmlSrc}: ${v.searchReplaceCount} patches on ${(v.fileSize / 1024).toFixed(1)}KB file (limit: ${maxPatches})`);
        console.error(`  → ${v.nextActions[0]}`);
      }
    }
  }

  process.exit(success ? 0 : 1);
}

main();
