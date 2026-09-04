"""允许通过 python -m lib.spec_tool 调用。"""

from .cli import main

raise SystemExit(main())
