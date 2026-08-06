"""对抗审查补充提示词自动加载器。

基于审查对象类型（治理策略/架构模式/通用）自动检测并注入对应的补充攻击视角、
检查清单和设计模板，确保V阶段对抗审查覆盖递归爆炸、信任根、自积累负反馈三大盲区。

设计原则：
- 零配置自动检测：根据文件路径和内容关键词判断是否需要注入补充视角
- 幂等安全：已注入的补充内容不会重复注入
- 手动覆盖：支持--force/--disable标志覆盖自动检测
- 可审计：输出注入日志说明哪些补充项被加载及原因
"""

from __future__ import annotations


# 版本校验：相对导入共享库（depth=0）
from .python310_version_check import enforce_python310

enforce_python310()

import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENTS_DIR = PROJECT_ROOT / ".agents"

ADDENDUM_PROMPT = AGENTS_DIR / "prompts" / "pattern-adversarial-review-addendum.md"
HARDENING_CHECKLIST = AGENTS_DIR / "checklists" / "pattern-extraction-hardening-checklist.md"
SELF_ACCUM_TEMPLATE = AGENTS_DIR / "templates" / "self-accumulating-mechanism-template.md"

GOVERNANCE_PATH_PATTERNS = [
    re.compile(r"governance-strategy", re.IGNORECASE),
    re.compile(r"methodology-patterns", re.IGNORECASE),
    re.compile(r"process-patterns", re.IGNORECASE),
]

ARCHITECTURE_PATH_PATTERNS = [
    re.compile(r"architecture-patterns", re.IGNORECASE),
]

PATTERN_PATH_PATTERNS = [
    re.compile(r"retrospective[\\/]+patterns", re.IGNORECASE),
    re.compile(r"methodology-patterns", re.IGNORECASE),
]

GOVERNANCE_KEYWORDS = [
    "迭代预算", "回溯", "重试", "熔断", "治理", "工作流", "流程控制",
    "阶段守卫", "质量门", "反馈循环", "闭环",
]

ARCHITECTURE_KEYWORDS = [
    "信任链", "溯源", "验证工具", "哈希", "签名", "日志", "审计",
    "append-only", "不可篡改", "完整性", "provenance",
]

SELF_ACCUM_KEYWORDS = [
    "自学习", "知识库", "经验库", "自积累", "自适应", "反馈循环",
    "经验沉淀", "历史优化", "置信度", "从每次", "学习", "积累",
    "优化", "学习到", "历史经验",
]

INJECTION_MARKER = "<!-- ADVERSARIAL_ADDENDUM_INJECTED -->"
INJECTION_SECTION_START = "<!-- ADVERSARIAL_ADDENDUM_START -->"
INJECTION_SECTION_END = "<!-- ADVERSARIAL_ADDENDUM_END -->"


@dataclass(frozen=True)
class AddendumFile:
    """单个补充文件定义。"""

    path: Path
    name: str
    description: str
    category: str
    always_load: bool = False

    @property
    def exists(self) -> bool:
        return self.path.is_file()

    def load_content(self) -> str:
        if not self.exists:
            raise FileNotFoundError(f"补充文件不存在: {self.path}")
        text = self.path.read_text(encoding="utf-8")
        return _strip_frontmatter(text)


@dataclass
class ReviewContext:
    """审查上下文——描述正在审查的对象。"""

    target_path: Path | None = None
    scenario: str = "auto"
    content_preview: str = ""
    forced_addenda: set[str] = field(default_factory=set)
    disabled_addenda: set[str] = field(default_factory=set)

    @classmethod
    def from_path(cls, path: Path, scenario: str = "auto") -> ReviewContext:
        preview = ""
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8")
                preview = _strip_frontmatter(text)[:3000]
            except Exception:
                preview = ""
        return cls(target_path=path, scenario=scenario, content_preview=preview)


@dataclass
class LoadResult:
    """补充内容加载结果。"""

    addenda_loaded: list[AddendumFile] = field(default_factory=list)
    addenda_skipped: list[tuple[AddendumFile, str]] = field(default_factory=list)
    detection_reasons: list[str] = field(default_factory=list)
    review_type: str = "general"
    content: str = ""

    @property
    def has_addenda(self) -> bool:
        return len(self.addenda_loaded) > 0


def _strip_frontmatter(text: str) -> str:
    """去除Markdown frontmatter，返回正文内容。"""
    text = text.strip()
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    if text.startswith("+++"):
        end = text.find("\n+++", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def _match_any(patterns: list[re.Pattern[str]], text: str) -> bool:
    return any(p.search(text) for p in patterns)


def _count_keywords(keywords: list[str], text: str) -> int:
    count = 0
    for kw in keywords:
        if kw.lower() in text.lower():
            count += 1
    return count


def _detect_review_type(ctx: ReviewContext) -> tuple[str, list[str]]:
    """检测审查类型，返回 (类型, 检测原因列表)。"""
    reasons: list[str] = []

    if ctx.scenario == "governance":
        return "governance", ["手动指定scenario=governance"]
    if ctx.scenario == "architecture":
        return "architecture", ["手动指定scenario=architecture"]
    if ctx.scenario == "pattern":
        return "pattern", ["手动指定scenario=pattern"]

    if ctx.target_path is not None:
        path_str = str(ctx.target_path)
        if _match_any(GOVERNANCE_PATH_PATTERNS, path_str):
            reasons.append(f"路径匹配治理策略模式: {path_str}")
            return "governance", reasons
        if _match_any(ARCHITECTURE_PATH_PATTERNS, path_str):
            reasons.append(f"路径匹配架构模式: {path_str}")
            return "architecture", reasons

    if ctx.content_preview:
        gov_kw = _count_keywords(GOVERNANCE_KEYWORDS, ctx.content_preview)
        arch_kw = _count_keywords(ARCHITECTURE_KEYWORDS, ctx.content_preview)

        if gov_kw >= 2:
            reasons.append(f"内容包含{gov_kw}个治理类关键词")
            return "governance", reasons
        if arch_kw >= 2:
            reasons.append(f"内容包含{arch_kw}个架构类关键词")
            return "architecture", reasons

    if ctx.target_path is not None and _match_any(PATTERN_PATH_PATTERNS, str(ctx.target_path)):
        reasons.append("路径在patterns/目录下")
        return "pattern", reasons

    return "general", ["无匹配特征，使用通用审查视角"]


def _has_self_accumulation(ctx: ReviewContext) -> tuple[bool, str]:
    """检测是否包含自积累机制。"""
    if ctx.content_preview:
        kw_count = _count_keywords(SELF_ACCUM_KEYWORDS, ctx.content_preview)
        if kw_count >= 2:
            return True, f"内容包含{kw_count}个自积累相关关键词"
    return False, ""


def _is_already_injected(content: str) -> bool:
    """检查内容是否已包含补充注入标记。"""
    return INJECTION_MARKER in content


def _build_addendum_section(loaded: list[AddendumFile], detection_reasons: list[str]) -> str:
    """构建注入的补充内容区块。"""
    parts = [INJECTION_SECTION_START, INJECTION_MARKER, ""]
    parts.append("## 🔍 对抗审查补充攻击视角（自动注入）")
    parts.append("")
    if detection_reasons:
        parts.append("> **检测原因**：" + "；".join(detection_reasons))
        parts.append("")
    for addendum in loaded:
        parts.append(f"### [{addendum.category}] {addendum.name}")
        parts.append("")
        parts.append(f"> {addendum.description}")
        parts.append("")
        parts.append(addendum.load_content())
        parts.append("")
    parts.append(INJECTION_SECTION_END)
    return "\n".join(parts)


def get_all_addenda() -> list[AddendumFile]:
    """返回所有可用的补充文件定义。"""
    return [
        AddendumFile(
            path=ADDENDUM_PROMPT,
            name="模式对抗审查补充攻击视角",
            description="治理/架构类模式V阶段必选：递归爆炸/信任根/自积累负反馈三个攻击视角",
            category="补充提示词",
        ),
        AddendumFile(
            path=HARDENING_CHECKLIST,
            name="新模式萃取补强检查清单",
            description="E→V阶段自检：连锁递归/参数可落地/自积累负反馈/信任链完整4大类17项",
            category="检查清单",
        ),
        AddendumFile(
            path=SELF_ACCUM_TEMPLATE,
            name="自积累机制负反馈设计模板",
            description="含自学习/知识库/经验库机制时配套使用：条目生命周期/置信度区间/防错误复合/冷启动策略",
            category="设计模板",
        ),
    ]


def load_applicable_addenda(ctx: ReviewContext) -> LoadResult:
    """根据审查上下文加载适用的补充文件。"""
    result = LoadResult()
    all_addenda = get_all_addenda()

    review_type, reasons = _detect_review_type(ctx)
    result.review_type = review_type
    result.detection_reasons = reasons

    has_self_accum, self_accum_reason = _has_self_accumulation(ctx)
    if has_self_accum:
        result.detection_reasons.append(self_accum_reason)

    for addendum in all_addenda:
        if addendum.name in ctx.disabled_addenda:
            result.addenda_skipped.append((addendum, "手动禁用"))
            continue

        if addendum.name in ctx.forced_addenda:
            if addendum.exists:
                result.addenda_loaded.append(addendum)
            else:
                result.addenda_skipped.append((addendum, "文件不存在"))
            continue

        should_load = False

        if review_type in ("governance", "architecture", "pattern"):
            if addendum.path == ADDENDUM_PROMPT:
                should_load = True
            elif addendum.path == HARDENING_CHECKLIST:
                should_load = True

        if addendum.path == SELF_ACCUM_TEMPLATE and has_self_accum:
            should_load = True

        if review_type == "governance" and addendum.path == SELF_ACCUM_TEMPLATE:
            should_load = has_self_accum or _count_keywords(
                ["预算", "回溯", "迭代"], ctx.content_preview
            ) >= 1

        if should_load:
            if addendum.exists:
                result.addenda_loaded.append(addendum)
            else:
                result.addenda_skipped.append((addendum, "文件不存在"))
        else:
            result.addenda_skipped.append((addendum, f"审查类型={review_type}，不适用"))

    if result.addenda_loaded:
        result.content = _build_addendum_section(
            result.addenda_loaded, result.detection_reasons
        )

    return result


def inject_into_prompt(base_prompt: str, ctx: ReviewContext) -> str:
    """将补充内容注入到基础prompt中，返回完整prompt。"""
    if _is_already_injected(base_prompt):
        logger.info("补充内容已存在，跳过重复注入")
        return base_prompt

    result = load_applicable_addenda(ctx)
    if not result.has_addenda:
        return base_prompt

    return base_prompt.rstrip() + "\n\n" + result.content + "\n"


def list_addenda_summary(result: LoadResult) -> str:
    """生成人类可读的加载摘要。"""
    lines = [f"审查类型: {result.review_type}"]
    if result.detection_reasons:
        lines.append(f"检测依据: {'; '.join(result.detection_reasons)}")
    lines.append("")
    if result.addenda_loaded:
        lines.append(f"已加载 {len(result.addenda_loaded)} 个补充文件:")
        for a in result.addenda_loaded:
            lines.append(f"  ✓ [{a.category}] {a.name}")
    if result.addenda_skipped:
        lines.append("")
        lines.append(f"已跳过 {len(result.addenda_skipped)} 个:")
        for a, reason in result.addenda_skipped:
            lines.append(f"  - [{a.category}] {a.name} ({reason})")
    return "\n".join(lines)

