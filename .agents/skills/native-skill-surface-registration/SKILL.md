---
name: native-skill-surface-registration
version: 1.0.0
description: "把新建或迁入 .agents/skills 的 SpecWeave 原生 Skill 完成四处全量登记（README 表行与分类计数、capability-registry/02-skills 表行与计数、skills/CHANGELOG 版本条目、.meta/toml SKILL.toml 镜像），再以质量门 34 项全过 + 链接门 0 断链双门验收收尾，最后用目录联接（非副本）把用户级 ~/.qoder/skills 指向主权区权威副本，并顺带审计登记面计数漂移。当用户提到「登记这个 Skill」「四处登记」「登记面同步」「SKILL.toml 镜像」「技能入库」「新建 Skill 要登记」「收尾双门」「联接而非副本」时，必须使用此技能。不用于外部平台技能镜像归档（用 skill-mirror-archive，其登记面仅 README+CHANGELOG 两轨）；不用于质量门掉分修复（用 skill-quality-gate-remediation）；不用于从零设计 Skill（用 skill-creator）。"
argument-hint: "<skill-dir-name> [registry-root]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/**/SKILL.md"
  - ".agents/skills/README.md"
  - ".agents/skills/CHANGELOG.md"
  - ".agents/capability-registry/02-skills.md"
source: "会话 82bdd798-8c2b-4dfb-a04d-1153618957a5 与 b2c97a46-89db-466b-837a-01b88669ae4b；skill-quality-gate-remediation v1.31 入库实测"
---

# Native Skill Surface Registration

把一个已经落盘在 `D:\spaces\SpecWeave\.agents\skills\<name>\`（或等价主权区路径）的原生 Skill，登记进仓库的四个登记面并通过双验收门，最后以目录联接暴露到用户级技能目录。目标产物：四个登记面各 +1 行/条目且计数同步、质量门 100/100（34 项全过、退出码 0）、链接门 0 断链 0 警告、用户级联接指向主权区且零内容复制。

## 1. 适用边界

适用：

- 新建或迁入 `.agents/skills` 的第一方 Skill 需要完成入库登记与验收收尾。
- 需要把 `~/.qoder/skills` 下的用户级副本改造为指向主权区的联接。
- 发现 README / capability-registry 分类计数与表行数不一致，需要顺带修正。

不适用：

- 外部平台/IDE 技能镜像归档 —— 用 `skill-mirror-archive`（登记面裁剪为 README+CHANGELOG 两轨，不登记 registry 与 toml 镜像）。
- 已有 Skill 质量门掉分的分诊修复 —— 用 `skill-quality-gate-remediation`。
- S0–S3 通用治理落盘批准门 —— 参考 `sovereign-rollout-cmd`；本技能假设 Skill 内容本身已获批准落盘。

> **为什么？** 原生 Skill、外部镜像、修复补救三类任务的登记面不同：原生必须四处全量且计数同步，镜像只走两轨。混淆三者会导致 registry 出现镜像条目污染、或原生 Skill 缺镜像而在后续 `--check-frontmatter-paths` 扫描中报断链。

## 2. 输入与前置

| 输入 | 默认值 | 缺失时 |
|---|---|---|
| Skill 目录名 | 无，必须明确给出 | 先询问，不要猜 |
| 主权区根目录 | `D:\spaces\SpecWeave` | 从当前工作区确认 |
| 内容是否已获批准落盘 | 假定已批准 | 未批准先走 skill-creator / sovereign-rollout-cmd |

前置探针（全部只读，任一不满足先处理再继续）：

```bash
# 1) 权威副本存在
ls .agents/skills/<name>/SKILL.md
# 2) 质量门基线（先过门再登记，避免失败项污染登记面）
python .agents/scripts/check-skill-quality.py --path .agents/skills/<name> --verbose
# 3) 幂等重入探测：四处是否已登记、用户级是否已联接
grep -n "<name>" .agents/skills/README.md .agents/capability-registry/02-skills.md .agents/skills/CHANGELOG.md
ls .meta/toml/.agents/skills/<name>/SKILL.toml 2>/dev/null
ls -la ~/.qoder/skills/ | grep "<name>"
```

| 探测结果 | 动作 |
|---|---|
| 某登记面已有同名行/条目 | 跳过该面，仅核对内容与计数 |
| `.meta/toml` 镜像已存在 | 跳过，核对字段 |
| 用户级已是联接（指向主权区） | 跳过 S6 |
| 用户级是实体副本目录 | 进入 S6 前先报告，经确认后改造为联接 |

## 3. 预览与确认门

登记是跨四个受版本控制文件的写操作。写入前输出一张预览清单并等待确认：

| 登记面 | 拟变更 | 计数变化 |
|---|---|---|
| `.agents/skills/README.md` | 分类表新增一行 | 该分类表头 (N个) → (N+1个) |
| `.agents/capability-registry/02-skills.md` | 分类表新增一行 | 表头同上独立计数 |
| `.agents/skills/CHANGELOG.md` | 顶部新增 v<下一版> 条目 | 版本 +1 |
| `.meta/toml/.agents/skills/<name>/SKILL.toml` | 新建镜像 | — |
| `~/.qoder/skills/<name>` | 新建目录联接 | — |

未确认不写入；用户只确认部分面时，只做被确认的部分并在交付报告注明缺口。

## 4. 四处登记

各面的精确格式模板与实测样例见 [references/registration-surfaces.md](references/registration-surfaces.md)。

1. **README 表行**：插入到对应分类（命令门面/完整Skill/工作流门面…）表格末尾，路径列用 `<name>/SKILL.md`（相对 `.agents/skills/`）。
2. **registry 表行**：插入到 02-skills.md 对应分类表，路径列用 `../skills/<name>/SKILL.md`（相对 `.agents/capability-registry/`）——两个登记面的路径基准不同，禁止互相照抄。
3. **CHANGELOG 条目**：先 `grep -m1 "^\- \*\*v" .agents/skills/CHANGELOG.md` 读取当前最新版本号再 +1；条目注明分类计数变化（如「完整 Skill 14→15」）与验收数据。
4. **toml 镜像**：新建 `.meta/toml/.agents/skills/<name>/SKILL.toml`，字段与既有镜像一致（id/title/category/date/version），`category` 为 `skills/<name>`。

计数规则：README 与 registry 的分类计数各自独立，均以「表头数字 = 表体行数」为准；修改表行的同时改表头，禁止只改一边。

> **为什么？** 登记面是后续会话发现该 Skill 的唯一索引入口。漏 registry 会让能力检索不到，漏 toml 镜像会让 `--check-frontmatter-paths` 与 OKF 构建缺元数据，CHANGELOG 不记验收数据则下次无法复跑比对基线。

## 5. 双门验收

登记完成后必须实跑两条命令，不以「已登记」推定「已验收」：

```bash
python .agents/scripts/check-skill-quality.py --path .agents/skills/<name> --score --threshold 100
python .agents/scripts/check-links.py --paths .agents/skills .agents/capability-registry --check-frontmatter-paths
```

- 质量门：100/100、34 项全部 PASS、退出码 0。不达标 → 转 `skill-quality-gate-remediation` 修复后回到本节复跑。
- 链接门：0 断链、0 警告。典型失败是新增行/引用指向目录（如 `.meta/toml/.../`）——链接检查按文件解析，必须把链接改为指向具体源文件（如 `SKILL.md`）再复跑。

## 6. 用户级目录联接

权威内容只保留主权区一份，用户级 `$env:USERPROFILE\.qoder\skills\<name>` 用 Windows 目录联接指向它，零复制：

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.qoder\skills\<name>" `
  -Target "<仓库根>\.agents\skills\<name>"
```

- 不要用 `cmd /c mklink /J`：在本机中文/长路径环境下输出乱码且失败难诊断，PowerShell `New-Item -ItemType Junction` 是已验证替代。
- 不要用复制（`cp`/`Copy-Item`）：双份内容必然漂移。
- 若登记或探测过程在用户级路径生成了空目录树，用 `rmdir`（仅空目录可删，非空即失败，天然安全）清掉后再建联接；非空目录说明存在实体副本，先向用户报告再处理。
- 收尾验证：通过用户级路径回读 `SKILL.md` 首行，确认内容与主权区一致。

> **为什么？** Qoder 从 `~/.qoder/skills` 发现技能，而版本控制只覆盖主权区。联接让「可触发」与「可追溯」同时成立；复制则制造两份真相，修改只会落在不被追踪的那一份上。

## 7. 计数漂移审计与记录

对 README 与 registry 的每个分类表头做一次「表头数字 vs 表体行数」比对（`awk` 取段落再 `grep -c "^| "`）。HEAD 里的既有漂移应顺带修正，并在 CHANGELOG 条目中显式记录，例如：

> 顺带修正既有计数漂移：README 完整Skill 表头 11→13（原有 12 行）、registry 9→11（实测行数为 …）。

漂移不修正会让下一次登记基于错误基数，错上加错；不记录则修正本身无法审计。

## 8. 交付报告

| 项目 | 内容 |
|---|---|
| 登记面状态 | 四处各自 +1 行/条目（或跳过原因） |
| 计数变化 | 分类表头 old→new，两处登记面分别列出 |
| 质量门 | 分数、通过项数、退出码、命令 |
| 链接门 | 断链/警告计数、命令 |
| 联接 | 创建命令与回读验证结果 |
| 漂移记录 | 是否发现并修正 HEAD 计数漂移 |

## 9. Gotchas（陷阱与反直觉行为）

1. `skill-mirror-archive` 的两轨登记面（README+CHANGELOG）只适用外部镜像；原生 Skill 套用会缺 registry 与 toml 镜像两处。
2. README 与 registry 的分类计数基数不同（同一分类可能 14 vs 12），各自与自身表行数比对，禁止互相「对齐」。
3. 两个登记面的相对路径基准不同：README 行内是 `<name>/SKILL.md`，registry 行内是 `../skills/<name>/SKILL.md`。
4. 指向目录的 Markdown 链接会被链接门判失败，必须改指具体文件。
5. CHANGELOG 版本号必须以磁盘 grep 结果为准，不能凭记忆 +1——并发会话可能已占用号。
6. 先跑质量门再全量登记更稳：登记后再修内容，CHANGELOG 里写的验收数据可能已过期。
7. `cmd /c mklink /J` 在中文环境乱码失败，改用 PowerShell `New-Item -ItemType Junction`。
8. 用户级空目录树用 `rmdir` 清理（非空即失败），不要 `rm -rf`；非空目录是实体副本信号，须先报告。
9. 链接门要扫「登记面 + 技能目录」全集，只扫新 Skill 目录会漏掉新增行里的跨区引用。
10. 质量门 `--threshold 70` 的「通过」不等于验收：本流程要求 `--score --threshold 100` 且 34 项全过。

## 10. 安全检查清单（逐项确认）

- [ ] 已确认 Skill 内容获批准落盘，未误改其他 Skill 目录
- [ ] 已在写入前输出四处登记预览并取得用户确认
- [ ] 已用磁盘 grep 确认 CHANGELOG 当前最新版本号
- [ ] README 与 registry 的表行与表头计数同轮修改、各自一致
- [ ] 已实跑质量门并确认 100/100、34 项全过、退出码 0
- [ ] 已实跑链接门并确认 0 断链、0 警告（目录链接已改指具体文件）
- [ ] 用户级联接用 PowerShell Junction 创建，未使用复制
- [ ] 已通过用户级路径回读 SKILL.md 验证联接生效
- [ ] 已审计各分类表头行数并记录/修正 HEAD 计数漂移
- [ ] 交付报告含双门原始命令与实测数值，可被他人复跑

## 参考

- 登记面模板与实测样例：[references/registration-surfaces.md](references/registration-surfaces.md)
- 真实入库案例：[references/case-skill-quality-gate.md](references/case-skill-quality-gate.md)
- 质量门掉分修复：`skill-quality-gate-remediation`；外部镜像归档：`skill-mirror-archive`

## 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-23 | 初始版本：前置探针、预览门、四处登记、双门验收、Junction 联接、漂移审计 |
