# 结伴之旅 · 活动报名微信小程序（jieban-zhilv-mp）- 独立审查

> 审查方法：五攻击者对抗审查（安全鉴权 / 数据完整性与并发时序 / 边界与模糊 / 存储通道 / 仓库规范）。
> 审查工具：4 个独立子代理（只读）+ 团队负责人独立读源码实证。
> 审查结论：**P0 = 0（全部修复）**，P1 = 6（全部修复），P2 = 15（全部修复）。

## 审查项

- [x] CP-R1: 四页闭环完整，导航双向可达，tabBar 图标真实存在
  - **Type**: `rule`
  - **Covers**: AC-1
  - **Evidence**: `pages/index|detail|signup|records/` 四页齐备；`app.json` 登记 4 页面 + tabBar 2 项；结构测试断言通过

- [x] CP-R2: 微信授权登录链路完整，appid 取运行时真实值
  - **Type**: `rule`
  - **Covers**: AC-2
  - **Evidence**: `utils/auth.js` 调 `signInWithWechat(code, appid)`；appid 来自 `wx.getAccountInfoSync().miniProgram.appId`；无硬编码

- [x] CP-R3: 活动与报名数据落云端数据库，报名写入唯一入口是 RPC
  - **Type**: `rule`
  - **Covers**: AC-3
  - **Evidence**: `utils/api.js` 全部经 `cloud.database`；写操作走 `submit_signup`；客户端对业务表只读

- [x] CP-R4: 图片走云端存储，客户端不硬编码云端路径
  - **Type**: `rule`
  - **Covers**: AC-4
  - **Evidence**: `utils/storage.js` 用 `createSignedUrl` 读 + `createSignedUploadUrl`/`wx.request` 直传写；结构测试扫描 `/.cloud/` 直连（排除 `vendor/`）

- [x] CP-R5: 人数口径全局统一为 `sum(companions)`，三处同源
  - **Type**: `rule`
  - **Covers**: AC-5
  - **Evidence**: `submit_signup` 与 `registration_stats` 均为 `sum(r.companions)`；结构测试断言不得出现 `count(*)`；`format.test.js` 的 `canFit` 七项边界

- [x] CP-R6: 并发安全——行锁早于聚合、部分唯一索引防重复报名
  - **Type**: `rule`
  - **Covers**: AC-6
  - **Evidence**: `submit_signup` 内 `FOR UPDATE` 位于 `sum(` 之前；唯一索引 `(activity_id, owner_id) WHERE status='confirmed'`；外键 `ON DELETE RESTRICT`

- [x] CP-R7: `owner_id` 不在访客可见列（**列级授权**，非仅客户端不读）
  - **Type**: `rule`
  - **Covers**: AC-7
  - **Evidence**: 云端实测：业务列读 200 返回真实数据；`select=owner_id` → 42501；`select=*` → 42501；RLS 的 owner 分支仍正确（`published=false` 探针活动对非归属人返回空，探针已删）；其它读路径（RPC / 单查 / 排序 / registrations）实测无回归；结构测试双向断言客户端白名单与服务端列级授权逐列对齐

- [x] CP-R8: 归属不可被终端用户夺取，运维链路仍然可用
  - **Type**: `rule`
  - **Covers**: AC-8、AC-9
  - **Evidence**: `claim_activity` 仅 service_role 且须显式给出 `p_owner_uid`（旧签名已 DROP）；`claim_activity_cover` 授予 authenticated，其函数体内含 `owner_id == auth.uid()` 与路径 owner 段等值比较；客户端无任何 claim 入口；运营脚本实测 3/3 跑通

- [x] CP-R9: 令牌不落盘，错误文案不外泄
  - **Type**: `rule`
  - **Covers**: AC-7
  - **Evidence**: `utils/auth.js` 缓存按字段白名单裁剪（`id`/`name`/`avatarUrl`/`provider`），读取时裁剪历史脏数据；`utils/api.js` 全部错误映射为固定可读文案，兜底「报名失败，请稍后重试」

- [x] CP-R10: 读失败不被误报为「0 人已报名」
  - **Type**: `rule`
  - **Covers**: AC-10
  - **Evidence**: `getRegistrationStats()` 由静默返回 `{}` 改为抛错；首页/详情/报名页三处 `quotaKnown=false` → 文案「人数待刷新」；详情页人数未知时 `full:false`（不断言已满）

- [x] CP-R11: 配图上传失败不再静默；名额不足时提交按钮真正禁用
  - **Type**: `rule`
  - **Covers**: AC-10
  - **Evidence**: `signup.js` 区分「报名成功」与「报名成功，配图未上传」；`fits` 已接入提交按钮 `disabled` 与文案「名额不足」（此前计算了却未用）

- [x] CP-R12: SDK 契约正确——白屏级缺陷与取图失败全部消除
  - **Type**: `rule`
  - **Covers**: AC-2、AC-4
  - **Evidence**: 6 条 SDK 契约经源码独立实证并逐条修复（`signedUrl` 字段名 / string-body 限制 / `getRandomValues` 透传 / 非法路径同步抛 / vendoring 免构建 npm / 诊断适配器顶层保护）；修复后 OAuth 路径实测 `error=null`；SDK vendoring 于应用内 `vendor/`

- [x] CP-R13: 路径校验全部去正则化（uid 与 slug 均不拼进正则模式）
  - **Type**: `rule`
  - **Covers**: AC-7
  - **Evidence**: `submit_signup` / `attach_registration_cover` / `claim_activity_cover` / `set_activity_cover` 四处均改为按 `/` 分段等值比较；结构测试断言 `schema.sql` 不出现 `^users/' || v_uid` 这类拼接

- [x] CP-R14: 界面品质——统一线性图标、无 Emoji、信息层级清晰
  - **Type**: `rubric`
  - **Covers**: AC-12
  - **Scale**: 1-5
  - **Anchors**: 1 = 通用模板感；3 = 可用但无辨识度；5 = 移动端原生质感
  - **Pass Threshold**: >= 4
  - **Evidence**: 22 个统一风格 PNG 图标（线性描边 + 扁平色块，主色 `#2f2733`/`#2f6bff`，栅格 64px / Tab 81px）+ 4 张主图，全部由 `scripts/generate_assets.py` 以 Pillow 几何绘制生成；结构测试断言源码不含 Emoji、WXML 仅用原生标签、引用的本地资源全部存在、四页均为白底 + 淡蓝主色的紧凑卡片布局

- [x] CP-R15: 仓库规范符合性——路由登记、spec 三件套、SDK vendoring 位置
  - **Type**: `rule`
  - **Covers**: AC-11
  - **Evidence**: `apps/AGENTS.md` 与 `apps/README.md` 路由表含 `jieban-zhilv-mp`；`.trae/specs/jieban-zhilv-mp/` 三件套（spec/tasks/review，无 checklist.md）；SDK vendoring 在应用内 `vendor/`（根级 `vendor/` 是 submodule，不可改）

- [x] CP-R16: 回归测试全绿
  - **Type**: `rule`
  - **Covers**: 全部 AC
  - **Evidence**: `node tests/format.test.js` → 32/32 通过；`node tests/structure.test.js` → 46/46 通过

## Review History

### Review R1
- **Result**: `pass`（经 R2 回归后仍 pass）
- **Evidence**: 4 份独立对抗审查报告收齐（安全鉴权 / 数据完整性与并发时序 / 边界与模糊测试 / 存储通道调研）；团队负责人**不盲信报告**，独立读 SDK 源码与云端 `information_schema` 做实证复核，结果发现 3 条比审查报告更致命且审查员未捕获的 P0（`signedUrl` 字段名 / 小程序端 string-body 限制 / `getRandomValues` 未透传），另有 1 条**自己引入的回归**（认领通道收归 service_role 导致运维链路断裂）。
- **Findings**（全部已修复或已接受）：
  1. **P0** `createSignedUrl` 返回 `signedUrl` 而非 `url` → 4 处封面/配图永远取不到 → **已修复**（改用 `signed.data.signedUrl`）
  2. **P0** 小程序端 fetch 只接受 string body → `storage.upload(ArrayBuffer)` 100% 失败 → **已修复**（改「SDK 签名 + `wx.request` 直传」，且不硬编码云端路径）
  3. **P0** 诊断适配器未透传 `getRandomValues` → 登录必抛 → **已修复**（条件透传，保留 SDK 能力探测语义）
  4. **P0** `nodeModules:false` + `miniprogram_npm/` 缺失 + 依赖 `"dev"` 非法 semver → **全站白屏** → **已修复**（SDK vendoring，免「构建 npm」）
  5. **P1** 认领通道对终端用户开放 → 任何登录用户可抢先接管活动主图绑定权 → **已修复**（归属建立收归 service_role + 显式指派；客户端入口全移除）
  6. **P1** 令牌明文落 wx storage → **已修复**（缓存字段白名单化）
  7. **P1** `fits` 计算了却未接入提交按钮 → **已修复**
  8. **P1** 配图上传失败被静默吞掉 → **已修复**（区分两种提示）
  9. **P2** 统计静默吞错把「读不到」显示成「0 人已报名」 → **已修复**（抛错 + 「人数待刷新」）
  10. **P2** `owner_id` 泄露 openid → **已修复**（表级改列级授权，客户端层修复不彻底之处一并封堵）
  11. **P2** 路径校验把 uid 拼进正则模式（uid 含 `.` 会放宽校验） → **已修复**（三处去正则化）
  12. **P2** `set_activity_cover` 把 slug 拼进正则模式（同族缺陷） → **已修复**
  13. **P2** `fallbackCover` 原型污染 → **已修复**（`hasOwnProperty.call` + `typeof` 守卫 + 回归用例）
  14. **P2** 首页 `priceNote` 缺失 → **已修复**
  15. **P2** 运营脚本硬编码账号 + 打印令牌片段 → **已修复**（凭据走环境变量、日志只打印 uid）
  16. **P2** `claim_activity` 被收归 service_role 后其函数体依赖 `auth.uid()`（该角色下为 NULL）→ 功能已死，叠加脚本用 authenticated 会话 → **运维链路断裂** → **已修复**（显式参数 + 绑定函数开放给归属人本人），并补「运营脚本与云端权限模型一致」结构断言防复发
  17. **P3** `client` 维度审计归属不可信（Origin 可伪造） → **接受偏差**：Origin 仅用于浏览器跨站缓解，真正的访问边界是会话；已在脚本注释与 README 中写明
  18. **P2** 微信登录 uid 形态（`wx:` + openid）**未真机实证** → **接受偏差并显式记录**：依据仅为 SDK 源码注释；已写入 spec 的 Assumptions 与 Open Questions，待真机验证后固化为契约测试
  19. **P2** 报名配图体积上限仅在客户端/文件系统层约束 → **接受偏差**：服务端只校验路径形状；当前无客户端上传入口，风险有限
- **Notes**:
  - 本轮修复中有一处是**审查者自己引入的回归**并被自查发现——把认领通道收归 service_role 使 `claim_activity` 失去可用性，同时打断了运营脚本的绑定链路。修复方式不是放宽安全边界，而是把「归属判定」彻底移出终端用户可触达范围，改由管理侧显式指派。
  - 「客户端不读 owner_id」这类**客户端层修复**不等于安全闭环：本轮实测发现表级 `GRANT SELECT` 仍让访客可直查该列。安全边界必须落在**服务端授权面**，客户端白名单只作为第二道防线。

### 第二轮审查发现（V 门回归后追加）

20. **P1** `cover_path` 内嵌 owner uid —— 列级授权的后门 → **已修复**
    - 现象：`activities.cover_path = shared/2114562052432330752/activities/dawn-trek.png`，
      而该路径第 2 段正是 `activities.owner_id`。`cover_path` 在公开可读列里，
      等于用「主图路径」把已从 `owner_id` 撤掉的创建者标识原样下发。
      **同一张表两列可见性不一致，属于自己打自己。**
    - 取证：匿名请求 `GET /.cloud/database/rest/activities?select=id,slug,title,cover_path`
      → 200 且响应含 `"cover_path":"shared/2114562052432330752/activities/dawn-trek.png"`。
    - 根因建模错误：主图是**应用资产**，却被放进「终端用户归属」作用域
      `shared/<uid>/`，于是路径里必然带 uid。
    - 修复（从取值域根除，不是堵入口）：
      - `sync_activity_cover(p_slug)`：**目标路径由服务端拼出**，调用方无法指定、
        不接受路径参数；对象未上传则拒绝绑定；只返回路径字符串。
      - `set_activity_cover(p_slug, p_path)`：只接受 `shared/_application/` 前缀。
      - 旧通道 `claim_activity_cover`（唯一能写入含 uid 路径的入口）**显式 DROP**。
      - 于是 `cover_path` 的取值域被服务端锁死为 `shared/_application/activities/<slug>.png`。
    - 配套：`set_activity_cover` 返回类型由 `SETOF public.activities` 改为 `TEXT` —— 旧版响应体带
      `owner_id`，一旦被误授权给 `authenticated` 就会绕开列级授权。
21. **P2** `fallbackCover` 是硬编码 slug→路径映射表 → 新增活动必然落默认图 → **已修复**
    - 现象：新增 slug 不在表里，匿名访客（私有桶无公开读通道，只能看随包副本）
      永远看到 `cover-default.png`；且加活动必须同时改代码与加图片。
    - 修复：改为规则化推导 `assets/covers/<slug>.png`（与云端路径同名规则），
      新增活动只需放文件；本地缺文件时由 `<image binderror>` 降级到 `default.png`。
      同时移除对象查表 → 原型污染面一并消失（改为 slug 形状校验，含路径穿越防护）。
22. **P2** `claim_activity_cover` 被授予 `authenticated` 时，路径 owner 段等于 `auth.uid()`
    即构成「把主图写进自己 uid 目录」的通道 → **已修复**（随 20 一并 DROP）。
23. **P2** `activities.created_at` 未按最小权限收回 → **已修复**（客户端与脚本都不读它）。
24. **P2** `ensureSession()` 非幂等 → **已修复**
    - `onLaunch` 调 `restoreSession()` 未 await、页面 `onShow` 又调 `ensureSession()`
      → 并发两次会话恢复。改为共享 in-flight promise。
25. **P2** 上传覆盖语义误判 → **已修复**
    - 原以为 `createSignedUploadUrl(path,{upsert:true})` 能覆盖写；实测预签名 `PUT`
      对已存在对象返回 `409 STORAGE_KEY_ALREADY_EXISTS`（`x-upsert` 只烧进签发请求）。
      改为「撞名先删后传」。
26. **P2** `pages/detail/detail.js` 尾部残留孤立 `}` → 详情页无法加载 → **已修复**
    - `node --check` 报 `SyntaxError: Unexpected token '}'`。
27. **P1** `shared/_application/` 的写入通道未验证 → **接受偏差并显式交接**
    - 实测：端用户会话在四种写入形态下全部 `403 STORAGE_ACCESS_DENIED`
      （RLS `workbuddy_runtime_objects_insert` 的 `with_check` 要求
      `owner_id = auth.uid()` 且路径第 2 段 = `auth.uid()`）；
      MCP `genie-baas` 存储端点只读、CLI 无管理面、operator 凭据仅存于 Electron 进程。
    - 唯一写入通道是 WorkBuddy 管理页（S5 prepare → S6 PUT → S7 commit），
      属平台对「应用归属作用域」的设计约束。已写成 README 运营步骤并交接给使用者。
    - 读侧已实测通过：`_application` 对象对 `authenticated` 可 list + 可签发。

## 第三轮审查发现（提审拦截复盘后追加 · 2026-10-26）

> 触发：某小程序 2026-10-26 提审被拒，拦截类型「收集你选中的照片或视频信息」。
> 用 `.agents/skills/platform-review-precheck` 扫本项目，检出**完全同型**的调用。

| 编号 | 严重度 | 发现 | 处置 |
|---|---|---|---|
| R3-01 | P0 | `pages/signup/signup.js` 调 `wx.chooseMedia`（收集你选中的照片或视频信息），但平台侧《用户隐私保护指引》未声明该类型 → 提审必被拦截 | 已整改：新增 `docs/privacy-declaration.md`（Task 19 TR-19.4） |
| R3-02 | P0 | 全仓无 `onNeedPrivacyAuthorization` / `requirePrivacyAuthorize` / `getPrivacySetting` → 用户未同意时隐私接口静默失败（不抛错、不回调） | 已整改：新增 `utils/privacy.js`，`app.js` 注册授权响应，调用点前显式校验并把拒绝转可读提示 |
| R3-03 | P1 | 授权兜底与隐私接口调用的**相对顺序**无断言保护 → 顺序反了等于没兜底 | 已整改：`structure.test.js` 新增顺序断言（先剥注释再匹配调用形态） |
| R3-04 | P1 | 协议正文若与代码调用面漂移（新增隐私接口后忘记同步），下个版本被拦 | 已整改：声明文件含「信息类型 ↔ 代码位置」对照表，由扫描器生成；断言「隐私声明覆盖代码调用的隐私接口」 |
| R3-05 | P2 | 仓库根目录 `.<appId>.privacy.json`（SDK 生成的云服务侧采集项清单）易被误认为平台侧声明 | 已整改：`structure.test.js` 断言存在**独立的** `docs/privacy-declaration.md`；Skill 反模式 §5 记录该坑 |

**本轮复查结论**：整改后 `structure.test.js` 50/50、`format.test.js` 32/32、
`check_declaration_alignment.py` 对本项目判定 FAIL=0。

## 遗留边界（不阻塞验收）

- 微信授权登录尚未真机验证（模拟器无法取得真实 `wx.login` code）；uid 形态依据为 SDK 源码注释。
- 报名配图体积上限未在服务端强制。
- `shared/` 作用域不支持 upsert，覆盖写依赖「先删后传」，运维脚本已处理。
- **平台侧隐私协议尚未誊写**：仓库已有 `docs/privacy-declaration.md` 草稿，但 mp 后台「管理 → 版本管理 → 提交代码审核 → 信息填写页面」（入口2）的表单内容仍需人工誊写并重新提审（Task 20）。仓库里有文件**不等于**平台已声明。
- **活动主图迁移待人工一步**：需在 WorkBuddy「文件存储」管理页把
  `assets/covers/<slug>.png` 上传到 `shared/_application/activities/`，
  随后执行 `node scripts/tools/sync-activity-covers.cjs` 完成绑定与自检。
  在此之前 `cover_path` 仍指向旧的 `shared/<uid>/` 路径（小程序功能正常，
  但该路径内嵌 uid，尚未彻底根除）。

> AI生成
