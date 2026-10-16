---
id: "doocs-md-py-agents-readme"
title: "doocs-md-py AI 资产容器"
source: "../AGENTS.md#嵌套路由关系"
---
# doocs-md-py - .agents 目录

本目录是 `apps/doocs-md-py`（doocs/md 的 Python 3.14 复刻）的 AI 协作者资产容器。
本应用为 SpecWeave 主仓库**根级内置应用**（非 git submodule），**可直接修改**；内容敏感度为**公开开源代码复刻**。

## 目录结构

```
.agents/
├── README.md                              ← 本文件（资产容器索引 + 核心资产真源 + 父级回退链）
├── CHANGELOG.md                           ← 应用变更日志（原子提交汇总）
└── rules/                                 ← 6 个单一职责规则主题
    ├── upstream-reconstruction.md         ← 上游复刻与契约审计纪律（§1-§7）
    ├── engineering-redlines.md            ← 工程红线、依赖白名单与质量门禁（§1-§7）
    ├── render-and-theme-contract.md       ← 渲染管线与主题装配契约（§1-§8）
    ├── server-api-and-security.md         ← 服务端契约、安全与配置治理（§1-§8）
    ├── uploaders-dual-path.md             ← 图床双路径辨识与签名纪律（§1-§7）
    └── cli-and-mcp-contract.md            ← CLI 退出码与 MCP 入参映射契约（§1-§7）
```

父级已有的资产不在本应用重复：`roles/`、`skills/`、`scripts/`、`workflows/`、`templates/`、
`prompts/`、`protocols/`、`checklists/` 均**未在本应用定义**（不存在对应目录），相关需求一律回退父级（见下方回退链）。

**特别说明**：`apps/doocs-md-py/.agents/docs/` **未创建且不得创建**——遵循 SpecWeave 根 AGENTS 文档边界声明
（`.agents/docs/` 为 2026-08-31 整体迁移后废止路径），对外可读文档一律入本应用 `../README.md` 与 `../docs/`
（工程向 5 篇）或根 `docs/`，禁止写入任何报告/复盘/Wiki。

## 6 个规则主题（单一职责，可独立检索）

| 文件 | 覆盖内容 |
|------|---------|
| [rules/upstream-reconstruction.md](rules/upstream-reconstruction.md) | ①上游基线唯一化与磁盘为准 ②锚点注释强制 ③复刻口径三分类（逐字复刻/等价实现/规格新增或裁剪） ④行为差异台账 `D-`/`CD-` 登记与裁决流程 ⑤验收口径与 AC-U2/AC-U3 ⑥非目标 NG1–NG6 冻结与平台差异处置 ⑦反模式 |
| [rules/engineering-redlines.md](rules/engineering-redlines.md) | ①运行时与语法红线（Python ≥3.14、禁 `__future__` annotations + AST 守护） ②依赖白名单与克制 ③scikit-build-core 构建后端三段声明 ④命名与 frontmatter/`source` 溯源 ⑤测试与覆盖率双门禁 ⑥静态检查与平台约束（ruff/PATH 裁剪/跨平台路径/`/mnt/ai` 大体积落点） ⑦反模式 |
| [rules/render-and-theme-contract.md](rules/render-and-theme-contract.md) | ①渲染核心无副作用与三入口共享 ②管线顺序 ③12 扩展清单与注册纪律 ④特色行为不可回退清单 ⑤主题 CSS 装配与 `var()`/`calc()` 解析、代码块主题 CDN 白名单 ⑥验收与黄金样例/DOM 对拍 ⑦性能基线 NFR-6 ⑧反模式 |
| [rules/server-api-and-security.md](rules/server-api-and-security.md) | ①契约 1:1 范围与装配顺序 ②持久化（SQLite 替代 D1 / 8 迁移 / epoch ms / LWW / 游标 / 配额 / 限流） ③鉴权与 Origin 白名单 ④分享（PBKDF2 / 常量时间比较 / cookie path / CSP / 净化） ⑤安全与配置治理（密钥不入库不入日志、配置体检、默认回环、单 worker） ⑥上传后端门控与对象键 ⑦爱发电验签、只信订单号回查与幂等 ⑧反模式 |
| [rules/uploaders-dual-path.md](rules/uploaders-dual-path.md) | ①两套上传路径辨识（极易踩坑） ②Web 图床契约与 `providers.ts` 协议 ③签名算法手写纪律与已知答案测试向量 ④凭证来源层级与零内置 ⑤图床数量口径与差异登记 ⑥`formCustom` 边界（不执行用户 JS） ⑦反模式 |
| [rules/cli-and-mcp-contract.md](rules/cli-and-mcp-contract.md) | ①`mdpy` 五子命令行为 ②退出码与输出契约 ③MCP 13 工具 1:1 ④`render_markdown` 入参显式映射与双向锁定测试 ⑤选项字面值一致性 ⑥数量口径更正纪律（19→20 更正先例） ⑦反模式 |

**单一职责原则**：新增规则只能新增文件，不得把上述主题拆散或复制到父级层；新增前先明确
「现有文件为何覆盖不了、新文件标题能否被一句话概括、父级是否已有同名规则」，并同步
[../AGENTS.md](../AGENTS.md) 的「上下文路由表」与「P0 约束速览」。

## 核心资产真源（AI 协作者必读，文档与代码冲突时以代码为准）

| 资产 | 路径 | 说明 |
|------|------|------|
| 上游基线声明 | [../docs/architecture.md](../docs/architecture.md) | 上游 v2.1.0 @ `1bdad48d` + 模块级上游映射总表（AC-U2 审计依据） |
| 行为差异台账 | [../docs/contract-differences.md](../docs/contract-differences.md) | `D-1..D-4` / `CD-1..CD-21` 的差异主题、裁决与锚点（AC-U3 审计依据） |
| 契约映射表 | [../docs/contract-mapping.md](../docs/contract-mapping.md) | 端点 / 字段 / 常量级对拍表 |
| 构建与依赖配置 | [../pyproject.toml](../pyproject.toml) | 构建后端、依赖白名单、ruff 与覆盖率 `fail_under` 门禁的唯一事实源 |
| 渲染装配入口 | [../src/doocs_md_py/render/renderer.py](../src/doocs_md_py/render/renderer.py) | 管线顺序与选项装配的唯一实现 |
| 渲染选项定义 | [../src/doocs_md_py/render/options.py](../src/doocs_md_py/render/options.py) | 全部渲染选项默认值（与 MCP 原版字面值一致） |
| DOM 对拍工具 | [../src/doocs_md_py/render/domcompare.py](../src/doocs_md_py/render/domcompare.py) | 归一化 DOM 等价验收的实现（替代字节比对） |
| 服务装配 | [../src/doocs_md_py/server/app.py](../src/doocs_md_py/server/app.py) | FastAPI 应用工厂与路由装配顺序 |
| 配置单一事实源 | [../src/doocs_md_py/server/config.py](../src/doocs_md_py/server/config.py) | 全部环境变量与默认值（`.env.example` 与之对齐） |
| 配置体检 | [../src/doocs_md_py/server/config_report.py](../src/doocs_md_py/server/config_report.py) | 启动体检报告（**密钥不回显**的唯一实现，FR-15） |
| 持久化层 | [../src/doocs_md_py/server/db.py](../src/doocs_md_py/server/db.py) | LWW upsert、游标 pull、配额与限流计数事务 |
| 迁移脚本 | [../src/doocs_md_py/server/migrations/](../src/doocs_md_py/server/migrations/0001_init.sql) | 8 个等价 D1 迁移（幂等） |
| 分享净化 | [../src/doocs_md_py/server/share_sanitize.py](../src/doocs_md_py/server/share_sanitize.py) | 分享页 HTML 净化黑名单与固定 CSP 的落地实现 |
| 图床注册表 | [../src/doocs_md_py/uploaders/base.py](../src/doocs_md_py/uploaders/base.py) | provider 注册表与公共基础设施（**图床数量以本文件为准**） |
| 对象存储抽象 | [../src/doocs_md_py/server/storage.py](../src/doocs_md_py/server/storage.py) | local / S3 后端（替代 R2 绑定） |
| MCP 入参映射 | [../src/doocs_md_py/mcp_server/tools.py](../src/doocs_md_py/mcp_server/tools.py) | `render_markdown` camelCase → snake_case 显式映射表 |
| CLI 入口 | [../src/doocs_md_py/cli.py](../src/doocs_md_py/cli.py) | `mdpy` 五个子命令与退出码 |
| 覆盖率门禁 | [../scripts/check_coverage.py](../scripts/check_coverage.py) | 关键模块 per-module ≥90% 的唯一机械门禁与模块口径常量 |
| AST 守护测试 | [../tests/test_no_future_annotations.py](../tests/test_no_future_annotations.py) | 拦截 `from __future__ import annotations` 的技术红线守护 |
| 前端构建脚本 | [../scripts/build-web-dist.ps1](../scripts/build-web-dist.ps1) / [.sh](../scripts/build-web-dist.sh) | 前端 dist 构建与回退路线 |

## 人类文档 ↔ AI 规则对应关系

| 人类文档 / 规格章节 | 对应 AI 规则文件 | 同步锚点 |
|------------------|----------------|---------|
| [../docs/architecture.md](../docs/architecture.md)（架构与上游映射） | [rules/upstream-reconstruction.md](rules/upstream-reconstruction.md) §1 §2 §3 | 上游基线锁定、锚点注释强制、复刻口径三分类 |
| [../docs/contract-differences.md](../docs/contract-differences.md)（差异台账） | 同上 §4 §6 | `D-`/`CD-` 登记流程、非目标冻结 |
| [spec.md](../../../.trae/specs/doocs-md-py/spec.md) NFR-2 / Constraints | [rules/engineering-redlines.md](rules/engineering-redlines.md) §1 §2 §3 §4 | 依赖白名单、`__future__` 禁令、scikit-build-core、命名 |
| spec.md NFR-3 / AC-16 | 同上 §5 | 覆盖率双门禁口径 |
| spec.md G1 / NG6 | [rules/render-and-theme-contract.md](rules/render-and-theme-contract.md) §2 §3 §4 §6 | 管线顺序、12 扩展、特色行为、归一化 DOM 等价 |
| spec.md G2 / FR-3–FR-11 | [rules/server-api-and-security.md](rules/server-api-and-security.md) §2 §3 §4 §7 | SQLite/LWW、鉴权与 Origin、分享净化、爱发电回查 |
| spec.md FR-15 | 同上 §5 | 配置体检与密钥治理 |
| spec.md FR-6 / FR-7 | [rules/uploaders-dual-path.md](rules/uploaders-dual-path.md) §1 §5 §6 | 上传双路径、数量口径、`formCustom` 边界 |
| spec.md FR-1 / FR-12 / G4 | [rules/cli-and-mcp-contract.md](rules/cli-and-mcp-contract.md) §1 §3 §4 §5 | 子命令、13 工具、入参映射、选项字面值 |
| [../docs/build-web-dist.md](../docs/build-web-dist.md) | [rules/engineering-redlines.md](rules/engineering-redlines.md) §6 + [rules/upstream-reconstruction.md](rules/upstream-reconstruction.md) §6 | 产物不入库、平台约束与回退路线 |
| [../docs/coverage-report-t20.md](../docs/coverage-report-t20.md) | [rules/engineering-redlines.md](rules/engineering-redlines.md) §5 + [rules/render-and-theme-contract.md](rules/render-and-theme-contract.md) §7 | 双门禁、性能基准 |

## 父级继承（所有未定义一律回退）

| 层级 | 入口路径 | 提供的资产 |
|------|---------|-----------|
| L1 apps 应用区 | [../../AGENTS.md](../../AGENTS.md) | 应用区入口、应用路由表、跨应用调用规范 |
| L2 SpecWeave 根 | [../../../AGENTS.md](../../../AGENTS.md) | 全局启动协议、沟通语言、提交规范、路径引用、修复闭环 |
| （根规则） | [../../../.agents/global-core-rules.md](../../../.agents/global-core-rules.md) | 内容敏感度预检、嵌套路由回退链、按需读取 |
| （根 Skill） | [../../../.agents/skills/README.md](../../../.agents/skills/README.md) | ci-check / link-check / atomic-commit / atomization / seven-concepts 等 L1 门面 |
| （根命令） | [../../../.agents/commands/README.md](../../../.agents/commands/README.md) | 七概念、复盘、洞察、原子化、对抗性评审 |

## 变更日志

完整条目见 [CHANGELOG.md](CHANGELOG.md)。

- 2026-10-16 | chore | 初始化本应用 AI 资产容器：`.agents/README.md` + `CHANGELOG.md` + 6 个单一职责规则主题（upstream-reconstruction / engineering-redlines / render-and-theme-contract / server-api-and-security / uploaders-dual-path / cli-and-mcp-contract）
