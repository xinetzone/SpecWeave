---
source: "apps/ai-agents/okf-knowledge-qa"
sensitivity: "public"
---

# OKF 知识库问答 Agent

> 部署在 Vercel 的检索增强问答服务：基于 SpecWeave OKF 知识包（1307 束 / 73188 片段），Python 3.14 + FastAPI + SQLite FTS5，按 OpenAI 兼容协议接入大模型。

**线上地址**：https://okf-knowledge-qa.vercel.app

## 特性

- **答案可溯源**：每一处结论都带 `[编号]` 出处标记，前端可点击跳转到原文卡片。
- **零数据准备**：开箱即可对仓库自带的全量知识包发问。
- **大模型可降级**：未配置 Key 或调用失败时，服务降级为原文片段直出 + 完整出处，绝不返回空答案，也绝不把故障伪装成配置缺失。
- **零构建前端**：原生 ES Module + 极简 Markdown 渲染，先转义再套语法，杜绝 XSS。
- **标准库检索**：用 `sqlite3(FTS5 + trigram)` 做中文检索，不引入任何第三方向量库或厂商 SDK。
- **冷启动友好**：Vercel 构建阶段现场构建索引，运行时只读打开，无长时加载。

## 本地开发

```bash
# 准备语料（从 awesome-okf-xs 子模块复制到 .corpus/bundles；默认非破坏、覆盖式复制）
python scripts/prepare_corpus.py

# 构建索引（输出 data/knowledge.db，~158 MB / 50s）
python scripts/build_index.py

# 安装依赖（含测试工具，覆盖率门禁依赖 pytest-cov）
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"

# 启动服务
.venv/Scripts/python.exe -m uvicorn app:app --reload --port 8000
```

打开 http://127.0.0.1:8000，未配置 Key 即可使用降级模式。

## 部署到 Vercel

```bash
vercel deploy --prod --yes --archive=tgz
```

> `--archive=tgz` 不是可选项：语料有 7000+ 个文件，超过免费版单次部署 5000 文件的上限。

仓库已包含 `vercel.json`，部署即按其配置执行：

- **运行时**：Python 3.14（由 `.python-version` 锁定，Vercel 官方支持）
- **构建命令**：`python scripts/build_index.py`（云端现场构建索引，约 21s）
- **静态托管**：`/` 与 `/static/*` 由 FastAPI 显式提供——Vercel 的 Python 运行时**不会**像 Node 运行时那样自动托管根目录静态文件
- **依赖**：`pyproject.toml`（构建后端 scikit-build-core，符合仓库主权区 Python 子项目规范）
- **排除上传**：`data/`、`tests/`、`.venv/`、`.coverage`、`.env` 等

## 配置大模型

通过 Vercel 控制台为项目添加环境变量：

| 变量 | 必填 | 说明 |
|---|---|---|
| `LLM_API_KEY` | 是 | OpenAI 兼容协议的 API Key |
| `LLM_BASE_URL` | 否 | 默认 `https://api.openai.com/v1`；可改为 `https://api.deepseek.com/v1` 等 |
| `LLM_MODEL` | 否 | 默认 `gpt-4o-mini`；按所选服务调整 |
| `LLM_TIMEOUT` | 否 | 默认 45s，须小于 `vercel.json` 的 `maxDuration` (60s) |
| `TOP_K` | 否 | 检索返回片段数，默认 6 |
| `MAX_CONTEXT_CHARS` | 否 | 送入模型的上下文预算，默认 6000 字符 |

未配置 `LLM_API_KEY` 时，页面顶部显示「未配置大模型 · 降级为原文直出」徽标，答案仍是带出处的原文片段。

## 端到端 API

```bash
# 健康检查
curl https://okf-knowledge-qa.vercel.app/api/health

# 提问
curl -X POST https://okf-knowledge-qa.vercel.app/api/ask \
  -H "Content-Type": "application/json" \
  -d '{"question": "道法自然是什么意思"}'
```

`/api/ask` 返回结构：

```json
{
  "answer": "...答案（带 [1][2] 引用）...",
  "citations": [
    {"index": 1, "title": "...", "bundle": "guoxue/laozi/...",
     "group": "...", "domain": "guoxue", "path": "...", "snippet": "...", "score": -12.5}
  ],
  "hit_count": 6,
  "degraded": false,
  "error": null
}
```

索引缺失时返回 **503** 并附构建指引——不伪装成「知识库里没有答案」。

## 测试与覆盖率

```bash
.venv/Scripts/python.exe -m pytest
```

- **92 项全部通过**（含 5 条对抗性审查回归用例）
- **覆盖率 95.10%**（retrieval 91% / server 92% / llm 100% / config 100% / prompts 100%）
- **`--cov-fail-under=80` 写进 `addopts`**——覆盖率跌破 80% 直接红

## 检索设计：三条中文失效边界

中文检索有几个和英文完全不同的坑，本模块逐一加固并留有回归测试：

| 编号 | 边界 | 表现 | 处理 |
|---|---|---|---|
| V1 | FTS5 查询语法注入 | 输入 `3.14` 抛 `fts5: syntax error`，整个检索崩溃 | 抽词后用双引号包裹转义，`OR` 连接 |
| V2 | 短查询永不命中 | trigram 最小单位 3 字符，`AI`、`C++` 无法命中 | 走 `LIKE` 兜底，标题命中优先 |
| V6 | 中文整串零召回 | 中文无词边界，`道法自然是什么` 作短语查询要求原文逐字连续匹配 | 中文串切重叠三元组后 `OR` 连接，由 BM25 排序 |

此外还有两条实测调优点：

- **功能词剥离（V7）**：疑问套话「是什么意思」遍布 FAQ 标题，会把真正的「道法自然」挤出前列。检索前剥离中文功能词与疑问套话。
- **标题权重下调**：BM25 标题权重由 10.0 降至 3.0——10 倍时标题命中两个泛化三元组就能压过正文命中三个专有三元组。

## 架构选型与权衡

| 决策 | 备选 | 选定理由 |
|---|---|---|
| SQLite FTS5 + trigram | 手写 TF-IDF 倒排索引、向量检索 | 19.2M 字符、单束最大 786K、分布极斜（p50=615, max=786,534）→ 按束分片不均衡；FTS5 自维护倒排索引、按页惰性读取、标准库零依赖、冷启动零加载 |
| 云端构建索引 | 上传 161MB 索引产物 | 索引属派生产物不入库；构建仅 21s，且避开免费版文件数与体积上限 |
| 仅 1307 个真知识包 | 2187 个含 index.md 的目录 | 其中 880 个是 `examples/`、`references/` 子目录被误判为独立知识包；二者对自然语言问答语义贡献低 |
| OpenAI 兼容协议 | 厂商 SDK | 一套环境变量适配 OpenAI、DeepSeek、通义、Moonshot；不锁定厂商 |

## 已知局限

- 关键词检索对「OKF 知识包的三层结构」这类查询仍会被泛化标题（如「复利的三层结构」）干扰——这是免向量方案的固有取舍。升级路线：接入 embedding API 做混合检索。
- 知识包内容变化后需重新执行 `prepare_corpus.py` + `build_index.py` + 部署；当前不自动监听重建。
- `.corpus/` 中可能残留历史遗留的无用文件（默认非破坏复制所致），仅影响上传体积，不影响索引；如需彻底清理，显式执行 `python scripts/prepare_corpus.py --prune`。

## 文件清单

```
okf-knowledge-qa/
├── app.py                  # Vercel 入口（sys.path 引导后导出 okfqa.server.app）
├── pyproject.toml          # scikit-build-core + 依赖与测试配置
├── vercel.json             # Vercel 部署配置（buildCommand / excludeFiles）
├── .python-version         # 锁定 Python 3.14
├── .vercelignore / .gitignore / .env.example
├── src/okfqa/
│   ├── config.py           # 环境变量集中读取与安全回退
│   ├── retrieval.py        # FTS5 检索（查询净化、短查询兜底、功能词剥离）
│   ├── llm.py              # OpenAI 兼容协议调用与失败包装
│   ├── prompts.py          # 系统提示与上下文装配（含字符预算）
│   └── server.py           # FastAPI：健康检查 / 问答 / 静态托管
├── static/                 # 零构建前端（index.html / styles.css / app.js）
├── scripts/
│   ├── build_index.py      # 构建 FTS5 索引（筛选逻辑的唯一事实来源）
│   ├── prepare_corpus.py   # 复制语料子集（复用 build_index 的筛选逻辑）
│   └── check_fts5.py       # 环境预检：确认 FTS5 + trigram 可用
└── tests/                  # 92 项测试，含 AST 红线守护
```

## 相关文档

- 需求与验收：[spec.md](../../../.trae/specs/okf-wiki-ecosystem/okf-knowledge-qa/spec.md)
- 实施队列与修复记录：[tasks.md](../../../.trae/specs/okf-wiki-ecosystem/okf-knowledge-qa/tasks.md)
- 独立审查：[review.md](../../../.trae/specs/okf-wiki-ecosystem/okf-knowledge-qa/review.md)
