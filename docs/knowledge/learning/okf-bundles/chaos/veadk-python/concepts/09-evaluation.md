---
type: Concept
title: 评估系统
description: BaseEvaluator 评估基类、EvalTestCase 测试用例模型、MetricResult 指标结果与 ADK/DeepEval 双评估器
tags: [veadk, evaluation, evaluator, metrics, deepeval, testing]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: veadk-source
    resource: "/references/veadk-source.md"
    title: veadk-python 源码
  - id: facts
    resource: "/references/facts.md"
    title: veadk-python 事实清单
---

# 评估系统

veadk-python 的评估系统定义于 `veadk/evaluation/`，提供结构化的 Agent 质量评估框架。核心包括 `BaseEvaluator` 抽象基类、`EvalTestCase` 测试用例模型、`MetricResult` 指标结果模型，以及 ADK 原生评估器和 DeepEval 评估器两种实现。评估数据可从 eval JSON 文件或 Runner 生成的 tracing JSON 构建，形成"运行→追踪→评估"的工程化闭环。

## 数据模型

评估系统使用一组 Pydantic 模型描述测试用例和结果 [F-098]。

### ToolInvocation

```python
class ToolInvocation(BaseModel):
    tool_name: str
    tool_args: dict
    tool_result: Any
```

记录单次工具调用的名称、参数和结果。

### Invocation

```python
class Invocation(BaseModel):
    invocation_id: str
    input: str
    actual_output: str
    expected_output: str
    actual_tool: list[ToolInvocation]
    expected_tool: list[ToolInvocation]
    latency: float
```

单次调用记录，包含输入、实际输出、期望输出、工具调用对比和延迟。

### EvalTestCase

```python
class EvalTestCase(BaseModel):
    invocations: list[Invocation]
```

一个测试用例可包含多次调用（如多轮对话场景）。

### MetricResult

```python
class MetricResult(BaseModel):
    metric_type: str
    success: bool
    score: float
    reason: str
```

单个指标的评估结果，包含指标类型、是否通过、分数（0-1）和文字理由。

## EvalResultData

`EvalResultData` 聚合单个测试用例的所有指标结果 [F-099]：

```python
class EvalResultData(BaseModel):
    metric_results: list[MetricResult]
    average_score: float = 0.0
    total_reason: str = ""
```

核心方法：

- `calculate_average_score()`：计算所有指标的平均分
- `generate_total_reason()`：将所有指标的理由拼接为 `"metric_type:reason"` 格式
- `call_before_append()`：在追加结果前调用上述两个方法

## BaseEvaluator 基类

`BaseEvaluator` 定义于 `veadk/evaluation/base_evaluator.py`，是所有评估器的抽象基类 [F-100]。

### 构造函数

```python
def __init__(self, agent, name: str)
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 评估器名称 |
| `agent` | `Agent` | 被评估的 Agent |
| `invocation_list` | `list[EvalTestCase]` | 测试用例列表 |
| `result_list` | `list[EvalResultData]` | 评估结果列表 |
| `agent_information_list` | `list[dict]` | Agent 元信息列表 |

### 评估集构建

**从 eval JSON 文件构建**：

```python
_build_eval_set_from_eval_json(eval_json_path: str)
```

通过 `load_eval_set_from_file` 加载 Google ADK 格式的评估集文件 [F-100]。

**从 tracing JSON 构建**：

```python
_build_eval_set_from_tracing_json(tracing_json_path: str)
```

从 Runner 保存的 tracing JSON 文件构建评估集 [F-100]。该方法：
1. 解析 tracing JSON 中的 span 数据
2. 按 `trace_id` 分组，将同一 trace 的 span 重组为一次完整调用
3. 提取输入、输出、工具调用等信息填充 `Invocation`

这使得实际运行的会话数据可以直接转化为评估测试用例，无需手动编写。

### 抽象方法

子类必须实现 `evaluate` 方法，定义具体的评估逻辑 [F-100]。

## 评估器实现

### ADK 评估器

`veadk/evaluation/adk_evaluator/` 目录包含 ADK 原生评估器，使用 Google ADK 的 `google-adk[eval]` 依赖 [F-007]。适用于使用 ADK 内置指标（如工具调用正确性、输出匹配度）的场景。

### DeepEval 评估器

`veadk/evaluation/deepeval_evaluator/` 目录包含基于 DeepEval（`deepeval>=3.2.6`）的评估器 [F-007]。DeepEval 提供丰富的 LLM-as-judge 指标，如：

- 回答相关性（Answer Relevancy）
- 忠实度（Faithfulness）
- 上下文精确度（Contextual Precision）
- 幻觉检测（Hallucination）

### Prometheus 集成

`veadk/evaluation/utils/prometheus.py` 提供 Prometheus 指标导出支持，可选依赖 `prometheus-client` [F-007]。

## 结果数据模型

### EvalResultCaseData

```python
class EvalResultCaseData(BaseModel):
    id: str
    input: str
    actual_output: str
    expected_output: str
    score: str
    reason: str
    status: str  # "PASSED" 或 "FAILURE"
    latency: str
```

`score` 和 `latency` 使用字符串类型以兼容外部系统 [F-101]。

### EvalResultMetadata

```python
class EvalResultMetadata(BaseModel):
    tested_model: str
    judge_model: str
```

记录被测模型和评判模型的名称 [F-101]。

## CLI 评估命令

`veadk eval` 命令提供命令行评估入口 [F-080]：

```bash
veadk eval \
  --agent-dir . \
  --evalset-file eval_set.json \
  --evaluator adk \
  --judge-model-name doubao-1-5-pro-256k-250115
```

参数说明：

| 参数 | 说明 |
|------|------|
| `--agent-dir` | Agent 目录（默认 `.`），须导出 `root_agent` |
| `--agent-a2a-url` | 远程 A2A 部署 URL（与 `--agent-dir` 二选一） |
| `--evalset-file` | 评估集文件路径（必填，Google ADK 格式） |
| `--evaluator` | 评估器类型：`adk` 或 `deepeval` |
| `--judge-model-name` | 评判模型（默认 `doubao-1-5-pro-256k-250115`） |
| `--volcengine-access-key` | 火山引擎 AK |
| `--volcengine-secret-key` | 火山引擎 SK |

## Runner 评估集成

Runner 提供两个方法支持评估工作流 [F-071]：

- `save_tracing_file(session_id)`：保存会话的完整 tracing 数据为 JSON，可作为评估输入
- `save_eval_set(session_id, eval_set_id="default")`：直接将会话保存为评估集

典型评估流程：

1. 使用 Runner 运行测试用例
2. 保存 tracing 文件或评估集
3. 使用 `veadk eval` 命令或 `BaseEvaluator` 子类加载评估数据
4. 选择 ADK 或 DeepEval 评估器执行评估
5. 查看 `MetricResult` 和 `EvalResultData` 结果

## eval_set 文件加载

`veadk/evaluation/eval_set_file_loader.py` 提供评估集文件加载功能，支持 Google ADK 格式的 JSON 评估集文件。`veadk/evaluation/eval_set_recorder.py` 负责评估结果的记录和持久化。

## 使用概念

评估系统的设计遵循以下原则：

1. **数据驱动**：测试用例来自实际运行的 tracing 数据，而非人工构造
2. **可插拔评估器**：ADK 和 DeepEval 两种实现可按需选择
3. **结构化结果**：所有指标结果使用统一的 Pydantic 模型，便于聚合和导出
4. **CLI 集成**：通过 `veadk eval` 命令可在 CI/CD 中自动化评估
5. **双模型架构**：被测模型（tested_model）与评判模型（judge_model）分离

## 相关概念

- [Runner 运行器](/concepts/05-runner.md)
- [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)
- [CLI 工具集](/concepts/10-cli-tools.md)
- [知识库](/concepts/08-knowledgebase.md)
- [高级特性](/concepts/11-advanced.md)
