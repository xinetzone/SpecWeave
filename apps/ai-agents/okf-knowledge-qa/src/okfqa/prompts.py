"""提示词资产与上下文装配。

上下文采用 `[编号]` 锚点编号，与返回给前端的 citations 数组一一对应，
使答案中的引用标记可被前端解析为可跳转的出处卡片。
"""

from .config import max_context_chars
from .retrieval import Hit

SYSTEM_PROMPT = """你是「OKF 知识库问答助手」，基于 SpecWeave 仓库的 OKF 知识包（bundles）回答用户问题。

严格约束：
1. 只依据【参考资料】作答。资料中没有的内容，直接回答"资料中未涉及"，禁止用先验知识编造。
2. 引用资料时，在句末用方括号标注编号，例如：道法自然是道家思想的核心[1]。可同时引用多个：[1][3]。
3. 答案使用简体中文，结构清晰：先给结论，再分点展开。
4. 若参考资料之间相互冲突，明确指出分歧并分别标注出处。
5. 不要复述问题，不要输出"根据参考资料"这类套话，直接给答案。"""

DEGRADED_NOTICE_NO_KEY = (
    "当前未配置大模型凭据，以下为知识库中相关度最高的原文片段，未经过大模型归纳。"
)
DEGRADED_NOTICE_LLM_FAILED = (
    "大模型调用失败，以下为知识库中相关度最高的原文片段，未经过大模型归纳。"
)


def build_context(hits: list[Hit]) -> str:
    """把命中片段装配为带编号锚点的上下文，并受字符预算约束。"""
    budget = max_context_chars()
    parts: list[str] = []
    used = 0
    for i, hit in enumerate(hits, start=1):
        header = f"[{i}]《{hit.title}》 知识包：{hit.bundle}"
        block = f"{header}\n{hit.body}"
        if used + len(block) > budget:
            remaining = budget - used
            if remaining > 200:
                parts.append(f"{header}\n{hit.body[: remaining - len(header) - 1]}…")
            break
        parts.append(block)
        used += len(block) + 2
    return "\n\n".join(parts)


def build_user_prompt(question: str, hits: list[Hit]) -> str:
    context = build_context(hits)
    return f"【参考资料】\n{context}\n\n【用户问题】\n{question}\n\n请按系统提示的要求作答。"


def build_degraded_answer(hits: list[Hit], llm_failed: bool = False) -> str:
    """降级答案：直接列出相关片段，保证服务仍可用。

    `llm_failed` 用于区分「未配置凭据」与「已配置但调用失败」——
    两者处置手段完全不同，混用同一文案会把线上故障伪装成配置缺失。
    """
    notice = DEGRADED_NOTICE_LLM_FAILED if llm_failed else DEGRADED_NOTICE_NO_KEY
    lines = [notice, ""]
    for i, hit in enumerate(hits, start=1):
        excerpt = hit.body if len(hit.body) <= 320 else hit.body[:320] + "…"
        lines.append(f"[{i}]《{hit.title}》（{hit.bundle}）")
        lines.append(excerpt)
        lines.append("")
    return "\n".join(lines).strip()
