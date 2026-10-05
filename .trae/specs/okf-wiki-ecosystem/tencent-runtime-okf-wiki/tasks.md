# 腾讯运行时生态源码批次 OKF Wiki - 实施计划

> 方法论：seven-concepts-cmd 场景 4（知识沉淀 R→I→E + 强制 V + C 收口），执行纪律遵循 source-code-to-okf-wiki v1.4。
> 四条束链路在 G0 通过后可并行推进；索引/门禁/评审为串行收口。每束产物根：`projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/`。

## Task 1: G0 信源稳定性门与环境基线
- **Status**: `completed`（2026-10-03 基线采集，2026-10-04 会话恢复时逐项复核相符）
- **Priority**: high
- **Depends On**: None
- **Completion Evidence**:
  - **TR-1.1 信源基线表**（2026-10-04 重新执行 `git rev-parse HEAD` + `git describe --tags --abbrev=0` + `git ls-files | Measure-Object -Line`，输出与 2026-10-03 基线逐一相符）：

    | 仓库 | remote | HEAD commit | 最近 tag | 跟踪文件 | 许可证 | 束动作 |
    |---|---|---|---|---|---|---|
    | CubeSandbox | git@github.com:TencentCloud/CubeSandbox.git | `e02976ae54729fb1684c5b51535381e54df1aea2` | v0.7.2（+11 commits，未切 tag） | 3938 | Apache-2.0（README 徽章；LICENSE 为腾讯开源声明文本，references 登记时原文引用） | 新建 cubesandbox/ |
    | Octop | git@github.com:TencentCloud/Octop.git | `e473dd3c4a4741618ffde1a42a3492341a189e8e` | v1.0.2b5（HEAD 即 tag） | 3697 | MIT | octop 束增量 |
    | TencentDB-Agent-Memory | git@github.com:TencentCloud/TencentDB-Agent-Memory.git | `8b86874a2daea49e3ff0fb53d699203146c5c77d` | v2.0.2-beta.3（+7） | 1106 | MIT（README 徽章，以 LICENSE 原文复核为准） | 新建 tencentdb-agent-memory/ |
    | tencentcloud-sdk-python | git@github.com:TencentCloud/tencentcloud-sdk-python.git | `be50b26d4d997c5d8d9c07fc84c03ee5e05ece68` | 3.1.185 | 1952 | Apache-2.0 | 新建 tencentcloud-sdk-python/ |

    获取日期均为 2026-10-03；信源位于主仓 gitignore 的 `external/dao/runtime/tencent/`，只读、不切 tag/分支，事实以 commit hash 锚定（NFR-5）。
  - **TR-1.2 子模块状态**：`projects/awesome-okf-xs` 分支 `feat/zhen-xu-qiu-reading-bundle`。工作树 12 项他方/在途变更，全部集中在 tencent-meeting-cli 束与 tencent/index.md，与本批次隔离：
    1. `tencent/index.md`（M，Task 16 改前必须先 Read 磁盘版）
    2. tencent-meeting-cli 束 10 个 M 文件（concepts/00、01、02、06、index；根 index；log；references/index；spec/facts；spec/insights）
    3. 未跟踪 `references/user-manual-qqdoc.md`（已被 00-overview.md 引用，属 0.2.0 版残留）
    隔离纪律：不 commit、不 revert、不 `git add 目录`；本批只 Write 新文件/Edit 精确目标；提交阶段（未来）显式列文件。
  - **TR-1.3 frontmatter/结构速查**（双源：子项目 `.agents/rules/frontmatter.md` + tencent-meeting-cli 束实况）：唯一必填 `type`；bundle 根 index.md 带 `type: bundle`/`okf_version: "0.2"`/`scope`/`name`/`version`/`source`/`description`；log.md 带 `type: Changelog`/`scope`/`name`/`version`；内容文件 type 取 Concept/Example/Reference/spec-facts，含 title（带引号）/description/tags/generated/verified/status/stale_after/sources；子目录 index.md 无 frontmatter、含人类导航 + 隐藏 `{toctree}`（`:maxdepth: 7`，无 .md 后缀）；根 index.md 末尾隐藏 toctree 收 concepts/index、examples/index、references/index、spec/facts、spec/insights、log；sources 内引用 `/references/xxx.md` bundle 相对；裸日期由 doc/conf.py 钩子自动加引号照写；Invoke 3.0.3 可用，门禁在子模块根跑 `invoke gates.all`/`invoke build`。
- **Description**:
  - 记录四仓远程 URL、tag、commit hash、获取日期（CubeSandbox `e02976ae`/v0.7.2+11；Octop `e473dd3c`=v1.0.2b5；Agent-Memory `8b86874`/v2.0.2-beta.3+7；SDK `be50b26d4`=3.1.185），形成四束共用的信源基线表（写入本任务完成证据，供各 references 引用）。
  - 核实 awesome-okf-xs 子模块工作树：当前分支、`git status` 是否干净、是否存在他方未提交变更（若有，登记隔离清单）。
  - 精读 OKF frontmatter 规范（子项目 `.agents/rules/frontmatter.md`）与最近模板束（tencent-meeting-cli 的 index/log/一篇 concept/一篇 reference/frontmatter 字段实况），确认 gates 调用方式（invoke 是否可用、Python 环境）。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-1.1: 四仓信源基线表 8 要素齐全（仓库/URL/tag/commit/日期/许可证/文件规模/束动作），`git rev-parse HEAD` 输出与表中 hash 逐一相符；证据：命令输出。
  - `rule` TR-1.2: 子模块工作树状态已书面记录（分支名 + status 清单 + 他方变更隔离结论）。
  - `rule` TR-1.3: frontmatter 必填字段与 toctree 格式从规范与模板束双源确认，产出一份字段速查（不入库，作为后续批次内部依据）。
- **Notes**: 不切换任何仓库 tag/分支；external/ 只读。

## Task 2: CubeSandbox R 阶段——分层事实采集
- **Status**: `in_progress`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 分层采样阅读：① 文档层（README_zh、CONTRIBUTING_zh、docs/zh/guide 全系列 quickstart/usecases/tutorials、AGENTS.md）；② 拓扑层（根 Makefile、各组件 Makefile/Dockerfile、deploy、openapi.yml、pkgs/proto）；③ 机制层关键文件（agent/src/*.rs 19 模块、hypervisor/src、cubecow、CubeShim、Cubelet、CubeMaster、CubeOps、CubeNet/cubevs 与 C 头、sdk 三语言入口）。
  - 产出 `cubesandbox/spec/facts.md`：编号 F-001 起，预计 120-180 条；每条含路径+符号/行号，零推断词，三级标记（代码证实/文档声称/推断）。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-2.1: facts.md 覆盖 FR-1 全部 10 个主题面（组件拓扑/VM 生命周期/控制面/节点面/网络/快照/API/SDK/部署/安全），每个主题面有事实编号区间映射表。
  - `rule` TR-2.2: G1 词表（用于|目的是|设计为|旨在|为了）在事实条目扫描零命中（标题/引用块除外）。
  - `rule` TR-2.3: 抽 20 条事实回溯，路径与符号在 commit e02976ae 中存在。

## Task 3: CubeSandbox I 阶段——架构洞察与知识地图
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 产出 `cubesandbox/spec/insights.md`：3-5 个洞察四元组（陈述/证据 F 编号/反常识/行动），须至少覆盖：极速启动与低开销的实现代价（RustVMM 极简设备模型/预置模板）、控制面-运维面-节点面拆分（v0.7 CubeOps）、CoW 快照与跨节点恢复的存储设计、E2B 兼容作为生态接入策略。
  - 确定 concepts 00-NN 编号与每篇覆盖的 F 编号区间、examples/references 清单。
- **Acceptance Criteria Addressed**: AC-2, AC-8
- **Test Requirements**:
  - `rule` TR-3.1: 每个洞察四元组完整且证据均引用 F 编号。
  - `rubric` TR-3.2: 洞察深度；1-5；1=复述 README，3=有机制解释，5=含反常识张力与工程取舍；阈值 >= 4；证据：抽读评分。

## Task 4: CubeSandbox E 阶段批次 A——references + concepts 00-05
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 信源先行：先建 references/ 5-7 份（openapi/proto、agent+hypervisor、CubeMaster+CubeOps+Cubelet、CubeNet、cubecow+存储、sdk、部署文档），含远程 URL+commit 溯源。
  - 分批写 concepts 00-05（总体架构、VM 生命周期、控制面/运维面、节点面 Cubelet、CubeNet 网络、安全/凭证与 egress），每文件 frontmatter 合规、结尾相关概念、bundle-relative 链接。
- **Acceptance Criteria Addressed**: AC-1, AC-7, AC-8, AC-10
- **Test Requirements**:
  - `rule` TR-4.1: references 文件先于 concepts 完成（git/文件时间戳与内容引用一致），每份信源含 commit e02976ae。
  - `rule` TR-4.2: 6 篇 concept 的关键标识符全部能在 facts.md 找到对应 F 条目。
  - `rubric` TR-4.3: 教学质量；1-5（锚点见 AC-8）；阈值 >= 4。

## Task 5: CubeSandbox E 阶段批次 B——concepts 06+、examples 与各级 index/log
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - concepts 06-11（快照与暂停恢复、E2B 兼容 API、三语言 SDK、部署形态、其余主题按 I 阶段地图补齐到 8-12 篇总量）。
  - examples 2-4 篇（快速创建沙箱、快照/克隆工作流、SDK 调用 E2B 兼容示例、K8s/集群部署择要）。
  - 最后写 concepts/index.md、examples/index.md、references/index.md 与根 index.md、log.md（含 toctree 块）。
- **Acceptance Criteria Addressed**: AC-1, AC-8, AC-10
- **Test Requirements**:
  - `rule` TR-5.1: 全部 index.md 含 `{toctree}` 且逐条收录本目录全部内容文件；目录文件数与索引清单一致（计数断言）。
  - `rule` TR-5.2: 示例代码的 API/命令均来自 facts.md 已验证条目。
  - `rubric` TR-5.3: 示例可操作性；1-5；3=步骤完整，5=含易错点与预期输出；阈值 >= 4。

## Task 6: CubeSandbox V 阶段——束内自验修复
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 结构/frontmatter/链接检查；对 ≥15 个关键标识符（如 agent 模块 struct、CubeMaster 路由、openapi operationId、sdk 方法名）做 Grep 存在性验证；全部数量陈述独立计数；修复并留痕。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-10
- **Test Requirements**:
  - `rule` TR-6.1: 虚构标识符 = 0；计数断言不一致项 = 0；验证表入任务证据。
  - `rule` TR-6.2: 相对链接/dummy 构建本束页面零 error。

## Task 7: TencentDB-Agent-Memory R 阶段
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 先用 `git ls-files` 建立完整目录树（MemoryCore/MemoryPanel/MemoryProxy/deploy 等真实布局），读 package.json/workspaces、start-all.sh、.env.example、INSTALL/ROADMAP。
  - 精读：Proxy server.ts 路由注册全集、MemoryCore gateway v2/v3-router 与 L0-L3 模型、资产萃取（Chat Memory/Skills/Wiki/CodeGraph）代码与存储层、Panel 路由/API、迁移脚本。
  - 产出 `tencentdb-agent-memory/spec/facts.md`（F-001 起，预计 70-110 条）。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-7.1: 覆盖 FR-2 七个主题面；G1 推断词扫描零命中；抽 15 条回溯命中。
  - `rule` TR-7.2: 端口/端点/环境变量三类清单逐一以源码或 INSTALL 为据，冲突处以代码为准并标注。

## Task 8: TencentDB-Agent-Memory I+E 阶段
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - insights.md 3-4 个（零代码接入的协议经济学、L0-L3 隔离与 v2→v3 迁移、资产自动萃取管线、beta 演进风险）。
  - references 4-6 份先写；concepts 5-7 篇（产品与三服务拓扑、Proxy 拦截路由、Core 数据面 L0-L3、资产模型与萃取、Hub/团队、部署配置、beta 边界）；examples 2-3 篇（一键部署+接入 Claude Code/CodeBuddy、团队共享与 API key、v2→v3 迁移）；各级 index/log 最后写。
- **Acceptance Criteria Addressed**: AC-1, AC-7, AC-8, AC-10
- **Test Requirements**:
  - `rule` TR-8.1: 篇数在 FR-2 区间；信源先于概念；index toctree 计数一致。
  - `rubric` TR-8.2: 教学质量；1-5；阈值 >= 4；证据：抽读 2 概念+1 示例。

## Task 9: TencentDB-Agent-Memory V 阶段
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 8
- **Description**: ≥15 标识符 Grep 验证（路由路径、端口、服务名、schema 字段、env 变量）、计数断言、链接/frontmatter、beta 风险与 stale_after 标注核查；修复留痕。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-10
- **Test Requirements**:
  - `rule` TR-9.1: 虚构项=0、计数不一致=0；stale_after 短于稳定束并在 index 说明 beta 时效。

## Task 10: Octop 增量 R 阶段——1.0 差异事实采集
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 以 CHANGELOG（1.0.2b1-b5 + 0.9.x→1.0 段）为索引，在 src/octop 抽查并量化：infra 子包清单、RepoBundle Repo 数、CLI 子命令数、schema 迁移版本链（v7→v18 文件编号）、_boot_runtime 装配变化、octop-harness 包 API 面、teams/connectors/skills/experts/backend/history/setup/i18n 代表符号。
  - 产出 `octop/spec/facts.md` 追加段（F-134 起，不改旧条目），每条标注新增/变更/废弃。
  - 形成旧 16 文档修订点台账（文件→行/章节→旧口径→新口径→证据 F）。
- **Acceptance Criteria Addressed**: AC-2, AC-9
- **Test Requirements**:
  - `rule` TR-10.1: 所有"变化"断言有 CHANGELOG 或代码双证据之一，计数类（Repo/命令/迁移数）经 Grep 独立计数。
  - `rule` TR-10.2: 修订点台账覆盖旧文档全部受影响条目，无事实性失效遗漏（抽查旧文档每篇至少比对 3 个关键断言）。

## Task 11: Octop 增量 E 阶段——续编号扩展与定点修订
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 新增 references 信源登记（v1.0.2b5，commit e473dd3c，记录信源路径迁移说明）。
  - insights.md 追加 1.0 新洞察（编号 I-06 起）。
  - concepts 续编号 07+（teams 协作、connectors/OAuth、skills/experts、backend 远程存储、history、setup/TLS、i18n 等择要 4-6 篇）；examples 续编号 04+（1-2 篇，如云桥接/团队或连接器实战）。
  - 按台账定点修订旧 16 文档（仅事实/版本口径，保留结论框架）；更新根 index（表格+toctree+信任说明版本）与 log.md 顶部 v2 条目；追加子目录 index 条目。
- **Acceptance Criteria Addressed**: AC-1, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `rule` TR-11.1: git diff 中无旧文件改名/删除；旧文件改动行与台账一一对应。
  - `rule` TR-11.2: 新文件编号严格续接；新事实 F 编号无重号。
  - `rubric` TR-11.3: 新旧内容一致性；1-5；3=无矛盾，5=交叉引用自然、学习路径连贯；阈值 >= 4。

## Task 12: Octop 增量 V 阶段
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 11
- **Description**: 新内容 ≥15 标识符 Grep；旧文档修订点逐条回归（旧断言要么有据保留要么已改）；计数断言（新篇数/事实数/Repo/命令数）；链接/frontmatter；修复留痕。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-9, AC-10
- **Test Requirements**:
  - `rule` TR-12.1: 虚构=0、计数不一致=0、台账修订闭环率 100%。

## Task 13: tencentcloud-sdk-python R 阶段
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - common 包全模块事实：abstract_client（含 TC3 与旧签名分支）、sign、http/profile、credentials（含 STS/角色/OIDC 若有）、abstract_model、exception、regions/endpoint、retry（sync+async）、interceptor chain；setup.py 分包发布；products.md 规模独立计数。
  - 产品包抽样：cvm（v20170312）、hunyuan（v20230901），COS 以在仓事实定（若无则记录并选替代）；走通 README 调用链涉及的类/方法。
  - 产出 `tencentcloud-sdk-python/spec/facts.md`（F-001 起，预计 70-110 条）。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-13.1: 覆盖 FR-3 六个概念主题 + 三个示例场景；签名算法每一步对应代码行（canonical/string2sign/派生签名）。
  - `rule` TR-13.2: 产品包数量与代表包结构（models/client 文件构成）经 Glob 独立计数。

## Task 14: tencentcloud-sdk-python I+E 阶段
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 13
- **Description**:
  - insights.md 3-4 个（代码生成器决定的同构架构、双签名/双版本兼容策略、interceptor chain 异步模型、凭证与 endpoint 解析）。
  - references 4-5 份先写；concepts 5-7 篇；examples 2-3 篇（CVM 调用链、hunyuan/AI 或 COS、STS 临时凭证/角色）；各级 index/log 最后写。
- **Acceptance Criteria Addressed**: AC-1, AC-7, AC-8, AC-10
- **Test Requirements**:
  - `rule` TR-14.1: 篇数达标；示例参数/类名与源码一致（含 import 路径）。
  - `rubric` TR-14.2: 教学质量；1-5；阈值 >= 4。

## Task 15: tencentcloud-sdk-python V 阶段
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 14
- **Description**: ≥15 标识符 Grep（签名函数、client 基类、模型基类、异常类、profile 字段、产品包方法名）；计数断言（产品包数、模块数）；示例代码可静态走通（import 链真实）；修复留痕。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-10
- **Test Requirements**:
  - `rule` TR-15.1: 虚构=0、计数不一致=0；示例 import/调用链零失实。

## Task 16: 分组索引与总索引连锁更新
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6, Task 9, Task 12, Task 15
- **Description**:
  - tencent/index.md：导航表新增 3 行（cubesandbox/tencentdb-agent-memory/tencentcloud-sdk-python）+ octop 简介改写为 1.0.2b5；toctree 增 3 条目；统计段（束数 10→13、概念/示例/信源/事实总数、日期、来源说明）重算；相关链接补充。
  - bundles/index.md 总索引：束计数与 tencent 分组表更新，按 check-bundles-index.py 五面口径（frontmatter/计数行/域节/分组表/toctree）。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-16.1: 分组统计数字与四束实际文件计数一致（脚本独立复算）。
  - `rule` TR-16.2: 总索引五面与目录树三角一致（gates.bundles 预检）。

## Task 17: 门禁与 Sphinx 构建收口
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 16
- **Description**:
  - 在子模块执行 `invoke gates.all`（utf8/toctrees/bundles）；失败项按归属过滤，本批次项修复至零红。
  - `invoke build`（或 sphinx dummy/HTML 定向构建全部新文件）零 error；清理构建副产物。
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-17.1: gates 全绿或他方欠债清单经核实与本批次零命中。
  - `rule` TR-17.2: 构建 0 error（本批次相关 warning 同样清零或入账说明）。

## Task 18: fresh-context 独立评审与修复闭环
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 17
- **Description**:
  - 创建 review.md，委派未参与写作的 fresh-context 只读评审（独立代理），按 AC-1~AC-11 全量检查点复核（每束 ≥15 标识符重验、计数抽验、每束抽读 2 概念+1 示例评分）。
  - 结果路由：pass 收口；fail 则将 actionable 发现物化为 Issue 入 tasks.md 队列，修复后重新发起新一轮 fresh 评审；blocked 记录环境阻塞。
  - C 阶段收口：输出变更清单（子模块新增/修改文件、主仓无变更）与原子提交建议（不执行提交）。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-8, AC-11
- **Test Requirements**:
  - `rule` TR-18.1: review.md 每个 AC 有独立证据与结论；首轮或修复轮结果 = pass。
  - `rule` TR-18.2: 每个失败检查点均对应一个已关闭 Issue；无遗留 actionable。
  - `rubric` TR-18.3: 四束内容质量评分均值 >= 4 且无单束 <= 2（AC-8 门限复核）。
