# 验收检查清单

## v1.1.0 验收（已通过 ✅）

### 功能正确性
- [x] 所有原有 67 个测试用例继续通过（无回归）
- [x] 新增 11 个跨平台测试用例双端全部通过
- [x] UTF-8 BOM 头文件正确解析（here-string/括号深度/插入点均不受影响）
- [x] CR-only (`\r`) 换行符 here-string 正确解析
- [x] 混合 CRLF/LF/CR 换行符 here-string 正确解析（`hs_skip_mixed_newlines_cr_lf`）
- [x] CR 换行下缩进结束标记不关闭 here-string（`hs_skip_cr_indented_end`）
- [x] CR 换行下反引号转义正常工作（`hs_skip_cr_with_backtick_escape`）
- [x] BOM + CRLF（Windows 默认编码）组合场景正确处理（`hs_skip_bom_crlf`）
- [x] BOM + param here-string 默认值场景正确处理（`hs_bom_param_default`）
- [x] CR 换行函数体内 here-string 括号深度正确（`hs_cr_in_function`）

### 向后兼容性
- [x] 不传任何新参数时行为正确（API 签名完全向后兼容）
- [x] 三种换行符（LF/CRLF/CR）默认全部支持，无需额外配置
- [x] 所有公开 API 签名保持不变
- [x] 纯函数特性保持（无副作用、无全局状态）
- [x] 位置语义不变（BOM 动态跳过，返回位置始终相对于原始 content）

### 双端对齐
- [x] Python 端和 PowerShell 端对相同输入产生完全一致的解析结果
- [x] JSON 测试用例导出/导入正确（40 InsertPoint + 28 HereString = 68 用例）
- [x] 版本号同步更新（`__version__ = "1.1.0"` / `$EncodingSafetyVersion = '1.1.0'`）
- [x] 日志函数双端对齐（`_trace_hs`/`Write-Ps1TraceHs` 等）
- [x] BOM 处理逻辑双端一致（均仅在位置0跳过 `\ufeff`/`0xFEFF`）

### 测试结果
- [x] Python 端：78 个用例全部通过（pytest）
- [x] PowerShell 端：81 个用例全部通过（test_ps1_syntax_unified.ps1）
- [x] 双端测试共享同一 JSON 数据源

---

## v1.2.0 验收（已通过 ✅）

### 版本感知参数
- [x] `target_version` 参数在 `_skip_ps1_here_string`/`iter_code_chars`/`find_top_level_insert_point`/`calc_brace_depth` 中正确传递
- [x] PowerShell 端 `-TargetVersion` 参数对应实现（9 个函数）
- [x] `target_version='5.1'` 严格模式（仅 CRLF+LF，不接受 CR-only）
- [x] `target_version='auto'` 自动检测换行符类型
- [x] 默认值 `'auto'` 保持向后兼容

### 版本自动检测
- [x] `detect_ps_version_from_content()` 对 `#Requires -Version 7` 正确返回 `'7.x'`
- [x] 对 `#Requires -Version 5.1` 正确返回 `'5.1'`
- [x] 对 `#Requires -PSEdition Core` 正确返回 `'7.x'`
- [x] 对 `$IsWindows/$IsLinux/$IsMacOS` 自动变量正确返回 `'7.x'`
- [x] 对 `??`/`??=` 运算符特征正确返回 `'7.x'`
- [x] PowerShell 端 `Get-Ps1TargetVersion` 与 Python 端行为一致（10/10 用例对齐）

### 辅助函数完善
- [x] `skip_line_comments()` 空行检测支持 CR（版本感知分支处理）
- [x] `skip_line_comments()` 行注释终止支持 CR（while 循环条件版本感知）
- [x] `find_top_level_insert_point()` 行扫描支持 CR-only 空行
- [x] PowerShell 端对应函数同步更新
- [x] 新增 CR 换行注释场景测试用例（TargetVersion Mode Tests）

### 代码质量
- [x] 新增函数均有完整的 docstring/注释块
- [x] 版本感知换行检测逻辑统一使用版本分支（5.1: CRLF+LF; 7.x: CRLF+LF+CR）
- [x] 所有接受空字符串的 PowerShell 参数均有 `[AllowEmptyString()]`
- [x] 版本号双端同步更新至 1.2.0

### 双端对齐
- [x] JSON 测试用例导出/导入包含 `version_detect_cases`（10 个）
- [x] `here_string_cases` 包含 `target_version` 字段（默认 `'auto'`）
- [x] Python 端 98 个、PowerShell 端 101 个测试全部通过（共 199 个）
- [x] 版本检测用例双端结果完全一致
