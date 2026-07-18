---
id: mdi-toolchain-guide
title: MDI研究报告 - 工具链使用指南
source: "mdi-research-report.md#5-工具链使用指南"
x-toml-ref: "../../../../.meta/toml/.agents/docs/knowledge/mdi-research/04-toolchain-guide.toml"
---
# 工具链使用指南

## 快速开始

### 环境要求

- Python 3.10+
- pip或conda包管理器

### 安装（作为项目脚本）

MDI目前作为SpecWeave项目的内置脚本工具，位于`.agents/scripts/mdi/`目录，无需独立安装。通过Python模块方式调用：

```bash
cd .agents/scripts
python -m mdi --help
```

### 第一个MDI文档

创建一个最小的MDI文档（如`hello-api.md`）：

```markdown
---
name: hello-api
version: "1.0.0"
description: A simple Hello World API
type: webapi
baseUrl: https://api.example.com
---

# Hello API

Simple greeting API.

## Endpoints

```{endpoint} GET /hello
:summary: Greet the user
:query name: string? - Your name
:response 200: Greeting - Success response
```
```

### 验证文档

```bash
python -m mdi validate hello-api.md
```

预期输出：
```
  [PASS] hello-api.md  (95分, profile=webapi)
  ✅ 无任何问题
```

### 生成代码

生成Python类型定义：
```bash
python -m mdi gen hello-api.md -l python -o ./output
```

生成pytest测试骨架：
```bash
python -m mdi gen hello-api.md -l pytest -o ./tests
```

生成OpenAPI 3.0规范：
```bash
python -m mdi gen hello-api.md -l openapi -o ./openapi
```

## CLI命令参考

### validate命令 - 验证MDI文档

```bash
python -m mdi validate <path> [options]
```

**参数**：
- `path`：MDI文件或目录路径

**选项**：
- `--profile {auto,skill,webapi,clitool}`：指定Profile类型（默认auto自动检测）
- `--threshold <int>`：分数阈值，低于此值返回非零退出码（默认70）
- `--score`：仅输出分数（适合CI脚本）
- `--json`：JSON格式输出
- `--verbose/-v`：显示详细警告和信息
- `--help`：显示帮助

**示例**：
```bash
# 验证单个文件
python -m mdi validate examples/user-api.md

# 批量验证目录
python -m mdi validate .agents/skills/ --score

# JSON输出用于CI集成
python -m mdi validate api.md --json
```

### gen命令 - 生成代码/文档

```bash
python -m mdi gen <path> [options]
```

**参数**：
- `path`：MDI文件或目录路径

**选项**：
- `-l, --lang <language>`：目标语言/格式
  - `python`：Python TypedDict类型定义
  - `typescript`：TypeScript interface类型
  - `openapi`：OpenAPI 3.0 JSON规范
  - `mcp`：MCP Tool JSON Schema
  - `markdown`：人类友好Markdown文档
  - `cli`：Python Click CLI骨架
  - `pytest`：pytest测试骨架
  - `jest`：Jest测试骨架
- `-o, --output <dir>`：输出目录（默认`./output`）
- `-t, --template-dir <dir>`：自定义模板目录（暂未使用）

**示例**：
```bash
# 生成Python类型
python -m mdi gen user-api.md -l python -o ./src/types

# 生成pytest测试
python -m mdi gen user-api.md -l pytest -o ./tests

# 生成OpenAPI规范
python -m mdi gen user-api.md -l openapi -o ./openapi
```

### diff命令 - 版本对比

```bash
python -m mdi diff <old> <new> [options]
```

**参数**：
- `old`：旧版本MDI文件路径
- `new`：新版本MDI文件路径

**选项**：
- `--bump`：显示语义化版本升级建议
- `--json`：JSON格式输出
- `--verbose/-v`：显示详细字段级变更

**示例**：
```bash
# 文本格式对比+版本建议
python -m mdi diff v1.md v2.md --bump

# JSON格式输出
python -m mdi diff v1.md v2.md --json
```

## Python API参考

### 核心API

```python
from pathlib import Path
import mdi

# 1. 解析MDI文档
doc = mdi.parse("api.md")
print(f"文档标题: {doc.title}")
print(f"接口数量: {len(doc.interfaces)}")
for iface in doc.interfaces:
    print(f"  {iface.method} {iface.path}: {iface.summary}")

# 2. 验证文档
report = mdi.validate("api.md")
print(f"验证分数: {report.score}")
if not report.passed():
    for err in report.errors():
        print(f"ERROR {err.code}: {err.message}")

# 3. 生成代码
files = mdi.generate("api.md", lang="python", output_dir="./output")
for f in files:
    print(f"生成: {f}")

# 4. 版本对比
diff = mdi.diff_files("v1.md", "v2.md")
print(diff.format_text(verbose=True))
print(f"建议版本: {diff.suggest_version_bump()}")
print(f"整体严重性: {diff.overall_severity().value}")
```

### 数据模型

```python
from mdi import MDIDocument, Interface, Parameter, Response, ErrorCode

# MDIDocument - 文档根对象
doc = MDIDocument(
    frontmatter={"name": "my-api", "version": "1.0.0"},
    title="My API",
    interfaces=[...],  # List[Interface]
)

# Interface - 接口定义
iface = Interface(
    name="get_user",
    method="GET",
    path="/users/{id}",
    summary="Get user by ID",
    parameters=[...],  # List[Parameter]
    responses=[...],   # List[Response]
    errors=[...],      # List[ErrorCode]
)

# Parameter - 参数定义
param = Parameter(
    name="id",
    type="string",
    required=True,
    location="path",  # path/query/body/header/arg/flag/option
    description="User unique identifier",
)
```

### 版本管理API

```python
import mdi
from mdi import ChangeSeverity

# 对比两个文档对象
old_doc = mdi.parse("v1.md")
new_doc = mdi.parse("v2.md")
diff = mdi.diff_documents(old_doc, new_doc)

# 检查是否有变更
if diff.has_changes:
    # 获取结构化变更
    print(f"新增接口: {len(diff.added_interfaces)}")
    print(f"删除接口: {len(diff.removed_interfaces)}")
    print(f"修改接口: {len(diff.interface_changes)}")

    # 影响分析
    impacts = diff.impact_analysis()
    for product, details in impacts.items():
        print(f"\n{product}:")
        for d in details:
            print(f"  - {d}")

    # 版本建议
    from mdi.versioning import get_version_bump_recommendation
    rec = get_version_bump_recommendation(diff)
    print(f"\n建议从 {rec['current_version']} 升级到 {rec['suggested_version']}")
    print(f"升级类型: {rec['bump_type'].upper()}")
    print(f"破坏性变更: {'是' if rec['has_breaking_changes'] else '否'}")
```

## 三种Profile使用指南

### Skill Profile（AI Agent Skill）

适用于AI Agent技能文档，兼容现有14个SKILL.md：

```markdown
---
name: my-skill
version: "1.0.0"
description: "触发词1、触发词2：这是一个AI Skill"
type: skill
---

# Skill Name

## Description
详细描述...

## Usage
如何使用这个技能...
```

### WebAPI Profile（RESTful API）

适用于HTTP RESTful API定义：

```markdown
---
name: user-api
version: "1.0.0"
description: "用户管理API"
type: webapi
baseUrl: https://api.example.com/v1
---

# User API

## Interfaces

### Get User

```{endpoint} GET /users/{id}
:summary: Get user details
:path id: string - User ID
:response 200: User - User object
:error 404: NotFound - User not found
```
```

### CLI Tool Profile（命令行工具）

适用于CLI命令行工具定义：

```markdown
---
name: file-tool
version: "1.0.0"
description: "文件操作CLI工具"
type: clitool
argument-hint: "[command] [options] [arguments]"
---

# File Tool

## Commands

```{command} copy <source> <destination>
:summary: Copy a file
:arg source: string - Source file path
:arg destination: string - Destination file path
:flag --recursive,-r: boolean - Copy directories recursively (default: false)
:flag --preserve: boolean - Preserve file attributes (default: true)
:exit 0: Success
:exit 1: Error occurred
```
```

---

**下一步阅读**：
- [版本控制与变更管理最佳实践](05-versioning-best-practices.md) - SemVer规范、变更严重性判定、推荐工作流
- [返回技术架构](03-technical-architecture.md)
- [返回索引](../mdi-research-report.md)
