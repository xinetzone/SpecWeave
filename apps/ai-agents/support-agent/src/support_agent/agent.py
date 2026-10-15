"""客服 Agent 编排：意图识别 -> 知识库检索 -> 大模型生成 -> 转人工兜底 -> 持久化。"""

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from . import llm
from .config import Config
from .faq import FaqEntry, FaqIndex
from .intent import classify
from .store import Message, Store, Ticket, new_id

# 回复中出现这些措辞视为「低置信」
LOW_CONFIDENCE_MARKERS = (
    "无法回答",
    "无法解决",
    "无法确定",
    "不清楚",
    "不确定",
    "没有相关信息",
    "建议您联系人工",
    "无法提供",
)

SYSTEM_PROMPT = """你是「{brand}」的智能客服助手「小织」。
行为准则：
1. 优先依据【知识库片段】回答；片段未覆盖的内容不要编造政策、价格、时效与订单数据。
2. 回答控制在 200 字以内，中文，语气友好、专业、分点清晰。
3. 信息不足时先提 1 个澄清问题，不要臆测。
4. 本轮识别到的用户意图是「{intent}」，请围绕该意图回应。
5. 确实无法解决时，直接说明限制并建议转人工，不要反复道歉。

【知识库片段】
{context}
"""

NO_CONTEXT = "（本轮未命中知识库，请依据通用客服常识回答，不确定时建议转人工。）"


@dataclass
class TurnResult:
    session_id: str
    reply: str
    intent: str
    intent_label: str
    confidence: float
    method: str
    source: str  # llm | faq | human
    needs_human: bool
    ticket_id: str
    faq: List[Dict[str, Any]]
    latency_ms: int
    degraded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "reply": self.reply,
            "intent": self.intent,
            "intent_label": self.intent_label,
            "confidence": round(self.confidence, 3),
            "method": self.method,
            "source": self.source,
            "needs_human": self.needs_human,
            "ticket_id": self.ticket_id,
            "faq": self.faq,
            "latency_ms": self.latency_ms,
            "degraded": self.degraded,
        }


class Agent:
    """一次用户回合的处理编排。"""

    def __init__(
        self,
        cfg: Config,
        store: Store,
        faq: FaqIndex,
        chat: Optional[Callable[..., Tuple[str, int]]] = None,
    ) -> None:
        self.cfg = cfg
        self.store = store
        self.faq = faq
        self.chat = chat or llm.chat

    # ---- 主流程 ---------------------------------------------------------
    def handle(
        self,
        session_id: str,
        user_text: str,
        *,
        cfg: Optional[Config] = None,
    ) -> TurnResult:
        cfg = cfg or self.cfg
        started = time.time()
        text = (user_text or "").strip()[: cfg.max_input_chars]

        self.store.ensure_session(session_id)
        history = self.store.recent_messages(session_id, limit=cfg.history_turns * 2)

        intent = classify(cfg, text, chat=self.chat)
        hits = self.faq.search(text, top_k=cfg.faq_top_k)
        top_score = hits[0][1] if hits else 0.0
        faq_payload = [
            {"id": entry.id, "question": entry.question, "answer": entry.answer, "score": score}
            for entry, score in hits
        ]

        needs_human = intent.intent == "human" or intent.needs_human
        reason = "用户明确要求转人工" if intent.intent == "human" else ""
        reply = ""
        source = "llm"
        latency_ms = 0

        if not needs_human:
            try:
                reply, latency_ms = self._generate(cfg, text, history, intent.label, hits)
            except llm.LLMError as exc:
                # 大模型不可用 -> 知识库直答，仍不行则转人工
                if hits and top_score >= cfg.faq_score_threshold:
                    reply = self._faq_answer(hits)
                    source = "faq"
                else:
                    needs_human = True
                    reason = f"大模型不可用且知识库未命中（{exc}）"

        # 连续两轮低置信 -> 自动转人工
        if not needs_human and self._low_confidence(reply, top_score, cfg):
            streak = self._low_confidence_streak(history)
            if streak >= 1:
                needs_human = True
                reason = "连续两轮未能有效解决"

        degraded = bool(getattr(self.store, "degraded", False))
        ticket_id = ""
        if needs_human:
            ticket_id = new_id("tk")
            self.store.add_ticket(
                Ticket(
                    id=ticket_id,
                    session_id=session_id,
                    intent=intent.intent,
                    reason=reason or "系统判定需人工介入",
                )
            )
            reply = self._handoff_reply(ticket_id, intent.label)
            source = "human"

        latency_ms = latency_ms or int((time.time() - started) * 1000)

        self.store.append_message(
            Message(
                session_id=session_id,
                role="user",
                content=text,
                intent=intent.intent,
                confidence=intent.confidence,
            )
        )
        self.store.append_message(
            Message(
                session_id=session_id,
                role="assistant",
                content=reply,
                intent=intent.intent,
                confidence=top_score,
                source=source,
                needs_human=needs_human,
                low_confidence=self._low_confidence(reply, top_score, cfg)
                and not needs_human,
                faq_ids=",".join(entry.id for entry, _ in hits),
                latency_ms=latency_ms,
            )
        )
        session_fields: Dict[str, Any] = {
            "last_intent": intent.intent,
            "status": "transferred" if needs_human else "open",
        }
        if needs_human:  # transferred 为粘性标记，人工介入过就不再回退
            session_fields["transferred"] = True
        self.store.update_session(session_id, **session_fields)

        return TurnResult(
            session_id=session_id,
            reply=reply,
            intent=intent.intent,
            intent_label=intent.label,
            confidence=intent.confidence,
            method=intent.method,
            source=source,
            needs_human=needs_human,
            ticket_id=ticket_id,
            faq=faq_payload,
            latency_ms=latency_ms,
            degraded=degraded,
        )

    # ---- 内部 -----------------------------------------------------------
    def _generate(
        self,
        cfg: Config,
        text: str,
        history: List[Message],
        intent_label: str,
        hits: List[Tuple[FaqEntry, float]],
    ) -> Tuple[str, int]:
        context = NO_CONTEXT
        if hits:
            context = "\n".join(
                f"[{idx}] 问：{entry.question}\n答：{entry.answer}"
                for idx, (entry, _score) in enumerate(hits, start=1)
            )
        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(
                    brand=cfg.brand, intent=intent_label, context=context
                ),
            }
        ]
        for msg in history[-cfg.history_turns * 2 :]:
            if msg.role in ("user", "assistant") and msg.content:
                messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": text})
        return self.chat(cfg, messages)

    @staticmethod
    def _faq_answer(hits: List[Tuple[FaqEntry, float]]) -> str:
        entry, _score = hits[0]
        return f"{entry.answer}\n\n（来自知识库：{entry.question}）"

    def _low_confidence(self, reply: str, top_score: float, cfg: Config) -> bool:
        if not reply:
            return True
        if top_score < cfg.faq_score_threshold and any(
            marker in reply for marker in LOW_CONFIDENCE_MARKERS
        ):
            return True
        return False

    @staticmethod
    def _low_confidence_streak(history: List[Message]) -> int:
        streak = 0
        for msg in reversed(history):
            if msg.role != "assistant":
                continue
            if msg.low_confidence or msg.needs_human:
                streak += 1
            else:
                break
        return streak

    def _handoff_reply(self, ticket_id: str, intent_label: str) -> str:
        return (
            f"已为您创建人工工单（工单号 {ticket_id}，类型：{intent_label}）。\n"
            "人工坐席工作时间为 9:00-21:00，将尽快接入本会话；"
            "若需加速处理，请补充订单号与问题描述。"
        )


__all__ = ["Agent", "TurnResult"]
