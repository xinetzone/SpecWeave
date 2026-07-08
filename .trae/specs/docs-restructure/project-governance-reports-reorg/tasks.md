---
version: "1.0"
date: "2026-06-26"
status: "completed"
x-toml-ref: "../../../../.meta/toml/.trae/specs/docs-restructure/project-governance-reports-reorg/tasks.toml"
---
# project-governance 复盘报告系统性重组 - The Implementation Plan

## [x] Task 1: 创建主题子目录并迁移报告文件

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `docs/retrospective/reports/project-governance/` 下创建 5 个主题子目录：
    - `comprehensive-reviews/`
    - `documentation-governance/`
    - `tools-and-automation/`
    - `process-and-compliance/`
    - `archiving-and-migration/`
  - 按照 spec.md 中的主题分类体系，将 18 个报告目录和 1 个独立文件移动到对应主题子目录
  - 迁移映射关系：
    - comprehensive-reviews/: retrospective-comprehensive-20260623/, retrospective-project-comprehensive-20260625/, retrospective-specweave-full-project-comprehensive-20260626/
    - documentation-governance/: reports-duplication-optimization-report.md, retrospective-report-system-planning/, retrospective-readme-sync-and-brand-naming-20260624/, retrospective-insights-reorg-20260626/, retrospective-link-fix-depth-adjustment-20260626/, retrospective-mermaid-rendering-fix-20260626/
    - tools-and-automation/: retrospective-report-tool-entropy-nonlinear-optimization/, retrospective-report-code-wiki-generation/
    - process-and-compliance/: retrospective-report-create-apps-directory/, retrospective-report-suggestion-execution-and-pattern-import/, retrospective-session-agents-md-violation-20260624/
    - archiving-and-migration/: retrospective-export-20260623/, retrospective-zhujian-wudao-apps-archiving-20260625/, retrospective-xinet-content-extraction-archiving-20260625/, retrospective-specweave-demo-production-flow-20260625/
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: 5 个主题子目录全部存在
  - `programmatic` TR-1.2: 19 份报告（18目录+1文件）全部迁移至对应子目录，无遗漏
  - `programmatic` TR-1.3: project-governance 根目录下无遗留的平铺报告（仅保留子目录）
  - `programmatic` TR-1.4: 迁移的文件数量和内部文件数与迁移前一致
- **Notes**: 使用 PowerShell 的 Move-Item 命令迁移；注意 reports-duplication-optimization-report.md 是独立文件而非目录

## [ ] Task 2: 修复因迁移导致的相对路径引用

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 迁移后所有报告内部相对路径引用深度增加了一层（多了一个主题目录层级）
  - 需要修复以下类型的路径引用：
    - 同报告子模块间的互链（如 `execution-retrospective.md` → `../execution-retrospective.md` 或保持不变，取决于是否在同一目录内）
    - 报告间的交叉引用（如 `../other-report/` → `../../other-report/`）
    - 指向 patterns/、concepts/、frameworks/ 等上层目录的引用（如 `../../../patterns/` → `../../../../patterns/`）
    - 指向 docs/retrospective/README.md 的引用深度调整
  - 优先使用 `python .agents/scripts/check-links.py --fix --dry-run` 预览自动修复，再应用修复
  - 自动修复无法处理的手动调整
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: 运行 `python .agents/scripts/check-links.py --path docs/retrospective/reports/project-governance/` 结果为 0 断链
  - `programmatic` TR-2.2: 报告内部子模块互链（README.md → execution-retrospective.md 等）全部有效
  - `programmatic` TR-2.3: 跨报告引用路径正确
  - `programmatic` TR-2.4: 指向上层 patterns/concepts/frameworks 的引用路径正确
- **Notes**: 由于迁移增加了一层目录深度，大多数跨目录引用需要增加一个 `../`；同目录内引用（如 README.md 链接到同目录下的 execution-retrospective.md）不需要修改

## [ ] Task 3: 生成 project-governance/README.md 主题分类索引

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `docs/retrospective/reports/project-governance/README.md` 作为主索引
  - 内容包含：
    - TOML frontmatter（id, date, type）
    - 标题与简介：说明本目录存放项目治理类复盘报告，采用二级主题分类
    - 主题分类总览表：5个主题的名称、定义、报告数量
    - Mermaid 主题关系图：展示 5 个主题之间的逻辑关联
    - 各主题详细列表：每个主题下的报告清单与一句话简介
    - 目录结构树
    - 快速导航指南
  - 风格参照 docs/retrospective/README.md 的写法
- **Acceptance Criteria Addressed**: AC-4, AC-7
- **Test Requirements**:
  - `human-judgement` TR-3.1: 索引文档包含主题定义表、Mermaid 图、报告清单、目录树、导航指南五个核心部分
  - `human-judgement` TR-3.2: Mermaid 图表遵循安全编码五规则（无空行、文本加引号、subgraph用英文ID、边标签格式正确）
  - `programmatic` TR-3.3: 文档中所有指向子主题和报告的相对链接有效
  - `programmatic` TR-3.4: TOML frontmatter 格式正确
- **Notes**: Mermaid 图可采用 flowchart 或 mindmap 形式展示主题分类体系

## [ ] Task 4: 生成 5 个主题子目录的 README.md

- **Priority**: medium
- **Depends On**: Task 1, Task 3
- **Description**:
  - 为每个主题子目录创建 README.md：
    - comprehensive-reviews/README.md
    - documentation-governance/README.md
    - tools-and-automation/README.md
    - process-and-compliance/README.md
    - archiving-and-migration/README.md
  - 每个 README.md 内容包含：
    - TOML frontmatter
    - 主题名称与详细定义
    - 该主题下的报告列表表格（报告名、日期、一句话简介、子模块链接）
    - 返回上级索引的链接
  - 保持风格统一，简洁实用
- **Acceptance Criteria Addressed**: AC-5, AC-7
- **Test Requirements**:
  - `human-judgement` TR-4.1: 每个主题 README.md 包含主题定义和报告列表表格
  - `programmatic` TR-4.2: 所有指向报告目录的链接有效
  - `programmatic` TR-4.3: 每个报告的子模块链接（execution/insight/export）有效
  - `human-judgement` TR-4.4: 报告简介准确反映各报告核心内容
- **Notes**: 报告简介从各报告的 README.md 中提取核心信息，不需要重新编写

## [ ] Task 5: 更新 docs/retrospective/README.md 上层索引

- **Priority**: high
- **Depends On**: Task 1, Task 3
- **Description**:
  - 更新 `docs/retrospective/README.md` 中 project-governance 相关部分：
    - 更新目录树（添加 5 个二级主题子目录）
    - 更新报告计数：从"12 份 + 1 独立报告"更新为"19 份（5主题分类）"
    - 重写"项目治理系列"部分的描述，按主题分组列出报告
    - 修正报告数量统计
    - 添加指向二级主题索引的链接
  - 确保其他主题部分（atomization/insight-extraction/spec-system/roles-teams/competitive-analysis）不受影响
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-5.1: 目录树正确反映新的二级分类结构
  - `programmatic` TR-5.2: 报告计数更新为 19 份
  - `programmatic` TR-5.3: 所有报告列表中的链接指向正确的新路径
  - `human-judgement` TR-5.4: 按主题分组的描述清晰、与实际分类一致
- **Notes**: 需确保文档中所有引用 project-governance 下报告的路径都已更新到新位置

## [ ] Task 6: 全项目链接验证与最终检查

- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 运行全项目链接检查：`python .agents/scripts/check-links.py --path .`
  - 运行 Mermaid 语法检查：`python .agents/scripts/check-mermaid.py`
  - 修复验证中发现的任何残留断链
  - 检查是否有其他文件（如 AGENTS.md 路由表、其他复盘报告中的关联引用）引用了 project-governance 下报告的旧路径，如有则同步更新
  - 确认 reports-duplication-optimization-report.md 迁移后其内部引用是否正确
- **Acceptance Criteria Addressed**: AC-8, AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: 全项目 `check-links.py --path .` 结果为 0 断链
  - `programmatic` TR-6.2: `check-mermaid.py` 结果为 0 错误 0 警告
  - `programmatic` TR-6.3: 无文件引用旧路径（project-governance/ 下直接平铺的报告路径）
  - `human-judgement` TR-6.4: 整体目录结构清晰、分类合理
- **Notes**: 重点检查 AGENTS.md、其他主题复盘报告中对 project-governance 报告的"关联报告"引用
