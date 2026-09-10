"""Jupyter Podman Rootless 容器管理任务入口。

常用命令：
    invoke build      - 构建镜像
    invoke run        - 启动容器
    invoke stop       - 停止并删除容器
    invoke clean      - 清理资源
    invoke status     - 查看容器状态
    invoke shell      - 进入容器Shell
    invoke logs       - 查看容器日志
    invoke exec       - 在容器中执行命令
    invoke container.* - 容器管理子命令集合
    invoke model.push    - 推送ML模型到OCI registry（OMLMD artifact）
    invoke model.pull    - 从OCI registry拉取ML模型（OMLMD artifact）
    invoke model.config  - 查看模型元数据配置（OMLMD）
    invoke model.pack    - 打包模型为KServe ModelCar镜像并推送（OLOT）
    invoke model.extract - 从ModelCar镜像提取/models到本地（OLOT）
    invoke registry.up   - 启动本地OCI registry（compose profile registry 的替代，Windows 可用）
    invoke registry.down - 停止本地OCI registry
"""
import os
import platform
import shutil
from pathlib import Path

from invoke import Collection

from . import container, model, registry


def _resolve_space_free_pwsh():
    """返回可用作 invoke shell 的无空格 PowerShell 7 路径；没有则返回 None。

    为什么要求"无空格"：见文件末尾 invoke shell 配置处的说明——invoke 在 Windows 上以
    `Popen(cmd, shell=True, executable=shell)` 启动 shell，含空格的路径无法转义。
    """
    candidates = [
        # App Execution Alias（Store 版 PowerShell 的稳定入口，路径无空格）
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WindowsApps/pwsh.exe",
        # shutil.which 的结果（Store 版常为 C:\Program Files\WindowsApps\...，含空格）
        Path(shutil.which("pwsh") or ""),
    ]
    for candidate in candidates:
        if candidate.is_file() and " " not in str(candidate):
            return str(candidate)
    return None


ns = Collection()

# 核心容器任务提升到根命名空间
ns.add_task(container.build, default=True)
ns.add_task(container.run)
ns.add_task(container.stop)
ns.add_task(container.clean)
ns.add_task(container.status)
ns.add_task(container.shell)
ns.add_task(container.logs)
ns.add_task(container.exec_task)

# 添加container子集合
ns.add_collection(Collection.from_module(container), name="container")

# 添加model子集合（OMLMD模型artifact管理 + OLOT ModelCar打包，不提升到根命名空间）
ns.add_collection(Collection.from_module(model), name="model")

# 添加registry子集合（本地OCI registry 生命周期；compose profile 的等价替代）
ns.add_collection(Collection.from_module(registry), name="registry")

# 默认配置
config = {
    "container": {
        "image_tag": "jupyter-podman-rootless:latest",
        "container_name": "jupyter-podman",
        "ssh_port": 2222,
        "jupyter_port": 8888,
        "workspace": "./workspace",
        "apt_mirror": "official",
        "conda_mirror": "official",
        "pip_mirror": "official",
    },
    "model": {
        "registry_url": "localhost:5000",
    },
    "registry": {
        "port": 5000,
    },
}

# Windows 上使用 PowerShell 7 (pwsh) 作为 invoke 的 shell：
# run_cmd 构造的是 POSIX 风格命令（单引号包裹参数、`&&` 串联），cmd.exe 会把单引号当
# 普通字符、把 `&&` 当命令分隔符，从而破坏它们（如 `--format '{{.Names}}'`、
# `bash -c 'cd X && olt_car.py pack ...'`），故必须用 PowerShell 7。
#
# ⚠️ shell 路径不得含空格：invoke 以 Popen(cmd, shell=True, executable=shell) 启动，
# Windows 下 Python 会拼成 f'{shell} /c "{cmd}"'，而 executable 不能被引号包裹
# （加引号会 OSError [WinError 123]）。Store 版 PowerShell 的 shutil.which() 结果形如
# `C:\Program Files\WindowsApps\...\pwsh.EXE`，被空格拆断后**所有** c.run 命令都会失败；
# 且该失败常被 warn=True 静默吞掉，表现为整条 CLI 兜底层不可用。故取无空格的
# App Execution Alias 路径（见 _resolve_space_free_pwsh）。
if platform.system() == "Windows":
    pwsh = _resolve_space_free_pwsh()
    if pwsh:
        config["run"] = {"shell": pwsh}

ns.configure(config)

