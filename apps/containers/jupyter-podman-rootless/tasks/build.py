"""Jupyter Podman Rootless image build task.

Three-tier backend priority:
  1. podman-compose build (declarative)
  2. podman-py SDK (REST API)
  3. CLI direct calls (fallback)
"""
import platform
from pathlib import Path

from invoke import Context, task
from invoke.exceptions import Exit

from .client import compose_available, get_client, sdk_build_kwargs, sdk_available
from .compose_backend import compose_build, is_compose_ready
from .utils import MIRROR_CHOICES, detect_runtime, run_cmd


def _should_use_compose():
    """Check if we should use podman-compose backend."""
    return compose_available() and is_compose_ready()


def _build_via_sdk(c, project_root, tag, apt_mirror, conda_mirror, pip_mirror, no_cache):
    """Try building image via podman-py SDK. Returns True on success."""
    if not sdk_available():
        return False

    try:
        with get_client() as client:
            if client is None:
                return False

            build_kwargs = sdk_build_kwargs(
                tag=tag,
                apt_mirror=apt_mirror,
                conda_mirror=conda_mirror,
                pip_mirror=pip_mirror,
                no_cache=no_cache,
            )

            with c.cd(str(project_root)):
                print(f"[SDK] Building image: {tag}")
                image, build_logs = client.images.build(**build_kwargs)

                for entry in build_logs:
                    if "stream" in entry:
                        line = entry["stream"].rstrip()
                        if line:
                            print(line)
                    elif "error" in entry:
                        print(f"[ERROR] {entry['error']}")
                        return False
                    elif "errorDetail" in entry:
                        print(f"[ERROR DETAIL] {entry['errorDetail'].get('message', '')}")
                        return False

                print(f"[SDK] Build complete: {tag} ({image.short_id})")
                return True
    except Exception as e:
        print(f"[SDK] Build failed, falling back to CLI: {e}")
        return False


def _build_via_cli(c, project_root, tag, apt_mirror, conda_mirror, pip_mirror, no_cache):
    """Build image via CLI commands (original logic)."""
    runtime = detect_runtime()

    build_args = [
        f"--build-arg APT_MIRROR={apt_mirror}",
        f"--build-arg CONDA_MIRROR={conda_mirror}",
        f"--build-arg PIP_MIRROR={pip_mirror}",
    ]

    cmd_parts = [
        runtime,
        "build",
        "--format docker",
        "-t", tag,
    ]

    if no_cache:
        cmd_parts.append("--no-cache")

    cmd_parts.extend(build_args)
    cmd_parts.append("-f")
    cmd_parts.append("Containerfile")
    cmd_parts.append(".")

    cmd = " ".join(cmd_parts)

    with c.cd(str(project_root)):
        run_cmd(c, cmd, pty=platform.system() != "Windows")

    print(f"Build complete: {tag}")


@task
def build(
    c,
    tag=None,
    apt_mirror="official",
    conda_mirror="official",
    pip_mirror="official",
    no_cache=False,
):
    """Build Jupyter container image.

    Three-tier backend priority:
      1. podman-compose build (declarative YAML config)
      2. podman-py SDK (requires Podman socket)
      3. CLI direct commands (fallback)
    """
    if tag is None:
        tag = c.container.get("image_tag", "jupyter-podman-rootless:latest")

    for mirror_name, mirror_val in [("apt_mirror", apt_mirror), ("conda_mirror", conda_mirror), ("pip_mirror", pip_mirror)]:
        if mirror_val not in MIRROR_CHOICES:
            raise Exit(f"{mirror_name} must be one of {MIRROR_CHOICES}, got: {mirror_val}")

    project_root = Path(__file__).parent.parent.resolve()
    print(f"Building image: {tag}")
    print(f"Build context: {project_root}")
    print(f"Mirror config: APT={apt_mirror}, Conda={conda_mirror}, PIP={pip_mirror}")

    # Tier 1: podman-compose build
    if _should_use_compose():
        print("[Backend] Using podman-compose (Tier 1)")
        build_args = {
            "APT_MIRROR": apt_mirror,
            "CONDA_MIRROR": conda_mirror,
            "PIP_MIRROR": pip_mirror,
        }
        if compose_build(project_root=project_root, no_cache=no_cache, build_args=build_args):
            return
        print("[Compose] Build failed, falling back to SDK/CLI...")

    # Tier 2 + 3: SDK then CLI
    if not _build_via_sdk(c, project_root, tag, apt_mirror, conda_mirror, pip_mirror, no_cache):
        _build_via_cli(c, project_root, tag, apt_mirror, conda_mirror, pip_mirror, no_cache)
