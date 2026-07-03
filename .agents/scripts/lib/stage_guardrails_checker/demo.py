DEMO_LOGS = """[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S1 | role=orchestrator | session=demo-001 | msg=进入需求接收阶段，开始明确需求边界与验收标准 | ctx={"entry_condition":"收到用户需求描述","prev_stage":null}
[PDR-LOG] | level=INFO | event=PDR_START | stage=S1 | role=orchestrator | session=demo-001 | msg=开始前置文档读取,共3份文档待读取 | ctx={"required_count":3,"required_docs":["用户需求原始描述","项目README.md","相关历史spec"],"resume":false}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S1 | role=orchestrator | session=demo-001 | msg=已读取: 用户需求原始描述 | ctx={"doc":"用户输入","bytes":520,"key_points":["需要用户认证功能","支持JWT"]}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S1 | role=orchestrator | session=demo-001 | msg=已读取: README.md | ctx={"doc":"README.md","bytes":3200,"key_points":["项目技术栈:FastAPI+PostgreSQL"]}
[PDR-LOG] | level=WARN | event=PDR_DOC_MISSING | stage=S1 | role=orchestrator | session=demo-001 | msg=前置文档缺失: 相关历史spec | ctx={"doc":".trae/specs/auth/*","risk":"low","risk_detail":"无相关历史spec,不影响当前工作","action":"annotate"}
[PDR-LOG] | level=INFO | event=PDR_CONFIRM | stage=S1 | role=orchestrator | session=demo-001 | msg=前置文档确认完成: 2份已读取,1份缺失已标注风险 | ctx={"read_count":2,"missing_count":1,"missing_with_risk":1,"ready_to_proceed":true}
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S1 | role=orchestrator | session=demo-001 | msg=阶段需求接收已完成,退出标准满足 | ctx={"exit_criteria_met":["需求已澄清","验收标准已明确"],"duration":"5min","output_artifacts":["任务分解清单"],"next_stage":"S2"}
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S2 | role=architect | session=demo-001 | msg=进入方案设计阶段，开始产出可执行的技术方案 | ctx={"entry_condition":"收到任务分解清单","prev_stage":"S1"}
[PDR-LOG] | level=INFO | event=PDR_START | stage=S2 | role=architect | session=demo-001 | msg=开始前置文档读取,共4份文档待读取 | ctx={"required_count":4,"required_docs":["任务分解清单","技术栈文档","架构文档","开发规范"],"resume":false}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S2 | role=architect | session=demo-001 | msg=已读取: 任务分解清单 | ctx={"doc":"task-list.md","bytes":1200,"key_points":["用户认证模块","JWT+Refresh Token"]}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S2 | role=architect | session=demo-001 | msg=已读取: docs/development-standards.md | ctx={"doc":"docs/development-standards.md","bytes":8420,"key_points":["Conventional Commits","测试覆盖率>=80%"]}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S2 | role=architect | session=demo-001 | msg=已读取: 架构文档 | ctx={"doc":".agents/modules/","bytes":5800,"key_points":["分层架构模式"]}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S2 | role=architect | session=demo-001 | msg=已读取: 技术栈文档 | ctx={"doc":"docs/knowledge/","bytes":2100,"key_points":["FastAPI","SQLAlchemy","PyJWT"]}
[PDR-LOG] | level=INFO | event=PDR_CONFIRM | stage=S2 | role=architect | session=demo-001 | msg=前置文档确认完成: 4份已读取,0份缺失 | ctx={"read_count":4,"missing_count":0,"missing_with_risk":0,"ready_to_proceed":true}
[SG-LOG] | level=DEBUG | event=BOUNDARY_CHECK | stage=S2 | role=architect | session=demo-001 | msg=校验操作合法性: 设计用户认证模块分层架构 | ctx={"operation":"架构设计","allowed_ops":["技术可行性分析","架构设计","技术选型","接口定义","风险评估"]}
[SG-LOG] | level=DEBUG | event=BOUNDARY_PASS | stage=S2 | role=architect | session=demo-001 | msg=操作通过边界检查: 设计用户认证模块分层架构 | ctx={"operation":"架构设计"}
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S2 | role=architect | session=demo-001 | msg=阶段方案设计已完成,退出标准满足 | ctx={"exit_criteria_met":["技术方案已完成","风险评估已覆盖","接口定义已明确"],"duration":"15min","output_artifacts":["技术方案文档","接口定义文档"],"next_stage":"S3"}
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S3 | role=orchestrator | session=demo-001 | msg=进入任务分配阶段，开始匹配角色明确交付要求 | ctx={"entry_condition":"技术方案已确认","prev_stage":"S2"}
[SG-LOG] | level=INFO | event=JUMP_REQUEST | stage=S3 | role=developer | session=demo-001 | msg=申请阶段跳转: 从S3任务分配正向跳至S4代码实现 | ctx={"jump_type":"skip","from_stage":"S3","to_stage":"S4","reason":"方案明确,任务单一,无需独立分配阶段","requested_by":"developer"}
[SG-LOG] | level=INFO | event=JUMP_APPROVED | stage=S3 | role=orchestrator | session=demo-001 | msg=阶段跳转已批准: S3→S4跳过任务分配 | ctx={"jump_type":"skip","approved_by":"orchestrator","conditions":"developer直接按方案执行"}
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S4 | role=developer | session=demo-001 | msg=进入代码实现阶段，开始按方案完成编码与单元测试 | ctx={"entry_condition":"收到任务分配+技术方案","prev_stage":"S3"}
[SG-LOG] | level=WARN | event=INTERCEPT | stage=S1 | role=developer | session=demo-002 | msg=阶段守卫拦截: 编写Redis配置代码属于S4代码实现阶段职责 | ctx={"current_stage":"S1","violating_operation":"编写Redis配置代码","target_stage":"S4","exit_criteria":"明确功能边界与验收标准"}
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S4 | role=developer | session=demo-001 | msg=阶段代码实现已完成,退出标准满足 | ctx={"exit_criteria_met":["核心功能编码完成","单元测试通过"],"duration":"45min","output_artifacts":["auth.py","test_auth.py"],"next_stage":"S5"}
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S5 | role=tester | session=demo-003 | msg=进入测试编写阶段，开始编写测试用例 | ctx={"entry_condition":"收到代码实现产物","prev_stage":"S4"}
[PDR-LOG] | level=INFO | event=PDR_START | stage=S5 | role=tester | session=demo-003 | msg=开始前置文档读取,共2份文档待读取 | ctx={"required_count":2,"required_docs":["技术方案文档","代码实现产物"],"resume":false}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S5 | role=tester | session=demo-003 | msg=已读取: 技术方案文档 | ctx={"doc":"technical-design.md","bytes":5600,"key_points":["JWT认证流程","接口契约"]}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S5 | role=tester | session=demo-003 | msg=已读取: 代码实现产物 | ctx={"doc":"auth.py","bytes":3200,"key_points":["login/logout接口","token刷新逻辑"]}
[PDR-LOG] | level=INFO | event=PDR_CONFIRM | stage=S5 | role=tester | session=demo-003 | msg=前置文档确认完成: 2份已读取,0份缺失 | ctx={"read_count":2,"missing_count":0,"missing_with_risk":0,"ready_to_proceed":true}
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S5 | role=tester | session=demo-003 | msg=阶段测试编写已完成,退出标准满足 | ctx={"exit_criteria_met":["测试用例编写完成","测试报告已生成"],"duration":"20min","output_artifacts":["test_auth.py","test_report.md"],"next_stage":"S6"}
[SG-LOG] | level=ERROR | event=ERROR | stage=S4 | role=developer | session=demo-004 | msg=检测到未经审批的阶段跳转 | ctx={"error_type":"UNAUTHORIZED_JUMP","error_detail":"S4→S6跳转无orchestrator批准记录","impact":"代码未经测试可能引入缺陷"}
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S1 | role=developer | session=demo-005 | msg=进入需求接收阶段(演示文档缺失未标风险+格式异常) | ctx={"entry_condition":"收到需求","prev_stage":null}
[PDR-LOG] | level=INFO | event=PDR_START | stage=S1 | role=developer | session=demo-005 | msg=开始前置文档读取 | ctx={"required_count":2}
[PDR-LOG] | level=WARN | event=PDR_DOC_MISSING | stage=S1 | role=developer | session=demo-005 | msg=前置文档缺失: 架构约束文档 | ctx={"doc":"docs/architecture.md"}
[SG-LOG] 格式错误的日志行-缺少竖线分隔符无法被正常解析
"""