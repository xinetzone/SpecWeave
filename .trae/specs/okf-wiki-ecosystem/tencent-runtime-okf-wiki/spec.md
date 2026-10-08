# 腾讯运行时生态源码批次（CubeSandbox / Agent-Memory / Octop 1.0 / 云 SDK）OKF Wiki - 需求文档

## Overview

- **Summary**：以七概念方法论 R→I→E→V→C（知识沉淀场景，元编排 `seven-concepts-cmd`，执行工作流遵循 `source-code-to-okf-wiki` v1.4）全面学习本地信源 `external/dao/runtime/tencent/` 下 4 个腾讯开源仓库，在 `projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/` 产出/更新 4 个 OKF v0.2 知识包（3 个新建 + 1 个大版本增量），并连锁更新分组索引与总索引。
- **Purpose**：把腾讯在「AI Agent 运行时」方向的四类基础设施——硬件级沙箱、Agent 共享记忆服务、自托管 Agent 平台、云 API SDK——沉淀为可溯源、可验证、可复用的中文教程，补齐 tencent 分组在运行时/基础设施方向的覆盖。
- **Target Users**：使用 OKF 文档库学习腾讯 AI 运行时生态的工程师与 AI 智能体；后续做技术选型（沙箱/E2B 替代、Agent 记忆、云 API 接入）的决策者。

## Goals

- **G1 CubeSandbox 新束**：完整讲清 RustVMM/KVM 硬件隔离沙箱的组件拓扑（控制面/数据面/节点面/网络/快照/SDK）与 E2B 兼容 API。
- **G2 TencentDB-Agent-Memory 新束**：讲清 memory-core / memory-hub / proxy 三服务架构、零代码 Proxy 接入机制、四类记忆资产与 L0-L3 隔离模型。
- **G3 tencentcloud-sdk-python 新束（标准深度）**：讲清 common 包机制（TC3 签名链/客户端装配/模型基类/凭证/重试/异步）+ 代表产品包的生成代码模式与实战调用。
- **G4 Octop 增量**：按多轮增量扩展规范将既有束从 v0.9.25 推进至 v1.0.2b5，覆盖 1.0 系列新子系统与依赖更名，不重写已验证基线。
- **G5 索引与门禁**：分组 index、bundles 总索引计数对账，`invoke gates.all` 与 Sphinx 构建通过，独立评审 pass。

## Non-Goals

- 不为 **tencentmeeting-cli** 产出内容（v1.0.18 知识包已与源码同版本，2026-10-03 已交付）。
- 不修改 `external/` 下任何源码仓库（只读信源；该目录被主仓 gitignore，不升级/不切 tag，固定当前 HEAD commit 登记）。
- 不逐个文档化 tencentcloud-sdk-python 约 1900 个自动生成产品包；标准深度 = common 机制 + 代表性产品包抽样（CVM/AI 类/凭证场景）。
- CubeSandbox 采用分层采样（架构文档→组件接口与协议→核心机制关键文件），不逐行通读 3938 个跟踪文件。
- 不执行 `git commit`/`git push`（七概念 C 阶段的提交动作待用户在评审通过后单独指令；本次 C = 变更完整性收口与提交建议，不自动提交）。
- 不重写 Octop 旧束 16 个已验证文档的结论框架；只做事实性错误与版本口径定点修订。

## Background & Context

- 信源目录 `external/dao/runtime/tencent/`（主仓 gitignore 的本地克隆，2026-10-03 核实完整，非 sparse）：

| 仓库 | 用途/技术栈 | 固定版本（G0 信源门） | 跟踪文件 | 束动作 |
|---|---|---|---|---|
| CubeSandbox | AI Agent 硬件沙箱；Rust(agent/hypervisor/shim/api/cubecow/guest-init) + Go(Master/CubeOps/Cubelet) + C/Go(CubeNet) + TS(web) + 三语言 SDK | HEAD `e02976ae`（2026-09-30），最近 tag `v0.7.2` +11 commits | 3938 | 新建 `cubesandbox/` |
| TencentDB-Agent-Memory | Agent 团队共享记忆；Node/TS 三服务（MemoryCore/MemoryPanel 或 memory-hub/MemoryProxy） | HEAD `8b86874`（2026-09-29），最近 tag `v2.0.2-beta.3` +7 | 1106 | 新建 `tencentdb-agent-memory/` |
| Octop | 自托管多用户 Agent 平台；Python 3.12+（src/octop）+ React + Go desktop | tag `v1.0.2b5`（2026-09-29，HEAD 即 tag） | 3697 | 既有束增量 |
| tencentcloud-sdk-python | 云 API 3.0 自动生成 SDK；Python（common + ~1900 产品包） | tag/release `3.1.185`，commit `be50b26d4`（2026-10-02） | 1952 | 新建 `tencentcloud-sdk-python/` |
| tencentmeeting-cli | 腾讯会议 CLI v1.0.18 | 已有知识包同版本 | 281 | 不处理 |

- 既有 tencent 分组（`doc/bundles/jishu/ai/ecosystems/tencent/`）含 10 束、57 概念、16 示例、39 信源、662 事实；本次后预期 13 束。
- Octop 既有束基线：v0.9.25，133 条事实 F-001~F-133，7 concepts/3 examples/6 references，5 洞察 I-01~I-05。1.0 系列代表性变化（CHANGELOG 证实）：运行时包 `orcakit-harness-agent/harness-*` → `octop-harness/octop-gateway/octop-memory/octop-browser 1.0.0`；schema v7 → v18；布局迁入 `src/octop/`；新增 teams、connectors（企查查/OpenAlex/OAuth）、skills/experts、backend 远程存储、history、setup/TLS、i18n 体系、极验验证码、Octop↔Octop 云桥接、CLI 多项变更。
- 侦察实证（Specify 阶段抽样）：CubeSandbox `openapi.yml` 声明 CubeAPI 为 E2B-compatible、数据面前缀 `/cubeapi/v1`，`docs/zh/guide/` 文档体系真实存在（quickstart/usecases/tutorials/sdk）；Agent-Memory 端口 Core 8420/Panel 8125/Knowledge 8424/Proxy 8096，Proxy 经 `ANTHROPIC_BASE_URL=.../claude-code/<spaceId>`、`OPENAI_BASE_URL=.../codebuddy/<spaceId>` 等 base_url 路由零代码接入，MemoryCore v3 路由为 L0-L3 strict isolation；SDK 签名链在 `tencentcloud/common/abstract_client.py`（TC3 canonical request → string2sign → `Sign.sign_tc3`），异步版 `abstract_client_async.py` 走 interceptor chain，hunyuan v20230901 产品包继承 `AbstractClient`。
- Spec 产物目录：`.trae/specs/okf-wiki-ecosystem/tencent-runtime-okf-wiki/`（公开内容工作流；产出物入子模块 bundles）。

## Functional Requirements

- **FR-1（CubeSandbox 新束）**：`cubesandbox/` 含 index.md、log.md、concepts/（8-12 篇，按学习路径编号 00 起）、examples/（2-4 篇）、references/（5-7 份信源登记）、spec/facts.md + spec/insights.md。内容须覆盖：总体架构与组件拓扑、RustVMM/KVM 虚拟机生命周期（agent + hypervisor + guest-init + CubeShim）、控制面 CubeMaster 与 v0.7 拆分出的 CubeOps、节点面 Cubelet、CubeNet 网络虚拟化与出向策略/流量令牌、CubeCoW 快照与跨节点暂停恢复（S3/Volume 插件）、CubeAPI/E2B 兼容面（openapi 端点分组）、三语言 SDK、部署形态（单机/K8s/Terraform）、安全模型（凭证托管/egress 代理）。
- **FR-2（Agent-Memory 新束）**：`tencentdb-agent-memory/` 含全套 bundle 结构，concepts 5-7 篇、examples 2-3 篇、references 4-6 份、spec 两件。内容须覆盖：产品定位与三服务拓扑、Proxy 零代码协议拦截（base_url 路由、各客户端差异、responses/realtime 端点）、MemoryCore 数据面 L0-L3 isolation（v2/v3 路由）、四类资产（Chat Memory/Skills/Wiki/CodeGraph）萃取与存储（含 MongoDB experimental）、Memory Hub 面板与团队协作（API key/成员/Agent）、安装与配置（start-all.sh、两组 LLM 参数、端口表）、beta 快速演进风险标注。
- **FR-3（SDK 标准深度束）**：`tencentcloud-sdk-python/` 含全套 bundle 结构，concepts 5-7 篇、examples 2-3 篇、references 4-5 份、spec 两件。concepts 覆盖：包生态与安装（common+分产品包/全产品包）、TC3-HMAC-SHA256 签名链、客户端装配（ClientProfile/HttpProfile/凭证链）、AbstractModel 序列化与产品包生成模式、错误模型与重试（含异步 interceptor chain）、同步/异步双版本。examples 至少覆盖：CVM 典型调用链、一个 AI 产品包（hunyuan）或 COS 对象存储、STS 临时凭证/角色场景。
- **FR-4（Octop 多轮增量）**：在既有 `octop/` 束内——新增 references 信源登记（v1.0.2b5，commit `e473dd3c`，注明新信源路径 external/dao/runtime/tencent/Octop 与旧信源路径差异）；facts.md 续号（F-134 起）；concepts 续编号（07 起）覆盖 1.0 新子系统（teams/connectors/skills-experts/backend/history/setup-tls/i18n 等中择要成篇）；examples 续编号；对旧 16 个文档做定点版本修订（外部包名、schema、路径、计数等事实性口径）；index.md 表格+toctree 追加、log.md 顶部追加 v2 条目；旧文件不重命名、不重排。
- **FR-5（索引连锁）**：更新 tencent 分组 `index.md`（10→13 束：导航表行、toctree 条目、统计段数字与日期、相关链接）；更新 `doc/bundles/index.md` 总索引（束计数 248→251 及五面对账所涉字段，以 gate 实际口径为准）。
- **FR-6（验证收口）**：每束完成 V 阶段（结构/frontmatter/链接/Grep API 真实性/计数断言）；`invoke gates.all`（或 dummy 定向构建 + 针对性 gates）本批次相关项全绿；Sphinx HTML 构建 0 error；产出独立评审所需证据。

## Non-Functional Requirements

- **NFR-1 事实可溯源（G1）**：每条编号事实附信源文件路径（相对仓库根）与关键行号/符号；事实句零推断词（"用于/目的是/设计为"等移入 insights）；区分"代码证实 / 文档声称 / 推断"三级。
- **NFR-2 零虚构（G4）**：文档引用的每个关键类名/函数/命令/端点/表名须能在固定 commit 的源码中 Grep 命中；代码示例与事实表一致。
- **NFR-3 计数准确**：所有"N 个模块/命令/端点/端口/服务"类陈述经 Glob/Grep 或脚本独立计数后落字，口径与对象一致。
- **NFR-4 OKF v0.2 合规**：frontmatter 必填字段完整（type/title/description/tags/generated/verified/status/stale_after/sources）；中文正文、英文 kebab-case 文件名；每个 index.md 含 `{toctree}` 块且与人类可读导航并存；bundle-relative 链接；相对路径引用、禁 file:///。
- **NFR-5 信源稳定（G0）**：references 登记远程仓库 URL + tag/commit hash + 获取日期；正文不出现主仓 gitignore 的易失绝对路径作为可引用信源（路径仅作事实溯源文本，以 commit 锚定）。
- **NFR-6 批次卫生**：不修复与本批次无关的在途门禁欠债；如全量 gates 被他方 WIP 拖红，过滤确认本束零命中后在评审中说明归属。
- **NFR-7 规模自律**：单批生成 ≤ 7 文件；CubeSandbox/SDK 坚持分层采样，事实与文档体量服从信息密度而非凑数。

## Constraints

- **Technical**：产出位置在 git 子模块 `projects/awesome-okf-xs/`（分支内开发，add/commit 分离、显式列文件；本次不执行提交）；质量门 `invoke gates.toctrees|gates.bundles|gates.utf8|gates.all` 与 `invoke build`（Python/invoke 环境，按子项目 README 执行）；多语言源码只读分析（Rust/Go/C/TS/Python）。
- **Business**：全部为公开开源项目（Apache-2.0/MIT），按公开内容工作流入 bundles；beta 项目（Agent-Memory、Octop b 版）须在文档与 stale_after 上体现时效风险。
- **Dependencies**：本地 external 克隆保持当前 HEAD；awesome-okf-xs 子模块工作区可写且无未处理冲突；Sphinx/invoke 工具链可用（不可用则改 dummy 构建并记录为评审 blocked 项）。
- **方法论**：seven-concepts-cmd 场景 4（知识沉淀 R→I→E，V 强制，C 收口不提交）；执行纪律遵循 source-code-to-okf-wiki v1.4（§6.5 多轮增量、反模式 1-13）。

## Assumptions

- 4 个外部仓库当前 HEAD 在任务期间不变（本地克隆无人切换）；如变动，以实际 commit 重新登记并回扫事实。
- tencent 分组是 CubeSandbox 等运行时设施的正确归属（同组已有 ai-infra-guard、ncnn 等基础设施束，且用户指定"对应位置"）。
- 子模块沿用当前工作分支（上次交付的 feat 分支）；若工作树存在他方未提交变更，实施前过滤隔离，不混入本批次。
- SDK 产品包抽样选择 CVM + hunyuan（AI）+ 凭证场景；COS 若在仓则纳入，否则以 AI 类产品替代（R 阶段核实后定）。

## Acceptance Criteria

### AC-1: 四个知识包交付物结构完整
- **Type**: `rule`
- **Given**: 实施完成后 bundles/jishu/ai/ecosystems/tencent/ 目录
- **When**: 检查 cubesandbox、tencentdb-agent-memory、tencentcloud-sdk-python 三个新束与 octop 增量
- **Then**: 三新束均含 index.md/log.md/concepts/index.md/examples/index.md/references/index.md/spec/facts.md/spec/insights.md 且概念/示例/信源篇数在 FR 规定区间；octop 束新文件续编号、旧文件无重命名
- **Pass Condition**: 目录与文件清单逐项核对一致
- **Evidence**: 目录树清单 + 各束 index.md

### AC-2: 编号事实满足零推断与全覆盖
- **Type**: `rule`
- **Given**: 四束 spec/facts.md
- **When**: 审查事实条目
- **Then**: 每条事实有 ID、源码路径（锚定 commit）、无因果推断词；CubeSandbox 覆盖 FR-1 全部主题面、其余束覆盖各自 FR 主题面；octop 新事实自 F-134 续号
- **Pass Condition**: 抽查 20 条/束均可回溯到指定文件符号，G1 词表扫描零命中
- **Evidence**: facts.md + Grep 扫描结果

### AC-3: 零虚构 API（Grep 级独立验证）
- **Type**: `rule`
- **Given**: 全部新内容文档与 octop 修订点
- **When**: 由 fresh context 复核者对每束至少 15 个关键标识符（类/函数/命令/端点/端口/表名）在固定 commit 源码中检索
- **Then**: 命中或文档已标注为"文档声称未在代码证实"；不存在凭空编造的 API
- **Pass Condition**: 每束虚构关键标识符 = 0
- **Evidence**: review.md 中 V 验证记录表（标识符→命中位置）

### AC-4: 数量陈述经独立计数断言
- **Type**: `rule`
- **Given**: 文档中所有"N 个/N 篇/N 条"类陈述
- **When**: 用 Glob/Grep/脚本独立复核
- **Then**: 数字与计数结果一致；束自身统计（概念/示例/信源/事实数）与文件系统一致
- **Pass Condition**: 不一致项 = 0（或已修正并留痕）
- **Evidence**: 计数命令与结果摘录入 review.md

### AC-5: 索引连锁与门禁通过
- **Type**: `rule`
- **Given**: 分组 index.md 与 bundles/index.md 更新完成
- **When**: 运行 `invoke gates.toctrees`、`invoke gates.bundles`、`invoke gates.utf8`
- **Then**: 本批次相关检查全绿（他方在途欠债需过滤列示且本束零命中）；总索引束/组/域计数与目录树三角一致
- **Pass Condition**: gates 通过证据齐全；新束全部可达、无孤立文档
- **Evidence**: gates 命令输出

### AC-6: Sphinx 构建零错误
- **Type**: `rule`
- **When**: 运行 `invoke build`（或 sphinx dummy/HTML 定向构建）
- **Then**: 0 error；新页面可导航
- **Pass Condition**: 构建日志无 error/warning 中属于本批次的项
- **Evidence**: 构建输出尾部摘要

### AC-7: 信源稳定性登记合规
- **Type**: `rule`
- **Given**: 每束 references/ 信源登记
- **When**: 核对 frontmatter sources 与信源文件
- **Then**: 四个仓库均记录远程 URL + tag/commit hash（CubeSandbox e02976ae / Octop v1.0.2b5=e473dd3c / Agent-Memory 8b86874 / SDK be50b26d4=3.1.185）+ 获取日期；无 file:/// 临时路径引用
- **Pass Condition**: 逐束核对 8 项登记要素齐全
- **Evidence**: references 文件清单

### AC-8: 内容教学质量
- **Type**: `rubric`
- **Dimension**: 知识包的学习路径合理性、架构洞察深度、示例可操作性
- **Scale**: 1-5
- **Anchors**: 1 = 事实堆砌、无路径设计、示例无法运行；3 = 结构完整但部分篇章停留在翻译 README、洞察平淡；5 = 概念按依赖递进、含反常识机制洞察（如 60ms/5MB 的实现代价、Proxy 拦截协议面、签名链设计动机）、示例可照做并覆盖易错点
- **Pass Threshold**: >= 4（四束各自评分，均值 >= 4 且无单束 <= 2）
- **Evidence**: 独立评审抽读每束 2 篇概念 + 1 篇示例的评分记录

### AC-9: Octop 增量纪律
- **Type**: `rule`
- **Given**: octop 束变更集
- **When**: git diff 审查
- **Then**: 新文档编号续接（07+/04+/07+）、事实续号、新增信源登记、log 追加；旧 16 文档的改动仅限事实性/版本口径修订且每条可指认；无旧文件改名/删除
- **Pass Condition**: diff 分类表与修订理由逐条对应
- **Evidence**: octop 束 git diff --stat 与修订点台账

### AC-10: frontmatter 与 OKF 格式合规
- **Type**: `rule`
- **When**: 扫描全部新文件
- **Then**: 必填字段齐全且日期/枚举合法；子目录 index 无 frontmatter；toctree 块与目录内容一致；无 `../` 交叉链接、无 file:///
- **Pass Condition**: 违例项 = 0
- **Evidence**: gates.toctrees + 人工抽查表

### AC-11: fresh-context 独立评审通过
- **Type**: `rule`
- **Given**: 全部任务完成
- **When**: 未参与写作的独立评审方按 review.md 检查点复核
- **Then**: 每个 AC 有独立证据，评审结果 pass；actionable  finding 全部闭环
- **Pass Condition**: Review R1（或修复后 RN）结果 = pass
- **Evidence**: review.md Review History

## Open Questions

- [ ] SDK 代表产品包最终抽样：CVM 确定；COS 是否在仓、AI 包取 hunyuan 还是其他，R 阶段按在仓事实定（不阻塞审批）。
- [ ] Octop 新子系统成篇数量（4-6 篇）依 R 阶段变化面事实量最终确定（区间已在 FR-4 限定）。
- [ ] 子模块工作分支沿用 feat/zhen-xu-qiu-reading-bundle 还是另开分支——Plan 阶段核实工作树状态后在 tasks.md 记录，不影响内容交付。
