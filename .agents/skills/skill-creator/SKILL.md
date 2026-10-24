---
source: "镜像自 Trae IDE builtin（整合 trae scope 默认版正文与用户级全量技能包资源）"
name: skill-creator
description: Create or update project or global skills, install skills globally, or measure skill performance with evals and benchmarks. Use when asked to create, edit, explain, or install a skill from GitHub, marketplace, or local folder, or to run evals, benchmark skill quality, or optimize a skill's description for better triggering accuracy. Not a callable tool.
---

# Skill Creator

Create or update project or global skills, or **install** existing skills into the current product's user-level global skills directory. A skill is a directory of instructions for the agent — not a tool, not an API. Do not call a tool named `skill-creator`. This file is already the procedure.

If the user asks to install, install. Do not only print the destination path.

## Decide first

Pick one path from the current user message. Do not ask whether the user is internal or external. Do not ask questions whose answers are already present.

Decide **action** first, then **scope**.

### Action — write vs install

| Situation | Action |
|-----------|--------|
| User is authoring instructions for how this repo should work | Create (project), or Update only when explicitly requested |
| User explicitly asks to update or edit an existing skill | Update — resolve the exact target using the Update rules, then read its `SKILL.md` |
| User only asks what a skill looks like / how format works | Explain — do not create a directory |
| User explicitly asks to install or add an existing skill from a GitHub/marketplace URL, package name, or local skill folder. A source reference alone is not install intent | **Install** into the current product's user-level global skills directory. Finish only when the files exist there |
| User is creating a new skill and explicitly asks for it to be global, user-level, or available across all projects | Create in the current product's user-level global skills directory |
| Task is generic model knowledge or a one-off with no reusable procedure | Refuse — say why, do not create or install |

### Scope — project vs global

| Signal | Scope |
|--------|--------|
| Skill is about this repo's APIs, layout, review checklist, deploy flow, or team conventions | **Project** — `<workspaceFolder>/.trae/skills/<skill-folder>/` |
| Action is Install | **Global** — current product's user-level global skills directory. Use Project only when the user explicitly asks to pin the installed skill in the repository |
| User explicitly asks for the skill to be global, user-level, or available across all projects | **Global** — current product's user-level global skills directory |
| Scope is ambiguous, but a project workspace exists and the user refers to the current repository or project | Default to **Project**. This selects project scope, not a specific folder in a multi-root workspace |
| Scope is ambiguous and no project workspace is available | Ask for a project path or explicit global scope; do not write yet |

Ask only for missing pieces (name, purpose, trigger phrases, install source, or an unresolved target workspace). One short question, then proceed.

## Location

Project and global roots are different. `dataFolderName` is a product setting, not a project setting.

| Kind | Path |
|------|------|
| **Project** | `<workspaceFolder>/.trae/skills/<skill-folder>/SKILL.md` |
| **Global** | `<userHome>/<dataFolderName>/skills/<skill-folder>/SKILL.md` |

Resolve `<workspaceFolder>` before writing a project skill:

1. Use an explicit project path from the user.
2. Otherwise, use the workspace folder that contains files referenced by the request.
3. Otherwise, use the only workspace folder when exactly one is open.
4. If multiple workspace folders are open, do not treat the primary working directory, default cwd, workspace ordering, or directory names as the user's selection. Use a folder only when the user explicitly identifies it or references files unique to it. Otherwise, ask which workspace to use before writing anything. Do not use their parent or container directory as the project root.

Resolve `dataFolderName` from the current session context before choosing a global path:

1. Prefer explicit runtime product metadata or a runtime-provided `dataFolderName`.
2. Otherwise, use the active product's built-in or system path as supporting evidence. Do not use arbitrary third-party skill paths.
3. Do not infer the product from directory existence alone; both product directories may exist on the same machine.
4. If the session signals are missing or conflict, ask one short question before writing to a global path.

Then use the matching product path — do not mix editions:

- CN (IDE CN + Work CN) — `.trae-cn` → `~/.trae-cn/skills/<skill-folder>/`
- International (IDE International + Work International) — `.trae` → `~/.trae/skills/<skill-folder>/`

If the session is CN, install and write global skills to the CN path. If the session is International, use the International path. Never install a CN session's skill into `~/.trae/skills/`, and never install an International session's skill into `~/.trae-cn/skills/`.

Project skills are **always** `<workspaceFolder>/.trae/skills/`, including on CN — never `<workspaceFolder>/.trae-cn/skills/`.

Skill directory layout (same at either root):

```text
<skill-folder>/
├── SKILL.md           # required
├── scripts/           # optional — deterministic or repeatedly rewritten code
├── references/        # optional — long docs loaded on demand
└── assets/            # optional — templates, images, boilerplate
```

Rules:

- `name` in frontmatter must equal the directory name `<skill-folder>`.
- If the target directory already exists, update it only when the user explicitly requested an update. Replace or overwrite it only after explicit user confirmation. Otherwise, stop and report the existing path. Do not create a second copy under another name.
- Do not vendor a downloaded third-party skill into the project tree unless the user explicitly wants it pinned in this repo.

## Frontmatter

`SKILL.md` starts with YAML frontmatter, then markdown body. No other required files.
The authoring rules in this section apply to Create and Update. For Install, require only parseable frontmatter with a valid `name` and a present `description`; preserve other loadable forms unchanged.

```yaml
---
name: kebab-case-name
description: What the skill does and when to use it. Include trigger words and do-not cases.
---
```

`name`:

- Lowercase `a-z`, digits `0-9`, single hyphens only
- 2–64 characters, no consecutive `--`, must start and end with a letter or digit
- Must match the parent directory name
- Do not quote it

`description` (this is the only trigger text the router sees):

- One line, plain YAML scalar — no `"..."` or `'...'`
- Must include what it does and when to invoke it
- Put trigger phrases here, not in the body
- Default language is English unless the user requires another language
- Target under 200 characters when possible; never pad with MUST/MANDATORY
- Do not use `: ` (colon-space) — it forces quoting. Reword with em dash or "including"
- Do not use `<` or `>`
- Prefer this shape: `Does X. Use when the user asks for Y or Z. Do not use for W.`

## Body

Write imperative instructions. Only include what the model does not already know.
These are Create and Update authoring guidelines. Do not use them to rewrite an existing third-party skill during Install.

- Keep `SKILL.md` well under 500 lines. Move long material to `references/` and link it from the body (one level deep, no nested references).
- Do not repeat the description. Body assumes the skill already triggered.
- Do not add `README.md`, `CHANGELOG.md`, or human-facing project files.
- Point to `scripts/` for commands that must be exact; point to `assets/` for files that should be copied rather than loaded into context.

## Create

1. Confirm the action is write. Choose project vs global from the scope table.
2. Normalize the skill name to kebab-case and confirm it is valid.
3. Resolve the destination root using the Location rules, including the multi-root workspace rules for project scope.
4. Build the destination path from the resolved root and skill name.
5. If the destination already exists, follow the existing-target rule above. Do not switch to Update without an explicit update request.
6. Create the directory and write `SKILL.md` with valid frontmatter and a short body.
7. Add `scripts/`, `references/`, or `assets/` only when the use case needs them.
8. Validate, then report the path and the final description.

Template:

```markdown
---
name: code-reviewer
description: Review code for bugs, regressions, and maintainability issues. Use when the user asks for a code review, review of a diff or PR, or feedback before merging. Do not use for writing code from scratch.
---

# Code Reviewer

Review the given code or diff. Report bugs, missing tests, and concrete fixes first. Skip style nits unless they hide a defect.
```

## Install

When the user asks to install, perform the install. Pointing at the path is not enough.

1. Resolve the current product's user-level global skills root from the Location rules. Do not resolve the final skill path yet.
2. Resolve the source URL, package, marketplace entry, or local folder. If a package name does not identify a provider or marketplace, ask once instead of guessing.
3. Materialize the source into a temporary staging directory under the global skills root:
   - Local folder — copy the directory that contains `SKILL.md`
   - GitHub/repo URL — download the skill folder by archive or sparse checkout, not the whole monorepo
   - Package or marketplace entry — use a trusted product installer or resolver when available
4. Locate exactly one skill directory in staging. If none or more than one contains `SKILL.md`, stop and ask for a specific skill folder.
5. Read the staged `SKILL.md`, minimally validate that it can be loaded, and derive `<skill-folder>` from `name`.
6. Treat the staged source as immutable. Preserve every source file and path exactly; do not rewrite frontmatter, move resources, rename optional directories, or otherwise normalize a valid historical layout. Extra frontmatter keys and directories are allowed for Install when they do not prevent loading.
7. Run the Install validation checks on the staged directory and record a manifest of every relative file path and content hash, without executing downloaded files.
8. Set the final destination to `<global-skills-root>/<skill-folder>/`. If it exists, overwrite or update only when the user explicitly requested it; otherwise stop and report the existing path.
9. Move the validated staged directory into the final destination as one operation. For an authorized replacement, preserve the existing directory until the replacement succeeds. On failure, restore the existing directory and remove partial output.
10. Confirm `<destination>/SKILL.md` exists and its relative-path and content-hash manifest exactly matches the staged manifest, then report the installed path. Do not say "installed" before the files are there.

A trusted product install command may replace the manual staging steps only when it preserves the same collision, validation, and final-path checks.

Default install target is **global**. Pin into `<workspaceFolder>/.trae/skills/` only when the user explicitly wants the skill committed with this repo.

## Update

1. Resolve the exact target from an explicit path or scope first.
2. If project and global skills share the same name and the user did not specify one, ask one short question. Never update both.
3. For project scope, resolve `<workspaceFolder>` using the multi-root rules in Location.
4. Read the target `SKILL.md` and any referenced files you will touch.
5. Patch only what changed — description, body section, or a resource file.
6. Keep `name` aligned with the directory unless the user is explicitly renaming; when renaming, rename the directory too.
7. Validate.

## Validate

Check all of the following before telling the user the skill is done. If the environment provides a trusted validation script, run it instead of hand-waving. Apply the strict format checks to Create and Update; for Install, use only the minimum Install checks below and preserve the source unchanged.

- Path matches the chosen scope — project = `<workspaceFolder>/.trae/skills/<skill-folder>/`; global/install = `<userHome>/<dataFolderName>/skills/<skill-folder>/` for the current product
- Directory name equals `name`
- `SKILL.md` has parseable frontmatter and a non-empty body
- For Create or Update, `name` and `description` are unquoted and legal
- For Create or Update, `description` has no `: `, no `<`, no `>`, no `TODO`, and includes both what and when
- For Create, default to only `name` and `description` unless the user or target format requires additional frontmatter keys. For Update, preserve existing valid extra keys unless the user asks to remove them
- `scripts/`, `references/`, and `assets/` are conventional optional directories, not an allowlist. Preserve other valid directories and do not relocate existing resources without a task-specific reason
- For Install, require only a valid `name`, a present `description`, a non-empty body, and existing referenced files. Allow extra frontmatter keys, extra directories, quoted scalars, and historical resource layouts when they remain loadable
- For Install, record the staged relative-path and content-hash manifest before moving it, then verify the installed manifest is identical. Do not execute downloaded scripts or other downloaded files
- For Create or Update, execute each new or modified script once successfully

For Create or Update validation failures, fix and re-check. For Install validation failures, stop and report the incompatibility or ask the user; never repair or normalize the staged source. Do not re-read the whole file after a clean validation.

## Anti-patterns

- Creating a skill for knowledge the model already has
- Putting trigger words only in the body
- Calling this skill as a tool, or instructing the model to "invoke skill-creator first"
- Asking for name/purpose/source when the user already gave them
- Asking whether the user is an internal teammate or an external user in order to choose a path
- Telling the user a global path instead of installing when they asked to install
- Installing or writing CN skills into `~/.trae/skills/`, or International skills into `~/.trae-cn/skills/`
- Writing project skills to `<workspaceFolder>/.trae-cn/skills/` — the project folder name is always `.trae`
- Treating "install from the web" as "create a project skill"
- Rewriting frontmatter or reorganizing files while installing an existing third-party skill
- Claiming success before the files exist and pass validation
- Duplicating an existing skill instead of updating it

## Evaluate and benchmark (optional)

Creating a skill is one half of the loop; the other half is proving it works. This directory ships the upstream evaluation toolchain. Use it when the skill has objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps). Skip it for subjective skills (writing style, art) and rely on human review instead.

> **Why the toolchain is optional rather than mandatory**: benchmarking costs real time and needs a second execution environment. If the user says "just vibe with me", drop straight to manual review — do not run evals nobody asked for.

### Bundled resources

| Path | Use it for |
|------|-----------|
| [agents/grader.md](agents/grader.md) | Grader subagent instructions — evaluate each assertion against the outputs |
| [agents/comparator.md](agents/comparator.md) | Blind A/B comparison between two versions |
| [agents/analyzer.md](agents/analyzer.md) | Analyze why one version beat another; read the "Analyzing Benchmark Results" section for what to look for |
| [references/schemas.md](references/schemas.md) | JSON schemas for `evals.json`, `grading.json`, `benchmark.json` |
| [assets/eval_review.html](assets/eval_review.html) | HTML template for reviewing trigger-word eval sets |
| [eval-viewer/generate_review.py](eval-viewer/generate_review.py) | Build the review UI; supports `--static <path>` for headless environments |
| [scripts/run_eval.py](scripts/run_eval.py) | Run one eval prompt and capture the output |
| [scripts/aggregate_benchmark.py](scripts/aggregate_benchmark.py) | Aggregate runs into `benchmark.json` / `benchmark.md` with mean, stddev, and delta |
| [scripts/improve_description.py](scripts/improve_description.py) | Propose a better `description` for triggering accuracy |
| [scripts/run_loop.py](scripts/run_loop.py) | Full trigger-optimization loop — 60/40 train/test split, up to 5 iterations |
| [scripts/generate_report.py](scripts/generate_report.py) | Render an eval report |
| [scripts/quick_validate.py](scripts/quick_validate.py) | Validate `SKILL.md` frontmatter and structure |
| [scripts/package_skill.py](scripts/package_skill.py) | Package a skill folder into a distributable archive |

### The eval loop

1. **Write test cases.** Save 2–3 realistic prompts a real user would type to `evals/evals.json`. Prompts only at this stage — assertions come next, while runs are in flight. Schema in [references/schemas.md](references/schemas.md).
2. **Spawn runs in one turn.** For each test case, launch the with-skill run and the baseline run together — never with-skill first and baselines later. Baseline is `without_skill` for a new skill, or a snapshot of the previous version for an improved one.
3. **Draft assertions while runs proceed.** Write objectively verifiable assertions with descriptive names, update `evals/evals.json` and each run's `eval_metadata.json`.
4. **Grade.** Hand each run's outputs and assertions to a grader following [agents/grader.md](agents/grader.md). Save `grading.json` per run using the fields `text`, `passed`, `evidence` — the viewer depends on those exact names.
5. **Aggregate.** Run `python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>` from this directory. Put the with-skill entry before its baseline counterpart.
6. **Analyze.** Read the aggregate data for non-discriminating assertions, high-variance evals, and time/token tradeoffs — see [agents/analyzer.md](agents/analyzer.md).
7. **Show the user.** Run [eval-viewer/generate_review.py](eval-viewer/generate_review.py) to open the outputs and benchmark tabs. In a headless environment use `--static <output_path>` instead of starting a server.
8. **Read the feedback.** When the user says they are done, read `feedback.json`. Empty feedback means they were happy — focus improvements on the cases with specific complaints.
9. **Improve and repeat.** Generalize from the feedback rather than overfitting to the examples, keep the prompt lean, explain the why behind each rule, and bundle any helper script the runs kept rewriting. Then iterate into `iteration-<N+1>/`.

### Trigger-word optimization

The `description` field is the primary mechanism that decides whether the skill is invoked, so it deserves its own measurement pass.

1. Write 20 trigger queries — 8–10 that should trigger, 8–10 that should not. The negative cases must be near-misses that a naive keyword match would wrongly trigger, not obvious irrelevancies.
2. Review them with the user via the [assets/eval_review.html](assets/eval_review.html) template — replace `__EVAL_DATA_PLACEHOLDER__`, `__SKILL_NAME_PLACEHOLDER__`, and `__SKILL_DESCRIPTION_PLACEHOLDER__`, then open the result.
3. Run `python -m scripts.run_loop --eval-set <path> --skill-path <path> --model <model-id> --max-iterations 5 --verbose`.
4. Apply `best_description` from the output and show the user the before/after scores.

> **Why the model id matters**: the triggering test only matches the user's real experience when it runs on the same model that powers the session. Read it from the system prompt instead of guessing.

## Placement in this repository

This is a mirror of the Trae IDE builtin `skill-creator`, vendored so the workspace can serve it without depending on the IDE installation. Two facts about its shape:

- **The body above is the Trae builtin scope version** — the procedure Trae itself exposes for skill creation, installation, and location resolution. The `Location` section describes where *Trae* writes skills (`<workspaceFolder>/.trae/skills/`, `~/.trae-cn/skills/`), which is not this repository's convention.
- **The evaluation toolchain is the upstream Anthropic skill-creator package**, copied in with its `agents/`, `assets/`, `eval-viewer/`, `references/`, and `scripts/` directories plus `LICENSE.txt` (Apache-2.0), so every resource the procedure references actually exists here.

When creating or updating skills *in this repository*, follow the repository's own conventions instead of the Location section:

| Concern | This repository |
|---------|-----------------|
| Where project skills live | `.agents/skills/<skill-name>/` |
| Which rules govern skill authoring | `.agents/rules/skill-development.md`, plus the vendor methodology at `vendor/flexloop/apps/chaos/.agents/skills/skill-creator/SKILL.md` |
| How a new skill is registered | `.agents/skills/README.md` and `.agents/skills/CHANGELOG.md` |
| Which mirror track applies | Mirror skills record `source` for provenance and register on those two surfaces only — they do not add a `capability-registry` row or a `.meta/toml` mirror |

> **Why the distinction matters**: writing to `.trae/skills/` inside this repository would put a skill where nothing discovers it. The Location section stays because it is the faithful mirror of the builtin procedure and still governs genuinely global user-level skills.

The evaluation scripts invoke the `claude` CLI as a subprocess and expect a Claude Code style project layout (`.claude/commands/`). Run them only where that CLI and layout exist; otherwise use the manual review path.
