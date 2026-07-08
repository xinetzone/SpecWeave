---
id: "templates-analysis-dimension-templates"
title: "差异化分析维度模板库"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/analysis-dimension-templates/README.toml"
version: "1.0.0"
---
# 差异化分析维度模板库

> **适用场景**：多对象并行分析任务中，为不同类型分析对象定义差异化分析维度，提升分析质量一致性。

## 模板索引

| 对象类型 | 模板文件 | 核心分析维度 |
|---------|---------|-------------|
| CLI/工具类 | [cli-tool-dimension.md](cli-tool-dimension.md) | 命令体系、核心API、扩展机制、配置体系 |
| CI/集成类 | [ci-integration-dimension.md](ci-integration-dimension.md) | 触发机制、事件流、配置项、环境依赖 |
| 基建/配置类 | [infrastructure-config-dimension.md](infrastructure-config-dimension.md) | 配置规范、版本策略、工具链、复用方式 |
| 示例/Demo类 | [example-demo-dimension.md](example-demo-dimension.md) | 集成模式、使用示例、最佳实践 |
| Skills/插件类 | [skills-plugin-dimension.md](skills-plugin-dimension.md) | 接口定义、注册机制、调用协议 |

## 使用方式

在 tasks.md 中按对象类型引用对应维度模板：

```markdown
- Task 1: 分析 minitest-cli（CLI/工具类）
  - 参照模板: analysis-dimension-templates/cli-tool-dimension.md
  - 输入: d:\AI\.chaos\libs\minitap-ai\minitest-cli
```

## 模板设计原则

1. **对象类型优先**：按分析对象类型切分，而非按分析维度切分
2. **维度差异化**：不同类型对象关注的核心维度不同
3. **质量一致性**：统一的分析深度要求，避免不同类型仓库分析深度不均
4. **可扩展性**：每个模板预留自定义扩展维度空间
