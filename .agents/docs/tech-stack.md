# 技术栈与环境要求

> **来源**：从 `README.md` "技术栈"与"环境要求"章节拆分

## 技术栈

| 类别 | 技术 / 标准 | 用途 |
|---|---|---|
| 智能体标准 | [AGENTS.md Open Standard](https://agents.md) | 项目级智能体指令文件 |
| 元数据格式 | YAML Frontmatter (---) + x-toml-ref | 唯一标准frontmatter格式，核心字段直接存储，完整元数据通过x-toml-ref引用外部TOML |
| 可视化 | [Mermaid](https://mermaid.js.org/) | 流程图、架构图、关系图 |
| 提交规范 | [Conventional Commits 1.0](https://conventionalcommits.org) | 统一提交信息格式 |
| 版本控制 | [Git](https://git-scm.com/) | 源代码版本管理 |
| 验证脚本 | [Python 3.13+](https://www.python.org/) | .gitignore 规则与 git 状态验证 |
| 自动化 | Git Hooks (pre-commit) | 阻止临时依赖被提交 |
| 许可证 | [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) | 开源许可证 |

## 环境要求

使用本规范体系前，请确认本地已安装以下工具：

| 工具 | 最低版本 | 用途 | 必需 |
|---|---|---|---|
| Git | 2.30+ | 版本控制、执行 hooks | 是 |
| Python | 3.13+ | 运行验证脚本 | 否（仅验证时需要） |
| AI 编码工具 | — | Codex / Cursor / Copilot / Claude 等 | 是 |

> 本规范体系本身不包含可执行的业务代码，无需安装运行时依赖。

> **关联模块**：
> - `../README.md`
> - `verification-automation.md`