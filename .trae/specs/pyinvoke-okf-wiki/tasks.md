---
name: pyinvoke-okf-wiki-tasks
version: 1.0.0
created: 2026-08-21
spec: ./spec.md
---

# PyInvoke OKF Wiki - 实现任务队列

## Phase 1: R（Retrospective）— 事实采集

### Task 1: 源码深度阅读与事实采集
- **Priority**: high
- **AC Coverage**: AC-5（源码事实可追溯）
- **Status**: pending
- **Dependencies**: 无
- **Description**: 逐文件深度阅读 pyinvoke 核心源码，建立事实清单（F-001 起编号），每个事实为纯客观描述，无因果推断。
- **Read-first paths**:
  - `external/libs/pyinvoke/invoke/invoke/__init__.py`
  - `external/libs/pyinvoke/invoke/invoke/tasks.py`
  - `external/libs/pyinvoke/invoke/invoke/collection.py`
  - `external/libs/pyinvoke/invoke/invoke/context.py`
  - `external/libs/pyinvoke/invoke/invoke/config.py`
  - `external/libs/pyinvoke/invoke/invoke/executor.py`
  - `external/libs/pyinvoke/invoke/invoke/program.py`
  - `external/libs/pyinvoke/invoke/invoke/runners.py`
  - `external/libs/pyinvoke/invoke/invoke/loader.py`
  - `external/libs/pyinvoke/invoke/invoke/exceptions.py`
  - `external/libs/pyinvoke/invoke/invoke/parser/parser.py`
  - `external/libs/pyinvoke/invoke/invoke/parser/argument.py`
  - `external/libs/pyinvoke/invoke/invoke/watchers.py`
  - `external/libs/pyinvoke/invoke/invoke/terminals.py`
  - `external/libs/pyinvoke/invoke/invoke/util.py`
  - `external/libs/pyinvoke/invoke/invoke/env.py`
  - `external/libs/pyinvoke/invoke/sites/docs/getting-started.rst`
  - `external/libs/pyinvoke/invoke/sites/docs/concepts/`
- **Output**: `.trae/specs/pyinvoke-okf-wiki/facts.md` — 编号事实清单（≥30条，含类/方法签名、参数、行为、数据流）
- **Test Requirements**:
  - **TR-1.1** (rule): 事实数量 ≥ 30条
  - **TR-1.2** (rule): 事实无因果推断词（"因为"、"所以"、"导致"等），纯客观描述
  - **TR-1.3** (rule): 关键API签名、参数默认值、类继承关系等可验证信息完整
  - **TR-1.4** (rule): 每条事实标注来源文件路径

## Phase 2: I（Insight）— 洞察分析

### Task 2: 架构洞察与知识结构设计
- **Priority**: high
- **AC Coverage**: AC-1, AC-2, AC-3
- **Status**: pending
- **Dependencies**: Task 1
- **Description**: 基于事实清单，提炼 invoke 的核心架构洞察，设计 OKF bundle 的知识组织结构（概念分组、依赖关系、学习路径）。
- **Output**: `.trae/specs/pyinvoke-okf-wiki/insights.md` — 3条核心洞察（四元组：陈述/证据/反常识/行动）+ bundle 知识地图
- **Test Requirements**:
  - **TR-2.1** (rule): 洞察数量 ≥ 3条，每条含完整四元组
  - **TR-2.2** (rule): 洞察引用事实编号（F-xxx）作为证据
  - **TR-2.3** (rule): 知识地图覆盖 FR-6 至 FR-24 所有文档，标注概念间前置/依赖关系

## Phase 3: E（Extraction）+ V（Verification）— 萃取生成与对抗审查

### Task 3: 创建 Bundle 目录骨架
- **Priority**: high
- **AC Coverage**: AC-1
- **Status**: pending
- **Dependencies**: Task 2
- **Description**: 在 `projects/awesome-okf-xs/bundles/pyinvoke/` 创建 bundle 目录结构。
- **Output**:
  - `pyinvoke/index.md`（带 okf_version frontmatter）
  - `pyinvoke/log.md`
  - `pyinvoke/concepts/index.md`
  - `pyinvoke/examples/index.md`
  - `pyinvoke/references/index.md`
- **Test Requirements**:
  - **TR-3.1** (rule): 目录结构与 FR-1 至 FR-5 一致
  - **TR-3.2** (rule): 根 index.md frontmatter 包含 `okf_version: "0.2"`

### Task 4: 生成信源登记文档（references/）
- **Priority**: high
- **AC Coverage**: AC-4, AC-5
- **Status**: pending
- **Dependencies**: Task 3
- **Description**: 创建 references/ 下的信源登记文档。
- **Output**:
  - `pyinvoke/references/pyinvoke-source.md` — type: Reference，记录 pyinvoke 源码路径、版本信息
  - `pyinvoke/references/index.md` 更新
- **Test Requirements**:
  - **TR-4.1** (rule): frontmatter 含 type: Reference、sources 字段
  - **TR-4.2** (rule): 源码路径准确可访问

### Task 5: 生成入门与核心概念文档（concepts/00-04）
- **Priority**: high
- **AC Coverage**: AC-2, AC-4, AC-5
- **Status**: pending
- **Dependencies**: Task 4
- **Description**: 创建 concepts/00 至 04 共 5 个入门与核心概念文档。
- **Output**:
  - `pyinvoke/concepts/00-introduction.md` — type: Concept
  - `pyinvoke/concepts/01-getting-started.md` — type: Concept
  - `pyinvoke/concepts/02-task-basics.md` — type: Concept
  - `pyinvoke/concepts/03-context-object.md` — type: Concept
  - `pyinvoke/concepts/04-collection-namespace.md` — type: Concept
- **Test Requirements**:
  - **TR-5.1** (rule): 每个文件 frontmatter 合规（type、title、description、tags、sources、generated、status）
  - **TR-5.2** (rule): 技术声明可追溯到事实编号或源码
  - **TR-5.3** (rule): 代码示例语法正确
  - **TR-5.4** (rule): 文件大小在 500-5000 字符范围内

### Task 6: 生成进阶概念文档（concepts/05-08）
- **Priority**: high
- **AC Coverage**: AC-2, AC-4, AC-5
- **Status**: pending
- **Dependencies**: Task 5
- **Description**: 创建 concepts/05 至 08 共 4 个进阶概念文档。
- **Output**:
  - `pyinvoke/concepts/05-configuration.md` — type: Concept
  - `pyinvoke/concepts/06-runners.md` — type: Concept
  - `pyinvoke/concepts/07-cli-program.md` — type: Concept
  - `pyinvoke/concepts/08-execution-model.md` — type: Concept
- **Test Requirements**: 同 Task 5（TR-5.1 至 TR-5.4）

### Task 7: 生成高级主题文档（concepts/09-11）
- **Priority**: medium
- **AC Coverage**: AC-2, AC-4, AC-5
- **Status**: pending
- **Dependencies**: Task 6
- **Description**: 创建 concepts/09 至 11 共 3 个高级主题文档。
- **Output**:
  - `pyinvoke/concepts/09-watchers.md` — type: Concept
  - `pyinvoke/concepts/10-terminals-io.md` — type: Concept
  - `pyinvoke/concepts/11-advanced-patterns.md` — type: Concept
- **Test Requirements**: 同 Task 5（TR-5.1 至 TR-5.4）

### Task 8: 生成示例文档（examples/）
- **Priority**: high
- **AC Coverage**: AC-3, AC-4
- **Status**: pending
- **Dependencies**: Task 5
- **Description**: 创建 examples/ 下 5 个示例文档。
- **Output**:
  - `pyinvoke/examples/basic-task.md` — type: Example
  - `pyinvoke/examples/namespace-organization.md` — type: Example
  - `pyinvoke/examples/custom-cli.md` — type: Example
  - `pyinvoke/examples/file-watcher-automation.md` — type: Example
  - `pyinvoke/examples/testing-tasks.md` — type: Example
  - 更新 `pyinvoke/examples/index.md`
- **Test Requirements**:
  - **TR-8.1** (rule): 每个示例含完整可运行代码块
  - **TR-8.2** (rule): frontmatter 含 type: Example
  - **TR-8.3** (rule): 代码示例与概念文档交叉引用

### Task 9: 更新所有 index.md 导航文件
- **Priority**: high
- **AC Coverage**: AC-1, AC-6
- **Status**: pending
- **Dependencies**: Task 7, Task 8
- **Description**: 更新根 index.md 和各子目录 index.md，包含所有文档条目和简短描述。
- **Output**:
  - `pyinvoke/index.md` — 完整目录，含章节分组和文档描述
  - `pyinvoke/concepts/index.md` — 概念文档索引
  - `pyinvoke/examples/index.md` — 示例文档索引
  - `pyinvoke/references/index.md` — 信源索引
- **Test Requirements**:
  - **TR-9.1** (rule): 所有文档在 index.md 中均有条目
  - **TR-9.2** (rule): index.md 无 frontmatter（根 index.md 除外，仅含 okf_version）
  - **TR-9.3** (rule): 链接使用相对路径或 bundle-relative 路径

### Task 10: 交叉链接修复与验证
- **Priority**: high
- **AC Coverage**: AC-6
- **Status**: pending
- **Dependencies**: Task 9
- **Description**: 检查并修复所有文档间的交叉链接，确保无断链。
- **Output**: 修复后的完整 bundle
- **Test Requirements**:
  - **TR-10.1** (rule): 所有内部链接目标文件存在
  - **TR-10.2** (rule): 概念文档间有合理的相关概念链接

### Task 11: 萃取通用提示词模板和 workflow
- **Priority**: medium
- **AC Coverage**: AC-7
- **Status**: pending
- **Dependencies**: Task 10
- **Description**: 基于本次任务的经验，萃取「开源项目学习→OKF wiki 生成」的通用提示词模板和标准化 workflow。
- **Output**:
  - `.trae/specs/pyinvoke-okf-wiki/prompt-template.md` — 通用提示词模板
  - `.trae/specs/pyinvoke-okf-wiki/workflow.md` — 标准化 workflow
- **Test Requirements**:
  - **TR-11.1** (rule): 模板包含：角色定义、输入要求、输出结构、质量门检查清单、反模式警告
  - **TR-11.2** (rule): workflow 包含：R→I→E→V→C 各阶段的具体步骤、输入/输出、质量门
  - **TR-11.3** (rule): 模板和 workflow 不绑定 pyinvoke  specifics，可迁移到其他 Python 开源项目

## Phase 4: C（Close）— 交付与更新

### Task 12: 生成 log.md 更新日志
- **Priority**: medium
- **AC Coverage**: AC-1
- **Status**: pending
- **Dependencies**: Task 11
- **Description**: 创建/更新 log.md 记录 bundle 创建历史。
- **Output**: `pyinvoke/log.md`
- **Test Requirements**:
  - **TR-12.1** (rule): 日期标题使用 YYYY-MM-DD 格式
  - **TR-12.2** (rule): 条目按倒序排列

## Phase 5: Review（独立审查）

### Task 13: 独立审查与问题修复
- **Priority**: high
- **AC Coverage**: AC-8
- **Status**: pending
- **Dependencies**: Task 12
- **Description**: 执行四视角对抗审查（魔鬼代言人/新人/老板/未来），记录问题并修复 P0/P1 问题。
- **Output**: `.trae/specs/pyinvoke-okf-wiki/review.md` — 审查记录 + 修复后的 bundle
- **Test Requirements**:
  - **TR-13.1** (rule): 四个视角全部覆盖，审查意见 ≥ 5 条
  - **TR-13.2** (rule): 至少采纳 2 条意见对产出进行修正
  - **TR-13.3** (rule): 所有 P0 问题已修复，P1 问题有回应
  - **TR-13.4** (rule): 源码事实抽查（AC-5 rubric）得分 ≥ 1
  - **TR-13.5** (rule): 通用模板可复用性评估（AC-7 rubric）得分 ≥ 1

---

## 任务依赖图

```
Task 1 (事实采集)
  └─> Task 2 (洞察分析)
       └─> Task 3 (目录骨架)
            ├─> Task 4 (信源登记)
            │    └─> Task 5 (概念00-04)
            │         ├─> Task 6 (概念05-08)
            │         │    └─> Task 7 (概念09-11)
            │         │         └─> Task 9 (更新索引)
            │         └─> Task 8 (示例文档)
            │              └─> Task 9
            └─> (Task 4 之后并行其他)
Task 9 ─> Task 10 (交叉链接修复)
  └─> Task 11 (萃取模板)
       └─> Task 12 (log.md)
            └─> Task 13 (独立审查)
```
