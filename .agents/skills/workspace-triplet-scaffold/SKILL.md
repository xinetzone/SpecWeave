---
name: workspace-triplet-scaffold
version: 1.0.0
description: 为目录补齐 README.md、AGENTS.md 与 .agents/README.md 三件套并校验结果。当用户要求给某目录添加三件套、AGENTS 入口或工作区治理结构，或排查目录缺少智能体入口时，必须使用此技能。先判定区域与 gitignore 状态，再对齐既有范本，最后检查断链、启动协议关键词、嵌套优先级与 git 状态。不用于从零创建根工作区、普通 README 或创建 Skill。
argument-hint: "<目标目录> [<目标目录> ...]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/workspace-triplet-scaffold/**"
  - "**/README.md"
  - "**/AGENTS.md"
  - "**/.agents/README.md"
title: "工作区三件套补齐（Workspace Triplet Scaffold）"
x-toml-ref: "../../../.meta/toml/.agents/skills/workspace-triplet-scaffold/SKILL.toml"
metadata:
  source: "来源会话 3e23608a-835b-4346-adf5-2ec846d41320；external/playground 三件套落盘实证"
---

# Workspace Triplet Scaffold

## 1. 这个技能解决什么

三件套是同一个目录的三层入口，不是三份重复文档：

| 文件 | 读者 | 回答的问题 |
|---|---|---|
| `README.md` | 人 | 这里是什么、包含什么、怎么开始 |
| `AGENTS.md` | 智能体 | 进入后先读什么、守什么规则、边界在哪 |
| `.agents/README.md` | 智能体（元数据层） | 本区有哪些嵌套入口、与父级 `.agents/` 是什么关系 |

合并会同时坏掉三件事：README 被迫承载规则而变得不可读；AGENTS.md 膨胀成百科；子目录的既有入口被覆盖。本技能只负责**补齐与校验**，不负责从零设计整个根工作区。

不适用：

- 从零创建 SpecWeave 根工作区 → 用 `.agents/protocols/workspace-discovery.md` 的五步发现与最小可行子集。
- 判断公开/私域、决定产出物落 `docs/` 还是 `playground/` → 用 `.agents/rules/content-sensitivity-precheck.md`。
- 创建或更新 Skill 本身 → 用 `skill-creator`。
- 提交改动 → 用 `scoped-commit-shared-worktree`（共享工作树）或常规提交技能。

## 2. 不可协商规则

1. **先读后写**。目标目录已有 `README.md` / `AGENTS.md` 时，先读全文；用户没明确要求重写，就只做增补。
   > **为什么？** 既有 README 往往承载分类、命名、路径稳定性等长期约定，重写会把它们静默删掉。
2. **先判定区域，再决定能不能写**。`vendor/` 与 `projects/` 的子模块内容不可直接修改；`apps/` 可直接改；`external/`、`playground/` 被整目录忽略。判错区域会让写入落到错误的版本控制边界。
3. **先查 Git 状态，再承诺交付**。用 `git check-ignore -v` 与 `git ls-files` 确认目标是被忽略、已跟踪还是未跟踪；被忽略目录禁止 `git add -f`，也不得报告「已提交」。
   > **为什么？** 被忽略目录的改动不进版本库，说「已提交」会让用户误以为可以回滚；而 `git add -f` 会把私域内容和大文件强行塞进历史，事后清理代价极高。
4. **不复制父级规则**。子目录 AGENTS 只写本区差异与路由，父级规则用相对链接引用。复制会让两份规则漂移。
5. **嵌套优先必须显式**。目标下已有子级 `AGENTS.md` 时，根 AGENTS 必须声明「嵌套优先」，并在 `.agents/README.md` 登记入口清单。
6. **链接必须可解析**。Markdown 交叉引用一律相对路径；禁止 `file:///` 绝对路径；写完后逐条验证。
7. **目录清单来自实际输出**。结构树、成员列表、嵌套入口都从 `ls` / `find` 的真实结果生成，不凭记忆补全。
8. **失效引用只记录，不顺手修**。发现指向已归档/已移动路径的引用时，写进报告与 evidence，不擅自改无关文件。
9. **写盘前提案**。至少列出目标、判定区域、新增/修改文件、校验命令；用户确认后执行。

## 3. 输入与决策树

开始前写下来：

- `TARGETS`：要补齐的目录（可多个）。
- `ZONE`：区域定位（未知则按 Step 2 判定）。
- `MODE`：`create`（三件套都不存在）/ `augment`（README 或 AGENTS 已存在）。
- `VCS`：`ignored` / `tracked` / `untracked` / `not-a-repo`。

```text
目标目录
├─ 位于 vendor/ 子模块内？ ── 是 → 停止，不写（第三方边界）
├─ 位于 projects/ 子模块内？ ── 是 → 停止，走子项目流程
├─ 位于 apps/？ ── 是 → 可写；完成后交给提交技能
├─ 整体被 .gitignore 忽略？ ── 是 → 可写；报告「不可提交」，禁止 add -f
├─ 已有 README.md？ ── 是 → augment：顶部加 AI 入口 + changelog，保留既有章节
├─ 已有 AGENTS.md？ ── 是 → 仅在用户明确要求时更新，保留仍有效规则
└─ 其他 ── 按父级 AGENTS / 仓库约定判定；无约定则用最小可行子集
```

## 4. 五步流程

### Step 1 采集事实

```bash
ls -la <target>
find <target> -name AGENTS.md -not -path '*/.git/*' -not -path '*/node_modules/*'
find <target> -path '*/.agents/README.md' -not -path '*/.git/*'
git -C <target> rev-parse --show-toplevel
git -C <repo> check-ignore -v -- <target-rel>
git -C <repo> ls-files -- <target-rel> | wc -l
```

同时读父级 `AGENTS.md`（若存在），确认路由与内容敏感度规则。不要把父级全文抄进子目录。

### Step 2 判定区域与定位

| 区域 | 管理方式 | 可写 | 定位 |
|---|---|---|---|
| `apps/` | 主仓直接管理 | 是 | 内置应用 |
| `projects/` 子模块 | git submodule | 否 | 第一方子项目，走子项目流程 |
| `projects/` 主仓直接追踪的工作目录 | 同主仓 | 是 | 按该目录约定 |
| `vendor/` | git submodule | 否 | 第三方依赖 |
| `external/` | 整目录 gitignore | 是（本地） | 他人资料 + 工具链实验 |
| `playground/` | 整目录 gitignore | 是（本地） | 私域产出 |
| 独立 Git 仓库根 | 自带 `.git` | 是 | 仓库自身 README/AGENTS |
| 普通目录 | 无 | 是 | 按父级约定，默认最小三件套 |

> 非 SpecWeave 目录按 `git check-ignore` 与父级 `AGENTS.md` 约定判定；不要把上表的区域假设套到无关仓库。

### Step 3 对齐范本（按需读 1–2 个）

| 需求 | 范本 |
|---|---|
| 元数据容器 | `apps/.agents/README.md`、`projects/.agents/README.md` |
| 区域入口（启动协议/路由/规则/嵌套） | `external/AGENTS.md`、`playground/AGENTS.md` |
| 完整三件套 + 独立性 | `playground/huncheng-lab/` |
| 最小可行 AGENTS | `.agents/protocols/workspace-discovery.md` §5 |
| 根工作区模板 | `templates/agent-workspace-hub/` |

只读与当前区域最接近的 1–2 个，不要整读全部范本。

> 目标不在 SpecWeave 仓库内时，跳过本表的 SpecWeave 范本；按 Step 4 骨架与 `.agents/protocols/workspace-discovery.md` §5 的最小可行子集原则写，不要引用不存在的范本路径。

### Step 4 写或改

#### README.md

- **不存在**：定位 + 这是什么/不是什么 + 实际结构树 + 命名或归类 + 约束 + 关联 + Changelog。
- **已存在**：只在顶部加一行 AI 入口引用，在 Changelog 追加一条；不改既有分类、顺序、链接。
- 不把智能体规则写进 README。

#### AGENTS.md

必须含：

1. **启动协议**：读本文件 → 读父级 → 按路由表加载 → 嵌套优先 → 自检后工作。
2. **区域性质**：位置、版本控制状态、与相邻区域的边界。
3. **上下文路由表**：父级契约、核心规则、本区 README、`.agents/README.md`。
4. **工作规则**：只写本区差异（如 external 上游只读、playground 跳过 `.trae/specs/`）。
5. **嵌套入口**：有子级 AGENTS 时列出表格，并声明「其余同样嵌套优先」。
6. **边界与退出**：默认行为、禁止事项、离开后恢复父级路由。

#### .agents/README.md

只做元数据容器，不复制 roles/rules/workflows/protocols：

- 本目录用途（存什么、不存什么）；
- 实际目录结构；
- 嵌套工作区入口清单（与根 AGENTS 一致）；
- 与父级 `.agents/` 的关系表。

### Step 5 校验

在任意工作目录执行（`<skill-dir>` 是本 `SKILL.md` 所在目录）：

```bash
python "<skill-dir>/scripts/check_triplet.py" <target> [<target> ...] --strict
```

人工确认：

- `git status --short` 没有被忽略目录的文件；
- `git check-ignore -v` 仍命中预期规则；
- 没有创建 `.agents/docs/`；
- 报告区分「新增」「修改」「未验证」。

## 5. 完成标准

- 三个文件存在且非空；
- 每个 `AGENTS.md` 含「启动协议」；
- 相对链接 0 断链，0 个 `file:///`；
- 嵌套 AGENTS 已声明或已说明「无嵌套入口」；
- Git 状态已分类报告；被忽略目录没有声称可提交；
- 报告列出实际改动与遗留失效引用。

## 6. 反模式

| 反模式 | 后果 | 正确做法 |
|---|---|---|
| 直接覆盖已有 README | 丢失分类/路径约定 | 先读，增补 |
| 把父级 AGENTS 全文复制到子目录 | 两份规则漂移 | 只链接 |
| 对 gitignore 目录 `git add -f` | 私域/大文件进入版本库 | 报告不可提交 |
| 目录树凭记忆写 | 索引与事实不符 | 用 `ls`/`find` 输出 |
| 没跑命令就说「已校验」 | 断链与漏文件被掩盖 | 跑脚本并贴结果 |
| 顺手修复无关断链 | 扩大改动面、混淆责任 | 记录后另立任务 |
| 在已存在 AGENTS 的目录再造一套规则 | 覆盖子级自治 | 声明嵌套优先 |

## 7. Gotchas

1. **重跑会重复插入 AI 入口**。增补 README 前先 `grep` 既有入口行，已存在则跳过；重复追加会让文件顶部堆成入口列表。
2. **被忽略目录的改动不出现在 `git status`**。`external/`、`playground/` 整目录忽略，看不到变更不等于没写成功，必须用 `ls` / `stat` 直接确认文件存在与大小。
3. **脚本默认只扫 4 层**。`check_triplet.py --max-depth` 默认为 4，嵌套计数会少于 `find` 全量结果；报告数量时写明扫描深度，不要与 `find` 数字混用。
4. **嵌套声明按中文关键词判定**。根 AGENTS 必须同时出现「嵌套」与「优先」；只写英文 `nested priority` 会被判为未声明。
5. **代码块里的路径不参与校验**。链接检查会剥离围栏与行内代码，写在代码块中的相对路径不会报断链，需要人工另行确认。
6. **含空格路径依赖 `%20` 约定**。脚本会把 `%20` 解码为空格；手写链接需与之一致，否则解析结果与人工核对不一致。

> **为什么？** 这些陷阱都不报错：重复入口、静默忽略、少算嵌套、代码块漏检，只会让最终报告看起来完整而与事实不符。

## 8. 安全检查清单（逐项确认）

- [ ] 已读取目标目录既有 README/AGENTS，未在未确认时覆盖
- [ ] 区域归属与 Git 状态均由命令实测，未凭记忆判断
- [ ] 目录树与嵌套入口来自 `ls` / `find` 实际输出
- [ ] 写盘前列出新增与修改文件清单并取得确认
- [ ] 已运行 `check_triplet.py --strict` 且 0 错误
- [ ] 被忽略目录未执行 `git add -f`，未声称可提交
- [ ] 发现的失效引用已记录，未顺手修改无关文件

## 9. 关联

- 工作区发现与最小可行子集：`.agents/protocols/workspace-discovery.md`
- 内容敏感度预检：`.agents/rules/content-sensitivity-precheck.md`
- Skill 创建：`skill-creator`
- 共享工作树隔离提交：`scoped-commit-shared-worktree`
- 来源实证：[references/evidence-case.md](references/evidence-case.md)
- 校验脚本：[scripts/check_triplet.py](scripts/check_triplet.py)
