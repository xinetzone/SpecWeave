---
id: "rules-alternatives-guide"
title: "替代方案指南"
source: "AGENTS.md#规则体系"
x-toml-ref: "../../.meta/toml/.agents/rules/alternatives-guide.toml"
---
# 替代方案指南

本指南是硬编码治理规则体系的核心文档，针对每种硬编码类型提供推荐的替代方案与具体实施步骤。遵循本指南可有效消除代码中的硬编码问题，提升项目的可维护性、可配置性与可移植性。

## 规范说明

硬编码（Hardcoding）是指在源代码中直接写入具体数值、字符串或配置信息，而非通过外部化方式引用。硬编码会导致以下问题：

- **可维护性下降**：修改一个配置值需要改动多处代码并重新编译部署。
- **可移植性不足**：环境差异（开发、测试、生产）无法通过统一机制切换。
- **安全风险**：敏感信息（密钥、密码）嵌入代码，容易泄露至版本控制系统。
- **国际化困难**：UI 文本与业务逻辑耦合，无法支持多语言。

本指南为每种硬编码类型提供标准化的替代方案，遵循"先识别、后迁移、新代码零容忍"的治理原则。

## 类型与替代方案映射表

| 硬编码类型 | 类型标识 | 典型表现 | 推荐替代方案 | 优先级 |
|---|---|---|---|---|
| 配置参数 | `HARD-CFG` | 超时时间、重试次数、缓存大小、开关阈值等以字面量写入代码 | 配置文件（YAML/JSON/TOML）+ 环境变量覆盖 | P0 |
| 业务常量 | `HARD-NUM` | 状态码、类型标识、费率、比例等固定数值散落各处 | 常量类/枚举定义 | P0 |
| URL/端点 | `HARD-URL` | API 地址、服务端点、第三方回调 URL 直接写在请求代码中 | 配置文件 + 环境变量 | P0 |
| 路径 | `HARD-PATH` | 文件路径、目录路径以字符串字面量出现在代码中 | 路径常量集中管理 | P1 |
| 错误/提示信息 | `HARD-STR` | 异常消息、日志模板、用户提示以字符串直接内联 | 资源文件/消息字典（支持国际化） | P1 |
| UI 文本 | `HARD-STR` | 按钮文案、标签文本、占位符等直接写在 UI 模板中 | 国际化资源文件（i18n） | P2 |
| 正则模式 | `HARD-REGEX` | 正则表达式字面量散落在验证函数中 | 模式常量库 | P2 |
| 颜色/样式 | `HARD-STYLE` | CSS 色值、字体大小、间距数值直接写在样式定义中 | 主题变量/设计令牌（Design Tokens） | P2 |
| 编码值 | `HARD-ENC` | 字符编码名称（如 `"utf-8"`）、MIME 类型、协议常量以字符串出现 | 常量定义（引用标准） | P2 |

## 各替代方案详细实施指南

### 3.1 配置文件管理（YAML/JSON/TOML）

#### 适用场景

配置参数（`HARD-CFG`）、URL/端点（`HARD-URL`）、功能开关、阈值参数、第三方服务配置。

#### 实施步骤

1. 在项目 `config/` 目录下创建配置文件，推荐使用 YAML 格式（可读性优于 JSON，生态成熟）。
2. 定义配置结构，按模块或功能域分层组织，每层对应一个配置节。
3. 编写配置加载器，负责读取解析配置文件并合并多层级源。
4. 实现环境变量覆盖机制，优先级为：**环境变量 > 配置文件 > 默认值**。
5. 在代码中仅通过配置加载器获取配置，杜绝直接字面量。

#### 示例代码

**`config/default.yaml`**

```yaml
# 服务配置
server:
  host: "0.0.0.0"
  port: 8080
  debug: false

# 数据库配置
database:
  driver: "postgresql"
  host: "localhost"
  port: 5432
  name: "app_db"
  pool:
    min_size: 5
    max_size: 20
    timeout_ms: 30000

# 第三方服务
services:
  payment:
    base_url: "https://api.payment.example.com"
    timeout_ms: 10000
    retry: 3

# 功能开关
features:
  new_checkout_flow: false
  experimental_search: false
```

**`config/config_loader.py`**

```python
"""配置加载器：支持 YAML 配置文件读取与环境变量覆盖。"""

import os
import yaml
from typing import Any


class ConfigLoader:
    """读取配置文件并以环境变量覆盖对应值。

    环境变量命名规范：APP_<SECTION>_<KEY>
    示例：APP_DATABASE_HOST=prod-db.example.com
    分隔符 `.` 替换为 `_`，全大写。
    """

    def __init__(self, config_dir: str = "config", env: str | None = None):
        self.config_dir = config_dir
        self.env = env or os.getenv("APP_ENV", "development")
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        # 1. 加载默认配置
        default_path = os.path.join(self.config_dir, "default.yaml")
        with open(default_path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f) or {}

        # 2. 合并环境特定配置（可选）
        env_path = os.path.join(self.config_dir, f"{self.env}.yaml")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                env_data = yaml.safe_load(f) or {}
                self._deep_merge(self._data, env_data)

        # 3. 环境变量覆盖（最高优先级）
        self._apply_env_overrides(self._data)

    def _apply_env_overrides(self, data: dict, prefix: str = "APP") -> None:
        """递归遍历配置字典，以 APP_SECTION_KEY 覆盖对应值。"""
        for key, value in data.items():
            env_key = f"{prefix}_{key.upper()}"
            if isinstance(value, dict):
                self._apply_env_overrides(value, prefix=env_key)
            else:
                if env_key in os.environ:
                    raw = os.environ[env_key]
                    # 尝试类型转换（保持与 YAML 解析值的类型一致）
                    data[key] = self._coerce(raw, value)

    @staticmethod
    def _coerce(raw: str, reference: Any) -> Any:
        """根据参考值类型对环境变量字符串做类型转换。"""
        if isinstance(reference, bool):
            return raw.lower() in ("true", "1", "yes")
        if isinstance(reference, int):
            return int(raw)
        if isinstance(reference, float):
            return float(raw)
        return raw

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> None:
        """深度合并字典，override 中的值覆盖 base 中的同名字段。"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ConfigLoader._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """通过点分隔路径获取配置值。"""
        keys = key_path.split(".")
        node = self._data
        for k in keys:
            if isinstance(node, dict):
                node = node.get(k)
                if node is None:
                    return default
            else:
                return default
        return node

    @property
    def data(self) -> dict[str, Any]:
        """返回完整的配置字典（只读）。"""
        return dict(self._data)


# 全局单例
config = ConfigLoader()
```

**使用示例**

```python
from config.config_loader import config

# 原有硬编码写法（禁止）：
#   timeout = 10
#   db_url = "postgresql://localhost:5432/app_db"

# 推荐写法：
timeout = config.get("services.payment.timeout_ms", default=10000)
db_host = config.get("database.host")
debug = config.get("server.debug", default=False)

if config.get("features.new_checkout_flow"):
    use_new_checkout()
```

---

### 3.2 环境变量

#### 适用场景

敏感信息（`API_KEY`、`SECRET`、`PASSWORD`）、部署环境差异参数、第三方服务凭据，以及需在运行时注入且不能写入配置文件的任何数据。

#### 实施步骤

1. 定义环境变量命名规范：`{APP}_{SECTION}_{KEY}` 全大写、下划线分隔。
2. 编写 `.env.example` 模板文件，标注每个变量的用途与默认值。
3. 实现环境变量读取与校验模块，启动时检查必填变量是否存在。
4. 确保 `.env`（含敏感信息的实际文件）已加入 `.gitignore`，仅提交 `.env.example`。

#### 示例代码

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

### 3.3 常量定义与枚举

#### 适用场景

业务常量（`HARD-NUM`）、状态码、类型标识、固定数值、有限枚举集合。

#### 实施步骤

1. 创建 `constants/` 包，包含 `__init__.py`、`enums.py` 等模块。
2. 使用 Python `enum` 标准库定义枚举类型，保持类型安全。
3. 使用模块级变量定义不可变常量，统一管理而非散落各处。
4. 命名规范：全大写字母 + 下划线分隔（`UPPER_SNAKE_CASE`）。

#### 示例代码

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

### 3.4 资源文件/消息字典

#### 适用场景

错误信息、提示信息、日志模板、通知消息等文本类硬编码（`HARD-STR`）。

#### 实施步骤

1. 创建 `messages/` 模块，存放消息字典。
2. 使用键值对定义所有消息模板，采用 `{param}` 语法标记可替换参数。
3. 代码中通过键引用消息，禁止直接内联字符串。
4. 消息键命名规范：`<模块>_<场景>_<含义>`，如 `ORDER_NOT_FOUND`。

#### 示例代码

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

### 3.5 国际化资源文件

#### 适用场景

面向用户的 UI 文本（按钮、标签、提示）、页面内容、邮件模板等需要支持多语言的所有字符串。

#### 实施步骤

1. 创建 `locales/` 目录，按语言代码创建子目录（如 `zh_CN/`、`en/`）。
2. 实现轻量 i18n 模块，支持按语言加载翻译文件并支持嵌套键。
3. 在代码中标记所有可翻译字符串，通过 `_()` 或 `t()` 函数引用。
4. 提供翻译模板文件（`.pot` 格式），便于翻译协作。

#### 示例代码

**`locales/zh_CN/messages.py`**

```python
"""简体中文语言包。"""

translations: dict[str, str] = {
    # 通用
    "common.ok": "确定",
    "common.cancel": "取消",
    "common.save": "保存",
    "common.delete": "删除",
    "common.search": "搜索",
    "common.loading": "加载中...",
    "common.no_data": "暂无数据",
    "common.confirm_delete": "确认删除 {item}？此操作不可撤销。",

    # 登录页
    "login.title": "用户登录",
    "login.username": "用户名",
    "login.password": "密码",
    "login.submit": "登录",
    "login.forgot_password": "忘记密码？",
    "login.register": "没有账户？立即注册",

    # 导航
    "nav.home": "首页",
    "nav.orders": "我的订单",
    "nav.settings": "设置",
    "nav.logout": "退出登录",

    # 订单
    "order.title": "订单详情",
    "order.status_pending": "待处理",
    "order.status_confirmed": "已确认",
    "order.status_shipped": "已发货",
    "order.status_delivered": "已签收",
}
```

**`locales/en/messages.py`**

```python
"""English language pack."""

translations: dict[str, str] = {
    # Common
    "common.ok": "OK",
    "common.cancel": "Cancel",
    "common.save": "Save",
    "common.delete": "Delete",
    "common.search": "Search",
    "common.loading": "Loading...",
    "common.no_data": "No data available",
    "common.confirm_delete": "Confirm deletion of {item}? This action cannot be undone.",

    # Login
    "login.title": "Login",
    "login.username": "Username",
    "login.password": "Password",
    "login.submit": "Sign In",
    "login.forgot_password": "Forgot password?",
    "login.register": "Don't have an account? Register",

    # Navigation
    "nav.home": "Home",
    "nav.orders": "My Orders",
    "nav.settings": "Settings",
    "nav.logout": "Sign Out",

    # Orders
    "order.title": "Order Details",
    "order.status_pending": "Pending",
    "order.status_confirmed": "Confirmed",
    "order.status_shipped": "Shipped",
    "order.status_delivered": "Delivered",
}
```

**`i18n/__init__.py`**

```python
"""国际化（i18n）模块。

根据当前语言设置加载对应的翻译字典，对外提供 _() 函数用于标记和获取翻译文本。
支持嵌套键（如 "common.ok"）和参数化占位符（{param}）。
"""

import importlib
import os
from typing import Any


class I18n:
    """国际化翻译管理器。"""

    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = locales_dir
        self._translations: dict[str, str] = {}
        self._current_lang = "zh_CN"
        self.load(self._current_lang)

    def load(self, lang: str) -> None:
        """加载指定语言的翻译文件。"""
        try:
            module_path = f"{self.locales_dir}.{lang}.messages"
            module = importlib.import_module(module_path)
            self._translations = getattr(module, "translations", {})
            self._current_lang = lang
        except (ImportError, AttributeError):
            raise ImportError(
                f"无法加载语言包 '{lang}'。请确认 "
                f"{self.locales_dir}/{lang}/messages.py 存在且定义了 translations 字典。"
            )

    def set_language(self, lang: str) -> None:
        """切换当前语言。"""
        if lang != self._current_lang:
            self.load(lang)

    def t(self, key: str, **kwargs: Any) -> str:
        """获取翻译文本并填充占位符。

        若 key 未找到翻译，返回 key 本身作为回退（fallback）。

        Args:
            key: 翻译键，支持点号分隔的嵌套路径。
            **kwargs: 填充 {param} 占位符的参数。

        Returns:
            翻译后的字符串。
        """
        text = self._translations.get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        return text

    @property
    def current_language(self) -> str:
        """当前语言代码。"""
        return self._current_lang


# 全局单例
_i18n = I18n()

# 对外暴露的翻译函数
_ = _i18n.t
set_language = _i18n.set_language
current_language = lambda: _i18n.current_language
```

**使用示例**

```python
from i18n import _, set_language

# 原有硬编码写法（禁止）：
#   button_text = "确定"
#   label = "用户名"

# 推荐写法：
button = _( "common.ok")       # → "确定"（zh_CN） 或 "OK"（en）
label = _("login.username")   # → "用户名" 或 "Username"

# 参数化翻译：
msg = _("common.confirm_delete", item="订单 #12345")
# → "确认删除 订单 #12345？此操作不可撤销。"

# 切换语言：
set_language("en")
print(_("nav.home"))          # → "Home"
```

---

### 3.6 模式常量库

#### 适用场景

正则表达式模式（`HARD-REGEX`），包括输入验证、数据提取、字符串匹配等场景。

#### 实施步骤

1. 创建 `constants/patterns.py` 集中管理所有正则模式。
2. 使用 `re.compile()` 预编译模式，避免每次调用时重复编译。
3. 为每个模式添加描述性注释，说明其用途与匹配规则。

#### 示例代码

**`constants/patterns.py`**

```python
"""正则表达式模式常量库。

所有模式的编译版本在模块加载时一次性创建，运行时直接复用，
避免重复编译带来的性能开销。
"""

import re

# ── 用户输入验证 ──
# 用户名：3-32 位字母、数字、下划线，字母开头
USERNAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{2,31}$")

# 密码：至少 8 位，包含大小写字母和数字
PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,128}$")

# 电子邮箱（RFC 5322 简化版）
EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)

# 中国大陆手机号
PHONE_CN_PATTERN = re.compile(r"^1[3-9]\d{9}$")

# ── 数据提取 ──
# 从文本中提取 URL
URL_EXTRACT_PATTERN = re.compile(
    r"https?://[^\s<>\"']+|www\.[^\s<>\"']+",
    re.IGNORECASE,
)

# 从字符串中提取数字（含正负号与小数点）
NUMBER_EXTRACT_PATTERN = re.compile(r"-?\d+\.?\d*")

# ── 格式校验 ──
# IPv4 地址
IPV4_PATTERN = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$"
)

# UUID v4
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# ISO 日期格式 (YYYY-MM-DD)
DATE_ISO_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")

# ── 安全相关 ──
# SQL 注入危险字符检测
SQL_INJECTION_PATTERN = re.compile(
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|EXEC)\b)",
    re.IGNORECASE,
)
```

**使用示例**

```python
from constants.patterns import EMAIL_PATTERN, PHONE_CN_PATTERN

# 原有硬编码写法（禁止）：
#   if not re.match(r'^[a-zA-Z0-9...]+@...', email):
#       raise ValueError("无效邮箱")

# 推荐写法：
if not EMAIL_PATTERN.match(email):
    raise ValueError("邮箱格式不正确")

if not PHONE_CN_PATTERN.match(phone):
    raise ValueError("手机号格式不正确")
```

---

### 3.7 主题变量/设计令牌

#### 适用场景

颜色值、字体族、字号、间距、阴影、圆角等样式硬编码（`HARD-STYLE`）。

#### 实施步骤

1. 定义设计令牌 JSON 文件，按层次组织：**基础令牌 → 语义令牌 → 组件令牌**。
2. 在样式代码中引用令牌变量，禁止直接写入色值、像素值。
3. 支持通过切换令牌文件实现主题切换（如亮色/暗色模式）。

#### 示例代码

**`tokens/design_tokens.json`**

```json
{
  "base": {
    "color": {
      "white": "#FFFFFF",
      "black": "#000000",
      "gray_50": "#F9FAFB",
      "gray_100": "#F3F4F6",
      "gray_200": "#E5E7EB",
      "gray_400": "#9CA3AF",
      "gray_600": "#4B5563",
      "gray_800": "#1F2937",
      "gray_900": "#111827",
      "blue_500": "#3B82F6",
      "blue_600": "#2563EB",
      "blue_700": "#1D4ED8",
      "red_500": "#EF4444",
      "red_600": "#DC2626",
      "green_500": "#22C55E",
      "green_600": "#16A34A",
      "yellow_500": "#EAB308",
      "yellow_600": "#CA8A04"
    },
    "spacing": {
      "xs": "4px",
      "sm": "8px",
      "md": "16px",
      "lg": "24px",
      "xl": "32px",
      "2xl": "48px"
    },
    "font_size": {
      "sm": "0.875rem",
      "base": "1rem",
      "lg": "1.125rem",
      "xl": "1.25rem",
      "2xl": "1.5rem",
      "3xl": "1.875rem"
    },
    "font_family": {
      "sans": "'Inter', 'Noto Sans SC', system-ui, sans-serif",
      "mono": "'JetBrains Mono', 'Fira Code', monospace"
    },
    "border_radius": {
      "sm": "4px",
      "md": "8px",
      "lg": "12px",
      "full": "9999px"
    },
    "shadow": {
      "sm": "0 1px 2px rgba(0, 0, 0, 0.05)",
      "md": "0 4px 6px rgba(0, 0, 0, 0.1)",
      "lg": "0 10px 15px rgba(0, 0, 0, 0.1)"
    }
  },
  "semantic": {
    "color": {
      "primary": "{base.color.blue_600}",
      "primary_hover": "{base.color.blue_700}",
      "danger": "{base.color.red_600}",
      "danger_hover": "{base.color.red_500}",
      "success": "{base.color.green_600}",
      "warning": "{base.color.yellow_600}",
      "text_primary": "{base.color.gray_900}",
      "text_secondary": "{base.color.gray_600}",
      "text_disabled": "{base.color.gray_400}",
      "bg_primary": "{base.color.white}",
      "bg_secondary": "{base.color.gray_50}",
      "border": "{base.color.gray_200}"
    }
  },
  "component": {
    "button": {
      "primary_bg": "{semantic.color.primary}",
      "primary_hover_bg": "{semantic.color.primary_hover}",
      "height": "40px",
      "padding_x": "{base.spacing.lg}",
      "border_radius": "{base.border_radius.md}",
      "font_size": "{base.font_size.base}"
    },
    "card": {
      "bg": "{semantic.color.bg_primary}",
      "border": "{semantic.color.border}",
      "border_radius": "{base.border_radius.lg}",
      "padding": "{base.spacing.lg}",
      "shadow": "{base.shadow.sm}"
    },
    "input": {
      "height": "40px",
      "border": "{semantic.color.border}",
      "border_radius": "{base.border_radius.md}",
      "padding_x": "{base.spacing.sm}",
      "font_size": "{base.font_size.base}"
    }
  }
}
```

**样式引用示例（CSS 变量风格）**

```css
/* 原有硬编码写法（禁止）：
   .button { background: #2563EB; padding: 16px 24px; border-radius: 8px; } */

/* 推荐写法：引用设计令牌生成的 CSS 变量 */
:root {
  --color-primary: #2563EB;
  --color-primary-hover: #1D4ED8;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --radius-md: 8px;
  --font-size-base: 1rem;
}

.button-primary {
  background: var(--color-primary);
  padding: 0 var(--spacing-lg);
  height: 40px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
}

.button-primary:hover {
  background: var(--color-primary-hover);
}

.card {
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}
```

---

## 模板与脚手架

以下为推荐的最小化项目配置骨架，展示了各替代方案的标准目录结构与关键文件。

```
project/
├── config/
│   ├── default.yaml           # 默认配置文件
│   ├── development.yaml       # 开发环境覆盖配置（可选）
│   ├── production.yaml        # 生产环境覆盖配置（可选）
│   ├── config_loader.py       # 配置加载器
│   └── __init__.py
├── constants/
│   ├── __init__.py            # 常量与枚举统一导出
│   ├── enums.py               # 枚举类型定义
│   └── patterns.py            # 正则模式常量库
├── messages/
│   ├── __init__.py            # 消息模块入口
│   └── error_messages.py      # 错误与提示消息字典
├── i18n/
│   ├── __init__.py            # 国际化模块
│   └── translator.py          # 语言加载与翻译函数
├── locales/
│   ├── zh_CN/
│   │   └── messages.py        # 简体中文语言包
│   ├── en/
│   │   └── messages.py        # 英文语言包
│   └── template.pot           # 翻译模板（可选）
├── tokens/
│   ├── design_tokens.json     # 设计令牌定义
│   └── token_loader.py        # 令牌解析器（可选）
├── .env.example               # 环境变量模板（可提交至仓库）
├── .env                       # 实际环境变量（不提交，已在 .gitignore 中）
└── .gitignore
```

**`.gitignore` 必要项**

```gitignore
# 环境变量
.env
.env.local
.env.*.local

# 运行时产物
__pycache__/
*.pyc
*.pyo

# IDE
.vscode/
.idea/

# 操作系统
.DS_Store
Thumbs.db
```

---

## 迁移策略

从现有硬编码代码迁移到上述替代方案，应采用渐进式策略，避免一次性大规模重构带来的回归风险。

### 1. 先识别，后迁移

- 使用静态分析工具或手动审查识别当前代码库中的硬编码位置。
- 按类型标识（`HARD-CFG`、`HARD-NUM` 等）分类记录，建立硬编码清单。
- 迁移前确保已有充分测试覆盖，作为功能等价的回归保障。
- **不打散已有功能**：单次迁移聚焦同一模块的同一类硬编码，不影响其他功能。

### 2. 新代码零容忍

- 代码审查阶段强制检查：任何新增代码不得包含硬编码值。
- 在 CI 流水线中集成硬编码检测规则（如自定义 lint 规则），自动拦截违规提交。
- 团队规范明确：所有配置项、常量、消息文本、正则模式必须走替代方案路径。

### 3. 按风险等级分批次重构

| 批次 | 优先级 | 硬编码类型 | 迁移范围 | 理由 |
|---|---|---|---|---|
| 第 1 批 | P0 | `HARD-CFG`、`HARD-NUM`、`HARD-URL` | 配置参数、业务常量、API 端点 | 影响范围最大，更改频率最高，安全风险最突出 |
| 第 2 批 | P1 | `HARD-PATH`、`HARD-STR`（错误信息） | 路径定义、错误消息 | 提升可移植性，为国际化打基础 |
| 第 3 批 | P2 | `HARD-STR`（UI 文本）、`HARD-REGEX`、`HARD-STYLE`、`HARD-ENC` | UI 文本、正则模式、样式、编码常量 | 完善工程化体系，非阻塞性问题 |

### 4. 每次迁移后验证

- 运行全量单元测试与集成测试，确保功能等价。
- 对比迁移前后的行为（输入输出、边界条件、异常路径）。
- 更新相关文档与注释，注明配置项来源与引用路径。
- 迁移完成的硬编码清单项标记为"已消除"，纳入知识库存档。

---

## 附录：硬编码检测清单

在代码审查中，以下模式应被标记为硬编码并触发替代方案要求：

| 检测模式 | 示例（应标记） | 正确写法 |
|---|---|---|
| 数字字面量参与业务逻辑 | `if retry_count > 3:` | `if retry_count > config.get("retry.max_attempts"):` |
| 字符串 URL | `requests.get("https://api.example.com/v1/users")` | `requests.get(config.get("services.api.base_url") + "/users")` |
| 文件路径字符串 | `open("data/export.csv")` | `open(os.path.join(DATA_DIR, "export.csv"))` |
| 正则表达式内联 | `re.match(r"^1[3-9]\d{9}$", phone)` | `PHONE_CN_PATTERN.match(phone)` |
| 错误消息内联 | `raise ValueError("订单不存在")` | `raise ValueError(get_error("ORDER_NOT_FOUND", order_id=id))` |
| 色值硬编码 | `color: #2563EB;` | `color: var(--color-primary);` |

## 相关模式

- [检查与恢复模式](../../docs/retrospective/patterns/code-patterns/check-and-restore.md)
- [三级问题解决](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)
- [Dry-run优先原则](../../docs/retrospective/patterns/methodology-patterns/tools-automation/dry-run-first.md)
