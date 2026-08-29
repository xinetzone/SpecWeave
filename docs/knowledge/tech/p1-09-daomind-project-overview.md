---
id: p1-09-daomind-project-overview
title: DaoMind 项目概览（道家哲学 TypeScript 框架）
source: d:\spaces\chaos\daoApps\DaoMind\README.md
source_type: file
category: tech
tags:
  - daomind
  - typescript
  - monorepo
  - philosophy-driven-design
  - project-overview
archive_status: archived
archive_priority: P1
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T11:40:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 DaoMind/README.md、正文为项目定位与架构概览提炼、元数据与 tech 分类映射核对通过
summary: DaoMind 是基于道家哲学宇宙论的现代化 TypeScript 框架，采用 pnpm monorepo 架构，核心包覆盖无/有/行动/应用/时序/道宇宙六层抽象，含函数式错误处理与 DaoUniverse 桥接体系。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\tech\p1-09-daomind-project-overview.md
archived_at: 2026-08-02T03:22:25Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:22:25Z archived from d:\spaces\chaos\.agents\knowledge\temp\tech\p1-09-daomind-project-overview.md to D:\spaces\SpecWeave\.agents\docs\knowledge\tech\p1-09-daomind-project-overview.md
---

# DaoMind 项目概览（道家哲学 TypeScript 框架）

## 来源

- 源文件：[DaoMind/README.md](file:///d:/spaces/chaos/daoApps/DaoMind/README.md)
- 部署说明：[DEPLOYMENT-GUIDE.md](file:///d:/spaces/chaos/daoApps/DaoMind/DEPLOYMENT-GUIDE.md)（如提炼部署要点可另行归档）
- 上游分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`tech`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\tech\`

## 正文摘要

**DaoMind** 是基于道家哲学宇宙论的现代化 TypeScript 框架，采用 pnpm monorepo 架构，核心思想来自帛书版《道德经》。

### 六层抽象核心

| 包 | 对应思想 | 职责 |
|---|---|---|
| `daoNothing` | 无 | 潜在性空间：编译期类型契约，零运行时开销 |
| `daoAnything` | 有 | 显化容器：运行时模块注册与生命周期管理 |
| `daoAgents` | 行动 | 自主实体：任务执行、事件观察、协调调度 |
| `daoApps` | 应用 | 可执行程序层：状态机驱动的应用生命周期 |
| `daoTimes` | 时序 | 定时器与调度：per-app 资源追踪与精准清理 |
| `daoCollective` | 道宇宙 | 根节点门面：统一入口、系统快照、DaoUniverse 层次化桥接器 |

### 关键能力

- 20+ 独立包，按需引入零冗余
- 1000 测试用例（52 套件），TypeScript 5.9 严格模式
- `DaoOption<T>` + `DaoResult<T,E>` 函数式错误处理，无 null/undefined 异常
- `DaoModuleGraph`：Kahn 拓扑排序 + DFS 循环检测的模块依赖图引擎
- `DaoUniverse*` 桥接体系：17 个分层桥接器
- 消费者层：DaoUniverseFacade → HealthBoard → Optimizer

### 快速开始

```bash
pnpx create-daomind my-app
cd my-app && pnpm install
pnpm dev
```

单包安装：`pnpm add @daomind/collective`（根节点推荐）、`@daomind/nothing`、`@daomind/anything`、`@daomind/agents`、`@daomind/times`

## 动作边界

本轮为 P1 项目说明条目。正式归档时以项目定位、六层架构、关键能力与快速开始为核心正文，不搬运完整 API 参考或全部示例代码。
