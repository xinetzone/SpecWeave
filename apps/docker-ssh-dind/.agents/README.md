# docker-ssh-dind .agents/ 目录

本目录是 docker-ssh-dind 子项目的 AI 资产容器，遵循 SpecWeave 渐进式披露规范：

## 目录结构

| 目录 | 职责 | 当前状态 |
|------|------|---------|
| rules/ | 项目特有规则（Containerfile、entrypoint、构建测试） | 已有3个规则文件 |
| roles/ | 角色定义 | 预留（.gitkeep） |
| skills/ | 项目专属技能 | 预留（.gitkeep） |
| scripts/ | 自动化脚本（构建、测试、验证） | 预留（.gitkeep） |
| workflows/ | 工作流定义 | 预留（.gitkeep） |
| templates/ | 模板文件 | 预留（.gitkeep） |
| docs/ | AI专属知识库 | 预留（.gitkeep） |

## 与父级工作区的关系

- 全局规则、Skill、角色、命令集 → 继承自 `../../../.agents/`（SpecWeave根）
- 本目录仅存放 docker-ssh-dind **特有**的AI资产
- 通用能力（七概念、原子提交、CI检查等）不重复实现，直接调用父级

## 何时扩展本目录

- 新增项目专属自动化脚本 → scripts/
- 需要定义项目特有的角色/职责 → roles/
- 可复用的项目工作流 → workflows/
- 项目专属知识/决策记录 → docs/
