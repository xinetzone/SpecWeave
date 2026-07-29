"""PowerShell 语法分析工具库。

提供字符串/注释感知的代码字符迭代、括号深度追踪、注释处理等底层原语，
供 check-pwsh7-compliance.py、migrate-to-pwsh7.py 等工具复用。

设计原则：
- 所有函数均为无状态纯函数，便于测试和组合
- 正确处理：行注释(#)、注释块(<# #>)、单引号字符串('')、双引号字符串("")、反引号转义(`)
- 完整支持双引号 here-string (@" ... "@) 和单引号 here-string (@' ... '@)

调试日志：设置环境变量 PS1_SYNTAX_DEBUG=1 启用详细调试输出。
"""

from __future__ import annotations


# 版本校验：相对导入共享库（depth=0）
from .python310_version_check import enforce_python310

enforce_python310()

import logging
import os
import re
import sys

# ── 调试日志配置 ─────────────────────────────────────────────────────────────
# 环境变量 PS1_SYNTAX_DEBUG=1 启用调试日志
_debug_enabled = os.environ.get("PS1_SYNTAX_DEBUG") == "1"
_logger = logging.getLogger("ps1_syntax")
if _debug_enabled and not _logger.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setFormatter(logging.Formatter("[PS1_SYNTAX] %(levelname)s %(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.DEBUG)


def _trace(msg: str) -> None:
    """输出调试跟踪日志（仅在 PS1_SYNTAX_DEBUG=1 时生效）。"""
    if _debug_enabled:
        _logger.debug(msg)


def _trace_char(pos: int, ch: str, context: str = "") -> None:
    """输出字符级调试信息。"""
    if _debug_enabled:
        visible = ch if ch not in ('\n', '\r', '\t') else repr(ch)
        ctx = f" [{context}]" if context else ""
        _logger.debug("  pos=%3d ch=%-6s%s", pos, visible, ctx)


def set_debug(enabled: bool) -> None:
    """编程方式启用/禁用调试日志。"""
    global _debug_enabled
    _debug_enabled = enabled
    if enabled:
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.WARNING)


# ── 底层跳过原语 ────────────────────────────────────────────────────────────

def _skip_ps1_here_string(content: str, position: int) -> int:
    """检测当前位置是否为 PowerShell here-string 开头，若是则跳过整个 here-string。

    PowerShell here-string 语法：
    - 双引号 here-string: @"<换行> ... <换行开头>"@  支持反引号 (`) 转义
    - 单引号 here-string: @'<换行> ... <换行开头>'@  完全字面量，不处理转义

    检测规则：
    1. 当前字符必须是 '@'
    2. 下一个字符必须是 '"' 或 "'"
    3. @<quote> 之后必须紧跟换行符（可带可选 CR）
    4. 结束标记 <quote>@ 必须在行首位置

    Args:
        content: 要分析的 PowerShell 代码字符串。
        position: 当前扫描位置（0-based）。

    Returns:
        若当前位置是 here-string 开头，返回 here-string 结束标记之后的位置；
        否则返回原 position（表示未跳过任何内容）。
    """
    n = len(content)
    i = position

    # 检测 @' 或 @" 后跟换行符
    if i < n and content[i] == '@' and i + 1 < n and content[i + 1] in ('"', "'"):
        quote_char = content[i + 1]
        j = i + 2
        # 跳过 @<quote> 后可能的 \r
        if j < n and content[j] == '\r':
            j += 1
        # @<quote> 后必须紧跟 \n 才是 here-string
        if j < n and content[j] == '\n':
            _trace(f"  here-string @{quote_char} started at pos={i}")
            i = j + 1  # 跳过换行符
            end_marker = quote_char + '@'
            while i < n:
                # 行首检测：当前位置是文件开头，或前一个字符是 \n
                at_line_start = (i == 0) or (content[i - 1] == '\n')
                if at_line_start and content[i:i + 2] == end_marker:
                    i += 2
                    _trace(f"  here-string {end_marker} ended at pos={i}")
                    break
                # 双引号 here-string 支持反引号转义
                if quote_char == '"' and content[i] == '`' and i + 1 < n:
                    i += 2
                    continue
                i += 1
            return i

    # 不是 here-string 开头，返回原位置
    return position


# ── 核心迭代器 ──────────────────────────────────────────────────────────────

def iter_code_chars(s: str, start: int = 0):
    """迭代字符串中的代码字符，跳过字符串和注释内容。

    Yields:
        (index, char) 元组，仅对代码部分（字符串/注释外的字符）。
        用于正确追踪括号深度，避免字符串/注释中的 {}() 干扰结构分析。

    正确处理：
    - 行注释 # 到行尾
    - 注释块 <# ... #>（支持嵌套）
    - 单引号字符串 '...'（含 '' 转义）
    - 双引号字符串 "..."（含反引号 ` 转义）
    - 双引号 here-string @" ... "@（含反引号转义）
    - 单引号 here-string @' ... '@（完全字面量）
    """
    _trace(f"iter_code_chars: start={start}, len={len(s)}")
    i = start
    n = len(s)
    while i < n:
        ch = s[i]

        # ── Here-string @' ... '@ 或 @" ... "@ ──
        new_i = _skip_ps1_here_string(s, i)
        if new_i != i:
            i = new_i
            continue

        # ── 注释块 <# ... #> ──
        if ch == '<' and i + 1 < n and s[i + 1] == '#':
            depth = 1
            _trace(f"  comment block <# started at pos={i}")
            i += 2
            while i < n and depth > 0:
                if s[i:i + 2] == '<#':
                    depth += 1
                    _trace(f"    nested <# at pos={i}, depth={depth}")
                    i += 2
                elif s[i:i + 2] == '#>':
                    depth -= 1
                    _trace(f"    #> at pos={i}, depth={depth}")
                    i += 2
                else:
                    i += 1
            _trace(f"  comment block ended at pos={i}")
            continue

        # ── 行注释 #...（非 #! shebang 和非 <# 注释块开头）──
        if ch == '#':
            comment_start = i
            while i < n and s[i] != '\n':
                i += 1
            _trace(f"  line comment skipped pos={comment_start}-{i}")
            continue

        # ── 单引号字符串 '...' ──
        if ch == "'":
            str_start = i
            i += 1
            while i < n:
                if s[i] == "'":
                    # '' 是单引号字符串中的转义
                    if i + 1 < n and s[i + 1] == "'":
                        _trace(f"    escaped '' at pos={i}")
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            _trace(f"  single-quoted string skipped pos={str_start}-{i}")
            continue

        # ── 双引号字符串 "..." ──
        if ch == '"':
            str_start = i
            i += 1
            while i < n:
                if s[i] == '`' and i + 1 < n:
                    # 反引号转义，跳过下一个字符
                    _trace(f"    backtick escape at pos={i}")
                    i += 2
                    continue
                if s[i] == '"':
                    i += 1
                    break
                i += 1
            _trace(f"  double-quoted string skipped pos={str_start}-{i}")
            continue

        yield i, ch
        i += 1


def iter_code_chars_no_comments(s: str, start: int = 0):
    """迭代代码字符（仅跳过字符串，不跳过注释）。

    适用于已经在逐行处理、注释已单独处理的场景。
    Yields: (index, char)
    """
    _trace(f"iter_code_chars_no_comments: start={start}")
    i = start
    n = len(s)
    in_single = False
    in_double = False
    while i < n:
        ch = s[i]
        if in_single:
            if ch == "'":
                if i + 1 < n and s[i + 1] == "'":
                    i += 2
                    continue
                in_single = False
                _trace(f"  single-quote closed at pos={i}")
            i += 1
            continue
        if in_double:
            if ch == '`' and i + 1 < n:
                i += 2
                continue
            if ch == '"':
                in_double = False
                _trace(f"  double-quote closed at pos={i}")
            i += 1
            continue
        if ch == "'":
            in_single = True
            i += 1
            continue
        if ch == '"':
            in_double = True
            i += 1
            continue
        yield i, ch
        i += 1


# ── 空白和注释跳过 ──────────────────────────────────────────────────────────

def find_non_whitespace(s: str, start: int = 0) -> int:
    """返回 start 之后第一个非空白字符的位置。"""
    i = start
    while i < len(s) and s[i] in ' \t\r\n':
        i += 1
    _trace(f"find_non_whitespace: start={start} -> {i}")
    return i


def skip_line_comments(s: str, start: int) -> int:
    """跳过连续的行注释和空行，返回下一个有意义代码的位置。

    注意：不会跳过 #Requires 行（它是有意义的声明）。
    """
    _trace(f"skip_line_comments: start={start}")
    i = start
    while i < len(s):
        i = find_non_whitespace(s, i)
        if i >= len(s):
            _trace(f"  reached end of string at pos={i}")
            break
        # 空行
        if s[i] == '\n':
            _trace(f"  blank line at pos={i}")
            i += 1
            continue
        # 行注释（但不是 #Requires）
        if s[i] == '#' and (i + 1 >= len(s) or s[i + 1] != '<'):
            if i + 8 < len(s) and s[i:i + 9].lower() == '#requires':
                _trace(f"  #Requires found at pos={i}, stopping")
                break
            comment_start = i
            while i < len(s) and s[i] != '\n':
                i += 1
            _trace(f"  line comment skipped pos={comment_start}-{i}")
            continue
        # 注释块 <# ... #>
        if s[i:i + 2] == '<#':
            depth = 1
            cb_start = i
            i += 2
            while i < len(s) and depth > 0:
                if s[i:i + 2] == '<#':
                    depth += 1
                    i += 2
                elif s[i:i + 2] == '#>':
                    depth -= 1
                    i += 2
                else:
                    i += 1
            _trace(f"  comment block skipped pos={cb_start}-{i}")
            continue
        break
    _trace(f"skip_line_comments: result pos={i}, next char={repr(s[i]) if i < len(s) else 'EOF'}")
    return i


def skip_whitespace_and_comments(s: str, start: int = 0) -> int:
    """跳过空白和注释，返回下一个代码字符的位置。"""
    result = skip_line_comments(s, find_non_whitespace(s, start))
    _trace(f"skip_whitespace_and_comments: start={start} -> {result}")
    return result


# ── 注释块 ─────────────────────────────────────────────────────────────────

def find_comment_block_end(s: str, start: int = 0) -> int:
    """找到 <# 注释块的结束位置（#> 之后的位置）。

    如果 start 位置不是 <#，或找不到匹配的 #>，返回 -1。
    """
    _trace(f"find_comment_block_end: start={start}")
    pos = s.find('<#', start)
    if pos != start:
        # 允许 start 和 <# 之间有空白
        actual_start = find_non_whitespace(s, start)
        if actual_start >= len(s) or s[actual_start:actual_start + 2] != '<#':
            _trace(f"  no comment block found at start={start}")
            return -1
        pos = actual_start

    _trace(f"  comment block starts at pos={pos}")
    depth = 0
    i = pos
    while i < len(s):
        if s[i:i + 2] == '<#':
            depth += 1
            i += 2
        elif s[i:i + 2] == '#>':
            depth -= 1
            i += 2
            if depth == 0:
                _trace(f"  comment block ends at pos={i}")
                return i
        else:
            i += 1
    _trace(f"  WARNING: unclosed comment block starting at pos={pos}")
    return -1


# ── 括号匹配 ────────────────────────────────────────────────────────────────

def find_matching_close(s: str, open_pos: int, open_ch: str = '{', close_ch: str = '}') -> int:
    """找到与 open_pos 处的开括号匹配的闭括号位置。

    使用 iter_code_chars 正确跳过字符串和注释。
    open_pos 应指向开括号字符本身。
    返回闭括号字符的索引，找不到返回 -1。
    """
    if open_pos >= len(s) or s[open_pos] != open_ch:
        _trace(f"find_matching_close: invalid open_pos={open_pos}, char={repr(s[open_pos]) if open_pos < len(s) else 'EOF'}, expected {repr(open_ch)}")
        return -1

    _trace(f"find_matching_close: open_pos={open_pos}, ch={repr(open_ch)}, looking for {repr(close_ch)}")
    depth = 0
    for idx, ch in iter_code_chars(s, open_pos):
        if ch == open_ch:
            depth += 1
            _trace(f"  open {repr(open_ch)} at pos={idx}, depth={depth}")
        elif ch == close_ch:
            depth -= 1
            _trace(f"  close {repr(close_ch)} at pos={idx}, depth={depth}")
            if depth == 0:
                _trace(f"  match found at pos={idx}")
                return idx
    _trace(f"  WARNING: no matching {repr(close_ch)} found")
    return -1


def find_param_block_end(s: str, search_from: int = 0) -> int:
    """找到 param(...) 块的结束位置（闭括号之后）。

    返回值指向闭括号 ) 之后的位置（跳过尾随空白和换行），找不到返回 -1。
    """
    _trace(f"find_param_block_end: search_from={search_from}")
    param_match = re.search(r'param\s*\(', s[search_from:], re.MULTILINE | re.IGNORECASE)
    if not param_match:
        _trace(f"  no param( found after pos={search_from}")
        return -1
    paren_start = search_from + param_match.start()
    # 找到 ( 的位置
    paren_pos = s.find('(', paren_start)
    if paren_pos == -1:
        _trace(f"  no ( found after param at pos={paren_start}")
        return -1

    _trace(f"  param( at pos={paren_pos}, scanning for matching )")

    # 使用括号深度匹配（不跳过 () 内的字符串，但跳过注释）
    paren_depth = 0
    i = paren_pos
    n = len(s)
    while i < n:
        ch = s[i]
        # Here-string 跳过（@'/@" 开始的 here-string）
        new_i = _skip_ps1_here_string(s, i)
        if new_i != i:
            _trace(f"    here-string skipped pos={i}-{new_i}")
            i = new_i
            continue
        # 简单字符串跳过（param 块内的字符串）
        if ch == "'":
            str_start = i
            i += 1
            while i < n:
                if s[i] == "'":
                    if i + 1 < n and s[i + 1] == "'":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            _trace(f"    string skipped pos={str_start}-{i}")
            continue
        if ch == '"':
            str_start = i
            i += 1
            while i < n:
                if s[i] == '`' and i + 1 < n:
                    i += 2
                    continue
                if s[i] == '"':
                    i += 1
                    break
                i += 1
            _trace(f"    string skipped pos={str_start}-{i}")
            continue
        if ch == '(':
            paren_depth += 1
            _trace(f"    ( at pos={i}, depth={paren_depth}")
        elif ch == ')':
            paren_depth -= 1
            _trace(f"    ) at pos={i}, depth={paren_depth}")
            if paren_depth == 0:
                # 跳过闭括号后的空白和换行
                next_char = i + 1
                while next_char < n and s[next_char] in ' \t':
                    next_char += 1
                if next_char < n and s[next_char] == '\n':
                    next_char += 1
                while next_char < n and s[next_char] in ' \t\r\n':
                    next_char += 1
                _trace(f"  param block ends at pos={next_char}")
                return next_char
        i += 1
    _trace(f"  WARNING: unclosed param block starting at pos={paren_pos}")
    return -1


# ── 行处理 ──────────────────────────────────────────────────────────────────

def strip_line_comment(line: str) -> str:
    """移除 PowerShell 行尾注释，保留字符串内的 #。"""
    _trace(f"strip_line_comment: line={repr(line[:60])}")
    for idx, ch in iter_code_chars_no_comments(line):
        if ch == '#':
            result = line[:idx]
            _trace(f"  comment found at pos={idx}, returning {repr(result[:60])}")
            return result
    _trace(f"  no comment found")
    return line


# ── 顶层代码检测 ────────────────────────────────────────────────────────────

# 函数定义正则（支持含连字符 - 和模块限定符 : 的 PowerShell 函数名）
FUNCTION_DEF_RE = re.compile(r'^\s*function\s+([\w:.-]+)', re.MULTILINE | re.IGNORECASE)

# 脚本级 param 检测：行首（允许空白）的 param(
PARAM_START_RE = re.compile(r'param\s*\(', re.MULTILINE | re.IGNORECASE)


def find_top_level_insert_point(content: str, search_from: int) -> int:
    """在 search_from 之后找到顶层（brace_depth=0）的代码插入点。

    正确识别：
    - 脚本级 param()（顶层 param）→ 返回 param 块结束后的位置
    - 第一个函数定义 → 返回函数定义前的位置
    - 其他顶层语句 → 返回语句起始位置

    这修复了迁移工具将版本校验块错误插入函数体内 param 之后的 bug。
    """
    _trace(f"find_top_level_insert_point: search_from={search_from}, content_len={len(content)}")
    pos = skip_whitespace_and_comments(content, search_from)

    # 检查是否以脚本级 param( 开头
    param_match = PARAM_START_RE.match(content, pos)
    if param_match:
        # 验证这是脚本级 param 而非函数内 param：
        # 检查 pos 之前的 brace_depth 是否为 0
        pre_depth = _calc_brace_depth(content[:pos])
        _trace(f"  param( found at pos={param_match.start()}, pre_depth={pre_depth}")
        if pre_depth == 0:
            _trace(f"  -> this is a script-level param, finding block end")
            param_end = find_param_block_end(content, param_match.start())
            if param_end > 0:
                _trace(f"  -> insert after param block at pos={param_end}")
                return param_end
            else:
                _trace(f"  -> param block end not found, falling through to scan")
        else:
            _trace(f"  -> param is inside a block (depth={pre_depth}), not script-level")

    # 扫描找到第一个顶层代码位置
    brace_depth = _calc_brace_depth(content[:pos]) if pos > 0 else 0
    _trace(f"  starting scan at pos={pos}, initial brace_depth={brace_depth}")
    i = pos
    line_num = content[:pos].count('\n') + 1
    while i < len(content):
        # 行首位置
        line_start = i
        while i < len(content) and content[i] in ' \t':
            i += 1

        # 空行
        if i < len(content) and content[i] == '\n':
            _trace(f"  L{line_num}: blank line at pos={i}")
            i += 1
            line_num += 1
            continue

        # 跳过注释
        old_i = i
        i = skip_line_comments(content, i)
        if i != old_i:
            comment_lines = content[old_i:i].count('\n')
            _trace(f"  L{line_num}: skipped comments/whitespace pos={old_i}->{i} ({comment_lines} lines)")
            line_num += comment_lines
        if i >= len(content):
            _trace(f"  L{line_num}: reached end of content")
            break

        # 如果在顶层，这就是插入点
        if brace_depth == 0:
            line_end = content.find('\n', i)
            if line_end == -1:
                line_end = len(content)
            context = content[line_start:min(line_end, line_start + 80)].replace('\n', '\\n')
            _trace(f"  L{line_num}: -> top-level code found at line_start={line_start}, depth=0")
            _trace(f"    context: \"{context}\"")
            return line_start

        _trace(f"  L{line_num}: not at top level (depth={brace_depth}), scanning line at pos={i}")

        # 扫描到行尾，追踪括号深度
        brace_events = []
        for idx, ch in iter_code_chars(content, i):
            if ch == '{':
                brace_depth += 1
                brace_events.append(f"{{at{idx}->d{brace_depth}")
                _trace(f"    {{ at pos={idx}, depth={brace_depth}")
            elif ch == '}':
                brace_depth -= 1
                brace_events.append(f"}}at{idx}->d{brace_depth}")
                _trace(f"    }} at pos={idx}, depth={brace_depth}")
            if ch == '\n':
                if brace_events:
                    _trace(f"    line end at pos={idx}, events: {', '.join(brace_events)}, final depth={brace_depth}")
                i = idx + 1
                line_num += 1
                break
        else:
            i = len(content)

    _trace(f"  -> end of content at L{line_num}, insert at pos={len(content)}")
    return len(content)


def _calc_brace_depth(s: str) -> int:
    """计算字符串中的括号深度（正数表示有未闭合的 {）。"""
    depth = 0
    for _, ch in iter_code_chars(s):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
    return depth


def validate_brace_balance(lines: list[str]) -> list[tuple[int, str]]:
    """检查 PowerShell 脚本的括号平衡和结构完整性。

    使用 iter_code_chars 在完整内容上单次扫描，正确处理注释块、字符串、
    转义序列等所有语法元素，避免逐行处理时的跨多行状态丢失问题。

    Args:
        lines: 脚本的行列表（1-indexed 错误报告）

    Returns:
        错误列表，每项为 (行号, 错误消息)。行号为 0 表示文件级错误。
    """
    _trace(f"validate_brace_balance: {len(lines)} lines")
    errors: list[tuple[int, str]] = []

    content = '\n'.join(lines)
    n = len(content)
    # 位置→行号映射
    line_starts = [0]
    for line in lines:
        line_starts.append(line_starts[-1] + len(line) + 1)

    def pos_to_line(pos: int) -> int:
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    # ── 构建 code-only 缓冲区（注释/字符串替换为空格），同时计算括号深度 ──
    code_only = [' '] * n
    brace_depth = 0
    brace_depth_at = [0] * (n + 1)  # brace_depth_at[i] = depth before char at pos i

    for idx, ch in iter_code_chars(content):
        code_only[idx] = ch
        brace_depth_at[idx] = brace_depth
        if ch == '{':
            brace_depth += 1
        elif ch == '}':
            brace_depth -= 1
            if brace_depth < 0:
                errors.append((pos_to_line(idx), f"括号不匹配：多余的 }} 在第 {pos_to_line(idx)} 行"))
                _trace(f"  L{pos_to_line(idx)}: ERROR - extra }} at depth {brace_depth}")
                brace_depth = 0

    code_only_str = ''.join(code_only)

    # ── 版本校验函数嵌套检测 ──
    version_func_re = re.compile(
        r'function\s+(Test-Pwsh7(?:Version|Requirement)|Show-Pwsh7(?:Version|Requirement)Error)\b',
        re.IGNORECASE
    )
    func_def_re = re.compile(r'function\s+([\w:.-]+)', re.IGNORECASE)

    for vm in version_func_re.finditer(code_only_str):
        vpos = vm.start()
        vdepth = brace_depth_at[vpos]
        vline = pos_to_line(vpos)
        if vdepth > 0:
            # 找最近的外层函数名
            outer_func = None
            outer_line = 0
            for fm in func_def_re.finditer(code_only_str):
                if fm.start() < vpos:
                    fbrace = code_only_str.find('{', fm.end())
                    if fbrace >= 0 and fbrace < vpos:
                        outer_func = fm.group(1)
                        outer_line = pos_to_line(fm.start())
            errors.append((
                vline,
                f"版本校验函数 '{vm.group(1)}' 被嵌套在函数 "
                f"'{outer_func or '(未知)'}'（L{outer_line}）内部，版本校验块必须位于顶层"
            ))
            _trace(f"  L{vline}: ERROR - version check function nested (depth={vdepth})")

    if brace_depth > 0:
        errors.append((0, f"括号不匹配：文件末尾有 {brace_depth} 个未闭合的 {{"))
        _trace(f"  EOF: ERROR - {brace_depth} unclosed {{")

    _trace(f"validate_brace_balance: {len(errors)} errors found")
    return errors

