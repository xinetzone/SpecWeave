---
id: deploy
---

# 发布上线

## 部署形态：同源单端口

前端站点与 API 由**同一个进程、同一个端口**提供。`/` 进工作台，`/api/*` 是接口。

这不是优化，是**发布的硬前提**——发布平台只暴露一个公网端口。分成两处会带来
三个必然后果：

| 后果 | 机理 |
|---|---|
| 跨域被拦 | 要配 CORS，而平台云服务要求 **Origin 精确匹配**（静态站域名 ≠ API 域名即被拒） |
| 用户要手填地址 | 页面打开却连不上，得手动在「设置」里填 API 基址 |
| 混合内容被拦 | HTTPS 页面请求 HTTP API，浏览器直接拦掉 |

同源部署把三个问题一次消掉。

## 通道一：平台发布（推荐）

```bash
# 平台会自动探测 Python 项目；也可显式指定
#   installCmd: pip install -r requirements.txt && pip install -e .
#   startCmd:   python app.py
```

`app.py` 是发布入口，它做三件事：

1. 把 `src` 挂到 `sys.path`（源码布局下平台未必会 `pip install -e .`）；
2. **确保前端构建产物存在**——平台上传目录时会排除「构建输出」，
   `_build/` 很可能被一并排除，于是线上只剩 API 没有页面。启动前现场构建
   一次即可解决（产物已在则直接复用）；
3. 读 `PORT` / `HOST` 启动 uvicorn（平台只暴露一个公网端口并注入 `PORT`，
   绑死端口号会导致探活失败）。

发布后自检：

```bash
curl -s https://<你的域名>/api/health
# {"status":"ok","storage":"cloud","storage_backend":"workbuddy-cloud",...}
```

## 通道二：容器平台

`Dockerfile` 基于 `python:3.14-slim`，**构建期就把 Sphinx 站点编好**，以非 root
用户运行：

```bash
docker build -t info-butler .
docker run --rm -p 8080:8080 \
  -e WB_CLOUD_ENDPOINT=... \
  -e WB_PUBLISHABLE_KEY=... \
  -e WB_LLM_MODEL=... \
  -e APP_TOKEN=... \
  info-butler
```

任何能跑容器的平台（Fly.io / Render / Railway / Cloud Run / Koyeb）均可。

## 通道三：静态站 + 独立 API（GitHub Pages）

推送 `main` 触发 `.github/workflows/personal-info-butler-pages.yml`（仓库根），
gates（pytest）→ build（`sphinx -W`）→ deploy。

这条通道要求前端与 API **分处两处**，因此：

- 前端构建时要注入 `BUTLER_API_BASE`（后端地址），
- 后端要把 `CORS_ORIGINS` 收窄到 Pages 域名。

## 数据存哪

三种存储实现，优先级如下（任一不满足就降级到下一档）：

| 优先级 | 实现 | 何时启用 | 数据面 |
|---|---|---|---|
| 1 | WorkBuddy 云服务 | `WB_CLOUD_ENDPOINT` + `WB_PUBLISHABLE_KEY` **成对** | `/.cloud/database/rest/<table>`，鉴权头 `x-wb-webapp-access-key` |
| 2 | Supabase / PostgreSQL | `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` **成对** | `/rest/v1/<table>` |
| 3 | 进程内存 | 都不满足 | 进程内，重启即失（仅本地体验） |

**成对才启用**是硬规则：只配一半等于没配，半启用会让「看起来在云上」与
「实际存在内存里」并存，最难排查。

诊断：`GET /api/health` 的 `storage` 与 `storage_backend` 字段会如实报出
当前实际生效的实现（以**真实 store 实例**为准，不读配置）。

## 大模型从哪来

三条通道，优先级：页面 BYOK > 云端免密钥通道 > 服务端 OpenAI 兼容配置。

| 通道 | 触发条件 | 说明 |
|---|---|---|
| BYOK | 页面「设置」里填了 API Key | 凭据只在本机浏览器，随请求头透传，**后端不落盘、不写日志** |
| 云端免密钥 | `WB_CLOUD_ENDPOINT` + `WB_PUBLISHABLE_KEY` + `WB_LLM_MODEL` | 平台托管，用户无需自己的 Key |
| 服务端配置 | `LLM_API_KEY` | 任何 OpenAI 兼容端点 |

都没有时，全部 AI 能力降级为启发式/统计直出——**应用仍完整可用**，
只是没那么聪明。

## 上线前检查清单

- [ ] `APP_TOKEN` 已设置（否则任何人可读写你的库）
- [ ] 云端存储已建表（见 `schema.sql`），列授权与代码里的 `select=*` 对齐
- [ ] 前端产物存在（`app.py` 会自动构建，但确认构建依赖已装）
- [ ] `GET /api/health` 返回 200 且 `storage` 不是 `memory`
- [ ] 本地 `pytest` 与 `sphinx -W` 均通过

:::{warning}
**代理环境**：httpx 默认信任 `HTTP_PROXY` 等环境变量。本机回环地址在应用内
已被显式豁免（`src/info_butler/http_client.py`），但**外部工具**（curl、浏览器
扩展）仍可能把回环请求转发给代理，导致看起来「接口全 404」。排查时先用
`curl --noproxy '*'` 排除这一层。
:::

## 数据模型

`schema.sql` 建三张表：

| 表 | 用途 |
|---|---|
| `items` | 条目主体（想法 / 资料 / 待办），含摘要、标签、状态、优先级、截止日期 |
| `item_links` | 条目间的关联及关联理由（可解释性的落地处） |
| `summaries` | 每次生成的阶段总结存档 |

文件末尾给出 `user_id` + RLS 的多用户隔离方案，MVP 默认单用户。
