"""提示词萃取系统 —— 命令行入口

支持 ``python -m prompt_extraction`` 启动 Streamlit UI。
"""

import sys
from pathlib import Path

_APPS_DIR = Path(__file__).resolve().parent.parent
if str(_APPS_DIR) not in sys.path:
    sys.path.insert(0, str(_APPS_DIR))


def main() -> None:
    import streamlit.web.cli as stcli

    ui_app = Path(__file__).resolve().parent / "ui" / "app.py"
    sys.argv = ["streamlit", "run", str(ui_app)]
    stcli.main()


if __name__ == "__main__":
    main()
