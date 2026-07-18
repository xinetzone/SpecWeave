---
id: "selective-testing-strategy"
source: "../../reports/competitive-analysis/retrospective-minitest-ecosystem-learning-20260707/insight-extraction.md#模式7"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/selective-testing-strategy.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  -   - "incremental-regression-verification"
---
> **来源**：从Minitest AI QA测试平台生态系统复盘萃取，经Minitest devops-common验证

# 选择性测试模式（Selective Testing Strategy Pattern）

## 模式类型

代码模式（CI测试优化）

## 成熟度

L1 首次萃取（Minitest devops-common验证）

## 适用场景

中大型Python项目的CI测试优化。

## 问题背景

全量测试在大代码库中耗时过长，拖慢PR反馈循环；但只跑受影响测试又可能遗漏依赖变更导致的问题。

## 核心规则

### 方案：双层测试策略

- **PR事件**：基于git diff + AST导入图分析（`pytest-impacted`插件），仅运行变更影响的测试用例
- **非PR事件**（push到main、tag推送等）：运行完整测试套件作为安全网
- **强制全量触发条件**：依赖文件变更（uv.lock、pyproject.toml）或conftest.py变更时自动运行所有测试
- **无受影响测试**：pytest退出码5（未收集到测试）视为成功通过

### 测试策略详解

| 事件类型 | 测试策略 | 实现方式 | 目的 |
|---------|---------|---------|------|
| PR事件 | 选择性测试 | git diff + AST导入图分析 | 快速反馈，缩短PR审查周期 |
| 非PR事件 | 全量测试 | 运行完整测试套件 | 作为安全网，确保主分支质量 |
| 依赖变更 | 强制全量 | uv.lock、pyproject.toml、conftest.py变更时 | 确保依赖变更不引入回归 |
| 无受影响测试 | 成功通过 | pytest退出码5视为成功 | 避免误报失败 |

## 验证清单

- [ ] PR事件使用`pytest-impacted`插件仅运行受影响测试
- [ ] push到main时运行完整测试套件
- [ ] uv.lock或pyproject.toml变更时自动运行所有测试
- [ ] conftest.py变更时自动运行所有测试
- [ ] pytest退出码5（未收集到测试）视为成功通过

## 实施建议

- **工具选择**：使用`pytest-impacted`插件进行AST导入图分析
- **分层验证**：PR事件快速验证，主分支全量验证
- **依赖监控**：监控依赖文件变更，触发全量测试
- **退出码处理**：正确处理pytest退出码5，避免误报失败

## 与incremental-regression-verification的关系

本模式是incremental-regression-verification在CI场景的具体实现，专注于基于变更影响分析的选择性测试策略，平衡测试速度与覆盖范围。
