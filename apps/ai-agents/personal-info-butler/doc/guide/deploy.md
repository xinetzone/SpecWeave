---
id: deploy
---

# 发布上线

两条链路**互相独立**：静态站发 GitHub Pages，后端发任意容器平台。
任一侧挂了，另一侧仍能提供部分价值（站点可浏览、接口可直连）。

## 通道一：静态站 → GitHub Pages

推送到 `main` 即触发 `.github/workflows/personal-info-butler-pages.yml`
（位于仓库根 `.github/workflows/`，GitHub 只认仓库根的工作流）：

1. **gates** —— 跑 `pytest`（API 契约与业务逻辑）；
2. **build** —— 安装 `requirements.txt`，`sphinx -W` 构建，上传 Pages 产物；
3. **deploy** —— `actions/deploy-pages` 发布。

首次发布前需在仓库 Settings → Pages 把 Source 设为 **GitHub Actions**。

构建时通过环境变量注入后端地址，读者打开就能连：

```yaml
env:
  BUTLER_API_BASE: https://info-butler-api.example.com
```

:::{warning}
`BUTLER_API_BASE` 写进产品页面 = 写进公开仓库。这是**有意为之**：
个人自托管场景下后端地址不是秘密，秘密是 `APP_TOKEN`，而它永远不进前端代码。
若你的后端需要保密，改为让读者在页面「设置」里自行填写（留空该变量即可）。
:::

## 通道二：后端 → 云端容器

`Dockerfile` 基于 `python:3.14-slim`，以非 root 用户运行：

```bash
docker build -t info-butler-api .
docker run --rm -p 8080:8080 \
  -e SUPABASE_URL=... \
  -e SUPABASE_SERVICE_ROLE_KEY=... \
  -e LLM_BASE_URL=... \
  -e LLM_API_KEY=... \
  -e APP_TOKEN=... \
  -e CORS_ORIGINS=https://<你的 Pages 域名> \
  info-butler-api
```

任何能跑容器的平台（Fly.io / Render / Railway / Cloud Run / Koyeb）均可，
关键是三件事：

| 项 | 要求 |
|---|---|
| 监听 | 容器内 `0.0.0.0:8080`（`Dockerfile` 已设置） |
| 环境变量 | 至少 `APP_TOKEN` 与 `CORS_ORIGINS`；存储与模型按需 |
| 健康检查 | `GET /api/health` 返回 200 |

## 上线前检查清单

- [ ] `APP_TOKEN` 已设置（否则任何人可读写你的库）
- [ ] `CORS_ORIGINS` 收窄到 Pages 域名（不要留 `*`）
- [ ] Supabase 已执行 `schema.sql`，并按需启用 RLS（见该文件末尾）
- [ ] `BUTLER_API_BASE` 指向 HTTPS 地址（Pages 是 HTTPS，混合内容会被浏览器拦）
- [ ] 本地 `pytest` 与 `sphinx -W` 均通过

## 数据模型

`schema.sql` 建三张表：

| 表 | 用途 |
|---|---|
| `items` | 条目主体（想法 / 资料 / 待办），含摘要、标签、状态、优先级、截止日期 |
| `item_links` | 条目间的关联及关联理由（可解释性的落地处） |
| `summaries` | 每次生成的阶段总结存档 |

文件末尾给出 `user_id` + RLS 的多用户隔离方案，MVP 默认单用户。
