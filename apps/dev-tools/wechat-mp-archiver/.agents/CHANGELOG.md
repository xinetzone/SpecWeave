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
- 2026-09-29 | docs | **新增 `docs/07-40164-blocker-followup.md`**（40164 第二轮排查，含自我纠错）：加白名单后仍报同一 `40164`。纠正首轮**误判**——首轮把 `ipv6 ::ffff:<EGRESS_IPV4>` 读成"需加 IPv6 白名单"，实测 `api.weixin.qq.com` **无 AAAA 记录**、`curl -6` 不通、连接源地址为内网 `<LAN_IPV4>` 经 NAT 出 `<EGRESS_IPV4>` → `::ffff:` 仅为回显格式，**微信不提供 IPv6 接入**。以两个受控实验推导**校验顺序：appid 存在性 → IP 白名单 → secret 校验**，并据此纠正"40164 说明 secret 正确"的无效推断（secret 错也报 40164，因未走到验签）。排除代理干扰 / 配置被覆盖 / IP 漂移；给出处置顺序（等生效窗口 → 核对白名单须位于"公众号后台→设置与开发→基本配置"、非功能设置栏/非开放平台 → CGNAT 兜底）。已同步 `docs/README.md` 索引。

## 规则主题演进

| 规则文件 | 引入日期 | 当前覆盖 |
|---------|---------|---------|
| [rules/archive-pipeline.md](rules/archive-pipeline.md) | 2026-09-28 | §1 限速 · §2 回环绑定 · §3 凭证 · §4 幂等续跑 · §5 熔断矩阵 · §6 结构感知风控 · §7 退出码 · §8 官方接口 · §9 派生产物 · §10 合规落地 |