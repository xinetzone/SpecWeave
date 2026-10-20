# SST 基础设施即代码框架 OKF Wiki 教程 - Implementation Plan

> **方法论**：七概念知识沉淀场景 `R→I→E→V→C`。以下任务均待用户批准后执行；C 阶段完成验证与交付闭环，不包含未经授权的 Git 提交。

## Task 1: 完成信源稳定性预检并固定研究基线
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 复核 `external/dao/anomalyco/sst` 工作树、tag、完整 commit hash 与 remote，确认源码事实基线为 `v4.17.2` / `e49ac31411f63ab4ed0d802b7e15d95f6b827e47`。
  - 将本机 checkout 分类为 env-bound 工作副本；持久文档只使用 GitHub 固定 commit 坐标，不创建或改动 vendor/submodule。
  - 复核 SST 官方文档页面可公开访问，记录本次采集日期及实际查阅页面；区分官网现行说明与固定源码事实。
  - 检查 SpecWeave 对应的 source-path stability 工具可用于最终 audit；本阶段不引用或写入本机绝对路径。
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `rule` TR-1.1: `git status`、tag、HEAD 与 remote 的记录一致，且提交 hash 精确匹配规格中的源码基线；Evidence: 命令输出与阶段记录。
  - `rule` TR-1.2: 官方文档登记包含实际查阅的页面 URL 与采集日期；Evidence: 页面清单。
  - `rule` TR-1.3: 长期文档引用方案只含不可变 GitHub commit URL 和公开官网 URL，不含本机路径或临时目录；Evidence: 信源方案检查。

## Task 2: 执行 R 阶段源码与官方文档事实采集
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 定向梳理 CLI 命令入口与执行流、项目/应用/阶段/stack/state 模型、server/provider 桥接、运行时、`sdk/js` 与 `platform` 的职责边界，以及 Mosaic/Live 相关源码。
  - 复核官方 Basics、Components、Providers、Linking、CLI、SDK、Live、Console、Monorepo 等页面，并把官网陈述与源码事实分别登记。
  - 将可验证事实编号写入 spec 目录的 `facts.md`；每条事实记录固定提交下的仓库相对文件路径及源码符号/必要行段，不混入洞察或因果判断。
  - 对文档中计划使用的数量陈述先脚本计数并记录口径；不能可靠计数的主题不写数量断言。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-6, AC-8
- **Test Requirements**:
  - `rule` TR-2.1: `facts.md` 中每条源码事实均有 F 编号和固定快照中的可定位出处；Evidence: 事实—路径映射表及源码定向搜索。
  - `rule` TR-2.2: FR-2 列出的每个主题均至少映射到一条源码事实或一条标注日期的官网陈述；Evidence: 初始覆盖矩阵。
  - `rule` TR-2.3: 数量事实包含统计口径与脚本计数证据，事实表不含未经核验的总量；Evidence: 计数脚本/输出及人工枚举交叉检查。

## Task 3: 完成 I 阶段架构洞察与教程知识地图
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 从 F 编号事实提炼至少 3 条彼此区分的架构洞察；每条包含陈述、事实证据、读者可能产生的反直觉误解及对教程组织的行动建议。
  - 将洞察、章节依赖、学习顺序和 FR-2 主题覆盖映射写入 `insights.md` 与 `coverage-matrix.md`。
  - 根据源码事实和官网文档确认正文主题边界，不将尚未核实的模块关系写成设计意图。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-3.1: 每条洞察均引用 F 编号，四元组字段完整，且覆盖矩阵映射 FR-2 全部主题；Evidence: `insights.md` 与 `coverage-matrix.md`。
  - `rubric` TR-3.2: 学习地图连贯性；Scale: 1-5; Anchors: 1 = 主题无依赖关系且来源无法追溯；3 = 主线可读但至少一个关键模块关系或主题映射不清；5 = 由产品模型逐步过渡到源码架构、开发/部署流程，所有主题均映射至事实与章节；Pass Threshold: >= 4; Evidence: 事实覆盖矩阵与章节依赖图。

## Task 4: 先行创建 references 信源登记
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 在目标 bundle 的 `references/` 登记固定源码快照及 SST 官方文档页面集合，记录仓库 URL、tag、完整 commit hash、页面 URL、采集日期和信源边界。
  - 让后续正文 frontmatter 的 `sources` 只指向已存在的 references 文件。
  - 本任务只创建信源正文；各级 `index.md` 留到所有内容文档完成后统一生成。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-4.1: 源码信源包含固定 commit 与上游 URL；官网信源包含实际查阅页面 URL 和日期；Evidence: references 文件核对。
  - `rule` TR-4.2: references 正文及 frontmatter 无本机绝对路径、`file:///`、临时目录路径或浮动分支作为版本锚点；Evidence: 全文路径扫描。

## Task 5: 编写核心概念文档第一批
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 在单批次内新增不超过 7 篇概念文档，暂定主题为：SST 定位与应用模型、配置/应用/阶段/stack/state 关系、CLI 到开发与部署生命周期。
  - 以 `facts.md` 和已登记 references 为依据；将 `sst dev`、deploy、diff 等官网用法与源码可验证的执行路径明确区分。
  - 如 R/I 阶段证据要求调整章节名称或合并主题，在不缩减 FR-2 覆盖的前提下同步覆盖矩阵。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6, AC-8
- **Test Requirements**:
  - `rule` TR-5.1: 每篇概念文档均有合规 frontmatter、有效 sources 引用、相应 F 编号证据和“相关概念”链接；Evidence: 文件级检查。
  - `rule` TR-5.2: 命令、配置字段、类型和执行行为均能回溯到固定源码或明确标日期的官网页面；Evidence: 逐断言溯源表。
  - `rubric` TR-5.3: 新读者可据文档解释应用模型及从本地开发到部署的主流程；Scale: 1-5; Anchors: 1 = 核心术语未定义且流程断裂；3 = 主流程基本可读但源码与产品说明混杂；5 = 先修概念清楚、流程步骤有依据且两类来源边界明确；Pass Threshold: >= 4; Evidence: 独立通读与断言溯源表。

## Task 6: 编写核心概念文档第二批
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 再新增不超过 7 篇概念文档，暂定主题为：组件/provider 边界、Go CLI/server 与 TypeScript platform/runtime 边界、JavaScript SDK 资源链接、Live/Mosaic 开发机制。
  - 根据证据决定是否拆分 provider/组件或合并 Live/Mosaic 内容；不为凑篇数重复已有内容。
  - 代表性组件与 provider 机制以固定源码及已登记官方文档为依据，不声称穷尽全部组件/API。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6, AC-8
- **Test Requirements**:
  - `rule` TR-6.1: 每个关键模块关系均可映射到 F 编号；涉及不存在/不支持的符号或行为时，负向结论有源码搜索证据；Evidence: 符号验证清单。
  - `rule` TR-6.2: concepts 两批各自不超过 7 篇，且 FR-2 全部主题仍在覆盖矩阵中有唯一或明确的多篇映射；Evidence: 文件清单与覆盖矩阵。
  - `rubric` TR-6.3: 多语言与部署组件边界清晰度；Scale: 1-5; Anchors: 1 = Go、TypeScript、provider 和运行时职责混为一谈；3 = 大部分职责已区分但关键调用/数据边界缺证据；5 = 各层职责、连接点和未核验边界均由事实清单支撑；Pass Threshold: >= 4; Evidence: 架构章节及符号验证清单。

## Task 7: 编写不少于三个可核验示例
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5, Task 6
- **Description**:
  - 编写最小应用/组件、资源链接，以及本地开发到部署流程三个示例文档；每次新增批次不超过 7 个文件。
  - 示例命令与代码只使用已核实的 API；对依赖云凭证、收费资源或无法在本环境执行的部分标明验证边界，不宣称完成真实云部署。
  - 示例与相应概念文档互链，并记录来自官网的用法及源码能够佐证的机制。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6, AC-8
- **Test Requirements**:
  - `rule` TR-7.1: 至少三个示例分别覆盖最小应用/组件、资源链接、本地开发至部署，且每个关键符号通过固定源码或官方页面核验；Evidence: 示例清单及符号清单。
  - `rule` TR-7.2: 所有未实际执行的操作、云端依赖与收费边界均有显式说明，无真实部署成功声明；Evidence: 示例边界检查。
  - `rubric` TR-7.3: 示例可学习性；Scale: 1-5; Anchors: 1 = 示例缺少前提或引用虚构 API；3 = 示例大体可跟随但验证边界或概念链接不完整；5 = 示例输入、步骤、关键结果、来源及不可执行边界清楚，能连接对应架构概念；Pass Threshold: >= 4; Evidence: 示例逐项审读与符号核验记录。

## Task 8: 内容定稿后生成 bundle 和父级索引
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 在所有 references、concepts、examples 正文定稿后，最后创建 bundle 根、concepts、examples、references 的 `index.md` 与 `log.md`；每个 index 同时提供人类导航和完整 `{toctree}`。
  - 新建 `jishu/iac/index.md`，更新 `jishu/index.md` 的分组表与 toctree，并在 `doc/bundles/index.md` 重读当前内容后更新技术域说明、导航和递归计数。
  - 记录采集快照、文档范围、批次与验证状态；不将“示例已验证”扩大为真实云部署。
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-8.1: bundle 与分组各级 index 的 `{toctree}` 收录对应目录内所有内容文档，父级导航从文档根可达；Evidence: toctree 检查输出。
  - `rule` TR-8.2: 总索引与技术域说明分别反映全库 652 束 / 63 组 / 9 域、jishu 482 束 / 19 组，并与实际目录树相符；Evidence: 索引文本和目录计数。
  - `rule` TR-8.3: `log.md` 记录源码版本、官网采集日期、范围与验证情况；Evidence: log 文件。

## Task 9: 执行 V 阶段独立事实、格式与路径核验
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 以不同于初次采集的搜索/脚本手段，逐项复核教程中的关键 Go/TypeScript 符号、CLI 命令、组件、参数、资源链接、模块关系和示例。
  - 机械检查 frontmatter、文件名、sources、内部/外部链接、各级 index 与 toctree；复核所有数量断言的统计口径。
  - 运行 source-path stability audit；创建 `verification.md`，登记每项检查结果、证据和修复记录。该文件不是 Spec Mode 的 `review.md`。
  - 发现问题时修复正文或索引并重跑受影响检查，直到无未解决的可行动内容问题。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `rule` TR-9.1: 所有关键符号与示例均有独立验证结果；虚构/无法证实的内容已删除、修正或明确降级为未验证边界；Evidence: `verification.md` 与定向源码搜索。
  - `rule` TR-9.2: 所有数量陈述均经独立复算，注明对象和口径；Evidence: 数量断言表。
  - `rule` TR-9.3: 稳定性 audit 未发现活动文档中的本机绝对路径、`file:///` 或临时信源引用；Evidence: audit 输出及人工分流记录。
  - `rule` TR-9.4: 每条 FR-2 主题覆盖、每个 bundle 内容文档及父级导航均可从最终矩阵/检查输出追溯；Evidence: `coverage-matrix.md` 与检查结果。

## Task 10: 运行项目质量门并完成 C 阶段闭环
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 在 `projects/awesome-okf-xs` 运行 `invoke gates.all` 与 `invoke build`，核实本次变更相关质量门无新增失败；若有既存失败，区分归属并证明本束检查通过。
  - 对照 AC-1 至 AC-8 汇总实现证据，检查最终 `git diff` 与 `git status`，确认只包含批准范围内的 bundle/导航及 Spec Mode 记录。
  - 完成七概念闭环并向用户报告结果；不创建 Git commit，除非用户另行明确要求。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-10.1: `invoke gates.all` 与 `invoke build` 均成功，或对环境/既存失败提供可复查的归属证据及本束定向通过证据；Evidence: 命令输出。
  - `rule` TR-10.2: AC-1 至 AC-8 均有对应完成证据，最终变更集无未批准文件；Evidence: AC 对账表与 `git status`/diff。
  - `rule` TR-10.3: 未执行 Git 提交；Evidence: 最终状态报告。

## Task Dependencies

`Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7 → Task 8 → Task 9 → Task 10`

所有内容与索引任务串行推进，以保证事实和洞察先行、references 先于正文、索引最后生成；每轮概念文档新增量不超过 7 篇。
