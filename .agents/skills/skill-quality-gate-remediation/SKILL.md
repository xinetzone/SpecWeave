---
name: skill-quality-gate-remediation
version: 1.0.0
description: "修复既有 Skill 在 SpecWeave 质量门 check-skill-quality.py 下的失分项，把 65 分档的 Skill 提升到 100 分且全部检查项通过。当用户提到「质量门 65 分」「check-skill-quality 报错」「Skill 评分不够」「过不了质量门」「补 Why/Gotchas/安全检查清单/dry-run」「skill quality gate」「Skill 体检不合格」时，必须使用此技能。流程是先跑基线、按严重度分诊、预览修改清单并取得确认、做实质修复、复跑至满分、记录首败原因。不用于从零创建 Skill（用 skill-creator），也不用于普通代码质量检查（用对应的 lint 与测试）。"
argument-hint: "<skill-dir> [checker-path]"
user-invocable: true
disable-model-invocation: false
paths:
  - "**/SKILL.md"
source: "会话 0b5028ae-4c67-46da-8e99-0c2b68ae9c3a；declared-consistency-fix 质量门 65→100"
---

# Skill Quality Gate Remediation

把一个「功能已经可用、但质量门不达标」的 Skill 修到 100 分，同时避免把文档改成关键词拼盘。适用对象是已有 `SKILL.md`（用户级 `~/.qoder/skills/` 或项目级 `.agents/skills/`），不是从零设计新 Skill。

## 1. 适用边界

适用：

- 质量门报告单项失败（error/warn），需要定位并修复。
- 分数在 40–90 之间，用户明确要求「修到 100」或「全部通过」。
- Skill 内容有效，但缺少 Why 解释、安全检查、Gotchas、frontmatter 推荐字段。

不适用：

- 从零创建 Skill —— 改用 `skill-creator`，本技能只做补救。
- 普通代码质量、lint、测试失败 —— 用对应语言工具链。
- 修改检查器本身来「让分数变高」—— 禁止，检查器是评分真源。

> **为什么？** 质量门检查的是文档契约而不是功能正确性。把「新建」误判成「补救」，会在没有基线分数的情况下堆砌章节；把「代码 lint」误判成「Skill 质量门」，则会改错文件。先分清任务类型，再决定是否进入本流程。

## 2. 输入与前置

动手前确认三件事：

| 输入 | 默认值 | 缺失时 |
|---|---|---|
| Skill 目录 | 无，必须由用户给出 | 先询问绝对路径，不要猜 |
| 检查器路径 | `<SpecWeave>/.agents/scripts/check-skill-quality.py` | 用默认值并在报告中注明 |
| 修改范围 | 仅目标 Skill 目录 | 需要新增 `references/` 或改仓库文件时先声明并取得确认 |

约束：

- 只读检查器与 `.agents/scripts/lib/check_skill_quality/` 源码，禁止修改检查规则或评分公式。
- 不提交 git，不发布，不修改目标目录之外的仓库文件。
- 目标目录不存在时停止：确认是路径写错，还是应改用 `skill-creator` 新建。
- 用户级 Skill 与项目级 Skill 的元数据要求不同；先确认目标实际位置，再套用本流程。

## 3. 基线：先量化，再动手

在 SpecWeave 仓库根目录运行并保存完整输出：

```bash
python .agents/scripts/check-skill-quality.py --path "<skill-dir>" --verbose
python .agents/scripts/check-skill-quality.py --path "<skill-dir>" --score --threshold 100
```

记录四项事实：

1. 当前分数与通过项数。
2. 每个失败项的检查名、severity、原始提示。
3. 失败项集中在 frontmatter、description、正文结构还是安全检查。
4. 目标目录是否已有 `references/`、`scripts/`、`assets/`、`evals/`。

评分公式（`scoring.py`）：100 起算，error −15、warn −5、info −1，最低 0。默认阈值 70；本技能的目标是 100 分且全部检查项通过，而不是「过 70 即可」。

> **为什么？** 65 分通常等于一个 error 加四个 warn（100 − 15 − 5×4）。不先看清扣分构成，容易先修一堆 warn 却漏掉 −15 的 error，复跑后分数仍然不达标。

## 4. 分诊顺序

按扣分权重从高到低修：

| 顺序 | 检查名 | 严重度 | 扣分 | 典型原因 |
|---|---|---|---|---|
| 1 | `safety.dry_run` | error | −15 | 写操作 Skill 没有任何预览/确认机制 |
| 2 | `description.mandatory_phrase` | error | −15 | 缺少「必须使用」等强制触发措辞 |
| 3 | `file.length` | error | −15 | 正文超过 500 行 |
| 4 | `why.explanations` | warn | −5 | 用 `## Why` 标题代替 `> **为什么？**` 引用块，或不足 2 处 |
| 5 | `safety.idempotent` | warn | −5 | 没有重复执行检查或收尾验证 |
| 6 | `safety.checklist` | warn | −5 | 缺少「安全检查清单（逐项确认）」或勾选项不足 5 个 |
| 7 | `open_standard.body.gotchas` | warn | −5 | Gotchas 标题没有编号 |
| 8 | `frontmatter.version` 等 | warn | 各 −5 | 缺少推荐字段 |
| 9 | `description.length`、`open_standard.name.*` | warn | 各 −5 | 描述过短、命名不合规 |
| 10 | `paths.no_file_url` | error | −15 | 文档出现 `file:///` 绝对路径 |

同一轮内先修 error，再修 warn；每轮只做一类修改，便于复跑时定位是哪个改动生效。

## 5. 预览修改方案（dry-run）

编辑前先输出一张修改清单，等用户确认后再落盘：

| 失败项 | 当前位置 | 拟修改内容 | 修改理由 | 预计消除扣分 |
|---|---|---|---|---|
| `safety.dry_run` | 工作流第 3 节 | 增加「先预览、再确认、后写入」步骤 | 写操作缺少确认门 | −15 |
| `why.explanations` | 全文 | 增加 2–3 个 `> **为什么？**` 引用块 | 解释设计意图 | −5 |

预览要给出章节级位置和改写意图，不要只写「补安全检查」。若修改涉及新增文件，先列出文件名与用途；若用户未确认，不写入。

> **为什么？** 质量门修复容易演变成大规模文档改写。预览让用户在看到 diff 之前就能否决方向错误的改动，也避免为了凑检查项而破坏原有有效内容。

## 6. 实质修复，而不是关键词填充

### 6.1 Why 解释

必须是 Markdown 引用块，且全文至少 2 处：

```markdown
> **为什么？** 这里解释该规则要解决的问题、不遵守时的真实故障，以及边界情况如何判断。
```

`## Why` 标题不计入；只写一句「因为这样更好」也不算实质解释。

### 6.2 dry-run / 预览

在目标 Skill 的工作流中真实加入「列出变更 → 用户确认 → 执行」的步骤，并写明未确认时停止。仅出现「预览」二字但流程没有确认门，属于伪修复。

### 6.3 幂等与收尾验证

写明重复执行的判定：目标已存在时是跳过、覆盖还是报错；执行后如何检查结果（文件存在、内容匹配、链接可解析）。至少加入一种可观察的收尾验证。

### 6.4 安全检查清单

使用编号章节标题，并提供至少 5 个真实可勾选项：

```markdown
## 9. 安全检查清单（逐项确认）

- [ ] 已确认目标目录，未误改其他 Skill
- [ ] 已预览全部修改并取得用户确认
```

检查项要对应真实风险，不要复制五个同义句。

### 6.5 Gotchas

使用带编号的标题，例如 `## 8. Gotchas（陷阱与反直觉行为）`。正文列容易误判的规则细节，例如「标题形式不算 Why」「清单少于 5 项不算通过」。

### 6.6 Frontmatter

保留原有有效字段，补齐 `name`、`description`、`version`、`argument-hint`、`user-invocable`、`paths`。`name` 必须是 kebab-case 且与目录同名；`description` 控制在 150–1024 字符，包含强制触发措辞与触发场景。

### 6.7 路径与长度

正文不超过 500 行；超出时把细节移入 `references/` 并在 SKILL.md 留导航。删除 `file:///` 绝对路径，改用相对路径或行内代码。

> **为什么？** 检查器只能判断形式是否存在，无法判断内容是否有用。只补关键词能过门，却会让后续读者拿到一份没有决策价值的文档；实质修复才让「100 分」同时代表可用性。

## 7. 复跑与收口

修改后必须重新执行真实命令，而不是凭印象宣布通过：

```bash
python .agents/scripts/check-skill-quality.py --path "<skill-dir>" --verbose
python .agents/scripts/check-skill-quality.py --path "<skill-dir>" --score --threshold 100
```

通过标准：

- 分数 100，全部检查项通过，命令退出码为 0。
- `--verbose` 输出中不存在 FAIL。
- 若 Skill 含 Markdown 链接，再跑链接检查并确认 0 断链。

未达标时，对照失败项继续第 4–6 节；禁止通过删除有效章节、缩短描述到不触发检查、或修改检查器来「绕过」。

## 8. 记录首败与交付

交付报告至少包含：

| 项目 | 内容 |
|---|---|
| 首次基线 | 分数、通过数、失败检查名 |
| 首败根因 | 为什么该检查失败（结构缺失还是措辞缺失） |
| 修改摘要 | 改了哪些章节、新增了哪些文件 |
| 复跑结果 | 最终分数、通过项数、退出码 |
| 复跑命令 | 可被他人重复执行的完整命令 |

把同样的信息写入目标 Skill 的变更记录，避免下次维护时只知道结果、不知道原因。

## 9. Gotchas（陷阱与反直觉行为）

1. `## Why` 标题不算 Why 解释：检查器只匹配 `> **为什么` 引用块，至少需要 2 处。
2. Gotchas 标题必须带编号（如 `## 8. Gotchas`）；无编号的 `## Gotchas` 仍会失分。
3. 安全检查清单只有标题不够：`- [ ]` 勾选项必须不少于 5 个。
4. `--threshold 70` 只保证「不是低分」，不保证满分；验收要用 `--threshold 100` 加全项通过。
5. 用户级 Skill 常用极简 frontmatter，直接套用项目级检查会稳定丢 20 分左右；这不是内容差，而是元数据契约不同。
6. 编辑前不读文件会导致 `old_string` 零匹配；先 Read 再 Edit，失败后重读而不是反复盲试。
7. 检查器把「检测到写操作关键词」作为触发条件；文档里出现「创建/更新/编辑」就会启用安全检查，不能以「本 Skill 不写文件」为由跳过。
8. 修完立即复跑；中间插入其他改动会让失败项来源无法归因。

## 10. 安全检查清单（逐项确认）

- [ ] 已确认真实的 Skill 目录与检查器路径，未误改其他目录
- [ ] 已保存首次基线输出与失败检查名
- [ ] 已预览修改清单并取得用户确认
- [ ] 已确认新增文件仅位于目标 Skill 目录内
- [ ] 已确认未修改检查器、评分公式或其他 Skill
- [ ] 已确认 Why 解释、dry-run、幂等验证、清单与 Gotchas 均有实质内容
- [ ] 已复跑质量门并确认 100 分、全项通过、退出码 0
- [ ] 已执行链接检查并确认无断链

## 参考

- 检查项与修复映射：[references/check-map.md](references/check-map.md)
- 真实修复案例：[references/case-declared-consistency-fix.md](references/case-declared-consistency-fix.md)
- 创建新 Skill：`skill-creator`（CLI 内置）

## 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-23 | 初始版本：基线、分诊、预览、实质修复、复跑与首败记录 |
