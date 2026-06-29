# Tasks

> 主题：roles-governance（角色与治理体系）
> 适用场景：新增开发流程阶段守卫规则、前置文档强制读取协议、功能演进分类处理

- [x] Task 0: 前置依赖与影响分析
  - [x] SubTask 0.1: 确认核心角色体系与功能开发工作流已稳定（core-foundation全部完成）
  - [x] SubTask 0.2: 分析阶段守卫规则对现有7个角色的影响范围
  - [x] SubTask 0.3: 检查功能演进分类与app-development-workflow协议的兼容性
  - [x] SubTask 0.4: 识别需要同步更新的索引文件清单（AGENTS.md、rules/README.md、protocols/README.md、roles/README.md）
  - [x] SubTask 0.5: 确认新增规则/协议的命名和定位与现有体系一致

- [x] Task 1: 编写阶段守卫规则文档
  - [x] SubTask 1.1: 创建 `.agents/rules/stage-guardrails.md`
  - [x] SubTask 1.2: 编写标准阶段序列定义（8个标准阶段+负责角色）
  - [x] SubTask 1.3: 编写每个阶段的操作边界（允许操作/禁止操作/正例/反例）
  - [x] SubTask 1.4: 编写跨阶段拦截规则（拦截输出格式、拦截后行为规范）
  - [x] SubTask 1.5: 编写阶段跳转审批流程（跳过/逆向回退的条件与审批角色），含Mermaid流程图

- [x] Task 2: 编写前置文档强制读取协议
  - [x] SubTask 2.1: 创建 `.agents/protocols/pre-document-reading.md`
  - [x] SubTask 2.2: 编写各角色×各阶段的前置文档清单表格
  - [x] SubTask 2.3: 编写读取确认机制（输出格式、缺失处理、风险标注）
  - [x] SubTask 2.4: 编写新会话强制重载规则
  - [x] SubTask 2.5: 编写协议使用场景示例（含一个完整的端到端示例）

- [x] Task 3: 增强功能开发工作流文档
  - [x] SubTask 3.1: 更新 `.agents/workflows/feature-development.md` 的Mermaid流程图，增加功能演进分支判断节点
  - [x] SubTask 3.2: 更新"角色参与"表格，增加功能扩展/功能重构路径的角色参与列
  - [x] SubTask 3.3: 为现有8个步骤各增加"阶段守卫检查"和"前置文档确认"段落
  - [x] SubTask 3.4: 新增"功能扩展轻量流程"章节（6步骤：影响分析→增量方案→增量实现→回归测试→增量审查→合并）
  - [x] SubTask 3.5: 新增"功能重构重量流程"章节（7步骤：全量影响评估→方案重审→全量重规划→实现→全量回归→双重审查→合并），含回滚策略要求
  - [x] SubTask 3.6: 新增"变更类型判定指南"小节，含判定决策树（Mermaid）

- [x] Task 4: 更新角色Non-Goals
  - [x] SubTask 4.1: 更新 `.agents/roles/developer.md` 的Non-Goals，补充阶段守卫约束
  - [x] SubTask 4.2: 更新 `.agents/roles/architect.md` 的Non-Goals，补充阶段守卫约束
  - [x] SubTask 4.3: 更新 `.agents/roles/tester.md` 的Non-Goals，补充阶段守卫约束
  - [x] SubTask 4.4: 更新 `.agents/roles/reviewer.md` 的Non-Goals，补充阶段守卫约束

- [x] Task 5: 更新索引与入口文档
  - [x] SubTask 5.1: 更新 `.agents/rules/README.md`，在规则体系架构图和索引表中新增stage-guardrails.md
  - [x] SubTask 5.2: 更新 `.agents/protocols/README.md`，在协议定义表格中新增pre-document-reading.md
  - [x] SubTask 5.3: 更新 `AGENTS.md` 的上下文路由表，新增阶段守卫规则和前置文档读取协议的入口
  - [x] SubTask 5.4: 更新 `AGENTS.md` 的规则体系索引表，新增stage-guardrails条目
  - [x] SubTask 5.5: roles/README.md为索引文件无需更新，保持现状

- [x] Task 6: 验证
  - [x] SubTask 6.1: 运行 `python .agents/scripts/check-links.py` 验证所有新增/修改文档中的链接正确（修复4个相对路径错误）
  - [x] SubTask 6.2: 确认AGENTS.md路由表与实际文件结构一致
  - [x] SubTask 6.3: 验证阶段守卫规则与现有规则（硬编码治理等）无矛盾
  - [x] SubTask 6.4: 验证功能演进三类流程与app-development-workflow协议的兼容性
  - [x] SubTask 6.5: 验证所有Mermaid图表语法正确
  - [x] SubTask 6.6: 在roles-governance/README.md的执行看板中登记本spec状态

# Task Dependencies

- Task 0 必须最先执行（影响分析是后续工作的基础）
- Task 1 和 Task 2 可并行执行（两个独立文档，互不依赖）
- Task 3 依赖 Task 1 和 Task 2 完成（workflow中需要嵌入阶段守卫和前置文档读取的内容）
- Task 4 依赖 Task 1 完成（角色Non-Goals需要与阶段守卫规则一致）
- Task 5 依赖 Task 1-4 全部完成（索引更新需要所有文档就位）
- Task 6 依赖 Task 1-5 全部完成
