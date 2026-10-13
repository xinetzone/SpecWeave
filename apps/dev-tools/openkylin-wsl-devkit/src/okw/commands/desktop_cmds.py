"""desktop 子组命令：preflight / install / verify。

判定矩阵、报告类型与格式化函数位于领域模块 okw.desktop，本模块只做参数解包
与调用编排；零第三方依赖，WSL 调用经 okw.distro。
"""

import argparse

from okw import desktop


def cmd_preflight(args: argparse.Namespace) -> int:
    """CLI 入口：okw desktop preflight <发行版> [--port]。"""
    report = desktop.preflight_check(args.name, port=getattr(args, "port", desktop.DEFAULT_PORT))
    print(desktop.format_preflight(report))
    return report.exit_code()


def cmd_install(args: argparse.Namespace) -> int:
    """CLI 入口：okw desktop install <发行版> [--yes] [--port]。"""
    report = desktop.install_run(
        args.name,
        yes=getattr(args, "yes", False),
        port=getattr(args, "port", desktop.DEFAULT_PORT),
    )
    print(desktop.format_install(report))
    return report.exit_code()


def cmd_verify(args: argparse.Namespace) -> int:
    """CLI 入口：okw desktop verify <发行版> [--port]。"""
    report = desktop.verify_run(args.name, port=getattr(args, "port", desktop.DEFAULT_PORT))
    print(desktop.format_verify(report))
    return report.exit_code()


def cmd_launch(args: argparse.Namespace) -> int:
    """CLI 入口：okw desktop launch <发行版> [--port]。"""
    report = desktop.launch_run(args.name, port=getattr(args, "port", desktop.DEFAULT_PORT))
    print(desktop.format_launch(report))
    return report.exit_code()
