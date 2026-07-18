"""Python 启动时自动执行的站点定制模块，配置 UTF-8 编码环境。

三层防御体系：
1. 环境变量层：设置 PYTHONIOENCODING 和 PYTHONUTF8
2. 流重配置层：重新配置 stdout/stderr 使用 UTF-8
3. 容错层：设置 errors='replace' 防止不可编码字符导致崩溃
"""

import os
import sys


def _setup_utf8_environment():
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    os.environ.setdefault('PYTHONUTF8', '1')


def _reconfigure_std_streams():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, 'reconfigure', None)
        if reconfigure is not None and callable(reconfigure):
            try:
                reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                try:
                    reconfigure(errors='replace')
                except Exception:
                    pass


_setup_utf8_environment()
_reconfigure_std_streams()
