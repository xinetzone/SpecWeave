---
title: "行政人事岗位进修 OKF Wiki 教程束 - Product Requirements Document"
status: "draft"
---

# 行政人事岗位进修 OKF Wiki 教程束 - Product Requirements Document

## Overview

- **Summary**：在 `projects/awesome-okf-xs/doc/bundles/` 下新建第 16 个知识域 `workplace/`（职场与管理），下设 `hr/`（人力资源）与 `admin/`（行政办公）两个组、共 5 个 OKF v0.2 知识束，系统覆盖行政人事岗位的职业地图、HR 六大模块与三支柱、劳动法律合规、行政管理实务、公文写作五大进修主题。全部事实经官方信源核验并带 sources 溯源。
- **Purpose**：用户希望系统性进修「行政人事岗位」知识以提升职业能力，需要一份可自学、可查阅、可直接行动（清单/模板/案例/计算规则）的中文 wiki 教程；同时以七概念方法论 R→I→E 链路保证事实零推测、洞察有反常识点、模式可迁移。
- **Target Users**：行政/人事/HR 在岗人员与转岗求职者（0-5 年经验为主），以及需要劳动合规速查的中小企业管理者。

## Goals

- G1：建立行政人事知识体系的**地图级框架**（岗位版图 → 能力模型 → 进修路径 → 证书体系），让读者知道「学什么、按什么顺序学、怎么验证学会」。
- G2：HR 实务覆盖**六大模块 + 三支柱**双框架，并落到入职/离职/绩效/薪酬等高频操作清单。
- G3：劳动法律合规做到**数字级准确**（试用期上限、N/N+1/2N、加班费倍率、年休假天数、社保费率、仲裁时效等），每条可溯源到法条/官方文件。
- G4：行政实务覆盖资产、采购、会议、接待、印章、档案、证照、后勤、预算、安全保密十大职能域；公文写作覆盖 15 种法定公文与职场常用文书。
- G5：全部产出通过 awesome-okf-xs 三门门控（bundles-index / toctrees / utf8）与 YAML frontmatter 扫描，不破坏并行会话 WIP。

## Non-Goals

- N1：不做法律咨询替代品——wiki 为知识科普与实务指引，个案争议引导至 12333/劳动仲裁/专业律师。
- N2：不覆盖公务员/事业单位人事管理的特殊体系（职称评审仅在「证书体系」中与企业 HR 证书做区分性提示，不展开）。
- N3：不做具体地域政策（各地社保基数下限、落户、人才补贴差异极大）——只给国家层面规则 + 「以当地社保局公告为准」的行动指引。
- N4：不收录招聘营销内容（培训机构广告、保过班、挂靠证书等），并在证书束中设「防骗」反面清单。
- N5：不主动执行 git commit / push（用户未要求）；不触碰并行会话 daojia WIP 的任何文件。

## Background & Context

### 方法论与工作流

- 七概念编排：场景 4 知识沉淀，链路 **R（事实采集）→ I（洞察）→ E（批量生成）**；A（原子化）体现为 5 束拆分；V（对抗审查）由 Spec Mode 独立 Review 阶段承担。CMD-LOG session=`sc-20260901-hr-admin`。
- 内容敏感度：**公开内容（Public）**——公开法规、官方政策、通用职业知识 → 标准工作流，产出物落 `doc/bundles/`，Spec 工件落 `.trae/specs/`。
- OKF 束范式：以 `think/relationships/five-love-languages/` 为模板——束 = `index.md`（type: OKF, okf_version: "0.2"）+ `facts.md`（F-NNN 事实表 + S 信源登记）+ `insights.md`（陈述/证据/反常识点/行动启示四元组 + Mermaid 知识地图）+ `log.md` + `concepts/` + `examples/` + `references/`（三层各含 index.md hidden toctree）。

### R 阶段已核验 P0 事实摘要（完整事实在各束 facts.md 展开）

1. **证书改革**：企业人力资源管理师 2003 年起为人社部统考职业资格；依**人社厅发〔2020〕80号**（2020-07-20），水平评价类技能人员职业资格分批退出目录，该职业与劳动关系协调员同列附件第 67 项，**第一批 2020-09-30 前退出**；退出后转**社会化职业技能等级认定**（用人单位/社会培训评价组织发证，技能人才评价证书全国联网查询 osta），**退出前已发职业资格证继续有效**；现行标准为《企业人力资源管理师国家职业技能标准（2019年版）》，等级四级/中级工→一级/高级技师。另有独立序列：**经济专业技术资格（人力资源管理）**职称考试（初级/中级/高级，中国人事考试网），勿混淆。
2. **劳动合同法**（2007-06-29 通过）：第 10 条用工 1 个月内订书面合同；第 14 条无固定期限合同三情形；**第 19 条试用期上限：合同 3 个月以上不满 1 年→≤1 个月；1 年以上不满 3 年→≤2 个月；3 年以上及无固定期限→≤6 个月；同一单位同一劳动者只能约定一次试用期；不满 3 个月及以完成一定工作任务为期限的合同不得约定试用期**；第 39 条过失性解除 6 情形（无补偿）；第 40 条无过失性解除（提前 30 日书面通知或额外付 1 个月工资，即「N+1」的 +1）；**第 47 条经济补偿 N：每满 1 年付 1 个月工资，6 个月以上不满 1 年按 1 年，不满 6 个月付半个月**；**第 87 条违法解除/终止按第 47 条标准二倍付赔偿金（2N）**；第 83 条违法约定试用期按试用期满月工资标准、超法定期间付赔偿金。
3. **司法实践**：深圳宝安区法院案例确认「协商一致延长试用期」属二次约定试用期，违反强制性规定，员工签了协议仍判赔。
4. **HR 框架**：六大模块（人力资源规划、招聘与配置、培训与开发、绩效管理、薪酬福利管理、劳动关系管理，围绕选/育/用/留）；三支柱（Ulrich：COE 专家中心、HRBP 业务伙伴、SSC 共享服务中心）。
5. **五险一金**：养老单位 16%/个人 8%（国办发〔2019〕13号）；医疗单位约 6%/个人 2%，生育已并入医疗（国办发〔2019〕10号）；失业阶段性费率合计 1%（单位个人各 0.5%，人社部发〔2023〕19号延至 2024 年底）；工伤单位 0.2%-1.9%（八类行业基准费率，个人不缴）；公积金单位个人各 5%-12%（《住房公积金管理条例》下限 5%）。
6. **工时加班**：劳动法第 36 条日不超 8 小时、周不超 44 小时（国务院令第 174 号现行周 40 小时）；第 41 条加班一般日≤1 小时、特殊日≤3 小时且**月≤36 小时**；第 44 条加班费工作日 150%、休息日不能补休 200%、法定节假日 300%；月计薪天数 21.75 天；不定时/综合计算工时需行政审批（劳部发〔1994〕503号）。
7. **年休假**：国务院令第 514 号（2008-01-01 施行）：累计工龄满 1 年不满 10 年→5 天；满 10 年不满 20 年→10 天；满 20 年→15 天；应休未休按日工资 **300%** 付报酬。
8. **劳动争议**：《劳动争议调解仲裁法》（2008-05-01 施行）第 27 条仲裁时效 **1 年**；劳动关系存续期间拖欠劳动报酬不受时效限制，但终止后须 **1 年内**提出；程序为协商→调解→仲裁→诉讼（**仲裁前置**）；举证责任中用人单位掌握的证据由单位提供。
9. **行政实务**（招聘市场 JD 实证）：办公物资与固定资产全生命周期、会议全流程、公文流转、印章保管与用印登记、档案/合同/证照管理、商务接待、差旅、后勤（物业/网络/车辆/公寓）、行政预算与成本管控、安全消防保密、资质补贴申报、企业文化活动。
10. **公文**：《党政机关公文处理工作条例》（中办发〔2012〕14号，2012-07-01 施行）第 8 条 **15 种法定公文**：决议、决定、命令（令）、公报、公告、通告、意见、通知、通报、报告、请示、批复、议案、函、纪要。
11. **女职工保护**：国务院令第 619 号（2012）：产假 **98 天**（难产+15 天，多胞胎每多 1 婴+15 天；流产 15/42 天）；不得因怀孕生育哺乳降薪/辞退/解约；孕 7 个月以上及哺乳未满 1 周岁婴儿不得延长工时或安排夜班；每日 1 小时哺乳时间。
12. **工伤保险**：国务院令第 375 号（2010 年第 586 号修订）第 14 条 7 种应认定工伤、第 15 条 3 种视同工伤（含工作岗位突发疾病 **48 小时**内抢救无效死亡）、第 16 条 3 种不得认定（故意犯罪/醉酒吸毒/自残自杀）；第 17 条申请时限：单位 **30 日**内，单位未申请的职工/近亲属/工会 **1 年**内可直接申请（《工伤认定办法》人社部令第 8 号同义）。

### 信源登记（S 系列，实施期录入各束 facts.md）

- S1 人社部《专家谈2021年版国家职业资格目录》 https://www.mohrss.gov.cn/SYrlzyhshbzb/zcfg/SYzhengcejiedu/202112/t20211224_431173.html
- S2 人社厅发〔2020〕80号 PDF（广东人社转发） https://hrss.gd.gov.cn/attachment/0/500/500378/3995752.pdf
- S3 劳动合同法全文（全国人大） http://www.npc.gov.cn/zgrdw/npc/xinwen/lfgz/zxfl/2007-06/29/content_368169.htm
- S4 深圳宝安区法院「延长试用期协议=合法？」案例 https://www.bafy.gov.cn/zjbf/fywh/pfkt/content/post_1619716.html
- S5 劳动法全文（全国人大，2018 修正） http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296651.html
- S6 人社部「加班工资如何计算」（法规司，2024） https://www.mohrss.gov.cn/SYrlzyhshbzb/ztzl/rslyyhyshj/zcwd/202411/t20241111_529591.html
- S7 人社部「养老保险缴费比例」（法规司，2025） https://www.mohrss.gov.cn/SYrlzyhshbzb/ztzl/rslyyhyshj/zcwd/202505/t20250513_541950.html
- S8 职工带薪年休假条例（国务院令第514号，中国政府网） https://www.gov.cn/gongbao/content/content_859865.htm
- S9 劳动争议调解仲裁法（全国人大） http://www.npc.gov.cn/zgrdw/npc/xinwen/lfgz/zxfl/2007-12/29/content_1387809.htm
- S10 党政机关公文处理工作条例（中国政府网） https://www.gov.cn/zhengce/2013-02/22/content_2640088.htm
- S11 女职工劳动保护特别规定（国务院令第619号，中国政府网） https://www.gov.cn/zhengce/2012-05/07/content_2602602.htm
- S12 工伤保险条例（最高法公报；2010 修订） http://gongbao.court.gov.cn/Details/1d6feae971025aee45ea3949189bb0.html
- S13 工伤认定办法（人社部令第8号） https://www.mohrss.gov.cn/xxgk2020/gzk/gz/202112/t20211228_431606.html
- S14 劳动人事争议仲裁办案规则（人社部令第33号） https://www.mohrss.gov.cn/xxgk2020/gzk/gz/202112/t20211228_431661.html
- S15 行政岗 JD 实证（企查查/智联招聘公开岗位描述，仅用于职责框架佐证，不作为法规信源）

### 门控与环境基线（2026-09-01 实测）

- `python scripts/check-bundles-index.py`：**通过**，15 域 / 69 组 / 347 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。
- `python scripts/check-toctrees.py`：**通过**，全部 index.md 引用有效、内容文档均可达。
- `invoke gates.*` 在本机 base conda 环境不可用（缺 invocations 包）→ 全程直跑 stdlib 脚本（check-bundles-index / check-toctrees / check-utf8）。
- **并行会话 WIP 警示**：子模块内存在他会话未提交变更（`M doc/bundles/index.md`、`M doc/bundles/think/index.md`、think/daojia 下 9 个未跟踪束目录）。共享文件 `doc/bundles/index.md` 我方也必须修改 → 铁律：只 add 己方文件；add 与 commit 分两次工具调用且中间核对 `git diff --cached --name-only`；禁止 reset/merge --abort；用户未要求不 commit。

## Functional Requirements

- **FR-1（域与组骨架）**：新建 `doc/bundles/workplace/index.md`（type: group，域导航表 + hidden toctree）、`workplace/hr/index.md`、`workplace/admin/index.md`（组 index，知识包列表表 + toctree）。
- **FR-2（束 1 hr-profession-map）**：`workplace/hr/hr-profession-map/`——岗位版图（行政/人事/HRBP/SSC/COE 分层）、能力模型与进修路径、证书体系双轨（技能等级认定 vs 职称考试）、osta 查询与防骗清单。
- **FR-3（束 2 hr-six-modules）**：`workplace/hr/hr-six-modules/`——六大模块逐一概念卡 + 三支柱模型 + 招聘/入职/培训/绩效/薪酬高频实务清单与案例。
- **FR-4（束 3 labor-law-compliance）**：`workplace/hr/labor-law-compliance/`——劳动合同全周期、试用期规则、N/N+1/2N 计算、工时加班与休假、五险一金合规、工伤、女职工保护、劳动争议仲裁时效与举证；含真实判例与计算示例。
- **FR-5（束 4 admin-operations）**：`workplace/admin/admin-operations/`——行政岗十大职能域概念卡 + 印章/档案/资产/会议/接待/预算/安全保密实务清单与案例。
- **FR-6（束 5 official-writing）**：`workplace/admin/official-writing/`——15 种法定公文适用场景与行文关系、公文格式要素、职场常用文书（通知/请示/报告/纪要/邮件/总结）范例与模板、写作四原则。
- **FR-7（总索引注册）**：更新 `doc/bundles/index.md` 五面：frontmatter 计数（352 束 / 71 组 / 16 域）、正文计数行、域节标题（`### 🏢 [职场与管理](workplace/index.md) · 5 束 · 2 组` 格式）、分组表两行、末尾 toctree 增 `workplace/index`；同步两处 Mermaid 图（如含域节点）。
- **FR-8（每束内容结构）**：每束 facts.md（F-NNN 编号、【P0】标记、S 信源登记）、insights.md（≥4 条四元组洞察 + 1 张 Mermaid 知识地图）、concepts/（3-6 张 NN-kebab 概念卡 + index.md）、examples/（2-3 个清单/模板/案例 + index.md）、references/（1-2 份法规/文件要点摘编 + index.md）、log.md、index.md（快速导航 + hidden toctree）。

## Non-Functional Requirements

- **NFR-1（事实准确性）**：所有法规数字（天数/倍率/比例/时限/条数）100% 可溯源至 S1-S14 官方信源；营销类信源（S15）仅用于职责框架佐证，不得支撑法规事实。
- **NFR-2（格式合规）**：全部 .md 为 UTF-8 无 BOM、LF/CRLF 与仓库现状一致；frontmatter 可被 yaml.safe_load 解析；双引号标量内禁嵌 ASCII 双引号（用全角“”）；文件名 kebab-case 英文；正文中文；交叉引用相对路径、禁 file:///。
- **NFR-3（教学可用性）**：每束至少含 1 个可直接复制使用的清单/模板/计算示例；概念卡遵循「是什么→为什么→怎么做→常见坑」结构；读者无需外部资料即可完成入门到实操。
- **NFR-4（可审计性）**：facts.md 信源登记表含 URL；index.md frontmatter 含 sources 与 generated.by=`reference_agent/trae-research-agent`；status: stable、stale_after 按法规时效性设置（法律束 stale_after 较短）。
- **NFR-5（隔离性）**：不修改 think/daojia 及任何他会话 WIP 文件；git 工作区只新增 workplace/ 树与修改 bundles/index.md 一个共享文件。

## Constraints

- **Technical**：Windows + py314/conda 环境；门控直跑 `python scripts\*.py`（cwd=projects/awesome-okf-xs）；OKF v0.2 frontmatter 规范（`.agents/rules/frontmatter.md`）；锚点组计数规则（check-bundles-index.py 源码已精读）。
- **Business**：内容为公开知识；法规以国家层面现行有效文本为准；地方差异显式提示「以当地政策为准」。
- **Dependencies**：awesome-okf-xs 子模块现有门控体系；five-love-languages 束模板；S1-S15 信源。
- **并行约束**：共享索引文件竞态防护（见 Background 门控基线）。

## Assumptions

- A1：新域名采用 **`workplace/`**（标题「🏢 职场与管理」）——现有 15 域无职业实务类归属（think/ 定位为思想理论），故新建第 16 域；备选 `career/`（偏个人发展，涵盖面窄）、`management/`（偏管理学理论）。**若用户偏好备选域名，审批时指出，实施前一键改名成本低。**
- A2：5 束规模（hr 组 3 束 + admin 组 2 束）与用户「全面调研 + 进修」意图匹配；不追求一次穷尽（如薪酬设计、OD、招聘面试技法等进阶主题可在后续迭代扩束）。
- A3：行政与人事在中小企业常为同岗（「行政人事专员」），故两组合为一域、交叉引用；不单独为「职场沟通/职业晋升」建束（其要点融入 hr-profession-map 与 official-writing）。

## Acceptance Criteria

### AC-1: 门控三门全绿

- **Type**: `rule`
- **Given**: 5 束与域/组骨架全部写入、总索引更新完成
- **When**: 在 `projects/awesome-okf-xs` 下依次执行 `python scripts/check-bundles-index.py`、`python scripts/check-toctrees.py`、`python scripts/check-utf8.py`
- **Then**: 三脚本均退出码 0；bundles-index 输出「16 域 / 71 组 / 352 束」且五面一致；toctrees 无断链、无孤立文档；utf8 无 BOM 告警
- **Pass Condition**: 三条命令输出均含通过/对账一致结论，无任何 FAIL/ERROR
- **Evidence**: 三条命令的完整终端输出

### AC-2: 束结构完整且可达

- **Type**: `rule`
- **Given**: workplace/ 树建成
- **When**: 检查 5 个束目录
- **Then**: 每束含 index.md（type: OKF + okf_version: "0.2" + sources + generated）、facts.md、insights.md、log.md、concepts/index.md、examples/index.md、references/index.md 及各层 NN-kebab 内容文件；所有 toctree 引用目标存在；域/组 index.md 为 type: group
- **Pass Condition**: 结构清单逐项存在；check-toctrees 已证明可达
- **Evidence**: 目录树清单 + 门控输出

### AC-3: 法规事实零错误且可溯源

- **Type**: `rule`
- **Given**: labor-law-compliance 束与其余束中的法规数字
- **When**: 抽查 12 个关键数字（试用期 1/2/6 月、N 计算、2N、加班费 150/200/300%、月 36 小时、21.75 天、年休假 5/10/15 天与 300%、仲裁时效 1 年、社保单位 16%/个人 8%、公积金 5%-12%、产假 98 天、工伤 48 小时/30 日/1 年、公文 15 种）
- **Then**: 每个数字与 S1-S14 官方文本一致，且在 facts.md 中有 F 编号与 S 信源对应
- **Pass Condition**: 12/12 一致；facts.md 信源登记表 URL 可解析
- **Evidence**: 抽查对照表（数字 → 条文 → 信源 URL）

### AC-4: frontmatter 与命名规范

- **Type**: `rule`
- **Given**: 全部新增 .md
- **When**: 运行 yaml.safe_load 扫描所有 frontmatter，并检查文件名
- **Then**: 0 个解析错误；okf_version 仅出现在 5 个束根 index.md；无 ASCII 双引号嵌套；文件名全 kebab-case 英文；无 file:/// 引用
- **Pass Condition**: 扫描脚本退出码 0 且报告 0 错误
- **Evidence**: 扫描脚本输出

### AC-5: 教学实用性

- **Type**: `rubric`
- **Dimension**: 进修可用性（读者能否据此自学并直接行动）
- **Scale**: 1-5
- **Anchors**: 1 = 只有概念罗列、无行动指引；3 = 有框架有要点但缺清单/模板/案例；5 = 每束含学习路径 + 可复制清单/模板 + 真实案例 + 常见坑，新手可照做
- **Pass Threshold**: >= 4
- **Evidence**: 每束 examples/ 内容与 concepts 卡片结构抽查

### AC-6: 洞察质量（I 阶段）

- **Type**: `rubric`
- **Dimension**: insights.md 四元组质量
- **Scale**: 1-5
- **Anchors**: 1 = 复述常识无洞察；3 = 有观点但反常识点牵强或无行动启示；5 = 每条洞察四元组完整（陈述/证据/反常识点/行动启示），反常识点有事实支撑且改变读者决策，Mermaid 地图呈现知识结构关系
- **Pass Threshold**: >= 4
- **Evidence**: 5 份 insights.md 抽查

### AC-7: 并行会话隔离

- **Type**: `rule`
- **Given**: 实施前后 git status
- **When**: 对比工作区变更
- **Then**: 新增/修改文件仅为 `doc/bundles/workplace/**`（新增）与 `doc/bundles/index.md`（修改）；think/daojia 及他会话文件零触碰；未执行 commit
- **Pass Condition**: `git status --porcelain` 中我方变更集合与上述完全一致
- **Evidence**: git status 输出

## Open Questions

- [ ] Q1：新域命名确认——推荐 `workplace/`（🏢 职场与管理），备选 `career/`、`management/`（见 Assumptions A1）。
- [ ] Q2：束范围确认——5 束（hr-profession-map / hr-six-modules / labor-law-compliance / admin-operations / official-writing）是否符合预期；如需增加「职场沟通与晋升」或「薪酬/绩效进阶」束，请在审批时指出。
