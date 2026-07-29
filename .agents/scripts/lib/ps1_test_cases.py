#!/usr/bin/env python3
"""PS1 语法分析的跨语言共享测试用例定义。

本模块定义了 PowerShell 语法分析（顶层插入点查找、括号深度计算等）的测试用例，
供 Python 端（pytest）和 PowerShell 端（JSON 导出）共享使用。

测试用例分为四类：
  - INSERT_POINT_CASES: 测试 find_top_level_insert_point / Find-Ps1TopLevelInsertPoint
  - BRACE_DEPTH_CASES: 测试 _calc_brace_depth / Get-Ps1BraceDepth
  - INSERT_CODE_CASES: 测试 add 代码插入功能的端到端验证
  - HERE_STRING_CASES: 测试 _skip_ps1_here_string / Skip-Ps1HereString 原语

使用方法：
  Python 端:
    from lib.ps1_test_cases import INSERT_POINT_CASES, BRACE_DEPTH_CASES, INSERT_CODE_CASES, HERE_STRING_CASES

  PowerShell 端:
    python -m lib.ps1_test_cases --export-json  # 导出 JSON 文件
    然后在 PowerShell 中读取 JSON 执行测试
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# ── 测试用例数据结构 ─────────────────────────────────────────────────────────


@dataclass
class InsertPointCase:
    """顶层插入点查找测试用例。"""

    id: str
    name: str
    content: str
    expected_keyword: Optional[str] = None  # 插入点附近应包含的关键词
    expected_min_pos: int = 0  # 插入点不应小于此位置
    search_from: int = 0  # 搜索起始位置（默认从0开始）
    tags: list[str] = field(default_factory=list)  # 标签：here-string, crlf, comment 等


@dataclass
class BraceDepthCase:
    """括号深度计算测试用例。"""

    id: str
    name: str
    content: str
    expected_depth: int
    end_pos: int = -1  # -1 表示计算到字符串末尾


@dataclass
class InsertCodeCase:
    """代码插入端到端测试用例。"""

    id: str
    name: str
    content: str
    code_to_insert: str
    expected_starts_with: Optional[str] = None  # 插入后应以...开头
    expected_contains: Optional[str] = None  # 插入后应包含...
    search_from: int = 0


@dataclass
class HereStringCase:
    """Here-string 跳过原语直接测试用例。"""

    id: str
    name: str
    content: str
    position: int
    expected_new_pos: int


# ── 辅助函数：构建 here-string 内容 ──────────────────────────────────────────


def _hs_double(lines: list[str]) -> str:
    """构建双引号 here-string 内容（@"... "@ 格式）。"""
    return '@"\n' + "\n".join(lines) + '\n"@'


def _hs_single(lines: list[str]) -> str:
    """构建单引号 here-string 内容（@'... '@ 格式）。"""
    return "@'\n" + "\n".join(lines) + "\n'@"


# ── 测试用例定义 ─────────────────────────────────────────────────────────────


INSERT_POINT_CASES: list[InsertPointCase] = [
    InsertPointCase(
        id="param_simple",
        name="1. 简单脚本级 param() - 应在 param 块后插入",
        content="""\
param(
    [string]$Name,
    [int]$Count
)

Write-Host "Hello $Name"
""",
        expected_keyword="Write-Host",
        expected_min_pos=40,
    ),
    InsertPointCase(
        id="func_inner_param",
        name="2. 函数内 param() - 应在 function 前插入",
        content="""\
function Get-Greeting {
    param(
        [string]$Name
    )
    return "Hello $Name"
}

Get-Greeting -Name "World"
""",
        expected_keyword="function",
        tags=["function"],
    ),
    InsertPointCase(
        id="comment_block_param",
        name="3. 头部注释块 + 脚本级 param()",
        content="""\
<#
.SYNOPSIS
    测试脚本
.DESCRIPTION
    这是一个有大注释块的脚本
#>
param(
    [string]$Path
)
Get-ChildItem $Path
""",
        expected_keyword="Get-ChildItem",
        expected_min_pos=80,
        tags=["comment-block"],
    ),
    InsertPointCase(
        id="nested_funcs",
        name="4. 嵌套函数 - 应在第一个 function 前插入",
        content="""\
function Outer {
    param([string]$x)
    function Inner {
        param([int]$y)
        if ($y -gt 0) {
            return $y * 2
        }
        return 0
    }
    return Inner -y $x.Length
}

Outer -x "hello"
""",
        expected_keyword="function Outer",
        tags=["function", "nested"],
    ),
    InsertPointCase(
        id="string_fake_braces",
        name="5. 字符串中的假括号和注释符号",
        content="""\
$msg = "This is { not a real brace } and # not a comment"
Write-Host $msg
$other = 'single quotes { also fake } # fake too'
Write-Host $other
function Test { "nested { brace } in string" }
""",
        expected_keyword="$msg =",
        tags=["string"],
    ),
    InsertPointCase(
        id="requires_with_param",
        name="6. #Requires + 脚本级 param()（从Requires之后搜索）",
        content="""\
#Requires -Version 5.1
param(
    [switch]$Force
)
if ($Force) { Write-Host "Forced" }
""",
        expected_keyword="if (",
        expected_min_pos=40,
        search_from=23,  # #Requires 行之后
        tags=["requires"],
    ),
    InsertPointCase(
        id="line_comment_fakes",
        name="7. 行注释中的假括号",
        content="""\
# This line has { fake } braces and # fake comment starts
# Another { comment } line
Write-Host "real code starts here"
""",
        expected_keyword="Write-Host",
        tags=["comment"],
    ),
    InsertPointCase(
        id="single_line_func",
        name="8. 单行函数 + 后续脚本级代码",
        content="""\
function Say-Hi { Write-Host "Hi" }
Say-Hi
""",
        expected_keyword="function Say-Hi",
        tags=["function"],
    ),
    InsertPointCase(
        id="if_else_toplevel",
        name="9. 脚本级 if/else 控制流（无函数）",
        content="""\
if ($IsWindows) {
    Write-Host "Windows"
} else {
    Write-Host "Other"
}
""",
        expected_keyword="if (",
        tags=["control-flow"],
    ),
    InsertPointCase(
        id="string_escapes",
        name="10. 字符串转义序列（'' 和 `）",
        content="""\
$a = 'don''t worry about { fake } braces'
$b = "hello `"world`" with `$var and { fake }"
Write-Host "$a $b"
""",
        expected_keyword="$a =",
        tags=["string", "escape"],
    ),
    InsertPointCase(
        id="comment_block_fakes",
        name="11. 注释块内包含 param( 和 { 的假信号",
        content="""\
<#
Example code that should NOT be parsed:
function Fake {
    param($x)
    { nested block }
}
#>
Write-Host "Real code"
""",
        expected_keyword="Write-Host",
        tags=["comment-block"],
    ),
    InsertPointCase(
        id="multi_funcs",
        name="12. 多个函数定义",
        content="""\
function Func1 {
    param([string]$a)
    return $a
}
function Func2 {
    param([int]$b)
    return $b * 2
}
Func1 -a "test"
""",
        expected_keyword="function Func1",
        tags=["function"],
    ),
    InsertPointCase(
        id="class_def",
        name="13. PowerShell class 定义",
        content="""\
class MyClass {
    [string]$Name
    MyClass([string]$name) {
        $this.Name = $name
    }
    [string]Greet() {
        return "Hello, $($this.Name)"
    }
}
$obj = [MyClass]::new("World")
""",
        expected_keyword="class MyClass",
        tags=["class"],
    ),
    InsertPointCase(
        id="empty_func_body",
        name="14. 空/简单函数体",
        content="""\
function EmptyFunc {}
function SimpleFunc { "simple" }
Write-Host "Done"
""",
        expected_keyword="function EmptyFunc",
        tags=["function"],
    ),
    InsertPointCase(
        id="try_catch",
        name="15. try/catch/finally 在脚本级",
        content="""\
try {
    $result = 1 / 0
} catch {
    Write-Error $_
} finally {
    Write-Host "cleanup"
}
""",
        expected_keyword="try {",
        tags=["control-flow"],
    ),
    InsertPointCase(
        id="dot_source",
        name="16. dot-source + 脚本级代码",
        content="""\
. "$PSScriptRoot/lib.ps1"
$config = Get-Config
Write-Host $config.Name
""",
        expected_keyword='.',
        tags=["dot-source"],
    ),
    InsertPointCase(
        id="func_special_chars",
        name="17. 函数名含特殊字符（: 和 -）",
        content="""\
function MyModule:Invoke-Task {
    param([string]$TaskName)
    Write-Host "Running $TaskName"
}
MyModule:Invoke-Task -TaskName "build"
""",
        expected_keyword="function MyModule",
        tags=["function"],
    ),
    InsertPointCase(
        id="using_statements",
        name="18. using namespace/module 语句",
        content="""\
using namespace System.Text
using module ./MyModule.psm1
Write-Host "Using loaded"
""",
        expected_keyword="using namespace",
        tags=["using"],
    ),
    # ── Here-string 专项测试 ──
    InsertPointCase(
        id="hs_double_toplevel",
        name="19. 双引号 here-string 在顶层（含假括号）",
        content="$text = " + _hs_double(["Hello {World}", "This is a {test}"]) + "\nWrite-Host $text\n",
        expected_keyword="$text =",
        tags=["here-string", "double-quoted"],
    ),
    InsertPointCase(
        id="hs_single_toplevel",
        name="20. 单引号 here-string 在顶层（含假括号）",
        content="$text = " + _hs_single(["Hello {World}", "No expansion {here}"]) + "\nWrite-Host $text\n",
        expected_keyword="$text =",
        tags=["here-string", "single-quoted"],
    ),
    InsertPointCase(
        id="hs_in_function",
        name="21. here-string 在函数体内（假括号不应干扰）",
        content="function Show-Msg {\n    $msg = " + _hs_double(["    {fake braces} inside here-string", "    should not {confuse} the parser"]) + "\n    Write-Host $msg\n}\nShow-Msg\n",
        expected_keyword="function Show-Msg",
        tags=["here-string", "function"],
    ),
    InsertPointCase(
        id="hs_param_default",
        name="22. param() 默认值为 here-string",
        content="param(\n    [string]$Config = " + _hs_double(["server=localhost", "port=8080"]) + "\n)\nInitialize-App\n",
        expected_keyword="Initialize-App",
        expected_min_pos=60,
        tags=["here-string", "param"],
    ),
    InsertPointCase(
        id="hs_crlf",
        name="23. CRLF 换行的 here-string",
        content="$s = " + _hs_double(["line1", "line2"]).replace("\n", "\r\n") + "\r\nWrite-Host $s\r\n",
        expected_keyword="$s =",
        tags=["here-string", "crlf"],
    ),
    InsertPointCase(
        id="hs_backtick_escape",
        name="24. 双引号 here-string 反引号转义",
        content="$s = " + _hs_double(["hello `\"world`\"", "line with `$var and {brace}"]) + "\nWrite-Host $s\n",
        expected_keyword="$s =",
        tags=["here-string", "escape"],
    ),
    # ── Here-string 极端边界用例 ──
    InsertPointCase(
        id="hs_consecutive",
        name="25. 连续多个 here-string",
        content="$a = " + _hs_double(["first"]) + "\n$b = " + _hs_single(["second"]) + "\n$c = " + _hs_double(["third with {braces}"]) + "\nWrite-Host $a$b$c\n",
        expected_keyword="$a =",
        tags=["here-string", "edge"],
    ),
    InsertPointCase(
        id="hs_indented_end_marker",
        name="26. here-string 结束标记有前导空格（不应关闭）",
        content="$s = " + _hs_double(["line1", "  \"@", "line3"]) + "\nWrite-Host $s\n",
        expected_keyword="$s =",
        tags=["here-string", "edge", "indented-marker"],
    ),
    InsertPointCase(
        id="hs_pseudo_nested",
        name='27. 伪嵌套 here-string（内部@"序列作为内容，缩进的"@不关闭）',
        content="$outer = " + _hs_double(["level1", "  @\"", "  inner", "  \"@", "level1 end"]) + "\nWrite-Host $outer\n",
        expected_keyword="$outer =",
        tags=["here-string", "edge", "nested"],
    ),
    InsertPointCase(
        id="hs_only",
        name="28. 仅包含 here-string 的脚本（无其他代码）",
        content=_hs_double(["only content here"]),
        expected_keyword='@"',
        tags=["here-string", "edge"],
    ),
    InsertPointCase(
        id="hs_mixed_with_regular_strings",
        name="29. here-string 后跟含假括号的普通字符串",
        content="$hs = " + _hs_double(["hs content"]) + "\n$reg = \"normal {fake} string\" + 'also {fake}'\nif ($true) { Write-Host $hs }\n",
        expected_keyword="$hs =",
        tags=["here-string", "edge", "mixed"],
    ),
    InsertPointCase(
        id="hs_backtick_line_continuation",
        name="30. 双引号 here-string 内含反引号转义的@和引号",
        content="$s = " + _hs_double(["line with ``@ and ``\" quotes", "{fake braces}", "end"]) + "\nWrite-Host $s\n",
        expected_keyword="$s =",
        tags=["here-string", "edge", "escape"],
    ),
    InsertPointCase(
        id="hs_triple_pseudo_nested",
        name='31. 三层伪嵌套 here-string（内容中含缩进的@"和"@序列）',
        content="$l1 = " + _hs_double([
            "level1",
            "  @\"",
            "  level2",
            "    @\"",
            "    level3",
            "    \"@",
            "  level2 end",
            "  \"@",
            "level1 end"
        ]) + "\nWrite-Host $l1\n",
        expected_keyword="$l1 =",
        tags=["here-string", "edge", "nested", "triple"],
    ),
    InsertPointCase(
        id="hs_empty_file",
        name="32. 空脚本文件",
        content="",
        expected_keyword=None,
        expected_min_pos=0,
        tags=["edge", "empty"],
    ),
    InsertPointCase(
        id="hs_end_no_newline",
        name="33. here-string 结束标记在文件末尾无换行",
        content="$s = " + _hs_double(["last line"]) + "",  # 末尾无换行
        expected_keyword="$s =",
        tags=["here-string", "edge", "eof"],
    ),
    InsertPointCase(
        id="hs_mid_line_at_quote",
        name="34. 行中@\"序列（非行首起始，不是here-string）",
        content='$s = "normal string with @" sequence inside"\nWrite-Host $s\n',
        expected_keyword='$s =',
        tags=["here-string", "edge", "mid-line"],
    ),
    InsertPointCase(
        id="hs_alternating_single_double",
        name="35. 交替出现单双引号here-string",
        content="$a = " + _hs_double(["double1"]) + "\n$b = " + _hs_single(["single1"]) + "\n$c = " + _hs_double(["double2"]) + "\n$d = " + _hs_single(["single2 with {braces}"]) + "\nWrite-Host $a$b$c$d\n",
        expected_keyword="$a =",
        tags=["here-string", "edge", "alternating"],
    ),
    InsertPointCase(
        id="hs_many_blank_lines",
        name="36. here-string 内含多个连续空行",
        content="$s = " + _hs_double(["line1", "", "", "", "line after blanks", "{fake}", ""]) + "\nWrite-Host $s\n",
        expected_keyword="$s =",
        tags=["here-string", "edge", "blank-lines"],
    ),
]


BRACE_DEPTH_CASES: list[BraceDepthCase] = [
    BraceDepthCase(
        id="bd_complete_func",
        name="完整函数后括号深度为 0",
        content='function f { param($x) "hi" }',
        expected_depth=0,
    ),
    BraceDepthCase(
        id="bd_inside_func",
        name="未闭合函数内括号深度为 1",
        content='function f { param($x)',
        expected_depth=1,
    ),
    BraceDepthCase(
        id="bd_string_comment_fakes",
        name="字符串和注释中的括号不影响深度",
        content='$s = "{ fake }" # comment { also fake }',
        expected_depth=0,
    ),
    BraceDepthCase(
        id="bd_hs_double",
        name="双引号 here-string 中的假括号不影响深度",
        content="$s = " + _hs_double(["{brace1}", "{brace2}"]) + "\n",
        expected_depth=0,
    ),
    BraceDepthCase(
        id="bd_hs_single",
        name="单引号 here-string 中的假括号不影响深度",
        content="$s = " + _hs_single(["{brace}"]) + "\n",
        expected_depth=0,
    ),
    BraceDepthCase(
        id="bd_nested_funcs",
        name="嵌套函数闭合后深度为 0",
        content="""\
function Outer {
    function Inner {
        return 1
    }
}
""",
        expected_depth=0,
    ),
    BraceDepthCase(
        id="bd_class",
        name="class 定义闭合后深度为 0",
        content="""\
class Foo {
    [string]$Name
}
""",
        expected_depth=0,
    ),
    BraceDepthCase(
        id="bd_hs_multiline",
        name="多行 here-string 中的假括号不影响深度",
        content="$config = " + _hs_double(["[server]", "host = {localhost}", "port = {8080}"]) + "\n",
        expected_depth=0,
    ),
    BraceDepthCase(
        id="bd_empty",
        name="空字符串括号深度为 0",
        content="",
        expected_depth=0,
    ),
    BraceDepthCase(
        id="bd_hs_triple_nested_look",
        name="三层伪嵌套here-string中的假括号不影响深度",
        content="$s = " + _hs_double(["  @\"", "  {level2}", "    @\"", "    {level3}", "    \"@", "  \"@", "  {outside}"]) + "\n",
        expected_depth=0,
    ),
]


INSERT_CODE_CASES: list[InsertCodeCase] = [
    InsertCodeCase(
        id="ins_before_func",
        name="在函数之前插入代码",
        content="""\
function Test-Func {
    param([int]$x)
    return $x
}
""",
        code_to_insert="# INSERTED CHECK\n",
        expected_starts_with="# INSERTED CHECK",
    ),
    InsertCodeCase(
        id="ins_after_param",
        name="在脚本级 param 块之后插入代码",
        content="""\
param([string]$Name)
Write-Host $Name
""",
        code_to_insert="# VERSION CHECK\n",
        expected_contains="# VERSION CHECK",
    ),
    InsertCodeCase(
        id="ins_after_hs_param",
        name="在 here-string 默认值的 param 块之后插入代码",
        content="param(\n    [string]$Config = " + _hs_double(["key=value"]) + "\n)\nStart-App\n",
        code_to_insert="# CHECK\n",
        expected_contains="# CHECK",
    ),
]


HERE_STRING_CASES: list[HereStringCase] = [
    HereStringCase(
        id="hs_skip_not_at_start",
        name="非 here-string 开头位置返回原位置",
        content="hello world",
        position=0,
        expected_new_pos=0,
    ),
    HereStringCase(
        id="hs_skip_double",
        name="跳过双引号 here-string (@\" ... \"@)",
        content=_hs_double(["a", "b"]),
        position=0,
        expected_new_pos=len(_hs_double(["a", "b"])),
    ),
    HereStringCase(
        id="hs_skip_single",
        name="跳过单引号 here-string (@' ... '@)",
        content=_hs_single(["a", "b"]),
        position=0,
        expected_new_pos=len(_hs_single(["a", "b"])),
    ),
    HereStringCase(
        id="hs_skip_not_hs_at_at",
        name="@ 后不跟引号或换行则不跳过",
        content='@(1,2,3)',
        position=0,
        expected_new_pos=0,
    ),
    HereStringCase(
        id="hs_skip_crlf",
        name="CRLF 换行的 here-string",
        content=_hs_double(["line1"]).replace("\n", "\r\n"),
        position=0,
        expected_new_pos=len(_hs_double(["line1"]).replace("\n", "\r\n")),
    ),
    HereStringCase(
        id="hs_skip_empty_body",
        name="空 here-string 体",
        content='@"\n"@',
        position=0,
        expected_new_pos=5,  # @"\n"@ = 5 chars
    ),
    # ── 极端边界用例 ──
    HereStringCase(
        id="hs_skip_at_not_followed_by_newline",
        name='@" 后不跟换行符（普通字符串）',
        content='@"not a here-string"',
        position=0,
        expected_new_pos=0,
    ),
    HereStringCase(
        id="hs_skip_indented_end_marker",
        name="缩进的结束标记不关闭 here-string",
        # here-string 体内 "  \"@  有前导空格，不是行首，不应关闭；真正关闭在最后一行（_hs_double自动添加）
        content=_hs_double(["line1", "  \"@", "  still inside", "real end"]),
        position=0,
        expected_new_pos=len(_hs_double(["line1", "  \"@", "  still inside", "real end"])),
    ),
    HereStringCase(
        id="hs_skip_backtick_escaped_quote",
        name="反引号转义的引号阻止过早关闭",
        # `\" 中反引号转义了引号，"@ 不应作为结束标记；真正结束在最后
        content=_hs_double(["hello `\"@ not end", "world"]),
        position=0,
        expected_new_pos=len(_hs_double(["hello `\"@ not end", "world"])),
    ),
    HereStringCase(
        id="hs_skip_at_end_of_string",
        name="@ 在字符串末尾（无后续字符）",
        content='@',
        position=0,
        expected_new_pos=0,
    ),
    HereStringCase(
        id="hs_skip_single_contains_double_end",
        name="单引号 here-string 内含 \"@ 不关闭",
        content=_hs_single(['contains "@ and even', 'multiple "@@" signs']),
        position=0,
        expected_new_pos=len(_hs_single(['contains "@ and even', 'multiple "@@" signs'])),
    ),
    HereStringCase(
        id="hs_skip_single_line_body",
        name="单行 here-string 体",
        content=_hs_double(["single line"]),
        position=0,
        expected_new_pos=len(_hs_double(["single line"])),
    ),
    HereStringCase(
        id="hs_skip_lf_only_no_cr",
        name="纯 LF 换行（无 CR）",
        content='@"\nline\n"@',
        position=0,
        expected_new_pos=len('@"\nline\n"@'),
    ),
    HereStringCase(
        id="hs_skip_position_in_middle",
        name="位置在here-string中间（非起始位置，不跳过）",
        content=_hs_double(["line1", "line2", "line3"]),
        position=5,  # 在here-string内部
        expected_new_pos=5,
    ),
    HereStringCase(
        id="hs_skip_position_after_end",
        name="位置在here-string结束标记之后",
        content=_hs_double(["content"]) + " after",
        position=len(_hs_double(["content"])),  # 刚好在"@之后
        expected_new_pos=len(_hs_double(["content"])),
    ),
    HereStringCase(
        id="hs_skip_single_contains_single_end",
        name="单引号here-string内含'@序列不关闭",
        content=_hs_single(["contains '@ sequence", "still inside", "real end"]),
        position=0,
        expected_new_pos=len(_hs_single(["contains '@ sequence", "still inside", "real end"])),
    ),
    HereStringCase(
        id="hs_skip_backtick_backtick",
        name="反引号转义的反引号（``）不影响结束标记",
        content=_hs_double(["line with `` backtick", "``@ not an end", "real end line"]),
        position=0,
        expected_new_pos=len(_hs_double(["line with `` backtick", "``@ not an end", "real end line"])),
    ),
    HereStringCase(
        id="hs_skip_crlf_indented_end",
        name="CRLF换行下缩进的结束标记不关闭",
        content=_hs_double(["line1", "  \"@", "still in", "real end"]).replace("\n", "\r\n"),
        position=0,
        expected_new_pos=len(_hs_double(["line1", "  \"@", "still in", "real end"]).replace("\n", "\r\n")),
    ),
    HereStringCase(
        id="hs_skip_double_contains_at_at",
        name="双引号here-string内含@@序列",
        content=_hs_double(["email: user@@example.com", "another @@ here", "end line"]),
        position=0,
        expected_new_pos=len(_hs_double(["email: user@@example.com", "another @@ here", "end line"])),
    ),
    HereStringCase(
        id="hs_skip_backtick_at_in_single",
        name="单引号here-string内反引号无转义效果（`@仍是普通字符）",
        content=_hs_single(["line with `@ backtick", "`\" also not special", "real end"]),
        position=0,
        expected_new_pos=len(_hs_single(["line with `@ backtick", "`\" also not special", "real end"])),
    ),
    HereStringCase(
        id="hs_skip_tab_indented_end",
        name="Tab缩进的结束标记不关闭here-string",
        content=_hs_double(["line1", "\t\"@", "still inside tab test", "real end"]),
        position=0,
        expected_new_pos=len(_hs_double(["line1", "\t\"@", "still inside tab test", "real end"])),
    ),
]


# ── JSON 导出（供 PowerShell 使用）─────────────────────────────────────────


def _case_to_dict(case) -> dict:
    """将 dataclass 转为 JSON 可序列化的 dict。"""
    d = asdict(case)
    return d


def export_cases_as_json() -> dict:
    """将所有测试用例导出为 JSON 可序列化的 dict。"""
    return {
        "insert_point_cases": [_case_to_dict(c) for c in INSERT_POINT_CASES],
        "brace_depth_cases": [_case_to_dict(c) for c in BRACE_DEPTH_CASES],
        "insert_code_cases": [_case_to_dict(c) for c in INSERT_CODE_CASES],
        "here_string_cases": [_case_to_dict(c) for c in HERE_STRING_CASES],
    }


def write_json(output_path: Path | None = None) -> Path:
    """将测试用例写入 JSON 文件，返回文件路径。"""
    if output_path is None:
        output_path = Path(__file__).resolve().parent.parent / "tests" / "ps1_syntax_cases.json"
    data = export_cases_as_json()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


# ── CLI 入口 ────────────────────────────────────────────────────────────────


def main() -> int:
    if "--export-json" in sys.argv:
        path = write_json()
        print(f"Test cases exported to: {path}")
        print(f"  Insert point cases: {len(INSERT_POINT_CASES)}")
        print(f"  Brace depth cases:  {len(BRACE_DEPTH_CASES)}")
        print(f"  Insert code cases:  {len(INSERT_CODE_CASES)}")
        print(f"  Here-string cases:  {len(HERE_STRING_CASES)}")
        return 0
    print("Usage: python -m lib.ps1_test_cases --export-json")
    return 1


if __name__ == "__main__":
    sys.exit(main())
