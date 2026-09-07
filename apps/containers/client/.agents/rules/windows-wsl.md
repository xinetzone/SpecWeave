# Windows 11 × WSL2 支持规范（jupyter-podman-client 消费端）

> 本规范是 `apps/containers/client` 区别于 `apps/containers/jupyter-podman-rootless`（构建端）的核心差异文件。
> 构建端可以跑在 WSL2 / Linux / macOS 原生即可；但消费端的目标场景之一是
> **Windows 11 原生 CPython 用户（不切到 WSL 终端）直接 `pip install -e .` + `invoke run` 连到 WSL2 内或 Podman Machine 的 Podman daemon**。

## 1. 两种 Windows 11 用户画像（谁需要本规范）

| 画像 A：Windows 原生 CPython + WSL2 共存 | 画像 B：Windows + Podman Desktop Machine |
|-----------------------------------------|----------------------------------------|
| 宿主 Python：`C:\Python314\python.exe`（原生） | 宿主 Python：同上 |
| Podman daemon：WSL2 `Ubuntu` 发行版里的 systemd 用户 podman.socket | Podman daemon：Podman Desktop 默认 Machine（`podman machine list` 能看到） |
| 技术路径：**WSL9P 9P 互挂 unix socket**（零开销，推荐度⭐⭐⭐⭐⭐） | 技术路径：**Podman Machine SSH**（零配置，推荐度⭐⭐⭐⭐） |
| SDK 连接：`unix:///mnt/wsl/Ubuntu/run/user/1000/podman/podman.sock` | SDK 连接：由 `containers.conf [engine].active_service` 指向的 SSH |

两种画像都走 `PODMAN_CLIENT_SDK_STRATEGY=auto`（默认）时会被自动探测命中，无需用户区分。

## 2. A/B 维度分离（最容易混淆的概念，本规范的核心）

本消费端的 Windows 支持同时涉及两个彼此独立的维度；
代码路径、文档说明、参数、诊断全部按维度分开，禁止混写：

| 维度 | 全称 | 功能 | 所在函数 | 典型输入 | 典型输出 |
|------|------|------|---------|---------|---------|
| **Dimension A · 容器卷挂载路径** | Container Volume Mount Path | 把宿主机的**工作区目录**（如 D 盘某个 repo）挂到容器内，供 devuser 在容器里写代码 | `utils.py::to_posix_path` | `D:\spaces\SpecWeave` 或 `D:/spaces/SpecWeave` | `/mnt/d/spaces/SpecWeave`（传给 `podman -v` 或 SDK `mounts=[{source: /mnt/d/...}]`） |
| **Dimension B · SDK daemon 连接 URL** | SDK Daemon Connection URL | 告诉 `PodmanClient(base_url=...)` 去哪里找 Podman daemon（在 WSL2 里？还是 Machine？还是 127.0.0.1？） | `utils.py::sdk_base_url_candidates` + `client_core.py::get_client` | 无参数（纯探测）或 `.env` 中 `WSL_DISTRO_NAME=Ubuntu` | `unix:///mnt/wsl/Ubuntu/run/user/1000/podman/podman.sock`（拼出 base_url） |

### 2.1 为什么混淆是灾难级 Bug

如果把 B 维的 daemon 路径误走 A 维的 `to_posix_path`：
- `to_posix_path("unix:///mnt/wsl/...")` 什么都不会改，还会误判断"前缀不是 Windows 盘符跳过"——看起来没问题，但实际上拼 daemon 路径需要的是 distro/UID 两个探测，与盘符转 `/mnt/d` 的正则完全无关
- 反过来如果把 A 维的工作区路径 `D:\workspace` 直接当 base_url 传：直接抛 `ValueError: Invalid URL scheme 'd'`

代码中两个维度的函数名已显式区分：A 维带 `path` / `posix` 关键词；B 维带 `base_url` / `candidates` / `distro` / `uid`。

## 3. WSL 发行版名探测：3 级回退（`wsl_distro_name()`）

Windows 原生 CPython 下 `P1 WSL9P` 分支需要知道 `<Distro>` 才能拼出 `/mnt/wsl/<Distro>/...`。
必须严格按以下 3 级回退顺序探测（从上到下优先级递减）：

```
第 1 级：环境变量 WSL_DISTRO_NAME 非空 → 返回（显式设置优先级最高，自动化场景用）
    │
    └─ 环境变量不存在或空串 →
第 2 级：subprocess.run(["wsl.exe", "--list", "--quiet"])
          按 UTF-16 LE 解码 → 去掉 BOM（\ufeff）→ splitlines() 首行非空 → 返回（默认发行版）
    │
    └─ 第 2 级失败（wsl.exe 返回空？系统无 WSL？）→
第 3 级：subprocess.run(["wsl.exe", "--list", "--verbose"])
          同样 UTF-16 LE 解码 → 跳过表头第一行 → 对每一行按 2+ 空白拆列 →
          parts[1].lower() == "running" 的第一行 → 返回 parts[0]（首个运行中的发行版）
    │
    └─ 都失败 → return None；P1 候选被跳过，sdk_base_url_candidates 自动降级到 P2/P3
```

### 3.1 编码必须显式 UTF-16 LE（最常见踩坑）

**PowerShell 5.1（Windows 11 默认）下 `wsl.exe` 的 stdout/stderr 是 UTF-16 LE，不是 UTF-8。**
如果用 `encoding="utf-8"` 或默认编码：
- 英文系统：还能勉强看到一些乱码字符，用 `errors="replace"` 可以 parse 出英文字母名字
- **中文系统：`wsl.exe` 输出里"默认"两个汉字对应的 UTF-16 字节按 UTF-8 解会完全乱码**，导致 `wsl.exe --list --quiet` 的首行被判定为空，跳到第 3 级但 3 级也全是乱码，最终 WSL 明明存在但 P1 被跳过用户以为坏了

正确代码：
```python
cp = subprocess.run(["wsl.exe", "--list", "--quiet"],
                   capture_output=True, text=True, timeout=5,
                   encoding="utf-16-le", errors="replace")
out = cp.stdout or ""
lines = [line.rstrip("\r").lstrip("\ufeff") for line in out.splitlines() if line.strip()]
if lines:
    return lines[0]
```

### 3.2 双门卫：_has_wsl_host_support()

调 `wsl.exe` 之前必须先过双门卫；两个条件任何一个不满足，直接认定"本系统没有 WSL 互操作能力"，**跳过所有 P1 分支**，不再发起任何 wsl.exe 子进程：

1. **`shutil.which("wsl.exe") is not None`**：`wsl.exe` 必须在 PATH（Windows 功能里没开 WSL 的话 which 返回 None）
2. **`Path("/mnt/wsl/").exists()`**：`/mnt/wsl/` 目录必须存在（这是 WSL2 发行版间 9P 互挂的根挂载点；没开 WSL2 / WSL1 环境都不会有这个路径）

Linux / macOS 环境下双门卫第一个守卫就返回 False，P1 分支全程无开销，不用担心拖慢。

## 4. UID 探测：严禁硬编码 1000

拼 `/mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock` 需要 <UID>。
**严禁硬编码 1000**（WSL 默认用户 UID 虽然 99% 是 1000，但：
① 多用户 WSL 的其他用户 UID=1001/1002；② `podman.socket` 由哪个用户启的就必须用哪个用户的 UID socket；
③ 用户自定义 WSL 发行版导入时 UID 可以是任意）。

正确做法（`_wsl_user_uid(distro)`）：

```python
cp = subprocess.run(
    ["wsl.exe", "-d", distro, "--", "sh", "-lc", "id -u"],
    capture_output=True, text=True, timeout=8,
    encoding="utf-16-le", errors="replace",
)
out = (cp.stdout or "").strip().rstrip("\r").lstrip("\ufeff")
uid = int(out) if out.isdigit() else 1000   # 仅当探测彻底失败时 1000 作为最后兜底（有诊断提示）
```

- 必须 `@functools.lru_cache(maxsize=None)` 缓存：同一 distro 进程生命周期内只调一次
- ⚠️ **调用方平台守卫**：sdk_base_url_candidates 中调 `_wsl_user_uid(distro)` 之前必须先检查 `is_host_windows` 且 distro 非 None；_wsl_user_uid 自身不带平台守卫（因为被调时一定是 Windows 路径），**调用方必须保证前置条件成立**

## 5. W-I1~W-I3 速查表（30 秒修复）

`windows_diagnose_hint(exc_type, exc_msg)` 正则匹配的三条 Windows 专属坑；
每条必须能在 README §5.4 和 utils.py 代码注释中找到完全一致的描述；改任何一处必须同步更新三处：

| ID | 触发异常匹配 | 根因（一句话） | 30 秒修复（必须是一行命令） |
|----|------------|--------------|--------------------------|
| **W-I1** | `FileNotFoundError` 或 `No such file or directory` + 异常里包含子串 `/run/user/` | podman-py from_env() 回退是 Linux `/run/user/$UID` 路径，Windows 原生不存在 | **三选一**：<br>a) 把 invoke 改在 WSL2 终端里跑（完全 Linux 行为）<br>b) 打开 **Podman Desktop** 初始化默认 Machine<br>c) PowerShell：`$env:CONTAINER_HOST="unix:///mnt/wsl/Ubuntu/run/user/1000/podman/podman.sock"` |
| **W-I2** | `Unsupported URL scheme` + 异常里有子串 `npipe` | docker-py 老用户粘 `npipe:////./pipe/docker_engine`；podman-py 没有 npipe Adapter | 把 base_url 改成以下 6 种合法之一：<br>`unix:///mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock`<br>或 `ssh://user@127.0.0.1:<MachinePort>`<br>或 `tcp://127.0.0.1:8888` |
| **W-I3** | `TimeoutError` 或 `Timeout` + 异常里有子串 `podman-forward` | SSH 模式下 SDK shell-out `ssh -N -L` 转发，但首次 SSH StrictHostKeyChecking 会在 stdin 阻塞问 `Are you sure you want to continue connecting?`，SDK 轮询等待不到本地 socket 文件最终超时 | **一次性**：PowerShell 里先跑 `podman machine ssh true`<br>然后当终端提示 `Are you sure you want to continue connecting (yes/no/[fingerprint])?` 时，手工敲 `yes` 回车<br>Machine 的 HostKey 被写入 `~/.ssh/known_hosts`，之后 SDK 调 SSH 永不阻塞 |

## 6. .env 与环境变量的加载语义（C9）

`manage.py::_load_env_overrides(project_root)` 做两件事（缺一不可，顺序不能换）：

```python
env_path = project_root / ".env"
if env_path.exists():
    # 第一步：同步到 os.environ（SDK 策略层必须靠 os.environ 读）
    load_dotenv(dotenv_path=str(env_path), override=False, verbose=False)
    # 第二步：返回 dict 给 _merge_config 合并 ContainerConfig 容器级字段
    return {k: v for k, v in dict(dotenv_values(str(env_path))).items() if v}
return {}
```

- **`override=False` 是红线（C9）**：用户 shell 里已经 `$env:PODMAN_CLIENT_SDK_STRATEGY="wsl"` 显式设置过，优先级必须高于 `.env` 文件，不能被 `.env` 里的 `auto` 覆盖。反过来 .env.example 里写的注释也明确说明「shell export 优先级高于 .env」
- **编码必须 UTF-8**：.env 文件里有中文注释（本项目的 .env.example 有中文），load_dotenv 默认 `locale.getpreferredencoding()`，中文 Windows 默认是 GBK，会乱码；必须显式 `encoding="utf-8"`
- **sdk_strategy_from_env() / wsl_distro_name() / sdk_base_url_candidates(P0 env)** 三个函数一律读 `os.environ`，不直接读文件；所以缺第一步（load_dotenv）会导致 .env 里写了 SDK 级变量却不生效，这是上一轮七概念 WIP 中被揪出的实际缺漏

## 7. 验证脚本（任何 WSL 相关改动后必跑 4 条）

在 Windows 11 PowerShell 下：

```powershell
# V1：诊断双门卫是否认为本系统有 WSL 能力（纯工具函数，无副作用）
python -c "import sys; sys.path.insert(0,'apps/containers/client/tasks');
from utils import _has_wsl_host_support; print('has_wsl=', _has_wsl_host_support())"

# V2：发行版名三级回退结果（必须看到非 None，才会生成 P1 候选）
python -c "import sys; sys.path.insert(0,'apps/containers/client/tasks');
from utils import wsl_distro_name; print('distro=', wsl_distro_name())"

# V3：sdk_base_url_candidates 完整序列（auto 策略下应当看到 4 条候选；legacy 只有 1 条）
$env:PODMAN_CLIENT_SDK_STRATEGY="auto"
python -c "import sys; sys.path.insert(0,'apps/containers/client/tasks');
from utils import sdk_base_url_candidates;
[print(f'{i+1}. source={c.source}  url={c.base_url}') for i,c in enumerate(sdk_base_url_candidates())]"

# V4：最终 invoke images 真的能通（生产冒烟）
cd apps/containers/client
invoke images
```
