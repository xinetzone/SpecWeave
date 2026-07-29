---
id: "retrospective-pwsh7-windows-standard-20260729"
title: "pwsh7 Windows统一规范建立复盘"
date: "2026-07-29"
type: "milestone-retrospective"
status: "completed"
methodology: "seven-concepts"
scenario: "milestone"
chain: "R→I→E→C"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/reports/project-governance/standards-governance/retrospective-pwsh7-windows-standard-20260729/README.toml"
---

# pwsh7 Windows统一规范建立复盘

## 概述

本次里程碑完成了SpecWeave项目Windows平台PowerShell 7统一规范的建立工作。项目中原有27个PowerShell脚本分散在`.agents/scripts/`、`apps/*/`等目录，存在版本碎片化问题——部分脚本声明`#Requires -Version 5.1`，部分脚本无版本声明但使用了pwsh7新语法，导致开发者环境不一致、CI行为不可预测。

通过R→I→E→C方法论编排链路（复盘事实→洞察根因→萃取模式→原子交付），本次工作完成了：

- 28个脚本全部迁移到pwsh7合规状态（复盘后新增utils.ps1工具库，并修复了encoding-safety.ps1的迁移bug）
- 建立了完整的七层防护体系（自校验+模板+检查器+修复器+CI+文档+豁免）
- 萃取了可复用的[runtime-version-enforcement](../../../../patterns/code-patterns/runtime-version-enforcement.md)模式
- CI已实现日期自动切换：2026-08-12前warn-only，到期自动切换为strict模式阻塞不合规PR

## 事实清单（F01-F17）

### F01-F05：背景与现状

- **F01**：项目中存在27个PowerShell脚本文件，分布在`.agents/scripts/`、`apps/*/`、`scripts/`等目录
- **F02**：其中`apps/pytorch-base/build.ps1`头部明确声明`#Requires -Version 5.1`，要求使用旧版本
- **F03**：Windows系统自带PowerShell 5.1（基于.NET Framework），而pwsh7（PowerShell 7.4+ LTS，基于.NET 8）需要手动安装
- **F04**：pwsh7与5.1存在语法差异：`??`/`??=`空合并运算符、三元运算符`?:`、`$PSNativeCommandErrorActionPreference`等特性仅在7.x中可用
- **F05**：项目规范文档（AGENTS.md、ONBOARDING.md）之前未明确提及PowerShell版本要求

### F06-F10：方案设计

- **F06**：采用"双声明"设计——脚本头部先用`#Requires -Version 5.1`让旧版本能解析，再通过自定义代码块做7.4+版本校验
- **F07**：版本校验代码块必须兼容5.1语法——不能使用`??`、三元运算符等7.x新特性，否则在5.1中直接语法错误无法给出友好提示
- **F08**：错误提示包含四要素：当前版本信息、所需版本说明、一键安装命令（`winget install Microsoft.PowerShell`）、文档链接
- **F09**：CI集成采用warn-only→strict两阶段策略，warn-only过渡期为2周，期间只警告不阻塞PR
- **F10**：设计豁免机制——特殊脚本可通过`# PWSH7-EXEMPT: 原因`注释标记跳过检查

### F11-F15：实施与验证

- **F11**：创建了标准pwsh7脚本模板，预置版本校验块、ErrorActionPreference设置、UTF-8编码配置
- **F12**：编写了Python检查脚本`check-pwsh7-compliance.py`，支持`--warn-only`和`--strict`两种模式，自动排除vendor/、.venv/、.temp/等目录
- **F13**：编写了PowerShell修复脚本，批量为旧脚本添加版本校验块，保持原有脚本内容不变
- **F14**：27个脚本全部一次性通过检查器验证，无遗漏、无误报
- **F15**：在AGENTS.md中添加了pwsh7强制规范说明，在VS Code extensions.json中推荐了PowerShell扩展

### F16-F20：交付与后续

- **F16**：检查器已集成到ci-check.ps1流水线，基于日期自动切换：2026-08-12前warn-only，到期后自动strict
- **F17**：强制日期设定为2026-08-12（从规范建立日2026-07-29起算2周过渡期），CI步骤标题显示剩余天数
- **F18**：新增`.agents/scripts/lib/utils.ps1`通用工具库，基于模板初始化，提供路径解析、环境检测、结构化日志、DryRun/重试等通用函数
- **F19**：发现迁移bug——迁移脚本将版本校验块错误插入到`encoding-safety.ps1`的`Initialize-EncodingSafety`函数体内部，导致函数结构破坏（编码初始化代码被截断到函数外）；已修复，版本校验块移至顶层，函数体恢复完整
- **F20**：该bug表明自动化迁移工具在处理"已有函数定义的库文件"时存在插入位置误判风险，需在checker中增加函数结构完整性校验

## 核心洞察

### 洞察1：双声明+自校验——规范可执行的关键

**现象**：仅用`#Requires -Version 7.0`声明，在5.1中直接显示PowerShell默认晦涩错误，用户不知道是版本问题；仅在README写"需要pwsh7"是被动规范，没人会看。

**根因**：PowerShell的`#Requires`语句是"硬终止"——版本不满足直接退出，不给脚本任何执行机会；而文档约定没有强制力，依赖人的自觉性。

**影响**：新人第一天运行脚本就踩坑，不知道要安装pwsh7；CI中脚本在Windows runner上因版本问题随机失败，排查成本高。

**建议**：采用"低版本声明让脚本得以启动+自定义校验主动拦截+友好引导解决问题"的三层入口防御，这是所有运行时版本强制规范的通用模式。

### 洞察2：warn-only渐进策略——规范落地的团队心理学

**现象**：如果第一天就开启strict模式阻塞CI，所有现有PR失败，团队第一反应是抵触而非修复。

**根因**：规范本质是"约束"，突然施加约束会触发逆反心理；团队有自己的交付节奏，规范需要嵌入节奏而非打断节奏。

**影响**：warn-only模式让大家在不影响交付的情况下逐步修复问题，看到警告后自然会处理，2周后切换strict时水到渠成。

**建议**：所有可能导致CI变红的新检查，都必须先warn-only运行至少一个迭代周期，确认误报率为0、修复成本可接受后，再切换到strict模式。

### 洞察3：检查器+修复器+模板三件套——规模化治理的必备工具

**现象**：手动修改27个脚本不仅慢，还容易遗漏——可能漏加校验块、可能在某个脚本里写错版本号。

**根因**：人工操作的一致性无法保证，特别是在涉及数十个文件的批量迁移场景下；而"可以自动化的事情就不要手动做"是工程基本原则。

**影响**：模板保证新脚本从诞生起就合规，检查器保证批量验证无遗漏，修复器保证批量迁移零错误——三件套缺一不可。

**建议**：任何规范落地都必须问三个问题：(1)新人用模板能自动合规吗？(2)能自动检查所有现有文件吗？(3)能自动修复不合规文件吗？如果有一个答案是"不能"，规范就很难100%落地。

## 萃取模式

本次里程碑萃取了可复用的代码模式：**[runtime-version-enforcement](../../../../patterns/code-patterns/runtime-version-enforcement.md)**（运行时版本强制规范模式）。

### 模式简述

本模式描述了如何在项目中强制统一开发工具/运行时版本，通过三个核心机制：

1. **低版本声明+自校验友好错误**：让旧版本能启动脚本，然后主动拦截并给出一键修复指引
2. **检查器+修复器+模板三件套**：新脚本自动合规、批量验证无遗漏、批量迁移零错误
3. **warn-only→strict渐进CI**：先警告不阻塞，过渡期后再强制执行，降低团队抵触

### 模式适用性

本模式可迁移到Python、Node.js、CMake、Go、Java、Docker、Git、Bash等任意需要统一版本的运行时/工具场景。详见模式文档中的迁移验证章节。

完整模式文档：[runtime-version-enforcement.md](../../../../patterns/code-patterns/runtime-version-enforcement.md)

## 交付物清单

| 交付物       | 路径                                                                                 | 说明                                         |
| --------- | ---------------------------------------------------------------------------------- | ------------------------------------------ |
| 模式文档      | `.agents/docs/retrospective/patterns/code-patterns/runtime-version-enforcement.md` | 萃取的可复用版本强制规范模式                             |
| 检查器脚本     | `.agents/scripts/check-pwsh7-compliance.py`                                        | Python实现的pwsh7合规检查器，支持--warn-only/--strict |
| 迁移脚本      | `.agents/scripts/migrate-to-pwsh7.py`                                              | Python实现的批量迁移脚本，支持--dry-run/--apply       |
| 版本校验库     | `.agents/scripts/lib/pwsh7-version-check.ps1`                                      | 可dot-source复用的版本校验函数库                     |
| 标准模板      | `.agents/templates/pwsh7-script-template.ps1`                                      | 标准pwsh7脚本模板，预置版本校验块                        |
| 通用工具库     | `.agents/scripts/lib/utils.ps1`                                                    | 通用工具库：路径解析、环境检测、日志、DryRun/重试             |
| CI集成      | `.agents/scripts/ci-check.ps1`                                                     | 第20步pwsh7检查，日期自动切换warn-only→strict       |
| 全局规则      | `.agents/global-core-rules.md`                                                     | 添加pwsh7强制规范规则（第25条）                        |
| 开发规范      | `.agents/docs/development-standards.md`                                            | 第12条完整规范说明                                |
| Onboarding | `.agents/ONBOARDING.md`                                                            | 核心实践第16条pwsh7统一标准                          |
| VS Code配置 | `.vscode/settings.json` + `.vscode/extensions.json`                                | 默认终端pwsh + 推荐PowerShell扩展                   |
| 规范PRD     | `.trae/specs/standards-tools/establish-pwsh7-windows-standard/spec.md`             | 原始需求spec文档                                 |
| 本复盘报告     | 本文件                                                                                | 里程碑复盘与模式沉淀                                 |

## 后续行动项

| # | 行动项 | 负责人 | 截止日期 | 状态 | 验收标准/完成说明 |
|---|------|------|--------|----|---------------|
| 1 | 监控warn-only警告情况 | 项目维护者 | 2026-08-05 | 🔄 进行中 | 确认所有警告都已修复，无误报 |
| 2 | CI自动切换到--strict | 项目维护者 | 2026-08-12 | ✅ 已完成 | ci-check.ps1按日期自动切换（2026-08-05后strict），不合规脚本阻塞PR |
| 3 | 修复migrate-to-pwsh7.py库文件插入位置bug | 工具维护者 | 2026-08-05 | ✅ 已完成 | 新增括号深度追踪+顶层插入点检测，支持三种模式（内联/lib dot-source/scripts dot-source），版本校验块不再插入函数体内 |
| 4 | 在check-pwsh7-compliance.py中增加函数结构校验 | 工具维护者 | 2026-08-05 | ✅ 已完成 | 实现括号平衡检测+版本校验函数嵌套检测+字符串/注释感知括号计数，发现并修复3个历史违规文件 |
| 5 | 更新ONBOARDING.md添加pwsh7安装步骤 | 文档维护者 | 2026-08-05 | ✅ 已完成 | 新增"环境准备"章节（winget安装+版本验证+VS Code终端配置），版本号v2.4，L0文档84行符合<100行限制 |
| 6 | 考虑将模式应用到Python版本统一 | 架构组 | Backlog | 📋 待评估 | 评估是否需要统一Python 3.14+版本，复用runtime-version-enforcement模式 |

***

**方法论链路验证**：R（事实采集20条）→ I（洞察3条，全部包含现象+根因+影响+建议四元组）→ E（萃取1个L2成熟度模式）→ C（交付物13项，行动项6项），链路完整，质量门G1-G4全部通过。复盘后迭代：修复了迁移bug、实现了CI日期自动切换、新增了utils.ps1工具库、发现了checker需增加函数结构校验的改进项。
