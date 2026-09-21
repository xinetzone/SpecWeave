---
title: "开源工具替代订阅费 OKF Wiki"
status: "completed"
date: "2026-09-20"
methodology: "seven-concepts-cmd: R -> I -> E -> V"
content-sensitivity: "public"
source: "https://mp.weixin.qq.com/s/RLsYjpbzUxdQU4U6ylTkTw"
---

# 开源工具替代订阅费 OKF Wiki 需求

## 概述

将 AI 识局《这五个项目，正在替掉你每月那笔订阅》转化为可溯源的 OKF v0.2 知识包，覆盖 Orca、God's Eye View、HyperFrames、Scrapling 与 OpenSEO。重点解释开源替代的成本迁移，而不是把“开源”误写成“零成本”。

## 内容判定与归属

- 内容级别：公开。微信公众号链接无 `code`、`token` 或登录控制参数。
- 内容性质：技术综述，包含部分可复现安装/启动片段。
- `examples/` 判定：两问均为“部分是”。原文给出了 HyperFrames、Scrapling、OpenSEO 的命令和 God's Eye View 的运行前置，但未提供完整版本锁定、输入输出和真机日志；因此 examples 仅呈现“官方路径重组”，不声称本文作者实测。
- 归属位置：`jishu/ai/agent-platform-notes/`。五个项目跨 Agent、空间数据、视频、抓取和 SEO，落入既有散篇聚合组，避免为单篇文章新增顶级分组。

## 七概念链路

- R：读取微信正文，登记五个项目的声明、价格、许可证、安装路径和限制，区分原文单源与官方补充。
- I：抽象“替代订阅 = 成本结构迁移”与“开源软件层/数据服务层/运维层分离”两条洞察。
- E：按项目形态拆分为五篇概念文档和三篇安装/评估示例。
- V：执行四视角审查、F 编号双表核对、toctree/相对链接/UTF-8/计数检查；未独立验证的价格和星标保留 `flagged`。

## 事实与边界

- 文章星标、订阅价格、节省金额与“替代”判断多为文章或第三方口径，不作为普遍成本结论。
- Orca 仍依赖用户已有模型订阅；God's Eye View 仍可能需要地图、影像和数据服务密钥；OpenSEO 仍依赖 DataForSEO。
- HyperFrames 的本地渲染、Scrapling 的自托管只消除部分托管费用，不能消除算力、带宽、代理、维护与合规成本。
- 不执行付费 API、不安装五个项目、不登录第三方服务，不把示例命令写成已实测结果。

## 验收标准

### AC-1 事实溯源

- **Type**: `rule`
- 五个项目均有 F 编号，文章数字与官方资料分层；`facts.md` 与 `article-source.md` 编号集合连续一致。

### AC-2 教学结构

- **Type**: `rubric`
- 概念文档覆盖五个项目的定位、成本边界和适用场景；示例文档明确“官方路径重组，未真机执行”。

### AC-3 反营销边界

- **Type**: `rule`
- 所有“替代订阅”“每月价格”“免费/零成本”主张均带来源和限制；关键数字无法独立核验时 bundle 为 `flagged`。

### AC-4 导航与编码

- **Type**: `rule`
- 根、子目录及父级分组 toctree 完整；相对链接可达；Markdown 为 UTF-8；不声称未运行的 `invoke` 门禁通过。
