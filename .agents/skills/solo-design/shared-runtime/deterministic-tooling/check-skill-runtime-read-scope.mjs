#!/usr/bin/env node

/**
 * Guard agent-readable solo-design skill files against growing near the
 * single-read limit. Scripts are intentionally excluded because they are
 * normally executed rather than read as runbooks.
 *
 * Usage:
 *   node check-skill-runtime-read-scope.mjs [--skill-dir <path>] [--json] [--task-query-file=<path>]
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_SKILL_DIR = path.resolve(SCRIPT_DIR, '..', '..');
const HARD_LIMIT_BYTES = 58 * 1024;
const WARN_LIMIT_BYTES = 48 * 1024;
const KB = 1024;

const INTENT_WORKFLOW_STANDARD = new Set([
  'intent-workflows/intent-page-free-exploration/INTENT_WORKFLOW.md',
  'intent-workflows/intent-page-restore-1to1/INTENT_WORKFLOW.md',
  'intent-workflows/intent-page-library-bound/INTENT_WORKFLOW.md',
  'intent-workflows/intent-graphic-asset-generation/INTENT_WORKFLOW.md',
  'intent-workflows/intent-project-complex-build/INTENT_WORKFLOW.md',
]);

const TEXT_EXTENSIONS = new Set(['.md', '.json', '.yml', '.yaml']);
const IGNORED_NAMES = new Set(['.DS_Store']);
const IGNORED_DIRS = new Set(['shared-runtime/deterministic-tooling']);
const FORBIDDEN_RUNTIME_PATHS = [
  {
    relPath: 'shared-runtime/deterministic-tooling/fixtures',
    reason: 'test fixtures and sample projects must not ship inside the builtin skill package',
  },
];

function parseArgs(argv) {
  let skillDir = DEFAULT_SKILL_DIR;
  let json = false;
  let processResultPath = null;
  let taskQueryFile = null;
  const errors = [];

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--json') {
      json = true;
    } else if (arg === '--skill-dir') {
      const value = argv[i + 1];
      if (!value || value.startsWith('--')) {
        errors.push('Missing value for --skill-dir');
      } else {
        skillDir = path.resolve(value);
        i += 1;
      }
    } else if (arg.startsWith('--skill-dir=')) {
      skillDir = path.resolve(arg.slice('--skill-dir='.length));
    } else if (arg === '--process-result') {
      const value = argv[i + 1];
      if (!value || value.startsWith('--')) {
        errors.push('Missing value for --process-result');
      } else {
        processResultPath = path.resolve(value);
        i += 1;
      }
    } else if (arg.startsWith('--process-result=')) {
      processResultPath = path.resolve(arg.slice('--process-result='.length));
    } else if (arg === '--task-query-file') {
      const value = argv[i + 1];
      if (!value || value.startsWith('--')) {
        errors.push('Missing value for --task-query-file');
      } else {
        taskQueryFile = path.resolve(value);
        i += 1;
      }
    } else if (arg.startsWith('--task-query-file=')) {
      taskQueryFile = path.resolve(arg.slice('--task-query-file='.length));
    } else {
      errors.push(`Unknown argument: ${arg}`);
    }
  }

  return { skillDir, json, processResultPath, taskQueryFile, errors };
}

function toPosix(relPath) {
  return relPath.split(path.sep).join('/');
}

function listFiles(root, rel = '') {
  const abs = path.join(root, rel);
  const entries = fs.readdirSync(abs, { withFileTypes: true });
  const out = [];

  for (const entry of entries) {
    if (IGNORED_NAMES.has(entry.name)) continue;
    const childRel = rel ? path.join(rel, entry.name) : entry.name;
    const childPosix = toPosix(childRel);

    if (entry.isDirectory()) {
      if ([...IGNORED_DIRS].some(dir => childPosix === dir || childPosix.startsWith(`${dir}/`))) continue;
      out.push(...listFiles(root, childRel));
      continue;
    }

    if (!entry.isFile()) continue;
    if (!TEXT_EXTENSIONS.has(path.extname(entry.name))) continue;
    out.push(childPosix);
  }

  return out;
}

function countLines(content) {
  if (content.length === 0) return 0;
  return content.split(/\r?\n/).length;
}

function limitFor(file) {
  if (file === 'SKILL.md') return { bytes: 16 * KB };
  if (INTENT_WORKFLOW_STANDARD.has(file)) return { bytes: 4 * KB, lines: 120 };
  if (file === 'intent-workflows/intent-project-mutation/INTENT_WORKFLOW.md') return { bytes: 6 * KB, lines: 160 };
  if (/^intent-workflows\/.*\/[^/]*-page-runtime\.md$/.test(file)) return { bytes: 8 * KB };
  if (/^intent-workflows\/.*\/[^/]*dispatch-contract[^/]*\.md$/.test(file) || /^intent-workflows\/.*\/dispatch-contract\.md$/.test(file)) return { bytes: 6 * KB };
  if (/^intent-workflows\/.*\/orchestration-summary-fields\.md$/.test(file)) return { bytes: 6 * KB };
  if (file === 'shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md') return { bytes: 12 * KB };
  if (file === 'shared-runtime/orchestration-summary-contract/orchestration-summary-contract.md') return { bytes: 8 * KB };
  if (file === 'intent-workflows/intent-project-complex-build/start-complex-project-build.md') return { bytes: 16 * KB };
  if (file === 'intent-workflows/intent-project-complex-build/00-requirement-and-style-intake.md') return { bytes: 40 * KB };
  if (file === 'intent-workflows/intent-project-complex-build/01-graphic-asset-preparation.md') return { bytes: 32 * KB };
  if (file === 'intent-workflows/intent-project-complex-build/02-page-composition.md') return { bytes: 40 * KB };
  if (file === 'intent-workflows/intent-project-complex-build/03-interaction-validation-delivery.md') return { bytes: 32 * KB };
  return { bytes: HARD_LIMIT_BYTES };
}

function classify(file, content) {
  const size = Buffer.byteLength(content);
  const lines = countLines(content);
  const limit = limitFor(file);
  const hard = size >= limit.bytes || (limit.lines !== undefined && lines > limit.lines);
  const warn = !hard && size > WARN_LIMIT_BYTES;
  return {
    file,
    bytes: size,
    lines,
    hardLimit: limit.bytes,
    lineLimit: limit.lines ?? null,
    warnLimit: WARN_LIMIT_BYTES,
    status: hard ? 'fail' : (warn ? 'warn' : 'ok'),
    suggestion: hard
      ? 'Split this runbook, move details to an existing SSOT, or reduce non-gate explanation. Byte limits are strict (<); line limits allow <=.'
      : null,
  };
}

function findForbiddenRuntimePaths(skillDir) {
  return FORBIDDEN_RUNTIME_PATHS
    .filter(rule => fs.existsSync(path.join(skillDir, rule.relPath)))
    .map(rule => ({ ...rule, status: 'fail' }));
}

const PROCESS_RESULT_THRESHOLDS = {
  repeated_context_read_count: { warn: 5, blocking: 10 },
  validation_attempt_count: { warn: 4, blocking: 8 },
  unnecessary_llm_call_count: { warn: 10, blocking: 20 },
  wasted_tokens: { warn: 2_000_000, blocking: 5_000_000 },
};

function analyzeProcessResult(processResultPath) {
  const data = JSON.parse(fs.readFileSync(processResultPath, 'utf8'));
  const metrics = data.metrics || data;
  const diagnostics = [];

  for (const [metric, thresholds] of Object.entries(PROCESS_RESULT_THRESHOLDS)) {
    const value = metrics[metric];
    if (value === undefined || value === null) continue;
    if (value >= thresholds.blocking) {
      diagnostics.push({ metric, value, threshold: thresholds.blocking, level: 'blocking' });
    } else if (value >= thresholds.warn) {
      diagnostics.push({ metric, value, threshold: thresholds.warn, level: 'warning' });
    }
  }

  const topWastePatterns = Array.isArray(metrics.top_waste_patterns) ? metrics.top_waste_patterns : [];
  const overallLevel = diagnostics.some(d => d.level === 'blocking') ? 'blocking'
    : diagnostics.some(d => d.level === 'warning') ? 'warning' : 'ok';

  return { diagnostics, topWastePatterns, overallLevel, rawMetrics: metrics };
}

function analyzeTaskQueryFile(taskQueryFile) {
  const content = fs.readFileSync(taskQueryFile, 'utf8');
  const diagnostics = [];
  if (/runtime-orchestration-summary\.json/i.test(content)) {
    diagnostics.push({
      level: 'blocking',
      rule: 'full-summary-in-task-query',
      message: 'Restore page tasks must use restoreCompactPacket, not full runtime-orchestration-summary.json',
    });
  }
  if (/visual-experience\/visual-experience-guidelines\.md/i.test(content) && /restoreCompactPacket/i.test(content)) {
    diagnostics.push({
      level: 'blocking',
      rule: 'restore-generic-visual-guidance',
      message: 'Restore page tasks must not load generic visual-experience guidance as source authority',
    });
  }
  const overallLevel = diagnostics.some(d => d.level === 'blocking') ? 'blocking'
    : diagnostics.some(d => d.level === 'warning') ? 'warning' : 'ok';
  return { diagnostics, overallLevel, bytes: Buffer.byteLength(content), taskQueryFile };
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
  const { skillDir, json, processResultPath, taskQueryFile, errors } = parseArgs(process.argv.slice(2));
  if (errors.length > 0) {
    for (const error of errors) console.error(`[ERROR] ${error}`);
    process.exit(1);
  }

  if (taskQueryFile) {
    if (!fs.existsSync(taskQueryFile)) {
      console.error(`[ERROR] task query file not found: ${taskQueryFile}`);
      process.exit(1);
    }
    const analysis = analyzeTaskQueryFile(taskQueryFile);
    if (json) {
      process.stdout.write(`${JSON.stringify({ success: analysis.overallLevel !== 'blocking', ...analysis }, null, 2)}\n`);
    } else {
      console.log(`Task query analysis: ${taskQueryFile}`);
      console.log(`Overall: ${analysis.overallLevel}`);
      for (const d of analysis.diagnostics) {
        const marker = d.level === 'blocking' ? '[BLOCKING]' : '[WARN]';
        console.log(`${marker} ${d.rule}: ${d.message}`);
      }
    }
    process.exit(analysis.overallLevel === 'blocking' ? 1 : 0);
  }

  // Process result analysis mode
  if (processResultPath) {
    if (!fs.existsSync(processResultPath)) {
      console.error(`[ERROR] process result file not found: ${processResultPath}`);
      process.exit(1);
    }
    const analysis = analyzeProcessResult(processResultPath);
    if (json) {
      process.stdout.write(`${JSON.stringify({ success: analysis.overallLevel !== 'blocking', ...analysis }, null, 2)}\n`);
    } else {
      console.log(`Process result analysis: ${processResultPath}`);
      console.log(`Overall: ${analysis.overallLevel}`);
      for (const d of analysis.diagnostics) {
        const marker = d.level === 'blocking' ? '[BLOCKING]' : '[WARN]';
        console.log(`${marker} ${d.metric}: ${d.value} (threshold: ${d.threshold})`);
      }
      if (analysis.topWastePatterns.length > 0) {
        console.log('\nTop waste patterns:');
        for (const p of analysis.topWastePatterns.slice(0, 5)) {
          console.log(`  - ${typeof p === 'string' ? p : JSON.stringify(p)}`);
        }
      }
    }
    process.exit(analysis.overallLevel === 'blocking' ? 1 : 0);
  }

  // File size check mode (original behavior)
  if (!fs.existsSync(skillDir) || !fs.statSync(skillDir).isDirectory()) {
    console.error(`[ERROR] skill directory not found: ${skillDir}`);
    process.exit(1);
  }

  const files = listFiles(skillDir);
  const records = (await mapLimit(files, 16, async file => {
    const content = await fs.promises.readFile(path.join(skillDir, file), 'utf8');
    return classify(file, content);
  })).sort((a, b) => b.bytes - a.bytes || a.file.localeCompare(b.file));

  const forbiddenRuntimePaths = findForbiddenRuntimePaths(skillDir);
  const failures = records.filter(record => record.status === 'fail');
  const warnings = records.filter(record => record.status === 'warn');
  const result = {
    success: failures.length === 0 && forbiddenRuntimePaths.length === 0,
    skillDir,
    hardLimitBytes: HARD_LIMIT_BYTES,
    warnLimitBytes: WARN_LIMIT_BYTES,
    checkedFiles: records.length,
    failureCount: failures.length,
    warningCount: warnings.length,
    forbiddenRuntimePathCount: forbiddenRuntimePaths.length,
    forbiddenRuntimePaths,
    failures,
    warnings,
    largestFiles: records.slice(0, 20),
  };

  if (json) {
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  } else {
    console.log(`Skill file size check: ${skillDir}`);
    console.log(`Checked ${records.length} file(s). hard=${HARD_LIMIT_BYTES} warn=${WARN_LIMIT_BYTES}`);
    for (const record of records.slice(0, 20)) {
      const marker = record.status === 'fail' ? '[FAIL]' : (record.status === 'warn' ? '[WARN]' : '[OK]');
      const lineText = record.lineLimit === null ? '' : ` ${record.lines}/${record.lineLimit} lines`;
      console.log(`${marker} ${String(record.bytes).padStart(7)} bytes${lineText}  ${record.file}`);
    }
    if (warnings.length > 0) {
      console.log(`\nWarnings: ${warnings.length} file(s) exceed ${WARN_LIMIT_BYTES} bytes but remain below hard limits.`);
    }
    if (forbiddenRuntimePaths.length > 0) {
      console.error(`\nForbidden runtime paths: ${forbiddenRuntimePaths.length}`);
      for (const item of forbiddenRuntimePaths) {
        console.error(`[FAIL] ${item.relPath}: ${item.reason}.`);
      }
    }
    if (failures.length > 0) {
      console.error(`\nFailures: ${failures.length} file(s) exceed their hard limit.`);
      for (const failure of failures) {
        const byteIssue = failure.bytes >= failure.hardLimit ? `${failure.bytes} >= ${failure.hardLimit}` : null;
        const lineIssue = failure.lineLimit !== null && failure.lines > failure.lineLimit ? `${failure.lines} > ${failure.lineLimit} lines` : null;
        console.error(`[FAIL] ${failure.file}: ${[byteIssue, lineIssue].filter(Boolean).join(', ')}. ${failure.suggestion}`);
      }
    }
  }

  process.exit(result.success ? 0 : 1);
}

main().catch(error => {
  console.error(`[ERROR] ${error.message}`);
  process.exit(1);
});
