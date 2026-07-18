---
id: "sg-guide-06"
title: "06 Python API参考与排错指南"
source: "rules/stage-guardrails-guide.md#06"
x-toml-ref: "../../../.meta/toml/.agents/rules/stage-guardrails-guide/06-api-troubleshooting.toml"
---

# 06 Python API参考与排错指南


### GuardrailRuntime 核心方法

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `guard_operation(op, role, detail)` | 操作前拦截检查（核心入口） | FormattedOutput |
| `enter_stage(stage, role, msg)` | 进入阶段 | FormattedOutput |
| `exit_stage(stage, role, msg, ...)` | 退出阶段 | FormattedOutput |
| `advance_to_next_stage(role, ...)` | 顺序推进到下一阶段 | FormattedOutput |
| `mark_doc_check(docs)` | 标记必读文档检查完成 | FormattedOutput |
| `mark_pdr_done()` | 标记PDR流程完成 | FormattedOutput |
| `request_jump(type, to, by, reason)` | 提交跳转申请 | (JumpRecord, FormattedOutput) |
| `approve_jump(id, by, ...)` | 批准跳转（rollback自动进入目标） | FormattedOutput |
| `reject_jump(id, by, reason)` | 拒绝跳转 | FormattedOutput |
| `execute_skip(id, role, msg)` | 执行已批准的正向跳过 | FormattedOutput |
| `can_transition_to(target)` | 查询是否可转换到目标阶段 | (bool, str) |
| `get_status()` | 获取运行时状态快照 | RuntimeStatus |
| `get_logs_since(event, level)` | 按类型/级别过滤日志 | list[str] |
| `dump_logs()` | 导出所有日志为字符串 | str |
| `reset()` | 重置运行时状态 | None |

### FormattedOutput 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `is_intercept` | bool | 是否被拦截（True=操作应被阻止） |
| `user_message` | str | 人类可读的拦截/错误消息（放行时为空） |
| `sg_log_line` | str | SG-LOG结构化日志行 |
| `log_level` | str | DEBUG/INFO/WARN/ERROR |
| `event_type` | str | 事件类型名称 |

### OperationType 常用操作

| 操作值 | 说明 | 典型阶段 |
|--------|------|---------|
| `clarify_requirement` | 澄清需求 | S1 |
| `create_task_list` | 创建任务清单 | S1/S2 |
| `identify_risk` | 识别风险 | S1 |
| `architecture_design` | 架构设计 | S2 |
| `choose_tech_stack` | 技术选型 | S2 |
| `define_api` | 定义API | S2 |
| `assign_task` | 分配任务 | S3 |
| `set_acceptance_criteria` | 设定验收标准 | S3 |
| `write_code` | 编写代码 | S4 |
| `write_unit_test` | 编写单元测试 | S4 |
| `run_test` | 运行测试 | S4/S5 |
| `modify_architecture` | 修改架构决策 | S2（需回退） |
| `submit_pr` | 提交PR | S4 |
| `review_code` | 审查代码 | S6 |
| `approve_code` | 批准代码 | S6 |
| `merge_code` | 合并代码 | S7 |
| `search_code` | 搜索代码 | 所有阶段 |
| `read_docs` | 读取文档 | 所有阶段 |

完整操作列表见 `boundary.py` 中的 `OperationType` 枚举（共60种操作类型）。

### 问题：CLI中文显示乱码

**原因**：Windows PowerShell默认编码非UTF-8

**解决方案**：设置环境变量 `$env:PYTHONIOENCODING='utf-8'`，或使用Windows Terminal替代旧版PowerShell

### 问题：guard_operation总是返回is_intercept=True

**排查步骤**：
1. 检查 `current_stage` 是否正确（是否已enter_stage）
2. 检查 `current_role` 是否匹配当前阶段的负责角色
3. 检查操作类型是否在当前阶段的允许列表中
4. 查看 `user_message` 获取具体拦截原因

### 问题：approve_jump后current_stage没有变化

**原因**：skip类型的跳转批准后需要手动调用 `execute_skip()` 才会进入目标阶段；只有rollback类型批准后会自动进入。

### 问题：导出的日志被离线工具检测出NO_PDR_FOR_STAGE

**原因**：进入阶段后没有调用 `mark_doc_check()` 和 `mark_pdr_done()`。每个阶段进入后都应该先做PDR检查。

- [阶段守卫规则定义](../stage-guardrails.md)
- [功能开发工作流](../../workflows/feature-development.md)
- [前置文档读取协议（PDR）](../../protocols/pre-document-reading.md)
- [阶段守卫离线分析工具check-stage-guardrails.py](../../scripts/check-stage-guardrails.py)
- [运行时模块源码](../../scripts/lib/stage_guardrails/README.md)

---

## 相关模式

- [三层检查工具模式](../../docs/retrospective/patterns/code-patterns/three-tier-check-tool.md)
- [双通道分级日志](../../docs/retrospective/patterns/code-patterns/dual-channel-tiered-logging.md)
---

← 上一章: [05 阶段跳转流程与CLI工具](05-jump-flows-tools.md) | **[返回索引](../stage-guardrails-guide.md)**
