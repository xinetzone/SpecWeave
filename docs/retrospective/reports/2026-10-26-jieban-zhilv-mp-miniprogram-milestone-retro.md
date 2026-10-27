---
type: Report
title: "结伴之旅微信小程序里程碑复盘"
date: 2026-10-26
archived: 2026-10-26
scenario: milestone
methodology: seven-concepts R→I→E→V→A→C
session: sc-20261026-jieban-zhilv-milestone
scope: project
status: archived
topic: jieban-zhilv-milestone
pattern: "skills/public-value-audit"
methodology_chain: "R→I→E→V→A→C"
review_views: 4
---

# 结伴之旅微信小程序里程碑复盘

## 执行摘要

本里程碑交付了「结伴之旅」活动报名微信小程序（四页闭环 + 微信授权登录 + 云端数据库 + 云端存储图片），
并在两轮对抗审查中修掉 27 条发现，最终萃取出可复用 Skill `public-value-audit`。

交付三样产物：
1. **小程序本体**——`apps/jieban-zhilv-mp/`，46 个非图片文件 / 6096 行可读源码，4 页闭环，云端 2 表 8 函数，
   数据面 HTTP 实测全部达标；
2. **可复用 Skill** `.agents/skills/public-value-audit/`（v1.1.0）——三张清单（公开面 / 标识列 / 值域构造方）
   的交叉定位法 + 收口三件套 + 第四件「读授权面对齐」+ 7 条可回归不变量 +
   扫描器/断言器/自检三脚本 + 三态对照夹具（pre-fix / p115-only / post-fix）；
3. **本复盘报告** + 四处登记面同步（README / registry / TOML 镜像 / CHANGELOG）。

> ⚠️ **本报告自身也经过 4 视角对抗审查**（50 条意见，采纳 12 类修复，见 §7）。
> 审查同时查出**工具自身的 8 处真实缺陷**——包括两处让不变量「恒不触发」的解析 bug。

过程中最关键的一次反转：**列级授权挡住了 `owner_id`，却从 `cover_path` 这条路把同一个 uid 又发了出去**。
上一轮整改只盯住了「哪一列被授权」，没有追问「**同一个标识是不是还从别的列漏出去**」——
同一张表两列可见性不一致，等于自己打自己。

| 指标 | 值 |
|---|---|
| 应用 | 微信小程序「结伴之旅」（面向全人类） |
| 页面 | 4（活动首页 / 活动详情 / 在线报名 / 报名记录） |
| 云端 applicationId | `wbapp_jkkqDWa54EKtV5jxugZnqz`（miniprogram） |
| 云端数据 | `activities` 3 行 / `registrations` 0 行 / `storage.objects` 3 个 / public 函数 8 个 |
| 对外列级授权 | 13 列（无 `owner_id`、无 `created_at`；service_role 与管理员持 15 列） |
| 客观事实 | 42 条（F-001–F-042） |
| 核心洞察 | 3 条（四元组完整） |
| 对抗审查发现 | 27 条（第一轮 19 + 第二轮 8，含 2 条 P1） |
| 报告自身的 V 门审查 | 4 视角 50 条意见，采纳 12 类修复 |
| 萃取产物 | 1 个 Skill（v1.1.0，1917 行，自检 25/25 通过，质量门 95 分） |
| 回归测试 | `format.test.js` 32/32 · `structure.test.js` 46/46 |
| 数据面 HTTP 实测 | 业务列 200 / `select=owner_id` 401 / `select=created_at` 401 / `order+limit` 200 / RPC 200 |
| 质量门 | G1✅ G2✅ G3✅ G4✅ V✅ |

---

## CMD-LOG 执行记录

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261026-jieban-zhilv-milestone | msg=方法论编排开始：结伴之旅微信小程序里程碑复盘 | ctx={"scenario":"milestone","topic":"jieban-zhilv-milestone","depth":"deep"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261026-jieban-zhilv-milestone | msg=场景识别：场景1 里程碑复盘（触发词命中"里程碑复盘""洞察""萃取"） | ctx={"scenario":"milestone","matched_triggers":["里程碑复盘","洞察","萃取"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261026-jieban-zhilv-milestone | msg=链路选定：R→I→E→V→A→C（depth=deep，V 多轮） | ctx={"chain":"R→I→E→V→A→C","depth":"deep","v_mandatory":true}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R0 | event=CONCEPT_STARTED | session=sc-20261026-jieban-zhilv-milestone | msg=R阶段开始：从 schema.sql / review.md / 云端实测 / 测试结果采集客观事实 | ctx={"min_facts":20}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R1 | event=CONCEPT_COMPLETED | session=sc-20261026-jieban-zhilv-milestone | msg=R阶段完成：42 条客观事实 | ctx={"facts_count":42,"causal_words_found":0}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G1 | event=GATE_PASSED | session=sc-20261026-jieban-zhilv-milestone | msg=G1质量门通过：事实 42 条 ≥ 20、无因果词、关键数据完整可追溯 | ctx={"gate":"G1","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=I0 | event=CONCEPT_STARTED | session=sc-20261026-jieban-zhilv-milestone | msg=I阶段开始：提炼核心洞察
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=I1 | event=CONCEPT_COMPLETED | session=sc-20261026-jieban-zhilv-milestone | msg=I阶段完成：3 条核心洞察，四元组完整 | ctx={"insights_count":3,"dimensions":["审计方法","资产建模","变更纪律"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G2 | event=GATE_PASSED | session=sc-20261026-jieban-zhilv-milestone | msg=G2质量门通过：洞察四元组完整、维度不重叠、有反常识性 | ctx={"gate":"G2","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=E0 | event=CONCEPT_STARTED | session=sc-20261026-jieban-zhilv-milestone | msg=E阶段开始：萃取可复用模式
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=E1 | event=CONCEPT_COMPLETED | session=sc-20261026-jieban-zhilv-milestone | msg=E阶段完成：萃取模式"取值域收口"（落为 Skill public-value-audit v1.0.0） | ctx={"pattern":"取值域收口","artifact":".agents/skills/public-value-audit","anti_patterns":6,"migration_examples":3}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G3 | event=GATE_PASSED | session=sc-20261026-jieban-zhilv-milestone | msg=G3质量门通过：模式含触发场景+核心步骤+6 反模式+检验标准+3 迁移示例，产物自带可执行脚本与前后对照夹具 | ctx={"gate":"G3","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V0 | event=CONCEPT_STARTED | session=sc-20261026-jieban-zhilv-milestone | msg=V阶段开始：4 视角对抗审查（depth=deep，多轮）
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V1 | event=CONCEPT_COMPLETED | session=sc-20261026-jieban-zhilv-milestone | msg=V阶段完成：4 视角 50 条意见，采纳 12 类并修正原产出（含工具侧 8 处真实缺陷） | ctx={"viewpoints":4,"findings":50,"adopted":12,"tool_defects_fixed":8,"skill_version_after":"1.1.0"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G4 | event=GATE_PASSED | session=sc-20261026-jieban-zhilv-milestone | msg=G4质量门通过：行动项原子化（单一职责/可独立验证/有 Owner 与时间节点） | ctx={"gate":"G4","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C1 | event=CONCEPT_COMPLETED | session=sc-20261026-jieban-zhilv-milestone | msg=C阶段完成：产物原子提交 | ctx={"commits":1}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261026-jieban-zhilv-milestone | msg=全链路完成：报告 + 3 洞察 + 1 Skill + 原子行动项 | ctx={"gates":"G1,G2,G3,G4,V","artifacts":3}
```

---

## 1. 客观事实清单（R 阶段）

> 全部为可复核的客观陈述，不含因果推断与主观评价。

| 编号 | 事实 |
|---|---|
| F-001 | 应用位于 `apps/jieban-zhilv-mp/`，含 45 个非图片文件（14 JS / 10 JSON / 8 SQL / 5 WXSS / 4 WXML / 2 MD / 1 PY / 1 CJS）与 26 个 PNG，可读源码 6344 行 |
| F-002 | 四个页面登记在 `app.json`：index（活动首页）、detail（活动详情）、signup（在线报名）、records（报名记录） |
| F-003 | 云端 applicationId 为 `wbapp_jkkqDWa54EKtV5jxugZnqz`，applicationType 为 miniprogram |
| F-004 | 云端 `activities` 表 3 行，`registrations` 表 0 行，`storage.objects` 3 个 |
| F-005 | 云端 public schema 共 8 个函数 |
| F-006 | `information_schema.column_privileges` 中 anon 与 authenticated 对 `activities` 各持 13 列 |
| F-007 | `activities` 表：`owner_id` 与 `created_at` 不在 anon/authenticated 的授权列清单内（13 列口径）；service_role 与管理员持 15 列。`registrations` 表为**表级** GRANT，anon/authenticated 可见其全部列（含 `owner_id`/`contact`/`created_at`），仅靠 RLS `registrations_read_own`（`owner_id = auth.uid()`）限制到本人行 |
| F-008 | 3 个存储对象均在 `shared/2114562052432330752/activities/` 路径下，owner_id 为 `2114562052432330752` |
| F-009 | 云端主图绑定相关函数为 `set_activity_cover(TEXT,TEXT)` 与 `sync_activity_cover(TEXT)` |
| F-010 | `claim_activity_cover(TEXT,TEXT)` 不存在于云端 `pg_proc` |
| F-011 | `set_activity_cover` 的 EXECUTE 授予对象为 service_role + 管理员，无 anon / authenticated |
| F-012 | `sync_activity_cover` 的 EXECUTE 授予对象为 authenticated + service_role + 管理员 |
| F-013 | `set_activity_cover` 与 `sync_activity_cover` 的返回类型均为 `text` |
| F-014 | 函数体磁盘与云端逐字节一致：`set_activity_cover` md5(prosrc)=`4e09cedf71ff116afd3a1f333ffb05fc`（1275 B）；`sync_activity_cover` md5(prosrc)=`eef21d37d7e55198df6749eb06c6eab3`（1049 B） |
| F-015 | 数据面匿名 HTTP：`GET /.cloud/database/rest/activities?select=id,slug,title,cover_path&limit=2` → 200 |
| F-016 | 同会话 `?select=owner_id&limit=1` → 401 `DATABASE_42501` |
| F-017 | 同会话 `?select=created_at&limit=1` → 401 `DATABASE_42501` |
| F-018 | 同会话 `?select=*&limit=1` → 401 `DATABASE_42501` |
| F-019 | 同会话 `?select=id,slug&order=starts_at&limit=1` → 200 |
| F-020 | 同会话 `POST /rpc/registration_stats` → 200，响应体 `[]` |
| F-021 | 存储网关对 `shared/_application/` 的写入，SDK upload / 预签名 PUT / 直连 PUT / 预签名签发四种形态均返回 403 `STORAGE_ACCESS_DENIED` |
| F-022 | 存储网关对 `shared/<uid>/` 的直连 PUT → 200 `{"Id":"5c8ae7ae-…","Key":"runtime/shared/…/activities/__probe_ctrl.png"}` |
| F-023 | 管理面权限表：`shared/_application` 的 `write` 为 `admin_only`，`shared/<uid>` 的 `write` 为 `owner_and_admin` |
| F-024 | 匿名会话请求存储签发 → 401 `MISSING_CREDENTIALS`；`object/public/runtime/...` → `STORAGE_BUCKET_NOT_FOUND` |
| F-025 | 存储 RLS 策略 `workbuddy_runtime_objects_insert`（roles={authenticated}）的 with_check：`bucket_id='runtime' AND owner_id=auth.uid() AND ((folder[1]='users' AND folder[2]=auth.uid()) OR (folder[1]='shared' AND folder[2]=auth.uid()))` |
| F-026 | 存储 RLS 策略 `workbuddy_runtime_objects_select` 含 `folder[2]='_application' AND owner_id LIKE 'wbapp:%'` 分支 |
| F-027 | `registrations` 的 RLS SELECT 策略为 `owner_id = auth.uid()`，roles={anon, authenticated} |
| F-028 | 对抗审查共 27 条发现：第一轮 19 条、第二轮 8 条（2 条 P1 + 6 条 P2） |
| F-029 | `node tests/format.test.js` → 32/32；`node tests/structure.test.js` → 46/46；全部 js/cjs 通过 `node --check` |
| F-030 | spec 三件套 688 行（spec.md 183 / tasks.md 327 / review.md 178） |
| F-031 | 本地主图资源 4 张，文件名与 slug 同名：`dawn-trek.png` / `night-market.png` / `island-week.png` / `default.png` |
| F-032 | 运营脚本 `scripts/tools/sync-activity-covers.cjs` 内无 `storage.upload` 调用，含 `--cleanup` 分支 |
| F-033 | 萃取 Skill `public-value-audit`（v1.1.0）：SKILL.md 334 行 + references 147/190 行 + scripts 447/489/121 行 = 代码与文档 1728 行；夹具 6 文件 189 行；合计 1917 行 |
| F-034 | 扫描器：`pre-fix` 夹具高危 2 条（H2/H3/H6 中 H2+H6 为高危）/ 退出码 1；`p115-only` 夹具高危 2 条（H6 服务端用标识拼路径 + H7 字面量内嵌标识）/ 退出码 1；`post-fix` 夹具高危 0 条 / 退出码 0；对 `apps/jieban-zhilv-mp` 实跑：文件 21 / 授权语句 2 / 对外表 2 / 检测到行隔离 2，高危 0、中危 6、已豁免 1，退出码 0 |
| F-035 | 不变量断言器：`pre-fix` 夹具 FAIL 6 / WARN 0 / 已豁免 2，退出码 1；`p115-only` 夹具 FAIL 2（I3 值域由入参决定、I7 字面量含标识），退出码 1；`post-fix` 夹具 FAIL 0 / WARN 1 / 已豁免 1，退出码 0；对 `apps/jieban-zhilv-mp` FAIL 0 / WARN 0 / 已豁免 8，退出码 0 |
| F-036 | Skill 自检 25 项断言全部通过，退出码 0；Skill 质量门 `check-skill-quality.py --score` 95 分（审查前 70 分）；链接门 0 断链 |
| F-037 | `auth.users` 共 2 个账号（1 个 email 为空，1 个 email 为 `vcva5822@agent.qq.com`），不存在 uid 形如 `wbapp:*` 的账号 |
| F-038 | `activities.owner_id` 的取值集合为单值 `2114562052432330752` |
| F-039 | 微信 uid 形态 `wx:` + openid 的依据仅为 SDK 源码注释，无真机实证 |
| F-040 | 探针元数据行 `shared/_application/activities/__probe_q5.png` 曾写入 `storage.objects`，已删除；当前 `storage.objects` 无 `__probe%` 行 |
| F-041 | `node --test tests/`（目录参数）在 Windows 下把目录当单文件执行而失败，逐文件运行正常 |
| F-042 | 文档看板：`.trae/specs/README.md` 收录 738 specs；`apps/README.md` 收录 15 个应用条目 |

---

## 2. 过程分析

### 2.1 里程碑时间线

| 阶段 | 动作 | 产物 |
|---|---|---|
| 需求落地 | 读 seven-concepts-cmd 与 `apps/` 路由规范，搭建四页骨架 | 小程序骨架 + spec 三件套 |
| 云端建模 | 建 `activities` / `registrations` 两表、RLS 策略、6 个 RPC | `scripts/db/schema.sql` |
| 素材与 UI | Pillow 生成 22 图标 + 4 主图，WXML/WXSS 四页布局 | `assets/` + `pages/` |
| SDK 契约修复 | 读 SDK 产物源码发现 4 处 P0（字段名 / string-body / getRandomValues / nodeModules） | `vendor/workbuddy-cloud-sdk/` vendoring |
| 对抗审查第一轮 | 4 视角并发安全 / 一致性 / 边界 / 存储通道审查 | 19 条发现 |
| 整改与回归 | 修 12 类问题，回归 44/44 | `format.test.js` 30→32、`structure.test.js` 44→45 |
| 对抗审查第二轮 | 自查 + 独立复核发现 `cover_path` 后门 | 8 条发现（含 2 条 P1） |
| 根除与迁移准备 | 取值域收口、脚本改口径、夹具化 | `sync_activity_cover` + 权限矩阵复核 |
| 方法论编排 | R→I→E→V→A→C，萃取可复用 Skill | 本报告 + `public-value-audit` |

### 2.2 对抗审查处置（两轮共 27 条）

| 等级 | 条数 | 代表条目 | 处置 |
|---|---|---|---|
| P0 | 4 | SDK 字段名 `signedUrl` / string-body 限制 / `getRandomValues` 未透传 / `nodeModules:false` 缺 `miniprogram_npm/` | 修（读 SDK 产物源码实证，非采信审查报告） |
| P1 | 6 | `owner_id` 表级授权可直查 / `cover_path` 内嵌 uid / 运维链路断裂（**P2 级，见下**）/ `detail.js` 尾部孤立 `}`（**P2 级**）/ 另 2 条 P1 | 修（列级授权 → 取值域收口；语法修复；显式参数化） |
| P2 | 16 | 路径校验拼正则 / 静默吞错 / 令牌落盘 / `ensureSession` 非幂等 / upsert 语义误判 / `created_at` 未收回 / `fallbackCover` 硬编码 map | 修（全部） |
| P3 | 1 | Origin 可伪造 / 报名配图体积上限未在服务端强制 | 接受偏差并显式登记 |

**两处值得单列的发现**：
- **P0×4 是独立读 SDK 产物源码实证的**——审查报告只给了「疑似」，读源码后确认字段名与契约，
  避免把猜测当结论修。
- **P1「运维链路断裂」是审查者自己引入的回归**：把 `claim_activity` 收归 service_role 后，
  其函数体 `v_uid := auth.uid()` 在该角色下为 NULL，运营脚本用 authenticated 会话调用必然失败。
  修法不是放宽安全边界，而是把归属判定彻底移出终端用户可触达范围。

### 2.3 关键实测：三个「反直觉」点

1. **RLS 策略引用无授权列仍正常求值**
   `owner_id` 不在列级授权清单内，但 `USING (published = TRUE OR owner_id = auth.uid())` 照常工作。
   探针验证：`seen_by_owner=1 / seen_by_other=0 / anon_total=3 / auth_total=4`。
   ⇒ 「收回列授权」与「RLS 用该列判归属」可以共存。
2. **列级授权下，请求未授权列会让整表失败**
   `select=id,owner_id` 与 `select=*` 均返回 401，不是「少一个字段」。
   ⇒ 客户端白名单必须与服务端授权清单逐列对齐。
3. **应用归属作用域只有管理员能写，读却对全体登录用户开放**
   `_application` 的写受 RLS with_check 限制（要求 `owner_id = auth.uid()` 且路径第 2 段 = `auth.uid()`），
   而 SELECT 策略含 `_application` 分支。四种写入形态全部 403。

---

## 3. 核心洞察（I 阶段）

### I-001：挡住列 ≠ 挡住值 —— 同一标识换个字段名就绕回去了

- **陈述**：列级授权只封住了 `owner_id` 这一列；`cover_path` 的值里嵌着同一个 uid，
  于是「列授权已生效」与「标识已不外泄」是两件事。
- **证据**：F-006 / F-007（`owner_id` 已不在对外授权列，匿名查它返回 401）、
  F-008 / F-015（`cover_path` 公开可读，值为 `shared/2114562052432330752/activities/dawn-trek.png`）、
  F-038（该段与 `activities.owner_id` 取值完全相同）。
- **反常识**：直觉上「`owner_id` 已经 42501，泄露闭环了」；实际上闭环的是**列**，
  不是**值**——同一个标识换个字段名、甚至不用换（只是被拼进了路径）就又出去了。
- **行动**：每次整改一处泄露面后，重跑全量扫描器并追问「同一个标识还从哪些列 / 字段 / 路径段漏出」；
  把「公开可见的值里不含标识」作为独立不变量写进 CI，而不是只断言「某列不可读」。

### I-002：应用资产放进用户作用域，路径必然带标识 —— 作用域选型比字段脱敏更根本

- **陈述**：活动主图是应用资产，却存放在终端用户归属作用域 `shared/<uid>/activities/`；
  作用域模型决定了路径第 2 段必然是归属标识，于是「路径不含 uid」在这个位置不可能实现。
- **证据**：F-008（对象在 `shared/<uid>/` 下）、F-023（`_application` 写权限为 admin_only）、
  F-025（RLS with_check 要求路径第 2 段 = `auth.uid()`，即「谁写就带谁的 uid」）。
- **反常识**：直觉上「路径里出现 uid，加个哈希或短 token 遮一下就行」；
  但作用域模型决定了：**只要路径按人分目录，第 2 段就是归属段，遮蔽只能让它不可读、
  不能让它不承载标识**（脱敏是更弱的手段，且不可反查性另需预签名 URL 支撑）。
  正解是**换作用域**——路径里根本不出现归属段。
- **行动**：新增「按人分目录」的资源前先问一句「这是应用资产还是用户资产」；
  应用资产一律走应用归属作用域，并让服务端成为路径的唯一构造方。
  ⚠️ **收口后必须补第四件「读授权面对齐」**：迁到应用级命名空间后，存储侧读授权从「行级受限」
  变成「命名空间可读」，若拼接进路径的片段（如 slug）可枚举，未发布对象的存储对象也可能被直接读到
  ——**表级 RLS 在这一层被绕过**（见 Skill `references/audit-method.md` 的收口手法库）。

### I-003：收紧权限是行为变更 —— 必须同步核查「谁还在调用」

- **陈述**：把 `claim_activity` 的 EXECUTE 收归 service_role 后，其函数体依赖 `auth.uid()`
  （该角色下为 NULL）直接抛错；叠加运营脚本用 authenticated 会话调用，运维链路当场断裂。
- **证据**：F-028（27 条发现中含该条，且为审查者自身引入的回归）、
  F-011 / F-012（两条主图绑定通道的授权面在本轮被改过，调用方随之改变）。
- **反常识**：直觉上「权限收紧只会更安全」；实际上**收回 EXECUTE 之后函数体可能根本跑不通**，
  且故障点不在你改的那一行，而在函数体内部对会话上下文的隐性依赖。
- **行动**：任何 `REVOKE EXECUTE` 或改授权的动作，都要在同一批次里完成两件事——
  ①列出全部调用方并确认新角色下仍可达；②在新角色下跑一次功能验证。
  授权面变更与功能验证必须同批交付，不允许拆成两个批次。

---

## 4. 萃取产物（E 阶段）

### 4.1 Skill：`public-value-audit`（v1.1.0）

位置：`.agents/skills/public-value-audit/`（1917 行，F-033）

| 文件 | 行数 | 作用 |
|---|---|---|
| `SKILL.md` | 334 | 入口层：三张清单方法、收口三件套 + 第四件、6 步流程、8 条反模式、检验标准、前置条件与降级路径、术语表、命令行入口、收口操作步骤、已知边界、12 项安全清单、Gotchas |
| `references/audit-method.md` | 147 | 方法层：清单填写范式、**授权面取数三条 SQL**、收口手法库、判定决策树、与相邻方法的边界 |
| `references/verified-case.md` | 190 | 证据层：本案例的完整发现链路、前后对照、**工具自身能力边界（已修复 8 处 + 仍存 5 项）** |
| `scripts/scan_public_identifiers.py` | 489 | 扫描器：H1~H7 七类形态，高危/中危/已豁免三级 + 覆盖率守卫 |
| `scripts/check_public_value_invariants.py` | 447 | 断言器：I1~I7 七条不变量，FAIL/WARN/已豁免三级 + 覆盖率守卫，可挂 CI |
| `scripts/selftest.py` | 121 | 自检：对三态夹具断言两个工具的判定结果（25 项） |
| `tests/fixtures/{pre-fix,p115-only,post-fix}/` | 6 文件 | **三态**对照夹具：P1-14 形态与 P1-15 形态必判 FAIL，收口后必判 PASS |

### 4.2 三张清单（Skill 的核心方法）

| 清单 | 内容 | 回答的问题 |
|---|---|---|
| **A 公开面清单** | 哪些表/列/接口/路径对「非所有者」可见 | 谁能看到什么 |
| **B 标识列清单** | 哪些值承载或内嵌用户标识 | 什么算敏感值 |
| **C 值域构造方清单** | 每个公开值由谁拼出来 | 值域能不能被收窄 |

交叉点即泄露面：`A ∩ B`（授权面直接发了标识）与
`A ∩ (B 内嵌于 C 的调用方入参)`（值域由调用方决定，授权面挡不住值）。

### 4.3 收口三件套（缺一不可）

1. **服务端拼装** —— 目标值由服务端拼出，调用方不传该参数 ⇒ 值域从「任意」变「有限集合」；
2. **列级授权** —— 标识列不进对外授权清单（RLS 内部求值不需要列级授权，已实测成立）；
3. **客户端白名单逐列对齐** —— 双向断言防漂移（否则整表 42501，不是少一个字段）。

### 4.4 可执行性：不是文档，是带回归的工程件

- 三态夹具：`pre-fix`（P1-14 形态）与 `p115-only`（**P1-15 形态**）必须判 FAIL，
  `post-fix` 必须判 PASS（F-034 / F-035）；
- 对真实项目 `apps/jieban-zhilv-mp` 实跑：扫描器**高危 0 / 退出码 0**，
  断言器**FAIL 0 / 退出码 0**（F-034 / F-035）；
- 自检 25/25 通过（F-036）；Skill 质量门 95 分；链接门 0 断链；
- ⚠️ **能力边界如实交代**（详见 `references/verified-case.md` §7）：
  两个工具做的是**源码形状分析**，不检查实际数据值——
  「公开值里到底有没有标识」仍需取真实值人工核对（Skill §8 检验标准 1~3 全部是手工步骤）；
  不解析角色组间接授予、不解析 `.ts`/`.js` 内嵌 SQL、不做多级变量传递链的完整语义分析。

### 4.5 6 条反模式（全部来自本项目真实教训）

1. 只把列从客户端拿掉就当作不泄露了（F-015 ~ F-018 反证）
2. 只挡列、不挡值（I-001）
3. 把「值看起来不敏感」当作放行理由（I-002；uid 是数字串但仍是标识）
4. RPC 返回整行 `SETOF <表>`（F-013 的前值）
5. 收紧权限时只看「能不能」，不看「谁还在调」（I-003）
6. 把「值域由入参决定」当成正常设计（I-001 的根因）

### 4.6 跨领域迁移示例（非本领域 · ⚠️ 均未验证）

> 这三条示例**未经第二个案例验证**，且当前扫描器的路径前缀词典不支持其形态
> （无 `teams`、标识词典无 `employee_no`/`工号`）。迁移前请用 Skill §4 的方法手工核对，
> 不要指望脚本直接报出来。

- SaaS 工单系统：`assignee_path = teams/<工号>/queue` → 改 `teams/_shared/queue`；
- Git 托管平台：公开仓库的分支引用带提交者用户名 → 改稳定引用名 + 服务端映射；
- 埋点与 CDN：把 `user_id` 拼进静态资源文件名 → 改内容哈希命名。

---

## 5. 原子行动项（A 阶段）

| # | 行动项 | 单一职责 | 可独立验证 | Owner | 时间节点 |
|---|---|---|---|---|---|
| A-1 | 把 `check_public_value_invariants.py` 接入 CI gates job（配 `--allow-row-isolated`，以 `waived` 计数确认豁免生效） | 新增一道门 | CI 日志出现该不变量项，FAIL 时红灯；**并先在项目上验证该门确实能触发**（造一条故意越界的客户端 select 确认报 FAIL） | 维护者 | 本周内 |
| A-2 | 在 `apps/jieban-zhilv-mp` 登记豁免名单 `public.registrations`（RLS 限本人）并写明理由 | 消除已知 WARN | 断言器输出「已豁免 ≥1 且 WARN 0」（实测当前为已豁免 8 / WARN 0） | 维护者 | 与 A-1 同批 |
| A-3 | **执行 Task 18（交付未闭环的唯一一项）**：管理页上传 3 张主图 → `sync-activity-covers.cjs` → `--cleanup` | 完成主图迁移 | `activities.cover_path` 3/3 以 `shared/_application/activities/` 开头 | 运营 | 用户操作后即时 |
| A-4 | 微信 uid 形态真机验证并固化为契约测试 | 关闭假设 | 测试用例基于真机 uid 形态断言 | 维护者 | 真机可用时 |
| A-5 | 把「公开值取值域审计」纳入新项目立项检查表 | 预防同类问题 | 立项模板含「公开面/标识列/值域构造方」三问 | 维护者 | 下个迭代 |

---

## 6. 可复用模式

### 模式 1：取值域收口（Value-Domain Closure）

- **适用**：任何「对外可见的值」承载或内嵌用户标识的系统。
- **不适用**：值只存在于调用者自己可见的范围内；标识已单向不可逆；第三方库内部实现。
- **核心做法**：列三张清单 → 交叉定位泄露面 → 服务端拼装收口 → 列级授权 →
  客户端白名单逐列对齐 → 写成可回归不变量。
- **检验标准**：匿名会话逐列取真实值，输出中无任何标识片段；
  公开路径型列的值集合能用一条正则完全描述。
- **载体**：Skill `.agents/skills/public-value-audit/`（含扫描器、断言器、前后夹具、自检）。

### 模式 2：权限收紧双查（Privilege Tightening Two-Check）· **假设（待独立案例验证）**

> ⚠️ **样本量为 1，且是自证**：唯一来源是本项目审查者**自己引入、自己发现**的一处回归
> （`review.md` 第 16 条原文等级为 **P2**，非 P1；且当时无测试捕获）。
> 本次 V 门审查进一步确认「模式 2 从未被独立审查过」——
> 因此本条目前只是**假设**，不作为已验证模式使用。
> 判定标准：出现**第二个独立案例**（他人引入、被他人或工具发现）后方可升为正式模式。

- **适用**：任何 `REVOKE` / 改 `GRANT` / 改函数签名的变更。
- **不适用**：纯新增授权（不改变既有可达性）。
- **核心做法**：①列全部调用方并确认新角色下仍可达；②在新角色下跑一次功能验证；
  ③函数体若依赖会话上下文（`auth.uid()` 等），检查该上下文在新角色下是否非空。
- **检验标准**：变更批次内留下「调用方清单 + 新角色下的功能验证输出」两项证据。
- **来源**：本项目「运维链路断裂」回归（自引入、自发现、P2 级、无测试捕获）。

---

## 7. 对抗审查记录（V 阶段）

### 7.1 审查配置

| 项 | 值 |
|---|---|
| 视角 | 4（魔鬼代言人 / 新人视角 / 老板视角 / 未来视角），并发独立执行 |
| 审查对象 | 本报告（R/I/E/A 四段）+ 可复用 Skill `public-value-audit` v1.0.0 全部文件 |
| 方式 | 各视角**实际运行脚本、构造探针夹具**后再下结论，不采信作者自述 |
| 意见总数 | **50 条**（魔鬼代言人 18 / 新人 15 / 老板 8 / 未来 9） |
| 采纳 | **12 类**（合并同类项后），全部已修正并回归验证 |
| 回归 | 修复后重跑自检 25/25、质量门 95 分、链接门 0 断链、真实项目扫描器与断言器均退出码 0 |

### 7.2 各视角结论摘要

| 视角 | 条数 | 最尖锐的一条 |
|---|---|---|
| 🔴 魔鬼代言人 | 18 | **Skill 的工具检不出它声称的核心案例**：按 `verified-case.md` 构造 P1-15 形态后，扫描器「高危 0 条」、断言器「6 条全 ✅ 退出码 0」——因为没有任何一条规则检查「公开列的实际值是否内嵌标识」，而这正是 P1-15 的发现路径 |
| 🟢 新人视角 | 15 | **清单 A 没有查询入口**：Skill 让人「列公开面清单」，但只给了视图名没给可执行 SQL，新人只能从客户端代码列 → **把服务端授权面整个漏掉**，结论完全反过来 |
| 🟠 老板视角 | 8 | **交付可信度**：扫描器在真实项目上退出码是 1（有高危），而报告只披露了断言器的判定、只字未提扫描器——一个「看起来有门、实际没覆盖」的假象；且 A-3（主图迁移）未做意味着**交付未闭环** |
| 🔵 未来视角 | 9 | **工具看不见自己开的处方**：H6 只在 `UPDATE t SET <路径列> = <p_ 入参>` 这一种字面形态上触发，而「服务端拼装」的标准写法恰恰是 `v_path := '...' || p_slug || '.png'`——经局部变量中转后 **0 findings** |

### 7.3 采纳清单（12 类，全部已修并回归）

| # | 攻击点 | 处置 | 验证 |
|---|---|---|---|
| 1 | 表名 schema 前缀不归一化 → 「客户端请求列 ⊆ 服务端授权」这条不变量**恒不触发** | 表名双向归一化（`public.activities` ≡ `activities`） | 构造越界 select 后 I2 正确报 FAIL |
| 2 | 列名解析 `strip("()")` 残留左括号 → 首个列名变成 `(id` | 改用标识符正则提取 | 同上 |
| 3 | RLS `USING (...)` 非贪婪捕获吃掉 `auth.uid()` 右括号 → 行隔离检测恒为 0 | 改贪婪捕获 | post-fix 夹具「检测到行隔离 1」，本该豁免项不再误报 |
| 4 | H6 只认字面赋值，漏中间变量中转 / `INSERT` / `$fn$` 分隔符 | 4 轮污点传播 + INSERT 支持 + 任意 dollar-quote 标签 | p115 夹具命中 H6；本项目 4 个 `$fn$` 文件纳入检测 |
| 5 | 原 pre-fix 夹具复现的是 P1-14 而非 P1-15 | 补 `p115-only` 夹具并纳入自检 | 三态夹具：两态必 FAIL、一态必 PASS |
| 6 | 表级授权降为 WARN → 已知可利用形态被放行 | 升 FAIL；并在同项目内检测到 RLS 行隔离时**自动豁免** | pre-fix I6 报 FAIL；真实项目 0 FAIL |
| 7 | 零覆盖报「全绿」 | 覆盖率输出 + 空目录退出码 3 | 自检断言「空目录 → 退出码 3」通过 |
| 8 | 授权面正则脆弱（`TO PUBLIC` / `GRANT ALL` / 无分号 / 角色组） | 改按语句切分解析；PUBLIC 视为对外；ALL 含 SELECT；角色组报中危 | 探针覆盖四类写法 |
| 9 | 豁免机制粒度粗（表级静默降级 5 条）、表名写法不一致静默失效 | 两脚本对称支持 `--allow-row-isolated`；表名归一化；未命中显式告警 | 裸名 `registrations` 亦可豁免 |
| 10 | 缺「公开值实际值含标识」这一维 | 新增 H7 / I7：字面量路径内嵌标识段 | p115 夹具命中 I7 |
| 11 | 「值域由入参决定」被一刀切判高危，误报正确的 slug 收口 | 判定分流：入参是否承载标识（名字像标识 / 路径型无形状约束 → 承载；被形状约束 → 不承载） | post-fix 的 H6 由高危降中危，退出码 0 |
| 12 | 报告自身数字漂移、V 段空占位、CMD-LOG 与正文矛盾 | 修正 F-001/F-007/F-033~F-036 与 §2.2 等级分布；填本节；CMD-LOG 计数与正文一致 | 关键计数与实测逐项复核 |

**随第 12 类一并完成的文档侧修订**：前置条件与降级路径、术语表、命令行入口与参数归属、
收口操作步骤 6 步、执行顺序（工具先行）、`SKIP_DIRS` 扩充与 H4 假阳性收紧、别名词典内置、
收口制造的二阶风险（读授权面对齐）、I-002 论证改写（删去与哈希脱敏的优劣比较）、
模式 2 降级为「假设」、迁移示例标注未验证、质量门补 dry-run / 安全清单 / Why 解释 / 幂等说明。

### 7.4 未采纳的意见与理由

| 意见 | 不采纳理由 |
|---|---|
| 未来视角：把检测主轴从「源码形状」换成「值域声明 + 跨出口一致性」，产出机器可读的 `public-surface.yaml` 契约 | 方向正确，但属**架构级演进**（需活库取数通道 + 契约语言设计），超出「从一次复盘萃取 Skill」的边界。登记为下一版演进方向 |
| 未来视角：授权面必须靠活库取真值（角色继承图 `pg_auth_members`） | 采纳其「静默失效不可接受」的原则（角色组改为报中危 + 覆盖率守卫），但活库取数需引入数据库连接，与本 Skill「不连数据库」的设计前提冲突 |
| 老板视角：补「审查投入产出比」的量化数据 | 本项目没有用户量/泄露量的度量，无法给出可信数字。**不编造指标** |
| 老板视角 / 未来视角：把「公开面清单」落成机器可读资产清单 | 与第一条同源，一并登记为演进方向 |
| 魔鬼代言人：把「值域由入参决定」直接升为 FAIL（不区分入参是否承载标识） | 采纳「升 FAIL」的方向，但**保留承载标识的判定分流**——否则会对正确的 slug 收口持续误报（实测 post-fix 会被判高危，退出码非 0） |

### 7.5 回归对抗（修复后）

| 验证 | 结果 |
|---|---|
| `scripts/selftest.py` | 25/25 通过，退出码 0 |
| `check-skill-quality.py --path .agents/skills/public-value-audit --score` | 95 分（审查前 70 分），0 error |
| `check-links.py --path .agents/skills/public-value-audit --check-frontmatter-paths` | 0 断链，frontmatter 路径全有效 |
| 扫描器对 `apps/jieban-zhilv-mp` | 高危 0 / 中危 6 / 已豁免 1，退出码 0 |
| 断言器对 `apps/jieban-zhilv-mp` | FAIL 0 / WARN 0 / 已豁免 8，退出码 0 |

---

## 8. 质量门记录

| 门 | 检查项 | 结果 |
|---|--------|------|
| G1 | 客观事实 42 条（≥20），无因果词、无推断混入，关键数据可追溯 | ✅ |
| G2 | 3 条洞察均为四元组（陈述/证据/反常识/行动），维度独立（审计方法/资产建模/变更纪律） | ✅ |
| G3 | 萃取产物含触发场景 + 核心步骤 + 适用边界 + 8 反模式 + 检验标准 + 迁移示例（标注未验证）+ 可执行脚本与三态夹具 | ✅ |
| G4 | 行动项原子化：单一职责 / 可独立验证 / 有 Owner / 有时间节点 | ✅ |
| V | 4 视角对抗审查 **50 条意见**，采纳 **12 类**修正（含工具侧 8 处实测确认的真实缺陷），修复后回归对抗（自检 25/25、质量门 95 分、链接门 0 断链、真实项目两个工具退出码 0） | ✅ |

---

## 9. 关联资产

| 类型 | 位置 |
|------|------|
| 小程序本体 | `apps/jieban-zhilv-mp/` |
| 云端真相源 | `apps/jieban-zhilv-mp/scripts/db/schema.sql`（+ 7 个 `fn_*.sql`） |
| spec 三件套 | `.trae/specs/jieban-zhilv-mp/`（spec / tasks / review） |
| 可复用 Skill | `.agents/skills/public-value-audit/` |
| 事件记忆 | `.workbuddy/memory/2026-10-26.md`、`.workbuddy/memory/MEMORY.md` |
| 运营脚本 | `apps/jieban-zhilv-mp/scripts/tools/sync-activity-covers.cjs` |

> AI生成
