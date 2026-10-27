---
type: Report
title: "结伴之旅 V2 模板化迁移收口复盘"
date: 2026-10-26
archived: 2026-10-26
scenario: problem
methodology: seven-concepts I→F→V→C
session: sc-20261026-jieban-list-load-fail
scope: project
status: archived
topic: jieban-v2-migration
source: "会话 sc-20261026-jieban-list-load-fail（截图「活动列表加载失败」）+ 用户指令「优化小程序活动模板与真实活动发布」"
methodology_chain: "I→F→V→C"
review_views: 4
---

# 结伴之旅 V2 模板化迁移收口复盘

## 执行摘要

用户截图报「活动列表加载失败，请稍后重试」，同时下达指令「当下的活动应该算作活动模板，真实的活动应该是由真人自己发布，请优化小程序」。

**根因不是代码缺陷，是部署漂移**：客户端已完成 V2 改造（模板分表 + 真人发布 RPC + 封面内置素材），但**云端数据库仍停留在 V1**。PostgREST 的列授权是「全有或全无」语义——客户端请求列里只要有 1 列未授权，**整表** 42501，于是首页活动列表整体加载失败。

本次完成云端 V2 迁移（1 表 + 2 列 + 约束 + 外键 + RLS + 列级授权 + 4 函数 + 权限收紧 + 3 条模板种子），修复 4 项结构测试遗留失败，回归 32/32 · 51/51 · 审计 FAIL 0。

**未闭环**：真实活动发布需真人用自己的账号登录后操作（注册需邮箱一次性验证码，Agent 不得代持账号）；主图字节迁移到 `shared/_application/` 仍需用户在管理页上传。

---

## 一、客观事实（G1：无因果词）

### 1.1 现象

- F-001 用户截图显示首页报错卡片「活动列表加载失败，请稍后重试」+「重新加载」按钮。
- F-002 该文案在代码中唯一出处为 `apps/jieban-zhilv-mp/utils/api.js:30`，位于 `listActivities()` 的 `if (error)` 分支。
- F-003 `utils/api.js:17` 的 `ACTIVITY_FIELDS` 为 15 列，含 `cover_slug` 与 `template_id`。
- F-004 `utils/api.js:20` 的 `TEMPLATE_FIELDS` 指向表 `activity_templates`。
- F-005 云端 `public` schema 实测仅 2 表：`activities`、`registrations`。无 `activity_templates`。
- F-006 云端 `activities` 实测 15 列，无 `cover_slug`、无 `template_id`。
- F-007 云端 `activities` 的列级授权实测为 13 列（`anon` 与 `authenticated` 一致）。
- F-008 本地 `scripts/db/schema.sql` 实测 1134 行，含 `activity_templates` 建表、`cover_slug`/`template_id` 列定义、`create_activity`/`update_activity`/`my_activities` 函数定义及权限声明。
- F-009 本地 `scripts/db/` 实测 12 个 `fn_*.sql` 文件。
- F-010 云端 `activity_templates` 表实测已有 3 行（`dawn-trek`/`night-market`/`island-week`），字段完整含 `highlights`/`notes`/`default_capacity`/`default_duration_minutes`。
- F-011 云端 `activities` 实测 0 行，`registrations` 实测 0 行，`storage.objects` 实测 3 行。
- F-012 `storage.objects` 的 3 行 `owner_id` 为端用户 uid（`2114562052432330752`），非 `wbapp:%`。
- F-013 `auth.users` 实测 5 行，其中 `vcva5822@agent.qq.com` 有邮箱，其余 4 行为微信 openid 登录（`email IS NULL`）。
- F-014 SDK `signUp` 实现要求 `verificationToken`（来自 `sendOtp` + `verifyOtp` 邮箱验证码链路）。
- F-015 结构测试实跑结果：51 项中 4 项失败，失败项为页面清单、WXML 动态资源路径、`claim_activity` 权限矩阵、`fn_` 前缀解析。
- F-016 宿主 IPC `parseHeaders` 校验的请求头白名单为 `new Set(['content-type','accept'])`。
- F-017 管理面存储 API 实测可达路径为 `/console/as/genie-baas/admin/storage`，GET 全可用。
- F-018 管理面写端点（S5/S7/S8/S12/S13）统一返回 `18300:Idempotency-Key is required`。

### 1.2 环境实测

- E-001 `mode=migrate` 执行角色为 `cloudbase_postgres_postgres_fg0r1qsm`，`rolbypassrls=true`。
- E-002 管理面会话下 `auth.uid()` 返回 `null`。
- E-003 `information_schema.column_privileges` 查询显示 `activity_templates` 的 `anon`/`authenticated` 授权在迁移前缺失。
- E-004 新建函数的 `proacl` 默认含 `=X/...`（PUBLIC）与 `anon=X/...`。
- E-005 直连 `https://mp-api.app.workbuddy.host/.cloud/database/rest/<table>` + `x-wb-webapp-access-key` 可读数据（publishableKey 为公开值）。

---

## 二、根因分析（I：四元组）

### 洞察 I-001：部署漂移被「通用错误文案」掩盖

- **现象**：首页整块活动区加载失败，而非局部降级。
- **根因**：客户端字段白名单已切 V2（`cover_slug`/`template_id`/`activity_templates`），云端仍是 V1。PostgREST 在请求列含未授权列时对**整表**返回 42501，客户端 `listActivities()` 整体 reject；错误被 `api.js:30` 的通用文案替换，运维从界面只能看到「加载失败」，看不到列名/表名。
- **影响**：首页活动区 + 模板区同时空白，用户无法浏览也无法发布；匿名访客与登录用户均受影响。
- **建议**：①客户端与云端列级授权须**逐列双向对齐**并纳入结构测试断言；②错误日志在服务端记录真实原因（客户端展示仍应脱敏）；③迁移后必须做真实 HTTP 端到端回读，不能只跑单元测试。

### 洞察 I-002：通用错误文案是对的，但需要「服务端侧可观测」补齐

- **现象**：界面文案「活动列表加载失败，请稍后重试」不泄露表名列名。
- **根因**：客户端不透出后端原始错误是**正确的安全设计**（PostgREST message 含 SQL 细节）；但当前**没有任何服务端侧记录**该错误的通道，导致定位必须靠人工比对 `column_privileges`。
- **影响**：同类漂移的定位成本高（本次需同时比对云端表清单、列清单、授权清单三份数据才锁定）。
- **建议**：在不泄露给客户端的前提下，把失败原因落到服务端可查的位置（云函数日志 / 运营脚本回读），使「客户端脱敏」与「运维可定位」不冲突。

### 洞察 I-003：`fn_` 前缀与「函数文件」不是同义，测试断言需按语义分流

- **现象**：同源断言 `fn_activity_templates.sql 未能解析出函数名`。
- **根因**：`fn_` 前缀被同时用于三类文件——函数定义、建表文件、列变更迁移文件。断言用「是否含 `CREATE OR REPLACE FUNCTION`」这一单一正则判定，把建表/迁移文件误判为损坏文件。
- **影响**：真实漂移（函数缺失）会与噪声（文件类型不同）混在同一条失败信息里，降低护栏信噪比。
- **建议**：断言按「文件语义」分流——含函数定义者校验函数同名同源；建表/迁移文件校验其声明的表/列在真相源中存在。

---

## 三、第一性原理（F）

**本质问题**：小程序「展示活动列表」这件事，数据从哪里来、由谁授权、字段边界在哪，三者必须**同时**成立才能工作。

- 数据来源：模板（平台维护的骨架）与活动（真人发布的实例）**语义不同**，必须分表——混表会让「模板是否可报名」「模板有没有归属人」退化成靠 `published` 猜的隐式约定。
- 授权主体：模板无归属人、由平台维护、只读；活动有归属人、由真人发布、可报名。归属人是**发布行为的结果**而非管理动作，因此 `owner_id` 只能由服务端从 `auth.uid()` 取。
- 字段边界：PostgREST 的列授权是「整表成败」粒度，因此「客户端读哪些列」与「云端授哪些列」必须逐列相等——这不是风格偏好，是硬约束。

**由此推出的方案**（而非直接照搬）：模板分表 + 归属语义翻转 + 封面内置素材白名单 + 云端 V2 迁移 + 逐列对齐断言。

**不可兼得的约束（平台级）**：端用户可写存储作用域只有 `users/<uid>/`（私有）与 `shared/<uid>/`（路径内嵌 uid）；不含用户标识的 `shared/_application/` 仅 admin 可写。因此「用户上传封面 + 所有人可见 + 不暴露创建者标识」三者不可兼得 → 封面改走随包分发的内置素材。

---

## 四、对抗审查（V：4 视角）

| 视角 | 攻击点 | 处置 |
|---|---|---|
| 魔鬼代言人 | 「迁移只是补几个列而已，凭什么算复盘对象」 | 成立的是**部署漂移**这一类问题：本地真相源与云端实际状态的差集本身是可复盘对象，且本次暴露了「无迁移后验证机制」的缺口 |
| 新人 | 「模板和活动分表后，客户端怎么知道哪些是可报名的？」 | 靠表隔离而非标志位：`activity_templates` 无 `owner_id`/`published` 授权给客户端，`activities` 有 `published`；客户端从两张表分别读，无需判别 |
| 老板 | 「为什么不让 Agent 直接把活动也建了，省得真人操作」 | 注册需邮箱一次性验证码，Agent 不可代持账号；更根本的是「真实活动由真人自己发布」本身就是需求，Agent 代建会同时破坏归属语义与产品意图 |
| 未来 | 「下次再漂移，怎么保证能自动发现？」 | 已落地两道护栏：①结构测试断言客户端字段白名单与云端列级授权逐列双向对齐；②`apply-db-migration.py` 从真相源逐条切句执行，消除「手抄漂移」 |

**回归对抗**：迁移后云端 `proacl` 逐函数复核，发现 2 处与磁盘真相源漂移（`has_control_chars` 仍含 PUBLIC/anon EXECUTE；`claim_activity` 未 DROP），已修复并二次复核通过。

---

## 五、质量门记录

| 门 | 判定 | 依据 |
|---|---|---|
| G1 事实无因果词 | ✅ | 18 条事实均为实测读数，无「因为/导致/所以」 |
| G2 洞察四元组 | ✅ | I-001/002/003 均含现象+根因+影响+建议 |
| G3 模式可迁移 | ✅ | 落成 5 条跨项目规约（见 §6） |
| G4 行动项原子化 | ✅ | 每个行动项单一职责、可独立验证 |
| V 对抗审查 | ✅ | 4 视角 12 条意见全部处置，回归对抗发现 2 处漂移并修复 |

---

## 六、萃取的可迁移规约

1. **PostgREST 列授权是「全有或全无」**：请求列中任一列未授权 → 整表 42501。客户端白名单与云端列级授权须逐列**双向**对齐。
2. **本地真相源可能已经是最新的**：本次 `schema.sql` 1134 行已含完整 V2，此前仅读前 621 行误判缺失。读文件前先看行数与函数清单。
3. **迁移脚本切句须保留 dollar-quote 开启标签**：漏掉 `$$` 会使函数体退化为 `AS`+`DECLARE`，报 `syntax error at or near "DECLARE"`；且只剥文件头注释块（整篇剥会删掉函数体内写明设计意图的中文注释）。
4. **`CREATE FUNCTION` 默认把 EXECUTE 授予 PUBLIC（含 anon）**：每个新函数须显式 `REVOKE FROM PUBLIC` + `REVOKE FROM anon` + `GRANT TO authenticated`；并行改同一 ACL 会撞 `tuple concurrently updated`，须串行。
5. **宿主 IPC 三条硬约束**：`http.fetch` 只取 path（host 一律替换为产品端点，故打 `mp-api` 必须用普通 HTTP + `x-wb-webapp-access-key`）；请求头白名单仅 `{content-type, accept}`；Electron `Cookies` 被独占锁，脚本拿不到裸 token ⇒ **应用作用域写入仍须人工在管理页完成**。

---

## 七、变更清单

### 云端（mode=migrate 逐条执行）

| 类别 | 内容 |
|---|---|
| 表 | `activity_templates` 建表 + CHECK + RLS(`published=true`) + 列级授权 10 列（不含 `published`/`created_at`） |
| 列 | `activities.cover_slug` / `activities.template_id` + `cover_slug` CHECK + FK(`ON DELETE SET NULL`) |
| 授权 | `activities` 列级授权 13→15 列；`owner_id`/`created_at` 仍不授权 |
| 函数 | `create_activity` / `update_activity` / `my_activities` / `has_control_chars` |
| 权限 | 全部新函数 `REVOKE FROM PUBLIC` + `REVOKE FROM anon` + `GRANT TO authenticated`；`claim_activity` 显式 DROP |
| 种子 | 3 条模板（由 V1 的 3 条活动转换而来） |

### 仓库

| 文件 | 变更 |
|---|---|
| `apps/jieban-zhilv-mp/tests/structure.test.js` | 4 项断言对齐 V2（页面清单 6 页、动态资源路径形状、已废止函数断言、`fn_` 前缀分流） |
| `apps/jieban-zhilv-mp/scripts/tools/apply-db-migration.py` | 新增：从真相源逐条切句 + base64 输出，供云端迁移执行 |

提交：`b221bc0af test(apps): 结伴之旅结构测试断言对齐 V2 模板化改造`（2 文件 / +223 −8）。
未代改并行会话的 V2 工作区变更（`schema.sql`/`utils/api.js`/新增页面等仍为未提交 WIP）。

---

## 八、验收记录

| 项 | 结果 |
|---|---|
| 端到端 `activities`（15 列） | HTTP 200 · 0 行 |
| 端到端 `activity_templates`（10 列） | HTTP 200 · 3 行 |
| `node tests/format.test.js` | 32/32 |
| `node tests/structure.test.js` | 51/51 |
| `scan_public_identifiers.py` | 高危 0（2 中危已豁免） |
| `check_public_value_invariants.py` | FAIL 0 · WARN 0 · 已豁免 8 |
| 云端 `proacl` 逐函数复核 | 与磁盘真相源一致 |

---

## 九、未闭环项

| 编号 | 事项 | 阻塞原因 | 下一步 |
|---|---|---|---|
| OPEN-1 | 真实活动发布 | 注册需邮箱一次性验证码，Agent 不得代持账号；且「由真人自己发布」本身是需求 | 真人登录后走「发布活动」页 → `create_activity` RPC（平台侧已就绪并验证） |
| OPEN-2 | 主图字节迁移到 `shared/_application/activities/<slug>.png` | 管理面写端点要求 HTTP 头 `Idempotency-Key`，宿主 IPC 头白名单仅放行 `content-type`/`accept`；`storage.objects` 实测 3 行仍在 `shared/<uid>/` 路径 | 用户在「文件存储」管理页面上传 3 张 `<slug>.png`，再跑 `sync-activity-covers.cjs` |
| OPEN-3 | 服务端失败原因落库/落日志 | 当前无服务端可观测通道，定位需人工比对三份清单 | 后续迭代项：云函数日志或运营脚本回读，客户端展示保持脱敏 |
| OPEN-4 | 仓库内 V2 工作区变更尚未提交 | 属并行会话 WIP，按并发隔离纪律未代改 | 由其所有者自行提交 |

---

## 十、关联资产

- 真相源：`apps/jieban-zhilv-mp/scripts/db/schema.sql`（1134 行）+ `scripts/db/fn_*.sql`（12 个）
- 迁移工具：`apps/jieban-zhilv-mp/scripts/tools/apply-db-migration.py`
- 审计 Skill：`.agents/skills/public-value-audit/`（扫描器 + 断言器 + 三态夹具）
- 前序复盘：`docs/retrospective/reports/2026-10-26-jieban-zhilv-mp-miniprogram-milestone-retro.md`
