---
type: spec
title: "CreatorHub 微信博文 → OKF v0.2 Wiki 教程知识包"
source: ".trae/specs/creatorhub-blog-okf-wiki/raw/article-raw.md"
source_url: "https://mp.weixin.qq.com/s/Y5AvYGtyj2t9xPJIXuSYBA"
status: active
generated_at: "2026-10-26"
---

# CreatorHub 微信博文 → OKF v0.2 Wiki 教程知识包

## Overview

把微信公众号「明见如是」2026-08-28 发布的《发现一个自媒体效率神器：CreatorHub，一个本地面板，把抖音小红书快手视频号全管了》转化为 OKF v0.2 知识包（Wiki 教程形态），落点 `projects/awesome-okf-xs/doc/bundles/jishu/ai/products/creatorhub/`。

按七概念方法论编排（`seven-concepts-cmd`）走**场景 4 知识沉淀链路 R→I→E→V→C**。

| 项 | 值 |
|---|---|
| 源文 URL | https://mp.weixin.qq.com/s/Y5AvYGtyj2t9xPJIXuSYBA |
| 源文标题 | 发现一个自媒体效率神器：CreatorHub，一个本地面板，把抖音小红书快手视频号全管了 |
| 发布方 | 微信公众号「明见如是」（个人号，互联网从业者自述） |
| 发布时间 | 2026-08-28 17:02 |
| 正文长度 | 1761 字（browser 提取 `#js_content`） |
| 内容敏感度 | **公开内容**（公开可访问文章，无 `share?code=` / token / 邀请码） |
| 工作流 | 标准工作流（spec 在 `.trae/specs/`，产出入子模块 `projects/awesome-okf-xs/`） |
| 目标落点 | `doc/bundles/jishu/ai/products/creatorhub/` |
| 信源距离 | **第三方公众号产品推介**（非厂商自宣通稿、非一手实测）；官方 README/仓库为核验源 |

## Goals

- G1：产出结构完整的 OKF v0.2 bundle，覆盖事实层（项目身份/版本）、机制层（本地面板架构/任务队列/风控）、路径层（安装/监控/采集/下载/发布）。
- G2：所有事实挂 F 编号，spec `facts.md` 与 bundle `references/article-source.md` 双份登记且编号集合逐字一致、连续无跳号。
- G3：P0 核验覆盖核心声明（仓库存在性、Star 时点、技术栈、许可、四平台能力边界、本地数据、Windows 安装版时效），产出核验报告与勘误清单。
- G4：三级 toctree（bundle index → products index → ai index → jishu index → bundles/index）与计数全部接入且自洽。
- G5：frontmatter 完整、相对链接可达、UTF-8 strict roundtrip 通过。

## Non-Goals

- 不复现真实平台登录与采集（涉及账号、Cookie、风控，且需实机与网络环境）；examples 只覆盖官方 README 可逐字照做的安装、启动、界面路径与配置项。
- 不为任何平台规则背书，不提供绕过风控/规避平台限制的方法。
- 不评价项目商业价值与 Star 增长归因（无独立数据）。
- 不将“开源”作为既定事实；许可状态单列勘误。

## 骨架判定（操作可复现性两问）

1. 是否有读者可照做的安装/配置/调用/实测流程？**是**（Windows 安装版、源码启动、start 命令、账号添加、监控/采集/下载/发布路径、配置项均有官方步骤）。
2. 这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？**是**（官方 README 给出环境要求、命令、界面路径与 v0.2.4 版本口径；本地未实机复跑，边界在 index 声明）。

结论：两问皆“是” → 设 `examples/`（4 篇）。

## 归属判定

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/products/` | **采用** | 同组已有 OpenCreator（本地优先创作者工作台）、VidBee（视频下载/转录）、wigolo（本地 Web 工具）等“终端工具 + 博文核验”先例；CreatorHub 是多平台内容运营工具，归类读者意图明确 |
| `jishu/web/` | 否 | 虽用 FastAPI，但读者找的是“内容运营工具”，不是 Web 框架学习 |
| `jishu/dev/` | 否 | 非开发协作工具 |
| 新建分组 | 否 | 单篇博文禁止新建分组（反模式 3） |

## 三层知识拆分

- 事实层（首篇）：项目身份、时间线、版本、Star、许可状态、博文与官方口径差异。
- 机制层（中部）：本地优先架构（FastAPI + CDP/Patchright + SQLite + 独立 Profile）、平台能力矩阵、任务队列与保守风控。
- 路径层（尾篇 + examples）：Windows/源码安装、账号与监控、采集/下载/发布、风控与排障；边界篇收束许可、合规与安全。

## 验收标准

- bundle 文件数：16（根 index/log + concepts 6 + examples 5 + references 3）。
- F 编号：F-001~F-072，连续无跳号，双份一致。
- P0/P1 核验：23 项（✅14 / ⚠️7 / ❌2），核心功能声明成立，“开源”许可声明不成立 → `status: flagged`。
- 计数：products 34→35、ai 268→270（本束 +1，另 +1 修正既有 practice 计数漂移）、jishu 500→502、total 679→681。
