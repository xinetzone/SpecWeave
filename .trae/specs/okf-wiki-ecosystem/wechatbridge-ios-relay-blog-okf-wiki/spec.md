---
type: Specification
title: "WeChatBridge iOS 版博文 → OKF v0.2 wiki 教程"
description: "把微信公众号《开源微信流 APP…》全面学习并转化为 OKF v0.2 知识包，含 P0 核验与 status: flagged 判定"
tags: [spec, okf-wiki, blog-article, wechatbridge, ios, seven-concepts, 博文转化]
source: "https://mp.weixin.qq.com/s/94FP4Cl7JIQbxU5-i3B6og"
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-11-06T12:20:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-06T12:20:00+08:00" }
status: flagged
stale_after: "2027-01-31"
---

# Spec：微信博文 → OKF v0.2 知识包（WeChatBridge iOS 版 / 定验收方法论）

## 0. 任务与场景识别

- **用户输入**：`/七概念 全面学习 https://mp.weixin.qq.com/s/94FP4Cl7JIQbxU5-i3B6og，生成 okf wiki 教程到 D:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles 的恰当位置`
- **命令解析**：`/七概念` 是仓库斜杠别名 → `.agents/commands/seven-concepts.md`（L2 指令）+ `.agents/skills/seven-concepts-cmd/SKILL.md`（L1 门面）；能力注册表 `02-skills.md` / `03-commands-workflows-protocols-rules.md` 两处登记行已核对，非运行时 Skill 名。
- **场景**：场景 4「知识沉淀/方法论」，链路 **R→I→E→V→（C 登记）**；由 `blog-article-to-okf-wiki` 七阶段工作流承载；质量门 G1（事实）→ G2（骨架/归属/洞察）→ G3（信源先行）→ G4（对抗审查 + 机械门禁）。
- **产出边界**：用户显式指定 `projects/awesome-okf-xs/doc/bundles/`；子项目 `AGENTS.md` 规定公开内容入 `doc/bundles/`，与根 `AGENTS.md`「根 `docs/` 为文档中心」不冲突（本产物是子项目内部资产）。
- **流程偏差登记**：Skill Gotcha 记载 `mp.weixin.qq.com` 反爬确定、应直接用 `browser_use` 取 `#js_content`；**本次 WebFetch 直接返回完整正文与元信息，未触发回退**。无内容损失，已在 bundle `log.md` 登记。

## 1. 内容敏感度预检

| 判据 | 结果 |
|------|------|
| URL 形态 | `mp.weixin.qq.com/s/<id>` 公开文章（F-003） |
| `share?code=` / `token=` / 邀请码 / 企业内部域名 | 均无 |
| 判定 | **Public** |
| 工作流 | 标准 Spec Mode：spec 在 `.trae/specs/okf-wiki-ecosystem/wechatbridge-ios-relay-blog-okf-wiki/`，产出在子项目 `doc/bundles/` |
| 排除 | 不进 `playground/`，不触发「就高不就低」私域条款 |

## 2. 骨架判定（L3 操作可复现性两问）

| 问题 | 判定 | 依据 |
|------|------|------|
| Q1 是否有读者可照做的安装/配置/代码/调用/实测流程？ | **是** | 博文给出两段**可逐字复制的提示词**（F-046/F-047）、Agent 执行顺序（F-054）、iOS 五步使用流程（F-014/F-017/F-020/F-025/F-027）；官方仓库另有 `swift test` / `xcodegen` / `verify.sh` 等命令（F-070/F-079） |
| Q2 是否经作者实测、具备版本/输入/输出/步骤顺序？ | **是** | 模型版本明确（Kimi K3.1 Pro，F-037）；输入为两段提示词 + 既有仓库与两份基线文档；输出为 `docs/design/` 下两份可查文档（F-071/F-072/F-078）与验收记录（F-079）；步骤顺序为「确认理解 → 出文档 → 人审阅 → 按 T 编号执行 → 逐任务汇报 → 验收/复跑」 |

**结论**：两问皆是 → **技术教程/方法论骨架，设 `examples/`**（3 篇：两段提示词复现、自设计验收闸门、iOS 使用流程）。
**边界声明**：可复现的是「提示词驱动的文档/验收设计流程」，**不是 iOS App 安装**——App 未上架（F-010 且被官方口径收窄），examples 中不得伪造安装命令；全部示例显著标注「非官方、本知识包未实机验证」。

## 3. 归属判定决策树

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/products/wechatbridge-ios-relay/` | ✅ **采用** | ① 主线实体是 WeChatBridge 这一终端工具产品的 iOS 版（F-001/F-009）；② `products/` 已有 `wigolo`、`agent-reach`、`orca-ade`、`craft-anything`、`wechat-intelligence-hub` 等「微信博文经 OKF v0.2 转化」先例，分组可容纳非源码类 bundle；③ 单篇博文不新建分组 |
| `jishu/ai/products/wechatbridge/` | ❌ **避让** | 该目录已由**并行会话**创建并归属另一篇文章（`https://mp.weixin.qq.com/s/QdCiRiwjjc5uOvBW0nBZxw`，2026-09-24「虾说AI实验室」产品推介文，见 `.trae/specs/okf-wiki-ecosystem/wechatbridge-okf-wiki/spec.md`）。按幂等规则禁止静默覆盖，改用带语义后缀的独立 bundle 名，并在两束之间做「主题关联」说明分工 |
| `jishu/ai/practice/` | ❌ | 该组定位 AI 工程方法论/行业洞察（29 束）。本文虽有强方法论线，但主线仍是产品发布与功能说明；方法论由本束 `concepts/02`、`concepts/03`、`examples/` 承载即可 |
| `sheke/industry/` | ❌ | 非行业趋势/市场分析 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更 |

**幂等检查**：开工时 `products/` 下已有空的 `wechatbridge/`（含 `concepts/ examples/ references/` 三空子目录）与未登记的 `workbuddy-wechat-chat-forward-skills/`；二者均属并行会话在途产物。本束不触碰、不代接线，仅在 `log.md` 登记。

## 4. 信源距离与时效性

- 发文 **2026-10-27 16:28**（F-002），核验日 **2026-11-06**，间隔 10 天；星标、模型版本、上架状态均为高漂移项。
- 四层信源距离：
  1. **产品方自述/作者观点**（F-001~F-003、F-009~F-013、F-037~F-061）：须标「作者观点/厂商自宣」，成效数字（6 小时、55 分、1.7k star）一律 P0。
  2. **作者一手实测经博文转述**（F-014~F-036 的 UI 与操作细节）：多数无法从官方 README 逐字复核，标「博文单源」。
  3. **官方仓库一手件**（F-062~F-080）：GitHub REST API、README、dev-spec、schedule、验收记录——**最高可信**，用于收窄或证伪第 1/2 层。
  4. **权威第三方/媒体转述**（F-081~F-084）：Kimi 发布与权重开放、AA 评分、官方致歉公告、第三方实测——须标「媒体转述」，不得写成「已取得官方原文」。
- `stale_after: 2027-01-31`（flagged bundle 缩短复核周期）；到期前须复核 iOS 上架状态、灵动岛是否入版、权重开放后的模型口径。

## 5. P0 权威核验结论

详见 `references/verification.md`（**24 项 P0/P1：12✅ / 8⚠️ / 4❌**）。核心结论：

- ✅ 仓库真实存在、MIT/Swift、Mac/Windows 已发布、100 条分批、隐私边界、18 个工作日档期、S1–S11 与 186 测试、自修 bug、Obsidian 笔记结构、AA 55 分、官方致歉 25% 补偿等均获官方或权威第三方印证（F-062~F-084）。
- ⚠️ 8 项（V-13~V-20）：星标时点（1.7k → 2024）、6 小时净运行时长与官方记录跨 10-23/10-24 两天、通知长按换目标未真机、「图文合一 PDF」仅部分目标默认格式、「客户复盘」六项仅博文单源、Kimi 发布规格仅媒体转述层级、3D 能力作者未实测、「有点贵」与第三方「便宜约 80%」口径相反。
- ❌ 4 项（V-21~V-24，其中 2 项为**核心声明**）：
  1. **V-21 iOS 版「开发完成 / 正在提审、还没上架」**（F-009/F-010）与官方 README「iOS 版正在开发中」+ 路线图 `[ ] iOS 版` + 验收记录 R3–R6「待真机」+ §10 交付定义未全打勾冲突（F-065/F-066/F-077/F-080）。
  2. **V-22「灵动岛小入口 / 复制提示词」**（F-019）与官方 dev-spec §12「不在 v1」明列「灵动岛」冲突；官方仅记录通知横幅「快速投递」且 R7 待真机（F-077/F-080）。
  3. V-23「一次发完，哪家都能吃」（F-022）与验收记录「豆包/千问只发 TXT」「视频和压缩包仍发不了」冲突（F-080）。
  4. V-24 10-27 称「国产开源模型 / 国产开源第一梯队」，但完整权重 11-04 才公开（F-081）。
- **状态管理**：核心声明 ❌ → frontmatter `status: flagged` + verification.md 顶部明示 + index 已知边界提示 + 短 `stale_after` 安排复核。

## 6. 三层知识拆分（I 阶段知识地图）

| 层 | 文件 | 职责 |
|----|------|------|
| references/ | `article-source.md`（F-001~F-084 双份登记）、`verification.md`（24 项核验 + 勘误四张清单） | 信源先行，先于 concepts 落盘 |
| concepts/ | `00` 身份与信源距离；`01` iOS 中转站能力（博文口径 vs 官方口径）；`02` 「先写计划再让它跑 / 别聊需求定验收」；`03` 规格与档期的验收控制面（S/R/T/M/交付定义）；`04` 验收记录、自修 bug 与勘误落实；`05` 可迁移模式、洞察四元组与采用边界 | 概念化 + 洞察 + 模式萃取 |
| examples/ | `00` 两段提示词复现；`01` 自设计验收闸门；`02` iOS 五步使用流程 | 可照做流程（全部标「非官方 / 未实机验证」） |
| 根 | `index.md`（唯一含 `okf_version`）、`log.md` | 导航与变更/门禁/CMD-LOG 记录 |

## 7. ADDED Requirements

- **R-1**：全部数字、模型名、命令、文件名、日期携带 F 编号；不得出现 facts.md 之外的具体声明。
- **R-2**：`facts.md` 与 `references/article-source.md` 的 F 编号集合相等、连续无跳号（F-001~F-084）。
- **R-3**：勘误四张清单（日期/版本、成效数字溯源、口径对照、引文逐字）齐全；4 项 ❌ 与 8 项 ⚠️ 在正文逐项有对应表述。
- **R-4**：`status: flagged` 三处落地（frontmatter / verification 顶部 / index 已知边界），且正文并列呈现博文口径与官方口径。
- **R-5**：四级索引接入——`products/index.md`（导航行 + toctree）、`ai/index.md`、`jishu/index.md`、`bundles/index.md`（frontmatter / 计数行 / 节标题 / 表行 / mermaid）；计数先读现值再 +1，避免与并行会话冲突。
- **R-6**：所有 `index.md` 含 `{toctree}`；计数排除以 `:` 开头的指令行；相对链接可达，禁止 `file:///` 绝对路径。
- **R-7**：`okf_version: "0.2"` 仅出现在 bundle 根 `index.md` 与总索引类文件；其余文档只用 `type` 等字段。
- **R-8**：机械门禁 `check-bundles-index.py` / `check-toctrees.py` / `check-utf8.py` 逐一执行；不可用时执行 §7 手动等效清单并在 log.md 注明，禁止谎报「gates 通过」。
- **R-9**：不执行 commit/push（用户未要求）；在 log.md 登记 C 阶段提交顺序待办。
- **R-10**：不触碰并行会话在途目录 `wechatbridge/`、`workbuddy-wechat-chat-forward-skills/`，不代其接线。

## 8. 提交顺序（C 阶段，仅登记不执行）

① 子模块 `projects/awesome-okf-xs` 内提交（本束文件 + products/ai/jishu/bundles 四级 index + README.md + doc/index.md）→ ② 主仓库提交 spec（`.trae/specs/okf-wiki-ecosystem/wechatbridge-ios-relay-blog-okf-wiki/`）→ ③ 主仓库更新子模块 gitlink。使用 `git-commit-utf8.py` 显式列全文件，不 push。
