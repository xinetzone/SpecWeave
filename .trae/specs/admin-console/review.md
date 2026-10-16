# admin-console 独立审查（Review）

> 审查对象：[spec.md](./spec.md) · [tasks.md](./tasks.md) · `apps/admin-console/`
> 审查时状态：队列已清空（Task 1–10 全部 completed），75 项 pytest 全绿，`scripts/smoke.py` 8 组全通过。
> 审查方式：以全新上下文对照 spec 的 12 条 AC 复核，并按「安全 / 边界 / 完整性 / 时序 / 模糊」五攻击者视角主动攻击实现。

## Review History

| # | 轮次 | 结果 | 关键结论 |
|---|------|------|----------|
| 1 | 2026-10-15 | **pass** | 12 条 AC 全部有独立证据；1 条阻断级安全发现已修复并回归，6 条建议项不阻塞验收 |

---

## 检查点（Checkpoints）

### AC-1 认证与会话安全 — ✅ pass

| 分支 | 期望 | 实测 | 证据 |
|---|---|---|---|
| 未登录访问 `/api/items` | 401 | 401 | `tests/test_asgi.py::test_api_requires_session` |
| 缺 `X-CSRF-Token` | 403 `bad_csrf` | 403 `bad_csrf` | `::test_write_requires_csrf` |
| CSRF 不匹配 | 403 | 403 | `::test_write_rejects_mismatched_csrf` |
| 跨 Origin POST | 403 `bad_origin` | 403 `bad_origin` | `::test_write_rejects_cross_origin` |
| 篡改 JWT 签名 | 401 | 401 | `::test_tampered_session_is_rejected` + `test_security.py::test_session_rejects_tampered_signature` |
| 非 JSON 请求体 | 415 | 415 | `::test_write_rejects_non_json` |

### AC-2 口令存储不可逆 — ✅ pass

`hash_password` 仅返回 `(salt_hex, hash_hex)`，PBKDF2-HMAC-SHA256 200,000 轮；断言明文不出现在 salt/hash；错误 salt/空值均返回 False。证据：`tests/test_security.py::test_password_storage_has_no_plaintext`、`::test_password_salt_is_unique`、`::test_verify_password_rejects_malformed`。

### AC-3 看板聚合正确 — ✅ pass

内存仓储构造数据集，`by_status` 增量与手算一致，趋势固定 14 桶。证据：`tests/test_store.py::test_memory_store_dashboard_aggregation_matches_manual_count`。Supabase 侧总数字段解析自 `content-range`：`::test_supabase_store_parses_total_from_content_range`。

### AC-4 列表搜索筛选分页 — ✅ pass

关键词/分页/非法排序参数均有断言；注入串经 `urlencode`，SQL 元字符不出现在最终 URL。证据：`test_store.py::test_memory_store_pagination_and_search`、`::test_supabase_store_encodes_filter_values`、`::test_supabase_store_whitelists_sort_fields`、`::test_supabase_store_rejects_unknown_table`。

### AC-5 表单校验与乐观并发 — ✅ pass

空标题/非法 status/超长 body 字段级错误；`expected_updated_at` 过期返回 409；未携带同名并发写成功。证据：`test_validate.py` 全量、`test_asgi.py::test_item_create_update_delete_flow`、`test_store.py::test_memory_store_optimistic_concurrency`。

### AC-6 云端文件与边界 — ✅ pass

成功/超限 413/类型非法 415/路径穿越净化 四类断言齐备；服务端生成路径（日期分片 + 随机名），文件名净化后不含 `..`。证据：`test_storage.py` 全量、`test_asgi.py::test_upload_*`。

### AC-7 引用完整性 — ✅ pass

被引用分类/标签删除返回 409 `conflict`。证据：`test_store.py::test_memory_store_blocks_deleting_used_category`、`::test_memory_store_blocks_deleting_used_tag`、`test_asgi.py::test_category_delete_blocked_when_referenced`。

### AC-8 云端降级 — ✅ pass

未配置云端时 `build_store` 返回 `MemoryStore`，`/api/health` 与看板 `degraded: true`；`scripts/smoke.py` 8 组全链路退出码 0。证据：`test_store.py::test_build_store_falls_back_to_memory_without_cloud`、`::test_supabase_store_degrades_on_network_failure`、smoke 输出。

### AC-9 凭证零泄露 — ✅ pass

`/api/health` 与鉴权链路响应体断言不含 `service-role-secret`。证据：`test_asgi.py::test_health_reports_degraded_without_leaking_secret`。另：`.env.example` 全占位符，`app/.gitignore` 覆盖 `.env`。

### AC-10 Python 红线与工程卫生 — ✅ pass

AST 守护扫描 `src/`、`api/`、`scripts/` 无 `from __future__`；`pyproject.toml` 使用 scikit-build-core 且含 `wheel.packages`/`build-dir`/`minimum-version`，无 cmake 段。证据：`tests/test_no_future_annotations.py`。

### AC-11 响应式与界面品质 — ✅ pass（rubric 4/5）

`web/styles.css` 具备 1200/900/720/420 四档断点，<900 侧栏转抽屉、<720 表格转卡片（`td::before` 渲染 `data-label`），表单栅格单列。锚点 4 分理由：配色与层次统一、三档均不破版；未达 5 分因未做真机截图评审（本轮不做额外视觉校验）。证据：断点清单 + `app.html` 中 `data-label` 覆盖全部数据列。

### AC-12 部署就绪度 — ✅ pass（rubric 5/5）

`schema.sql`（七表 + 索引 + RLS）+ `.env.example`（3 必填 + 4 可选）+ `vercel.json` + `.python-version` + README 五步上线齐备；ASGI 层实测 `/login`、`/static/*`、`/api/health` 均 200。证据：ASGI 层实测输出 + 文件清单核对。

---

## 五视角对抗发现

### 🔴 安全（阻断级，已修复）

**F1 · 演示账号默认口令在公网暴露**
- 攻击路径：若用户未配置 Supabase 就把应用部署到 Vercel，内存降级模式会注入 `admin@example.com / admin12345`——口令公开可知，任何人可登录后台。
- 判定：**阻断**。原实现把「本地演示便利」错当成「生产默认」。
- 修复：`Config.demo_admin_enabled = (not VERCEL) and ADMIN_DEMO != "0"`；`MemoryStore` 仅在其为真时注入演示账号；`/api/health` 新增 `demo_login` 标志，登录页仅在该标志为真时提示演示账号。
- 回归：`tests/test_store.py::test_demo_admin_is_disabled_in_production`（VERCEL=1 时 `count_admins() == 0`），75 项测试全绿。

### 🟠 边界 / 完整性（建议项，不阻塞）

| ID | 发现 | 评估 | 处置 |
|---|---|---|---|
| F2 | Serverless 多实例下 `LoginLimiter` 为进程内计数，攻击者可分摊请求绕过 | 限速为「尽力而为」，已与恒定延时配合 | 接受；README 与代码注释已明示，后续可换 Supabase 表计数 |
| F3 | `_attachment_delete` 忽略 Storage 删除结果，云端对象残留时仍返回成功 | 数据库记录已删，孤立对象不暴露（私有桶） | 接受并记录；建议后续加清理任务 |
| F4 | PATCH 未携带 `expected_updated_at` 时退化为 last-write-wins | 前端 `saveItem()` 始终携带 | 接受；后续可改为服务端强制 |
| F5 | 看板趋势为控制复杂度，取最近 5000 条 `created_at` 在服务端聚合 | 万级数据内可接受 | 接受；数据量增长后改用 SQL `date_trunc` 聚合视图 |
| F6 | 会话无吊销机制（无 `jti`/黑名单），登出仅清 Cookie | Cookie 为 HttpOnly + 12h 过期，风险可控 | 接受；如需强制下线再加服务端会话表 |
| F7 | `ac_items` 无全文索引，大表 `ilike` 扫描变慢 | MVP 量级（数万）可接受 | 接受；已建 status/category/时间索引 |

### 🟢 已验证无问题的攻击面

- SQL/PostgREST 注入：表名走 `TABLES` 白名单列名与排序字段走映射表，过滤值 `urlencode` — 已断言。
- 路径穿越：上传文件名与对象路径双重净化，`../../etc/passwd` → `etc/passwd` — 已断言。
- XSS：前端所有用户内容经 `esc()` 转义，服务端不回显 HTML — 已审查 `web/app.js`。
- 密钥泄露：service_role key 仅出现在服务端请求头；响应体与静态页均无 — 已断言。
- 未捕获 500：`build_app` 外层兜底为 JSON 500，业务路径全部显式降级。

---

## 结论

- **结果**：`pass`
- 所有必需检查点通过；每条 rule AC 有独立证据；rubric AC 达阈值并附理由。
- F1 为唯一阻断项，已修复并回归；F2–F7 为建议项，不影响本次验收，已记入后续迭代。
