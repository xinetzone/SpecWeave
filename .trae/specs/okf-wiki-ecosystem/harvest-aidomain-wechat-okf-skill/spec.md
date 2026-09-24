---
status: "draft"
id: "harvest-aidomain-wechat-okf-skill"
title: "爱域研究社公开文章 OKF Wiki 与自动化 Skill"
source: "User Request + seven-concepts-cmd"
methodology: "seven-concepts:R→I→E"
content-sensitivity: "public-only"
---

# 爱域研究社公开文章 OKF Wiki 与自动化 Skill Spec

## Why
用户希望系统学习截图所示微信公众号“爱域研究社”的公开内容，并将可复用知识沉淀为 OKF Wiki 教程，同时把经过验证的流程萃取为可重复执行的自动化 Skill。原始请求中的“全部内容”范围、公开入口和版权边界需要先被明确化，才能保证结果可核验、可持续更新且不复制受版权保护的全文。

## What Changes
- 以“爱域研究社”为账号锚点，建立公开文章发现、身份核验、去重和覆盖率记录流程。
- 仅处理无需登录或特殊邀请码即可访问的公开文章；失败、受限或无法确认归属的内容进入未获取清单，不伪造补全。
- 采用原创教程 + F 编号事实索引，不生成逐篇全文镜像；每条具体事实保留原文链接、标题、发布日期和定位信息。
- 按七概念知识沉淀链路执行 `R→I→E`：事实采集、机制洞察、可迁移模式萃取；必要的对抗审查作为质量门，不改变主链路。
- 设计一个可复用 Skill，覆盖公开账号确认、文章采集、信源距离判定、P0 核验、OKF bundle 生成、时效标记、索引更新和验证报告。
- 为 Skill 设计最小评测集，验证触发准确性、版权边界、停止条件、F 编号一致性和幂等重跑行为。

## Impact
- Affected specs: OKF/Wiki 知识生态、方法论萃取、Skill 开发规范。
- Affected code: `projects/awesome-okf-xs/doc/bundles/` 下的目标 bundle；`.agents/skills/` 下新增自动化 Skill；相关索引与验证记录。
- 预期公开产物位置：`projects/awesome-okf-xs/doc/bundles/`；Skill 位于 `.agents/skills/`。抓取原文缓存和受限内容不得进入公开文档中心。

## Scope and Non-Goals
- 范围：账号“爱域研究社”的公开可检索文章，主题由实际文章集合归纳，不预设单一观点。
- 不包含：需登录/验证码/邀请码的内容、付费或内部材料、未经授权的全文复制、绕过平台访问控制、无法核验归属的转载。
- “全部”定义为在执行时点、指定公开入口和可用检索能力下发现并成功核验的文章集合；覆盖率必须以清单和停止条件说明。

## ADDED Requirements
### Requirement: Account and source verification
系统 SHALL 在采集前确认账号名称、公开入口、文章归属信号和执行时点，并记录发现渠道。

#### Scenario: Account confirmed
- **WHEN** 用户确认截图账号为“爱域研究社”且授权处理公开内容
- **THEN** 采集流程建立账号级 source manifest，并把每篇文章绑定到可核验入口。

#### Scenario: Account or ownership uncertain
- **WHEN** 页面无法确认公众号归属或仅发现第三方转载
- **THEN** 条目标记为 `unverified`，不得进入稳定知识正文。

### Requirement: Public-only collection with stopping rules
系统 SHALL 只采集无需特殊权限即可访问的公开内容，并在反爬、登录墙、验证码或连续失败时停止重试并记录原因。

#### Scenario: Public article accessible
- **WHEN** 文章正文、标题、日期和 canonical URL 可获取
- **THEN** 保存最小必要信源登记，进入 F 编号事实采集。

#### Scenario: Restricted or inaccessible article
- **WHEN** 文章需要登录、验证码、邀请码，或自动化访问连续失败
- **THEN** 记录 `not-collected` 及原因，不绕过访问控制，不用猜测内容替代。

### Requirement: Traceable fact and insight separation
系统 SHALL 将“事实”“作者观点”“执行者洞察”分层，并为具体声明提供 F 编号和来源定位。

#### Scenario: Factual claim
- **WHEN** 文本包含日期、数量、定义、步骤或明确引述
- **THEN** 登记为 F 编号，附文章 URL、标题、日期和段落/页面定位。

#### Scenario: Interpretation
- **WHEN** 内容是作者观点或执行者对多篇文章的机制归纳
- **THEN** 显式标注观点/洞察，不伪装成官方事实，并在必要处经过 P0 核验或标记单源。

### Requirement: OKF tutorial generation
系统 SHALL 按信源先行顺序生成 OKF bundle：`references/`、`concepts/`、必要时 `examples/`，最后生成各级 `index.md` 和 `log.md`。

#### Scenario: Bundle generated
- **WHEN** 文章清单、事实表和核验记录达到质量门
- **THEN** 生成原创中文教程、主题索引、时效字段、sources 字段和可达的 toctree。

#### Scenario: No reproducible operation
- **WHEN** 文章只提供观点、案例或关系沟通分析，缺少可复现输入/输出步骤
- **THEN** 不创建空的 `examples/`，将方法步骤写入 concepts 并说明其非实测教程属性。

### Requirement: Reusable automation Skill
系统 SHALL 提供一个不依赖特定公众号的 Skill，支持公开内容发现、双方案采集、幂等重跑、dry-run 预览、失败清单和 OKF 验证。

#### Scenario: Dry-run
- **WHEN** 用户要求预览或首次运行
- **THEN** Skill 只生成账号确认结果、文章 manifest、候选主题和预计产物，不写入正式 bundle 或索引。

#### Scenario: Idempotent rerun
- **WHEN** 已存在同账号/同文章的 manifest 或 bundle
- **THEN** Skill 读取既有 `log.md` 和索引，执行更新/补核验判定，不静默覆盖，不重复增加计数。

#### Scenario: Skill trigger
- **WHEN** 用户表达“公众号文章转 OKF/Wiki”“抓取某公众号公开内容”“把这套流程做成 Skill”等同义需求
- **THEN** Skill description 能稳定触发，并把权限、版权和范围确认作为第一步。

### Requirement: Quality gates and auditability
系统 SHALL 对 F 编号双份一致、链接可达、toctree 完整、frontmatter、敏感路径和时效状态执行机械验证，并记录七概念阶段日志。

#### Scenario: Core claim unverifiable
- **WHEN** 核心数字、日期、官方表态或成效声明无法找到独立权威来源
- **THEN** bundle 标记 `status: flagged`，在正文和 verification 中显式说明单源边界与复核日期。

#### Scenario: Verification complete
- **WHEN** 所有规则检查和必要 rubric 达到阈值
- **THEN** 产物进入独立审查；审查通过前不得宣称任务完成。

## Acceptance Criteria
- **AC-1 (rule)**：账号 manifest 明确记录“爱域研究社”、公开入口、采集时点、发现渠道和停止条件。
- **AC-2 (rule)**：每篇纳入文章都有唯一 URL、标题、日期（若可得）、归属证据和 `F-xxx` 覆盖；受限内容全部进入未获取清单。
- **AC-3 (rule)**：OKF bundle 不含逐篇全文镜像；具体数字、日期、步骤和引述均可回溯到 F 编号与来源定位。
- **AC-4 (rubric)**：教程结构在“事实层→机制层→可迁移路径层”之间清晰分层，评分 0-2，达到 ≥1.5；证据为知识地图与正文抽查。
- **AC-5 (rule)**：bundle 的 frontmatter、toctree、sources、`status`、`stale_after` 和索引计数通过机械验证。
- **AC-6 (rule)**：自动化 Skill 具备 dry-run、幂等重跑、失败清单、公开性预检和最小评测集；不修改 vendor 文件。
- **AC-7 (rubric)**：Skill 在至少 3 个真实风格测试提示上能正确触发并遵守边界，评分 0-2，达到 ≥1.5；证据为 eval 输出与人工审查。

## Open Decisions
- 公开文章的具体发现入口（公众号历史页、搜索引擎、用户提供 URL 清单）需在实施阶段记录，不能假设单一入口覆盖全部文章。
- 账号内容若大量依赖图片、音频或短视频，应将其列为“未纳入公开文章集合”或另立授权项目，不在本 Spec 中扩展媒体转录。
