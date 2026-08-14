"""pytest 配置 —— 自动修正 sys.path 以支持从项目根目录运行测试。"""

import sys
from pathlib import Path

_APPS_DIR = Path(__file__).resolve().parent.parent.parent
if str(_APPS_DIR) not in sys.path:
    sys.path.insert(0, str(_APPS_DIR))
