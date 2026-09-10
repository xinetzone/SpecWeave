"""本地 OCI model-registry 生命周期任务（compose `model-registry` 服务的等价替代）。

**为什么需要本模块**：`model-registry` 此前只能由 compose 的 `--profile registry`
启动，而 podman-compose 在 Windows 原生宿主上不可用（见 `client.compose_available()`），
导致该服务在 Windows 上**没有任何启动路径**。本模块以 SDK→CLI 两层实现同一服务，
关键参数（容器名、卷名、端口、环境变量、重启策略、网络别名）与 `compose.yaml` 的
`model-registry` 服务**对齐**，使两种启动方式指向同一份数据卷、同一宿主端口。

用法：
    invoke registry.up                  # 启动（默认宿主端口 5000）
    invoke registry.up --port 5001      # 改宿主端口
    invoke registry.down                # 停止并删除容器（保留卷）
    invoke registry.down --volumes      # 连同数据卷一起删除
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values
from invoke import task
from invoke.exceptions import Exit

from .client import PodmanNotFound, get_client, sdk_available
from .utils import (
    check_runtime_ready,
    container_exists as cli_container_exists,
    detect_runtime,
    run_cmd,
)

# ── 与 compose.yaml 的 model-registry 服务保持同步的常量（改动须两处同步）──
COMPOSE_PROJECT = "jupyter-podman-rootless"           # compose.yaml 顶层 `name:`
COMPOSE_NETWORK = f"{COMPOSE_PROJECT}_default"        # podman-compose 生成的项目网络
REGISTRY_SERVICE_ALIAS = "model-registry"             # compose 服务名 → 容器内 DNS 名
REGISTRY_VOLUME = f"{COMPOSE_PROJECT}_registry-data"  # podman-compose 的 <project>_<volume>
REGISTRY_IMAGE = "registry:2"                         # compose.yaml 的 `image:`
REGISTRY_INNER_PORT = 5000                            # 容器内监听端口（不可改）
REGISTRY_DATA_DIR = "/var/lib/registry"
REGISTRY_RESTART_POLICY = "unless-stopped"
REGISTRY_ENV = {
    "REGISTRY_STORAGE_DELETE_ENABLED": "true",
    "REGISTRY_HTTP_ADDR": f"0.0.0.0:{REGISTRY_INNER_PORT}",
}


def _compose_root() -> Path:
    """定位 compose 项目根（向上找到含 compose.yaml 的目录，用于读取 .env）。"""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "compose.yaml").is_file():
            return current
        current = current.parent
    raise Exit("无法定位应用根目录：从模块路径向上未找到含 compose.yaml 的目录")


def _registry_port(c, port):
    """解析宿主端口：显式参数 > REGISTRY_PORT 环境变量 > .env > invoke 配置默认值。"""
    if port is not None:
        return int(port)
    if os.environ.get("REGISTRY_PORT"):
        return int(os.environ["REGISTRY_PORT"])
    env_path = _compose_root() / ".env"
    if env_path.exists():
        value = (dotenv_values(str(env_path)) or {}).get("REGISTRY_PORT")
        if value:
            return int(value)
    return int(c.registry.get("port", REGISTRY_INNER_PORT))


def _compose_network_exists(c, runtime) -> bool:
    """compose 项目网络是否已存在（决定能否挂 model-registry 别名）。

    注意：run_cmd 返回的是 invoke `Result`（属性为 `ok`/`return_code`），
    不是 subprocess.CompletedProcess（后者才是 `returncode`）。
    """
    result = run_cmd(
        c, f"{runtime} network exists {COMPOSE_NETWORK}", warn=True, hide=True, echo=False
    )
    return bool(result and result.ok)


def _registry_name(c) -> str:
    """容器名：与 compose.yaml 的 `${CONTAINER_NAME:-jupyter-podman}-registry` 对齐。"""
    base = c.container.get("container_name", "jupyter-podman")
    return f"{base}-registry"


def _up_via_sdk(client, name, port):
    """经 SDK 启动 registry。成功返回 True。"""
    try:
        try:
            old = client.containers.get(name)
            print(f"[SDK] Found old registry container {name}, removing...")
            old.remove(force=True)
        except PodmanNotFound:
            pass

        print(f"[SDK] Starting registry: {name}")
        container = client.containers.run(
            image=REGISTRY_IMAGE,
            name=name,
            ports={f"{REGISTRY_INNER_PORT}/tcp": port},
            volumes={REGISTRY_VOLUME: {"bind": REGISTRY_DATA_DIR, "mode": "rw"}},
            environment=dict(REGISTRY_ENV),
            restart_policy={"Name": REGISTRY_RESTART_POLICY},
            detach=True,
        )
        container.reload()
        print(f"[SDK] Registry started (detached): {container.short_id}")
        return True
    except Exception as e:
        print(f"[SDK] Registry start failed, falling back to CLI: {e}")
        return False


def _up_via_cli(c, name, port):
    """经 CLI 启动 registry。"""
    runtime = detect_runtime()

    if cli_container_exists(c, runtime, name):
        print(f"Registry container {name} already exists, removing first...")
        run_cmd(c, f"{runtime} rm -f {name}", warn=True, hide=True, echo=False)

    cmd_parts = [
        runtime, "run", "-d",
        "--name", name,
        "-p", f"{port}:{REGISTRY_INNER_PORT}",
        "-v", f"{REGISTRY_VOLUME}:{REGISTRY_DATA_DIR}",
        "--restart", REGISTRY_RESTART_POLICY,
    ]

    # 容器内 DNS 名 `model-registry` 只在 compose 项目网络（user-defined）上可解析，
    # 且 --network-alias 不允许用于默认网络——故仅在项目网络存在时挂载。
    if _compose_network_exists(c, runtime):
        cmd_parts.extend(["--network", COMPOSE_NETWORK, "--network-alias", REGISTRY_SERVICE_ALIAS])
    else:
        print(
            f"[Note] compose 项目网络 {COMPOSE_NETWORK} 不存在，registry 使用默认网络；"
            f"容器内无法用 http://{REGISTRY_SERVICE_ALIAS}:{REGISTRY_INNER_PORT} 访问，"
            f"请改用宿主端口或容器名 {name}"
        )

    for key, value in REGISTRY_ENV.items():
        cmd_parts.extend(["-e", f"{key}={value}"])

    cmd_parts.append(REGISTRY_IMAGE)
    run_cmd(c, " ".join(cmd_parts))
    print(f"Registry started: {name} (host {port} -> container {REGISTRY_INNER_PORT})")


def _remove_volume_via_sdk(client):
    """经 SDK 删除数据卷（--volumes 时调用）。"""
    print(f"[SDK] Removing volume: {REGISTRY_VOLUME}")
    client.volumes.get(REGISTRY_VOLUME).remove(force=True)


def _down_via_sdk(client, name, volumes):
    """经 SDK 停止并删除 registry。成功返回 True。"""
    try:
        try:
            container = client.containers.get(name)
            if container.status == "running":
                print(f"[SDK] Stopping registry: {name}")
                container.stop(timeout=10)
            print(f"[SDK] Removing registry container: {name}")
            container.remove(force=True)
        except PodmanNotFound:
            print(f"Registry container {name} does not exist, nothing to stop")
        if volumes:
            _remove_volume_via_sdk(client)
        return True
    except Exception as e:
        print(f"[SDK] Registry stop failed, falling back to CLI: {e}")
        return False


def _down_via_cli(c, name, volumes):
    """经 CLI 停止并删除 registry。"""
    runtime = detect_runtime()
    if cli_container_exists(c, runtime, name):
        print(f"Stopping registry container: {name}")
        run_cmd(c, f"{runtime} stop {name}", warn=True, hide=True, echo=False)
        run_cmd(c, f"{runtime} rm {name}", warn=True, hide=True, echo=False)
        print(f"Registry container {name} stopped and removed")
    else:
        print(f"Registry container {name} does not exist, nothing to stop")
    if volumes:
        print(f"Removing volume: {REGISTRY_VOLUME}")
        # 卷可能仍被其它容器占用（如 compose 栈），失败只告警不中断
        run_cmd(c, f"{runtime} volume rm {REGISTRY_VOLUME}", warn=True)


@task
def up(c, port=None):
    """Start the local OCI model-registry.

    等价于 `podman-compose --profile registry up -d`，但不依赖 compose——
    Windows 原生宿主（compose 后端不可用）亦可使用。参数与 compose.yaml 的
    `model-registry` 服务对齐，两种方式共享同一数据卷。

    Tier 2: podman-py SDK
    Tier 3: CLI
    """
    ready, hint = check_runtime_ready()
    if not ready:
        print(f"[Error] {hint}")
        raise Exit(1)

    name = _registry_name(c)
    host_port = _registry_port(c, port)

    sdk_ok = False
    if sdk_available():
        with get_client() as client:
            if client is not None:
                sdk_ok = _up_via_sdk(client, name, host_port)
    if not sdk_ok:
        _up_via_cli(c, name, host_port)

    print("\n" + "=" * 60)
    print("Registry access:")
    print(f"  From host:               localhost:{host_port}")
    print(f"  From jupyter container:  http://{REGISTRY_SERVICE_ALIAS}:{REGISTRY_INNER_PORT}"
          f"  (needs compose network {COMPOSE_NETWORK})")
    print(f"  Data volume:             {REGISTRY_VOLUME}")
    print("=" * 60)


@task
def down(c, volumes=False):
    """Stop and remove the local OCI model-registry.

    Args:
        volumes: 同时删除数据卷 `jupyter-podman-rootless_registry-data`（不可恢复）。

    Tier 2: podman-py SDK
    Tier 3: CLI
    """
    name = _registry_name(c)

    sdk_ok = False
    if sdk_available():
        with get_client() as client:
            if client is not None:
                sdk_ok = _down_via_sdk(client, name, volumes)
    if not sdk_ok:
        _down_via_cli(c, name, volumes)
