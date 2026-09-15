---
id: "jupyter-invoke-tasks-rules"
title: "Invoke任务开发规范"
source: "AGENTS.md#嵌套路由关系 + README.md#三层后端编排架构"
---
# Invoke任务开发规范（jupyter-podman-rootless）

## 基础约定

- 任务管理工具：invoke（Python任务执行工具）
- 任务定义目录：`tasks/`
- 入口文件：`tasks/__init__.py`（任务命名空间配置）
- Python环境：需要Python ≥3.10运行invoke任务
- 三层后端自动降级：podman-compose（优先）→ podman-py SDK → CLI fallback
- 后端选择对用户透明，同一命令自动选择最优后端
- 路径自动转换：WSL2下Windows路径自动转换为/mnt/...格式

## tasks目录结构

```
tasks/
├── __init__.py        ← 任务入口与命名空间配置（核心命令+model.*+registry.*命令）
├── utils.py           ← 构建端垫片：平台/进程/容器工具唯一实现位于 jpman_common，本文件仅再导出（另保留 MIRROR_CHOICES）
├── client.py          ← Podman/Docker client wrapper：连接层符号从 jpman_common.connection 再导出；本文件保留 builder 专属 compose 探测与 sdk_*_kwargs
├── compose_backend.py ← podman-compose后端封装
├── build.py           ← 镜像构建任务
├── manage.py          ← 容器生命周期管理（run/stop/status/clean）
├── interact.py        ← 容器交互（shell/logs/exec）
├── model.py           ← ML模型管理任务（push/pull/config/pack/extract）
├── registry.py        ← 本地OCI registry生命周期（up/down；compose profile的等价替代）
└── container.py       ← 向后兼容聚合模块（re-export所有子模块任务）
```

## pyproject.toml配置

invoke依赖和extras配置：

```toml
[project]
name = "jupyter-podman-rootless"
version = "0.1.0"
dependencies = [
    "invoke>=2.0",
    "jpman-common",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
sdk = ["podman>=5.0.0"]
compose = ["podman-compose>=1.0"]
full = ["podman-compose>=1.0", "podman>=5.0"]
model = ["omlmd", "olot[oras-py]"]
```

> **构建后端**：scikit-build-core 构建**纯 Python wheel**（`wheel.packages=["src/jpman_builder"]`、
> `wheel.cmake=false`），无 CMakeLists.txt、无 `[tool.scikit-build.cmake]` 段。
>
> **连接层位置（2026-09 重构后）**：`get_client`/`sdk_available`/`podman_sock_path`/
> `APIError`/`PodmanNotFound` 的唯一实现位于组内共享包 `jpman_common.connection`
> （apps/containers/shared）；`tasks/client.py` 只做再导出，六个调用点
> （build/container/interact/manage/model/registry）仍经 `tasks/client.py`
> 导入，路径不变。builder 专属逻辑保留在 `tasks/client.py`：
> `compose_available()`/`compose_unavailable_reason()`（`shutil.which("podman-compose")`
> 与 `os.name != "nt"` 双条件）与 `sdk_run_kwargs()`/`sdk_build_kwargs()`。
> `tasks/utils.py` 同理为 `jpman_common`（proc/platform_paths/containers）的再导出垫片。

安装方式：
```bash
pip install -e .              # 基础安装（CLI fallback）
pip install -e ".[compose]"   # +podman-compose（推荐）
pip install -e ".[full]"      # +podman-py SDK
pip install -e ".[model]"     # +OMLMD/OLOT（宿主机直接使用ML命令）
```

## 命名空间规范

### 核心命令（根命名空间）

| 命令 | 功能 | 所在文件 |
|------|------|---------|
| `build` | 构建镜像 | build.py |
| `run` | 启动容器 | manage.py |
| `stop` | 停止并删除容器 | manage.py |
| `status` | 查看容器状态 | manage.py |
| `shell` | 进入容器Shell | interact.py |
| `logs` | 查看容器日志 | interact.py |
| `exec` | 在容器中执行命令 | interact.py |
| `clean` | 清理资源 | manage.py |

### container.*命名空间（别名，用于命名空间隔离）

所有核心命令也可通过`invoke container.<命令>`访问：
- `invoke container.build`
- `invoke container.run`
- 等等...

实现方式：在`__init__.py`中创建ContainerNamespace并add_task所有核心任务。

### model.*命名空间（ML模型管理）

| 命令 | 功能 | 所在文件 |
|------|------|---------|
| `model.push` | 推送模型到OCI registry | model.py |
| `model.pull` | 从OCI registry拉取模型 | model.py |
| `model.config` | 查询OCI模型元数据配置 | model.py |
| `model.pack` | 打包模型为KServe ModelCar镜像 | model.py |
| `model.extract` | 从ModelCar镜像提取模型目录 | model.py |

### registry.*命名空间（本地OCI registry）

| 命令 | 功能 | 所在文件 |
|------|------|---------|
| `registry.up` | 启动本地OCI registry（`registry:2`） | registry.py |
| `registry.down` | 停止并删除registry容器（`--volumes` 连数据卷一起删） | registry.py |

**为什么必须有这一组命令**：该服务原只能由 compose 的 `--profile registry` 启动，而
podman-compose 在 Windows 原生宿主上不可用（见 `client.py::compose_available()`），
导致 Windows 上没有启动路径。`registry.py` 以 SDK→CLI 两层实现同一服务，
其容器名、数据卷名、端口、环境变量、重启策略均与 `compose.yaml` 的 `model-registry`
服务**对齐**（卷名同为 `<project>_registry-data`），故两种启动方式共享同一份数据。
改动这些常量时必须两处同步——见其文件头「与 compose.yaml 保持同步的常量」。

## 三层后端架构（client.py）

### 后端检测优先级

```
1. podman-compose后端（优先）
   ↓ 未安装podman-compose
2. podman-py SDK后端
   ↓ 未安装podman
3. CLI fallback（保底）
   - 通过subprocess调用podman/docker命令
   - 零依赖，任何有podman/docker的环境都能工作
```

### client.py核心接口

连接层符号由 `jpman_common.connection` 实现、`tasks/client.py` 再导出；
`get_client` 是**上下文管理器**（`@contextmanager`），全部连接候选失败时
yield `None`（调用方降级 CLI），不是返回统一后端对象的工厂：

```python
from jpman_builder.tasks.client import get_client, sdk_available

with get_client() as client:
    if client is None:
        ...  # 降级到 CLI（run_cmd 调 podman/docker）
    else:
        ...  # podman-py SDK 调用（client.containers / client.images ...）
```

后端选择逻辑：
1. podman-compose 可用性由 builder 专属 `compose_available()` 探测：
   `shutil.which("podman-compose")` 二进制存在 **且** `os.name != "nt"`
   （Windows 原生 ntpath 路径语义错配恒不可用，原因见函数 docstring 与
   `compose_unavailable_reason()`；不是「尝试 import podman_compose」）
2. SDK 可用性由 `jpman_common.connection.sdk_available` 给出（try-import
   podman 发生在共享包内，任务模块不得各自 try-import）
3. 最后 fallback 到 CLI（`run_cmd` 子进程调 podman/docker）
4. SDK 连接候选（P0 环境变量 → P1 WSL 9P → P2 Podman Machine → P3 tcp）
   全失败时 `get_client()` yield None，由调用给友好降级，不抛异常

> **UID 推导历史教训（C-I5，连接层旧坑）**：旧本地实现曾把宿主运行时 UID
> **硬编码为 1000**（`_podman_runtime_uid` 无条件默认），在 UID=1006 的原生
> Linux 宿主上生成不存在的 `/run/user/1000/podman/podman.sock` 挂载源，
> podman run 硬失败 exit=125（statfs no such file）。该实现已删除，改由
> `jpman_common.connection.host_runtime_uid()` 四级链推导：
> ① 显式 `PODMAN_RUNTIME_UID` → ② POSIX `$XDG_RUNTIME_DIR` 末段 →
> ③ `os.getuid()` → ④ Windows 原生回落 `"1000"`。新增代码一律调用共享层，
> 禁止再次硬编码 UID；`podman_sock_path()`/`ensure_host_podman_socket()`
> 同样只认共享层这一份事实源。

### compose_backend.py封装

podman-compose后端提供声明式编排能力：
- 支持多文件覆盖（`-f compose.yaml -f compose.dev.yaml`）
- 支持profiles（`--profile registry`）
- 环境变量从.env文件自动加载
- 自动处理WSL2路径转换

## 工具函数规范（utils.py）

> **实现位置（2026-09 重构后）**：下列工具的唯一实现位于组内共享包
> `jpman_common`（proc.py / platform_paths.py / containers.py），
> `tasks/utils.py` 仅 `from jpman_common import ...` 再导出，保持
> `from .utils import ...` 路径稳定；builder 专属常量仅有 `MIRROR_CHOICES`。
> 修改实现须改共享包并同步 shared/tests，禁止在 builder 本地复制分叉。

### 经垫片提供的工具函数（实际导出名以 tasks/utils.py 为准）

1. **路径转换**：`to_posix_path(path)` / `normalize_path_str(path)`
   - Windows路径（`D:\project`）→ POSIX（`/mnt/d/project`）
   - 已在POSIX环境下直接返回
   - 自动检测是否在WSL2环境

2. **随机字符串**：`generate_random_string(length: int = 16)`
   - 生成密码安全的随机字符串
   - 默认16位用于密码，32位用于token
   - 使用secrets模块（非random模块）

3. **运行时检测/命令执行/容器只读探测**：
   - `detect_runtime()`：检测容器运行时（podman/docker）
   - `run_cmd(c, cmd, ...)`：统一子进程执行（Windows 走无空格 pwsh 7 路径，见下）
   - `check_runtime_ready()`：daemon 预检
   - `container_exists()` / `container_running()`：只读状态探测
   - podman-compose 是否可用：`tasks/client.py::compose_available()`（builder 专属）；
     podman-py 是否可导入：`jpman_common.connection.sdk_available`

4. **日志输出**：任务层直接 `print` 中文状态行（历史上曾规划
   info/ok/warn/error 彩色助手，现代码库以 `[OK]/[WARN]` 前缀 print 为准；
   shell 脚本侧日志库见 `scripts/lib/logging.sh`）

## 任务编写规范

### 基本结构

```python
from invoke import task
from .utils import run_cmd, detect_runtime
from .client import get_client

@task(help={
    "tag": "镜像标签（默认：jupyter-podman-rootless:latest）",
    "apt-mirror": "APT镜像源：official/tuna/aliyun",
})
def build(ctx, tag="jupyter-podman-rootless:latest", apt_mirror="official",
          conda_mirror="official", pip_mirror="official", no_cache=False):
    """构建镜像"""
    print(f"[Build] Building image {tag}...")
    # 优先 SDK；get_client 为上下文管理器，全候选失败 yield None → CLI 降级
    with get_client() as client:
        if client is not None:
            client.images.build(...)  # podman-py SDK
        else:
            run_cmd(ctx, f"{detect_runtime()} build ...")  # CLI fallback
    print(f"[OK] Image {tag} built successfully!")
```

### 参数规范

- 参数名使用snake_case（Python风格），自动映射到命令行的`--kebab-case`
- 提供合理的默认值（与Containerfile/entrypoint中的默认值一致）
- 必须通过`help`参数提供参数说明
- 布尔参数使用`--flag/--no-flag`形式（invoke自动处理）

### 输出规范

- 任务开始时输出info日志说明正在做什么
- 关键步骤输出进度
- 任务完成时输出ok日志说明结果
- 错误时输出error日志并抛出异常（或sys.exit(1)）
- 自动生成的密码/token在启动成功后以醒目的方式打印
- 访问信息（SSH/Jupyter URL）必须清晰展示给用户

## 命令兼容性保证

- **命令名稳定**：不轻易修改现有命令名，新增功能通过新命令或新参数添加
- **参数向后兼容**：新增参数必须提供默认值，不破坏现有调用
- **输出格式稳定**：密码/token/URL的输出位置和格式保持一致，便于脚本解析
- **三层后端透明**：用户无需关心使用哪个后端，同一命令参数和输出格式一致

## Windows shell 配置（硬约束）

`__init__.py` 在 Windows 上把 `config["run"]["shell"]` 设为 **PowerShell 7（pwsh）**，两个条件都必须满足：

1. **必须是 PowerShell 7，不能用 cmd.exe**：`run_cmd` 构造的命令是 POSIX 风格——单引号包裹参数（`--format '{{.Names}}'`、`bash -c '{cmd}'`）与 `&&` 串联（`cd X && olt_car.py pack ...`）。cmd.exe 把单引号当普通字符、把 `&&` 当命令分隔符，会静默破坏这些命令。
2. **shell 路径不得含空格**：invoke 以 `Popen(cmd, shell=True, executable=shell)` 启动，Windows 下 Python 会拼成 `f'{shell} /c "{cmd}"'`，而 `executable` **不能被引号包裹**（加了会 `OSError [WinError 123]`）。Store 版 PowerShell 的 `shutil.which("pwsh")` 返回 `C:\Program Files\WindowsApps\...\pwsh.EXE`（含空格），被拆断后**所有** `c.run` 命令都失败；而 `warn=True` 会把它静默吞掉，症状表现为「整条 CLI 兜底层不可用、容器永远报不存在」。

因此必须用 `_resolve_space_free_pwsh()` 取 **App Execution Alias** 路径（`%LOCALAPPDATA%\Microsoft\WindowsApps\pwsh.exe`，无空格）。

**排查方法**：若怀疑 shell 失效，直接跑 `python -c "from invoke import Context; r=Context().run('podman --version', hide=True, warn=True); print(r.ok, r.stdout, r.stderr)"`——`ok=False` 且 stderr 出现 pwsh 用法帮助即为本问题。

## 验证清单

新增/修改invoke任务后必须验证：
- [ ] `invoke --list`正确列出所有命令（15个：8核心+5model+2registry）
- [ ] `invoke <command> --help`参数说明完整
- [ ] podman-compose可用时使用compose后端
- [ ] 未安装podman-compose时自动降级到podman-py
- [ ] 未安装podman-py时自动降级到CLI
- [ ] **CLI兜底层真能执行**：`Context().run('podman --version', hide=True, warn=True).ok` 为 `True`（Windows 上 shell 配置错误会让它静默失效，见「Windows shell 配置」）
- [ ] WSL2环境下Windows路径自动转换为/mnt/路径
- [ ] 随机密码/token生成正确（密码16位，token32位）
- [ ] `invoke build`构建成功
- [ ] `invoke run`启动成功并打印访问信息
- [ ] `invoke status`正确显示容器状态
- [ ] `invoke shell`可进入容器
- [ ] `invoke stop`可停止并删除容器
- [ ] `invoke clean --image`可清理容器和镜像
- [ ] `invoke registry.up`启动后 `curl http://localhost:5000/v2/_catalog` 返回 200，且卷名为 `<project>_registry-data`（与 compose 对齐）
- [ ] `invoke registry.down` 删除容器但保留卷；`--volumes` 连卷一起删
