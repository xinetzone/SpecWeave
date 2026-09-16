"""Jupyter Podman Rootless container interaction tasks.

Provides shell access, log viewing, and command execution:
- logs/exec: Three-tier priority (compose → SDK → CLI)
- shell: Requires PTY interaction, compose exec or CLI (SDK exec_run does not support interactive TTY)
"""
from pathlib import Path

from invoke import Context, task
from invoke.exceptions import Exit

from .client import PodmanNotFound, compose_available, get_client, sdk_available
from .compose_backend import compose_exec, compose_logs, is_compose_ready
from .utils import container_exists as cli_container_exists, container_running as cli_container_running, detect_runtime, run_cmd


def _should_use_compose():
    """Check if we should use podman-compose backend."""
    return compose_available() and is_compose_ready()


def _logs_via_sdk(client, name, follow, tail):
    """Get logs via SDK. Returns True on success."""
    try:
        container = client.containers.get(name)
        if follow:
            print(f"[SDK] Streaming logs (Ctrl+C to exit):")
            try:
                for line in container.logs(stream=True, follow=True, tail=tail):
                    print(line.decode("utf-8", errors="replace"), end="")
            except KeyboardInterrupt:
                print("\n[SDK] Log stream stopped")
        else:
            logs = container.logs(tail=tail)
            print(logs.decode("utf-8", errors="replace"))
        return True
    except PodmanNotFound:
        raise Exit(f"Container {name} does not exist")
    except Exception as e:
        print(f"[SDK] Log retrieval failed, falling back to CLI: {e}")
        return False


def _logs_via_cli(c, name, follow, tail):
    """Get logs via CLI (original logic)."""
    runtime = detect_runtime()
    cmd_parts = [runtime, "logs"]
    if follow:
        cmd_parts.append("-f")
    cmd_parts.extend(["--tail", str(tail)])
    cmd_parts.append(name)
    cmd = " ".join(cmd_parts)
    run_cmd(c, cmd, pty=follow)


def _exec_via_sdk(client, name, command, user):
    """Execute command via SDK. Returns True on success."""
    try:
        container = client.containers.get(name)
        if container.status != "running":
            raise Exit(f"Container {name} is not running, please start it first")

        print(f"[SDK] Executing command (user: {user}): {command}")
        exit_code, output = container.exec_run(command, user=user, demux=False)
        if output:
            print(output.decode("utf-8", errors="replace"))
        print(f"[SDK] Exit code: {exit_code}")
        return True
    except PodmanNotFound:
        raise Exit(f"Container {name} does not exist")
    except Exit:
        raise
    except Exception as e:
        print(f"[SDK] Command execution failed, falling back to CLI: {e}")
        return False


def _exec_via_cli(c, name, command, user):
    """Execute command via CLI (original logic)."""
    runtime = detect_runtime()
    if not cli_container_running(c, runtime, name):
        raise Exit(f"Container {name} is not running, please start it first")
    print(f"Executing command in container: {command}")
    escaped_cmd = command.replace('"', '\\"')
    cmd = f'{runtime} exec -it -u {user} {name} bash -c "{escaped_cmd}"'
    # 真交互式 exec：opt-in 转发 stdin（FIONREAD 崩溃面由 jpman_common.proc 兜）
    run_cmd(c, cmd, pty=True, forward_stdin=True)


@task
def shell(c, name=None, user="devuser"):
    """Enter container interactive shell.

    Tier 1: podman-compose exec (PTY)
    Tier 3: CLI (PTY required, SDK not used for interactive shell)
    """
    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

    # Tier 1: podman-compose exec (supports PTY)
    if _should_use_compose():
        project_root = Path(__file__).parent.parent.resolve()
        compose_exec(project_root=project_root, service="jupyter", command=None, user=user)
        return

    # Tier 3: CLI (SDK doesn't support interactive TTY well)
    runtime = detect_runtime()
    if not cli_container_running(c, runtime, name):
        raise Exit(f"Container {name} is not running, please start it first")
    print(f"Entering container shell: {name} (user: {user})")
    cmd = f"{runtime} exec -it -u {user} {name} bash"
    # 真交互式 shell：opt-in 转发 stdin（FIONREAD 崩溃面由 jpman_common.proc 兜）
    run_cmd(c, cmd, pty=True, echo=False, forward_stdin=True)


@task
def logs(c, name=None, follow=False, tail=100):
    """View container logs.

    Tier 1: podman-compose logs
    Tier 2: podman-py SDK
    Tier 3: CLI
    """
    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

    # Tier 1: podman-compose
    if _should_use_compose():
        project_root = Path(__file__).parent.parent.resolve()
        compose_logs(project_root=project_root, follow=follow, tail=tail, service="jupyter")
        return

    runtime = detect_runtime()
    if not cli_container_exists(c, runtime, name):
        raise Exit(f"Container {name} does not exist")

    sdk_ok = False
    if sdk_available():
        with get_client() as client:
            if client is not None:
                sdk_ok = _logs_via_sdk(client, name, follow, tail)
    if not sdk_ok:
        _logs_via_cli(c, name, follow, tail)


@task(name="exec")
def exec_task(c, command, name=None, user="devuser"):
    """Execute command in container.

    Tier 1: podman-compose exec
    Tier 2: podman-py SDK
    Tier 3: CLI
    """
    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

    # Tier 1: podman-compose exec
    if _should_use_compose():
        project_root = Path(__file__).parent.parent.resolve()
        compose_exec(project_root=project_root, service="jupyter", command=command, user=user)
        return

    # Tier 2 + 3: SDK then CLI
    sdk_ok = False
    if sdk_available():
        with get_client() as client:
            if client is not None:
                try:
                    sdk_ok = _exec_via_sdk(client, name, command, user)
                except Exit:
                    raise
    if not sdk_ok:
        _exec_via_cli(c, name, command, user)
