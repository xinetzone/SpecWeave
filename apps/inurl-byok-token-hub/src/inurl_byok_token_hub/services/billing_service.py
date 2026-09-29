"""套餐与计费服务（不含真实资金流转）。

套餐口径（源文档 F-051/F-072/F-089，**核心勘误 E1**）：
免费 ¥0 / **3 个厂商密钥**；标准 ¥9.9 月 / 10 个；专业 ¥29.9 月 / 无限。
「注册 17 家免费模型的 Key 且月费 0 元」在该价格表下**不成立**。
"""

import secrets
import time

from ..config import Settings
from ..errors import BillingError, ErrorCode
from ..logging_utils import get_logger
from ..models import (
    ORDER_TRANSITIONS,
    BillingEvent,
    BillingEventKind,
    OrderStatus,
    PaymentOrder,
    User,
)
from ..storage import Store

logger = get_logger("services.billing")


class BillingService:
    def __init__(self, store: Store, settings: Settings) -> None:
        self.store = store
        self.settings = settings

    def plan_of(self, user: User):
        return self.settings.plan(user.plan_key)

    def key_limit(self, user: User) -> int | None:
        return user.key_limit(self.settings.plan(user.plan_key).key_limit)

    def count_keys(self, user_id: str) -> int:
        return len(self.store.keys.where(lambda k: k.user_id == user_id))

    def assert_within_key_limit(self, user_id: str) -> None:
        user = self.store.users.find(lambda u: u.id == user_id)
        if user is None:
            raise BillingError(ErrorCode.UNAUTHORIZED)
        limit = self.key_limit(user)
        if limit is None:
            return
        if self.count_keys(user_id) >= limit:
            plan = self.plan_of(user)
            raise BillingError(
                ErrorCode.KEY_LIMIT_EXCEEDED,
                f"{plan.name}最多托管 {limit} 个厂商密钥，请升级套餐后重试",
            )

    def change_plan(self, user_id: str, plan_key: str) -> User:
        user = self.store.users.find(lambda u: u.id == user_id)
        if user is None:
            raise BillingError(ErrorCode.UNAUTHORIZED)
        self.settings.plan(plan_key)  # 校验存在性
        updated = user.model_copy(update={"plan_key": plan_key})
        self.store.users.replace(lambda u: u.id == user_id, updated)
        self._event(user_id, BillingEventKind.PLAN_CHANGE, 0, f"套餐切换为 {plan_key}")
        return updated

    # ------------------------------------------------------------- 订单
    def create_order(self, user_id: str, plan_key: str) -> PaymentOrder:
        plan = self.settings.plan(plan_key)
        order = PaymentOrder(
            id=secrets.token_hex(8),
            user_id=user_id,
            plan_key=plan_key,
            amount_cents=plan.price_cents,
            status=OrderStatus.CREATED,
        )
        self.store.orders.add(order)
        self._event(user_id, BillingEventKind.ORDER_CREATED, plan.price_cents, plan_key)
        return order

    def submit_proof(self, order_id: str, proof: str) -> PaymentOrder:
        return self._transition(order_id, OrderStatus.PROOF_SUBMITTED, proof=proof)

    def confirm_order(self, order_id: str, reviewer: str) -> PaymentOrder:
        order = self._transition(order_id, OrderStatus.CONFIRMED, reviewer=reviewer)
        self.change_plan(order.user_id, order.plan_key)
        self._event(
            order.user_id, BillingEventKind.ORDER_CONFIRMED, order.amount_cents, order.plan_key
        )
        return order

    def reject_order(self, order_id: str, reviewer: str) -> PaymentOrder:
        order = self._transition(order_id, OrderStatus.REJECTED, reviewer=reviewer)
        self._event(order.user_id, BillingEventKind.ORDER_REJECTED, order.amount_cents, order.plan_key)
        return order

    def _transition(
        self, order_id: str, target: OrderStatus, *, proof: str | None = None, reviewer: str | None = None
    ) -> PaymentOrder:
        order = self.store.orders.find(lambda o: o.id == order_id)
        if order is None:
            raise BillingError(ErrorCode.ORDER_STATE_INVALID, "订单不存在")
        if target not in ORDER_TRANSITIONS[order.status]:
            raise BillingError(
                ErrorCode.ORDER_STATE_INVALID,
                f"订单状态 {order.status.value} 不允许流转到 {target.value}",
            )
        update: dict = {"status": target, "updated_at": time.time()}
        if proof is not None:
            update["proof"] = proof
        if reviewer is not None:
            update["reviewer"] = reviewer
        updated = order.model_copy(update=update)
        self.store.orders.replace(lambda o: o.id == order_id, updated)
        return updated

    def _event(self, user_id: str, kind: BillingEventKind, amount: int, note: str) -> None:
        self.store.billing.add(
            BillingEvent(
                id=secrets.token_hex(8), user_id=user_id, kind=kind, amount_cents=amount, note=note
            )
        )

    def orders(self, *, user_id: str | None = None) -> tuple[PaymentOrder, ...]:
        if user_id is None:
            return tuple(self.store.orders.all())
        return tuple(self.store.orders.where(lambda o: o.user_id == user_id))


__all__ = ["BillingService"]
