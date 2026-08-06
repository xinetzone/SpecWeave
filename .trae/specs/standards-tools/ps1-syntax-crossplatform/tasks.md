# 实现任务清单

## v1.1.0 已完成

### 阶段一：核心基础增强（跨平台换行符 + BOM）
- [x] T1: 添加换行符检测和行首判定辅助函数（`_is_line_end()`、`_is_at_line_start()` Python 端；`Test-Ps1AtLineStart` PowerShell 端）
- [x] T2: 修改 `_skip_ps1_here_string()` 支持 CR/LF/CRLF 三种换行符
- [x] T3: 在 `_skip_ps1_here_string()` 中添加 UTF-8 BOM 自动跳过逻辑
- [x] T4: 更新 `find_non_whitespace()` 支持 BOM 跳过（Python + PowerShell 双端）
- [x] T5: 更新 `iter_code_chars()` 支持 BOM 跳过（Python 端）
- [x] T6: PowerShell 端 `Skip-Ps1HereString` 重构支持 CR/LF/CRLF + BOM
- [x] T7: 添加结构化日志埋点（`_trace_hs`/`_trace_newline`/`_trace_bom` 及 PowerShell 对应函数）

### 阶段二：测试覆盖与发布
- [x] T8: 在 `ps1_test_cases.py` 中新增 11 个跨平台测试用例（7 HereString + 4 InsertPoint）
- [x] T9: 重新生成 `ps1_syntax_cases.json` 测试数据（40 InsertPoint + 28 HereString 用例）
- [x] T10: 运行 Python 端 pytest 验证所有 78 个用例通过
- [x] T11: 运行 PowerShell 端统一测试验证所有 81 个用例通过
- [x] T12: 更新版本号到 1.1.0（Python `__version__` + PowerShell `$EncodingSafetyVersion`）
- [x] T13: 编写跨平台测试用例文档（CROSSPLATFORM_TEST_CASES.md）

### 提交记录
- commit `3f0f6024`: feat(ps1-syntax): PowerShell 7+ 跨平台支持（CR/LF/CRLF + UTF-8 BOM）

---

## v1.2.0 延期任务

### 版本感知参数
- [x] T14: 为所有公开解析函数添加 `target_version` 参数（`'5.1' | '7.x' | 'auto'`）
- [x] T15: PowerShell 端对应函数添加 `-TargetVersion` 参数
- [x] T16: 实现 `target_version='5.1'` 模式（仅 CRLF+LF，严格 Windows 兼容）

### 版本自动检测
- [x] T17: 实现 `detect_ps_version_from_content()` 自动版本检测函数（Python）
- [x] T18: 实现 `Get-Ps1TargetVersion` 版本检测函数（PowerShell）
- [x] T19: 添加版本检测测试用例（`#Requires -Version 7`/`5.1`、`$IsWindows` 等）

### 辅助函数完善
- [x] T20: `skip_line_comments()` 支持 CR-only 换行符的空行检测和注释终止
- [x] T21: `find_top_level_insert_point()` 行扫描逻辑支持 CR-only 空行
- [x] T22: PowerShell 端 `Skip-Ps1LineComments` 和 `Find-Ps1TopLevelInsertPoint` 同步更新

### 提交记录（v1.2.0）
- commit `e3201a52`: feat(ps1-syntax): add Ps1Version type and detect_ps_version_from_content()
- commit `bdd6cc41`: feat(ps1-syntax): add target_version param to _skip_ps1_here_string with 5.1/7.x newline modes
- commit `3901ccd0`: feat(ps1-syntax): add target_version to all public functions, CR support in skip_line_comments
- commit `03bbc629`: test(ps1-syntax): add VersionDetectCase, target_version tests, PS5.1 strict mode cases
- commit `117810ae`: feat(encoding-safety): add Get-Ps1TargetVersion and Resolve-Ps1TargetVersion functions
- commit `d3f486a2`: feat(encoding-safety): add -TargetVersion parameter to all core parsing functions
- commit `3d77bb69`: test(encoding-safety): add version detection and TargetVersion mode tests to PS runner
