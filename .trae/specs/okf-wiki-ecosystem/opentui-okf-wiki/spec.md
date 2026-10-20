---
status: "draft"
id: "opentui-okf-wiki-spec"
title: "OpenTUI 源码与官方文档 OKF Wiki 教程"
source: "User Request; OpenTUI source commit f8f608e2b9a41685d613a1156708ff06c826c3ce; https://opentui.com/docs/"
date: "2026-10-20"
methodology: "seven-concepts knowledge scenario: R-I-E-V-C"
content-sensitivity: "public"
tags: ["OpenTUI", "TUI", "Zig", "TypeScript", "OKF Wiki"]
---

# OpenTUI 源码与官方文档 OKF Wiki 教程

## Overview
- **Summary**：基于固定版本源码和 OpenTUI 官方文档，全面梳理 OpenTUI 的架构、公共包、核心 API、运行时与实践路径，并在 OKF bundle 库中创建可溯源的中文教程。
- **Purpose**：为终端 UI 开发者提供一套版本明确、从入门到核心机制逐步深入、可由源码与官方资料复核的 OpenTUI 学习入口。
- **Target Users**：TypeScript/Zig 开发者、终端 UI 框架使用者、希望理解 OpenTUI 渲染与原生核心的技术读者。

## Goals
- 在 `projects/awesome-okf-xs/doc/bundles/jishu/terminal/opentui/` 创建独立 OKF v0.2 bundle，与 Textualize bundle 并列。
- 按 R→I→E→V 完成信源核定、编号事实采集、架构洞察、文档生成和独立核验；保留 C 阶段交付核对，不在未获明确提交请求时创建 Git commit。
- 覆盖 OpenTUI 官方学习路径、源码 workspace 中的公开包与主要边界，以及 Core、React、Solid、native rendering 的关系。
- 同步更新终端组、技术域和 bundle 总索引，使新 bundle 可由文档根导航抵达。

## Non-Goals
- 不修改 OpenTUI 源码、官方文档或其构建配置。
- 不逐文件转录全部源码、测试、生成文件或官方文档；“全面学习”指覆盖公开包与核心机制，并对关键数据流深入取证。
- 不把 OpenTUI 并入 Textualize bundle，不新建顶层技术域或分组。
- 不将本机 `external/` 绝对路径写入长期知识包作为信源；不复制大段官方文档。
- 不创建 Git commit，除非用户另行明确要求。

## Background & Context
- **源码位置**：本机只读快照 `external/dao/anomalyco/opentui/`，远端为 `git@github.com:anomalyco/opentui.git`。
- **源码坐标**：`f8f608e2b9a41685d613a1156708ff06c826c3ce`；该提交没有精确 release tag，长期文档以 GitHub 不可变 commit 链接为准。
- **官方文档**：`https://opentui.com/docs/`；当前文档声明的发布版本为 0.6.6，正文中须区分该文档版本与源码 commit。
- **目标位置**：`projects/awesome-okf-xs/doc/bundles/jishu/terminal/opentui/`。
- **归属依据**：现有 `jishu/terminal/` 已承载终端渲染与 TUI 生态，OpenTUI 与 Textualize 是不同实现，应各自形成 bundle。
- **执行约束**：awesome-okf-xs 是 git 子模块；操作前后检查其状态，不触碰其他在途文件。修改共享索引前重新读取最新内容。

## Functional Requirements
- **FR-1：信源登记**：建立源码与官方文档 references，记录远端仓库、固定 commit、发布文档版本、读取日期及适用边界；sources 均指向 bundle 内 references，不引用本机绝对路径。
- **FR-2：事实与架构**：整理可定位到源码路径/官方页面的编号事实，并据此解释 TypeScript bindings 与 Zig native core、renderer/renderable tree、布局与绘制、终端输入输出、生命周期之间的关系。
- **FR-3：包与框架覆盖**：核对 workspace manifest、package entry points 和官方文档；覆盖源码仓库公开的包、Core 基础用法、React/Solid bindings 及其共享/差异边界。包名和数量以固定源码及官方清单为准。
- **FR-4：主题教程**：形成适合逐步学习的 concepts 与 examples，覆盖快速开始、renderables、renderer/layout、交互与焦点、测试与清理、native rendering，以及经源码核验的代表性包/API。若资料不足，明确标注未覆盖边界，不推测。
- **FR-5：OKF 结构与元数据**：按 OKF v0.2 创建 bundle 根索引、`log.md`、`concepts/`、`examples/`、`references/`；非保留 Markdown 文档包含可解析 YAML frontmatter 与 `sources`，索引包含人类导航和完整 `{toctree}`。
- **FR-6：导航登记**：将 bundle 挂入 `jishu/terminal/index.md`、相应上级导航和 `doc/bundles/index.md`；按官方 gate 口径复核束数、组数、域数，不沿用过期计数。
- **FR-7：分批生成与验证**：references 先行；概念/示例按每批不超过 7 个文件生成；内容完成后最后生成各级索引；完成源码符号、代码示例、计数断言、链接、frontmatter、UTF-8 与 toctree 验证。

## Non-Functional Requirements
- **NFR-1**：事实与解释分层；事实不混入动机推测，每条关键 API/行为说明可回到固定 commit 或官方页面核验。
- **NFR-2**：中文撰写，英文技术术语首次出现时解释；文件名使用 kebab-case。
- **NFR-3**：所有 API 名、导入路径、配置名与代码示例须与源码或官方文档一致；对不存在/不支持的声明也做必要的负向核验。
- **NFR-4**：避免未注明统计口径的数量陈述；源码事实中的计数由脚本/解析器采集，验证阶段以独立方法复核。
- **NFR-5**：所有 bundle 内交叉链接使用 bundle-relative `/` 路径；父级链接遵循项目现有导航格式。
- **NFR-6**：Bundle 状态、版本和更新时间清晰可见；不把 `next`/main 文档中的未发布能力混写为 0.6.6 稳定文档事实。

## Constraints
- **Technical**：以本机固定 commit `f8f608e2b9a41685d613a1156708ff06c826c3ce` 为源码事实基准；官方文档用于解释面向用户的 API 与使用路径。源码仓库 HEAD 无精确 tag。
- **Repository**：目标子模块当前工作树干净；根仓存在与本任务无关的 `projects/daoapps.github.io` 子模块状态变化及 `.trae/specs/daoapps-product/` 未跟踪目录，均不得纳入本任务。
- **Documentation**：遵循 `projects/awesome-okf-xs/.agents/rules/frontmatter.md` 与该项目的 toctree/bundle gates。
- **Workflow**：批准前只允许创建本 Spec 的需求/任务文件，不得创建目标 bundle 内容；Review 阶段再创建 `review.md`。

## Assumptions
- 官方文档主页、releases、Core 概念、framework bindings 与 native 文档可公开访问。
- `jishu/terminal/` 是该知识主题的正确分类；Textualize 当前独立 bundle 不改变这一归属判断。
- 全面覆盖以“全部公开包面 + 核心机制和主要学习路径”为验收口径，而非逐行注释整个仓库。
- 若源码 commit 与官方文档 0.6.6 出现差异，文档会分别注明源码证据和文档版本，不静默合并为同一版本结论。

## Acceptance Criteria

### AC-1：Bundle 归属与结构
- **Type**：`rule`
- **Given**：实施范围已获批准
- **When**：检查目标文档目录
- **Then**：独立 bundle 位于 `jishu/terminal/opentui/`，包含根 `index.md`、`log.md`、`concepts/`、`examples/`、`references/`；不改动 Textualize bundle 内容。
- **Pass Condition**：目录结构存在且每个目录索引遵守项目规范。
- **Evidence**：文件清单、`git diff --stat`、bundle 根索引。

### AC-2：信源与版本可追溯
- **Type**：`rule`
- **Given**：Bundle 文档引用 OpenTUI 源码或官方资料
- **When**：核验 references 与 frontmatter
- **Then**：源码引用锚定 commit `f8f608e2b9a41685d613a1156708ff06c826c3ce`，官方文档注明页面 URL 和版本边界；无本机绝对路径或浮动分支作为唯一源码坐标。
- **Pass Condition**：所有内容文档的 `sources` 指向已存在 references，信源坐标准确。
- **Evidence**：references 文件、frontmatter 扫描、固定 commit 页面。

### AC-3：包与架构事实覆盖
- **Type**：`rule`
- **Given**：固定源码和官方文档可读取
- **When**：审查 facts、concepts 与 examples
- **Then**：公开包清单、Core/React/Solid 使用边界、Zig native core、renderer/renderable、布局绘制、输入输出、生命周期、测试和 native rendering 均有证据驱动的说明；无资料支持的事项显式限定。
- **Pass Condition**：每个覆盖项至少关联一条编号事实或一项官方文档来源，关键符号在源码中可检索。
- **Evidence**：facts 清单、知识地图、逐项符号验证结果。

### AC-4：入门与代码示例可核验
- **Type**：`rule`
- **Given**：教程包含可执行 API 或命令示例
- **When**：对照官方文档和固定 commit 源码
- **Then**：示例所需 imports、构造参数、方法和清理路径均真实存在；与 `next` 文档或更新版本有关的差异已标注。
- **Pass Condition**：每段代码示例均有对应来源和核验记录，未验证内容不声称可运行。
- **Evidence**：源码搜索结果、示例来源映射及必要的静态/最小运行验证。

### AC-5：OKF 元数据与导航合规
- **Type**：`rule`
- **Given**：所有 bundle 内容文档已生成
- **When**：运行项目质量门
- **Then**：frontmatter、sources、目录索引、bundle-relative 链接、父级导航和总索引均符合 OKF v0.2 与子项目规范。
- **Pass Condition**：`invoke gates.toctrees`、`invoke gates.bundles`、`invoke gates.utf8` 对本次变更通过，或对既有失败作准确归属并证明本次文件零命中。
- **Evidence**：质量门命令输出及本次变更相关条目。

### AC-6：事实与数量断言准确
- **Type**：`rule`
- **Given**：文档含类名、方法名、包名、文件数或其他数量陈述
- **When**：执行独立验证
- **Then**：API/文件事实通过源码搜索验证，所有数量注明统计口径并由独立手段复核，不一致项已修正。
- **Pass Condition**：无未核验 API、无未复核数量断言、无悬空本地链接。
- **Evidence**：逐符号检查、计数脚本/命令、链接检查结果。

### AC-7：教程的学习路径与覆盖质量
- **Type**：`rubric`
- **Dimension**：全面性、准确性、可学习性与版本边界表达
- **Scale**：1-5
- **Anchors**：1 = 主题零散且关键机制/信源缺失；3 = 核心机制有覆盖但包边界或学习顺序仍有明显空缺；5 = 覆盖官方学习路径和全部公开包面，核心机制有源码证据，示例可核验，版本差异明确且学习顺序连贯
- **Pass Threshold**：>= 4
- **Evidence**：独立 Review 对照本规格 FR-1 至 FR-7 和源码/文档映射评分。

## Open Questions
- 无阻断性待决问题；若批准时要调整“全面学习”的范围或目标分类，实施前更新本规格和任务队列。
