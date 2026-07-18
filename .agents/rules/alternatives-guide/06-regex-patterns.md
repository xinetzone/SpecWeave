---
id: "rules-alt-regex-patterns"
title: "06 模式常量库"
source: "alternatives-guide.md#regex-patterns"
x-toml-ref: "../../../.meta/toml/.agents/rules/alternatives-guide/06-regex-patterns.toml"
---
# 06 模式常量库


## 适用场景

正则表达式模式（`HARD-REGEX`），包括输入验证、数据提取、字符串匹配等场景。

## 实施步骤

1. 创建 `constants/patterns.py` 集中管理所有正则模式。
2. 使用 `re.compile()` 预编译模式，避免每次调用时重复编译。
3. 为每个模式添加描述性注释，说明其用途与匹配规则。

## 示例代码

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

## 相关模式

- [硬编码治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/README.md)
- [三级问题解决](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)
- [检查与恢复模式](../../docs/retrospective/patterns/code-patterns/check-and-restore.md)
---

← 上一章: [05 国际化资源文件](05-i18n.md) | **[返回索引](../alternatives-guide.md)** | 下一章: [07 主题变量/设计令牌](07-design-tokens.md) →
