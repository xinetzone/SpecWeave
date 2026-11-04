"""意图识别：规则快判优先，大模型兜底，无模型时仍可用。

意图集合：refund（退款/退货） / order_query（订单查询） / tech_support（技术支持）
        / human（转人工） / smalltalk（寒暄） / other（其他）
"""

from dataclasses import dataclass
from typing import Dict, List

from .config import Config

INTENT_LABELS: Dict[str, str] = {
    "refund": "退款退货",
    "order_query": "订单查询",
    "tech_support": "技术支持",
    "human": "转人工",
    "smalltalk": "寒暄问候",
    "other": "通用咨询",
}

INTENTS = tuple(INTENT_LABELS.keys())

# 规则命中数 >= RULE_CONFIDENT 时直接采纳，不再调用大模型（省钱省时）
RULE_CONFIDENT = 0.6

RULES: Dict[str, List[str]] = {
    "human": ["人工", "转人工", "人工客服", "真人", "客服经理", "投诉", "找客服", "联系客服"],
    "refund": [
        "退款",
        "退货",
        "退钱",
        "退单",
        "退费",
        "退款政策",
        "怎么退",
        "退款多久",
        "退款到账",
        "不想要了",
    ],
    "order_query": [
        "订单",
        "物流",
        "快递",
        "发货",
        "查单",
        "订单号",
        "运单",
        "配送",
        "到哪了",
        "什么时候到",
        "我的货",
        "签收",
    ],
    "tech_support": [
        "报错",
        "异常",
        "故障",
        "闪退",
        "崩溃",
        "打不开",
        "登录不上",
        "无法登录",
        "安装失败",
        "更新失败",
        "卡顿",
        "bug",
        "不能用",
        "用不了",
        "白屏",
        "技术支持",
    ],
    "smalltalk": ["你好", "您好", "hi", "hello", "在吗", "谢谢", "感谢", "再见", "拜拜"],
}

# 关键词排除：命中排除词时，对应关键词不计命中。
# 「人工智能」含「人工」——裸子串匹配会把「人工智能客服能做到什么」判成转人工，
# 直接生成人工工单并抬高转人工率（后台总览的核心指标之一）。
EXCLUSIONS: List[tuple[str, str]] = [
    ("人工智能", "人工"),
    ("人工ai", "人工"),
]

# 查询类标记：退款与订单查询同时命中时，若用户在问「进度」而非「发起」，判为订单查询。
# 例：「退货到哪了」——含「退货」（动作）与「到哪了」（进度），应归订单查询。
STATUS_MARKERS = ("到哪了", "什么时候到", "多久到", "进度", "查单", "查一下", "物流", "发货了")


@dataclass
class IntentResult:
    intent: str
    confidence: float
    method: str  # rule | llm | fallback
    needs_human: bool = False
    reason: str = ""

    @property
    def label(self) -> str:
        return INTENT_LABELS.get(self.intent, self.intent)

    def to_dict(self) -> Dict[str, object]:
        return {
            "intent": self.intent,
            "label": self.label,
            "confidence": round(self.confidence, 3),
            "method": self.method,
            "needs_human": self.needs_human,
            "reason": self.reason,
        }


def rule_classify(text: str) -> IntentResult:
    """纯规则分类：确定性强、零成本。"""
    content = (text or "").lower()
    excluded = {kw for pattern, kw in EXCLUSIONS if pattern.lower() in content}
    hits: Dict[str, int] = {}
    for intent, keywords in RULES.items():
        count = sum(
            1
            for kw in keywords
            if kw.lower() in content and kw.lower() not in excluded
        )
        if count:
            hits[intent] = count

    if not hits:
        return IntentResult(intent="other", confidence=0.0, method="rule", reason="无关键词命中")

    if "human" in hits:
        return IntentResult(
            intent="human",
            confidence=0.95,
            method="rule",
            needs_human=True,
            reason="命中转人工关键词",
        )

    # 退款与订单查询同分时，按「问进度」优先归订单查询
    if (
        hits.get("refund") == hits.get("order_query")
        and "refund" in hits
        and any(marker in content for marker in STATUS_MARKERS)
    ):
        return IntentResult(
            intent="order_query",
            confidence=0.7,
            method="rule",
            reason="退款/订单查询同命中，按进度类标记归订单查询",
        )

    best = max(hits.items(), key=lambda kv: kv[1])[0]
    count = hits[best]
    confidence = 1.0 if count >= 2 else 0.7
    return IntentResult(
        intent=best,
        confidence=confidence,
        method="rule",
        reason=f"命中 {count} 个关键词",
    )


CLASSIFY_PROMPT = """你是客服意图分类器。只输出 JSON，不要解释。
可选意图：refund(退款退货) / order_query(订单查询) / tech_support(技术支持) / human(转人工) / smalltalk(寒暄) / other(其他)。
输出格式：{"intent":"<其一>","confidence":<0-1小数>,"needs_human":<true或false>}
用户最新消息："""


def classify(
    cfg: Config,
    text: str,
    *,
    chat=None,
) -> IntentResult:
    """规则优先 + 大模型兜底的意图识别。"""
    rule = rule_classify(text)
    if rule.confidence >= RULE_CONFIDENT:
        return rule

    if not cfg.llm_ready:
        return (
            rule
            if rule.intent != "other"
            else IntentResult(
                intent="other", confidence=0.2, method="fallback", reason="无大模型且无关键词"
            )
        )

    try:
        from . import llm

        caller = chat or llm.chat
        reply, _ = caller(
            cfg,
            [
                {"role": "system", "content": CLASSIFY_PROMPT},
                {"role": "user", "content": text[:500]},
            ],
            temperature=0.0,
            max_tokens=120,
            timeout=min(cfg.request_timeout, 15.0),
        )
        data = llm.extract_json(reply)
        intent = str(data.get("intent", "")).strip()
        if intent not in INTENTS:
            return rule if rule.intent != "other" else IntentResult(
                intent="other", confidence=0.3, method="fallback", reason="大模型返回非法意图"
            )
        try:
            confidence = float(data.get("confidence", 0.6))
        except (TypeError, ValueError):
            confidence = 0.6
        return IntentResult(
            intent=intent,
            confidence=max(0.0, min(1.0, confidence)),
            method="llm",
            needs_human=bool(data.get("needs_human", intent == "human")),
            reason="大模型分类",
        )
    except Exception as exc:  # 大模型不可用 -> 退回规则结果
        fallback = rule if rule.intent != "other" else IntentResult(
            intent="other", confidence=0.2, method="fallback", reason=f"大模型不可用：{exc}"
        )
        return fallback


__all__ = ["INTENTS", "INTENT_LABELS", "IntentResult", "classify", "rule_classify"]
