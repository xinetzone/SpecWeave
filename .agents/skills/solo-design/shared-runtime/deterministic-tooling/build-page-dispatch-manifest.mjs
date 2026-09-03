#!/usr/bin/env node

/**
 * Build dispatchPreflightManifest from runtime-orchestration-summary.json.
 *
 * This script is intentionally deterministic:
 * - It writes only runtime-orchestration-summary.json.
 * - It never edits HTML, .design, CSS, assets, or page content.
 * - It refuses to write a partial manifest when required fields are missing.
 *
 * Usage:
 *   node build-page-dispatch-manifest.mjs <design-project-path> --mode=free-fast|restore|library-bound|graphic-layout-static|complex|existing-edit|redesign|variants [--task-query-file=<path>]
 */

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = path.resolve(SCRIPT_DIR, '..', '..');
const DISPATCH_MANIFEST_FILE = 'runtime-dispatch-manifest.json';
const DETERMINISTIC_TOOL_NAMES = {
  applyHtmlHeadContract: 'apply-html-head-contract.mjs',
  recordDispatchCompletion: 'record-dispatch-completion.mjs',
  buildPageDispatchManifest: 'build-page-dispatch-manifest.mjs',
  validateDesignWorkspace: 'validate-design-workspace.mjs',
  validateFinishReadiness: 'validate-finish-readiness.mjs',
  validateRestoreContract: 'validate-restore-contract.mjs',
};

const PAGE_DISPATCH_MODES = new Set([
  'free-fast',
  'restore',
  'library-bound',
  'graphic-layout-static',
  'complex',
  'existing-edit',
  'redesign',
  'variants',
]);

function parseArgs(argv) {
  const positional = [];
  const errors = [];
  let mode = null;
  let taskQueryFile = null;
  let initOrNormalize = false;
  let json = false;

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg.startsWith('--mode=')) {
      mode = arg.slice('--mode='.length);
    } else if (arg === '--task-query-file') {
      const value = argv[i + 1];
      if (!value || value.startsWith('--')) errors.push('Missing value for --task-query-file');
      else {
        taskQueryFile = value;
        i += 1;
      }
    } else if (arg.startsWith('--task-query-file=')) {
      taskQueryFile = arg.slice('--task-query-file='.length);
    } else if (arg === '--init-or-normalize-summary') {
      initOrNormalize = true;
    } else if (arg === '--json') {
      json = true;
    } else if (arg.startsWith('--')) {
      errors.push(`Unknown flag: ${arg}`);
    } else {
      positional.push(arg);
    }
  }

  if (!mode) errors.push('Missing required --mode');
  if (mode && !PAGE_DISPATCH_MODES.has(mode)) {
    errors.push(`Unsupported mode: ${mode}`);
  }

  return { designDir: positional[0] || null, mode, taskQueryFile, initOrNormalize, json, errors };
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
}

function writeRuntimeDispatchManifest(designDir, summaryPath, summary, entries, mode) {
  const manifestPath = path.join(designDir, DISPATCH_MANIFEST_FILE);
  const deterministicCommandsByPage = {};
  for (const entry of entries) {
    const key = entry.htmlSrc || entry.nodeId || entry.pageId || `entry-${Object.keys(deterministicCommandsByPage).length}`;
    deterministicCommandsByPage[key] = entry.deterministicCommands || {};
  }
  writeJson(manifestPath, {
    schema_version: '1.0',
    generated_at: new Date().toISOString(),
    source: 'build-page-dispatch-manifest.mjs',
    mode,
    summary_path: path.relative(designDir, summaryPath).replace(/\\/g, '/'),
    skillProvenance: summary.skillProvenance || null,
    dispatchPreflightManifest: entries,
    deterministicCommandsByPage,
  });
  return manifestPath;
}

function sha256(value) {
  return crypto.createHash('sha256').update(String(value)).digest('hex');
}

function sha256File(filePath) {
  const hash = crypto.createHash('sha256');
  const fd = fs.openSync(filePath, 'r');
  const buffer = Buffer.allocUnsafe(1024 * 1024);
  try {
    let bytesRead = 0;
    do {
      bytesRead = fs.readSync(fd, buffer, 0, buffer.length, null);
      if (bytesRead > 0) hash.update(buffer.subarray(0, bytesRead));
    } while (bytesRead > 0);
  } finally {
    fs.closeSync(fd);
  }
  return hash.digest('hex');
}

async function sha256FileAsync(filePath) {
  const hash = crypto.createHash('sha256');
  const handle = await fs.promises.open(filePath, 'r');
  const buffer = Buffer.allocUnsafe(1024 * 1024);
  try {
    let bytesRead = 0;
    do {
      ({ bytesRead } = await handle.read(buffer, 0, buffer.length, null));
      if (bytesRead > 0) hash.update(buffer.subarray(0, bytesRead));
    } while (bytesRead > 0);
  } finally {
    await handle.close();
  }
  return hash.digest('hex');
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

function pathIsInside(baseDir, candidatePath) {
  const root = path.resolve(baseDir);
  const candidate = path.resolve(candidatePath);
  const rel = path.relative(root, candidate);
  return rel === '' || (rel && !rel.startsWith('..') && !path.isAbsolute(rel));
}

function normalizeProjectRelativePath(rawValue, designDir, options = {}) {
  const {
    label = 'path',
    allowDirectory = false,
    requireExtension = null,
  } = options;
  const raw = String(rawValue || '').trim().replace(/\\/g, '/');
  if (!raw) return { value: null, error: `${label} is empty` };
  if (path.isAbsolute(raw)) return { value: null, error: `${label} must be project-relative: ${raw}` };

  const withoutLeadingDot = raw.replace(/^\.\/+/, '');
  const rawSegments = withoutLeadingDot.split('/').filter(Boolean);
  if (rawSegments.includes('..')) return { value: null, error: `${label} must not contain "..": ${raw}` };

  let normalized = path.posix.normalize(withoutLeadingDot);
  if (!normalized || normalized === '.') return { value: null, error: `${label} is empty` };
  if (normalized.startsWith('../') || normalized === '..') {
    return { value: null, error: `${label} escapes the design project: ${raw}` };
  }

  const isDirectory = raw.endsWith('/');
  if (isDirectory && !allowDirectory) return { value: null, error: `${label} must be a file path: ${raw}` };
  if (isDirectory && !normalized.endsWith('/')) normalized = `${normalized}/`;

  if (requireExtension && path.posix.extname(normalized).toLowerCase() !== requireExtension) {
    return { value: null, error: `${label} must end with ${requireExtension}: ${raw}` };
  }

  const resolved = path.resolve(designDir, normalized);
  if (!pathIsInside(designDir, resolved) || resolved === path.resolve(designDir)) {
    return { value: null, error: `${label} escapes the design project: ${raw}` };
  }
  return { value: normalized, error: null };
}

function shellQuote(value) {
  if (process.platform === 'win32') {
    return `"${String(value).replace(/"/g, '\\"')}"`;
  }
  return `'${String(value).replace(/'/g, "'\\''")}'`;
}

function deterministicToolPath(fileName) {
  return path.join(SKILL_DIR, 'shared-runtime', 'deterministic-tooling', fileName);
}

function deterministicToolPaths() {
  return Object.fromEntries(
    Object.entries(DETERMINISTIC_TOOL_NAMES).map(([key, fileName]) => [
      key,
      deterministicToolPath(fileName),
    ])
  );
}

function buildRecordDispatchCompletionCommand(designDir, pageIdentity = {}) {
  const nodeId = pageIdentity.nodeId || '<page-id>';
  const htmlSrcArg = pageIdentity.htmlSrc
    ? ` --html-src=${shellQuote(pageIdentity.htmlSrc)}`
    : '';
  return [
    'node',
    shellQuote(deterministicToolPath('record-dispatch-completion.mjs')),
    shellQuote(designDir),
    `--node-id=${shellQuote(nodeId)}`,
    htmlSrcArg.trim(),
    '--status=completed',
    '--changed-files=<comma-separated-project-relative-files>',
    '--trace-digest=<main-agent-runtime-trace-digest>',
    '--tool-ledger-json=<tool-ledger-json-or-file>',
  ].filter(Boolean).join(' ');
}

function buildSkillRuntimePacket(designDir, pageIdentity = {}) {
  const toolPaths = deterministicToolPaths();
  return {
    skillDir: SKILL_DIR,
    deterministicToolDir: SCRIPT_DIR,
    toolPaths,
    requiredForPageSubAgent: [
      'applyHtmlHeadContract',
      'recordDispatchCompletion',
    ],
    pathInjection: 'absolute',
    pathContract: 'Do not use {SKILL_DIR} placeholders inside Page Sub-Agent packets; use toolPaths.* absolute paths.',
    commandTemplates: {
      recordDispatchCompletion: buildRecordDispatchCompletionCommand(designDir, pageIdentity),
    },
  };
}

function buildDeterministicCommands(designDir, options = {}) {
  const mode = options.mode || 'restore';
  const requiresFinalResponseDraft = options.requiresFinalResponseDraft === true;
  const finalResponseArg = ` --final-response-file=${shellQuote('<final-response-draft.md>')}`;
  const finishReadinessAll = `node ${shellQuote(deterministicToolPath('validate-finish-readiness.mjs'))} ${shellQuote(designDir)} --check=all${requiresFinalResponseDraft ? finalResponseArg : ''}`;
  return {
    restorePreflight: `node ${shellQuote(deterministicToolPath('validate-restore-contract.mjs'))} ${shellQuote(designDir)} --mode=preflight`,
    restorePreflightApplySafeFixes: `node ${shellQuote(deterministicToolPath('validate-restore-contract.mjs'))} ${shellQuote(designDir)} --mode=preflight --apply-safe-fixes`,
    buildManifest: `node ${shellQuote(deterministicToolPath('build-page-dispatch-manifest.mjs'))} ${shellQuote(designDir)} --mode=${mode}`,
    workspaceValidation: `node ${shellQuote(deterministicToolPath('validate-design-workspace.mjs'))} ${shellQuote(designDir)} --report-json=${shellQuote(path.join(designDir, 'validation-report.json'))}`,
    finishReadinessAll,
    finishReadinessAllWithResponse: `node ${shellQuote(deterministicToolPath('validate-finish-readiness.mjs'))} ${shellQuote(designDir)} --check=all${finalResponseArg}`,
    finishReadinessRepairLedger: `node ${shellQuote(deterministicToolPath('validate-finish-readiness.mjs'))} ${shellQuote(designDir)} --check=repair-ledger`,
    finishReadinessArtifact: `node ${shellQuote(deterministicToolPath('validate-finish-readiness.mjs'))} ${shellQuote(designDir)} --check=artifact`,
    finishReadinessResponse: `node ${shellQuote(deterministicToolPath('validate-finish-readiness.mjs'))} ${shellQuote(designDir)} --check=response --final-response-file=${shellQuote('<final-response-draft.md>')}`,
  };
}

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function truncate(value, maxLength) {
  const text = String(value || '').trim();
  if (text.length <= maxLength) return text;
  return `${text.slice(0, Math.max(0, maxLength - 1))}…`;
}

async function collectPreDispatchFileHashes(designDir) {
  const designFiles = (await fs.promises.readdir(designDir, { withFileTypes: true }))
    .filter(entry => entry.isFile() && entry.name.endsWith('.design'))
    .map(entry => entry.name);
  const entries = await mapLimit(designFiles, 8, async fileName => [
    fileName,
    await sha256FileAsync(path.join(designDir, fileName)),
  ]);
  return Object.fromEntries(entries);
}

function loadRestoreContractReport(designDir, errors) {
  const reportPath = path.join(designDir, 'restore-contract-report.json');
  if (!fs.existsSync(reportPath)) {
    errors.push('[restore-preflight] restore-contract-report.json is required; run validate-restore-contract.mjs before build-page-dispatch-manifest.mjs --mode=restore');
    return null;
  }
  let report;
  try {
    report = readJson(reportPath);
  } catch (error) {
    errors.push(`[restore-preflight] restore-contract-report.json is unreadable: ${error.message}`);
    return null;
  }
  if (report.success !== true) {
    errors.push('[restore-preflight] restore-contract-report.json success must be true before dispatch');
  }
  return {
    reportPath: 'restore-contract-report.json',
    reportHash: sha256File(reportPath),
    success: report.success === true,
    checkedAt: report.checkedAt || null,
    evidence: report.evidence || null,
    errorCount: Array.isArray(report.errors) ? report.errors.length : null,
    warningCount: Array.isArray(report.warnings) ? report.warnings.length : null,
  };
}

function restoreCoverageRows(project) {
  if (Array.isArray(project?.sourceRegionCoverage)) return project.sourceRegionCoverage;
  if (Array.isArray(project?.restorationContractLite?.sourceRegionCoverage)) {
    return project.restorationContractLite.sourceRegionCoverage;
  }
  return [];
}

function compactFact(fact) {
  return {
    id: fact?.id || null,
    cat: fact?.category || null,
    reg: fact?.sourceRegion || null,
    p: fact?.priority || null,
    fact: truncate(fact?.fact, 90),
    basis: truncate(fact?.measurementBasis, 70),
    vc: Array.isArray(fact?.usedByCheckpointIds) ? fact.usedByCheckpointIds : [],
  };
}

function compactCheckpoint(checkpoint) {
  return {
    id: checkpoint?.id || null,
    p: checkpoint?.priority || null,
    dim: checkpoint?.dimension || checkpoint?.category || null,
    reg: checkpoint?.region || checkpoint?.sourceRegion || null,
    src: truncate(checkpoint?.sourceFact || checkpoint?.sourceObservation, 80),
    exp: truncate(checkpoint?.expected || checkpoint?.targetImplementation, 80),
    dev: checkpoint?.allowedDeviationRef || null,
  };
}

function compactCoverage(row) {
  return {
    id: row?.id || null,
    reg: row?.sourceRegion || row?.region || null,
    group: row?.regionGroup || null,
    p: row?.priority || null,
    status: row?.mappedStatus || row?.status || null,
  };
}

function buildRestoreCompactPacket(project, page) {
  const facts = Array.isArray(project?.measuredSourceFacts)
    ? project.measuredSourceFacts
    : (Array.isArray(project?.restorationContractLite?.measuredSourceFacts)
      ? project.restorationContractLite.measuredSourceFacts
      : []);
  const checkpoints = Array.isArray(project?.restoreVisualCheckpoints) ? project.restoreVisualCheckpoints : [];
  const coverage = restoreCoverageRows(project);
  const packet = {
    schema: 'restoreCompactPacket.v1',
    sourceType: project?.sourceType || project?.intentProfile?.sourceType || project?.referenceCaptureEvidence?.sourceType || null,
    sourceIdentity: project?.sourceIdentity
      ? {
        businessType: project.sourceIdentity.businessType || null,
        coreObjects: Array.isArray(project.sourceIdentity.coreObjects) ? project.sourceIdentity.coreObjects.slice(0, 8) : [],
        deviceType: project.sourceIdentity.deviceType || null,
        pageTitle: truncate(project.sourceIdentity.pageTitle, 80),
      }
      : null,
    pageStateLock: project?.pageStateLock
      ? {
        currentState: truncate(project.pageStateLock.currentState, 120),
        forbiddenDeviations: Array.isArray(project.pageStateLock.forbiddenDeviations)
          ? project.pageStateLock.forbiddenDeviations.slice(0, 5).map(item => truncate(item, 80))
          : [],
      }
      : null,
    sourceDocumentProfile: project?.sourceDocumentProfile
      ? {
        sourceType: project.sourceDocumentProfile.sourceType || null,
        documentLengthClass: project.sourceDocumentProfile.documentLengthClass || null,
        viewportScrollRatio: project.sourceDocumentProfile.viewportScrollRatio ?? null,
        deviceFramePresent: project.sourceDocumentProfile.deviceFramePresent ?? null,
        requiredRegionGroups: Array.isArray(project.sourceDocumentProfile.requiredRegionGroups)
          ? project.sourceDocumentProfile.requiredRegionGroups
          : [],
      }
      : null,
    measuredSourceFacts: facts.map(compactFact),
    restoreVisualCheckpoints: checkpoints.map(compactCheckpoint),
    sourceRegionCoverage: coverage.map(compactCoverage),
    contentToPreserve: Array.isArray(page?.contentToPreserve) ? page.contentToPreserve.slice(0, 20) : [],
  };
  const byteLength = Buffer.byteLength(JSON.stringify(packet), 'utf8');
  return {
    ...packet,
    byteLength,
  };
}

const IMAGE_EVIDENCE_FIELDS = ['providedImagePath', 'providedImageEvidence', 'providedScreenshotEvidence', 'imageEvidence', 'screenshotEvidence'];
const URL_EVIDENCE_FIELDS = ['urlEvidence', 'fullPageScreenshotEvidence', 'browserCaptureEvidence', 'liveUrl'];
const RESTORE_REQUIRED_CATEGORIES = new Set(['viewport', 'layout-region', 'color-surface', 'component-proportion', 'density-spacing']);
const GENERALIZED_FLOW_CONTROL_VERSION = '2026.07.11.0';

function hasEvidence(captureEvidence, fields) {
  if (!captureEvidence || typeof captureEvidence !== 'object') return false;
  return fields.some(field => {
    const value = captureEvidence[field];
    if (Array.isArray(value)) return value.length > 0;
    if (value && typeof value === 'object') return Object.keys(value).length > 0;
    return value !== undefined && value !== null && value !== '';
  });
}

function validateRestoreDispatchReadiness(project) {
  const errors = [];
  const sourceType = String(
    project?.sourceType ||
    project?.intentProfile?.sourceType ||
    project?.referenceCaptureEvidence?.sourceType ||
    ''
  ).trim();
  const facts = Array.isArray(project?.measuredSourceFacts)
    ? project.measuredSourceFacts
    : (Array.isArray(project?.restorationContractLite?.measuredSourceFacts)
      ? project.restorationContractLite.measuredSourceFacts
      : []);
  const checkpoints = Array.isArray(project?.restoreVisualCheckpoints) ? project.restoreVisualCheckpoints : [];
  const captureEvidence = project?.referenceCaptureEvidence;
  const sourceAuthorityLock = project?.sourceAuthorityLock && typeof project.sourceAuthorityLock === 'object'
    ? project.sourceAuthorityLock
    : null;

  if (!['image', 'url', 'image+url'].includes(sourceType)) {
    errors.push(`invalid restore sourceType: ${sourceType || '(missing)'}`);
  }
  if (!captureEvidence || typeof captureEvidence !== 'object') {
    errors.push('missing referenceCaptureEvidence');
  }
  if (!sourceAuthorityLock && !(captureEvidence && captureEvidence.sourceAuthority)) {
    errors.push('missing sourceAuthorityLock or referenceCaptureEvidence.sourceAuthority');
  }
  if (sourceAuthorityLock) {
    if (!asString(sourceAuthorityLock.visualAuthority)) errors.push('sourceAuthorityLock.visualAuthority is required');
    if (sourceAuthorityLock.mayOverrideVisualAuthority !== false) {
      errors.push('sourceAuthorityLock.mayOverrideVisualAuthority must be false');
    }
    if (sourceAuthorityLock.lockedBeforeDispatch !== true) {
      errors.push('sourceAuthorityLock.lockedBeforeDispatch must be true');
    }
  }
  if (facts.length < 8) {
    errors.push(`measuredSourceFacts has ${facts.length} rows, requires >= 8`);
  }
  const highPriorityFacts = facts.filter(f => f?.priority === 'high');
  if (highPriorityFacts.length < 5) {
    errors.push(`measuredSourceFacts requires >= 5 high priority rows, found ${highPriorityFacts.length}`);
  }
  if (checkpoints.length < 8) {
    errors.push(`restoreVisualCheckpoints has ${checkpoints.length} rows, requires >= 8`);
  }
  const highPriorityCheckpoints = checkpoints.filter(c => c?.priority === 'high');
  if (highPriorityCheckpoints.length < 5) {
    errors.push(`restoreVisualCheckpoints requires >= 5 high priority rows, found ${highPriorityCheckpoints.length}`);
  }
  const categories = new Set(facts.map(f => String(f?.category || '').trim()).filter(Boolean));
  const missingCategories = [...RESTORE_REQUIRED_CATEGORIES].filter(c => !categories.has(c));
  if (missingCategories.length > 0) {
    errors.push(`measuredSourceFacts missing categories: ${missingCategories.join(', ')}`);
  }

  if (captureEvidence && sourceType === 'image+url') {
    if (!hasEvidence(captureEvidence, IMAGE_EVIDENCE_FIELDS)) {
      errors.push('image+url requires provided image evidence');
    }
    if (!hasEvidence(captureEvidence, URL_EVIDENCE_FIELDS)) {
      errors.push('image+url requires URL evidence');
    }
  } else if (captureEvidence && sourceType === 'url') {
    if (!hasEvidence(captureEvidence, ['fullPageScreenshotEvidence'])) {
      errors.push('url restore requires fullPageScreenshotEvidence');
    }
    if (hasEvidence(captureEvidence, IMAGE_EVIDENCE_FIELDS)) {
      errors.push('url sourceType must not contain image evidence; use image+url instead');
    }
  } else if (captureEvidence && sourceType === 'image') {
    if (hasEvidence(captureEvidence, URL_EVIDENCE_FIELDS)) {
      errors.push('image sourceType must not contain URL evidence; use image+url instead');
    }
  }

  return errors;
}

function asString(value) {
  return typeof value === 'string' && value.trim() ? value.trim() : null;
}

function compareVersion(a, b) {
  const left = String(a || '').split('.').map(part => Number.parseInt(part, 10) || 0);
  const right = String(b || '').split('.').map(part => Number.parseInt(part, 10) || 0);
  const length = Math.max(left.length, right.length);
  for (let i = 0; i < length; i += 1) {
    const diff = (left[i] || 0) - (right[i] || 0);
    if (diff !== 0) return diff;
  }
  return 0;
}

const QUALITY_EFFICIENCY_GATE_VERSION = '2026.07.10.0';

function isLaneIsolationContractActive(summary) {
  const version = summary?.skillProvenance?.version;
  return Boolean(version) && compareVersion(version, '2026.07.08.0') >= 0;
}

function isQualityEfficiencyContractActive(summary) {
  const version = summary?.skillProvenance?.version;
  return Boolean(version) && compareVersion(version, QUALITY_EFFICIENCY_GATE_VERSION) >= 0;
}

function isGeneralizedFlowControlActive(summary) {
  const version = summary?.skillProvenance?.version;
  return Boolean(version) && compareVersion(version, GENERALIZED_FLOW_CONTROL_VERSION) >= 0;
}

function relativeOrAbsolute(baseDir, value, fallbackRel) {
  const raw = asString(value) || fallbackRel;
  if (!raw) return null;
  return path.isAbsolute(raw) ? raw : path.join(baseDir, raw);
}

function laneForMode(summary, mode) {
  const project = summary.project || {};
  const intent = project.intentProfile || {};
  if (mode === 'restore' || intent.caseFamily === 'restore_1to1' || project.replicationMode === 'high-fidelity') return 'restore_1to1';
  if (mode === 'library-bound' || project.operatingMode === 'library-bound' || summary.designSource?.libraryIdentity) return 'library_bound';
  if (mode === 'graphic-layout-static' || project.graphicStrategyGate === 'layout-static') return 'graphic_layout_static';
  if (mode === 'existing-edit') return 'existing_edit_add_comparison';
  if (mode === 'redesign') return 'redesign_duplicate_project';
  if (mode === 'variants') return 'variants_multi_scheme';
  if (mode === 'complex') return 'complex_html_page';
  return 'free_exploration';
}

function packetTypeFor(lane) {
  return {
    free_exploration: 'FreePagePacket',
    restore_1to1: 'RestorePagePacket',
    library_bound: 'LibraryBoundPagePacket',
    graphic_layout_static: 'GraphicLayoutPagePacket',
    complex_html_page: 'ComplexPagePacket',
    existing_edit_add_comparison: 'ExistingEditPagePacket',
    redesign_duplicate_project: 'RedesignPagePacket',
    variants_multi_scheme: 'VariantPagePacket',
  }[lane] || 'FreePagePacket';
}

function runtimeGuideFor(lane) {
  return {
    free_exploration: 'intent-workflows/intent-page-free-exploration/free-exploration-page-runtime.md',
    restore_1to1: 'intent-workflows/intent-page-restore-1to1/restore-1to1-page-runtime.md',
    library_bound: 'intent-workflows/intent-page-library-bound/library-bound-page-runtime.md',
    graphic_layout_static: 'intent-workflows/intent-project-complex-build/graphic-layout-page-runtime.md',
    complex_html_page: 'intent-workflows/intent-project-complex-build/complex-page-runtime.md',
    existing_edit_add_comparison: 'intent-workflows/intent-project-mutation/existing-edit-page-runtime.md',
    redesign_duplicate_project: 'intent-workflows/intent-project-mutation/redesign-page-runtime.md',
    variants_multi_scheme: 'intent-workflows/intent-project-mutation/variant-page-runtime.md',
  }[lane];
}

function dispatchContractFor(lane) {
  return {
    free_exploration: 'intent-workflows/intent-page-free-exploration/dispatch-contract.md',
    restore_1to1: 'intent-workflows/intent-page-restore-1to1/dispatch-contract.md',
    library_bound: 'intent-workflows/intent-page-library-bound/dispatch-contract.md',
    graphic_layout_static: 'intent-workflows/intent-project-complex-build/graphic-layout-dispatch-contract.md',
    complex_html_page: 'intent-workflows/intent-project-complex-build/complex-page-dispatch-contract.md',
    existing_edit_add_comparison: 'intent-workflows/intent-project-mutation/existing-edit-dispatch-contract.md',
    redesign_duplicate_project: 'intent-workflows/intent-project-mutation/redesign-dispatch-contract.md',
    variants_multi_scheme: 'intent-workflows/intent-project-mutation/variant-dispatch-contract.md',
  }[lane];
}

function laneRootFor(lane) {
  return {
    free_exploration: 'intent-workflows/intent-page-free-exploration/',
    restore_1to1: 'intent-workflows/intent-page-restore-1to1/',
    library_bound: 'intent-workflows/intent-page-library-bound/',
    graphic_layout_static: 'intent-workflows/intent-project-complex-build/',
    complex_html_page: 'intent-workflows/intent-project-complex-build/',
    existing_edit_add_comparison: 'intent-workflows/intent-project-mutation/',
    redesign_duplicate_project: 'intent-workflows/intent-project-mutation/',
    variants_multi_scheme: 'intent-workflows/intent-project-mutation/',
  }[lane] || 'intent-workflows/intent-page-free-exploration/';
}

function workflowFileFor(lane) {
  return {
    free_exploration: 'intent-workflows/intent-page-free-exploration/INTENT_WORKFLOW.md',
    restore_1to1: 'intent-workflows/intent-page-restore-1to1/INTENT_WORKFLOW.md',
    library_bound: 'intent-workflows/intent-page-library-bound/INTENT_WORKFLOW.md',
    graphic_layout_static: 'intent-workflows/intent-project-complex-build/INTENT_WORKFLOW.md',
    complex_html_page: 'intent-workflows/intent-project-complex-build/INTENT_WORKFLOW.md',
    existing_edit_add_comparison: 'intent-workflows/intent-project-mutation/INTENT_WORKFLOW.md',
    redesign_duplicate_project: 'intent-workflows/intent-project-mutation/INTENT_WORKFLOW.md',
    variants_multi_scheme: 'intent-workflows/intent-project-mutation/INTENT_WORKFLOW.md',
  }[lane] || 'intent-workflows/intent-page-free-exploration/INTENT_WORKFLOW.md';
}

function parseContextRequirementsFromWorkflow(lane) {
  const relPath = workflowFileFor(lane);
  const filePath = path.join(path.resolve(SCRIPT_DIR, '..', '..'), relPath);
  if (!fs.existsSync(filePath)) {
    return { workflowPath: relPath, required: [], optional: [], errors: [`workflow file not found: ${relPath}`] };
  }
  const content = fs.readFileSync(filePath, 'utf8');
  const section = content.match(/## Context Requirements\s*\n([\s\S]*?)(?:\n## |\n# |$)/);
  if (!section) {
    return { workflowPath: relPath, required: [], optional: [], errors: [`Context Requirements section not found in ${relPath}`] };
  }
  const required = [];
  const optional = [];
  for (const line of section[1].split('\n')) {
    const match = line.match(/-\s+`([^`]+)`(.*)$/);
    if (!match) continue;
    const rel = normalizeRelPath(match[1]);
    if (!rel) continue;
    const qualifier = match[2] || '';
    const entry = {
      path: rel,
      qualifier: qualifier.trim(),
      workflowPath: relPath,
    };
    if (/\b(conditionally|fallback|optional)\b/i.test(qualifier)) optional.push(entry);
    else required.push(entry);
  }
  return { workflowPath: relPath, required, optional, errors: [] };
}

function normalizeRelPath(value) {
  const raw = asString(value);
  if (!raw) return null;
  return raw.replace(/\\/g, '/').replace(/^\.\//, '');
}

function isAllowedReadPath(relPath, lane) {
  const normalized = normalizeRelPath(relPath);
  if (!normalized) return false;
  if (normalized.startsWith('shared-runtime/')) return true;
  if (normalized.startsWith('delivery-quality/')) return true;
  if (normalized.startsWith('visual-experience/')) return true;
  if (normalized.startsWith(laneRootFor(lane))) return true;
  return false;
}

function validateSupplementaryReads(reads, lane, pageLabel) {
  const errors = [];
  if (!Array.isArray(reads)) return errors;
  for (const [index, read] of reads.entries()) {
    const relPath = normalizeRelPath(read?.path);
    if (!relPath) {
      errors.push(`${pageLabel}: supplementaryReads[${index}].path is required`);
      continue;
    }
    if (!asString(read?.reason)) errors.push(`${pageLabel}: supplementaryReads[${index}].reason is required`);
    if (!asString(read?.ownerLane)) errors.push(`${pageLabel}: supplementaryReads[${index}].ownerLane is required`);
    if (relPath.startsWith('intent-workflows/') && !relPath.startsWith(laneRootFor(lane))) {
      errors.push(`${pageLabel}: supplementaryReads[${index}] crosses lane boundary: ${relPath}`);
    } else if (!isAllowedReadPath(relPath, lane)) {
      errors.push(`${pageLabel}: supplementaryReads[${index}] is outside allowed runtime roots: ${relPath}`);
    }
  }
  return errors;
}

function appendReadLedger(summary, entries, lane) {
  const current = Array.isArray(summary.project?.readScopeLedger)
    ? summary.project.readScopeLedger
    : [];
  const next = [...current];
  const seen = new Set(current.map(item => `${item.actor}|${item.lane}|${item.path}|${item.reason}`));
  function add(item) {
    const key = `${item.actor}|${item.lane}|${item.path}|${item.reason}`;
    if (seen.has(key)) return;
    seen.add(key);
    next.push(item);
  }
  for (const entry of entries) {
    add({
      actor: 'page-sub-agent',
      lane,
      path: entry.sharedTemplate,
      reason: 'page runtime guide',
      scopeClass: 'page-runtime',
      declaredBeforeRead: true,
      recordedAt: entry.recorded_at,
      nodeId: entry.nodeId || null,
      htmlSrc: entry.htmlSrc || null,
    });
    add({
      actor: 'page-sub-agent',
      lane,
      path: entry.laneContract?.dispatchContract,
      reason: 'dispatch contract',
      scopeClass: 'dispatch-contract',
      declaredBeforeRead: true,
      recordedAt: entry.recorded_at,
      nodeId: entry.nodeId || null,
      htmlSrc: entry.htmlSrc || null,
    });
    for (const read of entry.supplementaryReads || []) {
      add({
        actor: 'page-sub-agent',
        lane,
        path: normalizeRelPath(read.path),
        reason: asString(read.reason) || 'supplementary read',
        ownerLane: asString(read.ownerLane) || lane,
        scopeClass: 'supplementary',
        declaredBeforeRead: true,
        recordedAt: entry.recorded_at,
        nodeId: entry.nodeId || null,
        htmlSrc: entry.htmlSrc || null,
      });
    }
  }
  summary.project.readScopeLedger = next;
}

function contextLoadedPath(item) {
  if (typeof item === 'string') return normalizeRelPath(item);
  if (!item || typeof item !== 'object') return null;
  return normalizeRelPath(item.path || item.file || item.relPath);
}

function contextLoadIsBodyRead(item) {
  if (typeof item === 'string') return false;
  if (!item || typeof item !== 'object') return false;
  if (item.bodyRead === true || item.declaredBeforeDispatch === true) return true;
  const status = String(item.readStatus || item.status || '').trim();
  return ['loaded', 'read', 'body-read'].includes(status);
}

function validateContextPreflight(summary, lane) {
  const errors = [];
  const project = summary.project || {};
  const requirements = parseContextRequirementsFromWorkflow(lane);
  errors.push(...requirements.errors.map(error => `[context-preflight] ${error}`));
  if (project.selectedIntentWorkflowRead !== true) {
    errors.push('[context-preflight] project.selectedIntentWorkflowRead must be true before dispatch');
  }
  const loaded = Array.isArray(project.contextRequirementsLoaded) ? project.contextRequirementsLoaded : [];
  const loadedByPath = new Map();
  for (const item of loaded) {
    const relPath = contextLoadedPath(item);
    if (!relPath) continue;
    loadedByPath.set(relPath, item);
  }
  for (const requirement of requirements.required) {
    const item = loadedByPath.get(requirement.path);
    if (!item) {
      errors.push(`[context-preflight] required context not loaded: ${requirement.path}`);
      continue;
    }
    if (isGeneralizedFlowControlActive(summary) && !contextLoadIsBodyRead(item)) {
      errors.push(`[context-preflight] ${requirement.path} must record bodyRead=true or readStatus="loaded"`);
    }
  }
  if (!project.contextReadScope && !Array.isArray(project.readScopeLedger)) {
    errors.push('[context-preflight] project.contextReadScope or project.readScopeLedger is required before dispatch');
  }
  return {
    success: errors.length === 0,
    errors,
    workflowPath: requirements.workflowPath,
    requiredContextFiles: requirements.required.map(item => item.path),
    optionalContextFiles: requirements.optional.map(item => item.path),
  };
}

function expectedAestheticsMode(packetType, summary) {
  if (packetType === 'RestorePagePacket') return 'high-fidelity';
  if (packetType === 'LibraryBoundPagePacket') return 'library-bound';
  return summary.project?.operatingMode || 'free-explore';
}

function structureHash(mobileNavigation) {
  const structure = mobileNavigation?.structure || {};
  const material = {
    items: Array.isArray(mobileNavigation?.items) ? mobileNavigation.items : [],
    navClass: structure.navClass || '',
    innerClass: structure.innerClass || '',
    itemTag: structure.itemTag || '',
    itemClass: structure.itemClass || '',
    iconClass: structure.iconClass || '',
    labelClass: structure.labelClass || ''
  };
  return sha256(JSON.stringify(material));
}

function pageNodeId(page) {
  return asString(page?.nodeId) || asString(page?.id) || null;
}

function pageHtmlSrc(page) {
  return asString(page?.htmlSrc) || asString(page?.devMetadata?.htmlSrc) || null;
}

function pageTitle(page) {
  return asString(page?.title) || asString(page?.name) || 'Untitled';
}

function inferFillCommand(summary, designDir, page, brandPrefix, headFillMode = null, normalizedHtmlSrc = null) {
  const htmlSrc = normalizedHtmlSrc || pageHtmlSrc(page);
  if (!htmlSrc) return null;
  const cssPath = relativeOrAbsolute(designDir, summary.designSource?.cssFilePath, 'colors_and_type.css');
  const htmlPath = path.join(designDir, htmlSrc);
  const title = pageTitle(page).replace(/"/g, '\\"');
  const lang = summary.project?.language || summary.language || 'zh-CN';
  const chartsFlag = page?.chartsRequired === true ? ' --charts' : '';
  const replaceHeadFlag = headFillMode === 'replace-head-after-body' ? ' --replace-head' : '';
  return `node ${shellQuote(deterministicToolPath('apply-html-head-contract.mjs'))} ${shellQuote(cssPath)} ${shellQuote(htmlPath)} --title=${shellQuote(title)} --lang=${shellQuote(lang)} --prefix=${shellQuote(brandPrefix)}${chartsFlag}${replaceHeadFlag}`;
}

function buildMobileNavigationEvidence(page, mobileNavigation) {
  if (!mobileNavigation || mobileNavigation.applies === false) {
    return {
      required: false,
      appliesToThisPage: false,
      canonicalHtmlIncluded: false,
      missingFields: []
    };
  }

  if (page.mobileNavigationApplies === false) {
    return {
      required: false,
      appliesToThisPage: false,
      omitReason: asString(page.mobileNavigationOmitReason) || null,
      canonicalHtmlIncluded: false,
      missingFields: asString(page.mobileNavigationOmitReason) ? [] : ['mobileNavigationOmitReason']
    };
  }

  const items = Array.isArray(mobileNavigation.items) ? mobileNavigation.items : [];
  const keys = items.map(item => asString(item?.key)).filter(Boolean);
  const activeKey = asString(page.mobileNavigationActiveKey);
  const structure = isObject(mobileNavigation.structure) ? mobileNavigation.structure : null;
  const canonicalHtmlByKey = isObject(structure?.canonicalHtmlByKey) ? structure.canonicalHtmlByKey : null;
  const canonicalHtml = activeKey && canonicalHtmlByKey ? asString(canonicalHtmlByKey[activeKey]) : null;

  const missingFields = [];
  if (keys.length < 3) missingFields.push('mobileNavigation.items');
  if (!activeKey) missingFields.push('pages[].mobileNavigationActiveKey');
  if (activeKey && keys.length > 0 && !keys.includes(activeKey)) {
    missingFields.push(`mobileNavigationActiveKey:${activeKey}:not-in-items`);
  }
  if (!structure) missingFields.push('mobileNavigation.structure');
  if (!canonicalHtmlByKey) missingFields.push('mobileNavigation.structure.canonicalHtmlByKey');
  if (canonicalHtmlByKey && activeKey && !canonicalHtml) {
    missingFields.push(`canonicalHtmlByKey.${activeKey}`);
  }

  return {
    required: true,
    appliesToThisPage: true,
    activeKey,
    contractPresent: Boolean(mobileNavigation),
    structurePresent: Boolean(structure),
    canonicalHtmlIncluded: Boolean(canonicalHtml),
    canonicalHtmlSource: activeKey
      ? `sharedProjectShellContract.mobileNavigation.structure.canonicalHtmlByKey.${activeKey}`
      : null,
    structureHash: structureHash(mobileNavigation),
    missingFields
  };
}

function validateTopLevel(summary, mode) {
  const errors = [];
  const fixHints = [];
  const addError = (msg) => errors.push(msg);
  const addFixHint = (field, action) => fixHints.push({ field, action });
  const project = summary.project || {};
  const pageCount = Array.isArray(summary.pages) ? summary.pages.length : 0;
  const activeContract = isLaneIsolationContractActive(summary);
  const expectedLane = laneForMode(summary, mode);
  if (summary.skillProvenance && summary.skillProvenance.name !== 'solo-design') {
    addError('skillProvenance.name must be "solo-design"');
  }
  if (activeContract && project.resolvedLane !== expectedLane) {
    addError(`project.resolvedLane must be "${expectedLane}" for --mode=${mode}`);
  }
  if (!asString(project.deviceType)) {
    addError('project.deviceType is required');
  }
  if (pageCount > 1 && !isObject(project.sharedProjectShellContract)) {
    addError('project.sharedProjectShellContract is required for multi-page dispatch');
  }
  if (pageCount === 0) {
    addError('pages[] must be non-empty');
  }
  if (mode === 'free-fast' && project.operatingMode === 'free-explore') {
    const cssEvidence = project.cssPreflightEvidence;
    if (!cssEvidence || cssEvidence.status !== 'passed') {
      addError('project.cssPreflightEvidence.status must be "passed" for free-fast free-explore dispatch');
    }
  }

  // Quality-efficiency preflight: visibility, copy blocks, validation discipline
  if (project.defaultDeliverableVisibility?.applies === true) {
    const regions = Array.isArray(project.defaultDeliverableVisibility.requiredVisibleRegions)
      ? project.defaultDeliverableVisibility.requiredVisibleRegions : [];
    if (regions.length === 0) {
      addError('defaultDeliverableVisibility.applies=true but requiredVisibleRegions[] is empty');
    }
    for (const [i, r] of regions.entries()) {
      if (!r?.htmlSrc) addError(`requiredVisibleRegions[${i}].htmlSrc is required`);
      if (!r?.selector) addError(`requiredVisibleRegions[${i}].selector is required`);
    }
  }

  if (project.textCriticality === 'high') {
    const checklist = project.deliverableCompletenessChecklist || {};
    const blocks = Array.isArray(checklist.requiredCopyBlocks) ? checklist.requiredCopyBlocks : [];
    if (blocks.length === 0) {
      addError('textCriticality=high requires deliverableCompletenessChecklist.requiredCopyBlocks[]');
    }
  }

  if (isQualityEfficiencyContractActive(summary) && !project.validationRunDiscipline) {
    addError('project.validationRunDiscipline must be declared before dispatch');
    addFixHint('project.validationRunDiscipline', 'write { "maxFullValidationRuns": 2, "softWarningsTriggerRepair": false, "blockingRepairMode": "targeted-once" }');
  }
  if (isGeneralizedFlowControlActive(summary)) {
    if (!project.lowValueCallWatchdog || typeof project.lowValueCallWatchdog !== 'object') {
      addError('project.lowValueCallWatchdog must be declared before dispatch');
      addFixHint('project.lowValueCallWatchdog', 'write { "applies": true, "noProgressNextAction": "enter_readiness_or_blocked_summary" }');
    } else {
      if (project.lowValueCallWatchdog.applies !== true) {
        addError('project.lowValueCallWatchdog.applies must be true');
      }
      if (!asString(project.lowValueCallWatchdog.noProgressNextAction)) {
        addError('project.lowValueCallWatchdog.noProgressNextAction is required');
      }
    }
    if (expectedLane === 'graphic_layout_static') {
      const checkpoints = Array.isArray(project.visualQualityCheckpoints) ? project.visualQualityCheckpoints : [];
      if (checkpoints.length < 4) {
        addError(`graphic_layout_static requires >= 4 visualQualityCheckpoints before dispatch, found ${checkpoints.length}`);
      }
      const requiredDimensions = new Set(['visual-anchor', 'information-hierarchy', 'composition-structure', 'implementation-strategy']);
      const presentDimensions = new Set(checkpoints.map(item => String(item?.dimension || '').trim()).filter(Boolean));
      for (const dimension of requiredDimensions) {
        if (!presentDimensions.has(dimension)) {
          addError(`visualQualityCheckpoints missing dimension: ${dimension}`);
        }
      }
    }
  }

  return { errors, fixHints };
}

function auditTaskQuery(taskQueryFile) {
  if (!taskQueryFile) {
    return {
      taskQueryAudited: false,
      proofSource: 'summary-only',
      largeWorkflowFilesInTaskQuery: null,
    };
  }
  const content = fs.readFileSync(path.resolve(taskQueryFile), 'utf8');
  const largeWorkflowFiles = [];
  const blockedLegacyTemplate = [
    'shared-runtime/blocked-legacy-entrypoints',
    ['blocked-legacy-page-template', 'md'].join('.'),
  ].join('/');
  for (const pattern of [
    'shared-runtime/agent-dispatch-runtime/shared-page-rendering-kernel.md',
    blockedLegacyTemplate,
  ]) {
    if (content.includes(pattern)) largeWorkflowFiles.push(pattern);
  }
  return {
    taskQueryAudited: true,
    proofSource: 'task-query-file',
    taskQueryHash: sha256(content),
    largeWorkflowFilesInTaskQuery: largeWorkflowFiles,
  };
}

async function buildManifest(summary, designDir, mode, taskQueryFile) {
  const lane = laneForMode(summary, mode);
  const packetType = packetTypeFor(lane);
  const sharedTemplate = runtimeGuideFor(lane);
  const dispatchContract = dispatchContractFor(lane);
  const aestheticsMode = expectedAestheticsMode(packetType, summary);
  const taskQueryAudit = auditTaskQuery(taskQueryFile);
  const brandPrefix = asString(summary.designSource?.brandPrefix) ||
    asString(summary.project?.brandPrefix) ||
    asString(summary.project?.cssPreflightEvidence?.brandPrefix) ||
    '';
  const cssFilePath = relativeOrAbsolute(designDir, summary.designSource?.cssFilePath, 'colors_and_type.css');
  const mobileNavigation = summary.project?.sharedProjectShellContract?.mobileNavigation;
  const now = new Date().toISOString();

  const entries = [];
  const errors = [];
  const pageInputs = (summary.pages || []).map(page => {
    const nodeId = pageNodeId(page);
    const rawHtmlSrc = pageHtmlSrc(page);
    const htmlPathCheck = rawHtmlSrc
      ? normalizeProjectRelativePath(rawHtmlSrc, designDir, {
        label: `${nodeId || '<unknown page>'}.htmlSrc`,
        requireExtension: '.html',
      })
      : { value: null, error: null };
    if (htmlPathCheck.error) errors.push(htmlPathCheck.error);
    const htmlSrc = htmlPathCheck.value;
    return {
      page,
      nodeId,
      htmlSrc,
      htmlFilePath: htmlSrc ? path.join(designDir, htmlSrc) : null,
    };
  });
  const contextPreflight = validateContextPreflight(summary, lane);
  errors.push(...contextPreflight.errors);
  const deterministicCommands = packetType === 'RestorePagePacket'
    ? buildDeterministicCommands(designDir, { mode, requiresFinalResponseDraft: true })
    : null;

  let restoreFields = null;
  let restoreContractStatus = null;
  const [preDispatchFileHashes, headFillModes] = await Promise.all([
    collectPreDispatchFileHashes(designDir),
    mapLimit(pageInputs, 8, async ({ page, htmlSrc }) => inferHeadFillMode(page, designDir, htmlSrc)),
  ]);
  if (packetType === 'RestorePagePacket') {
    const project = summary.project || {};
    restoreContractStatus = loadRestoreContractReport(designDir, errors);
    const restoreErrors = validateRestoreDispatchReadiness(project);
    for (const err of restoreErrors) {
      errors.push(`[restore-preflight] ${err}`);
    }
    const sourceType = String(
      project?.sourceType ||
      project?.intentProfile?.sourceType ||
      project?.referenceCaptureEvidence?.sourceType ||
      ''
    ).trim();
    const facts = Array.isArray(project?.measuredSourceFacts)
      ? project.measuredSourceFacts
      : (Array.isArray(project?.restorationContractLite?.measuredSourceFacts)
        ? project.restorationContractLite.measuredSourceFacts
        : []);
    const checkpoints = Array.isArray(project?.restoreVisualCheckpoints) ? project.restoreVisualCheckpoints : [];
    const captureEvidence = project?.referenceCaptureEvidence;
    restoreFields = {
      sourceType: sourceType || null,
      referenceCaptureEvidencePresent: Boolean(captureEvidence && typeof captureEvidence === 'object'),
      measuredSourceFactsCount: facts.length,
      highPriorityMeasuredSourceFactsCount: facts.filter(f => f?.priority === 'high').length,
      restoreVisualCheckpointsCount: checkpoints.length,
      highPriorityCheckpointCount: checkpoints.filter(c => c?.priority === 'high').length,
      sourceTypeEvidenceConsistent: restoreErrors.length === 0,
    };
  }

  for (const [pageIndex, pageInput] of pageInputs.entries()) {
    const { page, nodeId, htmlSrc, htmlFilePath } = pageInput;
    const pageMissing = [];
    if (!nodeId) pageMissing.push('nodeId');
    if (!htmlSrc) pageMissing.push('htmlSrc');
    if (!cssFilePath) pageMissing.push('cssFilePath');
    if (!htmlFilePath) pageMissing.push('htmlFilePath');
    if (!brandPrefix && summary.project?.cssPreflightEvidence?.prefixMode !== 'prefixless') pageMissing.push('brandPrefix');

    const mobileNavigationEvidence = buildMobileNavigationEvidence(page, mobileNavigation);
    const missingFields = [...pageMissing, ...(mobileNavigationEvidence.missingFields || [])];
    if (missingFields.length > 0) {
      errors.push(`${htmlSrc || nodeId || '<unknown page>'}: missing ${missingFields.join(', ')}`);
    }
    const supplementaryReads = Array.isArray(page.supplementaryReads)
      ? page.supplementaryReads
      : [];
    errors.push(...validateSupplementaryReads(supplementaryReads, lane, htmlSrc || nodeId || '<unknown page>'));

    const allowedWritePaths = [];
    const allowedWriteInputs = [
      htmlSrc,
      'assets/',
      ...(Array.isArray(page.allowedWritePaths) ? page.allowedWritePaths : []),
    ].filter(Boolean);
    for (const [allowedIndex, allowedPath] of allowedWriteInputs.entries()) {
      const normalized = normalizeProjectRelativePath(allowedPath, designDir, {
        label: `${htmlSrc || nodeId || '<unknown page>'}.allowedWritePaths[${allowedIndex}]`,
        allowDirectory: String(allowedPath).replace(/\\/g, '/').endsWith('/'),
      });
      if (normalized.error) {
        errors.push(normalized.error);
      } else if (!allowedWritePaths.includes(normalized.value)) {
        allowedWritePaths.push(normalized.value);
      }
    }

    const headFillMode = headFillModes[pageIndex];

    entries.push({
      recorded_at: now,
      generatedBy: 'build-page-dispatch-manifest.mjs',
      packetType,
      laneContract: {
        resolvedLane: lane,
        packetType,
        pageRuntimeGuide: sharedTemplate,
        dispatchContract,
      },
      taskLinePresent: true,
      outputPathPresent: Boolean(htmlFilePath),
      sharedTemplate,
      nodeId,
      htmlSrc,
      supplementaryReads,
      allowedWritePaths,
      forbiddenWriteRoots: [
        '*.design',
        'runtime-orchestration-summary.json',
        'validation-report.json',
        'finish-readiness-report.json',
        'restore-contract-report.json',
        'page-generation-summary.json',
      ],
      toolPolicy: {
        todoWriteAllowed: false,
        validationScriptsAllowed: false,
        previewAllowed: false,
        helperScriptsAllowed: false,
        designFileWriteAllowed: false,
        allowedWritePaths,
      },
      skillRuntime: buildSkillRuntimePacket(designDir, { nodeId, htmlSrc }),
      cssFilePath,
      htmlFilePath,
      brandPrefix,
      aestheticsMode,
      toolDisciplineBlockPresent: true,
      fillHtmlHeadCommand: packetType === 'RestorePagePacket' || page.stateRole === 'derived'
        ? null
        : inferFillCommand(summary, designDir, page, brandPrefix, headFillMode, htmlSrc),
      headFillMode,
      viewportMode: page.viewportMode || summary.project?.viewportMode || null,
      completionSchemaExpected: packetType === 'RestorePagePacket'
        ? 'restore'
        : (packetType === 'FreePagePacket' ? 'compact' : 'full'),
      restoreFields: packetType !== 'RestorePagePacket' ? null : restoreFields,
      restoreContractStatus: packetType !== 'RestorePagePacket' ? null : restoreContractStatus,
      restoreCompactPacket: packetType !== 'RestorePagePacket'
        ? null
        : buildRestoreCompactPacket(summary.project || {}, page),
      deterministicCommands,
      sourceAuthorityLock: packetType !== 'RestorePagePacket'
        ? null
        : (summary.project?.sourceAuthorityLock || summary.project?.referenceCaptureEvidence?.sourceAuthority || null),
      preDispatchFileHashes,
      contextPreflight: {
        workflowPath: contextPreflight.workflowPath,
        requiredContextFiles: contextPreflight.requiredContextFiles,
        optionalContextFiles: contextPreflight.optionalContextFiles,
        passed: contextPreflight.success,
      },
      pageSliceOnly: true,
      requiredFieldsPresent: missingFields.length === 0,
      missingFields,
      fillHtmlHeadCommandValid: true,
      mobileNavigation: mobileNavigationEvidence,
      persistedToSummary: true,
      ...taskQueryAudit
    });
  }

  return { entries, errors };
}

function normalizeSkillProvenanceName(summary, fixHints) {
  const provenance = summary?.skillProvenance;
  if (!provenance || !provenance.name) return;
  if (provenance.name === 'solo-design') return;
  if (!String(provenance.name).startsWith('solo-design')) return;
  const originalName = provenance.name;
  provenance.name = 'solo-design';
  fixHints.push({
    field: 'skillProvenance.name',
    action: `normalized "${originalName}" to "solo-design" (auto-iteration variant)`,
  });
}

function normalizeSummary(summary, mode) {
  const fixHints = [];
  if (!summary.skillProvenance) {
    summary.skillProvenance = { name: 'solo-design' };
    fixHints.push({ field: 'skillProvenance.name', action: 'auto-set to solo-design' });
  }
  if (!summary.project) summary.project = {};
  if (!summary.project.resolvedLane) {
    summary.project.resolvedLane = laneForMode(summary, mode);
    fixHints.push({ field: 'project.resolvedLane', action: `auto-set to ${summary.project.resolvedLane}` });
  }
  if (!summary.project.deviceType) {
    summary.project.deviceType = 'desktop';
    fixHints.push({ field: 'project.deviceType', action: 'defaulted to desktop' });
  }
  if (!summary.project.cssPreflightEvidence) {
    summary.project.cssPreflightEvidence = { prefixMode: 'standard', brandPrefix: '' };
    fixHints.push({ field: 'project.cssPreflightEvidence', action: 'initialized with standard prefix mode' });
  }
  const css = summary.project.cssPreflightEvidence;
  if (!css.prefixMode) {
    css.prefixMode = css.brandPrefix === '' ? 'prefixless' : 'standard';
    fixHints.push({ field: 'project.cssPreflightEvidence.prefixMode', action: `inferred as ${css.prefixMode}` });
  }
  if (!Array.isArray(summary.pages)) {
    summary.pages = [];
    fixHints.push({ field: 'pages', action: 'initialized as empty array' });
  }
  for (const [i, page] of summary.pages.entries()) {
    if (!page.nodeId) {
      page.nodeId = `page-${String(i + 1).padStart(3, '0')}`;
      fixHints.push({ field: `pages[${i}].nodeId`, action: `auto-assigned ${page.nodeId}` });
    }
    if (!page.htmlSrc) {
      page.htmlSrc = `pages/${page.nodeId}.html`;
      fixHints.push({ field: `pages[${i}].htmlSrc`, action: `defaulted to ${page.htmlSrc}` });
    }
  }
  return fixHints;
}

async function inferHeadFillMode(page, designDir, normalizedHtmlSrc = null) {
  const htmlSrc = normalizedHtmlSrc || pageHtmlSrc(page);
  if (!htmlSrc) return null;
  const htmlPath = path.join(designDir, htmlSrc);
  let content;
  try {
    content = await fs.promises.readFile(htmlPath, 'utf8');
  } catch (error) {
    if (error?.code === 'ENOENT') return 'skeleton-first';
    throw error;
  }
  const hasBody = /<body[^>]*>[\s\S]*\S[\s\S]*<\/body>/i.test(content);
  return hasBody ? 'replace-head-after-body' : 'skeleton-first';
}

async function main() {
  const { designDir, mode, taskQueryFile, initOrNormalize, json, errors } = parseArgs(process.argv.slice(2));
  if (errors.length > 0 || !designDir) {
    for (const error of errors) console.error('[ERROR]', error);
    console.error('Usage: node build-page-dispatch-manifest.mjs <design-project-path> --mode=free-fast|restore|... [--init-or-normalize-summary] [--json] [--task-query-file=<path>]');
    process.exit(1);
  }

  const resolvedDesignDir = path.resolve(designDir);
  const summaryPath = path.join(resolvedDesignDir, 'runtime-orchestration-summary.json');
  if (!fs.existsSync(summaryPath)) {
    const errMsg = 'runtime-orchestration-summary.json not found';
    if (json) {
      console.log(JSON.stringify({ success: false, errors: [errMsg], fixHints: [] }, null, 2));
    } else {
      console.error('[ERROR]', errMsg, summaryPath);
    }
    process.exit(1);
  }

  const summary = readJson(summaryPath);
  let fixHints = [];

  normalizeSkillProvenanceName(summary, fixHints);

  if (initOrNormalize) {
    fixHints.push(...normalizeSummary(summary, mode));
    if (fixHints.length > 0) {
      writeJson(summaryPath, summary);
    }
  }

  // Validate prefixless CSS: empty brandPrefix with prefixMode=prefixless is valid
  const cssEvidence = summary.project?.cssPreflightEvidence;
  if (cssEvidence && cssEvidence.prefixMode === 'prefixless' && cssEvidence.brandPrefix === '') {
    // explicitly valid — do not treat empty brandPrefix as missing
  }

  const { errors: topLevelErrors, fixHints: topLevelFixHints } = validateTopLevel(summary, mode);
  fixHints.push(...topLevelFixHints);
  const { entries, errors: manifestErrors } = await buildManifest(summary, resolvedDesignDir, mode, taskQueryFile);

  // Validate head fill mode consistency for each entry.
  for (const [i, entry] of entries.entries()) {
    const page = (summary.pages || [])[i];
    if (page) {
      if (entry.headFillMode === 'replace-head-after-body' && entry.fillHtmlHeadCommand && !String(entry.fillHtmlHeadCommand).includes('--replace-head')) {
        manifestErrors.push(`${entry.htmlSrc || entry.nodeId}: body already exists, fillHtmlHeadCommand must use --replace-head mode`);
        fixHints.push({ field: `entries[${i}].headFillMode`, action: 'requires --replace-head after body content exists' });
      }
    }
  }

  const allErrors = [...topLevelErrors, ...manifestErrors];
  if (allErrors.length > 0) {
    if (json) {
      console.log(JSON.stringify({ success: false, errors: allErrors, fixHints, entries }, null, 2));
    } else {
      console.error('[ERROR_CODE] dispatch_preflight_manifest_invalid');
      for (const error of allErrors) console.error('[ERROR]', error);
      if (fixHints.length > 0) {
        console.error('\nFix hints:');
        for (const hint of fixHints) console.error(`  ${hint.field}: ${hint.action}`);
      }
      console.error('No manifest was written. Fix runtime-orchestration-summary.json before dispatching page tasks.');
    }
    process.exit(1);
  }

  summary.project = summary.project || {};
  summary.project.dispatchPreflightManifest = entries;
  delete summary.project.expectedDispatches;
  appendReadLedger(summary, entries, laneForMode(summary, mode));
  writeJson(summaryPath, summary);
  const runtimeDispatchManifestPath = writeRuntimeDispatchManifest(resolvedDesignDir, summaryPath, summary, entries, mode);

  if (json) {
    console.log(JSON.stringify({
      success: true,
      entriesWritten: entries.length,
      fixHints,
      entries,
      runtimeDispatchManifestPath,
    }, null, 2));
  } else {
    console.log(`[OK] dispatchPreflightManifest written: ${entries.length} entr${entries.length === 1 ? 'y' : 'ies'}`);
    console.log(`Summary: ${summaryPath}`);
    console.log(`Runtime dispatch manifest: ${runtimeDispatchManifestPath}`);
    if (fixHints.length > 0) {
      console.log(`\nNormalized ${fixHints.length} field(s):`);
      for (const hint of fixHints) console.log(`  ${hint.field}: ${hint.action}`);
    }
  }
}

main().catch(error => {
  console.error('[ERROR]', error?.stack || error?.message || String(error));
  process.exit(1);
});
