# 行政人事岗位进修 OKF Wiki 教程束 - Implementation Plan

> 方法论：七概念 R→I→E（R 已完成，11 主题/S1-S15 信源见 spec.md）。每束内部顺序固定：facts.md（事实）→ concepts/（概念卡）→ examples/（清单/模板/案例）→ references/（法规摘编）→ insights.md（洞察+Mermaid）→ index.md（束根导航）→ log.md。frontmatter 范式照 `think/relationships/five-love-languages/`。

## Task 1: 束 1 hr-profession-map（HR 职业地图与进修路径）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建 `doc/bundles/workplace/hr/hr-profession-map/`
  - facts.md：F 编号事实覆盖证书改革（人社厅发〔2020〕80号、退出时点、社会化等级认定、旧证有效、2019 标准、四级→一级）、经济师人力职称独立序列、osta 查询、岗位版图与薪资框架事实；信源 S1/S2/S15
  - concepts/：01 行政人事岗位版图（行政 vs HR 关系、专员/主管/经理/总监、三支柱岗位映射）、02 证书双轨体系（技能等级认定 vs 职称考试 vs 劳动关系协调员）、03 能力模型与进修路径（选/育/用/留能力树、0-1/1-3/3-5 年学习路线）
  - examples/：01 分阶段进修行动清单、02 证书报考与防骗指南（官方渠道/挂靠骗局/保过班识别）
  - references/：01 人社厅发〔2020〕80号要点摘编
  - insights.md：≥4 条四元组洞察（如「退出国家职业资格目录 ≠ 证书作废」「证书是信号不是能力」等反常识点）+ Mermaid 职业地图
  - index.md（type: OKF, okf_version: "0.2", sources, generated, status: stable, stale_after: 2027-09）+ log.md + 三层 index.md hidden toctree
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-1.1: 束目录 7 类文件齐全（index/facts/insights/log + 三层 index），yaml.safe_load 全过
  - `rule` TR-1.2: 证书改革事实（2020-09-30 第一批退出、80号文、osta、旧证有效）与 S1/S2 一致
  - `rubric` TR-1.3: 教学实用性；1-5；锚点 1/3/5 同 spec AC-5；阈值 ≥4；证据 examples/ 两份清单可照做
- **Notes**: 防骗清单为 N4 非目标的正面落实。

## Task 2: 束 2 hr-six-modules（HR 六大模块与三支柱）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1（域目录已建则无硬依赖，可并行写）
- **Description**:
  - 新建 `doc/bundles/workplace/hr/hr-six-modules/`
  - facts.md：六大模块名称与边界、三支柱（COE/HRBP/SSC）定义与分工、选育用留闭环；信源 S15 + 框架佐证信源
  - concepts/：01 六大模块总览、02 三支柱与 Ulrich 模型、03 招聘配置与入职离职、04 培训开发与绩效管理（KPI/OKR 区分）、05 薪酬福利结构（薪资结构/调薪/福利）
  - examples/：01 入职/离职流程清单、02 绩效管理周期实操（目标设定→辅导→评估→反馈）、03 招聘 JD 与面试问题模板
  - references/：01 六大模块与三支柱框架说明（含框架来源与本土化演进）
  - insights.md：≥4 条四元组（如「六大模块是知识地图不是组织架构」「小公司 HR 是通才、大公司是三支柱」）+ Mermaid 模块关系图
  - index.md + log.md + 三层 index.md
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: 结构同 TR-1.1；六大模块名称与 spec Background 第 4 条逐字一致
  - `rubric` TR-2.2: 教学实用性；阈值 ≥4；证据 3 份 examples 可直接复用
  - `rubric` TR-2.3: 洞察质量；1-5；锚点同 AC-6；阈值 ≥4

## Task 3: 束 3 labor-law-compliance（劳动法律合规实务）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建 `doc/bundles/workplace/hr/labor-law-compliance/`
  - facts.md：F 编号逐条登记——劳动合同法第 10/14/19/39/40/47/83/87 条、劳动法第 36/41/44 条、年休假条例（5/10/15 天、300%）、社保费率（16%/8%、6%/2%、1%、0.2-1.9%、5%-12%）、工伤条例第 14/15/16/17 条、女职工 619 号令（98 天等）、仲裁法第 27 条（1 年时效、劳动报酬特殊时效、仲裁前置）、21.75 月计薪天数；每条标【P0】并挂 S3-S14 信源
  - concepts/：01 劳动合同全周期（订立/试用期/无固定期限/变更/解除终止）、02 经济补偿与赔偿金（N/N+1/2N/83 条试用期赔偿计算树）、03 工时加班与休假（标准工时/加班费/年休假/产假/特殊工时）、04 五险一金合规（费率表/基数/断缴风险/生育合并）、05 工伤认定（7+3+3 情形/申请时限/举证）、06 劳动争议处理（协商→调解→仲裁→诉讼/时效/证据清单）
  - examples/：01 延长试用期违法判例（S4 深圳宝安案例）、02 N/2N 计算示例（含 21.75 折算）、03 HR 合规自查清单 + 争议证据留存清单
  - references/：01 劳动合同法关键条文摘编、02 配套法规索引（劳动法/年休假条例/仲裁法/工伤条例/619 号令/工伤认定办法）
  - insights.md：≥5 条四元组（如「员工签字的违法约定仍然无效」「试用期不是廉价用工期」「加班费举证责任在用人单位掌握的考勤」）+ Mermaid 解除/补偿决策树
  - index.md（stale_after: 2027-03，法律时效性强）+ log.md + 三层 index.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: AC-3 抽查 12 个关键数字 12/12 与官方信源一致，对照表入 review 证据
  - `rule` TR-3.2: 结构与 yaml 同 TR-1.1；信源 S3-S14 全部在 facts.md 登记且 URL 可解析
  - `rubric` TR-3.3: 教学实用性；阈值 ≥4；证据计算示例与自查清单可直接使用
  - `rubric` TR-3.4: 洞察质量；阈值 ≥4；证据反常识点有判例/法条支撑

## Task 4: 束 4 admin-operations（行政管理实务全景）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建 `doc/bundles/workplace/admin/admin-operations/`
  - facts.md：行政岗职能域实证（来自 S15 JD 汇总：物资/资产/会议/公文/印章/档案/证照/接待/差旅/后勤/预算/安全保密）、固定资产全生命周期环节、印章管理红线（用印登记/不得带出/专人保管）
  - concepts/：01 行政岗职责版图（12 职能域 + 行政与 HR 边界）、02 资产与采购管理（固定资产全生命周期/办公用品/供应商/三家比价）、03 会议接待与差旅（会议全流程/商务接待分级/差旅预订）、04 印章档案与证照（用印审批流/档案分类保管/证照年检）、05 办公环境与安全保密（5S/消防/用电/访客/保密）、06 行政预算与成本管控
  - examples/：01 会议保障全流程清单、02 固定资产盘点表模板 + 用印登记表模板、03 行政年度预算框架
  - references/：01 行政岗 JD 实证汇总（S15，标注为市场实践非法规）
  - insights.md：≥4 条四元组（如「行政的价值是让组织感觉不到摩擦」「印章是公司法律人格的物理延伸」）+ Mermaid 行政职能地图
  - index.md + log.md + 三层 index.md
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 结构与 yaml 同 TR-1.1；S15 在 facts.md 明确标注「市场实践信源」
  - `rubric` TR-4.2: 教学实用性；阈值 ≥4；证据 3 份模板/清单可复制
  - `rubric` TR-4.3: 洞察质量；阈值 ≥4

## Task 5: 束 5 official-writing（公文写作与职场文书）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建 `doc/bundles/workplace/admin/official-writing/`
  - facts.md：15 种法定公文名称与适用场景（条例第 8 条逐条）、公文格式 18 要素（第 9 条）、行文关系（上行/下行/平行）、条例施行日期（2012-07-01）；信源 S10
  - concepts/：01 15 种法定公文总览（按行文方向分组 + 易混文种辨析：决议vs决定、公告vs通告、报告vs请示）、02 公文格式要素（标题三要素/发文字号/成文日期/印章）、03 职场常用文书（通知/请示/报告/会议纪要/商务邮件/工作总结）、04 写作四原则（实事求是/准确规范/精简高效/安全保密）
  - examples/：01 通知与会议纪要范例、02 报告 vs 请示对比范例、03 商务邮件规范模板（主题/称谓/正文/附件/签名）
  - references/：01《党政机关公文处理工作条例》要点摘编（第 8/9 条）
  - insights.md：≥4 条四元组（如「企业不用法定公文但文种逻辑通用」「请示与报告混写是职场高频错误」）+ Mermaid 文种选择决策图
  - index.md + log.md + 三层 index.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: 15 种文种名称与 S10 条文逐字一致；结构/yaml 同 TR-1.1
  - `rubric` TR-5.2: 教学实用性；阈值 ≥4；证据 3 份范例可套用
  - `rubric` TR-5.3: 洞察质量；阈值 ≥4

## Task 6: 域/组索引与总索引注册

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 新建 `workplace/index.md`（type: group；域标题「🏢 职场与管理」；hr/admin 两组导航表；hidden toctree 引 hr/index、admin/index）
  - 新建 `workplace/hr/index.md`、`workplace/admin/index.md`（type: group；知识包列表表 3 行/2 行；toctree 引各束 index）
  - 修改 `doc/bundles/index.md` 五面：①frontmatter total_bundles 347→352、groups 69→71、domains 15→16；②正文计数行同步；③新增域节 `### 🏢 [职场与管理](workplace/index.md) · 5 束 · 2 组`（正则格式照现有域节）；④分组表增 hr/admin 两行（束数列 3/2，链接可解析）；⑤末尾 hidden toctree 增 `workplace/index`；两处 Mermaid 图若含域节点则同步
  - 修改前先 Read 最新 bundles/index.md（并行会话可能已改动），基于磁盘最新内容编辑
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: check-bundles-index.py 输出「16 域 / 71 组 / 352 束」且五面一致
  - `rule` TR-6.2: check-toctrees.py 通过、无孤立文档
  - `rule` TR-6.3: `git status --porcelain` 变更集 = workplace/** 新增 + bundles/index.md 修改，无他会话文件

## Task 7: 门控总验证与规范扫描

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - cwd=projects/awesome-okf-xs 依次直跑：`python scripts/check-utf8.py`、`python scripts/check-bundles-index.py`、`python scripts/check-toctrees.py`
  - 跑 yaml.safe_load frontmatter 扫描脚本（遍历 workplace/**/*.md），确认 0 解析错误、okf_version 仅 5 处、无 ASCII 双引号嵌套
  - 核对 AC-3 数字抽查对照表（12 项）
  - 核对 git status 隔离性（AC-7）
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-7
- **Test Requirements**:
  - `rule` TR-7.1: 三脚本退出码均 0，输出存档
  - `rule` TR-7.2: yaml 扫描 0 错误；文件名 kebab-case 全过；无 file:/// 引用
  - `rule` TR-7.3: 12 数字对照表 12/12 一致

## Task 8: 独立审查（V 对抗审查）与修复闭环

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 委托 fresh context 独立审查者（general_purpose_task 子代理，不携带实施上下文），按 review.md  checkpoint 逐项核验：CP-R1 门控三门、CP-R2 束结构、CP-R3 法规数字溯源、CP-R4 frontmatter/命名、CP-R5 隔离性（rule）；CP-U1 教学实用性、CP-U2 洞察质量（rubric）
  - 审查产出 `.trae/specs/hr-admin-okf-wiki/review.md`
  - 若 fail：每个 actionable finding 建 Issue（artifact-templates Review Issue 格式）→ 回 Implement 修复 → 重跑门控 → 复审，直至 pass
- **Acceptance Criteria Addressed**: AC-1 ~ AC-7 全部
- **Test Requirements**:
  - `rule` TR-8.1: review.md 中每个 AC 有独立证据；rule checkpoint 全 pass
  - `rubric` TR-8.2: CP-U1/CP-U2 评分均 ≥4 且记录评分理由
  - `rule` TR-8.3: 最终 Review 结果为 pass（无 actionable finding 遗留）
