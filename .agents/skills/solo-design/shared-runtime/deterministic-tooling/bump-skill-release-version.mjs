#!/usr/bin/env node

/**
 * Bump solo-design skill-release-manifest.json to the latest skill file
 * modification timestamp.
 *
 * Version format: YYYY.MM.DD.HH.mm.ss, e.g. 2026.07.13.22.42.59.
 *
 * Usage:
 *   node bump-skill-release-version.mjs [--if-changed] [--version=YYYY.MM.DD.HH.mm.ss] [--json] [--dry-run]
 */

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = path.resolve(SCRIPT_DIR, '..', '..');
const MANIFEST_FILE = 'skill-release-manifest.json';
const IGNORED = new Set(['.DS_Store']);

function parseArgs(argv) {
  const args = {
    ifChanged: false,
    dryRun: false,
    json: false,
    version: null,
  };
  const errors = [];

  for (const arg of argv) {
    if (arg === '--if-changed') args.ifChanged = true;
    else if (arg === '--dry-run') args.dryRun = true;
    else if (arg === '--json') args.json = true;
    else if (arg.startsWith('--version=')) args.version = arg.slice('--version='.length);
    else errors.push(`Unknown flag: ${arg}`);
  }

  if (args.version && !/^\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{2}$/.test(args.version)) {
    errors.push(`--version must use YYYY.MM.DD.HH.mm.ss format; found ${args.version}`);
  }
  return { args, errors };
}

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
  return null;
}

function pad2(value) {
  return String(value).padStart(2, '0');
}

function formatVersion(date) {
  return [
    date.getFullYear(),
    pad2(date.getMonth() + 1),
    pad2(date.getDate()),
    pad2(date.getHours()),
    pad2(date.getMinutes()),
    pad2(date.getSeconds()),
  ].join('.');
}

function listSkillFiles(root, prefix = '') {
  const dir = path.join(root, prefix);
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (IGNORED.has(entry.name)) continue;
    const rel = prefix ? path.join(prefix, entry.name) : entry.name;
    if (entry.isDirectory()) out.push(...listSkillFiles(root, rel));
    else if (entry.isFile() && rel !== MANIFEST_FILE) out.push(rel);
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

async function latestSkillFileMtime() {
  const files = listSkillFiles(SKILL_DIR).map(rel => ({
    fullPath: path.join(SKILL_DIR, rel),
    displayPath: rel.replace(/\\/g, '/'),
  }));

  let latest = 0;
  let latestFile = null;
  const stats = await mapLimit(files, 16, async file => {
    const stat = await fs.promises.stat(file.fullPath);
    return { ...file, mtime: stat.mtimeMs };
  });
  for (const { mtime, displayPath } of stats) {
    if (mtime > latest) {
      latest = mtime;
      latestFile = displayPath;
    }
  }
  return {
    latest,
    latestFile,
    version: latest > 0 ? formatVersion(new Date(latest)) : formatVersion(new Date()),
  };
}

function gitHasNonManifestSkillChanges(repoRoot) {
  if (!repoRoot) return true;
  try {
    const skillPath = path.relative(repoRoot, SKILL_DIR);
    const output = execFileSync('git', ['status', '--porcelain', '--', skillPath], {
      cwd: repoRoot,
      encoding: 'utf8',
      shell: process.platform === 'win32',
    });
    return output
      .split('\n')
      .map(line => line.trim())
      .filter(Boolean)
      .some(line => !line.endsWith(MANIFEST_FILE));
  } catch {
    return true;
  }
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, value) {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

async function main() {
  const { args, errors } = parseArgs(process.argv.slice(2));
  if (errors.length > 0) {
    const result = { success: false, errors };
    console.error(JSON.stringify(result, null, 2));
    process.exit(1);
  }

  const repoRoot = findRepoRoot(SCRIPT_DIR);
  const hasChanges = gitHasNonManifestSkillChanges(repoRoot);
  if (args.ifChanged && !hasChanges) {
    const result = { success: true, skipped: true, reason: 'no non-manifest solo-design skill changes detected' };
    if (args.json) console.log(JSON.stringify(result, null, 2));
    else console.log('[OK] skill release version unchanged: no solo-design skill changes detected');
    return;
  }

  const latest = await latestSkillFileMtime();
  const nextVersion = args.version || latest.version;
  const manifestPath = path.join(SKILL_DIR, MANIFEST_FILE);
  if (!fs.existsSync(manifestPath)) {
    throw new Error(`missing manifest: ${manifestPath}`);
  }
  const manifest = readJson(manifestPath);
  const changed = manifest.version !== nextVersion;
  if (changed) {
    manifest.version = nextVersion;
    manifest.version_source = MANIFEST_FILE;
    if (!args.dryRun) writeJson(manifestPath, manifest);
  }

  const result = {
    success: true,
    version: nextVersion,
    source: args.version ? '--version' : 'latest-skill-file-mtime',
    latestFile: latest.latestFile,
    changed: changed ? 1 : 0,
    touched: changed ? ['solo-design'] : [],
    unchanged: changed ? [] : ['solo-design'],
    dryRun: args.dryRun,
  };
  if (args.json) console.log(JSON.stringify(result, null, 2));
  else if (changed) console.log(`[OK] solo-design skill version bumped to ${nextVersion}`);
  else console.log(`[OK] solo-design skill version already ${nextVersion}`);
}

main().catch(error => {
  console.error(error?.stack || error?.message || String(error));
  process.exit(1);
});
