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
- 2026-09-29 | docs | **凭证与网络信息脱敏**：应要求清除文档中的真实网络地址。`docs/06`、`docs/07` 中全部公网/内网 IP 与代理端口改为占位符（`<EGRESS_IPV4>` / `<LAN_IPV4>` / `<PROXY_PORT>` / `<IPV6_PREFIX>`），出口 IP 改为「现场 `curl -4 --noproxy '*' https://ipinfo.io/ip` 查询」的操作指引；本文档同处亦一并脱敏。确立约定：**真实网络地址不落文档、不入库**。
- 2026-09-29 | docs | **新增 `docs/06-credential-probe-2026-09-29.md`**（微信凭证联调实测记录）：`official-doctor` 分阶段结果（config/network 通过、token 因 `40164 invalid ip` 被拦、batchget 跳过）；记录两条环境陷阱——**系统代理会让 localhost 探测返回误导性 502，须加 `--noproxy '*'`**；**`requires-python>=3.14` 门槛可经 `PYTHONPATH=src` 直调模块绕过**；登记 R2 采集服务未部署（无 Docker、Podman machine 未启动、缺 `collector.env`）与 R1 主体权限前提。已同步 `docs/README.md` 索引。
- 2026-09-29 | docs | **`docs/08-48001-auth-gate-and-path-decision.md` 追加 §10「认证提交后的复测与等待期」**：用户提交微信认证后复测 **仍 48001**，同 token 三接口权限分布与提交前完全一致 → 认证状态未落到接口层，属审核期正常表现。补充官方生效时序（审核费 300 元/次 → **审核 1–3 个工作日** → 通过后**即时开通**；付款≠生效；有效期 1 年需年审，逾期权限断开）、用户侧状态自查路径（设置→微信认证）、生效唯一判据（`[batchget]` 由 `48001` 转 `[ok]`），并**警示不要用轮询探针试生效**（batchget 实页探测消耗当日配额，上限默认 90，审核期内白耗且结果必然相同）。同时给出审核期可并行事项：启动 R2 采集服务（不依赖认证，才是历史全量主路径）。

## 规则主题演进

| 规则文件 | 引入日期 | 当前覆盖 |
|---------|---------|---------|
| [rules/archive-pipeline.md](rules/archive-pipeline.md) | 2026-09-28 | §1 限速 · §2 回环绑定 · §3 凭证 · §4 幂等续跑 · §5 熔断矩阵 · §6 结构感知风控 · §7 退出码 · §8 官方接口 · §9 派生产物 · §10 合规落地 |