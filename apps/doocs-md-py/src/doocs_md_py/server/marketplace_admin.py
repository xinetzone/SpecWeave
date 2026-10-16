"""市场管理员判定（upstream: apps/api/src/marketplace-admin.ts 1:1）。

``ADMIN_GITHUB_LOGINS`` 逗号分隔，统一 normalize（trim+lowercase）后入集合。
"""

from .config import Config
from .plan import normalize_github_login


def get_admin_logins(config: Config) -> set[str]:
    """upstream: marketplace-admin.ts:5-14。"""
    result: set[str] = set()
    for part in config.admin_github_logins:
        login = normalize_github_login(part)
        if login:
            result.add(login)
    return result


def is_admin(config: Config, login: str | None) -> bool:
    """upstream: marketplace-admin.ts:16-20。"""
    if not login:
        return False
    return normalize_github_login(login) in get_admin_logins(config)
