# Case: xuanspace A1 license consistency fix

Date: 2026-10-23

Target: `projects/xuanspace` (a git submodule of SpecWeave)

Outcome: 8 files changed; submodule commit `185c3e0`; parent gitlink commit `36bb9ed51`.

## Initial hypothesis, and why it was too narrow

The audit reported A1 as a single conflict: `LICENSE` was Apache-2.0, `pyproject.toml:30` used an Apache classifier, but `README.md:173` said "MIT License". The natural reading was "one stale README line".

That reading missed two things:

1. The same stale MIT declaration existed in other first-party files, including a README that the initial file list did not mention.
2. The Python and native project templates still emitted MIT, so every newly scaffolded project would reintroduce the conflict.

The corrected scope was eight files.

## Truth-source evidence

The license file's history was decisive:

```text
5f65391 chore(license): 项目许可证从MIT更新为Apache License 2.0，
        同步更新pyproject.toml中的license字段和classifiers
bb9ecce feat: 初始化 Xuanspace（玄境）Python monorepo 项目
```

`5f65391` is an intentional license change. The README license line had not changed since the initial import (`bb9ecce`), so the README was stale residue, not an alternative decision.

The root metadata agreed with the LICENSE:

```text
LICENSE                         Apache License, Version 2.0
pyproject.toml:10               license = {file = "LICENSE"}
pyproject.toml:30               License :: OSI Approved :: Apache Software License
```

## The eight files

| File | Before | After |
|---|---|---|
| `README.md:173` | "MIT License" | Apache License 2.0 |
| `tools/xs/README.md:63` | "MIT License" | Apache License 2.0 |
| `tools/xs/pyproject.toml:30` | `{text = "MIT"}` | `"Apache-2.0"` + license classifier |
| `tools/okf/pyproject.toml:26` | `{text = "MIT"}` | `"Apache-2.0"` + license classifier |
| `libs/xuan-core/pyproject.toml:14` | `{text = "MIT"}` | `"Apache-2.0"` + license classifier |
| `libs/xuan-ext-demo/pyproject.toml:14` | `{text = "MIT"}` | `"Apache-2.0"` + license classifier |
| `tools/templates/python/pyproject.toml:10,18` | MIT license + MIT classifier | Apache-2.0 license + Apache classifier |
| `tools/templates/native/pyproject.toml:10,18` | MIT license + MIT classifier | Apache-2.0 license + Apache classifier |

`tools/xs/README.md` was the file the initial assessment missed. The two template files are the reproduction sources: fixing only the generated projects would have left the drift intact.

The SPDX string form was chosen over `{text = "..."}` because the table form is deprecated under PEP 639. Classifiers were added where they were missing so the metadata had two consistent surfaces.

## Intentional exception

`libs/xuan-compose` declares `GPL-2.0-only`, its LICENSE is the GNU GPL, and commit `7edfda0` says:

```text
feat(compose): 新增 xuan-compose 包脚手架，确立 GPL-2.0 对等重构基线
```

This is an intentional copyleft choice, not a missed MIT update. It was preserved. Flipping it to Apache would have changed a licensing decision, which is outside the scope of a consistency fix.

Other checks that did not require edits:

- `libs/caffe-ffi`, `libs/demo-ffi`, and `libs/npu-ffi` LICENSE headers were already Apache.
- `tools/templates/native-ffi` references a `LICENSE` file and its README states Apache; it was outside this A1 change.

## Verification performed

- All 13 `pyproject.toml` files in the verification scope parsed with `tomllib`.
- A first-party residual scan for `MIT` and `license = {text` returned zero hits.
- The bundled verifier's default scan covered 10 first-party `pyproject.toml` files and reported one advisory warning: `tools/templates/native-ffi/pyproject.toml` references a `LICENSE` file that is not present in the template. That template is outside A1; the warning is recorded, not auto-fixed.
- Running the verifier with `--include-submodules` covered 20 files and surfaced two pre-existing BSD-2-Clause/BSD-3-Clause conflicts under `vendor/caffe/`. Those are third-party submodules and were deliberately not touched. This is why the default scope skips nested repositories.
- Three-way check: root `pyproject.toml` license file, root Apache classifier, and root `LICENSE` text agreed; the root README now agreed as well.
- `git diff --stat` showed 8 files, +20/-10.
- Submodule commit `185c3e0` contained all eight files.
- Parent commit `36bb9ed51` updated only the xuanspace gitlink.
- `git ls-tree HEAD projects/xuanspace` showed `185c3e04...`, matching the submodule HEAD.
- The parent repository's eight pre-commit hooks passed.

## Failures and near-misses

- **Scope underestimation.** The audit line item looked like one file; the actual scope was eight. The full scan, not the report, defined the scope.
- **False positive from a build artifact.** `doc/_build/html/_static/scripts/fontawesome.js.LICENSE.txt` contains an MIT notice for a bundled dependency. It is not the project's license and must not drive the fix.
- **Inline Python path escaping failed.** A one-liner containing `p = f.replace('\\','/')` inside a single-quoted shell string produced `SyntaxError: unterminated string literal`. The verification should use a script or a here-doc.
- **Stale `index.lock`.** The lock was 0 bytes and about 2.9 days old. Running git processes were the agent's current read-only status/diff calls, not the lock owner. The lock was renamed to `index.lock.stale-20261020` (not deleted), the commit was retried, and the backup was removed after success.
- **Commit authorization was separate.** The user first asked to fix A1, then explicitly chose "全部统一为 Apache-2.0", and only later said "提交吧". Fixing and committing were two decisions.

## What the skill should have done

| Case step | Skill rule |
|---|---|
| README looked like the only conflict | Scan every declaration before choosing scope |
| `5f65391` proved the LICENSE was intentional | Establish truth source with `git log --follow` |
| `README.md` had not changed since `bb9ecce` | A stale reference is not an alternative decision |
| Templates still emitted MIT | Fix reproduction sources, not only outputs |
| `xuan-compose` was intentionally GPL | Policy gate; preserve intentional exceptions |
| Fontawesome notice looked like MIT | Exclude build artifacts and inspect the exclusion |
| Inline Python failed on Windows quoting | Use a script or here-doc for verification |
| `index.lock` blocked staging | Inspect processes and age; rename, do not delete |
| Submodule content needed a parent pointer update | Two-level commit; verify the gitlink |
