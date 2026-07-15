---
id: "lib-api-testing"
title: "lib.testing — 测试辅助工具库"
source: "lib/testing/__init__.py"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/15-testing.toml"
---

# lib.testing — 测试辅助工具库

提供边界场景测试模板、参数化测试fixture、多智能体场景生成器，专为仲裁/调度类并发模块设计。

## 设计目标

- **边界场景全覆盖**：自动覆盖 N=1,2,3,5,10 个agent的典型边界数量
- **策略组合矩阵**：支持多种优先级和负载策略组合，防止遗漏调度bug
- **参数化便捷**：通过装饰器一键参数化，减少样板代码
- **断言文档化**：内置边界场景断言说明，明确测试预期

---

## 模块导航

| 子模块 | 说明 |
|--------|------|
| [lib.testing.multi_agent](15-testing.md#multi_agent-子模块) | 多智能体边界场景生成器 |

---

## multi_agent 子模块

### 常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `BOUNDARY_AGENT_COUNTS` | `(1, 2, 3, 5, 10)` | 标准边界场景agent数量元组 |
| `EXTREME_AGENT_COUNTS` | `(0, 1, 2, 3, 5, 10, 50, 100)` | 扩展极端场景agent数量元组（含空、超大规模） |

### 数据类

#### `MultiAgentScenario`

多agent测试场景描述。

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 场景唯一标识名称 |
| `agent_count` | `int` | 场景中的agent数量 |
| `agents` | `dict[str, dict[str, Any]]` | agent字典，格式 `{agent_id: {id, role, priority, load, capabilities}}` |
| `description` | `str` | 场景中文描述 |
| `expected_winner` | `Optional[str]` | 预期胜出的agent ID（可预测场景） |
| `expected_access_order` | `Optional[list[str]]` | 预期访问顺序（资源竞争场景） |
| `metadata` | `dict[str, Any]` | 额外元数据（priority_strategy, load_strategy等） |

---

### 核心函数

#### `generate_agents()`

```python
def generate_agents(
    count: int,
    *,
    role: str = "developer",
    priority_strategy: str = "uniform",
    load_strategy: str = "ascending",
    capabilities: Optional[list[str]] = None,
    id_prefix: str = "agent",
) -> dict[str, dict[str, Any]]
```

生成指定数量的agent字典。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `count` | `int` | 必填 | agent数量，推荐使用 `BOUNDARY_AGENT_COUNTS` 中的值 |
| `role` | `str` | `"developer"` | 角色名称 |
| `priority_strategy` | `str` | `"uniform"` | 优先级分配策略，见下表 |
| `load_strategy` | `str` | `"ascending"` | 负载分配策略，见下表 |
| `capabilities` | `Optional[list[str]]` | `None` | 能力列表，None则默认为 `["coding"]` |
| `id_prefix` | `str` | `"agent"` | agent ID前缀 |

**priority_strategy 可选值**：

| 值 | 说明 |
|----|------|
| `"uniform"` | 所有agent优先级相同（默认值=2） |
| `"ascending"` | 优先级从1递增（第一个agent优先级最高） |
| `"descending"` | 优先级从N递减（最后一个agent优先级最高） |
| `"random"` | 随机优先级1-5 |

**load_strategy 可选值**：

| 值 | 说明 |
|----|------|
| `"uniform"` | 所有agent负载相同（默认值=50） |
| `"ascending"` | 负载递增（第一个agent负载最低，用于测试负载均衡） |
| `"descending"` | 负载递减（最后一个agent负载最低） |
| `"extremes"` | 极端分布：第一个最高(99)，最后一个最低(1)，其余均匀，用于测试饥饿场景 |

**返回**：`dict[str, dict[str, Any]]` - agent字典，格式 `{agent_id: agent_info}`

**示例**：

```python
from lib.testing import generate_agents, BOUNDARY_AGENT_COUNTS

# 生成3个agent，负载递增（用于负载均衡测试）
agents = generate_agents(3, load_strategy="ascending")
# agent_0: {load: 10}, agent_1: {load: 50}, agent_2: {load: 90}

# 生成10个agent，优先级递增，极端负载（用于饥饿场景测试）
agents = generate_agents(10, priority_strategy="ascending", load_strategy="extremes")
```

---

#### `agent_scenarios()`

```python
def agent_scenarios(
    *,
    name_prefix: str = "scenario",
    counts: tuple[int, ...] = BOUNDARY_AGENT_COUNTS,
    priority_strategies: tuple[str, ...] = ("uniform", "ascending", "descending"),
    load_strategies: tuple[str, ...] = ("uniform", "ascending", "descending", "extremes"),
    role: str = "developer",
    capabilities: Optional[list[str]] = None,
) -> list[MultiAgentScenario]
```

生成多agent边界场景矩阵（笛卡尔积），用于全面覆盖各种策略组合。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name_prefix` | `str` | `"scenario"` | 场景名称前缀 |
| `counts` | `tuple[int, ...]` | `BOUNDARY_AGENT_COUNTS` | 要测试的agent数量元组 |
| `priority_strategies` | `tuple[str, ...]` | 三种基础策略 | 要测试的优先级策略组合 |
| `load_strategies` | `tuple[str, ...]` | 四种策略 | 要测试的负载策略组合 |
| `role` | `str` | `"developer"` | 角色名 |
| `capabilities` | `Optional[list[str]]` | `None` | 能力列表 |

**返回**：`list[MultiAgentScenario]` - 测试场景列表，每个场景包含预生成的agents和元数据

**示例**：

```python
from lib.testing import agent_scenarios

# 生成完整测试矩阵（默认5种数量 × 3种优先级策略 × 4种负载策略 = 60个场景）
scenarios = agent_scenarios(name_prefix="conflict_resolution")
for sc in scenarios:
    result = resolver.resolve(report, agents=sc.agents)
    # 断言验证...
```

---

#### `parametrize_agent_counts()`

```python
def parametrize_agent_counts(
    *test_funcs: Callable,
    counts: tuple[int, ...] = BOUNDARY_AGENT_COUNTS,
    skip_single: bool = False,
)
```

pytest装饰器：为测试函数参数化不同agent数量，自动注入 `n_agents` 参数。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `*test_funcs` | `Callable` | 变长 | 要装饰的测试函数（支持同时装饰多个） |
| `counts` | `tuple[int, ...]` | `BOUNDARY_AGENT_COUNTS` | agent数量元组 |
| `skip_single` | `bool` | `False` | 是否跳过n=1的单agent场景（单agent无竞争，部分场景无意义） |

**使用方式**：

```python
from lib.testing import parametrize_agent_counts, generate_agents

@parametrize_agent_counts
def test_load_balancing(n_agents, resolver):
    \"\"\"自动测试 N=1,2,3,5,10 个agent场景下的负载均衡\"\"\"
    agents = generate_agents(n_agents, load_strategy="ascending")
    # ... 测试逻辑

# 跳过单agent场景
@parametrize_agent_counts(skip_single=True)
def test_no_starvation(n_agents, resolver):
    \"\"\"至少2个agent才有竞争场景\"\"\"
    agents = generate_agents(n_agents, load_strategy="extremes")
    # ... 测试逻辑
```

---

### 断言参考（BOUNDARY_ASSERTIONS）

`BOUNDARY_ASSERTIONS` 字典提供了边界场景的标准断言说明文档：

| Key | 断言说明 |
|-----|----------|
| `"no_starvation"` | 所有capability匹配的候选agent中，低负载/高优先级agent应在合理轮次内被选中 |
| `"deterministic"` | 相同输入应产生相同结果，无随机波动 |
| `"timeout_protection"` | 涉及锁/等待的操作必须有超时机制 |
| `"idempotent_rejection"` | 重复拒绝同一agent不应改变拒绝集合大小 |
| `"defensive_copy"` | 传入的agents字典不应被resolve方法修改 |
| `"empty_input"` | 空agents字典/None输入应返回ESCALATED升级而非崩溃 |
| `"invalid_values"` | 负优先级、超范围负载等无效值应被优雅处理或拒绝 |
| `"tie_breaking"` | 所有agent优先级和负载完全相同时应有确定性的平局打破机制 |
| `"missing_fields"` | 缺少必要字段的agent应被优雅处理或跳过 |
| `"large_scale"` | 大规模agent场景(50/100+)应性能正常不超时 |

---

### 边缘场景函数（异常与极端输入测试）

#### `generate_malformed_agents()`

```python
def generate_malformed_agents(
    variant: str = "missing_priority",
    base_count: int = 3,
) -> dict[str, dict[str, Any]]
```

生成包含异常/畸形数据的agent字典，用于错误处理测试。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `variant` | `str` | `"missing_priority"` | 畸形数据类型，见下表 |
| `base_count` | `int` | `3` | 基础正常agent数量 |

**variant 可选值**：

| 值 | 说明 |
|----|------|
| `"missing_priority"` | 部分agent缺少priority字段 |
| `"missing_load"` | 部分agent缺少load字段 |
| `"missing_capabilities"` | 部分agent缺少capabilities字段 |
| `"negative_priority"` | 优先级为负数 |
| `"negative_load"` | 负载为负数 |
| `"load_over_100"` | 负载超过100 |
| `"empty_capabilities"` | capabilities为空列表 |
| `"mixed_roles"` | 混合多种角色（developer/architect/reviewer） |
| `"extreme_priority_range"` | 极端优先级范围（0和999） |

**示例**：

```python
from lib.testing import generate_malformed_agents

# 测试缺少load字段的容错
agents = generate_malformed_agents("missing_load")
result = resolver.resolve(report, agents=agents)
# 应正常返回或优雅升级，而非抛出KeyError崩溃
```

---

#### `generate_tie_scenario()`

```python
def generate_tie_scenario(count: int = 5) -> dict[str, dict[str, Any]]
```

生成完全平局场景：所有agent优先级和负载完全相同，用于测试平局打破机制的确定性。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `count` | `int` | `5` | agent数量 |

**返回**：所有agent priority=2, load=50, capabilities=["coding"]

**示例**：

```python
from lib.testing import generate_tie_scenario

agents = generate_tie_scenario(10)
result1 = resolver.resolve(report, agents=agents)
result2 = resolver.resolve(report, agents=agents)
assert result1.winner == result2.winner  # 确定性：相同输入必须返回相同结果
```

---

#### `generate_partial_capability_match()`

```python
def generate_partial_capability_match(
    count: int = 5,
    required_cap: str = "design",
    matching_count: int = 2,
) -> dict[str, dict[str, Any]]
```

生成部分agent能力匹配场景：部分agent具备所需能力，其他不具备，用于验证能力过滤逻辑。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `count` | `int` | `5` | 总agent数 |
| `required_cap` | `str` | `"design"` | 需要的能力名称 |
| `matching_count` | `int` | `2` | 拥有该能力的agent数量（0表示无人匹配） |

**返回**：前matching_count个agent拥有required_cap能力，其余只有coding能力，负载按ascending策略分布。

**示例**：

```python
from lib.testing import generate_partial_capability_match

# 测试：5个agent中仅前2个具备"design"能力，应从中选择负载最低的
agents = generate_partial_capability_match(5, "design", matching_count=2)
report = ConflictReport(..., required_capability="design")
result = resolver.resolve(report, agents=agents)
assert result.winner in ["agent_0", "agent_1"]  # 只能从匹配的agent中选择

# 测试：无agent具备所需能力，应升级到人工处理
agents = generate_partial_capability_match(5, "architecture", matching_count=0)
report = ConflictReport(..., required_capability="architecture")
result = resolver.resolve(report, agents=agents)
assert result.status == ResolutionStatus.ESCALATED
assert result.needs_human is True
```

---

#### `edge_scenarios()`

```python
def edge_scenarios() -> list[MultiAgentScenario]
```

生成全套边缘测试场景，一键覆盖极端输入和异常情况，返回预构建的`MultiAgentScenario`列表。

**包含场景**（共18个）：

| 类别 | 场景名称 | 说明 | metadata edge_type |
|------|---------|------|-------------------|
| 空/单输入 | `edge_empty_agents` | 空agents字典（n=0） | `empty_input` |
| | `edge_single_agent` | 单agent场景（无竞争） | `single_agent` |
| 平局 | `edge_all_tie_5` | 5个agent完全平局 | `tie_breaking` |
| | `edge_all_tie_10` | 10个agent完全平局 | `tie_breaking` |
| 大规模 | `edge_large_scale_50` | 50个agent大规模场景 | `large_scale` |
| | `edge_large_scale_100` | 100个agent超大规模场景 | `large_scale` |
| 畸形数据（9种） | `edge_malformed_missing_priority` | 缺少priority字段 | `malformed` |
| | `edge_malformed_missing_load` | 缺少load字段 | `malformed` |
| | `edge_malformed_missing_capabilities` | 缺少capabilities字段 | `malformed` |
| | `edge_malformed_negative_priority` | 负优先级 | `malformed` |
| | `edge_malformed_negative_load` | 负负载 | `malformed` |
| | `edge_malformed_load_over_100` | 负载>100 | `malformed` |
| | `edge_malformed_empty_capabilities` | 空capabilities列表 | `malformed` |
| | `edge_malformed_mixed_roles` | 混合角色 | `malformed` |
| | `edge_malformed_extreme_priority_range` | 极端优先级(0/999) | `malformed` |
| 能力匹配 | `edge_partial_capability_match` | 部分agent匹配(2/5) | `partial_match` |
| | `edge_no_capability_match` | 无agent匹配应升级 | `no_match` |
| | `edge_all_capability_match` | 全部agent匹配 | `all_match` |

**示例：综合边缘场景测试**

```python
import pytest
from lib.testing import edge_scenarios
from lib.collaboration.conflict_resolution import ConflictResolver, ConflictReport, ConflictType, ResolutionStatus

class TestEdgeScenariosComprehensive:
    @pytest.fixture
    def resolver(self):
        return ConflictResolver()

    @pytest.mark.parametrize("scenario", edge_scenarios(), ids=lambda s: s.name)
    def test_all_edge_scenarios(self, resolver, scenario):
        \"\"\"所有边缘场景必须正常返回ArbitrationResult，不崩溃。\"\"\"
        if scenario.agent_count < 2:
            pytest.skip(f"单agent或空场景跳过（n={scenario.agent_count}）")

        ids = list(scenario.agents.keys())
        edge_type = scenario.metadata.get("edge_type", "unknown")
        required_cap = scenario.metadata.get("required_cap", "coding")

        report = ConflictReport(
            reporter_id=ids[0],
            opponent_id=ids[-1],
            conflict_type=ConflictType.RESPONSIBILITY,
            description=scenario.description,
            task_id=f"TASK-EDGE-{scenario.name}",
            required_capability=required_cap,
        )

        result = resolver.resolve(report, agents=scenario.agents)

        # 通用断言：必须返回有效结果
        assert result.status in (ResolutionStatus.RESOLVED, ResolutionStatus.ESCALATED)

        # 无能力匹配场景专项断言：必须升级
        if edge_type == "no_match":
            assert result.status == ResolutionStatus.ESCALATED
            assert result.needs_human is True
            assert result.winner is None
            return

        # 大规模场景性能断言：必须<5秒
        if edge_type == "large_scale":
            assert elapsed < 5.0

        # 有winner时必须在agents中且具备所需能力
        if result.status == ResolutionStatus.RESOLVED and result.winner:
            assert result.winner in scenario.agents
            assert required_cap in scenario.agents[result.winner]["capabilities"]
```

---

## 使用示例：完整测试模板

```python
import pytest
from lib.collaboration.conflict_resolution import ConflictType, ConflictReport, ConflictResolver
from lib.testing import (
    generate_agents,
    parametrize_agent_counts,
    BOUNDARY_AGENT_COUNTS,
)

@pytest.fixture
def resolver():
    return ConflictResolver()

@parametrize_agent_counts
def test_load_balancing_boundary(resolver, n_agents):
    \"\"\"N个agent场景下，负载均衡应选择真正负载最低的agent\"\"\"
    agents = generate_agents(n_agents, load_strategy="ascending")
    ids = list(agents.keys())
    if n_agents == 1:
        reporter = opponent = ids[0]
    else:
        reporter, opponent = ids[0], ids[-1]

    report = ConflictReport(
        reporter_id=reporter,
        opponent_id=opponent,
        conflict_type=ConflictType.RESPONSIBILITY,
        description=f"{n_agents}个agent负载均衡测试",
        task_id=f"TEST-LB-{n_agents}",
        required_capability="coding",
    )
    result = resolver.resolve(report, agents=agents)

    if n_agents == 1:
        assert result.winner == reporter
    else:
        loads = {aid: info["load"] for aid, info in agents.items()}
        assert loads[result.winner] == min(loads.values())
```

---

## 完整示例文件

| 文件 | 测试数 | 说明 |
|------|--------|------|
| [test_testing_template_demo.py](../../tests/test_testing_template_demo.py) | 42 | 模板库功能演示与自验证测试，覆盖所有基础API用法 |
| [test_conflict_resolution_boundary.py](../../tests/test_conflict_resolution_boundary.py) | 22 | ConflictResolver模块边界测试用例（使用parametrize_agent_counts） |
| [test_conflict_resolution_edge_cases.py](../../tests/test_conflict_resolution_edge_cases.py) | 72 | 边缘场景测试用例，覆盖空输入、畸形数据、平局、大规模、能力匹配等维度 |

---

## 相关模式

- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [增量验证+回归验证双层策略](../../../docs/retrospective/patterns/architecture-patterns/incremental-regression-verification.md)
- [多智能体冲突解决机制复盘](../../../docs/retrospective/reports/task-reports/retrospective-conflict-resolution-mechanism-20260708/retrospective-report.md)

---

**[返回索引](../README.md)** | 上一章 ← [全局常量](14-constants.md)
