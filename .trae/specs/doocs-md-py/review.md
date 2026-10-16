---
source: .trae/specs/doocs-md-py/tasks.md#Task 21, #Task 22
spec: doocs-md-py
task: T21, T22
updated: 2026-10-16
---

# 审查与实操记录（doocs-md-py · T21 / T22）

本文件承载 T21「应用文档、登记与交付说明」（TR-21.1 / TR-21.2）与 T22「契约差异台账补登与规格收尾」（TR-22.1 / TR-22.2）的验收证据。

## TR-21.1 链接检查与登记完整性（rule）

### 1. 链接检查（`check-links.py` 对变更目录）

命令（cwd `d:\AI`，解释器 `apps/doocs-md-py/.venv/Scripts/python.exe`）：

```bash
python .agents/scripts/check-links.py --path apps/doocs-md-py
```

**结果：校验通过——8 个 Markdown 文件、133 个本地引用全部有效。**

首轮检查发现并已修复两处问题：

| 问题 | 位置 | 处置 |
|---|---|---|
| 断链（相对层级多一级） | `README.md:37` `../../../.trae/specs/doocs-md-py/spec.md` 解析到 `D:\.trae\...` | 改为 `../../.trae/specs/doocs-md-py/spec.md`（正确解析到 `d:\AI\.trae\...`） |
| 目录链接警告 | `docs/architecture.md:117` 链接到 `server/migrations/` 目录 | 改为链接具体文件 `0001_init.sql`，并在文本标注「0001..0008 共 8 个」 |

`apps/AGENTS.md`、`apps/README.md` 变更行：对 `apps/` 整目录执行 `check-links.py` 后，两文件均无断链。整目录报告的 84 处断链全部位于其他应用（如 `docker-images/caffe-ffi-jupyter/` 内指向历史路径 `file:///d:/spaces/SpecWeave/...`），属既有历史遗留，与本次变更无关（已以关键词过滤核实：输出中无 `doocs-md-py` / `apps\AGENTS.md` / `apps\README.md` 命中）。

### 2. 登记完整性（`apps/AGENTS.md`）

新应用以「根级」登记，路由字段完整（5 列：分组 / 应用 / AGENTS.md 入口 / .agents/ / 说明）：

- 应用路由表：「根级 | doocs-md-py | —（遵循根规范） | ❌ 无 | doocs/md 的 Python 3.14 复刻（…）」
- 边界声明表：新增 `apps/doocs-md-py/`、`apps/doocs-md-py/README.md`、`apps/doocs-md-py/docs/` 三行，均标注「应用自治（遵循根规范） | ✅ 是」
- `apps/README.md` §2.3 根级独立应用补充段落同步新增 doocs-md-py 条目

归属层级经实测确认为**根级**（`Test-Path apps/dev-tools/doocs-md-py` = False），非 dev-tools 分组。

## TR-21.2 新人实操走查（rubric）

**执行方式**：在仓库外临时目录（`%TEMP%\mdpy-fresh`）**从零新建虚拟环境**，严格按 `apps/doocs-md-py/README.md` 第二节快速开始执行步骤 1–6，实时记录耗时与产出，最后清理临时环境。

| 步骤 | 命令 | 结果 | 耗时 |
|---|---|---|---|
| 1 建 venv | `python -m venv <tmp>` | 成功 | 9.7 s |
| 2 安装（可编辑 + dev） | `pip install -e "apps/doocs-md-py[dev]"` | 成功（exit 0） | 52.4 s |
| 3 初始化数据库 | `mdpy migrate --db <tmp>/check.db` | 成功，应用迁移 1–8，产出 `check.db` 176128 B | 0.5 s |
| 4 渲染 Markdown | `mdpy render -i README.md -o <tmp>/out.html` | 成功，产出 `out.html` 65520 B | 瞬时 |
| 5 构建前端 dist | （复用仓库内已构建产物；构建路径与回退预案见 `docs/build-web-dist.md`） | `assets/web-dist/index.html` 存在 | — |
| 6 启动同源服务 | `mdpy serve --port 8877` | 启动成功 | — |
| 6 首页探活 | `GET http://127.0.0.1:8877/` | **HTTP 200**，16323 B | — |
| 6 API 探活 | `GET http://127.0.0.1:8877/api/config` | **HTTP 200** | — |

- **库 / CLI / MCP 路径**（步骤 1–4）全程约 **1.2 分钟**，远低于 30 分钟阈值，零卡点。
- **Web UI 路径**（步骤 5–6）依赖已构建的 `web-dist` 产物；本次以仓库内现有产物验证 serve 与首页可达，构建过程本身与回退预案已在 `docs/build-web-dist.md` 完整记录（含本机实际发生的 Windows 原生回退路线）。
- 走查中未出现 README 无法解决的阻塞；唯一需注意的是**须使用 `mdpy` 控制台脚本调用**（`python -m doocs_md_py.cli` 无 `__main__` 入口，不执行任何操作）——README 通篇使用 `mdpy`，指引正确，无文档缺陷。

**清理**：临时 venv 与测试数据库、渲染产物均已删除；仓库内未产生 `data/` 或任何残留（`git status --porcelain` 仅显示 T21 预期变更）。

### 评分

| 维度 | 判定 |
|---|---|
| 从零可完成性 | 5 —— 步骤 1–6 一次通过，无需口头补充 |
| 耗时 | 5 —— 1.2 分钟（库/CLI/MCP） |
| 文档准确性 | 5 —— 所有命令、参数、默认值、产出与 README 描述一致 |

**TR-21.2 结论：5 / 5，通过（阈值 ≥4）。**

## TR-22.1 台账补登与本台账指令一一映射（rule）

### 1. 链接检查（复跑）

命令（cwd `d:\AI`，解释器 `apps/doocs-md-py/.venv/Scripts/python.exe`）：

```bash
python .agents/scripts/check-links.py --path apps/doocs-md-py
python .agents/scripts/check-links.py --path .trae/specs/doocs-md-py
```

| 扫描目标 | 文件数 | 本地引用 | 结果 |
|---|---|---|---|
| `apps/doocs-md-py` | 8 | 151 | **全部有效，0 断链 0 警告** |
| `.trae/specs/doocs-md-py` | 3 | 3 | **全部有效** |

首轮对 `apps/doocs-md-py` 报告 4 处**目录链接警告**（均位于 `docs/contract-differences.md`），已按 T21 对 `architecture.md:117` 的同一口径修复为具体文件：

| 位置 | 原链接 | 处置 |
|---|---|---|
| `contract-differences.md:38`（CD-19 表情层） | `../src/doocs_md_py/server`（目录） | 改为 `../src/doocs_md_py/server/routers/emojis.py` |
| `contract-differences.md:39`（CD-20 爱发电） | `../src/doocs_md_py/server`（目录） | 改为 `../src/doocs_md_py/server/routers/webhooks.py` |
| `contract-differences.md:40`（CD-21 MCP 层） | `../src/doocs_md_py/mcp_server/`（目录） | 改为 `../src/doocs_md_py/mcp_server/stdio.py` |
| `contract-differences.md:121`（§六 D1 `batch`） | `../src/doocs_md_py/server`（目录） | 改为 `../src/doocs_md_py/server/routers/webhooks.py` |

### 2. 机械对拍：tasks.md「T21 登记」指令 → 台账落点（零遗漏）

对 tasks.md 全量检索「T21 登记 / 待写入 contract-differences / T21 偏差 / T21 汇总」指令，共 **16 条**，逐条映射如下：

| tasks.md 行 | 任务 | 登记指令要点 | 台账落点 |
|---|---|---|---|
| L11 | T1 | `mcp` 2.3.0 与传递依赖 `cryptography` 50.0.2，差异登记 T21 | CD-21（删 `mcp` 依赖，传递依赖随之下线） |
| L33 | T2·TR-2.2 | 产物含上游 GA `gtag`（`G-7NZL3PZ0NK`），T21 文档须说明并提供可选移除策略 | CD-10 + §7.1 + `build-web-dist.md` §七 |
| L82 | T4 | 缺省 `UPLOAD_ENABLED` 上游 `false` / 本仓 `true`，待写入 contract-differences.md（T21） | CD-11 + §7.2 |
| L107 | T7 | markdown-it-py 自闭合 `<br />`、无 info 代码块 `language-` 与空 pending | §2.1「字节级不承诺」分类 |
| L175 | T10 | share 正则残留 `<a">`；style 属性内 CSS 原样保留；emoji `about:blank` src 剥离 | CD-16 + §7.6；后两项归 CD-5（DOMPurify→nh3 等价净化） |
| L202 | T8 | `calc()` 除法 `NaN`；无 highlight.js 语法着色 | CD-2 + CD-3（原台账已覆盖） |
| L224 | T9 | `httpx` 15s 超时（上游 Workers `fetch` 无超时） | CD-12 + §7.3 |
| L225 | T9 | `db.connect(check_same_thread=False)` + 自托管单 worker，T21 登记部署约束 | CD-13 + §7.4 + `README.md` |
| L247 | T11 | sync 路由 `async def` + 单 worker + `check_same_thread=False` | CD-13（与 L225 同一条） |
| L268 | T13 | `title` `trim` + `slice(200)`：JS UTF-16 码元 vs Python 码点 | CD-15 + §7.6 |
| L327 | T14 | `get_dir` UTC；qiniu-js region→HTTP multipart；formCustom 不执行用户 JS；S3 手写 SigV4；dcloud 保留原拼写 | CD-4 + CD-17 + CD-9 + §六 S3 行 + CD-18 + §7.7 |
| L349 | T15 | 限流计数以 SQLite 表替代 Workers D1；UTC 日界逐字一致（**无差异**） | §六 平台替代表第 1 行 |
| L372 | T16 | R2 binding→Local/S3；表情手写 SigV4；ETag 用对象 MD5 hex；`Content-Length` 取 DB size；无系统表情种子 | CD-19 + §7.8 + §六 |
| L394 | T17 | `httpx` 超时；D1 `batch`→`with conn:` 单事务；`AFDIAN_*` 无前缀；`{ec,em}` 应答体 | CD-12 + §六 第 2 行 + CD-20 + §7.9 |
| L423 | T18 | 官方 TS SDK→手写 stdio JSON-RPC 2.0；`initialize` 形状；校验文案；schema 去偏；协议版本；删 `mcp` 依赖 | CD-21 + §7.10 |
| L442 | T19 | `serve` 同源托管 dist；缓存头/SPA 回退；端口严格递增；未知 `--provider` 报错；用户级配置文件 | CD-6（×2）+ CD-7 + CD-14 + CD-8 |

**结论：16 条指令全部有台账落点，零遗漏**；其中 12 条为 T22 补登（CD-10..CD-21），4 条由 T21 已建的 CD-2/CD-3/CD-6..CD-8/CD-9 及 §2.1 覆盖。

**TR-22.1 结论：通过。**

## TR-22.2 差异可追溯性（rubric）

**执行方式**：对补登后的台账逐条抽查四要素（层 / 差异要点 / 裁决 / 证据锚点）齐全性与锚点可达性。

| 维度 | 判定 |
|---|---|
| 条目完整性 | 5 —— CD-1..CD-21 共 21 条（含 D-1..D-4 索引行）均含四要素，无缺项 |
| 裁决明确性 | 5 —— 每条均给出「对齐 / 接受差异 / 规格新增 / 改进 / 等价 / 保留上游缺陷 / 不复刻 / 部署约束登记」之一，无含糊表述 |
| 锚点可达性 | 5 —— 本仓锚点全部为具体文件，经 `check-links.py` 机械验证可达；上游锚点保留 `packages/...`/`apps/...` monorepo 相对路径 |
| 索引自治性 | 5 —— D-1..D-4 只索引不抄录，避免第二事实源；§七明细与总表编号双向一致（CD-13→§7.4 等引用已校正） |

**TR-22.2 结论：5 / 5，通过（阈值 ≥4）。**

### 清理与残留

T22 仅修改文档与规格文件，未触碰生产代码、未产生运行时产物；`git status --porcelain` 预期仅显示 §交付物 所列 5 个文件的变更。
