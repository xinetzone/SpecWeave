# Cordis 与时空可组合性论文 中文 Wiki 教程 Spec

## Why

`d:\AI\.chaos\temp\cordis` 是一个在研的 TypeScript"时空可组合性元框架"（Meta-Framework of Spatiotemporal Composability），`d:\AI\.chaos\temp\paper` 是与其配套的学术论文《A Programming Paradigm for Spatiotemporal Composability》。二者是同一套思想（可逆效应 revertible effects + 响应式协同效应 reactive coeffects）在理论与实践两个层面的对应。当前项目缺乏对这套内容的中文学习资料，需要通过方法论编排（七概念 R→I→E）系统学习并沉淀为可复用的中文 Wiki 教程。

## What Changes

- 新增一套中文 Wiki 教程，系统讲解 Cordis 框架与配套论文的核心概念、文件结构、技术实现与使用方法
- 教程放置于 `docs/knowledge/learning/03-agent-platforms-tools/cordis-spatiotemporal-composability-wiki/`（公开内容 → 标准工作流）
- 采用原子化章节结构（`00-overview.md` … `NN-summary-resources.md`），并附一份方法论报告 `seven-concepts-report.md`
- 更新父目录 `docs/knowledge/learning/03-agent-platforms-tools/README.md` 的导航索引

## Impact

- Affected specs：新增能力（知识库学习文档），无既有 spec 修改
- Affected code：仅文档类新增（`docs/knowledge/learning/03-agent-platforms-tools/`），不涉及源码
- 学习对象（只读，不修改）：
  - `d:\AI\.chaos\temp\cordis`（monorepo，含 core/loader/hmr/create/group/include/logger-console/timer/utils 等包）
  - `d:\AI\.chaos\temp\paper`（README.md + paper.pdf）

## ADDED Requirements

### Requirement: 教程整体结构
系统 SHALL 提供一套覆盖"概述→背景理论→架构→核心机制→使用示例→FAQ→资源"的中文 Wiki 教程。

#### Scenario: 章节完整覆盖
- **WHEN** 用户打开教程目录
- **THEN** 教程具备原子化章节、编号连续、封面概述与收尾总结齐备

### Requirement: 背景理论与论文讲解
系统 SHALL 讲解论文《A Programming Paradigm for Spatiotemporal Composability》的核心思想，包括时空可组合性、可逆效应、响应式协同效应、统一上下文类型、组件动态组合演算。

#### Scenario: 理论与实现对应
- **WHEN** 用户阅读背景章节
- **THEN** 能理解"temporal/spatial composability"等术语，并将其与 Cordis 源码实现对应起来

### Requirement: 核心源码实现讲解
系统 SHALL 讲解 Cordis 核心包（core）的关键抽象：Context、Service、Fiber、Registry、Events/Logger/Reflect 服务，以及 effect（可逆副作用）与 coeffect（依赖注入）机制。

#### Scenario: 读懂核心机制
- **WHEN** 用户阅读核心架构与机制章节
- **THEN** 能理解 `ctx.plugin()`、`@Inject`、`Fiber` 状态机、disposable/effect 的逆向回收原理

### Requirement: 辅助包与工具链讲解
系统 SHALL 讲解 loader（声明式加载与配置合并）、hmr（热更新）、create（脚手架）、group/include/logger-console/timer/utils 等辅助包的作用与用法。

#### Scenario: 理解工程化支撑
- **WHEN** 用户阅读辅助包章节
- **THEN** 能理解 yarn workspaces monocrepo 结构、声明式装配与热更新能力

### Requirement: 代码示例与图示
系统 SHALL 提供可运行的代码示例（插件注册、依赖注入、生命周期、可逆副作用）与必要的架构图（Mermaid）。因本项目为源码库、无 GUI，以代码摘录与图代替截图说明。

#### Scenario: 可操作示例
- **WHEN** 用户阅读使用示例章节
- **THEN** 能参照示例编写并装配一个最小 Cordis 插件

### Requirement: FAQ 与注意事项
系统 SHALL 提供常见问题解答（API 未稳定、active development、双向绑定语义、异步 effect 等）与注意事项。

#### Scenario: 规避误导
- **WHEN** 用户阅读 FAQ 章节
- **THEN** 明确该框架 API 尚不稳定、处于活跃开发，不将细节视为最终契约

### Requirement: 方法论报告
系统 SHALL 附一篇 `seven-concepts-report.md`，记录 R→I→E 知识沉淀链路与 G1-G3 质量门结果。

#### Scenario: 可审计的沉淀过程
- **WHEN** 用户查看方法论报告
- **THEN** 能看到事实采集、根因洞察、模式萃取的质量门通过记录