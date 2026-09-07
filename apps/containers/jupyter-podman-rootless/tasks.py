import sys as _s, os as _o
_s.path.insert(0, _o.path.join(_o.path.dirname(__file__), "src"))
from jpman_builder.tasks import *  # noqa: F401,F403
from jpman_builder.tasks import ns as namespace, ns  # noqa: F401
