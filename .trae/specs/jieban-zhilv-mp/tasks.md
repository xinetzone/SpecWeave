# 结伴之旅 · 活动报名微信小程序（jieban-zhilv-mp）- 实施计划

> 任务为依赖有序的垂直切片；每个 Task 至少含一条 TR。开发根：`apps/jieban-zhilv-mp/`。
> 本轮（对抗审查后）追加的任务以 **Task 8–12** 标记，均来自 V 门审查的采纳项。

## Task 1: 应用骨架、四页结构与设计令牌
- **Status**: `completed`
- **Completion Evidence**:
  - TR-1.1：`app.json` 登记 4 个页面 + tabBar 2 项，图标文件真实存在；`structure.test.js` 断言通过。
  - TR-1.2：22 个统一线性风格 PNG 图标 + 4 张主图由 `scripts/generate_assets.py` 生成；断言源码不含 Emoji。
  - TR-1.3：`project.config.json` 的 `miniprogramRoot` 为 `./`，`lazyCodeLoading: requiredComponents`，`tests` 已排除打包。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - `app.js` / `app.json` / `app.wxss`：全局逻辑、会话恢复（`ensureSession`）、设计令牌。
  - `pages/index|detail|signup|records/`：四页各自 `.js/.json/.wxml/.wxss`。
  - `assets/icons/`、`assets/covers/`：线性描边 + 扁平色块，栅格 64px（Tab 图标 81px），主色 `#2f2733`/`#2f6bff`。
  - `sitemap.json`、`package.json`。
- **Acceptance Criteria Addressed**: AC-1、AC-12
- **Test Requirements**:
  - `rule` TR-1.1: 四页登记完整、tabBar 图标存在、组件懒加载开启。
  - `rule` TR-1.2: 源码不含 Emoji；WXML 仅用小程序原生标签且无 `?.`/`??`/箭头函数；引用的本地资源全部存在。

## Task 2: 云端数据层与人数口径
- **Status**: `completed`
- **Completion Evidence**:
  - TR-2.1：`scripts/db/schema.sql` 为单一真相源；`submit_signup` 内 `FOR UPDATE` 行锁且早于 `sum(`；聚合结果 `::BIGINT`。
  - TR-2.2：`registration_stats()` 过滤 `published = TRUE`；结构测试断言通过。
  - TR-2.3：部分唯一索引 `(activity_id, owner_id) WHERE status='confirmed'`；`ON DELETE RESTRICT` 防静默抹除报名。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 两表 + CHECK 约束 + 部分唯一索引 + RLS 读策略（已发布全员可读 / 已下架仅归属人可见）。
  - 人数口径统一为 `sum(companions)`；`capacity <= 0` 表示不限名额。
- **Acceptance Criteria Addressed**: AC-3、AC-5、AC-6
- **Test Requirements**:
  - `rule` TR-2.1: 断言 `schema.sql` 中人数聚合为 `sum(` 且无 `count(*)`；行锁早于聚合。
  - `rule` TR-2.2: 统计函数含 `published = TRUE` 过滤。
  - `rule` TR-2.3: 部分唯一索引含 `WHERE status='confirmed'`；外键为 RESTRICT。

## Task 3: 客户端 SDK 接入与登录
- **Status**: `completed`
- **Completion Evidence**:
  - TR-3.1：SDK vendoring 到 `vendor/workbuddy-cloud-sdk/miniprogram.js`（零外部依赖的自包含 CommonJS bundle），`utils/cloud.js` 直接 require；免「构建 npm」。
  - TR-3.2：`utils/auth.js` 调 `signInWithWechat(code, appid)`，`appid` 取运行时真实值。
  - TR-3.3：诊断适配器透传 `getRandomValues` / `getAccountInfoSync` / `navigateToMiniProgram`（条件透传以保留 SDK 能力探测语义）；初始化日志包整体 try/catch。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `utils/cloud.js`：唯一 SDK 初始化点，只传 endpoint + publishableKey。
  - `utils/workbuddy-cloud-diagnostics.js`：请求诊断适配器。
  - `utils/auth.js`：会话恢复、微信授权登录、退出。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-3.1: 云客户端只传 publicConfig 的 endpoint/publishableKey；诊断适配器未二次包装。
  - `rule` TR-3.2: 微信登录使用运行时 appid，不硬编码。
  - `rule` TR-3.3: 适配器顶层异常不抛出（否则整条 require 链断裂 → 全站白屏）。

## Task 4: 云端存储读写与配图上传
- **Status**: `completed`
- **Completion Evidence**:
  - TR-4.1：`utils/storage.js` 用 `createSignedUrl` 读（返回字段是 `signedUrl`，不是 `url`）；用 `createSignedUploadUrl` + `wx.request` 直传写。
  - TR-4.2：客户端不硬编码云端路径（结构测试扫描 `/.cloud/` 直连，断言通过）。
  - TR-4.3：配图路径走 `cloud.storage.userPath(uid, ...)`，不手拼 `users/${uid}`。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 绕过 SDK 小程序端 fetch 的 string-body 限制（SDK 的 `createMiniProgramFetch` 传 ArrayBuffer 直接抛「暂不支持非字符串 body」）。
  - `createSignedUrl` 对非法路径同步抛 `CloudStoragePathError` → 逐对象独立 try/catch。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-4.1: 数据层不出现 `/.cloud/` 直连（`vendor/` 与 `.temp/` 排除）。
  - `rule` TR-4.2: 配图使用 `userPath` 且限制大小与类型。

## Task 5: 四页业务实现
- **Status**: `completed`
- **Completion Evidence**:
  - TR-5.1：`utils/format.js` 提供 `quotaText` / `percent` / `isFull` / `canFit` / `formatCountdown` 等纯函数；`format.test.js` 30 项全绿。
  - TR-5.2：首页 `Promise.allSettled` 隔离列表与人数；详情页底部固定报名按钮；报名页含同行人数/手机号/称呼/备注/配图；记录页可取消报名。
  - TR-5.3：提交按钮接上 `fits`（此前计算了却未用），名额不足时文案为「名额不足」。
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 纯函数层与展示层分离，便于单测。
  - 倒计时：今天同一时刻已过点仍显示「今天开始」。
- **Acceptance Criteria Addressed**: AC-1、AC-5、AC-10
- **Test Requirements**:
  - `rule` TR-5.1: `canFit` 七项边界（恰好装下 / 装不下 / 单人 / capacity<=0 / 并发超写 / 缺省兜底 / 与 `isFull` 不矛盾）。
  - `rule` TR-5.2: `fallbackCover` 原型污染回归（`constructor` / `toString` / `__proto__` / `hasOwnProperty` 均返回兜底图）。

## Task 6: 云端函数与权限矩阵
- **Status**: `completed`
- **Completion Evidence**:
  - TR-6.1：七个服务端函数落 `scripts/db/`，并按「每次一条语句」拆分（云端 MCP 不支持多语句）；`schema.sql` 与分文件脚本同源（结构测试断言）。
  - TR-6.2：函数 EXECUTE 权限矩阵：报名三函数 → authenticated；`registration_stats` → anon + authenticated；归属建立与 `set_activity_cover` → 仅 service_role；`PUBLIC` 无任何 EXECUTE。
  - TR-6.3：路径校验全部去正则化（按 `/` 分段等值比较），并断言 schema 中不出现 uid 拼正则的写法。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `submit_signup` / `cancel_registration` / `attach_registration_cover` / `registration_stats` / `claim_activity` / `claim_activity_cover` / `set_activity_cover`。
  - 已关闭的历史入口 `signup` 保留但不授予任何角色（阻止旧客户端绕过校验）。
- **Acceptance Criteria Addressed**: AC-3、AC-6、AC-7、AC-8
- **Test Requirements**:
  - `rule` TR-6.1: 每个 `fn_*.sql` 的函数名在 `schema.sql` 中有同名定义。
  - `rule` TR-6.2: 权限矩阵断言逐函数匹配 `REVOKE FROM PUBLIC` + 定向 `REVOKE` + 精确 `GRANT`。
  - `rule` TR-6.3: 断言不出现 `^users/' || v_uid` 这类拼接写法；改为断言结构化分段比较。

## Task 7: 运营脚本与 README
- **Status**: `completed`
- **Completion Evidence**:
  - TR-7.1：`scripts/tools/publish-activity-covers.cjs` 走 Email 登录会话；凭据必须由 `JBZL_EMAIL`/`JBZL_PASSWORD` 提供、无默认值；不打印令牌。
  - TR-7.2：README 覆盖功能、技术栈、权限矩阵、安全模型、目录结构、运营步骤、验收命令。
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 上传 → 绑定 → 签名 URL 自检（HTTP 200 + `image/png` + 字节一致）。
  - `shared/` 不支持 upsert，覆盖写先删后传。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-7.1: 脚本不硬编码邮箱；凭据来自环境变量；不打印 `accessToken`。

## Task 8: 修「认领通道」越权与运维断链（V 门 P1-1，追加）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-8.1：**架构性整改**——归属建立 `claim_activity` 改为管理侧**显式指派**（新增 `p_owner_uid` 参数，仅 service_role），彻底消除「谁先登录谁就是创建者」；旧签名 `claim_activity(BIGINT)` 已 DROP（云端与磁盘同步）。
  - TR-8.2：主图绑定 `claim_activity_cover` 授予 authenticated——安全依据是**函数体内的双重归属校验**（路径 owner 段 == `auth.uid()` 且 `activities.owner_id` == `auth.uid()`），而归属建立仅 service_role 可执行，终端用户无法成为任意活动归属人。
  - TR-8.3：客户端认领入口**全部移除**：`utils/api.js` 去掉 `claimActivity`/`claimActivityCover` 与 `owner_id`；`pages/detail/` 删除 4322 字符的认领/上传逻辑及对应 WXML/WXSS 入口。
  - TR-8.4：**自查发现并修复了一处自己引入的回归**——把 `claim_activity` 收归 service_role 后，其函数体 `v_uid := auth.uid()` 在该角色下为 NULL（必抛「请先完成微信授权登录」），叠加运营脚本用 authenticated 会话调用 → 运维链路实际断裂。改法：归属建立走显式参数 + 绑定函数开放给归属人本人。
  - TR-8.5：云端 `information_schema.routine_privileges` 复核：`claim_activity` 仅 service_role、`claim_activity_cover` 为 authenticated+service_role、`PUBLIC`/`anon` 均无 EXECUTE。
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 问题：`claim_activity` 原语义是「owner_id IS NULL 时首个登录用户认领」，对终端用户开放 EXECUTE 等于把归属判定降级为客户端时序。
  - 修法：归属判定收回管理侧，且必须显式给出归属 uid；终端用户侧的「绑定主图」保留但依赖服务端归属校验。
- **Acceptance Criteria Addressed**: AC-8、AC-9
- **Test Requirements**:
  - `rule` TR-8.1: `claim_activity` 授予 service_role + 显式收回 anon/authenticated + 旧签名被 DROP。
  - `rule` TR-8.2: `claim_activity_cover` 授予 authenticated，且断言其函数体内含 `owner_id == auth.uid()` 校验。
  - `rule` TR-8.3: 客户端源码不含 `claim` 相关调用；运营脚本不调 `claim_activity`。

## Task 9: 修 `owner_id` 泄露（V 门 P2-3，追加）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-9.1：**自查发现客户端层修复不彻底**——原修复只让客户端不读 `owner_id`，但表级 `GRANT SELECT` 仍让访客直接 `GET .../activities?select=owner_id` 绕过客户端。改为**列级授权**：撤销表级 SELECT，只逐列授予 14 个业务列。
  - TR-9.2：**云端实测**：业务列读 → 200 并返回真实数据；`select=owner_id` → 42501；`select=*` → 42501（`*` 展开到无权限列即整表失败）。
  - TR-9.3：**RLS 策略求值未被列级授权破坏**——插入 `published=false` 的探针活动后，匿名访问该 slug 返回空数组（非归属人读不到未下架活动），探针已删除。
  - TR-9.4：其它读路径实测无回归：`registration_stats` RPC 200、按 id 单查 200、`order=starts_at&limit` 200、`registrations` 匿名读返回空（RLS 正常）。
  - TR-9.5：客户端字段白名单 `ACTIVITY_FIELDS` 与服务端列级授权**逐列对齐**，并由结构测试双向断言（客户端列必须在授权名单内，且名单内不含 `owner_id`）。
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 微信 uid 形态为 `wx:` + openid，属个人敏感信息；授权面必须与客户端白名单同源。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-9.1: 断言 `REVOKE SELECT ON TABLE public.activities FROM anon, authenticated` 存在，且列级 GRANT 的列清单不含 `owner_id`。
  - `rule` TR-9.2: 客户端 `ACTIVITY_FIELDS` 每一列都在服务端列级授权名单内（防授权漂移）。

## Task 10: 修静默失败与错误反馈（V 门 P2-4 / P1-2 / P1-6，追加）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-10.1：`getRegistrationStats()` 由静默返回 `{}` 改为抛错；三页改为「人数待刷新」语义（`quotaKnown=false`），人数未知时不断言「已满」（详情页 `full:false`）。
  - TR-10.2：报名页提交按钮接上 `fits`，名额不足时禁用且文案为「名额不足」。
  - TR-10.3：配图上传失败不再静默——区分「报名成功」与「报名成功，配图未上传」两种提示（`coverUploadMessage`）。
  - TR-10.4：`utils/auth.js` 令牌明文落盘整改——缓存改为字段白名单（`id`/`name`/`avatarUrl`/`provider`），读取时裁剪历史脏数据。
  - TR-10.5：首页补 `priceNote` 映射；`fallbackCover` 原型污染修复（`hasOwnProperty.call` + `typeof` 守卫）。
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 原则：读不到 ≠ 0；上传失败必须让用户知道；凭证不落盘。
- **Acceptance Criteria Addressed**: AC-10、AC-7
- **Test Requirements**:
  - `rule` TR-10.1: 三页均存在「人数待刷新」分支。
  - `rule` TR-10.2: 结构测试断言 `fits` 被接入提交按钮的 `disabled` 与文案。
  - `rule` TR-10.3: 认证模块断言不缓存 `accessToken`/`refreshToken`。

## Task 11: 修 SDK 契约缺陷导致的白屏与取图失败（追加）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-11.1：**6 条 SDK 契约独立实证**（读 SDK 源码，不盲信审查报告），其中 3 条比审查报告更致命且审查员未捕获：
    1. `createSignedUrl` 返回 `{ signedUrl }` 而非 `{ url }` → 原实现 4 处封面/配图永远取不到；
    2. 小程序端 fetch 只接受 string body → `storage.upload(ArrayBuffer)` 100% 失败；
    3. 诊断适配器未透传 `getRandomValues` → SDK 登录路径必抛 `workbuddy sign-in requires wx.getRandomValues`；
    4. `createSignedUrl` 对非法路径**同步抛** → 一个坏路径会中断整个循环；
    5. `nodeModules:false` + `miniprogram_npm/` 缺失 + 依赖 `"dev"` 非法 semver → **全站白屏**；
    6. 诊断适配器顶层未保护 `getAccountInfoSync` → 全站白屏。
  - TR-11.2：SDK vendoring 解决白屏（零外部依赖的自包含 bundle）；`utils/storage.js` 用「SDK 签名 + `wx.request` 直传」绕开 string-body 限制且**不硬编码云端路径**；逐对象独立 try/catch。
  - TR-11.3：修复后实测 OAuth 路径 `error=null`。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 官方发布产物 vendoring 进 `apps/<app>/vendor/`（根级 `vendor/` 是 submodule，不可改）。
- **Acceptance Criteria Addressed**: AC-2、AC-4
- **Test Requirements**:
  - `rule` TR-11.1: 结构测试断言数据层无 `/.cloud/` 直连、诊断适配器顶层不抛错。

## Task 12: 修 `set_activity_cover` 的正则拼接（V 门 P2-11 同族，追加）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-12.1：`set_activity_cover` 原实现把 `p_slug` 拼进正则模式（`'^shared/_application/activities/' || p_slug || '\.(png|jpg|jpeg)$'`）——与已修复的 P2-11 同族缺陷：slug 含正则元字符时拼进模式会**放宽**校验。改为按 `/` 结构化分段等值比较 + 捕获组取出 slug 后等值比较。
  - TR-12.2：磁盘与云端同步（`CREATE OR REPLACE`）；`fn_set_activity_cover.sql` 与 `schema.sql` 保持同源。
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 该函数仅 service_role 可执行，风险等级低于客户端通道，但同族缺陷一并消除，避免留下「同类问题只修一半」的隐患。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-12.1: 结构测试断言 `schema.sql` 中不出现 uid/slug 拼进正则模式的写法。

## Task 13: 对抗审查回归与 spec 收口（追加）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-13.1：四份对抗审查报告（安全鉴权 / 数据完整性并发时序 / 边界模糊 / 存储通道）已收齐；采纳项远超 V 门要求的「至少 2 条」。
  - TR-13.2：回归测试全绿——`format.test.js` 32/32、`structure.test.js` 46/46。
  - TR-13.3：spec 三件套落 `.trae/specs/jieban-zhilv-mp/`（spec/tasks/review，无 checklist.md）。
  - TR-13.4：`apps/AGENTS.md` 与 `apps/README.md` 路由表已登记 `jieban-zhilv-mp`。- **Priority**: high
- **Depends On**: Task 8 ~ Task 12
- **Description**:
  - V 门流程：审查意见 ≥5 条且具体 → 采纳 ≥2 条并修正原产出 → 修复后回归对抗。
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rule` TR-13.1: 两套测试全绿；云端权限矩阵与磁盘 schema.sql 逐项对账一致。

## Task 14: 主图路径取值域根除（追加）
- **Status**: `completed`（字节迁移待人工一步，见 Task 18）
- **Completion Evidence**:
  - TR-14.1：云端新增 `sync_activity_cover(TEXT)`，函数体与磁盘 `fn_sync_activity_cover.sql`
    逐字节一致（`md5(prosrc)` = `eef21d37d7e55198df6749eb06c6eab3`，磁盘补尾换行后 MATCH）。
  - TR-14.2：`set_activity_cover` 返回类型由 `SETOF public.activities` 改为 `TEXT`，
    云端函数体 `md5(prosrc)` = `4e09cedf71ff116afd3a1f333ffb05fc`（磁盘补尾换行后 MATCH）。
  - TR-14.3：旧通道 `claim_activity_cover` 已 `REVOKE` + `DROP`；云端 `pg_proc` 复核
    确认该函数不存在。
  - TR-14.4：云端权限矩阵复核（`pg_proc.proacl`）：
    `sync_activity_cover` = authenticated + service_role + 管理员；
    `set_activity_cover` = service_role + 管理员（**无 anon / authenticated**）；
    `claim_activity` = service_role + 管理员；其余报名 RPC 维持原样。
  - TR-14.5：`activities` 列级授权收紧为 13 列（收回 `created_at`），
    `information_schema.column_privileges` 复核：anon/authenticated 无 `owner_id`、无 `created_at`。
  - TR-14.6：数据面 HTTP 实测：业务列 200；`select=owner_id` 401；
    `select=created_at` 401；`order=starts_at&limit` 200；`rpc/registration_stats` 200。
- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 主图是应用资产却被放进终端用户归属作用域，导致 `cover_path` 内嵌 uid。
  - 从**取值域**根除：目标路径只允许 `shared/_application/activities/<slug>.png`。
- **Acceptance Criteria Addressed**: AC-13
- **Test Requirements**:
  - `rule` TR-14.1: 结构测试断言「主图路径取值域被服务端锁死，不含用户标识」——
    canonical 通道不接受路径参数、管理侧通道只接受 `_application` 前缀、
    旧通道已 DROP 且分文件已删除。

## Task 15: 兜底主图规则化（追加）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-15.1：`utils/format.js` 的 `fallbackCover` 去掉硬编码映射表，改为
    `assets/covers/<slug>.png` 规则 + slug 形状校验；新增 `defaultCover()` / `isSafeSlug()`。
  - TR-15.2：首页与详情页 `<image>` 增加 `binderror`，加载失败降级 `default.png`。
  - TR-15.3：本地素材重命名为 `<slug>.png`（`dawn-trek.png` / `night-market.png` /
    `island-week.png` / `default.png`），`scripts/generate_assets.py` 同步；
    与云端路径规则同名 → 管理页上传无需重命名。
  - TR-15.4：回归用例覆盖规则命中、形状非法回落、原型链键返回字符串、路径穿越拒绝。
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 新增活动时匿名访客必须自动拿到正确主图，而不是永远落默认图。
- **Acceptance Criteria Addressed**: AC-14
- **Test Requirements**:
  - `rule` TR-15.1: `format.test.js` 断言 `fallbackCover` 不再查对象表，且形状校验拒绝 `../`。

## Task 16: 运营脚本改口径（追加）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-16.1：`scripts/tools/publish-activity-covers.cjs` 更名
    `scripts/tools/sync-activity-covers.cjs`，职责改为「绑定 + 自检 + 可选清理」。
  - TR-16.2：脚本不再上传字节（`_application` 作用域写权限仅管理员，走管理页），
    改为调 `sync_activity_cover` 绑定 → 签名拉取 → 与本地素材逐字节比对。
  - TR-16.3：新增 `--cleanup` 开关，删除历史遗留的 `shared/<uid>/activities/<slug>.png`。
  - TR-16.4：结构测试断言脚本「不调 `claim_activity` / `claim_activity_cover` /
    不传 `p_path` / 不调 `storage.upload` / 凭据走环境变量 / 不打印令牌」。
- **Priority**: medium
- **Depends On**: Task 14
- **Description**:
  - 上传通道受平台约束后，脚本职责与权限边界必须与云端授权模型保持一致。
- **Acceptance Criteria Addressed**: AC-15
- **Test Requirements**:
  - `rule` TR-16.1: 结构测试「运营脚本与云端权限模型一致」全绿。

## Task 17: 回归与文档同步（追加）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-17.1：`node tests/format.test.js` 32/32、`node tests/structure.test.js` 46/46 全绿。
  - TR-17.2：全部 `app.js` / `utils/*.js` / `pages/*/*.js` / `scripts/tools/*.cjs` /
    `tests/*.js` 通过 `node --check`。
  - TR-17.3：README 已同步函数表、权限矩阵、安全模型、目录结构、`scripts/db` 清单、
    素材命名规则、运营步骤（两段式）、验收项数。
  - TR-17.4：清理 worker 探针暂存目录 `.temp/`（凭据均来自环境变量，无明文口令）。
- **Priority**: medium
- **Depends On**: Task 14 ~ Task 16
- **Description**:
  - 文档与实现不同步 = 下一个维护者踩坑。
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rule` TR-17.1: 两套测试全绿；README 关键事实与 `schema.sql` 对账一致。

## Task 18: 主图字节迁移（追加 · 需人工一步）
- **Status**: `pending`
- **Completion Evidence**:
  - TR-18.1（待办）：在 WorkBuddy「设置 → 数据管理 → 应用 → 文件存储」中，
    进入 `shared/_application`，新建文件夹 `activities`，上传
    `assets/covers/` 下的 `dawn-trek.png` / `night-market.png` / `island-week.png`。
  - TR-18.2（待办）：执行 `node scripts/tools/sync-activity-covers.cjs`，
    预期 3/3「绑定成功 + HTTP 200 + content-type image/png + 字节完全一致」。
  - TR-18.3（待办）：`select id, slug, cover_path from public.activities order by id`
    复核 3 行 `cover_path` 均以 `shared/_application/activities/` 开头。
  - TR-18.4（待办）：执行 `node scripts/tools/sync-activity-covers.cjs --cleanup`
    删除历史遗留的 `shared/<uid>/activities/` 对象。
- **Priority**: high
- **Depends On**: Task 14
- **Description**:
  - `_application` 是应用归属作用域，存储 RLS 只允许管理员写，端用户会话
    （含脚本）一律 `403 STORAGE_ACCESS_DENIED`；MCP 存储端点只读、无 CLI。
  - 唯一写入通道是 WorkBuddy 管理页（S5 prepare → S6 PUT → S7 commit）。
  - 迁移按「先传字节 → 再切路径 → 最后删旧对象」排序，**全程零中断**：
  - TR-18.5：在字节迁移完成前，`cover_path` 仍指向旧的 `shared/<uid>/` 路径，
    小程序功能正常，不存在中间态不可用窗口。
- **Acceptance Criteria Addressed**: AC-13
- **Test Requirements**:
  - `rule` TR-18.1: 迁移后 `activities.cover_path` 全量落在规范作用域。

## Task 19: 隐私声明面整改（提审拦截防线 · 2026-10-26）
- **Status**: `completed`（代码与声明面已就绪；平台侧誊写另见 Task 20）
- **Completion Evidence**:
  - TR-19.1：`utils/privacy.js` 导出 `getPrivacySetting` / `requirePrivacyAuthorize` /
    `registerPrivacyAuthorization` 三个授权接口。
  - TR-19.2：`app.js` 的 `onLaunch` 首行调用 `privacy.registerPrivacyAuthorization()`。
  - TR-19.3：`pages/signup/signup.js` 中 `await this.ensurePrivacyAuthorized()`
    （第 193 行）早于 `wx.chooseMedia`（第 199 行）。
  - TR-19.4：`docs/privacy-declaration.md` 落盘，含官方 8 板块与「信息类型 ↔ 代码位置」对照表。
  - TR-19.5：`tests/structure.test.js` 新增「隐私合规面」4 条断言，总数 46 → 50，全绿。
- **Priority**: high
- **Depends On**: Task 15
- **Description**:
  - 微信平台审核逐项比对「本次提审版本的隐私接口调用情况」与
    「已填写的《用户隐私保护指引》所声明的信息类型」，缺任一项即拦截。
  - 本项目 `wx.chooseMedia` 命中「收集你选中的照片或视频信息」——
    与 2026-10-26 同类提审拦截的类型完全一致。
  - 声明侧（平台后台表单）与兜底侧（代码授权钩子）是**两条独立链路**：
    只声明则用户未同意时接口静默失败；只兜底则平台直接禁用接口。
  - 两侧必须同批修改，并各自留可回归断言（含**顺序**断言）。
- **Acceptance Criteria Addressed**: AC-16
- **Test Requirements**:
  - `rule` TR-19.6: `node tests/structure.test.js` → 50/50 通过。
  - `rule` TR-19.7: `.agents/skills/platform-review-precheck/scripts/check_declaration_alignment.py apps/jieban-zhilv-mp`
    → FAIL=0。

## Task 20: 平台侧隐私协议誊写与重新提审（需人工一步）
- **Status**: `pending`
- **Completion Evidence**:
  - TR-20.1（待办）：在 mp 后台「管理 → 版本管理 → 提交代码审核 → 信息填写页面」
    （**入口2**，非入口1）誊写 `docs/privacy-declaration.md` 的「开发者处理的信息」等章节。
  - TR-20.2（待办）：勾选扫描器输出的全部信息类型——
    至少含「收集你选中的照片或视频信息」「收集你的昵称、头像」「收集你的手机号」。
  - TR-20.3（待办）：填写联系方式与存储期限（平台不代填）。
  - TR-20.4（待办）：提审页面「用户隐私保护设置」勾选「采集用户隐私」。
  - TR-20.5（待办）：重新提交代码审核，确认通过。
- **Priority**: high
- **Depends On**: Task 19
- **Description**:
  - 仓库里存在协议草稿**不等于**平台已声明——两者是两份内容。
  - 官方明确：若提审版本被拦截，须在**入口2**更新；入口1 只作用于现网版本。
  - 用途描述须为具体动作，空话会被审核追问。
- **Acceptance Criteria Addressed**: AC-16
- **Test Requirements**:
  - `manual` TR-20.6: 提审结果为通过。

## Task 21: 模板化 + 真人发布活动（2026-10-26）

> 用户诉求：「当下的活动应该算作活动模板，真实的活动应该是由真人自己发布，请优化小程序」。
> 方法论链路：七概念场景 5（创新突破）F → V → I → C。

- **Status**: `completed`
- **Completion Evidence**:
  - TR-21.1：**模板表落地**——新建 `public.activity_templates`（slug/title/summary/cover_slug/
    highlights/notes/default_capacity/default_duration_minutes/published/sort_order），
    RLS 只放行 `published = TRUE`；客户端列级 SELECT 10 列（不含 published/created_at），无写权限。
  - TR-21.2：**存量迁移**——3 条运营预置活动（dawn-trek / night-market / island-week）
    迁入模板表并从 `activities` 删除；实测迁移后 `activities=0 / templates=3 / registrations=0`。
  - TR-21.3：**三个新 RPC**——`create_activity`（归属取 auth.uid()、slug 服务端生成、
    封面白名单、限流）、`update_activity`（归属校验、下架短路、已开始不可改期）、
    `my_activities`（服务端过滤、返回列不含 owner_id、不过滤 published）。
    权限：仅 `authenticated` + `service_role`，`PUBLIC`/`anon` 无 EXECUTE（`pg_proc.proacl` 复核）。
  - TR-21.4：**云端端到端实测**——以 `set_config('request.jwt.claim.sub', 'wx:testuser001', false)`
    构造登录态：发布返回 `id=11 / slug=act-fb0261dcbb084a53`，落库 `owner_id=wx:testuser001`；
    非法封面 → 22023；对象元素 → 22023；标题含换行 → 22023；他人编辑 → 42501；
    连建 11 次 → 停在 10 个；下架/重新上架 → true；`my_activities` 他人查返回 0 行。测试数据已清理。
  - TR-21.5：**客户端 6 页 4 tab**——新增 `pages/publish/publish`（选模板→填表→发布/编辑）
    与 `pages/mine/mine`（我的活动：下架/重新上架/编辑）；首页改双区块
    （「大家发起的活动」+「活动模板」）+ 发起入口；tabBar 扩为 4 项（活动/发起/我的活动/我的报名）。
  - TR-21.6：**封面改内置素材白名单**——新增 `cover_slug` 列与 6 张随包素材
    （dawn-trek / night-market / island-week / city-walk / co-reading / default）；
    保留 `cover_path` 承载平台侧已发布主图（取值域仍锁在 `_application`）。
  - TR-21.7：**V 门自查采纳项**——①JSONB 元素类型校验（`jsonb_array_elements_text`
    会把对象转文本从而绕过长度校验）；②控制字符校验（长度检查挡不住中间换行）；
    ③「已开始」判定必须用原值 `v_origin.starts_at`（用传入值可被绕过改期）；
    ④下架走短路（否则已结束活动永远无法下架）。
  - TR-21.8：**同步与回归**——`schema.sql` 与分文件同源；`claim_activity` 已废止并 DROP；
    `node tests/format.test.js` 46/46、`node tests/structure.test.js` 61/61 全绿。
- **Priority**: high
- **Depends On**: Task 20
- **Description**:
  - 翻转「活动由管理侧预置、归属由管理侧指派」的隐含假设，改为「活动由真人发布、归属即发布者」。
  - 模板与活动分表，避免「模板是否可报名」「模板有没有归属人」变成靠 published 猜的隐式约定。
- **Acceptance Criteria Addressed**: AC-17 ~ AC-21
- **Test Requirements**:
  - `rule` TR-21.9: `node tests/format.test.js` → 46/46；`node tests/structure.test.js` → 61/61。

## Task 22: 活动主图字节迁移（追加 · 需人工一步）

- **Status**: `pending`
- **Completion Evidence**:
  - TR-22.1（待办）：在 WorkBuddy「设置 → 数据管理 → 应用 → 文件存储」中，
    进入 `shared/_application`，新建文件夹 `activities`，上传
    `assets/covers/` 下的 `dawn-trek.png` / `night-market.png` / `island-week.png`。
  - TR-22.2（待办）：执行 `node scripts/tools/sync-activity-covers.cjs`，
    预期 3/3「绑定成功 + HTTP 200 + content-type image/png + 字节完全一致」。
- **Priority**: medium
- **Depends On**: Task 21
- **Description**:
  - 3 条运营活动已迁为模板，模板封面当前走随包素材；
  - 本任务只影响平台侧已发布主图的字节资产，不影响模板展示。
- **Acceptance Criteria Addressed**: AC-13
- **Test Requirements**:
  - `rule` TR-22.3: 迁移后 `activities.cover_path` 全量落在规范作用域。
