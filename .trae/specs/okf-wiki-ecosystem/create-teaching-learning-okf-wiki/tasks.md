# 「教与学」全面调研 → OKF Wiki 教程 Implementation Plan

> 目标 bundle：`projects/awesome-okf-xs/doc/bundles/zhexue/methodology/teaching-and-learning/`
> 状态：全部任务完成，Review R1 = pass（见 review.md）。

## Task 1: 创建 bundle 目录结构与子目录索引
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Acceptance Criteria Addressed**: AC-1, AC-9
- **Completion Evidence**:
  - `Test-Path` 确认 concepts/、examples/、references/ 三个子目录与三个子索引存在
  - 三个子索引均含 `{toctree}` 且列出全部内容文档
  - TR-1.1 / TR-1.2 通过

## Task 2: 概念文档 00-02（教、学、学习理论谱系）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Completion Evidence**:
  - 00/01/02 三篇落盘，frontmatter 均含 `type: concept` 与 sources（3-6 条/篇）
  - 00 篇含定义谱系表与第一性命题；01 篇含三要素与五范式谱系；02 篇含六范式对照与两次重心转移
  - TR-2.1 / TR-2.2 / TR-2.3（5/5）通过

## Task 3: 概念文档 03-05（教学法、循证学习策略、教与学关系）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Completion Evidence**:
  - 03/04/05 三篇落盘；05 篇含《学记》原文（教育部引例+陕师大双源）与"教学相长非自动发生"反例边界
  - TR-3.1 / TR-3.2 / TR-3.3（5/5）通过

## Task 4: 概念文档 06-08（本质、真需求、AI 时代）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Completion Evidence**:
  - 06/07/08 三篇落盘；06 篇含三重命题咬合关系图与对抗审查节；08 篇 AI 时代观点标注"观点/一方称"
  - TR-4.1 / TR-4.2 / TR-4.3（5/5）通过

## Task 5: 实操层 examples/（3 篇）
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Acceptance Criteria Addressed**: AC-7
- **Completion Evidence**:
  - 01 选型表（三步流程+失效自查）、02 手册（四策略执行步骤+何时用/不用）、03 双向自查清单（含红线）
  - TR-5.1 / TR-5.2 通过

## Task 6: 信源层 references/（4 篇）
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Acceptance Criteria Addressed**: AC-5
- **Completion Evidence**:
  - 01 中国教学论（含《学记》双源）、02 西方教育哲学（杜威）、03 学习科学（机构级）、04 AI 时代（观点/官方分层）
  - TR-6.1 / TR-6.2 通过

## Task 7: bundle 根 index.md 与 log.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2, 3, 4, 5, 6
- **Acceptance Criteria Addressed**: AC-1, AC-9
- **Completion Evidence**:
  - index.md frontmatter 含 `okf_version: "0.2"` + `type: bundle-index` + 计数（9/3/4）；toctree 经子索引覆盖全部 21 文件
  - log.md 日期倒序记录初版
  - TR-7.1 / TR-7.2 通过

## Task 8: 更新三级索引
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 7
- **Acceptance Criteria Addressed**: AC-8
- **Completion Evidence**:
  - methodology/index.md 3→4（toctree+列表表）；zhexue/index.md 补齐 methodology 导航行；bundles/index.md 650→651（frontmatter/计数行/mermaid 7→8/域节 7→8/分组表 3→4）
  - `check-bundles-index.py` exit 0 五面对账通过
  - TR-8.1 / TR-8.2 通过

## Task 9: 运行质量门验证
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 8
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Completion Evidence**:
  - `check-toctrees.py` exit 0（两次）；`check-bundles-index.py` exit 0（修复 650 计数行漂移后）；`check-utf8.py` exit 0
  - TR-9.1 / TR-9.2 通过

## Task 10: Sphinx 构建验证
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 9
- **Acceptance Criteria Addressed**: AC-3
- **Completion Evidence**:
  - py314 环境（sphinx 9.1.0）全量 `sphinx -b dummy -E doc _build/dummy` exit 0、"build succeeded"；325 warnings 均属既有束，无本束 ERROR/WARNING
  - TR-10.1 通过
