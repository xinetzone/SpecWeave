"""仓库合规检查模块集合。

每个子模块暴露 ``run(project_root: Path, args: argparse.Namespace) -> int`` 接口，
打印检查结果并返回退出码（0=通过，1=有错误）。
"""
