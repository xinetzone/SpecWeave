---
source: "agent-skills-open-standard-wiki.md#三目录结构规范"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/agent-skills-wiki/02-directory-structure.toml"
id: "agent-skills-wiki-directory-structure"
title: "三、目录结构规范"
---
# 三、目录结构规范

## 3.1 标准目录结构

```
skill-name/
├── SKILL.md          # 必填：元数据 + 指令（核心文件）
├── scripts/          # 可选：可执行代码
├── references/       # 可选：参考文档
├── assets/           # 可选：模板、静态资源
└── evals/            # 可选：质量评估测试用例
    └── evals.json
```

## 3.2 目录说明

| 目录/文件 | 必填 | 用途 |
|----------|------|------|
| `SKILL.md` | ✅ | 核心文件，包含 YAML frontmatter 元数据和 Markdown 指令正文 |
| `scripts/` | ❌ | 可执行脚本（Python/Bash/JS等），智能体运行时调用 |
| `references/` | ❌ | 详细参考文档，智能体按需加载 |
| `assets/` | ❌ | 静态资源：模板、图片、数据文件、Schema 等 |
| `evals/` | ❌ | 评估测试用例，用于质量保证 |

> **源码锚点**：目录结构定义见 [specification.mdx](../../../../external/agentskills/docs/specification.mdx)
