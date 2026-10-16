---
source: "apps/ai-agents/okf-knowledge-qa"
created: "2026-10-15"
methodology: "七概念 F→V→I→C"
sensitivity: "public"
---

# OKF 知识库问答 Agent - Product Requirements Document

## Overview

- **Summary**: 一个部署在 Vercel 的检索增强问答 Web 应用。用户输入自然语言问题，系统先在 SpecWeave OKF 知识包（1307 束 / 73188 片段）中检索相关段落，再交由大模型归纳作答，答案中每一处结论都标注可跳转的出处引用。
- **Purpose**: 让仓库沉淀的知识包从「静态文档」变成「可问答的资产」，降低知识检索的时间成本。
- **Target Users**: SpecWeave 仓库维护者与贡献者；需要跨 9 个技术域检索知识的研究者。

## Goals

- G1：以知识包内容为唯一事实来源作答，杜绝模型用先验知识编造。
- G2：答案可溯源——每处结论都能回溯到具体知识包片段。
- G3：零数据准备工作，开箱即可对全量知识包发问。
- G4：服务具备真实上线可用性，而非本地 Demo。

## Non-Goals

- NG1：不做用户上传自建知识库（本轮明确只内置 OKF 知识包）。
- NG2：不做向量/语义检索（本轮明确选择免向量关键词检索）。
- NG3：不做多轮对话上下文记忆（单轮问答）。
- NG4：不做用户账号体系与鉴权。
- NG5：不在页面提供 BYOK 密钥输入框（本轮选择服务端环境变量单通道）。

## Background & Context

- **语料实测**（`scripts/` 勘察，覆盖 `AGENTS.md` 中过期的「248 束」表述）：
  - 11,594 个 Markdown 文件、85.9 MB 原始体量；
  - 清洗后 19.2 M 字符，`concepts/` 占 45.3 MB、`references/` 13.5 MB、`examples/` 10.8 MB；
  - 2187 个含 index.md 的目录单元，其中 880 个是 `examples/`、`references/` 子目录被误纳；剔除后真实知识包 **1307 束**，字符数分布极斜：p50 = 615、p90 = 26,823、p99 = 100,527、max = 786,534；
  - 单组 `jishu/ai` 独占 35%，按「知识包」分片不均衡，故弃用按包分片的方案。
- **技术选型结论**：采用 SQLite FTS5 + trigram 分词器替代手写 TF-IDF 倒排索引。理由：SQLite 自维护倒排索引并按页惰性读取，冷启动零加载；语料分布极斜时无分片均衡问题；`sqlite3` 为标准库，不引入第三方检索依赖。实测索引 161 MB、构建 21s、查询毫秒级。
- **拒绝方案**：`okf-kit`（知识包内记载的 CLI，提供 MCP/Chat/HTTP 三模服务）位于 git submodule 内，作为运行时依赖会与部署包耦合，故不复用。
- **运行环境**：Vercel Python 运行时官方支持 3.14（可用版本 3.12 默认 / 3.13 / 3.14），且自动识别 FastAPI。

## Functional Requirements

- **FR-1**：用户在输入框提交问题（1–500 字符），系统返回答案。
- **FR-2**：答案基于检索到的知识包片段生成，句末以 `[编号]` 标注引用，前端可点击跳转到出处卡片。
- **FR-3**：答案下方展示参考出处列表，含标题、知识包路径、原文摘要。
- **FR-4**：未配置大模型凭据时，降级为「原文片段直出 + 出处引用」，服务不启动失败、不返回空答案。
- **FR-5**：大模型调用失败（超时 / 非 2xx / 格式异常）时降级并在响应中如实携带失败原因。
- **FR-6**：检索索引缺失时显式返回 503 并附构建指引，不伪装成「知识库里没有答案」。
- **FR-7**：提供 `/api/health` 自检端点，暴露索引就绪状态、片段数与大模型就绪状态。
- **FR-8**：静态页面由 FastAPI 显式托管（Vercel Python 运行时不自动托管静态文件）。

## Non-Functional Requirements

- **NFR-1**：检索与问答端到端响应在 60s（`maxDuration`）内完成，LLM 超时默认 45s 且必须小于该上限。
- **NFR-2**：单元测试覆盖率 ≥ 80%，检索与服务等关键模块 ≥ 90%。
- **NFR-3**：遵守仓库 Python 红线——禁止 `from __future__ import annotations`，并以 AST 守护测试硬阻断。
- **NFR-4**：构建后端统一使用 scikit-build-core（仓库主权区 Python 子项目规范）。
- **NFR-5**：索引（161 MB）与语料副本（50 MB）均不入版本库。
- **NFR-6**：大模型输出视为不可信输入，前端渲染前必须转义，杜绝 XSS。

## Constraints

- **Technical**：Vercel 免费版单次部署文件数上限 5000（实际 7084 个语料文件，须用 `--archive=tgz` 归档上传）；bundle 体积上限 500 MB（实测 161 MB 索引 + 50 MB 语料，达标）。
- **Dependencies**：`projects/awesome-okf-xs` 为 git submodule，部署时不在应用目录内，须先复制语料子集。
- **Business**：大模型 API Key 由用户提供，不写入代码库。

## Assumptions

- A1：知识包的 `concepts/` 与包索引承载问答所需的主要语义；`examples/`、`references/` 对自然语言问答贡献低，故排除。
- A2：用户使用 OpenAI 兼容端点，`LLM_BASE_URL` 可指向任意兼容服务。
- A3：检索以关键词相关性为准绳即可满足需求，暂不需语义召回。

## Acceptance Criteria

### AC-1: 检索服务可用
- **Type**: `rule`
- **Given**: 已构建索引的部署环境
- **When**: 调用 `GET /api/health`
- **Then**: 返回 `db_ready: true` 且 `stats.chunk_count` > 0
- **Pass Condition**: 线上健康检查 `db_ready` 为 true，片段数与本地构建一致（非硬编码常量）
- **Evidence**: 线上 `/api/health` 响应；本地构建输出

### AC-2: 问答返回带引用的答案
- **Type**: `rule`
- **Given**: 服务就绪
- **When**: `POST /api/ask` 提交「道法自然是什么意思」
- **Then**: 返回 `hit_count` > 0，且 `citations` 每条含 `title`/`bundle`/`snippet`
- **Pass Condition**: hit_count = 6，citations 非空且指向 guoxue/laozi 相关包
- **Evidence**: 线上 `/api/ask` 响应

### AC-3: 中文自然语言问句不漏召回
- **Type**: `rule`
- **Given**: 迷你索引中含「道法自然」文段
- **When**: 查询「道法自然是什么？」（原文不含「是什么」）
- **Then**: 仍能召回该文段
- **Pass Condition**: `tests/test_retrieval.py::test_natural_language_question_still_recalls` 通过
- **Evidence**: pytest 结果

### AC-4: 查询净化不触发 FTS5 语法错误
- **Type**: `rule`
- **Given**: 含 `.`、`"`、`*`、`+`、`-`、`()` 的查询
- **When**: 编译为 MATCH 表达式并交由 FTS5 执行
- **Then**: 不抛 `fts5: syntax error`
- **Pass Condition**: 7 个含特殊字符的查询全部正常执行
- **Evidence**: `test_build_match_expr_never_breaks_fts_syntax` 参数化用例

### AC-5: 短查询可兜底
- **Type**: `rule`
- **Given**: 查询词长度 < 3（trigram 最小单位），如「AI」
- **When**: 执行检索
- **Then**: 经 LIKE 兜底路径返回命中，而非空结果
- **Pass Condition**: 返回命中且内容含查询词
- **Evidence**: `test_short_query_falls_back_to_like`

### AC-6: 索引缺失显式报错
- **Type**: `rule`
- **Given**: 索引文件不存在
- **When**: 调用 `/api/ask`
- **Then**: 返回 HTTP 503 且 detail 含构建指引
- **Pass Condition**: 状态码 503，detail 含 `build_index.py`
- **Evidence**: `test_ask_returns_503_when_index_missing`

### AC-7: 大模型缺失与故障均降级
- **Type**: `rule`
- **Given**: 未配置 `LLM_API_KEY`，或大模型调用抛出 `LLMError`
- **When**: 调用 `/api/ask`
- **Then**: 返回 `degraded: true`、抽取式答案与完整出处；故障时额外携带 `error` 原因
- **Pass Condition**: 两条路径各有用例覆盖并通过
- **Evidence**: `test_ask_degrades_without_llm`、`test_ask_degrades_on_llm_failure`

### AC-8: 静态页面线上可达
- **Type**: `rule`
- **Given**: 部署到 Vercel
- **When**: 访问 `/` 与 `/static/app.js`
- **Then**: 均返回 200
- **Pass Condition**: 首页 HTML 返回 200 且长度正常
- **Evidence**: 线上 `Invoke-WebRequest` 结果

### AC-9: 检索相关性
- **Type**: `rubric`
- **Dimension**: 中文查询的排序合理性——返回的前 3 条是否与查询意图同主题
- **Scale**: 1-5
- **Anchors**:
  - 1 = 前 3 条全部与查询无关（被高频功能词或标题劫持）
  - 3 = 前 3 条中有 1 条同主题
  - 5 = 前 3 条全部同主题且排序与相关度一致
- **Pass Threshold**: >= 4
- **Evidence**: 真实索引上 7 条查询的冒烟输出

### AC-10: 代码规范性
- **Type**: `rubric`
- **Dimension**: 遵守仓库开发规范（Python 红线、构建后端、文档边界、派生产物溯源）
- **Scale**: 1-5
- **Anchors**:
  - 1 = 存在 `from __future__` 导入或 setuptools 后端
  - 3 = 无明显违规但缺守护测试
  - 5 = 全部合规且有 AST 守护测试与 ruff 红线
- **Pass Threshold**: >= 4
- **Evidence**: `test_no_future_annotations.py` 通过；`pyproject.toml` 使用 scikit-build-core

## Open Questions

- [ ] 大模型凭据由用户在 Vercel 控制台配置；当前线上处于降级模式（已验证可用）。
- [ ] 关键词检索对「OKF 知识包的三层结构」这类查询仍会被泛化的「三层结构」标题干扰，是否升级为向量检索待评估。
