#!/usr/bin/env node

/**
 * Safely record Page Sub-Agent dispatch completion evidence.
 *
 * This script only writes process-owned fields in runtime-orchestration-summary.json:
 * - project.expectedDispatches[]
 * - project.mainAgentPostDispatchMutations[]
 *
 * It does not modify HTML, assets, .design, restore facts, restore checkpoints,
 * visual diff evidence, validation history, or repair ledger state.
 *
 * Usage:
 *   node record-dispatch-completion.mjs <design-project-path> \
 *     --node-id=page-index \
 *     --status=completed \
 *     --changed-files=pages/index.html \
 *     --trace-digest=<trace-digest> \
 *     --tool-ledger-json='{"todoWriteCalls":0,"previewCalls":0,"validationScriptCalls":0,"helperScriptWrites":0}'
 */

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

function parseArgs(argv) {
  const positional = [];
  const errors = [];
  const mainAgentMutations = [];
  let nodeId = null;
  let htmlSrc = null;
  let status = 'completed';
  let changedFiles = [];
  let traceDigest = null;
  let toolLedgerJson = null;
  let json = false;

  for (const arg of argv) {
    if (arg.startsWith('--node-id=')) {
      nodeId = arg.slice('--node-id='.length);
    } else if (arg.startsWith('--html-src=')) {
      htmlSrc = arg.slice('--html-src='.length);
    } else if (arg.startsWith('--status=')) {
      status = arg.slice('--status='.length);
    } else if (arg.startsWith('--changed-files=')) {
      changedFiles = arg.slice('--changed-files='.length)
        .split(',')
        .map(item => item.trim())
        .filter(Boolean);
    } else if (arg.startsWith('--trace-digest=')) {
      traceDigest = arg.slice('--trace-digest='.length);
    } else if (arg.startsWith('--tool-ledger-json=')) {
      toolLedgerJson = arg.slice('--tool-ledger-json='.length);
    } else if (arg.startsWith('--main-agent-mutation=')) {
      mainAgentMutations.push(arg.slice('--main-agent-mutation='.length));
    } else if (arg === '--json') {
      json = true;
    } else if (arg.startsWith('--')) {
      errors.push(`Unknown flag: ${arg}`);
    } else {
      positional.push(arg);
    }
  }

  if (!positional[0]) errors.push('Missing design project path');
  if (!nodeId && !htmlSrc) errors.push('Missing --node-id=<page-id> or --html-src=<path>');
  if (!['completed', 'not_required'].includes(status)) errors.push(`Unsupported --status=${status}`);
  if (status === 'completed' && changedFiles.length === 0) errors.push('--changed-files is required when --status=completed');
  if (status === 'completed' && !traceDigest) errors.push('--trace-digest is required when --status=completed');
  if (status === 'completed' && !toolLedgerJson) errors.push('--tool-ledger-json is required when --status=completed');

  return {
    designDir: positional[0] ? path.resolve(positional[0]) : null,
    nodeId,
    htmlSrc,
    status,
    changedFiles,
    traceDigest,
    toolLedgerJson,
    mainAgentMutations,
    json,
    errors,
  };
}

function normalizeRelPath(value) {
  const raw = String(value || '').trim().replace(/\\/g, '/').replace(/^(?:\.\/)+/, '');
  if (!raw || path.posix.isAbsolute(raw) || /^[a-zA-Z]:\//.test(raw)) return null;
  if (raw.split('/').includes('..')) return null;
  const normalized = path.posix.normalize(raw);
  return normalized === '.' ? null : normalized;
}

function pathIsValidatorOwned(relPath) {
  const normalized = normalizeRelPath(relPath);
  return [
    'validation-report.json',
    'finish-readiness-report.json',
    'restore-contract-report.json',
    'page-generation-summary.json',
    'validation-run-ledger.json',
  ].includes(normalized);
}

function pathEscapesDesignDir(designDir, relPath) {
  const normalized = normalizeRelPath(relPath);
  if (!normalized || path.isAbsolute(normalized)) return true;
  const resolved = path.resolve(designDir, normalized);
  const rel = path.relative(path.resolve(designDir), resolved);
  return !rel || rel.startsWith('..') || path.isAbsolute(rel);
}

function pathIsAllowedForDispatch(relPath, allowed) {
  const normalized = normalizeRelPath(relPath);
  if (allowed.has(normalized)) return true;
  for (const allowedPath of allowed) {
    if (allowedPath.endsWith('/') && normalized.startsWith(allowedPath)) return true;
  }
  return false;
}

function collectDesignRegistrationsFromValue(value, sourceFile, out = []) {
  if (!value || typeof value !== 'object') return out;
  if (Array.isArray(value)) {
    for (const item of value) collectDesignRegistrationsFromValue(item, sourceFile, out);
    return out;
  }

  const nodeId = normalizeRelPath(value.nodeId || value.id);
  const htmlSrc = normalizeRelPath(value.htmlSrc || value.devMetadata?.htmlSrc);
  if (nodeId || htmlSrc) {
    out.push({ nodeId, htmlSrc, sourceFile });
  }

  for (const child of Object.values(value)) {
    if (child && typeof child === 'object') {
      collectDesignRegistrationsFromValue(child, sourceFile, out);
    }
  }
  return out;
}

function readDesignRegistrations(designDir) {
  const registrations = [];
  for (const entry of fs.readdirSync(designDir, { withFileTypes: true })) {
    if (!entry.isFile() || !entry.name.endsWith('.design')) continue;
    const filePath = path.join(designDir, entry.name);
    let parsed = null;
    try {
      parsed = readJson(filePath);
    } catch (error) {
      throw new Error(`${entry.name} is not valid JSON: ${error.message}`);
    }
    collectDesignRegistrationsFromValue(parsed?.data ?? parsed, entry.name, registrations);
  }
  return registrations;
}

function validateDesignRegistration(designDir, manifestEntry) {
  const nodeId = normalizeRelPath(manifestEntry?.nodeId);
  const htmlSrc = normalizeRelPath(manifestEntry?.htmlSrc);
  const registrations = readDesignRegistrations(designDir);
  if (registrations.length === 0) {
    throw new Error('no .design page registrations found; dispatch completion must match a canvas node');
  }
  const nodeMatches = registrations.filter(item => item.nodeId === nodeId);
  if (nodeMatches.length === 0) {
    throw new Error(`dispatch nodeId is not registered in .design: ${nodeId || '(missing)'}`);
  }
  if (htmlSrc && !nodeMatches.some(item => item.htmlSrc === htmlSrc)) {
    const observed = nodeMatches.map(item => `${item.sourceFile}:${item.htmlSrc || '(missing htmlSrc)'}`).join(', ');
    throw new Error(`dispatch htmlSrc does not match .design registration for ${nodeId}: expected ${htmlSrc}; observed ${observed}`);
  }
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, value) {
  const serialized = `${JSON.stringify(value, null, 2)}\n`;
  JSON.parse(serialized);
  fs.writeFileSync(filePath, serialized, 'utf8');
}

function sha256Text(text) {
  return crypto.createHash('sha256').update(text).digest('hex');
}

function reportError(errors, json = false) {
  const result = { success: false, errors };
  const output = JSON.stringify(result, null, 2);
  if (json) console.log(output);
  else console.error(output);
  process.exit(1);
}

function parseJsonValueOrFile(designDir, rawValue, label) {
  const raw = String(rawValue || '').trim();
  if (!raw) throw new Error(`${label} is empty`);
  const maybePath = path.isAbsolute(raw) ? raw : path.resolve(designDir, raw);
  const source = fs.existsSync(maybePath) && fs.statSync(maybePath).isFile()
    ? fs.readFileSync(maybePath, 'utf8')
    : raw;
  try {
    return JSON.parse(source);
  } catch (error) {
    throw new Error(`${label} is not valid JSON: ${error.message}`);
  }
}

function traceDigestIsPlaceholder(value) {
  const text = String(value || '').trim();
  if (!text) return true;
  if (/^<.*>$/.test(text)) return true;
  if (/todo|unknown|placeholder|trace-hash|sub-agent-run-trace-hash/i.test(text)) return true;
  return text.length < 8;
}

function normalizeToolLedger(rawLedger, traceDigest) {
  if (!rawLedger || typeof rawLedger !== 'object' || Array.isArray(rawLedger)) {
    throw new Error('tool ledger must be a JSON object');
  }
  const source = String(rawLedger.source || '').trim();
  if (source && source !== 'main-agent-runtime-trace') {
    throw new Error(`toolLedger.source must be main-agent-runtime-trace when provided; found ${source}`);
  }
  const numericField = field => {
    const value = Number(rawLedger[field] ?? 0);
    if (!Number.isFinite(value) || value < 0) {
      throw new Error(`toolLedger.${field} must be a non-negative number`);
    }
    return value;
  };
  return {
    source: 'main-agent-runtime-trace',
    traceDigest,
    todoWriteCalls: numericField('todoWriteCalls'),
    previewCalls: numericField('previewCalls'),
    validationScriptCalls: numericField('validationScriptCalls'),
    helperScriptWrites: numericField('helperScriptWrites'),
  };
}

function parseMutation(raw) {
  const text = String(raw || '').trim();
  const separatorIndex = text.indexOf(':');
  if (separatorIndex <= 0) {
    throw new Error(`--main-agent-mutation must use <path>:<reason>; got ${text || '(empty)'}`);
  }
  const relPath = normalizeRelPath(text.slice(0, separatorIndex));
  const reason = text.slice(separatorIndex + 1).trim();
  if (!relPath || !reason) {
    throw new Error(`--main-agent-mutation must include both path and reason; got ${text}`);
  }
  return { path: relPath, reason };
}

function findManifestEntry(summary, args) {
  const manifest = Array.isArray(summary?.project?.dispatchPreflightManifest)
    ? summary.project.dispatchPreflightManifest
    : [];
  return manifest.find(entry =>
    (args.nodeId && (entry?.nodeId === args.nodeId || entry?.pageId === args.nodeId || entry?.targetPageId === args.nodeId)) ||
    (args.htmlSrc && normalizeRelPath(entry?.htmlSrc) === normalizeRelPath(args.htmlSrc))
  );
}

function validateChangedFiles(designDir, manifestEntry, changedFiles) {
  const allowed = new Set((Array.isArray(manifestEntry?.allowedWritePaths) ? manifestEntry.allowedWritePaths : [])
    .map(normalizeRelPath)
    .filter(Boolean));
  if (allowed.size === 0) {
    throw new Error('matching dispatchPreflightManifest row has no allowedWritePaths[]');
  }

  const normalized = changedFiles.map(normalizeRelPath).filter(Boolean);
  if (normalized.length !== changedFiles.length) {
    throw new Error('changedFiles[] contains an invalid or traversing path');
  }
  for (const relPath of normalized) {
    if (pathEscapesDesignDir(designDir, relPath)) {
      throw new Error(`changed file escapes design project: ${relPath}`);
    }
    if (pathIsValidatorOwned(relPath)) {
      throw new Error(`validator-owned report file cannot be recorded as changedFiles[]: ${relPath}`);
    }
    if (!pathIsAllowedForDispatch(relPath, allowed)) {
      throw new Error(`changed file outside allowedWritePaths[]: ${relPath}`);
    }
  }
  return normalized;
}

function upsertExpectedDispatch(summary, entry, payload) {
  if (!Array.isArray(summary.project.expectedDispatches)) summary.project.expectedDispatches = [];
  const index = summary.project.expectedDispatches.findIndex(item =>
    item && typeof item === 'object' && !Array.isArray(item) && (
      item.nodeId === entry.nodeId ||
      item.pageId === entry.nodeId ||
      item.targetPageId === entry.nodeId ||
      normalizeRelPath(item.htmlSrc) === normalizeRelPath(entry.htmlSrc)
    )
  );
  if (index >= 0) summary.project.expectedDispatches[index] = payload;
  else summary.project.expectedDispatches.push(payload);
}

function appendMainAgentMutations(summary, mutations, recordedAt) {
  if (!Array.isArray(summary.project.mainAgentPostDispatchMutations)) {
    summary.project.mainAgentPostDispatchMutations = [];
  }
  for (const mutation of mutations) {
    const duplicate = summary.project.mainAgentPostDispatchMutations.some(item =>
      item && typeof item === 'object' &&
      normalizeRelPath(item.path || item.file || item.relPath) === mutation.path &&
      String(item.reason || '').trim() === mutation.reason
    );
    if (duplicate) continue;
    summary.project.mainAgentPostDispatchMutations.push({
      path: mutation.path,
      reason: mutation.reason,
      owner: 'main-agent',
      recordedAt,
      source: 'record-dispatch-completion.mjs',
    });
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.errors.length > 0) reportError(args.errors, args.json);

  if (args.traceDigest && traceDigestIsPlaceholder(args.traceDigest)) {
    reportError([`--trace-digest is empty, placeholder, or too short: ${args.traceDigest}`], args.json);
  }

  const summaryPath = path.join(args.designDir, 'runtime-orchestration-summary.json');
  if (!fs.existsSync(summaryPath)) {
    reportError([`runtime-orchestration-summary.json not found: ${summaryPath}`], args.json);
  }

  let summary;
  try {
    summary = readJson(summaryPath);
  } catch (error) {
    reportError([`runtime-orchestration-summary.json is not valid JSON: ${error.message}`], args.json);
  }
  if (!summary.project || typeof summary.project !== 'object') summary.project = {};

  const entry = findManifestEntry(summary, args);
  if (!entry) {
    reportError([`matching dispatchPreflightManifest row not found for ${args.nodeId || args.htmlSrc}`], args.json);
  }
  try {
    validateDesignRegistration(args.designDir, entry);
  } catch (error) {
    reportError([error.message], args.json);
  }

  let toolLedger = null;
  let changedFiles = [];
  if (args.status === 'completed') {
    try {
      const rawLedger = parseJsonValueOrFile(args.designDir, args.toolLedgerJson, '--tool-ledger-json');
      toolLedger = normalizeToolLedger(rawLedger, args.traceDigest);
      changedFiles = validateChangedFiles(args.designDir, entry, args.changedFiles);
    } catch (error) {
      reportError([error.message], args.json);
    }
  }

  let mutations = [];
  try {
    mutations = args.mainAgentMutations.map(parseMutation);
    for (const mutation of mutations) {
      if (pathEscapesDesignDir(args.designDir, mutation.path)) {
        throw new Error(`main-agent mutation path escapes design project: ${mutation.path}`);
      }
      if (pathIsValidatorOwned(mutation.path)) {
        throw new Error(`validator-owned report file cannot be recorded as mainAgentPostDispatchMutations[]: ${mutation.path}`);
      }
    }
  } catch (error) {
    reportError([error.message], args.json);
  }

  const recordedAt = new Date().toISOString();
  const payload = {
    nodeId: entry.nodeId,
    pageId: entry.nodeId,
    targetPageId: entry.nodeId,
    htmlSrc: entry.htmlSrc,
    packetType: entry.packetType,
    status: args.status,
    changedFiles,
    toolCallLedger: toolLedger,
    recordedAt,
    source: 'record-dispatch-completion.mjs',
  };
  if (args.status === 'not_required') {
    payload.changedFiles = [];
    payload.toolCallLedger = {
      source: 'main-agent-runtime-trace',
      traceDigest: args.traceDigest || sha256Text(`${entry.nodeId}:${recordedAt}:not_required`),
      todoWriteCalls: 0,
      previewCalls: 0,
      validationScriptCalls: 0,
      helperScriptWrites: 0,
    };
  }

  upsertExpectedDispatch(summary, entry, payload);
  appendMainAgentMutations(summary, mutations, recordedAt);
  writeJson(summaryPath, summary);

  const result = {
    success: true,
    summaryPath,
    nodeId: entry.nodeId,
    htmlSrc: entry.htmlSrc,
    status: args.status,
    changedFiles,
    changedPaths: [
      'project.expectedDispatches',
      ...(mutations.length > 0 ? ['project.mainAgentPostDispatchMutations'] : []),
    ],
    summaryHash: crypto.createHash('sha256').update(fs.readFileSync(summaryPath)).digest('hex'),
    nextCheck: {
      type: 'dispatch-discipline',
      fullValidationAllowed: false,
    },
  };

  if (args.json) console.log(JSON.stringify(result, null, 2));
  else console.log(`[OK] dispatch completion recorded for ${entry.nodeId || entry.htmlSrc}`);
}

main();
