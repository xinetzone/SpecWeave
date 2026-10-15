---
id: personal-info-butler
title: 个人信息管家 Agent
source: apps/AGENTS.md#应用路由表
---

# 个人信息管家 Agent

> 记录零散想法、资料与待办 → 自动分类、摘要、打标签、建立关联 → 支持检索、问答、重点提取、待办整理与阶段总结。
> **Sphinx 静态站（GitHub Pages）+ Python 3.14 云端 API**，数据存 Supabase，大模型走 OpenAI 兼容协议并支持页面 BYOK。

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
浏览器（Sphinx 静态站 · GitHub Pages）
        │  HTTPS /api/*
        ▼
Python 3.14 + FastAPI（云端常驻 · Docker）
        ├── PostgREST ──► Supabase / PostgreSQL（items / item_links / summaries）
        └── OpenAI 兼容 ──► 大模型（服务端配置 或 页面 BYOK）
```

- **前端**：Sphinx + MyST 构建静态站，`doc/app.md` 就是工作台界面，零框架、零打包；
- **后端**：`src/info_butler/`，FastAPI，无状态，可跑在任何最小规格实例；
- **降级**：没有 Supabase → 内存存储；没有模型 Key → 全部能力退化为启发式/统计直出。
  **应用在任何配置下都能跑通**，只是没那么聪明。

设计推导过程（第一性原理 → 对抗审查 → 洞察定型）见 `doc/guide/design.md`。

## 目录结构

```text
personal-info-butler/
├── doc/                     Sphinx 站点源（前端 + 文档的唯一事实来源）
│   ├── conf.py              Sphinx 配置 + 构建期守卫 + API 基址注入
│   ├── index.md             首页：定位、能力矩阵、架构
│   ├── app.md               工作台界面（产品主界面）
│   ├── guide/               design / quickstart / deploy / api 四篇
│   └── _static/             butler.css · butler.js（零依赖前端行为层）
├── src/info_butler/         Python 3.14 后端
│   ├── config.py            环境变量 → 配置，缺项即降级
│   ├── similarity.py        中英混合相似度（免向量）
│   ├── llm.py               OpenAI 兼容封装 + 请求级 BYOK
│   ├── store.py             Supabase / 内存 双实现（行为等价）
│   ├── prompts.py           全部提示词资产
│   ├── pipeline.py          归类 / 关联 / 检索 / 问答 / 提取 / 待办 / 总结
│   ├── api.py               FastAPI 路由与鉴权
│   └── cli.py               info-butler serve
├── tests/                   pytest（含 AST 红线守护与站点契约）
├── schema.sql               云端数据库 DDL（Supabase / PostgreSQL）
├── Dockerfile               后端镜像（python:3.14-slim，非 root）
├── pyproject.toml           scikit-build-core 纯 Python 包
├── requirements.txt         Sphinx 构建依赖
└── .env.example             环境变量模板
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
info-butler serve                       # http://127.0.0.1:8787

# 前端站点
python -m pip install -r requirements.txt
BUTLER_API_BASE=http://127.0.0.1:8787 \
  python -m sphinx -b html -d _build/doctrees --keep-going -W doc _build/html
python -m http.server -d _build/html 8931   # http://localhost:8931/app.html

# 门禁
python -m pytest tests -q
```

## 配置

复制 `.env.example` 为 `.env` 后填写：

| 变量 | 必填 | 说明 |
|---|:---:|---|
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | 可选 | **成对**配置才上云，否则内存存储 |
| `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` | 可选 | 任何 OpenAI 兼容端点 |
| `APP_TOKEN` | **上线必填** | 设置后 `/api/*` 需 `X-App-Token` |
| `CORS_ORIGINS` | 上线必填 | 收窄到站点域名，勿留 `*` |
| `BUTLER_API_BASE` | 构建期 | 注入静态页，读者免配置直连后端 |

页面 BYOK：工作台「设置」里填 Base URL / API Key / 模型，存本机 localStorage，
随 `X-LLM-*` 请求头发送，**后端不落盘**。

## 发布上线

两条独立链路：

1. **静态站 → GitHub Pages**：推送 `main` 触发 `.github/workflows/personal-info-butler-pages.yml`
   （仓库根），gates（pytest）→ build（`sphinx -W`）→ deploy。首次需在仓库
   Settings → Pages 把 Source 设为 **GitHub Actions**。
2. **后端 → 云端容器**：`docker build -t info-butler-api .` 后推到任意容器平台，
   注入环境变量，健康检查 `GET /api/health`。

完整步骤与上线前检查清单见 `doc/guide/deploy.md`。

## 安全说明

- `SUPABASE_SERVICE_ROLE_KEY` 与 `LLM_API_KEY` 只存在于服务端环境变量，不下发前端；
- 页面 BYOK 凭据只在本机浏览器，随请求头透传，服务端不落盘、不写日志；
- 上线必须设置 `APP_TOKEN` 并收窄 `CORS_ORIGINS`；
- `schema.sql` 末尾给出 `user_id` + RLS 的多用户隔离方案，MVP 默认单用户。

## 参考

- 站点结构与技术选型参考 [projects/daoapps.github.io](../../../projects/daoapps.github.io)（Sphinx + MyST + GitHub Actions 发布）；
- 遵循 [应用开发生命周期规范](../../../.agents/protocols/app-development-workflow.md)，在 `apps/ai-agents/` 下原地演进；
- 设计推导遵循 [七概念方法论](../../../.agents/commands/seven-concepts.md) 流程 5（F→V→I→C）。
