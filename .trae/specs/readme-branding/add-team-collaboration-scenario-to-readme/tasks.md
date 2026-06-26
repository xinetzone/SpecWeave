# Tasks

- [x] Task 1: 设计角色协作场景内容结构
  - [x] SubTask 1.1: 确定主导角色（orchestrator）与团队成员（architect/developer/reviewer/tester）
  - [x] SubTask 1.2: 设计触发条件（复杂任务接收、能力边界判断、角色相互 @ 触发）
  - [x] SubTask 1.3: 设计团队成员选择机制（基于 Responsibilities/Non-Goals 匹配）
  - [x] SubTask 1.4: 设计协作流程（任务分解→架构→实现→审查→测试→交付）
  - [x] SubTask 1.5: 设计任务分配方式（基于 bindings.rules 协议绑定）
  - [x] SubTask 1.6: 设计角色相互 @ 机制（去中心化协作模式）
  - [x] SubTask 1.7: 设计预期工作成果（交付物清单）
- [x] Task 2: 撰写「角色协作场景」章节内容
  - [x] SubTask 2.1: 撰写章节引言（场景概述与两种协作模式说明）
  - [x] SubTask 2.2: 撰写触发条件小节（含 orchestrator 主导与角色相互 @ 两种触发示例）
  - [x] SubTask 2.3: 撰写团队成员选择机制小节（含选择矩阵表）
  - [x] SubTask 2.4: 撰写协作流程小节（含 Mermaid 流程图，展示中心化与去中心化两种模式）
  - [x] SubTask 2.5: 撰写任务分配方式小节（含分配示例表）
  - [x] SubTask 2.6: 撰写角色相互 @ 机制小节（含 @ 语法示例与协作矩阵）
  - [x] SubTask 2.7: 撰写预期工作成果小节（含交付物清单表）
- [x] Task 3: 将章节插入 README.md
  - [x] SubTask 3.1: 在「系统规划」与「文档导航」之间插入新章节
  - [x] SubTask 3.2: 确保章节标题层级与现有结构一致（## 二级标题）
- [x] Task 4: 验证与质量检查
  - [x] SubTask 4.1: 运行 check-links.py 验证新增链接有效
  - [x] SubTask 4.2: 验证 Mermaid 图表语法正确
  - [x] SubTask 4.3: 确认场景描述与 .agents/roles/ 角色定义一致（Responsibilities/Non-Goals/bindings）
  - [x] SubTask 4.4: 确认场景描述与 .agents/protocols/ 协作协议一致（handoff/messaging/conflict-resolution/dependency-management）
  - [x] SubTask 4.5: 确认角色相互 @ 机制与 messaging 协议一致

# Task Dependencies

- Task 2 依赖 Task 1（需先设计内容结构）
- Task 3 依赖 Task 2（需先撰写内容）
- Task 4 依赖 Task 3（需先插入章节）
- Task 1 内部 SubTask 1.1-1.7 可并行设计
- Task 2 内部 SubTask 2.1-2.7 按顺序撰写
