"""AC-8 回归保护：CLI 冒烟（``inurl-byok-token-hub smoke``）纳入 pytest。

冒烟本身是端到端证据来源（19 步、全 mock、零真实密钥），此前只由人工执行，
没有回归守护；本文件用 Typer 的 ``CliRunner`` 把它拉进测试套件。
"""

from typer.testing import CliRunner

from inurl_byok_token_hub.cli import app

runner = CliRunner()


def test_smoke_command_exits_zero():
    result = runner.invoke(app, ["smoke"])
    assert result.exit_code == 0, result.output
    assert "冒烟全部通过" in result.output


def test_catalog_and_strategies_commands():
    catalog = runner.invoke(app, ["catalog"])
    assert catalog.exit_code == 0, catalog.output
    strategies = runner.invoke(app, ["strategies"])
    assert strategies.exit_code == 0, strategies.output
