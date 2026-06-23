# AI 智能体开发规范体系

[![License][license-badge]][license-link]
[![AGENTS.md][agents-badge]][agents-link]
[![Conventional Commits][commits-badge]][commits-link]
[![PRs Welcome][prs-badge]][prs-link]
[![Repo][repo-badge]][repo-link]
[![Issues][issue-badge]][issue-link]
[![Stars][star-badge]][star-link]
[![Forks][fork-badge]][fork-link]

[license-badge]: https://img.shields.io/badge/license-Apache--2.0-blue.svg
[license-link]: LICENSE
[agents-badge]: https://img.shields.io/badge/AGENTS.md-Open%20Standard-orange.svg
[agents-link]: AGENTS.md
[commits-badge]: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg
[commits-link]: https://conventionalcommits.org
[prs-badge]: https://img.shields.io/badge/PRs-welcome-brightgreen.svg
[prs-link]: CONTRIBUTING.md
[repo-badge]: https://img.shields.io/badge/repo-atomgit-blue.svg
[repo-link]: https://atomgit.com/daoCollective/AI
[issue-badge]: https://img.shields.io/badge/issues-welcome-red.svg
[issue-link]: https://atomgit.com/daoCollective/AI/issues
[star-badge]: https://img.shields.io/badge/stars-welcome-yellow.svg
[star-link]: https://atomgit.com/daoCollective/AI
[fork-badge]: https://img.shields.io/badge/forks-welcome-green.svg
[fork-link]: https://atomgit.com/daoCollective/AI

> 一套面向多智能体协作开发的开放规范体系，基于 [AGENTS.md 开放标准](https://agents.md) 定义智能体的角色、能力边界、协作协议与工作流，让 AI 智能体在项目中能够"按需加载、各司其职、协同交付"。

## 快速开始

```bash
# 克隆仓库
git clone <repository-url>
cd <repository-name>

# 验证 Git 忽略规则
python .agents/scripts/check-gitignore.py
```

预期输出：`验证通过: 所有临时依赖路径已被 .gitignore 覆盖`

将本仓库根目录指定为 AI 编码工具（Codex、Cursor、Copilot 等）的工作目录，工具会自动读取 `AGENTS.md` 作为项目级指令。

## 文档导航

| 文档 | 说明 |
|------|------|
| [项目概述](docs/project-overview.md) | 项目定位、设计理念、核心特性 |
| [项目结构](docs/project-structure.md) | 完整目录树与职责说明 |
| [技术栈与环境要求](docs/tech-stack.md) | 技术选型、环境依赖 |
| [智能体角色体系](docs/agent-roles.md) | 5 个核心角色定义与绑定关系 |
| [协作体系](docs/collaboration.md) | 4 项协作协议、3 个标准工作流 |
| [开发规范](docs/development-standards.md) | 代码风格、提交规范、测试要求、文档边界 |
| [验证与自动化](docs/verification-automation.md) | 临时依赖治理、验证脚本 |
| [知识库](docs/knowledge-base.md) | 技术知识库、复盘文档体系 |
| [贡献指南](CONTRIBUTING.md) | 贡献流程、分支命名、PR 规范 |
| [相关链接](docs/related-links.md) | 外部标准、工具文档、项目仓库 |

## 许可证

本项目基于 [Apache License 2.0](LICENSE) 开源。

## 联系方式

- **问题反馈**：[AtomGit Issues](https://atomgit.com/daoCollective/AI/issues)
- **讨论交流**：[AtomGit Pull Requests](https://atomgit.com/daoCollective/AI/pulls)

---

<details>
<summary>规范体系文档索引</summary>

| 文档 | 路径 | 说明 |
|---|---|---|
| 全局契约 | [AGENTS.md](AGENTS.md) | 智能体最高优先级入口 |
| 目录说明 | [.agents/README.md](.agents/README.md) | .agents/ 容器说明 |
| 角色索引 | [.agents/roles/README.md](.agents/roles/README.md) | 5 个角色索引与职责矩阵 |
| 提示词索引 | [.agents/prompts/README.md](.agents/prompts/README.md) | 系统提示词使用说明 |
| 工具规范索引 | [.agents/tools/README.md](.agents/tools/README.md) | 4 类工具调用规范 |
| 协议索引 | [.agents/protocols/README.md](.agents/protocols/README.md) | 4 项协作协议 |
| 工作流索引 | [.agents/workflows/README.md](.agents/workflows/README.md) | 3 个标准工作流 |
| 模板索引 | [.agents/templates/README.md](.agents/templates/README.md) | 任务与交接模板 |
| 规格文档 | [.trae/specs/create-agents-md-and-config/spec.md](.trae/specs/create-agents-md-and-config/spec.md) | 本体系的需求规格 |
| 知识库索引 | [docs/knowledge/README.md](docs/knowledge/README.md) | 技术知识库入口 |
| 复盘体系索引 | [docs/retrospective/README.md](docs/retrospective/README.md) | 复盘文档体系入口 |
| 提示词萃取 | [docs/retrospective/prompt-extraction.md](docs/retrospective/prompt-extraction.md) | 可迁移提示词模式与方法论 |

</details>