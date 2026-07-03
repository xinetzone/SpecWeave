---
id: "feat-dev-06"
title: "06 结构化日志与交接协议"
source: "workflows/feature-development.md#06"
x-toml-ref: "../../../.meta/toml/.agents/workflows/feature-development/06-logging-handoff.toml"
---

# 06 结构化日志与交接协议


所有智能体在执行开发流程各阶段时，必须输出结构化日志（`[SG-LOG]`和`[PDR-LOG]`），以便CI流水线通过 `check-stage-guardrails.py --strict` 自动检测流程合规性。

### 日志输出时机

| 时机 | 日志前缀 | 必须输出的事件 |
|------|---------|--------------|
| 进入新阶段时 | `[SG-LOG]` | `STAGE_ENTER` |
| 前置文档读取时 | `[PDR-LOG]` | `PDR_START` → `PDR_DOC_READ`/`PDR_DOC_MISSING` → `PDR_CONFIRM` |
| 操作边界校验时 | `[SG-LOG]` | `BOUNDARY_PASS`（DEBUG级别，常规操作可省略）/ `INTERCEPT`（WARN级别，拦截时必须输出） |
| 阶段跳转时 | `[SG-LOG]` | `JUMP_REQUEST` → `JUMP_APPROVED`/`JUMP_REJECTED` |
| 退出阶段时 | `[SG-LOG]` | `STAGE_EXIT` |
| 发生错误时 | `[SG-LOG]` | `ERROR`（必须包含 `recovery_hint` 字段） |

### 日志格式

```
[SG-LOG] | level=<LEVEL> | event=<EVENT> | stage=<STAGE_ID> | role=<ROLE> | session=<SESSION_ID> | msg=<MESSAGE> | ctx=<CONTEXT_JSON>
[PDR-LOG] | level=<LEVEL> | event=<EVENT> | stage=<STAGE_ID> | role=<ROLE> | session=<SESSION_ID> | msg=<MESSAGE> | ctx=<CONTEXT_JSON>
```

### 最小合规示例（STAGE_ENTER → PDR → STAGE_EXIT）

```
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S4 | role=developer | session=task-001 | msg=进入代码实现阶段 | ctx={"entry_condition":"任务分配已完成","prev_stage":"S3"}
[PDR-LOG] | level=INFO | event=PDR_START | stage=S4 | role=developer | session=task-001 | msg=开始前置文档读取 | ctx={"required_count":2}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S4 | role=developer | session=task-001 | msg=已读取: docs/development-standards.md | ctx={"doc":"docs/development-standards.md","bytes":8420,"key_points":["Conventional Commits","测试覆盖率>=80%"]}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S4 | role=developer | session=task-001 | msg=已读取: spec.md | ctx={"doc":"spec.md","bytes":3200,"key_points":["接口定义","验收标准"]}
[PDR-LOG] | level=INFO | event=PDR_CONFIRM | stage=S4 | role=developer | session=task-001 | msg=前置文档确认完成: 2份已读取,0份缺失 | ctx={"read_count":2,"missing_count":0,"missing_with_risk":0,"ready_to_proceed":true}
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S4 | role=developer | session=task-001 | msg=代码实现阶段已完成 | ctx={"exit_criteria_met":["编码完成","单元测试通过"],"duration":"30min","output_artifacts":["auth.py","test_auth.py"],"next_stage":"S5"}
```

### 关键合规要求

1. **每个STAGE_ENTER必须有对应的PDR流程**：进入新阶段后必须输出PDR_START并完成文档读取确认，否则触发`NO_PDR_FOR_STAGE`警告
2. **DOC_MISSING必须标注风险**：前置文档缺失时，ctx必须包含`risk`和`action`字段，否则触发`MISSING_RISK_ANNOTATION`警告
3. **ERROR必须包含recovery_hint**：错误日志ctx中必须包含`recovery_hint`恢复建议，否则触发`ERROR_NO_RECOVERY`警告
4. **禁止未审批跳转**：跨阶段跳转必须有JUMP_REQUEST和JUMP_APPROVED记录，否则触发ERROR
5. **CI严格模式**：CI流水线使用`--strict`模式运行检查，WARN级别异常也会导致CI失败

### 日志检查命令

```bash
# 手动检查日志文件
python .agents/scripts/check-stage-guardrails.py --log-file <session.log> --strict

# CI自动检查（扫描.agents/logs/目录最新日志）
python .agents/scripts/check-stage-guardrails.py --log-file .agents/logs/<task-id>.log --strict

# 使用内置demo演示分析效果
python .agents/scripts/check-stage-guardrails.py --demo --strict
```

> 详细日志格式规范、事件类型枚举、各事件模板见 [.agents/rules/stage-guardrails/05-logging-spec.md 结构化日志格式](../../rules/stage-guardrails/05-logging-spec.md#结构化日志格式) 章节。PDR日志格式见 [.agents/protocols/pre-document-reading/05-examples-logging.md 日志输出规范](../../protocols/pre-document-reading/05-examples-logging.md#日志输出规范) 章节。

## 交接协议

各步骤之间的任务交接须遵循 `.agents/protocols/handoff.md` 中定义的交接协议，确保上下文完整传递。交接时应使用 `templates/handoff-template.md` 模板填写交接信息，包括已完成工作、待办事项与风险提示。

---

## 相关模式

- [学习-验证-采用](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/learn-validate-adopt.md)
- [两阶段处理](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/two-phase-processing.md)
---

← 上一章: [05 治理规则引用](05-governance-references.md) | **[返回索引](../feature-development.md)**
