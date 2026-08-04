# P2 阶段实施指南：模型适配层延迟治理

> 整合架构演进脉络、压测结论、接口定义与 P1-P2 实施步骤，
> 形成 P2 阶段完整实施指南（源文件已合并归档）。
> 日期：2026-08-03 | 状态：T1 已完成，T2-T5 待实施

## 1. 架构演进脉络

```
P0 骨架 ──► P1 模型适配层 ──► P2 延迟治理（本文档）──► P2 整合
```

| 阶段 | 核心交付 | 验证 |
|------|---------|------|
| P0 | `router.py` ModelRouter + 4 种策略 | 12 用例通过（`test_router.py`） |
| P1 | `model_provider.py` 模型适配层 + 延迟量测 | 53 用例通过 + 2 个压测脚本 |
| P2 | 延迟治理（预算/超时/缓存/熔断）+ 接入 main.py | T1 已实现，T2-T5 待实施 |

## 2. 压测结论（实施依据）

P2 优化必须建立在已量化的压测数据上，避免凭经验设定阈值。

### 2.1 路由判定延迟（非瓶颈）

`stress_router_latency.py` 压测结果：

| 配置 | 路由判定开销 | 吞吐 |
|------|------------|------|
| 并发 1 | 1.13us/次 | 503,236 QPS |
| 并发 4 | 1.63us/次 | 428,640 QPS |
| 并发 16 | 1.41us/次 | 455,021 QPS |

**结论**：路由判定为纯内存决策，开销 ~1-2us、与并发无关，吞吐 43-50 万 QPS，**绝非瓶颈**。真实模型推理延迟为 100ms~数秒，路由判定在端到端延迟中占比可忽略（<0.3%）。

**架构含义**：正常模式（完整策略评估）可放心用于多数任务，无需频繁切换直通模式；直通模式作为简单任务的可选优化保留。

### 2.2 真实模型延迟（抖动扫描）

`stress_model_latency.py` 集成 ModelProvider，测量模型推理延迟（200ms 基准），并发 50 扫描不同抖动幅度：

| 抖动(ms) | mean | p50 | p95 | p99 | stdev | max |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 200.4 | 200.4 | 201.1 | 201.3 | 0.3 | 201.6 |
| 50 | 198.9 | 198.1 | 247.1 | 249.4 | 29.3 | 250.1 |
| 100 | 199.2 | 197.0 | 289.1 | 295.8 | 56.7 | 298.8 |
| 200 | 202.9 | 200.6 | 378.6 | 395.4 | 115.0 | 399.2 |

**结论**：抖动幅度越大，延迟分布越分散（stdev 0.3→115ms），p99 越远离均值（201→395ms）。**真实网络场景下应以 p99 而非均值作为延迟预算依据**，否则 5% 的慢请求会超预算。

### 图表区：延迟分布可视化（并发 50）

![模型延迟分布（并发50）· 不同抖动幅度 p50/p95/p99](images/latency-distribution.png)

> 图表数据源：`stress_model_latency.py --concurrency 50` 压测结果。

### 2.3 实施原则

- **以 p99 为延迟预算依据**，而非均值
- **接口（`ModelProvider.invoke`）保持稳定**，所有优化为内部实现
- **并发 50 不放大延迟**（线程开销 <1ms），线程化非瓶颈，优化重心在模型层

## 3. ModelProvider 接口定义（P1 已交付）

`model_provider.py` 提供统一模型调用抽象，屏蔽供应商差异，是 P2 优化的承载接口。

### 3.1 抽象基类

```python
class ModelProvider:
    def invoke(self, model: str, prompt: str, **kwargs: Any) -> str:
        """调用指定模型，返回生成的文本。"""
        raise NotImplementedError

    def get_latency_ms(self) -> float:
        """返回最近一次 invoke 调用的耗时（毫秒）。"""
        raise NotImplementedError
```

### 3.2 核心实现

| 实现 | 用途 | 关键参数 |
|------|------|---------|
| `LocalProvider` | 本地 mock，压测可控复现 | `latency_ms`（固定延迟）、`response_prefix` |
| `RemoteProvider` | 远程 LLM，模拟真实网络波动 | `latency_ms`（基准）、`jitter_ms`（抖动） |

### 3.3 网络延迟模拟（RemoteProvider）

```python
provider = RemoteProvider(
    base_url="http://localhost:8000",
    latency_ms=200,
    jitter_ms=50,
)
```

每次调用实际延迟 = 基准 + 均匀随机抖动（[−jitter, +jitter]），实测 8 样本落在 150.8~250.5ms、均值 198.5ms，符合 200±50 预期。

### 3.4 工厂函数

```python
build_default_provider(
    provider_type="local" | "remote",
    latency_ms=0,
    jitter_ms=0,          # 仅 remote 生效
    **kwargs,             # base_url / api_key / timeout 等透传
) -> ModelProvider
```

### 3.5 延迟量测体系（计时包装）

`_TimedProviderMixin` 提供非侵入式计时：执行 `invoke` 时用 `perf_counter` 记录耗时，存于 `_last_latency_ms`，经 `get_latency_ms()` 读取。路由逻辑与供应商调用均不感知量测，实现"量测与业务解耦"。

## 4. P2 优化目标

| 指标 | 当前基线 | P2 目标 |
|------|---------|---------|
| p99 延迟 | 抖动相关（200~395ms） | ≤ 预算 p99（如 300ms） |
| 并发吞吐 | 50 并发稳定 | ≥ 50 并发稳定 |
| 超时率 | 未设超时 | <1% |

## 5. 实施步骤（T1-T5）

### T1 延迟预算（✅ 已完成）

**目标**：ModelProvider 增加 p99 预算属性 + 路由参考。

**已实现代码**（model_provider.py）：

```python
class ModelProvider:
    LATENCY_HISTORY_SIZE = 500

    def __init__(self):
        self._latency_history = deque(maxlen=self.LATENCY_HISTORY_SIZE)
        self.p99_budget_ms = 0.0  # 0 表示未设预算

    def set_p99_budget(self, budget_ms): ...
    def record_latency_ms(self, latency_ms): ...   # 每次 invoke 自动记录
    def p99_latency_ms(self): ...                   # 计算样本 p99
    def is_within_budget(self): ...                 # 判定是否超预算
```

`_TimedProviderMixin._measure` 自动将每次调用耗时记入历史，供 p99 计算。

**验证**（test_model_provider.py TestLatencyBudget）：
- 延迟 10ms、预算 20ms → 在预算内 ✅
- 延迟 100ms、预算 50ms → 超预算 ✅
- 未设预算 → 通过 ✅
- p99 计算逼近最大样本 ✅
- 样本记录正确 ✅

**接入路由**（下一步）：

```python
# 路由层降级决策参考预算
if not provider.is_within_budget():
    model = fallback_strategy.route(...)  # 降级到便宜模型
```

### T2 超时与重试

**目标**：`RemoteProvider` 落地强制超时 + 指数退避重试。

**实施步骤**：
1. **强制超时**：在 `RemoteProvider._call` 中落地 `timeout` 硬超时（当前为参数占位）
2. **指数退避重试**：新增 `retry` + `backoff` 参数，仅对幂等请求重试
3. **超时计入统计**：超时样本按最大延迟计入，暴露真实尾部

**验收**：
- 超时请求不卡死，正常返回
- 重试次数 ≤ 3，退避收敛
- 超时率可观测

### T3 连接池与并发

**目标**：复用连接，控制并发上限。

**实施步骤**：
1. **连接池**：集成 `httpx.Client` 或 `requests.Session`，全局复用
2. **并发上限**：`RemoteProvider` 增加 `max_concurrency`，用信号量控制
3. **批量路由**：路由层批量提交，减少框架层调用

**验收**：
- 并发 50 下连接数受限、吞吐稳定
- 无 TLS 握手重复开销

### T4 缓存与降级

**目标**：结果缓存 + 降级链 + 熔断。

**实施步骤**：
1. **结果缓存**：按 `(prompt哈希, model)` 缓存，命中则跳过模型调用
2. **降级链**：强模型超时 → 降级便宜模型 → 兜底默认结果
3. **熔断**：连续超时计数达到阈值，暂缓调用该模型一段时间

**验收**：
- 重复任务命中缓存，不重复调用模型
- 降级链可达，熔断后自动恢复

### T5 压测回归

**目标**：扩展 `stress_model_latency.py` 覆盖上述路径。

**实施步骤**：
1. **超时场景**：压测中注入超时（如 latency > timeout），验证不卡死
2. **缓存命中**：压测重复任务，验证缓存命中率与延迟改善
3. **降级触发**：构造超预算模型，验证降级链生效
4. **p99 达标**：以 p99 预算为验收，验证各抖动下 p99 达标

**验收**：
- 新增用例全部通过，无回归
- p99 在预算内、超时率 <1%

## 6. 实施顺序与依赖

```
T1 延迟预算（已完成）→ T2 超时重试 → T3 连接池 → T4 缓存降级 → T5 压测回归
```

- T2 依赖 T1 的 p99 预算（超时阈值）
- T3 独立，可与 T2 并行
- T4 依赖 T2（降级依赖超时判定）
- T5 为最终回归，覆盖 T1-T4

## 7. 风险与应对

| 风险 | 应对 |
|------|------|
| 超时设置过严导致大量失败 | 以压测 p99 为基线，预留 20% 余量 |
| 重试放大上游压力 | 指数退避 + 熔断，限制重试次数 |
| 缓存命中率低 | 先评估任务重复度，再决定缓存规模 |
| 优化引入复杂度 | 保持 ModelProvider 接口不变，优化为内部实现 |

## 8. P2 整合（后续）

- 接入 `main.py`：`router.route()` → `provider.invoke()` 完整链路
- 复用 `BoundaryChecker.check_model_boundary()` 校验路由结果
- 以 p99 为延迟预算接入真实模型，替换 mock 占位

## 9. 测试覆盖（当前基线）

| 测试文件 | 覆盖 | 用例数 |
|---------|------|:---:|
| `test_router.py` | 路由三种风险对抗 | 12 |
| `test_model_provider.py` | Local 固定延迟 + Remote 抖动 + T1 预算 | 13 |
| `test_workspace_context.py` | 工作区/上下文/工具边界 | 33 |
| **合计** | | **58** |

压测脚本：`stress_router_latency.py`（路由判定延迟）、`stress_model_latency.py`（真实模型延迟抖动扫描）。