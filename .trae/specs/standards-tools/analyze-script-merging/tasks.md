# 脚本合并可行性分析 - The Implementation Plan (Decomposed and Prioritized Task List)

---
version: 1.0
---

## [/] Task 1: 脚本间依赖与调用关系深度分析
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 分析 26 个 Python 脚本之间的 import 依赖关系（谁 import 了谁）
  - 分析脚本在文档（README.md、AGENTS.md、.agents/ 下各 .md）中的被引用情况
  - 分析脚本在 CI（ci-check.ps1/ci-check.sh）和其他脚本中的 subprocess 调用关系
  - 识别脚本间的数据流依赖（一个脚本的输出是否是另一个的输入）
  - 识别 lib/ 共享库被各脚本使用的程度
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: 生成脚本依赖关系图（Mermaid flowchart），标注 import 关系和调用关系
  - `human-judgement` TR-1.2: 审查依赖关系是否完整，是否遗漏了间接依赖或文档引用
- **Notes**: 重点关注 finalize-atomization.py 如何调用其他脚本，以及 check-atomization-duplication.py 与 pattern-maturity-stats.py 的功能重叠

## [ ] Task 2: 7 个功能组合并可行性逐一评估
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 对初步识别的 7 个功能组逐一进行深度评估：
    1. 原子化工作流组（check-atomization-coverage.py、check-atomization-duplication.py、finalize-atomization.py、verify-atomization.py）
    2. 链接管理组（check-links.py、build-ref-index.py、check-move.py）
    3. Spec 检查组（check-spec-consistency.py、check-spec-format.py、generate-tests.py）
    4. 模式成熟度组（pattern-maturity-stats.py、scan-maturity-upgrades.py、check-atomization-duplication.py --verify-stats）
    5. 索引导航生成组（generate-nav.py、generate-dashboard.py、generate-apps-index.py、check-retrospective-index.py）
    6. 仓库合规检查组（check-gitignore.py、check-vendor.py、check-filename-convention.py、check-mermaid.py、check-role-permissions.py）
    7. 其他专项组（check-action-items.py、check-report-categorization.py、check-source-traceability.py）
  - 对每组从以下维度评分（1-5分）：
    - 功能内聚度（组内脚本是否服务于同一目标）
    - 数据耦合度（是否共享大量数据结构或处理流程）
    - CLI 一致性（参数风格、输出格式是否统一）
    - 执行频率相似度（CI/手动/一次性）
    - 合并后代码量（合并后单文件是否过大）
  - 同时评估 2 个 CI 脚本（ci-check.ps1/ci-check.sh）和 constants.py、README.md 的定位
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `human-judgement` TR-2.1: 每个组给出明确结论：合并/不合并/统一入口，并附评分表和核心理由
  - `human-judgement` TR-2.2: 不合并的组需说明"如果不合并，现状有什么问题、如何缓解"
- **Notes**: verify-atomization.py 是硬编码一次性脚本，需单独评估是否建议删除

## [ ] Task 3: 合并方案详细设计（建议合并的组）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 对 Task 2 中建议"合并"的每个分组，设计详细合并方案：
    - 目标文件名（含路径）
    - 子命令结构设计（argparse subparsers）
    - 参数映射表（原脚本参数 → 新脚本子命令参数）
    - 核心函数迁移计划（哪些函数移入新文件、哪些移入 lib/）
    - 向后兼容策略（薄包装脚本/别名/兼容层）
    - CI 脚本更新方案
    - 文档引用更新方案
  - 对建议"统一入口"的分组，设计统一入口脚本方案
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `human-judgement` TR-3.1: 每个合并方案包含子命令树状结构和参数映射表
  - `human-judgement` TR-3.2: 向后兼容策略明确说明"旧命令是否还能用、如何用"
  - `human-judgement` TR-3.3: 评估合并后单文件代码行数，不超过 500 行限制（超出则需二次拆分）
- **Notes**: 合并后单文件不得超过 500 行（项目硬规则），若超出需考虑拆分为子模块

## [ ] Task 4: 收益与风险量化评估
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 对每个合并建议计算/评估：
    - 可消除的重复代码行数（估算）
    - 可减少的脚本文件数量
    - 用户体验提升（命令记忆负担降低）
    - 维护成本变化（需维护的入口点数量）
  - 识别风险并分级：
    - 兼容性风险（现有命令失效）
    - 回归风险（功能逻辑在迁移中出错）
    - 调用方影响（文档、CI、其他脚本需要更新的引用数）
    - 过度合并风险（单文件职责过多）
  - 为每个风险给出缓解措施
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-4.1: 收益按高/中/低三级评估，附具体估算数字
  - `human-judgement` TR-4.2: 风险按高/中/低三级评估，每个风险附缓解措施
- **Notes**: 参考前一轮共享库重构的经验（消除约 280 行重复代码），本次合并主要收益是入口点简化而非代码去重

## [ ] Task 5: 生成最终分析报告
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4
- **Description**:
  - 将所有分析结果整合为一份完整的 Markdown 报告，输出到 `.trae/specs/standards-tools/analyze-script-merging/report.md`
  - 报告结构：
    1. 执行摘要（核心结论一览）
    2. 现状分析（脚本清单、CI 流程、依赖关系图）
    3. 功能分组与评估（7 组详细分析 + 评分表）
    4. 合并决策总表（每个文件的归宿：合并到/保留独立/废弃/统一入口）
    5. 详细合并方案（每个合并组的子命令设计、参数映射、兼容策略）
    6. 收益与风险评估
    7. 分阶段实施路线图（P0/P1/P2 + Mermaid Gantt/Pie 图）
    8. 开放问题与建议
  - 包含至少 2 个 Mermaid 图：
    - 合并前功能分组与依赖关系图（flowchart）
    - 合并后架构图（flowchart）
  - 所有文件引用使用相对路径，禁止 file:/// 绝对路径
- **Acceptance Criteria Addressed**: AC-6, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-5.1: check-links.py --path 报告所在目录，无断链
  - `programmatic` TR-5.2: check-mermaid.py --path 报告所在目录，Mermaid 语法正确
  - `human-judgement` TR-5.3: 报告结构完整、结论明确、可直接作为后续重构任务的输入
- **Notes**: 报告是本 Spec 的核心产出物，需经用户审核后才能进入实施阶段
