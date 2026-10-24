#!/usr/bin/env node
'use strict';

// Read-only guard for shared worktrees. This script never writes to the repository.
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const EXIT = { OK: 0, DEFER: 1, CONFLICT: 2, ERROR: 3 };

function baseEnv() {
  return {
    ...process.env,
    GIT_CONFIG_NOSYSTEM: '1',
    GIT_TERMINAL_PROMPT: '0',
    GIT_EDITOR: 'true',
    GIT_SEQUENCE_EDITOR: 'true',
    GIT_PAGER: 'cat',
    PAGER: 'cat',
  };
}

function runGit(cwd, args, env) {
  const r = spawnSync('git', args, {
    cwd,
    encoding: 'utf8',
    env: env || baseEnv(),
    timeout: 20000,
    windowsHide: true,
  });
  return {
    ok: r.status === 0,
    status: r.status,
    stdout: (r.stdout || '').replace(/\r\n/g, '\n').trim(),
    stderr: (r.stderr || '').replace(/\r\n/g, '\n').trim(),
  };
}

function gitPath(repo, name) {
  const abs = runGit(repo, ['rev-parse', '--path-format=absolute', '--git-path', name]);
  if (abs.ok && abs.stdout) return abs.stdout;
  const rel = runGit(repo, ['rev-parse', '--git-path', name]);
  return rel.ok && rel.stdout ? path.resolve(repo, rel.stdout) : null;
}

function readText(file) {
  try {
    return fs.readFileSync(file, 'utf8').trim();
  } catch {
    return null;
  }
}

function countActiveLines(file) {
  const text = readText(file);
  if (text === null) return null;
  return text.split('\n').filter((line) => line.trim() && !line.trim().startsWith('#')).length;
}

function readRebaseMeta(dir) {
  const get = (name) => readText(path.join(dir, name));
  return {
    dir,
    headName: get('head-name'),
    onto: get('onto'),
    origHead: get('orig-head'),
    stoppedSha: get('stopped-sha'),
    msgnum: get('msgnum') || get('next'),
    end: get('end') || get('last'),
    doneCount: countActiveLines(path.join(dir, 'done')),
    todoCount: countActiveLines(path.join(dir, 'git-rebase-todo')),
  };
}

function probe(repo) {
  const top = runGit(repo, ['rev-parse', '--show-toplevel']);
  if (!top.ok) {
    return { error: `not a git repository: ${top.stderr || repo}` };
  }
  const repoRoot = top.stdout;
  const gitDir = runGit(repoRoot, ['rev-parse', '--absolute-git-dir']).stdout;
  const branch = runGit(repoRoot, ['rev-parse', '--abbrev-ref', 'HEAD']).stdout || '(unknown)';
  const head = runGit(repoRoot, ['rev-parse', '--short', 'HEAD']).stdout || '(unborn)';

  const paths = {};
  for (const name of [
    'rebase-merge',
    'rebase-apply',
    'MERGE_HEAD',
    'CHERRY_PICK_HEAD',
    'REVERT_HEAD',
    'sequencer',
    'index.lock',
  ]) {
    const resolved = gitPath(repoRoot, name);
    paths[name] = { path: resolved, exists: Boolean(resolved && fs.existsSync(resolved)) };
  }

  const unmerged = runGit(repoRoot, ['ls-files', '-u']).stdout;
  const conflicts = [
    ...new Set(
      unmerged
        .split('\n')
        .map((line) => line.split('\t').pop())
        .filter(Boolean)
    ),
  ].sort();

  const operations = [];
  let rebase = null;
  if (paths['rebase-merge'].exists) {
    operations.push('rebase');
    rebase = { kind: 'merge', ...readRebaseMeta(paths['rebase-merge'].path) };
  } else if (paths['rebase-apply'].exists) {
    operations.push('rebase');
    rebase = { kind: 'apply', ...readRebaseMeta(paths['rebase-apply'].path) };
  }
  if (paths['MERGE_HEAD'].exists) operations.push('merge');
  if (paths['CHERRY_PICK_HEAD'].exists) operations.push('cherry-pick');
  if (paths['REVERT_HEAD'].exists) operations.push('revert');
  if (paths['sequencer'].exists && !operations.includes('rebase')) operations.push('sequencer');

  const reflog = runGit(repoRoot, ['reflog', '-8', '--date=iso']).stdout
    .split('\n')
    .filter(Boolean);

  return { repoRoot, gitDir, branch, head, operations, rebase, conflicts, reflog, paths };
}

function classify(repoRoot, target) {
  if (!target) return { input: null, kind: 'none' };

  const abs = path.resolve(target);
  const relRaw = path.relative(repoRoot, abs);
  const outside =
    relRaw === '..' || relRaw.startsWith(`..${path.sep}`) || path.isAbsolute(relRaw);

  if (outside) return { input: target, abs, kind: 'outside-repo' };

  const rel = relRaw.split(path.sep).join('/');
  if (!rel) {
    const trackedAll = runGit(repoRoot, ['ls-files']).stdout;
    return {
      input: target,
      abs,
      rel: '.',
      kind: 'tracked',
      trackedCount: trackedAll ? trackedAll.split('\n').filter(Boolean).length : 0,
    };
  }

  const tracked = runGit(repoRoot, ['ls-files', '--', rel]).stdout;
  const trackedCount = tracked ? tracked.split('\n').filter(Boolean).length : 0;
  if (trackedCount > 0) return { input: target, abs, rel, kind: 'tracked', trackedCount };

  const ignored = runGit(repoRoot, ['check-ignore', '-q', '--', rel]);
  if (ignored.status === 0) return { input: target, abs, rel, kind: 'ignored' };

  return { input: target, abs, rel, kind: 'untracked' };
}

function isSafeTarget(targetInfo) {
  return Boolean(
    targetInfo &&
      (targetInfo.kind === 'outside-repo' ||
        targetInfo.kind === 'untracked' ||
        targetInfo.kind === 'ignored')
  );
}

function decide(probeData, targetInfo, strict) {
  if (probeData.error) {
    return { exitCode: EXIT.ERROR, verdict: 'error', reason: probeData.error };
  }

  const lockExists = probeData.paths['index.lock'] && probeData.paths['index.lock'].exists;
  if (lockExists) {
    if (isSafeTarget(targetInfo)) {
      return {
        exitCode: EXIT.OK,
        verdict: 'safe-target-index-locked',
        reason: 'index.lock exists but target is outside tracked paths',
      };
    }
    return {
      exitCode: EXIT.DEFER,
      verdict: 'index-lock',
      reason: 'index.lock exists; inspect the holder instead of deleting the lock',
    };
  }

  if (probeData.conflicts.length > 0) {
    if (isSafeTarget(targetInfo)) {
      return {
        exitCode: EXIT.OK,
        verdict: 'safe-target-despite-conflict',
        reason: `unmerged paths in repository: ${probeData.conflicts.join(', ')}`,
      };
    }
    return {
      exitCode: EXIT.CONFLICT,
      verdict: 'conflict-readonly',
      reason: 'unmerged paths present; treat repository writes as read-only',
    };
  }

  if (probeData.operations.length > 0) {
    if (!targetInfo || targetInfo.kind === 'none') {
      return {
        exitCode: EXIT.DEFER,
        verdict: 'operation-in-progress',
        reason: `${probeData.operations.join(', ')} in progress`,
      };
    }
    if (isSafeTarget(targetInfo)) {
      return {
        exitCode: EXIT.OK,
        verdict: 'safe-target',
        reason: `target is ${targetInfo.kind} while ${probeData.operations.join(', ')} is in progress`,
      };
    }
    return {
      exitCode: EXIT.DEFER,
      verdict: 'defer-tracked',
      reason: `target is ${targetInfo.kind} while ${probeData.operations.join(', ')} is in progress`,
    };
  }

  if (strict && targetInfo && targetInfo.kind === 'tracked') {
    const dirty = runGit(probeData.repoRoot, ['status', '--porcelain', '--', targetInfo.rel]);
    if (dirty.stdout) {
      return {
        exitCode: EXIT.DEFER,
        verdict: 'strict-dirty-target',
        reason: 'target has uncommitted changes',
      };
    }
  }

  if (strict && !targetInfo) {
    const dirty = runGit(probeData.repoRoot, ['status', '--porcelain']);
    if (dirty.stdout) {
      return {
        exitCode: EXIT.DEFER,
        verdict: 'strict-dirty-worktree',
        reason: 'working tree has changes',
      };
    }
  }

  return {
    exitCode: EXIT.OK,
    verdict: isSafeTarget(targetInfo) ? 'safe-target' : 'clean',
    reason: targetInfo ? `target is ${targetInfo.kind}` : 'no operation in progress',
  };
}

function buildReport(probeData, targetInfo, decision, strict) {
  return {
    repo: probeData.repoRoot,
    gitDir: probeData.gitDir,
    branch: probeData.branch,
    head: probeData.head,
    operations: probeData.operations,
    rebase: probeData.rebase,
    conflicts: probeData.conflicts,
    reflog: probeData.reflog,
    indexLock: Boolean(probeData.paths['index.lock'] && probeData.paths['index.lock'].exists),
    target: targetInfo,
    strict: Boolean(strict),
    verdict: decision.verdict,
    reason: decision.reason,
    exitCode: decision.exitCode,
  };
}

function printHuman(report) {
  const lines = [
    'Shared worktree write guard',
    `repo: ${report.repo}`,
    `branch/head: ${report.branch} @ ${report.head}`,
    `operations: ${report.operations.length ? report.operations.join(', ') : 'none'}`,
  ];

  if (report.rebase) {
    const rb = report.rebase;
    lines.push(
      `rebase: kind=${rb.kind} onto=${rb.onto || '-'} orig-head=${rb.origHead || '-'} ` +
        `progress=${rb.msgnum || '?'}/${rb.end || '?'} stopped=${rb.stoppedSha || '-'} ` +
        `done=${rb.doneCount == null ? '?' : rb.doneCount} todo=${rb.todoCount == null ? '?' : rb.todoCount}`
    );
  }
  lines.push(`conflicts: ${report.conflicts.length ? report.conflicts.join(', ') : 'none'}`);
  lines.push(`index.lock: ${report.indexLock ? 'present' : 'none'}`);

  if (report.target) {
    const target = report.target;
    const count = target.trackedCount == null ? '' : ` (${target.trackedCount} tracked file(s))`;
    lines.push(`target: ${target.abs || target.input} -> ${target.kind}${count}`);
  } else {
    lines.push('target: none');
  }

  lines.push(`verdict: ${report.verdict}`);
  lines.push(`reason: ${report.reason}`);
  lines.push(`exit: ${report.exitCode}`);
  process.stdout.write(`${lines.join('\n')}\n`);
}

function printUsage() {
  process.stdout.write(
    [
      'Usage: node check_rebase_guard.js [options]',
      '',
      'Read-only guard for shared worktrees. Never writes to the repository.',
      '',
      'Options:',
      '  --repo <path>      Repository root (default: current directory)',
      '  --target <path>    Path you intend to write (default: report only)',
      '  --json             Emit machine-readable JSON',
      '  --strict           Also defer when a tracked target/worktree is dirty',
      '  --self-test        Run built-in fixtures and exit',
      '  -h, --help         Show this help',
      '',
      'Exit codes:',
      '  0  safe to write / no operation in progress',
      '  1  defer: an operation is in progress or the target is locked/dirty',
      '  2  conflict: unmerged paths present; repository writes are read-only',
      '  3  usage or git error',
    ].join('\n') + '\n'
  );
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function initRepo(dir, env) {
  fs.mkdirSync(dir, { recursive: true });
  const init = runGit(dir, ['init', '-q'], env);
  assert(init.ok, `git init failed: ${init.stderr}`);
  runGit(dir, ['symbolic-ref', 'HEAD', 'refs/heads/main'], env);
  runGit(dir, ['config', 'user.name', 'Guard Test'], env);
  runGit(dir, ['config', 'user.email', 'guard@example.invalid'], env);
  runGit(dir, ['config', 'commit.gpgsign', 'false'], env);
}

function commitFile(dir, env, name, content, message) {
  fs.writeFileSync(path.join(dir, name), content);
  runGit(dir, ['add', '--', name], env);
  const commit = runGit(dir, ['commit', '-q', '-m', message], env);
  assert(commit.ok, `commit failed: ${commit.stderr}`);
}

function writeSyntheticRebase(repo, partial) {
  const dir = path.join(repo, '.git', 'rebase-merge');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'head-name'), 'refs/heads/main\n');
  if (partial) return;
  fs.writeFileSync(path.join(dir, 'onto'), '1111111111111111111111111111111111111111\n');
  fs.writeFileSync(path.join(dir, 'orig-head'), '2222222222222222222222222222222222222222\n');
  fs.writeFileSync(path.join(dir, 'stopped-sha'), '3333333333333333333333333333333333333333\n');
  fs.writeFileSync(path.join(dir, 'msgnum'), '2\n');
  fs.writeFileSync(path.join(dir, 'end'), '9\n');
  fs.writeFileSync(path.join(dir, 'done'), 'pick abc\npick def\n');
  fs.writeFileSync(path.join(dir, 'git-rebase-todo'), 'pick ghi\npick jkl\n');
}

function makeConflict(repo, env, kind) {
  initRepo(repo, env);
  commitFile(repo, env, 'a.txt', 'base\n', 'base');
  runGit(repo, ['checkout', '-q', '-b', 'feature'], env);
  commitFile(repo, env, 'a.txt', 'feature\n', 'feature');
  runGit(repo, ['checkout', '-q', 'main'], env);
  commitFile(repo, env, 'a.txt', 'main\n', 'main');
  runGit(repo, ['checkout', '-q', 'feature'], env);
  if (kind === 'rebase') {
    const result = runGit(repo, ['rebase', 'main'], env);
    assert(result.status !== 0, 'expected rebase to stop on a conflict');
  } else {
    runGit(repo, ['checkout', '-q', 'main'], env);
    const result = runGit(repo, ['merge', '--no-ff', 'feature', '-m', 'merge feature'], env);
    assert(result.status !== 0, 'expected merge to stop on a conflict');
  }
}

function selfTest() {
  const sandbox = fs.mkdtempSync(path.join(os.tmpdir(), 'rebase-guard-'));
  const env = {
    ...baseEnv(),
    HOME: sandbox,
    USERPROFILE: sandbox,
    GIT_CONFIG_GLOBAL: path.join(sandbox, '.gitconfig-global'),
    GIT_CONFIG_SYSTEM: path.join(sandbox, '.gitconfig-system'),
  };
  const results = [];
  const test = (name, fn) => {
    try {
      results.push({ name, pass: true, detail: fn() });
    } catch (error) {
      results.push({ name, pass: false, detail: error.message });
    }
  };

  try {
    test('clean repo: no operation', () => {
      const repo = path.join(sandbox, 'clean');
      initRepo(repo, env);
      commitFile(repo, env, 'a.txt', 'base\n', 'base');
      const report = probe(repo);
      assert(report.operations.length === 0, `unexpected operations: ${report.operations}`);
      const decision = decide(report, classify(report.repoRoot, path.join(repo, 'new-skill')), false);
      assert(decision.exitCode === 0, `expected 0, got ${decision.exitCode}`);
      return '0 clean';
    });

    test('untracked target under a clean repo is safe', () => {
      const repo = path.join(sandbox, 'untracked-clean');
      initRepo(repo, env);
      commitFile(repo, env, 'a.txt', 'base\n', 'base');
      const report = probe(repo);
      const target = classify(report.repoRoot, path.join(repo, 'new-skill'));
      assert(target.kind === 'untracked', `expected untracked, got ${target.kind}`);
      const decision = decide(report, target, false);
      assert(decision.exitCode === 0 && decision.verdict === 'safe-target', `${decision.exitCode}/${decision.verdict}`);
      return '0 safe-target';
    });

    test('tracked target is clean when no operation runs', () => {
      const repo = path.join(sandbox, 'tracked-clean');
      initRepo(repo, env);
      commitFile(repo, env, 'README.md', 'base\n', 'base');
      const report = probe(repo);
      const target = classify(report.repoRoot, path.join(repo, 'README.md'));
      assert(target.kind === 'tracked', `expected tracked, got ${target.kind}`);
      const decision = decide(report, target, false);
      assert(decision.exitCode === 0 && decision.verdict === 'clean', `${decision.exitCode}/${decision.verdict}`);
      return '0 clean';
    });

    test('tracked target is deferred during rebase', () => {
      const repo = path.join(sandbox, 'tracked-rebase');
      initRepo(repo, env);
      commitFile(repo, env, 'README.md', 'base\n', 'base');
      writeSyntheticRebase(repo, false);
      const report = probe(repo);
      assert(report.operations.includes('rebase'), 'expected rebase operation');
      const target = classify(report.repoRoot, path.join(repo, 'README.md'));
      const decision = decide(report, target, false);
      assert(decision.exitCode === 1 && decision.verdict === 'defer-tracked', `${decision.exitCode}/${decision.verdict}`);
      return '1 defer-tracked';
    });

    test('untracked target stays safe during rebase', () => {
      const repo = path.join(sandbox, 'untracked-rebase');
      initRepo(repo, env);
      commitFile(repo, env, 'README.md', 'base\n', 'base');
      writeSyntheticRebase(repo, false);
      const report = probe(repo);
      const target = classify(report.repoRoot, path.join(repo, 'new-skill'));
      const decision = decide(report, target, false);
      assert(decision.exitCode === 0 && decision.verdict === 'safe-target', `${decision.exitCode}/${decision.verdict}`);
      return '0 safe-target';
    });

    test('rebase metadata is parsed', () => {
      const repo = path.join(sandbox, 'metadata');
      initRepo(repo, env);
      commitFile(repo, env, 'a.txt', 'base\n', 'base');
      writeSyntheticRebase(repo, false);
      const report = probe(repo);
      const rb = report.rebase;
      assert(rb && rb.kind === 'merge', 'expected rebase-merge');
      assert(rb.onto === '1111111111111111111111111111111111111111', `onto=${rb.onto}`);
      assert(rb.origHead === '2222222222222222222222222222222222222222', `orig-head=${rb.origHead}`);
      assert(rb.stoppedSha === '3333333333333333333333333333333333333333', `stopped-sha=${rb.stoppedSha}`);
      assert(rb.msgnum === '2' && rb.end === '9', `progress=${rb.msgnum}/${rb.end}`);
      assert(rb.doneCount === 2 && rb.todoCount === 2, `done=${rb.doneCount} todo=${rb.todoCount}`);
      return 'metadata parsed';
    });

    test('partial rebase directory does not crash', () => {
      const repo = path.join(sandbox, 'partial');
      initRepo(repo, env);
      commitFile(repo, env, 'README.md', 'base\n', 'base');
      writeSyntheticRebase(repo, true);
      const report = probe(repo);
      assert(report.rebase && report.rebase.kind === 'merge', 'expected rebase-merge');
      const target = classify(report.repoRoot, path.join(repo, 'README.md'));
      const decision = decide(report, target, false);
      assert(decision.exitCode === 1, `expected 1, got ${decision.exitCode}`);
      return '1 partial metadata tolerated';
    });

    test('real rebase conflict is read-only', () => {
      const repo = path.join(sandbox, 'real-rebase');
      makeConflict(repo, env, 'rebase');
      const report = probe(repo);
      assert(report.operations.includes('rebase'), `operations=${report.operations}`);
      assert(report.conflicts.includes('a.txt'), `conflicts=${report.conflicts}`);
      const target = classify(report.repoRoot, path.join(repo, 'a.txt'));
      const decision = decide(report, target, false);
      assert(decision.exitCode === 2 && decision.verdict === 'conflict-readonly', `${decision.exitCode}/${decision.verdict}`);
      return '2 conflict-readonly';
    });

    test('real merge conflict is read-only', () => {
      const repo = path.join(sandbox, 'real-merge');
      makeConflict(repo, env, 'merge');
      const report = probe(repo);
      assert(report.operations.includes('merge'), `operations=${report.operations}`);
      assert(report.conflicts.includes('a.txt'), `conflicts=${report.conflicts}`);
      const decision = decide(report, null, false);
      assert(decision.exitCode === 2 && decision.verdict === 'conflict-readonly', `${decision.exitCode}/${decision.verdict}`);
      return '2 conflict-readonly';
    });

    test('outside target is safe during rebase', () => {
      const repo = path.join(sandbox, 'outside');
      initRepo(repo, env);
      commitFile(repo, env, 'a.txt', 'base\n', 'base');
      writeSyntheticRebase(repo, false);
      const report = probe(repo);
      const target = classify(report.repoRoot, path.join(sandbox, 'outside-skill'));
      assert(target.kind === 'outside-repo', `expected outside-repo, got ${target.kind}`);
      const decision = decide(report, target, false);
      assert(decision.exitCode === 0, `expected 0, got ${decision.exitCode}`);
      return '0 outside-repo';
    });

    test('strict mode defers a dirty tracked target', () => {
      const repo = path.join(sandbox, 'strict');
      initRepo(repo, env);
      commitFile(repo, env, 'README.md', 'base\n', 'base');
      fs.writeFileSync(path.join(repo, 'README.md'), 'dirty\n');
      const report = probe(repo);
      const target = classify(report.repoRoot, path.join(repo, 'README.md'));
      const decision = decide(report, target, true);
      assert(decision.exitCode === 1 && decision.verdict === 'strict-dirty-target', `${decision.exitCode}/${decision.verdict}`);
      return '1 strict-dirty-target';
    });

    test('ignored target stays safe during rebase', () => {
      const repo = path.join(sandbox, 'ignored');
      initRepo(repo, env);
      fs.writeFileSync(path.join(repo, '.gitignore'), 'build/\n');
      commitFile(repo, env, '.gitignore', 'build/\n', 'ignore build');
      writeSyntheticRebase(repo, false);
      const report = probe(repo);
      const target = classify(report.repoRoot, path.join(repo, 'build', 'artifact.txt'));
      assert(target.kind === 'ignored', `expected ignored, got ${target.kind}`);
      const decision = decide(report, target, false);
      assert(decision.exitCode === 0, `expected 0, got ${decision.exitCode}`);
      return '0 ignored';
    });
  } finally {
    try {
      fs.rmSync(sandbox, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
    } catch {
      // Cleanup is best-effort; the fixtures live under the OS temp directory.
    }
  }

  for (const result of results) {
    process.stdout.write(`[${result.pass ? 'PASS' : 'FAIL'}] ${result.name}${result.pass ? '' : `: ${result.detail}`}\n`);
  }
  const passed = results.filter((result) => result.pass).length;
  process.stdout.write(`\n${passed}/${results.length} PASS\n`);
  return passed === results.length;
}

function parseArgs(argv) {
  const options = {
    repo: process.cwd(),
    target: null,
    json: false,
    strict: false,
    selfTest: false,
    help: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--self-test') options.selfTest = true;
    else if (arg === '--json') options.json = true;
    else if (arg === '--strict') options.strict = true;
    else if (arg === '-h' || arg === '--help') options.help = true;
    else if (arg === '--repo') {
      options.repo = argv[index + 1];
      if (!options.repo) return { error: '--repo requires a value' };
      index += 1;
    } else if (arg.startsWith('--repo=')) {
      options.repo = arg.slice('--repo='.length);
    } else if (arg === '--target') {
      options.target = argv[index + 1];
      if (!options.target) return { error: '--target requires a value' };
      index += 1;
    } else if (arg.startsWith('--target=')) {
      options.target = arg.slice('--target='.length);
    } else {
      return { error: `unknown argument: ${arg}` };
    }
  }

  return options;
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.error) {
    process.stderr.write(`ERROR: ${options.error}\n`);
    printUsage();
    process.exit(EXIT.ERROR);
  }
  if (options.help) {
    printUsage();
    process.exit(EXIT.OK);
  }
  if (options.selfTest) {
    process.exit(selfTest() ? EXIT.OK : EXIT.DEFER);
  }

  const repo = path.resolve(options.repo);
  const probeData = probe(repo);
  if (probeData.error) {
    process.stderr.write(`ERROR: ${probeData.error}\n`);
    process.exit(EXIT.ERROR);
  }

  const targetInfo = classify(probeData.repoRoot, options.target ? path.resolve(options.target) : null);
  const decision = decide(probeData, targetInfo, options.strict);
  const report = buildReport(probeData, targetInfo, decision, options.strict);

  if (options.json) {
    process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
  } else {
    printHuman(report);
  }

  process.exit(decision.exitCode);
}

main();
