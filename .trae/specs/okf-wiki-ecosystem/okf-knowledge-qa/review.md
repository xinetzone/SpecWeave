---
source: "apps/ai-agents/okf-knowledge-qa"
---

# OKF 知识库问答 Agent - Independent Review

## Checkpoints

- [x] CP-R1: 服务已部署且索引就绪
  - **Type**: `rule`
  - **Covers**: AC-1, TR-2.1, TR-2.3, TR-6.1, TR-6.2, TR-6.3
  - **Evidence**: 线上 `GET /api/health` 返回 `db_ready=true`、`bundle_count=1307`、`chunk_count=73060`、`tokenizer=fts5-trigram`；云端构建日志 `Using Python 3.14 from .python-version` → `知识包/片段数: 1307 / 73060`；生产地址 https://okf-knowledge-qa.vercel.app

- [x] CP-R2: 问答返回带引用的答案
  - **Type**: `rule`
  - **Covers**: AC-2, AC-8
  - **Evidence**: 线上 `POST /api/ask` 返回 `hit_count=6`，citations 含 title/bundle/snippet；「容器镜像构建的最佳实践」前 3 条全部命中 `jishu/build/tooling/podman-container-tools`。首页与静态资源返回 200。

- [x] CP-R3: 中文检索三条失效边界均有回归覆盖
  - **Type**: `rule`
  - **Covers**: AC-3, AC-4, AC-5
  - **Evidence**: `test_natural_language_question_still_recalls`（V6）、`test_build_match_expr_never_breaks_fts_syntax` 参数化含 `3.14`/`C++`/`foo.bar`/引号/布尔运算符/括号（V1）、`test_short_query_falls_back_to_like`（V2）全部通过。

- [x] CP-R4: 降级与故障不伪装
  - **Type**: `rule`
  - **Covers**: AC-6, AC-7, TR-I-3.1, TR-I-4.1
  - **Evidence**: `test_ask_returns_503_when_index_missing`（503 + 构建指引）；`test_ask_degrades_without_llm`；`test_ask_degrades_on_llm_failure` 双向断言含「大模型调用失败」且不含「未配置大模型凭据」。

- [x] CP-R5: 对外响应不泄露服务端路径
  - **Type**: `rule`
  - **Covers**: TR-I-4.1（R1-F4 未修部分）
  - **Evidence**: `test_error_responses_leak_no_server_paths` 断言 health 无 `db_path` 键、error 与 503 detail 均不含盘符或 `/vercel`；`test_failure_messages_leak_no_server_paths` 断言异常消息不含 tmp_path。线上 health 响应实测 `db_path` 字段已移除。

- [x] CP-R6: 测试与覆盖率门禁真实生效
  - **Type**: `rule`
  - **Covers**: AC-10, NFR-2, TR-7.1, TR-7.2, TR-I-5.1, TR-I-5.2
  - **Evidence**: `pytest` → **95 passed**，`TOTAL 245 12 95%`，`Required test coverage of 80% reached. Total coverage: 95.10%`；`--cov-fail-under=80` 写入 `addopts`。AST 守护测试扫描 `src`/`tests`/`scripts`，红线扫描仅命中守护测试自身的 docstring。

- [x] CP-U1: 检索相关性
  - **Type**: `rubric`
  - **Covers**: AC-9, TR-3.4
  - **Scale**: 1-5
  - **Anchors**: 1 = 前 3 条全部与查询无关；3 = 前 3 条中 1 条同主题；5 = 前 3 条全部同主题且排序与相关度一致
  - **Pass Threshold**: >= 4
  - **Evidence**: 真实索引 7 条查询冒烟——「道法自然是什么意思」「Python 3.14 新特性」「容器镜像构建最佳实践」「3.14」前 3 条全部同主题（4 条）；「AI」「量子纠缠」部分同主题（2 条）；「OKF 三层结构」被泛化标题干扰（1 条）。评分 **4/5**，达阈值。已知局限已记入 README。

- [x] CP-U2: 仓库规范符合度
  - **Type**: `rubric`
  - **Covers**: AC-10, NFR-3, NFR-4, NFR-5
  - **Scale**: 1-5
  - **Anchors**: 1 = 存在 `from __future__` 导入或使用 setuptools 后端；3 = 无明显违规但缺守护测试；5 = 全部合规且有 AST 守护测试与编辑器红线
  - **Pass Threshold**: >= 4
  - **Evidence**: 红线扫描全仓无真实 `__future__` import（仅守护测试 docstring 命中）；`pyproject.toml` 使用 `scikit_build_core.build` 且声明 `wheel.packages`/`build-dir`/`minimum-version`；ruff `TID251` 禁 `__future__`；161MB 索引与 50MB 语料副本经 `.gitignore`/`.vercelignore` 排除，未入库。评分 **5/5**。

## Review History

### Review R1
- **Result**: `blocked`
- **Evidence**: 审查者执行了静态审计（22 个文件）、全仓 `from __future__` 扫描、6 个测试文件用例清点、部署配置交叉核对。静态清点 92 个用例与实施方声称的 95 存在 3 项差异（后证实为 skip 分支与参数化展开所致）。
- **Blocked By**: 审查者运行环境无命令执行与网络能力，`pytest --cov`、`.coverage` 解析、线上 `.vercel.app` 全部无法自证。
- **Findings**: F1（examples/references 伪知识包混入，P1）、F2（本地/云端双口径，P1）、F3（降级文案伪装故障，P2）、F4（索引损坏被静默 + 路径泄露，P2）、F5（`a*bc` 用例被 skip，P3）、F6（覆盖率无门禁，P3）、F7（配置卫生，P3）。
- **Resume When**: 由具备命令执行与网络能力的一方补齐运行期证据，并对 7 项发现逐条修复。

### Review R2
- **Result**: `fail`
- **Evidence**: 新审查者逐条核验 R1 的 7 项发现，确认 F1/F2/F3/F5/F6/F7 已修复；**F4 只修了一半**——`retrieval.connect()` 的异常消息仍内插绝对 `db_path`，经 `server.health` 的 error 字段与 `ask` 的 503 detail 原样返回客户端。
- **Findings**: N1（`abc*def` 的星号在分词阶段即被丢弃，未真正触达 FTS5，属假保证，P3）、N2（路径泄露残留，P2）、N3（`test_api.py` 未使用的 `tmp_path` 形参，P3）、N4（`prepare_corpus` 重复调用 `iter_bundle_dirs`，P3）、N5（关键模块 ≥90% 无 per-module 门禁，P3）。
- **Routing**: 回 Implement，5 项发现固化为 pending issue 后修复。

### Review R3
- **Result**: `pending`
- **Evidence**: R2 的 N1–N5 已全部修复并重新部署，运行期证据已就地采集：
  - `pytest` → **95 passed**，`TOTAL 245 12 95%`，`Required test coverage of 80% reached. Total coverage: 95.10%`；
  - 线上 `/api/health` → `db_ready=true`、`bundle_count=1307`、`chunk_count=73060`、`db_path` 字段已不存在；
  - 线上 `/api/ask`「容器镜像构建的最佳实践」→ `hit_count=6`，前 3 条全部命中 `jishu/build/tooling/podman-container-tools`。
- **Blocked By**: 尚未由**全新上下文的审查者**执行第三轮独立复核。
  Spec Mode 明确要求「修复清空队列后，用新审查者开启新一轮 Review，
  绝不把实施者自验当最终权威」——上述运行期证据出自实施者，只能作为自验，
  不能充当 R3 的独立证据。
- **Resume When**: 委派新的独立审查者，对照 `review.md` 的 CP-R1..CP-R6 与 CP-U1/CP-U2
  复核上述证据，并确认 N1–N5 的修复未引入回归。通过后即可将结果置为 `pass`。
