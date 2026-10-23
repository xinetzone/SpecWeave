"""openkylin-wsl-devkit：openKylin WSL 开发工具包。

以 WSL 为切入点，提供 openKylin 发行版管理、环境验收、开发脚手架（deb/dput）
与知识库快速参考。知识依据：docs/knowledge/tech/openkylin/docs-wiki/。
"""

import sys

MINIMUM_PYTHON_VERSION = (3, 10)


def require_python_version(minimum=MINIMUM_PYTHON_VERSION, current=None):
    """导入时版本守卫：低于阈值立即以可诊断信息终止，避免后续语法/特性错误。

    仅使用各版本通用语法（无 PEP 604 联合注解、无 match），确保在低于阈值
    的解释器上也能被解析执行并抛出本 RuntimeError。``current`` 仅供测试注入。
    """
    if current is None:
        current = sys.version_info
    current_tuple = tuple(current[:3])
    if current_tuple[:2] < tuple(minimum[:2]):
        actual = ".".join(str(part) for part in current_tuple)
        required = ".".join(str(part) for part in tuple(minimum[:2]))
        raise RuntimeError(
            f"openkylin-wsl-devkit 需要 Python >={required}，"
            f"当前解释器为 {actual}（pyproject.toml requires-python = \">={required}\"）。"
            "请升级 Python 后重试。"
        )


require_python_version()

__version__ = "0.1.0"
