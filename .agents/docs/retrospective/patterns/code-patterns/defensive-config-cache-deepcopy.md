---
id: "defensive-config-cache-deepcopy"
source: "README.md"
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
# 防御性配置缓存：全返回路径统一深拷贝

## 模式概述

返回缓存配置对象的函数，必须在**所有返回路径**上统一执行防御性深拷贝，防止调用方修改返回值后污染全局缓存。

## 问题现象

缓存对象被调用方修改后污染全局缓存；条件分支不对称导致一条路径有保护另一条没有——这是静态代码审查中极易漏过的经典"阅读偏差"：人眼自然聚焦于"有保护的代码"，对"无保护的代码"视而不见。

典型反例：
- `_merge_configs` 中 overlay 直接修改 base 字典，导致配置合并优先级颠倒
- `config.copy()` 是浅拷贝，嵌套字典仍然共享引用
- 缓存命中时做 deepcopy，但首次加载时直接返回缓存对象本身

## 解决方案

```python
import copy
from typing import Any

_config_cache: dict[str, Any] | None = None

def get_config() -> dict[str, Any]:
    global _config_cache
    if _config_cache is not None:
        return copy.deepcopy(_config_cache)
    config = _load_and_merge_configs()
    _config_cache = config
    return copy.deepcopy(config)  # ★ 首次返回也要拷贝！两个return路径必须对称
```

合并配置时的对称保护：
```python
def _merge_configs(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    base = copy.deepcopy(base)
    base.update(overlay)
    return base
```

## 关键检查点

1. **两个 return 路径都必须 deepcopy**：不能只保护缓存命中路径
2. **测试必须覆盖三种场景**：首次调用、二次调用、调用方修改返回值后再调用
3. **合并配置时 overlay 不能直接修改 base**：使用 `base = copy.deepcopy(base); base.update(overlay)` 模式

## 正反例

### 正例

```python
# ✅ 两个返回路径对称保护
def get_config() -> dict[str, Any]:
    if _config_cache is not None:
        return copy.deepcopy(_config_cache)
    config = _load_and_merge_configs()
    _config_cache = config
    return copy.deepcopy(config)
```

### 反例

```python
# ❌ 条件分支不对称：首次调用直接返回缓存本身
def get_config() -> dict[str, Any]:
    if _config_cache is not None:
        return copy.deepcopy(_config_cache)
    config = _load_and_merge_configs()
    _config_cache = config
    return config  # BUG: 首次调用者拿到的是缓存引用！
```

## 适用场景

- 全局/单例配置缓存
- 任何返回可变对象缓存的函数
- 配置合并、默认值覆盖等场景

## 注意事项

1. **性能考虑**：deepcopy 有性能开销，若配置对象很大且调用频繁，考虑使用不可变数据结构（frozen dataclass、MappingProxyType）
2. **审查偏差**：M12 的修复经过四轮审查+五轮修复，仍然漏掉了"首次调用"路径——静态阅读代码时必须刻意检查所有分支
3. **测试覆盖**：不能只测"第二次调用"，必须测"第一次调用"后修改返回值的影响
