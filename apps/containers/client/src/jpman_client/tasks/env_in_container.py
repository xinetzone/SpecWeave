"""在容器内自举 jupyter-podman-client 运行环境的 invoke 任务。

提供三个入口：
  env.build-layer   - 基于 Containerfile.client 构建叠加镜像
                      (localhost/jupyter-podman-client:latest)
  env.run-cmd       - 在自举容器内执行任意一条命令（rootless 三必需 +
                      workspace / .image-cache 双挂载，login shell 自动激活
                      conda main 环境，无需额外 activate）
  env.shell         - 启动交互式 bash shell（进入后可直接 `inv run/stop/status`）

与 manage.py / client_core.py 的关系：
  本模块**不**调用 podman-py SDK（避免在宿主已经 SDK 不连通时陷入循环依赖），
  统一走 utils.detect_runtime() + run_cmd() CLI 子进程。
"""

import platform
import shlex
from pathlib import Path

from invoke import Context, task
from invoke.exceptions import Exit

from .manage import _project_root
from .utils import (
    ContainerConfig,
    detect_runtime,
    default_build_cache_dir,
    normalize_path_str,
    run_cmd,
    to_posix_path,
)


def _quote_bash_script(s: str) -> str:
    """将 bash 脚本（用于 bash -lc <script>）包装成 host shell 认识的单个 CLI 单词。

    - Windows (cmd / pwsh) 不认 shlex.quote 的单引号分组，必须用双引号
      包装，并转义内部双引号 / 反斜杠。
    - POSIX 下走 shlex.quote（单引号）最安全。
    """
    if platform.system() == "Windows":
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return shlex.quote(s)


DEFAULT_CLIENT_IMAGE = "localhost/jupyter-podman-client:latest"
DEFAULT_CLIENT_CONTAINER = "jpman-client-env"

# ---------------------------------------------------------------------------
# R1 修复（C 阶段·原子行动项 C3）：容器内前置启动 podman system service
#
# 背景与根因：bootstrap 用 `--entrypoint /usr/bin/tini` 跳过基础镜像
# entrypoint.sh 的 setup_podman()，而 supervisord 只监督 Jupyter，因此容器内
# 从无运行中的 podman daemon。当 SDK 以 PODMAN_CLIENT_SDK_STRATEGY=legacy 走
# `PodmanClient.from_env()` 时，会连默认 Linux UDS socket
# `/run/user/<UID>/podman/podman.sock`，该文件不存在 → podman/api/uds.py:41
# `super().connect(netloc)` 抛 FileNotFoundError，随后被 urllib3 包装成
# APIError（即截图中"红色报错"的真实形态，注意 netloc 是 UDS socket 路径参数名，
# 不是"缺少 URL netloc"）。
#
# 方案（保留 DinP 自包含语义）：在真正执行 SDK 用到的命令前，先以当前用户
# 启动 rootless `podman system service` 并等待默认 UDS socket 就绪，使
# from_env() 直接连通，同时避免 CLI fallback 的隐式降级。
# 幂等：socket 已存在则跳过（同容器内多次调用只启动一次）。
# 注意：`--time=0` 常驻（不是仅 `podman info` 惰性拉起，后者 socket 命太短）。
# 容器内仍为 devuser 运行，XDG_RUNTIME_DIR 按 $(id -u) 而非硬编码 1000，防 UID 漂移。
# 权限子修复（C3 收边）：bootstrap 跳过 setup_podman() 后容器内无 systemd-logind
# 保证 /run/user/<uid> 属主正确 → devuser 在 root 属主目录下 mkdir 会 Permission denied。
# 利用构建期无条件写入的 NOPASSWD sudo，先 sudo 创建/授权 `${XDG_RUNTIME_DIR}[/podman]`
# 给 devuser，再以普通 mkdir 兜底；整段 `|| true` 确保目录不可写也不中断命令链。
# 启动超时子修复（C3 收边，对应 `podman service 启动超时` 根因）：
#   ① `/dev/fuse` 未 chmod 666：storage driver=overlay→fuse-overlayfs，非 root 需
#      能 open /dev/fuse，否则存储引擎初始化失败，服务进程直接退出、socket 永不创建。
#      与 entrypoint.sh setup_podman() 的 `chmod 666 /dev/fuse` 对齐（bootstrap 跳过它）。
#   ② `podman info` 初始化未运行：setup_podman() 用它触发存储目录创建与配置验证，
#      也是 system service 能正常拉起的前置；此处补齐并与 service 启动对齐。
#   ③ 失败可诊断：服务日志落 /tmp/podman-service.log，超时后 tail 真实错误，
#      替代原先笼统的「SDK 或将降级到 CLI」模糊警告；`timeout 60` 兜底防 fuse 挂载卡死拖垮整个 bootstrap。
# ---------------------------------------------------------------------------
PODMAN_SERVICE_BOOT = (
    "export XDG_RUNTIME_DIR=/run/user/$(id -u); "
    "[ -c /dev/fuse ] && chmod 666 /dev/fuse 2>/dev/null || true; "
    "if ! [ -w \"${XDG_RUNTIME_DIR}/podman\" ]; then "
    "  sudo -n mkdir -p \"${XDG_RUNTIME_DIR}/podman\" 2>/dev/null "
    "    && sudo -n chown -R \"$(id -u):$(id -g)\" \"${XDG_RUNTIME_DIR}\" 2>/dev/null "
    "    || true; "
    "fi; "
    "mkdir -p \"${XDG_RUNTIME_DIR}/podman\" 2>/dev/null || true; "
    "chmod 700 \"${XDG_RUNTIME_DIR}\" 2>/dev/null || true; "
    "# rootless podman 需把 pause.pid 写入 libpod/tmp，目录缺失会报 no such file / Permission denied; "
    "mkdir -p \"${XDG_RUNTIME_DIR}/libpod/tmp\" 2>/dev/null || true; "
    "chmod 700 \"${XDG_RUNTIME_DIR}/libpod/tmp\" 2>/dev/null || true; "
    "echo '[env][SDK就绪] 初始化 rootless podman storage (podman info)...'; "
    "timeout 60 podman info >/dev/null 2>&1 || timeout 60 podman system migrate >/dev/null 2>&1 || true; "
    "if ! [ -S \"${XDG_RUNTIME_DIR}/podman/podman.sock\" ]; then "
    "  nohup podman system service --time=0 >/tmp/podman-service.log 2>&1 </dev/null & "
    "  for _i in $(seq 1 30); do "
    "    [ -S \"${XDG_RUNTIME_DIR}/podman/podman.sock\" ] && break; "
    "    sleep 1; "
    "  done; "
    "  if [ -S \"${XDG_RUNTIME_DIR}/podman/podman.sock\" ]; then "
    "    echo '[env][SDK就绪] podman system service 在线: ${XDG_RUNTIME_DIR}/podman/podman.sock'; "
    "  else "
    "    echo '[env][SDK就绪] ⚠ podman service 启动超时，日志见 /tmp/podman-service.log'; "
    "    tail -n 20 /tmp/podman-service.log 2>/dev/null || true; "
    "  fi; "
    "fi; "
)


def _client_root() -> Path:
    """定位 client 应用根目录（Containerfile.client、pyproject.toml 所在）。"""
    return _project_root()


def _ensure_image_built(c: Context, tag: str) -> None:
    """如果本地没有 client 叠加镜像，给出可执行的修复指令并 Exit。"""
    runtime = detect_runtime()
    r = run_cmd(
        c,
        f'{runtime} images --format="{{{{.Repository}}}}:{{{{.Tag}}}}"',
        hide=True,
        warn=True,
        echo=False,
    )
    if r is None:
        raise Exit(1, "无法查询本地镜像列表")
    lines = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
    if tag in lines:
        return
    print(f"[env] ⚠ 本地未找到叠加镜像: {tag}")
    print("[env]   先执行（首次/修改了 client 源码后）：")
    print(f"[env]     invoke env.build-layer     # 或指定 tag：--tag {tag}")
    raise Exit(1)


# ---------------------------------------------------------------------------
# 镜像构建
# ---------------------------------------------------------------------------


@task(
    help={
        "tag": "产出镜像标签，默认 localhost/jupyter-podman-client:latest",
        "base-image": "基础镜像（ARG BASE_IMAGE），默认 localhost/jupyter-podman-rootless:latest",
        "no-cache": "等价 podman build --no-cache（强制全量重建）",
    }
)
def build_layer(
    c: Context,
    tag: str = DEFAULT_CLIENT_IMAGE,
    base_image: str = "localhost/jupyter-podman-rootless:latest",
    no_cache: bool = False,
) -> None:
    """基于 jupyter-podman-rootless:latest 构建 podman-py SDK 自举叠加层。"""
    runtime = detect_runtime()
    root = _client_root()
    containerfile = root / "Containerfile.client"
    if not containerfile.exists():
        raise Exit(1, f"未找到 Containerfile.client: {containerfile}")

    # 基底指纹（预防闭环）：构建前取基底当前 digest，经 --build-arg 写入镜像
    # LABEL（org.specweave.base-digest），invoke run 启动前据此检测叠加层陈旧。
    # 取不到不阻断构建（指纹留空，run 侧按「无指纹」降级提示）。
    base_digest = ""
    dr = run_cmd(
        c,
        f'{runtime} image inspect --format "{{{{.Digest}}}}" {base_image}',
        hide=True,
        warn=True,
        echo=False,
    )
    if dr is not None and getattr(dr, "ok", False):
        base_digest = (dr.stdout or "").strip()
    if base_digest:
        print(f"[env] 基底指纹: {base_image} -> {base_digest}")
    else:
        print(f"[env] ⚠ 未能获取基底 digest（{base_image}），本次构建不写入基底指纹")

    parts = [
        runtime,
        "build",
        f"-f {containerfile}",
        f"--build-arg BASE_IMAGE={base_image}",
        f"--build-arg BASE_DIGEST={base_digest}",
        f"-t {tag}",
    ]
    if no_cache:
        parts.append("--no-cache")
    # build context = client 根目录（Containerfile 中 COPY . 依赖此目录）
    parts.append(str(root))

    run_cmd(c, " ".join(parts), pty=True)
    print(f"\n[env] ✅ 叠加镜像构建完成: {tag}")
    print("[env]   快速验证：  invoke env.run-cmd --cmd \"inv --list\"")


# ---------------------------------------------------------------------------
# 容器内命令执行（单条）
# ---------------------------------------------------------------------------


@task(
    help={
        "cmd": "在容器内执行的命令（会被 bash -lc 登录 shell 包裹，自动激活 conda main，无需显式 activate）",
        "tag": "使用的叠加镜像标签",
        "name": "容器名（默认 jpman-client-env，用完自动删除）",
        "workspace": "挂载到容器内 /workspace 的宿主路径（默认 = IMAGE_CACHE_DIR 的父目录 / 当前执行目录）",
        "cache-dir": "挂载到容器内 /workspace/.image-cache 的宿主镜像缓存目录",
        "keep": "执行完毕后保留容器（用于排障），默认 --rm",
        "extra-mount": "追加卷挂载，格式=宿主绝对路径:容器内路径，可重复传多次（逗号分隔）",
    },
    iterable=["extra_mount"],
)
def run_cmd_(
    c: Context,
    cmd: str,
    tag: str = DEFAULT_CLIENT_IMAGE,
    name: str = DEFAULT_CLIENT_CONTAINER,
    workspace: str | None = None,
    cache_dir: str | None = None,
    keep: bool = False,
    extra_mount: list[str] | None = None,
) -> None:
    """在自举容器内执行一条命令（自动挂载 workspace/.image-cache，rootless 三必需）。"""
    _ensure_image_built(c, tag)
    runtime = detect_runtime()

    # ---- 挂载路径计算（Dimension A：宿主路径→POSIX，防止 Windows Python 误判）
    cache_path = Path(cache_dir) if cache_dir else default_build_cache_dir()
    if workspace:
        ws_path = Path(workspace).expanduser().resolve()
    else:
        # 未指定 workspace：默认缓存目录的父目录（一般即 client/ 或 SpecWeave 根）
        ws_path = cache_path.parent.resolve()
    if not ws_path.exists():
        ws_path.mkdir(parents=True, exist_ok=True)
    if not cache_path.exists():
        cache_path.mkdir(parents=True, exist_ok=True)
    ws_posix = to_posix_path(ws_path)
    cache_posix = to_posix_path(cache_path)

    inner_bash = (
        f"{PODMAN_SERVICE_BOOT}"
        f". /opt/conda/etc/profile.d/conda.sh && conda activate main && {cmd}"
    )

    parts = [runtime, "run", "--rm" if not keep else "", f"--name {name}"]
    # ---- rootless 三必需（与 ContainerConfig 硬编码一致，C3 约束）
    parts.append("--device /dev/fuse")
    parts.append("--security-opt label=disable")
    parts.append("--cgroupns=host")
    # ---- 跳过基础镜像 entrypoint.sh：显式用 tini 当 init，直接跑 bash 命令
    #      （避免 entrypoint.sh 里 setup_passwords 在某些 sandbox 环境触发 PAM chpasswd 失败）
    # ---- 同时提供 USER_PASSWORD 和 GRANT_SUDO，保证就算某些 entrypoint 路径执行也不会因为密码生成失败
    parts.append("-e USER_PASSWORD=devpass")
    parts.append("-e GRANT_SUDO=yes")
    parts.append("--entrypoint /usr/bin/tini")
    # ---- 双挂载
    parts.extend(["-v", f"{ws_posix}:/workspace"])
    parts.extend(["-v", f"{cache_posix}:/workspace/.image-cache"])
    # ---- 额外挂载
    for m in extra_mount or []:
        if not m or ":" not in m:
            continue
        src, dst = m.split(":", 1)
        src_posix = normalize_path_str(src) if Path(src).is_absolute() else src
        parts.extend(["-v", f"{src_posix}:{dst}"])
    # ---- 镜像 + tini 后接命令（tini -- bash -lc '<script>'）
    parts.append(tag)
    parts.append("--")
    # 注意：bash -lc 后面的 inner_bash 必须作为一个 shell 单词传递
    # （里面有 &&/空格/引号 等特殊字符）。Windows 下 shell 用双引号分组，
    # POSIX 用 shlex.quote（单引号），用 _quote_bash_script() 统包。
    parts.extend(["bash", "-lc", _quote_bash_script(inner_bash)])

    # 过滤掉 "" 空元素（如 --rm="" 会导致 shell 收到空参数）
    cleaned = [p for p in parts if p != ""]
    run_cmd(c, " ".join(cleaned), pty=True)


# ---------------------------------------------------------------------------
# 交互式 shell
# ---------------------------------------------------------------------------


@task(
    help={
        "tag": "使用的叠加镜像标签",
        "name": "容器名（用完自动删除）",
        "workspace": "宿主 workspace 路径（默认 IMAGE_CACHE_DIR 的父目录）",
        "cache-dir": "宿主镜像缓存目录（默认 IMAGE_CACHE_DIR env / ./.image-cache）",
        "extra-mount": "追加挂载，宿主绝对路径:容器内路径，逗号分隔或重复传",
    },
    iterable=["extra_mount"],
)
def shell(
    c: Context,
    tag: str = DEFAULT_CLIENT_IMAGE,
    name: str = DEFAULT_CLIENT_CONTAINER,
    workspace: str | None = None,
    cache_dir: str | None = None,
    extra_mount: list[str] | None = None,
) -> None:
    """启动一个交互式 bash shell（进入后可直接 inv load/run/stop/status）。"""
    _ensure_image_built(c, tag)
    runtime = detect_runtime()

    cache_path = Path(cache_dir) if cache_dir else default_build_cache_dir()
    ws_path = (
        Path(workspace).expanduser().resolve()
        if workspace
        else cache_path.parent.resolve()
    )
    if not ws_path.exists():
        ws_path.mkdir(parents=True, exist_ok=True)
    if not cache_path.exists():
        cache_path.mkdir(parents=True, exist_ok=True)
    ws_posix = to_posix_path(ws_path)
    cache_posix = to_posix_path(cache_path)

    parts = [runtime, "run", "--rm", "-it", f"--name {name}"]
    # rootless 三必需
    parts.append("--device /dev/fuse")
    parts.append("--security-opt label=disable")
    parts.append("--cgroupns=host")
    # 跳过基础镜像 entrypoint.sh：显式 tini + USER_PASSWORD，避免 sandbox 下 PAM chpasswd 失败
    parts.append("-e USER_PASSWORD=devpass")
    parts.append("-e GRANT_SUDO=yes")
    parts.append("--entrypoint /usr/bin/tini")
    # 双挂载
    parts.extend(["-v", f"{ws_posix}:/workspace"])
    parts.extend(["-v", f"{cache_posix}:/workspace/.image-cache"])
    for m in extra_mount or []:
        if not m or ":" not in m:
            continue
        src, dst = m.split(":", 1)
        src_posix = normalize_path_str(src) if Path(src).is_absolute() else src
        parts.extend(["-v", f"{src_posix}:{dst}"])
    parts.append(tag)
    parts.append("--")
    # 登录式 bash（激活 conda main + 进入 /workspace + 友好提示）。
    # Windows 下用双引号分组，POSIX 下 shlex.quote，用 _quote_bash_script()。
    shell_script = (
        f"{PODMAN_SERVICE_BOOT}"
        ". /opt/conda/etc/profile.d/conda.sh"
        " && conda activate main"
        " && cd /workspace"
        " && echo '=== jupyter-podman-client 自举环境 ==='"
        " && echo '[可用命令]  inv --list   inv load   inv run   inv stop   inv status'"
        " && echo '[退出]      exit'"
        " && exec bash -i"
    )
    parts.extend(["bash", "-lc", _quote_bash_script(shell_script)])
    run_cmd(c, " ".join(parts), pty=True)
