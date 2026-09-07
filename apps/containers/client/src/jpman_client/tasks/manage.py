"""镜像消费端 invoke 任务入口。

提供面向用户的 6 个核心命令：
  load    - 从本地 tar.gz 加载镜像（默认自动搜索构建端缓存）
  images  - 列出本地 podman 镜像
  run     - 启动容器（自动填充密码/token，rootless 三必需参数内置）
  stop    - 停止并删除容器
  status  - 查看容器状态
  clean   - 清理容器/卷/镜像

配置优先级：命令行参数 > .env 环境变量 > ContainerConfig 默认值。

Windows WSL 支持（OKF v0.2 podman-py §8 三路径）：
  本模块在读取 .env 时会 **同步写入 os.environ**（dotenv ``load_dotenv``，
  默认不覆盖 shell 已有变量），因此以下 SDK 专属变量既可以写在终端
  ``export`` / ``$env:``，也可以直接放到本应用根目录 ``.env`` 里：

  .. code-block:: bash

     # ---- 写到 apps/containers/client/.env 即可，不需要手动 export ----

     # [可选·逃生舱] 连接候选策略  auto|legacy|wsl|machine  （默认 auto）
     PODMAN_CLIENT_SDK_STRATEGY=auto

     # [可选·策略=wsl 或 auto 时] 显式指定 WSL2 发行版名
     # 不设时自动探测（默认发行版 → Running 首个）
     WSL_DISTRO_NAME=Ubuntu

     # [可选·最高优先级] 直接指定 podman-py base_url（6 scheme 合法）
     # 未设时按 P0→P3 自动探测。例：
     #   unix:///mnt/wsl/Ubuntu/run/user/1000/podman/podman.sock
     #   tcp://127.0.0.1:8888
     CONTAINER_HOST=unix:///mnt/wsl/Ubuntu/run/user/1000/podman/podman.sock
     # DOCKER_HOST=...  # docker 兼容兜底，优先级低于 CONTAINER_HOST
"""
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
from invoke import Context, task
from invoke.exceptions import Exit

from .client_core import (
    clean_container,
    image_exists,
    list_images,
    load_image,
    run_container,
    status_container,
    stop_container,
)
from .utils import (
    ContainerConfig,
    default_build_cache_dir,
    find_latest_image_tar,
    normalize_path_str,
)


def _load_env_overrides(project_root: Path) -> dict:
    """读取 .env（若存在），覆盖 ContainerConfig 默认值。

    关键副作用（Windows WSL 支持必须）：
      用 ``load_dotenv(override=False)`` 把 .env 中的键值同步到 ``os.environ``，
      保证 utils 层读取 ``os.environ`` 的逻辑（SDK 策略、WSL 发行版名、
      CONTAINER_HOST 显式 URL 等）也能拿到 .env 里写的值。
      ``override=False`` 表示：shell 中用户已 ``export`` / ``$env:`` 的变量
      **优先级更高**，不会被 .env 覆盖，符合"命令行 > .env > 默认"约定。
    """
    env_path = project_root / ".env"
    if env_path.exists():
        # 先同步到 os.environ（SDK 策略层需要读环境变量）
        load_dotenv(dotenv_path=str(env_path), override=False, verbose=False)
        # 再拿 dict 供 _merge_config 合并 ContainerConfig 专用字段
        return {k: v for k, v in dict(dotenv_values(str(env_path))).items() if v}
    return {}


def _project_root() -> Path:
    return Path(__file__).parent.parent.resolve()


def _merge_config(
    name,
    tag,
    ssh_port,
    jupyter_port,
    workspace,
    user_password,
    jupyter_token,
    ssh_public_key,
    grant_sudo,
) -> ContainerConfig:
    """根据 args > .env > 默认 的优先级合并配置。"""
    project_root = _project_root()
    env = _load_env_overrides(project_root)

    def pick(arg_val, env_key, default):
        if arg_val is not None and arg_val not in ("", False):
            return arg_val
        if env_key in env:
            return env[env_key]
        return default

    cfg = ContainerConfig(
        image=str(pick(tag, "IMAGE_TAG", ContainerConfig.image)),
        name=str(pick(name, "CONTAINER_NAME", ContainerConfig.name)),
        ssh_port=int(pick(ssh_port, "SSH_PORT", ContainerConfig.ssh_port)),
        jupyter_port=int(pick(jupyter_port, "JUPYTER_PORT", ContainerConfig.jupyter_port)),
        workspace=str(
            normalize_path_str(str(pick(workspace, "WORKSPACE", ContainerConfig.workspace)))
        ),
        user_password=str(pick(user_password, "USER_PASSWORD", "")),
        jupyter_token=str(pick(jupyter_token, "JUPYTER_TOKEN", "")),
        ssh_public_key=str(pick(ssh_public_key, "SSH_PUBLIC_KEY", "")),
        grant_sudo=bool(pick(grant_sudo, "GRANT_SUDO", ContainerConfig.grant_sudo)),
    )
    return cfg


# ---------------------------------------------------------------------------
# 镜像命令
# ---------------------------------------------------------------------------


@task(
    help={
        "path": "镜像 tar.gz 路径。未指定时自动从构建端 .image-cache 找最新文件",
        "cache-dir": "构建端缓存目录，默认 ../jupyter-podman-rootless/.image-cache",
    }
)
def load(c: Context, path: str | None = None, cache_dir: str | None = None) -> None:
    """从本地 tar.gz 加载 jupyter-podman-rootless 镜像。"""
    cache_path = Path(cache_dir) if cache_dir else default_build_cache_dir()

    if path:
        tar_path = Path(path).resolve()
    else:
        tar_path = find_latest_image_tar(cache_path)
        if tar_path is None:
            print(f"[Load] 缓存目录中未找到 tar.gz: {cache_path}")
            print("[Load] 请先在构建端执行: cd ../jupyter-podman-rootless && bash bin/jpman save")
            raise Exit(1)
        print(f"[Load] 自动选择最新缓存: {tar_path}")

    result = load_image(c, tar_path)
    if not result.loaded:
        raise Exit(1, result.message)


@task
def images(c: Context) -> None:
    """列出本地所有容器镜像。"""
    rows = list_images(c)
    if not rows:
        print("(本地镜像列表为空)")
        return
    print(f"{'ID':<14} {'SIZE':<12} TAGS")
    print("-" * 72)
    for r in rows:
        tags = ", ".join(r["tags"]) if r["tags"] else "<none>"
        size = r.get("size") or ""
        print(f"{r['id']:<14} {str(size):<12} {tags}")


# ---------------------------------------------------------------------------
# 容器生命周期命令
# ---------------------------------------------------------------------------


@task(
    help={
        "name": "容器名（默认 jupyter-podman）",
        "tag": "镜像标签（默认 localhost/jupyter-podman-rootless:latest）",
        "ssh-port": "SSH 端口",
        "jupyter-port": "Jupyter 端口",
        "workspace": "工作区路径，支持 Windows/WSL 自动转换",
        "user-password": "devuser 登录密码（未指定自动生成 16 位）",
        "jupyter-token": "Jupyter token（未指定自动生成 32 位）",
        "ssh-public-key": "注入的 SSH 公钥字符串",
        "grant-sudo": "是否开启容器内 sudo（默认 True）",
        "no-detach": "前台运行而非后台",
    }
)
def run(
    c: Context,
    name: str | None = None,
    tag: str | None = None,
    ssh_port: int | None = None,
    jupyter_port: int | None = None,
    workspace: str | None = None,
    user_password: str | None = None,
    jupyter_token: str | None = None,
    ssh_public_key: str | None = None,
    grant_sudo: bool = True,
    no_detach: bool = False,
) -> None:
    """启动 jupyter-podman-rootless 容器（SDK 优先，CLI fallback）。"""
    cfg = _merge_config(
        name=name,
        tag=tag,
        ssh_port=ssh_port,
        jupyter_port=jupyter_port,
        workspace=workspace,
        user_password=user_password,
        jupyter_token=jupyter_token,
        ssh_public_key=ssh_public_key,
        grant_sudo=grant_sudo,
    )
    cfg.detach = not no_detach

    if not image_exists(c, cfg.image):
        print(f"[Run] ⚠ 本地未找到镜像: {cfg.image}")
        print("[Run]   先执行: invoke load    （从构建端缓存加载）")
        print("[Run]   或执行: cd ../jupyter-podman-rootless && bash bin/jpman rebuild-all")
        raise Exit(1)

    run_container(c, cfg)


@task(help={"name": "容器名（默认 jupyter-podman）"})
def stop(c: Context, name: str | None = None) -> None:
    """停止并删除容器（不删镜像和工作区数据）。"""
    env = _load_env_overrides(_project_root())
    target = name or env.get("CONTAINER_NAME", ContainerConfig.name)
    stop_container(c, str(target))


@task(help={"name": "容器名（默认 jupyter-podman）"})
def status(c: Context, name: str | None = None) -> None:
    """查看容器运行状态。"""
    env = _load_env_overrides(_project_root())
    target = name or env.get("CONTAINER_NAME", ContainerConfig.name)
    status_container(c, str(target))


@task(
    help={
        "name": "容器名",
        "tag": "需要删除的镜像标签（--image 时使用）",
        "volume": "同时清理未使用的卷",
        "image": "同时删除本地镜像（谨慎使用）",
    }
)
def clean(
    c: Context,
    name: str | None = None,
    tag: str | None = None,
    volume: bool = False,
    image: bool = False,
) -> None:
    """清理容器资源（谨慎使用 --image）。"""
    env = _load_env_overrides(_project_root())
    target_name = str(name or env.get("CONTAINER_NAME", ContainerConfig.name))
    target_tag = str(tag or env.get("IMAGE_TAG", ContainerConfig.image))
    clean_container(c, target_name, target_tag, volume=volume, image=image)
