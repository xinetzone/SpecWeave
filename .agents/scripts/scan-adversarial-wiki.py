#!/usr/bin/env python3
"""扫描wiki知识库中旧版"四大攻击者"定义的使用，分类标记并生成报告。

用法:
    python scan-adversarial-wiki.py                # 仅扫描，生成报告
    python scan-adversarial-wiki.py --apply        # 执行自动替换（机械安全替换）
    python scan-adversarial-wiki.py --wiki PATH    # 指定wiki目录

分类规则:
    - auto_replace: 纯描述性文本，可机械替换（"四大"→"五大"等）
    - structural:  表格/列表等结构变更，需人工调整（角色表从4行扩5行）
    - manual_review: 实战案例/历史记录，需人工保留历史准确性
    - skip:        不处理（生成产物.html/.toml等）
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# 常量定义
# ---------------------------------------------------------------------------

WIKI_DEFAULT = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "knowledge"
    / "learning"
    / "02-agent-engineering-methodology"
    / "adversarial-review-wiki"
)

# 需要检测的旧版关键词
LEGACY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("四大攻击者", re.compile(r"四大攻击者")),
    ("性能攻击者", re.compile(r"性能攻击者")),
    ("Performance Attacker", re.compile(r"Performance Attacker", re.IGNORECASE)),
    ("performance(参数值)", re.compile(r"`performance`")),
    ("四个攻击者", re.compile(r"四个攻击者")),
    ("四类攻击者", re.compile(r"四类攻击者")),
    ("四大角色", re.compile(r"四大角色")),
]

# 永远跳过的文件（生成产物/非Markdown）
SKIP_FILES = {
    "knowledge-graph.html",
    "knowledge-graph-config.toml",
    "_scan_report.md",
}

# 整文件为manual_review（实战案例/历史日志）
MANUAL_REVIEW_FILES = {
    "08-practice-cases.md",
}

# manual_review段落关键词（行内出现即标记为需人工复核）
MANUAL_REVIEW_CONTEXT = re.compile(
    r"(发现|案例|实战|历史|CVE|AIHOT|微软|红队|审查日志|验证记录|"
    r"经验教训|问题\d+|攻击者分组|发现角色|联合发现)"
)

# auto_replace上下文关键词（纯描述性文本）
AUTO_REPLACE_CONTEXT = re.compile(
    r"(定义|框架|流程|步骤|清单|模板|Prompt|速查|术语|概念|"
    r"方法论|机制|核心|概述|索引|认知偏差|检查清单|角色详解|"
    r"角色定义|角色速查|角色检查|参数|scope|attacker)"
)

# 表格行模式（| ... | 格式）
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")

# Markdown标题模式
HEADING = re.compile(r"^(#{1,6})\s+(.+)$")


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

Category = Literal["auto_replace", "structural", "manual_review", "skip"]


@dataclass
class Match:
    """单个匹配项。"""
    line_no: int
    line_text: str
    pattern_name: str
    category: Category
    reason: str
    in_table: bool = False
    in_heading: bool = False
    heading_path: str = ""  # 当前所在标题路径


@dataclass
class FileResult:
    """单个文件的扫描结果。"""
    path: Path
    rel_path: str
    matches: list[Match] = field(default_factory=list)

    @property
    def stats(self) -> dict[Category, int]:
        s: dict[Category, int] = {"auto_replace": 0, "structural": 0, "manual_review": 0, "skip": 0}
        for m in self.matches:
            s[m.category] += 1
        return s


@dataclass
class ScanResult:
    """整体扫描结果。"""
    wiki_dir: Path
    files: list[FileResult] = field(default_factory=list)

    @property
    def total_matches(self) -> int:
        return sum(len(f.matches) for f in self.files)

    @property
    def total_stats(self) -> dict[Category, int]:
        s: dict[Category, int] = {"auto_replace": 0, "structural": 0, "manual_review": 0, "skip": 0}
        for f in self.files:
            for cat, cnt in f.stats.items():
                s[cat] += cnt
        return s


# ---------------------------------------------------------------------------
# 分类逻辑
# ---------------------------------------------------------------------------

def classify_line(
    line: str,
    line_no: int,
    file_name: str,
    current_heading: str,
    in_table: bool,
    in_case_section: bool,
) -> tuple[Category, str]:
    """对单行进行分类。"""
    if file_name in SKIP_FILES:
        return "skip", "生成产物/配置文件，跳过"

    # 整文件为manual_review的特殊文件
    if file_name in MANUAL_REVIEW_FILES:
        return "manual_review", "实战案例文件，历史记录需保留准确性"

    # 检查是否在案例/实战段落下
    if in_case_section:
        return "manual_review", f"位于实战/历史段落（{current_heading}）"

    # 检查行内上下文关键词
    if MANUAL_REVIEW_CONTEXT.search(line):
        # 但如果同时在定义性标题下且是简单文本替换（如"四大攻击者"在非案例语境），仍可auto
        if "四大攻击者" in line and not TABLE_ROW.match(line):
            # 检查是否是"四大攻击者角色定义"等纯描述性标题/段落
            if AUTO_REPLACE_CONTEXT.search(line) or "定义" in current_heading or "框架" in current_heading:
                pass  # 继续判断
            else:
                return "manual_review", f"行内包含实战/发现上下文（{MANUAL_REVIEW_CONTEXT.search(line).group()[:10]}...）"

    # 表格行
    if in_table or TABLE_ROW.match(line):
        # 角色定义表格需要结构调整（4行变5行）
        if any(kw in line for kw in ["🟡", "性能", "🔴", "安全", "🟢", "边界", "🔵", "时序", "🟣", "模糊"]):
            # 检查是否是攻击者角色表
            if "攻击" in line or "Attacker" in line or "角色" in current_heading:
                return "structural", "攻击者角色表，需从4行扩展为5行（新增integrity/fuzzer）"
        # 一般表格中的"四大攻击者"描述可替换
        if "四大攻击者" in line or "四大角色" in line:
            return "auto_replace", "表格内描述性文本，可机械替换"
        # 表格中"性能攻击者"出现在"发现角色"列时
        if "性能攻击者" in line and ("发现角色" in line or "发现者" in line):
            return "manual_review", "表格中案例记录，描述谁发现了问题"
        if "性能攻击者" in line:
            return "structural", "表格中的角色引用，需检查列上下文"

    # 标题行
    heading_m = HEADING.match(line)
    if heading_m:
        title = heading_m.group(2)
        if "实战" in title or "案例" in title or "问题" in title and re.search(r"问题\d+", title):
            return "manual_review", f"案例/问题标题: {title[:30]}"
        if "四大攻击者" in line or "四大角色" in line:
            return "auto_replace", "标题文本，'四大'→'五大'"
        if "性能攻击者" in line and ("角色" in title or "详解" in title or "检查清单" in title):
            return "structural", f"角色相关标题，需调整为完整性+模糊测试: {title[:30]}"

    # 简单机械替换：四大→五大
    if "四大攻击者" in line or "四大角色" in line or "四个攻击者" in line or "四类攻击者" in line:
        return "auto_replace", "数量描述'四大/四个/四类'，可替换为'五大/五个/五类'"

    # 性能攻击者在定义性/描述性语境中
    if "性能攻击者" in line:
        # 检查是否是方法论/定义段落
        if AUTO_REPLACE_CONTEXT.search(line) or any(
            kw in current_heading for kw in ["定义", "框架", "流程", "角色", "清单", "术语", "速查", "机制"]
        ):
            return "structural", "描述角色定义/清单的文本，需替换为完整性攻击者+补充模糊测试者"
        return "manual_review", "非定义语境中的性能攻击者引用，需人工判断是否为案例描述"

    if "`performance`" in line:
        return "auto_replace", "参数值，可替换为`integrity`并新增`fuzzer`"

    if "Performance Attacker" in line:
        return "auto_replace", "英文术语，可替换为Integrity Attacker并补充Fuzzer"

    return "manual_review", "未明确分类，默认人工复核"


# ---------------------------------------------------------------------------
# 扫描逻辑
# ---------------------------------------------------------------------------

def is_case_heading(title: str) -> bool:
    """判断标题是否进入案例/实战段落。"""
    return bool(
        re.search(r"实战|案例|经验教训|问题\s*\d+|发现的问题|CVE|AIHOT|微软|泄露|红队测试", title)
    )


def is_exit_case_heading(title: str, level: int, case_level: int) -> bool:
    """判断是否退出案例段落（同级或更高级标题且非案例标题）。"""
    return level <= case_level and not is_case_heading(title)


def scan_file(path: Path, wiki_dir: Path) -> FileResult:
    """扫描单个文件。"""
    rel = path.relative_to(wiki_dir)
    result = FileResult(path=path, rel_path=str(rel).replace("\\", "/"))

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ⚠️ 无法读取 {rel}: {e}", file=sys.stderr)
        return result

    lines = text.splitlines()
    heading_stack: list[tuple[int, str]] = []  # (level, title)
    in_case_section = False
    case_section_level = 0
    in_table = False

    for i, line in enumerate(lines, start=1):
        # 更新标题栈
        hm = HEADING.match(line)
        if hm:
            level = len(hm.group(1))
            title = hm.group(2).strip()
            # 弹出同级或更高级的标题
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))

            # 案例段落追踪
            if is_case_heading(title):
                in_case_section = True
                case_section_level = level
            elif in_case_section and is_exit_case_heading(title, level, case_section_level):
                in_case_section = False
                case_section_level = 0

        # 表格追踪
        if TABLE_ROW.match(line):
            in_table = True
        elif line.strip() == "":
            # 空行可能表示表格结束，但不确定，保持保守
            pass
        elif not TABLE_ROW.match(line) and not line.startswith("|"):
            in_table = False

        current_heading = heading_stack[-1][1] if heading_stack else ""
        heading_path = " > ".join(t for _, t in heading_stack[-3:])

        # 匹配所有旧版模式
        for pat_name, pat in LEGACY_PATTERNS:
            if pat.search(line):
                cat, reason = classify_line(
                    line, i, path.name, current_heading, in_table, in_case_section
                )
                result.matches.append(Match(
                    line_no=i,
                    line_text=line.rstrip(),
                    pattern_name=pat_name,
                    category=cat,
                    reason=reason,
                    in_table=in_table,
                    in_heading=bool(hm),
                    heading_path=heading_path,
                ))
                break  # 一行只记录第一个匹配

    return result


def scan_wiki(wiki_dir: Path) -> ScanResult:
    """扫描整个wiki目录。"""
    result = ScanResult(wiki_dir=wiki_dir)
    md_files = sorted(wiki_dir.glob("*.md"))
    for f in md_files:
        if f.name == "README.md" or f.name in SKIP_FILES:
            continue
        fr = scan_file(f, wiki_dir)
        if fr.matches:
            result.files.append(fr)
    return result


# ---------------------------------------------------------------------------
# 自动替换逻辑（--apply模式）
# ---------------------------------------------------------------------------

# 安全的机械替换规则（仅文本替换，不改变结构）
SAFE_REPLACEMENTS: list[tuple[re.Pattern[str], str, str]] = [
    # "四大攻击者" → "五大攻击者"（但不在表格角色行中）
    (re.compile(r"四大攻击者"), "五大攻击者", "四大→五大"),
    (re.compile(r"四大角色"), "五大角色", "四大角色→五大角色"),
    (re.compile(r"四个攻击者"), "五个攻击者", "四个→五个"),
    (re.compile(r"四类攻击者"), "五类攻击者", "四类→五类"),
    # 参数值
    (re.compile(r"`performance`"), "`integrity`", "参数performance→integrity"),
]


def apply_safe_replacements(path: Path, dry_run: bool = False) -> list[str]:
    """对文件执行安全替换，返回变更描述列表。"""
    text = path.read_text(encoding="utf-8")
    changes: list[str] = []
    new_text = text

    for pat, repl, desc in SAFE_REPLACEMENTS:
        matches = pat.findall(new_text)
        if matches:
            new_text = pat.sub(repl, new_text)
            changes.append(f"  {desc}: {len(matches)}处")

    if not dry_run and new_text != text:
        path.write_text(new_text, encoding="utf-8")

    return changes


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------

CATEGORY_LABEL: dict[Category, str] = {
    "auto_replace": "🟢 可自动替换",
    "structural": "🟡 需结构调整",
    "manual_review": "🔴 需人工复核",
    "skip": "⚪ 跳过",
}


def generate_report(result: ScanResult) -> str:
    """生成Markdown格式报告。"""
    lines: list[str] = []
    lines.append("# Wiki知识库旧版攻击者定义扫描报告\n")
    lines.append(f"- **扫描目录**: `{result.wiki_dir}`")
    lines.append(f"- **扫描文件数**: {len(result.files)} 个有匹配")
    lines.append(f"- **总匹配数**: {result.total_matches} 处\n")

    stats = result.total_stats
    lines.append("## 分类统计\n")
    lines.append("| 分类 | 数量 | 说明 |")
    lines.append("|------|------|------|")
    lines.append(f"| 🟢 可自动替换 | {stats['auto_replace']} | 纯文本，可机械替换（四大→五大等） |")
    lines.append(f"| 🟡 需结构调整 | {stats['structural']} | 表格/列表需增行（4角色→5角色） |")
    lines.append(f"| 🔴 需人工复核 | {stats['manual_review']} | 实战案例/历史记录，保留准确性 |")
    lines.append(f"| ⚪ 跳过 | {stats['skip']} | 生成产物，不处理 |")
    lines.append("")

    for fr in result.files:
        lines.append(f"## {fr.rel_path}\n")
        s = fr.stats
        lines.append(
            f"> 🟢{s['auto_replace']} 🟡{s['structural']} 🔴{s['manual_review']} ⚪{s['skip']}\n"
        )
        for m in fr.matches:
            label = CATEGORY_LABEL[m.category]
            context = f" [{m.heading_path[-50:]}]" if m.heading_path else ""
            lines.append(f"- **L{m.line_no}** {label}{context}")
            lines.append(f"  - 模式: `{m.pattern_name}`")
            lines.append(f"  - 原因: {m.reason}")
            # 截断显示
            display = m.line_text.strip()
            if len(display) > 100:
                display = display[:97] + "..."
            lines.append(f"  - 内容: `{display}`")
            lines.append("")

    lines.append("## 建议处理顺序\n")
    lines.append("1. **先执行 `--apply` 自动替换** 🟢：处理纯文本机械替换")
    lines.append("2. **手动处理结构调整** 🟡：更新角色定义表（4行→5行）、角色详解章节、检查清单、术语表")
    lines.append("3. **人工复核历史案例** 🔴：在AIHOT等实战案例中添加角色演变注记，保留历史描述的准确性")
    lines.append("4. **同步配置文件**：更新 knowledge-graph-config.toml 并重新生成 knowledge-graph.html")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI主入口
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="扫描wiki知识库中旧版四大攻击者定义并分类标记",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--wiki",
        type=Path,
        default=WIKI_DEFAULT,
        help=f"wiki目录路径（默认: {WIKI_DEFAULT}）",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="执行安全的机械替换（默认仅扫描）",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="报告输出路径（默认: wiki目录/_scan_report.md）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="与--apply配合，显示将做的替换但不写入",
    )
    args = parser.parse_args()

    wiki_dir: Path = args.wiki.resolve()
    if not wiki_dir.is_dir():
        print(f"❌ wiki目录不存在: {wiki_dir}", file=sys.stderr)
        return 1

    print(f"🔍 扫描目录: {wiki_dir}\n")

    # 扫描
    result = scan_wiki(wiki_dir)
    print(f"📊 发现 {result.total_matches} 处匹配，分布在 {len(result.files)} 个文件中:")
    for cat, cnt in result.total_stats.items():
        if cnt:
            print(f"   {CATEGORY_LABEL[cat]}: {cnt}")
    print()

    # 执行自动替换
    if args.apply:
        print("🔧 执行自动替换...")
        for fr in result.files:
            auto_matches = [m for m in fr.matches if m.category == "auto_replace"]
            if not auto_matches:
                continue
            changes = apply_safe_replacements(fr.path, dry_run=args.dry_run)
            if changes:
                print(f"\n📝 {fr.rel_path}:")
                for c in changes:
                    print(c)
        print("\n✅ 自动替换完成（机械替换部分）")
        if args.dry_run:
            print("   （dry-run模式，未实际写入文件）")
        print()
        # 重新扫描以更新结果
        result = scan_wiki(wiki_dir)

    # 生成报告
    report_path = args.report or (wiki_dir / "_scan_report.md")
    report = generate_report(result)
    report_path.write_text(report, encoding="utf-8")
    print(f"📄 详细报告已写入: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
