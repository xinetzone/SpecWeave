---
id: "session-file-externalization"
source: "../../reports/competitive-analysis/retrospective-tuyaopen-dev-skills-learning-20260630/insight-extraction.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/session-file-externalization.toml"
---
# 会话外部化：用 session file 解耦多命令状态

## 模式概述

当一个工具以多个子命令形式提供能力（例如 `start/tail/stop/status`）时，常见的错误做法是把状态留在内存或依赖“同一个终端进程”。这会导致：

- 多终端/多进程协同时状态丢失
- 异常退出后无法恢复或清理
- 上层编排无法可靠读取当前状态

本模式将会话状态外部化为一个明确位置的 session file，使状态成为“可读、可恢复、可测试”的文件资产。

## 触发条件

- 子命令共享状态（PID、端口、日志文件、临时路径、上次运行时间等）
- 需要跨进程协同（start 与 tail/stop 不在同一进程）
- 希望在测试中可注入 session 目录与文件路径

## 设计约束

### 位置约束

session file 应位于“项目资产目录”下，避免污染全局：

```text
<project_dir>/.tool_state/session.json
```

### Schema 约束

建议字段（按需增减）：

```json
{
  "pid": 12345,
  "log_file": "path/to/log",
  "port": "COM3"
}
```

## 实现要点

- 写入前确保目录存在（`mkdir -p` 等价行为）
- 写入采用覆盖式更新，保证文件始终是完整 JSON
- 读取失败时按“无会话”处理，不做半解析
- `stop` 等破坏性操作必须先验证状态合法性（可结合进程身份校验模式）

## 最小代码片段（Python）

```python
import json
from pathlib import Path


def load_session(path: Path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_session(path: Path, session: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(session, ensure_ascii=False), encoding="utf-8")
```

## 测试建议

- session dir/file 作为可注入变量（便于 monkeypatch）
- 覆盖场景：
  - 无 session file
  - session file 内容损坏
  - stop 后 session file 被清理

