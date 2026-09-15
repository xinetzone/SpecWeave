"""pytest 公共夹具。"""
import pytest

from jpman_common import _win32_transcode as wt


@pytest.fixture
def reset_transcode_singleton():
    """隔离 Windows 转码模块的模块级单例：用例前强制未初始化，用例后恢复现场。

    proc 层测试会经 run_cmd 真实初始化单例（PIPE 分支），故夹具必须在**入口**
    也复位，否则后续 TTY 分支用例会直接读到跨文件缓存的 ("", False 系) 结果。
    """
    saved_ready = wt._WIN32_STDOUT_TRANSCODE_READY
    saved_cached = wt._WIN32_TRANSCODE_CACHED_RESULT
    wt._WIN32_STDOUT_TRANSCODE_READY = False
    wt._WIN32_TRANSCODE_CACHED_RESULT = ("", False)
    yield
    wt._WIN32_STDOUT_TRANSCODE_READY = saved_ready
    wt._WIN32_TRANSCODE_CACHED_RESULT = saved_cached
