---
name: user-level-skill-junction-delivery
version: 1.0.0
description: "当自动推荐要求在用户级技能根 ~/.qoder/skills 新建 Skill，而主权区 .agents/skills 已有同名且已通过质量门与链接门的权威副本、本轮又明确不做四处登记时，必须使用此技能：以目录联接而非复制交付，经目标路径复跑链接跟随、质量门、链接门、脚本帮助与 evals 解析，并用 git status 哈希证明未改工作树。当用户提到「在用户级新建」「装到 ~/.qoder/skills」「建联接不复制」「目录联接」「junction 交付」「为什么用户级没有这个技能」「经目标路径验证」时必须使用。不用于只读取证分诊（用 skill-recommendation-disk-triage）、四处登记（用 native-skill-surface-registration）、用户级迁入主权区（用 user-skill-sovereign-migration）或从零设计技能（用 skill-creator）。"
argument-hint: "<skill-name> [--target <user-level-path>]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/**/SKILL.md"
source: "会话 55d75850-2970-4739-b3f2-5226175d4a6f 的 shared-branch-merge-push-gate 交付实测：推荐 create 到用户级，主权区已有 100/100 权威副本且四处登记延后，最终以目录联接交付并经目标路径完成六项验收"
title: "用户级 Skill 目录联接交付"
x-toml-ref: "../../../.meta/toml/.agents/skills/user-level-skill-junction-delivery/SKILL.toml"
---

# 用户级 Skill 目录联接交付

推荐说「在用户级新建」，磁盘说「主权区已经有一份验收过的」。这时要交付的不是第二份内容，而是一条**指向权威副本的目录联接**，以及一组**经链接路径执行**的验证证据。

## 1. 适用与不适用

适用需三条同时成立：

1. 推荐或用户指定在 `~/.qoder/skills/<name>` 新建。
2. 主权区 `.agents/skills/<name>` 已有同名副本，并已通过质量门与链接门。
3. 用户在本轮**明确**表示不做四处登记，或登记明确延后。

| 场景 | 使用本技能 | 改用什么 |
|---|---|---|
| 已验收主权副本 + 登记延后 + 只补用户级可见性 | 是 | — |
| 判断推荐该新建、补登记还是改内容 | 否 | `skill-recommendation-disk-triage`（全程只读） |
| 需要同步 README/registry/CHANGELOG/TOML 四处面 | 否 | `native-skill-surface-registration` |
| 用户级实体目录迁入主权区 | 否 | `user-skill-sovereign-migration` |
| 内容还不存在，需要从零设计 | 否 | `skill-creator` |
| 质量门掉分需要修复 | 否 | `skill-quality-gate-remediation` |

> **为什么**三条要同时成立？少第一条就没有用户级目标；少第二条就没有可指向的权威副本，联接会悬空；少第三条就意味着登记仍在授权范围内，此时用 `native-skill-surface-registration` 一次做完更安全，单独做联接会把「已入库」与「已可见」拆成两个可能不同步的状态。

## 2. 交付判定决策树

```text
推荐 action=create，目标在 ~/.qoder/skills/<name>
├─ 主权区 .agents/skills/<name> 存在且双门达标？
│  ├─ 否 → 不是本技能：真新建用 skill-creator；用户级迁入用 user-skill-sovereign-migration
│  └─ 是 → 用户级目标现状？
│           ├─ 不存在 → 目录联接交付（本技能）
│           ├─ 已联接到同一处 → 幂等：跳过创建，只复跑验收
│           ├─ 联接到别处 → 停止，报告目标冲突
│           └─ 实体目录 → 停止，报告；不删除、不覆盖
└─ 本轮登记是否明确排除？
   ├─ 是 → 允许只做联接（本技能）
   └─ 否 → 登记在范围内：改用 native-skill-surface-registration 走完整管线
```

## 3. 交付前取证（只读，四步）

**步骤1：跨根查重并确认两个根的状态。**

```bash
ls -d ~/.qoder/skills/<name> 2>/dev/null
ls -d .agents/skills/<name> 2>/dev/null
```

推荐 JSON 通常只写用户级一个根，权威副本常在主权区。两个根都要看，再决定是新建、联接还是改道。

**步骤2：复验主权区副本。**

```bash
python .agents/scripts/check-skill-quality.py --path .agents/skills/<name> --score --threshold 100
python .agents/scripts/check-links.py --paths .agents/skills .agents/capability-registry --check-frontmatter-paths
```

要求质量门 100/100、退出码 0，链接门 0 断链。不达标先修内容或转修复技能，不要给未验收的副本建联接。

**步骤3：探测登记面与目标现状。**

```bash
git grep -l "<name>"
ls -la ~/.qoder/skills | grep "<name>"
```

登记零命中说明四处面尚未收录。目标路径已存在时，先用 PowerShell `Get-Item` 判断它是联接还是实体目录，再决定是否可以继续。

**步骤4：确认「本轮不做登记」来自用户的明确表述。**

用户只说了「建个 Skill」，不等于同意跳过登记；只有明确说「不做登记」「登记延后」「只建联接」才算。存疑就停下提问，不要替代用户缩小范围。

> **为什么**取证必须在写盘前完成？联接一旦创建，后续所有「已验证」的表述都会被理解为对交付整体的确认。先取证才能把「内容没问题」与「位置该不该建」分开判断。

## 4. 提案与确认门

写盘前输出下表并停下等确认：

| 项目 | 内容 |
|---|---|
| 推荐动作 | `create` 与目标目录 |
| 磁盘事实 | 主权区副本路径、双门分数、登记命中数、目标现状 |
| 改判结论 | 目录联接交付（不复制、不改写、不登记） |
| 唯一写入 | 在用户级根创建一个目录联接 |
| 明确不做 | 复制文件、改正文、四处登记、提交、推送 |
| 验收方式 | 第 6 节六项，全部经目标路径 |

用户只确认部分面时，只做被确认的部分，并在交付报告注明缺口。

> **为什么**提案要分开写「唯一写入」与「明确不做」？联接是写操作，但不改仓库内容。把两者混在一句「我来处理一下」里，用户无法判断授权边界，事后也说不清哪些是已批准范围。

## 5. 创建目录联接

先确认目标不存在，再用 PowerShell 创建：

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.qoder\skills\<name>" `
  -Target "D:\spaces\SpecWeave\.agents\skills\<name>"
```

- 目标目录必须已存在；指向不存在路径只会制造悬空联接。
- 不要用 `cmd /c mklink /J`：中文与长路径环境下输出乱码，失败难诊断。
- 不要用 `cp`/`Copy-Item`：复制产生两份真相，后续修改只落在其中一份。
- 不要向联接路径内复制内容（如 `cp -r src/. <target>/`）：写入会**穿透联接**落进主权区，等于在权威副本里再复制一份自己。
- 不要为了「干净」先删目标：实体目录可能是用户已有内容，删除需要单独授权。

> **为什么**用联接而不是复制？Qoder 从 `~/.qoder/skills` 发现技能，版本控制只覆盖 `.agents/skills`。联接让「可触发」与「可追溯」同时成立，并且只有一份内容。

## 6. 经目标路径验收

交付物是联接本身，所以验证必须在**目标路径**上执行；对源路径复跑只能证明内容，不能证明交付。

**步骤1：确认联接类型与目标，验证写入落在正确位置。**

```powershell
Get-Item "$env:USERPROFILE\.qoder\skills\<name>" | Select-Object LinkType, Target
```

期望 `LinkType: Junction`，`Target` 精确指向主权区同名目录。

**步骤2：经联接枚举文件，验证清单非空。**

```bash
find -L "$HOME/.qoder/skills/<name>" -type f | sort
```

`find` 默认不跟随联接，不加 `-L` 会返回 0 个文件；把「0 文件」当成空包会误判交付失败。

**步骤3：经联接复跑质量门，验证评分未因路径变化而降级。**

```bash
PYTHONDONTWRITEBYTECODE=1 python .agents/scripts/check-skill-quality.py \
  --path "$HOME/.qoder/skills/<name>" --score --threshold 100
```

期望 100/100、退出码 0。

**步骤4：经联接复跑链接门，验证 frontmatter 路径仍可解析。**

```bash
PYTHONDONTWRITEBYTECODE=1 python .agents/scripts/check-links.py \
  --path "$HOME/.qoder/skills/<name>" --check-frontmatter-paths
```

期望 0 断链、退出码 0。

**步骤5：经联接运行捆绑脚本与解析 evals，验证资源可执行。**

```bash
PYTHONDONTWRITEBYTECODE=1 python "$HOME/.qoder/skills/<name>/scripts/<script>.py" --help
PYTHONDONTWRITEBYTECODE=1 python -c "import json,pathlib;d=json.loads(pathlib.Path.home().joinpath('.qoder/skills/<name>/evals/evals.json').read_text(encoding='utf-8'));assert d['skill_name']=='<name>';print(len(d['evals']))"
```

技能没有 `scripts/` 或 `evals/` 时，在报告里写「不适用」，不要伪造通过。

**步骤6：证明未改工作树。**

```bash
git -C <repo> status --porcelain=v1 -z | sha256sum
```

在创建联接前与验收后各取一次，两个哈希必须一致。再检查运行残留：

```bash
find -L "$HOME/.qoder/skills/<name>" \( -name '__pycache__' -o -name '*.pyc' \) -print
```

> **为什么**要经目标路径复跑？用户级路径是 Qoder 的发现入口，源路径通过不代表联接可解析。只有经联接读到的文件、跑出的分数和退出码，才能证明「安装到位」。

> **为什么**用 `git status` 哈希而不是口头声明只读？联接创建在仓库外，但联接下运行 Python 可能写回 `__pycache__`。前后两次哈希一致是可复跑的客观证据，也顺手证明没有混入其他会话的改动。

## 7. 交付报告

| 项目 | 内容 |
|---|---|
| 联接 | 路径、`LinkType`、`Target` |
| 经联接可见文件 | 文件数、完整清单 |
| 质量门（目标路径） | 分数、通过项数、退出码、原始命令 |
| 链接门（目标路径） | 断链数、警告数、原始命令 |
| 脚本与 evals | `--help` 退出码、evals 场景数（或「不适用」） |
| 只读证明 | 创建前与验收后的 `git status` 哈希 |
| 未执行项 | 四处登记、提交、推送、内容改写 |

「未执行项」必须显式列出。把联接写成「已安装」会让人以为四处登记也完成了。

## 8. 幂等与重入

| 探针 | 状态 | 重入动作 |
|---|---|---|
| 用户级目标 | 不存在 | 创建联接 |
| 用户级目标 | 联接到同一权威副本 | 跳过创建，只复跑第 6 节 |
| 用户级目标 | 联接到别处 | 停止，报告冲突 |
| 用户级目标 | 实体目录 | 停止，报告；删除需单独授权 |
| 联接到目标 | 悬空或断链 | 停止，先修复目标再重建 |
| 双门 | 已达标且内容未变 | 不重复跑；怀疑被改才复跑 |
| 登记面 | 已登记 | 本技能不回滚登记，只核对联接状态 |

## 9. Gotchas

1. **`find` 不带 `-L` 什么都看不到**：Windows 目录联接在 Git Bash 里表现为符号链接，`find` 默认不跟随，输出为空不代表目录为空。
2. **`ls -la` 显示 `lrwxrwxrwx` 是正常的**：那是联接的表现，不是断链。用 PowerShell `Get-Item | Select LinkType, Target` 确认类型与目标。
3. **向联接内复制会写进主权区**：`cp`/`Copy-Item` 的目标是联接时，写入穿透到真实目录；这不是「复制到用户级」。
4. **联接不会自动创建目标**：`New-Item -ItemType Junction` 要求 `-Target` 已存在，否则得到悬空引用。
5. **`cmd /c mklink /J` 在本机不可靠**：中文与长路径下乱码、失败信息难读，统一用 PowerShell。
6. **质量门默认阈值不是验收线**：`--threshold 70` 的「通过」只表示没崩，验收用 `--score --threshold 100`。
7. **链接门传单个文件可能假通过**：扫到 0 个文件也会打印「通过」，验收要传目录并核对扫描文件数。
8. **Python 会经联接写 `__pycache__`**：在主权区留下运行残留会污染工作树；统一加 `PYTHONDONTWRITEBYTECODE=1`，并在验收后复查。
9. **`git grep` 只搜受追踪文件**：未提交的登记改动不会命中，零命中只能说明「已暂存/已提交的登记面没有它」。
10. **`~` 在 PowerShell 不展开**：PowerShell 用 `$env:USERPROFILE`，Git Bash 用 `$HOME`，不要在两者之间混用写法。
11. **实体目录不能直接换成联接**：那需要删除用户已有内容，属于单独授权事项；先报告，再等用户决定。
12. **联接删除只删链接本身**：`Remove-Item`/`rmdir` 不会删目标内容，但仍是可见性变更，需在授权范围内执行。

## 10. 安全检查清单（逐项确认）

- [ ] 已确认主权区副本存在且质量门 100/100、链接门 0 断链
- [ ] 已确认用户级目标不存在或指向同一处，未覆盖实体目录
- [ ] 已确认本轮不做登记由用户明确说明，未擅自改四处登记面
- [ ] 已确认创建命令为 PowerShell Junction，未使用复制或 mklink
- [ ] 已通过目标路径枚举文件，`find -L` 结果非空且与主权区一致
- [ ] 已通过目标路径复跑质量门与链接门，确认无断链
- [ ] 已确认脚本 `--help`（若有）退出 0，evals（若有）可解析
- [ ] 已验证 `git status` 哈希前后一致，工作树无残留
- [ ] 已确认无 `__pycache__`/`.pyc` 残留
- [ ] 交付报告已列明未执行项（登记/提交/推送/内容改写），无遗漏

## 参考

- 本次已验证案例：[references/verified-case.md](references/verified-case.md)
- 行为评估场景：[evals/evals.json](evals/evals.json)
- 上下游技能：`skill-recommendation-disk-triage`、`native-skill-surface-registration`、`user-skill-sovereign-migration`

## 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-24 | 初始版本：基于会话 `55d75850` 的联接交付实测，固化三条前置、决策树、只读取证、提案门、Junction 创建、经目标路径六项验收与只读哈希证明 |
