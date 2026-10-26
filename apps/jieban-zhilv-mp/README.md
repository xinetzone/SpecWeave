# 结伴之旅 · 活动报名微信小程序

面向**全人类**的活动报名小程序：活动首页、活动详情、在线报名、报名记录四个页面，
支持微信授权登录，活动与报名数据存于云端数据库，活动图片存于云端存储。

## 功能

| 页面 | 路径 | 职责 |
|------|------|------|
| 活动首页 | `pages/index/index` | 品牌区 + 活动卡片列表（时间、地点、名额进度、费用），支持下拉刷新，点击进入详情 |
| 活动详情 | `pages/detail/detail` | 主图、亮点、报名须知、名额进度，底部固定「立即报名」 |
| 在线报名 | `pages/signup/signup` | 同行人数、手机号校验、备注、报名配图上传（存云端存储） |
| 报名记录 | `pages/records/records` | 本人报名列表、状态、取消报名 |

底部 Tab：活动 / 我的报名。

## 技术栈与云端能力

| 能力 | 实现 |
|------|------|
| 微信授权登录 | `wx.login` → `cloud.auth.signInWithWechat(code, appid)`，`appid` 取运行时真实值 |
| 云端数据库 | `cloud.database.from('activities' / 'registrations')`（PostgREST 兼容 supabase-js 风格） |
| 云端存储 | `utils/storage.js`：`createSignedUrl` 取签名地址读图；`createSignedUploadUrl` + `wx.request` 直传写图 |
| 名额校验 | 服务端 `submit_signup` RPC（`SECURITY DEFINER` + `FOR UPDATE` 行锁）原子完成，客户端不传 `owner_id` |

### 数据模型

```
activities     id, slug, title, summary, cover_path, location,
               starts_at, ends_at, capacity, price_note,
               highlights(jsonb), notes(jsonb), published,
               owner_id（创建者；客户端不读）

registrations  id, activity_id → activities.id, owner_id, owner_name,
               contact, companions, remark, cover_path,
               status('confirmed'|'cancelled'), created_at
```

### 服务端函数

| 函数 | 可执行角色 | 职责 |
|------|-----------|------|
| `submit_signup(activity_id, companions, contact, remark, owner_name, cover_path)` | `authenticated` | 报名写入唯一入口：登录态 + 字段 + 活动状态 + **人数口径**容量校验 + 行锁 |
| `cancel_registration(registration_id)` | `authenticated` | 软取消本人有效报名（保留历史） |
| `attach_registration_cover(registration_id, cover_path)` | `authenticated` | 绑定本人报名配图，路径须落在本人私有目录且记录为 `confirmed` |
| `registration_stats()` | `authenticated` + `anon` | 各活动已报名**人数**（跨用户聚合，不放开原始表读权限；只统计已发布活动） |
| `sync_activity_cover(slug)` | `authenticated` + `service_role` | 绑定活动主图到**规范路径** `shared/_application/activities/<slug>.png`。目标路径由服务端拼出、调用方无法指定；对象尚未上传则拒绝绑定。只返回路径字符串 |
| `claim_activity(activity_id, owner_uid)` | 仅 `service_role` | **管理侧**显式指派活动归属。终端用户无法调用，因此不可能出现「谁先登录谁就是创建者」 |
| `set_activity_cover(slug, path)` | 仅 `service_role` | 管理侧绑定主图（路径前缀 `shared/_application/activities/`）。**只返回路径**，不返回 `activities` 行 |

> `signup` 是已关闭的历史入口（不授予任何角色），保留仅为阻止旧客户端绕过校验。
>
> `set_activity_cover` 刻意只返回路径字符串：旧版返回 `SETOF activities`，响应体带
> `owner_id`，一旦被误授权给 `authenticated`，创建者标识就会绕开列级授权从 RPC 响应体下发。
> 终端用户要绑定主图请用 `sync_activity_cover`。

### 权限矩阵

| 角色 | activities | registrations | 报名 RPC | 主图绑定 RPC | 归属指派 |
|------|-----------|--------------|---------|------------|---------|
| `anon` | 仅 13 个业务列 | 无（RLS 恒空） | — | — | — |
| `authenticated` | 同上（不含 `owner_id` / `created_at`） | 仅 SELECT（RLS 限本人） | 可调 | `sync_activity_cover` 可调 | — |
| `service_role` | 全表 | 全表 | 可调 | 可调 | 可调 |

### 安全模型

- **写入全部收敛到 RPC**：客户端对 `activities` / `registrations` 两表只有 `SELECT` 权限；
  `registrations` 的 insert/update/delete RLS 策略已删除，表级 `GRANT` 也已收窄。
- **`activities` 采用列级授权**：`owner_id` 存的是微信 uid（形态 `wx:<openid>`）。
  若给表级 `SELECT`，访客直接 `GET /.cloud/database/rest/activities?select=owner_id`
  就能绕过客户端读到创建者的 openid。因此撤销表级 SELECT，只逐列授予 13 个业务列
  （`created_at` 客户端与脚本都不读，按最小权限不授权）；
  `owner_id` 仅供 RLS 策略内部求值（策略求值不需要列级 SELECT 授权）。
  实测：业务列读 200；`select=owner_id` 与 `select=*` 均 42501；未发布活动对非归属人仍不可见。
- **主图路径取值域不含用户标识**：`activities.cover_path` 是公开可读列，一旦它的值里
  内嵌 owner uid，就等于用「主图路径」这条后门把已从 `owner_id` 撤掉的创建者标识
  又原样下发——同一张表两列可见性不一致，属于自己打自己。
  现在 `cover_path` 的取值域被**服务端锁死**为 `shared/_application/activities/<slug>.png`：
  - `sync_activity_cover` 由服务端拼出目标路径，调用方无法指定，也不接受路径参数；
  - `set_activity_cover` 只接受 `shared/_application/` 前缀；
  - 旧通道 `claim_activity_cover`（唯一能写入含 uid 路径的入口）已显式 `DROP`。
  该作用域属主是应用身份 `wbapp:<applicationId>`，而 `applicationId` 本就硬编码在客户端
  `publishableKey` 里，不构成新增泄露。
- **归属不能被终端用户夺取**：归属建立（`claim_activity`）只有 `service_role` 能执行，
  且必须显式给出 `p_owner_uid`；客户端对 `activities` 无 UPDATE 权限，
  因此普通用户无法把自己写进任何活动的 `owner_id`。
- **人数口径统一**：`registration_stats()` 与 `submit_signup()` 的容量校验一律按
  `sum(companions)`（含本人），客户端 `quotaText` / `percent` / `isFull` / `canFit` 与之对齐。
  `capacity <= 0` 表示不限名额。
- **防重复报名**：部分唯一索引 `(activity_id, owner_id) WHERE status = 'confirmed'`；
  取消后 `status` 变为 `cancelled`，允许再次报名。
- **不静默抹除数据**：活动删除为 `ON DELETE RESTRICT`，避免连带删掉用户报名记录。
- **存储路径受服务端约束**：报名配图路径按 `/` 结构化分段比较，必须是
  `users/<调用者 uid>/registrations/<文件名>`；校验**不把 uid 拼进正则模式**
  （uid 含 `.` 等元字符时拼进模式会放宽校验）。活动主图路径则由服务端拼出，
  调用方不可指定。
- **不泄露用户标识**：客户端不查询也不接收 `owner_id`，服务端授权面也已将其移出访客可见列；
  `cover_path` 的取值域同样不含 uid（见上一条），RPC 响应体也不回传 `activities` 行。
- **错误文案不外泄**：所有后端原始错误映射为可读文案，兜底固定为「报名失败，请稍后重试」。
- **令牌不落盘**：本地缓存的会话快照只保留 `id` / `name` / `avatarUrl` / `provider`，
  `accessToken` / `refreshToken` 不写入 wx storage。

## 目录结构

```
jieban-zhilv-mp/
├── app.js / app.json / app.wxss      # 全局逻辑与设计令牌
├── project.config.json                # miniprogramRoot: "./"，tests 已排除打包
├── sitemap.json
├── package.json
├── pages/                             # index / detail / signup / records
├── utils/
│   ├── cloud.js                       # 云客户端（唯一 SDK 初始化点）
│   ├── api.js                         # 数据访问层
│   ├── auth.js                        # 会话与微信授权登录
│   ├── format.js                      # 展示层格式化（纯函数）
│   ├── storage.js                     # 云端存储读写（签名 URL + 二进制直传）
│   └── workbuddy-cloud-diagnostics.js # 请求诊断适配器
├── vendor/workbuddy-cloud-sdk/        # SDK 官方发布产物（免「构建 npm」步骤）
├── assets/icons/                      # 22 个统一风格线性图标（PNG）
├── assets/covers/                     # 4 张活动主图（PNG，本地降级图，文件名=slug）
├── scripts/
│   ├── generate_assets.py             # 素材生成脚本（Pillow）
│   ├── db/                            # 云数据库最终态真相源（逐条 SQL）
│   └── tools/
│       └── sync-activity-covers.cjs   # 运营脚本：绑定并校验主图（上传走管理页）
└── tests/
    ├── format.test.js                 # 纯函数单测（32 项）
    └── structure.test.js              # 静态契约检查（46 项）
```

### `scripts/db/` 说明

云端 MCP 端点不支持多语句，故按「每次一条语句」拆分为独立文件：

| 文件 | 内容 |
|------|------|
| `schema.sql` | 云端最终态**单一真相源**：建表、CHECK 约束、部分唯一索引、RLS 策略、表级 GRANT、七个服务端函数及函数级 EXECUTE 权限矩阵 |
| `fn_submit_signup.sql` | 报名写入唯一入口 |
| `fn_cancel_registration.sql` | 软取消 |
| `fn_registration_stats.sql` | 人数口径聚合（只统计已发布活动） |
| `fn_attach_registration_cover.sql` | 报名配图绑定（限本人、限 `confirmed`） |
| `fn_set_activity_cover.sql` | 活动主图绑定（管理侧，只接受 `_application` 前缀，只返回路径） |
| `fn_claim_activity.sql` | 活动归属指派（管理侧，需显式给出归属 uid） |
| `fn_sync_activity_cover.sql` | 活动主图绑定（canonical 通道，路径由服务端拼出） |

## 素材

图标与主图均由 `scripts/generate_assets.py` 以 Pillow 几何绘制生成，
风格统一为线性描边 + 扁平色块，**不使用 Emoji**：

```bash
python scripts/generate_assets.py
```

图标主色 `#2f2733`/`#2f6bff`，栅格 64px（Tab 图标 81px）。

**主图命名规则**：本地 `assets/covers/<slug>.png` 与云端
`shared/_application/activities/<slug>.png` **同名**。因此往管理页上传时直接选
`assets/covers/` 下的文件即可，无需重命名；本地兜底图的推导规则也与之对齐
（`utils/format.js` 的 `fallbackCover`）。

> 本地兜底图是**匿名访客唯一能看到的主图来源**：云存储是私有桶，没有公开读通道，
> 未登录用户拿不到签名地址（实测 `401 MISSING_CREDENTIALS`），因此 `assets/covers/`
> 里的副本必须随包分发。登录用户则看到云端主图。
> 兜底图路径按 slug 规则推导，**不再依赖硬编码映射表**——新增活动只要把
> `<slug>.png` 放进 `assets/covers/` 就自动命中；本地没有对应文件时，
> `<image>` 的 `binderror` 会降级到 `default.png`。

## 本地运行

1. 微信开发者工具导入本目录（`miniprogramRoot` 为 `./`）。
2. 直接编译运行。**无需执行「构建 npm」**：SDK 官方发布产物已随应用 vendoring 到
   `vendor/workbuddy-cloud-sdk/miniprogram.js`（零外部依赖的自包含 CommonJS bundle），
   `utils/cloud.js` 直接 require 该副本。
3. 微信授权登录需在小程序账号下调试（工具内模拟器无法取得真实 `wx.login` code，
   需真机或已授权的体验版验证）。

> 若改用 npm 方式安装 SDK，则需在开发者工具执行「工具 → 构建 npm」，
> 生成 `miniprogram_npm/@tencent-ai/workbuddy-cloud-sdk/miniprogram.js` 后再编译；
> 且 `project.config.json` 的 `setting.nodeModules` 需为 `true`。

## 运营步骤

### 一次性：把活动归属指派给运营账号

活动由管理侧预置时 `owner_id` 为空。归属必须由管理侧**显式指派**
（`claim_activity` 仅 `service_role` 可执行，终端用户无法调用）：

```sql
-- 指派：p_activity_id 为活动 id，p_owner_uid 为运营账号的 uid
SELECT public.claim_activity(1, '2114562052432330752');
SELECT public.claim_activity(2, '2114562052432330752');
SELECT public.claim_activity(3, '2114562052432330752');
```

> 指派是幂等的：已归属给同一账号时返回 `true`；已归属给**他人**时抛
> '活动已有创建者，无法认领'。

### 日常：发布活动主图

主图分两处存放，**分工明确**：

| 位置 | 作用域 | 谁写 | 谁读 | 作用 |
|---|---|---|---|---|
| `shared/_application/activities/<slug>.png` | 应用归属（`admin_only` 写） | WorkBuddy 管理页 | 登录用户 | **唯一真相源**，客户端按 `cover_path` 签发 |
| `assets/covers/<slug>.png` | 小程序包内 | 随包分发 | 所有人 | 匿名访客的兜底展示（私有桶无公开读通道） |

#### 第 1 步：在管理页上传主图字节

`shared/_application/` 是**应用归属作用域**，平台侧明确限定为「仅管理员可写」：
存储 RLS `workbuddy_runtime_objects_insert` 的 `with_check` 要求
`owner_id = auth.uid()` 且路径第 2 段等于 `auth.uid()`，端用户会话写不进去
（实测四种写入形态一律 `403 STORAGE_ACCESS_DENIED`）；MCP 的 `genie-baas` 存储端点只读，
CLI 无管理面。唯一写入通道是 WorkBuddy 桌面端：

> 设置 → 数据管理 → 应用 → 目标应用 → **文件存储** → `shared/_application` →
> 新建文件夹 `activities` → 进入后「上传文件」→ 选中
> `apps/jieban-zhilv-mp/assets/covers/` 下的
> `dawn-trek.png` / `night-market.png` / `island-week.png`
>
> **文件名必须等于 slug**——本地素材已按此命名，直接上传即可，无需重命名。

#### 第 2 步：绑定并自检

```bash
# 1. 准备凭据（运营账号的邮箱与密码；密码只经环境变量传入，不落盘到仓库）
export JBZL_EMAIL='<运营账号邮箱>'
export JBZL_PASSWORD='<运营账号密码>'

# 2. 绑定并自检（幂等，可重复运行）
node scripts/tools/sync-activity-covers.cjs

# 3. 核对结果：cover_path 应全部落在 shared/_application/activities/ 下
#    select id, slug, cover_path, published from public.activities order by id;
```

脚本依次执行：用运营账号建立会话 → 调 `sync_activity_cover` 绑定 `cover_path`
（目标路径由服务端拼出，脚本不传路径）→ 生成签名 URL 并拉取字节，
与本地 `assets/covers/<slug>.png` 逐字节比对（HTTP 200、`content-type` 为 `image/png`）。

#### 迁移旧对象（一次性）

主图早期放在 `shared/<运营账号 uid>/activities/` 下，那条路径内嵌 owner uid。
迁移完成后可删除：

```bash
node scripts/tools/sync-activity-covers.cjs --cleanup
```

> **为什么脚本不调用 `claim_activity`**：该函数仅 `service_role` 可执行，
> 而脚本用的是运营账号的 `authenticated` 会话，调用必然 42501。
> 归属在「一次性」步骤里由管理侧指派好之后，脚本只需 `sync_activity_cover`。

> **为什么上传不在脚本里**：`shared/_application/` 的写入权仅管理员，
> 这是平台对「应用归属作用域」的设计约束（MCP 只读、无 CLI），
> 不是脚本能绕开的限制；同理 `claim_activity` 脚本也调不了。

> **鉴权边界**：真正的访问控制是**会话**——数据面网关要求请求携带有效 Bearer 令牌，
> 否则返回 `401 invalid_grant`。`Origin` 头只用于区分浏览器跨站请求的来源白名单，
> **不是访问控制**（实测缺 `Origin` 时网关放行，只有 Origin 存在且不在白名单内才 403）。
> 脚本仍显式带上 `Origin: https://servicewechat.com`（小程序来源），
> 以便服务端按小程序通道处理，而不是依赖「缺省会放行」这一宽松行为。

> 脚本查询 `activities` 时**不包含 `owner_id`**：该列已改为列级授权，
> 不授予 `anon` / `authenticated`，查询它会直接 42501。

### 客户端为什么不用 SDK 的 `storage.upload`

SDK 的小程序端 fetch 只接受**字符串** body，传 `ArrayBuffer` 会直接抛
「暂不支持非字符串 body（ArrayBuffer/FormData 待补）」；而 `wx.request` 的 `data`
本身支持 `ArrayBuffer`。因此客户端上传走「SDK 签名 + `wx.request` 直传」：

1. `cloud.storage.createSignedUploadUrl(path, { upsert: true })` 取预签名上传 URL
   （鉴权与路径规则全在 SDK 内，客户端不硬编码云端路径）；
2. `wx.request` 以 `PUT` 把字节送到该预签名 URL。

读取侧则直接用 SDK 的 `createSignedUrl`（返回字段是 `signedUrl`）。

**覆盖写**：客户端不依赖 upsert 语义，改用「撞名先删后传」——
预签名 `PUT` 对已存在对象会返回 `409 STORAGE_KEY_ALREADY_EXISTS`，
而 `createSignedUploadUrl` 只把 `x-upsert` 头烧进**签发请求**，未必作用于最终 PUT。
因此 `utils/storage.js` 在收到 409 时删除同名对象并重试一次。
（报名配图路径含报名记录 id，正常流程不会撞名；这条兜的是「同一条报名换图重传」。）

## 验收

```bash
node tests/format.test.js     # 32 项纯函数单测
node tests/structure.test.js  # 46 项静态契约检查
```

`structure.test.js` 覆盖：项目结构与打包配置、app.json 四页登记、组件懒加载、
tabBar 图标存在性、云客户端只传 publicConfig 的 endpoint/publishableKey、
诊断适配器未二次包装、客户端不传也不读 `owner_id`、无 `/.cloud/` 直连、
报名走 `submit_signup`、取消走 `cancel_registration` 且客户端不直接改表、
人数口径 `sum(companions)` 且不得出现 `count(*)`、服务端函数含登录态/字段/活动状态校验、
表级只读 + 部分唯一索引（含 `WHERE status='confirmed'`）存在、
`activities` 采用列级授权且 `owner_id` 不在其中、客户端字段白名单与列级授权逐列对齐、
主图绑定函数的归属校验存在、归属建立仅 `service_role`、旧签名 `claim_activity(BIGINT)` 已 DROP、
运营脚本与云端权限模型一致（不调 `claim_activity`、不 select `owner_id`、凭据走环境变量）、
页面用 `this.data.activityId` 而非 `this.activityId`、
配图走 `userPath` 且限制大小类型、服务端配图路径按分段限定本人目录且不把 uid 拼进正则、
records 用 `allSettled`、`ensureSession` 存在、首页开启下拉刷新、
错误文案不直出原始错误、`schema.sql` 与分文件脚本同源。

## 说明

- 报名手机号为用户自填内容，存储于云端数据库，仅本人可读。
- 活动主图存放于发布者本人的 `shared/<uid>/activities/` 作用域（运营脚本写入），
  登录用户可读；主图未就绪时页面回落到内置 PNG 降级图。
- 报名配图存放于本人私有 `users/<uid>/registrations/` 作用域，仅本人可读。
- 报名人数统计加载失败时，页面显示「人数待刷新」而不是「0 人已报名」，
  避免把「读不到」误报成「还有名额」。
