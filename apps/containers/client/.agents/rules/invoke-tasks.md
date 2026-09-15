# Invoke 任务开发规范（jupyter-podman-client 消费端）

> 适用范围：`src/jpman_client/tasks/` 目录下现有 9 个模块的新增/修改：
> `__init__.py` / `utils.py` / `client_core.py` / `env_in_container.py` /
> `manage.py`（根命名空间五模块）+ `overlay_core.py`（数据驱动栈编排内核）
> + `quant.py` / `xmnn.py` / `monetize.py`（三个声明式栈模块）。
> **组内共享层**：连接层 / 进程 / 平台路径 / 容器只读工具已迁至
> `apps/containers/shared` 的 `jpman_common` 包（消费端与构建端两端共享；
> 连接层单一事实源 = `jpman_common.connection`，`import podman` 只允许
> 出现在该包）；client 侧 `utils.py` / `client_core.py` 只做再导出垫片与
> client 专属逻辑（透传 spec、ContainerConfig、镜像加载、WSL compose
> 桥接、host key 等），修改连接行为一律改共享包。
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
├── __init__.py            ← 命名空间配置：根命令（load/images/save/run/stop/status/clean 共 7 个）+ container.* 别名 + env.* 自举 + quant/xmnn/monetize 三栈命名空间
├── utils.py               ← client 专属层：ContainerConfig、透传 spec、跨平台 load 命令（image_load_cli_command）、WSL compose 桥接（run_in_wsl_bridge）、host key；jpman_common 通用工具再导出垫片
├── client_core.py         ← 两层后端核心：load_image/save_image、list_images、image_exists；get_client 等连接能力自 jpman_common.connection 再导出
├── env_in_container.py    ← env.* 自举任务：build-layer / run-cmd / shell；PODMAN_SERVICE_BOOT 常量（容器内 podman service 自举）
├── manage.py              ← 对外 invoke 任务：7 个根命令（load/images/save/run/stop/status/clean）+ container.* 别名；_load_env_overrides(.env → os.environ)
├── overlay_core.py        ← 数据驱动栈编排内核：StackSpec/SourceMount/SmokeSpec/TaskDocs + gates/prepare_env/compose_argv/run_compose/残留自愈/smoke_stack + make_stack_tasks 六任务工厂（零栈知识、禁 import podman）
├── quant.py               ← 声明式栈模块：QUANT_SPEC + TASKS=make_stack_tasks(...) + 6 任务别名（88 行，无编排函数）
├── xmnn.py                ← 声明式栈模块：XMNN_SPEC + 6 工厂任务 + build_tvm/wheel 两个栈内 exec 长任务（双 cp314 ABI 契约）
└── monetize.py            ← 声明式栈模块：MONETIZE_SPEC + 6 工厂任务 + build_native/wheel 两个栈内 exec 长任务（单一 cp314 GIL）
```

> 共享实现不在本目录：`apps/containers/shared/src/jpman_common/`
> （platform_paths / proc / containers / connection / _win32_transcode），
> 本目录通过 `jpman_common` 与 `jpman_common.connection` 消费，不得复制私有副本。

### 2.1 模块职责边界（禁止跨层调用）

| 模块 | 可以 import | 禁止 import |
|------|------------|------------|
| `__init__.py` | 从 `manage.py` / `env_in_container.py` import 任务函数，再 ns(`container`, ...) / ns(`env`, ...) 聚合 | 禁止直接从 `client_core.py`/`utils.py` import 内部实现 |
| `manage.py` | 从 `client_core.py` import 对外 API（load_image / run_container / stop_container ...）；从 `utils.py` import ContainerConfig / 纯工具函数 | 禁止从 `__init__.py` 回环 import；禁止直接调 `PodmanClient` |
| `client_core.py` | 从 `jpman_common.connection` import 连接层（get_client / APIError / podman_sock_path / 诊断等，client 侧只做再导出与消费）；从 `utils.py` import client 专属工具 | 禁止直接 `import podman`（连接层 import 只允许在 jpman_common）；禁止依赖 `manage.py` 或 `__init__.py` |
| `env_in_container.py` | 从 `utils.py` import `detect_runtime` / `run_cmd` / 路径工具（再导出自 jpman_common）；只走 CLI 子进程 | 禁止 import `manage.py`/`client_core.py`/`__init__.py`；**禁止调用 podman-py SDK**（避免循环依赖） |
| `utils.py` | Python 标准库 + invoke.exceptions + `jpman_common` / `jpman_common.connection`（平台/进程/容器只读/连接层再导出垫片）；client 专属逻辑保留本文件 | 禁止 import 同目录下的其他实现模块，避免循环依赖；禁止复制连接层私有副本 |
| `overlay_core.py` | `.manage` 的私有函数（`_load_env_overrides` / `_project_root`）、`.utils`（run_cmd/run_in_wsl_bridge/to_posix_path/check_runtime_ready 等）、`jpman_common` | **禁止 import quant/xmnn/monetize 具体栈模块、禁止出现具体栈名/栈路径；禁止 `import podman`** |
| `quant.py` / `xmnn.py` / `monetize.py` | 仅从 `.overlay_core` import StackSpec 与内核 helper（xmnn/monetize 另用 invoke 的 Context/task） | **禁止 `import podman`；禁止跨栈 import 另两个栈模块**；同构编排逻辑一律走内核，不在栈模块复制 |

## 3. 两层后端架构（SDK → CLI fallback）

### 3.1 核心承诺：get_client() 行为不可变

```python
@contextmanager
def get_client() -> Iterator[Optional[PodmanClient]]:
    ...
```

> 实现位置（2026-09 重构后）：`get_client` / `sdk_base_url_candidates` /
> `host_runtime_uid` / `podman_sock_path` / `host_runtime_dir` /
> `ensure_host_podman_socket` / `sdk_strategy_from_env` /
> `windows_diagnose_hint` 等连接层符号的**单一事实源**在
> `apps/containers/shared` 的 `jpman_common.connection`；client 侧
> `client_core.py` 仅做再导出垫片（既有 `from .client_core import get_client`
> 路径仍可用）。下列 8 条行为承诺原文有效，改动需同时改共享包与其测试。

**100% 不可变的行为契约**（修改任何一点 = C4 违反打回）：

1. **返回类型**：`Optional[PodmanClient]`；不是 `PodmanClient`，不是 `None` 抛异常
2. **仅在所有候选路径都失败时才 yield `None`**；任何一条候选 ping 成功都 yield client
3. **yield 前必须 `client.ping()`**；不能只构造不 ping，否则 SSH/Machine 场景在后续调用才炸，诊断链路断裂
4. **每条候选失败后必须 `_close_safe(client)`**；尤其是 SSH 分支，防止 `ssh -N -L` 子进程僵尸
5. **每轮失败必须结构化记录 `attempts` 列表**（source / base_url / hint / exc_type / exc_msg）；不能裸 raise 吞信息
6. **最终必须调用 `windows_diagnose_hint(exc_type, exc_msg)`** 叠加匹配 **W-I1~W-I3**（宿主 Windows）+ **C-I1/C-I2**（容器内坑，平台无关）；输出格式固定：`[i/N] source=...  base_url=...  错误=...  提示=...`。⚠️ C-I2 分支（EACCES，容器内 devuser 无权访问宿主直通 socket）**必须置于 `platform.system() != "Windows"` 平台守卫之前**，否则容器内（Linux）场景永不命中
7. **候选顺序严格 P0→P1→P2→P3**（见 `jpman_common.connection.sdk_base_url_candidates`）；不能私自调换顺序导致 Linux 场景先尝试 WSL 路径拖慢
8. **sdk_strategy_from_env() 返回值严格白名单归一化**：`{auto, legacy, wsl, machine}`；策略=`legacy` 时**必须**走「只调一次 from_env，失败即 None」等价于 v0.0.x 旧行为，方便生产热回滚

### 3.2 CLI fallback 调用链

`get_client() yield None` 后，`manage.py` / `client_core.py` 中以下函数**必须**有等价的 `podman` 子进程实现（不可直接 return None 了事）：

| 函数 | SDK 路径（client 非 None 时） | CLI fallback 路径（client is None 时） |
|------|------------------------------|-------------------------------------|
| `load_image(ctx, tar_path) -> LoadImageResult` | `client.images.load(file_path=tar_path)`（SDK 自行 open 直读，零内存拷贝；**禁止**传 file-like） | **平台分流**：命令字符串只能由 `utils.image_load_cli_command(runtime, tar_path)` 构造，再交 `run_cmd(warn=True, pty=False)` 执行——POSIX（Linux/WSL2 内/macOS/容器内）= `<runtime> load -i "<tar>"`；Windows 原生 = `type "<tar>" \| <runtime> load`（cmd.exe 管道）。成功判定与错误翻译见下方「load 专项契约」 |
| `list_images(ctx)` | `client.images.list()` | `subprocess.run([runtime, "images", ...], capture_output=True, text=True)` 然后 parse 输出 |
| `image_exists(ctx, tag)` | `client.images.get(tag)`, 404=False | `subprocess.run([runtime, "inspect", tag], ...)` returncode == 0 |
| `run_container(ctx, cfg)` | `client.containers.run(...)` 挂载/端口/环境转容器 API 字段 | 拼接 CLI 参数 `-v` / `-p` / `-e` / `--device` / `--security-opt` / `--cgroupns` 完全一致 |
| `stop_container(ctx, name)` | `client.containers.get(name).stop(timeout=30) + remove(v=True)` | `podman stop -t 30 <name> ; podman rm -f -v <name>` |
| `status_container(ctx, name)` | `client.containers.get(name).status + ports` | `podman inspect <name> + json.loads(parse)` 或 `podman ps -a --filter name=...` |
| `clean_container(ctx, name/tag/image/volume)` | `containers.prune()` + 条件删镜像/卷 | `podman rm -f -v` + `podman rmi` + `podman volume rm` |

⚠️ CLI fallback 中 `[runtime, ...]` 的 runtime 必须来自 `jpman_common.detect_runtime()`（utils 再导出；优先 podman，回退 docker）；
**禁止** 任何地方硬编码 `"podman"`。

⚠️ **`load` 的喂入方式必须平台分流（2026-09-12 事故固化，违反=复现 exit=125）**：命令只能由
`utils.py::image_load_cli_command(runtime, tar_path)` 产出——**POSIX 用 `load -i`，Windows 原生用 `type |` 管道**。
两条路径各有硬约束，禁止互相"统一"：
- POSIX 严禁 `type file | podman load`：`type` 在 bash/zsh/dash 都是"显示命令类型"内建（不是 Windows cmd 的读文件命令），
  管道送出的是文本/空流，podman 必报 `payload does not match any of the supported image formats`；
- POSIX 也不要用 `cat file | podman load`：podman 3.4.x 的 stdin 路径对未压缩 docker-archive 同样误报上述错误（同文件 `-i` 正常，实测）；
- Windows 原生保留 `type |` 管道：`-i`/REST path 经 Windows→WSL2 远距 daemon 传超大镜像有 EOF 历史实测。

⚠️ **运行时透传参数必须由 `utils.py::build_passthrough_spec(cfg)` 统一产出**，SDK（`_sdk_run_kwargs`）
与 CLI（`_run_via_cli`）只允许消费同一份 spec，**禁止两条路径各自拼接**——否则极易出现
「SDK 支持某开关、CLI 不支持」的不一致（C8 A/B 维度分离之外的第三条隐式约束）。

⚠️ **B-scheme socket 路径必须来自 `jpman_common.connection.host_runtime_uid()` 单一事实源**（`podman_sock_path()` /
`host_runtime_dir()` 均消费它，禁止任何调用方重新拼 `/run/user/<uid>` 或硬编码 1000）。
推导优先级：`PODMAN_RUNTIME_UID` 显式覆盖 → POSIX `$XDG_RUNTIME_DIR` 末段 → `os.getuid()` →
Windows 原生回落 1000。`invoke run` 在 `check_runtime_ready()` 之后必须调用
`ensure_host_podman_socket()`：原生 Linux 上 socket 缺失时自动 `systemctl --user start podman.socket`
（10s 超时、best-effort、容器内/非 podman/非 Linux 一律放行），失败 fail-fast 抛 **C-I5** 指引。
C-I5（必选核心 socket）与 C-I3（opt-in 透传资源）的诊断分流：异常文本含 `podman.sock` → C-I5；
`passthrough_diagnose_hint()` 对 `podman.sock` 路径必须返回空串，严禁误报"去掉 --wayland/--gpu 开关"。

### 3.3 load 专项契约（`manage.load` → `client_core.load_image`）

`invoke load` 的完整调用链与判定语义（任何重构必须逐项保持等价）：

1. **任务层（`manage.py::load`）前置顺序不可调换**：
   `_load_env_overrides()`（同步 `IMAGE_CACHE_DIR` 到 os.environ）→ 定位缓存目录 →
   `find_latest_image_tar()`（双扩展名 `*.tar.gz` / `*.tar`，按 mtime 取最新）→
   `validate_manifest_integrity()`（manifest.txt 存在时校验 SIZE/SHA256，失败直接 Exit）→
   最后才进 `load_image()`。
2. **函数层（`load_image`）预检先行**：先 `tar_path.exists()`（不存在直接返回
   `LoadImageResult(loaded=False)`），再 `check_runtime_ready()`——daemon 不可达时**禁止**启动
   大文件加载（POSIX 的 `-i` / Windows 的 `type |` 都会先白做一轮 GB 级 IO）。
3. **后端降级两级**：SDK `images.load(file_path=...)` 成功即返回；**SDK 能连通但加载本身失败
   也要降级 CLI**（打印统一 `[INFO][降级]` 前缀），不能因一次 API 错误中断。
4. **CLI 成功判定不以退出码为准**：Windows cmd 管道退出码不可靠；以 stdout 是否含子串
   `"Loaded image"` 判定（同时兼容 podman 3.x 的 `Loaded image(s):` 与 4/5.x 的
   `Loaded image:`），命中行按 `:` 切出镜像名写入 `LoadImageResult.tags`。
5. **已知错误必须翻译成可执行指引（C-I 诊断体系，禁止裸 exit 码）**：
   - 命中 `cannot connect to podman` / `actively refused it` / `nonexistent pipe` / `exporting`
     → 「Podman machine 未运行」中文指引；
   - 命中 `payload does not match` / `supported image formats` → **C-I4** 三步排查
     （`tar tf` 自检结构 → 手动 `load -i` 复核 → 升级 podman / 重新 save）；
   - 其余真失败：消息必须同时带 exit 码**与 podman 原生 stderr 末行**（S1，禁止只报 exit=125）。
6. **返回值契约**：统一返回 `LoadImageResult(loaded: bool, tags: list[str], id: str, message: str)`；
   任务层仅在 `loaded=False` 时 `raise Exit(1, message)`，**禁止**在 client_core 层直接 raise Exit。

## 4. 命名空间规范（`__init__.py`）

`src/jpman_client/tasks/__init__.py` 必须同时提供三套入口（人类用户习惯短命令；集成调用习惯容器前缀；容器内自举习惯 env.* 前缀）：

### 4.1 根命名空间（人类驾驶员）

```python
from .manage import (load as image_load, images as list_images, save as image_save,
                     run as container_run, stop as container_stop,
                     status as container_status, clean as container_clean)
from invoke import Collection

ns = Collection()
ns.add_task(image_load, "load")
ns.add_task(list_images, "images")
ns.add_task(image_save, "save")
ns.add_task(container_run, "run")
ns.add_task(container_stop, "stop")
ns.add_task(container_status, "status")
ns.add_task(container_clean, "clean")
```

> 实际实现（`__init__.py`）直接以 `ns.add_task(manage.load)` 形式注册（invoke 取函数名作为任务名），
> 上表 import 别名仅示意语义；新增根命令时 §2 目录树、§4.4 兼容表、`__init__.py` 三处必须同步。

### 4.2 container.* 聚合命名空间（自动化集成）

```python
container_ns = Collection("container")
container_ns.add_task(image_load, "load")
container_ns.add_task(list_images, "images")
container_ns.add_task(image_save, "save")
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
| `invoke load` | `invoke container.load` | `--path *tar(.gz)` / `--cache-dir *dir`（不传 `--path` 时自动取缓存目录中最新的 `.tar.gz`/`.tar`） |
| `invoke images` | `invoke container.images` | （无参数） |
| `invoke save` | `invoke container.save` | `--tag *T` / `--cache-dir *dir`（pigz→gzip→未压缩三档降级，产物扩展名随之 `.tar.gz`/`.tar`，与 load 双扩展名契约对齐） |
| `invoke run` | `invoke container.run` | `--name N --tag T --ssh-port P --jupyter-port P --workspace W --user-password PW --jupyter-token TK --ssh-public-key KEY --grant-sudo/--no-grant-sudo --no-detach --host-network/--no-host-network --wayland/--no-wayland --gpu/--no-gpu --usb/--no-usb --dbus/--no-dbus --video/--no-video --rebuild-layer` |
| `invoke stop` | `invoke container.stop` | `--name N` |
| `invoke status` | `invoke container.status` | `--name N` |
| `invoke clean` | `invoke container.clean` | `--name N --tag T --volume --image` |

**布尔项三态规则（新增约束，违反打回）**：所有布尔参数必须拆成 `--x` / `--no-x` 一对并交由
`manage.py::_resolve_bool()` 解析（优先级：显式开 > 显式关 > `.env` > 默认；同开同关报错）。
原因（invoke 3.0.3 实测）：① `Argument.kind` 仅由 `type(default)` 推断，默认写 `None` 会退化为 `str`
（旗标变成"需取值"）；② `value` 在未赋值时回落 `default`，**无法区分「未指定」与「显式 False」**；
③ 反向旗标仅在 `default is True` 时自动生成。因此单参数写法无法表达"CLI 关闭 .env 开启项"。

**短选项规则（新增约束）**：参数较多的任务（如 `run`）必须显式 `auto_shortflags=False`。
invoke 的短名生成是「逐字符取首个未被占用字符」且与参数顺序耦合——实测 `ssh_public_key` 抢走 `-h`
致 `invoke run -h` 报错、`--host-network` 退化到短名 `-`。**长选项是唯一公开契约，短名不得作为 API**。

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
| S5 | load 的 tar_path 必须在调用子进程**之前**完成存在性校验（`load_image` 内 `tar_path.exists()` 不通过即返回 `LoadImageResult(loaded=False)`，由 `manage.load` 任务层 `raise Exit(1)`）；POSIX 命令为 `podman load -i`、Windows 原生为 `type \| podman load`（均经 `image_load_cli_command()` 构造）。不能让 podman 子进程自己报 "file not found"，导致用户分不清是 tar 不存在还是 daemon 连不上 |
| S6 | B-scheme socket 路径 UID 禁止硬编码：只允许经 `host_runtime_uid()` 推导（显式 `PODMAN_RUNTIME_UID` → POSIX `$XDG_RUNTIME_DIR` 末段 → `os.getuid()` → Windows 1000）。`invoke run` 必须先 `ensure_host_podman_socket()` 预检/自愈再拼 `podman run`；诊断分流上 `podman.sock` 缺失归 **C-I5**，opt-in 透传资源缺失归 C-I3，二者关键字不得交叉误报 |

## 6. 测试与验证

- 静态语法：`python -m py_compile src/jpman_client/tasks/*.py`（无 SyntaxError，全部通过）
- Lint/类型：VS Code GetDiagnostics（tasks 目录九模块零告警）
- 功能冒烟（任何任务修改后必跑 5 条）：
  1. `invoke --list`：命名空间加载无 ImportError，且 7 个根命令 + `container.*`（7 个）+ `env.*`（3 个）+ 三栈任务齐全：`quant.*` 6 个（build/up/down/ps/logs/smoke）、`xmnn.*` 8 个（六任务 + build-tvm/wheel）、`monetize.*` 8 个（六任务 + build-native/wheel）
  2. `invoke images`：SDK 可用→显示表格；SDK 不可用→自动 CLI fallback 同样显示表格（不能直接崩，哪怕是空表）
  3. `PODMAN_CLIENT_SDK_STRATEGY=legacy invoke images`：逃生舱 legacy 等价行为确认（调用路径不同但输出格式一致）
  4. **load 平台分流回归（改动 load 链路时必跑）**：POSIX 上 `invoke load`（有缓存时幂等执行）回显必须是 `podman load -i "..."` 且解析出 Tags；无缓存/无 daemon 环境至少静态断言 `image_load_cli_command("podman", p)` 在 Linux 输出 `load -i`、在模拟 `platform.system()=="Windows"` 下输出 `type "..." | podman load`——两条分支字符串错配即判失败（2026-09-12 exit=125 事故回归门）
  5. **B-scheme socket 回归（改动 run 链路时必跑）**：`host_runtime_uid()` 静态断言四优先级（显式覆盖 / XDG 末段 / `os.getuid()` / 模拟 Windows→1000）；原生 Linux 上构造 socket 缺失（`systemctl --user stop podman.socket` 后文件不在）调用 `ensure_host_podman_socket()` 必须返回第三元 `True`（已自愈）；`passthrough_diagnose_hint("Error: statfs .../podman/podman.sock: no such file...")` 必须返回空串（防 C-I5/C-I3 交叉误报，2026-09-12 UID 1006 事故回归门）
- 单元测试（client 包内，`python -m pytest tests -q`）：现状 **57 passed, 1 skipped**；三个测试文件——`tests/test_overlay_core.py`（数据驱动内核 39 用例体系）、`tests/test_tasks_surface.py`（三命名空间任务表面黄金清单）、`tests/test_compose_merge.py`（extends 合并 18 用例）。共享包测试在 `apps/containers/shared/tests/`（jpman_common 覆盖率 97%），两端改动须分别跑绿。
