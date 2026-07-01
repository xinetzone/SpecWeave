# 项目知识库

## 统计摘要

- **总条目数**：24

| 分类 | 数量 |
|------|------|
| architecture | 1 |
| best-practices | 1 |
| decisions | 1 |
| learning | 6 |
| operations | 6 |
| troubleshooting | 3 |
| unknown | 6 |

## 按类别浏览

### architecture

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md) | SpecWeave项目治理方法论体系的架构总览文档，定义了治理基建四层递进核心模型，以及围绕该模型形成的5个可复用元洞察模式，包含模式间关系、落地状态和自反性验证案例。 | 2026-06-30 | governance、architecture、methodology、stage-guardrails、patterns、four-layer-model、governance-loop、retrospective、meta-insights |

### best-practices

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Mermaid 图表操作指南](best-practices/mermaid-guide.md) | SpecWeave 项目中 Mermaid 图表的一站式操作手册，涵盖起步模板、安全编码六规则、自动化检查工具详解、渲染问题排查流程和不同图表类型注意事项。 | 2026-06-29 | mermaid、图表、可视化、check-mermaid、安全编码、六规则、模板、ci |

### decisions

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md) | 记录将第三方依赖目录从 libs/ 重命名为 vendor/ 的架构决策及其理由 | 2026-06-23 | architecture、naming、directory、vendor、convention |

### learning

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Claude Tag 文章知识捕获](learning/claude-tag-article.md) | 捕获量子位 2026-06-24 文章《刚刚，Claude Code大升级！卡帕西：LLM第三次变革》核心内容：Anthropic 发布企业协作工具 Claude Tag，定位为 Claude Code 进化，强调团队共享、主动介入（Ambient Mode）、异步执行，卡帕西称其为 LLM 用户界面第三次重大变革。 | 2026-06-29 | claude、tag、anthropic、agent、enterprise、slack、ambient-mode、opus、karpathy、llm、协作、知识沉淀 |
| [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md) | TuyaOpen 是涂鸦开源的跨平台、跨芯片、跨操作系统的 AI-IoT SDK，核心目标是用一套灵活的 C/C++ SDK，结合涂鸦云的低延迟多模态 AI 能力，简化开放式 AI-IoT 生态的搭建。 | 2026-06-30 | tuya、tuyaopen、iot、sdk、ai、embedded、c、cpp、mcu、esp32、mcp、cloud、tkl、tal、tdd、tdl |
| [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md) | TuyaOpen-dev-skills 是面向 TuyaOpen 硬件开发流程的 AI Skills 仓库，以“最小 SKILL.md + references/ 按需加载 + scripts/ 可执行脚本”的三分结构，把环境搭建、编译、代码检查、烧录监控与调试闭环规范化。 | 2026-06-30 | tuya、tuyaopen、skills、agent-skills、cursor、claude、iot、embedded、workflow、ci |
| [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md) | 针对 .temp/libs/TuyaOpen 工作区的可执行学习路线：先跑通 LINUX target 构建闭环，再进入硬件烧录与 AI 智能体硬件能力区。 | 2026-06-30 | tuyaopen、learning-path、iot、embedded、sdk、cli、tos |
| [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md) | 基于 .temp/libs/WSL 源码（src/windows/wslc/ + doc/docs/）深度核实的 WSL CLI 命令树、参数定义、CLI 架构四层模型与官方架构 Mermaid 源图。修正先前学习计划中关于 CLI 命令短形态的误判——list/remove 才是主名，ls/ps/rm/delete 是别名。补充 interop binfmt 机制、systemd 启动流程、wslservice COM 接口、mini_init 多通道拓扑等技术细节。所有信息均有源码文件锚点可追溯。 | 2026-07-01 | wsl、wslc、cli、command-tree、argument-definitions、architecture、mermaid、interop、systemd、wslservice、com、binfmt、hvsocket、source-verification |
| [WSL 系统学习计划](learning/wsl-learning-plan.md) | 基于 .temp/libs/WSL 源码 + wsl.dev 开发者文档 + learn.microsoft.com 官方文档制定的系统学习计划，涵盖 Windows/Linux 三层架构、Linux 侧核心进程（mini_init/init/plan9/gns/relay）、Plan9/DrvFs 文件系统互操作、WSLC Container API 三语言投影（C/C#/C++ WinRT）、CMake 跨编译构建、组策略与诊断调试，包含 5 个实操练习、官方端到端示例、完整错误码表与 4 周学习路径。 | 2026-07-01 | wsl、learning-path、linux、windows、container、wslc、plan9、drvfs、cmake、sdk、diagnostics、hvsocket、gns、systemd、winrt、nuget、com、error-codes |

### operations

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md) | 基于Trae IDE集成浏览器（integrated_browser MCP）和Playwright Python脚本操作forum.trae.cn论坛的完整指南，包含DOM选择器参考、Ember框架感知操作方法、操作序列模板、JavaScript代码片段、独立Python脚本使用、故障排查和长期方案（@discourse/mcp）接入指南。v2.1更新：精确化DOM选择器、新增diagnoseButtons诊断函数、补充MCP参数陷阱警告、补全误操作恢复方法、新增MCP vs Playwright操作区别对照表。 | 2026-06-30 | discourse、论坛、自动化、browser、mcp、playwright、发布 |
| [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md) | 一条可落地执行、可观测验收的 Tuya IPC（网络摄像机）端-云-手机最小闭环跑通路径：先明确最小假设，再按步骤给出依赖/验收/排查，并附依赖关系图与闭环验收总表。 | 2026-06-30 | tuya、ipc、iot、闭环、配网、音视频、设备绑定、事件上报、联调、排查、验收 |
| [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md) | 当需要在 SpecWeave 中新增或使用 flexloop 相关功能时，基于三区域边界模型和四不原则的5种合规集成路径决策指南 | 2026-06-29 | vendor、flexloop、agentforge、submodule、集成方案、三区域模型、四不原则 |
| [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md) | 记录 Windows PowerShell 环境下 heredoc 语法不可用的替代方案 | 2026-06-23 | windows、powershell、shell、heredoc、git |
| [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md) | 记录 Windows PowerShell 下将 Python 中文 stdout 通过文本管道写入文件时可能发生的转码污染，以及推荐的安全写回方案 | 2026-06-30 | windows、powershell、encoding、utf-8、pipe、set-content、python、docs |
| [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md) | 系统性解决Windows终端中文乱码问题的完整指南，涵盖系统级/用户级/项目级三层配置方案 | 2026-07-01 | windows、powershell、cmd、utf-8、encoding、gbk、chcp、乱码 |

### troubleshooting

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md) | 记录 AI 智能体因未读取 AGENTS.md 启动协议而导致输出格式、文件路径、文档结构三项错误的完整故障链与修复方案 | 2026-06-24 | agents、protocol、startup、output-format、path、skill-conflict |
| [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md) | 记录 PowerShell Move-Item 重命名目录时 Access Denied 错误的排查与解决方案 | 2026-06-23 | windows、powershell、rename、directory、access-denied |
| [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md) | 记录在 submodule 目录内创建主项目文件导致 submodule 永久 dirty 的故障原因与解决方案，以及 submodule 元数据外置的最佳实践 | 2026-06-29 | git、submodule、vendor、dirty、modified-content |

### unknown

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [stage-guardrails-guide](stage-guardrails-guide.md) |  |  | - |
| [three-layer-routing](three-layer-routing.md) |  |  | - |
| [VENDOR-INTEGRATION](VENDOR-INTEGRATION.md) |  |  | - |
| [ian-xiaohei-illustrations](learning/ian-xiaohei-illustrations.md) |  |  | - |
| [discourse-api-research](operations/discourse-api-research.md) |  |  | - |
| [wechat-mp-content-extraction](operations/wechat-mp-content-extraction.md) |  |  | - |

## 标签索引

### access-denied

- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### agent

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### agent-skills

- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)

### agentforge

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### agents

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### ai

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### ambient-mode

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### anthropic

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### architecture

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)
- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### argument-definitions

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### binfmt

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### browser

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### c

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### chcp

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### check-mermaid

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### ci

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)

### claude

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)

### cli

- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)
- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### cloud

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### cmake

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### cmd

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### com

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### command-tree

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### container

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### convention

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### cpp

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### cursor

- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)

### diagnostics

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### directory

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### dirty

- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### discourse

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### docs

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### drvfs

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### embedded

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)

### encoding

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### enterprise

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### error-codes

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### esp32

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### flexloop

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### four-layer-model

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### gbk

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### git

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### gns

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### governance

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### governance-loop

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### heredoc

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### hvsocket

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### interop

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### iot

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)
- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### ipc

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### karpathy

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### learning-path

- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### linux

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### llm

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### mcp

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### mcu

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### mermaid

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)
- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### meta-insights

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### methodology

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### modified-content

- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### naming

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### nuget

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### opus

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### output-format

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### path

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### patterns

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### pipe

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### plan9

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### playwright

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### powershell

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### protocol

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### python

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### rename

- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### retrospective

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### sdk

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### set-content

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### shell

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### skill-conflict

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### skills

- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)

### slack

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### source-verification

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### stage-guardrails

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### startup

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### submodule

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### systemd

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### tag

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### tal

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tdd

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tdl

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tkl

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tos

- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)

### tuya

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### tuyaopen

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md)

### utf-8

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### vendor

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### windows

- [WSL 系统学习计划](learning/wsl-learning-plan.md)
- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### winrt

- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### workflow

- [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md)

### wsl

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### wslc

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/wsl-learning-plan.md)

### wslservice

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md)

### 三区域模型

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 乱码

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### 事件上报

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 六规则

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 协作

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### 发布

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 可视化

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 四不原则

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 图表

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 安全编码

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 排查

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 未分类

- [stage-guardrails-guide](stage-guardrails-guide.md)
- [three-layer-routing](three-layer-routing.md)
- [VENDOR-INTEGRATION](VENDOR-INTEGRATION.md)
- [ian-xiaohei-illustrations](learning/ian-xiaohei-illustrations.md)
- [discourse-api-research](operations/discourse-api-research.md)
- [wechat-mp-content-extraction](operations/wechat-mp-content-extraction.md)

### 模板

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 知识沉淀

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### 联调

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 自动化

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 论坛

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 设备绑定

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 配网

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 闭环

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 集成方案

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 音视频

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 验收

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

## 最近更新

| 标题 | 日期 | 分类 |
|------|------|------|
| [WSL CLI 命令树与架构 Wiki 参考手册](learning/wsl-cli-and-architecture-wiki.md) | 2026-07-01 | learning |
| [WSL 系统学习计划](learning/wsl-learning-plan.md) | 2026-07-01 | learning |
| [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md) | 2026-07-01 | operations |
| [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md) | 2026-06-30 | architecture |
| [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md) | 2026-06-30 | learning |
| [TuyaOpen-dev-skills 学习笔记](learning/tuyaopen-dev-skills-learning.md) | 2026-06-30 | learning |
| [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/tuyaopen-folder-learning-path.md) | 2026-06-30 | learning |
| [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md) | 2026-06-30 | operations |
| [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md) | 2026-06-30 | operations |
| [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md) | 2026-06-30 | operations |

## 相关资源

### 回溯报告

- [项目硬编码问题系统性复盘报告](../retrospective/hardcode-retrospective-report.md)
- [提示词工程 — 可迁移模式、模板与方法论萃取](../retrospective/prompt-extraction.md)
- [复盘文档体系](../retrospective/README.md)

### 任务总结

- [任务执行总结报告](../task-summaries/task-summary-git-local-clone-bug-20260701.md)
- [任务执行总结报告](../task-summaries/task-summary-readme-creation-20260623.md)

## 使用指南

### 如何添加知识条目

1. 在 `docs/knowledge/` 下选择对应的分类目录（如 `operations/`、`platform/` 等）
2. 复制 `template.md` 作为模板，创建新的 `.md` 文件
3. 填写 YAML frontmatter 元数据（标题、分类、标签、日期、摘要等）
4. 在正文中按照模板结构编写内容
5. 运行 `python scripts/generate_index.py` 重新生成索引

### 如何检索

- **按类别浏览**：使用上方的「按类别浏览」章节，按操作、平台、排错等分类查找
- **按标签检索**：使用上方的「标签索引」章节，按关键词标签快速定位
- **按时间排序**：查看「最近更新」章节，了解最新添加的知识条目
- **全文搜索**：在项目根目录使用 `grep -r "关键词" docs/knowledge/` 进行全文搜索

### 如何维护

- **定期整理**：每月检查一次知识条目，更新过时内容，补充遗漏信息
- **标签规范化**：使用统一的标签命名，避免同义词分散（如 `powershell` 和 `ps`）
- **及时归档**：完成任务或解决问题后，及时将经验沉淀为知识条目
- **索引更新**：每次添加、修改或删除知识条目后，运行本脚本重新生成索引

---

*索引自动生成于 2026-07-01 14:30:19*
