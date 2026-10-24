---
name: user-skill-sovereign-migration
version: 1.2.0
description: 把用户级 Skill 迁入 SpecWeave 主权区 .agents/skills，并完成原生轨改造与交接验收。当用户说「迁入 .agents/skills」「用户级 Skill 入库」「原生迁移」「移入主权区」「为什么没放在 .agents/skills」，或方案批准后改目标根但源 Skill 从未写入任何根时，必须使用此技能。先零写入分流：旧根有实体源才读源、保真复制并做 SHA256；旧根不存在且非联接则走零源改根分支——新根跨根查重、原生 frontmatter 直接创建、新根双门验收，重规划细节移交 skill-target-root-switch-replan。不用于外部平台镜像、从零设计、质量门修复、四处登记与联接。
argument-hint: "<skill-name 或用户级目录> [仓库根]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/**/SKILL.md"
  - ".agents/skills/README.md"
  - ".agents/skills/CHANGELOG.md"
  - ".agents/capability-registry/02-skills.md"
title: "用户级 Skill 主权区原生迁移"
x-toml-ref: "../../../.meta/toml/.agents/skills/user-skill-sovereign-migration/SKILL.toml"
metadata:
  source: "会话 0b5028ae-4c67-46da-8e99-0c2b68ae9c3a、82aa536e-ed72-4370-bd04-6f0ef014f959、511919f2-09d9-46aa-b6bb-a423d6f9e91d；declared-consistency-fix 迁移 + 零源改根 + ci-gate 迁移质量门分差实测"
---

# 用户级 Skill 主权区原生迁移

把已经可用、但仍放在 `~/.qoder/skills/` 的 Skill 迁入 SpecWeave 仓库的 `.agents/skills/`，并让它像原生 Skill 一样被发现、被索引、被质量门约束。若用户只说「迁入」、源却从未写入任何根，则走 §4.0A 直接创建，不执行复制与哈希。

## 1. Why

用户级目录与仓库主权区是两套发现体系。放在 `~/.qoder/skills/`，Skill 只对当前用户可见，不进入 README 索引、capability-registry、TOML 镜像和 CHANGELOG，也不受仓库质量门约束；放在 `.agents/skills/`，它才成为团队资产，能被链接门、质量门、docgen 和后续复用者找到。

但“复制过去”不等于迁移完成。三条轨道必须分清：

| 轨道 | 适用 | 登记与收尾 |
|---|---|---|
| 外部镜像 `skill-mirror-archive` | 外部平台/IDE 技能，要求原貌保真 | README + CHANGELOG 两处，不建 TOML |
| 原生迁移（本技能前半段） | 本地编写、需要按五要素治理 | 本技能负责迁入与内容验证，登记与联接移交 `native-skill-surface-registration` |
| 从零创建 `skill-creator` | 还不存在的 Skill | 先设计，再走原生登记 |

> **为什么位置决策必须前置？** 来源会话里，Skill 先在用户级目录创建，随后被连续纠正两次——“为何没有放在 `.agents/skills`?”与“移入 `.agents/skills` 目录”。返工成本不在复制，而在事后补位置判断、补登记、补质量门。先判断该不该迁，再动手。

> **为什么必须区分复制与联接？** 用户级与主权区各留一份实体内容，必然产生两份真相：后续修改只会落在其中一份，另一份继续漂移。当前约定是主权区保存权威副本，用户级用目录联接指回；本技能只负责把内容安全搬入主权区，联接与删除实体源目录交由 `native-skill-surface-registration` 按确认门执行。

> **为什么「迁入」不能直接当迁移执行？** 用户说「迁入 .agents/skills」时，源可能根本不存在。来源会话里，方案批准后用户只改了目标根，旧根从未写入；若照迁移流程读源全文、复制、比对哈希，只会得到一串“文件不存在”的假失败，或更糟——先创建空源再复制，留下一个空壳。先判定源是否存在，再决定是迁移还是直接创建。

## 2. 适用边界

适用：

- 用户级 Skill 已能工作，但需要纳入 SpecWeave 的发现与治理体系
- 用户质疑“为什么没放在 `.agents/skills`”，要求迁入
- 需要为用户级 Skill 补 `version/title/x-toml-ref/paths` 等原生字段
- 需要把用户级 Skill 的正文、`references/`、`scripts/` 原样搬入仓库并验证保真
- 用户口头说「迁入」但旧根从未写入任何根 → 零源改根分支：不复制、不哈希，直接按主权区原生轨创建

不适用：

| 场景 | 改用什么 |
|---|---|
| 外部平台/IDE 技能原貌归档 | `skill-mirror-archive` |
| 从零创建或大改内容 | `skill-creator` |
| 质量门掉分修复 | `skill-quality-gate-remediation` |
| 四处登记、双门验收、用户级 Junction | `native-skill-surface-registration` |
| Skill 已在仓库内，只想换目录 | `skill-migration-position-governance` 模式文档 |
| 方案已批准后仅更换目标根、且无源可迁 | `skill-target-root-switch-replan`（本技能只负责判定无源并完成创建） |
| 与 SpecWeave 无关、只服务个人跨项目 | 保留在 `~/.qoder/skills`，不迁移 |

## 3. 位置决策树

```
这个 Skill 应该放在哪里？
├─ 用户说「迁入」但旧根从未写入（无源可迁）？ → 零源改根分支（§4.0A）
├─ 依赖 SpecWeave 的脚本/规则/索引，需要团队发现？ → 原生迁移到 .agents/skills（本技能）
├─ 来自外部平台，要求原貌与来源追溯？ → skill-mirror-archive（镜像轨）
├─ 还不存在，需要设计新 Skill？ → skill-creator
├─ 已在 .agents/skills，只需换目录？ → skill-migration-position-governance
└─ 纯个人、与仓库无关？ → 保留用户级，不迁移
```

目标路径固定为 `<repo-root>/.agents/skills/<skill-name>`，目录名与 frontmatter `name` 必须一致。

## 4. 工作流

### 4.0 分流预检（零写入）

先判定「有没有源」，再选轨道：

```bash
test -e "<旧根>/<name>" && echo OLD_EXISTS || echo OLD_NOT_FOUND
test -L "<旧根>/<name>" && echo OLD_IS_LINK || echo OLD_NOT_LINK
```

| 旧根状态 | 轨道 |
|---|---|
| 实体目录 | §4.0B 有源迁移 |
| 不存在，且不是联接 | §4.0A 零源改根（直接创建） |
| 联接 | 停止，核实联接目标；不要重复迁移 |
| 存在但既非实体也非联接 | 停止，先定性（权限失败/特殊文件） |

### 4.0A 零源改根分支（无源可迁）

触发：用户说「迁入 .agents/skills」，但方案批准后只更换了目标根，旧根从未写入。

1. 复述 delta：旧根 → 新根，确认尚未写入任一目标根
2. 旧根取证：不存在、非联接、无未跟踪残留；若有空壳/半套副本/联接，先分类再报告，删除仅限本轮产物且需单独授权
3. 新根跨根查重：`~/.qoder/skills`、`~/.agents/skills`、`<repo>/.agents/skills`，仓库内补 `git grep` 与 TOML 探测
4. 重读新根约定：frontmatter 字段、登记面、质量门与链接门位置；不要沿用旧根假设
5. 输出修订方案等待确认
6. 确认后直接按新根原生轨写入；**不读取源全文、不复制、不做 SHA256**
7. 验收按新根门禁执行；并发登记面脏时只交付内容并写明「登记延后」

> **为什么无源时必须换轨？** 复制与哈希的前提是「源存在」。没有源时继续执行，只会在 `find`/`cp` 上得到假失败，或先造一个空源再复制，把空壳当成迁移结果。报告里把不存在的比对写成「不适用」，不要写成 PASS。

> **与 `skill-target-root-switch-replan` 的分工：** 后者的 R1–R6 负责「方案批准后改根」的完整重规划；本技能负责在「迁入」触发下判定无源，并在获准后完成新根创建与验收。只改根、不涉迁移时优先走后者。

### 4.0B 有源迁移预检（零写入）

1. 读取源 Skill 全文，列出 `references/`、`scripts/`、`assets/`、`evals/` 实际文件
2. 判断源路径是实体目录还是联接：
   - PowerShell：`Get-Item <path> | Select-Object LinkType, Target`
   - 已是联接说明它已指向某处，停止并核实，不要重复迁移
3. 确认目标目录不存在；若存在，停止并进入冲突裁决（覆盖/改名/放弃）
4. 确认仓库根：`git rev-parse --show-toplevel`，并判断是否在 submodule 内
5. `git status --short` 记录无关脏文件，后续不 stage、不 stash、不清理
6. 探测四个登记面是否已有同名条目，判断这是首次迁移还是重入

> **为什么先读全文再迁移？** 只按文件名复制会漏掉正文里写死的相对路径、资源引用和 frontmatter 依赖；用户级与项目级的元数据契约也不同，先读才能判断哪些字段要补、哪些正文要改。

### 4.1 提案与批准（零写入）

输出一张清单，至少包含：

| 项目 | 内容 |
|---|---|
| 源路径 | `~/.qoder/skills/<name>`（实体目录/联接） |
| 目标路径 | `<repo>/.agents/skills/<name>` |
| frontmatter 变更 | 新增/保留哪些字段 |
| 正文变更 | 只做原生化必要修改，列明章节 |
| 资源清单 | 将复制的 `references/`、`scripts/`、`assets/` |
| 交接事项 | 四处登记、质量门/链接门、Junction 收尾 |
| 收尾语义 | 仅迁入（保留源）还是迁入后联接（需单独确认） |

等待用户确认后再写入。批准范围外的扩展回到本阶段补充。

### 4.2 原生化 frontmatter

在保留原有有效字段的前提下补齐：

```yaml
name: <skill-name>
version: <语义化版本>
description: <单行，未加引号，含触发场景与强制使用措辞>
argument-hint: "<...>"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/<skill-name>/**"
title: "<Skill 标题>"
metadata:
  source: "<会话与案例溯源，不写本机绝对路径>"
# 仅当 .meta/toml 镜像已创建时写：
x-toml-ref: "../../../.meta/toml/.agents/skills/<skill-name>/SKILL.toml"
```

`x-toml-ref` 的层数必须按文件实际位置推算：`.agents/skills/<name>/SKILL.md` 到仓库根是三级，因此是 `../../../`；不要照抄模板文件在 `.agents/skills/` 根目录时的 `../../`。

`x-toml-ref` 是条件字段，不是模板常量：`check-links.py --check-frontmatter-paths` 默认校验 `source` 与 `x-toml-ref`（`check-links.py:477`），`.meta/toml` 镜像尚未创建时写入必然报「文件不存在」，等于自造一条链接门断链。若本轮登记延后，`source`/`x-toml-ref` 一并延后；`metadata.source` 用会话 ID 等非路径文本。

> **为什么条件字段不能照抄模板？** 模板默认所有原生字段都已就位；实际迁移常常先交付内容、后补登记。镜像未建时写回指字段，链接门会立刻变红，而失败原因不是内容缺陷，而是模板假设与本轮范围不一致。

### 4.3 保真复制

- 正文与资源用文件复制完成，禁止手抄
- 复制前确认目标不存在，避免 `Copy-Item`/`cp` 变成嵌套目录
- 排除 `__pycache__`、`*.pyc`、`.DS_Store` 等运行残留
- 保留 `references/`、`scripts/` 的相对路径与兄弟依赖

### 4.4 内容级验证

至少完成五项：

1. 资源逐文件 SHA256 与源一致
2. `SKILL.md` 去掉 frontmatter 后，正文与源一致（除非提案列明了正文修改）
3. 全文无 `file:///`
4. `references/`、`scripts/` 中被正文引用的路径真实存在
5. 内部 Markdown 链接可达

质量门必须做**两侧对照**，而不是只看目标分数：

1. 在目标目录与源目录用同一命令各跑一次（`check-skill-quality.py --path <dir> --json`），记录分数、错误/警告清单与退出码。
2. 计算分差并逐项归因：目标分差应只来自已批准的 frontmatter 变更；其余警告须能在源侧逐条找到对应项，才可判定「零漂移」。来源会话实测：源 65 分/7 warn → 目标 70 分/6 warn，+5 恰好是新增 `paths` 消掉的一条，残余 6 项在源侧逐条存在。
3. 目标 <100 时按批准范围分流：
   - 批准范围允许正文修改 → 转 `skill-quality-gate-remediation`，修完复跑 `--score --threshold 100` 再交接。
   - 批准范围明确排除正文（如「只迁入内容 + 验收」「正文不动」）→ **不得改正文凑分**；把未达标项、残余警告清单、两侧分差写入交付报告与交接载荷，标注「质量门未达标，修复待下一轮单独授权」。本轮不得把登记/联接表述为「已达标」。

> **为什么质量门要两侧对照？** 目标分数低不一定是迁入造成的：用户级与原生轨的元数据契约不同，有些警告在源侧本来就存在。只有同一命令在源与目标各跑一次、把分差逐项归因，才能区分「迁入漂移」与「既有内容特征」。

> **为什么批准范围排除正文时不能转修复？** `skill-quality-gate-remediation` 会改正文；当用户只批准「迁入内容 + 验收」且明示「正文不动」时，转修复即越权。正确动作是停止修复、把未达标项如实上报，把修复留给下一轮单独授权。

### 4.5 移交登记与收尾

目标目录验证通过后，调用 `native-skill-surface-registration`，并附上迁移事实：

- 源路径与目标路径
- frontmatter 变更摘要
- 资源哈希比对结果
- 源目录当前是实体目录还是联接
- 用户是否已授权删除实体源目录

该技能负责四处登记、质量门与链接门双验收、用户级 Junction 创建与回读验证。不要在本技能内另写一套登记模板，避免两处格式漂移。

### 4.6 移入收尾与报告

只有同时满足以下条件，实体源目录才可被清除：

- 目标目录校验全部通过
- 源与目标文件清单、哈希一致（frontmatter 差异已列明）
- 用户明确授权“移入/删除源目录”
- `native-skill-surface-registration` 已完成 Junction 创建或明确报告联接状态

否则保留源目录，交付时明确写“已完成迁入，源目录保留”，不得声称已 move。

## 5. 安全检查清单（逐项确认）

- [ ] 已先判定旧根存在性与联接类型，未把「迁入」当有源证据
- [ ] 无源分支未执行读源全文、复制或 SHA256，报告如实标注不适用
- [ ] 无源分支已在新根跨根查重并重读该根 frontmatter 约定
- [ ] （有源迁移）已读源 Skill 全文并盘点全部资源，目标目录不存在
- [ ] 已确认源路径是实体目录而非既有联接
- [ ] 已输出提案并取得用户确认，批准前零写入
- [ ] 已确认仓库根与 submodule 状态，未触碰无关脏文件
- [ ] `x-toml-ref` 深度按文件实际位置推算，非照抄模板
- [ ] （有源迁移）复制采用文件复制并做 SHA256 比对，无手抄
- [ ] 已确认正文仅按提案列明的范围修改
- [ ] 已确认无 `file:///`、无运行残留、引用资源存在
- [ ] 质量门已在源与目标两侧用同一命令各跑一次，分差可逐项归因
- [ ] 质量门 <100 时已按批准范围分流：可改正文则转修复，不可改正文则如实上报未达标项
- [ ] `x-toml-ref` 仅在 `.meta/toml` 镜像已创建时写入；登记延后时 `source`/`x-toml-ref` 一并延后
- [ ] 四处登记与 Junction 已移交 `native-skill-surface-registration`
- [ ] 删除实体源目录前已获得单独且明确的授权
- [ ] 未提交、未推送，除非用户明确要求

## 6. Gotchas（陷阱与反直觉行为）

1. **源目录可能已经是联接**：直接复制会复制目标内容或形成环；先用 `Get-Item | Select LinkType, Target` 判断。
2. **`x-toml-ref` 层数会错**：模板在 `.agents/skills/` 根目录时是 `../../`，迁到子目录后必须多一层。按文件实际位置数，不按记忆。
3. **复制会嵌套**：目标已存在时 `Copy-Item -Recurse` 可能生成 `dst/<name>`；复制前必须确认目标不存在。
4. **copy 不等于 move**：删除实体源目录是独立授权，校验通过也不能自行推定。
5. **两份实体必然漂移**：用户级与主权区同时保留实体内容时，后续修改只会落在其中一份；最终状态应是一个权威副本加一个联接。
6. **表头计数可能本来就错**：登记面由 `native-skill-surface-registration` 按“表头数字 = 表体行数”校正；本技能不要顺手另改一套。
7. **`check-links` 对单文件可能假通过**：`--path` 传单个文件时可能按目录解析，扫 0 个文件也报通过；新增链接目标要用显式存在性检查兜底。
8. **`source` 字段断链不一定是本次引入**：frontmatter 路径按文件所在目录解析，仓库根相对写法天然报错；先与 HEAD 对照再定性。
9. **质量门 70 分不等于达标**：原生轨验收用 `--threshold 100` 且全项通过；65 分常见构成是一个 error 加四个 warn。
10. **`Edit` 零匹配先重读**：迁移中修改正文时，`old_string` 不匹配通常是文件已被前一步改动；重读后再编辑，不要反复盲试。
11. **`git add -A` 会混入他人变更**：共享工作区按路径精确暂存，提交前用 `git diff --cached --name-status` 复核。
12. **不要用 `rm -rf` 清理用户级目录**：空目录用 `rmdir`（非空即失败），非空目录是实体副本信号，先报告再处理。
13. **「迁入」是意图不是证据**：先 `test -e` 与 `test -L`；旧根不存在时照做复制会制造空壳，哈希比对也没有对象。
14. **`ls` 输出为空不等于从未写入**：空目录、联接与权限失败都可能表现为空；存在性和联接类型必须分开判定。
15. **无源时不要伪造“哈希一致”**：没有源就没有比对对象，报告写“不适用”；把不适用写成 PASS 会让后续审计误判。
16. **方案批准后改根归 `skill-target-root-switch-replan`**：本技能只做无源分流与创建，不要另写一套重规划清单。
17. **目标分数低不必然是迁入失败**：只看目标分数会把既有内容特征误判为迁移漂移；必须与源侧同命令分差对照，逐项归因（如新增 `paths` 带来的 +5）。
18. **批准范围排除正文时，「转修复」是越权**：`skill-quality-gate-remediation` 会改正文；范围只批「迁入 + 验收」时应停止修复、上报未达标项，把修复留给下一轮单独授权。
19. **`x-toml-ref` 不是无条件字段**：`check-links.py` 默认校验 `source` 与 `x-toml-ref`；`.meta/toml` 镜像未建时写入等于自造断链，登记延后则两个回指字段一并延后。

## 参考

- 精确命令、哈希/正文比对脚本与交接载荷：[references/migration-procedure.md](references/migration-procedure.md)
- 已验证案例（declared-consistency-fix）：[references/case-declared-consistency-fix.md](references/case-declared-consistency-fix.md)
- 已验证案例（零源改根）：[references/case-zero-source-root-switch.md](references/case-zero-source-root-switch.md)
- 已验证案例（ci-gate-effectiveness-audit 迁移与质量门分差）：[references/case-ci-gate-migration.md](references/case-ci-gate-migration.md)

## Changelog

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.2.0 | 2026-10-24 | 补充三条实测分支。依据会话 `511919f2-09d9-46aa-b6bb-a423d6f9e91d` 的 ci-gate-effectiveness-audit 迁移：①质量门在源与目标两侧用同一命令各跑一次，用分差证明零漂移（源 65/7 warn → 目标 70/6 warn，+5 为新增 `paths`）；②批准范围排除正文时，<100 不得改正文凑分，应上报未达标项并留待下一轮授权；③`x-toml-ref` 仅在 `.meta/toml` 镜像已创建时写入，登记延后则 `source`/`x-toml-ref` 一并延后。 |
| 1.1.0 | 2026-10-24 | 新增零源改根分支。依据会话 `82aa536e-ed72-4370-bd04-6f0ef014f959`：用户说「迁入 .agents/skills」时旧根从未写入，复制与哈希不适用。工作流拆为 4.0 分流、4.0A 零源改根、4.0B 有源迁移；补充旧根存在/联接取证、无源不得伪造哈希结论，交接 `skill-target-root-switch-replan`；迁移入主权区并补齐原生 frontmatter。 |
| 1.0.0 | 2026-10-23 | 初始版本。基于会话 `0b5028ae-4c67-46da-8e99-0c2b68ae9c3a` 的 declared-consistency-fix 迁移，固化位置决策、原生化、保真复制、内容验证与登记/Junction 交接门。 |
