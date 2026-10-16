---
source: "apps/ai-agents/okf-knowledge-qa"
created: "2026-10-15"
---

# OKF 知识库问答 Agent - Implementation Plan

## Task 1: 语料勘察与索引方案定型
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 量化 OKF 知识包真实体量与分布，据此确定检索方案与分片粒度；排除 `examples/`、`references/` 以控制索引体积。
- **Acceptance Criteria Addressed**: AC-9, AC-10
- **Test Requirements**:
  - `rule` TR-1.1: 勘察脚本输出知识包数、清洗后字符数与分位数；实测 19.2M 字符 / p50=615 / max=786,534。
- **Completion Evidence**:
  - 勘察结论已固化进 `spec.md` 的 Background & Context；按分布极斜（单组占 35%）的事实否定了「按知识包分片」方案，改为 SQLite FTS5。
  - 一次性勘察脚本完成任务后已删除，避免与 `build_index.py` 的遍历逻辑重复。
- **Notes**:
  - 本任务原报「2187 单元」未区分真伪，见 Issue I-1——其中 880 个是 examples/references 伪知识包。

## Task 2: 索引构建器
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 实现 `scripts/build_index.py`：清洗 Markdown、按标题切段、打包 ≤900 字符片段，写入 FTS5(trigram) 虚拟表，并在 `meta` 表记录派生产物溯源信息。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-2.1: 全量构建产出 `data/knowledge.db`，体积约 158 MB，知识包数与片段数由构建输出给出。
  - `rule` TR-2.2: `meta` 表含 `source` / `built_at` / `chunk_count` / `tokenizer` 字段。
  - `rule` TR-2.3: 本地与云端读取同一份 `.corpus/bundles`，构建结果必须一致（消除 Issue I-2 的双口径）。
- **Notes**:
  - 修复 Issue I-1 后重建：知识包数由 2187 降至 1307（剔除 880 个 examples/references 伪知识包）。
- **Completion Evidence**:
  - 修复后重建：`知识包/片段数: 1307 / 73188`，`索引体积: 158.4 MB`，`耗时: 50.0s`，语料来源 `.corpus/bundles`。
  - `prepare_corpus.py` 改为直接 `from build_index import ...` 复用同一套筛选逻辑，从根上消除双源偏差。
  - `server.py` 的 description 不再硬编码「2187 束 / 74955 片段」，规模统一以 `/api/health` 的 stats 为准。

## Task 3: 检索层（含查询净化与兜底）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 实现 `src/okfqa/retrieval.py`：FTS5 MATCH 表达式编译、BM25 排序、短查询 LIKE 兜底、中文功能词剥离。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-9
- **Test Requirements**:
  - `rule` TR-3.1: 含 `.` `"` `*` `+` `-` `()` 的 7 条查询编译后不触发 `fts5: syntax error`。
  - `rule` TR-3.2: 长度 < 3 的词元返回 None 并走 LIKE 兜底，「AI」可召回。
  - `rule` TR-3.3: 「道法自然是什么？」能召回原文仅含「道法自然」的片段。
  - `rubric` TR-3.4: 检索相关性；scale 1-5；1=前3条全无关，3=1条同主题，5=前3条全同主题；threshold >= 4。
- **Notes**:
  - 实施中经对抗性审查发现并修复三条失效边界：V1 FTS5 语法注入、V2 短查询无法命中、V6 中文整串短语零召回。
  - 冒烟中又发现 V7：疑问套话「是什么意思」遍布 FAQ 标题，淹没内容词；加入中文功能词剥离后，「道法自然是什么意思」从返回「原子化行动项的原子是什么意思」修正为返回老庄「自然」。
  - BM25 标题权重由 10.0 下调至 3.0——10 倍时标题命中两个泛化三元组即压过正文命中三个专有三元组。
- **Completion Evidence**:
  - `tests/test_retrieval.py` 30 项全部通过（含 4 条 V1/V2/V6/V7 回归用例）。
  - 真实索引冒烟：7 条查询中 4 条前 3 命中全部同主题，2 条部分同主题，1 条（OKF 三层结构）被泛化标题干扰。rubric TR-3.4 评分 **4/5**。
  - Windows 路径隐患已修：SQLite URI 改用 `as_posix()` 并补前导斜杠，否则 `file:D:\...` 被当相对路径。

## Task 4: 服务层与大模型接入
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 实现 `src/okfqa/server.py`（健康检查、问答、静态托管）与 `src/okfqa/llm.py`（OpenAI 兼容协议，httpx 直连，不引入厂商 SDK）。
- **Acceptance Criteria Addressed**: AC-2, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-4.1: 索引缺失时 `/api/ask` 返回 503 且 detail 含 `build_index.py`。
  - `rule` TR-4.2: 未配置凭据时返回 `degraded: true` 与抽取式答案；LLM 抛错时额外携带 `error`。
  - `rule` TR-4.3: 空问题与超长问题（>500）返回 422；`top_k` 越界返回 422。
  - `rule` TR-4.4: `/`、`/static/app.js` 返回 200。
- **Completion Evidence**:
  - `tests/test_api.py` 11 项、`tests/test_llm.py` 17 项全部通过；llm 模块覆盖率 100%。
  - `llm.py` 覆盖超时、传输错误、5 种 HTTP 错误码、4 种畸形响应体，全部抛 `LLMError` 而非静默降级。
  - 线上验证：首页 `status=200 len=2909`；`/api/ask` 返回 `hits=6 degraded=True`。

## Task 5: 前端界面
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 零构建静态页面：提问区、示例问题、加载骨架、答案区（极简 Markdown 渲染）、出处侧栏、引用跳转。
- **Acceptance Criteria Addressed**: AC-2, AC-8
- **Test Requirements**:
  - `rule` TR-5.1: 静态资源经 FastAPI 挂载可访问（`/`、`/static/styles.css`、`/static/app.js` 均 200）。
  - `rubric` TR-5.2: 前端安全性；scale 1-5；1=直接 innerHTML 渲染模型输出，3=有转义但覆盖不全，5=先转义再套 Markdown；threshold >= 4。
- **Completion Evidence**:
  - `test_static_asset_served`、`test_index_page_served` 通过。
  - `app.js` 中 `escapeHtml` 先转义 `& < > " '`，再执行行内语法替换；代码块内容不参与行内渲染。rubric TR-5.2 评分 **5/5**。
  - 支持 Ctrl/⌘+Enter 发送、深色模式、响应式布局（900px 断点）。

## Task 6: 部署上线
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2, Task 4
- **Description**:
  - 配置 `.python-version`、`vercel.json`（buildCommand 云端构建索引、excludeFiles 裁剪运行时包）、`.vercelignore`；复制语料子集后部署到 Vercel 生产环境。
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `rule` TR-6.1: 部署使用 Python 3.14（`.python-version` 生效）。
  - `rule` TR-6.2: 云端 buildCommand 成功构建索引且部署可达。
  - `rule` TR-6.3: 线上 `/api/health` 返回 `db_ready: true`。
- **Notes**:
  - 首次部署失败两轮，均已定位修复：
    1. 上传 209.8 MB 且 7084 文件超限——`.vercelignore` 补 `data/` 排除本地 161MB 索引，改用 `--archive=tgz` 绕开免费版 5000 文件上限。
    2. `APP_ROOT.parents[2]` 在云端 `IndexError`——Vercel 部署根即应用目录，parents 层级不足；改为惰性探测 `default_bundles_root()`，按 2/1/0 层逐级查找子模块并回落 `.corpus`。
- **Completion Evidence**:
  - 云端构建日志：`Using Python 3.14 from .python-version` → `Installing required dependencies from pyproject.toml` → `知识包根目录: /vercel/path0/.corpus/bundles` → `74827 片段 / 161.0 MB / 20.8s` → `Build Completed`。
  - 生产地址 https://okf-knowledge-qa.vercel.app ；线上 `/api/health` `db_ready=true`，`chunk_count=74827`。

## Task 7: 测试与规范守护
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**:
  - 补齐测试套件与仓库规范守护：AST 红线守护、pytest 覆盖率、ruff 编辑器红线。
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `rule` TR-7.1: `tests/test_no_future_annotations.py` 扫描 `src`/`tests`/`scripts` 全部 .py，无 `__future__.annotations` 导入。
  - `rule` TR-7.2: 整体覆盖率 ≥ 80%，关键模块（retrieval/server/llm/config）≥ 90%。
- **Notes**:
  - 开发过程中本人一度在 `analyze_corpus.py` 里写入了被明令禁止的 `from __future__ import annotations`（讲解自犯效应），已被守护测试捕获并立即修正。
- **Completion Evidence**:
  - `pytest -q` → **94 passed, 1 skipped**。
  - 覆盖率：`config 100%`、`llm 100%`、`server 97%`、`retrieval 91%`、`prompts 100%`，**TOTAL 96%**。
  - `pyproject.toml` 构建后端为 scikit-build-core，并配置 ruff `TID251` 禁 `__future__` 规则作为编辑器即时红线。
  - 覆盖率门禁 `--cov-fail-under=80` 写入 `addopts`，实测 `Total coverage: 95.10%`、`92 passed`。

---

# Review R1 修复队列

以下 issue 由独立审查（Review R1）发现，已固化并按优先级修复。

## Issue I-1: examples/references 伪知识包混入索引
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Discovered By**: Review R1 / F1
- **Description**:
  - `iter_bundle_dirs` 把任何含 `index.md` 的目录当作知识包，而 `examples/`、`references/` 子目录自身也带 index.md，导致本应排除的内容被重新纳入。实证路径：`.../free-llm-api-hands-on/examples/index.md`。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-I-1.1: 重建后索引中不存在 `path` 含 `/examples/` 或 `/references/` 的 chunk，且知识包数由 2187 降至 1307。
- **Completion Evidence**:
  - `build_index.py` 新增 `EXCLUDED_DIR_PARTS = {"examples", "references"}` 过滤；重建输出 `1307 / 73188`。

## Issue I-2: 本地与云端构建双口径
- **Status**: `completed`
- **Priority**: high
- **Depends On**: I-1
- **Discovered By**: Review R1 / F2
- **Description**:
  - 本地读子模块（74955 片段）与云端读 `.corpus`（74827 片段）各用一套筛选规则，产出不可复现；`server.py` description 还硬编码了第三个数字。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-I-2.1: `prepare_corpus.py` 与 `build_index.py` 共用同一份筛选函数，本地与云端均从 `.corpus/bundles` 构建。
- **Completion Evidence**:
  - `prepare_corpus.py` 改为 `from build_index import bundle_files, default_bundles_root, iter_bundle_dirs`；`server.py` 移除硬编码规模。

## Issue I-3: 降级文案把故障伪装成配置缺失
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R1 / F3
- **Description**:
  - 大模型调用失败时复用「未配置大模型凭据」文案，掩盖真实故障原因。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-I-3.1: 调用失败时 answer 含「大模型调用失败」且不含「未配置大模型凭据」。
- **Completion Evidence**:
  - `prompts.py` 拆分 `DEGRADED_NOTICE_NO_KEY` / `DEGRADED_NOTICE_LLM_FAILED`；`test_ask_degrades_on_llm_failure` 增加双向断言。

## Issue I-4: 索引损坏被静默吞掉
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R1 / F4
- **Description**:
  - `stats()` 吞 `sqlite3.Error` 返回空字典，导致索引损坏时 `/api/health` 仍报 `db_ready: true`；健康检查同时泄露服务端绝对路径 `db_path`。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-I-4.1: 元信息读取失败时抛 `KnowledgeBaseUnavailable`，健康检查返回 `db_ready: false` 并携带 error。
- **Completion Evidence**:
  - `retrieval.stats` 改为抛异常；`server.health` 拦截后返回 error；响应体移除 `db_path` 字段。

## Issue I-5: 测试与配置卫生
- **Status**: `completed`
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R1 / F5, F6, F7
- **Description**:
  - AC-4 的 `a*bc` 用例因词元 < 3 字符实际被 skip；覆盖率无门禁；`vercel.json` 引用已删除文件；`requirements.txt` 与 `pyproject.toml` 依赖双份维护；`.coverage` 未忽略。
- **Acceptance Criteria Addressed**: AC-4, AC-10
- **Test Requirements**:
  - `rule` TR-I-5.1: 所有含特殊字符的查询都真实执行，不再 skip。
  - `rule` TR-I-5.2: `pytest` 默认带覆盖率门禁，低于 80% 直接失败。
- **Completion Evidence**:
  - 查询改为 `abc*def`；`addopts` 增加 `--cov=okfqa --cov-fail-under=80`；删除 `requirements.txt`；清理 `vercel.json` excludeFiles 与 `.vercelignore`；`.gitignore` 增加 `.coverage`。
