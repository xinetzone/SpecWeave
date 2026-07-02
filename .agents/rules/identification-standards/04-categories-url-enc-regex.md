---
id: "rules-identification-04-categories-url-enc-regex"
title: "硬编码识别标准：类别详解（URL·编码·正则）"
source: "rules/identification-standards.md#各类别详细说明"
x-toml-ref: "../../../.meta/toml/.agents/rules/identification-standards/04-categories-url-enc-regex.toml"
---
# 硬编码识别标准：类别详解（URL·编码·正则）

本节详细说明各硬编码类别的定义、正反例与检测要点。

## 固定 URL/端点（HARD-URL）

**定义**：在代码中以字符串字面量形式直接写死的 HTTP/HTTPS 地址、API 端点、第三方服务回调地址、OAuth 授权端点等。此类地址因运行环境（开发/测试/生产）、服务迁移或版本升级而频繁变化。

**正例（应避免的写法）**：

```python
# ❌ 错误：API 端点硬编码
response = requests.post("https://api.example.com/v1/users", json=data)

# ❌ 错误：OAuth 端点硬编码
OAUTH_URL = "https://auth.example.com/oauth/authorize"

# ❌ 错误：回调地址硬编码
CALLBACK_URL = "https://myapp.com/callback"
```

**反例（推荐写法）**：

```python
# ✅ 正确：端点从配置读取，支持环境切换
response = requests.post(
    f"{config.API_BASE_URL}/v1/users",
    json=data
)

# ✅ 正确：OAuth 端点通过服务发现或配置管理
OAUTH_URL = config.OAUTH_AUTHORIZE_ENDPOINT

# ✅ 正确：回调地址动态构建
CALLBACK_URL = f"{config.BASE_URL}/callback"
```

**检测要点**：

- 以 `http://` 或 `https://` 开头的字符串字面量
- 包含域名或 IP 地址的字符串
- 排除：代码注释中的示例 URL
- 排除：测试代码中的 mock 地址（如 `http://localhost:8000` 或 `http://127.0.0.1`）

---

## 固定编码值（HARD-ENC）

**定义**：在代码中直接写死的字符编码标识、媒体类型（MIME Type）、协议标识等标准编码常量。此类值虽变更频率较低，但为了统一管理和避免拼写错误，建议通过常量库引用。

**正例（应避免的写法）**：

```python
# ❌ 错误：编码字符串硬编码
content = data.encode("utf-8")

# ❌ 错误：MIME 类型硬编码
headers = {"Content-Type": "application/json; charset=utf-8"}

# ❌ 错误：协议标识硬编码
version = "HTTP/1.1"
```

**反例（推荐写法）**：

```python
# ✅ 正确：使用标准库或自定义常量
from .constants import ENCODING_UTF8, MIME_JSON, HTTP_VERSION_11
content = data.encode(ENCODING_UTF8)
headers = {"Content-Type": f"{MIME_JSON}; charset={ENCODING_UTF8}"}
version = HTTP_VERSION_11
```

**检测要点**：

- 字符串参数中出现编码名称（如 `"utf-8"`、`"latin-1"`）
- 字符串中出现 MIME 类型格式（`"type/subtype"`）
- 注：此类硬编码风险较低，审查时可放宽处理，但建议在项目层面统一收口为常量

---

## 固定正则模式（HARD-REGEX）

**定义**：在代码中直接以正则表达式字面量或模式字符串形式出现的匹配规则，如邮箱验证、手机号校验、身份证号校验等。此类模式可能随业务规则调整而变化，且复杂正则难以维护和理解。

**正例（应避免的写法）**：

```python
# ❌ 错误：正则表达式直接写死在函数中
import re

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))

# ❌ 错误：正则模式作为字符串硬编码
phone_pattern = r"^1[3-9]\d{9}$"
```

**反例（推荐写法）**：

```python
# ✅ 正确：正则模式集中管理在常量模块
from .patterns import EMAIL_PATTERN
import re

def is_valid_email(email: str) -> bool:
    return bool(re.match(EMAIL_PATTERN, email))

# ✅ 正确：通过校验规则配置文件管理
from .validators import match_rule
match_rule("phone", value)
```

**检测要点**：

- `re.match`、`re.search`、`re.findall`、`re.compile` 的第一个参数是字符串字面量
- 变量赋值右侧为正则字符串字面量（以 `r"` 开头）
- 排除：简单的分隔符正则（如 `r"\s+"`、`r","`），属于通用数据处理逻辑

---
← 上一章: [03 类别详解：字符串/数值/路径](03-categories-str-num-path.md) | **[返回索引](../identification-standards.md)** | 下一章 → [05 类别详解：样式/配置](05-categories-style-cfg.md)
