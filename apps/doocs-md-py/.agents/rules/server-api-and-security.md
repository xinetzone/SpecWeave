---
id: "doocs-md-py-rule-server-api-and-security"
title: "服务端契约、安全与配置治理"
source: "../../AGENTS.md#P0 约束速览"
---

# 服务端契约、安全与配置治理

> **适用范围**：修改服务端端点、路由装配、错误体、数据库与迁移、鉴权、分享页、配置项处理、上传后端、爱发电回调。
> **权威事实源**：[../../src/doocs_md_py/server/app.py](../../src/doocs_md_py/server/app.py)（装配顺序）、[../../src/doocs_md_py/server/config.py](../../src/doocs_md_py/server/config.py)（环境变量单一事实源）、[../../src/doocs_md_py/server/db.py](../../src/doocs_md_py/server/db.py)、[../../docs/contract-mapping.md](../../docs/contract-mapping.md)（端点/字段对拍表）。

## §1 契约 1:1 范围与装配顺序

- 服务端对外契约（路径、方法、请求/响应字段、状态码、错误体形状、响应头）**与上游 `apps/api` 1:1**；对拍表为 [../../docs/contract-mapping.md](../../docs/contract-mapping.md)，任何字段级差异必须登记 `D-`/`CD-`（见 [upstream-reconstruction.md](upstream-reconstruction.md) §4）。
- **路由装配顺序**由 `server/app.py` 的应用工厂集中定义，顺序影响中间件与路由匹配优先级；**禁止**在路由模块内自行 `include_router` 打乱顺序。
- 路由模块位于 `server/routers/`（9 个）；**业务逻辑不得堆在路由函数里** —— 路由只做参数校验、鉴权依赖注入与响应封装，逻辑下沉到 `server/*.py` 领域模块。
- **错误体统一**：由既有错误处理路径收口（见 `tests/server/test_error_contract.py`）；新增端点必须复用同一形状，**禁止**自定义裸 `JSONResponse` 破坏契约。

## §2 持久化（SQLite 替代 D1）

- 上游 Cloudflare D1 方言在本仓等价映射为 **SQLite**（结构性差异，登记为 `D-` 编号）。
- **迁移**：`server/migrations/`（`0001_init.sql` … `0008_*.sql`，共 8 个）**原样移植**上游 `apps/api/migrations/`；新增迁移必须继续编号、**幂等可重入**，并由 `tests/server/test_migrations.py` 覆盖。
- **时间语义**：时间戳统一 **epoch 毫秒**；跨端同步采用 **LWW（Last-Write-Wins）** 冲突策略，由 `server/db.py` 的 upsert 实现（覆盖见 `tests/server/test_db_lww.py`）。
- **拉取游标**：pull 接口使用游标分页，游标语义对齐上游；**禁止**改用自造分页参数。
- **配额与限流**：配额常量与限流窗口在 `server/sync_limits.py` / `server/ratelimit.py`；限流窗口对齐上游（UTC 窗口，等价实现）。**禁止**在业务代码内散落计数器。
- 数据库与本地对象存储落在应用内 `data/` 目录（已 `.gitignore`），**不得入库**。

## §3 鉴权与 Origin 白名单

- **JWT**：算法 **HS256**，有效期 **30 天**；签发与校验集中于 `server/security.py`。密钥来自配置（必填），**不得有内置默认密钥**。
- **GitHub OAuth**（`server/github_oauth.py`）：`state` 校验采用**双 cookie** 方案（对齐上游 `auth.ts`）；回调校验失败一律拒绝，不得降级放行。
- **Origin 白名单**（`server/origin.py`）：默认来源为单站点（`APP_URL`）；**单标签 `*` 的语义必须严格对齐上游**（仅作特定通配用途，不得当作"允许任意来源"）；浏览器扩展来源按其独立规则处理。
- 出站请求统一 `User-Agent: md-api` 标识（便于上游/第三方识别），由 `server/httputil.py` 收口。

## §4 分享页（净化 / CSP / 密码门）

- **密码存储**：PBKDF2-SHA256，迭代 **100000**；**比较必须常量时间**（`hmac.compare_digest`），实现于 `server/share_password.py`，并有跨实现互操作测试向量（`tests/golden/share_pbkdf2_interop.json`）。
- **Cookie 作用域**：分享解锁 cookie 的 `path` **精确固定为 `/s/<id>`** —— 收紧作用域，**禁止**放宽到 `/`。
- **CSP**：分享页响应头使用**固定 CSP 串**（对齐上游），**禁止**为兼容性放宽到 `unsafe-inline` / `*`。
- **净化**：分享内容经 `server/share_sanitize.py` 黑名单净化（对齐上游 `share-sanitize.ts`）；**黑名单项只增不减需经裁决**，删除项等同安全回退。
- **状态码语义**：分享不存在→404；已过期/已撤销→410；访问计数按上游口径递增。**禁止**混用 404/410 语义。

## §5 安全与配置治理

- **密钥治理（P0）**：密钥**不入库、不入日志、不回显**。启动体检 `server/config_report.py` 只输出"启用 / 未启用"状态，**绝不回显密钥值**（对应 FR-15）。`.env.example` 只列键名与说明，**不含真实值**。
- **配置单一事实源**：全部环境变量与默认值集中在 `server/config.py`；`.env.example` 必须与之对齐（新增变量两侧同步）。本仓新增变量统一前缀 `DOOCS_MD_PY_*`。
- **安全响应头**：静态与动态响应携带 `X-Content-Type-Options: nosniff` 与 `ETag` 语义（对齐上游）。
- **默认回环**：服务默认只绑 `127.0.0.1`；**禁止**把默认监听改为 `0.0.0.0`。
- **单 worker**：默认单 worker 运行（SQLite + 内存态一致性要求）；**禁止**在多 worker 下宣称配额/限流/幂等正确。
- **付费回调默认关闭**：爱发电相关能力默认关闭，仅在显式配置后启用。

## §6 上传后端门控与对象键（服务端 `/upload`）

> 注意：本节仅涉 **服务端上传后端**（`server/upload_*.py`）；Web 客户端图床是**另一套路径**，见 [uploaders-dual-path.md](uploaders-dual-path.md) §1。

- **门控**：由 `UPLOAD_ENABLED` 开关控制，未启用时端点必须拒绝而非静默通过。
- **校验链**：MIME 前缀校验 → 大小上限（≤5 MiB）→ 限流（`server/upload_rate.py`）；任一不通过即拒绝，**禁止**跳过任一步。
- **对象键生成**（`server/upload_filename.py`）：格式 `<epochms>-<uuid>.<ext>`；对象存储路径前缀 `YYYY/MM/DD`。**禁止**改用客户端提供文件名。
- **GitHub 后端**（`server/upload_github.py`）：使用 GitHub contents API 上传，返回地址按上游规则改写为 jsDelivr CDN。
- **R2 等价**（`server/upload_r2.py`）：以 **S3 SigV4（标准库手写）** 等价实现；签名正确性由测试向量守护（`tests/golden/sigv4_vectors.json`、`tests/server/test_sigv4_vectors.py`）。**禁止**引入 `boto3`（见 [engineering-redlines.md](engineering-redlines.md) §2）。
- 对象存储抽象在 `server/storage.py`（local / S3 后端）；表情资产使用独立桶（`server/emoji_storage.py`）。

## §7 爱发电（webhook / 回查 / 幂等）

- **出站验签**：调用爱发电 API 使用 **md5 签名**，签名构造严格遵循上游协议；空响应或非 200 统一返回 `None`（不做部分解析）。
- **webhook 只信订单号**：回调体**只采信 `out_trade_no`**，**订单事实一律通过开放平台回查确认**。**不得信任回调传入的其它字段**（防止伪造）。
- **幂等**：`afdian_orders` 表以订单号幂等，重复回调不得重复发放 Pro 权限。
- **资格判定**：`status=2` 且 `product_type ∈ {0,1}` 且 `plan_id` 命中白名单，三者同时满足才发放；不符合者**静默忽略**（不报错、不发放）。
- 相关测试：`tests/server/test_afdian.py`。

## §8 反模式（出现即打回）

| # | 反模式 | 后果 |
|---|--------|------|
| A1 | 端点字段/状态码偏离上游且未登记 `D-`/`CD-` | 契约破坏，前端接入失败 |
| A2 | 回显密钥 / 写密钥进日志 / `.env.example` 填真实值 | 凭证泄露 |
| A3 | 分享解锁 cookie 放宽到 `path=/`，或 CSP 放松 | 安全回退 |
| A4 | 密码比较用 `==` 非常量时间 | 时序侧信道 |
| A5 | 默认监听 `0.0.0.0` 或多 worker 下宣称配额正确 | 暴露面扩大 / 语义错误 |
| A6 | 信任爱发电回调非订单号字段，或跳过回查 | 权限伪造 |
| A7 | 引入 `boto3` 做 S3，或换掉已验证签名算法 | 破坏测试向量与依赖白名单 |
| A8 | 跳过 MIME/大小/限流任一步 | 上传滥用 |

## 变更纪律

- 本文档只增不删；端点契约、持久化语义、鉴权参数、分享安全参数四者变更须同步 [../../docs/contract-mapping.md](../../docs/contract-mapping.md) 与 [../../docs/contract-differences.md](../../docs/contract-differences.md)，并补回归测试后回写本文。
