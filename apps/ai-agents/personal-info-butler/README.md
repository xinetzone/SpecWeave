---
id: personal-info-butler
title: 个人信息管家 Agent
source: apps/AGENTS.md#应用路由表
---

# 个人信息管家 Agent

> 记录零散想法、资料与待办 → 自动分类、摘要、打标签、建立关联 → 支持检索、问答、重点提取、待办整理与阶段总结。
> **同源单端口**：前端站点与 API 由同一个进程提供。数据存云端（WorkBuddy 云服务 / Supabase / 本地内存三档自动降级），
> 大模型走 OpenAI 兼容协议、云端免密钥通道或页面 BYOK。

## 项目定位

解决「记了很多，用的时候找不到」的痛点：

| 痛点 | 本应用的解法 |
|---|---|
| 想法/资料/待办混在一起 | 录入即自动判定类型，并生成标题、摘要、标签 |
| 记完就忘、彼此孤立 | 自动计算与已有条目的关联度，写入关联关系并给出**可解释**的理由 |
| 想不起记在哪 | 关键词检索（中文二元组 + 英文词元混合打分）+ 智能问答（带引用） |
| 一堆记录看不过来 | 重点信息提取 + 待办整理（去重、分组、优先级） |
| 不知道这段时间干了啥 | 阶段总结：概览 → 主题分布 → 进展 → 风险 → 后续行动建议，并自动存档 |

## 架构

```text
浏览器（工作台 + 文档，同一个域）
        │  同源 /api/*
        ▼
Python 3.14 + FastAPI（单进程 · 单端口）
        ├── 静态资源 ──► Sphinx 构建产物（_build/html）
        ├── PostgREST ──► WorkBuddy 云服务 / Supabase（items / item_links / summaries）
        └── OpenAI 兼容 ──► 大模型（服务端配置 / 云端免密钥 / 页面 BYOK）
```

- **前端**：Sphinx + MyST 构建静态站，`doc/app.md` 就是工作台界面，零框架、零打包；
- **后端**：`src/info_butler/`，FastAPI，无状态，可跑在任何最小规格实例；
- **降级**：没有云端存储 → 内存存储；没有模型 Key → 全部能力退化为启发式/统计直出。
  **应用在任何配置下都能跑通**，只是没那么聪明。

设计推导过程（第一性原理 → 对抗审查 → 洞察定型）见 `doc/guide/design.md`。

## 目录结构

```text
personal-info-butler/
├── app.py                    发布入口（sys.path 适配 + 前端自建 + 读 PORT 启动）
├── doc/                      Sphinx 站点源（前端 + 文档的唯一事实来源）
│   ├── conf.py               Sphinx 配置 + 构建期守卫 + API 基址注入
│   ├── index.md              首页：定位、能力矩阵、架构
│   ├── app.md                工作台界面（产品主界面）
│   ├── guide/                design / quickstart / deploy / api 四篇
│   └── _static/              butler.css · butler.js（零依赖前端行为层）
├── src/info_butler/          Python 3.14 后端
│   ├── config.py             环境变量 → 配置，缺项即降级
│   ├── http_client.py        HTTP 客户端工厂（回环豁免环境代理）
│   ├── similarity.py         中英混合相似度（免向量）
│   ├── llm.py                OpenAI 兼容 + 云端免密钥（流式聚合）双通道
│   ├── store.py              WorkBuddy 云服务 / Supabase / 内存 三实现（行为等价）
│   ├── prompts.py            全部提示词资产
│   ├── pipeline.py           归类 / 关联 / 检索 / 问答 / 提取 / 待办 / 总结
│   ├── api.py                FastAPI 路由与鉴权
│   ├── web.py                同源应用：API + 前端静态资源
│   ├── asgi.py               ASGI 入口（info_butler.asgi:app）
│   └── cli.py                info-butler serve
├── tests/                    pytest（含 AST 红线守护、站点契约、云通道、单端口）
├── schema.sql                云端数据库 DDL
├── Dockerfile                应用镜像（构建期编好前端）
├── pyproject.toml            scikit-build-core 纯 Python 包
├── requirements.txt          Sphinx 构建依赖
└── .env.example              环境变量模板
```

## 功能矩阵

| 能力 | 入口 | 无大模型时 |
|---|---|---|
| 随手录入 + 分类/摘要/标签 | `POST /api/items` | 启发式判定，仍派生待办 |
| 自动关联已有内容 | `POST /api/items` | 相似度 + 标签重合，理由为统计口径 |
| 关键词检索 | `GET /api/items?q=` | 不受影响（本就不走模型） |
| 智能问答（带引用） | `POST /api/ask` | 返回相关度最高的原文片段 |
| 重点信息提取 | `POST /api/extract` | 统计摘要，章节结构一致 |
| 待办整理 | `GET /api/todos` | 按标签分组 + 优先级排序 |
| 阶段总结 | `POST /api/summary` | 统计总结 + 未完成待办转行动建议 |

## 快速开始

```bash
cd apps/ai-agents/personal-info-butler

# 后端（零配置也能跑：内存存储 + 启发式）
python -m pip install -e .
info-butler serve                       # http://127.0.0.1:8787  纯 API

# 同源模式：同一个端口同时提供前端与 API
python -m pip install -r requirements.txt
info-butler serve --static              # http://127.0.0.1:8787/app.html

# 门禁
python -m pytest tests -q
```

## 配置

复制 `.env.example` 为 `.env` 后填写：

| 变量 | 必填 | 说明 |
|---|:---:|---|
| `WB_CLOUD_ENDPOINT` / `WB_PUBLISHABLE_KEY` | 可选 | **成对**配置才上 WorkBuddy 云服务，否则降级 |
| `WB_LLM_MODEL` | 可选 | 云端免密钥大模型使用的模型名 |
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | 可选 | **成对**配置才上 Supabase，否则降级 |
| `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` | 可选 | 任何 OpenAI 兼容端点 |
| `APP_TOKEN` | **上线必填** | 设置后 `/api/*` 需 `X-App-Token` |
| `CORS_ORIGINS` | 分部部署才需要 | 同源部署下前端与 API 同域，无需 CORS |
| `BUTLER_API_BASE` | 分部部署才需要 | 注入静态页，读者免配置直连后端 |
| `BUTLER_STATIC_DIR` | 可选 | 前端构建产物位置，默认 `_build/html` |

存储优先级：WorkBuddy 云服务 > Supabase > 进程内存。诊断看 `GET /api/health`
的 `storage` 与 `storage_backend` 字段（以真实 store 实例为准）。

页面 BYOK：工作台「设置」里填 Base URL / API Key / 模型，存本机 localStorage，
随 `X-LLM-*` 请求头发送，**后端不落盘**。

## 发布上线

三条通道，详见 [doc/guide/deploy.md](doc/guide/deploy.md)：

1. **平台发布（推荐）**：`python app.py` 单端口同源；入口会自建前端产物。
2. **容器平台**：`docker build -t info-butler .`，镜像构建期已编好前端。
3. **静态站 + 独立 API**：GitHub Pages（前端）与容器（后端）分处两处，
   需配 CORS 与 API 基址。

## 安全说明

- `WB_PUBLISHABLE_KEY` / `SUPABASE_SERVICE_ROLE_KEY` / `LLM_API_KEY` 只存在于服务端环境变量，不下发前端；
- 页面 BYOK 凭据只在本机浏览器，随请求头透传，服务端不落盘、不写日志；
- 上线必须设置 `APP_TOKEN`；
- `schema.sql` 末尾给出 `user_id` + RLS 的多用户隔离方案，MVP 默认单用户。

## 参考

- 站点结构与技术选型参考 [projects/daoapps.github.io](../../../projects/daoapps.github.io)（Sphinx + MyST + GitHub Actions 发布）；
- 遵循 [应用开发生命周期规范](../../../.agents/protocols/app-development-workflow.md)，在 `apps/ai-agents/` 下原地演进；
- 设计推导遵循 [七概念方法论](../../../.agents/commands/seven-concepts.md) 流程 5（F→V→I→C）。

