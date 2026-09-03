#!/usr/bin/env node

/**
 * Validate an entire design project directory in one pass.
 *
 * Purpose: run a full validation of the design directory before presenting
 *          results to the user after the Agent task is complete.
 *
 * Usage: node validate-design-workspace.mjs <design-directory-path> [--expected-pages=<N>] [--require-interactions=domId1:file1.html,domId2:file2.html,...] [--report-json=<path>]
 *
 * Arguments:
 *   <design-directory-path>          : root path of the design project (required)
 *   --expected-pages=<N>             : expected total page count (optional; passed to .design validation if provided)
 *   --require-interactions=<entries> : comma-separated list of domId:htmlFile pairs (optional);
 *                                      passed to .design validation to verify each domId exists
 *                                      in the HTML file and is registered in .design interactions
 *   --report-json=<path>             : write machine-readable validation evidence JSON (optional)
 *
 * Checks:
 *   1. Directory structure (assets/, pages/ present)
 *   2. Discover and validate all .design files (--expected-pages forwarded automatically;
 *      includes cross-version reachability check 18 of validate-design-file-format.mjs)
 *   3. Validate HTML files in pages/
 *   4. Validate HTML infrastructure (Tailwind / theme-vars / icons)
 *   5. Validate Tailwind @apply rules (no local component class cross-references)
 *   6. Validate no custom <style> blocks in <head> beyond protected infrastructure
 *   7. Validate .theme files in theme/ (optional — no error if absent)
 *   8. Check that assets/ directory exists, and that every image file under
 *      assets/ (.jpg/.jpeg/.png/.gif/.webp/.svg) is registered as a
 *      type:"image" node in at least one .design file (reverse coverage)
 *   9. Validate runtime-orchestration-summary.json presence (warning when absent)
 *  10. Validate library-bound custom CSS constraints (when operatingMode=library-bound)
 *  11. Validate HTML quality rules (no hardcoded colors, no secondary/accent vars,
 *      image path validity, free-explore colors_and_type.css hue/radius/shadow rules)
 *  12. Validate WeChat Mini Program chrome rules (when miniProgramStyle is set)
 *  13. Validate restore_1to1 evidence completeness when restore mode is active
 *  14. Generate a full validation report
 *
 * Exit codes: 0 = passed, 1 = failed
 */

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

// script directory (fileURLToPath handles Windows drive letters and percent-encoded paths)
const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = path.resolve(SCRIPT_DIR, '..', '..');
const VALIDATE_DESIGN_SCRIPT = path.join(SCRIPT_DIR, 'validate-design-file-format.mjs');
const SKILL_MANIFEST_PATH = path.join(SKILL_DIR, 'skill-release-manifest.json');

const errors = [];
const warnings = [];
const repairPlanHints = [];
let terminalValidationState = null;
const MAX_PAGE_HTML_BYTES = 2 * 1024 * 1024;
const pageHtmlCache = new Map();
const pageHtmlReadErrors = new Set();
const fileHashCache = new Map();
const HASH_IMAGE_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']);
const MAX_PROJECT_HASH_ASSET_ENTRIES = 500;
const MAX_PROJECT_HASH_ASSET_DEPTH = 8;
const RESTORE_VISUAL_DIFF_STATUSES = new Set(['matched', 'partial', 'missing']);
const RESTORE_VISUAL_DIFF_SEVERITIES = new Set(['blocking', 'warning']);
const RESTORE_REQUIRED_DIMENSIONS = new Set([
  'layout',
  'color-rhythm',
  'typography',
  'component-proportion',
  'density',
  'fine-detail',
]);
const RESTORE_VALID_SOURCE_TYPES = new Set(['image', 'url', 'image+url']);
const RESTORE_REQUIRED_MEASURED_FACT_CATEGORIES = new Set([
  'viewport',
  'layout-region',
  'color-surface',
  'component-proportion',
  'density-spacing',
]);
const RESTORE_URL_LONG_PAGE_REGION_GROUPS = ['first-screen', 'middle-section', 'footer-bottom'];
const RESTORE_IMAGE_DEVICE_REGION_GROUPS = ['outer-frame', 'device-shell', 'inner-screen', 'primary-object'];
const RESTORE_MAX_FULL_VALIDATION_RUNS = 3;

function shellQuote(value) {
  if (process.platform === 'win32') {
    return `"${String(value).replace(/"/g, '\\"')}"`;
  }
  return `'${String(value).replace(/'/g, "'\\''")}'`;
}

function deterministicToolPath(fileName) {
  return path.join(SKILL_DIR, 'shared-runtime', 'deterministic-tooling', fileName);
}
const RESTORE_DIMENSION_GATE_VERSION = '2026.07.09.0';
const RESTORE_EVIDENCE_SKIP_VERSION = '2026.07.16.21';
const QUALITY_EFFICIENCY_GATE_VERSION = '2026.07.10.0';
const GRAPHIC_SOURCE_MATERIAL_COVERAGE = new Set(['complete', 'partial']);
const SUMMARY_MUTABLE_FIELDS = new Set([
  'artifactReadinessEvidence',
  'finishReadinessEvidence',
  'validationHistory',
  'validationRepairLedger',
  'lastValidationReportCheckedAt',
  'validationSnapshot',
  'repairEntryEvidence',
  'repairStopConditionMet',
  'repairStopReason',
  'remainingBlockingIssues',
  'lastValidationReportPath',
]);
const REPAIR_ACTION_TABLE = [
  {
    errorPattern: /head|theme-vars|tailwind|semantic-token|apply-html-head/i,
    errorClass: 'head-infrastructure',
    severity: 'blocking',
    action: 'run_apply_html_head_replace_once',
    owner: 'main-agent',
    sourceReadPolicy: 'no-validator-source-read',
  },
  {
    errorPattern: /dispatchPreflightManifest|mobile-navigation-dispatch|expectedDispatches|allowedWritePaths|changedFiles/i,
    errorClass: 'dispatch-preflight-or-ownership',
    severity: 'blocking',
    action: 'return_to_dispatch_preflight_gate',
    owner: 'main-agent',
    sourceReadPolicy: 'read summary and dispatch contract only',
  },
  {
    errorPattern: /restore|sourceAuthority|sourceFact|checkpoint|visualDiffReview|referenceCaptureEvidence/i,
    errorClass: 'restore-source-authority-or-checkpoint',
    severity: 'blocking',
    action: 'repair_only_matching_source_authority_or_checkpoint',
    owner: 'main-agent',
    sourceReadPolicy: 'read persisted source facts and checkpoint ledger only',
  },
  {
    errorPattern: /validationRepairLedger|repairEntryEvidence|repair stop condition/i,
    errorClass: 'repair-ledger',
    severity: 'blocking',
    action: 'append_repair_entry_evidence_and_revalidation_report',
    owner: 'main-agent',
    sourceReadPolicy: 'read validation report and repair workflow only',
  },
  {
    errorPattern: /\.design|htmlSrc|imageSrc|interaction|registered|asset exists|page exists/i,
    errorClass: 'artifact-readiness',
    severity: 'blocking',
    action: 'repair_design_registration_or_file_reference_only',
    owner: 'main-agent',
    sourceReadPolicy: 'read .design and affected file metadata only',
  },
  {
    errorPattern: /visualQualityCheckpoints|visual-anchor|information-hierarchy|composition-structure|implementation-strategy/i,
    errorClass: 'visual-checkpoint',
    severity: 'blocking',
    action: 'repair_only_the_failed_visual_checkpoint',
    owner: 'main-agent-or-page-owner',
    sourceReadPolicy: 'read checkpoint ledger and targeted page excerpt only',
  },
];

function addRepairPlanHint(errorClass, hint = {}) {
  const key = `${errorClass}:${(hint.affectedFiles || []).join('|')}:${hint.strategy || ''}`;
  if (repairPlanHints.some(item => item._key === key)) return;
  repairPlanHints.push({
    _key: key,
    errorClass,
    owner: hint.owner || 'main-agent',
    repairScope: hint.repairScope || null,
    strategy: hint.strategy || null,
    affectedFiles: hint.affectedFiles || [],
    repairReportPath: hint.repairReportPath || null,
    repairAlreadyAttempted: Boolean(hint.repairAlreadyAttempted),
    allowSourceRead: hint.allowSourceRead || 'targeted-excerpt-only',
    maxValidationRuns: hint.maxValidationRuns || 3
  });
}

function addError(loc, message) {
  errors.push(`[${loc}] ${message}`);
}

function addWarning(loc, message) {
  warnings.push(`[${loc}] ${message}`);
}

function printSection(title, char = '=') {
  console.log(char.repeat(60));
  console.log(title);
  console.log(char.repeat(60));
}

function validateDirectoryStructure(designDir) {
  console.log('\nChecking directory structure...');

  const expectedDirs = ['assets', 'pages'];
  for (const dir of expectedDirs) {
    const fullPath = path.join(designDir, dir);
    if (!fs.existsSync(fullPath)) {
      addError('directory-structure', `Missing required directory: ${dir}/`);
    } else {
      console.log(`  [OK] ${dir}/ directory found`);
    }
  }
}

function findDesignFiles(designDir) {
  console.log('\nLooking for .design files...');

  const designFiles = [];
  const items = fs.readdirSync(designDir);

  for (const item of items) {
    if (item.endsWith('.design')) {
      designFiles.push(item);
    }
  }

  if (designFiles.length === 0) {
    addError('design-files', 'No .design file found in the root directory');
  } else if (designFiles.length > 1) {
    addWarning('design-files', `Multiple .design files found: ${designFiles.join(', ')} (usually only one expected)`);
  } else {
    console.log(`  [OK] Found ${designFiles.length} .design file: ${designFiles[0]}`);
  }

  return designFiles;
}

function validateDesignFiles(designDir, designFiles, expectedPages, requireInteractions) {
  console.log('\nValidating .design files...');

  if (designFiles.length === 0) return;

  const args = [
    VALIDATE_DESIGN_SCRIPT,
    ...designFiles.map(designFile => path.join(designDir, designFile)),
  ];
  if (expectedPages !== undefined) {
    args.push(`--expected-pages=${expectedPages}`);
  }
  if (requireInteractions) {
    args.push(`--require-interactions=${requireInteractions}`);
  }

  try {
    console.log(`  - Validating ${designFiles.length} .design file(s)...`);
    execFileSync(process.execPath, args, {
      stdio: ['inherit', 'pipe', 'pipe'],
      encoding: 'utf8'
    });
    for (const designFile of designFiles) {
      console.log(`    [OK] ${designFile} validation passed`);
    }
  } catch (error) {
    const stderr = error.stderr || error.stdout || '';
    addError('design-file', `Validation failed for .design file batch: ${stderr}`);
  }
}

function validateHtmlFiles(designDir) {
  console.log('\nChecking HTML files...');

  const pagesDir = path.join(designDir, 'pages');

  if (!fs.existsSync(pagesDir)) {
    addError('html-files', 'pages/ directory not found, cannot check HTML files');
    return;
  }

  const htmlFiles = fs.readdirSync(pagesDir).filter(f => f.endsWith('.html'));

  if (htmlFiles.length === 0) {
    addWarning('html-files', 'No HTML files found in pages/ directory');
  } else {
    console.log(`  [OK] Found ${htmlFiles.length} HTML file(s)`);

    for (const htmlFile of htmlFiles) {
      const htmlPath = path.join(pagesDir, htmlFile);
      const content = readHtmlFileCached(htmlPath, htmlFile);
      if (content === null) continue;
      // basic length check
      if (content.length < 50) {
        addWarning('html-files', `HTML file seems too short: ${htmlFile}`);
      }
      // check basic structure tags
      if (!content.includes('<html') || !content.includes('<head') || !content.includes('<body')) {
        addError('html-files', `HTML file missing basic structure: ${htmlFile}`);
      } else {
        console.log(`    [OK] ${htmlFile} looks valid`);
      }
    }
  }
}

/**
 * Check that no @layer components class is referenced inside @apply.
 *
 * Tailwind browser runtime only accepts utility classes in @apply.
 * Referencing a locally-defined component class (e.g. `.section-shell { @apply panel-card ... }`)
 * causes "Cannot apply unknown utility class" at compile-time, which silently drops ALL styles on
 * that page — even if every other page is fine.
 *
 * Algorithm:
 *   1. Extract every <style type="text/tailwindcss"> block in the file.
 *   2. Collect all custom class names defined in that block (.foo { ... }).
 *   3. Scan every @apply token; strip variant prefixes (sm:, hover:, etc.).
 *   4. If the base token matches a custom class name → error.
 */
function validateTailwindApplyRules(designDir) {
  console.log('\nChecking Tailwind @apply rules (no local component class cross-references)...');

  const pagesDir = path.join(designDir, 'pages');
  if (!fs.existsSync(pagesDir)) return;

  const htmlFiles = fs.readdirSync(pagesDir).filter(f => f.endsWith('.html'));
  if (htmlFiles.length === 0) return;

  for (const htmlFile of htmlFiles) {
    const htmlPath = path.join(pagesDir, htmlFile);
    const content = readHtmlFileCached(htmlPath, htmlFile);
    if (content === null) continue;

    // Extract all <style type="text/tailwindcss"> blocks
    const tailwindStyleRegex = /<style[^>]*type=["']text\/tailwindcss["'][^>]*>([\s\S]*?)<\/style>/gi;
    let styleMatch;

    while ((styleMatch = tailwindStyleRegex.exec(content)) !== null) {
      const styleBlock = styleMatch[1];

      // Step 1: collect custom class names defined in this block (.foo { ... })
      const customClasses = new Set();
      const classDefRegex = /\.([a-zA-Z_][a-zA-Z0-9_-]*)\s*\{/g;
      let classMatch;
      while ((classMatch = classDefRegex.exec(styleBlock)) !== null) {
        customClasses.add(classMatch[1]);
      }
      if (customClasses.size === 0) continue;

      // Step 2: scan all @apply statements and check tokens
      const applyRegex = /@apply\s+([^;}{]+)/g;
      let applyMatch;
      while ((applyMatch = applyRegex.exec(styleBlock)) !== null) {
        const applyValue = applyMatch[1].trim();
        const tokens = applyValue.split(/\s+/).filter(t => t.length > 0);
        for (const token of tokens) {
          // Strip variant prefix (e.g. sm:p-5 → p-5, hover:bg-card → bg-card)
          const baseToken = token.includes(':') ? token.split(':').pop() : token;
          if (customClasses.has(baseToken)) {
            addError(
              'tailwind-apply',
              `${htmlFile}: @apply references local component class ".${baseToken}" — ` +
              `Tailwind will throw "Cannot apply unknown utility class \`${baseToken}\`", ` +
              `causing ALL styles on this page to be dropped. ` +
              `Fix: inline the constituent utilities directly instead of referencing the custom class name.`
            );
          }
        }
      }
    }
  }
}

// Required infrastructure markers in every HTML page.
// Missing any one of these causes styles / icons / theme to break.
const HTML_INFRA_CHECKS = [
  {
    id: 'tailwind-cdn',
    pattern: '@tailwindcss/browser@4',
    desc: 'Tailwind CSS CDN (<script src="...@tailwindcss/browser@4">)',
    consequence: 'all utility classes stop working; page degrades to unstyled HTML',
    owner: 'MAIN-AGENT',
  },
  {
    id: 'theme-vars',
    pattern: 'id="theme-vars"',
    desc: '<style id="theme-vars"> theme CSS variable block',
    consequence: 'all semantic token colors degrade to transparent/default values',
    owner: 'MAIN-AGENT',
  },
  {
    id: 'theme-inline',
    pattern: '@theme inline',
    desc: '@theme inline Tailwind <-> CSS variable bridge block',
    consequence: 'bg-primary, text-foreground and similar classes cannot map to theme colors',
    owner: 'MAIN-AGENT',
  },
  {
    id: 'layer-base',
    pattern: '@layer base',
    desc: '@layer base global base styles',
    consequence: 'body background color, font, table word-break and other base styles are lost',
    owner: 'MAIN-AGENT',
  },
  {
    id: 'lucide-init',
    pattern: 'lucide.createIcons()',
    condition: (html) => html.includes('data-lucide'),
    desc: 'lucide.createIcons() icon init script (required only when data-lucide is used)',
    consequence: 'all <i data-lucide> icons will not render',
    owner: 'SUB-AGENT',
  },
  {
    id: 'theme-class',
    pattern: /\bclass=["'][^"']*\b(?:light|dark)\b[^"']*["']/,
    desc: '<html class="light"> or <html class="dark"> theme mode selector',
    consequence: 'CSS variable selectors do not match; all theme colors stop working',
    owner: 'MAIN-AGENT',
  },
];

function validateHtmlInfrastructure(designDir) {
  console.log('\nChecking HTML infrastructure (Tailwind / theme / icons)...');

  const pagesDir = path.join(designDir, 'pages');
  if (!fs.existsSync(pagesDir)) {
    // pages/ dir absence is already reported by validateHtmlFiles; skip here
    return;
  }

  const htmlFiles = fs.readdirSync(pagesDir).filter(f => f.endsWith('.html'));
  if (htmlFiles.length === 0) return;

  const summary = loadOrchestrationSummary(designDir);
  // Only library-bound projects may downgrade a missing @theme inline bridge to a warning;
  // free-explore projects rely on the bridge equally, so absence stays an error.
  const hasDesignLibrary = summary?.designSource?.operatingMode === 'library-bound';

  for (const htmlFile of htmlFiles) {
    const htmlPath = path.join(pagesDir, htmlFile);
    const content = readHtmlFileCached(htmlPath, htmlFile);
    if (content === null) continue;

    const missing = HTML_INFRA_CHECKS.filter(({ id, pattern, condition }) => {
      if (condition && !condition(content)) return false;
      if (id === 'theme-class') {
        const htmlTag = (content.match(/<html\b[^>]*>/i) || [''])[0];
        if (!htmlTag) return true;
        return !/\bclass=["'][^"']*\b(?:light|dark)\b[^"']*["']/.test(htmlTag);
      }
      return typeof pattern === 'string' ? !content.includes(pattern) : !pattern.test(content);
    });

    if (missing.length === 0) {
      console.log(`    [OK] ${htmlFile} infrastructure complete`);
    } else {
      const mainAgentMissing = missing.filter(m => m.owner === 'MAIN-AGENT');
      const subAgentMissing = missing.filter(m => m.owner === 'SUB-AGENT');
      for (const { id, desc, consequence, owner } of missing) {
        const ownerTag = `[${owner}]`;
        const fixHint = owner === 'MAIN-AGENT'
          ? ` Fix: run apply-html-head-contract.mjs <css-path> ${htmlFile} --replace-head`
          : ` Fix: Sub-Agent must add the missing element using Edit tool`;
        if (id === 'theme-inline' && hasDesignLibrary) {
          addWarning(
            'html-infrastructure',
            `${ownerTag} ${htmlFile} missing ${desc}. Impact: ${consequence} (downgraded to warning — Design Library present)`
          );
        } else {
          addError(
            'html-infrastructure',
            `${ownerTag} ${htmlFile} missing ${desc}. Impact: ${consequence}.${fixHint}`
          );
        }
      }
      if (mainAgentMissing.length > 0) {
        addRepairPlanHint('head-infrastructure-missing', {
          owner: 'main-agent',
          repairScope: 'affected-page-head',
          strategy: 'run_apply_html_head_replace',
          affectedFiles: [htmlFile],
          allowSourceRead: 'no-full-html-read',
          maxValidationRuns: 2
        });
      }
      if (subAgentMissing.length > 0) {
        addRepairPlanHint('missing-lucide-init', {
          owner: 'sub-agent',
          repairScope: 'append-before-body-close',
          strategy: 'append_lucide_init_script',
          affectedFiles: [htmlFile],
          allowSourceRead: 'no-full-html-read',
          maxValidationRuns: 2
        });
      }
    }
  }
}

const SEMANTIC_TOKEN_CLASS_PATTERN = /\b(?:bg|text|border|ring)-(?:background|foreground|card|card-foreground|muted|muted-foreground|primary|primary-foreground|secondary|secondary-foreground|accent|accent-foreground|border|input|ring)\b/;

function validateSemanticTokenFallback(designDir, operatingMode = 'free-explore') {
  console.log('\nChecking semantic token fallback CSS...');

  const pagesDir = path.join(designDir, 'pages');
  if (!fs.existsSync(pagesDir)) return;

  const htmlFiles = fs.readdirSync(pagesDir).filter(f => f.endsWith('.html'));
  if (htmlFiles.length === 0) return;

  const addFallbackIssue = operatingMode === 'library-bound' ? addWarning : addError;

  for (const htmlFile of htmlFiles) {
    const htmlPath = path.join(pagesDir, htmlFile);
    const content = readHtmlFileCached(htmlPath, htmlFile);
    if (content === null) continue;

    if (!SEMANTIC_TOKEN_CLASS_PATTERN.test(content)) continue;
    if (content.includes('id="semantic-token-fallback"') || content.includes("id='semantic-token-fallback'")) {
      console.log(`    [OK] ${htmlFile} semantic fallback present`);
      continue;
    }

    addFallbackIssue(
      'semantic-token-fallback',
      `${htmlFile}: uses Tailwind semantic token classes such as bg-card/text-foreground/border-border, ` +
      `but <style id="semantic-token-fallback"> is missing. If Tailwind browser runtime fails to compile ` +
      `@theme inline in the canvas iframe, the page can degrade to default black/white styling. ` +
      `Fix: regenerate the page head with apply-html-head-contract.mjs.`
    );
  }
}

function stripThemeVars(content) {
  return content.replace(/<style[^>]*id=["']theme-vars["'][^>]*>[\s\S]*?<\/style>/gi, '');
}

function detectNonInfrastructureStyleBlocks(html) {
  const styleRegex = /<style[^>]*>[\s\S]*?<\/style>/gi;
  const matches = html.match(styleRegex) || [];

  return matches.filter((block) => {
    if (/id=["']theme-vars["']/i.test(block)) return false;
    if (/id=["']component-vars["']/i.test(block)) return false;
    if (/id=["']semantic-token-fallback["']/i.test(block)) return false;
    if (/type=["']text\/tailwindcss["']/i.test(block)) return false;
    if (/\.no-scrollbar/.test(block) || /\[data-icon\]/.test(block)) {
      const inner = block.replace(/<style[^>]*>/i, '').replace(/<\/style>/i, '').trim();
      const stripped = inner
        .replace(/\.no-scrollbar[^}]*\{[^}]*\}/g, '')
        .replace(/\[data-icon\][^}]*\{[^}]*\}/g, '')
        .trim();
      if (stripped.length === 0) return false;
    }
    const inner = block.replace(/<style[^>]*>/i, '').replace(/<\/style>/i, '').trim();
    return inner.length > 0;
  });
}

/**
 * Detect non-infrastructure <style> blocks in <head>.
 * The page contract keeps <head> exclusively managed by apply-html-head-contract.mjs;
 * custom styles must live in <body> so theme replacement stays deterministic.
 */
function detectCustomStylesInHead(headHtml) {
  return detectNonInfrastructureStyleBlocks(headHtml);
}

function validateNoCustomStylesInHead(designDir, operatingMode = 'free-explore') {
  const isFreeExplore = operatingMode !== 'library-bound';
  // In free-explore mode, custom styles in <head> are self-correcting:
  // apply-html-head-contract.mjs --replace-head will destroy them automatically.
  const addStyleIssue = isFreeExplore ? addWarning : addError;
  console.log('\nChecking custom <style> placement in <head>...');

  const pagesDir = path.join(designDir, 'pages');
  if (!fs.existsSync(pagesDir)) return;

  const htmlFiles = fs.readdirSync(pagesDir).filter(f => f.endsWith('.html'));
  if (htmlFiles.length === 0) return;

  for (const htmlFile of htmlFiles) {
    const htmlPath = path.join(pagesDir, htmlFile);
    const content = readHtmlFileCached(htmlPath, htmlFile);
    if (content === null) continue;

    const headMatch = content.match(/<head[\s\S]*?<\/head>/i);
    if (!headMatch) continue;

    const customStyles = detectCustomStylesInHead(headMatch[0]);
    if (customStyles.length > 0) {
      addStyleIssue(
        'html-head-style',
        `${htmlFile}: found ${customStyles.length} custom <style> block(s) in <head>. ` +
        `The <head> is owned by apply-html-head-contract.mjs; move custom styles before </body> or re-run ` +
        `apply-html-head-contract.mjs <css-path> <html-file> --replace-head to relocate them.`
      );
    }
  }
}

function validateOrchestrationSummaryPresence(designDir, expectedPages, designFiles) {
  console.log('\nChecking orchestration summary presence...');

  const summaryPath = path.join(designDir, 'runtime-orchestration-summary.json');
  if (fs.existsSync(summaryPath)) {
    console.log('  [OK] runtime-orchestration-summary.json found');
    const summary = loadOrchestrationSummary(designDir);
    const provenance = summary?.skillProvenance;
    const explicitMissingFallback = provenance?.version === null &&
      provenance?.version_source === 'unknown' &&
      provenance?.read_status === 'missing';
    if (!provenance?.name || (!provenance?.version && !explicitMissingFallback) || !provenance?.version_source) {
      addWarning(
        'orchestration-summary',
        'runtime-orchestration-summary.json is missing skillProvenance.name/version/version_source. ' +
        'Version provenance will be reported as observed_unknown by external evaluators.'
      );
    }
    return;
  }

  const pagesDir = path.join(designDir, 'pages');
  const htmlFiles = fs.existsSync(pagesDir)
    ? fs.readdirSync(pagesDir).filter(f => f.endsWith('.html'))
    : [];

  if (expectedPages !== undefined && designFiles.length > 0 && htmlFiles.length > 0) {
    addWarning(
      'orchestration-summary',
      'runtime-orchestration-summary.json is missing. Canvas validation can still pass, but quality-context checks ' +
      '(operatingMode, visualNorthStar, compositionPattern, continuityAnchors, miniProgramStyle) are degraded.'
    );
  } else {
    console.log('  [OK] orchestration summary not required for this scan context');
  }
}

function collectRepairStopConditionEvidence(summary) {
  const project = summary?.project || {};
  const missing = [];
  const stopConditionMet = project.repairStopConditionMet === true;
  const stopReason = String(project.repairStopReason || '').trim();
  if (!stopConditionMet) missing.push('project.repairStopConditionMet must be true');
  if (!stopReason) missing.push('project.repairStopReason is required');
  if (!Array.isArray(project.remainingBlockingIssues) || project.remainingBlockingIssues.length === 0) {
    missing.push('project.remainingBlockingIssues[] is required');
  }
  if (!String(project.lastValidationReportPath || '').trim()) missing.push('project.lastValidationReportPath is required');
  return { complete: missing.length === 0, missing };
}

function isDiagnosticHistoryRecord(item) {
  return item?.diagnosticOnly === true || item?.diagnosticClass === 'repair-ledger';
}

function validateValidationRepairLedger(summary, designDir) {
  console.log('\nChecking validation repair ledger...');

  const history = Array.isArray(summary?.project?.validationHistory)
    ? summary.project.validationHistory
    : [];
  const failed = history.filter(item =>
    item &&
    !isDiagnosticHistoryRecord(item) &&
    (item.success === false || Number(item.exitCode) === 1)
  );
  const ledger = Array.isArray(summary?.project?.validationRepairLedger)
    ? summary.project.validationRepairLedger
    : [];
  const diagnosticReports = Array.isArray(summary?.project?.ledgerDiagnosticReports)
    ? summary.project.ledgerDiagnosticReports
    : [];
  if (failed.length === 0) {
    if (ledger.length > 0) {
      addError('repair-ledger', 'validationRepairLedger[] exists but validationHistory[] contains no failed validation');
    } else {
      console.log('  [OK] No failed validation history; repair ledger gate skipped');
    }
    return;
  }
  if (ledger.length === 0) {
    addError('repair-ledger', 'validationRepairLedger[] is required because validationHistory[] contains failed validation');
    return;
  }
  if (ledger.length < failed.length) {
    addError('repair-ledger', `validationHistory has ${failed.length} failed validation(s) but validationRepairLedger has ${ledger.length} entr${ledger.length === 1 ? 'y' : 'ies'}`);
  }

  if (ledger.length > 3) {
    const stopEvidence = collectRepairStopConditionEvidence(summary);
    if (!stopEvidence.complete) {
      addError('repair-ledger', `validationRepairLedger[] has ${ledger.length} entries; repair stop condition threshold is 3`);
      for (const missing of stopEvidence.missing) {
        addError('repair-ledger', `repair stop condition evidence incomplete: ${missing}`);
      }
    }
  } else if (ledger.length > 2) {
    addWarning('repair-ledger', `validationRepairLedger[] has ${ledger.length} entries; retry_or_repair_loop risk should be reviewed`);
  }

  function readLedgerReport(reportPath) {
    const trimmed = String(reportPath || '').trim();
    if (!trimmed) return { status: 'empty' };
    const resolved = path.resolve(designDir, trimmed);
    const designDirResolved = path.resolve(designDir);
    if (!resolved.startsWith(`${designDirResolved}${path.sep}`) && resolved !== designDirResolved) {
      addError('repair-ledger', `revalidationReportPath escapes design project: ${trimmed}`);
      return { status: 'escaped' };
    }
    if (!fs.existsSync(resolved)) return { status: 'missing', path: resolved };
    try {
      const content = fs.readFileSync(resolved, 'utf8');
        return { status: 'found', report: JSON.parse(content), reportHash: hashString(content), path: resolved };
    } catch (err) {
      addError('repair-ledger', `revalidationReportPath is not valid JSON or unreadable: ${trimmed} (${err.message})`);
      return { status: 'invalid', path: resolved };
    }
  }

    function findHistoryRecord(reportPath, reportHash, predicate = null) {
      const normalizedPath = String(reportPath || '').trim();
      const normalizedHash = String(reportHash || '').trim();
      if (!normalizedPath || !normalizedHash) return null;
      return history.find(item =>
        item &&
        String(item.reportPath || '').trim() === normalizedPath &&
        String(item.reportHash || '').trim() === normalizedHash &&
        (!predicate || predicate(item))
      ) || null;
    }
    function isFailedHistoryRecord(item) {
      return item && (item.success === false || Number(item.exitCode) === 1);
    }
    function findDiagnosticRecord(reportPath, reportHash) {
      const normalizedPath = String(reportPath || '').trim();
      const normalizedHash = String(reportHash || '').trim();
      if (!normalizedPath || !normalizedHash) return null;
      return diagnosticReports.find(item =>
        item &&
        item.diagnosticClass === 'repair-ledger' &&
        String(item.reportPath || '').trim() === normalizedPath &&
        String(item.reportHash || '').trim() === normalizedHash
      ) || null;
    }

  for (const [index, item] of ledger.entries()) {
    if (!item || typeof item !== 'object') {
      addError('repair-ledger', `validationRepairLedger[${index}] must be an object`);
      continue;
    }
      if (!String(item.failedReportPath || '').trim()) addWarning('repair-ledger', `validationRepairLedger[${index}].failedReportPath is missing`);
      if (!String(item.failedReportHash || '').trim()) addWarning('repair-ledger', `validationRepairLedger[${index}].failedReportHash is missing`);
      if (!String(item.repairWorkflowReadPath || '').trim()) addWarning('repair-ledger', `validationRepairLedger[${index}].repairWorkflowReadPath is missing`);
      if (!Array.isArray(item.ownerTriage) || item.ownerTriage.length === 0) addWarning('repair-ledger', `validationRepairLedger[${index}].ownerTriage[] is missing`);
      if (!Array.isArray(item.repairActions) || item.repairActions.length === 0) addWarning('repair-ledger', `validationRepairLedger[${index}].repairActions[] is missing`);
    if (Array.isArray(item.repairActions)) {
      for (const [actionIndex, action] of item.repairActions.entries()) {
        if (!Array.isArray(action?.preEditFileHashes) || action.preEditFileHashes.length === 0) {
            addWarning('repair-ledger', `validationRepairLedger[${index}].repairActions[${actionIndex}].preEditFileHashes[] is missing (legacy optional evidence)`);
        }
        if (!Array.isArray(action?.postEditFileHashes) || action.postEditFileHashes.length === 0) {
            addWarning('repair-ledger', `validationRepairLedger[${index}].repairActions[${actionIndex}].postEditFileHashes[] is missing (legacy optional evidence)`);
        }
        if (!Array.isArray(action?.repairOwnedFields) || action.repairOwnedFields.length === 0) {
            addWarning('repair-ledger', `validationRepairLedger[${index}].repairActions[${actionIndex}].repairOwnedFields[] is missing`);
        }
      }
    }
      if (!String(item.revalidationReportPath || '').trim()) addWarning('repair-ledger', `validationRepairLedger[${index}].revalidationReportPath is missing`);
      if (!String(item.revalidationReportHash || '').trim()) addWarning('repair-ledger', `validationRepairLedger[${index}].revalidationReportHash is missing`);
    if (item.revalidationSuccess !== true && item.revalidationSuccess !== false) {
        addWarning('repair-ledger', `validationRepairLedger[${index}].revalidationSuccess should be a boolean`);
    }
      const failedHistory = findHistoryRecord(item.failedReportPath, item.failedReportHash, isFailedHistoryRecord);
      if (String(item.failedReportPath || '').trim() && String(item.failedReportHash || '').trim() && !failedHistory) {
        addWarning('repair-ledger', `validationRepairLedger[${index}].failedReportHash does not reference a failed validationHistory record`);
      }

    if (designDir) {
      const result = readLedgerReport(item.revalidationReportPath);
        const revalidationHistory = findHistoryRecord(item.revalidationReportPath, item.revalidationReportHash);
        const revalidationDiagnostic = findDiagnosticRecord(item.revalidationReportPath, item.revalidationReportHash);
      if (result.status === 'found') {
          const currentHashMatches = item.revalidationReportHash && result.reportHash === item.revalidationReportHash;
            if (item.revalidationReportHash && !currentHashMatches && !revalidationHistory && !revalidationDiagnostic) {
              addWarning('repair-ledger', `ledger[${index}].revalidationReportHash does not match ${item.revalidationReportPath}`);
            }
          if ((currentHashMatches || !item.revalidationReportHash) && result.report.success !== item.revalidationSuccess) {
          addError('repair-ledger', `ledger[${index}].revalidationSuccess=${item.revalidationSuccess} but report.success=${result.report.success}`);
          } else if (!currentHashMatches && revalidationHistory && revalidationHistory.success !== item.revalidationSuccess) {
            addError('repair-ledger', `ledger[${index}].revalidationSuccess=${item.revalidationSuccess} but validationHistory report success=${revalidationHistory.success}`);
          } else if (!currentHashMatches && revalidationDiagnostic && revalidationDiagnostic.success !== item.revalidationSuccess) {
            addError('repair-ledger', `ledger[${index}].revalidationSuccess=${item.revalidationSuccess} but ledgerDiagnosticReports report success=${revalidationDiagnostic.success}`);
        }
        } else if (result.status === 'missing' && item.revalidationSuccess === true && !revalidationHistory && !revalidationDiagnostic) {
        addError('repair-ledger', `ledger[${index}] claims revalidationSuccess=true but report file does not exist: ${item.revalidationReportPath}`);
        } else if (result.status === 'missing' && revalidationHistory && revalidationHistory.success !== item.revalidationSuccess) {
          addError('repair-ledger', `ledger[${index}].revalidationSuccess=${item.revalidationSuccess} but validationHistory report success=${revalidationHistory.success}`);
        } else if (result.status === 'missing' && revalidationDiagnostic && revalidationDiagnostic.success !== item.revalidationSuccess) {
          addError('repair-ledger', `ledger[${index}].revalidationSuccess=${item.revalidationSuccess} but ledgerDiagnosticReports report success=${revalidationDiagnostic.success}`);
        } else if (result.status === 'missing' && item.revalidationSuccess === false && !revalidationHistory) {
        if (!revalidationDiagnostic) addWarning('repair-ledger', `ledger[${index}] revalidationSuccess=false but report file missing (degraded evidence)`);
      }
    }
  }

  const repairEntryEvidence = Array.isArray(summary?.project?.repairEntryEvidence)
    ? summary.project.repairEntryEvidence
    : [];
  if (repairEntryEvidence.length < failed.length) {
      addWarning('repair-ledger', `validationHistory has ${failed.length} failed validation(s) but repairEntryEvidence has ${repairEntryEvidence.length} entr${repairEntryEvidence.length === 1 ? 'y' : 'ies'}`);
  }
    for (const [failedIndex, failedRecord] of failed.entries()) {
      const failedReportPath = String(failedRecord.reportPath || '').trim();
      const failedReportHash = String(failedRecord.reportHash || '').trim();
      if (!failedReportPath || !failedReportHash) continue;
      const matchingLedger = ledger.find(item =>
        item &&
        item.failedReportPath === failedReportPath &&
        item.failedReportHash === failedReportHash
      );
      if (!matchingLedger) {
          addWarning('repair-ledger', `validationHistory[${failedIndex}] has no matching validationRepairLedger entry for ${failedReportPath}#${failedReportHash}`);
      }
    }
}

function isRestoreSummary(summary) {
  const project = summary?.project || {};
  const intent = project.intentProfile || {};
  if (intent.caseFamily === 'restore_1to1') return true;
  if (project.replicationMode === 'high-fidelity') return true;

  const captureEvidence = project.referenceCaptureEvidence;
  const hasCaptureEvidence = captureEvidence &&
    typeof captureEvidence === 'object' &&
    captureEvidence.applies !== false &&
    Boolean(captureEvidence.sourceAuthority || captureEvidence.sourceType);
  if (hasCaptureEvidence) return true;

  const checkpoints = Array.isArray(project.restoreVisualCheckpoints)
    ? project.restoreVisualCheckpoints
    : [];
  if (checkpoints.length > 0) return true;

  const pages = Array.isArray(summary?.pages) ? summary.pages : [];
  return pages.some(page => {
    const evidence = page?.restoreEvidence;
    return evidence &&
      typeof evidence === 'object' &&
      evidence.applies !== false &&
      (
        Array.isArray(evidence.visualCheckpointResults) ||
        evidence.dominantReferenceImageUsedAsBody !== undefined
      );
  });
}

function restoreSourceTypeFrom(project, captureEvidence) {
  return String(
    project?.sourceType ||
    project?.intentProfile?.sourceType ||
    captureEvidence?.sourceType ||
    project?.restorationContractLite?.sourceType ||
    ''
  ).trim();
}

function hasAnyObjectField(object, fields) {
  if (!object || typeof object !== 'object') return false;
  return fields.some(field => {
    const value = object[field];
    if (Array.isArray(value)) return value.length > 0;
    if (value && typeof value === 'object') return Object.keys(value).length > 0;
    return value !== undefined && value !== null && value !== '';
  });
}

function validateRestoreSourceType(project, captureEvidence) {
  const sourceType = restoreSourceTypeFrom(project, captureEvidence);
  if (!sourceType) {
    addError('restore-source-type', 'restore sourceType is required on project.sourceType, project.intentProfile.sourceType, or referenceCaptureEvidence.sourceType');
    return;
  }
  if (!RESTORE_VALID_SOURCE_TYPES.has(sourceType)) {
    addError('restore-source-type', `restore sourceType must be image, url, or image+url; found ${sourceType}`);
    return;
  }

  const hasImageEvidence = hasAnyObjectField(captureEvidence, [
    'providedImagePath',
    'providedImageEvidence',
    'providedScreenshotEvidence',
    'imageEvidence',
    'screenshotEvidence',
  ]);
  const hasFullPageScreenshot = hasAnyObjectField(captureEvidence, [
    'fullPageScreenshotEvidence',
  ]);
  const hasUrlEvidence = hasAnyObjectField(captureEvidence, [
    'urlEvidence',
    'fullPageScreenshotEvidence',
    'browserCaptureEvidence',
    'liveUrl',
  ]);

  if (sourceType === 'url' && !hasFullPageScreenshot) {
    addError('restore-source-type', 'URL restore requires referenceCaptureEvidence.fullPageScreenshotEvidence');
  }
  if (sourceType === 'image+url') {
    if (!hasImageEvidence) addError('restore-source-type', 'image+url restore requires provided image/screenshot evidence');
    if (!hasUrlEvidence) addError('restore-source-type', 'image+url restore requires URL evidence');
    const visualAuthority = String(captureEvidence?.visualAuthority || '').trim();
    if (visualAuthority && !['provided-image', 'provided-screenshot', 'image-primary-url-secondary', 'image', 'screenshot'].includes(visualAuthority)) {
      addError('restore-source-type', `image+url visualAuthority must keep the provided image/screenshot primary; found ${visualAuthority}`);
    }
  }
  if (sourceType === 'image' && hasUrlEvidence) {
    addError('restore-source-type', 'referenceCaptureEvidence contains URL evidence; sourceType must be image+url instead of image');
  }
  if (sourceType === 'url' && hasImageEvidence) {
    addError('restore-source-type', 'referenceCaptureEvidence contains provided image evidence; sourceType must be image+url instead of url');
  }
}

function getRestoreCoverageRows(project) {
  if (Array.isArray(project?.sourceRegionCoverage)) {
    return { rows: project.sourceRegionCoverage, source: 'project.sourceRegionCoverage' };
  }
  if (Array.isArray(project?.restorationContractLite?.sourceRegionCoverage)) {
    return {
      rows: project.restorationContractLite.sourceRegionCoverage,
      source: 'project.restorationContractLite.sourceRegionCoverage'
    };
  }
  return { rows: [], source: null };
}

function restoreCoverageStatus(row) {
  return String(row?.mappedStatus || row?.status || '').trim();
}

function validateRestoreIdentityAndDocumentProfile(project, sourceType) {
  const identity = project.sourceIdentity;
  if (!identity || typeof identity !== 'object' || Array.isArray(identity)) {
    addError('restore-source-identity', 'project.sourceIdentity is required before measuredSourceFacts');
  } else {
    if (!String(identity.businessType || '').trim()) addError('restore-source-identity', 'sourceIdentity.businessType is required');
    if (!Array.isArray(identity.coreObjects) || identity.coreObjects.length === 0) {
      addError('restore-source-identity', 'sourceIdentity.coreObjects[] is required');
    }
    if (!String(identity.deviceType || '').trim()) addError('restore-source-identity', 'sourceIdentity.deviceType is required');
    if (!String(identity.pageTitle || '').trim()) addError('restore-source-identity', 'sourceIdentity.pageTitle is required');
  }

  const pageStateLock = project.pageStateLock;
  if (!pageStateLock || typeof pageStateLock !== 'object' || Array.isArray(pageStateLock)) {
    addError('restore-page-state-lock', 'project.pageStateLock is required before measuredSourceFacts');
  } else {
    if (!String(pageStateLock.currentState || '').trim()) addError('restore-page-state-lock', 'pageStateLock.currentState is required');
    if (!Array.isArray(pageStateLock.forbiddenDeviations) || pageStateLock.forbiddenDeviations.length === 0) {
      addError('restore-page-state-lock', 'pageStateLock.forbiddenDeviations[] is required');
    }
  }

  const profile = project.sourceDocumentProfile;
  if (!profile || typeof profile !== 'object' || Array.isArray(profile)) {
    addError('restore-document-profile', 'project.sourceDocumentProfile is required');
    return;
  }
  if (!String(profile.sourceType || '').trim()) addError('restore-document-profile', 'sourceDocumentProfile.sourceType is required');
  if (sourceType && profile.sourceType && profile.sourceType !== sourceType) {
    addError('restore-document-profile', `sourceDocumentProfile.sourceType=${profile.sourceType} must match sourceType=${sourceType}`);
  }
  if (!Array.isArray(profile.requiredRegionGroups) || profile.requiredRegionGroups.length === 0) {
    addError('restore-document-profile', 'sourceDocumentProfile.requiredRegionGroups[] is required');
  }
}

function validateRestoreRegionGroupCoverage(project, sourceType) {
  const profile = project.sourceDocumentProfile || {};
  const { rows, source } = getRestoreCoverageRows(project);
  if (rows.length === 0) {
    addError('restore-region-coverage', 'project.sourceRegionCoverage[] is required');
    return;
  }
  if (source !== 'project.sourceRegionCoverage') {
    addWarning('restore-region-coverage', 'sourceRegionCoverage should be promoted to project.sourceRegionCoverage; nested restorationContractLite.sourceRegionCoverage remains compatibility-only');
  }

  const requiredRegionGroups = new Set(Array.isArray(profile.requiredRegionGroups)
    ? profile.requiredRegionGroups.map(item => String(item || '').trim()).filter(Boolean)
    : []);
  if (sourceType === 'url' && profile.documentLengthClass !== 'short') {
    for (const group of RESTORE_URL_LONG_PAGE_REGION_GROUPS) requiredRegionGroups.add(group);
  }
  if ((sourceType === 'image' || sourceType === 'image+url') && profile.deviceFramePresent === true) {
    for (const group of RESTORE_IMAGE_DEVICE_REGION_GROUPS) requiredRegionGroups.add(group);
  }

  const mappedGroups = new Set();
  for (const [index, row] of rows.entries()) {
    if (!row || typeof row !== 'object' || Array.isArray(row)) {
      addError('restore-region-coverage', `sourceRegionCoverage[${index}] must be an object`);
      continue;
    }
    const status = restoreCoverageStatus(row);
    const priority = String(row.priority || '').trim();
    const regionGroup = String(row.regionGroup || '').trim();
    if (['high', 'medium'].includes(priority) && !regionGroup) {
      addError('restore-region-coverage', `sourceRegionCoverage[${index}].regionGroup is required for high/medium priority rows`);
    }
    if (['high', 'medium'].includes(priority) && !['mapped', 'intentionally-deviated'].includes(status)) {
      addError(
        'restore-region-coverage',
        `sourceRegionCoverage[${index}] is ${priority} priority but status is ${status || 'missing'}; must be mapped or intentionally-deviated`
      );
    }
    if (regionGroup && ['mapped', 'intentionally-deviated'].includes(status)) {
      mappedGroups.add(regionGroup);
    }
  }

  const missingGroups = [...requiredRegionGroups].filter(group => !mappedGroups.has(group));
  if (missingGroups.length > 0) {
    addError('restore-region-coverage', `required region groups not covered: ${missingGroups.join(', ')}`);
  }
}

function validateMeasuredSourceFacts(project, checkpoints) {
  const facts = Array.isArray(project?.measuredSourceFacts)
    ? project.measuredSourceFacts
    : (Array.isArray(project?.restorationContractLite?.measuredSourceFacts)
      ? project.restorationContractLite.measuredSourceFacts
      : []);

  if (facts.length < 8) {
    addError('restore-measured-source-facts', `project.measuredSourceFacts must contain at least 8 rows; found ${facts.length}`);
  }

  const highPriorityFacts = facts.filter(fact => fact && fact.priority === 'high');
  if (highPriorityFacts.length < 5) {
    addError('restore-measured-source-facts', `project.measuredSourceFacts must contain at least 5 high priority rows; found ${highPriorityFacts.length}`);
  }
  const highPriorityWithMeasurementBasis = highPriorityFacts
    .filter(fact => String(fact?.measurementBasis || '').trim()).length;
  if (highPriorityWithMeasurementBasis < 5) {
    addWarning(
      'restore-measured-source-facts',
      `at least 5 high priority measuredSourceFacts should include measurementBasis; found ${highPriorityWithMeasurementBasis}. This will be enforced by validate-restore-contract.mjs before dispatch.`
    );
  }

  const presentCategories = new Set();
  const checkpointIds = new Set((Array.isArray(checkpoints) ? checkpoints : [])
    .map(checkpoint => String(checkpoint?.id || '').trim())
    .filter(Boolean));
  const factIds = new Set(facts.map(fact => String(fact?.id || '').trim()).filter(Boolean));
  const factIdsByCheckpoint = new Map();

  function addLink(checkpointId, factId) {
    if (!checkpointId || !factId) return;
    if (!factIdsByCheckpoint.has(checkpointId)) factIdsByCheckpoint.set(checkpointId, new Set());
    factIdsByCheckpoint.get(checkpointId).add(factId);
  }

  for (const [index, fact] of facts.entries()) {
    if (!fact || typeof fact !== 'object') {
      addError('restore-measured-source-facts', `measuredSourceFacts[${index}] must be an object`);
      continue;
    }
    const factId = String(fact.id || '').trim();
    const category = String(fact.category || '').trim();
    if (category) presentCategories.add(category);
    if (!factId) addError('restore-measured-source-facts', `measuredSourceFacts[${index}].id is required`);
    if (!category) addError('restore-measured-source-facts', `measuredSourceFacts[${index}].category is required`);
    if (!String(fact.sourceRegion || '').trim()) addError('restore-measured-source-facts', `measuredSourceFacts[${index}].sourceRegion is required`);
    if (!String(fact.fact || '').trim()) addError('restore-measured-source-facts', `measuredSourceFacts[${index}].fact is required`);
    if (!String(fact.priority || '').trim()) addError('restore-measured-source-facts', `measuredSourceFacts[${index}].priority is required`);
    const linkedCheckpoints = Array.isArray(fact.usedByCheckpointIds) ? fact.usedByCheckpointIds : [];
    for (const checkpointId of linkedCheckpoints) {
      const cid = String(checkpointId || '').trim();
      if (!cid) continue;
      if (!checkpointIds.has(cid)) {
        addError('restore-measured-source-facts', `measuredSourceFacts[${index}] references unknown checkpoint id ${cid}`);
      } else {
        addLink(cid, factId);
      }
    }
  }

  for (const checkpoint of checkpoints) {
    if (!checkpoint?.id) continue;
    const cid = String(checkpoint.id).trim();
    const reverseLinkedFacts = Array.isArray(checkpoint.measuredSourceFactIds) ? checkpoint.measuredSourceFactIds : [];
    for (const factId of reverseLinkedFacts) {
      const fid = String(factId || '').trim();
      if (!fid) continue;
      if (!factIds.has(fid)) {
        addError('restore-measured-source-facts', `checkpoint ${cid} references unknown measured fact id ${fid}`);
      } else {
        addLink(cid, fid);
      }
    }
  }

  for (const checkpoint of checkpoints.filter(c => c && c.priority === 'high')) {
    const cid = String(checkpoint?.id || '').trim();
    if (!cid) continue;
    if (!factIdsByCheckpoint.get(cid)?.size) {
      addError('restore-measured-source-facts', `high priority checkpoint ${cid} has no measured source fact linked (neither usedByCheckpointIds nor measuredSourceFactIds)`);
    }
  }

  for (const fact of facts) {
    const fid = String(fact?.id || '').trim();
    if (!fid) continue;
    const isLinked = [...factIdsByCheckpoint.values()].some(s => s.has(fid));
    if (!isLinked) {
      addError('restore-measured-source-facts', `measured fact ${fid} is an orphan: not linked to any checkpoint via either direction`);
    }
  }

  const missingCategories = [...RESTORE_REQUIRED_MEASURED_FACT_CATEGORIES]
    .filter(category => !presentCategories.has(category));
  if (missingCategories.length > 0) {
    addError('restore-measured-source-facts', `measuredSourceFacts category coverage missing: ${missingCategories.join(', ')}`);
  }
}

function validateRestoreEvidence(designDir, summary) {
  console.log('\nChecking restore_1to1 evidence gates...');

  if (!isRestoreSummary(summary)) {
    console.log('  [OK] Not restore_1to1; restore evidence gate skipped');
    return;
  }

  const skillVersion = summary?.skillProvenance?.version;
  if (skillVersion && compareVersion(skillVersion, RESTORE_EVIDENCE_SKIP_VERSION) >= 0) {
    console.log('  [OK] restore evidence review/visualDiffReview/sourceFactCoverageMap skipped (deprecated since ' + RESTORE_EVIDENCE_SKIP_VERSION + ')');
    const project = summary?.project || {};
    const captureEvidence = project.referenceCaptureEvidence;
    const sourceType = restoreSourceTypeFrom(project, captureEvidence);
    if (!captureEvidence || typeof captureEvidence !== 'object') {
      addError('restore-evidence', 'project.referenceCaptureEvidence is required for restore_1to1');
    } else {
      validateRestoreSourceType(project, captureEvidence);
    }
    validateRestoreIdentityAndDocumentProfile(project, sourceType);
    validateRestoreRegionGroupCoverage(project, sourceType);
    const pages = Array.isArray(summary?.pages) ? summary.pages : [];
    const restorePages = pages.filter(page => page && typeof page.htmlSrc === 'string');
    validateRestoreReferenceImageBody(designDir, restorePages);
    validateRestoreLargeVisualAssetGate(designDir, project, restorePages);
    return;
  }

  const project = summary?.project || {};
  const captureEvidence = project.referenceCaptureEvidence;
  const sourceType = restoreSourceTypeFrom(project, captureEvidence);
  if (!captureEvidence || typeof captureEvidence !== 'object') {
    addError('restore-evidence', 'project.referenceCaptureEvidence is required for restore_1to1');
  } else {
    validateRestoreSourceType(project, captureEvidence);
  }
  validateRestoreIdentityAndDocumentProfile(project, sourceType);

  const checkpoints = Array.isArray(project.restoreVisualCheckpoints)
    ? project.restoreVisualCheckpoints
    : [];
  if (checkpoints.length < 8) {
    addError('restore-evidence', `project.restoreVisualCheckpoints must contain at least 8 rows; found ${checkpoints.length}`);
  }
  const highPriorityCount = checkpoints.filter(item => item && item.priority === 'high').length;
  if (highPriorityCount < 5) {
    addError('restore-evidence', `project.restoreVisualCheckpoints must contain at least 5 high priority rows; found ${highPriorityCount}`);
  }
  validateMeasuredSourceFacts(project, checkpoints);
  validateRestoreCheckpointDimensionCoverage(summary, checkpoints);
  for (const [index, checkpoint] of checkpoints.entries()) {
    if (!checkpoint || checkpoint.priority !== 'high') continue;
    for (const field of ['sourceFact', 'expected']) {
      const value = String(checkpoint[field] || '');
      if (!value) addError('restore-evidence', `restoreVisualCheckpoints[${index}].${field} is required for high priority checkpoints`);
      if (value.length > 120) addError('restore-evidence', `restoreVisualCheckpoints[${index}].${field} exceeds 120 chars`);
    }
  }

  validateRestoreRegionGroupCoverage(project, sourceType);

  const pages = Array.isArray(summary?.pages) ? summary.pages : [];
  const restorePages = pages.filter(page => page && typeof page.htmlSrc === 'string');
  for (const page of restorePages) {
    const evidence = page.restoreEvidence;
    if (!evidence || typeof evidence !== 'object') {
      addError('restore-evidence', `${page.htmlSrc}: pages[].restoreEvidence is required for restore_1to1`);
      continue;
    }
    if (!Array.isArray(evidence.visualCheckpointResults) || evidence.visualCheckpointResults.length === 0) {
      addError('restore-evidence', `${page.htmlSrc}: restoreEvidence.visualCheckpointResults must be non-empty`);
    }
    if (evidence.dominantReferenceImageUsedAsBody !== false) {
      addError('restore-evidence', `${page.htmlSrc}: restoreEvidence.dominantReferenceImageUsedAsBody must be false`);
    }
  }

  const review = project.restoreEvidenceReview;
  if (!review || typeof review !== 'object') {
    addError('restore-evidence', 'project.restoreEvidenceReview is required for restore_1to1 before final validation');
  } else {
    if (review.applies === false) {
      addError('restore-evidence', 'project.restoreEvidenceReview.applies must not be false for restore_1to1');
    }
    if (review.allHighPriorityCheckpointsAcceptable !== true) {
      addError('restore-evidence', 'project.restoreEvidenceReview.allHighPriorityCheckpointsAcceptable must be true');
    }
    if ((review.highPriorityMissingCount ?? 0) > 0) {
      addError(
        'restore-evidence',
        `project.restoreEvidenceReview.highPriorityMissingCount must be 0; found ${review.highPriorityMissingCount}`
      );
    }
    if ((review.highPriorityPartialWithoutDeviationCount ?? 0) > 0) {
      addError(
        'restore-evidence',
        `project.restoreEvidenceReview.highPriorityPartialWithoutDeviationCount must be 0; found ${review.highPriorityPartialWithoutDeviationCount}`
      );
    }
  }

  validateRestoreVisualDiffReview(project);
  validateRestoreReferenceImageBody(designDir, restorePages);
  validateRestoreLargeVisualAssetGate(designDir, project, restorePages);
}

function isNewRestoreDimensionGateActive(summary) {
  const version = summary?.skillProvenance?.version;
  return Boolean(version) && compareVersion(version, RESTORE_DIMENSION_GATE_VERSION) >= 0;
}

function normalizeRestoreDimension(value) {
  const raw = String(value || '').trim().toLowerCase().replaceAll('_', '-').replace(/\s+/g, '-');
  const aliases = new Map([
    ['color', 'color-rhythm'],
    ['colors', 'color-rhythm'],
    ['colour-rhythm', 'color-rhythm'],
    ['typography-scale', 'typography'],
    ['type', 'typography'],
    ['component', 'component-proportion'],
    ['components', 'component-proportion'],
    ['component-ratio', 'component-proportion'],
    ['component-proportions', 'component-proportion'],
    ['spacing', 'density'],
    ['spacing-density', 'density'],
    ['detail', 'fine-detail'],
    ['details', 'fine-detail'],
  ]);
  return aliases.get(raw) || raw;
}

function validateRestoreCheckpointDimensionCoverage(summary, checkpoints) {
  const rows = Array.isArray(checkpoints) ? checkpoints : [];
  const active = isNewRestoreDimensionGateActive(summary);
  const dimensions = rows
    .map(row => normalizeRestoreDimension(row?.dimension || row?.category || row?.taxonomy))
    .filter(Boolean);
  const present = new Set(dimensions);
  const missing = [...RESTORE_REQUIRED_DIMENSIONS].filter(dimension => !present.has(dimension));
  const componentCount = dimensions.filter(dimension => dimension === 'component-proportion').length;
  const componentRatio = rows.length > 0 ? componentCount / rows.length : 0;
  const issues = [];

  if (missing.length > 0) {
    issues.push(`restoreVisualCheckpoints dimension coverage missing: ${missing.join(', ')}`);
  }
  if (componentCount < 2 && componentRatio < 0.25) {
    issues.push(`restoreVisualCheckpoints component-proportion coverage is insufficient: count=${componentCount}, ratio=${componentRatio.toFixed(2)}`);
  }

  for (const issue of issues) {
    if (active) {
      addError('restore-checkpoint-dimension-coverage', issue);
    } else {
      addWarning('restore-checkpoint-dimension-coverage', `${issue}; hard gate starts at skill version ${RESTORE_DIMENSION_GATE_VERSION}`);
    }
  }
}

function validateRestoreVisualDiffReview(project) {
  const review = project.visualDiffReview;
  if (!review || typeof review !== 'object') {
    addError('restore-visual-diff', 'project.visualDiffReview is required for restore_1to1 before final validation');
    return;
  }
  if (review.applies !== true) {
    addError('restore-visual-diff', 'project.visualDiffReview.applies must be true for restore_1to1');
  }
  const checks = Array.isArray(review.checks) ? review.checks : [];
  if (checks.length < 5 || checks.length > 12) {
    addError('restore-visual-diff', `project.visualDiffReview.checks must contain 5-12 checks; found ${checks.length}`);
  }
  let derivedBlockingMismatchCount = 0;
  for (const [index, check] of checks.entries()) {
    if (!check || typeof check !== 'object') {
      addError('restore-visual-diff', `visualDiffReview.checks[${index}] must be an object`);
      continue;
    }
    const status = String(check.status || '');
    const severity = String(check.severity || '');
    if (!RESTORE_VISUAL_DIFF_STATUSES.has(status)) {
      addError('restore-visual-diff', `visualDiffReview.checks[${index}].status must be matched, partial, or missing`);
    }
    if (!RESTORE_VISUAL_DIFF_SEVERITIES.has(severity)) {
      addError('restore-visual-diff', `visualDiffReview.checks[${index}].severity must be blocking or warning`);
    }
    if (severity === 'blocking' && (status === 'partial' || status === 'missing')) {
      derivedBlockingMismatchCount += 1;
    }
    for (const field of ['sourceFact', 'targetObservation']) {
      const value = String(check[field] || '');
      if (!value) addError('restore-visual-diff', `visualDiffReview.checks[${index}].${field} is required`);
      if (value.length > 100) addError('restore-visual-diff', `visualDiffReview.checks[${index}].${field} exceeds 100 chars`);
    }
    const repairInstruction = String(check.repairInstruction || '');
    if (repairInstruction.length > 120) {
      addError('restore-visual-diff', `visualDiffReview.checks[${index}].repairInstruction exceeds 120 chars`);
    }
  }
  const declaredBlockingMismatchCount = Number(review.blockingMismatchCount);
  if (!Number.isInteger(declaredBlockingMismatchCount) || declaredBlockingMismatchCount < 0) {
    addError('restore-visual-diff', 'project.visualDiffReview.blockingMismatchCount must be a non-negative integer');
  } else if (declaredBlockingMismatchCount !== derivedBlockingMismatchCount) {
    addError('restore-visual-diff', `project.visualDiffReview.blockingMismatchCount (${declaredBlockingMismatchCount}) must match blocking partial/missing checks (${derivedBlockingMismatchCount})`);
  }
  if (declaredBlockingMismatchCount > 0) {
    addError('restore-visual-diff', `project.visualDiffReview.blockingMismatchCount must be 0; found ${review.blockingMismatchCount}`);
  }
  if (review.allBlockingMismatchesResolved !== true) {
    addError('restore-visual-diff', 'project.visualDiffReview.allBlockingMismatchesResolved must be true');
  }
}

function validateRestoreSourceFactCoverage(summary) {
  console.log('\nChecking restore source fact coverage map...');

  if (!hasQualityEfficiencyGates(summary)) {
    console.log('  [OK] quality-efficiency gate inactive for this skill version');
    return;
  }

  if (!isRestoreSummary(summary)) {
    console.log('  [OK] Not restore_1to1; source fact coverage skipped');
    return;
  }

  const project = summary?.project || {};
  const facts = Array.isArray(project.measuredSourceFacts)
    ? project.measuredSourceFacts
    : (Array.isArray(project.restorationContractLite?.measuredSourceFacts)
      ? project.restorationContractLite.measuredSourceFacts
      : []);
  const checkpoints = Array.isArray(project.restoreVisualCheckpoints) ? project.restoreVisualCheckpoints : [];
  const coverage = Array.isArray(project.sourceFactCoverageMap)
    ? project.sourceFactCoverageMap
    : (Array.isArray(project.visualDiffReview?.sourceFactCoverageMap)
      ? project.visualDiffReview.sourceFactCoverageMap
      : []);

  const highFactIds = facts.filter(f => f?.priority === 'high').map(f => String(f.id || '').trim()).filter(Boolean);
  const highCheckpointIds = checkpoints.filter(c => c?.priority === 'high').map(c => String(c.id || '').trim()).filter(Boolean);

  if (coverage.length === 0) {
    addError('restore-source-fact-coverage', 'restore_1to1 requires project.sourceFactCoverageMap[] for high-priority source facts and checkpoints');
    return;
  }

  const coveredFactIds = new Set();
  const coveredCheckpointIds = new Set();
  for (const [index, row] of coverage.entries()) {
    if (!row || typeof row !== 'object') {
      addError('restore-source-fact-coverage', `sourceFactCoverageMap[${index}] must be an object`);
      continue;
    }
    const factId = String(row.sourceFactId || '').trim();
    const checkpointId = String(row.checkpointId || '').trim();
    const selector = String(row.selector || '').trim();
    const implementedProperty = String(row.implementedProperty || '').trim();
    if (!factId) addError('restore-source-fact-coverage', `sourceFactCoverageMap[${index}].sourceFactId is required`);
    if (!checkpointId) addError('restore-source-fact-coverage', `sourceFactCoverageMap[${index}].checkpointId is required`);
    if (!selector) addError('restore-source-fact-coverage', `sourceFactCoverageMap[${index}].selector is required`);
    if (!implementedProperty) addError('restore-source-fact-coverage', `sourceFactCoverageMap[${index}].implementedProperty is required`);
    if (factId) coveredFactIds.add(factId);
    if (checkpointId) coveredCheckpointIds.add(checkpointId);
  }

  for (const factId of highFactIds) {
    if (!coveredFactIds.has(factId)) {
      addError('restore-source-fact-coverage', `high-priority measuredSourceFact ${factId} has no sourceFactCoverageMap row`);
    }
  }
  for (const checkpointId of highCheckpointIds) {
    if (!coveredCheckpointIds.has(checkpointId)) {
      addError('restore-source-fact-coverage', `high-priority restoreVisualCheckpoint ${checkpointId} has no sourceFactCoverageMap row`);
    }
  }

  const checks = Array.isArray(project.visualDiffReview?.checks) ? project.visualDiffReview.checks : [];
  for (const [index, check] of checks.entries()) {
    if (check?.status !== 'matched' || check?.severity !== 'blocking') continue;
    if (!String(check.checkpointId || '').trim()) {
      addError('restore-source-fact-coverage', `visualDiffReview.checks[${index}] matched blocking row requires checkpointId`);
    }
    if (!String(check.selector || '').trim()) {
      addError('restore-source-fact-coverage', `visualDiffReview.checks[${index}] matched blocking row requires selector`);
    }
    if (!Array.isArray(check.measuredSourceFactIds) || check.measuredSourceFactIds.length === 0) {
      addError('restore-source-fact-coverage', `visualDiffReview.checks[${index}] matched blocking row requires measuredSourceFactIds[]`);
    }
  }
}

function validateRestoreReferenceImageBody(designDir, pages) {
  const suspiciousReferencePattern = /(?:src|background-image)\s*[:=][^>;\n]*(?:reference|screenshot|full-page|source)[^>;\n]*(?:png|jpg|jpeg|webp)/i;
  const dominantSizingPattern = /(fixed\s+inset-0|absolute\s+inset-0|w-full\s+h-full|min-h-screen|width\s*:\s*100%|height\s*:\s*100%|100vw|100vh|object-cover)/i;

  for (const page of pages) {
    const htmlPath = path.resolve(designDir, page.htmlSrc);
    if (!htmlPath.startsWith(`${path.join(designDir, 'pages')}${path.sep}`)) continue;
    if (!fs.existsSync(htmlPath)) continue;

    const content = readHtmlFileCached(htmlPath, page.htmlSrc);
    if (content === null) continue;
    if (suspiciousReferencePattern.test(content) && dominantSizingPattern.test(content)) {
      addError(
        'restore-evidence',
        `${page.htmlSrc}: appears to use a reference/screenshot image as dominant page body; rebuild visible UI as HTML/CSS components`
      );
    }
  }
}

function validateRestoreLargeVisualAssetGate(designDir, project, pages) {
  const facts = Array.isArray(project.measuredSourceFacts)
    ? project.measuredSourceFacts
    : (Array.isArray(project.restorationContractLite?.measuredSourceFacts)
      ? project.restorationContractLite.measuredSourceFacts
      : []);
  const focalFacts = facts.filter(fact => fact && fact.priority === 'high' && fact.category === 'focal-object');
  if (focalFacts.length === 0) return;

  const plan = Array.isArray(project.largeVisualRegionPlan) ? project.largeVisualRegionPlan : [];
  const plannedFactIds = new Set(plan.flatMap(item => {
    if (!item || typeof item !== 'object') return [];
    return [
      item.measuredSourceFactId,
      item.sourceFactId,
      item.factId,
      ...(Array.isArray(item.measuredSourceFactIds) ? item.measuredSourceFactIds : []),
    ].map(value => String(value || '').trim()).filter(Boolean);
  }));

  const factsWithoutPlan = focalFacts.filter(fact => {
    const id = String(fact.id || '').trim();
    if (fact.allowedDeviation || fact.allowedDeviationRef) return false;
    if (fact.assetPlanId || fact.largeVisualRegionPlanId) return false;
    return id && !plannedFactIds.has(id);
  });
  if (factsWithoutPlan.length > 0) {
    addError(
      'restore-large-visual-asset',
      `high-priority focal-object facts require assetPlanId, largeVisualRegionPlanId, largeVisualRegionPlan mapping, or allowedDeviation: ${factsWithoutPlan.map(fact => fact.id).join(', ')}`
    );
  }

  const allFocalFactsAllowedToDeviate = focalFacts.every(fact => fact.allowedDeviation || fact.allowedDeviationRef);
  if (allFocalFactsAllowedToDeviate) return;

  const html = pages
    .map(page => readPageHtml(designDir, page))
    .filter(Boolean)
    .join('\n');
  const assetImagePattern = /<img\b[^>]*\bsrc=["'][^"']*(?:\.\.\/assets\/|\/assets\/|assets\/)[^"']+["']/i;
  if (!assetImagePattern.test(html)) {
    addError(
      'restore-large-visual-asset',
      'high-priority focal-object facts require an <img> asset reference under assets/ or an explicit allowedDeviation'
    );
  }
}

function isGraphicLayoutStaticSummary(summary) {
  const project = summary?.project || {};
  return project.resolvedLane === 'graphic_layout_static' ||
    project.graphicStrategyGate === 'layout-static' ||
    project.layoutStaticRequired === true;
}

function validateGraphicLayoutCompleteness(designDir, summary) {
  console.log('\nChecking graphic layout-static completeness...');

  if (!isGraphicLayoutStaticSummary(summary)) {
    console.log('  [OK] Not graphic_layout_static; deliverable completeness gate skipped');
    return;
  }

  const project = summary?.project || {};
  if (project.layoutStaticRequired !== true) {
    addError('graphic-layout-completeness', 'graphic_layout_static requires project.layoutStaticRequired=true');
  }

  const checklist = project.deliverableCompletenessChecklist;
  if (!checklist || typeof checklist !== 'object') {
    addError('graphic-layout-completeness', 'graphic_layout_static requires project.deliverableCompletenessChecklist before final validation');
    return;
  }

  for (const field of ['requiredPagesOrAssets', 'requiredCopyBlocks', 'requiredInfoTypes', 'missingRequiredItems']) {
    if (!Array.isArray(checklist[field])) {
      addError('graphic-layout-completeness', `deliverableCompletenessChecklist.${field} must be an array`);
    }
  }

  const missing = Array.isArray(checklist.missingRequiredItems) ? checklist.missingRequiredItems : [];
  if (missing.length > 0) {
    addError('graphic-layout-completeness', `deliverableCompletenessChecklist.missingRequiredItems must be empty; found ${missing.join(', ')}`);
  }

  const expectedPageCount = checklist.expectedPageCount;
  const actualPageCount = checklist.actualPageCount;
  if (!Number.isInteger(expectedPageCount) || expectedPageCount < 1) {
    addError('graphic-layout-completeness', 'deliverableCompletenessChecklist.expectedPageCount must be a positive integer');
  }
  if (!Number.isInteger(actualPageCount) || actualPageCount < 0) {
    addError('graphic-layout-completeness', 'deliverableCompletenessChecklist.actualPageCount must be a non-negative integer');
  }
  if (Number.isInteger(expectedPageCount) && Number.isInteger(actualPageCount) && actualPageCount < expectedPageCount) {
    addError('graphic-layout-completeness', `actualPageCount ${actualPageCount} is less than expectedPageCount ${expectedPageCount}`);
  }

  if (!GRAPHIC_SOURCE_MATERIAL_COVERAGE.has(checklist.sourceMaterialCoverage)) {
    addError('graphic-layout-completeness', 'deliverableCompletenessChecklist.sourceMaterialCoverage must be complete or partial');
  }
  if (
    project.textCriticality === 'high' &&
    checklist.sourceMaterialCoverage !== 'complete' &&
    checklist.userApprovedReduction !== true
  ) {
    addError('graphic-layout-completeness', 'text-critical layout-static deliverables require complete sourceMaterialCoverage unless userApprovedReduction=true');
  }

  if (checklist.blocking === true) {
    addError('graphic-layout-completeness', 'deliverableCompletenessChecklist.blocking must not be true at final validation');
  } else if (checklist.blocking !== false) {
    addError('graphic-layout-completeness', 'deliverableCompletenessChecklist.blocking must be false at final validation');
  }

  if (hasQualityEfficiencyGates(summary) && project.textCriticality === 'high') {
    validateTextCriticalCopyBlocks(designDir, checklist, project);
  }
}

function validateTextCriticalCopyBlocks(designDir, checklist, project) {
  const blocks = Array.isArray(checklist.requiredCopyBlocks) ? checklist.requiredCopyBlocks : [];
  if (blocks.length === 0) {
    addError('text-critical-layout', 'text-critical layout requires deliverableCompletenessChecklist.requiredCopyBlocks[]');
    return;
  }

  const evidence = Array.isArray(project.copyBlockEvidence) ? project.copyBlockEvidence : [];
  if (evidence.length === 0) {
    addError('text-critical-layout', 'text-critical layout requires project.copyBlockEvidence[] before final validation');
  }

  let primaryCount = 0;
  for (const [index, block] of blocks.entries()) {
    if (!block || typeof block !== 'object' || Array.isArray(block)) {
      addError('text-critical-layout', `requiredCopyBlocks[${index}] must be an object with label, text, htmlSrc, selector, and role`);
      continue;
    }
    const label = String(block.label || '').trim();
    const text = String(block.text || '').trim();
    const htmlSrc = String(block.htmlSrc || '').trim();
    const selector = String(block.selector || '').trim();
    const role = String(block.role || '').trim();
    if (!label) addError('text-critical-layout', `requiredCopyBlocks[${index}].label is required`);
    if (!text) addError('text-critical-layout', `requiredCopyBlocks[${index}].text is required`);
    if (!htmlSrc) addError('text-critical-layout', `requiredCopyBlocks[${index}].htmlSrc is required`);
    if (!selector) addError('text-critical-layout', `requiredCopyBlocks[${index}].selector is required`);
    if (!role) addError('text-critical-layout', `requiredCopyBlocks[${index}].role is required`);
    if (role === 'primary') primaryCount += 1;
    if (!htmlSrc || !selector) continue;

    const content = readPageHtml(designDir, { htmlSrc });
    if (content === null) continue;
    const tag = findOpeningTagBySelector(content, selector);
    if (!tag) {
      addError('text-critical-layout', `${htmlSrc}: required copy selector not found: ${selector}`);
      continue;
    }
    if (tagIsHiddenByDefault(tag)) {
      addError('text-critical-layout', `${htmlSrc}: required copy selector is hidden by default: ${selector}`);
    }
    if (!selectorTextAppears(content, selector, text)) {
      addError('text-critical-layout', `${htmlSrc}: required copy selector ${selector} does not contain expected text "${text}"`);
    }
  }

  const hierarchy = checklist.hierarchyContract || project.hierarchyContract || {};
  const expectedPrimaryCount = Number.isInteger(hierarchy.primaryCount) ? hierarchy.primaryCount : 1;
  if (primaryCount !== expectedPrimaryCount) {
    addError('text-critical-layout', `requiredCopyBlocks role=primary count ${primaryCount} must equal hierarchy primaryCount ${expectedPrimaryCount}`);
  }
}

function validateDefaultDeliverableVisibility(designDir, summary) {
  console.log('\nChecking default deliverable visibility...');

  if (!hasQualityEfficiencyGates(summary)) {
    console.log('  [OK] quality-efficiency gate inactive for this skill version');
    return;
  }

  const gate = summary?.project?.defaultDeliverableVisibility;
  if (!gate || gate.applies !== true) {
    console.log('  [OK] default deliverable visibility gate skipped');
    return;
  }

  const required = Array.isArray(gate.requiredVisibleRegions) ? gate.requiredVisibleRegions : [];
  if (required.length === 0) {
    addError('default-deliverable-visibility', 'defaultDeliverableVisibility.requiredVisibleRegions[] is required when applies=true');
    return;
  }

  for (const [index, region] of required.entries()) {
    if (!region || typeof region !== 'object') {
      addError('default-deliverable-visibility', `requiredVisibleRegions[${index}] must be an object`);
      continue;
    }
    const htmlSrc = String(region.htmlSrc || '').trim();
    const selector = String(region.selector || '').trim();
    if (!htmlSrc) addError('default-deliverable-visibility', `requiredVisibleRegions[${index}].htmlSrc is required`);
    if (!selector) addError('default-deliverable-visibility', `requiredVisibleRegions[${index}].selector is required`);
    if (!htmlSrc || !selector) continue;

    const content = readPageHtml(designDir, { htmlSrc });
    if (content === null) continue;
    const tag = findOpeningTagBySelector(content, selector);
    if (!tag) {
      addError('default-deliverable-visibility', `${htmlSrc}: required visible selector not found: ${selector}`);
      continue;
    }
    if (tagIsHiddenByDefault(tag)) {
      addError('default-deliverable-visibility', `${htmlSrc}: required visible selector is hidden by default: ${selector}`);
      addRepairPlanHint('default-deliverable-visibility', {
        owner: 'sub-agent',
        repairScope: 'targeted-visibility-fix',
        strategy: 'targeted_visibility_fix_once',
        affectedFiles: [htmlSrc],
        allowSourceRead: 'no-full-html-read',
        maxValidationRuns: 2
      });
    }
  }
}

function getValidationRunDisciplineStatus(summary) {
  const project = summary?.project || {};
  const discipline = project.validationRunDiscipline || {};
  const history = Array.isArray(project.validationHistory) ? project.validationHistory : [];
  const countedHistory = history.filter(item => !isDiagnosticHistoryRecord(item));
  const ledger = Array.isArray(project.validationRepairLedger) ? project.validationRepairLedger : [];
  const declaredMaxFullValidationRuns = Number.isInteger(discipline.maxFullValidationRuns) ? discipline.maxFullValidationRuns : null;
  const isRestore = isRestoreSummary(summary);
  const maxFullValidationRuns = isRestore
    ? Math.min(declaredMaxFullValidationRuns ?? RESTORE_MAX_FULL_VALIDATION_RUNS, RESTORE_MAX_FULL_VALIDATION_RUNS)
    : declaredMaxFullValidationRuns;
  const violations = [];
  let terminalState = null;

  if (maxFullValidationRuns !== null && countedHistory.length > maxFullValidationRuns) {
    const prefix = isRestore ? 'VALIDATION_LIMIT_EXCEEDED: ' : '';
    violations.push(`${prefix}validationHistory has ${countedHistory.length} full validation run(s), max allowed is ${maxFullValidationRuns}`);
    terminalState = 'validation-budget-exhausted';
  }

  if (discipline.softWarningsTriggerRepair === false) {
    for (const [index, item] of ledger.entries()) {
      const trigger = String(item?.trigger || item?.repairTrigger || item?.reason || '').trim();
      if (/soft-warning-only|warning-only|provenance-warning-only|style-warning-only/i.test(trigger)) {
        violations.push(`validationRepairLedger[${index}] was triggered by non-blocking warning: ${trigger}`);
      }
    }
  }

  return {
    declared: Boolean(project.validationRunDiscipline),
    restoreMode: isRestore,
    maxFullValidationRuns,
    validationHistoryCount: countedHistory.length,
    repairLedgerCount: ledger.length,
    softWarningsTriggerRepair: discipline.softWarningsTriggerRepair ?? null,
    terminalState,
    nextAction: terminalState ? 'stop_and_report_blocking_summary' : null,
    violations,
    success: violations.length === 0,
  };
}

function validateValidationRunDiscipline(summary) {
  console.log('\nChecking validation run discipline...');

  if (!hasQualityEfficiencyGates(summary)) {
    console.log('  [OK] quality-efficiency gate inactive for this skill version');
    return;
  }

  const status = getValidationRunDisciplineStatus(summary);
  if (!status.declared) {
    const history = Array.isArray(summary?.project?.validationHistory) ? summary.project.validationHistory : [];
    if (status.restoreMode) {
      for (const violation of status.violations) {
          if (status.terminalState) addWarning('validation-discipline', violation);
          else addError('validation-discipline', violation);
      }
        if (status.terminalState) terminalValidationState = status;
      if (status.violations.length === 0) {
        console.log(`  [OK] restore default max of ${RESTORE_MAX_FULL_VALIDATION_RUNS} full validation runs not exceeded`);
      }
    } else if (status.validationHistoryCount > 2) {
        terminalValidationState = {
          ...status,
          terminalState: 'validation-budget-exhausted',
          nextAction: 'stop_and_report_blocking_summary',
        };
        addWarning('validation-discipline', `validationRunDiscipline not declared but validationHistory has ${status.validationHistoryCount} run(s); default max is 2`);
    } else {
      console.log('  [OK] No validation run discipline declared; default max of 2 runs not exceeded');
    }
    return;
  }
  for (const violation of status.violations) {
      if (status.terminalState) addWarning('validation-discipline', violation);
      else addError('validation-discipline', violation);
  }
    if (status.terminalState) terminalValidationState = status;
  if (status.violations.length === 0) {
    console.log('  [OK] validation run discipline respected');
  }
}

function validateLibraryBoundCustomCss(designDir) {
  console.log('\nChecking Library-bound custom CSS restrictions...');

  const summary = loadOrchestrationSummary(designDir);
  const operatingMode = summary?.designSource?.operatingMode;
  if (operatingMode !== 'library-bound') {
    console.log('  [OK] Not Library-bound; custom CSS class restriction skipped');
    return;
  }

  const pagesDir = path.join(designDir, 'pages');
  if (!fs.existsSync(pagesDir)) return;

  const htmlFiles = fs.readdirSync(pagesDir).filter(f => f.endsWith('.html'));
  if (htmlFiles.length === 0) return;

  const classDefinitionPattern = /\.([a-zA-Z_][a-zA-Z0-9_-]*)\s*\{/g;

  for (const htmlFile of htmlFiles) {
    const htmlPath = path.join(pagesDir, htmlFile);
    const content = readHtmlFileCached(htmlPath, htmlFile);
    if (content === null) continue;

    const customStyleBlocks = detectNonInfrastructureStyleBlocks(content);
    for (const block of customStyleBlocks) {
      const classes = [...block.matchAll(classDefinitionPattern)].map(match => match[1]);
      if (classes.length === 0) continue;

      addWarning(
        'library-bound-css',
        `${htmlFile}: Library-bound mode discourages custom CSS class definitions in <style> blocks ` +
        `(${[...new Set(classes)].slice(0, 8).map(name => `.${name}`).join(', ')}). ` +
        `Prefer Tailwind utilities plus Library brand CSS variables/component JSON instead.`
      );
    }
  }
}

function loadOrchestrationSummary(designDir) {
  const summaryPath = path.join(designDir, 'runtime-orchestration-summary.json');
  if (!fs.existsSync(summaryPath)) {
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(summaryPath, 'utf8'));
  } catch (error) {
    addWarning('orchestration-summary', `Cannot parse runtime-orchestration-summary.json: ${error.message}`);
    return null;
  }
}

function readSkillManifest() {
  if (!fs.existsSync(SKILL_MANIFEST_PATH)) return null;
  try {
    return JSON.parse(fs.readFileSync(SKILL_MANIFEST_PATH, 'utf8'));
  } catch {
    return null;
  }
}

function normalizeSkillProvenance(summary) {
  const manifest = readSkillManifest();
  const provenance = summary?.skillProvenance;
  if (provenance && typeof provenance === 'object') {
    const mismatch = manifest?.version && provenance.version && manifest.version !== provenance.version;
    return {
      name: provenance.name ?? null,
      version: provenance.version ?? null,
      version_source: provenance.version_source ?? 'unknown',
      runtime_skill_dir: provenance.runtime_skill_dir ?? null,
      recorded_at: provenance.recorded_at ?? null,
      expected_version: manifest?.version ?? null,
      status: mismatch ? 'mismatch' : (provenance.version ? 'matched' : 'observed_unknown'),
      read_status: provenance.read_status ?? (provenance.version ? 'ok' : 'unknown')
    };
  }

  if (manifest?.version) {
    return {
      name: manifest.name ?? 'solo-design',
      version: manifest.version,
      version_source: manifest.version_source ?? 'skill-release-manifest.json',
      runtime_skill_dir: SKILL_DIR,
      recorded_at: null,
      expected_version: manifest.version,
      status: 'manifest_fallback',
      read_status: 'ok',
      reason: 'runtime-orchestration-summary.json missing skillProvenance; used skill-release-manifest.json'
    };
  }

  return {
    name: 'solo-design',
    version: null,
    version_source: 'unknown',
    runtime_skill_dir: null,
    recorded_at: null,
    read_status: 'missing',
    reason: 'runtime-orchestration-summary.json missing skillProvenance'
  };
}

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function hashString(value) {
  return crypto.createHash('sha256').update(String(value)).digest('hex');
}

function normalizeSummaryForHash(summary) {
  if (!summary || typeof summary !== 'object') return summary;
  const cloned = JSON.parse(JSON.stringify(summary));
  if (cloned.project && typeof cloned.project === 'object') {
    for (const field of SUMMARY_MUTABLE_FIELDS) {
      delete cloned.project[field];
    }
  }
  return cloned;
}

function sha256File(filePath) {
  const stat = fs.statSync(filePath);
  const cacheKey = `${path.resolve(filePath)}:${stat.size}:${stat.mtimeMs}`;
  const cached = fileHashCache.get(cacheKey);
  if (typeof cached === 'string') return cached;
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
  const digest = hash.digest('hex');
  fileHashCache.set(cacheKey, digest);
  return digest;
}

async function sha256FileAsync(filePath) {
  const stat = fs.statSync(filePath);
  const cacheKey = `${path.resolve(filePath)}:${stat.size}:${stat.mtimeMs}`;
  const cached = fileHashCache.get(cacheKey);
  if (typeof cached === 'string') return cached;
  if (cached) return cached;

  const promise = (async () => {
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
  })();

  fileHashCache.set(cacheKey, promise);
  const digest = await promise;
  fileHashCache.set(cacheKey, digest);
  return digest;
}

function hashProjectFile(filePath, relPath) {
  if (relPath === 'runtime-orchestration-summary.json') {
    try {
      const summary = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      return hashString(stableJson(normalizeSummaryForHash(summary)));
    } catch {
      return sha256File(filePath);
    }
  }
  return sha256File(filePath);
}

async function hashProjectFileAsync(filePath, relPath) {
  if (relPath === 'runtime-orchestration-summary.json') {
    try {
      const summary = JSON.parse(await fs.promises.readFile(filePath, 'utf8'));
      return hashString(stableJson(normalizeSummaryForHash(summary)));
    } catch {
      return sha256FileAsync(filePath);
    }
  }
  return sha256FileAsync(filePath);
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

async function collectProjectFileHashes(designDir) {
  const relPaths = [];
  function addRelPath(relPath) {
    relPaths.push(relPath.replace(/\\/g, '/'));
  }
  function addIfExists(relPath) {
    const filePath = path.join(designDir, relPath);
    if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
      addRelPath(relPath);
    }
  }

  for (const entry of fs.readdirSync(designDir, { withFileTypes: true })) {
    if (entry.isFile() && entry.name.endsWith('.design')) addRelPath(entry.name);
  }
  addIfExists('colors_and_type.css');
  addIfExists('runtime-orchestration-summary.json');
  addIfExists('page-generation-summary.json');

  const pagesDir = path.join(designDir, 'pages');
  if (fs.existsSync(pagesDir)) {
    for (const entry of fs.readdirSync(pagesDir, { withFileTypes: true })) {
      if (entry.isFile() && entry.name.endsWith('.html')) addRelPath(path.join('pages', entry.name));
    }
  }

  const assetsDir = path.join(designDir, 'assets');
  let assetEntryCount = 0;
  let assetDepthWarningEmitted = false;
  let assetCountWarningEmitted = false;
  function visitAssets(dir, prefix, depth = 0) {
    if (!fs.existsSync(dir)) return;
    if (depth > MAX_PROJECT_HASH_ASSET_DEPTH) {
      if (!assetDepthWarningEmitted) {
        addWarning('project-hash', `assets/ traversal exceeded max depth ${MAX_PROJECT_HASH_ASSET_DEPTH}; deeper assets skipped`);
        assetDepthWarningEmitted = true;
      }
      return;
    }
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const rel = path.join(prefix, entry.name);
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        visitAssets(full, rel, depth + 1);
      } else if (entry.isFile() && HASH_IMAGE_EXTENSIONS.has(path.extname(entry.name).toLowerCase())) {
        if (assetEntryCount >= MAX_PROJECT_HASH_ASSET_ENTRIES) {
          if (!assetCountWarningEmitted) {
            addWarning('project-hash', `assets/ traversal reached max image count ${MAX_PROJECT_HASH_ASSET_ENTRIES}; remaining assets skipped`);
            assetCountWarningEmitted = true;
          }
          continue;
        }
        assetEntryCount += 1;
        addRelPath(rel);
      }
    }
  }
  visitAssets(assetsDir, 'assets');

  const entries = await mapLimit(relPaths, 8, async relPath => {
    const filePath = path.join(designDir, relPath);
    return [relPath, await hashProjectFileAsync(filePath, relPath)];
  });
  const hashes = {};
  for (const [relPath, hash] of entries) hashes[relPath] = hash;
  return hashes;
}

function classAttrContains(tag, className) {
  const match = tag.match(/\bclass=["']([^"']*)["']/i);
  if (!match) return false;
  return match[1].split(/\s+/).includes(className);
}

function compareVersion(a, b) {
  const left = String(a || '').split(/[.-]/).map(part => Number(part) || 0);
  const right = String(b || '').split(/[.-]/).map(part => Number(part) || 0);
  const len = Math.max(left.length, right.length);
  for (let i = 0; i < len; i += 1) {
    const diff = (left[i] || 0) - (right[i] || 0);
    if (diff !== 0) return diff;
  }
  return 0;
}

function hasQualityEfficiencyGates(summary) {
  const version = summary?.skillProvenance?.version || readSkillManifest()?.version;
  return Boolean(version) && compareVersion(version, QUALITY_EFFICIENCY_GATE_VERSION) >= 0;
}

function normalizePageRecord(page) {
  if (!page || typeof page.htmlSrc !== 'string') return null;
  return {
    nodeId: page.nodeId ?? page.id ?? null,
    title: page.title ?? null,
    htmlSrc: page.htmlSrc,
    viewportMode: page.viewportMode ?? null,
    mobileNavigationApplies: page.mobileNavigationApplies,
    mobileNavigationActiveKey: page.mobileNavigationActiveKey ?? null,
    mobileNavigationOmitReason: page.mobileNavigationOmitReason ?? null
  };
}

function loadDesignProjectFacts(designDir, designFiles, summary) {
  const pagesByHtmlSrc = new Map();
  let designDeviceType = null;
  const designDeviceTypes = [];

  if (Array.isArray(designFiles)) {
    for (const designFile of designFiles) {
      const designJson = readDesignJson(designDir, designFile);
      if (!designJson) continue;

      if (typeof designJson?.config?.deviceType === 'string') {
        designDeviceTypes.push(designJson.config.deviceType);
        if (!designDeviceType) {
          designDeviceType = designJson.config.deviceType;
        }
      }

      const nodes = Array.isArray(designJson?.data) ? designJson.data : [];
      for (const node of nodes) {
        if (node?.type !== 'page') continue;
        const htmlSrc = node?.devMetadata?.htmlSrc;
        if (typeof htmlSrc !== 'string') continue;
        pagesByHtmlSrc.set(htmlSrc, {
          nodeId: node.id ?? null,
          title: node.title ?? null,
          htmlSrc,
          viewportMode: null
        });
      }
    }
  }

  const summaryPages = Array.isArray(summary?.pages) ? summary.pages : [];
  for (const page of summaryPages) {
    const normalized = normalizePageRecord(page);
    if (!normalized) continue;
    pagesByHtmlSrc.set(normalized.htmlSrc, {
      ...(pagesByHtmlSrc.get(normalized.htmlSrc) || {}),
      ...normalized
    });
  }

  const summaryDeviceType = typeof summary?.project?.deviceType === 'string'
    ? summary.project.deviceType
    : null;
  const sharedProjectShellContract = summary?.project?.sharedProjectShellContract &&
    typeof summary.project.sharedProjectShellContract === 'object'
    ? summary.project.sharedProjectShellContract
    : null;
  const mobileNavigation = sharedProjectShellContract?.mobileNavigation &&
    typeof sharedProjectShellContract.mobileNavigation === 'object'
    ? sharedProjectShellContract.mobileNavigation
    : null;

  return {
    deviceType: summaryDeviceType || designDeviceType || null,
    summaryDeviceType,
    designDeviceType,
    designDeviceTypes,
    dashboardMode: summary?.project?.dashboardMode === true,
    deviceTypeSource: summaryDeviceType
      ? 'orchestration-summary'
      : (designDeviceType ? '.design.config.deviceType' : 'unknown'),
    summaryPresent: Boolean(summary),
    sharedProjectShellContract,
    mobileNavigation,
    pages: Array.from(pagesByHtmlSrc.values())
  };
}

function hasRuntimeContractGates(summary) {
  if (!summary) return false;
  const version = summary.skillProvenance?.version;
  if (!version) return true;
  return compareVersion(version, '2026.07.04.2') >= 0;
}

function hasMobileNavigationDispatchGate(summary) {
  if (!summary) return false;
  const manifest = summary?.project?.dispatchPreflightManifest;
  if (Array.isArray(manifest) && manifest.length > 0) return true;
  const version = summary.skillProvenance?.version;
  return Boolean(version) && compareVersion(version, '2026.07.06.8') >= 0;
}

function validateDeviceTypeConsistency(projectFacts) {
  console.log('\nChecking device type consistency...');

  const summaryDeviceType = projectFacts?.summaryDeviceType;
  const designDeviceType = projectFacts?.designDeviceType;
  const designDeviceTypes = Array.isArray(projectFacts?.designDeviceTypes)
    ? projectFacts.designDeviceTypes
    : [];
  const uniqueDesignDeviceTypes = [...new Set(designDeviceTypes)];

  if (uniqueDesignDeviceTypes.length > 1) {
    addError(
      'device-type-consistency',
      `multiple .design files declare different config.deviceType values: ${uniqueDesignDeviceTypes.join(', ')}`
    );
    return;
  }

  if (summaryDeviceType && designDeviceType && summaryDeviceType !== designDeviceType) {
    addError(
      'device-type-consistency',
      `orchestration-summary project.deviceType="${summaryDeviceType}" does not match .design config.deviceType="${designDeviceType}". Fix .design config before final delivery.`
    );
    return;
  }

  if (summaryDeviceType && !designDeviceType) {
    addError(
      'device-type-consistency',
      `orchestration-summary project.deviceType="${summaryDeviceType}" exists but .design config.deviceType is missing. Generated design projects must declare config.deviceType.`
    );
    return;
  }

  if (projectFacts?.dashboardMode === true && projectFacts?.deviceType === 'freeSize') {
    addError(
      'device-type-consistency',
      'dashboardMode=true must use deviceType="desktop", not "freeSize". Data-screen dashboards need a stable desktop canvas viewport.'
    );
    return;
  }

  if (summaryDeviceType || designDeviceType) {
    console.log(`  [OK] Device type resolved as ${projectFacts.deviceType} (${projectFacts.deviceTypeSource})`);
  } else {
    console.log('  [OK] No project device type declared');
  }
}

function readHtmlFileCached(htmlPath, displayPath = path.basename(htmlPath)) {
  const resolvedHtmlPath = path.resolve(htmlPath);
  if (pageHtmlCache.has(resolvedHtmlPath)) return pageHtmlCache.get(resolvedHtmlPath);

  if (!fs.existsSync(resolvedHtmlPath)) {
    if (!pageHtmlReadErrors.has(resolvedHtmlPath)) {
      addError('html-files', `${displayPath}: HTML file not found`);
      pageHtmlReadErrors.add(resolvedHtmlPath);
    }
    pageHtmlCache.set(resolvedHtmlPath, null);
    return null;
  }

  try {
    const stat = fs.statSync(resolvedHtmlPath);
    if (!stat.isFile()) {
      if (!pageHtmlReadErrors.has(resolvedHtmlPath)) {
        addError('html-files', `${displayPath}: expected a file but found a non-file path`);
        pageHtmlReadErrors.add(resolvedHtmlPath);
      }
      pageHtmlCache.set(resolvedHtmlPath, null);
      return null;
    }
    if (stat.size > MAX_PAGE_HTML_BYTES) {
      if (!pageHtmlReadErrors.has(resolvedHtmlPath)) {
        addError(
          'html-files',
          `${displayPath}: HTML file is too large (${stat.size} bytes; max ${MAX_PAGE_HTML_BYTES}). ` +
          'Move large inline assets to assets/ and keep page HTML lightweight before validation.'
        );
        pageHtmlReadErrors.add(resolvedHtmlPath);
      }
      pageHtmlCache.set(resolvedHtmlPath, null);
      return null;
    }
    const content = fs.readFileSync(resolvedHtmlPath, 'utf8');
    pageHtmlCache.set(resolvedHtmlPath, content);
    return content;
  } catch (error) {
    if (!pageHtmlReadErrors.has(resolvedHtmlPath)) {
      addError('html-files', `${displayPath}: cannot read HTML file (${error.message})`);
      pageHtmlReadErrors.add(resolvedHtmlPath);
    }
    pageHtmlCache.set(resolvedHtmlPath, null);
    return null;
  }
}

function readPageHtml(designDir, page) {
  if (!page || typeof page.htmlSrc !== 'string') return null;
  const pagesDir = path.join(designDir, 'pages');
  const htmlPath = path.resolve(designDir, page.htmlSrc);
  if (!htmlPath.startsWith(`${pagesDir}${path.sep}`)) {
    const key = `outside:${designDir}:${page.htmlSrc}`;
    if (!pageHtmlReadErrors.has(key)) {
      addError('html-files', `${page.htmlSrc}: htmlSrc must stay under pages/`);
      pageHtmlReadErrors.add(key);
    }
    return null;
  }
  return readHtmlFileCached(htmlPath, page.htmlSrc);
}

function getOpeningTagsAfterBody(content, limit = 8) {
  const bodyIndex = content.search(/<body\b/i);
  if (bodyIndex < 0) return [];
  const bodySlice = content.slice(bodyIndex);
  return (bodySlice.match(/<[a-zA-Z][\w:-]*(?:\s[^>]*)?>/g) || []).slice(0, limit + 1);
}

function tagHasLockedViewportClasses(tag) {
  return classAttrContains(tag, 'h-screen') && classAttrContains(tag, 'overflow-hidden');
}

function hasFixedMobileViewportHeight(content) {
  return /\b(?:min-)?height\s*:\s*(?:812|844)px\b/i.test(content) ||
    /\b(?:min-)?height\s*:\s*calc\(\s*(?:812|844)px\b/i.test(content);
}

function hasOverflowHidden(content) {
  return /\boverflow-hidden\b/i.test(content) || /overflow\s*:\s*hidden\b/i.test(content);
}

function hasLockedMobileViewport(content) {
  const bodyTag = (content.match(/<body\b[^>]*>/i) || [''])[0];
  if (tagHasLockedViewportClasses(bodyTag)) return true;

  const openingTags = getOpeningTagsAfterBody(content, 8).slice(1);
  if (openingTags.some(tag => tagHasLockedViewportClasses(tag))) return true;

  return hasFixedMobileViewportHeight(content) && hasOverflowHidden(content);
}

function getTagAttr(tag, attrName) {
  const match = tag.match(new RegExp(`\\b${attrName}=["']([^"']*)["']`, 'i'));
  return match ? match[1] : '';
}

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function findOpeningTagBySelector(content, selector) {
  const raw = String(selector || '').trim();
  if (!raw) return null;

  if (raw.startsWith('#')) {
    const id = escapeRegExp(raw.slice(1));
    return content.match(new RegExp(`<([a-zA-Z][\\w:-]*)\\b[^>]*\\bid=["']${id}["'][^>]*>`, 'i'))?.[0] || null;
  }

  if (raw.startsWith('.')) {
    const cls = escapeRegExp(raw.slice(1));
    return content.match(new RegExp(`<([a-zA-Z][\\w:-]*)\\b[^>]*\\bclass=["'][^"']*(?:^|\\s)${cls}(?:\\s|$)[^"']*["'][^>]*>`, 'i'))?.[0] || null;
  }

  const domIdMatch = raw.match(/^\[data-dom-id=["']([^"']+)["']\]$/);
  if (domIdMatch) {
    const domId = escapeRegExp(domIdMatch[1]);
    return content.match(new RegExp(`<([a-zA-Z][\\w:-]*)\\b[^>]*\\bdata-dom-id=["']${domId}["'][^>]*>`, 'i'))?.[0] || null;
  }

  return null;
}

function tagIsHiddenByDefault(tag) {
  if (!tag) return false;
  const cls = getTagAttr(tag, 'class');
  const style = getTagAttr(tag, 'style');
  if (/\bhidden\b|\binvisible\b|\bopacity-0\b/.test(cls)) return true;
  if (/\bhidden(?:\s|>|$)/i.test(tag)) return true;
  if (/\baria-hidden=["']true["']/i.test(tag)) return true;
  if (/display\s*:\s*none/i.test(style)) return true;
  if (/visibility\s*:\s*hidden/i.test(style)) return true;
  if (/opacity\s*:\s*0(?:\D|$)/i.test(style)) return true;
  return false;
}

function selectorTextAppears(content, selector, expectedText) {
  const text = String(expectedText || '').trim();
  if (!text) return true;
  const tag = findOpeningTagBySelector(content, selector);
  if (!tag) return false;
  const tagName = (tag.match(/^<([a-zA-Z][\w:-]*)\b/) || [])[1];
  if (!tagName) return content.includes(text);
  const start = content.indexOf(tag);
  if (start < 0) return content.includes(text);
  const close = content.indexOf(`</${tagName}>`, start + tag.length);
  const slice = close >= 0 ? content.slice(start, close) : content.slice(start, start + 4096);
  return slice.includes(text);
}

function collectCssCustomProperties(content) {
  return new Set([...content.matchAll(/--([a-zA-Z0-9-]+)\s*:/g)].map(match => match[1]));
}

function extractCssVarRefs(value) {
  return [...String(value || '').matchAll(/var\(\s*--([a-zA-Z0-9-]+)\s*(?:,\s*([^)]+))?\)/g)]
    .map(match => ({ name: match[1], hasFallback: Boolean(match[2]?.trim()) }));
}

function findUnresolvedCssVarRefs(value, declaredVars) {
  return extractCssVarRefs(value).filter(ref => !declaredVars.has(ref.name) && !ref.hasFallback);
}

function formatCssVarRefs(refs) {
  return refs.map(ref => `--${ref.name}`).join(', ');
}

function tagHasMinViewportHeight(tag) {
  return /\bmin-h-screen\b/i.test(tag) ||
    /min-height\s*:\s*100vh\b/i.test(tag) ||
    /min-height\s*:\s*calc\(\s*100vh\b/i.test(tag);
}

function isTransparentBackgroundValue(value) {
  return /(?:^|\s)(?:transparent|none|inherit|initial|unset)(?:\s|$)/i.test(String(value || '').trim());
}

function extractInlineBackgroundValues(tag) {
  const style = getTagAttr(tag, 'style');
  if (!style) return [];
  return [...style.matchAll(/(?:^|;)\s*(?:background|background-color)\s*:\s*([^;]+)/gi)]
    .map(match => match[1].trim())
    .filter(value => !isTransparentBackgroundValue(value));
}

function extractCssBodyBackgroundValues(content) {
  const values = [];
  const bodyRulePattern = /\bbody\s*\{([^}]*)\}/gi;
  let bodyRuleMatch;
  while ((bodyRuleMatch = bodyRulePattern.exec(content)) !== null) {
    const declarations = bodyRuleMatch[1];
    for (const match of declarations.matchAll(/(?:^|;)\s*(?:background|background-color)\s*:\s*([^;]+)/gi)) {
      const value = match[1].trim();
      if (!isTransparentBackgroundValue(value)) {
        values.push(value);
      }
    }
  }
  return values;
}

function resolveBackgroundClassValue(className, content, declaredVars) {
  if (className === 'bg-transparent' || className === 'bg-none') return null;

  const arbitraryMatch = className.match(/^bg-\[(.+)\]$/);
  if (arbitraryMatch) {
    return arbitraryMatch[1].replace(/_/g, ' ');
  }

  const tokenMatch = className.match(/^bg-([a-zA-Z0-9-]+)$/);
  if (!tokenMatch) return null;

  const token = tokenMatch[1];
  const fallbackClassPattern = new RegExp(`\\.bg-${escapeRegExp(token)}\\s*\\{[^}]*background(?:-color)?\\s*:\\s*([^;}]+)`, 'i');
  const fallbackClassMatch = content.match(fallbackClassPattern);
  if (fallbackClassMatch) {
    return fallbackClassMatch[1].trim();
  }

  if (declaredVars.has(`color-${token}`)) {
    return `var(--color-${token})`;
  }
  if (declaredVars.has(token)) {
    return `var(--${token})`;
  }

  // Literal Tailwind color classes still cover the host background. Other
  // quality checks can warn about token fidelity; this gate focuses on coverage.
  if (!/^(?:opacity|transparent|none)$/.test(token)) {
    return 'literal-tailwind-background';
  }

  return null;
}

function analyzeTagBackground(tag, content, declaredVars) {
  const values = extractInlineBackgroundValues(tag);
  const classAttr = getTagAttr(tag, 'class');
  if (classAttr) {
    for (const className of classAttr.split(/\s+/).filter(Boolean)) {
      const classValue = resolveBackgroundClassValue(className, content, declaredVars);
      if (classValue) {
        values.push(classValue);
      }
    }
  }

  const unresolved = values.flatMap(value => findUnresolvedCssVarRefs(value, declaredVars));
  return {
    declaresBackground: values.length > 0,
    hasResolvableBackground: values.length > 0 && unresolved.length === 0,
    unresolved
  };
}

function analyzeBodyBackground(content, bodyTag, declaredVars) {
  const tagAnalysis = analyzeTagBackground(bodyTag, content, declaredVars);
  const cssValues = extractCssBodyBackgroundValues(content);
  const cssUnresolved = cssValues.flatMap(value => findUnresolvedCssVarRefs(value, declaredVars));

  return {
    declaresBackground: tagAnalysis.declaresBackground || cssValues.length > 0,
    hasResolvableBackground: tagAnalysis.hasResolvableBackground || (cssValues.length > 0 && cssUnresolved.length === 0),
    unresolved: [...tagAnalysis.unresolved, ...cssUnresolved]
  };
}

function findMobileRootTag(content) {
  const openingTags = getOpeningTagsAfterBody(content, 8).slice(1);
  return openingTags.find(tag => /^<main\b/i.test(tag)) ||
    openingTags.find(tag => /^<(?:div|section|article)\b/i.test(tag)) ||
    '';
}

function validateMobileViewportMode(designDir, projectFacts) {
  console.log('\nChecking mobile viewport mode contracts...');
  const pages = Array.isArray(projectFacts?.pages) ? projectFacts.pages : [];
  const projectDeviceType = projectFacts?.deviceType;
  if (projectDeviceType !== 'mobile') {
    console.log('  [OK] Not a mobile project; mobile viewport mode check skipped');
    return;
  }

  const mobileAppShellPages = pages.filter(page => page && page.viewportMode === 'app-shell' && typeof page.htmlSrc === 'string');
  if (mobileAppShellPages.length > 0) {
    addError(
      'mobile-viewport-mode',
      `mobile project declares ${mobileAppShellPages.length} app-shell page(s). Ordinary mobile visual mockups must use viewportMode="document-scroll" so the canvas shows the full design board. Fix the page plan/orchestration summary and use natural document flow; do not repair by adding h-screen overflow-hidden.`
    );
  } else {
    console.log('  [OK] Mobile pages use document-scroll viewport mode');
  }
}

function validateDesktopAppShellViewport(designDir, projectFacts) {
  console.log('\nChecking desktop/tablet app-shell viewport contracts...');

  const pages = Array.isArray(projectFacts?.pages) ? projectFacts.pages : [];
  const projectDeviceType = projectFacts?.deviceType;
  if (projectDeviceType === 'mobile') {
    console.log('  [OK] Mobile project; desktop/tablet app-shell checks skipped');
    return;
  }

  const appShellPages = pages.filter(page => page && page.viewportMode === 'app-shell' && typeof page.htmlSrc === 'string');
  if (appShellPages.length === 0) {
    console.log('  [OK] No app-shell viewport pages declared');
    return;
  }

  const pagesDir = path.join(designDir, 'pages');
  for (const page of appShellPages) {
    const htmlPath = path.resolve(designDir, page.htmlSrc);
    if (!htmlPath.startsWith(`${pagesDir}${path.sep}`)) {
      addError('app-shell-viewport', `${page.htmlSrc}: htmlSrc must stay under pages/ for app-shell validation`);
      continue;
    }
    if (!fs.existsSync(htmlPath)) {
      addError('app-shell-viewport', `${page.htmlSrc}: HTML file not found for app-shell validation`);
      continue;
    }

    const content = readHtmlFileCached(htmlPath, page.htmlSrc);
    if (content === null) continue;
    const hasAppShellMarker = /data-viewport-mode=["']app-shell["']/i.test(content);
    const scrollRegionTags = content.match(/<[^>]+data-scroll-region=["']primary["'][^>]*>/gi) || [];
    const hasPrimaryScrollRegion = scrollRegionTags.some(tag => classAttrContains(tag, 'overflow-y-auto'));

    if (!hasAppShellMarker) {
      addError(
        'app-shell-viewport',
        `${page.htmlSrc}: viewportMode is app-shell but data-viewport-mode="app-shell" is missing on the shell container.`
      );
    }
    if (!hasPrimaryScrollRegion) {
      addError(
        'app-shell-viewport',
        `${page.htmlSrc}: app-shell pages must declare data-scroll-region="primary" on a class list containing overflow-y-auto.`
      );
    }
    if (content.includes('min-h-screen') && (!hasAppShellMarker || !hasPrimaryScrollRegion)) {
      addError(
        'app-shell-viewport',
        `${page.htmlSrc}: app-shell page still looks like natural document flow (min-h-screen) without a complete internal scroll shell.`
      );
    }
  }
}

function validateMobileDocumentScrollPages(designDir, projectFacts) {
  console.log('\nChecking mobile document-scroll canvas contracts...');

  const projectDeviceType = projectFacts?.deviceType;
  if (projectDeviceType !== 'mobile') {
    console.log('  [OK] Not a mobile project; mobile document-scroll check skipped');
    return;
  }

  const pages = Array.isArray(projectFacts?.pages) ? projectFacts.pages : [];
  const documentScrollPages = pages.filter(
    page => page && page.viewportMode !== 'app-shell' && typeof page.htmlSrc === 'string'
  );
  if (documentScrollPages.length === 0) {
    console.log('  [OK] No mobile document-scroll pages declared');
    return;
  }

  for (const page of documentScrollPages) {
    const content = readPageHtml(designDir, page);
    if (!content) continue;
    const bodyTag = (content.match(/<body\b[^>]*>/i) || [''])[0];
    if (/\bh-screen\b/i.test(bodyTag) && /\boverflow-hidden\b/i.test(bodyTag)) {
      addError(
        'mobile-document-scroll',
        `${page.htmlSrc}: mobile document-scroll mockups must not lock <body> to h-screen overflow-hidden; use natural document flow so the canvas can show the full design board.`
      );
    }
  }
}

function validateMobileFixedViewportArtifacts(designDir, projectFacts) {
  console.log('\nChecking mobile fixed viewport artifacts...');

  const projectDeviceType = projectFacts?.deviceType;
  if (projectDeviceType !== 'mobile') {
    console.log('  [OK] Not a mobile project; mobile fixed viewport check skipped');
    return;
  }

  const pages = Array.isArray(projectFacts?.pages) ? projectFacts.pages : [];
  if (pages.length === 0) {
    console.log('  [OK] No mobile page records found for fixed viewport check');
    return;
  }

  for (const page of pages) {
    const content = readPageHtml(designDir, page);
    if (!content) continue;

    if (/data-viewport-mode=["']app-shell["']/i.test(content)) {
      addError(
        'mobile-viewport-mode',
        `${page.htmlSrc}: mobile mockups must not include data-viewport-mode="app-shell"; use document-scroll natural flow and let prototype preview provide the device frame.`
      );
    }

    const openingTags = getOpeningTagsAfterBody(content, 8).slice(1);
    if (openingTags.some(tag => tagHasLockedViewportClasses(tag))) {
      addError(
        'mobile-fixed-viewport',
        `${page.htmlSrc}: mobile mockups must not lock a root wrapper to h-screen overflow-hidden; keep the canvas board vertically expandable.`
      );
    }

    if (hasFixedMobileViewportHeight(content) && hasOverflowHidden(content)) {
      addError(
        'mobile-fixed-viewport',
        `${page.htmlSrc}: mobile mockups must not combine fixed 812/844px viewport height with overflow hidden; use natural document flow.`
      );
    }
  }
}

function findBottomOverlayEvidence(content) {
  const patterns = [
    /\bclass=["'][^"']*\b(?:fixed|absolute)\b[^"']*\bbottom(?:-|\[|:|=)[^"']*["']/gi,
    /\bstyle=["'][^"']*position\s*:\s*(?:fixed|absolute)[^"']*bottom\s*:/gi
  ];
  const semanticPattern = /(?:cta|button|tab|nav|bottom|data-dom-id=["'](?:cta-|nav-))/i;

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      const start = Math.max(0, match.index - 300);
      const end = Math.min(content.length, match.index + match[0].length + 300);
      const snippet = content.slice(start, end);
      if (semanticPattern.test(snippet)) {
        return match[0].slice(0, 160);
      }
    }
  }

  return null;
}

function validateMobileBottomOverlayRisk(designDir, projectFacts) {
  console.log('\nChecking mobile bottom overlay risks...');

  const projectDeviceType = projectFacts?.deviceType;
  if (projectDeviceType !== 'mobile') {
    console.log('  [OK] Not a mobile project; mobile bottom overlay check skipped');
    return;
  }

  const pages = Array.isArray(projectFacts?.pages) ? projectFacts.pages : [];
  if (pages.length === 0) {
    console.log('  [OK] No mobile page records found for bottom overlay check');
    return;
  }

  for (const page of pages) {
    const content = readPageHtml(designDir, page);
    if (!content) continue;

    const evidence = findBottomOverlayEvidence(content);
    if (!evidence) continue;

    if (hasLockedMobileViewport(content)) {
      addError(
        'mobile-bottom-overlay',
        `${page.htmlSrc}: bottom fixed/absolute CTA or navigation is combined with a locked mobile viewport, which can crop or cover content. Use document-scroll natural flow and in-flow/safe-area spacing instead. Evidence: ${evidence}`
      );
    } else {
      addWarning(
        'mobile-bottom-overlay',
        `${page.htmlSrc}: bottom fixed/absolute CTA or navigation found. Ensure it has safe-area spacing and does not cover content. Evidence: ${evidence}`
      );
    }
  }
}

function splitClassList(value) {
  return String(value || '').split(/\s+/).filter(Boolean);
}

function classListHasAll(value, required) {
  const classes = new Set(splitClassList(value));
  return required.every(name => classes.has(name));
}

function normalizeNavItemTag(tag) {
  const match = String(tag || '').match(/^<([a-zA-Z][\w:-]*)\b/);
  return match ? match[1].toLowerCase() : 'unknown';
}

function findOpeningTagAt(content, attrIndex) {
  const itemStart = content.lastIndexOf('<', attrIndex);
  const itemEnd = content.indexOf('>', attrIndex);
  if (itemStart < 0 || itemEnd < attrIndex) return '';
  return content.slice(itemStart, itemEnd + 1);
}

function collectDataNavKeyMatches(content) {
  const matches = [];
  const navRegex = /\bdata-nav-key=["']([^"']+)["']/gi;
  let match;
  while ((match = navRegex.exec(content)) !== null) {
    const key = match[1].trim();
    if (!key) continue;
    if (!matches.some(item => item.key === key)) {
      matches.push({ key, index: match.index, itemTag: findOpeningTagAt(content, match.index) });
    }
  }
  return matches;
}

function collectLegacyNavIdMatches(content) {
  const matches = [];
  const navRegex = /\b(?:data-dom-id|id)=["'](nav-[^"']+)["']/gi;
  let match;
  while ((match = navRegex.exec(content)) !== null) {
    const key = match[1].replace(/^nav-/, '').trim();
    if (!key) continue;
    if (!matches.some(item => item.key === key)) {
      matches.push({ key, index: match.index });
    }
  }
  return matches;
}

function extractNavigationBlocks(content) {
  const blocks = [];
  const navBlockRegex = /<nav\b[^>]*>[\s\S]*?<\/nav>/gi;
  let match;
  while ((match = navBlockRegex.exec(content)) !== null) {
    const html = match[0];
    const openTag = (html.match(/^<nav\b[^>]*>/i) || [''])[0];
    blocks.push({ html, index: match.index, openTag });
  }
  return blocks;
}

function findNearestMobileNavTag(content, firstIndex) {
  const before = content.slice(Math.max(0, firstIndex - 900), firstIndex);
  const tags = before.match(/<[^>]+>/g) || [];
  return [...tags].reverse().find(tag =>
    /<nav\b/i.test(tag) || /\b(?:bottom|tab|fixed|absolute|sticky)\b/i.test(tag)
  ) || '';
}

function findFirstChildDivTag(blockHtml) {
  const navOpenEnd = blockHtml.search(/>/);
  const afterNavOpen = navOpenEnd >= 0 ? blockHtml.slice(navOpenEnd + 1) : blockHtml;
  return (afterNavOpen.match(/<div\b[^>]*>/i) || [''])[0];
}

function parseHeightPxFromTag(tag) {
  if (!tag) return null;
  const inlineHeight = tag.match(/\bheight\s*:\s*(\d+)px\b/i);
  if (inlineHeight) return Number(inlineHeight[1]);
  const arbitraryHeight = tag.match(/\bh-\[(\d+)px\]/i);
  if (arbitraryHeight) return Number(arbitraryHeight[1]);
  const spacingHeight = tag.match(/\bh-(\d+)\b/i);
  if (spacingHeight) return Number(spacingHeight[1]) * 4;
  return null;
}

function extractNavItemHtml(blockHtml, item) {
  const tagName = normalizeNavItemTag(item.itemTag);
  if (!tagName || tagName === 'unknown') return '';
  const key = escapeRegExp(item.key);
  const patterns = [
    new RegExp(`<${tagName}\\b[^>]*\\bdata-nav-key=["']${key}["'][^>]*>[\\s\\S]*?<\\/${tagName}>`, 'i'),
    new RegExp(`<${tagName}\\b[^>]*\\b(?:data-dom-id|id)=["']nav-${key}["'][^>]*>[\\s\\S]*?<\\/${tagName}>`, 'i')
  ];
  for (const pattern of patterns) {
    const match = blockHtml.match(pattern);
    if (match) return match[0];
  }
  return item.itemTag || '';
}

function visibleTextFromHtml(html) {
  return String(html || '')
    .replace(/<script\b[\s\S]*?<\/script>/gi, '')
    .replace(/<style\b[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/gi, ' ')
    .trim();
}

function collectNavItemLabelTags(itemHtml) {
  return [...String(itemHtml || '').matchAll(/<span\b[^>]*>[\s\S]*?<\/span>/gi)]
    .map(match => match[0])
    .filter(tag => {
      if (/<svg\b/i.test(tag) || /\bdata-lucide=/i.test(tag)) return false;
      return visibleTextFromHtml(tag).length > 0;
    });
}

function collectNavItemIconClass(itemHtml) {
  const html = String(itemHtml || '');
  const iconTags = [
    ...html.matchAll(/<i\b[^>]*data-lucide=["'][^"']+["'][^>]*>/gi),
    ...html.matchAll(/<svg\b[^>]*>/gi)
  ].map(match => match[0]);
  if (iconTags.length === 0) return '';

  const wrapperClasses = [];
  for (const wrapperMatch of html.matchAll(/<(?:span|div)\b[^>]*>[\s\S]*?(?:<i\b[^>]*data-lucide=["'][^"']+["'][^>]*>|<svg\b[^>]*>)/gi)) {
    const wrapperOpen = (wrapperMatch[0].match(/^<(?:span|div)\b[^>]*>/i) || [''])[0];
    const cls = getTagAttr(wrapperOpen, 'class');
    if (splitClassList(cls).some(c => /^(?:w-|h-|size-|shrink-)/.test(c))) {
      wrapperClasses.push(cls);
    }
  }

  return [
    ...iconTags.map(tag => getTagAttr(tag, 'class')),
    ...wrapperClasses
  ].filter(Boolean).join(' ');
}

function mobileNavRepairText() {
  return 'Repair: rebuild the Page Packet with Mobile Navigation Contract and copy canonicalNavHtml. If this is post-validation repair, run repair-mobile-navigation-flow.mjs once; do not patch individual span/data-dom-id/class fragments.';
}

function addMobileNavError(page, message) {
  addRepairPlanHint('mobile-navigation-consistency', {
    owner: 'main-agent',
    repairScope: 'all-pages-with-mobile-nav',
    strategy: 'run_repair_mobile_navigation_once',
    affectedFiles: page?.htmlSrc ? [page.htmlSrc] : [],
    repairReportPath: 'mobile-nav-repair-report.json',
    allowSourceRead: 'no-full-html-read'
  });
  addError('mobile-navigation-consistency', `${message} ${mobileNavRepairText()}`);
}

function analyzeMobileNavStructure(blockHtml, openTag, matches) {
  const navClass = getTagAttr(openTag, 'class');
  const navStyle = getTagAttr(openTag, 'style');
  const innerTag = findFirstChildDivTag(blockHtml);
  const innerClass = getTagAttr(innerTag, 'class');
  const innerStyle = getTagAttr(innerTag, 'style');
  const itemTags = matches.map(item => item.itemTag).filter(Boolean);
  const itemTagNames = [...new Set(itemTags.map(normalizeNavItemTag))];
  const itemClasses = itemTags.map(tag => getTagAttr(tag, 'class'));
  const itemHtmlList = matches.map(item => extractNavItemHtml(blockHtml, item));
  const labelTagsByItem = itemHtmlList.map(collectNavItemLabelTags);
  const labelTags = labelTagsByItem.flat();
  const iconClasses = itemHtmlList.map(collectNavItemIconClass).filter(Boolean);

  const labelNowrap = labelTagsByItem.length >= matches.length &&
    labelTagsByItem.every(tags =>
      tags.length > 0 &&
      tags.some(tag => classAttrContains(tag, 'whitespace-nowrap') || classAttrContains(tag, 'truncate'))
    );
  const itemClassSignature = [...new Set(itemClasses
    .map(value => splitClassList(value)
      .filter(cls => !/^text(?:-|$)/.test(cls) && !/^font(?:-|$)/.test(cls) && !/^style-/.test(cls))
      .sort()
      .join('.')))]
    .join('|');
  const iconSignature = [...new Set(iconClasses
    .map(cls => {
      const sizingClasses = splitClassList(cls)
        .filter(c => /^(?:w-|h-|size-|shrink-)/.test(c))
        .sort()
        .join('.');
      return `icon:${sizingClasses || 'missing'}`;
    }))]
    .join('|');
  const gridClass = (innerClass.match(/\bgrid-cols-(?:\d+|\[[^\]]+\])\b/) || openTag.match(/\bgrid-cols-(?:\d+|\[[^\]]+\])\b/) || [''])[0];
  const hasScrollRow = classListHasAll(innerClass, ['grid-flow-col', 'overflow-x-auto']) ||
    classListHasAll(navClass, ['grid-flow-col', 'overflow-x-auto']);

  return {
    navClass,
    navStyle,
    innerClass,
    innerStyle,
    itemTagNames,
    itemClasses,
    itemClassSignature,
    iconClasses,
    iconSignature,
    labelNowrap,
    labelCount: labelTags.length,
    iconCount: iconClasses.length,
    innerHeightPx: parseHeightPxFromTag(innerTag),
    gridClass,
    hasGrid: classAttrContains(innerTag, 'grid') || classAttrContains(openTag, 'grid'),
    hasScrollRow,
    hasMaxWidth: classAttrContains(innerTag, 'max-w-md') || classAttrContains(openTag, 'max-w-md'),
    hasFullWidth: classAttrContains(innerTag, 'w-full') || classAttrContains(openTag, 'w-full'),
    hasFullHeight: classAttrContains(innerTag, 'h-full') || classAttrContains(openTag, 'h-full')
  };
}

function buildMobileNavCluster(matches, navTag, source, blockHtml = '') {
  if (matches.length < 3) return null;

  let position = 'flow';
  if (/\bfixed\b/i.test(navTag) || /position\s*:\s*fixed/i.test(navTag)) {
    position = 'fixed';
  } else if (/\babsolute\b/i.test(navTag) || /position\s*:\s*absolute/i.test(navTag)) {
    position = 'absolute';
  } else if (/\bsticky\b/i.test(navTag) || /position\s*:\s*sticky/i.test(navTag)) {
    position = 'sticky';
  }

  const keys = matches.map(item => item.key);
  const structure = analyzeMobileNavStructure(blockHtml, navTag, matches);
  const heightPx = parseHeightPxFromTag(navTag) ?? structure.innerHeightPx;

  return {
    keys,
    position,
    heightPx,
    source,
    structure,
    signature: [
      keys.join('|'),
      position,
      heightPx ?? 'auto',
      `tag=${structure.itemTagNames.join(',')}`,
      `item=${structure.itemClassSignature}`,
      `icon=${structure.iconSignature}`,
      `nowrap=${structure.labelNowrap}`,
      `grid=${structure.gridClass || (structure.hasScrollRow ? 'scroll-row' : 'none')}`,
      `max=${structure.hasMaxWidth}`,
      `full=${structure.hasFullWidth}/${structure.hasFullHeight}`
    ].join('::')
  };
}

function extractMobileNavCluster(content) {
  const navigationBlocks = extractNavigationBlocks(content);

  for (const block of navigationBlocks) {
    const stableMatches = collectDataNavKeyMatches(block.html)
      .map(item => ({ ...item, index: item.index + block.index }));
    const cluster = buildMobileNavCluster(stableMatches, block.openTag, 'data-nav-key', block.html);
    if (cluster) return cluster;
  }

  const stableMatches = collectDataNavKeyMatches(content);
  if (stableMatches.length >= 3) {
    const navTag = findNearestMobileNavTag(content, stableMatches[0].index);
    return buildMobileNavCluster(stableMatches, navTag, 'data-nav-key', content);
  }

  for (const block of navigationBlocks) {
    const legacyMatches = collectLegacyNavIdMatches(block.html)
      .map(item => ({ ...item, index: item.index + block.index }));
    const cluster = buildMobileNavCluster(legacyMatches, block.openTag, 'legacy-nav-id', block.html);
    if (cluster) return cluster;
  }

  const legacyMatches = collectLegacyNavIdMatches(content);
  if (legacyMatches.length >= 3) {
    const navTag = findNearestMobileNavTag(content, legacyMatches[0].index);
    return buildMobileNavCluster(legacyMatches, navTag, 'legacy-nav-id', content);
  }

  return null;
}

function expectedMobileNavKeys(projectFacts) {
  const items = Array.isArray(projectFacts?.mobileNavigation?.items)
    ? projectFacts.mobileNavigation.items
    : [];
  return items
    .map(item => typeof item?.key === 'string' ? item.key.trim() : '')
    .filter(Boolean);
}

function expectedGridClass(projectFacts) {
  const itemCount = expectedMobileNavKeys(projectFacts).length;
  return itemCount >= 3 && itemCount <= 5 ? `grid-cols-${itemCount}` : '';
}

function parseExpectedHeight(projectFacts) {
  const rawHeight = projectFacts?.mobileNavigation?.heightPx;
  const numeric = Number(rawHeight);
  return Number.isFinite(numeric) && numeric > 0 ? numeric : null;
}

function expectedMobileNavStructure(projectFacts) {
  const structure = projectFacts?.mobileNavigation?.structure;
  return structure && typeof structure === 'object' ? structure : null;
}

function geometryClassesFromContract(classValue) {
  return splitClassList(classValue)
    .filter(cls =>
      /^(?:fixed|sticky|relative|absolute|bottom-|top-|left-|right-|z-|w-|h-|min-w-|max-w-|grid|grid-cols-|grid-flow-|auto-cols-|overflow-x-|no-scrollbar|flex|flex-col|items-|justify-|gap-|px-|py-|shrink-|truncate|whitespace-nowrap)/.test(cls)
    );
}

function validateMobileNavStructureContract(page, cluster, projectFacts) {
  const structure = cluster.structure;
  if (!structure) return;

  if (structure.labelCount > 0 && !structure.labelNowrap) {
    addMobileNavError(
      page,
      `${page.htmlSrc}: mobile nav labels must include whitespace-nowrap/truncate so Chinese tab labels do not wrap.`
    );
  }

  if (structure.itemTagNames.length !== 1) {
    addMobileNavError(
      page,
      `${page.htmlSrc}: mobile nav must use one item tag consistently; found ${structure.itemTagNames.join(', ')}.`
    );
  }

  if (structure.iconCount > 0 && structure.iconCount < cluster.keys.length) {
    addMobileNavError(
      page,
      `${page.htmlSrc}: mobile nav exposes ${cluster.keys.length} items but only ${structure.iconCount} icon(s); icon visibility/structure must be consistent.`
    );
  }

  const expectedHeight = parseExpectedHeight(projectFacts);
  if (expectedHeight !== null && cluster.heightPx !== expectedHeight) {
    addMobileNavError(
      page,
      `${page.htmlSrc}: mobile nav height ${cluster.heightPx === null ? 'missing' : `${cluster.heightPx}px`} does not match mobileNavigation.heightPx ${expectedHeight}px.`
    );
  }

  const expectedGrid = expectedGridClass(projectFacts);
  if (expectedGrid && !structure.hasScrollRow && structure.gridClass !== expectedGrid) {
    addMobileNavError(
      page,
      `${page.htmlSrc}: mobile nav grid class ${structure.gridClass || 'missing'} does not match item count (${expectedGrid}).`
    );
  }

  const contract = expectedMobileNavStructure(projectFacts);
  if (!contract) return;

  const requiredNavGeometry = geometryClassesFromContract(contract.navClass);
  if (requiredNavGeometry.length > 0 && !classListHasAll(structure.navClass, requiredNavGeometry)) {
    const missing = requiredNavGeometry.filter(cls => !splitClassList(structure.navClass).includes(cls));
    addMobileNavError(
      page,
      `${page.htmlSrc}: mobile nav root is missing contract geometry class(es): ${missing.join(', ')}.`
    );
  }

  if (typeof contract.itemTag === 'string' && contract.itemTag && !structure.itemTagNames.includes(contract.itemTag)) {
    addMobileNavError(
      page,
      `${page.htmlSrc}: mobile nav item tag must follow mobileNavigation.structure.itemTag="${contract.itemTag}", found ${structure.itemTagNames.join(', ')}.`
    );
  }

  const requiredInnerGeometry = geometryClassesFromContract(contract.innerClass);
  if (requiredInnerGeometry.length > 0 && !classListHasAll(structure.innerClass, requiredInnerGeometry)) {
    const missing = requiredInnerGeometry.filter(cls => !splitClassList(structure.innerClass).includes(cls));
    addMobileNavError(
      page,
      `${page.htmlSrc}: mobile nav inner wrapper is missing contract geometry class(es): ${missing.join(', ')}.`
    );
  }

  const requiredItemGeometry = geometryClassesFromContract(contract.itemClass);
  if (requiredItemGeometry.length > 0) {
    for (const itemClass of structure.itemClasses) {
      const itemClassList = splitClassList(itemClass);
      const missing = requiredItemGeometry.filter(cls => !itemClassList.includes(cls));
      if (missing.length > 0) {
        addMobileNavError(
          page,
          `${page.htmlSrc}: mobile nav item is missing contract geometry class(es): ${missing.join(', ')}.`
        );
        break;
      }
    }
  }

  if (typeof contract.labelClass === 'string' && contract.labelClass.includes('whitespace-nowrap')) {
    if (structure.labelCount < cluster.keys.length) {
      addMobileNavError(
        page,
        `${page.htmlSrc}: mobile nav labelClass contract requires one label span per nav item.`
      );
    } else if (!structure.labelNowrap) {
      addMobileNavError(
        page,
        `${page.htmlSrc}: mobile nav labelClass contract requires whitespace-nowrap/truncate.`
      );
    }
  }

  const requiredIconGeometry = geometryClassesFromContract(contract.iconClass);
  if (requiredIconGeometry.length > 0 && structure.iconClasses.length > 0) {
    for (const iconClass of structure.iconClasses) {
      const missing = requiredIconGeometry.filter(cls => !splitClassList(iconClass).includes(cls));
      if (missing.length > 0) {
        addMobileNavError(
          page,
          `${page.htmlSrc}: mobile nav icon is missing contract geometry class(es): ${missing.join(', ')}.`
        );
        break;
      }
    }
  }
}

function validateMobileNavigationConsistency(designDir, projectFacts) {
  console.log('\nChecking mobile navigation consistency...');

  const projectDeviceType = projectFacts?.deviceType;
  if (projectDeviceType !== 'mobile') {
    console.log('  [OK] Not a mobile project; mobile navigation consistency check skipped');
    return;
  }

  const pages = Array.isArray(projectFacts?.pages) ? projectFacts.pages : [];
  const clusters = [];
  const pagesWithoutClusters = [];
  const expectedKeys = expectedMobileNavKeys(projectFacts);
  const expectedSignature = expectedKeys.length >= 3 ? expectedKeys.join('|') : null;

  for (const page of pages) {
    const content = readPageHtml(designDir, page);
    if (!content) continue;
    const cluster = extractMobileNavCluster(content);
    if (cluster) {
      clusters.push({ page, cluster });
      if (cluster.source !== 'data-nav-key') {
        addMobileNavError(
          page,
          `${page.htmlSrc}: mobile nav cluster is only detectable from data-dom-id/id. Add stable data-nav-key="<key>" to every tab item; data-dom-id is only for click wiring and must not define active-state structure.`
        );
      }
      if (expectedSignature && cluster.source === 'data-nav-key' && cluster.keys.join('|') !== expectedSignature) {
        addMobileNavError(
          page,
          `${page.htmlSrc}: data-nav-key order (${cluster.keys.join('|')}) does not match sharedProjectShellContract.mobileNavigation.items (${expectedSignature}).`
        );
      }
      if (cluster.source === 'data-nav-key') {
        validateMobileNavStructureContract(page, cluster, projectFacts);
      }
    } else {
      pagesWithoutClusters.push(page);
    }
  }

  if (clusters.length < 2) {
    if (expectedSignature && pagesWithoutClusters.length > 0 && pages.length > 1) {
      addWarning(
        'mobile-navigation-consistency',
        `sharedProjectShellContract.mobileNavigation declares ${expectedSignature}, but only ${clusters.length} page(s) expose a 3+ item data-nav-key nav cluster. Detail/reward/modal pages may omit it only when planned explicitly.`
      );
    }
    console.log('  [OK] Fewer than two mobile nav clusters found');
    return;
  }

  const canonical = clusters[0];
  const mismatches = clusters.filter(item => item.cluster.signature !== canonical.cluster.signature);
  if (mismatches.length > 0) {
    const details = [
      `${canonical.page.htmlSrc}: ${canonical.cluster.signature}`,
      ...mismatches.map(item => `${item.page.htmlSrc}: ${item.cluster.signature}`)
    ].join('; ');
    addMobileNavError(
      canonical.page,
      `mobile pages with global nav must keep the same data-nav-key item order, positioning, height, and structural geometry. ${details}. Use data-dom-id only for click wiring.`
    );
  } else {
    console.log('  [OK] Mobile navigation clusters are consistent');
  }

  if (pagesWithoutClusters.length > 0) {
    addWarning(
      'mobile-navigation-consistency',
      `${pagesWithoutClusters.length} mobile page(s) do not expose a 3+ item data-nav-key nav cluster while sibling pages do. This is acceptable for detail/reward/modal pages only when planned explicitly.`
    );
  }
}

function validateMobileNavigationDispatchEvidence(projectFacts, summary) {
  console.log('\nChecking mobile navigation dispatch evidence...');

  if (!hasMobileNavigationDispatchGate(summary)) {
    console.log('  [OK] Mobile navigation dispatch evidence gate skipped for legacy summary');
    return;
  }

  if (projectFacts?.deviceType !== 'mobile') {
    console.log('  [OK] Not a mobile project; mobile navigation dispatch evidence skipped');
    return;
  }

  const mobileNavigation = projectFacts?.mobileNavigation;
  if (!mobileNavigation || mobileNavigation.applies === false) {
    console.log('  [OK] No global mobile navigation contract declared');
    return;
  }

  const pages = Array.isArray(projectFacts?.pages) ? projectFacts.pages : [];
  const manifest = Array.isArray(summary?.project?.dispatchPreflightManifest)
    ? summary.project.dispatchPreflightManifest
    : [];

  for (const page of pages) {
    if (page.mobileNavigationApplies === false) {
      if (!page.mobileNavigationOmitReason) {
        addError(
          'mobile-navigation-dispatch',
          `${page.htmlSrc}: mobileNavigationApplies=false requires mobileNavigationOmitReason.`
        );
      }
      continue;
    }

    const pageEntry = manifest.find(entry =>
      entry?.htmlSrc === page.htmlSrc || entry?.nodeId === page.nodeId
    );
    const navEvidence = pageEntry?.mobileNavigation;
    if (!navEvidence?.canonicalHtmlIncluded) {
      addRepairPlanHint('mobile-navigation-dispatch', {
        owner: 'main-agent',
        repairScope: 'page-dispatch-packet',
        strategy: 'rebuild_page_packet_with_mobile_navigation_contract',
        affectedFiles: page?.htmlSrc ? [page.htmlSrc] : [],
        allowSourceRead: 'no-html-read'
      });
      addError(
        'mobile-navigation-dispatch',
        `${page.htmlSrc}: mobileNavigation applies but dispatchPreflightManifest does not prove canonicalNavHtml was included. Rebuild the Page Packet with Mobile Navigation Contract; do not dispatch generic page tasks.`
      );
      continue;
    }

    if (navEvidence.required === true && navEvidence.appliesToThisPage !== true) {
      addError(
        'mobile-navigation-dispatch',
        `${page.htmlSrc}: mobileNavigation evidence is required but appliesToThisPage is not true.`
      );
    }
    if (navEvidence.missingFields && Array.isArray(navEvidence.missingFields) && navEvidence.missingFields.length > 0) {
      addError(
        'mobile-navigation-dispatch',
        `${page.htmlSrc}: mobileNavigation dispatch evidence has missing fields: ${navEvidence.missingFields.join(', ')}.`
      );
    }
  }
}

function normalizeDispatchPath(value) {
  const raw = String(value || '').trim().replace(/\\/g, '/').replace(/^(?:\.\/)+/, '');
  if (!raw || path.posix.isAbsolute(raw) || /^[a-zA-Z]:\//.test(raw)) return null;
  if (raw.split('/').includes('..')) return null;
  const normalized = path.posix.normalize(raw);
  return normalized === '.' ? null : normalized;
}

function pathIsForbiddenForSubAgent(relPath) {
  const normalized = normalizeDispatchPath(relPath);
  if (!normalized) return false;
  if (normalized.endsWith('.design')) return true;
  if (normalized === 'runtime-orchestration-summary.json') return true;
  if (normalized === 'validation-report.json') return true;
  if (normalized === 'finish-readiness-report.json') return true;
  if (normalized === 'restore-contract-report.json') return true;
  if (normalized === 'page-generation-summary.json') return true;
  if (/^\.design(?:\/|$)/.test(normalized)) return true;
  if (/(^|\/)(?:todo|TODO)(?:[-_.][^/]*)?\.(?:md|json|txt)$/i.test(normalized)) return true;
  return false;
}

function pathIsValidatorOwnedForDispatchHash(relPath) {
  const normalized = normalizeDispatchPath(relPath);
  return [
    'validation-report.json',
    'finish-readiness-report.json',
    'restore-contract-report.json',
    'page-generation-summary.json',
    'validation-run-ledger.json',
  ].includes(normalized);
}

function pathIsAllowedForDispatch(relPath, allowed) {
  const normalized = normalizeDispatchPath(relPath);
  if (allowed.has(normalized)) return true;
  for (const allowedPath of allowed) {
    if (allowedPath.endsWith('/') && normalized.startsWith(allowedPath)) return true;
  }
  return false;
}

function fileHashIfPresent(designDir, relPath) {
  const normalized = normalizeDispatchPath(relPath);
  if (!normalized) return null;
  const full = path.resolve(designDir, normalized);
  if (!full.startsWith(`${path.resolve(designDir)}${path.sep}`)) return null;
  if (!fs.existsSync(full) || !fs.statSync(full).isFile()) return null;
  return sha256File(full);
}

function mutationIsMainAgentRecorded(summary, relPath) {
  const normalized = normalizeDispatchPath(relPath);
  const mutations = Array.isArray(summary?.project?.mainAgentPostDispatchMutations)
    ? summary.project.mainAgentPostDispatchMutations
    : [];
  return mutations.some(item => {
    if (!item || typeof item !== 'object') return false;
    const paths = [
      item.path,
      item.file,
      item.relPath,
      ...(Array.isArray(item.paths) ? item.paths : []),
      ...(Array.isArray(item.files) ? item.files : []),
    ].map(normalizeDispatchPath).filter(Boolean);
    return paths.includes(normalized) && String(item.owner || 'main-agent') === 'main-agent';
  });
}

function validateDispatchChangedFilesDiscipline(designDir, summary) {
  console.log('\nChecking dispatch changedFiles discipline...');

  const manifest = Array.isArray(summary?.project?.dispatchPreflightManifest)
    ? summary.project.dispatchPreflightManifest
    : [];
  if (manifest.length === 0) {
    console.log('  [OK] No dispatchPreflightManifest; changedFiles discipline skipped');
    return;
  }

  const expectedDispatches = Array.isArray(summary?.project?.expectedDispatches)
    ? summary.project.expectedDispatches
    : [];
  if (expectedDispatches.length === 0) {
    addError('dispatch-changed-files', 'project.expectedDispatches[] is required when dispatchPreflightManifest[] exists');
    return;
  }

  const objectRows = expectedDispatches.filter(item => item && typeof item === 'object' && !Array.isArray(item));
  if (objectRows.length !== expectedDispatches.length) {
    addError('dispatch-changed-files', 'project.expectedDispatches[] must contain completion objects with status and changedFiles[], not bare page ids');
  }

  for (const entry of manifest) {
    const label = entry?.htmlSrc || entry?.nodeId || '<unknown dispatch>';
    const rawAllowed = Array.isArray(entry?.allowedWritePaths) ? entry.allowedWritePaths : [];
    const allowed = new Set(rawAllowed
      .map(normalizeDispatchPath)
      .filter(Boolean));
    if (allowed.size !== rawAllowed.length) {
      addError('dispatch-changed-files', `${label}: dispatchPreflightManifest.allowedWritePaths[] contains an invalid or traversing path`);
    }
    if (allowed.size === 0) {
      addError('dispatch-changed-files', `${label}: dispatchPreflightManifest.allowedWritePaths[] is required`);
    }

    const completion = objectRows.find(item =>
      item.nodeId === entry?.nodeId ||
      item.pageId === entry?.nodeId ||
      item.targetPageId === entry?.nodeId ||
      item.htmlSrc === entry?.htmlSrc
    );
    if (!completion) {
      addError('dispatch-changed-files', `${label}: matching project.expectedDispatches[] completion row is required`);
      continue;
    }
    if (completion.status !== 'completed' && completion.status !== 'not_required') {
      addError('dispatch-changed-files', `${label}: expectedDispatches.status must be completed or not_required`);
    }
    if (completion.status === 'not_required') continue;

    const rawChangedFiles = Array.isArray(completion.changedFiles) ? completion.changedFiles : [];
    const changedFiles = rawChangedFiles.map(normalizeDispatchPath).filter(Boolean);
    if (changedFiles.length !== rawChangedFiles.length) {
      addError('dispatch-changed-files', `${label}: changedFiles[] contains an invalid or traversing path`);
    }
    if (changedFiles.length === 0) {
      addError('dispatch-changed-files', `${label}: completed dispatch requires changedFiles[]`);
    }
    for (const relPath of changedFiles) {
      if (!pathIsAllowedForDispatch(relPath, allowed)) {
        addError('dispatch-changed-files', `${label}: changed file outside allowedWritePaths[]: ${relPath}`);
      }
      if (pathIsForbiddenForSubAgent(relPath)) {
        addError('dispatch-changed-files', `${label}: Sub-Agent changed forbidden file: ${relPath}`);
      }
    }

    const discipline = completion.toolDisciplineEvidence || completion.completion?.toolDisciplineEvidence || {};
    if (discipline.todoWriteUsed === true) {
      addError('dispatch-changed-files', `${label}: toolDisciplineEvidence.todoWriteUsed must be false`);
    }
    if (discipline.validationScriptsRunBySubAgent === true) {
      addError('dispatch-changed-files', `${label}: toolDisciplineEvidence.validationScriptsRunBySubAgent must be false`);
    }
    if (discipline.previewStarted === true) {
      addError('dispatch-changed-files', `${label}: toolDisciplineEvidence.previewStarted must be false`);
    }
    if (discipline.helperScriptsCreated === true) {
      addError('dispatch-changed-files', `${label}: toolDisciplineEvidence.helperScriptsCreated must be false`);
    }
    const toolCallLedger = completion.toolCallLedger || completion.completion?.toolCallLedger || null;
    if (!toolCallLedger || typeof toolCallLedger !== 'object' || Array.isArray(toolCallLedger)) {
      addError('dispatch-changed-files', `${label}: completed dispatch requires toolCallLedger for strict ownership audit`);
    } else {
        const ledgerSource = String(toolCallLedger.source || '').trim();
        const traceDigest = String(toolCallLedger.traceDigest || '').trim();
        if (ledgerSource !== 'main-agent-runtime-trace') {
          addError('dispatch-changed-files', `${label}: toolCallLedger.source must be main-agent-runtime-trace; found ${ledgerSource || '(missing)'}`);
        }
        if (!traceDigest) {
          addError('dispatch-changed-files', `${label}: toolCallLedger.traceDigest is required for trace-sourced discipline audit`);
        }
      const todoWriteCalls = Number(toolCallLedger.todoWriteCalls || 0);
      const previewCalls = Number(toolCallLedger.previewCalls || 0);
      const validationScriptCalls = Number(toolCallLedger.validationScriptCalls || 0);
      const helperScriptWrites = Number(toolCallLedger.helperScriptWrites || 0);
      if (todoWriteCalls > 0) {
        addError('dispatch-changed-files', `${label}: toolCallLedger.todoWriteCalls must be 0; found ${todoWriteCalls}`);
      }
      if (previewCalls > 0) {
        addError('dispatch-changed-files', `${label}: toolCallLedger.previewCalls must be 0 for Page Sub-Agents; found ${previewCalls}`);
      }
      if (validationScriptCalls > 0) {
        addError('dispatch-changed-files', `${label}: toolCallLedger.validationScriptCalls must be 0; found ${validationScriptCalls}`);
      }
      if (helperScriptWrites > 0) {
        addError('dispatch-changed-files', `${label}: toolCallLedger.helperScriptWrites must be 0; found ${helperScriptWrites}`);
      }
    }
    if (changedFiles.some(relPath => /(^|\/)(?:todo|TODO)(?:[-_.][^/]*)?\.(?:md|json|txt)$/i.test(relPath)) && discipline.todoWriteUsed === false) {
      addError('dispatch-changed-files', `${label}: todoWriteUsed=false conflicts with changedFiles containing todo files`);
    }

    const preDispatchHashes = entry?.preDispatchFileHashes && typeof entry.preDispatchFileHashes === 'object'
      ? entry.preDispatchFileHashes
      : null;
    if (preDispatchHashes) {
      for (const [relPath, expectedHash] of Object.entries(preDispatchHashes)) {
        const normalized = normalizeDispatchPath(relPath);
        if (pathIsValidatorOwnedForDispatchHash(normalized)) continue;
        const currentHash = fileHashIfPresent(designDir, normalized);
        if (!currentHash || currentHash === expectedHash) continue;
        if (!mutationIsMainAgentRecorded(summary, normalized)) {
          addError('dispatch-changed-files', `${label}: controlled file changed after dispatch preflight without mainAgentPostDispatchMutations evidence: ${normalized}`);
        }
      }
    }
  }
}

function validateMobileBackgroundCoverage(designDir, projectFacts) {
  console.log('\nChecking mobile background coverage...');

  const projectDeviceType = projectFacts?.deviceType;
  if (projectDeviceType !== 'mobile') {
    console.log('  [OK] Not a mobile project; mobile background check skipped');
    return;
  }

  const pages = Array.isArray(projectFacts?.pages) ? projectFacts.pages : [];
  for (const page of pages) {
    const content = readPageHtml(designDir, page);
    if (!content) continue;

    const declaredVars = collectCssCustomProperties(content);
    const bodyTag = (content.match(/<body\b[^>]*>/i) || [''])[0];
    const bodyBackground = analyzeBodyBackground(content, bodyTag, declaredVars);

    if (bodyBackground.unresolved.length > 0) {
      addError(
        'mobile-background-coverage',
        `${page.htmlSrc}: body background references undefined CSS variable(s): ${formatCssVarRefs(bodyBackground.unresolved)}. Use a defined brand/semantic background variable or provide a real fallback.`
      );
      continue;
    }

    if (bodyBackground.hasResolvableBackground) {
      continue;
    }

    const rootTag = findMobileRootTag(content);
    const rootBackground = rootTag
      ? analyzeTagBackground(rootTag, content, declaredVars)
      : { declaresBackground: false, hasResolvableBackground: false, unresolved: [] };

    if (rootBackground.unresolved.length > 0) {
      addError(
        'mobile-background-coverage',
        `${page.htmlSrc}: root background references undefined CSS variable(s): ${formatCssVarRefs(rootBackground.unresolved)}. Use a defined brand/semantic background variable or provide a real fallback.`
      );
      continue;
    }

    if (!rootBackground.hasResolvableBackground) {
      addError(
        'mobile-background-coverage',
        `${page.htmlSrc}: mobile mockups must declare a resolvable body/root background so short pages do not expose the canvas host background.`
      );
      continue;
    }

    if (!tagHasMinViewportHeight(rootTag)) {
      addError(
        'mobile-background-coverage',
        `${page.htmlSrc}: root owns the mobile page background but does not cover the viewport. Add min-h-screen or min-height:100vh to the root wrapper, or put the background on body.`
      );
    }

    if (hasFixedMobileViewportHeight(content) && /height\s*:\s*(?:1[4-9]\d|[2-7]\d{2})px\b/i.test(content)) {
      addWarning(
        'mobile-background-coverage',
        `${page.htmlSrc}: fixed mobile viewport height plus large spacer-like heights can create blank lower-page areas; prefer natural document flow and meaningful bottom content.`
      );
    }
  }
}

function readDesignJson(designDir, designFile) {
  const designPath = path.join(designDir, designFile);
  try {
    return JSON.parse(fs.readFileSync(designPath, 'utf8'));
  } catch (error) {
    addWarning('design-library-identity', `Cannot parse ${designFile} for Library identity check: ${error.message}`);
    return null;
  }
}

function validateDesignLibraryIdentityObject(identity, nodePath) {
  const requiredFields = ['name', 'id', 'version', 'scope', 'path', 'versionSource'];
  if (typeof identity !== 'object' || identity === null || Array.isArray(identity)) {
    addError('design-library-identity', `${nodePath} must be an object in Library-bound mode`);
    return false;
  }

  let valid = true;
  for (const field of requiredFields) {
    if (!Object.prototype.hasOwnProperty.call(identity, field)) {
      addError('design-library-identity', `${nodePath}.${field} is required; use null when unavailable`);
      valid = false;
      continue;
    }

    const value = identity[field];
    if (field === 'version') {
      if (value !== null && typeof value !== 'string' && typeof value !== 'number') {
        addError('design-library-identity', `${nodePath}.${field} must be a string, number, or null`);
        valid = false;
      }
    } else if (value !== null && typeof value !== 'string') {
      addError('design-library-identity', `${nodePath}.${field} must be a string or null`);
      valid = false;
    }
  }

  return valid;
}

function normalizeIdentityValue(value) {
  return value === undefined || value === null ? null : String(value);
}

function validateLibraryIdentity(designDir, designFiles) {
  console.log('\nChecking Design Library identity...');

  const summary = loadOrchestrationSummary(designDir);
  const operatingMode = summary?.designSource?.operatingMode;
  if (operatingMode !== 'library-bound') {
    console.log('  [OK] Not Library-bound; Library identity check skipped');
    return;
  }

  const summaryIdentity = summary?.designSource?.libraryIdentity;
  const summaryValid = validateDesignLibraryIdentityObject(
    summaryIdentity,
    'runtime-orchestration-summary.json.designSource.libraryIdentity'
  );

  if (designFiles.length === 0) {
    addError('design-library-identity', 'Cannot verify .design config.designLibrary because no .design file was found');
    return;
  }

  let checked = 0;
  for (const designFile of designFiles) {
    const designJson = readDesignJson(designDir, designFile);
    const designIdentity = designJson?.config?.designLibrary;
    const designValid = validateDesignLibraryIdentityObject(
      designIdentity,
      `${designFile}.config.designLibrary`
    );
    if (!summaryValid || !designValid) continue;

    for (const field of ['name', 'id', 'version', 'scope', 'path']) {
      const summaryValue = normalizeIdentityValue(summaryIdentity[field]);
      const designValue = normalizeIdentityValue(designIdentity[field]);
      if (summaryValue !== designValue) {
        addError(
          'design-library-identity',
          `${designFile}.config.designLibrary.${field} (${designValue}) must match runtime-orchestration-summary.json.designSource.libraryIdentity.${field} (${summaryValue})`
        );
      }
    }
    checked += 1;
  }

  if (checked > 0) {
    console.log(`  [OK] Library identity recorded in ${checked} .design file(s)`);
  }
}

function getAttr(tag, name) {
  const match = tag.match(new RegExp(`\\b${name}=["']([^"']*)["']`, 'i'));
  return match ? match[1] : '';
}

function hasMoreAffordance(html) {
  return /data-lucide=["'](?:more-horizontal|ellipsis)["']/.test(html) || /[···⋯]/.test(html) || /aria-label=["'](?:更多|More)["']/.test(html);
}

function hasCloseAffordance(html) {
  return /data-lucide=["'](?:x|circle-x)["']/.test(html) || /aria-label=["'](?:关闭|Close)["']/.test(html) || /[×✕]/.test(html);
}

function hasCapsuleDivider(html) {
  return /\bw-px\b|\bborder-l\b|\bdivide-x\b/.test(html);
}

function parseCssAlpha(rawAlpha) {
  if (!rawAlpha) return null;
  const trimmed = rawAlpha.trim();
  if (!trimmed) return null;
  if (trimmed.endsWith('%')) return Number(trimmed.slice(0, -1)) / 100;
  return Number(trimmed);
}

function extractShadowAlphas(value) {
  const alphas = [];
  const colorPattern = /\b(rgba?|hsla?)\(([^)]*)\)/gi;
  for (const m of value.matchAll(colorPattern)) {
    const fn = m[1].toLowerCase();
    const body = m[2].trim();
    let alpha = null;

    if (body.includes('/')) {
      alpha = parseCssAlpha(body.split('/').pop());
    } else {
      const parts = body.split(',').map(part => part.trim());
      if ((fn === 'rgba' || fn === 'hsla') && parts.length >= 4) {
        alpha = parseCssAlpha(parts[3]);
      } else {
        alpha = 1;
      }
    }

    if (Number.isFinite(alpha)) alphas.push(alpha);
  }
  return alphas;
}

function isFloatingShadowToken(tokenName) {
  return /(?:float|floating|popover|modal|overlay|drawer|dropdown|tooltip|toast|menu|dialog)/i.test(tokenName)
    || /^--shadow-(?:2|3)$/i.test(tokenName);
}

function validateHtmlQualityRules(designDir, operatingMode = 'free-explore') {
  const isFreeExplore = operatingMode !== 'library-bound';
  // Aesthetic/token-discipline issues: warning in free-explore, error in library-bound.
  // This prevents expensive repair loops for non-functional visual quality issues.
  const addAestheticIssue = isFreeExplore ? addWarning : addError;
  console.log('\nChecking HTML quality rules (tokens / images / CSS delivery)...');

  const pagesDir = path.join(designDir, 'pages');
  const assetsDir = path.join(designDir, 'assets');
  if (!fs.existsSync(pagesDir)) return;

  const htmlFiles = fs.readdirSync(pagesDir).filter(f => f.endsWith('.html'));
  if (htmlFiles.length === 0) return;

  const brandCssPath = path.join(designDir, 'colors_and_type.css');
  // secondary/accent checks are free-explore only — Library-bound DLs may legitimately define these tokens.
  const shouldCheckFreeExploreBrandCss = isFreeExplore;
  if (fs.existsSync(brandCssPath) && shouldCheckFreeExploreBrandCss) {
    try {
      const brandCss = fs.readFileSync(brandCssPath, 'utf8');
      const forbiddenBrandHuePattern = /--(?:[a-z0-9]+-)?(?:color-)?(?:secondary|accent)(?:-[a-z0-9]+)?\s*:/gi;
      const forbiddenBrandHues = [...brandCss.matchAll(forbiddenBrandHuePattern)].map(m => m[0].replace(/\s*:$/, ''));
      if (forbiddenBrandHues.length > 0) {
        addAestheticIssue(
          'html-quality',
          `colors_and_type.css: free-explore brand CSS must use one primary hue only; forbidden secondary/accent brand variables found (${[...new Set(forbiddenBrandHues)].slice(0, 12).join(', ')}). Use --state-success/warning/error/info only for semantic states.`
        );
      }

      const forbiddenRadiusTokenPattern = /--(?:[a-z0-9]+-)?radius-(?:xl|2xl|3xl|4xl|huge|large)\s*:\s*([^;]+);/gi;
      const forbiddenRadiusTokens = [];
      for (const m of brandCss.matchAll(forbiddenRadiusTokenPattern)) {
        const token = m[0].replace(/\s*:\s*[^;]+;$/, '');
        const value = m[1].trim();
        if (!/^1(?:2|6)px$/.test(value)) {
          forbiddenRadiusTokens.push(`${token}: ${value}`);
        }
      }

      const oversizedRadiusPattern = /--(?:[a-z0-9]+-)?radius-[a-z0-9-]+\s*:\s*(\d+(?:\.\d+)?)px\s*;/gi;
      const oversizedRadiusTokens = [];
      for (const m of brandCss.matchAll(oversizedRadiusPattern)) {
        if (/--(?:[a-z0-9]+-)?radius-(?:full|pill)\s*:/i.test(m[0])) continue;
        const value = Number(m[1]);
        if (value > 16) {
          const token = m[0].replace(/\s*:\s*[^;]+;$/, '');
          oversizedRadiusTokens.push(`${token}: ${value}px`);
        }
      }

      const radiusViolations = [...new Set([...forbiddenRadiusTokens, ...oversizedRadiusTokens])];
      if (radiusViolations.length > 0) {
        addAestheticIssue(
          'html-quality',
          `colors_and_type.css: free-explore radius tokens must stay within the restrained 2/4/8/12/16px scale; oversized or forbidden radius tokens found (${radiusViolations.slice(0, 12).join(', ')}). Do not use 20px+ radii unless the user explicitly requested large rounded shapes.`
        );
      }

      const rootCss = [...brandCss.matchAll(/:root\s*\{([\s\S]*?)\}/g)].map(m => m[1]).join('\n');
      const shadowTokenPattern = /(--[a-z0-9-]*shadow[a-z0-9-]*)\s*:\s*([^;]+);/gi;
      const staticShadowViolations = [];
      for (const m of rootCss.matchAll(shadowTokenPattern)) {
        const tokenName = m[1];
        if (isFloatingShadowToken(tokenName)) continue;
        const value = m[2].trim();
        const overLimit = extractShadowAlphas(value).filter(alpha => alpha > 0.05);
        if (overLimit.length > 0) {
          staticShadowViolations.push(`${tokenName}: ${value}`);
        }
      }

      if (staticShadowViolations.length > 0) {
        addAestheticIssue(
          'html-quality',
          `colors_and_type.css: ordinary/static shadow tokens must keep every shadow alpha <= 0.05; deeper shadows are allowed only for floating-layer tokens such as modal/popover/dropdown/drawer/overlay (${staticShadowViolations.slice(0, 12).join(', ')}).`
        );
      }
    } catch (e) {
      // Other directory/file existence checks report unreadable files elsewhere.
    }
  }

  const namedColorPattern = /\b(?:bg|text|border|from|to|via|ring|divide|outline|decoration|accent|caret|fill|stroke)-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}\b/g;
  const arbitraryColorPattern = /\b(?:bg|text|border|from|to|via|ring|shadow|fill|stroke)-\[#/;
  const inlineHardcodedColorPattern = /(?:color|background|background-color|border-color|box-shadow)\s*:\s*#[0-9a-fA-F]{3,8}\b/;
  const brandCssLinkPattern = /<link\b[^>]*rel=["']stylesheet["'][^>]*(?:colors_and_type\.css|brand css|theme-vars)[^>]*>/i;
  const imgSrcPattern = /<img\b[^>]*\bsrc=["']([^"']+)["'][^>]*>/gi;
  const forbiddenSecondaryAccentUsagePattern = /var\(\s*--(?:[a-z0-9]+-)?(?:color-)?(?:secondary|accent)(?:-[a-z0-9]+)?\s*\)/i;

  for (const htmlFile of htmlFiles) {
    const htmlPath = path.join(pagesDir, htmlFile);
    const content = readHtmlFileCached(htmlPath, htmlFile);
    if (content === null) continue;

    const visibleContent = stripThemeVars(content);

    if (brandCssLinkPattern.test(visibleContent)) {
      addError(
        'html-quality',
        `${htmlFile}: brand CSS must be inlined by apply-html-head-contract.mjs; do not use <link rel="stylesheet"> for colors_and_type.css`
      );
    }

    const namedColors = [...visibleContent.matchAll(namedColorPattern)].map(m => m[0]);
    if (namedColors.length > 0) {
      addAestheticIssue(
        'html-quality',
        `${htmlFile}: Tailwind named color utilities are forbidden (${[...new Set(namedColors)].slice(0, 8).join(', ')}). Use brand CSS variables instead.`
      );
    }

    if (arbitraryColorPattern.test(visibleContent) || inlineHardcodedColorPattern.test(visibleContent)) {
      addAestheticIssue(
        'html-quality',
        `${htmlFile}: hardcoded colors are forbidden outside <style id="theme-vars">. Use brand CSS variables from the token reference.`
      );
      addRepairPlanHint('hardcoded-color-in-body', {
        owner: 'sub-agent',
        repairScope: 'targeted-token-replace',
        strategy: 'targeted_token_replace_once',
        affectedFiles: [htmlFile],
        allowSourceRead: 'no-full-html-read',
        maxValidationRuns: 2
      });
    }

    if (isFreeExplore && forbiddenSecondaryAccentUsagePattern.test(visibleContent)) {
      addAestheticIssue(
        'html-quality',
        `${htmlFile}: free-explore pages must not use secondary/accent brand variables. Use the single primary hue, neutral tints, or --state-success/warning/error/info for real semantic states.`
      );
    }

    let imgMatch;
    while ((imgMatch = imgSrcPattern.exec(content)) !== null) {
      const src = imgMatch[1].trim();
      if (/^(https?:)?\/\//i.test(src) || src.startsWith('data:')) {
        addError('html-quality', `${htmlFile}: external/base64 image source is forbidden: ${src}`);
        addRepairPlanHint('external-image-url', {
          owner: 'sub-agent',
          repairScope: 'targeted-path-fix',
          strategy: 'fix_image_paths_once',
          affectedFiles: [htmlFile],
          allowSourceRead: 'no-full-html-read',
          maxValidationRuns: 2
        });
        continue;
      }
      if (!src.startsWith('../assets/')) {
        addError('html-quality', `${htmlFile}: image source must use ../assets/ relative path: ${src}`);
        continue;
      }
      const assetRel = src.slice('../assets/'.length);
      const assetPath = path.join(assetsDir, assetRel);
      if (!fs.existsSync(assetPath)) {
        addError('html-quality', `${htmlFile}: image references missing asset file: ${src}`);
      }
    }
  }
}

function validateMiniProgramChromeRules(designDir, operatingMode = 'free-explore') {
  const isFreeExplore = operatingMode !== 'library-bound';
  console.log('\nChecking mini program chrome rules...');
  const summary = loadOrchestrationSummary(designDir);
  if (!summary || !Array.isArray(summary.pages)) {
    console.log('  [OK] No orchestration summary; mini program chrome check skipped');
    return;
  }

  const pagesDir = path.join(designDir, 'pages');
  if (!fs.existsSync(pagesDir)) return;

  const miniPages = summary.pages.filter((page) => page && page.miniProgramStyle === true && typeof page.htmlSrc === 'string');
  if (miniPages.length === 0) {
    console.log('  [OK] No miniProgramStyle pages');
    return;
  }

  for (const page of miniPages) {
    const htmlFile = path.basename(page.htmlSrc);
    const htmlPath = path.join(pagesDir, htmlFile);
    if (!fs.existsSync(htmlPath)) continue;

    const content = readHtmlFileCached(htmlPath, htmlFile);
    if (content === null) continue;
    const divRegex = /(<div\b[^>]*>)([\s\S]*?)<\/div>/gi;
    let match;
    let foundRightCapsule = false;

    while ((match = divRegex.exec(content)) !== null) {
      const tag = match[1];
      const inner = match[2].trim();
      const cls = getAttr(tag, 'class');
      const hasCapsuleSize = /\bw-\[(?:87|88)px\]/.test(cls) && /\bh-8\b/.test(cls);
      if (!hasCapsuleSize) continue;

      if (/\bopacity-0\b|\bpointer-events-none\b/.test(cls)) {
        addError('mini-program-chrome', `${htmlFile}: mini program right capsule must be visible and functional, not an invisible spacer.`);
        continue;
      }

      foundRightCapsule = true;

      if (inner.length === 0) {
        addError('mini-program-chrome', `${htmlFile}: mini program right capsule is empty. It must contain more and close actions.`);
        continue;
      }
      if (!hasMoreAffordance(inner)) {
        addError('mini-program-chrome', `${htmlFile}: mini program right capsule missing more action.`);
      }
      if (!hasCloseAffordance(inner)) {
        addError('mini-program-chrome', `${htmlFile}: mini program right capsule missing close action.`);
      }
      if (!hasCapsuleDivider(inner)) {
        addError('mini-program-chrome', `${htmlFile}: mini program right capsule missing divider between more and close actions.`);
      }
    }

    if (!foundRightCapsule) {
      addError('mini-program-chrome', `${htmlFile}: miniProgramStyle page must include a visible right system capsule.`);
    }

    if (/w-\[(?:87|88)px\][^"']*(?:var\(--(?:primary|secondary|accent|card)\)|shadow-\[var\(--shadow|shadow-)/.test(content)) {
      addError('mini-program-chrome', `${htmlFile}: mini program system chrome must not use brand surface/color tokens or brand shadows.`);
    }
  }
}

function validateThemeFiles(designDir) {
  console.log('\nChecking theme files...');

  const themeDir = path.join(designDir, 'theme');

  if (!fs.existsSync(themeDir)) {
    console.log('  [OK] No theme files (optional)');
    return;
  }

  const themeFiles = fs.readdirSync(themeDir).filter(f => f.endsWith('.theme'));

  if (themeFiles.length === 0) {
    console.log('  [OK] No theme files (optional)');
  } else {
    console.log(`  [OK] Found ${themeFiles.length} theme file(s)`);

    for (const themeFile of themeFiles) {
      const themePath = path.join(themeDir, themeFile);
      try {
        const content = fs.readFileSync(themePath, 'utf8');
        // parse JSON
        const parsed = JSON.parse(content);

        // basic structure check
        if (!parsed.styles || !parsed.styles.light || !parsed.styles.dark) {
          addWarning('theme-files', `Theme file missing styles.light or styles.dark: ${themeFile}`);
        } else {
          console.log(`    [OK] ${themeFile} looks valid`);
        }
      } catch (error) {
        addWarning('theme-files', `Invalid theme file ${themeFile}: ${error.message}`);
      }
    }
  }
}

function checkAssetsDirectory(designDir, designFiles, operatingMode = 'free-explore') {
  // Assets coverage is a canvas contract (not just visual) — always blocking.
  const addCoverageIssue = addError;
  console.log('\nChecking assets directory...');

  const assetsDir = path.join(designDir, 'assets');

  if (!fs.existsSync(assetsDir)) {
    addWarning('assets', 'assets/ directory not found');
    return;
  }

  const assets = fs.readdirSync(assetsDir, { withFileTypes: true });
  console.log(`  [OK] Assets directory found with ${assets.length} item(s)`);

  // Reverse coverage: every image file under assets/ must be registered as an image node in .design
  // Subdirectories (e.g., assets/icons/) are skipped — they contain HTML support assets, not canvas images
  const IMAGE_EXTENSIONS = new Set(['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']);
  const imageFiles = assets
    .filter(entry => entry.isFile() && IMAGE_EXTENSIONS.has(path.extname(entry.name).toLowerCase()))
    .map(entry => entry.name);

  if (imageFiles.length === 0) {
    return;
  }

  if (!designFiles || designFiles.length === 0) {
    return;
  }

  // Aggregate registered imageSrc across all .design files
  const registeredImageSrcs = new Set();
  for (const designFile of designFiles) {
    const designPath = path.join(designDir, designFile);
    try {
      const raw = fs.readFileSync(designPath, 'utf8');
      const parsed = JSON.parse(raw);
      if (!parsed || !Array.isArray(parsed.data)) continue;
      for (const node of parsed.data) {
        if (node && typeof node === 'object' && node.type === 'image' && node.devMetadata && typeof node.devMetadata.imageSrc === 'string') {
          registeredImageSrcs.add(node.devMetadata.imageSrc.replace(/^\.\//, ''));
        }
      }
    } catch {
      // .design parsing errors are already reported by validate-design-file-format.mjs; skip here
    }
  }

  const unregistered = imageFiles.filter((name) => !registeredImageSrcs.has(`assets/${name}`));
  if (unregistered.length > 0) {
    for (const name of unregistered) {
      addCoverageIssue(
        'assets-coverage',
        `Image file "assets/${name}" exists on disk but is not registered as a type:"image" node in any .design file. ` +
        `Every image asset must have a corresponding image node so it surfaces on the canvas. ` +
        `Fix: append an image node to .design (see intent-workflows/intent-project-complex-build/01-graphic-asset-preparation.md or intent-workflows/intent-project-mutation/edit-existing-project.md Step 2b').`
      );
    }
  } else {
    console.log(`  [OK] All ${imageFiles.length} image asset(s) are registered as image nodes`);
  }
}

function checkIconPathValidity(designDir) {
  const summary = loadOrchestrationSummary(designDir);
  if (summary?.designSource?.operatingMode !== 'library-bound') return;
  if (!summary?.designSource?.iconAssets) return;

  console.log('\nChecking Design Library icon path validity...');

  const pagesDir = path.join(designDir, 'pages');
  if (!fs.existsSync(pagesDir)) return;

  const htmlFiles = fs.readdirSync(pagesDir).filter(f => f.endsWith('.html'));
  const maskPathRegex = /mask-image:\s*url\(['"]?([^'")\s]+)['"]?\)/g;
  let checkedCount = 0;
  let missingCount = 0;

  for (const htmlFile of htmlFiles) {
    const htmlPath = path.join(pagesDir, htmlFile);
    const content = readHtmlFileCached(htmlPath, htmlFile);
    if (content === null) continue;

    let match;
    while ((match = maskPathRegex.exec(content)) !== null) {
      const iconPath = match[1];
      if (!iconPath.includes('assets/icons/')) continue;
      const resolved = path.resolve(pagesDir, iconPath);
      checkedCount++;
      if (!fs.existsSync(resolved)) {
        missingCount++;
        addWarning(
          'icon-path',
          `${htmlFile}: mask-image references "${iconPath}" but file does not exist. ` +
          `Fix: replace with Lucide fallback or verify icon was copied from Design Library.`
        );
      }
    }
  }

  if (checkedCount > 0 && missingCount === 0) {
    console.log(`  [OK] All ${checkedCount} icon path(s) verified`);
  }
}

function printReport() {
  console.log('\n');

  if (warnings.length > 0) {
    printSection('Warnings', '!');
    warnings.forEach(w => console.log(`  [WARN] ${w}`));
    console.log('\n');
  }

  if (terminalValidationState?.terminalState) {
    printSection('Validation Stopped', '=');
    console.log(`Terminal state: ${terminalValidationState.terminalState}`);
    console.log('Stop and report the smallest blocking summary from validation-report.json.');
    printStopDirectives(terminalValidationState);
    return false;
  }

  if (errors.length > 0) {
    printSection('Errors', 'X');
    errors.forEach(e => console.log(`  [FAIL] ${e}`));
    console.log('\n');

    printSection('Validation Failed', '=');
    console.log(`Found ${errors.length} error(s) and ${warnings.length} warning(s).`);
    console.log('\nPlease fix all errors before presenting results to the user.');
    printRepairDirectives(false);
    return false;
  } else {
    printSection('Validation Passed', '=');
    console.log('All checks passed!');
    if (warnings.length > 0) {
      console.log(`\nNote: ${warnings.length} warning(s) found, but these are non-blocking.`);
    }
    printRepairDirectives(true);
    return true;
  }
}

function printStopDirectives(status) {
  console.log('\n--- TERMINAL_STOP_DIRECTIVES ---');
  console.log('OUTCOME: terminal_stop');
  console.log('REPAIRABLE: false');
  console.log('NEXT_ACTION: stop_and_report_blocking_summary');
  console.log('NEXT_CHECK: NONE');
  console.log('FORBIDDEN: do not repair ledger, do not delete validation state, do not rerun validation');
  const violations = Array.isArray(status?.violations) ? status.violations : [];
  if (violations.length > 0) {
    console.log(`TERMINAL_VIOLATIONS: ${violations.slice(0, 5).join(' | ')}`);
  }
  console.log('--- END_DIRECTIVES ---');
}

function printRepairDirectives(success) {
  console.log('\n--- REPAIR_DIRECTIVES ---');
  if (success) {
    console.log('REPAIR_SCOPE_REMAINING: 0');
    console.log('NEXT_ACTION: NONE');
  } else if (repairPlanHints.length > 0) {
    const scriptHints = repairPlanHints.filter(h => h.strategy === 'run_apply_html_head_replace');
    const allFiles = [...new Set(repairPlanHints.flatMap(h => h.affectedFiles || []))];
    console.log('REPAIR_SCOPE_REMAINING: 1');
    if (scriptHints.length > 0 && scriptHints.length === repairPlanHints.length) {
      const files = [...new Set(scriptHints.flatMap(h => h.affectedFiles || []))].join(' ');
      console.log(`NEXT_ACTION: run apply-html-head-contract.mjs <css-path> ${files} --replace-head`);
    } else {
      console.log('NEXT_ACTION: follow repair state machine in validation-report.json repairPlanHints');
    }
    if (allFiles.length > 0) {
      console.log(`AFFECTED_FILES: ${allFiles.join(', ')}`);
    }
    console.log('FORBIDDEN: read full HTML, read validator source, start browser preview, create helper scripts');
  } else {
    console.log('REPAIR_SCOPE_REMAINING: 1');
    console.log('NEXT_ACTION: follow validation-report.json repairActionTable and delivery-quality/design-artifact-validation.md');
    console.log('FORBIDDEN: read full HTML, read validator source, start browser preview, create helper scripts');
  }
  console.log('--- END_DIRECTIVES ---');
}

function buildRepairActionTable() {
  return errors.map(error => {
    const matched = REPAIR_ACTION_TABLE.find(row => row.errorPattern.test(error));
    if (matched) {
      const { errorPattern, ...rest } = matched;
      return {
        error,
        ...rest,
      };
    }

    return {
      error,
      errorClass: 'unknown-blocking',
      severity: 'blocking',
      action: 'read validation report, classify owner, then use the narrowest targeted repair',
      owner: 'main-agent',
      sourceReadPolicy: 'no validator source read; targeted affected-file excerpt only',
    };
  });
}

function errorClassForSignature(error) {
  const matched = REPAIR_ACTION_TABLE.find(row => row.errorPattern.test(error));
  if (matched?.errorClass) return matched.errorClass;
  const bracketMatch = String(error || '').match(/^\[([^\]]+)\]/);
  if (bracketMatch) return bracketMatch[1];
  const colonMatch = String(error || '').match(/^([a-z0-9][a-z0-9_-]+):/i);
  if (colonMatch) return colonMatch[1];
  return 'unknown-blocking';
}

function normalizeErrorForSignature(error) {
  return String(error || '')
    .replace(/[a-f0-9]{32,}/gi, '<hash>')
    .replace(/\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\b/g, '<timestamp>')
    .replace(/\b\d{10,}\b/g, '<number>')
    .replace(/\s+/g, ' ')
    .trim();
}

function buildErrorSignatures(errorList = errors) {
  return errorList.map(error => {
    const errorClass = errorClassForSignature(error);
    const normalized = normalizeErrorForSignature(error);
    return {
      errorClass,
      normalized,
      signature: crypto.createHash('sha256').update(`${errorClass}:${normalized}`).digest('hex'),
    };
  });
}

function signaturesFromHistoryRecord(record) {
  const rows = Array.isArray(record?.errorSignatures)
    ? record.errorSignatures
    : (Array.isArray(record?.renderBlockingErrorSignatures) ? record.renderBlockingErrorSignatures : []);
  return rows.map(row => (typeof row === 'string' ? row : row?.signature)).filter(Boolean);
}

function validateRepeatedErrorConvergence(summary) {
  if (terminalValidationState?.terminalState || errors.length === 0) return;
  const history = Array.isArray(summary?.project?.validationHistory) ? summary.project.validationHistory : [];
  const failedHistory = history.filter(item => item && (item.success === false || Number(item.exitCode) === 1));
  if (failedHistory.length === 0) return;

  const currentRows = buildErrorSignatures();
  for (const row of currentRows) {
    let consecutiveCount = 1;
    for (let index = failedHistory.length - 1; index >= 0; index--) {
      const signatures = new Set(signaturesFromHistoryRecord(failedHistory[index]));
      if (!signatures.has(row.signature)) break;
      consecutiveCount += 1;
    }
    if (consecutiveCount >= 3) {
      terminalValidationState = {
        terminalState: 'repeated-error-non-convergent',
        nextAction: 'stop_and_report_blocking_summary',
        repeatedErrorSignature: row.signature,
        repeatedErrorClass: row.errorClass,
        repeatedErrorCount: consecutiveCount,
        violations: [
          `same validation error signature repeated ${consecutiveCount} consecutive time(s): ${row.errorClass}`,
          row.normalized,
        ],
        success: false,
      };
      addWarning('validation-discipline', `same validation error signature repeated ${consecutiveCount} consecutive time(s): ${row.errorClass}; stop instead of continuing repair`);
      return;
    }
  }
}

function buildNextCheck(designDir, summary, success) {
  const finishReadiness = deterministicToolPath('validate-finish-readiness.mjs');
  const restoreContract = deterministicToolPath('validate-restore-contract.mjs');
  const workspaceValidation = deterministicToolPath('validate-design-workspace.mjs');
  const errorText = errors.join('\n');
  const isRestore = summary?.project?.intentProfile?.caseFamily === 'restore_1to1' ||
    summary?.project?.resolvedLane === 'restore_1to1' ||
    summary?.project?.replicationMode === 'high-fidelity';

  if (success) {
    const finalResponseArg = ` --final-response-file=${shellQuote('<final-response-draft.md>')}`;
    return {
      type: 'finish-readiness',
      command: `node ${shellQuote(finishReadiness)} ${shellQuote(designDir)} ${isRestore ? `--check=all${finalResponseArg}` : '--check=all'}`,
      fullValidationAllowed: false,
      reason: isRestore
        ? 'restore workspace validation passed; run complete finish readiness with final response draft before delivery'
        : 'workspace validation passed; run complete finish readiness before final delivery',
    };
  }

    if (terminalValidationState?.terminalState) {
      return {
        type: 'stop',
        command: null,
        fullValidationAllowed: false,
        reason: terminalValidationState.terminalState,
        nextAction: 'stop_and_report_blocking_summary',
      };
    }

  if (/repair-ledger/i.test(errorText)) {
    return {
      type: 'repair-ledger',
      command: `node ${shellQuote(finishReadiness)} ${shellQuote(designDir)} --check=repair-ledger`,
      fullValidationAllowed: false,
      reason: 'current failure is repair ledger evidence; do not rerun full validation until this targeted check passes',
    };
  }

  if (isRestore && /restore-(?:source|document|measured|visual|region|css|pages|evidence)/i.test(errorText)) {
    return {
      type: 'restore-contract',
      command: `node ${shellQuote(restoreContract)} ${shellQuote(designDir)} --mode=preflight --apply-safe-fixes`,
      fullValidationAllowed: false,
      reason: 'restore contract/schema failure can be repaired or classified by the restore preflight gate',
    };
  }

  if (/post-validation mutation|artifact|readiness/i.test(errorText)) {
    return {
      type: 'artifact-readiness',
      command: `node ${shellQuote(finishReadiness)} ${shellQuote(designDir)} --check=artifact`,
      fullValidationAllowed: false,
      reason: 'artifact readiness can be checked without another full workspace validation run',
    };
  }

  if (isRestore && /dispatch|changedFiles|allowedWritePaths|toolCallLedger|toolDisciplineEvidence/i.test(errorText)) {
    return {
      type: 'dispatch-discipline',
      command: `node ${shellQuote(workspaceValidation)} ${shellQuote(designDir)} --check=dispatch-discipline --report-json=${shellQuote(path.join(designDir, 'validation-report.json'))}`,
      fullValidationAllowed: false,
      reason: 'restore dispatch discipline can be checked without another full workspace validation run',
    };
  }

  if (isRestore && /head|html-infrastructure|theme-vars|tailwind|semantic-token/i.test(errorText)) {
    return {
      type: 'html-infrastructure',
      command: `node ${shellQuote(workspaceValidation)} ${shellQuote(designDir)} --check=html-infrastructure --report-json=${shellQuote(path.join(designDir, 'validation-report.json'))}`,
      fullValidationAllowed: false,
      reason: 'restore HTML infrastructure can be checked without another full workspace validation run',
    };
  }

  if (isRestore) {
    return {
      type: 'blocked',
      command: null,
      fullValidationAllowed: false,
      reason: 'restore failure has no narrower deterministic targeted check; do not rerun full validation until the failure is classified',
    };
  }

  return {
    type: 'full',
    command: `node ${shellQuote(workspaceValidation)} ${shellQuote(designDir)} --report-json=${shellQuote(path.join(designDir, 'validation-report.json'))}`,
    fullValidationAllowed: true,
    reason: 'no narrower deterministic targeted check is available for the current failure class',
  };
}

function writeReportJson(reportJsonPath, report) {
  const resolvedReportPath = path.resolve(reportJsonPath);
  fs.mkdirSync(path.dirname(resolvedReportPath), { recursive: true });
  fs.writeFileSync(resolvedReportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf-8');
  console.log(`\nValidation report JSON: ${resolvedReportPath}`);
}

function buildTerminalStopFields(success) {
  const isTerminalStop = Boolean(terminalValidationState?.terminalState && !success);
  const terminalViolations = isTerminalStop && Array.isArray(terminalValidationState.violations)
    ? terminalValidationState.violations
    : [];
  return {
    outcome: isTerminalStop ? 'terminal_stop' : (success ? 'passed' : 'validation_failed'),
    repairable: !isTerminalStop,
    terminalViolations,
    terminalBlockingSummary: isTerminalStop
      ? {
          terminalState: terminalValidationState.terminalState,
          nextAction: 'stop_and_report_blocking_summary',
          violations: terminalViolations.slice(0, 8),
        }
      : null,
  };
}

function buildRepairContextPacket(designDir, summary, success) {
  if (terminalValidationState?.terminalState && !success) {
    const terminalFields = buildTerminalStopFields(success);
    return {
      schema_version: '1.0',
      purpose: 'terminal stop packet; do not repair',
      success,
      ...terminalFields,
      terminalState: terminalValidationState.terminalState,
      skillProvenance: normalizeSkillProvenance(summary),
      renderBlockingErrorCount: 0,
      softWarningCount: warnings.length,
      renderBlockingErrors: [],
      repairActionTable: [],
      repairPlanHints: [],
      nextCheck: buildNextCheck(designDir, summary, success),
      forbidden: [
        'do not repair ledger',
        'do not delete validation state',
        'do not rerun validation',
        'do not read validator source',
      ],
    };
  }

  const actionTable = buildRepairActionTable().map(row => ({
    errorClass: row.errorClass,
    owner: row.owner,
    severity: row.severity,
    action: row.action,
    affectedFiles: row.affectedFiles || [],
    sourceReadPolicy: row.sourceReadPolicy,
  }));
  return {
    schema_version: '1.0',
    purpose: 'small-context repair packet; read this before full validation-report.json',
    success,
      terminalState: terminalValidationState?.terminalState || null,
    skillProvenance: normalizeSkillProvenance(summary),
    renderBlockingErrorCount: errors.length,
    softWarningCount: warnings.length,
    renderBlockingErrors: errors.slice(0, 12),
    repairActionTable: actionTable.slice(0, 12),
    nextCheck: buildNextCheck(designDir, summary, success),
    forbidden: [
      'do not read validator source',
      'do not rerun full validation when nextCheck.fullValidationAllowed=false',
      'do not start preview/browser unless user explicitly asks',
      'do not hand-edit repair ledger fields',
    ],
  };
}

function printUsage() {
  console.error('Usage: node validate-design-workspace.mjs <design-directory-path> [--expected-pages=<N>] [--require-interactions=domId1:file1.html,...] [--check=all|changed-files-hash|html-infrastructure|dispatch-discipline] [--report-json=<path>]');
}

async function main() {
  const args = process.argv.slice(2);

  // parse args
  let designDir = undefined;
  let expectedPages = undefined;
  let requireInteractions = undefined; // raw string, forwarded as-is to validate-design-file-format.mjs
  let reportJsonPath = undefined;
  let check = 'all';
  const argErrors = [];

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--expected-pages=')) {
      const match = arg.match(/^--expected-pages=(\d+)$/);
      if (match) {
        expectedPages = parseInt(match[1], 10);
      } else {
        argErrors.push(`Invalid --expected-pages syntax: ${arg}`);
      }
    } else if (arg.startsWith('--require-interactions=')) {
      const match = arg.match(/^--require-interactions=(.+)$/);
      if (match) {
        requireInteractions = match[1];
      } else {
        argErrors.push(`Invalid --require-interactions syntax: ${arg}`);
      }
    } else if (arg.startsWith('--report-json=')) {
      const match = arg.match(/^--report-json=(.+)$/);
      if (match) {
        reportJsonPath = match[1];
      } else {
        argErrors.push(`Invalid --report-json syntax: ${arg}`);
      }
    } else if (arg.startsWith('--check=')) {
      const value = arg.slice('--check='.length);
      if (['all', 'changed-files-hash', 'html-infrastructure', 'dispatch-discipline'].includes(value)) {
        check = value;
      } else {
        argErrors.push(`Unsupported --check=${value}`);
      }
    } else if (arg.startsWith('--')) {
      argErrors.push(`Unknown flag: ${arg}`);
    } else if (designDir === undefined) {
      designDir = arg;
    } else {
      argErrors.push(`Unexpected positional argument: ${arg}`);
    }
  }

  if (argErrors.length > 0) {
    argErrors.forEach((error) => console.error(`[ERROR] ${error}`));
    printUsage();
    process.exit(1);
  }

  if (!designDir) {
    printUsage();
    process.exit(1);
  }

  designDir = path.resolve(designDir);

  printSection('Design Directory Scan', '=');
  console.log(`Design directory: ${designDir}`);
  if (expectedPages !== undefined) {
    console.log(`Expected pages: ${expectedPages}`);
  }

  if (!fs.existsSync(designDir)) {
    addError('directory', `Design directory not found: ${designDir}`);
    printReport();
    process.exit(1);
  }

  if (!fs.statSync(designDir).isDirectory()) {
    addError('directory', `Path is not a directory: ${designDir}`);
    printReport();
    process.exit(1);
  }

  if (check !== 'all') {
    const summary = loadOrchestrationSummary(designDir);
    if (check === 'html-infrastructure') {
      validateHtmlInfrastructure(designDir);
    } else if (check === 'dispatch-discipline') {
      validateDispatchChangedFilesDiscipline(designDir, summary);
    } else if (check === 'changed-files-hash') {
      console.log('\nChecking changed file hashes...');
      console.log('  [OK] project file hash collection completed');
    }
    validateRepeatedErrorConvergence(summary);
    const success = printReport();
    if (reportJsonPath) {
      try {
        writeReportJson(reportJsonPath, {
          success,
          ...buildTerminalStopFields(success),
          targetedCheck: check,
          skillProvenance: normalizeSkillProvenance(summary),
          renderBlockingErrorCount: errors.length,
          softWarningCount: warnings.length,
          renderBlockingErrors: errors,
          errorSignatures: buildErrorSignatures(),
          softWarnings: warnings,
          errorCount: errors.length,
          warningCount: warnings.length,
          errors,
          warnings,
            validationRunDisciplineStatus: getValidationRunDisciplineStatus(summary),
            terminalState: terminalValidationState?.terminalState || null,
            nextAction: terminalValidationState?.terminalState && !success
              ? { type: 'stop', reason: terminalValidationState.terminalState, command: null }
              : buildNextCheck(designDir, summary, success),
            repairActionTable: terminalValidationState?.terminalState && !success ? [] : buildRepairActionTable(),
            repairBatch: terminalValidationState?.terminalState && !success ? [] : buildRepairActionTable(),
            repairContextPacket: buildRepairContextPacket(designDir, summary, success),
          projectFileHashes: await collectProjectFileHashes(designDir),
          designDir,
          checkedAt: new Date().toISOString(),
        });
      } catch (error) {
        console.error(`[ERROR] Failed to write validation report JSON: ${error.message}`);
        process.exit(1);
      }
    }
    process.exit(success ? 0 : 1);
  }

  // run all checks
  validateDirectoryStructure(designDir);
  const designFiles = findDesignFiles(designDir);
  validateDesignFiles(designDir, designFiles, expectedPages, requireInteractions);
  validateHtmlFiles(designDir);
  validateHtmlInfrastructure(designDir);

  // Extract operatingMode for mode-aware checks.
  // free-explore (no Design Library) downgrades aesthetic/token checks to warnings.
  const summary = loadOrchestrationSummary(designDir);
  const operatingMode = summary?.designSource?.operatingMode || 'free-explore';
  const projectFacts = loadDesignProjectFacts(designDir, designFiles, summary);

  validateNoCustomStylesInHead(designDir, operatingMode);
  validateOrchestrationSummaryPresence(designDir, expectedPages, designFiles);
  validateValidationRepairLedger(summary, designDir);
  validateSemanticTokenFallback(designDir, operatingMode);
  validateDeviceTypeConsistency(projectFacts);
  validateMobileViewportMode(designDir, projectFacts);
  validateDesktopAppShellViewport(designDir, projectFacts);
  validateMobileDocumentScrollPages(designDir, projectFacts);
  validateMobileFixedViewportArtifacts(designDir, projectFacts);
  validateMobileBottomOverlayRisk(designDir, projectFacts);
  validateMobileNavigationDispatchEvidence(projectFacts, summary);
  validateDispatchChangedFilesDiscipline(designDir, summary);
  validateMobileNavigationConsistency(designDir, projectFacts);
  validateMobileBackgroundCoverage(designDir, projectFacts);
  validateLibraryIdentity(designDir, designFiles);
  validateLibraryBoundCustomCss(designDir);
  validateRestoreEvidence(designDir, summary);
  validateRestoreSourceFactCoverage(summary);
  validateGraphicLayoutCompleteness(designDir, summary);
  validateDefaultDeliverableVisibility(designDir, summary);
  validateValidationRunDiscipline(summary);
  validateHtmlQualityRules(designDir, operatingMode);
  validateMiniProgramChromeRules(designDir, operatingMode);
  validateTailwindApplyRules(designDir);
  validateThemeFiles(designDir);
  checkAssetsDirectory(designDir, designFiles, operatingMode);
  checkIconPathValidity(designDir);
  validateRepeatedErrorConvergence(summary);

  // print report
  const success = printReport();

  if (reportJsonPath) {
    try {
      writeReportJson(reportJsonPath, {
        success,
        ...buildTerminalStopFields(success),
        skillProvenance: normalizeSkillProvenance(summary),
        operatingMode,
        renderBlockingErrorCount: errors.length,
        softWarningCount: warnings.length,
        renderBlockingErrors: errors,
        errorSignatures: buildErrorSignatures(),
        softWarnings: warnings,
          repairPlanHints: terminalValidationState?.terminalState && !success
            ? []
            : repairPlanHints.map(({ _key, ...hint }) => hint),
          repairActionTable: terminalValidationState?.terminalState && !success ? [] : buildRepairActionTable(),
        errorCount: errors.length,
        warningCount: warnings.length,
        errors,
        warnings,
          validationRunDisciplineStatus: getValidationRunDisciplineStatus(summary),
          terminalState: terminalValidationState?.terminalState || null,
          nextCheck: terminalValidationState?.terminalState && !success
            ? { type: 'stop', reason: terminalValidationState.terminalState, command: null }
            : buildNextCheck(designDir, summary, success),
          repairBatch: terminalValidationState?.terminalState && !success ? [] : buildRepairActionTable(),
        repairContextPacket: buildRepairContextPacket(designDir, summary, success),
        projectFileHashes: await collectProjectFileHashes(designDir),
        designDir,
        expectedPages: expectedPages ?? null,
        requireInteractions: requireInteractions ?? null,
        checkedAt: new Date().toISOString()
      });
    } catch (error) {
      console.error(`[ERROR] Failed to write validation report JSON: ${error.message}`);
      process.exit(1);
    }
  }

  process.exit(success ? 0 : 1);
}

main().catch(error => {
  console.error(`[ERROR] ${error.message}`);
  process.exit(1);
});
