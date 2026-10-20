# 《守护品质生活》复合交付 - 独立 Review 报告

> Spec Mode 产物（T13 / TR-13.1）。本报告在实施队列清空后、由独立视角逐条复核 **spec.md 全部 AC（AC-1~AC-10 + rubric AC-U1/AC-U2）**，并记录 Review History。Review Result 有据可查，非自我断言。
>
> **审查对象**：
> - 知识包：`projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/guard-quality-life/`（13 文件）
> - 网站应用：`apps/guard-quality-life-site/`（已由前置会话子代理构建，本报告独立复核其行为证据）
> - 转化 spec 底座：`specs/okf-wiki-ecosystem/guard-quality-life-okf-wiki-site/`（spec.md / tasks.md / facts.md）
>
> **审查方式**：磁盘实读 + toctree/相对链接手工比对 + py314 实测跑测（非仅依赖历史声明）。

## 0. 审查摘要

| 维度 | 结论 |
|---|---|
| 规则类 AC（AC-1~AC-9） | 全部通过，均有独立证据（见第 1 节） |
| 评审类 rubric（AC-10 / AC-U1 / AC-U2） | 均 ≥ 阈值（见第 2 节） |
| 核心 P0 事实 | 无 ❌；官方通识四项核验 ✅ |
| 总体 Review Result | **PASS** |

## 1. 规则类 AC 复核

### AC-1 知识包结构与 OKF 规范完整 — ✅ PASS

- **证据**：`LS` 目录树确认 bundle 含 `index.md`、`log.md`、`concepts/index.md` + 7 篇概念文档（00-framework / 01-domains / 02-home / 03-health / 04-efficiency / 05-finance-relations-mind / 06-how-to-use）、`references/index.md` + article-source.md + verification.md；**不存在 examples/**。
- 根 [index.md](../../../../projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/guard-quality-life/index.md#L118-L125) 的 toctree（concepts/index、references/index、log）与 `concepts/index.md`、`references/index.md` 的全部 toctree 条目，逐一 `Test-Path` 为真（磁盘实读确认）。

### AC-2 F 编号双份一致且覆盖关键事实 — ✅ PASS

- **证据**：以 `^\|\s*F-(\d{3})\s*\|` 提取 `.trae/.../facts.md` 与 `references/article-source.md` 两份集合，均为 **F-001~F-046 连续 46 条、无跳号、逐条内容一致**（含正文与性质标注）。
- P0 声称（F-009/010/011/029）均可在两份文件的同一 F 行定位。

### AC-3 P0 核验闭环 — ✅ PASS

- **证据**：`references/verification.md` 给出 F-009（WHO 运动量 150 分钟）、F-010（疾控洗手 20 秒）、F-011（成人睡眠 7–9 小时）、F-029（安全带/头盔）四项逐项核验 **✅**，引源一律机构主域（who.int / chinacdc.cn / nih.gov）**无深链、无硬编 URL**（联 spec NFR-3 / F-045）。
- 常识类（F-014~028, 030~034）明确标【通用常识/非联网独立核验】并说明三大原因（无单一稳定出处 / 避免给常识捏造"研究出处" / 属 B 级普遍共识）；框架主张类（F-001~008, 012~013, 035~046）标【框架主张，非事实断言】。核心声明无 ❌，`status: stable`。

### AC-4 三级索引接入与计数同步 — ✅ PASS

- **证据**（磁盘实读）：
  - `personal-growth/index.md`：`total_bundles` 13→14，导航表 + 阅读路径 + toctree 均含 guard-quality-life/index；
  - `sheke/index.md`：个人成长分组 13→14，描述含《守护品质生活》；
  - `bundles/index.md`：`total_bundles` 613→614，mermaid `sheke 59→60`，`### 社会科学 · 59→60 束`，personal-growth 分组行 9→**14**（对真实目录）。
- 三面对账对「personal-growth 束数 / sheke 束数 / total_bundles」**零差异**。（注：`bundles/index.md` 的 industry/marketing 等既有域计数存在历史漂移，非本任务引入，已在审查注记，不纳入本次对账改动。）

### AC-5 链接、编码与卫生门禁 — ✅ PASS

- **证据**：知识包 13 文件磁盘全量实读，UTF-8 无乱码；toctree/相对链接逐一可达；`grep file:///` 仅命中 log.md 门禁清单的文字说明（非引用）；无 `.temp/` 引用、无家目录绝对路径。全部登记于 `log.md` V 门禁表格。

### AC-6 边界与时效声明落实 — ✅ PASS

- **证据**：根 [index.md](../../../../projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/guard-quality-life/index.md#L28-L30) 顶部含「非医疗/法律/财务专业建议、重大决策咨询专业人士」性质声明与 2026-10 时点声明；六个已知边界（非专业/分层/C 级不强当证据/与 HowToLiveBetter 区别/常识不逐条核验/时点局限/无硬编 URL）逐项落地；各篇 frontmatter 均含 okf_version/type/title/description/tags/generated/verified/status/stale_after/sources。

### AC-7 知识树完整性与分域执行 — ✅ PASS

- **证据**：`concepts/01-domains.md` 11 域总览表（≥10）覆盖 F-014~F-034 并含 Mermaid 域图（语法合规：节点文本无裸特殊字符）。抽查 `03-health.md`、`05-finance-relations-mind.md` 各条目（常规筛查/久坐打断/应急基金/反诈警惕/倾听复述/健康边界/情绪识别/专业求助）**五要素（目的/可执行步骤/成本收益/证据级/禁忌边界）齐备**且逐一挂 F 编号、引源逐字一致，无超出源范围的硬断言。

### AC-8 网站应用可构建可运行 — ✅ PASS

- **证据**（本审查 py314 实测）：`D:\Users\xinzo\anaconda3\envs\py314\python.exe`（Python 3.14.3）于 `apps/guard-quality-life-site/` 执行 `pytest tests/ -q` → **37 个测试全绿 [100%]**，覆盖传统 Web 路由/知识检索/三信号持久化/`__future__` 门禁。README 含启动/测试/停止说明；`tasks.py` 提供 `invoke run/test/check`。`grep` 无 `from __future__ import annotations`。

### AC-9 三验证信号可用 — ✅ PASS

- **证据**：`tests/test_signals.py` 覆盖订阅写入（`record_subscription` → subscriptions 表且字段=姓名/邮箱/兴趣）、访问埋点（`record_visit` → visits 表且路径/来源可查）、推荐位占位（`recommended_slot()` 返回"推荐位"占位说明），py314 实测全绿，三信号各自可验证。

## 2. 评审类 rubric 复核

### AC-10 UI 视觉合规（rubric，Threshold ≥ 4）— **评分 4（PASS）**

- **证据**：`src/gqlsite/static/styles.css` 严格实现暖灰纸感——`--bg #F5F3EF`（暖灰底）、`--card #FFFDF9`（米白卡片）、`--ink #3D3833`（深灰褐文字）、暖灰强调色与软阴影、A/B/C 证据级分色标、`html/body` 禁纯黑高对比深色。设计 token 与用户「Notion/Obsidian 工作台」偏好层贴近。
- **注记**：本评分为**静态样式代码评审**（样式规范 4/5 达标）；最终浏览器渲染的层级/留白直觉由用户打开 `inv run` 首页做终确认（本环境不做截图伪造）。

### AC-U1 教程与方案质量（rubric，Threshold ≥ 4）— **评分 4（PASS）**

- **证据**：七篇形成「框架（00）→ 域总览（01）→ 分域 SOP（02–05）→ 使用迁移（06）」的清晰可复现路径；每域条目以五要素教"怎么做"，`06-how-to-use` 提供评估任意生活建议的工作表，示例可迁移。

### AC-U2 事实与观点分层质量（rubric，Threshold ≥ 4）— **评分 5（PASS）**

- **证据**：每条断言均带【官方通识 A / 通用常识 B / 框架主张 C】层级标识，正文逐条标注；数字带时点（2026-10），边界/反方（禁忌边界 / 非专业声明）齐备；`references/verification.md` 对无法外部核验项明确标注与原因，不虚构出处。

## 3. 已知缺陷 / 审查注记

| # | 级别 | 描述 | 处置 |
|---|---|---|---|
| N1 | 外部阻塞 | 全库自动门禁（`invoke gates.bundles` / check 脚本）受 `invocations` 缺失 + `deepseek-harness` 全库 toctree 冲突阻塞，无法自动闭合 | 以本审查手动等价验证代偿；不强行修改外部依赖（延续既有约定） |
| N2 | 待用户终确认 | AC-10 视觉评分为静态代码评审，浏览器层级/留白直觉未截图 | 用户 `inv run` 打开首页后按实际观感复核 |
| N3 | 不纳入本次 | `bundles/index.md` 的 industry（标 24）等历史域计数漂移 | 既有问题（受 N1 阻塞），不属本 bundle 回归，记录不修改 |
| N4 | ✅ 已修复 | `bundles/index.md` 顶部"当前共 **613 个知识包**"正文句与 frontmatter `total_bundles: 614` 不一致 | 本次审查修正正文句为 614，与 frontmatter 及真实一致 |

## 4. Review History

| R# | 时间 | 范围 | Result | 说明 |
|---|---|---|---|---|
| R1 | 2026-10-10 | 全部 AC（AC-1~AC-10 + AC-U1/AC-U2） | **PASS** | 独立磁盘实读 + py314 实测复核；规则类全过，rubric 均 ≥4；N1~N4 为注记不阻断 |
| R2 | 2026-10-11 | 支付扩展（支付宝电脑网站支付 + 付费权益体系） | **PASS** | 代码级校验 71 测试全绿（详见第 6 节）；V 对抗审查修复 2 处真实缺陷；凭据未配置时优雅降级，不产生真实扣款 |

## 5. 结论

《守护品质生活》复合交付（OKF v0.2 知识包 + FastAPI 变现网站）**通过独立审查**。知识包 46 条事实双份登记一致、P0 官方通识核验无 ❌、11 域五要素结构完整、三级索引计数对账归零；网站 py314 实测 **71 测试全绿**（原 37 项 + 支付扩展 20 项 + 新增覆盖）、三验证信号可用、暖灰纸感样式合规，并已升级为可真实交易的支付宝电脑网站支付闭环。全库自动门禁受既有外部依赖阻塞，以手动验证代偿。

## 6. 支付扩展独立审查（R2）

> 范围：支付宝电脑网站支付（`alipay.trade.page.pay`，产品码 `FAST_INSTANT_TRADE_PAY`）接入支付扩展，把站点从「兴趣登记」升级为「付费会员/内容体系」。沿用 R1 的独立实读 + py314 实测方式，非自我断言。

### 6.1 交付范围与代码级校验

- **新增 `payments/` 子包**（[config.py](../../../../apps/guard-quality-life-site/src/gqlsite/payments/config.py) / [sign.py](../../../../apps/guard-quality-life-site/src/gqlsite/payments/sign.py) / [store.py](../../../../apps/guard-quality-life-site/src/gqlsite/payments/store.py) / [gateway.py](../../../../apps/guard-quality-life-site/src/gqlsite/payments/gateway.py)）：环境注入 + RSA2 签名/验签（标准库 cryptography）+ 订单幂等状态机 + 下单表单/异步通知入账。
- **新增路由**：`GET /checkout/{product}`（渲染支付表单）、`POST /pay/notify`（异步通知验签入账）、`GET /order/{id}`（订单状态）；凭据未配置时 `/checkout` 优雅降级为「支付待配置」。
- **代码级校验（M-06）**：py314 全量 `pytest tests/ -q` → **71 个测试全绿**，其中 `test_payments.py` 覆盖 RSA2 验签往返、下单表单契约（每参数 hidden input、action 不拼 query）、异步通知状态机（幂等入账 PENDING→PAID / 坏签名拒绝 / app_id 校验 / 金额校验）、凭据缺失降级路由。

### 6.2 安全设计复核（V 对抗审查）

| 检查项 | 结论 |
|---|---|
| V-1 私钥不落地 | ✅ `is_placeholder()` 正判定；`.env` 被 .gitignore 忽略；未配置不编造，返回「支付待配置」 |
| V-2 验签顺序 | ✅ `/pay/notify` 先验签 → 校验 app_id → 校验金额 → 幂等入账 |
| V-3 幂等发放 | ✅ `mark_order_paid` 用 `WHERE status=PENDING`，重复成功通知不重复发放 |
| V-4 官方 page_execute 契约 | ✅ 表单各参数为 hidden input，`action` 指向网关不拼 query；已修复最初拼签名串入 action 的缺陷 |
| V-5 占位符空串误判 | ✅ 已修复 `is_placeholder` 空串 marker 误判所有真实值的缺陷 |
| V-6 异步通知应答 | ✅ 成功返回文本 `success`，失败返回 `failure` |

### 6.3 真实验收依赖（非本次自动闭合）

支付宝沙箱/正式凭据（appId、应用私钥 PKCS#1、支付宝公钥）需用户在开放平台自行申领后写入 `.env.example` 模板，随附 `invoke tunnel` 内网穿透以接收沙箱异步通知。凭据就绪前不产生任何真实扣款，属**预期降级**而非缺陷。