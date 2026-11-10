---
type: spec
title: "mini-SWE-agent 全面学习 → OKF v0.2 知识包"
source_url: "https://lukaxiya.github.io/coding-agent-blog/posts/mini-swe-agent/"
secondary_sources:
  - "https://zhuanlan.zhihu.com/p/2011860096536314782"
  - "https://github.com/SWE-agent/mini-swe-agent"
status: completed
generated_at: "2026-11-10"
---

# mini-SWE-agent 全面学习 → OKF v0.2 知识包

## Overview

把三份信源（技术博客、知乎专栏、官方 GitHub 仓库）合并学习，转化为 `projects/awesome-okf-xs/doc/bundles/` 下的 OKF v0.2 知识包。按七概念方法论编排（`seven-concepts-cmd`）走**场景 4 知识沉淀链路 R→I→E→V→C**。

| 项 | 值 |
|---|---|
| 主信源 | https://lukaxiya.github.io/coding-agent-blog/posts/mini-swe-agent/ |
| 第二信源 | https://zhuanlan.zhihu.com/p/2011860096536314782（不可达，见 R-2） |
| 源码信源 | https://github.com/SWE-agent/mini-swe-agent（v2.4.6，commit `04d809ce`） |
| 内容敏感度 | 公开内容（无访问控制、无邀请码） |
| 工作流 | 标准工作流（spec 在 `.trae/specs/`，产出在 `projects/awesome-okf-xs/doc/bundles/`） |
| 目标落点 | `projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/mini-swe-agent/` |

## Goals

- G1：产出结构完整的 OKF v0.2 bundle，覆盖**项目身份 / 设计哲学 / 代码架构 / 执行环境 / 模型接入 / 配置扩展 / 评测边界 / 可迁移经验**八层。
- G2：所有具体声明挂 F 编号；spec `facts.md` 与 bundle `references/*-source.md` 双份登记、编号集合一致且连续。
- G3：P0 核验覆盖 Stars、SWE-bench 年份、74% 成绩、代码规模、快速开始 API、v2 默认工具调用方式。
- G4：三级 toctree（bundle index → ai-agent index → frameworks index → ai index → bundles index）与计数自洽。
- G5：frontmatter 完整、相对链接可达、UTF-8 strict roundtrip 通过、无敏感绝对路径。

## Non-Goals

- 不在本机执行 `pip install mini-swe-agent` 或 SWE-bench（需要 API Key 与 Docker/x86 环境）；`examples/` 只登记官方文档命令，明确标注“未在本机实测”。
- 不复刻 74% 评测；不声称某个模型“必然”达到该分数。
- 不把 README 的采用者名单与“启动快于 Claude Code”当成独立验证事实。
- 不修改并发会话正在生成的其它未跟踪 bundle。

## Background & Context

### 1. 信源与公开性预检

| 检查项 | 结论 |
|---|---|
| 内容性质 | 公开技术博客 + 公开 GitHub 仓库 |
| 访问控制 | 博客与仓库无登录墙；知乎链接返回 403/404 |
| 信源距离 | 博客为第三方解读；GitHub 仓库与官方 docs 为一手信源 |
| 时效性 | 仓库迭代快（v2.4.6，2026-09-03）；`stale_after=2027-03-31` |

### 2. 信源获取记录（R-1～R-3）

| 编号 | 信源 | 结果 |
|---|---|---|
| R-1 | 博客 `lukaxiya.github.io/.../mini-swe-agent/` | ✅ WebFetch 成功，正文约 5.7 KB |
| R-2 | 知乎 `zhuanlan.zhihu.com/p/2011860096536314782` | ❌ 三种抓取均失败：zhuanlan 403、api.zhihu.com 40362、www.zhihu.com 404；**未使用其内容** |
| R-3 | GitHub `SWE-agent/mini-swe-agent` | ✅ 浅克隆 `--depth 1` 成功；commit `04d809ce`，版本 `2.4.6` |

### 3. 骨架判定（操作可复现性两问）

1. 是否有读者可照做的安装/配置/代码/调用流程？**是**（README Quick Start、`mini` CLI、Python bindings、SWE-bench 批处理脚本）。
2. 这些流程是否经作者实测、具备版本/输入输出/步骤顺序？**部分是**：官方 docs 给出命令与版本，但本次未在本机执行，且博客中的示例 API 与 v2 实际 API 不符（E-3）。

结论：设 `examples/`，但每篇顶部标注“官方文档命令，未在本机实测”，并只使用源码中真实存在的类名/命令。

### 4. 归属判定

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/frameworks/ai-agent/mini-swe-agent/` | **选中** | 主体是 Coding Agent 框架/源码；ai-agent 组已有 opencode、pi-cli、deepseek-reasonix 等同类束 |
| `jishu/ai/practice/` | 未选 | 本束重点在源码架构与可复现用法，不是行业洞察 |
| `jishu/ai/learning/` | 未选 | 不是学习路径盘点，而是单项目系统教程 |
| 新建分组 | 未选 | 单项目新建分组属过度工程 |

### 5. 三层知识拆分

| 层 | 文档 | 内容 |
|---|---|---|
| 身份与判断层 | 00、01 | 项目谱系、硬指标、三条约简设计哲学 |
| 机制与实现层 | 02、03、04、05 | Agent/Model/Environment 三协议、执行环境、模型接入、配置与扩展 |
| 评测与迁移层 | 06、07 | SWE-bench 成绩与能力边界、可迁移工程经验 |

## Deliverables

| 文件 | 说明 |
|---|---|
| `index.md` | bundle 根索引、核心结论、阅读路径、主题关联、核验摘要 |
| `concepts/00-project-overview.md` | 身份、谱系、版本、硬指标与勘误 |
| `concepts/01-design-philosophy.md` | 三条约简：bash-only / 线性历史 / 独立 subprocess |
| `concepts/02-architecture-and-code.md` | 三协议与 172 行主循环的代码级解剖 |
| `concepts/03-execution-environments.md` | local/docker/singularity/bubblewrap/contree/swerex 六类后端 |
| `concepts/04-model-integration.md` | litellm/openrouter/portkey/requesty；toolcall vs textbased |
| `concepts/05-configuration-and-extension.md` | YAML 三段配置、Jinja 模板、轨迹格式、子类化 |
| `concepts/06-benchmarks-and-boundaries.md` | 74% 成绩、SWE-bench、Ramp/DeepSWE/ProgramBench、能力边界 |
| `concepts/07-transferable-lessons.md` | 七条可迁移工程经验 |
| `examples/01-install-and-cli.md` | 安装与 `mini` CLI 三模式 |
| `examples/02-python-bindings.md` | 20 行嵌入 Agent |
| `examples/03-swebench-batch.md` | SWE-bench 批处理与单实例调试 |
| `references/blog-source.md` | 博客事实 F-001～F-034 |
| `references/repo-source.md` | 仓库事实 F-035～F-090 |
| `references/verification.md` | P0 核验、E-1～E-4、单源边界 |
| `log.md` | 变更日志与 CMD-LOG |

## Risks & Mitigations

| 风险 | 缓解 |
|---|---|
| 博客把 v1 特性写成现状 | 以 v2.4.6 源码为准，E-3/E-4 明确版本边界 |
| 74% 被当作无条件的框架能力 | 标注“官方 docs 声明 + Gemini 3 Pro 单点成绩”，不给完整评测配置 |
| README 与实现不一致 | F-078 单列文档滞后，正文以源码默认值为准 |
| 知乎信源缺失 | R-2 明示不可达，结论只依赖博客 + 仓库，不虚构知乎观点 |
| 计数漂移 | 运行 `check-bundles-index.py` 与 `check-toctrees.py` 机械对账 |

## Acceptance

- [x] 8 篇概念 + 3 篇示例 + 3 篇 references + 3 个子目录索引 + index + log（共 19 个文件）。
- [x] F-001～F-090 双份一致、连续。
- [x] P0 核验覆盖核心声明，4 条硬勘误 + 1 条信源缺口。
- [x] bundle index → ai-agent index → frameworks index → ai index → bundles index 三级接入。
- [x] 本 bundle 相对链接 0 断链，UTF-8 通过，无敏感绝对路径。
