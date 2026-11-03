#!/usr/bin/env python3
"""行形态校验：检测「行合并」故障与行首标记残缺。

**为什么需要它**：批量编辑 Markdown 时，编辑工具的 `old_string` 若以换行结尾，
会把下一行的行首一起吞掉，于是「上一行 + 下一行」被拼成一行。这类故障在肉眼
复核时极易漏掉——合并不一定产生语法错误，只会让结构悄悄变形（例如一个三级标题
变成了某个列表项的尾巴，渲染出来仍然「看着正常」）。

**它为什么不按「行首白名单」检查**：最直觉的做法是「合法行首只有 `- ` / `  - `
/ `#` / `|` / `>`」，但这是**白名单式**判据，会把一切非列表正文（散文段落、
YAML frontmatter、代码块内容、缩进续行、表格数据行）判成异常——实测误报数百
条。真信号会被淹没，工具随即失去价值。

**它实际检查什么**（查「结构不变式被破坏」，而不是「形态像不像被吞」）：
1. **围栏代码块不配对**（强）：` ``` ` 围栏数为奇数——吞行会直接破坏围栏配对。
2. **YAML frontmatter 未闭合**（强）：以 `---` 开头却没有配对的结束分隔线。
3. **表格列数不一致**（强）：同一表格块内各行列数必须相同；吞行会把两行挤成
   列数翻倍的一行。这是**机械可判**的结构不变式。
4. **行内标记紧贴中文**（弱，仅 `--verbose`）：行内出现紧贴中日韩字符的结构性
   标记（`这一行是正文- 下一行`）。

   为什么不把它当主判据：`> 5倍`（比较符）、`（url）- 控制台`（破折号）、
   `（- * + 1.）`（举例）与吞行后的 `正文- 条目B` **形态完全相同**，无法区分。
   全仓实测这类形态判据命中 1000+ 条，绝大多数是合法写法——**闸门误报多了就会
   被整体忽略，那时闸门就真的没了**。故只作可选信号，默认不输出。

**按文件类型分层**（避免把代码/配置误当正文）：
- **Markdown 类**（`.md` / `.markdown` / `.mdx` / `.rst`）：执行结构检查。
  掩码：YAML frontmatter、围栏代码块内部、HTML 块、行内代码、行内强调
  （`**粗**` / `*斜*` / `_斜_` / `~~删~~`）、尖括号占位符（`<模块名>`）。
- **Python**（`.py`）：用 `tokenize` 精确掩码字符串、f-string 与注释——docstring
  里的自由文本因此不会误判；但**不做**行内标记/行首标记检查，因为 `|` 是运算符、
  `-1` 是负数，markdown 语义在此不成立。仅在文件无法分词时给出提示。
- 其他文本：只做围栏配对检查。

**用法**：
    python .agents/scripts/check-line-form.py --path docs
    python .agents/scripts/check-line-form.py --path . --exclude playground
    python .agents/scripts/check-line-form.py --file a.md
    # 退出码 0 = 无异常；1 = 有强/中级问题（逐条打印明细）；2 = 用法错误
"""

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR / "lib"))
sys.path.insert(0, str(_SCRIPT_DIR))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import io
import re
import subprocess
import tokenize
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from constants import EXCLUDED_DIRS
from lib.cli import print_error, print_header, print_pass, print_warn

# ── 规则标识 ────────────────────────────────────────────────────────────────
RULE_INLINE_MARKER = "inline-marker"
RULE_INLINE_MARKER_CJK = "inline-marker-cjk"
RULE_FENCE_UNPAIRED = "fence-unpaired"
RULE_FRONTMATTER_UNCLOSED = "frontmatter-unclosed"
RULE_TABLE_COLUMNS = "table-columns"
RULE_MARKER_NO_SPACE = "marker-no-space"
RULE_PY_UNTOKENIZABLE = "python-untokenizable"

# 强信号：结构不变式被破坏，必须报
HARD_RULES = (RULE_FENCE_UNPAIRED, RULE_FRONTMATTER_UNCLOSED, RULE_TABLE_COLUMNS)
# 弱信号：形态可疑但无法与合法写法区分，默认不输出（--verbose 才显示）
VERBOSE_RULES = (RULE_INLINE_MARKER, RULE_INLINE_MARKER_CJK, RULE_MARKER_NO_SPACE)

# ── 文件类型分层 ────────────────────────────────────────────────────────────
MARKDOWN_SUFFIXES = {".md", ".markdown", ".mdx", ".rst"}
PYTHON_SUFFIXES = {".py"}
TEXT_SUFFIXES = {".txt", ".yml", ".yaml"}

# ── 结构性标记指纹 ──────────────────────────────────────────────────────────
# 判据分两级，避免「形态相同但语义不同」的误报：
#
#   强（确定性）：**行首有结构标记 + 行内又出现结构标记** ⇒ 同一行里挤了两个块
#     （`- 条目A- 条目B`、`| a | b || c | d |`）。这正是吞行的确定性指纹。
#
#   中（概率性）：行内标记紧贴**中日韩字符或数字**。
#     吞行时上一行几乎总是以中文收尾；反过来 `A- B`、`2024-01-01` 这类英文
#     区间/日期写法前缀是拉丁字母，不会命中。
#
#   为什么不用「行内任意位置出现标记」：中文技术文档里 `A- B`、`正文-说明`
#   与吞行后的 `正文- 条目B` 形态完全相同，只看形态无法区分。
#   纯英文文档的行合并因此可能漏检——这是有意识的取舍，误报比漏检更危险。
CJK_CHARS = "\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef0-9"
# 行内标记（任意前缀）：标记前紧贴非空白字符，标记后紧跟空白或行尾
#   `->` `<-` `--` `=>` 等因「后面不是空白」天然不命中，无需额外排除
#   `(?<![-*>|])`：标记前若已是同类符号，则属 `--` `||` `**` 这类成对写法，不算
#   **不含有序列表标记 `1.` / `1)`**：标题与正文里「## 10. 概述」极常见。
#   **不含 `+`**：`PowerShell 7+`、`C++`、`A+` 这类写法比 `+ ` 列表常见得多。
INLINE_MARKER_RE = re.compile(r"(?<![-*>|])(?<=[^\s])([-*#>|])(?=\s|$)")
# 行内标记（中文/数字前缀）—— 吞行时上一行几乎总是以中文收尾
INLINE_MARKER_CJK_RE = re.compile(
    rf"(?<![-*>|])(?<=[{CJK_CHARS}])([-*#>|])(?=\s|$)"
)
# 行首结构标记（用于强信号判定）：标题/列表/引用/表格
LINE_START_MARKER_RE = re.compile(r"^\s*(?:#{1,6}|[-*+>]|\d{1,3}[.)])\s|^\s*\|")
# 行首标记序列（掩码用）：把行首的 `#`/`-`/`1.`/`>`/`|` 序列抹成空格，
#   否则 `### 5.1 标题` 里第三个 `#`（后面跟空格）会被当成「行内标记」误报。
#   行首是否有标记改用原始行判定（LINE_START_MARKER_RE），掩码不影响该判定。
LINE_START_MARK_MASK_RE = re.compile(r"^(\s*)(#{1,6}|[-*+]|\d{1,3}[.)]|>|\|)")
# 行首标记缺空格：`-条目` / `###标题`
#   - `(?!\#)`：阻止贪婪回溯，否则 `### 5.1` 会回退成 `##` + `#` 被误判
#   - 只在标记后紧跟**中文**时报：`- 3`（负数）、`1. 项目`（有序列表）等合法写法不误报
#   - **不含 `*` / `_`**：行首 `**加粗**：` 是合法强调，比「缺空格的列表」常见得多
#   - 水平线/表格分隔行由 SEPARATOR_LINE_RE 整体排除
NO_SPACE_MARKER_RE = re.compile(
    r"^\s*(?:#{1,6}(?!#)|[-+>]|\d{1,3}[.)])(?=[\u4e00-\u9fff])"
)
# 分隔行：水平线 `---`、表格分隔行 `|---|---|`、`***`、`===`
#   这些行由符号组成，行内天然含大量标记，必须整体排除
SEPARATOR_LINE_RE = re.compile(r"^\s*[-*_=~|: ]+\s*$")
# 行内代码
#   `[^`\n]*` 而非 `[^`]*`——后者能匹配换行，遇到奇数反引号时会一路吞到很后面，
#   把中间整段（含换行）替换掉，导致掩码后行数塌缩、后续行号与内容全面错位。
INLINE_CODE_RE = re.compile(r"`+[^`\n]*`+")
# 尖括号占位符 / HTML 标签：`<模块名称>`、`<br>`、`<span class="x">`
#   文档模板里大量使用，其闭合尖括号 `>` 前紧贴中文，会被误判成引用标记。
ANGLE_RE = re.compile(r"<[^<>\n]*>")
# 行内强调（成对）：`**粗**` / `*斜*` / `~~删~~`
#   - **不含下划线类**（`_斜_` / `__粗__`）：snake_case 极常见（`build_base_config`），
#     而 `_..._` 匹配会跨过表格列分隔符，把中间的 `|` 一起抹掉 ⇒ 列数算错。
#   - 强调内容**不得含 `|`**：同理，避免抹掉表格列分隔符。
EMPHASIS_RE = re.compile(r"(\*\*[^*\n|]+\*\*|\*[^*\n|]+\*|~~[^~\n|]+~~)")
# YAML frontmatter
FRONTMATTER_RE = re.compile(r"^---\s*$")
# 围栏代码块
FENCE_RE = re.compile(r"^(\s*)(```+|~~~+)(.*)$")
# HTML 块起始
HTML_BLOCK_RE = re.compile(r"^\s*<[A-Za-z!/]")


@dataclass
class Issue:
    """一处形态问题。"""

    path: Path
    lineno: int
    rule: str
    snippet: str
    reason: str


def _mask_span(grid: list[list[str]], row: int, col_start: int, col_end: int) -> None:
    """把 1-based 行 `row` 的 [col_start, col_end) 区段替换为空格（原地）。"""
    if row - 1 >= len(grid):
        return
    line = grid[row - 1]
    for idx in range(col_start, min(col_end, len(line))):
        line[idx] = " "


def mask_python(text: str) -> str | None:
    """用 tokenize 掩码 Python 的字符串 / f-string / 注释。

    返回掩码后的文本；语法错误导致无法分词时返回 None（调用方降级为不掩码，
    并给出一条提示）。
    """
    lines = text.splitlines()
    if not lines:
        return text
    grid = [list(line) for line in lines]
    string_types = {tokenize.STRING}
    for name in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END"):
        code = getattr(tokenize, name, None)
        if code is not None:
            string_types.add(code)
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return None
    for tok in tokens:
        if tok.type in string_types or tok.type == tokenize.COMMENT:
            (srow, scol), (erow, ecol) = tok.start, tok.end
            for row in range(srow, erow + 1):
                start = scol if row == srow else 0
                end = ecol if row == erow else len(grid[row - 1])
                _mask_span(grid, row, start, end)
    return "\n".join("".join(line) for line in grid)


def mask_spans(text: str, pattern: re.Pattern) -> str:
    """把 pattern 命中的区段替换为等长空格。

    命中的换行符**原样保留**——掩码只应改变内容，不应改变行数，否则行号会错位。
    """

    def _blank(match: re.Match) -> str:
        return "".join("\n" if ch == "\n" else " " for ch in match.group(0))

    return pattern.sub(_blank, text)


def strip_frontmatter(lines: list[str]) -> tuple[list[str], int, bool]:
    """剥离 YAML frontmatter。

    返回 (剩余行, frontmatter 行数, 是否闭合)。以 `---` 开头却没有配对的结束
    分隔线时，视为「未闭合」并原样保留全部行——这本身就是一处结构损坏。
    """
    if not lines or not FRONTMATTER_RE.match(lines[0]):
        return lines, 0, True
    for idx in range(1, len(lines)):
        if FRONTMATTER_RE.match(lines[idx]):
            return lines[idx + 1 :], idx + 1, True
    return lines, 0, False


def split_table_columns(raw: str) -> list[str]:
    """按未转义的 `|` 切分表格行列数（`\\|` 视为内容而非分隔符）。"""
    text = raw.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]
    return re.split(r"(?<!\\)\|", text)


# 表格分隔行：`|---|---|` / `| :--- | ---: |`
TABLE_SEP_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
# 表格里塞目录树：`|   |   +-- sidenav-icon/  # 注释` —— 单元格内含未转义竖线，
#   但这是**合法用法**（用表格模拟缩进树），不能按坏表格报。
TREE_CELL_RE = re.compile(r"\+--|\|--|├|└|──|┌")


def check_table_blocks(body: list[str], masked: list[str], issues: list[Issue], offset: int) -> None:
    """检查同一表格块内各行列数是否一致。

    吞行会把相邻两行挤成一行，列数随之翻倍——这是**机械可判**的结构不变式，
    且不依赖「行内标记长什么样」这类无法区分合法写法的形态判断。

    两个细节决定准确率：
    - 切分前必须掩码**行内代码**，否则 `` `a|b` `` 里的竖线会被算成列分隔符；
    - 以**分隔行**为界分表，否则紧邻的两个表格会被混算成一张表的列数不一致。
    """
    idx = 0
    while idx < len(body):
        if not body[idx].strip().startswith("|"):
            idx += 1
            continue
        end = idx
        while end < len(body) and body[end].strip().startswith("|"):
            end += 1
        block = body[idx:end]
        masked_block = masked[idx:end] if len(masked) >= end else block
        if len(block) >= 2:
            # 以分隔行为界切成若干张表
            groups: list[list[int]] = []
            current: list[int] = []
            for offset_in_block, line in enumerate(block):
                if TABLE_SEP_RE.match(line):
                    if current:
                        groups.append(current)
                    current = []
                    continue
                current.append(offset_in_block)
            if current:
                groups.append(current)
            for group in groups:
                if len(group) < 2:
                    continue
                # 目录树塞在单元格里：列数天然不齐，属合法用法，跳过
                if any(TREE_CELL_RE.search(block[pos]) for pos in group):
                    continue
                counts = [
                    len(split_table_columns(masked_block[pos])) for pos in group
                ]
                common = Counter(counts).most_common(1)[0][0]
                # 只报「列数变多」的行：吞行把两行挤成一行，列数随之翻倍；
                # 「列数变少」是漏写列的另一种坏表格，与吞行无关，不在本工具职责内。
                for pos, count in zip(group, counts):
                    if count <= common:
                        continue
                    issues.append(
                        Issue(
                            path=Path("<memory>"),
                            lineno=idx + pos + 1 + offset,
                            rule=RULE_TABLE_COLUMNS,
                            snippet=block[pos].strip()[:80],
                            reason=(
                                f"表格列数多于同表其余行（本行 {count} 列，其余 {common} 列）"
                                "——疑似两行被合并"
                            ),
                        )
                    )
        idx = end


def _fence_state(lines: list[str]) -> tuple[str | None, int]:
    """扫描围栏，返回 (未闭合的围栏标记字符, 其起始行索引)。

    配对规则遵循 CommonMark：
    - 在围栏**外**遇到任何围栏行 ⇒ 开启；
    - 在围栏**内**只有「无 info string」的围栏行才能关闭，且字符相同、长度 ≥ 开启长度。

    两处细节决定准确率：
    - 只比字符不比长度会把「嵌套围栏」（外层四反引号内含三反引号）误判成配对成功；
    - 不区分 info string 会把「```typescript」（开启）当成关闭围栏。
    """
    fence_char: str | None = None
    fence_len = 0
    fence_start = 0
    for idx, line in enumerate(lines):
        fence_match = FENCE_RE.match(line)
        if not fence_match:
            continue
        marker = fence_match.group(2)
        info = fence_match.group(3)
        if fence_char is None:
            fence_char = marker[0]
            fence_len = len(marker)
            fence_start = idx
        elif not info.strip() and marker[0] == fence_char and len(marker) >= fence_len:
            fence_char = None
    return fence_char, fence_start


def _check_fences(lines: list[str], issues: list[Issue], offset: int = 0) -> None:
    """检查围栏配对，把未闭合的围栏记为问题。"""
    fence_char, fence_start = _fence_state(lines)
    if fence_char is not None:
        issues.append(
            Issue(
                path=Path("<memory>"),
                lineno=fence_start + 1 + offset,
                rule=RULE_FENCE_UNPAIRED,
                snippet=lines[fence_start].strip()[:80],
                reason=(
                    f"代码围栏 `{fence_char}` 未闭合（起始于 L{fence_start + 1 + offset}），"
                    "通常意味着某行被吞"
                ),
            )
        )


def scan_markdown(text: str) -> list[Issue]:
    """扫描 Markdown 类文本。

    两套行视图：
    - **原始行**：用于围栏配对与行首标记判定——围栏标记 `` ``` `` 会被行内代码
      掩码规则抹掉，若在掩码行上判定围栏，围栏检测将永远「配对成功」而失效。
    - **掩码行**：用于行内标记判定——行内代码、强调、行首标记序列都已被抹成
      空格，避免把 `` `a-b` ``、`` **加粗** ``、`` ### 标题 `` 误判成结构标记。
    """
    issues: list[Issue] = []
    original = text.splitlines()
    if not original:
        return issues

    body, offset, fm_closed = strip_frontmatter(original)
    if not fm_closed:
        issues.append(
            Issue(
                path=Path("<memory>"),
                lineno=1,
                rule=RULE_FRONTMATTER_UNCLOSED,
                snippet=original[0].strip()[:80] if original else "",
                reason="YAML frontmatter 以 `---` 开头却没有配对的结束分隔线",
            )
        )
    masked_text = mask_spans("\n".join(body), INLINE_CODE_RE)
    masked_text = mask_spans(masked_text, EMPHASIS_RE)
    masked_text = mask_spans(masked_text, ANGLE_RE)
    # 轻量掩码（不抹行首标记）：供表格列数切分使用
    masked_light = masked_text.split("\n")
    masked_lines = [
        LINE_START_MARK_MASK_RE.sub(lambda m: " " * len(m.group(0)), line)
        for line in masked_light
    ]

    _check_fences(body, issues, offset)

    fence_char: str | None = None
    fence_len = 0
    for idx, raw in enumerate(body):
        fence_match = FENCE_RE.match(raw)
        if fence_match:
            marker = fence_match.group(2)
            info = fence_match.group(3)
            if fence_char is None:
                fence_char, fence_len = marker[0], len(marker)
            elif not info.strip() and marker[0] == fence_char and len(marker) >= fence_len:
                fence_char = None
            continue
        if fence_char is not None:
            continue  # 代码块内部不检查
        line = masked_lines[idx] if idx < len(masked_lines) else ""
        if HTML_BLOCK_RE.match(line):
            continue  # HTML 块内的自由文本不检查
        if SEPARATOR_LINE_RE.match(line):
            continue  # 水平线 / 表格分隔行：符号组成，天然含大量标记

        lineno = idx + 1 + offset
        any_match = INLINE_MARKER_RE.search(line)
        cjk_match = INLINE_MARKER_CJK_RE.search(line)
        has_head_marker = LINE_START_MARKER_RE.match(raw) is not None

        if cjk_match:
            marker = cjk_match.group(1)
            issues.append(
                Issue(
                    path=Path("<memory>"),
                    lineno=lineno,
                    rule=RULE_INLINE_MARKER_CJK,
                    snippet=raw.strip()[:80],
                    reason=(
                        f"行内出现紧贴中文的结构性标记「{marker}」——"
                        "疑似上一行与本行被合并（编辑时行首被吞）"
                    ),
                )
            )
        elif any_match and has_head_marker:
            marker = any_match.group(1)
            issues.append(
                Issue(
                    path=Path("<memory>"),
                    lineno=lineno,
                    rule=RULE_INLINE_MARKER,
                    snippet=raw.strip()[:80],
                    reason=(
                        f"行首有结构标记、行内又出现「{marker}」——同一行挤了两个块，"
                        "疑似上一行与本行被合并（编辑时行首被吞）"
                    ),
                )
            )
        elif NO_SPACE_MARKER_RE.match(raw):
            issues.append(
                Issue(
                    path=Path("<memory>"),
                    lineno=lineno,
                    rule=RULE_MARKER_NO_SPACE,
                    snippet=raw.strip()[:80],
                    reason="行首结构性标记后缺少空格",
                )
            )
    check_table_blocks(body, masked_light, issues, offset)
    return issues


def scan_python(text: str) -> list[Issue]:
    """扫描 Python 文件：只提示无法分词（其余靠 tokenize 掩码规避误报）。"""
    issues: list[Issue] = []
    if mask_python(text) is None:
        issues.append(
            Issue(
                path=Path("<memory>"),
                lineno=0,
                rule=RULE_PY_UNTOKENIZABLE,
                snippet="",
                reason="Python 文件无法分词（语法错误），字符串/注释未被掩码",
            )
        )
    return issues


def scan_text(text: str, suffix: str) -> list[Issue]:
    """按文件类型分派扫描。"""
    if suffix in MARKDOWN_SUFFIXES:
        return scan_markdown(text)
    if suffix in PYTHON_SUFFIXES:
        return scan_python(text)
    if suffix in TEXT_SUFFIXES:
        issues: list[Issue] = []
        _check_fences(text.splitlines(), issues)
        return issues
    return []


def scan_file(path: Path) -> list[Issue]:
    """扫描单个文件。"""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        return [Issue(path=path, lineno=0, rule="unreadable", snippet="", reason=str(exc))]
    issues = scan_text(text, path.suffix.lower())
    for issue in issues:
        issue.path = path
    return issues


def _git_ls_files(root: Path, suffixes: set[str], excluded: set[str]) -> list[Path] | None:
    """用 `git ls-files` 列出受版本控制的文件。

    比目录遍历快几个数量级，且口径更准——「受版本控制的文件」正是会被公开出去的
    那些。返回 None 表示 git 不可用或该目录不在仓库内，调用方回退到目录遍历。
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    files: list[Path] = []
    for rel in result.stdout.decode("utf-8", "replace").split("\0"):
        if not rel:
            continue
        rel_path = Path(rel)
        if rel_path.suffix.lower() not in suffixes:
            continue
        if set(rel_path.parts) & excluded:
            continue
        files.append(root / rel_path)
    return files


def collect_files(root: Path, excluded: set[str], use_git: bool = True) -> list[Path]:
    """收集待扫描的文本文件。

    排除判定只针对**相对扫描根**的路径部分——扫描根自身可能是隐藏目录
    （如 `.agents/scripts`），把它一并排除会导致「扫了 0 个文件」。
    """
    suffixes = MARKDOWN_SUFFIXES | PYTHON_SUFFIXES | TEXT_SUFFIXES
    if root.is_file():
        return [root]
    if use_git:
        tracked = _git_ls_files(root, suffixes, excluded)
        if tracked is not None:
            return sorted(tracked)
    found: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        try:
            rel_parts = path.relative_to(root).parts
        except ValueError:
            continue
        if set(rel_parts) & excluded:
            continue
        if any(part.startswith(".") for part in rel_parts[:-1]):
            continue  # 隐藏子目录（如 .git、.venv）
        found.append(path)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="行形态校验：检测行合并故障与行首标记残缺")
    parser.add_argument("--path", default=".", help="扫描根目录或单个文件（默认：当前目录）")
    parser.add_argument("--file", help="扫描单个文件（与 --path 二选一）")
    parser.add_argument(
        "--exclude",
        default="",
        help="额外排除的目录名，逗号分隔（默认额外排除 playground、projects、.temp）",
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="不用 git ls-files，改用目录遍历（用于扫描未纳入版本控制的目录）",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="同时输出弱信号（行内标记、行首缺空格）——形态可疑但无法与合法写法区分",
    )
    args = parser.parse_args()

    excluded = set(EXCLUDED_DIRS) | {"playground", ".temp", ".venv", "site-packages"}
    if args.exclude:
        excluded |= {part.strip() for part in args.exclude.split(",") if part.strip()}

    target = Path(args.file) if args.file else Path(args.path)
    if not target.exists():
        print_error(f"路径不存在：{target}")
        return 2

    files = collect_files(target, excluded, use_git=not args.no_git)
    issues: list[Issue] = []
    for path in files:
        issues.extend(scan_file(path))

    hard = [i for i in issues if i.rule in HARD_RULES]
    weak = [i for i in issues if i.rule in VERBOSE_RULES]
    hints = [i for i in issues if i.rule == RULE_PY_UNTOKENIZABLE]

    print(f"行形态核查：{len(files)} 个文件 / 命中 {len(issues)} 条")
    if hard:
        print_header("问题明细")
        for issue in hard:
            print_error(
                f"{issue.rule}  {issue.path.as_posix()} L{issue.lineno}  {issue.reason}\n"
                f"        └ {issue.snippet}"
            )
    if hints:
        print_header("提示")
        for issue in hints:
            print_warn(f"{issue.rule}  {issue.path.as_posix()}  {issue.reason}")
    if weak and args.verbose:
        print_header("弱信号（--verbose）")
        for issue in weak:
            print_warn(
                f"{issue.rule}  {issue.path.as_posix()} L{issue.lineno}  {issue.reason}\n"
                f"        └ {issue.snippet}"
            )
    if hard or hints:
        print(
            f"\n未通过：问题 {len(hard)} 条 / 提示 {len(hints)} 条 / "
            f"弱信号 {len(weak)} 条{'（已展开）' if args.verbose else '（--verbose 展开）'}"
        )
        return 1
    if weak:
        print(f"\n弱信号 {len(weak)} 条（--verbose 展开）")
        return 0
    print_pass("全部通过：无行合并故障、无行首标记残缺")
    return 0


if __name__ == "__main__":
    sys.exit(main())
