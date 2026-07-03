"""Click CLI测试生成器子包。

使用click.testing.CliRunner为CLI Tool Profile生成集成测试。
"""

from .generator import CLITestGenerator

__all__ = ["CLITestGenerator"]
