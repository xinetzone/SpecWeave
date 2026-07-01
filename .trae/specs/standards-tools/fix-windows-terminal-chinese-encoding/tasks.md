---
version: 1.0
date: 2026-07-01
category: standards-tools
---

# Windows终端中文编码彻底修复 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建编码诊断脚本 check-encoding.ps1
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建PowerShell诊断脚本，一键检测当前终端编码健康状态
  - 检测项包括：活动代码页(chcp)、Console Input/OutputEncoding、$OutputEncoding、Python stdout编码、Git编码配置、环境变量(PYTHONIOENCODING/PYTHONUTF8)
  - 输出彩色健康报告（绿色✅正常/黄色⚠️警告/红色❌异常），并给出具体修复建议
  - 支持-json参数输出结构化JSON结果，便于自动化检查
  - 脚本保存为 `.agents/scripts/check-encoding.ps1`（UTF-8 BOM + CRLF编码）
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-1.1: 脚本在代码页936环境下运行能正确识别出GBK编码问题
  - `programmatic` TR-1.2: 脚本在UTF-8环境下运行能报告所有项正常
  - `programmatic` TR-1.3: -json参数输出为有效JSON格式，包含所有检测字段
  - `programmatic` TR-1.4: 脚本在PowerShell 5.1和PowerShell 7+下均能正常运行
  - `human-judgement` TR-1.5: 报告清晰易读，问题项附带具体修复命令
- **Notes**: 使用.agents/scripts/lib/powershell.py的write_ps1_script()写入，确保UTF-8 BOM+CRLF

## [x] Task 2: 创建项目级PowerShell配置文件 profile.ps1
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建项目级PowerShell Profile，启动时自动设置UTF-8编码
  - 设置项包括：chcp 65001 > $null、[Console]::OutputEncoding = [System.Text.Encoding]::UTF8、[Console]::InputEncoding = [System.Text.Encoding]::UTF8、$OutputEncoding = [System.Text.Encoding]::UTF8
  - 设置PYTHONIOENCODING=utf-8和PYTHONUTF8=1环境变量
  - 显示编码设置成功的提示信息
  - 脚本保存为 `.agents/scripts/profile.ps1`
  - 同时创建一个`Install-Profile.ps1`帮助用户将项目Profile添加到PowerShell Profile中（点源加载）
- **Acceptance Criteria Addressed**: [AC-1, AC-3]
- **Test Requirements**:
  - `programmatic` TR-2.1: 点源加载profile.ps1后，chcp返回65001
  - `programmatic` TR-2.2: 加载后[Console]::OutputEncoding.WebName为utf-8
  - `programmatic` TR-2.3: 加载后Python sys.stdout.encoding为utf-8
  - `programmatic` TR-2.4: print("中文✅测试")无异常无乱码
  - `human-judgement` TR-2.5: Install-Profile.ps1能正确指导用户完成配置，且配置可持久化
- **Notes**: 注意chcp 65001在PowerShell中需要用cmd /c chcp 65001执行

## [x] Task 3: 创建CMD AutoRun配置脚本 setup-cmd-utf8.ps1
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建PowerShell脚本，配置CMD的AutoRun注册表项，使CMD启动时自动执行chcp 65001
  - 支持用户级(HKCU)和系统级(HKLM)配置，默认使用用户级（无需管理员权限）
  - 创建卸载选项(undo)，可恢复原始配置
  - 注册表路径：HKCU:\Software\Microsoft\Command Processor\AutoRun
  - 备份原始AutoRun值，避免覆盖用户已有配置
  - 脚本保存为 `.agents/scripts/setup-cmd-utf8.ps1`
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-3.1: 脚本执行后注册表AutoRun项包含chcp 65001
  - `programmatic` TR-3.2: undo参数可恢复原始配置
  - `programmatic` TR-3.3: 已有AutoRun配置时不会覆盖，而是追加chcp命令
  - `human-judgement` TR-3.4: 脚本有清晰的确认提示和操作结果反馈
- **Notes**: 使用&连接多条AutoRun命令；需要提醒用户重启CMD生效

## [x] Task 4: 创建统一环境初始化脚本 setup-utf8-env.ps1
- **Priority**: high
- **Depends On**: [Task 1, Task 2, Task 3]
- **Description**: 
  - 创建一键式环境初始化脚本，按以下顺序引导用户完成配置：
    1. 运行check-encoding.ps1诊断当前状态
    2. 询问配置范围（仅当前会话/用户级/系统级）
    3. 设置环境变量（PYTHONIOENCODING、PYTHONUTF8）
    4. 调用setup-cmd-utf8.ps1配置CMD AutoRun
    5. 提示如何将profile.ps1添加到PowerShell Profile
    6. 可选：提供Git编码配置命令
    7. 运行验证测试，确认配置生效
  - 支持-WhatIf预览模式，显示将要执行的操作但不实际修改
  - 脚本保存为 `setup-utf8-env.ps1`（项目根目录）
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-5]
- **Test Requirements**:
  - `programmatic` TR-4.1: -WhatIf模式下不修改任何配置，仅输出计划
  - `programmatic` TR-4.2: "仅当前会话"选项立即生效但不持久化
  - `programmatic` TR-4.3: 用户级配置后环境变量在新PowerShell窗口中依然存在
  - `human-judgement` TR-4.4: 脚本引导流程清晰，用户可根据提示做出选择
  - `programmatic` TR-4.5: 完成配置后自动运行验证，所有检查项通过

## [x] Task 5: 配置Python项目级UTF-8默认值
- **Priority**: medium
- **Depends On**: None
- **Description**: 
  - 在项目根目录创建或更新 `pth` 文件或sitecustomize.py，确保在项目目录下运行Python时默认启用UTF-8模式
  - 更新 `.agents/scripts/` 下所有Python脚本，在shebang后统一添加编码设置（使用已有的三层防御体系，检查是否有遗漏）
  - 在pytest.ini中添加环境变量配置：`python_files = test_*.py` 和 `env = PYTHONIOENCODING=utf-8 PYTHONUTF8=1`
  - 添加 `.env` 文件（如不存在）包含PYTHONIOENCODING=utf-8和PYTHONUTF8=1
  - 更新ci-check.ps1和ci-check.sh，在执行测试前设置UTF-8编码
- **Acceptance Criteria Addressed**: [AC-3, AC-6]
- **Test Requirements**:
  - `programmatic` TR-5.1: 在项目目录下运行pytest时，所有测试输出中文正常
  - `programmatic` TR-5.2: 直接运行任一.agents/scripts/下的Python脚本，中文输出正常
  - `programmatic` TR-5.3: ci-check.ps1执行时中文和emoji状态标记正确显示
  - `programmatic` TR-5.4: 现有282+个测试全部通过，无回归

## [x] Task 6: 创建编码验证测试脚本 verify-encoding.ps1
- **Priority**: medium
- **Depends On**: [Task 1, Task 2, Task 3]
- **Description**: 
  - 创建全面的验证脚本，测试各类场景下的中文显示：
    - 直接Write-Host中文和emoji
    - Python脚本print中文和emoji
    - Python管道输出到PowerShell
    - Get-Content读取中文Markdown文件
    - git log中文提交信息
    - cmd /c echo中文
    - 运行项目脚本（check-links.py、ci-check.ps1等）的中文输出
  - 每个测试项返回PASS/FAIL状态
  - 脚本保存为 `.agents/scripts/verify-encoding.ps1`
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-5, AC-6, AC-7, AC-10]
- **Test Requirements**:
  - `programmatic` TR-6.1: UTF-8环境下所有测试项返回PASS
  - `programmatic` TR-6.2: GBK环境下能正确识别出失败项
  - `programmatic` TR-6.3: 脚本退出码：全部通过返回0，有失败返回1
  - `human-judgement` TR-6.4: 测试输出清晰，每项测试有明确的输入和实际输出对比

## [x] Task 7: 更新知识库文档 - Windows终端UTF-8配置完整指南
- **Priority**: high
- **Depends On**: [Task 1, Task 2, Task 3, Task 4, Task 5, Task 6]
- **Description**: 
  - 创建新的知识库文档 `docs/knowledge/operations/windows-terminal-utf8-complete-guide.md`
  - 文档结构：
    1. 问题根源：为什么Windows终端会乱码（四层问题分析）
    2. 快速诊断：运行check-encoding.ps1
    3. 一键配置：运行setup-utf8-env.ps1
    4. 系统级配置（可选，需重启）：启用"Beta: Unicode UTF-8提供全球语言支持"
    5. PowerShell配置：profile.ps1使用指南
    6. CMD配置：AutoRun设置说明
    7. Python环境变量配置
    8. Git for Windows编码配置
    9. Trae IDE终端配置
    10. Windows Terminal配置（可选）
    11. 验证配置：运行verify-encoding.ps1
    12. 常见问题FAQ（如某些旧软件不兼容UTF-8如何回退）
    13. 故障排查：常见乱码场景与解决方案
  - 更新现有文档 `docs/knowledge/operations/windows-powershell-pipe-utf8.md`，添加指向新指南的链接
  - 文档使用Markdown格式，包含具体命令和配置示例
- **Acceptance Criteria Addressed**: [AC-8, AC-9]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 文档结构清晰，新手可按步骤30分钟内完成配置
  - `programmatic` TR-7.2: 文档中所有命令均可执行，无错误命令
  - `human-judgement` TR-7.3: 包含系统级/用户级/项目级三种配置方案，用户可按需选择
  - `programmatic` TR-7.4: 按文档操作后verify-encoding.ps1所有测试通过
  - `human-judgement` TR-7.5: FAQ覆盖常见问题（如chcp 65001导致的批处理问题、旧GBK程序兼容等）
- **Notes**: 参考Microsoft官方文档关于Windows代码页和UTF-8支持的说明

## [x] Task 8: 更新standards-tools主题README和spec索引
- **Priority**: medium
- **Depends On**: [Task 7]
- **Description**: 
  - 更新 `.trae/specs/standards-tools/README.md`，添加新spec的看板条目
  - 更新 `.trae/specs/README.md` 全局看板，更新统计数据
  - 在docs/knowledge/README.md中添加新文档索引
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-8.1: 主题README中spec计数正确
  - `programmatic` TR-8.2: 全局看板统计数字更新
  - `human-judgement` TR-8.3: 索引链接可正常跳转

## [x] Task 9: 实际验证与端到端测试
- **Priority**: high
- **Depends On**: [Task 4, Task 6, Task 7]
- **Description**: 
  - 在当前Windows环境下实际执行setup-utf8-env.ps1进行完整配置
  - 重启终端后验证所有设置持久化
  - 打开新的PowerShell窗口、CMD窗口分别验证
  - 在Trae IDE内置终端中验证
  - 运行项目的完整测试套件（pytest）确保无回归
  - 运行ci-check.ps1确保中文输出正常
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10]
- **Test Requirements**:
  - `programmatic` TR-9.1: 新PowerShell窗口chcp为65001，Python编码为utf-8
  - `programmatic` TR-9.2: 新CMD窗口chcp为65001
  - `programmatic` TR-9.3: verify-encoding.ps1所有测试项PASS
  - `programmatic` TR-9.4: pytest全量测试通过（282+个用例）
  - `programmatic` TR-9.5: check-encoding.ps1所有检查项绿色✅
  - `human-judgement` TR-9.6: Trae IDE终端中中文和emoji显示清晰正确
