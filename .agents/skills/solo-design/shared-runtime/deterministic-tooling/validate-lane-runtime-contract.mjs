#!/usr/bin/env node

/**
 * Validate lane runtime contract fields in runtime-orchestration-summary.json.
 *
 * Usage:
 *   node validate-lane-runtime-contract.mjs <design-project-path> --mode=auto|free-fast|complex|restore|library-bound|graphic-bitmap|graphic-layout-static|existing-edit|redesign|variants|theme-customize|image-asset-append
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const MODE_TO_LANE = new Map([
  ['free-fast', 'free_exploration'],
  ['complex', 'complex_html_page'],
  ['restore', 'restore_1to1'],
  ['library-bound', 'library_bound'],
  ['graphic-bitmap', 'graphic_bitmap_first'],
  ['graphic-layout-static', 'graphic_layout_static'],
  ['existing-edit', 'existing_edit_add_comparison'],
  ['redesign', 'redesign_duplicate_project'],
  ['variants', 'variants_multi_scheme'],
  ['theme-customize', 'theme_customize'],
  ['image-asset-append', 'image_asset_append'],
]);

const SUPPORTED_MODES = new Set(['auto', ...MODE_TO_LANE.keys()]);
const PAGE_DISPATCH_LANES = new Set([
  'free_exploration',
  'restore_1to1',
  'library_bound',
  'graphic_layout_static',
  'complex_html_page',
  'existing_edit_add_comparison',
  'redesign_duplicate_project',
  'variants_multi_scheme',
]);
const QUALITY_EFFICIENCY_GATE_VERSION = '2026.07.10.0';
const GENERALIZED_FLOW_CONTROL_VERSION = '2026.07.11.0';
const RESTORE_EVIDENCE_SKIP_VERSION = '2026.07.16.21';

function parseArgs(argv) {
  const positional = [];
  let mode = 'auto';
  const errors = [];

  for (const arg of argv) {
    if (arg.startsWith('--mode=')) {
      mode = arg.slice('--mode='.length);
    } else if (arg.startsWith('--')) {
      errors.push(`Unknown flag: ${arg}`);
    } else {
      positional.push(arg);
    }
  }

  if (!SUPPORTED_MODES.has(mode)) errors.push(`Unsupported mode: ${mode}`);
  if (!positional[0]) errors.push('Missing design project path');
  return { designDir: positional[0], mode, errors };
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
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

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function asNonEmptyArray(value) {
  return Array.isArray(value) && value.length > 0;
}

function inferLane(summary, mode) {
  if (mode !== 'auto') return MODE_TO_LANE.get(mode);

  const project = summary.project || {};
  const intent = project.intentProfile || {};
  if (intent.caseFamily === 'restore_1to1' || project.replicationMode === 'high-fidelity') return 'restore_1to1';
  if (project.operatingMode === 'library-bound' || summary.designSource?.libraryIdentity || project.libraryIdentity) return 'library_bound';
  if (project.graphicStrategyGate === 'bitmap-first' && project.layoutStaticRequired !== true) return 'graphic_bitmap_first';
  if (project.graphicStrategyGate === 'layout-static' || project.layoutStaticRequired === true) return 'graphic_layout_static';
  if (project.duplicateProjectPath) return 'redesign_duplicate_project';
  if (project.variantAxis || project.expectedCount) return 'variants_multi_scheme';
  if (project.changedDimensions || project.noNewPageAssertion === true) return 'theme_customize';
  if (project.appendMode === true || project.imageAssetAppend === true) return 'image_asset_append';
  if (project.sourcePageId || project.derivationType || project.inPlaceEditAllowed !== undefined) return 'existing_edit_add_comparison';
  if (project.generationTree || project.graphicStrategyGate === 'page') return 'complex_html_page';
  return 'free_exploration';
}

function normalizeRelPath(value) {
  if (typeof value !== 'string' || !value.trim()) return null;
  const raw = value.trim().replace(/\\/g, '/').replace(/^(?:\.\/)+/, '');
  if (path.posix.isAbsolute(raw) || /^[a-zA-Z]:\//.test(raw)) return null;
  if (raw.split('/').includes('..')) return null;
  const normalized = path.posix.normalize(raw);
  return normalized === '.' ? null : normalized;
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
    graphic_bitmap_first: 'intent-workflows/intent-graphic-asset-generation/INTENT_WORKFLOW.md',
    theme_customize: 'intent-workflows/intent-project-mutation/INTENT_WORKFLOW.md',
    image_asset_append: 'intent-workflows/intent-graphic-asset-generation/INTENT_WORKFLOW.md',
  }[lane] || 'intent-workflows/intent-page-free-exploration/INTENT_WORKFLOW.md';
}

function parseContextRequirements(lane) {
  const relPath = workflowFileFor(lane);
  const skillDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
  const filePath = path.join(skillDir, relPath);
  if (!fs.existsSync(filePath)) return { required: [], optional: [], errors: [`workflow file not found: ${relPath}`] };
  const content = fs.readFileSync(filePath, 'utf8');
  const section = content.match(/## Context Requirements\s*\n([\s\S]*?)(?:\n## |\n# |$)/);
  if (!section) return { required: [], optional: [], errors: [`Context Requirements section not found in ${relPath}`] };
  const required = [];
  const optional = [];
  for (const line of section[1].split('\n')) {
    const match = line.match(/-\s+`([^`]+)`(.*)$/);
    if (!match) continue;
    const item = { path: normalizeRelPath(match[1]), qualifier: match[2]?.trim() || '' };
    if (!item.path) continue;
    if (/\b(conditionally|fallback|optional)\b/i.test(item.qualifier)) optional.push(item);
    else required.push(item);
  }
  return { required, optional, errors: [] };
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

function validateContextRequirements(project, lane, collector, activeFlowControl) {
  const requirements = parseContextRequirements(lane);
  for (const error of requirements.errors) collector.block(`context preflight: ${error}`);
  const loaded = Array.isArray(project.contextRequirementsLoaded) ? project.contextRequirementsLoaded : [];
  const loadedByPath = new Map();
  for (const item of loaded) {
    const relPath = contextLoadedPath(item);
    if (relPath) loadedByPath.set(relPath, item);
  }
  for (const requirement of requirements.required) {
    const item = loadedByPath.get(requirement.path);
    collector.require(Boolean(item), `missing required context read before dispatch: ${requirement.path}`, activeFlowControl);
    if (item && activeFlowControl) {
      collector.require(
        contextLoadIsBodyRead(item),
        `contextRequirementsLoaded entry for ${requirement.path} must record bodyRead=true or readStatus="loaded"`
      );
    }
  }
}

function makeCollector(activeContract) {
  const blockingIssues = [];
  const warnings = [];
  return {
    require(condition, message, gated = true) {
      if (condition) return;
      if (gated && !activeContract) warnings.push(message);
      else blockingIssues.push(message);
    },
    warn(message) {
      warnings.push(message);
    },
    block(message) {
      blockingIssues.push(message);
    },
    blockingIssues,
    warnings,
  };
}

function validate(summary, mode) {
  const project = summary.project || {};
  const designSource = summary.designSource || {};
  const lane = inferLane(summary, mode);
  const activeContract = isLaneIsolationContractActive(summary);
  const activeQualityContract = isQualityEfficiencyContractActive(summary);
  const activeFlowControl = isGeneralizedFlowControlActive(summary);
  const collector = makeCollector(activeContract);

  if (project.resolvedLane && project.resolvedLane !== lane) {
    collector.block(`resolvedLane mismatch: expected ${lane}, found ${project.resolvedLane}`);
  }
  collector.require(Boolean(project.resolvedLane), 'missing project.resolvedLane');
  collector.require(isObject(project.intentProfile) || lane === 'theme_customize', 'missing project.intentProfile');
  collector.require(project.selectedIntentWorkflowRead === true, 'missing project.selectedIntentWorkflowRead=true');
  collector.require(Array.isArray(project.contextRequirementsLoaded) && project.contextRequirementsLoaded.length > 0, 'missing project.contextRequirementsLoaded[]');
  collector.require(
    Boolean(project.contextReadScope || project.readScopeLedger),
    'missing context read scope evidence'
  );
  validateContextRequirements(project, lane, collector, activeFlowControl);

  if (PAGE_DISPATCH_LANES.has(lane)) {
    collector.require(Array.isArray(project.dispatchPreflightManifest), 'missing dispatchPreflightManifest[] for page-dispatch lane');
    validateExpectedDispatches(project, collector, activeContract);
    validateDispatchOwnership(project, collector, activeFlowControl);
  } else {
    collector.require(!Array.isArray(project.dispatchPreflightManifest) || project.dispatchPreflightManifest.length === 0, `${lane} must not write page dispatch manifest`);
    if (Array.isArray(project.expectedDispatches) && project.expectedDispatches.length > 0) {
      collector.warn(`${lane} should not write expectedDispatches[] unless explicitly converted into a page-dispatch lane`);
    }
  }

  if (lane === 'restore_1to1') {
    const sourceType = String(
      project.sourceType ||
      project.intentProfile?.sourceType ||
      project.referenceCaptureEvidence?.sourceType ||
      ''
    ).trim();
    const facts = Array.isArray(project.measuredSourceFacts)
      ? project.measuredSourceFacts
      : (Array.isArray(project.restorationContractLite?.measuredSourceFacts)
        ? project.restorationContractLite.measuredSourceFacts
        : []);
    const checkpoints = Array.isArray(project.restoreVisualCheckpoints) ? project.restoreVisualCheckpoints : [];
    const requiredCategories = new Set(['viewport', 'layout-region', 'color-surface', 'component-proportion', 'density-spacing']);

    collector.require(['image', 'url', 'image+url'].includes(sourceType), `restore lane requires valid sourceType (image|url|image+url), found: ${sourceType || '(missing)'}`);
    collector.require(asNonEmptyArray(project.referenceCaptureEvidence) || isObject(project.referenceCaptureEvidence), 'restore lane requires referenceCaptureEvidence');
    collector.require(Array.isArray(facts) && facts.length >= 8, `restore lane requires >= 8 measuredSourceFacts, found ${facts.length}`);
    const highPriorityFacts = facts.filter(f => f?.priority === 'high');
    collector.require(highPriorityFacts.length >= 5, `restore lane requires >= 5 high priority measuredSourceFacts, found ${highPriorityFacts.length}`);
    collector.require(checkpoints.length >= 8, `restore lane requires >= 8 restoreVisualCheckpoints, found ${checkpoints.length}`);
    const highPriorityCheckpoints = checkpoints.filter(c => c?.priority === 'high');
    collector.require(highPriorityCheckpoints.length >= 5, `restore lane requires >= 5 high priority restoreVisualCheckpoints, found ${highPriorityCheckpoints.length}`);
    const presentCategories = new Set(facts.map(f => String(f?.category || '').trim()).filter(Boolean));
    const missingCategories = [...requiredCategories].filter(c => !presentCategories.has(c));
    collector.require(missingCategories.length === 0, `restore lane measuredSourceFacts missing categories: ${missingCategories.join(', ')}`);
    const usesCurrentRestoreContract = compareVersion(
      summary?.skillProvenance?.version,
      RESTORE_EVIDENCE_SKIP_VERSION
    ) >= 0;
    if (!usesCurrentRestoreContract) {
      collector.require(isObject(project.restoreEvidenceReview), 'restore lane requires restoreEvidenceReview');
      collector.require(isObject(project.visualDiffReview), 'restore lane requires visualDiffReview');
      if (activeQualityContract) {
        collector.require(Array.isArray(project.sourceFactCoverageMap) && project.sourceFactCoverageMap.length > 0, 'restore lane requires sourceFactCoverageMap[]');
      }
    }
    if (activeFlowControl) {
      const lock = project.sourceAuthorityLock;
      collector.require(isObject(lock), 'restore lane requires project.sourceAuthorityLock');
      if (isObject(lock)) {
        collector.require(Boolean(lock.visualAuthority), 'sourceAuthorityLock.visualAuthority is required');
        collector.require(lock.mayOverrideVisualAuthority === false, 'sourceAuthorityLock.mayOverrideVisualAuthority must be false');
        collector.require(lock.lockedBeforeDispatch === true, 'sourceAuthorityLock.lockedBeforeDispatch must be true');
      }
    }
    if (!usesCurrentRestoreContract && activeQualityContract && Array.isArray(project.sourceFactCoverageMap)) {
      for (const [index, row] of project.sourceFactCoverageMap.entries()) {
        collector.require(Boolean(row?.sourceFactId), `sourceFactCoverageMap[${index}] requires sourceFactId`);
        collector.require(Boolean(row?.checkpointId), `sourceFactCoverageMap[${index}] requires checkpointId`);
        collector.require(Boolean(row?.selector), `sourceFactCoverageMap[${index}] requires selector`);
        collector.require(Boolean(row?.implementedProperty), `sourceFactCoverageMap[${index}] requires implementedProperty`);
      }
    }
  }

  if (lane === 'library_bound') {
    collector.require(isObject(designSource.libraryIdentity) || isObject(project.libraryIdentity), 'library lane requires library identity');
    collector.require(Boolean(designSource.actualTokenNameReference || project.actualTokenNameReference), 'library lane requires actualTokenNameReference');
  }

  if (lane === 'graphic_bitmap_first') {
    collector.require(project.layoutStaticRequired !== true, 'graphic_bitmap_first must not have layoutStaticRequired=true');
  }

  if (lane === 'graphic_layout_static') {
    collector.require(project.layoutStaticRequired === true, 'graphic_layout_static requires layoutStaticRequired=true');
    collector.require(isObject(project.deliverableCompletenessChecklist), 'graphic_layout_static requires deliverableCompletenessChecklist');
    if (activeQualityContract) {
      const checklist = project.deliverableCompletenessChecklist || {};
      const blocks = Array.isArray(checklist.requiredCopyBlocks) ? checklist.requiredCopyBlocks : [];
      collector.require(blocks.length > 0, 'graphic_layout_static requires deliverableCompletenessChecklist.requiredCopyBlocks[]');
      for (const [index, block] of blocks.entries()) {
        collector.require(block && typeof block === 'object' && !Array.isArray(block), `requiredCopyBlocks[${index}] must be an object`);
        collector.require(Boolean(block?.label), `requiredCopyBlocks[${index}] requires label`);
        collector.require(Boolean(block?.text), `requiredCopyBlocks[${index}] requires text`);
        collector.require(Boolean(block?.htmlSrc), `requiredCopyBlocks[${index}] requires htmlSrc`);
        collector.require(Boolean(block?.selector), `requiredCopyBlocks[${index}] requires selector`);
        collector.require(Boolean(block?.role), `requiredCopyBlocks[${index}] requires role`);
      }
    }
    if (activeFlowControl) {
      validateVisualQualityCheckpoints(project, collector);
    }
  }

  if (lane === 'existing_edit_add_comparison') {
    collector.require(Boolean(project.sourcePageId), 'existing edit requires sourcePageId');
    collector.require(Boolean(project.derivationType), 'existing edit requires derivationType');
    collector.require(typeof project.inPlaceEditAllowed === 'boolean', 'existing edit requires inPlaceEditAllowed boolean');
  }

  if (lane === 'redesign_duplicate_project') {
    collector.require(Boolean(project.duplicateProjectPath), 'redesign requires duplicateProjectPath');
  }

  if (lane === 'variants_multi_scheme') {
    collector.require(Boolean(project.variantAxis), 'variants require variantAxis');
    collector.require(Number.isInteger(project.expectedCount) && project.expectedCount >= 2, 'variants require expectedCount >= 2');
  }

  if (lane === 'theme_customize') {
    collector.require(Boolean(project.changedDimensions), 'theme_customize requires changedDimensions');
    collector.require(Array.isArray(project.affectedPageRefreshList), 'theme_customize requires affectedPageRefreshList[]');
    collector.require(project.noNewPageAssertion === true, 'theme_customize requires noNewPageAssertion=true');
  }

  if (lane === 'image_asset_append') {
    collector.require(Boolean(project.assetInventory || project.imageAssetInventory), 'image_asset_append requires asset inventory');
  }

  if (activeQualityContract && PAGE_DISPATCH_LANES.has(lane)) {
    collector.require(
      isObject(project.validationRunDiscipline),
      'page-dispatch lanes require project.validationRunDiscipline before dispatch'
    );
  }

  if (activeFlowControl && PAGE_DISPATCH_LANES.has(lane)) {
    collector.require(isObject(project.lowValueCallWatchdog), 'page-dispatch lanes require project.lowValueCallWatchdog');
    if (isObject(project.lowValueCallWatchdog)) {
      collector.require(project.lowValueCallWatchdog.applies === true, 'lowValueCallWatchdog.applies must be true');
      collector.require(Boolean(project.lowValueCallWatchdog.noProgressNextAction), 'lowValueCallWatchdog.noProgressNextAction is required');
    }
  }

  return {
    lane,
    success: collector.blockingIssues.length === 0,
    blockingIssues: collector.blockingIssues,
    warnings: collector.warnings,
    proof: {
      mode,
      activeContract,
      resolvedLane: project.resolvedLane || null,
      skillProvenance: summary.skillProvenance || null,
    },
  };
}

function getExpectedDispatchPageId(entry) {
  return entry?.nodeId || entry?.pageId || entry?.targetPageId || null;
}

function getExpectedDispatchChangedFiles(entry) {
  if (Array.isArray(entry?.changedFiles)) return entry.changedFiles;
  if (Array.isArray(entry?.changed_files)) return entry.changed_files;
  return [];
}

function normalizeAllowedWritePaths(entry) {
  const paths = Array.isArray(entry?.allowedWritePaths) ? entry.allowedWritePaths : [];
  return paths.map(normalizeRelPath).filter(Boolean);
}

function dispatchChangedFileAllowed(file, allowedPaths) {
  return allowedPaths.some(allowed => {
    if (file === allowed) return true;
    return allowed.endsWith('/') && file.startsWith(allowed);
  });
}

function validateDispatchOwnership(project, collector, activeFlowControl) {
  const manifest = Array.isArray(project.dispatchPreflightManifest) ? project.dispatchPreflightManifest : [];
  const expected = Array.isArray(project.expectedDispatches) ? project.expectedDispatches : [];
  if (!activeFlowControl) return;
  const manifestByPage = new Map();
  for (const entry of manifest) {
    const pageId = entry?.nodeId || entry?.pageId || entry?.targetPageId;
    if (pageId) manifestByPage.set(pageId, entry);
    collector.require(normalizeAllowedWritePaths(entry).length > 0, `${entry?.htmlSrc || pageId || '<dispatch>'} requires allowedWritePaths[]`);
  }
  const forbidden = [
    '.design',
    'runtime-orchestration-summary.json',
    'validation-report.json',
    'finish-readiness-report.json',
    'page-generation-summary.json',
  ];
  for (const [index, entry] of expected.entries()) {
    const pageId = getExpectedDispatchPageId(entry);
    const manifestEntry = manifestByPage.get(pageId);
    if (!manifestEntry) continue;
    const allowed = normalizeAllowedWritePaths(manifestEntry);
    const rawChanged = getExpectedDispatchChangedFiles(entry);
    const changed = rawChanged.map(normalizeRelPath).filter(Boolean);
    const status = String(entry?.status || 'completed').trim();
    if (status !== 'completed') continue;
    if (changed.length !== rawChanged.length) {
      collector.block(`expectedDispatches[${index}] changedFiles[] contains an invalid or traversing path`);
    }
    collector.require(changed.length > 0, `expectedDispatches[${index}] requires changedFiles[] for ownership proof`);
    for (const file of changed) {
      if (forbidden.some(token => file.endsWith(token) || file.includes(`/${token}`))) {
        collector.block(`expectedDispatches[${index}] changed forbidden Main-Agent-owned file: ${file}`);
      }
      if (!dispatchChangedFileAllowed(file, allowed)) {
        collector.block(`expectedDispatches[${index}] changed file outside allowedWritePaths: ${file}`);
      }
    }
  }
}

function validateVisualQualityCheckpoints(project, collector) {
  const checkpoints = Array.isArray(project.visualQualityCheckpoints) ? project.visualQualityCheckpoints : [];
  collector.require(checkpoints.length >= 4, `graphic/layout lane requires >= 4 visualQualityCheckpoints, found ${checkpoints.length}`);
  const required = new Set(['visual-anchor', 'information-hierarchy', 'composition-structure', 'implementation-strategy']);
  const present = new Set(checkpoints.map(item => String(item?.dimension || '').trim()).filter(Boolean));
  for (const dimension of required) {
    collector.require(present.has(dimension), `visualQualityCheckpoints missing dimension: ${dimension}`);
  }
  for (const [index, item] of checkpoints.entries()) {
    collector.require(Boolean(item?.checkpointId || item?.id), `visualQualityCheckpoints[${index}] requires checkpointId`);
    collector.require(Boolean(item?.expected), `visualQualityCheckpoints[${index}] requires expected`);
    collector.require(Boolean(item?.evidenceTarget), `visualQualityCheckpoints[${index}] requires evidenceTarget`);
  }
}

function validateExpectedDispatches(project, collector, activeContract) {
  const expected = project.expectedDispatches;
  const manifest = project.dispatchPreflightManifest;
  collector.require(Array.isArray(expected), 'missing expectedDispatches[] for page-dispatch lane', activeContract);
  if (!Array.isArray(expected)) return;

  if (Array.isArray(manifest) && expected.length !== manifest.length) {
    collector.block(`expectedDispatches.length (${expected.length}) must equal dispatchPreflightManifest.length (${manifest.length})`);
  }

  for (const [index, entry] of expected.entries()) {
    if (!entry || typeof entry !== 'object') {
      collector.block(`expectedDispatches[${index}] must be an object`);
      continue;
    }
    if (!getExpectedDispatchPageId(entry)) {
      collector.block(`expectedDispatches[${index}] requires nodeId`);
    }
    if (!String(entry.packetType || '').trim()) {
      collector.block(`expectedDispatches[${index}] requires packetType`);
    }
    if (!['completed', 'not_required'].includes(entry.status)) {
      collector.block(`expectedDispatches[${index}].status must be completed or not_required`);
    }
  }
}

function main() {
  const { designDir, mode, errors } = parseArgs(process.argv.slice(2));
  if (errors.length) {
    errors.forEach(error => console.error(`[ERROR] ${error}`));
    process.exit(1);
  }

  try {
    const summaryPath = path.join(path.resolve(designDir), 'runtime-orchestration-summary.json');
    if (!fs.existsSync(summaryPath)) throw new Error(`runtime-orchestration-summary.json not found: ${summaryPath}`);
    const result = validate(readJson(summaryPath), mode);
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
    process.exit(result.success ? 0 : 1);
  } catch (error) {
    console.error(`[ERROR] ${error.message}`);
    process.exit(1);
  }
}

main();
