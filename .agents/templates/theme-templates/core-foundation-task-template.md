# Tasks

> 主题：core-foundation（核心体系基础）
> 适用场景：从零创建新的目录结构、核心系统、管理体系、工作空间

- [ ] Task 0: 前置依赖验证
  - [ ] SubTask 0.1: 确认所有前置 spec 已 100% 完成（检查对应 tasks.md 复选框状态）
  - [ ] SubTask 0.2: 确认项目根目录结构符合预期（参照 AGENTS.md 目录树）
  - [ ] SubTask 0.3: 确认无同名或功能重叠的现有系统/目录（避免重复建设）
  - [ ] SubTask 0.4: 明确新系统的定位、边界和与现有系统的关系

- [ ] Task 1: 目录结构与骨架创建
  - [ ] SubTask 1.1: 创建目标目录结构（参照现有目录风格，如 .agents/、docs/ 的组织方式）
  - [ ] SubTask 1.2: 创建核心入口文件/配置文件
  - [ ] SubTask 1.3: 编写基础骨架内容（参考现有类似文件的结构和风格）
  - [ ] SubTask 1.4: 在上级索引文档中登记（如 AGENTS.md 路由表、docs/README.md 等）

- [ ] Task 2: 核心内容实现
  - [ ] SubTask 2.1: 实现核心功能模块/编写核心内容文档
  - [ ] SubTask 2.2: 创建子目录结构（如需要，如 roles/、prompts/、scripts/ 等）
  - [ ] SubTask 2.3: 编写各子模块/子文档的内容
  - [ ] SubTask 2.4: 为子目录创建 README.md 索引（如子目录包含 3 个以上文件）
  - [ ] SubTask 2.5: 编写使用说明或快速开始指南

- [ ] Task 3: 路径与引用更新
  - [ ] SubTask 3.1: 检查所有内部相对路径引用是否正确
  - [ ] SubTask 3.2: 更新其他文件中指向新系统的引用（如有）
  - [ ] SubTask 3.3: 跨主题引用注意 `../` 层级（主题目录下文件引用根目录需用 `../../../`）

- [ ] Task 4: 验证与集成
  - [ ] SubTask 4.1: 运行 check-spec-consistency.py 验证 spec 内部一致性
  - [ ] SubTask 4.2: 运行 check-links.py 验证所有链接有效（如适用）
  - [ ] SubTask 4.3: 验证交付物完整存在（所有规划的文件和目录均已创建）
  - [ ] SubTask 4.4: 验证文件命名符合 kebab-case 规范
  - [ ] SubTask 4.5: 确认无临时文件或中间产物遗留
  - [ ] SubTask 4.6: 在对应主题 README.md 的执行看板中登记完成状态

# Task Dependencies

- Task 0 必须最先执行（确保前置条件满足）
- Task 1 依赖 Task 0 完成
- Task 2 依赖 Task 1 完成（需要骨架就位）
- Task 3 可与 Task 2 并行后期执行，或在 Task 2 完成后执行
- Task 4 依赖 Task 2、3 完成
