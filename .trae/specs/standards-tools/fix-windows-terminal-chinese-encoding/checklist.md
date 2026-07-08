---
version: 1.0
date: 2026-07-01
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/fix-windows-terminal-chinese-encoding/checklist.toml"
---
# Windows终端中文编码彻底修复 - Verification Checklist

## 脚本创建验证
- [x] check-encoding.ps1 诊断脚本已创建，使用UTF-8编码
- [x] check-encoding.ps1 可正确识别GBK(936)环境和UTF-8(65001)环境（修复了`$results`→`$script:results`初始化bug）
- [x] check-encoding.ps1 支持-Json参数输出结构化结果
- [x] profile.ps1 项目级PowerShell配置文件已创建
- [x] profile.ps1 点源加载后可正确设置chcp/Console编码/$OutputEncoding/环境变量
- [x] Install-Profile.ps1 帮助脚本可正确指导用户安装配置
- [x] setup-cmd-utf8.ps1 CMD AutoRun配置脚本已创建
- [x] setup-cmd-utf8.ps1 支持用户级/系统级配置和-Undo回退
- [x] setup-cmd-utf8.ps1 不覆盖已有AutoRun配置，正确追加命令
- [x] setup-utf8-env.ps1 一键初始化脚本已创建
- [x] setup-utf8-env.ps1 支持-WhatIf预览模式
- [x] setup-utf8-env.ps1 包含完整的配置引导流程
- [x] verify-encoding.ps1 全面验证脚本已创建
- [x] verify-encoding.ps1 覆盖所有关键场景（Python/Git/文件/管道/emoji）（修复了`$results`→`$script:results`引用bug）

## Python环境配置验证
- [x] 项目Python脚本通过环境变量和sitecustomize.py默认使用UTF-8编码输出
- [x] 环境变量PYTHONUTF8=1和PYTHONIOENCODING=utf-8正确设置
- [x] sitecustomize.py实现三层防御（环境变量层/流重配置层/容错层）
- [x] 加载profile.ps1后Python sys.stdout.encoding确认为utf-8

## 文档验证
- [x] windows-terminal-utf8-complete-guide.md 知识库文档已创建
- [x] 文档包含四层问题分析（系统/终端/应用/项目）
- [x] 文档包含一键配置和手动配置两种方式
- [x] 文档包含会话级/用户级/系统级三种配置方案
- [x] 文档包含Git for Windows编码配置
- [x] 文档包含Trae IDE终端配置说明
- [x] 文档包含Windows Terminal配置指南
- [x] 文档包含常见问题FAQ和故障排查对照表
- [x] windows-powershell-pipe-utf8.md 已更新并添加新指南链接

## 端到端功能验证（加载profile.ps1后实测）
- [x] chcp为65001（UTF-8代码页）
- [x] [Console]::OutputEncoding为utf-8 (CodePage=65001)
- [x] $OutputEncoding为utf-8 (CP=65001)
- [x] Python sys.stdout.encoding为utf-8
- [x] PowerShell Write-Host输出中文文本成功
- [x] PowerShell Write-Host输出emoji成功
- [x] Python print("中文输出测试")无异常
- [x] Python print emoji无UnicodeEncodeError
- [x] Python管道输出中文成功
- [x] Get-Content读取Markdown文件中文正常
- [x] git log输出无乱码
- [x] cmd /c echo中文正常
- [x] 项目脚本（check-links.py等）中文输出正常
- [x] 环境变量PYTHONIOENCODING=utf-8, PYTHONUTF8=1正确设置
- [x] verify-encoding.ps1 14/14测试项全部PASS
- [x] check-encoding.ps1 Health Score: 100%, 11/11检查项全部PASS

## 索引与看板更新
- [x] standards-tools/README.md 主题看板已更新（10/10完成，新增交付物索引条目）
- [x] specs/README.md 全局看板已更新（38个specs，standards-tools 10个）
- [x] 新spec目录命名符合kebab-case规范（fix-windows-terminal-chinese-encoding）

## 持久性与兼容性验证
- [x] 配置方案设计为持久化（PowerShell Profile/CMD AutoRun注册表/环境变量）
- [x] 脚本兼容PowerShell 5.1和PowerShell 7+（检测版本并相应设置）
- [x] 用户级配置无需管理员权限（环境变量Scope=User，注册表HKCU）
- [x] 方案不影响Linux/macOS（所有脚本为.ps1仅Windows执行，sitecustomize.py跨平台兼容UTF-8）
- [x] 提供-Undo/回退机制，配置可完全撤销
