---
id: "protocols-onboarding-protocol"
title: "会话启动协议（Onboarding Protocol）"
source: "AGENTS.md#协作协议"
x-toml-ref: "../../.meta/toml/.agents/protocols/onboarding-protocol.toml"
---
# 会话启动协议（Onboarding Protocol）

> **层级**：L2深度层 | **适用范围**：所有接入SpecWeave的AI Agent | **阅读时机**：需要理解Onboarding设计原理、排查上下文建立问题、或实现自动化启动流程时

---

## 1. 协议目标

会话启动协议定义了AI Agent在新会话中建立项目上下文认知的标准流程。核心目标：

1. **快速定位**：Agent在1-2轮工具调用内知道"这里有什么能力可用"
2. **按需加载**：不预读所有文档，避免上下文窗口浪费
3. **正确路由**：根据任务类型准确跳转到目标能力的详细文档
4. **可审计**：启动过程可追踪、可验证

---

## 2. 设计理念：从"全量预读"到"索引导向"

### 2.1 历史问题

最初的设计采用"全量预读"模式——要求Agent在开始工作前读取大量前置文档。这导致两个问题：

1. **上下文窗口浪费**：大量当前任务不需要的文档占据了宝贵的上下文空间
2. **启动慢**：Agent需要遍历多个目录才能找到所需能力，违反Agent-First设计原则

### 2.2 渐进式披露（Progressive Disclosure）

本协议采用**渐进式披露**原则，将信息分为三层：

| 层级 | 文件 | 行数限制 | 阅读时间 | 内容 |
|------|------|---------|---------|------|
| L0入口层 | [ONBOARDING.md](../ONBOARDING.md) | <100行 | <30秒 | 身份声明+核心能力速查+路由表 |
| L1索引层 | [capability-registry.md](../capability-registry.md) | <500行 | 1-3分钟 | 全量能力索引（脚本/Skill/命令/工作流/协议/规则/知识库） |
| L2深度层 | commands/、protocols/、rules/ 等 | 不限 | 按需 | 完整参考手册、原理阐述、边缘情况 |

Agent的阅读路径：L0 → L1（定位能力）→ L2（按需读取目标能力的详细文档）

### 2.3 与PDR协议的关系

前置文档强制读取协议（[pre-document-reading.md](pre-document-reading.md)，简称PDR）是Onboarding的**下游协议**：

- **Onboarding**：解决"我是谁？这里有什么？我该去哪？"——全局认知建立
- **PDR**：解决"开始这个具体任务前我需要读什么？"——阶段级文档加载

Onboarding在会话开始时执行一次；PDR在每个开发阶段开始时执行。两者不冲突，互为补充。

```mermaid
flowchart LR
    A[新会话开始] --> B[Onboarding协议<br/>L0→L1→按需L2]
    B --> C[任务类型识别]
    C --> D[路由到具体能力]
    D --> E[进入开发阶段]
    E --> F[PDR协议<br/>读取阶段前置文档]
    F --> G[执行任务]
```

---

## 3. 标准启动流程

```
步骤1：读取 AGENTS.md
  └─ 获取全局规则、启动协议、上下文路由表
  └─ 按任务类型预检（步骤2.0）检查是否需要vendor方法论资产

步骤2：读取 ONBOARDING.md（本L0入口）
  └─ 了解核心高频能力（8条速查，其余能力通过L1注册表发现）
  └─ 确认必知vs按需的阅读策略
  └─ 使用路由决策树初步定位任务类型

步骤3：读取 capability-registry.md（L1索引）
  └─ 获取全量能力清单（30+脚本、6个Skill、5个命令集、3个工作流、7份协议、7条规则、4个知识参考入口）
  └─ 通过分类索引和快速查找指南精确定位目标能力

步骤4：路由到目标能力
  └─ 命令集任务 → 读取对应SKILL.md（L1门面）→ 按需读取commands/下L2文档
  ├─ Skill任务 → 读取对应SKILL.md → 按Skill指引执行
  ├─ 脚本任务 → 直接使用（脚本有--help参数自描述）
  ├─ 协议/规则任务 → 读取对应protocols/或rules/下L2文档
  └─ 跨模块任务 → 按AGENTS.md路由表读取相关模块的AGENTS.md

步骤5：按需读取目标能力的详细文档（L2）
  └─ 不预读全部文档
  └─ 只读当前任务直接相关的内容
  └─ 遵循PDR协议确认前置文档

步骤6：输出启动确认
  └─ 按指定格式确认上下文已建立
  └─ 识别任务类型
  └─ 声明将使用的能力

步骤7：执行任务
```

---

## 4. 启动确认格式

### 4.1 新会话启动

```
📋 上下文已建立：已读取 [AGENTS.md](../AGENTS.md)、[ONBOARDING.md](../ONBOARDING.md)（L0）、[capability-registry.md](../capability-registry.md)（L1）
任务类型识别：<复盘/Skill操作/检查/开发/...>
将使用：<对应能力名称+路径>
```

### 4.2 上下文恢复（收到summary）

当从先前会话上下文恢复时（收到会话历史摘要/summary），仍需重新执行步骤1-3，不得假设摘要中已包含完整路由信息。上下文压缩会导致认知视野收窄。

```
📋 新会话上下文重建：已重新读取 [AGENTS.md](../AGENTS.md)、[ONBOARDING.md](../ONBOARDING.md)（L0）、[capability-registry.md](../capability-registry.md)（L1）
当前进度：<当前处于哪个阶段/任务完成到哪一步>
待办事项：<接下来要做什么>
```

---

## 5. vendor区域的特殊处理

当任务工作目录位于 `vendor/` 内时，启动协议增加嵌套路由步骤（详见 [AGENTS.md §步骤2.1-2.2](../../AGENTS.md)）：

```
标准步骤1-3 → 额外读取 vendor/AGENTS.md → 按子模块路由表进入对应子模块AGENTS.md
→ 回到标准步骤4-7
```

无论工作目录是否在vendor/内，都必须执行任务类型预检（AGENTS.md步骤2.0），检查是否命中vendor方法论资产（如Skill创建必须读取vendor中的skill-creator规范）。

---

## 6. 常见反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| 跳过ONBOARDING直接LS/Glob遍历目录 | 盲目遍历效率低，容易遗漏能力 | 始终按L0→L1→L2路径导航 |
| L0阶段就读取L2详细文档 | 上下文浪费在当前不需要的内容上 | L0只做定位，L2按需读取 |
| 依赖会话摘要/summary不重新读取 | 摘要压缩导致信息丢失 | 新会话必须重新执行启动步骤1-3 |
| ONBOARDING.md中放入L2详细内容 | 导致L0膨胀，失去入口价值 | L0严格控制<100行，详细内容放L2 |
| capability-registry.md中放入L2教程 | 导致L1膨胀，索引变手册 | L1只做索引（用途+触发词+路径），教程放L2 |
| 不输出启动确认 | 无法审计上下文是否正确建立 | 首次输出中必须包含📋确认 |

---

## 7. 日志规范

会话启动过程的关键事件应输出结构化日志（与[PDR-LOG](pre-document-reading.md)格式一致），使用`[ONBOARD-LOG]`前缀：

| event值 | 级别 | 触发时机 |
|---------|------|---------|
| `ONBOARD_START` | INFO | 启动协议开始执行 |
| `ONBOARD_L0_READ` | INFO | L0 ONBOARDING.md读取完成 |
| `ONBOARD_L1_READ` | INFO | L1 capability-registry.md读取完成 |
| `ONBOARD_L2_READ` | DEBUG | 按需读取L2文档（每读一份记一条） |
| `ONBOARD_ROUTE` | INFO | 任务路由决策完成 |
| `ONBOARD_CONFIRM` | INFO | 启动确认输出 |
| `ONBOARD_RESUME` | INFO | 上下文恢复场景（收到summary） |
| `ONBOARD_ERROR` | ERROR | 启动过程中发生错误 |

日志格式：
```
[ONBOARD-LOG] | level=<LEVEL> | event=<EVENT> | session=<SESSION_ID> | msg=<MESSAGE> | ctx=<CONTEXT_JSON>
```

---

## 8. 相关文档

| 文档 | 关系 |
|------|------|
| [AGENTS.md](../../AGENTS.md) | 全局入口，启动协议的权威定义 |
| [ONBOARDING.md](../ONBOARDING.md) | L0入口层文件 |
| [capability-registry.md](../capability-registry.md) | L1索引层文件 |
| [capabilities/ARCHITECTURE.md](../capabilities/ARCHITECTURE.md) | 三层架构完整规范 |
| [pre-document-reading.md](pre-document-reading.md) | PDR协议——Onboarding的下游阶段级文档加载协议 |
| [stage-guardrails.md](../rules/stage-guardrails.md) | 阶段守卫——未完成Onboarding等同于跨阶段操作 |
| [VENDOR-INTEGRATION.md](../VENDOR-INTEGRATION.md) | vendor子模块协同规范 |
