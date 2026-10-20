# daoApps 学习产品站 — Product Requirements Document

## Overview
- **Summary**: 基于「教与学」OKF 知识包（zhexue/methodology/teaching-and-learning），在 daoapps.github.io 站点下新建一个**可视化、流程化、可交互**的产品子站 `doc/xuexi/`，作为"AI 时代学习能力"主题的获客落地页 + 免费自检工具，支撑后续付费转化。
- **Purpose**: 把知识包的第一性原理（学不可代理 / 教是条件工程 / 输出驱动输入）、SDT 真需求框架、AI 时代认知外包洞察，转化为可被普通用户消费、可交互体验的产品页面，而非静态文档。
- **Target Users**: C 端学习者（大学生/知识工作者/终身学习者），痛点是"AI 用得越多越觉得自己学不会"。

## Goals
- 一个可交互的「学习体检」工具页：用户答题 → 三维度可视化报告 → 对应改进策略
- 一个机制图解页：三重命题与教学相长循环可视化、可展开
- 一个可勾选的循证策略手册页
- 产品落地页：价值主张 + 三卖点 + CTA（引导付费/联系，不收集信息、不设表单）

## Non-Goals
- 不做后端、不做用户账号系统、不收集表单数据（纯静态前端）
- 不改动组织主页 14 仓库卡片与结伴站任何内容
- 不接支付链接（CTA 仅文字引导，外部转化在站外完成）
- 不修改 conf.py 构建配置与 dao.js 既有行为

## Background & Context
- 知识包资产：`projects/awesome-okf-xs/doc/bundles/zhexue/methodology/teaching-and-learning/`（9 概念 + 3 实操 + 4 信源）
- 站点约束：Sphinx + MyST（`-W` 警告即失败）、契约测试 22 项、dao.css token 体系、禁用词全站扫描（感恩小队/民政局小分队/玩转AI变现）、版本守卫扫描《老子》引文
- 既有模式：`doc/jieban/`、`doc/fupan/` 两个子站均为「index + 子页面 + toctree 注册」结构
- 交互实现路径：myst `{raw} html` 内嵌 HTML+CSS+JS（无后端、无外部依赖）

## Functional Requirements
- **FR-1**: `doc/xuexi/index.md` 产品落地页：主标题 + 痛点陈述（AI 流畅陷阱）+ 三重命题卖点卡片 + CTA 按钮 + 体检工具入口
- **FR-2**: `doc/xuexi/checkup.md` 学习体检器：10 道单选题（认知外包度/策略健康度/动机自主度三维），JS 实时计分，输出 SVG 雷达图 + 分级文字建议
- **FR-3**: `doc/xuexi/cycle.md` 教学相长机制图：三重命题循环流程图（SVG 或 div），每节点可点击展开解释（对应知识包 05/06 篇）
- **FR-4**: `doc/xuexi/playbook.md` 循证策略手册：检索练习/间隔/费曼/认知负荷四策略的可勾选 checklist + 每策略"何时用/何时不用"
- **FR-5**: 组织主页 `doc/index.md` toctree 注册 `xuexi/index`

## Non-Functional Requirements
- **NFR-1**: `pytest tests -q` 全部通过（不破坏既有 22 项契约）
- **NFR-2**: `sphinx -b html -W --keep-going doc _build/html` 零 warning 构建成功
- **NFR-3**: 新页面不含禁用词（感恩小队/民政局小分队/玩转AI变现）、不含《老子》帛书引文（避免触发版本守卫）
- **NFR-4**: 交互脚本挂 DOMContentLoaded 闸门，无裸顶层 querySelector
- **NFR-5**: 新增组件样式限定在 `.xx-lab` 作用域内（参照 `.org-home` 隔离纪律）

## Constraints
- **Technical**: 纯静态（HTML/CSS/JS），myst raw fence；SVG 内联画图；无外部 JS 库
- **Business**: 不收集信息、不出现 `<form>` 与弹窗
- **Dependencies**: py314 环境（sphinx/pytest/myst-parser 已就绪）

## Assumptions
- 产品中文名暂定「学以不教 · 学习实验室」（叶圣陶"教是为了不教"化用），上线后可改
- CTA 文案："想系统提升？微信端联系"（与结伴站一致的无表单纪律）

## Acceptance Criteria

### AC-1: 新站结构完整
- **Type**: `rule`
- **Given**: 实施完成后
- **When**: 检查 doc/xuexi/ 目录
- **Then**: index.md / checkup.md / cycle.md / playbook.md 四文件存在，且 index.md toctree 注册后三页
- **Pass Condition**: 4 个文件存在 + toctree 含三页 + 组织主页 toctree 含 xuexi/index
- **Evidence**: 文件清单 + toctrees 检查

### AC-2: 契约测试全绿
- **Type**: `rule`
- **Pass Condition**: `python -m pytest tests -q` exit 0，无失败
- **Evidence**: pytest 输出

### AC-3: Sphinx -W 构建零警告
- **Type**: `rule`
- **Pass Condition**: `sphinx -b html -W --keep-going` exit 0，本站新增页面无 WARNING
- **Evidence**: 构建输出

### AC-4: 体检器可交互
- **Type**: `rule`
- **Pass Condition**: checkup.md 含 10 道单选题 + JS 计分逻辑 + 三维度报告渲染（SVG 雷达图），浏览器打开可答题出结果
- **Evidence**: 源码中含答题计分函数与 SVG 渲染段

### AC-5: 内容知识包溯源准确
- **Type**: `rubric`
- **Dimension**: 产品内容与知识包三重命题/SDT/AI 洞察的对应准确度
- **Scale**: 1-5
- **Anchors**: 1=泛泛鸡汤无出处；3=引用知识包概念但对应牵强；5=每个卖点/题目可回溯到知识包具体篇目（05/06/07/08）
- **Pass Threshold**: >= 4
- **Evidence**: 页面内文与知识包篇目对照表

### AC-6: 可视化与可交互性
- **Type**: `rubric`
- **Dimension**: 页面的可视化/流程化/可交互程度
- **Scale**: 1-5
- **Anchors**: 1=纯文字无图；3=有静态图；5=至少两处真正可交互（答题计分/展开/勾选）且有可视化图形（SVG 雷达/流程图）
- **Pass Threshold**: >= 4
- **Evidence**: checkup 答题交互 + cycle 展开交互 + playbook 勾选交互

## Open Questions
- 产品正式名称（spec 阶段暂定，实施中可改）
