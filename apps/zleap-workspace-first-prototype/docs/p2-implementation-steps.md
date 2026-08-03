# P2 性能优化方案：详细实施步骤

> 基于并发50压测结论与 `p2-performance-optimization.md` 方案，细化 T1-T5 的实施步骤。
> 前置：T1 延迟预算已实现（`model_provider.py`，58 用例通过）
> 日期：2026-08-03 | 状态：T1 已完成，T2-T5 待实施

## 0. 压测结论回顾（实施依据）

- **p99 显著偏离 p50**：抖动 200ms 时 p99(395ms) 比 p50(200ms) 高 ~195ms，均值无法反映尾部延迟
- **并发 50 不放大延迟**：线程开销 <1ms，非瓶颈
- **抖动主导延迟宽度**：stdev 随抖动线性增长（0.3→115ms）

**实施原则**：以 p99 为延迟预算依据，接口（ModelProvider.invoke）保持稳定，所有优化为内部实现。

## 1. T1 延迟预算（已完成）

**目标**：ModelProvider 增加 p99 预算属性 + 路由参考。

### 已实现代码（model_provider.py）

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

### 验证（test_model_provider.py TestLatencyBudget）

- 延迟 10ms、预算 20ms → 在预算内 ✅
- 延迟 100ms、预算 50ms → 超预算 ✅
- 未设预算 → 通过 ✅
- p99 计算逼近最大样本 ✅
- 样本记录正确 ✅

### 接入路由（下一步）

```python
# 路由层降级决策参考预算
if not provider.is_within_budget():
    model = fallback_strategy.route(...)  # 降级到便宜模型
```

## 2. T2 超时与重试

**目标**：`RemoteProvider` 落地强制超时 + 指数退避重试。

### 实施步骤

1. **强制超时**：在 `RemoteProvider._call` 中落地 `timeout` 硬超时（当前为参数占位）
2. **指数退避重试**：新增 `retry` + `backoff` 参数，仅对幂等请求重试
3. **超时计入统计**：超时样本按最大延迟计入，暴露真实尾部

### 验收
- 超时请求不卡死，正常返回
- 重试次数 ≤ 3，退避收敛
- 超时率可观测

## 3. T3 连接池与并发

**目标**：复用连接，控制并发上限。

### 实施步骤

1. **连接池**：集成 `httpx.Client` 或 `requests.Session`，全局复用
2. **并发上限**：`RemoteProvider` 增加 `max_concurrency`，用信号量控制
3. **批量路由**：路由层批量提交，减少框架层调用

### 验收
- 并发 50 下连接数受限、吞吐稳定
- 无 TLS 握手重复开销

## 4. T4 缓存与降级

**目标**：结果缓存 + 降级链 + 熔断。

### 实施步骤

1. **结果缓存**：按 `(prompt哈希, model)` 缓存，命中则跳过模型调用
2. **降级链**：强模型超时 → 降级便宜模型 → 兜底默认结果
3. **熔断**：连续超时计数达到阈值，暂缓调用该模型一段时间

### 验收
- 重复任务命中缓存，不重复调用模型
- 降级链可达，熔断后自动恢复

## 5. T5 压测回归

**目标**：扩展 `stress_model_latency.py` 覆盖上述路径。

### 实施步骤

1. **超时场景**：压测中注入超时（如 latency > timeout），验证不卡死
2. **缓存命中**：压测重复任务，验证缓存命中率与延迟改善
3. **降级触发**：构造超预算模型，验证降级链生效
4. **p99 达标**：以 p99 预算为验收，验证各抖动下 p99 达标

### 验收
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