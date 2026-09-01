---
id: "sg-guide-04"
title: "04 常见拦截原因与解决方案"
source: "rules/stage-guardrails-guide.md#04"
x-toml-ref: "../../../.meta/toml/.agents/rules/stage-guardrails-guide/04-common-interceptions.toml"
---

# 04 常见拦截原因与解决方案


### 1. 当前阶段未允许该操作

**现象**：S1阶段尝试WRITE_CODE，被拦截提示"编写代码属于S4代码实现阶段职责"

**原因**：操作类型与当前阶段职责不匹配

**解决方案**：
- 按照正常流程：完成当前阶段的退出标准 → exit_stage → enter_stage进入目标阶段
- 如需跳过中间阶段：调用 `request_jump('skip', target_stage, role, reason)` → orchestrator批准 → `execute_skip()`
- 如需回退到之前阶段：调用 `request_jump('rollback', target_stage, role, reason)` → orchestrator批准（批准后自动进入目标阶段）

### 2. 角色与阶段不匹配

**现象**：tester在S1阶段尝试CLARIFY_REQUIREMENT被拦截

**原因**：当前阶段的负责角色不包含执行角色（S1仅orchestrator可执行需求操作）

**解决方案**：
- 确认当前应由哪个角色执行操作（参考阶段权限速查表）
- 通过handoff协议将任务交接给正确角色

### 3. 未进入任何阶段就执行操作

**现象**：调用guard_operation时current_stage为None，提示"未进入任何开发阶段"

**原因**：忘记先调用 `enter_stage('S1', 'orchestrator', ...)`

**解决方案**：每个任务开始时必须先从S1进入，不能跳过S1直接操作

### 4. 重复进入阶段（DUPLICATE_ENTRY）

**现象**：已经进入S1后再次调用enter_stage('S1', ...)

**原因**：状态机已在活跃阶段，不能重复进入

**解决方案**：如需重新开始，先调用 `reset()` 重置运行时；如需推进，先exit_stage再enter_stage

### 5. 退出阶段不匹配（STAGE_MISMATCH）

**现象**：当前在S2但调用exit_stage('S1', ...)

**原因**：退出的阶段ID与当前活跃阶段不一致

**解决方案**：使用 `current_stage` 属性确认当前活跃阶段后再退出

### 6. 未经审批执行跳转（UNAUTHORIZED_JUMP）

**现象**：未approve就调用execute_skip

**原因**：跳过/回退必须经orchestrator审批

**解决方案**：严格执行 request_jump → approve_jump → execute_skip 的流程

### 7. 疑似绕过拦截（BYPASS_DETECTED）

**现象**：WRITE_CODE被拦截后，改用MODIFY_BUSINESS_CODE执行同类操作，触发绕过检测

**原因**：BypassDetector跟踪被拦截的操作，检测等价操作替代执行

**解决方案**：这是ERROR级别事件，必须立即停止并走正规审批流程。绕过检测会记录到SG-LOG，离线分析工具会检测到并标记为严重违规。

---

## 相关模式

- [三层检查工具模式](../../../docs/retrospective/patterns/code-patterns/three-tier-check-tool.md)
- [双通道分级日志](../../../docs/retrospective/patterns/code-patterns/dual-channel-tiered-logging.md)
---

← 上一章: [03 日志示例与格式规范](03-logging-examples.md) | **[返回索引](../stage-guardrails-guide.md)** | 下一章: [05 阶段跳转流程与CLI工具](05-jump-flows-tools.md) →
