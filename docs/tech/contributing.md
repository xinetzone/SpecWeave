# 贡献指南

欢迎参与 SpecWeave 项目贡献！无论是提交问题、改进文档还是贡献代码，我们都非常感谢。

## 贡献流程

### 1. 启动协议（必须遵守）

所有 AI 智能体在参与项目前，**必须首先阅读并遵守**根目录 [`AGENTS.md`](../../AGENTS.md) 中定义的启动协议：

- **步骤 1**：读取 `AGENTS.md` 全文
- **步骤 2**：按「上下文路由表」确定本次任务需要读取的规范文件
- **步骤 3**：读取对应的规范文件（角色定义/复盘模板/知识库等）
- **步骤 3.5**：完成自检（确认任务类型、内容敏感度、相关规范已读取、相关 Skill 应被加载）
- **步骤 4**：在规范指导下选择 Skill 工具并执行任务

> ⚠️ **禁止在完成步骤 1-3.5 之前加载 Skill 或生成任何产出物。**

### 2. 提交 Pull Request

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 遵循 [Conventional Commits](https://conventionalcommits.org) 规范提交更改
   - 格式：`type(scope): subject`，主体使用中文描述
   - 修复类提交须标注预防措施类型
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

### 3. 代码审查

- 所有 PR 必须经过代码审查
- 审查员角色遵循 `.agents/roles/reviewer.md` 定义
- 确保所有自动化检查通过（CI 流水线）

### 4. 开发规范

完整开发规范见 `.agents/docs/development-standards.md`，核心要点：

- **代码风格**：遵循现有代码风格，新增 `.agents/scripts/` 脚本前先查阅 `lib/README.md` 共享库，禁止重复实现已有功能
- **测试要求**：单元测试覆盖率不低于 80%，关键模块不低于 90%，所有测试用例通过无回归
- **文档边界**：`AGENTS.md`/`.agents/` 面向 AI 智能体，`.agents/docs/` 是唯一有效的文档容器
- **路径引用**：Markdown 文档交叉引用使用相对路径，禁止 `file:///` 绝对路径

---

:::{note}
本文档为初始骨架，更详细的贡献指南将逐步完善。
:::
