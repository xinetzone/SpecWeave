# PS1 Syntax 跨平台增强 - Product Requirement Document

## Overview

- **Summary**: 为 ps1_syntax 模块（Python）和 encoding-safety.ps1 模块（PowerShell）增加跨平台编码鲁棒性和版本感知能力。v1.1.0 新增 UTF-8 BOM 自动跳过和三种换行符统一支持；v1.2.0 新增版本感知参数 `target_version`（支持 PS5.1/PS7.x/auto 三模式）、版本自动检测启发式规则、CR-only 换行在注释/插入点扫描中的完整支持。确保在 Windows/Linux/macOS 三平台上 here-string 解析、括号深度计算和注释处理行为完全一致，并可按目标 PowerShell 版本精准切换换行符策略。
- **Version**: 1.2.0（从 1.1.0 升级）
- **Status**: ✅ 已完成并发布（v1.2.0，commits e3201a52..3d77bb69）
- **Purpose**: 解决在 Linux/macOS 平台处理 Windows 编写的 PS1 脚本（CRLF+BOM）和 Windows 平台处理 Linux 编写的 PS1 脚本（LF）时可能出现的解析偏差；提高对混合换行符、BOM 头等非标准但实际存在的文件格式的容错能力；通过结构化日志埋点支持跨平台兼容性问题排查。
- **Target Users**: SpecWeave 脚本工具库的所有调用方（check-pwsh7-compliance.py、migrate-to-pwsh7.py 等），以及在跨平台环境中处理 PowerShell 脚本的开发者。

## Goals

- ✅ 新增编码预处理层：自动检测并跳过 UTF-8 BOM（`\ufeff` / `0xFEFF`）
- ✅ 统一换行符处理：支持 LF（`\n`）、CRLF（`\r\n`）、CR（`\r`，老式 Mac）三种换行符
- ✅ 跨平台 here-string 行首检测：精确识别三种换行符后的行首位置，避免 CRLF 双行首误判
- ✅ Python/PowerShell 双端逻辑完全对齐，共享测试用例覆盖所有新场景
- ✅ 结构化日志埋点：双端对齐的追踪函数（`_trace_hs`/`Write-Ps1TraceHs` 等）
- ✅ 版本感知参数 `target_version`（v1.2.0）
- ✅ 版本自动检测工具（v1.2.0）

## Non-Goals (Out of Scope)

- 不修改 PowerShell 语法本身的解析规则（PS5.1/PS7 当前 here-string 核心行为一致，无需差异化处理）
- 不实现 PowerShell 抽象语法树（AST）级别的完整解析（当前仅做字符级语法分析）
- 不处理 PowerShell 7+ 新增的 `??`、`??=`、三元运算符 `? :` 等新语法特性（这些不影响 here-string 和括号深度计算）
- 不做文件编码转换（仅在解析层面处理 BOM，不改变原始文件编码）
- `skip_line_comments` 等辅助函数对 CR-only 换行的完整支持（v1.2.0 已实现）

## Background & Context

### 实际验证结论

经在 PowerShell 7.6.4 和 Windows PowerShell 5.1 上的实际测试验证：

| 行为 | PS5.1 | PS7.x | v1.0.0 | v1.1.0 |
|------|-------|-------|--------|--------|
| 严格行首 `"@`/`'@` 结束标记 | ✅ 必须 | ✅ 必须 | ✅ 正确 | ✅ 正确 |
| 空格前缀结束标记 | ❌ 报错 | ❌ 报错 | ✅ 正确拒绝 | ✅ 正确拒绝 |
| Tab 前缀结束标记 | ❌ 报错 | ❌ 报错 | ✅ 正确拒绝 | ✅ 正确拒绝 |
| CRLF 换行符 | ✅ 支持 | ✅ 支持 | ✅ 正确处理 | ✅ 正确处理 |
| LF 换行符 | - (Windows) | ✅ 支持 | ✅ 正确处理 | ✅ 正确处理 |
| CR 换行符 | 未测试 | 未测试 | ❌ 未支持 | ✅ 支持 |
| UTF-8 BOM 开头 | ✅ 支持 | ✅ 支持 | ❌ 误判为非空白 | ✅ 自动跳过 |

**关键发现**：PS5.1 和 PS7.x 在 here-string 核心语法上的行为完全一致，不存在需要差异化处理的语法分歧。因此 v1.1.0 的核心价值在于跨平台编码鲁棒性（换行符 + BOM），版本感知参数（`target_version`）作为扩展预留点延期至 v1.2.0。

### v1.0.0 局限性

1. **BOM 不感知**：文件开头的 UTF-8 BOM 会被当作普通非空白字符，导致 `find_non_whitespace` 返回位置 0，进而使后续解析从 BOM 开始
2. **CR-only 换行不支持**：老式 Mac 风格的 `\r` 换行符未被识别为换行，导致 here-string 行首检测失败
3. **混合换行符**：同一文件中混用 CRLF 和 LF 时，行首检测逻辑可能对 CRLF 双计行首
4. **缺少日志埋点**：here-string 解析过程无可观测性，跨平台问题难以排查

## Design Details

### 1. BOM 动态跳过

BOM 处理采用**内联动态跳过**策略（不做预处理截断），避免位置映射问题：

**Python 端**（在 `_skip_ps1_here_string` 和 `find_non_whitespace`/`iter_code_chars` 入口处）：
```python
# 跳过 UTF-8 BOM（仅当 i==0 且首字符是 BOM 时）
if i == 0 and n > 0 and content[0] == '\ufeff':
    _trace_bom(True)
    i = 1
```

**PowerShell 端**（在 `Skip-Ps1HereString` 和 `Find-NonWhitespace` 中）：
```powershell
$bomChar = [char]0xFEFF
if ($i -eq 0 -and $Content[0] -eq $bomChar) {
    $i = 1
}
```

BOM 跳过仅在起始位置为 0 时生效，避免误跳字符串内部出现的 BOM 字符。

### 2. 跨平台换行符检测

统一使用 `_is_line_end()` 辅助函数判断换行符，CRLF 优先匹配避免误拆：

```python
def _is_line_end(content: str, pos: int) -> bool:
    """检测当前位置是否为换行符（LF/CRLF/CR）。

    CRLF 优先判定：若当前位置是 \r 且下一个字符是 \n，视为 CRLF 整体。
    """
    if pos >= len(content):
        return False
    ch = content[pos]
    if ch == '\r':
        if pos + 1 < len(content) and content[pos + 1] == '\n':
            return True  # CRLF（两字符）
        return True  # CR-only
    if ch == '\n':
        return True  # LF
    return False
```

行首判定 `_is_at_line_start()` 精确处理三种换行符：
- 文件开头（pos == 0 或跳过 BOM 后 pos == 1）
- LF 后：前一个字符是 `\n`
- CR 后：前一个字符是 `\r` 且不是 CRLF 的一部分（即前一个字符是 `\r` 时，前前字符不是 `\r` 后接 `\n` 的情况——实际上简化为：前一字符是 `\r` 且当前位置前没有更前的 `\r\n` 组合）

实际实现中通过精确的位置计算避免 CRLF 双行首误判。

### 3. Here-string 跨平台解析

`_skip_ps1_here_string` 核心逻辑：
1. 入口处检测并跳过 BOM（position=0 时）
2. 检测 `@"`/`@'` 后的换行符，记录换行符类型（CRLF/LF/CR）
3. 逐字符扫描，遇到行首结束标记（`<quote>@`）时退出
4. 双引号 here-string 支持反引号转义（`` `"@ `` 不结束）
5. 到达 EOF 时记录警告日志

### 4. 结构化日志埋点（v1.1.0 新增）

双端对齐的追踪函数族：

| Python 函数 | PowerShell 函数 | 用途 |
|-------------|----------------|------|
| `_trace_hs(pos, event, ...)` | `Write-Ps1TraceHs` | here-string 事件追踪（start/end/escape/eof_warn/skip） |
| `_trace_newline(pos, type)` | `Write-Ps1TraceNewline` | 换行符检测（CRLF/LF/CR） |
| `_trace_bom(detected)` | `Write-Ps1TraceBom` | BOM 检测结果 |

日志格式统一为 `[HS-START] pos=0 quote=" newline=CR` 形式，便于跨平台问题定位。

### 5. 向后兼容性保证

1. **API 签名不变**：所有公开函数签名保持不变，现有调用方无需任何修改
2. **位置语义不变**：BOM 采用动态跳过策略，返回位置始终相对于传入的原始 content 字符串
3. **纯函数保证**：所有逻辑仍然保持纯函数特性，无副作用
4. **默认行为增强**：CR/LF/CRLF 三种换行符默认全部支持，无需额外配置

## Implementation Summary

### 已完成（v1.1.0）

1. ✅ `_is_line_end()` 跨平台换行符检测辅助函数（Python）
2. ✅ `_is_at_line_start()` 行首判定辅助函数（Python）
3. ✅ `Test-Ps1AtLineStart` 行首检测函数（PowerShell）
4. ✅ `_skip_ps1_here_string()` 重构支持 CR/LF/CRLF + BOM
5. ✅ `Skip-Ps1HereString` 重构支持 CR/LF/CRLF + BOM
6. ✅ `find_non_whitespace()` 更新支持 BOM 跳过
7. ✅ `Find-NonWhitespace` 更新支持 BOM 跳过
8. ✅ `iter_code_chars()` 更新支持 BOM 跳过
9. ✅ 结构化日志埋点（`_trace_hs`/`_trace_newline`/`_trace_bom` 及 PowerShell 对应函数）
10. ✅ 新增 11 个跨平台测试用例（7 HereString + 4 InsertPoint）
11. ✅ Python 78 个、PowerShell 81 个测试全部通过
12. ✅ 版本号更新到 1.1.0（双端）

### 已完成（v1.2.0）

1. ✅ `Ps1Version` 类型别名和 `detect_ps_version_from_content()` 版本自动检测函数（Python）
2. ✅ `Get-Ps1TargetVersion` 和 `Resolve-Ps1TargetVersion` 版本检测函数（PowerShell）
3. ✅ `_skip_ps1_here_string`/`Skip-Ps1HereString` 添加 `target_version`/`-TargetVersion` 参数，实现 5.1/7.x 换行符分支
4. ✅ 所有公开函数添加 `target_version`/`-TargetVersion` 参数并正确传递调用链
5. ✅ `skip_line_comments`/`Skip-Ps1LineComments` 版本感知 CR 换行处理（空行检测+注释终止）
6. ✅ `find_top_level_insert_point`/`Find-Ps1TopLevelInsertPoint` 版本感知 CR 空行处理
7. ✅ `VersionDetectCase` 数据类和 10 个版本检测用例
8. ✅ PS5.1 严格模式 here-string 测试用例（3 个）
9. ✅ TargetVersion 模式测试（7 个：auto/explicit/CR/CRLF 场景）
10. ✅ PowerShell 测试运行器添加版本检测和 TargetVersion 测试段
11. ✅ 版本号更新到 1.2.0（双端）
12. ✅ Python 98 个、PowerShell 101 个测试全部通过（共 199 个）

## Test Scenarios

### v1.1.0 新增跨平台测试用例（11个）

| ID | 名称 | 分类 | 换行/BOM | 场景说明 |
|----|------|------|----------|----------|
| `hs_skip_cr_only_newline` | CR-only 换行双引号 here-string | HereString | CR | 老式 Mac 风格 CR 换行 |
| `hs_skip_cr_single_quoted` | CR-only 换行单引号 here-string | HereString | CR | 单引号变体 CR 换行 |
| `hs_skip_mixed_newlines_cr_lf` | 混合换行符 here-string | HereString | LF+CRLF+CR | 同一字符串内三种换行符混用 |
| `hs_skip_cr_indented_end` | CR 换行下缩进结束标记 | HereString | CR | 缩进的 `"@` 不关闭 here-string |
| `hs_skip_utf8_bom_at_start` | UTF-8 BOM 开头 here-string | HereString | LF+BOM | BOM 在位置0自动跳过 |
| `hs_skip_bom_crlf` | BOM + CRLF 换行 here-string | HereString | CRLF+BOM | Windows 默认编码场景 |
| `hs_skip_cr_with_backtick_escape` | CR 换行反引号转义 | HereString | CR | `` `"@ `` 转义不结束 |
| `hs_cr_only_toplevel` | CR 换行顶层 here-string | InsertPoint | CR | 假花括号不影响括号深度 |
| `hs_bom_toplevel` | BOM 开头+顶层 here-string | InsertPoint | LF+BOM | BOM 不影响插入点检测 |
| `hs_bom_param_default` | BOM+param here-string 默认值 | InsertPoint | LF+BOM | param 块内 here-string |
| `hs_cr_in_function` | CR 换行函数体内 here-string | InsertPoint | CR | 函数体+CR+here-string 组合 |

详细用例说明见 `.agents/scripts/tests/CROSSPLATFORM_TEST_CASES.md`。

## Acceptance Criteria

### v1.1.0 已验证

1. ✅ 所有原有 67 个测试用例继续通过（无回归）
2. ✅ 新增 11 个跨平台测试用例双端全部通过
3. ✅ 含 BOM 的 PS1 文件能正确识别 here-string 和括号深度
4. ✅ CR-only 换行符 here-string 能正确解析
5. ✅ 混合换行符（LF/CRLF/CR）文件能正确解析
6. ✅ BOM + CRLF（Windows 默认编码）场景正确处理
7. ✅ CR 换行下反引号转义和缩进结束标记正确处理
8. ✅ Python 端版本号更新为 `__version__ = "1.1.0"`
9. ✅ PowerShell 端版本号更新为 `$script:EncodingSafetyVersion = '1.1.0'`
10. ✅ 双端测试总计 Python 78 个、PowerShell 81 个用例全部通过

### v1.2.0 已验证

1. ✅ `target_version` 参数在所有公开函数中正确传递
2. ✅ `detect_ps_version_from_content()` 对各种 `#Requires` 声明和 PS7+ 特征的识别准确率 100%（10/10 用例通过）
3. ✅ `skip_line_comments` 完整支持 CR 换行
4. ✅ 版本检测相关测试用例双端通过（10 个版本检测 + 7 个 TargetVersion 模式）
5. ✅ PS5.1 严格模式正确拒绝 CR-only 换行（here-string 和注释）
6. ✅ PS7.x 跨平台模式正确处理 CRLF/LF/CR 三种换行
7. ✅ Python 端版本号更新为 `__version__ = "1.2.0"`
8. ✅ PowerShell 端版本号更新为 `$script:EncodingSafetyVersion = '1.2.0'`
9. ✅ 双端测试总计 Python 98 个、PowerShell 101 个用例全部通过（共 199 个）
