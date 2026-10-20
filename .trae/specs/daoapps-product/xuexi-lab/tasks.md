# daoApps 学习产品站 — Implementation Plan

> 落点：`projects/daoapps.github.io/doc/xuexi/`；门禁：pytest + sphinx -W（py314 环境）。

## Task 1: 创建 xuexi 落地页 index.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 产品名「学以不教 · 学习实验室」落地页：痛点（AI 流畅陷阱）+ 三重命题卖点卡片（教是条件工程/学不可代理/输出驱动输入）+ CTA + 入口链接
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-1.1: 文件存在且含 toctree 注册后三页（checkup/cycle/playbook）

## Task 2: checkup.md 学习体检器（核心交互）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 10 道单选题，三维度（认知外包度/策略健康度/动机自主度）；JS 实时计分；SVG 雷达图 + 分级建议
  - 题目素材回溯知识包 08（认知外包）/04（循证策略）/07（SDT）
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: 含 10 题 + 计分函数 + SVG 渲染段
  - `rule` TR-2.2: 脚本挂 DOMContentLoaded

## Task 3: cycle.md 教学相长机制图
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 三重命题循环流程可视化（内联 SVG/div），节点可点击展开解释（知识包 05/06）
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 含三重命题节点 + 展开交互段

## Task 4: playbook.md 循证策略手册
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 检索/间隔/费曼/认知负荷四策略，可勾选 checklist + 何时用/何时不用（知识包 examples/02 交互化）
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 四策略齐全且含可勾选交互

## Task 5: dao.css 追加 .xx-lab 样式节
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1-4
- **Description**:
  - 新组件样式限定 `.xx-lab` 作用域，复用既有 token（--cinnabar 等），不覆盖主题规则
- **Acceptance Criteria Addressed**: NFR-5
- **Test Requirements**:
  - `rule` TR-5.1: 新样式全部以 `.xx-lab` 开头

## Task 6: 组织主页 toctree 注册
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - doc/index.md toctree 追加 `xuexi/index`，并加子站入口链接
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-6.1: 主页 toctree 含 xuexi/index（不破坏既有 jieban/index 断言）

## Task 7: 质量门验证
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - pytest tests -q 全绿；sphinx -W 零 warning；禁用词/帛书引文自查
- **Acceptance Criteria Addressed**: AC-2, AC-3, NFR-3
- **Test Requirements**:
  - `rule` TR-7.1: pytest exit 0
  - `rule` TR-7.2: sphinx -W exit 0 且 xuexi 页无 WARNING
