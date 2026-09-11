"""镜像消费端 PodmanClient 封装。

后端优先级：
  Tier 1: podman-py SDK（声明式 API，pyproject 已强制依赖）
  Tier 2: CLI subprocess（保底路径，当 SDK 连接失败 / 版本不兼容时）

rootless 三必需参数（/dev/fuse、label=disable、cgroupns=host）
由 utils.ContainerConfig 默认值内置，调用方无需显式传入。
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
from typing import Optional

from invoke import Context
from invoke.exceptions import Exit

from .utils import (
    ContainerConfig,
    LoadImageResult,
    SDK_STRATEGY_ENV,
    build_passthrough_spec,
    check_runtime_ready,
    container_exists as cli_container_exists,
    container_running as cli_container_running,
    detect_runtime,
    generate_random_string,
    passthrough_diagnose_hint,
    podman_sock_path,
    run_cmd,
    sdk_base_url_candidates,
    sdk_strategy_from_env,
    to_posix_path,
    windows_diagnose_hint,
)

# ---------------------------------------------------------------------------
# podman-py SDK 探测（核心依赖，失败时走 CLI fallback）
# ---------------------------------------------------------------------------
try:
    import podman as _podman_sdk
    from podman.errors import APIError, NotFound as PodmanNotFound

    _SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - 仅当安装被破坏时发生
    _podman_sdk = None
    APIError = Exception
    PodmanNotFound = Exception
    _SDK_AVAILABLE = False


def sdk_available() -> bool:
    """podman-py 模块是否已安装。"""
    return _SDK_AVAILABLE


@contextmanager
def get_client():
    """获取 PodmanClient 的上下文管理器（SDK 不可达时 yield None）。

    Windows 11 原生支持策略（对齐 OKF v0.2 §8 Windows 三路径）：
      按 ``PODMAN_CLIENT_SDK_STRATEGY`` 环境变量（默认 ``auto``）依次
      尝试：P0 环境变量显式 URL → P1 WSL2 9P 互通 socket →
      P2 Podman Machine 命名连接 → P3 TCP 回环 → 全部失败时
      输出每轮尝试的诊断信息 + W-I1~W-I3 速查表命中项，然后 yield None
      进入 CLI fallback。**行为承诺**：所有候选都失败时才返回 ``None``，
      与旧版本 API 语义一致，调用方 ``if client is not None:`` 判断无需修改。

    使用方式::

        with get_client() as client:
            if client is not None:
                client.images.list()
            else:
                # CLI fallback
    """
    if not _SDK_AVAILABLE:
        yield None
        return

    strategy = sdk_strategy_from_env()
    candidates = sdk_base_url_candidates(strategy)

    attempts: list[dict] = []
    client = None

    def _close_safe(c):
        if c is None:
            return
        try:
            c.close()
        except Exception:
            pass

    try:
        for cand in candidates:
            this_client = None
            try:
                if cand.base_url is None:
                    # None → 走 SDK 默认分支：from_env() / 无参 PodmanClient()，
                    # 让其自身读取 containers.conf active_service（含 PM-1 PM-2 Machine）
                    this_client = _podman_sdk.from_env()
                else:
                    this_client = _podman_sdk.PodmanClient(base_url=cand.base_url)
                ping_result = this_client.ping()
                # podman-py 5.x ``system.ping()`` 返回 bool（HTTP response.text == "OK"）。
                # 严格 True 才当选：防止 ping 返回 False（如打到 Jupyter/其他 HTTP 服务，
                # 200 OK 但 body 不是 "OK"）时错误选中假 client。
                ping_ok = ping_result is True
                if not ping_ok:
                    raise RuntimeError(
                        f"ping()={ping_result!r}，未返回 True"
                        f"（可能连接到非 Podman daemon，如其他监听该端口的服务）"
                    )
                # 成功：把这个 client 作为最终 yield 的，跳出循环
                client = this_client
                this_client = None
                break
            except Exception as exc:  # noqa: BLE001 - 失败需要记录信息，不能吞
                exc_type_name = type(exc).__name__
                exc_msg = str(exc)
                attempts.append(
                    {
                        "source": cand.source,
                        "base_url": cand.base_url,
                        "hint": cand.hint,
                        "exc_type": exc_type_name,
                        "exc_msg": exc_msg,
                    }
                )
            finally:
                _close_safe(this_client)

        if client is not None:
            yield client
            return

        # 所有候选全部失败：
        #   - LOG_LEVEL=DEBUG 才打印完整候选诊断（每轮10+行，避免每次调用打印噪音）
        #   - 普通 INFO 级仅 1 行「[INFO][降级]」统一前缀，用户一眼懂：不是失败=降级
        log_level = (os.environ.get("PODMAN_CLIENT_LOG_LEVEL") or "INFO").upper()
        is_debug = log_level in {"DEBUG", "TRACE"}
        first_err = attempts[0] if attempts else {"exc_type": "Unknown", "source": "-"}
        print(
            "[INFO][降级] SDK路径不可用（首候选="
            f"{first_err['source']} {first_err['exc_type']}）→ 走CLI fallback"
            f"（PODMAN_CLIENT_LOG_LEVEL=DEBUG 打印完整诊断）"
        )
        if is_debug:
            print("[SDK-DEBUG] 全部连接候选失败，降级到 CLI。诊断清单：")
            print(f"           strategy = {strategy} (通过 {SDK_STRATEGY_ENV} 修改)")
            for i, att in enumerate(attempts, 1):
                src = att["source"]
                url = att["base_url"] or "(SDK 自行读 from_env/containers.conf)"
                print(f"    [{i}/{len(attempts)}] source={src}")
                print(f"          base_url = {url}")
                print(f"          错误     = {att['exc_type']}: {att['exc_msg']}")
                if att["hint"]:
                    for line in att["hint"].splitlines():
                        print(f"          提示     = {line}")
            last = attempts[-1] if attempts else {"exc_type": "", "exc_msg": ""}
            hint = windows_diagnose_hint(last["exc_type"], last["exc_msg"])
            if hint:
                print("[SDK-DEBUG] 已知坑匹配（W-I1~W-I3 / C-I1~C-I2）:")
                for line in hint.splitlines():
                    print(f"           {line}")
        yield None
    finally:
        _close_safe(client)


# ===========================================================================
# 镜像管理：加载 + 查询
# ===========================================================================


def _load_via_sdk(client, tar_path: Path) -> LoadImageResult:
    """通过 podman-py SDK 加载镜像 tar。

    podman-py 5.x 的 ``ImagesManager.load`` 支持两种互斥参数：
      * ``file_path`` (:class:`os.PathLike`) — SDK 内部自行 open 读取，零内存拷贝，推荐。
      * ``data`` (:class:`bytes`) — SDK 内部 ``io.BytesIO(data)`` 包装，**不能传 file-like**
        （否则 ``io.BytesIO`` 抛 ``a bytes-like object is required, not BufferedReader``）。
    """
    try:
        loaded = client.images.load(file_path=tar_path)
        tags: list[str] = []
        img_id = ""
        if isinstance(loaded, list) and loaded:
            # podman-py 5.x: 返回 Image 对象列表（签名是 Generator 但实际调用端可能是 list）
            first = loaded[0]
            img_id = getattr(first, "short_id", "") or getattr(first, "id", "")
            tags = list(getattr(first, "tags", []) or [])
        elif hasattr(loaded, "__iter__") and not isinstance(loaded, (str, bytes, list)):
            # Generator 情况（严格按 podman-py 签名）
            items = list(loaded)
            if items:
                first = items[0]
                img_id = getattr(first, "short_id", "") or getattr(first, "id", "")
                tags = list(getattr(first, "tags", []) or [])
        return LoadImageResult(
            loaded=True,
            tags=tags,
            id=img_id,
            message=f"[SDK] 已加载镜像（file_path={tar_path}）",
        )
    except Exception as e:
        return LoadImageResult(loaded=False, message=f"[SDK] 加载失败: {e}")



def _load_via_cli(c: Context, tar_path: Path) -> LoadImageResult:
    """通过 podman load 命令加载镜像 tar。

    使用 stdin pipe（type file | podman load）而非 -i flag，
    避免大文件经 REST API path 参数传输时触发 WSL2 daemon EOF 错误。

    注意：
    - Windows PowerShell 管道中 type 命令可能返回非零退出码，
      因此以 stdout 是否包含 "Loaded image" 作为成功判断依据，而非 exit code。
    - 以 ``warn=True`` 调用 run_cmd：命令失败时返回 Result 而不抛异常，使下方
      「Podman machine 未运行」检测分支可达（此前失败即 raise Exit，友好提示被
      原生英文报错与 ``exit=125`` 掩盖）。
    """
    runtime = detect_runtime()
    result = run_cmd(
        c,
        f'type "{tar_path}" | {runtime} load',
        pty=False,
        echo=True,
        warn=True,
    )

    # TTY Console 路径：subprocess.call() 成功返回 None，输出已直接写入控制台
    # 此时无法捕获 stdout，但命令已成功执行（否则会 raise Exit）
    if result is None:
        return LoadImageResult(
            loaded=True,
            tags=[],
            message="[CLI] 镜像加载完成",
        )

    _out = getattr(result, "stdout", "") or ""
    _err = getattr(result, "stderr", "") or ""
    combined = (_out + " " + _err).lower()

    # 优先检查 Podman machine 未运行的特定错误（在检查成功标志之前）
    if "cannot connect to podman" in combined or \
       "actively refused it" in combined or \
       "nonexistent pipe" in combined or \
       "exporting" in combined:
        return LoadImageResult(
            loaded=False,
            message=(
                "[CLI] Podman machine 未运行。\n"
                "解决方法：在终端执行以下命令启动 Podman machine：\n"
                "  podman machine start\n"
                "如需初始化：podman machine init"
            )
        )

    # Windows PowerShell 管道退出码不可靠，以 stdout 是否含 "Loaded image" 为准
    stdout = _out
    tags: list[str] = []
    for line in stdout.splitlines():
        if "Loaded image" in line:
            name = line.split(":", 1)[1].strip()
            tags.append(name)

    if tags:
        return LoadImageResult(
            loaded=True,
            tags=tags,
            message="[CLI] 镜像加载完成",
        )

    # 没有 Loaded image 且没有已知错误 → 真正的失败
    return LoadImageResult(loaded=False, message=f"[CLI] load 命令执行失败（exit={result.exited}）")


def load_image(c: Context, tar_path: Path) -> LoadImageResult:
    """从本地 tar.gz 加载镜像，SDK 优先失败则走 CLI。"""
    if not tar_path.exists():
        return LoadImageResult(loaded=False, message=f"镜像文件不存在: {tar_path}")

    # 就绪预检：Podman machine 未运行时直接给出中文指引，避免执行注定失败的
    # `type <大文件> | podman load`（既浪费 IO 又只会得到英文原生报错）。
    ready, hint = check_runtime_ready()
    if not ready:
        return LoadImageResult(loaded=False, message=f"[Load] {hint}")

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
            # SDK 成功连接到 daemon，但加载本身失败（非连接失败）→ 仍降级 CLI，统一 [INFO][降级] 前缀
            print(f"[INFO][降级] SDK加载失败 → 走CLI fallback: {sdk_result.message}")

    cli_result = _load_via_cli(c, tar_path)
    if cli_result.loaded:
        print(cli_result.message)
        if cli_result.tags:
            print(f"[Load] Tags: {', '.join(cli_result.tags)}")
    else:
        print(cli_result.message)
    return cli_result


def _list_images_sdk(client) -> list[dict]:
    """SDK 列出本地镜像。"""
    out: list[dict] = []
    try:
        for img in client.images.list():
            tags = list(getattr(img, "tags", []) or [])
            out.append(
                {
                    "id": getattr(img, "short_id", "") or getattr(img, "id", "")[:12],
                    "tags": tags,
                    "size": getattr(img, "attrs", {}).get("Size", 0),
                    "created": getattr(img, "attrs", {}).get("Created", ""),
                }
            )
    except Exception:
        return []
    return out


def _list_images_cli(c: Context) -> list[dict]:
    """CLI 列出本地镜像。"""
    runtime = detect_runtime()
    out: list[dict] = []
    go_fmt = "{{.ID}}|{{.Repository}}:{{.Tag}}|{{.Size}}"
    result = run_cmd(
        c,
        runtime + ' images --format "' + go_fmt + '"',
        hide=True,
        warn=True,
        echo=False,
    )
    if result is None:
        return out
    for line in (getattr(result, "stdout", "") or "").splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        img_id, tag, size = parts
        tag = tag if "<none>" not in tag else ""
        out.append(
            {
                "id": img_id[:12],
                "tags": [tag] if tag else [],
                "size": size,
                "created": "",
            }
        )
    return out


def list_images(c: Context) -> list[dict]:
    """列出本地所有镜像（SDK 优先）。"""
    with get_client() as client:
        if client is not None:
            return _list_images_sdk(client)
    return _list_images_cli(c)


def image_exists(c: Context, tag: str) -> bool:
    """判断本地是否存在指定标签的镜像。"""
    images = list_images(c)
    for img in images:
        if tag in img["tags"]:
            return True
    return False


def image_inspect_info(c: Context, tag: str) -> dict:
    """读取单镜像 inspect 摘要（CLI 路径，供 run 前基底指纹检测等轻量场景）。

    走 ``podman image inspect`` 原始 JSON（而非 --format 模板），规避
    Windows cmd / Linux bash 双 shell 下模板引号与 ``$`` 变量展开差异。
    返回 ``{"digest": str, "labels": dict}``；镜像不存在或解析失败返回空 dict，
    调用方按「无指纹」降级，不得抛异常阻断主流程。
    """
    runtime = detect_runtime()
    r = run_cmd(
        c,
        f"{runtime} image inspect {tag}",
        hide=True,
        warn=True,
        echo=False,
    )
    if r is None or not getattr(r, "ok", False) or not (r.stdout or "").strip():
        return {}
    try:
        data = json.loads(r.stdout)
        info = data[0] if isinstance(data, list) and data else {}
    except (json.JSONDecodeError, IndexError, TypeError):
        return {}
    if not isinstance(info, dict):
        return {}
    labels = info.get("Labels") or {}
    return {
        "digest": str(info.get("Digest") or "").strip(),
        "labels": labels if isinstance(labels, dict) else {},
    }


# ===========================================================================
# 容器生命周期：run / stop / status / clean
# ===========================================================================


def _ensure_secrets(cfg: ContainerConfig) -> None:
    """自动填充缺失的密码/token（与构建端生成规则一致）。"""
    if not cfg.user_password:
        cfg.user_password = generate_random_string(16)
        print(f"[Config] 自动生成密码: {cfg.user_password}")
    if not cfg.jupyter_token:
        cfg.jupyter_token = generate_random_string(32)
        print(f"[Config] 自动生成 token: {cfg.jupyter_token}")


def _sdk_run_kwargs(cfg: ContainerConfig, workspace_posix: str) -> dict:
    """构造 podman-py containers.run 的 kwargs。

    透传部分由 ``utils.build_passthrough_spec`` 统一解析，与 CLI fallback 共用同一份
    结果，确保两条路径的运行参数完全一致（见 invoke-tasks 规则 §3.2）。
    """
    spec = build_passthrough_spec(cfg)
    ports = {
        "22/tcp": cfg.ssh_port,
        "8888/tcp": cfg.jupyter_port,
    }
    volumes = {
        workspace_posix: {"bind": "/workspace", "mode": "rw"},
        # B-scheme: 直连宿主 rootless daemon（绕过嵌套 userns）。
        # 宿主 socket bind-mount 到容器同一路径，容器内 entrypoint 的 B-scheme
        # 分支据此建立符号链接并设置 CONTAINER_HOST，SDK from_env() 即可连通。
        podman_sock_path(): {"bind": podman_sock_path(), "mode": "rw"},
    }
    # Wayland / D-Bus 透传挂载
    for src, dst, mode in spec.volumes:
        volumes[src] = {"bind": dst, "mode": mode}

    environment: dict[str, str] = {
        "USER_PASSWORD": cfg.user_password,
        "JUPYTER_TOKEN": cfg.jupyter_token,
        # B-scheme: 告知容器内 entrypoint 宿主 daemon socket 已 bind-mount 到
        # 容器内的哪个路径（与构建端语义一致）。
        "HOST_PODMAN_SOCK": podman_sock_path(),
    }
    if cfg.ssh_public_key:
        environment["SSH_PUBLIC_KEY"] = cfg.ssh_public_key
    if cfg.grant_sudo:
        environment["GRANT_SUDO"] = "yes"
    # 透传注入的环境变量（XDG_RUNTIME_DIR / WAYLAND_DISPLAY / DBUS_SESSION_BUS_ADDRESS
    # / SSHD_PORT）
    environment.update(spec.environment)

    kwargs = {
        "image": cfg.image,
        "name": cfg.name,
        "volumes": volumes,
        "environment": environment,
        "detach": cfg.detach,
        # C3：rootless 三必需的 /dev/fuse 硬编码保留，开启 GPU/USB 时在其后追加
        "devices": list(cfg.devices) + spec.devices,
        "security_opt": cfg.security_opt,
        "cgroupns": cfg.cgroupns,
        "user": cfg.user,
    }
    # Host 网络与端口发布互斥：host 网络下不传 ports
    if spec.publish_ports:
        kwargs["ports"] = ports
    if spec.network_mode:
        kwargs["network_mode"] = spec.network_mode
    return kwargs


def _run_via_sdk(client, cfg: ContainerConfig, workspace_posix: str) -> bool:
    """SDK 启动容器。"""
    try:
        try:
            old = client.containers.get(cfg.name)
            print(f"[SDK] 清理旧容器: {cfg.name}")
            old.remove(force=True)
        except PodmanNotFound:
            pass

        kwargs = _sdk_run_kwargs(cfg, workspace_posix)
        print(f"[SDK] 启动容器: {cfg.name} ({cfg.image})")
        container = client.containers.run(**kwargs)
        if cfg.detach:
            container.reload()
            print(f"[SDK] 容器已启动 (detached): {container.short_id}")
        else:
            print("[SDK] 容器前台运行")
        return True
    except Exception as e:
        # 透传资源缺失（C-I3）：podman 硬失败，且 Windows 原生 TTY 控制台下 CLI 路径
        # 走 subprocess.call 不捕获 stderr，故 SDK 层是 C-I3 指引的主要提示来源。
        hint = passthrough_diagnose_hint(str(e))
        if hint:
            print(hint)
        print(f"[SDK] 启动失败 fallback to CLI: {e}")
        return False


def _run_via_cli(c: Context, cfg: ContainerConfig, workspace_posix: str) -> None:
    """CLI 启动容器（与 jpman create 参数一致）。

    透传参数与 SDK 路径同为 ``utils.build_passthrough_spec`` 的产物，逐项等价：
      ``--network host``（且不带 ``-p``）/ ``-v``（Wayland、D-Bus）/ ``--device``（GPU、USB）
      / ``-e``（XDG_RUNTIME_DIR、WAYLAND_DISPLAY、DBUS_SESSION_BUS_ADDRESS、SSHD_PORT）。
    """
    runtime = detect_runtime()
    spec = build_passthrough_spec(cfg)

    if cli_container_exists(c, runtime, cfg.name):
        print(f"[CLI] 容器 {cfg.name} 已存在，先清理...")
        _stop_via_cli(c, cfg.name)

    cmd_parts = [
        runtime,
        "run",
        "--name",
        cfg.name,
    ]
    # ① Host 网络模式：与端口发布互斥，改传 --network host
    if spec.publish_ports:
        cmd_parts.extend(["-p", f"{cfg.ssh_port}:22", "-p", f"{cfg.jupyter_port}:8888"])
    else:
        cmd_parts.extend(["--network", spec.network_mode or "host"])
    cmd_parts.extend(
        [
            "-v",
            f"{workspace_posix}:/workspace",
            # B-scheme: 直连宿主 rootless daemon（绕过嵌套 userns）。
            # 宿主 socket bind-mount 到容器同一路径，容器内 entrypoint 的 B-scheme
            # 分支据此建立符号链接并设置 CONTAINER_HOST，容器内 podman SDK/CLI 可连通。
            "-v",
            f"{podman_sock_path()}:{podman_sock_path()}",
        ]
    )
    # ② Wayland / ④ D-Bus 透传挂载
    for src, dst, mode in spec.volumes:
        cmd_parts.extend(["-v", f"{src}:{dst}:{mode}"])
    cmd_parts.extend(
        [
            # C3：rootless 三必需硬编码，先于可选的 GPU/USB 设备
            "--device /dev/fuse",
            "--security-opt label=disable",
            "--cgroupns=host",
            "--user",
            cfg.user,
        ]
    )
    # ③ GPU / ⑤ USB 透传设备
    for dev in spec.devices:
        cmd_parts.extend(["--device", dev])
    if cfg.detach:
        cmd_parts.append("-d")
    cmd_parts.extend(["-e", f"USER_PASSWORD={cfg.user_password}"])
    cmd_parts.extend(["-e", f"JUPYTER_TOKEN={cfg.jupyter_token}"])
    cmd_parts.extend(["-e", f"HOST_PODMAN_SOCK={podman_sock_path()}"])
    if cfg.ssh_public_key:
        cmd_parts.extend(["-e", f'SSH_PUBLIC_KEY="{cfg.ssh_public_key}"'])
    if cfg.grant_sudo:
        cmd_parts.extend(["-e", "GRANT_SUDO=yes"])
    for key, val in spec.environment.items():
        cmd_parts.extend(["-e", f"{key}={val}"])
    cmd_parts.append(cfg.image)
    run_cmd(c, " ".join(cmd_parts), pty=not cfg.detach)
    if cfg.detach:
        print("[CLI] 容器已启动 (detached)")


def _exception_text(exc: BaseException) -> str:
    """拼接异常消息与 invoke 结果对象的 stderr/stdout。

    透传诊断（C-I3）需要 podman 的原始报错（``Error: statfs ...``），而该内容在
    ``UnexpectedExit.result.stderr`` 里，不在异常消息本身。
    """
    parts = [str(exc)]
    result = getattr(exc, "result", None)
    for attr in ("stderr", "stdout"):
        val = getattr(result, attr, "") or ""
        if val:
            parts.append(val)
    return "\n".join(parts)


def _print_passthrough_summary(cfg: ContainerConfig) -> None:
    """打印已启用的运行时透传项（全部关闭时零输出，保持默认隔离的输出不变）。"""
    enabled = [
        label
        for label, on in (
            ("host-network", cfg.host_network),
            ("wayland", cfg.wayland),
            ("gpu", cfg.gpu),
            ("usb", cfg.usb),
            ("dbus", cfg.dbus),
            ("video", cfg.video),
        )
        if on
    ]
    if enabled:
        print(f"[Run] 透传: {', '.join(enabled)}")


def run_container(c: Context, cfg: ContainerConfig) -> ContainerConfig:
    """启动容器，SDK 优先失败走 CLI。返回最终使用的配置（含自动填充的密码/token）。"""
    ready, hint = check_runtime_ready()
    if not ready:
        # 用 Exit 而非 RuntimeError：invoke 下前者打印简洁中文提示，后者会抛出完整 traceback
        raise Exit(1, f"运行时未就绪: {hint}")

    _ensure_secrets(cfg)
    workspace_path = cfg.resolved_workspace()
    if not workspace_path.exists():
        print(f"[Workspace] 创建工作目录: {workspace_path}")
        workspace_path.mkdir(parents=True, exist_ok=True)
    workspace_posix = to_posix_path(workspace_path)

    print(f"[Run] 容器: {cfg.name}  镜像: {cfg.image}")
    print(f"[Run] 挂载 {workspace_posix} -> /workspace")
    if cfg.host_network:
        # host 网络下容器直接占用宿主端口：SSH 走 SSHD_PORT（= --ssh-port，非特权端口），
        # Jupyter 固定为容器内 8888（不由 --jupyter-port 控制）。
        print(
            f"[Run] 网络: host（不发布端口；SSH=localhost:{cfg.ssh_port}，"
            "Jupyter=localhost:8888）"
        )
    else:
        print(f"[Run] 端口映射: SSH={cfg.ssh_port}  Jupyter={cfg.jupyter_port}")
    _print_passthrough_summary(cfg)

    sdk_ok = False
    with get_client() as client:
        if client is not None:
            sdk_ok = _run_via_sdk(client, cfg, workspace_posix)
    if not sdk_ok:
        try:
            _run_via_cli(c, cfg, workspace_posix)
        except Exception as exc:  # noqa: BLE001 - 需把 podman 原生报错翻译成 C-I3 指引
            pt_hint = passthrough_diagnose_hint(_exception_text(exc))
            if pt_hint:
                print(pt_hint)
            raise

    if cfg.host_network and cfg.jupyter_port != 8888:
        print(
            f"[Run] ⚠ host 网络模式下 Jupyter 固定监听容器内 8888，"
            f"--jupyter-port={cfg.jupyter_port} 不生效"
        )
    jupyter_port = 8888 if cfg.host_network else cfg.jupyter_port

    print("\n" + "=" * 60)
    print("访问信息:")
    print(f"  SSH:         ssh -p {cfg.ssh_port} devuser@localhost")
    print(f"  SSH 密码:    {cfg.user_password}")
    print(f"  Jupyter Lab: http://localhost:{jupyter_port}/lab?token={cfg.jupyter_token}")
    print(f"  工作区:      {workspace_path}")
    print("=" * 60)
    return cfg


def _stop_via_sdk(client, name: str) -> bool:
    try:
        container = client.containers.get(name)
        if container.status == "running":
            print(f"[SDK] 停止容器: {name}")
            container.stop(timeout=10)
        print(f"[SDK] 删除容器: {name}")
        container.remove(force=True)
        return True
    except PodmanNotFound:
        print(f"[SDK] 容器 {name} 不存在")
        return True
    except Exception as e:
        print(f"[SDK] 停止失败 fallback: {e}")
        return False


def _stop_via_cli(c: Context, name: str) -> None:
    runtime = detect_runtime()
    if not cli_container_exists(c, runtime, name):
        print(f"[CLI] 容器 {name} 不存在")
        return
    print(f"[CLI] 停止容器: {name}")
    run_cmd(c, f"{runtime} stop {name}", warn=True, hide=True, echo=False)
    run_cmd(c, f"{runtime} rm {name}", warn=True, hide=True, echo=False)
    print("[CLI] 容器已停止并删除")


def stop_container(c: Context, name: str) -> None:
    """停止并删除容器（SDK 优先）。"""
    print(f"[Stop] 目标容器: {name}")
    sdk_ok = False
    with get_client() as client:
        if client is not None:
            sdk_ok = _stop_via_sdk(client, name)
    if not sdk_ok:
        _stop_via_cli(c, name)


def _status_via_sdk(client, name: str) -> bool:
    try:
        target = None
        for ct in client.containers.list(all=True):
            if ct.name == name:
                target = ct
                break
        print(f"容器状态: {name}")
        print("-" * 60)
        if target is None:
            print(f"容器 {name} 不存在")
            return True
        target.reload()
        ports_str = ", ".join(
            f"{p.get('HostPort', '?')}->{container_port}"
            for container_port, port_bindings in target.ports.items()
            if port_bindings
            for p in port_bindings or []
        )
        status = target.status
        print(f"  Name:      {target.name}")
        print(f"  Status:    {status}")
        print(f"  Image:     {target.image.tags[0] if target.image.tags else target.short_id}")
        print(f"  Ports:     {ports_str or 'none'}")
        started = target.attrs.get("State", {}).get("StartedAt")
        exited = target.attrs.get("State", {}).get("ExitCode")
        if status == "running" and started:
            print(f"  Started:   {started}")
        if status == "exited" and exited is not None:
            print(f"  ExitCode:  {exited}")
        return True
    except Exception as e:
        print(f"[SDK] status 失败 fallback: {e}")
        return False


def _status_via_cli(c: Context, name: str) -> None:
    runtime = detect_runtime()
    print(f"容器状态: {name}")
    print("-" * 60)
    if not cli_container_exists(c, runtime, name):
        print(f"容器 {name} 不存在")
        return
    go_fmt = "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    result = run_cmd(
        c,
        runtime + ' ps -a --filter name=^' + name + '$ --format "' + go_fmt + '"',
        pty=False,
        echo=False,
    )
    if result:
        print(result.stdout)


def status_container(c: Context, name: str) -> None:
    """查询容器状态（SDK 优先）。"""
    sdk_ok = False
    with get_client() as client:
        if client is not None:
            sdk_ok = _status_via_sdk(client, name)
    if not sdk_ok:
        _status_via_cli(c, name)


def clean_container(c: Context, name: str, tag: str, volume: bool = False, image: bool = False) -> None:
    """清理容器/卷/镜像（SDK 优先）。"""
    print(f"[Clean] 容器={name}  卷={volume}  镜像={image}")
    sdk_ok = False
    with get_client() as client:
        if client is not None:
            try:
                _stop_via_sdk(client, name)
                if volume:
                    print("[SDK] 清理未使用卷...")
                    try:
                        client.volumes.prune()
                    except Exception:
                        pass
                if image:
                    print(f"[SDK] 删除镜像: {tag}")
                    try:
                        img = client.images.get(tag)
                        img.remove(force=True)
                    except Exception:
                        pass
                sdk_ok = True
            except Exception as e:
                print(f"[SDK] clean 失败 fallback: {e}")
    if not sdk_ok:
        runtime = detect_runtime()
        _stop_via_cli(c, name)
        if volume:
            print("[CLI] 清理未使用卷...")
            run_cmd(c, f"{runtime} volume prune -f", warn=True)
        if image:
            print(f"[CLI] 删除镜像: {tag}")
            run_cmd(c, f"{runtime} rmi {tag}", warn=True)
    print("[Clean] 完成")
