---
id: "sunlogin-ai-developer-ecosystem-wiki-tasks"
title: "向日葵AI开发者生态Wiki更新 - 实施计划"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/sunlogin-ai-developer-ecosystem-wiki/tasks.toml"
date: "2026-07-06"
---
# 向日葵AI开发者生态（MCP+Skill+CLI+UI Locator）系统性学习与Wiki更新 - The Implementation Plan

## [x] Task 1: 创建向日葵AI开发者生态主Wiki文档框架（前3章）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建文件 `docs/knowledge/learning/07-vendor-product-learning/sunlogin/sunlogin-ai-developer-ecosystem-wiki.md`
  - 添加正确的YAML frontmatter（title、source、date、tags）
  - 编写第一章「概述与学习目标」：研究背景、学习目标、分析框架
  - 编写第二章「AI开发者生态四层架构」：MCP Server层、Skill封装层、CLI工具层、UI Locator层的定位与协同关系，包含架构图说明
  - 编写第三章「前置条件与准备工作」：客户端版本要求（16.2.3+/16.3.2+）、Python环境要求（3.7+）、支持的AI客户端列表、模型选择建议（Kimi K2.5/Gemini 2.5 Pro等视觉模型）
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件创建成功，路径正确，文件名符合kebab-case规范
  - `programmatic` TR-1.2: YAML frontmatter格式正确，包含所有必要字段
  - `human-judgement` TR-1.3: 前3章内容结构完整，逻辑清晰，四层架构描述准确
  - `human-judgement` TR-1.4: 版本要求、环境要求与官方文档一致
- **Notes**: 参考现有sunlogin-comprehensive-analysis-wiki.md的章节风格和格式

## [x] Task 2: 编写MCP Server核心能力章节（第4章，含22工具+双模式+客户端配置）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 编写第四章「MCP Server核心能力详解（22个工具）」：
    - 设备管理类（7个）：device_add/device_search/device_info/device_update/device_remove/device_wakeup/device_shutdown，用表格列出工具名、功能、核心参数
    - 远控会话类（6个）：control_connect/control_sessions/control_disconnect/control_command/control_screenshot/control_portforward
    - 桌面操作类（9个）：desktop_click_mouse/desktop_move_mouse/desktop_drag_mouse/desktop_scroll_mouse/desktop_press_keys/desktop_typing_keys/desktop_typing_text/desktop_paste_text/desktop_waiting
    - 附录：坐标归一化公式和示例、远控类型说明表（file/desktop/cmd2/ssh/desktop_view/newcamera/forward）
  - 编写第五章「MCP双模式通信与配置」：
    - Stdio模式：本地进程通信、低延迟、适用本地AI客户端
    - Streamable HTTP模式：HTTP远程通信、跨网络调用场景
    - 向日葵客户端启用MCP Server的操作步骤
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-8
- **Test Requirements**:
  - `human-judgement` TR-2.1: 22个工具分类正确（7+6+9），无遗漏无多余
  - `human-judgement` TR-2.2: 每个工具的功能描述与官方mcp_tools.md一致
  - `human-judgement` TR-2.3: 坐标归一化公式和示例准确无误
  - `human-judgement` TR-2.4: 远控类型7种均有说明
  - `human-judgement` TR-2.5: 双模式通信特点描述准确
- **Notes**: 直接参考d:\AI\.chaos\libs\awesun-mcp\docs\mcp_tools.md，确保参数和功能描述准确

## [x] Task 3: 编写Skill/CLI/UI Locator组件章节（第5-7章，客户端配置已整合至4.7节）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 编写第六章「三大AI客户端配置实战」：
    - 6.1 OpenCode配置：模型服务配置（推荐Kimi K2.5/Gemini 2.5 Pro）、工作区结构（AGENTS.md + opencode.json）、opencode.json配置示例、/mcp验证连接状态、功能演示
    - 6.2 Claude Code配置：CLI安装（irm https://claude.ai/install.ps1 | iex）、工作区结构（CLAUDE.md + .mcp.json）、.mcp.json配置示例（Windows路径C:\Program Files\Oray\AweSun\...）、环境变量设置（ANTHROPIC_BASE_URL=https://api.kimi.com/coding/、ANTHROPIC_API_KEY）、/status验证、--dangerously-skip-permissions说明
    - 6.3 Cherry Studio配置：MCP服务器JSON导入、模型服务配置、助手配置、提示词设置、功能演示
    - 6.4 Windows vs macOS路径差异对照表
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-7, AC-8
- **Test Requirements**:
  - `human-judgement` TR-3.1: 三种客户端配置步骤完整，与官方question/50091.html一致
  - `human-judgement` TR-3.2: JSON配置示例语法正确，端口号正确（8908/8980）
  - `human-judgement` TR-3.3: Windows和macOS路径差异明确标注
  - `human-judgement` TR-3.4: 环境变量名称和值准确（ANTHROPIC_BASE_URL等）
  - `programmatic` TR-3.5: 代码块均标注正确语言（json/bash）
- **Notes**: 注意区分Windows路径（C:\Program Files\Oray\AweSun\flutter\awesun-mcp-server.exe）和macOS路径（/Applications/AweSun.app/Contents/Helpers/awesun-mcp-server）

## [x] Task 4: 编写用例示例、最佳实践、资源链接章节（第8-12章）
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 编写第七章「awesun-skill渐进式披露封装」：
    - Skill定位：为支持Skills的AI Agent提供渐进式披露工具调用
    - 架构设计：SKILL.md元数据 + executor.py执行器 + mcp-config.json配置
    - executor.py工作原理：--list列出工具、--describe查看工具schema、--call执行工具调用
    - 安装方法：Claude Code（~/.claude/skills/）、OpenCode（~/.opencode/skills/）、OpenClaw（~/.openclaw/skills/）的全局/工作区安装
    - 依赖安装：pip install mcp
  - 编写第八章「awesun-cli命令行工具」：
    - 五大核心特点：全平台全系统支持（含信创）、一行指令操作千台设备、开箱即用被控端零更新、安全可追溯、20MB轻量无感知
    - 四大命令类别：设备管理（awesun-cli device ls）、远程会话与控制（session connect）、远程文件操作（file transfer）、端口映射（forward config）
    - 适用场景：批量运维、脚本自动化、CI/CD集成
    - 注意：详细命令参数请参考官方CLI文档，本文档不编造未公开参数
  - 编写第九章「awesun-ui-locator视觉定位」：
    - 工作流程：读取截图→理解用户意图→视觉分析→计算归一化坐标→返回结果
    - 坐标系统：原点左上角(0,0)，范围[0.0,1.0]，公式x=x_pixel/width, y=y_pixel/height
    - 5类UI元素特征表：按钮、输入框、图标、导航、反馈元素
    - 定位策略：先整体后局部、多特征匹配、处理歧义
    - 坐标计算示例：3个典型场景计算
    - 边界情况处理：多个匹配项、未找到元素、模糊匹配
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-8
- **Test Requirements**:
  - `human-judgement` TR-4.1: awesun-skill架构描述与SKILL.md、executor.py一致
  - `human-judgement` TR-4.2: executor.py三个命令（--list/--describe/--call）说明准确
  - `human-judgement` TR-4.3: 三种AI工具的Skill安装路径正确
  - `human-judgement` TR-4.4: awesun-cli五大特点和四大命令类别与官方活动页面一致，不编造未公开参数
  - `human-judgement` TR-4.5: UI Locator坐标系统、5类元素、定位策略与SKILL.md、ui_patterns.md一致
  - `human-judgement` TR-4.6: 坐标计算示例数值准确
- **Notes**: CLI章节严格基于官方活动页面已有信息，不编造详细命令参数；UI Locator参考ui_patterns.md的元素特征表

## [ ] Task 5: 编写用例示例、最佳实践、资源链接章节（第10-12章）
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 编写第十章「用例示例与自定义Skill开发」：
    - 10.1 官方示例：远程安装飞书（feishu-install-pc）案例分析
      - 13步标准流程详解
      - Skill设计原则：重试机制（每2-5秒重试，最多1-3次）、截屏节制（无要求不截屏）、失败中止（重试失败不继续）、UI Locator优先
    - 10.2 如何构建自己的Skill：
      - Skill基本结构（SKILL.md + 可选executor）
      - SKILL.md frontmatter规范（name/description/version）
      - 操作流程设计原则：状态确认→重试策略→失败回退
      - 典型Skill开发流程
    - 10.3 完整MCP调用流程示例：搜索设备→建立远程桌面连接→截图确认→UI元素定位→点击操作→验证结果→断开连接
  - 编写第十一章「最佳实践与常见问题」：
    - 最佳实践：模型选择（视觉模型推荐）、设备授信（手动远控一次后AI即可使用）、截屏策略（避免频繁截屏）、坐标归一化注意事项、会话及时断开
    - FAQ：
      - Q: 为什么AI远控失败？A: 需手动验证一次设备密码/信任设备
      - Q: 为什么桌面操作不成功？A: 建议使用kimi-2.5等视觉能力更强的模型
      - Q: Stdio和HTTP模式如何选择？
      - Q: 批量设备管理推荐用什么？（CLI）
  - 编写第十二章「相关资源链接」：
    - 官方资源链接（MCP页面、CLI页面、帮助文档、GitHub仓库）
    - 内部Wiki链接（安全产品、综合分析、产品系列索引）
    - 相关模式库链接
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-8
- **Test Requirements**:
  - `human-judgement` TR-5.1: 飞书安装13步流程与SKILL.md一致
  - `human-judgement` TR-5.2: Skill设计原则总结准确（重试、截屏节制、失败中止）
  - `human-judgement` TR-5.3: 自定义Skill开发指南清晰可操作
  - `human-judgement` TR-5.4: MCP完整调用流程示例逻辑通顺
  - `human-judgement` TR-5.5: FAQ内容与官方Q&A一致
  - `human-judgement` TR-5.6: 资源链接完整，内部链接使用相对路径
- **Notes**: 飞书安装流程严格参考feishu-install-pc/SKILL.md，不遗漏步骤

## [ ] Task 6: 更新向日葵综合分析Wiki第八章AI战略部分
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 读取现有sunlogin-comprehensive-analysis-wiki.md第八章内容
  - 扩展8.2节「向日葵AI产品矩阵两大核心组件」为「8.2 向日葵AI开发者生态四层架构」：
    - 补充Skill层（awesun-skill）：渐进式披露理念、为什么需要Skill层、executor架构
    - 补充CLI层（awesun-cli）：批量运维入口、五大核心特点、适用场景
    - 补充UI Locator层：视觉闭环的关键环节、为什么视觉操作需要UI定位
    - 更新架构图说明，展示四层协同关系
  - 保持第八章其他小节（8.1、8.3等）和其他章节内容不变
  - 确保更新后文档结构完整，无断裂
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgement` TR-6.1: 8.2节四层架构描述准确，与新Wiki一致
  - `human-judgement` TR-6.2: 原有内容和其他章节未被破坏
  - `human-judgement` TR-6.3: 添加适当的内部链接指向新创建的AI开发者生态Wiki
- **Notes**: 使用Edit工具进行精确编辑，避免重写整个文件

## [ ] Task 7: 更新向日葵产品系列索引
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 读取现有sunlogin-product-series-index.md
  - 在「五、跨产品综合分析与AI战略」表格中添加新行：
    - 主题：向日葵AI开发者生态
    - Wiki链接：sunlogin-ai-developer-ecosystem-wiki.md
    - 核心内容：MCP Server 22工具详解、双模式通信、三大客户端配置实战、Skill渐进式封装、CLI批量运维、UI Locator视觉定位、自定义Skill开发指南、四层生态架构
    - 萃取模式：待入库：渐进式披露封装、视觉操作闭环、Skill标准化流程
  - 更新系列概览表格：Wiki总数从11篇更新为12篇
  - 在「跨产品共性洞察」部分补充AI开发者生态相关洞察：
    - 渐进式披露：Skill层通过SKILL.md元数据+executor实现工具能力的渐进式暴露，避免AI一次性看到过多工具导致决策混乱
    - 视觉操作闭环：MCP截图→UI Locator定位→桌面操作→截图验证，形成完整的视觉感知-决策-执行闭环
  - 在「AI Agent跨领域映射」表格中补充：
    - 渐进式披露封装 → Agent工具暴露策略 → 🔄 待入库
    - 视觉操作闭环（截图-定位-操作-验证） → Agent与异构系统交互范式 → 🔄 待入库
    - Skill标准化流程（重试/截屏节制/失败中止） → Agent任务执行可靠性设计 → 🔄 待入库
  - 更新「阅读路径建议」，在AI战略部分补充AI开发者生态Wiki的阅读位置
  - 更新页脚最后更新日期
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-7.1: 新Wiki入口添加正确，链接使用相对路径
  - `programmatic` TR-7.2: Wiki总数统计更新为12篇
  - `human-judgement` TR-7.3: 跨产品共性洞察和AI Agent映射表更新合理
  - `human-judgement` TR-7.4: 阅读路径建议更新完整
- **Notes**: 使用Edit工具精确修改表格对应部分

## [ ] Task 8: 全局链接验证与格式检查
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 检查新创建的Wiki文档中所有内部链接（相对路径）是否正确
  - 检查综合分析Wiki中新增链接是否正确
  - 检查产品系列索引中新增链接是否正确
  - 运行文件名规范检查脚本验证文件名
  - 检查所有代码块是否标注正确语言
  - 检查所有表格格式是否整齐
  - 检查YAML frontmatter格式
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-8.1: 运行 `python .agents/scripts/check-filename-convention.py` 验证文件名
  - `human-judgement` TR-8.2: 所有内部链接点击可到达目标文档
  - `human-judgement` TR-8.3: 代码块语言标注正确
  - `human-judgement` TR-8.4: 表格对齐整齐
- **Notes**: 链接检查时注意相对路径层级关系（sunlogin/目录下的文档链接到同目录其他文档直接用文件名，链接到上级目录用../）
