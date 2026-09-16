"""Jupyter Podman Rootless container lifecycle management tasks.

Provides container start, stop, status, and cleanup functionality.
Three-tier backend priority:
  1. podman-compose (declarative YAML, daemon-less, rootless-first)
  2. podman-py SDK (REST API)
  3. CLI direct calls (fallback)
"""
import os
from pathlib import Path

from dotenv import dotenv_values
from invoke import Context, task
from invoke.exceptions import Exit, UnexpectedExit

from .client import (
    HOST_KEY_DIR,
    HOST_KEY_VOLUME,
    PodmanNotFound,
    compose_available,
    get_client,
    podman_sock_path,
    sdk_available,
    sdk_run_kwargs,
)
from .compose_backend import compose_down, compose_ps, compose_up, is_compose_ready
from .utils import (
    PHASE_ABSENT,
    PHASE_RUNNING,
    PHASE_STOPPED,
    PHASE_UNKNOWN,
    check_runtime_ready,
    container_exists as cli_container_exists,
    container_phase,
    detect_runtime,
    generate_random_string,
    normalize_path_str,
    run_cmd,
    to_posix_path,
)


def _load_or_create_env(c, project_root, ssh_port, jupyter_port, workspace,
                        user_password, jupyter_token, ssh_public_key, grant_sudo,
                        apt_mirror, conda_mirror, pip_mirror):
    """Load .env file, auto-generate empty secrets, write back if needed.

    Returns dict of effective environment variables for compose.
    """
    env_path = project_root / ".env"
    env_vars = {}

    # Load existing .env if present
    if env_path.exists():
        env_vars = dict(dotenv_values(str(env_path)))

    # Build effective values: explicit args > .env > defaults
    def get_val(key, arg_val, default):
        if arg_val is not None:
            return str(arg_val)
        return env_vars.get(key, str(default))

    effective = {
        "CONTAINER_NAME": get_val("CONTAINER_NAME", None, c.container.get("container_name", "jupyter-podman")),
        "IMAGE_TAG": get_val("IMAGE_TAG", None, c.container.get("image_tag", "jupyter-podman-rootless:latest")),
        "SSH_PORT": get_val("SSH_PORT", ssh_port, c.container.get("ssh_port", 2222)),
        "JUPYTER_PORT": get_val("JUPYTER_PORT", jupyter_port, c.container.get("jupyter_port", 8888)),
        "WORKSPACE": normalize_path_str(get_val("WORKSPACE", workspace, c.container.get("workspace", "./workspace"))),
        "USER_PASSWORD": get_val("USER_PASSWORD", None, ""),
        "JUPYTER_TOKEN": get_val("JUPYTER_TOKEN", None, ""),
        "SSH_PUBLIC_KEY": get_val("SSH_PUBLIC_KEY", ssh_public_key, ""),
        "GRANT_SUDO": "yes" if grant_sudo else get_val("GRANT_SUDO", None, "no"),
        "APT_MIRROR": get_val("APT_MIRROR", apt_mirror, c.container.get("mirrors", {}).get("apt", "official")),
        "CONDA_MIRROR": get_val("CONDA_MIRROR", conda_mirror, c.container.get("mirrors", {}).get("conda", "official")),
        "PIP_MIRROR": get_val("PIP_MIRROR", pip_mirror, c.container.get("mirrors", {}).get("pip", "official")),
    }

    # Auto-generate secrets if empty
    write_back = False
    if not effective["USER_PASSWORD"] or effective["USER_PASSWORD"] == "changeme":
        effective["USER_PASSWORD"] = user_password or generate_random_string(16)
        print(f"[Env] Auto-generated user password: {effective['USER_PASSWORD']}")
        write_back = True
    if not effective["JUPYTER_TOKEN"] or effective["JUPYTER_TOKEN"] == "changeme":
        effective["JUPYTER_TOKEN"] = jupyter_token or generate_random_string(32)
        print(f"[Env] Auto-generated Jupyter token: {effective['JUPYTER_TOKEN']}")
        write_back = True

    # Write .env if we generated secrets or file doesn't exist
    if write_back or not env_path.exists():
        lines = [
            "# Jupyter Podman Rootless - Auto-generated .env",
            f"CONTAINER_NAME={effective['CONTAINER_NAME']}",
            f"IMAGE_TAG={effective['IMAGE_TAG']}",
            f"SSH_PORT={effective['SSH_PORT']}",
            f"JUPYTER_PORT={effective['JUPYTER_PORT']}",
            f"WORKSPACE={effective['WORKSPACE']}",
            f"USER_PASSWORD={effective['USER_PASSWORD']}",
            f"JUPYTER_TOKEN={effective['JUPYTER_TOKEN']}",
            f"SSH_PUBLIC_KEY={effective['SSH_PUBLIC_KEY']}",
            f"GRANT_SUDO={effective['GRANT_SUDO']}",
            f"APT_MIRROR={effective['APT_MIRROR']}",
            f"CONDA_MIRROR={effective['CONDA_MIRROR']}",
            f"PIP_MIRROR={effective['PIP_MIRROR']}",
        ]
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[Env] Wrote configuration to {env_path}")

    return effective


def _should_use_compose():
    """Check if we should use podman-compose backend."""
    return compose_available() and is_compose_ready()


def _stop_via_sdk(client, name):
    """Stop and remove container via SDK. Returns True on success."""
    try:
        container = client.containers.get(name)
        if container.status == "running":
            print(f"[SDK] Stopping container: {name}")
            container.stop(timeout=10)
        print(f"[SDK] Removing container: {name}")
        container.remove(force=True)
        return True
    except PodmanNotFound:
        print(f"Container {name} does not exist, nothing to stop")
        return True
    except Exception as e:
        print(f"[SDK] Stop failed, falling back to CLI: {e}")
        return False


def _stop_via_cli(c, name):
    """Stop and remove container via CLI (original logic)."""
    runtime = detect_runtime()
    if not cli_container_exists(c, runtime, name):
        print(f"Container {name} does not exist, nothing to stop")
        return
    print(f"Stopping container: {name}")
    run_cmd(c, f"{runtime} stop {name}", warn=True, hide=True, echo=False)
    run_cmd(c, f"{runtime} rm {name}", warn=True, hide=True, echo=False)
    print(f"Container {name} stopped and removed")


def _run_via_sdk(client, name, tag, ssh_port, jupyter_port, workspace_posix,
                 user_password, jupyter_token, ssh_public_key, grant_sudo, detach):
    """Start container via SDK. Returns True on success."""
    try:
        try:
            old = client.containers.get(name)
            print(f"[SDK] Found old container {name}, removing...")
            old.remove(force=True)
        except PodmanNotFound:
            pass

        run_kwargs = sdk_run_kwargs(
            ssh_port=ssh_port,
            jupyter_port=jupyter_port,
            workspace_posix=workspace_posix,
            name=name,
            tag=tag,
            user_password=user_password,
            jupyter_token=jupyter_token,
            ssh_public_key=ssh_public_key,
            grant_sudo=grant_sudo,
            detach=detach,
        )

        print(f"[SDK] Starting container: {name}")
        container = client.containers.run(**run_kwargs)

        if detach:
            container.reload()
            print(f"[SDK] Container started (detached): {container.short_id}")
        else:
            print("[SDK] Container started in foreground")
        return True
    except Exception as e:
        print(f"[SDK] Start failed, falling back to CLI: {e}")
        return False


def _run_via_cli(c, name, tag, ssh_port, jupyter_port, workspace_posix,
                 user_password, jupyter_token, ssh_public_key, grant_sudo, detach):
    """Start container via CLI (original logic)."""
    runtime = detect_runtime()

    if cli_container_exists(c, runtime, name):
        print(f"Container {name} already exists, stopping and removing first...")
        _stop_via_cli(c, name)

    cmd_parts = [
        runtime,
        "run",
        "--name", name,
        "-p", f"{ssh_port}:22",
        "-p", f"{jupyter_port}:8888",
        "-v", f"{workspace_posix}:/workspace",
        # B-scheme: 直连宿主 rootless daemon（绕过嵌套 userns）。
        # 宿主 socket bind-mount 到容器同一路径，容器内 podman CLI 即可连通。
        "-v", f"{podman_sock_path()}:{podman_sock_path()}",
        # SSH host key 持久化：容器删除重建不轮换密钥（与 compose.yaml 同名卷对齐）
        "-v", f"{HOST_KEY_VOLUME}:{HOST_KEY_DIR}",
        "--device /dev/fuse",
        "--security-opt label=disable",
        "--cgroupns=host",
    ]

    if detach:
        cmd_parts.append("-d")

    cmd_parts.extend(["-e", f"USER_PASSWORD={user_password}"])
    cmd_parts.extend(["-e", f"JUPYTER_TOKEN={jupyter_token}"])
    # B-scheme: 告知 entrypoint 宿主 daemon socket 已 bind-mount 到容器内路径，
    # 由它建立 devuser 可控符号链接并设置 CONTAINER_HOST（绕过嵌套 userns）。
    cmd_parts.extend(["-e", f"HOST_PODMAN_SOCK={podman_sock_path()}"])

    if ssh_public_key:
        cmd_parts.extend(["-e", f'SSH_PUBLIC_KEY="{ssh_public_key}"'])
    if grant_sudo:
        cmd_parts.extend(["-e", "GRANT_SUDO=yes"])

    cmd_parts.append(tag)
    cmd = " ".join(cmd_parts)
    run_cmd(c, cmd, pty=not detach)

    if detach:
        print("Container started (detached)")
    else:
        print("Container started in foreground")


def _read_container_env(c, name):
    """从现存容器读回启动时注入的 USER_PASSWORD / JUPYTER_TOKEN。

    幂等分支（同名容器已在运行）需要展示**真实**访问凭证而非新生成一组；
    探测失败返回空 dict，调用方降级为不显示凭证。
    """
    runtime = detect_runtime()
    # 单引号而非双引号：invoke 在 Windows 把命令包装为 pwsh /c "<cmd>"，内嵌双引号
    # 会截断外层引用（见 shared containers.py 模块注释的实证）。
    result = run_cmd(
        c,
        runtime + ' inspect ' + name
        + " --format '{{range .Config.Env}}{{println .}}{{end}}'",
        hide=True,
        warn=True,
        echo=False,
    )
    env: dict[str, str] = {}
    if result is None or not getattr(result, "ok", False):
        return env
    wanted = ("USER_PASSWORD", "JUPYTER_TOKEN")
    for line in (result.stdout or "").splitlines():
        for key in wanted:
            prefix = key + "="
            if line.startswith(prefix):
                env[key] = line[len(prefix):].strip()
    return env


def reconcile_before_run(c, name, force=False):
    """``run`` 前同名容器对账（幂等状态机核心）。

    返回调用方应采取的动作：
      - ``PHASE_RUNNING``：容器运行中且未指定 force → 幂等 no-op，调用方直接展示访问信息
      - ``PHASE_ABSENT`` ：不存在 / 残留已清理 / 运行中但 force → 调用方继续新建
      - ``PHASE_UNKNOWN``：探测命令失败 → 调用方继续尝试，由 run 冲突兜底裁决

    2026-09-15 实证：旧实现用布尔 ``container_exists`` 单点探测，命令失败被
    ``warn=True`` 吞成 False，残留容器存在时裸跑 ``podman run`` 必撞
    name already in use（exit 125）。四态相位把「不存在」与「探测失败」分开。
    """
    runtime = detect_runtime()
    phase = container_phase(c, runtime, name)

    if phase == PHASE_STOPPED:
        print(f"[Reconcile] 检测到残留容器 {name}（Created/Exited 等非运行态），强制删除后重建…")
        run_cmd(c, f"{runtime} rm -f {name}", warn=True, hide=True, echo=False)
        return PHASE_ABSENT

    if phase == PHASE_RUNNING:
        if force:
            print(f"[Reconcile] 容器 {name} 正在运行，--force：删除旧容器后重建…")
            _stop_via_cli(c, name)
            return PHASE_ABSENT
        return PHASE_RUNNING

    if phase == PHASE_UNKNOWN:
        print(
            "[Reconcile] 容器状态探测失败（daemon 瞬断/预热？），继续尝试启动；"
            "若名称冲突将自动对账并重试一次"
        )
        return PHASE_UNKNOWN

    return PHASE_ABSENT


def _print_already_running_access(c, name, ssh_port, jupyter_port, workspace_path):
    """幂等分支：展示现存容器的真实访问信息（凭证从容器 env 回读）。"""
    env = _read_container_env(c, name)
    print("\n" + "=" * 60)
    print(f"容器 {name} 已在运行 —— inv run 幂等返回，未重复创建。")
    print("如需应用新配置重建：invoke stop 后再 invoke run，或 invoke run --force")
    print(f"  SSH:         ssh -p {ssh_port} devuser@localhost")
    if env.get("USER_PASSWORD"):
        print(f"  SSH password: {env['USER_PASSWORD']}")
    if env.get("JUPYTER_TOKEN"):
        print(f"  Jupyter Lab: http://localhost:{jupyter_port}/lab?token={env['JUPYTER_TOKEN']}")
    else:
        print(f"  Jupyter Lab: http://localhost:{jupyter_port}/lab（token 见容器启动时输出）")
    print(f"  Workspace:   {workspace_path}")
    print("=" * 60)


def _print_host_key_rotation_hint(ssh_port):
    """新建容器后的 SSH 主机密钥提示。

    自 2026-09-15 起 host key 存于 named volume（jupyter-podman-rootless_ssh-host-keys），
    删除重建容器不轮换；仅首次启用持久卷（旧容器层密钥迁入前）或卷被显式删除后才会变。
    """
    print(
        "  SSH host key: 密钥持久化于 named volume，重建容器不再轮换。\n"
        "                若连接报 REMOTE HOST IDENTIFICATION HAS CHANGED\n"
        "                （首次启用持久卷 / 卷被删除），请先执行：\n"
        f'                ssh-keygen -R "[localhost]:{ssh_port}"'
    )


def _is_name_in_use_error(exc):
    """判断异常是否为 podman 的容器名占用。"""
    result = getattr(exc, "result", None)
    text = " ".join(
        part
        for part in (
            str(exc),
            getattr(result, "stderr", "") or "",
            getattr(result, "stdout", "") or "",
        )
        if part
    )
    return "already in use" in text


def _run_via_cli_self_heal(
    c, name, tag, ssh_port, jupyter_port, workspace_posix,
    user_password, jupyter_token, ssh_public_key, grant_sudo, detach,
):
    """CLI 启动 + name-already-in-use 单次自愈（重试上限 1 次）。

    - PIPE 路径：直接读 stderr 中的 ``already in use``；
    - TTY 控制台路径（Windows）：``run_cmd`` 走 subprocess.call 拿不到 stderr，
      用失败后相位裁决——同名容器已存在即判定为名称冲突。
    第二次启动再失败则原样抛出，避免无限重试。
    """
    kwargs = dict(
        tag=tag,
        ssh_port=ssh_port,
        jupyter_port=jupyter_port,
        workspace_posix=workspace_posix,
        user_password=user_password,
        jupyter_token=jupyter_token,
        ssh_public_key=ssh_public_key,
        grant_sudo=grant_sudo,
        detach=detach,
    )
    try:
        _run_via_cli(c, name, **kwargs)
        return
    except (UnexpectedExit, Exit) as exc:
        runtime = detect_runtime()
        conflict = _is_name_in_use_error(exc) or container_phase(
            c, runtime, name
        ) in (PHASE_RUNNING, PHASE_STOPPED)
        if not conflict:
            raise
        print(f"[Reconcile] podman 报告容器名 {name} 已占用，强制清理后重试（仅 1 次）…")
        run_cmd(c, f"{runtime} rm -f {name}", warn=True, hide=True, echo=False)
        _run_via_cli(c, name, **kwargs)


def _status_via_sdk(client, name):
    """Check container status via SDK. Returns True on success."""
    try:
        containers = client.containers.list(all=True)
        target = None
        for ct in containers:
            if ct.name == name:
                target = ct
                break

        print(f"Container status: {name}")
        print("-" * 60)

        if target is None:
            print(f"Container {name} does not exist")
            return True

        target.reload()
        status = target.status
        ports_str = ", ".join(
            f"{p.get('HostPort', '?')}-&gt;{container_port}"
            for container_port, port_bindings in target.ports.items() if port_bindings
            for p in (port_bindings or [])
        )
        print(f"  Name:      {target.name}")
        print(f"  Status:    {status}")
        print(f"  Image:     {target.image.tags[0] if target.image.tags else target.short_id}")
        print(f"  Ports:     {ports_str or 'none'}")
        if status == "running" and target.attrs.get("State", {}).get("StartedAt"):
            print(f"  Started:   {target.attrs['State']['StartedAt']}")
        if status == "exited" and target.attrs.get("State", {}).get("ExitCode") is not None:
            print(f"  ExitCode:  {target.attrs['State']['ExitCode']}")
        return True
    except Exception as e:
        print(f"[SDK] Status check failed, falling back to CLI: {e}")
        return False


def _status_via_cli(c, name):
    """Check container status via CLI (original logic)."""
    runtime = detect_runtime()
    print(f"Container status: {name}")
    print("-" * 60)
    if not cli_container_exists(c, runtime, name):
        print(f"Container {name} does not exist")
        return
    # 单引号模板：双引号会被 Windows invoke 的 pwsh /c "..." 包装截断（同 run 探针事故）。
    # hide=True 捕获后单次打印；否则非 hide 路径在 Windows 会先流式输出再被 print 一遍。
    result = run_cmd(
        c,
        f"{runtime} ps -a --filter name=^{name}$ --format 'table {{{{.Names}}}}\t{{{{.Status}}}}\t{{{{.Ports}}}}'",
        hide=True,
        warn=True,
        echo=False,
    )
    if result is not None and getattr(result, "ok", False):
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")


def _clean_via_sdk(client, name, tag, volume, image):
    """Clean up resources via SDK. Returns True on success."""
    try:
        print("[SDK] Cleaning up...")
        _stop_via_sdk(client, name)

        if volume:
            print("[SDK] Pruning volumes...")
            client.volumes.prune()

        if image:
            print(f"[SDK] Removing image: {tag}")
            try:
                img = client.images.get(tag)
                img.remove(force=True)
            except Exception:
                pass

        print("[SDK] Cleanup complete")
        return True
    except Exception as e:
        print(f"[SDK] Cleanup failed, falling back to CLI: {e}")
        return False


def _clean_via_cli(c, name, tag, volume, image):
    """Clean up resources via CLI (original logic)."""
    runtime = detect_runtime()
    print("Cleaning up...")
    if cli_container_exists(c, runtime, name):
        _stop_via_cli(c, name)
    if volume:
        print("Pruning volumes...")
        run_cmd(c, f"{runtime} volume prune -f", warn=True)
    if image:
        print(f"Removing image: {tag}")
        run_cmd(c, f"{runtime} rmi {tag}", warn=True)
    print("Cleanup complete")


@task
def stop(c, name=None):
    """Stop and remove container.

    Tier 1: podman-compose down
    Tier 2: podman-py SDK
    Tier 3: CLI
    """
    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

    # Tier 1: podman-compose
    if _should_use_compose():
        project_root = Path(__file__).parent.parent.resolve()
        if compose_down(project_root=project_root):
            return
        print("[Compose] Stop failed, falling back to SDK/CLI...")

    # Tier 2 + 3: SDK then CLI
    sdk_ok = False
    if sdk_available():
        with get_client() as client:
            if client is not None:
                sdk_ok = _stop_via_sdk(client, name)
    if not sdk_ok:
        _stop_via_cli(c, name)


@task
def run(
    c,
    name=None,
    tag=None,
    ssh_port=None,
    jupyter_port=None,
    workspace=None,
    user_password=None,
    jupyter_token=None,
    ssh_public_key=None,
    grant_sudo=False,
    detach=True,
    force=False,
    apt_mirror=None,
    conda_mirror=None,
    pip_mirror=None,
):
    """Start Jupyter container（幂等）。

    同名容器对账（SDK/CLI 路径，compose 路径由 podman-compose 自身保证幂等）：
      - 已在运行：直接回显真实访问信息后成功返回，不重复创建；
      - Created/Exited 残留：自动删除后重建；
      - 状态探测失败：尝试启动，若撞 name already in use（exit 125）自动
        清理并重试一次；
      - --force：即使运行中也删除旧容器后重建。

    Three-tier backend priority:
      1. podman-compose (declarative YAML, daemon-less, rootless-first)
      2. podman-py SDK (REST API)
      3. CLI direct calls (fallback)
    """
    project_root = Path(__file__).parent.parent.resolve()

    if name is None:
        name = c.container.get("container_name", "jupyter-podman")
    if tag is None:
        tag = c.container.get("image_tag", "jupyter-podman-rootless:latest")
    if ssh_port is None:
        ssh_port = c.container.get("ssh_port", 2222)
    if jupyter_port is None:
        jupyter_port = c.container.get("jupyter_port", 8888)
    if workspace is None:
        workspace = c.container.get("workspace", "./workspace")

    workspace_path = Path(workspace).resolve() if not os.path.isabs(workspace) else Path(workspace)
    workspace_posix = to_posix_path(workspace_path)

    if not workspace_path.exists():
        print(f"Creating workspace directory: {workspace_path}")
        workspace_path.mkdir(parents=True, exist_ok=True)

    # Pre-flight: check container runtime is reachable
    ready, hint = check_runtime_ready()
    if not ready:
        print(f"[Error] {hint}")
        raise Exit(1)

    # Tier 1: podman-compose path
    if _should_use_compose():
        print("[Backend] Using podman-compose (Tier 1)")
        env = _load_or_create_env(
            c, project_root, ssh_port, jupyter_port, workspace_posix,
            user_password, jupyter_token, ssh_public_key, grant_sudo,
            apt_mirror, conda_mirror, pip_mirror,
        )
        print(f"[Compose] Mounting {env['WORKSPACE']} -> /workspace")
        success = compose_up(project_root=project_root, build=False, detach=detach, env=env)
        if success:
            print("\n" + "=" * 60)
            print("Access info:")
            print(f"  SSH:         ssh -p {env['SSH_PORT']} devuser@localhost")
            print(f"  SSH password: {env['USER_PASSWORD']}")
            print(f"  Jupyter Lab: http://localhost:{env['JUPYTER_PORT']}/lab?token={env['JUPYTER_TOKEN']}")
            print(f"  Workspace:   {workspace_path}")
            _print_host_key_rotation_hint(env["SSH_PORT"])
            print(f"\n[Compose] You can also manage with: podman-compose ps/logs/exec/down")
            print("=" * 60)
            return
        print("[Compose] Start failed, falling back to SDK/CLI...")
    else:
        # SDK/CLI 路径专属的同名容器对账（Tier1 compose 的幂等性由其自身保证）。
        # 对账先于密钥生成：幂等命中时展示容器内现存凭证，不打印用不上的新密钥。
        action = reconcile_before_run(c, name, force=force)
        if action == PHASE_RUNNING:
            _print_already_running_access(c, name, ssh_port, jupyter_port, workspace_path)
            return

        if user_password is None:
            user_password = generate_random_string(16)
            print(f"Auto-generated user password: {user_password}")
        if jupyter_token is None:
            jupyter_token = generate_random_string(32)
            print(f"Auto-generated Jupyter token: {jupyter_token}")

    print(f"Starting container: {name}")
    print(f"Using image: {tag}")
    print(f"Mounting {workspace_posix} -> /workspace")

    # Tier 2 + 3: SDK then CLI
    sdk_ok = False
    if sdk_available():
        with get_client() as client:
            if client is not None:
                sdk_ok = _run_via_sdk(
                    client, name, tag, ssh_port, jupyter_port, workspace_posix,
                    user_password, jupyter_token, ssh_public_key, grant_sudo, detach,
                )
    if not sdk_ok:
        _run_via_cli_self_heal(
            c, name, tag, ssh_port, jupyter_port, workspace_posix,
            user_password, jupyter_token, ssh_public_key, grant_sudo, detach,
        )

    print("\n" + "=" * 60)
    print("Access info:")
    print(f"  SSH:         ssh -p {ssh_port} devuser@localhost")
    print(f"  SSH password: {user_password}")
    print(f"  Jupyter Lab: http://localhost:{jupyter_port}/lab?token={jupyter_token}")
    print(f"  Workspace:   {workspace_path}")
    _print_host_key_rotation_hint(ssh_port)
    print("=" * 60)


@task
def status(c, name=None):
    """Check container running status.

    Tier 1: podman-compose ps
    Tier 2: podman-py SDK
    Tier 3: CLI
    """
    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

    # Tier 1: podman-compose
    if _should_use_compose():
        project_root = Path(__file__).parent.parent.resolve()
        if compose_ps(project_root=project_root):
            return
        print("[Compose] Status check failed, falling back to SDK/CLI...")

    # Tier 2 + 3: SDK then CLI
    sdk_ok = False
    if sdk_available():
        with get_client() as client:
            if client is not None:
                sdk_ok = _status_via_sdk(client, name)
    if not sdk_ok:
        _status_via_cli(c, name)


@task
def clean(c, name=None, tag=None, volume=False, image=False):
    """Clean container resources.

    Tier 1: podman-compose down -v
    Tier 2: podman-py SDK
    Tier 3: CLI
    """
    if name is None:
        name = c.container.get("container_name", "jupyter-podman")
    if tag is None:
        tag = c.container.get("image_tag", "jupyter-podman-rootless:latest")

    # Tier 1: podman-compose
    if _should_use_compose():
        project_root = Path(__file__).parent.parent.resolve()
        print("[Compose] Cleaning up...")
        compose_down(project_root=project_root, volumes=volume)
        if image:
            print(f"Removing image: {tag}")
            runtime = detect_runtime()
            run_cmd(c, f"{runtime} rmi {tag}", warn=True)
        print("[Compose] Cleanup complete")
        return

    # Tier 2 + 3: SDK then CLI
    sdk_ok = False
    if sdk_available():
        with get_client() as client:
            if client is not None:
                sdk_ok = _clean_via_sdk(client, name, tag, volume, image)
    if not sdk_ok:
        _clean_via_cli(c, name, tag, volume, image)
