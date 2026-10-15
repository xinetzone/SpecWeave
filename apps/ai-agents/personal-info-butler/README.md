---
id: personal-info-butler
title: 个人信息管家 Agent
source: apps/AGENTS.md#应用路由表
---

# 个人信息管家 Agent

> 记录零散想法、资料与待办 → 自动分类、摘要、打标签、建立关联 → 支持检索、问答、重点提取、待办整理与阶段总结。
> 数据存云端（Supabase），大模型可插拔（任何 OpenAI 兼容端点），已发布到 Vercel。

**线上地址**：https://personal-info-butler.vercel.app

## 项目定位

解决「记了很多，用的时候找不到」的痛点：

| 痛点 | 本应用的解法 |
|---|---|
| 想法/资料/待办混在一起 | 录入即自动判定类型（想法 / 资料 / 待办），并生成标题、摘要、标签 |
| 记完就忘、彼此孤立 | 录入时自动计算与已有条目的关联度并写入关联关系（可解释的关联理由） |
| 想不起记在哪 | 关键词检索（中文二元组 + 英文词元混合打分）+ 智能问答（带来源引用） |
| 一堆记录看不过来 | 重点信息提取（观点/决策/风险/待确认/实体）+ 待办整理（去重合并 + 优先级） |
| 不知道这段时间干了啥 | 阶段总结：概览 → 主题分布 → 进展 → 风险 → 后续行动建议，并自动存档 |

## 目录结构

```
personal-info-butler/
├── index.html             # 单页前端入口
├── styles.css             # 设计系统（亮/暗双主题、响应式）
├── app.js                 # 前端逻辑（零构建，原生 ES Module）
├── api/                   # Serverless API（Vercel 直接托管）
│   ├── _lib/
│   │   ├── config.js      # 环境变量 + 请求级 BYOK 覆盖
│   │   ├── http.js        # CORS / 鉴权 / 统一异常（双运行时兼容）
│   │   ├── store.js       # Supabase PostgREST 驱动 + 内存回退
│   │   ├── llm.js         # OpenAI 兼容 /chat/completions 封装
│   │   ├── prompts.js     # 全部 system prompt 资产
│   │   ├── similarity.js  # 中英混合相似度（免向量）
│   │   └── pipeline.js    # 录入归类 → 派生待办 → 关联分析
│   ├── items.js           # GET 列表/检索 · POST 录入
│   ├── item.js            # GET/PATCH/DELETE 单条目
│   ├── ask.js             # 智能问答（带引用）
│   ├── extract.js         # 重点信息提取
│   ├── todos.js           # 待办整理
│   ├── summary.js         # 阶段总结 + 历史存档
│   ├── tags.js            # 标签云与概览统计
│   └── health.js          # 健康检查
├── scripts/dev-server.mjs # 零依赖本地开发服务器（复用 api/ 处理函数）
├── schema.sql             # 云端数据库 DDL（Supabase / PostgreSQL）
├── vercel.json            # 部署配置
└── .env.example           # 环境变量模板
```

## 功能矩阵

| 能力 | 入口 | 是否依赖大模型 |
|---|---|---|
| 随手录入 + 自动分类/摘要/标签 | `POST /api/items` | 可选（无 Key 时启发式降级） |
| 自动关联已有内容 | `POST /api/items` | 可选（无 Key 时相似度降级） |
| 关键词检索 | `GET /api/items?q=` | 否 |
| 智能问答（带引用） | `POST /api/ask` | 是 |
| 重点信息提取 | `POST /api/extract` | 是 |
| 待办整理（去重/优先级/下一步） | `GET /api/todos` | 可选 |
| 阶段总结 + 后续行动建议 | `POST /api/summary` | 是 |

未配置大模型密钥时，所有接口自动降级为「统计直出 / 相似度检索」，应用仍然可用。

## 快速开始

### 1. 本地运行（内存模式，零配置）

```bash
npm run dev      # 等价于 node scripts/dev-server.mjs
# 打开 http://localhost:3000
```

此模式数据存在进程内存中，重启即失，用于体验与开发。

### 2. 接入云端存储（Supabase）

1. 在 [Supabase](https://supabase.com) 创建项目；
2. 打开 SQL Editor，执行本目录下 `schema.sql`；
3. 在项目根目录创建 `.env`（参考 `.env.example`）：

```bash
SUPABASE_URL=https://xxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=sk-xxxxxx
LLM_MODEL=deepseek-chat
APP_TOKEN=自定义一个强口令
```

重启服务，侧栏徽标会显示「存储：云端」。

### 3. 接入大模型

支持任何 OpenAI 兼容端点（DeepSeek / 通义千问 / 腾讯混元 / Moonshot / OpenAI …），两种方式二选一：

- **服务端配置**：`LLM_BASE_URL` + `LLM_API_KEY` + `LLM_MODEL`；
- **页面 BYOK**：打开「设置」，填写 Base URL / API Key / 模型，凭据只存在本机浏览器，随请求头发给本应用后端转发，服务端不落盘。

## 发布上线（Vercel）

```bash
npm i -g vercel
vercel login
vercel --prod                # 首次按提示关联项目
# 随后在 Vercel 控制台 → Settings → Environment Variables 填入 .env 中的变量
vercel deploy --prod         # 重新部署使环境变量生效
```

部署产物：`api/*.js` 自动成为 Serverless 函数，根目录静态文件自动托管。
`.vercelignore` 已排除 `scripts/`、`schema.sql` 与 `.env*`。

## API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 存储模式、大模型就绪状态 |
| GET | `/api/items?q=&kind=&tag=&status=&limit=` | 列表与关键词检索 |
| POST | `/api/items` | 录入（自动分类/摘要/标签/关联/派生待办） |
| GET/PATCH/DELETE | `/api/item?id=` | 单条目读写删 |
| POST | `/api/ask` | 智能问答，返回答案与引用 |
| POST | `/api/extract` | 重点信息提取（Markdown） |
| GET | `/api/todos` | 待办整理（去重、分组、建议） |
| GET/POST | `/api/summary` | 历史总结 / 生成阶段总结 |
| GET | `/api/tags` | 标签云与统计 |

## 安全说明

- `SUPABASE_SERVICE_ROLE_KEY` 只在服务端环境变量中使用，不下发前端；
- 建议设置 `APP_TOKEN`，缺失令牌的请求将被 401 拦截；
- `schema.sql` 末尾给出多用户隔离方案（`user_id` + RLS 策略），MVP 默认单用户。

## 来源

遵循 [应用开发生命周期规范](../../../.agents/protocols/app-development-workflow.md) 在 `apps/ai-agents/` 下直接新建；技术栈选择依据「零构建、可一键部署」原则。
