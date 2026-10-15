---
id: admin-console
source: apps/admin-console
---

# 通用内容管理后台（admin-console）

一个可直接上线的**通用内容管理骨架**：登录认证 → 数据看板 → 内容列表（搜索/筛选/排序/分页/批量）→ 表单编辑（正文/分类/标签/云端附件）。业务字段后置替换即可复用到具体场景（文章/商品/知识条目）。

- 语言/运行时：**Python 3.14**（`requires-python = ">=3.14"`，本地实测 3.14.3）
- 运行时依赖：**零第三方**（标准库 `urllib` 直连 PostgREST / Storage REST，`hashlib`+`hmac` 自签会话）
- 数据库：**Supabase（Postgres）云端**，未配置时自动降级为内存仓储并标记 `degraded`
- 文件存储：**Supabase Storage**
- 前端：**零构建**原生 HTML/CSS/JS，响应式（桌面侧栏 / 移动抽屉 / 窄屏表格转卡片）
- 部署：Vercel Serverless（`api/index.py` 导出 ASGI 应用）

## 能力矩阵

| 需求 | 实现 |
|---|---|
| 登录认证 | 邮箱 + 口令（PBKDF2-SHA256 20 万轮 + 随机盐）；HS256 签名会话 Cookie（HttpOnly）；CSRF 双提交 + Origin 同源；登录失败限速；登出 |
| 数据看板 | 4 张指标卡（总数/已发布/草稿归档/附件用量）+ 近 14 天新增 SVG 柱状趋势 + 分类分布 + 最近操作日志 |
| 列表管理 | 关键词搜索（标题/摘要/正文/别名）+ 状态/分类/标签筛选 + 4 种排序 + 分页 + 勾选批量改状态/删除 |
| 表单编辑 | 抽屉表单：标题、别名、状态、分类、摘要、正文、多标签、封面与附件云端上传；服务端 schema 校验 + 乐观并发（`expected_updated_at`） |
| 分类/标签 | 独立维护页；删除前引用计数检查（被引用返回 409） |
| 云端持久化 | Supabase 七表 `ac_*`；写操作同步落审计日志 |
| 云端存储 | Supabase Storage 桶 `ac-uploads`；体积/类型白名单；路径服务端生成杜绝穿越 |
| 响应式 | ≥1200 三区 / 900–1200 侧栏收窄 / <900 侧栏抽屉 + 表格转卡片 / <720 单列表单 |
| 降级 | 云端缺失或不可达时切内存仓储，全站可演示，永不 500 |

## 目录结构

```
admin-console/
├── api/index.py              # Vercel Serverless 入口（导出 ASGI app）
├── schema.sql                # Supabase 七表结构 + 索引 + RLS 建议
├── vercel.json               # 路由重写到单入口
├── .env.example              # 环境变量模板（占位符，无真实密钥）
├── requirements.txt          # 运行时零依赖（仅触发 Python 运行时判定）
├── src/admin_console/
│   ├── config.py             # 环境变量配置
│   ├── security.py           # PBKDF2 / HS256 JWT / CSRF / Origin / 登录限速
│   ├── http_client.py        # 标准库 HTTP（超时 + 指数退避重试 + 可注入）
│   ├── store.py              # Supabase 仓储 + 内存降级 + 聚合
│   ├── storage.py            # Supabase Storage 上传/删除/URL + 文件边界
│   ├── validate.py           # 服务端白名单 schema 校验
│   ├── asgi.py               # ASGI 应用与路由（鉴权/CSRF/Origin/降级）
│   └── cli.py                # serve / doctor / seed-admin
├── scripts/smoke.py          # 本地全链路冒烟（不联网）
├── web/                      # 零构建前端（login.html / app.html / styles.css / app.js）
└── tests/                    # pytest 74 项
```

## 快速开始

```bash
cd apps/admin-console
cp .env.example .env          # 填写 3 个必填变量
export PYTHONPATH=src
python -m admin_console.cli doctor       # 检查云端与会话密钥就绪状态
python -m admin_console.cli seed-admin --email you@example.com   # 建管理员（口令交互输入）
python -m admin_console.cli serve        # http://127.0.0.1:8000 （登录页 /login，后台 /app）
```

未配置 Supabase 时也能直接 `serve`：应用进入内存降级模式，可用 `.env` 中的 `ADMIN_EMAIL` / `ADMIN_PASSWORD` 登录（该演示账号仅在本地生效，部署到 Vercel 时自动关闭，fail-closed）。

测试与冒烟：

```bash
export PYTHONPATH=src && python -m pytest -q      # 74 项
python scripts/smoke.py                          # 8 组全链路自检，退出码 0 即通过
```

## 五步上线（Vercel）

1. **建表**：Supabase 控制台 → SQL Editor → 粘贴执行 [`schema.sql`](schema.sql)（七表 + 索引 + RLS）。
2. **建桶**：Storage → New bucket → 名称 `ac-uploads`（与 `SUPABASE_BUCKET` 一致）；公开桶用 public URL，私有桶应用自动改用签名 URL。
3. **建号**：`python -m admin_console.cli seed-admin --email you@example.com`（需先配好环境变量）。
4. **配环境变量**：Vercel 项目 → Settings → Environment Variables（见下表）。
5. **部署**：`vercel deploy --prod`（已提供 `vercel.json`，`/.python-version` 固定 3.14）。

| 变量 | 必填 | 说明 |
|---|:---:|---|
| `SUPABASE_URL` | ✅ | Supabase 项目 URL |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | service_role key（**服务端专用，勿下发浏览器**） |
| `SESSION_SECRET` | ✅ | 会话签名密钥（`openssl rand -hex 32`）；缺失则随机生成，重启后会话失效 |
| `SUPABASE_BUCKET` | 可选 | 默认 `ac-uploads` |
| `SESSION_TTL` | 可选 | 默认 `43200`（12 小时） |
| `MAX_UPLOAD_BYTES` | 可选 | 默认 `5242880`（5MB；注意 Vercel 请求体上限 4.5MB） |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | 可选 | `seed-admin` 默认值；降级模式下的演示账号 |

## HTTP 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/login` `/app` | 登录页 / 后台单页（未登录跳登录） |
| GET | `/api/health` | 云端/会话密钥就绪状态 |
| POST | `/api/auth/login` `logout` | 登录 / 登出 |
| GET | `/api/auth/me` | 当前账号 |
| GET | `/api/meta` | 分类/标签/状态枚举/上传限制 |
| GET | `/api/dashboard` | 看板聚合 |
| GET | `/api/items` | 列表（q/status/category_id/tag/sort/order/page/page_size） |
| POST | `/api/items` | 新建 |
| GET/PATCH/DELETE | `/api/items/:id` | 详情 / 更新（乐观并发）/ 删除 |
| POST | `/api/items/bulk` | 批量改状态或删除 |
| GET/POST | `/api/categories` | 分类列表 / 新建 |
| PATCH/DELETE | `/api/categories/:id` | 重命名 / 删除（被引用 409） |
| GET/POST | `/api/tags`、DELETE `/api/tags/:id` | 标签维护 |
| POST | `/api/uploads` | 上传（裸二进制 + `X-File-Name` 头） |
| GET | `/api/attachments`、DELETE `/api/attachments/:id` | 附件列表 / 删除（连带云端对象） |
| GET | `/api/logs` | 操作日志 |

## 设计取舍（第一性原理摘要）

1. **Serverless 无本地磁盘** → 所有状态落云端 Postgres，文件落云端 Storage；未配置时内存降级而非崩溃。
2. **零第三方依赖** → 避免 Vercel 构建期不确定性与冷启动成本；PostgREST 已提供过滤/分页/计数，无需 ORM。
3. **密钥边界** → `service_role` key 只在服务端请求头；浏览器只拿短时效签名 Cookie 与 CSRF token；响应体不回显任何密钥。
4. **输入边界** → 所有写入过服务端白名单 schema；表名/列名/排序字段白名单映射 + 过滤值 `urlencode`，杜绝 PostgREST 注入；对象路径服务端生成。
5. **永不 500** → 外呼统一超时 8s + 退避重试，失败降级并在响应/看板显式标记 `degraded`。
6. **展示层是数据投影** → 前端不做业务规则，只渲染与提示；规则单一事实源在服务端。

## 安全说明

- 口令：PBKDF2-HMAC-SHA256 200,000 轮 + 每账号 16 字节随机盐，只存哈希；登录失败恒定提示（不区分账号是否存在）。
- 会话：HS256 自签 JWT（含 `exp`/`role`），`hmac.compare_digest` 常量时间校验；Cookie `HttpOnly` + `SameSite=Lax`（HTTPS 下追加 `Secure`）。
- 写操作三重校验：登录 + Origin 同源 + CSRF 双提交；非 `application/json` 一律 415。
- 上传：体积上限 + 类型白名单 + 文件名净化（去 `..`、控制字符、路径分隔符）。
- 表级 RLS 已启用（service_role 绕过，anon 被拒），避免误用 anon key 暴露数据。
- 角色仅 `admin`/`editor` 两档，账号管理走 CLI（不提供自助注册/找回密码）。

## 规格

方法论链路：七概念场景 5（创新突破）**F → V → I → C**；规格见 [`.trae/specs/admin-console/`](../../../.trae/specs/admin-console/spec.md)。

> AI生成
