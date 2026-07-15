---
id: "exception-precision-guards"
source: "../../../../../.temp/backup/docs-before-agents-docs-20260715/retrospective/patterns/code-patterns/exception-precision-guards.md"
domain: "code"
layer: "code"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "standard"

[bindings]
rules = []
references = []
skills = []
---
# 异常精确性守卫：只捕获可恢复异常，编程错误自然抛出

## 模式概述

`except Exception` 会吞掉 TypeError、AttributeError、NameError 等**编程错误**，等于关闭了编译器的类型检查。库函数只能捕获该函数语义上"可恢复"的异常类型，且必须记录日志；CLI 顶层入口才可作为最后防线兜底。

## 问题现象

`except Exception` 吞掉 TypeError/AttributeError/NameError 等编程错误：
- 传了 None 给期望 str 的函数 → TypeError 被吞，返回空默认值掩盖问题
- 打错方法名 → AttributeError 被吞，程序静默继续运行产生错误结果
- 打错变量名 → NameError 被吞，逻辑走到错误分支
- YAML 语法错误 → 被 OSError 范围的 except 吞掉，返回空配置造成后续更难调试的错误

## 解决方案

```python
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

# ✅ 正确做法：只捕获可恢复异常，记录日志，编程错误自然抛出
def load_config(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.info("配置文件 %s 不存在，使用默认值", path)
        return {}
    except (yaml.YAMLError, OSError) as exc:
        logger.warning("加载配置文件 %s 失败: %s，使用默认值", path, exc)
        return {}
# TypeError(传了None给Path)、AttributeError(打错方法名)等会正确向上抛出
```

## 异常分层原则

| 层级 | 可捕获范围 | 日志要求 |
|------|-----------|---------|
| **库函数内部** | 只捕获该函数语义上**预期可恢复**的异常类型 | 必须记录 warning/info 级别日志，包含异常信息 |
| **业务逻辑层** | 可捕获已知业务异常，做降级/重试处理 | 记录 error 级别日志，包含上下文 |
| **CLI 顶层入口** | 可 `except Exception` 作为最后防线 | 必须 `logger.exception(...)` 记录完整栈 trace |

## 判断标准

> 如果这个异常被吞掉后程序继续运行，它产生的错误结果是否比崩溃更难调试？

- **更难调试** → 不要捕获，让它崩溃（快速失败）
- **可优雅降级** → 捕获并记录日志，返回合理默认值

## 正反例

### 正例

```python
# ✅ 精确捕获可恢复异常
def load_config(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.info("配置文件 %s 不存在，使用默认值", path)
        return {}
    except (yaml.YAMLError, OSError) as exc:
        logger.warning("加载配置文件 %s 失败: %s", path, exc)
        return {}

# ✅ CLI顶层最后防线
def main():
    try:
        run_app()
    except Exception:
        logger.exception("程序异常退出")
        sys.exit(1)
```

### 反例

```python
# ❌ 吞掉所有异常，编程错误被掩盖
def load_config_bad(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception:  # TypeError/AttributeError/NameError都被吞了！
        return {}
```

## 适用场景

- 配置加载、文件读写、网络请求等 IO 操作
- 库函数、工具模块中的异常处理
- 任何有默认值/降级策略的代码路径
- CLI 工具的入口和子命令

## 注意事项

1. **捕获后必须记录日志**：空 except 块是反模式，至少要有 `logger.debug/info/warning`
2. **不要在库代码中使用 bare except**：`except:` 甚至会捕获 KeyboardInterrupt 和 SystemExit
3. **重新抛出保留栈信息**：如果捕获后需要转换异常类型，使用 `raise NewException(...) from exc`
4. **TypeError/AttributeError 是朋友**：它们在告诉你代码有 bug，不要隐藏它们
