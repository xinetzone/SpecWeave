---
id: "rules-identification-05-categories-style-cfg"
title: "硬编码识别标准：类别详解（样式·配置）"
source: "rules/identification-standards.md#各类别详细说明"
x-toml-ref: "../../../.meta/toml/.agents/rules/identification-standards/05-categories-style-cfg.toml"
---
# 硬编码识别标准：类别详解（样式·配置）

本节详细说明各硬编码类别的定义、正反例与检测要点。

## 固定颜色/样式（HARD-STYLE）

**定义**：在代码中直接写死的视觉样式值，包括 CSS 颜色值（十六进制、RGB）、字体大小、边距、间距、边框样式等。此类值通常应与设计系统（Design System）或主题变量绑定。

**正例（应避免的写法）**：

```python
# ❌ 错误：颜色值硬编码
button_style = {"background-color": "#1890ff", "font-size": "14px"}

# ❌ 错误：间距硬编码
layout = {"padding": "24px", "margin": "16px"}

# ❌ 错误：尺寸硬编码
component_size = {"width": 320, "height": 240}
```

**反例（推荐写法）**：

```python
# ✅ 正确：引用设计令牌（Design Token）
from .tokens import Color, Spacing, FontSize
button_style = {"background-color": Color.PRIMARY, "font-size": FontSize.BASE}

# ✅ 正确：从主题配置读取
layout = {"padding": theme.SPACING_LG, "margin": theme.SPACING_MD}

# ✅ 正确：组件尺寸从预设常量读取
from .constants import DIALOG_SIZES
component_size = DIALOG_SIZES["medium"]
```

**检测要点**：

- 字符串中出现 `#` 开头的十六进制颜色值或 `rgb(` 函数
- 字符串中出现 `px`、`em`、`rem` 等 CSS 单位且无变量引用
- 整数值用于表示像素尺寸且无上下文关联

---

## 固定配置参数（HARD-CFG）

**定义**：在代码中直接写死的系统运行参数，包括数据库连接池大小、线程池大小、重试次数、缓存过期时间、队列容量、批量处理大小等。此类参数的调优依赖具体硬件资源和业务负载，必须在运行时灵活调整。

**正例（应避免的写法）**：

```python
# ❌ 错误：连接池大小硬编码
pool = ConnectionPool(max_connections=10)

# ❌ 错误：重试次数硬编码
@retry(stop_max_attempt_number=3)
def send_message(msg):
    ...

# ❌ 错误：缓存过期时间硬编码
cache.set(key, value, expire=3600)
```

**反例（推荐写法）**：

```python
# ✅ 正确：连接池大小从配置读取
pool = ConnectionPool(max_connections=config.DB_POOL_SIZE)

# ✅ 正确：重试次数从配置读取
@retry(stop_max_attempt_number=config.RETRY_MAX_ATTEMPTS)
def send_message(msg):
    ...

# ✅ 正确：缓存过期时间从配置读取
cache.set(key, value, expire=config.CACHE_TTL_SECONDS)
```

**检测要点**：

- 函数参数中代表容量、次数、时长的非零整数/浮点数
- `time.sleep()`、`cache.set(..., expire=N)`、`max_workers=N` 等参数
- 排除：`0`、`1`、`-1` 等表示"禁用/启用/无限"的哨兵值
← 上一章: [04 类别详解：URL/编码/正则](04-categories-url-enc-regex.md) | **[返回索引](../identification-standards.md)** | 下一章 → [06 区分标准与边界判断](06-boundary-judgment.md)
