"""Jupyter Podman Rootless 核心容器管理任务。

自动检测容器运行时（优先podman，回退docker），提供完整的容器生命周期管理。
"""
from __future__ import annotations

import platform
import secrets
import shutil
import string
from pathlib import Path
from typing import Optional

from invoke import Context, task
from invoke.exceptions import Exit, UnexpectedExit

MIRROR_CHOICES = ["official", "tuna", "aliyun"]


def detect_runtime():
    """检测容器运行时，优先使用podman。"""
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise Exit("未找到podman或docker，请先安装其中之一")


def to_posix_path(path):
    """将路径转换为POSIX风格（适配WSL2/远程Linux podman）。"""
    path_str = str(path.resolve())
    if platform.system() == "Windows":
        if len(path_str) >= 2 and path_str[1] == ":":
            drive = path_str[0].lower()
            rest = path_str[2:].replace("\\", "/")
            return f"/mnt/{drive}{rest}"
        return path_str.replace("\\", "/")
    return path_str


def run_cmd(c, cmd, pty=False, hide=False, warn=False, echo=True):
    """执行命令的包装函数。"""
    if echo and not hide:
        print(f"执行: {cmd}")
    try:
        return c.run(cmd, pty=pty, hide=hide, warn=warn, echo=False)
    except UnexpectedExit as e:
        if not warn:
            raise
        return e.result


def generate_random_string(length=12):
    """生成随机字符串（用于密码/token）。"""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def container_exists(c, runtime, name):
    """检查容器是否存在（包括停止状态）。"""
    result = run_cmd(
        c, f"{runtime} ps -a --filter name=^{name}$ --format '{{{{.Names}}}}'", hide=True, warn=True, echo=False
    )
    return result and result.stdout.strip() == name


def container_running(c, runtime, name):
    """检查容器是否正在运行。"""
    result = run_cmd(
        c, f"{runtime} ps --filter name=^{name}$ --format '{{{{.Names}}}}'", hide=True, warn=True, echo=False
    )
    return result and result.stdout.strip() == name


@task
def build(
    c,
    tag=None,
    apt_mirror="official",
    conda_mirror="official",
    pip_mirror="official",
    no_cache=False,
):
    """构建Jupyter容器镜像。"""
    runtime = detect_runtime()

    if tag is None:
        tag = c.container.get("image_tag", "jupyter-podman-rootless:latest")

    for mirror_name, mirror_val in [("apt_mirror", apt_mirror), ("conda_mirror", conda_mirror), ("pip_mirror", pip_mirror)]:
        if mirror_val not in MIRROR_CHOICES:
            raise Exit(f"{mirror_name}必须是{MIRROR_CHOICES}之一，当前值: {mirror_val}")

    project_root = Path(__file__).parent.parent.resolve()
    print(f"开始构建镜像: {tag}")
    print(f"构建上下文: {project_root}")
    print(f"镜像源配置: APT={apt_mirror}, Conda={conda_mirror}, PIP={pip_mirror}")

    build_args = [
        f"--build-arg APT_MIRROR={apt_mirror}",
        f"--build-arg CONDA_MIRROR={conda_mirror}",
        f"--build-arg PIP_MIRROR={pip_mirror}",
    ]

    cmd_parts = [
        runtime,
        "build",
        "--format docker",
        "--security-opt label=disable",
        "--device /dev/fuse",
        "-t", tag,
    ]

    if no_cache:
        cmd_parts.append("--no-cache")

    cmd_parts.extend(build_args)
    cmd_parts.append(".")

    cmd = " ".join(cmd_parts)

    with c.cd(str(project_root)):
        run_cmd(c, cmd, pty=True)

    print(f"镜像构建完成: {tag}")


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
):
    """启动Jupyter容器。"""
    runtime = detect_runtime()

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

    workspace_path = Path(workspace).resolve()
    workspace_posix = to_posix_path(workspace_path)

    if not workspace_path.exists():
        print(f"创建工作目录: {workspace_path}")
        workspace_path.mkdir(parents=True, exist_ok=True)

    if container_exists(c, runtime, name):
        print(f"容器 {name} 已存在，先停止并删除...")
        stop(c, name=name)

    if user_password is None:
        user_password = generate_random_string(16)
        print(f"自动生成用户密码: {user_password}")
    if jupyter_token is None:
        jupyter_token = generate_random_string(32)
        print(f"自动生成Jupyter token: {jupyter_token}")

    print(f"启动容器: {name}")
    print(f"使用镜像: {tag}")

    cmd_parts = [
        runtime,
        "run",
        "--name", name,
        "-p", f"{ssh_port}:22",
        "-p", f"{jupyter_port}:8888",
        "-v", f"{workspace_posix}:/workspace",
        "--device /dev/fuse",
        "--security-opt label=disable",
        "--cgroupns=host",
    ]

    if detach:
        cmd_parts.append("-d")

    cmd_parts.extend(["-e", f"USER_PASSWORD={user_password}"])
    cmd_parts.extend(["-e", f"JUPYTER_TOKEN={jupyter_token}"])

    if ssh_public_key:
        cmd_parts.extend(["-e", f'SSH_PUBLIC_KEY="{ssh_public_key}"'])
    if grant_sudo:
        cmd_parts.extend(["-e", "GRANT_SUDO=yes"])

    cmd_parts.append(tag)

    cmd = " ".join(cmd_parts)
    run_cmd(c, cmd, pty=not detach)

    if detach:
        print("容器已启动（后台运行）")
    else:
        print("容器已在前台启动")

    print("\n" + "=" * 60)
    print("访问信息:")
    print(f"  SSH访问: ssh -p {ssh_port} devuser@localhost")
    print(f"  SSH密码: {user_password}")
    print(f"  Jupyter Lab: http://localhost:{jupyter_port}/lab?token={jupyter_token}")
    print(f"  工作目录: {workspace_path}")
    print("=" * 60)


@task
def stop(c, name=None):
    """停止并删除容器。"""
    runtime = detect_runtime()

    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

    if not container_exists(c, runtime, name):
        print(f"容器 {name} 不存在，无需停止")
        return

    print(f"停止容器: {name}")
    run_cmd(c, f"{runtime} stop {name}", warn=True, hide=True, echo=False)
    run_cmd(c, f"{runtime} rm {name}", warn=True, hide=True, echo=False)
    print(f"容器 {name} 已停止并删除")


@task
def status(c, name=None):
    """查看容器运行状态。"""
    runtime = detect_runtime()

    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

    print(f"容器状态: {name}")
    print("-" * 60)

    if not container_exists(c, runtime, name):
        print(f"容器 {name} 不存在")
        return

    result = run_cmd(
        c,
        f'{runtime} ps -a --filter name=^{name}$ --format "table {{{{.Names}}}}\t{{{{.Status}}}}\t{{{{.Ports}}}}"',
        pty=False,
        echo=False,
    )

    if result:
        print(result.stdout)


@task
def shell(c, name=None, user="devuser"):
    """进入容器交互式Shell。"""
    runtime = detect_runtime()

    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

    if not container_running(c, runtime, name):
        raise Exit(f"容器 {name} 未运行，请先启动")

    print(f"进入容器Shell: {name} (用户: {user})")
    cmd = f"{runtime} exec -it -u {user} {name} bash"
    run_cmd(c, cmd, pty=True, echo=False)


@task
def logs(c, name=None, follow=False, tail=100):
    """查看容器日志。"""
    runtime = detect_runtime()

    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

    if not container_exists(c, runtime, name):
        raise Exit(f"容器 {name} 不存在")

    cmd_parts = [runtime, "logs"]
    if follow:
        cmd_parts.append("-f")
    cmd_parts.extend(["--tail", str(tail)])
    cmd_parts.append(name)

    cmd = " ".join(cmd_parts)
    run_cmd(c, cmd, pty=follow)


@task(name="exec")
def exec_task(c, command, name=None, user="devuser"):
    """在容器中执行命令。"""
    runtime = detect_runtime()

    if name is None:
        name = c.container.get("container_name", "jupyter-podman")

    if not container_running(c, runtime, name):
        raise Exit(f"容器 {name} 未运行，请先启动")

    print(f"在容器中执行命令: {command}")
    escaped_cmd = command.replace('"', '\\"')
    cmd = f'{runtime} exec -it -u {user} {name} bash -c "{escaped_cmd}"'
    run_cmd(c, cmd, pty=True)


@task
def clean(
    c,
    name=None,
    tag=None,
    volume=False,
    image=False,
):
    """清理容器资源。"""
    runtime = detect_runtime()

    if name is None:
        name = c.container.get("container_name", "jupyter-podman")
    if tag is None:
        tag = c.container.get("image_tag", "jupyter-podman-rootless:latest")

    print("开始清理...")

    if container_exists(c, runtime, name):
        stop(c, name=name)

    if volume:
        print("清理卷...")
        run_cmd(c, f"{runtime} volume prune -f", warn=True)

    if image:
        print(f"删除镜像: {tag}")
        run_cmd(c, f"{runtime} rmi {tag}", warn=True)

    print("清理完成")
