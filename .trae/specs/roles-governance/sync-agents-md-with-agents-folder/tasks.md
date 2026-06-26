# Tasks

- [x] Task 1: 读取 .agents/ 实际文件结构，确认索引表内容
  - [x] SubTask 1.1: 读取 .agents/modules/README.md，确认 8 个模块的 ID、层级、入口
  - [x] SubTask 1.2: 读取 .agents/tools/README.md，确认 4 个工具规范的名称、用途、入口
  - [x] SubTask 1.3: 读取 .agents/workflows/README.md，确认 3 个工作流的名称、用途、入口
  - [x] SubTask 1.4: 读取 .agents/templates/README.md，确认 2 个模板的名称、用途、入口
  - [x] SubTask 1.5: 读取 .agents/prompts/README.md，确认 5 个角色提示词的名称、入口
  - [x] SubTask 1.6: 读取 .agents/scripts/README.md，确认 7 个脚本的名称、用途、入口
- [x] Task 2: 更新 AGENTS.md，新增 5 个索引表
  - [x] SubTask 2.1: 在「角色定义索引」后新增「自我演进模块索引」表
  - [x] SubTask 2.2: 在「协作协议概要」后新增「工具规范索引」表
  - [x] SubTask 2.3: 在工具规范索引后新增「标准工作流索引」表
  - [x] SubTask 2.4: 在工作流索引后新增「模板索引」表
  - [x] SubTask 2.5: 在模板索引后新增「提示词索引」表
- [x] Task 3: 更新 AGENTS.md 上下文路由表
  - [x] SubTask 3.1: 补充 scripts 目录下所有脚本的说明（6 个新增）
  - [x] SubTask 3.2: 确保路由表格式与现有条目一致
- [x] Task 4: 更新 README.md 规范体系文档索引
  - [x] SubTask 4.1: 在折叠索引中补充 .agents/scripts/README.md 条目
  - [x] SubTask 4.2: 确认 README.md 中其他 .agents/ 引用与实际文件一致
- [x] Task 5: 验证与质量检查
  - [x] SubTask 5.1: 确认 AGENTS.md 所有索引表条目与 .agents/ 实际文件一一对应
  - [x] SubTask 5.2: 确认 README.md 规范体系文档索引与 .agents/ 实际文件一致
  - [x] SubTask 5.3: 运行 check-links.py 验证 AGENTS.md 和 README.md 链接有效
  - [x] SubTask 5.4: 确认索引表格式与现有「角色定义索引」一致
  - [x] SubTask 5.5: 确认未修改 .agents/ 下任何文件

# Task Dependencies

- Task 2、3、4 依赖 Task 1（需先确认实际文件结构）
- Task 5 依赖 Task 2、3、4（需先完成更新）
- Task 1 内部 SubTask 1.1-1.6 可并行
- Task 2 内部 SubTask 2.1-2.5 可并行
- Task 2、3、4 可并行（更新不同文件/区域）
