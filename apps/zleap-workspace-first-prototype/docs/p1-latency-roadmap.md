# P1 阶段实施路线图：真实模型延迟量测

> 基于 `docs/multi-model-routing-plan.md` §4 路线图与 `docs/router-test-report.md` 结论，制定 P1 阶段实施路线图。
> 核心：接入真实模型并落地端到端延迟量测方案，量化路由判定的额外开销。
> 前置：P0 骨架已完成（`ModelRouter` + 四种策略，12 用例全通过）
> 日期：2026-08-03 | 状态：规划中

## 1. P1 目标与范围

**目标**：将 `ModelRouter` 从"策略骨架"升级为"可量测的真实路由"，验证路由判定在真实模型下的延迟成本，为"何时该路由、何时该直通"提供数据依据。

**范围**：
- 接入真实模型调用（mock→真实 LLM API 适配层）
- 建立分层延迟量测体系（路由判定 / 模型推理 / 端到端）
- 落地自动化压测脚本（`tests/stress_router_latency.py`）
- 输出延迟基线报告，作为 P2 整合的准入依据

**非目标**：不做模型间成本优化、不做分布式部署、不做生产级监控告警。

## 2. 前置条件（P0 已完成）

- [x] `router.py`：`ModelRouter` + `DataBoundaryStrategy`/`ComplexityStrategy`/`CostStrategy`/`FallbackStrategy`
- [x] `tests/test_router.py`：12 用例全通过，三种风险加固已验证
- [x] 边界复用：`BoundaryChecker.check_model_boundary()` 不修改

## 3. 真实模型接入方案

### 3.1 模型适配层（新增 `model_provider.py`）

| 抽象 | 说明 | 接口 |
|------|------|------|
| `ModelProvider` | 统一模型调用抽象，屏蔽供应商差异 | `invoke(model, prompt, **kw) -> str` |
| `LocalProvider` | 本地模型（mock，可注入固定延迟模拟） | `invoke` 返回固定文本 |
| `RemoteProvider` | 远程 LLM API（OpenAI/本地网关） | `invoke` 走 HTTP 调用 |

**设计要点**：
- 路由层只依赖 `ModelProvider` 抽象，不感知具体供应商
- 延迟量测通过 `ModelProvider` 的计时包装实现，不侵入路由逻辑
- 支持注入固定延迟（`latency_ms` 参数）用于压测脚本可控复现

### 3.2 接入点（`main.py` 演示扩展）

```python
provider = RemoteProvider(base_url="https://api.example.com", api_key="...")
router = build_default_router(registry, boundary, provider=provider)
model = router.route("finance", "处理一份客户财务票据", complexity=0.9)
result = provider.invoke(model, task)
```

## 4. 真实模型延迟量测方案（核心）

### 4.1 三层延迟维度

| 维度 | 定义 | 量测点 | 意义 |
|------|------|--------|------|
| **路由判定延迟** | `route()` 内部决策耗时 | 计时 `route()` 方法（不含模型调用） | 量化路由本身开销 |
| **模型推理延迟** | 模型生成响应耗时 | 计时 `provider.invoke()` | 量化模型能力差异 |
| **端到端延迟** | 路由→调用的完整耗时 | 计时 `route()` + `invoke()` | 量化整体链路 |

**核心指标**：路由判定延迟通常 <1ms（纯内存决策），真实模型推理延迟为 100ms~数秒。**目的是量化路由判定在总延迟中的占比，判断路由是否值得**。

### 4.2 量测方法

- **冷热启动**：首次调用（冷）与预热后（热）分别量测，区分初始化开销
- **多轮采样**：每维度采样 ≥1000 次，消除单次抖动
- **计时精度**：`time.perf_counter()`（纳秒级），避免 `time.time()` 精度不足
- **并发控制**：压测脚本支持 `--concurrency` 参数，验证并发下的延迟分布

### 4.3 指标定义

| 指标 | 定义 | 验收基线（建议） |
|------|------|-----------------|
| 平均延迟（mean） | 样本均值 | 路由判定 <1ms |
| p50 / p95 / p99 | 分位延迟 | 路由判定 p99 <5ms |
| 吞吐量（QPS） | 每秒请求数 | 路由判定 >1000 QPS |
| 超时率 | 超过阈值的样本占比 | <1% |
| 直通 vs 正常 | 直通模式相对正常模式的延迟节省 | 正常模式路由判定开销可忽略 |

### 4.4 输出报告

压测脚本输出 `docs/latency-baseline-report.md`，包含：
- 各维度延迟分布（均值/分位/标准差）
- 直通 vs 正常模式对比
- 冷热启动对比
- 结论：路由判定是否为瓶颈、是否值得路由

## 5. 任务分解与验收标准

| 任务 | 内容 | 验收标准 |
|------|------|---------|
| T1 模型适配层 | 新增 `model_provider.py`（抽象+本地/远程实现） | 可注入延迟、可替换供应商 |
| T2 路由接入 | `router.py` 支持注入 `ModelProvider` | 路由结果可传给 provider 调用 |
| T3 压测脚本 | 新增 `tests/stress_router_latency.py` | 输出分层延迟统计与直通对比 |
| T4 延迟基线 | 运行压测生成 `docs/latency-baseline-report.md` | 三类延迟指标齐全，结论清晰 |
| T5 边界回归 | 现有 12 用例 + 新增压测用例全通过 | 无回归，边界不越权 |

## 6. 风险与应对

| 风险 | 应对 |
|------|------|
| 真实 API 有成本/限流 | 压测默认用本地 mock（可注入延迟），真实 API 仅小样本验证 |
| 网络抖动干扰量测 | 多次采样取分位数，报告标注网络环境 |
| 路由判定延迟过小难以量测 | 用 `perf_counter` + 循环批量计时取平均，避免单次计时误差 |
| 接入真实模型增加复杂度 | 通过 `ModelProvider` 抽象隔离，路由层不感知供应商 |

## 7. 与 P0 的衔接

- P0 已交付：路由策略骨架 + 边界对抗测试（`docs/router-test-report.md`）
- P1 将：新增模型适配层 + 延迟量测体系 + 压测脚本
- P2 再：接入 `main.py` 完整流程 + 边界校验联调