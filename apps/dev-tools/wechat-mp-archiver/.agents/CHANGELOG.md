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
- 2026-09-29 | docs | **新增 `docs/06-credential-probe-2026-09-29.md`**（微信凭证联调实测记录）：`official-doctor` 分阶段结果（config/network 通过、token 因 `40164 invalid ip <EGRESS_IPV4>` 被拦、batchget 跳过）；记录两条环境陷阱——**系统代理 `http_proxy=127.0.0.1:<PROXY_PORT>` 会让 localhost 探测返回误导性 502，须加 `--noproxy '*'`**；**`requires-python>=3.14` 门槛可经 `PYTHONPATH=src` 直调模块绕过**；登记 R2 采集服务未部署（无 Docker、Podman machine 未启动、缺 `collector.env`）与 R1 主体权限前提。已同步 `docs/README.md` 索引。
- 2026-09-29 | docs | **新增 `docs/08-48001-auth-gate-and-path-decision.md`**：IP 白名单生效后（`40164` 消失、`token` 阶段 `[ok]`、token 长度 137 独立复现），探针进到 `batchget` 阶段报 `48001 api unauthorized`。以**同 token 对比测试**定性——`material/get_materialcount` ✅、`draft/batchget` ✅、**仅 `freepublish/batchget` ❌** → 不是账号级无权限而是单接口无权限；据官方社区口径（2025-07 起个人主体/未认证/不支持认证账号**回收发布能力相关接口**权限；社区标准答复"发布能力接口需完成微信认证"）判定为**账号主体认证门槛**，非配置问题。同时明确 **R1 与 R2 定位**：R1 官方接口仅覆盖"发布成功"图文、**不含群发历史**，历史全量只能靠 R2 → 推进归档的正确动作是启动 R2 采集服务（当前缺口：无 Docker/CLI、Podman machine 未启动、缺 `collector.env`），并给出是否走认证的决策项。已同步 `docs/README.md` 索引。

## 规则主题演进

| 规则文件 | 引入日期 | 当前覆盖 |
|---------|---------|---------|
| [rules/archive-pipeline.md](rules/archive-pipeline.md) | 2026-09-28 | §1 限速 · §2 回环绑定 · §3 凭证 · §4 幂等续跑 · §5 熔断矩阵 · §6 结构感知风控 · §7 退出码 · §8 官方接口 · §9 派生产物 · §10 合规落地 |