#!/usr/bin/env node

/**
 * Deterministically repair global mobile navigation from
 * runtime-orchestration-summary.json project.sharedProjectShellContract.mobileNavigation.
 *
 * This script is intentionally narrow:
 * - It only replaces/inserts the global mobile nav block.
 * - It never edits <head>, .design, CSS, assets, or non-nav page content.
 * - It refuses to run again after a successful report already exists.
 */

import fs from 'node:fs';
import path from 'node:path';

const MAX_PAGE_HTML_BYTES = 2 * 1024 * 1024;
const MAX_JSON_BYTES = 10 * 1024 * 1024;

function parseArgs(argv) {
  const positional = [];
  let reportJson = null;
  const errors = [];

  for (const arg of argv) {
    if (arg.startsWith('--report-json=')) {
      reportJson = arg.slice('--report-json='.length);
    } else if (arg.startsWith('--')) {
      errors.push(`Unknown flag: ${arg}`);
    } else {
      positional.push(arg);
    }
  }

  return { designDir: positional[0] || null, reportJson, errors };
}

function readJson(filePath) {
  const stat = fs.statSync(filePath);
  if (!stat.isFile()) {
    throw new Error(`JSON path is not a file: ${filePath}`);
  }
  if (stat.size > MAX_JSON_BYTES) {
    throw new Error(`JSON file is too large (${stat.size} bytes; max ${MAX_JSON_BYTES}): ${filePath}`);
  }
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
}

function readHtmlFileForRepair(htmlPath) {
  const stat = fs.statSync(htmlPath);
  if (!stat.isFile()) {
    throw new Error('HTML path is not a file');
  }
  if (stat.size > MAX_PAGE_HTML_BYTES) {
    throw new Error(`HTML file is too large (${stat.size} bytes; max ${MAX_PAGE_HTML_BYTES})`);
  }
  return fs.readFileSync(htmlPath, 'utf8');
}

function countDataNavKeys(html) {
  return (String(html || '').match(/\bdata-nav-key=["'][^"']+["']/gi) || []).length;
}

function findNavBlocks(html) {
  const text = String(html || '');
  const blocks = [];
  const tagRe = /<!--[\s\S]*?-->|<script\b[\s\S]*?<\/script\s*>|<style\b[\s\S]*?<\/style\s*>|<template\b[\s\S]*?<\/template\s*>|<\/?nav\b[^>]*>/gi;
  const stack = [];
  let match;

  while ((match = tagRe.exec(text)) !== null) {
    const token = match[0];
    if (!/^<\/?nav\b/i.test(token)) continue;
    if (/^<nav\b/i.test(token)) {
      stack.push(match.index);
      continue;
    }

    const start = stack.pop();
    if (start === undefined) continue;
    if (stack.length === 0) {
      const end = match.index + token.length;
      blocks.push({ start, end, html: text.slice(start, end) });
    }
  }
  return blocks;
}

function replaceRange(text, start, end, replacement) {
  return text.slice(0, start) + replacement + text.slice(end);
}

function replaceOrInsertGlobalNav(html, canonicalNav) {
  const blocks = findNavBlocks(html);
  const explicit = blocks.find(block => /\bdata-mobile-nav=["']global["']/i.test(block.html));
  if (explicit) {
    return {
      html: replaceRange(html, explicit.start, explicit.end, canonicalNav),
      action: 'replace-data-mobile-nav-global'
    };
  }

  const keyed = blocks.find(block => countDataNavKeys(block.html) >= 3);
  if (keyed) {
    return {
      html: replaceRange(html, keyed.start, keyed.end, canonicalNav),
      action: 'replace-data-nav-key-cluster'
    };
  }

  const mainClose = html.search(/<\/main>/i);
  if (mainClose >= 0) {
    return {
      html: replaceRange(html, mainClose, mainClose, `\n${canonicalNav}\n`),
      action: 'insert-before-main-close'
    };
  }

  throw new Error('No global nav cluster and no </main> insertion point found');
}

function validateCanonicalNav(nav, activeKey) {
  if (typeof nav !== 'string' || nav.trim().length === 0) {
    throw new Error(`canonicalHtmlByKey.${activeKey} is empty`);
  }
  if (!/\bdata-mobile-nav=["']global["']/i.test(nav)) {
    throw new Error(`canonicalHtmlByKey.${activeKey} must include data-mobile-nav="global"`);
  }
  if (countDataNavKeys(nav) < 3) {
    throw new Error(`canonicalHtmlByKey.${activeKey} must contain at least 3 data-nav-key items`);
  }
}

function main() {
  const { designDir, reportJson, errors } = parseArgs(process.argv.slice(2));
  if (errors.length > 0 || !designDir || !reportJson) {
    for (const error of errors) console.error('[ERROR]', error);
    console.error('Usage: node repair-mobile-navigation-flow.mjs <design-project-path> --report-json=<path>');
    process.exit(1);
  }

  const resolvedDesignDir = path.resolve(designDir);
  const resolvedReport = path.resolve(reportJson);

  let previousFailedReportDetected = false;
  if (fs.existsSync(resolvedReport)) {
    try {
      const existing = readJson(resolvedReport);
      if (existing?.success === true) {
        console.error('[ERROR_CODE] mobile_nav_repair_already_completed');
        console.error('Error: mobile navigation repair report already records success; refusing to run again.');
        console.error('  Report:', resolvedReport);
        process.exit(1);
      }
      previousFailedReportDetected = true;
    } catch (_) {
      previousFailedReportDetected = true;
    }
  }

  const summaryPath = path.join(resolvedDesignDir, 'runtime-orchestration-summary.json');
  if (!fs.existsSync(summaryPath)) {
    console.error('[ERROR] runtime-orchestration-summary.json not found:', summaryPath);
    process.exit(1);
  }

  let summary;
  try {
    summary = readJson(summaryPath);
  } catch (error) {
    console.error('[ERROR_CODE] orchestration_summary_read_failed');
    console.error('Error: failed to read runtime-orchestration-summary.json.');
    console.error('  File:', summaryPath);
    console.error('  Reason:', error.message);
    process.exit(1);
  }
  const project = summary.project || {};
  const mobileNavigation = project.sharedProjectShellContract?.mobileNavigation;
  const canonicalHtmlByKey = mobileNavigation?.structure?.canonicalHtmlByKey;

  const failedPages = [];
  const repairedPages = [];
  const skippedPages = [];

  if (project.deviceType !== 'mobile') {
    failedPages.push({ reason: `project.deviceType must be mobile, got ${project.deviceType || 'missing'}` });
  }
  if (!mobileNavigation || mobileNavigation.applies === false) {
    failedPages.push({ reason: 'sharedProjectShellContract.mobileNavigation.applies is not true' });
  }
  if (!canonicalHtmlByKey || typeof canonicalHtmlByKey !== 'object') {
    failedPages.push({ reason: 'mobileNavigation.structure.canonicalHtmlByKey is missing' });
  }

  const pages = Array.isArray(summary.pages) ? summary.pages : [];
  if (pages.length === 0) {
    failedPages.push({ reason: 'summary.pages is empty or missing' });
  }

  if (failedPages.length === 0) {
    for (const page of pages) {
      if (!page || typeof page.htmlSrc !== 'string') continue;
      if (page.mobileNavigationApplies === false) {
        skippedPages.push({
          htmlSrc: page.htmlSrc,
          reason: page.mobileNavigationOmitReason || 'mobileNavigationApplies=false'
        });
        continue;
      }

      const activeKey = page.mobileNavigationActiveKey;
      if (!activeKey) {
        failedPages.push({ htmlSrc: page.htmlSrc, reason: 'mobileNavigationActiveKey is missing' });
        continue;
      }

      const canonicalNav = canonicalHtmlByKey[activeKey];
      try {
        validateCanonicalNav(canonicalNav, activeKey);
      } catch (error) {
        failedPages.push({ htmlSrc: page.htmlSrc, reason: error.message });
        continue;
      }

      const htmlPath = path.resolve(resolvedDesignDir, page.htmlSrc);
      const pagesDir = path.join(resolvedDesignDir, 'pages');
      if (!htmlPath.startsWith(`${pagesDir}${path.sep}`)) {
        failedPages.push({ htmlSrc: page.htmlSrc, reason: 'htmlSrc must stay under pages/' });
        continue;
      }
      if (!fs.existsSync(htmlPath)) {
        failedPages.push({ htmlSrc: page.htmlSrc, reason: 'HTML file not found' });
        continue;
      }

      try {
        const html = readHtmlFileForRepair(htmlPath);
        const result = replaceOrInsertGlobalNav(html, canonicalNav);
        fs.writeFileSync(htmlPath, result.html, 'utf8');
        repairedPages.push({ htmlSrc: page.htmlSrc, action: result.action, activeKey });
      } catch (error) {
        failedPages.push({ htmlSrc: page.htmlSrc, reason: error.message });
      }
    }
  }

  const report = {
    success: failedPages.length === 0,
    repairedPages,
    skippedPages,
    failedPages,
    repairCount: repairedPages.length,
    previousFailedReportDetected,
    checkedAt: new Date().toISOString()
  };
  writeJson(resolvedReport, report);

  console.log(`Mobile navigation repair report JSON: ${resolvedReport}`);
  if (!report.success) {
    console.error('[ERROR] Mobile navigation repair failed.');
    process.exit(1);
  }
  console.log(`[OK] Mobile navigation repaired for ${repairedPages.length} page(s).`);
}

main();
