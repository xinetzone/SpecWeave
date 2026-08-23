---
type: Concept
title: Skill 脚本工具模式（Python/Shell）
description: Agent Skill 中可执行脚本的设计模式，PEP 723 内联依赖、click CLI 框架、统一输出契约、共享库导入、Shell 脚本最佳实践
tags: [agent-skills, scripts, python, shell, pep723, click, cli]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: jira-skill-source
    resource: "/references/jira-skill-source.md"
    title: jira-skill 源码
  - id: retro-skill-source
    resource: "/references/retro-skill-source.md"
    title: retro-skill 源码
  - id: awesun-skill-source
    resource: "/references/awesun-skill-source.md"
    title: awesun-skill 源码
  - id: awesun-ui-locator-source
    resource: "/references/awesun-ui-locator-source.md"
    title: awesun-ui-locator 源码
---

# Skill 脚本工具模式（Python/Shell）

Agent Skill 中的 scripts/ 目录存放可执行脚本，是 Skill 从"知识包"升级为"可操作能力"的关键。本概念从六个项目的实践中提炼脚本工具的设计模式：PEP 723 内联依赖、统一 CLI 契约、共享库组织、Shell 脚本无依赖原则、异步执行器模式和参数设计。

## 脚本的角色定位

在渐进式披露三层结构中，scripts/ 属于第三层：

| 层级 | 内容 | AI 交互方式 |
|------|------|------------|
| SKILL.md 正文 | 何时调用脚本、脚本功能描述、参数说明 | AI 阅读后决定调用 |
| scripts/ 源码 | 具体实现逻辑 | AI 需要理解行为时读取，需要执行时调用 |
| scripts/ 执行 | 命令行调用 | AI 通过 Bash 工具执行 |

SKILL.md 不应重复脚本内部实现，只需描述"何时用"和"怎么传参"。

## PEP 723 内联依赖（Python）

jira-skill 展示了 PEP 723 的最佳实践。每个核心脚本在文件头部声明内联元数据：

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "atlassian-python-api>=3.41.0,<4",
#     "click>=8.1.0,<9",
# ]
# ///
"""Jira issue operations - get, update, and delete issue details."""
```

### 关键要素

1. **shebang**：`#!/usr/bin/env -S uv run --script` 使脚本可直接执行，uv 自动创建隔离环境
2. **requires-python**：声明最低 Python 版本
3. **dependencies**：内联依赖列表，无需 requirements.txt 或 pyproject.toml
4. **版本固定**：使用 `>=x.y,<major+1` 约束，避免主版本升级引入破坏性变更

### 适用场景

PEP 723 适合"单文件可分发"的脚本。当脚本数量多且共享代码时（如 jira-skill 的 21 个脚本共享 lib/），仍通过 PYTHONPATH 导入共享模块，但每个入口脚本保持 PEP 723 头。

### 与传统虚拟环境的对比

| 维度 | PEP 723 + uv | 传统 venv + requirements.txt |
|------|-------------|---------------------------|
| 安装步骤 | 零（首次运行自动安装） | 创建 venv、pip install |
| 可移植性 | 单文件包含所有依赖信息 | 需附带 requirements.txt |
| 隔离性 | uv 自动管理缓存环境 | 手动激活/切换 |
| 适用规模 | 中小型脚本 | 大型应用 |

## 统一 CLI 契约

jira-skill 的所有 21 个脚本遵循统一的命令行接口规范：

| 参数 | 类型 | 用途 |
|------|------|------|
| `--help` | flag | 自动生成帮助 |
| `--json` | flag | JSON 格式输出（机器可读） |
| `--quiet` | flag | 静默模式（仅关键信息/错误） |
| `--debug` | flag | 调试输出（详细日志） |
| `--dry-run` | flag | 破坏性操作预览（不实际执行） |

### 三种输出格式

同一命令支持三种输出，满足不同消费者：

- **默认（表格/人类可读）**：格式化表格、颜色、进度信息，适合人类用户
- `--json`：紧凑 JSON，适合 AI 解析和脚本链式调用
- `--quiet`：仅输出关键 ID 或错误信息，适合管道操作

lib/output.py 提供了统一的输出函数：
- `format_output(data, json_flag, quiet_flag)`：根据参数自动选择格式
- `success(msg)` / `warning(msg)` / `error(msg)`：语义化状态输出
- `compact_json(obj)`：最小化 JSON 序列化
- `extract_adf_text()`：从 Atlassian Document Format 提取纯文本

### --dry-run 保护

所有写操作（创建、更新、删除、转换）必须支持 `--dry-run`，显示将要执行的操作但不实际调用 API。这给 AI 和人类提供了安全预览机制。

## click 框架模式

jira-skill 使用 click 而非 argparse 构建 CLI：

```python
import click

@click.group()
@click.option("--json", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Quiet mode")
@click.option("--debug", is_flag=True, help="Debug output")
def cli(json, quiet, debug):
    """Jira issue operations."""
    pass

@cli.command()
@click.argument("issue_key")
def get(issue_key, **kwargs):
    """Get issue details."""
    ...

@cli.command()
@click.argument("issue_key")
@click.option("--dry-run", is_flag=True)
def update(issue_key, dry_run, **kwargs):
    """Update issue."""
    ...
```

click 的优势：
- 自动生成 `--help`（含子命令帮助）
- 子命令分组（`jira-issue.py get` / `jira-issue.py work` / `jira-issue.py qa`）
- 类型校验和参数转换
- 上下文对象在子命令间共享配置

## 共享库组织

jira-skill 的 `scripts/lib/` 目录展示了共享库的组织模式：

```text
scripts/
├── core/           # 入口脚本（PEP 723 头 + CLI 定义）
├── workflow/       # 入口脚本
├── utility/        # 入口脚本
└── lib/            # 共享库（无 PEP 723 头，被导入而非直接执行）
    ├── __init__.py
    ├── client.py   # API 客户端
    ├── config.py   # 配置管理
    ├── errors.py   # 异常定义
    ├── output.py   # 输出格式化
    ├── input.py    # 输入处理
    ├── users.py    # 用户相关
    ├── jql.py      # JQL 工具
    ├── markup.py   # Wiki 标记
    └── changelog.py # 变更日志分析
```

### PYTHONPATH 导入

入口脚本通过以下方式导入 lib：

```python
_script_dir = Path(__file__).parent
_lib_path = _script_dir.parent / "lib"
if _lib_path.exists():
    sys.path.insert(0, str(_lib_path.parent))

from lib.client import LazyJiraClient
from lib.output import format_output
```

这种模式避免了包安装，脚本可直接通过 uv run 执行，同时共享代码不重复。

### 库模块设计原则

- **client.py**：封装外部 API 交互，处理认证、重试、分页
- **config.py**：配置加载、环境变量、多 profile
- **errors.py**：领域异常（AuthenticationError、CaptchaError、SessionExpiredError）
- **output.py**：输出格式化，统一 JSON/表格/静默模式
- **纯函数优先**：如 changelog.py 的状态转换分析函数尽量无副作用，便于测试

## Shell 脚本的无依赖原则

agency-agents 的 Bash 脚本展示了 Shell 的最佳实践：

### lib.sh 共享库

`scripts/lib.sh` 是纯 Bash 共享库，兼容 Bash 3.2+（macOS 默认版本），无外部依赖：

```bash
get_field() { awk -F': ' ...; }
get_body() { awk '...'; }
slugify() { echo "$1" | tr '[:upper:]' '[:lower:]' | sed ...; }
agent_slug() { get_field name "$1" | slugify; }
is_agent_file() { head -1 "$1" | grep -q '^---'; }
```

### 无 jq 设计

check-divisions.sh 不依赖 jq 解析 JSON，而是使用 awk/grep/sed 从 divisions.json 提取部门名称：

```bash
canonical() {
    awk -F'"' '/^    "[a-z]/ {print $2}' divisions.json
}
```

这种设计确保脚本在 macOS 默认环境和 CI 的最小化 Linux 环境中都能运行，无需安装额外工具。

### 使用 git ls-files 而非 glob

```bash
actual_dirs() {
    git ls-files --directory --no-empty-directory \
        | awk -F/ '/\// {print $1}' \
        | sort -u
}
```

使用 `git ls-files` 而非文件系统 glob 的好处是：结果与 CI 的干净检出一致，不受本地构建产物、临时文件干扰。

## 异步执行器模式（Python asyncio）

awesun-skill 的 executor.py 展示了异步 MCP 客户端模式：

```python
class MCPExecutor:
    async def connect(self):
        self.exit_stack = AsyncExitStack()
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read_stream, write_stream = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self.session.initialize()

    async def close(self):
        if self.exit_stack:
            await self.exit_stack.aclose()
```

关键模式：
- **AsyncExitStack**：管理多个异步上下文资源的生命周期，确保逆序清理
- **可选依赖**：try/except ImportError + HAS_MCP 标志，使脚本在未安装 mcp 时仍可被读取
- **配置验证**：connect() 先验证必填字段（command、env），缺失时抛出 ValueError
- **CLI 包装**：asyncio.run(main()) 将异步逻辑包装为同步命令行入口

## 无依赖计算脚本

awesun-ui-locator 的 coordinate_utils.py 展示了最小化依赖模式：

```python
from typing import Tuple

def calculate_coordinates(
    pixel_x: int, pixel_y: int, image_width: int, image_height: int
) -> Tuple[float, float]:
    x = pixel_x / image_width
    y = pixel_y / image_height
    return (round(x, 6), round(y, 6))

def validate_coordinates(x: float, y: float) -> bool:
    return 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0

def format_coordinates(x: float, y: float) -> dict:
    return {"coordinates": {"x": x, "y": y}}
```

仅使用 `typing.Tuple`（标准库），无第三方依赖。这类纯计算函数：
- 可被 AI 直接在推理中复现
- 可通过任意 Python 3.7+ 环境执行
- 易于单元测试

## 信号检测脚本的注册模式

retro-skill 的 detect-mechanical.py 使用字典注册信号函数：

```python
SIGNAL_FUNCS = {
    "A1": signal_tool_errors,
    "A2": signal_retry_clusters,
    # ... 21 个信号
    "C6": signal_rule_exists_but_violated,
}
```

这种模式的优势：
- 通过 `--signals A1,A6,A14` 参数选择性运行信号
- 新增信号只需编写函数并添加到字典，无需修改主流程
- 每个信号有唯一 ID，便于追踪和测试
- 信号函数签名一致（接收事件/文本，返回发现列表）

## 参数设计最佳实践

综合各项目实践，Skill 脚本的参数设计应遵循：

1. **位置参数用于必填标识**：如 issue_key、remote_id、session_id
2. **选项用于可选配置**：如 `--json`、`--dry-run`、`--limit`
3. **破坏性操作需要显式确认**：`--yes` 或 `--dry-run` 默认
4. **环境变量用于敏感信息**：API token 通过环境变量传入，不做命令行参数（避免 ps 泄露）
5. **stdin 支持**：支持管道输入（jira-skill 的 `read_stdin_utf8()`），便于链式调用
6. **一致的命名**：所有脚本使用相同的参数名（`--json` 而非 `--format json`）

## 相关概念

- [SKILL.md 标准与渐进式披露](/concepts/01-skill-md-standard.md)
- [Jira Skill 工程化实践](/concepts/08-jira-skill-engineering.md)
- [Retro Skill 自省与演进模式](/concepts/09-retro-skill-introspection.md)
- [MCP 协议与工具集成](/concepts/04-mcp-protocol.md)
