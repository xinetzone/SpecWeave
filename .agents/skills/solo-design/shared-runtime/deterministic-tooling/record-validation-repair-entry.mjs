#!/usr/bin/env node

/**
 * Record the repair entry that must exist immediately after a failed
 * validate-design-workspace.mjs run and before any repair edits.
 *
 * This script only writes runtime-orchestration-summary.json. It does not
 * repair files, inspect workflow sources, start previews, or create helper
 * scripts.
 *
 * Usage:
 *   node record-validation-repair-entry.mjs <design-project-path> --phase=start --failed-report=<design-project-path>/validation-report.json
 *   node record-validation-repair-entry.mjs <design-project-path> --phase=action --failed-report=<design-project-path>/validation-report.json --owner=main-agent --error-class=head-infrastructure --action=run_apply_html_head_replace_once --affected-files=pages/index.html
 *   node record-validation-repair-entry.mjs <design-project-path> --phase=revalidate --revalidation-report=<design-project-path>/validation-report.json
 */

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

function parseArgs(argv) {
  const positional = [];
  const errors = [];
  let phase = 'start';
  let failedReport = null;
  let revalidationReport = null;
  let owner = null;
  let errorClass = null;
  let action = null;
  let affectedFiles = [];
  let preEditFileHashes = [];
  let postEditFileHashes = [];
  let repairOwnedFields = [];
  let blockedReason = null;
  let json = false;

  for (const arg of argv) {
    if (arg.startsWith('--phase=')) {
      phase = arg.slice('--phase='.length);
    } else if (arg.startsWith('--failed-report=')) {
      failedReport = arg.slice('--failed-report='.length);
    } else if (arg.startsWith('--revalidation-report=')) {
      revalidationReport = arg.slice('--revalidation-report='.length);
    } else if (arg.startsWith('--owner=')) {
      owner = arg.slice('--owner='.length);
    } else if (arg.startsWith('--error-class=')) {
      errorClass = arg.slice('--error-class='.length);
    } else if (arg.startsWith('--action=')) {
      action = arg.slice('--action='.length);
    } else if (arg.startsWith('--affected-files=')) {
      affectedFiles = arg.slice('--affected-files='.length)
        .split(',')
        .map(item => item.trim())
        .filter(Boolean);
    } else if (arg.startsWith('--pre-edit-file-hash=')) {
      preEditFileHashes = arg.slice('--pre-edit-file-hash='.length)
        .split(',')
        .map(item => item.trim())
        .filter(Boolean);
    } else if (arg.startsWith('--post-edit-file-hash=')) {
      postEditFileHashes = arg.slice('--post-edit-file-hash='.length)
        .split(',')
        .map(item => item.trim())
        .filter(Boolean);
    } else if (arg.startsWith('--repair-owned-fields=')) {
      repairOwnedFields = arg.slice('--repair-owned-fields='.length)
        .split(',')
        .map(item => item.trim())
        .filter(Boolean);
    } else if (arg.startsWith('--blocked-reason=')) {
      blockedReason = arg.slice('--blocked-reason='.length);
    } else if (arg === '--json') {
      json = true;
    } else if (arg.startsWith('--')) {
      errors.push(`Unknown flag: ${arg}`);
    } else {
      positional.push(arg);
    }
  }

  if (!positional[0]) errors.push('Missing design project path');
  if (!['start', 'action', 'revalidate'].includes(phase)) errors.push(`Unsupported --phase=${phase}`);
  if (phase === 'start' && !failedReport) errors.push('Missing --failed-report=<path>');
  if (phase === 'action' && !action && !blockedReason) errors.push('Missing --action=<repair-action> or --blocked-reason=<reason>');
  if (phase === 'revalidate' && !revalidationReport) errors.push('Missing --revalidation-report=<path>');

  return {
    designDir: positional[0] ? path.resolve(positional[0]) : null,
    phase,
    failedReport,
    revalidationReport,
    owner,
    errorClass,
    action,
    affectedFiles,
    preEditFileHashes,
    postEditFileHashes,
    repairOwnedFields,
    blockedReason,
    json,
    errors,
  };
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, value) {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

function relPath(designDir, filePath) {
  const resolved = path.resolve(filePath);
  const rel = path.relative(designDir, resolved).replace(/\\/g, '/');
  return rel && !rel.startsWith('..') && !path.isAbsolute(rel) ? rel : resolved;
}

function assertInsideDesignDir(designDir, filePath, label) {
  const designRoot = path.resolve(designDir);
  const resolved = path.resolve(filePath);
  const rel = path.relative(designRoot, resolved);
  if (!rel || rel.startsWith('..') || path.isAbsolute(rel)) {
    reportError([`${label} escapes design project: ${filePath}`]);
  }
  return resolved;
}

function resolveInputPath(designDir, filePath) {
  const raw = String(filePath || '').trim();
  if (!raw) return null;
  return path.isAbsolute(raw) ? raw : path.resolve(designDir, raw);
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

function ensureProjectArrays(summary) {
  if (!summary.project || typeof summary.project !== 'object') summary.project = {};
  if (!Array.isArray(summary.project.validationHistory)) summary.project.validationHistory = [];
  if (!Array.isArray(summary.project.validationRepairLedger)) summary.project.validationRepairLedger = [];
  if (!Array.isArray(summary.project.repairEntryEvidence)) summary.project.repairEntryEvidence = [];
}

function isRepairLedgerOnlyReport(report) {
  const errors = Array.isArray(report?.errors)
    ? report.errors
    : (Array.isArray(report?.renderBlockingErrors) ? report.renderBlockingErrors : []);
  if (errors.length === 0) return false;
  return errors.every(error => /\[?repair-ledger\]?|repair ledger|validationRepairLedger|repairEntryEvidence/i.test(String(error)));
}

function ensureLedgerDiagnosticReports(summary) {
  if (!summary.project || typeof summary.project !== 'object') summary.project = {};
  if (!Array.isArray(summary.project.ledgerDiagnosticReports)) summary.project.ledgerDiagnosticReports = [];
}

function recordLedgerDiagnosticReport(summary, reportRel, report, reportHash, blockedReason) {
  ensureLedgerDiagnosticReports(summary);
  const payload = {
    reportPath: reportRel,
    reportHash,
    checkedAt: report.checkedAt || new Date().toISOString(),
    success: report.success === true,
    exitCode: report.success === true ? 0 : 1,
    diagnosticOnly: true,
    diagnosticClass: 'repair-ledger',
    blockedReason: blockedReason || null,
  };
  const existing = summary.project.ledgerDiagnosticReports.find(item => item && item.reportHash === reportHash);
  if (existing) Object.assign(existing, payload);
  else summary.project.ledgerDiagnosticReports.push(payload);
  summary.project.ledgerDiagnosticReports = summary.project.ledgerDiagnosticReports.slice(-3);
}

function reportError(errors) {
  const result = { success: false, errors };
  console.error(JSON.stringify(result, null, 2));
  process.exit(1);
}

function inferOwnerTriage(report) {
  const hints = Array.isArray(report?.repairPlanHints) ? report.repairPlanHints : [];
  if (hints.length > 0) {
    return hints.map((hint, index) => ({
      owner: hint.owner || 'main-agent',
      errorClass: hint.errorClass || hint.repairScope || `repair-hint-${index + 1}`,
      affectedFiles: Array.isArray(hint.affectedFiles) ? hint.affectedFiles : [],
      repairScope: hint.repairScope || null,
      strategy: hint.strategy || null,
    }));
  }

  const actionTable = Array.isArray(report?.repairActionTable) ? report.repairActionTable : [];
  if (actionTable.length > 0) {
    return actionTable.slice(0, 8).map(item => ({
      owner: item.owner || 'main-agent',
      errorClass: item.errorClass || 'validation-error',
      affectedFiles: [],
      repairScope: item.action || null,
      strategy: item.sourceReadPolicy || null,
    }));
  }

  const errors = Array.isArray(report?.errors)
    ? report.errors
    : (Array.isArray(report?.renderBlockingErrors) ? report.renderBlockingErrors : []);
  return errors.slice(0, 8).map((error, index) => ({
    owner: 'main-agent',
    errorClass: `validation-error-${index + 1}`,
    affectedFiles: [],
    repairScope: String(error).slice(0, 160),
    strategy: 'classify-owner-then-batch-repair',
  }));
}

function ensureValidationHistory(summary, reportRel, report, reportHash) {
  const project = summary.project || {};
  if (!Array.isArray(project.validationHistory)) project.validationHistory = [];
  const existing = project.validationHistory.find(item => item && item.reportHash === reportHash);
  const next = {
    reportPath: reportRel,
    reportHash,
    checkedAt: report.checkedAt || new Date().toISOString(),
    success: report.success === true,
    exitCode: report.success === true ? 0 : 1,
    renderBlockingErrorCount: Number.isInteger(report.renderBlockingErrorCount)
      ? report.renderBlockingErrorCount
      : (Array.isArray(report.errors) ? report.errors.length : null),
    repairPlanHints: Array.isArray(report.repairPlanHints)
      ? report.repairPlanHints.map(hint => hint.errorClass || hint.repairScope || hint.strategy).filter(Boolean)
      : [],
    errorSignatures: Array.isArray(report.errorSignatures)
      ? report.errorSignatures
      : [],
    terminalState: report.terminalState || null,
  };
  if (existing) {
    Object.assign(existing, next);
  } else {
    project.validationHistory.push(next);
  }
  summary.project = project;
}

function findLedger(summary, failedReportRel, failedReportHash = null) {
  const ledger = summary.project.validationRepairLedger;
  if (failedReportRel && failedReportHash) {
    const exact = ledger.find(item => item && item.failedReportPath === failedReportRel && item.failedReportHash === failedReportHash);
    if (exact) return exact;
    const openSamePath = ledger.filter(item => item && item.failedReportPath === failedReportRel && !item.revalidationReportPath);
    if (openSamePath.length > 0) return openSamePath[openSamePath.length - 1];
    return null;
  }
  if (failedReportRel) {
    const openSamePath = ledger.filter(item => item && item.failedReportPath === failedReportRel && !item.revalidationReportPath);
    if (openSamePath.length > 0) return openSamePath[openSamePath.length - 1];
    return ledger.find(item => item && item.failedReportPath === failedReportRel) || null;
  }
  const open = ledger.filter(item => item && !item.revalidationReportPath);
  if (open.length > 0) return open[open.length - 1];
  return ledger.length > 0 ? ledger[ledger.length - 1] : null;
}

function failedReportRelFromArgs(designDir, failedReport) {
  const resolved = resolveInputPath(designDir, failedReport);
  return resolved ? relPath(designDir, resolved) : null;
}

function failedReportIdentityFromArgs(designDir, failedReport) {
  const resolved = resolveInputPath(designDir, failedReport);
  if (!resolved) return { path: null, rel: null, hash: null };
  const hash = fs.existsSync(resolved) && fs.statSync(resolved).isFile()
    ? sha256File(resolved)
    : null;
  return { path: resolved, rel: relPath(designDir, resolved), hash };
}

function collectAffectedFileHashes(designDir, affectedFiles) {
  const hashes = [];
  for (const affectedFile of affectedFiles || []) {
    const inputPath = resolveInputPath(designDir, affectedFile);
    const resolved = inputPath ? assertInsideDesignDir(designDir, inputPath, '--affected-files') : null;
    if (!resolved || !fs.existsSync(resolved) || !fs.statSync(resolved).isFile()) continue;
    hashes.push({
      path: relPath(designDir, resolved),
      hash: sha256File(resolved),
    });
  }
  return hashes;
}

function readLedgerFailedReport(designDir, ledgerEntry) {
  const failedReportPath = path.resolve(designDir, ledgerEntry.failedReportPath || '');
  if (!ledgerEntry.failedReportPath || !fs.existsSync(failedReportPath)) return null;
  try {
    return readJson(failedReportPath);
  } catch {
    return null;
  }
}

function allowedErrorClassesFromReport(report) {
  const classes = new Set();
  for (const row of Array.isArray(report?.repairActionTable) ? report.repairActionTable : []) {
    if (row?.errorClass) classes.add(row.errorClass);
  }
  for (const hint of Array.isArray(report?.repairPlanHints) ? report.repairPlanHints : []) {
    if (hint?.errorClass) classes.add(hint.errorClass);
    else if (hint?.repairScope) classes.add(hint.repairScope);
  }
  return [...classes].filter(Boolean);
}

function ensureRepairEntryEvidence(summary, failedReportRel, failedReportHash, entry) {
  const existing = summary.project.repairEntryEvidence.find(item =>
    item && item.failedReportPath === failedReportRel && item.failedReportHash === failedReportHash
  );
  const payload = {
    failedReportPath: failedReportRel,
    failedReportHash,
    repairWorkflowReadPath: entry.repairWorkflowReadPath,
    repairStartedAt: entry.repairStartedAt,
    ledgerIndex: summary.project.validationRepairLedger.findIndex(item => item === entry),
    ownerTriageCount: Array.isArray(entry.ownerTriage) ? entry.ownerTriage.length : 0,
    repairActionCount: Array.isArray(entry.repairActions) ? entry.repairActions.length : 0,
    revalidationReportPath: entry.revalidationReportPath || null,
    revalidationReportHash: entry.revalidationReportHash || null,
    revalidationSuccess: entry.revalidationSuccess ?? null,
  };
  if (existing) Object.assign(existing, payload);
  else summary.project.repairEntryEvidence.push(payload);
}

function recordStart(summary, args, failedReportPath, failedReportRel, failedReport) {
  if (failedReport.success === true) {
    reportError(['--failed-report points to a successful report; repair entry is only for failed validation']);
  }
  const recordedAt = new Date().toISOString();
  const failedReportHash = sha256File(failedReportPath);
  ensureValidationHistory(summary, failedReportRel, failedReport, failedReportHash);

  if (failedReport.terminalState) {
    summary.project.repairStopConditionMet = true;
    summary.project.repairStopReason = failedReport.terminalState;
    summary.project.remainingBlockingIssues = Array.isArray(failedReport.terminalViolations)
      ? failedReport.terminalViolations
      : (Array.isArray(failedReport.errors) ? failedReport.errors : []);
    return {
      phase: args.phase,
      failedReportPath: failedReportRel,
      outcome: 'terminal_stop',
      repairable: false,
      terminalState: failedReport.terminalState,
      requiredNextAction: 'stop_and_report_blocking_summary',
      forbiddenNextActions: [
        'repair ledger',
        'delete validation state',
        'rerun validation',
      ],
    };
  }

  const existingLedger = summary.project.validationRepairLedger.find(item =>
    item && item.failedReportPath === failedReportRel && item.failedReportHash === failedReportHash
  );
  const entry = {
    failedReportPath: failedReportRel,
    failedReportHash,
    repairWorkflowReadPath: 'intent-workflows/intent-project-mutation/main-agent-repair-workflow.md',
    repairStartedAt: recordedAt,
    repairEntryStatus: 'started-awaiting-owner-batch-repair',
    ownerTriage: inferOwnerTriage(failedReport),
    repairPlanHints: Array.isArray(failedReport.repairPlanHints) ? failedReport.repairPlanHints : [],
    repairActions: [],
    revalidationReportPath: null,
    revalidationReportHash: null,
    revalidationSuccess: null,
    blockedReason: null,
  };

  if (existingLedger) {
    Object.assign(existingLedger, {
      failedReportHash: entry.failedReportHash,
      repairWorkflowReadPath: existingLedger.repairWorkflowReadPath || entry.repairWorkflowReadPath,
      repairStartedAt: existingLedger.repairStartedAt || entry.repairStartedAt,
      repairEntryStatus: existingLedger.repairEntryStatus || entry.repairEntryStatus,
      ownerTriage: Array.isArray(existingLedger.ownerTriage) && existingLedger.ownerTriage.length > 0
        ? existingLedger.ownerTriage
        : entry.ownerTriage,
      repairPlanHints: Array.isArray(existingLedger.repairPlanHints) && existingLedger.repairPlanHints.length > 0
        ? existingLedger.repairPlanHints
        : entry.repairPlanHints,
      repairActions: Array.isArray(existingLedger.repairActions) ? existingLedger.repairActions : [],
    });
  } else {
    summary.project.validationRepairLedger.push(entry);
  }

  const ledgerEntry = existingLedger || entry;
  ensureRepairEntryEvidence(summary, failedReportRel, failedReportHash, ledgerEntry);
  return {
    phase: args.phase,
    failedReportPath: failedReportRel,
    ledgerIndex: summary.project.validationRepairLedger.findIndex(item => item === ledgerEntry),
    requiredNextRead: 'intent-workflows/intent-project-mutation/main-agent-repair-workflow.md',
    allowedNextActions: allowedErrorClassesFromReport(failedReport),
    forbiddenNextActions: [
      'validator source read',
      'SearchReplace runtime-orchestration-summary.json',
      'rerun full validation before batch repair',
    ],
    batchRepairRequired: true,
  };
}

function recordAction(summary, args) {
  const failedReportIdentity = failedReportIdentityFromArgs(args.designDir, args.failedReport);
  const ledgerEntry = findLedger(summary, failedReportIdentity.rel, failedReportIdentity.hash);
  if (!ledgerEntry) reportError(['No validationRepairLedger entry found; run --phase=start before --phase=action']);

  if (ledgerEntry.revalidationReportPath && !args.blockedReason) {
    reportError(['This failed report already has revalidation evidence; a second repair batch requires --blocked-reason and must not continue schema chasing']);
  }
  if (args.blockedReason) {
    ledgerEntry.blockedReason = args.blockedReason;
    ledgerEntry.repairEntryStatus = 'blocked-after-revalidation';
    summary.project.repairStopConditionMet = true;
    summary.project.repairStopReason = args.blockedReason;
    ensureRepairEntryEvidence(summary, ledgerEntry.failedReportPath, ledgerEntry.failedReportHash, ledgerEntry);
    return {
      phase: args.phase,
      failedReportPath: ledgerEntry.failedReportPath,
      blockedReason: args.blockedReason,
    };
  }

  const failedReport = readLedgerFailedReport(args.designDir, ledgerEntry);
  const allowedClasses = allowedErrorClassesFromReport(failedReport);
  let errorClass = args.errorClass;
  if (!errorClass && allowedClasses.length === 1) errorClass = allowedClasses[0];
  if (!errorClass) {
    reportError(['--error-class=<class> is required for repair action; use validation-report.json repairActionTable[].errorClass']);
  }
  if (allowedClasses.length > 0 && !allowedClasses.includes(errorClass)) {
    reportError([`--error-class=${errorClass} is not present in validation-report.json repairActionTable/repairPlanHints (${allowedClasses.join(', ')})`]);
  }

  if (!Array.isArray(ledgerEntry.repairActions)) ledgerEntry.repairActions = [];
  const observedFileHashes = collectAffectedFileHashes(args.designDir, args.affectedFiles);
  ledgerEntry.repairActions.push({
    owner: args.owner || 'main-agent',
    errorClass,
    affectedFiles: args.affectedFiles,
    action: args.action,
    observedFileHashes,
    preEditFileHashes: args.preEditFileHashes,
    postEditFileHashes: args.postEditFileHashes,
    repairOwnedFields: args.repairOwnedFields.length > 0 ? args.repairOwnedFields : [errorClass],
    recordedAt: new Date().toISOString(),
    repairActionTableRequired: allowedClasses.length > 0,
  });
  ledgerEntry.repairEntryStatus = 'action-recorded-awaiting-revalidation';
  ensureRepairEntryEvidence(summary, ledgerEntry.failedReportPath, ledgerEntry.failedReportHash, ledgerEntry);
  return {
    phase: args.phase,
    failedReportPath: ledgerEntry.failedReportPath,
    repairActionCount: ledgerEntry.repairActions.length,
  };
}

function recordRevalidate(summary, args) {
  const failedReportIdentity = failedReportIdentityFromArgs(args.designDir, args.failedReport);
  const ledgerEntry = findLedger(summary, failedReportIdentity.rel, failedReportIdentity.hash);
  if (!ledgerEntry) reportError(['No validationRepairLedger entry found; run --phase=start before --phase=revalidate']);

  const revalidationReportPath = resolveInputPath(args.designDir, args.revalidationReport);
  if (!fs.existsSync(revalidationReportPath)) {
    reportError([`revalidation report not found: ${revalidationReportPath}`]);
  }
  const revalidationReport = readJson(revalidationReportPath);
  const revalidationReportRel = relPath(args.designDir, revalidationReportPath);
  const revalidationReportHash = sha256File(revalidationReportPath);
  const isLedgerDiagnostic = revalidationReport.success !== true && isRepairLedgerOnlyReport(revalidationReport);
  if (revalidationReport.success !== true && !args.blockedReason && !isLedgerDiagnostic) {
    reportError(['Revalidation report is still failing; record a blocked summary with --blocked-reason=<reason> instead of starting a second repair loop']);
  }

  if (isLedgerDiagnostic) {
    recordLedgerDiagnosticReport(
      summary,
      revalidationReportRel,
      revalidationReport,
      revalidationReportHash,
      args.blockedReason || 'repair-ledger-diagnostic'
    );
  } else {
    ensureValidationHistory(summary, revalidationReportRel, revalidationReport, revalidationReportHash);
  }
  ledgerEntry.revalidationReportPath = revalidationReportRel;
  ledgerEntry.revalidationReportHash = revalidationReportHash;
  ledgerEntry.revalidationSuccess = revalidationReport.success === true;
  ledgerEntry.revalidationRecordedAt = new Date().toISOString();
  ledgerEntry.repairEntryStatus = revalidationReport.success === true
    ? 'revalidated-success'
    : 'revalidated-failed-blocked';
  if (args.blockedReason) {
    ledgerEntry.blockedReason = args.blockedReason;
    summary.project.repairStopConditionMet = true;
    summary.project.repairStopReason = args.blockedReason;
    summary.project.remainingBlockingIssues = Array.isArray(revalidationReport.errors)
      ? revalidationReport.errors
      : (Array.isArray(revalidationReport.renderBlockingErrors) ? revalidationReport.renderBlockingErrors : []);
  }
  ensureRepairEntryEvidence(summary, ledgerEntry.failedReportPath, ledgerEntry.failedReportHash, ledgerEntry);
  return {
    phase: args.phase,
    failedReportPath: ledgerEntry.failedReportPath,
    revalidationReportPath: revalidationReportRel,
    revalidationSuccess: ledgerEntry.revalidationSuccess,
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.errors.length > 0) {
    reportError(args.errors);
  }

  const summaryPath = path.join(args.designDir, 'runtime-orchestration-summary.json');
  if (!fs.existsSync(summaryPath)) {
    reportError([`runtime-orchestration-summary.json not found: ${summaryPath}`]);
  }

  const summary = readJson(summaryPath);
  ensureProjectArrays(summary);

  let phaseResult;
  if (args.phase === 'start') {
    const failedReportPath = resolveInputPath(args.designDir, args.failedReport);
    if (!fs.existsSync(failedReportPath)) {
      reportError([`failed report not found: ${failedReportPath}`]);
    }
    const failedReport = readJson(failedReportPath);
    phaseResult = recordStart(summary, args, failedReportPath, relPath(args.designDir, failedReportPath), failedReport);
  } else if (args.phase === 'action') {
    phaseResult = recordAction(summary, args);
  } else {
    phaseResult = recordRevalidate(summary, args);
  }

  writeJson(summaryPath, summary);
  const result = {
    success: true,
    ...phaseResult,
    summaryPath,
    ledgerCount: summary.project.validationRepairLedger.length,
    repairEntryEvidenceCount: summary.project.repairEntryEvidence.length,
  };

  if (args.json) console.log(JSON.stringify(result, null, 2));
  else console.log(`[OK] repair ledger ${args.phase} recorded`);
}

main();
