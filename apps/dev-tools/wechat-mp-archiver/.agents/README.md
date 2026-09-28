---
id: "wechat-mp-archiver-agents-readme"
title: "wechat-mp-archiver AI 资产容器"
source: "../AGENTS.md#嵌套路由关系"
---
# wechat-mp-archiver - .agents 目录

本目录是 `apps/dev-tools/wechat-mp-archiver`（微信公众号全量内容归档工具）的 AI 协作者资产容器。
本应用为 SpecWeave 主仓库内置应用（非 git submodule），**可直接修改**；内容敏感度为**公开开源代码**。

## 目录结构

```
.agents/
├── README.md                          ← 本文件（资产容器索引）
├── CHANGELOG.md                       ← 应用变更日志（原子提交汇总）
└── rules/
    └── archive-pipeline.md            ← 唯一规则主题：归档管线硬约束（§1-§10 + 新增规则纪律）
```

父级已有的资产不在本应用重复：`roles/`、`skills/`、`scripts/`、`workflows/`、`templates/`、
`prompts/`、`protocols/` 均**未在本应用定义**（不存在对应目录），相关需求一律回退父级（见下方回退链）。

**特别说明**：`apps/dev-tools/wechat-mp-archiver/.agents/docs/` **未创建且不得创建**——
遵循 SpecWeave 根 AGENTS 文档边界声明，对外可读文档一律入本应用 `../docs/`（原子文档集）
或根 `docs/`，禁止写入任何报告/复盘/Wiki。

## 唯一规则主题

| 文件 | 覆盖内容 |
|------|---------|
| [rules/archive-pipeline.md](rules/archive-pipeline.md) | ①保守限速不可下调 ②采集服务只绑回环 ③凭证治理 ④幂等与断点续跑 ⑤故障作用域分流与熔断矩阵 ⑥风控判定必须结构感知 ⑦退出码契约 ⑧官方接口边界 ⑨派生产物纪律 ⑩合规条款工程化落地 |

**单一职责原则**：新增规则只能新增文件，不得把上述主题拆散或复制到父级层；新增前先明确
「现有文件为何覆盖不了、新文件标题能否被一句话概括、父级是否已有同名规则」，并同步
[../AGENTS.md](../AGENTS.md) 的「上下文路由表」与「P0 约束速览」。

## 核心资产真源（AI 协作者必读，文档与代码冲突时以代码为准）

| 资产 | 路径 | 说明 |
|------|------|------|
| 配置单一事实源 | [../src/mp_archiver/config.py](../src/mp_archiver/config.py) | pydantic-settings（`MP_ARCHIVER_` 前缀）：限速/退避/熔断阈值/官方配额等全部默认值 |
| 限速与退避 | [../src/mp_archiver/http_client.py](../src/mp_archiver/http_client.py) | 保守限速 + 指数退避 + 熔断计数的唯一实现；新增网络路径必须复用 |
| 状态机 schema | [../src/mp_archiver/db/schema.sql](../src/mp_archiver/db/schema.sql) | articles/media/comments/metrics/sync_state 五表定义 |
| 统一编排 | [../src/mp_archiver/core/pipeline.py](../src/mp_archiver/core/pipeline.py) | `sync`/`run` 编排、故障分类与计数、断点续跑 |
| 正文归档 | [../src/mp_archiver/core/article_archive.py](../src/mp_archiver/core/article_archive.py) | 四件套落盘、失败隔离、半成目录重建；风控结构感知判定 |
| 凭证脱敏日志 | [../src/mp_archiver/logging_utils.py](../src/mp_archiver/logging_utils.py) | 凭证脱敏（§3 的落地实现） |
| 采集服务部署 | [../deploy/docker-compose.yml](../deploy/docker-compose.yml) | 仅绑 `127.0.0.1:5000`（§2 的落地实现） |

## 人类文档 ↔ AI 规则对应关系

| 人类文档章节 | 对应 AI 规则文件 | 同步锚点 |
|------------|----------------|---------|
| [docs/00-overview.md](../docs/00-overview.md)（定位与架构） | [rules/archive-pipeline.md](rules/archive-pipeline.md) §2 §9 | 采集服务回环绑定、正文直连、派生产物不触网 |
| [docs/01-quickstart.md](../docs/01-quickstart.md)（演练与凭证） | 同上 §2 §3 §4 | 扫码授权、凭证只存 `.env`、幂等续跑 |
| [docs/02-commands.md](../docs/02-commands.md)（命令与退出码） | 同上 §4 §7 | `--include-failed` 语义、`--full` 显式才全量、退出码契约 |
| [docs/03-operations.md](../docs/03-operations.md)（限速与故障处置） | 同上 §1 §5 §6 | 限速默认值即推荐值、熔断矩阵、结构感知风控 |
| [docs/05-compliance.md](../docs/05-compliance.md)（合规声明） | 同上 §3 §8 §10 | 凭证安全、官方接口边界、24 小时删除义务 |

## 父级继承（所有未定义一律回退）

| 层级 | 入口路径 | 提供的资产 |
|------|---------|-----------|
| L1 apps 应用区 | [../../../AGENTS.md](../../../AGENTS.md) | 应用区入口、应用路由表、跨应用调用规范 |
| L2 SpecWeave 根 | [../../../../AGENTS.md](../../../../AGENTS.md) | 全局启动协议、沟通语言、提交规范、路径引用、修复闭环 |
| （根规则） | [../../../../.agents/global-core-rules.md](../../../../.agents/global-core-rules.md) | 内容敏感度预检、嵌套路由回退链、按需读取 |
| （根 Skill） | [../../../../.agents/skills/README.md](../../../../.agents/skills/README.md) | ci-check / link-check / atomic-commit / atomization / seven-concepts 等 L1 门面 |
| （根命令） | [../../../../.agents/commands/README.md](../../../../.agents/commands/README.md) | 七概念、复盘、洞察、原子化、对抗性评审 |

## 变更日志

完整条目见 [CHANGELOG.md](CHANGELOG.md)。

- 2026-09-28 | docs | 初始化本应用 AI 资产容器：`.agents/README.md` + `CHANGELOG.md` + 唯一规则主题 `rules/archive-pipeline.md`；README.md 原子化为 `../docs/`（6 篇 + 索引）