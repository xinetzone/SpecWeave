"""AI 栈子组命令：preflight / install / verify。

判定矩阵、报告类型与格式化函数位于领域模块 okw.ai，本模块只做参数解包
与调用编排；零第三方依赖，WSL 调用经 okw.distro。
"""

import argparse

from okw import ai


def cmd_preflight(args: argparse.Namespace) -> int:
    """CLI 入口：okw ai preflight <发行版>。"""
    report = ai.preflight_check(args.name)
    print(ai.format_preflight(report))
    return report.exit_code()


def cmd_install(args: argparse.Namespace) -> int:
    """CLI 入口：okw ai install <发行版> [--yes]。"""
    yes = getattr(args, "yes", False)
    if not yes:
        report = ai.InstallReport(distro_name=args.name, missing_yes=True)
        print(ai.format_install(report))
        return report.exit_code()
    report = ai.install_run(args.name, yes=True)
    print(ai.format_install(report))
    return report.exit_code()


def cmd_verify(args: argparse.Namespace) -> int:
    """CLI 入口：okw ai verify <发行版> [--smoke-ocr 图片路径]。"""
    smoke_ocr = getattr(args, "smoke_ocr", None)
    report = ai.verify_run(args.name, smoke_ocr=smoke_ocr)
    print(ai.format_verify(report))
    return report.exit_code()
