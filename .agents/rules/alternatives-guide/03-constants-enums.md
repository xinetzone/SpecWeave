---
id: "rules-alt-constants-enums"
title: "03 常量定义与枚举"
source: "alternatives-guide.md#constants-enums"
x-toml-ref: "../../../.meta/toml/.agents/rules/alternatives-guide/03-constants-enums.toml"
---
# 03 常量定义与枚举


## 适用场景

业务常量（`HARD-NUM`）、状态码、类型标识、固定数值、有限枚举集合。

## 实施步骤

1. 创建 `constants/` 包，包含 `__init__.py`、`enums.py` 等模块。
2. 使用 Python `enum` 标准库定义枚举类型，保持类型安全。
3. 使用模块级变量定义不可变常量，统一管理而非散落各处。
4. 命名规范：全大写字母 + 下划线分隔（`UPPER_SNAKE_CASE`）。

## 示例代码

**`constants/enums.py`**

```python
"""项目枚举类型定义。"""

from enum import Enum, IntEnum, StrEnum


class OrderStatus(IntEnum):
    """订单状态枚举。"""
    PENDING = 0       # 待处理
    CONFIRMED = 1     # 已确认
    SHIPPED = 2       # 已发货
    DELIVERED = 3     # 已签收
    CANCELLED = 4     # 已取消
    REFUNDED = 5      # 已退款


class UserRole(StrEnum):
    """用户角色枚举。"""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"


class PaymentMethod(StrEnum):
    """支付方式枚举。"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    WECHAT_PAY = "wechat_pay"
    ALIPAY = "alipay"
    BANK_TRANSFER = "bank_transfer"


class Environment(StrEnum):
    """部署环境枚举。"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class HttpMethod(StrEnum):
    """HTTP 请求方法。"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
```

**`constants/__init__.py`**

```python
"""项目常量与枚举集中定义模块。"""

from .enums import (
    OrderStatus,
    UserRole,
    PaymentMethod,
    Environment,
    HttpMethod,
)

# ── 业务常量 ──
MAX_LOGIN_ATTEMPTS = 5
SESSION_TIMEOUT_SECONDS = 3600
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ── 数值边界 ──
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 32

# ── 时间相关 ──
TOKEN_EXPIRY_HOURS = 24
REFRESH_TOKEN_EXPIRY_DAYS = 30
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 100

# ── 编码常量 ──
DEFAULT_ENCODING = "utf-8"
JSON_CONTENT_TYPE = "application/json"
FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"

__all__ = [
    "OrderStatus",
    "UserRole",
    "PaymentMethod",
    "Environment",
    "HttpMethod",
    "MAX_LOGIN_ATTEMPTS",
    "SESSION_TIMEOUT_SECONDS",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
]
```

**使用示例**

```python
from constants import OrderStatus, MAX_LOGIN_ATTEMPTS

# 原有硬编码写法（禁止）：
#   if status == 4:
#       process_refund()

# 推荐写法：
if order.status == OrderStatus.CANCELLED:
    process_refund(order)

if login_attempts >= MAX_LOGIN_ATTEMPTS:
    lock_account(user_id)
```
---

## 相关模式

- [硬编码治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/)
- [三级问题解决](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)
- [检查与恢复模式](../../docs/retrospective/patterns/code-patterns/check-and-restore.md)
---

← 上一章: [02 环境变量](02-env-vars.md) | **[返回索引](../alternatives-guide.md)** | 下一章: [04 资源文件/消息字典](04-message-dictionary.md) →
