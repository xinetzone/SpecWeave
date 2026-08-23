---
type: Example
title: SKILL.md 编写示例
description: 从零编写一个符合 Agent Skills 开放标准的 SKILL.md，涵盖 frontmatter、工作流、脚本引用、references 和 allowed-tools
tags: [agent-skills, skill.md, example, authoring, tutorial]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: awesun-ui-locator-source
    resource: "/references/awesun-ui-locator-source.md"
    title: awesun-ui-locator 源码
  - id: awesun-skill-source
    resource: "/references/awesun-skill-source.md"
    title: awesun-skill 源码
  - id: jira-skill-source
    resource: "/references/jira-skill-source.md"
    title: jira-skill 源码
---

# SKILL.md 编写示例

本文档通过一个完整示例演示如何编写符合 Agent Skills 开放标准的 SKILL.md。示例综合了 awesun-ui-locator 的工作流模式、awesun-skill 的工具清单模式和 jira-skill 的脚本组织模式。

## 第一步：最小可用 SKILL.md

一个最小的技能只需要一个 SKILL.md 文件，包含 name 和 description 两个必需字段：

```markdown
---
name: hello-world
description: 示例技能，用于演示 SKILL.md 编写。当用户说"打招呼"或"问候"时使用。
---

# Hello World

这是一个示例技能。当激活时，向用户友好地打招呼。

## 工作流

1. 识别用户希望被问候的语言
2. 使用对应语言说"你好"
```

### 关键要点

- `name` 使用 kebab-case
- `description` 必须包含**功能描述**和**触发关键词**——这是 AI 判断是否加载技能的唯一依据
- 正文应简洁，说明"做什么"和"怎么做"

## 第二步：添加 version 和 metadata

参考 jira-skill 和 retro-skill 的实践，为技能添加版本和元数据：

```markdown
---
name: data-processor
description: 数据处理技能，支持 CSV/JSON 文件的清洗、转换和统计分析。关键词：数据清洗、CSV处理、JSON转换、数据统计。
version: 1.0.0
license: MIT
metadata:
  author: Your Name
  version: 1.0.0
  repository: https://github.com/yourname/data-processor
---
```

如果技能遵循 Plugin 规范，`metadata.version` 应与 plugin.json 的 version 保持一致。

## 第三步：添加 allowed-tools

如果技能需要执行脚本或读写文件，通过 `allowed-tools` 声明所需权限：

```markdown
---
name: data-processor
description: 数据处理技能，支持 CSV/JSON 文件的清洗、转换和统计分析。
version: 1.0.0
allowed-tools:
  - Bash(python3:*)
  - Read
  - Write
---
```

常见的 allowed-tools 声明（参考 retro-skill）：

```yaml
allowed-tools:
  - Bash(python3:*)      # 执行 Python 脚本
  - Bash(git:*)          # 执行 git 命令
  - Bash(gh:*)           # GitHub CLI
  - Bash(jq:*)           # JSON 处理
  - Read                 # 读取文件
  - Write                # 写入文件
  - Edit                 # 编辑文件
  - Glob                 # 文件通配符搜索
  - Grep                 # 内容搜索
  - Task                 # 任务管理
```

纯知识技能（如 jira-syntax）不需要 allowed-tools。

## 第四步：组织正文结构

### 工具清单模式（参考 awesun-skill）

如果技能封装了多个工具，按类别列出：

```markdown
## Available Tools

### Data Loading
- `load_csv` - 加载 CSV 文件，自动检测编码和分隔符
    - Required parameters:
      - `path` (string): 文件路径
    - Optional parameters:
      - `encoding` (string): 文件编码，默认自动检测
      - `delimiter` (string): 分隔符，默认自动检测

### Data Transformation
- `filter_rows` - 按条件过滤行
    - Required parameters:
      - `condition` (string): 过滤条件表达式
- `sort_data` - 按列排序
```

### 工作流模式（参考 awesun-ui-locator）

如果技能定义了多步流程，使用编号步骤：

```markdown
## Workflow

### Step 1: Read the File
使用 Read 工具读取用户指定的数据文件。支持 .csv 和 .json 格式。

### Step 2: Analyze Structure
检查数据结构：列名、数据类型、缺失值比例。

### Step 3: Clean Data
根据分析结果执行清洗：
- 去除完全空行
- 标准化日期格式
- 去除字符串首尾空格

### Step 4: Transform
按用户要求转换数据（过滤、排序、聚合）。

### Step 5: Output Results
以 JSON 格式返回处理结果和统计摘要。
```

### 意图映射模式（参考 jira-skill）

如果技能有多个脚本，提供意图到脚本的映射表：

```markdown
## Script Mapping

| User Intent | Command |
|-------------|---------|
| 加载并预览数据 | `python scripts/load.py preview <path>` |
| 过滤数据 | `python scripts/transform.py filter --condition <expr>` |
| 生成统计报告 | `python scripts/stats.py report <path> --format json` |
| 导出结果 | `python scripts/export.py <input> --output <path>` |
```

## 第五步：添加 References 表

当正文较长时，将详细文档移入 references/ 子目录，在 SKILL.md 中引用：

```markdown
## References

| Document | Purpose |
|----------|---------|
| [references/csv-format.md](references/csv-format.md) | CSV 格式细节和编码处理 |
| [references/transformations.md](references/transformations.md) | 所有转换操作的完整参考 |
| [references/troubleshooting.md](references/troubleshooting.md) | 常见问题和故障排除 |
```

AI 在需要具体细节时才读取这些文档，保持主入口精简。

## 第六步：添加脚本

创建 `scripts/` 目录存放可执行脚本。遵循 PEP 723 模式（参考 jira-skill）：

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pandas>=2.0,<3",
#     "click>=8.1,<9",
# ]
# ///
"""Data loading and preview."""

import sys
from pathlib import Path
import click
import pandas as pd

@click.group()
def cli():
    """Data loading tools."""
    pass

@cli.command()
@click.argument("path")
@click.option("--rows", default=10, help="Number of rows to preview")
def preview(path, rows):
    """Preview a CSV file."""
    df = pd.read_csv(path)
    click.echo(df.head(rows).to_json(orient="records", indent=2))

if __name__ == "__main__":
    cli()
```

### 脚本契约

所有脚本应遵循统一 CLI 契约（参考 jira-skill）：
- `--json`：JSON 格式输出
- `--quiet`：静默模式
- `--debug`：调试输出
- `--dry-run`：写操作的预览模式
- `--help`：自动生成的帮助

## 完整示例

以下是一个完整的 SKILL.md，综合了上述所有模式：

```markdown
---
name: log-analyzer
description: 日志文件分析技能，支持解析常见日志格式、错误统计、时间线生成和异常检测。
  当用户提到"分析日志"、"排查错误"、"日志统计"、"异常检测"时使用。
  支持 .log、.jsonl 格式和常见应用日志格式。
version: 1.0.0
license: MIT
allowed-tools:
  - Bash(python3:*)
  - Read
  - Glob
  - Grep
---

# Log Analyzer

分析应用日志文件，识别错误模式，生成统计摘要。

## Workflow

1. 使用 Glob 或用户指定路径定位日志文件
2. 读取文件前 100 行检测日志格式
3. 使用 scripts/parse.py 解析日志
4. 使用 scripts/stats.py 生成统计
5. 向用户报告摘要和异常发现

## Script Mapping

| Intent | Command |
|--------|---------|
| 解析日志 | `python scripts/parse.py <file> --format auto` |
| 错误统计 | `python scripts/stats.py errors <file> --json` |
| 时间线 | `python scripts/stats.py timeline <file> --from <time> --to <time>` |
| 异常检测 | `python scripts/detect.py <file> --threshold 3` |

## Common Patterns

- 统计 ERROR 级别日志数量
- 按错误消息分组找出 Top 10 高频错误
- 检测短时间内大量错误的爆发模式
- 提取特定 request ID 的完整日志链路

## References

| Document | Purpose |
|----------|---------|
| [references/formats.md](references/formats.md) | 支持的日志格式和正则定义 |
| [references/queries.md](references/queries.md) | 常用查询示例 |
```

## 常见错误

1. **description 过于简短**：只写"日志分析"没有触发词和场景，AI 可能不会在正确时机激活。
2. **正文过长**：把所有参考文档内容塞入 SKILL.md 正文，导致每次激活消耗大量 Token。使用 references/ 分层。
3. **重复脚本实现**：SKILL.md 不应粘贴脚本代码，只需说明何时调用、如何传参。需要理解实现时 AI 会自行读取脚本。
4. **缺少触发关键词**：description 应包含用户可能使用的各种表达方式。
5. **version 不一致**：插件中 plugin.json 和各 SKILL.md 的版本号必须同步，使用 CI 门控。

## 相关概念

- [SKILL.md 标准与渐进式披露](/concepts/01-skill-md-standard.md)
- [Skill 脚本工具模式](/concepts/10-skill-tooling-scripts.md)
- [插件架构](/concepts/05-plugin-architecture.md)
