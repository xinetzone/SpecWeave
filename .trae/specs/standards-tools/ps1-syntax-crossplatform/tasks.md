# 实现任务清单

## 阶段一：核心基础增强
- [ ] T1: 在 ps1_syntax.py 中添加 `_skip_bom()` 辅助函数（动态BOM跳过）
- [ ] T2: 在 ps1_syntax.py 中添加 `_is_line_end()` 和 `_is_at_line_start()` 辅助函数
- [ ] T3: 修改 `_skip_ps1_here_string()` 使用新的换行符检测逻辑，支持 target_version 参数
- [ ] T4: 更新 `iter_code_chars()` 中的注释/字符串处理使用新的换行符逻辑
- [ ] T5: 更新 `find_top_level_insert_point()` 添加 target_version 参数
- [ ] T6: 更新 `calc_brace_depth()` 添加 target_version 参数
- [ ] T7: 更新 `find_non_whitespace()` 和 `skip_line_comments()` 使用新的换行符逻辑

## 阶段二：版本检测工具
- [ ] T8: 实现 `detect_ps_version_from_content()` 自动版本检测函数
- [ ] T9: PowerShell端实现 `Get-Ps1TargetVersion` 函数

## 阶段三：PowerShell端对齐
- [ ] T10: 在 encoding-safety.ps1 中添加 `Skip-Ps1Bom` 函数（动态BOM跳过）
- [ ] T11: 在 encoding-safety.ps1 中添加换行符检测辅助函数（`Test-Ps1LineEnd`、`Test-Ps1AtLineStart`）
- [ ] T12: 更新 `Skip-Ps1HereString` 添加 -TargetVersion 参数
- [ ] T13: 更新 `Find-NonWhitespace`、`Get-Ps1BraceDepth`、`Skip-Ps1LineComments`、`Find-Ps1TopLevelInsertPoint` 等函数添加 -TargetVersion 参数
- [ ] T14: 确保双端逻辑完全对齐

## 阶段四：测试与发布
- [ ] T15: 在 ps1_test_cases.py 中新增12个跨平台测试用例
- [ ] T16: 重新生成 ps1_syntax_cases.json 测试数据
- [ ] T17: 运行Python端pytest验证所有用例通过
- [ ] T18: 运行PowerShell端统一测试验证所有用例通过
- [ ] T19: 更新版本号到1.1.0（Python + PowerShell）
- [ ] T20: 更新测试报告文档