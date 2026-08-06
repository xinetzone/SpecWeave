# Changelog

All notable changes to the PS1 Syntax Cross-Platform Parsing Library will be documented in this file.

---

## [1.2.0] - 2026-07-29

### 🚀 新增功能：版本感知 API

**版本自动检测与目标版本参数**

v1.2.0 引入了版本感知能力，解决了 v1.1.0 中"一刀切"将所有脚本视为 PS7+ 跨平台模式的问题。现在库可以根据脚本特征自动推断目标 PowerShell 版本，也支持显式指定版本以获得严格模式行为。

- **Python 端**：新增 [`detect_ps_version_from_content()`](lib/ps1_syntax.py#L36) 函数，基于启发式规则从脚本内容自动推断目标 PowerShell 版本
- **Python 端**：新增 [`_resolve_target_version()`](lib/ps1_syntax.py#L72) 内部函数，统一处理 `'5.1'`/`'7.x'`/`'auto'` 三种模式的版本解析
- **PowerShell 端**：新增 [`Get-Ps1TargetVersion`](lib/encoding-safety.ps1) 函数，Python 端逻辑的对等实现
- **PowerShell 端**：新增 `Resolve-Ps1TargetVersion` 函数，`-TargetVersion` 参数的统一解析入口
- 所有核心解析函数（共 9 个 Python 函数 + 9 个 PowerShell 函数）均新增 `target_version` / `-TargetVersion` 参数，默认值 `'auto'` 保持向后兼容

**版本检测启发式规则**（优先级从高到低）：

1. `#Requires -Version N` → N≥7 返回 `'7.x'`，N≥5 返回 `'5.1'`
2. `#Requires -PSEdition Core` → `'7.x'`，`#Requires -PSEdition Desktop` → `'5.1'`
3. PS7+ 自动变量（`$IsWindows`/`$IsLinux`/`$IsMacOS`/`$IsCoreCLR`）→ `'7.x'`
4. PS7+ 运算符（`??`/`??=`/`?.`）→ `'7.x'`
5. 无任何特征时默认返回 `'7.x'`（跨平台优先策略）

### 🐛 跨平台兼容性修复

**CR-only 换行符处理盲区修复**

v1.1.0 虽然在 here-string 原语 `_skip_ps1_here_string` / `Skip-Ps1HereString` 中添加了 CR-only 换行支持，但以下辅助函数仍存在 CR 换行处理盲区：

| 函数 | 问题 | 修复方式 |
|------|------|---------|
| `skip_line_comments` / `Skip-Ps1LineComments` | 空行检测仅识别 LF，遇到 CR 换行的空行会误判为非空行导致位置偏移 | 添加版本感知分支：5.1 模式仅检测 `\n`/`\r\n`，7.x 模式增加 `\r` 单字符换行检测 |
| `skip_line_comments` 注释终止条件 | while 循环在行尾判断时，CR 单字符换行不被识别为行尾，导致注释内容"吞掉"下一行代码 | 版本感知的行尾判定，CRLF 优先匹配避免双行首误判 |
| `find_top_level_insert_point` / `Find-Ps1TopLevelInsertPoint` | 行扫描过程中空行检测同样缺少 CR 支持 | 通过 `skip_line_comments` 的修复间接解决，版本参数完整传递调用链 |

**PS5.1 严格模式换行策略**

在 `target_version='5.1'` 模式下，库严格遵循 Windows PowerShell 5.1 的行为：
- 仅识别 CRLF（`\r\n`）和 LF（`\n`）作为有效换行符
- CR-only（`\r`，老式 Mac 换行）不被识别为换行，here-string 终止符 `"@`/`'@` 必须在标准换行后才能正确识别
- 这确保了面向 Windows PowerShell 5.1 的脚本不会因 CR 换行而产生错误的解析结果

### 🔧 API 变更

所有核心函数签名新增 `target_version` 参数（默认 `'auto'`，完全向后兼容）：

**Python 端**（`lib/ps1_syntax.py`）：

| 函数 | 新增参数 |
|------|---------|
| `_skip_ps1_here_string()` | `target_version: str = 'auto'` |
| `iter_code_chars()` | `target_version: str = 'auto'` |
| `iter_code_chars_no_comments()` | `target_version: str = 'auto'` |
| `find_non_whitespace()` | `target_version: str = 'auto'` |
| `skip_line_comments()` | `target_version: str = 'auto'` |
| `skip_whitespace_and_comments()` | `target_version: str = 'auto'` |
| `find_param_block_end()` | `target_version: str = 'auto'` |
| `find_top_level_insert_point()` | `target_version: str = 'auto'` |
| `_calc_brace_depth()` | `target_version: str = 'auto'` |

**PowerShell 端**（`lib/encoding-safety.ps1`）：

| 函数 | 新增参数 |
|------|---------|
| `Skip-Ps1HereString` | `-TargetVersion [string]` |
| `Find-NonWhitespace` | `-TargetVersion [string]` |
| `Skip-Ps1LineComments` | `-TargetVersion [string]` |
| `Skip-WhitespaceAndComments` | `-TargetVersion [string]` |
| `Find-Ps1ParamBlockEnd` | `-TargetVersion [string]` |
| `Find-Ps1TopLevelInsertPoint` | `-TargetVersion [string]` |
| `Get-Ps1BraceDepth` | `-TargetVersion [string]` |
| `Add-Ps1CodeAtTopLevel` | `-TargetVersion [string]` |

### 🧪 测试覆盖

新增 21 个测试用例（从 v1.1.0 的 178 个增至 199 个）：

- **10 个版本自动检测用例**：覆盖 `#Requires -Version`、`#Requires -PSEdition`、`$IsWindows`、`$IsLinux`、`??` 运算符、默认 7.x 等场景
- **3 个 PS5.1 严格模式 here-string 用例**：验证 CR-only 在 5.1 模式下被拒绝、CRLF 在 5.1 模式下正常工作
- **7 个 TargetVersion 模式测试**：验证显式指定版本覆盖内容检测、auto 模式自动检测、CR 在不同模式下的行为差异
- **1 个 PS 端版本检测+TargetVersion 集成测试段**：PowerShell 统一测试运行器新增两个测试段

测试结果：**Python 98 个 + PowerShell 101 个 = 199/199 全部通过**。

### 📊 变更统计

```
6 files changed, 849 insertions(+), 140 deletions(-)
```

- `lib/ps1_syntax.py`：+160/-56 行（版本检测函数、target_version 参数传递、CR 注释支持）
- `lib/encoding-safety.ps1`：+241/-63 行（PS 端版本检测、-TargetVersion 参数、CR 支持）
- `lib/ps1_test_cases.py`：+100 行（VersionDetectCase 数据类、版本检测用例）
- `tests/test_ps1_syntax.py`：+57/-3 行（版本检测测试、TargetVersion 模式测试）
- `tests/test_ps1_syntax_unified.ps1`：+137/-2 行（PS 端版本检测和 TargetVersion 测试段）
- `tests/ps1_syntax_cases.json`：+154/-16 行（JSON 测试数据更新）

---

## [1.1.0] - 2026-07-29

### 🚀 新增功能：跨平台换行符支持

- 新增 UTF-8 BOM（`\xEF\xBB\xBF`）自动跳过能力
- 在 `_skip_ps1_here_string()` 中统一支持三种换行符：LF（`\n`，Linux/macOS）、CRLF（`\r\n`，Windows）、CR（`\r`，老式 Mac）
- 新增 `_is_line_end()` 和 `_is_at_line_start()` 辅助函数
- 新增结构化日志埋点（`_trace_hs`/`_trace_newline`/`_trace_bom`）
- 版本号更新至 1.1.0
- 新增 11 个跨平台测试用例
- 测试结果：Python 78 个 + PowerShell 81 个全部通过

---

## [1.0.0] - 2026-07-28

### 🎉 初始发布

- here-string 解析核心逻辑（`_skip_ps1_here_string`/`Skip-Ps1HereString`）
- 括号深度计算（`_calc_brace_depth`/`Get-Ps1BraceDepth`）
- 顶层插入点检测（`find_top_level_insert_point`/`Find-Ps1TopLevelInsertPoint`）
- 代码插入功能（`Add-Ps1CodeAtTopLevel`）
- 双端（Python/PowerShell）共享 JSON 测试用例
- 41 个基础测试用例全部通过
