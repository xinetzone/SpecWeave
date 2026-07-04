# The Agency 项目学习与 Wiki 教程文档 - 产品需求文档

## Overview
- **Summary**: 系统学习微信公众号文章《一人组建一支 Agent 军团，狂揽 11.9 万 Star!》，理解 The Agency 项目的核心概念、技术要点、操作流程及应用场景，基于学习成果创建一份结构清晰、内容详实的 wiki 教程文档。
- **Purpose**: 为项目团队提供 The Agency 项目的完整学习资料，帮助不同技术水平的读者理解和使用该项目。
- **Target Users**: 项目团队成员、AI Agent 技术爱好者、希望了解和使用 The Agency 项目的开发者。

## Goals
- 创建包含目录导航系统的 wiki 教程文档
- 解释 The Agency 项目的核心概念
- 提供分步骤操作指南
- 解析关键技术点
- 整理常见问题解答
- 汇总相关资源链接

## Non-Goals (Out of Scope)
- 不包含 The Agency 项目源码的深度分析
- 不涉及 Agent 角色的自定义开发
- 不提供桌面客户端的安装包
- 不进行 The Agency 项目的代码贡献

## Background & Context
- The Agency 是一个开源项目，拥有 232 个 AI Agent 角色，分为 16 个部门
- 项目已获得 11.9 万 Star，得到广泛认可
- 配套桌面客户端 Agency Agents 支持 Windows、macOS、Linux 系统
- 兼容 Claude Code、Codex、OpenCode、Cursor 等主流 AI 编程工具
- 原文参考：[一人组建一支 Agent 军团，狂揽 11.9 万 Star!](https://mp.weixin.qq.com/s/A1dFio_9NqKKsVQ0SSUIWg?from=industrynews&color_scheme=light#rd)

## Functional Requirements
- **FR-1**: 创建 wiki 教程文档主页面，包含目录导航系统
- **FR-2**: 编写核心概念章节，解释 The Agency 项目的定义、起源和架构
- **FR-3**: 编写分步骤操作指南，指导用户如何选择和使用 Agent 角色
- **FR-4**: 编写关键技术点解析章节，分析 Agent 角色定义的技术细节
- **FR-5**: 编写常见问题解答章节，解答用户可能遇到的问题
- **FR-6**: 编写相关资源链接章节，提供项目地址和参考资料

## Non-Functional Requirements
- **NFR-1**: 文档语言通俗易懂，逻辑严谨，适合不同技术水平的读者
- **NFR-2**: 在适当位置引用原网页内容作为参考依据
- **NFR-3**: 文档结构清晰，便于阅读和导航
- **NFR-4**: 文档格式符合项目规范（Markdown 格式，kebab-case 命名）

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范
- **Business**: 基于公开文章内容创建，不得添加未验证的信息
- **Dependencies**: 依赖网页内容获取，已通过浏览器工具成功获取

## Assumptions
- 用户已了解基本的 AI Agent 概念
- 用户具备基本的 GitHub 操作经验
- 用户可以访问互联网下载客户端和项目代码

## Acceptance Criteria

### AC-1: Wiki 教程文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: wiki 教程文档包含目录导航、核心概念、操作指南、技术解析、FAQ 和资源链接六个部分
- **Verification**: `human-judgment`
- **Notes**: 文档应放置在 docs/knowledge/learning/ 目录下

### AC-2: 目录导航系统可用
- **Given**: 用户打开 wiki 教程文档
- **When**: 用户查看文档顶部的目录导航
- **Then**: 目录导航包含所有章节的链接，点击可跳转到对应章节
- **Verification**: `programmatic`
- **Notes**: 使用 Markdown 锚点链接实现

### AC-3: 核心概念解释清晰
- **Given**: 用户阅读核心概念章节
- **When**: 用户理解 The Agency 项目的定义、起源和架构
- **Then**: 用户能够准确回答 What is The Agency? How was it created? What is its structure?
- **Verification**: `human-judgment`
- **Notes**: 引用原文内容作为参考

### AC-4: 操作指南步骤完整
- **Given**: 用户按照操作指南执行
- **When**: 用户完成所有步骤
- **Then**: 用户能够成功选择和安装所需的 Agent 角色
- **Verification**: `human-judgment`
- **Notes**: 步骤应包含下载客户端、选择 Agent、安装部署等关键环节

### AC-5: 技术要点解析深入
- **Given**: 用户阅读技术要点解析章节
- **When**: 用户理解 Agent 角色定义的技术细节
- **Then**: 用户能够解释角色定义的组成部分（语气、工作流、交付内容、衡量指标）
- **Verification**: `human-judgment`
- **Notes**: 引用原文描述的技术细节

### AC-6: FAQ 章节实用
- **Given**: 用户遇到问题
- **When**: 用户查阅 FAQ 章节
- **Then**: 用户能够找到对应的解决方案
- **Verification**: `human-judgment`
- **Notes**: FAQ 应覆盖常见问题，如上下文限制、自定义修改等

### AC-7: 资源链接有效
- **Given**: 用户点击资源链接章节中的链接
- **When**: 用户访问链接
- **Then**: 链接指向正确的资源页面
- **Verification**: `programmatic`
- **Notes**: 至少包含 GitHub 项目地址和原文链接

## Open Questions
- [ ] 是否需要创建原子化的子目录结构来组织 wiki 文档？
- [ ] 是否需要添加更多的技术细节（如具体的 Agent 文件格式）？