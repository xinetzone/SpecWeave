# Kylin Agent Runtime 源码 → OKF Wiki 知识包 - 实施计划

> 方法链路：阶段 0（G0 已在 Specify 完成）→ R 事实 → I 洞察 → E 分批生成 → V 独立验证 → Review。
> 束根（BUNDLE）：`projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/kylin-agent-runtime/`
> 信源快照（SRC）：`external/dao/action/openkylin/agent-runtime` @ `ee0c1709199b37ebccdc69b545f266e52e5ed6c9`

## Task 1: R 阶段 — 快照复验与分层事实采集
- **Status**: `completed`
- **Completion Evidence**:
  - hash 复验 ee0c170…（开工/V 前两次一致，工作树零改动）；spec/facts.md 落盘 150 F + 10 Q + 8 勘误（E-001~E-008）。
  - G1 推断词扫描零命中；TR-1.3 数量事实全附口径；三路事实卡（agent/gateway/外围）经主会话抽查复核。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 复验 SRC 仍在 `ee0c170`、工作树干净；记录复验输出。
  - 分层阅读：①配置/入口层（pyproject.toml、README*.md、AGENTS.md、setup-kylin-agent-runtime.sh、Dockerfile、docker-compose.yml、cli.py、run_agent.py 头部与类签名）；②核心包（agent/、kylin_agent_runtime_cli/、tools/、gateway/、acp_adapter/、cron/、plugins/、skills/、tui_gateway/、mcp_serve.py、model_tools.py、toolsets.py、toolset_distributions.py、kylin_agent_runtime_state.py）；③接口资产（web/、ui-tui/ 的 package.json/入口，locales/）。
  - 产出 `BUNDLE/spec/facts.md`：按模块分组编号 F-001…，每条 `事实 —— 证据(文件:行)`；类/函数事实记录签名与关键参数。
  - 数量类事实（模块 py 数、平台数、技能/插件目录数、locales 数、根脚本行数、工具集成员数等）一律写计数脚本，记录命令与口径（含/不含 `__init__.py`、原始匹配/去重名），与 Specify 阶段预盘对照，差异以脚本为准并写勘误注记。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: facts.md 中每条事实可经给出的 `文件:行` 在 `ee0c170` 复验；抽查 10 条全部命中。
  - `rule` TR-1.2: 事实描述段不含"用于/目的是/设计为/旨在"等推断词（Grep 零命中，推断统一归入 insights）。
  - `rule` TR-1.3: 全部数量类事实附计数口径，且脚本输出数字与文中数字逐一相符。
  - `rule` TR-1.4: 开工 hash 复验输出保存（commit 全 hash = ee0c170…）。
- **Notes**: 超大库采用分层采样，tests/ 仅读 conftest 与目录规模，不逐文件采集。

## Task 2: I 阶段 — 架构洞察与知识地图
- **Status**: `completed`
- **Completion Evidence**:
  - spec/insights.md 落盘 5 条四元组洞察（三代架构/双轨扩展/下游血缘/自进化三回路/供应链约束），证据全回指 F/Q；知识地图覆盖 10+2 文档。G2 四节齐全。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 产出 `BUNDLE/spec/insights.md`：4-5 条洞察，每条四元组（陈述/证据:引用 F-xxx/反常识/行动:对应概念文档）。
  - 必含方向：①单仓巨石入口（cli.py 1.3 万行）与包化子系统（kylin_agent_runtime_cli 等）并存的演进形态；②工具注册"导入时自注册 + 发现链"架构；③openKylin 分支相对 Hermes 上游的增量（命名/状态/时间/引导、KylinAgent 桌面协同、国产平台/模型适配）与遗留血缘（hermes 命名、~/.kylin-agent-runtime 目录、Nous Research 署名）；④自进化闭环（技能策展 curator、记忆、会话检索 FTS5）。
  - 给出 10 概念 + 2 示例的知识地图：学习路径顺序、每篇覆盖的 F-xxx 区间、跨篇链接关系。
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: 每条洞察四元组四节齐全且证据均回指已存在的 F 编号。
  - `rubric` TR-2.2: 洞察质量；scale 1-5；anchors 1=复述目录结构/无反常识，3=有洞察但差异点空泛，5=含可验证的上下游差异判断与学习路径设计；threshold >= 4；evidence=insights.md 评审记录。

## Task 3: E 批次 0 — references 信源登记（信源先行）
- **Status**: `completed`
- **Completion Evidence**:
  - references/source-code-map.md（快照元数据+文件→F 映射）与 community-sig.md（SIG 120）落盘；verify_bundle.py 校验无 file:///、无本地路径、sources 可达。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 建束目录骨架（concepts/examples/references/spec）。
  - `references/source-code-map.md`：快照元数据表（URL、全 hash、describe V0.9.4-52、pyproject 1.0.1、Python>=3.11、MIT、快照日期 2026-10-14）、关键文件→事实 ID 映射表（分类分组）、事实统计。
  - `references/community-sig.md`：SIG 120 AISubsystem 信源（名称、使命三条、邮件列表、URL、抓取日期、9 页仓库生态与不可静态翻页边界、时点数字不采信声明）。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-3.1: 两文件含 AC-1 全部要素；无本地路径/file:///。
  - `rule` TR-3.2: frontmatter 合规，sources 自指/指远程 URL。

## Task 4: E 批次 1 — 概念文档 00-04
- **Status**: `completed`
- **Completion Evidence**:
  - 00~04 共 5 篇落盘（153/143/159/138/153 行）；子代理 Grep 自验 + V 阶段 verify_symbols/verify_bundle 双通过。
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**: 生成 00-overview、01-architecture-module-map、02-agent-core-loop、03-cli-and-tui、04-tool-system（≤7 篇/批纪律）；每篇附相关 F 编号写作，代码块标语言，结尾"相关概念"，sources 指向两份 references。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 5 篇文件齐备且 frontmatter/交叉链接/分节规范符合 AC-3。
  - `rule` TR-4.2: 本篇出现的全部类名/函数名/命令在快照中 Grep 命中（随本批先自验，V 阶段总验）。

## Task 5: E 批次 2 — 概念文档 05-09
- **Status**: `completed`
- **Completion Evidence**:
  - 05~09 共 5 篇落盘（170/130/123/123/121 行）；05 篇三处行号与 AuxiliaryClient 后缀简称已在 V 前修正（E-007、V 核验）。
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 生成 05-model-providers、06-skills-and-plugins、07-memory-and-context、08-gateway-and-cron、09-acp-mcp-protocols；其中 06/07 承担与 hermes-agent 束差异化阐述的主要证据（AC-6）。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: 5 篇齐备且规范同 TR-4.1。
  - `rule` TR-5.2: API/命令 Grep 自验全部命中。
  - `rubric` TR-5.3: 上下游差异化表达；scale 1-5；anchors 同 AC-6；threshold >= 4；evidence=06/07 篇 + 评审批注。

## Task 6: E 批次 3 — 示例文档
- **Status**: `completed`
- **Completion Evidence**:
  - examples 2 篇落盘（158/148 行）；shell 命令逐条对 README.zh-CN 与 cron.py/main.py 源码字符串匹配，零臆造参数。
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 生成 examples/01-install-setup-first-run.md（uv 建环境→`kylin-agent-runtime setup`→交互/TUI/`-z`/dashboard 四种运行→测试命令，严格对齐 README 事实）、examples/02-gateway-and-cron-usage.md（systemd 用户服务命令集 + cron 定时能力，命令仅取 README 明列与 cron/ 源码可证项）。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-6.1: 所有 shell 命令在 README 或源码中可证，零臆造参数。
  - `rule` TR-6.2: frontmatter/sources/相关概念齐备。

## Task 7: E 批次 4 — 各级 index 与 log（Index 最后写）
- **Status**: `completed`
- **Completion Evidence**:
  - 3 个子目录 index（表格+toctree 收全 stem）、束根 index、log.md 落盘；五级导航（簇/类/域/总索引 + jishu）在并行会话 629/466 基线上精确 +1；check-bundles-index 五面一致（630 束）。
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 生成 concepts/index.md、examples/index.md、references/index.md（无 frontmatter，表格 + 隐藏 toctree 收全本目录 stem）。
  - 生成束根 index.md（bundle 型 frontmatter、中文标题定稿、导航表、目录结构、技术栈、与 hermes-agent 关联束区块、根 toctree 收 concepts/examples/references/spec/log）。
  - 生成 log.md（首轮条目：信源快照、F 条数、洞察条数、15 个内容文档清单、验证结论占位）。
  - 集成四级索引（本任务只改与新束相关的行/计数/toctree 条目）：ai-agent/index.md、frameworks/index.md、jishu/ai/index.md、bundles/index.md。
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-7.1: 每个 index 的 toctree stem 与磁盘文件一一对应（无多余、无遗漏）。
  - `rule` TR-7.2: 四级计数 +1 且各自内部加总自洽（ai 域六类和=总计数；总索引 total/jishu/ai 同步）。

## Task 8: V 阶段 — 独立验证与修复
- **Status**: `completed`
- **Completion Evidence**:
  - check-bundles-index rc=0（9 域/61 组/630 束五面一致）；check-utf8 rc=0（11511 文件）；check-toctrees 本束零命中零断链（97 红项全归并行 WIP：deepseek-harness/agent-self-evolution-evaluation/microsoft-mxc/wifit3/tauri，与本束无关）。
  - verify_bundle.py：87 个束内链接全可达、frontmatter 必填键齐全、零 file:///、零本地路径、子目录 index 均含 toctree。
  - recount.py（Python 独立口径，异于 R 阶段 PowerShell）：19 项数量 ALL MATCH；修正 E-008（终端环境继承树 9 类/8 叶子）。
  - verify_symbols.py：115 个类名/常量 + 40 个关键函数在快照全部命中，零虚构；E-007 三处行号已修。
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 结构：UTF-8 BOM 扫描、frontmatter 必填字段校验、束内链接可达性、交叉链接风格（无 `../`、无 file:///）。
  - API 真实性：汇总 12 篇内容文档全部类/函数/CLI/配置键/平台名，逐项对 `ee0c170` Grep，产出验证表；未命中即修复或删除。
  - 计数断言：用独立于 Task 1 的手段（换正则/解析口径）复核 facts 与文档中全部"X 个/Y 处"陈述，区分原始匹配/去重名；不一致即修并在 facts.md 留勘误、同步文档与 insights。
  - 门禁：在 awesome-okf-xs 下运行 toctree/bundles/utf8 检查（invoke 不可用时直接 `python scripts/check-toctrees.py`、`check-bundles-index.py`、`check-utf8.py`；必要时 dummy Sphinx 定向构建本束）；无关在途欠债（hermes-agent 缺文件等）过滤并列归属，不修共享 WIP。
  - 输出验证小结（嵌入 log.md 与 tasks 完成证据）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-8.1: API 验证表 100% 有结论（pass/已修复），零悬置。
  - `rule` TR-8.2: 计数复核二次口径结果与文中一致；差异全部有勘误记录。
  - `rule` TR-8.3: 本束在 toctree/utf8 门禁零失败；bundles 三角校验通过，或出具无关红项过滤清单证明本束零命中。

## Task 9: Review — fresh-context 独立评审
- **Status**: `completed`
- **Completion Evidence**:
  - R1（fresh context）= fail：2 条低危 actionable（02 篇 recovery_policy_for_tool "四元组"语义错；F-128 缺号致 150/149 不一致）+ 2 条顺手修 advisory（gateway status 归因、F-064 行号口径）。
  - 整改后 R2（另一个 fresh context）= pass：两条 actionable 与两条 advisory 独立对照源码确认到位，三脚本 rc=0 无回归；review.md 记录 R1→整改→R2 全历史，CP-R1~CP-R7 全 pass（AC-6 评 4/5）。
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 队列清空后创建 review.md，以全新上下文的独立评审者按合同复核 AC-1~AC-7（含 rubric 打分）；pass 则收尾，fail 则把每条 actionable 发现落成 pending Issue 回 Implementation 整改，整改后重新评审。
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-9.1: review.md 覆盖全部 AC 且每个 rule AC 有独立证据。
  - `rubric` TR-9.2: AC-6 维度独立复评 >= 4 并写明打分理由。
  - `rule` TR-9.3: 末次 Review result=pass。
