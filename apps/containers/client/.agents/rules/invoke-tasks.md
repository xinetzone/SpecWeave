# Invoke 任务开发规范（jupyter-podman-client 消费端）

> 适用范围：`src/jpman_client/tasks/` 目录下 5 个模块的新增/修改：`__init__.py` / `utils.py` / `client_core.py` / `env_in_container.py` / `manage.py`。
> 本规则是 **消费端** 版本；构建端（jupyter-podman-rootless）有自己独立的 invoke-tasks.md，两者不混用。

## 1. 基础约定

| 项 | 值 |
|----|----|
| 任务管理工具 | invoke（`pip install -e .` 后使用） |
| 任务定义目录 | `src/jpman_client/tasks/`（pyproject.toml `[tool.invoke] package="jpman_client.tasks"`） |
| 入口文件 | `src/jpman_client/tasks/__init__.py`（命名空间配置）；根 `tasks.py` 仅为转发层（`from jpman_client.tasks import *`） |
| Python 版本 | 运行环境 ≥ 3.14（与 pyproject.toml `requires-python` 对齐） |
| 编排后端层级 | 两层自动降级：**podman-py SDK（优先）→ CLI fallback**（没有 podman-compose 层） |
| 后端选择对用户 | 完全透明：同一命令（`invoke run`/`load`/`stop`...）自动选最优后端 |
| 路径自动转换 | 宿主 Windows 绝对路径（如 `D:/spaces`）→ `/mnt/d/spaces`（容器内 POSIX 形式） |

## 2. tasks 目录结构（单一职责）

```
src/jpman_client/tasks/
├── __init__.py            ← 命名空间配置：根命令（load/images/run/stop/status/clean）+ container.* 别名 + env.* 自举命名空间
├── utils.py               ← 无状态工具函数：ContainerConfig、路径转换（A 维）、SDK 探测（B 维）、WSL 探测、Windows 诊断
├── client_core.py         ← 两层后端核心：get_client()（SDK + CLI fallback）、load_image、list_images、image_exists
├── env_in_container.py    ← env.* 自举任务：build-layer / run-cmd / shell；PODMAN_SERVICE_BOOT 常量（容器内 podman service 自举）
└── manage.py              ← 对外 invoke 任务：6 个根命令 + container.* 别名；_load_env_overrides(.env → os.environ)
```

### 2.1 模块职责边界（禁止跨层调用）

| 模块 | 可以 import | 禁止 import |
|------|------------|------------|
| `__init__.py` | 从 `manage.py` / `env_in_container.py` import 任务函数，再 ns(`container`, ...) / ns(`env`, ...) 聚合 | 禁止直接从 `client_core.py`/`utils.py` import 内部实现 |
| `manage.py` | 从 `client_core.py` import 对外 API（load_image / run_container / stop_container ...）；从 `utils.py` import ContainerConfig / 纯工具函数 | 禁止从 `__init__.py` 回环 import；禁止直接调 `PodmanClient` |
| `client_core.py` | 从 `utils.py` import 连接策略、诊断、路径工具；直接 `import podman`（SDK 探测 ImportError 时降级） | 禁止依赖 `manage.py` 或 `__init__.py` |
| `env_in_container.py` | 从 `utils.py` import `detect_runtime` / `run_cmd` / 路径工具；只走 CLI 子进程 | 禁止 import `manage.py`/`client_core.py`/`__init__.py`；**禁止调用 podman-py SDK**（避免循环依赖） |
| `utils.py` | Python 标准库 + 三方库（podman/dotenv/invoke.exceptions）；无本地模块依赖 | 禁止 import 同目录下的其他 4 个模块，避免循环依赖 |

## 3. 两层后端架构（SDK → CLI fallback）

### 3.1 核心承诺：get_client() 行为不可变

```python
@contextmanager
def get_client() -> Iterator[Optional[PodmanClient]]:
    ...
```

**100% 不可变的行为契约**（修改任何一点 = C4 违反打回）：

1. **返回类型**：`Optional[PodmanClient]`；不是 `PodmanClient`，不是 `None` 抛异常
2. **仅在所有候选路径都失败时才 yield `None`**；任何一条候选 ping 成功都 yield client
3. **yield 前必须 `client.ping()`**；不能只构造不 ping，否则 SSH/Machine 场景在后续调用才炸，诊断链路断裂
4. **每条候选失败后必须 `_close_safe(client)`**；尤其是 SSH 分支，防止 `ssh -N -L` 子进程僵尸
5. **每轮失败必须结构化记录 `attempts` 列表**（source / base_url / hint / exc_type / exc_msg）；不能裸 raise 吞信息
6. **最终必须调用 `windows_diagnose_hint(exc_type, exc_msg)`** 叠加匹配 **W-I1~W-I3**（宿主 Windows）+ **C-I1/C-I2**（容器内坑，平台无关）；输出格式固定：`[i/N] source=...  base_url=...  错误=...  提示=...`。⚠️ C-I2 分支（EACCES，容器内 devuser 无权访问宿主直通 socket）**必须置于 `platform.system() != "Windows"` 平台守卫之前**，否则容器内（Linux）场景永不命中
7. **候选顺序严格 P0→P1→P2→P3**（见 `utils.py::sdk_base_url_candidates`）；不能私自调换顺序导致 Linux 场景先尝试 WSL 路径拖慢
8. **sdk_strategy_from_env() 返回值严格白名单归一化**：`{auto, legacy, wsl, machine}`；策略=`legacy` 时**必须**走「只调一次 from_env，失败即 None」等价于 v0.0.x 旧行为，方便生产热回滚

### 3.2 CLI fallback 调用链

`get_client() yield None` 后，`manage.py` / `client_core.py` 中以下函数**必须**有等价的 `podman` 子进程实现（不可直接 return None 了事）：

| 函数 | SDK 路径（client 非 None 时） | CLI fallback 路径（client is None 时） |
|------|------------------------------|-------------------------------------|
| `load_image(ctx, tar_path)` | `client.images.import_image(...)` | `subprocess.run([runtime, "load", "-i", tar_path], check=True)` |
| `list_images(ctx)` | `client.images.list()` | `subprocess.run([runtime, "images", ...], capture_output=True, text=True)` 然后 parse 输出 |
| `image_exists(ctx, tag)` | `client.images.get(tag)`, 404=False | `subprocess.run([runtime, "inspect", tag], ...)` returncode == 0 |
| `run_container(ctx, cfg)` | `client.containers.run(...)` 挂载/端口/环境转容器 API 字段 | 拼接 CLI 参数 `-v` / `-p` / `-e` / `--device` / `--security-opt` / `--cgroupns` 完全一致 |
| `stop_container(ctx, name)` | `client.containers.get(name).stop(timeout=30) + remove(v=True)` | `podman stop -t 30 <name> ; podman rm -f -v <name>` |
| `status_container(ctx, name)` | `client.containers.get(name).status + ports` | `podman inspect <name> + json.loads(parse)` 或 `podman ps -a --filter name=...` |
| `clean_container(ctx, name/tag/image/volume)` | `containers.prune()` + 条件删镜像/卷 | `podman rm -f -v` + `podman rmi` + `podman volume rm` |

⚠️ CLI fallback 中 `[runtime, ...]` 的 runtime 必须来自 `utils.py::detect_runtime()`（优先 podman，回退 docker）；
**禁止** 任何地方硬编码 `"podman"`。

⚠️ **运行时透传参数必须由 `utils.py::build_passthrough_spec(cfg)` 统一产出**，SDK（`_sdk_run_kwargs`）
与 CLI（`_run_via_cli`）只允许消费同一份 spec，**禁止两条路径各自拼接**——否则极易出现
「SDK 支持某开关、CLI 不支持」的不一致（C8 A/B 维度分离之外的第三条隐式约束）。

## 4. 命名空间规范（`__init__.py`）

`src/jpman_client/tasks/__init__.py` 必须同时提供三套入口（人类用户习惯短命令；集成调用习惯容器前缀；容器内自举习惯 env.* 前缀）：

### 4.1 根命名空间（人类驾驶员）

```python
from .manage import (load as image_load, images as list_images,
                     run as container_run, stop as container_stop,
                     status as container_status, clean as container_clean)
from invoke import Collection

ns = Collection()
ns.add_task(image_load, "load")
ns.add_task(list_images, "images")
ns.add_task(container_run, "run")
ns.add_task(container_stop, "stop")
ns.add_task(container_status, "status")
ns.add_task(container_clean, "clean")
```

### 4.2 container.* 聚合命名空间（自动化集成）

```python
container_ns = Collection("container")
container_ns.add_task(image_load, "load")
container_ns.add_task(list_images, "images")
container_ns.add_task(container_run, "run")
container_ns.add_task(container_stop, "stop")
container_ns.add_task(container_status, "status")
container_ns.add_task(container_clean, "clean")

ns.add_collection(container_ns)
```

### 4.3 env.* 自举环境命名空间（容器内环境）

```python
env_ns = Collection("env")
env_ns.add_task(env_in_container.build_layer, "build-layer")
env_ns.add_task(env_in_container.run_cmd_, "run-cmd")
env_ns.add_task(env_in_container.shell, "shell")
ns.add_collection(env_ns)
```

| env.* 命令 | 参数签名（`*` 表示可选） | 说明 |
|-----------|----------------------|------|
| `invoke env.build-layer` | `--tag *T` / `--base-image *I` / `--no-cache` | 基于 client 根目录 Containerfile.client 构建容器内自举叠加层镜像 |
| `invoke env.run-cmd` | `--cmd CMD` / `--tag *T` / `--name *N` / `--workspace *W` / `--cache-dir *D` / `--keep` / `--extra-mount *M` | 在自举容器内执行单条命令（rootless 三必需 + `/workspace` 与 `/workspace/.image-cache` 双挂载） |
| `invoke env.shell` | `--tag *T` / `--name *N` / `--workspace *W` / `--cache-dir *D` | 进入自举容器交互式 bash shell |

⚠️ `env.*` 三个任务**只走 CLI 子进程**（`utils.detect_runtime()` + `run_cmd()`），**禁止调用 podman-py SDK**；`PODMAN_SERVICE_BOOT` 常量在容器内自举 podman service（bootstrap 以 `--entrypoint /usr/bin/tini` 跳过 `entrypoint.sh::setup_podman()`，故 daemon 需自行拉起）。

### 4.4 命令兼容性保证

| 根命令 | container.* 别名 | 参数签名（`*` 表示可选） |
|-------|-----------------|----------------------|
| `invoke load` | `invoke container.load` | `--path *tar` / `--cache-dir *dir` |
| `invoke images` | `invoke container.images` | （无参数） |
| `invoke run` | `invoke container.run` | `--name N --tag T --ssh-port P --jupyter-port P --workspace W --user-password PW --jupyter-token TK --ssh-public-key KEY --grant-sudo/--no-grant-sudo --no-detach --host-network --wayland --gpu --usb --dbus` |
| `invoke stop` | `invoke container.stop` | `--name N` |
| `invoke status` | `invoke container.status` | `--name N` |
| `invoke clean` | `invoke container.clean` | `--name N --tag T --volume --image` |

**新增参数规则**：任何在 `ContainerConfig` 中出现的字段，`invoke run` 必须有对应的长参数 `--kebab-case`（下划线→中划线）；
命令行参数的优先级最高，必须覆盖 `.env` 和 ContainerConfig 默认值（`_merge_config` 已实现优先级链，修改时不得重写）。

## 5. P0 安全约束（违反打回）

| # | 内容 |
|---|------|
| C3（根） | **所有启动路径必须硬编码 rootless 三必需**：`--device /dev/fuse` + `--security-opt label=disable` + `--cgroupns=host`；**严禁 `--privileged`**。不能放参数里可配置，必须是源码硬编码死在 `ContainerConfig.host_args_defaults()` 里 |
| C4（根） | `get_client()` 只有所有候选都失败才 `yield None`；不能任何一条失败就提前返回，也不能成功后继续尝试其他路径 |
| S1 | 所有 subprocess 调用必须 `check=True` 或显式判断 returncode；不得 `check=False` 然后只 stdout 不 stderr，导致错误被吞 |
| S2 | 容器名 `cfg.name` 必须做 shell 安全白名单校验（`re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", name)`）；不能包含 `;`/`&`/`|`/空格 等命令注入字符；同样适用于 `cfg.image` tag 字段 |
| S3 | 挂载卷源路径必须先 `Path(...).expanduser().resolve()` 再转 POSIX；不能接相对路径直接拼 `-v` |
| S4 | 自动生成的 `USER_PASSWORD`/`JUPYTER_TOKEN` 必须使用 `secrets.token_urlsafe(16)` / `secrets.token_hex(32)`（强加密随机），不能用 `random.choices` 或 uuid4（可预测） |
| S5 | `podman load -i` / `podman import` 的 tar_path 必须先 `exists() and is_file()` 抛 Exit 再调用子进程；不能让 podman 子进程自己报"file not found"，导致用户分不清是 tar 不存在还是 daemon 连不上 |

## 6. 测试与验证

- 静态语法：`python -m py_compile src/jpman_client/tasks/*.py`（无 SyntaxError，全部通过）
- Lint/类型：VS Code GetDiagnostics（五文件零告警）
- 功能冒烟（任何任务修改后必跑 3 条）：
  1. `invoke --list`：命名空间加载无 ImportError
  2. `invoke images`：SDK 可用→显示表格；SDK 不可用→自动 CLI fallback 同样显示表格（不能直接崩，哪怕是空表）
  3. `PODMAN_CLIENT_SDK_STRATEGY=legacy invoke images`：逃生舱 legacy 等价行为确认（调用路径不同但输出格式一致）
