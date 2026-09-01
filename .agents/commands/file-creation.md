---
id: "file-creation"
title: "文件创建指令集"
source: "AGENTS.md#文件创建纪律"
x-toml-ref: "../../.meta/toml/.agents/commands/file-creation.toml"
---
# 文件创建指令集

## 触发条件

- 需要创建新文档或代码文件时
- 文件迁移或重命名时
- 收到明确的文件创建任务时

## 输入规范

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| file_name | string | 是 | 拟创建的文件名（建议符合 kebab-case） |
| file_content | string | 是 | 文件内容 |
| target_directory | string | 否 | 目标目录（未指定时自动确定） |
| file_type | string | 否 | 文件类型：`document`/`code`/`configuration` |

## RACI责任分配矩阵

**RACI模型说明**：
- **R** = 负责执行（Responsible）：实际完成工作的角色
- **A** = 最终审批（Accountable）：对结果负最终责任，拥有最终决策权，每项活动有且仅有一个A
- **C** = 需咨询（Consulted）：决策前需征求意见、提供专业输入的角色，双向沟通
- **I** = 需知会（Informed）：决策后需告知进展与结果的角色，单向沟通

| 文件创建核心活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 触发文件创建任务 | **R/A** | I | I | I | I | I |
| 确定归属目录（步骤1） | R | C | **A** | C | I | I |
| 确定文件名格式（步骤2） | R | C | **A** | C | I | I |
| 自动化验证（步骤3） | R | I | **A** | C | I | I |
| 文件创建执行 | R | I | **A** | C | I | I |
| 文件内容质量验收 | C | C | I | **R/A** | I | I |
| 归档与索引更新 | **R/A** | I | I | C | I | I |

### 审批权限边界

- **常规文件创建**：developer审批文件名合规性，reviewer审批文件内容质量
- **架构相关文件**：architect参与目录归属决策
- **重大文件变更**（跨模块/规范类文件）：co-founder最终审批

## 执行步骤

### 步骤 1：确定归属目录

查阅 [docs/knowledge/README.md](../../docs/knowledge/README.md)，根据文件内容类型确定应放置的分类目录：

| 文件类型 | 推荐目录 |
|---------|---------|
| 学习报告 | `docs/knowledge/learning/` |
| 操作指南 | `docs/knowledge/operations/` |
| 故障排除 | `docs/knowledge/troubleshooting/` |
| 架构决策 | `docs/knowledge/decisions/` |
| 最佳实践 | `docs/knowledge/best-practices/` |
| 代码文件 | `apps/` 或 `.agents/scripts/` |
| 配置文件 | 项目根目录或 `.agents/config/` |

**禁止在项目根目录直接创建文档文件**。

### 步骤 2：确定文件名格式

查阅 [.agents/rules/file-naming-convention.md](../rules/file-naming-convention.md)，确保文件名遵循以下规则：

- 采用 kebab-case（小写字母 + 连字符 `-` 分隔）
- 纯英文命名，禁止中文
- 文件扩展名正确（`.md`、`.py`、`.json` 等）
- 符合项目约定的命名模式（日期格式 `YYYY-MM-DD-*`、编号格式 `NN-*`）

### 步骤 3：自动化验证

运行文件名检查脚本验证合规性：

```bash
# CLI 方式
python .agents/scripts/check-filename-convention.py <文件名>

# 或使用统一检查工具
python .agents/scripts/repo-check.py filename --directory <目录>

# API 方式（Python）
from .agents.scripts.lib.checks.filename import run
result = run(project_root, args)
```

**验证不通过时**：修正文件名后重新执行步骤 3。

### 步骤 4：创建文件

验证通过后执行文件创建：

1. 在目标目录创建文件
2. 添加必要的 frontmatter（TOML 或 YAML）
3. 写入文件内容
4. 更新相关索引（如适用）

### 步骤 5：质量验收

- 文件名合规性：通过自动化检查
- 目录归属：符合知识分类体系
- 文件内容：格式正确、链接有效
- Frontmatter：完整且符合规范

## 输出规范

| 产出物 | 格式 | 存储位置 |
|--------|------|---------|
| 创建的文件 | 根据文件类型 | 目标目录 |
| 验证报告 | CLI 输出 | 控制台 |
| 索引更新 | 自动 | 相关索引文件 |

## 质量验收

- 文件名通过 `check-filename-convention.py` 验证
- 文件放置在正确的分类目录
- 文件内容完整、格式正确
- 若为 Markdown 文件，frontmatter 完整
- 相关索引已更新

## 约束条件

- 禁止在项目根目录创建文档文件
- 文件名必须遵循 kebab-case 规范
- 必须通过自动化验证后才能创建文件
- 不负责文件内容的业务逻辑审查（归对应角色）

## 关联资源

- [文件创建前置检查模式](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/file-creation-precheck-pattern.md)
- [文件命名规范](../rules/file-naming-convention.md)
- [文件名检查脚本](../scripts/check-filename-convention.py)
- [知识库入口](../../docs/knowledge/README.md)