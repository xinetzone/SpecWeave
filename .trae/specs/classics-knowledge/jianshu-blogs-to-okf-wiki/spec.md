---
title: "简书博文集 → OKF Wiki 教程"
status: "draft"
---

# 简书博文集 → OKF Wiki 教程 Spec

## Why

用户拥有三套简书连载博文集（matplotlib & pillow & networkx 手册、开源的世界、无人驾驶），内容为 2020 年前后的旧教程，已停止维护、散落在简书平台且格式零散。需要按 OKF v0.2 规范将其系统化为结构化中文 Wiki 教程，沉淀到 `projects/awesome-okf-xs/doc/bundles/` 知识包库的恰当位置，实现长期维护、交叉引用与检索。鉴于教程时点较旧（2020 年），文档须标注时点并对已过时的 API/做法给出现状校正说明。

## What Changes

- **新增 2 个 jishu 技术分组**（目录 + index.md + toctree）：
  - `jishu/dev/`（开发协作与版本控制）——承载 Git / GitHub / 开源实践
  - `jishu/autonomous/`（无人驾驶与机器人）——承载 Autoware / ROS2 / DDS / 数据集
- **新增约 10 个 OKF bundle**（每个含 `index.md` + `log.md` + `concepts/`，视内容加 `examples/`、`references/`）：
  - Notebook 1 → `jishu/data/pydata/networkx/`、`jishu/data/pydata/pillow/`，并**扩展现有** `jishu/data/pydata/matplotlib/`（补齐事件处理、patches/path、分形示例等缺口概念）
  - Notebook 2 → `jishu/dev/git/`、`jishu/dev/github/`、`jishu/dev/opensource/`
  - Notebook 3 → `jishu/autonomous/autoware/`、`jishu/autonomous/ros2/`、`jishu/autonomous/dds/`、`jishu/autonomous/ecosystem/`
- **索引同步**：更新 `jishu/index.md`、`jishu/data/index.md`、`doc/bundles/index.md` 总索引（束/组/域计数对账）。
- **时点标注与现状校正**：所有文档 frontmatter 标注内容时点（2020 年）；对明显过时的 API（如 networkx 1.x/2.x 绘制 API、matplotlib 老接口、ROS 1 残留）在文中给出「现状」说明，不虚构当代行为。
- **方法链路**：遵循 `source-code-to-okf-wiki` 的 R→I→E→V→C 五阶段（事实采集→洞察→分批生成→独立验证→模式沉淀），由 `seven-concepts-cmd` 编排质量门。

## Impact

- 受影响 bundle 库：`jishu/data/pydata/`（matplotlib 扩展、networkx/pillow 新增）、`jishu/dev/`（新分组）、`jishu/autonomous/`（新分组）、`doc/bundles/index.md` 总索引
- 受影响计数：总束数 389 → 增加约 10；`jishu` 分组数 12 → 14
- 受影响文件：`projects/awesome-okf-xs/doc/bundles/**`（仅新增与 matplotlib 扩展；不触碰并行会话未提交的 yixue/tcm、medicine 等文件）
- 不影响：SpecWeave 主权区 `.agents/`、`docs/`；不修改 OKF 规范本体

## ADDED Requirements

### Requirement: 信源采集与事实登记
系统 SHALL 抓取三个简书连载（nb/46194813、nb/40234132、nb/47487870）的全部文章正文，保存原始文本快照至 `.trae/specs/classics-knowledge/jianshu-blogs-to-okf-wiki/raw/`，并在 `facts.md` 中登记编号事实（F-xxx），每条事实标注来源文章 URL 与内容时点（2020 年前后），零推测。

#### Scenario: 成功采集
- **WHEN** 执行信源采集
- **THEN** 三套连载全部文章（约 34 篇）正文均被保存，facts.md 中每篇至少有 1 条可溯源事实

### Requirement: 束结构与放置恰当
系统 SHALL 依据主题内容将生成的知识包放置到 `doc/bundles/` 的恰当分组，新增分组遵循现有 jishu 分组命名与 index 规范。

#### Scenario: 放置校验
- **WHEN** 完成所有束生成
- **THEN** networkx/pillow/matplotlib 位于 `jishu/data/pydata/`，dev 与 autonomous 两个新分组位于 `jishu/` 且各自 index.md 含完整 toctree

### Requirement: OKF v0.2 文档规范
每个 bundle 的文档 SHALL 遵循 OKF v0.2 frontmatter（type/title/description/tags/generated/verified/status/stale_after/sources），子目录 index.md 不含 frontmatter，所有 index.md 含 `{toctree}` 块，交叉链接使用 `/` 开头 bundle-relative 路径。

#### Scenario: 格式校验
- **WHEN** 运行 `invoke gates.toctrees` 与 `sphinx-build`
- **THEN** 无断链、无孤立文档、无 toctree 遗漏、构建零错误零警告

### Requirement: 时点标注与现状校正
因教程为 2020 年旧文，文档 SHALL 在 frontmatter 或文首标注内容时点，并对已过时 API/做法给出「现状」校正说明；禁止把旧 API 当作现行 API 陈述，禁止虚构当代行为。

#### Scenario: 过时内容处理
- **WHEN** 文档涉及 networkx 2.x / matplotlib 旧接口 / ROS 1 等已过时内容
- **THEN** 文档明确标注「2020 年时点」并给出当前版本（如 networkx 3.x）的差异说明，且该说明有信源依据

### Requirement: 索引对账
新增束与分组后，总索引 `doc/bundles/index.md` 的 frontmatter/计数行/域节标题/分组表束数列/toctree 五面 SHALL 与目录树一致。

#### Scenario: 计数校验
- **WHEN** 运行 `invoke gates.bundles`
- **THEN** 束/组/域计数三角校验通过，无手工估算值

### Requirement: 原子提交与并行会话隔离
交付 SHALL 通过原子提交（add 与 commit 分两次，add 后核对暂存集），且不得触碰并行会话未提交的 yixue/tcm、medicine 等文件；若存在暂存区竞态，停止提交并如实报告。

#### Scenario: 提交校验
- **WHEN** 执行 git 提交
- **THEN** 暂存集仅含本任务新增/修改文件，提交信息为 Conventional Commits 中文主体，门禁全绿后交付

## MODIFIED Requirements

无（本任务不修改既有 bundle 的既有内容，仅对 matplotlib 束做增量扩展）。
