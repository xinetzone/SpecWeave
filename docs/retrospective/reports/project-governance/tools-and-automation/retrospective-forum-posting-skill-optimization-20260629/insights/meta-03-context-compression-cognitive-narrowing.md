---
id: "meta-context-compression-cognitive-narrowing"
source: "../insight-extraction.md#发现8上下文丢失context-compression放大了就近直觉偏差"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/insights/meta-03-context-compression-cognitive-narrowing.toml"
---
# Meta洞察3：上下文压缩放大"就近直觉"偏差——Context恢复需重执行协议

→ 正式模式：[context-recovery-protocol.md](../../../../../patterns/methodology-patterns/ai-collaboration/context-recovery-protocol.md)（已入库L1）

## 事件事实

本次会话是"continues a previous conversation that lost its context"，前半段的决策上下文通过summary压缩恢复。

## 影响链

```
上下文丢失 → 智能体对"项目全局结构"的认知降级为"当前可见文件"
  → 更容易只关注工作目录附近的文件
    → 不去主动探索vendor子模块中的资产
      → 触发"就近直觉"偏差，导致路由违规
```

## 深层含义

**上下文压缩不仅是"信息丢失"，更是"认知视野收窄"**。当上下文窗口有限时，智能体倾向于处理"手边的信息"（最近读取的文件、当前目录），而不是建立完整的项目全局视图。这使得启动协议（强制读取全局路由表）在上下文不完整时更加重要——它是防止视野收窄的结构性保障。

## 落地措施：Context恢复协议

收到session continuation（summary/继续）后，**必须重新执行完整启动协议**：
1. 重新读取AGENTS.md全文
2. 重新执行任务类型预检（步骤2.0）
3. 重新读取所有相关规范
4. 重新执行自检（步骤3.5）
5. 再继续工作

> **为什么？** 不能假设summary包含了所有路由信息——上下文压缩会导致认知视野收窄，只依赖summary容易遗漏vendor方法论资产。

## 关联洞察

- [meta-05-availability-heuristic-structural-guard.md](meta-05-availability-heuristic-structural-guard.md) — 可得性启发是系统性认知偏差
- [finding-01-three-layer-routing-non-symmetric-trigger.md](finding-01-three-layer-routing-non-symmetric-trigger.md) — 非对称触发陷阱
- [law-02-three-layer-routing-task-type-precheck.md](law-02-three-layer-routing-task-type-precheck.md) — 任务类型预检流程

---
*来源：[forum-posting Skill优化复盘](../README.md)*
