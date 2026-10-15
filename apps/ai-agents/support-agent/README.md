---
id: support-agent
source: apps/ai-agents/support-agent
---

# 智能客服 Agent（support-agent）

面向电商/ SaaS 场景的智能客服 Web 应用：多轮对话、FAQ 知识库检索、意图自动识别（退款 / 订单查询 / 技术支持）、无法解决自动转人工、对话历史云端持久化、管理后台查看对话记录与满意度统计。

- 语言/运行时：**Python 3.14**（`requires-python = ">=3.14"`），运行时**零第三方依赖**（仅标准库）
- 存储：**Supabase（Postgres）云端**，未配置时自动降级为内存存储
- 大模型：**OpenAI 兼容协议**（DeepSeek / 通义 / 混元 / OpenAI / Moonshot 任意一家），支持服务端配置或前端 BYOK
- 部署：Vercel Serverless（`api/index.py` 导出 ASGI 应用）

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
└── tests/                    # pytest 用例（39 项）
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
