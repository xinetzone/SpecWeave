---
id: "invoke-task-dual-backend-load"
title: "Invoke Task 双后端（SDK 优先 + CLI Fallback）模式"
type: "code-pattern"
date: "2026-09-08"
maturity: "L1-draft"
source: "jpman-client `invoke load` 任务实现 (2026-09-08)"
related_patterns:
  - "invoke-layered-namespace-tasks"
  - "multi-strategy-auto-discovery"
  - "ffi-fallback-diagnostics"
  - "env-var-five-layer-protection"
tags: ["invoke", "sdk-fallback", "cli", "container", "podman", "python", "dual-backend", "graceful-degradation", "context-manager"]
validation_count: 2
reuse_count: 0
---

# Invoke Task 双后端（SDK 优先 + CLI Fallback）模式

## 模式概述

在基于 Python invoke 的 CLI 工具中，容器操作（镜像加载、容器启停、镜像列表等）同时提供**声明式 SDK** 和**命令式 CLI** 两种后端，形成"SDK 优先 → CLI 兜底"的双后端架构。SDK 后端提供类型安全、结构化返回值、细粒度错误处理；CLI 后端作为零依赖的保底路径，确保在没有 SDK 或连接失败时功能仍可运行。

该模式的核心设计是：**所有对外 API 函数签名不暴露后端差异**，调用方只看到统一的返回结果，无需关心实际走了哪条路径。

## 触发场景

- Python CLI 工具需要操作容器运行时（Podman/Docker），且需跨多种环境（WSL2/原生/Podman Machine/TCP）
- SDK 是可选依赖（`pyproject.toml` 中为可选安装组），但需要在可用时提供更好体验
- 环境不可控（CI/CD、多平台分发），需要优雅降级而非硬失败
- 操作涉及网络/进程调用，存在连接失败、版本不兼容等不确定性

**不适用于**：
- SDK 为必填依赖（强制安装，不存在降级场景）
- 纯 CLI 工具（无 SDK 层）
- 同步性要求极高、不允许任何额外开销的场景

## 核心步骤

### 第一步：定义统一的结果类型（Result Dataclass）

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class LoadImageResult:
    loaded: bool
    tags: list[str] = field(default_factory=list)
    id: str = ""
    message: str = ""
```

**设计要点**：
- `loaded: bool` 是通用信号量，调用方可用 `if result.loaded:` 统一判断
- 结构化字段（`tags`、`id`）供上层消费，`message` 供用户可见
- 无论走 SDK 还是 CLI，返回同类型对象，调用方不感知后端差异

### 第二步：编写双后端私有函数（`_xxx_via_sdk` / `_xxx_via_cli`）

```python
def _load_via_sdk(client, tar_path: Path) -> LoadImageResult:
    """通过 podman-py SDK 加载镜像 tar。"""
    try:
        loaded = client.images.load(file_path=tar_path)
        tags: list[str] = []
        img_id = ""
        if isinstance(loaded, list) and loaded:
            first = loaded[0]
            img_id = getattr(first, "short_id", "") or getattr(first, "id", "")
            tags = list(getattr(first, "tags", []) or [])
        elif hasattr(loaded, "__iter__") and not isinstance(loaded, (str, bytes, list)):
            items = list(loaded)
            if items:
                first = items[0]
                img_id = getattr(first, "short_id", "") or getattr(first, "id", "")
                tags = list(getattr(first, "tags", []) or [])
        return LoadImageResult(
            loaded=True, tags=tags, id=img_id,
            message=f"[SDK] 已加载镜像（file_path={tar_path}）",
        )
    except Exception as e:
        return LoadImageResult(loaded=False, message=f"[SDK] 加载失败: {e}")


def _load_via_cli(c: Context, tar_path: Path) -> LoadImageResult:
    """通过 podman load 命令加载镜像 tar。"""
    runtime = detect_runtime()
    result = run_cmd(c, f'{runtime} load -i "{tar_path}"', pty=False, echo=True)
    if result is None or result.exited != 0:
        return LoadImageResult(loaded=False, message="[CLI] load 命令执行失败")
    stdout = getattr(result, "stdout", "") or ""
    tags: list[str] = []
    for line in stdout.splitlines():
        if "Loaded image" in line:
            name = line.split(":", 1)[1].strip()
            tags.append(name)
    return LoadImageResult(loaded=True, tags=tags, message="[CLI] 镜像加载完成")
```

**设计要点**：
- 私有函数以 `_` 开头，不对外暴露
- SDK 函数接收已确认可用的 `client` 对象（由上层管理生命周期）
- CLI 函数接收 `Context` 对象（invoke 的任务上下文）
- **异常处理策略**：SDK 函数内部 `except Exception` 捕获并将失败包装为 `loaded=False` 的结果，不向上抛异常——让上层决定是继续降级还是报错

### 第三步：编写客户端探测上下文管理器

```python
from contextlib import contextmanager
from typing import Optional, Generator

@contextmanager
def get_client() -> Generator[Optional[Client], None, None]:
    """获取后端客户端的上下文管理器（SDK 不可达时 yield None）。

    策略优先级：环境变量显式 URL → WSL2 socket → Podman Machine → TCP 回环 → None
    """
    if not sdk_available():
        yield None
        return

    candidates = sdk_base_url_candidates(strategy)
    client = None

    try:
        for cand in candidates:
            this_client = None
            try:
                this_client = _connect_attempt(cand)
                if this_client is not None and this_client.ping() is True:
                    client = this_client
                    break
            except Exception:
                _log_attempt_failure(cand)
            finally:
                _close_safe(this_client)

        if client is not None:
            yield client
            return

        # 全部失败：输出降级提示
        print("[INFO][降级] SDK路径不可用 → 走CLI fallback")
        yield None
    finally:
        _close_safe(client)
```

**设计要点**：
- 返回 `Optional[Client]`：`None` 表示 SDK 不可用，调用方自行决定 CLI 路径
- 使用 `yield None` 而非 `return` 进入 finally 块，确保 `client.close()` 被正确调用
- 每轮失败的详细信息仅 `DEBUG` 级别输出，避免干扰普通用户

### 第四步：编写统一对外 API 函数

```python
def load_image(c: Context, tar_path: Path) -> LoadImageResult:
    """从本地 tar.gz 加载镜像，SDK 优先失败则走 CLI。"""
    if not tar_path.exists():
        return LoadImageResult(loaded=False, message=f"镜像文件不存在: {tar_path}")

    print(f"[Load] 从 {tar_path} 加载镜像...")

    sdk_result: Optional[LoadImageResult] = None
    with get_client() as client:
        if client is not None:
            sdk_result = _load_via_sdk(client, tar_path)
            if sdk_result.loaded:
                print(sdk_result.message)
                if sdk_result.tags:
                    print(f"[Load] Tags: {', '.join(sdk_result.tags)}")
                return sdk_result
            # SDK 连上了但加载本身失败 → 仍降级 CLI
            print(f"[INFO][降级] SDK加载失败 → 走CLI fallback: {sdk_result.message}")

    cli_result = _load_via_cli(c, tar_path)
    if cli_result.loaded:
        print(cli_result.message)
        if cli_result.tags:
            print(f"[Load] Tags: {', '.join(cli_result.tags)}")
    else:
        print(cli_result.message)
    return cli_result
```

**设计要点**：
- 对外 API 不接受"选择哪个后端"的参数，后端选择是内部决策
- `with get_client() as client:` 块内判断 `client is not None`，自然分流
- 返回类型始终为 `LoadImageResult`，调用方代码无需改动

### 第五步：在 Invoke Task 装饰器中调用统一 API

```python
from invoke import task, Context
from invoke.exceptions import Exit

@task(
    help={
        "path": "镜像 tar.gz 路径。未指定时自动搜索缓存目录",
        "cache-dir": "镜像缓存目录",
    }
)
def load(c: Context, path: str | None = None, cache_dir: str | None = None) -> None:
    """从本地 tar.gz 加载镜像（SDK 优先，CLI fallback）。"""
    # 1. 确定 tar 路径
    tar_path = _resolve_tar_path(path, cache_dir)
    if tar_path is None:
        raise Exit(1, "未找到镜像文件")

    # 2. 调用统一 API
    result = load_image(c, tar_path)

    # 3. 统一错误处理
    if not result.loaded:
        raise Exit(1, result.message)
```

## 模式扩展：同类操作复用同一架构

本模式不止适用于镜像加载，整个容器操作集合均可复用：

| 操作 | SDK 函数 | CLI 函数 | 对外 API |
|------|----------|----------|---------|
| 镜像加载 | `_load_via_sdk` | `_load_via_cli` | `load_image()` |
| 镜像列表 | `_list_images_sdk` | `_list_images_cli` | `list_images()` |
| 容器启动 | `_run_via_sdk` | `_run_via_cli` | `run_container()` |
| 容器停止 | `_stop_via_sdk` | `_stop_via_cli` | `stop_container()` |
| 容器状态 | `_status_via_sdk` | `_status_via_cli` | `status_container()` |

所有对外 API 签名保持一致，调用方（`manage.py` 中的 `@task` 函数）无感知切换。

## 反模式与陷阱

| 陷阱 | 后果 | 正确做法 |
|------|------|---------|
| SDK 异常直接向上抛出 | CLI fallback 被绕过，功能完全中断 | SDK 私有函数内部捕获异常，返回 `loaded=False` |
| 对外 API 暴露 `backend: str` 参数 | 调用方被迫了解内部实现，API 耦合度高 | 后端选择完全封装在内部，对外 API 签名不变 |
| `get_client()` 返回 `Client` 而非 `Optional[Client]` | 无法区分"SDK 不可用"和"连接失败"两种情况 | 返回 `Optional[Client]`，`None` 触发 CLI 路径 |
| CLI fallback 不检查 SDK 是否真的失败了 | SDK 部分成功（如连上 daemon 但加载失败）时可能丢失信息 | 区分"连接失败"（yield None）和"操作失败"（loaded=False）两种降级场景 |
| 在 SDK 成功时打印 `[INFO][降级]` | 误导用户以为发生了降级 | 仅在 SDK 失败后才打印降级提示，成功路径不打此标记 |
| 两个后端返回不同的数据结构 | 调用方需要写两套结果处理逻辑 | 通过 Result dataclass 统一返回结构 |
| `podman load -i <path>` 传大文件经 REST API | WSL2 Podman machine 下 ~300MB+ tar.gz 触发 `EOF` 错误（连接意外关闭） | 改用 `type file \| podman load` stdin pipe，绕过 REST API path 传输 |

## 迁移验证

- ✅ jpman-client（jupyter-podman-rootless 消费端）：`invoke load` / `invoke run` / `invoke stop` / `invoke status` / `invoke images` / `invoke clean` 六条命令全部通过此模式验证，覆盖 SDK 可用/不可用两种环境
- ✅ jpman-client CLI fallback 大文件 EOF 修复（2026-09-08）：`podman load -i <path>` 对 ~352MB 镜像在 WSL2 REST API 路径下触发 EOF，改用 `type file | podman load` stdin pipe 后绕过 REST API，问题解决
- ⏳ 等待第二案例：其他容器管理 CLI 工具或类似 SDK+CLI 双后端的项目

## 适用条件

- 语言/框架：Python + invoke（可泛化至其他任务 runner 如 Task/Just/Make）
- SDK 性质：可选依赖（`try/except ImportError` 保护），不影响主安装路径
- 后端一致性：SDK API 和 CLI 命令的输出语义需要能映射到统一结果类型
- 不适用场景：SDK 为必填依赖、没有等价 CLI 命令、或对性能极其敏感不允许额外开销

## 升级标准（candidate → 正式）

当满足以下任一条件时升级为正式 L2 模式：
1. 在第二个独立项目中验证"SDK 优先 + CLI fallback"架构的必要性
2. 发现"SDK 异常未捕获导致 fallback 失效"的故障至少 2 次，形成反模式验证
3. 验证该模式在非容器领域（数据库操作、对象存储、ML 推理等）的适用性
