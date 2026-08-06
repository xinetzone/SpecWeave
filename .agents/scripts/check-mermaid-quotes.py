#!/usr/bin/env python3
"""Mermaid 引号语法检查器。

基于 mermaid-quote-rules-checklist.md 萃取的规则，自动检测 Markdown 文档中
Mermaid 代码块的引号使用错误。覆盖 16 类图表的引号规则，重点检测 Top 5 反模式。

用法:
    python check-mermaid-quotes.py [文件或目录...]
    python check-mermaid-quotes.py --path .agents/docs/
    python check-mermaid-quotes.py --json file.md

规则来源: .agents/docs/knowledge/learning/04-docs-markup-tooling/mermaid-wiki/mermaid-quote-rules-checklist.md
"""

# ── 路径引导（遵循项目脚本规范）──────────────────────────────
import sys as _sys
from pathlib import Path as _Path
_SCRIPTS_DIR = _Path(__file__).resolve().parent
_LIB_DIR = _SCRIPTS_DIR / "lib"
_sys.path.insert(0, str(_LIB_DIR))
_sys.path.insert(0, str(_SCRIPTS_DIR))

from python310_version_check import enforce_python310  # noqa: E402

enforce_python310()

import argparse  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import List, Optional, Tuple  # noqa: E402

from lib.cli import (  # noqa: E402
    add_common_args,
    print_error,
    print_header,
    print_pass,
    print_summary,
    print_warn,
    setup_safe_output,
)
from constants import ANSI_CYAN, ANSI_GREEN, ANSI_RED, ANSI_RESET, ANSI_YELLOW  # noqa: E402

# ── 常量 ────────────────────────────────────────────────────

MERMAID_FENCE_RE = re.compile(r"(```mermaid\s*\n)(.*?)(```)", re.DOTALL)
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")

ISSUE_ERROR = "error"
ISSUE_WARNING = "warning"


@dataclass
class Issue:
    """单个检测问题。"""
    line: int
    level: str  # error / warning
    rule_id: str
    message: str
    diagram_type: str
    snippet: str = ""

    def to_dict(self) -> dict:
        return {
            "line": self.line,
            "level": self.level,
            "rule_id": self.rule_id,
            "message": self.message,
            "diagram_type": self.diagram_type,
            "snippet": self.snippet,
        }


@dataclass
class BlockResult:
    """单个 Mermaid 代码块的检测结果。"""
    file_path: str
    start_line: int
    diagram_type: str
    issues: List[Issue] = field(default_factory=list)


# ── 图表类型检测 ─────────────────────────────────────────────

def detect_diagram_type(block_text: str) -> str:
    """检测 Mermaid 代码块的图表类型。"""
    first_line = block_text.strip().split("\n")[0].strip().lower()
    if not first_line:
        return "unknown"
    dt = first_line.split()[0]
    if dt in ("flowchart", "graph"):
        return "flowchart"
    if dt.startswith("statediagram"):
        return "stateDiagram"
    if dt == "sequencediagram":
        return "sequenceDiagram"
    if dt == "classdiagram":
        return "classDiagram"
    if dt == "erdiagram":
        return "erDiagram"
    if dt == "pie":
        return "pie"
    if dt == "gantt":
        return "gantt"
    if dt == "journey":
        return "journey"
    if dt == "timeline":
        return "timeline"
    if dt == "sankey-beta" or dt == "sankey":
        return "sankey"
    if dt == "quadrantchart":
        return "quadrantChart"
    if dt == "gitgraph":
        return "gitGraph"
    if dt == "requirementdiagram":
        return "requirementDiagram"
    if dt == "mindmap":
        return "mindmap"
    if dt == "block":
        return "block"
    if dt.startswith("c4"):
        return "C4"
    if dt == "zenuml":
        return "zenuml"
    if dt == "xychart-beta":
        return "xychart-beta"
    return "unknown"


# ── 通用工具函数 ─────────────────────────────────────────────

def _line_in_block(block_text: str, match_start: int) -> int:
    """计算正则匹配在代码块中的行号（从1开始）。"""
    return block_text[:match_start].count("\n") + 1


def _snippet(line_text: str, max_len: int = 50) -> str:
    """截取代码行片段用于显示。"""
    s = line_text.strip()
    return s[:max_len] + ("..." if len(s) > max_len else "")


def _make_issue(start_line: int, line_in_block: int, level: str, rule_id: str,
                message: str, diagram_type: str, snippet: str = "") -> Issue:
    return Issue(
        line=start_line + line_in_block - 1,
        level=level,
        rule_id=rule_id,
        message=message,
        diagram_type=diagram_type,
        snippet=snippet,
    )


# ── 通用引号检查（跨图表）────────────────────────────────────

def _check_title_quotes(block_text: str, start_line: int, diagram_type: str) -> List[Issue]:
    """检测 title 后多余引号（适用于 gantt/pie/journey/timeline/quadrantChart/C4/flowchart）。"""
    issues = []
    # 模式1: title 独占一行 → title "xxx"
    pat1 = re.compile(r"^(\s*title\s+)(['\"])(.+)\2\s*$", re.MULTILINE)
    for m in pat1.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        issues.append(_make_issue(
            start_line, lb, ISSUE_ERROR, "TITLE-QUOTED",
            f"title 不应加引号包裹，应改为「title {m.group(3)}」",
            diagram_type, snippet,
        ))
    # 模式2: title 与图表关键字同行 → pie title "xxx" / journey title "xxx"
    pat2 = re.compile(r"^(\s*(?:pie|journey|timeline)\s+title\s+)(['\"])(.+)\2\s*$", re.MULTILINE)
    for m in pat2.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        kw = m.group(0).strip().split()[0]
        issues.append(_make_issue(
            start_line, lb, ISSUE_ERROR, "TITLE-QUOTED",
            f"{kw} title 不应加引号，应改为「{kw} title {m.group(3)}」",
            diagram_type, snippet,
        ))
    return issues


def _check_arrow_label_quotes(block_text: str, start_line: int, diagram_type: str,
                               arrow_pat: re.Pattern, label_group: int = 2,
                               rule_msg: str = "箭头/关系标签不应加引号") -> List[Issue]:
    """检测箭头/关系标签后的多余引号（通用模式）。

    匹配模式：在 --> / -- / <|-- 等操作符后 : 或 | 引导的标签文本被引号包裹。
    """
    issues = []
    for m in arrow_pat.finditer(block_text):
        label = m.group(label_group)
        if label is None:
            continue
        label_stripped = label.strip()
        if (label_stripped.startswith('"') and label_stripped.endswith('"')) or \
           (label_stripped.startswith("'") and label_stripped.endswith("'")):
            lb = _line_in_block(block_text, m.start())
            snippet = _snippet(m.group(0))
            inner = label_stripped[1:-1]
            issues.append(_make_issue(
                start_line, lb, ISSUE_ERROR, "ARROW-LABEL-QUOTED",
                f"{rule_msg}，应去掉引号改为「{inner}」",
                diagram_type, snippet,
            ))
    return issues


# ── 各图表类型专用检查 ──────────────────────────────────────

def _check_flowchart(block_text: str, start_line: int) -> List[Issue]:
    issues = []
    issues.extend(_check_title_quotes(block_text, start_line, "flowchart"))

    # 不对称形节点多余方括号：G>["文本"] → G>"文本"]
    asym_pat = re.compile(r'\b([A-Za-z][A-Za-z0-9_]*)>\[([^\]]*"\])', re.MULTILINE)
    for m in asym_pat.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        issues.append(_make_issue(
            start_line, lb, ISSUE_ERROR, "FC-ASYMM-BRACKET",
            f"不对称形节点语法错误，多了一个[：应为「{m.group(1)}>\"...\"]」",
            "flowchart", snippet,
        ))

    # 注意：流程图 pipe 标签语法 -->|"label"| 中的引号是正确的（用于含中文/空格的标签），
    # 与 colon 标签 --> B : label 不同（后者不加引号），此处不检测。

    # colon 箭头标签引号检查：--> : "label" 或 --> B : "label"
    # 仅检测 : 后紧跟引号的情况（不含 pipe 标签场景 |...|）
    colon_label_pat = re.compile(
        r"^(\s*.+?(?:-->|==>|-\.->|<-->|<==>|--|==|-\.)\s*.*?:\s*)(['\"])(.+)\2\s*$",
        re.MULTILINE,
    )
    for m in colon_label_pat.finditer(block_text):
        prefix = m.group(1)
        # 排除 pipe 标签行（含 |...| 的行）
        if "|" in prefix:
            continue
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        inner = m.group(3)
        issues.append(_make_issue(
            start_line, lb, ISSUE_ERROR, "FC-COLON-LABEL-QUOTED",
            f"流程图冒号标签不应加引号，改为「: {inner}」",
            "flowchart", snippet,
        ))

    return issues


def _check_state_diagram(block_text: str, start_line: int) -> List[Issue]:
    """stateDiagram-v2 检查 —— 重点检测 #1 反模式：state ID : "描述"。"""
    issues = []
    diagram_type = "stateDiagram"

    # ❌ state ID : "描述" —— #1 反模式！冒号后描述加引号导致 Parse error
    state_desc_quoted = re.compile(
        r"^(\s*state\s+\S+\s*:\s*)(['\"])(.+)\2\s*$",
        re.MULTILINE,
    )
    for m in state_desc_quoted.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        issues.append(_make_issue(
            start_line, lb, ISSUE_ERROR, "SD-STATE-DESC-QUOTED",
            f"state 描述不应加引号（#1反模式，会触发Expecting 'AS'错误），改为「state ... : {m.group(3)}」",
            diagram_type, snippet,
        ))

    # 转换标签引号：--> : "事件" → --> : 事件
    trans_quoted = re.compile(
        r"^(\s*(?:\"[^\"]*\"|\[[\*]\]|\S+)\s*-->\s*(?:\"[^\"]*\"|\[[\*]\]|\S+)\s*:\s*)(['\"])(.+)\2\s*$",
        re.MULTILINE,
    )
    for m in trans_quoted.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        issues.append(_make_issue(
            start_line, lb, ISSUE_ERROR, "SD-TRANS-LABEL-QUOTED",
            f"状态转换标签不应加引号，改为「: {m.group(3)}」",
            diagram_type, snippet,
        ))

    # note right/left/over of ID : "文本" → note ... : 文本
    note_quoted = re.compile(
        r"^(\s*note\s+(?:right|left|over)\s+(?:of\s+)?\S+\s*:\s*)(['\"])(.+)\2\s*$",
        re.MULTILINE,
    )
    for m in note_quoted.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        issues.append(_make_issue(
            start_line, lb, ISSUE_ERROR, "SD-NOTE-QUOTED",
            f"note 文本不应加引号，改为「: {m.group(3)}」",
            diagram_type, snippet,
        ))

    return issues


def _check_class_diagram(block_text: str, start_line: int) -> List[Issue]:
    issues = []
    diagram_type = "classDiagram"

    # ❌ class "中文" as ID —— #3 反模式，错误别名语法
    class_as_quoted = re.compile(
        r"^(\s*class\s+)(['\"])([^'\"]+)\2(\s+as\s+)([A-Za-z][A-Za-z0-9_]*)\s*$",
        re.MULTILINE,
    )
    for m in class_as_quoted.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        cname = m.group(3)
        cid = m.group(5)
        issues.append(_make_issue(
            start_line, lb, ISSUE_ERROR, "CD-CLASS-AS-QUOTED",
            f"class 标签语法错误，应为「class {cid}[\"{cname}\"]」，不要用「class \"中文\" as ID」格式",
            diagram_type, snippet,
        ))

    # ❌ <<Interface>> —— #4 反模式，注解必须全小写
    interface_upper = re.compile(
        r"<<\s*Interface\s*>>",
        re.MULTILINE,
    )
    for m in interface_upper.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        issues.append(_make_issue(
            start_line, lb, ISSUE_ERROR, "CD-INTERFACE-UPPERCASE",
            "类注解(stereotype)必须全小写，将「<<Interface>>」改为「<<interface>>」",
            diagram_type, snippet,
        ))

    # 泛型注解大写检测
    for anno in ("Abstract", "Service", "Repository", "Controller"):
        pat = re.compile(rf"<<\s*{anno}\s*>>")
        for m in pat.finditer(block_text):
            lb = _line_in_block(block_text, m.start())
            snippet = _snippet(m.group(0))
            issues.append(_make_issue(
                start_line, lb, ISSUE_ERROR, "CD-ANNOTATION-UPPERCASE",
                f"类注解应全小写，将「<<{anno}>>」改为「<<{anno.lower()}>>」",
                diagram_type, snippet,
            ))

    # 关系标签引号：<|--|*--|o--|--> 等后 : "标签"
    rel_ops = r"<\|--|\*--|o--|-->|<--|--\*|--o|<\.-|\.->|--"
    rel_label_quoted = re.compile(
        rf"^(\s*[A-Za-z0-9_\"\[\]]+\s*(?:{rel_ops})\s*[A-Za-z0-9_\"\[\]]+\s*:\s*)(['\"])(.+)\2\s*$",
        re.MULTILINE,
    )
    for m in rel_label_quoted.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        issues.append(_make_issue(
            start_line, lb, ISSUE_ERROR, "CD-REL-LABEL-QUOTED",
            f"类关系标签不应加引号，改为「: {m.group(3)}」",
            diagram_type, snippet,
        ))

    return issues


def _check_er_diagram(block_text: str, start_line: int) -> List[Issue]:
    """erDiagram 引号检查：中文实体名加引号；关系标签不加引号；属性块内跳过。"""
    issues = []
    diagram_type = "erDiagram"
    lines = block_text.split("\n")
    brace_depth = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("erdiagram"):
            continue

        # 追踪属性块深度（支持 { 在同行末尾："客户" {）
        # 先计算本行的括号变化
        prev_depth = brace_depth
        brace_depth += stripped.count("{") - stripped.count("}")

        # 如果正在属性块内（且当前行不是 { 开启或 } 关闭行），跳过
        is_open_brace = stripped.endswith("{") and stripped.count("{") > stripped.count("}")
        is_close_brace = stripped == "}" or (stripped.endswith("}") and stripped.count("}") > stripped.count("{"))
        if prev_depth > 0 and not is_close_brace:
            # 在属性块内部的普通行，跳过
            continue
        if is_close_brace and prev_depth <= 1:
            # 闭合括号行本身，跳过
            continue

        # 关系行检查：包含关系操作符和 : 的行
        if "--" in stripped:
            colon_pos = stripped.rfind(":")
            if colon_pos != -1:
                label = stripped[colon_pos + 1:].strip()
                if (label.startswith('"') and label.endswith('"')) or \
                   (label.startswith("'") and label.endswith("'")):
                    inner = label[1:-1]
                    snippet = _snippet(line)
                    issues.append(_make_issue(
                        start_line, i + 1, ISSUE_ERROR, "ER-REL-LABEL-QUOTED",
                        f"ER关系标签不应加引号，改为「: {inner}」",
                        diagram_type, snippet,
                    ))
            # 关系行也可能在 : 前包含中文实体名（无引号）
            rel_part = stripped[:colon_pos] if colon_pos != -1 else stripped
            for token in re.split(r'\s*(?:\|\|--o\{|\|\|--\|\||\}o--o\{|\}o--\|\||\|o--o\{|\|o--\|\||\|\|--\}\||\|o--o\||\|o--\}|\|--o\{|\|--\|\||o--o\{|o--\|\||--o\{|--\|\||--\|o|--o|--)\s*', rel_part):
                token = token.strip().rstrip("{").strip()
                if token and CHINESE_RE.search(token) and not (
                    token.startswith('"') and token.endswith('"')
                ) and not token.startswith("'"):
                    snippet = _snippet(line)
                    issues.append(_make_issue(
                        start_line, i + 1, ISSUE_ERROR, "ER-ENTITY-UNQUOTED",
                        f"中文实体名「{token[:20]}」必须加双引号：\"{token}\"",
                        diagram_type, snippet,
                    ))
            continue

        # 实体声明行（含 { 或独立实体名）
        if is_open_brace or (not is_close_brace and brace_depth == 0 and "--" not in stripped):
            entity_part = stripped.split("{")[0].strip().rstrip().rstrip("{").strip()
            if not entity_part:
                continue
            # 检查是否是中文且未加引号
            if CHINESE_RE.search(entity_part) and not (
                entity_part.startswith('"') and entity_part.endswith('"')
            ):
                snippet = _snippet(line)
                issues.append(_make_issue(
                    start_line, i + 1, ISSUE_ERROR, "ER-ENTITY-UNQUOTED",
                    f"中文实体名「{entity_part[:20]}」必须加双引号：\"{entity_part}\"",
                    diagram_type, snippet,
                ))

    return issues


def _check_gantt(block_text: str, start_line: int) -> List[Issue]:
    issues = []
    issues.extend(_check_title_quotes(block_text, start_line, "gantt"))

    # section 加引号
    section_quoted = re.compile(r"^(\s*section\s+)(['\"])(.+)\2\s*$", re.MULTILINE)
    for m in section_quoted.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        issues.append(_make_issue(
            start_line, lb, ISSUE_WARNING, "GT-SECTION-QUOTED",
            f"section 不需要引号，改为「section {m.group(3)}」",
            "gantt", snippet,
        ))

    # vert 独立成行（应该作为任务标签）
    vert_standalone = re.compile(r"^\s*vert\s+\S+\s*$", re.MULTILINE)
    for m in vert_standalone.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        date_str = m.group(0).strip().split()[-1]
        issues.append(_make_issue(
            start_line, lb, ISSUE_ERROR, "GT-VERT-STANDALONE",
            f"vert 不能独立成行，应为任务标签格式：「标记线 : vert, v{date_str[-2:]}, {date_str}, 1d」",
            "gantt", snippet,
        ))

    return issues


def _check_pie(block_text: str, start_line: int) -> List[Issue]:
    issues = []
    issues.extend(_check_title_quotes(block_text, start_line, "pie"))

    # pie 数据标签未加引号（中文标签必须加引号）
    # 格式："标签" : 数值
    data_line = re.compile(r"^\s*([^:\n]+?)\s*:\s*(\d+(?:\.\d+)?)\s*$", re.MULTILINE)
    lines = block_text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("pie") or stripped.startswith("title") \
           or stripped.startswith("showData") or stripped.startswith("accTitle") \
           or stripped.startswith("accDescr"):
            continue
        m = data_line.match(stripped)
        if m:
            label = m.group(1).strip()
            if CHINESE_RE.search(label) or " " in label:
                if not (label.startswith('"') and label.endswith('"')):
                    snippet = _snippet(line)
                    issues.append(_make_issue(
                        start_line, i + 1, ISSUE_ERROR, "PIE-DATA-UNQUOTED",
                        f"pie 数据标签「{label[:20]}」含中文/空格，必须加双引号：\"{label}\" : {m.group(2)}",
                        "pie", snippet,
                    ))
    return issues


def _check_quadrant_chart(block_text: str, start_line: int) -> List[Issue]:
    issues = []
    issues.extend(_check_title_quotes(block_text, start_line, "quadrantChart"))

    # quadrantChart: 轴标签/象限名/点名称必须加引号
    lines = block_text.split("\n")
    section = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("quadrantchart"):
            continue
        lower = stripped.lower()
        if lower.startswith("x-axis") or lower.startswith("y-axis"):
            section = "axis"
            # 检查轴标签
            after_axis = stripped.split(" ", 1)[1] if " " in stripped else ""
            if after_axis:
                parts = [p.strip() for p in re.split(r"\s+-->\s+|\s+", after_axis) if p.strip()]
                for part in parts:
                    if CHINESE_RE.search(part) and not (part.startswith('"') and part.endswith('"')):
                        snippet = _snippet(line)
                        issues.append(_make_issue(
                            start_line, i + 1, ISSUE_ERROR, "QC-AXIS-UNQUOTED",
                            f"象限图轴标签「{part[:20]}」含中文，必须加双引号",
                            "quadrantChart", snippet,
                        ))
            continue
        if lower.startswith("quadrant-"):
            section = "quadrant"
            # 象限名在后面
            qname = stripped.split(" ", 1)[1] if " " in stripped else ""
            if qname and CHINESE_RE.search(qname) and not (qname.startswith('"') and qname.endswith('"')):
                snippet = _snippet(line)
                issues.append(_make_issue(
                    start_line, i + 1, ISSUE_ERROR, "QC-QUADRANT-UNQUOTED",
                    f"象限名「{qname[:20]}」含中文，必须加双引号",
                    "quadrantChart", snippet,
                ))
            continue
        # 点名称: "名称": [x, y]
        point_match = re.match(r'^([^:\[\]]+?)\s*:\s*\[\s*[\d.]+\s*,\s*[\d.]+\s*\]\s*$', stripped)
        if point_match:
            pname = point_match.group(1).strip()
            if CHINESE_RE.search(pname) or " " in pname:
                if not (pname.startswith('"') and pname.endswith('"')):
                    snippet = _snippet(line)
                    issues.append(_make_issue(
                        start_line, i + 1, ISSUE_ERROR, "QC-POINT-UNQUOTED",
                        f"数据点名称「{pname[:20]}」含中文/空格，必须加双引号：\"{pname}\": [x, y]",
                        "quadrantChart", snippet,
                    ))
    return issues


def _check_requirement_diagram(block_text: str, start_line: int) -> List[Issue]:
    issues = []
    diagram_type = "requirementDiagram"
    lines = block_text.split("\n")

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("requirementdiagram"):
            continue

        # requirement "中文名称" { —— 中文名必须加引号
        req_match = re.match(
            r'^(requirement|functionalRequirement|interfaceRequirement|performanceRequirement|physicalRequirement|designConstraint)\s+([^{]+?)\s*\{?\s*$',
            stripped, re.IGNORECASE,
        )
        if req_match:
            rname = req_match.group(2).strip()
            if CHINESE_RE.search(rname) and not (rname.startswith('"') and rname.endswith('"')):
                snippet = _snippet(line)
                issues.append(_make_issue(
                    start_line, i + 1, ISSUE_ERROR, "REQ-NAME-UNQUOTED",
                    f"需求名称「{rname[:20]}」含中文，必须加双引号",
                    diagram_type, snippet,
                ))
            continue

        # docref → docRef (驼峰)
        if re.search(r'\bdocref\b', stripped, re.IGNORECASE) and not re.search(r'\bdocRef\b', stripped):
            if 'docref' in stripped.lower() and 'docRef' not in stripped:
                snippet = _snippet(line)
                issues.append(_make_issue(
                    start_line, i + 1, ISSUE_ERROR, "REQ-DOCREF-CASE",
                    "应为驼峰命名「docRef」，不是「docref」",
                    diagram_type, snippet,
                ))

        # risk: High → risk: high（枚举值小写）
        risk_match = re.match(r'^risk\s*:\s*(\S+)', stripped)
        if risk_match:
            val = risk_match.group(1).strip().rstrip('.')
            if val not in ("low", "medium", "high"):
                snippet = _snippet(line)
                issues.append(_make_issue(
                    start_line, i + 1, ISSUE_ERROR, "REQ-RISK-CASE",
                    f"risk 枚举值必须小写（low/medium/high），当前「{val}」",
                    diagram_type, snippet,
                ))

        # verifymethod: Test → verifymethod: test
        vm_match = re.match(r'^verifymethod\s*:\s*(\S+)', stripped)
        if vm_match:
            val = vm_match.group(1).strip().rstrip('.')
            valid_vm = ("analysis", "inspection", "test", "demonstration")
            if val.lower() in valid_vm and val != val.lower():
                snippet = _snippet(line)
                issues.append(_make_issue(
                    start_line, i + 1, ISSUE_ERROR, "REQ-VERIFYMETHOD-CASE",
                    f"verifymethod 枚举值必须小写，将「{val}」改为「{val.lower()}」",
                    diagram_type, snippet,
                ))

    return issues


def _check_sankey(block_text: str, start_line: int) -> List[Issue]:
    issues = []
    lines = block_text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("sankey"):
            continue
        # CSV三列格式：源, 目标, 值
        parts = [p.strip() for p in stripped.split(",")]
        if len(parts) >= 3:
            for part in parts[:2]:  # 节点名
                if CHINESE_RE.search(part):
                    snippet = _snippet(line)
                    issues.append(_make_issue(
                        start_line, i + 1, ISSUE_ERROR, "SK-CHINESE-NODE",
                        f"sankey v11.x 不支持中文节点名「{part[:20]}」，请改用英文/拼音",
                        "sankey", snippet,
                    ))
                    break
    return issues


def _check_zenuml(block_text: str, start_line: int) -> List[Issue]:
    issues = []
    diagram_type = "zenuml"
    lines = block_text.split("\n")

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.lower() == "zenuml":
            continue

        # if/while 条件中的中文未加引号
        cond_match = re.match(r'^(if|while|else\s+if)\s*\(([^)]+)\)\s*\{?\s*$', stripped)
        if cond_match:
            cond_text = cond_match.group(2).strip()
            if CHINESE_RE.search(cond_text):
                # 检查是否有引号包裹
                inner = cond_text
                if not ((cond_text.startswith('"') and cond_text.endswith('"')) or
                        (cond_text.startswith("'") and cond_text.endswith("'"))):
                    snippet = _snippet(line)
                    issues.append(_make_issue(
                        start_line, i + 1, ISSUE_ERROR, "ZN-COND-UNQUOTED",
                        f"zenuml 条件中文「{cond_text[:20]}」必须加双引号：{cond_match.group(1)} (\"{cond_text}\")",
                        diagram_type, snippet,
                    ))

        # sync 方法调用中文方法名 A.中文()
        sync_call = re.match(r'^([A-Za-z][A-Za-z0-9_]*)\.([A-Za-z0-9_\u4e00-\u9fff]+)\(\)', stripped)
        if sync_call:
            method_name = sync_call.group(2)
            if CHINESE_RE.search(method_name):
                snippet = _snippet(line)
                issues.append(_make_issue(
                    start_line, i + 1, ISSUE_ERROR, "ZN-SYNC-CHINESE",
                    f"zenuml 同步方法名「{method_name}」不支持中文，请用英文方法名或改用异步箭头语法 A->B: 消息",
                    diagram_type, snippet,
                ))

    return issues


def _check_block_diagram(block_text: str, start_line: int) -> List[Issue]:
    issues = []
    # block 圆角用 A("文本")，不是 A(["文本"])
    stadium_pat = re.compile(
        r'\b([A-Za-z][A-Za-z0-9_]*)\(\["([^\]]*)"\]\)',
        re.MULTILINE,
    )
    for m in stadium_pat.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        issues.append(_make_issue(
            start_line, lb, ISSUE_WARNING, "BLK-STADIUM-SHAPE",
            f"block中「([\"...\"])」是体育场形，如需圆角应为「{m.group(1)}(\"{m.group(2)}\")」（圆括号）",
            "block", snippet,
        ))
    return issues


def _check_journey_timeline(block_text: str, start_line: int, diagram_type: str) -> List[Issue]:
    """journey 和 timeline 的通用检查：title/section 无引号。"""
    issues = []
    issues.extend(_check_title_quotes(block_text, start_line, diagram_type))

    section_kw = "section"
    section_quoted = re.compile(rf"^(\s*{section_kw}\s+)(['\"])(.+)\2\s*$", re.MULTILINE)
    for m in section_quoted.finditer(block_text):
        lb = _line_in_block(block_text, m.start())
        snippet = _snippet(m.group(0))
        issues.append(_make_issue(
            start_line, lb, ISSUE_WARNING, f"{diagram_type.upper()}-SECTION-QUOTED",
            f"section 不需要引号，改为「section {m.group(3)}」",
            diagram_type, snippet,
        ))
    return issues


# ── 检查器调度表 ─────────────────────────────────────────────

CHECKER_MAP = {
    "flowchart": _check_flowchart,
    "stateDiagram": _check_state_diagram,
    "classDiagram": _check_class_diagram,
    "erDiagram": _check_er_diagram,
    "gantt": _check_gantt,
    "pie": _check_pie,
    "quadrantChart": _check_quadrant_chart,
    "requirementDiagram": _check_requirement_diagram,
    "sankey": _check_sankey,
    "zenuml": _check_zenuml,
    "block": _check_block_diagram,
    "journey": lambda b, s: _check_journey_timeline(b, s, "journey"),
    "timeline": lambda b, s: _check_journey_timeline(b, s, "timeline"),
    # sequenceDiagram / mindmap / gitGraph / C4 / xychart-beta: 基础title检查即可
    "sequenceDiagram": lambda b, s: _check_title_quotes(b, s, "sequenceDiagram"),
    "mindmap": lambda b, s: [],
    "gitGraph": lambda b, s: [],
    "C4": lambda b, s: _check_title_quotes(b, s, "C4"),
    "xychart-beta": lambda b, s: _check_title_quotes(b, s, "xychart-beta"),
}


def check_mermaid_block(block_text: str, start_line: int) -> BlockResult:
    """检查单个 Mermaid 代码块，返回检测结果。"""
    diagram_type = detect_diagram_type(block_text)
    result = BlockResult(
        file_path="",
        start_line=start_line,
        diagram_type=diagram_type,
        issues=[],
    )
    checker = CHECKER_MAP.get(diagram_type)
    if checker:
        result.issues = checker(block_text, start_line)
    return result


def scan_file(file_path: Path) -> List[BlockResult]:
    """扫描单个 Markdown 文件中的所有 Mermaid 代码块。"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    results = []
    for m in MERMAID_FENCE_RE.finditer(content):
        block_text = m.group(2)
        # 计算代码块在文件中的起始行号
        start_off = m.start(2)
        start_line = content[:start_off].count("\n") + 1
        result = check_mermaid_block(block_text, start_line)
        result.file_path = str(file_path)
        results.append(result)
    return results


def collect_md_files(paths: List[Path]) -> List[Path]:
    """收集所有需要检查的 Markdown 文件。"""
    files = []
    for p in paths:
        if p.is_file() and p.suffix.lower() in (".md", ".markdown"):
            files.append(p.resolve())
        elif p.is_dir():
            for md in p.rglob("*.md"):
                # 排除 .git / node_modules / vendor 等目录
                parts = set(md.parts)
                if any(skip in parts for skip in (".git", "node_modules", "__pycache__", ".venv")):
                    continue
                files.append(md.resolve())
    return sorted(set(files))


# ── CLI 入口 ─────────────────────────────────────────────────

def main():
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description="Mermaid 引号语法检查器 — 自动检测 Markdown 文档中 Mermaid 代码块的引号使用错误",
    )
    add_common_args(parser)
    parser.add_argument(
        "targets", nargs="*", type=Path,
        help="要检查的文件或目录（默认为当前目录）",
    )
    parser.add_argument(
        "--rule", type=str, default=None,
        help="只检查指定规则ID（如 SD-STATE-DESC-QUOTED）",
    )
    args = parser.parse_args()

    targets = args.targets if args.targets else [Path(".")]
    if args.path:
        targets.append(args.path)

    md_files = collect_md_files(targets)

    if not args.json:
        print_header("Mermaid 引号语法检查器")
        print(f"  扫描目录: {', '.join(str(t.resolve()) for t in targets)}")
        print(f"  文件总数: {len(md_files)}")
        print()

    all_results: List[dict] = []
    total_errors = 0
    total_warnings = 0
    files_with_issues = 0

    for md in md_files:
        block_results = scan_file(md)
        file_issues = []
        for br in block_results:
            for issue in br.issues:
                if args.rule and issue.rule_id != args.rule:
                    continue
                file_issues.append((br, issue))

        if not file_issues:
            continue

        files_with_issues += 1
        rel = md.relative_to(Path.cwd()).as_posix() if md.is_relative_to(Path.cwd()) else str(md)

        if args.json:
            file_entry = {
                "file": str(md),
                "issues": [
                    {
                        **issue.to_dict(),
                        "block_start_line": br.start_line,
                    }
                    for br, issue in file_issues
                ],
            }
            all_results.append(file_entry)
        else:
            print(f"[{ANSI_CYAN}文件{ANSI_RESET}] {rel}")
            for br, issue in sorted(file_issues, key=lambda x: x[1].line):
                color = ANSI_RED if issue.level == ISSUE_ERROR else ANSI_YELLOW
                icon = "[错误]" if issue.level == ISSUE_ERROR else "[警告]"
                print(f"  {color}{icon} L{issue.line}{ANSI_RESET} [{issue.rule_id}] {issue.message}")
                if issue.snippet:
                    print(f"         {ANSI_CYAN}→{ANSI_RESET} {issue.snippet}")
                if issue.level == ISSUE_ERROR:
                    total_errors += 1
                else:
                    total_warnings += 1
            print()

    if not args.json:
        print_summary(
            pass_count=len(md_files) - files_with_issues,
            warn_count=total_warnings,
            error_count=total_errors,
        )
        if total_errors > 0:
            print(f"\n{ANSI_RED}发现 {total_errors} 个错误，请修复后再提交。{ANSI_RESET}")
            return 1
        if total_warnings > 0:
            print(f"\n{ANSI_YELLOW}发现 {total_warnings} 个警告，建议检查。{ANSI_RESET}")
            return 0
        print(f"\n{ANSI_GREEN}所有 Mermaid 代码块引号检查通过！{ANSI_RESET}")
        return 0
    else:
        output = {
            "total_files": len(md_files),
            "files_with_issues": files_with_issues,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "results": all_results,
        }
        json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
