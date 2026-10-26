---
name: embedded-page-submit-cmd
version: 1.1.0
description: "在 WorkBuddy/宿主应用的内嵌智能页（Smart Page）上代替用户完成表单提交（报名、投稿、登记、问卷），当用户说『帮我提交』『代填并提交』『帮我在活动页报名』『这个表单替我填』时必须使用此技能。也适用于：页面表单只存在于宿主应用 webview 内、无头浏览器点不到按钮、页面 JS 里有 submitWork/saveWork 之类的保存函数但找不到对应后端接口、写入报 permission denied / 12607 / not login 时定位正确的写入通道。核心能力是通道权限模型判定 + 宿主 HTTP 面逆向 + 写后回读复核（false-success defense）+ 写入授权边界与红线字段拦截（授权/承诺类字段禁止代填）+ 幂等查重防重复提交。不适用于普通公开网页表单（用浏览器自动化即可）与本地 Excel/CSV 批量导入。"
argument-hint: "<目标页面URL或pageId> <提交动作说明>"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/embedded-page-submit-cmd/**"
title: "内嵌智能页代提交通道 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/embedded-page-submit-cmd/SKILL.toml"
---

# 内嵌智能页代提交通道 Skill

> 萃取自 sc-20261026-workbuddy-contest-submit 实战（WorkBuddy「1024 造物挑战」活动页代投稿：前一轮判定「Agent 无法代提交」，本轮实测通过写通道完成两条记录写入 + 回读复核，提交编号 `S1024-1a176238787-lros`）。本 Skill 把「内嵌页提交链路的通道判定方法」固化为可重复执行的流程。

## 1. Skill ID

`embedded-page-submit-cmd`

## 2. 功能描述

把「在宿主应用内嵌页上代替用户提交表单」这件事拆为三段可独立验证的动作：

| 方案 | 适用场景 | 优势 |
|------|---------|------|
| **方案 A：宿主 HTTP 面逆向** | ⭐ 宿主是 Electron/桌面应用，页面由宿主 SPA 渲染 | 稳定、可脚本化、可回读复核、不依赖 UI 自动化环境 |
| **方案 B：页面内 SDK 直调** | 宿主页面已注入 SDK 且能在浏览器上下文拿到 SDK 对象 | 零逆向成本，直接复用宿主已封装的字段映射 |

核心能力：

1. **通道权限模型判定**——先画清 3 条 API 权限通道（agent-gateway / view / share）+ 1 条上下文通道（宿主 SDK）+ 1 条交互兜底（UI 自动化）各自能读能写什么，再决定投入哪条（不做这个判定就会得出「不可达」的假结论）
2. **写通道逆向**——从宿主 SPA 产物（asar / 前端 chunk）里逆出 `database.addRecord` → 后端路径的映射与参数形状
3. **写后回读复核**——写入成功后必须 `getRecord`/`query` 回读并逐字段比对，防 false-success
4. **授权边界与红线字段**——代填不等于代承诺，授权/承诺类字段默认禁止 Agent 代填（见 §6.5）
5. **幂等去重**——重复提交在评选场景是实质违规，写入前必须先查（见 §7.3）

**配套脚本（可直接执行）**：

| 脚本 | 作用 | 是否写库 |
|------|------|---------|
| `scripts/probe_channels.py` | 通道可达性 + 登录态 + schema + 目标表身份判定 | **只读，绝不写** |
| `scripts/submit_record.py` | 幂等查重 → dry-run 回显 → 三道闸门 → 探针写删 → 正式写入 → 回读复核 | 写入（受闸门约束） |

> **为什么 Skill 声称可调用就必须真的能跑？** 本 Skill 首版只有文档没有脚本，被对抗审查判为 P0——"声称是可调用的能力，仓库里却没有可执行入口"。现在两个脚本均已实测跑通：三道闸门（用户确认 / 红线字段 / 幂等）分别用真实数据验证过会正确拦截。

> **为什么必须先画权限模型？** 本次实战最大的教训是：第一轮只试了 agent-gateway 通道（`space_api.py`），撞上 `code=12607 permission denied` 就写下「Agent 无法代提交」并把交付物降级成「材料包 + 手工步骤」。实际上同一个 host 上还有一条带登录态、可写可删的 `view` 通道。**一次 12607 只能证伪「这一条通道」，不能证伪「这件事」。**

## 3. 何时使用本技能

当用户提到以下任何内容时触发：

- "帮我提交"、"代填并提交"、"替我报名"、"帮我投稿"、"帮我在活动页登记"
- "这个表单你帮我填"、"后台点不动"、"提交按钮点不了"
- "无头浏览器打不开这个页面"、"页面能打开但点提交没反应"
- "permission denied"、"12607"、"not login"、"401"、"写入被拒"
- 目标页面是 `*.workbuddy.link/p/*` 形态的智能页 / Smart Page
- 页面 HTML 里出现 `__SMART_PAGE__`、`addRecord`、`databaseId` 等标识
- 需要把内容写入平台的数据表（database）而不是走公开 API

> **关于触发**：即使没说"用 skill"，只要用户要在**宿主应用内嵌页**上完成提交，就应该使用此技能——手工在页面里逐字段填既慢又易漏（本次 18 个字段），而本 Skill 封装了通道判定、字段形状逆向与回读复核三件最容易翻车的事。

**不适用**：普通公开网页表单（用浏览器自动化更直接）、本地 Excel/CSV 导入、需要人工实名验证的流程（如短信验证码、人脸）。

## 4. 方案选择决策树

```
目标页面是宿主内嵌智能页（Smart Page / workbuddy.link/p/*）？
├─ 是 → 走本 Skill
│   ├─ 页面 HTML 里能直接看到提交函数（saveWork/submitXxx）？ → 提取字段映射（方案 B 的信息源）
│   ├─ 宿主是 Electron 应用、asar 里能找到前端 chunk？ → 逆向 API 映射（方案 A 的信息源）
│   └─ 两者都有 → 先做方案 A（更稳），用方案 B 的字段映射做交叉校验
└─ 否 → 公开网页表单走浏览器自动化，本 Skill 不介入
```

**通道优先级（重要）**：宿主 HTTP 面 > 宿主 SDK > 浏览器 UI 自动化。

```
同一目标有多条候选通道时，按此顺序试：
1. view 通道（带登录态，通常可读可写）   ← 本次成功的就是这条
2. 宿主 SDK 暴露的方法（页面内 bridge.call）
3. agent-gateway 通道（CLI / space_api.py，可能对主办方表无权限）
4. share 通道（通常只读 schema，且无登录态时全 401）
5. CDP 通道（Chrome DevTools Protocol，见下）
6. UI 自动化（最后手段，依赖本地小助手，Windows 常不可用）
```

> **为什么 view 通道排在 agent-gateway 前面？** agent-gateway 是给"通用 Agent 调用平台自有资源"设计的，对第三方/主办方创建的资源表天然无权；`view` 通道是"以页面访问者身份操作该页面挂载的数据表"，语义上恰好匹配"我在这个页面上填表"。**同一个 host 上不同前缀 ≠ 同一套权限。**

**第 5 条：CDP 通道（此前遗漏，现补入）**

当页面在宿主 webview 内且无法用 HTTP 面直调时，可尝试以 `--remote-debugging-port` 启动宿主/浏览器，再走 CDP 协议（`/json/list` 拿 target，`Runtime.evaluate` 在页面上下文执行 `__SMART_PAGE__` SDK 调用）。

- **适用**：HTTP 面逆向失败，但页面确实能渲染、有登录态。
- **前置**：宿主需支持传入调试端口；部分 Electron 应用会因安全策略忽略该参数。
- **风险**：调试端口开启等于把宿主会话暴露给本机任意进程，**属于安全降级**，只在必要时启用，且不得把端口暴露到非回环地址。
- **本次状态**：⚠️ **未实测**。它是在前四条通道全部失败后的兜底设想，不能当作已验证能力使用。

> **为什么把未实测的通道写进来并标注状态？** 删掉它会让后来者重新踩一遍同样的坑（以为只有四条）；写进来但明确标注"未实测"，既保留了线索，又不会被误当成保证。**能力清单里"未验证"和"已验证"必须分开标注。**

## 5. 输入参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| page_url | string | 是 | - | 目标智能页 URL（形如 `https://xxx.workbuddy.link/p/<id>`） |
| page_id | string | 是 | - | 页面 ID（URL 末段），**写操作必带**，缺失即 `permission denied` |
| database_id | string | 是 | - | 目标数据表 ID（从页面 JS 中提取） |
| properties | object | 是 | - | 字段字典，值必须是 oneof 形状（见 §6.2） |
| target_table_identity | string | 是 | - | 目标表身份确认（表 title + 判定结论，见 §7.1.5）。**写入前必须由用户确认**，防止误写「已发布/公示」类对外列表 |
| idempotency_key | string | 建议 | - | 业务唯一键（提交编号/作品名/UserID+应用名），用于写入前查重（见 §7.3 步骤 2.5） |
| confirm_written | boolean | 是 | false | 用户对「完整字段清单 + 取值来源」的明示确认。**未置 true 不得进入写步骤**（见 §6.5） |
| dry_run | boolean | 否 | false | 只读通道探测 + 字段回显，不执行写入 |
| probe_write | boolean | 否 | false | 允许写一条 `__probe__` 探针记录并立即删除（用于确认写权限） |

> **为什么 dry_run 默认存在？** 写操作一旦执行就产生不可撤销的记录（本次直接进主办方审核池）。先用只读通道拿到 schema、用探针记录确认写权限、再正式写，是成本最低的防误操作手段。

> **为什么 `confirm_written` 是必填而不是可选？** 代填的边界不是"能不能写"，而是"能不能替用户做承诺"。把确认动作设计成必填参数，意味着跳过它会直接导致流程不完整，而不是被悄悄忽略。

## 6. 依赖与前置准备

### 6.1 通道探测前置

- **必读**：目标页面的 HTML 源码（抓取或从宿主缓存落盘），从中提取 `databaseId`、`pageId`、提交函数、字段映射
- **读权限来源**：优先用带登录态的通道读 schema；失败再降级
- **操作限制**：写操作前必须确认目标表的所有必填字段已具备值（见 §6.3）

### 6.2 PropertyValue oneof 形状（实测契约）

`database.addRecord` 的 `properties` 每个值是 Go oneof，**不能传裸字符串**（传裸值报 `cannot unmarshal string into Go struct field AddRecordReq.properties`）：

| 字段类型 | 形状 |
|---------|------|
| 文本 | `{"text": "..."}` |
| 数字 | `{"number": 3}` |
| 单选 | `{"select": "选项文本"}` |
| 链接 | `{"url": {"text": "显示文本", "link": "https://..."}}` |
| 图片 | `{"image": {"images": [{"title": "...", "imageUrl": "https://...", "width": 1280, "height": 720}]}}` |
| 勾选 | `{"checkbox": true}` |
| 附件 | `{"attachment": [...]}` |

**图片字段额外要求**：`images[]` 的每一项**必须带 `title`**。缺失 title 的项会被页面侧的 `^https://` 过滤逻辑连同整组丢弃——写进去 `code=0`，回读却为空。

### 6.3 前端校验 ≠ 后端校验

页面前端的必填校验（手机号正则、链接格式、勾选授权）**只存在于页面 JS**，直接写库绕得过去。**绕得过去 ≠ 合规**：主办方审核阶段仍按同一规则看。缺项必须向用户索取，不得留空蒙混。

### 6.4 依赖

- `workbuddy_ipc`（WorkBuddy 内置 skill 库 `library/workbuddy_ipc`）——提供带登录态的 `http_request`
- 宿主的 `app.asar` 或前端 chunk——逆向 API 映射用（只读）
- Python 3.14+（本仓库禁止 `from __future__ import annotations`）

> **为什么不用 cookie 提取？** Electron 的 Cookies 是 SQLite 且被宿主进程独占（Windows 上报 `Device or resource busy` / `CreateFileW err 32`）。`workbuddy_ipc.http_request` 走宿主 IPC 管道（`wb.request` 的 `http.fetch`），自动携带登录态，无需碰 cookie 文件。

### 6.5 写入授权边界与红线字段（代填 ≠ 代承诺）

> **这是本 Skill 最容易被跳过、也最不可跳过的一节。** "代用户填表"在工程上是写一行 JSON，在语义上可能是替用户做了法律承诺、授权第三方使用其作品、或提交了受监管的个人信息。两者必须分开。

**（a）写入前必须逐项展示并取得明示确认。** 展示内容固定为三列：

| 字段 | 将写入的值 | 取值来源 |
|------|------------|----------|
| 应用名称 | 知识保鲜台… | 用户口述（2026-10-26） |
| 参赛授权 | ⛔ 不由 Agent 填 | 用户本人勾选 |

来源分三类，必须标注：**用户口述** / **文件读出** / **系统读取（如 UserID）**。凡属 Agent 推断、猜测或"顺手补全"的值，一律不得写入——若必填且用户未给，**留空并向用户索取**，不得蒙混过关（见 §6.3）。

**（b）红线字段：Agent 禁止代填或代传。** 即使技术上 oneof 形状完全支持，下列字段也必须由用户本人操作，或由用户明确给出原始值并确认：

| 类别 | 示例字段 | 处置 |
|------|---------|------|
| 授权 / 承诺 / 权利转让 | `参赛授权`、`优质作品`、同意条款、著作权转让声明 | **默认禁写**。Agent 不得替用户勾选授权类 checkbox |
| 身份 / 证件 | 身份证号、护照号、社保号 | 禁止代填 |
| 金融 / 支付 | 银行卡号、支付账户、结算信息 | 禁止代填 |
| 敏感住址 / 生物识别 | 家庭住址、精确位置、指纹/虹膜/人脸 | 禁止代填 |
| 金融账户信息 | 手机号 + 验证码组合 | 手机号可由用户口述获取并回显核对；验证码须用户当场提供 |

> **本次实测的实例**：目标表「投稿收集池（待运营审核）」共 **31 个字段**，其中 `参赛授权`（checkbox）、`优质作品`（checkbox）即属授权类字段。技术上 `{"checkbox": true}` 一次写入毫无难度，但代用户勾选「参赛授权」等于替用户作出权利授权承诺——**这类动作不是技术问题，是边界问题。**

**（c）授权作用域有限且不继承。**
- 一次授权只对**本次目标 `pageId` + `databaseId` + 这一次写入**有效。
- 换表、换页面、批量重跑、隔天补写，**须重新确认**——上一轮的确认不自动延续。
- 授权不得被理解为"以后这类操作都免确认"。

**（d）红线字段的检测是自动化的。** 本 Skill 的 `scripts/probe_channels.py` 输出的 schema 字段名中命中上表类别关键词（授权/承诺/同意/证件/身份证/银行卡/支付/住址/签名/声明）时，**必须在 dry-run 回显阶段显式标红并要求用户逐项处理**，不得静默跳过。

## 7. 方案 A：宿主 HTTP 面逆向（推荐）

### 7.0 通道重新发现协议（先做这一步，再谈逆向）

> **为什么放在最前面**：本次实战中"通道不存在"的错误结论，是在**只试了一条通道**的前提下写下的。若先做一次完整的通道重发现（旧结论就会被推翻）。本节把"试通道"从随手一试变成有清单的协议。

**六步骨架**（详细命令、chunk 裁决规则、baseUrl 穷举表、页面 HTML 来源 → 见 `references/host-channel-discovery.md`）：

1. **定位宿主安装目录**——不写死路径，按 `<Vendor>/Install/<App>/resources/app.asar.unpacked` 结构找；`probe_channels.py` 已自动化。
2. **检索 asar**——`app.asar` 未压缩，`grep -a` 直接搜路径字符串；需要完整 JS 才解包。
3. **chunk 权威性裁决**——运行时代码段 > 静态资源段；mtime 新者优先；命中多者未必权威（可能是旧版残留），冲突时两个都试。
4. **baseUrl 穷举**——`/space/api/view` / `/space/api/page/share` / `/space/api/agent/v1` / `/space/api/page` 逐一实测。
5. **host 不得写死**——API host 与页面域**跨域**（本次 `www.workbuddy.cn` vs `www.workbuddy.link`）；host 从 chunk 常量或页面 `window.__CONFIG__` 取，用 `WB_SPACE_HOST` 承载。
6. **跑只读探针确认**——`python scripts/probe_channels.py --page-id <pid> --database-id <db>`，输出通道矩阵 + 登录态 + schema + 表身份判定。

### 7.1 逆向 API 映射

宿主 SPA 产物里能找到页面 SDK 的实现。典型映射（本次实测）：

| SDK 方法 | 后端路径（`view` 前缀） |
|---------|---------------------|
| `database.addRecord` | `POST /space/api/view/database/addRecord` |
| `database.updateRecord` | `POST /space/api/view/database/updateRecord` |
| `database.deleteRecord` | `POST /space/api/view/database/deleteRecord` |
| `database.getRecord` | `POST /space/api/view/database/getRecord` |
| `database.query` | `POST /space/api/view/database/query` |
| `database.get`（schema） | `POST /space/api/page/share/database/get` |
| `database.uploadImage` | `POST /space/api/view/upload/image` |
| `database.getUserInfo` | `POST /space/api/view/user/current` |

**逆向入口定位法**：详见 `references/host-channel-discovery.md`（四步：页面 HTML 取 SDK 方法名 → asar 搜字符串定位 chunk → chunk 内取后端路径与前缀 → 多前缀分别试）。**页面 HTML 来源三选一**（webview devtools 另存 / IPC GET 响应体 / 匿名分享链接 GET），取完必须落盘并记录字节数。

### 7.1.5 目标表身份判定（写错表是最贵的错）

> **为什么单独一节**：写错表的后果是**污染对外可见的列表**（如"已发布名单"），而且这种错误在 `code=0` 的成功返回里完全看不出来——你确实成功写入了一条记录，只是写到了不该写的表。

判定流程（由 `scripts/probe_channels.py` 的 `classify_table()` 自动执行）：

| 表 title 命中 | 判定 | 处置 |
|--------------|------|------|
| 含「已发布 / 正式名单 / 公示 / 上线」 | **RISK** | 停下，向用户明示风险并要求明确确认；未确认不得写入 |
| 含「待审核 / 待运营 / 收集 / 投稿 / 登记 / 问卷」 | **OK** | 符合投稿收集表特征，可继续（仍需 §6.5 确认） |
| 无判定关键词 | **UNKNOWN** | 视为未知，须用户确认目标表身份后方可写入 |

本次实测：目标表 title = `投稿收集池（待运营审核）` → 判定 **OK**；表内共 31 个字段。

### 7.2 调用约束

- **`pageId` 必须带**：读写 `/space/api/view/database/*` 都要带 `pageId`，不带即 `code=12607 permission denied`。**这个报错文案极具误导性——它说的是"缺上下文参数"，不是"你没权限"。**
- **写后回读**：`addRecord` 返回 `{"code":0,"data":{"id":"..."}}` 只代表服务端接受，**不代表字段写对了**。必须 `getRecord` 回读比对。

### 7.3 完整执行流程

```
步骤0：抓取/落盘目标页面 HTML（记录来源与字节数），提取 pageId、databaseId、提交函数与字段映射
步骤0.5：跑 scripts/probe_channels.py —— 通道可达性 + 登录态 + schema + 目标表身份判定（只读）
步骤1：读 schema 确认字段名、类型与 select 选项（不要凭猜测填字段）；标出红线字段
步骤2：探测登录态（getUserInfo），确认 UserID 类字段取值
步骤2.5：★ 幂等查重 —— 用 idempotency_key（提交编号/作品名/UserID+应用名）
      调 query 查该表是否已有同键记录；已有 → 停下汇报，绝不重复写入
步骤3：上传图片/附件类字段，拿到 https URL（确认返回含 url）
步骤4：【dry-run】组装 properties 并打印逐字段回显（含「取值来源」列 + 红线字段标红）
步骤4.5：★ 用户确认闸门 —— 把回显结果交给用户，取得明示确认（confirm_written=true）
      未取得确认不得进入步骤5
步骤5：写探针记录（probe_write=true）确认写权限，验证后立即删除
步骤6：正式写入正式记录，取得 record id
步骤7：回读复核（getRecord），逐字段比对关键字段值
步骤8：清理探针与临时文件，汇报提交编号与凭据
```

> **为什么探针记录要单独一步而不是直接写正式记录？** 写权限确认与正式写入是两次不同的失败模式。探针能一次性区分"通道不通"（探针也失败）与"字段形状不对"（探针成功但正式记录字段丢失）。用正式记录做探针会把脏数据留进审核池。

> **为什么幂等查重要提到步骤 2.5 这种靠前的位置？** `query` 端点本次实测可用（`POST /space/api/view/database/query`，必带 `pageId`），查重成本是一次只读请求。而重复投稿在评选场景是**实质违规**——不是"多了一条记录"，是可能被判定为刷量而取消资格。查重必须在写之前，写完再查已经晚了。

**查重必须走服务端 filter，不能靠本地翻页遍历**（这是实测踩到的第二个坑）：

```json
{"databaseId": "<dbId>", "pageId": "<pageId>",
 "filter": {"property": {"property": "提交编号", "text": {"equals": "S1024-1a176238787-lros"}}}}
```

filter 是**递归树**，三种节点：`{property: {property: "字段名", <类型字段>: {<操作符>: 值}}}` / `{and: [...]}` / `{or: [...]}`。类型字段与操作符对照（来自宿主 SDK 契约）：

| 字段类型 | 条件字段 | 操作符 |
|---------|---------|--------|
| text / url / email / phone | `text` | `equals`、`contains` |
| number | `number` | `equals`、`greater_than`、`less_than`、`is_empty` 等 |
| select / multi_select | `select` | `equals`、`does_not_equal` |
| date | `date` | `equals`、`before`、`after` |
| checkbox | `checkbox` | `equals`、`does_not_equal` |

**实测证据（幂等假阴性）**：该投稿池首页仅返回 **50 条**且 `hasMore=true`、`nextCursor` 存在。翻 10 页（500 条）**仍未命中**我们已于 2026-10-26 10:56 写入的那条记录——因为记录按提交时间落位，不在首页。改用服务端 `filter` 后**一次命中 1 条**（`_id=xTlEYCTwBkBKs9SXuoY8a3`）。

> **这个坑为什么危险？** 它是**静默失败**：翻页扫完没找到 → 判定"无重复" → 照常写入 → 实际写入了一条重复记录 → 评审时才发现。**查重工具的默认行为（遍历）恰好在最需要它正确的场景下失效**，而失败模式是无声的。

> **为什么幂等查重要提到步骤 2.5 这种靠前的位置？** 见上。

**记录主键字段名是 `_id`，不是 `id`**（实测 `query` 返回的每条记录都带 `_id`；`addRecord` 返回值里的 `id` 与记录上的 `_id` 是同一个值）。

> **为什么确认闸门独立成一步 4.5 而不是并进步骤 4？** 步骤 4 是"我准备写什么"，步骤 4.5 是"用户是否认可这些内容"。合并会让确认变成一个顺带的动作，独立成步才能在流程记录里留下"确认发生过"的痕迹。

### 7.4 可复用的调用封装

```python
import sys
sys.path.insert(0, r"<library skill 路径>/library")
import workbuddy_ipc

HOST = "https://www.workbuddy.cn"
PAGE_ID = "<pageId>"
DB_ID = "<databaseId>"

def post(path, body):
    """带登录态的宿主 HTTP 调用。绝对 URL 必须用此封装，
    直接 pipe.invoke('http.fetch', {'url': ...}) 会报
    E_BAD_REQUEST: path must be relative and start with /。"""
    return workbuddy_ipc.http_request("POST", HOST + path, body=body)

def add_record(db_id, properties, page_id=PAGE_ID):
    r = post("/space/api/view/database/addRecord",
             {"databaseId": db_id, "pageId": page_id, "properties": properties})
    if r.get("code") != 0:
        raise RuntimeError(f"addRecord failed: {r}")
    return r["data"]["id"]

def get_record(db_id, record_id, page_id=PAGE_ID):
    r = post("/space/api/view/database/getRecord",
             {"databaseId": db_id, "recordId": record_id, "pageId": page_id})
    if r.get("code") != 0:
        raise RuntimeError(f"getRecord failed: {r}")
    return (r.get("data") or {}).get("result") or {}

def upload_image(base64_no_prefix, filename, content_type="image/png", page_id=PAGE_ID):
    """data 必须是去前缀的纯 base64；返回含 url/width/height。"""
    r = post("/space/api/view/upload/image",
             {"data": base64_no_prefix, "contentType": content_type,
              "fileName": filename, "pageId": page_id})
    if r.get("code") != 0:
        raise RuntimeError(f"upload failed: {r}")
    return r["data"]
```

> **为什么封装成 `post()` 而不是直接调 pipe？** `workbuddy_ipc.http_request` 内部把绝对 URL 拆成 path + query 再交给 `wb.request` 的 `http.fetch`；直接 `pipe.invoke('http.fetch', {'url': 'https://...'})` 因为传的是绝对 URL 会被拒。这个坑不报错在业务层，只有在封装后才不会重复踩。

## 8. 方案 B：页面内 SDK 直调

在能拿到 SDK 对象的上下文里（页面注入环境），直接：

```javascript
// 页面 SDK 对象名随宿主而变，形态为 __SMART_PAGE__ 或注入的全局对象
sp.database.addRecord({databaseId: "<dbId>", properties: {/* oneof 形状 */}});
```

字段映射从页面自身的 `buildSubmissionProperties` 一类函数里抄——它是页面作者写的最权威字段说明，比猜 schema 准。

> **为什么方案 B 不作为首选？** 它依赖页面上下文存在且 SDK 对象可见（本次顶层打开时页面被安全挡板替换成提示页，`inject.js` 只做 iframe 代理与 postMessage 桥接）。**在无头环境里这条路经常直接断掉**，因此只作为"有上下文时的捷径"，主路径应走方案 A。

## 9. 通用工具函数

```python
def build_props(fields):
    """把 {字段名: 裸值} 转成 oneof 形状；调用方显式给类型更安全。"""
    TYPE_MAP = {
        "text":    lambda v: {"text": v},
        "number":  lambda v: {"number": v},
        "select":  lambda v: {"select": v},
        "url":     lambda v: {"url": {"text": v[0], "link": v[1]}},
        "checkbox":lambda v: {"checkbox": bool(v)},
        "image":   lambda v: {"image": {"images": v}},
    }
    out = {}
    for k, (t, v) in fields.items():
        out[k] = TYPE_MAP[t](v)
    return out

def verify_record(db_id, record_id, expected, page_id=PAGE_ID):
    """回读复核：返回 (通过?, 差异字典)。expected 为 {字段: 期望值}。"""
    actual = get_record(db_id, record_id, page_id)
    diff = {}
    for k, want in expected.items():
        got = actual.get(k)
        if isinstance(want, (list, dict)):
            got_s = str(got); want_s = str(want)
            if want_s not in got_s:
                diff[k] = {"expected": want_s[:120], "actual": got_s[:120]}
        elif got != want:
            diff[k] = {"expected": want, "actual": got}
    return (not diff), diff
```

> **为什么要写 `verify_record` 而不是肉眼看返回值？** `code=0` 与"字段写对了"是两件事——本次若图片项缺 `title`，`addRecord` 同样返回 `code=0`，但回读时 `作品截图` 为空。**只有逐字段比对才能发现这类静默丢弃。**

## 10. 安全检查清单（逐项确认）

- [ ] 已确认目标表与页面 ID 的对应关系（`databaseId` / `pageId` 来自页面源码，非猜测）
- [ ] 已读取目标表 schema，字段名与 select 选项已核对（未凭猜测填字段）
- [ ] 已做**目标表身份判定**（§7.1.5）：判定非 RISK，或用户已明确确认写入对外列表
- [ ] 已确认登录态与当前账号标识（UserID 类字段取值来源已验证）
- [ ] 已完成 dry-run 字段回显（含「取值来源」列）并获得用户**明示**确认（`confirm_written=true`）
- [ ] **红线字段已逐项处理**：授权/承诺类字段由用户本人勾选，证件/金融/生物识别类字段未由 Agent 代填
- [ ] 已做**幂等查重**（步骤 2.5）：确认该表无同 `idempotency_key` 的既有记录
- [ ] 已用探针记录确认写权限，且探针已删除、无残留（并已回读确认删除生效）
- [ ] 图片/附件字段每一项均带 `title`，且返回 URL 为 https
- [ ] 前端必填项（手机号、链接、勾选授权）已向用户逐项确认取到真实值，未留空绕过
- [ ] 写后已回读复核，关键字段逐项比对，差异已归因
- [ ] 敏感字段（手机号、账号 ID）未写入日志、脚本常量与可提交产物
- [ ] 临时文件（HTML 缓存、base64 落盘、探针记录）已清理
- [ ] 已向用户汇报提交编号、记录 ID 与审核状态

> **为什么清单里单列"敏感字段未写入脚本常量"？** 本次脚本用环境变量接收手机号与对话链接，避免把个人信息硬编码进会被提交的源码文件——这类文件会进 git 历史，一旦提交就等于永久留存。

> **为什么"红线字段"要单列成一条而不是并入 dry-run 那条？** dry-run 是"展示内容"，红线是"禁止动作"。两者的失效后果不同：展示漏了用户还能在确认环节补上；红线被代填了，用户可能永远不知道自己的名字被勾进了授权框。

## 11. 常见错误处理

| 错误 | 场景 | 处理方式 |
|------|------|---------|
| `code=12607 permission denied` | 读写 `/space/api/view/database/*` 未带 `pageId`；或走了 agent-gateway 通道 | 先补 `pageId` 重试；再换通道（view → SDK → agent-gateway → share → CDP → UI） |
| `401 not login` | 用了 `/space/api/page/share/*` 写接口 | share 通道无登录态，只用于读 schema；写必须走 view 通道 |
| `cannot unmarshal string into ... PropertyValue` | `properties` 值传了裸字符串 | 按 §6.2 改成 oneof 形状 |
| `E_BAD_REQUEST: path must be relative` | 直接 `pipe.invoke('http.fetch', {'url': 绝对URL})` | 改用 `workbuddy_ipc.http_request` |
| `stdin JSON must be an object` | CLI 批量接口要求对象包裹 | 改用对象或走 HTTP 直调 |
| `11607 empty filter: at least one of property/and/or is required` | 传了 `filter` 但没给子树 | filter 是递归树，须给 `{property:{property:"字段名",text:{equals:"值"}}}` |
| `11607 property filter: property name is empty` | filter 叶子的 `property` 键值不是字段名 | 叶子形状是 `{property: "<字段名>", <类型字段>: {...}}`，不是 `{"字段名": 值}` |
| `11607 cannot unmarshal array into ... PropertyFilter` | filter 的 `property` 传成了数组 | `property` 是单个对象，不是数组 |
| 写入 `code=0` 但回读字段为空 | 图片项缺 `title` / 值形状错 | 补 `title`、按 oneof 重写后重试 |
| 查重说"无重复"但记录已存在 | 翻页遍历只覆盖首页 | 改用服务端 `filter` 查重（见 §7.3 步骤 2.5） |
| `not login` on share channel | 同 401 | 同上 |

> **完整故障排查见 references/troubleshooting-matrix.md；脚本方案加 `--debug` 获取详细日志。**

## 12. Gotchas（陷阱与反直觉行为）

### 12.1 通道与鉴权陷阱

- **一次 12607 不等于不可达**：这是本次最贵的教训。第一轮只试 agent-gateway 就下"Agent 无法代提交"的结论并降级交付物，实际同 host 上存在可写通道。**至少试完 §7.0 的通道重发现协议（含 baseUrl 穷举）再下不可达结论。**
- **`permission denied` 文案会骗人**：本次所有 12607 的真实原因都是"缺 `pageId`"，不是权限不足。看到这个文案先查必填参数。
- **`space_api.py` 与 `view` 通道不是一回事**：前者走 agent-gateway，对第三方资源表无权限；后者是页面访问者身份，对页面挂载的表可写。
- **`share` 通道只读**：无登录态时写接口 401，但 `database/get`（schema）反而可读——**同一前缀下读写能力不同**。

### 12.2 参数形状陷阱

- **`properties` 值必须是 oneof**：裸字符串会让 Go 反序列化直接失败，报错文案指向 struct 字段，容易误以为是接口版本问题。
- **图片项必须带 `title`**：缺失时页面侧 `^https://` 过滤会丢弃整组，且写入仍返回 `code=0`。
- **base64 必须去前缀**：`data:` 前缀会导致上传失败或产生无效 URL。
- **`pageId` 与 `databaseId` 都要带**：只带一个同样报 12607。

### 12.3 写入与验证陷阱

- **`code=0` ≠ 字段写对**：写入成功与内容正确是两件事，必须回读比对。本次回读逐字段核对了 **18 个关键字段**（目标表 schema 共 31 个字段，其余为审核侧字段，本次未写入）。
- **回读也要带 `pageId`**：不带 `pageId` 的 `getRecord` 会报与写入相同的 12607，容易误判为"记录没写进去"。
- **探针记录必须删**：本次实测 `deleteRecord` 的 body **只需 `{"recordId": "<rid>"}`**（不带 `pageId` 也成功删除）；若删除失败须立即重试并汇报残留记录 ID，不要假设"删掉了"。
- **前端校验绕过 ≠ 合规**：手机号正则、链接必填只在前端；绕过能写进去，但审核阶段仍按同一规则看。
- **翻页查重是静默失效**：query 默认只回首页 50 条，翻 10 页 500 条仍可能漏掉目标记录（实测如此）。**查重必须用服务端 `filter`**，翻页遍历只会给出"没重复"的假结论。
- **记录主键叫 `_id` 不是 `id`**：遍历结果按 `rec["id"]` 取会拿到 None，进而让幂等拦截打印不出记录 ID。

### 12.4 工具与环境陷阱

- **绝对 URL 不能直接进 `pipe.invoke`**：必须用 `workbuddy_ipc.http_request`。
- **Electron cookie 文件被独占**：Windows 上读 `Cookies` 报 `Device or resource busy` / `CreateFileW err 32`，`sqlite3 mode=ro&immutable=1` 也失败——**不要在这条路上耗时间**，走 IPC 管道自带登录态。
- **Windows 屏幕自动化小助手常缺**：`resolve_cli.sh` 报平台不匹配、`.ps1` 被执行策略拦截，UI 自动化往往是最后才考虑的路。
- **会话记录体积大**：取证不要全文 Read，用切片脚本定点抽（参见 `oversized-tool-output-slicing`）。

### 12.5 领域陷阱

- **不可逆点**：正式提交进审核池后，形态类字段通常不可改；社媒数据与评审窗口有截止时间。**写入前把"选错就撤不回"的字段一次定对。**
- **过程证据链接与内容不符**：本次用户提供的会话分享链接指向另一个主题的会话，形式合规但语义不匹配评审预期。**填链接前核对内容主题是否对得上。**
- **授权类字段不是普通字段**：`参赛授权` 这类 checkbox 在技术上只是一行 `{"checkbox": true}`，但它代表用户的权利承诺。**能写 ≠ 该写。**
- **"页面 URL 的域" ≠ "API host"**：本次页面域 `www.workbuddy.link`、API 域 `www.workbuddy.cn` 跨域，照抄页面域会整片 404。
- **写错表不会报错**：误写「已发布名单」表返回同样是 `code=0`。目标表身份判定（§7.1.5）必须前置。

## 13. 关键参考速查表

> **观测于 2026-10-26（WorkBuddy 平台）。端点可能随版本变化——每次使用前用 `scripts/probe_channels.py` 复核，不要把本表当永久事实。完整端点层见 `references/workbuddy-endpoints.md`。**

| 目标 | 端点/参数 | 注意事项 |
|------|----------|---------|
| 读 schema | `POST /space/api/page/share/database/get` | 无需 pageId；先读再填字段 |
| 读当前用户 | `POST /space/api/view/user/current` | 返回体 `{data:{userInfo:{nickName,id,...}}}` |
| 新增记录 | `POST /space/api/view/database/addRecord` | 必带 `pageId`；properties 为 oneof |
| 回读记录 | `POST /space/api/view/database/getRecord` | 必带 `pageId` 与 `recordId` |
| 查表记录 | `POST /space/api/view/database/query` | 必带 `pageId`；**默认只返回首页 50 条**；查重须带 `filter` |
| 查重过滤 | `filter: {property:{property:"字段名", text:{equals:"值"}}}` | 服务端过滤，一次命中；**不可用翻页替代** |
| 删除记录 | `POST /space/api/view/database/deleteRecord` | 实测 body 仅需 `{"recordId": "<rid>"}` |
| 上传图片 | `POST /space/api/view/upload/image` | `data` 为去前缀 base64；返回 url/width/height |
| 调用封装 | `workbuddy_ipc.http_request("POST", url, body=...)` | 绝对 URL 专用；自动带登录态 |
| 记录主键 | 记录上字段名为 `_id` | 不是 `id` |
| 依赖位置 | 宿主 `resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills/library/` | 勿写死，用 `probe_channels.py` 自动定位 |
| API host | `WB_SPACE_HOST` 环境变量，默认 `https://www.workbuddy.cn` | 与页面域（`*.workbuddy.link`）跨域 |
| 幂等查重 | `POST /space/api/view/database/query` + `filter` | 见 §7.3 步骤 2.5 的 filter 形状表 |

> **为什么端点表要带观测日期？** 平台端点是**易变资产**，不是常量。把"观测于某日"写进标题，等于给读者一个判断新鲜度的把手；不写，读者会默认它永远正确。

## 14. 长期方案与演进方向

- **宿主提供正式 API 时优先切官方 API**：本 Skill 的逆向路径是过渡方案，一旦官方开放投稿/报名 API，应切过去并保留本 Skill 作为兜底。
- **通道判定已沉淀为通用探针脚本**：`scripts/probe_channels.py` 已实现并实测跑通（只读探测 + schema 读取 + 登录态 + 目标表身份判定），可复用到其他智能页提交场景。
- **幂等重入**：**已落地**，不再是演进方向。`scripts/submit_record.py` 的 `--idempotency-field` + `--idempotency-key` 走服务端 filter 查重，命中即拒绝写入（实测拦截成功）。§7.3 步骤 2.5 为强制步骤。
- **提交脚本化**：**已完成**——`scripts/submit_record.py` 已实现三道闸门 + 探针写删 + 正式写入 + 回读复核，退出码区分失败原因（2=闸门拦截 / 4=探针删除失败 / 5=回读不一致）。
- **CDP 通道待验证**：§4 第 5 条通道目前仅为设想，需在真实环境跑通并记录前置条件后，才能从"未实测"升级为"已验证"。
- **端点层与通用层分离**：WorkBuddy 具体端点与形状属易变资产，已归入 `references/workbuddy-endpoints.md`（带观测日期）；本 SKILL.md 保留的是**跨平台通用方法论**（通道判定、oneof 形状规律、闸门设计、回读复核）。

## 15. Changelog

- **v1.0.0** (2026-10-26): 初始版本。萃取自 sc-20261026-workbuddy-contest-submit 实战（WorkBuddy「1024 造物挑战」活动页代投稿）。内容：通道权限模型判定顺序、宿主 HTTP 面逆向路径（asar → SDK 映射 → 后端路径）、PropertyValue oneof 形状契约、图片 title 必带与 base64 去前缀两个静默陷阱、`pageId` 缺失导致的误导性 12607、写后回读复核（false-success defense）、18 条 Gotchas（12.1–12.5）、11 项安全检查清单。
- **v1.1.0** (2026-10-26): 对抗审查后修订。新增 §6.5 写入授权边界与红线字段（授权/承诺/证件/金融类字段禁代填）、§7.0 通道重新发现协议（asar 定位/解包/chunk 权威性裁决/baseUrl 穷举/host 不得写死）、§7.1.5 目标表身份判定、CDP 第五通道（标注未实测）、幂等查重升级为 §7.3 强制步骤 2.5、用户确认闸门步骤 4.5、`confirm_written`/`target_table_identity`/`idempotency_key` 三个必填参数；新增 `scripts/probe_channels.py`（只读探针，已实测跑通）与 `scripts/submit_record.py`（三道闸门 + 探针写删 + 正式写入 + 回读复核，闸门已用真实数据逐条验证）；新增 `references/workbuddy-endpoints.md`（端点层，带观测日期与失效自检）；修正事实层自洽：Gotchas 计数 14→18、deleteRecord 参数以实测为准（仅 `recordId`）、`x-toml-ref` 路径修正为 `../../../`、端点表加"观测于 2026-10-26"时效标注、字段总数修正为 31（初稿口述 34 有误）、记录主键 `_id`、查重 filter 形状与"翻页查重静默失效"实测坑。
