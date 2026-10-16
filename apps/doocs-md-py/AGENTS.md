---
id: "doocs-md-py-agents-manifest"
title: "doocs-md-py AI 协作者入口"
source: "apps/AGENTS.md#应用路由表"
---
# doocs-md-py - AI 协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文（含首部「启动协议」四个字）
> 步骤 2：确认父级工作区 — 本应用是 SpecWeave apps/ 根级独立应用：
>         ../AGENTS.md（apps 应用区入口）、../../AGENTS.md（SpecWeave 根契约）、
>         ../../.agents/（根 AI 资产容器）；apps/ 根级无分组层 AGENTS.md
> 步骤 3：文档边界 — 面向人类可读的文档只入本应用 README.md 与 docs/（工程向 5 篇）；
>         .agents/ 只放 AI 资产；禁止向 .agents/docs/ 写入任何产出物（该路径已废止）
> 步骤 3.5：自检 — 逐项勾选：
>   □ 已完成内容敏感度预检（本应用 = 公开开源代码复刻；产出物落本应用 docs/ 或应用目录内）
>   □ 父级 AGENTS.md 已回读磁盘原文（启动协议步骤 1.1），与系统注入一致
>   □ 改动涉及渲染 / 服务端 / 上传 / CLI / MCP 时，已加载 .agents/rules/ 下对应主题文件
>   □ 改动触及上游契约口径时，已在 docs/contract-differences.md 登记 D-/CD- 编号
>   □ 新增模块已标注 `# upstream: <上游路径>:<行号>` 锚点注释
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 **apps/doocs-md-py（doocs/md 的 Python 3.14 复刻）** 的应用级路由入口，
> 只承载本应用特有事实；未覆盖的规则逐级回退父级（见「上下文路由表」末两行）。

## 项目概述

- **应用性质**：上游 `doocs/md` **v2.1.0**（commit `1bdad48d20048bddc8d32afb1b75a6475169f163`，2026-10-12）的**纯 Python 3.14 复刻**——同一渲染核心共用三条对外入口，原版 Vue3 前端**零源码修改**、由同源 FastAPI 托管其构建产物
- **三条入口**：① `mdpy` CLI（`render` / `serve` / `upload` / `mcp` / `migrate`）；② stdio MCP Server（JSON-RPC 2.0，13 工具，同名同 schema）；③ FastAPI HTTP 服务（认证 / 同步 / 分享 / 市场 / 表情 / 通知 / 上传 / 爱发电 webhook，+ 同源 SPA 托管）
- **渲染核心**：`src/doocs_md_py/render/`（27 模块）— front-matter → markdown-it-py token 遍历 → 12 扩展 → 净化 → 阅读时间 → 主题 CSS 装配，**无 I/O 副作用**，是三个入口的公共依赖
- **上游参照树（只读）**：`d:/AI/.chaos/libs/md` —— 所有契约争议**以该磁盘源码逐行对拍为准**（spec 假设 A1），本应用文档中的数字与磁盘冲突时**以磁盘为准**
- **技术栈**：Python ≥ 3.14；scikit-build-core 纯 Python 包（`doocs_md_py` / CLI `mdpy`）；FastAPI + uvicorn；SQLite 替代 Cloudflare D1（8 个迁移等价落地）；本地文件系统 + 手写 SigV4 S3 替代 R2 绑定；markdown-it-py 替代 marked；nh3 替代 DOMPurify
- **关键外部输入**：全部凭证由**部署者自备**（GitHub OAuth、图床密钥、S3/本地存储、爱发电）；**默认配置即可本地离线运行**，无凭证时相关功能优雅降级；不内置任何凭证或 AI Key
- **父级工作区**：[../AGENTS.md](../AGENTS.md)（apps 应用区）→ [../../AGENTS.md](../../AGENTS.md)（SpecWeave 根契约）
- **AI 资产容器**：[.agents/](.agents/README.md)（6 个规则主题 `rules/upstream-reconstruction.md`、`engineering-redlines.md`、`render-and-theme-contract.md`、`server-api-and-security.md`、`uploaders-dual-path.md`、`cli-and-mcp-contract.md`）
- **人类文档**：[README.md](README.md)（功能矩阵 / 快速开始 / CLI / 配置全表 / 图床 / MCP / 许可与来源）+ [docs/](docs/architecture.md)（工程向 5 篇，暂无索引页）
- **规格与方案**：规格 [.trae/specs/doocs-md-py/spec.md](../../.trae/specs/doocs-md-py/spec.md)；工程文档 [docs/architecture.md](docs/architecture.md)（上游映射总表）/ [docs/contract-differences.md](docs/contract-differences.md)（行为差异台账）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、七概念指令）
  └─ apps/AGENTS.md（应用区入口路由）
       └─ apps/doocs-md-py/AGENTS.md（本文件 = 应用级路由入口 · 根级独立应用）
            ├─ README.md                          ← 人类入口：功能矩阵、快速开始、配置全表、许可与来源
            ├─ docs/                              ← 人类可读工程文档（5 篇，暂无索引页）
            │    ├─ architecture.md               ← 架构分层 + 上游映射总表（AC-U2/AC-U3 依据）
            │    ├─ contract-mapping.md           ← 契约映射（端点/字段/常量对拍表）
            │    ├─ contract-differences.md       ← 行为差异台账（D-1..D-4 / CD-1..CD-21 + 裁决锚点）
            │    ├─ build-web-dist.md             ← 前端产物构建与回退路线
            │    └─ coverage-report-t20.md        ← 覆盖率门禁与性能基准实测报告
            ├─ .agents/                           ← 本应用 AI 资产容器
            │    ├─ README.md                     ← 资产索引 + 核心资产真源 + 父级回退链
            │    ├─ CHANGELOG.md                  ← 应用变更日志（原子提交汇总）
            │    └─ rules/                        ← 6 个单一职责规则主题
            │         ├─ upstream-reconstruction.md    ← 上游复刻与契约审计纪律（§1-§7）
            │         ├─ engineering-redlines.md       ← 工程红线、依赖白名单与质量门禁（§1-§7）
            │         ├─ render-and-theme-contract.md  ← 渲染管线与主题装配契约（§1-§8）
            │         ├─ server-api-and-security.md    ← 服务端契约、安全与配置治理（§1-§8）
            │         ├─ uploaders-dual-path.md        ← 图床双路径辨识与签名纪律（§1-§7）
            │         └─ cli-and-mcp-contract.md       ← CLI 退出码与 MCP 入参映射契约（§1-§7）
            ├─ src/doocs_md_py/                   ← Python 包
            │    ├─ render/                       ← 渲染核心（27 模块 + extensions/ 12 扩展 + assets/ 主题 CSS）
            │    ├─ server/                       ← FastAPI 服务层（44 模块，含 routers/ 9 模块 + migrations/ 8）
            │    ├─ uploaders/                    ← 图床上传器（13 模块，覆盖 14 家）
            │    ├─ mcp_server/                   ← stdio MCP Server（6 模块）
            │    ├─ assets/web-dist/              ← 前端构建产物落点（.gitkeep / MANIFEST.sha256 / NOTICE 入库，其余不入库）
            │    ├─ cli.py                        ← `mdpy` CLI 入口
            │    └─ user_config.py                ← 用户级配置文件读取
            ├─ scripts/                           ← 构建与证据重生成脚本（build-web-dist / check_coverage / bench_render / 各 *_regen / gen-*-data）
            ├─ tests/                             ← pytest 测试集（render/ server/ mcp/ uploaders/ golden/ + CLI / E2E / AST 守护）
            └─ pyproject.toml                     ← 构建后端、依赖白名单、ruff、覆盖率双门禁配置
```

**嵌套优先原则**：进入 `src/`、`tests/`、`scripts/` 后仍以本文件为最近入口；未覆盖规则按 本应用 → apps → SpecWeave 根 逐级回退（apps/ 根级无分组层 AGENTS.md）。

## 上下文路由表（任务类型 → 入口）

| 任务类型 | 必读入口 |
|---------|---------|
| 改渲染管线 / 新增或调整渲染扩展 | `src/doocs_md_py/render/` + [.agents/rules/render-and-theme-contract.md](.agents/rules/render-and-theme-contract.md) §2 §3 §4 + [docs/architecture.md](docs/architecture.md) §二 |
| 改主题 CSS 装配 / `var()`·`calc()` 解析 / 代码块主题 | `render/css.py`、`render/code_themes.py`、`render/assets/*.css` + [.agents/rules/render-and-theme-contract.md](.agents/rules/render-and-theme-contract.md) §5 |
| 改渲染验收口径 / 黄金样例 / DOM 对拍 | `render/domcompare.py`、`tests/golden/`、`scripts/golden_regenerate.py` + [.agents/rules/render-and-theme-contract.md](.agents/rules/render-and-theme-contract.md) §6 |
| 改上游复刻口径 / 登记或裁决行为差异 | [.agents/rules/upstream-reconstruction.md](.agents/rules/upstream-reconstruction.md) §1 §3 §4 + [docs/contract-mapping.md](docs/contract-mapping.md) + [docs/contract-differences.md](docs/contract-differences.md) |
| 新增依赖 / 改构建后端 / 改覆盖率门槛 | [.agents/rules/engineering-redlines.md](.agents/rules/engineering-redlines.md) §2 §3 §5 + `pyproject.toml` + `scripts/check_coverage.py` |
| 新增文件命名 / frontmatter / 派生产物溯源 | [.agents/rules/engineering-redlines.md](.agents/rules/engineering-redlines.md) §4 + [../../AGENTS.md](../../AGENTS.md)（开发规范） |
| 改服务端端点 / 路由装配 / 错误体 | `src/doocs_md_py/server/`（`app.py`、`routers/`）+ [.agents/rules/server-api-and-security.md](.agents/rules/server-api-and-security.md) §1 + [docs/contract-mapping.md](docs/contract-mapping.md) |
| 改 DB / 迁移 / LWW / 游标 / 配额 / 限流 | `server/db.py`、`server/migrations/`、`server/sync_limits.py`、`server/ratelimit.py` + [.agents/rules/server-api-and-security.md](.agents/rules/server-api-and-security.md) §2 |
| 改鉴权 / JWT / OAuth / Origin 白名单 | `server/security.py`、`server/github_oauth.py`、`server/origin.py` + [.agents/rules/server-api-and-security.md](.agents/rules/server-api-and-security.md) §3 |
| 改分享页净化 / CSP / 密码门 | `server/share_sanitize.py`、`server/share_page.py`、`server/share_password.py` + [.agents/rules/server-api-and-security.md](.agents/rules/server-api-and-security.md) §4 |
| 改配置项 / 启动配置体检 / 密钥处理 | `server/config.py`、`server/config_report.py`、`.env.example` + [.agents/rules/server-api-and-security.md](.agents/rules/server-api-and-security.md) §5 |
| 改上传后端（`/upload`）或图床上传器 | `server/upload_*.py` **或** `uploaders/*.py` + [.agents/rules/uploaders-dual-path.md](.agents/rules/uploaders-dual-path.md) §1 §2 §3 |
| 改 CLI 子命令 / 退出码 / 标准输入输出 | `src/doocs_md_py/cli.py` + [.agents/rules/cli-and-mcp-contract.md](.agents/rules/cli-and-mcp-contract.md) §1 §2 |
| 改 MCP 工具 / 入参 schema / 选项字面值 | `src/doocs_md_py/mcp_server/` + [.agents/rules/cli-and-mcp-contract.md](.agents/rules/cli-and-mcp-contract.md) §3 §4 §5 |
| 构建或更新前端 dist | `scripts/build-web-dist.ps1` / `.sh` + [docs/build-web-dist.md](docs/build-web-dist.md)（**产物不入库**） |
| 性能基准 / 覆盖率报告复现 | `scripts/bench_render.py`、`scripts/check_coverage.py` + [docs/coverage-report-t20.md](docs/coverage-report-t20.md) |
| 全局提交与代码规范 | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) |
| Skill 与七概念指令 | [../../.agents/skills/README.md](../../.agents/skills/README.md) / [../../.agents/commands/README.md](../../.agents/commands/README.md) |

## P0 约束速览（违反 = 打回）

| # | 约束 | 权威事实源 |
|---|------|-----------|
| 1 | **上游基线唯一且以磁盘为准**：`doocs/md` v2.1.0 @ `1bdad48d`，参照树 `d:/AI/.chaos/libs/md`；文档与磁盘源码冲突时**以磁盘源码为准** | [upstream-reconstruction.md](.agents/rules/upstream-reconstruction.md) §1 |
| 2 | **上游锚点注释强制**：每个模块在 docstring/注释标注 `# upstream: <上游路径>:<行号>`；关键魔数集中为常量并注释来源行号 | 同上 §2 |
| 3 | **行为差异必须登记**：任何非逐字等价的实现都要在 `docs/contract-differences.md` 登记 `D-`/`CD-` 编号（含裁决与锚点），**禁止静默偏离** | 同上 §4 |
| 4 | **验收口径 = 归一化 DOM 等价**：marked 与 markdown-it-py token 模型有固有差异，**禁止承诺 HTML 字节一致**（NG6） | 同上 §5 |
| 5 | **禁止 `from __future__ import annotations`**：由 AST 守护测试 `tests/test_no_future_annotations.py` 机械拦截；3.14 直接用内置泛型 | [engineering-redlines.md](.agents/rules/engineering-redlines.md) §1 |
| 6 | **依赖克制白名单（8 项）**：运行期仅 fastapi / uvicorn / python-multipart / markdown-it-py / nh3 / PyJWT / httpx / pyyaml，**不含 `mcp`**（stdio JSON-RPC 2.0 传输层本仓手写，见 `CD-21`）；签名一律标准库手写，**禁 boto3 / cryptography**；新增依赖须说明理由 | 同上 §2 |
| 7 | **覆盖率双门禁**：总覆盖率 ≥80%（`pyproject.toml` `fail_under`）+ 关键模块 per-module ≥90%（`scripts/check_coverage.py`，四个前缀 `render/` `server/` `uploaders/` `mcp_server/`） | 同上 §5 |
| 8 | **凭证零内置、密钥不入库不入日志**：不内置任何官方凭证或 AI Key；启动配置体检只报"启用/未启用"，**不回显密钥**；爱发电付费回调默认关闭 | [server-api-and-security.md](.agents/rules/server-api-and-security.md) §5 |
| 9 | **上传双路径不得混用**：`server/upload_*.py`（服务端 `/upload` 接口）与 `uploaders/*.py`（Web 客户端图床清单）是**两套独立实现**，改动前先辨识路径 | [uploaders-dual-path.md](.agents/rules/uploaders-dual-path.md) §1 |
| 10 | **MCP 契约 1:1 且入参显式映射**：13 工具同名、同 schema、同输出形状；`render_markdown` 入参须经**显式 camelCase → snake_case 映射表**（禁止机械转换），并由双向锁定测试守护 | [cli-and-mcp-contract.md](.agents/rules/cli-and-mcp-contract.md) §4 |
| 11 | **前端产物不入库**：`src/doocs_md_py/assets/web-dist/` 仅 `.gitkeep` / `MANIFEST.sha256` / `NOTICE` 入库，dist 由脚本构建（哈希清单随仓库记录） | [build-web-dist.md](docs/build-web-dist.md) |
| 12 | **非目标冻结 NG1–NG6**：不复刻 VS Code / uTools / 浏览器扩展与其浏览器运行时能力（PDF 打印、截图、剪贴板内联、浏览器内直传、用户 JS 沙箱）；不复刻云厂商运维特性与服务端 AI 代理 | [upstream-reconstruction.md](.agents/rules/upstream-reconstruction.md) §6 |

## 变更日志

完整条目见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)。

- 2026-10-16 | chore | AI 资产容器初始化：新增应用级 `AGENTS.md` + `.agents/`（README + CHANGELOG + 6 个 rules 主题文件）；本应用由「遵循根规范」升级为**应用自治**，同步 `apps/AGENTS.md` 路由表、可用资产索引、边界声明与嵌套优先级图
