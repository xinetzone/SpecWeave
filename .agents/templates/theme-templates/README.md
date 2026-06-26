# 主题任务模板索引

本目录包含按主题分类的 spec 任务模板。创建新 spec 时，根据归类结果选择对应主题模板作为 tasks.md 的编写参考。

## 使用方法

1. 按照 [.trae/specs/README.md](../../.trae/specs/README.md) 中的归类决策树确定主题
2. 复制对应主题模板到新 spec 目录的 `tasks.md`
3. 根据具体任务需求填充和调整任务项
4. 删除模板中的注释和提示文字
5. 同步编写 `spec.md`（需求规格）和 `checklist.md`（验收清单）

## 模板清单

| 模板文件 | 适用主题 | 核心特点 |
|---|---|---|
| [core-foundation-task-template.md](core-foundation-task-template.md) | 核心体系基础 | 前置验证→骨架创建→内容实现→验证集成 |
| [roles-governance-task-template.md](roles-governance-task-template.md) | 角色与治理体系 | 影响分析→角色/规则定义→索引同步→权限验证 |
| [standards-tools-task-template.md](standards-tools-task-template.md) | 规范标准与工具链 | 需求设计→核心实现→测试验证→集成文档 |
| [readme-branding-task-template.md](readme-branding-task-template.md) | README 与品牌定位 | 内容规划→文案撰写→一致性检查→渲染验证 |
| [docs-restructure-task-template.md](docs-restructure-task-template.md) | 文档体系重组 | 现状调研→执行重组（原子提交）→验证修复→收尾 |
| [retrospectives-insights-task-template.md](retrospectives-insights-task-template.md) | 复盘与洞察萃取 | 复盘准备→信息分析→报告撰写→归档联动 |
| [migration-archival-task-template.md](migration-archival-task-template.md) | 迁移与归档 | 迁移准备→萃取清理→执行迁移→验证收尾 |

## 通用约定

所有模板遵循以下统一约定：

- 任务编号从 Task 0 开始（Task 0 为前置准备/验证）
- 每个 Task 包含若干 SubTask，使用 `- [ ]` 复选框格式
- 任务描述以动词开头，明确可执行
- 包含 `# Task Dependencies` 章节说明任务间依赖关系
- 最后一个任务必须包含"在主题 README.md 中登记"子任务
