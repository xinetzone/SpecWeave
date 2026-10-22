# OpenCode 同快照源码深化 - Implementation Plan

已获得 NotifyUser 显式批准，进入 Implement；不复用前轮已完成证据作为本轮验证。
知识产出限定在既有 OpenCode bundle，编号默认续接 F-115、概念 10、示例 03，Task 1 重新核实。

## Task 1: 固定本轮信源与增量基线
- **Status**: `completed`
- **Completion Evidence**: TR-1.1/1.2 通过。源码 HEAD 为 6ec56821d63100fe5bda45b759364f561c56b359，manifest 2.0.32 / bun@1.4.2，源码 status 为空；子项目 HEAD a12a6ec229900171acba376d501c59377be81af0，status 为空，MERGE_HEAD/rebase-merge/rebase-apply 均不存在。磁盘事实最大 F-114、概念 09、示例 02，旧日志 0.2.0 保留。主仓 HEAD 239ca09b43977fcd28ae21435a53394591c08eaf；private-wiki-increment、两个看板、vibeknow-cli-okf-wiki 临时计数文件全部排除。批准记录已写 spec Approval。活动信源采用不可变 GitHub commit URL；本地 checkout 仅为读取通道。
- **Priority**: high
- **Depends On**: None
- **Description**: 复核批准记录、源码 HEAD/manifest/状态、目标 bundle 编号与文件清单；保存他方改动的排除清单。以不可变远端 commit 坐标作为活动信源，记录本地读取方式，不改变 checkout。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 实施前源码 HEAD 等于规格坐标，manifest 版本可核验；既有编号和旧日志基线有命令证据。
  - `rule` TR-1.2: 确认无进行中的 merge/rebase，批准记录存在，修改排除清单完整，无本机路径作为活动引用。

## Task 2: R - 配置、上下文及 codemode 事实
- **Status**: `completed`
- **Completion Evidence**: TR-2.1 通过，R 草稿 facts.md 登记 F-115～F-130，固定 commit/path/行范围，未重复旧编号；预算数字直接取实现常量，无新总体计数。TR-2.2 自验 3/3：Config→领域插件→服务状态、CodeMode→解释器→宿主工具链已读；技能/压缩调用测试及 JSON Schema render-only 测试已对照。Core 未传 limits、输出非统一字节上限、持久指令去重边界均有实现证据；未运行源码测试。E 阶段将固定坐标链接迁入正式事实文件。
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 阅读对应嵌套 AGENTS、Core 配置/skill/instruction/compaction、codemode 实现与 Core 接线，选取测试或调用方对照。登记新增编号事实及已读/未读文件，不重复 F-001～F-114。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-2.1: 新事实续编号、带固定来源与路径；数量有工具计数口径，无设计意图推断混入事实。
  - `rubric` TR-2.2: 前两主题实现深度；0 = 臆造，1 = 入口摘要，2 = 每主题有代表性链路和范围，3 = 加入测试/调用方、复用与限制证据；阈值 >= 2；证据为事实与覆盖矩阵。

## Task 3: R - 扩展契约与产品状态流事实
- **Status**: `completed`
- **Completion Evidence**: TR-3.1 通过，facts.md 续接 F-131～F-140，Schema/Plugin 签名、Scope cleanup、Core policy/activation、三端各自持久化链均有固定实现路径；子代理报告经主代理关键正文回读整合。TR-3.2 自验 3/3：事件测试、插件加载测试、App/TUI/Desktop 存储测试或调用方已对照；明确 ACK/flush 不等于 SQLite 落盘，以及未读 session/global-sync 范围。仅静态读取，无运行成功声明。
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 阅读 Schema/Plugin 代表性契约及宿主接线，追踪 TUI、App、Desktop 状态同步/持久化或进程通信链路；避免凭入口推导实现，保留各端差异和失败边界。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-3.1: 符号、签名与调用关系有源码证据，继续唯一编号；每个产品端有自身实现证据。
  - `rubric` TR-3.2: 中间两主题实现深度；0 = 臆造，1 = 入口摘要，2 = 每主题有代表性链路和范围，3 = 加入测试/调用方及生命周期证据；阈值 >= 2；证据为事实与覆盖矩阵。

## Task 4: R - 验证回放、云端与更新事实
- **Status**: `completed`
- **Completion Evidence**: TR-4.1 通过：facts.md 共37条/37唯一编号，F-115～F-151连续；六主题矩阵齐全，EOF检查修正八处过长坐标并留审计记录。TR-4.2 自验3/3：HTTP recorder/store/replay/测试/固定夹具、simulation provider/Timeline、Console调用方、Stats daemon、files Worker、GUI updater正文与machine测试片段、TUI notification均有代表链；未读鉴权计费/Stats core/其他transport/真实更新部署明确标注。无源码运行成功声明。
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 阅读 simulation、http-recorder、代表性夹具和 workflow；阅读 console/stats/services 的代表性接线。汇总六主题矩阵，记录源码事实、已有测试和本轮实际运行的不同证据等级。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-4.1: 所有新增事实唯一且来源可定位，计数经工具产生，六主题均在矩阵中；无线上状态或真实部署推断。
  - `rubric` TR-4.2: 后两主题实现深度；0 = 臆造，1 = 入口摘要，2 = 每主题有代表性链路和范围，3 = 加入测试/调用方与回放/更新限制证据；阈值 >= 2；证据为事实与覆盖矩阵。

## Task 5: I - 洞察与增量学习地图
- **Status**: `completed`
- **Completion Evidence**: TR-5.1 通过：insights.md 五条陈述/证据/反常识/行动四元组，引用F-115～F-151；六主题映射概念10～15，示例03续接。TR-5.2自验3/3：前置05～09保留，按配置/工具/扩展/状态/验证/交付划分读者路径，静态核验练习不声称可直接运行。
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 基于 G1 通过的事实形成 3～5 条陈述/证据/反常识/行动四元组洞察；确定新篇名、前置关系及事实覆盖。新地图不覆盖前轮地图，不为凑数量拆主题。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-5.1: 洞察四元组齐全且引用真实新增 F 编号；六主题均映射到教程，全部篇名续编号。
  - `rubric` TR-5.2: 学习地图；0 = 无路径，1 = 重复旧内容，2 = 主题独立、顺序与前置清楚，3 = 加入读者分层和验证导读；阈值 >= 2；证据为知识地图。

## Task 6: E - 信源先行及分批教程
- **Status**: `completed`
- **Completion Evidence**: TR-6.1通过：第一批references/source-deepening先建，随后facts/insights；第二批概念10～12，第三批13～15及示例03，每批≤7。新非保留文档含type/source/sources，无伪verified；旧insights仅将模型turn修为step，依据根源码术语契约，Task7日志留理由。TR-6.2自验3/3：六概念各有独立主题、F编号、定位路径、误解与限制；示例03明确静态阅读而非运行脚本。十个新增文件仅在目标束。
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 先新增本轮信源登记，再落盘新事实/洞察和概念/示例。每批最多 7 文件；每篇引用事实并标注快照、范围及相关概念。源码导读/示意不宣称本轮运行成功；核实前轮 step/turn 措辞后只修确证问题。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-6.1: 信源创建顺序、批次与续接编号有记录；新非保留文档有合规 frontmatter/sources；历史未重排，任何旧事实修订有明确理由。
  - `rubric` TR-6.2: 增量教程质量；0 = 臆造/矛盾，1 = 摘要堆叠，2 = 独立主题、事实回链和学习顺序完整，3 = 加入导读与误解/限制说明；阈值 >= 2；证据为新教程。

## Task 7: E - 导航及本轮日志收尾
- **Status**: `completed`
- **Completion Evidence**: TR-7.1通过：机械集合比对concepts=16/examples=3/references=3/spec=6，各目录文件/tree/人类链接集合差异0；根导航连四目录和log，版本0.3.0与新增日志一致，旧历史保留。TR-7.2通过：git status仅目标束十个新增、六导航日志修改及旧insights一行修订，未改共享父级。
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 内容定稿后更新 bundle 根、concepts/examples/references/spec 的 index、版本与日志；不改共享父级或全局看板，不改写前轮覆盖等级。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-7.1: 人类导航与 toctree 逐目录集合等于实际文件；新篇全部可达；旧日志保留，新版本与本轮覆盖一致。
  - `rule` TR-7.2: diff 仅在目标 bundle 内，未修改他方索引或知识包。

## Task 8: V - 内容核验与文档质量门
- **Status**: `completed`
- **Completion Evidence**: TR-8.1通过：逐37事实及新教程初次回验发现全部修订并由独立只读回归逐项PASS；37唯一连续编号、68唯一固定行段、10新文档元数据、四目录16/3/3/6双导航集合一致，172本地引用全部存在，SPS blocking0。TR-8.2通过：最终gates.all exit0（12031文件UTF-8，toctree全可达，9域/63组/659束对账），期间他方open-code-review六项在途导航exit1已归因且未代修；正式invoke build job-671e4c69437342619ec29b98e8adac94已收到exit0通知，全站325警告、本束路径诊断0；定向本束修订版invoke build exit0/无文档诊断。TR-8.3通过：git diff --check、源码HEAD/clean、空cached、旧历史与log尾部核对通过，子项目改动仅本束十新七改；他方open-code-review、主仓Skill/看板/报告排除。所有测试定义只读，不执行源码或Git写操作。
- **Validation Progress**: 首次只读逐37事实/概念10～15/示例03回验发现字段返回值、远程指令状态、平台差分下载及合并证据不足；已同步正式事实、R草稿与概念10/15，另起只读回归，非最终Review。py314 gates.all退出0（12025文件UTF-8、全部toctree有效、9域/63组/659束对账与自检通过）。主仓链接工具从绝对子模块路径扫描0文件不作证据，改从本束cwd以--path .有效扫描34文件/172本地引用通过。独立临时辅助解析脚本在仓库外执行，37唯一连续事实、10新增文件、元数据及68唯一固定行段EOF、旧历史/旧log尾部、空暂存和源码HEAD/clean通过；临时脚本不属于知识信源或仓库产物。全站invoke build仍运行；另用项目配置定向构建本束修订后版本，输出仓库外。主仓他方报告及子项目open-code-review新文件排除，不修改。
- **Regression Evidence**: 只读内容回归6a52743b逐项PASS：字段值、URL失败、七项补充表、cache先返回和平台差分设置全部闭合，无限定范围P0-P3残余；两表37唯一编号差集空。定向invoke build（source=本束，-b html -c doc，target=仓库外临时目录）退出0，34页成功，无文档WARNING/ERROR，仅jieba依赖弃用提示。修订后gates.all首次退出1，仅open-code-review六个未注册在途文件；未代修，后续导航恢复，再跑gates.all退出0（12031文件UTF-8、toctree全可达、9域/63组/659束对账通过）。最终SPS扫描34文件blocking=0，唯一env-bound为旧日志2026-08-23历史本机读取路径，不是活动信源。
- **Priority**: high
- **Depends On**: Task 7
- **Description**: 对新 API/签名/调用关系、固定来源、编号、计数、frontmatter、链接和导航逐项核验；数量改用独立方法复计。运行 py314 的子项目 gates.all 与 invoke build，等待进程退出，按目标路径归因诊断。不为文档任务运行付费模型或云部署。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: 关键符号、行号与引用事实核验通过，数量独立复核一致，所有元数据/链接/导航无新增问题。
  - `rule` TR-8.2: 质量门、构建均有实际命令、退出状态与日志；目标 bundle 无新增诊断，无关失败逐项归因，不使用前轮构建代替本轮。
  - `rule` TR-8.3: 两仓状态与本轮 diff 核对边界，无暂存、提交、推送或源码修改。

## Task 9: C - 候选评估与交接
- **Status**: `completed`
- **Completion Evidence**: TR-9.1通过：候选评估如下一字段，不新增模式/模板/主仓资产、不提交；范围和验证限制写入本束log。最终日志定向HTML回归job-3e1c807b17fb42e18774906d621e380e exit0，链接172、本轮37编号、四目录导航与历史再检通过。Task1～9清空，转独立Review；未把自验或Task8内容代理当作最终Review。
- **Candidate Assessment**: 本轮发现字段值与document混同、URL失败与整体状态混同、machine参数与平台效果混同、链接标签与实际范围不齐、扫描0文件假绿。现有源码知识化流程已要求回源、符号/签名验证、独立计数和边界声明；这些是具体落实不足，尚无超出既有流程且经独立跨场景验证的新模式。结论为不新增主仓方法论或Prompt模板，C仅评估；日志已记录，Git写操作零次。日志收尾后链接172/编号37/导航16-3-3-6/历史再次通过，定向HTML回归等待退出。
- **Priority**: low
- **Depends On**: Task 8
- **Description**: 记录是否产生超出现有源码知识化流程的新候选方法及其证据；没有则明确不新增资产。不入库主仓、不提交，汇总本轮范围与验证限制。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-9.1: 候选评估有结论及理由，未新增主仓方法论或执行 Git 写操作。

## Approval Gate

2026-10-21 NotifyUser 返回明确批准，批准对象为 spec.md 与 tasks.md。按依赖逐项推进，状态唯一承载于 Status。

## Review Gate

Task 1～9 和任何修复 issue 全部清空后，才创建 review.md。
委托可用时，以全新上下文作一次只读独立审查，逐条覆盖所有 AC/TR；检查实现真实性、读者路径、部署/安全限制与未来快照边界。
可行动发现登记 pending issue 后回到实施，修复并回归；独立 pass 是最终成功出口。

## Planning Log

`[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261021-opencode-deepening | msg=同快照增量学习规划 | ctx={"scenario":"knowledge","depth":"deep","implementation":"awaiting_approval"}`

恢复调查只读完成：启动路由、子项目状态、既有规格和学习地图、固定源码 HEAD 及候选入口已核对。
不将上述规划调查记为 R/I/E/V/C 实施完成。

`[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V | event=GATE_PASSED | session=sc-20261021-opencode-deepening | msg=内容回验修订与文档验证闭合 | ctx={"facts":37,"local_refs":172,"build_exit":0,"target_diagnostics":0}`

`[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C | event=CONCEPT_COMPLETED | session=sc-20261021-opencode-deepening | msg=候选评估完成，不新增主仓模式且不提交 | ctx={"new_patterns":0,"git_writes":0,"next":"independent_review"}`
