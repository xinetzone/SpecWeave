# podman-py SDK 连接硬约束（jupyter-podman-client 消费端）

> **规范来源**：本规范以 `projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-py/concepts/01-connection.md §8`
> 和 `05-advanced.md §6`（OKF v0.2 podman-py 知识包）为最高可信度裁决源。
> 所有与 podman-py 行为相关的冲突一律以知识包 bundles 为准，不凭经验修改。
>
> **实现位置（2026-09 重构后）**：本文件涉及的全部连接层符号——
> `sdk_base_url_candidates` / `get_client` / `sdk_strategy_from_env` /
> `wsl_distro_name` / `_wsl_user_uid` / `machine_connection_uri` /
> `host_runtime_uid` / `podman_sock_path` / `host_runtime_dir` /
> `ensure_host_podman_socket` / `windows_diagnose_hint`——**单一事实源**
> 在组内共享包 `apps/containers/shared` 的 `jpman_common.connection`
> （消费端与构建端共享，`import podman` 只允许出现在该包）。client 侧
> `utils.py` / `client_core.py` 仅保留再导出垫片，旧导入路径仍可用；
> 修改连接行为必须改共享包，不得在 client 复制私有副本。

## 1. 合法 scheme 白名单（6 个 = 全集）

podman-py `PodmanClient(base_url=...)` / `APIClient` 的 Adapter 映射层只支持以下 6 种 scheme；
**任何其他 scheme（包括 docker-py 的 `npipe://`、Unix 域的 `socket://`、file:// 等）一律抛 `ValueError: Unsupported URL scheme`**。

| scheme | 说明 | 典型 URL | 适用平台 |
|--------|------|---------|---------|
| `unix` | Unix 域 socket 直连 | `unix:///run/user/1000/podman/podman.sock` | Linux / WSL2 内 / WSL9P 互通 |
| `http+unix` | Unix 域 socket 上的 HTTP 抽象层 | `http+unix:///run/user/1000/podman/podman.sock` | 同上（SDK 内部会自动从 `unix://` 归一化到 `http+unix://`，外部传哪种都可以） |
| `ssh` | SSH 远程 + UDS；SDK shell-out `ssh -N -L` 端口转发 | `ssh://devuser@192.168.1.10/run/user/1000/podman/podman.sock` | 跨机、Podman Machine 场景 |
| `http+ssh` | SSH 上的 HTTP 抽象层 | `http+ssh://devuser@192.168.1.10:22/run/user/1000/podman/podman.sock` | 同上（内部归一化） |
| `tcp` | TCP 明文连接（无 TLS） | `tcp://127.0.0.1:8888` | 本机 loopback、可信内网 |
| `http` | TCP 上的 HTTP 抽象层 | `http://127.0.0.1:8888` | 同上（内部归一化） |

### 1.1 绝对禁止（W-I2 触发）

**`npipe://` 是 docker-py 在 Windows 上的专有方案**（`npipe:////./pipe/docker_engine`），
podman-py **从来没有支持过**。docker-py 老用户复制粘贴会直接触发 W-I2 诊断。
修复：改成上述 6 种之一（推荐 WSL9P unix 或 Podman Machine SSH）。

## 2. Windows 原生 CPython：base_url 必须显式（不能依赖 from_env 默认值）

### 2.1 为什么默认值在 Windows 必挂

`PodmanClient()` 无参构造 / `from_env()` 的默认回退链是：

1. 读 `CONTAINER_HOST` / `DOCKER_HOST` 环境变量
2. 读 `containers.conf` 中 `[engine] active_service`
3. **回退到 `XDG_RUNTIME_DIR`（默认 `/run/user/$UID`） + `/podman/podman.sock`**

第 3 步是**纯 Linux 语义**：Windows 原生 CPython 没有 `/run/user/` 目录，`shutil.which("podman")`
即使存在也会在 `APIClient.__init__` 层抛 `FileNotFoundError: No such file or directory: '/run/user/...'`（W-I1）。

### 2.2 必须显式传 base_url 的条件

`platform.system() == "Windows"` 且**没有**显式设置 `CONTAINER_HOST`/`DOCKER_HOST` 环境变量时，
SDK 代码必须**自己**从 `sdk_base_url_candidates()` 拿到候选并传 `PodmanClient(base_url=cand.base_url)`，
**绝对不能**直接调 `PodmanClient()` 无参构造。

Linux / WSL2 内原生 CPython 没有这个约束：`/run/user/$UID` 目录真实存在，可以 `from_env()` 直连。

## 3. 四策略逃生舱（PODMAN_CLIENT_SDK_STRATEGY）

用户和自动化可以通过环境变量 `PODMAN_CLIENT_SDK_STRATEGY` 紧急切换连接策略，
无需改代码，热生效。合法值=白名单 `{auto, legacy, wsl, machine}`；非合法值归一化为 `auto`。

| 值 | 行为 | 使用场景 |
|----|------|---------|
| `auto`（默认） | P0 env → P1 WSL9P → P2 Machine → P3 tcp，按顺序逐个 ping，命中即停 | 99% 用户；日常驾驶；零配置 |
| `legacy` | 只调一次 `from_env()`（等价于 v0.0.x 旧行为），不做任何多候选探测 | ① 生产紧急回滚怀疑新逻辑有 bug  ② 100% Linux 用户不想有 P1/P2/P3 额外探测开销 |
| `wsl` | 只走 P0 env + P1 WSL9P（Windows 下）或 P0 env（Linux 下）；跳过 P2 Machine、P3 tcp | 明确**只连 WSL2 内 daemon**；不装 Podman Desktop 的纯 WSL 用户 |
| `machine` | 只走 P0 env + P2 Machine；跳过 P1 WSL9P、P3 tcp | 明确**只连 Podman Desktop 默认 Machine**；打开 Podman Desktop 初始化一次后日常驾驶 |

### 3.1 归一化实现要求

```python
def sdk_strategy_from_env() -> str:
    raw = os.environ.get(SDK_STRATEGY_ENV, "auto").strip().lower()
    return raw if raw in _VALID_STRATEGIES else "auto"  # 不抛错，静默归一
```

⚠️ **绝对不能**：
- 非合法值抛 `ValueError`（会导致 shell 手误打了 `PODMAN_CLIENT_SDK_STRATEGY=auto1` 整个 invoke 崩）
- 归一化到 `legacy` 以外的其他值（`auto` 是唯一安全回退）

## 4. 多候选优先级（sdk_base_url_candidates 行为契约）

不同 `strategy × platform` 组合产生的候选序列必须严格如下；不能私自调换顺序。

| strategy | platform==Windows | platform!=Windows |
|----------|-------------------|--------------------|
| auto | [P0 env, **P1 WSL9P**, P2 Machine, P3 tcp] | [P0 env, P2 Machine]（等价于 legacy，无 WSL 探测开销） |
| legacy | [P2 Machine only（单次 from_env，无 P1/P3）] | [P2 Machine only]（与旧版一致） |
| wsl | [P0 env, **P1 WSL9P**]（跳过 Machine/tcp） | [P0 env]（Linux 下 WSL 分支直接跳过，无额外探测） |
| machine | [P0 env, P2 Machine]（跳过 WSL9P/tcp） | [P0 env, P2 Machine] |

### 4.1 P1 WSL9P 生成契约（Windows 独有）

```
base_url = f"unix:///mnt/wsl/{distro}/run/user/{uid}/podman/podman.sock"
hint = "WSL2 内先：sudo loginctl enable-linger $USER && systemctl --user enable --now podman.socket"
```

其中：
- **distro** 必须走 `wsl_distro_name()` 三级回退（WSL_DISTRO_NAME env → wsl.exe -l -q → wsl.exe -l -v Running 首个）
- **uid** 必须走 `_wsl_user_uid(distro)`（`wsl.exe -d <Distro> id -u` 实际探测 + lru_cache）；**严禁硬编码 1000**（WSL 默认用户 UID 不一定是 1000，非英语版自定义用户也会变）

### 4.2 P3 tcp loopback 兜底

```
base_url = "tcp://127.0.0.1:8888"
hint = "手动：podman system service tcp:127.0.0.1:8888 --time 0   # loopback 仅本机安全"
```

P3 永远是最后一个；不能放第一个导致生产环境误连到手动起的无认证 TCP。

## 5. 错误记录与诊断（不可变格式）

所有候选失败后必须输出**结构化汇总表**，每行格式固定：

```
[i/N] source=<P0-env|P1-wsl-9p|P2-machine|P3-tcp-loopback|legacy>
      base_url=<真实 url 或 from_env-legacy>
      错误=<exc_type: exc_msg>
      提示=<cand.hint 空串占位>
```

最后一行**必须**追加 `windows_diagnose_hint(last_exc_type, last_exc_msg)` 的命中结果（非 Windows 下返回空串自动消失）。

**不能**：
- 直接 `raise exc` 裸堆栈（用户看不懂；也没有速查表）
- 只打印最后一个失败（用户不知道前面还试过 3 条更合适的路径没）
- 把 hint 省略（哪怕空也要留 `提示=` 字段，方便诊断脚本 parse）

## 6. SDK Import 安全

```python
try:
    import podman as _podman_sdk
    from podman import PodmanClient
    _HAS_PODMAN_PY = True
except ImportError:
    _HAS_PODMAN_PY = False
    _podman_sdk = None
    PodmanClient = None  # type: ignore[misc,assignment]
```

`get_client()` 内部 `if not _HAS_PODMAN_PY: yield None`；不能让 ImportError 直接冒泡。
这样 `pip install -e .` 时漏了 podman 依赖也能走 CLI fallback 不崩，只是会慢一点。
