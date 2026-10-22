"""CLI 分支测试：无 Key 保护路径 + 演示模式退出路径（不触发真实 API 调用）。"""

import builtins

from langgraph_poc import cli


def test_cli_deepseek_without_key(monkeypatch):
    """--model deepseek 但无 DEEPSEEK_API_KEY -> 返回错误码 2，不启动会话。"""
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    assert cli.main(["--model", "deepseek"]) == 2


def test_cli_demo_eof_exits_cleanly(monkeypatch):
    """演示模式 + stdin EOF -> 正常退出 0。"""
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    def _eof(_prompt=""):
        raise EOFError

    monkeypatch.setattr(builtins, "input", _eof)
    assert cli.main(["--model", "demo"]) == 0
