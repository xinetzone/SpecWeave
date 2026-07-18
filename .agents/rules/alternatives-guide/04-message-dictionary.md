---
id: "rules-alt-message-dictionary"
title: "04 资源文件/消息字典"
source: "alternatives-guide.md#message-dictionary"
x-toml-ref: "../../../.meta/toml/.agents/rules/alternatives-guide/04-message-dictionary.toml"
---
# 04 资源文件/消息字典


## 适用场景

错误信息、提示信息、日志模板、通知消息等文本类硬编码（`HARD-STR`）。

## 实施步骤

1. 创建 `messages/` 模块，存放消息字典。
2. 使用键值对定义所有消息模板，采用 `{param}` 语法标记可替换参数。
3. 代码中通过键引用消息，禁止直接内联字符串。
4. 消息键命名规范：`<模块>_<场景>_<含义>`，如 `ORDER_NOT_FOUND`。

## 示例代码

**`messages/error_messages.py`**

```python
"""错误消息与提示信息字典。

使用 KeyError 风格键命名，支持参数化占位符。
"""

ERROR_MESSAGES: dict[str, str] = {
    # ── 通用错误 ──
    "INTERNAL_ERROR": "服务器内部错误，请联系管理员。",
    "UNAUTHORIZED": "认证失败，请检查凭据后重试。",
    "FORBIDDEN": "没有权限执行此操作。",
    "NOT_FOUND": "请求的资源不存在。",
    "VALIDATION_ERROR": "请求参数校验失败：{detail}。",
    "RATE_LIMITED": "请求过于频繁，请在 {seconds} 秒后重试。",

    # ── 认证相关 ──
    "LOGIN_FAILED": "用户名或密码错误，剩余尝试次数：{attempts}。",
    "ACCOUNT_LOCKED": "账户已被锁定，请于 {unlock_time} 后重试或联系管理员。",
    "TOKEN_EXPIRED": "登录已过期，请重新登录。",
    "PASSWORD_TOO_WEAK": "密码强度不足，需至少包含 {min_length} 个字符。",

    # ── 订单相关 ──
    "ORDER_NOT_FOUND": "订单 {order_id} 不存在或已被删除。",
    "ORDER_STATUS_INVALID": "订单状态不允许此操作，当前状态：{current}。",
    "INSUFFICIENT_STOCK": "商品 {product_name} 库存不足，剩余 {stock} 件。",

    # ── 文件处理 ──
    "FILE_TOO_LARGE": "文件大小超过限制，最大允许 {max_size_mb} MB。",
    "FILE_TYPE_UNSUPPORTED": "不支持的文件类型：{file_type}，允许的类型：{allowed}。",
    "FILE_UPLOAD_FAILED": "文件上传失败：{reason}。",
}


def get_error(key: str, **kwargs: object) -> str:
    """获取参数化错误消息。

    Args:
        key: 消息键。
        **kwargs: 用于填充消息模板中 {param} 占位符的值。

    Returns:
        格式化后的错误消息字符串。

    Raises:
        KeyError: 当指定的 key 在消息字典中不存在时。
    """
    template = ERROR_MESSAGES[key]
    if kwargs:
        return template.format(**kwargs)
    return template
```

**`messages/__init__.py`**

```python
from .error_messages import ERROR_MESSAGES, get_error

__all__ = ["ERROR_MESSAGES", "get_error"]
```

**使用示例**

```python
from messages import get_error

# 原有硬编码写法（禁止）：
#   raise ValueError(f"订单 {order_id} 不存在或已被删除。")

# 推荐写法：
raise ValueError(get_error("ORDER_NOT_FOUND", order_id=order_id))

# 参数化消息：
msg = get_error(
    "FILE_TOO_LARGE",
    max_size_mb=10,
)
```
---

## 相关模式

- [硬编码治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/README.md)
- [三级问题解决](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)
- [检查与恢复模式](../../docs/retrospective/patterns/code-patterns/check-and-restore.md)
---

← 上一章: [03 常量定义与枚举](03-constants-enums.md) | **[返回索引](../alternatives-guide.md)** | 下一章: [05 国际化资源文件](05-i18n.md) →
