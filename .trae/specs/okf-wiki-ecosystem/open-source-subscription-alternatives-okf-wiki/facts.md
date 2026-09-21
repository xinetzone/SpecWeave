---
title: "五个开源工具事实登记"
type: Reference
source: "https://mp.weixin.qq.com/s/RLsYjpbzUxdQU4U6ylTkTw"
date: "2026-09-20"
---

# 五个开源工具事实登记

> W = 微信原文；O = 项目官方仓库/文档；P = PyPI；T = 第三方价格或产品目录。文章正文约 11,887 字符（去重后），未执行项目安装或付费调用。

| 编号 | 声明 | 来源 | 状态与边界 |
| --- | --- | --- | --- |
| F-001 | 文章标题为“这五个项目，正在替掉你每月那笔订阅”，公众号为 AI识局，页面显示 2026-09-20 11:30、浙江。 | W | 页面元信息已读 |
| F-002 | 文章讨论 Orca、God's Eye View、HyperFrames、Scrapling、OpenSEO 五个项目。 | W | 文章结构已读 |
| F-003 | Orca 使用独立 git worktree 让多个 CLI 编程 Agent 并行，再比较和合并结果。 | W、O | 机制已获仓库/第三方描述支持 |
| F-004 | Orca 使用已有模型订阅或 API key，不提供模型额度；并行 Agent 会叠加底层调用成本。 | W、O | 成本结构成立，实际账单未测 |
| F-005 | Orca 提供 Design Mode、diff 批注、SSH worktree、移动端通知和 CLI 操作。 | W、O | 功能声明，版本会变 |
| F-006 | Orca 仓库为 `stablyai/orca`，文章将其标为 MIT 开源。 | W、O | 以仓库当前许可证为准 |
| F-007 | God's Eye View 将航班、船舶、卫星、地震、摄像头等公开信号放在浏览器 3D 地球中。 | W、O | 数据层存在延迟、模拟或估计状态 |
| F-008 | God's Eye View 的部分图层可免密钥运行，照片级地图、语音或服务配额可能需要密钥/计费。 | W、O | “免密钥”不等于零成本 |
| F-009 | God's Eye View 的交通、摄像头位姿和发射回放可能是模拟、估计或重建，不应一律视为实时观测。 | W、O | 官方 README 明示边界 |
| F-010 | God's Eye View 仓库为 `bilawalsidhu/gods-eye-view`，文章按 MIT 文本描述。 | W、O | 许可证以仓库文件为最终依据 |
| F-011 | HyperFrames 用 HTML、CSS、媒体和可寻址动画渲染 MP4，定位为 agent-friendly。 | W、O | 官方口号为“Write HTML. Render video. Built for agents.” |
| F-012 | HyperFrames 支持 `npx hyperframes init/preview/lint/render` 工作流。 | W、O | 命令需按当前版本复核 |
| F-013 | HyperFrames 支持 GSAP、Lottie、CSS、Three.js 等 Frame Adapter。 | W、O | 具体适配器随版本变化 |
| F-014 | HyperFrames 为 Apache-2.0 开源项目，本地渲染不收按次托管费。 | W、O | 云渲染仍有云或厂商成本 |
| F-015 | HyperFrames 要求 Node.js 22+ 与 FFmpeg；文章称仍处于 0.8.x。 | W、O | 版本为时间快照 |
| F-016 | Scrapling 是 Python 自适应 Web Scraping 框架，支持从单请求到完整爬虫。 | W、O、P | 官方文档与 PyPI 支持 |
| F-017 | Scrapling 可用 `auto_save=True` 保存元素特征，后续用 `adaptive=True` 适应页面改版。 | W、O | 需在目标站点自行验证误匹配率 |
| F-018 | Scrapling 提供 Fetcher、StealthyFetcher、DynamicFetcher 与 Scrapy 风格 Spider。 | W、O | 反爬能力不代表绕过所有企业防护 |
| F-019 | Scrapling 需要 Python 3.10+；抓取器可通过 `pip install "scrapling[fetchers]"` 与 `scrapling install` 配置。 | W、O、P | 安装命令未在本任务执行 |
| F-020 | Scrapling 的许可证为 BSD-3-Clause。 | O、P | 以项目仓库和发行元数据为准 |
| F-021 | OpenSEO 定位为 Semrush/Ahrefs 的开源、自托管或按量替代方案。 | W、O、T | “替代”是产品定位，不是功能等价证明 |
| F-022 | OpenSEO 覆盖关键词、排名、竞品、反向链接、站点审计和 AI 可见性。 | W、O、T | 数据覆盖由上游服务决定 |
| F-023 | OpenSEO 提供 MCP 入口和 Agent Skills，可接入支持 MCP 的客户端。 | W、O、T | 具体客户端支持随版本变化 |
| F-024 | OpenSEO 的 SEO 数据依赖 DataForSEO key，自托管不等于数据服务免费。 | W、O、T | 上游计费与配额需单独核算 |
| F-025 | OpenSEO 可通过 Docker 或 Cloudflare 路径部署；Docker 示例使用 `.env` 和 `docker compose up -d`。 | W、O、T | 未在本任务部署 |
| F-026 | OpenSEO 软件仓库为 `every-app/open-seo`，文章按 MIT 描述。 | W、O | 许可证以仓库当前文件为准 |
| F-027 | 文章将爬虫 API 入门价写为约 49 美元/月起。 | W | 原文/第三方口径，未形成统一市场基准 |
| F-028 | 文章将 SEO 套件入门价写为约 129–139 美元/月。 | W | 原文价格对照，需按产品、地区和计费周期复核 |
| F-029 | 文章将视频工具订阅写为每月 54.99 美元。 | W | 未指定产品与区域，不能作为普遍价格 |
| F-030 | 文章将 OpenSEO 托管版写为每月 10 美元加 API 成本，并提及 28% 加价。 | W、T | 价格和加价需查官方当前计划 |
| F-031 | 文章总体结论是开源替代把订阅费转移为本地算力、带宽、数据 API、代理、运维和维护时间。 | W | 作者/本教程共同抽象，非实验结论 |
| F-032 | 五个项目的功能描述、星标数字与价格对照未在本任务中全部通过同条件独立复现。 | W、O、T | bundle 使用 `flagged` |
