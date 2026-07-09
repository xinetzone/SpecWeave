---
version: 1.0
date: 2026-07-09
---

# Best-Practices 目录断链修复与入口文档建设 - The Implementation Plan

## [x] Task 1: 系统性扫描与断链识别
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 对 `docs/knowledge/best-practices/` 下所有 11 个 .md 文件执行全面的 retrospective 引用扫描
  - 使用 Grep 搜索所有包含 `retrospective` 的行（Markdown 链接、frontmatter source/related_retrospective 字段、正文路径提及）
  - 对每个引用的目标路径进行文件存在性验证（使用 os.path.exists 或 Glob）
  - 生成扫描结果清单（文件:行号 | 当前路径 | 目标是否存在 | 问题类型：路径深度错误/目标不存在/source字段过期/有效引用）
  - 输出格式：Markdown 表格，标注问题分类
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: Grep 扫描覆盖 best-practices 下所有 11 个 .md 文件，输出所有含 retrospective 的行（含行号）
  - `programmatic` TR-1.2: 对每个引用路径执行文件存在性检查，区分"有效"、"深度错误"、"目标不存在"、"frontmatter过期"四类
  - `programmatic` TR-1.3: 扫描清单包含至少以下文件中的引用：cli-setup-in-agent-environment.md、b2b-product-info-collection-sop.md、eight-dimensions-concurrent-safety-spec.md、concurrent-code-safety-review.md、mermaid-guide.md、multi-file-edit-reliability.md、parser-complexity-budget.md、pattern-validation-v3-template-batch-upgrade.md
  - `human-judgement` TR-1.4: 扫描清单无遗漏，分类准确，问题描述清晰可执行
- **Notes**: 重点关注 `../retrospective/`（单父目录）vs `../../retrospective/`（双父目录）的区别；best-practices 的路径深度是 docs/knowledge/best-practices/，到 docs/ 需要两级 `../`

## [x] Task 2: 修复所有确认的断链
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 根据 Task 1 的扫描清单，逐一修复所有断链：
    - **路径深度错误**：将 `../retrospective/` 修正为 `../../retrospective/`（从 best-practices 到 docs 需要两级）
    - **frontmatter source 字段过期**：更新为正确的溯源路径（指向文件当前位置而非旧 retrospective 路径）
    - **目标文件不存在/已归档**：若目标文件已被迁移/删除，将链接转为 inline code 格式（反引号包裹），或更新到文件新位置
    - **有效引用保持不变**：确认存在的 `../../retrospective/patterns/...` 和 `../../retrospective/reports/...` 链接不做修改
  - 修复 eight-dimensions-concurrent-safety-spec.md 更新记录中对压力测试报告的引用
  - 修复 b2b-product-info-collection-sop.md 的 defuddle-web-extraction-preferred 路径深度
  - 修复各文件 frontmatter 中过期的 source 字段
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: 运行 `python .agents/scripts/check-links.py --path docs/knowledge/best-practices` 返回 0 断链
  - `programmatic` TR-2.2: Grep 搜索 `../retrospective/`（单父目录）在 best-practices 下返回 0 结果（所有路径都应是 `../../retrospective/`）
  - `programmatic` TR-2.3: best-practices 内部互链（如 eight-dimensions 与 concurrent-code-safety-review 之间）均有效
  - `human-judgement` TR-2.4: frontmatter source 字段准确反映文件溯源，不残留过期的旧 retrospective 路径
- **Notes**: 使用 Edit 工具精确替换，避免影响正文内容；同一文件中多处修改使用 replace_all 或一次性 Edit

## [ ] Task 3: 创建 best-practices/README.md 入口文档
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 在 `docs/knowledge/best-practices/` 下创建 README.md，包含以下章节：
    1. **概述**（1-2段）：best-practices 目录定位——从实战复盘中沉淀的可复用最佳实践
    2. **核心方法：八维检查法**：1段话概述 + 8维度速览表格（维度名/代码/严重级别/一句话说明），基于 eight-dimensions-concurrent-safety-spec.md
    3. **关键应用场景**：3+ 个典型场景（并发代码提交前检查、多文件编辑操作、CLI工具配置、Mermaid图表编写、Parser开发等）
    4. **5分钟快速上手流程**：5步流程（了解八维法 → 选择场景指南 → 阅读对应最佳实践 → 使用Checklist → 提交前检查）
    5. **最佳实践文档索引**：按类别分组（代码质量与安全、工具与环境、文档工程、方法论验证）列出所有11个文档的链接和一句话摘要
    6. **延伸阅读**：指向 retrospective/patterns/ 模式库和 retrospective/reports/ 复盘报告的链接
  - 包含 YAML frontmatter（id、title、date、category、status）
  - 总行数控制在 200 行以内
  - 所有链接使用相对路径
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: README.md 文件存在于 docs/knowledge/best-practices/README.md
  - `programmatic` TR-3.2: 总行数 ≤ 200
  - `programmatic` TR-3.3: 所有链接为有效相对路径，无 file:/// 绝对路径（通过 check-links.py 验证）
  - `programmatic` TR-3.4: 包含必需章节：概述、八维检查法、应用场景、上手流程、文档索引、延伸阅读
  - `human-judgement` TR-3.5: 新成员阅读 README 后5分钟内能理解八维检查法基本原理和使用方法
  - `human-judgement` TR-3.6: 文档索引覆盖所有11个 best-practices 文件，分类合理
- **Notes**: 参考 docs/knowledge/README.md 的索引风格；八维表格基于 eight-dimensions-concurrent-safety-spec.md 中的八维规则详解表格精简

## [ ] Task 4: 更新 knowledge/README.md 索引
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 更新 `docs/knowledge/README.md` 中 best-practices 部分：
    - 修正条目数量（当前显示8个，实际11个文档+README）
    - 添加缺失的文档条目（eight-dimensions-concurrent-safety-spec.md、git-hook-chain-architecture.md、ai-anthropomorphic-crisis-intervention-implementation.md 等）
    - 添加 best-practices/README.md 的入口链接
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: knowledge/README.md 中 best-practices 分类下包含所有11个文档+README的链接
  - `programmatic` TR-4.2: 链接均为有效相对路径
  - `human-judgement` TR-4.3: 摘要描述准确反映文档内容
- **Notes**: 如果自动生成索引的脚本存在，考虑使用脚本更新而非手动编辑；需检查 docs/knowledge/scripts/generate_index.py 是否负责生成此文件

## [ ] Task 5: 更新 CHANGELOG.md
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 在根目录 `CHANGELOG.md` 的 `<!-- changelog -->` 标记后新增条目
  - 条目格式：`- 2026-07-09 | docs | description`
  - 描述内容包含：
    - 背景：best-practices 目录从 retrospective 迁移后遗留断链问题
    - 范围：修复11个文件中的断链（路径深度错误/frontmatter过期）
    - 优化：新增 README 入口文档（八维检查法5分钟上手指南）、同步更新 knowledge 索引
    - 影响：提升文档可发现性，消除导航断链，新成员上手效率提升
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: CHANGELOG.md 在 <!-- changelog --> 后新增条目，日期为2026-07-09
  - `programmatic` TR-5.2: 条目标题格式正确（`- YYYY-MM-DD | docs | ...`），使用中文描述
  - `human-judgement` TR-5.3: 描述清晰完整，包含背景、范围、优化内容、影响
- **Notes**: 参考既有条目风格（如2026-07-07的docs条目），保持简洁但信息完整

## [ ] Task 6: 链接修复验证（自动化检查）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 运行完整链接验证：`python .agents/scripts/check-links.py --path docs/knowledge/best-practices --fix`
  - 运行 knowledge 目录链接验证：`python .agents/scripts/check-links.py --path docs/knowledge`
  - 确认无 file:/// 绝对路径
  - 确认无 `../retrospective/` 深度错误
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: check-links.py 在 best-practices 目录返回 0 errors
  - `programmatic` TR-6.2: check-links.py 在 knowledge 目录不引入新的断链
  - `programmatic` TR-6.3: Grep 搜索 `file:///` 在 best-practices 下返回 0 结果
- **Notes**: 如果 check-links.py 支持 --fix 自动修复，使用之；否则手动修复发现的问题

## [x] Task 7: 执行完整复盘流程
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 使用 retrospective-cmd 技能执行标准化复盘流程：
    1. **事实收集**：统计变更文件数、修复断链数、新增文件数、代码行数变化
    2. **过程分析**：分析本次文档迁移修复过程中的经验与教训（哪些环节顺利、哪些踩坑）
    3. **洞察萃取**：提炼3-5个关键洞察（如"文档迁移后frontmatter source字段是高频遗忘点"、"路径深度心算不可靠需工具验证"等）
    4. **最佳实践沉淀**：形成文档迁移后链接修复的标准化操作指南（Checklist形式）
    5. **后续行动计划**：提出2-3个可执行的改进项
  - 导出复盘报告至 `docs/retrospective/reports/task-reports/retrospective-best-practices-link-fix-20260709/` 目录
  - 报告包含 README.md（执行概要）和 insight-extraction.md（洞察萃取）
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-7.1: 复盘报告目录存在，包含 README.md
  - `programmatic` TR-7.2: 报告包含事实统计、过程分析、洞察萃取、最佳实践、行动计划五个章节
  - `human-judgement` TR-7.3: 洞察具有可复用价值，最佳实践可操作，行动计划具体可执行
- **Notes**: 遵循项目既有复盘报告模板和命名规范；使用 retrospective-cmd 技能辅助生成
