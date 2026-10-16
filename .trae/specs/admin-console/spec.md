---
title: "通用内容管理后台 admin-console（Python 3.14）"
status: "completed"
methodology: "seven-concepts (F→V→I→C)"
spec_mode: "Review"
---

# 通用内容管理后台（admin-console）- 产品需求文档

> 方法论链路：七概念场景 5（创新突破）F → V → I → C。本 spec 为 F（第一性原理）与 V（对抗审查）的产出固化。
> 用户关键决策（2026-10-15 确认）：①管理内容 = **通用骨架**（内容条目 + 分类 + 标签 + 附件），业务字段后置替换；②云端 = **Supabase**（Postgres + Storage）；③上线方式 = **代码可部署、凭证由用户填**（我产出 `vercel.json` + `schema.sql` + `.env.example` 并跑通本地冒烟，不接触任何密钥）；④运行时 **Python 3.14**。

## Overview

- **Summary**：一个可部署到 Vercel 的通用内容管理后台：管理员登录认证 → 数据看板 → 内容条目列表（搜索/筛选/分页/批量）→ 表单编辑（富文本正文/分类/标签/附件上传），数据持久化在 Supabase Postgres，文件存放于 Supabase Storage，界面响应式。
- **Purpose**：把「内容条目 + 分类 + 标签 + 附件」这一通用后台骨架一次做对并可直接上线，后续只需替换业务字段即可复用到具体业务（文章/商品/知识条目）。
- **Target Users**：需要内容后台的运营/管理员（单租户，1~N 个后台账号）。

## Goals

- G1：登录认证——邮箱 + 口令（PBKDF2-SHA256 落库，绝不明文）、HS256 签名会话 Cookie（HttpOnly）、CSRF 双提交、登出、登录失败限速。
- G2：数据看板——条目总数/按状态分布/按分类分布/近 14 天新增趋势/存储用量/附件数/最近操作日志。
- G3：列表管理——关键词搜索（标题/摘要/正文/别名）、按状态/分类/标签筛选、排序、分页、批量改状态与批量删除。
- G4：表单编辑——新建/编辑抽屉表单：标题、别名 slug、摘要、正文、状态（草稿/已发布/已归档）、分类、多标签、封面与附件上传（云端 Storage）。
- G5：分类与标签独立维护（列表管理 + 表单编辑能力复用同一套组件范式）。
- G6：云端持久化——Supabase Postgres 七表；文件走 Supabase Storage；未配置时内存降级并在界面显式标记 `degraded`，永不 500。
- G7：响应式——桌面侧栏 / 移动抽屉，表格在窄屏转卡片，≥360px 不破版。
- G8：部署就绪——`vercel.json` + `api/index.py` 单入口 + `schema.sql` + `.env.example`，零构建前端。

## Non-Goals

- 不做多租户、不做自助注册/找回密码/邮箱验证（管理员由 CLI `seed-admin` 预置）。
- 不做细粒度 RBAC（仅 `admin` / `editor` 两档，editor 不可管理账号）。
- 不做前端构建链（无 npm/node_modules，原生 HTML/CSS/JS）。
- 不做实时协同、版本回滚、工作流审批、国际化。
- 不在仓库内置任何真实密钥（`SUPABASE_SERVICE_ROLE_KEY` / `SESSION_SECRET` 全部走环境变量）。

## Background & Context

- **F 阶段公理体系**（不可再分前提）：
  - A1：Serverless 无本地磁盘持久性 → 所有状态（含会话以外的业务数据）必须落云端 Postgres；文件落云端 Storage。
  - A2：Vercel Python Runtime 构建期不确定性与冷启动成本 → 运行时**零第三方依赖**（标准库 `urllib` 直连 PostgREST / Storage REST，`hashlib`+`hmac` 自签 JWT）。
  - A3：密钥边界 → `service_role` key 只存在于服务端进程内，浏览器只拿到短时效签名会话 Cookie 与 CSRF token，任何响应体不得回显密钥。
  - A4：降级优先 → 云端不可达时切内存仓储并显式标记 `degraded`，功能仍可演示，绝不抛未捕获异常。
  - A5：输入边界 → 所有写操作服务端 schema 白名单校验（类型/枚举/长度/体积），未知字段拒绝，中文错误提示。
  - A6：展示层是数据的投影 → 前端不做业务规则，只做渲染与校验提示，规则单一事实源在服务端。
- **F 阶段假设剥离**（被证伪的经验假设）：必须上 FastAPI/uvicorn（Serverless 下 ASGI 裸函数更轻且零依赖）；必须引入 ORM/SQLAlchemy（PostgREST 已提供过滤/分页/计数）；必须前端框架（管理后台交互密度可用原生 JS 覆盖）；必须 Supabase Auth（自建口令哈希更可控且免去 GoTrue 依赖）。
- **V 阶段对抗审查结论**（须在设计中兑现）：

  | 攻击者 | 攻击路径 | 防御设计 |
  |---|---|---|
  | 🔴 安全 | 口令明文/弱哈希被拖库还原 | PBKDF2-SHA256 200k 轮 + 每账号随机 16B salt；登录只回「邮箱或口令不正确」，不区分账号是否存在 |
  | 🔴 安全 | 会话 Cookie 被伪造/篡改 | HS256 签名 JWT（含 `exp`/`role`），`hmac.compare_digest` 常量时间校验；密钥缺失时随机生成并标 `degraded` |
  | 🔴 安全 | 跨站请求伪造（Cookie 自动携带） | 三道：SameSite=Lax + `X-CSRF-Token` 双提交 + Origin 同源校验；非 JSON 内容类型一律拒绝 |
  | 🔴 安全 | `service_role` key 泄露到浏览器 | 仅服务端请求头携带；`/api/health` 与所有响应只回布尔 `cloud_ready`，不回显密钥或 URL |
  | 🟠 注入 | PostgREST 过滤值拼接注入 / 路径穿越 | 过滤值走 `urlencode` + 标识符白名单（表名/列名/排序字段/方向枚举映射），对象路径做文件名净化且拒绝 `..` |
  | 🟠 上传 | 超大文件/伪装类型打爆函数 | 体积上限（默认 5MB）+ 内容类型白名单 + 存储路径服务端生成（日期分片 + 随机名） |
  | 🟢 边界 | 超长标题、空 slug、非法状态、负数分页 | 服务端 fail-fast 校验，长度截断与中文提示 |
  | 🟢 边界 | 删除被引用分类/标签造成孤儿 | 删除前引用计数检查，被引用则拒绝并提示 |
  | 🔵 时序 | 并发改同一条目互相覆盖 | PATCH 携带 `updated_at` 期望值做乐观并发（不匹配返回 409） |
  | 🟣 模糊 | 畸形 JSON / 二进制冒充 JSON body | `json()` 解析失败返回空 dict 并走校验分支，统一 400 而非 500 |
  | 🟣 可用性 | 云端超时把请求拖死 | 每个外呼带超时（默认 8s）+ 指数退避重试 1 次，失败降级 |

- **仓库先例**：`apps/ai-agents/support-agent/`（Supabase REST + 零依赖 ASGI + Vercel `api/index.py` + 内存降级）、`apps/ai-agents/personal-info-butler/`（Supabase + 零构建前端 + Vercel）、`apps/travel-planner/`（CSRF + Origin + 服务端 schema 校验）——本应用复用其云端接入、安全与工程骨架模式。
- **仓库约束**：`apps/*` 新增 Python 子项目默认 **scikit-build-core** 纯 Python 包；Python 红线**禁止 `from __future__ import annotations`** 并须同步 AST 守护测试；Conventional Commits 中文主体；新增应用须登记 `apps/AGENTS.md` 路由表。

## Functional Requirements

- **FR-1（认证）**：`POST /api/auth/login {email,password}` → PBKDF2 校验 → 设置 `ac_session`（HttpOnly, SameSite=Lax, TTL 12h）+ `ac_csrf`（可读）；失败恒定延时（≥200ms）与尝试计数限速（同邮箱 10 分钟内 >10 次锁定 10 分钟）；`POST /api/auth/logout` 清除；`GET /api/auth/me` 返回当前账号与角色；未登录访问 `/app` 跳 `/login`，未登录访问 `/api/*`（除 health/auth）返回 401。
- **FR-2（看板）**：`GET /api/dashboard` 返回：条目总数、按状态计数、按分类计数（Top 8）、近 14 天每日新增、附件总数与总字节、最近 10 条操作日志、`degraded` 标记。界面含 4 张指标卡 + SVG 柱状趋势图 + 分类分布条 + 日志流。
- **FR-3（列表）**：`GET /api/items?q=&status=&category_id=&tag=&sort=&order=&page=&page_size=` → `{items, total, page, page_size}`；搜索覆盖标题/摘要/正文/slug；`sort` 枚举 `created_at|updated_at|title|published_at`，`order` 枚举 `asc|desc`；批量 `POST /api/items/bulk {ids, action: publish|draft|archive|delete}`。
- **FR-4（表单）**：`GET/POST/PATCH/DELETE /api/items[/:id]`；字段：title(必填 ≤200)、slug(可选，空则自动生成)、summary(≤500)、body(≤20000)、status(枚举 draft/published/archived)、category_id、tags(字符串数组)、cover_url；PATCH 需带 `expected_updated_at` 做乐观并发；写入同步维护 `ac_item_tags` 与审计日志。
- **FR-5（分类/标签）**：`GET/POST /api/categories`、`PATCH/DELETE /api/categories/:id`；`GET/POST /api/tags`、`DELETE /api/tags/:id`；删除前引用计数 >0 则 409 拒绝。
- **FR-6（云端文件）**：`POST /api/uploads`（裸二进制 body，`X-File-Name` 头）→ 服务端校验体积/类型 → 转发 Supabase Storage → 返回 `{url,path,size,content_type}`；`GET /api/attachments?item_id=`；`DELETE /api/attachments/:id`（同时删 Storage 对象）；界面支持拖拽上传与进度态、封面预览。
- **FR-7（审计）**：写操作落 `ac_audit_logs`（操作者/动作/目标/摘要/时间）；看板展示最近 10 条。
- **FR-8（响应式）**：CSS Grid 布局；≥1200px 三区（侧栏+主区+详情）；900–1200px 侧栏收窄；<900px 侧栏转抽屉 + 表格转卡片流；<720px 表单单列、批量操作转底部操作条。

## Non-Functional Requirements

- **NFR-1（技术栈）**：Python **3.14**（`requires-python = ">=3.14"`，本地实测 3.14.3）；运行时零第三方依赖；原生 HTML/CSS/JS 零构建；包构建 **scikit-build-core 纯 Python**（`wheel.packages` / `build-dir = "build/{wheel_tag}"` / `minimum-version = "0.9"`，无 cmake 段）；禁止 `__future__` 导入。
- **NFR-2（持久化）**：Supabase Postgres 七表 `ac_admins/ac_items/ac_categories/ac_tags/ac_item_tags/ac_attachments/ac_audit_logs`；文件桶 `ac-uploads`。
- **NFR-3（降级）**：云端未配置或不可达 → 内存仓储，全站可演示，`/api/health` 与看板显示 `degraded: true` 与中文原因；无未捕获 500。
- **NFR-4（测试）**：关键模块（security/store/validate）覆盖率 ≥90%，整体 ≥80%；AST 守护测试断言无 `from __future__` 导入；网络层用假 `urlopen` 注入测试，不依赖真实 Supabase。
- **NFR-5（性能）**：外呼统一超时 8s、重试 1 次；列表默认页大小 20（上限 100）；看板聚合以 PostgREST 计数为主，避免全量拉取。
- **NFR-6（凭证治理）**：密钥仅环境变量；日志/响应/模板一律不回显；`.env.example` 只给占位符；`.gitignore` 覆盖 `.env`。
- **NFR-7（仓库卫生）**：应用代码全在 `apps/admin-console/`；无运行时产物入库；`git status` 零污染。

## Constraints

- **Technical**：Windows 本机开发 + Vercel Serverless 部署；Serverless 请求体上限（4.5MB）决定单文件默认 ≤5MB 需说明。
- **Business**：我不接触任何真实密钥；上线由用户在 Vercel/Supabase 控制台配置环境变量后一键 `vercel deploy --prod`。
- **Dependencies**：无运行时外部硬依赖（Supabase 为可选增强，缺失即降级）。
- **区域**：代码属 `apps/admin-console/`（主仓库直接管理，根级，参照 travel-planner / guard-quality-life-site 先例；新增后登记 `apps/AGENTS.md` 路由表）。

## Assumptions

- 单租户、管理员账号由 CLI `seed-admin` 预置（首次运行引导创建，口令走环境变量或交互输入）。
- Supabase 项目已建、Storage 桶 `ac-uploads` 设为 public（或改用签名 URL，代码已兼容二者）。
- 条目量级 ≤ 数万，PostgREST 计数与分页足够，不需要物化视图。

## Acceptance Criteria

### AC-1：认证与会话安全
- **Type**：`rule`
- **Given**：已预置管理员账号的应用
- **When**：正确口令登录；错误口令；无 Cookie 访问 `/api/items`；携带 Cookie 但无/错 CSRF 发起 POST；篡改 JWT 签名；跨 Origin 发起 POST
- **Then**：正确登录下发 `ac_session`(HttpOnly)+`ac_csrf`；错误口令统一提示且不区分账号存在性；未登录 API 返 401；CSRF 缺失/不匹配 403；篡改签名 401；跨 Origin 403
- **Pass Condition**：六分支断言通过
- **Evidence**：pytest `tests/test_security.py` / `tests/test_asgi.py`

### AC-2：口令存储不可逆
- **Type**：`rule`
- **Given**：创建管理员
- **When**：读取 `ac_admins` 落库行
- **Then**：仅存 `password_hash` + `salt`（PBKDF2-SHA256 ≥200k 轮），明文口令不出现在任何响应、日志或内存快照
- **Pass Condition**：断言落库字段与轮数，全响应体子串扫描无明文
- **Evidence**：pytest

### AC-3：看板聚合正确
- **Type**：`rule`
- **Given**：构造 12 条条目（跨 3 状态 3 分类）+ 3 个附件 + 5 条日志
- **When**：请求 `/api/dashboard`
- **Then**：总数/状态分布/分类分布/近 14 天趋势/附件统计与手算一致；日志按时间倒序取 10
- **Pass Condition**：聚合断言通过
- **Evidence**：pytest `tests/test_store.py`

### AC-4：列表搜索筛选分页
- **Type**：`rule`
- **Given**：30 条条目（含不同状态/分类/标签）
- **When**：分别按关键词、状态、分类、标签查询；翻页；非法 `sort`/`page`/`page_size`
- **Then**：结果集与筛选条件一致；分页 total/页边界正确；非法参数回退默认或被拒且无 500
- **Pass Condition**：断言通过
- **Evidence**：pytest

### AC-5：表单校验与乐观并发
- **Type**：`rule`
- **Given**：合法条目载荷；空标题；非法 status；超长 body；两个会话同改一条目
- **When**：提交
- **Then**：合法写入且标签关联同步；非法载荷 400 + 中文字段级错误；`expected_updated_at` 过期返回 409
- **Pass Condition**：五分支断言通过
- **Evidence**：pytest `tests/test_validate.py` / `tests/test_asgi.py`

### AC-6：云端文件与边界
- **Type**：`rule`
- **Given**：合法图片（≤5MB）；超大文件；非白名单类型；文件名含 `..` 与控制字符
- **When**：调用 `/api/uploads`
- **Then**：合法落 Storage 并返回可访问 URL；超限 413；类型非法 415；路径被净化且不含穿越片段
- **Pass Condition**：四分支断言通过
- **Evidence**：pytest `tests/test_storage.py`

### AC-7：引用完整性
- **Type**：`rule`
- **Given**：分类/标签被条目引用
- **When**：删除该分类/标签
- **Then**：409 拒绝并提示引用数量；无引用时删除成功
- **Pass Condition**：两分支断言通过
- **Evidence**：pytest

### AC-8：云端降级
- **Type**：`rule`
- **Given**：未配置 `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY`
- **When**：完整走登录→看板→新建→编辑→删除
- **Then**：内存仓储全链路可用；`/api/health` 与看板 `degraded: true`；无未捕获异常
- **Pass Condition**：冒烟脚本 + 测试断言
- **Evidence**：`scripts/smoke.py` 输出 + pytest

### AC-9：凭证零泄露
- **Type**：`rule`
- **Given**：已配置 `SUPABASE_SERVICE_ROLE_KEY`/`SESSION_SECRET` 的实例
- **When**：审计全部 HTTP 响应体、静态页面与日志输出
- **Then**：密钥原文与 Supabase URL 中的 key 段不出现在任何输出
- **Pass Condition**：响应/模板子串断言通过
- **Evidence**：pytest + 静态扫描

### AC-10：Python 红线与工程卫生
- **Type**：`rule`
- **Given**：应用源码树
- **When**：AST 扫描全部 `*.py`；检查 `pyproject.toml` 构建后端
- **Then**：无 `from __future__` 导入；`build-backend = "scikit_build_core.build"` 且含 `wheel.packages`/`build-dir`/`minimum-version`；无 cmake 段
- **Pass Condition**：AST 守护测试与配置断言通过
- **Evidence**：pytest `tests/test_no_future_annotations.py`

### AC-11：响应式与界面品质
- **Type**：`rubric`
- **Dimension**：响应式布局完好度与视觉品质（侧栏/抽屉、表格转卡片、表单密度、留白与配色）
- **Scale**：1-5
- **Anchors**：1 = 窄屏破版或元素重叠；3 = 可用但窄屏拥挤、层次普通；5 = 桌面/平板/手机三档均自然，卡片与表格切换顺滑，配色统一有质感
- **Pass Threshold**：>= 4
- **Evidence**：`web/styles.css` 断点审查 + 三档宽度静态检查清单

### AC-12：部署就绪度
- **Type**：`rubric`
- **Dimension**：一键上线顺滑度（schema 可执行、环境变量清单完整、Vercel 配置正确、README 步骤无歧义）
- **Scale**：1-5
- **Anchors**：1 = 缺关键文件导致部署失败；3 = 可部署但需 ≥2 处人工试错补齐；5 = 按 README 五步内完成（建表 → 配 4 个环境变量 → deploy）
- **Pass Threshold**：>= 4
- **Evidence**：文件清单核对 + README 步骤走查

## Open Questions

- [ ] Storage 桶是否设为 public——代码同时支持 public URL 与签名 URL，用户按桶策略自决；不阻塞。
- [ ] 后续业务字段替换（如价格/库存）——骨架已预留 `ac_items` 扩展位，届时新增列与表单字段即可；不阻塞 MVP。

> AI生成
