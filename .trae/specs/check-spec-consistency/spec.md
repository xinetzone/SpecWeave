# 规格文档一致性检查工具 Spec

## Why

项目中 `spec.md`、`tasks.md`、`checklist.md` 三者之间存在逻辑关联与交叉引用关系。当 `spec.md` 变更时（如新增需求、修改场景、删除需求），`tasks.md` 和 `checklist.md` 可能不同步，导致规格与任务/检查清单不一致。当前缺乏自动化检测机制，依赖人工逐项核对，效率低且易遗漏。需要开发 `check-spec-consistency.py` 脚本，自动检测三份文档之间的一致性，输出差异报告与修复建议。

v1.0 已实现基础检查功能，但在实际运行中暴露出三个问题：语义匹配阈值固定导致中文短文本匹配率低、路径引用基于项目根目录解析导致误报、复盘类 spec 中"自引用数据"与"外部引用数据"混淆导致数据一致性检查误报。v1.1 针对这三类问题进行优化。

v1.1 中元文档识别采用关键词检测（"复盘"、"回顾"等），存在假阳性/假阴性风险。v1.2 将元文档识别升级为"显式标记优先 + 关键词兜底"的双层策略，消除关键词检测的误判风险。

## What Changes

- 新增 `.agents/scripts/check-spec-consistency.py`：规格文档一致性检查脚本（v1.0 已完成）
  - 解析 `spec.md` 提取需求列表、场景列表、关键数据引用
  - 解析 `tasks.md` 提取任务/子任务列表、依赖关系
  - 解析 `checklist.md` 提取检查类别、检查点列表
  - 交叉验证：需求 → 任务覆盖、场景 → 检查点覆盖、引用数据一致性
  - 输出差异报告（缺失项、多余项、不一致项）
- 新增 `.agents/scripts/README.md`：脚本目录说明（v1.0 已完成）
- **v1.1 优化**：修改 `.agents/scripts/check-spec-consistency.py`
  - 语义匹配阈值从固定 2 改为可配置（`--match-threshold`，默认 1）
  - 路径引用解析从项目根目录改为 spec 所在目录
  - 数据一致性检查区分"自引用数据"与"外部引用数据"，仅对自引用数据报错
  - 修复当前 spec.md 自身的数据引用不一致
- **v1.2 优化**：修改 `.agents/scripts/check-spec-consistency.py`
  - 元文档识别从"纯关键词检测"升级为"显式标记优先 + 关键词兜底"
  - 新增 `detect_meta_document()` 函数，替代 `is_retrospective_context()`
  - 支持 `<!-- meta_type: xxx -->` HTML 注释作为显式标记（零误判）
  - 未找到显式标记时回退到关键词检测（保持向后兼容）
  - 为 `retrospective-agents-spec-system/spec.md` 添加显式标记

## Impact

- Affected specs: 无（修改工具脚本，不修改现有 specs）
- Affected code: 仅 `.agents/scripts/check-spec-consistency.py`
- 与现有 `.agents/scripts/check-gitignore.py` 的关系：同属自动化验证脚本，放在同一目录下，命名风格一致

## ADDED Requirements

### Requirement: 需求 → 任务覆盖检查

系统 SHALL 解析 `spec.md` 中的 ADDED/MODIFIED/REMOVED Requirements 章节，提取所有需求标题，与 `tasks.md` 中的任务描述进行语义匹配，检测是否存在未被任何任务覆盖的需求。

#### Scenario: 需求有对应任务

- **WHEN** `spec.md` 中定义了 "Requirement: AGENTS.md 全局契约"
- **AND** `tasks.md` 中存在 "Task 1: 创建 AGENTS.md 全局契约文件"
- **THEN** 检查通过，该需求被视为已覆盖

#### Scenario: 需求无对应任务

- **WHEN** `spec.md` 中定义了某个需求
- **AND** `tasks.md` 中不存在语义匹配的任务
- **THEN** 输出警告："需求 XXX 在 tasks.md 中无对应任务"

### Requirement: 场景 → 检查点覆盖检查

系统 SHALL 解析 `spec.md` 中各需求下的 Scenario 列表，提取所有场景标题，与 `checklist.md` 中的检查点进行语义匹配，检测是否存在未被任何检查点覆盖的场景。

#### Scenario: 场景有对应检查点

- **WHEN** `spec.md` 中定义了 "Scenario: 智能体启动路由"
- **AND** `checklist.md` 中存在语义匹配的检查点
- **THEN** 检查通过，该场景被视为已覆盖

#### Scenario: 场景无对应检查点

- **WHEN** `spec.md` 中定义了某个场景
- **AND** `checklist.md` 中不存在语义匹配的检查点
- **THEN** 输出警告："场景 XXX 在 checklist.md 中无对应检查点"

### Requirement: 关键数据引用一致性检查

系统 SHALL 从 `spec.md` 中提取关键数据引用（如任务数量、子任务数量、检查类别数量、检查点数量、文件产出数量），与 `tasks.md` 和 `checklist.md` 的实际统计数据进行比对，检测数据不一致。

#### Scenario: 数据引用一致

- **WHEN** `spec.md` 引用 "9 个主任务、42 个子任务"
- **AND** `tasks.md` 实际包含 9 个主任务、42 个子任务
- **THEN** 检查通过，数据一致

#### Scenario: 数据引用不一致

- **WHEN** `spec.md` 引用 "9 个主任务"
- **AND** `tasks.md` 实际包含 10 个主任务
- **THEN** 输出错误："数据不一致：spec.md 引用 9 个主任务，但 tasks.md 实际包含 10 个"

### Requirement: 需求变更检测

系统 SHALL 支持对比两个版本的 `spec.md`（或通过 git diff 检测变更），识别新增、修改、删除的需求，并输出受影响的 tasks.md 和 checklist.md 条目。

#### Scenario: 检测新增需求

- **WHEN** `spec.md` 中新增了一条 Requirement
- **THEN** 输出提示："新增需求 XXX，建议在 tasks.md 中添加对应任务，在 checklist.md 中添加对应检查点"

#### Scenario: 检测删除需求

- **WHEN** `spec.md` 中删除了一条 Requirement
- **THEN** 输出提示："删除需求 XXX，建议检查 tasks.md 和 checklist.md 中是否残留相关条目"

### Requirement: 结构化输出报告

系统 SHALL 以结构化的格式输出检查结果，包含通过项、警告项、错误项三类，并给出具体的修复建议。

#### Scenario: 输出格式

- **WHEN** 执行检查脚本
- **THEN** 输出应包含：检查摘要（通过 X 项，警告 Y 项，错误 Z 项）、警告详情（每项含文件路径、行号、问题描述、修复建议）、错误详情（每项含文件路径、行号、问题描述、修复建议）

### Requirement: 脚本可独立运行

系统 SHALL 确保脚本可从项目根目录或任意位置独立运行，支持命令行参数指定 spec 目录路径，并返回非零退出码当存在错误时。

#### Scenario: 默认路径运行

- **WHEN** 在项目根目录执行 `python .agents/scripts/check-spec-consistency.py`
- **THEN** 脚本自动扫描 `.trae/specs/` 下所有 spec 目录，逐一检查

#### Scenario: 指定路径运行

- **WHEN** 执行 `python .agents/scripts/check-spec-consistency.py --spec-dir .trae/specs/create-agents-md-and-config`
- **THEN** 脚本仅检查指定 spec 目录下的三份文档

#### Scenario: 错误时返回非零退出码

- **WHEN** 检查发现不一致项（错误级别）
- **THEN** 脚本返回退出码 1

## MODIFIED Requirements

### Requirement: 需求 → 任务覆盖检查

系统 SHALL 解析 `spec.md` 中的 ADDED/MODIFIED/REMOVED Requirements 章节，提取所有需求标题，与 `tasks.md` 中的任务描述进行语义匹配，检测是否存在未被任何任务覆盖的需求。语义匹配阈值通过 `--match-threshold` 参数控制（默认 1，即至少 1 个共同关键词视为匹配）。

#### Scenario: 需求有对应任务（阈值 1）

- **WHEN** `spec.md` 中定义了 "Requirement: 角色定义体系"
- **AND** `tasks.md` 中存在 "Task 3: 编写角色定义文件"
- **AND** `--match-threshold` 为 1（默认）
- **THEN** 关键词「角色」「定义」至少 1 个匹配，检查通过

#### Scenario: 需求有对应任务（阈值 2）

- **WHEN** `spec.md` 中定义了 "Requirement: 角色定义体系"
- **AND** 使用 `--match-threshold 2`
- **THEN** 关键词「角色」「定义」仅 2 个匹配，检查通过（恰好满足阈值）

#### Scenario: 需求无对应任务

- **WHEN** `spec.md` 中定义了某个需求
- **AND** `tasks.md` 中不存在语义匹配的任务
- **THEN** 输出警告："需求 XXX 在 tasks.md 中无对应任务"

### Requirement: 关键数据引用一致性检查

系统 SHALL 从 `spec.md` 中提取关键数据引用，与 `tasks.md` 和 `checklist.md` 的实际统计数据进行比对。数据引用分为两类：**自引用数据**（引用当前 spec 自身的任务/检查点数量）和**外部引用数据**（引用其他 spec 或外部项目的数据，如复盘类 spec 中引用被复盘项目的数据）。自引用数据不一致标记为**错误**，外部引用数据不一致标记为**警告**。

系统通过以下双层策略区分元文档：
1. **显式标记优先**（v1.2 新增）：检查 spec.md 中是否存在 `<!-- meta_type: xxx -->` HTML 注释标记，存在则直接判定为元文档
2. **关键词兜底**：未找到显式标记时，检查 spec.md 中是否存在"复盘"、"回顾"、"审计"、"评审"等关键词，存在则判定为元文档

#### Scenario: 显式标记识别（v1.2 新增）

- **WHEN** `spec.md` 第一行包含 `<!-- meta_type: retrospective -->`
- **THEN** 系统直接识别为元文档，无需关键词匹配，消除误判

#### Scenario: 关键词兜底识别

- **WHEN** `spec.md` 中未找到显式标记
- **AND** 包含"复盘"、"回顾"等关键词
- **THEN** 系统通过关键词识别为元文档（向后兼容）

#### Scenario: 自引用数据不一致

- **WHEN** `spec.md` 引用 "8 个主任务"
- **AND** `tasks.md` 实际包含 10 个主任务
- **AND** spec.md 未被识别为元文档
- **THEN** 输出错误："数据不一致：spec.md 引用 8 个主任务，但 tasks.md 实际包含 10 个"

#### Scenario: 外部引用数据不一致（元文档）

- **WHEN** `spec.md` 引用 "9 个主任务、42 个子任务"
- **AND** `tasks.md` 实际包含 2 个主任务
- **AND** spec.md 被识别为元文档（显式标记或关键词）
- **THEN** 输出警告："数据引用可能指向外部项目：spec.md 引用 9 个主任务，但当前 tasks.md 仅包含 2 个（元文档）"

## ADDED Requirements (v1.1)

### Requirement: 可配置语义匹配阈值

系统 SHALL 支持通过 `--match-threshold` 命令行参数控制语义匹配的最小共同关键词数量，默认值为 1。

#### Scenario: 默认阈值匹配

- **WHEN** 执行 `python check-spec-consistency.py`（不指定阈值）
- **THEN** 使用默认阈值 1，需求与任务有 1 个共同关键词即视为匹配

#### Scenario: 自定义阈值

- **WHEN** 执行 `python check-spec-consistency.py --match-threshold 2`
- **THEN** 需求与任务需至少 2 个共同关键词才视为匹配

### Requirement: 路径引用上下文感知解析

系统 SHALL 在检查交叉引用时，将 spec.md 中的相对路径基于 spec 所在目录（而非项目根目录）解析，减少因路径基准不一致导致的误报。

#### Scenario: spec 相对路径正确解析

- **WHEN** `spec.md` 位于 `.trae/specs/XXX/`，其中引用 `protocols/handoff.md`
- **THEN** 脚本应以 `.trae/specs/XXX/` 为基准解析为 `.trae/specs/XXX/protocols/handoff.md`，而非项目根目录下的 `protocols/handoff.md`

#### Scenario: 项目根目录路径仍以根目录解析

- **WHEN** `spec.md` 引用 `.agents/protocols/handoff.md`（以 `.agents/` 开头的路径）
- **THEN** 脚本识别为项目根目录相对路径，以项目根目录为基准解析

## ADDED Requirements (v1.2)

### Requirement: 元文档显式标记识别

系统 SHALL 支持通过 `<!-- meta_type: xxx -->` HTML 注释标记识别元文档，优先于关键词检测。标记可出现在 spec.md 的任意位置，推荐放在文件第一行。

#### Scenario: 显式标记优先

- **WHEN** `spec.md` 中包含 `<!-- meta_type: retrospective -->`
- **THEN** 系统通过 `detect_meta_document()` 返回 `(True, "explicit")`，不依赖关键词检测

#### Scenario: 无显式标记时关键词兜底

- **WHEN** `spec.md` 中不包含 `<!-- meta_type: -->` 标记
- **AND** 包含"复盘"关键词
- **THEN** 系统通过 `detect_meta_document()` 返回 `(True, "keyword")`

#### Scenario: 无标记无关键词

- **WHEN** `spec.md` 中既无显式标记，也无元文档关键词
- **THEN** 系统通过 `detect_meta_document()` 返回 `(False, "none")`

### Requirement: 扩展关键词覆盖

系统 SHALL 扩展元文档关键词列表，从原有的 5 个（复盘、回顾、被复盘、retrospective、回顾分析）扩展至覆盖更多元文档类型，包括审计、评审、评估、对比分析、迁移方案等场景。

#### Scenario: 审计类文档识别

- **WHEN** `spec.md` 中包含"审计"关键词
- **AND** 无显式标记
- **THEN** 系统识别为元文档

#### Scenario: 评估类文档识别

- **WHEN** `spec.md` 中包含"评估"关键词
- **AND** 无显式标记
- **THEN** 系统识别为元文档