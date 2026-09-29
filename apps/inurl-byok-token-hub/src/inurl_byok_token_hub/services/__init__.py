"""服务层导出。

分层约束：``services`` 可依赖 ``config`` / ``models`` / ``crypto`` /
``storage`` / ``providers``，但**不得**反向依赖 ``api`` / ``web`` / ``cli``。
"""

from .billing_service import BillingService
from .chat_service import ChatResult, ChatService
from .health_service import HealthService, ProviderHealth
from .hub import Hub, build_hub
from .ops_service import OpsService
from .router_service import RoutePlan, RouterService
from .strategies import Candidate, StrategyContext, apply_strategy
from .token_service import TokenService
from .usage_service import UsageService
from .vault_service import VaultService

__all__ = [
    "BillingService",
    "Candidate",
    "ChatResult",
    "ChatService",
    "HealthService",
    "Hub",
    "OpsService",
    "ProviderHealth",
    "RoutePlan",
    "RouterService",
    "StrategyContext",
    "TokenService",
    "UsageService",
    "VaultService",
    "apply_strategy",
    "build_hub",
]
