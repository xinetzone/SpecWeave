---
name: jupyter-okf-wiki-group-spec
version: 1.0.0
created: 2026-08-22
source: Jupyter ecosystem source code analysis (external/libs/jupyter/)
methodology: seven-concepts knowledge-sedimentation (R→I→E→V→C) per bundle
okf_version: "0.2"
scope: 67 bundles under projects/awesome-okf-xs/bundles/jupyter/
---

# Jupyter 分组 OKF Wiki 全量系统化处理 - 产品需求文档

## Overview
- **Summary**: 对 `projects/awesome-okf-xs/bundles/jupyter/` 分组下全部 67 个子 bundle 执行系统化知识沉淀，按 R→I→E→V→C 五阶段链路补全/验证 facts.md（事实清单）和 insights.md（架构洞察），确保所有 bundle 达到 OKF v0.2 质量标准。
- **Purpose**: Jupyter 生态是交互式计算的事实标准，现有 67 个 bundle 中有 51 个缺少 R/I 阶段核心文档，2 个部分完成，需全量补齐并做 V 阶段独立验证，形成可离线查阅的源码级中文知识体系。
- **Target Users**: Python/前端开发者、数据科学家、Jupyter 扩展开发者、SpecWeave 知识库用户、需要深入理解 Jupyter 架构的工程师。

## Problem Statement
Jupyter 分组已建立 index.md 骨架并按架构层次（协议层/格式层/服务层/应用层/部署层/自动化层等）组织了 67 个子 bundle，但多数 bundle 仅有内容文档（concepts/examples/references）而缺少 R 阶段（facts.md 零推测事实清单）和 I 阶段（insights.md 架构洞察文档）。缺乏 facts/insights 导致：(1) 文档溯源不可验证，无法 Grep 离线核对；(2) 缺少架构洞察，学习路径断层；(3) 与已完成 bundle（cockle、binderhub 等 14 个）质量不一致。

## Goals
- **G1**: 为全部 67 个子 bundle 补全/验证 facts.md（R 阶段：零推测事实清单，每条事实可 Grep 到源码）
- **G2**: 为全部 67 个子 bundle 补全/验证 insights.md（I 阶段：架构分层、核心数据流、设计决策、关键模式洞察）
- **G3**: 对已有内容的 14 个已完成 bundle 执行 V 阶段独立验证（抽样核对 facts 与源码一致性，修正偏差）
- **G4**: 对 2 个部分完成 bundle 补齐缺失阶段
- **G5**: 确保所有 bundle 的 index.md frontmatter 包含 sources 字段且本地源码路径正确
- **G6**: 所有事实声明可通过 Grep 在本地源码目录验证，实现离线可审计

## Non-Goals (Out of Scope)
- 不重写已有的 concepts/examples/references 内容文档（仅做链接有效性检查和必要修正）
- 不逐行翻译官方英文文档
- 不深度覆盖 Jupyter 生态外的周边项目（如 Voilà、Panel 等可视化框架）
- 不为 Jupyter 各项目贡献代码或修复 bug
- 不重构 bundle 的目录结构或重新分类架构层次

## Background & Context

### Bundle 现状（截至 2026-08-22）
通过 PowerShell 脚本分析，67 个 bundle 状态如下：

| 状态 | 数量 | 说明 |
|------|------|------|
| ✅ 已完成 | 14 | 含 index.md + 内容文档 + facts.md + insights.md |
| ⚠️ 部分完成 | 2 | 有内容文档但 facts/insights 缺失其一 |
| ❌ 待补全 R/I | 51 | 有 index.md 和内容文档，缺少 facts.md 和 insights.md |

### 架构层次（按 jupyter/index.md 组织）
1. **协议层**：jupyter-client（内核通信协议）、jupyter-core（路径/配置规范）
2. **格式层**：nbformat（.ipynb 格式规范）
3. **服务层**：jupyter_server、jupyter_server_fileid、jupyter-server-terminals、jupyverse、fps、enterprise-gateway
4. **应用层**：jupyterlab、jupyterlab_server、jupyter-notebook、jupyterhub、the-littlest-jupyterhub、binderhub、jupyterlite、jupyverse
5. **前端 UI**：lumino、jupyterlab 扩展体系、jupyter-renderers、ui-profiler
6. **扩展/模板**：extension-cookiecutter、extension-template、extension-examples、plugin-playground
7. **内核**：ipython、echo-kernel、javascript-kernel、p5-kernel、pyodide-kernel、xeus、xeus-lite-demo
8. **工具链**：nbconvert、nbviewer、papyri、jupyter_releaser、jupyterlab-translate、language-packs、pytest-jupyter
9. **扩展项目**：jupyterlab-git、jupyterlab-github、jupyterlab-latex、jupyterlab-webrtc-docprovider、jupyter-resource-usage、jupyter-scheduler、jupyter-collaboration、jupyter-ai、jupyter-chat、jupyterlite-ai、jupyterlite-lsp、jupyterlite-sphinx、litegitpuller、repo2jupyterlite
10. **部署/运维**：jupyter-docker-stacks、cookiecutter-docker-stacks、jupyterlab-desktop、try-jupyter、jupyterlab-demo、jupyterlite-demo、sphinx-demo
11. **治理/团队**：governance、team-compass、frontends-team-compass、jupyter（元仓库）、jupyterlab-probot、pr-triage-board-bot、surveys
12. **终端**：terminal、cockle

### 源码本地路径
Jupyter 生态源码克隆目标目录为 `d:\spaces\SpecWeave\external\libs\jupyter\`，按 bundle 名称组织（已有部分源码如 binderhub、cockle、fps、ai、jupyterlab、lumino、xeus、nbconvert、nbformat、nbviewer、notebook、terminal、papyri 等）。

### 参考规范
- OKF v0.2 规范：`d:\spaces\SpecWeave\projects\awesome-okf-xs\.agents\rules\frontmatter.md`
- 已完成 bundle 参考模板：`bundles/jupyter/cockle/`（facts.md 334 条零推测事实 + insights.md 架构洞察）
- 方法论：seven-concepts 知识沉淀场景，source-code-to-okf-wiki 技能的 R→I→E→V→C 五阶段链路

## Functional Requirements

### R 阶段：事实采集（Retrospective/Read）— facts.md
对每个 bundle：
- **FR-1**: facts.md 文件位于 bundle 根目录，与 index.md 同级
- **FR-2**: facts.md 包含 YAML frontmatter，字段至少包含：type: Facts、okf_version: "0.2"、bundle_name、source（本地源码路径 + GitHub URL）、generated、verified
- **FR-3**: 事实条目数量按项目规模分级：核心项目（jupyter_server/jupyterlab/jupyterhub/ipython/nbconvert 等）≥200 条；重要项目（50-200 条）；小型工具/模板/治理类（≥30 条）
- **FR-4**: 每条事实格式：`- [事实编号] [文件/模块路径]:[行号范围] — 事实描述`，可通过 Grep 直接定位源码验证
- **FR-5**: 事实分类组织：项目元信息→目录结构→核心模块/类→关键函数/API→配置系统→扩展机制→数据结构→依赖关系→构建系统
- **FR-6**: 零推测原则：所有事实必须可在本地源码中 Grep 验证，禁止编造函数名、参数、行为
- **FR-7**: 源码路径使用本地相对路径：`../../../../../external/libs/jupyter/<bundle-name>/`，与 binderhub 已有格式保持一致

### I 阶段：架构洞察（Insight）— insights.md
对每个 bundle：
- **FR-8**: insights.md 文件位于 bundle 根目录，与 facts.md 同级
- **FR-9**: insights.md 包含 YAML frontmatter，字段至少包含：type: Insights、okf_version: "0.2"、bundle_name、source、generated、verified
- **FR-10**: 洞察章节（按需裁剪，核心项目全包含，小型项目可合并）：
  1. 架构定位（在 Jupyter 生态中的位置与职责）
  2. 分层架构图（Mermaid 或文字描述核心层次）
  3. 核心数据流（请求/消息/数据在组件间的流转路径）
  4. 关键设计决策（为什么这么设计，trade-off 分析）
  5. 扩展机制（插件/钩子/entry_points 等扩展点）
  6. 与兄弟项目的协作关系（依赖/被依赖关系）
  7. 核心模式提炼（可复用的架构/代码模式）
  8. 潜在改进点/已知限制
- **FR-11**: 所有洞察必须基于 facts.md 中的事实推导，洞察中引用的事实编号需回指 facts.md
- **FR-12**: 使用 Mermaid 图表描述架构关系（若适用），遵循 `.agents/commands/mermaid-cmd` 规范

### V 阶段：独立验证（Verification）
对所有 bundle（含已完成的 14 个）：
- **FR-13**: 对 facts.md 执行抽样验证：随机抽取 10% 事实条目（至少 10 条）在源码中 Grep 核对，修正不准确的事实
- **FR-14**: 检查 index.md frontmatter 的 sources 字段是否正确指向本地源码路径
- **FR-15**: 检查 bundle 内部交叉链接有效性（concepts/examples/references 中的链接目标存在）
- **FR-16**: 验证 facts.md 和 insights.md 的 frontmatter 格式合规（OKF v0.2）
- **FR-17**: 验证记录写入每个 bundle 的 log.md（追加 V 阶段验证条目）

### 源码准备
- **FR-18**: 将缺失的 Jupyter 生态源码仓库克隆到 `external/libs/jupyter/<bundle-name>/` 目录
- **FR-19**: 已有源码的 bundle（如 binderhub、cockle 等）执行 git pull 更新到最新稳定版
- **FR-20**: 源码克隆/更新记录写入 references/sources-register.md

### 分批执行策略
- **FR-21**: 按架构层次和学习路径顺序分批处理，每批 5-8 个 bundle
- **FR-22**: 批次顺序：协议层→格式层→服务层核心→应用层核心→前端 UI→内核→工具链→扩展项目→部署运维→治理/团队→终端/特殊
- **FR-23**: 每批完成后执行验证检查，通过后进入下一批

## Non-Functional Requirements
- **NFR-1**: 所有正文为中文，技术术语保留英文并附首次中文解释
- **NFR-2**: 所有文件符合 OKF v0.2 frontmatter 规范
- **NFR-3**: 文件命名使用 kebab-case（facts.md、insights.md 为固定文件名，不使用 kebab-case）
- **NFR-4**: 事实描述准确、简洁，避免冗余，每条事实一个原子知识点
- **NFR-5**: insights.md 洞察有深度，不停留在表面描述，要分析"为什么"
- **NFR-6**: 源码路径引用统一格式，与 bundle 根目录相对路径计算正确
- **NFR-7**: Mermaid 图表语法正确，可在 IDE/渲染器中正常显示
- **NFR-8**: 整个处理过程分批增量执行，支持断点续做，每批完成有明确进度记录

## Constraints
- **Technical**: 所有事实必须基于本地源码 Grep 验证，离线可审计；源码克隆使用公开 GitHub 仓库
- **Format**: 严格遵循 OKF v0.2 规范（frontmatter.md）和 seven-concepts R→I→E→V→C 链路
- **Path**: 产出物存放于 `projects/awesome-okf-xs/bundles/jupyter/<bundle-name>/`；源码存放于 `external/libs/jupyter/<bundle-name>/`
- **Methodology**: 使用 source-code-to-okf-wiki 技能的工作流，seven-concepts-cmd 编排知识沉淀场景
- **Language**: 正文中文，文件名英文，代码/API/路径保留原文
- **Scope**: 不修改已有的 concepts/examples/references 内容，仅补全 facts.md/insights.md 和验证修正

## Assumptions
- 读者具备基本 Python/JavaScript 编程能力和 Jupyter 使用经验
- `external/libs/jupyter/` 目录可写入，网络可访问 GitHub 进行源码克隆
- 已完成的 14 个 bundle（cockle、binderhub 等）可作为质量基准模板
- 部分小型/治理类 bundle（governance、team-compass、surveys 等）源码内容较少，facts.md 条目数可适当降低但不低于 30 条

## Acceptance Criteria

### AC-1: 全量覆盖（rule）
- **Given**: jupyter/ 分组下 67 个子 bundle
- **When**: 检查每个 bundle 根目录
- **Then**: 每个 bundle 均存在 facts.md 和 insights.md，且 frontmatter 合规（type 字段正确、sources 字段指向本地源码路径）
- **Evidence**: 全量文件列表 + frontmatter 校验脚本输出

### AC-2: 事实可验证（rubric）
- **Given**: 所有 bundle 的 facts.md
- **When**: 每个 bundle 随机抽取 10% 事实条目（至少 10 条）在源码中 Grep 验证
- **Then**: 准确率 ≥95%（即抽样中 ≤5% 的事实无法在源码中定位或描述不准确）
- **Scale**: 0-2（2=≥98%准确；1=90-97%准确；0=<90%）
- **Threshold**: ≥1
- **Evidence**: Grep 验证记录 + 修正日志

### AC-3: 洞察有深度（rubric）
- **Given**: 所有 bundle 的 insights.md
- **When**: 独立审查者阅读评估
- **Then**: 核心项目（前 3 层）insights 包含架构分层、数据流、设计决策分析；非核心项目至少包含架构定位和核心模式提炼；洞察基于事实推导而非空泛描述
- **Scale**: 0-2（2=核心项目全章节覆盖且有独到洞察；1=基本覆盖但部分分析较浅；0=大量缺失或空泛）
- **Threshold**: ≥1
- **Evidence**: 独立审查评估记录

### AC-4: 源码路径正确（rule）
- **Given**: facts.md 和 index.md 中的 sources 路径
- **When**: 检查本地路径是否存在
- **Then**: 所有引用的本地源码目录存在且包含对应项目文件
- **Evidence**: 路径存在性检查脚本输出

### AC-5: 已完成 bundle 验证通过（rule）
- **Given**: 已标记为完成的 14 个 bundle（cockle、binderhub 等）
- **When**: 执行 V 阶段验证
- **Then**: 无 P0 级事实错误；如有偏差已修正；log.md 有验证记录
- **Evidence**: 验证记录 + 修正 diff

### AC-6: 交叉链接有效（rule）
- **Given**: facts.md 和 insights.md 中的内部链接
- **When**: 检查链接目标文件
- **Then**: 内部链接目标文件存在；回指 facts.md 的事实编号引用有效
- **Evidence**: 链接有效性检查

### AC-7: 分批进度可追溯（rule）
- **Given**: 处理过程记录
- **When**: 查看进度文档
- **Then**: 有清晰的批次划分、每批完成状态、验证结果记录；支持断点续做
- **Evidence**: 进度追踪文档（log.md 或 progress.md）

## Open Questions
- 无（任务范围明确，源码仓库公开可获取）
