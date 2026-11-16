# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import re
from pathlib import Path

from .constants import (
    REQUIRED_SECTIONS,
    OPTIONAL_SECTIONS,
    SECTION_ALIASES,
    RECOMMENDED_SECTIONS,
    IMPORTANT_SECTIONS,
    IMPORTANT_SECTION_ALIASES,
    INNOVATION_PATTERN_SECTIONS,
    MIN_PATTERN_LINES,
    MAX_PATTERN_LINES,
    RECOMMENDED_MIN_LINES,
    RECOMMENDED_MAX_LINES,
    WHY_EXPLANATION_PATTERN,
    CHECKLIST_ITEM_PATTERN,
    SECTION_HEADER_PATTERN,
    MERMAID_PATTERN,
    CROSS_REFERENCE_PATTERN,
    INNOVATION_TYPE_KEYWORDS,
    FALLBACK_INNOVATION_KEYWORDS,
    FAILURE_CASE_PATTERN,
    ANTI_TARGET_PATTERN,
    WARNING_SIGNAL_PATTERN,
)
from .models import CheckResult


def check_sections(content, fields=None):
    """章节检查：必要章节做别名归一，模式类型/成熟度改为可选（A1 模板口径统一）。

    fields 为 frontmatter 解析结果；提供时「成熟度」章节可由 maturity 字段承担，
    与 `pattern-to-methodology-library` 模板一致。
    """
    results = []
    fields = fields or {}
    section_headers = {m.group(1).strip(): m.start() for m in SECTION_HEADER_PATTERN.finditer(content)}
    section_names = set(section_headers.keys())

    for sec_name, sec_id in REQUIRED_SECTIONS.items():
        candidates = (sec_name,) + SECTION_ALIASES.get(sec_name, ())
        found = any(any(c in name for name in section_names) for c in candidates)
        results.append(CheckResult(
            name=f"sections.required.{sec_id}",
            passed=found,
            severity="error",
            message=f"包含必要章节「{sec_name}」" if found
            else f"缺少必要章节「{sec_name}」（或其等价写法 {'/'.join(candidates[1:])}）"
        ))

    for sec_name, sec_id in OPTIONAL_SECTIONS.items():
        found = any(sec_name in name for name in section_names)
        if not found and sec_id == "maturity" and fields.get("maturity"):
            results.append(CheckResult(
                name=f"sections.required.{sec_id}",
                passed=True,
                severity="info",
                message="成熟度由 frontmatter 的 maturity 字段承担，无需独立章节"
            ))
            continue
        results.append(CheckResult(
            name=f"sections.required.{sec_id}",
            passed=True,
            severity="info",
            message=f"包含可选章节「{sec_name}」" if found
            else f"可选章节「{sec_name}」缺省（新模板不强制）"
        ))

    core_found = False
    for sec_name, sec_id in RECOMMENDED_SECTIONS.items():
        if any(sec_name in name for name in section_names):
            core_found = True
            break
    results.append(CheckResult(
        name="sections.core_content",
        passed=core_found,
        severity="error",
        message="包含核心内容章节（核心规则/核心做法/操作流程等）" if core_found
        else "缺少核心内容章节（应包含核心规则/核心做法/操作流程之一）"
    ))

    for sec_name, sec_id in IMPORTANT_SECTIONS.items():
        candidates = (sec_name,) + IMPORTANT_SECTION_ALIASES.get(sec_name, ())
        found = any(any(c in name for name in section_names) for c in candidates)
        results.append(CheckResult(
            name=f"sections.important.{sec_id}",
            passed=found,
            severity="warn",
            message=f"包含重要章节「{sec_name}」" if found
            else f"建议补充「{sec_name}」章节（提高模式可复用性）"
        ))

    checklist_items = len(CHECKLIST_ITEM_PATTERN.findall(content))
    has_checklist_section = any("检查清单" in name for name in section_names)
    if has_checklist_section:
        checklist_ok = checklist_items >= 3
        results.append(CheckResult(
            name="sections.checklist_items",
            passed=checklist_ok,
            severity="warn",
            message=f"实施检查清单包含{checklist_items}个可执行检查项" if checklist_ok
            else f"检查清单只有{checklist_items}个项，建议至少3个可执行检查项（- [ ]格式）"
        ))
    else:
        results.append(CheckResult(
            name="sections.checklist_items",
            passed=False,
            severity="warn",
            message="无实施检查清单章节，跳过检查项计数"
        ))

    return results


def check_file_length(pattern_md, content):
    results = []
    lines = content.count("\n") + 1

    if lines < MIN_PATTERN_LINES:
        passed = False
        severity = "error"
        msg = f"文件仅{lines}行，过短可能内容不完整（建议≥{RECOMMENDED_MIN_LINES}行）"
    elif lines > MAX_PATTERN_LINES:
        passed = False
        severity = "warn"
        msg = f"文件{lines}行，过长建议考虑拆分（建议≤{RECOMMENDED_MAX_LINES}行）"
    elif lines < RECOMMENDED_MIN_LINES:
        passed = True
        severity = "warn"
        msg = f"文件{lines}行（建议≥{RECOMMENDED_MIN_LINES}行以保证完整性）"
    elif lines > RECOMMENDED_MAX_LINES:
        passed = True
        severity = "warn"
        msg = f"文件{lines}行（建议≤{RECOMMENDED_MAX_LINES}行以保持可读性）"
    else:
        passed = True
        severity = "info"
        msg = f"文件{lines}行（长度适中）"

    results.append(CheckResult(
        name="file.length",
        passed=passed,
        severity=severity,
        message=msg
    ))

    return results


def check_why_explanations(content):
    results = []

    why_count = len(WHY_EXPLANATION_PATTERN.findall(content))
    has_why = why_count >= 1

    results.append(CheckResult(
        name="why.explanations",
        passed=has_why,
        severity="warn",
        message=f"包含{why_count}个Why设计意图解释" if has_why
        else "建议补充关键规则的Why解释（帮助理解设计意图和边界情况判断）"
    ))

    return results


def check_visualization(content):
    results = []

    mermaid_count = len(MERMAID_PATTERN.findall(content))
    has_mermaid = mermaid_count >= 1

    results.append(CheckResult(
        name="visualization.mermaid",
        passed=has_mermaid,
        severity="info",
        message=f"包含{mermaid_count}个Mermaid可视化图表" if has_mermaid
        else "建议添加Mermaid流程图/决策树增强理解（非强制）"
    ))

    return results


def check_cross_references(content):
    results = []

    xref_count = len(CROSS_REFERENCE_PATTERN.findall(content))
    has_related_section = "与现有模式的关系" in content or "关联模式" in content or "相关模式" in content

    if has_related_section:
        xref_ok = xref_count >= 2
        results.append(CheckResult(
            name="cross_references.exist",
            passed=xref_ok,
            severity="warn",
            message=f"包含{xref_count}个模式交叉引用链接" if xref_ok
            else f"关联模式章节只有{xref_count}个链接，建议至少引用2个相关模式构建知识网络"
        ))
    else:
        results.append(CheckResult(
            name="cross_references.exist",
            passed=False,
            severity="warn",
            message="缺少「与现有模式的关系」章节，无法建立模式间知识网络"
        ))

    return results


def _mask_frontmatter(content: str) -> str:
    """把 YAML frontmatter 抹成等长空白（保留换行与字符偏移），返回全文。

    兜底分类只看正文，但**不能改变扫描窗口**：frontmatter 是元数据，其中的
    maturity_note / source / tags 常出现「跨域迁移」「反向」等词，不代表模式主张
    （2026-11-16 实测：执行类模式的 maturity_note 写「跨域迁移为同构推演」即被
    误判为创新类）。若直接切除 frontmatter，后续正文会前移进入 1000 字符窗口，
    反而把原本在窗口外的正文关键词纳入（实测全库 +15 篇误判），故改用等长掩码。
    """
    if not content.startswith("---"):
        return content
    end = content.find("\n---", 3)
    if end == -1:
        return content
    mask_end = end + 4
    masked_head = re.sub(r"[^\n]", " ", content[:mask_end])
    return masked_head + content[mask_end:]


def _is_innovation_pattern(content: str) -> bool:
    """判断模式是否为创新/跨领域迁移类模式。

    有「## 模式类型」章节时只看该章节（宽口径，含裸「迁移」「反向」）；
    无该章节时回退扫描正文开头 1000 字符，但用短语级关键词
    （FALLBACK_INNOVATION_KEYWORDS）并对 frontmatter 做等长掩码——开头普遍
    出现「迁移」二字的 SOP/速查/操作手册，以及「反向」用于表示计算方向
    （前向/反向计算、反向传播、反向依赖）的工程文档，不应被兜底判为创新类。
    """
    type_section_match = re.search(
        r"##\s*模式类型\s*\n(.+?)(?=\n##|\Z)", content, re.DOTALL
    )
    if type_section_match:
        type_text = type_section_match.group(1)
        return bool(INNOVATION_TYPE_KEYWORDS.search(type_text))
    return bool(FALLBACK_INNOVATION_KEYWORDS.search(_mask_frontmatter(content)[:1000]))


def check_innovation_pattern_v2(content: str) -> list[CheckResult]:
    """创新/跨领域迁移类模式V2强制检查项。

    基于i-have-adhd V2审查发现的成功偏误/确认偏误缺陷，
    对创新类模式强制执行4项V2检查：
    1. 至少1个真实失败案例
    2. 反目标用户/场景分析
    3. 早期预警信号
    4. 边界/适用前提明确

    对执行/协作类模式跳过这些检查。
    """
    if not _is_innovation_pattern(content):
        return [CheckResult(
            name="innovation.v2_gate",
            passed=True,
            severity="info",
            message="非创新/跨领域类模式，跳过V2强制检查"
        )]

    results = []

    failure_count = len(FAILURE_CASE_PATTERN.findall(content))
    # 标题匹配改为「标题行包含失败类词」，兼容带修饰前缀的写法
    # （如「已记录的失败案例（V2补充）」「失败案例与边界」）。
    has_failure_section = bool(re.search(
        r"^##+.*(失败案例|反面案例|失败教训|失败警示|负面案例).*$",
        content, re.MULTILINE,
    ))
    has_real_failure = failure_count >= 1 and has_failure_section
    results.append(CheckResult(
        name="innovation.failure_cases",
        passed=has_real_failure,
        severity="error" if not has_real_failure else "info",
        message="包含至少1个真实失败案例（V2要求）" if has_real_failure
        else "创新/跨领域类模式必须包含至少1个真实失败案例（防止成功偏误），请补充「失败案例」章节"
    ))

    anti_target_count = len(ANTI_TARGET_PATTERN.findall(content))
    has_anti_target_section = bool(re.search(
        r"##+\s*(.*?[：:])?\s*(反目标|不适用|边界场景|反目标用户|反目标场景|适用边界|不适用场景|反模式警示)",
        content, re.MULTILINE,
    ))
    has_anti_target = anti_target_count >= 3 and has_anti_target_section
    results.append(CheckResult(
        name="innovation.anti_target_users",
        passed=has_anti_target,
        severity="error" if not has_anti_target else "info",
        message="包含反目标用户/场景分析（≥3类，V2要求）" if has_anti_target
        else f"创新/跨领域类模式必须分析≥3类反目标用户/场景（防止确认偏误），当前检测到{anti_target_count}处相关提及，请补充「反目标用户/场景」章节"
    ))

    warning_count = len(WARNING_SIGNAL_PATTERN.findall(content))
    has_warning_section = bool(re.search(
        r"##+\s*(早期预警|预警信号|警告信号|警示信号|危险信号)",
        content, re.MULTILINE | re.IGNORECASE,
    ))
    has_warnings = warning_count >= 3 and has_warning_section
    results.append(CheckResult(
        name="innovation.warning_signals",
        passed=has_warnings,
        severity="warn" if not has_warnings else "info",
        message="包含早期预警信号表（V2建议）" if has_warnings
        else f"建议补充≥5个早期预警信号（出现时应暂停推进回到用户研究），当前检测到{warning_count}处相关提及"
    ))

    has_boundary = bool(re.search(
        r"##+\s*(.*?[：:])?\s*(适用边界|边界条件|适用前提|前提条件|不适用场景|例外处理)",
        content, re.MULTILINE,
    ))
    results.append(CheckResult(
        name="innovation.boundary_conditions",
        passed=has_boundary,
        severity="warn" if not has_boundary else "info",
        message="明确标注适用边界/前提条件" if has_boundary
        else "建议明确标注适用边界和前提条件（8个适用前提检查表）"
    ))

    return results


PENDING_EVIDENCE_MARKER = "暂无实测失败样本"


def check_pending_evidence(content):
    """待补失败样本清单：显式登记的「暂无实测失败样本」在每次质量门中被列出。

    这是登记项而非缺陷项——登记本身是诚实的，因此不用 error（不阻断提交），
    但必须持续可见：warn 级会出现在每次质量门输出里；一旦补入真实案例并删除声明，
    该项自动从清单消失。
    """
    pending = PENDING_EVIDENCE_MARKER in content
    return [CheckResult(
        name="evidence.pending_failure_sample",
        passed=not pending,
        severity="warn",
        message="本文显式登记「暂无实测失败样本」，补入真实失败案例后请删除该声明"
        if pending else "本文已具备失败样本（或未登记待补）",
    )]

