---
id: "configurable-by-default-principle"
source: "external: 不存在-docs/retrospective/reports/task-reports/retrospective-conflict-resolution-mechanism-20260708/retrospective-report.md"
domain: "code"
layer: "code"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "comprehensive"

[bindings]
rules = []
references = [
  "../methodology-patterns/governance-strategy/implement-review-harden-sop.md",
  "../methodology-patterns/governance-strategy/defensive-programming-first-principles.md",
  "dynamic-path-derivation.md"
]
skills = []
---
# 可配置性默认原则：业务规则注入而非硬编码

## 模式概述

从多智能体冲突解决机制的技术分歧仲裁规则硬编码问题（D5）中萃取的设计原则。初始实现将"最佳实践关键词"硬编码在类中，导致无法根据不同项目的技术栈调整规则，扩展性差。修复方案是通过构造函数参数注入，提供合理默认值但允许覆盖。

**核心洞察**：业务规则、阈值、关键词、权重表这类"可能因场景/项目/用户而变"的值，从第一行代码开始就应该支持注入，而不是"先硬编码上线，以后需要再改"——重构硬编码的成本远高于一开始就设计为可配置。

## 问题场景

### 反模式：硬编码的"快速上线"陷阱

```python
# ❌ 反模式：硬编码关键词
class ConflictResolver:
    def _is_best_practice(self, proposal: str) -> bool:
        # 硬编码的最佳实践关键词——只适用于当前项目
        return any(kw in proposal.lower() for kw in [
            "exception", "try", "单一职责", "最小改动"
        ])
```

**问题**：
1. 不同项目/团队有不同的最佳实践（如函数式vs面向对象）
2. 多语言项目需要不同语言的关键词
3. 测试时无法注入mock规则验证逻辑
4. 每次调整规则都要改代码+重新部署
5. 规则变化时无法通过配置文件热更新

---

### 正解模式：构造函数注入+合理默认

```python
# ✅ 正解：可配置+默认值
BEST_PRACTICE_KEYWORDS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "exception_over_error_code": (("异常抛出", "exception", "try"), ("错误码", "error code")),
    "single_responsibility": (("单一职责", "拆分", "modular"), ("大函数", "monolithic")),
}

class ConflictResolver:
    def __init__(
        self,
        logger: Callable[[str], None] | None = None,
        lock_timeout_seconds: int = DEFAULT_LOCK_TIMEOUT_SECONDS,
        best_practice_rules: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] | None = None,
    ):
        self._logger = logger or (lambda msg: None)
        self._lock_timeout = lock_timeout_seconds
        self._bp_rules = best_practice_rules or BEST_PRACTICE_KEYWORDS
```

**优势**：
1. 开箱即用：不传参数使用合理默认值
2. 灵活扩展：新项目/新场景可注入自定义规则
3. 易于测试：单元测试可注入极简规则集
4. 配置外置：规则可移到YAML/TOML配置文件
5. A/B测试：不同规则集可在运行时对比效果

## 哪些内容应该可配置？

### 应该默认可配置的内容

| 类型 | 示例 | 配置方式 |
|------|------|---------|
| **业务规则表** | 关键词匹配规则、仲裁权重、评分标准 | 构造函数注入dict |
| **阈值/超时** | 锁超时时间、重试次数、负载阈值 | 构造函数注入int/float，带常量默认值 |
| **策略选择** | 负载均衡策略、排序算法、缓存淘汰策略 | 构造函数注入策略对象/枚举 |
| **功能开关** | 是否启用资源隔离、是否记录详细日志 | 构造函数注入bool |
| **外部依赖** | logger、存储后端、通知客户端 | 构造函数注入接口/回调 |

### 不需要配置的内容（可以硬编码）

| 类型 | 示例 | 理由 |
|------|------|------|
| **协议常量** | HTTP状态码、标准错误码 | 由标准定义，不会因场景变化 |
| **数学/物理常量** | π、e、光速 | 自然常数，永恒不变 |
| **内部实现细节** | 私有辅助方法、局部临时变量 | 封装在内部，外部无需感知 |
| **类型定义** | Enum、dataclass字段名 | 属于类型系统的一部分 |

## 判断标准：三个问题快速决策

写代码时遇到常量/规则/阈值，问自己三个问题：

1. **"不同的用户/项目/场景会不会需要不同的值？"**
   - 会 → 可配置
   - 不会 → 继续问Q2

2. **"测试的时候会不会需要传入一个简单的/极端的值来验证逻辑？"**
   - 会 → 可配置（测试友好性）
   - 不会 → 继续问Q3

3. **"未来6个月内这个值会不会因为需求变化而调整？"**
   - 可能会 → 可配置（可维护性）
   - 绝对不会 → 可以硬编码

> **经验法则**：如果三个问题中有一个答案是"是"或"可能会"，就设计为可配置。多写一个参数的成本远低于未来重构硬编码的成本。

## 实现模式

### 模式1：模块级默认常量 + None覆盖

```python
# 模块级默认值（作为文档）
DEFAULT_LOCK_TIMEOUT = 300  # 5分钟
DEFAULT_RETRY_COUNT = 3

class ResourceManager:
    def __init__(
        self,
        lock_timeout: int = DEFAULT_LOCK_TIMEOUT,
        retry_count: int = DEFAULT_RETRY_COUNT,
        *,  # 关键字参数分隔，防止位置传参错误
        custom_rules: dict | None = None,
    ):
        self._lock_timeout = lock_timeout
        self._retry_count = retry_count
        self._rules = custom_rules if custom_rules is not None else self._default_rules()
```

**要点**：
- 默认值定义为模块级常量（全大写），方便文档生成和引用
- 可选配置参数用None做哨兵值，`param = user_value or default`（但注意0/False/空集合的情况，用`if x is not None`判断）
- 复杂配置建议用关键字-only参数（`*`分隔）

---

### 模式2：配置对象/数据类聚合

当配置项超过5个时，聚合为配置数据类：

```python
from dataclasses import dataclass, field

@dataclass
class ConflictResolverConfig:
    lock_timeout_seconds: int = 300
    enable_resource_isolation: bool = True
    max_escalation_depth: int = 3
    best_practice_rules: dict = field(default_factory=lambda: BEST_PRACTICE_KEYWORDS)
    logger: Callable[[str], None] | None = None

class ConflictResolver:
    def __init__(self, config: ConflictResolverConfig | None = None):
        self._config = config or ConflictResolverConfig()
```

**优势**：
- 参数列表不会爆炸式增长
- 配置可序列化/反序列化（从YAML/TOML加载）
- 配置可在多处复用传递
- 新增配置项不改变构造函数签名

---

### 模式3：策略对象注入（行为可配置）

当变化的是"算法/行为"而非"值"时，注入策略对象：

```python
from typing import Protocol

class LoadBalancingStrategy(Protocol):
    def select(self, candidates: list[AgentInfo]) -> AgentInfo: ...

class LeastLoadStrategy:
    def select(self, candidates):
        return min(candidates, key=lambda a: a.load)

class PriorityFirstStrategy:
    def select(self, candidates):
        return sorted(candidates, key=lambda a: (-a.priority, a.load))[0]

class TaskScheduler:
    def __init__(self, strategy: LoadBalancingStrategy | None = None):
        self._strategy = strategy or LeastLoadStrategy()
```

## 反模式清单

1. **❌ 魔法数字直接写在代码里**
   ```python
   time.sleep(30)  # 为什么是30？30秒够吗？不同环境需要不同值吗？
   ```
   → 改为：`time.sleep(self._config.retry_interval_seconds)`

2. **❌ 硬编码的业务规则表**
   ```python
   if error_code in [400, 401, 403, 404, 429, 500, 502, 503]:  # 这个列表会变吗？
   ```
   → 改为：从配置注入可重试状态码集合

3. **❌ 用布尔标志控制多种行为**
   ```python
   def process(use_fast_mode=False, enable_logging=True, strict_mode=False):
   ```
   → 参数超过3个时，考虑配置对象

4. **❌ 默认值是可变对象（经典Python坑）**
   ```python
   def __init__(self, rules={}):  # ❌ 所有实例共享同一个dict！
       self.rules = rules
   ```
   → 正确写法：
   ```python
   def __init__(self, rules: dict | None = None):
       self.rules = rules if rules is not None else {}
   ```

5. **❌ 配置参数不做验证**
   ```python
   self._timeout = timeout  # 如果传入-1或1000000会怎么样？
   ```
   → 在`__post_init__`或构造函数中验证参数范围：
   ```python
   if timeout <= 0:
       raise ValueError(f"timeout must be positive, got {timeout}")
   if timeout > 3600:
       warnings.warn(f"timeout {timeout}s > 1h, may cause hang")
   ```

## 验证清单

开发新模块时，逐项确认：

- [ ] 所有业务规则/阈值/超时都作为构造函数参数
- [ ] 有合理的模块级默认常量
- [ ] 可选参数用None做哨兵值，正确处理0/False/空集合
- [ ] 可变默认值使用`field(default_factory=...)`或None判断
- [ ] 超过5个配置项时聚合为配置数据类
- [ ] 行为变化使用策略对象注入而非if/else分支
- [ ] 配置参数有基本的边界验证
- [ ] 单元测试可以注入自定义配置验证边界

## 权衡思考

可配置性不是免费的，需要权衡：

| 优势 | 成本 |
|------|------|
| ✅ 灵活性高，适应不同场景 | ❌ 参数增多，API表面变大 |
| ✅ 测试友好，可注入mock | ❌ 配置组合爆炸，需要测试更多组合 |
| ✅ 可维护性好，改配置不用改代码 | ❌ 过度配置导致"什么都能改"但没人知道怎么改 |
| ✅ 支持配置文件外置 | ❌ 文档负担增加 |

**实用建议**：
- 库/框架代码：高优先级，必须可配置
- 业务应用代码：核心规则可配置，一次性脚本可以简单
- 如果拿不准：先设计为可配置——从可配置改为硬编码很简单，反过来很难

## 适用场景

- 仲裁/调度/评分类核心机制
- 可复用库和框架代码
- 需要适配多租户/多项目/多环境的模块
- 规则可能随产品迭代频繁调整的功能
- 所有需要单元测试mock依赖的代码

## 相关模式

- ["实现→审查→加固"三段式SOP](../methodology-patterns/governance-strategy/implement-review-harden-sop.md)：阶段3加固的核心措施之一
- [防御性编程第一性原理](../methodology-patterns/governance-strategy/defensive-programming-first-principles.md)：配置默认值的哲学基础
- [dynamic-path-derivation.md](dynamic-path-derivation.md)：路径配置的动态推导模式
