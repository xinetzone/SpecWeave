---
id: quickstart
---

# 快速开始

## 1. 起后端（零配置也能跑）

```bash
cd apps/ai-agents/personal-info-butler

python -m pip install -e .        # 装 info-butler（FastAPI / uvicorn / httpx / pydantic）
info-butler serve                 # 默认 http://127.0.0.1:8787
```

什么都不配时：存储走**进程内存**（重启即失），所有 AI 能力走**启发式**。
打开 <http://127.0.0.1:8787/api/health> 应看到：

```json
{"status":"ok","storage":"memory","llm_ready":false,"auth_required":false}
```

## 2. 起前端站点

```bash
python -m pip install -r requirements.txt

python -m sphinx -b html -d _build/doctrees --keep-going -W doc _build/html
python -m http.server -d _build/html 8931
```

打开 <http://localhost:8931/app.html> 即是工作台。此时前端走同源 `/api/*`，
而 `python -m http.server` 不代理后端，所以状态徽标会显示「无法连接后端」——
在页面「设置」里把 API 基址填成 `http://127.0.0.1:8787` 即可连通。

:::{tip}
不想每次手填，可以在构建时注入：

```bash
BUTLER_API_BASE=http://127.0.0.1:8787 python -m sphinx -b html -d _build/doctrees -W doc _build/html
```
:::

## 3. 接云端存储（Supabase）

1. 在 [Supabase](https://supabase.com) 新建项目；
2. SQL Editor 里执行仓库内的 `schema.sql`；
3. 配置环境变量（参考 `.env.example`）：

```bash
SUPABASE_URL=https://xxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...
```

重启服务后 `/api/health` 的 `storage` 变为 `cloud`。
**两个变量必须成对出现**，只填一个会被判为未配置并继续走内存存储。

## 4. 接大模型

服务端配置或页面 BYOK 二选一。任何 OpenAI 兼容端点都可以：

```bash
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=sk-xxxxxx
LLM_MODEL=deepseek-chat
```

页面 BYOK：工作台右上角「设置」里填 Base URL / API Key / 模型，
凭据存本机 localStorage，随 `X-LLM-*` 请求头发给后端，**后端不落盘**。

## 5. 上鉴权

```bash
APP_TOKEN=你自己定的强口令
```

设置后所有 `/api/*` 请求必须带 `X-App-Token`（或 `Authorization: Bearer`），
否则 401。前端在「设置」里填同一个值即可。**上线前必须设置。**

## 常用命令

| 命令 | 作用 |
|---|---|
| `info-butler serve --reload` | 开发模式热重载 |
| `info-butler serve --host 0.0.0.0 --port 8080` | 容器内对外监听 |
| `python -m pytest tests -q` | 跑全部测试 |
| `python -m sphinx -b html -d _build/doctrees -W doc _build/html` | 构建站点（警告即失败） |
