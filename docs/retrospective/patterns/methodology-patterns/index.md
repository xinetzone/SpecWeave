# 方法论模式库索引

> 本目录存放经过七概念方法论编排（R→I→E→V）萃取的可复用方法论模式。每个模式均通过G1-G4质量门与V对抗审查。

## 模式清单

| 模式ID | 模式名称 | 成熟度 | 验证次数 | 复用次数 | 触发场景 |
|--------|---------|--------|---------|---------|---------|
| bp-dual-layer | [双层分析报告结构](concepts/dual-layer-analysis-report.md) | L2-validated | 3 | 15 | 需要对网页/文章/技术内容进行"既理解内容又提炼洞察"的双目标分析时 |
| bp-subagent-std | [子代理分析任务标准化指令](concepts/subagent-standardized-instruction.md) | L2-validated | 3 | 3 | 需要委派子代理执行复杂多步骤分析任务时 |
| bp-content-funnel | [内容漏斗分析模式](concepts/content-funnel-analysis.md) | L1-draft | 1 | 1 | 需要对技术文章/行业报告进行递进式深度分析时 |
| bp-integration-over-invention | [整合优于发明模式](concepts/integration-over-invention.md) | L1-draft | 1 | 1 | 存在多个互补开源工具但组合使用门槛高时 |
| bp-offline-first-architecture | [离线优先架构模式](concepts/offline-first-architecture.md) | L1-draft | 1 | 1 | 系统需要在离线状态下保证完整功能可用时 |
| bp-lowering-barriers-creates-markets | [降低门槛即创造市场模式](concepts/lowering-barriers-creates-markets.md) | L1-draft | 1 | 1 | 技术方案成熟但安装配置复杂度阻碍大规模采用时 |
| bp-knowledge-compilation | [知识编译模式](concepts/knowledge-compilation.md) | L1-draft | 2 | 1 | 高频深度使用的结构化知识源（技术书籍/手册/规范）需要比RAG更高的token效率时。[案例：七概念方法论编译](../../../../.agents/skills/seven-concepts-cmd/references/compiled-methodology.md)（10个源文件→365行~4800token自包含Skill） |
| bp-dual-engine-uncertainty-certainty | [不确定性探索+确定性校验双引擎架构](concepts/dual-engine-uncertainty-certainty.md) | L2-validated | 2 | 1 | 高风险AI应用场景（改错即故障）中，AI正确率不足但存在确定性程序校验通道时 |
| bp-evaluation-driven-self-evolution | [评测驱动的自进化闭环](concepts/evaluation-driven-self-evolution.md) | L2-validated | 2 | 1 | AI系统需要持续优化而非一次性交付，且输出可明确判定对错时 |
| bp-responsibility-transfer-governance | [责任转移治理模式](concepts/responsibility-transfer-governance.md) | L2-validated | 2 | 1 | 业务方因风险收益不对等缺乏治理动力，平台方能构建可靠自动化系统兜底时 |
| bp-error-blacklist-monotonic-evolution | [错误黑名单单调进化模式](concepts/error-blacklist-monotonic-evolution.md) | L2-validated | 2 | 1 | 系统需持续提升可靠性，且"重犯已知错误"是主要故障来源时 |
| bp-cross-framework-atomic-analysis | [跨框架原子化设计分析模式](concepts/cross-framework-atomic-analysis.md) | L1-draft | 1 | 0 | AI Agent 库需引入跨框架设计方法论（如原子化设计）并回写到具体 Agent 时 |
| bp-layered-chained-spec | [分层链式规格模式](concepts/layered-chained-spec.md) | L1.5 | 1 | 0 | AI编程/多代理协作中需将vibe coding转化为"按图施工"工程流程时。案例：GitHub Spec Kit六命令+SpecWeave三件套双案例萃取 |
| bp-plugin-bridge-standard-integration | [插件桥接规范集成法](governance-strategy/plugin-bridge-standard-integration.md) | L1-draft | 1 | 1 | 需要把一套工作区规范（AGENTS协议/路由/Skill）接入已运行的Agent平台，且目录感知地自动生效时。案例：Hermes接入SpecWeave规范 |
| bp-automation-idempotent-four-elements | [自动化幂等四要素](tools-automation/automation-idempotent-four-elements.md) | L1-draft | 1 | 1 | 编写部署/启用/验证类操作脚本（安装器/环境引导/CI初始化）需保证幂等可重跑时。案例：specweave-bridge install.py |
| bp-three-layer-repair-closure | [三层修复闭环](concepts/three-layer-repair-closure.md) | L1-draft | 1 | 1 | 反复复发型故障需根治而非治标时。案例：Windows截图工具10天3次复发双源头根因（治标→断源→兜底→沉淀） |
| bp-preflight-integrity-gate | [前置完整性门禁](preflight-integrity-gate.md) | L1-draft | 1 | 0 | 本地容错工具（编辑器/浏览器）掩盖的数据损坏（编码截断/非法字节/格式错误）需在 CI 依赖安装与构建之前主动曝光（shift-left）时。案例：awesome-okf-xs 12个UTF-8损坏文档于Sphinx构建阶段暴露 |
| bp-destructive-probe-gate | [破坏性探针双向验证门禁](destructive-probe-gate.md) | L1-draft | 1 | 0 | 为 CI 新增校验性 gate 脚本（格式/编码/lint/门禁）时，需双向验证"异常输入拦得住、正常输入放得行"，防止 gate 逻辑缺陷形同虚设。案例：check-utf8.py 截断中文字节探针双向闭环 |
| bp-history-based-doc-repair | [历史基线文档修复法](history-based-doc-repair.md) | L1-draft | 1 | 0 | Markdown/YAML 等文本文件出现编码损坏（UTF-8 截断/U+FFFD/非法字节）且损坏前存在完好 git 历史版本时。案例：awesome-okf-xs 12个损坏文档以历史提交基线无损重建 |
| pattern-failure-annotation-config | [故障注释固化](retrospective-knowledge/failure-annotation-config.md) | L2-validated | 2 | 0 | 构建/工具链配置因外部组件组合行为反复出错时，将故障因果链就地固化于防御性配置值旁的注释与钩子 docstring。案例：awesome-okf-xs/doc/conf.py 14提交9fix 全量固化（正例）+ 主仓库钩子复制未带修复形成活跃滞后缺口（反例） |
| bp-nav-co-registration | [生成-登记同步法](concepts/nav-co-registration.md) | L1.5 | 2 | 0 | 批量生成结构化内容（知识包/Wiki/报告）需通过导航层（toctree/索引表/注册表）被消费时。案例：docs全量审计2,245处导航债务+OKF v0.2转换双案例（同谱系，待跨项目正向验证升级L2） |
| bp-tech-article-to-wiki-batch | [技术文章Wiki化批量生成模式](concepts/tech-article-to-wiki-batch-generation.md) | L2-validated | 6 | 6 | 将长技术文章/教程（800行以上、多章节需独立引用）转化为原子化Wiki结构时：Spec约束下子代理批量生成原子文件、自动化工具链修复元数据/索引、链接检查为必经门禁（8步标准化流程；短篇<500行用单文件轻量变体）。案例：Harness Engineering Wiki 2小时10原子文件 |
| batch-docs-to-okf-bundle-conversion | [批量Markdown文档到OKF Bundle转换模式](concepts/batch-docs-to-okf-bundle-conversion.md) | stable | — | — | 大量散乱Markdown文档（20+）需批量转换为结构化OKF v0.2 Bundle时：R→I→E→V→C五阶段分批工作流，覆盖frontmatter统一补全、index导航建立、跨文档链接修复与正文保真验证 |
| bp-classical-commentary-dual-layer-bundle | [古典文本-现代阐释双层Bundle构建模式](concepts/classical-commentary-dual-layer-bundle.md) | L1-draft | 1 | 0 | 同一主题存在古典原文+现代阐释双层结构时，需构建两个独立OKF Bundle并通过F编号隔离避免交叉冲突。案例：《了凡四训》+《了凡生意经》双层Bundle |
| capability-precondition-pairing | [能力前提配对搬运](tools-automation/capability-precondition-pairing.md) | L1-draft | 1 | 0 | 搬运/复制某项能力资产（二进制/工具/服务）时，其运行前提（宿主侧启动器路径、环境变量、外部回调二进制）未随资产一并搬运，导致目标环境报裸错误而非可执行指引时。案例：jupyter-podman-rootless 镜像 toolbox 缺 `TOOLBOX_PATH` 与 `flatpak-spawn` 前提 |
| validation-probe-semantics-convergence | [验证探针语义收敛](tools-automation/validation-probe-semantics-convergence.md) | L1-draft | 1 | 0 | 构建/CI/健康检查中的验证探针因短路型 flag + 输出重定向 + `&&` 链而恒真，且声明（available/可用）超出自证范围（存在性/活性）时。案例：jupyter-podman-rootless 镜像工具箱探针假阳性（Containerfile:191/725，`toolbox --help >/dev/null 2>&1` 恒真） |
| pattern-summary-over-transcription | [摘要替代转录](summary-over-transcription.md) | L2-validated | 2 | 0 | 扫描版版权书籍（纯图像或图像+噪声OCR混合型）转教程/知识包时：route 决策前置、多模态通读、深度摘要+原创改写替代逐字转录。案例1《管道的故事》、案例2《魔力》（混合型PDF+练习册体裁） |
| pattern-compliance-contracting | [合规契约化](compliance-contracting.md) | L2-validated | 2 | 0 | 版权引用/数据脱敏等合规红线需经他人审查时：态度式约束翻译为可度量契约（数字/正则/清单+计数口径），三段式声明、按契约打勾；含"作者主张—客观事实"分层第二契约轴。案例1《管道的故事》、案例2《魔力》 |
| bp-doc-automation-pipeline | [文档自动化生成与验证流水线模式](concepts/doc-automation-pipeline.md)（简称：文档流水线模式） | L1-draft | 1 | 0 | 文档规模扩大后（经验阈值约 500 条目，非测量值），以统一元数据规范+自动化脚本（模板生成/链接验证/索引生成）+质量门禁构成生成-验证流水线，突破人工维护索引的规模瓶颈；含多生产者契约漂移等 5 条反模式。案例：SpecWeave 智能文档系统 1288 条目 |
| net-value-four-questions | [净时薪四问](governance-strategy/net-value-four-questions.md) | L1-draft | 1 | 0 | 在多个外部机会/平台之间做取舍（副业平台、外包供应商、SaaS 工具、开源依赖），且决策依据主要来自对方宣传口径或当期数据时：先用"净时薪—无补贴模型—替代成本—提现闭环—合规三查"五步做三缺口收敛（计量/时点/退出），再进入加权比较。案例：2026 中国副业平台全面调研（73 条事实） |
| content-sensitivity-routing | [公私域内容分离路由](governance-strategy/content-sensitivity-routing.md) | L1-draft | 1 | 0 | 任何同时承载公开与私域内容的工作区/文档中心长期演进时：任务启动即按内容敏感度分流（公开→docs/ 标准工作流，私域→playground/ 简化工作流），私域转公开走显式脱敏提取，落盘前三查防路径残留。案例：SpecWeave 全仓 100 天演进（2026-08-31 docs/ 唯一文档中心确立），规则落地于 .agents/rules/content-sensitivity-precheck.md |
| bp-weight-aligned-prep | [权重对位备赛法](product-growth/weight-aligned-preparation.md) | L1-draft | 1 | 0 | 评审标准（维度+权重）完全公开、以"材料包+演示"交付的竞赛/黑客松/政府专项申报/基金答辩：把评分表当公开契约，先判评分模型并清零准入门槛，再按边际得分率与权重对位组织证据物和工时，含评分表版本管理与临赛降级路径。案例：2026上海开源软件应用创新大赛（创新30/落地30/治理20/长期20，F-004~F-065） |
| minimal-sufficient-scaffold | [最小充分脚手架选型法](governance-strategy/minimal-sufficient-scaffold-selection.md) | L1-draft | 3（外部） | 0 | agent 框架/SDK/harness 选库：功能清单趋同、star 失真、0.x 频变的高速迭代赛道，按"任务分级→最小执行环→同任务小赛（TTFA/LOC/治理缺口）→生命体征检查→最薄栈+治理三件套→锁版本"六步选型。案例：AI Harness Python 包全景调研（mini-swe-agent 131 行/65% 对 SWE-agent 4161 行/67%、七框架实测、AutoGPT 退潮三外部案例），待本项目实战验证升 L2 |
| scenario-interval-selection | [场景区间选型法](governance-strategy/scenario-interval-selection.md) | L1-draft | 1 | 0 | 同治理体系内两个相邻根社区/基础软件分支（同源、特性表重叠、名称易混但按工作负载分工）选型：不按知名度与总量横评，按"工作负载形态→商业下游与合规→生命周期→生态技能存量→硬件适配"五问固定顺序归区，再以目标环境最小实测收口，生产承诺只给商业下游。案例：openEuler vs openKylin 后端/桌面双根社区（47 条双侧事实、8 条 V 意见），待第二个非同谱系场景验证升 L1 |
| reverse-order-doc-learning | [逆序文档学习法](research-knowledge/reverse-order-doc-learning.md) | L1-draft | 1 | 0 | 百篇级、多人贡献、时效不均的社区/Git 文档站学习：不按官方目录顺读，先以版本控制接口逆向建图（文件树量化分布、骨架扫描、提交记录定年），再按学习者问题域（选型→安装→使用→开发→贡献）重组路径，三方交叉验证、冲突显式标注。案例：openKylin 文档平台 237 篇逆向导读（44 事实/4 洞察、首页与新手入口最旧），待第二个非同谱系文档站验证升 L1.5 |
| docs-as-product | [文档即产品经营法](governance-strategy/docs-as-product.md) | L1-draft | 1 | 0 | 文档已成为对外交付面（用户按文档接入、集成方按文档判兼容、AI 检索按文档作答）且读者异质（终端用户/集成方/内部工程师/机器消费者）时：以"读者契约→最小公理集合→Diátaxis 四型原子分区→质量门内建 CI→预览发布节奏→M1–M5 指标回灌"六步把文档当产品持续经营。案例：QwenWork Canvas《文档即产品》主张页 V6 发布态（22 事实/4 洞察），待第二个非同谱系场景验证升 L1.5 |
| migration-triggered-convention-alignment | [迁移窗口的结构约定对齐法（迁入即治理）](governance-strategy/migration-triggered-convention-alignment.md) | L1 | 1 | 0 | 外部单体或新包迁入已存在公共约定的统一仓库（monorepo）、迁入动作一次性暴露被迁包隐性私有约定时：在同一迁移窗口内完成私有约定→公共约束对齐（构建后端与参数/语言版本/版本来源/目录文档形态），以未解释偏离数替代功能提交计数，并将可机械判定项纳入自动核验。案例：xuan-compose 迁入玄境 monorepo（2026-08-26 后 38 次增量；同期上游怪癖分级并入 behavior-characterization-freeze），待跨项目验证升 L2 |
| unified-contract-tool-orchestration-layer | [统一契约工具编排层](product-growth/unified-contract-tool-orchestration-layer.md) | L1-draft | 1 | 0 | 一个消费者需统一使用多个异构外部工具（AI agent/上层服务），且工具为用户自备不可改造时：不逐工具接入，而是在消费者与工具间插入统一契约适配层——每个工具经 Provider 适配器接入，把"工具结果+元数据+运行时观测"规整为契约化工具与证据，能力以契约为单一事实源、CLI/前端只是契约投影，本地优先有界证据。案例：REA rea-agents v6.4.0 统一 MCP 契约编排（66 条源码事实） |
| wsl-network-share-drvfs-mount | [WSL 网络共享 drvfs 挂载三段验证与幂等持久化法](tools-automation/wsl-network-share-drvfs-mount.md) | L1-draft | 1 | 0 | 在 WSL 中挂载 Windows 盘或 SMB 共享时：先在 Windows 侧只读探测既有认证会话（盘符映射/凭据）再以 drvfs 复用，按「挂载表→目录非空→业务用户写探针」三层证据验收，持久化走「备份→grep 幂等守卫→nofail fstab→terminate 冷启动实证」。案例：\\10.16.11.3\ai 经 S: 映射挂入 openKylin-3.0（2026-10-13） |
| community-metric-triple-check | [社区指标三查法（口径-时点-独立性）](governance-strategy/community-metric-triple-check.md) | L1-draft | 1 | 0 | 引用开源社区/厂商生态规模指标（用户数/开发者数/成员单位/SIG/部署量）撰写评估或尽调时：按「查口径→查时点→查独立性」三查强制核验，再以「冲突并陈不裁决、引用降级标口径」两道收口对齐结论强度与证据等级；含 6 条反模式与三问检验标准。案例：openKylin 全面评估（145 条事实、12 项冲突/12 项缺口），待非同谱系第二案例验证升 L1.5 |
| gap-two-round-verification | [缺口双轮核验法（公开信源轮+零变更功能轮）](research-knowledge/gap-two-round-verification.md) | L1-draft | 1 | 0 | 评估/尽调报告交付时仍挂「未获取/待验证」缺口清单，或完整复现用户路径成本过高（GB 级镜像/账号/GUI）时：第一轮公开信源轮（换环境复述+服务端配置/目录枚举/包元数据等供给侧观测点优先+负证据强制留痕），第二轮零变更功能轮（模拟安装/下载解包/strings 静态取证/免安装冒烟/总线只读探测），结论锚定 L0~L3 四档证据等级，三道收口（评分解耦/未验证留痕/前后对账）；含 7 条反模式与 6 条检验标准。案例：openKylin 评估 Q-1~Q-8 双轮核验（61 条 VF 事实），待非同谱系第二案例验证升 L1.5 |
| citation-evidence-reconciliation | [引文回证对账](ai-collaboration/citation-evidence-reconciliation.md) | L1-draft | 1 | 0 | 成稿含成批带出处直接引用且原始证据可第三方独立打开时：判定口径先脚本化冻结，机械枚举全部引号样式（含覆盖率交叉核验）后按漏斗分流回证（存在性/逐字性/跨度），核验与修复分波分代理，收口毛=净+排除复算闭环；含非引号事实抽样回证位与复查触发器。单案例萃取（扫描版权书转多代理Wiki生产线，证据留私域溯源），待非同谱系第二案例升L1.5 |
| cross-period-metric-scope-alignment | [跨期指标口径对齐先行](governance-strategy/cross-period-metric-scope-alignment.md) | L1 | 1 | 0 | 对同一对象做第二次及以后的度量对比，且两次观测之间存在结构治理动作（目录迁移/资产归并/分类重构）时 |
| two-round-source-strategy | [双轮信源·漂移检出法](ai-collaboration/two-round-source-strategy.md) | L2 | 2 | 1 | 为同时有源码与官方手册的系统产出可溯源教程，且手册的人读层可能过期时（XERJ 两轮检出 6 处漂移，其中 1 处为分析器清单实质错误） |
| hermetic-isolated-verification | [隔离验证法](ai-collaboration/hermetic-isolated-verification.md) | L2 | 2 | 2 | 验证大树里的局部变更，整树验证慢到会被跳过或被并行会话写入打断时（XERJ 束 31 文件 0 warning，替代 10 分钟以上且会被竞态打断的整树构建） |
| shared-index-count-coupling | [共享索引计数耦合与同批判决](governance-strategy/shared-index-count-coupling.md) | L2 | 3 | 3 | 共享索引的计数由目录树派生、且多会话并行写同一仓库时，新增条目必然要改共享索引多处（awesome-okf-xs 子模块三次提交） |
| governance-engine-dual-loop | [治理×引擎双件闭环](governance-strategy/governance-engine-dual-loop.md) | L1.5 | 3 | 1 | 规则密集型资产（约定文件/检测器/门禁/装载管道）需持续优化与自进化时：拆「守护件（合规路由+回归矩阵+误报防护）×引擎件（R→I→E→V 分析决策）」，引擎产出经守护验证后原子写回，双件各自演进。案例：agent-workspace-conventions×七概念组合、技能自动装载器、awesome-okf-xs UTF-8 治理 |
| symbol-vs-variable-decomposition | [符号之争与变量之争分离法](research-knowledge/symbol-vs-variable-decomposition.md) | L1-draft | 1 | 0 | 议题被渲染成「是否应当承认/允许某种形式」的二元道德之争、双方长期僵持无新证据进入时：先检验形式特征与目标结果间是否存在单调因果（横截面/纵向/实验三型证据，结论三态判定），若无则判定为符号之争并重述为「哪个变量通过什么机制影响结果」（控制权+退出权+救济可达性），再按功能清单分级为「不触及符号可先行项」与「须触及符号设前置条件项」；含 6 条反模式与 8 条边界前提。案例：一夫多妻议题分析（74 条事实/8 假设证伪/9 要素/6 公理），待非同谱系第二案例验证升 L1.5 |
| decomposable-recognition-ladder | [可分离承认阶梯法](research-knowledge/decomposable-recognition-ladder.md) | L1-draft | 1 | 0 | 「承认某形式」被当作全有全无的开关、且承认具有符号溢出性质（资格外溢至舆论/动员/文化）时：按符号触及度与保护强度双轴把承认拆成 L0–L4 阶梯，使零符号成本的功能保障先行落地、符号型承认置于可被经验证据满足的前置条件之后，并评估无为选项（一阶/二阶后果）；含 7 条反模式与 8 条边界前提。案例：一夫多妻议题分析（L0–L4 五级阶梯 + 无为三方案），待非同谱系第二案例验证升 L1.5 |
| release-eligibility-invariant-gate | [发布资格不变量与发布路径对账](governance-strategy/release-eligibility-invariant-gate.md) | L1 | 1 | 0 | 版本坐标四者（标签/变更记录/声明版本号/分发面实际发布）不闭合、或唯一高标准关卡不在发布触发路径上、且发布由人工事件触发时：先建坐标台账→判可达与谱系→写成可判定的发布资格不变量清单→挂到发布触发路径并消灭人工旁路→不可修复项显式登记→发布后回写再对账。案例：mystx 13 个 tag 分属 6 条谱系且 11 个非 HEAD 祖先、12 个无变更记录条目、最新 tag v0.3.8 未发布到任何分发面、三 workflow 无 pytest 且唯一会失败的 RTD 关卡不在发布路径上（F-008~F-012、F-049、F-054、F-058~F-061、F-071、F-072、F-089、F-092~F-094、F-097） |
| single-authority-declaration-alignment | [单一权威源与多载体声明面对齐](governance-strategy/single-authority-declaration-alignment.md) | L1 | 1 | 0 | 同一事实被 ≥2 个载体手工声明且未指定权威源时：先显式定源，其余载体降级为投影并由机器校验对齐，差异须登记理由而非强制全等，冗余本身不算缺陷。案例：mystx 的 PEP 621 extras 与 PEP 735 groups 双轨 dev 组 21 项 vs 11 项分叉、README「核心依赖」5 项与空 dependencies 矛盾、flake8 行长 100 vs ruff/black 120（F-025~F-028、F-031、F-033、F-063、F-064、F-066、F-067） |

## 成熟度等级说明

| 等级 | 名称 | 标准 |
|------|------|------|
| L1-draft | 假设性模式 | 单案例,待验证 |
| L1.5 | 同谱系双案例 | 同一方法论谱系的两个独立实现互为验证,待第三方独立案例升级L2 |
| L2-validated | 已验证模式 | ≥2独立案例,已在本项目验证 |
| L3-mature | 成熟模式 | 跨项目验证,有明确边界条件 |
| L4-optimized | 优化模式 | 经过对抗审查,工具化/自动化支持 |

## 模式入库流程

1. **R阶段（复盘）**:采集案例事实,≥2个独立案例
2. **I阶段（洞察）**:提炼跨案例共性,形成四元组洞察（现象+根因+影响+建议）
3. **E阶段（萃取）**:按标准模板结构化模式（触发场景+核心做法+反模式+检验标准+迁移示例）
4. **V阶段（对抗审查）**:多视角攻击验证,≥5条审查意见,采纳≥2条修正
5. **入库**:创建模式文档+更新本索引+创建TOML元数据

详见 [萃取指令集](../../../../.agents/commands/extraction.md) 与 [七概念方法论编排指令集](../../../../.agents/commands/seven-concepts.md)。

## 关联资源

- 七概念方法论体系索引（如存在，待创建）
- [网页内容→结构化学习笔记 模式库](../../reports/concepts/milestone/web-content-learning-notes-patterns-20260801.md)
- [萃取指令集](../../../../.agents/commands/extraction.md)
- [七概念方法论编排指令集](../../../../.agents/commands/seven-concepts.md)

```{toctree}
:maxdepth: 2

ai-collaboration/index
concepts/index
creative-design/index
document-architecture/index
governance-strategy/index
product-growth/index
research-knowledge/index
retrospective-knowledge/index
spec-workflow/index
tools-automation/index
CATEGORIES
compliance-contracting
destructive-probe-gate
history-based-doc-repair
log
preflight-integrity-gate
prompt-extraction
summary-over-transcription
```

> AI生成
