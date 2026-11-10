---
type: spec
title: "Coding Harness for General-Purpose Agents → OKF v0.2 知识包"
source_url: "https://www.thoughtworks.com/radar/techniques/coding-harness-for-general-purpose-agents"
status: completed
generated_at: "2026-11-10"
---

# Coding Harness for General-Purpose Agents → OKF v0.2 知识包

## Overview

把 Thoughtworks Technology Radar Vol 35 的 Trial 级 blip《Coding harness for general-purpose agents》转化为 `projects/awesome-okf-xs/doc/bundles/` 下的 OKF v0.2 知识包。按七概念方法论编排（`seven-concepts-cmd`）走**场景 4 知识沉淀链路 R→I→E→V→C**。

| 项 | 值 |
|---|---|
| 源文 URL | https://www.thoughtworks.com/radar/techniques/coding-harness-for-general-purpose-agents |
| 源文标题 | Coding harness for general-purpose agents |
| 发布方 | Thoughtworks Technology Radar |
| 发布信息 | 2026-11-04，Vol 35，Trial |
| 内容敏感度 | 公开内容（无访问控制、无邀请码） |
| 工作流 | 标准工作流（spec 在 `.trae/specs/`，产出在 `projects/awesome-okf-xs/doc/bundles/`） |
| 目标落点 | `projects/awesome-okf-xs/doc/bundles/jishu/ai/practice/coding-harness-general-purpose-agents/` |

## Goals

- G1：产出结构完整的 OKF v0.2 bundle，覆盖**定义层 / 入口层 / 运行时层 / 护栏层 / 成本层 / 采用层 / 雷达坐标层**。
- G2：所有事实挂 F 编号，spec `facts.md` 与 bundle `references/article-source.md` 双份登记且编号集合一致、连续无跳号。
- G3：P0 核验覆盖发布信息、四个编程入口、会话/无头能力、沙箱与审批、相关 blip 评级。
- G4：三级 toctree（bundle index → practice index → ai index → bundles/index）与计数全部接入且自洽。
- G5：frontmatter 完整、相对链接可达、UTF-8 strict roundtrip 通过、无敏感绝对路径。

## Non-Goals

- 不设 `examples/`：源文为观点型雷达条目，没有作者实测、可照做的安装/配置/代码/实测流程（操作可复现性两问均否）。
- 不做四家 harness 的横向 benchmark；不声称“某家更快/更便宜”。
- 不把 Thoughtworks 的 .NET 迁移案例当作可复现证据。
- 不把作者对 token 成本与编码偏向的经验判断写成量化事实。
- 不修改并发会话正在生成的 `claude-agent-sdk-production` 与 `agent-framework-selection-2026` 两个未跟踪 bundle。

## Background & Context

### 1. 信源与公开性预检

| 检查项 | 结论 |
|---|---|
| 内容性质 | 公开发布的技术雷达条目 |
| 访问控制 | 无 token / 邀请码 / 登录墙 |
| 信源距离 | 厂商/咨询机构观点，非独立实测；案例为厂商自述 |
| 时效性 | 雷达一年两期；SDK 能力变化快，`stale_after=2027-04-30` |

### 2. 骨架判定（操作可复现性两问）

1. 源文是否有读者可照做的安装/配置/代码/调用/实测流程？**否**。
2. 这些流程是否经作者实测、具备可复现性？**否**。

结论：不设 `examples/`。官方 SDK 的最小调用形状只放在概念文档中，标注“官方文档示例（节选）”，用于说明形态，不构成可复现实操教程。

### 3. 归属判定

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/practice/` | **选中** | 源文是行业洞察/技术趋势条目，不是源码教程；practice 已容纳多篇博文核验转化束 |
| `jishu/ai/frameworks/ai-agent/` | 未选 | 该组以框架/运行时源码教程为主；本束不提供源码级实现 |
| `jishu/ai/ecosystems/` | 未选 | 本束不以某厂商生态为主体，而是四家横向对照 |
| 新建分组 | 未选 | 单篇 blip 新建分组属过度工程 |

### 4. 三层知识拆分

| 层 | 文档 | 内容 |
|---|---|---|
| 定义与判断层 | 00、03 | 什么是 harness、与 framework 的取舍、护栏差异 |
| 机制与入口层 | 01、02 | 四个编程入口、循环/压缩/会话/无头执行 |
| 落地与坐标层 | 04、05、06 | 领域适配与成本、采用路径、雷达主题簇 |

## Deliverables

| 文件 | 说明 |
|---|---|
| `index.md` | bundle 根索引、核心结论、阅读路径、主题关联、核验摘要 |
| `concepts/00-what-is-a-coding-harness.md` | 定义与四层区分 |
| `concepts/01-four-programmatic-surfaces.md` | 四家入口对照 |
| `concepts/02-reused-runtime-capabilities.md` | 运行时四能力 |
| `concepts/03-guardrails-and-capability-differences.md` | 沙箱、审批、扩展 |
| `concepts/04-domain-fit-and-hidden-costs.md` | 编码偏向、token、评测 |
| `concepts/05-adoption-playbook.md` | 五步采用、评分卡、迁移 |
| `concepts/06-radar-context-and-related-blips.md` | Vol 35 主题簇 |
| `references/article-source.md` | 47 条事实登记 |
| `references/verification.md` | P0 核验、E-1～E-4、单源边界 |
| `log.md` | 变更日志与 CMD-LOG |

## Risks & Mitigations

| 风险 | 缓解 |
|---|---|
| 把厂商观点写成事实 | 事实表分“博文声明/作者观点/官方文档/相关 blip”四级 |
| SDK 细节快速过期 | 标注核验日期、版本边界（OpenCode V1/V2）与 `stale_after` |
| 并发会话改动污染计数 | 只提交本 bundle 与本次索引改动；外部未跟踪 bundle 不计入本 spec 的验收 |
| 编码偏向被忽略 | 单独一篇成本与领域适配文档，给出六层清单 |

## Acceptance

- [x] 6 篇概念 + 2 篇 references + index + log。
- [x] F-001～F-047 双份一致、连续。
- [x] P0 核验覆盖核心声明，4 条口径勘误。
- [x] bundle index → practice index → ai index → bundles/index 三级接入。
- [x] 本 bundle 相对链接 0 断链，UTF-8 通过，无敏感绝对路径。
