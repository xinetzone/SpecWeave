---
type: Concept
title: OpenMAIC 使用入门指南
description: 从零开始使用 OpenMAIC 的完整操作指南：注册、上传教材、生成课程、导出分享
tags: [openmaic, tutorial, getting-started, how-to]
generated:
  by: agent-agnes
  at: "2026-09-09T10:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-09T10:00:00+08:00"
status: draft
stale_after: "2027-09-09"
sources:
  - id: S-001
    resource: /references/00-sources.md
    title: "微信公众号文章《短短5个月暴涨3.3万Star》"
---

# OpenMAIC 使用入门指南

本文档介绍如何从零开始使用 OpenMAIC，涵盖在线体验和 local 部署两种路径。

## 路径一：在线体验（推荐新手）

### 步骤 1：访问平台

打开 https://open.maic.chat ，注册账号。

### 步骤 2：领取免费额度

每天可领取免费额度，日常使用足够。

### 步骤 3：进入专业模式

点击"PRO 专业模式"，进入完整功能界面。侧边栏支持新建对话和课程。

### 步骤 4：上传教材

- 支持格式：PDF 文档
- 操作：拖拽或点击上传
- 示例：七年级数学上册 PDF

### 步骤 5：描述需求

在对话框中输入需求描述，例如：
> "请根据这本数学书规划一周课程，每节课带有测验和互动"

### 步骤 6：等待生成

Agent 自动完成以下工作：
1. 读取 PDF 材料
2. 规划每节课内容
3. 生成互动课件
4. 编写课后测验
5. 创建配音角色

### 步骤 7：预览与修改

- 点击"开始学习"进入在线上课状态
- 可通过对话框描述指令修改课件细节
- 支持导出 PPT、教学资源包、带配音和字幕的视频

## 路径二：本地部署

### 前置条件

- 需要一定技术背景（Python 环境）
- 参考 OpenMAIC GitHub 仓库中的部署文档

### 步骤

1. 克隆仓库：`git clone https://github.com/THU-MAIC/OpenMAIC`
2. 安装依赖（见仓库 README）
3. 配置 API 密钥
4. 启动服务

### 官方 Skill 辅助

安装 OpenMAIC 官方 Skill 后，只需一行指令即可完成部署引导（F-021）。

## 适用人群

| 人群 | 推荐路径 | 主要用途 |
|------|---------|---------|
| 学生/自学者 | 在线体验 | 将教材转化为学习笔记和测验 |
| 教师 | 在线体验 | 快速备课，生成课件和讲解视频 |
| 开发者 | 本地部署 | 定制技能、二次开发 |
| 研究人员 | 两种路径 | 论文解读、学习路线规划 |

## 相关概念

- [OpenMAIC 项目概览](/concepts/00-project-overview.md)
- [OpenMAIC 核心功能详解](/concepts/01-core-features.md)
- [OpenMAIC 技能系统](/concepts/03-skill-system.md)

## 事实溯源

- F-004, F-010~F-016, F-021, F-022, F-024
