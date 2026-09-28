---
id: "wechat-mp-archiver-agents-changelog"
title: "wechat-mp-archiver 应用变更日志"
source: "../AGENTS.md#变更日志"
---
# 应用变更日志

本文件记录 `apps/dev-tools/wechat-mp-archiver` 的规范与工程变更（原子提交汇总）。
格式：`日期 | 类型 | 摘要`（类型遵循 Conventional Commits 的 type 词表）。

## 2026-09

- 2026-09-28 | docs | **文档体系重构**：`README.md` 原子化为 `docs/`（索引 + `00-overview` 定位与架构 / `01-quickstart` 快速开始与凭证 / `02-commands` 命令与退出码 / `03-operations` 限速故障处置与排障 / `04-storage-and-layout` 存储与源码结构 / `05-compliance` 合规声明六条）；README 瘦身为人类入口。
- 2026-09-28 | chore | **AI 资产容器初始化**：新增应用级 `AGENTS.md`（启动协议 + 项目概述 + 嵌套路由关系 + 上下文路由表 + P0 约束速览）与 `.agents/`（`README.md` 资产索引 + `CHANGELOG.md` + `rules/archive-pipeline.md` 唯一规则主题）；本应用由「遵循根规范」升级为**应用自治**，同步 `apps/AGENTS.md` 路由表与边界声明。

## 规则主题演进

| 规则文件 | 引入日期 | 当前覆盖 |
|---------|---------|---------|
| [rules/archive-pipeline.md](rules/archive-pipeline.md) | 2026-09-28 | §1 限速 · §2 回环绑定 · §3 凭证 · §4 幂等续跑 · §5 熔断矩阵 · §6 结构感知风控 · §7 退出码 · §8 官方接口 · §9 派生产物 · §10 合规落地 |