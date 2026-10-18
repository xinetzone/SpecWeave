# 秒悟赏金 IDEA·026「Skill 导航台」 - Implementation Plan

> 方法论：seven-concepts 场景 5（F→V→I→C）+ Spec Mode 五阶段。
> 目标路径：`apps/samples/skill-navigator/`（`mise.toml` + `README.md` + `site/` 4 文件）。
> 对外承诺：平台已公开登记的交付说明见 `raw/source-capture.md` §四，本计划与之逐项对齐。

## Task 1: R 阶段事实采集 + 接单（平台侧动作）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 抓取赏金详情页（S1），登记 F-001~F-010：编号/标题/问题陈述/目标用户/期望产出/发起人/赏金池/推荐工具/广场计数/相邻 Idea。
  - 探测平台层与工具层（F-011~F-016）：市场页 DOM 结构、原始 HTML 正则命中、详情页可达性、`meoo skill` 子命令、登录账号、mise/node/npm/python 版本。
  - 读取 Meoo 部署协议（F-019）与仓库同类先例（F-020）。
  - 接单：浏览器代理点击「我要接单」→ 填 202 字符交付说明 → 「确认接单」（F-017/F-018）。
  - 落盘 `raw/source-capture.md`（源页逐字 + 探测表 + S1–S5 台账 + 缺口清单）。
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-1.1: F 编号连续无跳号（F-001–F-020），每条含来源标注（主源/实测）。
  - `rule` TR-1.2: 接单动作有可核对证据（点击前后状态文本：待接单 → 制作中），非口头声明。
  - `rule` TR-1.3: 缺口清单 ≥5 项，源页未明示项不得被推断补全。
- **Completion Evidence**:
  - 赏金详情页匿名单次抓取即返回完整渲染正文；F-001~F-020 连续登记于 `raw/source-capture.md`，每条标注主源/实测 → TR-1.1 满足。
  - 浏览器子代理报告：点击「我要接单」后弹出「接单确认」弹窗（标题/描述/输入框/确认按钮）；填入 202 字符（JS 读取 textarea.value 回验未截断）后点击「确认接单」，页面状态由「待接单」→「制作中」，无额外必填项、无失败提示 → TR-1.2 满足。
  - 缺口清单 6 项（赏金金额与结算规则 / 验收判定规则 / 牛来徽章权益 / 单 Skill 详情 ID / 市场页条目全集 / 两页同主题条目同一性）→ TR-1.3 满足。

## Task 2: F 阶段设计与 V 阶段对抗审查冻结

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - F：问题界定 → 7 条隐含假设逐条剥离（H1~H7，每条附验证动作与结论）→ 要素识别 → 5 条公理（A1~A5）→ 自下而上重构方案。
  - V：F 之后强制四视角对抗审查（魔鬼代言人 / 新人 / 老板 / 未来），每视角 ≥3 攻击点，汇总采纳修正 ≥2 条。
  - 落盘 `raw/design-f.md`（含假设剥离表、公理、重构方案、四视角审查表、采纳修正汇总、未通过项）。
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-2.1: 假设剥离 ≥5 条，每条须有"验证动作"与"结论"（剥离/成立/部分成立/降级）。
  - `rule` TR-2.2: V 四视角全覆盖，审查意见合计 ≥5 条且具体（非客套话）；采纳修正 ≥2 条并逐条落到 FR/NFR。
  - `rubric` TR-2.3: 方案与原问题的一致性（1–5，阈值 ≥4）——重构方案须服务 F-003 的原始问题，不得为创新而创新。
- **Completion Evidence**:
  - `raw/design-f.md` §1.2 剥离 7 条假设（H1~H7），每条含验证动作与结论（剥离 3 / 成立受阻降级 2 / 部分成立降级 2）→ TR-2.1 满足。
  - §2 完成四视角审查，合计 14 条攻击点（魔鬼代言人 4 / 新人 4 / 老板 3 / 未来 3），逐条给出结论与处置；采纳修正汇总 11 条，均已映射到 spec FR-1~FR-7 与 NFR-1~NFR-7 → TR-2.2 满足。
  - TR-2.3（rubric）：自评 5/5——方案每组要素均可回溯到 A1~A5 与 F-003；无「为创新而创新」项（未引入大模型、未引入构建链、未引入后端）。

## Task 3: 数据集策展与演示覆盖（I→E 的落地物）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 合并 S2（事件页 25 条逐字）与 S3（市场页条目逐字 + 使用量）为一份策展集，同主题不同署名条目各自登记、不判同一性。
  - 每条 Skill 落 8 个字段：`name`/`author`/`usage`(缺失为 `null`)/`source`/`desc`(逐字)/`solve`/`fit`/`notFor`/`tags`(≥2)/`demo{input,steps×3,deliverables≥2}`。
  - 设计痛点卡 ≥12 张（两分组），并机械校验「每张痛点卡候选数 ≥2」「零悬空标签」。
  - 生成 `site/assets/data.js`（`window.SKILL_DATA = {snapshot, sources, pains, skills}`）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-8
- **Test Requirements**:
  - `rule` TR-3.1: 条目数 ≥30；8 字段非空；`tags` 全集覆盖 `pains` 全部标签引用（零悬空）。
  - `rule` TR-3.2: 痛点卡 ≥12，每卡候选 ≥2（机械计数，非人工点数）。
  - `rule` TR-3.3: `desc` 与来源页逐字一致；`usage` 与来源页数字一致；事件页来源条目 `usage` 必须为 `null`。
- **Completion Evidence**:
  - 落盘 `site/assets/data.js`：`skills` 共 **39** 条（market **26** + event **13**），每条 8 字段齐备，`demo.steps` 全为 3 步、`demo.deliverables` ≥2 项 → TR-3.1 前半满足。
  - `pains` 共 **14** 张（「我想做点什么」7 张 + 「我卡在哪一步」7 张）；机械校验最小候选数 = **3**（每卡 ≥2）；技能侧标签 **27** 个全部被痛点卡引用，**零悬空、零死标签**；`tagLabels` 27 条与标签集合等势 → TR-3.1 / TR-3.2 满足。
  - `market` 26 条 `usage` 全为数字、`event` 13 条 `usage` 全为 `null`；`desc` 逐字取自来源页，长度区间 18–165 字符 → TR-3.3 满足。
  - **机械校验命令与输出**（脚本位于系统临时目录，不入库）：`node check-data.cjs <data.js>` → `技能条目数: 39 {"market":26,"event":13}`、`痛点卡数: 14`、`错误数: 0`、`VERDICT=PASS`。
  - **推荐快照实测**（14 张痛点卡的前 2 名，含命中标签数与使用量）：p1 一键设计稿转应用/秒悟UI设计专家；p2 高级UI/UX(37115,3)/秒悟UI设计专家；p3 PPT精编/Frontend-Slides；p4 AI图像生成(1608)/笔记封面设计；p5 西瓜业务产品化/语文书籍模板；p6 文字脚本转白板动画/多平台推广视频生成；p7 中国全域地图展示/AI产品调研；p8 头脑风暴(25445,3)/产品需求验证判断；p9 首批用户获取(3)/产品增长诊断；p10 AI应用成本核算与定价/海明App商业化；p11 UI精准还原(3)/高级UI/UX；p12 代码质控/代码审查专家；p13 SignalMine/产品增长诊断；p14 菜菜的冲浪Skill/热点自传播网感冲浪。

## Task 4: 页面实现（4 文件静态站点）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - `site/index.html`：语义化结构——首屏（标题 + 一句话说明 + 痛点卡两组 + 自由输入）、结果区（1–2 张卡 + 候选折叠）、演示面板、兜底区、页脚声明。
  - `site/assets/app.css`：暖灰纸感视觉（暖灰底 + 米白卡片 + 深灰褐文字，符合本用户"阅读优先"偏好）；响应式 ≥900 双列 / <900 单列；不含 CSS 框架。
  - `site/assets/app.js`：加权标签打分（命中标签 + 分值回显）、痛点卡与自由输入统一入参、候选折叠、演示面板展开/收起、兜底路径、键盘可达。
  - 零外部请求：无 CDN、无外链图片、无字体外链（系统字体栈）、无 `fetch`。
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-7
- **Test Requirements**:
  - `rule` TR-4.1: `site/` 下恰 4 个文件；全站 `http(s)://` 仅出现于数据来源标注与 CTA 链接（点击才跳转），运行时零网络请求。
  - `rule` TR-4.2: 任一痛点卡触发推荐，返回 1–2 条且「匹配理由」非空（含命中标签名 + 分值）。
  - `rubric` TR-4.3: 新手可用性（1–5，阈值 ≥4）——首屏可判、卡片可读、演示可懂、无术语墙。
- **Completion Evidence**:
  - `site/` 下恰 4 个文件（`index.html` / `assets/app.css` / `assets/data.js` / `assets/app.js`）；全站 `http(s)://` 出现 10 处，全部落在 **CTA 链接**（index.html 4 处 `<a href>`）与**数据来源标注/官方简介原文**（data.js 6 处，其中 1 处在 `desc` 逐字文本内），**无** `fetch(`/`XMLHttpRequest`/`.src=`/`@import`/`url(` → TR-4.1 静态侧满足。
  - **浏览器实测（fresh context，`?t=verify2` 强制加载，逐字回抄）**：
    - 首屏：无暗色遮罩、痛点卡可直接点击；
    - 点选「我不会写代码，但想先做个小工具试试」→ 回显「你说的是：我不会写代码，但想先做个小工具试试」，首卡 **一键设计稿转应用**，作者行「作者 职场懒人 · 使用量：事件页未提供」，「为什么是它」原文「命中了你说到的「设计稿转代码」「应用 / 工具」，2 个点都对得上。」→ TR-4.2 满足（结果非空、理由含命中标签与数量）。
    - 演示面板逐字：提示条「示意演示 · 不是这个技能的真实运行结果」；示例输入「[上传三张页面设计稿] 把它变成一个能点的小应用。」；3 步「解析设计稿结构并生成页面 / 串起页面间跳转 / 与设计稿比对还原度并修正」；产出物「可运行的应用页面」「还原度比对记录」。
    - Esc 关闭面板 → 回到结果区；自由输入「我做了个记账小工具，但没人用，不知道怎么推」→ 回显「你写的是：…」，首卡 **首批用户获取**；「都不太对」→「共有 9 个候选」（前 3：首批用户获取 / GitHub星标增长器 / 高审美产品官网）；「重新选」→ 回到第一步。
    - 网络请求 12 条**全部指向 `127.0.0.1:3015`**，外部域请求 0 条；控制台无 error → TR-4.1 运行时侧满足。
  - **V 门实测发现并修复的 P0 缺陷**：首轮浏览器实测发现 `.demo-layer { display: flex }` 覆盖了 `[hidden]` 的 UA 默认 `display:none`，导致演示面板遮罩在首屏铺满页面并拦截点击（页面看似不可用）。修复：CSS 增加 `[hidden] { display: none !important; }`；复测 8 项全 PASS（详见 `review.md`）。
  - TR-4.3（rubric，新手可用性）：自评 4.5/5——首屏一句话可判断、痛点卡为第一人称口语、结果卡必带「什么时候不该用它」、演示面板三段式可懂；扣分项为「为什么是它」仍含「标签」一词（见 `review.md` 遗留项）。

## Task 5: mise 协议与本地验证

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 项目根落 `mise.toml`：`[tasks.dev]` 监听 `0.0.0.0:3015`；`[meoo.deploy] mode = "static"`、`output = "site"`；不声明 `port`/`tasks.start`。
  - 运行 `.agents/skills/meoo-cli/scripts/validate-mise-protocol.cjs ./mise.toml`，修复全部错误。
  - `mise run dev` 起服 → 验证 `http://127.0.0.1:3015/` 返回真实页面、资源相对路径可达。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 协议校验脚本退出码 0，无 ERROR 项。
  - `rule` TR-5.2: `mise run dev` 后本地 3015 端口 HTTP 200，页面标题文本命中，4 文件全部可获取（无 404）。
- **Completion Evidence**:
  - `mise.toml` 通过协议校验：`node .agents/skills/meoo-cli/scripts/validate-mise-protocol.cjs ./mise.toml` → `Mise 协议校验通过`，`EXIT=0` → TR-5.1 满足。
  - `mise trust --yes ./mise.toml` 成功；`mise install` → `all tools are installed`；`mise exec -- python --version` → **Python 3.13.13**。
  - `mise run dev` 起服后本机实测（`Invoke-WebRequest`）：
    - `/` → HTTP 200，正文 4624 字节，含标题文本「Skill 导航台」；
    - `/assets/app.css` → HTTP 200，12018 字节；
    - `/assets/data.js` → HTTP 200，24607 字节；
    - `/assets/app.js` → HTTP 200，15023 字节。
    四个文件全部可达、零 404 → TR-5.2 满足。

## Task 6: 部署到 Meoo 平台 + C 阶段收尾

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - `meoo projects create` 建远端项目并绑定当前目录（`.env` 记 `MEOO_PROJECT_URL_ID`）；确认 `.env` 不被提交。
  - `meoo deploy` → 取得公网静态链接；`meoo releases list` 核对发布记录。
  - 复跑 Task 3/4/5 的全部机械校验（条目数、痛点候选数、零悬空标签、零外部请求、协议校验）。
  - 公网链接回填 `spec.md` / `tasks.md` / `README.md`。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-6.1: `meoo deploy` 退出码 0，输出含公网访问链接。
  - `rule` TR-6.2: 复跑校验全部通过；条目数/痛点数/候选数与 Task 3 冻结值一致。
  - `rule` TR-6.3: 公网链接实测可达（HTTP 200）且返回页面标题文本。
- **Completion Evidence**:
  - `meoo projects create "Skill 导航台"` → `✔ 项目已创建并绑定到当前目录: Skill 导航台 (yzv5eq2kp2uc)`，`EXIT=0`；生成的 `.env` 仅含 `MEOO_PROJECT_URL_ID`，且 `.gitignore` 第 54–55 行已忽略 `.env` / `.env.*`，不会入库。
  - `meoo deploy --force`（`EXIT=0`）→ 代码同步沙箱成功 → 打包 `site/` → 上传产物 v2 → `✔ 发布成功！v2`，访问地址 `https://yzv5eq2kp2uc.meoo.run`，Commit `5377ab56`，CLI 发布额度 12/1000 → TR-6.1 满足。
  - `meoo releases list` → `发布历史 (2 个版本)`：`v2 active 5377ab56 2026/10/18 19:52:54`、`v1 success 5377ab56` → 发布记录可核对。
  - **公网实测**（`Invoke-WebRequest`）：`/` → HTTP **200**、6686 字节、含标题文本「Skill 导航台」；`/assets/app.css` → 200 / 12167；`/assets/data.js` → 200 / 24607；`/assets/app.js` → 200 / 15023 → TR-6.3 满足。
  - TR-6.2（复跑校验）：见 `review.md` 的独立审查对账（第三方 fresh-context 复核条目数 / 候选数 / 零悬空 / 零外部请求 / 协议校验）。
  - **未部署云服务**：纯前端项目，按 `meoo-cli` 规范**不**执行 `meoo cloud enable`（项目状态「云服务：未开通」为预期值）。

## Task 7: 原子提交与 apps 路由表登记

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 按 `apps/AGENTS.md`「新增应用说明」第 4 条，在 `apps/AGENTS.md` 应用路由表 `samples/` 组追加一行。
  - `python .agents/scripts/check-gitignore.py`、`python .agents/scripts/check-links.py --path apps/samples/skill-navigator` 预检。
  - 按 Conventional Commits 原子提交（中文主体），仅暂存本任务涉及文件。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-7.1: 提交文件清单与 `git status` 实测一致，无他会话变更混入。
  - `rule` TR-7.2: 链接检查通过（零断链、无 `file:///`）。
- **Completion Evidence**:
  - **已完成部分**：按 `apps/AGENTS.md`「新增应用说明」第 4 条，在应用路由表 `samples/` 组 `study-goal-hub` 行后追加 `skill-navigator` 行（含定位、文件结构、数据规模、线上地址与规格路径）。
  - **已跑预检**：`python .agents/scripts/check-links.py --path apps/samples/skill-navigator` → `校验通过: 所有链接均有效`，`EXIT=0`；`python .agents/scripts/check-links.py --path .trae/specs/create-miaowu-skill-navigator` → `校验通过: 所有链接均有效`，`EXIT=0` → TR-7.2 满足。
  - **工作区实况**：`git status --short` 恰为 ` M apps/AGENTS.md`、`?? apps/samples/skill-navigator/`、`?? .trae/specs/create-miaowu-skill-navigator/` 三项，**无他会话变更混入**；项目目录内的 `.env`（Meoo 项目绑定）被 `.gitignore` 第 54–55 行忽略，不会入库 → TR-7.1 满足。
  - **原子提交已执行**（2026-10-18，用户显式指令「提交」），拆为两个单一职责提交：
    - `fbb8e5daa docs(spec): 新增秒悟赏金 IDEA·026「技能导航台」规格三件套` —— 3 文件 / 353 insertions（`spec.md`、`tasks.md`、`review.md`）；
    - `d771e2af0 feat(skill-navigator): 新增技能导航台静态引导页并登记 apps 路由表` —— 7 文件 / 1708 insertions（`apps/AGENTS.md` 路由表 1 行 + 应用 6 文件）。
  - 提交经 `git-commit-utf8.py` 走 UTF-8 bytes 通道（带文件清单，暂存集 == 指定集）；提交后 `git cat-file -p HEAD` 回验中文**无乱码**；`git status --short` 本任务路径**零残留**（其余 `M`/`??` 条目属他会话在途工作，未纳入本次提交）。
  - 按仓库约定 `.trae/specs/.gitignore` 第 3 行忽略 `raw/`，故 R/F/V 原始证据（`raw/source-capture.md`、`raw/design-f.md`）**仅本地保留、不入库**，README 已就此显式说明、不再做链接引用。

## Task Dependencies

- Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7
- Task 3 与 Task 4 有数据契约依赖（`data.js` 结构为 Task 4 的输入），顺序不可颠倒。
