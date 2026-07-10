---
id: "cli-json-pipeline"
source: "../../reports/competitive-analysis/retrospective-minitest-ecosystem-learning-20260707/insight-extraction.md#模式1"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/cli-json-pipeline.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  -   - "cli-as-api-design"
  -   - "script-json-output-contract"
---
> **来源**：从Minitest AI QA测试平台生态系统复盘萃取，经Minitest CLI验证

# CLI-JSON管道模式（CLI-JSON Pipeline Pattern）

## 模式类型

代码模式（CLI工具输出设计）

## 成熟度

L1 首次萃取（Minitest CLI验证）

## 适用场景

所有需要被脚本、CI流水线、AI Agent编程式调用的CLI工具。

## 问题背景

CLI工具输出人类可读的格式化文本，难以被脚本/AI Agent可靠解析；诊断消息混入数据输出导致管道处理失败。

## 核心规则

**问题→方案→适用场景**结构：

### 方案

- 提供全局`--json`标志，输出camelCase JSON到stdout
- 所有诊断/警告/进度消息输出到stderr
- Pydantic模型自动通过`by_alias=True`序列化为camelCase
- 非JSON模式使用Rich库输出人类友好表格

### 关键设计

| 设计要素 | 实现方式 | 目的 |
|---------|---------|------|
| 输出分离 | stdout=结构化数据，stderr=诊断消息 | 管道安全，jq等工具可可靠解析 |
| 格式转换 | `--json`触发JSON模式 | 双消费者支持（人类/机器） |
| 命名规范 | camelCase序列化 | 符合API约定，便于JavaScript消费 |
| 人类友好 | Rich表格渲染 | 提升交互体验 |

## 验证清单

- [ ] `--json`模式下stdout仅输出JSON，可被`json.loads()`解析
- [ ] 所有诊断、警告、进度消息输出到stderr
- [ ] JSON字段使用camelCase命名
- [ ] 默认模式（无`--json`）输出人类友好的Rich表格
- [ ] `minitest --json user-story list \| jq '.items[].name'`可正常工作

## 与cli-as-api-design的关系

本模式是cli-as-api-design的核心子集，专注于stdout/stderr分离和JSON输出契约。cli-as-api-design在此基础上扩展了多格式输出、会话持久化等更复杂的功能。
