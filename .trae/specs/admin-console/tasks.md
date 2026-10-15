# admin-console 实施队列

> 由 [spec.md](./spec.md) 派生。每条任务映射 AC，含任务级测试要求（TR，类型 `rule`/`rubric`）。
> 状态取值：`pending` / `in_progress` / `blocked` / `completed` / `cancelled`。

## Task 1: 工程骨架与 Python 红线守卫

**Status**: completed
**Priority**: high
**Maps to AC**: AC-10
**Depends on**: —

- 创建 `apps/admin-console/`，落 `pyproject.toml`（scikit-build-core 纯 Python、`requires-python >=3.14`）、`requirements.txt`（空/注释）、`.python-version`、`vercel.json`、`api/index.py`、`schema.sql`。
- **TR-1.1** `rule`：`pyproject.toml` 的 `build-backend == "scikit_build_core.build"` 且 `[tool.scikit-build]` 含 `wheel.packages`/`build-dir = "build/{wheel_tag}"`/`minimum-version = "0.9"`，无 `[tool.scikit-build.cmake]` 段。
- **TR-1.2** `rule`：AST 扫描 `src/**.py` 无 `from __future__` 导入（守护测试 `tests/test_no_future_annotations.py`）。
- **TR-1.3** `rule`：`python3.14 -c "import admin_console"` 可导入且 `sys.version_info >= (3, 14)`。

## Task 2: 安全内核（PBKDF2 + HS256 JWT + CSRF + Origin）

**Status**: completed
**Priority**: high
**Maps to AC**: AC-1, AC-2
**Depends on**: Task 1

- 实现 `src/admin_console/security.py`：`hash_password`/`verify_password`（PBKDF2-SHA256 ≥200k，随机 salt）、`sign_session`/`verify_session`（HS256，`exp`+`role`，常量时间比对）、`new_csrf_token`/`csrf_ok`、`origin_ok`。
- **TR-2.1** `rule`：正确/错误口令、错误 salt 三分支断言；落库仅 hash+salt。
- **TR-2.2** `rule`：JWT 篡改签名/篡改 payload/过期三类均返回 `None`。
- **TR-2.3** `rule`：登录失败限速（同邮箱 10 分钟内 >10 次锁定 10 分钟）计数断言。

## Task 3: Supabase 仓储（PostgREST）与内存降级

**Status**: completed
**Priority**: high
**Maps to AC**: AC-3, AC-4, AC-5, AC-7, AC-8
**Depends on**: Task 1

- 实现 `src/admin_console/http_client.py`（超时 8s + 指数退避重试 1 次）与 `store.py`（七表 CRUD、计数、标签关联、引用计数、审计日志、看板聚合）与内存降级 `MemoryStore`。
- **TR-3.1** `rule`：过滤值经 `urlencode`、表名/列名/排序字段走白名单映射——构造注入串（`' or 1=1`、`; drop`）断言不出现在最终 URL。
- **TR-3.2** `rule`：假 `urlopen` 注入下，看板聚合与手算一致（AC-3 数据集）。
- **TR-3.3** `rule`：引用计数 >0 的删除返回 409；无引用删除成功。
- **TR-3.4** `rule`：PATCH 乐观并发 `expected_updated_at` 不匹配 → 409。

## Task 4: Supabase Storage 接入与上传边界

**Status**: completed
**Priority**: high
**Maps to AC**: AC-6
**Depends on**: Task 3

- 实现 `src/admin_console/storage.py`：上传（裸二进制转发 + `x-upsert`）、删除、public URL / 签名 URL；文件名净化（去 `..`、控制字符、路径分隔符）；体积 ≤5MB、类型白名单。
- **TR-4.1** `rule`：四类（合法/超限/类型非法/路径穿越）断言通过。
- **TR-4.2** `rule`：`sanitize_object_path("../../etc/passwd")` 不含 `..` 与分隔符。

## Task 5: 输入校验层

**Status**: completed
**Priority**: high
**Maps to AC**: AC-5
**Depends on**: Task 1

- 实现 `src/admin_console/validate.py`：条目/分类/标签载荷白名单校验、slug 生成、长度与枚举约束、字段级中文错误。
- **TR-5.1** `rule`：空标题/非法 status/超长 body/未知字段/负数分页五分支断言通过。

## Task 6: ASGI 应用与路由（含鉴权中间件）

**Status**: completed
**Priority**: high
**Maps to AC**: AC-1, AC-5, AC-6, AC-9, AC-10
**Depends on**: Task 2, 3, 4, 5

- 实现 `src/admin_console/asgi.py`：静态白名单、`/api/auth/*`、`/api/dashboard`、`/api/items*`、`/api/categories*`、`/api/tags*`、`/api/uploads`、`/api/attachments*`、`/api/logs`、`/api/health`；统一鉴权 + CSRF + Origin + 非 JSON 拒绝 + 永不 500。
- **TR-6.1** `rule`：AC-1 六分支（未登录 401 / CSRF 缺失 403 / CSRF 不匹配 403 / 跨 Origin 403 / 篡改签名 401 / 非 JSON 415）断言通过。
- **TR-6.2** `rule`：全响应体不含 `SUPABASE_SERVICE_ROLE_KEY` 与 `SESSION_SECRET` 原文。
- **TR-6.3** `rule`：上传四分支（200/413/415/400）与附件删除联动态。

## Task 7: CLI（serve / doctor / seed-admin）与本地冒烟

**Status**: completed
**Priority**: medium
**Maps to AC**: AC-8
**Depends on**: Task 6

- 实现 `src/admin_console/cli.py`（WSGI→ASGI 适配本地启动、配置体检、创建管理员）与 `scripts/smoke.py`（未配置云端时全链路冒烟）。
- **TR-7.1** `rule`：无云端配置下冒烟脚本退出码 0 且打印各步骤 OK。
- **TR-7.2** `rule`：`doctor` 输出含 `cloud_ready`/`session_secret`/`storage` 且不含密钥原文。

## Task 8: 前端（登录页 + 后台单页，响应式）

**Status**: completed
**Priority**: high
**Maps to AC**: AC-11
**Depends on**: Task 6

- `web/login.html`、`web/app.html`、`web/styles.css`、`web/app.js`：登录 → 看板（指标卡 + SVG 趋势 + 分类分布 + 日志）→ 列表（搜索/筛选/排序/分页/批量）→ 抽屉表单（字段 + 标签 + 拖拽上传 + 校验提示）；分类/标签维护页；Toast 与降级横幅。
- **TR-8.1** `rubric`：响应式与视觉品质（同 AC-11，1-5，阈值 ≥4）。
- **TR-8.2** `rule`：三档宽度（1440/900/375）关键容器无溢出（`overflow-x` 检查 + 媒体查询断点存在性断言）。

## Task 9: 部署就绪产物与文档

**Status**: completed
**Priority**: high
**Maps to AC**: AC-12
**Depends on**: Task 6

- `schema.sql`（七表 + 索引 + 初始分类/标签）、`.env.example`（4 个变量，占位符）、`README.md`（五步上线）、`vercel.json` 校验。
- **TR-9.1** `rubric`：一键上线顺滑度（同 AC-12，1-5，阈值 ≥4）。
- **TR-9.2** `rule`：`.env.example` 含全部必填变量占位且无真实密钥；`schema.sql` 含七张 `ac_` 表。

## Task 10: 登记与收尾（路由表 + 看板刷新）

**Status**: completed
**Priority**: medium
**Maps to AC**: AC-10
**Depends on**: Task 9

- 更新 `apps/AGENTS.md` 路由表与边界声明；刷新 `.trae/specs` 看板。
- **TR-10.1** `rule`：`apps/AGENTS.md` 出现 `admin-console` 条目且链接可达。

## Review Issues

（空：首轮 Review 结果 `pass`，无待修复项。审查详情见 [review.md](./review.md)。）

## 完成证据汇总

| 任务 | 完成证据 |
|---|---|
| Task 1 工程骨架 | `apps/admin-console/{pyproject.toml,requirements.txt,.python-version,vercel.json,api/index.py}`；`tests/test_no_future_annotations.py` 通过；Python 3.14.3 实测可导入 |
| Task 2 安全内核 | `src/admin_console/security.py`；`tests/test_security.py` 12 项通过（口令/签名/CSRF/Origin/限速） |
| Task 3 Supabase 仓储 | `src/admin_console/{http_client,store}.py`；`tests/test_store.py` 18 项通过（注入防护/聚合/引用/降级） |
| Task 4 Storage 接入 | `src/admin_console/storage.py`；`tests/test_storage.py` 8 项通过（净化/超限/类型/URL） |
| Task 5 输入校验 | `src/admin_console/validate.py`；`tests/test_validate.py` 11 项通过 |
| Task 6 ASGI 路由 | `src/admin_console/asgi.py`；`tests/test_asgi.py` 22 项通过；ASGI 层实测 `/login`、`/static/*`、`/api/health` 均 200 |
| Task 7 CLI 与冒烟 | `src/admin_console/cli.py`、`scripts/smoke.py`；冒烟 8 组全 OK、退出码 0 |
| Task 8 前端 | `web/{login.html,app.html,styles.css,app.js}`；四档断点 + `data-label` 表格转卡片；rubric 4/5 |
| Task 9 部署产物 | `schema.sql`（七表+索引+RLS）、`.env.example`、`.gitignore`、`README.md`（五步上线）；rubric 5/5 |
| Task 10 登记收尾 | `apps/AGENTS.md` 路由表与边界声明已登记 `admin-console` |

**回归**：`python -m pytest -q` 75 passed；`python scripts/smoke.py` 退出码 0。

## 原子提交记录（C 阶段）

| # | 提交 | 主题 | 文件数 |
|---|---|---|---:|
| 1 | `74340da30` | docs(spec): 新增 admin-console 通用内容管理后台规格三件套 | 3 |
| 2 | `314948ba2` | chore(apps/admin-console): 建立 Python 3.14 零第三方依赖工程骨架 | 8 |
| 3 | `bedfc09d5` | feat(apps/admin-console): 新增安全内核与服务端输入校验层 | 2 |
| 4 | `6a7cf0372` | feat(apps/admin-console): 新增 Supabase 云端仓储与文件存储层 | 3 |
| 5 | `e5c513774` | feat(apps/admin-console): 新增 ASGI 路由层与命令行入口 | 2 |
| 6 | `260ef0ef9` | test(apps/admin-console): 新增 75 项测试与离线冒烟脚本 | 8 |
| 7 | `9482de1e6` | feat(apps/admin-console): 新增零构建响应式后台前端 | 4 |
| 8 | `041e812ac` | docs(apps/admin-console): 新增五步上线文档、建表脚本与环境变量模板 | 3 |

> 路由表与边界声明登记（`apps/AGENTS.md` 第 79 / 287 行）随并发会话提交 `3b9d5505d` 一并入库，内容已核验正确。
>
> 提交过程实测两点并发风险：① 并行会话占用索引导致 `git-commit-utf8` 中止，按 [commit-staging-integrity](../../../.agents/rules/commit-staging-integrity.md) R1/R3 等待索引释放后重提；② 路径级提交不清索引残留，需在每枚提交后 `git restore --staged` 自清。另按敏感信息钩子要求为测试桩值补 `# nosec`（与命中同行）。
