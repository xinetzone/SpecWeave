+++
id = "dual-channel-tiered-logging"
domain = "code"
layer = "code"
maturity = "L2"
validation_count = 1
reuse_count = 0
documentation_level = "detailed"
source = "forum-bot.py logging system"
+++

# 分级日志双轨输出模式

## 问题

自动化脚本的日志面临矛盾需求：
- 控制台需要简洁（避免刷屏影响操作体验）
- 排查问题时需要完整详细日志（DEBUG级全量信息）
- 静态资源等噪音日志会淹没关键信息

## 解决方案

Logger 始终设为 DEBUG 级，由 Handler 控制输出粒度——而非 Logger 过滤 Handler。控制台 Handler 设为 INFO 级，文件 Handler 设为 DEBUG 级，并对高频低价值日志（静态资源请求）进行过滤。

## 代码

```python
import logging
import sys
import time
from pathlib import Path

logger = logging.getLogger("my-tool")

def setup_logging(debug: bool = False) -> None:
    """初始化日志系统：控制台按级别过滤，文件始终记录DEBUG级。"""
    console_level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(logging.DEBUG)  # logger本身始终放行所有级别
    logger.handlers.clear()  # 防止重复添加handler

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-5s] %(message)s",
        datefmt="%H:%M:%S",
    )

    # 控制台Handler：按debug参数控制级别
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(console_level)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # 文件Handler：始终DEBUG级
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(
        log_dir / f"tool-{time.strftime('%Y%m%d')}.log",
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)-5s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(fh)
```

### 语义化日志辅助函数

```python
def step(msg: str) -> None:
    """步骤开始日志 — INFO级，始终可见"""
    logger.info("▸ %s", msg)

def gate_ok(msg: str) -> None:
    """门禁检查通过 — DEBUG级，仅文件/--debug可见"""
    logger.debug("  ✅ %s", msg)

def gate_fail(msg: str) -> None:
    """门禁检查失败 — WARNING级，始终可见"""
    logger.warning("  ❌ %s", msg)

def retry_log(attempt: int, max_attempts: int, action: str) -> None:
    """重试日志 — WARNING级"""
    logger.warning("  🔄 %s [%d/%d]", action, attempt, max_attempts)
```

### 静态资源日志过滤（浏览器自动化场景）

```python
def _attach_network_logging(context) -> None:
    """为浏览器上下文附加网络请求日志（过滤静态资源）。"""
    def _should_log(url: str) -> bool:
        skip_ext = (".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg",
                    ".woff", ".woff2", ".ico", ".webp", ".map")
        return not any(url.split("?")[0].endswith(ext) for ext in skip_ext)

    context.on("request", lambda req: (
        logger.debug("  📤 %s %s", req.method, req.url[:120])
        if _should_log(req.url) else None
    ))
    context.on("response", lambda resp: (
        logger.debug("  📥 %d %s", resp.status, resp.url[:120])
        if resp.status >= 400 or _should_log(resp.url) else None
    ))
```

## 关键设计决策

1. **Logger级 vs Handler级**：Logger设为DEBUG、Handler过滤级别，确保FileHandler能收到所有级别消息。反之则FileHandler永远收不到DEBUG。
2. **handlers.clear()**：防止setup_logging被多次调用时重复添加Handler导致日志重复输出。
3. **语义化函数**：step/gate_ok/gate_fail/retry_log封装了日志级别和emoji，调用处语义清晰。
4. **噪音过滤**：4xx/5xx响应无论资源类型一律记录（可能指示CDN/权限问题），200的静态资源跳过。
5. **双时间格式**：控制台用简洁`%H:%M:%S`，文件用完整`%Y-%m-%d %H:%M:%S`便于事后追溯。

## 复用场景

任何需要"控制台简洁+文件详细"双轨输出的Python CLI工具，特别是：
- 浏览器自动化脚本（Playwright/Selenium）
- CI/CD工具脚本
- 数据处理ETL脚本
- 系统运维脚本

## 来源

[forum-bot.py](file:///d:/spaces/SpecWeave/.agents/scripts/forum-bot.py) — `setup_logging()` 及辅助函数

> **关联模式**：
> - [multi-signal-detection](../methodology-patterns/tools-automation/multi-signal-detection.md)
