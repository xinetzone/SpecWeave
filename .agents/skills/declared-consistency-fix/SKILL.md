---
name: declared-consistency-fix
version: 1.0.0
description: "修复跨文件「声明不一致」（许可证、版本号、路径、分类、依赖下限、构建元数据等）：先用 git log --follow / git log -S 判断哪一侧是有意决策的真源，再全仓扫描同类声明及模板/生成器等再生产源，统一修正后做机械验证。当用户说『统一口径』『修正许可证声明』『README 与 LICENSE 不一致』『版本号对不上』『路径引用失效』『声明漂移』『修完又漂回去』，或发现同一事实在多处互相矛盾并准备修改时，必须使用本技能；涉及许可/合规等策略性口径先向用户确认方向；不用于只读核验（有 artifact-consistency-audit 时优先用它）。"
argument-hint: "<仓库根或冲突文件路径> [声明类型]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/declared-consistency-fix/**"
title: "声明一致性修复 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/declared-consistency-fix/SKILL.toml"
---

# 声明一致性修复 Skill (Declared Consistency Fix)

## 1. Why

A fact repeated in several files is not one fact. It is one fact plus N chances to drift. Fixing the visible copy while leaving its source of reproduction — a template, scaffold, generator, CI default, or metadata mirror — guarantees the old value returns on the next generation.

Before choosing which copy is "right", establish which side was an intentional decision and which side is stale residue. The newest file is not automatically the truth; a generated file can be the newest and still wrong.

> **为什么先判真源再改？** 文件新旧与修改次数都不能证明意图；只有提交信息与变更历史能区分「有意决策」与「陈旧残留」。判错方向时，修得越彻底，偏离越远。

## 2. Scope

Use this skill when the same declaration disagrees across artifacts:

- a license appears differently in `LICENSE`, README, `pyproject.toml`, package manifests, or subpackages
- a version disagrees across tags, submodule pointers, package metadata, docs, or changelog
- path references point at a directory that was renamed (`docs/` vs `doc/`)
- project classification or build metadata disagrees across configs and templates
- a template or scaffold keeps regenerating a value that was just corrected
- the user says "统一口径", "修正声明", "为什么改完又变回去", "README 和 LICENSE 对不上"

Do not use this skill for:

- read-only verification of a derived artifact against its source; use `artifact-consistency-audit` when available
- a single-file typo with no repeated declaration
- deciding what a license should be; this skill structures the decision, it does not make it
- committing unrelated work; this skill carries submodule-specific commit rules, not a general commit workflow

## 3. Core model

| Concept | Definition | Question to answer |
|---|---|---|
| Declaration | A fact repeated in a file | Where does this fact appear? |
| Truth source | The side backed by an intentional decision | Which commit established the intended value, and why? |
| Reproduction source | Template, generator, CI default, or metadata mirror that creates new declarations | What will reintroduce the old value? |
| Policy boundary | A choice the user must make: license, compliance, security, intentional exception | Am I allowed to change this direction? |

The four concepts are independent. A file can be the truth source and still not be the reproduction source. A template can be neither the truth nor the current output, yet be the reason the inconsistency keeps returning.

> **为什么把再生产源单独建模？** 只修当前输出，模板会在下一次生成时把旧值带回来；只有同时修输出与生产源，修复才具备可持续性。这是「修完又漂回去」的唯一根因。

## 4. Workflow

### 0. Preflight

Read the working tree before touching anything:

```bash
git status --short
git rev-parse --show-toplevel
git rev-parse --show-superproject-working-tree 2>/dev/null || true
```

Record unrelated modified or untracked files. Do not stash, reset, clean, or commit them. If the user only asked to inspect, stop after reporting; inspection and repair are separate authorizations.

Identify whether the target is inside a submodule. A submodule commit and its parent gitlink are two commits, not one.

### 1. Establish the truth source

Run git archaeology on every conflicting side:

```bash
git log --follow --format='%h %ad %s' --date=short -- <file>
git log -S '<exact value>' --oneline --all -- <path>
git log --all --oneline -- <file>
git show --stat <sha>
git show <sha> -- <file>
```

Read the commit message and body, not just the diff. `git log -S` finds when a string was added or removed; `git log -G` finds regex changes. `git log --follow` follows one path at a time and tracks renames.

Use this decision table:

| Evidence | Conclusion |
|---|---|
| A later commit explicitly changes the canonical artifact and says why | The canonical artifact is the truth; references are stale |
| A reference has not changed since initial import while the canonical artifact changed | The reference is stale |
| A subpackage has an independent license with an explicit decision commit | Intentional exception; preserve it |
| Only a generated output is newer | The generator/template is the truth, not the output |
| Both sides have plausible intent, or neither has intent evidence | Stop and ask; do not guess |

For licenses, the canonical artifact is usually the `LICENSE` file plus the root project metadata, not a README sentence. For versions, check tags, submodule pointers, and package metadata before trusting a docs table. For paths, the filesystem is the current truth, but check whether the move was intentional.

### 2. Expand the scan

Search for every occurrence of the declaration, not just the reported one:

```bash
rg -n -F --hidden \
  -g '!.git/**' -g '!**/build/**' -g '!**/dist/**' -g '!**/node_modules/**' \
  '<value or keyword>'
```

Then inventory the hits by class:

- first-party deliverables: READMEs, package manifests, docs
- reproduction sources: templates, scaffolds, generator code, init commands, CI defaults
- metadata mirrors: generated TOML/JSON, docs front matter
- vendored or third-party notices: exclude from the fix, but record why

Explicitly inspect the directories you exclude at least once. A build artifact can contain a real-looking license notice that is not your project's declaration. An over-broad exclusion is worse than no scan because it produces false confidence.

### 3. Pass the policy gate

Ask the user before changing:

- a license, copyright, export-control, or compliance position
- an intentional exception such as copyleft, dual licensing, or vendored code
- a value where both sides have plausible intent

Present the evidence compactly:

| File | Current value | Truth evidence | Proposed value | Keep? |
|---|---|---|---|---|

Then wait. A user's earlier "fix it" does not authorize flipping a deliberate license choice. A subpackage that is intentionally GPL is not a missed update.

> **为什么策略门不能由 Agent 自行决定？** 许可证方向、合规口径与有意例外属于用户的决策权，不是技术一致性问题。Agent 的职责是摊开证据与影响，而不是替用户选择方向。

### 4. Fix all declarations, including reproduction sources

Before applying edits, show the proposed diff and wait for confirmation — the diff is this skill's dry-run preview. The bundled license checker is read-only, so running it first is safe.

- Update every inconsistent first-party declaration.
- Update the template, scaffold, generator, CI default, or metadata mirror that produces the declaration.
- Preserve intentional exceptions and record the reason in the final report.
- Prefer the repository's canonical metadata form. In Python projects that support PEP 639, an SPDX string such as `license = "Apache-2.0"` is preferable to the deprecated `license = {text = "MIT"}` form.
- Keep license classifiers synchronized with the declared license.
- Do not touch dependencies or unrelated fields.

If the root canonical artifact is correct and a subpackage is intentionally different, the correct output is "root unified, subpackage preserved", not "all files identical".

### 5. Verify mechanically

- Parse every changed config file. For Python, use `tomllib`.
- Re-scan for the old value in the first-party scope. Print how many files were scanned.
- Compare the canonical artifact, machine metadata, and human-facing docs in three directions.
- For licenses, run the bundled verifier:

```bash
python scripts/check_license_consistency.py <repo-root>
```

- Run `git diff --stat` and `git status --short`; confirm the diff matches the intended scope.
- Treat zero hits from an over-broad exclusion as no evidence. If the expected file count is lower than expected, inspect the exclusions before declaring success.

### 6. Commit only when authorized

Modification and commit are separate authorizations.

For a submodule:

```bash
git -C <submodule> status --short
git -C <submodule> add <explicit paths>
git -C <submodule> commit -F <utf8-message-file>
git add <submodule-path>
git commit -F <utf8-message-file>
git ls-tree HEAD <submodule-path>
```

The last command must show the submodule's new HEAD. Stage explicit paths, never `git add -A`. Leave unrelated dirty files untouched.

If `index.lock` exists, inspect running git processes and the lock's age before acting. If it is stale, rename it to `index.lock.stale-<date>` rather than deleting it, retry, and remove the backup only after a successful commit.

On Windows, pass the commit message through a UTF-8 file or stdin; verify the encoding before committing. Do not push unless asked.

### 7. Prevent recurrence

If a template or generator caused the drift, the fix is not complete until that source is fixed. If the repository has a CI gate, suggest adding a consistency check; do not silently rewrite the pipeline. If you add a check, seed it with a known violation to prove it can fail.

## 5. 安全检查清单（逐项确认）

- [ ] 写操作前已展示 diff 预览（dry-run 等价物）并获得明确确认
- [ ] 重复执行只读扫描/校验是幂等的（结果一致，不产生新改动）
- [ ] Every conflicting declaration is enumerated, including templates and generators
- [ ] Truth source is backed by a commit SHA and message, not by file recency
- [ ] Policy decision is confirmed for licenses, compliance, and intentional exceptions
- [ ] All changed configs parse
- [ ] Residual scan reports zero first-party hits and states the scan scope
- [ ] Canonical artifact, machine metadata, and human docs agree
- [ ] `git diff --stat` matches the intended scope
- [ ] Submodule commit and parent gitlink agree, if applicable
- [ ] Unrelated dirty files are untouched
- [ ] Commit happened only after explicit authorization

## 6. Gotchas（陷阱与反直觉行为）

1. **The audit report's scope is a hypothesis.** In the source case, "README one line" became eight files after `git log -S` and a full scan.
2. **Templates are production sources.** A template that still emits MIT will reintroduce MIT after the next scaffold, no matter how many outputs you fix.
3. **Newest is not truth.** Generated files can be newest and still wrong; find the generator.
4. **Intentional exceptions look like bugs.** A copyleft subpackage with a decision commit is not a missed update.
5. **Build artifacts and vendored notices create false positives.** A minified dependency's license notice is not your project's license.
6. **An over-excluding scan is worse than no scan.** Print the scanned file count and inspect what you excluded.
7. **Editing the parent repo alone does not change submodule content.** Commit inside the submodule first, then update the gitlink.
8. **Do not delete `index.lock` blindly.** Inspect processes and age; rename a stale lock.
9. **License metadata has two surfaces.** Fix both the `license` field and the `License ::` classifiers.
10. **README can mention a license in badges, tables, footers, and dependency notices.** Check every occurrence, not just the license section.
11. **Windows shell quoting breaks inline Python one-liners.** A path expression such as `replace('\\','/')` inside a single-quoted shell string can end in a `SyntaxError`; use a script or a here-doc.
12. **`git log --follow` follows one path.** Run it per file; do not assume one call covers a directory.

## 7. References

- `references/case-xuanspace-license.md` — the real case: scope expansion, truth-source evidence, eight files, the GPL exception, and the two-level commit
- `references/verification-recipes.md` — command recipes for license, version, path, and classification declarations
- `scripts/check_license_consistency.py` — read-only verifier for Python license declarations

## 8. Changelog

- 2026-10-23: Initial version, distilled from the xuanspace A1 license consistency fix.
- 2026-10-23: Migrated from user-level `~/.qoder/skills` into SpecWeave `.agents/skills`; added SpecWeave frontmatter fields, Why blocks, and the diff-preview safety gate.
