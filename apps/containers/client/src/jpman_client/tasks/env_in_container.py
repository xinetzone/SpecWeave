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

    parts = [
        runtime,
        "build",
        f"-f {containerfile}",
        f"--build-arg BASE_IMAGE={base_image}",
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
