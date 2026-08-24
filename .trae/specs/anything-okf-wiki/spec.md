---
spec_version: "1.0"
created: 2026-08-23
source: "external/libs/ai/Anything"
target: "projects/awesome-okf-xs/bundles"
methodology: "source-code-to-okf-wiki (R→I→E→V→C) + seven-concepts-cmd (知识沉淀场景)"
---

# Anything 子项目 OKF Wiki 生成规格

## 问题陈述

`external/libs/ai/Anything/` 目录下包含两个独立的开源子项目，需要系统化学习其源码并生成符合 OKF v0.2 规范的中文 Wiki 教程，放置于 `projects/awesome-okf-xs/bundles/` 的恰当位置：

1. **CLI-Anything**（HKUDS）：AI Agent 软件控制框架——通过7阶段管线自动为任意软件生成 Agent 可用的 CLI 接口，包含 CLI-Hub 包管理器、60+ 软件 Harness、SKILL.md 技能系统、多平台插件适配
2. **anywidget**（Manz et al.）：Jupyter 自定义 Widget 工具包——基于 ESM 模块的轻量级 Jupyter Widget 开发框架，支持 HMR、多前端框架桥接（React/Svelte/Vue）、Vite 集成

## 用户与目标

- **用户**：需要理解 CLI-Anything 框架架构与 anywidget 核心机制的开发者
- **目标**：通过源码深度阅读，产出可溯源、API 经 Grep 验证的结构化中文教程

## 非目标

- 不覆盖 CLI-Anything 中 60+ 个具体软件 Harness（gimp/blender/inkscape 等）的详细文档——这些是框架生成的实例产物，遵循统一模板，核心架构在框架层已覆盖
- 不覆盖 anywidget 的 Astro 文档站点（`docs/`）前端代码
- 不覆盖 anywidget JS 包中除核心类型定义外的框架桥接实现细节（react/svelte/vue/signals 包作为 references 信源登记即可）
- 不执行 C 阶段（模式沉淀入库）——本任务聚焦于 Wiki 生成，模式萃取视情况作为可选项

## 需求

### 功能需求

1. **R 阶段（事实采集）**：对两个子项目分别进行源码深度阅读，提取编号事实清单（F-xxx），零推测
2. **I 阶段（架构洞察）**：提炼 3-5 个核心架构洞察（陈述+证据+反常识+行动四元组），设计知识地图
3. **E 阶段（批量生成）**：按 OKF v0.2 规范生成文档，遵循信源先行、分批生成（≤7文件/批）、Index 最后写原则
4. **V 阶段（独立验证）**：结构检查 + Frontmatter 检查 + 链接检查 + Grep 级 API 真实性验证
5. **Bundle 放置**：
   - `cli-anything` → `bundles/ai-agent/cli-anything/`（AI Agent 工具框架，归属 ai-agent 分组）
   - `anywidget` → `bundles/jupyter/anywidget/`（Jupyter Widget 库，归属 jupyter 分组）
6. **分组索引更新**：更新 `bundles/ai-agent/index.md` 和 `bundles/jupyter/index.md` 以包含新 bundle
7. **总索引更新**：更新 `bundles/index.md` 的统计数字、分组导航、生态关系图

### 非功能需求

1. **文档语言**：中文撰写，英文技术术语首次出现时括号注释
2. **代码示例**：Python 代码块标注 `python`，JS/TS 标注 `javascript`/`typescript`，API 调用必须与 facts.md 事实一致
3. **交叉引用**：使用 `/` 开头的 bundle-relative 路径
4. **Frontmatter**：所有非保留 .md 文件包含 type 字段 + 推荐字段（title/description/tags/generated/verified/status/stale_after/sources）
5. **保留文件**：index.md 仅 bundle 根带 okf_version frontmatter，子目录 index.md 无 frontmatter；log.md 记录变更

## 约束与假设

### 约束

- 遵循 source-code-to-okf-wiki 技能的五阶段工作流（R→I→E→V→C），C 阶段可选
- 遵循 seven-concepts-cmd 的知识沉淀场景链路（R→I→E）
- 遵循 OKF v0.2 规范（frontmatter、目录结构、交叉引用）
- 遵循 awesome-okf-xs 项目规范（中文、kebab-case 文件名、相对路径引用）
- 不修改 vendor 子模块源码（external/ 下为外部依赖镜像）
- 产出文件位于 `projects/awesome-okf-xs/bundles/` 下

### 假设

- CLI-Anything 的核心源码集中在 `cli-anything-plugin/`（框架方法论）、`cli-hub/cli_hub/`（包管理器）、`skill_generation/`（测试辅助）；60+ Harness 目录为框架产出物，不作为核心学习对象
- anywidget 的核心源码集中在 `anywidget/anywidget/`（Python 包），JS 包（`packages/`）作为信源参考但不作为概念文档主体
- 两个项目规模适中（核心 Python 代码均 < 2000 行），适合单 bundle 覆盖

## 验收标准

### Rule 类型（二元验证）

| ID | 验收条件 | 验证方式 |
|----|---------|---------|
| R1 | cli-anything bundle 目录结构完整（index.md + log.md + concepts/ + examples/ + references/ + spec/facts.md + spec/insights.md） | 文件系统检查 |
| R2 | anywidget bundle 目录结构完整（同上） | 文件系统检查 |
| R3 | 所有非保留 .md 文件包含可解析的 YAML frontmatter 且含非空 type 字段 | frontmatter 解析检查 |
| R4 | 所有 concepts/ 和 examples/ 文档的 sources 字段指向存在的 references/ 文件 | 链接检查 |
| R5 | 文档中引用的关键类名/方法名/函数名在源码中可通过 Grep 验证存在 | Grep 验证（每 bundle 抽检 ≥15 个 API） |
| R6 | bundle 根 index.md 包含 okf_version: "0.2" | 内容检查 |
| R7 | 子目录 index.md（concepts/index.md, examples/index.md, references/index.md）不含 frontmatter | 内容检查 |
| R8 | 交叉链接使用 `/` 开头的 bundle-relative 路径，无 `../` 相对路径 | 正则检查 |
| R9 | 代码块标注语言标识 | 正则检查 |
| R10 | ai-agent/index.md 和 jupyter/index.md 已更新包含新 bundle 条目 | 内容检查 |
| R11 | bundles/index.md 统计数字、分组表、详情表已更新 | 内容检查 |
| R12 | 无虚构 API——V 阶段 Grep 验证发现的虚构 API 数量为 0 | Grep 验证报告 |
| R13 | facts.md 中无推断性表述（"用于"/"目的是"/"设计为"等），仅记录可验证事实 | 内容审查 |

### Rubric 类型（评分评估）

| ID | 维度 | 评分标尺 | 通过阈值 |
|----|------|---------|---------|
| B1 | 概念文档质量 | 0=事实错误多/结构混乱；1=基本准确但缺乏深度；2=结构清晰/概念解释透彻/示例恰当 | ≥1.5 |
| B2 | API 覆盖度 | 0=核心 API 大量遗漏；1=主要 API 覆盖但边缘缺失；2=核心+重要扩展 API 全覆盖 | ≥1.5 |
| B3 | 知识地图合理性 | 0=学习路径混乱；1=路径基本合理但有跳跃；2=学习路径循序渐进/概念间依赖清晰 | ≥1.5 |
| B4 | 文档间一致性 | 0=术语/命名不一致；1=基本一致偶有偏差；2=术语统一/交叉引用准确 | ≥1.5 |

## 开放问题

1. CLI-Anything 是否需要覆盖 cli-hub-matrix（5个领域矩阵：3d-cad/game-development/image-design/knowledge-research/video-creation）？——建议仅在 references 中作为信源登记，不单独出概念文档，因为矩阵是元数据配置而非核心代码
2. anywidget 的 JS 包（types/vite/react/svelte/vue/signals）需要覆盖到什么深度？——建议 types 包作为核心信源（类型定义），其余桥接包在 references 中登记即可
3. 是否需要更新 bundles/index.md 的生态关系图？——需要，但保持简洁，不引入复杂的 Mermaid 图变更
