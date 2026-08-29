# spec-loader.toml 配置速查手册

> 配置文件路径：`.agents/config/spec-loader.toml`
> 对应代码：[spec_loader.py](../../../scripts/lib/spec_loader.py)、[spec-loader CLI](../../../scripts/spec-loader.py)

## 快速开始

```toml
# 最小可用配置（开箱即用，生产推荐）
[cache]
enabled = true

[performance]
auto_save_cache = true
```

SpecLoader 初始化时自动读取 `.agents/config/spec-loader.toml`，所有配置项均有内置默认值，配置文件中只需覆盖需要调整的项。

**配置优先级**：构造函数显式参数 > TOML配置文件 > 代码内置默认值

---

## 配置项总览

| Section | 配置项 | 类型 | 默认值 | 说明 |
|---------|--------|------|--------|------|
| `[meta]` | `version` | string | `"1.0"` | 配置文件自身版本（仅标注用） |
| | `description` | string | — | 配置描述 |
| | `last_updated` | string | — | 最后更新日期 |
| `[cache]` | `enabled` | bool | `true` | 启用磁盘持久化缓存 |
| | `dir_name` | string | `".cache"` | 缓存目录名（相对于 `.agents/`） |
| | `filename` | string | `"spec-loader.json"` | 缓存文件名 |
| | `max_entries` | int | `200` | LRU最大缓存条目数 |
| | `version` | int | `2` | 缓存格式版本号 |
| | `atomic_write` | bool | `true` | 原子写入（防缓存损坏） |
| | `mtime_precision` | float | `0.001` | mtime比对精度（秒） |
| `[layers]` | `l1b_default_stages` | [string] | `["planning","startup"]` | 默认加载L1b的阶段 |
| | `l0_specs` | [path] | `["ONBOARDING.md"]` | L0入口文件列表 |
| | `l1a_core_specs` | [path] | 见下方 | L1a核心规则文件列表 |
| | `l1b_index_specs` | [path] | 见下方 | L1b索引文件列表 |
| `[logging]` | `enable_timing_breakdown` | bool | `true` | 启用步骤级耗时分解日志 |
| | `cache_log_level` | string | `"info"` | 缓存HIT/MISS日志级别 |
| `[performance]` | `max_l2_chars` | int | 不限制 | L2最大加载字符数 |
| | `auto_save_cache` | bool | `true` | 自动保存缓存（仅dirty时） |
| | `preload_disk_cache` | bool | `true` | 启动时预加载磁盘缓存 |

---

## 各 Section 详细说明

### [meta] — 元信息

仅用于标注，不影响运行时行为。

```toml
[meta]
version = "1.0"
description = "L2渐进式披露规范加载器生产配置"
last_updated = "2026-07-12"
```

---

### [cache] — 磁盘缓存策略

基于 mtime（文件修改时间戳）的持久化缓存，缓存文件路径为 `.agents/.cache/spec-loader.json`。

**工作原理**：
1. 首次加载（冷启动）：读取规范文件内容，写入磁盘缓存
2. 后续加载（温启动）：比较磁盘文件 mtime 与缓存记录，未修改则直接复用缓存内容
3. 文件修改后自动失效：mtime 变化触发重新读取并更新缓存

| 配置项 | 取值 | 使用场景 |
|--------|------|----------|
| `enabled = true` | **生产推荐** | 跨会话复用缓存，温启动 ~0.25ms |
| `enabled = false` | 调试/排查 | 每次从磁盘读取，禁用缓存便于观察真实IO |

**max_entries 调优指南**：

| 项目规模 | 规范文件数 | 建议值 |
|----------|-----------|--------|
| 小型项目 | <20 | 50 |
| 中型项目（当前） | ~40 | 100-200 |
| 大型项目（多vendor） | 100+ | 500 |

超过 `max_entries` 时按 LRU 策略淘汰最久未访问的条目。

**version 字段使用方式**：当缓存格式发生不兼容变更（如新增字段、修改JSON结构）时，递增 `version` 值即可强制所有旧缓存失效，无需手动删除缓存文件。

**atomic_write 原子写入流程**：
1. 写入临时文件 `spec-loader.json.tmp`
2. `os.replace()` 原子替换目标文件
3. 防止写入中途崩溃导致缓存文件损坏/为空

```toml
[cache]
enabled = true
dir_name = ".cache"
filename = "spec-loader.json"
max_entries = 200       # 项目规范文件数 + 50~100 余量
version = 2             # 缓存格式升级时 +1
atomic_write = true     # 生产环境务必开启
mtime_precision = 0.001 # 1ms精度，覆盖所有主流文件系统
```

---

### [layers] — 四层渐进式披露配置

控制 L0→L1a→L1b→L2 各层的默认加载文件列表。

**四层架构**：

| 层级 | 加载时机 | 内容 | 默认加载阶段 |
|------|----------|------|-------------|
| L0 | 始终 | 入口速查（ONBOARDING.md） | 全部阶段 |
| L1a | 始终 | 核心规则（global-core-rules, capability-boundaries） | 全部阶段 |
| L1b | 按需 | 索引文档（capability-registry, context-routing, skills/README） | planning/startup |
| L2 | 任务路由 | 角色/工作流/检查清单等详细规范 | 按任务类型匹配 |

**l1b_default_stages**：控制哪些阶段默认包含L1b索引层。execution和verification阶段默认跳过L1b以减少常驻上下文。在 `load_for_task()` 中可通过 `include_l1b=True/False` 参数覆盖此设置。

**l0/l1a/l1b 文件列表**：指定各层对应的文件路径（相对于 `.agents/` 目录）。修改路径时确保文件实际存在，缺失文件会打印警告日志但不会崩溃。

```toml
[layers]
l1b_default_stages = ["planning", "startup"]

l0_specs = [
    "ONBOARDING.md",
]

l1a_core_specs = [
    "global-core-rules.md",
    "capability-boundaries.md",
]

l1b_index_specs = [
    "capability-registry.md",
    "context-routing.md",
    "skills/README.md",
]
```

---

### [logging] — 日志配置

| 配置项 | 取值 | 效果 |
|--------|------|------|
| `enable_timing_breakdown = true` | 调试/性能调优 | 输出 resolve/memcheck/lookup/mtime-stat/construct/read-io 各步骤耗时 |
| `enable_timing_breakdown = false` | **生产推荐** | 仅输出汇总日志，减少日志噪音 |
| `cache_log_level = "debug"` | 排查缓存问题 | 输出每次HIT/MISS详细信息 |
| `cache_log_level = "info"` | **生产推荐** | 输出缓存统计汇总（命中率、条目数等） |

```toml
[logging]
enable_timing_breakdown = true   # 性能调优时开启
cache_log_level = "info"         # 生产环境用info级别
```

---

### [performance] — 性能调优

**auto_save_cache**：核心优化开关。
- `true`（推荐）：`load_for_task()` 结束后仅在缓存有更新（MISS）时自动保存到磁盘，dirty flag 机制避免每次调用都触发磁盘写入
- `false`：需手动调用 `save_cache()`，适合批量加载后统一保存的场景

**preload_disk_cache**：
- `true`（推荐）：`__init__` 时一次性读取缓存文件到内存（~0.15ms开销），后续查询零IO
- `false`：首次访问缓存时懒加载，适合短暂生命周期的实例

**max_l2_chars**（可选，默认不限制）：限制单次 `load_for_task()` 加载的L2文件总字符数，防止异常任务类型匹配加载过多规范导致上下文爆炸。建议值 50000-100000。

```toml
[performance]
# max_l2_chars = 50000          # 取消注释以限制L2加载量
auto_save_cache = true          # dirty flag优化，必开
preload_disk_cache = true       # 预加载，必开
```

---

## 常用配置场景

### 场景1：开发调试（禁用缓存，详细日志）

```toml
[cache]
enabled = false

[logging]
enable_timing_breakdown = true
cache_log_level = "debug"

[performance]
auto_save_cache = false
```

### 场景2：高并发服务端（最小IO）

```toml
[cache]
enabled = true
max_entries = 500
atomic_write = true

[logging]
enable_timing_breakdown = false
cache_log_level = "info"

[performance]
auto_save_cache = true
preload_disk_cache = true
```

### 场景3：CI/测试环境（快速验证）

```toml
[cache]
enabled = false       # CI环境不依赖持久化缓存

[performance]
preload_disk_cache = false
auto_save_cache = false
```

### 场景4：缓存格式升级后强制重建

```toml
[cache]
version = 3           # 递增版本号，旧缓存自动失效
```

---

## CLI 命令参考

配置完成后，可通过以下CLI命令验证和调试：

```bash
# 运行基准测试，查看冷/温启动耗时和加速比
python .agents/scripts/spec-loader.py benchmark

# 查看缓存统计（版本、条目数、命中率）
python .agents/scripts/spec-loader.py cache-stats

# 清除磁盘缓存（强制下次冷启动）
python .agents/scripts/spec-loader.py cache-clear

# 审计所有TASK_ROUTING路由的L2文件是否存在
python .agents/scripts/spec-loader.py audit

# 模拟加载指定任务（execution阶段，仅输出清单）
python .agents/scripts/spec-loader.py task "代码审查"

# 模拟加载指定任务（planning阶段，含L1b索引，输出内容）
python .agents/scripts/spec-loader.py task "代码审查" --stage planning --content
```

---

## 性能基线（当前生产配置）

| 指标 | 数值 | 条件 |
|------|------|------|
| 冷启动（无磁盘缓存） | ~0.90ms | SSD, Windows, Python 3.13 |
| 温启动（磁盘缓存命中） | ~0.25ms | mtime命中，dirty=False |
| 内存缓存命中（连续调用） | ~0.02ms | 同一实例内第2次起 |
| 冷/温加速比 | 3.6x | benchmark综合平均 |
| 缓存文件大小 | ~15KB | 13个条目 |
| 磁盘写入频率 | 仅MISS时 | dirty flag机制 |

---

## 并发10x场景下的IO瓶颈分析

当前温启动0.25ms的性能在并发量提升10倍时，IO瓶颈点如下：

### 瓶颈1：原子写入竞态（影响正确性）

**场景**：多个SpecLoader实例同时冷启动或遇到MISS，并发写入缓存文件。
- 原子写入（tmp+rename）保证文件不损坏，但**最后写入者覆盖先前写入者的新条目**
- 结果：部分缓存条目丢失，后续实例需重新读取源文件（性能回退，非崩溃）
- **缓解**：dirty flag大幅减少了写入频率（温启动时不写盘），仅冷启动/MISS时触发

### 瓶颈2：初始化时缓存文件读放大

**场景**：10x并发意味着更多新实例初始化，每个实例在`__init__`中读取整个缓存JSON。
- 当前缓存文件~15KB（13条目），即使100并发读取，SSD吞吐完全可承受
- 若`max_entries=500`（大型项目），缓存文件增长到~60KB，仍微不足道
- **结论**：非瓶颈点

### 瓶颈3：mtime stat() 系统调用

**场景**：每次`load_for_task`调用对每个所需文件执行`os.path.getmtime()`。
- execution阶段约5个stat调用，planning阶段约8个
- stat()是VFS元数据操作，OS内核缓存后约1-5μs/次
- 即使1000次/秒调用，stat总开销约25-40μs，可忽略
- **结论**：非瓶颈点

### 瓶颈4：Windows文件锁（平台特定）

**场景**：Windows上`os.replace()`原子替换时，若另一个进程恰好正在读取该文件，可能短暂失败。
- 当前代码无文件锁重试机制
- 但dirty flag将写入频率降至极低，碰撞概率极小
- **建议**：若部署到高并发Windows服务端，可在`_save_disk_cache`中添加重试逻辑（3次，间隔10ms）

### 综合结论

在dirty flag优化下，**温启动路径完全零磁盘写入**（仅mtime stat调用），IO瓶颈几乎消除。真正需要关注的是**冷启动风暴**：当缓存版本升级或缓存文件被清除时，大量并发实例同时冷启动会导致：
1. 并发读取相同源文件（OS页缓存可缓解）
2. 并发写入缓存竞态（最后写入者获胜，可能丢失条目）

**建议预防措施**：
- 生产环境避免在高并发时段执行`cache-clear`
- 大版本升级时考虑分批重启，避免冷启动风暴
- 如部署为长期运行服务，可在服务启动时预热缓存（提前调用一次`load_for_task`）
