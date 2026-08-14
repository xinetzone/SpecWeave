# ModelRouter 路由边界对抗测试报告

> 针对多模型路由规划中的三种风险（策略冲突 / 路由延迟 / 阈值主观）的自动化对抗测试结果。
> 参考：`docs/multi-model-routing-plan.md` §3 对抗审查 | 测试文件：`tests/test_router.py`
> 日期：2026-08-03 | 状态：✅ 全部通过（12/12）

## 1. 测试目标

验证 `ModelRouter`（P0 骨架）在三种对抗场景下的健壮性，对应规划 §3 的加固措施：

| 风险 | 对抗攻击 | 加固设计 | 本文验证 |
|------|---------|---------|---------|
| 策略冲突 | 多策略同时命中时优先级是否正确 | 数据边界策略为硬约束（优先级100）恒优先 | 3 项 |
| 路由延迟 | 路由判定是额外开销，简单任务不值得 | 直通模式（direct_mode）跳过路由判定 | 3 项 |
| 阈值主观 | 复杂度阈值主观设定，无法精确衡量 | 用可观测信号（复杂度参数）作代理 + 白名单校验 | 4 项 |

## 2. 测试环境

- 运行方式：`python -m unittest tests.test_router -v`
- 框架：Python 内置 `unittest`
- 用例总数：12，全部通过，耗时 0.001s
- 测试夹具（`build_fixture`）：finance 私有工作区（model=local-model），白名单 `[local-model, strong-model, cheap-model]`

## 3. 测试结果

### 3.1 风险1：策略冲突（`TestStrategyConflict`，5 用例 ✅）

| 用例 | 场景 | 期望 | 结果 |
|------|------|------|:---:|
| `test_sensitive_task_wins_over_complexity` | 敏感+高复杂度 | local-model（数据边界优先） | ✅ |
| `test_sensitive_task_wins_over_cost` | 敏感+简单查询 | local-model（数据边界优先） | ✅ |
| `test_strategy_priority_ordering` | 策略按优先级降序存储 | 降序且首>尾 | ✅ |
| `test_high_complexity_nonsensitive_uses_strong` | 非敏感+高复杂度 | strong-model | ✅ |
| `test_simple_query_nonsensitive_uses_cheap` | 非敏感+简单查询 | cheap-model | ✅ |

**结论**：数据边界策略（优先级100）在敏感任务中恒优先于复杂度（50）与成本（30）策略，优先级排序无冲突。

### 3.2 风险2：路由延迟（`TestDirectMode`，3 用例 ✅）

| 用例 | 场景 | 期望 | 结果 |
|------|------|------|:---:|
| `test_direct_mode_uses_default_model` | 直通+满足所有策略 | 默认模型 local-model | ✅ |
| `test_direct_mode_skips_strategy_evaluation` | 直通普通任务 | 轨迹 strategy=direct | ✅ |
| `test_normal_mode_evaluates_strategies` | 非直通复杂任务 | strong-model + 策略轨迹 | ✅ |

**结论**：直通模式跳过全部策略评估，直接使用工作区默认模型，有效规避路由延迟；仅在非直通模式才评估策略。

### 3.3 风险3：阈值主观 + 边界越权（`TestBoundaryAndThreshold`，4 用例 ✅）

| 用例 | 场景 | 期望 | 结果 |
|------|------|------|:---:|
| `test_routing_outside_whitelist_raises` | 路由结果不在白名单 | 抛 `BoundaryViolation` | ✅ |
| `test_route_within_whitelist_ok` | 路由结果在白名单 | 正常返回 | ✅ |
| `test_complexity_threshold_boundary` | 阈值 0.7 边界 | 0.7 不触发 / 0.71 触发 | ✅ |
| `test_route_trace_recorded` | 路由轨迹记录 | 记录 workspace_id 与 model | ✅ |

**结论**：复杂度阈值边界精确（0.7 不触发、0.71 触发）；路由结果经模型白名单校验，越权强制拦截（`BoundaryViolation`），杜绝"路由到越权模型"。

## 4. 关键边界情况

1. **阈值边界**：`ComplexityStrategy(threshold=0.7)` 时，`complexity=0.7` 不触发（兜底默认），`0.71` 触发（强模型）——严格大于阈值才触发。
2. **白名单越权**：finance 白名单仅 `[local-model]` 时，路由到 strong-model 立即抛 `BoundaryViolation`。
3. **直通 vs 评估**：直通模式轨迹标记 `strategy=direct`，与正常模式的策略名（如 `ComplexityStrategy`）可区分，便于审计路由延迟是否被绕过。

## 5. 结论

三种风险对应的对抗加固措施均通过自动化测试验证，`ModelRouter` P0 骨架在策略优先级、直通降延迟、阈值与白名单边界上行为正确。建议后续 P1 阶段在接入真实模型后再补充端到端延迟量测。

## 6. 测试命令

```bash
cd apps/samples/zleap-workspace-first-prototype
python -m unittest tests.test_router -v
```