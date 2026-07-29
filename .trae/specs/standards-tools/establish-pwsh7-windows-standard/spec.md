---
id: "establish-pwsh7-windows-standard"
title: "建立Windows pwsh7脚本统一规范"
source: "用户需求 + 七概念方法论(F→V→I)分析"
x-toml-ref: "../../.meta/toml/.trae/specs/standards-tools/establish-pwsh7-windows-standard/spec.toml"
---

# 建立Windows pwsh7脚本统一规范 - Product Requirement Document

## Overview
- **Summary**: 为SpecWeave项目建立强制性Windows脚本规范，要求所有项目自有Windows PowerShell脚本统一使用pwsh7（PowerShell 7.4+ LTS）执行、开发、测试和部署，严禁使用Windows PowerShell 5.1。规范包含脚本头部版本声明、运行时版本校验、友好错误引导、CI门禁检查、开发者环境配置指南等完整保障体系。
- **Purpose**: 解决Windows平台PowerShell版本碎片化问题（5.1 vs 7.x），消除因版本差异导致的脚本语法不兼容、行为不一致、CI/CD失败等问题；为开发者提供明确的版本要求和便捷的环境配置指引；建立可自动化验证的CI门禁，确保规范强制执行而非仅文档约定。
- **Target Users**: SpecWeave项目所有开发者（包括AI智能体协作者）、CI/CD流水线维护者、项目新人Onboarding。

## Goals
- 所有项目自有.ps1脚本头部统一添加`#Requires -Version 7.0`和自定义pwsh版本校验逻辑
- 提供标准脚本模板，预置版本检测、友好错误提示、安装引导
- 建立CI自动化检查脚本，不合规脚本阻塞PR合并
- 在AGENTS.md和相关文档中明确标注pwsh7技术要求
- 提供VS Code推荐配置，默认终端使用pwsh7
- 现有脚本分批迁移完成，消除`#Requires -Version 5.1`等错误声明

## Non-Goals (Out of Scope)
- 不修改vendor/目录下的第三方脚本（git submodule）
- 不修改.venv/、__pycache__/、.temp/等临时/虚拟环境目录下的自动生成脚本
- 不强制要求pwsh7跨平台兼容（Linux/macOS可使用bash），但脚本应尽量考虑跨平台
- 不立即强制迁移所有现有脚本（提供warn-only过渡期）
- 不负责安装pwsh7到用户机器（仅提供安装指引）

## Background & Context
- **现状问题**：项目中已有数十个.ps1脚本分散在.agents/scripts/、apps/*/、scripts/等目录，部分脚本（如[build.ps1](file:///d:/spaces/SpecWeave/apps/pytorch-base/build.ps1#L1-L1)）头部声明`#Requires -Version 5.1`，明确要求旧版本，这与未来统一使用pwsh7的目标冲突
- **版本差异**：PowerShell 5.1（Windows自带，基于.NET Framework）与PowerShell 7（pwsh，基于.NET Core/8+）存在大量语法和行为差异：
  - pwsh7新特性：`??`/`??=`空合并运算符、三元运算符`?:`、`ForEach-Object -Parallel`、`ConvertFrom-Json -Depth`支持更高深度、`$PSNativeCommandErrorActionPreference`等
  - 5.1独有/差异：部分.NET Framework类型可用性、COM对象访问、WMI查询行为差异等
- **项目约束**：根据project_memory，项目要求使用WSL作为优先构建环境，但Windows原生脚本仍用于CI检查、开发辅助、Docker构建包装等场景
- **pwsh7版本选择**：选择pwsh 7.4作为最低版本要求，因为7.4是当前LTS版本，特性稳定，且包含重要的错误处理改进

## Functional Requirements
- **FR-1**: 脚本头部强制版本声明
  - 所有项目自有.ps1脚本必须在第一行（shebang/注释之后）包含`#Requires -Version 7.0`
  - 在`#Requires`之前必须包含自定义版本校验代码块，提供比默认错误更友好的用户体验
- **FR-2**: 自定义版本校验与友好引导
  - 脚本启动时检测：(1) 是否运行在pwsh Core环境（PSEdition -eq 'Core'），(2) 版本是否≥7.4
  - 检测失败时输出：当前版本信息、问题说明、安装命令（`winget install Microsoft.PowerShell`）、文档链接
  - 错误退出码统一为1
- **FR-3**: 标准脚本模板
  - 在.agents/templates/下提供标准pwsh7脚本模板
  - 模板包含：版本校验块、ErrorActionPreference设置、UTF-8编码设置、结构化日志参考
- **FR-4**: CI自动化检查脚本
  - 编写Python检查脚本check-pwsh7-compliance.py，扫描指定目录下的.ps1文件
  - 检查项：(1) 是否包含`#Requires -Version 7.x`，(2) 是否包含自定义版本校验逻辑，(3) 是否存在`#Requires -Version 5.1`等违规声明
  - 支持--warn-only模式（过渡期使用，不阻塞）和--strict模式（正式期阻塞）
- **FR-5**: 文档更新
  - 在AGENTS.md或global-core-rules.md中添加pwsh7强制规范说明
  - 在开发环境配置指南中添加pwsh7安装步骤
  - 在README或ONBOARDING.md中提及pwsh7要求
- **FR-6**: VS Code推荐配置
  - 提供.vscode/settings.json推荐配置，将默认终端设置为pwsh
  - 配置PowerShell扩展使用pwsh7
- **FR-7**: 例外审批机制
  - 确实无法迁移到pwsh7的特殊脚本，允许在脚本头部注释中说明原因，格式为`# PWSH7-EXEMPT: <原因>`
  - 检查脚本识别此注释并跳过检查

## Non-Functional Requirements
- **NFR-1**: 性能：CI检查脚本扫描整个项目（不含排除目录）应在5秒内完成
- **NFR-2**: 可靠性：版本检测逻辑必须可靠，不能误报也不能漏报；检测代码自身必须兼容pwsh7
- **NFR-3**: 可用性：错误提示必须对新手友好，直接给出复制即可用的安装命令
- **NFR-4**: 可维护性：检查脚本和模板应易于更新，版本要求变更时只需修改一处
- **NFR-5**: 向后兼容：过渡期（至少2周）内CI检查使用warn-only模式，不阻塞现有PR

## Constraints
- **Technical**: 
  - 检查脚本使用Python编写（与现有.agents/scripts/下的检查脚本风格一致）
  - 版本校验PowerShell代码必须同时能在5.1和7中运行（否则在5.1中会直接报错无法给出友好提示）
  - 排除目录固定为：vendor/、.venv/、venv/、__pycache__/、.temp/、playground/
- **Business**:
  - 不能破坏现有CI/CD流水线的稳定性
  - 迁移成本可控，优先使用批量修改+脚本自动化
- **Dependencies**:
  - 依赖现有ci-check.ps1作为CI入口
  - 依赖现有Python脚本库（.agents/scripts/lib/）

## Assumptions
- 开发者机器可以安装pwsh7（Windows 10 1607+或Windows 11均支持）
- CI环境（GitHub Actions等）可以安装或预装pwsh7
- 现有脚本中pwsh7不兼容语法的数量不多，可逐个修复
- winget在Windows 11和更新的Windows 10上默认可用，旧版本用户可使用其他安装方式

## Acceptance Criteria

### AC-1: 版本声明规范
- **Given**: 一个项目自有.ps1脚本文件
- **When**: 脚本被检查
- **Then**: 脚本包含`#Requires -Version 7.x`声明，且不存在`#Requires -Version 5`或更低版本声明
- **Verification**: `programmatic`（检查脚本验证）
- **Notes**: x为0或更大，推荐7.4

### AC-2: 自定义版本校验存在
- **Given**: 一个项目自有.ps1脚本文件
- **When**: 脚本被检查
- **Then**: 脚本包含PSEdition/PSVersion检测逻辑和友好错误提示
- **Verification**: `programmatic`（检查脚本通过AST或正则验证关键模式存在）

### AC-3: 友好错误提示
- **Given**: 在Windows PowerShell 5.1中运行一个合规脚本
- **When**: 脚本启动
- **Then**: 脚本输出明确的错误信息，包含当前版本、所需版本、安装命令，并以exit code 1退出
- **Verification**: `programmatic`（测试脚本在5.1中运行验证行为）

### AC-4: CI集成
- **Given**: CI运行ci-check.ps1
- **When**: 存在不合规脚本（非warn-only模式）
- **Then**: CI检查失败退出，阻止PR合并
- **Verification**: `programmatic`（CI运行验证）

### AC-5: 检查范围正确
- **Given**: vendor/、.venv/等目录下的第三方/临时脚本
- **When**: 运行检查脚本
- **Then**: 这些脚本被自动跳过，不产生误报
- **Verification**: `programmatic`（检查脚本验证排除列表）

### AC-6: 例外机制有效
- **Given**: 一个带有`# PWSH7-EXEMPT: 原因说明`注释的脚本
- **When**: 运行检查脚本
- **Then**: 该脚本被豁免，不产生合规错误
- **Verification**: `programmatic`（检查脚本识别豁免标记）

### AC-7: 文档完整
- **Given**: 项目规范文档
- **When**: 新开发者阅读入门文档
- **Then**: 文档明确说明pwsh7要求、安装步骤、VS Code配置
- **Verification**: `human-judgment`（文档审查）

### AC-8: 模板可用
- **Given**: 新创建的pwsh7脚本
- **When**: 使用标准模板创建
- **Then**: 模板自动预置版本声明、校验逻辑、推荐设置
- **Verification**: `human-judgment`（创建新脚本验证模板完整性）

## Open Questions
- [ ] 是否需要将pwsh7检查添加到pre-commit钩子？还是仅CI检查即可？
- [ ] 过渡期warn-only持续多长时间合适？（建议2周）
- [ ] apps/下各子项目的脚本是否需要单独配置，还是统一遵循根规范？
- [ ] 是否需要提供一个一键迁移脚本，自动为现有脚本添加版本声明和校验块？
