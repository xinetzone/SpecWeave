---
id: "doocs-md-py-rule-cli-and-mcp-contract"
title: "CLI 退出码与 MCP 入参映射契约"
source: "../../AGENTS.md#P0 约束速览"
---

# CLI 退出码与 MCP 入参映射契约

> **适用范围**：修改 `mdpy` CLI 子命令、退出码、标准输入输出；修改 MCP 工具、入参 schema、选项字面值。
> **权威事实源**：[../../src/doocs_md_py/cli.py](../../src/doocs_md_py/cli.py)、[../../src/doocs_md_py/mcp_server/](../../src/doocs_md_py/mcp_server/tools.py)、[../../src/doocs_md_py/render/options.py](../../src/doocs_md_py/render/options.py)（选项默认值）。

## §1 `mdpy` 五子命令

| 子命令 | 职责 | 关键约束 |
|--------|------|---------|
| `render` | Markdown → HTML 渲染输出 | 复用 `render/` 核心，**不得**内联渲染逻辑 |
| `serve` | 启动 FastAPI 服务 | 参数经 `server/config.py` 装配；默认回环绑定 |
| `upload` | 上传通道（服务端/图床路径由实现决定） | **注意双路径区分**，见 [uploaders-dual-path.md](uploaders-dual-path.md) §1 |
| `mcp` | 启动 stdio MCP Server | 与 `mcp_server/` 同源 |
| `migrate` | 执行数据库迁移 | 复用 `server/migrations/`，幂等 |

- CLI 是**薄封装**：只做参数解析、装配与退出码返回，业务逻辑一律下沉到对应领域模块。**禁止**在 `cli.py` 内实现渲染/服务/迁移逻辑。
- 参数命名与默认值须与 [../../README.md](../../README.md) 的 CLI 表一致；新增子命令须同步 README 与本文 §1。

## §2 退出码与输出契约

- **退出码语义固定**：`0` = 成功；非 `0` = 失败。失败时**必须**在 stderr 输出可读原因，**不得**只返回码而无消息。
- **stdout 只承载结果**（渲染产物、数据），**stderr 只承载诊断**（日志、错误）。**禁止**把诊断信息写入 stdout（会污染管道消费者与 MCP 客户端）。
- `render` 的 stdout 必须是**纯净的渲染结果**，日志一律走 stderr。
- 幂等约束：重复执行同一命令不应产生额外副作用（如重复迁移、重复写库）。
- 相关测试：`tests/test_cli.py`、`tests/test_serve_e2e.py`。

## §3 MCP 13 工具 1:1

- MCP Server（stdio，JSON-RPC 2.0）对外暴露 **13 个工具**，与上游 `packages/mcp-server` **同名、同入参 schema、同输出形状**。
- 工具注册表集中在 [../../src/doocs_md_py/mcp_server/tools.py](../../src/doocs_md_py/mcp_server/tools.py)（上游锚点 `index.ts:150-431`）；schema 定义在 `mcp_server/schema.py`（上游 `index.ts:24-137`）；传输层在 `mcp_server/stdio.py`（上游 `index.ts:139-441`）。
- **禁止**新增/删除工具或改工具名而不登记差异；工具数量与清单变更等同契约变更。
- 选项默认值与上游字面值一致（见 §5）；快照见 `tests/golden/mcp_options_snapshot.json`（由 `scripts/mcp_options_snapshot_regen.py` 再生成）。

## §4 `render_markdown` 入参显式映射

- `render_markdown` 上游入参为 **camelCase**（如 `primaryColor`、`fontSize`），本仓底层 `RenderArticleInput` 为 **snake_case**。
- **必须经显式映射表转换**（位于 `mcp_server/tools.py`），**禁止**依赖机械驼峰→下划线转换。
  - 历史缺陷（已修复，作为永久警戒）：原实现把 camelCase 键名直接传入 snake_case 命名函数，引发 `TypeError` 并被错误兜底掩盖；修复方案是**显式字段映射表**。
- **双向锁定测试**：须有测试同时断言
  1. 每个上游入参都有对应映射项（无遗漏）；
  2. 每个映射项都指向存在的底层字段（无悬空）。
  任一向失败即视为契约破坏。
- **入参数量口径**：上游 `render_markdown` 的 zod 字段实测为 **20 个**。历史上曾误记为"19"，原因是将 zod 字段数与 `get_renderer_options` 的 19 行选项表混算（2026-10-15 按"磁盘为准"更正）。**此类数字一律以磁盘源码为准**，见 §6。

## §5 选项字面值一致性

- 渲染选项默认值以 [../../src/doocs_md_py/render/options.py](../../src/doocs_md_py/render/options.py) 为唯一事实源，必须与上游 MCP `config-options.ts` 字面值一致。已知字面值（**以代码为准**）：

  | 选项 | 默认值 |
  |------|--------|
  | `primaryColor` | `#0F4C81` |
  | `fontSize` | `16px` |
  | `lineHeight` | `1.75` |
  | `linkColor` | `#576b95` |
  | `legend` | `alt`（六值之一，见 [render-and-theme-contract.md](render-and-theme-contract.md) §4） |

- CLI、MCP、HTTP 三入口的选项默认值必须**同源**（都取自 `render/options.py`）；**禁止**为某入口单独设默认值。
- 选项快照漂移由 `tests/mcp/test_mcp_option_snapshots.py` 守护；改动默认值须再生成快照并在 [../../docs/contract-differences.md](../../docs/contract-differences.md) 登记（若构成可观测差异）。

## §6 数量口径更正纪律

- 凡涉及"上游有 N 个 X"的陈述（工具数、入参数、选项数、扩展数、图床数），**必须**：
  1. 以**磁盘源码**逐行实测为准（spec 假设 A1）；
  2. 度量对象**不得混算**（如"zod 字段数"与"选项表行数"是两回事）；
  3. 发现与文档冲突时**同步更正文档全文**（而非只改一处），并在 [../CHANGELOG.md](../CHANGELOG.md) 记录更正条目。
- **更正先例**：`render_markdown` 入参 19→20（2026-10-15），属 C-类事实更正，须留痕。

## §7 反模式（出现即打回）

| # | 反模式 | 后果 |
|---|--------|------|
| A1 | 用机械驼峰转换替代显式映射表 | 字段丢失/`TypeError`，MCP 静默失效 |
| A2 | 无双向锁定测试 | 映射遗漏不可发现 |
| A3 | 诊断/日志写入 stdout | 污染管道与 MCP 客户端 |
| A4 | 三入口各自定义选项默认值 | 行为漂移 |
| A5 | 手改快照 JSON 使测试变绿 | 掩盖漂移 |
| A6 | 陈述"上游有 N 个 X"而未实测磁盘源码，或混算度量对象 | 事实失真（19/20 教训） |
| A7 | 增删 MCP 工具或改工具名而不登记 | 契约破坏 |

## 变更纪律

- 本文档只增不删；子命令集、退出码语义、工具清单、入参映射、选项默认值五者变更须同步 [../../README.md](../../README.md)、快照与 [../CHANGELOG.md](../CHANGELOG.md)，映射类变更必须补双向锁定测试。
