---
id: "establish-pwsh7-windows-standard-tasks"
title: "建立Windows pwsh7脚本统一规范 - 任务分解"
source: "spec.md 功能需求分解"
---

# 建立Windows pwsh7脚本统一规范 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 编写pwsh7版本校验代码块（PowerShell模板片段）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 编写可在PowerShell 5.1和pwsh7中都能运行的版本检测代码片段
  - 检测PSEdition是否为Core（即pwsh），检测版本是否≥7.4
  - 检测失败时输出：当前版本信息、问题说明、安装命令（winget install Microsoft.PowerShell）、参考文档提示
  - 退出码统一为1
  - 代码必须简洁，可被其他脚本dot-source引用或直接复制粘贴
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-1.1: 在PowerShell 5.1中运行，代码正确检测并输出友好错误，exit code=1
  - `programmatic` TR-1.2: 在pwsh 7.4+中运行，代码静默通过（不输出错误）
  - `human-judgement` TR-1.3: 错误提示清晰，包含可直接复制的安装命令
- **Notes**: 代码不能使用pwsh7专属语法（如??、三元运算符），否则在5.1中会解析失败

## [x] Task 2: 创建标准pwsh7脚本模板
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在.agents/templates/目录下创建pwsh7-script-template.ps1模板文件
  - 模板包含：版本校验块（Task1成果）、#Requires -Version 7.0声明、$ErrorActionPreference = "Stop"设置、UTF-8编码配置、注释头说明、示例参数解析、示例日志函数
  - 模板注释说明每个部分的作用
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgement` TR-2.1: 模板结构清晰，注释完整
  - `programmatic` TR-2.2: 基于模板创建的新脚本能通过后续的合规性检查
  - `programmatic` TR-2.3: 模板在pwsh7中可正常加载（语法正确）

## [x] Task 3: 编写Python合规性检查脚本 check-pwsh7-compliance.py
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在.agents/scripts/目录下创建check-pwsh7-compliance.py
  - 实现目录扫描功能，自动跳过排除目录：vendor/、.venv/、venv/、__pycache__/、.temp/、playground/、.git/、.trae/
  - 检查项：
    1. 是否存在`#Requires -Version 5`或更低版本声明（违规）
    2. 是否存在`#Requires -Version 7.x`声明（必需）
    3. 是否包含版本校验关键代码模式（如`PSEdition`或`PSVersionTable.PSVersion`检测）
    4. 是否存在`# PWSH7-EXEMPT:`豁免标记（豁免则跳过其他检查）
  - 支持命令行参数：--path指定扫描路径、--warn-only仅警告不失败、--strict严格模式
  - 输出清晰的错误报告：违规文件路径、行号、问题描述
  - 退出码：0=全部合规或仅警告，1=存在违规
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: 正确识别`#Requires -Version 5.1`为违规
  - `programmatic` TR-3.2: 正确识别`#Requires -Version 7.0`为合规声明
  - `programmatic` TR-3.3: 正确跳过vendor/、.venv/等排除目录
  - `programmatic` TR-3.4: 正确识别`# PWSH7-EXEMPT:`注释并豁免该文件
  - `programmatic` TR-3.5: --warn-only模式下违规不返回失败退出码
  - `programmatic` TR-3.6: 扫描完整项目耗时<5秒

## [x] Task 4: 将pwsh7检查集成到ci-check.ps1
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 修改.agents/scripts/ci-check.ps1，在现有检查步骤中添加pwsh7合规性检查
  - 初始阶段使用--warn-only模式（过渡期），不阻塞CI
  - 预留切换到--strict模式的位置（注释标记TODO）
  - 参考现有其他检查步骤的输出格式，保持一致的UI风格
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 运行ci-check.ps1时pwsh7检查步骤被执行
  - `programmatic` TR-4.2: warn-only模式下即使发现违规CI也能继续完成其他检查
  - `human-judgement` TR-4.3: 检查输出格式与其他步骤一致，用户体验统一

## [x] Task 5: 更新全局规范文档（global-core-rules.md 和 ONBOARDING.md）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在.agents/global-core-rules.md中添加pwsh7强制规范规则，说明：
    - Windows脚本必须使用pwsh7（7.4+）
    - 禁止使用Windows PowerShell 5.1
    - 脚本必须包含版本声明和校验块
    - 例外审批机制
  - 在.agents/ONBOARDING.md中添加：
    - pwsh7安装命令（winget install Microsoft.PowerShell）
    - 验证安装方法（pwsh --version）
    - VS Code配置说明
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-5.1: 规范文档清晰明确，没有歧义
  - `human-judgement` TR-5.2: Onboarding文档提供一步到位的安装命令
  - `programmatic` TR-5.3: 文档交叉引用正确

## [x] Task 6: 添加VS Code推荐配置
- **Priority**: medium
- **Depends On**: None
- **Description**: 
  - 创建或更新.vscode/settings.json（如果已存在则合并配置）
  - 配置默认终端为pwsh："terminal.integrated.defaultProfile.windows": "PowerShell"
  - 确保PowerShell扩展使用pwsh7作为默认版本
  - 创建.vscode/extensions.json推荐安装PowerShell扩展
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-6.1: 配置符合VS Code规范，无语法错误
  - `programmatic` TR-6.2: JSON文件可被正确解析

## [x] Task 7: 批量迁移现有项目自有脚本（第一阶段：添加#Requires声明）
- **Priority**: medium
- **Depends On**: Task 1, Task 3
- **Description**: 
  - 扫描项目，列出所有项目自有.ps1脚本（排除vendor/、.venv/等）
  - 为每个脚本添加`#Requires -Version 7.0`声明
  - 替换现有`#Requires -Version 5.1`为`#Requires -Version 7.0`
  - 注意：此阶段暂不添加完整版本校验块（留给后续任务或PR）
  - 对于明确无法迁移的脚本，添加`# PWSH7-EXEMPT:`注释说明原因
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-7.1: 迁移后运行check-pwsh7-compliance.py，#Requires相关违规数量为0
  - `human-judgement` TR-7.2: 迁移未破坏脚本原有功能（人工审查关键脚本）

## [x] Task 8: 编写一键迁移辅助脚本（可选）
- **Priority**: low
- **Depends On**: Task 1, Task 3
- **Description**: 
  - 编写一个Python脚本migrate-to-pwsh7.py，自动为现有合规（已有#Requires但无校验块）的脚本插入版本校验代码块
  - 脚本支持--dry-run模式预览变更
  - 自动识别脚本结构，在合适位置插入代码（#Requires之后、其他代码之前）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-8.1: --dry-run模式不修改任何文件
  - `programmatic` TR-8.2: 迁移后脚本语法正确
  - `human-judgement` TR-8.3: 插入位置合理，不破坏原有代码结构

## [x] Task 9: 更新standards-tools主题README和全局specs看板
- **Priority**: medium
- **Depends On**: None
- **Description**: 
  - 更新.trae/specs/standards-tools/README.md，添加本spec条目
  - 更新.trae/specs/README.md全局看板，登记本spec
  - 标记为"已完成"
- **Acceptance Criteria Addressed**: （流程性任务）
- **Test Requirements**:
  - `programmatic` TR-9.1: README文件正确更新，链接有效
  - `human-judgement` TR-9.2: 看板状态与实际进度一致
