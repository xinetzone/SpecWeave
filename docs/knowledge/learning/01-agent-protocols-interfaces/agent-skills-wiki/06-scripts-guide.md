---
source: "agent-skills-open-standard-wiki.md#七脚本使用指南"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/06-scripts-guide.toml"
id: "agent-skills-wiki-scripts-guide"
title: "/// script"
---
## 七、脚本使用指南

### 7.1 一次性命令 vs 捆绑脚本

当现有包已经能满足你的需求时，可以直接在 `SKILL.md` 指令中引用它，无需 `scripts/` 目录。许多生态系统提供在运行时自动解析依赖的工具：

| 工具 | 生态系统 | 示例 |
|------|---------|------|
| `uvx` | Python | `uvx ruff@0.8.0 check .` |
| `pipx` | Python | `pipx run 'black==24.10.0' .` |
| `npx` | Node.js | `npx eslint@9 --fix .` |
| `bunx` | Bun | `bunx eslint@9 --fix .` |
| `deno run` | Deno | `deno run npm:create-vite@6 my-app` |
| `go run` | Go | `go run golang.org/x/tools/cmd/goimports@v0.28.0 .` |

**一次性命令提示**：
- **固定版本**（例如 `npx eslint@9.0.0`），使命令随时间表现一致
- 在 `SKILL.md` 中**说明前置条件**（例如"需要 Node.js 18+"）
- **将复杂命令移入脚本**。当命令复杂到第一次尝试很难正确时，`scripts/` 中经过测试的脚本更可靠。

### 7.2 从 SKILL.md 引用脚本

使用**相对于技能目录根目录的相对路径**来引用捆绑文件。智能体会自动解析这些路径——不需要绝对路径。

在 `SKILL.md` 中列出可用脚本：

```markdown
## 可用脚本
- **`scripts/validate.sh`** — 验证配置文件
- **`scripts/process.py`** — 处理输入数据
```

然后指示智能体运行它们：

````markdown
## 工作流
1. 运行验证脚本：
```bash
bash scripts/validate.sh "$INPUT_FILE"
```

2. 处理结果：
```bash
python3 scripts/process.py --input results.json
```
````

相同的相对路径约定适用于支持文件，如 `references/*.md`——脚本执行路径（在代码块中）是相对于**技能目录根目录**的，因为智能体从那里运行命令。

### 7.3 自包含脚本

当你需要可复用逻辑时，在 `scripts/` 中捆绑一个内联声明其自身依赖的脚本。智能体可以用单个命令运行脚本——不需要单独的清单文件或安装步骤。

#### Python（PEP 723）

[PEP 723](https://peps.python.org/pep-0723/) 定义了内联脚本元数据的标准格式。在 `# ///` 标记内的 TOML 块中声明依赖：

`scripts/extract.py`：
```python
# /// script
# dependencies = [
#   "beautifulsoup4>=4.12,<5",
# ]
# requires-python = ">=3.11"
# ///

from bs4 import BeautifulSoup

html = '<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>'
print(BeautifulSoup(html, "html.parser").select_one("p.info").get_text())
```

使用 [uv](https://docs.astral.sh/uv/) 运行（推荐）：
```bash
uv run scripts/extract.py
```

#### Deno

Deno 的 `npm:` 和 `jsr:` 导入说明符默认使每个脚本自包含：

`scripts/extract.ts`：
```typescript
#!/usr/bin/env -S deno run

import * as cheerio from "npm:cheerio@1.0.0";

const html = `<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>`;
const $ = cheerio.load(html);
console.log($("p.info").text());
```

```bash
deno run scripts/extract.ts
```

#### Bun

当找不到 `node_modules` 目录时，Bun 在运行时自动安装缺失的包。直接在导入路径中固定版本：

`scripts/extract.ts`：
```typescript
#!/usr/bin/env bun

import * as cheerio from "cheerio@1.0.0";

const html = `<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>`;
const $ = cheerio.load(html);
console.log($("p.info").text());
```

```bash
bun run scripts/extract.ts
```

#### Ruby（Bundler Inline）

Ruby 2.6+ 内置 Bundler，使用 `bundler/inline` 直接在脚本中声明 gems：

`scripts/extract.rb`：
```ruby
require 'bundler/inline'

gemfile do
  source 'https://rubygems.org'
  gem 'nokogiri', '~> 1.16'
end

html = '<html><body><h1>Welcome</h1><p class="info">This is a test.</p></body></html>'
doc = Nokogiri::HTML(html)
puts doc.at_css('p.info').text
```

```bash
ruby scripts/extract.rb
```

> **注意**：显式固定版本（`gem 'nokogiri', '~> 1.16'`）——没有锁文件。工作目录中现有的 `Gemfile` 或 `BUNDLE_GEMFILE` 环境变量可能会干扰。

### 7.4 面向智能体的脚本设计原则

当智能体运行你的脚本时，它读取 stdout 和 stderr 来决定下一步做什么。一些设计选择使脚本对于智能体来说显著更容易使用。

#### 避免交互式提示（硬要求）
这是智能体执行环境的硬要求。智能体在非交互式 shell 中运行——它们无法响应 TTY 提示、密码对话框或确认菜单。阻塞在交互式输入上的脚本将无限期挂起。

通过命令行标志、环境变量或 stdin 接受所有输入：

```bash
# 错误：挂起等待输入
$ python scripts/deploy.py
Target environment: _

# 正确：清晰错误带指导
$ python scripts/deploy.py
Error: --env is required. Options: development, staging, production.
Usage: python scripts/deploy.py --env staging --tag v1.2.3
```

#### 用 `--help` 文档化用法
`--help` 输出是智能体了解脚本接口的主要方式。包括简要描述、可用标志和使用示例：

```
Usage: scripts/process.py [OPTIONS] INPUT_FILE

Process input data and produce a summary report.

Options:
  --format FORMAT   Output format: json, csv, table (default: json)
  --output FILE     Write output to FILE instead of stdout
  --verbose         Print progress to stderr

Examples:
  scripts/process.py data.csv
  scripts/process.py --format csv --output report.csv data.csv
```

保持简洁——输出与智能体正在处理的其他所有内容一起进入其上下文窗口。

#### 编写有用的错误消息
当智能体收到错误时，消息直接塑造其下一次尝试。不透明的"错误：无效输入"浪费一轮。相反，说明哪里错了、期望什么、尝试什么：

```
Error: --format must be one of: json, csv, table.
  Received: "xml"
```

#### 使用结构化输出
优先使用结构化格式——JSON、CSV、TSV——而非自由格式文本。结构化格式可以被智能体和标准工具（`jq`、`cut`、`awk`）消费，使你的脚本可在管道中组合。

```
# 空白对齐——难以编程解析
NAME        STATUS    CREATED
my-service  running   2025-01-15

# 分隔——明确的字段边界
{"name": "my-service", "status": "running", "created": "2025-01-15"}
```

**分离数据和诊断**：将结构化数据发送到 stdout，将进度消息、警告和其他诊断发送到 stderr。这让智能体捕获干净、可解析的输出，同时在需要时仍能访问诊断信息。

#### 其他考虑因素

| 原则 | 说明 |
|------|------|
| **幂等性** | 智能体可能重试命令。"不存在则创建"比"创建并在重复时失败"更安全 |
| **输入约束** | 用清晰错误拒绝模糊输入，而不是猜测。尽可能使用枚举和闭集 |
| **Dry-run 支持** | 对于破坏性或有状态操作，`--dry-run` 标志让智能体预览将发生什么 |
| **有意义的退出码** | 为不同失败类型使用不同的退出码（未找到、无效参数、认证失败），并在 `--help` 中记录 |
| **安全默认值** | 考虑破坏性操作是否需要显式确认标志（`--confirm`、`--force`） |
| **可预测的输出大小** | 许多智能体工具自动截断超过阈值（例如 10-30K 字符）的工具输出，可能丢失关键信息 |
