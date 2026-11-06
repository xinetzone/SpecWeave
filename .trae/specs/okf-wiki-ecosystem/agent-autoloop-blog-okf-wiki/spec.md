---
status: "completed"
id: "agent-autoloop-blog-okf-wiki-spec"
title: "Agent-Autoloop 开源博文 → OKF 知识包"
source: "微信公众号「数字生命卡兹克」《开源我这折腾了1年的「Agent自动化系统」，愿所有人都能感受Agent的魅力。》(2026-11-04)；权威源 GitHub KKKKhazix/agent-autoloop README.md / INSTALL.md"
date: "2026-11-06"
methodology: "seven-concepts knowledge scenario: R→I→E→V→C（叠加 blog-article-to-okf-wiki 七阶段）"
content-sensitivity: "public"
tags: ["Agent-Autoloop", "Agent编排", "事件溯源", "插件架构", "Prompt注入", "OKF Wiki"]
---

# Agent-Autoloop 开源博文 → OKF 知识包

## 内容敏感度预检（步骤 1 / 步骤 2.3）

- URL：`https://mp.weixin.qq.com/s/T9_acg247gxzUNL4j5zrCw`（微信公众号公开短链，无 `code=`/`token=`/邀请码等访问控制参数，公开域名）
- 内容主题：开源项目发布公告与架构说明，不含个人隐私、商业秘密、内部会议或付费培训材料
- 判定：**公开内容（Public）** → 标准工作流
- Spec 目录：`.trae/specs/okf-wiki-ecosystem/agent-autoloop-blog-okf-wiki/`
- 产出物：`projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/agent-autoloop/`
- 版权路线：产出为**原创教程 + 事实转述 + 短语级引用**，不逐字转录博文全文；所有具体声明挂 F 编号并标注信源。源材料是有文本层的公开网页（非扫描版版权书籍），不触发「扫描版材料 route 决策前置」附加条款，但沿用「摘要替代转录」的原创改写原则。

## Overview

- **Summary**：把卡兹克 2026-11-04 的 Agent-Autoloop 开源公告转化为可溯源的 OKF v0.2 中文知识包，主线是「确定性内核 + 万物皆插件」的架构、五步事件驱动流程、内核四机制（挂起零消耗 / 事件溯源 / 指令数据分离 / 跳数熔断）、四类插件与可复现的上手路径。
- **Purpose**：给希望理解「如何让命令行 Agent 在后台自主跑长流程、只在需要人拍板时才打扰人」的读者，提供一条从博文到官方仓库、再到可照做配置的复核路径；同时把博文口径与官方口径的差异显式留存。
- **Target Users**：AI Agent 框架/运行时工程师、做个人自动化与 Agent Ops 的开发者、关注事件溯源与 Prompt 注入防护的读者。

## Goals

- 在 `jishu/ai/frameworks/ai-agent/` 新建独立 bundle `agent-autoloop`；与同组 `deepseek-harness*`、`pi-agent-harness`、`pi-cli`（博文明确提到的两个设计来源）形成可交叉引用的主题簇。
- 按 R→I→E→V 完成 F 编号事实采集（68 条）、P0 官方核验（10 大项）、三层知识拆分、信源先行的 bundle 生成与四视角对抗审查。
- 同步更新 `jishu/ai/frameworks/ai-agent/index.md`、`jishu/ai/frameworks/index.md`、`jishu/ai/index.md`、`jishu/index.md` 与 `doc/bundles/index.md` 的导航与计数，使新 bundle 由文档根可达。
- 保留 C 阶段交付核对；用户未要求提交，不创建 Git commit。

## Non-Goals

- 不实际安装或运行 Agent-Autoloop（本机为 Windows，官方 Windows 版待定，见 F-045）；examples 均为官方文档可复核的配置与命令示例，标注「未在本机实测」。
- 不逐字转录博文全文，不复制官方 README 全文。
- 不把作者自述的公司虚实中台成效数字（F-042）或作者自测性能数字（F-014）表述为独立验证结论。
- 不新建顶级技术域或分组；不改动同组其他 bundle 既有内容。
- 不创建 Git commit，除非用户另行明确要求。

## Background & Context

- **信源 A**：微信公众号「数字生命卡兹克」，作者卡兹克，2026-11-04 08:19 上海发布，标注原创。
- **信源 B**：`github.com/KKKKhazix/agent-autoloop` 的 `README.md` / `INSTALL.md`（`main`，取于 2026-11-06），项目作者即博文作者，属开源项目官方一手发布。
- **归属依据**：`ai-agent` 分组导语明确「本组也容纳官方文档驱动的架构学习包；资讯转化采用 R→I→E→V 核验」，且分组内已有 `siemens-industrial-agent`、`qwen-ui-agent` 等博文转化先例，以及 `deepseek-harness` / `pi-agent-harness` 两个设计来源 bundle 可作交叉引用。
- **执行约束**：`awesome-okf-xs` 是 git submodule，按子项目 AGENTS.md 与 `.agents/rules/frontmatter.md` 执行；开工前已确认子模块与主仓工作树干净，目标 bundle 与 spec 目录均不存在（幂等检查通过）。
- **方法论叠加**：用户以 `/七概念` 触发 → 场景识别为「知识沉淀」（R→I→E→V→入库），G1/G2/G3/V 门由 `seven-concepts` 提供；博文→bundle 的七阶段判据由 `blog-article-to-okf-wiki` Skill（L1）与其 L2 模式文档提供，两者链路一致，不重复执行。

## 归属位置分析（步骤 3）

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/frameworks/ai-agent/agent-autoloop/` | ✅ 选定 | ① 主线实体是 Agent-Autoloop 这一 Agent 编排运行时/中台；② 分组导语已声明容纳「官方文档驱动的架构学习包」与 R→I→E→V 资讯转化束；③ 分组内有 `siemens-industrial-agent`、`qwen-ui-agent` 等非源码转化先例，以及 `deepseek-harness`、`pi-agent-harness`、`pi-cli` 可作设计来源互链 |
| `jishu/ai/ecosystems/deepseek-harness/` | ❌ | 该组以 DeepSeek Harness 生态为中心，博文主线不是 DSH，仅借鉴其架构理念 |
| `jishu/ai/practice/` | ❌ | 该组为工程方法论、上下文工程、行业趋势研究；本包是具体开源框架的结构化教程 |
| `jishu/ai/products/` | ❌ | 该组为面向终端任务的 AI 产品；Autoloop 是编排中台而非任务型产品 |
| `jishu/ai/learning/` | ❌ | 该组为体系化学习路径；本包是单一项目知识包 |
| 新建顶级分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更原则 |

## Functional Requirements

- **FR-1 事实集**：`facts.md` 以连续 F 编号登记博文事实与官方补充事实，剥离因果词（G1），分离客观事实 / 作者观点 / 作者自述。
- **FR-2 P0 核验**：数字、平台支持、机制可靠性边界、Agent 支持范围等关键声明逐项对照官方 README/INSTALL，按勘误四张清单登记差异；核验失败项不静默照搬。
- **FR-3 骨架判定**：以「操作可复现性两问」决定 `examples/` 取舍，结论在 spec 与 bundle 索引双重留痕。
- **FR-4 三层知识拆分**：发布与架构事实层 → concepts 首篇；机制原理层 → concepts 中部；插件生态与上手实践层 → concepts 尾篇 + examples；作者观点与自述单列不与事实混同。
- **FR-5 OKF 结构**：按 OKF v0.2 生成 `index.md`、`log.md`、`concepts/`、`examples/`、`references/`；非保留 `.md` 含可解析 YAML frontmatter（唯一必填 `type`，本项目治理要求补全 `sources` 等）；各级 index 含隐藏 `{toctree}`。
- **FR-6 导航登记**：挂入分组 index 及必要上级导航；按磁盘现值 +1 更新计数，不凭记忆写数字。
- **FR-7 门禁**：运行可用的 `invoke gates.*`；依赖不可用时执行手动等效验证清单并在 `log.md` 注明，禁止声称「gates 通过」。

## Non-Functional Requirements

- **NFR-1**：事实 / 作者观点 / 执行者洞察三层分离。
- **NFR-2**：具体声明（数字、命令、产品名、组件名）全部挂 F 编号，无 facts.md 之外的新增断言；推导与示意配置显著标注「非官方」或「未在本机实测」。
- **NFR-3**：中文撰写，文件名 kebab-case 纯英文；首次出现的英文术语给出中文解释。
- **NFR-4**：bundle 内链接一律用**相对路径**（同目录直连、跨层 `../`、跨 bundle `../../<bundle>/index.md`）；禁止 `/` 开头的 bundle-relative 绝对路径与 `file:///`。该条在 V 阶段依门禁实测修正：原「bundle-relative `/` 路径」写法会触发 V-5「绝对路径残留」拦截，且与同组既有 bundle 的相对链接惯例不符。
- **NFR-5**：时效性显式声明——`stale_after` 前复核 Windows 版进度（issue #17）、版本号、性能数字与插件支持范围。
- **NFR-6**：敏感信息零残留；不写入本机绝对路径或用户目录绝对路径（统一 `~/`）。

## Constraints

- **Technical**：以官方 README/INSTALL 为一手事实基准；博文口径仅在差异对照时出现，不混入正文结论。
- **Repository**：只写 `jishu/ai/frameworks/ai-agent/agent-autoloop/`、相关索引行与本级 spec 目录。
- **Documentation**：遵循 `projects/awesome-okf-xs/.agents/rules/frontmatter.md` 与该子项目 toctree / bundle gates。
- **Workflow**：spec 三件套（spec.md + tasks.md + review.md）+ facts.md + insights.md 同步落地；用户未要求提交时不建 commit。

## Acceptance Criteria

### AC-1：归属与结构（rule）
- **Given** 交付完成
- **When** 检查目标目录
- **Then** `agent-autoloop/` 含 `index.md`、`log.md`、三个子目录，且 `examples/` 存在并有实际内容（骨架两问皆是）

### AC-2：可溯源（rule）
- **Given** 任一 concepts/examples 文档
- **When** 抽取其中数字、命令与产品名
- **Then** 每条可映射到 F 编号，且 `facts.md` 与 `references/article-source.md` 的编号集合完全相等、连续无跳号

### AC-3：勘误落实（rule）
- **Given** `verification.md` 中登记的 ⚠️ 项
- **When** 检查正文
- **Then** 呈现的是官方口径（如派活 p99 1.82 ms、内核约 1650 行、Windows 待定、整机断电未单独测过），并标注博文原口径

### AC-4：导航可达（rule）
- **Given** 文档根 `doc/index.md`
- **When** 沿 toctree 做 BFS
- **Then** 新 bundle 的全部内容文档可达，无孤立文档与断链

### AC-5：计数一致（rule）
- **Given** 各级索引
- **When** 核对 frontmatter、正文、导航表与 toctree 条目
- **Then** 组束数 / 域束数 / `total_bundles` 三处与目录树实际计数一致

### AC-6：质量门留痕（rubric）
- **Given** `review.md` 与 `log.md`
- **When** 检查方法论留痕
- **Then** G1/G2/G3 通过记录、V 阶段 ≥5 条具体审查意见且 ≥2 条被采纳修正、门禁实际执行结果（含环境依赖说明）均可查

## 完成情况（2026-11-06）

| AC | 结果 | 证据 |
|----|------|------|
| AC-1 归属与结构 | ✅ | `agent-autoloop/` 14 个 md：根 index + log + 3 子目录 index + concepts 4 + examples 3 + references 2；骨架两问皆是，`examples/` 有实际内容 |
| AC-2 可溯源 | ✅ | 双份 F 编号 `facts.md` / `references/article-source.md` / 期望集合均为 68 条且连续无跳号；bundle 正文引用 0 越界；14 文件 0 断链、0 绝对路径残留 |
| AC-3 勘误落实 | ✅ | 正文采用官方口径：p99 1.82 ms、约 1650 行（含空行注释）、Windows 待定、强杀不丢但整机断电未单独测过、支持范围三档、`deliver-review` 单源；博文原口径仅在对照表出现 |
| AC-4 导航可达 | ✅ | `check-toctrees.py <bundle>` 通过，全部内容文档可达；根 index 与 `ai-agent/index.md` toctree 均已接入 |
| AC-5 计数一致 | ✅ | `check-bundles-index.py` 全绿：9 域 / 64 组 / 713 束，五面一致；README 与 doc 首页规模数字同步 |
| AC-6 质量门留痕 | ✅ | `review.md` 9 条意见 / 8 条采纳；`log.md` 记录门禁执行结果、`invoke` 依赖缺失与资产门禁剩余项；G1/G2/G3 见 `insights.md` |

- **质量门**：G1 ✅（facts.md 声明列无因果词）、G2 ✅（5 条洞察四元组完整）、G3 ✅（洞察 5 给出跨任务迁移场景）、G4 ✅（21 项任务单一职责可独立验证）、V 门 ✅（9 条 / 采纳 8 条）。
- **工具链限制**：`invoke` 因 `invocations` 包元数据缺失不可用，改跑 5 个官方 `scripts/check-*.py` 等效验证；未声称 invoke gates 通过。
- **交付状态**：未创建 Git commit、未 push；`awesome-okf-xs` 为第一方 git submodule，需单独提交。
