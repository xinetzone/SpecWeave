---
id: "file-io-concurrency-safety"
title: "文件 I/O 并发安全规范：原子写入、日志模板与重试策略"
x-toml-ref: "../../../.meta/toml/docs/knowledge/best-practices/file-io-concurrency-safety.toml"
category: "best-practices"
tags: ["concurrency", "file-io", "atomic-write", "logging", "retry-pattern", "windows", "defensive-programming"]
date: "2026-07-12"
status: "stable"
author: "SpecWeave"
summary: "基于原子写入重构实战（11个模块统一改造、46个测试覆盖、并发成功率82%→100%），提炼文件I/O并发安全三原则：写共享文件必须原子化、日志必须分阶段计时、重试必须有限次+退避。提供决策树、日志模板、重试参数规范和完整代码示例，作为所有涉及文件写入的脚本必须遵守的开发规范。"
---

# 文件 I/O 并发安全规范：原子写入、日志模板与重试策略

> 基于 spec_loader 冷启动优化与原子写入方案推广到全项目11个模块的实战经验。核心教训：**直接 `write_text()`/`json.dump()` 在多进程场景下不是安全操作**——Windows文件锁、内容截断、tmp残留等问题在压测中暴露，必须使用统一的原子写入工具和标准化的日志/重试模式。

**洞察来源**：[原子写入重构性能对比报告](../../retrospective/2026-07-12-atomic-write-refactoring.md)

---

## 核心数据

| 指标 | 重构前 | 重构后 |
|------|--------|--------|
| 并发写入成功率 | 82-95% | **100%** |
| 文件损坏率 | 3-8% | **0%** |
| tmp文件残留 | 崩溃时泄漏 | **0残留**（stale自动清理） |
| 冷启动耗时 | 15-25ms | **0.88ms**（↓94%） |
| 温启动耗时 | 5-10ms | **0.26ms**（↓95%） |
| 测试覆盖模块 | 1个模块 | **11个模块**（46个测试） |

---

## 原则一：写共享文件必须原子化

### 决策树：何时使用原子写入

```
写文件操作
├── 写入目标是否为进程独占的临时文件？
│   ├── 是（如 tempfile.TemporaryDirectory() 内的文件）
│   │   └── 可直接使用 write_text/write_bytes
│   └── 否（共享路径/缓存/报告/配置/文档）
│       ├── 写入模式是"覆盖"（全量替换）？
│       │   ├── 是 → 使用 atomic_write_bytes/text/json
│       │   └── 否（read-modify-write 循环）
│       │       ├── 修改独立标记区域？→ 使用 atomic_edit_text
│       │       └── 多进程同时修改同一文件不同区域？
│       │           └── 需要文件锁（当前规范未覆盖，避免此模式）
│       └── 文件名是否固定/可预测？
│           └── 是 → 必须使用原子写入
```

### 禁止的写法

```python
# ❌ 禁止：直接写入共享文件
path.write_text(content, encoding="utf-8")
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# ❌ 禁止：read-modify-write 无原子性
content = path.read_text(encoding="utf-8")
new_content = content.replace("old", "new")
path.write_text(new_content, encoding="utf-8")  # 竞态窗口

# ❌ 禁止：手动创建tmp文件（无PID隔离、无重试、无清理）
tmp = path.with_suffix(".tmp")
tmp.write_text(content)
os.rename(tmp, path)  # Windows上os.rename失败时不重试
```

### 正确的写法

```python
# ✅ 正确：原子写入文本/JSON/字节
from lib.atomic_write import atomic_write_text, atomic_write_json, atomic_write_bytes

atomic_write_text(path, content, encoding="utf-8")
atomic_write_json(path, data, ensure_ascii=False, indent=2)
atomic_write_bytes(path, binary_data)

# ✅ 正确：原子编辑（read-modify-write）
from lib.atomic_write import atomic_edit_text

def replace_marker(content: str) -> str:
    start = content.find("<!-- START -->") + len("<!-- START -->")
    end = content.find("<!-- END -->")
    return content[:start] + new_section + content[end:]

atomic_edit_text(path, replace_marker, encoding="utf-8")
```

### 适用场景清单

| 场景 | 推荐函数 | 已应用模块 |
|------|---------|-----------|
| JSON缓存文件 | `atomic_write_json` | spec_loader, check-links, check-academic-sources |
| JSON/HTML/MD报告 | `atomic_write_json`/`atomic_write_text` | sg_dashboard, mermaid-scan, extract-entities, scan_toml_frontmatter |
| Markdown标记区域更新 | `atomic_edit_text` | docgen (update_marker_region) |
| API文档生成 | `atomic_write_text` | api_docs |
| 迁移报告输出 | `atomic_write_json` | migrate_frontmatter/cli |
| 性能基线导出 | `atomic_write_json` | spec-loader-export-metrics |
| 敏感信息扫描结果 | `atomic_write_text` | checks/sensitive_info |

---

## 原则二：关键路径日志必须分阶段计时

### 问题

传统日志只记录总耗时（如"缓存保存完成，耗时5ms"），无法定位瓶颈在哪个子阶段。当性能退化时，需要重新添加日志复现问题，效率极低。

### 日志模板规范

**所有涉及文件 I/O 的关键操作，必须在子阶段级别记录耗时。**

#### 模板A：多阶段写入操作（缓存保存/导出）

```python
import logging
import time

_log = logging.getLogger(__name__)

def _save_disk_cache(self):
    _t_save_start = time.perf_counter()
    try:
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        # 阶段1：构建数据
        _t_build_start = time.perf_counter()
        entries = self._build_cache_entries()
        _t_build_ms = (time.perf_counter() - _t_build_start) * 1000

        # 阶段2：淘汰/清理
        _t_evict_start = time.perf_counter()
        evicted = self._evict_old_entries(entries)
        _t_evict_ms = (time.perf_counter() - _t_evict_start) * 1000

        # 阶段3：序列化
        _t_ser_start = time.perf_counter()
        data = {"version": self._cache_version, "entries": entries}
        serialized = json.dumps(data).encode("utf-8")
        _t_ser_ms = (time.perf_counter() - _t_ser_start) * 1000

        # 阶段4：原子写入
        _t_write_start = time.perf_counter()
        atomic_write_bytes(self._cache_path, serialized)
        _t_write_ms = (time.perf_counter() - _t_write_start) * 1000

        _log.debug(
            "磁盘缓存保存完成 | 条目=%d(evict=%d) | "
            "build=%.2fms | evict=%.2fms | serialize=%d bytes/%.2fms | "
            "atomic-write=%.2fms | 总耗时=%.2fms",
            len(entries), evicted, _t_build_ms, _t_evict_ms,
            len(serialized), _t_ser_ms, _t_write_ms,
            (time.perf_counter() - _t_save_start) * 1000,
        )
    except OSError as e:
        _log.warning(
            "磁盘缓存保存失败 | error=%s | elapsed=%.2fms",
            e, (time.perf_counter() - _t_save_start) * 1000,
        )
```

#### 模板B：初始化/加载操作（冷启动路径）

```python
def _load_disk_cache(self):
    _t_load_start = time.perf_counter()

    _t_config_start = time.perf_counter()
    config = self._load_config()
    _t_config_ms = (time.perf_counter() - _t_config_start) * 1000

    _t_read_start = time.perf_counter()
    try:
        with open(self._cache_path, "rb") as f:
            data = json.loads(f.read())
        _t_read_ms = (time.perf_counter() - _t_read_start) * 1000
        _log.debug(
            "磁盘缓存加载完成 | entries=%d | config=%.2fms | read=%.2fms | 总耗时=%.2fms",
            len(data.get("entries", {})), _t_config_ms, _t_read_ms,
            (time.perf_counter() - _t_load_start) * 1000,
        )
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        _log.debug(
            "磁盘缓存未命中 | reason=%s | elapsed=%.2fms",
            e, (time.perf_counter() - _t_load_start) * 1000,
        )
        return None
```

#### 模板C：Stale清理/后台维护操作

```python
# 在 atomic_write 内部已实现：
_log.debug("stale清理完成 | scanned=%d | cleaned=%d | errors=%d | 耗时=%.3fms",
           scanned, cleaned, errors, _t_ms)
```

### 日志格式规范

| 要素 | 规范 | 示例 |
|------|------|------|
| 分隔符 | 使用 `\|` 分隔键值对 | `"操作完成 | key1=val1 | key2=val2"` |
| 键名 | 使用kebab-case | `atomic-write`, `build`, `evict` |
| 数值 | 计数用`%d`，毫秒用`%.2fms`，字节用`%d bytes` | `"entries=%d"`, `"build=%.2fms"` |
| 错误 | 用`warning`级别，包含error和elapsed | `"保存失败 | error=%s | elapsed=%.2fms"` |
| 成功 | 用`debug`级别（热路径） | 不污染正常输出 |
| 时间源 | 统一使用 `time.perf_counter()` | 最高精度（~0.1μs），不受系统时钟调整影响 |

---

## 原则三：重试必须有限次+退避，禁止无限重试

### 问题

Windows上 `os.replace()` 可能因杀毒软件、文件索引器短暂锁定文件而抛出 `PermissionError`。无重试→偶发失败；无限重试→可能挂死。

### 重试参数规范

| 参数 | 默认值 | 适用场景 | 调整建议 |
|------|--------|---------|---------|
| `max_retries` | **3**（不含首次尝试，共4次机会） | 常规文件替换 | 高并发写热点可增至5 |
| `retry_interval_ms` | **10ms** | Windows文件锁短暂冲突 | 不建议超过50ms（总延迟过高） |
| `stale_max_age_sec` | **3600**（1小时） | tmp残留清理 | 短生命周期文件可降至300s |
| `cleanup_stale` | **True** | 默认清理 | 性能敏感路径可设False |

### 重试日志模板

```python
# 重试中（debug级别）
_log.debug("atomic_replace重试 | attempt=%d/%d | error=%s | interval=%dms | src=%s",
           attempt + 1, max_retries, e, interval_ms, src.name)

# 重试耗尽（异常向上抛出前，清理tmp）
try:
    src.unlink(missing_ok=True)
except OSError:
    pass
raise last_error
```

### 禁止的重试模式

```python
# ❌ 禁止：无限重试
while True:
    try:
        os.replace(src, dst)
        break
    except PermissionError:
        time.sleep(0.01)

# ❌ 禁止：无退避重试（CPU空转）
for _ in range(100):
    try:
        os.replace(src, dst)
        break
    except PermissionError:
        pass  # 忙等

# ❌ 禁止：吞掉异常静默成功
try:
    os.replace(src, dst)
except PermissionError:
    pass  # 写入失败但假装成功 → 文件丢失
```

### 正确的重试模式

```python
# ✅ 正确：有限次+固定退避+失败清理
max_retries = 3
interval_ms = 10
last_error = None
for attempt in range(max_retries + 1):
    try:
        os.replace(src, dst)
        return
    except OSError as e:
        last_error = e
        if attempt < max_retries:
            _log.debug("retry | attempt=%d/%d | error=%s", attempt + 1, max_retries, e)
            time.sleep(interval_ms / 1000.0)
        else:
            try:
                src.unlink(missing_ok=True)
            except OSError:
                pass
raise last_error
```

> **注意**：固定间隔重试适用于短暂锁冲突（AV/索引器），不需要指数退避。指数退避适用于网络请求等场景，不适用于本地文件操作。

---

## 原子写入API参考

### atomic_write_bytes

```python
def atomic_write_bytes(
    dst: Union[str, Path],
    data: bytes,
    max_retries: int = 3,
    retry_interval_ms: int = 10,
    stale_max_age_sec: float = 3600,
    cleanup_stale: bool = True,
) -> Path:
```

写入流程：
1. `dst.parent.mkdir(parents=True, exist_ok=True)` — 确保父目录存在
2. 清理过期tmp文件（PID+随机后缀匹配，>1小时自动删除）
3. 生成唯一tmp路径：`{dst.name}.pid{pid}.{rand6}.tmp`
4. 写入tmp文件
5. `os.replace(tmp, dst)` 原子替换（Windows锁冲突自动重试3次）
6. 任何异常→清理tmp文件后抛出

### atomic_write_text / atomic_write_json

`atomic_write_text` 和 `atomic_write_json` 是便捷封装，参数透传给 `atomic_write_bytes`。

### atomic_edit_text

```python
def atomic_edit_text(
    dst: Union[str, Path],
    editor: Callable[[str], str],
    encoding: str = "utf-8",
    max_retries: int = 3,
    retry_interval_ms: int = 10,
    **kwargs,
) -> Path:
```

读取文件→调用editor→原子写入。保证读者不会看到中间状态，但不提供跨进程乐观锁（last-writer-wins）。适用于标记区域更新、单进程脚本。

---

## 竞态条件风险分级与处理

### 🔴 高风险：必须使用原子写入

| 场景 | 风险 | 处理方式 |
|------|------|---------|
| 多进程/Agent写入同一缓存文件 | 文件损坏、内容截断 | atomic_write_json |
| CI/CD脚本生成报告 | 读者看到不完整JSON/HTML | atomic_write_json/text |
| 自动更新Markdown标记区域 | 更新丢失、文件损坏 | atomic_edit_text 或 update_marker_region |
| JSON状态文件持久化 | JSONDecodeError导致下次加载失败 | atomic_write_json |

### 🟡 中风险：建议使用原子写入

| 场景 | 风险 | 处理方式 |
|------|------|---------|
| 单实例脚本生成输出文件 | 低概率冲突（如两次手动运行） | atomic_write_text（防御性编程） |
| 文档自动生成工具 | 手动运行时中断→文件损坏 | atomic_write_text |
| 日志轮转/备份文件 | 多实例部署时冲突 | atomic_write_bytes |

### 🟢 低风险：可使用直接写入

| 场景 | 原因 |
|------|------|
| tempfile.TemporaryDirectory() 内的文件 | 进程独占目录，无并发可能 |
| 一次性脚本输出到用户指定的新路径 | 文件不存在，首次创建 |
| 测试fixture中的临时文件 | 测试隔离 |
| Playwright/Playwright的storage_state | 第三方库自行保证原子性 |

---

## 代码审查Checklist

审查任何文件写入代码时，必须逐项确认：

- [ ] **写入目标是否为共享路径？** 如果是，是否使用了 atomic_write 系列函数？
- [ ] **是否存在read-modify-write循环？** 如果是，是否使用了 atomic_edit_text？
- [ ] **临时文件名是否包含PID和随机后缀？** 禁止使用固定 `.tmp` 后缀
- [ ] **os.replace失败是否有重试？** 重试次数是否≤5？间隔是否在10-50ms？
- [ ] **重试失败是否清理临时文件？** 防止tmp泄漏
- [ ] **关键路径是否有分阶段计时日志？** 格式是否符合模板（build/serialize/write拆分）？
- [ ] **失败路径是否有error日志？** 是否包含 error 信息和 elapsed 时间？
- [ ] **是否使用time.perf_counter()计时？** 禁止使用time.time()（受NTP调整影响）
- [ ] **单元测试是否覆盖？** 至少覆盖：成功写入、重试成功、重试失败清理、多进程并发

---

## 测试要求

| 测试场景 | 必须覆盖 | 测试方法 |
|---------|---------|---------|
| 基本写入 | ✅ | bytes/text/json/encoding/overwrite/empty/large |
| PID唯一命名 | ✅ | 格式验证+多进程碰撞测试 |
| Stale清理 | ✅ | 过期删除/新文件保留/unlink容错/自定义TTL |
| 文件锁重试 | ✅ | 首次成功/重试成功/耗尽清理/重试次数验证/间隔验证 |
| 失败清理 | ✅ | 序列化失败/replace失败/双重失败不崩溃 |
| 多进程并发 | ✅ | 8进程并发写入无损坏、无tmp泄漏 |
| 原子编辑 | ✅ | 基本替换/标记区域/异常传播/无tmp残留 |

参考实现：[test_atomic_write.py](file:///d:/spaces/SpecWeave/.agents/scripts/tests/test_atomic_write.py)（46个测试用例）

---

## 相关资源

- [atomic_write.py 源码](file:///d:/spaces/SpecWeave/.agents/scripts/lib/atomic_write.py)
- [原子写入重构性能对比报告](../../retrospective/2026-07-12-atomic-write-refactoring.md)
- [并发代码安全审查六维检查法](./concurrent-code-safety-review.md)
- [八维并发安全规范](./eight-dimensions-concurrent-safety-spec.md)
