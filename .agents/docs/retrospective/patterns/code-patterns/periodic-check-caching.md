---
id: "periodic-check-caching"
source: "../../reports/project-governance/documentation-governance/retrospective-link-fix-depth-adjustment-20260626/insights/insight-08-cache-for-periodic-checks.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/periodic-check-caching.toml"
---
# 定期检查类工具的缓存机制（Periodic Check Caching）

## 模式类型
代码模式

## 成熟度
L1 实验性（1次案例：check-links.py外部URL检查7天缓存）

## 适用场景
开发定期检查类CLI工具，特别是需要：
- 访问外部网络资源（HTTP请求、API调用）
- 执行耗时计算（全量扫描、复杂分析）
- 在CI/本地频繁运行的检查脚本

## 问题背景

定期检查工具在首次运行时访问外部资源或执行耗时计算是必要的，但后续运行如果每次都重复相同的昂贵操作，会导致：
- 运行时间过长（如50个HTTP请求需10-20秒）
- 对外部服务造成不必要的压力
- CI/本地开发体验差（等待时间长，减少运行频率）

## 核心设计

任何需要访问外部资源或执行耗时计算的检查工具，都应内置缓存机制，且缓存策略必须可配置。

### 缓存三要素

| 要素 | 说明 | 默认值 |
|------|------|--------|
| **缓存存储** | 结果持久化位置 | 项目内 `.cache/` 目录，JSON格式 |
| **缓存有效期（TTL）** | 多久后缓存过期需要刷新 | 7天（外部资源）/ 1天（内部扫描） |
| **缓存控制选项** | 用户如何覆盖默认缓存行为 | --no-cache / --cache-ttl N / --clear-cache |

### 代码结构示例

```python
import json
import time
from pathlib import Path

CACHE_DIR = Path(".cache")
DEFAULT_TTL = 7 * 24 * 3600  # 7天

def get_cached_result(key: str, ttl: int = DEFAULT_TTL):
    """从缓存获取结果，如果过期返回None"""
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        if time.time() - data["timestamp"] < ttl:
            return data["result"]
    return None

def set_cached_result(key: str, result):
    """将结果写入缓存"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{key}.json"
    cache_file.write_text(
        json.dumps({"timestamp": time.time(), "result": result}, ensure_ascii=False),
        encoding="utf-8"
    )

def check_external_url(url: str, no_cache: bool = False, cache_ttl: int = DEFAULT_TTL):
    """带缓存的URL检查"""
    cache_key = f"url_check_{hashlib.md5(url.encode()).hexdigest()}"
    
    if not no_cache:
        cached = get_cached_result(cache_key, cache_ttl)
        if cached is not None:
            return cached  # 缓存命中
    
    result = do_actual_http_check(url)  # 耗时操作
    set_cached_result(cache_key, result)
    return result
```

### CLI参数设计

```
--no-cache          强制绕过缓存，重新执行所有检查
--cache-ttl HOURS   自定义缓存有效期（小时），默认168（7天）
--clear-cache       清除所有缓存后退出
```

## 效果数据

check-links.py外部URL检查加入缓存后：
| 场景 | HTTP请求数 | 耗时 |
|------|-----------|------|
| 首次运行 | 50 | 10-20秒 |
| 二次运行（缓存命中） | 0 | <1秒 |
| 强制刷新（--no-cache） | 50 | 10-20秒 |

## 缓存策略选择指南

| 检查类型 | 推荐TTL | 是否默认缓存 |
|---------|---------|------------|
| 外部URL可达性 | 7天 | 是 |
| 文件系统扫描 | 不缓存（本地IO快） | 否 |
| 外部API数据 | 1-24小时（视数据更新频率） | 是 |
| 耗时计算/分析 | 1天 | 是 |
| CI环境中的检查 | 通常no-cache（确保新鲜） | 否（CI可用--no-cache） |

## 检查清单

- [ ] 工具是否访问外部资源或执行耗时计算？
- [ ] 是否有默认缓存机制降低重复运行成本？
- [ ] 缓存TTL是否适合数据的更新频率？
- [ ] 用户是否能通过参数绕过缓存（--no-cache）？
- [ ] 用户是否能自定义TTL（--cache-ttl）？
- [ ] 用户是否能清除缓存（--clear-cache）？
- [ ] 缓存目录是否在.gitignore中？
- [ ] 缓存失效是否优雅降级（过期自动刷新，不报错）？

## 反例警示

| 陷阱 | 后果 |
|------|------|
| 没有缓存，每次都发HTTP请求 | 运行慢，用户减少使用频率 |
| 缓存不可绕过 | 用户无法在需要时获取最新结果 |
| TTL硬编码不可配置 | 不同场景需要不同TTL时无法调整 |
| 缓存文件不加入.gitignore | 缓存被提交到仓库，污染版本控制 |
| 缓存过期时报错 | 用户体验差，应自动刷新而非报错 |

## 与现有模式的关系

- `three-tier-check-tool.md`：三层检查工具架构（感知层→引擎→报告层），缓存属于引擎层的优化策略
