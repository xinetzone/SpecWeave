---
id: "rules-identification-03-categories-str-num-path"
title: "硬编码识别标准：类别详解（字符串·数值·路径）"
source: "rules/identification-standards.md#各类别详细说明"
x-toml-ref: "../../../.meta/toml/.agents/rules/identification-standards/03-categories-str-num-path.toml"
---
# 硬编码识别标准：类别详解（字符串·数值·路径）

本节详细说明各硬编码类别的定义、正反例与检测要点。

## 固定字符串（HARD-STR）

**定义**：直接在代码中以字面量形式出现的文本字符串，包括但不限于错误消息、日志输出内容、用户界面标签、提示文本、通知模板等。此类字符串通常应通过消息字典、国际化（i18n）资源文件或配置中心管理。

**正例（应避免的写法）**：

```python
# ❌ 错误：错误消息硬编码在代码中
raise ValueError("配置文件格式不正确，请检查 YAML 语法")

# ❌ 错误：日志文本硬编码
logger.info("用户登录成功，开始加载个人数据")

# ❌ 错误：UI 标签硬编码
return {"label": "请输入您的用户名"}
```

**反例（推荐写法）**：

```python
# ✅ 正确：错误消息外部化到消息字典
from .messages import ERROR_MSGS
raise ValueError(ERROR_MSGS["config_format_invalid"])

# ✅ 正确：日志消息通过消息模板管理
logger.info(MSG_TEMPLATES["user_login_success"])

# ✅ 正确：UI 标签通过 i18n 资源加载
return {"label": t("input.username.placeholder")}
```

**检测要点**：

- 函数调用中直接出现的非变量中文字符串或完整英文句子
- `raise`、`print`、`log`、`logger.info` 等语句中直接写死的文本
- 字典或 JSON 结构中写死的面向用户的文本内容
- 排除：日志中的变量插值占位符（如 `f"user_id={uid}"`）属于数据拼接，不属于此类

---

## 固定数值（HARD-NUM）

**定义**：在代码中直接以数字字面量形式出现的业务相关数值，包括业务规则阈值、超时时间、分页大小、权重系数、折扣率、手续费比例等。此类数值通常随业务需求变化，应抽取为配置项。

**正例（应避免的写法）**：

```python
# ❌ 错误：业务阈值硬编码
if score < 60:
    return "不合格"

# ❌ 错误：超时时间硬编码
response = requests.get(url, timeout=30)

# ❌ 错误：分页大小硬编码
items = query.limit(20).all()
```

**反例（推荐写法）**：

```python
# ✅ 正确：业务阈值从配置读取
if score < config.PASS_THRESHOLD:
    return "不合格"

# ✅ 正确：超时时间从配置读取
response = requests.get(url, timeout=config.HTTP_TIMEOUT)

# ✅ 正确：分页大小从配置读取
items = query.limit(config.PAGE_SIZE).all()
```

**检测要点**：

- 在比较运算符（`<`、`>`、`==`、`!=`）或函数参数中出现的非零整数/浮点数
- 排除：数组索引 `0`、`-1`，循环计数器 `i=0`，偏移量等逻辑控制数值
- 排除：数学或物理常量（如 `math.pi`、`gravitational_constant`）

---

## 固定路径（HARD-PATH）

**定义**：在代码中以字符串字面量形式直接写死的文件系统路径、目录路径或资源路径。此类路径通常因部署环境（开发/测试/生产）、操作系统或目录布局而异，应通过环境变量或配置中心管理。

**正例（应避免的写法）**：

```python
# ❌ 错误：文件路径硬编码（且针对性适配某个操作系统）
with open("/etc/app/config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

# ❌ 错误：日志目录硬编码
LOG_DIR = "./logs"

# ❌ 错误：资源路径硬编码
TEMPLATE_PATH = "templates/email/welcome.html"
```

**反例（推荐写法）**：

```python
# ✅ 正确：路径通过环境变量读取
import os
cfg_path = os.environ.get("APP_CONFIG_PATH", "/etc/app/config.yaml")
with open(cfg_path, "r") as f:
    cfg = yaml.safe_load(f)

# ✅ 正确：路径通过配置对象读取
LOG_DIR = config.LOG_DIR

# ✅ 正确：使用 pathlib 构建跨平台路径，根路径来自配置
from pathlib import Path
TEMPLATE_PATH = Path(config.RESOURCE_ROOT) / "email" / "welcome.html"
```

**检测要点**：

- 字符串中出现的 `/` 或 `\` 路径分隔符
- 文件扩展名联合路径字符串（如 `.yaml`、`.json`、`.log`、`.html`）
- 排除：Python 模块导入路径（`import` 语句），其属于语言机制
- 排除：`os.path.join` 中作为拼接片段的纯目录名（若根路径来自外部）

---
← 上一章: [02 分类定义表](02-category-table.md) | **[返回索引](../identification-standards.md)** | 下一章 → [04 类别详解：URL/编码/正则](04-categories-url-enc-regex.md)
