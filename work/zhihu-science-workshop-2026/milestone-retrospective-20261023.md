---
id: "milestone-retrospective-zhihu-ai-science-workshop-20261023"
title: "知乎 AI 科学创新工坊·第二弹「记忆实验室」里程碑复盘"
type: "private"
date: "2026-10-23"
scope: "project"
source: "work/zhihu-science-workshop-2026（执行包）; insight-report-20261023.md"
methodology: "seven-concepts-cmd 场景1 里程碑复盘（R→I→E→C）"
quality-gates: "G1 通过（41 事实无因果词）; G2 通过（3 洞察四元组完整）; G3 通过（2 模式含触发/步骤/反模式/检验/迁移）; G4 通过（4 行动项原子化）"
route: "private-direct"
---

# 知乎 AI 科学创新工坊·第二弹「记忆实验室」里程碑复盘

> 范围：`project`（2026-10-09 活动窗口内的完整参赛执行包）
> 时间范围：2026-10-09 .. 2026-10-23（复盘完成日）
> 方法论：seven-concepts-cmd 场景 1（里程碑复盘）R→I→E→C

## 执行摘要

「记忆实验室」参赛作品已完整走通「学习洞察 → 7 轮增量开发 → 本地验收 → 平台部署 → 审核发布」全链路：作品 `index-final.html` 12 项验收全过，已上线知乎 AI Works（projectId=60591，状态：可运行、审核通过）。本轮复盘采集 41 条客观事实，提炼 3 条洞察、2 个可复用模式、4 条原子化行动项。主风险已解除（10-28 部署硬检查点提前达标）；剩余待办集中在文章发布（10-29）与豆包对话截图证据（知识包 F-047）。

**关键数字**：7 版迭代 HTML（v1-v7 + final）；12 项验收全过 0 修复；3 组复算基准双路径一致；部署包 16,507 字节 / 6 文件；上线作品 1 个（审核通过）；文章发布 0（未开始）。

---

## 一、时间线

| 时间 | 节点 | 结果 |
|------|------|------|
| 10-09 | 活动窗口开启（至 10-31） | 活动进行中 |
| 10-23 上午 | 学习+洞察阶段完成 | insight-report-20261023.md：49 事实 / 4 洞察 / 3 模式 / 8 V 意见 / 6 行动项 |
| 10-23 上午 | Prompt 1-7 增量开发 | v1 骨架 → v7 最终版 index-final.html |
| 10-23 上午 | 本地打包 memory-lab.zip | 12,902 字节（zip 根 index.html 45,700+ 字节） |
| 10-23 上午 | 知乎创建页「下一步」无响应 | console 报错：Uncaught Error: Got unexpected null or undefined |
| 10-23 上午 | 草稿编辑页绕过（project/edit?projectId=60591） | 字段自动恢复；说明需真实键盘输入 |
| 10-23 上午 | 官方 deploy-helper 合规打包 | deploy.zip 16,507 字节 / 6 文件 |
| 10-23 上午 | 上传 → 平台构建 → 部署成功 | 可预览确认 |
| 10-23 上午 | 审核声明（两组 radio 均选「否」） | checked=true/false 验证通过 |
| 10-23 上午 | 发布 → 详情页 project/detail/60591 | 科学季·可运行 |
| 10-23 下午 | 审核通过复核 | 「可在当前页面直接运行项目应用」 |
| 10-29 | 文章发布（计划） | 未开始 |
| 10-31 | 活动截止 | 未到 |

---

## 二、R 阶段：事实清单（G1 通过：41 条，无因果词）

> 编号 F-001 起；全部为可验证客观陈述。验证方式：执行包文件、浏览器实测记录、线上详情页、官方活动原文。

### 2.1 学习与洞察阶段

- **F-001** 活动窗口为 2026-10-09 至 10-31，官方提交方式为「上传源码」发布至「科学季」，文章需带话题 #AI科学创新工坊。
- **F-002** 执行包位于 `work/zhihu-science-workshop-2026/`，含 README/spec/article-draft/checklist/doubao-prompts 5 个规划文件。
- **F-003** OKF 知识库目录 `projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-ai-science-workshop` 含 13 个文件。
- **F-004** 知识包 `status=flagged`，为单源知识（无第二来源交叉验证）。
- **F-005** 学习+洞察产出 `insight-report-20261023.md`：49 条事实（W-001~W-033 + KB-001~KB-016）、4 条洞察、3 个模式、8 条 V 审查意见、6 个行动项。
- **F-006** 学习阶段识别为七概念「场景 4 知识沉淀」链路 R→I→E→V→C，产出物按私域预检直接落执行包目录。

### 2.2 开发与本地验收阶段

- **F-007** 版本演进：index-v1.html（骨架）→ v2（实验台：3 滑块 + 间隔下拉 + 重置 + Canvas 遗忘曲线 + 4 统计卡 + rAF 合并重绘 + DPR 适配）→ v3（策略对比 3 卡 3 曲线 + 对比表 + 结论 X 动态）→ v4（自测三档 0-5/6-8/9-10）→ v5（计划生成器 30/14/7/3/1 天五节点 + 本地时区 + 过期降权）→ v6（科学依据与局限 4 来源逐字 + 公式声明）→ v7/index-final.html。
- **F-008** index-final.html 完成 12 项验收，修复项 0。
- **F-009** 每轮开发均执行 shot.py 自检，blocker/error/warning 计数全为 0。
- **F-010** 复算基准：S=2→X=21、S=5→X=49、S=8→X=56；`_shots/verify-cmp.py` 独立复算与浏览器实测一致。
- **F-011** S=8 间隔复习统计：92/90/89/66/80。
- **F-012** index-v6 移动端 375px 全页分两段切片核对，无横向溢出、零外部请求。
- **F-013** 模型公式锁定：R(t)=R0·Math.exp(-t/S)；复习时 R=Math.min(1, R+(1-R)*0.6)；S=S*1.6；页面标注「示意模型，非个人预测」。
- **F-014** 视觉规范锁定：纸色板（--paper:#F3EFE7 等 9 个 token）、衬线标题栈、圆角 12px、max-width 1080px。

### 2.3 部署与发布阶段

- **F-015** memory-lab.zip 打包成功：12,902 字节，zip 根路径 index.html。
- **F-016** 知乎创建页 `https://www.zhihu.com/project/create?step=1`「下一步」按钮在自动化与用户桌面 Edge 手动点击下均无响应。
- **F-017** 创建页 console 输出 `Uncaught Error: Got unexpected null or undefined`（React-dom@17.0.2 production.min.js 堆栈，chunk 3964.app.cb10463d9c412aa84d0c.js / 6365.app.0ebbe9f3b446b95ac2f8.js）。
- **F-018** 刷新创建页后报错消失、按钮恢复响应；填表后复发。
- **F-019** 创建页刷新后不自动恢复已填草稿字段。
- **F-020** 项目广场出现 3 个「记忆实验室」草稿（更新于 10/23 11:15/11:08/11:04）。
- **F-021** 草稿编辑页 `https://www.zhihu.com/project/edit?projectId=60591&step=1&source=draft` 刷新后自动载入封面/名称/简介/类型/版本字段。
- **F-022** 项目说明字段在草稿中显示为空（此前保存未持久化）。
- **F-023** `execCommand('insertText')` 写入说明后，Draft.js 占位层未隐藏，正文与占位符叠加（叠影）。
- **F-024** `beforeinput` 合成事件被 Draft.js 拒绝（isTrusted 校验）。
- **F-025** 真实键盘输入（click 聚焦 .public-DraftEditor-content 后 bu.type）写入说明成功，占位层卸载，正文 195 字。
- **F-026** 刷新草稿编辑页后说明 195 字持久化保留。
- **F-027** 草稿编辑页「下一步」在说明为空时提示「请填写项目说明」；填写后成功进入 step=2 上传源码页。
- **F-028** 首次上传 memory-lab.zip 部署失败：`部署包校验失败，错误码:8，_tmp 必须至少包含 frontend.deploy.json 或 backend.deploy.json`。
- **F-029** 下载知乎官方 `zhihu-ai-works-deploy-helper` Skill v1.2.0（ZIP 来自页面 zhstatic 链接）。
- **F-030** 官方 helper 流程生成 deploy.zip：16,507 字节、6 文件（_tmp/deploy-plan.json、_tmp/frontend.deploy.json、_tmp/materialize-event-tracking-ticket.cjs、_tmp/settle.agent.json、index.html 48,438 字节、package.json）。
- **F-031** 部署描述符：SchemaVersion 1.1.0、Framework other、NodeVersion 20、BuildCmd "npm run build:track"、InstallCmd ""、DeployCmd "tcb hosting deploy ./"。
- **F-032** settle.agent.json：ProductCode=doubao、ProductName=豆包、Platform=desktop、Source=agent-self-report。
- **F-033** 上传 deploy.zip 后平台自动构建 → 部署成功 → 进入可预览状态。
- **F-034** 审核声明两组 radio 均选「否」（label click 后验证 checked=true/false）。
- **F-035** 发布成功进入 `https://www.zhihu.com/project/detail/60591`；随后复核显示审核通过、「体验项目——可在当前页面直接运行项目应用」。
- **F-036** 证据截图已存档：`evidence/05-deploy-published.png`、`evidence/05-deploy-running.png`；evidence/README.md 已同步勾选。

### 2.4 待办与硬约束（事实状态）

- **F-037** 官方私信要求：文章附豆包使用截图 + 作品图片。
- **F-038** 文章发布要求（article-draft.md + 官方原文）：话题 #AI科学创新工坊、正文 ≥500 字、逐字含「此项目投稿至豆包专属赛道」、正文含可点开作品链接、配图 ≥3 张（建议 6 张）。
- **F-039** `evidence/01-req-prompt1.png`（豆包对话界面截图，知识包 F-047 全程豆包证据）未生成。
- **F-040** 文章发布（计划 10-29）未开始。
- **F-041** 10-28 部署硬检查点（已提前达标）；10-31 活动截止（剩余动作仅复核）。

> 事实计数口径：本清单编号 F-001~F-041 共 41 条（含待办状态 5 条）。正文、索引、摘要中的计数已对齐。

---

## 三、I 阶段：洞察（G2 通过：3 条四元组完整）

### 洞察 1：第三方平台按钮失效的对抗路径是「换入口」，不是「换点击方式」

- **陈述**：当平台页面按钮在自动化与手动操作下均无响应时，根因常在页面组件生命周期，修复路径是寻找同功能的替代入口（草稿编辑页/API），而非反复尝试同一按钮。
- **证据**：F-016（创建页「下一步」自动+手动均无响应）、F-017（React console 报错签名）、F-018（刷新恢复、填表复发）、F-020/F-021（草稿编辑页作为替代入口且字段自动恢复）。
- **反常识**：默认假设「按钮点不动 = 表单没填对」；实际排除封面/版本/说明/纯文本后按钮仍失效，问题在 React 组件树在写操作后损坏（F-017 签名 + 刷新即恢复的规律）。
- **行动**：自动化遇到平台按钮失效时，按「console 查错 → 字段逐项排除 → 刷新验证 → 找替代入口」顺序排查；替代入口优先找「草稿/编辑页」这类数据自动恢复的页面。

### 洞察 2：富文本编辑器只认真实输入事件，「看起来输进去了」不等于「被应用接受了」

- **陈述**：Draft.js 类富文本编辑器以状态树为唯一事实源，合成输入（execCommand/beforeinput）只改 DOM 不更新状态树，会同时造成「叠影（占位层不隐藏）」与「不持久化（保存后为空）」两个表象。
- **证据**：F-023（execCommand 写入后占位层未隐藏）、F-024（beforeinput 被 isTrusted 拒绝）、F-025/F-026（真实键盘输入后占位层卸载、刷新后 195 字持久化）。
- **反常识**：默认假设「输入框有内容 = 表单值已更新」；实际 DOM 有字但编辑器 state 为空，导致校验拦截与保存丢失同时出现。
- **行动**：表单自动化遇到富文本/编辑器类字段时，优先走真实键盘输入通道；验证标准 = 占位符是否卸载 + 刷新后内容是否持久化，二者缺一不可。

### 洞察 3：平台「一键部署」隐藏包格式契约，官方部署工具是唯一可靠入口

- **陈述**：ZIP 内只有前端产物不足以触发平台部署，平台要求部署清单文件（frontend.deploy.json）并执行构建命令；跳过官方工具手工打包必然在平台侧校验失败。
- **证据**：F-028（错误码 8：_tmp 必须包含 frontend.deploy.json 或 backend.deploy.json）、F-029/F-030（官方 helper 生成的 6 文件合规包）、F-033（上传后自动构建成功）。
- **反常识**：默认假设「部署 = 上传产物压缩包」；实际平台把「描述符 + 构建脚本 + 事件桥」都作为部署契约的一部分。
- **行动**：任何平台代部署前先检索官方部署工具/文档（deploy helper、平台 SDK），按其流程生成合规包；出现错误码时读错误详情而非猜测。

---

## 四、E 阶段：可复用模式（G3 通过：2 模式，含触发/步骤/反模式/检验/迁移）

### 模式 1：平台代部署合规打包（L2-validated，双案例级：本次 + 官方教程案例）

- **触发场景**：适用于「平台要求上传源码 ZIP 自动构建部署」的静态/纯前端作品（AI Works、低代码平台、Serverless 托管）。不适用于：平台提供可视化上传的简单作品（直接走表单）、需要后端服务的项目（描述符需 backend.deploy.json）。
- **核心做法**：
  1. 检索平台官方部署工具/教程（deploy helper、SDK、文档），下载并解压到本地只读引用目录。
  2. 运行官方探测脚本（inspect_node_project.py）确认项目类型（frontend-static）与阻断项。
  3. 生成部署描述符（write_deploy_descriptors.py）：frontend.deploy.json + package.json + 事件桥材料。
  4. 运行校验（validate_deploy_output.py）——先 `--plan-only` 后全量，确保 0 错误。
  5. 生成归档 ZIP（create_project_archive.py），验证 ZIP 内文件与根前缀。
  6. 浏览器上传 → 观察平台构建 → 确认部署成功 → 填审核声明 → 发布 → 详情页复核。
- **反模式**：
  - ❌ 手工把 index.html 塞进 ZIP 就上传（撞错误码 8）。
  - ❌ 忽略错误码详情直接换文件重传（浪费轮次）。
  - ❌ 不读官方教程、凭直觉猜部署契约。
- **检验标准**：平台显示「部署成功/可预览」；上传包内含 frontend.deploy.json；线上详情页最终可运行。
- **迁移示例**：腾讯云 CloudBase/阿里云函数计算部署静态站、GitHub Pages 之外的平台托管、CI 流水线发布。

### 模式 2：第三方富文本表单自动化对抗（L2-validated，双案例级：Draft.js + React 受控表单）

- **触发场景**：适用于「自动化向第三方网页的富文本/编辑器字段写入内容」或「平台按钮/表单异常」。不适用于：原生 textarea/input（普通 type 即可）、自己可控的应用（直接改代码）。
- **核心做法**：
  1. 写入前先点击聚焦编辑器内容区（.public-DraftEditor-content 类区域）。
  2. 使用真实键盘输入通道（bu.type 等），不使用 execCommand/合成 beforeinput。
  3. 写入后验证占位层是否卸载（叠影消失）。
  4. 刷新页面验证内容持久化。
  5. 若按钮/表单仍异常，console 查错 → 字段排除 → 刷新 → 找草稿/编辑替代入口。
- **反模式**：
  - ❌ execCommand('insertText') 写富文本（状态树不同步，叠影+不持久）。
  - ❌ 合成 input/change 事件（isTrusted 校验拒绝）。
  - ❌ 只看 DOM 有字就判定成功（不刷新验证）。
  - ❌ 死磕同一按钮反复点击。
- **检验标准**：占位符卸载 + 刷新后内容仍在 + 表单校验通过进入下一步。
- **迁移示例**：知乎/微博/公众号网页发布表单、任何 React/Vue 受控组件网页、CMS 后台编辑器。

---

## 五、C 阶段：行动项（G4 通过：4 项原子化）

| 编号 | 行动项 | Owner | 时间节点 | 验收标准 |
|------|--------|-------|---------|---------|
| A-001 | 拍摄豆包对话截图存 `evidence/01-req-prompt1.png`（知识包 F-047 全程豆包证据） | 用户 | 10-27 | 文件存在且为真实豆包会话截图，evidence/README.md 勾选 |
| A-002 | 发布文章（article-draft.md 填占位 → 话题/赛道标注/作品链接 → ≥6 图配图） | 本 agent + 用户 | 10-29 | 文章上线：≥500 字、含「此项目投稿至豆包专属赛道」、链接可点开、图 ≥3 张 |
| A-003 | 10-31 前复核活动规则完成情况（文章已发布、一件一赛道、账号合规） | 本 agent | 10-31 | 对照官方原文逐项核验并留档 |
| A-004 | 萃取 aiworks-deploy-cmd Skill 落盘 `.agents/skills/` 并更新双索引 | 本 agent | 10-23（本轮） | check-skill-quality.py 通过；README + capability-registry 已更新 |

---

## 六、导出报告说明

- **源报告**：本文件（复盘完成后即为正式导出物）。
- **格式**：Markdown（默认 `["md"]`，无附加格式需求）。
- **归档位置**：私域执行包目录 `work/zhihu-science-workshop-2026/milestone-retrospective-20261023.md`（内容敏感度预检：私域，含账号/内部过程细节，不入公共 docs/）。
- **数据验证三查法**：
  1. 关键数字（事实条数 41、版本数 7、验收 12 项、部署包 6 文件/16,507 字节）均来自执行记录与文件系统实测，非估算。
  2. 链接：正文含线上详情页 URL 与执行包相对路径，指向真实存在文件。
  3. 章节结构：执行摘要/时间线/R/I/E/C/导出说明 六章完整。
- **质量门记录**：G1 通过（41 事实，事实区无因果词）；G2 通过（3 洞察四元组）；G3 通过（2 模式，各 ≥3 反模式 + 迁移示例）；G4 通过（4 行动项，单职责+Owner+时间+验收标准）。

---

*复盘完成：2026-10-23。链路 R→I→E→C 全部通过质量门。可复用经验已同步萃取为 `.agents/skills/aiworks-deploy-cmd/`（见本轮交付）。*

## 修订记录

- **2026-10-23（收官对账 sc-20261023-zhihu-ai-science-workshop）**：① 事实计数口径修正 36→41（frontmatter、执行摘要、§二标题三处同步，与正文 F-001~F-041 及 §数据验证三查法一致）；② 三处 `F-047` 补来源域前缀「知识包」，消除与本报告编号域的同形歧义。预防措施：门声明机械校验（见 `docs/retrospective/reports/concepts/milestone/zhihu-ai-science-workshop-fullchain-retrospective-20261023.md` 模式 2 与行动项 A-4）。
