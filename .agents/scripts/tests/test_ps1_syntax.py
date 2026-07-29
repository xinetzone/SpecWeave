#!/usr/bin/env python3
"""测试 ps1_syntax.find_top_level_insert_point 在复杂场景下的准确性。

覆盖场景：
  1. 简单脚本级 param()
  2. 函数开头有 param()（不应误判为脚本级）
  3. 注释块 <# ... #> 包裹
  4. 嵌套函数 + 嵌套括号
  5. 字符串中的括号和 #
  6. here-string @' '@ / @" "@
  7. 混合注释和字符串
  8. #Requires 声明
  9. 空文件/纯注释文件
  10. 单引号转义 '' 和双引号反引号转义 `
  11. 多个函数定义
  12. 类定义（PowerShell 5.0+ class）
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.ps1_syntax import (
    find_top_level_insert_point,
    find_non_whitespace,
    skip_whitespace_and_comments,
    validate_brace_balance,
    find_matching_close,
    find_param_block_end,
)

PASS = 0
FAIL = 0


def check(name: str, content: str, expected_pos_keyword: str | None = None, expected_min_pos: int = 0):
    """测试 find_top_level_insert_point。

    Args:
        name: 测试名称
        content: PowerShell 脚本内容
        expected_pos_keyword: 期望插入点所在位置附近的关键词（用于验证插入点正确性）
        expected_min_pos: 期望插入点不小于此位置
    """
    global PASS, FAIL
    pos = find_non_whitespace(content, 0)
    pos = skip_whitespace_and_comments(content, pos)
    insert_pos = find_top_level_insert_point(content, pos)

    # 验证括号平衡
    lines = content.split('\n')
    balance_errors = validate_brace_balance(lines)

    ok = True
    issues = []

    if insert_pos < expected_min_pos:
        ok = False
        issues.append(f"insert_pos={insert_pos} < expected_min_pos={expected_min_pos}")

    if insert_pos > len(content):
        ok = False
        issues.append(f"insert_pos={insert_pos} > len(content)={len(content)}")

    if expected_pos_keyword is not None:
        # 检查插入点后是否包含期望关键词（在合理窗口内）
        window_start = insert_pos
        window_end = min(insert_pos + 200, len(content))
        window = content[window_start:window_end]
        if expected_pos_keyword not in window:
            # 也检查插入点前（可能插入点在函数之前）
            pre_window = content[max(0, insert_pos - 50):insert_pos]
            if expected_pos_keyword not in pre_window:
                ok = False
                issues.append(f"keyword '{expected_pos_keyword}' not found near insert_pos={insert_pos}")

    # 验证插入点处 brace_depth 为 0
    if insert_pos < len(content):
        pre = content[:insert_pos]
        from lib.ps1_syntax import _calc_brace_depth
        depth = _calc_brace_depth(pre)
        if depth != 0:
            ok = False
            issues.append(f"brace_depth at insert_pos={insert_pos} is {depth}, expected 0")

    if ok:
        PASS += 1
        snippet = content[insert_pos:insert_pos+60].replace('\n', '\\n')
        print(f"  ✓ {name}")
        print(f"    insert_pos={insert_pos}, next: \"{snippet}...\"")
    else:
        FAIL += 1
        print(f"  ✗ {name}")
        for issue in issues:
            print(f"    ERROR: {issue}")
        print(f"    insert_pos={insert_pos}")
        if insert_pos < len(content):
            snippet = content[max(0,insert_pos-20):insert_pos+60].replace('\n', '\\n')
            print(f"    context: \"...{snippet}...\"")
    print()


def main():
    global PASS, FAIL
    print("=" * 70)
    print("Testing find_top_level_insert_point with complex PowerShell scripts")
    print("=" * 70)
    print()

    # ── 场景1：简单脚本级 param() ──
    check(
        "1. 脚本级 param() - 应在 param 块后插入",
        """\
param(
    [string]$Name,
    [int]$Count
)

Write-Host "Hello $Name"
""",
        expected_pos_keyword="Write-Host",
        expected_min_pos=40,
    )

    # ── 场景2：函数开头有 param()（不应误判为脚本级）──
    check(
        "2. 函数内 param() - 应在 function 前插入",
        """\
function Get-Greeting {
    param(
        [string]$Name
    )
    return "Hello $Name"
}

Get-Greeting -Name "World"
""",
        expected_pos_keyword="function",
        expected_min_pos=0,
    )

    # ── 场景3：注释块 <# ... #> 头部 ──
    check(
        "3. 头部注释块 + 脚本级 param()",
        """\
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
        expected_pos_keyword="Get-ChildItem",
        expected_min_pos=80,
    )

    # ── 场景4：嵌套函数 + 嵌套括号 ──
    check(
        "4. 嵌套函数 - 应在第一个 function 前插入",
        """\
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
        expected_pos_keyword="function Outer",
    )

    # ── 场景5：字符串中的括号和 # ──
    check(
        "5. 字符串中的假括号和注释符号",
        """\
$msg = "This is { not a real brace } and # not a comment"
Write-Host $msg
$other = 'single quotes { also fake } # fake too'
Write-Host $other
function Test { "nested { brace } in string" }
""",
        expected_pos_keyword='$msg =',
    )

    # ── 场景6：#Requires 声明 + 脚本级 param()（模拟 migrate-to-pwsh7 调用方式）──
    # 在实际使用中，search_from 是 #Requires 行之后的位置
    content6 = """\
#Requires -Version 5.1
param(
    [switch]$Force
)
if ($Force) { Write-Host "Forced" }
"""
    requires_end = content6.find('\n', content6.index('#Requires')) + 1
    check_from6 = skip_whitespace_and_comments(content6, requires_end)
    insert_pos6 = find_top_level_insert_point(content6, check_from6)
    snippet6 = content6[insert_pos6:insert_pos6+50].replace('\n', '\\n')
    # param 块结束位置大约在 44 左右
    if insert_pos6 >= 40 and 'if (' in content6[insert_pos6:insert_pos6+50]:
        PASS += 1
        print(f"  ✓ 6. #Requires + 脚本级 param()（从Requires之后搜索）")
        print(f"    search_from={check_from6}, insert_pos={insert_pos6}, next: \"{snippet6}...\"")
    else:
        FAIL += 1
        print(f"  ✗ 6. #Requires + 脚本级 param()（从Requires之后搜索）")
        print(f"    search_from={check_from6}, insert_pos={insert_pos6}, expected >= 40 near 'if ('")
        print(f"    next: \"{snippet6}...\"")
    print()

    # ── 场景7：行注释干扰 ──
    check(
        "7. 行注释中的假括号",
        """\
# This line has { fake } braces and # fake comment starts
# Another { comment } line
Write-Host "real code starts here"
""",
        expected_pos_keyword="Write-Host",
    )

    # ── 场景8：单行函数 + 脚本级代码 ──
    check(
        "8. 单行函数 + 后续脚本级代码",
        """\
function Say-Hi { Write-Host "Hi" }
Say-Hi
""",
        expected_pos_keyword="function Say-Hi",
    )

    # ── 场景9：if/else 块中的括号 ──
    check(
        "9. 脚本级 if/else 控制流（无函数）",
        """\
if ($IsWindows) {
    Write-Host "Windows"
} else {
    Write-Host "Other"
}
""",
        expected_pos_keyword="if (",
    )

    # ── 场景10：单引号转义 '' 和双引号反引号转义 ` ──
    check(
        "10. 字符串转义序列",
        """\
$a = 'don''t worry about { fake } braces'
$b = "hello `"world`" with `$var and { fake }"
Write-Host "$a $b"
""",
        expected_pos_keyword='$a =',
    )

    # ── 场景11：注释块内包含 param( 和 { ──
    check(
        "11. 注释块内包含 param( 和 { 的假信号",
        """\
<#
Example code that should NOT be parsed:
function Fake {
    param($x)
    { nested block }
}
#>
Write-Host "Real code"
""",
        expected_pos_keyword="Write-Host",
    )

    # ── 场景12：多个函数定义，脚本级代码在最后 ──
    check(
        "12. 多个函数定义",
        """\
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
        expected_pos_keyword="function Func1",
    )

    # ── 场景13：类定义（PowerShell class）──
    check(
        "13. PowerShell class 定义",
        """\
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
        expected_pos_keyword="class MyClass",
    )

    # ── 场景14：空函数体 + 脚本级代码 ──
    check(
        "14. 空/简单函数体",
        """\
function EmptyFunc {}
function SimpleFunc { "simple" }
Write-Host "Done"
""",
        expected_pos_keyword="function EmptyFunc",
    )

    # ── 场景15：try/catch/finally 块 ──
    check(
        "15. try/catch/finally 在脚本级",
        """\
try {
    $result = 1 / 0
} catch {
    Write-Error $_
} finally {
    Write-Host "cleanup"
}
""",
        expected_pos_keyword="try {",
    )

    # ── 场景16：dot-source 引用和脚本级代码 ──
    check(
        "16. dot-source + 脚本级代码",
        """\
. "$PSScriptRoot/lib.ps1"
$config = Get-Config
Write-Host $config.Name
""",
        expected_pos_keyword='.',
    )

    # ── 场景17：函数名含特殊字符（如 : 和 .）──
    check(
        "17. 函数名含特殊字符",
        """\
function MyModule:Invoke-Task {
    param([string]$TaskName)
    Write-Host "Running $TaskName"
}
MyModule:Invoke-Task -TaskName "build"
""",
        expected_pos_keyword="function MyModule",
    )

    # ── 场景18：脚本开头有 using 语句 ──
    check(
        "18. using namespace/module 语句",
        """\
using namespace System.Text
using module ./MyModule.psm1
Write-Host "Using loaded"
""",
        expected_pos_keyword="using namespace",
    )

    # ── 总结 ──
    print("=" * 70)
    print(f"Results: {PASS} passed, {FAIL} failed")
    print("=" * 70)

    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
