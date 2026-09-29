"""inurl BYOK Token Hub —— BYOK 统一令牌枢纽的 Python 3.14+ 复刻实现。

分层：``config`` / ``models`` / ``crypto`` / ``storage`` / ``services`` /
``providers`` / ``api`` / ``web`` / ``cli``。外部依赖调用统一经
``providers.transport`` 抽象，便于以 mock 传输层完成零密钥端到端验证。
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
