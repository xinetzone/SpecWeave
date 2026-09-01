---
id: "templates-theme-templates-core-foundation-task-template"
title: "Tasks"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/theme-templates/core-foundation-task-template.toml"
version: "1.1.0"
patterns_applied: ["spec-driven-development", "three-tier-governance", "four-negatives-external-dependency", "entry-container-separation"]
---
# Tasks

> 主题：core-foundation（核心体系基础）
> 适用场景：从零创建新的目录结构、核心系统、管理体系、工作空间
>
> **L3标准化模式集成**：本模板已应用以下L3标准化模式——
> - [spec-driven-development](../../../docs/retrospective/patterns/methodology-patterns/creative-design/spec-driven-development.md)：Spec驱动开发，先规划再执行
> - [three-tier-governance](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md)：三层治理闭环（原子化→自动化→验证）
> - [four-negatives-external-dependency](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/four-negatives-external-dependency.md)：零依赖原则，脚本仅用标准库
> - [entry-container-separation](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/entry-container-separation.md)：入口精简，容器承载深度内容

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
  - [ ] SubTask 1.5: **入口精简检查**（entry-container-separation模式）：入口文档（README.md/索引文件）控制在<100行，仅含导航和快速索引，深度内容放在子文件中

- [ ] Task 2: 核心内容实现
  - [ ] SubTask 2.1: 实现核心功能模块/编写核心内容文档
  - [ ] SubTask 2.2: 创建子目录结构（如需要，如 roles/、prompts/、scripts/ 等）
  - [ ] SubTask 2.3: 编写各子模块/子文档的内容
  - [ ] SubTask 2.4: 为子目录创建 README.md 索引（如子目录包含 3 个以上文件）
  - [ ] SubTask 2.5: 编写使用说明或快速开始指南
  - [ ] SubTask 2.6: **零依赖检查**（four-negatives-external-dependency模式）：新增Python脚本仅使用标准库，不引入第三方包依赖，确保跨平台即用

- [ ] Task 3: 路径与引用更新
  - [ ] SubTask 3.1: 检查所有内部相对路径引用是否正确
  - [ ] SubTask 3.2: 更新其他文件中指向新系统的引用（如有）
  - [ ] SubTask 3.3: 跨主题引用注意 `../` 层级（主题目录下文件引用根目录需用 `../../../`）

- [ ] Task 4: 验证与集成（遵循three-tier-governance三层治理闭环）
  - [ ] SubTask 4.1: 运行 check-spec-consistency.py 验证 spec 内部一致性（L1原子化验证）
  - [ ] SubTask 4.2: 运行 check-links.py 验证所有链接有效（如适用）（L2自动化验证）
  - [ ] SubTask 4.3: 验证交付物完整存在（所有规划的文件和目录均已创建）
  - [ ] SubTask 4.4: 验证文件命名符合 kebab-case 规范
  - [ ] SubTask 4.5: 确认无临时文件或中间产物遗留
  - [ ] SubTask 4.6: 在对应主题 README.md 的执行看板中登记完成状态
  - [ ] SubTask 4.7: **元文档杠杆验证**（meta-document-leverage模式）：新增模块后上级索引/README已同步更新，导航路径完整
  - [ ] SubTask 4.8: **三层治理门禁确认**：原子化规范存在→自动化检查脚本就绪→提交前验证通过

# Task Dependencies

- Task 0 必须最先执行（确保前置条件满足）
- Task 1 依赖 Task 0 完成
- Task 2 依赖 Task 1 完成（需要骨架就位）
- Task 3 可与 Task 2 并行后期执行，或在 Task 2 完成后执行
- Task 4 依赖 Task 2、3 完成
