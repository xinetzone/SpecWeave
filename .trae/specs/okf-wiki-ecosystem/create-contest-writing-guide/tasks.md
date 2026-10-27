---
type: plan
title: "参赛和写作综合指南任务队列"
status: draft
source: spec.md
---

# 参赛和写作综合指南任务队列

规格已于本会话获明确批准，当前实施由子代理承担，主代理负责调度与证据整合。访问探测不算正式规则核验。

## 执行约定

- 写入范围以 [规格](spec.md) 为准；不报名、发布、签协议、安装依赖、提交或推送。
- 实施前重新读取工作区和子项目入口，检查 Git 中间态与路径级变更；不处理其他会话的资产。
- Task 1–3 可并行，只读研究结果返回主代理，不同时写事实表或共享索引。临时证据放在仓库外，最终保留的来源摘要归入已批准的知识包文件。
- Task 4 统一分配 F/G/C/E 编号；各来源研究阶段仅用带来源前缀的临时编号，防止并发冲突。
- 七概念采用知识沉淀 R→I→E→V，记录真实 CMD-LOG 和 G1/G2/G3 检查事件；C 等待单独授权，不为满足数量制造事实、案例或审查发现。
- 完成任务时勾选任务标题并更新 Status，补充 Completion Evidence；失败或受阻不能记为 completed。

## [x] Task 1 知乎活动规则复核

- Status: completed
- Priority: high
- Depends On: 无
- Description: 合法读取用户指定专栏和关联官方规则，对照既有知乎知识包，登记当前资格、时点、工具、作品、投稿材料、评分、奖励及授权条款。403 时换合法来源，不反复使用同一失败通道。
- Acceptance Criteria Addressed: AC-1、AC-2、AC-4、AC-7
- Test Requirements:
  - `rule` TR-1.1: 返回来源 URL、采集时点、原文定位、条款覆盖矩阵和缺口；未取得正文不得记成核验通过。
  - `rule` TR-1.2: 日期与权利主张逐项对照官方依据；旧包与本轮规则差异保留，不覆盖旧包。
- Completion Evidence: zhihu_rules 子代理于 2026-10-27 通过官方 CLI 公共搜索取得知乎科学活动规则片段，返回 ZH-01 至 ZH-25 与七项缺口及旧包映射。TR-1.1/TR-1.2 已对照，10-31 细钟点/时区、跨外部赛事和适用协议均保留缺口，部署公告编辑日期差异留痕；未将片段声称全文或独立多源核验。正式台账由 Task 4 统一落盘。

## [x] Task 2 WorkBuddy 活动规则复核

- Status: completed
- Priority: high
- Depends On: 无
- Description: 读取公开活动页或公开引导数据，复核作品形态、指定工具、阶段赛程、材料、评审、奖励、重复参赛与授权条件。区分赛事规则和既有包中的候选方案。
- Acceptance Criteria Addressed: AC-1、AC-2、AC-4、AC-7
- Test Requirements:
  - `rule` TR-2.1: 返回公开来源定位和覆盖矩阵；SPA 空壳不记为正文，未说明与无法读取分别登记。
  - `rule` TR-2.2: 每阶段截止、提交渠道和跨赛事限制均有证据或明确缺口；不默认用户选择知识罗盘。
- Completion Evidence: workbuddy_rules 于 2026-10-27 读取公开引导数据版本 54、Carn2iELxRnY/janus.data.json 和活动 HTML，返回 WB-01 至 WB-35。ruleHTML 与旧版 49 字符串机械一致；新 sharecode 提示、更新后的链接路径、UTC+8 前端时序与权利段条件主语逐项记录。TR-2.1/TR-2.2 通过，服务协议正文及外部跨赛等仍为显式缺口，名额算术矛盾未擅自修正。

## [x] Task 3 头条写作入口与权利复核

- Status: completed
- Priority: high
- Depends On: 无
- Description: 确认 exclusive 入口对应的计划，查当前公开官方帮助和协议，分别核验首发激励、独家及签约条件。个人账号资格不进入公共资料。
- Acceptance Criteria Addressed: AC-1、AC-2、AC-4、AC-7
- Test Requirements:
  - `rule` TR-3.1: 明确入口身份是否确认，通用介绍页不能充当独家规则；未确认身份时不把首发条款直接套用。
  - `rule` TR-3.2: 首发窗口、站外先发表、自动同步、修改重发、相似内容及公开 Git/Wiki 风险分别有依据或缺口；不代用户接受协议。
- Completion Evidence: toutiao_rules 于 2026-10-27 读取公开首发帮助 detail/242/566/0 的正文与 FAQ、官方升级公告及用户协议 3.9 等，返回 TT-01 至 TT-22 和五组缺口。TR-3.1/TR-3.2 通过：exclusive 入口未确认，不套用首发计划；72 小时、实质相似、同步、不能补声明和申诉规则均挂实际公开来源；2021 收益页面仅保留历史基线，同页 100 字措辞差异留痕。

## [x] Task 4 统一事实与发布顺序

- Status: completed
- Priority: high
- Depends On: Task 1、Task 2、Task 3
- Description: 建立 source-inventory 和 facts，合并三个来源结果及旧包编号映射。比较资格、作品和发布三条时间线，形成版权情景表与保守发布分支。
- Acceptance Criteria Addressed: AC-1、AC-2、AC-4
- Test Requirements:
  - `rule` TR-4.1: 编号定义与引用双向机械比对，无重复定义、悬空引用；关键主张覆盖矩阵没有未登记的空项。
  - `rule` TR-4.2: G1 将客观事实与推断分离；旧包采集日期和本轮实际验证日期不混用。
  - `rule` TR-4.3: 对已确认时间窗计算相交和截止约束；缺时区或协议的分支保留未知，不断言允许一稿多投。
- Completion Evidence: guide_author 已落盘 facts/source-inventory/版权页，references/verification.md 记录作者 Node 断言首败及修正后退出0：82F/24G/7C/6E连续唯一、研究输入82/82双向映射、旧显式编号存在、初批13本地链接和3页YAML/UTF-8/BOM通过。现金、评分、奖位、71小时、三项72小时及43201秒差值回验；时区、实际入口和适用协议未知均保留。作者自验不替代Task7独立验收。

## [x] Task 5 选题写作与洞察萃取

- Status: completed
- Priority: high
- Depends On: Task 4
- Description: 比较至少三类候选方向，写清各平台的读者问题、文章结构和真实证据要求。提炼至少三条洞察、一至两项候选方法，在已批准的 concepts 页面落稿。
- Acceptance Criteria Addressed: AC-3、AC-5、AC-7
- Test Requirements:
  - `rubric` TR-5.1: 参与和写作质量采用 AC-3 的 1–5 量表；1 为通用摘要，3 为平台内容齐全但证据与选题不足，5 为三类候选、差异写法、举证及失败边界齐备；阈值至少 4，记录逐页理由。
  - `rule` TR-5.2: G2 每条洞察有事实编号、解释或假设、影响和建议，三条不重复；G3 每项方法有适用边界、步骤、至少三种反模式和迁移检验。
  - `rule` TR-5.3: 候选方法标明成熟度和未经获奖验证；案例不足时保留候选身份，示例不捏造用户过程、数据或成果。
- Completion Evidence: guide_author 已写三类选题、材料、差异写作、洞察方法页。references/verification.md 记录累计7页Node断言退出0、YAML7/7、20本地链接、编号悬空0和BOM0；3洞察各六元素、2方法各6步/4反模式/跨域桌面检验，均L1-draft且不宣称真实获奖验证。作者逐页评分02=4、03=5、04=4、07=4，综合4/5；独立评分待Task7。

## [x] Task 6 知识包导航与元数据收尾

- Status: completed
- Priority: medium
- Depends On: Task 5
- Description: 补齐包内 index/log/verification，按 spec 文件清单建立 toctree。重新读取共享索引后串行添加本包条目和必要计数，不覆盖并发增量。
- Acceptance Criteria Addressed: AC-2、AC-6、AC-7
- Test Requirements:
  - `rule` TR-6.1: 全部非保留内容文件 frontmatter 可解析且 type 非空，sources 每项含 resource；okf_version 只在包根索引。
  - `rule` TR-6.2: 文件清单与导航集合对账一致；UTF-8 无 BOM、范围内相对路径链接和来源路径通过检查。
  - `rule` TR-6.3: 运行子项目 toctree、计数等适用门禁及范围内 Sphinx 构建，记录退出码；既有失败与新增回归分开，环境阻塞不冒充通过。
  - `rule` TR-6.4: 路径级 diff 仅包含本包和必要索引增量，无旧包覆盖、个人数据、来源全文镜像或临时证据。
- Completion Evidence: guide_author 回传并落盘 references/verification.md：批准与实际15页集合一致；YAML12页/resource31项、F82/G24/C7/E6、UTF-8/BOM/文件名通过；显式15页链接检查覆盖62本地引用断链0；run_scan本包15页及industry366页错误0。三索引逆去本包增量指纹与写前匹配，industry34→35、社科81→82、总686→687，计数门退出0（9域/63组/687束）。Sphinx9.1范围构建status0、15源文档/19HTML，仓库外输出，依赖弃用警告保留；范围diff检查通过。全库既有导航及资产口径债务未冒称消除。

## [ ] Task 7 独立验收与修复回验

- Status: blocked
- Blocked By: R2无遗留内容缺陷，但早期关键条款原始核验资料及Task6写前三索引快照未取得，CP-2/CP-7历史证据不可独立确认。
- Unblock Condition: 取得真实历史核验与隔离证据后委托新上下文复验；不补造历史事件或快照。当前指南保留draft可读交付，不宣告完整验收。
- Priority: high
- Depends On: Task 6
- Description: 委托全新上下文只读审查全部 AC/TR 和 checklist，覆盖质疑者、新人、投入产出、未来变化四视角。可行动发现转为附加任务，交由子代理修复并重新验证。
- Acceptance Criteria Addressed: AC-1、AC-2、AC-3、AC-4、AC-5、AC-6、AC-7
- Test Requirements:
  - `rule` TR-7.1: 每项二元标准有独立证据；通过的检查点才勾选，无法执行的检查记录阻塞。
  - `rubric` TR-7.2: 独立复核 AC-3/TR-5.1，沿用相同 1–5 锚点与至少 4 的阈值，给出得分和依据。
  - `rule` TR-7.3: 审查发现有 P0–P3 分级、裁定及修复回验；不按数量伪造缺陷，未解决的可行动发现不能记最终通过。

## 任务与验收映射

## [x] Task 8 独立审查发现修补与证据补齐

- Status: completed
- Priority: high
- Depends On: Task 6
- Discovered By: Review R1
- Description: 修正P1表单字段遗漏、P1代维权授权遗漏和P2完整日志缺口，删去P3不直接支撑映射；真实当前规则未复核项不得冒充当日确认。补充作者留存的原始来源与写前快照证据供新上下文核验，无法取得则明确保留边界。
- Acceptance Criteria Addressed: AC-1、AC-2、AC-4、AC-5、AC-7
- Test Requirements:
  - `rule` TR-8.1: 表单13项和11必填逐字段覆盖，实名、联系方式、UserID仅描述类型不填真实值；授权由用户本人决定。
  - `rule` TR-8.2: 代维权条款和配合义务有当前证据或显式历史待复核缺口，事实、权利页、地图和来源矩阵同步；非独占不替代义务解释。
  - `rule` TR-8.3: 当前G1/G2/G3复验有真实CMD-LOG，历史事件缺失只留痕不倒填；F-054无关旧号删除。编号、链接、导航、范围构建复跑通过。
- Completion Evidence: guide_review_remediation已定点读取当前W-R/W-H（HTTP200），完整13字段/11必填并新增F-083代维权条款，删除无关映射；83F/24G/7C/6E、YAML/UTF-8/BOM、G1-G3、4条逐字短引、67本地引用、完整导航、计数687及回填后Sphinx15源/19HTML通过。log含22条真实当前事件和两次首败，不倒填历史。旧研究原始响应和Task6写前快照未取得，明确保留CP2/7历史证据局限，未声称最终通过。

### Review R1

- Result: fail
- Findings: P1必填投稿字段未完整展开；P1代维权授权及配合义务遗漏；P2完整事件日志承诺未兑现；P3 advisory F-054附无关旧F-093b/F-093c。
- Evidence: 独立guide_independent_review已完整读取15页。CP1/4/5 fail；CP2/7因部分原文与写前快照未取得blocked；CP3评分4/5；CP6通过。15页/YAML12/resource31、F82/G24/C7/E6、62本地链接、run_scan、计数687和最终Sphinx15源/19HTML通过。修复后新上下文重新验收，不预勾最终完成。

### Review R2

- Result: blocked
- Evidence: guide_independent_recheck独立复验83F/24G/7C/6E、13字段/11必填、F-083代维权9要素、22当前日志、67本地链接、导航与计数687，范围构建status0、15源19HTML；评分4/5，四视角完成，35输入文件前后指纹相同。
- Findings: R1两P1及P3已解决，P2当前日志完成且历史缺失保留；无未解决可行动内容缺陷。CP1/3/4/5/6通过；CP2/7仍为历史证据blocked，未据自述补勾。具体检查点见checklist.md。

| 标准 | 任务 |
|---|---|
| AC-1 | 1、2、3、4、7 |
| AC-2 | 1、2、3、4、6、7 |
| AC-3 | 5、7 |
| AC-4 | 1、2、3、4、7 |
| AC-5 | 5、7 |
| AC-6 | 6、7 |
| AC-7 | 1、2、3、5、6、7 |

## 完成证据

待实施后逐任务填写真实命令、结果、文件定位和审查依据。最终检查使用 [验收检查表](checklist.md)，不以规划完成替代 Wiki 交付完成。
