"""FAQ 知识库：内置种子 + 云端（Supabase cs_faq）热加载 + 中文关键词打分检索。"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .config import Config
from .store import FAQS, Store

_PUNCT = re.compile(r"[\s，。！？、；：,.;!?()（）\[\]【】\"'“”]+")


@dataclass
class FaqEntry:
    id: str
    category: str  # refund | order_query | tech_support | other
    question: str
    answer: str
    keywords: str = ""
    source: str = "builtin"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "question": self.question,
            "answer": self.answer,
            "keywords": self.keywords,
        }


BUILTIN_FAQ: List[FaqEntry] = [
    FaqEntry(
        id="faq-refund-policy",
        category="refund",
        question="退款政策是怎样的？",
        answer=(
            "支持 7 天无理由退款：自签收之日起 7 天内，商品未使用且包装完好可申请全额退款；"
            "超过 7 天但在 15 天内，若为质量问题可申请退款或换货。"
        ),
        keywords="退款,退款政策,退货,无理由,七天",
    ),
    FaqEntry(
        id="faq-refund-process",
        category="refund",
        question="怎么申请退款？",
        answer=(
            "申请路径：我的订单 → 选择订单 → 申请退款 → 选择原因并上传凭证 → 提交。"
            "提交后 1 个工作日内审核，审核通过后款项按原支付渠道退回。"
        ),
        keywords="申请退款,怎么退款,退款流程,退单,退钱,退货流程",
    ),
    FaqEntry(
        id="faq-refund-eta",
        category="refund",
        question="退款多久到账？",
        answer=(
            "审核通过后：微信/支付宝 1-3 个工作日到账，银行卡 3-7 个工作日到账，"
            "信用卡以银行账单周期为准（一般 7-15 个工作日）。"
        ),
        keywords="退款到账,多久,退款时间,到账时间,退款进度",
    ),
    FaqEntry(
        id="faq-refund-fee",
        category="refund",
        question="退款会扣手续费吗？",
        answer="无理由退款且商品完好不收取手续费；因商品质量问题产生的退款，往返运费由平台承担。",
        keywords="手续费,运费,退款扣费",
    ),
    FaqEntry(
        id="faq-order-query",
        category="order_query",
        question="怎么查询我的订单？",
        answer=(
            "路径：我的 → 我的订单，可按订单号、商品名或下单时间筛选。"
            "也可直接提供订单号（如 SO20261015001）由我帮您查询状态。"
        ),
        keywords="查询订单,查单,订单查询,我的订单,订单状态",
    ),
    FaqEntry(
        id="faq-order-logistics",
        category="order_query",
        question="怎么查看物流进度？",
        answer="在订单详情点击「查看物流」即可看到实时轨迹；若显示已揽收但 48 小时无更新，可发起物流催派。",
        keywords="物流,快递,发货,运单,配送,到哪了,什么时候到",
    ),
    FaqEntry(
        id="faq-order-modify",
        category="order_query",
        question="可以修改收货地址吗？",
        answer="未发货订单可在订单详情自助修改收货地址；已发货订单需联系人工客服协助拦截改址。",
        keywords="修改地址,改地址,收货地址,改收货",
    ),
    FaqEntry(
        id="faq-tech-login",
        category="tech_support",
        question="登录不上 / 收不到验证码怎么办？",
        answer=(
            "请依次排查：① 确认手机号与区号正确；② 检查短信是否被拦截；"
            "③ 60 秒后重试；④ 切换网络或重启 App。仍失败可提供手机号后四位与手机型号转人工核查。"
        ),
        keywords="登录,登录不上,验证码,无法登录,登录失败,收不到验证码",
    ),
    FaqEntry(
        id="faq-tech-crash",
        category="tech_support",
        question="App 闪退 / 打不开怎么办？",
        answer=(
            "建议：① 更新到最新版本；② 清除缓存后重启；③ 确认系统版本满足最低要求（iOS 15 / Android 10）；"
            "④ 重装 App。若仍复现，请提供机型、系统版本与复现步骤转人工。"
        ),
        keywords="闪退,崩溃,打不开,卡顿,异常,报错,bug",
    ),
    FaqEntry(
        id="faq-tech-install",
        category="tech_support",
        question="安装失败 / 更新失败怎么解决？",
        answer="请检查存储空间是否大于 1GB、网络是否稳定；iOS 用户确认 Apple ID 已登录；Android 用户允许「未知来源」安装权限。",
        keywords="安装失败,更新失败,装不上,下载失败",
    ),
    FaqEntry(
        id="faq-account-invoice",
        category="other",
        question="怎么开电子发票？",
        answer="订单完成后在「订单详情 → 申请开票」填写抬头与税号，1 个工作日内开具并发送至预留邮箱。",
        keywords="发票,开票,电子发票,税号",
    ),
    FaqEntry(
        id="faq-account-coupon",
        category="other",
        question="优惠券为什么用不了？",
        answer="常见原因：未达使用门槛、品类不适用、已过期或与其他优惠互斥。可在「我的优惠券」查看适用范围。",
        keywords="优惠券,券,优惠,折扣,满减",
    ),
    FaqEntry(
        id="faq-human",
        category="other",
        question="怎么联系人工客服？",
        answer="工作时间 9:00-21:00 可回复「转人工」或在对话中点击转人工按钮，我会为您创建人工工单并安排坐席跟进。",
        keywords="人工,人工客服,转人工,投诉,联系客服",
    ),
]


def normalize(text: str) -> str:
    return _PUNCT.sub("", (text or "").strip().lower())


def _bigrams(text: str) -> List[str]:
    return [text[i : i + 2] for i in range(len(text) - 1)] or ([text] if text else [])


def score_entry(query: str, entry: FaqEntry) -> float:
    """关键词命中 + 中文二元字串重合度打分（0 分表示不相关）。"""
    q = normalize(query)
    if not q:
        return 0.0
    haystack = normalize(entry.question + entry.answer + entry.keywords)
    score = 0.0
    for keyword in (entry.keywords or "").split(","):
        kw = normalize(keyword)
        if len(kw) >= 2 and kw in q:
            score += 3.0
    grams = _bigrams(q)
    if grams:
        hit = sum(1 for g in grams if g in haystack)
        score += 2.0 * hit / len(grams)
    if normalize(entry.question) == q:
        score += 5.0
    return round(score, 3)


class FaqIndex:
    """知识库索引：内置种子 + 云端条目合并后检索。"""

    def __init__(self, entries: Optional[Sequence[FaqEntry]] = None):
        self.entries: List[FaqEntry] = list(entries if entries is not None else BUILTIN_FAQ)

    @classmethod
    def load(cls, cfg: Config, store: Optional[Store] = None) -> "FaqIndex":
        index = cls(list(BUILTIN_FAQ))
        if store is not None:
            index.reload_remote(store)
        return index

    def reload_remote(self, store: Store) -> int:
        """从云端知识库表合并条目，返回新增条数。"""
        try:
            rows = store.list_faq() or []
        except Exception:
            return 0
        known = {e.id for e in self.entries}
        added = 0
        for row in rows:
            fid = str(row.get("id") or "").strip()
            if not fid or fid in known:
                continue
            self.entries.append(
                FaqEntry(
                    id=fid,
                    category=row.get("category") or "other",
                    question=row.get("question") or "",
                    answer=row.get("answer") or "",
                    keywords=row.get("keywords") or "",
                    source="cloud",
                )
            )
            known.add(fid)
            added += 1
        return added

    def search(self, query: str, top_k: int = 3) -> List[Tuple[FaqEntry, float]]:
        scored = [(entry, score_entry(query, entry)) for entry in self.entries]
        scored = [item for item in scored if item[1] > 0]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]

    def seed_payload(self) -> List[Dict[str, Any]]:
        return [entry.to_dict() for entry in BUILTIN_FAQ]


__all__ = ["FaqEntry", "FaqIndex", "BUILTIN_FAQ", "score_entry", "normalize", "FAQS"]
