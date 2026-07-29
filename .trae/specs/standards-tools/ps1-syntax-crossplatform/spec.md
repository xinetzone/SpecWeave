# PS1 Syntax 跨平台增强 - Product Requirement Document

## Overview

- **Summary**: 为 ps1_syntax 模块（Python）和 encoding-safety.ps1 模块（PowerShell）增加 PowerShell 版本感知能力和跨平台编码鲁棒性。通过 `target_version` 参数显式声明目标解析版本（5.1/7.x/auto），新增编码预处理层自动处理 UTF-8 BOM 和混合换行符，确保在 Windows/Linux/macOS 三平台上解析行为完全一致。当前 v1.0.0 核心逻辑已验证 PS5.1 与 PS7.x here-string 行为一致，本次增强主要面向跨平台编码鲁棒性和未来版本兼容性预留扩展点。
- **Version**: 1.1.0 (从 1.0.0 升级)
- **Purpose**: 解决在 Linux/macOS 平台处理 Windows 编写的 PS1 脚本（CRLF+BOM）和 Windows 平台处理 Linux 编写的 PS1 脚本（LF）时可能出现的解析偏差；为未来 PowerShell 版本可能引入的语法差异预留版本适配接口；提高对混合换行符、无 trailing newline、BOM 头等非标准但实际存在的文件格式的容错能力。
- **Target Users**: SpecWeave 脚本工具库的所有调用方（check-pwsh7-compliance.py、migrate-to-pwsh7.py 等），以及在跨平台环境中处理 PowerShell 脚本的开发者。

## Goals

- ✅ 为所有核心解析函数新增 `target_version` 参数（`'5.1' | '7.x' | 'auto'`），默认 `'auto'` 保持向后兼容
- ✅ 新增编码预处理层：自动检测并跳过 UTF-8 BOM（`\xEF\xBB\xBF`）
- ✅ 统一换行符处理：支持 LF（`\n`）、CRLF（`\r\n`）、CR（`\r`，老式 Mac）三种换行符
- ✅ 增强 here-string 对文件末尾无 trailing newline 场景的容错
- ✅ Python/PowerShell 双端逻辑完全对齐，共享测试用例覆盖所有新场景
- ✅ 版本检测工具函数：从文件内容或 `$PSVersionTable` 自动判断目标版本

## Non-Goals (Out of Scope)

- 不修改 PowerShell 语法本身的解析规则（PS5.1/PS7 当前 here-string 核心行为一致，无需差异化处理）
- 不实现 PowerShell 抽象语法树（AST）级别的完整解析（当前仅做字符级语法分析）
- 不处理 PowerShell 7+ 新增的 `??`、`??=`、三元运算符 `? :` 等新语法特性（这些不影响 here-string 和括号深度计算）
- 不做文件编码转换（仅在解析层面处理 BOM，不改变原始文件编码）
- 不支持 PowerShell 7 未来可能引入的 here-string 新变体（预留接口但不猜测实现）

## Background & Context

### 实际验证结论

经在 PowerShell 7.6.4 和 Windows PowerShell 5.1 上的实际测试验证：

| 行为 | PS5.1 | PS7.x | 当前实现 |
|------|-------|-------|---------|
| 严格行首 `"@`/`'@` 结束标记 | ✅ 必须 | ✅ 必须 | ✅ 正确 |
| 空格前缀结束标记 | ❌ `WhitespaceBeforeHereStringFooter` 错误 | ❌ 同样报错 | ✅ 正确拒绝 |
| Tab 前缀结束标记 | ❌ 同样报错 | ❌ 同样报错 | ✅ 正确拒绝 |
| CRLF 换行符 | ✅ 支持 | ✅ 支持 | ✅ 正确处理 |
| LF 换行符 | - (Windows) | ✅ 支持 | ✅ 正确处理 |
| CR 换行符 | 未测试 | 未测试 | ❌ 未支持 |

**关键发现**：PS5.1 和 PS7.x 在 here-string 核心语法上的行为完全一致，不存在需要差异化处理的语法分歧。因此版本感知参数的主要价值在于：
1. 为未来可能的版本差异预留扩展点
2. 允许调用方显式声明严格/宽容解析模式
3. 在自动检测版本时可对已知差异做预处理

### 当前代码局限性

1. **BOM 不感知**：文件开头的 UTF-8 BOM（`\xEF\xBB\xBF`）会被当作普通字符，可能导致行首检测失败（BOM 后的 `"@` 前不是 `\n` 而是 BOM 字符）
2. **CR-only 换行不支持**：老式 Mac 风格的 `\r` 换行符未被识别为换行
3. **混合换行符**：同一文件中混用 CRLF 和 LF 时，`\r\n` 中的 `\r` 可能被误判
4. **无 trailing newline**：here-string 结束标记在文件最末尾且无换行符时，需要确保正确识别

## Design Details

### 1. 版本感知参数设计

#### Python 端

所有公开函数新增 `target_version` 关键字参数：

```python
Ps1Version = Literal['5.1', '7.x', 'auto']

def _skip_ps1_here_string(
    content: str,
    position: int,
    target_version: Ps1Version = 'auto',
) -> int:
    ...

def iter_code_chars(
    s: str,
    start: int = 0,
    target_version: Ps1Version = 'auto',
) -> Iterator[tuple[int, str]]:
    ...

def find_top_level_insert_point(
    content: str,
    marker: str | None = None,
    target_version: Ps1Version = 'auto',
) -> int:
    ...

def calc_brace_depth(
    content: str,
    end_pos: int = -1,
    target_version: Ps1Version = 'auto',
) -> int:
    ...
```

**版本行为矩阵**：

| target_version | 换行符处理 | BOM处理 | 说明 |
|---------------|-----------|---------|------|
| `'5.1'` | CRLF + LF | 跳过BOM | Windows PowerShell 兼容模式 |
| `'7.x'` | CRLF + LF + CR | 跳过BOM | PowerShell 7+ 跨平台模式 |
| `'auto'` | 自动检测 | 跳过BOM | 自动检测换行符类型（默认） |

#### PowerShell 端

对应函数新增 `-TargetVersion` 参数：

```powershell
function Skip-Ps1HereString {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)][AllowEmptyString()][string]$Content,
        [Parameter(Mandatory=$true, Position=1)][int]$Position,
        [Parameter(Position=2)][ValidateSet('5.1','7.x','auto')][string]$TargetVersion = 'auto'
    )
    ...
}
```

### 2. BOM 处理与换行符检测

BOM 处理采用**动态跳过**策略而非预处理截断，避免位置映射问题：

```python
def _skip_bom(content: str, pos: int) -> int:
    """若当前位置在文件开头且存在 UTF-8 BOM，跳过 BOM 返回新位置。

    仅在 pos==0 且 content[0] 为 U+FEFF（UTF-8 BOM 解码后）时跳过，
    避免破坏位置相对于原始 content 的语义。
    """
    if pos == 0 and content and content[0] == '\ufeff':
        return 1
    return pos
```

在所有公开解析函数入口处调用：若 position 为 0 且内容以 BOM 开头，从 position=1 开始解析；返回位置仍相对于原始 content。

**换行符检测逻辑**（替换当前硬编码的 `\r\n`/`\n` 检测）：

```python
def _is_line_end(content: str, pos: int) -> tuple[bool, int]:
    """检测当前位置是否为换行符，返回 (是否换行, 换行符长度)。

    支持:
    - \r\n (CRLF): 返回 (True, 2)
    - \n (LF): 返回 (True, 1)
    - \r (CR): 返回 (True, 1) — 注意 \r 后若紧跟 \n 则归入 CRLF
    """
    if pos >= len(content):
        return False, 0
    ch = content[pos]
    if ch == '\r':
        if pos + 1 < len(content) and content[pos + 1] == '\n':
            return True, 2  # CRLF
        return True, 1  # CR only
    if ch == '\n':
        return True, 1  # LF
    return False, 0


def _is_at_line_start(content: str, pos: int) -> bool:
    """检测当前位置是否在行首（文件开头或前一个字符是换行符）。"""
    if pos == 0:
        return True
    return _is_line_end(content, pos - 1)[0]
```

### 3. Here-string 起始检测增强

当前逻辑 `@<quote> 后必须紧跟 \r?\n` 需要增强为支持 CR-only：

```python
def _skip_ps1_here_string(content: str, position: int, target_version='auto'):
    n = len(content)
    i = position

    if i < n and content[i] == '@' and i + 1 < n and content[i+1] in ('"', "'"):
        quote_char = content[i+1]
        j = i + 2
        # 检测 @<quote> 后的换行符（支持 CR, CRLF, LF）
        is_le, le_len = _is_line_end(content, j)
        if is_le:
            # here-string 开始
            i = j + le_len
            end_marker = quote_char + '@'
            while i < n:
                at_line_start = _is_at_line_start(content, i)
                if at_line_start and content[i:i+2] == end_marker:
                    i += 2
                    break
                # 双引号 here-string 反引号转义
                if quote_char == '"' and content[i] == '`' and i + 1 < n:
                    i += 2
                    continue
                i += 1
            return i
    return position
```

### 4. 版本自动检测工具

```python
def detect_ps_version_from_content(content: str) -> Ps1Version:
    """从脚本内容特征推断目标 PowerShell 版本。

    检测启发式规则：
    - 含 `#Requires -Version 7` 或 `#Requires -PSEdition Core` → '7.x'
    - 含 `#Requires -Version 5` 或 `#Requires -PSEdition Desktop` → '5.1'
    - 含 `$IsWindows`/`$IsLinux`/`$IsMacOS` 等 PS7+ 自动变量 → '7.x'
    - 含 `??` 或 `??=` 运算符（PS7+特性）→ '7.x'
    - 其他情况返回 '7.x'（默认跨平台模式）
    """
    # 简化的启发式检测
    if re.search(r'#Requires\s+-Version\s+7', content, re.IGNORECASE):
        return '7.x'
    if re.search(r'#Requires\s+-PSEdition\s+Core', content, re.IGNORECASE):
        return '7.x'
    if re.search(r'#Requires\s+-Version\s+5', content, re.IGNORECASE):
        return '5.1'
    if re.search(r'#Requires\s+-PSEdition\s+Desktop', content, re.IGNORECASE):
        return '5.1'
    # 默认使用 7.x 跨平台模式
    return '7.x'
```

PowerShell 端对应函数：
```powershell
function Get-Ps1TargetVersion {
    param([string]$Content)
    # 同上启发式规则检测
    ...
}
```

### 5. 向后兼容性保证

1. **默认参数不变**：所有新增参数均有默认值 `'auto'`，现有调用方无需任何修改
2. **`auto` 模式** 等价于 `'7.x'` 模式（跨平台全支持），与当前行为向后兼容
3. **位置语义不变**：BOM 采用动态跳过策略，返回位置始终相对于传入的原始 content 字符串，不做截断
4. **纯函数保证**：所有新增逻辑仍然保持纯函数特性，无副作用

## Implementation Plan

### 阶段一：核心基础增强
1. 在 `ps1_syntax.py` 中添加 `_preprocess_content()`、`_is_line_end()`、`_is_at_line_start()` 辅助函数
2. 修改 `_skip_ps1_here_string()` 使用新的换行符检测逻辑
3. 更新 `iter_code_chars()` 中的行注释/注释块检测使用新的换行符逻辑
4. 修改其他公开函数添加 `target_version` 参数

### 阶段二：版本检测工具
5. 实现 `detect_ps_version_from_content()` 自动检测函数
6. PowerShell 端实现 `Get-Ps1TargetVersion` 函数

### 阶段三：PowerShell 端对齐
7. 在 `encoding-safety.ps1` 中实现所有新增辅助函数
8. 更新所有相关 PowerShell 函数添加 `-TargetVersion` 参数
9. 确保双端逻辑完全对齐

### 阶段四：测试覆盖
10. 在 `ps1_test_cases.py` 中新增跨平台测试用例：
    - UTF-8 BOM 头场景（3个：BOM+here-string、BOM+正常代码、BOM+空文件）
    - CR-only 换行场景（2个：CR换行here-string、混合CR/CRLF）
    - 无 trailing newline 场景（2个：末尾直接结束标记、末尾直接结束标记+EOF）
    - 版本检测场景（4个：各版本声明检测、自动变量检测）
11. 运行双端测试验证全部通过
12. 更新版本号到 1.1.0

## Test Scenarios

### 新增测试用例清单

| ID | 场景 | 类型 | 说明 |
|----|------|------|------|
| `hs_bom_double` | BOM+双引号here-string | BOM | `\ufeff@"\n...\n"@` BOM在文件开头不影响here-string识别 |
| `hs_bom_single` | BOM+单引号here-string | BOM | 同上但单引号 |
| `hs_bom_normal_code` | BOM+普通代码 | BOM | BOM不影响括号深度计算和插入点查找 |
| `hs_cr_only_newline` | CR-only换行here-string | 换行符 | `@"\rline1\r"@` 老式Mac风格 |
| `hs_mixed_crlf_lf` | 混合CRLF/LF换行 | 换行符 | 同一文件中混用两种换行符 |
| `hs_mixed_cr_crlf` | 混合CR/CRLF换行 | 换行符 | 极端混合场景 |
| `hs_no_trailing_newline_eof` | EOF无换行结束 | 边界 | 结束标记"@在文件最后两个字符 |
| `hs_no_trailing_newline_eof_single` | 单引号EOF无换行 | 边界 | 同上但单引号 |
| `ver_detect_requires_7` | `#Requires -Version 7` 检测 | 版本检测 | 正确识别为7.x |
| `ver_detect_requires_5` | `#Requires -Version 5.1` 检测 | 版本检测 | 正确识别为5.1 |
| `ver_detect_pwtcore` | `#Requires -PSEdition Core` 检测 | 版本检测 | 正确识别为7.x |
| `ver_detect_iswindows` | `$IsWindows` 变量检测 | 版本检测 | 正确识别为7.x |

## Acceptance Criteria

1. ✅ 所有原有 70 个测试用例继续通过（无回归）
2. ✅ 新增 12 个跨平台测试用例双端全部通过
3. ✅ 含 BOM 的 PS1 文件能正确识别 here-string 和括号深度
4. ✅ CR-only 换行符文件能正确解析
5. ✅ 混合换行符文件能正确解析
6. ✅ 无 trailing newline 的 here-string 能正确识别结束标记
7. ✅ 版本自动检测函数对各种声明的识别准确率 100%
8. ✅ 默认调用方式（不传 target_version）行为与 v1.0.0 完全兼容
9. ✅ Python 端版本号更新为 `__version__ = "1.1.0"`
10. ✅ PowerShell 端版本号更新为 `$script:EncodingSafetyVersion = '1.1.0'`