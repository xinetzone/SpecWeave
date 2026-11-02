---
id: support-agent
source: apps/ai-agents/support-agent
---

# 智能客服 Agent（support-agent）

面向电商/ SaaS 场景的智能客服 Web 应用：多轮对话、FAQ 知识库检索、意图自动识别（退款 / 订单查询 / 技术支持）、无法解决自动转人工、对话历史云端持久化、管理后台查看对话记录与满意度统计。

- 语言/运行时：**Python 3.14**（`requires-python = ">=3.14"`），运行时**零第三方依赖**（仅标准库）
- 存储：**Supabase（Postgres）云端**，未配置时自动降级为内存存储
- 大模型：**OpenAI 兼容协议**（DeepSeek / 通义 / 混元 / OpenAI / Moonshot 任意一家），支持服务端配置或前端 BYOK
- 部署：Vercel Serverless（`api/index.py` 导出 ASGI 应用）/ WorkBuddy 应用平台（`scripts/deploy-start.sh`）
- 前端：零构建静态页，视觉语言取自 `projects/daoapps.github.io` 的「新宣纸」设计体系（朱砂 / 黛色 / 纸白）

## 能力矩阵

| 需求 | 实现 |
|---|---|
| 多轮对话 | 服务端会话（`cs_sid` Cookie）+ 历史消息注入大模型上下文（默认 6 轮） |
| FAQ 知识库检索 | 内置 13 条种子知识 + 云端 `cs_faq` 热加载；中文关键词 + 二元字串重合度打分 |
| 意图识别 | 规则快判（命中即返回，零成本）→ 大模型兜底 → 无模型时降级；6 类意图 |
| 自动转人工 | ① 显式「转人工/投诉」② 大模型不可用且知识库未命中 ③ 连续两轮低置信 → 生成 `cs_tickets` 工单 |
| 对话历史持久化 | `cs_sessions` / `cs_messages` / `cs_feedback` / `cs_tickets` / `cs_faq` 五表 |
| 管理后台 | `/admin`：会话总数/消息数/转人工率/平均满意度/解决率 + 意图分布 + 会话明细追溯 + 知识库维护 |
| 云端存储 | Supabase REST（PostgREST），失败自动降级且响应中标记 `degraded` |
| 接入大模型 | `support_agent/llm.py`，Chat Completions 协议，超时 + 指数退避重试 |

## 目录结构

```
support-agent/
├── api/index.py              # Vercel Serverless 入口（导出 ASGI app）
├── schema.sql                # Supabase 表结构（5 张表）
├── vercel.json               # 路由重写到单入口
├── requirements.txt          # 零第三方依赖（仅触发 Python 运行时判定）
├── src/support_agent/
│   ├── config.py             # 环境变量配置 + BYOK 覆盖
│   ├── http_client.py        # 标准库 HTTP（超时/重试）
│   ├── store.py              # Supabase 仓储 + 内存降级 + 统计聚合
│   ├── faq.py                # 知识库与检索打分
│   ├── intent.py             # 意图识别（规则 + 大模型）
│   ├── llm.py                # 大模型接入（OpenAI 兼容）
│   ├── agent.py              # 回合编排（检索→生成→转人工→落库）
│   ├── asgi.py               # 极简 ASGI 应用与路由
│   └── cli.py                # serve / doctor / seed-faq
├── web/                      # 零构建前端（客服端 + 管理后台）
├── scripts/deploy-start.sh   # 部署启动脚本（自解析可用 Python 解释器）
└── tests/                    # pytest 用例（86 项）
```

## 快速开始

```bash
cd apps/ai-agents/support-agent
cp .env.example .env          # 填写 Supabase / LLM / ADMIN_TOKEN
export PYTHONPATH=src
python -m support_agent.cli doctor      # 检查云端与大模型就绪状态
python -m support_agent.cli serve       # http://127.0.0.1:8000  （后台 /admin）
python -m support_agent.cli seed-faq    # 把内置知识库写入云端
```

测试：

```bash
export PYTHONPATH=src && python -m pytest -q
```

## 云端存储初始化

在 Supabase 控制台 → SQL Editor 执行 `schema.sql`，然后把 `SUPABASE_URL`、
`SUPABASE_SERVICE_ROLE_KEY` 配到环境变量。未配置时应用仍可运行（内存存储），
`/api/health` 与后台总览会显示 `degraded`。

## 部署（Vercel）

```bash
vercel deploy --prod
```

部署后在 Vercel 控制台配置环境变量（或在部署前）：

| 变量 | 必填 | 说明 |
|---|:---:|---|
| `SUPABASE_URL` | 推荐 | Supabase 项目 URL |
| `SUPABASE_SERVICE_ROLE_KEY` | 推荐 | service_role key（服务端专用，勿下发前端） |
| `LLM_BASE_URL` | 可选 | 默认 `https://api.deepseek.com/v1` |
| `LLM_API_KEY` | 可选 | 不配置则降级为知识库直答；也可前端 BYOK |
| `LLM_MODEL` | 可选 | 默认 `deepseek-chat` |
| `ADMIN_TOKEN` | **必填** | 未配置时 `/api/admin/*` 返回 503 |

## 部署（WorkBuddy 应用平台）

```bash
# 平台注入 PORT，脚本自行解析可用解释器并绑定 0.0.0.0
sh scripts/deploy-start.sh
```

**为什么需要 `deploy-start.sh`**：部署沙箱用 pyenv 管理 Python，预置版本不含 3.14，
而项目根的 `.python-version` 钉死了 3.14 —— 直接执行 `python3` 会命中
`pyenv: version '3.14' is not installed` 而启动失败。脚本按以下顺序解析解释器：

1. uv 托管的 3.14（部署期由 `installCmd` 执行 `uv python install 3.14` 预装）
2. 平台自带 venv（`$VIRTUAL_ENV` / `/workspace/.venv`）
3. 系统预置解释器（`/usr/bin`、`/usr/local/bin`，显式枚举以绕开 pyenv shim）
4. pyenv / uv 版本目录中任意一个 ≥3.10 的解释器
5. `PYENV_VERSION=system` —— 让 pyenv 忽略 `.python-version` 兜底

应用**零第三方依赖、纯标准库**，已在 Python 3.13 与 3.14 双版本跑通全部 86 项测试，
因此降级到任意 ≥3.10 的解释器都是安全的。

## 前端设计（5 分钟改配色）

视觉语言移植自 `projects/daoapps.github.io` 的「新宣纸」体系：纸白底、朱砂主行动色、黛色引文。
所有颜色集中在 **`web/styles.css` 的 `:root` 变量表**，改配色只改这一处：

| 变量 | 值 | 用途 |
|---|---|---|
| `--paper` / `--paper-deep` | `#f5f1ea` / `#ede6d9` | 页面底色 / 分区底色 |
| `--card` | `#fcfaf5` | 卡片面 |
| `--ink` / `--ink-2` / `--ink-3` | `#3a352e` / `#6e655a` / `#9c9386` | 正文 / 次要 / 弱化文字 |
| `--line` / `--line-strong` | `#e2d9c8` / `#cfc4ae` | 细线 / 强分隔线 |
| `--cinnabar` / `--cinnabar-deep` | `#a8543c` / `#8f442f` | 朱砂：主行动色、印章、强调 |
| `--dai` | `#46534f` | 黛色：引文与次要信息 |
| `--ok` / `--warn` / `--danger` | `#5e7659` / `#8a6d2f` / `#a33127` | 语义状态色（不与朱砂混用） |

改配色后跑 `pytest tests/test_web_contract.py` 即可校验契约（`:root` 之外不得出现硬编码色值）。

**移植边界**：移植「色与质」，不移植「排版密度」。daoapps 是阅读型内容站（大字、疏排版），
客服是高频工具界面，故正文保持 14px/1.7，标题不放大到内容站尺度——`test_web_contract.py`
中的 `test_density_is_not_content_site_scale` 会守住这条边界。

## HTTP 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 客服对话页 |
| GET | `/admin` | 管理后台页 |
| GET | `/api/health` | 云端/大模型就绪状态 |
| POST | `/api/chat` | 一轮对话（body: `message`, 可选 `session_id`、`llm_*` BYOK） |
| GET | `/api/history` | 当前会话历史 |
| POST | `/api/feedback` | 满意度评价（`rating` 1-5） |
| POST | `/api/session` | 新建会话 |
| GET | `/api/admin/overview` | 统计总览（需 `X-Admin-Token`） |
| GET | `/api/admin/sessions` | 会话列表（支持 `q` 筛选） |
| GET | `/api/admin/sessions/<id>` | 会话明细（含满意度） |
| GET/POST | `/api/admin/faq` | 知识库列表 / 新增 |

## 设计取舍（第一性原理摘要）

1. **状态必须外置**：Serverless 无本地磁盘持久性，故所有会话/消息/评价落云端。
2. **知识优先于生成**：先生检 FAQ 再让大模型作答，并从提示词层面禁止编造政策与时效。
3. **成本与延迟优先**：意图规则命中即返回，仅低置信时才调用大模型分类。
4. **永不 500**：云端与大模型任一不可用时降级（知识库直答 → 转人工），响应中显式标记 `degraded`。
5. **最小依赖**：零第三方依赖，避免 Serverless 冷启动与构建期不确定性。

## Gotcha 记录

| # | 现象 | 根因 | 预防 |
|---|---|---|---|
| 1 | 后台会话列表可被恶意 `session_id` 触发存储型 XSS | 客户端可自带 `session_id`（Cookie / query / body），原先原样落库，再经 `innerHTML` 渲染 | 服务端按 `^s_[0-9a-f]{16}$` 白名单校验，不合规一律重新签发；前端渲染再转义一次（纵深防御）。**注意**：不要改成严格格式校验后不回退——历史会话 ID 形态可能不同，校验失败必须重新签发而非报错 |
| 2 | 「人工智能客服能做到什么」被判为转人工，转人工率虚高 | 意图规则按子串匹配，「人工智能」命中了「人工」关键词 | 转人工关键词改为带上下文的前缀匹配，并补 `test_intent.py` 回归用例 |
| 3 | 部署到应用平台时启动失败（`pyenv: version '3.14' is not installed`） | 沙箱 pyenv 无 3.14，而 `.python-version` 钉死版本 | 用 `scripts/deploy-start.sh` 自解析解释器并按序降级；不要用「换 language / 换 startCmd 硬凑」绕过 |
