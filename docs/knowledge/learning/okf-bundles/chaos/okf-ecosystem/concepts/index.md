# 概念文档

* [00 — OKF 知识包生态概览](00-okf-overview.md) — okf-kit 与 okf-desktop 构成的生态总览，CLI 命令全景、模块架构、版本依赖
* [01 — Bundle 数据模型与语义边](01-bundle-data-model.md) — 目录结构、Page/PageRecord 数据类、frontmatter 规范、URL 映射、content_hash 与边计算策略
* [02 — 网站爬取与 Bundle 构建流水线](02-crawl-build-pipeline.md) — Fetcher 抽象、BFS 爬取、内容提取流水线、writer 写入、质量启发与 enrich
* [03 — 增量同步与安全阀门](03-sync-incremental.md) — state.json 恢复、三集合 diff、安全阀门阈值、post_sync 钩子
* [04 — MCP/Chat/HTTP 三模服务架构](04-service-modes.md) — 导航内核三原语、MCP 工具注册、Chat Agent 循环、HTTP API 路由、token 鉴权与 provider 抽象
* [05 — 桌面应用同进程架构与打包](05-desktop-architecture.md) — pywebview 窗口、进程内 uvicorn、token 传递、PyInstaller 打包配置与跨平台差异

```{toctree}
:maxdepth: 2

00-okf-overview
01-bundle-data-model
02-crawl-build-pipeline
03-sync-incremental
04-service-modes
05-desktop-architecture
```