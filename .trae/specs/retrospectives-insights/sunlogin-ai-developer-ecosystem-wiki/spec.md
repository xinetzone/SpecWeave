---
id: "sunlogin-ai-developer-ecosystem-wiki"
title: "向日葵AI开发者生态（MCP+Skill+CLI+UI Locator）系统性学习与Wiki更新"
source: "https://activity.sunlogin.oray.com/mcp, https://activity.sunlogin.oray.com/cli, https://service.oray.com/question/50091.html, d:\\AI\\.chaos\\libs\\awesun-*"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/sunlogin-ai-developer-ecosystem-wiki/spec.toml"
date: "2026-07-06"
---
# 向日葵AI开发者生态（MCP+Skill+CLI+UI Locator）系统性学习与Wiki更新 - Product Requirement Document

## Overview
- **Summary**: 系统性学习向日葵AI开发者生态四大核心组件（MCP Server、Skill封装层、CLI命令行工具、UI Locator视觉定位器）以及用例示例项目，基于官方网页文档、GitHub开源仓库代码、配置指南等一手资料，创建结构化的专业Wiki教程，并系统性更新现有综合分析Wiki和产品系列索引，确保知识库完整覆盖向日葵"AI执行基础设施"战略的技术细节、配置流程、最佳实践和开发者生态。
- **Purpose**: 填补现有知识库在向日葵AI开发者工具链方面的空白，为AI Agent开发者、运维自动化工程师、RPA开发者提供从MCP协议接入到Skill自定义开发、从CLI批量运维到UI视觉定位的完整学习资源，完善向日葵产品学习系列的"AI战略"板块。
- **Target Users**: AI Agent开发者、MCP协议集成工程师、运维自动化工程师、RPA开发者、远程控制技术研究者、向日葵企业版用户、AI应用架构师。

## Goals
- 创建向日葵AI开发者生态完整Wiki文档，覆盖四大核心组件+开发指南+最佳实践
- 更新向日葵综合分析Wiki第八章AI战略部分，补充Skill、CLI、UI Locator等组件的详细介绍和生态架构
- 更新向日葵产品系列索引，添加AI开发者生态Wiki入口并更新统计数字
- 确保所有工具参数、配置示例、命令语法、代码片段均准确反映官方文档和GitHub仓库的最新信息
- 提取可复用的技术模式和设计原则（渐进式披露、视觉操作范式、Skill标准化封装等）
- 建立完整的内部链接网络，连接相关Wiki文档（安全产品、综合分析、产品系列索引等）

## Non-Goals (Out of Scope)
- 不修改单个硬件产品Wiki（插座、PDU、鼠标、摄像头、控控、开机盒子等）
- 不实际编写或测试MCP/Skill/CLI代码
- 不创建独立的复盘报告（任务完成后按需进行）
- 不更新贝锐全产品线分析Wiki（除非有直接关联）
- 不翻译或本地化英文文档（保持中文为主）

## Background & Context
- 向日葵于2026年推出完整的AI开发者生态，包含四层架构：
  1. **MCP Server层**：内置于向日葵客户端16.2.3+版本，提供22个标准化工具（7个设备管理+6个远控会话+9个桌面操作），支持Stdio/HTTP双模式
  2. **Skill封装层**（awesun-skill）：为Claude Code/OpenCode/OpenClaw等支持Skills的AI Agent提供渐进式披露的工具调用包装，通过Python executor实现
  3. **CLI工具层**（awesun-cli）：20MB轻量命令行工具，支持全平台（Windows/macOS/Linux/信创），提供设备管理、会话控制、文件传输、端口转发等命令，支持批量操作千台设备
  4. **UI Locator层**（awesun-ui-locator）：截图UI元素定位器，通过AI视觉模型识别按钮、输入框、图标等界面元素，返回归一化坐标[0.0,1.0]，提升桌面操作准确性
- 配套有**awesun-usecase-skill-example**项目，提供"远程安装飞书"等Skill示例，展示如何通过定义Skill规范AI操作路径，提高自动化成功率和稳定性
- 官方配置指南详细说明了OpenCode、Claude Code、Cherry Studio三种主流AI客户端的MCP配置流程
- 现有向日葵产品系列包含11篇Wiki，但AI战略部分仅在综合分析Wiki第八章有基础介绍，缺少专门的开发者生态深度Wiki
- 现有add-sunlogin-cli-wiki spec规划不完整，需要被本更全面的spec取代

## Functional Requirements
- **FR-1**: 创建向日葵AI开发者生态主Wiki文档（sunlogin-ai-developer-ecosystem-wiki.md），采用12章标准结构
- **FR-2**: Wiki第一章概述需明确AI开发者生态的四层架构（MCP Server→Skill→CLI→UI Locator）及其协同关系
- **FR-3**: Wiki需包含前置条件说明（客户端版本16.2.3+/16.3.2+、Python 3.7+、支持MCP的AI客户端）
- **FR-4**: Wiki需详细介绍MCP Server的22个工具分类（设备管理7个、远控会话6个、桌面操作9个）及核心功能
- **FR-5**: Wiki需包含MCP双模式通信（Stdio/HTTP）的适用场景和配置说明
- **FR-6**: Wiki需包含三种主流AI客户端（OpenCode、Claude Code、Cherry Studio）的详细配置步骤，含JSON配置示例
- **FR-7**: Wiki需介绍awesun-skill的架构设计、executor.py工作原理、安装方法（Claude Code/OpenCode/OpenClaw）
- **FR-8**: Wiki需介绍awesun-cli的核心特点（20MB轻量、全平台、批量千台设备、安全可追溯、开箱即用）及主要命令类别
- **FR-9**: Wiki需介绍awesun-ui-locator的工作原理、坐标系统（归一化0.0-1.0）、UI元素识别指南、坐标计算方法
- **FR-10**: Wiki需包含awesun-usecase-skill-example的"远程安装飞书"案例分析，展示Skill如何规范AI操作流程、提高成功率
- **FR-11**: Wiki需包含"如何构建自己的Skill"开发指南，基于官方示例总结Skill设计最佳实践
- **FR-12**: Wiki需包含常见问题解答（FAQ）章节，覆盖远控失败、桌面操作不成功、模型选择建议等官方Q&A内容
- **FR-13**: Wiki需包含专业深度洞察章节，分析"视觉+键鼠"vs"API调用"技术路线选择、渐进式披露设计、Skill标准化封装等可复用模式
- **FR-14**: 更新向日葵综合分析Wiki（sunlogin-comprehensive-analysis-wiki.md）第八章AI战略部分，补充Skill层、CLI层、UI Locator层的介绍，完善AI生态架构图
- **FR-15**: 更新向日葵产品系列索引（sunlogin-product-series-index.md），在"五、跨产品综合分析与AI战略"分类下添加AI开发者生态Wiki入口，更新Wiki总数统计（11→12）
- **FR-16**: 所有代码块使用正确的语言标注（json/bash/python）
- **FR-17**: 添加适当的内部链接，连接到安全产品Wiki、综合分析Wiki、产品系列索引等相关文档

## Non-Functional Requirements
- **NFR-1**: 文档语言使用标准现代汉语，专业、清晰、准确，避免网络流行语
- **NFR-2**: 文档结构遵循现有向日葵Wiki的12章标准格式
- **NFR-3**: 所有表格使用Markdown标准格式，对齐整齐
- **NFR-4**: 文件名使用kebab-case纯英文命名
- **NFR-5**: YAML frontmatter包含title、source、date、tags字段
- **NFR-6**: 内部链接使用相对路径，确保可点击导航
- **NFR-7**: 配置示例中的路径需同时说明Windows和macOS的差异（如MCP server路径）
- **NFR-8**: 工具参数描述需与官方mcp_tools.md文档完全一致
- **NFR-9**: 坐标归一化公式和示例需准确无误（x = x_pixel/width, y = y_pixel/height）

## Constraints
- **Technical**: 必须遵循现有Wiki文档的格式和风格；使用纯Markdown格式；不引入新的依赖；所有配置示例必须可验证
- **Business**: 必须准确反映官方文档和GitHub仓库内容，不得添加未经证实的信息；涉及未公开的CLI详细命令时，基于官方活动页面已有信息进行描述，不编造
- **Dependencies**: 依赖现有Wiki文档结构；依赖官方MCP配置指南；依赖四个GitHub开源仓库的README和代码

## Assumptions
- 官方网页文档（2026-06/07更新）和GitHub仓库内容是最新且准确的
- awesun-cli虽然详细命令文档未完全公开，但官方活动页面已披露核心功能类别（设备管理、会话控制、文件传输、端口映射），可基于此进行概述
- 现有Wiki结构稳定，综合分析Wiki第八章AI战略部分可扩展而不需要大规模重构
- AI开发者生态Wiki应放在"五、跨产品综合分析与AI战略"分类下

## Acceptance Criteria

### AC-1: AI开发者生态Wiki文档结构完整性
- **Given**: 所有官方资料和GitHub仓库已完整学习
- **When**: 主Wiki文档创建完成
- **Then**: Wiki包含以下12个章节：一、概述与学习目标、二、AI开发者生态四层架构、三、前置条件与准备工作、四、MCP Server核心能力详解（22个工具）、五、MCP双模式通信与配置、六、三大AI客户端配置实战（OpenCode/Claude Code/Cherry Studio）、七、awesun-skill渐进式披露封装、八、awesun-cli命令行工具、九、awesun-ui-locator视觉定位、十、用例示例与自定义Skill开发、十一、最佳实践与常见问题、十二、相关资源链接
- **Verification**: `human-judgment`
- **Notes**: 章节标题可根据内容微调，但需覆盖所有核心主题

### AC-2: MCP工具参考准确性
- **Given**: 官方mcp_tools.md文档
- **When**: Wiki第四章编写完成
- **Then**: 所有22个工具均按三大类（设备管理7、远控会话6、桌面操作9）准确记录，包含功能描述、核心参数说明；坐标归一化公式和远控类型说明完整准确
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 可通过与mcp_tools.md逐项对比验证

### AC-3: 客户端配置步骤准确性
- **Given**: 官方配置指南（question/50091.html）
- **When**: Wiki第六章编写完成
- **Then**: OpenCode、Claude Code、Cherry Studio三种客户端的配置步骤完整，包含工作区结构、opencode.json/.mcp.json配置示例、环境变量设置（Claude Code用Kimi API的ANTHROPIC_BASE_URL等）、验证方法
- **Verification**: `human-judgment`
- **Notes**: Windows和macOS路径差异需明确标注

### AC-4: Skill/CLI/UI Locator组件介绍完整性
- **Given**: 四个GitHub仓库的README、SKILL.md、代码
- **When**: Wiki第七、八、九、十章编写完成
- **Then**: 
  - awesun-skill：架构说明、executor.py工作原理（--list/--describe/--call三个命令）、三种AI工具安装路径
  - awesun-cli：五大核心特点（全平台/千台设备/开箱即用/安全可追溯/20MB轻量）、四大命令类别（设备管理/会话控制/文件操作/端口映射）
  - awesun-ui-locator：工作流程、坐标系统、5类UI元素特征（按钮/输入框/图标/导航/反馈）、定位策略、坐标计算示例
  - 用例示例：飞书安装13步标准流程分析、Skill设计原则（重试机制、截屏节制、失败中止）
- **Verification**: `human-judgment`

### AC-5: 综合分析Wiki更新
- **Given**: 现有sunlogin-comprehensive-analysis-wiki.md
- **When**: 第八章更新完成
- **Then**: 
  - 8.2节扩展为完整的四层生态架构说明（MCP Server→Skill→CLI→UI Locator）
  - 添加各层协同工作流程图或架构说明
  - 补充awesun-skill渐进式披露设计理念
  - 补充awesun-cli作为批量运维入口的定位
  - 补充awesun-ui-locator视觉闭环的重要性
  - 保持原有文档结构和其他章节内容不变
- **Verification**: `human-judgment`

### AC-6: 产品系列索引更新
- **Given**: 现有sunlogin-product-series-index.md
- **When**: 更新完成
- **Then**: 
  - 在"五、跨产品综合分析与AI战略"表格中添加AI开发者生态Wiki链接和核心内容描述
  - 系列概览中Wiki总数从11篇更新为12篇
  - 跨产品共性洞察中补充AI开发者生态相关洞察
  - AI Agent跨领域映射表中补充相关模式（渐进式披露、视觉操作范式、Skill标准化）
  - 阅读路径建议中补充AI开发者生态的阅读位置
- **Verification**: `human-judgment`

### AC-7: 格式与规范符合性
- **Given**: 所有文档创建/更新完成
- **When**: 进行格式检查
- **Then**: 
  - YAML frontmatter格式正确，包含必要字段
  - 文件名符合kebab-case规范（sunlogin-ai-developer-ecosystem-wiki.md）
  - 内部链接使用相对路径且有效
  - 代码块标注正确语言类型（json/bash/python）
  - 所有表格格式整齐
- **Verification**: `programmatic`
- **Notes**: 可运行文件名规范检查脚本

### AC-8: 内容准确性验证
- **Given**: 完成的Wiki文档
- **When**: 与官方资料交叉验证
- **Then**: 
  - MCP工具数量正确（22个：7+6+9）
  - 客户端版本要求正确（MCP需16.2.3+，Skill需16.3.2+）
  - 配置示例中的端口正确（8908/8980）
  - 推荐模型正确（Kimi K2.5、Gemini 2.5 Pro等视觉模型）
  - Q&A内容与官方一致（需手动验证一次设备、视觉模型选择建议）
  - 飞书安装流程步骤数正确（13步）
- **Verification**: `human-judgment`

## Open Questions
- [ ] awesun-cli的详细命令参考（如完整的awesun-cli device ls等命令参数）官方文档中未完全披露，Wiki中应如何处理？（建议：基于官方活动页面已有信息做概述，标注"详细命令参考请见官方CLI帮助文档"，不编造参数）
- [ ] 是否需要在Wiki中包含MCP工具调用的实际示例（如device_search、control_connect的JSON调用示例）？（建议：包含1-2个典型调用流程示例，展示完整的"搜索设备→建立连接→截图→操作→断开"闭环）
