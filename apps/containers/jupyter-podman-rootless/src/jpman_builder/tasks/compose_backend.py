"""podman-compose backend wrapper.

Provides declarative container orchestration via podman-compose CLI.
This is Tier 1 backend (highest priority) when compose.yaml exists and
podman-compose is installed.
"""

import os
import subprocess
import sys
from pathlib import Path


def _compose_cmd(args, project_root=None, env=None, pty=False, capture=False):
    """Execute a podman-compose command.

    Args:
        args: List of command arguments (e.g., ['up', '-d'])
        project_root: Working directory for the command (defaults to parent of tasks/)
        env: Additional environment variables
        pty: Whether to allocate a PTY (for interactive commands)
        capture: Whether to capture stdout/stderr

    Returns:
        subprocess.CompletedProcess result if capture=True, else None
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.resolve()

    cmd = ["podman-compose"] + list(args)

    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    if capture:
        return subprocess.run(
            cmd,
            cwd=str(project_root),
            env=run_env,
            capture_output=True,
            text=True,
        )
    else:
        return subprocess.run(
            cmd,
            cwd=str(project_root),
            env=run_env,
        )


def compose_up(project_root=None, build=False, detach=True, env=None):
    """Start services via podman-compose up.

    Args:
        project_root: Project directory containing compose.yaml
        build: Whether to build images before starting
        detach: Run in detached mode
        env: Additional environment variables
    """
    args = ["up"]
    if detach:
        args.append("-d")
    if build:
        args.append("--build")
    print("[Compose] Starting services...")
    result = _compose_cmd(args, project_root=project_root, env=env)
    return result.returncode == 0


def compose_down(project_root=None, volumes=False, env=None):
    """Stop and remove containers via podman-compose down.

    Args:
        project_root: Project directory containing compose.yaml
        volumes: Whether to remove named volumes
        env: Additional environment variables
    """
    args = ["down"]
    if volumes:
        args.append("-v")
    print("[Compose] Stopping and removing services...")
    result = _compose_cmd(args, project_root=project_root, env=env)
    return result.returncode == 0


def compose_ps(project_root=None, env=None):
    """List running containers via podman-compose ps."""
    print("[Compose] Container status:")
    result = _compose_cmd(["ps"], project_root=project_root, env=env, capture=False)
    return result.returncode == 0


def compose_logs(project_root=None, follow=False, tail=None, service=None, env=None):
    """View service logs via podman-compose logs.

    Args:
        project_root: Project directory
        follow: Stream logs in real-time
        tail: Number of lines to show from end
        service: Specific service name (None for all)
        env: Additional environment variables
    """
    args = ["logs"]
    if follow:
        args.append("-f")
    if tail is not None:
        args.extend(["--tail", str(tail)])
    if service:
        args.append(service)
    print(f"[Compose] Viewing logs{' (streaming)' if follow else ''}...")
    _compose_cmd(args, project_root=project_root, env=env, pty=follow)


def compose_exec(project_root=None, service="jupyter", command=None, user=None, env=None):
    """Execute a command in a running service container via podman-compose exec.

    Args:
        project_root: Project directory
        service: Service name (default: jupyter)
        command: Command string to execute
        user: User to run as (e.g., 'devuser', 'root')
        env: Additional environment variables
    """
    if command is None:
        # Interactive shell
        args = ["exec"]
        if user:
            args.extend(["-u", user])
        args.extend([service, "bash"])
        print(f"[Compose] Entering shell in service '{service}'...")
        _compose_cmd(args, project_root=project_root, env=env, pty=True)
    else:
        args = ["exec"]
        if user:
            args.extend(["-u", user])
        args.extend([service, "bash", "-c", command])
        print(f"[Compose] Executing in '{service}': {command}")
        result = _compose_cmd(args, project_root=project_root, env=env, pty=True)
        return result.returncode == 0


def compose_build(project_root=None, no_cache=False, build_args=None, env=None):
    """Build images via podman-compose build.

    Args:
        project_root: Project directory
        no_cache: Disable build cache
        build_args: Dict of build arguments (APT_MIRROR, CONDA_MIRROR, PIP_MIRROR)
        env: Additional environment variables
    """
    args = ["build"]
    if no_cache:
        args.append("--no-cache")

    run_env = None
    if build_args:
        run_env = (env or {}).copy()
        for k, v in build_args.items():
            run_env[k] = str(v)

    print("[Compose] Building images...")
    result = _compose_cmd(args, project_root=project_root, env=run_env)
    return result.returncode == 0


def compose_stop(project_root=None, env=None):
    """Stop services without removing them via podman-compose stop."""
    print("[Compose] Stopping services...")
    result = _compose_cmd(["stop"], project_root=project_root, env=env)
    return result.returncode == 0


def compose_start(project_root=None, env=None):
    """Start existing stopped services via podman-compose start."""
    print("[Compose] Starting services...")
    result = _compose_cmd(["start"], project_root=project_root, env=env)
    return result.returncode == 0


def is_compose_ready(project_root=None):
    """Check if compose.yaml exists in project root.

    Returns:
        True if compose.yaml exists, False otherwise
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.resolve()
    compose_file = Path(project_root) / "compose.yaml"
    return compose_file.exists()


__all__ = [
    "compose_available",
    "compose_build",
    "compose_down",
    "compose_exec",
    "compose_logs",
    "compose_ps",
    "compose_start",
    "compose_stop",
    "compose_up",
    "is_compose_ready",
]
