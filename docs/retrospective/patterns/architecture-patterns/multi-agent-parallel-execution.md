+++
id = "multi-agent-parallel-execution"
domain = "architecture"
layer = "architecture"
maturity = "L2"
validation_count = 2
reuse_count = 0
documentation_level = "basic"
source = "docs/retrospective/knowledge-extraction.md"

[bindings]
rules = []
references = []
skills = []
+++

> **来源**：从 `docs/retrospective/knowledge-extraction.md` 二、可复用架构模式 拆分

# 多智能体并行执行模式

## 来源
智能体开发规范体系项目的实施策略

## 模式
```
前提条件：任务间无依赖关系
执行策略：N 个子代理并行，每个负责独立领域
上下文隔离：每个子代理仅加载其领域的上下文，避免全局上下文膨胀
```

## 决策矩阵

| 任务特征 | 执行方式 | 原因 |
|---------|---------|------|
| 有副作用（文件系统操作） | 主代理串行 | 确保环境就绪后再并行 |
| 无依赖、纯文档创建 | 子代理并行 | 上下文隔离，效率最大化 |
| 有依赖关系 | 主代理串行 | 依赖顺序不可打破 |

## 复用场景
任何需要批量创建文档/文件的项目。

> **关联模块**：
> - `patterns/methodology-patterns/spec-driven-development.md`