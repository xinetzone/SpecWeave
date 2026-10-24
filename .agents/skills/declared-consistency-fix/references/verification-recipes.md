# Verification recipes

Use these as starting points. Replace `<repo>`, `<file>`, and `<value>` with the actual paths and strings. Prefer a script or here-doc over long inline Python on Windows shells.

## 1. Find every declaration

```bash
rg -n -i --hidden \
  -g '!.git/**' -g '!**/build/**' -g '!**/dist/**' -g '!**/node_modules/**' \
  -e 'MIT License' -e 'Apache License' -e 'GPL' \
  -e 'license\s*=' -e 'License ::'
```

For a literal string, add `-F` so regex metacharacters do not change the match.

Inventory the hits before editing:

- first-party README and package manifests
- templates, scaffolds, init commands, and generator code
- CI defaults and release scripts
- generated metadata mirrors
- vendored or third-party notices

Inspect every excluded directory at least once. Record why each exclusion is safe.

## 2. License truth source

Read the canonical text:

```bash
head -20 LICENSE
head -20 COPYING 2>/dev/null
```

Find when the license changed and whether the change was intentional:

```bash
git log --follow --format='%h %ad %s' --date=short -- LICENSE
git log -S 'MIT License' --oneline --all -- .
git show <sha> --stat
git show <sha> -- LICENSE
```

Parse every Python project's metadata:

```bash
python - <<'PY'
import pathlib
import tomllib

skip = {'.git', 'build', 'dist', 'node_modules', '.venv', 'venv', '_build'}
for path in sorted(pathlib.Path('.').rglob('pyproject.toml')):
    if any(part in skip for part in path.parts):
        continue
    data = tomllib.loads(path.read_text(encoding='utf-8'))
    project = data.get('project', {})
    classifiers = [c for c in project.get('classifiers', []) if c.startswith('License ::')]
    print(f"{path}: license={project.get('license')!r} classifiers={classifiers}")
PY
```

Run the bundled verifier for a compact conflict report:

```bash
python scripts/check_license_consistency.py <repo>
python scripts/check_license_consistency.py <repo> --strict
python scripts/check_license_consistency.py <repo> --json
```

The verifier is read-only. Conflicts exit 1; with `--strict`, warnings also exit 1.

By default it skips nested repositories and submodules, so it reports first-party declarations only. Pass `--include-submodules` when you intentionally want to audit vendored or nested repositories; expect third-party inconsistencies there and do not "fix" them as part of a first-party change.

## 3. Version truth source

```bash
git tag --sort=-v:refname | head -20
git submodule status
rg -n -F '<version>' --hidden \
  -g '!.git/**' -g '!**/build/**' -g '!**/dist/**'
```

Compare four surfaces:

1. release tag or submodule pointer
2. package metadata (`pyproject.toml`, `package.json`, `Cargo.toml`, etc.)
3. human docs or README tables
4. changelog or release notes

The tag or submodule pointer is usually the truth. A docs table is a derived surface. If the version is hand-maintained in several places, consider deriving it or deleting the duplicate column.

## 4. Path truth source

```bash
test -d doc && echo 'doc exists'
test -d docs && echo 'docs exists'
rg -n -F 'docs/' --hidden -g '!.git/**'
rg -n -F 'doc/' --hidden -g '!.git/**'
git log --follow --diff-filter=R --summary -- <path>
```

The filesystem is the current truth. The rename commit tells you whether the move was intentional. Update every reference, including routing tables, toctrees, build configs, CI paths, and scripts.

## 5. Classification and build metadata

```bash
rg -n -e 'build-backend' -e 'requires-python' -e 'wheel.packages' \
  -e 'build-dir' -e 'classifiers' -g 'pyproject.toml'
```

Compare the root project, subpackages, and templates. A template that emits a different build backend or Python floor is a reproduction source for future drift.

## 6. Residual scan discipline

```bash
rg -n -F '<old value>' --hidden \
  -g '!.git/**' -g '!**/build/**' -g '!**/dist/**' \
  -g '!**/node_modules/**' -g '!**/_build/**'
```

Before declaring success:

- print the number of files scanned
- list the exclusions and why they are safe
- inspect any hit that looks like a third-party notice
- confirm the scan would have caught the original conflict

A zero-hit scan with an over-broad exclusion is not evidence.

## 7. Submodule two-level commit

```bash
git -C <submodule> status --short
git -C <submodule> add <explicit paths>
git -C <submodule> commit -F <utf8-message-file>
git add <submodule-path>
git commit -F <utf8-message-file>
git ls-tree HEAD <submodule-path>
```

The final command must show the submodule's new HEAD. Do not stage unrelated files in either repository.

If `index.lock` blocks staging:

```bash
ls -l .git/modules/<path>/index.lock
ps -ef | grep '[g]it'
```

On Windows, inspect the command lines and start times of running git processes. If no process owns the lock and there is no merge/rebase state, rename the lock instead of deleting it:

```bash
mv .git/modules/<path>/index.lock .git/modules/<path>/index.lock.stale-<date>
```

Retry the commit, then remove the backup after success.

## 8. Encoding and commit message

Write the message to a UTF-8 file, then verify it:

```bash
python - <<'PY'
text = open('msg.txt', encoding='utf-8').read()
print(text)
PY
git commit -F msg.txt
```

On Windows, avoid passing multi-line Chinese commit messages directly through a shell variable.
