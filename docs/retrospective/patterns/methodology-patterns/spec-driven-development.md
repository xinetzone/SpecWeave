> **来源**：从 `docs/retrospective/knowledge-extraction.md` 三、可复用方法论 拆分

# Spec-driven 开发流程

## 来源
两个项目的完整开发过程

## 流程图
```
需求分析 → spec.md（需求规格）
         → tasks.md（任务分解）
         → checklist.md（验证清单）
         → 实施
         → 验证闭环
```

## 关键原则
- "理解需求"与"执行任务"解耦——规格阶段专注需求表达，实施阶段专注机械执行
- 验证标准前置定义——checklist 在规格阶段即编写，不随实施结果调整
- 需求冻结机制——进入规格设计前明确需求冻结标准

## 复用场景
任何需要"先设计后实施"的开发任务。

> **关联模块**：
> - `templates/spec-template.md`
> - `templates/tasks-template.md`
> - `templates/checklist-template.md`
> - `patterns/architecture-patterns/multi-agent-parallel-execution.md`