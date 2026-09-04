---
title: "Textualize 生态源码学习 → OKF Wiki 教程"
status: "draft"
---

# Textualize 生态源码学习 → OKF Wiki 教程 Spec

## Why

用户要求系统化学习 `external/dao/action/Textualize` 下全部 12 个子项目（Textualize 开源组织生态：rich/textual 及其卫星工具），并在 `projects/Textualize` 下产出 OKF v0.2 规范的结构化 Wiki 教程。直接"读源码写文档"会导致虚构 API、事实无溯源、结构混乱，必须走 source-code-to-okf-wiki 五阶段工作流（G0 预检 + R→I→E→V→C），由 seven-concepts-cmd 编排（场景4：知识沉淀，R→I→E 链路 + V 对抗验证）。

## 信源盘点（步骤0 预检输入）

12 个本地 git 克隆，均位于 `external/dao/action/Textualize/<repo>`（main 分支，2026-09-01 盘点）：

| 仓库 | 定位 | 深度分层 |
|------|------|---------|
| rich | 终端富文本渲染基础库 | 深度（deep） |
| textual | TUI 框架（构建于 rich 之上） | 深度（deep） |
| frogmouth | 终端 Markdown 浏览器 | 中度（medium） |
| toolong | 终端日志实时查看器 | 中度 |
| trogon | CLI 自动生成 TUI 表单 | 中度 |
| rich-cli | rich 的命令行工具 | 中度 |
| textual-dev | textual 开发辅助工具 | 中度 |
| textual-serve | textual 应用转 Web 服务 | 中度 |
| textual-web | textual 应用发布到浏览器 | 中度 |
| textual-demo | 官方演示应用 | 轻度（light，并入生态总览） |
| textual-key-recorder | 按键录制小工具 | 轻度（并入生态总览） |
| .github | 组织 profile README | 轻度（并入生态总览） |

**信源稳定性（G0）判定**：克隆位于工作区持久目录 `external/dao/action/Textualize/`（非 .chaos/.tmp/Temp 临时段），但均处于 main 浮动分支。处置：**不升级为 vendor 子模块**（用户指定信源即此目录），改为在 references/ 信源登记中逐仓库记录 **commit hash + 分支 + 盘点日期**，任务期间禁止 `git pull`（视为按盘点时 hash 固定的快照）。V 阶段运行 `check-source-path-stability.py` audit 验证引用路径无临时段。

## What Changes

- 新建 `projects/Textualize/` 单一 OKF Bundle（根 index.md + log.md + concepts/ + examples/ + references/），按文件名前缀分组各仓库内容
- R 阶段：逐仓库提取编号事实（F-xxx），产出 `<spec-dir>/facts-<repo>.md`（零推测）
- I 阶段：提炼 3-5 个核心洞察四元组 + 知识地图，产出 `<spec-dir>/insights.md`
- E 阶段（信源先行）：references/（12 仓库信源登记）→ concepts/ 分批（每批≤7文件）→ examples/ → index.md 最后
- V 阶段：Grep 级 API 真实性验证、计数断言复核、toctree 门禁、链接与 frontmatter 检查
- C 阶段：模式沉淀回顾（仅当用户要求时才做原子提交）

## Impact

- Affected specs: 无既有 capability 变更（纯新增知识产出）
- Affected code: 新增 `projects/Textualize/**`（约 50 个文档）；`.trae/specs/okf-wiki-ecosystem/textualize-okf-wiki/` 下 facts/insights 中间产物
- 不修改 `external/` 信源本身；不涉及 projects/ 子模块 gitlink 变更（Textualize 为普通目录，非 submodule）

## ADDED Requirements

### Requirement: Textualize OKF Bundle
系统 SHALL 在 `projects/Textualize/` 产出符合 OKF v0.2 规范的单一 Bundle，覆盖全部 12 个子项目，深度分层为 deep（rich/textual）/ medium（7 个卫星工具）/ light（3 个并入生态总览）。

#### Scenario: 深度仓库覆盖
- **WHEN** 读者查阅 rich 与 textual 概念文档
- **THEN** 每个深度仓库有 5-6 篇概念文档 + 2-3 篇示例文档，全部 API 引用可在信源 commit hash 对应代码中 Grep 命中

#### Scenario: 中度仓库覆盖
- **WHEN** 读者查阅 frogmouth/toolong/trogon/rich-cli/textual-dev/textual-serve/textual-web
- **THEN** 每个仓库有 2 篇概念文档（架构 + 核心用法），定位与依赖关系清晰

#### Scenario: 信源可追溯
- **WHEN** 审计任意文档的 sources 字段
- **THEN** 指向 references/ 下对应信源登记文件，其中含仓库路径、分支、commit hash、盘点日期

### Requirement: 质量门全通过
系统 SHALL 满足 G0-G4 质量门：事实零推测（G1）、洞察四元组完整（G2）、信源先行+分批+index最后（G3）、无虚构 API + 计数断言一致 + toctree 完整（G4）。

#### Scenario: V 阶段验证
- **WHEN** 执行独立验证
- **THEN** 文档中每个类名/方法名经 Grep 信源验证存在；每个"X个/Y份"数量陈述经 Glob/Grep 独立计数比对一致
