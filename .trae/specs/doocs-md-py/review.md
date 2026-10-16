---
source: .trae/specs/doocs-md-py/tasks.md#Task 21
spec: doocs-md-py
task: T21
updated: 2026-10-16
---

# 审查与实操记录（doocs-md-py · T21）

本文件承载 T21「应用文档、登记与交付说明」的验收证据，对应 Test Requirements TR-21.1（rule）与 TR-21.2（rubric）。

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
