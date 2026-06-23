# 开发规范

> **来源**：从 `README.md` "开发规范"章节拆分

## 代码风格

- 遵循现有代码风格，不引入与项目不一致的新风格。
- 命名、缩进、注释、文件组织均以仓库内既有约定为准。
- 新增依赖前先评估必要性，优先复用现有工具链。

## 提交规范

遵循 [Conventional Commits](https://conventionalcommits.org) 规范，格式为 `type(scope): subject`：

| 类型 | 用途 |
|---|---|
| `feat` | 新功能 |
| `fix` | 缺陷修复 |
| `refactor` | 代码重构（不改变行为） |
| `test` | 测试相关 |
| `docs` | 文档变更 |
| `chore` | 构建、工具、依赖等杂项 |
| `perf` | 性能优化 |

提交信息主体使用中文描述，简明扼要说明"为什么"而非仅"做了什么"。

## 测试要求

- 每个模块必须有对应的单元测试，覆盖核心逻辑与边界条件。
- 整体测试覆盖率不低于 **80%**，关键模块不低于 **90%**。
- 所有测试用例通过，无新增失败用例与回归问题。

## 文档边界

- `README.md` 面向**人类读者**，介绍项目用途、安装、使用与贡献方式。
- `AGENTS.md` 与 `.agents/` 面向 **AI 智能体**，存放机器可读规范。
- 两者职责分离，不相互混用。

## 派生产物溯源约定

从其他文档（如 `README.md`、spec 文档）派生出的结构化产物，须在 TOML frontmatter 携带 `source` 字段标注信息来源，建立"提取物→源头"的可追溯链路。

- **字段格式**：`source = "<文件路径>#<章节锚点>"`
- **示例**：`source = "README.md#自我迭代机制"`
- **适用范围**：一切从源文档提取并独立归档的结构化定义文件（如 `.agents/modules/` 下的自我演进模块定义）。
- **价值**：源头文档变更时，可程序化定位受影响的派生产物，避免信息失同步。

## Spec 文档路径引用规范

spec 文档位于 `.trae/specs/<change-id>/` 三级嵌套目录下，路径引用存在两类系统性风险："层级陷阱"（相对路径层级计算错误）与"前缀缺失"（未添加项目根目录前缀）。为消除这两类风险，所有 spec 文档的路径引用须遵循以下规范：

### 规则 1：引用项目根目录文件使用三级回退

spec 文档位于 `.trae/specs/<change-id>/spec.md`，引用项目根目录下的文件时，必须使用三级 `../../../` 回退至项目根目录。

| 错误写法 | 正确写法 | 说明 |
|---------|---------|------|
| `AGENTS.md` → `../../AGENTS.md` | `AGENTS.md` → `../../../AGENTS.md` | 两级回退仅到 `.trae/`，无法到达项目根 |
| `README.md` → `../../README.md` | `README.md` → `../../../README.md` | 同上 |
| `.agents/README.md` → `../../.agents/README.md` | `.agents/README.md` → `../../../.agents/README.md` | 同上 |

### 规则 2：引用 `.agents/` 下文件使用完整前缀

在 spec 文档的描述性文本中引用 `.agents/` 目录下的文件时，必须使用完整路径前缀 `.agents/`，确保 `check-spec-consistency.py` 的 `resolve_path` 函数能正确按项目根目录解析。

| 错误写法 | 正确写法 | 说明 |
|---------|---------|------|
| `` `worlds/README.md` `` | `` `.agents/worlds/README.md` `` | 缺少 `.agents/` 前缀，被误解析为 spec 目录相对路径 |
| `` `teams/permission-system.md` `` | `` `.agents/teams/permission-system.md` `` | 同上 |
| `` `protocols/conflict-resolution.md` `` | `` `.agents/protocols/conflict-resolution.md` `` | 同上 |

### 规则 3：引用同目录 spec 使用单级回退

引用 `.trae/specs/` 下其他 spec 文档时，使用单级 `../` 回退至 `specs/` 目录。

| 正确写法 | 说明 |
|---------|------|
| `create-agents-md-and-config` → `../create-agents-md-and-config/spec.md` | 单级回退至 `specs/`，再进入目标 spec 目录 |

### 验证方式

- **链接有效性**：运行 `python .agents/scripts/check-links.py`，退出码为 0 表示所有本地链接有效
- **spec 一致性**：运行 `python .agents/scripts/check-spec-consistency.py`，交叉引用有效性错误数为 0 表示路径前缀正确

> **关联模块**：
> - `../README.md`
> - `../AGENTS.md`
> - `../CONTRIBUTING.md`