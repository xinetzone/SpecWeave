"""okw 命令注册表：全部叶子命令 handler 的唯一登记处。

键形固化（与 cli.parser 子命令 dest 约定一一对应）：
- 顶层命令用其名字：``"list"``、``"verify"`` ……；
- 子组叶子命令用空格连接的路径：``"podman preflight"``、``"image verify"``。

导入本包零副作用：仅定义函数与映射，不触子进程、不读 argv。
新增命令的机械纪律：在分组模块写 handler → 在此登记一行 →
在 cli.parser 装配 parser；test_command_registry 会强制三者一致。
"""

import argparse
from collections.abc import Callable

from okw.commands.distro_cmds import (
    cmd_exec,
    cmd_export,
    cmd_import,
    cmd_list,
    cmd_status,
    cmd_unregister,
)
from okw.commands.ai_cmds import cmd_install as cmd_ai_install
from okw.commands.ai_cmds import cmd_preflight as cmd_ai_preflight
from okw.commands.ai_cmds import cmd_verify as cmd_ai_verify
from okw.commands.compose_cmds import cmd_install as cmd_compose_install
from okw.commands.compose_cmds import cmd_preflight as cmd_compose_preflight
from okw.commands.compose_cmds import cmd_verify as cmd_compose_verify
from okw.commands.image_cmds import cmd_build as cmd_image_build
from okw.commands.image_cmds import cmd_verify as cmd_image_verify
from okw.commands.podman_cmds import cmd_install as cmd_podman_install
from okw.commands.podman_cmds import cmd_preflight as cmd_podman_preflight
from okw.commands.podman_cmds import cmd_verify as cmd_podman_verify
from okw.commands.ref_cmds import cmd_ref
from okw.commands.scaffold_cmds import cmd_scaffold
from okw.commands.verify_cmds import cmd_verify

# 所有 handler 统一签名：消费 argparse 解析出的 Namespace，返回进程退出码。
Handler = Callable[[argparse.Namespace], int]

COMMAND_HANDLERS: dict[str, Handler] = {
    "list": cmd_list,
    "status": cmd_status,
    "import": cmd_import,
    "export": cmd_export,
    "unregister": cmd_unregister,
    "exec": cmd_exec,
    "verify": cmd_verify,
    "scaffold": cmd_scaffold,
    "ref": cmd_ref,
    "ai preflight": cmd_ai_preflight,
    "ai install": cmd_ai_install,
    "ai verify": cmd_ai_verify,
    "podman preflight": cmd_podman_preflight,
    "podman install": cmd_podman_install,
    "podman verify": cmd_podman_verify,
    "compose preflight": cmd_compose_preflight,
    "compose install": cmd_compose_install,
    "compose verify": cmd_compose_verify,
    "image build": cmd_image_build,
    "image verify": cmd_image_verify,
}
