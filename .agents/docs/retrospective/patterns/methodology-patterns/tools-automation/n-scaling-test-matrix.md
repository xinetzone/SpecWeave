---
id: "n-scaling-test-matrix"
source: "external: 不存在-docs/retrospective/reports/task-reports/retrospective-conflict-resolution-mechanism-20260708/insight-extraction.md"
domain: "methodology"
layer: "tools-automation"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "comprehensive"

[bindings]
rules = []
references = [
  "../governance-strategy/implement-review-harden-sop.md",
  "../governance-strategy/test-coverage-diminishing-returns.md",
  "model-to-test-matrix.md"
]
skills = []
---
# N-scaling测试矩阵：调度/仲裁/选择类算法的参与者规模覆盖法

## 模式概述

从多智能体冲突解决机制的负载均衡/优先级调度Bug（D3/D4）中萃取的测试方法论。初始26个测试行覆盖率100%，但因主要使用N=2个agent场景，未发现N≥3时才暴露的排序/饥饿bug。

**核心洞察**：行覆盖率只衡量"代码是否被执行"，不衡量"所有输入组合是否被测试"。涉及多对象比较、选择、排序、调度、负载均衡的算法，其bug往往在参与者数量变化时暴露——尤其是N=3这个临界点。

## 问题场景

### 反模式：只测Happy Path的N=2场景

```python
# ❌ 反模式：只测2个agent，N=3时bug暴露
def test_load_balancing():
    agents = {"a": AgentInfo(load=30), "b": AgentInfo(load=50)}
    selected = resolver._balance_load(agents, task)
    assert selected.id == "a"  # N=2正确，但只比较前2个的bug在N=3时才暴露
```

**问题**：
1. 只比较前2个候选的bug（D3）在N=2时测试通过
2. 优先级相等时跳过排序的bug（D4）在N=2且优先级不等时无法发现
3. 饥饿问题（低负载/低优先级永远选不上）需要N≥3才能观察到
4. "行覆盖率100%"给人虚假的安全感

---

### 正解：N-scaling六档测试矩阵

对于所有涉及多对象选择、排序、仲裁、调度、负载均衡的算法，测试必须覆盖以下六档规模：

| N（参与者数量） | 测试目的 | 典型bug发现 |
|----------------|---------|------------|
| **N=0** | 空输入/异常处理 | 空列表崩溃、无候选时的降级策略 |
| **N=1** | 单参与者快速路径 | 单候选时不必要的比较逻辑、self-winner问题 |
| **N=2** | 基础两两比较 | 基础功能正确（但仅此一档不够！） |
| **N=3** | ⚠️ **排序/选择边界（最容易出bug的规模）** | 只比较前2个、并列处理、第三者插足 |
| **N=5** | 小规模多参与者 | 部分算法在N>4时分支变化、轮询调度验证 |
| **N=10** | 性能基本验证 | O(n²)算法性能爆炸、大规模下的公平性 |

> **为什么N=3是最高危档位？** 绝大多数比较/选择bug在从"两两比较"扩展到"三者及以上"时暴露：
> - "取前两个比较"的硬编码逻辑在N=2时正确
> - "优先级相等则跳过排序"在N=2且一高一低时无法触发
> - "A>B, B>C 但 C>A"的循环逻辑需要第三者才能暴露
> - 公平性/饥饿问题需要至少3个参与者才能观察到"谁总是轮不到"

## 标准实现

### 步骤1：参数化工厂函数

```python
def generate_agents(n: int, *, load_range=(0, 100), priority_range=(1, 5)) -> dict[str, AgentInfo]:
    """生成N个具有不同负载和优先级的agent"""
    return {
        f"agent_{i}": AgentInfo(
            load=(i * 13) % (load_range[1] - load_range[0]) + load_range[0],
            priority=(i % (priority_range[1] - priority_range[0] + 1)) + priority_range[0],
        )
        for i in range(n)
    }
```

### 步骤2：参数化测试覆盖所有档位

```python
import pytest

@pytest.mark.parametrize("n", [0, 1, 2, 3, 5, 10])
def test_load_balancing_selects_least_loaded(n: int):
    """负载均衡在所有N规模下都选择最低负载的agent"""
    agents = generate_agents(n)
    if n == 0:
        with pytest.raises(NoAvailableAgentError):
            resolver._balance_load(agents, task)
        return
    selected = resolver._balance_load(agents, task)
    min_load = min(a.load for a in agents.values())
    assert selected.load == min_load
```

### 步骤3：针对N=3的专项边界测试

```python
def test_priority_scheduling_with_tie_at_n3():
    """N=3时，前两个优先级相同，正确选择第三个"""
    agents = {
        "high_a": AgentInfo(priority=5, load=80),
        "high_b": AgentInfo(priority=5, load=90),
        "medium": AgentInfo(priority=4, load=10),
    }
    selected = resolver._priority_schedule(agents, task)
    # 高优先级组(5)内选负载最低的 → high_a，而不是跳过并列选medium
    assert selected.id == "high_a"

def test_load_balancing_at_n3_finds_lowest():
    """N=3时，最低负载的是第三个agent，不被遗漏"""
    agents = {
        "a": AgentInfo(load=50),
        "b": AgentInfo(load=60),
        "c": AgentInfo(load=20),  # 最低负载在第三位
    }
    selected = resolver._balance_load(agents, task)
    assert selected.id == "c"  # 如果只比较前2个，会错误选a
```

### 步骤4：公平性/饥饿测试（需要N≥3）

```python
def test_no_starvation_at_n5():
    """N=5时，连续调度100次，所有agent都至少被选中一次"""
    agents = generate_agents(5)
    selected_ids = set()
    for _ in range(100):
        selected = resolver._balance_load(agents, task)
        selected_ids.add(selected.id)
        agents[selected.id].load += 10  # 模拟选中后负载增加
    assert selected_ids == set(agents.keys())  # 无饥饿
```

## 适用算法类型

| 算法类型 | 为什么N-scaling关键 | 高危档位 |
|---------|-------------------|---------|
| **负载均衡** | 最低负载可能不在前2个 | N=3 |
| **优先级调度** | 优先级并列处理逻辑 | N=3（含并列） |
| **排序/Top-K** | 比较器实现错误在N≥3时暴露 | N=3 |
| **仲裁/投票** | kingmaker效应、循环投票 | N=3（奇数） |
| **轮询调度** | 轮询指针回绕、模运算边界 | N=5 |
| **资源分配** | 剩余资源碎片问题 | N=3, N=5 |
| **一致性协议** | 拜占庭/脑裂场景 | N=3（最小奇数集群） |
| **淘汰/选举** | kingmaker king of the mountain | N=3 |

## 反模式清单

1. **❌ 只测N=2，认为"两两比较正确则N>2也正确"**
   - N=2只能验证A和B的关系，无法验证B和C、A和C的关系
2. **❌ 行覆盖率100%就认为测试充分**
   - 行覆盖≠输入空间覆盖，N=2可能覆盖了所有代码行但没覆盖所有逻辑分支
3. **❌ 只测Happy Path，不测空输入和单输入**
   - N=0和N=1的边界测试发现的崩溃类bug占比很高
4. **❌ 生成N个相同属性的参与者**
   - 所有agent负载相同的测试无法验证"正确选择最低负载"，需要属性多样化
5. **❌ 忽略公平性/饥饿测试**
   - 只验证每次选择正确，不验证多次调度后是否所有参与者都有机会

## 验证清单

为调度/仲裁/选择类模块编写测试时，逐项确认：

- [ ] N=0：空输入有正确处理（返回空/抛异常/降级）
- [ ] N=1：单参与者快速路径正确
- [ ] N=2：基础两两比较正确
- [ ] N=3：排序/选择边界场景覆盖（含并列、第三者最优）
- [ ] N=5：小规模多参与者正确
- [ ] N=10：性能在可接受范围（无O(n²)爆炸）
- [ ] N≥3：公平性/饥饿测试（连续调度后所有参与者都被选中）
- [ ] 使用参数化测试避免重复代码

## 与其他模式的关系

- **与model-to-test-matrix的区别**：model-to-test-matrix是将理论模型（分层/决策树）转化为测试矩阵，N-scaling是专门针对"参与者数量"这一维度的测试覆盖方法论，二者互补
- **与implement-review-harden-sop的关系**：N-scaling是三段式SOP八维检查中第3维（边界：N≥3场景覆盖）的具体实施方法
- **与test-coverage-diminishing-returns的关系**：N=10以上继续增加N带来的覆盖收益递减，六档矩阵是性价比最优的覆盖方案

## 适用场景

- 多智能体任务分配与仲裁
- 负载均衡器、调度器
- 排序算法、Top-K选择
- 投票/选举/一致性协议
- 资源分配与竞争机制
- 任何"从N个候选中选1个或K个"的算法

## 成功案例

| 项目 | 缺陷 | 发现方式 | N-scaling能否预防 |
|------|------|---------|------------------|
| 冲突解决机制 | D3负载均衡只比前2个agent | 主动代码审查 | ✅ N=3专项测试可发现 |
| 冲突解决机制 | D4优先级并列跳过排序 | 主动代码审查 | ✅ N=3（含并列）测试可发现 |
