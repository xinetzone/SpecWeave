# Kylin Agent Runtime 源码 → OKF Wiki 知识包 - 需求规格

## Overview

- **Summary**：以七概念方法论场景 4（知识沉淀 R→I→E，经 source-code-to-okf-wiki 工作流具体化并加 V 对抗审查）全面学习 openKylin `agent-runtime` 源码仓（包名 `kylin-agent-runtime`，Hermes Agent 的 openKylin 下游自进化分支），在 awesome-okf-xs 知识包库的 `jishu/ai/frameworks/ai-agent/` 簇下新建 `kylin-agent-runtime` OKF v0.2 知识包。
- **Purpose**：为中文读者提供一份事实可溯源、API 零虚构、导航完整的麒麟 OS Agent 运行时源码教程；与既有 `hermes-agent` 束形成"上游框架 ↔ openKylin 下游演进"的对照知识链。
- **Target Users**：希望理解 openKylin 麒麟 OS Agent 架构（核心循环/CLI/工具体系/多模型 Provider/技能自进化/记忆上下文/消息网关/ACP·MCP 协议）的 AI 应用开发者与架构学习者。

## Goals

- 对固定快照（commit `ee0c170`）完成 R 阶段编号事实采集，数量类事实一律脚本计数并标注口径。
- 产出 10 篇概念文档 + 2 篇示例文档 + 2 份信源登记 + 束内 spec（facts/insights），全部中文、kebab-case 文件名、OKF v0.2 frontmatter。
- 束接入既有四级导航（ai-agent 簇 → frameworks 类 → ai 域 → bundles 总索引），计数与 toctree 一致。
- 经过独立 V 阶段（Grep 级 API 存在性验证、计数断言复核、链接/frontmatter/toctree 检查）与 fresh-context 独立评审。

## Non-Goals

- 不修改、不重构 `external/dao/action/openkylin/agent-runtime` 源码仓任何文件（只读信源）。
- 不重写、不重排既有 `hermes-agent` 束及其它任何在途束（其 toctree 引用缺失属并行会话欠债，仅记录归属，不代为修复）。
- 不做 git commit/push（除非用户后续明确授权；子模块提交需另行确认）。
- 不翻译整个代码库、不生成 API 参考大全；以架构理解与学习路径为边界。
- 不硬引用 SIG 页面的动态时点数字（PR/Issues/Commits/贡献排名随时变化）。

## Background & Context

- **信源 1（源码，主信源）**：`d:\spaces\SpecWeave\external\dao\action\openkylin\agent-runtime`
  - remote：`https://gitee.com/openkylin/agent-runtime.git`；工作树干净
  - HEAD：`ee0c1709199b37ebccdc69b545f266e52e5ed6c9`（2026-10-13 16:39 +0800，master）
  - `git describe`：`V0.9.4-52-gee0c170`（最近 tag V0.9.4 之后 52 提交；HEAD 无精确 release tag，故固定 commit hash）
  - `pyproject.toml`：name=`kylin-agent-runtime`，version=`1.0.1`，requires-python `>=3.11`，MIT，authors Nous Research；setuptools 后端 + 全依赖精确钉版
  - README.zh-CN 自述："基于 Hermes 改进的自进化智能体运行时"；仓内 AGENTS.md 标题仍为 "Hermes Agent - Development Guide"，核心文件保留 hermes 命名（血缘证据）
  - G0 分类：`external/` 为 gitignored env-bound 信源（GATE-SPS 警告级，非 temporary 阻断级）；文档中不出现该本地路径与 file:/// 链接，sources 指向远程 URL + 束内 references
- **信源 2（社区，补充信源）**：openKylin 官方 SIG 120 = **AISubsystem SIG**（抓取于 2026-10-14）
  - URL：`https://www.openkylin.top/sig/sig_detail.html?sig_id=120`
  - 使命三条：①AI 子系统软件包规划/维护/升级；②管理本地与云端大模型、屏蔽框架差异、提供 AI 基础能力与场景 SDK；③打造麒麟 OS Agent
  - 邮件列表：`aisubsystem@lists.openkylin.top`；仓库列表 9 页（JS 分页，静态无法翻页），首屏 10 仓库为 kylin-ai-engine/kylin-ai-sdk/kylin-ai-runtime 等引擎生态，未见 agent-runtime——references 如实记录，不臆测登记页
- **模块规模脚本盘点（口径：`Get-ChildItem -Recurse -Filter *.py`，R 阶段须以独立手段复核）**：agent/ 120、plugins/ 118、tests/ 1199、tools/ 93、kylin_agent_runtime_cli/ 94、gateway/ 64（platforms/ 32 个平台文件，不含 `__init__.py`）、optional-skills/ 48、skills/ 33（25 个子目录）、scripts/ 14、acp_adapter/ 10、tui_gateway/ 8、cron/ 4；locales/ 16 个 YAML；根脚本 18 个（cli.py 13108 行、run_agent.py 3810、kylin_agent_runtime_state.py 3692、model_tools.py 849、toolsets.py 771、mcp_serve.py 745 等）；另有 web/（Web 控制台）、ui-tui/（Ink/React 终端 UI）、acp_adapter/、providers/、nix/、Dockerfile/docker-compose.yml
- **目标位置（落盘前三查结论）**：
  - 同类比肩：`frameworks/ai-agent/hermes-agent/` 束已存在（本项目即其 openKylin 下游），故新束置于同簇最具可发现性
  - 范本：以结构完整的 `nanobot` 束为格式范本（hermes-agent 束当前 toctree 引用 30+ 个磁盘不存在文件，属在途 WIP，不可作范本）
  - 束根：`projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/kylin-agent-runtime/`
- **方法论**：seven-concepts-cmd 场景 4（R→I→E）+ source-code-to-okf-wiki 五阶段（阶段 0 + R→I→E→V→C）；本轮不涉及 C 阶段模式入库（工作流模式已存在，仅在 log/总结中记录复用情况）

## Functional Requirements

- **FR-1（信源登记先行）**：先生成 `references/source-code-map.md`（固定 commit、目录与关键文件→事实 ID 映射）与 `references/community-sig.md`（SIG 信源），全部内容文档的 `sources` 指向这两份登记。
- **FR-2（事实层）**：`spec/facts.md` 按模块分组编号 F-xxx，每条含 `文件:行` 证据；禁用"用于/目的是/设计为"类推断词；数量类事实附计数脚本口径与原始匹配/去重名区分。
- **FR-3（洞察层）**：`spec/insights.md` 产出 4-5 条四元组洞察（陈述/证据/反常识/行动），含与 hermes-agent 上游的差异化演进判断。
- **FR-4（概念文档 10 篇）**：
  - `00-overview` 定位、自进化闭环、Hermes 血缘与版本事实
  - `01-architecture-module-map` 模块地图、文件依赖链、技术栈
  - `02-agent-core-loop` AIAgent 对话循环、工具调用迭代、预算/重试/上下文
  - `03-cli-and-tui` cli.py/CLI 子命令包、setup、dashboard、ui-tui/tui_gateway
  - `04-tool-system` 工具自动发现注册、toolsets 分组、environments、computer_use
  - `05-model-providers` transports 多模型适配、凭证池、模型元数据、懒安装
  - `06-skills-and-plugins` skills/optional-skills、curator、插件体系
  - `07-memory-and-context` SessionDB(FTS5)、记忆插件、上下文引擎/压缩、embeddings
  - `08-gateway-and-cron` 多平台网关（32 平台文件）、投递/配对、cron 调度
  - `09-acp-mcp-protocols` acp_adapter、mcp_serve、LSP 子系统概览
- **FR-5（示例文档 2 篇）**：`01-install-setup-first-run`（uv 安装/setup/三种运行/dashboard，源自 README）、`02-gateway-and-cron-usage`（systemd 网关服务 + 定时任务，源自 README 与 cron/ 源码）。
- **FR-6（导航集成）**：束根/子目录 index 全部含隐藏 `{toctree}`；新增束登记到 ai-agent 簇 index、frameworks index、ai 域 index、bundles 总索引四级（表格 + toctree + 计数同步）。
- **FR-7（变更日志）**：`log.md` 记录首轮创建：信源快照、事实/洞察数量、文档清单与验证结论。

## Non-Functional Requirements

- **NFR-1 真实性**：文档引用的每个类名/函数名/CLI 命令/配置键必须在 `ee0c170` 快照中 Grep 可证存在；代码示例与源码签名一致。
- **NFR-2 可复现**：凭 references 中的 URL + commit hash + 获取日期可重新获得同一快照。
- **NFR-3 规范一致**：遵循 OKF v0.2（frontmatter 必填字段、`/` 开头 bundle-relative 交叉链接、子目录 index 无 frontmatter、toctree 与表格并存）。
- **NFR-4 语言风格**：正文中文，英文术语首次出现加括号注释；`##` 分节；每篇含"相关概念"。
- **NFR-5 规模纪律**：E 阶段单批生成 ≤ 7 篇；Index/总索引最后写。
- **NFR-6 编码**：所有新文件 UTF-8 无 BOM（满足 gates.utf8）。

## Constraints

- **Technical**：Windows + PowerShell 7 环境；awesome-okf-xs 质量门 `invoke gates.toctrees / gates.bundles / gates.utf8`（需在子项目目录、可能缺 invoke 环境，备用直接 `python scripts/check-toctrees.py` 等与 dummy Sphinx 构建）；不得用 heredoc 式提交。
- **Business**：产出物位于 git submodule `projects/awesome-okf-xs` 内——用户已明确指定该路径（写入授权）；不主动提交。
- **Dependencies**：只读依赖本地源码快照与公开 SIG 页；无需联网安装依赖。
- **Scope**：超大代码库（仅 tests 即 1199 个 py）采用分层采样：架构文档/根入口 → 核心包接口 → 按需深入，不追求逐行覆盖。

## Assumptions

- `external/dao/action/openkylin/agent-runtime` 工作树在任务期间保持 `ee0c170` 不切换（开工前与 V 阶段各核一次 hash）。
- awesome-okf-xs 子模块当前已有与本束无关的门禁欠债（如 hermes-agent 束 toctree 缺文件、各级计数 234/238 不一致）；本任务只保证本束零命中并同步本束引起的计数增量，既有无关红项在评审报告中列归属、不扩大修改面。
- SIG 页动态数据仅作背景，不进入数量断言。

## Acceptance Criteria

### AC-1: 信源固定与溯源完整
- **Type**: `rule`
- **Given**: 两份 references 已生成
- **When**: 检查其内容
- **Then**: 均记录远程 URL；源码信源含 commit `ee0c170…` 全 hash、分支/describe（V0.9.4-52）、pyproject 版本 1.0.1、抓取固定日期；SIG 信源含 URL、抓取日期 2026-10-14 与"9 页静态不可翻页"边界说明；全束无 `external/` 本地路径与 `file:///` 链接
- **Pass Condition**: 上述要素逐项可在文件中指出；Grep 全束 `file:///|external/dao` 零命中
- **Evidence**: references 两文件 + Grep 命令输出

### AC-2: 事实层零推断且数量经脚本计数
- **Type**: `rule`
- **Given**: spec/facts.md 完成
- **When**: 抽查任意 5 条事实与全部数量类事实
- **Then**: 每条事实有 `路径:行` 证据且无推断词；每个数量陈述附计数口径（命令/正则/原始匹配 vs 去重名），R 脚本计数与 V 阶段独立复核一致；勘误留审计行
- **Pass Condition**: 推断词扫描零命中（事实段）；数量事实 100% 有口径注记且两次计数一致
- **Evidence**: facts.md、计数脚本输出记录

### AC-3: 束结构与 OKF 规范完整
- **Type**: `rule`
- **Given**: E 阶段完成
- **When**: 检查束目录
- **Then**: index/log + concepts(10)/examples(2)/references(2)/spec(facts,insights) 齐备；每个 index.md 含 `{toctree}` 且收录本目录全部内容文档；内容文档 frontmatter 字段完整（type/title/description/tags/generated/verified/status/stale_after/sources）；交叉链接为 `/` 束内绝对路径；UTF-8 无 BOM
- **Pass Condition**: 结构清单逐项存在；check-toctrees 对本束零错误；utf8 检查零错误
- **Evidence**: 目录清单、门禁输出

### AC-4: API/命令零虚构
- **Type**: `rule`
- **Given**: V 阶段验证
- **When**: 对全部 12 篇内容文档提取引用的类名/函数名/CLI/配置键
- **Then**: 逐项在 `ee0c170` 快照中 Grep 命中（白名单：README 明列命令与通用标准库）；代码示例签名与源码一致；不命中项已修复或删除并记录
- **Pass Condition**: 验证清单中项项 pass，零遗留未解释未命中
- **Evidence**: V 阶段 Grep 验证表

### AC-5: 四级导航计数一致
- **Type**: `rule`
- **Given**: 索引更新完成
- **When**: 运行计数对账门禁
- **Then**: ai-agent 簇束数 55→56、frameworks 83→84（描述同步）、ai 域六类加总与总计数同步 +1、bundles 总索引 628→629 且 jishu 465→466；四处 toctree 均收录新束；本束引起的计数增量全部对账一致
- **Pass Condition**: `check-bundles-index.py` 对总索引三角校验通过；若被无关在途项拖红，须出具过滤清单证明本束零命中
- **Evidence**: 四级索引 diff、门禁输出（含必要的过滤说明）

### AC-6: 教程质量与上下游差异化
- **Type**: `rubric`
- **Dimension**: 内容质量（学习路径连贯性、洞察深度、与 hermes-agent 束的差异化、中文可读性）
- **Scale**: 1-5
- **Anchors**: 1 = 事实堆砌/复制 hermes 束/无学习路径；3 = 结构完整但差异点泛泛、读者需自行拼图；5 = 路径清晰、洞察四元组扎实、明确讲清 openKylin 分支相对上游的增量与遗留血缘
- **Pass Threshold**: >= 4
- **Evidence**: insights.md + 概念文档 00/01/06/07 + 独立评审批注

### AC-7: 独立评审通过
- **Type**: `rule`
- **Given**: 实现队列清空
- **When**: fresh-context 独立评审按评审合同执行
- **Then**: review.md 全部检查点 pass，每个 AC 有独立证据，无未处理 actionable finding
- **Pass Condition**: 最近一次 Review 结果 = pass（fail 则整改后重新评审）
- **Evidence**: review.md

## Open Questions

- [x] 束安放位置 → 已定：`jishu/ai/frameworks/ai-agent/kylin-agent-runtime/`（与 hermes-agent 同簇）
- [x] SIG 页是否纳入 → 纳入为第二信源（社区归属背景），动态数字不引用
- [ ] 首篇概念定稿时确认对外束名中文标题（候选："Kylin Agent Runtime 麒麟智能体运行时"）——E 阶段批次 1 落定，不阻塞审批
