"""服务容器：按配置装配全部服务，供 API / CLI / Web 复用。"""

from pathlib import Path

from ..config import Settings
from ..logging_utils import get_logger
from ..storage import Store
from .billing_service import BillingService
from .health_service import HealthService
from .ops_service import OpsService
from .router_service import RouterService
from .token_service import TokenService
from .usage_service import UsageService
from .vault_service import VaultService

logger = get_logger("services.hub")


def _restrict_permissions(path: Path) -> None:
    """尽量收紧文件权限为 0600（Windows 上为 best-effort）。"""
    try:
        import os

        os.chmod(path, 0o600)  # noqa: S103 - 收紧权限，非放宽
    except OSError:  # pragma: no cover - Windows/受限文件系统
        logger.debug("无法收紧 %s 的文件权限，沿用默认", path)


class Hub:
    """服务聚合：持有 store 与各服务实例。"""

    def __init__(self, settings: Settings, store: Store, catalog: object) -> None:
        self.settings = settings
        self.store = store
        self.catalog = catalog
        #: 进程内主密钥缓存：解锁后驻留内存，**绝不落盘**
        self._master_keys: dict[str, bytes] = {}
        self.health = HealthService()
        self.billing = BillingService(store, settings)
        self.vault = VaultService(store, self.billing, catalog)
        self.tokens = TokenService(store)
        self.usage = UsageService(store)
        self.router = RouterService(store, settings, catalog, self.health)
        self.ops = OpsService(store)

    def ensure_admin(self) -> None:
        """确保存在初始管理员账户（幂等）。"""
        from ..crypto import digest, issue_token, random_salt
        from ..models import Role, TokenRecord, TokenStatus, User
        from .token_service import hash_password

        if self.store.users.find(lambda u: u.role is Role.ADMIN):
            return
        import secrets

        #: 口令留空时随机生成——配置文件里不放明文口令（敏感信息预提交钩子会拦截）
        password = self.settings.admin_password or secrets.token_urlsafe(16)
        salt = random_salt()
        admin = User(
            id="admin",
            email=self.settings.admin_email,
            password_digest=hash_password(password, salt),
            password_salt=salt.hex(),
            role=Role.ADMIN,
            plan_key="pro",
        )
        self.store.users.add(admin)
        token = issue_token()
        self.store.tokens.add(
            TokenRecord(
                id="admin-token",
                user_id=admin.id,
                digest=digest(token),
                status=TokenStatus.ACTIVE,
            )
        )
        #: 管理员令牌写入运行期文件，便于 CLI/演示读取（不入库）。
        #: 注意：该文件是**明文令牌**（NFR-3 只允许库内存摘要），故权限收紧为 0600
        #: 并显式告警——拿到本文件即等同于管理员权限（见 README 假设说明）。
        token_file = Path(self.store.data_dir) / "admin.token"
        token_file.write_text(token, encoding="utf-8")
        _restrict_permissions(token_file)
        logger.warning(
            "管理员令牌已写入 %s（明文，权限 0600）；任何可读取该文件的进程即拥有管理员权限",
            token_file,
        )

    def admin_token(self) -> str | None:
        token_file = Path(self.store.data_dir) / "admin.token"
        if token_file.exists():
            return token_file.read_text(encoding="utf-8").strip()
        return None

    # ------------------------------------------------------- 主密钥（内存）
    def unlock(self, user_id: str, password: str) -> bytes:
        master = self.vault.unlock_with_password(user_id, password)
        self._master_keys[user_id] = master
        return master

    def unlock_with_recovery(self, user_id: str, recovery_secret: str) -> bytes:
        master = self.vault.unlock_with_recovery(user_id, recovery_secret)
        self._master_keys[user_id] = master
        return master

    def master_key(self, user_id: str) -> bytes:
        master = self._master_keys.get(user_id)
        if master is None:
            from ..errors import ByokError, ErrorCode

            raise ByokError(ErrorCode.VAULT_LOCKED, "密钥库未解锁，请先调用 /api/unlock")
        return master

    def is_unlocked(self, user_id: str) -> bool:
        return user_id in self._master_keys


def build_hub(settings: Settings, catalog: object | None = None) -> Hub:
    """按配置构造 Hub（数据目录自动创建，目录缺省时自动加载种子目录）。"""
    if catalog is None:
        from .catalog_service import CatalogService

        catalog = CatalogService.load(settings)
    store = Store(settings.data_dir)
    hub = Hub(settings, store, catalog)
    hub.ensure_admin()
    hub.ops.ensure_seed()
    return hub


__all__ = ["Hub", "build_hub"]
