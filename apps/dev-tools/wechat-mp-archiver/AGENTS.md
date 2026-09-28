---
id: "wechat-mp-archiver-agents-manifest"
title: "wechat-mp-archiver AI 协作者入口"
source: "apps/AGENTS.md#应用路由表"
---
# wechat-mp-archiver - AI 协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文（含首部「启动协议」四个字）
> 步骤 2：确认父级工作区 — 本应用是 SpecWeave apps/dev-tools/ 下的独立归档工具：
>         ../../AGENTS.md（apps 应用区入口）、../../../AGENTS.md（SpecWeave 根契约）、
>         ../../../.agents/（根 AI 资产容器）；dev-tools 为普通分组，无组级 AGENTS.md
> 步骤 3：文档边界 — 对外人类可读文档唯一入本应用 docs/（docs/README.md 为索引入口）；
>         .agents/ 只放 AI 资产；禁止向 .agents/docs/ 写入任何产出物（该路径已废止）
> 步骤 3.5：自检 — 逐项勾选：
>   □ 已完成内容敏感度预检（本应用=公开开源代码；产出物落本应用 docs/ 或应用目录内，
>     禁止向 .agents/docs/ 写入任何产出物）
>   □ 父级 AGENTS.md 已回读磁盘原文（启动协议步骤 1.1），与系统注入一致
>   □ 改动涉及限速/熔断/凭证/退出码/合规边界时已加载 .agents/rules/archive-pipeline.md
>   □ 新增网络请求路径已复用 http_client.py 的限速与退避能力（未裸直连）
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 **apps/dev-tools/wechat-mp-archiver（微信公众号全量内容归档工具）** 的应用级路由入口，
> 只承载本应用特有事实；未覆盖的规则逐级回退父级（见「上下文路由表」末两行）。

## 项目概述

- **应用性质**：微信公众号全量内容归档工具——私有部署的开源采集服务（R2 主路线）提供文章列表，本机 Python 薄管线（`mp-archiver` CLI）完成正文/富媒体下载、元数据管理、断点续采与增量更新
- **三种产出形态**：① 离线归档（原始 HTML 快照 + 本地化图片 + Markdown，`archive/<账号>/<年>/<日期_标题>/`）；② RAG 语料（带 YAML frontmatter 的纯文本 JSONL，`exports/rag.jsonl`）；③ 分析报表（更新趋势、失败/对账清单，`exports/report/`）
- **架构边界**：采集服务承载微信登录态、向管线提供列表接口（仅绑 `127.0.0.1:5000`）；管线只经回环取列表，正文与媒体**直连** `mp.weixin.qq.com`（剥离采集服务 Token），数据全部落地本机；派生产物为**纯离线**任务，不触网
- **技术栈**：Python ≥ 3.14；scikit-build-core 纯 Python 包（`mp-archiver` CLI）；pydantic-settings 配置（`MP_ARCHIVER_` 前缀）；SQLite 五表状态机（articles/media/comments/metrics/sync_state）；采集服务经 Docker 私有部署（NAS 可用多架构镜像）
- **关键外部输入**：专用订阅号**管理员本人扫码登录态**（经验约 4 天有效）；可选 `appmsg_token`/`pass_ticket`（互动数据，默认关闭）；可选 AppID/AppSecret（自有认证号官方清单交叉补全）
- **父级工作区**：[../../AGENTS.md](../../AGENTS.md)（apps 应用区）→ [../../../AGENTS.md](../../../AGENTS.md)（SpecWeave 根契约）
- **AI 资产容器**：[.agents/](.agents/README.md)（仅一个规则主题 `rules/archive-pipeline.md`）
- **人类文档**：[docs/](docs/README.md)（索引 + 6 篇）
- **规格与方案**：规格 [spec.md](../../../.trae/specs/wechat-mp-content-archiver/spec.md) / [tasks.md](../../../.trae/specs/wechat-mp-content-archiver/tasks.md)；技术方案 [wechat-mp-full-archive-solution.md](../../../docs/knowledge/operations/wechat-mp-full-archive-solution.md)

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、七概念指令）
  └─ apps/AGENTS.md（应用区入口路由）
       └─ apps/dev-tools/wechat-mp-archiver/AGENTS.md（本文件 = 应用级路由入口）
            ├─ README.md                        ← 人类入口：定位、快速开始、命令速查、文档索引
            ├─ docs/                            ← 人类可读文档（索引 + 6 篇）
            │    ├─ README.md                   ← 文档索引
            │    ├─ 00-overview.md              ← 定位 / 三种产出形态 / 架构图 / 职责边界
            │    ├─ 01-quickstart.md            ← 安装 + 从零到单篇七步演练 + 账号准备与凭证管理
            │    ├─ 02-commands.md              ← 命令总览 + sync/run 编排与退出码契约 + list/fetch/export-rag/report 详解
            │    ├─ 03-operations.md            ← 默认限速与核定依据 + 故障处置与断点续跑 + 故障排查速查
            │    ├─ 04-storage-and-layout.md    ← 存储布局 + 源码结构 + 仓库内其他目录
            │    └─ 05-compliance.md            ← 合规声明六条（含 24 小时删除义务）
            ├─ .agents/                         ← 本应用 AI 资产容器
            │    ├─ README.md                   ← 资产索引 + 核心资产真源 + 父级回退链
            │    ├─ CHANGELOG.md                ← 应用变更日志（原子提交汇总）
            │    └─ rules/archive-pipeline.md   ← 唯一规则主题：归档管线硬约束（§1-§10）
            ├─ deploy/                          ← 采集服务私有部署（docker-compose + collector.env.example + deploy/README.md + sync-incremental.ps1）
            ├─ src/mp_archiver/                 ← Python 包：config/models/logging_utils/naming/http_client + db/ + adapters/ + core/ + exporters/
            └─ tests/                           ← pytest 测试集（验收 / 故障注入 / CLI / 导出 / 适配器）
```

**嵌套优先原则**：进入 `src/`、`tests/`、`deploy/` 后仍以本文件为最近入口；未覆盖规则按 本应用 → apps → SpecWeave 根 逐级回退（`dev-tools/` 为普通分组，无组级 AGENTS.md）。

## 上下文路由表（任务类型 → 入口）

| 任务类型 | 必读入口 |
|---------|---------|
| 新增/修改网络请求路径（限速、退避、熔断） | [.agents/rules/archive-pipeline.md](.agents/rules/archive-pipeline.md) §1 §5 + `src/mp_archiver/http_client.py`（唯一实现，禁止裸直连） |
| 改配置项与默认值 | `src/mp_archiver/config.py`（单一事实源）+ [.agents/rules/archive-pipeline.md](.agents/rules/archive-pipeline.md) §1（限速默认值即推荐值）+ [docs/03-operations.md](docs/03-operations.md) |
| 改凭证处理 / 日志脱敏 | `src/mp_archiver/logging_utils.py` + `src/mp_archiver/core/credentials.py` + [.agents/rules/archive-pipeline.md](.agents/rules/archive-pipeline.md) §3 |
| 改状态机 / 幂等续跑 / 故障分类 | `src/mp_archiver/db/schema.sql` + `src/mp_archiver/core/pipeline.py` + [.agents/rules/archive-pipeline.md](.agents/rules/archive-pipeline.md) §4 §5 |
| 改正文归档与风控判定 | `src/mp_archiver/core/article_archive.py` + [.agents/rules/archive-pipeline.md](.agents/rules/archive-pipeline.md) §5 §6（**结构感知，禁止全文子串匹配**） |
| 改 CLI 命令面 / 退出码 | `src/mp_archiver/cli.py` + [.agents/rules/archive-pipeline.md](.agents/rules/archive-pipeline.md) §7 + [docs/02-commands.md](docs/02-commands.md) |
| 改官方接口适配（biz/配额/降级） | `src/mp_archiver/adapters/official_api.py` + `src/mp_archiver/core/official_sync.py` + [.agents/rules/archive-pipeline.md](.agents/rules/archive-pipeline.md) §8 |
| 改 RAG / 报表导出 | `src/mp_archiver/exporters/` + `src/mp_archiver/core/text_extract.py` + [.agents/rules/archive-pipeline.md](.agents/rules/archive-pipeline.md) §9 + [docs/02-commands.md](docs/02-commands.md) |
| 改采集服务部署（compose / 端口 / Token） | [.agents/rules/archive-pipeline.md](.agents/rules/archive-pipeline.md) §2 + [deploy/README.md](deploy/README.md) + `deploy/docker-compose.yml`（**仅绑 127.0.0.1，禁公网**） |
| 合规边界争议 / 功能涉及权限与付费 | [docs/05-compliance.md](docs/05-compliance.md) + [.agents/rules/archive-pipeline.md](.agents/rules/archive-pipeline.md) §10 + 方案文档第六节 |
| 日常使用与排障（人类操作） | [docs/01-quickstart.md](docs/01-quickstart.md) / [docs/03-operations.md](docs/03-operations.md)（故障排查速查索引） |
| 全局提交与代码规范 | [../../../AGENTS.md](../../../AGENTS.md) → [../../../.agents/global-core-rules.md](../../../.agents/global-core-rules.md) |
| Skill 与七概念指令 | [../../../.agents/skills/README.md](../../../.agents/skills/README.md) / [../../../.agents/commands/README.md](../../../.agents/commands/README.md) |

## P0 约束速览（违反 = 打回）

| # | 约束 | 权威事实源 |
|---|------|-----------|
| 1 | **保守限速不可下调，默认值即推荐值**：2–5 秒/篇随机间隔 + 指数退避封顶 60 秒；保守方向来自平台事实，2–5 秒区间为本项目工程判断（非平台阈值）；新增网络路径必须复用 `http_client.py` | [archive-pipeline.md](.agents/rules/archive-pipeline.md) §1 |
| 2 | **采集服务只绑回环**：仅监听 `127.0.0.1:5000`，`deploy/docker-compose.yml` 禁止公网绑定；正文与媒体直连微信、剥离采集服务 Token | 同上 §2 |
| 3 | **凭证只走 `.env` 且日志脱敏**：不入库、不进日志；仅用管理员本人扫码登录态；不共享账号、不转售凭证 | 同上 §3 |
| 4 | **幂等与断点续跑**：五表状态机即时落库；半成目录重跑整体清空重建；普通重跑只采 pending，仅 `--include-failed` 才重试失败篇 | 同上 §4 |
| 5 | **故障作用域分流**：403/验证码为账号级**立即熔断**；传输/5xx 连续 2 篇才熔断；404 与媒体失效按单篇/资源级隔离；退避日志只记主机名 | 同上 §5 |
| 6 | **风控判定必须结构感知**：基于 `#js_content` 缺失/为空判定，**禁止全文子串匹配**（历史误报缺陷） | 同上 §6 |
| 7 | **退出码契约冻结**：`0` 成功 / `1` 失败或参数错误 / `2` 登录态失效 / `3` 账号未找到 / `4` 环境或风控异常 | 同上 §7 |
| 8 | **官方接口边界**：仅用于自有认证号；48001 自动降级退出码 0；日配额守护 90 次（UTC 日滚动） | 同上 §8 |
| 9 | **派生产物纯离线且原子覆盖**：`export-rag`/`report` 不触网、幂等、临时文件 + 原子覆盖；统计口径须在报表页首声明并附对账 SQL | 同上 §9 |
| 10 | **合规条款为发布硬约束**：个人学习限定、不绕付费与权限、尊重版权、频率自律、凭证安全、**24 小时删除义务** | [docs/05-compliance.md](docs/05-compliance.md) + 同上 §10 |

## 变更日志

完整条目见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)。

- 2026-09-28 | docs | 文档体系重构：README.md 原子化为 `docs/`（索引 + 6 篇）；README 瘦身为人类入口
- 2026-09-28 | chore | AI 资产容器初始化：新增应用级 `AGENTS.md` + `.agents/`（README + CHANGELOG + `rules/archive-pipeline.md`）；本应用由「遵循根规范」升级为**应用自治**，同步 `apps/AGENTS.md` 路由表与边界声明