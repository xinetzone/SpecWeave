# 建立Windows pwsh7脚本统一规范 - 验证检查清单

## 代码与工具验证
- [x] 版本校验代码块在PowerShell 5.1中能正确检测并输出友好错误（exit code=1）
- [x] 版本校验代码块在pwsh 7.4+中能静默通过
- [x] 版本校验代码块不使用pwsh7专属语法（兼容5.1解析）
- [x] 标准脚本模板包含完整的版本声明、校验块、推荐设置
- [x] Python检查脚本check-pwsh7-compliance.py能正确识别#Requires -Version 5.x为违规
- [x] Python检查脚本能正确识别#Requires -Version 7.x为合规
- [x] Python检查脚本正确跳过vendor/、.venv/、__pycache__/、.temp/、playground/、.git/、.trae/目录
- [x] Python检查脚本正确识别# PWSH7-EXEMPT:豁免标记
- [x] Python检查脚本--warn-only模式违规时返回exit code=0
- [x] Python检查脚本--strict模式违规时返回exit code=1
- [x] Python检查脚本扫描完整项目耗时小于5秒
- [x] ci-check.ps1已集成pwsh7检查步骤
- [x] ci-check初始使用warn-only模式不阻塞CI
- [x] migrate-to-pwsh7.py（如实现）--dry-run模式不修改文件

## 文档验证
- [x] global-core-rules.md已添加pwsh7强制规范条目
- [x] ONBOARDING.md已添加pwsh7安装命令和验证方法
- [x] VS Code配置（.vscode/settings.json）已设置默认终端为pwsh
- [x] .vscode/extensions.json推荐PowerShell扩展
- [x] 文档说明清晰，无歧义
- [x] 安装命令可直接复制执行（winget install Microsoft.PowerShell）

## 迁移验证
- [x] 所有项目自有.ps1脚本已添加#Requires -Version 7.0（或已豁免）
- [x] 所有#Requires -Version 5.1声明已替换或豁免
- [x] 关键脚本（ci-check.ps1等）人工验证功能正常
- [x] 运行check-pwsh7-compliance.py无#Requires相关违规

## 流程与规范验证
- [x] standards-tools/README.md已登记本spec
- [x] 全局specs/README.md看板已更新
- [x] 例外审批机制文档化（# PWSH7-EXEMPT:格式说明）
- [x] 过渡期warn-only时间窗口已记录（建议2周）
- [x] 未来切换到--strict模式的TODO标记已添加
