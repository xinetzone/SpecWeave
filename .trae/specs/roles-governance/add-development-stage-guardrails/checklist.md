# 开发流程阶段守卫与功能演进治理规则检查点清单

## 目录与文件结构检查

- [x] `.agents/rules/stage-guardrails.md` 已创建
- [x] `.agents/protocols/pre-document-reading.md` 已创建
- [x] `.agents/workflows/feature-development.md` 已更新
- [x] `.agents/roles/developer.md` 已更新
- [x] `.agents/roles/architect.md` 已更新
- [x] `.agents/roles/tester.md` 已更新
- [x] `.agents/roles/reviewer.md` 已更新
- [x] `.agents/roles/orchestrator.md` 已更新（补充阶段守卫Non-Goals）
- [x] `AGENTS.md` 已更新
- [x] `.agents/rules/README.md` 已更新
- [x] `.agents/protocols/README.md` 已更新

## 阶段守卫规则文档检查

- [x] 文档包含标准8阶段序列定义（需求接收→方案设计→任务分配→代码实现→测试编写→代码审查→合并代码→完成确认）
- [x] 每个阶段有明确的负责角色
- [x] 每个阶段有明确的进入条件和退出标准
- [x] 每个阶段的操作边界清晰（允许操作列表+禁止操作列表）
- [x] 每个阶段边界包含至少1个正例和1个反例
- [x] 跨阶段拦截规则定义了标准输出格式（⚠️阶段守卫拦截格式）
- [x] 拦截后行为规范明确（不得执行越界操作、等待当前阶段完成或审批跳转）
- [x] 阶段跳转审批流程包含Mermaid流程图
- [x] 明确了跳过阶段的审批权限（orchestrator批准）
- [x] 明确了逆向回退的额外要求（reviewer确认回退范围）
- [x] 文档使用中文编写

## 前置文档强制读取协议检查

- [x] 文档包含各角色×各阶段的前置文档清单表格
- [x] 表格中8个阶段×对应角色的前置文档均有具体路径指向
- [x] 读取确认机制定义了标准输出格式（📋前置文档确认格式）
- [x] 文档缺失处理规则明确（请求获取/标注缺失+说明风险）
- [x] 新会话强制重载规则已定义
- [x] 包含至少一个完整的端到端使用示例
- [x] 文档使用中文编写

## 功能开发工作流增强检查

- [x] Mermaid流程图已更新，包含变更类型判定分支节点
- [x] 三类变更路径用视觉样式区分（新功能/功能扩展/功能重构）
- [x] "角色参与"表格已更新，包含功能扩展和功能重构路径
- [x] 现有8个步骤均增加了"阶段守卫检查"段落
- [x] 现有8个步骤均增加了"前置文档确认"段落
- [x] "功能扩展轻量流程"章节存在（6步骤：影响分析→增量方案→增量实现→回归测试→增量审查→合并）
- [x] 功能扩展流程明确说明跳过"任务分配"阶段（E3注意项）
- [x] 功能扩展流程要求architect明确回归测试范围（E2执行要点3）
- [x] "功能重构重量流程"章节存在（7步骤：全量影响评估→方案重审→全量重规划→实现→全量回归→双重审查→合并）
- [x] 功能重构流程要求包含回滚策略（R2执行要点3、R4执行要点4）
- [x] 功能重构涉及数据迁移时要求包含迁移脚本和验证步骤（R1要点3+R3要点3+R4要点3）
- [x] "变更类型判定指南"小节存在
- [x] 变更类型判定包含Mermaid决策树
- [x] 三类变更（新功能/功能扩展/功能重构）的判定标准清晰可操作

## 角色Non-Goals更新检查

- [x] developer.md Non-Goals包含"不在代码实现阶段擅自变更架构决策"
- [x] developer.md Non-Goals包含"不在未读取技术方案文档的情况下开始编码"
- [x] architect.md Non-Goals包含"不在方案设计阶段编写业务代码"
- [x] architect.md Non-Goals包含"不在需求未澄清时给出技术方案"
- [x] tester.md Non-Goals包含"不在测试阶段自行修复缺陷（须反馈developer）"
- [x] tester.md Non-Goals包含"不在未读取需求和技术方案的情况下设计测试用例"
- [x] reviewer.md Non-Goals包含"不在审查阶段直接修改业务代码"
- [x] reviewer.md Non-Goals包含"不在未读取前置文档的情况下给出审查结论"
- [x] orchestrator.md Non-Goals包含"不跳过阶段守卫检查直接允许跨阶段操作"
- [x] orchestrator.md Non-Goals包含"不在未确认前置文档已读取的情况下分配任务"

## 索引与路由更新检查

- [x] `.agents/rules/README.md` 的架构图包含stage-guardrails.md
- [x] `.agents/rules/README.md` 的索引表包含stage-guardrails.md条目
- [x] `.agents/protocols/README.md` 的协议定义表格包含pre-document-reading.md条目
- [x] AGENTS.md上下文路由表包含阶段守卫规则入口（stage-guardrails相关任务类型）
- [x] AGENTS.md上下文路由表包含前置文档读取协议入口（pre-document-reading相关任务类型）
- [x] AGENTS.md规则体系索引表包含stage-guardrails条目

## 整体质量与一致性检查

- [x] 所有新增/修改文档使用中文编写
- [x] 所有Mermaid图表语法正确
- [x] 所有文档间交叉引用链接有效（通过check-links.py验证，修复4个相对路径错误）
- [x] 阶段守卫规则与现有硬编码治理规则无矛盾
- [x] 功能演进三类流程与app-development-workflow协议兼容
- [x] 新增文档风格与现有`.agents/`文档一致（结构、术语、格式）
- [x] 前置文档清单中的每个文档路径均指向实际存在的文件
- [x] 拦截格式和确认格式在所有相关文档中保持一致
- [x] roles-governance/README.md执行看板已登记本spec状态
- [x] 全局看板已通过generate-dashboard.py自动更新（35/35 spec全部完成）
