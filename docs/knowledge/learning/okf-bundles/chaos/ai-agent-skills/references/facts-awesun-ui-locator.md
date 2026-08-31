---
type: Facts
title: "awesun-ui-locator 事实清单"
---

# awesun-ui-locator 事实清单

> R阶段事实采集。源码路径：d:\AI\.chaos\libs\awesun-ui-locator\
> 采集日期：2026-08-23

## 项目概述

- F-001: 项目名称为"Awesun UI Locator - 截图 UI 元素定位器"，用于分析桌面截图并精确定位 UI 元素 — 源码：`README.md:1-3`
- F-002: 通过 AI 视觉模型识别截图中的按钮、输入框、图标等界面元素，返回标准化坐标位置 — 源码：`README.md:3`
- F-003: 核心功能包括智能识别、精确定位（归一化坐标 x_norm/y_norm，范围 [0.0, 1.0]）、多种元素支持、多格式支持、上下文理解 — 源码：`README.md:7-11`
- F-004: 前置条件包括 Python 3.7+（坐标计算工具）、向日葵客户端 16.3.2+ — 源码：`README.md:46-53`
- F-005: 支持的 AI 编辑器包括 Claude Code、Open Code、OpenClaw — 源码：`README.md:55-58`

## SKILL.md 结构

- F-006: SKILL.md frontmatter 包含 name（screenshot-ui-locator）和 description 两个字段 — 源码：`SKILL.md:1-4`
- F-007: description 描述技能用途：引导 AI 视觉模型识别桌面截图中的 UI 元素位置并返回归一化坐标 — 源码：`SKILL.md:3`
- F-008: SKILL.md 定义了 5 步工作流程：读取图片→理解用户意图→视觉分析→计算归一化坐标→返回结果 — 源码：`SKILL.md:12-97`

## 工作流程

- F-009: 步骤 1 使用 read 工具读取用户提供的图片文件，工具自动将图片转换为 base64 格式展示给视觉模型 — 源码：`SKILL.md:14-31`
- F-010: 支持图片格式包括 PNG（.png）、JPEG/JPG（.jpg、.jpeg）及其他常见格式 — 源码：`SKILL.md:33-36`
- F-011: 步骤 2 解析用户想要定位的 UI 元素类型：按钮、输入框、图标、文本元素等 — 源码：`SKILL.md:43-50`
- F-012: 步骤 3 视觉分析包括：整体观察布局→识别 UI 组件→匹配目标元素→精确定位像素位置→计算归一化坐标 — 源码：`SKILL.md:54-67`
- F-013: 归一化坐标公式为 x_norm = x_pixel / image_width，y_norm = y_pixel / image_height — 源码：`SKILL.md:71-75`
- F-014: 坐标系以左上角为原点 (0.0, 0.0)，右下角为 (1.0, 1.0) — 源码：`SKILL.md:79-81`
- F-015: 返回结果为 JSON 格式，包含 found（boolean）、element（string）、coordinates（{x, y}）、confidence（high/medium/low）、description — 源码：`SKILL.md:85-97`

## coordinate_utils.py 脚本

- F-016: coordinate_utils.py 是 UI 元素坐标计算工具，仅用于计算归一化坐标 — 源码：`scripts/coordinate_utils.py:1-5`
- F-017: calculate_coordinates() 函数接收 pixel_x、pixel_y、image_width、image_height 四个整数参数，返回归一化坐标元组 (x, y)，保留 6 位小数 — 源码：`scripts/coordinate_utils.py:10-31`
- F-018: validate_coordinates() 函数验证 x、y 是否在 [0.0, 1.0] 范围内，返回布尔值 — 源码：`scripts/coordinate_utils.py:34-45`
- F-019: format_coordinates() 函数将坐标格式化为字典 `{"coordinates": {"x": x, "y": y}}` — 源码：`scripts/coordinate_utils.py:48-59`
- F-020: 脚本使用 typing.Tuple 类型注解，无外部依赖 — 源码：`scripts/coordinate_utils.py:7`

## references/ui_patterns.md 参考文档

- F-021: ui_patterns.md 是 UI 元素识别参考，提供常见 UI 元素特征对照表和定位策略 — 源码：`references/ui_patterns.md:1-3`
- F-022: 按钮分类包括主要按钮、次要按钮、文字按钮、图标按钮、幽灵按钮，各有视觉特征和常见位置 — 源码：`references/ui_patterns.md:7-13`
- F-023: 输入框分类包括单行文本框、多行文本框、搜索框、密码框、下拉选择框 — 源码：`references/ui_patterns.md:17-23`
- F-024: 图标对照表列出 12 种常见图标（汉堡菜单、放大镜、齿轮、人像、房子、心形、铃铛、购物车、分享、垃圾桶、X、箭头）及其含义 — 源码：`references/ui_patterns.md:27-40`
- F-025: 导航元素包括 Tab 标签、面包屑、侧边栏、分页器、步骤条 — 源码：`references/ui_patterns.md:44-50`
- F-026: 反馈元素包括提示消息、加载动画、徽章/角标、工具提示 — 源码：`references/ui_patterns.md:54-59`
- F-027: 定位策略包括"先整体后局部"（理解页面结构→缩小搜索范围→精确定位）和"多特征匹配"（位置、颜色、形状、文字、图标结合） — 源码：`references/ui_patterns.md:61-80`

## 渐进式披露模式

- F-028: SKILL.md 作为主入口包含完整工作流程和坐标计算公式 — 源码：`SKILL.md:1-100`
- F-029: scripts/coordinate_utils.py 提供可执行的坐标计算和验证函数，供 AI 调用 — 源码：`scripts/coordinate_utils.py:1-59`
- F-030: references/ui_patterns.md 提供详细的 UI 元素视觉特征参考，作为 SKILL.md 的扩展知识 — 源码：`references/ui_patterns.md:1-80`
