---
id: "dynamic-path-derivation"
source: "README.md"
domain: "code"
layer: "code"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "standard"

[bindings]
rules = []
references = ["path-anchor-semantization"]
skills = []
---
# 动态路径推导：基于 __file__ 的可移植默认路径

## 模式概述

代码内置默认路径必须基于 `__file__` 位置动态推导，禁止硬编码开发者机器的绝对路径，确保代码在不同机器、不同部署位置均可移植。

## 问题现象

硬编码开发者绝对路径导致代码不可移植：
- M6 硬编码开发者绝对路径（如 `/home/dev/project/libs/tvm`）
- 新开发者 clone 代码后路径不存在，程序崩溃
- CI/CD 环境路径不同导致构建失败
- Docker 容器内挂载路径与宿主机不同

## 解决方案

```python
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[1]  # 项目根目录（基于当前文件位置推导）
_DEFAULT_TVM_SRC = ROOT_DIR.parent.parent / "libs" / "npu_tvm"

def _get_path_config(
    key: str,
    fallback: Path,
    warn_on_fallback: bool = True,
) -> Path:
    value = get_config_value(key, None)
    if value is not None:
        return Path(value)
    if warn_on_fallback:
        logger.warning("配置项 %s 未设置，使用默认路径: %s", key, fallback)
    return fallback

def get_tvm_src() -> Path:
    return _get_path_config("paths.tvm_src", _DEFAULT_TVM_SRC)
```

## 关键检查点

1. **默认值基于 `__file__` 推导**：不硬编码绝对路径，使用 `Path(__file__).resolve().parents[N]`
2. **fallback 时发出 warning**：告知用户配置项缺失，避免静默使用默认值造成困惑
3. **`parents[N]` 中 N 根据文件位置调整**：写好后用 `print(ROOT_DIR)` 验证层级是否正确
4. **配置优先于默认值**：通过配置项可覆盖默认路径，满足特殊部署需求

## 默认值三分类

代码内置默认值只能是三类：

| 类型 | 示例 | 说明 |
|------|------|------|
| 基于 `__file__` 的相对路径推导 | `Path(__file__).resolve().parents[1]` | 项目内资源、相邻模块 |
| 协议标准定义的常量 | `8080`(HTTP)、`22`(SSH)、`64*1024`(缓冲) | 通用协议端口、超时、大小限制 |
| `None`（表示"必须配置"） | 外部服务地址、API Key | 无法给出合理默认值的配置项 |

## 正反例

### 正例

```python
# ✅ 动态推导 + fallback警告 + 配置覆盖
ROOT_DIR = Path(__file__).resolve().parents[1]
_DEFAULT_DATA_DIR = ROOT_DIR / "data"

def get_data_dir() -> Path:
    configured = get_config_value("paths.data_dir", None)
    if configured:
        return Path(configured)
    logger.warning("paths.data_dir 未配置，使用默认值: %s", _DEFAULT_DATA_DIR)
    return _DEFAULT_DATA_DIR
```

### 反例

```python
# ❌ 硬编码开发者绝对路径
TVM_SRC = Path("/home/zhangsan/projects/npu/libs/npu_tvm")
DATA_DIR = Path("C:\\Users\\lisi\\project\\data")  # Windows路径在Linux/Mac上不存在
```

## 适用场景

- 项目内资源路径定位（模板、配置文件、数据目录）
- 相邻子模块/依赖库的相对路径推导
- 开发环境工具链中的路径配置
- 可配置路径的默认值设定

## 注意事项

1. **层级验证**：`parents[N]` 容易算错，务必在写完后 `print(ROOT_DIR)` 验证
2. **语义化变量**：参考 [path-anchor-semantization.md](path-anchor-semantization.md) 模式，为每级 parent 赋予语义变量名
3. **resolve() 必须调用**：不调用 resolve() 时，符号链接可能导致路径计算错误
4. **跨平台兼容**：使用 `pathlib.Path` 的 `/` 运算符拼接路径，不要用字符串拼接
