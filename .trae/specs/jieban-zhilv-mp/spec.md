---
title: "结伴之旅 · 活动报名微信小程序（jieban-zhilv-mp）"
status: "completed"
methodology: "seven-concepts (F→V→I→C)"
spec_mode: "Review"
---

# 结伴之旅 · 活动报名微信小程序 - 产品需求文档

> 方法论链路：七概念场景 5（创新突破）F → V → I → C。本 spec 为 F（第一性原理）与 V（五攻击者对抗审查）的产出固化。
> 用户关键决策（2026-10-26 确认）：①活动名称 =【结伴之旅】；②面向人群 =【全人类】；③必须 4 个页面；④微信授权登录；⑤活动与报名数据走云端数据库；⑥活动图片走云端存储；⑦简洁移动端设计、统一风格图标、**不使用 Emoji**。

## Overview

- **Summary**：一个微信小程序，面向全人类提供活动报名闭环——浏览活动、看详情、在线报名、查自己的报名记录。活动与报名数据存于云端 PostgreSQL（PostgREST 兼容），活动主图与报名配图存于云端对象存储。
- **Purpose**：把「活动发布 → 看到 → 报名 → 确认/取消」这条链路做成**无需下载额外 App、打开即用**的形态，并让报名数据天然带账号归属（微信授权登录后写入 uid），无需另建账号体系。
- **Target Users**：全体微信用户（活动发布方为运营账号，通过同一套云端能力运维主图）。

## Goals

- G1：四页闭环。活动首页（列表）→ 活动详情 → 在线报名 → 报名记录，双向可达。
- G2：微信授权登录作为唯一身份来源，报名归属自动绑定 uid，客户端不传归属字段。
- G3：活动与报名数据落云端数据库；主图与报名配图落云端存储。
- G4：名额口径全局统一为「人数」（含本人），客户端展示、服务端校验、统计函数三处同源。
- G5：并发安全。同一活动的报名写入在服务端原子完成，不依赖客户端顺序。
- G6：可运维。运营账号可自助发布主图并绑定，无需改动云端授权。
- G7：安全面收敛。写权限全部收敛到服务端函数；用户标识不外泄；令牌不落盘。

## Non-Goals

- 不做活动管理后台（运营动作通过脚本 + 管理侧 SQL 完成）。
- 不做支付、发票、分销、评价体系。
- 不做多语言与国际化（单语言中文）。
- 不做实时推送（无订阅消息）。
- 不做图片审核流水线。
- 不做服务端渲染与 SEO（小程序无此概念）。
- 不引入第三方 UI 框架（原生组件 + 自绘图标）。

## Background & Context

- **F 阶段公理体系**（设计的不可再分前提）：
  - A1：身份唯一来源 = 微信授权登录后的服务端会话 uid。客户端**不得**自报身份。
  - A2：所有业务写入必须经服务端函数完成；客户端对业务表只有读权限。
  - A3：名额的真实口径 = `sum(companions)`（含本人），不是报名行数。
  - A4：报名归属判定完全在服务端；客户端既不传也不读归属字段。
  - A5：用户标识（uid，含 openid 片段）属于个人敏感信息，不得下发给无关访问者。
  - A6：对象存储的作用域决定可见性：`users/<uid>/` 属主可写；`shared/<uid>/` 属主可写、他人可读；`shared/_application/` 仅管理侧可写。
  - A7：数据面网关的访问边界是**有效会话**；`Origin` 只用于区分浏览器跨站请求，不是访问控制。
- **F 阶段假设剥离**（被证伪剥离的经验假设）：必须自建账号密码体系（微信授权已足够）；主图必须公网可访问（签名 URL 即可）；报名行数即人数（同行人数场景下不成立）；SDK 的 `storage.upload` 在小程序端能传二进制（实测只接受字符串 body）。
- **V 阶段对抗审查结论**（已在设计中兑现）：

  | 攻击者 | 攻击路径 | 防御设计 |
  |---|---|---|
  | 🔴 安全 | 访客直查 `activities.owner_id` 拿到创建者微信 uid（含 openid） | `activities` 改**列级授权**，`owner_id` 不授予 anon/authenticated；客户端字段白名单同步对齐 |
  | 🔴 安全 | 任意登录用户「先到先得」认领活动、抢占主图绑定权 | 归属建立 `claim_activity` 仅 service_role 且须显式给出归属 uid；客户端对 `activities` 无 UPDATE |
  | 🔴 安全 | 客户端构造路径参数，把配图写进他人目录 | 服务端按 `/` 结构化分段等值比较，**不把 uid 拼进正则模式**（uid 含 `.` 会放宽校验） |
  | 🔴 安全 | 令牌明文落 wx storage | 本地会话快照按字段白名单裁剪，`accessToken`/`refreshToken` 不落盘 |
  | 🟠 完整性 | 并发报名超卖 | 服务端 `submit_signup` 内 `FOR UPDATE` 行锁 + 人数口径校验；部分唯一索引兜底重复报名 |
  | 🟠 完整性 | 人数统计读失败被静默显示成「0 人已报名」，误导用户以为还有名额 | 统计失败改为抛错，页面显示「人数待刷新」；人数未知时不言「已满」 |
  | 🟠 完整性 | 报名配图上传失败被静默吞掉，用户以为配图已提交 | 区分「报名成功」与「报名成功，配图未上传」两种提示 |
  | 🟠 完整性 | `activities` 删除连带抹掉用户报名记录 | 外键 `ON DELETE RESTRICT` |
  | 🟢 边界 | 同行人数越界（0 / 负数 / 超上限） | 服务端 CHECK 约束 + 函数内校验 + 客户端 `canFit` 预判 |
  | 🟢 边界 | `slug` 含正则元字符时拼进模式放宽路径校验 | 全部路径校验去正则化：分段等值比较 + 捕获组取值后等值比较 |
  | 🟡 模糊 | 未知活动 slug / 已下架活动 | 详情页返回 null 并提示「活动不存在或已下架」；列表只展示 `published=true` |
  | 🟡 模糊 | 存储对象路径非法导致整个列表渲染失败 | 逐对象独立 try/catch，单张主图失败不影响其它项 |

## Functional Requirements

- FR-1 **活动首页**：品牌区 + 活动卡片列表（时间、地点、名额进度、费用、主图），支持下拉刷新，点击进入详情。
- FR-2 **活动详情**：主图、亮点、报名须知、名额进度，底部固定「立即报名」。
- FR-3 **在线报名**：同行人数（1–4）、手机号、称呼、备注、报名配图上传（存云端存储）；提交后给出明确结果提示。
- FR-4 **报名记录**：本人报名列表、状态、取消报名。
- FR-5 **微信授权登录**：`wx.login` → `cloud.auth.signInWithWechat(code, appid)`；`appid` 取运行时真实值，不硬编码试用/正式任一值。
- FR-6 **云端数据库**：活动表与报名表；报名写入、取消、绑图均走服务端函数。
- FR-7 **云端存储**：活动主图读签名 URL；报名配图走「SDK 签名 + `wx.request` 直传」写二进制。
- FR-8 **运营发布主图**：脚本用运营账号会话上传 PNG 到 `shared/<uid>/activities/` 并绑定 `cover_path`，带字节自检。

## Non-Functional Requirements

- NFR-1 **一致性**：人数口径在三处（客户端展示 / 服务端校验 / 统计函数）必须同源，均为 `sum(companions)`。
- NFR-2 **原子性**：报名写入的校验与插入必须在同一事务内完成（`SECURITY DEFINER` + 行锁）。
- NFR-3 **最小权限**：客户端对业务表只有读权限；函数 EXECUTE 按角色精确授予；`PUBLIC` 无任何 EXECUTE。
- NFR-4 **最小暴露**：用户标识不下发；令牌不落盘；后端原始错误不外泄。
- NFR-5 **可运维**：主图发布不依赖改动云端授权；流程有幂等性与字节自检。
- NFR-6 **可移植**：SDK 随应用 vendoring，免「构建 npm」步骤；`miniprogramRoot` 为 `./`。
- NFR-7 **无障碍与视觉**：统一线性风格图标（22 个 PNG），**不使用 Emoji**；信息层级清晰、布局紧凑。

## Constraints

- 微信小程序原生框架：WXML 禁用可选链 / 空值合并 / 箭头函数，仅用原生标签；tabBar 2–5 项且图标文件真实存在。
- 云端 MCP 端点不支持多语句 → SQL 按「每次一条语句」拆分。
- `vendor/` 是根级第三方区域（git submodule，禁止本地修改）→ SDK 只能 vendoring 到应用内 `apps/<app>/vendor/`。
- `apps/` 内所有资产可直接修改；应用须登记进 `apps/AGENTS.md` 路由表与 `apps/README.md`。
- 仓库 Python 禁用 `from __future__ import annotations`（requires-python ≥3.14，PEP 649 已默认）。

## Assumptions

- 微信登录 uid 形态为 `wx:` + openid（依据 SDK 源码注释；**未真机实证**，属已知边界）。
- 云端存储 `shared/` 作用域不支持 upsert，覆盖写需先删后传。
- 运营账号使用 Email + 口令登录云端，其 uid 与 `auth.users.id` 一致。

## Acceptance Criteria

### AC-1：四页闭环与导航
- 首页列出已发布活动；点击进入详情；详情可跳报名；报名完成后可在报名记录看到。
- **Evidence**：`pages/` 四页齐备；`app.json` 登记 4 个页面；tabBar 两项图标文件存在。

### AC-2：微信授权登录
- 登录成功后取得服务端会话，后续写入以该会话身份落库。
- **Evidence**：`utils/auth.js` 调 `signInWithWechat(code, appid)`；`appid` 取自 `wx.getAccountInfoSync().miniProgram.appId`；无硬编码 appid。

### AC-3：云端数据库存储活动与报名
- 活动列表、详情、报名写入、报名记录均走云端数据库。
- **Evidence**：`utils/api.js` 全部经 `cloud.database`；报名写走 `submit_signup` RPC。

### AC-4：云端存储承载图片
- 主图读签名 URL；报名配图写入云端存储并回填路径。
- **Evidence**：`utils/storage.js` 用 `createSignedUrl` 读、`createSignedUploadUrl` + `wx.request` 写；客户端不硬编码云端路径。

### AC-5：人数口径统一
- 客户端展示、服务端校验、统计函数三处均为 `sum(companions)`。
- **Evidence**：`schema.sql` 中 `submit_signup` 聚合为 `sum(r.companions)`；`registration_stats` 同口径；`tests/format.test.js` 的 `canFit`/`quotaText` 用例覆盖；结构测试断言不得出现 `count(*)`。

### AC-6：并发安全与防重复报名
- 并发报名不超卖；同一用户对同一活动只有一条有效报名。
- **Evidence**：`submit_signup` 内 `FOR UPDATE` 行锁且 `FOR UPDATE` 早于 `sum(`；部分唯一索引 `(activity_id, owner_id) WHERE status='confirmed'`。

### AC-7：安全面收敛
- 客户端对业务表只读；`owner_id` 不在访客可见列；令牌不落盘；错误文案不外泄。
- **Evidence**：`activities` 列级授权（13 业务列，无 `owner_id`、无 `created_at`）；`utils/auth.js` 白名单裁剪；实测 `select=owner_id` 与 `select=*` 均 42501、业务列读 200。

### AC-8：归属不可被终端用户夺取
- 只有管理侧能指派归属；普通用户调主图绑定必被拒。
- **Evidence**：`claim_activity` 仅 service_role 且需显式 `p_owner_uid`；`claim_activity(BIGINT)` 旧签名已 DROP；终端用户侧的主图绑定通道 `claim_activity_cover` 已 DROP，改为 `sync_activity_cover`（路径由服务端拼出）。

### AC-9：可运维
- 运营账号能自助绑定主图并完成字节自检，流程幂等；字节入库走平台唯一的管理面通道。
- **Evidence**：`scripts/tools/sync-activity-covers.cjs` 调 `sync_activity_cover` 绑定后拉取字节，
  要求 HTTP 200 + `content-type: image/png` + 与 `assets/covers/<slug>.png` 逐字节一致；
  上传通道为 WorkBuddy 管理页（`_application` 作用域仅管理员可写，已实测端用户会话 403）。

### AC-10：不因可读性牺牲正确性
- 人数读失败显示「人数待刷新」而非「0 人已报名」；人数未知时不判定「已满」。
- **Evidence**：`getRegistrationStats()` 抛错；首页/详情/报名页三处 `quotaKnown=false` 分支。

### AC-11：仓库规范符合性
- 应用登记进 `apps/` 路由表；spec 三件套齐备；SDK vendoring 在应用内。
- **Evidence**：`apps/AGENTS.md` 与 `apps/README.md` 路由表含 `jieban-zhilv-mp`；`.trae/specs/jieban-zhilv-mp/` 三件套（无 checklist.md）。

### AC-12：界面品质
- 统一线性图标、无 Emoji、信息层级清晰、布局紧凑。
- **Evidence**：`tests/structure.test.js` 断言源码不含 Emoji、WXML 仅用原生标签、本地资源全部存在；22 个图标 PNG 统一风格。

### AC-13：主图路径取值域不含用户标识
- 公开可读的 `activities.cover_path` 不得内嵌任何用户标识；其取值域由**服务端**锁死为
  `shared/_application/activities/<slug>.png`，调用方无法指定路径。
- **Evidence**：`sync_activity_cover` 函数体内拼出目标路径、不接受路径参数、
  只返回路径字符串；`set_activity_cover` 只接受 `_application` 前缀且返回类型为 `TEXT`
  （不再返回含 `owner_id` 的整行）；旧通道 `claim_activity_cover` 已 `REVOKE` + `DROP`；
  云端 `pg_proc.proacl` 复核确认 `set_activity_cover` 不含 anon/authenticated。

### AC-14：新增活动不需改代码即可正确展示
- 新增活动只要把 `<slug>.png` 放进 `assets/covers/`，匿名访客即可看到该活动主图
  （私有桶无公开读通道，随包副本是匿名用户唯一来源），无需改映射表或补代码分支。
- **Evidence**：`utils/format.js` 的 `fallbackCover` 按 slug 规则推导路径并做形状校验
  （拒绝路径穿越、不查对象原型）；首页与详情页 `<image>` 有 `binderror` 降级到
  `default.png`；本地素材与云端路径同名规则。

### AC-15：运营脚本与云端权限模型一致
- 脚本只用 `authenticated` 会话能调的函数，不上传写入仅管理员可写的作用域，
  凭据走环境变量且令牌不进日志。
- **Evidence**：`scripts/tools/sync-activity-covers.cjs` 调 `sync_activity_cover`、
  不调 `claim_activity` / `claim_activity_cover`、不传路径、不调 `storage.upload`；
  结构测试「运营脚本与云端权限模型一致」全绿。

## Open Questions

- 微信登录 uid 的真实形态（`wx:` + openid）尚未真机实证——待真机验证后固化为契约测试（见 review.md 的遗留边界）。
- 报名配图的大小上限目前在客户端与文件系统层约束，服务端只校验路径形状；若未来放开客户端上传入口，需同步补服务端体积校验。
- **活动主图字节迁移待人工一步**：`_application` 是应用归属作用域，存储 RLS 只允许管理员写，
  端用户会话（含脚本）一律 `403 STORAGE_ACCESS_DENIED`，MCP 存储端点只读且无 CLI，
  唯一写入通道是 WorkBuddy 管理页。迁移按「先传字节 → 再切路径 → 再删旧对象」排序，
  中间态不影响小程序可用性。


### AC-16：隐私声明面与代码调用面一致
- 代码调用的隐私接口所映射的「处理的信息」类型，必须在《用户隐私保护指引》中逐项声明；
  隐私接口调用点必须先过授权兜底（`requirePrivacyAuthorize`）再发起调用。
- 声明侧（平台后台表单）与兜底侧（代码授权钩子）是两条独立链路，缺任一侧都会导致功能失败，
  因此两侧必须同批修改并各自留可回归断言。
- **Evidence**：`utils/privacy.js` 导出授权三接口；`app.js` 的 `onLaunch` 注册
  `privacy.registerPrivacyAuthorization()`；`pages/signup/signup.js` 中
  `await this.ensurePrivacyAuthorized()`（第 193 行）早于 `wx.chooseMedia`（第 199 行）；
  `docs/privacy-declaration.md` 含官方 8 板块与「信息类型 ↔ 代码位置」对照表；
  `tests/structure.test.js`「隐私合规面」4 条断言（含顺序断言）全绿，测试总数 50/50；
  `.agents/skills/platform-review-precheck/scripts/check_declaration_alignment.py`
  对本项目判定 FAIL=0。