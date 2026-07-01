---
id: "perception-check-report-model"
source: "docs/retrospective/knowledge-extraction.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/architecture-patterns/perception-check-report-model.toml"
---
> **来源**：从 `docs/retrospective/knowledge-extraction.md` 二、可复用架构模式 拆分

# 感知→检查→报告 三层模型

## 来源
v1.0→v1.1 的优化过程揭示的核心规律

## 架构图
```
┌─────────────────────────────────────────────────┐
│  感知层：理解上下文                                │
│  ├─ 文档类型识别（元文档 / 普通文档）                │
│  ├─ 路径语义识别（根目录引用 / 相对引用）             │
│  └─ 语义粒度识别（中文短文本 / 英文长文本）            │
├─────────────────────────────────────────────────┤
│  检查层：执行检查                                  │
│  ├─ 覆盖率检查（需求→任务、场景→检查点）              │
│  ├─ 一致性检查（数据引用、交叉引用）                  │
│  └─ 变更检测（diff 对比）                          │
├─────────────────────────────────────────────────┤
│  报告层：分级输出                                  │
│  ├─ ❌ 错误：需立即修复                             │
│  ├─ ⚠️ 警告：建议关注                              │
│  └─ ✓ 通过：无问题                                 │
└─────────────────────────────────────────────────┘
```

## 核心原则
检查工具的质量取决于**感知层的深度**。感知层越深，检查层误报越少。

## 复用场景
任何自动化检查/验证工具的设计蓝图。

> **关联模块**：
> - `patterns/code-patterns/three-tier-check-tool.md`
> - `patterns/code-patterns/context-aware-path-resolution.md`
> - `concepts/context-awareness.md`