---
title: 文件I/O并发安全统一库架构演进报告
date: 2026-07-12
updated: 2026-07-12
type: architecture-evolution
source: 分散锁逻辑扫描 → atomic_write原子写入 → io_safety统一库 → 冗余清理
tags: [architecture, concurrency, atomic-write, retry-pattern, staged-timer, code-consolidation, windows, dead-code-removal]
---

# 文件I/O并发安全统一库架构演进报告

## 1. 演进背景

### 1.1 问题发现

在 L2 渐进式披露加载器性能优化过程中，通过并发压测（30进程×10轮）暴露了四类文件I/O风险：

| 风险类型 | 根因 | 影响 |
|----------|------|------|
| 竞态写入 | MDI生成器 `base.py` 使用 `path.write_text()` 直接写入共享路径 | 并发时读者可见截断/半写内容 |
| Windows文件锁 | `os.replace()` 在AV/索引器短暂持锁时抛出 `PermissionError` | Windows环境偶发写入失败 |
| 持久化缺失 | 关键状态文件无 `fsync`，系统崩溃时可能丢失数据 | 缓存版本不一致 |
| 性能黑盒 | 关键I/O路径无分阶段计时，无法定位瓶颈 | 优化缺乏数据支撑 |

### 1.2 审计发现

对整个 `.agents/scripts/` 目录（120+ Python模块，308+脚本）进行了全量扫描，结论：**架构基线良好**——所有文件写入路径已统一收敛到 `atomic_write.py`，无散落重复实现。但缺少面向开发者的上层API（装饰器、计时上下文管理器）。

## 2. 演进三阶段

```mermaid
flowchart LR
    subgraph S1 ["阶段1：直接写入（历史）"]
        A1["open/write_text<br/>无保护"]
        A2["手动try/except<br/>无统一重试"]
        A3["print调试<br/>无结构化日志"]
    end
    subgraph S2 ["阶段2：atomic_write（底层原语）"]
        B1["atomic_write_bytes/text/json/edit_text<br/>原子写入原语"]
        B2["内建Windows锁重试<br/>3次×10ms"]
        B3["tmp命名PID+随机后缀"]
        B4["stale自动清理"]
        B5["fsync可选刷盘"]
    end
    subgraph S3 ["阶段3：io_safety统一库（本次最终态）"]
        C1["staged_timer<br/>分阶段计时上下文管理器"]
        C2["retry_on_lock<br/>通用重试装饰器"]
        C3["write_file_with_retry<br/>语义化便捷接口"]
        C4["冗余清理<br/>删除薄包装层+死代码"]
        C5["lib/__init__.py统一导出"]
    end
    S1 -->|"识别竞态→抽取公共模块"| S2
    S2 -->|"上层API封装+收敛冗余"| S3
    style S1 fill:#fdd,stroke:#a33
    style S2 fill:#ffd,stroke:#aa3
    style S3 fill:#dfd,stroke:#3a3
```

### 阶段1：直接写入模式（历史状态）

- 各模块自行使用 `path.write_text()` / `open(path, 'w')` 写入文件
- Windows文件锁问题靠"重试运气"或忽略
- 崩溃后临时文件无清理机制
- 日志格式不统一，缺乏耗时数据

### 阶段2：atomic_write 原子写入模块（底层原语）

创建 [atomic_write.py](../../scripts/lib/atomic_write.py)，解决核心原子性问题：

| 能力 | 实现 |
|------|------|
| 原子替换 | `os.replace()` 保证POSIX/Windows原子性 |
| 唯一临时文件名 | `{name}.pid{PID}.{hex}.tmp`，防止多进程冲突 |
| Windows锁重试 | 捕获OSError，3次×10ms固定间隔退避 |
| Stale文件清理 | >1小时的残留tmp自动清理 |
| 失败清理兜底 | replace失败时best-effort删除tmp |
| fsync刷盘 | 关键文件可开启（+1~5ms开销） |
| 原子编辑 | `atomic_edit_text` 实现安全read-modify-write |

此阶段为**底层原语层**，直接使用需要自行组合：重试逻辑不可复用到非原子写入场景，计时日志各模块手写。

### 阶段3：io_safety 统一库（本次最终态）

创建 [io_safety.py](../../scripts/lib/io_safety.py)，在 atomic_write 之上提供**面向开发者的高层组合API**：

| 组件 | 类型 | 解决的问题 |
|------|------|-----------|
| `staged_timer` | 上下文管理器 | 分阶段计时→统一格式日志（`DEBUG/WARNING`、各阶段ms、总耗时、key=value字段） |
| `retry_on_lock` | 装饰器 | 通用文件锁重试，可装饰**任意**文件操作函数（不限于atomic_write），支持cleanup回调 |
| `write_file_with_retry` | 便捷函数 | 语义化接口名，降低新成员理解成本 |

**模块边界明确**：
- `atomic_write.py` → 原子写入原语（bytes/text/json/edit），不做高层封装
- `io_safety.py` → 高层组合工具（timer/retry/语义别名），不重复导出atomic_write函数
- [lib/__init__.py](../../scripts/lib/__init__.py) → 统一门面，支持 `from lib import staged_timer, retry_on_lock, atomic_write_bytes`

**冗余清理**（本次优化收尾）：
- 移除 [spec_loader.py](../../scripts/lib/spec_loader.py) 中未使用的 `_atomic_replace_with_retry` 向后兼容薄包装器
- 移除 io_safety.py 中原有的4个 `atomic_write_*` 转发包装器（生产代码零引用，直接从 atomic_write 导入），保持模块单一职责
- 更新相关测试导入源，确保测试正确指向定义源

## 3. 架构质量指标

### 3.1 覆盖率审计

全项目递归扫描（覆盖 lib/、mdi/、sg_dashboard/、forum_bot/、trae_edge_case_handler/ 等所有子目录）：

| 检查项 | 结果 |
|--------|------|
| 散落的 `os.replace`/`os.rename` 非规范调用（生产代码） | **0处**（仅在atomic_write.py规范实现中） |
| 手动PermissionError/OSError重试循环（文件I/O场景） | **0处** |
| 绕过公共API直接导入 `_atomic_replace_with_retry` | **0处** |
| 未使用的向后兼容包装器/薄转发层 | **0处**（已清理） |
| 使用原子写入API的生产模块 | **12+**（spec_loader、api_docs、markdown、各generator、sg_dashboard等） |
| 架构结论 | ✅ 完全集中，无重复实现，无死代码，符合DRY原则 |

### 3.2 测试覆盖

| 测试文件 | 用例数 | 覆盖场景 |
|----------|--------|----------|
| [test_atomic_write.py](../../scripts/tests/test_atomic_write.py) | 70个 | 基础写入、唯一命名、stale清理、重试、并发、fsync、二进制边缘、深层路径、原子编辑、快速顺序写入 |
| [test_windows_file_lock.py](../../scripts/tests/test_windows_file_lock.py) | 7个 | **真实msvcrt.locking加锁**、锁超时清理、脉冲锁、装饰器、失败日志、便捷API |
| [test_spec_loader.py](../../scripts/tests/test_spec_loader.py) | 53个 | 分层加载、磁盘缓存、mtime失效、并发保存、原子重试（间接覆盖atomic_write） |
| **合计** | **130个** | 含真实Windows文件锁场景（非仅mock） |

### 3.3 性能数据

| 操作 | 耗时 | 开销来源 |
|------|------|----------|
| `atomic_write_bytes` 默认 | 与直接write相当（<0.1ms额外） | tmp文件创建+rename |
| `atomic_write_bytes` + `fsync=True` | +1~5ms | 强制磁盘刷盘 |
| `staged_timer` 上下文管理 | <0.01ms | perf_counter计时 |
| `retry_on_lock` 无冲突时 | <0.001ms | 装饰器包装开销 |

冷启动优化（spec_loader磁盘缓存）：15-25ms → 0.88ms（-94%），温启动：5-10ms → 0.26ms（-95%）。

## 4. 设计原则提炼

本次演进验证了以下架构原则：

1. **底层原语与上层API分层**：`atomic_write.py` 提供原子替换原语，`io_safety.py` 提供开发者友好的组合API，两层职责清晰不交叉
2. **集中式能力管理**：文件锁/重试逻辑完全集中在两个共享库中，零散落实现，降低维护成本
3. **默认安全、可选性能**：默认启用重试+清理保证安全，`fsync=False` 默认值保证性能，关键场景可开启持久化
4. **真实场景测试**：Windows平台测试使用真实 `msvcrt.locking()` 加锁，而非仅mock，确保回归测试能捕获真实锁冲突
5. **统一日志格式**：`staged_timer` 强制分阶段输出格式，避免各模块自行打印不可聚合的日志
6. **避免冗余转发层**：每个模块只导出自己独有的能力，不做薄包装转发（导入路径应该指向定义源而非转发层）

## 5. 演进前后对比

| 维度 | 阶段1（直接写入） | 阶段2（atomic_write） | 阶段3（io_safety 最终态） |
|------|------------------|----------------------|-------------------|
| 原子性保证 | ❌ 无 | ✅ os.replace原子替换 | ✅ 同左 |
| Windows锁重试 | ❌ 偶发失败 | ✅ 内建3次重试 | ✅ +可装饰任意函数 |
| tmp文件清理 | ❌ 泄漏 | ✅ 自动stale清理 | ✅ 同左 |
| 分阶段计时 | ❌ 黑盒 | ❌ 各模块手写 | ✅ staged_timer统一 |
| 持久化选项 | ❌ 无 | ✅ fsync可选 | ✅ 同左 |
| 原子编辑 | ❌ 读-改-写竞态 | ✅ atomic_edit_text | ✅ 同左 |
| 重试复用范围 | ❌ 无 | ❌ 仅限atomic_write | ✅ 任意文件操作函数 |
| API导入方式 | 散乱 | 子模块导入 | ✅ lib包统一门面 |
| 冗余包装层 | N/A | ❌ 有（spec_loader薄包装+io_safety转发层） | ✅ 已清理 |
| 测试用例 | 0 | 70个 | 130个（含真实锁+spec_loader） |
| 文档 | 无 | 代码注释 | ✅ README+架构报告 |

## 6. 复用指南

### 6.1 新脚本快速接入

```python
import sys, json, os, logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import staged_timer, atomic_write_bytes, retry_on_lock
_log = logging.getLogger(__name__)

def save_cache(path: Path, data: dict) -> None:
    with staged_timer(_log, "缓存保存完成", path=str(path)) as t:
        with t.stage("serialize"):
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        with t.stage("write"):
            atomic_write_bytes(path, raw)

@retry_on_lock(max_retries=3, interval_ms=10)
def replace_output(src: Path, dst: Path) -> None:
    os.replace(src, dst)
```

### 6.2 关键决策点

| 场景 | 推荐API | fsync | 重试次数 |
|------|---------|-------|---------|
| 频繁更新的缓存文件 | `atomic_write_bytes` | `False` | 默认3次 |
| 关键状态/版本文件 | `atomic_write_bytes` | `True` | 默认3次 |
| 自定义文件操作（非write） | `@retry_on_lock` 装饰器 | N/A | 按需配置 |
| 需要计时的复合操作 | `staged_timer` 上下文管理器 | N/A | N/A |
| 读-改-写场景 | `atomic_edit_text` | 按需 | 默认3次 |
| 语义化写入（降低理解成本） | `write_file_with_retry` | 按需 | 可配置 |

## 7. 遗留与后续

本次演进**无遗留问题**，全量测试130/130通过。扫描中发现3个未启用的独立子系统（约900行），属于独立历史残留，不在本次io-safety范围内：

| 子系统 | 位置 | 行数 | 说明 |
|--------|------|------|------|
| 知识库分级加密 | knowledge_crypto/security/integrity.py | ~600行 | 从未启用的WIP特性；`InputValidator.sanitize_filename()`被使用需先迁移 |
| flexloop沙箱 | vendor_sandbox.py | ~180行 | 为从未接入的vendor子系统预留 |
| PowerShell编码工具 | powershell.py（3个函数） | ~130行 | .ps1编码校验能力，从未被调用 |

未来可扩展方向：
- 可选的指数退避重试策略（当前为固定间隔，适合<10ms的AV锁场景）
- 跨平台文件锁（`fcntl.flock` on Linux/macOS）
- 基于 `staged_timer` 数据的自动性能异常检测
