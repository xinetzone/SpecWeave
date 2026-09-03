#!/usr/bin/env node

/**
 * Validate the restore_1to1 contract before page dispatch.
 *
 * This preflight is intentionally narrow: it reads the orchestration summary
 * and CSS token file, writes a small report, and never edits page HTML,
 * assets, .design, or repair state.
 *
 * Usage:
 *   node validate-restore-contract.mjs <design-project-path> [--mode=preflight] [--report-json=<path>] [--apply-safe-fixes] [--json]
 */

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const VALID_SOURCE_TYPES = new Set(['image', 'url', 'image+url']);
const REQUIRED_FACT_CATEGORIES = new Set([
  'viewport',
  'layout-region',
  'color-surface',
  'component-proportion',
  'density-spacing',
]);
const REQUIRED_CHECKPOINT_DIMENSIONS = new Set([
  'layout',
  'color-rhythm',
  'typography',
  'component-proportion',
  'density',
  'fine-detail',
]);
const URL_LONG_PAGE_GROUPS = ['first-screen', 'middle-section', 'footer-bottom'];
const IMAGE_DEVICE_GROUPS = ['outer-frame', 'device-shell', 'inner-screen', 'primary-object'];
const SEMANTIC_TOKEN_SUFFIXES = [
  'background',
  'foreground',
  'card',
  'primary',
  'border',
  'muted',
  'radius-sm',
  'radius-md',
  'radius-lg',
];

function parseArgs(argv) {
  const positional = [];
  const errors = [];
  let mode = 'preflight';
  let reportJson = null;
  let applySafeFixes = false;
  let json = false;

  for (const arg of argv) {
    if (arg.startsWith('--mode=')) {
      mode = arg.slice('--mode='.length);
    } else if (arg.startsWith('--report-json=')) {
      reportJson = arg.slice('--report-json='.length);
    } else if (arg === '--apply-safe-fixes') {
      applySafeFixes = true;
    } else if (arg === '--json') {
      json = true;
    } else if (arg.startsWith('--')) {
      errors.push(`Unknown flag: ${arg}`);
    } else {
      positional.push(arg);
    }
  }

  if (!positional[0]) errors.push('Missing design project path');
  if (mode !== 'preflight') errors.push(`Unsupported --mode=${mode}`);
  return {
    designDir: positional[0] ? path.resolve(positional[0]) : null,
    mode,
    reportJson,
    applySafeFixes,
    json,
    errors,
  };
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

function asString(value) {
  return typeof value === 'string' && value.trim() ? value.trim() : null;
}

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function hashFileIfExists(filePath) {
  if (!filePath || !fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) return null;
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

function resolveProjectPath(designDir, value, fallbackRel) {
  const raw = asString(value) || fallbackRel;
  if (!raw) return null;
  return path.isAbsolute(raw) ? raw : path.join(designDir, raw);
}

function normalizeRelPath(value) {
  return String(value || '').replace(/\\/g, '/').replace(/^\.\//, '');
}

function uniqueStrings(values) {
  return [...new Set(values.map(value => String(value || '').trim()).filter(Boolean))];
}

function sourceTypeOf(project) {
  return asString(project?.sourceType) ||
    asString(project?.intentProfile?.sourceType) ||
    asString(project?.referenceCaptureEvidence?.sourceType) ||
    '';
}

function factsOf(project) {
  return Array.isArray(project?.measuredSourceFacts)
    ? project.measuredSourceFacts
    : (Array.isArray(project?.restorationContractLite?.measuredSourceFacts)
      ? project.restorationContractLite.measuredSourceFacts
      : []);
}

function checkpointsOf(project) {
  return Array.isArray(project?.restoreVisualCheckpoints) ? project.restoreVisualCheckpoints : [];
}

function coverageRowsOf(project) {
  if (Array.isArray(project?.sourceRegionCoverage)) {
    return { rows: project.sourceRegionCoverage, source: 'project.sourceRegionCoverage' };
  }
  if (Array.isArray(project?.restorationContractLite?.sourceRegionCoverage)) {
    return { rows: project.restorationContractLite.sourceRegionCoverage, source: 'project.restorationContractLite.sourceRegionCoverage' };
  }
  return { rows: [], source: null };
}

function coverageStatus(row) {
  return asString(row?.mappedStatus) || asString(row?.status) || '';
}

function requiredGroupsFor(sourceType, profile) {
  const groups = [];
  if (sourceType === 'url' && profile?.documentLengthClass !== 'short') groups.push(...URL_LONG_PAGE_GROUPS);
  if ((sourceType === 'image' || sourceType === 'image+url') && profile?.deviceFramePresent === true) groups.push(...IMAGE_DEVICE_GROUPS);
  return uniqueStrings(groups);
}

function buildSafeFixPlan(summary) {
  const project = summary?.project || {};
  const fixes = [];
  const sourceType = sourceTypeOf(project);
  const sourceTypeIsKnown = VALID_SOURCE_TYPES.has(sourceType);
  const profile = isObject(project.sourceDocumentProfile) ? project.sourceDocumentProfile : null;
  const requiredGroups = requiredGroupsFor(sourceType, profile || {});

  function addFix(fix) {
    fixes.push({
      safe: true,
      ...fix,
    });
  }

  if (!profile && sourceTypeIsKnown) {
    const value = { sourceType };
    if (requiredGroups.length > 0) value.requiredRegionGroups = requiredGroups;
    addFix({
      field: 'project.sourceDocumentProfile',
      action: 'set-if-missing',
      value,
      reason: 'sourceType is already locked and sourceDocumentProfile is missing',
    });
  } else if (profile) {
    if (!asString(profile.sourceType) && sourceTypeIsKnown) {
      addFix({
        field: 'project.sourceDocumentProfile.sourceType',
        action: 'set-if-missing',
        value: sourceType,
        reason: 'sourceDocumentProfile.sourceType is uniquely derived from locked restore sourceType',
      });
    }
    if ((!Array.isArray(profile.requiredRegionGroups) || profile.requiredRegionGroups.length === 0) && requiredGroups.length > 0) {
      addFix({
        field: 'project.sourceDocumentProfile.requiredRegionGroups',
        action: 'set-if-missing',
        value: requiredGroups,
        reason: 'canonical restore region groups can be derived without visual judgment',
      });
    }
  }

  if (!Array.isArray(project.sourceRegionCoverage) && Array.isArray(project.restorationContractLite?.sourceRegionCoverage)) {
    addFix({
      field: 'project.sourceRegionCoverage',
      action: 'promote-from',
      value: 'project.restorationContractLite.sourceRegionCoverage',
      reason: 'sourceRegionCoverage is already present in restorationContractLite and should be promoted to the project root',
    });
  }

  const coverageSources = [
    { prefix: 'project.sourceRegionCoverage', rows: Array.isArray(project.sourceRegionCoverage) ? project.sourceRegionCoverage : [] },
    { prefix: 'project.restorationContractLite.sourceRegionCoverage', rows: Array.isArray(project.restorationContractLite?.sourceRegionCoverage) ? project.restorationContractLite.sourceRegionCoverage : [] },
  ];
  for (const source of coverageSources) {
    for (const [index, row] of source.rows.entries()) {
      if (!isObject(row)) continue;
      if (!asString(row.status) && asString(row.mappedStatus)) {
        addFix({
          field: `${source.prefix}[${index}].status`,
          action: 'set-if-missing',
          value: row.mappedStatus,
          reason: 'status can be normalized from mappedStatus alias',
        });
      }
      if (!asString(row.mappedStatus) && asString(row.status)) {
        addFix({
          field: `${source.prefix}[${index}].mappedStatus`,
          action: 'set-if-missing',
          value: row.status,
          reason: 'mappedStatus can be normalized from status alias',
        });
      }
    }
  }

  return fixes;
}

function applySafeFixPlan(summary, fixPlan) {
  if (!summary.project || typeof summary.project !== 'object') summary.project = {};
  const project = summary.project;
  const appliedFixes = [];
  let changed = false;

  function markApplied(fix) {
    appliedFixes.push({ ...fix, applied: true });
    changed = true;
  }

  for (const fix of fixPlan.filter(item => item && item.safe === true)) {
    if (fix.field === 'project.sourceDocumentProfile' && fix.action === 'set-if-missing') {
      if (!isObject(project.sourceDocumentProfile)) {
        project.sourceDocumentProfile = { ...fix.value };
        markApplied(fix);
      }
    } else if (fix.field === 'project.sourceDocumentProfile.sourceType' && fix.action === 'set-if-missing') {
      if (isObject(project.sourceDocumentProfile) && !asString(project.sourceDocumentProfile.sourceType)) {
        project.sourceDocumentProfile.sourceType = fix.value;
        markApplied(fix);
      }
    } else if (fix.field === 'project.sourceDocumentProfile.requiredRegionGroups' && fix.action === 'set-if-missing') {
      if (isObject(project.sourceDocumentProfile) && (!Array.isArray(project.sourceDocumentProfile.requiredRegionGroups) || project.sourceDocumentProfile.requiredRegionGroups.length === 0)) {
        project.sourceDocumentProfile.requiredRegionGroups = fix.value;
        markApplied(fix);
      }
    } else if (fix.field === 'project.sourceRegionCoverage' && fix.action === 'promote-from') {
      if (!Array.isArray(project.sourceRegionCoverage) && Array.isArray(project.restorationContractLite?.sourceRegionCoverage)) {
        project.sourceRegionCoverage = JSON.parse(JSON.stringify(project.restorationContractLite.sourceRegionCoverage));
        markApplied(fix);
      }
    } else {
      const match = fix.field.match(/^project(?:\.restorationContractLite)?\.sourceRegionCoverage\[(\d+)\]\.(status|mappedStatus)$/);
      if (!match) continue;
      const rows = fix.field.startsWith('project.restorationContractLite.')
        ? project.restorationContractLite?.sourceRegionCoverage
        : project.sourceRegionCoverage;
      const row = Array.isArray(rows) ? rows[Number(match[1])] : null;
      const key = match[2];
      if (isObject(row) && !asString(row[key])) {
        row[key] = fix.value;
        markApplied(fix);
      }
    }
  }

  return { changed, appliedFixes };
}

function normalizeDimension(value) {
  const raw = String(value || '').trim().toLowerCase().replaceAll('_', '-').replace(/\s+/g, '-');
  const aliases = new Map([
    ['color', 'color-rhythm'],
    ['colors', 'color-rhythm'],
    ['typography-scale', 'typography'],
    ['component', 'component-proportion'],
    ['components', 'component-proportion'],
    ['component-ratio', 'component-proportion'],
    ['spacing', 'density'],
    ['spacing-density', 'density'],
    ['detail', 'fine-detail'],
    ['details', 'fine-detail'],
  ]);
  return aliases.get(raw) || raw;
}

function validateRestoreContract(designDir, summary) {
  const errors = [];
  const warnings = [];
  const evidence = {};
  const addError = (loc, message) => errors.push(`[${loc}] ${message}`);
  const addWarning = (loc, message) => warnings.push(`[${loc}] ${message}`);
  const project = summary?.project || {};
  const pages = Array.isArray(summary?.pages) ? summary.pages : [];
  const sourceType = sourceTypeOf(project);

  evidence.sourceType = sourceType || null;

  if (!VALID_SOURCE_TYPES.has(sourceType)) {
    addError('restore-source-type', `sourceType must be image, url, or image+url; found ${sourceType || '(missing)'}`);
  }

  const captureEvidence = project.referenceCaptureEvidence;
  if (!isObject(captureEvidence)) {
    addError('restore-source-authority', 'project.referenceCaptureEvidence is required');
  }

  const lock = project.sourceAuthorityLock;
  if (!isObject(lock)) {
    addError('restore-source-authority', 'project.sourceAuthorityLock is required before restore preflight');
  } else {
    if (!asString(lock.visualAuthority)) addError('restore-source-authority', 'sourceAuthorityLock.visualAuthority is required');
    if (lock.mayOverrideVisualAuthority !== false) addError('restore-source-authority', 'sourceAuthorityLock.mayOverrideVisualAuthority must be false');
    if (lock.lockedBeforeDispatch !== true) addError('restore-source-authority', 'sourceAuthorityLock.lockedBeforeDispatch must be true');
  }

  const identity = project.sourceIdentity;
  if (!isObject(identity)) {
    addError('restore-source-identity', 'project.sourceIdentity is required before measuredSourceFacts');
  } else {
    if (!asString(identity.businessType)) addError('restore-source-identity', 'sourceIdentity.businessType is required');
    if (!Array.isArray(identity.coreObjects) || identity.coreObjects.length === 0) {
      addError('restore-source-identity', 'sourceIdentity.coreObjects[] is required');
    }
    if (!asString(identity.deviceType)) addError('restore-source-identity', 'sourceIdentity.deviceType is required');
    if (!asString(identity.pageTitle)) addError('restore-source-identity', 'sourceIdentity.pageTitle is required');
  }

  const stateLock = project.pageStateLock;
  if (!isObject(stateLock)) {
    addError('restore-page-state-lock', 'project.pageStateLock is required before measuredSourceFacts');
  } else {
    if (!asString(stateLock.currentState)) addError('restore-page-state-lock', 'pageStateLock.currentState is required');
    if (!Array.isArray(stateLock.forbiddenDeviations) || stateLock.forbiddenDeviations.length === 0) {
      addError('restore-page-state-lock', 'pageStateLock.forbiddenDeviations[] is required');
    }
  }

  const profile = project.sourceDocumentProfile;
  if (!isObject(profile)) {
    addError('restore-document-profile', 'project.sourceDocumentProfile is required');
  } else {
    if (!asString(profile.sourceType)) addError('restore-document-profile', 'sourceDocumentProfile.sourceType is required');
    if (asString(profile.sourceType) && sourceType && profile.sourceType !== sourceType) {
      addError('restore-document-profile', `sourceDocumentProfile.sourceType=${profile.sourceType} must match sourceType=${sourceType}`);
    }
    if (!Array.isArray(profile.requiredRegionGroups) || profile.requiredRegionGroups.length === 0) {
      addError('restore-document-profile', 'sourceDocumentProfile.requiredRegionGroups[] is required');
    }
  }

  const facts = factsOf(project);
  evidence.measuredSourceFactsCount = facts.length;
  if (facts.length < 8) addError('restore-measured-source-facts', `measuredSourceFacts requires >= 8 rows; found ${facts.length}`);
  const highFacts = facts.filter(fact => fact?.priority === 'high');
  evidence.highPriorityMeasuredSourceFactsCount = highFacts.length;
  if (highFacts.length < 5) addError('restore-measured-source-facts', `measuredSourceFacts requires >= 5 high-priority rows; found ${highFacts.length}`);
  const categories = new Set();
  const factIds = new Set();
  let highFactsWithMeasurementBasis = 0;
  for (const [index, fact] of facts.entries()) {
    if (!isObject(fact)) {
      addError('restore-measured-source-facts', `measuredSourceFacts[${index}] must be an object`);
      continue;
    }
    const id = asString(fact.id);
    const category = asString(fact.category);
    if (!id) addError('restore-measured-source-facts', `measuredSourceFacts[${index}].id is required`);
    else factIds.add(id);
    if (!category) addError('restore-measured-source-facts', `measuredSourceFacts[${index}].category is required`);
    else categories.add(category);
    if (!asString(fact.sourceRegion)) addError('restore-measured-source-facts', `measuredSourceFacts[${index}].sourceRegion is required`);
    if (!asString(fact.fact)) addError('restore-measured-source-facts', `measuredSourceFacts[${index}].fact is required`);
    if (!asString(fact.priority)) addError('restore-measured-source-facts', `measuredSourceFacts[${index}].priority is required`);
    if (fact.priority === 'high' && asString(fact.measurementBasis)) highFactsWithMeasurementBasis += 1;
  }
  const missingCategories = [...REQUIRED_FACT_CATEGORIES].filter(category => !categories.has(category));
  if (missingCategories.length > 0) {
    addError('restore-measured-source-facts', `measuredSourceFacts missing categories: ${missingCategories.join(', ')}`);
  }
  evidence.highPriorityFactsWithMeasurementBasis = highFactsWithMeasurementBasis;
  if (highFactsWithMeasurementBasis < 5) {
    addError('restore-measured-source-facts', `at least 5 high-priority measuredSourceFacts require measurementBasis; found ${highFactsWithMeasurementBasis}`);
  }

  const checkpoints = checkpointsOf(project);
  evidence.restoreVisualCheckpointsCount = checkpoints.length;
  if (checkpoints.length < 8) addError('restore-visual-checkpoints', `restoreVisualCheckpoints requires >= 8 rows; found ${checkpoints.length}`);
  const highCheckpoints = checkpoints.filter(checkpoint => checkpoint?.priority === 'high');
  evidence.highPriorityCheckpointCount = highCheckpoints.length;
  if (highCheckpoints.length < 5) addError('restore-visual-checkpoints', `restoreVisualCheckpoints requires >= 5 high-priority rows; found ${highCheckpoints.length}`);
  const dimensions = new Set();
  for (const [index, checkpoint] of checkpoints.entries()) {
    if (!isObject(checkpoint)) {
      addError('restore-visual-checkpoints', `restoreVisualCheckpoints[${index}] must be an object`);
      continue;
    }
    const dimension = normalizeDimension(checkpoint.dimension || checkpoint.category || checkpoint.taxonomy);
    if (dimension) dimensions.add(dimension);
    if (checkpoint.priority === 'high') {
      if (!asString(checkpoint.sourceFact) && !asString(checkpoint.sourceObservation)) {
        addError('restore-visual-checkpoints', `restoreVisualCheckpoints[${index}] high-priority row requires sourceFact or sourceObservation`);
      }
      if (!asString(checkpoint.expected) && !asString(checkpoint.targetImplementation)) {
        addError('restore-visual-checkpoints', `restoreVisualCheckpoints[${index}] high-priority row requires expected or targetImplementation`);
      }
    }
  }
  const missingDimensions = [...REQUIRED_CHECKPOINT_DIMENSIONS].filter(dimension => !dimensions.has(dimension));
  if (missingDimensions.length > 0) {
    addError('restore-visual-checkpoints', `restoreVisualCheckpoints missing dimensions: ${missingDimensions.join(', ')}`);
  }

  const { rows: coverageRows, source: coverageSource } = coverageRowsOf(project);
  evidence.sourceRegionCoverageSource = coverageSource;
  evidence.sourceRegionCoverageCount = coverageRows.length;
  if (coverageRows.length === 0) {
    addError('restore-region-coverage', 'project.sourceRegionCoverage[] is required');
  } else if (coverageSource !== 'project.sourceRegionCoverage') {
    addWarning('restore-region-coverage', 'sourceRegionCoverage should be promoted to project.sourceRegionCoverage to avoid schema drift');
  }

  const requiredRegionGroups = new Set(Array.isArray(profile?.requiredRegionGroups) ? profile.requiredRegionGroups.map(String) : []);
  if (sourceType === 'url' && profile?.documentLengthClass !== 'short') {
    for (const group of URL_LONG_PAGE_GROUPS) requiredRegionGroups.add(group);
  }
  if ((sourceType === 'image' || sourceType === 'image+url') && profile?.deviceFramePresent === true) {
    for (const group of IMAGE_DEVICE_GROUPS) requiredRegionGroups.add(group);
  }

  const mappedGroups = new Set();
  for (const [index, row] of coverageRows.entries()) {
    if (!isObject(row)) {
      addError('restore-region-coverage', `sourceRegionCoverage[${index}] must be an object`);
      continue;
    }
    const status = coverageStatus(row);
    if (['high', 'medium'].includes(row.priority) && !['mapped', 'intentionally-deviated'].includes(status)) {
      addError('restore-region-coverage', `sourceRegionCoverage[${index}] ${row.priority} row must be mapped or intentionally-deviated; found ${status || '(missing)'}`);
    }
    const group = asString(row.regionGroup);
    if (!group && ['high', 'medium'].includes(row.priority)) {
      addError('restore-region-coverage', `sourceRegionCoverage[${index}].regionGroup is required for high/medium rows`);
    }
    if (group && ['mapped', 'intentionally-deviated'].includes(status)) mappedGroups.add(group);
  }
  const missingGroups = [...requiredRegionGroups].filter(group => !mappedGroups.has(group));
  evidence.requiredRegionGroups = [...requiredRegionGroups];
  if (missingGroups.length > 0) {
    addError('restore-region-coverage', `required region groups not covered: ${missingGroups.join(', ')}`);
  }

  if (pages.length === 0) addError('restore-pages', 'pages[] must be non-empty before restore dispatch');
  for (const [index, page] of pages.entries()) {
    if (!asString(page?.nodeId) && !asString(page?.id)) addError('restore-pages', `pages[${index}].nodeId is required`);
    if (!asString(page?.htmlSrc) && !asString(page?.devMetadata?.htmlSrc)) addError('restore-pages', `pages[${index}].htmlSrc is required`);
  }

  const cssPath = resolveProjectPath(designDir, summary?.designSource?.cssFilePath, 'colors_and_type.css');
  const brandPrefix = asString(summary?.designSource?.brandPrefix) ||
    asString(project.brandPrefix) ||
    asString(project.cssPreflightEvidence?.brandPrefix) ||
    '';
  evidence.cssFilePath = cssPath;
  evidence.brandPrefix = brandPrefix || null;
  if (!cssPath || !fs.existsSync(cssPath)) {
    addError('restore-css-preflight', `CSS token file not found: ${cssPath || '(missing)'}`);
  } else {
    const css = fs.readFileSync(cssPath, 'utf8');
    const requiredTokens = SEMANTIC_TOKEN_SUFFIXES.map(suffix => brandPrefix ? `--${brandPrefix}-${suffix}` : `--${suffix}`);
    const missingTokens = requiredTokens.filter(token => !new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*:`).test(css));
    if (missingTokens.length > 0) {
      addError('restore-css-preflight', `CSS missing semantic aliases: ${missingTokens.join(', ')}`);
    }
    evidence.cssHash = hashFileIfExists(cssPath);
  }

  return {
    success: errors.length === 0,
    mode: 'preflight',
    errors,
    warnings,
    evidence,
    checkedAt: new Date().toISOString(),
    designDir,
    summaryPath: normalizeRelPath(path.join(designDir, 'runtime-orchestration-summary.json')),
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.errors.length > 0) {
    const result = { success: false, errors: args.errors, warnings: [] };
    console.error(JSON.stringify(result, null, 2));
    process.exit(1);
  }

  const summaryPath = path.join(args.designDir, 'runtime-orchestration-summary.json');
  if (!fs.existsSync(summaryPath)) {
    const result = { success: false, errors: [`runtime-orchestration-summary.json not found: ${summaryPath}`], warnings: [] };
    console.error(JSON.stringify(result, null, 2));
    process.exit(1);
  }

  const summary = readJson(summaryPath);
  const initialFixPlan = buildSafeFixPlan(summary);
  const { changed: safeFixesChanged, appliedFixes } = args.applySafeFixes
    ? applySafeFixPlan(summary, initialFixPlan)
    : { changed: false, appliedFixes: [] };
  if (safeFixesChanged) writeJson(summaryPath, summary);

  const report = validateRestoreContract(args.designDir, summary);
  report.fixPlan = buildSafeFixPlan(summary);
  report.appliedFixes = appliedFixes;
  const reportPath = path.resolve(args.reportJson || path.join(args.designDir, 'restore-contract-report.json'));
  writeJson(reportPath, report);

  if (args.json) {
    console.log(JSON.stringify({ ...report, reportPath }, null, 2));
  } else if (report.success) {
    console.log(`[OK] restore contract preflight passed: ${reportPath}`);
    if (appliedFixes.length > 0) console.log(`[OK] applied ${appliedFixes.length} safe restore preflight fix(es)`);
  } else {
    console.error(`[ERROR_CODE] restore_contract_preflight_failed`);
    for (const error of report.errors) console.error(`[ERROR] ${error}`);
    for (const warning of report.warnings) console.error(`[WARN] ${warning}`);
    if (report.fixPlan.length > 0) {
      console.error('Fix plan:');
      for (const fix of report.fixPlan) {
        console.error(`  ${fix.safe ? 'safe' : 'manual'} ${fix.field}: ${fix.action}`);
      }
    }
    console.error(`Report: ${reportPath}`);
  }

  process.exit(report.success ? 0 : 1);
}

main();
