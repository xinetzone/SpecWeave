---
id: "open-code-review-wiki-03"
title: "使用流程与命令详解"
source: "../open-code-review-wiki.md#使用流程与命令详解"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/open-code-review-wiki/03-usage.toml"
---
# 使用流程与命令详解

Open Code Review 提供两套互补的评审命令：`ocr review` 面向变更（diff）的增量评审，`ocr scan` 面向完整文件的全量扫描。本章系统介绍两条命令的使用方式、关键参数与多阶段流程。

---

## ocr review 命令详解（diff 评审）

`ocr review` 针对**代码变更（diff）**进行评审，是日常开发工作流中最常用的命令。它支持三种变更来源：工作区、分支对比、单次提交，并可通过 `--background` 注入需求背景信息。

### 基本用法

```bash
# 工作区模式 —— 评审所有暂存、未暂存和未追踪的变更
ocr review

# 分支对比 —— 比较两个引用之间的 diff
ocr review --from main --to feature-branch

# 单次提交 —— 评审指定提交的变更
ocr review --commit abc123

# 附带需求背景 —— 评审变更是否正确实现了需求
ocr review --background "实现用户登录的手机号验证逻辑"
```

### 常用参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--repo` | 当前目录 | Git 仓库根目录 |
| `--format` | `text` | 输出格式：`text` 或 `json` |
| `--concurrency` | `8` | 最大并发评审文件数 |
| `--timeout` | `10` | 并发任务超时（分钟） |
| `--audience` | `human` | `human`（展示进度）或 `agent`（仅输出摘要） |
| `--background` | — | 需求背景描述 |
| `--preview`、`-p` | — | 预览将被审查的文件列表 |

---

## ocr scan 全量扫描模式

`ocr scan` 针对**完整文件**进行评审——它不依赖 diff，而是直接读取并审查整份源码。相比 `ocr review` 的增量视角，`ocr scan` 适用于需要全局视野的场景。

### 适用场景

- **审计陌生代码库：** 新接手一个项目，想快速摸清潜在风险点。
- **迁移/重构前体检：** 在大规模改造之前，对目标目录做一次全量缺陷扫描。
- **无有意义 diff 的目录：** 例如初始化导入的存量代码、长期未评审的历史模块。

### 支持非 Git 目录

`ocr scan` 同样适用于**非 Git 目录**——当目标目录不是 Git 仓库时，会自动回退到文件系统遍历，并遵守 `.gitignore` 的排除规则。

### 使用示例

```bash
# 扫描整个仓库（不指定 --path 时的默认行为）
ocr scan

# 扫描单个目录
ocr scan --path internal/agent

# 扫描多个指定文件
ocr scan --path internal/agent/agent.go,internal/diff/scan.go

# 排除生成代码 / 测试文件
ocr scan --path internal --exclude '**/*_test.go,**/generated/**'

# 扫描非 Git 目录，并以 JSON 输出（包含 project_summary 字段）
ocr scan --repo /path/to/plain/dir --format json
```

---

## ocr scan 多阶段评审流程

为了在「全量」这一更大的扫描范围下保持效果与成本可控，`ocr scan` 在主评审循环之外引入了多个可选阶段。每个阶段都可以通过 CLI 参数单独跳过，便于在效果与成本之间灵活权衡。

### 四个阶段概览

| 阶段 | 作用 | 跳过参数 |
| --- | --- | --- |
| **1. Plan 阶段（逐文件）** | 在评审每个文件前，先让 LLM 制定结构化的评审计划，确保复杂文件不被遗漏 | `--no-plan` |
| **2. 批次评审（Batching）** | 将文件按策略归并为批次后并发评审 | 通过 `--batch` 控制 |
| **3. Dedup 阶段（批内去重）** | 每个批次评审结束后，对批内相似评论进行合并去重，降低噪声 | `--no-dedup` |
| **4. Project Summary 阶段（跨文件总结）** | 所有批次完成后，生成一份项目级的 Markdown 总结，提炼跨文件的共性问题与高风险热点 | `--no-summary` |

### 阶段详解

1. **Plan 阶段（逐文件）：** 在评审每个文件前，先让 LLM 制定结构化的评审计划，确保复杂文件不被遗漏。可用 `--no-plan` 跳过以节省一次 LLM 调用。
2. **批次评审（Batching）：** 将文件按策略归并为批次后并发评审，通过 `--batch` 控制：`by-language`（按语言/扩展名，默认）、`by-directory`（按一级子目录）、`none`（每个文件独立成批）。
3. **Dedup 阶段（批内去重）：** 每个批次评审结束后，对批内相似评论进行合并去重，降低噪声。可用 `--no-dedup` 跳过。
4. **Project Summary 阶段（跨文件总结）：** 所有批次完成后，生成一份项目级的 Markdown 总结，提炼跨文件的共性问题与高风险热点。可用 `--no-summary` 跳过；JSON 输出中以 `project_summary` 字段返回。

---

## ocr scan 成本控制

由于全量扫描的范围远大于 diff 评审，`ocr scan` 内置了成本预估与预算上限能力，帮助开发者在调用 LLM 之前对开销心里有数。

### 成本控制机制

- **token 成本预估：** 每次运行前会打印一份粗略的 token 成本预估，让你在调用 LLM 前对开销心里有数。
- **`--preview`（`-p`）：** 在不调用任何 LLM 的情况下，先查看将被扫描的文件清单。
- **`--max-tokens-budget`：** 设置总 token 上限（input + output），一旦超出便停止调度新的批次，避免在大型仓库上失控消耗。

### 成本控制示例

```bash
# 先预览将被扫描的文件清单（不调用 LLM）
ocr scan --preview

# 扫描整个仓库，将开销限制在约 50 万 token 以内
ocr scan --max-tokens-budget 500000

# 最快速的扫描：跳过 Plan、Dedup 和项目总结三个阶段
ocr scan --no-plan --no-dedup --no-summary
```

---

## ocr scan 常用参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--path` | 整个仓库 | 逗号分隔的待扫描目录或文件（仓库相对路径） |
| `--exclude` | — | 逗号分隔的 gitignore 风格排除模式 |
| `--preview`、`-p` | `false` | 预览将被扫描的文件清单，不调用 LLM |
| `--max-tokens-budget` | `0`（不限） | 总 token 用量上限，超出后停止调度新批次 |
| `--no-plan` | `false` | 跳过逐文件的 Plan 预处理阶段 |
| `--no-dedup` | `false` | 跳过批内相似评论的去重阶段 |
| `--no-summary` | `false` | 跳过项目级总结阶段 |
| `--batch` | `by-language` | 批次策略：`none` / `by-language` / `by-directory` |
| `--format`、`-f` | `text` | 输出格式：`text` 或 `json` |
| `--model` | — | 覆盖本次扫描使用的 LLM 模型 |
| `--background`、`-b` | — | 需求/业务背景描述 |
| `--concurrency` | `8` | 最大并发扫描文件数 |
| `--repo` | 当前目录 | 待扫描的仓库或目录根 |
| `--rule` | — | 自定义 JSON 评审规则文件路径 |
