#!/usr/bin/env node

/**
 * Check that intent workflow directories do not directly read each other and
 * that visual-experience / delivery-quality references follow the declared matrix.
 *
 * Usage:
 *   node check-intent-workflow-boundaries.mjs --skill-dir <solo-design-path>
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_SKILL_DIR = path.resolve(SCRIPT_DIR, '..', '..');

function parseArgs(argv) {
  let skillDir = DEFAULT_SKILL_DIR;
  const errors = [];
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--skill-dir') {
      const value = argv[i + 1];
      if (!value || value.startsWith('--')) errors.push('Missing value for --skill-dir');
      else {
        skillDir = path.resolve(value);
        i += 1;
      }
    } else if (arg.startsWith('--skill-dir=')) {
      skillDir = path.resolve(arg.slice('--skill-dir='.length));
    } else {
      errors.push(`Unknown argument: ${arg}`);
    }
  }
  return { skillDir, errors };
}

function listMarkdown(root, rel = '') {
  const dir = path.join(root, rel);
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const child = rel ? path.join(rel, entry.name) : entry.name;
    if (entry.isDirectory()) out.push(...listMarkdown(root, child));
    else if (entry.isFile() && entry.name.endsWith('.md')) out.push(child.split(path.sep).join('/'));
  }
  return out;
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
  const { skillDir, errors } = parseArgs(process.argv.slice(2));
  if (errors.length) {
    errors.forEach(error => console.error(`[ERROR] ${error}`));
    process.exit(1);
  }

  const workflowsDir = path.join(skillDir, 'intent-workflows');
  const workflowNames = fs.readdirSync(workflowsDir, { withFileTypes: true })
    .filter(entry => entry.isDirectory())
    .map(entry => entry.name)
    .sort();

  const issues = [];
  const isNegativeOrRouteReference = line => /\b(do not|Do not|forbidden|FORBIDDEN|stop and use|route to|re-route|redirect)\b/.test(line);
  const isReadOrLoadReference = line => /\b(Read|read|load|Load|loads|Context Requirements)\b/.test(line);

  const markdownFiles = workflowNames.flatMap(workflow =>
    listMarkdown(path.join(workflowsDir, workflow)).map(file => ({
      workflow,
      rel: `intent-workflows/${workflow}/${file}`,
    }))
  );
  const records = await mapLimit(markdownFiles, 16, async record => ({
    ...record,
    content: await fs.promises.readFile(path.join(skillDir, record.rel), 'utf8'),
  }));

  for (const { workflow, rel, content } of records) {
    const lines = content.split(/\r?\n/);
    for (const other of workflowNames) {
      if (other === workflow) continue;
      for (const [index, line] of lines.entries()) {
        if (!line.includes(`intent-workflows/${other}/`)) continue;
        if (isReadOrLoadReference(line) && !isNegativeOrRouteReference(line)) {
          issues.push(`${rel}:${index + 1} reads or loads ${other}`);
        }
      }
    }
    for (const [index, line] of lines.entries()) {
      if (!line.includes('visual-experience/')) continue;
      if ((workflow === 'intent-page-restore-1to1' || workflow === 'intent-graphic-asset-generation') && !isNegativeOrRouteReference(line)) {
        issues.push(`${rel}:${index + 1} must not declare visual-experience`);
      }
    }
  }

  if (issues.length) {
    issues.forEach(issue => console.error(`[FAIL] ${issue}`));
    process.exit(1);
  }
  console.log(`Intent workflow boundary check passed: ${workflowNames.length} workflows`);
}

main().catch(error => {
  console.error(`[ERROR] ${error?.stack || error?.message || String(error)}`);
  process.exit(1);
});
