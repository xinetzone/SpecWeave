---
id: "rules-alt-env-vars"
title: "02 环境变量"
source: "alternatives-guide.md#env-vars"
x-toml-ref: "../../../.meta/toml/.agents/rules/alternatives-guide/02-env-vars.toml"
---
# 02 环境变量


## 适用场景

敏感信息（`API_KEY`、`SECRET`、`PASSWORD`）、部署环境差异参数、第三方服务凭据，以及需在运行时注入且不能写入配置文件的任何数据。

## 实施步骤

1. 定义环境变量命名规范：`{APP}_{SECTION}_{KEY}` 全大写、下划线分隔。
2. 编写 `.env.example` 模板文件，标注每个变量的用途与默认值。
3. 实现环境变量读取与校验模块，启动时检查必填变量是否存在。
4. 确保 `.env`（含敏感信息的实际文件）已加入 `.gitignore`，仅提交 `.env.example`。

## 示例代码

**`.env.example`**

```ini
# ── 应用配置 ──
APP_ENV=development
APP_DEBUG=true

# ── 数据库 ──
APP_DATABASE_HOST=localhost
APP_DATABASE_PORT=5432
APP_DATABASE_NAME=app_db
APP_DATABASE_USER=app_user
APP_DATABASE_PASSWORD=your_password_here

# ── 第三方密钥（敏感信息） ──
APP_PAYMENT_API_KEY=sk_live_xxxxxxxxxxxxxxxxxxxx
APP_PAYMENT_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxx

# ── Redis ──
APP_REDIS_URL=redis://localhost:6379/0
```

**`config/env_reader.py`**

```python
"""环境变量读取与校验模块。"""

import os
import sys
from typing import Any

# 可以通过 python-dotenv 加载 .env 文件（开发环境）
# from dotenv import load_dotenv
# load_dotenv()


_required_vars: list[tuple[str, type | None]] = [
    ("APP_DATABASE_HOST", str),
    ("APP_DATABASE_PORT", int),
    ("APP_DATABASE_NAME", str),
    ("APP_DATABASE_USER", str),
    ("APP_DATABASE_PASSWORD", str),
    ("APP_PAYMENT_API_KEY", str),
]

_optional_vars: dict[str, Any] = {
    "APP_ENV": "development",
    "APP_DEBUG": "false",
    "APP_REDIS_URL": "redis://localhost:6379/0",
    "APP_DATABASE_PORT": "5432",
}


def _validate() -> None:
    """校验必填环境变量是否存在，并将可选变量填充默认值。"""
    missing: list[str] = []
    for var_name, expected_type in _required_vars:
        value = os.getenv(var_name)
        if not value:
            missing.append(var_name)
            continue
        if expected_type and expected_type is not str:
            try:
                expected_type(value)
            except (ValueError, TypeError):
                print(
                    f"[CONFIG] 环境变量 {var_name}={value!r} 类型不匹配，"
                    f"期望 {expected_type.__name__}",
                    file=sys.stderr,
                )

    for var_name, default in _optional_vars.items():
        if var_name not in os.environ:
            os.environ[var_name] = str(default)

    if missing:
        print(
            f"[CONFIG] 缺少必要环境变量: {', '.join(missing)}\n"
            f"请参考 .env.example 配置后重新启动。",
            file=sys.stderr,
        )
        sys.exit(1)


def get_env(key: str, default: str | None = None) -> str:
    """读取环境变量，未设置时返回默认值。"""
    return os.getenv(key, default)


def get_env_int(key: str, default: int = 0) -> int:
    """读取整型环境变量。"""
    return int(os.getenv(key, str(default)))


def get_env_bool(key: str, default: bool = False) -> bool:
    """读取布尔型环境变量。"""
    return os.getenv(key, str(default).lower()) in ("true", "1", "yes")


# 模块加载时自动校验
_validate()
```

**`.gitignore` 追加项**

```gitignore
# 环境变量敏感文件
.env
.env.local
.env.*.local
```
---

## 相关模式

- [硬编码治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/)
- [三级问题解决](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)
- [检查与恢复模式](../../docs/retrospective/patterns/code-patterns/check-and-restore.md)
---

← 上一章: [01 配置文件管理](01-config-files.md) | **[返回索引](../alternatives-guide.md)** | 下一章: [03 常量定义与枚举](03-constants-enums.md) →
