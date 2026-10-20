---
status: "draft"
id: "create-sst-okf-wiki-tutorial-spec"
title: "SST 基础设施即代码框架 OKF Wiki 教程"
source: "seven-concepts knowledge-scenario: anomalyco/sst v4.17.2 source + https://sst.dev/docs/"
date: "2026-10-20"
methodology: "seven-concepts R→I→E→V→C"
content-sensitivity: "public"
tags: ["SST", "IaC", "Pulumi", "Cloudflare", "AWS", "OKF", "Wiki教程"]
---

# SST 基础设施即代码框架 OKF Wiki 教程

## Overview
- **Summary**: 基于 SST 固定源码快照和 SST 官方文档，创建一套中文 OKF Wiki 教程，讲清 SST 的应用模型、部署与开发工作流、主要运行时和资源链接机制，以及 Go CLI、TypeScript 平台组件和 provider 桥接之间的实现关系。
- **Purpose**: 为开发者提供可循证、可复查的 SST 学习路径，避免把官方文档的当前行为误写成固定源码版本的实现事实。
- **Target Users**: 使用或评估 SST 的应用开发者、平台工程师及需要理解其架构的开源项目读者。

## Goals
- 以 `R→I→E→V→C` 完成来源预检、事实采集、架构洞察、教程生成、独立验证与闭环。
- 将知识包放在 `projects/awesome-okf-xs/doc/bundles/jishu/iac/sst/`；为 SST 新建 `jishu/iac/` 分组，定位为基础设施即代码与云应用部署框架。
- 以 SST v4.17.2 对应的不可变源码提交为源码事实基线；将官网文档标注为 2026-10-20 采集的现行说明，两类来源不得混同。
- 解释核心架构及其端到端关系，提供可依来源核验的学习示例和操作路径。
- 将新 bundle、分组及计数完整接入 OKF 导航。

## Non-Goals
- 不逐项讲解 SST 所支持的所有 AWS、Cloudflare 或第三方 provider 资源/API。
- 不将官网当前版本的行为推定为 v4.17.2 的源码行为；来源无法确认的差异须显式标为未验证或版本差异。
- 不修改 SST 上游源码，不注册/移动/改写本地 SST checkout，也不引入新的 vendor/submodule。
- 不在本任务中执行真实云账号部署、创建云资源或验证收费服务。
- 不自动创建 Git commit。

## Background & Context
- SST checkout 位于 `external/dao/anomalyco/sst`，当前工作树干净，HEAD 为 tag `v4.17.2`、commit `e49ac31411f63ab4ed0d802b7e15d95f6b827e47`，远程仓库为 `github.com/anomalyco/sst`。
- 该 checkout 不是 SpecWeave 登记的 git submodule；永久文档须用固定 commit 的 GitHub 链接作为源码坐标，不得引用本机绝对路径或临时提取文件。
- 已读取 SST 官方文档主页及 Basics、Components、Providers、Linking、CLI、SDK、Live、Console、Monorepo 等页面。官网页面可能随时间更新，需在 references 中记录 URL 和采集日期。
- 初步源码地图包含 `cmd/sst/`、`cmd/sst/mosaic/`、`pkg/project/`、`pkg/server/`、`pkg/runtime/`、`pkg/bus/`、`sdk/js/` 与 `platform/`；R 阶段需逐项验证实际职责及模块间调用关系。
- 既有 `jishu/cloud` 专门收录云厂商开放 API SDK；`jishu/build` 收录构建与包管理工具链；`jishu/dev` 收录开发工具和开源协作；`jishu/systems` 的现有内容聚焦操作系统与运行环境。SST 横跨 IaC、云应用组件和部署/开发工作流，放入这些分组会模糊其边界，因此新增 `jishu/iac`。
- `awesome-okf-xs` 当前工作树干净；总索引计数门禁与 toctree 导航门禁基线均通过：9 域 / 62 组 / 651 束。

## Functional Requirements
- **FR-1**: 在 `jishu/iac/sst/` 创建 OKF v0.2 bundle，正文使用中文，文件名使用英文 kebab-case。
- **FR-2**: 按事实采集和架构洞察结果生成概念、示例、来源登记及各级索引；主题至少覆盖：
  - SST 定位、`sst.config.ts`、应用/阶段/stack/state 的关系；
  - `sst dev`、部署、差异查看及 CLI 到项目/部署流程的主路径；
  - Go CLI、项目模型、provider/server 桥接、语言运行时与平台组件之间的职责边界；
  - 代表性 AWS/Cloudflare 组件、Pulumi/provider 扩展面和组件/底层资源关系；
  - JavaScript SDK 的资源链接，以及 Live/Mosaic 开发体验和相关运行时机制；
  - 官方文档中的快速开始、组件、provider、link、CLI 和部署/阶段使用方式。
- **FR-3**: 每个技术性断言可追溯到编号事实或官方文档来源；代码/API 示例须在固定源码或注明日期的官方文档中核验。
- **FR-4**: 在 `references/` 先登记固定源码坐标与官方文档来源，再生成引用这些信源的概念和示例文档。
- **FR-5**: 生成至少三个示例，分别讲解最小应用/组件部署、资源链接，以及本地开发到部署的关键工作流；若示例不能在本任务环境实跑，须标明验证边界。
- **FR-6**: 新建 `jishu/iac/index.md`，并更新 `jishu/index.md` 与 `doc/bundles/index.md` 的说明、导航和计数。
- **FR-7**: bundle 根及所有子目录索引均以 `{toctree}` 覆盖全部内容；SST bundle 根 index 收录概念、示例、参考和日志导航。
- **FR-8**: 在 log 中记录来源版本、采集时间、范围、生成批次及验证结果。

## Non-Functional Requirements
- **NFR-1**: frontmatter 遵循 awesome-okf-xs 的 OKF v0.2 规范；来源信息必须足以定位外部材料。
- **NFR-2**: 源码链接使用 `https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/...` 等固定提交坐标；禁止 `file:///`、本机绝对路径和临时目录路径。
- **NFR-3**: 官网资料标注采集日期；若其说法与 v4.17.2 源码不能相互印证，必须并列说明，不得静默合并。
- **NFR-4**: 每批新增正文不超过 7 个文件；references 先行，所有内容完成后再统一编写/更新索引。
- **NFR-5**: 关键数字须注明统计口径，并以脚本或官方索引独立复核；不以人工枚举作为唯一依据。
- **NFR-6**: 示例中的命令、类型、组件名、参数和数据流均不得依惯例推测。

## Constraints
- **Technical**: 最终教程仅使用 Markdown 与 YAML frontmatter，兼容 awesome-okf-xs 的 Sphinx/MyST 和 OKF v0.2 约定。
- **Repository**: 变更落在 `projects/awesome-okf-xs` 子项目内，遵循其 `AGENTS.md`、frontmatter 规范和 Invoke 质量门。
- **Sources**: 源码事实固定于 tag `v4.17.2` / commit `e49ac31411f63ab4ed0d802b7e15d95f6b827e47`；官网说明注明采集日期 `2026-10-20`。
- **Approval**: `spec.md` 与 `tasks.md` 获得用户明确批准前，不创建或修改 bundle、父级索引及知识文档。

## Assumptions
- SST 作为跨云 IaC 与云应用部署框架，在技术域下拥有独立 `iac` 分组，比扩展现有 SDK、构建或系统运行环境分组更清晰。
- “全面学习”指覆盖核心架构、端到端生命周期和主要扩展机制，不代表逐一解释每个组件参数或 150+ 外部 provider 的 API。
- 官方文档未声明与 v4.17.2 对齐时，以可验证的源码事实为版本实现依据，并将官网文档仅作为有日期的产品说明。
- 用户批准本规格与任务清单即授权按目标路径创建教程及必要的导航/计数更新；提交仍需单独明确指令。

## Acceptance Criteria

### AC-1: 来源版本可追溯且边界清晰
- **Type**: `rule`
- **Given**: 教程包含源码与官网文档两类来源
- **When**: 检查 references 和相关 frontmatter
- **Then**: 源码来源固定记录 tag、完整 commit hash、仓库 URL；官网来源记录具体页面 URL 和 2026-10-20 采集日期，且不把两者混作同一版本事实
- **Pass Condition**: 所有源码声明可回溯到固定提交链接；无本机绝对路径、`file:///` 或临时路径
- **Evidence**: references、frontmatter、全 bundle 路径扫描

### AC-2: 核心学习范围有事实映射
- **Type**: `rule`
- **Given**: R 阶段完成源码事实清单与官网页面采集
- **When**: 对照 FR-2 的主题清单检查 concepts/examples
- **Then**: 每个主题均有对应 F 编号或官方来源；关键模块关系有明确证据，未经核验的职责不作为事实陈述
- **Pass Condition**: FR-2 每一条主题均在覆盖矩阵中映射到文档与来源
- **Evidence**: facts、insights、教程与覆盖矩阵

### AC-3: 教程学习路径具备教学连贯性
- **Type**: `rubric`
- **Dimension**: 新读者能否从产品模型逐步理解源码架构并完成基本工作流
- **Scale**: 1-5
- **Anchors**: 1 = 章节割裂、关键概念无定义或无可执行路径；3 = 主要主题齐全但依赖关系或源码到用法的连接不稳定；5 = 先修关系清晰，配置/部署/组件/运行时/资源链接之间由证据串联，示例能支撑读者复述端到端流程
- **Pass Threshold**: >= 4
- **Evidence**: 独立审读学习路径、章节依赖、示例与交叉链接

### AC-4: OKF bundle 与导航完整
- **Type**: `rule`
- **Given**: bundle 和新增 `iac` 分组创建完成
- **When**: 运行项目导航质量门
- **Then**: 所有 Markdown 内容有合规 frontmatter；bundle 根与子目录索引的 `{toctree}` 覆盖全部内容，父级导航可从文档根到达 SST bundle
- **Pass Condition**: `python scripts/check-toctrees.py` 通过，bundle 文件无孤立内容
- **Evidence**: 索引文件、脚本输出

### AC-5: 分组注册与总索引计数一致
- **Type**: `rule`
- **Given**: 新建一个技术域分组和一个 bundle
- **When**: 更新 `jishu/index.md` 与 `doc/bundles/index.md`
- **Then**: 新分组有导航表和 toctree 入口，技术域说明同步为 19 组；总索引的 bundle/group/domain 计数以目录树为准
- **Pass Condition**: `python scripts/check-bundles-index.py` 通过；技术域从 481 束 / 18 组增至 482 束 / 19 组；全库从 651 束 / 62 组 / 9 域增至 652 束 / 63 组 / 9 域，且均与目录树机械计数一致
- **Evidence**: 两级索引与计数门禁输出

### AC-6: 技术符号与示例经过独立核验
- **Type**: `rule`
- **Given**: 文档包含 SST 命令、组件名、TypeScript/Go 符号或 API 示例
- **When**: 使用不同于初次采集的核验方式复查
- **Then**: 正向引用在固定源码或对应官网页面中存在；涉及负向结论时也执行源码搜索；示例不把推测伪装成可运行代码
- **Pass Condition**: 所有关键符号及示例均有验证记录，未解决项已降级为明确标注的范围限制
- **Evidence**: V 阶段逐符号核验清单与命令输出

### AC-7: 文档构建和项目质量门通过
- **Type**: `rule`
- **Given**: bundle 与索引变更完成
- **When**: 运行 UTF-8、toctree、总索引及文档构建检查
- **Then**: 所有新增内容可构建，质量门无新增失败
- **Pass Condition**: `invoke gates.all` 与 `invoke build` 成功；如发现非本次变更导致的既有失败，须区分并证明本束相关检查通过
- **Evidence**: 命令输出和最终 git diff/status

### AC-8: 范围及版本限制没有被夸大
- **Type**: `rule`
- **Given**: 教程总结 SST 能力和覆盖范围
- **When**: 检查概述、组件/provider 章节和结论
- **Then**: 明确本教程覆盖代表性组件与主要机制，不宣称穷尽全部组件/provider；官网与 v4.17.2 的差异和未实测部署边界得到说明
- **Pass Condition**: 全文无未限定的“全部 API/所有组件均已覆盖”声明
- **Evidence**: 搜索范围断言并人工复核相关章节

## Open Questions
- 当前无待决问题；分组选择、来源版本边界及“全面学习”的范围已在本规格中明确，用户可在批准时提出调整。
