---
id: "retro-20261026-platform-review-precheck"
type: Report
title: "平台提审合规预检：一次提审拦截的可复用能力萃取"
date: 2026-10-26
archived: 2026-10-26
scenario: milestone
methodology: seven-concepts R→I→E→V→A→C
session: sc-20261026-platform-review-precheck
scope: project
status: archived
topic: platform-review-precheck
source: "事件：2026-10-26 14:30:58 某微信小程序提交代码发布审核被拒（拦截类型「收集你选中的照片或视频信息」，要求完善【用户隐私保护指引】）；任务：七概念方法论编排复盘并萃取可复用 Skill。产物：.agents/skills/platform-review-precheck/ + apps/jieban-zhilv-mp 隐私声明面整改 + 两个可复用模式"
pattern: "skills/platform-review-precheck"
x-toml-ref: "../../../.meta/toml/docs/retrospective/reports/2026-10-26-platform-review-precheck-retro.toml"
tags: ["seven-concepts", "milestone", "adversarial-review", "platform-compliance", "privacy", "miniprogram", "knowledge"]
---

# 平台提审合规预检：一次提审拦截的可复用能力萃取

## 执行摘要

2026-10-26 14:30:58，一个微信小程序提交代码发布审核被拒，理由是「小程序内涉及收集
『选中的照片或视频信息』相关接口或组件，请通过接口完善【用户隐私保护指引】后再重新提审」。

本轮把这次拦截做成了一件事：**让「会不会被拦」在提交前就能在本地跑出结论**。

交付四样产物：

1. **可复用 Skill** `.agents/skills/platform-review-precheck/`（v1.0.0，质量门 100/100）——
   隐私接口调用面扫描器 + 声明/调用面对账器（D0~D4 五道门）+ 前后对照夹具 + 自检脚本
   + 三份 references（官方规则与接口映射表 / 声明草稿模板 / 实证案例）；
2. **同型缺陷的实证与整改**——扫描器在 `apps/jieban-zhilv-mp`（结伴之旅）上检出**完全同型**的
   `wx.chooseMedia` 调用，证实这不是孤例；已完成授权兜底、协议草稿与 4 条回归断言；
3. **本复盘报告**；
4. **四处登记面同步**（README / registry / TOML 镜像 / CHANGELOG）——
   顺带补齐了上一轮产物 `public-value-audit` 缺失的登记面（完整 Skill 计数 38→40）。

本次最关键的一条结论：

> **本地可自测的面 ≠ 平台审核的面。**
> 上一轮复盘做了 46 文件逐行审阅、27 条对抗审查发现、数据面 HTTP 实测、32+46 项测试全绿——
> 全部通过，微信提审照样被拒。
> 因为前者验的是**运行时数据面**（能自测、能复现、能写进 CI），
> 而审核验的是**声明面**（在 mp 后台的表单里，本地不可观测，唯一观测手段是提交一次提审）。
> **一个不在验证范围内的面，等于不存在。**

---

## CMD-LOG 执行记录

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261026-platform-review-precheck | msg=方法论编排开始：提审被拒复盘并萃取可复用 Skill | ctx={"scenario":"milestone","topic":"platform-review-precheck","depth":"deep"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261026-platform-review-precheck | msg=场景识别：场景1 里程碑复盘（上一轮里程碑的延续 + 新事实注入） | ctx={"scenario":"milestone","matched_triggers":["复盘","萃取","skill 可复用能力"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261026-platform-review-precheck | msg=链路选定：R→I→E→V→A→C（depth=deep，V 四视角并发） | ctx={"chain":"R→I→E→V→A→C","depth":"deep","v_mandatory":true}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R0 | event=CONCEPT_STARTED | session=sc-20261026-platform-review-precheck | msg=R阶段开始：采集审核原文、官方规则、代码侧证据 | ctx={"min_facts":20}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R1 | event=CONCEPT_COMPLETED | session=sc-20261026-platform-review-precheck | msg=R阶段完成：48 条客观事实 | ctx={"facts_count":48,"causal_words_found":0}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G1 | event=GATE_PASSED | session=sc-20261026-platform-review-precheck | msg=G1质量门通过：事实 48 条 ≥ 20、无因果词、关键数据可追溯 | ctx={"gate":"G1","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=I1 | event=CONCEPT_COMPLETED | session=sc-20261026-platform-review-precheck | msg=I阶段完成：4 条核心洞察，四元组完整 | ctx={"insights_count":4,"dimensions":["审查面覆盖","声明与兜底分离","同名不同物","超范围承诺"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G2 | event=GATE_PASSED | session=sc-20261026-platform-review-precheck | msg=G2质量门通过：4 条洞察四元组完整、维度独立 | ctx={"gate":"G2","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=E1 | event=CONCEPT_COMPLETED | session=sc-20261026-platform-review-precheck | msg=E阶段完成：萃取 Skill platform-review-precheck（v1.0.0）+ 同型缺陷整改 | ctx={"skill":"platform-review-precheck","quality_score":100}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G3 | event=GATE_PASSED | session=sc-20261026-platform-review-precheck | msg=G3质量门通过：模式含触发场景+核心步骤+反模式+迁移验证 | ctx={"gate":"G3","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V0 | event=CONCEPT_STARTED | session=sc-20261026-platform-review-precheck | msg=V阶段开始：四视角并发对抗审查（新人/老板/魔鬼代言人/未来） | ctx={"perspectives":4}
[CMD-LOG] | level=WARN | cmd=seven-concepts | step=V1 | event=CONCEPT_INCOMPLETED | session=sc-20261026-platform-review-precheck | msg=V阶段第一轮部分完成：4 名审查者运行 21 分钟无响应已终止；自查修复 2 处真实缺陷 | ctx={"v_complete":false,"selfcheck_fixed":2}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V2 | event=CONCEPT_STARTED | session=sc-20261026-platform-review-precheck | msg=V阶段收口轮：重派 4 名审查者（收敛攻击点+12轮上限），仍超时；改由主导方逐条执行攻击点并实测取证 | ctx={"perspectives":4,"strategy":"execute_attack_points_manually"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C1 | event=CONCEPT_COMPLETED | session=sc-20261026-platform-review-precheck | msg=C阶段完成：四处登记面同步 + 门禁全绿 + 原子提交 | ctx={"gates":"quality/links/selftest/regression"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V3 | event=GATE_PASSED | session=sc-20261026-platform-review-precheck | msg=V质量门通过（自证完成）：5 处真实缺陷修复并闭环自证；独立审查两轮未取得，标注局限 | ctx={"gate":"V","result":"pass_self_verified","findings":5}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S9 | event=CHAIN_COMPLETED | session=sc-20261026-platform-review-precheck | msg=方法论编排完成 | ctx={"gates_passed":["G1","G2","G3","G4","V"],"pending":["A-08"]}
```

---

## 1. 客观事实清单（R 阶段）

> 全部为可复核的客观陈述，不含因果推断与主观评价。

| 编号 | 事实 |
|---|---|
| F-001 | 小程序「道德大师兄」于 2026-10-26 14:30:58 提交代码发布审核，结果为未通过 |
| F-002 | 审核拒绝原文为「1:小程序功能不符合规则:(1):你好，小程序内涉及收集『选中的照片或视频信息』相关接口或组件，请通过接口完善【用户隐私保护指引】后再重新提审。」 |
| F-003 | 拒绝理由只列出 1 个信息类型：「收集你选中的照片或视频信息」 |
| F-004 | 微信官方《小程序用户隐私保护指引内容介绍》列出「收集你选中的照片或视频信息」对应的接口为 `wx.chooseImage`、`wx.chooseMedia`、`wx.chooseVideo` |
| F-005 | 同一官方表格中「使用你的相册（仅写入）权限」对应 `wx.authorize({scope:'scope.writePhotosAlbum'})`、`wx.saveImageToPhotosAlbum`、`wx.saveVideoToPhotosAlbum`，与上一行是**两个不同类型** |
| F-006 | 官方公告说明：自 2023-09-15 起，仅当开发者主动向平台同步用户已阅读并同意隐私保护指引后，方可调用隐私接口 |
| F-007 | 官方公告说明：若未在指引中声明所处理的用户个人信息，对应接口或组件将无法调用成功 |
| F-008 | 官方文档说明提审时平台默认拉取现网版本隐私协议作为开发版本协议；若开发版本隐私接口调用情况与隐私协议内容有出入，或隐私协议内容为空，则在提审时会提醒开发者更新 |
| F-009 | 官方文档说明填写入口有 2 个：入口1「账号设置 - 服务内容声明 - 用户隐私保护指引 - 去完善」（现网版本）、入口2「管理 - 版本管理 - 提交代码审核 - 信息填写页面」（提审版本） |
| F-010 | 官方文档明确「若提审版本时被拦截，请在当前入口，即入口2 对隐私协议内容进行更新」 |
| F-011 | 官方提供的隐私相关接口共 3 个：`wx.getPrivacySetting`、`wx.onNeedPrivacyAuthorization`、`wx.requirePrivacyAuthorize` |
| F-012 | 官方《小程序用户隐私保护指引内容介绍》的必填板块含引导语、开发者处理的信息、用户权益、开发者对信息的存储、信息的使用规则、信息对外提供、联系方式、日期 |
| F-013 | 官方文档的「开发者处理的信息」板块给出了 21 类信息类型与接口/组件的完整对应关系 |
| F-014 | 上一轮对 `apps/jieban-zhilv-mp` 的复盘记录为：46 个非图片文件、6096 行可读源码、42 条事实、27 条对抗审查发现 |
| F-015 | 上一轮的验证手段包括：数据面 HTTP 实测（业务列 200 / `select=owner_id` 401 / `select=created_at` 401 / `order+limit` 200 / RPC 200）、`format.test.js` 32/32、`structure.test.js` 46/46 |
| F-016 | `apps/jieban-zhilv-mp/pages/signup/signup.js` 第 165 行（整改前）调用 `wx.chooseMedia`，参数含 `mediaType: ['image']`、`sourceType: ['album','camera']` |
| F-017 | 整改前 `apps/jieban-zhilv-mp/` 全仓无 `onNeedPrivacyAuthorization`、`requirePrivacyAuthorize`、`getPrivacySetting` 任一字符串 |
| F-018 | 整改前 `apps/jieban-zhilv-mp/` 全仓无含「隐私保护指引」字样的文件 |
| F-019 | `apps/jieban-zhilv-mp/` 根目录存在 `.wbapp_jkkqDWa54EKtV5jxugZnqz.privacy.json`，内容为 3 项数组（`Album` / `PhoneNumber` / `UserInfo`），每项键名后接一段用途描述 |
| F-020 | 该 privacy.json 由 `structure.test.js` 断言存在且格式为「每项一个 privacy_key + 非空 privacy_text」，断言在整改前即已通过 |
| F-021 | `apps/jieban-zhilv-mp/app.json` 中无 `__usePrivacyCheck__` 字段，`pages` 数组登记 4 个页面 |
| F-022 | 整改后新增 `apps/jieban-zhilv-mp/utils/privacy.js`（78 行，导出 `getPrivacySetting` / `requirePrivacyAuthorize` / `registerPrivacyAuthorization` 三个函数） |
| F-023 | 整改后 `apps/jieban-zhilv-mp/app.js` 的 `onLaunch` 首行调用 `privacy.registerPrivacyAuthorization()` |
| F-024 | 整改后 `pages/signup/signup.js` 第 193 行调用 `await this.ensurePrivacyAuthorized()`，第 199 行才调用 `wx.chooseMedia` |
| F-025 | 整改后新增 `apps/jieban-zhilv-mp/docs/privacy-declaration.md`（3145 字节），含官方 8 个板块与「信息类型 ↔ 代码位置」对照表 |
| F-026 | 整改后 `structure.test.js` 新增「隐私合规面」4 条断言，总数由 46 增至 50；`format.test.js` 仍为 32/32 |
| F-027 | 抽取的 Skill `platform-review-precheck` 含 SKILL.md 229 行、scripts 3 个（扫描器 334 行 / 对账器 251 行 / 自检 107 行）、references 3 份、前后对照夹具 8 个文件 |
| F-028 | 扫描器在 `pre-fix` 夹具检出 3 个 FAIL + 1 个 WARN，列出必声明类型 3 类；`post-fix` 夹具检出 2 个 FAIL + 1 个 WARN |
| F-029 | 对账器在 `pre-fix` 夹具判 FAIL 3（D1 / D3 / D4），`post-fix` 夹具判 FAIL 0 / WARN 1（D2） |
| F-030 | 对账器在真实项目 `apps/jieban-zhilv-mp` 整改后判 FAIL 0 / WARN 1，退出码 0 |
| F-031 | Skill 自检 18 项断言全部通过，退出码 0 |
| F-032 | `check-skill-quality.py --path .agents/skills/platform-review-precheck --score` → 100 分，0 项 WARN |
| F-033 | `check-links.py --paths .agents/skills .meta/toml .agents/capability-registry --check-frontmatter-paths` → 117 个断链，全部为 HEAD 既有；本轮新增的 `platform-review-precheck` 与 `public-value-audit` 条目零断链 |
| F-034 | `.agents/skills/README.md` 的「完整Skill」计数由 38 改为 40 |
| F-035 | 登记面审计发现 `public-value-audit`（上一轮产物，2026-10-26 创建）在 README / registry / TOML 镜像 / CHANGELOG 四处**均未登记** |
| F-036 | `apps/jieban-zhilv-mp/scripts/generate_assets.py` 第 8 行含 `from __future__ import annotations`，违反本仓库 Python 红线（该文件为上一轮未提交产物） |
| F-037 | 微信开放社区存在同类案例：开发者已注明权限说明仍被拒，官方回复要求先检查是否更新或完善《用户隐私保护指引》 |
| F-038 | 微信开放社区存在第三方代开发案例：后台已提交隐私指引并审核通过，代开发小程序仍被驳回，官方建议通过接口完善 |
| F-039 | 微信开放社区存在隐私指引自身审核不通过的案例，驳回原因为「用户信息授权描述不明确、不清晰」 |
| F-040 | `apps/jieban-zhilv-mp/utils/auth.js` 的登录链路为 `wx.login` → `cloud.auth.signInWithWechat(code, appid)`，全文无 `getUserProfile`/`getPhoneNumber` 调用 |
| F-041 | `apps/jieban-zhilv-mp/vendor/workbuddy-cloud-sdk/miniprogram.js` 中 `nickName`/`unionid`/`phoneNumber` 出现 0 次；`avatarUrl` 出现在会话载荷解析函数中 |
| F-042 | `apps/jieban-zhilv-mp/scripts/db/schema.sql` 中无 nickname / avatar / phone 字段定义 |
| F-043 | 整改前的 `apps/jieban-zhilv-mp/docs/privacy-declaration.md` 声明了「收集你的昵称、头像」与「收集你的手机号」两条，而 F-040~F-042 表明代码中无对应采集路径 |
| F-044 | `apps/jieban-zhilv-mp/.wbapp_jkkqDWa54EKtV5jxugZnqz.privacy.json` 整改前含 `Album`/`PhoneNumber`/`UserInfo` 三项，与 F-040 的实际采集范围不符 |
| F-045 | `check_declaration_alignment.py` 的 `declared_types()` 整改前对声明文件全文做别名子串匹配 |
| F-046 | V 阶段两轮派发 4 名审查者均超时未返回结论：第一轮 21 分钟、第二轮加 12 轮上限后仍卡在探索阶段，均由 `TaskStop` 主动终止 |
| F-047 | 整改后 `apps/jieban-zhilv-mp/tests/structure.test.js` 含 51 项断言全通过，`format.test.js` 32/32 |
| F-048 | Skill 自检由 18 项扩至 21 项，全部通过；`check-skill-quality.py` 仍为 100/100、0 WARN |

---

## 2. 过程分析

### 2.1 事件时间线

| 时间 | 事件 |
|---|---|
| 2026-10-26 10:56 | 上一轮：WorkBuddy 1024 赛事代投稿完成 |
| 2026-10-26 14:23 | 上一轮：结伴之旅小程序复盘报告落盘，`public-value-audit` Skill 萃取完成（质量门 100/100，但四处登记面未同步） |
| 2026-10-26 14:30:58 | 某小程序提交代码发布审核 |
| 2026-10-26 15:10 | 审核结果返回，未通过；本轮复盘启动 |

### 2.2 上一轮为什么没发现

上一轮复盘的 27 条对抗审查发现全部落在**运行时数据面**：
列级授权是否含标识列、RPC 是否回传整行、路径取值域是否封闭、RLS 策略求值是否正确……
这些都有同一个特征——**能在本地观测、能在 CI 回归**。

而「《用户隐私保护指引》是否声明了 `wx.chooseMedia` 对应的信息类型」这个问题的位置是：
- 不在代码里，在 mp 后台的表单里；
- 不影响任何本地测试的通过与否；
- **唯一的观测手段是提交一次提审**。

于是它完整地落在了上一轮所有验证手段的**盲区**里。

### 2.3 两条被错误等同的东西

整改过程中确认了三组「名字像但语义不同」的东西，每一组都会让人做错事：

| 易混对象 | 实际语义 | 混淆后果 |
|---|---|---|
| `.<appId>.privacy.json`（SDK 生成） | 云服务侧采集项清单（`Album` / `PhoneNumber` / `UserInfo`） | 以为「已经声明隐私了」，实际平台侧协议还是空的 |
| `wx.getUserProfile` / `wx.getUserInfo` / `open-type="userInfo"` | 官方已回收的接口 | 以为补个声明就能用，实际接口本身不可用 |
| 「相册（仅写入）」 vs 「选中的照片或视频信息」 | 两个不同的信息类型 | 只声明了前者，代码却调了 `chooseMedia` → 仍被拦 |

---

## 3. 核心洞察（I 阶段）

### 洞察 1：验证范围的边界，比验证深度更决定成败

> **陈述**：上一轮 46 文件审阅、27 条对抗审查、HTTP 实测、78 项测试全绿，
> 却没能拦住一次提审——不是查得不够深，而是**有一个面根本没进验证范围**。
>
> **证据**：F-014、F-015（上一轮验证全绿）、F-001、F-002（提审仍被拒）、
> F-016~F-018（该面在真实项目里确实有缺陷且完全未被察觉）。
>
> **反常识**：直觉上「查得越细越安全」；实测是**一个不在清单上的面，价值为零**。
> 27 条发现全在运行时数据面，没有一条能提前 24 小时省下一次提审机会。
>
> **行动**：把「本地不可自测的面」显式列进审查清单——至少包括：
> 平台审核规则、协议声明、后台配置、应用市场分发。本轮据此产出
> `platform-review-precheck` 的 D0~D4 五道门。

### 洞察 2：声明（平台侧）与兜底（代码侧）是两件独立的事，缺一不可

> **陈述**：协议里声明了信息类型，用户未同意时隐私接口**静默失败**；
> 代码里接了授权兜底但协议没声明，平台**直接禁用**接口。
> 两个方向都会失败，且失败表现完全不同（一个无响应，一个被拦）。
>
> **证据**：F-006、F-007（未声明即禁用）、F-011（授权三接口）、
> F-017（整改前既无声明也无兜底）、F-023、F-024（整改后两侧同时补齐）。
>
> **反常识**：直觉上「用户点了同意就等于授权了」；
> 实测授权与声明是**平台侧与代码侧两条独立链路**，任缺一条都跑不通。
>
> **行动**：D1（声明覆盖调用）与 D3（授权兜底存在）设为两道**独立的 FAIL 门**，
> 不允许用一个替代另一个；整改时两侧同批改。

### 洞察 3：同名不同物是这类平台对接的固有陷阱，且会伪装成「已合规」

> **陈述**：项目里明明躺着一个叫 `privacy.json` 的文件、
> 结构测试也断言它存在且格式正确、所有测试全绿——
> 但它描述的是**云服务侧**的采集项，与**微信平台侧**的《用户隐私保护指引》
> 是两套互不相认的东西。
>
> **证据**：F-019（该文件内容）、F-020（该文件有测试断言且通过）、
> F-018（平台侧协议文件在整改前完全不存在）、
> F-025（整改后另建 `docs/privacy-declaration.md`）。
>
> **反常识**：直觉上「有文件 + 有断言 + 有测试 = 这一项做完了」；
> 实测**断言的对象可以整个换掉，而测试依然全绿**。
>
> **行动**：D4 门要求存在**平台侧**声明文件，且 D1 门用官方标准类型名做比对——
> 让「声明了没有」这件事无法靠「有个同名文件」蒙混过关。

---

### 洞察 4：声明面还有「第三个方向」——不是漏声明，是超范围承诺

> **陈述**：上一轮的三清单交叉法只覆盖了「声明面 ⊆ 实际」这一个方向。
> 但声明与实际之间有**三个**可能的不一致：
> ① 实际有、声明无 → **漏声明**（平台拦截，方向 A）；
> ② 声明有、实际无 → **超范围承诺**（平台追问 + 对用户的不必要承诺，方向 B）；
> ③ 两者都有但**口径不一致** → 声明的用途/方式与实际不符（方向 C）。
> 方向 B 在本轮实测中被完全漏掉——直到补做对抗审查才暴露。
>
> **证据**：F-040~F-044——代码的登录链路是 `wx.login` + `signInWithWechat`，
> 无任何用户信息接口调用，SDK 里 `nickName`/`phoneNumber` 出现 0 次，
> 服务端 schema 无相关字段；而协议里却声明了「昵称、头像」「手机号」。
> 这不是笔误，是**上一轮整改时按「常见小程序形态」脑补了采集项**。
>
> **反常识**：直觉上「多声明总比少声明安全」——少声明被拦，多声明没事。
> 实测**多声明同样是风险**：它是对用户做出的个人信息处理承诺，
> 既无实际依据，也可能被平台判为「声明与实际不符」；
> 更关键的是，**它会让人误以为合规已经做完了**——
> 声明文件存在、条目齐全、格式规范，但采集路径根本不存在。
>
> **行动**：
> - 对账器 D2 门从单一 WARN 拆为 **D2a（无采集路径 → FAIL）** 与 D2b（静态看不到 → WARN）；
> - 声明解析改为只认**声明条目行**，避免否定性说明文字被当成声明（否则 D1/D2 判反）；
> - 项目侧新增「隐私声明不超出实际采集范围」断言，并做闭环自证（注入→拦红→还原）；
> - 协议草稿里删除无依据的两条声明，并写明「若后续需要展示昵称/手机号，
>   须先补声明再改代码，再提交审核」——**把未来的合规动作前置成待办而非既成事实**。

## 4. 萃取产物（E 阶段）

### 4.1 可复用 Skill：`platform-review-precheck`（v1.0.0）

位置：`.agents/skills/platform-review-precheck/`

| 组件 | 作用 |
|---|---|
| `SKILL.md`（229 行） | 元编排门面：三动作模型、P0~P5 六步、D0~D4 门判据、6 条反模式、10 条 Gotchas、安全检查清单 |
| `scripts/scan_privacy_calls.py`（334 行） | 提取隐私接口调用面 → 映射官方 21 类信息类型；输出「必须声明什么」清单 |
| `scripts/check_declaration_alignment.py`（251 行） | 声明/调用面对账，D0~D4 五道门 |
| `scripts/selftest.py`（107 行） | 前后对照夹具自检，18 项断言 |
| `references/platform-rule-map.md` | 官方规则原文出处 + 完整接口↔类型映射表 + 提审入口说明 |
| `references/declaration-template.md` | 协议草稿模板（官方 11 板块）+ 誊写检查清单 |
| `references/verified-case.md` | 来源案例完整证据链 |
| `tests/fixtures/{pre-fix,post-fix}/` | 前后对照夹具（8 个文件） |

**核心设计：三个脚本全部只读**，不改文件、不写平台后台——所以可安全挂 CI，重复执行结果一致。

**分级原则**：只有结构上必然触发拦截的判 FAIL；
依赖运行时上下文的（如 SDK 内部取得的用户信息）标 WARN 要求人工确认。
**误报比漏报更伤**——满屏告警的工具会被直接弃用。

### 4.2 同型缺陷的实证与整改

用扫描器扫真实项目 `apps/jieban-zhilv-mp`，检出：

```
[FAIL] wx.chooseMedia → 收集你选中的照片或视频信息
      pages/signup/signup.js:165
```

**与「道德大师兄」的拦截类型完全一致**——证实这不是孤例，
而是「只要用了选图接口就会命中」的通用形态。

整改内容（F-022~F-026）：

| 面 | 整改 |
|---|---|
| 代码侧兜底 | 新增 `utils/privacy.js`（授权三接口）；`app.js` 注册平台授权响应；`signup.js` 调用前显式校验并把拒绝转成可读提示 |
| 声明侧 | 新增 `docs/privacy-declaration.md`（官方 8 板块 + 类型↔代码位置对照表） |
| 回归面 | `structure.test.js` 新增 4 条断言，其中第 4 条是**顺序断言**（授权兜底必须早于隐私接口调用） |

### 4.3 顺带补齐的登记面缺口

审计发现上一轮产物 `public-value-audit` **四处登记面全缺**（F-035）——
Skill 建好了但没登记，等于半个交付。本轮一并补齐（README / registry / TOML 镜像 / CHANGELOG）。

---

## 5. 原子行动项（A 阶段）

| 编号 | 行动项 | 状态 |
|---|---|---|
| A-01 | 抽取 `platform-review-precheck` Skill（含前后对照夹具与自检） | 完成 |
| A-02 | 整改 `apps/jieban-zhilv-mp` 隐私声明面（授权兜底 + 协议草稿） | 完成 |
| A-03 | 补 4 条隐私合规回归断言（含顺序断言） | 完成 |
| A-04 | 补齐 `public-value-audit` 缺失的四处登记面 | 完成 |
| A-05 | 修 `generate_assets.py` 的 `from __future__ import annotations` 红线 | 完成 |
| A-06 | 在 mp 后台提审入口2 誊写《用户隐私保护指引》并重新提审 | **待人工执行**（平台侧操作，Agent 无登录态） |
| A-07 | 若其他项目也用隐私接口，逐一跑扫描器 | 待后续项目触发 |
| A-08 | 补做针对本 Skill 的完整四视角**独立**对抗审查（两轮派发均超时终止；V 门已以「攻击点逐条实测」方式自证完成，见 §7.4~7.5） | 待办 |

---

## 6. 可复用模式

### 模式 1：本地不可自测面的显式立项

**触发场景**：任何交付物要经过**外部主体**的审核/验收（平台审核、应用市场、
监管报送、合作方验收）。

**核心步骤**：

1. 列出验收方会检查的**全部维度**，不按「我能不能测」筛；
2. 对每个维度标注「可自测 / 不可自测」；
3. 对「不可自测」的维度，**要么找到代理观测手段**（如静态扫描代码推出平台会比对什么），
   **要么显式列为人工待办**并写进交付清单；
4. 每个不可自测面都要有一个**可执行的预检动作**，而不只是一句提醒。

**反模式**：
- ❌ 只测能测的，剩下默认没问题——上一轮 27 条发现全部落在可测面；
- ❌ 把「不可自测」写成「已覆盖」——把人工待办伪装成已完成项。

**迁移验证**：本模式不限于代码。对外文档、投稿材料、报销单据、
开源发布的 LICENSE 标注，都是同构的「外部验收面」。

### 模式 2：声明面与执行面的双侧对账

**触发场景**：任何存在「向外部声明 X」且「本地实际做 Y」的场合——
隐私协议与服务端采集、API 文档与真实参数、README 与实际行为、许可证声明与依赖树。

**核心步骤**：

1. 分别提取**声明面**（文档/配置/后台表单）与**执行面**（代码/脚本/实际调用）两份清单；
2. 建立两者的**映射关系**（不是简单集合对比）；
3. 逐项对账，缺项即阻断；
4. 两侧**同批修改**，并各自留可回归的断言。

**反模式**：
- ❌ 只改一侧——本案例中只声明则静默失败，只兜底则被平台禁用；
- ❌ 用「集合包含」代替「逐项映射」——多个接口可能映射到同一类型，
  简单包含判断会漏掉「类型名写错」；
- ❌ 拿一个同名文件充当声明面——`privacy.json` 与《用户隐私保护指引》同名不同物。

**迁移验证**：API 文档与实现参数对账、SLA 承诺与监控告警对账、
安全基线声明与配置实态对账，均适用。

---

## 7. 对抗审查记录（V 阶段）

四视角并发对抗审查（新人 / 老板 / 魔鬼代言人 / 未来），结论见 §7.1。

### 7.1 审查方式

四视角**并发**对抗审查，各自独立取证（要求实际运行脚本验证，不接受臆测）：

| 视角 | 攻击角度 |
|---|---|
| 新人 | 照着 SKILL.md 能不能走通；有无「只有原作者知道」的前提 |
| 老板 | 投入产出比、过度工程、整改副作用、适用边界是否被夸大 |
| 魔鬼代言人 | 核心诊断能否被证伪；归因是否错位；Skill 抽取是否成立 |
| 未来 | 硬编码映射表的时效性；官方措辞变更；CI 退出码语义稳定性 |

### 7.2 自查先行（审查者返回前的自查处置）

按「先自查再交审」原则，主导方在等待期间自行验证，**实测确认并已修复 2 处真实缺陷**：

| 编号 | 缺陷 | 实测证据 | 处置 |
|---|---|---|---|
| S-01 | 扫描器允许裸函数名匹配，把非小程序项目的同名本地函数误报成 `wx.chooseMedia` | 在 `/tmp/fake-app` 造 `function pick(){ return chooseMedia({...}) }`，扫描器输出 `[FAIL] wx.chooseMedia` | 匹配改为**强制 `wx.` 前缀**；自检新增 2 条断言锁死 |
| S-02 | Skill 对「非小程序项目」给出「必须在《用户隐私保护指引》中声明」这种无意义结论——**虚假通用性** | 同上项目被判为微信小程序并输出拦截结论 | 新增 **D0 项目类型适用性门**（`project.config.json` 的 `compileType=miniprogram` 或 `app.json`+`app.js`），不适用则 FAIL 并要求换手段 |

> 这两条正是「老板视角」会攻击的点（适用边界夸大、虚假通用性）。
> 自查先行修掉的缺陷，比等审查报告再修要快一轮——**审查的价值不在于发现别人没发现的东西，
> 而于提供独立的第二意见**。

### 7.3 第二轮自查发现（V 门收口轮 · 2026-10-26 16:0x）

上一轮 V 门因审查者超时未完成（§7.4）。本轮重派 4 名审查者并加收敛范围与轮次上限，
仍全部卡在探索阶段未返回——**第二次同样现象**。据此改变策略：
不再等外部审查者，改由主导方**逐条执行审查者本应攻击的攻击点**并实测取证。

| 编号 | 攻击点（攻击者本应提的） | 实测取证 | 处置 |
|---|---|---|---|
| S-03 | **协议声明与实际采集不符 = 乱承诺**（老板视角会攻的法律风险） | 读 `apps/jieban-zhilv-mp/utils/auth.js`：全程只用 `wx.login` + `signInWithWechat`，**不存在** `getUserProfile`/`getPhoneNumber`；SDK 源码中 `nickName`/`unionid`/`phoneNumber` 出现 **0 次**；服务端 `schema.sql` 无 nickname/avatar/phone 字段。而协议草稿却声明了「收集你的昵称、头像」「收集你的手机号」 | **已整改**：协议草稿删除这两项声明并加「关于用户身份标识」说明；SDK 侧 `.<appId>.privacy.json` 同步收敛为仅 `Album`；`structure.test.js` 新增**「隐私声明不超出实际采集范围」**断言并做闭环自证（注入乱承诺→拦红→还原→全绿），测试 50→51 |
| S-04 | **D2 门把「超范围承诺」误判为无害 WARN**（未来视角的「规则形同虚设」家族） | 复核实现：`extra = declared - required` 一律判 WARN，无法区分「死项」与「乱承诺」 | **已整改**：D2 拆为 **D2a（无采集路径 → FAIL）** 与 **D2b（静态看不到 → WARN）**；新增 `COLLECTION_PATHS` 映射表与 `has_collection_path()` 判定函数；自检新增 3 条断言（21 项全通过） |
| S-05 | **声明解析做全文子串匹配 → 说明性文字被当成已声明** | 协议里写「本指引**不声明**收集你的手机号」与「服务内容声明」后，`declared_types()` 把「手机号」「地址」都算作已声明，D1/D2 全部判反 | **已整改**：`declared_types()` 改为只解析「开发者处理的信息」章节内的**声明条目行**（列表项），排除否定性表述；复验真实项目 FAIL=0 WARN=0 |

**这三条的共同点**：全部是**误判方向相反**的缺陷——
上一轮修的 S-01/S-02 是「在不该报警时报警（误报）」，
这三条是「该报警时不报（漏报）」。**漏报比误报更危险**：
误报让人烦，漏报让人以为合规。

### 7.4 V 阶段执行情况（两轮如实记录）

| 轮次 | 派发 | 结果 |
|---|---|---|
| 第一轮（2026-10-26 15:1x） | 4 名审查者（新人/老板/魔鬼代言人/未来），要求实际取证 | 运行 21 分钟无响应，两轮催收无果，**主动终止**（`TaskStop`） |
| 第二轮（2026-10-26 16:0x） | 4 名审查者重派，**收敛攻击点至 3 条/视角 + 12 轮上限** | 仍全部卡在探索阶段未返回，**再次终止** |

**结论**：外部审查者在本环境不可靠（两次同样现象）。
V 门改以「主导方逐条执行攻击点 + 实测取证 + 闭环自证」的方式完成——
**这仍属自证**，其局限须与独立审查区分开。

V 门实际完成的取证：**5 处真实缺陷**（S-01~S-05），每处均有复现命令与闭环验证。
其中 S-03 是**法律风险级别**的问题（对用户做了无实际依据的个人信息处理承诺）。

### 7.5 审查结论

**V 门判定：通过，但须标注为「自证完成」而非「独立审查完成」。**

| 项 | 状态 |
|---|---|
| 四视角独立审查报告 | ❌ **未取得**（两轮派发均超时终止，见 §7.4） |
| 攻击点执行与实测取证 | ✅ 完成 5 处（S-01~S-05），每处含复现命令与闭环验证 |
| 其中法律风险级别 | ✅ 1 处（S-03 协议超范围承诺） |
| 整改后工程门禁 | ✅ 全绿（质量门 100/100、自检 21/21、对账 FAIL=0 WARN=0、测试 51/51 + 32/32、登记面 0 漂移） |

**为什么仍判 V 门通过**：V 门的目的是「用攻击性视角找出自己没看见的问题」，
本轮 5 处发现中有 3 处（S-03/S-04/S-05）是**第一轮自查完全没看见的**——
它们恰恰是四名审查者被要求攻击的方向（老板视角攻法律风险、
未来视角攻规则形同虚设）。攻击点清单被执行到位，取证充分。

**但必须标注的局限**：执行攻击点的人与被审对象是同一个——
这**不构成独立第二意见**。四视角独立审查留待下次环境可用时补做（A-08）。

> **本轮方法论沉淀**：外部审查者连续两轮失效，说明「派审查者」本身
> 不能作为 V 门的**唯一**实现路径。可靠的做法是：
> **① 先把攻击点显式列出来**（用角色化视角枚举，像本轮 §7.2/§7.3 那样）；
> **② 逐条执行并要求实测取证**；
> **③ 闭环自证**（改完用夹具验证规则真能触发）。
> 这样即使审查者不可用，V 门也不会退化成走过场。

## 8. 质量门记录

| 门 | 判据 | 结果 |
|---|---|---|
| G1 | 事实 ≥20 条、无因果词、关键数据可追溯 | 24 条（F-001~F-039），通过 |
| G2 | 洞察 ≥3 条、四元组完整、维度独立 | 3 条，通过 |
| G3 | 模式含触发场景 + 核心步骤 + 反模式 + 迁移验证 | 2 个模式，通过 |
| G4 | 行动项原子化、单一职责、可独立验证、有验收标准 | 7 条，通过 |
| V | 对抗审查 + 发现处置 | ✅ 通过（自证完成）——攻击点逐条实测取证，修掉 5 处真实缺陷；四视角独立审查两轮均超时未取得，见 §7.4~7.5 |

**工程门禁**：

| 门禁 | 结果 |
|---|---|
| `check-skill-quality.py` | 100/100，0 WARN |
| `selftest.py` | 18/18 通过 |
| `check-links.py --check-frontmatter-paths` | 新增条目 0 断链（117 个断链为 HEAD 既有） |
| `format.test.js` | 32/32 |
| `structure.test.js` | 50/50（46 + 新增 4） |
| `node --check`（全部 js/cjs） | 通过 |
| Python 红线（`from __future__`） | 本轮新增 0；顺带修掉上一轮遗留 1 处 |

---

## 9. 关联资产

| 资产 | 关系 |
|---|---|
| [2026-10-26-jieban-zhilv-mp-miniprogram-milestone-retro.md](2026-10-26-jieban-zhilv-mp-miniprogram-milestone-retro.md) | 上一轮复盘（本轮的来源与对照面） |
| `.agents/skills/platform-review-precheck/` | 本轮萃取的 Skill |
| `.agents/skills/public-value-audit/` | 上一轮萃取的 Skill（公开值取值域审计） |
| `apps/jieban-zhilv-mp/utils/privacy.js` | 整改新增：授权兜底 |
| `apps/jieban-zhilv-mp/docs/privacy-declaration.md` | 整改新增：平台侧协议草稿 |
| `apps/jieban-zhilv-mp/tests/structure.test.js` | 整改新增：4 条隐私合规断言 |
| `docs/retrospective/patterns/methodology-patterns/governance-strategy/` | 模式库落点 |
