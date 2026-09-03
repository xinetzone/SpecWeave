#!/usr/bin/env node

/**
 * Regression checks for solo-design runtime contracts.
 *
 * These checks build temporary design projects and call the deterministic
 * tooling entrypoints directly. They must not write repo-local fixtures.
 */

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = path.resolve(SCRIPT_DIR, '..', '..');
const REPO_ROOT = findRepoRoot(SCRIPT_DIR);
const failures = [];

const COMMON_CONTEXT = [
  'shared-runtime/runtime-boundaries/lane-runtime-contracts.md',
  'shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md',
  'shared-runtime/agent-dispatch-runtime/shared-page-rendering-kernel.md',
  'delivery-quality/page-rendering-quality-gate.md',
  'delivery-quality/design-artifact-validation.md',
  'delivery-quality/delivery-evidence-contract.md',
  'visual-experience/visual-experience-guidelines.md',
  'visual-experience/visual-checkpoint-protocol.md',
];

function findRepoRoot(startDir) {
  let dir = startDir;
  const { root } = path.parse(dir);
  while (true) {
    if (fs.existsSync(path.join(dir, '.git'))) return dir;
    if (dir === root) break;
    const nextDir = path.dirname(dir);
    if (nextDir === dir) break;
    dir = nextDir;
  }
  return path.resolve(SCRIPT_DIR, '../../../../../../../../..');
}

function toolPath(name) {
  return path.join(SCRIPT_DIR, name);
}

function writeJson(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
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

function runNode(args, options = {}) {
  return spawnSync(process.execPath, args, {
    cwd: options.cwd || REPO_ROOT,
    encoding: 'utf8',
  });
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function tempProject(name) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), `solo-design-${name}-`));
  fs.mkdirSync(path.join(dir, 'pages'), { recursive: true });
  fs.mkdirSync(path.join(dir, 'assets'), { recursive: true });
  fs.writeFileSync(path.join(dir, 'colors_and_type.css'), ':root{--brand:#111;}\n', 'utf8');
  return dir;
}

function commonProjectFields() {
  return {
    resolvedLane: 'free_exploration',
    intentProfile: { caseFamily: 'free_exploration' },
    selectedIntentWorkflowRead: true,
    contextRequirementsLoaded: COMMON_CONTEXT.map(item => ({ path: item, readStatus: 'loaded', bodyRead: true })),
    contextReadScope: { status: 'declared-before-dispatch' },
    deviceType: 'desktop',
    operatingMode: 'free-explore',
    cssPreflightEvidence: { status: 'passed', prefixMode: 'prefixless', brandPrefix: '' },
  };
}

function baseSummary(pages, projectOverrides = {}) {
  return {
    schemaVersion: '1.0',
    skillProvenance: {
      name: 'solo-design',
      version: '2026.07.09.0',
      version_source: 'skill-release-manifest.json',
    },
    project: { ...commonProjectFields(), ...projectOverrides },
    designSource: { cssFilePath: 'colors_and_type.css' },
    pages,
  };
}

function writeSummary(projectDir, summary) {
  writeJson(path.join(projectDir, 'runtime-orchestration-summary.json'), summary);
}

function runBuildManifest(projectDir, mode = 'free-fast') {
  return runNode([
    toolPath('build-page-dispatch-manifest.mjs'),
    projectDir,
    `--mode=${mode}`,
    '--json',
  ]);
}

function parseToolJson(result) {
  const text = String(result.stdout || '').trim();
  return text ? JSON.parse(text) : null;
}

function currentSkillVersion() {
  return readJson(path.join(SKILL_DIR, 'skill-release-manifest.json')).version;
}

function pageNode(id, htmlSrc, title = 'Page') {
  return {
    id,
    title,
    type: 'page',
    version: 1,
    createdAt: 1,
    canvasData: { x: 0, y: 0, group: 0 },
    devMetadata: { htmlSrc, interactions: [] },
  };
}

function testBuildManifestDevMetadataAndPrefixless() {
  const dir = tempProject('manifest-success');
  fs.writeFileSync(path.join(dir, 'pages/index.html'), '<html><head></head><body><main>Ready</main></body></html>\n', 'utf8');
  writeSummary(dir, baseSummary([
    { nodeId: 'page-index', devMetadata: { htmlSrc: 'pages/index.html' }, title: 'Index' },
  ]));

  const result = runBuildManifest(dir);
  assert(result.status === 0, `build manifest failed: ${result.stderr || result.stdout}`);
  const summary = readJson(path.join(dir, 'runtime-orchestration-summary.json'));
  const entry = summary.project.dispatchPreflightManifest?.[0];
  assert(entry?.htmlSrc === 'pages/index.html', 'devMetadata.htmlSrc was not normalized into manifest htmlSrc');
  assert(entry?.headFillMode === 'replace-head-after-body', 'existing body did not infer replace-head-after-body');
  assert(String(entry?.fillHtmlHeadCommand || '').includes('--replace-head'), 'fill command missing --replace-head');
  assert(!String(entry?.fillHtmlHeadCommand || '').includes('{SKILL_DIR}'), 'fill command still contains unresolved {SKILL_DIR} placeholder');
  assert(path.isAbsolute(entry?.skillRuntime?.skillDir || ''), 'skillRuntime.skillDir must be an absolute path');
  assert(path.isAbsolute(entry?.skillRuntime?.toolPaths?.recordDispatchCompletion || ''), 'recordDispatchCompletion path must be absolute');
  assert(fs.existsSync(entry.skillRuntime.toolPaths.recordDispatchCompletion), 'recordDispatchCompletion path does not exist');
  assert(path.isAbsolute(entry?.skillRuntime?.toolPaths?.applyHtmlHeadContract || ''), 'applyHtmlHeadContract path must be absolute');
  assert(fs.existsSync(entry.skillRuntime.toolPaths.applyHtmlHeadContract), 'applyHtmlHeadContract path does not exist');
  assert(String(entry?.skillRuntime?.commandTemplates?.recordDispatchCompletion || '').includes('record-dispatch-completion.mjs'), 'record dispatch completion command template missing');
  assert(!String(entry?.skillRuntime?.commandTemplates?.recordDispatchCompletion || '').includes('{SKILL_DIR}'), 'record dispatch completion command still contains unresolved {SKILL_DIR} placeholder');
  assert(entry?.deterministicCommands === null, 'non-restore page dispatch should not expose restore deterministicCommands');
  assert(!Object.prototype.hasOwnProperty.call(summary.project, 'expectedDispatches'), 'pre-dispatch build wrote expectedDispatches[]');
  assert(!entry.missingFields?.includes('brandPrefix'), 'prefixless project was treated as missing brandPrefix');
}

function testValidateDesignFileFormatMultiFileDoesNotApplyBatchExpectedPagesPerFile() {
  const dirA = tempProject('design-file-multi-a');
  const dirB = tempProject('design-file-multi-b');
  fs.writeFileSync(path.join(dirA, 'pages/a.html'), '<html><head></head><body><main>A</main></body></html>\n', 'utf8');
  fs.writeFileSync(path.join(dirB, 'pages/b.html'), '<html><head></head><body><main>B</main></body></html>\n', 'utf8');
  const designA = path.join(dirA, 'a.design');
  const designB = path.join(dirB, 'b.design');
  writeJson(designA, { data: [pageNode('page-a', 'pages/a.html', 'A')] });
  writeJson(designB, { data: [pageNode('page-b', 'pages/b.html', 'B')] });

  const result = runNode([
    toolPath('validate-design-file-format.mjs'),
    designA,
    designB,
    '--expected-pages=2',
  ]);
  assert(result.status === 0, `multi-file design validation applied batch expectedPages per file: ${result.stderr || result.stdout}`);
}

function restoreFacts() {
  const categories = ['viewport', 'layout-region', 'color-surface', 'component-proportion', 'density-spacing'];
  return Array.from({ length: 8 }, (_, index) => ({
    id: `fact-${index + 1}`,
    category: categories[index % categories.length],
    sourceRegion: `region-${index + 1}`,
    fact: `source fact ${index + 1}`,
    measurementBasis: 'fixture',
    priority: index < 5 ? 'high' : 'medium',
    usedByCheckpointIds: [`vc-${index + 1}`],
  }));
}

function restoreCheckpoints() {
  return Array.from({ length: 8 }, (_, index) => ({
    id: `vc-${index + 1}`,
    priority: index < 5 ? 'high' : 'medium',
    sourceRegion: `region-${index + 1}`,
    sourceFact: `source fact ${index + 1}`,
    expected: `expected restoration ${index + 1}`,
    implementationEvidence: 'pages/index.html',
    status: 'matched',
  }));
}

function restoreContextRequirements() {
  return [
    'intent-workflows/intent-page-restore-1to1/start-restore-1to1-project.md',
    'shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md',
    'intent-workflows/intent-page-restore-1to1/dispatch-contract.md',
    'intent-workflows/intent-page-restore-1to1/restore-dispatch-packet-format.md',
  ].map(item => ({ path: item, readStatus: 'loaded', bodyRead: true }));
}

function testRestoreFinishReadinessAllRequiresResponseDraft() {
  const dir = tempProject('restore-finish-command');
  fs.writeFileSync(path.join(dir, 'pages/index.html'), '<html><head></head><body><main>Restore</main></body></html>\n', 'utf8');
  writeJson(path.join(dir, 'restore-contract-report.json'), {
    success: true,
    checkedAt: '2026-07-14T00:00:00.000Z',
    errors: [],
    warnings: [],
  });
  writeSummary(dir, baseSummary(
    [{ nodeId: 'page-index', htmlSrc: 'pages/index.html', title: 'Restore' }],
    {
      resolvedLane: 'restore_1to1',
      intentProfile: { caseFamily: 'restore_1to1', sourceType: 'image' },
      replicationMode: 'high-fidelity',
      sourceType: 'image',
      referenceCaptureEvidence: { providedImagePath: 'assets/reference.png' },
      sourceAuthorityLock: {
        visualAuthority: 'user-screenshot',
        contentSupplement: 'none',
        browserObservationRole: 'targeted-verification-only',
        mayOverrideVisualAuthority: false,
        lockedBeforeDispatch: true,
      },
      contextRequirementsLoaded: restoreContextRequirements(),
      measuredSourceFacts: restoreFacts(),
      restoreVisualCheckpoints: restoreCheckpoints(),
    }
  ));

  const result = runBuildManifest(dir, 'free-fast');
  assert(result.status === 0, `restore build manifest failed: ${result.stderr || result.stdout}`);
  const summary = readJson(path.join(dir, 'runtime-orchestration-summary.json'));
  const command = summary.project.dispatchPreflightManifest?.[0]?.deterministicCommands?.finishReadinessAll;
  assert(summary.project.dispatchPreflightManifest?.[0]?.packetType === 'RestorePagePacket', 'restore summary did not infer RestorePagePacket');
  assert(String(command || '').includes('--check=all'), 'restore finishReadinessAll missing --check=all');
  assert(String(command || '').includes('--final-response-file='), 'restore finishReadinessAll missing --final-response-file');
}

function testBuildManifestAcceptsProvidedImagePathForImageUrlRestore() {
  const dir = tempProject('restore-image-url-evidence');
  fs.writeFileSync(path.join(dir, 'pages/index.html'), '<html><head></head><body><main>Restore</main></body></html>\n', 'utf8');
  writeJson(path.join(dir, 'restore-contract-report.json'), {
    success: true,
    checkedAt: '2026-07-20T00:00:00.000Z',
    errors: [],
    warnings: [],
  });
  writeSummary(dir, baseSummary(
    [{ nodeId: 'page-index', htmlSrc: 'pages/index.html', title: 'Restore' }],
    {
      resolvedLane: 'restore_1to1',
      intentProfile: { caseFamily: 'restore_1to1', sourceType: 'image+url' },
      replicationMode: 'high-fidelity',
      sourceType: 'image+url',
      referenceCaptureEvidence: {
        providedImagePath: 'assets/reference.png',
        fullPageScreenshotEvidence: 'assets/url-capture.png',
      },
      sourceAuthorityLock: {
        visualAuthority: 'user-screenshot',
        contentSupplement: 'url-copy-and-structure-only',
        browserObservationRole: 'targeted-verification-only',
        mayOverrideVisualAuthority: false,
        lockedBeforeDispatch: true,
      },
      contextRequirementsLoaded: restoreContextRequirements(),
      measuredSourceFacts: restoreFacts(),
      restoreVisualCheckpoints: restoreCheckpoints(),
    }
  ));

  const result = runBuildManifest(dir, 'restore');
  assert(result.status === 0, `providedImagePath was rejected as image evidence: ${result.stderr || result.stdout}`);
}

function validThemeCss() {
  return `:root {
  --background: #fff;
  --foreground: #111;
  --card: #fff;
  --primary: #2563eb;
  --border: #ddd;
  --muted: #f3f4f6;
  --radius-sm: 4px;
  --radius-md: 8px;
}
`;
}

function testReplaceHeadAddsMissingThemeClass() {
  const dir = tempProject('replace-head-theme-class');
  const cssPath = path.join(dir, 'colors_and_type.css');
  const htmlPath = path.join(dir, 'pages/index.html');
  const existingLightPath = path.join(dir, 'pages/existing-light.html');
  const existingDarkPath = path.join(dir, 'pages/existing-dark.html');
  fs.writeFileSync(cssPath, validThemeCss(), 'utf8');
  fs.writeFileSync(
    htmlPath,
    '<!DOCTYPE html><html lang="en"><head><title>Keep</title></head><body><main>Preserve me</main></body></html>\n',
    'utf8'
  );
  fs.writeFileSync(
    existingLightPath,
    '<!DOCTYPE html><html lang="en" class="app light"><head><title>Light</title></head><body><main>Switch dark</main></body></html>\n',
    'utf8'
  );
  fs.writeFileSync(
    existingDarkPath,
    '<!DOCTYPE html><html lang="en" class="app dark"><head><title>Dark</title></head><body><main>Keep dark</main></body></html>\n',
    'utf8'
  );

  const result = runNode([
    toolPath('apply-html-head-contract.mjs'),
    cssPath,
    htmlPath,
    existingLightPath,
    existingDarkPath,
    '--replace-head',
    '--theme=dark',
  ]);
  assert(result.status === 0, `replace-head failed: ${result.stderr || result.stdout}`);
  const html = fs.readFileSync(htmlPath, 'utf8');
  assert(/<html\b[^>]*\bclass=["'][^"']*\bdark\b[^"']*["']/i.test(html), 'replace-head did not add requested dark theme class');
  assert(html.includes('<main>Preserve me</main>'), 'replace-head changed main content');
  const existingLightHtml = fs.readFileSync(existingLightPath, 'utf8');
  assert(/\bclass=["']app dark["']/.test(existingLightHtml), 'replace-head did not switch an existing light class to dark');
  assert(!/\bclass=["'][^"']*\blight\b/.test(existingLightHtml), 'replace-head left the previous light theme class behind');
  assert(existingLightHtml.includes('<main>Switch dark</main>'), 'replace-head changed switched page main content');
  const existingDarkHtml = fs.readFileSync(existingDarkPath, 'utf8');
  assert(/\bclass=["']app dark["']/.test(existingDarkHtml), 'replace-head did not preserve an existing theme class');
  assert(existingDarkHtml.includes('<main>Keep dark</main>'), 'replace-head changed existing dark page main content');
}

function testReplaceHeadPreservesExistingThemeWithoutExplicitFlag() {
  const dir = tempProject('replace-head-preserve-theme');
  const cssPath = path.join(dir, 'colors_and_type.css');
  const htmlPath = path.join(dir, 'pages/existing-dark.html');
  fs.writeFileSync(cssPath, validThemeCss(), 'utf8');
  fs.writeFileSync(
    htmlPath,
    '<!DOCTYPE html><html lang="en" class="app dark"><head><title>Dark</title></head><body><main>Keep dark</main></body></html>\n',
    'utf8'
  );

  const result = runNode([
    toolPath('apply-html-head-contract.mjs'),
    cssPath,
    htmlPath,
    '--replace-head',
  ]);
  assert(result.status === 0, `replace-head without theme failed: ${result.stderr || result.stdout}`);
  const html = fs.readFileSync(htmlPath, 'utf8');
  assert(/\bclass=["']app dark["']/.test(html), 'replace-head without explicit theme changed the existing dark class');
  assert(html.includes('<main>Keep dark</main>'), 'replace-head without theme changed main content');
}

function testValidateDesignFileAcceptsSingleQuotedDomId() {
  const dir = tempProject('single-quoted-dom-id');
  const htmlPath = path.join(dir, 'pages/index.html');
  fs.writeFileSync(htmlPath, "<html><body><button data-dom-id='go'>Go</button></body></html>\n", 'utf8');
  const node = pageNode('page-index', 'pages/index.html', 'Index');
  node.devMetadata.interactions = [{ domId: 'go', targetPageId: 'page-index' }];
  const designPath = path.join(dir, 'project.design');
  writeJson(designPath, { data: [node] });

  const result = runNode([toolPath('validate-design-file-format.mjs'), designPath]);
  assert(result.status === 0, `single-quoted data-dom-id was rejected: ${result.stderr || result.stdout}`);
}

function testInteractionDomIdCheckerReadsMultiplePages() {
  const dir = tempProject('interaction-domids-multiple-pages');
  fs.writeFileSync(path.join(dir, 'pages/a.html'), '<html><body><button data-dom-id="a">A</button></body></html>\n', 'utf8');
  fs.writeFileSync(path.join(dir, 'pages/b.html'), "<html><body><button data-dom-id='b'>B</button></body></html>\n", 'utf8');
  writeSummary(dir, {
    pages: [
      { nodeId: 'page-a', htmlSrc: 'pages/a.html', domIdsRequired: ['a'] },
      { nodeId: 'page-b', htmlSrc: 'pages/b.html', domIdsRequired: ['b'] },
    ],
  });

  const result = runNode([toolPath('check-interaction-domids.mjs'), dir, '--json']);
  assert(result.status === 0, `multi-page domId check failed: ${result.stderr || result.stdout}`);
  const parsed = parseToolJson(result);
  assert(parsed?.checkedPages === 2 && parsed?.totalDomIdsChecked === 2, 'multi-page domId check returned incorrect counts');
}

function testLaneContractSkipsDeprecatedRestoreEvidenceForCurrentVersion() {
  const dir = tempProject('restore-lane-current-contract');
  const summary = baseSummary(
    [{ nodeId: 'page-index', htmlSrc: 'pages/index.html', title: 'Restore' }],
    {
      resolvedLane: 'restore_1to1',
      intentProfile: { caseFamily: 'restore_1to1', sourceType: 'image' },
      replicationMode: 'high-fidelity',
      sourceType: 'image',
      referenceCaptureEvidence: { providedImagePath: 'assets/reference.png' },
      sourceAuthorityLock: {
        visualAuthority: 'user-screenshot',
        mayOverrideVisualAuthority: false,
        lockedBeforeDispatch: true,
      },
      contextRequirementsLoaded: restoreContextRequirements(),
      measuredSourceFacts: restoreFacts(),
      restoreVisualCheckpoints: restoreCheckpoints(),
      validationRunDiscipline: {
        maxFullValidationRuns: 2,
        softWarningsTriggerRepair: false,
        blockingRepairMode: 'targeted-once',
      },
      lowValueCallWatchdog: {
        applies: true,
        noProgressNextAction: 'enter_readiness_or_blocked_summary',
      },
      dispatchPreflightManifest: [{
        nodeId: 'page-index',
        htmlSrc: 'pages/index.html',
        packetType: 'RestorePagePacket',
        allowedWritePaths: ['pages/index.html', 'assets/'],
      }],
      expectedDispatches: [{
        nodeId: 'page-index',
        packetType: 'RestorePagePacket',
        status: 'not_required',
      }],
    }
  );
  summary.skillProvenance.version = currentSkillVersion();
  writeSummary(dir, summary);

  const result = runNode([toolPath('validate-lane-runtime-contract.mjs'), dir, '--mode=restore']);
  assert(result.status === 0, `current restore contract required deprecated evidence fields: ${result.stderr || result.stdout}`);
}

function testWorkspaceAcceptsProvidedImagePathForImageUrlRestore() {
  const dir = tempProject('workspace-restore-image-url-evidence');
  fs.writeFileSync(path.join(dir, 'pages/index.html'), '<html><head></head><body><main>Restore</main></body></html>\n', 'utf8');
  const summary = baseSummary(
    [{ nodeId: 'page-index', htmlSrc: 'pages/index.html', title: 'Restore' }],
    {
      resolvedLane: 'restore_1to1',
      intentProfile: { caseFamily: 'restore_1to1', sourceType: 'image+url' },
      replicationMode: 'high-fidelity',
      sourceType: 'image+url',
      referenceCaptureEvidence: {
        providedImagePath: 'assets/reference.png',
        fullPageScreenshotEvidence: 'assets/url-capture.png',
        visualAuthority: 'provided-image',
      },
    }
  );
  summary.skillProvenance.version = currentSkillVersion();
  writeSummary(dir, summary);

  const result = runNode([toolPath('validate-design-workspace.mjs'), dir]);
  const output = `${result.stdout || ''}\n${result.stderr || ''}`;
  assert(output.includes('Checking restore_1to1 evidence gates'), 'workspace restore evidence validation did not run');
  assert(
    !output.includes('image+url restore requires provided image/screenshot evidence'),
    'workspace validator rejected providedImagePath as image evidence'
  );
}

function testGraphicValidatorRejectsFalsyJsonRoots() {
  for (const [name, value] of [['null', null], ['false', false], ['zero', 0]]) {
    const dir = tempProject(`graphic-falsy-root-${name}`);
    fs.writeFileSync(path.join(dir, 'project.design'), `${JSON.stringify(value)}\n`, 'utf8');
    const result = runNode([toolPath('validate-graphic-asset-design.mjs'), dir]);
    assert(result.status !== 0, `graphic validator accepted ${name} JSON root`);
    assert(String(result.stderr || result.stdout).includes('[root] must be a JSON object'), `graphic validator did not report ${name} root type`);
  }
}

function testRestoreNextCheckUsesCompleteGate() {
  const source = fs.readFileSync(toolPath('validate-design-workspace.mjs'), 'utf8');
  assert(/const finalResponseArg = ` --final-response-file=\$\{shellQuote\('<final-response-draft\.md>'\)\}`;/.test(source), 'nextCheck missing final response draft placeholder');
  assert(/isRestore \? `--check=all\$\{finalResponseArg\}` : '--check=all'/.test(source), 'restore success nextCheck must use --check=all with final response draft');
}

function testWorkspaceNextCheckUsesCompleteGateForHtmlPageWorkflows() {
  const source = fs.readFileSync(toolPath('validate-design-workspace.mjs'), 'utf8');
  assert(
    source.includes("command: `node ${shellQuote(finishReadiness)} ${shellQuote(designDir)} --check=all`") ||
      source.includes("isRestore ? `--check=all${finalResponseArg}` : '--check=all'"),
    'HTML/page workspace success nextCheck must use complete finish readiness gate, not --check=artifact'
  );
  assert(
    !source.includes("isRestore ? `--check=all${finalResponseArg}` : '--check=artifact'"),
    'HTML/page workspace success nextCheck still points to partial artifact gate'
  );
}

function testWorkspaceValidatorAcceptsTargetPageIdAlias() {
  const source = fs.readFileSync(toolPath('validate-design-workspace.mjs'), 'utf8');
  assert(source.includes('item.targetPageId === entry?.nodeId'), 'workspace validator must accept legacy expectedDispatches.targetPageId alias');
}

function testWorkspaceProjectFileHashKeysUseForwardSlashes() {
  const source = fs.readFileSync(toolPath('validate-design-workspace.mjs'), 'utf8');
  assert(source.includes("relPaths.push(relPath.replace(/\\\\/g, '/'))"), 'workspace projectFileHashes keys must normalize path separators to forward slashes');
}

function testWorkspaceRejectsDispatchTraversalPath() {
  const dir = tempProject('workspace-dispatch-traversal');
  const summary = laneSummary([
    {
      nodeId: 'page-index',
      packetType: 'FreePagePacket',
      status: 'completed',
      changedFiles: ['pages/../runtime-orchestration-summary.json'],
      toolCallLedger: {
        source: 'main-agent-runtime-trace',
        traceDigest: 'abcdef1234567890',
        todoWriteCalls: 0,
        previewCalls: 0,
        validationScriptCalls: 0,
        helperScriptWrites: 0,
      },
    },
  ]);
  writeSummary(dir, summary);
  const result = runNode([
    toolPath('validate-design-workspace.mjs'),
    dir,
    '--check=dispatch-discipline',
  ]);
  assert(result.status !== 0, 'workspace dispatch validation accepted a changedFiles traversal path');
  assert(String(result.stderr || result.stdout).includes('invalid or traversing path'), 'workspace traversal error was not reported');
}

function testBuildManifestRejectsEscapes() {
  const dir = tempProject('manifest-escape-html');
  writeSummary(dir, baseSummary([
    { nodeId: 'page-index', htmlSrc: '../escape.html', title: 'Escape' },
  ]));
  const result = runBuildManifest(dir);
  assert(result.status !== 0, 'build manifest accepted escaping htmlSrc');
  const parsed = parseToolJson(result);
  assert((parsed?.errors || []).some(error => String(error).includes('must not contain ".."')), 'escaping htmlSrc error was not reported');
}

function testBuildManifestRejectsAllowedWriteEscapes() {
  const dir = tempProject('manifest-escape-allowed');
  fs.writeFileSync(path.join(dir, 'pages/index.html'), '<html><body>Ready</body></html>\n', 'utf8');
  writeSummary(dir, baseSummary([
    { nodeId: 'page-index', htmlSrc: 'pages/index.html', allowedWritePaths: ['../outside/'] },
  ]));
  const result = runBuildManifest(dir);
  assert(result.status !== 0, 'build manifest accepted escaping allowedWritePaths[]');
  const parsed = parseToolJson(result);
  assert((parsed?.errors || []).some(error => String(error).includes('allowedWritePaths') && String(error).includes('must not contain ".."')), 'escaping allowedWritePaths[] error was not reported');
}

function laneSummary(expectedDispatches) {
  return {
    schemaVersion: '1.0',
    skillProvenance: {
      name: 'solo-design',
      version: '2026.07.11.0',
      version_source: 'skill-release-manifest.json',
    },
    project: {
      ...commonProjectFields(),
      validationRunDiscipline: {
        maxFullValidationRuns: 2,
        softWarningsTriggerRepair: false,
        blockingRepairMode: 'targeted-once',
      },
      lowValueCallWatchdog: {
        applies: true,
        noProgressNextAction: 'enter_readiness_or_blocked_summary',
      },
      dispatchPreflightManifest: [
        {
          nodeId: 'page-index',
          htmlSrc: 'pages/index.html',
          packetType: 'FreePagePacket',
          allowedWritePaths: ['pages/', 'assets/'],
        },
      ],
      expectedDispatches,
    },
    designSource: { cssFilePath: 'colors_and_type.css' },
    pages: [{ nodeId: 'page-index', htmlSrc: 'pages/index.html' }],
  };
}

function testLaneContractNodeIdAndAllowedDirectory() {
  const dir = tempProject('lane-nodeid');
  writeSummary(dir, laneSummary([
    {
      nodeId: 'page-index',
      packetType: 'FreePagePacket',
      status: 'completed',
      changedFiles: ['assets/a.png'],
    },
  ]));
  const result = runNode([
    toolPath('validate-lane-runtime-contract.mjs'),
    dir,
    '--mode=free-fast',
  ]);
  assert(result.status === 0, `nodeId expectedDispatches did not pass lane validation: ${result.stderr || result.stdout}`);
}

function testLaneContractNotRequiredNoChangedFiles() {
  const dir = tempProject('lane-not-required');
  writeSummary(dir, laneSummary([
    {
      nodeId: 'page-index',
      packetType: 'FreePagePacket',
      status: 'not_required',
      reason: 'no page task needed',
    },
  ]));
  const result = runNode([
    toolPath('validate-lane-runtime-contract.mjs'),
    dir,
    '--mode=free-fast',
  ]);
  assert(result.status === 0, `not_required dispatch required changedFiles[]: ${result.stderr || result.stdout}`);
}

function testRepairLedgerSamePathNewHashCreatesEntry() {
  const dir = tempProject('repair-ledger');
  writeSummary(dir, { schemaVersion: '1.0', project: {} });
  const failedPath = path.join(dir, 'validation-report.json');
  const revalidationPath = path.join(dir, 'revalidation-report.json');

  writeJson(failedPath, { success: false, errors: ['first failure'], checkedAt: '2026-07-14T00:00:00.000Z' });
  let result = runNode([
    toolPath('record-validation-repair-entry.mjs'),
    dir,
    '--phase=start',
    `--failed-report=${failedPath}`,
  ]);
  assert(result.status === 0, `first repair start failed: ${result.stderr || result.stdout}`);

  writeJson(revalidationPath, { success: true, errors: [], checkedAt: '2026-07-14T00:01:00.000Z' });
  result = runNode([
    toolPath('record-validation-repair-entry.mjs'),
    dir,
    '--phase=revalidate',
    `--failed-report=${failedPath}`,
    `--revalidation-report=${revalidationPath}`,
  ]);
  assert(result.status === 0, `first repair revalidate failed: ${result.stderr || result.stdout}`);

  writeJson(failedPath, { success: false, errors: ['second failure'], checkedAt: '2026-07-14T00:02:00.000Z' });
  result = runNode([
    toolPath('record-validation-repair-entry.mjs'),
    dir,
    '--phase=start',
    `--failed-report=${failedPath}`,
  ]);
  assert(result.status === 0, `second repair start failed: ${result.stderr || result.stdout}`);

  const summary = readJson(path.join(dir, 'runtime-orchestration-summary.json'));
  const ledger = summary.project.validationRepairLedger || [];
  assert(ledger.length === 2, `expected 2 repair ledger entries, found ${ledger.length}`);
  assert(ledger[1].revalidationReportPath === null, 'new failed report reused old revalidation evidence');
  assert(ledger[0].failedReportHash !== ledger[1].failedReportHash, 'ledger entries did not preserve distinct failed report hashes');
}

function testRepairLedgerOnlyRevalidationDoesNotCreateCascadingHistory() {
  const dir = tempProject('ledger-only-diagnostic');
  const failedReportPath = path.join(dir, 'validation-report.json');
  writeJson(failedReportPath, {
    success: false,
    errors: ['[artifact-readiness] missing design registration'],
    checkedAt: '2026-07-14T00:00:00.000Z',
    repairActionTable: [{ errorClass: 'artifact-readiness', action: 'fix-design-registration' }],
  });
  writeSummary(dir, baseSummary([], {
    validationRunDiscipline: { maxFullValidationRuns: 2, softWarningsTriggerRepair: false },
  }));

  let result = runNode([
    toolPath('record-validation-repair-entry.mjs'),
    dir,
    '--phase=start',
    `--failed-report=${failedReportPath}`,
  ]);
  assert(result.status === 0, `start failed: ${result.stderr || result.stdout}`);

  result = runNode([
    toolPath('record-validation-repair-entry.mjs'),
    dir,
    '--phase=action',
    `--failed-report=${failedReportPath}`,
    '--owner=main-agent',
    '--error-class=artifact-readiness',
    '--action=fix-design-registration',
    '--affected-files=runtime-orchestration-summary.json',
  ]);
  assert(result.status === 0, `action failed: ${result.stderr || result.stdout}`);

  writeJson(failedReportPath, {
    success: false,
    errors: [
      '[repair-ledger] validationHistory has 2 failed validation(s) but validationRepairLedger has 1 entry',
      '[repair-ledger] validationHistory has 2 failed validation(s) but repairEntryEvidence has 1 entry',
    ],
    checkedAt: '2026-07-14T00:01:00.000Z',
    repairActionTable: [{ errorClass: 'repair-ledger', action: 'append_repair_entry_evidence' }],
  });

  result = runNode([
    toolPath('record-validation-repair-entry.mjs'),
    dir,
    '--phase=revalidate',
    `--failed-report=${failedReportPath}`,
    `--revalidation-report=${failedReportPath}`,
    '--blocked-reason=repair-ledger-diagnostic',
  ]);
  assert(result.status === 0, `ledger diagnostic revalidate failed: ${result.stderr || result.stdout}`);

  const summary = readJson(path.join(dir, 'runtime-orchestration-summary.json'));
  assert(summary.project.validationHistory.length === 1, 'ledger-only diagnostic report was appended to validationHistory and can cascade');
  assert(summary.project.ledgerDiagnosticReports.length === 1, 'ledger-only diagnostic report was not recorded as bounded diagnostic evidence');

  result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=repair-ledger',
  ]);
  assert(result.status === 0, `repair ledger readiness rejected current diagnostic report: ${result.stderr || result.stdout}`);

  writeJson(failedReportPath, {
    success: true,
    errors: [],
    checkedAt: '2026-07-14T00:02:00.000Z',
    validationRunDisciplineStatus: {
      validationHistoryCount: 1,
      repairLedgerCount: 1,
    },
  });

  result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=repair-ledger',
  ]);
  assert(result.status === 0, `repair ledger readiness rejected diagnostic evidence after final report overwrite: ${result.stderr || result.stdout}`);
}

function testRecordRepairActionDoesNotRequireAgentHashes() {
  const dir = tempProject('repair-action-no-agent-hashes');
  fs.writeFileSync(path.join(dir, 'runtime-orchestration-summary.json'), `${JSON.stringify({
    schemaVersion: '1.0',
    project: {},
  }, null, 2)}\n`, 'utf8');
  fs.writeFileSync(path.join(dir, 'pages/index.html'), '<html><head></head><body><main>Before</main></body></html>\n', 'utf8');
  const failedPath = path.join(dir, 'validation-report.json');
  writeJson(failedPath, {
    success: false,
    errors: ['[html-quality] pages/index.html missing token'],
    checkedAt: '2026-07-14T00:00:00.000Z',
    repairActionTable: [{ errorClass: 'html-quality', action: 'targeted_token_replace_once' }],
  });

  let result = runNode([
    toolPath('record-validation-repair-entry.mjs'),
    dir,
    '--phase=start',
    `--failed-report=${failedPath}`,
  ]);
  assert(result.status === 0, `repair start failed: ${result.stderr || result.stdout}`);

  result = runNode([
    toolPath('record-validation-repair-entry.mjs'),
    dir,
    '--phase=action',
    `--failed-report=${failedPath}`,
    '--owner=main-agent',
    '--error-class=html-quality',
    '--action=targeted_token_replace_once',
    '--affected-files=pages/index.html',
  ]);
  assert(result.status === 0, `repair action required agent-provided hashes: ${result.stderr || result.stdout}`);

  const summary = readJson(path.join(dir, 'runtime-orchestration-summary.json'));
  const action = summary.project.validationRepairLedger?.[0]?.repairActions?.[0];
  assert(action?.affectedFiles?.[0] === 'pages/index.html', 'repair action did not preserve affectedFiles');
  assert(Array.isArray(action?.observedFileHashes) && action.observedFileHashes.length === 1, 'repair action did not record script-owned file hash evidence');
  assert(action.observedFileHashes[0].path === 'pages/index.html', 'observed file hash path was not normalized');
}

function testRecordRepairActionRejectsEscapingAffectedFiles() {
  const dir = tempProject('repair-action-escape');
  fs.writeFileSync(path.join(dir, 'runtime-orchestration-summary.json'), `${JSON.stringify({
    schemaVersion: '1.0',
    project: {},
  }, null, 2)}\n`, 'utf8');
  const outside = path.join(path.dirname(dir), 'outside.html');
  fs.writeFileSync(outside, '<html>outside</html>\n', 'utf8');
  const failedPath = path.join(dir, 'validation-report.json');
  writeJson(failedPath, {
    success: false,
    errors: ['[html-quality] outside path attempt'],
    checkedAt: '2026-07-14T00:00:00.000Z',
    repairActionTable: [{ errorClass: 'html-quality', action: 'targeted_token_replace_once' }],
  });
  let result = runNode([
    toolPath('record-validation-repair-entry.mjs'),
    dir,
    '--phase=start',
    `--failed-report=${failedPath}`,
  ]);
  assert(result.status === 0, `repair start failed: ${result.stderr || result.stdout}`);

  result = runNode([
    toolPath('record-validation-repair-entry.mjs'),
    dir,
    '--phase=action',
    `--failed-report=${failedPath}`,
    '--owner=main-agent',
    '--error-class=html-quality',
    '--action=targeted_token_replace_once',
    `--affected-files=${path.relative(dir, outside)}`,
  ]);
  assert(result.status !== 0, 'repair action accepted affected file outside design project');
  assert(String(result.stderr || result.stdout).includes('escapes design project'), 'escaping affected file error was not reported');
}

function testFinishReadinessIgnoresRepairActionHashes() {
  const dir = tempProject('finish-ledger-no-action-hashes');
  const validationReportPath = path.join(dir, 'validation-report.json');
  writeJson(validationReportPath, {
    success: true,
    errors: [],
    checkedAt: '2026-07-14T00:05:00.000Z',
    projectFileHashes: { 'pages/index.html': 'unused-for-repair-ledger-check' },
    validationRunDisciplineStatus: { validationHistoryCount: 1, repairLedgerCount: 1 },
    skillProvenance: { name: 'solo-design', version: currentSkillVersion() },
    renderBlockingErrorCount: 0,
    errorCount: 0,
    designDir: dir,
  });
  writeSummary(dir, {
    schemaVersion: '1.0',
    project: {
      validationHistory: [
        {
          reportPath: 'validation-report.json',
          reportHash: 'failed-report-hash-1',
          success: false,
          exitCode: 1,
          checkedAt: '2026-07-14T00:00:00.000Z',
        },
      ],
      validationRepairLedger: [
        {
          failedReportPath: 'validation-report.json',
          repairWorkflowReadPath: 'intent-workflows/intent-project-mutation/main-agent-repair-workflow.md',
          repairStartedAt: '2026-07-14T00:01:00.000Z',
          ownerTriage: [{ owner: 'main-agent' }],
          repairActions: [{ owner: 'main-agent', errorClass: 'html-quality', affectedFiles: ['pages/index.html'], action: 'targeted' }],
          revalidationReportPath: 'validation-report.json',
          revalidationSuccess: true,
        },
      ],
      repairEntryEvidence: [{ failedReportPath: 'validation-report.json' }],
    },
  });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=repair-ledger',
  ]);
  assert(result.status === 0, `finish readiness rejected repair action without pre/post hashes: ${result.stderr || result.stdout}`);
}

function testFinishReadinessRejectsIncompleteValidationReport() {
  const dir = tempProject('finish-incomplete-report');
  writeJson(path.join(dir, 'validation-report.json'), { success: true });
  writeSummary(dir, { schemaVersion: '1.0', project: {} });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=all',
  ]);
  assert(result.status !== 0, 'finish readiness accepted a forged/incomplete validation-report.json');
  const parsed = parseToolJson(result);
  assert(
    (parsed?.errors || []).some(error => String(error).includes('projectFileHashes') || String(error).includes('validationRunDisciplineStatus')),
    'incomplete validation report integrity error was not reported'
  );
}

function testPostValidationMutationStillFails() {
  const dir = tempProject('finish-post-mutation');
  const htmlPath = path.join(dir, 'pages/index.html');
  fs.writeFileSync(htmlPath, '<html><head></head><body><main>Valid</main></body></html>\n', 'utf8');
  writeJson(path.join(dir, 'validation-report.json'), {
    success: true,
    errors: [],
    checkedAt: '2026-07-14T00:05:00.000Z',
    projectFileHashes: {
      'colors_and_type.css': sha256File(path.join(dir, 'colors_and_type.css')),
      'pages/index.html': sha256File(htmlPath),
    },
    validationRunDisciplineStatus: { validationHistoryCount: 0, repairLedgerCount: 0 },
    skillProvenance: { name: 'solo-design', version: currentSkillVersion() },
    renderBlockingErrorCount: 0,
    errorCount: 0,
    designDir: dir,
  });
  fs.writeFileSync(htmlPath, '<html><head></head><body><main>Mutated</main></body></html>\n', 'utf8');
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=mutation',
  ]);
  assert(result.status !== 0, 'finish readiness accepted post-validation mutation');
  const parsed = parseToolJson(result);
  assert((parsed?.errors || []).some(error => String(error).includes('post-validation mutation detected')), 'post-validation mutation error was not reported');
}

function testFinishReadinessAssetHashTraversalMatchesWorkspaceLimit() {
  const dir = tempProject('finish-bounded-assets');
  const htmlPath = path.join(dir, 'pages/index.html');
  fs.writeFileSync(htmlPath, '<html><head></head><body><main>Valid</main></body></html>\n', 'utf8');
  let deepDir = path.join(dir, 'assets');
  for (let i = 0; i < 10; i += 1) {
    deepDir = path.join(deepDir, `d${i}`);
    fs.mkdirSync(deepDir, { recursive: true });
  }
  fs.writeFileSync(path.join(deepDir, 'deep.png'), 'not-a-real-png-but-hashed\n', 'utf8');
  writeJson(path.join(dir, 'validation-report.json'), {
    success: true,
    errors: [],
    checkedAt: '2026-07-14T00:05:00.000Z',
    projectFileHashes: {
      'colors_and_type.css': sha256File(path.join(dir, 'colors_and_type.css')),
      'pages/index.html': sha256File(htmlPath),
    },
    validationRunDisciplineStatus: { validationHistoryCount: 0, repairLedgerCount: 0 },
    skillProvenance: { name: 'solo-design', version: currentSkillVersion() },
    renderBlockingErrorCount: 0,
    errorCount: 0,
    designDir: dir,
  });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=mutation',
  ]);
  assert(result.status === 0, `finish readiness collected assets outside workspace hash limit: ${result.stderr || result.stdout}`);
}

function testValidationBudgetExhaustionIsTerminal() {
  const dir = tempProject('validation-budget-terminal');
  const summary = baseSummary([], {
    validationRunDiscipline: {
      maxFullValidationRuns: 2,
      softWarningsTriggerRepair: false,
      blockingRepairMode: 'targeted-once',
    },
    validationHistory: [
      { reportPath: 'validation-report.json', reportHash: 'a', success: false, exitCode: 1, checkedAt: '2026-07-14T00:00:00.000Z' },
      { reportPath: 'validation-report.json', reportHash: 'b', success: false, exitCode: 1, checkedAt: '2026-07-14T00:01:00.000Z' },
      { reportPath: 'validation-report.json', reportHash: 'c', success: false, exitCode: 1, checkedAt: '2026-07-14T00:02:00.000Z' },
    ],
  });
  summary.skillProvenance.version = currentSkillVersion();
  writeSummary(dir, summary);
  const reportPath = path.join(dir, 'validation-report.json');
  const result = runNode([
    toolPath('validate-design-workspace.mjs'),
    dir,
    `--report-json=${reportPath}`,
  ]);
  assert(result.status !== 0, 'workspace validator exited 0 after validation budget was exhausted');
  const report = readJson(reportPath);
  assert(report.success === false, 'validation budget exhaustion report must not be success=true');
  assert(report.terminalState === 'validation-budget-exhausted', 'validation budget exhaustion terminalState was not written');
  assert(report.outcome === 'terminal_stop', 'terminal validation report did not set outcome=terminal_stop');
  assert(report.repairable === false, 'terminal validation report must be repairable=false');
  assert(report.nextCheck?.type === 'stop' && report.nextCheck?.command === null, 'terminal validation report did not instruct stop');
  assert(Array.isArray(report.repairActionTable) && report.repairActionTable.length === 0, 'terminal validation report should not produce repair actions');
  assert(Array.isArray(report.repairContextPacket?.repairActionTable) && report.repairContextPacket.repairActionTable.length === 0, 'terminal repairContextPacket should not produce repair actions');
  assert(!String(result.stdout || '').includes('REPAIR_SCOPE_REMAINING: 1'), 'terminal stdout still advertises remaining repair scope');
  assert(!String(result.stdout || '').includes('follow repair state machine'), 'terminal stdout still points to repair state machine');
}

function testBuildManifestExcludesValidatorOwnedHashes() {
  const dir = tempProject('manifest-validator-owned-hashes');
  fs.writeFileSync(path.join(dir, 'pages/index.html'), '<html><head></head><body><main>Ready</main></body></html>\n', 'utf8');
  fs.writeFileSync(path.join(dir, 'validation-report.json'), '{"success":false}\n', 'utf8');
  fs.writeFileSync(path.join(dir, 'finish-readiness-report.json'), '{"success":true}\n', 'utf8');
  fs.writeFileSync(path.join(dir, 'page-generation-summary.json'), '{"ok":true}\n', 'utf8');
  writeJson(path.join(dir, 'project.design'), { data: [pageNode('page-index', 'pages/index.html', 'Index')] });
  writeSummary(dir, baseSummary([
    { nodeId: 'page-index', htmlSrc: 'pages/index.html', title: 'Index' },
  ]));

  const result = runBuildManifest(dir);
  assert(result.status === 0, `build manifest failed: ${result.stderr || result.stdout}`);
  const summary = readJson(path.join(dir, 'runtime-orchestration-summary.json'));
  const hashes = summary.project.dispatchPreflightManifest?.[0]?.preDispatchFileHashes || {};
  assert(Object.prototype.hasOwnProperty.call(hashes, 'project.design'), 'preDispatchFileHashes should still include .design files');
  assert(!Object.prototype.hasOwnProperty.call(hashes, 'validation-report.json'), 'preDispatchFileHashes must not include validation-report.json');
  assert(!Object.prototype.hasOwnProperty.call(hashes, 'finish-readiness-report.json'), 'preDispatchFileHashes must not include finish-readiness-report.json');
  assert(!Object.prototype.hasOwnProperty.call(hashes, 'page-generation-summary.json'), 'preDispatchFileHashes must not include page-generation-summary.json');
}

function testWorkspaceIgnoresLegacyValidatorOwnedDispatchHashes() {
  const dir = tempProject('legacy-validator-owned-hash');
  fs.writeFileSync(path.join(dir, 'validation-report.json'), 'changed-after-dispatch\n', 'utf8');
  const summary = laneSummary([
    {
      nodeId: 'page-index',
      status: 'completed',
      changedFiles: ['pages/index.html'],
      toolCallLedger: {
        source: 'main-agent-runtime-trace',
        traceDigest: 'abcdef1234567890',
        todoWriteCalls: 0,
        previewCalls: 0,
        validationScriptCalls: 0,
        helperScriptWrites: 0,
      },
    },
  ]);
  summary.project.dispatchPreflightManifest[0].preDispatchFileHashes = {
    'validation-report.json': 'legacy-stale-hash',
  };
  writeSummary(dir, summary);
  const reportPath = path.join(dir, 'validation-report.json');
  const result = runNode([
    toolPath('validate-design-workspace.mjs'),
    dir,
    '--check=dispatch-discipline',
    `--report-json=${reportPath}`,
  ]);
  assert(result.status === 0, `legacy validator-owned preDispatch hash was not ignored: ${result.stderr || result.stdout}`);
}

function testRecordDispatchCompletionWritesSafeEvidence() {
  const dir = tempProject('record-dispatch-completion');
  writeJson(path.join(dir, 'project.design'), { data: [pageNode('page-index', 'pages/index.html', 'Index')] });
  writeSummary(dir, laneSummary([]));
  const result = runNode([
    toolPath('record-dispatch-completion.mjs'),
    dir,
    '--node-id=page-index',
    '--status=completed',
    '--changed-files=pages/index.html',
    '--trace-digest=abcdef1234567890',
    '--tool-ledger-json={"todoWriteCalls":0,"previewCalls":0,"validationScriptCalls":0,"helperScriptWrites":0}',
    '--main-agent-mutation=pages/index.html:registered interaction metadata',
    '--json',
  ]);
  assert(result.status === 0, `record-dispatch-completion failed: ${result.stderr || result.stdout}`);
  const summary = readJson(path.join(dir, 'runtime-orchestration-summary.json'));
  const row = summary.project.expectedDispatches?.[0];
  assert(row?.nodeId === 'page-index', 'expectedDispatches[] row was not written');
  assert(row?.packetType === 'FreePagePacket', 'expectedDispatches[] row did not preserve manifest packetType');
  assert(row?.toolCallLedger?.source === 'main-agent-runtime-trace', 'toolCallLedger source was not normalized');
  assert(row?.toolCallLedger?.traceDigest === 'abcdef1234567890', 'traceDigest was not preserved');
  assert(Array.isArray(summary.project.mainAgentPostDispatchMutations), 'mainAgentPostDispatchMutations[] was not initialized');
  assert(summary.project.mainAgentPostDispatchMutations[0]?.path === 'pages/index.html', 'main-agent mutation path was not recorded');
}

function testRecordDispatchCompletionRejectsFakeOrForbiddenEvidence() {
  const dir = tempProject('record-dispatch-reject');
  writeJson(path.join(dir, 'project.design'), { data: [pageNode('page-index', 'pages/index.html', 'Index')] });
  writeSummary(dir, laneSummary([]));
  let result = runNode([
    toolPath('record-dispatch-completion.mjs'),
    dir,
    '--node-id=page-index',
    '--status=completed',
    '--changed-files=pages/index.html',
    '--trace-digest=<sub-agent-run-trace-hash>',
    '--tool-ledger-json={"todoWriteCalls":0,"previewCalls":0,"validationScriptCalls":0,"helperScriptWrites":0}',
  ]);
  assert(result.status !== 0, 'record-dispatch-completion accepted placeholder traceDigest');

  result = runNode([
    toolPath('record-dispatch-completion.mjs'),
    dir,
    '--node-id=page-index',
    '--status=completed',
    '--changed-files=validation-report.json',
    '--trace-digest=abcdef1234567890',
    '--tool-ledger-json={"todoWriteCalls":0,"previewCalls":0,"validationScriptCalls":0,"helperScriptWrites":0}',
  ]);
  assert(result.status !== 0, 'record-dispatch-completion accepted validator-owned changedFiles[]');

  result = runNode([
    toolPath('record-dispatch-completion.mjs'),
    dir,
    '--node-id=page-index',
    '--status=completed',
    '--changed-files=pages/../runtime-orchestration-summary.json',
    '--trace-digest=abcdef1234567890',
    '--tool-ledger-json={"todoWriteCalls":0,"previewCalls":0,"validationScriptCalls":0,"helperScriptWrites":0}',
  ]);
  assert(result.status !== 0, 'record-dispatch-completion accepted a changedFiles traversal path');

  result = runNode([
    toolPath('record-dispatch-completion.mjs'),
    dir,
    '--node-id=page-index',
    '--status=completed',
    '--changed-files=pages/index.html',
    '--trace-digest=abcdef1234567890',
    '--tool-ledger-json={"todoWriteCalls":0,"previewCalls":0,"validationScriptCalls":0,"helperScriptWrites":0}',
    '--main-agent-mutation=validation-report.json:fake mutation',
  ]);
  assert(result.status !== 0, 'record-dispatch-completion accepted validator-owned mutation path');
  const summary = readJson(path.join(dir, 'runtime-orchestration-summary.json'));
  assert(!Array.isArray(summary.project.expectedDispatches) || summary.project.expectedDispatches.length === 0, 'failed dispatch recording mutated expectedDispatches[]');
}

function testRecordDispatchCompletionRejectsDesignRegistrationMismatch() {
  const dir = tempProject('record-dispatch-registration-mismatch');
  writeJson(path.join(dir, 'project.design'), { data: [pageNode('page-other', 'pages/other.html', 'Other')] });
  writeSummary(dir, laneSummary([]));
  const result = runNode([
    toolPath('record-dispatch-completion.mjs'),
    dir,
    '--node-id=page-index',
    '--status=completed',
    '--changed-files=pages/index.html',
    '--trace-digest=abcdef1234567890',
    '--tool-ledger-json={"todoWriteCalls":0,"previewCalls":0,"validationScriptCalls":0,"helperScriptWrites":0}',
  ]);
  assert(result.status !== 0, 'record-dispatch-completion accepted a nodeId missing from .design');
  assert(String(result.stderr || result.stdout).includes('not registered in .design'), 'design registration mismatch error was not reported');
  const summary = readJson(path.join(dir, 'runtime-orchestration-summary.json'));
  assert(!Array.isArray(summary.project.expectedDispatches) || summary.project.expectedDispatches.length === 0, 'failed design registration check mutated expectedDispatches[]');
}

function testRepeatedErrorSignatureBecomesTerminal() {
  const dir = tempProject('repeated-error-terminal');
  const summary = laneSummary([]);
  summary.project.expectedDispatches = [];
  writeSummary(dir, summary);
  const reportPath = path.join(dir, 'validation-report.json');
  let result = runNode([
    toolPath('validate-design-workspace.mjs'),
    dir,
    '--check=dispatch-discipline',
    `--report-json=${reportPath}`,
  ]);
  assert(result.status !== 0, 'initial dispatch error unexpectedly passed');
  const firstReport = readJson(reportPath);
  const signatureRow = firstReport.errorSignatures?.[0];
  assert(signatureRow?.signature, 'initial dispatch error did not write errorSignatures[]');

  summary.project.validationHistory = [
    {
      reportPath: 'validation-report.json',
      reportHash: 'a',
      success: false,
      exitCode: 1,
      checkedAt: '2026-07-14T00:00:00.000Z',
      errorSignatures: [signatureRow],
    },
    {
      reportPath: 'validation-report.json',
      reportHash: 'b',
      success: false,
      exitCode: 1,
      checkedAt: '2026-07-14T00:01:00.000Z',
      errorSignatures: [signatureRow],
    },
  ];
  writeSummary(dir, summary);
  result = runNode([
    toolPath('validate-design-workspace.mjs'),
    dir,
    '--check=dispatch-discipline',
    `--report-json=${reportPath}`,
  ]);
  assert(result.status !== 0, 'repeated dispatch error unexpectedly passed');
  const report = readJson(reportPath);
  assert(report.terminalState === 'repeated-error-non-convergent', 'repeated same-error did not become terminal');
  assert(report.repairable === false, 'repeated same-error terminal report must be repairable=false');
  assert(Array.isArray(report.repairActionTable) && report.repairActionTable.length === 0, 'repeated same-error terminal report produced repair actions');
}

function testFinishReadinessRejectsTerminalValidationReport() {
  const dir = tempProject('finish-terminal-report');
  const htmlPath = path.join(dir, 'pages/index.html');
  fs.writeFileSync(htmlPath, '<html><head></head><body><main>Valid</main></body></html>\n', 'utf8');
  writeJson(path.join(dir, 'validation-report.json'), {
    success: true,
    terminalState: 'validation-budget-exhausted',
    errors: [],
    checkedAt: '2026-07-14T00:05:00.000Z',
    projectFileHashes: { 'pages/index.html': sha256File(htmlPath) },
    validationRunDisciplineStatus: { validationHistoryCount: 3, repairLedgerCount: 0 },
    skillProvenance: { name: 'solo-design', version: currentSkillVersion() },
    renderBlockingErrorCount: 0,
    errorCount: 0,
    designDir: dir,
  });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=mutation',
  ]);
  assert(result.status !== 0, 'finish readiness accepted terminal validation report');
  const parsed = parseToolJson(result);
  assert((parsed?.errors || []).some(error => String(error).includes('terminalState')), 'terminal report error was not reported');
}

function testFinishReadinessRejectsMismatchedDesignDirReport() {
  const dir = tempProject('finish-mismatched-designdir');
  const htmlPath = path.join(dir, 'pages/index.html');
  fs.writeFileSync(htmlPath, '<html><head></head><body><main>Valid</main></body></html>\n', 'utf8');
  writeJson(path.join(dir, 'validation-report.json'), {
    success: true,
    errors: [],
    checkedAt: '2026-07-14T00:05:00.000Z',
    projectFileHashes: { 'pages/index.html': sha256File(htmlPath) },
    validationRunDisciplineStatus: { validationHistoryCount: 0, repairLedgerCount: 0 },
    skillProvenance: { name: 'solo-design', version: currentSkillVersion() },
    renderBlockingErrorCount: 0,
    errorCount: 0,
    designDir: path.dirname(dir),
  });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=mutation',
  ]);
  assert(result.status !== 0, 'finish readiness accepted validation report from a different designDir');
  const parsed = parseToolJson(result);
  assert((parsed?.errors || []).some(error => String(error).includes('designDir does not match')), 'mismatched designDir error was not reported');
}

function testFinishReadinessMatchesRepairLedgerByHash() {
  const dir = tempProject('finish-ledger-hash');
  const validationReportPath = path.join(dir, 'validation-report.json');
  writeJson(validationReportPath, { success: true, errors: [], checkedAt: '2026-07-14T00:05:00.000Z' });
  const revalidationReportHash = sha256File(validationReportPath);
  writeSummary(dir, {
    schemaVersion: '1.0',
    project: {
      validationHistory: [
        {
          reportPath: 'validation-report.json',
          reportHash: 'failed-report-hash-1',
          success: false,
          exitCode: 1,
          checkedAt: '2026-07-14T00:00:00.000Z',
        },
        {
          reportPath: 'validation-report.json',
          reportHash: 'failed-report-hash-2',
          success: false,
          exitCode: 1,
          checkedAt: '2026-07-14T00:03:00.000Z',
        },
      ],
      validationRepairLedger: [
        {
          failedReportPath: 'validation-report.json',
          failedReportHash: 'failed-report-hash-1',
          repairWorkflowReadPath: 'intent-workflows/intent-project-mutation/main-agent-repair-workflow.md',
          repairStartedAt: '2026-07-14T00:01:00.000Z',
          ownerTriage: [{}],
          repairActions: [{}],
          revalidationReportPath: 'validation-report.json',
          revalidationReportHash,
          revalidationSuccess: true,
        },
        {
          failedReportPath: 'validation-report.json',
          failedReportHash: 'failed-report-hash-2',
          repairWorkflowReadPath: 'intent-workflows/intent-project-mutation/main-agent-repair-workflow.md',
          repairStartedAt: '2026-07-14T00:04:00.000Z',
          ownerTriage: [{}],
          repairActions: [{}],
          revalidationReportPath: 'validation-report.json',
          revalidationReportHash,
          revalidationSuccess: true,
        },
      ],
      repairEntryEvidence: [
        { failedReportPath: 'validation-report.json', failedReportHash: 'failed-report-hash-1' },
        { failedReportPath: 'validation-report.json', failedReportHash: 'failed-report-hash-2' },
      ],
    },
  });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=repair-ledger',
  ]);
  assert(result.status === 0, `finish readiness matched same-path ledger by path instead of hash: ${result.stderr || result.stdout}`);
}

function testFinishReadinessRejectsMissingHashMatchedRepairLedger() {
  const dir = tempProject('finish-ledger-missing-hash-match');
  const validationReportPath = path.join(dir, 'validation-report.json');
  writeJson(validationReportPath, { success: true, errors: [], checkedAt: '2026-07-14T00:05:00.000Z' });
  const revalidationReportHash = sha256File(validationReportPath);
  writeSummary(dir, {
    schemaVersion: '1.0',
    project: {
      validationHistory: [
        {
          reportPath: 'validation-report.json',
          reportHash: 'failed-report-hash-1',
          success: false,
          exitCode: 1,
          checkedAt: '2026-07-14T00:00:00.000Z',
        },
        {
          reportPath: 'validation-report.json',
          reportHash: 'failed-report-hash-2',
          success: false,
          exitCode: 1,
          checkedAt: '2026-07-14T00:03:00.000Z',
        },
      ],
      validationRepairLedger: [
        {
          failedReportPath: 'validation-report.json',
          failedReportHash: 'failed-report-hash-1',
          repairWorkflowReadPath: 'intent-workflows/intent-project-mutation/main-agent-repair-workflow.md',
          repairStartedAt: '2026-07-14T00:01:00.000Z',
          ownerTriage: [{}],
          repairActions: [{}],
          revalidationReportPath: 'validation-report.json',
          revalidationReportHash,
          revalidationSuccess: true,
        },
        {
          failedReportPath: 'validation-report.json',
          failedReportHash: 'different-failed-report-hash',
          repairWorkflowReadPath: 'intent-workflows/intent-project-mutation/main-agent-repair-workflow.md',
          repairStartedAt: '2026-07-14T00:04:00.000Z',
          ownerTriage: [{}],
          repairActions: [{}],
          revalidationReportPath: 'validation-report.json',
          revalidationReportHash,
          revalidationSuccess: true,
        },
      ],
      repairEntryEvidence: [
        { failedReportPath: 'validation-report.json', failedReportHash: 'failed-report-hash-1' },
        { failedReportPath: 'validation-report.json', failedReportHash: 'different-failed-report-hash' },
      ],
    },
  });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=repair-ledger',
  ]);
  assert(result.status !== 0, 'finish readiness accepted failed validation history without hash-matched ledger');
  const parsed = parseToolJson(result);
  assert((parsed?.errors || []).some(error => String(error).includes('has no matching validationRepairLedger entry')), 'missing hash-matched ledger error was not reported');
}

function testFinishReadinessRejectsSuccessfulHistoryAsFailedReportHash() {
  const dir = tempProject('finish-ledger-successful-failed-hash');
  const validationReportPath = path.join(dir, 'validation-report.json');
  writeJson(validationReportPath, { success: true, errors: [], checkedAt: '2026-07-14T00:05:00.000Z' });
  const successfulReportHash = sha256File(validationReportPath);
  writeSummary(dir, {
    schemaVersion: '1.0',
    project: {
      validationHistory: [
        {
          reportPath: 'validation-report.json',
          reportHash: 'unrelated-failed-report-hash',
          success: false,
          exitCode: 1,
          checkedAt: '2026-07-14T00:00:00.000Z',
        },
        {
          reportPath: 'validation-report.json',
          reportHash: successfulReportHash,
          success: true,
          exitCode: 0,
          checkedAt: '2026-07-14T00:01:00.000Z',
        },
      ],
      validationRepairLedger: [
        {
          failedReportPath: 'validation-report.json',
          failedReportHash: successfulReportHash,
          repairWorkflowReadPath: 'intent-workflows/intent-project-mutation/main-agent-repair-workflow.md',
          repairStartedAt: '2026-07-14T00:02:00.000Z',
          ownerTriage: [{}],
          repairActions: [{}],
          revalidationReportPath: 'validation-report.json',
          revalidationReportHash: successfulReportHash,
          revalidationSuccess: true,
        },
      ],
      repairEntryEvidence: [
        { failedReportPath: 'validation-report.json', failedReportHash: successfulReportHash },
      ],
    },
  });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=repair-ledger',
  ]);
  assert(result.status !== 0, 'finish readiness accepted a failedReportHash that points to successful validationHistory');
  const parsed = parseToolJson(result);
  assert((parsed?.errors || []).some(error => String(error).includes('does not reference a failed validationHistory record')), 'successful-history failedReportHash error was not reported');
}

function testFinishReadinessChecksMissingRevalidationHistorySuccess() {
  const dir = tempProject('finish-ledger-missing-revalidation-success');
  const validationReportPath = path.join(dir, 'validation-report.json');
  writeJson(validationReportPath, { success: true, errors: [], checkedAt: '2026-07-14T00:05:00.000Z' });
  const failedHash = 'failed-report-hash-1';
  const missingRevalidationHash = 'missing-revalidation-report-hash';
  writeSummary(dir, {
    schemaVersion: '1.0',
    project: {
      validationHistory: [
        {
          reportPath: 'validation-report.json',
          reportHash: failedHash,
          success: false,
          exitCode: 1,
          checkedAt: '2026-07-14T00:00:00.000Z',
        },
        {
          reportPath: 'missing-revalidation-report.json',
          reportHash: missingRevalidationHash,
          success: false,
          exitCode: 1,
          checkedAt: '2026-07-14T00:01:00.000Z',
        },
      ],
      validationRepairLedger: [
        {
          failedReportPath: 'validation-report.json',
          failedReportHash: failedHash,
          repairWorkflowReadPath: 'intent-workflows/intent-project-mutation/main-agent-repair-workflow.md',
          repairStartedAt: '2026-07-14T00:00:30.000Z',
          ownerTriage: [{}],
          repairActions: [{}],
          revalidationReportPath: 'missing-revalidation-report.json',
          revalidationReportHash: missingRevalidationHash,
          revalidationSuccess: true,
        },
      ],
      repairEntryEvidence: [
        { failedReportPath: 'validation-report.json', failedReportHash: failedHash },
      ],
    },
  });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=repair-ledger',
  ]);
  assert(result.status !== 0, 'finish readiness accepted missing revalidation report with contradictory history success');
  const parsed = parseToolJson(result);
  assert((parsed?.errors || []).some(error => String(error).includes('validationHistory report success=false')), 'missing revalidation history success mismatch was not reported');
}

function testWorkspaceRepairLedgerSourceChecksFailedAndMissingRevalidationHistory() {
  const source = fs.readFileSync(toolPath('validate-design-workspace.mjs'), 'utf8');
  assert(source.includes('isFailedHistoryRecord'), 'workspace repair ledger must distinguish failed validationHistory records');
  assert(source.includes('failedReportHash does not reference a failed validationHistory record'), 'workspace repair ledger must reject failedReportHash that points to non-failed history');
  assert(source.includes("result.status === 'missing' && revalidationHistory && revalidationHistory.success !== item.revalidationSuccess"), 'workspace repair ledger must compare missing revalidation report against history success');
  assert(source.includes('ledgerDiagnosticReports'), 'workspace repair ledger must preserve diagnostic report evidence after current report overwrite');
  assert(source.includes('findDiagnosticRecord'), 'workspace repair ledger must resolve diagnostic report evidence by path and hash');
}

function testFinishReadinessAcceptsOverwrittenRevalidationReportWithHistoryHash() {
  const dir = tempProject('finish-ledger-overwritten-report');
  const validationReportPath = path.join(dir, 'validation-report.json');
  writeJson(validationReportPath, { success: true, errors: [], checkedAt: '2026-07-14T00:01:00.000Z' });
  const originalRevalidationHash = sha256File(validationReportPath);
  writeJson(validationReportPath, { success: true, errors: [], warnings: ['later run'], checkedAt: '2026-07-14T00:03:00.000Z' });

  writeSummary(dir, {
    schemaVersion: '1.0',
    project: {
      validationHistory: [
        {
          reportPath: 'validation-report.json',
          reportHash: 'failed-report-hash-1',
          success: false,
          exitCode: 1,
          checkedAt: '2026-07-14T00:00:00.000Z',
        },
        {
          reportPath: 'validation-report.json',
          reportHash: originalRevalidationHash,
          success: true,
          exitCode: 0,
          checkedAt: '2026-07-14T00:01:00.000Z',
        },
      ],
      validationRepairLedger: [
        {
          failedReportPath: 'validation-report.json',
          failedReportHash: 'failed-report-hash-1',
          repairWorkflowReadPath: 'intent-workflows/intent-project-mutation/main-agent-repair-workflow.md',
          repairStartedAt: '2026-07-14T00:00:30.000Z',
          ownerTriage: [{}],
          repairActions: [{}],
          revalidationReportPath: 'validation-report.json',
          revalidationReportHash: originalRevalidationHash,
          revalidationSuccess: true,
        },
      ],
      repairEntryEvidence: [
        { failedReportPath: 'validation-report.json', failedReportHash: 'failed-report-hash-1' },
      ],
    },
  });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=repair-ledger',
  ]);
  assert(result.status === 0, `finish readiness rejected ledger evidence preserved in validationHistory after report overwrite: ${result.stderr || result.stdout}`);
}

function testFinishReadinessRejectsEvidenceClearedAfterValidationReport() {
  const dir = tempProject('finish-evidence-cleared-after-report');
  writeJson(path.join(dir, 'validation-report.json'), {
    success: true,
    errors: [],
    checkedAt: '2026-07-14T00:05:00.000Z',
    validationRunDisciplineStatus: {
      validationHistoryCount: 1,
      repairLedgerCount: 1,
    },
  });
  writeSummary(dir, {
    schemaVersion: '1.0',
    project: {
      validationHistory: [],
      validationRepairLedger: [],
      repairEntryEvidence: [],
    },
  });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=all',
  ]);
  assert(result.status !== 0, 'finish readiness accepted evidence cleared after validation report');
  const parsed = parseToolJson(result);
  assert((parsed?.errors || []).some(error => String(error).includes('validationHistory[] was reduced')), 'cleared validationHistory error was not reported');
}

function testGraphicProjectFileHashKeysUseForwardSlashes() {
  const source = fs.readFileSync(toolPath('validate-graphic-asset-design.mjs'), 'utf8');
  assert(source.includes("relPaths.push(relPath.replace(/\\\\/g, '/'))"), 'graphic projectFileHashes keys must normalize path separators to forward slashes');
  assert(source.includes('return [relPath, await hashFile(filePath, relPath)]'), 'graphic projectFileHashes must hash and write normalized keys');
}

function testFinishReadinessInvalidJsonStructuredError() {
  const dir = tempProject('finish-invalid-json');
  fs.writeFileSync(path.join(dir, 'validation-report.json'), '{ invalid json', 'utf8');
  writeSummary(dir, { schemaVersion: '1.0', project: {} });
  const result = runNode([
    toolPath('validate-finish-readiness.mjs'),
    dir,
    '--check=all',
  ]);
  assert(result.status !== 0, 'finish readiness accepted invalid validation-report.json');
  const parsed = parseToolJson(result);
  assert((parsed?.errors || []).some(error => String(error).includes('validation-report.json is invalid JSON')), 'invalid JSON was not reported as structured error');
}

function testVersionFormatGate() {
  let result = runNode([
    toolPath('bump-skill-release-version.mjs'),
    '--version=2026.07.14.12.34.56',
    '--dry-run',
    '--json',
  ]);
  assert(result.status === 0, `valid dotted timestamp version was rejected: ${result.stderr || result.stdout}`);
  result = runNode([
    toolPath('bump-skill-release-version.mjs'),
    '--version=07141600',
    '--dry-run',
    '--json',
  ]);
  assert(result.status !== 0, 'MMddHHmm version was accepted');
}

function testPerformanceSensitiveToolingUsesBoundedAsyncIo() {
  const readScopeSource = fs.readFileSync(toolPath('check-skill-runtime-read-scope.mjs'), 'utf8');
  assert(readScopeSource.includes('await mapLimit(files, 16'), 'check-skill-runtime-read-scope must use bounded parallel reads');
  assert(readScopeSource.includes('fs.promises.readFile'), 'check-skill-runtime-read-scope must avoid serial readFileSync over all skill files');

  const graphicSource = fs.readFileSync(toolPath('validate-graphic-asset-design.mjs'), 'utf8');
  assert(graphicSource.includes('async function collectProjectFileHashes'), 'graphic validator project hash collection must be async');
  assert(graphicSource.includes('await mapLimit(relPaths, 8'), 'graphic validator project hashes must use bounded concurrency');
  assert(graphicSource.includes('fs.promises.open'), 'graphic validator project hashes must use async file reads');
    assert(graphicSource.includes('MAX_PROJECT_HASH_ASSET_DEPTH'), 'graphic validator asset hash traversal must be depth bounded');
    assert(graphicSource.includes('assetEntryCount >= MAX_PROJECT_HASH_ASSET_ENTRIES'), 'graphic validator asset hash traversal must be count bounded');
    assert(!graphicSource.includes('addIfExists(rel);'), 'graphic validator must not restat assets already identified by Dirent.isFile()');

    const finishSource = fs.readFileSync(toolPath('validate-finish-readiness.mjs'), 'utf8');
    assert(finishSource.includes('MAX_PROJECT_HASH_ASSET_DEPTH'), 'finish readiness asset traversal must be depth bounded');
    assert(finishSource.includes('maxEntries: MAX_PROJECT_HASH_ASSET_ENTRIES'), 'finish readiness artifact asset collection must use the workspace hash count limit');
    assert(!finishSource.includes('addIfExists(rel);'), 'finish readiness must not restat assets already identified by Dirent.isFile()');

  const bumpSource = fs.readFileSync(toolPath('bump-skill-release-version.mjs'), 'utf8');
  assert(bumpSource.includes("shell: process.platform === 'win32'"), 'bump-skill-release-version must allow git .cmd resolution on Windows');
  assert(bumpSource.includes('listSkillFiles(SKILL_DIR)'), 'cloud release bump must scan the single distributed Skill directory');
  assert(!bumpSource.includes('const PLATFORMS'), 'cloud release bump must not depend on platform mirror directories');

  const interactionSource = fs.readFileSync(toolPath('check-interaction-domids.mjs'), 'utf8');
  assert(interactionSource.includes('await mapLimit(pages, 8'), 'check-interaction-domids must read independent pages with bounded concurrency');
  assert(interactionSource.includes('fs.promises.readFile'), 'check-interaction-domids must avoid serial readFileSync for page HTML');

  const buildManifestSource = fs.readFileSync(toolPath('build-page-dispatch-manifest.mjs'), 'utf8');
  assert(buildManifestSource.includes('async function collectPreDispatchFileHashes'), 'dispatch manifest pre-dispatch hashes must be async');
  assert(buildManifestSource.includes('await mapLimit(designFiles, 8'), 'dispatch manifest design file hashes must use bounded concurrency');
  assert(buildManifestSource.includes('mapLimit(pageInputs, 8'), 'dispatch manifest page HTML reads must use bounded concurrency');

  const workflowBoundarySource = fs.readFileSync(toolPath('check-intent-workflow-boundaries.mjs'), 'utf8');
  assert(workflowBoundarySource.includes('await mapLimit(markdownFiles, 16'), 'intent workflow boundary scan must use bounded concurrent reads');
  assert(workflowBoundarySource.includes('fs.promises.readFile'), 'intent workflow boundary scan must avoid serial readFileSync');

  const workspaceSource = fs.readFileSync(toolPath('validate-design-workspace.mjs'), 'utf8');
  assert(
    workspaceSource.includes("fs.readdirSync(assetsDir, { withFileTypes: true })"),
    'workspace assets coverage must use Dirent metadata'
  );
  assert(!workspaceSource.includes('fs.statSync(fullPath).isDirectory()'), 'workspace assets coverage must not stat every Dirent');
}

function testCloudSotHasNoPlatformMirrorTools() {
  assert(!fs.existsSync(toolPath('sync-skill-platforms.mjs')), 'cloud Skill must not ship platform sync tooling');
  assert(!fs.existsSync(toolPath('check-builtin-skill-sync.mjs')), 'cloud Skill must not ship platform mirror checks');
}

const tests = [
  testBuildManifestDevMetadataAndPrefixless,
  testValidateDesignFileFormatMultiFileDoesNotApplyBatchExpectedPagesPerFile,
  testRestoreFinishReadinessAllRequiresResponseDraft,
  testBuildManifestAcceptsProvidedImagePathForImageUrlRestore,
  testReplaceHeadAddsMissingThemeClass,
  testReplaceHeadPreservesExistingThemeWithoutExplicitFlag,
  testValidateDesignFileAcceptsSingleQuotedDomId,
  testInteractionDomIdCheckerReadsMultiplePages,
  testLaneContractSkipsDeprecatedRestoreEvidenceForCurrentVersion,
  testWorkspaceAcceptsProvidedImagePathForImageUrlRestore,
  testGraphicValidatorRejectsFalsyJsonRoots,
  testRestoreNextCheckUsesCompleteGate,
  testWorkspaceNextCheckUsesCompleteGateForHtmlPageWorkflows,
  testWorkspaceValidatorAcceptsTargetPageIdAlias,
  testWorkspaceProjectFileHashKeysUseForwardSlashes,
  testWorkspaceRejectsDispatchTraversalPath,
  testBuildManifestRejectsEscapes,
  testBuildManifestRejectsAllowedWriteEscapes,
  testLaneContractNodeIdAndAllowedDirectory,
  testLaneContractNotRequiredNoChangedFiles,
  testRepairLedgerSamePathNewHashCreatesEntry,
  testRepairLedgerOnlyRevalidationDoesNotCreateCascadingHistory,
  testRecordRepairActionDoesNotRequireAgentHashes,
  testRecordRepairActionRejectsEscapingAffectedFiles,
  testFinishReadinessIgnoresRepairActionHashes,
  testFinishReadinessRejectsIncompleteValidationReport,
  testPostValidationMutationStillFails,
  testFinishReadinessAssetHashTraversalMatchesWorkspaceLimit,
  testValidationBudgetExhaustionIsTerminal,
  testBuildManifestExcludesValidatorOwnedHashes,
  testWorkspaceIgnoresLegacyValidatorOwnedDispatchHashes,
  testRecordDispatchCompletionWritesSafeEvidence,
  testRecordDispatchCompletionRejectsFakeOrForbiddenEvidence,
  testRecordDispatchCompletionRejectsDesignRegistrationMismatch,
  testRepeatedErrorSignatureBecomesTerminal,
  testFinishReadinessRejectsTerminalValidationReport,
  testFinishReadinessRejectsMismatchedDesignDirReport,
  testFinishReadinessChecksMissingRevalidationHistorySuccess,
  testWorkspaceRepairLedgerSourceChecksFailedAndMissingRevalidationHistory,
  testFinishReadinessAcceptsOverwrittenRevalidationReportWithHistoryHash,
  testFinishReadinessRejectsEvidenceClearedAfterValidationReport,
  testGraphicProjectFileHashKeysUseForwardSlashes,
  testFinishReadinessInvalidJsonStructuredError,
  testVersionFormatGate,
  testPerformanceSensitiveToolingUsesBoundedAsyncIo,
  testCloudSotHasNoPlatformMirrorTools,
];

for (const test of tests) {
  try {
    test();
    console.log(`[PASS] ${test.name}`);
  } catch (error) {
    failures.push(`[FAIL] ${test.name}: ${error.message}`);
    console.error(failures[failures.length - 1]);
  }
}

if (failures.length > 0) {
  console.error(`\n${failures.length} solo-design contract regression(s) failed.`);
  process.exit(1);
}

console.log(`\nAll ${tests.length} solo-design contract regressions passed.`);
