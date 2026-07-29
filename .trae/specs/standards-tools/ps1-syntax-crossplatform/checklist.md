# 验收检查清单

## 功能正确性
- [ ] 所有原有 70 个测试用例继续通过（无回归）
- [ ] 新增 12 个跨平台测试用例双端全部通过
- [ ] UTF-8 BOM 头文件正确解析（here-string/括号深度/插入点均不受影响）
- [ ] CR-only (`\r`) 换行符文件正确解析
- [ ] 混合 CRLF/LF/CR 换行符文件正确解析
- [ ] 无 trailing newline 的 here-string 在 EOF 处正确识别结束标记
- [ ] 版本自动检测对 `#Requires -Version 7` 正确返回 7.x
- [ ] 版本自动检测对 `#Requires -Version 5.1` 正确返回 5.1
- [ ] 版本自动检测对 `#Requires -PSEdition Core` 正确返回 7.x
- [ ] 版本自动检测对 `$IsWindows/$IsLinux/$IsMacOS` 正确返回 7.x

## 向后兼容性
- [ ] 不传 target_version 参数时行为与 v1.0.0 完全一致
- [ ] target_version='auto' 等价于跨平台全支持模式
- [ ] 所有公开 API 签名保持向后兼容（仅新增可选参数）
- [ ] 纯函数特性保持（无副作用、无全局状态）

## 双端对齐
- [ ] Python端和PowerShell端对相同输入产生完全一致的解析结果
- [ ] JSON 测试用例导出/导入正确
- [ ] 版本号同步更新（__version__ / $EncodingSafetyVersion）

## 代码质量
- [ ] 新增函数均有完整的 docstring/注释块
- [ ] 代码风格与现有代码保持一致
- [ ] 无硬编码的换行符检测，统一使用 `_is_line_end()` 辅助函数
- [ ] 所有接受空字符串的 PowerShell 参数均有 `[AllowEmptyString()]`