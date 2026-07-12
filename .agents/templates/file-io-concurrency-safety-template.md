# 文件 I/O 并发安全开发规范（模板）

> **使用说明**：本文档是一份**模板**，用于为新项目/新模块制定文件 I/O 并发安全规范。复制后请替换所有 `{{占位符}}` 内容，根据项目实际情况调整参数值和场景分类。
>
> **基于实战数据**：本模板提炼自 SpecWeave 项目原子写入重构经验（12个模块改造、70个单元测试、并发成功率82%→100%、冷启动耗时↓94%）。

---

## 1. 适用范围

本规范适用于 `{{项目/模块名称}}` 中所有涉及文件写入操作的代码，包括但不限于：
- {{场景1：如"缓存文件写入"}}
- {{场景2：如"配置文件保存"}}
- {{场景3：如"报告/日志输出"}}
- {{场景4：如"状态持久化"}}

**不适用场景**：
- {{排除场景1：如"进程独占的临时文件（tempfile.TemporaryDirectory内）"}}
- {{排除场景2：如"只读文件访问"}}

---

## 2. 核心原则

### 原则一：写共享文件必须原子化

**禁止的写法**：
```python
# ❌ 禁止：直接写入共享文件（读者可能读到截断内容）
path.write_text(content, encoding="utf-8")
with open(path, "w") as f:
    json.dump(data, f)

# ❌ 禁止：手动tmp+rename（无重试、无stale清理）
tmp = path.with_suffix(".tmp")
tmp.write_text(content)
os.rename(tmp, path)  # Windows上PermissionError时不重试

# ❌ 禁止：read-modify-write无原子性
content = path.read_text()
new_content = transform(content)
path.write_text(new_content)  # 竞态窗口
```

**正确的写法**：
```python
# ✅ 原子覆盖写入
from lib.atomic_write import atomic_write_text, atomic_write_json
atomic_write_text(path, content, encoding="utf-8")
atomic_write_json(path, data, ensure_ascii=False, indent=2)

# ✅ 原子read-modify-write
from lib.atomic_write import atomic_edit_text
def my_editor(content: str) -> str:
    return transform(content)
atomic_edit_text(path, my_editor, encoding="utf-8")

# ✅ 关键数据使用fsync确保持久化（~1-5ms额外开销）
atomic_write_json(path, critical_data, fsync=True)
```

### 原则二：关键路径日志必须分阶段计时

**禁止的日志写法**：
```python
# ❌ 只记录总耗时，无法定位瓶颈
t0 = time.time()
result = do_work()
_log.debug("操作完成: %.2fms", (time.time()-t0)*1000)
```

**正确的日志写法**（参考模板A/B/C）：
- 使用 `time.perf_counter()`（最高精度，不受NTP调整影响）
- 每个子阶段独立计时
- 成功用 `debug`，失败用 `warning` 并包含 `error` 和 `elapsed`
- 格式：`"操作 | key1=val1 | key2=val2 | 总耗时=%.2fms"`

### 原则三：重试必须有限次+固定退避

**禁止的重试模式**：
```python
# ❌ 无限重试（可能挂死）
while True:
    try: op(); break
    except: time.sleep(0.01)

# ❌ 忙等无退避（CPU空转）
for _ in range(100):
    try: op(); break
    except: pass

# ❌ 吞掉异常
try: op()
except: pass
```

**正确的重试模式**：
```python
# ✅ 有限次 + 固定间隔 + 失败清理
max_retries = {{默认3}}
interval_ms = {{默认10}}
last_error = None
for attempt in range(max_retries + 1):
    try:
        operation()
        return
    except OSError as e:
        last_error = e
        if attempt < max_retries:
            _log.debug("retry | attempt=%d/%d | error=%s", attempt+1, max_retries, e)
            time.sleep(interval_ms / 1000.0)
        else:
            cleanup_tmp_files()
raise last_error
```

---

## 3. 决策树：何时使用原子写入

```
写文件操作
├── 写入目标是否为进程独占临时文件？
│   ├── 是（tempfile.TemporaryDirectory() 内）→ 可直接 write_text/write_bytes
│   └── 否（共享路径/缓存/报告/配置）
│       ├── 模式？
│       │   ├── 全量覆盖 → atomic_write_bytes/text/json
│       │   ├── read-modify-write → atomic_edit_text
│       │   └── 多区域并发编辑 → 需要文件锁（避免此模式）
│       └── 数据重要性？
│           ├── 可重建（缓存/报告）→ fsync=False（默认，性能优先）
│           └── 不可重建（状态/配置）→ fsync=True（~1-5ms开销）
```

---

## 4. 日志模板

### 模板A：多阶段写入操作

```python
def save_cache(self):
    _t_start = time.perf_counter()
    try:
        _t_build = time.perf_counter()
        entries = self.build_entries()
        _build_ms = (time.perf_counter() - _t_build) * 1000

        _t_ser = time.perf_counter()
        data = json.dumps(entries).encode("utf-8")
        _ser_ms = (time.perf_counter() - _t_ser) * 1000

        _t_write = time.perf_counter()
        atomic_write_bytes(self._path, data)
        _write_ms = (time.perf_counter() - _t_write) * 1000

        _log.debug(
            "缓存保存完成 | entries=%d | build=%.2fms | "
            "serialize=%d bytes/%.2fms | atomic-write=%.2fms | 总耗时=%.2fms",
            len(entries), _build_ms, len(data), _ser_ms, _write_ms,
            (time.perf_counter() - _t_start) * 1000,
        )
    except OSError as e:
        _log.warning("缓存保存失败 | error=%s | elapsed=%.2fms",
                     e, (time.perf_counter() - _t_start) * 1000)
```

### 模板B：初始化/加载操作

```python
def load_config(self):
    _t_start = time.perf_counter()
    _t_read = time.perf_counter()
    try:
        data = json.loads(self._path.read_text(encoding="utf-8"))
        _read_ms = (time.perf_counter() - _t_read) * 1000
        _log.debug("配置加载完成 | keys=%d | read=%.2fms | 总耗时=%.2fms",
                   len(data), _read_ms, (time.perf_counter()-_t_start)*1000)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        _log.debug("配置加载失败 | reason=%s | elapsed=%.2fms",
                   e, (time.perf_counter()-_t_start)*1000)
        return None
```

### 模板C：维护/清理操作

```python
_log.debug("清理完成 | scanned=%d | cleaned=%d | errors=%d | 耗时=%.3fms",
           scanned, cleaned, errors, _t_ms)
```

### 日志格式规范

| 要素 | 规范 | 示例 |
|------|------|------|
| 分隔符 | `\|` | `"操作完成 \| key1=val1 \| key2=val2"` |
| 键名 | kebab-case | `atomic-write`, `build`, `evict` |
| 计数 | `%d` | `"entries=%d"` |
| 毫秒耗时 | `%.2fms` | `"build=%.2fms"` |
| 字节数 | `%d bytes` | `"serialize=%d bytes/%.2fms"` |
| 错误级别 | 成功=debug，失败=warning | `"保存失败 \| error=%s \| elapsed=%.2fms"` |
| 时间源 | `time.perf_counter()` | 禁止 `time.time()`（受NTP调整影响） |

---

## 5. 重试参数规范

| 参数 | 默认值 | 适用场景 | 调整建议 |
|------|--------|---------|---------|
| `max_retries` | **3** | 常规文件替换（共4次机会） | 高并发热点增至5 |
| `retry_interval_ms` | **10** | Windows文件锁冲突（AV/索引器） | 不超过50ms |
| `stale_max_age_sec` | **3600**（1小时） | tmp残留清理 | 短生命周期文件降至300s |
| `cleanup_stale` | **True** | 默认清理stale | 性能敏感路径设False |
| `fsync` | **False** | 默认性能优先 | 关键状态文件设True |

---

## 6. 临时文件命名规范

```
格式：{目标文件名}.pid{PID}.{6位随机hex}.tmp
示例：cache.json.pid12345.a3f9c2.tmp
```

- **PID**：确保不同进程的临时文件不会冲突
- **随机后缀**：6位hex（16M种可能），防止PID复用导致碰撞
- **同目录**：临时文件必须在目标文件同一目录（保证os.replace是原子操作，跨分区rename不原子）

---

## 7. 竞态条件风险分级

### 🔴 高风险：必须使用原子写入

| 场景 | 风险 | 处理方式 |
|------|------|---------|
| {{高风险1：如"多进程写入同一缓存"}} | {{风险描述}} | atomic_write_json |
| {{高风险2：如"CI脚本生成报告"}} | {{风险描述}} | atomic_write_text |
| {{高风险3：如"标记区域更新"}} | {{风险描述}} | atomic_edit_text |

### 🟡 中风险：建议使用原子写入

| 场景 | 风险 | 处理方式 |
|------|------|---------|
| {{中风险1：如"单实例脚本输出"}} | 低概率冲突 | atomic_write_text（防御性编程） |
| {{中风险2：如"文档自动生成"}} | 中断时文件损坏 | atomic_write_text |

### 🟢 低风险：可使用直接写入

| 场景 | 原因 |
|------|------|
| {{低风险1：如"tempfile.TemporaryDirectory内的文件"}} | 进程独占目录 |
| {{低风险2：如"测试fixture临时文件"}} | 测试隔离 |
| {{低风险3：如"首次创建新文件（目标不存在）"}} | 无覆盖风险 |

---

## 8. 代码审查 Checklist

审查文件写入代码时，必须逐项确认：

- [ ] 写入目标是否为共享路径？是则使用了 atomic_write 系列函数
- [ ] 是否存在 read-modify-write 循环？是则使用了 atomic_edit_text
- [ ] 临时文件名是否包含 PID 和随机后缀？禁止固定 `.tmp`
- [ ] os.replace 失败是否有重试？重试次数 ≤ 5？间隔 10-50ms？
- [ ] 重试失败是否清理临时文件？防止 tmp 泄漏
- [ ] 关键路径是否有分阶段计时日志？格式是否符合模板？
- [ ] 失败路径是否有 error 日志？包含 error 和 elapsed？
- [ ] 计时是否使用 `time.perf_counter()`？禁止 `time.time()`
- [ ] 单元测试是否覆盖？至少：成功/重试成功/重试失败清理/多进程并发
- [ ] 关键数据是否启用 `fsync=True`？

---

## 9. 测试要求

### 必测场景

| 测试场景 | 测试方法 | 优先级 |
|---------|---------|--------|
| 基本写入（bytes/text/json/encoding/overwrite/empty/large） | 常规单元测试 | P0 |
| PID唯一命名（格式验证+多进程碰撞测试） | multiprocessing | P0 |
| Stale清理（过期删除/新文件保留/unlink容错/自定义TTL） | mock mtime | P0 |
| 文件锁重试（首次成功/重试成功/耗尽清理/次数验证/间隔验证） | mock os.replace | P0 |
| 失败清理（序列化失败/replace失败/双重失败不崩溃） | mock抛出异常 | P0 |
| 多进程并发（8进程并发写入无损坏、无tmp泄漏） | multiprocessing.Pool | P0 |
| 原子编辑（基本替换/标记区域/异常传播/无残留） | 常规单元测试 | P0 |
| fsync持久化（启用fsync写入正确/无残留） | 常规单元测试 | P1 |
| 深层目录创建 | 常规单元测试 | P1 |
| 二进制数据（全字节/空字节/Unicode） | 常规单元测试 | P1 |
| 字符串路径输入兼容性 | 常规单元测试 | P2 |
| 100次连续写入无tmp累积 | 循环写入 | P2 |

### 参考实现

参见 `{{项目中的测试文件路径}}`，共 {{N}} 个测试用例。

---

## 10. API 参考

```python
from lib.atomic_write import (
    atomic_write_bytes,    # 原子写字节
    atomic_write_text,     # 原子写文本
    atomic_write_json,     # 原子写JSON
    atomic_edit_text,      # 原子编辑（read-edit-write）
)

# 原子写字节
atomic_write_bytes(
    dst: Union[str, Path],
    data: bytes,
    max_retries: int = 3,              # replace重试次数
    retry_interval_ms: int = 10,       # 重试间隔（毫秒）
    stale_max_age_sec: float = 3600,   # stale文件最大存活（秒）
    cleanup_stale: bool = True,        # 写入前清理stale
    fsync: bool = False,               # 持久化到磁盘
) -> Path

# 原子写JSON
atomic_write_json(
    dst, obj,
    encoding: str = "utf-8",
    ensure_ascii: bool = False,
    indent: int | None = 2,
    **kwargs,  # 透传给atomic_write_bytes
) -> Path

# 原子写文本
atomic_write_text(
    dst, text,
    encoding: str = "utf-8",
    **kwargs,  # 透传给atomic_write_bytes
) -> Path

# 原子编辑（read-modify-write）
atomic_edit_text(
    dst,
    editor: Callable[[str], str],  # 接收原文本返回新文本
    encoding: str = "utf-8",
    **kwargs,  # 透传给atomic_write_bytes
) -> Path
```

---

## 11. 性能数据参考

> 以下数据来自 `{{项目名称}}` 的 `{{环境描述}}` 基准测试，供新项目参考设定预期。

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 并发写入成功率 | {{如"82-95%"}} | **100%** | {{如"+18%"}} |
| 文件损坏率 | {{如"3-8%"}} | **0%** | 消除 |
| tmp文件残留 | {{如"崩溃时泄漏"}} | **0残留** | 自动清理 |
| 冷启动耗时 | {{如"15-25ms"}} | {{如"0.88ms"}} | {{如"↓94%"}} |
| 温启动耗时 | {{如"5-10ms"}} | {{如"0.26ms"}} | {{如"↓95%"}} |
| fsync额外开销 | - | ~1-5ms | 可接受 |

---

## 12. 关联资源

- 完整规范文档：{{链接到已填充的最佳实践文档}}
- 性能对比报告：{{链接到重构复盘报告}}
- 工具源码：{{链接到atomic_write.py}}
- 单元测试：{{链接到测试文件}}
- 代码审查工具：{{链接到静态检查工具/脚本}}

---

## 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| {{YYYY-MM-DD}} | 1.0 | 初始版本（基于原子写入重构经验） | {{作者}} |
| | | | |
