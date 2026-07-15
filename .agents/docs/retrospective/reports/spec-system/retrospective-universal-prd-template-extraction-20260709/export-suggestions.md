# 改进建议与行动项

## 改进行动项（按优先级排序）

### 高优先级（立即执行）

| ID | 行动项 | 验收标准 | 责任人 | 预计完成时间 |
|---|---|---|---|---|
| ACT-001 | 在git-commit-helper/原子提交技能中补充Windows PowerShell环境兼容说明 | 在Gotchas章节添加PowerShell不支持bash HEREDOC语法的说明，给出正确的提交消息写法 | orchestrator | 2026-07-09 |
| ACT-002 | 更新spec-writing-guide，补充Open Questions闭环机制说明 | 明确Open Questions解决后的标记方式（勾选+补充解决说明/记录到Version History） | architect | 2026-07-10 |

### 中优先级（近期迭代）

| ID | 行动项 | 验收标准 | 责任人 | 预计完成时间 |
|---|---|---|---|---|
| ACT-003 | 升级check-spec-format.py脚本，增加对PRD Spec格式的检查支持 | 脚本能够识别PRD Spec格式，检查必填章节、frontmatter字段完整性、格式正确性，与现有Change Spec检查并行 | developer | 2026-07-15 |
| ACT-004 | 在spec-writing-guide中补充"Spec演进指南"章节 | 说明项目执行过程中如何更新Spec、如何维护Version History、如何追踪变更、已解决问题如何标记 | architect | 2026-07-15 |
| ACT-005 | 将本次萃取的4个方法论模式沉淀到docs/retrospective/patterns/methodology-patterns/对应目录 | 第一性原理模板提炼法、Dogfooding自验证法、规范双轨制、规范四要素模型分别创建独立模式文件，补充frontmatter和成熟度标记 | orchestrator | 2026-07-12 |

### 低优先级（后续规划）

| ID | 行动项 | 验收标准 | 责任人 | 预计完成时间 |
|---|---|---|---|---|
| ACT-006 | 提供PRD模板填写示例项目 | 用一个简单完整的示例项目（如"待办事项应用"）展示如何填写PRD模板，作为最佳实践参考 | 待定 | 后续版本 |
| ACT-007 | 评估是否需要"迷你PRD"简化版模板 | 针对<1天工作量、单文件的极小项目，评估是否需要提供更简化的模板版本 | 待定 | 收集3个以上场景后再决策 |
| ACT-008 | 评估元数据是否需要增加estimated_effort/priority字段 | 收集项目排期需求，评估是否需要在元数据中增加工作量估算和优先级字段 | 待定 | 后续版本 |

## 对其他项目的建议

1. **所有新项目立项必须使用本次提炼的通用PRD模板**，不要再使用非结构化的需求描述
2. **小范围增量变更继续使用Change Spec格式**，不要用PRD模板写小变更，避免过度规范
3. **所有规范类/模板类项目必须包含Dogfooding自验证环节**，作为强制验收标准
4. **规范交付必须包含四要素**（模板+指南+决策框架+最佳实践），不要只发一个空模板

## 遗留Open Questions处理

原Spec中提出的5个Open Questions处理结果：

| 问题 | 处理结果 |
|---|---|
| 模板是否应该包含"RACI责任矩阵"作为可选章节？ | 保留为可选内容，在prd-structure-guide.md中说明可根据项目需要添加 |
| 对于非常小的项目，是否需要"迷你PRD"简化版？ | 记录为ACT-007，待收集足够场景后再决策 |
| 元数据中是否需要增加estimated_effort/priority字段？ | 记录为ACT-008，待有明确排期需求时再评估 |
| 模板归档位置：模式目录还是规则目录？ | 采取"双归档"：模板本身放在patterns/methodology-patterns/spec-workflow/，在.agents/rules/spec-writing-guide/中建立引用链接 |
| 是否需要提供填写示例？ | 记录为ACT-006，后续版本提供 |

## 经验复用指南

其他项目复用本项目成果时：
1. 直接复制 [universal-prd-template.md](../../../../retrospective/patterns/methodology-patterns/spec-workflow/universal-prd-template.md) 作为新项目Spec的起点
2. 阅读 [format-selection-guide.md](../../../../retrospective/patterns/methodology-patterns/spec-workflow/format-selection-guide.md) 判断应该用PRD还是Change格式
3. 参考 [best-practices.md](../../../../retrospective/patterns/methodology-patterns/spec-workflow/best-practices.md) 中的自检清单检查Spec质量
4. 如果是做规范/模板类项目，严格遵循"第一性原理提炼→Dogfooding自验证→规范四要素交付"的流程
