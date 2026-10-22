---
status: "completed"
version: 1.1
source: "https://vibeknow.com"
session: "sc-20261021-vibeknow-research"
---
# VibeKnow 视频专家全面调研复盘 - Product Requirement Document

## Overview
- **Summary**: 以七概念方法论（场景4 知识沉淀，链路 R→I→E→V→C）对 VibeKnow 视频专家做全面调研，产出可溯源的事实清单、四元组洞察、可迁移方法论模式与四视角对抗审查记录，并落盘为对外可读调研报告。
- **Purpose**: 为 SpecWeave 沉淀「AI 视频生成类 SaaS 产品全面调研」的可复用调研范式与可迁移方法论模式，同时为知识库提供一份有证据强度分级的第三方产品评估底稿。
- **Target Users**: 知识库读者（选型/调研者）、SpecWeave 模式库维护者、AI 工具链选型决策者。

## Goals
- 采集 VibeKnow 产品功能、技术架构（CLI）、商业化定价、竞品定位、口碑与风险五个维度的可溯源事实
- 产出统一编号、带来源 URL 与访问日期的事实清单，并显式登记数据冲突与证据缺口
- 从事实中提炼 ≥3 条四元组洞察（陈述／证据编号／反常识／可执行行动）
- 萃取 1 个可迁移方法论模式（含触发条件、核心步骤、反模式、检验标准、跨域迁移），标注 L1-draft
- 执行四视角对抗审查，≥5 条实质意见，≥2 条采纳并回写修正
- 落盘报告至根 `docs/retrospective/reports/competitive-analysis/`，完成索引登记与原子提交

## Non-Goals (Out of Scope)
- 不对 VibeKnow 做实测账号购买与成片产出验证（成本与时间不可控，列为待验证项）
- 不撰写商业计划书、投资建议或采购决策结论
- 不做代码级逆向工程，不审计 VibeKnow 服务端实现
- 不翻译官网教程，不复刻其产品教程内容

## Background & Context
- VibeKnow 为公开可访问的 AI 知识视频创作平台（中国站 vibeknow.com，英文站 vibeknow.ai），内容敏感度判定为公开（Public）
- 官网、定价页、教程站、npm/GitHub 开源 CLI、第三方评测均为无访问控制的公开信源，可直接引用
- 存在双站点（中文站 / 英文站）口径并存、中英文定价与积分体系不同的事实基础，须按冲突登记处理
- 仓库已有同类型范式参照：`docs/retrospective/reports/competitive-analysis/retrospective-openkylin-evaluation-20261014/`（一报告一子目录 + index.md toctree + README.md + facts-*.md 附录）

## Functional Requirements
- **FR-1**: 五维度事实采集（产品功能全景 / 技术架构与 CLI / 商业化与竞品 / 口碑与风险 / 官方口径基线）
- **FR-2**: 统一编号事实清单（按四维度分段编号 PRO/TEC/COM/RP-xxx），每条含事实陈述、来源 URL、访问日期
- **FR-3**: 数据冲突登记表（同一指标多值并陈，不裁决，编号 C-x）
- **FR-4**: 未获取项／证据缺口清单（商业化段 E-x、口碑段 G-x）
- **FR-5**: ≥3 条四元组洞察，每条含证据引用的事实编号
- **FR-6**: ≥1 个可迁移模式，结构含触发条件／3–7 步核心做法／≥3 反模式／检验标准／≥1 跨域迁移
- **FR-7**: 四视角对抗审查记录（魔鬼代言人／新人／老板／未来），含意见清单与修正回写记录
- **FR-8**: 报告主体落盘 + 附录拆分（facts-*.md）+ 目录索引（index.md toctree）
- **FR-9**: 模式入库登记（模式库 .md + `.meta/toml` 伴生 TOML + `index.md` toctree + README 索引刷新）
- **FR-10**: CMD-LOG 执行日志输出（session=sc-20261021-vibeknow-research）
- **FR-11**: Spec 三件套创建与主题看板刷新（docgen）

## Non-Functional Requirements
- **NFR-1**: 报告语言为中文，产品名/命令/参数/模式名保留英文原文
- **NFR-2**: 事实陈述剥离因果与评价词，仅保留可验证客观陈述
- **NFR-3**: 每条事实可独立回溯到来源 URL 与访问日期（2026-10-21）
- **NFR-4**: 结论强度与证据等级对齐，单一厂商口径数据降级引用
- **NFR-5**: 报告结构对齐仓库既有同类报告骨架，便于横向对照
- **NFR-6**: 产出物落盘路径全部位于根 `docs/` 下，禁止写入 `.agents/docs/`

## Constraints
- **Technical**: 调研信源限于公开可访问内容；CLI 事实以 npm/GitHub 官方 README 为准；Markdown 内部交叉引用使用相对路径，禁止 `file:///`
- **Business**: 第三方推广合作类评测（如实测推荐稿）须显式标注商业属性，结论降级
- **Dependencies**: `python .agents/scripts/docgen.py theme-dashboards`、`update-spec-readme`、`generate-readme.py --update`；原子提交走 atomic-commit-cmd 规范（路径级点名暂存）

## Assumptions
- 官网与定价页内容在访问日（2026-10-21）可复现，数值以当日抓取为准
- npm `vibeknow-cli` 与 GitHub `vibeknow/cli` 的 README 与包版本信息以访问日抓取为准
- 第三方评测的评分与用户量数据属外部转述，未经独立审计

## Acceptance Criteria

### AC-1: 事实清单规模与可溯源
- **Type**: `rule`
- **Given**: 五维度已采集信源
- **When**: 合并去重并编号
- **Then**: 事实总数 ≥20 条，按 PRO/TEC/COM/RP 四段统一编号，每条含事实陈述 + 来源 URL + 访问日期（2026-10-21）
- **Pass Condition**: 机械计数事实条数 ≥20，且逐条可定位到 URL
- **Evidence**: facts-*.md 附录全文（实际达成 106 条）

### AC-2: 事实去因果化与去评价化
- **Type**: `rule`
- **Given**: 已编号事实清单
- **When**: 执行 G1 逐条检查
- **Then**: 事实陈述中不出现「因为／所以／导致／说明／错误／失误／显然／最佳」等因果或评价词（技术术语用法与原文引述须逐条甄别说明）
- **Pass Condition**: 全文检索上述词命中项逐条甄别后，事实陈述内违例数为 0（或逐条说明为原文引述）
- **Evidence**: G1 检查记录（实际：四份附录按完整词表扫描命中 8 处 = 事实陈述行 4 处（3 处技术术语用法 + 1 处 GitHub issue 标题原文引述）+ 缺口/冲突登记表 4 处（2 处表头 + 2 处缺口描述）；事实陈述内违例 0）

### AC-3: 冲突与缺口显式登记
- **Type**: `rule`
- **Given**: 双站点／双来源同指标多值
- **When**: 编制冲突表与缺口表
- **Then**: 冲突项按「多值原样并陈、不裁决」登记（编号 C-x）；未获取项按 E-x（商业化）/ G-x（口碑）编号登记
- **Pass Condition**: 存在独立的冲突登记表与未获取项清单，且正文引用相应降级标签
- **Evidence**: 报告「数据冲突登记」与「未获取项清单」章节（实际：9 项冲突 C-1~C-9、24 项已编号缺口 E-1~E-13 / G-1~G-11 + 4 项未编号未获取点）

### AC-4: 四元组洞察完整性
- **Type**: `rule`
- **Given**: 事实清单
- **When**: 执行 I 阶段
- **Then**: ≥3 条洞察，每条含「陈述 / 证据引用（事实编号）/ 反常识 / 可执行行动」四要素，且维度不重叠
- **Pass Condition**: 逐条四要素齐备，引用编号可在事实清单中查到
- **Evidence**: 报告「洞察」章节

### AC-5: 模式可迁移性
- **Type**: `rubric`
- **Dimension**: 模式结构完整度与迁移潜力
- **Scale**: 1-5
- **Anchors**: 1 = 仅一句话总结；3 = 含步骤与反模式，缺检验标准或迁移；5 = 触发条件 + 3–7 步 + ≥3 反模式 + 检验标准 + ≥1 跨域迁移齐备
- **Pass Threshold**: >= 4
- **Evidence**: 模式库新增 .md 全文

### AC-6: 对抗审查实质性与回写
- **Type**: `rubric`
- **Dimension**: V 阶段审查覆盖度与修正闭环
- **Scale**: 1-5
- **Anchors**: 1 = 仅形式化表态；3 = 四视角齐备但意见笼统；5 = ≥5 条具体意见（含可复现的证伪点），≥2 条采纳并回写修正且标注重正位置
- **Pass Threshold**: >= 4
- **Evidence**: 报告「对抗审查记录」章节与 CMD-LOG

### AC-7: 落盘路径与索引登记
- **Type**: `rule`
- **Given**: 全部产出物
- **When**: 执行落盘
- **Then**: 报告目录位于 `docs/retrospective/reports/competitive-analysis/` 下并含 index.md toctree；模式登记于 `docs/retrospective/patterns/methodology-patterns/tools-automation/` 并同步 `index.md` toctree 与 `.meta/toml` 伴生 TOML
- **Pass Condition**: 路径全部在根 `docs/` 下；`docs/` 下不存在本次新增的 `.agents/docs/` 残留；toctree 条目与实体文件一一对应
- **Evidence**: 目录列表 + 索引 diff

### AC-8: 原子提交可审计
- **Type**: `rule`
- **Given**: 全部变更
- **When**: 执行原子提交
- **Then**: 单次提交仅含本调研产出物，Conventional Commits 格式（`type(scope): 中文主体`），路径级点名暂存，提交后 `git cat-file -p HEAD` 复验
- **Pass Condition**: 提交内容与本次产出物集合一致，提交信息合规，无 `git add .`
- **Evidence**: `git show --stat HEAD`

### AC-9: 待验证清单可执行
- **Type**: `rule`
- **Given**: 未实测项与不可验证口径
- **When**: 编制待验证清单
- **Then**: 每项含待验证问题、验证方法、所需成本/权限级别、优先级
- **Pass Condition**: 条目均具备四要素
- **Evidence**: 报告「待验证清单」章节

## Open Questions
- [ ] VibeKnow 中文站与英文站的积分换算人民币/美元汇率口径如何统一（待官方说明或实测）
- [ ] 官方宣称的「一条成片 ≈16 元」在不同模式（PPT 讲解 / 数字人 / 手绘）下的实际积分消耗差异（需实测）
- [ ] CLI 的 `--engine agent` 与 `--engine pipeline` 在同一素材上的产出质量与积分消耗对比（需实测账号）
- [ ] 50,000+ creators 与 4.5/5 独立评测均分是否具备可独立审计的第三方信源
