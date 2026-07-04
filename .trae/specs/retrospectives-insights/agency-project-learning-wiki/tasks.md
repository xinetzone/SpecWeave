# The Agency 项目学习与 Wiki 教程文档 - 实现计划

## [x] Task 1: 创建 wiki 教程文档主页面，包含目录导航系统
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建 wiki 教程文档主页面 `the-agency-project-wiki.md`
  - 在文档顶部添加目录导航系统，包含所有章节的锚点链接
  - 添加文档元信息（标题、来源、日期等）
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: 文档存在于 docs/knowledge/learning/ 目录下，命名符合 kebab-case 规范
  - `programmatic` TR-1.2: 目录导航包含至少 6 个章节链接，所有链接使用有效的 Markdown 锚点格式
  - `human-judgement` TR-1.3: 目录导航结构清晰，便于用户快速定位到所需章节
- **Notes**: 参考现有 wiki 文档的目录结构，如 agent-skills-wiki/

## [x] Task 2: 编写核心概念章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 编写核心概念章节，包含 The Agency 项目的定义、起源和架构
  - 引用原文内容作为参考依据
  - 解释 232 个 Agent 角色和 16 个部门的组织结构
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgement` TR-2.1: 核心概念解释清晰，用户能够理解 The Agency 是什么、如何创建的、结构如何
  - `human-judgement` TR-2.2: 原文引用准确，标注了来源链接
  - `human-judgement` TR-2.3: 组织结构描述完整，包含开发、运营、设计、产品、测试等部门的介绍
- **Notes**: 参考原文中的描述："作者在 Reddit 上随手发的一个帖子"、"232 个 Agent，并分成 16 个部门"

## [x] Task 3: 编写分步骤操作指南
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 编写分步骤操作指南，指导用户如何选择和使用 Agent 角色
  - 包含下载安装桌面客户端、选择 Agent、部署到项目等步骤
  - 说明兼容的 AI 编程工具（Claude Code、Codex、OpenCode、Cursor）
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-3.1: 操作步骤完整，覆盖从下载到部署的全流程
  - `human-judgement` TR-3.2: 步骤描述清晰，不同技术水平的用户都能理解
  - `human-judgement` TR-3.3: 包含兼容工具的说明，帮助用户选择适合自己的工具
- **Notes**: 参考原文中的描述："配套了一个桌面客户端 Agency Agents"、"支持 Windows、macOS、Linux 系统"、"兼容目前主流的 AI 编程工具"

## [x] Task 4: 编写关键技术点解析章节
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 编写关键技术点解析章节，分析 Agent 角色定义的技术细节
  - 解释角色定义的组成部分：表达语气、工作流、交付内容、衡量指标
  - 说明如何自定义修改 Agent 角色定义
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgement` TR-4.1: 技术要点解析深入，用户能够理解 Agent 角色定义的技术细节
  - `human-judgement` TR-4.2: 覆盖角色定义的四个组成部分（语气、工作流、交付内容、衡量指标）
  - `human-judgement` TR-4.3: 包含自定义修改的说明，帮助用户根据需求调整角色定义
- **Notes**: 参考原文中的描述："每个 Agent 里面都是一份完整的角色定义，包括角色的表达语气、做事的工作流，最后要交付的内容，还配有一套衡量做得好不好的硬核指标"

## [x] Task 5: 编写常见问题解答章节
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 编写常见问题解答章节，解答用户可能遇到的问题
  - 覆盖上下文限制、自定义修改、Agent 选择等常见问题
  - 提供实用的解决方案
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-5.1: FAQ 覆盖用户可能遇到的常见问题
  - `human-judgement` TR-5.2: 解决方案实用，能够帮助用户解决实际问题
  - `human-judgement` TR-5.3: 问题分类清晰，便于用户快速找到所需答案
- **Notes**: 参考原文中的描述："要是全部装到项目里，上下文估计要爆"、"也能打开它们的文件进行自定义修改"

## [x] Task 6: 编写相关资源链接章节
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 编写相关资源链接章节，提供项目地址和参考资料
  - 包含 GitHub 项目地址、原文链接等关键资源
  - 整理相关学习资源和社区链接
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: 链接格式正确，使用标准的 Markdown 链接语法
  - `human-judgement` TR-6.2: 至少包含 GitHub 项目地址和原文链接两个关键资源
  - `human-judgement` TR-6.3: 资源分类清晰，便于用户查找所需资源
- **Notes**: 参考原文中的信息："GitHub 项目地址：https://github.com/msitarzewski/agency-agents"