"""Jupyter Podman Rootless container interaction tasks.

Provides shell access, log viewing, and command execution:
- logs/exec: SDK-first with CLI fallback
- shell: requires PTY interaction, always uses CLI (SDK exec_run does not support interactive TTY)
"""
from invoke import Context, task
from invoke.exceptions import Exit

from .client import PodmanNotFound, get_client, sdk_available
from .utils import container_exists as cli_container_exists, container_running as cli_container_running, detect_runtime, run_cmd


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
    run_cmd(c, cmd, pty=True)


@task
def shell(c, name=None, user="devuser"):
    """Enter container interactive shell.

    Note: Requires PTY interaction, always uses CLI mode.
    """
    runtime = detect_runtime()
    if name is None:
        name = c.container.get("container_name", "jupyter-podman")
    if not cli_container_running(c, runtime, name):
        raise Exit(f"Container {name} is not running, please start it first")
    print(f"Entering container shell: {name} (user: {user})")
    cmd = f"{runtime} exec -it -u {user} {name} bash"
    run_cmd(c, cmd, pty=True, echo=False)


@task
def logs(c, name=None, follow=False, tail=100):
    """View container logs."""
    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

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
    """Execute command in container."""
    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

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
