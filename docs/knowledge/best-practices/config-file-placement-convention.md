---
id: "config-file-placement-convention"
title: "配置文件放置治理与 .temp/ 临时文件约定"
source: ".trae/specs/standards-tools/config-file-placement-governance/spec.md"
x-toml-ref: ".meta/toml/.agents/docs/knowledge/best-practices/config-file-placement-convention.toml"
category: "best-practices"
tags:
  - file-placement
  - governance
  - sitecustomize
  - python-autoload
  - temp-lifecycle
  - convention
  - anti-pattern
date: "2026-07-18"
status: "active"
version: "1.0.0"
author: "SpecWeave Team"
summary: "SpecWeave 项目关键配置文件的标准存放路径、放置决策树、Python 自动加载约定（sitecustomize.py / .pth / PYTHONPATH 关系）、sitecustomize.py 曾被错放根目录的根因分析，以及 .temp/ 临时文件的用途分类、命名规则、保留期与清理机制。"
---

# 配置文件放置治理与 .temp/ 临时文件约定

## 概述

本约定沉淀自一次关键配置文件迁移复盘：`sitecustomize.py`、`setup-utf8-env.ps1` 等文件曾被放在项目根目录，迁移到 `.agents/scripts/` 后需要明确放置规则，避免同类错误重发。同时覆盖 `.temp/` 临时文件的全生命周期治理，替代"靠记忆清理"的人工模式。

**适用范围**：
- 团队成员（开发者/智能体）新增任何配置文件、脚本、临时产物前的放置决策
- CI/预提交钩子对错误放置的自动检测依据
- `.temp/` 下任何中间产物的命名、保留期与清理

**溯源**：本约定由 [config-file-placement-governance spec](../../../../.trae/specs/standards-tools/config-file-placement-governance/spec.md) 落地，spec 中的 "Requirement: 文件放置治理文档" 定义了完整 Scenario。

---

## 一、关键配置文件标准路径表

下表列出受放置治理约束的关键配置文件。这些文件若被错误放回根目录，会导致自动加载失效或与 `.agents/scripts/` 版本冲突。

| 文件名 | 标准位置 | 用途 | 自动加载机制依赖 |
|--------|----------|------|------------------|
| `sitecustomize.py` | `.agents/scripts/sitecustomize.py` | Python 启动时由 `site` 模块自动执行，配置 UTF-8 编码环境（环境变量层 + 流重配置层 + 容错层三层防御） | Python `site` 模块自动加载；要求所在目录在 `sys.path` 中，通过 `PYTHONPATH` 包含 `.agents/scripts/` 实现 |
| `profile.ps1` | `.agents/scripts/profile.ps1` | 项目级 PowerShell 配置文件，设置控制台 UTF-8 编码并将 `.agents/scripts/` 注入 `PYTHONPATH`，使 `sitecustomize.py` 能被自动加载 | 由用户通过 `Install-Profile.ps1` 安装到 PowerShell Profile 后自动加载；亦可手动 `. ./.agents/scripts/profile.ps1` 加载 |
| `setup-utf8-env.ps1` | `.agents/scripts/setup-utf8-env.ps1` | Windows 终端 UTF-8 环境一键配置脚本，支持 Session/User/System 三种范围，可持久化 `PYTHONPATH` 到用户环境变量 | 由用户显式执行；`-Scope User` 模式下持久化 `PYTHONPATH`，新终端自动生效 |
| `setup-cmd-utf8.ps1` | `.agents/scripts/setup-cmd-utf8.ps1` | CMD 终端 UTF-8 环境配置脚本 | 由用户显式执行；通过 CMD AutoRun 注册持久化 |
| `Install-Profile.ps1` | `.agents/scripts/Install-Profile.ps1` | 将 `profile.ps1` 安装到用户 PowerShell Profile 的引导脚本 | 由用户显式执行一次 |
| `check-encoding.ps1` | `.agents/scripts/check-encoding.ps1` | 编码状态检查脚本，被 `setup-utf8-env.ps1` 调用 | 由 `setup-utf8-env.ps1` 显式调用 |
| `verify-encoding.ps1` | `.agents/scripts/verify-encoding.ps1` | 编码配置验证脚本 | 由用户或 CI 显式调用 |
| `verify-sitecustomize-autoload.py` | `.agents/scripts/verify-sitecustomize-autoload.py` | 验证 `sitecustomize.py` 在新终端会话中是否被 Python 自动加载 | 由用户或 CI 显式调用 |
| `check-file-placement.py` | `.agents/scripts/check-file-placement.py` | 检测关键配置文件是否被错误放置到项目根目录 | 由 CI/预提交钩子自动调用 |
| `check-temp-lifecycle.py` | `.agents/scripts/check-temp-lifecycle.py` | `.temp/` 生命周期检查与交互式清理 | 由 CI/预提交钩子或用户显式调用 |

> 💡 **规则**：上表中的文件**禁止**出现在项目根目录。`check-file-placement.py` 会扫描根目录，若检测到这些文件名出现于根目录，将以非零退出码退出并给出修复指引。

---

## 二、放置决策树

新增任何配置文件、脚本或文档时，按下图决策树判断标准位置。决策依据是**文件被谁/什么机制加载**，而非"放哪里最方便"。

```
                    ┌─ 新增文件 ─┐
                    │            │
                    ▼            ▼
        ┌──────────────────────────────────┐
        │ Q1: 文件是否由 Python site 模块   │
        │     或解释器约定自动加载？         │
        │     （如 sitecustomize.py、       │
        │      usercustomize.py、.pth）     │
        └──────────────┬───────────────────┘
                       │
            ┌──────────┴──────────┐
           是                    否
            │                     │
            ▼                     ▼
  ┌──────────────────┐   ┌────────────────────────────────┐
  │ 放 .agents/scripts/│   │ Q2: 文件是否是项目治理/规范     │
  │ 并通过 PYTHONPATH │   │     文档（best-practice/guide/ │
  │ 或 .pth 保证其    │   │     spec/retrospective 等）？   │
  │ 所在目录在 sys.path│   └──────────────┬─────────────────┘
  └──────────────────┘                  │
                              ┌─────────┴─────────┐
                             是                  否
                              │                   │
                              ▼                   ▼
                  ┌────────────────────┐  ┌────────────────────────────┐
                  │ 放 .agents/docs/   │  │ Q3: 文件是否是临时产物       │
                  │ 下对应子目录        │  │     （备份/实验/导出/截图）？│
                  │ （knowledge/       │  └──────────────┬─────────────┘
                  │  retrospective/    │                 │
                  │  rules/ 等）       │      ┌──────────┴──────────┐
                  └────────────────────┘     是                    否
                                              │                     │
                                              ▼                     ▼
                                  ┌────────────────────┐  ┌──────────────────────┐
                                  │ 放 .temp/{purpose}/ │  │ Q4: 文件是否是 CI/    │
                                  │ 并带日期或 task-id  │  │     预提交钩子、构建  │
                                  │ 命名                │  │     配置等项目根级    │
                                  └────────────────────┘  │     元配置？          │
                                                          └──────────┬───────────┘
                                                                    │
                                                            ┌───────┴───────┐
                                                           是              否
                                                            │               │
                                                            ▼               ▼
                                                  ┌──────────────────┐  ┌────────────────┐
                                                  │ 放项目根目录或   │  │ 默认放         │
                                                  │ 对应约定位置     │  │ .agents/scripts/│
                                                  │（如 .githooks/、 │  │ 或拒绝创建     │
                                                  │ .github/、       │  │ （需团队评审）  │
                                                  │ .trae/specs/）   │  └────────────────┘
                                                  └──────────────────┘
```

### 决策要点

| 问题 | 倾向根目录 | 倾向 `.agents/scripts/` | 倾向 `.agents/docs/` | 倾向 `.temp/` |
|------|-----------|------------------------|---------------------|---------------|
| 谁加载它？ | 外部工具按约定扫描根目录（如 `.gitignore`、`.git/`、`.githooks/`、`.github/`） | Python 解释器、PowerShell、CI 脚本 | 团队成员、智能体查阅 | 一次性任务产物 |
| 加载机制 | 工具硬编码扫描项目根 | `PYTHONPATH`、显式 `python <script>`、`. ./.agents/scripts/x.ps1` | 文档导航/链接 | 不被加载，仅暂存 |
| 生命周期 | 项目级长期 | 项目级长期 | 项目级长期 | 短期（3/7/14 天） |

> ⚠️ **反直觉提示**：`sitecustomize.py` 虽然是"Python 约定自动加载"的文件，但 Python 并未规定它必须在项目根目录——它只需在 `sys.path` 中。把 `.agents/scripts/` 加入 `PYTHONPATH` 即可让放在 `.agents/scripts/` 下的 `sitecustomize.py` 被自动加载，避免污染项目根目录。

---

## 三、Python 自动加载约定说明

### 3.1 三种自动加载机制的关系

Python 启动时（在执行用户代码前）会依次触发以下机制，本项目的 `sitecustomize.py` 依赖第一种：

| 机制 | 触发者 | 加载位置 | 本项目是否使用 |
|------|--------|----------|---------------|
| `sitecustomize.py` | Python `site` 模块（启动时自动 import） | `sys.path` 中第一个匹配的 `sitecustomize` 模块 | ✅ 使用，放 `.agents/scripts/`，通过 `PYTHONPATH` 注入 `sys.path` |
| `usercustomize.py` | Python `site` 模块（若启用 `-s` 之外的默认模式） | `site.ENABLE_USER_SITE` 对应的用户站点目录 | ❌ 未使用 |
| `.pth` 文件 | Python `site` 模块（启动时扫描 `site-packages` 等目录） | `site-packages/` 等 site 目录下的 `.pth` 文件，每行一个路径被追加到 `sys.path` | ❌ 未使用（项目无 `.pth` 文件） |
| `PYTHONPATH` 环境变量 | 操作系统/Shell 在启动 Python 前注入 | 启动时被追加到 `sys.path` 前部 | ✅ 使用，由 `profile.ps1` 或 `setup-utf8-env.ps1 -Scope User` 设置为包含 `.agents/scripts/` |

### 3.2 本项目的加载链路

```
┌─────────────────────────────────────────────────────────────────┐
│  新终端启动                                                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │ 用户曾运行 setup-utf8-env.ps1 -Scope User     │
        │ → 用户级环境变量 PYTHONPATH 已持久化          │
        │   包含 <项目根>/.agents/scripts/              │
        │ 或者：用户已加载 profile.ps1                  │
        │ → 当前会话 PYTHONPATH 临时包含 .agents/scripts/│
        └──────────────────────┬───────────────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │ 用户执行 python xxx.py                        │
        │ → Python 启动，site 模块运行                   │
        │ → sys.path 包含 .agents/scripts/（来自PYTHONPATH）│
        │ → site 模块自动 import sitecustomize          │
        │ → 加载 .agents/scripts/sitecustomize.py       │
        │ → 执行 _setup_utf8_environment()              │
        │ → 执行 _reconfigure_std_streams()             │
        │ → stdout/stderr 编码变为 utf-8                │
        └──────────────────────────────────────────────┘
```

### 3.3 验证方式

运行 [verify-sitecustomize-autoload.py](../../../scripts/verify-sitecustomize-autoload.py) 可复现地检查上述链路是否正常工作，覆盖三种场景：

1. **裸终端**（未加载 profile、未运行 setup 脚本）：脚本报告 `PYTHONPATH` 未包含 `.agents/scripts/`，`sitecustomize.py` 不会被自动加载，以非零退出码退出并提示修复方法
2. **已持久化 PYTHONPATH 的新终端**：脚本报告 `.agents/scripts/` 在 `sys.path` 中、`import sitecustomize` 成功且 `sitecustomize.__file__` 指向 `.agents/scripts/sitecustomize.py`、stdout/stderr 编码为 utf-8，以零退出码退出
3. **已加载 profile.ps1 的终端**：与场景 2 一致

详细 Scenario 见 [config-file-placement-governance spec](../../../../.trae/specs/standards-tools/config-file-placement-governance/spec.md) 的 "Requirement: sitecustomize.py 自动加载验证"。

---

## 四、根因分析：sitecustomize.py 为何曾被放到根目录

### 4.1 错放的原因（便利性驱动）

`sitecustomize.py` 原本被放在项目根目录，根本动机是利用 Python 的一个隐式约定：

> **Python 启动时，`sys.path[0]` 默认包含脚本所在目录或当前工作目录（cwd）。**

这意味着：如果用户在项目根目录执行 `python xxx.py`，`sys.path[0]` 就是项目根目录，Python `site` 模块在自动 `import sitecustomize` 时会直接命中根目录的 `sitecustomize.py`，**无需配置 `PYTHONPATH`、无需 `.pth` 文件、无需任何额外步骤**。

这种"零配置即可生效"的便利性，是 `sitecustomize.py` 被放到根目录的唯一合理动机。

### 4.2 错放的代价

| 代价 | 说明 |
|------|------|
| **根目录污染** | 项目根目录本应只保留项目级元配置（`.gitignore`、`.git/`、`.githooks/`、`AGENTS.md`、`README.md`、`.trae/`、`.agents/`、`docs/`、`vendor/` 等），把 Python 启动脚本放根目录破坏了这一约定 |
| **组织不一致** | `setup-utf8-env.ps1`、`profile.ps1`、`Install-Profile.ps1` 等配套脚本都在 `.agents/scripts/` 下，唯独 `sitecustomize.py` 在根目录，造成"配置文件分散在两处"的认知负担 |
| **与 `.agents/` 架构违背** | SpecWeave 的 `.agents/` 是 AI 智能体与脚本的统一容器（见 [AGENTS.md](../../../../AGENTS.md) 核心规范入口表），脚本类资产统一放 `.agents/scripts/` 是既定架构 |
| **`sys.path[0]` 不确定性** | `sys.path[0]` 实际是脚本所在目录，不是 cwd。用户从子目录执行 `python ../xxx.py` 时 `sys.path[0]` 不再是项目根，根目录的 `sitecustomize.py` 不会被加载——所谓"零配置"只在特定 cwd 下成立，并非真正可靠 |
| **多项目切换冲突** | 若多个项目都在根目录放 `sitecustomize.py`，从一个项目切到另一个项目时，旧的 cwd 仍可能命中错误的 `sitecustomize.py`，引发难以排查的编码问题 |
| **CI 环境失效** | CI 流水线通常不在项目根目录执行 Python，根目录的 `sitecustomize.py` 在 CI 中可能完全不生效，导致本地通过、CI 失败 |

### 4.3 迁移后的正确做法

迁移到 `.agents/scripts/` 后，自动加载通过**显式 `PYTHONPATH` 注入**实现，而非依赖 cwd 的隐式行为：

- [profile.ps1](../../../scripts/profile.ps1#L23-L31)：第 23-31 行明确将 `.agents/scripts/` 注入 `PYTHONPATH`
- [setup-utf8-env.ps1](../../../scripts/setup-utf8-env.ps1)：`-Scope User` 模式持久化 `PYTHONPATH` 到用户环境变量

**收益**：
- 自动加载不再依赖 cwd，从任何目录执行 Python 都能正确加载
- 配套脚本集中管理，组织一致
- 通过 [verify-sitecustomize-autoload.py](../../../scripts/verify-sitecustomize-autoload.py) 可复现验证，CI 与本地行为一致

### 4.4 经验沉淀

| 经验 | 含义 |
|------|------|
| **显式优于隐式** | `PYTHONPATH` 显式注入比 `sys.path[0]` 隐式命中更可靠、更可调试 |
| **架构一致性 > 短期便利** | 少写一行 `PYTHONPATH` 配置的便利，不足以抵消组织不一致带来的长期认知成本 |
| **可验证 > 可工作** | "在某种 cwd 下能工作"不等于"在所有场景下能工作"；显式机制可通过脚本验证全场景，隐式机制不能 |

---

## 五、团队操作流程

### 5.1 新增配置文件时的放置决策流程

团队成员（开发者或智能体）新增任何配置文件、脚本或临时产物前，必须执行以下步骤：

```
步骤 1：查阅决策树（本文第二节）
    │
    ▼
步骤 2：确定标准位置
    │
    ▼
步骤 3：创建文件到标准位置
    │
    ▼
步骤 4：运行放置校验
    python .agents/scripts/check-file-placement.py
    │
    ▼
步骤 5：若校验失败 → 按提示移动文件 → 回到步骤 4
    若校验通过 → 提交
```

### 5.2 新增关键配置文件的扩展流程

若新增的是**会被自动加载或被其他脚本依赖**的关键配置文件（如新的 `*.py` 启动模块、`.ps1` profile 脚本等），在步骤 2 之后还需：

1. **更新本约定第一节的"关键配置文件标准路径表"**：新增一行记录文件名、标准位置、用途、自动加载机制依赖
2. **更新 `check-file-placement.py` 的受管文件清单**：将新文件名加入扫描列表，使其被错误放置时能被自动检测
3. **必要时更新 `.gitignore`**：若文件是临时产物或包含敏感信息，按 `.temp/` 治理约定或 `.gitignore` 现有模式处理
4. **运行验证**：
   ```powershell
   python .agents/scripts/check-file-placement.py
   python .agents/scripts/verify-sitecustomize-autoload.py  # 若与 Python 自动加载相关
   ```

### 5.3 放置校验脚本使用

| 场景 | 命令 | 预期结果 |
|------|------|----------|
| 本地手动校验 | `python .agents/scripts/check-file-placement.py` | 所有受管文件位置正确 → 零退出码；存在错误放置 → 非零退出码并列出错误文件 |
| 预提交钩子触发 | （由 `.githooks/pre-commit` 自动调用） | 存在错误放置 → 提交被阻止并显示修复指引 |
| CI 质量门禁触发 | （由 CI 流水线调用） | 存在错误放置 → CI 失败 |

详细 Scenario 见 [config-file-placement-governance spec](../../../../.trae/specs/standards-tools/config-file-placement-governance/spec.md) 的 "Requirement: 关键配置文件放置校验"。

---

## 六、.temp/ 临时文件治理约定

### 6.1 定义与溯源

`.temp/` 是项目根目录下的临时文件目录，由 [.gitignore](../../../../.gitignore#L2) 第 2 行规则 `.temp/` 排除版本控制。

**语义**：`可随时清理`。存放任务执行过程中的中间产物，不保证持久性，任何脚本与团队成员均可在遵循本节规则的前提下清理其内容。

**溯源依据**：[.gitignore](../../../../.gitignore#L2) 第 1 行注释 `# 任务中间产物（.temp/ 为可随时清理的临时文件）` 与第 2 行规则 `.temp/` 共同确立了"可随时清理"的语义契约——本节约定将该语义转化为可执行的命名、保留期与清理规则，替代"靠记忆清理"的人工模式。

### 6.2 用途分类（按子目录组织）

`.temp/` 下必须按用途分目录组织，禁止在 `.temp/` 根级直接放文件（除非是未分类的临时文件，保留期更短，见 6.5）。

| 子目录 | 用途 | 典型内容 |
|--------|------|----------|
| `backup/` | 迁移/重构前的备份快照 | 目录迁移前的整体副本、批量重命名前的文件备份、元数据批量修改前的 toml mirror 备份 |
| `experiments/` | 实验性脚本（PoC、调试工具、一次性脚本） | 新算法 PoC、性能基准调试脚本、一次性数据探查脚本 |
| `exports/` | 临时数据导出 | 报告草稿、中间数据集、批量导出的 JSON/CSV |
| `screenshots/` | 调试截图、临时图片产物 | bug 复现截图、临时图表 PNG、UI 调试截图 |

### 6.3 命名规则

`.temp/` 下的子目录与文件名**必须**包含创建日期（`YYYYMMDD`）或关联 task-id。命名格式：

```
{purpose}/{task-id-or-date}-{描述}/        # 子目录形式（推荐用于成组产物）
{purpose}/{date}-{描述}.{ext}              # 单文件形式
```

**task-id 格式约定**：`task-{alphanumeric-hyphen}`，即以 `task-` 开头，后接字母数字与连字符组合（不区分大小写）。合规 task-id 示例：
- `task-abc123`（短 ID）
- `task-config-file-placement`（基于任务名的 kebab-case ID）
- `task-agent-app-marketplace-task3`（带阶段标识的复合 ID）

`check-temp-lifecycle.py` 通过正则 `task-[a-zA-Z0-9][a-zA-Z0-9-]*`（忽略大小写）识别 task-id 命名，命中即视为合规（基准日期回退取文件 mtime，因为 task-id 本身不含日期信息）。

**合规示例**：

```
.temp/backup/docs-migration-20260715/                    # 含日期的备份目录
.temp/backup/agent-app-marketplace-task3-20260718/       # 含 task-id + 日期的备份目录
.temp/experiments/color-palette-20260718/                # 含日期的实验目录
.temp/experiments/task-abc123/                           # 仅含 task-id 的实验目录（合规，基准日期取 mtime）
.temp/experiments/task-config-file-placement/            # 仅含 task-id 的实验目录（合规）
.temp/exports/20260718-spec-draft.md                     # 含日期的单文件
.temp/screenshots/20260718-encoding-bug.png              # 含日期的单文件
```

**不合规示例**（会被 `check-temp-lifecycle.py` 告警）：

```
.temp/record.md                  # 无用途前缀、无日期与 task-id
.temp/backup/old/                # 无日期与 task-id
.temp/experiments/test.py        # 无日期与 task-id
.temp/foo/                       # 非法用途前缀（不在 4 类之内）
```

> 💡 **task-id 与日期二选一即可**，但若使用 task-id，建议同时附日期（如 `docs-migration-20260715`）便于按时间排序与跨任务追溯。纯 task-id 命名（如 `task-abc123`）虽合规，但基准日期只能取文件 mtime，跨任务按时间筛选不如日期命名直观。

### 6.4 存储位置

临时文件**仅限**存放在项目根目录 `.temp/` 下，禁止散落到其他目录：

| 位置 | 是否允许 | 说明 |
|------|----------|------|
| `.temp/{purpose}/...` | ✅ 允许 | 唯一合法位置 |
| 项目根目录直接放临时文件（如 `d:\spaces\SpecWeave\tmp.md`） | ❌ 禁止 | 污染根目录，不被 `.gitignore` 排除 |
| `.agents/` 下放临时文件 | ❌ 禁止 | `.agents/` 是规范容器，非临时产物区 |
| `docs/` 下放临时文件 | ❌ 禁止 | `docs/` 是正式文档区 |
| `vendor/` 下放临时文件 | ❌ 禁止 | `vendor/` 是第三方依赖区 |
| `external/`、`playground/` | ⚠️ 不适用 | 这两个目录有独立语义（外部参考库、个人沙箱），不是 `.temp/` 的替代品，详见 [.gitignore](../../../../.gitignore#L10-L12) |

### 6.5 保留期

按用途分类设置保留期，超期内容由 `check-temp-lifecycle.py` 自动检测并提示清理：

| 用途分类 | 保留期 | 基准日期确定方式 |
|----------|--------|------------------|
| `backup/` | **3 天** | 优先取名称中的 `YYYYMMDD`；若无日期，取文件系统 mtime 回退 |
| `experiments/` | **14 天** | 同上 |
| `exports/` | **14 天** | 同上 |
| `screenshots/` | **14 天** | 同上 |
| 未分类根级文件（`.temp/foo.md` 等） | **7 天** | 同上 |

**保留期基准日期的确定**（来自 spec 的 "Scenario: 保留期基准日期的确定"）：
1. 优先取名称中解析出的 `YYYYMMDD` 日期
2. 若名称无日期但含 task-id，视为合规命名，基准日期取文件系统修改时间（mtime）回退
3. 若名称无日期也无 task-id，取文件系统修改时间（mtime）作为回退基准，并标记为不合规
4. `check-temp-lifecycle.py` 在输出中标注每项的基准日期来源（"名称解析"、"task-id" 或 "文件 mtime"）

### 6.6 清理机制

清理由脚本驱动，**不依赖人工记忆**。

| 操作 | 命令 | 行为 |
|------|------|------|
| 查看过期清单（只读） | `python .agents/scripts/check-temp-lifecycle.py` | 列出所有过期项及用途分类、创建日期、保留期、已存活天数；列出命名不合规项；按用途分组汇总；不删除任何内容 |
| 交互式清理 | `python .agents/scripts/check-temp-lifecycle.py --clean` | 先列出所有过期项并按用途分组展示，请求 `y/N` 确认后删除过期内容；保留未过期内容与命名不合规内容（不合规项需人工处理）；输出清理摘要（删除项数、释放空间 MB、剩余项数） |
| 自动化清理（谨慎） | `python .agents/scripts/check-temp-lifecycle.py --clean --yes` | 跳过确认，用于 CI/自动化场景 |
| 预提交钩子触发 | （由 `.githooks/pre-commit` 自动调用，只读模式） | 检测到超过 30 天的 `.temp/` 内容 → 提交被阻止并提示运行 `--clean` |
| CI 质量门禁触发 | （由 CI 流水线调用，只读模式） | 超过 14 天 → CI 报警告（不阻塞）；超过 30 天 → CI 报错误（阻塞流水线） |

**清理边界**：
- `--clean` 仅删除**过期**内容，保留未过期内容
- `--clean` **不删除**命名不合规内容（避免误删无日期但仍有用的产物），不合规项需人工重命名或手动删除
- `.temp/` 目录本身不删除（保留空目录供后续使用）

### 6.7 责任人

| 角色 | 职责 |
|------|------|
| **创建者**（开发者/智能体） | ① 按 6.3 命名规则正确命名；② 按 6.4 选择正确存储位置；③ 任务完成后主动运行 `check-temp-lifecycle.py --clean` 清理自己的产物 |
| **CI/预提交钩子** | ① 自动检测错误放置（`check-file-placement.py`）；② 自动检测过期内容（`check-temp-lifecycle.py` 只读模式）；③ 阻止超期 30 天的提交 |
| **项目维护者** | ① 定期审查 `.temp/` 整体规模与分布；② 在大版本/里程碑前组织统一清理；③ 审查命名规则与保留期是否仍符合实际工作流 |

---

## 七、反模式

以下反模式在 CI/预提交钩子或代码审查中应被拒绝：

| 反模式 | 危害 | 正确做法 |
|--------|------|----------|
| 在 `.temp/` 外放置临时文件（如根目录、`.agents/`、`docs/` 下放临时截图/草稿/备份） | 临时文件混入正式区，`.gitignore` 不覆盖，可能被误提交 | 一律放 `.temp/{purpose}/...` |
| 在 `.temp/` 下创建无日期无 task-id 的内容 | 无法计算保留期，回退到 mtime 导致清理不可预测；无法追溯归属 | 名称必须含 `YYYYMMDD` 或 task-id |
| 依赖人工记忆清理 `.temp/` | 遗忘导致 `.temp/` 无限膨胀；多人协作时无人负责 | 必须由 `check-temp-lifecycle.py` 驱动，CI 强制门禁 |
| 把 `sitecustomize.py` 放回项目根目录 | 短期"零配置"便利，长期造成根目录污染、组织不一致、cwd 依赖、多项目冲突、CI 失效（见第四节根因分析） | 放 `.agents/scripts/`，通过 `PYTHONPATH` 显式注入 |
| 把 `.pth` 文件放项目根目录期望自动加载 | `.pth` 文件只在 `site-packages` 等 site 目录被扫描，放根目录无效 | 通过 `PYTHONPATH` 注入 `.agents/scripts/` |
| 新增关键配置文件后不更新 `check-file-placement.py` 受管清单 | 新文件被错放时无法被自动检测 | 同步更新受管清单与本约定第一节路径表 |
| 修改 `.gitignore` 移除 `.temp/` 排除规则 | `.temp/` 内容会被 git 跟踪，"可随时清理"语义失效 | 保留 [.gitignore](../../../../.gitignore#L2) 第 2 行规则不动；若需调整清理策略，修改本约定或 `check-temp-lifecycle.py` |

---

## 关联资源

- **Spec 来源**：[config-file-placement-governance spec](../../../../.trae/specs/standards-tools/config-file-placement-governance/spec.md)
- **`.gitignore` 溯源**：[.gitignore](../../../../.gitignore#L2) 第 2 行 `.temp/` 规则
- **关键脚本**：
  - [sitecustomize.py](../../../scripts/sitecustomize.py)：UTF-8 自动加载模块
  - [profile.ps1](../../../scripts/profile.ps1)：PowerShell profile，注入 `PYTHONPATH`
  - [setup-utf8-env.ps1](../../../scripts/setup-utf8-env.ps1)：UTF-8 环境一键配置
  - [verify-sitecustomize-autoload.py](../../../scripts/verify-sitecustomize-autoload.py)：自动加载验证脚本
  - [check-file-placement.py](../../../scripts/check-file-placement.py)：放置校验脚本
  - [check-temp-lifecycle.py](../../../scripts/check-temp-lifecycle.py)：`.temp/` 生命周期检查与清理
- **相关 best-practices**：
  - [directory-migration-checklist.md](./directory-migration-checklist.md)：目录迁移五步法（本约定的文件迁移依据）
  - [cli-setup-in-agent-environment.md](./cli-setup-in-agent-environment.md)：IDE Agent 环境下 CLI 工具配置操作手册
- **架构参考**：[AGENTS.md](../../../../AGENTS.md) 核心规范入口表（`.agents/` 容器约定）

---

**变更记录**：

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0.0 | 2026-07-18 | 初始版本：关键配置文件路径表、放置决策树、Python 自动加载约定、sitecustomize.py 根因分析、团队操作流程、`.temp/` 全生命周期治理 | SpecWeave Team |
