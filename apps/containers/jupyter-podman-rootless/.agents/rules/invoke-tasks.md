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
├── utils.py           ← 工具函数（运行时检测/路径转换/随机字符串/日志）
├── client.py          ← Podman/Docker client wrapper（三层后端优先级检测）
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
]

[project.optional-dependencies]
compose = ["podman-compose>=1.0"]
full = ["podman-compose>=1.0", "podman>=5.0"]
model = ["omlmd", "olot[oras-py]"]
```

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

```python
from jpman_builder.tasks.client import get_client

client = get_client()  # 自动检测最优后端

# 统一接口（所有后端实现相同方法）
client.build(...)      # 构建镜像
client.run(...)        # 运行容器
client.stop(...)       # 停止容器
client.status(...)     # 查看状态
client.exec(...)       # 执行命令
client.logs(...)       # 查看日志
```

后端选择逻辑：
1. 首先检查`podman-compose`是否可用（尝试import podman_compose）
2. 其次检查`podman`模块是否可用（podman-py SDK）
3. 最后fallback到CLI（检查podman/docker命令是否在PATH中）
4. 都不可用时抛出友好错误提示安装依赖

### compose_backend.py封装

podman-compose后端提供声明式编排能力：
- 支持多文件覆盖（`-f compose.yaml -f compose.dev.yaml`）
- 支持profiles（`--profile registry`）
- 环境变量从.env文件自动加载
- 自动处理WSL2路径转换

## 工具函数规范（utils.py）

### 必须提供的工具函数

1. **路径转换**：`to_posix_path(path: str) -> str`
   - Windows路径（`D:\project`）→ WSL2路径（`/mnt/d/project`）
   - 已在POSIX环境下直接返回
   - 自动检测是否在WSL2环境

2. **随机字符串**：`random_string(length: int = 16) -> str`
   - 生成密码安全的随机字符串
   - 默认16位用于密码，32位用于token
   - 使用secrets模块（非random模块）

3. **运行时检测**：
   - `detect_runtime() -> Literal["podman", "docker"]`：检测容器运行时
   - `is_wsl2() -> bool`：检测是否在WSL2环境
   - `is_podman_compose_available() -> bool`：检测podman-compose是否安装
   - `is_podman_py_available() -> bool`：检测podman-py是否安装

4. **日志输出**：彩色日志（使用colorama或ANSI转义码）
   - `info(msg)`：蓝色[INFO]
   - `ok(msg)`：绿色[OK]
   - `warn(msg)`：黄色[WARN]
   - `error(msg)`：红色[ERROR]

## 任务编写规范

### 基本结构

```python
from invoke import task
from .utils import info, ok, error, to_posix_path
from .client import get_client

@task(help={
    "tag": "镜像标签（默认：jupyter-podman-rootless:latest）",
    "apt-mirror": "APT镜像源：official/tuna/aliyun",
})
def build(ctx, tag="jupyter-podman-rootless:latest", apt_mirror="official",
          conda_mirror="official", pip_mirror="official", no_cache=False):
    """构建镜像"""
    client = get_client()
    info(f"Building image {tag}...")
    client.build(
        tag=tag,
        build_args={
            "APT_MIRROR": apt_mirror,
            "CONDA_MIRROR": conda_mirror,
            "PIP_MIRROR": pip_mirror,
        },
        no_cache=no_cache,
    )
    ok(f"Image {tag} built successfully!")
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
