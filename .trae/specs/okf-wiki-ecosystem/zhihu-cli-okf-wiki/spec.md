---
title: "Zhihu CLI 知乎数据开放平台 OKF Wiki 教程"
status: draft
---

# Zhihu CLI 知乎数据开放平台 - Product Requirement Document

## Overview

* **Summary**: 基于6篇公开文章（腾讯云开发者社区、知乎官方开放平台、知乎专栏/问答、第三方技术博客），生成一份结构化、可溯源、带时效管理的 OKF v0.2 知识包，系统介绍知乎数据开放平台 Zhihu CLI 的产品定位、安装配置、核心能力、安全设计、实战玩法与生态集成。

* **Purpose**: 解决"AI读不到知乎内容"的长期痛点，为 AI Agent 开发者和知乎创作者提供一份可信赖的 Zhihu CLI 入门与进阶指南，覆盖从注册到高级玩法的全链路知识。

* **Target Users**: AI Agent 开发者、知乎内容创作者、对大模型知识接入感兴趣的技术人员。

## Goals

* 系统性梳理知乎数据开放平台的产品矩阵与核心能力

* 提供可复现的 Zhihu CLI 安装、配置与使用教程

* 详解 Skill + CLI 与 MCP 两种接入方式的差异与适用场景

* 整理供应链安全设计与凭证存储机制

* 汇总实战玩法与生态集成方案

* 所有技术事实带 F 编号溯源，P0 声明经权威交叉核验

## Non-Goals (Out of Scope)

* 不开发 Zhihu CLI 相关的代码或工具

* 不提供知乎开放平台的商业授权咨询

* 不涉及知乎爬虫或非官方 API 的技术细节

* 不做社区版 pyzhihu-cli 的深度教程（仅作对比提及）

* 不覆盖所有 CLI 命令的参数级细节（聚焦常用核心命令）

## Background & Context

* 知乎数据开放平台（developer.zhihu.com）推出了官方 Zhihu CLI，支持 Skill 和 MCP 两种接入方式

* 解决了 AI Agent 无法高效读取知乎内容的长期痛点，同时支持个人创作数据的 AI 化利用

* 6篇来源覆盖：官方平台介绍、第三方教程、实测专栏、高赞玩法讨论，形成多源交叉验证

* 产出物符合 OKF v0.2 规范，存放于 `projects/awesome-okf-xs/doc/bundles/` 对应分组

## Functional Requirements

* **FR-1**: 知识包包含知乎数据开放平台产品定位与核心能力矩阵介绍

* **FR-2**: 提供完整的注册、安装、配置教程（含多平台注意事项）

* **FR-3**: 详解 Skill + CLI 与 MCP 两种接入方式的技术架构与差异对比

* **FR-4**: 整理核心命令的使用方法与输出格式说明（搜索、热榜、直答、个人数据）

* **FR-5**: 分析供应链安全设计与凭证存储机制

* **FR-6**: 汇总实战玩法（创作数据分析、风格蒸馏、选题雷达等）

* **FR-7**: 介绍生态集成方案（Codex、Claude Code、Cursor 等）

## Non-Functional Requirements

* **NFR-1**: 所有事实声明带 F 编号溯源，P0 级声明（数字、日期、官方表态）经权威交叉核验

* **NFR-2**: 发现源文错误时不静默照搬，新增勘误记录并在正文呈现正确值

* **NFR-3**: 知识包遵循 OKF v0.2 目录结构与 frontmatter 规范

* **NFR-4**: 时效性内容（如额度、版本号）标注 stale\_after 日期

* **NFR-5**: 相对链接全部可达，toctree 结构完整

## Constraints

* **Technical**: 产出物为 Markdown 格式的 OKF v0.2 知识包，存放于 git submodule `projects/awesome-okf-xs/` 内

* **Business**: 免费试用额度、版本号等信息具有时效性，需明确标注时点

* **Dependencies**: 6篇公开文章作为主要信源，P0 核验通过 WebSearch 补充官方权威信源

## Assumptions

* 知乎开放平台处于邀测阶段，免费额度 5000 次/天（以官方最新为准）

* Zhihu CLI 当前稳定版本约 v0.5.x，更新较快

* Skill 方式为官方主推的 first-party 接入方式

* Windows PowerShell 5.1 的 UTF-8 编码问题是已知安装坑点

## Acceptance Criteria

### AC-1: 产品定位与能力矩阵完整

* **Given**: 读者打开知识包首页

* **When**: 浏览 concepts/ 首篇概念文档

* **Then**: 能清晰了解知乎数据开放平台的定位、核心产品矩阵、技术特点与应用场景

* **Verification**: `rubric`

* **Notes**: 评分维度：完整性（覆盖平台定位/产品矩阵/内容质量保障/应用场景）、准确性（与官方介绍一致）、可读性

### AC-2: 安装配置教程可复现

* **Given**: 读者按照教程步骤操作

* **When**: 从注册到完成 CLI 安装验证

* **Then**: 能成功获取 Access Secret 并完成 CLI 基本验证，包含常见坑点的规避说明

* **Verification**: `rubric`

* **Notes**: 评分维度：步骤完整性、平台覆盖度（Windows/Linux/macOS）、坑点提示充分性

### AC-3: 两种接入方式对比清晰

* **Given**: 读者想了解接入方式

* **When**: 阅读相关概念文档

* **Then**: 能明确 Skill+CLI 与 MCP 两种方式的技术架构差异、优缺点与适用场景

* **Verification**: `rule`

* **Notes**: 必须包含架构图或对比表，调用链路清晰

### AC-4: 核心命令使用说明完整

* **Given**: 读者已完成安装

* **When**: 查阅 examples/ 中的命令使用示例

* **Then**: 能掌握 search/hot/answer/me 四类核心命令的基本用法与输出格式

* **Verification**: `rubric`

* **Notes**: 评分维度：命令覆盖度、示例有效性、输出格式说明清晰度

### AC-5: 安全设计分析深入

* **Given**: 读者关注安全性

* **When**: 阅读安全相关章节

* **Then**: 能了解供应链校验机制、凭证存储方案、权限最小化设计

* **Verification**: `rule`

* **Notes**: 四道校验（官方域名/文件大小/SHA-256/版本自报）必须明确列出

### AC-6: 实战玩法丰富有启发

* **Given**: 读者想探索高级用法

* **When**: 浏览玩法相关概念文档

* **Then**: 能了解至少3种有价值的实战玩法及其实现思路

* **Verification**: `rubric`

* **Notes**: 评分维度：玩法数量（≥3种）、创新性、可操作性说明

### AC-7: 事实溯源完整准确

* **Given**: 审查者核对知识包

* **When**: 检查 references/ 与正文引用

* **Then**: 所有数字、日期、产品名、官方表态等关键事实均有 F 编号溯源，P0 项有核验记录

* **Verification**: `rule`

* **Notes**: 双份 F 编号一致（facts.md 与 article-source.md），无跳号或漂移

### AC-8: OKF 规范合规

* **Given**: 知识包已生成

* **When**: 执行 OKF 规范检查

* **Then**: 目录结构正确、frontmatter 字段完整、toctree 三级齐全、相对链接全部可达

* **Verification**: `rule`

* **Notes**: 手动等效验证 §7 机械门禁清单

## Open Questions

* [ ] 知识包归属哪个技术域/分组？（初步建议：AI Agent 域 → 工具/平台分组）

* [ ] 是否需要设立 examples/ 目录？（初步判定：是，包含安装和命令使用示例）

