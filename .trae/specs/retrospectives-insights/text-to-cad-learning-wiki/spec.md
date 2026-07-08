---
title: "text-to-cad 项目学习与 Wiki 教程文档"
source: "微信公众号文章《机械设计又又又卡住了？这个开源项目让 AI 直接生成可编辑的 CAD 源代码》"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/text-to-cad-learning-wiki/spec.toml"
date: "2026-07-04"
tags: ["text-to-cad", "cad", "ai-agent", "build123d", "step", "urdf", "3d-printing", "robotics"]
---
# text-to-cad 项目学习与 Wiki 教程文档 - 产品需求文档

## Overview
- **Summary**: 系统学习微信公众号文章介绍的 text-to-cad 开源项目，理解其核心概念、技术原理、功能特性、安装使用流程及应用边界，基于学习成果创建一份结构清晰、内容详实的 wiki 教程文档。
- **Purpose**: 为项目团队提供 text-to-cad 项目的完整学习资料，帮助机械设计、机器人开发、3D打印等领域的开发者理解和使用该AI辅助CAD设计工具。
- **Target Users**: 机械设计工程师、机器人开发者、3D打印爱好者、AI Agent技术爱好者、希望使用AI提升CAD设计效率的开发者。

## Goals
- 创建包含目录导航系统的 wiki 教程文档
- 解释 text-to-cad 项目的核心概念和设计理念
- 详细介绍5大核心功能特性
- 提供分步骤安装与使用指南
- 解析关键技术实现要点
- 说明项目局限性和使用边界
- 整理常见问题解答
- 汇总相关资源链接

## Non-Goals (Out of Scope)
- 不包含 text-to-cad 项目源码的深度代码分析
- 不涉及 Build123d 库的完整教学
- 不提供CAD软件（SolidWorks等）的使用教程
- 不进行 text-to-cad 项目的代码贡献
- 不包含复杂装配体设计的高级教程

## Background & Context
- text-to-cad 是面向Agent的CAD技能库，GitHub上有7400+ stars
- 核心思路：用AI生成可编辑的CAD源代码，而非黑盒STL网格模型
- 使用Build123d Python作为CAD源码语言
- 支持导出STEP、URDF、DXF、G-code等工程文件
- 内置标准件库（螺丝、轴承、电机等）
- 提供本地WebGL浏览器预览器
- 开源地址：https://github.com/earthtojake/text-to-cad
- 开源协议：MIT
- 原文参考：https://mp.weixin.qq.com/s/mfC7NwTsmmthfKzdarnTaQ

## Functional Requirements
- **FR-1**: 创建 wiki 教程文档主页面，包含完整的目录导航系统
- **FR-2**: 编写项目概述章节，介绍text-to-cad解决的痛点和核心价值
- **FR-3**: 编写核心功能章节，详细解析5大功能特性（参数化CAD源码生成、URDF自动生成、标准件库、本地预览器、DXF/G-code导出）
- **FR-4**: 编写安装配置章节，提供Skills CLI、Claude Code插件、Python环境、Viewer前端的分步安装指南
- **FR-5**: 编写使用流程章节，演示从自然语言描述到生成CAD模型的完整工作流
- **FR-6**: 编写局限性说明章节，客观说明项目当前的不足和使用边界
- **FR-7**: 编写核心价值总结章节，分析项目的设计思路和适用场景
- **FR-8**: 编写常见问题解答章节
- **FR-9**: 编写相关资源链接章节
- **FR-10**: 更新知识库索引（docs/knowledge/README.md）添加本教程入口

## Non-Functional Requirements
- **NFR-1**: 文档语言通俗易懂，逻辑严谨，适合不同技术水平的读者（机械工程师/软件开发者/爱好者）
- **NFR-2**: 在适当位置引用原网页内容作为参考依据
- **NFR-3**: 文档结构清晰，便于阅读和导航
- **NFR-4**: 文档格式符合项目规范（Markdown格式，kebab-case命名，TOML frontmatter）
- **NFR-5**: 技术术语准确，关键概念提供清晰解释

## Constraints
- **Technical**: 文档必须使用Markdown格式，遵循项目命名规范，放置在docs/knowledge/learning/目录下
- **Business**: 基于公开文章内容创建，不得添加未验证的信息，客观说明项目局限性
- **Dependencies**: 依赖已获取的网页内容，无需额外网络请求

## Assumptions
- 用户具备基本的CAD设计概念（了解STEP、STL等格式）
- 用户具备基本的Python和命令行操作经验
- 用户了解基本的AI Agent使用方式（如Claude Code）
- 用户可以访问互联网下载项目代码和依赖

## Acceptance Criteria

### AC-1: Wiki 教程文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: wiki教程文档包含目录导航、项目概述、核心功能、安装指南、使用流程、局限性、价值总结、FAQ和资源链接等完整章节
- **Verification**: `human-judgment`
- **Notes**: 文档应放置在docs/knowledge/learning/目录下，文件名为text-to-cad-wiki.md

### AC-2: 目录导航系统可用
- **Given**: 用户打开wiki教程文档
- **When**: 用户查看文档顶部的目录导航
- **Then**: 目录导航包含所有章节的链接，点击可跳转到对应章节
- **Verification**: `programmatic`
- **Notes**: 使用Markdown锚点链接实现

### AC-3: 项目痛点与核心价值阐述清晰
- **Given**: 用户阅读项目概述章节
- **When**: 用户理解text-to-cad要解决的问题
- **Then**: 用户能够说明传统AI CAD生成的3个痛点（STL不可编辑、STEP需重建、URDF手动编写易出错）以及text-to-cad的核心价值主张
- **Verification**: `human-judgment`
- **Notes**: 引用原文中的痛点描述

### AC-4: 5大核心功能解析完整
- **Given**: 用户阅读核心功能章节
- **When**: 用户理解5大功能的技术细节
- **Then**: 用户能够解释参数化CAD源码生成、URDF自动生成、标准件库、本地预览器、DXF/G-code切片的工作原理和价值
- **Verification**: `human-judgment`
- **Notes**: 每个功能需包含技术要点和实际应用价值

### AC-5: 安装指南步骤明确
- **Given**: 用户按照安装指南执行
- **When**: 用户完成所有步骤
- **Then**: 用户能够成功安装text-to-cad的Skills CLI、Python环境和Viewer前端
- **Verification**: `human-judgment`
- **Notes**: 包含4个安装部分的完整命令

### AC-6: 工作流演示清晰
- **Given**: 用户阅读使用流程章节
- **When**: 用户理解完整工作流程
- **Then**: 用户能够描述从自然语言描述→Build123d源码→STEP/URDF导出→预览查看→制造文件生成的完整链路
- **Verification**: `human-judgment`
- **Notes**: 以机器人底盘设计为例进行说明

### AC-7: 局限性说明客观准确
- **Given**: 用户阅读局限性章节
- **When**: 用户了解项目当前的不足
- **Then**: 用户能够说出至少5个项目局限性（Implicit CAD试验性、Node环境门槛、Git LFS、无中文文档、复杂装配体验证不足、许可证问题）
- **Verification**: `human-judgment`
- **Notes**: 客观说明，不夸大也不贬低

### AC-8: FAQ章节实用
- **Given**: 用户遇到问题
- **When**: 用户查阅FAQ章节
- **Then**: 用户能够找到对应的解决方案或解释
- **Verification**: `human-judgment`
- **Notes**: FAQ应覆盖常见问题

### AC-9: 资源链接有效
- **Given**: 用户点击资源链接章节中的链接
- **When**: 用户访问链接
- **Then**: 链接指向正确的资源页面
- **Verification**: `programmatic`
- **Notes**: 至少包含GitHub项目地址和原文链接

### AC-10: 知识库索引更新完成
- **Given**: wiki文档创建完成
- **When**: 查看docs/knowledge/README.md
- **Then**: 学习分类中新增text-to-cad教程条目，包含标题、摘要、日期和标签
- **Verification**: `programmatic`
- **Notes**: 遵循现有索引格式

## Open Questions
- [ ] 是否需要创建原子化的子目录结构来组织wiki文档？
- [ ] 是否需要补充GitHub仓库的更详细分析？
