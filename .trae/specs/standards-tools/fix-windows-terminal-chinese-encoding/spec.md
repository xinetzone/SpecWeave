---
version: 1.0
date: 2026-07-01
category: standards-tools
status: draft
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/fix-windows-terminal-chinese-encoding/spec.toml"
---
# Windows终端中文编码彻底修复 - Product Requirement Document

## Overview
- **Summary**: 系统性解决Windows终端环境下中文显示乱码问题，从系统设置、终端配置、项目脚本、环境变量、文档指南五个层面建立完整的UTF-8编码支持体系，确保中文文本在CMD、PowerShell、Trae IDE终端、WSL等各类终端环境中均能正确显示，彻底消除GBK编码导致的中文乱码问题。
- **Purpose**: 当前项目环境中Windows终端活动代码页为936(GBK)，控制台编码为GB2312，与Python默认编码、PowerShell输出编码(UTF-8)存在不一致，导致Git输出、脚本运行日志、中文文档查看等场景出现乱码。现有方案仅在Python代码层面做了防御性处理（三层防御体系），但未从终端环境根源解决问题。
- **Target Users**: SpecWeave项目开发者、在Windows环境下使用本项目的贡献者、使用Trae IDE进行开发的用户。

## Goals
- 将Windows终端默认代码页从936(GBK)切换为65001(UTF-8)并持久化
- 统一PowerShell控制台输入/输出编码为UTF-8，消除$OutputEncoding与Console编码不一致问题
- 配置Python环境变量(PYTHONIOENCODING/PYTHONUTF8)确保所有Python脚本默认使用UTF-8
- 创建项目级PowerShell配置文件和环境初始化脚本，新用户开箱即用
- 提供完整的系统级UTF-8启用指南（Windows Beta: Unicode UTF-8支持）
- 建立自动化编码诊断与验证脚本，一键检测终端编码健康状态
- 更新知识库文档，沉淀Windows终端编码配置最佳实践
- 在CMD、PowerShell 5.x、PowerShell 7+、Trae IDE终端四类环境中验证中文显示正确性

## Non-Goals (Out of Scope)
- 不修改WSL Linux子系统内部的编码配置（WSL默认UTF-8，无需修复）
- 不强制用户修改系统区域设置为"英语(美国)"等非中文区域
- 不修改Git for Windows的核心代码（仅配置其编码相关选项）
- 不解决第三方终端软件（如Windows Terminal、ConEmu等）的专有配置问题，仅提供通用配置指南
- 不对历史提交中的乱码文件进行修复（仅防止未来出现乱码）

## Background & Context

### 当前诊断结果（2026-07-01）
| 配置项 | 当前值 | 问题 |
|--------|--------|------|
| CMD活动代码页(chcp) | 936 (GBK) | ❌ 非UTF-8，不支持emoji和全量Unicode |
| [Console]::OutputEncoding | GB2312 (CP936) | ❌ 与Python/现代工具输出不一致 |
| [Console]::InputEncoding | GB2312 (CP936) | ❌ 中文输入可能被错误解码 |
| $OutputEncoding | UTF-8 (CP65001) | ⚠️ 与Console编码不一致，管道操作易乱码 |
| Python sys.stdout.encoding | gbk | ❌ print含emoji时UnicodeEncodeError |
| 系统区域 | zh-CN | ✅ 正常，无需修改 |

### 已有防护层（代码层面）
- `.agents/scripts/lib/cli.py`：三层防御体系（入口编码设置+防御性TTY检测+安全符号选择）
- `.agents/scripts/lib/powershell.py`：.ps1脚本UTF-8 BOM+CRLF编码处理
- `docs/knowledge/operations/windows-powershell-pipe-utf8.md`：PowerShell管道UTF-8注意事项
- `docs/retrospective/patterns/code-patterns/cross-platform-encoding-enforcement.md`：跨平台编码强制模式

### 问题层级分析
乱码问题涉及四个层级，需逐层解决：
1. **系统层**：Windows ANCI代码页默认为GBK，非Unicode程序使用GBK
2. **终端层**：CMD/PowerShell启动时默认代码页936，编码设置不持久
3. **应用层**：Python/Git等工具默认跟随系统编码，输出GBK
4. **项目层**：缺少统一的环境初始化脚本和配置检查机制

## Functional Requirements
- **FR-1**: 创建项目级PowerShell配置文件(`profile.ps1`)，启动时自动设置UTF-8编码
- **FR-2**: 创建CMD自动运行脚本，通过注册表AutoRun将chcp 65001持久化
- **FR-3**: 创建环境初始化脚本(`setup-utf8-env.ps1`)，一键配置系统/用户/项目三级环境变量
- **FR-4**: 创建编码诊断脚本(`check-encoding.ps1`/`check-encoding.py`)，一键检测终端编码健康状态
- **FR-5**: 配置项目级Python启动默认参数(-X utf8)和环境变量(PYTHONIOENCODING=utf-8)
- **FR-6**: 提供Windows系统级"Beta: Unicode UTF-8支持"启用指南
- **FR-7**: 编写Git for Windows编码配置指南（i18n.commitencoding等）
- **FR-8**: 创建Trae IDE终端编码配置说明
- **FR-9**: 更新知识库文档，补充完整的Windows终端编码配置最佳实践
- **FR-10**: 创建验证测试脚本，覆盖CMD/PowerShell/Trae终端/python输出/git日志等场景

## Non-Functional Requirements
- **NFR-1**: 配置持久性：终端重启后编码设置依然生效，不需要每次手动chcp
- **NFR-2**: 无副作用：启用UTF-8后不影响现有GBK文件的正常读取和编辑
- **NFR-3**: 向后兼容：旧脚本在UTF-8环境下仍能正常运行（通过errors=replace降级）
- **NFR-4**: 一键验证：诊断脚本可在10秒内完成所有编码检查项并输出清晰报告
- **NFR-5**: 跨版本兼容：支持PowerShell 5.1(Windows自带)和PowerShell 7+
- **NFR-6**: 文档完整性：配置步骤包含截图/命令/验证方法，新手可按步骤操作

## Constraints
- **Technical**: Windows 10/11环境，PowerShell 5.1默认预装，PowerShell 7+可选安装；不依赖管理员权限即可完成用户级配置；项目脚本需兼容现有Python 3.8+环境
- **Business**: 配置方案不能影响项目CI/CD流水线（Linux/macOS环境默认UTF-8，无需修改）
- **Dependencies**: Windows注册表访问（CMD AutoRun配置）、PowerShell Profile执行策略需允许

## Assumptions
- 用户使用Windows 10 1903+或Windows 11，支持"Beta: Unicode UTF-8提供全球语言支持"功能
- 用户PowerShell执行策略允许运行本地脚本(RemoteSigned或Unrestricted)
- Python已通过python.org或Microsoft Store安装，且在PATH中
- Git for Windows已安装并配置在PATH中
- Trae IDE使用内置终端或系统PowerShell

## Acceptance Criteria

### AC-1: PowerShell启动后默认使用UTF-8编码
- **Given**: 已执行项目环境初始化脚本
- **When**: 打开新的PowerShell窗口
- **Then**: chcp显示65001，[Console]::OutputEncoding为UTF-8，$OutputEncoding为UTF-8
- **Verification**: `programmatic`
- **Notes**: 同时验证PowerShell 5.1和PowerShell 7+

### AC-2: CMD启动后默认代码页为65001
- **Given**: 已配置CMD AutoRun注册表项
- **When**: 打开新的CMD窗口
- **Then**: chcp显示活动代码页65001
- **Verification**: `programmatic`

### AC-3: Python默认使用UTF-8输出
- **Given**: 已配置PYTHONIOENCODING和PYTHONUTF8环境变量
- **When**: 在终端运行`python -c "import sys; print(sys.stdout.encoding)"`
- **Then**: 输出为utf-8，且print("中文✅")无乱码无异常
- **Verification**: `programmatic`

### AC-4: 诊断脚本可正确检测编码问题
- **Given**: 终端编码配置存在问题（如代码页936）
- **When**: 运行check-encoding诊断脚本
- **Then**: 脚本能够识别出所有编码问题，给出具体的修复建议，输出清晰的健康报告
- **Verification**: `programmatic`
- **Notes**: 包括代码页、Console编码、Python编码、Git编码等检查项

### AC-5: Git日志中文显示正常
- **Given**: Git已配置i18n编码选项
- **When**: 在含中文提交信息的仓库中运行git log
- **Then**: 中文提交信息正确显示，无乱码
- **Verification**: `programmatic`

### AC-6: 项目脚本中文输出无乱码
- **Given**: 终端已配置为UTF-8
- **When**: 运行项目中任一Python脚本（如ci-check.ps1、check-links.py）
- **Then**: 中文输出和emoji状态标记正确显示
- **Verification**: `programmatic`

### AC-7: 中文文档内容查看正常
- **Given**: 终端已配置为UTF-8
- **When**: 使用type/cat/Get-Content查看Markdown文件
- **Then**: 中文字符正确显示，无乱码
- **Verification**: `programmatic`

### AC-8: 知识库文档完整清晰
- **Given**: 用户按照知识库文档操作
- **When**: 按步骤完成所有配置
- **Then**: 可以在30分钟内完成从诊断到验证的完整流程，且所有AC-1到AC-7均通过
- **Verification**: `human-judgment`
- **Notes**: 文档包含系统级/用户级/项目级三个层级的配置方案，用户可根据权限选择

### AC-9: Trae IDE终端中文显示正常
- **Given**: Trae IDE终端使用系统PowerShell配置
- **When**: 在Trae IDE内置终端中运行命令和脚本
- **Then**: 中文输出和emoji正确显示
- **Verification**: `human-judgment`

### AC-10: 管道操作中文不被污染
- **Given**: 终端已配置为UTF-8
- **When**: 执行含中文输出的管道命令（如python script.py | Select-Object ...）
- **Then**: 管道传递后的中文内容仍正确，无转码污染
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要为项目提供一个统一的启动脚本（如`start-dev.ps1`），在启动开发环境前自动设置编码？
- [ ] 是否需要将编码检查纳入CI流水线？（Windows runner上的编码验证）
- [ ] Windows Terminal（Windows 11默认终端）是否需要单独的配置指南？
